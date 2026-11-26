# Cloud Blender Rendering — Setup and Operations

## Purpose

This skill is used from Claude Code Web. The user's Windows 7 computer is not expected to install or run Blender. The connected public GitHub repository and GitHub Actions Ubuntu runner are the initial rendering infrastructure.

## What is already in the repository

- `runtime/story_scene.py`: actual Blender Python scene compiler.
- `runtime/render_story.py`: per-shot Blender rendering, FFmpeg assembly, bounded retry, progress JSON and ffprobe QA.
- `runtime/animation_runtime.py`: dependency inspection and Blender/FFmpeg smoke test.
- `runtime/asset_catalog.py`: asset metadata validation/search.
- `.github/workflows/runtime-smoke-test.yml`: automated Blender smoke render and cross-genre fixture renders.
- `.github/workflows/cloud-render.yml`: manually dispatched cloud video production workflow.
- `assets/catalog.json` and `assets/presets/`: reusable asset metadata and camera/lighting/environment preset definitions.

## Run a cloud render

1. Push/commit the storyboard JSON and any permitted production assets to the repository.
2. Open the repository's **Actions** tab.
3. Select **Cloud Blender Video Render**.
4. Select **Run workflow**.
5. Enter the repository-relative storyboard JSON path and output filename.
6. Choose Shorts or Long, Eevee or Cycles, dimensions, FPS and samples.
7. Add optional repository-relative voice, music and SRT paths only if those files are safe to store in the repository.
8. Start the job and inspect its logs.
9. When complete, download the MP4 artifact. The artifact also contains the final report, progress JSON and render logs when those files were produced.

The default resolution/FPS/samples are intentionally small preview values. For Shorts, final dimensions are 1080x1920; for Long, 1920x1080. Standard hosted runners may not finish a long full-HD/60-FPS Cycles render within the job timeout. Increase quality in stages and monitor runner resources.

## Private media and public repository warning

This repository is public. Never commit private voice recordings, personal reference videos, credentials, private client models or any asset the user does not want public. The workflow's optional media inputs currently resolve to files checked out from the repository. If a project uses private media, first configure a private repository or an approved private object-storage upload/download adapter. Do not put secrets or signed private URLs in storyboard JSON or logs. No external storage provider is configured by default.

## Permissions and secrets

The render workflow needs only repository contents read permission and the standard Actions artifact upload permission. The basic Blender/Python/FFmpeg renderer needs no paid API key. Optional transcription, TTS, cloud object storage or third-party asset services must be separately configured and approved; do not invent keys or claim those services are active.

If GitHub Actions is disabled by repository policy or usage limits, the owner must enable Actions or select a supported runner. The workflow cannot bypass repository policies or account limits.

## Asset library maintenance

1. Add a legally usable asset file under the appropriate `assets/` category.
2. Inspect the model in Blender: mesh integrity, scale, orientation, materials, armature, bone names, shape keys and animation actions.
3. Add an entry to `assets/catalog.json` with stable ID, category, path, format, visual style, tags, exact license, source URL, attribution, rig and animation compatibility.
4. Run `python runtime/asset_catalog.py validate`.
5. Test the asset in a small Blender render before reusing it in production.

The current repository contains a catalog and preset definitions, not a bundled commercial-grade character/animation collection. Do not label empty asset folders as finished assets. Use procedural geometry only as a documented replacement when a suitable detailed asset is unavailable.

## Troubleshooting

- **Blender executable missing**: inspect the Actions install step and Ubuntu package availability.
- **Unsupported engine**: select Eevee or Cycles available in the installed Blender build; requested engines now fail explicitly instead of silently falling back.
- **Missing model file**: check the storyboard-relative `asset_file` path and catalog registration.
- **Rig/bone error**: inspect the imported armature and use exact bone names; do not guess.
- **Shot failure**: download the per-attempt Blender log from the artifact, fix that shot, and rerun.
- **Runner timeout/OOM/disk**: reduce resolution, samples, frame count or scene complexity; render shots separately; do not claim full quality if settings were reduced.
- **Artifact absent**: inspect the final upload step and preceding render errors. An artifact upload warning is not proof an MP4 was generated.

## What a passing workflow proves

A passing render confirms that the selected storyboard was executed by Blender on that runner, MP4 assembly completed and the configured technical checks passed. It does not prove photorealism, feature-film quality, universal character retargeting, perfect lip sync, historical accuracy or correct hand contact. Those require visual inspection, suitable assets, rig-specific animation and dedicated acceptance tests.
\n\n## Free external render backends\n\nSee `docs/EXTERNAL_RENDER_BACKENDS.md`. The `Export SheepIt Render Package` workflow creates self-contained per-shot Blender projects. Upload them to SheepIt manually because its project-owner interface does not execute custom render scripts and no official authenticated submission/download integration is configured. The package also includes `kaggle_gpu_render.py`; `cloud/kaggle_blender_renderer.ipynb` is a Kaggle notebook template for rendering Cycles scenes on a free GPU when available. Neither service has guaranteed availability or unlimited compute.\n