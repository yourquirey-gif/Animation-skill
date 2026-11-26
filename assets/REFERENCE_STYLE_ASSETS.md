# Reference-style 3D asset packs

The two user-supplied visual references call for stylized, expressive humanoid characters and detailed fantasy/palace environments. Use these verified CC0 packs as the first humanoid pipeline baseline; they are not photorealistic film assets and must be previewed before use.

## Rigged humanoid bases
- **Quaternius Universal Base Characters** — six animation-friendly humanoid base models, rigged humanoid skeleton, glTF/FBX/Blend formats, 20 hairstyles, CC0. Official source: https://quaternius.com/packs/universalbasecharacters.html
- Free Standard download page: https://quaternius.itch.io/universal-base-characters

## Retargetable motion
- **Quaternius Universal Animation Library** — 120+ humanoid actions (locomotion, combat, emotes, swim/crawl, etc.), universal retarget-friendly rig, FBX/GLB/Blend, CC0. Official source: https://quaternius.com/packs/universalanimationlibrary.html
- Download page: https://quaternius.itch.io/universal-animation-library

## Integration contract
1. Download the Standard/CC0 packs from the publisher. Do not scrape private or paid Source files.
2. Put extracted character and animation files under `assets/characters/` and `assets/animations/` respectively; do not commit large packs unless explicitly intended.
3. Record the exact downloaded filenames, publisher URL, CC0 license evidence, armature name, action names and bone map in a project-local asset manifest.
4. Import the character GLB/FBX into Blender. Import the animation GLB/FBX separately, select its source armature/action, then call `runtime/rig_retarget.py` with an explicit source-to-target bone map. Never assume Mixamo/Quaternius/other skeleton names match.
5. Preview feet, root motion, shoulder/hip axes and hand contacts. Adjust per-rig rotation offsets. The retargeter bakes mapped local rotations; it is not a full motion-capture cleanup or foot-lock solver.
6. Face/lip sync requires a facial rig with named mouth shape keys (or a separately mapped facial bone rig). A body-only humanoid rig cannot produce expressive mouth animation.

## Reference visual direction
Use these assets as a rig/animation foundation, then create story-specific costumes, hair, facial features, palace architecture, lanterns, props, lighting and cinematic camera work. Avoid reusing the same base appearance for every character.
