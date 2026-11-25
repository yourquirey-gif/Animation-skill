# Production Workflow

## A. Intake
- Preserve the user's story, language, tone, and intended platform.
- Confirm target duration, aspect ratio, narration language, and reference assets only when missing information blocks production.
- Inspect existing project structure before creating or moving files.

## B. Reference analysis
- Probe source media metadata (duration, dimensions, frame rate, audio streams).
- Sample frames from beginning, middle, end, and meaningful scene changes.
- Describe only observable traits: character design, palette, lighting, composition, camera, motion, pacing, transitions, typography, and sound.
- Save findings and representative timestamps in REFERENCE_STYLE_GUIDE.md.

## C. Story design
- Extract story beats and preserve chronological order.
- Build character, location, and prop inventories.
- Identify continuity dependencies and recurring assets.
- Create a shot list with explicit start/end action and duration.

## D. Asset generation
- Generate character reference sheets and approved location references.
- Review references before using them as continuity anchors.
- Store prompts, provider/model identifiers, seed/reference IDs where available, and generation status in the project manifest.

## E. Shot generation
- Generate one shot at a time or in controlled batches.
- Use reference-guided image/video generation where supported.
- Keep each shot focused on one primary action.
- Check motion and visual quality before accepting a shot.
- Retry transient failures with bounded backoff; do not retry permanent validation or policy failures endlessly.

## F. Audio and edit
- Generate narration and dialogue, then derive subtitle timing from actual audio.
- Mix voice clearly above music and effects.
- Assemble accepted clips; avoid hiding continuity problems with excessive transitions.
- Export using the requested platform profile.

## G. QA and delivery
- Inspect every shot and the final render.
- Validate streams, codecs, frame rate, dimensions, duration, audio, subtitles, and black/frozen frames.
- Provide a concise report separating complete, tested, pending, failed, and mocked functionality.
- Include actual output paths and provider/model details.
