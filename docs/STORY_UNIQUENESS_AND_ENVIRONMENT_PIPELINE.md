# Story-by-story unique world and production design

## Non-negotiable objective

Every story must feel like it was designed and produced as its own world. Do not carry over a prior story's full set, background, layout, character cast, wardrobe, prop dressing, lighting, camera blocking or shot composition. Asset libraries provide reusable components, not ready-made story worlds.

## Required project artifacts

Each project must persist:

- `story_id` and a short art-direction brief.
- `character_bible.json`: stable identity and visual/performance specification for every recurring character, plus controlled variation specs for crowd members.
- `location_bible.json`: one record per distinct location with a unique `location_id`, visual brief, layout, geometry/landform, architecture, materials, landmarks, dressing, weather, time of day, atmosphere and lighting concept.
- `prop_bible.json`: story-critical object design, materials, scale, ownership and state changes.
- `environment_manifest.json`: generated and imported components, source/license metadata, placement, material variants and environment fingerprint.
- `storyboard.json`: each shot references its location, characters, props, action, camera, lighting and continuity constraints.

## Environment design workflow

1. Extract the story's actual places, era, climate, culture, scale, mood and action requirements.
2. Design a location concept before opening Blender. Define spatial layout, foreground/midground/background, routes, landmarks, playable areas, sight lines and camera positions.
3. Search the approved asset catalog for components that fit. Verify files, license, style, scale, material quality and rig compatibility. Never infer that a catalog entry means a finished asset is present.
4. Generate missing architecture, terrain, vegetation, set dressing and props procedurally or create/import suitable models. Use procedural primitives only for blocking; final environments require detailed geometry/materials and visual dressing.
5. Assign a unique location ID and compute a deterministic fingerprint from normalized design inputs. Store it in the location manifest.
6. Compare fingerprints between different locations in the same story. Similar fingerprints trigger a redesign unless they intentionally depict the same physical place.
7. Reuse geometry only across shots that depict the same physical location and require continuity. A new physical location must have a separate manifest and distinct design.
8. Build story-specific weather, sky, atmosphere, time-of-day, practical lighting, color temperature, palette and camera language.
9. Populate crowds with visibly distinct models, clothing, silhouettes, placements and motion. Do not make a crowd by duplicating one model in a straight line.
10. Render low-resolution previews, inspect frames, fix defects, and only then approve final rendering.

## What may be reused

A licensed tree, rock, chair, vehicle, wall module, texture, HDRI, animation clip or rig may be reused when appropriate. It must be recontextualized through placement, scale, materials, variants and set dressing. Do not reuse a complete environment, complete shot, or previous story's entire scene collection unchanged. Track reuse in the manifest and disclose it in the QA report.

## Automated and visual acceptance gates

- Every shot's `location_id` resolves to a location manifest.
- Every location has a unique ID, complete design fields and a non-empty environment fingerprint.
- Different locations in the same story do not have duplicate fingerprints, unless explicitly marked as the same physical location.
- Characters retain identity across shots; crowd members are not obvious clones.
- Story-critical props retain correct ownership and state.
- Preview inspection checks geometry detail, composition, scale, clipping, empty backgrounds, lighting, atmosphere, motion and continuity.
- QA reports reused assets and any unmet uniqueness requirement.
- A failed uniqueness or visual gate blocks final delivery. Do not call a blocking proxy scene a completed cinematic environment.

## Important distinction

“Unique for every story” does not mean rebuilding the same physical location from scratch in every shot. It means a newly designed world per story, with continuity-preserving reuse only between shots that belong to the same location. Distinct locations within a story receive distinct designs; stories do not inherit another story's world by default.
