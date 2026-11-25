"""Blender integration test for explicit rig action retargeting."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "runtime"))
import bpy
from rig_retarget import retarget_action


def make_rig(name, bone_names):
    data = bpy.data.armatures.new(name + "_Data")
    obj = bpy.data.objects.new(name, data)
    bpy.context.scene.collection.objects.link(obj)
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    bpy.ops.object.mode_set(mode="EDIT")
    previous = None
    for bone_name in bone_names:
        bone = data.edit_bones.new(bone_name)
        bone.head = (0, 0, 0 if previous is None else 1)
        bone.tail = (0, 0, 1 if previous is None else 2)
        if previous:
            bone.parent = previous
        previous = bone
    bpy.ops.object.mode_set(mode="OBJECT")
    obj.select_set(False)
    return obj


def main():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    source = make_rig("SourceRig", ["root", "hips", "head"])
    target = make_rig("TargetRig", ["Root", "Pelvis", "Head"])
    source.animation_data_create()
    action = bpy.data.actions.new("Walk_Test")
    source.animation_data.action = action
    bone = source.pose.bones["hips"]
    bone.rotation_mode = "QUATERNION"
    bone.rotation_quaternion = (1, 0, 0, 0)
    bone.keyframe_insert(data_path="rotation_quaternion", frame=1, group="hips")
    bone.rotation_quaternion = (0.9238795, 0.3826834, 0, 0)
    bone.keyframe_insert(data_path="rotation_quaternion", frame=9, group="hips")
    result = retarget_action(source, target, action, [
        {"source": "root", "target": "Root"},
        {"source": "hips", "target": "Pelvis"},
        {"source": "head", "target": "Head"},
    ], frame_start=1, frame_end=9)
    assert result["frames"] == 9 and result["mapped_bones"] == 3
    assert target.animation_data.action is not None
    assert len(target.animation_data.action.fcurves) >= 4
    print("RIG_RETARGET_TEST_PASS", result)


if __name__ == "__main__":
    main()
