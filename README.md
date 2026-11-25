# Universal Cinematic Video Engine — Claude Code Skill

A reusable Claude Code Skill and Blender-free Python runtime for building universal 3D story and documentary videos.

## Technology
- **Panda3D**: primary 3D scene graph, geometry, camera, lighting and offscreen rendering.
- **Python**: story/shot orchestration, asset handling and automation.
- **FFmpeg + ffprobe**: MP4 encoding, audio/subtitle processing and technical QA.
- **panda3d-gltf**: optional GLB/glTF model loading.
- **Three.js**: optional web preview, not required for cloud rendering.

Blender and `bpy` are prohibited. The runtime does not require Blender or local 3D software on the user's Windows 7 computer.

## Install as a Claude Code Skill
Place this repository in `.claude/skills/animation-skill` or package it as a ZIP Skill. The entry point is `SKILL.md`.

## Runtime setup
Use Python 3.10+ and install:
```bash
python -m pip install -r requirements.txt
```
Install FFmpeg and ffprobe and ensure they are on PATH.

## Render a storyboard
```bash
python runtime/render_panda_story.py --storyboard templates/storyboard.universal.example.json --output output/story.mp4 --format shorts
```
For narration, music or subtitles:
```bash
python runtime/render_panda_story.py --storyboard story.json --output story.mp4 --voice narration.wav --music music.mp3 --captions captions.srt
```

The renderer generates real Panda3D 3D frames and assembles them into MP4. Imported GLB/glTF assets need the optional Panda3D glTF loader declared in requirements. The example storyboard is a schema reference, not a claim of finished film quality.

## Important limitations
Panda3D provides a real-time 3D engine, not an automatic character modeller or universal auto-rigger. High-quality character animation requires compatible rigged assets and tested animation/control mappings. Historical accuracy requires research and source references. Always inspect rendered frames before calling a video complete.

## Project layout
- `SKILL.md`: Claude Code instructions and production standards.
- `runtime/panda3d_scene.py`: one-shot Panda3D scene renderer.
- `runtime/render_panda_story.py`: multi-shot, FFmpeg, audio and MP4 QA pipeline.
- `runtime/align_visemes.py`: optional Rhubarb-to-viseme cue conversion.
- `docs/`: architecture and workflow guidance.
- `tests/`: renderer and utility tests.
