# Code-First Animation: End-to-End Production

This document defines the default implementation strategy when the user says to make the complete video using code. Do not assume a paid AI video API is required. First build the strongest local, reproducible pipeline with code and installed tools. Optional external AI providers are an enhancement, not a prerequisite.

## 1. What "make the video with code" means

Claude Code is the coding agent: it writes the scripts, procedural scene descriptions, animation timelines, render automation, audio/subtitle processing, and tests. The actual rendering is performed by installed software such as Blender and FFmpeg. Do not claim Claude Code itself is a video renderer.

The default target is a complete, reproducible, code-generated animated video:
- Procedurally construct 3D characters, props, sets, terrain, and environments.
- Create meshes, materials, textures, rigs, lights, cameras, and animation using Blender's Python API.
- Animate characters and objects using keyframes, constraints, drivers, inverse kinematics where practical, shape keys, and physics where useful.
- Render real frames from a 3D scene.
- Generate or synthesize audio, create subtitles, mix tracks, and assemble the final MP4 using code.

A local code-first workflow can create genuine animated 3D scenes without image-to-video APIs. It may not automatically equal the detailed organic look of a high-end AI-generated reference; measure the gap and improve the scene assets, rigging, shaders, lighting, animation, and rendering. Never hide that limitation.

## 2. Inspect the execution environment first

Before coding, inspect:
- OS and available CPU/GPU/RAM/disk.
- Blender availability and version.
- FFmpeg/ffprobe availability and codecs.
- Python version and installed packages.
- Available fonts and audio tools.
- Existing project files and reference videos.

Use shell commands such as:
- `blender --version`
- `ffmpeg -version`
- `ffprobe -version`
- `python --version`
- GPU/system inspection commands appropriate to the OS.

If Blender is unavailable, determine whether it can be installed in the user's environment. Explain required disk space and rendering performance. Do not silently switch to a still-image slideshow if Blender cannot run; report the blocker and offer a clearly labelled fallback.

## 3. Default local toolchain

Preferred stack:
- Blender + bpy: procedural 3D scene creation, modeling, rigging, animation, lighting, camera, rendering.
- Python: story parsing, shot manifests, asset generation, orchestration, validation, subtitles, and tests.
- FFmpeg/ffprobe: audio/video assembly, encoding, muxing, probing, and final validation.
- Optional local TTS/audio tools: use only if installed and suitable; inspect licenses and language/voice quality.
- Optional local image/audio generation tools: use only when installed and user-approved.

Do not add cloud APIs by default. Do not require API keys for the basic local pipeline. If optional paid or hosted providers would materially improve results, describe why, show costs/limits, and wait for approval before using them.

## 4. Build a reusable code architecture

Create modular code rather than one giant script. Adapt names to the existing repository, but aim for modules equivalent to:

- `src/story/`: story input, beat extraction, scene timing, storyboard schema.
- `src/characters/`: character specifications, procedural models, materials, rigs, reusable poses.
- `src/environments/`: procedural sets, terrain, buildings, vegetation, props, sky and atmosphere.
- `src/animation/`: action libraries, walk/run/talk/gesture/fight cycles, facial expressions, object interactions, camera animation.
- `src/blender/`: Blender scene builder, render settings, lighting and render orchestration.
- `src/audio/`: narration import/generation, sound effects, music beds, mixing and loudness checks.
- `src/subtitles/`: transcript timing, SRT/ASS generation, safe-area layout.
- `src/editing/`: FFmpeg assembly, transitions, titles, audio mix and export.
- `src/qa/`: render inspection, metadata validation, black/frozen-frame checks, audio/subtitle checks.
- `projects/<id>/`: story, character/location bibles, scene manifests, generated assets, renders and logs.
- `scripts/`: setup, preview, render, resume, package and validate commands.

Keep story data separate from rendering code. Use JSON/YAML schemas with validation. Record deterministic random seeds so procedural assets can be reproduced.

## 5. Procedural 3D character construction

Create a reusable stylized 3D character system in Blender:
- Parametric body proportions and silhouette controls.
- Separate head, torso, limbs, hands, feet, hair, clothing, and accessories where useful.
- Materials with controlled roughness, specular response, skin/hair/cloth variation.
- Face geometry and/or shape keys for eyes, brows, mouth, blinks, and expressions.
- A consistent armature and named bones.
- Reusable poses and animation actions.
- Character-specific configuration stored outside the Blender script.

Prefer clean topology and deformation-friendly joints. Use a modular rig that can be reused across characters. Make visual quality improvements through silhouettes, facial proportions, clothing layers, hair shapes, material quality, eye design, and lighting—not by adding random detail.

Do not claim a character is production-quality merely because a primitive mannequin exists. Build and render a close-up and full-body turntable preview, inspect them, and iterate before using the character in all scenes.

## 6. Animation system

Build actual timed animation, not static renders:
- Walk/run cycles with foot contact and body weight shifts.
- Idle breathing and subtle head/eye motion.
- Hand and arm gestures.
- Head turns and gaze targets.
- Dialogue mouth movement driven by phonemes/visemes when transcript timing exists; otherwise use a clearly described approximate dialogue animation.
- Emotion poses and facial shape-key transitions.
- Object interactions with explicit grip points, parent constraints, contact timing, and release.
- Fight/action choreography broken into understandable beats.
- Environment motion such as wind, water, fire, smoke, particles, and moving crowds where feasible.
- Camera animation with establishing, wide, medium, close-up, tracking, pan, tilt, and dolly shots.

Use Blender keyframes, action/NLA tracks, constraints, IK, drivers, shape keys, particle systems, and physics as appropriate. Ensure scene frame ranges and action timing match the storyboard.

## 7. Environments and props

Create reusable procedural assets:
- Terrain and mountains with coherent connected geometry and a defined visible silhouette.
- Buildings with consistent architectural logic and complete roofs/walls.
- Roads, paths, floors, and ground contact.
- Trees, rocks, vegetation, water, sky, clouds, and atmospheric depth.
- Handheld props and tools with correct dimensions and grip points.

For important story props, create a dedicated model and interaction setup. Example: a hammer must have a distinct head and handle; the hand grips the handle; the head is oriented toward the strike surface; contact occurs at the correct time. Do not let hands pass through props or props float.

Use location configuration to preserve geography, object placement, lighting direction, and recurring landmarks between shots.

## 8. Story-to-scene compiler

Convert story beats into structured scene data. Each shot must specify:
- Shot ID and duration.
- Set/location ID.
- Character IDs and initial positions.
- Action/action-library references.
- Prop IDs and object states.
- Camera type, position, target, lens, and movement.
- Lighting setup and time of day.
- Environment effects.
- Narration/dialogue timing.
- Render quality and output file.
- Continuity requirements and QA status.

Generate a scene manifest first, then build Blender scenes from that manifest. Do not let the language model improvise untracked scene changes during rendering.

## 9. Audio and subtitles using code

Audio can be supplied by the user or produced with locally available tools. Inspect local TTS options and their language support before choosing one. If no suitable local Hindi/English TTS is installed, allow the user to provide voice files; do not fabricate narration audio.

- Keep narration, dialogue, music, and SFX as separate tracks.
- Use actual audio duration and timestamps to align subtitles and mouth movement.
- Generate SRT/ASS subtitles programmatically.
- Mix with FFmpeg filters and prevent clipping.
- Ensure dialogue remains intelligible above music.
- Use licensed or user-provided music and effects. Do not copy copyrighted audio from reference videos.

## 10. Rendering strategy and performance

- Start with low-resolution, low-sample previews.
- Render a representative character close-up, full-body action, and environment test before the full video.
- Use render layers and reusable assets to avoid rebuilding everything.
- Use Eevee for faster previews and choose Cycles only when the visual improvement justifies the cost.
- Set samples, denoising, shadows, textures, and resolution according to available hardware.
- Render shots independently so failures can resume without restarting the entire project.
- Save Blender files and render logs.
- Do not promise render times without benchmarking the actual machine.
- Do not silently lower quality to fit memory limits; report the changed settings.

## 11. Reference matching loop

When reference videos are supplied:
1. Extract frames at representative timestamps.
2. Record aspect ratio, framing, shot duration, palette, lighting, character proportions, camera motion, depth of field, and editing rhythm.
3. Build a visual style guide.
4. Create a code-generated look-development scene.
5. Render a test frame and a short animated test.
6. Compare the output against the reference using side-by-side visual inspection.
7. Improve modeling, rigging, materials, lighting, camera, and timing.
8. Repeat until the user accepts the preview or the remaining gap is clearly documented.

Do not copy exact protected characters, logos, or copyrighted assets from references. Reproduce broad visual characteristics with original assets.

## 12. Commands and automation

Provide simple project commands, for example:
- `python -m app inspect`
- `python -m app storyboard --story story.txt`
- `python -m app preview --project projects/example`
- `python -m app render --project projects/example`
- `python -m app resume --project projects/example`
- `python -m app export --project projects/example`
- `python -m app validate --project projects/example`

These are examples: implement actual commands matching the chosen architecture. Every command must work and report real progress.

## 13. Acceptance gates

Do not proceed to full production until:
- A character turntable is rendered and inspected.
- A short action test shows real motion and acceptable rig deformation.
- A location preview is rendered and inspected.
- A camera test has correct framing.
- Audio/subtitle timing has been validated.
- A short end-to-end MP4 has been produced and probed.

For each gate, report pass/fail and the actual evidence. If a gate fails, fix it before scaling up.

## 14. Optional AI enhancement

Only after the local code-first pipeline is working, consider optional AI image/video/TTS providers for tasks where procedural code is insufficient. Provider use must be modular, documented, costed, and explicitly approved if paid. The local Blender workflow must remain usable without those providers.

## 15. Final delivery

Deliver:
- Source code and reusable procedural assets.
- Blender project files.
- Storyboard and character/location bibles.
- Rendered shot files and final MP4.
- Audio and subtitle files.
- Reproduction instructions and dependency list.
- Machine/render settings and actual render duration.
- QA report with known visual defects and limitations.

A real code-generated animated video means rendered 3D frames with moving geometry, rigs, camera, and environment. A sequence of still images with transitions is not an acceptable substitute.
