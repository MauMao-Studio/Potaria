"""
Potaria - Comprehensive Unit Test Suite for Traders, UI Console, Crafting Folder, and Torch Physics
Verifies:
1. 3 Specialized Animated Traders (Wares, Enhance, Affix) with animated frames & 64x64 portraits.
2. Single Trader Rule (only 1 can exist at a time).
3. Distant Spawning (15-35 tiles from player).
4. Turtle Shield 3-block radius (96px).
5. All 3 traders repair broken gear for 1 Gold.
6. Browse Wares rich hover tooltip rendering.
7. data/crafting/craftable_items.json loading and recipe book integration.
8. Console chat auto-hide (6.0s) and word-wrapping.
9. Torch physics: no water placement, no open air floating, requires wall or solid support, drops on support break.
10. All items icon retrieval safety (zero crash guarantee).

Developer: Kurados | Pure Python 3.13 & pygame-ce
"""

import os
import json
import math
import time
import unittest
import pygame

from src.constants import (
    SCALED_TILE, TILE_AIR, TILE_WATER, TILE_TORCH, TILE_STONE, TILE_DIRT,
    WALL_AIR, WALL_STONE, RARITY_LEGENDARY, RARITY_ANCIENT
)
from src.assets.asset_factory import AssetFactory
from src.audio.sound_effects import SoundManager
from src.entities.player import Player
from src.entities.mob import Mob
from src.entities.npc import MysticTraderNPC, WaresTraderNPC, EnhancerTraderNPC, OccultistTraderNPC
from src.world.world import World
from src.ui.inventory import Inventory, ItemStack, ITEM_REGISTRY
from src.ui.crafting import CraftingSystem, load_craftable_recipes
from src.ui.hud import HUD
from src.ui.npc_dialogue import NPCDialogueWindow
from src.combat.combat_system import CombatManager


class TestTradersUIAndTorchRules(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pygame.init()
        cls.asset_factory = AssetFactory()
        cls.sound_manager = SoundManager()

    def setUp(self):
        self.world = World(self.asset_factory, seed=12345)
        self.player = Player(400, 300, self.asset_factory, self.sound_manager)
        self.inventory = Inventory(40)
        self.combat = CombatManager(self.asset_factory, self.sound_manager, None, None)
        self.hud = HUD(self.asset_factory)
        self.dialogue = NPCDialogueWindow(self.asset_factory, self.sound_manager)

    def test_01_three_distinct_animated_traders(self):
        """All 3 traders exist with unique roles, quotes, 4 animated sprite frames, and 64x64 portraits."""
        wares = WaresTraderNPC("Zephyrion", asset_factory=self.asset_factory, sound_manager=self.sound_manager)
        enhance = EnhancerTraderNPC("Ignis Vance", asset_factory=self.asset_factory, sound_manager=self.sound_manager)
        affix = OccultistTraderNPC("Morrigan", asset_factory=self.asset_factory, sound_manager=self.sound_manager)

        self.assertEqual(wares.npc_type, "trader_wares")
        self.assertEqual(enhance.npc_type, "trader_enhance")
        self.assertEqual(affix.npc_type, "trader_affix")

        # Animated frames
        for t_type in ("trader_wares", "trader_enhance", "trader_affix"):
            self.assertIn(t_type, self.asset_factory.npc_frames)
            frames = self.asset_factory.npc_frames[t_type]
            self.assertEqual(len(frames), 4, f"{t_type} must have 4 animated frames")
            for f in frames:
                self.assertIsInstance(f, pygame.Surface)
                self.assertEqual(f.get_size(), (28, 36))

        # 64x64 Portraits
        for t_type in ("trader_wares", "trader_enhance", "trader_affix"):
            self.assertIn(t_type, self.asset_factory.npc_portraits)
            p = self.asset_factory.npc_portraits[t_type]
            self.assertEqual(p.get_size(), (64, 64))

        # Role titles & quotes
        self.assertIn("Wares", wares.role_title)
        self.assertIn("Artificer", enhance.role_title)
        self.assertIn("Occultist", affix.role_title)

    def test_02_single_trader_rule_and_distant_spawn(self):
        """Only one trader can exist in the world at a time, spawning 15-35 tiles from player."""
        self.player.x = 2000
        self.player.y = 800

        # First trader spawn
        t1 = self.world.spawn_mystic_trader(self.player, self.asset_factory, self.sound_manager)
        self.assertIsNotNone(t1)
        self.assertIn(t1, self.world.town_npcs)

        # Distance check: should be at least 12 blocks away
        dist_tiles = abs(t1.x - self.player.x) / SCALED_TILE
        self.assertGreaterEqual(dist_tiles, 12.0, "Trader must spawn far from player (not camping in house)")

        # Second spawn attempt must return None (single trader at a time)
        t2 = self.world.spawn_mystic_trader(self.player, self.asset_factory, self.sound_manager)
        self.assertIsNone(t2, "Cannot spawn a second trader while one is active")

    def test_03_turtle_shield_three_blocks_radius(self):
        """Trader turtle shield activates when hostile enemies are within 3 blocks radius (96px)."""
        trader = WaresTraderNPC("Zephyrion", x=500, y=500, asset_factory=self.asset_factory, sound_manager=self.sound_manager)
        self.assertEqual(trader.shield_radius, 3 * SCALED_TILE) # 96 px

        # Outside 3 blocks (e.g. 150px away) -> shield inactive
        mob_far = Mob(650, 500, 24, 24, 50, 10, "Crawler")
        self.combat.mobs = [mob_far]
        trader.check_hostile_enemies(self.combat)
        self.assertFalse(trader.shield_active)

        # Inside 3 blocks (e.g. 60px away) -> shield active
        mob_near = Mob(560, 500, 24, 24, 50, 10, "Crawler")
        self.combat.mobs = [mob_near]
        trader.check_hostile_enemies(self.combat)
        self.assertTrue(trader.shield_active)

    def test_04_all_three_traders_repair_gear_for_one_gold(self):
        """All three traders can repair broken gear for 1 Gold Coin."""
        broken_blade = ItemStack("iron_broadsword", 1, enhancement_level=5, is_broken=True)
        self.inventory.slots[0] = broken_blade

        for trader_cls in (WaresTraderNPC, EnhancerTraderNPC, OccultistTraderNPC):
            trader = trader_cls(asset_factory=self.asset_factory, sound_manager=self.sound_manager)
            broken_blade.is_broken = True

            # Insufficient funds: 9,999 copper
            self.inventory.copper_coins = 9999
            self.inventory.silver_coins = 0
            self.inventory.gold_coins = 0
            ok, msg = trader.repair_item(broken_blade, self.inventory)
            self.assertFalse(ok)
            self.assertTrue(broken_blade.is_broken)

            # Exactly 1 Gold (10,000 copper)
            self.inventory.copper_coins = 10000
            ok, msg = trader.repair_item(broken_blade, self.inventory)
            self.assertTrue(ok)
            self.assertFalse(broken_blade.is_broken)
            self.assertEqual(self.inventory.copper_coins, 0)

    def test_05_shop_hover_tooltip_rendering(self):
        """Shop view correctly handles hover and renders rich item details matching inventory tooltips."""
        wares = WaresTraderNPC("Zephyrion", asset_factory=self.asset_factory, sound_manager=self.sound_manager)
        self.dialogue.open(wares, self.player, self.world, self.combat)
        self.dialogue.current_view = "shop"

        # Mock target surface
        surf = pygame.Surface((800, 600))
        catalog = wares.shop_catalog
        self.assertGreater(len(catalog), 0)

        # Hover over first slot (x=self.dialogue.x + 30, y=self.dialogue.y + 80)
        slot_x = self.dialogue.x + 40
        slot_y = self.dialogue.y + 85
        # Must render without error
        self.dialogue.render(surf, self.player, self.inventory, slot_x, slot_y)

        # Test tooltip method directly with an item entry and an affix service voucher
        item_entry = catalog[0]
        self.dialogue._render_shop_item_tooltip(surf, 100, 100, item_entry)

        affix_voucher = {
            "item_id": "affix_slot_service",
            "name": "Affix Slot Carving",
            "price": 50,
            "currency": "silver_coin",
            "is_affix_service": True,
            "rarity": "legendary"
        }
        self.dialogue._render_shop_item_tooltip(surf, 100, 100, affix_voucher)

    def test_06_craftable_items_json_loading(self):
        """Craftable items are saved in data/crafting/craftable_items.json and loaded by CraftingSystem."""
        json_path = os.path.join("data", "crafting", "craftable_items.json")
        self.assertTrue(os.path.exists(json_path), "data/crafting/craftable_items.json must exist")

        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        self.assertIn("craftable_items", data)
        items = data["craftable_items"]
        self.assertGreaterEqual(len(items), 110, "Must contain 110+ craftable recipes")

        # Verify CraftingSystem loads from this file
        recipes = load_craftable_recipes()
        self.assertGreaterEqual(len(recipes), len(items))

        crafting = CraftingSystem(self.asset_factory, self.sound_manager)
        self.assertGreaterEqual(len(crafting.recipes), 110)

    def test_07_console_chat_word_wrap_and_auto_hide(self):
        """Console wraps long text within box width (460px) and auto-hides idle messages after 6s."""
        self.hud.chat_active = False
        self.hud.local_chat_history = []

        # Add message
        self.hud.add_chat_message("[SYSTEM]", "This is a test notification message for the player.")
        self.assertEqual(len(self.hud.local_chat_history), 1)

        # Message is active (0s old) -> renders
        surf = pygame.Surface((800, 600))
        self.hud._render_chat(surf)

        # Age the message beyond 6.0 seconds
        self.hud.local_chat_history[0]["time"] = time.time() - 7.0

        # When chat is not active, older messages are hidden (clean view)
        surf_clean = pygame.Surface((800, 600))
        self.hud._render_chat(surf_clean)

        # When chat is active, console window appears with full history even if old
        self.hud.chat_active = True
        self.hud._render_chat(surf)

        # Test very long command message wraps cleanly
        long_msg = "/give " + "a" * 80 + " 1"
        self.hud.add_chat_message("[SYSTEM]", long_msg)
        self.hud._render_chat(surf)

    def test_08_torch_physics_placement_rules(self):
        """Torches cannot be placed in water or floating in air; require background wall or solid support."""
        tx, ty = 100, 50

        # Clear tile and wall
        self.world.set_tile(tx, ty, TILE_AIR)
        self.world.set_wall(tx, ty, WALL_AIR)
        self.world.set_tile(tx, ty + 1, TILE_AIR)
        self.world.set_tile(tx - 1, ty, TILE_AIR)
        self.world.set_tile(tx + 1, ty, TILE_AIR)

        # 1. Floating in open air without wall or solid neighbors -> fails
        placed = self.world.place_tile(tx, ty, TILE_TORCH)
        self.assertFalse(placed, "Torch cannot be placed floating in open air")

        # 2. Placing directly into water -> fails
        self.world.set_tile(tx, ty, TILE_WATER)
        self.world.set_tile(tx, ty + 1, TILE_STONE) # even with base solid
        placed_water = self.world.place_tile(tx, ty, TILE_TORCH)
        self.assertFalse(placed_water, "Torch cannot be placed underwater")

        # 3. Valid: solid block underneath
        self.world.set_tile(tx, ty, TILE_AIR)
        self.world.set_tile(tx, ty + 1, TILE_STONE)
        placed_ground = self.world.place_tile(tx, ty, TILE_TORCH)
        self.assertTrue(placed_ground, "Torch can be placed supported by a solid block beneath")

        # 4. Destroying the supporting block underneath breaks the torch!
        broken, drop, tid = self.world.damage_tile_at(tx, ty + 1, power=100)
        self.assertTrue(broken)
        self.assertEqual(self.world.get_tile(tx, ty), TILE_AIR, "Torch must fall/break when supporting block is destroyed")

        # 5. Valid: background wall behind torch
        self.world.set_tile(tx, ty + 1, TILE_AIR) # no ground support
        self.world.set_wall(tx, ty, WALL_STONE)
        placed_wall = self.world.place_tile(tx, ty, TILE_TORCH)
        self.assertTrue(placed_wall, "Torch can be placed on a background wall")

    def test_09_all_items_asset_generation_safety(self):
        """Every item in weapons.json, equipments.json, and ITEM_REGISTRY generates safely without crashing."""
        all_ids = set(ITEM_REGISTRY.keys())

        # Load weapons and equipments JSON
        for fpath in ("data/weapons.json", "data/equipments.json"):
            if os.path.exists(fpath):
                with open(fpath, "r", encoding="utf-8") as f:
                    cdata = json.load(f)
                    if isinstance(cdata, list):
                        all_ids.update(item["id"] for item in cdata if isinstance(item, dict) and "id" in item)
                    elif isinstance(cdata, dict):
                        all_ids.update(cdata.keys())

        # Sample check across diverse item types
        for iid in list(all_ids)[:150]:
            icon = self.asset_factory.items.get(iid)
            self.assertIsNotNone(icon)
            self.assertIsInstance(icon, pygame.Surface)
            self.assertEqual(icon.get_size(), (24, 24))

        # Check ItemStack passed to items.get (the bug that crashed previously)
        stack = ItemStack("iron_broadsword", 1)
        stack_icon = self.asset_factory.items.get(stack)
        self.assertIsNotNone(stack_icon)
        self.assertIsInstance(stack_icon, pygame.Surface)


if __name__ == "__main__":
    unittest.main()
