"""Rig-aware Blender action retargeting with explicit skeleton mapping.

Run inside Blender's Python. Source and target must be imported armatures.
This intentionally requires an explicit map; it never guesses bone names.
"""
from mathutils import Quaternion, Vector


def _bone(armature, name):
    bone = armature.pose.bones.get(str(name))
    if bone is None:
        raise ValueError("Bone %r not found in armature %r" % (name, armature.name))
    return bone


def _as_quaternion(value):
    if value is None:
        return Quaternion((1.0, 0.0, 0.0), 0.0)
    if len(value) == 4:
        q = Quaternion(tuple(float(x) for x in value))
    elif len(value) == 3:
        from mathutils import Euler
        q = Euler(tuple(float(x) for x in value), "XYZ").to_quaternion()
    else:
        raise ValueError("rotation_offset must have 3 Euler or 4 quaternion values")
    q.normalize()
    return q


def retarget_action(source_armature, target_armature, source_action, bone_map,
                    frame_start=None, frame_end=None, copy_root_motion=False,
                    root_translation_scale=1.0, action_name="Retargeted_Action"):
    """Bake a source action onto a target rig using explicit bone pairs.

    Each bone_map item: {source, target, rotation_offset?, copy_location?}.
    Rotation offsets are target-rig local correction rotations. Root translation
    is opt-in because source/target rest origins and units often differ.
    """
    if source_armature.type != "ARMATURE" or target_armature.type != "ARMATURE":
        raise TypeError("source_armature and target_armature must be ARMATURE objects")
    if not bone_map:
        raise ValueError("An explicit non-empty bone_map is required")
    if source_action is None:
        raise ValueError("A source animation action is required")

    action_range = source_action.frame_range
    start = int(frame_start if frame_start is not None else action_range[0])
    end = int(frame_end if frame_end is not None else action_range[1])
    if end < start:
        raise ValueError("frame_end must be >= frame_start")

    pairs = []
    seen_targets = set()
    for item in bone_map:
        src_name, dst_name = str(item["source"]), str(item["target"])
        src = _bone(source_armature, src_name)
        dst = _bone(target_armature, dst_name)
        if dst_name in seen_targets:
            raise ValueError("Duplicate target bone mapping: " + dst_name)
        seen_targets.add(dst_name)
        pairs.append((src, dst, _as_quaternion(item.get("rotation_offset")),
                      bool(item.get("copy_location", False))))

    source_armature.animation_data_create()
    source_armature.animation_data.action = source_action
    target_armature.animation_data_create()
    baked = target_armature.animation_data.action
    target_action = source_action.copy()
    target_action.name = action_name
    target_action.fcurves.clear()
    target_armature.animation_data.action = target_action

    scene = __import__("bpy").context.scene
    original_frame = scene.frame_current
    try:
        for frame in range(start, end + 1):
            scene.frame_set(frame)
            for src, dst, offset, copy_location in pairs:
                # Pose-bone quaternion is the local delta from its rest pose.
                delta = src.rotation_quaternion.copy()
                delta.normalize()
                dst.rotation_mode = "QUATERNION"
                dst.rotation_quaternion = offset @ delta
                dst.keyframe_insert(data_path="rotation_quaternion", frame=frame,
                                    group=dst.name)
                if copy_location:
                    dst.location = src.location.copy() * float(root_translation_scale)
                    dst.keyframe_insert(data_path="location", frame=frame,
                                        group=dst.name)
    finally:
        scene.frame_set(original_frame)

    return {"action": target_action.name, "frames": end - start + 1,
            "mapped_bones": len(pairs), "source_action": source_action.name}
