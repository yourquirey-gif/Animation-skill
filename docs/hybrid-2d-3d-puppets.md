# Hybrid 2D Characters in 3D Blender Worlds

The runtime supports a hybrid composition: 3D sets, props, lights and cameras with 2D cutout characters built from transparent image layers.

## Character authoring contract

Create one storyboard subject with a `parts` array. Each part is a transparent PNG/WebP sprite plane. The plane is upright by default, keeps its source aspect ratio, and receives its own transform keyframes. Use separate images for torso, head, upper/lower arms, hands, legs, eyes and mouth so the character can act rather than slide as one still image.

```json
{
  "name": "Guddu",
  "keyframes": [
    {"time_seconds": 0.0, "location": [0, 0, 0]},
    {"time_seconds": 2.0, "location": [1.2, 0, 0]}
  ],
  "parts": [
    {
      "name": "Guddu_Body",
      "primitive": "sprite",
      "image_file": "assets/guddu/body.png",
      "location": [0, 0, 1.0],
      "character_height": 2.0
    },
    {
      "name": "Guddu_Head",
      "primitive": "sprite",
      "image_file": "assets/guddu/head.png",
      "location": [0, -0.015, 2.0],
      "character_height": 0.9,
      "keyframes": [
        {"time_seconds": 0.0, "rotation": [1.5708, 0, 0]},
        {"time_seconds": 0.4, "rotation": [1.5708, 0, -0.12]},
        {"time_seconds": 0.8, "rotation": [1.5708, 0, 0.08]}
      ]
    },
    {
      "name": "Guddu_Mouth_A",
      "primitive": "sprite",
      "image_file": "assets/guddu/mouth_A.png",
      "location": [0, -0.04, 1.88],
      "character_height": 0.16
    },
    {
      "name": "Guddu_Mouth_B",
      "primitive": "sprite",
      "image_file": "assets/guddu/mouth_B.png",
      "location": [0, -0.04, 1.88],
      "character_height": 0.16
    }
  ],
  "viseme_map": {
    "A": "Guddu_Mouth_A",
    "B": "Guddu_Mouth_B"
  }
}
```

This is a minimal schema illustration, not a complete character asset pack. Production stories should provide all required cutout parts and enough mouth poses for their dialogue. Rhubarb's A-H cues should map to the corresponding named mouth layers; X/REST hides every mouth layer. Do not invent missing image paths or treat a single full-body still as a fully animated puppet.

## Audio-driven lip-sync

With a voice file and Rhubarb installed (or supplied with `--rhubarb`), run:

```bash
python runtime/render_story.py \
  --storyboard story.json \
  --voice voice.wav \
  --auto-lip-sync \
  --rhubarb /path/to/rhubarb \
  --format shorts \
  --output output.mp4
```

The voice is the master timeline and must match the total storyboard duration. Rhubarb cues are distributed across shots and applied either to exact 3D blendshape names or to exact 2D sprite mouth-part names. The 2D path switches transparent mouth cutouts on the cue frames.

## Validation expectations

- Blender integration test: `tests/blender/test_sprite_character.py`
- Confirm the sprite is upright, alpha is connected, materials are isolated per character, and viseme events switch the correct mouth layers.
- Inspect the rendered frames for perspective, scale, occlusion, shadows and set integration. Passing the integration test does not by itself certify final cinematic quality.
