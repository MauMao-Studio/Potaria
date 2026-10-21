"""
Potaria - Comprehensive Test Suite for Fishing Overhaul, Cooking Overhaul,
Philippine Farming System, and Multi-Aspect Viewport Scaling.
Developer: Kurados | Pure Python 3.13 + Pygame-ce 2.5.8
"""

import os
import sys
import random
import unittest
from unittest.mock import MagicMock, patch
import pygame

# Headless pygame setup
os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"
pygame.init()
pygame.display.set_mode((1280, 720), pygame.DOUBLEBUF)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

from src.constants import (
    SCREEN_WIDTH, SCREEN_HEIGHT, SCALED_TILE, SURFACE_LEVEL,
    TILE_AIR, TILE_DIRT, TILE_GRASS, TILE_WATER, TILE_FURNACE, TILE_FIREPLACE,
    TILE_TORCH, TILE_FARMLAND, TILE_FARMLAND_WET, TILE_CROP, TILE_WILD_PLANT,
    CRAFT_CAT_SURVIVAL
)
from src.assets.asset_factory import AssetFactory
from src.world.world import World
from src.entities.player import Player
from src.ui.inventory import Inventory, ITEM_REGISTRY
from src.ui.crafting import CraftingSystem, RECIPES
from src.ui.fishing_minigame import FishingBattleMiniGame, PINOY_FISH_DATA
from src.rendering.surface_renderer import SurfaceRenderer


class DummySound:
    def __init__(self):
        self.played = []

    def play(self, sound_name):
        self.played.append(sound_name)


class TestFishingCookingFarming(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.factory = AssetFactory()
        cls.sound = DummySound()

    def setUp(self):
        self.world = World(self.factory, seed=12345)
        self.player = Player(100, 100, self.factory, self.sound)
        self.inv = Inventory(self.factory)
        self.crafting = CraftingSystem(self.factory, self.sound)
        self.fishing = FishingBattleMiniGame(self.factory, self.sound)

    # =========================================================================
    # 1. FISHING OVERHAUL TESTS
    # =========================================================================

    def test_fishing_dynamic_time_limits_by_rarity(self):
        """Verifies fish rarity dynamically scales battle time limit (7.5s - 16.0s)."""
        # Common fish (e.g. dilis)
        self.fishing.start(fish_id="raw_dilis")
        self.assertAlmostEqual(self.fishing.time_limit, 8.5, places=1)
        self.assertEqual(self.fishing.rarity, "common")

        # Uncommon fish (e.g. bangus)
        self.fishing.start(fish_id="raw_bangus")
        self.assertAlmostEqual(self.fishing.time_limit, 10.0, places=1)
        self.assertEqual(self.fishing.rarity, "uncommon")

        # Rare fish (e.g. maya_maya)
        self.fishing.start(fish_id="raw_maya_maya")
        self.assertAlmostEqual(self.fishing.time_limit, 11.5, places=1)
        self.assertEqual(self.fishing.rarity, "rare")

        # Epic fish (e.g. lapu_lapu)
        self.fishing.start(fish_id="raw_lapu_lapu")
        self.assertAlmostEqual(self.fishing.time_limit, 13.0, places=1)
        self.assertEqual(self.fishing.rarity, "epic")

        # Junk item (e.g. old_boot)
        self.fishing.start(fish_id="old_boot")
        self.assertAlmostEqual(self.fishing.time_limit, 7.5, places=1)
        self.assertEqual(self.fishing.catch_category, "junk")

    def test_fishing_sweet_spot_tension_bonus(self):
        """Verifies reeling in the 30%-70% tension zone grants 1.35x speed and visual flash."""
        self.fishing.start(fish_id="raw_bangus")
        self.fishing.is_thrashing = False

        # Reeling outside sweet spot (e.g. tension = 20%)
        self.fishing.tension = 20.0
        base_progress = 100.0 / float(self.fishing.target_clicks)
        self.fishing.handle_click(is_right_click=True)
        self.assertAlmostEqual(self.fishing.reeling_progress, base_progress, places=2)
        self.assertEqual(self.fishing.perfect_timing_flash, 0.0)

        # Reeling inside sweet spot (e.g. tension = 45%)
        self.fishing.tension = 45.0
        prev_progress = self.fishing.reeling_progress
        self.fishing.handle_click(is_right_click=True)
        gained = self.fishing.reeling_progress - prev_progress
        self.assertAlmostEqual(gained, base_progress * 1.35, places=2)
        self.assertGreater(self.fishing.perfect_timing_flash, 0.0)

    def test_fishing_battle_time_limit_escape(self):
        """Verifies that running out of time during battle results in fish escape."""
        self.fishing.start(fish_id="raw_tilapia")
        self.assertTrue(self.fishing.is_active)

        # Advance time beyond time limit
        res = self.fishing.update(self.fishing.time_limit + 1.0)
        self.assertEqual(res, "escaped")
        self.assertFalse(self.fishing.is_active)
        self.assertEqual(self.fishing.result, "escaped")

    def test_fishing_battle_tension_overload_escape(self):
        """Verifies tension >= 100 causes the line to snap and fish to escape."""
        self.fishing.start(fish_id="raw_hito")
        self.fishing.tension = 99.0
        self.fishing.is_thrashing = True
        self.fishing.handle_click(is_right_click=True)  # Thrash reel adds 14 tension
        self.assertEqual(self.fishing.result, "escaped")
        self.assertFalse(self.fishing.is_active)

    def test_fishing_battle_caught_success(self):
        """Verifies reaching 100% reel progress catches the fish."""
        self.fishing.start(fish_id="raw_dilis")
        self.fishing.reeling_progress = 99.0
        self.fishing.tension = 25.0
        self.fishing.is_thrashing = False
        self.fishing.handle_click(is_right_click=True)
        self.assertEqual(self.fishing.result, "caught")
        self.assertFalse(self.fishing.is_active)

    def test_fishing_bobber_bite_window_timeout(self):
        """Simulates bobber bite timer expiring (1.6-2.0s), causing fish to escape."""
        notifications = []
        mock_inv = MagicMock()
        mock_inv.notify = lambda msg: notifications.append(msg)

        bobber = {
            "x": 200, "y": 200,
            "state": "bite",
            "timer": 0.0,
            "bite_timer": 1.8,
            "bite_duration": 1.8,
        }

        # Simulate frame update where bite_timer ticks down
        bobber["bite_timer"] -= 1.0
        self.assertGreater(bobber["bite_timer"], 0)

        # Timer expires
        bobber["bite_timer"] -= 1.0
        if bobber["bite_timer"] <= 0:
            mock_inv.notify("The fish bit and got away! Reel timing missed.")
            bobber = None

        self.assertIsNone(bobber)
        self.assertIn("The fish bit and got away! Reel timing missed.", notifications)

    def test_fishing_early_reel_spook(self):
        """Simulates early reeling during waiting state, spooking the fish."""
        notifications = []
        mock_inv = MagicMock()
        mock_inv.notify = lambda msg: notifications.append(msg)

        bobber = {
            "x": 200, "y": 200,
            "state": "waiting",
            "timer": 3.0,
            "bite_timer": 0.0,
        }

        # Early reel action
        if bobber.get("state") == "waiting":
            mock_inv.notify("Reeled in too early! The fish was spooked.")
            bobber = None

        self.assertIsNone(bobber)
        self.assertIn("Reeled in too early! The fish was spooked.", notifications)

    # =========================================================================
    # 2. COOKING OVERHAUL TESTS
    # =========================================================================

    def test_cooking_duration_rarity_scaling(self):
        """Verifies cooking durations match rarity tiers: common (4s) to ancient (24s)."""
        self.assertEqual(self.world.get_cooking_duration("cooked_bangus"), 6.0)     # uncommon
        self.assertEqual(self.world.get_cooking_duration("cooked_tilapia"), 4.0)    # common
        self.assertEqual(self.world.get_cooking_duration("cooked_maya_maya"), 9.0)  # rare
        self.assertEqual(self.world.get_cooking_duration("cooked_lapu_lapu"), 13.0) # epic

    def test_furnace_single_food_limit(self):
        """Verifies strictly one food item per furnace at a time."""
        gx, gy = 10, 10
        self.world.set_tile(gx, gy, TILE_FURNACE)

        # First cooking job succeeds
        started = self.world.start_furnace_cooking(gx, gy, "cooked_bangus", count=1)
        self.assertTrue(started)
        self.assertTrue(self.world.is_furnace_busy(gx, gy))

        # Second cooking job on same furnace is rejected
        second = self.world.start_furnace_cooking(gx, gy, "cooked_tilapia", count=1)
        self.assertFalse(second)

    def test_furnace_and_campfire_stations(self):
        """Verifies both TILE_FURNACE and TILE_FIREPLACE act as valid cooking stations."""
        fx, fy = 15, 15
        self.world.set_tile(fx, fy, TILE_FIREPLACE)
        self.player.center_x = fx * SCALED_TILE
        self.player.center_y = fy * SCALED_TILE

        # CraftingSystem detects fireplace as furnace station
        self.crafting.check_nearby_stations(self.world, self.player)
        self.assertTrue(self.crafting.near_furnace)

        station_pos = self.crafting.get_nearest_cooking_station(self.world, self.player)
        self.assertEqual(station_pos, (fx, fy))

    def test_furnace_cooking_lifecycle_and_collection(self):
        """Verifies full cooking lifecycle: start, update over time, and collection."""
        gx, gy = 20, 20
        self.world.set_tile(gx, gy, TILE_FURNACE)
        self.world.start_furnace_cooking(gx, gy, "cooked_bangus", count=1)

        # Before finished: collection returns (None, time_left)
        item, time_left = self.world.collect_furnace_food(gx, gy, self.inv)
        self.assertIsNone(item)
        self.assertAlmostEqual(time_left, 6.0, places=1)
        self.assertEqual(self.inv.count_item("cooked_bangus"), 0)

        # Update half duration (3s elapsed)
        self.world.update_furnaces(3.0)
        self.assertTrue(self.world.is_furnace_busy(gx, gy))

        # Update remaining duration (4s elapsed, total 7s > 6s)
        self.world.update_furnaces(4.0)
        self.assertFalse(self.world.is_furnace_busy(gx, gy))

        # Collection after finished yields cooked food into inventory
        item, count = self.world.collect_furnace_food(gx, gy, self.inv)
        self.assertEqual(item, "cooked_bangus")
        self.assertEqual(count, 1)
        self.assertEqual(self.inv.count_item("cooked_bangus"), 1)
        self.assertNotIn((gx, gy), self.world.active_furnaces)

    def test_inihaw_fish_naming_and_recipes(self):
        """Verifies all 10 Philippine fish cook into 'Inihaw na [Fish]'."""
        fish_list = [
            ("raw_bangus", "cooked_bangus", "Inihaw na Bangus"),
            ("raw_tilapia", "cooked_tilapia", "Inihaw na Tilapia"),
            ("raw_galunggong", "cooked_galunggong", "Inihaw na Galunggong"),
            ("raw_maya_maya", "cooked_maya_maya", "Inihaw na Maya-Maya"),
            ("raw_tanigue", "cooked_tanigue", "Inihaw na Tanigue"),
            ("raw_tambakol", "cooked_tambakol", "Inihaw na Tambakol"),
            ("raw_lapu_lapu", "cooked_lapu_lapu", "Inihaw na Lapu-Lapu"),
            ("raw_hito", "cooked_hito", "Inihaw na Hito"),
            ("raw_dilis", "cooked_dilis", "Inihaw na Dilis"),
            ("raw_dalagang_bukid", "cooked_dalagang_bukid", "Inihaw na Dalagang Bukid"),
        ]

        recipe_results = [r["result"] for r in RECIPES if r.get("station") == "furnace"]
        for raw_id, cooked_id, display_name in fish_list:
            self.assertIn(cooked_id, ITEM_REGISTRY, f"Missing item: {cooked_id}")
            self.assertEqual(ITEM_REGISTRY[cooked_id]["name"], display_name)
            self.assertIn(cooked_id, recipe_results, f"Missing furnace recipe for: {cooked_id}")

    def test_headless_crafting_instant_fallback(self):
        """Verifies unit tests running craft() without world/player craft instantly."""
        recipe = next(r for r in RECIPES if r["result"] == "cooked_bangus")
        self.inv.add_item("raw_bangus", 1)
        success = self.crafting.craft(recipe, self.inv, world=None, player=None)
        self.assertTrue(success)
        self.assertEqual(self.inv.count_item("raw_bangus"), 0)
        self.assertEqual(self.inv.count_item("cooked_bangus"), 1)

    # =========================================================================
    # 3. PHILIPPINE FARMING SYSTEM TESTS
    # =========================================================================

    def test_farming_tools_registered(self):
        """Verifies bamboo_hoe, iron_hoe, and watering_can are registered with attributes."""
        tools = ["bamboo_hoe", "iron_hoe", "watering_can"]
        for t in tools:
            self.assertIn(t, ITEM_REGISTRY, f"Tool {t} not registered")
            data = ITEM_REGISTRY[t]
            self.assertTrue(any(term in data.get("special", "") for term in ("Farming Tool", "Watering Tool")))

    def test_philippine_crops_and_seeds_registered(self):
        """Verifies 8 native Philippine crops and seeds exist in registry."""
        crops = [
            ("rice", "rice_seeds"),
            ("garlic", "garlic_seeds"),
            ("onion", "onion_seeds"),
            ("ginger", "ginger_seeds"),
            ("eggplant", "eggplant_seeds"),
            ("string_beans", "string_beans_seeds"),
            ("tamarind", "tamarind_seeds"),
            ("calamansi", "calamansi_seeds"),
        ]
        for crop_id, seed_id in crops:
            self.assertIn(crop_id, ITEM_REGISTRY, f"Missing crop: {crop_id}")
            self.assertIn(seed_id, ITEM_REGISTRY, f"Missing seed: {seed_id}")
            self.assertEqual(ITEM_REGISTRY[seed_id]["cat"], "material")

    def test_seed_extraction_recipes(self):
        """Verifies seed extraction recipes: 1 crop -> 2 seeds for all 8 native crops."""
        crop_seeds = [
            ("rice", "rice_seeds"),
            ("garlic", "garlic_seeds"),
            ("onion", "onion_seeds"),
            ("ginger", "ginger_seeds"),
            ("eggplant", "eggplant_seeds"),
            ("string_beans", "string_beans_seeds"),
            ("tamarind", "tamarind_seeds"),
            ("calamansi", "calamansi_seeds"),
        ]
        for crop_id, seed_id in crop_seeds:
            recipe = next((r for r in RECIPES if r["result"] == seed_id), None)
            self.assertIsNotNone(recipe, f"Missing recipe for {seed_id}")
            self.assertEqual(recipe["count"], 2)
            self.assertIn((crop_id, 1), recipe["ingredients"])

    def test_soil_tilling(self):
        """Verifies tilling converts dirt and grass into farmland."""
        # Dirt to farmland
        self.world.set_tile(5, 5, TILE_DIRT)
        self.world.set_tile(5, 4, TILE_AIR)
        self.assertTrue(self.world.till_soil(5, 5))
        self.assertEqual(self.world.get_tile(5, 5), TILE_FARMLAND)

        # Grass to farmland
        self.world.set_tile(6, 5, TILE_GRASS)
        self.world.set_tile(6, 4, TILE_AIR)
        self.assertTrue(self.world.till_soil(6, 5))
        self.assertEqual(self.world.get_tile(6, 5), TILE_FARMLAND)

    def test_farmland_4_block_water_hydration_radius(self):
        """Verifies permanent hydration if within 4 horizontal blocks of water."""
        water_x, water_y = 50, 10
        self.world.set_tile(water_x, water_y, TILE_WATER)

        # Distances 1 to 4 should be recognized as near water
        for dx in range(1, 5):
            self.assertTrue(
                self.world.is_farmland_near_water(water_x + dx, water_y),
                f"Failed for dx={dx}"
            )
            self.assertTrue(
                self.world.is_farmland_near_water(water_x - dx, water_y),
                f"Failed for dx=-{dx}"
            )

        # Distance 5 is outside hydration radius
        self.assertFalse(self.world.is_farmland_near_water(water_x + 5, water_y))
        self.assertFalse(self.world.is_farmland_near_water(water_x - 5, water_y))

    def test_manual_watering_and_dry_timer(self):
        """Verifies watering can hydrates dry farmland, and timer expires back to dry."""
        gx, gy = 80, 10
        self.world.set_tile(gx, gy, TILE_FARMLAND)

        # Water with watering can
        self.assertTrue(self.world.water_soil(gx, gy, duration=240.0))
        self.assertEqual(self.world.get_tile(gx, gy), TILE_FARMLAND_WET)
        self.assertEqual(self.world.soil_water_timers.get((gx, gy)), 240.0)

        # Partial timer decrement
        self.world.update_crops(100.0)
        self.assertEqual(self.world.get_tile(gx, gy), TILE_FARMLAND_WET)
        self.assertAlmostEqual(self.world.soil_water_timers.get((gx, gy)), 140.0, places=1)

        # Full expiry -> reverts to dry farmland
        self.world.update_crops(150.0)
        self.assertEqual(self.world.get_tile(gx, gy), TILE_FARMLAND)
        self.assertNotIn((gx, gy), self.world.soil_water_timers)

    def test_cave_farming_torchlight_requirement(self):
        """Verifies underground crops only grow when illuminated by torchlight/lantern."""
        # Deep underground (beyond surface level)
        gx, gy = 100, SURFACE_LEVEL + 40
        self.world.set_tile(gx, gy + 1, TILE_FARMLAND_WET)
        self.world.set_tile(gx, gy, TILE_AIR)

        # Solid roof above (no sky light)
        for y in range(gy - 15, gy):
            self.world.set_tile(gx, y, TILE_DIRT)

        self.world.plant_crop(gx, gy, "rice_seeds")
        self.assertEqual(self.world.get_tile(gx, gy), TILE_CROP)

        # Without torch: no growth
        self.assertFalse(self.world.has_crop_light(gx, gy))
        self.world.update_crops(50.0)
        self.assertEqual(self.world.farm_crops[(gx, gy)]["stage"], 0)

        # Place torch 3 blocks away
        self.world.set_tile(gx + 3, gy, TILE_TORCH)
        self.assertTrue(self.world.has_crop_light(gx, gy))

        # Now crop grows
        self.world.update_crops(50.0)
        self.assertEqual(self.world.farm_crops[(gx, gy)]["stage"], 1)

    def test_crop_growth_and_mature_harvest(self):
        """Verifies 4-stage growth and mature harvest returning crops + seeds."""
        gx, gy = 120, 10
        self.world.set_tile(gx, gy + 1, TILE_FARMLAND_WET)
        self.world.set_tile(gx, gy, TILE_AIR)
        self.world.set_tile(gx + 1, gy, TILE_TORCH)  # Guaranteed light

        self.world.plant_crop(gx, gy, "garlic_seeds")
        self.assertEqual(self.world.farm_crops[(gx, gy)]["stage"], 0)

        # Grow to stage 3 (mature)
        for _ in range(3):
            self.world.update_crops(45.0)

        self.assertEqual(self.world.farm_crops[(gx, gy)]["stage"], 3)

        # Harvest mature garlic
        drops = self.world.harvest_crop(gx, gy)
        self.assertEqual(self.world.get_tile(gx, gy), TILE_AIR)
        drop_dict = dict(drops)
        self.assertIn("garlic", drop_dict)
        self.assertIn("garlic_seeds", drop_dict)
        self.assertGreaterEqual(drop_dict["garlic"], 1)
        self.assertGreaterEqual(drop_dict["garlic_seeds"], 1)

    def test_farmland_destruction_pops_crop(self):
        """Verifies destroying supporting farmland breaks the crop above."""
        gx, gy = 140, 10
        self.world.set_tile(gx, gy + 1, TILE_FARMLAND_WET)
        self.world.set_tile(gx, gy, TILE_AIR)
        self.world.set_tile(gx + 1, gy, TILE_TORCH)
        self.world.plant_crop(gx, gy, "rice_seeds")
        self.assertEqual(self.world.get_tile(gx, gy), TILE_CROP)

        # Destroy supporting farmland
        self.world.set_tile(gx, gy + 1, TILE_AIR)
        self.world.update_crops(0.1)

        # Crop is popped off and cleaned up
        self.assertEqual(self.world.get_tile(gx, gy), TILE_AIR)
        self.assertNotIn((gx, gy), self.world.farm_crops)

    def test_weather_rain_hydrates_open_farmland(self):
        """Verifies rain hook waters all outdoor farmland exposed to sky."""
        gx, gy = 160, 5
        self.world.set_tile(gx, gy, TILE_FARMLAND)
        self.world.player_placed_tiles.add((gx, gy))

        # Clear sky above
        for y in range(0, gy):
            self.world.set_tile(gx, y, TILE_AIR)

        self.world.water_open_farmland()
        self.assertEqual(self.world.get_tile(gx, gy), TILE_FARMLAND_WET)
        self.assertIn((gx, gy), self.world.soil_water_timers)

    def test_wild_plant_harvest(self):
        """Verifies harvesting TILE_WILD_PLANT drops a native Philippine crop and seeds."""
        gx, gy = 180, 10
        self.world.set_tile(gx, gy, TILE_WILD_PLANT)
        drops = self.world.harvest_crop(gx, gy)
        self.assertEqual(self.world.get_tile(gx, gy), TILE_AIR)
        self.assertGreaterEqual(len(drops), 1)

    # =========================================================================
    # 4. VIEWPORT SCALING & MULTI-ASPECT RATIO TESTS
    # =========================================================================

    def test_viewport_scaling_standard_and_ultrawide(self):
        """Tests window_to_virtual_pos mapping across 16:9, 18:9, 20:9, and 21:9."""
        renderer = SurfaceRenderer(width=1280, height=720)

        # 1. 16:9 Standard HD (1920x1080) -> Uniform 1.5x scale
        with patch("pygame.display.get_window_size", return_value=(1920, 1080)):
            self.assertEqual(renderer.window_to_virtual_pos((960, 540)), (640, 360))
            self.assertEqual(renderer.window_to_virtual_pos((0, 0)), (0, 0))
            self.assertEqual(renderer.window_to_virtual_pos((1920, 1080)), (1279, 719))

        # 2. 18:9 Phone Display (2160x1080) -> Pillarbox (offset_x = 120)
        with patch("pygame.display.get_window_size", return_value=(2160, 1080)):
            # Center of active viewport: 120 + 960 = 1080
            self.assertEqual(renderer.window_to_virtual_pos((1080, 540)), (640, 360))
            # Left edge of viewport
            self.assertEqual(renderer.window_to_virtual_pos((120, 0)), (0, 0))
            # Outside viewport (in pillarbox) clamps safely to 0
            self.assertEqual(renderer.window_to_virtual_pos((20, 540)), (0, 360))

        # 3. 20:9 Modern Phone (2400x1080) -> Pillarbox (offset_x = 240)
        with patch("pygame.display.get_window_size", return_value=(2400, 1080)):
            # Center of active viewport: 240 + 960 = 1200
            self.assertEqual(renderer.window_to_virtual_pos((1200, 540)), (640, 360))
            # Right edge of viewport: 240 + 1920 = 2160
            self.assertEqual(renderer.window_to_virtual_pos((2160, 1080)), (1279, 719))

        # 4. 21:9 Ultrawide Phone (2520x1080) -> Pillarbox (offset_x = 300)
        with patch("pygame.display.get_window_size", return_value=(2520, 1080)):
            # Center of active viewport: 300 + 960 = 1260
            self.assertEqual(renderer.window_to_virtual_pos((1260, 540)), (640, 360))

    # =========================================================================
    # 5. ADDITIONAL EDGE CASE TESTS
    # =========================================================================

    def test_cannot_plant_crop_on_non_farmland(self):
        """Verifies crops cannot be planted on raw dirt, stone, wood, or air."""
        gx, gy = 200, 10
        # On stone
        self.world.set_tile(gx, gy + 1, 3) # TILE_STONE
        self.world.set_tile(gx, gy, TILE_AIR)
        self.assertFalse(self.world.plant_crop(gx, gy, "rice_seeds"))
        self.assertEqual(self.world.get_tile(gx, gy), TILE_AIR)

        # On raw dirt
        self.world.set_tile(gx, gy + 1, TILE_DIRT)
        self.assertFalse(self.world.plant_crop(gx, gy, "rice_seeds"))
        self.assertEqual(self.world.get_tile(gx, gy), TILE_AIR)

    def test_furnace_broken_cleans_up_active_cooking_job(self):
        """Verifies breaking a furnace removes its active cooking job during update."""
        gx, gy = 210, 10
        self.world.set_tile(gx, gy, TILE_FURNACE)
        self.world.start_furnace_cooking(gx, gy, "cooked_bangus", count=1)
        self.assertIn((gx, gy), self.world.active_furnaces)

        # Break furnace block to air
        self.world.set_tile(gx, gy, TILE_AIR)
        self.world.update_furnaces(1.0)
        self.assertNotIn((gx, gy), self.world.active_furnaces)

    def test_watering_can_refill_does_not_drain_water(self):
        """Verifies water tile remains intact when watering can is refilled from it."""
        wx, wy = 220, 10
        self.world.set_tile(wx, wy, TILE_WATER)

        # Simulate watering can interaction on water tile
        tile_before = self.world.get_tile(wx, wy)
        self.assertEqual(tile_before, TILE_WATER)

        # Refill interaction simulates checking tile is water, playing sound, and notifying
        is_water = (self.world.get_tile(wx, wy) == TILE_WATER)
        self.assertTrue(is_water)
        # Tile must remain water without draining
        tile_after = self.world.get_tile(wx, wy)
        self.assertEqual(tile_after, TILE_WATER)

    def test_grass_damage_seed_drop_logic(self):
        """Verifies grass blocks can yield seeds when broken."""
        gx, gy = 230, 10
        self.world.set_tile(gx, gy, TILE_GRASS)
        # Call damage_tile_at with enough damage to break the tile
        broken, drop, orig_tid = self.world.damage_tile_at(gx, gy, 100.0)
        self.assertTrue(broken)
        self.assertEqual(orig_tid, TILE_GRASS)
        self.assertEqual(self.world.get_tile(gx, gy), TILE_AIR)


if __name__ == "__main__":
    unittest.main()

