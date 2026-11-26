"""Story-driven procedural acting clips for the starter humanoid.

These clips animate named body-part objects, not a skeletal rig. They are useful
for blocking and background performers. Close-up/final acting should use a
proper rigged character with authored pose_keyframes or imported actions.
"""
from __future__ import annotations

import math


PARTS = {
    "left_arm": "upper_arm_left",
    "right_arm": "upper_arm_right",
    "left_forearm": "forearm_left",
    "right_forearm": "forearm_right",
    "head": "head",
    "mouth": "mouth",
    "torso": "torso",
}


def _pose(action, side="right", intensity=1.0):
    """Return generic part rotation/scale offsets for a semantic acting beat."""
    side = side if side in {"left", "right"} else "right"
    sign = -1.0 if side == "left" else 1.0
    amount = max(0.0, min(1.5, float(intensity)))
    poses = {
        "wave": {
            f"upper_arm_{side}": (0.0, sign * 1.05 * amount, 0.0),
            f"forearm_{side}": (-0.35 * amount, 0.0, 0.0),
        },
        "point": {
            f"upper_arm_{side}": (0.0, sign * 0.92 * amount, -0.12 * sign),
            f"forearm_{side}": (0.0, 0.0, -0.18 * sign),
        },
        "raise_arms": {
            "upper_arm_left": (0.0, -1.25 * amount, 0.0),
            "upper_arm_right": (0.0, 1.25 * amount, 0.0),
        },
        "cheer": {
            "upper_arm_left": (0.0, -1.35 * amount, 0.0),
            "upper_arm_right": (0.0, 1.35 * amount, 0.0),
            "head": (-0.12 * amount, 0.0, 0.0),
        },
        "look_left": {"head": (0.0, 0.0, 0.38 * amount)},
        "look_right": {"head": (0.0, 0.0, -0.38 * amount)},
        "look_up": {"head": (0.28 * amount, 0.0, 0.0)},
        "look_down": {"head": (-0.28 * amount, 0.0, 0.0)},
        "nod": {"head": (0.22 * amount, 0.0, 0.0)},
        "shake_head": {"head": (0.0, 0.0, 0.24 * amount)},
        "surprised": {
            "head": {"rotation": [-0.12 * amount, 0.0, 0.0]},
            "mouth": {"scale": [1.0, 1.0, 2.4]},
        },
        "sad": {
            "head": (0.22 * amount, 0.0, 0.0),
            "upper_arm_left": (0.12 * amount, 0.0, 0.0),
            "upper_arm_right": (0.12 * amount, 0.0, 0.0),
        },
        "talk": {"mouth": {"scale": [1.0, 1.0, 1.8]}},
        "idle_breath": {"torso": {"scale": [1.015, 1.0, 1.01]}},
    }
    if action not in poses:
        raise ValueError(
            f"Unsupported procedural action '{action}'. Supported: {', '.join(sorted(poses))}"
        )
    return poses[action]


def compile_performance(events, fps, total_frames):
    """Compile semantic beats into per-part keyframes.

    Event format: {time_seconds, action, duration_seconds?, side?, intensity?}.
    Each event returns to neutral at its end, so actions do not permanently
    leave a character in a pose. Overlapping events on the same part are rejected
    instead of silently producing unpredictable keyframe order.
    """
    if not isinstance(events, list):
        raise ValueError("character.performance must be an array")
    tracks = {}
    occupied = {}
    normalized = []
    for index, event in enumerate(events):
        if not isinstance(event, dict):
            raise ValueError(f"performance[{index}] must be an object")
        action = str(event.get("action", "")).strip().lower()
        start = float(event.get("time_seconds", 0))
        duration = float(event.get("duration_seconds", 0.7))
        if start < 0 or duration <= 0 or start + duration > total_frames / fps + 1e-6:
            raise ValueError(f"performance[{index}] time/duration is outside the shot")
        pose = _pose(action, event.get("side", "right"), event.get("intensity", 1.0))
        normalized.append((start, duration, pose, index))
    normalized.sort(key=lambda item: item[0])

    for start, duration, pose, index in normalized:
        peak = start + duration * 0.45
        end = start + duration
        for part, transform in pose.items():
            previous_end = occupied.get(part, -1.0)
            if start < previous_end - 1e-6:
                raise ValueError(
                    f"Overlapping procedural actions affect '{part}' near {start:.3f}s; "
                    "sequence the beats or use a rigged animation track."
                )
            occupied[part] = end
            track = tracks.setdefault(part, [])
            if isinstance(transform, dict):
                channel, value = next(iter(transform.items()))
            else:
                channel, value = "rotation", list(transform)
            neutral = [1.0, 1.0, 1.0] if channel == "scale" else [0.0, 0.0, 0.0]
            track.extend([
                {"time_seconds": round(start, 4), channel: list(neutral)},
                {"time_seconds": round(peak, 4), channel: list(value)},
                {"time_seconds": round(end, 4), channel: list(neutral)},
            ])
    for track in tracks.values():
        track.sort(key=lambda item: item["time_seconds"])
    return tracks
