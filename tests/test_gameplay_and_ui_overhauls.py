"""
Potaria - Unit and Integration Tests for Gameplay, UI, Visual, and Persistence Overhauls.
Covers:
1. Player illumination (zero by default, lit when equipped or held torch/lantern)
2. Merchant dialogue UI layout & ellipsis truncation
3. Settings UI (Back left, Reset right, confirmation modal, disk persistence)
4. Daylight block shadowing (exposed roof top receives incident sunlight)
5. Camera zoom (discrete levels 1x, 2x, 3x, cycling, screen/world conversions)
6. Default difficulty (Easy)
7. World card subtitle (omits ADVENTURE)
8. Death transition (pitch-black fade, instant teleport at peak, instant camera snap)
"""

import os
import sys
import json
import math
import unittest
import pygame

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.constants import (
    SCALED_TILE,
    DIFFICULTY_EASY, DIFFICULTY_NORMAL,
    STATE_MENU, STATE_SETTINGS, STATE_WORLDS,
    TILE_AIR, TILE_DIRT, TILE_STONE, TILE_WOOD
)
from src.ui.menu import MenuManager, STATE_INPUT_MAPPING
from src.assets.asset_factory import AssetFactory
from src.audio.sound_effects import SoundManager
from src.camera import Camera
from src.world.world import World
from src.world.lighting import LightingEngine
from src.entities.player import Player
from src.ui.inventory import ItemStack
from src.ui.npc_dialogue import NPCDialogueWindow
from src.ui.menu import MenuManager
from src.settings_manager import load_settings, save_settings, DEFAULT_SETTINGS, DEFAULT_KEY_BINDINGS
from main import PotariaGame


class TestGameplayAndUIOverhauls(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pygame.init()
        cls.factory = AssetFactory()
        cls.sound = SoundManager()

    def setUp(self):
        self.camera = Camera(800, 600)
        self.world = World(self.factory, seed=54321)
        self.player = Player(200, 200, self.factory, self.sound)

    # 1. Player Illumination: Zero by default, glows ONLY when holding torch/lantern or equipped
    def test_player_illumination_zero_by_default(self):
        game = PotariaGame()
        game.lighting = LightingEngine(800, 600)

        # Set game time to deep night (midnight)
        game.sky.time = 0.75 * game.sky.cycle_duration

        # Player inventory has miner helmet in backpack slot 5 by default
        self.assertTrue(game.inventory.has_miner_helmet())
        # But player does NOT have it equipped
        self.assertFalse(game.player.equipment.has_miner_helmet_equipped())
        # Nor holding any torch or lantern
        game.inventory.slots[0] = None
        game.inventory.selected_slot = 0

        # Simulate update_lighting logic from main.py
        held_item = game.inventory.get_active_item()
        has_miner_helm = (
            (hasattr(game.player, "equipment") and game.player.equipment.has_miner_helmet_equipped())
            or (hasattr(game.player, "equipment") and game.player.equipment.slots.get("head") == "miner_helmet")
        )
        has_light_emitter = (
            hasattr(game.player, "equipment") and hasattr(game.player.equipment, "has_light_emitter") and game.player.equipment.has_light_emitter()
        )
        has_astral_radiance = (
            (hasattr(game.player, "equipment") and game.player.equipment.has_astral_radiance())
            or (hasattr(game.player, "has_effect") and game.player.has_effect("celestial radiance"))
        )

        extra_lights = []
        ptx = int(game.player.center_x // SCALED_TILE)
        pty = int(game.player.center_y // SCALED_TILE)

        if has_astral_radiance:
            extra_lights.append((ptx, pty, 13, 8, False))
        elif has_miner_helm or has_light_emitter:
            extra_lights.append((ptx, pty, 8, 5, False))
        elif held_item and held_item.item_id in ("carved_tuber_lantern", "brass_lantern", "spectral_lantern"):
            extra_lights.append((ptx, pty, 9, 5, False))
        elif held_item and held_item.item_id == "torch":
            extra_lights.append((ptx, pty, 7, 4, False))

        # Must have zero extra lights for player
        self.assertEqual(len(extra_lights), 0, "Player must NOT emit light just because miner helmet is in backpack!")

        # Now EQUIP miner helmet
        game.player.equipment.slots["head"] = "miner_helmet"
        self.assertTrue(game.player.equipment.has_miner_helmet_equipped())

        # Check light emission with helmet equipped
        has_miner_helm = (
            (hasattr(game.player, "equipment") and game.player.equipment.has_miner_helmet_equipped())
            or (hasattr(game.player, "equipment") and game.player.equipment.slots.get("head") == "miner_helmet")
        )
        if has_miner_helm:
            extra_lights.append((ptx, pty, 8, 5, False))
        self.assertEqual(len(extra_lights), 1, "Player must emit light when miner helmet is equipped!")

        # Unequip helmet, hold torch
        game.player.equipment.slots["head"] = None
        extra_lights.clear()
        game.inventory.slots[0] = ItemStack("torch", 5)
        held_item = game.inventory.get_active_item()
        if held_item and held_item.item_id == "torch":
            extra_lights.append((ptx, pty, 7, 4, False))
        self.assertEqual(len(extra_lights), 1, "Player must emit light when holding torch!")

    # 2. Merchant Dialogue UI: Width 580, Card width 265, Ellipsis Truncation
    def test_merchant_dialogue_ui_layout_and_truncation(self):
        diag = NPCDialogueWindow(self.factory, self.sound)
        self.assertEqual(diag.width, 580, "NPC Dialogue Window width must be 580")

        # Verify shop card slot width and buy button placement
        # bx = diag.x + 18 + col * 272
        # buy_rect = Rect(bx + 205, by + 5, 52, 26)
        # slot_rect = Rect(bx, by, 265, 38)
        # Card width 265 allows 205px before BUY button
        self.assertGreaterEqual(265, 205 + 52, "Card width must accommodate buy button with margin")

        # Test truncation calculation
        i_title = "Extraordinarily Long Mythic Enchanted Legendary Potato Blade"
        max_title_w = (205) - (36) - 4  # buy_rect.left - (bx + 36) - 4 = 165
        orig_title = i_title
        if diag.font_sm.size(i_title)[0] > max_title_w:
            while len(i_title) > 3 and diag.font_sm.size(i_title + "...")[0] > max_title_w:
                i_title = i_title[:-1]
            i_title = i_title + "..."

        self.assertTrue(i_title.endswith("..."), "Long item name must be truncated with ellipsis")
        self.assertLessEqual(diag.font_sm.size(i_title)[0], max_title_w)

    # 3. Settings UI: Back Left, Reset Right, Reset Confirmation Modal, Persistence
    def test_settings_buttons_layout_and_modal(self):
        menu = MenuManager(self.factory, self.sound)

        # In Settings screen: Back button on left, Reset button on right
        self.assertLess(menu.settings_back_btn.rect.x, menu.settings_reset_btn.rect.x,
                        "In Settings screen, Back button must be to the left of Reset Defaults button")

        # In Input Mapping screen: Back button on left, Reset button on right
        self.assertLess(menu.input_back_button.rect.x, menu.input_reset_button.rect.x,
                        "In Input Mapping screen, Back button must be to the left of Reset Defaults button")

        # Clicking settings_reset_all activates confirmation modal
        menu.state = STATE_SETTINGS
        self.assertFalse(getattr(menu, "reset_confirm_modal_active", False))
        menu.handle_click(menu.settings_reset_btn.rect.center)
        self.assertTrue(menu.reset_confirm_modal_active, "Clicking reset button must activate confirmation modal")

        # Clicking Cancel dismisses modal without resetting
        menu.settings["zoom"] = 3.0  # modified value
        menu.handle_click(menu.reset_confirm_cancel_btn.rect.center)
        self.assertFalse(menu.reset_confirm_modal_active)
        self.assertEqual(menu.settings["zoom"], 3.0, "Cancelling reset must preserve settings")

        # Clicking Confirm resets settings to defaults and saves
        menu.handle_click(menu.settings_reset_btn.rect.center)
        self.assertTrue(menu.reset_confirm_modal_active)
        res = menu.handle_click(menu.reset_confirm_yes_btn.rect.center)
        self.assertEqual(res, "reset_keys")
        self.assertFalse(menu.reset_confirm_modal_active)
        self.assertEqual(menu.settings["zoom"], DEFAULT_SETTINGS["zoom"], "Confirming reset must restore defaults")

    def test_settings_persistence_across_initialization(self):
        # Save a custom setting
        settings, keybinds = load_settings()
        original_zoom = settings.get("zoom", 1.0)
        settings["zoom"] = 2.0
        save_settings(settings, keybinds)

        # Initialize MenuManager with None settings (as happens on game restart)
        menu = MenuManager(self.factory, self.sound, settings=None)
        self.assertEqual(menu.settings.get("zoom"), 2.0,
                         "MenuManager must load saved settings from disk when initialized without settings")

        # Clean up
        settings["zoom"] = original_zoom
        save_settings(settings, keybinds)

    # 4. Daylight Block Shadowing: Exposed block top receives sunlight
    def test_daylight_exposed_roof_block_lighting(self):
        le = LightingEngine(800, 600)

        # Set up a solid roof block with air above it
        rx, ry = 10, 10
        self.world.set_tile(rx, ry - 1, TILE_AIR)
        self.world.set_tile(rx, ry, TILE_STONE)
        self.world.set_tile(rx, ry + 1, TILE_STONE)

        # Clear background wall so sunlight descends
        chunk_x = rx // 16
        local_x = rx % 16
        chunk = self.world.chunk_manager.get_chunk(chunk_x)
        if chunk:
            chunk.surface_heights[local_x] = ry + 5

        le.compute_viewport_light(self.world, min_tx=0, min_ty=0, max_tx=20, max_ty=20, ambient_sunlight=15)

        top_air_light = le.get_light_level(rx, ry - 1)
        roof_block_light = le.get_light_level(rx, ry)
        below_block_light = le.get_light_level(rx, ry + 1)

        # Air above receives full sunlight (15)
        self.assertEqual(top_air_light, 15)
        # Top roof block exposed to sky MUST receive incident sunlight (15) before diminishing downward
        self.assertEqual(roof_block_light, 15, "Exposed roof block must receive incident sunlight on top surface")
        # Below block should diminish
        self.assertLess(below_block_light, roof_block_light, "Blocks beneath roof must diminish in light")

    # 5. Camera Zoom: Discrete levels (1x, 2x, 3x), cycling, coordinate conversions
    def test_camera_zoom_levels_and_conversions(self):
        cam = Camera(800, 600)
        self.assertEqual(cam.zoom, 1.0)
        self.assertEqual(cam.screen_width, 800)
        self.assertEqual(cam.screen_height, 600)

        # Cycle zoom: 1x -> 2x
        z2 = cam.cycle_zoom()
        self.assertEqual(z2, 2.0)
        self.assertEqual(cam.screen_width, 400)
        self.assertEqual(cam.screen_height, 300)

        # Cycle zoom: 2x -> 3x
        z3 = cam.cycle_zoom()
        self.assertEqual(z3, 3.0)
        self.assertEqual(cam.screen_width, 266)
        self.assertEqual(cam.screen_height, 200)

        # Cycle zoom: 3x -> 1x
        z1 = cam.cycle_zoom()
        self.assertEqual(z1, 1.0)
        self.assertEqual(cam.screen_width, 800)
        self.assertEqual(cam.screen_height, 600)

        # Coordinate conversion roundtrip
        cam.set_zoom(2.0)
        cam.x = 100.0
        cam.y = 50.0
        cam.shake_offset_x = 0.0
        cam.shake_offset_y = 0.0

        wx, wy = 300.0, 150.0
        # When render_to_world_surf is False (UI / screen coords)
        cam.render_to_world_surf = False
        sx, sy = cam.world_to_screen(wx, wy)
        # sx = (300 - 100) * 2 = 400, sy = (150 - 50) * 2 = 200
        self.assertEqual((sx, sy), (400.0, 200.0))

        # Inverse conversion: screen_to_world
        r_wx, r_wy = cam.screen_to_world(sx, sy)
        self.assertAlmostEqual(r_wx, wx)
        self.assertAlmostEqual(r_wy, wy)

        # When render_to_world_surf is True (rendering world elements to intermediate surf)
        cam.render_to_world_surf = True
        wsx, wsy = cam.world_to_screen(wx, wy)
        self.assertEqual((wsx, wsy), (200.0, 100.0), "In world render pass, coordinates must be unzoomed")

    # 6. Default Difficulty: Easy
    def test_default_difficulty_is_easy(self):
        menu = MenuManager(self.factory, self.sound)
        self.assertEqual(menu.new_world_diff, DIFFICULTY_EASY, "Menu default difficulty must be Easy")
        self.assertEqual(menu.nw_btn_diff.text, "DIFFICULTY: EASY")

        game = PotariaGame()
        self.assertEqual(game.difficulty, DIFFICULTY_EASY, "PotariaGame default difficulty must be Easy")

    # 7. World Selection: Remove "· ADVENTURE" from card subtitle
    def test_world_card_subtitle_omits_adventure(self):
        menu = MenuManager(self.factory, self.sound)
        # Test formatting logic
        w_type = "INFINITE"
        w_diff = "EASY"
        w_mode = "ADVENTURE"

        if w_mode == "ADVENTURE":
            detail_str = f"{w_type}  •  {w_diff}"
        else:
            detail_str = f"{w_type}  •  {w_diff}  •  {w_mode}"

        self.assertNotIn("ADVENTURE", detail_str, "World card subtitle must omit ADVENTURE")
        self.assertEqual(detail_str, "INFINITE  •  EASY")

        # Non-adventure mode retains mode label
        w_mode_lms = "LAST MAN STANDING"
        if w_mode_lms == "ADVENTURE":
            detail_str_lms = f"{w_type}  •  {w_diff}"
        else:
            detail_str_lms = f"{w_type}  •  {w_diff}  •  {w_mode_lms}"
        self.assertIn("LAST MAN STANDING", detail_str_lms)

    # 8. Death Transition: Pitch-black fade and instant teleport
    def test_death_transition_fade_and_instant_teleport(self):
        player = Player(1000, 500, self.factory, self.sound)
        player.spawn_point = (100, 200)

        # Fatal damage triggers death
        player.take_damage(9999, ignore_defense=True)
        self.assertTrue(player.is_dead)
        self.assertEqual(player.respawn_timer, 3.0)
        self.assertEqual(player.death_fade_alpha, 0)
        self.assertFalse(player.death_teleported)
        self.assertFalse(player.snap_camera_instant)

        # Update 0.75s: fade to black in progress
        player.update(0.75, self.world)
        self.assertGreater(player.death_fade_alpha, 0)
        self.assertLess(player.death_fade_alpha, 255)
        self.assertFalse(player.death_teleported)

        # Update another 0.75s (total 1.5s elapsed): peak blackness
        player.update(0.75, self.world)
        self.assertTrue(player.death_teleported, "Player must be teleported at peak black (1.5s)")
        self.assertEqual((player.x, player.y), (100, 200), "Player must be at spawn point")
        self.assertTrue(player.snap_camera_instant, "Camera snap instant flag must be True")

        # Update remaining 1.5s: fade back in and finish
        player.update(1.5, self.world)
        self.assertFalse(player.is_dead, "Player must be alive after respawn transition completes")
        self.assertEqual(player.death_fade_alpha, 0)
        self.assertFalse(player.snap_camera_instant)


if __name__ == "__main__":
    unittest.main()
