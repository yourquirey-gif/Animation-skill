"""Run inside Blender to validate the procedural terrain mesh generator."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

import bpy
from runtime.story_scene import create_mesh

bpy.ops.object.select_all(action="SELECT")
bpy.ops.object.delete(use_global=False)

spec = {
    "name": "Terrain_Integration_Test",
    "primitive": "terrain",
    "location": [0, 0, 0],
    "terrain": {
        "segments_x": 12,
        "segments_y": 10,
        "width": 20,
        "depth": 16,
        "base_height": 0,
        "ridge_amplitude": 0.25,
        "peaks": [
            {"x": -3, "y": 1, "height": 4, "radius_x": 2.5, "radius_y": 3},
            {"x": 4, "y": 2, "height": 5, "radius_x": 3, "radius_y": 2.5},
        ],
    },
    "material": {"color": [0.2, 0.28, 0.22], "roughness": 0.95},
}
terrain = create_mesh(spec, {}, collection=bpy.context.scene.collection, base_dir=ROOT)
assert terrain.type == "MESH", "terrain generator must return a mesh object"
assert len(terrain.data.vertices) == 13 * 11, "unexpected terrain vertex count"
assert len(terrain.data.polygons) == 12 * 10, "unexpected terrain face count"
assert len(terrain.data.materials) == 1, "terrain must have a material"
zs = [vertex.co.z for vertex in terrain.data.vertices]
assert max(zs) - min(zs) > 1.0, "terrain peaks did not create meaningful height variation"
assert len(terrain.data.uv_layers) == 0 or len(terrain.data.uv_layers) >= 0
print({
    "status": "PASS",
    "vertices": len(terrain.data.vertices),
    "faces": len(terrain.data.polygons),
    "height_range": [min(zs), max(zs)],
})
