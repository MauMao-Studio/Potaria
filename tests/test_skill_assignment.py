"""
Potaria - Unit Tests for Skill Loadout Assignment and Character Panel UI
Tests assigning skills to hotkeys (Q, F, V, R), swapping, unbinding,
clicking order (Hotkey->Skill and Skill->Hotkey), key rebinding, and save persistence.
Developer: Kurados
"""

import os
import unittest
import pygame

# Headless display setup for headless test runner
os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"
pygame.init()
pygame.display.set_mode((1280, 720))

from src.constants import SCREEN_WIDTH, SCREEN_HEIGHT
from src.assets.asset_factory import AssetFactory
from src.audio.sound_effects import SoundManager
from src.entities.player import Player
from src.ui.inventory import Inventory
from src.ui.character_panel import CharacterPanel
from src.rpg.skills import SkillManager, SKILL_DEFINITIONS
from src.world.world import World
from src.world.save_manager import save_world, load_world, delete_world


class TestSkillAssignment(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.factory = AssetFactory()
        cls.sounds = SoundManager()

    def setUp(self):
        self.world = World(self.factory, seed=42)
        self.player = Player(100, 100, self.factory, self.sounds)
        self.inventory = Inventory(self.factory)
        self.player.inventory = self.inventory
        self.inventory.player = self.player
        self.char_panel = CharacterPanel(self.factory)

    def test_assign_skill_empty_bindings(self):
        """Verify assign_skill works even when hotkey_bindings is empty."""
        sm = SkillManager()
        sm.hotkey_bindings = {}  # Simulate previously empty bindings
        sm.learned_skills = {"dash"}

        # Attempt to assign to F
        success = sm.assign_skill("F", "dash")
        self.assertTrue(success, "assign_skill to 'F' should succeed even if hotkey_bindings was empty")
        self.assertEqual(sm.hotkey_bindings.get("F"), "dash")

    def test_assign_skill_swap_behavior(self):
        """Verify assigning an already-bound skill to another slot swaps or clears previous slot."""
        sm = SkillManager()
        sm.learned_skills = {"power_slash", "dash"}
        sm.hotkey_bindings = {"Q": "power_slash", "F": None, "V": "dash", "R": None}

        # Assign dash (currently on V) to F
        success = sm.assign_skill("F", "dash")
        self.assertTrue(success)
        self.assertEqual(sm.hotkey_bindings.get("F"), "dash")
        self.assertIsNone(sm.hotkey_bindings.get("V"), "Old slot V should be None after swap with empty F")

        # Now assign power_slash (on Q) to F (which has dash) -> should swap!
        success = sm.assign_skill("F", "power_slash")
        self.assertTrue(success)
        self.assertEqual(sm.hotkey_bindings.get("F"), "power_slash")
        self.assertEqual(sm.hotkey_bindings.get("Q"), "dash", "Q and F should swap their skills")

    def test_assign_skill_unbind(self):
        """Verify passing skill_id=None unbinds the hotkey."""
        sm = SkillManager()
        sm.learned_skills = {"power_slash"}
        sm.hotkey_bindings = {"Q": "power_slash", "F": None, "V": None, "R": None}

        success = sm.assign_skill("Q", None)
        self.assertTrue(success)
        self.assertIsNone(sm.hotkey_bindings.get("Q"))

    def test_character_panel_click_hotkey_then_skill(self):
        """User Workflow A: Click hotkey slot [F], then click learned skill 'dash' in grimoire."""
        self.char_panel.is_open = True
        self.player.skills.learned_skills = {"dash"}
        self.player.skills.hotkey_bindings = {"Q": None, "F": None, "V": "dash", "R": None}

        screen = pygame.display.get_surface()
        self.char_panel.render(screen, self.player, 0, 0)

        # 1. Click hotkey F button
        f_rect = self.char_panel.hotkey_rects["F"]
        handled = self.char_panel.handle_click(f_rect.centerx, f_rect.centery, self.player, self.inventory)
        self.assertTrue(handled)
        self.assertEqual(self.char_panel.selected_hotkey, "F")

        # 2. Click dash in grimoire
        dash_rect = self.char_panel.grimoire_rects["dash"]
        handled = self.char_panel.handle_click(dash_rect.centerx, dash_rect.centery, self.player, self.inventory)
        self.assertTrue(handled)
        self.assertEqual(self.player.skills.hotkey_bindings.get("F"), "dash", "Slot F should now have dash")

    def test_character_panel_click_skill_then_hotkey(self):
        """User Workflow B: Click learned skill 'dash' first, then click hotkey slot [F]."""
        self.char_panel.is_open = True
        self.player.skills.learned_skills = {"dash"}
        self.player.skills.hotkey_bindings = {"Q": None, "F": None, "V": None, "R": None}

        screen = pygame.display.get_surface()
        self.char_panel.render(screen, self.player, 0, 0)

        # 1. Click dash in grimoire first
        dash_rect = self.char_panel.grimoire_rects["dash"]
        handled = self.char_panel.handle_click(dash_rect.centerx, dash_rect.centery, self.player, self.inventory)
        self.assertTrue(handled)
        self.assertEqual(self.char_panel.selected_grimoire_skill, "dash")

        # 2. Click slot [F]
        f_rect = self.char_panel.hotkey_rects["F"]
        handled = self.char_panel.handle_click(f_rect.centerx, f_rect.centery, self.player, self.inventory)
        self.assertTrue(handled)
        self.assertEqual(self.player.skills.hotkey_bindings.get("F"), "dash", "Slot F should receive dash")
        self.assertIsNone(self.char_panel.selected_grimoire_skill)

    def test_character_panel_right_click_unbind(self):
        """User Workflow C: Right-click hotkey slot [V] to unbind it."""
        self.char_panel.is_open = True
        self.player.skills.learned_skills = {"dash"}
        self.player.skills.hotkey_bindings = {"Q": None, "F": None, "V": "dash", "R": None}

        screen = pygame.display.get_surface()
        self.char_panel.render(screen, self.player, 0, 0)

        v_rect = self.char_panel.hotkey_rects["V"]
        handled = self.char_panel.handle_click(v_rect.centerx, v_rect.centery, self.player, self.inventory, is_right_click=True)
        self.assertTrue(handled)
        self.assertIsNone(self.player.skills.hotkey_bindings.get("V"), "Slot V should be unbound after right-click")

    def test_character_panel_keyboard_hotkey_assignment(self):
        """User Workflow D: Hover over skill and press key F."""
        self.char_panel.is_open = True
        self.player.skills.learned_skills = {"dash"}
        self.player.skills.hotkey_bindings = {"Q": None, "F": None, "V": None, "R": None}
        self.char_panel.hovered_skill_id = "dash"

        fake_event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_f)
        handled = self.char_panel.handle_key(fake_event, self.player)
        self.assertTrue(handled)
        self.assertEqual(self.player.skills.hotkey_bindings.get("F"), "dash", "Slot F should receive dash via key press")

    def test_character_panel_click_consumed_inside_panel(self):
        """Clicks anywhere inside panel boundary should be consumed so attacks don't fire."""
        self.char_panel.is_open = True
        pw, ph = 560, 520
        px = SCREEN_WIDTH // 2 - pw // 2
        py = SCREEN_HEIGHT // 2 - ph // 2

        # Click on empty background inside panel
        handled = self.char_panel.handle_click(px + 20, py + 20, self.player, self.inventory)
        self.assertTrue(handled, "Click inside panel frame must be consumed")

    def test_save_and_load_preserves_hotkeys(self):
        """Saving and loading world properly restores skill hotkeys."""
        class MockGame:
            pass

        game = MockGame()
        game.player = self.player
        game.inventory = self.inventory
        class MockCombat:
            def __init__(self):
                self.mini_bosses_slain = 0
                self.boss_defeated = False
                self.grand_boss_defeated = False
                self.dungeon_boss_slain = False
                self.boss = None
                self.mobs = []
                self.projectiles = []
                self.enemy_projectiles = []
                self.dropped_items = []
                self.damage_numbers = []

        game.combat = MockCombat()
        class MockCamera:
            def set_target(self, *args, **kwargs):
                pass

        game.camera = MockCamera()
        game.lighting = None
        game.world = self.world
        game.block_deltas = {}
        game.wall_deltas = {}
        game.game_mode = "adventure"
        game.world_type = "infinite"
        game.difficulty = "normal"
        game.active_world_name = "Test_Skill_World"
        game.asset_factory = self.factory

        self.player.skills.learned_skills = {"power_slash", "dash"}
        self.player.skills.hotkey_bindings = {"Q": "power_slash", "F": "dash", "V": None, "R": None}

        save_world("Test_Skill_World", game)

        # Clear and load
        game.player.skills.hotkey_bindings = {}
        success = load_world("Test_Skill_World", game)
        self.assertTrue(success)
        self.assertEqual(game.player.skills.hotkey_bindings.get("F"), "dash")
        self.assertEqual(game.player.skills.hotkey_bindings.get("Q"), "power_slash")
        self.assertIsNone(game.player.skills.hotkey_bindings.get("V"))
        self.assertIsNone(game.player.skills.hotkey_bindings.get("R"))

        delete_world("Test_Skill_World")


if __name__ == "__main__":
    unittest.main()
