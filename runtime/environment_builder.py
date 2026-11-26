"""Deterministic, story-specific procedural environment dressing for Blender.

The generator creates a distinct environment kit from a semantic profile and seed.
It deliberately emits ordinary scene specs so the main scene compiler retains
ownership of materials, collections, animation and render lifecycle.
"""
import hashlib
import random


PROFILES = {
    "village": {"ground": (0.34, 0.25, 0.13), "wall": (0.66, 0.48, 0.30), "green": (0.12, 0.34, 0.12), "accent": (0.72, 0.30, 0.10)},
    "urban": {"ground": (0.20, 0.22, 0.25), "wall": (0.48, 0.52, 0.58), "green": (0.08, 0.24, 0.12), "accent": (0.18, 0.38, 0.72)},
    "market": {"ground": (0.30, 0.25, 0.19), "wall": (0.72, 0.48, 0.24), "green": (0.12, 0.30, 0.12), "accent": (0.78, 0.16, 0.10)},
    "forest": {"ground": (0.12, 0.22, 0.10), "wall": (0.20, 0.28, 0.16), "green": (0.07, 0.30, 0.10), "accent": (0.28, 0.42, 0.16)},
    "desert": {"ground": (0.68, 0.43, 0.20), "wall": (0.78, 0.58, 0.32), "green": (0.20, 0.30, 0.10), "accent": (0.78, 0.28, 0.08)},
    "snow": {"ground": (0.72, 0.82, 0.90), "wall": (0.36, 0.48, 0.62), "green": (0.10, 0.22, 0.18), "accent": (0.35, 0.62, 0.82)},
    "coast": {"ground": (0.78, 0.68, 0.48), "wall": (0.86, 0.80, 0.64), "green": (0.08, 0.30, 0.20), "accent": (0.06, 0.42, 0.62)},
    "sci_fi": {"ground": (0.07, 0.09, 0.16), "wall": (0.16, 0.20, 0.32), "green": (0.08, 0.28, 0.25), "accent": (0.10, 0.68, 0.88)},
    "fantasy": {"ground": (0.20, 0.16, 0.28), "wall": (0.38, 0.30, 0.48), "green": (0.12, 0.30, 0.20), "accent": (0.55, 0.28, 0.78)},
    "interior": {"ground": (0.24, 0.20, 0.17), "wall": (0.68, 0.60, 0.48), "green": (0.12, 0.28, 0.12), "accent": (0.65, 0.30, 0.12)},
}


def _mat(color, roughness=0.82):
    return {"color": list(color), "roughness": roughness}


def generate_environment_specs(environment, story_id="story", shot_id="shot"):
    """Return deterministic 3D dressing specs unique to this story/shot."""
    config = environment.get("procedural", {}) or {}
    profile = str(config.get("profile", environment.get("profile", ""))).lower().replace("-", "_").replace(" ", "_")
    if not profile:
        return []
    if profile not in PROFILES:
        raise ValueError("Unknown procedural environment profile %r; choose one of %s" % (profile, sorted(PROFILES)))
    seed_text = "%s|%s|%s|%s" % (story_id, shot_id, profile, config.get("seed", 0))
    seed = int(hashlib.sha256(seed_text.encode("utf-8")).hexdigest()[:8], 16)
    rng = random.Random(seed)
    palette = PROFILES[profile]
    width = max(12.0, min(100.0, float(config.get("width", 34.0))))
    depth = max(12.0, min(100.0, float(config.get("depth", 34.0))))
    count = max(4, min(48, int(config.get("dressing_count", 18))))
    specs = [{
        "name": "Generated_%s_Ground" % profile, "primitive": "cube",
        "location": [0, 0, -0.22], "scale": [width / 2, depth / 2, 0.22],
        "material": _mat(palette["ground"]), "bevel": 0.08,
    }]
    # A recognizable skyline/backdrop silhouette prevents empty voids while
    # keeping the hero action area clear in the center foreground.
    for index in range(8):
        x = -width * 0.46 + index * width * 0.13
        height = rng.uniform(2.8, 8.0)
        if profile in {"forest", "desert", "snow", "fantasy"}:
            primitive = "cone" if profile in {"forest", "snow"} else "ico_sphere"
            scale = [rng.uniform(1.2, 2.8), rng.uniform(1.2, 2.8), height / 2]
            material = _mat(palette["green"] if profile in {"forest", "snow"} else palette["wall"])
        else:
            primitive = "cube"
            scale = [rng.uniform(1.1, 2.4), rng.uniform(1.0, 2.2), height / 2]
            material = _mat(palette["wall"])
        specs.append({
            "name": "Generated_%s_Backdrop_%02d" % (profile, index),
            "primitive": primitive, "location": [x, depth * 0.43, height / 2 - 0.1],
            "scale": scale, "material": material, "bevel": 0.06 if primitive == "cube" else 0,
        })
    # Randomized side dressing: never place large blockers in the central action lane.
    for index in range(count):
        side = -1 if index % 2 == 0 else 1
        x = side * rng.uniform(width * 0.28, width * 0.47)
        y = rng.uniform(-depth * 0.38, depth * 0.35)
        height = rng.uniform(1.0, 4.2)
        if profile in {"forest", "village", "coast"} and index % 3 == 0:
            primitive = "cylinder"
            scale = [0.16, 0.16, height * 0.38]
            material = _mat(palette["wall"])
            specs.append({"name": "Generated_%s_Trunk_%02d" % (profile, index), "primitive": primitive,
                          "location": [x, y, height * 0.38], "scale": scale, "material": material})
            specs.append({"name": "Generated_%s_Canopy_%02d" % (profile, index), "primitive": "ico_sphere",
                          "location": [x, y, height * 0.95], "scale": [height * 0.38] * 3,
                          "material": _mat(palette["green"])})
        elif profile == "desert" and index % 4 == 0:
            specs.append({"name": "Generated_%s_Dune_%02d" % (profile, index), "primitive": "uv_sphere",
                          "location": [x, y, 0.05], "scale": [rng.uniform(1.5, 3.5), 1.6, rng.uniform(0.5, 1.2)],
                          "material": _mat(palette["accent"])})
        elif profile == "interior":
            specs.append({"name": "Generated_%s_Pillar_%02d" % (profile, index), "primitive": "cube",
                          "location": [x, y, height / 2], "scale": [0.22, 0.22, height / 2],
                          "material": _mat(palette["wall"]), "bevel": 0.08})
        else:
            specs.append({"name": "Generated_%s_Dressing_%02d" % (profile, index),
                          "primitive": "cube" if profile in {"urban", "market", "sci_fi"} else "ico_sphere",
                          "location": [x, y, height / 2], "scale": [rng.uniform(0.35, 1.3), rng.uniform(0.35, 1.3), height / 2],
                          "material": _mat(palette["accent"] if index % 4 == 0 else palette["wall"]),
                          "bevel": 0.08})
    # Unique per-story identity is recorded in object names and render report.
    return specs
