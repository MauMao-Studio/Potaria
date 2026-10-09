"""
Potaria - Comprehensive House Furniture & Decoration Verification Test Suite
Developer: Kurados
Engine: Pure Python + pygame-ce (100% offline)

Verifies:
1. Tile IDs and TILE_PROPS for all 13 furniture items/blocks
2. ITEM_REGISTRY and ITEM_ALIASES metadata, descriptions, and lore
3. Pixel art synthesis for 16x16 block tiles and 24x24 inventory icons
4. Crafting recipes for Work Bench and Furnace stations
5. Non-solid placement permitting player rect overlap
6. One-way platform physics (jump through from below, stand on top)
7. Wooden Bed interaction, spawn point setting, resting HP regen, damage wake-up, and respawn
8. Grandfather Clock 12-hour AM/PM time calculation and interaction
9. Stone Fireplace tracking, smoke & ember emission, and ambient light emission
10. Room shelter validation with fireplace, candelabra, and chandelier light sources
11. Persistence of custom bed spawn points across world saves and loads
"""

import os
import sys
import math
import shutil
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"

import pygame
from src.constants import (
    SCREEN_WIDTH, SCREEN_HEIGHT, SCALED_TILE,
    TILE_AIR, TILE_DIRT, TILE_STONE, TILE_WOOD, TILE_TORCH,
    TILE_WORK_BENCH, TILE_FURNACE, TILE_DOOR_CLOSED,
    TILE_BED, TILE_BOOKSHELF, TILE_GRANDFATHER_CLOCK, TILE_FIREPLACE,
    TILE_CANDELABRA, TILE_CHANDELIER, TILE_POTTED_PLANT, TILE_DRESSER,
    TILE_TAPESTRY, TILE_BATHTUB, TILE_SINK, TILE_PAINTING, TILE_WOOD_SHELF,
    TILE_PROPS, WALL_WOOD, WALL_STONE_BRICK
)
from src.assets.asset_factory import AssetFactory
from src.audio.sound_effects import SoundManager
from src.world.world import World
from src.world.lighting import LightingEngine
from src.entities.player import Player
from src.entities.particle import ParticleSystem
from src.environment.sky import DayNightCycle
from src.ui.inventory import Inventory, ItemStack, ITEM_REGISTRY, ITEM_ALIASES
from src.ui.crafting import CraftingSystem
from src.world.save_manager import save_world, load_world, delete_world
from main import PotariaGame

FURNITURE_TILES = [
    TILE_BED, TILE_BOOKSHELF, TILE_GRANDFATHER_CLOCK, TILE_FIREPLACE,
    TILE_CANDELABRA, TILE_CHANDELIER, TILE_POTTED_PLANT, TILE_DRESSER,
    TILE_TAPESTRY, TILE_BATHTUB, TILE_SINK, TILE_PAINTING, TILE_WOOD_SHELF
]

FURNITURE_ITEM_IDS = [
    "wooden_bed", "bookshelf", "grandfather_clock", "stone_fireplace",
    "candelabra", "chandelier", "potted_plant", "wooden_dresser",
    "wall_tapestry", "bathtub", "sink", "painting", "wood_shelf"
]

class TestFurnitureSystem(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pygame.init()
        cls.factory = AssetFactory()
        cls.sound = SoundManager()

    def test_01_tile_constants_and_properties(self):
        """Verifies all 13 furniture tiles have correct IDs, hardness, drops, and solid/platform flags."""
        expected_ids = {
            TILE_BED: 38,
            TILE_BOOKSHELF: 39,
            TILE_GRANDFATHER_CLOCK: 40,
            TILE_FIREPLACE: 41,
            TILE_CANDELABRA: 42,
            TILE_CHANDELIER: 43,
            TILE_POTTED_PLANT: 44,
            TILE_DRESSER: 45,
            TILE_TAPESTRY: 46,
            TILE_BATHTUB: 47,
            TILE_SINK: 48,
            TILE_PAINTING: 49,
            TILE_WOOD_SHELF: 50
        }
        for tile_const, expected_val in expected_ids.items():
            self.assertEqual(tile_const, expected_val)

        for tid in FURNITURE_TILES:
            self.assertIn(tid, TILE_PROPS, f"Tile ID {tid} missing in TILE_PROPS")
            props = TILE_PROPS[tid]
            self.assertGreater(props.get("hardness", 0), 0)
            self.assertIsNotNone(props.get("drop"))
            self.assertFalse(props.get("solid", True), f"Tile {tid} should not be solid")
            self.assertFalse(props.get("opaque", True), f"Tile {tid} should be transparent to light")

        # Specific platform properties
        platforms = [TILE_WOOD_SHELF, TILE_BED, TILE_BOOKSHELF, TILE_FIREPLACE, TILE_DRESSER, TILE_BATHTUB, TILE_SINK]
        for tid in platforms:
            self.assertTrue(TILE_PROPS[tid].get("platform"), f"Tile {tid} should be a platform")

        # Specific light emitters
        self.assertEqual(TILE_PROPS[TILE_FIREPLACE].get("light_emit"), 13)
        self.assertEqual(TILE_PROPS[TILE_CHANDELIER].get("light_emit"), 14)
        self.assertEqual(TILE_PROPS[TILE_CANDELABRA].get("light_emit"), 12)
        self.assertEqual(TILE_PROPS[TILE_POTTED_PLANT].get("light_emit"), 2)

    def test_02_item_registry_and_aliases(self):
        """Verifies all 13 items are registered in ITEM_REGISTRY and alias resolution works."""
        inv = Inventory(self.factory)
        for item_id in FURNITURE_ITEM_IDS:
            self.assertIn(item_id, ITEM_REGISTRY)
            data = ITEM_REGISTRY[item_id]
            self.assertIn("name", data)
            self.assertIn("desc", data)
            self.assertIn("lore", data)
            self.assertIn("cat", data)
            self.assertIn("rarity", data)
            self.assertIn("tile", data)
            self.assertIn(data["tile"], FURNITURE_TILES)

        # Check aliases
        aliases_to_test = {
            "bed": "wooden_bed",
            "fireplace": "stone_fireplace",
            "hearth": "stone_fireplace",
            "clock": "grandfather_clock",
            "potted_spud_plant": "potted_plant",
            "bonsai": "potted_plant",
            "dresser": "wooden_dresser",
            "wardrobe": "wooden_dresser",
            "tapestry": "wall_tapestry",
            "banner": "wall_tapestry",
            "wall_art": "painting",
            "shelf": "wood_shelf"
        }
        for alias, formal in aliases_to_test.items():
            self.assertEqual(ITEM_ALIASES.get(alias), formal, f"Alias '{alias}' did not resolve to '{formal}'")
            resolved_data = inv.get_item_data(alias)
            self.assertEqual(resolved_data, ITEM_REGISTRY[formal])

    def test_03_pixel_art_tile_and_item_generation(self):
        """Verifies 16x16 tile textures and 24x24 item sprites are synthesized with valid pixels."""
        for tid in FURNITURE_TILES:
            self.assertIn(tid, self.factory.tiles, f"Tile {tid} missing in asset_factory.tiles")
            surf = self.factory.tiles[tid]
            self.assertIsInstance(surf, pygame.Surface)
            self.assertEqual(surf.get_size(), (16, 16))
            mask = pygame.mask.from_surface(surf)
            self.assertGreater(mask.count(), 10, f"Tile {tid} sprite has too few non-transparent pixels")

        for item_id in FURNITURE_ITEM_IDS:
            self.assertIn(item_id, self.factory.items, f"Item '{item_id}' missing in asset_factory.items")
            surf = self.factory.items[item_id]
            self.assertIsInstance(surf, pygame.Surface)
            self.assertEqual(surf.get_size(), (24, 24))
            mask = pygame.mask.from_surface(surf)
            self.assertGreater(mask.count(), 10, f"Item '{item_id}' icon has too few non-transparent pixels")

    def test_04_crafting_recipes_discovery_and_craft(self):
        """Verifies crafting recipes for Work Bench and Furnace stations."""
        crafting = CraftingSystem(self.factory, self.sound)
        inv = Inventory(self.factory, difficulty="hardcore")
        world = World(self.factory, seed=123)
        player = Player(100, 100, self.factory, self.sound)

        # Place a workbench and furnace adjacent to player
        tx = int(player.center_x // SCALED_TILE)
        ty = int(player.center_y // SCALED_TILE)
        world.set_tile(tx - 1, ty, TILE_WORK_BENCH)
        world.set_tile(tx + 1, ty, TILE_FURNACE)

        crafting.update_recipes(inv, world, player)
        available_results = [r["result"] for r in crafting.available_recipes]

        for item_id in FURNITURE_ITEM_IDS:
            self.assertIn(item_id, available_results, f"Recipe for '{item_id}' not found in available recipes")

        # Test crafting wooden bed with ingredients: 12 wood, 4 spud_sap
        bed_rec = next(r for r in crafting.available_recipes if r["result"] == "wooden_bed")
        self.assertFalse(bed_rec["can_craft"])
        self.assertFalse(crafting.craft(bed_rec, inv))

        # Add materials for bed: 12 wood, 4 spud_sap
        inv.add_item("wood", 20)
        inv.add_item("spud_sap", 10)
        crafting.update_recipes(inv, world, player)
        bed_rec = next(r for r in crafting.available_recipes if r["result"] == "wooden_bed")
        self.assertTrue(bed_rec["can_craft"])
        crafted = crafting.craft(bed_rec, inv)
        self.assertTrue(crafted)
        self.assertEqual(inv.count_item("wooden_bed"), 1)
        self.assertEqual(inv.count_item("wood"), 8)
        self.assertEqual(inv.count_item("spud_sap"), 6)

    def test_05_world_placement_and_drops(self):
        """Verifies placement and mining drops for furniture."""
        world = World(self.factory, seed=123)
        tx, ty = 10, 50

        # Ensure ground below for support
        world.set_tile(tx, ty + 1, TILE_WOOD)
        world.set_tile(tx, ty, TILE_AIR)

        placed = world.place_tile(tx, ty, TILE_BED)
        self.assertTrue(placed)
        self.assertEqual(world.get_tile(tx, ty), TILE_BED)

        # Mine the bed
        broken, drop, old_tid = world.damage_tile_at(tx, ty, 50)
        self.assertTrue(broken)
        self.assertEqual(drop, "wooden_bed")
        self.assertEqual(world.get_tile(tx, ty), TILE_AIR)

    def test_06_one_way_platform_mechanics(self):
        """Verifies shelf and furniture one-way platform jump-through and landing physics."""
        world = World(self.factory, seed=123)
        player = Player(100, 100, self.factory, self.sound)

        shelf_tx = 5
        shelf_ty = 10
        world.set_tile(shelf_tx, shelf_ty, TILE_WOOD_SHELF)

        shelf_rect = pygame.Rect(shelf_tx * SCALED_TILE, shelf_ty * SCALED_TILE, SCALED_TILE, SCALED_TILE)
        solids = world.get_solid_rects_in_bounds(shelf_rect)
        self.assertTrue(any(rect == shelf_rect and is_plat for rect, is_plat in solids))

        # 1. Jumping up from below through the shelf: player.vy < 0 should not be blocked
        player.x = shelf_rect.left
        player.y = shelf_rect.bottom + 5
        player.vy = -6.0
        player.on_ground = False
        player.update(0.016, world)
        self.assertLess(player.vy, 0.0)

        # 2. Falling downward onto the shelf: player lands on top
        player.x = shelf_rect.left
        player.y = shelf_rect.top - player.height + 2
        player.vy = 2.0
        player.update(0.016, world)
        self.assertTrue(player.on_ground)
        self.assertAlmostEqual(player.y, shelf_rect.top - player.height, delta=1.0)

    def test_07_wooden_bed_resting_and_respawn(self):
        """Verifies setting bed spawn point, resting HP regeneration, damage wake-up, and respawn."""
        game = PotariaGame()
        game.player.health = 50
        game.player.stats.hp = 50
        game.player.stats.base_max_hp = 100

        tx, ty = 15, 30
        game.world.set_tile(tx, ty, TILE_BED)
        tile_wx = tx * SCALED_TILE
        tile_wy = ty * SCALED_TILE

        # Move player close to bed
        game.player.x = tile_wx
        game.player.y = tile_wy - SCALED_TILE
        game.sky.time = 0.75 * game.sky.cycle_duration  # Bed sleep requires night

        # Right-click bed
        screen_x, screen_y = game.camera.world_to_screen(tile_wx + 16, tile_wy + 16)
        game.handle_right_click(screen_x, screen_y)

        # Check spawn point updated and player is resting
        self.assertEqual(game.player.spawn_point, (tile_wx, tile_wy - SCALED_TILE))
        self.assertEqual(game.world.spawn_point, (tile_wx, tile_wy - SCALED_TILE))
        self.assertTrue(game.player.is_resting)
        self.assertEqual(game.player.resting_bed_pos, (tx, ty))

        # Advance time to trigger resting HP healing (+4 HP every 0.5s)
        initial_hp = game.player.health
        game.player.update(0.55, game.world)
        self.assertEqual(game.player.health, initial_hp + 4)

        # Taking damage wakes player up
        game.player.take_damage(5)
        self.assertFalse(game.player.is_resting)

        # Test respawn at bed spawn point
        game.player.health = 0
        game.player.is_dead = True
        game.player.respawn_timer = 0.0
        game.player.x = 9999
        game.player.y = 9999
        game.player.update(0.1, game.world)
        self.assertFalse(game.player.is_dead)
        self.assertEqual((game.player.x, game.player.y), (tile_wx, tile_wy - SCALED_TILE))

    def test_08_grandfather_clock_time_interaction(self):
        """Verifies Grandfather Clock time calculation and interaction banner."""
        sky = DayNightCycle(self.factory)
        sky.time = 0.0 * sky.cycle_duration
        self.assertEqual(sky.get_time_string(), "6:00 AM (Day)")

        sky.time = 0.25 * sky.cycle_duration
        self.assertEqual(sky.get_time_string(), "12:00 PM (Day)")

        sky.time = 0.55 * sky.cycle_duration
        self.assertEqual(sky.get_time_string(), "7:12 PM (Night)")

        sky.time = 0.75 * sky.cycle_duration
        self.assertEqual(sky.get_time_string(), "12:00 AM (Night)")

        game = PotariaGame()
        tx, ty = 20, 30
        game.world.set_tile(tx, ty, TILE_GRANDFATHER_CLOCK)
        tile_wx = tx * SCALED_TILE
        tile_wy = ty * SCALED_TILE
        game.player.x = tile_wx
        game.player.y = tile_wy

        game.sky.time = 0.25 * game.sky.cycle_duration
        screen_x, screen_y = game.camera.world_to_screen(tile_wx + 16, tile_wy + 16)
        game.handle_right_click(screen_x, screen_y)
        self.assertIn("Grandfather Clock: 12:00 PM (Day)", game.inventory.last_learned_message)

    def test_09_stone_fireplace_smoke_and_lighting(self):
        """Verifies fireplace registration, smoke particle emission, and ambient light."""
        world = World(self.factory, seed=123)
        particle_system = ParticleSystem()
        tx, ty = 12, 40

        # Setting fireplace tile registers in world.fireplaces
        world.set_tile(tx, ty, TILE_FIREPLACE)
        self.assertIn((tx, ty), world.fireplaces)

        # Emit fireplace smoke
        initial_particle_count = len(particle_system.particles)
        cam_rect = pygame.Rect(0, 0, 5000, 5000)
        # Run several iterations to ensure randomized smoke/embers trigger
        for _ in range(25):
            world.emit_fireplace_smoke(particle_system, cam_rect)
        self.assertGreater(len(particle_system.particles), initial_particle_count)

        # Removing fireplace unregisters from world.fireplaces
        world.set_tile(tx, ty, TILE_AIR)
        self.assertNotIn((tx, ty), world.fireplaces)

    def test_10_shelter_validation_with_furniture(self):
        """Verifies that fireplace, candelabra, and chandelier qualify as light sources in shelter checks."""
        world = World(self.factory, seed=123)
        center_x, center_y = 50, 50

        # Construct enclosed room with background walls and a door
        for dx in range(-2, 3):
            for dy in range(-2, 3):
                world.set_wall(center_x + dx, center_y + dy, WALL_WOOD)

        world.set_tile(center_x - 2, center_y, TILE_DOOR_CLOSED)

        # Test fireplace
        world.set_tile(center_x, center_y, TILE_FIREPLACE)
        self.assertTrue(world.check_shelter(center_x, center_y))

        # Test candelabra
        world.set_tile(center_x, center_y, TILE_CANDELABRA)
        self.assertTrue(world.check_shelter(center_x, center_y))

        # Test chandelier
        world.set_tile(center_x, center_y, TILE_CHANDELIER)
        self.assertTrue(world.check_shelter(center_x, center_y))

    def test_11_save_load_bed_spawn_point_persistence(self):
        """Verifies that bed spawn points persist through save and load."""
        game = PotariaGame()
        test_save_name = "Test_Furniture_Bed_Save"

        bed_spawn = (450.0, 680.0)
        game.player.spawn_point = bed_spawn
        game.world.spawn_point = bed_spawn

        save_world(test_save_name, game)

        # Reset game player spawn point
        game.player.spawn_point = (100.0, 100.0)
        game.world.spawn_point = (100.0, 100.0)

        # Load world
        loaded = load_world(test_save_name, game)
        self.assertTrue(loaded)
        self.assertEqual(game.player.spawn_point, bed_spawn)
        self.assertEqual(game.world.spawn_point, bed_spawn)

        # Cleanup test save
        delete_world(test_save_name)

    def test_12_non_solid_placement_overlap(self):
        """Verifies solid blocks are blocked by player hitbox but non-solid furniture can be placed."""
        game = PotariaGame()
        tx = int(game.player.center_x // SCALED_TILE)
        ty = int(game.player.center_y // SCALED_TILE)
        game.world.set_tile(tx, ty, TILE_AIR)
        game.world.set_tile(tx, ty + 1, TILE_DIRT)

        screen_x, screen_y = game.camera.world_to_screen(tx * SCALED_TILE + 16, ty * SCALED_TILE + 16)

        # 1. Solid block (stone_block): placement is blocked by player rect
        game.inventory.slots[0] = ItemStack("stone_block", 10)
        game.inventory.selected_slot = 0
        game.handle_block_placement(screen_x, screen_y, game.inventory.slots[0])
        self.assertEqual(game.world.get_tile(tx, ty), TILE_AIR)
        self.assertEqual(game.inventory.slots[0].count, 10)

        # 2. Non-solid furniture (wooden_bed): placement succeeds through player rect
        game.inventory.slots[0] = ItemStack("wooden_bed", 2)
        game.handle_block_placement(screen_x, screen_y, game.inventory.slots[0])
        self.assertEqual(game.world.get_tile(tx, ty), TILE_BED)
        self.assertEqual(game.inventory.slots[0].count, 1)

    def test_13_bed_and_clock_edge_cases(self):
        """Verifies bed wake-up toggle, max HP cap, movement cancellation, and clock reach limit."""
        game = PotariaGame()
        tx = 30
        ty = 40
        game.world.set_tile(tx, ty, TILE_BED)
        tile_wx = tx * SCALED_TILE
        tile_wy = ty * SCALED_TILE

        # Player adjacent
        game.player.x = tile_wx
        game.player.y = tile_wy - SCALED_TILE
        game.sky.time = 0.75 * game.sky.cycle_duration  # Bed sleep requires night
        screen_x, screen_y = game.camera.world_to_screen(tile_wx + 16, tile_wy + 16)

        # Right-click to rest
        game.handle_right_click(screen_x, screen_y)
        self.assertTrue(game.player.is_resting)

        # Right-click again toggles resting off
        game.handle_right_click(screen_x, screen_y)
        self.assertFalse(game.player.is_resting)
        self.assertIn("Woke up", game.inventory.last_learned_message)

        # Rest again with full HP: cannot exceed max health
        game.handle_right_click(screen_x, screen_y)
        self.assertTrue(game.player.is_resting)
        game.player.health = game.player.max_health
        game.player.update(1.0, game.world)
        self.assertEqual(game.player.health, game.player.max_health)

        # Moving with key input cancels resting
        fake_keys = {pygame.K_d: True}
        game.player.handle_input(fake_keys, tile_wx + 100, tile_wy)
        self.assertFalse(game.player.is_resting)

        # Clock out of reach (> 5.5 tiles)
        game.world.set_tile(tx + 20, ty, TILE_GRANDFATHER_CLOCK)
        far_screen_x, far_screen_y = game.camera.world_to_screen((tx + 20) * SCALED_TILE + 16, ty * SCALED_TILE + 16)
        game.inventory.last_learned_message = None
        game.handle_right_click(far_screen_x, far_screen_y)
        self.assertIsNone(game.inventory.last_learned_message)

if __name__ == "__main__":
    unittest.main()
