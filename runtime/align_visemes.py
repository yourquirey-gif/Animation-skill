#!/usr/bin/env python3
"""Create Blender-ready mouth-shape events from audio with Rhubarb Lip Sync."""
import argparse
import json
import shutil
import subprocess
from pathlib import Path


def cues_to_keyframes(payload):
    cues = payload.get("mouthCues")
    if not isinstance(cues, list):
        raise ValueError("Rhubarb JSON must contain a mouthCues array")
    events, previous = [], None
    for cue in cues:
        start, end = float(cue["start"]), float(cue["end"])
        label = str(cue["value"]).upper()
        if start < 0 or end < start or label not in set("ABCDEFGHX"):
            raise ValueError("Invalid Rhubarb cue: " + repr(cue))
        if previous is not None and start < previous:
            raise ValueError("Rhubarb cues must be ordered and non-overlapping")
        events.append({"time_seconds": start, "viseme": label, "strength": 1.0})
        # Explicit neutral event at every cue end prevents the previous mouth
        # pose from being held through silence or the next phoneme.
        events.append({"time_seconds": end, "viseme": "X", "strength": 1.0})
        previous = end
    events.sort(key=lambda item: item["time_seconds"])
    return events


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--audio", required=True, type=Path)
    p.add_argument("--output", required=True, type=Path)
    p.add_argument("--dialogue", type=Path)
    p.add_argument("--rhubarb", default=None)
    a = p.parse_args()
    if not a.audio.is_file():
        raise FileNotFoundError(a.audio)
    if a.dialogue and not a.dialogue.is_file():
        raise FileNotFoundError(a.dialogue)
    exe = a.rhubarb or shutil.which("rhubarb")
    if not exe:
        raise RuntimeError("Rhubarb Lip Sync CLI not found; install it or pass --rhubarb.")
    a.output.parent.mkdir(parents=True, exist_ok=True)
    raw = a.output.with_suffix(".rhubarb.json")
    cmd = [exe, "-f", "json", "-o", str(raw)]
    if a.dialogue:
        cmd += ["-d", str(a.dialogue)]
    cmd.append(str(a.audio))
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode:
        raise RuntimeError("Rhubarb failed: " + (result.stderr or result.stdout)[-4000:])
    data = json.loads(raw.read_text(encoding="utf-8"))
    output = {
        "source": "Rhubarb Lip Sync",
        "cue_type": "mouth-shape approximation; not phoneme-perfect alignment",
        "audio_file": str(a.audio.resolve()),
        "viseme_keyframes": cues_to_keyframes(data),
        "rhubarb_raw_json": str(raw.resolve()),
    }
    a.output.write_text(json.dumps(output, indent=2), encoding="utf-8")
    print(json.dumps({"status": "ALIGNED", "output": str(a.output.resolve()),
                      "events": len(output["viseme_keyframes"]),
                      "note": output["cue_type"]}, indent=2))


if __name__ == "__main__":
    main()
