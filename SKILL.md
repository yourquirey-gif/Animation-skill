---
name: animation-skill
description: Plan, generate, animate, edit, and quality-check cinematic AI story videos with consistent characters and environments. Use whenever the user asks to create or modify an animated story, storyboard, scene, character, animation pipeline, or video.
---

# Animation Skill

Use this skill for every animated-story task. Treat user-provided reference videos and images as the primary visual target. Do not claim a result matches a reference unless it has been inspected.

## Core standard

Create cinematic, story-driven animated shots, not a slideshow. Static images with pan/zoom are not animation. Use actual image-to-video, text-to-video, 3D animation, or motion-rendering capability for moving subjects. FFmpeg is for assembly, timing, audio, subtitles, compositing, and export—not for inventing character motion.

Never promise exact replication of a reference. Aim for the closest achievable style and clearly report model, budget, duration, and technical limits.

## Workflow

1. Inspect the project, available assets, reference media, installed tools, provider documentation, and existing conventions before changing anything.
2. Analyze references when supplied: sample representative frames across the whole clip; inspect aspect ratio, frame rate, shot length, palette, lighting, character design, camera language, motion, subtitles, sound, and transitions. Write findings to docs/REFERENCE_STYLE_GUIDE.md. Do not infer unseen details.
3. Parse the story into beats, characters, locations, props, and chronological events. Preserve the user's plot and causal order.
4. Create a storyboard before generation. Each shot records: ID, purpose, duration, location, characters, action, emotion, framing, lens/camera movement, lighting, environment motion, narration/dialogue, SFX/music, visual prompt, motion prompt, continuity constraints, and status.
5. Create a Character Bible and Location Bible. Record stable visual traits, wardrobe, scale, voice, props, geography, layout, lighting and recurring details. Generate turnaround/reference sheets where supported.
6. Generate keyframes/reference images, then animate each shot with a provider that supports the required motion and reference inputs. Reuse approved references and seeds where supported. Do not assume a provider supports identity locking; verify its current API documentation.
7. Generate narration/dialogue and subtitles. Align timing to the actual audio, not estimated text length. Mix music and effects below dialogue.
8. Assemble shots with FFmpeg. Preserve the intended pacing, safe margins, resolution, aspect ratio, and audio levels.
9. Run visual, temporal, audio, subtitle, and technical QA. Regenerate failed shots where possible; otherwise mark them as failed and ask for a decision. Never silently replace a failed shot with an unrelated still.
10. Save project manifests and intermediate assets so work can resume without regenerating successful shots.

## Character and scene continuity

- Keep a canonical Character Bible entry and approved reference images for each character.
- Repeat essential identity, wardrobe, scale, and prop constraints in every generation prompt.
- Track screen direction, position, eyelines, time of day, weather, lighting, and object state across adjacent shots.
- For recurring locations, reuse approved environment references and spatial descriptions.
- Check anatomy, hands, object contact, tool orientation, ground contact, shadows, and physical geography.
- A character holding a tool must grip it correctly; a hammer, for example, must be held by its handle and strike with its head.
- Do not describe a mountain, building, or other structure in a way that can produce disconnected, missing, or contradictory geometry. Specify the complete visible structure and camera viewpoint.
- If a model cannot reliably render a complex action, split it into simpler shots or use a 3D scene/animation workflow rather than pretending it succeeded.

## Prompt construction

For every shot, provide:
- Subject and stable identity description.
- One clear primary action with beginning, middle, and end.
- Environment and relevant props.
- Composition and camera position/movement.
- Lighting, atmosphere, and visual style.
- Continuity references and explicit exclusions.
- Motion constraints (what moves, what stays still, direction, speed).
Avoid contradictory instructions, overloaded action lists, and unnecessary style changes between shots.

## Provider and implementation rules

- Inspect official, current provider documentation before integrating APIs.
- Verify endpoint, model identifier, request schema, accepted media, duration, resolution, polling, errors, rate limits, pricing, and commercial-use terms.
- Keep providers behind adapters; do not hardcode one vendor into the story planner.
- Keep secrets in environment variables; provide .env.example with names only.
- Do not expose keys in logs, UI, commits, or generated reports.
- Do not incur paid usage or make purchases without explicit user approval.
- Distinguish implemented, tested, mocked, and pending integrations.
- Never fabricate API responses, progress, successful renders, or quality scores.
- Add retries with bounded backoff, timeouts, job persistence, resumability, and clear error reporting.
- Respect provider safety rules, rights, and user-supplied asset permissions.

## Default delivery profile

Unless the user specifies otherwise:
- Vertical short: 1080x1920, 9:16, 30 fps, MP4/H.264, AAC.
- Landscape: 1920x1080, 16:9, 30 fps, MP4/H.264, AAC.
- Choose actual output settings supported by the provider; upscale only when appropriate and disclose it.
- Keep captions inside platform-safe margins and make them readable on mobile.

## Quality-control checklist

For every shot and final video, check:
- Correct story beat and chronological continuity.
- Character identity, face, body, clothing, and accessories.
- Anatomy, hands, contact, object/tool orientation.
- Environment and spatial/geographical continuity.
- Motion plausibility, temporal flicker, warping, unwanted morphing.
- Camera movement, composition, exposure, lighting, and color consistency.
- Missing frames, black frames, corrupt clips, unintended freezes.
- Voice clarity, clipping, loudness balance, music/SFX levels.
- Subtitle wording, timing, spelling, placement, and safe margins.
- Exact output dimensions, frame rate, duration, codec, and audio stream.

Report failures honestly with shot IDs and corrective actions.

## Project artifacts

Prefer a clear structure such as:

- references/ — user-provided reference videos/images.
- docs/REFERENCE_STYLE_GUIDE.md — observed style characteristics.
- docs/STORY_BIBLE.md — story facts and chronology.
- docs/CHARACTER_BIBLE.md — canonical character descriptions.
- docs/LOCATION_BIBLE.md — recurring environment descriptions.
- projects/<project-id>/storyboard.json — shot plan and status.
- projects/<project-id>/assets/ — approved references and generated assets.
- projects/<project-id>/renders/ — shot and final renders.
- config/ — non-secret configuration.
- .env.example — required environment variable names only.

Adapt to the existing repository rather than forcing this layout onto an established project.

## User interaction

Ask only for information that blocks progress. If reference media is missing, explain exactly where to put it. Before paid generation, show estimated cost and obtain approval. Provide previews and allow individual shot regeneration. Do not regenerate approved assets unnecessarily.

## Final report

State what was created, what was actually tested, provider/model used, output path, actual duration/resolution/frame rate, failed or pending shots, API credentials still needed, and known limitations. Never say complete when core generation is mocked or untested.
