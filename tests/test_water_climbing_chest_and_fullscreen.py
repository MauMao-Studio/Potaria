"""
Potaria - Verification Suite for Water Submersion, Half-Buoyancy, Dropped Item Transparency,
Rope Rungs & Scaffolding Climbing, Storage Chest Foreground Dragging, and Borderless Fullscreen.
Developer: Kurados
"""

import os
import sys
import unittest
from unittest.mock import patch
import pygame

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")


class DummySound:
    def __init__(self):
        self.played = []

    def play(self, sound_name):
        self.played.append(sound_name)


class TestWaterClimbingChestAndFullscreen(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pygame.init()
        pygame.display.set_mode((1280, 720))
        from src.assets.asset_factory import AssetFactory
        cls.factory = AssetFactory()
        cls.sound = DummySound()

    def setUp(self):
        from src.world.world import World
        from src.entities.player import Player
        from src.ui.inventory import Inventory
        self.world = World(self.factory, seed=42424)
        self.player = Player(200, 200, self.factory, self.sound)
        self.inventory = Inventory(self.factory)
        self.player.inventory = self.inventory

    def _clear_area(self, tx_min, tx_max, ty_min, ty_max):
        from src.constants import TILE_AIR
        for tx in range(tx_min, tx_max + 1):
            for ty in range(ty_min, ty_max + 1):
                self.world.set_tile(tx, ty, TILE_AIR)

    def test_01_borderless_fullscreen_prevents_exclusive_lock_blackout(self):
        """Verifies GLRenderer and SurfaceRenderer use borderless fullscreen (NOFRAME) instead of exclusive FULLSCREEN."""
        from src.rendering.gl_renderer import GLRenderer
        from src.rendering.surface_renderer import SurfaceRenderer

        recorded_calls = []
        orig_set_mode = pygame.display.set_mode

        def spy_set_mode(size, flags=0, *args, **kwargs):
            recorded_calls.append((size, flags, os.environ.get("SDL_VIDEO_WINDOW_POS", "")))
            return orig_set_mode((1280, 720))

        with patch("pygame.display.set_mode", side_effect=spy_set_mode):
            surf_rend = SurfaceRenderer(width=1280, height=720, fullscreen=True)
            surf_rend.initialize()
            self.assertTrue(len(recorded_calls) >= 1)
            _, flags_fs, pos_fs = recorded_calls[-1]
            self.assertTrue(flags_fs & pygame.NOFRAME, "Fullscreen SurfaceRenderer must use pygame.NOFRAME")
            self.assertFalse(flags_fs & pygame.FULLSCREEN, "Fullscreen SurfaceRenderer must not use exclusive pygame.FULLSCREEN")
            self.assertEqual(pos_fs, "0,0")

            surf_rend.set_mode(1280, 720, fullscreen=False)
            _, flags_win, pos_win = recorded_calls[-1]
            self.assertFalse(flags_win & pygame.FULLSCREEN)
            self.assertEqual(pos_win, "centered")

            gl_rend = GLRenderer(width=1280, height=720, fullscreen=True)
            gl_rend._apply_display_mode()
            _, gl_flags_fs, gl_pos_fs = recorded_calls[-1]
            self.assertTrue(gl_flags_fs & pygame.NOFRAME, "Fullscreen GLRenderer must use borderless pygame.NOFRAME")
            self.assertFalse(gl_flags_fs & pygame.FULLSCREEN, "Fullscreen GLRenderer must not use exclusive pygame.FULLSCREEN")
            self.assertEqual(gl_pos_fs, "0,0")

    def test_02_water_requires_lower_body_submersion_and_no_blue_box_overlay(self):
        """Verifies in_water requires lower-body submersion and sprites in water have zero blue square box."""
        from src.constants import SCALED_TILE, TILE_AIR, TILE_STONE, TILE_WATER
        from src.entities.mob import GreenSlime
        from src.entities.dropped_item import DroppedItem
        from src.camera import Camera

        self._clear_area(0, 15, 0, 15)
        # Solid ground at ty=6 (y=192)
        for tx in range(0, 12):
            self.world.set_tile(tx, 6, TILE_STONE)

        # Place water only at tx=6, ty=5 (x=192..224, y=160..192)
        self.world.set_tile(6, 5, TILE_WATER)

        # 1. Player standing on dry land right next to water (x=192 - player.width + 1 -> 1px edge touch)
        self.player.x = float(6 * SCALED_TILE - self.player.width + 1)
        self.player.y = float(6 * SCALED_TILE - self.player.height)
        self.player.update(0.016, self.world)
        self.assertFalse(self.player.in_water, "Standing next to water with 1px edge contact must not trigger in_water")

        # 2. Player with only upper body overlapping water (ty=4 has water, lower body at ty=5 is dry)
        self.world.set_tile(6, 5, TILE_AIR)
        self.world.set_tile(6, 4, TILE_WATER)
        self.player.x = float(6 * SCALED_TILE + 2)
        self.player.y = float(5 * SCALED_TILE - 6)  # Top 6px in ty=4, lower body in ty=5 (dry)
        self.player.update(0.016, self.world)
        self.assertFalse(self.player.in_water, "Upper-head contact without lower-body submersion must not trigger in_water")

        # 3. Player with lower body submerged in water at (6, 5)
        self.world.set_tile(6, 5, TILE_WATER)
        self.player.x = float(6 * SCALED_TILE + 2)
        self.player.y = float(6 * SCALED_TILE - self.player.height)
        self.player.update(0.016, self.world)
        self.assertTrue(self.player.in_water, "Lower-body submersion must set in_water=True")

        # 4. Verify rendering Player, Slime, and DroppedItem in water produces zero blue box on transparent corners
        cam = Camera(1280, 720)
        cam.x = 0
        cam.y = 0

        canvas = pygame.Surface((400, 400), pygame.SRCALPHA)
        canvas.fill((0, 0, 0, 0))
        self.player.x = 100.0
        self.player.y = 100.0
        self.player.in_water = True
        self.player.is_submerged = True
        self.player.render(canvas, cam)
        draw_sy = int(100 - self.player.sprout_offset_y)
        self.assertEqual(canvas.get_at((100, draw_sy))[3], 0, "Top-left corner of player bounding box in water must be transparent")

        slime = GreenSlime(200, 100, self.factory)
        slime.in_water = True
        test_surf = pygame.Surface((28, 22), pygame.SRCALPHA)
        overlayed = slime.apply_water_overlay(test_surf)
        self.assertEqual(overlayed.get_at((0, 0))[3], 0, "Mob apply_water_overlay must not tint transparent pixels blue")

        drop = DroppedItem("copper_ore", 1, 300, 100, self.factory)
        drop.in_water = True
        canvas.fill((0, 0, 0, 0))
        drop.render(canvas, cam)
        self.assertEqual(canvas.get_at((296, 96))[3], 0, "Dropped item in water must not have a blue square box")

    def test_03_enemy_half_buoyancy_sinks_slowly_and_jumps_slowly_in_water(self):
        """Verifies enemies in water have half buoyancy (slow downward sink) and can jump slowly upward in water."""
        from src.constants import SCALED_TILE, TILE_STONE, TILE_WATER
        from src.entities.mob import GreenSlime, Zombie, DesertScorpion

        self._clear_area(0, 15, 0, 15)
        # Create a 4-tile deep water pool at tx=4..8, ty=5..8 with solid floor at ty=9 and wall at tx=7
        for tx in range(3, 10):
            self.world.set_tile(tx, 9, TILE_STONE)
            for ty in range(5, 9):
                self.world.set_tile(tx, ty, TILE_WATER)

        slime = GreenSlime(5 * SCALED_TILE, 6 * SCALED_TILE, self.factory)
        slime.vy = 0.0
        slime.jump_cooldown = 5.0
        slime.update(0.016, self.world, self.player)
        self.assertTrue(slime.in_water)
        self.assertGreater(slime.vy, 0.0, "Enemy with half buoyancy must sink slowly downward (vy > 0), not float upward")
        self.assertLess(slime.vy, 1.5, "Enemy sinking speed in water must be damped by half buoyancy")

        # Verify slime in water performs a slow upward jump when jump cooldown expires
        slime.state = "squishing"
        slime.squish_timer = 0.001
        slime.vy = 0.2
        slime.update(0.02, self.world, self.player)
        self.assertLess(slime.vy, -1.5, "Slime must be able to jump upward in water")
        self.assertGreater(slime.vy, -5.0, "Slime water jump must be slower than dry-land jump (-7.0)")

        # Verify zombie in water jumps slowly when obstructed by a 1-block ledge or pursuing player above
        self.world.set_tile(6, 8, TILE_STONE)  # 1-block underwater step at (6, 8)
        zombie = Zombie(5 * SCALED_TILE + 8, 9 * SCALED_TILE - 44, self.factory)
        self.player.x = 8 * SCALED_TILE
        self.player.y = 4 * SCALED_TILE
        zombie.on_ground = True
        zombie.update(0.016, self.world, self.player)
        self.assertTrue(zombie.in_water)
        self.assertLess(zombie.vy, -1.5, "Zombie must jump upward in water when obstructed")
        self.assertGreater(zombie.vy, -5.0, "Zombie water jump must be slow (-3.4*0.9)")

        scorpion = DesertScorpion(5 * SCALED_TILE + 4, 9 * SCALED_TILE - 22, self.factory)
        scorpion.on_ground = True
        scorpion.update(0.016, self.world, self.player)
        self.assertTrue(scorpion.in_water)
        self.assertLess(scorpion.vy, -1.5)
        self.assertGreater(scorpion.vy, -5.0)

    def test_04_dropped_items_and_blocks_have_transparent_corners_no_square_box(self):
        """Verifies all mob drops, ores, natural blocks, and every item icon in AssetFactory.items have transparent corners."""
        items_to_check = set(self.factory.items.keys()) | {
            "copper_ore", "iron_ore", "gold_ore",
            "dirt_block", "sand_block", "stone_block", "wood", "leaves",
            "snow_block", "ice_block", "sandstone_block", "blightstone_block",
            "cactus", "rope_rungs", "iron_storage_chest",
        }

        for item_id in sorted(items_to_check):
            icon = self.factory.items.get(item_id)
            self.assertIsNotNone(icon, f"Missing icon for {item_id}")
            w, h = icon.get_size()
            corners = [
                icon.get_at((0, 0))[3],
                icon.get_at((w - 1, 0))[3],
                icon.get_at((0, h - 1))[3],
                icon.get_at((w - 1, h - 1))[3],
            ]
            self.assertEqual(
                corners, [0, 0, 0, 0],
                f"Item icon '{item_id}' has opaque square box corners {corners} instead of transparent background"
            )

    def test_05_rope_rungs_and_scaffolding_climbing_up_and_down(self):
        """Verifies player can climb up, climb down, and cling on TILE_ROPE_RUNGS and climb TILE_WOOD_PLATFORM scaffolding."""
        from src.constants import SCALED_TILE, TILE_ROPE_RUNGS, TILE_WOOD_PLATFORM, TILE_STONE

        self._clear_area(0, 15, 0, 15)
        for tx in range(0, 12):
            self.world.set_tile(tx, 10, TILE_STONE)

        # Build a vertical column of Rope Rungs at tx=5, ty=4..9
        for ty in range(4, 10):
            self.world.set_tile(5, ty, TILE_ROPE_RUNGS)

        self.player.x = float(5 * SCALED_TILE + 2)
        self.player.y = float(7 * SCALED_TILE)
        self.player.vy = 2.0

        # 1. No vertical input on rope rungs -> clings in place (vy == 0)
        self.player.handle_input({}, self.player.center_x, self.player.center_y, world=self.world)
        self.player.update(0.016, self.world)
        self.assertTrue(self.player.on_rope_rungs)
        self.assertEqual(self.player.vy, 0.0, "Player on rope rungs with no input must cling without falling")
        self.assertTrue(self.player.on_ground)

        # 2. Holding W climbs upward on rope rungs
        start_y = self.player.y
        for _ in range(10):
            self.player.handle_input({pygame.K_w: True}, self.player.center_x, self.player.center_y, world=self.world)
            self.player.update(0.016, self.world)
        self.assertLess(self.player.y, start_y - 20.0, "Holding W on rope rungs must climb upward")

        # 3. Holding S climbs downward on rope rungs through platform tops
        mid_y = self.player.y
        for _ in range(10):
            self.player.handle_input({pygame.K_s: True}, self.player.center_x, self.player.center_y, world=self.world)
            self.player.update(0.016, self.world)
        self.assertGreater(self.player.y, mid_y + 20.0, "Holding S on rope rungs must climb downward smoothly")

        # 4. Build a vertical column of scaffolding (TILE_WOOD_PLATFORM) at tx=8, ty=4..9
        for ty in range(4, 10):
            self.world.set_tile(8, ty, TILE_WOOD_PLATFORM)

        self.player.x = float(8 * SCALED_TILE + 2)
        self.player.y = float(7 * SCALED_TILE)
        scaf_start_y = self.player.y
        for _ in range(10):
            self.player.handle_input({pygame.K_w: True}, self.player.center_x, self.player.center_y, world=self.world)
            self.player.update(0.016, self.world)
        self.assertLess(self.player.y, scaf_start_y - 20.0, "Holding W inside scaffolding column must climb upward")

        scaf_mid_y = self.player.y
        for _ in range(10):
            self.player.handle_input({pygame.K_s: True}, self.player.center_x, self.player.center_y, world=self.world)
            self.player.update(0.016, self.world)
        self.assertGreater(self.player.y, scaf_mid_y + 20.0, "Holding S inside scaffolding column must descend downward")

    def test_06_chest_ui_dragged_item_renders_in_foreground(self):
        """Verifies dragged items (inventory.held_item) render in front of ChestStorageWindow instead of behind it."""
        from src.ui.chest_ui import ChestStorageWindow
        from src.ui.hud import HUD
        from src.ui.crafting import CraftingSystem
        from src.ui.inventory import ItemStack
        from src.world.storage_chest import StorageChest
        from src.camera import Camera

        chest_ui = ChestStorageWindow(self.factory, self.sound)
        hud = HUD(self.factory)
        crafting = CraftingSystem(self.factory, self.sound)
        cam = Camera(1280, 720)
        chest = StorageChest(5, 5)
        chest_ui.open(chest, self.player, self.inventory)

        # Pick a cursor point inside the ChestStorageWindow header/background where no slot icon is drawn
        mx = chest_ui.x + chest_ui.width - 60
        my = chest_ui.y + 16

        surf_without_held = pygame.Surface((1280, 720), pygame.SRCALPHA)
        self.inventory.held_item = None
        hud.render(surf_without_held, self.player, self.inventory, crafting, cam, mx, my, world=self.world)
        chest_ui.render(surf_without_held, self.inventory, mx, my)
        hud.render_dragged_item(surf_without_held, self.inventory, mx, my)

        surf_with_held = pygame.Surface((1280, 720), pygame.SRCALPHA)
        self.inventory.held_item = ItemStack("gold_broadsword", 1)
        hud.render(surf_with_held, self.player, self.inventory, crafting, cam, mx, my, world=self.world)
        chest_ui.render(surf_with_held, self.inventory, mx, my)
        hud.render_dragged_item(surf_with_held, self.inventory, mx, my)

        # Compare the 24x24 region around (mx, my) to prove the dragged item icon was drawn on top of the chest panel
        diff_pixels = 0
        for dx in range(-12, 12):
            for dy in range(-12, 12):
                if surf_without_held.get_at((mx + dx, my + dy)) != surf_with_held.get_at((mx + dx, my + dy)):
                    diff_pixels += 1
        self.assertGreater(diff_pixels, 20, "Dragged item must be rendered in the foreground on top of the Chest UI")


if __name__ == "__main__":
    unittest.main()
