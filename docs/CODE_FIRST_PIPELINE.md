# Blender-Free Code-First Video Pipeline

## Architecture
The active rendering stack is Panda3D + Python + FFmpeg/ffprobe. Blender and `bpy` are not allowed.

1. Claude Code inspects the connected target repository and authors story-specific storyboard data.
2. Python validates the storyboard and resolves media/assets.
3. Panda3D creates scene graphs, geometry, materials, lighting and cameras, then renders real PNG frames.
4. FFmpeg encodes each shot, joins the shots, adds captions and mixes supplied narration/music.
5. ffprobe validates streams, codec, dimensions, fps and duration.
6. A human or visual inspection step checks representative frames for continuity, composition and semantic correctness.

## Rendering modules
- `runtime/panda3d_scene.py`: renders a single shot in an offscreen Panda3D context.
- `runtime/render_panda_story.py`: orchestrates all shots, audio/subtitles, MP4 output and technical QA.
- `runtime/align_visemes.py`: optional Rhubarb cue conversion; actual mouth motion requires a rig with compatible facial controls.

## Cloud execution
Use GitHub Actions or another explicitly configured worker. On Linux headless runners, install FFmpeg, Panda3D and Xvfb/software OpenGL. Do not assume a GPU. Use small preview renders first, then render final shots in bounded jobs and upload MP4/report artifacts. GitHub artifact retention and runtime limits must be documented.

## Asset and animation policy
Panda3D is a general-purpose real-time engine, not an automatic character creation system. Use legally usable GLB/glTF assets and verify importer support. Use exact rig/control mappings for skeletal or facial animation; never assume arbitrary assets share bone names. Primitive-only scenes are suitable for tests and blocking, not a substitute for detailed final art.

## Quality gates
Compilation is not rendering. A command exit code is not visual QA. Every integration test must generate actual frames and an MP4, inspect frame signatures/dimensions/count, run ffprobe, verify audio when requested, and retain logs. Visual QA must inspect frames and report defects; technical checks alone do not prove cinematic quality.
