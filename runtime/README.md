# Panda3D Runtime

This is the active Blender-free runtime.

## Requirements
- Python 3.10+
- `panda3d==1.10.15`
- `panda3d-gltf==1.3.0` for GLB/glTF loading
- FFmpeg and ffprobe on PATH
- A working graphics backend. For Linux headless CI, use Xvfb/software OpenGL.

Install Python packages from the repository root:
```bash
python -m pip install -r requirements.txt
```

## Render
```bash
python runtime/render_panda_story.py --storyboard templates/storyboard.universal.example.json --output output/demo.mp4 --format shorts
```

The orchestrator starts a Panda3D renderer for each shot, writes numbered PNG frames, validates signatures/count/dimensions, encodes segments with FFmpeg, concatenates them, optionally adds captions/voice/music, and verifies the final MP4 with ffprobe. It writes a `final_report.json` in the work directory.

## Scene schema
Each shot can contain:
- `environment.world_color` and `environment.objects`;
- `subjects[]` with `parts[]`, optional imported `asset`, and transform keyframes;
- `props[]` with geometry/assets and transform keyframes;
- `camera.location`, `camera.target`, optional FOV and camera keyframes;
- `lighting[]` for additional directional lights.

Transforms use 3D arrays. Keyframes use `time_seconds` and optional `location`, `rotation`, and `scale`. Primitive geometry is useful for blocking, prototypes, scientific visuals and tests; final cinematic characters/environments should use suitable licensed assets and detailed materials.

## Honest limitations
Panda3D does not automatically create professional characters, rigs, motion capture, facial shapes or physically correct hand-object interaction. Those require compatible assets and animation systems. The runtime currently supports transform keyframes and imported models; it must not claim universal skeletal retargeting or auto-rigging. Inspect actual frames and logs for every final render.
