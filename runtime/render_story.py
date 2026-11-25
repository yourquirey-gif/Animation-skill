#!/usr/bin/env python3
"""Orchestrate a complete storyboard -> Blender shot renders -> MP4 pipeline."""
import argparse
import hashlib
import json
import struct
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
        detail = Path(log_path).read_text(encoding="utf-8", errors="replace")[-6000:]
    else:
        result = subprocess.run(command, capture_output=True, text=True)
        detail = getattr(result, "stderr", "") or ""
    if result.returncode:
        raise RuntimeError("Command failed (" + str(result.returncode) + "): " + " ".join(command) + "\\n" + detail[-6000:])
    return result


def ffmpeg_escape(path):
    return str(Path(path).resolve()).replace("\\", "\\\\").replace(":", "\\:").replace("'", "\\'")


def validate_rendered_frames(shot_dir, expected_frames, width, height):
    frames = sorted(shot_dir.glob("frame_*.png"))
    if len(frames) != expected_frames:
        raise RuntimeError(
            "Shot frame count mismatch in " + str(shot_dir) + ": expected " +
            str(expected_frames) + ", found " + str(len(frames))
        )
    previous_hash = None
    duplicate_adjacent = 0
    for frame in frames:
        with frame.open("rb") as fp:
            header = fp.read(24)
        if len(header) != 24 or header[:8] != b"\x89PNG\r\n\x1a\n":
            raise RuntimeError("Invalid or truncated PNG frame: " + str(frame))
        actual_width, actual_height = struct.unpack(">II", header[16:24])
        if (actual_width, actual_height) != (width, height):
            raise RuntimeError(
                "Frame dimensions mismatch in " + str(frame) + ": " +
                str(actual_width) + "x" + str(actual_height)
            )
        digest = hashlib.sha256(frame.read_bytes()).digest()
        if digest == previous_hash:
            duplicate_adjacent += 1
        previous_hash = digest
    return {
        "frame_count": len(frames),
        "dimensions": [width, height],
        "adjacent_identical_frame_pairs": duplicate_adjacent,
        "duplicate_frames_are_review_candidates": duplicate_adjacent > 0,
    }


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--storyboard", required=True, type=Path)
    p.add_argument("--output", required=True, type=Path)
    p.add_argument("--voice", type=Path)
    p.add_argument("--auto-lip-sync", action="store_true", help="Run Rhubarb on --voice and distribute viseme cues to storyboard subjects with viseme_map")
    p.add_argument("--rhubarb", help="Optional path to Rhubarb Lip Sync CLI")
    p.add_argument("--music", type=Path)
    p.add_argument("--captions", type=Path, help="Optional SRT file burned into the final video")
    p.add_argument("--format", choices=("shorts", "long"), default=None)
    p.add_argument("--width", type=int)
    p.add_argument("--height", type=int)
    p.add_argument("--fps", type=int)
    p.add_argument("--samples", type=int, default=32)
    p.add_argument("--workdir", type=Path)
    p.add_argument("--retries", type=int, default=1, help="Number of retries after the first failed shot render")
    p.add_argument("--progress-file", type=Path, help="Write machine-readable job progress JSON")
    a = p.parse_args()
    if a.retries < 0 or a.retries > 5:
        raise ValueError("--retries must be between 0 and 5")

    def progress(status, shot_index=None, shot_id=None, message=None):
        payload = {"status": status, "completed_shots": len(shot_qc),
                   "total_shots": len(shots), "current_shot_index": shot_index,
                   "current_shot_id": shot_id, "message": message}
        if a.progress_file:
            a.progress_file.parent.mkdir(parents=True, exist_ok=True)
            temporary = a.progress_file.with_suffix(a.progress_file.suffix + ".tmp")
            temporary.write_text(json.dumps(payload, indent=2), encoding="utf-8")
            temporary.replace(a.progress_file)
        print(json.dumps(payload), flush=True)

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

    lip_sync_report = {"enabled": False, "subjects_animated": 0, "events": 0}
    if a.auto_lip_sync:
        if not a.voice:
            raise ValueError("--auto-lip-sync requires --voice")
        viseme_output = work / "audio_visemes.json"
        align_script = Path(__file__).with_name("align_visemes.py").resolve()
        align_command = [sys.executable, str(align_script), "--audio", str(a.voice),
                         "--output", str(viseme_output)]
        if a.rhubarb:
            align_command += ["--rhubarb", a.rhubarb]
        run(align_command, work / "rhubarb_alignment.log")
        aligned = json.loads(viseme_output.read_text(encoding="utf-8"))
        all_events = aligned.get("viseme_keyframes", [])
        elapsed = 0.0
        subjects_animated = 0
        for shot in shots:
            duration = float(shot["duration_seconds"])
            shot_events = [
                {"time_seconds": round(float(event["time_seconds"]) - elapsed, 4),
                 "viseme": event["viseme"], "strength": event.get("strength", 1.0)}
                for event in all_events
                if elapsed - 1e-6 <= float(event["time_seconds"]) <= elapsed + duration + 1e-6
            ]
            for subject in shot.get("subjects", []):
                if subject.get("viseme_map"):
                    subject["viseme_keyframes"] = shot_events
                    subjects_animated += 1
            elapsed += duration
        if subjects_animated == 0:
            raise ValueError("--auto-lip-sync found no storyboard subject with a viseme_map. Add exact facial shape-key names to the character subject.")
        # Keep relative asset paths anchored to the original storyboard directory.
        for shot in shots:
            entries = list(shot.get("subjects", [])) + list(shot.get("props", []))
            entries += list(shot.get("environment", {}).get("objects", []))
            for entry in entries:
                if entry.get("asset_file"):
                    pth = Path(entry["asset_file"])
                    if not pth.is_absolute():
                        entry["asset_file"] = str((storyboard.parent / pth).resolve())
                retarget_cfg = entry.get("retarget", {})
                if retarget_cfg.get("animation_file"):
                    pth = Path(retarget_cfg["animation_file"])
                    if not pth.is_absolute():
                        retarget_cfg["animation_file"] = str((storyboard.parent / pth).resolve())
        storyboard = work / "storyboard_with_audio_lipsync.json"
        storyboard.write_text(json.dumps(data, indent=2), encoding="utf-8")
        lip_sync_report = {"enabled": True, "subjects_animated": subjects_animated,
                           "events": len(all_events), "source": "Rhubarb Lip Sync"}

    scene_script = Path(__file__).with_name("story_scene.py").resolve()
    segment_files = []
    shot_qc = []

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
        shot_id = shot.get("id", index + 1)
        progress("RENDERING", index + 1, shot_id)
        print("Rendering shot", index + 1, "of", len(shots), "-", shot_id, flush=True)
        last_error = None
        for attempt in range(a.retries + 1):
            for stale in shot_dir.glob("frame_*.png"):
                stale.unlink()
            try:
                run(blender_cmd, shot_dir / ("blender_attempt_%02d.log" % (attempt + 1)))
                last_error = None
                break
            except Exception as exc:
                last_error = exc
                print("Shot", shot_id, "attempt", attempt + 1, "failed:", str(exc), flush=True)
                if attempt >= a.retries:
                    progress("FAILED", index + 1, shot_id, str(exc))
                    raise
        if last_error:
            raise last_error
        expected_frames = max(1, round(float(shot["duration_seconds"]) * fps))
        shot_qc.append({
            "shot_id": shot.get("id", index + 1),
            **validate_rendered_frames(shot_dir, expected_frames, width, height),
        })
        segment = shot_dir / "segment.mp4"
        encode_cmd = [
            ffmpeg, "-y", "-framerate", str(fps), "-i", str(shot_dir / "frame_%04d.png"),
            "-c:v", "libx264", "-preset", "medium", "-crf", "18",
            "-pix_fmt", "yuv420p", "-an", str(segment)
        ]
        run(encode_cmd, shot_dir / "ffmpeg.log")
        segment_files.append(segment)
        progress("SHOT_COMPLETE", index + 1, shot_id)

    progress("ASSEMBLING")
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
    streams = metadata.get("streams", [])
    video_streams = [stream for stream in streams if stream.get("codec_type") == "video"]
    audio_streams = [stream for stream in streams if stream.get("codec_type") == "audio"]
    actual_duration = float(metadata.get("format", {}).get("duration", 0))
    expected_duration = sum(max(1, round(float(shot["duration_seconds"]) * fps)) for shot in shots) / fps
    duration_tolerance = max(0.15, 2.0 / fps)
    if not video_streams:
        raise RuntimeError("Final MP4 has no video stream.")
    if actual_duration <= 0:
        raise RuntimeError("Final MP4 has an invalid or zero duration.")
    if abs(actual_duration - expected_duration) > duration_tolerance:
        raise RuntimeError(
            "Final MP4 duration mismatch: expected %.3fs, got %.3fs." %
            (expected_duration, actual_duration)
        )
    video = video_streams[0]
    if int(video.get("width", 0)) != width or int(video.get("height", 0)) != height:
        raise RuntimeError("Final MP4 dimensions do not match the requested output profile.")
    rate = str(video.get("r_frame_rate", "0/1")).split("/")
    actual_fps = float(rate[0]) / max(1.0, float(rate[1])) if len(rate) == 2 else 0.0
    if abs(actual_fps - fps) > 0.01:
        raise RuntimeError("Final MP4 FPS mismatch: requested %s, got %s." % (fps, actual_fps))
    if (a.voice or a.music) and not audio_streams:
        raise RuntimeError("Audio was requested but final MP4 contains no audio stream.")
    black_probe = run([ffmpeg, "-hide_banner", "-i", str(output), "-vf",
                       "blackdetect=d=1:pix_th=0.10", "-an", "-f", "null", "-"])
    black_log = getattr(black_probe, "stderr", "") or ""
    black_segments = [line.strip() for line in black_log.splitlines() if "black_start:" in line]
    report = {
        "status": "PASS_WITH_REVIEW_WARNINGS" if any(x["adjacent_identical_frame_pairs"] for x in shot_qc) else "PASS",
        "output": str(output),
        "duration_seconds": actual_duration,
        "shot_count": len(shots),
        "shot_frame_qc": shot_qc,
        "qc_note": "Adjacent byte-identical frames are flagged for visual review; a duplicate may be intentional in a held/static shot.",
        "resolution": [width, height],
        "fps": fps,
        "detected_black_segments_over_one_second": black_segments,
        "lip_sync": lip_sync_report,\n        "audio_inputs": {"voice": str(a.voice.resolve()) if a.voice else None,
                         "voice_duration_seconds": voice_duration,
                         "music": str(a.music.resolve()) if a.music else None,
                         "captions": str(a.captions.resolve()) if a.captions else None},
        "metadata": metadata,
        "workdir": str(work)
    }
    (work / "final_report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))
    progress("COMPLETE", message=str(output))


if __name__ == "__main__":
    main()
