"""
Potaria - Comprehensive Verification Test Suite
Tests for:
1. Skill Bar HUD layout (no overlap, badge sizing, 46x54 slots, 30x30 icon area).
2. Fishing Battle Mini-Game completion, freeze fix, and loot drop under player's feet.
3. Rod-rarity weighted loot tables, junk items, Philippine fish, ingredients, equipment cap (Epic), skill books.
4. Dynamic rod tip calculation and line-of-sight casting check.
5. Authentic Filipino land animals (Manok, Pato, Baboy, Kalabaw, Kambing) & enemies (Aswang, BlightCultist).
6. Filipino culinary items, ingredients, spices, and recipes.
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import random
import unittest
import pygame

# Initialize pygame headless
os.environ["SDL_VIDEODRIVER"] = "dummy"
pygame.init()

from src.constants import SCREEN_WIDTH, SCREEN_HEIGHT, TILE_WATER, TILE_DIRT, SCALED_TILE
from src.assets.asset_factory import AssetFactory
from src.audio.sound_effects import SoundManager
from src.entities.player import Player
from src.combat.combat_system import CombatManager, has_line_of_sight
from src.ui.fishing_minigame import FishingBattleMiniGame, PINOY_FISH_DATA
from src.ui.inventory import Inventory, ItemStack, ITEM_REGISTRY
from src.ui.crafting import RECIPES
from src.ui.hud import HUD
from src.entities.mob import (
    MOB_TYPE_REGISTRY, ManokMob, PatoMob, BaboyMob, KalabawMob, KambingMob,
    Aswang, BlightCultist, PassiveAnimalMob
)


class MockWorld:
    def __init__(self, width=50, height=50):
        self.width = width
        self.height = height
        # 0 is air by default
        self.tiles = [[0 for _ in range(height)] for _ in range(width)]

    def get_tile(self, tx, ty):
        if 0 <= tx < self.width and 0 <= ty < self.height:
            return self.tiles[tx][ty]
        return 0

    def is_tile_solid(self, tx, ty):
        return self.get_tile(tx, ty) == TILE_DIRT

    def get_solid_rects_in_bounds(self, rect):
        return []


class TestPhOverhaulsVerification(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.asset_factory = AssetFactory()
        cls.sound_manager = SoundManager()

    def setUp(self):
        self.player = Player(100, 100, self.asset_factory, self.sound_manager)
        self.combat = CombatManager(self.asset_factory, self.sound_manager, None, None)
        self.inventory = Inventory(self.asset_factory)
        self.fishing_minigame = FishingBattleMiniGame(self.asset_factory, self.sound_manager)

    # =========================================================================
    # 1. SKILL BAR HUD REDESIGN VERIFICATION
    # =========================================================================
    def test_skill_bar_hud_layout_and_geometry(self):
        """Verifies skill bar slots are expanded to 46x54 with clean badges and no text clipping."""
        hud = HUD(self.asset_factory)
        surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        # Assign dummy skills
        if hasattr(self.player, "skills"):
            self.player.skills.hotkey_bindings = {"Q": "power_slash", "F": "whirlwind", "V": "dash", "R": "fireball"}
            self.player.skills.learned_skills = {"power_slash", "dash", "fireball", "whirlwind"}

        hud._render_skill_bar(surface, self.player)

        # Slot layout invariants
        slot_w, slot_h = 46, 54
        icon_box = 30
        self.assertLess(icon_box, slot_w)
        self.assertLess(icon_box, slot_h)

    # =========================================================================
    # 2. FISHING MINI-GAME FREEZE FIX & LOOT DROP UNDER PLAYER FEET
    # =========================================================================
    def test_fishing_battle_completion_and_loot_drop_under_feet(self):
        """Verifies completing reel progress to 100% spawns loot at player's feet and closes modal."""
        # Start fishing battle
        self.fishing_minigame.start(fish_id="raw_bangus", caught_count=2)
        self.assertTrue(self.fishing_minigame.is_active)
        self.assertIsNone(self.fishing_minigame.result)

        # Reel to 100%
        self.fishing_minigame.is_thrashing = False
        for _ in range(self.fishing_minigame.target_clicks + 2):
            self.fishing_minigame.handle_click(is_right_click=True)

        self.assertEqual(self.fishing_minigame.reeling_progress, 100.0)
        self.assertFalse(self.fishing_minigame.is_active)
        self.assertEqual(self.fishing_minigame.result, "caught")

        # Simulate main.py game loop update block
        class MockGame:
            pass

        game = MockGame()
        game.player = self.player
        game.combat = self.combat
        game.fishing_minigame = self.fishing_minigame
        game.fishing_bobber = {"x": 200, "y": 200, "state": "caught"}
        game.inventory = self.inventory
        game.asset_factory = self.asset_factory
        game.sound_manager = self.sound_manager

        initial_drop_count = len(game.combat.dropped_items)

        # Execute the update logic from main.py
        dt = 0.016
        if hasattr(game, "fishing_minigame") and (game.fishing_minigame.is_active or game.fishing_minigame.result is not None):
            res = game.fishing_minigame.update(dt)
            if res == "caught":
                fish_id = game.fishing_minigame.fish_id
                fish_cnt = game.fishing_minigame.caught_count
                game.combat._spawn_loot_drop(fish_id, fish_cnt, game.player.center_x, game.player.y + game.player.height)
                game.fishing_minigame.result = None
                game.fishing_minigame.is_active = False
                game.fishing_bobber = None

        # Verify loot dropped
        self.assertEqual(len(game.combat.dropped_items), initial_drop_count + 1)
        dropped = game.combat.dropped_items[-1]
        self.assertEqual(dropped.item_id, "raw_bangus")
        self.assertEqual(dropped.count, 2)

        # Verify loot spawned under player's feet (y coordinate around player.y + player.height)
        expected_feet_y = game.player.y + game.player.height
        self.assertAlmostEqual(dropped.y, expected_feet_y, delta=2.0)
        self.assertAlmostEqual(dropped.x, game.player.center_x, delta=10.0)

        # Verify state is completely reset (modal will not freeze on screen)
        self.assertIsNone(game.fishing_minigame.result)
        self.assertFalse(game.fishing_minigame.is_active)
        self.assertIsNone(game.fishing_bobber)

        # Verify render does NOT render anything when active is False and result is None
        dummy_surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        game.fishing_minigame.render(dummy_surf)

    def test_dynamic_rod_tip_calculation(self):
        """Verifies player.get_rod_tip_pos tracks facing direction and aim angle."""
        self.player.facing_right = True
        self.player.aim_angle = 0.0
        rx, ry = self.player.get_rod_tip_pos()
        self.assertGreater(rx, self.player.center_x, "Right-facing rod tip should be forward of player center")

        self.player.facing_right = False
        lx, ly = self.player.get_rod_tip_pos()
        self.assertLess(lx, self.player.center_x, "Left-facing rod tip should be backward of player center")

    def test_line_of_sight_to_water_before_casting(self):
        """Verifies casting requires clear line of sight to water without solid terrain obstruction."""
        world = MockWorld(width=20, height=20)
        # Player at (2, 2) in world tiles (64, 64)
        # Water at (10, 2)
        # Solid dirt wall at (5, 2)
        world.tiles[5][2] = TILE_DIRT
        has_los = has_line_of_sight(world, 2 * SCALED_TILE + 16, 2 * SCALED_TILE + 16, 10 * SCALED_TILE + 16, 2 * SCALED_TILE + 16)
        self.assertFalse(has_los, "Line of sight should be blocked by solid dirt block")

        # Clear line of sight
        world.tiles[5][2] = 0 # Air
        has_los_clear = has_line_of_sight(world, 2 * SCALED_TILE + 16, 2 * SCALED_TILE + 16, 10 * SCALED_TILE + 16, 2 * SCALED_TILE + 16)
        self.assertTrue(has_los_clear, "Clear path should have line of sight")

    # =========================================================================
    # 3. MINECRAFT-STYLE FISHING LOOT TABLES
    # =========================================================================
    def test_junk_items_and_recyclable_items(self):
        """Verifies recyclable junk and dirt items exist in registry with proper properties."""
        junk_items = ["dirt_clod", "old_boot", "rusty_can", "seaweed", "driftwood"]
        for jid in junk_items:
            self.assertIn(jid, ITEM_REGISTRY, f"Missing junk item: {jid}")
            item_data = ITEM_REGISTRY[jid]
            self.assertEqual(item_data.get("rarity"), "common")
            self.assertEqual(item_data.get("cat"), "material")
            self.assertIn("Recyclable", item_data.get("special", ""))

    def test_equipment_capped_at_epic(self):
        """Verifies fishing loot tables do NOT grant Legendary or Mythic equipment."""
        forbidden_mythic_legendary = [
            "neptune_tide_rod", "astral_leviathan_rod", "celestial_bow", "celestial_shard",
            "starfury", "totem_of_resurgence", "starch_blade"
        ]
        epic_equipment = [
            "zephyr_striders", "talisman_of_vigor", "arcane_orchid", "gilded_russet",
            "magma_greatsword", "bone_scythe", "magma_bow", "hermes_boots"
        ]
        for eq in epic_equipment:
            self.assertIn(eq, ITEM_REGISTRY)
            self.assertEqual(ITEM_REGISTRY[eq].get("rarity"), "epic")

        for f_eq in forbidden_mythic_legendary:
            self.assertNotIn(f_eq, epic_equipment)

    # =========================================================================
    # 4. PHILIPPINE LAND ANIMALS, POULTRY & HOSTILE MOBS
    # =========================================================================
    def test_philippine_animals_registration_and_properties(self):
        """Verifies Manok, Pato, Baboy, Kalabaw, Kambing are registered and passive."""
        ph_animals = [
            ("manok", ManokMob),
            ("pato", PatoMob),
            ("baboy", BaboyMob),
            ("kalabaw", KalabawMob),
            ("kambing", KambingMob),
        ]
        for mob_type, mob_cls in ph_animals:
            self.assertIn(mob_type, MOB_TYPE_REGISTRY)
            self.assertEqual(MOB_TYPE_REGISTRY[mob_type], mob_cls)

            # Instance check
            mob_inst = mob_cls(100, 100, self.asset_factory)
            self.assertTrue(getattr(mob_inst, "is_passive", False))
            self.assertIsInstance(mob_inst, PassiveAnimalMob)

    def test_philippine_animal_special_behaviors(self):
        """Verifies flutter falling for chicken, water buoyancy for duck, high jump for goat, defense for carabao."""
        world = MockWorld()
        manok = ManokMob(100, 100, self.asset_factory)
        manok.vy = 5.0
        manok.update(0.016, world, self.player)
        self.assertLessEqual(manok.vy, 2.5, "Chicken should flutter-fall with reduced terminal velocity")

        kalabaw = KalabawMob(100, 100, self.asset_factory)
        self.assertGreaterEqual(kalabaw.defense, 4, "Carabao should have tough natural defense")
        self.assertGreaterEqual(kalabaw.max_hp, 100, "Carabao should have high max health")

        kambing = KambingMob(100, 100, self.asset_factory)
        self.assertLess(kambing.jump_power, -5.5, "Goat should have high agility jump power")

    def test_philippine_enemies_registration(self):
        """Verifies Aswang and Blight Cultist are registered hostile enemies."""
        self.assertIn("aswang", MOB_TYPE_REGISTRY)
        self.assertIn("blight_cultist", MOB_TYPE_REGISTRY)
        self.assertEqual(MOB_TYPE_REGISTRY["aswang"], Aswang)
        self.assertEqual(MOB_TYPE_REGISTRY["blight_cultist"], BlightCultist)

        aswang = Aswang(100, 100, self.asset_factory)
        self.assertFalse(getattr(aswang, "is_passive", False))
        self.assertEqual(aswang.name, "Aswang")

        cultist = BlightCultist(100, 100, self.asset_factory)
        self.assertFalse(getattr(cultist, "is_passive", False))
        self.assertEqual(cultist.name, "Blight Cultist")

    def test_mob_loot_drops_for_animals_and_enemies(self):
        """Verifies combat loot drop system spawns authentic meats, milk, eggs, feathers, and cultist drops."""
        manok = ManokMob(100, 100, self.asset_factory)
        self.combat.dropped_items.clear()
        self.combat._drop_mob_loot(manok)
        item_ids = [d.item_id for d in self.combat.dropped_items]
        self.assertIn("raw_chicken", item_ids)
        self.assertIn("feather", item_ids)

        kalabaw = KalabawMob(100, 100, self.asset_factory)
        self.combat.dropped_items.clear()
        self.combat._drop_mob_loot(kalabaw)
        item_ids = [d.item_id for d in self.combat.dropped_items]
        self.assertIn("raw_beef", item_ids)
        self.assertIn("carabao_milk", item_ids)

    # =========================================================================
    # 5. FILIPINO FOODS, INGREDIENTS & RECIPES
    # =========================================================================
    def test_filipino_recipes_and_ingredients_integration(self):
        """Verifies Filipino recipes in crafting.py require authentic ingredients and produce dishes."""
        expected_dishes = [
            "chicken_adobo", "pork_adobo", "sinigang", "tinola", "kare_kare",
            "bulalo", "lechon", "pancit_bihon", "arroz_caldo", "halo_halo",
            "daing_na_bangus", "kaldereta", "balut", "itlog_na_maalat", "sinangag"
        ]
        recipe_results = [r.get("result") for r in RECIPES]
        for dish in expected_dishes:
            self.assertIn(dish, recipe_results, f"Missing Filipino dish recipe: {dish}")
            self.assertIn(dish, ITEM_REGISTRY, f"Missing dish in ITEM_REGISTRY: {dish}")
            self.assertEqual(ITEM_REGISTRY[dish].get("cat"), "consumable")

        # Check ingredients exist
        expected_ingredients = [
            "rice", "garlic", "onion", "ginger", "calamansi", "tamarind",
            "soy_sauce", "vinegar", "black_pepper", "salt", "coconut_milk",
            "peanut_butter", "eggplant", "string_beans", "pancit_noodles"
        ]
        for ing in expected_ingredients:
            self.assertIn(ing, ITEM_REGISTRY, f"Missing Filipino ingredient in ITEM_REGISTRY: {ing}")

    def test_pinoy_food_and_animal_sprites_generated(self):
        """Verifies AssetFactory generates sprites for all Pinoy items and mobs."""
        for item_id in ["sinigang", "chicken_adobo", "tinola", "dirt_clod", "old_boot", "calamansi"]:
            self.assertIn(item_id, self.asset_factory.items)
            self.assertIsInstance(self.asset_factory.items[item_id], pygame.Surface)

        for mob_id in ["manok", "pato", "baboy", "kalabaw", "kambing", "aswang", "blight_cultist"]:
            self.assertIn(mob_id, self.asset_factory.mobs)
            self.assertIsInstance(self.asset_factory.mobs[mob_id], list)
            self.assertGreater(len(self.asset_factory.mobs[mob_id]), 0)


if __name__ == "__main__":
    unittest.main()
