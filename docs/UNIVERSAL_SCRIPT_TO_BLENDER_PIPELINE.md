# Universal Script-to-Blender Production Contract

## Non-negotiable architecture

The repository must separate the universal production engine from each individual story.

- **Story planner (Claude Code):** reads the user's idea, script or audio; extracts story beats, cast, locations, props, actions, dialogue, emotions, continuity and timing; then authors a project-specific scene manifest.
- **Asset resolver:** searches the licensed asset catalog and installed asset library, checks actual files and metadata, and selects compatible models, rigs, actions, materials and props. It must never pretend a catalog entry is a downloaded asset.
- **Blender scene builder (Python/bpy):** reads the manifest and constructs/imports the actual 3D scene. It instantiates characters, environments and props, assigns materials, rigs, cameras and lights, and creates animation from semantic action plans.
- **Render manager:** schedules preview/final shot renders, caches reusable assets, retries failed shots, records progress and render metrics, and resumes completed shots.
- **Media finisher:** aligns actual narration, visemes and captions, mixes audio, concatenates rendered shots and validates the MP4.

Blender is the 3D renderer and scene runtime. It should not be expected to infer a story from raw prose on its own. Claude Code performs story understanding and produces structured scene instructions; Blender executes those instructions as real 3D scenes and animation.

## Runtime input contract

Each project has its own folder, e.g. `projects/<project-id>/`:
- `source.md` or private audio reference (do not commit private audio to a public repository)
- `story_bible.json`
- `character_bible.json`
- `location_bible.json`
- `storyboard.json`
- `asset_manifest.json`
- `renders/`, `blender/`, `reports/`

The storyboard is generated from the current user's story. It must not be copied from a fixed sample or smoke-test fixture.

Each shot must describe:
- shot ID and duration
- location and time/weather
- characters/subjects present, identity references and exact 3D asset/rig resolution
- each subject's starting transform, action, emotion, gaze, gesture and ending state
- props, attachment/grip/transfer events and physical interactions
- camera position, lens, framing, focus and movement
- lighting, atmosphere and environment motion
- dialogue/narration/SFX/music timing and caption cues
- continuity links to previous/next shots
- quality profile and output paths

## Dynamic scene construction

The Blender builder must iterate over the manifest's entities and instantiate what that story actually needs. It must not contain story-specific constants such as a fixed number of bridge visitors, named story characters, a hard-coded palace, or a fixed sequence of actions.

- Entity counts come from the generated manifest, not constants in renderer source.
- Character models are resolved from the asset library by type, style, rig and quality needs. If no suitable asset exists, create or obtain a story-specific model/rig through an explicit supported path; never quietly substitute primitive stick/capsule figures for final-quality humans.
- Environment geometry, props, crowd placement, camera coverage and lighting are generated from the story's location description and spatial plan.
- Crowd scenes use instancing/LOD and varied approved models, outfits, poses and gaze targets. Crowd members should have plausible placement and animation; avoid identical cloned silhouettes.
- Semantic actions (walk, run, look, sit, point, pick up, hold, throw, build, react, speak, etc.) map to validated rig controls or prepared animation clips. If a rig lacks a required control/action, report the gap rather than faking it with an unrelated transform.
- Dialogue is assigned to the correct subject and aligned to actual audio timestamps. Facial performance requires real facial controls/shape keys.
- Every shot is checked for visual continuity, contact, framing, lighting and missing assets before final rendering.

## Test-fixture policy

Smoke-test fixtures are synthetic QA inputs only. They may contain a deliberately small fixed test scene to validate that a code path works. They are never templates for production stories and must never be shipped as the user's finished video.

A crowd test fixture may specify a crowd size to test crowd rendering, but the production engine must accept arbitrary crowd sizes and compositions from the generated storyboard. Do not hard-code the bridge/sunset/crowd story into the runtime.

## Required implementation milestones

1. **Planner contract:** validate story bible and storyboard JSON against schemas; ensure all required fields and references exist.
2. **Asset inventory:** scan actual downloaded assets and record license, formats, rig names, actions, shape keys, dimensions and preview renders.
3. **Character system:** reusable rigged character loading, identity/wardrobe consistency, crowd instancing, LOD and semantic animation mapping.
4. **Environment system:** reusable modular 3D set generation/import, terrain/architecture/props, lighting and atmosphere.
5. **Action system:** semantic action-to-rig mapping, IK/constraints, contact-aware props, facial expression and viseme timing.
6. **Shot builder:** per-shot Blender scene assembly from manifest; no story-specific code branches.
7. **Render manager:** preview/final tiers, per-shot caching, parallel execution where runner capacity permits, retries/resume and real performance measurements.
8. **Finalizer and QA:** audio/caption alignment, FFmpeg assembly, ffprobe metadata checks and actual frame review.

## Acceptance tests

- Run at least three unrelated story manifests without changing renderer source code.
- Vary crowd size, character count, locations, props, shot count, duration and aspect ratio solely through project data.
- Demonstrate a close-up acting shot, a crowd-wide shot, a prop interaction and a voice/lip-sync shot using actual suitable assets.
- Verify that missing assets/rig controls fail with clear actionable errors rather than silently rendering placeholders.
- Compare preview/final timing and report measured performance; do not claim a speed target until benchmarked.
- Inspect the actual MP4 and representative frames. A successful process exit or ffprobe PASS alone is not a visual-quality pass.
