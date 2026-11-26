"""Universal JSON-to-Blender scene compiler.

Claude authors story-specific storyboard JSON; this renderer turns each shot's
3D environment, subjects, props, camera and animation into real rendered frames.
No story/genre is hard-coded here. Run inside Blender's bundled Python:
blender --background --python-exit-code 1 --python story_scene.py -- --storyboard ... --shot-index 0 --output-dir ...
"""
import argparse
import json
import math
import os
import sys
import time
from pathlib import Path

# Blender may execute this file without adding its containing folder to sys.path.
# Register the runtime directory so shared helpers (asset_catalog, semantic_actions,
# rig_retarget) resolve consistently in headless cloud rendering.
sys.path.insert(0, str(Path(__file__).resolve().parent))

import bpy
from mathutils import Vector


PRIMITIVES = {"cube", "uv_sphere", "ico_sphere", "cylinder", "cone", "torus", "plane", "terrain", "text"}
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
    parser.add_argument("--progress-file", default=None, help="Write per-frame render progress JSON")
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
                        if label not in viseme_map and label not in {"X", "REST"}:
                            raise ValueError(f"Unknown viseme label '{label}' at shots[{i}].{group}[{j}]")
                        strength = float(event.get("strength", 1.0))
                        if strength < 0 or strength > 1:
                            raise ValueError("Viseme strength must be between 0 and 1")
    return story


def import_fbx_asset(filepath):
    """Import FBX using Blender 5's maintained C++ importer, with legacy fallback."""
    filepath = str(Path(filepath).resolve())
    wm_ops = getattr(bpy.ops, "wm", None)
    if wm_ops is not None and hasattr(wm_ops, "fbx_import"):
        return bpy.ops.wm.fbx_import(filepath=filepath)
    legacy_ops = getattr(bpy.ops, "import_scene", None)
    if legacy_ops is None or not hasattr(legacy_ops, "fbx"):
        raise RuntimeError("This Blender build has no supported FBX importer")
    return bpy.ops.import_scene.fbx(filepath=filepath)


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
            import_fbx_asset(asset_path)
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

        # Optional separate animation asset -> target character retarget.
        # Explicit armature/action names and bone map prevent unsafe guessing.
        retarget = spec.get("retarget")
        if retarget:
            if retarget.get("animation_file"):
                animation_path = Path(retarget["animation_file"])
                if not animation_path.is_absolute():
                    animation_path = (Path(base_dir or Path.cwd()) / animation_path).resolve()
            elif retarget.get("animation_query"):
                animation_root = Path(retarget.get("animation_dir", "runtime-assets/animations"))
                if not animation_root.is_absolute():
                    animation_root = (Path(base_dir or Path.cwd()) / animation_root).resolve()
                query = str(retarget["animation_query"]).casefold().replace("-", "_").replace(" ", "_")
                candidates = sorted(
                    path for path in animation_root.glob("*")
                    if path.is_file() and path.suffix.casefold() in {".fbx", ".glb", ".gltf"}
                    and query in path.stem.casefold().replace("-", "_").replace(" ", "_")
                )
                exact = [path for path in candidates
                         if path.stem.casefold().replace("-", "_").replace(" ", "_") in
                         {query, "kinemiq_" + query, "animation_" + query}]
                if exact:
                    candidates = exact
                if len(candidates) != 1:
                    raise ValueError(
                        "animation_query %r must resolve to exactly one clip in %s; candidates=%s" %
                        (retarget["animation_query"], animation_root,
                         [path.name for path in candidates])
                    )
                animation_path = candidates[0]
                print("RESOLVED_ANIMATION_QUERY", {
                    "query": retarget["animation_query"], "file": str(animation_path)
                }, flush=True)
            else:
                raise ValueError("retarget requires animation_file or animation_query")
            if not animation_path.is_file():
                raise FileNotFoundError("Retarget animation file not found: " + str(animation_path))
            target_armatures = [o for o in imported if o.type == "ARMATURE"]
            if len(target_armatures) != 1:
                raise ValueError("Retarget target model must contain exactly one armature; found %d" % len(target_armatures))
            before_animation = set(bpy.data.objects)
            animation_suffix = animation_path.suffix.lower()
            if animation_suffix in {".glb", ".gltf"}:
                bpy.ops.import_scene.gltf(filepath=str(animation_path))
            elif animation_suffix == ".fbx":
                import_fbx_asset(animation_path)
            else:
                raise ValueError("Retarget animation must be .glb, .gltf or .fbx")
            source_objects = [o for o in bpy.data.objects if o not in before_animation]
            source_armatures = [o for o in source_objects if o.type == "ARMATURE"]
            source_armature_name = retarget.get("source_armature")
            source_armature = next((o for o in source_armatures if o.name == source_armature_name), None) if source_armature_name else (source_armatures[0] if len(source_armatures) == 1 else None)
            if source_armature is None:
                raise ValueError("Set retarget.source_armature to an exact imported source armature name")
            source_action_name = retarget.get("source_action")
            source_action = bpy.data.actions.get(str(source_action_name)) if source_action_name else source_armature.animation_data.action if source_armature.animation_data else None
            if source_action is None:
                # Some FBX exporters store the imported clip as a named action
                # without assigning it to the source armature.
                clip_stem = animation_path.stem.casefold()
                candidates = [action for action in bpy.data.actions
                              if clip_stem in action.name.casefold() or action.name.casefold() in clip_stem]
                if len(candidates) == 1:
                    source_action = candidates[0]
            if source_action is None:
                raise ValueError("No animation action found in imported clip: " + str(animation_path.name))
            bone_map = retarget.get("bone_map", [])
            if not bone_map and retarget.get("auto_map_by_name", True):
                target_names = set(target_armatures[0].data.bones.keys())
                source_names = set(source_armature.data.bones.keys())
                shared_names = sorted(target_names.intersection(source_names))
                if len(shared_names) < int(retarget.get("minimum_shared_bones", 12)):
                    raise ValueError(
                        "Automatic retarget refused: only %d exact bone-name matches between source and target. "
                        "Provide an explicit retarget.bone_map." % len(shared_names)
                    )
                bone_map = [{"source": name, "target": name} for name in shared_names]
                print("AUTO_RETARGET_BONE_MAP", {
                    "source": source_armature.name, "target": target_armatures[0].name,
                    "shared_bones": len(shared_names), "action": source_action.name,
                }, flush=True)
            from rig_retarget import retarget_action
            result = retarget_action(
                source_armature, target_armatures[0], source_action,
                bone_map,
                frame_start=retarget.get("frame_start"),
                frame_end=retarget.get("frame_end"),
                copy_root_motion=bool(retarget.get("copy_root_motion", False)),
                root_translation_scale=float(retarget.get("root_translation_scale", 1.0)),
                action_name=str(retarget.get("action_name", "Story_Retargeted_" + name)),
            )
            print("RETARGET_RESULT", result, flush=True)
            for source_object in source_objects:
                bpy.data.objects.remove(source_object, do_unlink=True)
        return root
    if primitive == "terrain":
        terrain = spec.get("terrain", {})
        sx = max(8, min(128, int(terrain.get("segments_x", 48))))
        sy = max(8, min(128, int(terrain.get("segments_y", 48))))
        width = float(terrain.get("width", 18.0))
        depth = float(terrain.get("depth", 18.0))
        base_height = float(terrain.get("base_height", 0.0))
        peaks = terrain.get("peaks", [
            {"x": -3.0, "y": 1.0, "height": 4.0, "radius_x": 3.0, "radius_y": 4.0},
            {"x": 3.5, "y": 2.0, "height": 5.2, "radius_x": 2.8, "radius_y": 3.5},
        ])
        vertices = []
        for row in range(sy + 1):
            y = (row / sy - 0.5) * depth
            for col in range(sx + 1):
                x = (col / sx - 0.5) * width
                z = base_height
                for peak in peaks:
                    rx = max(0.1, float(peak.get("radius_x", 3.0)))
                    ry = max(0.1, float(peak.get("radius_y", 3.0)))
                    dx = (x - float(peak.get("x", 0.0))) / rx
                    dy = (y - float(peak.get("y", 0.0))) / ry
                    z += float(peak.get("height", 2.0)) * math.exp(-1.25 * (dx * dx + dy * dy))
                ridge = float(terrain.get("ridge_amplitude", 0.18))
                z += ridge * math.sin(x * 1.7 + float(terrain.get("seed", 0))) * math.cos(y * 1.3)
                vertices.append((x, y, z))
        faces = []
        stride = sx + 1
        for row in range(sy):
            for col in range(sx):
                a = row * stride + col
                faces.append((a, a + 1, a + stride + 1, a + stride))
        mesh = bpy.data.meshes.new(name + "_TerrainMesh")
        mesh.from_pydata(vertices, [], faces)
        mesh.update()
        obj = bpy.data.objects.new(name, mesh)
        (collection or bpy.context.scene.collection).objects.link(obj)
        obj.location = location
        obj.rotation_euler = rotation
        obj.scale = scale
        obj.data.materials.append(make_material(spec.get("material"), cache))
        for polygon in obj.data.polygons:
            polygon.use_smooth = True
        if spec.get("subdivision", 0):
            modifier = obj.modifiers.new("Terrain_Smooth", "SUBSURF")
            modifier.levels = max(1, min(2, int(spec["subdivision"])))
        return obj
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
    elif primitive == "text":
        bpy.ops.object.text_add(location=location)
        text_obj = bpy.context.object
        text_obj.data.body = str(spec.get("text", name))
        text_obj.data.align_x = str(spec.get("align_x", "CENTER"))
        text_obj.data.align_y = str(spec.get("align_y", "CENTER"))
        text_obj.data.extrude = float(spec.get("extrude", 0.025))
        text_obj.data.bevel_depth = float(spec.get("bevel_depth", 0.006))
        text_obj.data.bevel_resolution = 2
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



def aim(camera, target):
    camera.rotation_euler = (Vector(target) - camera.location).to_track_quat("-Z", "Y").to_euler()


def build_camera(spec):
    """Create a physically-based camera with optional focus target and animated lens."""
    spec = spec or {}
    bpy.ops.object.camera_add(location=vector(spec.get("location"), [7, -10, 6]))
    camera = bpy.context.object
    camera.name = "Story_Camera"
    camera.data.lens = float(spec.get("lens", 50))
    camera.data.sensor_fit = "AUTO"
    target = vector(spec.get("target"), [0, 0, 1])
    aim(camera, target)
    dof = spec.get("dof", {}) or {}
    if dof.get("enabled", False):
        camera.data.dof.use_dof = True
        camera.data.dof.aperture_fstop = max(0.7, float(dof.get("f_stop", 2.8)))
        camera.data.dof.aperture_blades = max(0, min(16, int(dof.get("blades", 7))))
        if dof.get("focus_distance") is not None:
            camera.data.dof.focus_distance = max(0.01, float(dof["focus_distance"]))
        else:
            focus = bpy.data.objects.new("Camera_Focus_Target", None)
            bpy.context.scene.collection.objects.link(focus)
            focus.empty_display_type = "SPHERE"
            focus.empty_display_size = 0.05
            focus.location = vector(dof.get("focus_target"), target)
            camera.data.dof.focus_object = focus
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



def create_stylized_humanoid(spec, cache, root, fps, total_frames):
    """Build a reusable, detailed stylized humanoid from configurable proportions and colors.

    This is a procedural starter character, not a substitute for a production
    sculpt/rig. Imported rigged assets remain preferred for close-up acting.
    """
    cfg = spec.get("character", {}) or {}
    palette = {
        "skin": cfg.get("skin_color", [0.62, 0.39, 0.25]),
        "clothes": cfg.get("clothing_color", [0.12, 0.24, 0.62]),
        "accent": cfg.get("accent_color", [0.9, 0.55, 0.12]),
        "hair": cfg.get("hair_color", [0.08, 0.045, 0.025]),
        "eyes": cfg.get("eye_color", [0.025, 0.018, 0.012]),
        "shoes": cfg.get("shoe_color", [0.035, 0.04, 0.055]),
    }
    for key, color in palette.items():
        if not isinstance(color, list) or len(color) != 3 or any(float(c) < 0 or float(c) > 1 for c in color):
            raise ValueError("character." + key + " must be an RGB array with values in 0..1")
    scale = float(cfg.get("height", 3.2))
    if not 1.4 <= scale <= 5.0:
        raise ValueError("character.height must be between 1.4 and 5.0")
    ratio = scale / 3.2
    parts = {}

    def part(name, location, dimensions, color, smooth=True):
        obj = create_mesh({
            "name": spec.get("name", "Character") + "_" + name,
            "primitive": "uv_sphere",
            "location": [v * ratio for v in location],
            "scale": [v * ratio for v in dimensions],
            "smooth": smooth,
            "material": {"color": palette[color], "roughness": 0.58},
        }, cache)
        obj.parent = root
        parts[name] = obj
        return obj

    # Main silhouette: torso, pelvis, neck, head and articulated-looking limbs.
    part("pelvis", [0, 0, 1.15], [0.34, 0.24, 0.25], "clothes")
    part("torso", [0, 0, 1.72], [0.48, 0.29, 0.62], "clothes")
    part("shirt_collar", [0, -0.005, 2.25], [0.19, 0.20, 0.12], "accent")
    part("neck", [0, 0, 2.36], [0.15, 0.15, 0.20], "skin")
    part("head", [0, 0, 2.68], [0.34, 0.30, 0.42], "skin")
    part("ear_left", [-0.34, 0, 2.67], [0.075, 0.10, 0.13], "skin")
    part("ear_right", [0.34, 0, 2.67], [0.075, 0.10, 0.13], "skin")
    part("hair_cap", [0, 0.015, 2.98], [0.355, 0.31, 0.19], "hair")
    part("hair_fringe", [0, -0.235, 2.91], [0.28, 0.10, 0.12], "hair")

    # Face faces toward negative Y; layered eyes, brows, nose and mouth improve readability.
    for side, x in (("left", -0.13), ("right", 0.13)):
        part("eye_white_" + side, [x, -0.275, 2.72], [0.075, 0.035, 0.055], "eyes")
        part("eyebrow_" + side, [x, -0.285, 2.82], [0.09, 0.035, 0.025], "hair")
    part("nose", [0, -0.31, 2.64], [0.055, 0.07, 0.09], "skin")
    mouth = part("mouth", [0, -0.286, 2.53], [0.09, 0.025, 0.025], "hair")
    # Procedural face gets real Blender shape keys so Rhubarb cues can animate
    # mouth poses even when a story uses the built-in stylized character.
    basis = mouth.shape_key_add(name="Basis")
    viseme_profiles = {
        "A": (1.00, 1.00, 1.00, 0.00),  # closed lips (M/B/P)
        "B": (1.35, 1.12, 1.00, 0.00),  # wide EE
        "C": (1.18, 1.42, 1.00, 0.00),  # EH
        "D": (1.00, 2.10, 1.00, 0.00),  # open AH
        "E": (0.72, 1.72, 1.00, 0.00),  # rounded OH
        "F": (0.62, 1.18, 1.00, 0.02),  # tight OO
        "G": (1.20, 1.00, 0.70, 0.025), # teeth/lip contact F/V
        "H": (1.08, 1.20, 1.00, 0.00),  # tongue/alveolar L approximation
        "X": (1.00, 1.00, 1.00, 0.00),  # rest
    }
    for label, (width, height, depth, forward) in viseme_profiles.items():
        key = mouth.shape_key_add(name="viseme_" + label)
        for index, vertex in enumerate(basis.data):
            co = vertex.co
            key.data[index].co = (co.x * width, co.y * depth - forward, co.z * height)

    # Upper arms, forearms, hands, thighs, shins and shoes are separate objects
    # so authored motion keys can animate them independently.
    part("upper_arm_left", [-0.55, 0, 1.92], [0.16, 0.17, 0.34], "clothes")
    part("upper_arm_right", [0.55, 0, 1.92], [0.16, 0.17, 0.34], "clothes")
    part("forearm_left", [-0.62, -0.01, 1.48], [0.13, 0.14, 0.31], "skin")
    part("forearm_right", [0.62, -0.01, 1.48], [0.13, 0.14, 0.31], "skin")
    part("hand_left", [-0.64, -0.035, 1.14], [0.13, 0.11, 0.15], "skin")
    part("hand_right", [0.64, -0.035, 1.14], [0.13, 0.11, 0.15], "skin")
    part("thigh_left", [-0.20, 0, 0.82], [0.19, 0.21, 0.42], "clothes")
    part("thigh_right", [0.20, 0, 0.82], [0.19, 0.21, 0.42], "clothes")
    part("shin_left", [-0.20, 0, 0.36], [0.14, 0.16, 0.34], "skin")
    part("shin_right", [0.20, 0, 0.36], [0.14, 0.16, 0.34], "skin")
    part("shoe_left", [-0.20, -0.10, 0.12], [0.18, 0.29, 0.12], "shoes")
    part("shoe_right", [0.20, -0.10, 0.12], [0.18, 0.29, 0.12], "shoes")

    # Optional accessories can be enabled per story without changing the generator.
    if cfg.get("cape"):
        part("cape", [0, 0.27, 1.72], [0.43, 0.10, 0.72], "accent")
    if cfg.get("hat"):
        part("hat_brim", [0, 0, 3.02], [0.42, 0.34, 0.055], "accent")
        part("hat_crown", [0, 0, 3.16], [0.25, 0.24, 0.17], "accent")

    # Explicit part tracks remain available for carefully authored blocking.
    authored_tracks = cfg.get("part_keyframes", {}) or {}
    for name, keys in authored_tracks.items():
        if name not in parts:
            raise ValueError("Unknown procedural character part_keyframes target: " + str(name))
        apply_keyframes(parts[name], keys, fps, total_frames)

    # Story-authored semantic performance beats (wave, point, nod, etc.) are
    # compiled into per-part keyframes. This is a reusable blocking layer, not
    # a substitute for a facially-rigged production character.
    if cfg.get("performance"):
        from semantic_actions import compile_performance
        generated_tracks = compile_performance(cfg["performance"], fps, total_frames)
        for name, keys in generated_tracks.items():
            if name not in parts:
                raise ValueError("Semantic action targets unavailable character part: " + name)
            if name in authored_tracks:
                raise ValueError(
                    "Do not mix performance and part_keyframes for the same part ('" + name +
                    "'); use one authored track to avoid conflicting poses."
                )
            apply_keyframes(parts[name], keys, fps, total_frames)

    # Lightweight looping walk-cycle motion is a preview-level procedural gait.
    motion = str(cfg.get("motion", "idle")).lower()
    if motion not in {"idle", "walk", "run"}:
        raise ValueError("character.motion must be idle, walk or run")
    if motion in {"walk", "run"}:
        cycles = float(cfg.get("motion_cycles", 2.0 if motion == "walk" else 3.0))
        amplitude = 0.42 if motion == "walk" else 0.68
        for frame in range(1, total_frames + 1):
            phase = 2.0 * math.pi * cycles * (frame - 1) / max(1, total_frames - 1)
            for name, sign in (("thigh_left", 1), ("thigh_right", -1),
                               ("upper_arm_left", -1), ("upper_arm_right", 1)):
                obj = parts[name]
                obj.rotation_euler.x = math.sin(phase) * amplitude * sign
                obj.keyframe_insert(data_path="rotation_euler", frame=frame)
    return parts



def merge_static_environment_meshes(objects):
    """Join unanimated primitive environment meshes to reduce per-frame draw overhead.

    Only static, unparented mesh objects are passed here. Joining preserves their
    world-space transforms and material slots; animated subjects and imported rigs
    are deliberately kept separate.
    """
    meshes = [obj for obj in objects if obj and obj.type == "MESH" and obj.parent is None]
    if len(meshes) < 2:
        return len(meshes), 1 if meshes else 0
    bpy.ops.object.select_all(action="DESELECT")
    for obj in meshes:
        obj.select_set(True)
    bpy.context.view_layer.objects.active = meshes[0]
    bpy.ops.object.join()
    merged = bpy.context.view_layer.objects.active
    merged.name = "Environment_Static_Merged"
    merged.data.name = "Environment_Static_Merged_Mesh"
    return len(meshes), 1


def resolve_story_assets(story):
    """Resolve catalog IDs to real files before Blender imports any models."""
    from asset_catalog import resolve_asset
    for shot_index, shot in enumerate(story["shots"]):
        entries = list(shot.get("subjects", [])) + list(shot.get("props", []))
        entries += list(shot.get("environment", {}).get("objects", []))
        for entry in entries:
            asset_id = entry.get("asset_id")
            if asset_id:
                if entry.get("asset_file"):
                    raise ValueError("Use either asset_id or asset_file, not both: " + str(entry.get("name", asset_id)))
                resolved, metadata = resolve_asset(str(asset_id))
                entry["asset_file"] = str(resolved)
                entry["_resolved_asset_metadata"] = {
                    "id": metadata["id"], "name": metadata["name"],
                    "license": metadata["license"], "source_url": metadata["source_url"]
                }
            retarget = entry.get("retarget", {})
            animation_asset_id = retarget.get("animation_asset_id")
            if animation_asset_id:
                if retarget.get("animation_file"):
                    raise ValueError("Use either retarget.animation_asset_id or animation_file")
                resolved, _ = resolve_asset(str(animation_asset_id))
                retarget["animation_file"] = str(resolved)


def main():
    args = parse_args()
    story_path = Path(args.storyboard).resolve()
    story = validate(json.loads(story_path.read_text(encoding="utf-8")))
    resolve_story_assets(story)
    if args.shot_index < 0 or args.shot_index >= len(story["shots"]):
        raise ValueError("shot-index is outside storyboard shots array")
    shot = story["shots"][args.shot_index]
    out = Path(args.output_dir)
    out.mkdir(parents=True, exist_ok=True)
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    available_engines = scene.render.bl_rna.properties["engine"].enum_items.keys()
    requested_engine = os.environ.get("ANIMATION_RENDER_ENGINE")
    if requested_engine:
        if requested_engine not in available_engines:
            raise RuntimeError(
                "Requested Blender render engine '" + requested_engine +
                "' is not available in this Blender build. Available engines: " +
                ", ".join(available_engines)
            )
        scene.render.engine = requested_engine
    elif "BLENDER_EEVEE_NEXT" in available_engines:
        scene.render.engine = "BLENDER_EEVEE_NEXT"
    elif "BLENDER_EEVEE" in available_engines:
        scene.render.engine = "BLENDER_EEVEE"
    else:
        raise RuntimeError("No supported Eevee render engine is available; refusing silent Workbench downgrade.")
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
    world_color = tuple(shot.get("environment", {}).get("world_color", [0.025, 0.03, 0.05]))
    scene.world.color = world_color
    scene.world.use_nodes = True
    background = scene.world.node_tree.nodes.get("Background") if scene.world.node_tree else None
    if background:
        background.inputs["Color"].default_value = (*world_color, 1.0)
        background.inputs["Strength"].default_value = float(shot.get("environment", {}).get("world_strength", 0.35))
    # Consistent cinematic color pipeline; optional shot-level exposure/look overrides.
    scene.view_settings.view_transform = "AgX"
    available_looks = {item.name for item in scene.view_settings.bl_rna.properties["look"].enum_items}
    requested_look = shot.get("color_management", {}).get("look", "AgX - Medium High Contrast")
    if requested_look in available_looks:
        scene.view_settings.look = requested_look
    scene.view_settings.exposure = float(shot.get("color_management", {}).get("exposure", 0.0))
    scene.view_settings.gamma = float(shot.get("color_management", {}).get("gamma", 1.0))
    cache = {}

    env = shot.get("environment", {})
    static_environment_meshes = []
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
        is_static_primitive = (
            not item.get("asset_file")
            and not item.get("keyframes")
            and not item.get("pose_keyframes")
            and not item.get("facial_keyframes")
            and not item.get("rig_controls")
            and obj.type == "MESH"
            and obj.parent is None
        )
        if is_static_primitive:
            static_environment_meshes.append(obj)
    static_mesh_count, merged_mesh_count = merge_static_environment_meshes(static_environment_meshes)
    print("STATIC_ENVIRONMENT_MESH_OPTIMIZATION", {
        "source_meshes": static_mesh_count,
        "merged_meshes": merged_mesh_count,
    }, flush=True)
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
        elif (item.get("character") or {}).get("type") == "stylized_humanoid":
            create_stylized_humanoid(item, cache, root, args.fps, scene.frame_end)
        else:
            for part in item.get("parts", []):
                obj = create_mesh(part, cache, base_dir=story_path.parent)
                obj.parent = root
                apply_keyframes(obj, part.get("keyframes", []), args.fps, scene.frame_end)
        apply_keyframes(root, item.get("keyframes", []), args.fps, scene.frame_end)
        apply_rig_animation(
            root,
            item.get("pose_keyframes", []),
            item.get("facial_keyframes", []),
            args.fps,
            scene.frame_end,
            item.get("rig_controls", {}),
        )
        viseme_map = item.get("viseme_map", {})
        if not viseme_map and (item.get("character") or {}).get("auto_visemes"):
            viseme_map = {label: "viseme_" + label for label in "ABCDEFGHX"}
        apply_viseme_animation(
            root,
            item.get("viseme_keyframes", []),
            viseme_map,
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
    # Render as one animation job so Blender can retain scene/render data
    # between frames. This is still a genuine per-frame 3D render, not a still pan.
    if hasattr(scene.render, "use_persistent_data"):
        scene.render.use_persistent_data = True
    scene.render.image_settings.file_format = "PNG"
    scene.render.filepath = str(out / "frame_")
    render_started = time.perf_counter()
    total_frames = max(1, scene.frame_end - scene.frame_start + 1)
    progress_path = Path(args.progress_file).resolve() if args.progress_file else None

    def report_frame_progress(render_scene, *unused):
        current_frame = min(scene.frame_end, max(scene.frame_start, render_scene.frame_current))
        completed_frames = max(0, current_frame - scene.frame_start + 1)
        elapsed = time.perf_counter() - render_started
        average_per_frame = elapsed / max(1, completed_frames)
        remaining = max(0, total_frames - completed_frames) * average_per_frame
        payload = {
            "status": "RENDERING",
            "completed_frames": completed_frames,
            "total_frames": total_frames,
            "current_frame": current_frame,
            "percent": round(100.0 * completed_frames / total_frames, 1),
            "elapsed_seconds": round(elapsed, 1),
            "eta_seconds": round(remaining, 1),
            "rendered_frames_per_second": round(completed_frames / max(elapsed, 0.001), 3),
        }
        if progress_path:
            try:
                progress_path.parent.mkdir(parents=True, exist_ok=True)
                temporary = progress_path.with_suffix(progress_path.suffix + ".tmp")
                temporary.write_text(json.dumps(payload), encoding="utf-8")
                temporary.replace(progress_path)
            except Exception as exc:
                print("FRAME_PROGRESS_FILE_WARNING", str(exc), flush=True)
        print("FRAME_PROGRESS " + json.dumps(payload), flush=True)

    print("FRAME_PROGRESS " + json.dumps({
        "status": "RENDERING", "completed_frames": 0, "total_frames": total_frames,
        "current_frame": scene.frame_start, "percent": 0.0,
        "elapsed_seconds": 0.0, "eta_seconds": None
    }), flush=True)
    render_handler = report_frame_progress
    bpy.app.handlers.render_write.append(render_handler)
    try:
        bpy.ops.render.render(animation=True)
    finally:
        if render_handler in bpy.app.handlers.render_write:
            bpy.app.handlers.render_write.remove(render_handler)
    render_elapsed = time.perf_counter() - render_started

    report = {
        "status": "RENDERED",
        "shot_id": shot.get("id", str(args.shot_index + 1)),
        "frames": scene.frame_end,
        "fps": args.fps,
        "render_seconds": round(render_elapsed, 3),
        "rendered_frames_per_second": round(scene.frame_end / max(render_elapsed, 0.001), 3),
        "static_environment_source_meshes": static_mesh_count,
        "static_environment_merged_meshes": merged_mesh_count,
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