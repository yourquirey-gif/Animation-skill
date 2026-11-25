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
                if not isinstance(entry, dict):
                    raise ValueError(f"shots[{i}].{group}[{j}] must be an object")
                if entry.get("primitive", "cube") not in PRIMITIVES and not entry.get("asset_file"):
                    raise ValueError(f"Unsupported primitive at shots[{i}].{group}[{j}]")
                duration = float(shot["duration_seconds"])
                for track_name in ("keyframes", "pose_keyframes", "facial_keyframes", "viseme_keyframes"):
                    for kf in entry.get(track_name, []):
                        event_time = float(kf.get("time_seconds", -1))
                        if event_time < 0 or event_time > duration:
                            raise ValueError(
                                f"shots[{i}].{group}[{j}].{track_name} time_seconds must be within 0..{duration}"
                            )
                if entry.get("viseme_keyframes"):
                    viseme_map = entry.get("viseme_map")
                    if not isinstance(viseme_map, dict) or not viseme_map:
                        raise ValueError(f"shots[{i}].{group}[{j}] viseme_keyframes require a non-empty viseme_map")
                    for event in entry["viseme_keyframes"]:
                        label = str(event.get("viseme", "REST"))
                        if label not in viseme_map:
                            raise ValueError(f"Unknown viseme label '{label}' at shots[{i}].{group}[{j}]")
                        strength = float(event.get("strength", 1.0))
                        if strength < 0 or strength > 1:
                            raise ValueError("Viseme strength must be between 0 and 1")
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


def create_mesh(spec, cache, collection=None, base_dir=None):
    primitive = spec.get("primitive", "cube")
    location = vector(spec.get("location"), [0, 0, 0])
    scale = vector(spec.get("scale"), [1, 1, 1])
    rotation = vector(spec.get("rotation"), [0, 0, 0])
    name = str(spec.get("name", "Story_Object"))
    # Import detailed story-specific models when supplied. GLB/glTF preserves
    # PBR materials and hierarchy; FBX is supported for common rigged assets.
    if spec.get("asset_file"):
        asset_path = Path(spec["asset_file"])
        if not asset_path.is_absolute():
            asset_path = (Path(base_dir or Path.cwd()) / asset_path).resolve()
        if not asset_path.is_file():
            raise FileNotFoundError("3D asset file not found: " + str(asset_path))
        before = set(bpy.data.objects)
        suffix = asset_path.suffix.lower()
        if suffix in {".glb", ".gltf"}:
            bpy.ops.import_scene.gltf(filepath=str(asset_path))
        elif suffix == ".fbx":
            bpy.ops.import_scene.fbx(filepath=str(asset_path))
        else:
            raise ValueError("Supported detailed model formats are .glb, .gltf and .fbx: " + suffix)
        imported = [o for o in bpy.data.objects if o not in before and o.type not in {"CAMERA", "LIGHT"}]
        if not imported:
            raise RuntimeError("Blender importer produced no objects for " + str(asset_path))
        root = bpy.data.objects.new(name + "_AssetRoot", None)
        bpy.context.scene.collection.objects.link(root)
        for child in imported:
            world_matrix = child.matrix_world.copy()
            child.parent = root
            child.matrix_world = world_matrix
        root.location = location
        root.rotation_euler = rotation
        root.scale = scale
        action_name = spec.get("asset_action")
        if action_name:
            action = bpy.data.actions.get(str(action_name))
            if action is None:
                raise ValueError("Requested imported animation action not found: " + str(action_name))
            armatures = [o for o in imported if o.type == "ARMATURE"]
            if not armatures:
                raise ValueError("asset_action was supplied but imported model has no armature")
            for armature in armatures:
                armature.animation_data_create()
                armature.animation_data.action = action
        return root
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


def find_armature(root):
    stack = list(root.children)
    while stack:
        obj = stack.pop()
        stack.extend(list(obj.children))
        if obj.type == "ARMATURE":
            return obj
    return None


def apply_rig_animation(root, pose_keyframes, facial_keyframes, fps, total_frames, rig_controls=None):
    """Animate imported armature bones and mesh shape keys using story timing."""
    armatures = []
    meshes = []
    stack = list(root.children)
    while stack:
        obj = stack.pop()
        stack.extend(list(obj.children))
        if obj.type == "ARMATURE":
            armatures.append(obj)
        elif obj.type == "MESH":
            meshes.append(obj)

    if pose_keyframes and not armatures:
        raise ValueError("pose_keyframes require an imported rigged model with an armature")

    for armature in armatures:
        if not pose_keyframes:
            continue
        armature.animation_data_create()
        # A dedicated per-shot action keeps source-library actions untouched.
        action = bpy.data.actions.new("StoryPose_" + armature.name)
        armature.animation_data.action = action
        for entry in pose_keyframes:
            frame = max(1, min(total_frames, 1 + round(float(entry["time_seconds"]) * fps)))
            bones = entry.get("bones", {})
            for bone_name, transform in bones.items():
                pose_bone = armature.pose.bones.get(bone_name)
                if pose_bone is None:
                    raise ValueError("Bone '" + bone_name + "' not found in imported rig '" + armature.name + "'")
                pose_bone.rotation_mode = "XYZ"
                if "rotation" in transform:
                    pose_bone.rotation_euler = vector(transform["rotation"], list(pose_bone.rotation_euler))
                    pose_bone.keyframe_insert(data_path="rotation_euler", frame=frame, group=bone_name)
                if "location" in transform:
                    pose_bone.location = vector(transform["location"], list(pose_bone.location))
                    pose_bone.keyframe_insert(data_path="location", frame=frame, group=bone_name)
                if "scale" in transform:
                    pose_bone.scale = vector(transform["scale"], list(pose_bone.scale))
                    pose_bone.keyframe_insert(data_path="scale", frame=frame, group=bone_name)

    controls = rig_controls or {}
    for armature in armatures:
        if controls:
            apply_rig_controls(armature, controls, fps, total_frames)

    if facial_keyframes:
        shape_key_map = {}
        for mesh in meshes:
            if mesh.data.shape_keys:
                for key in mesh.data.shape_keys.key_blocks:
                    shape_key_map[key.name] = key
        if not shape_key_map:
            raise ValueError("facial_keyframes require imported mesh shape keys (blendshapes)")
        for entry in facial_keyframes:
            frame = max(1, min(total_frames, 1 + round(float(entry["time_seconds"]) * fps)))
            for shape_name, value in entry.get("shapes", {}).items():
                block = shape_key_map.get(shape_name)
                if block is None:
                    raise ValueError("Shape key '" + shape_name + "' not found in imported character")
                block.value = max(0.0, min(1.0, float(value)))
                block.keyframe_insert(data_path="value", frame=frame)



def _rig_bone(armature, bone_name, purpose):
    bone = armature.pose.bones.get(str(bone_name))
    if bone is None:
        raise ValueError(purpose + " bone '" + str(bone_name) + "' not found in rig '" + armature.name + "'")
    return bone


def apply_rig_controls(armature, controls, fps, total_frames):
    """Apply explicitly mapped IK, procedural locomotion and finger-control keys.

    All bone names are rig-specific and must be inspected from the imported asset.
    This deliberately avoids guessing a universal humanoid skeleton naming scheme.
    """
    # Finger controls are explicit authored poses, not an automatic grasp solver.
    finger_keys = controls.get("finger_keyframes", [])
    if finger_keys:
        armature.animation_data_create()
        action = armature.animation_data.action
        if action is None:
            action = bpy.data.actions.new("StoryFingerPose_" + armature.name)
            armature.animation_data.action = action
        for entry in finger_keys:
            frame = max(1, min(total_frames, 1 + round(float(entry["time_seconds"]) * fps)))
            for bone_name, transform in entry.get("bones", {}).items():
                bone = _rig_bone(armature, bone_name, "Finger control")
                bone.rotation_mode = "XYZ"
                if "rotation" in transform:
                    bone.rotation_euler = vector(transform["rotation"], list(bone.rotation_euler))
                    bone.keyframe_insert(data_path="rotation_euler", frame=frame, group=bone_name)
                if "location" in transform:
                    bone.location = vector(transform["location"], list(bone.location))
                    bone.keyframe_insert(data_path="location", frame=frame, group=bone_name)

    # A named IK control constrains a selected end-effector bone to an animated
    # Empty target. Optional pole targets control bend direction.
    for index, spec in enumerate(controls.get("ik", [])):
        bone_name = str(spec["bone"])
        bone = _rig_bone(armature, bone_name, "IK end-effector")
        target = bpy.data.objects.new(str(spec.get("name", "IK_Target_%s" % (index + 1))), None)
        bpy.context.scene.collection.objects.link(target)
        target.empty_display_type = "SPHERE"
        target.empty_display_size = float(spec.get("display_size", 0.12))
        target.location = vector(spec.get("target"), [0, 0, 0])
        constraint = bone.constraints.new("IK")
        constraint.name = str(spec.get("constraint_name", "StoryIK_" + bone_name))
        constraint.target = target
        constraint.chain_count = int(spec.get("chain_count", 2))
        if constraint.chain_count < 1:
            raise ValueError("IK chain_count must be at least 1")
        constraint.use_stretch = bool(spec.get("use_stretch", False))
        constraint.influence = max(0.0, min(1.0, float(spec.get("influence", 1.0))))
        if spec.get("pole_bone"):
            _rig_bone(armature, spec["pole_bone"], "IK pole")
            pole = bpy.data.objects.new(str(spec.get("pole_name", "IK_Pole_%s" % (index + 1))), None)
            bpy.context.scene.collection.objects.link(pole)
            pole.empty_display_type = "CIRCLE"
            pole.location = vector(spec.get("pole_target"), [0, 0, 0])
            constraint.pole_target = pole
            constraint.pole_angle = float(spec.get("pole_angle", 0.0))
        for key in spec.get("keyframes", []):
            frame = max(1, min(total_frames, 1 + round(float(key["time_seconds"]) * fps)))
            if "target" in key:
                target.location = vector(key["target"], list(target.location))
                target.keyframe_insert(data_path="location", frame=frame)
            if "pole_target" in key and constraint.pole_target:
                constraint.pole_target.location = vector(key["pole_target"], list(constraint.pole_target.location))
                constraint.pole_target.keyframe_insert(data_path="location", frame=frame)

    # Optional mapped walk/run cycle. It only animates bones explicitly named by
    # the asset author; no guessed rig names or universal anatomy assumptions.
    locomotion = controls.get("locomotion")
    if locomotion:
        mapping = locomotion.get("bone_map", {})
        if not mapping:
            raise ValueError("locomotion requires bone_map with exact imported bone names")
        for semantic, bone_name in mapping.items():
            _rig_bone(armature, bone_name, "Locomotion " + semantic)
        start = max(1, 1 + round(float(locomotion.get("start_seconds", 0)) * fps))
        end = min(total_frames, 1 + round(float(locomotion.get("end_seconds", (total_frames - 1) / fps)) * fps))
        if end <= start:
            raise ValueError("locomotion end_seconds must be after start_seconds")
        cycles = max(0.1, float(locomotion.get("cycles", 2.0)))
        stride = float(locomotion.get("stride_radians", 0.55))
        knee = float(locomotion.get("knee_radians", 0.65))
        arm_swing = float(locomotion.get("arm_swing_radians", 0.4))
        phase_offset = float(locomotion.get("phase_offset_radians", 0.0))
        amplitude = {
            "left_hip": stride, "right_hip": stride,
            "left_knee": knee, "right_knee": knee,
            "left_shoulder": arm_swing, "right_shoulder": arm_swing,
            "left_elbow": arm_swing * 0.35, "right_elbow": arm_swing * 0.35,
            "left_ankle": stride * 0.25, "right_ankle": stride * 0.25,
        }
        signs = {"left_hip": 1, "right_hip": -1, "left_knee": 1, "right_knee": 1,
                 "left_shoulder": -1, "right_shoulder": 1, "left_elbow": 1, "right_elbow": -1,
                 "left_ankle": -1, "right_ankle": 1}
        for frame in range(start, end + 1):
            phase = ((frame - start) / max(1, end - start)) * (2.0 * math.pi * cycles) + phase_offset
            for semantic, bone_name in mapping.items():
                bone = _rig_bone(armature, bone_name, "Locomotion " + semantic)
                bone.rotation_mode = "XYZ"
                axis = int(locomotion.get("axis", 0))
                if axis not in (0, 1, 2):
                    raise ValueError("locomotion axis must be 0, 1 or 2")
                amp = amplitude.get(semantic, stride)
                angle = math.sin(phase + (math.pi if semantic.startswith("right_") else 0.0)) * amp
                if semantic.endswith("_knee"):
                    angle = max(0.0, angle) * (1 if semantic.startswith("left_") else 1)
                if semantic.endswith("_elbow"):
                    angle = abs(angle)
                rotation = list(bone.rotation_euler)
                rotation[axis] = angle * signs.get(semantic, 1)
                bone.rotation_euler = rotation
                bone.keyframe_insert(data_path="rotation_euler", frame=frame, group=bone_name)
    if armature.animation_data and armature.animation_data.action:
        for fc in armature.animation_data.action.fcurves:
            for point in fc.keyframe_points:
                point.interpolation = "BEZIER"

def apply_viseme_animation(root, viseme_keyframes, viseme_map, fps, total_frames):
    """Map externally aligned viseme events onto imported facial shape keys."""
    if not viseme_keyframes:
        return
    if not isinstance(viseme_map, dict) or not viseme_map:
        raise ValueError("viseme_keyframes require a viseme_map from viseme labels to exact imported shape-key names")
    shape_keys = {}
    stack = list(root.children)
    while stack:
        obj = stack.pop()
        stack.extend(list(obj.children))
        if obj.type == "MESH" and obj.data.shape_keys:
            for key in obj.data.shape_keys.key_blocks:
                shape_keys[key.name] = key
    for label, shape_name in viseme_map.items():
        if shape_name not in shape_keys:
            raise ValueError("Viseme '" + str(label) + "' maps to missing shape key '" + str(shape_name) + "'")
    # Key every mapped shape at every event, so unused mouth poses return to zero.
    for entry in viseme_keyframes:
        frame = max(1, min(total_frames, 1 + round(float(entry["time_seconds"]) * fps)))
        label = str(entry.get("viseme", "REST"))
        strength = max(0.0, min(1.0, float(entry.get("strength", 1.0))))
        active_shape = viseme_map.get(label)
        for mapped_label, shape_name in viseme_map.items():
            block = shape_keys[shape_name]
            block.value = strength if shape_name == active_shape else 0.0
            block.keyframe_insert(data_path="value", frame=frame)
    for shape_name in set(viseme_map.values()):
        block = shape_keys[shape_name]
        if block.id_data.animation_data and block.id_data.animation_data.action:
            for fc in block.id_data.animation_data.action.fcurves:
                for point in fc.keyframe_points:
                    point.interpolation = "LINEAR"


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
    if "BLENDER_EEVEE_NEXT" in available_engines:
        scene.render.engine = "BLENDER_EEVEE_NEXT"
    elif "BLENDER_EEVEE" in available_engines:
        scene.render.engine = "BLENDER_EEVEE"
    else:
        scene.render.engine = "BLENDER_WORKBENCH"
    eevee = getattr(scene, "eevee", None)
    if eevee is not None and hasattr(eevee, "taa_render_samples"):
        eevee.taa_render_samples = max(8, args.samples)
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
        obj = create_mesh(item, cache, base_dir=story_path.parent)
        apply_keyframes(obj, item.get("keyframes", []), args.fps, scene.frame_end)
        apply_rig_animation(
            obj,
            item.get("pose_keyframes", []),
            item.get("facial_keyframes", []),
            args.fps,
            scene.frame_end,
            item.get("rig_controls", {}),
        )
    subject_roots = {}
    subject_rigs = {}
    for item in shot.get("subjects", []):
        subject_name = str(item.get("name", "Subject"))
        if subject_name in subject_roots:
            raise ValueError("Duplicate subject name in shot: " + subject_name)
        root = bpy.data.objects.new(subject_name + "_Root", None)
        scene.collection.objects.link(root)
        if item.get("asset_file"):
            model_root = create_mesh(item, cache, base_dir=story_path.parent)
            model_root.parent = root
        else:
            for part in item.get("parts", []):
                obj = create_mesh(part, cache, base_dir=story_path.parent)
                obj.parent = root
        apply_keyframes(root, item.get("keyframes", []), args.fps, scene.frame_end)
        apply_rig_animation(
            root,
            item.get("pose_keyframes", []),
            item.get("facial_keyframes", []),
            args.fps,
            scene.frame_end,
            item.get("rig_controls", {}),
        )
        apply_viseme_animation(
            root,
            item.get("viseme_keyframes", []),
            item.get("viseme_map", {}),
            args.fps,
            scene.frame_end,
        )
        subject_roots[subject_name] = root
        subject_rigs[subject_name] = find_armature(root)

    for item in shot.get("props", []):
        obj = create_mesh(item, cache, base_dir=story_path.parent)
        attachment = item.get("attach_to")
        if attachment:
            subject_name = str(attachment.get("subject", ""))
            bone_name = str(attachment.get("bone", ""))
            rig = subject_rigs.get(subject_name)
            if rig is None:
                raise ValueError("Prop attachment requires a rigged subject: " + subject_name)
            if rig.data.bones.get(bone_name) is None:
                raise ValueError("Attachment bone '" + bone_name + "' not found on subject " + subject_name)
            obj.parent = rig
            obj.parent_type = "BONE"
            obj.parent_bone = bone_name
            obj.location = vector(attachment.get("offset"), [0, 0, 0])
            obj.rotation_euler = vector(attachment.get("rotation"), [0, 0, 0])
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
