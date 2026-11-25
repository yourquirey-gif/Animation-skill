#!/usr/bin/env python3
"""Panda3D storyboard renderer and FFmpeg MP4 assembler."""
import argparse, hashlib, json, shutil, struct, subprocess, sys
from pathlib import Path

def run(cmd, log=None):
    if log:
        with open(log,"w",encoding="utf-8") as f: p=subprocess.run(cmd,stdout=f,stderr=subprocess.STDOUT,text=True)
    else: p=subprocess.run(cmd,capture_output=True,text=True)
    if p.returncode: raise RuntimeError("Command failed: "+" ".join(map(str,cmd))+"\n"+(getattr(p,"stderr","") or "")[-2500:])
    return p

def check_frames(folder,count,w,h):
    files=sorted(folder.glob("frame_*.png"))
    if len(files)!=count: raise RuntimeError(f"Expected {count} PNG frames, found {len(files)}")
    prev=None; duplicates=0
    for f in files:
        data=f.read_bytes()
        if len(data)<24 or data[:8]!=b"\x89PNG\r\n\x1a\n": raise RuntimeError(f"Invalid PNG: {f}")
        if struct.unpack(">II",data[16:24])!=(w,h): raise RuntimeError(f"Wrong PNG dimensions: {f}")
        digest=hashlib.sha256(data).digest()
        if digest==prev: duplicates+=1
        prev=digest
    return {"frame_count":len(files),"dimensions":[w,h],"adjacent_identical_frame_pairs":duplicates}

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--storyboard",required=True,type=Path); p.add_argument("--output",required=True,type=Path)
    p.add_argument("--voice",type=Path); p.add_argument("--music",type=Path); p.add_argument("--captions",type=Path)
    p.add_argument("--format",choices=("shorts","long")); p.add_argument("--width",type=int); p.add_argument("--height",type=int); p.add_argument("--fps",type=int); p.add_argument("--workdir",type=Path)
    a=p.parse_args(); board=a.storyboard.resolve(); data=json.loads(board.read_text(encoding="utf-8")); shots=data.get("shots")
    if not isinstance(shots,list) or not shots: raise ValueError("Storyboard must contain shots")
    for i,s in enumerate(shots):
        if float(s.get("duration_seconds",0))<=0: raise ValueError(f"Shot {i} duration must be positive")
    ffmpeg,ffprobe=shutil.which("ffmpeg"),shutil.which("ffprobe")
    if not ffmpeg or not ffprobe: raise RuntimeError("Install FFmpeg and ffprobe and add them to PATH")
    try: import panda3d
    except ImportError as e: raise RuntimeError("Panda3D missing; run python -m pip install -r requirements.txt") from e
    fmt=a.format or data.get("project",{}).get("resolution","shorts"); w=a.width or (1080 if fmt=="shorts" else 1920); h=a.height or (1920 if fmt=="shorts" else 1080); fps=a.fps or int(data.get("project",{}).get("fps",24))
    if min(w,h,fps)<=0: raise ValueError("Invalid render dimensions or fps")
    for f in (a.voice,a.music,a.captions):
        if f and not f.is_file(): raise FileNotFoundError(f)
    out=a.output.resolve(); out.parent.mkdir(parents=True,exist_ok=True); work=(a.workdir or out.parent/(out.stem+"_work")).resolve(); work.mkdir(parents=True,exist_ok=True)
    scene=Path(__file__).with_name("panda3d_scene.py").resolve(); segments=[]; qc=[]
    for i,shot in enumerate(shots):
        folder=work/f"shot_{i+1:03d}"; folder.mkdir(parents=True,exist_ok=True)
        cmd=[sys.executable,str(scene),"--storyboard",str(board),"--shot-index",str(i),"--output-dir",str(folder),"--width",str(w),"--height",str(h),"--fps",str(fps)]
        print(f"Rendering Panda3D shot {i+1}/{len(shots)}: {shot.get('id',i+1)}",flush=True); run(cmd,folder/"panda3d.log")
        n=max(1,round(float(shot["duration_seconds"])*fps)); qc.append({"shot_id":shot.get("id",i+1),**check_frames(folder,n,w,h)})
        segment=folder/"segment.mp4"; run([ffmpeg,"-y","-framerate",str(fps),"-i",str(folder/"frame_%04d.png"),"-c:v","libx264","-preset","veryfast","-crf","19","-pix_fmt","yuv420p",str(segment)],folder/"encode.log"); segments.append(segment)
    concat=work/"concat.txt"; concat.write_text("".join("file '"+str(x).replace("'","'\\''")+"'\n" for x in segments),encoding="utf-8")
    joined=work/"joined.mp4"; run([ffmpeg,"-y","-f","concat","-safe","0","-i",str(concat),"-c","copy",str(joined)],work/"concat.log"); final=joined
    if a.captions:
        captioned=work/"captioned.mp4"; run([ffmpeg,"-y","-i",str(final),"-vf","subtitles="+str(a.captions.resolve()),"-c:v","libx264","-crf","19","-pix_fmt","yuv420p","-an",str(captioned)],work/"captions.log"); final=captioned
    if a.voice or a.music:
        cmd=[ffmpeg,"-y","-i",str(final)]
        if a.voice: cmd += ["-i",str(a.voice)]
        if a.music: cmd += ["-stream_loop","-1","-i",str(a.music)]
        if a.voice and a.music: filt="[1:a]aresample=48000,apad[v];[2:a]volume=0.18,aresample=48000,apad[m];[v][m]amix=inputs=2:duration=longest[a]"
        elif a.voice: filt="[1:a]aresample=48000,apad[a]"
        else: filt="[1:a]volume=0.18,aresample=48000,apad[a]"
        cmd += ["-filter_complex",filt,"-map","0:v:0","-map","[a]","-c:v","copy","-c:a","aac","-shortest","-movflags","+faststart",str(out)]; run(cmd,work/"audio.log")
    else: shutil.copy2(final,out)
    probe=run([ffprobe,"-v","error","-show_entries","format=duration:stream=codec_type,codec_name,width,height,r_frame_rate","-of","json",str(out)])
    meta=json.loads(probe.stdout); streams=meta.get("streams",[]); videos=[x for x in streams if x.get("codec_type")=="video"]; duration=float(meta.get("format",{}).get("duration",0)); expected=sum(max(1,round(float(s["duration_seconds"])*fps)) for s in shots)/fps
    if not videos or duration<=0 or abs(duration-expected)>max(.2,2/fps): raise RuntimeError("Final MP4 failed stream/duration validation")
    if (a.voice or a.music) and not any(x.get("codec_type")=="audio" for x in streams): raise RuntimeError("Audio missing from final MP4")
    report={"status":"PASS_WITH_VISUAL_REVIEW" if any(x["adjacent_identical_frame_pairs"] for x in qc) else "PASS","output":str(out),"duration_seconds":duration,"resolution":[w,h],"fps":fps,"shot_qc":qc,"metadata":meta,"workdir":str(work)}
    (work/"final_report.json").write_text(json.dumps(report,indent=2),encoding="utf-8"); print(json.dumps(report,indent=2))

if __name__=="__main__": main()
