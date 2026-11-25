# Blender Cloud Runtime

The production renderer is **Blender + bpy**, orchestrated by Python and assembled/validated by FFmpeg/ffprobe. In Claude Code Web, all 3D rendering must happen on GitHub Actions Ubuntu runners. The user's Windows 7 computer is not a rendering host and must not be asked to install Blender.

## Cloud render workflow

GitHub Actions workflow: `.github/workflows/cloud-render.yml`

1. Open the repository on GitHub.
2. Select **Actions → Cloud Blender Video Render → Run workflow**.
3. Choose a storyboard JSON already committed to the repository, output name, aspect ratio, Blender engine, resolution, FPS, samples, and optional repository-relative voice/music/SRT paths.
4. The Ubuntu runner installs Blender, FFmpeg and headless graphics libraries, reports CPU/RAM/disk/GPU availability, validates inputs, and runs the real renderer.
5. Each shot is rendered separately in Blender background mode. Failed shots get a bounded retry; progress is written to JSON and logs are retained.
6. FFmpeg encodes and joins shot frames, applies captions and mixes audio. ffprobe validates the final MP4.
7. The workflow uploads the MP4, final report, progress record and render logs as a downloadable Actions artifact (7-day retention).

The default workflow settings are deliberately low-resolution smoke/preview values to stay within hosted-runner limits. Select 1080x1920 for Shorts or 1920x1080 for Long only after a preview confirms the scene and the expected render time is acceptable. Standard GitHub-hosted runners are CPU/software-rendered unless a GPU is explicitly detected; no GPU is assumed.

## Local development / tests

A developer with Blender installed may run the same pipeline locally:

```bash
python runtime/animation_runtime.py inspect
python runtime/animation_runtime.py smoke-test
python runtime/render_story.py --storyboard tests/fixtures/human_prop_story.json --output output/test.mp4 --format shorts
python runtime/asset_catalog.py validate
```

Use Blender's bundled Python for `bpy`; do not pip-install `bpy` into arbitrary system Python. Set `BLENDER_BIN`, `FFMPEG_BIN`, and `FFPROBE_BIN` only when executable discovery needs an override.

## Storyboard renderer

`runtime/render_story.py` reads story-specific JSON and launches Blender once per shot. It renders actual PNG frames, validates frame count/signature/dimensions, encodes each shot with FFmpeg, concatenates the shots, optionally burns SRT captions and muxes voice/music, then checks the final MP4 with ffprobe. It supports bounded shot retries and machine-readable progress via `--progress-file`. Work directories contain `.blend` files, frames, logs, and `final_report.json` for diagnosis/resume.

## Detailed model assets

Storyboard entries may use `asset_file` instead of a procedural primitive. Supported imports are `.glb`, `.gltf`, and `.fbx`; relative paths resolve from the storyboard JSON file. GLB/glTF is preferred for embedded PBR materials and hierarchy. An optional `asset_action` selects an imported Blender action by exact name. Keep every model's source, license, attribution, rig and animation compatibility in `assets/catalog.json`. Use:

```bash
python runtime/asset_catalog.py validate
python runtime/asset_catalog.py search --query "roman soldier" --style realistic
python runtime/asset_catalog.py list --category characters
```

The registry contains metadata and presets, not a bundled collection of finished commercial-grade models. Add only assets whose files and licenses have been verified. The catalog tool checks metadata and file existence; it cannot certify model quality, rig compatibility or legal rights.

## Rigged character animation and facial performance

For a detailed character model, provide an imported rigged GLB/glTF or FBX with its armature and (for facial animation) shape keys/blendshapes. A subject entry may use `asset_file`, `asset_action`, `pose_keyframes`, `facial_keyframes`, and `rig_controls`. Bone and shape-key names are asset-specific: inspect the imported model and use its actual names. The runtime supports explicit bone pose keys, mapped IK targets, finger-control keys, locomotion mappings, facial shape keys and viseme events. These are rig-specific controls, not a universal auto-rigger or a fully automatic hand-grasp solver.

## Props attached to character hands/bones

Use `attach_to` on a prop with the subject name and exact armature bone name. Tune local offset/rotation from preview renders. Bone parenting makes the prop follow the animated hand; it does not itself solve finger closure, collision or contact physics.

## Audio-aligned lip-sync

`runtime/align_visemes.py` converts Rhubarb cue JSON into viseme events. Rhubarb must be installed separately and run against the actual audio; the renderer does not invent phoneme timestamps. The viseme map must match the model's real blendshape names. Inspect close-up previews against the master narration.

## Honest quality limits

Panda3D is not part of the active renderer. Blender is the only 3D render engine in this project. Blender's presence does not automatically provide high-quality models, universal retargeting, motion capture, perfect lipsync, physically correct contacts, cloth, or photorealistic assets. These require suitable assets, rig mappings, story-specific implementation and visual inspection. A successful CI smoke test proves the cloud toolchain can render its fixtures, not that every arbitrary story is cinematic or production-ready.
