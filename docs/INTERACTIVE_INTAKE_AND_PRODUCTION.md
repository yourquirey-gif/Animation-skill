# Interactive Intake and Video Production Flow

This document defines how the skill must talk to the user before making a video. Follow it in order, but skip questions already answered or made unnecessary by supplied files.

## 1. Detect what the user supplied

Inspect the current message and uploaded files first.

### Mode A — "I need an idea"
If the user chooses idea mode:
1. Ask for the topic only if it was not supplied.
2. Identify the audience, central premise, strongest verified fact/conflict, and emotional angle.
3. For factual/history topics, research reliable sources and distinguish verified facts from legend, disputed claims, and dramatized reconstruction.
4. Offer a concise premise and script direction. Do not turn uncertain details into facts.
5. Write the complete voiceover script after the user approves the direction, or proceed directly if the user asked you to decide independently.

### Mode B — "I have a script"
1. Read the complete script/file.
2. Identify the premise, beats, factual claims, characters, locations, props, and ending.
3. Preserve the user's meaning and key facts. Improve pacing, clarity, and retention without changing the core story.
4. If factual claims are questionable, flag and verify them; do not silently invent corrections.
5. Provide the polished production script and time estimate. If major rewriting is needed, explain why and request approval before changing the story materially.

### Mode C — "I have voice/audio"
This mode takes priority when an audio file is attached, even if the user did not type "audio mode".
1. Inspect file type, codec, sample rate, channels, and actual duration with ffprobe/available audio tools.
2. Transcribe the actual speech in its original language. Preserve wording; mark uncertain words for review.
3. Detect speech segments, pauses, emphasis, emotional tone, and word/phrase timestamps using forced alignment or verified ASR timestamps.
4. Treat the supplied recording as the narration master. Do not generate replacement narration or rewrite the spoken script.
5. Design scenes to fit the audio's actual timeline. Never speed up, stretch, cut, or reorder speech merely to hit a nominal duration. Ask before any material audio edit.
6. If the audio has music/noise or multiple speakers, report this and separate tracks only where technically possible.
7. Begin story analysis and visual planning immediately. Do not ask the user to provide a script that is already spoken in the audio.
8. Ask only for the missing aspect ratio if not known: YouTube Shorts (9:16) or YouTube Long (16:9). Duration is derived from the audio; offer trimming/extension only as an optional, explicit choice.

If an audio upload cannot be accessed or decoded, state the exact issue and ask for a supported audio file. Do not pretend to have heard it.

## 2. Ask duration, then format — only when needed

For idea/script modes, after the topic/script is known, ask one question at a time:

**Duration:** 30 seconds, 60 seconds, or custom duration.

**Format:** YouTube Shorts (vertical 9:16) or YouTube Long (landscape 16:9).

Rules:
- If the user already specified duration or format, remember it and skip that question.
- If they answer "30 sec Shorts", both fields are complete; do not ask again.
- A 30/60-second choice is a target, not permission to rush or pad. Calculate a realistic narration word budget for the selected language and delivery speed.
- If the script/audio cannot fit naturally, explain the mismatch and offer concise options: preserve full content and extend runtime, or approve a shortened version.
- Audio-led mode derives duration from the actual recording and asks format only if missing.
- Never ask a multi-part form when one short question will do.

## 3. Scriptwriting style and story formats

Choose a style appropriate to the topic. Do not force every story into the same formula.

### Historical / mystery / true-story documentary
- Cold open on the strangest verified event, contradiction, danger, or consequence.
- Establish only essential time/place/identity.
- Escalate with evidence, decisions, obstacles, and consequences.
- Place reveals/clues throughout; reserve the strongest answer for the final payoff.
- Clearly distinguish historical record from popular legend or dramatized reconstruction.
- End with a memorable consequence, irony, question, or natural loop.

### Explainer / educational story
- Start with a surprising question or practical consequence.
- Explain one core idea using a concrete visual analogy.
- Reveal the mechanism step by step.
- End with the implication or a concise takeaway.

### Biography / character story
- Open on a defining moment or contradiction.
- Show the choice, pressure, setback, turning point, and consequence.
- Avoid a list of dates and achievements.

### Fiction / imaginative story
- Establish a clear goal, obstacle, stakes, escalation, twist, and resolution.
- Keep internal story logic consistent; do not present fiction as fact.

### Script quality requirements
- One clear premise that can be summarized in one sentence.
- No greeting, channel intro, generic "today we will discuss", or slow preamble.
- Natural spoken language; short, vivid sentences; avoid robotic exposition.
- Every sentence must add a fact, clue, emotion, escalation, or payoff.
- First five seconds create a clear curiosity gap. Final five seconds deliver the promised payoff.
- Use multiple escalating curiosity beats rather than withholding everything until the final line.
- Do not use fake shock, unsupported claims, fabricated quotes, or misleading clickbait.
- For Shorts, use 25–40 seconds as a general testing target, unless the user explicitly chooses 30/60/custom. Respect the requested duration.
- For Long videos, structure chapters and pacing around the story; do not apply the Shorts cut frequency mechanically.

## 4. Required pre-production response

Before rendering, show the user a concise production brief:
1. Mode selected: idea / script / audio.
2. One-sentence premise.
3. Target runtime and aspect ratio.
4. Full timed narration/script (except do not rewrite supplied audio; show verified transcript).
5. Three distinct opening-hook concepts with different visual actions, not just rephrased lines.
6. Selected hook and why it is clearest/most compelling and truthful.
7. Storyboard with shot IDs, time ranges, visual action, camera, environment, captions, and sound cues.
8. Character and location continuity plan.
9. Title, description, restrained hashtags, thumbnail-frame idea, and optional pinned-comment question.
10. Any factual uncertainty, missing asset, dependency, or render limitation.

For direct "just make it" requests, do not stall for approval on routine creative decisions. Ask only about material ambiguities, paid services, or irreversible actions.

## 5. Visual storytelling and cut rhythm

For Shorts:
- First frame is already in motion or contains a high-impact readable event.
- Use a new shot, camera angle, framing, meaningful action, or relevant insert about every 1.5–2.5 seconds as a default.
- A cut is not enough by itself: each shot must add information, emotion, movement, clue, or escalation.
- Maintain visual continuity and screen direction. Do not randomly jump between unrelated images.
- Include wide shots for geography, medium shots for action, close-ups for emotion, and inserts for important evidence/props.
- Every major narration beat should have a visual counterpart.
- Use camera movement with motivation: push-in for realization, tracking for pursuit, orbit for reveal, overhead for geography, controlled shake for impact only.
- Show a reveal clearly; do not cover it with captions or effects.
- If one continuous shot lasts more than 2.5 seconds, document the evolving action/camera movement that earns the duration.
- Long-form videos may use longer takes when tension, dialogue, or complex action benefits from them.

## 6. Quality gates

### Before rendering
- Story facts and chronology verified where factual.
- Script fits chosen runtime and natural speaking speed.
- Hook is strong, clear, honest, and visually executable.
- Storyboard covers the full narration/audio with no orphaned lines.
- Character/location/prop continuity specified.
- Captions have actual timing source.
- Hardware and dependencies inspected; render settings chosen from real capabilities.

### After preview and final render
- Watch the complete video, not only a contact sheet.
- Inspect first frame and opening 5 seconds frame-by-frame.
- For Shorts, review every shot boundary and flag any visual inactivity gap over 2.5 seconds.
- Inspect fast captions and all important action/prop contacts.
- Listen to the complete audio mix.
- Verify video dimensions, frame rate, duration, codec, audio stream, and file integrity with ffprobe.
- Check black/frozen frames, missing shots, clipping, subtitle overflow, and sync drift.
- Failed critical checks require correction and re-render, or a clearly stated blocker.

## 7. Completion report

Report the exact final file path and actual runtime, resolution, frame rate, codecs, render time, and validation results. List any defects or approximations. Never claim a finished video when only a storyboard, stills, animatic, mock output, or untested code exists.
