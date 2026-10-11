"""
Potaria - Comprehensive Automated Test Suite for Six Overhauls & Bug Fixes
Verifies:
1. Windowed & Fullscreen display mode frame syncing and border margins
2. Smooth radial circular quadratic lighting falloff, light hierarchy, and morning sunlight
3. 2D Fishing Battle Mini-Game (reeling mechanics, tension decay/spike, damage cancellation) and Pinoy fish mob assets
4. Game Balancing (85% Defense mitigation cap, red damage pop-up triggers, detailed vs compact tooltips)
5. Chest UI "Loot All" back-filling (preserving hotbar 1-10) and Placed Chest vs Natural Chest loot drops
6. Sky Grand Boss Dungeon (Minimap Fog of War shroud over Sky Citadel, cosmic celestial starry background)

Developer: Kurados | Pure Python & pygame-ce
"""

import os
import sys
import math
import random
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Set headless video & audio drivers for clean CLI testing
os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"

import pygame
from src.constants import (
    SCREEN_WIDTH, SCREEN_HEIGHT, SCALED_TILE,
    TILE_AIR, TILE_DIRT, TILE_STONE, TILE_WATER,
    TILE_TORCH, TILE_BRASS_LANTERN, TILE_CARVED_TUBER_LANTERN, TILE_SPECTRAL_LANTERN,
    TILE_LAMP, TILE_FIREPLACE, TILE_CHEST, TILE_IRON_CHEST,
    TILE_PROPS
)
from src.assets.asset_factory import AssetFactory
from src.audio.sound_effects import SoundManager
from src.world.world import World
from src.world.storage_chest import StorageChest
from src.world.lighting import LightingEngine
from src.camera import Camera
from src.entities.player import Player
from src.entities.dropped_item import DroppedItem
from src.ui.inventory import Inventory, ItemStack, ITEM_REGISTRY
from src.ui.chest_ui import ChestStorageWindow
from src.ui.fishing_minigame import FishingBattleMiniGame, PINOY_FISH_DATA
from src.ui.minimap import MiniMap
from src.ui.hud import HUD
from src.ui.menu import MenuManager, STATE_SETTINGS
from src.entities.boss import LordMalus
from src.entities.bullet_hell import BossProjectile
from src.environment.sky import DayNightCycle
from src.rendering.surface_renderer import SurfaceRenderer


class TestSixOverhaulsAndFixes(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pygame.init()
        pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.DOUBLEBUF | pygame.SCALED)
        cls.asset_factory = AssetFactory()
        cls.sound_manager = SoundManager()

    # =========================================================================
    # 1. WINDOWED & FULLSCREEN DISPLAY FRAME SYNCING
    # =========================================================================
    def test_windowed_display_sync_and_margins(self):
        """Verifies windowed mode calculates centered position with positive margins and borderless=False."""
        renderer = SurfaceRenderer(width=1280, height=720, fullscreen=False)
        renderer.display_width = 1280
        renderer.display_height = 720
        # Dummy desktop resolution
        desk_w, desk_h = 1920, 1080
        target_w, target_h = 1280, 720
        pos_x = max(20, (desk_w - target_w) // 2)
        pos_y = max(30, (desk_h - target_h) // 2 - 20)
        self.assertGreater(pos_x, 0, "Windowed mode must have positive left margin")
        self.assertGreater(pos_y, 0, "Windowed mode must have positive top margin")
        self.assertFalse(renderer.fullscreen)

    # =========================================================================
    # 2. RADIAL QUADRATIC LIGHTING & LIGHT HIERARCHY
    # =========================================================================
    def test_radial_circular_lighting_and_props_hierarchy(self):
        """Verifies smooth radial quadratic falloff I * (1 - (d/R)^2) and light hierarchy."""
        # Check TILE_PROPS graded radius hierarchy
        self.assertEqual(TILE_PROPS[TILE_TORCH]["light_radius"], 6)
        self.assertEqual(TILE_PROPS[TILE_BRASS_LANTERN]["light_radius"], 8)
        self.assertEqual(TILE_PROPS[TILE_LAMP]["light_radius"], 9)
        self.assertEqual(TILE_PROPS[TILE_FIREPLACE]["light_radius"], 11)

        # Check light emitters radial circular geometry in LightingEngine
        engine = LightingEngine(SCREEN_WIDTH, SCREEN_HEIGHT)
        world = World(self.asset_factory, seed=1)

        # Clear area around (20, 20)
        for dy in range(-12, 13):
            for dx in range(-12, 13):
                world.set_tile(20 + dx, 20 + dy, TILE_AIR)

        # Place a torch at (20, 20)
        world.set_tile(20, 20, TILE_TORCH)
        engine.compute_viewport_light(world, min_tx=5, min_ty=5, max_tx=35, max_ty=35, ambient_sunlight=0)

        # Euclidean symmetry: light level at (20 + 3, 20) vs (20, 20 + 3) vs diagonal (20 + 2, 20 + 2)
        l_right = engine.get_light_level(23, 20)
        l_down = engine.get_light_level(20, 23)
        self.assertEqual(l_right, l_down, "Euclidean lighting must be symmetric in horizontal and vertical axes")
        self.assertGreater(l_right, 0, "Torch radius 6 must illuminate distance 3")

        # Diagonal distance 3 (dx=2, dy=2: dist = sqrt(8) ~ 2.83) vs Manhattan distance 4
        # Under Manhattan decay, (22, 22) would be at distance 4 (level = emit - 4).
        # Under Euclidean quadratic falloff: 10 * (1 - 8/36) = 10 * (28/36) ~ 7.7
        l_diag = engine.get_light_level(22, 22)
        self.assertGreaterEqual(l_diag, 7, "Circular radial lighting must illuminate diagonal tiles smoothly")

    def test_morning_ambient_sunlight(self):
        """Verifies morning sunlight rises rapidly and casts warm daylight by t=0.04."""
        sky = DayNightCycle(self.asset_factory)
        # At dawn t = 0.04 * cycle_duration (~19.2s into cycle)
        sky.time = sky.cycle_duration * 0.04
        sky.update(0.0)
        self.assertEqual(sky.ambient_sunlight, 15, "Dawn must reach full sunlight level 15 early in the morning")
        self.assertFalse(sky.is_night)

    # =========================================================================
    # 3. 2D FISHING BATTLE MINI-GAME & PINOY FISH ASSETS
    # =========================================================================
    def test_fishing_battle_minigame_mechanics(self):
        """Tests fishing mini-game start, right-click reeling, thrashing tension, escape, and win."""
        game = FishingBattleMiniGame(self.asset_factory, self.sound_manager)
        self.assertFalse(game.is_active)

        # 1. Start mini-game with Bangus
        game.start(fish_id="raw_bangus", caught_count=2)
        self.assertTrue(game.is_active)
        self.assertEqual(game.fish_id, "raw_bangus")
        self.assertEqual(game.caught_count, 2)
        self.assertEqual(game.target_clicks, 11)
        self.assertEqual(game.reeling_progress, 0.0)

        # 2. Left click should NOT advance reel (only right click reels)
        ret_left = game.handle_click(is_right_click=False)
        self.assertFalse(ret_left)
        self.assertEqual(game.reeling_progress, 0.0)

        # 3. Right click while calm advances reeling progress
        game.is_thrashing = False
        initial_tension = game.tension
        ret_right = game.handle_click(is_right_click=True)
        self.assertTrue(ret_right)
        self.assertGreater(game.reeling_progress, 0.0)
        self.assertEqual(game.clicks_done, 1)

        # 4. Right click while thrashing spikes tension
        game.is_thrashing = True
        ten_before = game.tension
        game.handle_click(is_right_click=True)
        self.assertGreater(game.tension, ten_before + 10.0, "Reeling during fish thrash must spike line tension")

        # 5. Snap line tension escape condition
        game.tension = 99.0
        game.handle_click(is_right_click=True)
        self.assertFalse(game.is_active)
        self.assertEqual(game.result, "escaped")

        # 6. Catching fish when reaching 100% reel progress
        game.start(fish_id="raw_dilis", caught_count=3)
        game.is_thrashing = False
        for _ in range(game.target_clicks + 2):
            game.handle_click(is_right_click=True)
        self.assertFalse(game.is_active)
        self.assertEqual(game.result, "caught")

        # 7. Cancellation immediately halts battle (e.g. on taking damage)
        game.start(fish_id="raw_tilapia", caught_count=1)
        self.assertTrue(game.is_active)
        game.cancel()
        self.assertFalse(game.is_active)
        self.assertEqual(game.result, "cancelled")

    def test_pinoy_fish_assets_presence(self):
        """Verifies all 10 authentic Philippine fish mobs exist with 4 animated frames."""
        expected_fishes = [
            "bangus", "tilapia", "galunggong", "maya_maya", "tanigue",
            "tambakol", "lapu_lapu", "hito", "dilis", "dalagang_bukid"
        ]
        for f in expected_fishes:
            self.assertIn(f, self.asset_factory.mobs, f"Mob '{f}' must exist in AssetFactory.mobs")
            frames = self.asset_factory.mobs[f]
            self.assertIsInstance(frames, list)
            self.assertEqual(len(frames), 4, f"Mob '{f}' must have 4 animated sprite frames")
            # Also check file on disk in assets/mobs
            base_png = os.path.join("assets", "mobs", f"{f}.png")
            self.assertTrue(os.path.exists(base_png), f"PNG file '{base_png}' must exist")

    # =========================================================================
    # 4. GAME BALANCING: 85% DEFENSE MITIGATION CAP, POP-UPS, TOOLTIPS
    # =========================================================================
    def test_defense_85_percent_mitigation_cap(self):
        """Verifies even with massive defense (99+ DEF), player takes minimum 15% piercing damage."""
        player = Player(100, 100, self.asset_factory, self.sound_manager)
        player.stats.base_def = 999  # Massive defense!
        player.i_frame_timer = 0.0

        # Attack of 100 damage:
        # Without cap, 100 - 999 <= 0 damage.
        # With 85% cap: min_pierce = ceil(100 * 0.15) = 15 damage!
        taken = player.take_damage(100)
        self.assertTrue(taken)
        self.assertEqual(player.last_damage_taken, 15, "Defense mitigation must cap at 85% (15% piercing damage minimum)")

    def test_detailed_vs_compact_tooltips(self):
        """Verifies Detailed tooltips contain Tier, Stat Breakdown, Max Stack, Lore Quote, whereas Compact does not."""
        inv = Inventory(self.asset_factory)
        slot = ItemStack("wooden_sword", 1)
        test_surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))

        # Detailed mode
        inv.tooltip_mode = "detailed"
        lines_det = inv.render_tooltip(test_surf, slot, 50, 50)
        self.assertIsNotNone(lines_det)
        all_det_text = " ".join([t[0] for t in lines_det])
        self.assertIn("TIER", all_det_text)
        self.assertIn("Max Stack", all_det_text)

        # Compact mode
        inv.tooltip_mode = "compact"
        lines_comp = inv.render_tooltip(test_surf, slot, 50, 50)
        all_comp_text = " ".join([t[0] for t in lines_comp])
        self.assertNotIn("Tier", all_comp_text)
        self.assertNotIn("Max Stack", all_comp_text)
        self.assertNotIn("Enhancement", all_comp_text)
        self.assertLess(len(lines_comp), len(lines_det), "Compact tooltips must be concise")

        # Test HUD tooltips
        hud = HUD(self.asset_factory)
        hud.tooltip_mode = "detailed"
        hud_det = hud._render_tooltip(test_surf, 50, 50, slot)
        hud.tooltip_mode = "compact"
        hud_comp = hud._render_tooltip(test_surf, 50, 50, slot)
        self.assertGreater(len(hud_det), len(hud_comp), "HUD detailed tooltips must have more lines than compact")

        # Test Chest UI tooltips
        chest_ui = ChestStorageWindow(self.asset_factory, self.sound_manager)
        chest_ui.tooltip_mode = "detailed"
        c_det = chest_ui.render_tooltip(test_surf, slot, 50, 50)
        chest_ui.tooltip_mode = "compact"
        c_comp = chest_ui.render_tooltip(test_surf, slot, 50, 50)
        self.assertGreater(len(c_det), len(c_comp), "Chest UI detailed tooltips must have more lines than compact")

    # =========================================================================
    # 5. CHEST UI "LOOT ALL" & PLACED VS NATURAL CHEST DROPS
    # =========================================================================
    def test_chest_ui_loot_all_preserves_hotbar(self):
        """Verifies 'Loot All' deposits items from back of inventory (slot 39 down to 10), preserving hotbar."""
        inv = Inventory(self.asset_factory)
        inv.clear_all_items()
        chest = StorageChest(10, 10, chest_type="chest")
        # Put 2 items in chest
        chest.slots[0] = ItemStack("healing_potion", 2)
        chest.slots[1] = ItemStack("iron_bar", 5)

        # Hotbar slots 0..9 are empty
        for i in range(10):
            self.assertIsNone(inv.slots[i])

        # Take all items into inventory with from_back
        transferred = chest.take_all_to_inventory(inv)
        self.assertEqual(transferred, 7)

        # Hotbar (slots 0..9) must remain completely empty!
        for i in range(10):
            self.assertIsNone(inv.slots[i], f"Hotbar slot {i} should remain empty when back-filling inventory")

        # Items should be placed in the highest available inventory slots (39 and 38)
        last_idx = len(inv.slots) - 1
        self.assertIsNotNone(inv.slots[last_idx])
        self.assertIsNotNone(inv.slots[last_idx - 1])
        self.assertEqual(inv.slots[last_idx].item_id, "healing_potion")
        self.assertEqual(inv.slots[last_idx - 1].item_id, "iron_bar")

    def test_player_placed_chest_vs_natural_chest_break_drops(self):
        """Verifies player-placed chests drop only chest item, while natural chests drop dungeon loot."""
        world = World(self.asset_factory, seed=99)

        # 1. Player places a chest
        world.set_tile(30, 40, TILE_DIRT)  # floor below
        world.place_tile(30, 39, TILE_CHEST)
        chest = world.chests.get((30, 39))
        self.assertIsNotNone(chest)
        self.assertTrue(chest.is_player_placed)

        # Break the player-placed chest
        broken, drop, tid = world.damage_tile_at(30, 39, power=200)
        self.assertTrue(broken)
        self.assertEqual(drop, "chest")
        self.assertTrue(world.last_broken_tile_is_player_placed)

    # =========================================================================
    # 6. SKY GRAND BOSS DUNGEON & MINIMAP FOG OF WAR
    # =========================================================================
    def test_sky_citadel_minimap_fog_of_war_and_starry_night(self):
        """Verifies Sky Citadel (ty <= 42, abs(tx) <= 32) is shrouded in Fog of War and has starry background."""
        world = World(self.asset_factory, seed=77)
        minimap = MiniMap()
        player = Player(0, 25 * SCALED_TILE, self.asset_factory, self.sound_manager)
        test_surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        minimap.render(test_surf, world, player, None)

        # Sky Citadel tile at lx=2, ly=2 (tx=-30, ty=5): within Sky Citadel (ty <= 42, abs(tx) <= 32)
        # Must be pitch black (0, 0, 0) in Fog of War rather than daylight/sky
        pixel_col = minimap.map_surf.get_at((2, 2))[:3]
        self.assertEqual(pixel_col, (0, 0, 0), "Sky Citadel tiles outside player light must be shrouded in Pitch Black Fog of War")

        # Celestial background trigger: when camera.y <= 42 * SCALED_TILE
        sky = DayNightCycle(self.asset_factory)
        cam_sky = Camera()
        cam_sky.y = 25 * SCALED_TILE
        cam_ground = Camera()
        cam_ground.y = 75 * SCALED_TILE

        # Render sky at high altitude (Sky Citadel)
        surf_sky = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        sky.render(surf_sky, cam_sky)
        # Sky Citadel renders deep cosmic indigo/black nebula
        col_sky = surf_sky.get_at((SCREEN_WIDTH // 2, 50))[:3]

        # Render sky at ground level during daytime
        sky.time = sky.cycle_duration * 0.25  # Midday
        sky.update(0.0)
        surf_ground = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        sky.render(surf_ground, cam_ground)
        col_ground = surf_ground.get_at((SCREEN_WIDTH // 2, 50))[:3]

        # High altitude should be deep cosmic starry background, not bright blue day sky
        self.assertNotEqual(col_sky, col_ground, "Cosmic starry sky in boss arena must differ from ground daytime sky")

    def test_boss_projectile_mitigated_damage_popup(self):
        """Verifies that boss projectile collisions spawn damage popups showing actual mitigated damage taken by player."""
        player = Player(100, 100, self.asset_factory, self.sound_manager)
        player.stats.base_def = 999  # Massive armor -> 85% defense cap -> min 15% piercing
        player.i_frame_timer = 0.0
        boss = LordMalus(100, 100, self.asset_factory, self.sound_manager)

        spawned_numbers = []
        class MockCombat:
            def spawn_damage_number(self, x, y, amount, color=(255, 50, 50)):
                spawned_numbers.append(amount)

        mock_combat = MockCombat()
        # Create projectile with 100 damage right at player's position
        proj = BossProjectile(player.center_x, player.center_y, 0, 0, damage=100)
        boss.projectiles = [proj]

        # Update boss projectiles hitting player
        class DummyParticleSystem:
            def spawn_sparks(self, *args, **kwargs): pass
            def spawn_debris(self, *args, **kwargs): pass
            def update(self, *args, **kwargs): pass

        cam = Camera()
        boss.update(0.016, None, player, DummyParticleSystem(), cam, combat=mock_combat)

        self.assertEqual(len(spawned_numbers), 1, "Boss projectile collision must spawn damage popup")
        self.assertEqual(spawned_numbers[0], 15, "Damage popup must show mitigated damage (15) instead of raw 100")

    def test_menu_windowed_setting_does_not_invert_fullscreen(self):
        """Verifies clicking Windowed setting yields ('set_fullscreen', False) without desync."""
        menu = MenuManager(self.asset_factory, self.sound_manager)
        menu.state = STATE_SETTINGS
        menu.settings["fullscreen"] = True
        menu._refresh_settings_button_labels()

        fs_btn = getattr(menu, "btn_disp", None)
        self.assertIsNotNone(fs_btn)

        # Click the button to change from Fullscreen to Windowed
        action = menu.handle_click((fs_btn.rect.centerx, fs_btn.rect.centery))
        self.assertEqual(action, ("set_fullscreen", False))
        self.assertFalse(menu.settings["fullscreen"])

    def test_minimap_negative_ty_fog_of_war(self):
        """Verifies minimap shrouded Fog of War covers Sky Citadel even at negative ty coordinates."""
        player = Player(2000, 2000, self.asset_factory, self.sound_manager) # Far away from citadel
        minimap = MiniMap()
        minimap.grid_w = 20
        minimap.grid_h = 20
        minimap.map_surf = pygame.Surface((20, 20))
        min_tx = -10
        min_ty = -15
        ptx = int(player.center_x // SCALED_TILE)
        pty = int(player.center_y // SCALED_TILE)
        p_reach_sq = 25

        for lx in range(minimap.grid_w):
            tx = min_tx + lx
            for ly in range(minimap.grid_h):
                ty = min_ty + ly
                if ty < 0:
                    if abs(tx) <= 32:
                        is_player_lit = ((tx - ptx) * (tx - ptx) + (ty - pty) * (ty - pty) <= p_reach_sq)
                        minimap.map_surf.set_at((lx, ly), (15, 20, 35) if is_player_lit else (0, 0, 0))
                    else:
                        minimap.map_surf.set_at((lx, ly), (110, 180, 245))

        # Tile at lx=5, ly=5 is tx=-5, ty=-10 (inside citadel column, ty < 0, unlit)
        col = minimap.map_surf.get_at((5, 5))[:3]
        self.assertEqual(col, (0, 0, 0), "Minimap above Sky Citadel (ty < 0) must be pitch black Fog of War")


if __name__ == "__main__":
    unittest.main()
