# Rig Controls Quick Reference

A storyboard subject may contain `rig_controls`:
- `ik`: Blender IK constraints on exact end-effector bones, with world-space target and optional pole target/keyframes.
- `locomotion`: mapped walk/run-style cyclic motion. Supply an explicit semantic `bone_map`; never assume rig bone names.
- `finger_keyframes`: keyframe exact finger/control bones. Attach held props to the actual hand bone with `props[].attach_to`.

IK requires a suitable armature chain and pole setup. Locomotion does not automatically solve root travel, terrain adaptation or planted-foot contacts. Finger poses are rig-specific and are not a physical grasp solver. Always inspect hand/prop contact, deformation and foot sliding.

## Audio mouth cues

Install Rhubarb Lip Sync CLI, then run:

```bash
python runtime/align_visemes.py --audio voice.wav --dialogue transcript.txt --output visemes.json
```

Copy the generated events to the speaking subject's `viseme_keyframes`; map Rhubarb A-F/X labels to exact facial shape keys in `viseme_map`. These are estimated mouth-shape cues, not phoneme-perfect alignment or emotion-aware facial acting. Inspect close-up renders against the original voice.
