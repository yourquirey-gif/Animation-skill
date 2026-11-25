import json
import tempfile
import unittest
from pathlib import Path

from runtime.asset_catalog import load_catalog, validate_asset


class AssetCatalogTests(unittest.TestCase):
    def test_empty_catalog_is_valid(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            catalog = root / "assets" / "catalog.json"
            catalog.parent.mkdir()
            catalog.write_text(json.dumps({"schema_version": 1, "assets": []}), encoding="utf-8")
            self.assertEqual(load_catalog(catalog)["assets"], [])

    def test_registered_asset_must_exist(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "assets").mkdir()
            catalog_asset = {
                "id": "hero.stylized",
                "category": "characters/stylized",
                "name": "Hero",
                "path": "assets/characters/stylized/hero.glb",
                "format": "glb",
                "visual_style": "stylized",
                "license": "CC0-1.0",
                "source_url": "https://example.invalid/source",
                "tags": ["hero", "humanoid"],
                "rig": {"skeleton": "humanoid"},
                "animation_compatibility": ["idle", "walk"]
            }
            with self.assertRaises(FileNotFoundError):
                validate_asset(catalog_asset, 0, root)

    def test_asset_path_cannot_escape_repository(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            outside = root.parent / "outside.glb"
            outside.write_bytes(b"not a model")
            catalog_asset = {
                "id": "bad.asset",
                "category": "props",
                "name": "Bad",
                "path": "../outside.glb",
                "format": "glb",
                "visual_style": "neutral",
                "license": "unknown",
                "source_url": "unknown"
            }
            with self.assertRaises(ValueError):
                validate_asset(catalog_asset, 0, root)


if __name__ == "__main__":
    unittest.main()
