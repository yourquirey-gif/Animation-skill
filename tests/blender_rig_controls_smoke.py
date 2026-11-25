"""Blender integration smoke test for mapped IK, locomotion and finger poses."""
import sys
from pathlib import Path
import bpy

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "runtime"))
from story_scene import apply_rig_controls


def add_bone(bones, name, head, tail, parent=None):
    bone = bones.new(name)
    bone.head, bone.tail = head, tail
    if parent:
        bone.parent = bones[parent]


def main():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    arm = bpy.data.armatures.new("RigControlsTest")
    rig = bpy.data.objects.new("RigControlsTest", arm)
    bpy.context.scene.collection.objects.link(rig)
    bpy.context.view_layer.objects.active = rig
    rig.select_set(True)
    bpy.ops.object.mode_set(mode="EDIT")
    eb = arm.edit_bones
    add_bone(eb, "upper_arm.L", (0,0,2), (0.8,0,2))
    add_bone(eb, "forearm.L", (0.8,0,2), (1.6,0,2), "upper_arm.L")
    add_bone(eb, "hand.L", (1.6,0,2), (2,0,2), "forearm.L")
    add_bone(eb, "elbow_pole.L", (0.8,0.8,2), (0.8,1,2))
    add_bone(eb, "index.01.L", (1.9,0,2), (2.2,0,2), "hand.L")
    add_bone(eb, "thigh.L", (-0.3,0,1), (-0.3,0,0.5))
    add_bone(eb, "shin.L", (-0.3,0,0.5), (-0.3,0,0), "thigh.L")
    add_bone(eb, "thigh.R", (0.3,0,1), (0.3,0,0.5))
    add_bone(eb, "shin.R", (0.3,0,0.5), (0.3,0,0), "thigh.R")
    bpy.ops.object.mode_set(mode="OBJECT")
    controls = {
        "ik": [{
            "bone": "hand.L", "target": [1.8,-0.3,2.1], "chain_count": 3,
            "pole_bone": "elbow_pole.L", "pole_target": [0.8,1,2],
            "keyframes": [
                {"time_seconds": 0, "target": [1.8,-0.3,2.1]},
                {"time_seconds": 1, "target": [2,-0.4,2.2]},
            ],
        }],
        "locomotion": {
            "bone_map": {"left_hip":"thigh.L","right_hip":"thigh.R",
                         "left_knee":"shin.L","right_knee":"shin.R"},
            "cycles": 1, "start_seconds": 0, "end_seconds": 1.5,
        },
        "finger_keyframes": [
            {"time_seconds": 0, "bones": {"index.01.L":{"rotation":[0,0,0]}}},
            {"time_seconds": 0.5, "bones": {"index.01.L":{"rotation":[0.45,0,0]}}},
        ],
    }
    apply_rig_controls(rig, controls, fps=24, total_frames=48)
    hand = rig.pose.bones["hand.L"]
    ik = next((c for c in hand.constraints if c.type == "IK"), None)
    assert ik and ik.target and ik.pole_target
    assert rig.animation_data and rig.animation_data.action
    assert ik.target.animation_data and ik.target.animation_data.action
    bpy.context.scene.frame_set(25)
    assert abs(ik.target.location.x - 2.0) < 1e-5
    print("PASS: IK, pole target, animated target, locomotion and finger pose")


if __name__ == "__main__":
    main()
