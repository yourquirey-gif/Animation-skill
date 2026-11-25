# Local Runtime

The skill bundles executable Python tools for environment inspection and a real Blender-to-FFmpeg integration test.

Requirements: Blender executable (with bundled Python/bpy), FFmpeg with libx264, ffprobe, and Python 3.10+ for orchestration.

Run from the skill folder:

    python runtime/animation_runtime.py inspect
    python runtime/animation_runtime.py smoke-test --workdir animation_work/smoke_test

Optional executable overrides: BLENDER_BIN, FFMPEG_BIN, FFPROBE_BIN.

The smoke test creates actual animated 3D geometry, a prop, terrain, camera and lights; renders PNG frames with Blender; encodes MP4 with FFmpeg; and checks the result with ffprobe. It saves a .blend, frames, logs and a JSON report.

This is a technical integration test, not a finished story or proof of cinematic art quality. Each user story still needs its own characters, props, environments, actions, camera and lighting implementation, followed by preview inspection.

Use Blender's embedded Python for bpy. The supported invocation is Blender background mode with --python and --python-exit-code 1. Do not assume system Python can import bpy, and avoid GUI-only operators in headless scripts.


## Story-driven rendering

Claude should convert each arbitrary user story/script/audio plan into a project-specific JSON storyboard, then run:

    python runtime/render_story.py --storyboard projects/<id>/storyboard.json --output projects/<id>/final.mp4 --format shorts

For a horizontal long video:

    python runtime/render_story.py --storyboard projects/<id>/storyboard.json --output projects/<id>/final.mp4 --format long

Optional narration, music and subtitles:

    python runtime/render_story.py --storyboard projects/<id>/storyboard.json --output projects/<id>/final.mp4 --voice voice.wav --music music.wav --captions captions.srt

The storyboard contains a sequence of shots. Each shot defines its own environment objects, subject assemblies, props, keyframes, camera and lights. See `templates/storyboard.universal.example.json`. Claude must create a new storyboard and story-specific assets for every production; the example JSON is a schema illustration only.

The current scene compiler supports procedural mesh primitives and transform/camera keyframes. It is a working foundation for generated 3D scenes, not a claim that primitive geometry alone achieves feature-film character quality. Production art direction, detailed meshes/rigs, contact-aware hand/prop actions, facial performance and lip-sync still require story-specific asset/animation work and visual QA.


### Detailed model assets

Storyboard object/subject-part entries may use `asset_file` instead of a procedural primitive. Supported imports are `.glb`, `.gltf` and `.fbx`; relative paths resolve from the storyboard JSON file. GLB/glTF is preferred for embedded PBR materials and hierarchy. An optional `asset_action` selects an imported Blender action by exact action name for imported armatures. Keep asset licenses and source notes in the project asset manifest. The renderer does not download models or assume external asset access.


### Rigged character animation and facial performance

For a detailed character model, provide an imported rigged GLB/glTF or FBX with its armature and (for facial animation) shape keys/blendshapes. A subject entry may use:

- `asset_file`: model path relative to the storyboard.
- `asset_action`: exact existing Blender action name to play from the imported asset.
- `pose_keyframes`: per-time bone transforms keyed by exact armature bone names; each transform may contain Euler `rotation`, `location` or `scale` arrays.
- `facial_keyframes`: per-time shape-key values keyed by exact imported shape-key names, with values from 0 to 1.

Example fragment:

    {
      "name": "StoryHero",
      "asset_file": "assets/hero.glb",
      "pose_keyframes": [
        {"time_seconds": 0, "bones": {"upper_arm.L": {"rotation": [0, 0, 0]}}},
        {"time_seconds": 1, "bones": {"upper_arm.L": {"rotation": [0, 0.8, 0]}}}
      ],
      "facial_keyframes": [
        {"time_seconds": 0, "shapes": {"Smile": 0.0, "MouthOpen": 0.0}},
        {"time_seconds": 1, "shapes": {"Smile": 0.7, "MouthOpen": 0.15}}
      ]
    }

Bone and shape-key names are asset-specific: inspect the imported model first and use its actual names. `pose_keyframes` creates a dedicated action for the supplied bone poses; do not combine it with `asset_action` on the same armature because the pose action becomes the active action. Use an imported action for a prepared motion clip, or explicit pose keyframes for custom performance. Facial shape-key animation is a separate animation channel.

This enables real rig-driven performance when suitable assets exist; it does not magically auto-rig arbitrary downloaded meshes. If a character asset has no rig, Claude must create/rig an appropriate model or state the limitation rather than pretending it can perform skeletal acting.


### Props attached to character hands/bones

To keep a prop attached to an animated hand or other rig bone, put `attach_to` on its prop entry. It references the subject name and exact armature bone name; `offset` and `rotation` are local to that bone:

    {
      "name": "Lantern",
      "asset_file": "assets/lantern.glb",
      "attach_to": {
        "subject": "StoryHero",
        "bone": "hand.R",
        "offset": [0.02, 0.0, 0.08],
        "rotation": [0.0, 0.0, 0.0]
      }
    }

This gives the prop a real Blender bone parent, so it follows the character's animated hand. Claude must inspect the model's real bone names and tune local offsets from a preview. It does not automatically solve finger gripping, collisions or contact physics; those need a suitable hand rig, constraints and story-specific animation.


### Audio-aligned lip-sync (viseme tracks)

A subject can use `viseme_map` and `viseme_keyframes` to animate imported facial blendshapes from a phoneme/viseme alignment track. The map keys are viseme labels and values are the exact imported shape-key names. Each event supplies `time_seconds`, `viseme`, and optional `strength` (0–1). Example:

    {
      "name": "NarratorCharacter",
      "asset_file": "assets/character.glb",
      "viseme_map": {
        "REST": "Mouth_Closed", "AA": "Mouth_A", "EE": "Mouth_E",
        "OH": "Mouth_O", "FV": "Mouth_FV"
      },
      "viseme_keyframes": [
        {"time_seconds": 0.00, "viseme": "REST"},
        {"time_seconds": 0.18, "viseme": "AA", "strength": 0.9},
        {"time_seconds": 0.34, "viseme": "EE", "strength": 0.8},
        {"time_seconds": 0.52, "viseme": "REST"}
      ]
    }

The timestamps must come from actual audio/phoneme alignment (or carefully authored dialogue timing) on the same unmodified master-audio timeline. The Blender renderer animates the supplied viseme events; it does not itself recognize speech or infer phonemes from a WAV. If no trustworthy alignment tool is available, do not invent precise mouth timing. `viseme_map` must match the model's actual blendshape names. This is mouth-shape animation, not proof of perfect speech synchronization; inspect close-up previews and refine coarticulation/strengths.

### Render integrity checks

The end-to-end renderer verifies the exact expected number of PNG frames per shot, PNG signatures, each frame's dimensions, final video stream, final duration, and requested audio stream. It also flags adjacent byte-identical frames as review candidates in `final_report.json`; static holds can be intentional, so these are warnings rather than automatic failures. Visual review remains mandatory for black frames, camera framing, frozen motion, flicker, anatomy and contact quality.
