# Animation Skill for Claude Code

A reusable Claude Code skill for producing complete cinematic animated story videos through code.

## Install in a project

```bash
mkdir -p .claude/skills
git clone https://github.com/yourquirey-gif/Animation-skill.git .claude/skills/animation-skill
```

The Claude Code skill entry point is:

```
.claude/skills/animation-skill/SKILL.md
```

Reopen Claude Code if the skill is not immediately discovered.

## Code-first production

The default workflow does not require a paid AI video API. Claude Code writes the code and automation; Blender performs actual 3D modeling, rigging, animation, and rendering; Python orchestrates story/scene data, assets, audio, subtitles, and QA; FFmpeg assembles and validates the final MP4.

The skill instructs Claude Code to:
- Ask whether the user wants an idea, has a script, or is supplying voice/audio; skip questions already answered and start audio-led analysis immediately when audio is uploaded.
- Ask for duration and Shorts/Long format only when those details are still needed.
- Create story-specific scripts with a strong opening, escalating curiosity, a truthful final payoff, and natural loop where suitable.
- Inspect the user's machine and available tools first.
- Analyze supplied reference videos and document their visual style.
- Turn any story into a structured storyboard and scene manifest.
- Build reusable procedural 3D characters, rigs, props, and environments using Blender Python (bpy).
- Animate real geometry using keyframes, rigs, constraints, shape keys, and physics where useful.
- Render preview shots, inspect them, improve quality, and render final scenes.
- Add narration/audio and synchronized subtitles using available local tools or user-provided audio.
- Assemble, encode, and validate the final video using FFmpeg/ffprobe.
- Save project files and intermediate assets so failed renders can resume.

## Documentation

- `SKILL.md` — main Claude Code skill instructions and mandatory workflow.
- `docs/INTERACTIVE_INTAKE_AND_PRODUCTION.md` — idea/script/audio intake, duration/format questions, script styles, storyboard, and production gates.
- `docs/APP_IMPLEMENTATION_SPEC.md` — implementation contract for the actual reusable Blender/Python/FFmpeg application.
- `docs/CODE_FIRST_PIPELINE.md` — detailed end-to-end code-first implementation architecture.
- `docs/PRODUCTION_WORKFLOW.md` — production workflow.
- `templates/shot-prompt-template.md` — reusable shot specification template.
- `templates/storyboard.example.json` — example storyboard manifest.

## Important

This repository contains the skill, instructions, and templates—not a prebuilt video-rendering service. Claude Code must implement the actual project code in the user's working repository and run it with available local tools. Blender and FFmpeg must be installed or made available. Rendering speed and achievable visual fidelity depend on hardware, modeling/rigging quality, and render settings.

Optional hosted AI providers are enhancements only. Do not use paid APIs or incur costs without explicit user approval. Never describe a still-image slideshow with zoom effects as actual character animation.


## Bundled executable runtime

The repository now includes a real local dependency inspector and Blender/FFmpeg smoke-test runner:

```bash
python runtime/animation_runtime.py inspect
python runtime/animation_runtime.py smoke-test
```

The smoke test builds and animates actual 3D geometry in headless Blender, renders image frames, encodes an MP4 with FFmpeg, and validates metadata with ffprobe. See runtime/README.md. This validates the local toolchain; it is not a finished story render. Claude Code must still create story-specific scenes and assets for each new script/audio/story.
