---
name: animation-skill
description: Create complete cinematic animated story videos through code-first 3D production, Blender Python, procedural modeling, character rigs, animation, audio, subtitles, FFmpeg, and quality control. Use whenever the user asks to create or modify an animated story, storyboard, scene, character, animation pipeline, or video.
---

# Animation Skill

Use this skill for every animated-story task. Treat user-provided reference videos and images as the primary visual target. Do not claim a result matches a reference unless it has been inspected.

## Core standard

The default approach is to build the complete video using code. Claude Code writes the application, procedural assets, Blender Python scripts, animation timelines, audio/subtitle processing, render automation, and tests. Blender performs 3D rendering; FFmpeg performs media assembly. Do not assume a paid cloud AI video API is required.

Create real animated shots with moving 3D geometry, rigs, objects, camera, and environments—not a slideshow. Static images with pan/zoom are not animation. A code-first Blender pipeline is the default. Optional external AI providers are enhancements only and require user approval if paid.

Never promise exact replication of a reference. Aim for the closest achievable style and clearly report visual gaps, render time, hardware constraints, and technical limits.

## Mandatory code-first production workflow

1. Inspect the project, available assets, reference media, OS, CPU/GPU/RAM/disk, Python, Blender, FFmpeg/ffprobe, fonts, and audio tools before changing anything.
2. If Blender is missing, assess whether it can be installed and explain requirements. Do not silently replace 3D animation with a slideshow.
3. Analyze references when supplied: sample frames across the whole clip; inspect aspect ratio, frame rate, shot length, palette, lighting, character design, camera language, motion, subtitles, sound, and transitions. Write findings to docs/REFERENCE_STYLE_GUIDE.md.
4. Parse the story into beats, characters, locations, props, and chronological events. Preserve the user's plot and causal order.
5. Create a structured storyboard/scene manifest before rendering. Each shot records ID, duration, location, characters, initial positions, action, emotion, props, framing, camera/lens/movement, lighting, environment motion, narration/dialogue, SFX/music, continuity constraints, output path, and status.
6. Create a Character Bible and Location Bible. Record stable visual traits, wardrobe, scale, voice, props, geography, layout, lighting, and recurring details.
7. Build reusable procedural 3D characters, props, and environments using Blender's Python API (bpy). Create meshes, materials, textures, armatures, named bones, facial shape keys, camera rigs, lighting, and reusable scene assets.
8. Animate actual geometry using keyframes, action/NLA tracks, constraints, IK where practical, drivers, shape keys, particles, and physics where useful. Implement walk/run/idle/talk/gesture/action cycles and correct prop interactions.
9. Render real frames from Blender. Use low-quality previews first, inspect them, fix defects, then render final shots. Save .blend files and per-shot renders.
10. Generate or import narration, dialogue, music, and sound effects. Use locally available TTS/audio tools when suitable; otherwise ask for user-provided audio or approval for an optional provider. Do not fabricate audio.
11. Generate subtitles from actual audio timing. Mix audio and assemble scenes using FFmpeg.
12. Validate the final MP4 with ffprobe and visual/audio checks. Save manifests and intermediate assets so failed jobs can resume.

Read docs/CODE_FIRST_PIPELINE.md before implementing a complete code-generated video. It defines the architecture, procedural modeling, rigging, animation, rendering, audio, performance, reference matching, commands, and acceptance gates.

## Character and scene continuity

- Keep a canonical Character Bible entry and approved reference renders for each character.
- Reuse the same procedural model, rig, materials, proportions, hair, wardrobe, and accessories across every shot.
- Track screen direction, position, eyelines, time of day, weather, lighting, and object state across adjacent shots.
- For recurring locations, reuse the same environment assets and spatial descriptions.
- Check anatomy, hands, object contact, tool orientation, ground contact, shadows, and physical geography.
- A character holding a tool must grip it correctly; a hammer must be held by its handle and strike with its head.
- Mountains, buildings, and other structures must have complete, coherent geometry, not disconnected or missing sections.
- If a complex action fails, simplify its choreography, improve the rig, or split it into readable shots. Do not hide failure with a still image.

## Procedural 3D quality requirements

- Avoid primitive-only placeholder characters in final output.
- Build appealing silhouettes, facial proportions, eyes, hair, layered clothing, accessories, and coherent materials.
- Use deformation-friendly topology and a reusable armature.
- Create facial expressions and mouth movement with shape keys or an equivalent rig.
- Create turntable, close-up, full-body, and action previews before production.
- Use coherent terrain, architecture, ground planes, props, shadows, and spatial scale.
- Use Eevee for fast previews; choose Cycles when its quality improvement justifies the cost.
- Benchmark render speed on the actual machine. Never invent render-time estimates.

## Prompt and shot design

For every shot, provide:
- Subject and stable identity description.
- One clear primary action with beginning, middle, and end.
- Environment and relevant props.
- Composition, camera position, lens, and movement.
- Lighting, atmosphere, and visual style.
- Continuity constraints and explicit exclusions.
- Motion constraints (what moves, what stays still, direction, speed).

Avoid contradictory instructions, overloaded action lists, and unnecessary style changes between shots.

## Tooling and provider rules

- Prefer Blender + bpy, Python, and FFmpeg/ffprobe for the complete local pipeline.
- Inspect official documentation for tools and libraries before integration.
- Do not add cloud APIs by default. If an optional AI image/video/TTS provider would materially improve a result, explain capability, pricing, limits, and required credentials; obtain approval before paid usage.
- Keep optional providers behind adapters so the local pipeline remains usable without them.
- Keep secrets in environment variables; provide .env.example with names only.
- Do not expose keys in logs, UI, commits, or generated reports.
- Distinguish implemented, tested, mocked, and pending functionality.
- Never fabricate API responses, progress, successful renders, or quality scores.
- Add retries with bounded backoff, timeouts, job persistence, resumability, and clear error reporting.
- Respect software licenses, asset rights, and user-supplied asset permissions. Do not copy copyrighted music or protected characters from references.

## Audio and subtitles

- Keep narration, dialogue, music, and SFX as separate tracks.
- Align subtitle timing and mouth movement to actual audio timestamps.
- Generate SRT/ASS subtitles programmatically.
- Mix dialogue clearly above music and prevent clipping.
- Use licensed or user-provided audio. Never extract copyrighted music from reference videos.

## Default delivery profile

Unless the user specifies otherwise:
- Vertical short: 1080x1920, 9:16, 30 fps, MP4/H.264, AAC.
- Landscape: 1920x1080, 16:9, 30 fps, MP4/H.264, AAC.
- Render previews at lower resolution/samples first; render final quality only after preview approval.
- Keep captions inside platform-safe margins and readable on mobile.

## Acceptance gates

Before full production:
- Render and inspect a character turntable and close-up.
- Render and inspect a short action test with real character motion.
- Render and inspect a location preview.
- Validate camera framing and continuity.
- Validate audio/subtitle timing.
- Produce and probe a short end-to-end MP4.

Do not proceed as if a gate passed unless actual output exists and was inspected.

## Quality-control checklist

For every shot and final video, check:
- Correct story beat and chronological continuity.
- Character identity, face, body, clothing, and accessories.
- Anatomy, hands, contact, and object/tool orientation.
- Environment and spatial/geographical continuity.
- Motion plausibility, rig deformation, foot sliding, temporal flicker, and unwanted morphing.
- Camera movement, composition, exposure, lighting, and color consistency.
- Missing frames, black frames, corrupt clips, unintended freezes.
- Voice clarity, clipping, loudness balance, music/SFX levels.
- Subtitle wording, timing, spelling, placement, and safe margins.
- Exact output dimensions, frame rate, duration, codec, and audio stream.

Report failures honestly with shot IDs and corrective actions.

## Project artifacts

Prefer a clear structure such as:

- references/ — user-provided reference videos/images.
- docs/REFERENCE_STYLE_GUIDE.md — observed reference characteristics.
- docs/CODE_FIRST_PIPELINE.md — code-first implementation guide.
- docs/STORY_BIBLE.md — story facts and chronology.
- docs/CHARACTER_BIBLE.md — canonical character descriptions.
- docs/LOCATION_BIBLE.md — recurring environment descriptions.
- projects/<project-id>/storyboard.json — shot plan and status.
- projects/<project-id>/assets/ — procedural and approved assets.
- projects/<project-id>/blender/ — .blend scene files.
- projects/<project-id>/renders/ — shot and final renders.
- config/ — non-secret configuration.
- .env.example — optional provider variable names only.

Adapt to the existing repository rather than forcing this layout onto an established project.

## User interaction

Ask only for information that blocks progress. If reference media is missing, explain exactly where to put it. Do not ask the user to design every scene manually; take responsibility for story breakdown and code implementation. Before paid generation or purchases, show estimated cost and obtain approval. Provide previews and allow individual shot regeneration. Do not regenerate approved assets unnecessarily.

## Final report

State what code and assets were created, what was actually tested, Blender/FFmpeg versions, actual output path, duration/resolution/frame rate, render time, failed or pending shots, optional API credentials still needed, and known visual limitations. Never say complete when core animation is mocked or untested.
