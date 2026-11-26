#!/usr/bin/env python3
"""Build self-contained per-shot .blend files for manual SheepIt submission."""
import argparse, json, os, shutil, subprocess, zipfile
from pathlib import Path

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--storyboard", required=True, type=Path)
    p.add_argument("--output", required=True, type=Path)
    p.add_argument("--blender", default=os.environ.get("BLENDER_BIN", "blender"))
    p.add_argument("--width", type=int, default=1080)
    p.add_argument("--height", type=int, default=1920)
    p.add_argument("--fps", type=int, default=30)
    p.add_argument("--samples", type=int, default=16)
    p.add_argument("--engine", choices=("BLENDER_EEVEE", "CYCLES"), default="CYCLES")
    p.add_argument("--voice", type=Path)
    p.add_argument("--music", type=Path)
    p.add_argument("--captions", type=Path)
    a = p.parse_args()
    storyboard = a.storyboard.resolve()
    data = json.loads(storyboard.read_text(encoding="utf-8"))
    shots = data.get("shots")
    if not isinstance(shots, list) or not shots:
        raise ValueError("Storyboard must contain a non-empty shots array.")
    repo_root = Path(__file__).resolve().parent.parent
    scene_script = repo_root / "runtime" / "story_scene.py"
    work = a.output.resolve().parent / (a.output.stem + "_package")
    if work.exists():
        shutil.rmtree(work)
    work.mkdir(parents=True)
    manifest = {"story_id": data.get("story_id") or data.get("title") or storyboard.stem,
                "backend": "SheepIt/Kaggle external render package", "shots": [], "media": {}}
    env = os.environ.copy()
    env["ANIMATION_RENDER_ENGINE"] = a.engine
    for index, shot in enumerate(shots):
        shot_id = str(shot.get("id") or "shot-%03d" % (index + 1))
        safe_id = "".join(c if c.isalnum() or c in "-_" else "-" for c in shot_id)
        shot_dir = work / ("%03d-%s" % (index + 1, safe_id))
        shot_dir.mkdir(parents=True)
        command = [a.blender, "--background", "--factory-startup", "--python-exit-code", "1",
                   "--python", str(scene_script), "--", "--storyboard", str(storyboard),
                   "--shot-index", str(index), "--output-dir", str(shot_dir),
                   "--width", str(a.width), "--height", str(a.height), "--fps", str(a.fps),
                   "--samples", str(a.samples), "--export-blend-only"]
        print("EXPORTING_SHOT", shot_id, flush=True)
        subprocess.run(command, check=True, env=env)
        blend, report_path = shot_dir / "shot.blend", shot_dir / "shot_report.json"
        if not blend.is_file() or not report_path.is_file():
            raise RuntimeError("Blender did not produce a self-contained project for " + shot_id)
        report = json.loads(report_path.read_text(encoding="utf-8"))
        manifest["shots"].append({"id": shot_id, "blend": str(blend.relative_to(work)),
            "duration_seconds": float(shot["duration_seconds"]), "frames": int(report["frames"]),
            "fps": int(report["fps"]), "resolution": report["resolution"],
            "engine": report["render_engine"]})
    (work / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    (work / "SHEEPIT_README.md").write_text(
        "# SheepIt upload package\n\n"
        "Upload each shot .blend as its own animation project through the SheepIt website. "
        "Keep its configured frame range, FPS and resolution. Download the rendered frame "
        "sequence and assemble shots/audio/captions with the normal FFmpeg pipeline.\n\n"
        "This ZIP does not automate account login, project submission or frame download. "
        "SheepIt does not execute owner-authored custom render scripts; the scene is baked "
        "into each packed .blend before upload. Queue time and available compute vary.\n",
        encoding="utf-8")
    media_dir = work / "media"
    for media_name, media_path in (("voice", a.voice), ("music", a.music), ("captions", a.captions)):
        if media_path:
            source = media_path.resolve()
            if not source.is_file():
                raise FileNotFoundError(str(source))
            media_dir.mkdir(parents=True, exist_ok=True)
            destination = media_dir / (media_name + source.suffix.lower())
            shutil.copy2(source, destination)
            manifest["media"][media_name] = str(destination.relative_to(work))
    (work / "source_storyboard.json").write_text(json.dumps(data, indent=2), encoding="utf-8")
    kaggle_worker = repo_root / "cloud" / "kaggle_gpu_render.py"
    if kaggle_worker.is_file():
        shutil.copy2(kaggle_worker, work / "kaggle_gpu_render.py")
    a.output.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(a.output, "w", zipfile.ZIP_DEFLATED, compresslevel=6) as archive:
        for file in sorted(work.rglob("*")):
            if file.is_file():
                archive.write(file, file.relative_to(work))
    print(json.dumps({"status": "PACKAGE_READY", "output": str(a.output),
                      "shot_count": len(shots), "shots": manifest["shots"]}, indent=2))

if __name__ == "__main__":
    main()
