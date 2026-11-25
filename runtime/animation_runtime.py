#!/usr/bin/env python3
"""Inspect local tools and run a real Blender -> FFmpeg -> ffprobe smoke test."""
import argparse, json, os, platform, shutil, subprocess, sys, time
from pathlib import Path

def locate(env, names):
    p=os.environ.get(env)
    if p and Path(p).exists(): return str(Path(p).resolve())
    for n in names:
        p=shutil.which(n)
        if p: return p
    return None

def version(path, args):
    if not path: return {"available":False}
    try:
        p=subprocess.run([path,*args],capture_output=True,text=True,timeout=20)
        return {"available":p.returncode==0,"version":(p.stdout+"\n"+p.stderr)[:1000],"returncode":p.returncode}
    except Exception as e: return {"available":False,"error":str(e)}

def inspect():
    b=locate("BLENDER_BIN",["blender","Blender"])
    f=locate("FFMPEG_BIN",["ffmpeg"])
    q=locate("FFPROBE_BIN",["ffprobe"])
    return {"platform":platform.platform(),"python":sys.version,"tools":{
        "blender":{"path":b,**version(b,["--version"])},
        "ffmpeg":{"path":f,**version(f,["-version"])},
        "ffprobe":{"path":q,**version(q,["-version"])}},
        "note":"bpy belongs to Blender's bundled Python. This smoke test is not proof of story-quality output."}

def smoke(a):
    r=inspect()["tools"]; blender=r["blender"]["path"]; ffmpeg=r["ffmpeg"]["path"]; ffprobe=r["ffprobe"]["path"]
    if not all((blender,ffmpeg,ffprobe)):
        print("BLOCKED: Blender, FFmpeg and ffprobe are all required. Set BLENDER_BIN/FFMPEG_BIN/FFPROBE_BIN if needed.",file=sys.stderr); return 2
    work=a.workdir.resolve(); frames=work/"frames"; frames.mkdir(parents=True,exist_ok=True)
    blend=work/"smoke_test.blend"; log=work/"blender.log"; video=work/"smoke_test.mp4"
    script=Path(__file__).with_name("blender_smoke_test.py")
    cmd=[blender,"--background","--factory-startup","--python-exit-code","1","--python",str(script),"--",
         "--output-dir",str(frames),"--blend-file",str(blend),"--width",str(a.width),"--height",str(a.height),
         "--fps",str(a.fps),"--frames",str(a.frames)]
    start=time.time()
    with log.open("w",encoding="utf-8") as fp: p=subprocess.run(cmd,stdout=fp,stderr=subprocess.STDOUT)
    if p.returncode:\n        print("Blender failed; last log lines:\\n"+ "\\n".join(log.read_text(encoding="utf-8",errors="replace").splitlines()[-80:]),file=sys.stderr)\n        return p.returncode
    if not (frames/"frame_0001.png").exists(): print("No rendered frame found.",file=sys.stderr); return 1
    p=subprocess.run([ffmpeg,"-y","-framerate",str(a.fps),"-i",str(frames/"frame_%04d.png"),
                      "-c:v","libx264","-pix_fmt","yuv420p","-movflags","+faststart",str(video)],capture_output=True,text=True)
    if p.returncode: print(p.stderr[-3000:],file=sys.stderr); return p.returncode
    p=subprocess.run([ffprobe,"-v","error","-show_entries","format=duration:stream=codec_type,codec_name,width,height,r_frame_rate","-of","json",str(video)],capture_output=True,text=True)
    if p.returncode: print(p.stderr,file=sys.stderr); return p.returncode
    report={"status":"PASS","elapsed_seconds":round(time.time()-start,2),"blend":str(blend),
            "video":str(video),"metadata":json.loads(p.stdout),"log":str(log),
            "scope":"Technical smoke test only; not a final story render."}
    (work/"report.json").write_text(json.dumps(report,indent=2),encoding="utf-8")
    print(json.dumps(report,indent=2)); return 0

def main():
    p=argparse.ArgumentParser(); sub=p.add_subparsers(dest="cmd",required=True)
    sub.add_parser("inspect")
    s=sub.add_parser("smoke-test"); s.add_argument("--workdir",type=Path,default=Path("animation_work/smoke_test"))
    s.add_argument("--width",type=int,default=360); s.add_argument("--height",type=int,default=640)
    s.add_argument("--fps",type=int,default=24); s.add_argument("--frames",type=int,default=48)
    a=p.parse_args()
    if a.cmd=="inspect":
        report=inspect(); print(json.dumps(report,indent=2))
        return 0 if all(report["tools"][x]["available"] for x in ("blender","ffmpeg","ffprobe")) else 2
    return smoke(a)
if __name__=="__main__": raise SystemExit(main())
