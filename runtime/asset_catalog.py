#!/usr/bin/env python3
"""Validate and search the reusable 3D asset metadata catalog."""
import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CATALOG = ROOT / "assets" / "catalog.json"


def load_catalog(path=CATALOG):
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    if data.get("schema_version") != 1 or not isinstance(data.get("assets"), list):
        raise ValueError("Asset catalog must have schema_version=1 and an assets array")
    return data


def validate_asset(item, index, root=ROOT):
    required = ("id", "category", "name", "path", "format", "visual_style", "license", "source_url")
    missing = [key for key in required if not str(item.get(key, "")).strip()]
    if missing:
        raise ValueError(f"assets[{index}] missing required fields: {', '.join(missing)}")
    rel = Path(item["path"])
    if rel.is_absolute() or ".." in rel.parts:
        raise ValueError(f"assets[{index}] path must stay inside repository: {rel}")
    path = (root / rel).resolve()
    if root.resolve() not in path.parents:
        raise ValueError(f"assets[{index}] path escapes repository root")
    if not path.is_file():
        raise FileNotFoundError(f"assets[{index}] file does not exist: {rel}")
    if item["format"].lower() not in {"blend", "glb", "gltf", "fbx", "obj", "abc", "png", "jpg", "jpeg", "exr", "hdr", "wav", "mp3", "flac"}:
        raise ValueError(f"assets[{index}] unsupported catalog format: {item['format']}")
    if not isinstance(item.get("tags", []), list):
        raise ValueError(f"assets[{index}].tags must be an array")
    if item.get("category", "").startswith("characters") and item.get("rig") is not None:
        if not isinstance(item["rig"], dict):
            raise ValueError(f"assets[{index}].rig must be an object")
    return path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("validate", "list", "search"))
    parser.add_argument("--query", default="")
    parser.add_argument("--category", default="")
    parser.add_argument("--style", default="")
    parser.add_argument("--catalog", type=Path, default=CATALOG)
    args = parser.parse_args()
    data = load_catalog(args.catalog)
    assets = data["assets"]
    ids = set()
    for index, item in enumerate(assets):
        if item.get("id") in ids:
            raise ValueError("Duplicate asset id: " + str(item.get("id")))
        ids.add(item.get("id"))
        validate_asset(item, index, args.catalog.resolve().parents[1])
    if args.command == "validate":
        print(json.dumps({"status": "PASS", "asset_count": len(assets)}, indent=2))
        return 0
    query = args.query.casefold()
    results = []
    for item in assets:
        if args.category and not item.get("category", "").startswith(args.category):
            continue
        if args.style and item.get("visual_style", "").casefold() != args.style.casefold():
            continue
        haystack = " ".join([item.get("id", ""), item.get("name", ""), item.get("category", ""), *item.get("tags", [])]).casefold()
        if query and query not in haystack:
            continue
        results.append(item)
    print(json.dumps(results, indent=2))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print("Asset catalog error:", exc, file=sys.stderr)
        raise SystemExit(1)
