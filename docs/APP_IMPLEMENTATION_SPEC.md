# Reusable Video Production Application — Implementation Specification

This repository is a skill package, not a prebuilt rendering app. Claude Code must implement the actual application inside the user's working project. This specification is an implementation contract, not a claim that code already exists.

## 1. Required user-facing experience

The application must support three input modes:
- Idea mode: topic/brief → researched premise → script → storyboard → video.
- Script mode: user script/file → validation and pacing → storyboard → video.
- Audio mode: user audio file → technical inspection/transcription/alignment → audio-led storyboard → video.

Support output profiles:
- YouTube Short: 9:16, default 1080x1920, 30 fps.
- YouTube Long: 16:9, default 1920x1080, 30 fps.

Allow target duration 30 sec, 60 sec, or custom for idea/script modes. In audio mode, actual audio duration is authoritative unless the user explicitly approves trimming or extension.

## 2. Suggested project structure

Adapt to the existing project; do not overwrite user code or impose this layout blindly.

```text
animation_app/
  pyproject.toml
  README.md
  config/
    defaults.yaml
  schemas/
    project.schema.json
    storyboard.schema.json
  src/animation_app/
    cli.py
    intake/
      modes.py
      audio_inspect.py
      transcription.py
      alignment.py
    story/
      premise.py
      script.py
      pacing.py
      storyboard.py
    characters/
      specs.py
      procedural_character.py
      rigging.py
    environments/
      builders.py
      props.py
      lighting.py
    animation/
      actions.py
      facial.py
      camera.py
      continuity.py
    blender/
      scene_builder.py
      render.py
    audio/
      import_audio.py
      mix.py
      sfx.py
    subtitles/
      transcript.py
      timing.py
      render.py
    editing/
      assemble.py
      export.py
    qa/
      media_probe.py
      visual_checks.py
      audio_checks.py
      report.py
  projects/
    <project-id>/
      input/
      story/
      storyboard.json
      bibles/
      assets/
      blender/
      renders/
      audio/
      subtitles/
      exports/
      logs/
```

## 3. CLI commands that must actually work

Implement commands matching the installed environment. These are required capabilities; exact names may be adapted consistently.

- `animation-app inspect`: inspect dependencies, hardware, fonts, and media tools.
- `animation-app new --mode idea|script|audio`: create a persisted project.
- `animation-app analyze-audio --project ID --input PATH`: probe, transcribe, and align audio.
- `animation-app storyboard --project ID`: create and validate storyboard.
- `animation-app preview --project ID --shot SHOT_ID`: render a low-quality preview.
- `animation-app render --project ID`: render approved shots and assemble.
- `animation-app resume --project ID`: resume failed/incomplete shots.
- `animation-app validate --project ID`: run technical and content QA.
- `animation-app export --project ID`: package final MP4 and project assets.

If the runtime does not support a persistent interactive UI, Claude Code conducts the conversation and writes the answers into project metadata. Do not pretend a terminal wizard or graphical UI exists unless implemented.

## 4. Data model and project persistence

Persist at least:
- Project ID and creation time.
- Input mode, original input path, source file hash, transcript, language, and audio duration where applicable.
- Requested target duration, actual duration, aspect ratio, resolution, frame rate.
- Script version and approval state.
- Characters, locations, props, and continuity bibles.
- Storyboard shots and their time ranges.
- Asset/render file paths and statuses.
- Preview approvals, QA results, errors, and resume checkpoints.

Use a validated JSON schema or typed models. Store source media unchanged. Keep generated assets separate from user originals. Use deterministic seeds for procedural assets where practical.

## 5. Audio-led pipeline

For uploaded audio:
1. Probe with ffprobe and validate file readability.
2. Decode to a working PCM format without modifying the original.
3. Transcribe in detected language; retain confidence/uncertain spans.
4. Generate word/phrase-level timestamps using forced alignment where possible.
5. If alignment is unavailable, create verified phrase-level timing and label it approximate. Never claim word-accurate sync without evidence.
6. Detect pauses, speaker changes, emphasis, and broad emotional beats where tools support it.
7. Use the audio timeline as the master edit timeline.
8. Map shots to narration intervals; fill gaps with relevant action, not frozen frames.
9. Generate captions from aligned transcript.
10. Sync facial mouth movement to available phoneme/viseme data; if unavailable, use documented approximate lip motion.
11. Keep supplied voice intact unless user approves edits. Never fabricate missing narration.

Do not promise a specific ASR/alignment tool until installed and tested. Make providers replaceable and disclose accuracy limits.

## 6. Storyboard schema requirements

Every shot must include:
- `shot_id`, `start_seconds`, `end_seconds`, `duration_seconds`.
- `location_id`, `character_ids`, `prop_ids`.
- `narration_start/end` or linked transcript segment IDs.
- `visual_purpose` and story beat.
- Primary action with beginning, middle, end.
- Character expression, gaze, gesture, posture, reaction.
- Prop interaction: grip/contact/orientation/trajectory/release where applicable.
- Camera shot size, lens, angle, position, target, movement, focus.
- Lighting setup, environment motion, atmosphere.
- Caption segment IDs and safe-zone position.
- Music/SFX cue IDs.
- Continuity requirements and validation status.
- Render status, preview path, final path, errors.

For Shorts, include a planned visual change/action/camera/insert roughly every 1.5–2.5 seconds. The storyboard validator must flag unmotivated gaps longer than 2.5 seconds for review. It must allow justified continuous action with an explicit reason.

## 7. Blender implementation requirements

- Use Blender Python API (`bpy`) to create actual meshes, materials, lights, cameras, rigs, shape keys, animation curves, and scene collections.
- Create story-specific environments and props as 3D assets wherever practical.
- Create reusable character templates and rig modules; preserve approved identity and wardrobe across shots.
- Implement actual animated actions, object contact, camera movement, and facial acting.
- Support preview and final render profiles.
- Save a .blend file and render log for every project.
- Render shots independently and resume failed shots.
- No final output made solely from still images with pan/zoom, slideshow transitions, or fake motion.
- If procedural character quality is insufficient, report it and improve the model/rig; do not call a primitive mannequin production-ready.

## 8. FFmpeg assembly and output

- Use FFmpeg for video/audio assembly, encoding, muxing, and technical validation.
- Keep narration, music, and SFX separate until final mix.
- Create SRT/ASS captions from the timing model; use fonts supporting the script language.
- Apply audio loudness and peak checks; prevent clipping and music masking.
- Ensure transitions and frame rates are consistent.
- Use H.264 MP4 and AAC by default unless user requests otherwise.
- Run ffprobe on the final export and save its JSON report.

## 9. Automated and visual QA

Automated checks should include:
- Missing/corrupt shot files and unexpected duration.
- Black/frozen-frame detection with thresholds and false-positive notes.
- Audio stream presence, clipping/peak/loudness checks, duration mismatch.
- Caption timestamp bounds, overlaps, safe margins, and missing text.
- Output aspect ratio, dimensions, frame rate, codec, and container integrity.
- Storyboard coverage: no narration interval left without a visual shot.
- Shorts pacing: detect visual change intervals over 2.5 sec and require justification.
- Continuity metadata: character/location/prop IDs remain stable as required.

Visual inspection is still mandatory. Claude Code must actually open/watch previews and final video where supported, not treat automated metrics as proof of good storytelling. Save QA report and list checks not possible to automate.

## 10. Reliability, safety, and user approval

- Use bounded retries, timeouts, resumable jobs, structured logs, and clear error messages.
- Do not delete source media or overwrite user files.
- Do not spend money, call paid APIs, or purchase assets without explicit approval.
- Keep credentials in environment variables and never log secrets.
- Do not upload private media to third-party services without explicit permission.
- Clearly distinguish implemented, tested, approximated, mocked, and pending features.
- Never fabricate rendering progress, preview files, benchmark results, or validation success.

## 11. First implementation acceptance test

Before calling the application ready:
1. Dependency and hardware inspection succeeds or reports exact blockers.
2. A procedural character turntable and close-up render.
3. A short action animation with visible geometry movement.
4. A story-specific 3D location render.
5. Audio import, transcript/timing, and caption generation test.
6. A short complete MP4 with moving 3D shots, voice/audio, captions, and sound mix.
7. ffprobe confirms actual dimensions, frame rate, duration, video codec, and audio codec.
8. Project can resume after an intentionally interrupted shot.
9. QA report records pass/fail and actual evidence.

Do not mark the app ready if any critical test is mocked or missing. If local resources prevent completion, explain what is implemented and what must be installed or supplied.


## 12. Universal, genre-agnostic story compiler

The story engine must not be built around one sample story, one historical event, or a fixed genre list. The input is arbitrary natural-language material. Genres such as documentary, mystery, history, fantasy, science, comedy, biography, emotional drama, action, nature, and children's stories are examples—not an exhaustive enum or routing limit.

Required behavior:
- Parse the actual story into entities, chronology, locations, time periods, props, goals, conflicts, emotional beats, and visual metaphors. Do not assume every story needs a human protagonist, a fight, a city, or a narrator.
- Select visual treatment from the story itself. A space story may need spacecraft and zero gravity; a cooking story needs a kitchen, food and correct utensil interaction; an animal story needs appropriate animal anatomy and locomotion; an abstract explainer may use purpose-built 3D visual metaphors.
- Generate a fresh visual bible and environment plan per project. Never use the technical smoke-test scene or previous story's world as a default production template.
- Keep reusable systems generic: camera rigs, lighting controls, rig utilities, walk/run/talk cycles, object constraints, facial controls, render profiles, audio sync and QA. Keep character designs, locations, props, costumes, actions and art direction project-specific.
- Support multiple character species/body plans and non-character subjects. Do not force a humanoid rig onto animals, vehicles, machines or abstract objects.
- Every storyboard action must be executable as a sequence with start state, movement, contact/interaction, end state and timing. Validate physical plausibility and story continuity.
- For unusual action, write a dedicated Blender Python action/asset module rather than mapping it to an unrelated generic preset.
- Use procedural geometry as a foundation, not a quality ceiling. Use original project-specific meshes, materials, textures, rigging, set dressing and lighting. Disclose limitations where an asset cannot be created credibly.
- Add regression fixtures from different genres and subject types. Passing one sample story is not proof of universal coverage.

### Universal acceptance suite

Before calling the story engine reusable, test at least three structurally different briefs: (1) a human character story with prop interaction and a location change; (2) a non-human subject story requiring species-appropriate movement and environment; (3) an explainer or abstract concept requiring custom 3D visual metaphors. For each, validate the storyboard, generated Blender scene, actual animated geometry, preview frames, audio/caption timeline and ffprobe-valid short MP4. Record what was rendered and inspected. These are engineering fixtures, not preset production styles.


## 13. Rigged performance, facial animation and prop contact

The Blender scene compiler supports imported rigged GLB/glTF/FBX assets, exact named Blender actions, explicit armature bone pose keyframes, facial shape-key/blendshape keyframes, and props parented to an exact character bone with local offset/rotation. Story generation should inspect imported rigs and shape keys before writing animation data. Use a prepared action clip or explicit pose keyframes for an armature; custom pose keys replace the active armature action. Facial shape keys animate separately. Bone parenting makes a prop follow a hand but does not solve finger closure, collision, grip pressure or physics; those require dedicated rig controls/constraints and visual review. Never claim lip-sync unless viseme/phoneme timing is actually generated and checked against the voice.
