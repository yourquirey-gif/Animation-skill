# Reusable Asset Library

This library is a metadata-first registry for reusable Blender production assets. It does not pretend that empty folders contain finished models. Add legally usable model files and register each one in `catalog.json`.

## Categories
- `characters/stylized`, `characters/realistic`, `characters/animals`, `characters/historical`
- `rigs/humanoid`, `rigs/animal`, `rigs/facial`
- `animations/locomotion`, `animations/gestures`, `animations/actions`, `animations/emotions`
- `environments/forests`, `environments/mountains`, `environments/cities`, `environments/historical`, `environments/interiors`
- `props/tools`, `props/vehicles`, `props/furniture`, `props/weapons`
- `materials`, `textures`, `hdris`, `audio`, `camera_presets`, `lighting_presets`, `scene_templates`

## Register an asset
Each entry in `catalog.json` requires a stable `id`, `category`, `name`, repository-relative `path`, `format`, `visual_style`, `tags`, `license`, and `source_url`. Include `rig` and `animation_compatibility` for animated characters. Use `CC0-1.0`, `CC-BY-4.0`, or another accurate SPDX identifier only when confirmed from the source. Do not guess a license.

## Validate and search
```bash
python runtime/asset_catalog.py validate
python runtime/asset_catalog.py search --query "ancient roman soldier" --style realistic
python runtime/asset_catalog.py list --category characters
```

The registry validates metadata and file existence. It does not automatically certify mesh quality, topology, rig correctness, animation retargeting or legal rights; inspect each asset and retain source/license evidence.
