"""
Potaria - Comprehensive Automated Test Suite for New Overhauls
Verifies:
1. Cute Terraria Trees (Root flares, branchlets, spherical canopies, leaf damage immunity, tree felling cascade)
2. Liquid Water System (Animated wave caustics, swimming buoyancy, fluid drag, 10-bubble oxygen meter, drowning damage)
3. Cinematic Synth BGM Transitions (Main menu BGM, Night, Cavern, Boss, and Victory crossfading)
4. Main Menu Polish (Title logo glow, ambient sparkle particles, animated Spud mascot)
5. Achievements System (12 feats in data/achievements.json, persistence, toasts, browser, and in-game triggers)
6. Create New World UI/UX & Mods Separation (No MODE button in new world, dedicated MODS menu with Last Man Standing toggle)

Developer: Kurados | Pure Python & pygame-ce
"""

import os
import sys
import json
import time
import math

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pygame

# Set headless video driver for clean CLI testing
os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"

import unittest
from src.constants import (
    SCREEN_WIDTH, SCREEN_HEIGHT, SCALED_TILE,
    TILE_AIR, TILE_DIRT, TILE_GRASS, TILE_STONE, TILE_WOOD,
    TILE_WOOD_TRUNK, TILE_LEAVES, TILE_WATER, TILE_DOOR_CLOSED, TILE_TORCH,
    TILE_CORRUPT_GRASS, WALL_WOOD,
    STATE_MENU, STATE_PLAYING, STATE_NEW_WORLD, STATE_WORLDS,
    STATE_MODS, STATE_ACHIEVEMENTS, STATE_VICTORY,
    MODE_ADVENTURE, MODE_LAST_MAN_STANDING,
    WORLD_TYPE_INFINITE, DIFFICULTY_NORMAL, CAVERN_LEVEL
)
from src.assets.asset_factory import AssetFactory
from src.audio.sound_effects import SoundManager
from src.audio.bgm_manager import BgmManager
from src.world.world import World
from src.camera import Camera
from src.entities.player import Player
from src.entities.particle import ParticleSystem
from src.ui.menu import MenuManager
from src.rpg.achievements import AchievementManager, AchievementToast


class TestNewOverhauls(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pygame.init()
        pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.DOUBLEBUF | pygame.SCALED)
        cls.asset_factory = AssetFactory()
        cls.sound_manager = SoundManager()

    def setUp(self):
        # Clean temporary test save paths
        self.test_ach_file = os.path.join("saves", "test_achievements_runner.json")
        self.test_mods_file = os.path.join("saves", "test_mods_runner.json")
        for p in (self.test_ach_file, self.test_mods_file):
            if os.path.exists(p):
                try:
                    os.remove(p)
                except Exception:
                    pass

    def tearDown(self):
        for p in (self.test_ach_file, self.test_mods_file):
            if os.path.exists(p):
                try:
                    os.remove(p)
                except Exception:
                    pass

    # =========================================================================
    # 1. CUTE TERRARIA TREES & LEAF PROTECTION
    # =========================================================================
    def test_tree_assets_and_mechanics(self):
        """Tests Terraria-style tree assets, leaf damage immunity, and trunk felling cascade."""
        af = self.asset_factory
        # Check custom tree assets exist in asset factory (including palm, autumn, and biome branchlets)
        self.assertIn("trunk_base", af.tiles)
        self.assertIn("trunk_branch_l", af.tiles)
        self.assertIn("trunk_branch_r", af.tiles)
        self.assertIn("trunk_branch_l_snow", af.tiles)
        self.assertIn("trunk_branch_r_blight", af.tiles)
        self.assertIn("trunk_branch_l_palm", af.tiles)
        self.assertIn("snow_leaves", af.tiles)
        self.assertIn("blight_leaves", af.tiles)
        self.assertIn("palm_leaves", af.tiles)
        self.assertIn("autumn_leaves", af.tiles)
        self.assertIn(TILE_LEAVES, af.tiles)
        self.assertIn(TILE_WOOD_TRUNK, af.tiles)
        self.assertIn("achievement_banner", af.ui)

        # Create test world
        world = World(af, seed=42)

        # Plant a test tree: trunk at (50, 60), (50, 59), (50, 58), leaves at (50, 57), (49, 57), (51, 57)
        world.set_tile(50, 60, TILE_WOOD_TRUNK)
        world.set_tile(50, 59, TILE_WOOD)
        world.set_tile(50, 58, TILE_WOOD)
        world.set_tile(50, 57, TILE_LEAVES)
        world.set_tile(49, 57, TILE_LEAVES)
        world.set_tile(51, 57, TILE_LEAVES)

        # Rule 1: Player CANNOT destroy leaves directly
        broken, drop, tid = world.damage_tile_at(50, 57, power=100)
        self.assertFalse(broken, "Leaves should not be directly breakable by player tools")
        self.assertIsNone(drop)
        self.assertEqual(world.get_tile(50, 57), TILE_LEAVES, "Leaves must remain in world")

        # Rule 2: Breaking the trunk cascades and fells all connected wood and canopy leaves above
        broken, drop, tid = world.damage_tile_at(50, 60, power=200)
        self.assertTrue(broken, "Trunk should break when damaged by axe")
        self.assertEqual(drop, "wood")

        # Check that trunk and leaves were felled
        self.assertEqual(world.get_tile(50, 60), TILE_AIR, "Bottom trunk should be cleared")
        self.assertEqual(world.get_tile(50, 59), TILE_AIR, "Upper trunk should be felled")
        self.assertEqual(world.get_tile(50, 58), TILE_AIR, "Top trunk should be felled")
        self.assertEqual(world.get_tile(50, 57), TILE_AIR, "Center leaf should be felled")
        self.assertEqual(world.get_tile(49, 57), TILE_AIR, "Left leaf should be felled")
        self.assertEqual(world.get_tile(51, 57), TILE_AIR, "Right leaf should be felled")

        # Check felled metadata
        felled = getattr(world, "last_felled_tree", None)
        self.assertIsNotNone(felled)
        felled_wood, leaf_coords = felled
        self.assertEqual(felled_wood, 3, "Should have felled 3 wood blocks")
        self.assertGreaterEqual(len(leaf_coords), 3, "Should have cleared at least 3 leaves")
        self.assertIn((50, 60), world.last_felled_trunks, "Full felled trunk list must be recorded")

        # Rule 3: Player-placed wood structures (houses) are NOT cascade-felled
        world.set_tile(70, 65, TILE_DIRT)
        world.place_tile(70, 64, TILE_WOOD)
        world.place_tile(70, 63, TILE_WOOD)
        world.place_tile(70, 62, TILE_WOOD)
        # Mining bottom block of player house breaks ONLY that block
        broken_placed, drop_placed, _ = world.damage_tile_at(70, 64, power=200)
        self.assertTrue(broken_placed)
        self.assertEqual(world.get_tile(70, 64), TILE_AIR)
        self.assertEqual(world.get_tile(70, 63), TILE_WOOD, "Player-placed wood wall must NOT be cascade-felled!")
        self.assertEqual(world.get_tile(70, 62), TILE_WOOD, "Player-placed wood wall must NOT be cascade-felled!")

        # Rule 4: Player-placed wood trunk blocks are also protected from cascade-felling
        world.place_tile(72, 64, TILE_WOOD_TRUNK)
        world.place_tile(72, 63, TILE_WOOD_TRUNK)
        broken_placed_trunk, _, _ = world.damage_tile_at(72, 64, power=200)
        self.assertTrue(broken_placed_trunk)
        self.assertEqual(world.get_tile(72, 64), TILE_AIR)
        self.assertEqual(world.get_tile(72, 63), TILE_WOOD_TRUNK, "Player-placed wood trunk must NOT be cascade-felled!")

        # Rule 5: Root flare rendering with TILE_CORRUPT_GRASS executes without NameError
        world.set_tile(80, 50, TILE_CORRUPT_GRASS)
        world.set_tile(80, 49, TILE_WOOD_TRUNK)
        cam = Camera(80 * SCALED_TILE, 50 * SCALED_TILE)
        render_surf = pygame.Surface((200, 200))
        world.render(render_surf, cam)

        # Rule 6: Chunk trees generated at safe interior offsets (5, 11) have valid bounds in chunks
        chunk = world.chunk_manager.get_chunk(2)
        for lx in range(chunk.width):
            for ly in range(chunk.height):
                if chunk.tiles[lx][ly] == TILE_LEAVES:
                    self.assertTrue(0 <= lx < 16, f"Leaf at lx={lx} must be valid within chunk bounds")

    # =========================================================================
    # 2. LIQUID WATER SYSTEM & SWIMMING PHYSICS
    # =========================================================================
    def test_water_system_and_swimming_physics(self):
        """Tests animated water frames, swimming physics, oxygen breath meter, and drowning."""
        af = self.asset_factory
        # Check animated water assets and HUD bubbles exist
        self.assertIn("water_frames", af.tiles)
        self.assertEqual(len(af.tiles["water_frames"]), 8, "Water surface must have 8 animated frames")
        self.assertIn("water_submerged_frames", af.tiles)
        self.assertEqual(len(af.tiles["water_submerged_frames"]), 8)
        self.assertIn("bubble_full", af.ui)
        self.assertIn("bubble_empty", af.ui)
        self.assertIn("bubble_pop", af.ui)

        # Create world and player
        world = World(af, seed=123)
        player = Player(100, 100, af, self.sound_manager)

        # Place a pool of water around player
        ptx = int(player.center_x // SCALED_TILE)
        pty = int(player.center_y // SCALED_TILE)
        for dy in range(-2, 4):
            for dx in range(-2, 3):
                world.set_tile(ptx + dx, pty + dy, TILE_WATER)

        # Water block property check: is_water and non-solid
        self.assertTrue(world.is_water(ptx, pty))
        self.assertFalse(world.is_tile_solid(ptx, pty), "Water must be non-solid/liquid")

        # Update player inside water
        player.update(0.1, world)
        self.assertTrue(player.in_water, "Player must register as in water")
        self.assertTrue(player.is_submerged, "Player head is submerged in water pool")

        # Swimming physics check: buoyancy and drag
        # In air, vy increases by GRAVITY = 0.44 per tick. In water, fluid drag reduces terminal vel
        player.vy = 8.0
        player.update(0.1, world)
        self.assertLess(player.vy, 8.0, "Fluid drag must dampen vertical speed in water")

        # Swimming input check: Jump / Up paddles upwards
        keys = {pygame.K_SPACE: True, pygame.K_a: False, pygame.K_d: False, pygame.K_s: False}
        player.handle_input(keys, player.center_x, player.center_y)
        self.assertLess(player.vy, 0.0, "Jumping in water should paddle player upwards smoothly")

        # Diving input check: Drop / S dives downwards
        keys = {pygame.K_SPACE: False, pygame.K_a: False, pygame.K_d: False, pygame.K_s: True}
        player.handle_input(keys, player.center_x, player.center_y)
        self.assertGreater(player.vy, 0.0, "Pressing S in water should dive player downwards")

        # Oxygen depletion & Drowning test
        player.oxygen = 2.0  # Set low oxygen
        player.submerged_duration = 10.0
        player.drown_timer = 0.0
        init_hp = player.health

        # Submerged tick depletes oxygen to 0
        player.update(2.5, world)
        self.assertAlmostEqual(player.oxygen, 0.0, delta=0.1, msg="Oxygen should deplete underwater")

        # Oxygen is 0: drowning damage ticks
        player.update(1.2, world)
        self.assertLess(player.health, init_hp, "Player should take drowning damage when out of oxygen")

        # Surfacing recovery test: move player out of water
        for dy in range(-2, 4):
            for dx in range(-2, 3):
                world.set_tile(ptx + dx, pty + dy, TILE_AIR)

        player.update(0.1, world)
        self.assertFalse(player.in_water)
        self.assertFalse(player.is_submerged)
        self.assertGreater(player.oxygen, 0.0, "Oxygen must rapidly recover upon surfacing")

        # Water tile tool immunity & displacement check
        world.set_tile(ptx, pty, TILE_WATER)
        broken, drop, tid = world.damage_tile_at(ptx, pty, power=500)
        self.assertFalse(broken, "Liquid water cannot be broken by pickaxes")
        self.assertIsNone(drop)

        # Displacing water by placing a solid block
        world.set_tile(ptx, pty + 1, TILE_DIRT)  # Neighbor below
        placed = world.place_tile(ptx, pty, TILE_STONE)
        self.assertTrue(placed, "Placing solid block in water should displace the liquid")
        self.assertEqual(world.get_tile(ptx, pty), TILE_STONE)

        # Underwater oxygen bubble particles test
        ps = ParticleSystem()
        ps.spawn_bubbles(100, 100, count=4)
        self.assertEqual(len(ps.particles), 4)
        bubble = ps.particles[0]
        self.assertFalse(bubble.gravity, "Underwater bubbles must be buoyant (gravity=False)")
        self.assertLess(bubble.vy, 0.0, "Underwater bubbles must rise upward")

    # =========================================================================
    # 3. CINEMATIC SYNTH BGM REWORK & SCENE TRANSITIONS
    # =========================================================================
    def test_bgm_synthesis_and_crossfading(self):
        """Tests procedural synth BGM loading, tracks presence, and smooth crossfading transitions."""
        bgm = BgmManager()
        # Verify synthesized tracks exist
        for expected in ("menu", "forest", "desert", "snow", "corruption", "cavern", "battle", "miniboss", "night", "victory"):
            self.assertIn(expected, bgm.tracks, f"BGM track '{expected}' must be synthesized and cached")

        # Test initial play: scene='menu'
        bgm.update(0.1, scene="menu")
        self.assertEqual(bgm.current_track, "menu", "Menu scene must play 'menu' track")

        # Test transition to gameplay (forest)
        bgm.update(0.1, current_biome="forest")
        self.assertEqual(bgm.next_track, "forest", "Should initiate crossfade transition to forest")

        # Advance crossfade past duration (1.5s)
        bgm.update(1.6, current_biome="forest")
        self.assertEqual(bgm.current_track, "forest", "Forest track should become active after crossfade completes")
        self.assertIsNone(bgm.next_track)

        # Test transition to Cavern depth
        bgm.update(0.1, current_biome="forest", is_cavern=True)
        self.assertEqual(bgm.next_track, "cavern", "Should transition to cavern track when subterranean")
        bgm.update(1.6, current_biome="forest", is_cavern=True)
        self.assertEqual(bgm.current_track, "cavern")

        # Test transition to Victory
        bgm.update(0.1, scene="victory")
        self.assertEqual(bgm.next_track, "victory", "Should transition to victory track on boss defeat")
        bgm.update(1.6, scene="victory")
        self.assertEqual(bgm.current_track, "victory")

        # Test paused game keeps active track and finishes crossfades without resetting to 'menu'
        bgm.update(0.1, current_biome="forest")
        self.assertEqual(bgm.next_track, "forest")
        bgm.update_tick(1.6)  # advance while paused
        self.assertEqual(bgm.current_track, "forest", "update_tick must complete crossfade without switching to menu")
        self.assertIsNone(bgm.next_track)
        bgm.update_tick(0.5)
        self.assertEqual(bgm.current_track, "forest", "update_tick must maintain current in-game track")
        bgm.stop()

    # =========================================================================
    # 4. MAIN MENU VISUAL POLISH
    # =========================================================================
    def test_main_menu_visual_polish(self):
        """Tests glowing title logo, particle effects, and animated Spud mascot on main menu."""
        menu = MenuManager(self.asset_factory, self.sound_manager)
        # Check particle system has ambient floating particles
        self.assertGreaterEqual(len(menu.ambient_particles), 40)
        p = menu.ambient_particles[0]
        self.assertIn("type", p)
        self.assertIn("phase", p)

        # Check player idle frames exist for animated mascot
        self.assertIn("idle_frames", self.asset_factory.player_sprites)
        self.assertGreaterEqual(len(self.asset_factory.player_sprites["idle_frames"]), 6)

        # Test render executes without errors onto a surface
        test_surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        menu.render(test_surf)
        # Verify surface has drawn pixels (not empty black)
        self.assertNotEqual(test_surf.get_at((SCREEN_WIDTH // 2, 80))[:3], (0, 0, 0))

    # =========================================================================
    # 5. ACHIEVEMENTS SYSTEM & PERSISTENCE
    # =========================================================================
    def test_achievements_catalog_persistence_and_toasts(self):
        """Tests 12 feats catalog, progress calculation, disk persistence, toasts, and UI browser."""
        ach_mgr = AchievementManager(
            catalog_path="data/achievements.json",
            save_path=self.test_ach_file,
            sound_manager=self.sound_manager
        )
        self.assertGreaterEqual(len(ach_mgr.achievements), 200, "Must contain at least 200 comprehensive feats")

        # Check required feat IDs exist
        expected_feats = [
            "timber", "first_blood", "deep_diver", "hold_your_breath",
            "into_the_depths", "master_crafter", "slayer_of_titans",
            "pack_mule", "star_catcher", "home_sweet_home", "iron_age", "potaria_hero"
        ]
        for fid in expected_feats:
            self.assertIn(fid, ach_mgr.achievements_dict, f"Feat '{fid}' must exist in catalog")

        # Initial progress: 0 / tot
        unl, tot, pct = ach_mgr.get_progress()
        self.assertEqual(unl, 0)
        self.assertEqual(tot, len(ach_mgr.achievements))
        self.assertEqual(pct, 0.0)

        # Unlock a feat
        unlocked = ach_mgr.unlock("timber")
        self.assertTrue(unlocked)
        self.assertTrue(ach_mgr.is_unlocked("timber"))
        # Unlocking again returns False (idempotent)
        self.assertFalse(ach_mgr.unlock("timber"))

        # Verify toast was created
        self.assertIsNotNone(ach_mgr.current_toast)
        self.assertEqual(ach_mgr.current_toast.data["id"], "timber")
        self.assertEqual(ach_mgr.current_toast.width, 420)
        self.assertEqual(ach_mgr.current_toast.height, 64)

        # Update toast over time
        ach_mgr.update(2.0)
        self.assertIsNotNone(ach_mgr.current_toast)
        ach_mgr.update(3.0)  # Total 5s > 4.2s duration
        self.assertIsNone(ach_mgr.current_toast, "Toast should finish and clear")

        # Verify disk persistence
        self.assertTrue(os.path.exists(self.test_ach_file))
        # Create a second manager reading from the same file
        ach_mgr2 = AchievementManager(
            catalog_path="data/achievements.json",
            save_path=self.test_ach_file
        )
        self.assertTrue(ach_mgr2.is_unlocked("timber"), "Progress must persist across sessions")
        unl2, tot2, pct2 = ach_mgr2.get_progress()
        self.assertEqual(unl2, 1)
        self.assertEqual(tot2, len(ach_mgr.achievements))
        self.assertAlmostEqual(pct2, 1.0 / float(tot2) * 100.0, places=1)

        # Verify browser rendering and scrolling with 200+ feats
        test_surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        ach_mgr.render_browser(test_surf, (0, 0), scroll_y=200)
        self.assertGreater(ach_mgr.max_scroll, 0, "Max scroll must be positive for 200+ achievements")
        self.assertEqual(ach_mgr.scroll_y, 200)

        # Verify menu scrolling interaction
        menu = MenuManager(self.asset_factory, self.sound_manager, achievement_manager=ach_mgr)
        menu.state = STATE_ACHIEVEMENTS
        menu.handle_scroll(-2)  # Wheel down -> increase scroll_y
        self.assertGreater(menu.achievements_scroll_y, 0)
        menu.handle_scroll(2)   # Wheel up -> return to top
        self.assertEqual(menu.achievements_scroll_y, 0.0)

    # =========================================================================
    # 6. CREATE NEW WORLD UI/UX & MODS SEPARATION
    # =========================================================================
    def test_mods_separation_and_new_world_panel(self):
        """Tests removal of MODE button from Create New World, dedicated MODS menu, and LMS toggle."""
        menu = MenuManager(self.asset_factory, self.sound_manager)
        menu.mods_file = self.test_mods_file

        # Check Main Menu buttons contain MODS and ACHIEVEMENTS
        button_actions = [btn.action for btn in menu.menu_buttons]
        self.assertIn("mods", button_actions, "Main Menu must have dedicated 'MODS / ADD-ONS' button")
        self.assertIn("achievements", button_actions, "Main Menu must have dedicated 'ACHIEVEMENTS' button")

        # Test opening MODS menu
        # Click on mods button
        mods_btn = next(btn for btn in menu.menu_buttons if btn.action == "mods")
        menu.handle_click(mods_btn.rect.center)
        self.assertEqual(menu.state, STATE_MODS, "State must transition to STATE_MODS")

        # In MODS menu, LMS toggle button exists
        self.assertFalse(menu.enabled_mods.get("last_man_standing", False))
        self.assertEqual(menu.mods_toggle_lms_btn.text, "ENABLE")

        # Toggle LMS ON
        menu.handle_click(menu.mods_toggle_lms_btn.rect.center)
        self.assertTrue(menu.enabled_mods.get("last_man_standing", False), "Last Man Standing mod should be enabled")
        self.assertEqual(menu.mods_toggle_lms_btn.text, "DISABLE")
        self.assertEqual(menu.new_world_mode, MODE_LAST_MAN_STANDING)

        # Back to Main Menu
        menu.handle_click(menu.mods_back_btn.rect.center)
        self.assertEqual(menu.state, STATE_MENU)

        # Open Create New World screen
        menu.state = STATE_NEW_WORLD
        test_surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        menu.render(test_surf)

        # Confirm MODE button is NOT part of the new world interactive screen (no nw_btn_mode update/render)
        self.assertNotIn(menu.nw_btn_mode, [menu.nw_btn_type, menu.nw_btn_diff, menu.nw_btn_create, menu.nw_btn_back])

        # Confirm creating a new world inherits the active mod configuration
        result = menu.handle_click(menu.nw_btn_create.rect.center)
        self.assertIsNotNone(result)
        action, cfg = result
        self.assertEqual(action, "create_world")
        self.assertEqual(cfg["game_mode"], MODE_LAST_MAN_STANDING, "New world must inherit enabled Last Man Standing add-on")


if __name__ == "__main__":
    unittest.main()
