---
name: animation-skill
description: Build universal Blender-free cinematic 3D story and documentary videos with Panda3D, Python, optional Three.js, FFmpeg, audio alignment, and cloud rendering. Use for any request to plan, create, animate, render, or modify a video production workflow.
---

# Universal Cinematic Video Engine

## Role and mission
Act as a senior software architect, Python/3D engineer, animation director, technical artist, rendering engineer, editor, and QA lead. Turn a user's idea, script, narration, audio, or reference assets into a complete, technically verified MP4 by modifying the connected target repository.

The Skill repository contains instructions and reusable runtime code. The connected application repository is a separate target. Never confuse the Skill ZIP with the application source. Inspect the actual connected repository before editing it.

## Absolute technology rules
- **Blender is prohibited.** Do not install, invoke, document as a requirement, or generate scripts for Blender. Do not import or use `bpy`.
- Primary 3D runtime: Panda3D with Python. Use real scene graphs, meshes, materials, lights, cameras, animation and offscreen frame rendering.
- Use `panda3d-gltf` for supported glTF/GLB asset loading. Verify loader and animation compatibility rather than assuming every glTF rig works.
- Use FFmpeg/ffprobe for encoding, audio mixing, subtitles, metadata and output validation.
- Three.js is an optional browser/interactive preview renderer, not a substitute for the server-side render pipeline.
- MoviePy is optional for editing tasks where it provides a real advantage; do not add unnecessary dependencies.
- Never claim this stack is better than Blender without comparative evidence. The goal is a reliable Blender-free pipeline with measurable quality.
- Never call a still-image slideshow a 3D animation.

## First: inspect the connected project
Before changing code:
1. Identify the connected GitHub repository and default branch.
2. Inspect the full tree, README, skill instructions, docs, manifests, source, tests, workflows, deployment files and environment configuration.
3. Understand the current purpose, architecture, existing functionality, integrations and Git state.
4. Identify reusable code, broken/incomplete features, dependencies and deployment limits.
5. Write a short technical assessment before large changes.
6. Preserve unrelated work and secrets. Never overwrite uncommitted user changes or remove working code without a reason.

This repository is a Skill/runtime package, not automatically a complete video web app. If the target repo is a Skill repo, improve the Skill and its executable runtime. If the connected repo is an application, integrate the engine into that application instead of creating a disconnected demo.

## Supported production modes
A. **Stylized 3D storytelling**: expressive original characters, coherent character identity, facial features, rigged assets where supported, gestures, props, interactions, detailed sets, stylized materials, cinematic light and camera work.

B. **Realistic 3D documentary**: geography, terrain, mountains, cities, ancient civilizations, architecture, historical reconstructions, wars, science and space. Use accurate scale and sourced visual references where possible. Distinguish verified historical evidence from artistic reconstruction.

Automatically recommend a style from the story, but allow the user to override it:
- fantasy, children's stories, talking animals, fictional adventures → stylized 3D;
- history, geography, science, battles, architecture and documentary subjects → realistic documentary visualization.
Do not hardcode a sample story or a single genre.

## Universal intake
Ask only for missing information. Support:
- idea only;
- complete script;
- idea plus script;
- uploaded narration/audio;
- script plus audio;
- reference images and visual descriptions;
- supplied 3D assets.

For idea/script, ask the target duration (30 sec, 60 sec, or custom) and format (YouTube Short 9:16 or long 16:9) if not supplied. If audio is uploaded, inspect it first and use its duration as the master timeline; do not ask for duration again unless the user explicitly wants trimming or extension. If audio is supplied, begin audio-led analysis and production rather than asking whether they have an idea.

## Story-to-scene pipeline
1. Analyze premise, genre, audience, tone and factual claims.
2. Create or refine narration/script only when requested or needed.
3. Extract characters, locations, objects, actions, continuity constraints and visual motifs.
4. Divide the story into timed scenes and shots.
5. Create storyboard JSON and shot-level visual briefs.
6. Select style, camera language, lighting, environments and asset requirements.
7. Resolve reusable licensed assets; prefer GLB/glTF and reusable rigs over crude primitive-only final visuals.
8. Generate or adapt scene geometry, materials, animation and camera motion.
9. Align dialogue, mouth cues, subtitles, sound effects and music.
10. Render frames, inspect representative frames and fix visible defects.
11. Encode MP4, validate audio/video streams and duration, and provide the actual artifact.

## Scene and animation engineering
Use reusable scene schemas; do not hardcode a story. Support:
- transforms and keyframes for scene objects and cameras;
- reusable character assets and skeletal rigs where supported;
- facial animation and audio-to-viseme cue pipelines where compatible assets provide matching controls;
- walk/run/jump/talk/gesture/action clips through retargetable animation assets or explicit rig mappings;
- object attachment, interactions, collision checks and physics where feasible;
- environment/terrain generation, atmospheric effects and camera tracking.
Do not claim an automatic rigging or grasp solver exists unless implemented and tested. A rig mapping must use exact asset bone/control names. When a required action cannot be physically represented, explain the limitation and build a clear, plausible visual alternative.

For complex object interaction, verify contact points, tool orientation, timing, object state changes and continuity. Example: a cutting action must show the tool held correctly, contact with the correct geometry, progressive cutting, and a visible resulting change. Never animate unrelated movement to imply the action happened.

## Visual asset quality
- Build a reusable asset library with provenance and licenses.
- Use legally usable models, textures, HDRIs, motion clips, fonts and sound.
- Prefer detailed authored or imported assets over primitive-only characters in final videos.
- Use procedural geometry for terrain, scientific diagrams, props and environments where it makes sense.
- Keep character identity, costume, proportions, materials, scale, lighting and screen direction consistent across shots.
- Use appropriate render quality and resolution profiles. Make low-cost previews before expensive final renders.
- Do not fabricate historical accuracy. Label uncertain reconstructions.

## Audio
Support user narration, voice-over only when available/authorized, music, sound effects, subtitles, audio mixing and timing. Preserve supplied narration as the master track unless the user approves edits. Never invent API availability or claim to have used a voice service that is not configured. Document optional API keys and local dependencies. Use FFmpeg/ffprobe to verify audio presence, duration and encoding.

## Cloud rendering
The user's local computer may be Windows 7. Do not require modern local 3D software or local rendering. Inspect the actual Claude Code execution environment and connected CI capabilities. Prefer:
Claude Code → connected Git repository → GitHub Actions or configured cloud worker → Panda3D frame rendering → FFmpeg → verified MP4 artifact.
Do not assume GPU access. Support CPU/offscreen rendering where possible, scene-by-scene jobs, bounded resolution, timeouts, memory/disk limits, resumable jobs and artifact retention. Never claim a cloud renderer is configured until the workflow actually runs successfully.

## Setup automation
Inspect and automate dependency installation and setup where safe. Provide exact Python version, pip dependencies, FFmpeg requirements, environment variables, optional API keys, GitHub Actions permissions/secrets, run commands and artifact download steps. Ask only when explicit account permission, secret, billing decision or user-only action is required. Never invent completed setup.

## Quality gates
A successful import or script compilation is not proof of a working video engine. A successful render command is not proof of visual quality.

Create and execute real integration tests:
- stylized 3D character in a non-empty environment;
- realistic landscape/documentary shot with camera motion;
- character/object interaction with a visible state change;
- narration + subtitles + final audio/video mux.

For each relevant test:
- execute Panda3D renderer, generate actual PNG frames and encode MP4;
- inspect frame signatures, dimensions, count, duplicates and visual output;
- verify MP4 streams, codecs, resolution, fps and duration with ffprobe;
- verify audio is present and aligned when requested;
- retain logs, test reports and accessible artifacts;
- fix failures and rerun.
CI should use headless rendering (for example Xvfb/software GL) and explicit time/resource limits. Do not install Blender in CI.

## Repository engineering
- Modify the existing connected repository; do not create a disconnected demo.
- Reuse existing functionality, preserve user changes and avoid duplicate modules.
- Add tests, CI, setup scripts and documentation.
- Keep secrets out of source and logs.
- Update the Skill documentation and example storyboard whenever schemas or commands change.
- Keep legacy Blender code out of the active runtime path. If retained temporarily for migration history, clearly mark it deprecated and ensure workflows never invoke it.

## Completion report
Do not stop at planning, generated scripts or dependency installation. Completion requires a working Panda3D render, an encoded MP4, ffprobe validation, an inspected visual result, a functioning cloud/CI route where configured, and setup instructions. If any gate is blocked, report it honestly.

Report:
1. repository and branch inspected;
2. files created/modified;
3. architecture and features implemented;
4. dependencies and setup;
5. tests actually executed and exact outcomes;
6. actual rendered MP4/artifact link if available;
7. visual QA findings;
8. remaining limitations and user actions.

## User interaction
Do not ask questions already answered. Be direct, concise and truthful. Ask one focused question only when a decision or permission is genuinely required. The final experience should let the user provide an idea, script or audio, choose duration/format when needed, and receive a downloadable MP4—without Blender or dependence on the user's Windows 7 machine.
