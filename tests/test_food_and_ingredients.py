"""
Unit and Integration Tests for Potaria Culinary and Ingredients System
Validates:
1. Complete registration of all authentic Filipino cuisine, cooked fishes, potato delicacies, and ingredients in ITEM_REGISTRY.
2. Complete recipe catalog and station assignments in RECIPES (Furnace and By-Hand).
3. Asset sprite availability and valid dimensions for all 79 foods and ingredients in assets/items/.
4. Player consumption mechanics and health restoration for all edible culinary items.
5. Furnace cooking and recipe crafting execution.
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pygame
pygame.init()
pygame.display.set_mode((1, 1), pygame.NOFRAME)

from src.assets.asset_factory import AssetFactory
from src.audio.sound_effects import SoundManager
from src.entities.player import Player
from src.ui.inventory import Inventory, ItemStack, ITEM_REGISTRY, CAT_CONSUMABLE
from src.ui.crafting import CraftingSystem, RECIPES


class TestFoodAndIngredients(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.asset_factory = AssetFactory()
        cls.sound_manager = SoundManager()

        cls.filipino_dishes = [
            'chicken_adobo', 'pork_adobo', 'sinigang', 'kare_kare', 'bulalo', 'tinola',
            'lechon', 'pancit_bihon', 'arroz_caldo', 'halo_halo', 'kaldereta', 'balut',
            'itlog_na_maalat', 'sinangag', 'daing_na_bangus', 'sinigang_na_bangus',
            'ginataang_tilapia', 'kinilaw_na_tanigue'
        ]

        cls.cooked_fishes = [
            'cooked_bangus', 'cooked_tilapia', 'cooked_galunggong', 'cooked_maya_maya',
            'cooked_tanigue', 'cooked_tambakol', 'cooked_lapu_lapu', 'cooked_hito',
            'cooked_dilis', 'cooked_dalagang_bukid'
        ]

        cls.potato_delicacies = [
            'mashed_potato', 'golden_fry', 'hearty_root_stew', 'glazed_golden_tuber',
            'smoked_spud_jerky', 'gilded_russet', 'potato_bread', 'sweet_tuber_pie',
            'herbal_salve'
        ]

        cls.raw_fishes = [
            'raw_bangus', 'raw_tilapia', 'raw_galunggong', 'raw_maya_maya', 'raw_tanigue',
            'raw_tambakol', 'raw_lapu_lapu', 'raw_hito', 'raw_dilis', 'raw_dalagang_bukid'
        ]

        cls.raw_meats = [
            'raw_chicken', 'raw_pork', 'pork_belly', 'raw_beef', 'raw_goat_meat',
            'duck_egg', 'carabao_milk'
        ]

        cls.pantry_ingredients = [
            'raw_potato', 'rice', 'garlic', 'onion', 'ginger', 'tamarind', 'eggplant',
            'string_beans', 'black_pepper', 'calamansi', 'soy_sauce', 'vinegar',
            'salt', 'shaved_ice', 'condensed_milk', 'ube_halaya', 'pancit_noodles',
            'peanut_butter', 'coconut_milk', 'spud_sap', 'seaweed', 'snow_block',
            'wood', 'glowing_mushroom', 'gold_bar'
        ]

        cls.all_items = (
            cls.filipino_dishes + cls.cooked_fishes + cls.potato_delicacies +
            cls.raw_fishes + cls.raw_meats + cls.pantry_ingredients
        )

    def test_01_all_foods_and_ingredients_in_registry(self):
        """Verifies every single food dish and ingredient is registered in ITEM_REGISTRY."""
        for item_id in self.all_items:
            self.assertIn(item_id, ITEM_REGISTRY, f"Missing item '{item_id}' from ITEM_REGISTRY")
            data = ITEM_REGISTRY[item_id]
            self.assertTrue(len(data.get("name", "")) > 0, f"Item '{item_id}' has empty name")
            self.assertTrue(len(data.get("desc", "")) > 0, f"Item '{item_id}' has empty description")

    def test_02_all_cooked_items_have_valid_recipes(self):
        """Verifies all cooked dishes and crafted ingredients have registered recipes with valid stations."""
        recipe_map = {r["result"]: r for r in RECIPES}
        cooked_targets = (
            self.filipino_dishes + self.cooked_fishes +
            ['mashed_potato', 'golden_fry', 'hearty_root_stew', 'glazed_golden_tuber',
             'smoked_spud_jerky', 'gilded_russet', 'potato_bread', 'sweet_tuber_pie',
             'salt', 'vinegar', 'shaved_ice', 'condensed_milk', 'ube_halaya',
             'pancit_noodles', 'peanut_butter', 'coconut_milk']
        )
        for item_id in cooked_targets:
            self.assertIn(item_id, recipe_map, f"Missing recipe for craftable item '{item_id}'")
            r = recipe_map[item_id]
            self.assertIn(r.get("station"), ("furnace", None, "work_bench"), f"Invalid station for '{item_id}'")
            self.assertTrue(len(r.get("ingredients", [])) > 0, f"Recipe for '{item_id}' has no ingredients")
            # Verify each ingredient exists in registry
            for ing_id, ing_cnt in r["ingredients"]:
                self.assertIn(ing_id, ITEM_REGISTRY, f"Ingredient '{ing_id}' in recipe '{item_id}' not in registry")
                self.assertGreater(ing_cnt, 0, f"Ingredient count for '{ing_id}' must be > 0")

    def test_03_all_items_have_valid_assets_on_disk(self):
        """Verifies every food item and ingredient has an asset PNG file on disk in assets/craftable_items/ or assets/items/."""
        craft_dir = "assets/craftable_items"
        items_dir = "assets/items"
        self.assertTrue(os.path.isdir(craft_dir))
        self.assertTrue(os.path.isdir(items_dir))
        for item_id in self.all_items:
            craft_path = os.path.join(craft_dir, f"{item_id}.png")
            items_path = os.path.join(items_dir, f"{item_id}.png")
            png_path = craft_path if os.path.exists(craft_path) else items_path
            self.assertTrue(os.path.isfile(png_path), f"Asset file missing on disk: {png_path}")
            surf = pygame.image.load(png_path)
            self.assertGreater(surf.get_width(), 0)
            self.assertGreater(surf.get_height(), 0)
            # Ensure not completely transparent
            has_visible = any(surf.get_at((x, y))[3] > 0 for x in range(surf.get_width()) for y in range(surf.get_height()))
            self.assertTrue(has_visible, f"Asset file for '{item_id}' has no visible pixels")

    def test_04_player_consumption_and_healing(self):
        """Verifies that eating food restores health properly through player.consume_item()."""
        player = Player(100, 100, self.asset_factory, self.sound_manager)
        player.max_health = 500

        edible_dishes = self.filipino_dishes + self.cooked_fishes + [
            'mashed_potato', 'hearty_root_stew', 'glazed_golden_tuber',
            'smoked_spud_jerky', 'potato_bread', 'sweet_tuber_pie',
            'raw_potato', 'raw_bangus', 'raw_chicken', 'duck_egg'
        ]

        for food_id in edible_dishes:
            player.health = 50
            heal_amt = ITEM_REGISTRY[food_id].get("heal", 0)
            success = player.consume_item(food_id)
            self.assertTrue(success, f"consume_item returned False for '{food_id}'")
            self.assertEqual(player.health, 50 + heal_amt, f"HP restoration mismatch for '{food_id}'")

    def test_05_furnace_crafting_execution(self):
        """Verifies crafting a furnace dish consumes raw ingredients and produces cooked output in inventory."""
        inv = Inventory(self.asset_factory)
        engine = CraftingSystem(self.asset_factory, self.sound_manager)

        # Clear inventory
        for i in range(len(inv.slots)):
            inv.slots[i] = None

        # Add ingredients for Sinigang na Baboy: 1x pork_belly, 1x tamarind, 1x onion, 1x eggplant
        inv.add_item("pork_belly", 1)
        inv.add_item("tamarind", 1)
        inv.add_item("onion", 1)
        inv.add_item("eggplant", 1)

        sinigang_recipe = None
        for r in RECIPES:
            if r["result"] == "sinigang":
                sinigang_recipe = r
                break
        self.assertIsNotNone(sinigang_recipe)

        crafted = engine.craft(sinigang_recipe, inv)
        self.assertTrue(crafted, "Furnace crafting for Sinigang na Baboy failed")
        self.assertEqual(inv.count_item("sinigang"), 1)
        self.assertEqual(inv.count_item("pork_belly"), 0)
        self.assertEqual(inv.count_item("tamarind"), 0)


if __name__ == "__main__":
    unittest.main()
