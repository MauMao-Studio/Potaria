import unittest
import os
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

from src.loot.item_registry import registry, CANONICAL_CATEGORIES
from src.loot.affix_engine import AffixEngine
from src.loot.rarity_engine import RarityEngine
from src.loot.loot_system import LootSystem
from src.ui.inventory import ITEM_REGISTRY
from src.ui.crafting import RECIPES


class TestLootAndAffixPhase1(unittest.TestCase):
    def setUp(self):
        self.loot_system = LootSystem()
        self.affix_engine = self.loot_system.affix_engine
        self.rarity_engine = self.loot_system.rarity_engine

    def test_registry_loaded_all_1461_items(self):
        self.assertGreaterEqual(len(registry.items), 1461)
        self.assertEqual(len(registry.items), len(ITEM_REGISTRY))

    def test_all_craftable_items_registered_and_marked(self):
        for r in RECIPES:
            res_id = r["result"]
            item_def = registry.get(res_id)
            self.assertIsNotNone(item_def, f"Missing craftable item in registry: {res_id}")
            self.assertTrue(item_def.craftable, f"Craftable flag not set on {res_id}")

    def test_canonical_9_categories_enforced(self):
        for item_id, item_def in registry.items.items():
            self.assertIn(
                item_def.category,
                CANONICAL_CATEGORIES,
                f"Item {item_id} has non-canonical category {item_def.category}",
            )

    def test_all_9_canonical_affixes_exist(self):
        expected = {
            "Vampiric",
            "Burning",
            "Frozen",
            "Swift",
            "Heavy",
            "Piercing",
            "Rootbound",
            "Astral",
            "Blighted",
        }
        self.assertTrue(expected.issubset(set(self.affix_engine.affixes.keys())))

    def test_multi_affix_naming_prefixes_and_suffixes(self):
        name1 = self.affix_engine.generate_name("Iron Sword", ["Vampiric", "Swift"])
        self.assertEqual(name1, "Vampiric Swift Iron Sword")
        name2 = self.affix_engine.generate_name("Iron Sword", ["Vampiric", "Swift", "of the Root"])
        self.assertEqual(name2, "Vampiric Swift Iron Sword of the Root")

    def test_deterministic_seeded_rolls(self):
        affixes1 = self.affix_engine.roll_affixes("iron_sword", "rare", 42)
        affixes2 = self.affix_engine.roll_affixes("iron_sword", "rare", 42)
        self.assertEqual(affixes1, affixes2)
        self.assertEqual(len(affixes1), 2)

    def test_rarity_validation_common(self):
        tier = self.rarity_engine.get_tier("common")
        self.assertEqual(tier["affix_count"], 0)
        self.assertEqual(self.affix_engine.roll_affixes("iron_sword", "common", 99), [])

    def test_rarity_validation_legendary(self):
        tier = self.rarity_engine.get_tier("legendary")
        self.assertEqual(tier["affix_count"], 5)

    def test_rarity_validation_ancient(self):
        tier = self.rarity_engine.get_tier("ancient")
        self.assertEqual(tier["affix_count"], 6)

    def test_mutual_exclusion_enforcement(self):
        burning = self.affix_engine.affixes["Burning"]
        self.assertIn("Frozen", burning.get("excludes", []))
        self.assertFalse(
            self.affix_engine.is_affix_compatible("Frozen", "weapon", "Ancient", ["Burning"])
        )
        self.assertFalse(
            self.affix_engine.is_affix_compatible("Heavy", "weapon", "Ancient", ["Swift"])
        )
        self.assertFalse(
            self.affix_engine.is_affix_compatible("Blighted", "weapon", "Ancient", ["Rootbound"])
        )

    def test_category_compatibility_enforcement(self):
        # Vampiric is weapon-only, should not be compatible with armor
        self.assertFalse(
            self.affix_engine.is_affix_compatible("Vampiric", "armor", "Ancient", [])
        )
        # Rootbound is allowed on armor and accessory
        self.assertTrue(
            self.affix_engine.is_affix_compatible("Rootbound", "armor", "Rare", [])
        )

    def test_4_layer_generate_loot_merges_stats_and_preserves_base_id(self):
        loot = self.affix_engine.generate_loot(
            "iron_sword",
            rarity="Epic",
            forced_affixes=["Vampiric", "Swift"],
        )
        self.assertEqual(loot["base_id"], "iron_sword")
        self.assertEqual(loot["id"], "iron_sword")
        self.assertEqual(loot["name"], "Vampiric Swift Iron Broadsword")
        self.assertEqual(loot["rarity"], "Epic")
        self.assertGreater(loot["stats"].get("lifesteal", 0), 0)
        self.assertGreater(loot["stats"].get("atk", 0), ITEM_REGISTRY["iron_sword"]["atk"])

    def test_loot_random_path(self):
        item_id = self.loot_system.roll_random_loot("weapon", 1, 42)
        self.assertIsNotNone(item_id)
        self.assertIn(item_id, ITEM_REGISTRY)

    def test_loot_targeted_boss_path(self):
        item_id = self.loot_system.roll_targeted_loot("lord_malus", 42)
        self.assertIsNotNone(item_id)
        self.assertIn(item_id, ITEM_REGISTRY)
        self.assertIn(item_id, self.loot_system.loot_tables["targeted"]["lord_malus"])

    def test_loot_targeted_biome_path(self):
        item_id = self.loot_system.roll_targeted_loot("desert", 42)
        self.assertIsNotNone(item_id)
        self.assertIn(item_id, ITEM_REGISTRY)
        self.assertIn(item_id, self.loot_system.loot_tables["targeted"]["desert"])

    def test_loot_guaranteed_milestone_path(self):
        item_id = self.loot_system.get_guaranteed_milestone_loot("first_boss", 42)
        self.assertEqual(item_id, "portal_shard")
        self.assertIn(item_id, ITEM_REGISTRY)

    def test_all_loot_table_items_exist_in_item_registry(self):
        for group_key in ("targeted", "milestone"):
            group = self.loot_system.loot_tables.get(group_key, {})
            for k, val in group.items():
                if isinstance(val, list):
                    for iid in val:
                        self.assertIn(iid, ITEM_REGISTRY, f"Missing {iid} in {group_key}.{k}")
                elif isinstance(val, str):
                    self.assertIn(val, ITEM_REGISTRY, f"Missing {val} in {group_key}.{k}")

    def test_docx_generated(self):
        path = os.path.join(BASE_DIR, "Potaria_Items_Catalog.docx")
        self.assertTrue(os.path.exists(path))
        self.assertGreater(os.path.getsize(path), 100000)

    def test_pdf_generated(self):
        path = os.path.join(BASE_DIR, "Potaria_Items_Catalog.pdf")
        self.assertTrue(os.path.exists(path))
        self.assertGreater(os.path.getsize(path), 100000)


if __name__ == "__main__":
    unittest.main()
