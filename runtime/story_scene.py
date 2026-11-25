"""Universal JSON-to-Blender scene compiler.

Claude authors story-specific storyboard JSON; this renderer turns each shot's
3D environment, subjects, props, camera and animation into real rendered frames.
No story/genre is hard-coded here. Run inside Blender's bundled Python:
blender --background --python-exit-code 1 --python story_scene.py -- --storyboard ... --shot-index 0 --output-dir ...
"""
import argparse
import json
import math
import sys
from pathlib import Path

import bpy
from mathutils import Vector


PRIMITIVES = {"cube", "uv_sphere", "ico_sphere", "cylinder", "cone", "torus", "plane"}
DEFAULT_MATERIAL = {"color": [0.35, 0.42, 0.55], "roughness": 0.7, "metallic": 0.0}


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--storyboard", required=True)
    parser.add_argument("--shot-index", type=int, required=True)
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--width", type=int, default=1080)
    parser.add_argument("--height", type=int, default=1920)
    parser.add_argument("--fps", type=int, default=24)
    parser.add_argument("--samples", type=int, default=32)
    return parser.parse_args(sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else [])


def vector(value, default):
    if value is None:
        value = default
    if not isinstance(value, list) or len(value) != 3:
        raise ValueError("3D vectors must be arrays of exactly three numbers")
    return tuple(float(x) for x in value)


def validate(story):
    if not isinstance(story, dict) or not isinstance(story.get("shots"), list) or not story["shots"]:
        raise ValueError("Storyboard must contain a non-empty 'shots' array")
    for i, shot in enumerate(story["shots"]):
        if not isinstance(shot, dict):
            raise ValueError(f"shots[{i}] must be an object")
        if float(shot.get("duration_seconds", 0)) <= 0:
            raise ValueError(f"shots[{i}].duration_seconds must be positive")
        for group in ("environment", "subjects", "props"):
            value = shot.get(group, [] if group != "environment" else {})
            if group == "environment":
                if not isinstance(value, dict) or not isinstance(value.get("objects", []), list):
                    raise ValueError(f"shots[{i}].environment.objects must be an array")
            elif not isinstance(value, list):
                raise ValueError(f"shots[{i}].{group} must be an array")
            entries = value.get("objects", []) if group == "environment" else value
            for j, entry in enumerate(entries):
                if entry.get("primitive", "cube") not in PRIMITIVES:
                    raise ValueError(f"Unsupported primitive at shots[{i}].{group}[{j}]")
                for kf in entry.get("keyframes", []):
                    if float(kf.get("time_seconds", -1)) < 0:
                        raise ValueError("keyframe time_seconds cannot be negative")
    return story


def make_material(spec, cache):
    spec = {**DEFAULT_MATERIAL, **(spec or {})}
    key = json.dumps(spec, sort_keys=True)
    if key in cache:
        return cache[key]
    color = vector(spec.get("color"), DEFAULT_MATERIAL["color"])
    if any(c < 0 or c > 1 for c in color):
        raise ValueError("Material color components must be between 0 and 1")
    mat = bpy.data.materials.new("Generated_Material_" + str(len(cache) + 1))
    mat.diffuse_color = (*color, 1)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs["Base Color"].default_value = (*color, 1)
    bsdf.inputs["Roughness"].default_value = max(0.0, min(1.0, float(spec.get("roughness", 0.7))))
    bsdf.inputs["Metallic"].default_value = max(0.0, min(1.0, float(spec.get("metallic", 0.0))))
    cache[key] = mat
    return mat


def create_mesh(spec, cache, collection=None):
    primitive = spec.get("primitive", "cube")
    location = vector(spec.get("location"), [0, 0, 0])
    scale = vector(spec.get("scale"), [1, 1, 1])
    rotation = vector(spec.get("rotation"), [0, 0, 0])
    name = str(spec.get("name", "Story_Object"))
    if primitive == "cube":
        bpy.ops.mesh.primitive_cube_add(size=1, location=location)
    elif primitive == "uv_sphere":
        bpy.ops.mesh.primitive_uv_sphere_add(segments=32, ring_count=20, radius=1, location=location)
    elif primitive == "ico_sphere":
        bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2, radius=1, location=location)
    elif primitive == "cylinder":
        bpy.ops.mesh.primitive_cylinder_add(vertices=32, radius=1, depth=2, location=location)
    elif primitive == "cone":
        bpy.ops.mesh.primitive_cone_add(vertices=32, radius1=1, radius2=0, depth=2, location=location)
    elif primitive == "torus":
        bpy.ops.mesh.primitive_torus_add(major_segments=48, minor_segments=12, location=location)
    elif primitive == "plane":
        bpy.ops.mesh.primitive_plane_add(size=2, location=location)
    obj = bpy.context.object
    obj.name = name
    obj.rotation_euler = rotation
    obj.scale = scale
    obj.data.materials.append(make_material(spec.get("material"), cache))
    if spec.get("bevel", 0):
        bevel = obj.modifiers.new("Story_Soft_Edges", "BEVEL")
        bevel.width = float(spec["bevel"])
        bevel.segments = 3
        obj.modifiers.new("Story_Weighted_Normals", "WEIGHTED_NORMAL")
    if spec.get("smooth", primitive in ("uv_sphere", "ico_sphere", "torus")):
        if obj.type == "MESH":
            for face in obj.data.polygons:
                face.use_smooth = True
    if collection is not None:
        for col in list(obj.users_collection):
            col.objects.unlink(obj)
        collection.objects.link(obj)
    return obj


def apply_keyframes(obj, keyframes, fps, total_frames):
    if not keyframes:
        return
    for key in keyframes:
        frame = max(1, min(total_frames, 1 + round(float(key["time_seconds"]) * fps)))
        if "location" in key:
            obj.location = vector(key["location"], list(obj.location))
            obj.keyframe_insert(data_path="location", frame=frame)
        if "rotation" in key:
            obj.rotation_euler = vector(key["rotation"], list(obj.rotation_euler))
            obj.keyframe_insert(data_path="rotation_euler", frame=frame)
        if "scale" in key:
            obj.scale = vector(key["scale"], list(obj.scale))
            obj.keyframe_insert(data_path="scale", frame=frame)
    if obj.animation_data and obj.animation_data.action:
        for fc in obj.animation_data.action.fcurves:
            for point in fc.keyframe_points:
                point.interpolation = "BEZIER"


def aim(camera, target):
    camera.rotation_euler = (Vector(target) - camera.location).to_track_quat("-Z", "Y").to_euler()


def build_camera(spec):
    spec = spec or {}
    bpy.ops.object.camera_add(location=vector(spec.get("location"), [7, -10, 6]))
    camera = bpy.context.object
    camera.name = "Story_Camera"
    camera.data.lens = float(spec.get("lens", 50))
    aim(camera, vector(spec.get("target"), [0, 0, 1]))
    bpy.context.scene.camera = camera
    for key in spec.get("keyframes", []):
        frame = max(1, min(bpy.context.scene.frame_end, 1 + round(float(key["time_seconds"]) * bpy.context.scene.render.fps)))
        if "location" in key:
            camera.location = vector(key["location"], list(camera.location))
            camera.keyframe_insert(data_path="location", frame=frame)
        if "target" in key:
            aim(camera, vector(key["target"], [0, 0, 1]))
            camera.keyframe_insert(data_path="rotation_euler", frame=frame)
        if "lens" in key:
            camera.data.lens = float(key["lens"])
            camera.data.keyframe_insert(data_path="lens", frame=frame)
    return camera


def add_lights(lights):
    if not lights:
        lights = [
            {"type": "AREA", "location": [2, -5, 7], "energy": 1100, "size": 5},
            {"type": "AREA", "location": [-5, 2, 4], "energy": 700, "size": 4, "color": [0.35, 0.55, 1.0]},
        ]
    for item in lights:
        kind = str(item.get("type", "AREA")).upper()
        if kind not in {"AREA", "POINT", "SUN", "SPOT"}:
            raise ValueError("Light type must be AREA, POINT, SUN or SPOT")
        bpy.ops.object.light_add(type=kind, location=vector(item.get("location"), [0, -4, 5]))
        light = bpy.context.object
        light.name = str(item.get("name", "Story_" + kind + "_Light"))
        light.data.energy = float(item.get("energy", 800))
        if "color" in item:
            light.data.color = vector(item["color"], [1, 1, 1])
        if kind == "AREA":
            light.data.shape = "DISK"
            light.data.size = float(item.get("size", 4))
        if "target" in item:
            aim(light, vector(item["target"], [0, 0, 0]))


def main():
    args = parse_args()
    story_path = Path(args.storyboard)
    story = validate(json.loads(story_path.read_text(encoding="utf-8")))
    if args.shot_index < 0 or args.shot_index >= len(story["shots"]):
        raise ValueError("shot-index is outside storyboard shots array")
    shot = story["shots"][args.shot_index]
    out = Path(args.output_dir)
    out.mkdir(parents=True, exist_ok=True)
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    available_engines = scene.render.bl_rna.properties["engine"].enum_items.keys()
    scene.render.engine = "BLENDER_EEVEE_NEXT" if "BLENDER_EEVEE_NEXT" in available_engines else "BLENDER_EEVEE"
    scene.eevee.taa_render_samples = max(8, args.samples)
    scene.render.resolution_x = args.width
    scene.render.resolution_y = args.height
    scene.render.resolution_percentage = 100
    scene.render.fps = args.fps
    scene.frame_start = 1
    scene.frame_end = max(1, round(float(shot["duration_seconds"]) * args.fps))
    scene.render.image_settings.file_format = "PNG"
    scene.render.film_transparent = False
    scene.world = bpy.data.worlds.new("Story_World")
    scene.world.color = tuple(shot.get("environment", {}).get("world_color", [0.025, 0.03, 0.05]))
    scene.view_settings.view_transform = "AgX"
    cache = {}

    env = shot.get("environment", {})
    for item in env.get("objects", []):
        obj = create_mesh(item, cache)
        apply_keyframes(obj, item.get("keyframes", []), args.fps, scene.frame_end)
    for item in shot.get("subjects", []):
        root = bpy.data.objects.new(str(item.get("name", "Subject")) + "_Root", None)
        scene.collection.objects.link(root)
        for part in item.get("parts", []):
            obj = create_mesh(part, cache)
            obj.parent = root
        apply_keyframes(root, item.get("keyframes", []), args.fps, scene.frame_end)
    for item in shot.get("props", []):
        obj = create_mesh(item, cache)
        apply_keyframes(obj, item.get("keyframes", []), args.fps, scene.frame_end)

    build_camera(shot.get("camera", {}))
    add_lights(shot.get("lighting", []))
    # Render every frame to disk; no still-image pan/zoom substitution.
    for frame in range(1, scene.frame_end + 1):
        scene.frame_set(frame)
        scene.render.filepath = str(out / ("frame_%04d.png" % frame))
        bpy.ops.render.render(write_still=True)

    report = {
        "status": "RENDERED",
        "shot_id": shot.get("id", str(args.shot_index + 1)),
        "frames": scene.frame_end,
        "fps": args.fps,
        "resolution": [args.width, args.height],
        "rendered_frame_pattern": str((out / "frame_%04d.png").resolve()),
        "scene_object_count": len(scene.objects),
        "blend_file": str((out / "shot.blend").resolve()),
    }
    bpy.ops.wm.save_as_mainfile(filepath=report["blend_file"])
    (out / "shot_report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
