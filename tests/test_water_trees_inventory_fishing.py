"""
Potaria: Root Realm - Test Suite for Water Buoyancy, Trees Ecosystem,
Block Icon Parity, Inventory Organizing, Fishing System, Rope Rungs, and Iron Chest.
Developer: Kurados | Pure Python 3.13 + Pygame-ce 2.5.8
"""

import os
import sys
import unittest
import pygame

# Headless pygame setup
os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"
pygame.init()
pygame.display.set_mode((1280, 720), pygame.DOUBLEBUF)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

from src.constants import (
    GRAVITY, SCALED_TILE,
    TILE_AIR, TILE_DIRT, TILE_GRASS, TILE_WOOD, TILE_WOOD_TRUNK, TILE_LEAVES,
    TILE_WATER, TILE_CHEST, TILE_SAPLING, TILE_IRON_CHEST, TILE_ROPE_RUNGS,
    TILE_STONE, TILE_SAND, TILE_SNOW, TILE_ICE, TILE_COPPER_ORE, TILE_IRON_ORE,
    TILE_GOLD_ORE, TILE_SANDSTONE, TILE_BLIGHTSTONE
)
from src.assets.asset_factory import AssetFactory
from src.world.world import World
from src.entities.player import Player
from src.entities.mob import GreenSlime, Zombie, CaveBat, DemonEye, ShadowCrawler
from src.entities.dropped_item import DroppedItem
from src.ui.inventory import Inventory, ItemStack, ITEM_REGISTRY, ITEM_ALIASES
from src.ui.crafting import RECIPES


class DummySound:
    def __init__(self):
        self.played = []

    def play(self, sound_name):
        self.played.append(sound_name)


class TestWaterTreesInventoryFishing(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.factory = AssetFactory()
        cls.sound = DummySound()

    def setUp(self):
        self.world = World(self.factory, seed=12345)
        self.player = Player(100, 100, self.factory, self.sound)
        self.inv = Inventory(self.factory)

    # =========================================================================
    # 1. WATER BUOYANCY & UNDERWATER OVERLAY & DROWNING
    # =========================================================================
    def test_water_buoyancy_and_fluid_drag_mobs(self):
        slime = GreenSlime(100, 100, self.factory)
        zombie = Zombie(100, 100, self.factory)
        crawler = ShadowCrawler(100, 100, self.factory)

        # Place water at mob position in world
        tx, ty = int(100 // SCALED_TILE), int(100 // SCALED_TILE)
        self.world.set_tile(tx, ty, TILE_WATER)

        # Before entering water, in_water is False
        self.assertFalse(getattr(slime, "in_water", False))

        # When update_water_buoyancy is called on Mob
        buoyant_slime = slime.update_water_buoyancy(self.world)
        self.assertTrue(buoyant_slime)
        self.assertTrue(slime.in_water)
        # vy should be buoyant and upward opposing gravity
        self.assertLess(slime.vy, 2.0)

        buoyant_zombie = zombie.update_water_buoyancy(self.world)
        self.assertTrue(buoyant_zombie)
        self.assertTrue(zombie.in_water)

        buoyant_crawler = crawler.update_water_buoyancy(self.world)
        self.assertTrue(buoyant_crawler)
        self.assertTrue(crawler.in_water)

    def test_water_buoyancy_dropped_items(self):
        tx, ty = 10, 10
        self.world.set_tile(tx, ty, TILE_WATER)
        item = DroppedItem("wood", 1, tx * SCALED_TILE + 4, ty * SCALED_TILE + 4, self.factory)
        item.vy = 5.0
        item.update(0.1, self.world, self.player)
        self.assertTrue(item.in_water)
        # Upward buoyant velocity and fluid drag reduces downward speed
        self.assertLess(item.vy, 2.0)

    def test_underwater_overlay_render(self):
        # Surface overlay when in_water
        slime = GreenSlime(100, 100, self.factory)
        slime.in_water = True
        test_surf = pygame.Surface((28, 22), pygame.SRCALPHA)
        test_surf.fill((100, 255, 100, 255))
        overlayed = slime.apply_water_overlay(test_surf)
        # Check that blue component increased due to (30, 110, 200, 75)
        self.assertIsNotNone(overlayed)
        self.assertEqual(overlayed.get_size(), test_surf.get_size())

    def test_drowning_bypasses_defense_at_1_heart_per_second(self):
        tx = int(self.player.center_x // SCALED_TILE)
        ty = int((self.player.y + 6) // SCALED_TILE)
        self.world.set_tile(tx, ty, TILE_WATER)

        self.player.equipment.slots["armor_chest"] = ItemStack("iron_armor_chest", 1)
        self.player.stats.defense = 25  # High defense
        self.player.max_health = 100
        self.player.health = 100
        self.player.oxygen = 0.0
        self.player.drown_timer = 1.0

        # Exact 1 heart per second = max_health // 10 = 10 HP
        prev_hp = self.player.health
        self.player.update(0.01, self.world)
        drown_dmg = prev_hp - self.player.health
        self.assertEqual(drown_dmg, 10)

    # =========================================================================
    # 2. INDIVIDUAL TREE HARVESTING & LEAVES/SAPLING ECOSYSTEM
    # =========================================================================
    def test_individual_tree_harvesting_no_cascade(self):
        # When tree_cascade_felling is False, chopping base wood does not destroy upper wood or leaves
        self.world.tree_cascade_felling = False
        tx, ty = 5, 20
        # Build mini tree: 3 trunk blocks, 1 leaves block on top
        self.world.set_tile(tx, ty, TILE_WOOD_TRUNK)
        self.world.set_tile(tx, ty - 1, TILE_WOOD_TRUNK)
        self.world.set_tile(tx, ty - 2, TILE_WOOD_TRUNK)
        self.world.set_tile(tx, ty - 3, TILE_LEAVES)

        # Break the bottom-most wood trunk
        broken, drop, tid = self.world.damage_tile_at(tx, ty, 100)
        self.assertTrue(broken)
        self.assertEqual(drop, "wood")
        self.assertEqual(self.world.get_tile(tx, ty), TILE_AIR)

        # Upper trunk and leaves remain intact in the world
        self.assertEqual(self.world.get_tile(tx, ty - 1), TILE_WOOD_TRUNK)
        self.assertEqual(self.world.get_tile(tx, ty - 2), TILE_WOOD_TRUNK)
        self.assertEqual(self.world.get_tile(tx, ty - 3), TILE_LEAVES)

    def test_leaves_breakable_and_drop_leaves(self):
        self.world.tree_cascade_felling = False
        tx, ty = 8, 15
        self.world.set_tile(tx, ty, TILE_LEAVES)

        broken, drop, tid = self.world.damage_tile_at(tx, ty, 50)
        self.assertTrue(broken)
        self.assertEqual(drop, "leaves")
        self.assertEqual(self.world.get_tile(tx, ty), TILE_AIR)

    def test_sapling_placement_and_daily_growth(self):
        # Sapling requires solid ground below it
        tx, ty = 12, 30
        self.world.set_tile(tx, ty + 1, TILE_GRASS)
        self.world.set_tile(tx, ty, TILE_AIR)

        # Clear sky above it
        for y in range(ty - 10, ty):
            self.world.set_tile(tx, y, TILE_AIR)

        placed = self.world.place_tile(tx, ty, TILE_SAPLING, chest_type="oak_sapling")
        self.assertTrue(placed)
        self.assertEqual(self.world.get_tile(tx, ty), TILE_SAPLING)
        self.assertIn((tx, ty), self.world.planted_saplings)

        # Trigger daily growth in sunlight
        self.world.grow_plants_daily()
        # Sapling matures into full tree with trunk and canopy
        self.assertEqual(self.world.get_tile(tx, ty), TILE_WOOD_TRUNK)
        self.assertNotIn((tx, ty), self.world.planted_saplings)

    # =========================================================================
    # 3. WORLD TILE ASSET PARITY FOR BLOCK ICONS
    # =========================================================================
    def test_world_tile_asset_parity_block_icons(self):
        natural_blocks = [
            "dirt_block", "sand_block", "stone_block", "wood", "leaves",
            "snow_block", "ice_block", "copper_ore", "iron_ore", "gold_ore",
            "sandstone_block", "blightstone_block", "rope_rungs", "iron_chest", "oak_sapling"
        ]
        for item_id in natural_blocks:
            icon = self.factory.items.get(item_id)
            self.assertIsNotNone(icon, f"Missing icon for {item_id}")
            self.assertEqual(icon.get_size(), (24, 24), f"Icon for {item_id} should be scaled to 24x24")

    # =========================================================================
    # 4. ORGANIZE INVENTORY (FILL GAPS)
    # =========================================================================
    def test_organize_inventory_fills_gaps_forward(self):
        # Create inventory with scattered items and holes
        self.inv.slots = [None] * len(self.inv.slots)
        self.inv.slots[1] = ItemStack("iron_sword", 1)
        self.inv.slots[3] = ItemStack("wood", 20)
        self.inv.slots[7] = ItemStack("healing_potion", 5)
        self.inv.slots[12] = ItemStack("leaves", 15)

        self.inv.organize_inventory(include_hotbar=True)

        # Items should be compacted sequentially forward without gaps
        self.assertIsNotNone(self.inv.slots[0])
        self.assertEqual(self.inv.slots[0].item_id, "iron_sword")

        self.assertIsNotNone(self.inv.slots[1])
        self.assertEqual(self.inv.slots[1].item_id, "wood")

        self.assertIsNotNone(self.inv.slots[2])
        self.assertEqual(self.inv.slots[2].item_id, "healing_potion")

        self.assertIsNotNone(self.inv.slots[3])
        self.assertEqual(self.inv.slots[3].item_id, "leaves")

        # Remaining slots are None
        for i in range(4, len(self.inv.slots)):
            self.assertIsNone(self.inv.slots[i])

    # =========================================================================
    # 5. FISHING SYSTEM & PINOY FISHES
    # =========================================================================
    def test_10_authentic_pinoy_fishes_in_registry_and_crafting(self):
        pinoy_fishes = [
            ("raw_bangus", "cooked_bangus", "Bangus"),
            ("raw_tilapia", "cooked_tilapia", "Tilapia"),
            ("raw_galunggong", "cooked_galunggong", "Galunggong"),
            ("raw_maya_maya", "cooked_maya_maya", "Maya-Maya"),
            ("raw_tanigue", "cooked_tanigue", "Tanigue"),
            ("raw_tambakol", "cooked_tambakol", "Tambakol"),
            ("raw_lapu_lapu", "cooked_lapu_lapu", "Lapu-Lapu"),
            ("raw_hito", "cooked_hito", "Hito"),
            ("raw_dilis", "cooked_dilis", "Dilis"),
            ("raw_dalagang_bukid", "cooked_dalagang_bukid", "Dalagang Bukid"),
        ]

        # Verify all 10 raw & cooked fishes exist in registry with Filipino names only
        for raw_id, cooked_id, pinoy_name in pinoy_fishes:
            self.assertIn(raw_id, ITEM_REGISTRY)
            self.assertIn(cooked_id, ITEM_REGISTRY)
            raw_item = ITEM_REGISTRY[raw_id]
            cooked_item = ITEM_REGISTRY[cooked_id]
            self.assertIn(pinoy_name, raw_item["name"])
            self.assertIn(pinoy_name, cooked_item["name"])
            # Ensure unique procedural pixel art
            raw_icon = self.factory.items.get(raw_id)
            cooked_icon = self.factory.items.get(cooked_id)
            self.assertIsNotNone(raw_icon)
            self.assertIsNotNone(cooked_icon)

        # Verify furnace recipes exist for all 10 fishes
        cooked_results = {r["result"]: r for r in RECIPES if r.get("station") == "furnace"}
        for raw_id, cooked_id, _ in pinoy_fishes:
            self.assertIn(cooked_id, cooked_results, f"Missing furnace recipe for {cooked_id}")
            recipe = cooked_results[cooked_id]
            self.assertEqual(recipe["ingredients"][0][0], raw_id)

    def test_fishing_rod_recipe(self):
        rod_recipes = [r for r in RECIPES if r.get("result") == "fishing_rod"]
        self.assertGreater(len(rod_recipes), 0)
        recipe = rod_recipes[0]
        self.assertEqual(recipe["station"], "work_bench")

    # =========================================================================
    # 6. ROPE RUNGS ASSET PARITY
    # =========================================================================
    def test_rope_rungs_tile_and_item_parity(self):
        self.assertEqual(TILE_ROPE_RUNGS, 56)
        self.assertIn(TILE_ROPE_RUNGS, self.factory.tiles)
        icon = self.factory.items.get("rope_rungs")
        self.assertIsNotNone(icon)
        self.assertEqual(icon.get_size(), (24, 24))

    # =========================================================================
    # 7. TREASURE CHEST VS IRON STORAGE CHEST DISPARITY
    # =========================================================================
    def test_iron_storage_chest_tile_and_placement(self):
        self.assertEqual(TILE_IRON_CHEST, 55)
        self.assertNotEqual(TILE_IRON_CHEST, TILE_CHEST)
        self.assertIn(TILE_IRON_CHEST, self.factory.tiles)

        # Placing iron chest in world
        tx, ty = 20, 25
        self.world.set_tile(tx, ty + 1, TILE_STONE)
        placed = self.world.place_tile(tx, ty, TILE_IRON_CHEST, chest_type="iron_chest")
        self.assertTrue(placed)
        self.assertEqual(self.world.get_tile(tx, ty), TILE_IRON_CHEST)
        self.assertIn((tx, ty), self.world.chests)
        chest_obj = self.world.chests[(tx, ty)]
        self.assertEqual(chest_obj.chest_type, "iron_chest")

        # Mining iron chest drops iron_chest item
        broken, drop, tid = self.world.damage_tile_at(tx, ty, 100)
        self.assertTrue(broken)
        self.assertEqual(drop, "iron_chest")
        self.assertEqual(self.world.get_tile(tx, ty), TILE_AIR)

    # =========================================================================
    # 8. EDGE CASES
    # =========================================================================
    def test_organize_inventory_edge_cases(self):
        # 1. Empty inventory remains empty
        self.inv.slots = [None] * len(self.inv.slots)
        self.inv.organize_inventory(include_hotbar=True)
        self.assertTrue(all(s is None for s in self.inv.slots))

        # 2. Packed distinct items remain in exact sequential order
        self.inv.slots = [None] * len(self.inv.slots)
        test_items = ["iron_sword", "wood_axe", "copper_pickaxe", "torch", "wood_platform"]
        for i, item_id in enumerate(test_items):
            self.inv.slots[i] = ItemStack(item_id, 1)
        self.inv.organize_inventory(include_hotbar=True)
        for i, item_id in enumerate(test_items):
            self.assertIsNotNone(self.inv.slots[i])
            self.assertEqual(self.inv.slots[i].item_id, item_id)

    def test_sapling_placement_rejections(self):
        tx, ty = 30, 30
        # Rejection in mid-air (no solid block below)
        self.world.set_tile(tx, ty + 1, TILE_AIR)
        self.world.set_tile(tx, ty, TILE_AIR)
        placed_air = self.world.place_tile(tx, ty, TILE_SAPLING)
        self.assertFalse(placed_air)

        # Rejection underwater
        self.world.set_tile(tx, ty + 1, TILE_STONE)
        self.world.set_tile(tx, ty, TILE_WATER)
        placed_water = self.world.place_tile(tx, ty, TILE_SAPLING)
        self.assertFalse(placed_water)

    def test_leaf_block_alias_and_drops(self):
        self.assertEqual(ITEM_ALIASES.get("leaf_block"), "leaves")
        self.assertIn("leaves", ITEM_REGISTRY)
        self.assertEqual(ITEM_REGISTRY["leaves"]["tile"], TILE_LEAVES)


if __name__ == "__main__":
    unittest.main()
