# Aryan 3D Character Generator

The Blender script `runtime/generate_character_showcase.py` procedurally creates a stylized 3D hero named **Aryan** and renders a 1920x1080 character sheet with 16 modeled facial-expression variants.

## Run in the cloud

Push to `blender-cloud-production`. The `Blender Python Runtime Smoke Test` workflow runs the generator after installing Blender and stores these files in the `blender-cross-genre-smoke-renders` artifact:

- `aryan_character.blend` — editable Blender scene.
- `aryan_character_16_emotions.png` — rendered full-body hero and 4x4 expression lineup.
- `character_report.json` — generation metadata and expression names.

## Expressions

Happy, Sad, Angry, Surprised, Fearful, Disgusted, Excited, Confused, Thinking, Shy, Proud, Sleepy, Shocked, Crying, Nervous, Calm.

## Current scope

This is a code-generated 3D mesh character and a modeled expression showcase. The 16 expressions are separate modeled facial variants in the preview, not yet 16 animated facial shape keys on one production rig. The generated .blend is editable; a reusable armature, deformation weights, phoneme visemes and timed facial animation are separate follow-up work. Do not describe the current showcase as a finished facial-animation rig.
