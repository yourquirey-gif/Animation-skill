import json
import tempfile
import unittest
from pathlib import Path

from runtime.asset_catalog import resolve_asset


class AssetResolverTests(unittest.TestCase):
    def test_resolves_only_existing_catalog_assets(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            asset = root / "assets" / "characters" / "hero.glb"
            asset.parent.mkdir(parents=True)
            asset.write_bytes(b"glTF")
            catalog = root / "assets" / "catalog.json"
            catalog.write_text(json.dumps({
                "schema_version": 1,
                "assets": [{
                    "id": "hero_regular",
                    "category": "characters.humanoid",
                    "name": "Hero Regular",
                    "path": "assets/characters/hero.glb",
                    "format": "glb",
                    "visual_style": "stylized",
                    "license": "CC0-1.0",
                    "source_url": "https://example.invalid/hero",
                    "tags": ["humanoid"],
                    "rig": {"type": "humanoid"}
                }]
            }), encoding="utf-8")
            resolved, metadata = resolve_asset("hero_regular", catalog)
            self.assertEqual(resolved, asset.resolve())
            self.assertEqual(metadata["id"], "hero_regular")

    def test_unknown_asset_id_fails_clearly(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            catalog = root / "assets" / "catalog.json"
            catalog.parent.mkdir(parents=True)
            catalog.write_text(json.dumps({"schema_version": 1, "assets": []}), encoding="utf-8")
            with self.assertRaisesRegex(KeyError, "found 0"):
                resolve_asset("missing_character", catalog)


if __name__ == "__main__":
    unittest.main()
