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

## Mandatory interactive intake and operating modes

Before creating a new video, follow `docs/INTERACTIVE_INTAKE_AND_PRODUCTION.md`. This is the required conversation flow, not optional guidance.

- First identify the input mode: (A) develop an idea, (B) user supplies a script, or (C) user supplies recorded voice/audio.
- If the user uploads audio directly, detect that input and begin audio-led analysis immediately. Do not restart the intake by asking whether they want an idea or script.
- For idea mode, ask for the topic only if absent; research/verify factual stories where needed, propose a premise, then write the complete script.
- For script mode, accept the user's script as source material; fact-check factual claims and preserve intended meaning. Ask before making material story changes.
- For audio mode, inspect duration, language, speech, pauses, transcript, and word/phrase timestamps. Treat the supplied recording as the narration master; do not rewrite or replace it unless asked. Build visuals to fit the actual recording, not the reverse.
- After idea/script input is established, ask for duration (30 seconds, 60 seconds, or custom) and then format (YouTube Shorts 9:16 or YouTube Long 16:9). If user already specified either, do not ask again.
- For direct audio input, infer duration from the actual file. Ask only the missing output format (Shorts or Long) unless the user's context already determines it. Never ask for an arbitrary duration that conflicts with the supplied audio.
- Ask one concise question at a time. Remember answers within the current task; never repeat answered questions. If a ZIP contains multiple assets, inspect its contents before asking for anything.
- After intake, take ownership of script timing, storyboard, characters, environments, animation, sound design, captions, rendering, and QA. Ask only when a genuine blocker or user approval is needed.

## Bundled executable runtime — run it, do not only describe it

This skill now ships executable helpers in runtime/. When a user starts a video task in Claude Code, use the terminal to run the bundled runtime from the skill directory before inventing a new setup:

1. Run `python runtime/animation_runtime.py inspect` (Windows may use `py`). Read the actual report; do not assume Blender or FFmpeg is installed.
2. If all three tools are available, run `python runtime/animation_runtime.py smoke-test`. This must create a real animated 3D Blender scene, render frames, encode an MP4 with FFmpeg, and validate it with ffprobe. Inspect the produced MP4 and report the real result.
3. If a dependency is missing, identify OS and install route; ask before using administrator privileges, large downloads, or changing system configuration. Support BLENDER_BIN, FFMPEG_BIN and FFPROBE_BIN overrides.
4. Do not pip-install bpy into arbitrary system Python as the default. Use Blender's own bundled Python for bpy scripts and invoke Blender in background mode with --python and --python-exit-code 1.
5. The smoke test is only a technical integration check. It is not a finished story engine, not a production character benchmark, and not permission to reuse its sample scene as every story.
6. For the actual user story, Claude Code must author a new story-specific Blender scene/asset code from the approved storyboard: unique world, set dressing, characters, props, physically coherent actions, camera, lighting and facial acting. Keep reusable rig/animation utilities separate from story data.
7. Use a real preview render and inspect it. Fix defects before final render. Assemble audio/captions/music/SFX and validate the final export with ffprobe. In Claude chat, present the preview/result file paths and attach or surface the actual MP4 using the host's supported file workflow; never claim an attachment exists if it was not produced.

The bundled runtime commands and requirements are documented in runtime/README.md. The Blender API's supported headless pattern is documented by Blender itself: `blender --background --python script.py`. See https://docs.blender.org/api/current/info_tips_and_tricks.html and https://docs.blender.org/api/current/info_advanced_blender_as_bpy.html.

## First-use application implementation requirement

This repository is a Claude Code skill/instruction package, not a prebuilt renderer. When installed into a user's working project, inspect that project and implement a real reusable local video-production application before claiming the workflow is ready. Follow `docs/APP_IMPLEMENTATION_SPEC.md` and `docs/CODE_FIRST_PIPELINE.md`.

- Create working Python orchestration, Blender `bpy` scene generation, FFmpeg assembly, audio/transcription/timestamp handling, subtitle rendering, job persistence, preview/render/resume/validate commands, and automated tests.
- Do not merely create placeholder directories, pseudocode, fake progress bars, mock renders, or a sample slideshow and call it complete.
- Detect Blender, FFmpeg, Python, available hardware, fonts, audio tools, and dependencies. Provide a setup report and a real smoke test.
- Keep the app modular and story data separate from rendering code. Validate storyboard data against a schema.
- Implement graceful missing-dependency handling and clearly explain installation steps. Never silently switch to still images if Blender is unavailable.
- Build the first usable vertical/horizontal end-to-end sample with actual moving 3D geometry, real audio, subtitles, and ffprobe validation before declaring the app operational.
- If environment limits prevent implementation or rendering, complete the parts that can be completed, list exact blockers and untested items, and do not claim success.

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


## YouTube Shorts: hook and retention requirements

Whenever the requested output is a YouTube Short or vertical short-form story, read docs/SHORTS_RETENTION_WORKFLOW.md and follow it as a mandatory production standard.

- Write the complete script before production, built around one clear premise.
- Make the first 0–3 seconds the strongest part: frame 1 must already show a clear, high-impact action or unusual image, paired with a concise hook line or on-screen text.
- Create at least three genuinely different hook concepts, evaluate visual clarity, curiosity, stakes, mute-viewer comprehension, and connection to the payoff, then select the strongest.
- Do not open with greetings, channel intros, slow establishing shots, fade-ins, empty walking, or backstory.
- Build a curiosity gap in the opening and resolve it with a satisfying payoff near the end. Do not use misleading bait.
- Default to a 25–40 second runtime while testing a new format, but never pad a story just to reach a duration.
- As a starting point, change the visual, camera angle, meaningful action, or relevant insert every 1.5–2.5 seconds where the story supports it. Remove dead air and unnecessary pauses.
- Keep dynamic captions readable and inside platform-safe areas; keep voice clear above music.
- Plan a natural loop when appropriate, plus an accurate title, restrained hashtags, thumbnail frame suggestion, and story-related audience question.
- Render and inspect the opening hook preview before rendering the entire Short. A static title card or slideshow does not pass.
- If the user supplied a reference video, inspect its opening and use its hook technique as guidance. Never claim to have inspected unavailable reference media or copy protected footage, characters, dialogue, or music.


## Story-specific 3D art direction, camera, captions, and acting

For every new story, follow the extended requirements in docs/SHORTS_RETENTION_WORKFLOW.md. These requirements are mandatory:
- Design a fresh, story-specific 3D environment/background for every story. Do not reuse another story's world by default. Different locations within a story need coherent separate 3D sets.
- Keep the approved recurring character's identity, face, proportions, costume, palette, and defining details consistent. Change the world, props, camera language, lighting, and set dressing to fit each new story without redesigning the character.
- Build all story elements other than the character as 3D scene elements wherever practical: terrain, buildings, sky, objects, vehicles, furniture, vegetation, and props. Never substitute a flat background or slideshow for a 3D environment.
- Design lighting per scene and emotion using motivated key/fill/rim and practical lights, readable faces, contact shadows, and controlled contrast. Use atmospheric effects only when appropriate.
- Plan camera shot size, lens, angle, movement, focus, composition, axis, and eyelines for every shot. Use intentional close-ups and reaction shots.
- For the opening hook, make a story-specific strongest visual idea. A brief controlled camera shake may accent a meaningful impact, shock, near miss, or reveal, inspired by the user's second reference video. Keep shake short and readable; never shake continuously. Inspect the actual reference before claiming exact matching.
- Animate captions word by word, synchronized to actual voice timestamps. Highlight the active/important word tastefully; keep text readable, accurate, centered in a safe zone, and clear of faces and platform UI.
- Animate high-quality facial emotions and reactions: eyes, brows, mouth, head, hands, posture, recoil, anticipation, and follow-through. Use facial rigs/shape keys and lip sync where applicable. Keep the character recognizable and consistent.
- For every new story, create fresh hook alternatives, environment concept, lighting/camera tests, caption timing preview, and acting close-up before full rendering.


## User-supplied reference videos

Read docs/REFERENCE_VIDEO_ANALYSIS.md before creating videos based on the two supplied visual references. The original assets are expected at:
- references/1000328716.mp4
- references/1000328717.mp4

The repository currently contains the reference instructions and analysis, not the MP4 binaries. Verify both files exist before claiming full reference inspection. If either is missing, tell the user exactly which file needs to be copied into references/. Inspect the full videos, especially the first three seconds, audio, caption timing, facial acting, camera language, and the second clip's opening shake. Do not guess unverified details from the sampled-frame description.


## Strict Shorts retention rules from the user's checklist

For every Short, apply the following as a measurable production standard:
- Target 25–40 seconds during early format testing unless the selected duration or story requires otherwise. A requested 30/60-second duration takes precedence; do not silently override it.
- Frame 1 must contain an already-readable dynamic action or striking visual; no fade-in, title card, greeting, channel intro, or slow establishing shot.
- Establish a clear unanswered curiosity question in the first five seconds and resolve it with a satisfying, truthful reveal in the final five seconds.
- Design at least one meaningful escalation, clue, reversal, surprise, or mini-reveal through the middle. Do not rely on one reveal only at the end; maintain rising curiosity throughout.
- Plan a natural loop where it genuinely fits. The final line/image/sound may lead back to the opening, but never force an incoherent loop.
- As a default edit rhythm, introduce a new shot, angle, composition, meaningful action, or relevant insert every 1.5–2.5 seconds. Track this in the timeline and flag gaps longer than 2.5 seconds for review. A continuous shot may exceed this only when it contains clear evolving action/camera movement and the story benefits from it.
- Remove dead air, unnecessary breaths, pauses, repeated information, and empty movement without making speech unnatural.
- Use dynamic, high-contrast captions aligned to actual speech timestamps. Keep them clear of faces, hands, important props, right-side engagement controls, and bottom UI/title zones.
- Voice must remain crisp and clearly louder than music; music and SFX must support rather than mask the story.
- Finish with an accurate, intriguing title (aim under 50 characters when practical), restrained relevant hashtags, best thumbnail-frame suggestion, and one story-specific audience question.
- Run the checklist before and after rendering. A failed critical item requires correction and re-render, or an explicit documented blocker—not a silent pass.


## Genre-agnostic story generation — mandatory

The video generator must handle arbitrary stories, not just the reference example or a hard-coded genre menu. Treat genre labels as hints, never as a finite allow-list. Infer the required subjects, body plans, locations, period, props, physics, action vocabulary, visual metaphors and tone from each individual story. A human story, animal story, vehicle story, science explainer, fantasy sequence, cooking tutorial, biography or abstract concept may require completely different 3D assets and animation logic.

Reuse only general-purpose systems (camera, lighting, animation utilities, render, audio, captions, QA). Generate story-specific characters/subjects, environments, props, actions and visual direction for every new project. Never reuse the diagnostic smoke-test scene as the user's story. Read docs/APP_IMPLEMENTATION_SPEC.md section 12 and pass its cross-genre acceptance suite before claiming the engine is universal.


## Execute the bundled story renderer

For a user-approved story, create a project-specific storyboard JSON using the structure in `templates/storyboard.universal.example.json`. Do not copy its sample scene as the finished story. Then execute the actual pipeline from the skill directory:

- Shorts: `python runtime/render_story.py --storyboard projects/<id>/storyboard.json --output projects/<id>/final.mp4 --format shorts`
- Long: `python runtime/render_story.py --storyboard projects/<id>/storyboard.json --output projects/<id>/final.mp4 --format long`
- With supplied audio: add `--voice <path>`; optionally add `--music <path>` and `--captions <path-to-srt>`.

The renderer invokes Blender once per shot, renders real PNG frames, encodes each shot with FFmpeg, concatenates shots, optionally burns SRT captions and muxes voice/music, then validates the final MP4 with ffprobe. Inspect Blender logs, previews and final video. Do not report success if any shot fails or the output file/metadata is missing.

The bundled renderer currently provides a procedural 3D foundation (primitive meshes, subject assemblies, transform keyframes, camera keyframes and lighting). For professional story-specific output, add suitable detailed models, rigs, facial performance, contact-aware interactions, scene-specific textures and refined acting. Do not pass off the primitive diagnostic look as finished cinematic quality. The user's supplied audio remains the timing/master track; plan shot durations against its actual duration.


### Detailed story assets and animation

When quality requires more than procedural blockout geometry, use story-specific licensed/approved `.glb`, `.gltf` or `.fbx` models in the storyboard via `asset_file`; paths are relative to the storyboard JSON. Preserve embedded materials and model hierarchy. For imported armatures, an exact existing Blender action may be selected with `asset_action`. Do not invent a model path or claim an asset was imported unless the file exists and Blender import succeeds. Keep an asset manifest with source/license. Procedural primitives are for layout, blockout and simple visual metaphors—not a universal substitute for detailed character/environment art.


### Rigged character performance and face animation

For character-driven stories, prefer detailed licensed/approved rigged GLB/glTF or FBX assets over primitive assemblies. Inspect the actual armature bone names, available animation actions and facial shape keys after import. Use `asset_action` for a prepared motion clip, `pose_keyframes` for custom bone-level acting, and `facial_keyframes` for shape-key expressions. The bundled Blender renderer implements these channels; see runtime/README.md for the storyboard schema. Never invent bone or shape-key names. If no suitable rig exists, build/rig an appropriate story-specific character or disclose the limitation. Do not call simple object transforms skeletal animation or claim lip-sync unless phoneme/viseme timing has actually been generated and rendered.


### Believable hand-held prop continuity

When a character picks up, holds, carries, throws or hands over an object, prefer a bone-attached prop using the renderer's `attach_to` support. Inspect the imported rig and use its exact hand/finger bone names; author local offsets and rotations from preview renders. Animate the prop's release/transfer as an explicit state change. Do not fake a grip by leaving the prop floating near the hand. Bone parenting makes the prop follow the hand, but does not itself create finger closure, collision or contact physics; author those actions with the rig's real controls and validate them visually.
