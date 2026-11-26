# Recommended Open Asset Sources

These official sources were checked for reusable production assets. This is a discovery index only; no model binaries are bundled or silently downloaded by the skill.

| Source | Useful content | License evidence |
|---|---|---|
| [Quaternius Universal Base Characters](https://quaternius.com/packs/universalbasecharacters.html) | Six humanoid base characters, rigged proportions and hairstyles | Official pack page labels the pack CC0 and lists FBX/glTF/OBJ formats |
| [Quaternius Universal Animation Library](https://quaternius.com/packs/universalanimationlibrary.html) | 120+ humanoid animation clips for retargeting | Official pack page labels the pack CC0 |
| [Poly Haven](https://polyhaven.com) | HDRIs, PBR textures and 3D environment models | [Official license page](https://polyhaven.com/license) states its assets are CC0 |

## Download and integrate safely

1. Download only from the official source page.
2. Check the license shown on the specific pack/asset at the time of download and retain a copy or record of the terms.
3. Inspect archive contents and supported formats; do not assume every file listed on a pack page is in the free download.
4. Extract into the matching `assets/` category.
5. Inspect Blender import, scale, orientation, mesh integrity, materials, armature, bone names, shape keys and animation actions.
6. Register the exact file in `assets/catalog.json` with the correct path, source URL, license, attribution, rig and compatibility.
7. Run `python runtime/asset_catalog.py validate` and a small Blender preview render.

Quaternius humanoid animation packs are not a universal retarget guarantee: inspect the skeleton and retarget mapping for each model. Poly Haven assets are useful for environment realism but do not supply a character/animation system.

No paid asset or provider is required by the base pipeline. Do not scrape websites or guess download URLs; use official download links and respect each provider's terms.
