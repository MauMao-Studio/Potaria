"""
Potaria - Minecraft-Style Crafting Categories & 50+ New Craftable Items Test Suite
Verifies:
  1. Crafting Category tabs ([ALL], [BUILDING], [EQUIPMENT], [SURVIVAL], [FURNITURE]).
  2. Tab clicking, filtering, and scroll mechanics.
  3. 50+ Minecraft-inspired items with original Potaria names, stats, lore, and recipes.
  4. ITEM_REGISTRY and ARMOR_DATA registration.
  5. Crafting ingredient deduction and station requirements (Hand, Workbench, Furnace).
  6. Consumable food/potion consumption.
  7. Procedural sprite generation for all new items without missing textures.
Developer: Kurados | Pure Python 3.13 & pygame-ce
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Headless pygame setup
os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"
import pygame
pygame.init()

from src.constants import (
    SCALED_TILE, TILE_WORK_BENCH, TILE_FURNACE,
    CRAFT_CAT_ALL, CRAFT_CAT_BUILDING, CRAFT_CAT_EQUIPMENT,
    CRAFT_CAT_SURVIVAL, CRAFT_CAT_FURNITURE,
    CAT_BLOCK, CAT_WALL, CAT_TOOL, CAT_WEAPON, CAT_ACCESSORY, CAT_CONSUMABLE, CAT_MATERIAL
)
from src.assets.asset_factory import AssetFactory
from src.ui.inventory import Inventory, ItemStack, ITEM_REGISTRY
from src.ui.crafting import CraftingSystem, RECIPES, CRAFT_TABS
from src.rpg.equipment import ARMOR_DATA
from src.world.world import World
from src.entities.player import Player


class DummySound:
    def __init__(self):
        self.played = []

    def play(self, sound_name):
        self.played.append(sound_name)


class TestCraftingCategoriesAndItems(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.factory = AssetFactory()
        cls.sound = DummySound()

    def setUp(self):
        self.sound.played.clear()
        self.crafting = CraftingSystem(self.factory, self.sound)
        self.inv = Inventory(self.factory)
        self.inv.slots = [None] * len(self.inv.slots)
        self.world = World(self.factory, seed=12345)
        self.player = Player(100, 100, self.factory, self.sound)
        self.font = pygame.font.SysFont("Arial", 12)

    # -------------------------------------------------------------------------
    # 1. Category Tabs & Constants Verification
    # -------------------------------------------------------------------------
    def test_category_constants_and_tabs(self):
        """Verifies category tab constants and structure."""
        self.assertEqual(CRAFT_CAT_ALL, "all")
        self.assertEqual(CRAFT_CAT_BUILDING, "building")
        self.assertEqual(CRAFT_CAT_EQUIPMENT, "equipment")
        self.assertEqual(CRAFT_CAT_SURVIVAL, "survival")
        self.assertEqual(CRAFT_CAT_FURNITURE, "furniture")

        tab_ids = [t["id"] for t in CRAFT_TABS]
        self.assertEqual(tab_ids, [
            CRAFT_CAT_ALL,
            CRAFT_CAT_BUILDING,
            CRAFT_CAT_EQUIPMENT,
            CRAFT_CAT_SURVIVAL,
            CRAFT_CAT_FURNITURE
        ])

        for tab in CRAFT_TABS:
            self.assertIn("id", tab)
            self.assertIn("label", tab)
            self.assertIn("full_name", tab)
            self.assertIn("tooltip", tab)

    # -------------------------------------------------------------------------
    # 2. Recipe Categorization & Item Registration
    # -------------------------------------------------------------------------
    def test_all_recipes_have_valid_categories(self):
        """Verifies that every single recipe has a valid category assigned."""
        valid_cats = {CRAFT_CAT_BUILDING, CRAFT_CAT_EQUIPMENT, CRAFT_CAT_SURVIVAL, CRAFT_CAT_FURNITURE}
        self.assertGreaterEqual(len(RECIPES), 110, "Total recipes must be >= 110 after expansion")

        for r in RECIPES:
            res = r["result"]
            cat = r.get("category")
            self.assertIn(cat, valid_cats, f"Recipe '{res}' has invalid category: '{cat}'")
            self.assertIn(res, ITEM_REGISTRY, f"Recipe result '{res}' missing from ITEM_REGISTRY")

    def test_minecraft_inspired_items_registered(self):
        """Verifies that all 50+ Minecraft-inspired items are properly registered in ITEM_REGISTRY."""
        expected_new_items = [
            # Building
            "carved_stone_bricks", "mosaic_tiles", "rope_rungs", "bamboo_scaffold",
            "cobblestone_parapet", "wrought_iron_palisade", "dried_thatch_bale",
            "forged_iron_chain", "reinforced_slate_slab", "hardened_clay_shingles",
            # Equipment & Tools & Weapons & Shields
            "fiber_clippers", "pyrite_sparker", "oak_buckler", "iron_aegis",
            "spud_angler_rod", "arbalest_repeater", "glowing_lumen_arrow",
            "totem_of_resurgence", "copper_harvester_sickle", "spud_quiver",
            # Survival, Consumables & Materials
            "hearty_root_stew", "glazed_golden_tuber", "herbal_salve",
            "night_gazer_elixir", "zephyr_tonic", "smoked_spud_jerky",
            "gilded_russet", "glass_flask", "burlap_tether", "explorers_satchel",
            "magnetic_lodestone", "brass_far_seer", "solar_chronometer",
            "abyssal_alloy_bar", "potato_bread", "sweet_tuber_pie",
            # Furniture & Workstations & Mechanisms
            "cozy_hearth_pit", "blight_ember_hearth", "smithing_anvil",
            "whetstone_wheel", "alchemical_retort", "iron_reinforced_door",
            "brass_lantern", "spectral_lantern", "timber_trapdoor", "hooped_cask",
            "iron_cauldron", "weaver_loom", "blast_kiln", "smokehouse_stove",
            "cartographer_desk", "fletcher_bench", "masonry_saw",
            "archery_target", "galvanic_attractor", "carved_tuber_lantern"
        ]

        self.assertGreaterEqual(len(expected_new_items), 50)
        for item_id in expected_new_items:
            self.assertIn(item_id, ITEM_REGISTRY, f"Item '{item_id}' missing from ITEM_REGISTRY")
            data = ITEM_REGISTRY[item_id]
            self.assertIn("name", data)
            self.assertIn("cat", data)
            self.assertIn("desc", data)
            self.assertTrue(len(data["name"]) > 0)
            self.assertTrue(len(data["desc"]) > 0)

    def test_armor_data_registration(self):
        """Verifies that equippable armor/shields/accessories are in ARMOR_DATA with valid stats."""
        equip_items = [
            "oak_buckler", "iron_aegis", "arbalest_repeater", "totem_of_resurgence",
            "explorers_satchel", "magnetic_lodestone", "brass_far_seer",
            "solar_chronometer", "spud_quiver", "copper_harvester_sickle"
        ]
        for eq_id in equip_items:
            self.assertIn(eq_id, ARMOR_DATA, f"Equippable item '{eq_id}' missing from ARMOR_DATA")
            data = ARMOR_DATA[eq_id]
            self.assertIn("slot", data)
            self.assertIn("name", data)

    # -------------------------------------------------------------------------
    # 3. Procedural Sprite Generation
    # -------------------------------------------------------------------------
    def test_procedural_sprites_for_all_new_items(self):
        """Verifies that AssetFactory generates clean, non-empty 24x24 icons for every new item."""
        new_items = [
            "carved_stone_bricks", "mosaic_tiles", "rope_rungs", "bamboo_scaffold",
            "fiber_clippers", "pyrite_sparker", "oak_buckler", "iron_aegis",
            "spud_angler_rod", "arbalest_repeater", "glowing_lumen_arrow",
            "totem_of_resurgence", "hearty_root_stew", "glazed_golden_tuber",
            "herbal_salve", "night_gazer_elixir", "zephyr_tonic", "smoked_spud_jerky",
            "gilded_russet", "glass_flask", "burlap_tether", "explorers_satchel",
            "magnetic_lodestone", "brass_far_seer", "solar_chronometer",
            "abyssal_alloy_bar", "potato_bread", "sweet_tuber_pie",
            "cozy_hearth_pit", "blight_ember_hearth", "smithing_anvil",
            "whetstone_wheel", "alchemical_retort", "iron_reinforced_door",
            "brass_lantern", "spectral_lantern", "timber_trapdoor", "hooped_cask",
            "iron_cauldron", "weaver_loom", "blast_kiln", "smokehouse_stove",
            "cartographer_desk", "fletcher_bench", "masonry_saw",
            "archery_target", "galvanic_attractor", "carved_tuber_lantern"
        ]

        for item_id in new_items:
            icon = self.factory.items.get(item_id)
            self.assertIsNotNone(icon, f"Icon for '{item_id}' must not be None")
            self.assertIsInstance(icon, pygame.Surface)
            self.assertEqual(icon.get_size(), (24, 24))
            # Verify surface has at least some opaque pixels
            has_pixels = any(icon.get_at((x, y))[3] > 0 for x in range(24) for y in range(24))
            self.assertTrue(has_pixels, f"Icon for '{item_id}' must not be completely blank")

    # -------------------------------------------------------------------------
    # 4. Crafting Category Tab Filtering
    # -------------------------------------------------------------------------
    def test_crafting_category_filtering(self):
        """Verifies that selecting category tabs filters recipes accurately."""
        # Near a workbench so all workbench and hand recipes are available
        ptx = int(self.player.center_x // SCALED_TILE)
        pty = int(self.player.center_y // SCALED_TILE)
        self.world.set_tile(ptx + 1, pty, TILE_WORK_BENCH)
        self.crafting.update_recipes(self.inv, self.world, self.player)

        total_available = len(self.crafting.available_recipes)
        self.assertGreater(total_available, 40)

        # Tab [ALL]: Should show 100% of available recipes
        self.crafting.set_category(CRAFT_CAT_ALL)
        self.assertEqual(len(self.crafting.filtered_recipes), total_available)

        # Tab [BUILDING]: Should show only building recipes
        self.crafting.set_category(CRAFT_CAT_BUILDING)
        building_recipes = self.crafting.filtered_recipes
        self.assertGreater(len(building_recipes), 0)
        for r in building_recipes:
            self.assertEqual(r["category"], CRAFT_CAT_BUILDING)
        b_results = [r["result"] for r in building_recipes]
        self.assertIn("wood_platform", b_results)
        self.assertIn("carved_stone_bricks", b_results)
        self.assertIn("rope_rungs", b_results)

        # Tab [EQUIPMENT]: Should show only equipment recipes
        self.crafting.set_category(CRAFT_CAT_EQUIPMENT)
        equipment_recipes = self.crafting.filtered_recipes
        self.assertGreater(len(equipment_recipes), 0)
        for r in equipment_recipes:
            self.assertEqual(r["category"], CRAFT_CAT_EQUIPMENT)
        eq_results = [r["result"] for r in equipment_recipes]
        self.assertIn("wooden_sword", eq_results)
        self.assertIn("oak_buckler", eq_results)
        self.assertIn("fiber_clippers", eq_results)

        # Tab [SURVIVAL]: Should show only survival & consumable recipes
        self.crafting.set_category(CRAFT_CAT_SURVIVAL)
        survival_recipes = self.crafting.filtered_recipes
        self.assertGreater(len(survival_recipes), 0)
        for r in survival_recipes:
            self.assertEqual(r["category"], CRAFT_CAT_SURVIVAL)
        surv_results = [r["result"] for r in survival_recipes]
        self.assertIn("herbal_salve", surv_results)
        self.assertIn("explorers_satchel", surv_results)
        self.assertIn("burlap_tether", surv_results)

        # Tab [FURNITURE]: Should show only furniture & mechanism recipes
        self.crafting.set_category(CRAFT_CAT_FURNITURE)
        furniture_recipes = self.crafting.filtered_recipes
        self.assertGreater(len(furniture_recipes), 0)
        for r in furniture_recipes:
            self.assertEqual(r["category"], CRAFT_CAT_FURNITURE)
        furn_results = [r["result"] for r in furniture_recipes]
        self.assertIn("work_bench", furn_results)
        self.assertIn("cozy_hearth_pit", furn_results)
        self.assertIn("smithing_anvil", furn_results)
        self.assertIn("brass_lantern", furn_results)

    def test_loose_category_naming_resolution(self):
        """Verifies that loose tab names like 'survival & consumables' resolve properly."""
        self.crafting.set_category("SURVIVAL & CONSUMABLES")
        self.assertEqual(self.crafting.selected_category, CRAFT_CAT_SURVIVAL)

        self.crafting.set_category("FURNITURE & MECHANISMS")
        self.assertEqual(self.crafting.selected_category, CRAFT_CAT_FURNITURE)

        self.crafting.set_category("BUILDING")
        self.assertEqual(self.crafting.selected_category, CRAFT_CAT_BUILDING)

        self.crafting.set_category("EQUIPMENT")
        self.assertEqual(self.crafting.selected_category, CRAFT_CAT_EQUIPMENT)

    # -------------------------------------------------------------------------
    # 5. Interactive Tab Clicking & Scrolling
    # -------------------------------------------------------------------------
    def test_handle_click_tab_selection(self):
        """Verifies clicking category tab screen rectangles switches tabs."""
        self.crafting.set_category(CRAFT_CAT_ALL)
        self.assertEqual(self.crafting.selected_category, CRAFT_CAT_ALL)

        # Click the EQUIPMENT tab
        eq_rect = self.crafting.tab_rects[CRAFT_CAT_EQUIPMENT]
        clicked = self.crafting.handle_click(eq_rect.centerx, eq_rect.centery, self.inv)
        self.assertTrue(clicked)
        self.assertEqual(self.crafting.selected_category, CRAFT_CAT_EQUIPMENT)
        self.assertEqual(self.crafting.scroll_row, 0)
        self.assertIn("place", self.sound.played)

        # Click the BUILDING tab
        b_rect = self.crafting.tab_rects[CRAFT_CAT_BUILDING]
        clicked = self.crafting.handle_click(b_rect.centerx, b_rect.centery, self.inv)
        self.assertTrue(clicked)
        self.assertEqual(self.crafting.selected_category, CRAFT_CAT_BUILDING)

    def test_scrolling_mechanics(self):
        """Verifies mouse wheel and scroll button bounds."""
        ptx = int(self.player.center_x // SCALED_TILE)
        pty = int(self.player.center_y // SCALED_TILE)
        self.world.set_tile(ptx + 1, pty, TILE_WORK_BENCH)
        self.crafting.update_recipes(self.inv, self.world, self.player)
        self.crafting.set_category(CRAFT_CAT_ALL)

        self.assertEqual(self.crafting.scroll_row, 0)

        # Scroll down
        self.crafting.handle_scroll(-1)
        self.assertGreaterEqual(self.crafting.scroll_row, 0)

        # Scroll cannot go negative
        self.crafting.handle_scroll(10)
        self.assertEqual(self.crafting.scroll_row, 0)

        # Scroll buttons click test
        if self.crafting.scroll_down_rect:
            self.crafting.handle_click(self.crafting.scroll_down_rect.centerx, self.crafting.scroll_down_rect.centery, self.inv)

    # -------------------------------------------------------------------------
    # 6. Crafting Execution & Ingredient Deductions
    # -------------------------------------------------------------------------
    def test_crafting_by_hand_cozy_hearth_pit(self):
        """Verifies crafting Cozy Hearth Pit by hand consumes wood, torch, and stone."""
        self.crafting.update_recipes(self.inv, self.world, self.player)
        recipe = next((r for r in self.crafting.available_recipes if r["result"] == "cozy_hearth_pit"), None)
        self.assertIsNotNone(recipe, "Cozy Hearth Pit recipe must be available by hand")
        self.assertFalse(recipe["can_craft"])

        # Add ingredients: 6 wood, 2 torch, 4 stone_block
        self.inv.add_item("wood", 6)
        self.inv.add_item("torch", 2)
        self.inv.add_item("stone_block", 4)
        self.crafting.update_recipes(self.inv, self.world, self.player)

        recipe = next(r for r in self.crafting.available_recipes if r["result"] == "cozy_hearth_pit")
        self.assertTrue(recipe["can_craft"])

        crafted = self.crafting.craft(recipe, self.inv)
        self.assertTrue(crafted)
        self.assertEqual(self.inv.count_item("cozy_hearth_pit"), 1)
        self.assertEqual(self.inv.count_item("wood"), 0)
        self.assertEqual(self.inv.count_item("torch"), 0)
        self.assertEqual(self.inv.count_item("stone_block"), 0)
        self.assertIn("craft", self.sound.played)

    def test_crafting_at_workbench_oak_buckler(self):
        """Verifies crafting Oak Buckler at a Work Bench requires proximity and ingredients."""
        # 1. Without workbench -> recipe not available
        self.crafting.update_recipes(self.inv, self.world, self.player)
        self.assertIsNone(next((r for r in self.crafting.available_recipes if r["result"] == "oak_buckler"), None))

        # 2. Place workbench near player
        ptx = int(self.player.center_x // SCALED_TILE)
        pty = int(self.player.center_y // SCALED_TILE)
        self.world.set_tile(ptx + 1, pty, TILE_WORK_BENCH)

        self.inv.add_item("wood", 10)
        self.inv.add_item("iron_bar", 1)
        self.crafting.update_recipes(self.inv, self.world, self.player)

        recipe = next((r for r in self.crafting.available_recipes if r["result"] == "oak_buckler"), None)
        self.assertIsNotNone(recipe)
        self.assertTrue(recipe["can_craft"])

        crafted = self.crafting.craft(recipe, self.inv)
        self.assertTrue(crafted)
        self.assertEqual(self.inv.count_item("oak_buckler"), 1)
        self.assertEqual(self.inv.count_item("wood"), 0)
        self.assertEqual(self.inv.count_item("iron_bar"), 0)

    def test_crafting_at_furnace_hearty_root_stew(self):
        """Verifies cooking Hearty Root Stew at a Furnace."""
        ptx = int(self.player.center_x // SCALED_TILE)
        pty = int(self.player.center_y // SCALED_TILE)
        self.world.set_tile(ptx + 1, pty, TILE_FURNACE)

        self.inv.add_item("raw_potato", 3)
        self.inv.add_item("glowing_mushroom", 1)
        self.inv.add_item("wood", 1)
        self.crafting.update_recipes(self.inv, self.world, self.player)

        recipe = next((r for r in self.crafting.available_recipes if r["result"] == "hearty_root_stew"), None)
        self.assertIsNotNone(recipe)
        self.assertTrue(recipe["can_craft"])

        crafted = self.crafting.craft(recipe, self.inv)
        self.assertTrue(crafted)
        self.assertEqual(self.inv.count_item("hearty_root_stew"), 1)
        self.assertEqual(self.inv.count_item("raw_potato"), 0)

    # -------------------------------------------------------------------------
    # 7. Consumables Healing & Stat Buffs
    # -------------------------------------------------------------------------
    def test_consumable_food_and_potions(self):
        """Verifies player consumption and healing from new foods/potions."""
        self.player.stats.max_hp = 200

        # Hearty Root Stew (+60 HP)
        self.player.health = 50
        consumed = self.player.consume_item("hearty_root_stew")
        self.assertTrue(consumed)
        self.assertEqual(self.player.health, 110)

        # Herbal Salve (+35 HP)
        consumed = self.player.consume_item("herbal_salve")
        self.assertTrue(consumed)
        self.assertEqual(self.player.health, 145)

        # Glazed Golden Tuber (+100 HP, +30 MP)
        self.player.health = 40
        self.player.stats.mp = 10
        consumed = self.player.consume_item("glazed_golden_tuber")
        self.assertTrue(consumed)
        self.assertEqual(self.player.health, 140)
        self.assertGreaterEqual(self.player.stats.mp, 40)

        # Gilded Russet (Full Heal)
        self.player.health = 20
        consumed = self.player.consume_item("gilded_russet")
        self.assertTrue(consumed)
        self.assertEqual(self.player.health, 200)

    # -------------------------------------------------------------------------
    # 8. Rendering & Tooltips
    # -------------------------------------------------------------------------
    def test_crafting_ui_rendering_and_tooltips(self):
        """Verifies that crafting UI, category tabs, and tooltips render without errors."""
        screen = pygame.Surface((1280, 720))
        ptx = int(self.player.center_x // SCALED_TILE)
        pty = int(self.player.center_y // SCALED_TILE)
        self.world.set_tile(ptx + 1, pty, TILE_WORK_BENCH)
        self.crafting.update_recipes(self.inv, self.world, self.player)

        # Render with hover over a tab
        tab_rect = self.crafting.tab_rects[CRAFT_CAT_EQUIPMENT]
        self.crafting.render(screen, tab_rect.centerx, tab_rect.centery, self.font)

        # Render with hover over recipe
        self.crafting.render(screen, 36, 310, self.font)

        # Direct recipe tooltip rendering
        recipe = self.crafting.available_recipes[0]
        self.crafting._render_recipe_tooltip(screen, 150, 150, recipe, self.font)


if __name__ == "__main__":
    unittest.main()
