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
