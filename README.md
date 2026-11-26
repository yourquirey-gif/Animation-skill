# Animation Skill for Claude Code

A reusable Claude Code Skill for generating original 3D animated stories and realistic documentary scenes through Blender Python, FFmpeg and cloud rendering.

## Install as a Skill

Clone or place this repository at `.claude/skills/animation-skill` in the project where Claude Code runs. The entry point is `SKILL.md`.

## Blender cloud rendering (Windows 7 compatible)

The user's local PC is not used for rendering. In Claude Code Web, use GitHub Actions Ubuntu runners:

1. Commit a storyboard JSON and any permitted asset/audio files to the connected repository.
2. Open **Actions → Cloud Blender Video Render → Run workflow**.
3. Select the storyboard, output format, Blender engine, resolution, FPS, samples and optional audio/captions.
4. Wait for the job to finish.
5. Download the MP4 and QA logs from the workflow's **Artifacts** section.

The workflow installs Blender and FFmpeg on Ubuntu, renders each shot in background mode, encodes the video, verifies it with ffprobe and uploads a downloadable artifact. Standard runners are CPU/software-rendered unless a GPU is explicitly detected. Default settings are preview quality; full-HD jobs consume more time and runner resources.

## Free external render backends

- **SheepIt:** run the `Export SheepIt Render Package` workflow to build self-contained per-shot `.blend` files, then upload them to SheepIt.
- **Kaggle:** use `cloud/kaggle_blender_renderer.ipynb` with a free GPU session; export scenes with `CYCLES` for NVIDIA GPU acceleration.
- Details and limitations: `docs/EXTERNAL_RENDER_BACKENDS.md`.

These services are not silently assumed to be connected. SheepIt account submission/download and Kaggle GPU session startup require the user's authenticated session.

## Existing renderer

- `runtime/story_scene.py`: JSON-to-Blender scene compiler.
- `runtime/render_story.py`: scene-by-scene Blender rendering, bounded retries, progress, FFmpeg assembly and ffprobe validation.
- `runtime/animation_runtime.py`: dependency inspection and real Blender/FFmpeg smoke test.
- `runtime/asset_catalog.py`: reusable asset catalog validation and search.
- `runtime/align_visemes.py`: optional Rhubarb cue-to-viseme conversion.

## Reusable assets

Add legally usable models and textures under `assets/`, register each file in `assets/catalog.json`, and include accurate license/source/attribution metadata. The repository provides the catalog system and camera/lighting/environment preset metadata; it does not claim to ship a large library of production-ready characters or environments. Validate with `python runtime/asset_catalog.py validate`.

## Local development

Local Blender is optional for developers who have a compatible machine. It is never required from the user. The same renderer can be run locally for debugging, but production rendering for Claude Code Web must use cloud Actions.

## Documentation

- `SKILL.md`: main Claude Code instructions.
- `docs/CLOUD_RENDERING.md`: exact cloud job workflow and setup.
- `docs/APP_IMPLEMENTATION_SPEC.md`: application implementation contract.
- `docs/CODE_FIRST_PIPELINE.md`: story-to-video architecture.
- `docs/INTERACTIVE_INTAKE_AND_PRODUCTION.md`: idea/script/audio intake and story design.
- `assets/README.md`: asset catalog and licensing rules.

## Honest completion standard

A successful Blender smoke render proves the cloud toolchain works for the tested fixture; it does not prove arbitrary stories are feature-film quality. Inspect the actual MP4 and report missing assets, rig limitations, visual defects, resource constraints and untested features. Never substitute a slideshow for real 3D animation.
