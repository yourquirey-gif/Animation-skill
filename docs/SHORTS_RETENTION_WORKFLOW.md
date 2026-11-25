# YouTube Shorts: Hook, Script, Retention, Edit, and Publishing Standard

This workflow applies whenever the user asks for a YouTube Short or any vertical short-form story. It supplements the code-first Blender/Python/FFmpeg production pipeline. It is a quality standard, not a guarantee of views or retention.

## 1. Story and script before production
- Reduce the whole Short to one clear premise. If it cannot be explained in one sentence, simplify the story.
- Write the complete voiceover/dialogue script before building shots.
- Default target runtime: 25–40 seconds while testing a new format. Change duration when the story genuinely needs it; never pad a story to hit a number.
- Remove greetings, channel intros, logos, and warm-up. Begin inside the action, danger, mystery, surprise, or strongest consequence.
- Establish a curiosity question in the opening and delay its full answer until the payoff near the end.
- Every line must advance the story, reveal a clue, raise stakes, or deliver a payoff. Remove filler and repeated information.
- Design the ending so the final image, sound, or sentence can flow naturally into the opening when a seamless loop suits the story. Do not force an awkward loop.
- Keep the story understandable without requiring viewers to know earlier episodes.

## 2. First-three-second hook — highest priority
The first 0–3 seconds must be the strongest, most visually arresting part of the Short. Do not treat the hook as merely a title card or a spoken question over a static shot.

### Hook requirements
- Frame 1 must already contain a readable, high-impact action or unusual image. Start during the event, not before it.
- Pair the visual action with a short, specific voiceover line or on-screen text that creates an immediate question, danger, contradiction, mystery, or surprising claim.
- Show the consequence, threat, impossible situation, or a partial reveal immediately; withhold only the explanation/payoff.
- Use a close-up, strong silhouette, clear subject separation, expressive face/body pose, decisive camera move, impact, or meaningful object movement where appropriate.
- The viewer should understand what is at stake even with audio muted.
- The hook must accurately represent the story. Never use misleading bait unrelated to the payoff.
- Do not spend the opening seconds on establishing scenery, slow camera travel, character introductions, fade-ins, empty walking, or explanatory backstory.
- Analyze the user's supplied reference video for its actual opening: first frame, first action, first spoken line, camera movement, pacing, framing, sound cue, and how curiosity is created. Learn the technique and visual language; do not copy protected characters, footage, dialogue, or music.
- If reference media is not available in the project, ask the user to place it in references/ and state that the exact reference-specific hook cannot yet be inspected. Do not pretend to have analyzed it.

### Hook timing guide
- 0.0–0.5 s: visual impact/action is already happening.
- 0.5–1.5 s: a short hook line or readable text clarifies the danger/mystery/stakes.
- 1.5–3.0 s: escalate, reveal a clue, or make the viewer need the answer.
These are editing guides, not rigid frame quotas. The first three seconds should feel like one compelling event, not three unrelated cuts.

### Hook quality gate
Before producing the full video, create at least three genuinely different hook concepts for the same story (different action, reveal, or framing—not just reworded sentences). Score each for:
1. Immediate visual clarity.
2. Curiosity / unanswered question.
3. Emotional stakes or surprise.
4. Mute-viewer comprehension.
5. Honest connection to the final payoff.
Choose the strongest and show the user the hook line plus a preview/animatic. Do not proceed with a weak or static opening.

## 3. Script structure for a 25–40 second Short
Use this as a flexible structure:
- 0–3 s — Hook: strongest action + curiosity gap.
- 3–8 s — Context: only the minimum information needed to understand the situation.
- 8–22 s — Escalation: complications, discoveries, reversals, or rising stakes. Introduce a visual or information change roughly every 1.5–2.5 seconds when the material supports it.
- 22–34 s — Payoff: answer the opening question with a satisfying reveal, twist, consequence, or emotional beat.
- Final seconds — Loop / interaction: connect back to the opening when natural, or end on one concise question that invites a genuine response.
For other durations, scale the beats proportionally while preserving the same principles.

## 4. Visual pacing and animation
- Change the visual, composition, camera angle, meaningful character action, or relevant insert about every 1.5–2.5 seconds as a starting point. Do not cut mechanically if a continuous action is more compelling.
- Remove dead air, long pauses, redundant reactions, and shots that do not add information.
- Every shot must have a clear purpose and visible motion. Prefer actual character, prop, environment, and camera animation over static frames with pan/zoom.
- Use close-ups and inserts to make important story details readable on a phone.
- Ensure action is physically coherent: correct object grip, contact point, direction, weight, and reaction. Preserve character/location continuity.
- Use impact frames, camera movement, sound cues, and reaction shots only when they improve comprehension or emotion; avoid random effects.
- Build the opening shot first and review it independently before rendering the full timeline.

## 5. Captions and audio mix
- Add accurate, dynamic captions synchronized to actual speech.
- Use large, high-contrast, concise caption chunks. Emphasize only important words; avoid covering faces, hands, or key story objects.
- Keep captions inside vertical platform-safe areas: avoid the right-side engagement controls and bottom title/description interface.
- Check readability on a phone-sized preview and with the video muted.
- Keep narration/dialogue crisp and clearly above background music.
- Music should support the emotional beat without masking speech. Use licensed, user-provided, or otherwise permitted audio; never extract copyrighted music from a reference.
- Add purposeful sound effects for impacts, movement, reveals, and transitions. Avoid excessive or generic SFX.
- Check clipping, sudden volume jumps, silence, and subtitle/audio synchronization.

## 6. Title, thumbnail, and publishing package
- Write a clear, intriguing, accurate title. Aim for fewer than 50 characters when practical, but clarity matters more than an arbitrary character limit.
- Proofread spelling, grammar, names, and factual claims. Remove excessive hashtags from the visible title; use only a small number of relevant tags if needed.
- Select the strongest available thumbnail frame in YouTube Studio. Prioritize a clear subject, readable emotion/action, and curiosity; do not assume the software can set the Shorts thumbnail through an unsupported API.
- Add a concise description and only relevant hashtags.
- When appropriate, suggest one specific audience question in the ending or pinned comment. It must arise naturally from the story, not be generic engagement bait.
- Do not promise virality, views, or retention. Treat performance as something to measure and iterate.

## 7. Pre-render and pre-publish checklist
### Script and concept
- [ ] One-sentence premise is clear.
- [ ] Opening has no greeting, intro, or unnecessary setup.
- [ ] First three seconds have a powerful visual action and matching hook line.
- [ ] Hook creates a real curiosity gap that the ending resolves.
- [ ] Every line contributes; no filler.
- [ ] Ending payoff is satisfying and loop is natural if used.
### Visual and edit
- [ ] First frame is active and understandable.
- [ ] Visual changes or meaningful motion maintain pace.
- [ ] No dead air or unnecessary pauses.
- [ ] Character, prop, geography, and action continuity are correct.
- [ ] Captions are accurate, readable, and platform-safe.
- [ ] Voice is clear; music and SFX do not overpower it.
- [ ] Phone preview and muted preview have been checked.
### Publishing
- [ ] Title is accurate, intriguing, and proofread.
- [ ] Thumbnail frame is selected where the platform workflow allows it.
- [ ] Description and hashtags are relevant and restrained.
- [ ] Optional audience question is specific and story-related.
- [ ] Final MP4 passes technical validation.

## 8. Required output from Claude Code
Before rendering, provide:
1. One-sentence premise.
2. Full timed script with narration/dialogue and on-screen text.
3. Three opening-hook alternatives with their first-shot visual descriptions.
4. Selected hook and why it is strongest.
5. Shot-by-shot storyboard with durations, actions, camera, captions, and audio cues.
6. Planned title, description, hashtags, and optional pinned comment.
Then implement the shots in the existing code-first Blender pipeline, render a hook preview first, inspect it, and only then render the complete Short. Report actual test/render results honestly.


## 9. Cinematic 3D look, lighting, camera, and story-specific worlds

These are mandatory requirements for every story, not optional polish.

### Story-specific visual direction
- Treat every new story as a fresh visual-production brief. Read its genre, location, time period, mood, weather, season, emotional arc, and action before designing its world.
- Generate a distinct environment/background concept for each story. Do not reuse the previous story's background by default.
- Build each environment as a coherent 3D world: terrain, ground, sky, buildings, vegetation, furniture, roads, mountains, props, atmosphere, and depth must be real 3D geometry or suitable 3D scene elements.
- Reuse a background within the same story only when continuity requires the same location. Different locations in one story need their own designed 3D sets.
- Only the approved recurring character design remains consistent across stories. Keep that character's identity, face, proportions, costume, colors, and recognizable details stable. The environment, props, lighting, camera language, color palette, and supporting set dressing may change to suit each story.
- Build a per-story Visual Bible and Location Bible before final production. Include palette, materials, environment layout, weather, time of day, lighting mood, camera language, and recurring props.
- Do not use a flat 2D background, static picture, or image slideshow as a substitute for the 3D world. If a specific element is genuinely best represented by a 2D texture (for example a label or distant matte detail), keep it integrated into an otherwise dimensional scene.

### Lighting direction
- Design lighting per scene and emotional beat, not one generic light setup for the whole video.
- Use a deliberate key/fill/rim or motivated-light setup, contact shadows, ambient bounce, and practical lights where appropriate.
- Create distinct moods such as warm/cold, soft/hard, high/low contrast, dawn/night, suspense/reveal, while preserving continuity within a location and time.
- Ensure faces, eyes, and important actions remain readable. Avoid blown highlights, crushed shadows, flat lighting, and inconsistent light direction.
- Use volumetric haze, god rays, fog, dust, rain, firelight, or atmospheric effects only when story-appropriate and render-performance allows.
- Save lighting presets as reusable code/configuration, but choose and tune them separately for each story.

### Camera direction
- Plan camera language shot by shot: shot size, lens/focal length, angle, composition, depth of field, camera movement, focus target, and screen direction.
- Use motivated push-ins, pull-backs, tracking, orbit, pan, tilt, handheld-style motion, low/high angles, and close-ups to express action or emotion.
- Keep camera movement intentional and readable; avoid random shake or motion that hides the action.
- Use close-ups for facial emotion and reactions, inserts for critical objects, and wide shots to establish spatial geography.
- Maintain axis, eyelines, screen direction, character position, and geography across cuts unless a deliberate transition is planned.
- Use physically coherent camera rigs and test camera motion at preview quality before final rendering.

### Opening hook impact and frame shake
- The opening must use a story-specific strongest hook, not a copied generic hook template. Generate multiple distinct visual/action ideas and choose the strongest honest match for that story.
- For the first hook beat, consider a brief, controlled impact-style camera shake inspired by the user's second reference video. Apply only around a meaningful impact, sudden reveal, near miss, or shock; do not shake continuously.
- Build shake as a camera transform animation (small position/rotation offsets with quick decay), optionally paired with a subtle impact sound and motion blur. Keep the subject and key action visible.
- Provide a clean version and a shake version in the hook preview if the effect is uncertain. Tune amplitude, frequency, and duration to the actual reference after inspecting it; never invent exact settings from an unavailable clip.
- Do not let shake cause nausea, obscure captions, create excessive blur, or reduce visual clarity. The shake must enhance the moment, not compensate for weak staging.

## 10. Word-by-word animated captions
- Captions must appear word by word, synchronized to the actual spoken audio timestamps—not as one full sentence appearing at once by default.
- Use a karaoke-style timing model: reveal each spoken word at its speech onset, with sensible punctuation and phrase grouping. Keep already-spoken words visible only as long as needed for comfortable reading.
- Emphasize the current or important word through scale, weight, highlight, color, or a brief pop animation. Avoid making every word flash or bounce excessively.
- Use accurate speech-to-text alignment or manually verified timestamps. Do not guess timing when actual audio is available.
- Keep captions centered in a consistent safe caption zone, but offset them as needed to avoid faces, hands, story-critical objects, and platform UI overlays.
- Limit words per line and use high-contrast typography, readable stroke/shadow, consistent font hierarchy, and mobile-size previews.
- Support Hindi, English, and mixed Hinglish text, including correct spelling, punctuation, and line breaks.
- Inspect captions frame by frame at the opening hook and at least one fast dialogue section. Check timing, clipping, overlap, readability, and safe margins.

## 11. Character acting, facial emotion, and reactions
- Use expressive character acting in every relevant shot: facial expression, eye direction, brows, mouth shape, head movement, shoulders, hands, posture, and body weight must communicate the emotion.
- Create a reusable facial rig/shape-key library for emotions such as fear, shock, joy, sadness, anger, confusion, suspicion, relief, pain, and determination, adapting the set to the character design.
- Animate reactions to actual events: anticipation before impact, recoil after impact, eye tracking, flinch, breathing, hesitation, surprise, recovery, and emotional follow-through.
- Do not leave characters with a blank face during dialogue or dramatic events. Avoid constant exaggerated expressions; match intensity to the story beat.
- Use lip sync based on actual dialogue/audio timing where dialogue is present.
- Preserve the exact approved character identity across all stories. Improve acting and animation quality without changing the character's signature face, silhouette, proportions, costume, or defining features.
- Check hands, fingers, gaze, facial deformation, body balance, foot contact, and interaction with props in close-up previews.

## 12. Mandatory per-story production gates
Before full rendering of every new story:
1. Create a fresh story-specific visual direction and 3D environment concept.
2. Confirm the recurring character matches its approved character reference.
3. Produce lighting and camera tests for the key locations.
4. Produce at least three distinct story-specific opening hook concepts.
5. Preview the selected hook with controlled impact shake when appropriate.
6. Preview word-by-word captions against actual voice timing.
7. Preview facial emotions and reactions in close-up.
8. Inspect the opening and representative shots before full render.
Do not carry over the previous story's environment, hook, camera setup, lighting, or caption timing without re-evaluating them.
