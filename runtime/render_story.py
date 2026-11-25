#!/usr/bin/env python3
"""Orchestrate a complete storyboard -> Blender shot renders -> MP4 pipeline."""
import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


def locate(env, names):
    value = os.environ.get(env)
    if value and Path(value).exists():
        return str(Path(value).resolve())
    for name in names:
        found = shutil.which(name)
        if found:
            return found
    return None


def run(command, log_path=None):
    if log_path:
        with Path(log_path).open("w", encoding="utf-8") as log:
            result = subprocess.run(command, stdout=log, stderr=subprocess.STDOUT, text=True)
    else:
        result = subprocess.run(command, capture_output=True, text=True)
    if result.returncode:
        detail = getattr(result, "stderr", "") or ""
        raise RuntimeError("Command failed (" + str(result.returncode) + "): " + " ".join(command) + "\n" + detail[-4000:])
    return result


def ffmpeg_escape(path):
    return str(Path(path).resolve()).replace("\\", "\\\\").replace(":", "\\:").replace("'", "\\'")


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--storyboard", required=True, type=Path)
    p.add_argument("--output", required=True, type=Path)
    p.add_argument("--voice", type=Path)
    p.add_argument("--music", type=Path)
    p.add_argument("--captions", type=Path, help="Optional SRT file burned into the final video")
    p.add_argument("--format", choices=("shorts", "long"), default=None)
    p.add_argument("--width", type=int)
    p.add_argument("--height", type=int)
    p.add_argument("--fps", type=int)
    p.add_argument("--samples", type=int, default=32)
    p.add_argument("--workdir", type=Path)
    a = p.parse_args()

    storyboard = a.storyboard.resolve()
    data = json.loads(storyboard.read_text(encoding="utf-8"))
    shots = data.get("shots")
    if not isinstance(shots, list) or not shots:
        raise ValueError("Storyboard must contain a non-empty shots array.")
    for i, shot in enumerate(shots):
        if float(shot.get("duration_seconds", 0)) <= 0:
            raise ValueError("Shot " + str(i) + " must have positive duration_seconds.")

    blender = locate("BLENDER_BIN", ["blender", "Blender"])
    ffmpeg = locate("FFMPEG_BIN", ["ffmpeg"])
    ffprobe = locate("FFPROBE_BIN", ["ffprobe"])
    if not all((blender, ffmpeg, ffprobe)):
        raise RuntimeError("Missing Blender, FFmpeg or ffprobe. Run animation_runtime.py inspect and configure BLENDER_BIN/FFMPEG_BIN/FFPROBE_BIN.")

    fmt = a.format or data.get("project", {}).get("resolution", "shorts")
    width = a.width or (1080 if fmt == "shorts" else 1920)
    height = a.height or (1920 if fmt == "shorts" else 1080)
    fps = a.fps or int(data.get("project", {}).get("fps", 24))
    if width < 16 or height < 16 or fps < 1:
        raise ValueError("Invalid output dimensions or fps.")
    for path in (a.voice, a.music, a.captions):
        if path and not path.is_file():
            raise FileNotFoundError(str(path))
    total_story_seconds = sum(float(shot["duration_seconds"]) for shot in shots)
    voice_duration = None
    if a.voice:
        voice_probe = run([ffprobe, "-v", "error", "-show_entries", "format=duration", "-of", "json", str(a.voice)])
        voice_duration = float(json.loads(voice_probe.stdout).get("format", {}).get("duration", 0))
        tolerance = max(0.5, 1.0 / fps)
        if abs(voice_duration - total_story_seconds) > tolerance:
            raise ValueError(
                "Voice is the master timeline: its duration is %.3fs but storyboard totals %.3fs. "
                "Adjust shot durations to the supplied audio before rendering; the voice will not be sped up, cut or replaced."
                % (voice_duration, total_story_seconds)
            )

    output = a.output.resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    work = a.workdir.resolve() if a.workdir else output.parent / (output.stem + "_work")
    work.mkdir(parents=True, exist_ok=True)
    scene_script = Path(__file__).with_name("story_scene.py").resolve()
    segment_files = []

    for index, shot in enumerate(shots):
        shot_dir = work / ("shot_%03d" % (index + 1))
        shot_dir.mkdir(parents=True, exist_ok=True)
        blender_cmd = [
            blender, "--background", "--factory-startup", "--python-exit-code", "1",
            "--python", str(scene_script), "--",
            "--storyboard", str(storyboard), "--shot-index", str(index),
            "--output-dir", str(shot_dir), "--width", str(width), "--height", str(height),
            "--fps", str(fps), "--samples", str(a.samples)
        ]
        print("Rendering shot", index + 1, "of", len(shots), "-", shot.get("id", index + 1))
        run(blender_cmd, shot_dir / "blender.log")
        segment = shot_dir / "segment.mp4"
        encode_cmd = [
            ffmpeg, "-y", "-framerate", str(fps), "-i", str(shot_dir / "frame_%04d.png"),
            "-c:v", "libx264", "-preset", "medium", "-crf", "18",
            "-pix_fmt", "yuv420p", "-an", str(segment)
        ]
        run(encode_cmd, shot_dir / "ffmpeg.log")
        segment_files.append(segment)

    concat_file = work / "concat.txt"
    concat_file.write_text("".join("file '" + str(x).replace("'", "'\\''") + "'\n" for x in segment_files), encoding="utf-8")
    joined = work / "joined_video.mp4"
    run([ffmpeg, "-y", "-f", "concat", "-safe", "0", "-i", str(concat_file), "-c", "copy", str(joined)], work / "concat.log")

    final_input = joined
    if a.captions:
        captioned = work / "captioned_video.mp4"
        vf = "subtitles=filename='" + ffmpeg_escape(a.captions) + "'"
        run([ffmpeg, "-y", "-i", str(joined), "-vf", vf, "-c:v", "libx264", "-preset", "medium",
             "-crf", "18", "-pix_fmt", "yuv420p", "-an", str(captioned)], work / "captions.log")
        final_input = captioned

    if a.voice or a.music:
        cmd = [ffmpeg, "-y", "-i", str(final_input)]
        if a.voice:
            cmd += ["-i", str(a.voice)]
        if a.music:
            cmd += ["-stream_loop", "-1", "-i", str(a.music)]
        if a.voice and a.music:
            cmd += ["-filter_complex", "[1:a]aresample=48000,apad[voice];[2:a]volume=0.18,aresample=48000,apad[music];[voice][music]amix=inputs=2:duration=longest:dropout_transition=2[aout]",
                    "-map", "0:v:0", "-map", "[aout]"]
        elif a.voice:
            cmd += ["-filter_complex", "[1:a]aresample=48000,apad[aout]", "-map", "0:v:0", "-map", "[aout]"]
        else:
            cmd += ["-filter_complex", "[1:a]volume=0.18,aresample=48000,apad[aout]", "-map", "0:v:0", "-map", "[aout]"]
        cmd += ["-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart", str(output)]
        run(cmd, work / "audio_mux.log")
    else:
        shutil.copy2(final_input, output)

    probe = run([ffprobe, "-v", "error", "-show_entries",
                 "format=duration:stream=codec_type,codec_name,width,height,r_frame_rate",
                 "-of", "json", str(output)])
    metadata = json.loads(probe.stdout)
    report = {
        "status": "PASS",
        "output": str(output),
        "duration_seconds": float(metadata.get("format", {}).get("duration", 0)),
        "shot_count": len(shots),
        "resolution": [width, height],
        "fps": fps,
        "audio_inputs": {"voice": str(a.voice.resolve()) if a.voice else None,\n                         "voice_duration_seconds": voice_duration,
                         "music": str(a.music.resolve()) if a.music else None,
                         "captions": str(a.captions.resolve()) if a.captions else None},
        "metadata": metadata,
        "workdir": str(work)
    }
    (work / "final_report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
