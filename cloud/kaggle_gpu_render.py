#!/usr/bin/env python3
"""Kaggle GPU worker. Run via:
blender -b shot.blend --python cloud/kaggle_gpu_render.py -- --output-dir /kaggle/working/frames
Use Cycles for NVIDIA CUDA/OptiX acceleration; Eevee is not automatically accelerated by CUDA.
"""
import argparse, json, sys
from pathlib import Path
import bpy

def main():
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    p = argparse.ArgumentParser()
    p.add_argument("--output-dir", required=True)
    p.add_argument("--force-cpu", action="store_true")
    a = p.parse_args(argv)
    out = Path(a.output_dir).resolve()
    out.mkdir(parents=True, exist_ok=True)
    scene = bpy.context.scene
    report = {"engine": scene.render.engine, "requested_device": "CPU", "gpu_devices": []}
    if scene.render.engine == "CYCLES" and not a.force_cpu:
        try:
            prefs = bpy.context.preferences.addons["cycles"].preferences
            for backend in ("CUDA", "OPTIX"):
                try:
                    prefs.compute_device_type = backend
                    prefs.get_devices()
                    devices = []
                    for device in prefs.devices:
                        device.use = device.type != "CPU"
                        if device.type != "CPU":
                            devices.append({"name": device.name, "type": device.type})
                    if devices:
                        scene.cycles.device = "GPU"
                        report["requested_device"] = backend
                        report["gpu_devices"] = devices
                        break
                except Exception:
                    continue
            if not report["gpu_devices"]:
                scene.cycles.device = "CPU"
                report["gpu_fallback"] = "No compatible CUDA/OptiX device detected."
        except Exception as exc:
            scene.cycles.device = "CPU"
            report["gpu_fallback"] = str(exc)
    scene.render.filepath = str(out / "frame_")
    report.update({"resolution": [scene.render.resolution_x, scene.render.resolution_y],
                   "fps": scene.render.fps, "frame_range": [scene.frame_start, scene.frame_end]})
    print("KAGGLE_RENDER_CONFIG " + json.dumps(report), flush=True)
    bpy.ops.render.render(animation=True)
    report["status"] = "RENDERED"
    (out / "render_report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    print("KAGGLE_RENDER_COMPLETE " + json.dumps(report), flush=True)

if __name__ == "__main__":
    main()
