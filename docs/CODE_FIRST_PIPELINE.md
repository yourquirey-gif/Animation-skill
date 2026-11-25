# Blender Cloud Production Pipeline

## Architecture

- **Claude Code Web**: inspect and modify the connected application repository, plan story/shot data, write code, and monitor CI.
- **GitHub repository**: stores skill instructions, Blender/Python source, storyboard JSON, reusable assets and metadata.
- **GitHub Actions Ubuntu runner**: installs Blender, FFmpeg and system graphics libraries; performs CPU/software-compatible headless rendering.
- **Blender + bpy**: builds 3D scene graphs, meshes, materials, armatures, keyframes, lights, cameras and rendered frames.
- **Python**: validates storyboards, manages assets, orchestrates shot rendering, retries, progress and QA.
- **FFmpeg/ffprobe**: encodes shots, concatenates scenes, burns subtitles, mixes audio and validates the final MP4.
- **Actions artifact**: provides the MP4, final report and logs for download.

The user's Windows 7 computer is not part of the rendering pipeline. Do not ask the user to install Blender or render locally. GPU acceleration is optional and must be detected; standard GitHub-hosted runners are treated as CPU/software rendering.

## Story-to-video flow

1. Inspect the actual target repository, Git state, existing modules, workflows, secrets requirements and asset availability.
2. Determine input mode: idea, script, audio, script+audio, reference images, or supplied production assets. Ask only for missing choices.
3. Analyze the story and audio timeline. Preserve supplied narration as the master timeline.
4. Select stylized 3D or realistic documentary style, with a user override.
5. Create story, character and location bibles; identify subjects, props, environments and continuity constraints.
6. Search the reusable asset catalog. Reuse only assets whose files, licenses, style and rig compatibility have been checked. Generate procedural replacements where appropriate.
7. Build a timed storyboard with actions, camera, lighting, environment motion, captions and sound cues.
8. Render a low-resolution preview on cloud first. Inspect representative frames and correct composition, geometry, animation and contact defects.
9. Run final Blender renders scene-by-scene with bounded retries and progress logs.
10. Use FFmpeg to encode/concatenate shots, apply captions and mix narration/music/SFX.
11. Use ffprobe and frame checks to validate duration, dimensions, FPS, codecs, frame count and audio streams.
12. Upload MP4, report and logs as a GitHub Actions artifact. Never commit rendered videos to source control.

## Reusable asset architecture

`assets/catalog.json` is the source of truth for asset metadata. The catalog records stable IDs, category, file path, format, visual style, tags, license, source URL, attribution, rig and animation compatibility. `runtime/asset_catalog.py` validates entries, checks repository-relative file existence, and supports category/style/tag searches.

Asset directories are organized by characters, rigs, animation clips, environments, props, materials, textures, HDRIs, audio, camera/lighting presets and scene templates. Empty directories are not assets. Never fabricate model files, previews or licenses. Register only actual, legally usable files. If no suitable model is present, create a procedural asset or clearly report the quality/rig limitation.

## Animation and interaction

Use Blender actions/NLA, armatures, exact bone mappings, IK constraints, shape keys, visemes and physics only where suitable. Reuse compatible animation assets but inspect skeleton structure before retargeting. Handheld props must be attached to actual rig bones with preview-tuned offsets; finger closure and contact require rig-specific controls. A generic walk cycle is not proof of foot planting or terrain-aware locomotion. Story-specific actions must have start state, movement, contact and end state.

## Cloud job controls

`.github/workflows/cloud-render.yml` supports manual dispatch with storyboard path, output name, format, render engine, dimensions, FPS, samples and optional narration/music/captions paths. The workflow validates paths and numeric bounds, reports runner resources, installs Blender/FFmpeg, validates the asset catalog, executes the real renderer, and uploads the MP4/report/logs for seven days.

Default values are intentionally preview quality. Use full HD/30 FPS only after a preview and resource estimate. Jobs have timeouts; GitHub Actions minutes, disk, RAM, artifact size and retention are finite. No GPU or unlimited render capacity is assumed.

## Quality gates

- Compile Python orchestration.
- Execute Blender headless; compilation alone is not rendering.
- Render actual frames and inspect PNG signatures/count/dimensions.
- Validate output MP4 streams, duration, dimensions, FPS and audio with ffprobe.
- Inspect representative frames and the complete video where possible.
- Check character continuity, hands/props, geometry, camera, lighting, captions and audio sync.
- Keep failed logs and progress state; rerender only failed shots.
- Distinguish technical CI PASS from cinematic/artistic PASS.

## Limitations that must be disclosed

Blender is a general-purpose 3D suite, not an automatic professional character modeller or universal auto-rigger. The asset catalog begins as a registry and preset library; it does not contain a prebuilt paid-quality asset collection. Realistic documentary quality requires detailed, historically appropriate assets and fact checking. Motion capture, universal animation retargeting, advanced cloth, complex fracture, physically exact hand interactions and perfect lip-sync require additional assets/systems and dedicated tests.
