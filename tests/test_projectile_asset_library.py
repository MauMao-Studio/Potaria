import json
import os
import unittest


class TestProjectileAssetLibrary(unittest.TestCase):
    def setUp(self):
        self.root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        self.root_json_path = os.path.join(self.root_dir, "Potaria_Projectile_Asset_Library.json")
        self.docs_json_path = os.path.join(self.root_dir, "docs", "Potaria_Projectile_Asset_Library.json")

    def test_01_files_exist(self):
        self.assertTrue(os.path.exists(self.root_json_path), "Root JSON file must exist")
        self.assertTrue(os.path.exists(self.docs_json_path), "Docs JSON file must exist")

    def test_02_files_content_identical(self):
        with open(self.root_json_path, "r", encoding="utf-8") as f:
            root_content = f.read()
        with open(self.docs_json_path, "r", encoding="utf-8") as f:
            docs_content = f.read()
        self.assertEqual(root_content, docs_content, "Root and docs JSON files must have identical content")

    def test_03_top_level_schema(self):
        with open(self.root_json_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        expected_keys = {
            "schema_version",
            "project",
            "document_type",
            "purpose",
            "shared_asset_guidelines",
            "behavior_types_not_separate_art_by_default",
            "effect_asset_families",
            "projectiles",
            "prompt_template",
            "starter_batch_recommendation",
        }
        self.assertEqual(set(data.keys()), expected_keys)
        self.assertEqual(data["schema_version"], "1.0.0")
        self.assertEqual(data["project"], "Potaria")
        self.assertEqual(data["document_type"], "projectile_asset_library")

    def test_04_shared_asset_guidelines(self):
        with open(self.root_json_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        guidelines = data["shared_asset_guidelines"]
        expected_guidelines_keys = {
            "default_canvas",
            "format",
            "style",
            "camera_and_view",
            "background",
            "lighting",
            "animation_sheets",
            "scaling",
            "readability",
            "cultural_direction",
            "pipeline",
        }
        self.assertEqual(set(guidelines.keys()), expected_guidelines_keys)
        self.assertEqual(guidelines["default_canvas"], "32x32 pixels")
        self.assertIsInstance(guidelines["pipeline"], list)
        self.assertGreater(len(guidelines["pipeline"]), 0)

    def test_05_behavior_types_and_effect_families(self):
        with open(self.root_json_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        behaviors = data["behavior_types_not_separate_art_by_default"]
        self.assertEqual(len(behaviors), 14)
        for b in behaviors:
            self.assertIn("name", b)
            self.assertIn("description", b)
            self.assertTrue(b["name"])
            self.assertTrue(b["description"])

        effects = data["effect_asset_families"]
        self.assertEqual(len(effects), 12)
        expected_fx_ids = [f"FX{i:02d}" for i in range(1, 13)]
        self.assertEqual([e["id"] for e in effects], expected_fx_ids)
        for e in effects:
            self.assertIn("id", e)
            self.assertIn("name", e)
            self.assertIn("description", e)

    def test_06_projectiles_count_and_ids(self):
        with open(self.root_json_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        projectiles = data["projectiles"]
        self.assertEqual(len(projectiles), 40)
        expected_ids = [f"P{i:02d}" for i in range(1, 41)]
        self.assertEqual([p["id"] for p in projectiles], expected_ids)

    def test_07_projectile_records_fields_and_types(self):
        with open(self.root_json_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        required_fields = {
            "id",
            "name",
            "category",
            "visual_description",
            "palette",
            "material_and_surface",
            "flight_animation",
            "trail_effect",
            "impact_effect",
            "suggested_variants",
            "asset_generation_prompt",
            "implementation_note",
        }

        for p in data["projectiles"]:
            self.assertEqual(set(p.keys()), required_fields, f"Projectile {p.get('id')} fields mismatch")
            for field in [
                "id",
                "name",
                "category",
                "visual_description",
                "palette",
                "material_and_surface",
                "flight_animation",
                "trail_effect",
                "impact_effect",
                "asset_generation_prompt",
                "implementation_note",
            ]:
                self.assertIsInstance(p[field], str, f"{field} should be str in {p['id']}")
                self.assertTrue(p[field].strip(), f"{field} should not be empty in {p['id']}")

            self.assertIsInstance(p["suggested_variants"], list, f"suggested_variants should be list in {p['id']}")
            self.assertGreater(len(p["suggested_variants"]), 0, f"suggested_variants empty in {p['id']}")
            for variant in p["suggested_variants"]:
                self.assertIsInstance(variant, str)
                self.assertTrue(variant.strip())

    def test_08_starter_batch_recommendations(self):
        with open(self.root_json_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        starter_batch = data["starter_batch_recommendation"]
        expected = ["P01", "P02", "P06", "P07", "P08", "P10", "P16", "P19", "P23", "P25", "P29", "P32"]
        self.assertEqual(starter_batch, expected)

        all_ids = {p["id"] for p in data["projectiles"]}
        for pid in starter_batch:
            self.assertIn(pid, all_ids)

    def test_09_specific_projectile_content(self):
        with open(self.root_json_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        by_id = {p["id"]: p for p in data["projectiles"]}

        # P01 Iron Arrow
        self.assertEqual(by_id["P01"]["name"], "Iron Arrow")
        self.assertEqual(by_id["P01"]["category"], "physical_ranged")
        self.assertIn("wooden", by_id["P01"]["suggested_variants"])

        # P29 Bolo Throw
        self.assertEqual(by_id["P29"]["name"], "Bolo Throw")
        self.assertEqual(by_id["P29"]["category"], "filipino_physical")
        self.assertIn("ancestral", by_id["P29"]["suggested_variants"])

        # P30 Araw Sigil
        self.assertEqual(by_id["P30"]["name"], "Araw Sigil")
        self.assertEqual(by_id["P30"]["category"], "filipino_magic")

        # P40 Abyssal Seed
        self.assertEqual(by_id["P40"]["name"], "Abyssal Seed")
        self.assertEqual(by_id["P40"]["category"], "boss_magic")
