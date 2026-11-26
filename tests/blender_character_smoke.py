"""Blender integration test for reusable procedural humanoid generation."""
import sys
from pathlib import Path
import bpy

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "runtime"))
from story_scene import create_stylized_humanoid, make_material


def main():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    root = bpy.data.objects.new("Hero_Root", None)
    bpy.context.scene.collection.objects.link(root)
    cache = {}
    spec = {
        "name": "Hero",
        "character": {
            "type": "stylized_humanoid",
            "height": 3.4,
            "skin_color": [0.55, 0.32, 0.2],
            "clothing_color": [0.08, 0.22, 0.68],
            "accent_color": [0.9, 0.42, 0.08],
            "hair_color": [0.035, 0.02, 0.015],
            "motion": "walk",
            "motion_cycles": 1.0,
            "cape": True,
            "hat": True,
        },
    }
    parts = create_stylized_humanoid(spec, cache, root, fps=30, total_frames=31)
    required = {"head", "torso", "pelvis", "eye_white_left", "eye_white_right",
                "upper_arm_left", "upper_arm_right", "hand_left", "hand_right",
                "thigh_left", "thigh_right", "shoe_left", "shoe_right", "cape", "hat_crown"}
    assert required.issubset(set(parts)), "Missing generated character parts"
    assert len(parts) >= 25, "Character should have detailed separated mesh parts"
    assert all(obj.type == "MESH" and obj.data.materials for obj in parts.values())
    assert parts["thigh_left"].animation_data and parts["thigh_left"].animation_data.action
    assert parts["upper_arm_right"].animation_data and parts["upper_arm_right"].animation_data.action
    assert all(obj.parent == root for obj in parts.values())
    print("PASS: procedural humanoid meshes, materials, accessories, hierarchy and walk-cycle keys")


if __name__ == "__main__":
    main()
