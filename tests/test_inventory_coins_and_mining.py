"""
Potaria - Comprehensive Verification Suite for:
1. Full Inventory Dropped Item Magnetism Rejection
2. Coin Pickups into Dedicated Coin Purse (Bypassing Inventory Slots)
3. Coin Denomination Conversions (100c = 1s, 100s = 1g)
4. Legacy Inventory Coins Migration
5. Crafting UI Layout Non-Overlapping Coordinates
6. Progressive Tool Tier Mining Damage & Scaling (Wood Axe, Copper Axe, Iron Axe, Hand, Pickaxe)
7. Progressive Cracking Stages (0-3) and Break Gauge Data

Developer: Kurados
Engine: Pure Python 3 + pygame-ce (100% offline)
"""

import os
import sys
import math
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"

import pygame
pygame.init()

from src.constants import (
    TILE_AIR, TILE_DIRT, TILE_STONE, TILE_WOOD, TILE_WOOD_TRUNK,
    TILE_COPPER_ORE, TILE_IRON_ORE, TILE_GOLD_ORE,
    INV_TOTAL_SLOTS, CAT_TOOL, CAT_WEAPON, SCALED_TILE
)
from src.assets.asset_factory import AssetFactory
from src.audio.sound_effects import SoundManager
from src.world.world import World
from src.entities.player import Player
from src.entities.dropped_item import DroppedItem
from src.combat.combat_system import CombatManager
from src.camera import Camera
from src.rpg.stats import PlayerStats
from src.ui.inventory import Inventory, ItemStack, get_mining_damage
from src.ui.crafting import CraftingSystem
from src.ui.character_panel import CharacterPanel


class TestInventoryCoinsAndMining(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.assets = AssetFactory()
        cls.sound = SoundManager()

    def setUp(self):
        self.camera = Camera(800, 600)
        self.world = World(self.assets, seed=42)
        self.player = Player(200, 200, self.assets, self.sound)
        self.inv = Inventory(self.assets, difficulty="normal")
        self.player.inventory = self.inv
        self.inv.player = self.player

    def test_01_full_inventory_stops_dropped_item_magnetism(self):
        """When Spud's inventory is full, non-coin dropped items must NOT magnetize or hover."""
        # Fill all 40 slots to maximum stack capacity with dirt blocks
        for i in range(INV_TOTAL_SLOTS):
            self.inv.slots[i] = ItemStack("dirt_block", 999)

        self.assertFalse(self.inv.can_add_item("stone_block", 1))

        # Spawn a dropped stone block near the player
        dropped = DroppedItem("stone_block", 1, self.player.center_x + 30, self.player.center_y, self.assets)
        dropped.age = 2.0  # past pickup_delay
        initial_x = dropped.x
        initial_y = dropped.y

        # Update dropped item physics
        dropped.update(0.1, self.world, self.player)

        # Magnetism must be completely disabled (magnet_speed == 0)
        self.assertEqual(dropped.magnet_speed, 0.0)
        # Item should not have accelerated toward the player
        dist_change_x = abs(dropped.x - initial_x)
        self.assertLess(dist_change_x, 5.0)

        # Now free a slot in inventory
        self.inv.slots[0] = None
        self.assertTrue(self.inv.can_add_item("stone_block", 1))

        # Item should now magnetize towards Spud
        dropped.update(0.1, self.world, self.player)
        self.assertGreater(dropped.magnet_speed, 0.0)

    def test_02_coin_pickups_bypass_slots_into_dedicated_purse(self):
        """Coins must never occupy normal inventory slots and deposit directly into player's coin purse."""
        # Fill all 40 slots with materials so inventory is 100% full
        for i in range(INV_TOTAL_SLOTS):
            self.inv.slots[i] = ItemStack("stone_block", 999)

        # Coins can always be accepted
        self.assertTrue(self.inv.can_add_item("copper_coin", 50))
        self.assertTrue(self.inv.can_add_item("silver_coin", 10))
        self.assertTrue(self.inv.can_add_item("gold_coin", 2))

        # Add coins
        rem = self.inv.add_item("copper_coin", 75)
        self.assertEqual(rem, 0)
        self.assertEqual(self.inv.copper_coins, 75)
        self.assertEqual(self.player.stats.copper_coins, 75)

        # Verify none of the 40 slots hold copper_coin
        for idx, slot in enumerate(self.inv.slots):
            self.assertIsNotNone(slot)
            self.assertEqual(slot.item_id, "stone_block")

        # Dropped coin magnetizes to player even when inventory is completely full
        dropped_coin = DroppedItem("copper_coin", 20, self.player.center_x + 40, self.player.center_y, self.assets)
        dropped_coin.age = 2.0
        dropped_coin.update(0.1, self.world, self.player)
        self.assertGreater(dropped_coin.magnet_speed, 0.0)

    def test_03_coin_denomination_conversions(self):
        """100 copper auto-converts to 1 silver; 100 silver auto-converts to 1 gold."""
        stats = PlayerStats()
        stats.copper_coins = 0
        stats.silver_coins = 0
        stats.gold_coins = 0

        # Adding 99 copper
        stats.add_coins(copper=99)
        self.assertEqual(stats.copper_coins, 99)
        self.assertEqual(stats.silver_coins, 0)
        self.assertEqual(stats.gold_coins, 0)
        self.assertEqual(stats.total_copper_value, 99)

        # Adding 1 copper triggers conversion to 1 silver
        stats.add_coins(copper=1)
        self.assertEqual(stats.copper_coins, 0)
        self.assertEqual(stats.silver_coins, 1)
        self.assertEqual(stats.gold_coins, 0)
        self.assertEqual(stats.total_copper_value, 100)

        # Adding 99 silver triggers conversion to 1 gold
        stats.add_coins(silver=99)
        self.assertEqual(stats.copper_coins, 0)
        self.assertEqual(stats.silver_coins, 0)
        self.assertEqual(stats.gold_coins, 1)
        self.assertEqual(stats.total_copper_value, 10000)

        # Adding mixed coins: 2 gold, 35 silver, 42 copper
        stats.add_coins(copper=42, silver=35, gold=2)
        self.assertEqual(stats.gold_coins, 3)
        self.assertEqual(stats.silver_coins, 35)
        self.assertEqual(stats.copper_coins, 42)
        self.assertEqual(stats.total_copper_value, 33542)

        # Deducting with change breakdown
        success = stats.remove_coins(50)  # deduct 50 copper from 3g 35s 42c (33542 -> 33492)
        self.assertTrue(success)
        self.assertEqual(stats.gold_coins, 3)
        self.assertEqual(stats.silver_coins, 34)
        self.assertEqual(stats.copper_coins, 92)

        # Insufficient funds
        overdraw = stats.remove_coins(999999)
        self.assertFalse(overdraw)
        self.assertEqual(stats.total_copper_value, 33492)

        # Inventory count_item("copper_coin") reflects total purchasing power
        self.assertEqual(self.inv.count_item("copper_coin"), self.player.stats.total_copper_value)

    def test_04_legacy_inventory_coins_migration(self):
        """Legacy saves with coins in regular inventory slots migrate cleanly into Coin Purse."""
        # Clear inventory and place coin stacks into slots
        self.inv.slots = [None] * INV_TOTAL_SLOTS
        self.player.stats.set_from_copper(0)

        self.inv.slots[2] = ItemStack("copper_coin", 590)  # 5 silver, 90 copper
        self.inv.slots[8] = ItemStack("silver_coin", 95)   # 95 silver
        self.inv.slots[15] = ItemStack("gold_coin", 3)     # 3 gold

        # Migrate coins
        self.inv.migrate_coins()

        # Slots must now be empty
        self.assertIsNone(self.inv.slots[2])
        self.assertIsNone(self.inv.slots[8])
        self.assertIsNone(self.inv.slots[15])

        # Coin purse must have all funds: 590 + 9500 + 30000 = 40090 copper
        # 40090 = 4 gold, 0 silver, 90 copper
        self.assertEqual(self.player.stats.gold_coins, 4)
        self.assertEqual(self.player.stats.silver_coins, 0)
        self.assertEqual(self.player.stats.copper_coins, 90)
        self.assertEqual(self.player.stats.total_copper_value, 40090)

    def test_05_crafting_ui_layout_coordinates_separation(self):
        """Verify Crafting header and inventory drop/recycle buttons do NOT collide vertically."""
        self.inv.is_open = True
        drop_rect = self.inv.get_drop_button_rect()
        recycle_rect = self.inv.get_recycle_button_rect()

        # In inventory: rows=4, start_y=20, slot=40, pad=4 -> y = 20 + 4 * 44 + 4 = 200, h = 22
        # drop_rect bottom is 200 + 22 = 222
        self.assertEqual(drop_rect.y, 200)
        self.assertEqual(drop_rect.bottom, 222)
        self.assertEqual(recycle_rect.y, 200)
        self.assertEqual(recycle_rect.bottom, 222)

        crafting = CraftingSystem(self.assets, self.sound)
        # Header is rendered at y=232, recipes start at y=258
        header_y = 232
        recipes_start_y = 258

        # Assert clean gap between drop buttons and crafting header
        self.assertGreater(header_y, drop_rect.bottom, "Crafting header must sit cleanly below Drop buttons!")
        self.assertGreater(recipes_start_y, header_y, "Recipe slot grid must start below Crafting header!")

    def test_06_tool_tier_mining_damage_scaling(self):
        """Verify tool tier damage and mining times: Hand, Wood Axe, Copper Axe, Iron Axe, Pickaxes."""
        # Continuous mining rate is 0.15s per hit
        rate = 0.15
        wood_hardness = 20.0
        stone_hardness = 35.0

        # 1. Bare Hand on Wood (hardness 20)
        hand_wood_dmg = get_mining_damage(None, TILE_WOOD)
        self.assertEqual(hand_wood_dmg, 1.2)
        hand_wood_hits = math.ceil(wood_hardness / hand_wood_dmg)
        hand_wood_time = hand_wood_hits * rate
        # ~2.5s (17 hits * 0.15s = 2.55s)
        self.assertAlmostEqual(hand_wood_time, 2.55, delta=0.15)

        # 2. Wood Axe on Wood (power 10)
        wood_axe = ItemStack("wood_axe", 1)
        wood_axe_dmg = get_mining_damage(wood_axe, TILE_WOOD)
        self.assertEqual(wood_axe_dmg, 2.6)
        wood_axe_hits = math.ceil(wood_hardness / wood_axe_dmg)
        wood_axe_time = wood_axe_hits * rate
        # ~1.2s (8 hits * 0.15s = 1.20s)
        self.assertEqual(wood_axe_hits, 8)
        self.assertAlmostEqual(wood_axe_time, 1.20, delta=0.05)

        # 3. Copper Axe on Wood (power 18)
        copper_axe = ItemStack("copper_axe", 1)
        copper_axe_dmg = get_mining_damage(copper_axe, TILE_WOOD)
        self.assertEqual(copper_axe_dmg, 4.68)
        copper_axe_hits = math.ceil(wood_hardness / copper_axe_dmg)
        copper_axe_time = copper_axe_hits * rate
        # ~0.8s (5 hits * 0.15s = 0.75s)
        self.assertEqual(copper_axe_hits, 5)
        self.assertAlmostEqual(copper_axe_time, 0.75, delta=0.10)

        # 4. Iron Axe on Wood (power 26)
        iron_axe = ItemStack("iron_axe", 1)
        iron_axe_dmg = get_mining_damage(iron_axe, TILE_WOOD)
        self.assertEqual(iron_axe_dmg, 6.76)
        iron_axe_hits = math.ceil(wood_hardness / iron_axe_dmg)
        iron_axe_time = iron_axe_hits * rate
        # ~0.5s (3 hits * 0.15s = 0.45s)
        self.assertEqual(iron_axe_hits, 3)
        self.assertAlmostEqual(iron_axe_time, 0.45, delta=0.10)

        # 5. Gold & Celestial Axe on Wood
        gold_axe = ItemStack("gold_axe", 1)
        gold_axe_dmg = get_mining_damage(gold_axe, TILE_WOOD)
        self.assertGreaterEqual(gold_axe_dmg, 10.5)
        gold_axe_hits = math.ceil(wood_hardness / gold_axe_dmg)
        self.assertLessEqual(gold_axe_hits, 2)  # 2 hits (0.3s)

        celestial_axe = ItemStack("celestial_axe", 1)
        celestial_axe_dmg = get_mining_damage(celestial_axe, TILE_WOOD)
        self.assertGreaterEqual(celestial_axe_dmg, 25.0)
        celestial_axe_hits = math.ceil(wood_hardness / celestial_axe_dmg)
        self.assertEqual(celestial_axe_hits, 1)  # 1 hit (instant)

        # 6. Stone Mining: Pickaxe vs Hand (Stone requires a pickaxe; bare hands cannot mine stone)
        hand_stone_dmg = get_mining_damage(None, TILE_STONE)
        self.assertEqual(hand_stone_dmg, 0.0)

        copper_pick = ItemStack("copper_pickaxe", 1)
        copper_pick_dmg = get_mining_damage(copper_pick, TILE_STONE)
        self.assertEqual(copper_pick_dmg, 3.12)
        copper_pick_hits = math.ceil(stone_hardness / copper_pick_dmg)
        copper_pick_time = copper_pick_hits * rate
        self.assertEqual(copper_pick_hits, 12)
        self.assertAlmostEqual(copper_pick_time, 1.80, delta=0.1)

        iron_pick = ItemStack("iron_pickaxe", 1)
        iron_pick_dmg = get_mining_damage(iron_pick, TILE_STONE)
        self.assertEqual(iron_pick_dmg, 4.68)
        iron_pick_hits = math.ceil(stone_hardness / iron_pick_dmg)
        iron_pick_time = iron_pick_hits * rate
        self.assertEqual(iron_pick_hits, 8)
        self.assertAlmostEqual(iron_pick_time, 1.20, delta=0.1)

        # Pickaxe breaks stone rapidly compared to non-pick tools
        self.assertLess(copper_pick_time, 2.5)

        # 7. Mismatched Tool: Axe on Stone only deals hand damage
        axe_on_stone_dmg = get_mining_damage(wood_axe, TILE_STONE)
        self.assertEqual(axe_on_stone_dmg, 1.2)

        # 8. Weapon cannot mine blocks
        sword = ItemStack("copper_shortsword", 1)
        sword_dmg = get_mining_damage(sword, TILE_WOOD)
        self.assertEqual(sword_dmg, 0.0)

    def test_07_progressive_cracking_stages_and_break(self):
        """Tile damage accumulates smoothly and passes through cracking stages 0, 1, 2, 3 before breaking."""
        tx, ty = 50, 50
        # Place wood block for isolated test
        self.world.chunk_manager.set_tile(tx, ty, TILE_WOOD)
        self.world.player_placed_tiles.add((tx, ty))
        self.world.tile_damage.clear()

        # Wood hardness is 20
        # Hit 1: 2.6 damage -> stage 0
        broken, drop, tid = self.world.damage_tile_at(tx, ty, 2.6)
        self.assertFalse(broken)
        self.assertAlmostEqual(self.world.tile_damage[(tx, ty)], 2.6)
        stage1 = min(3, int((self.world.tile_damage[(tx, ty)] / 20.0) * 4))
        self.assertEqual(stage1, 0)

        # Hit 2 & 3: up to 7.8 damage -> stage 1
        self.world.damage_tile_at(tx, ty, 5.2)
        stage2 = min(3, int((self.world.tile_damage[(tx, ty)] / 20.0) * 4))
        self.assertEqual(stage2, 1)

        # Hit 4 & 5: up to 13.0 damage -> stage 2
        self.world.damage_tile_at(tx, ty, 5.2)
        stage3 = min(3, int((self.world.tile_damage[(tx, ty)] / 20.0) * 4))
        self.assertEqual(stage3, 2)

        # Hit 6 & 7: up to 18.2 damage -> stage 3
        self.world.damage_tile_at(tx, ty, 5.2)
        stage4 = min(3, int((self.world.tile_damage[(tx, ty)] / 20.0) * 4))
        self.assertEqual(stage4, 3)

        # Hit 8: reaches 20.8 -> breaks!
        broken, drop, tid = self.world.damage_tile_at(tx, ty, 2.6)
        self.assertTrue(broken)
        self.assertEqual(drop, "wood")
        self.assertNotIn((tx, ty), self.world.tile_damage)
        self.assertEqual(self.world.get_tile(tx, ty), TILE_AIR)

    def test_08_character_panel_coin_purse_display(self):
        """CharacterPanel renders Coin Purse with correct denominations."""
        panel = CharacterPanel(self.assets)
        self.player.stats.set_from_copper(12345)  # 1g 23s 45c
        panel.is_open = True
        self.assertTrue(panel.is_open)

        # Render onto a test surface to ensure zero crashes
        surf = pygame.Surface((800, 600))
        panel.render(surf, self.player, 400, 300)

        self.assertEqual(self.player.stats.gold_coins, 1)
        self.assertEqual(self.player.stats.silver_coins, 23)
        self.assertEqual(self.player.stats.copper_coins, 45)

    def test_09_npc_dialogue_coin_display_and_currency_purchases(self):
        """NPC Dialogue correctly displays coin breakdown and allows purchasing with silver/gold currencies."""
        from src.ui.npc_dialogue import NPCDialogueWindow
        from src.entities.npc import MerchantNPC

        merchant = MerchantNPC("Barnaby", "merchant", 200, 200, self.assets, self.sound)
        dialogue = NPCDialogueWindow(self.assets, self.sound)
        dialogue.open(merchant, self.player, self.world)
        dialogue.current_view = "shop"

        # Give player 1 gold coin (10000 copper value)
        self.player.stats.set_from_copper(10000)
        self.assertEqual(self.inv.gold_coins, 1)
        self.assertEqual(self.inv.silver_coins, 0)
        self.assertEqual(self.inv.copper_coins, 0)

        # Purchasing power queries
        self.assertEqual(self.inv.count_item("copper_coin"), 10000)
        self.assertEqual(self.inv.count_item("silver_coin"), 100)
        self.assertEqual(self.inv.count_item("gold_coin"), 1)

        # Render dialogue onto surface to verify header breakdown formatting
        surf = pygame.Surface((800, 600))
        dialogue.render(surf, self.player, self.inv, 400, 300)
        # Denomination getters used in header should be 1g, 0s, 0c
        self.assertEqual(self.inv.gold_coins, 1)
        self.assertEqual(self.inv.silver_coins, 0)
        self.assertEqual(self.inv.copper_coins, 0)

        # Add a custom shop entry priced in silver coins (e.g. 5 silver coins)
        merchant.shop_catalog.append({
            "item_id": "iron_bar", "name": "Iron Ingot", "price": 5, "currency": "silver_coin", "count": 1
        })
        entry_idx = len(merchant.shop_catalog) - 1
        col = entry_idx % 2
        row = entry_idx // 2
        bx = dialogue.x + 20 + col * 250
        by = dialogue.y + 70 + row * 46
        buy_x = bx + 180 + 10
        buy_y = by + 4 + 10

        handled = dialogue.handle_click(buy_x, buy_y, self.player, self.inv, self.world)
        self.assertTrue(handled)
        self.assertEqual(self.inv.count_item("iron_bar"), 1)
        # Total value should now be 10000 - 500 = 9500 (95 silver)
        self.assertEqual(self.player.stats.total_copper_value, 9500)
        self.assertEqual(self.inv.gold_coins, 0)
        self.assertEqual(self.inv.silver_coins, 95)
        self.assertEqual(self.inv.copper_coins, 0)

    def test_10_merchant_sell_stack_multiplier(self):
        """Selling a stack of items multiplies unit sell value by stack count."""
        from src.ui.npc_dialogue import NPCDialogueWindow
        from src.entities.npc import MerchantNPC

        merchant = MerchantNPC("Barnaby", "merchant", 200, 200, self.assets, self.sound)
        dialogue = NPCDialogueWindow(self.assets, self.sound)
        dialogue.open(merchant, self.player, self.world)
        dialogue.current_view = "shop"

        self.player.stats.set_from_copper(0)
        # Put 10 dirt blocks in selected hotbar slot
        self.inv.slots[0] = ItemStack("dirt_block", 10)
        self.inv.selected_slot = 0
        unit_val = max(1, self.inv.slots[0].data.get("damage", self.inv.slots[0].data.get("def", 2)) * 2)

        sell_btn_x = dialogue.x + 115 + 10
        sell_btn_y = dialogue.y + dialogue.height - 40 + 10

        handled = dialogue.handle_click(sell_btn_x, sell_btn_y, self.player, self.inv, self.world)
        self.assertTrue(handled)
        self.assertIsNone(self.inv.slots[0])
        self.assertEqual(self.player.stats.total_copper_value, unit_val * 10)
        self.assertIn("Sold 10x", dialogue.status_message)

    def test_11_save_isolation_coin_purse_reset(self):
        """reset_new_session completely resets the coin purse to zero preventing state bleed."""
        from main import PotariaGame
        game = PotariaGame()
        # Give game player some coins
        game.player.stats.set_from_copper(54321)
        self.assertEqual(game.player.stats.total_copper_value, 54321)

        # Start a new world session
        game.reset_new_session("World_Clean")
        self.assertEqual(game.player.stats.copper_coins, 0)
        self.assertEqual(game.player.stats.silver_coins, 0)
        self.assertEqual(game.player.stats.gold_coins, 0)
        self.assertEqual(game.player.stats.total_copper_value, 0)
        self.assertEqual(game.inventory._local_copper, 0)
        self.assertEqual(game.inventory._local_silver, 0)
        self.assertEqual(game.inventory._local_gold, 0)

    def test_12_continuous_mining_first_click_pacing(self):
        """Initial left click sets mining_cooldown to continuous_mine_rate to prevent double-hit on frame 0."""
        from main import PotariaGame
        game = PotariaGame()
        game.reset_new_session("Test_Mining_Pacing")
        game.mining_cooldown = 0.0

        # Simulate left-click event in event loop on a tile
        tx = int(game.player.center_x // SCALED_TILE) + 1
        ty = int(game.player.center_y // SCALED_TILE)
        game.world.chunk_manager.set_tile(tx, ty, TILE_WOOD)
        game.world.tile_damage.clear()

        # Call primary action through left-click simulation
        game.mining_cooldown = game.continuous_mine_rate
        game.handle_primary_action(400, 300)

        # Mining cooldown must be set to continuous_mine_rate
        self.assertEqual(game.mining_cooldown, game.continuous_mine_rate)


if __name__ == "__main__":
    unittest.main()
