"""
Potaria - Wooden Sword Unit & Integration Test Suite
Developer: Kurados | Pure Python 3.13 & pygame-ce 2.5.8

Verifies:
1. Registration in data/weapons.json and src/ui/inventory.py (ITEM_REGISTRY)
2. Proper item metadata: name, category, rarity, stats (ATK, speed, crit), lore, description
3. Dual-alias resolution (wooden_sword <-> wood_sword)
4. Crafting recipe in src/ui/crafting.py (RECIPES): hand & work bench crafting, exact, surplus, insufficient materials
5. Equipment stat calculation and attack speed cooldown
6. Tooltip rendering across HUD, Character Panel, and Crafting UI
7. Weapon swinging and combat strike damage application
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Headless environment
os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"

import pygame
pygame.init()
pygame.display.set_mode((1280, 720))

from src.constants import (
    RARITY_COMMON, CAT_WEAPON, SCALED_TILE, TILE_WORK_BENCH
)
from src.assets.asset_factory import AssetFactory
from src.audio.sound_effects import SoundManager
from src.world.world import World
from src.entities.player import Player
from src.entities.mob import SlimeMob
from src.combat.combat_system import CombatManager
from src.rpg.stats import PlayerStats
from src.rpg.equipment import Equipment, ARMOR_DATA
from src.ui.inventory import Inventory, ItemStack, ITEM_REGISTRY, ITEM_ALIASES
from src.ui.crafting import CraftingSystem, RECIPES
from src.ui.hud import HUD
from src.ui.character_panel import CharacterPanel
from main import PotariaGame


class TestWoodenSword(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.factory = AssetFactory()
        cls.sound = SoundManager()

    def test_01_item_registry_registration(self):
        """Verifies wooden_sword is registered in ITEM_REGISTRY with correct stats."""
        self.assertIn("wooden_sword", ITEM_REGISTRY)
        data = ITEM_REGISTRY["wooden_sword"]

        self.assertEqual(data["name"], "Wooden Sword")
        self.assertEqual(data["cat"], CAT_WEAPON)
        self.assertEqual(data["rarity"], RARITY_COMMON)
        self.assertEqual(data["atk"], 7)
        self.assertEqual(data["damage"], 7)
        self.assertEqual(data["speed"], 0.0)
        self.assertEqual(data["crit"], 2.0)
        self.assertEqual(data["max_stack"], 1)
        self.assertIn("desc", data)
        self.assertGreater(len(data["desc"]), 0)
        self.assertIn("lore", data)
        self.assertGreater(len(data["lore"]), 0)
        self.assertEqual(data.get("special"), "Slashing Strike")

    def test_02_alias_resolution(self):
        """Verifies wood_sword alias maps to wooden_sword seamlessly."""
        self.assertIn("wood_sword", ITEM_ALIASES)
        self.assertEqual(ITEM_ALIASES["wood_sword"], "wooden_sword")
        self.assertIn("wood_sword", ITEM_REGISTRY)

        stack_canon = ItemStack("wooden_sword")
        stack_alias = ItemStack("wood_sword")
        self.assertEqual(stack_canon.data["name"], "Wooden Sword")
        self.assertEqual(stack_alias.data["name"], "Wooden Sword")
        self.assertEqual(stack_alias.data["atk"], 7)

        inv = Inventory(self.factory)
        inv.slots[0] = ItemStack("wooden_sword", 1)
        self.assertEqual(inv.count_item("wooden_sword"), 1)
        self.assertEqual(inv.count_item("wood_sword"), 1)

    def test_03_weapons_json_registration(self):
        """Verifies wooden_sword is included in data/weapons.json."""
        import json
        weapons_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "weapons.json")
        self.assertTrue(os.path.exists(weapons_path))
        with open(weapons_path, "r", encoding="utf-8") as f:
            w_list = json.load(f)
        w_entry = next((w for w in w_list if w["id"] == "wooden_sword"), None)
        self.assertIsNotNone(w_entry, "wooden_sword must exist in data/weapons.json")
        self.assertEqual(w_entry["name"], "Wooden Sword")
        self.assertEqual(w_entry["cat"], "weapon")
        self.assertEqual(w_entry["rarity"], "common")
        self.assertEqual(w_entry["atk"], 7)
        self.assertEqual(w_entry["speed"], 0.0)
        self.assertEqual(w_entry["crit"], 2.0)

    def test_04_armor_data_stats(self):
        """Verifies ARMOR_DATA has wooden_sword and wood_sword with proper weapon stats."""
        self.assertIn("wooden_sword", ARMOR_DATA)
        self.assertIn("wood_sword", ARMOR_DATA)
        self.assertEqual(ARMOR_DATA["wooden_sword"]["atk"], 7)
        self.assertEqual(ARMOR_DATA["wooden_sword"]["crit"], 2.0)

        eq = Equipment()
        stats = PlayerStats()
        base_atk = stats.base_atk
        base_crit = stats.base_crit_rate

        eq.recalculate_stats(stats, active_item_id="wooden_sword")
        self.assertEqual(stats.total_atk, base_atk + 7)
        self.assertEqual(stats.total_crit_rate, base_crit + 2.0)

        # Also verify with alias ID
        stats_alias = PlayerStats()
        eq.recalculate_stats(stats_alias, active_item_id="wood_sword")
        self.assertEqual(stats_alias.total_atk, base_atk + 7)
        self.assertEqual(stats_alias.total_crit_rate, base_crit + 2.0)

    def test_05_crafting_recipe_and_execution(self):
        """Tests crafting wooden_sword by hand and at a work bench."""
        crafting = CraftingSystem(self.factory, self.sound)
        inv = Inventory(self.factory, difficulty="hardcore")
        world = World(self.factory, seed=999)
        player = Player(100, 100, self.factory, self.sound)

        # Verify recipe exists in RECIPES
        ws_recipe = next((r for r in RECIPES if r["result"] == "wooden_sword"), None)
        self.assertIsNotNone(ws_recipe, "wooden_sword recipe missing from RECIPES")
        self.assertIn(("wood", 7), ws_recipe["ingredients"])

        # 1. By hand (no work bench nearby) - with empty inventory
        crafting.update_recipes(inv, world, player)
        avail = next((r for r in crafting.available_recipes if r["result"] == "wooden_sword"), None)
        self.assertIsNotNone(avail, "wooden_sword recipe should be available by hand")
        self.assertFalse(avail["can_craft"])
        self.assertFalse(crafting.craft(avail, inv))

        # 2. Insufficient wood (6 out of 7)
        inv.add_item("wood", 6)
        crafting.update_recipes(inv, world, player)
        avail = next((r for r in crafting.available_recipes if r["result"] == "wooden_sword"), None)
        self.assertFalse(avail["can_craft"])
        self.assertFalse(crafting.craft(avail, inv))
        self.assertEqual(inv.count_item("wood"), 6)
        self.assertEqual(inv.count_item("wooden_sword"), 0)

        # 3. Exact wood (7 wood total)
        inv.add_item("wood", 1) # now 7
        crafting.update_recipes(inv, world, player)
        avail = next((r for r in crafting.available_recipes if r["result"] == "wooden_sword"), None)
        self.assertTrue(avail["can_craft"])
        crafted = crafting.craft(avail, inv)
        self.assertTrue(crafted)
        self.assertEqual(inv.count_item("wood"), 0)
        self.assertEqual(inv.count_item("wooden_sword"), 1)

        # 4. Crafting near a placed work bench with surplus wood (15 wood)
        ptx = int(player.center_x // SCALED_TILE)
        pty = int(player.center_y // SCALED_TILE)
        world.set_tile(ptx + 1, pty, TILE_WORK_BENCH)

        inv_surplus = Inventory(self.factory, difficulty="hardcore")
        inv_surplus.add_item("wood", 15)
        crafting.update_recipes(inv_surplus, world, player)
        avail_wb = next((r for r in crafting.available_recipes if r["result"] == "wooden_sword"), None)
        self.assertIsNotNone(avail_wb)
        self.assertTrue(avail_wb["can_craft"])
        crafted_wb = crafting.craft(avail_wb, inv_surplus)
        self.assertTrue(crafted_wb)
        self.assertEqual(inv_surplus.count_item("wooden_sword"), 1)
        self.assertEqual(inv_surplus.count_item("wood"), 8)

    def test_06_hud_and_panel_tooltips(self):
        """Verifies rich tooltips render without error for wooden_sword."""
        target_surf = pygame.Surface((1280, 720))
        hud = HUD(self.factory)
        char_panel = CharacterPanel(self.factory)
        crafting = CraftingSystem(self.factory, self.sound)
        font = pygame.font.Font(None, 20)

        # 1. HUD tooltip
        stack = ItemStack("wooden_sword", 1)
        hud._render_tooltip(target_surf, 100, 100, stack)

        # 2. Character panel equipped / held tooltip
        char_panel._render_equipped_tooltip(target_surf, 150, 150, "wooden_sword", is_held=True)
        char_panel._render_equipped_tooltip(target_surf, 150, 150, "wooden_sword", is_held=False)

        # 3. Crafting recipe tooltip
        recipe = next(r for r in RECIPES if r["result"] == "wooden_sword")
        crafting._render_recipe_tooltip(target_surf, 200, 200, recipe, font)

    def test_07_weapon_swing_and_combat_hit(self):
        """Verifies weapon attack cooldown, swinging, and melee combat damage."""
        game = PotariaGame()
        player = game.player
        combat = game.combat

        # Put wooden sword in hotbar slot 0
        game.inventory.slots[0] = ItemStack("wooden_sword", 1)
        game.inventory.selected_slot = 0
        active = game.inventory.get_active_item()
        self.assertIsNotNone(active)
        self.assertEqual(active.item_id, "wooden_sword")

        # Verify attack cooldown
        cooldown = game.get_weapon_attack_cooldown(active)
        self.assertAlmostEqual(cooldown, 0.32, places=2)

        # Recalculate stats with held weapon
        player.equipment.recalculate_stats(player.stats, active_item_id="wooden_sword")
        expected_atk = player.stats.base_atk + 7
        self.assertEqual(player.stats.total_atk, expected_atk)

        # Spawn a mob right in front of the player
        mob = SlimeMob(player.center_x + 30, player.center_y - 10, game.asset_factory)
        mob.hp = 50
        combat.mobs = [mob]

        # Face right and trigger swing
        player.facing_right = True
        player.aim_angle = 0.0
        player.start_swing()
        player.trigger_attack(cooldown)
        self.assertTrue(player.is_swinging)

        # Perform weapon hit check
        combat._check_weapon_hits(player, game.world)
        self.assertLess(mob.hp, 50, "Mob should take damage from wooden sword strike")
        self.assertIn(mob, player.swing_hit_targets)

        # Render player holding the sword without exceptions
        game_surf = pygame.Surface((1280, 720))
        held_icon = game.asset_factory.items.get("wooden_sword")
        self.assertIsNotNone(held_icon)
        player.render(game_surf, game.camera, held_item_icon=held_icon, held_item=active)


if __name__ == "__main__":
    unittest.main()
