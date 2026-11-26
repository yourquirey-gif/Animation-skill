"""Blender integration test for transparent 2D sprites in a 3D scene."""
import tempfile
import sys
from pathlib import Path

import bpy

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from runtime.story_scene import create_mesh


def main():
    with tempfile.TemporaryDirectory(prefix="sprite-smoke-") as tmp:
        image_path = Path(tmp) / "character.png"
        image = bpy.data.images.new("SpriteSmokeImage", width=4, height=4, alpha=True)
        image.pixels = [component for _ in range(16) for component in (1.0, 0.2, 0.1, 0.0 if _ % 2 else 1.0)]
        image.filepath_raw = str(image_path)
        image.file_format = "PNG"
        image.save()
        bpy.data.images.remove(image)

        material_cache = {}
        obj = create_mesh({
            "name": "Hybrid_2D_Character",
            "primitive": "sprite",
            "image_file": str(image_path),
            "location": [0, 0, 1],
            "scale": [1, 2, 1],
        }, material_cache, base_dir=tmp)

        assert obj.type == "MESH"
        assert obj.get("story_character_mode") == "2D_SPRITE_IN_3D_WORLD"
        assert abs(obj.rotation_euler.x - 1.57079632679) < 1e-5
        assert abs(obj["sprite_aspect_ratio"] - 1.0) < 1e-5
        assert obj.get("sprite_source") == str(image_path)
        material = obj.data.materials[0]
        assert material.use_nodes
        image_nodes = [node for node in material.node_tree.nodes if node.type == "TEX_IMAGE"]
        assert len(image_nodes) == 1 and image_nodes[0].image is not None
        bsdf = next(node for node in material.node_tree.nodes if node.type == "BSDF_PRINCIPLED")
        assert any(link.to_node == bsdf and link.to_socket.name == "Alpha" for link in material.node_tree.links)
        second = create_mesh({
            "name": "Second_Hybrid_2D_Character",
            "primitive": "sprite",
            "image_file": str(image_path),
            "location": [2, 0, 1],
        }, material_cache, base_dir=tmp)
        assert second.data.materials[0] != material, "Sprite materials must not share image textures"
        print("HYBRID_2D_SPRITE_IN_3D_WORLD_OK", {
            "object": obj.name,
            "image": image_path.name,
            "alpha_linked": True,
            "upright": True,
            "isolated_materials": True,
            "transform": list(obj.location),
        })


if __name__ == "__main__":
    main()
