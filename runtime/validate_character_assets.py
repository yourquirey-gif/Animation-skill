"""Validate generated Ara 3D Gen GLB assets inside Blender before rendering."""
from __future__ import annotations

import argparse
from pathlib import Path
import bpy


def parse_args():
    import sys
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    parser = argparse.ArgumentParser()
    parser.add_argument("--asset-dir", required=True)
    parser.add_argument("--min-assets", type=int, default=1)
    return parser.parse_args(argv)


def clear_scene():
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)
    for action in list(bpy.data.actions):
        bpy.data.actions.remove(action)


def main():
    args = parse_args()
    asset_dir = Path(args.asset_dir).resolve()
    models = sorted(asset_dir.glob("*.glb"))
    if len(models) < args.min_assets:
        raise RuntimeError(f"Expected at least {args.min_assets} Ara GLB assets, found {len(models)}")
    summaries = []
    for path in models:
        clear_scene()
        before_actions = set(bpy.data.actions)
        bpy.ops.import_scene.gltf(filepath=str(path))
        imported = list(bpy.context.scene.objects)
        armatures = [obj for obj in imported if obj.type == "ARMATURE"]
        meshes = [obj for obj in imported if obj.type == "MESH"]
        if not armatures:
            raise RuntimeError(f"{path.name}: no armature imported")
        if not meshes:
            raise RuntimeError(f"{path.name}: no skinned mesh imported")
        shape_key_count = sum(
            max(0, len(obj.data.shape_keys.key_blocks) - 1)
            for obj in meshes if obj.data.shape_keys
        )
        actions = [a for a in bpy.data.actions if a not in before_actions]
        if not actions:
            raise RuntimeError(f"{path.name}: no animation actions imported")
        if shape_key_count == 0:
            raise RuntimeError(f"{path.name}: no facial/body blend shapes imported")
        summaries.append({
            "file": path.name,
            "armatures": len(armatures),
            "meshes": len(meshes),
            "actions": [a.name for a in actions],
            "shape_keys": shape_key_count,
        })
    print("ARA_CHARACTER_ASSET_QA", summaries, flush=True)
    print(f"ARA_CHARACTER_ASSET_QA_PASS count={len(summaries)}", flush=True)


if __name__ == "__main__":
    main()
