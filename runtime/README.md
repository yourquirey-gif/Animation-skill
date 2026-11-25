# Local Runtime

The skill bundles executable Python tools for environment inspection and a real Blender-to-FFmpeg integration test.

Requirements: Blender executable (with bundled Python/bpy), FFmpeg with libx264, ffprobe, and Python 3.10+ for orchestration.

Run from the skill folder:

    python runtime/animation_runtime.py inspect
    python runtime/animation_runtime.py smoke-test --workdir animation_work/smoke_test

Optional executable overrides: BLENDER_BIN, FFMPEG_BIN, FFPROBE_BIN.

The smoke test creates actual animated 3D geometry, a prop, terrain, camera and lights; renders PNG frames with Blender; encodes MP4 with FFmpeg; and checks the result with ffprobe. It saves a .blend, frames, logs and a JSON report.

This is a technical integration test, not a finished story or proof of cinematic art quality. Each user story still needs its own characters, props, environments, actions, camera and lighting implementation, followed by preview inspection.

Use Blender's embedded Python for bpy. The supported invocation is Blender background mode with --python and --python-exit-code 1. Do not assume system Python can import bpy, and avoid GUI-only operators in headless scripts.
