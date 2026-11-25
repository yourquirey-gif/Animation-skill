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

Production workflow defaults: 1080x1920 (9:16) for Shorts and 1920x1080 (16:9) for Long, both at 30 FPS. Width/height inputs may override these defaults; FPS can also be changed. Smoke tests deliberately remain low-resolution. The cloud-render workflow also runs on pushes affecting runtime or story fixtures, using the Shorts Full-HD/30 FPS default when no manual inputs are supplied; this is the target-profile regression check, not a guarantee that every complex scene fits the hosted runner. Standard GitHub-hosted runners are CPU/software-rendered unless a GPU is explicitly detected; no GPU is assumed, so complex 1080p renders may be slow or hit the workflow's 45-minute limit.

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

## Real humanoid animation retargeting

A subject can import a rigged character and a separate animation pack, then bake the animation onto the character's own armature:

```json
{
  "name": "Palace_Guard",
  "asset_file": "characters/guard.glb",
  "retarget": {
    "animation_file": "animations/UAL1_Standard.glb",
    "source_armature": "Armature",
    "source_action": "Walk",
    "action_name": "Guard_Walk",
    "frame_start": 1,
    "frame_end": 48,
    "copy_root_motion": true,
    "root_translation_scale": 1.0,
    "bone_map": [
      {"source": "root", "target": "Root"},
      {"source": "hips", "target": "Hips"},
      {"source": "spine", "target": "Spine"},
      {"source": "head", "target": "Head"}
    ]
  }
}
```

Bone names and action names above are examples only. Inspect the exact imported rig/action first. `rotation_offset` accepts 3 Euler radians or 4 quaternion values for per-bone axis correction. The first mapped bone receives root translation when `copy_root_motion` is true. Retargeting bakes local bone rotations; it does not automatically solve foot sliding, contact, scale mismatch or facial motion. The `runtime/rig_retarget.py` helper is covered by a Blender integration test.

The reference-style starting assets are documented in `assets/REFERENCE_STYLE_ASSETS.md`. The Quaternius character and animation packs are CC0 according to their official publisher pages, but their ZIP files are not bundled in this repository; download the Standard packs and place the extracted files under `assets/characters/` and `assets/animations/`. Keep large source packs out of Git unless intentionally required.

## Audio-aligned lip-sync

`runtime/align_visemes.py` converts Rhubarb cue JSON into viseme events and inserts a neutral-mouth reset at every cue end. For automatic orchestration, pass `--voice narration.wav --auto-lip-sync --rhubarb /path/to/rhubarb` to `render_story.py`. Each speaking subject must define a `viseme_map` with exact imported shape-key names (Rhubarb A-H); neutral X/REST resets all mapped mouth shapes to zero and needs no dedicated shape key. Rhubarb must be installed separately and run against the actual audio; the renderer does not invent phoneme timestamps. This is approximate mouth-shape alignment, not phoneme-perfect facial acting. Inspect close-up previews against the master narration.

## Honest quality limits

Panda3D is not part of the active renderer. Blender is the only 3D render engine in this project. Blender's presence does not automatically provide high-quality models, universal retargeting, motion capture, perfect lipsync, physically correct contacts, cloth, or photorealistic assets. These require suitable assets, rig mappings, story-specific implementation and visual inspection. A successful CI smoke test proves the cloud toolchain can render its fixtures, not that every arbitrary story is cinematic or production-ready.
