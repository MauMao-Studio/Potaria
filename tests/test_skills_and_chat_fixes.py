"""
Unit tests for Chat Rendering Safety, Power Slash Directional Flipping, and Omnidirectional Swift Dash
Developer: Kurados | Pure Python 3.13 & pygame-ce
"""

import math
import unittest
import pygame

# Initialize pygame headless
pygame.init()
pygame.display.set_mode((1, 1), pygame.NOFRAME)

from src.constants import SCREEN_WIDTH, SCREEN_HEIGHT
from src.entities.player import Player
from src.entities.vfx import AnimatedVFX, VisualEffectManager
from src.assets.asset_factory import AssetFactory
from src.ui.hud import HUD


class DummySoundManager:
    def play(self, sound_name):
        pass

    def play_spatial(self, sound_name, x, y, px, py):
        pass


class DummyParticleSystem:
    def spawn_sparks(self, x, y, color, count=10):
        pass

    def spawn_debris(self, x, y, color, count=10):
        pass


class DummyCamera:
    def __init__(self):
        self.scroll_x = 0
        self.scroll_y = 0

    def add_shake(self, intensity, duration):
        pass

    def world_to_screen(self, wx, wy):
        return int(wx - self.scroll_x), int(wy - self.scroll_y)


class TestSkillsAndChatFixes(unittest.TestCase):
    def setUp(self):
        self.asset_factory = AssetFactory()
        self.sound_manager = DummySoundManager()
        self.particle_system = DummyParticleSystem()
        self.camera = DummyCamera()
        self.vfx_manager = VisualEffectManager(self.asset_factory)
        self.player = Player(100.0, 100.0, self.asset_factory, self.sound_manager)
        self.player.vfx_manager = self.vfx_manager

    def test_chat_render_handles_tuples_and_strings_without_crash(self):
        """Verifies _render_chat handles 2-tuples ('[SYSTEM]', msg) and raw strings safely."""
        hud = HUD(self.asset_factory)
        target_surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)

        # Populate local_chat_history with mixed types as used in main.py
        hud.local_chat_history = [
            ("[SYSTEM]", "God mode enabled."),
            ("Spud", "Hello from Potaria!"),
            ("[SYSTEM]", "Added item: ancient_god_blade x1"),
            "Just a raw string message",
            ("[SYSTEM]", "Time set to night.")
        ]

        # Should render cleanly without throwing TypeError: text must be a unicode or bytes
        try:
            hud._render_chat(target_surf, lan_client=None)
            success = True
        except TypeError as e:
            success = False
            self.fail(f"_render_chat crashed with TypeError: {e}")

        self.assertTrue(success, "HUD._render_chat must render tuple and string entries without error")

    def test_animated_vfx_flip_support(self):
        """Verifies AnimatedVFX supports flip_x and flip_y flags."""
        base_surf = pygame.Surface((32, 32))
        base_surf.fill((255, 0, 0))
        # Draw distinctive pixel at top-left
        base_surf.set_at((0, 0), (0, 255, 0))

        vfx = AnimatedVFX(50, 50, [base_surf], duration=0.5, flip_x=True)
        self.assertTrue(vfx.flip_x)
        self.assertFalse(vfx.flip_y)

        canvas = pygame.Surface((100, 100), pygame.SRCALPHA)
        vfx.render(canvas, self.camera)
        # Rendering succeeded without errors
        self.assertTrue(vfx.is_alive)

    def test_power_slash_cursor_direction_right(self):
        """Power slash with cursor aiming right faces right and spawns to the right without flip_x."""
        self.player.x = 200.0
        self.player.y = 200.0
        self.player.aim_angle = 0.0  # Directly right
        self.vfx_manager.clear()

        cast = self.player.cast_skill_hotkey("Q", self.particle_system, self.camera)
        self.assertTrue(cast, "Power slash should cast successfully")
        self.assertTrue(self.player.facing_right, "Player should face right when cursor is right")

        # Check spawned VFX
        self.assertGreater(len(self.vfx_manager.effects), 0, "VFX should be spawned for power slash")
        for effect in self.vfx_manager.effects:
            self.assertFalse(effect.flip_x, "VFX should NOT be flipped when slashing right")
            self.assertGreaterEqual(effect.x, self.player.center_x, "VFX should be positioned to the right of player")

    def test_power_slash_cursor_direction_left(self):
        """Power slash with cursor aiming left faces left and spawns flipped to the left."""
        self.player.x = 200.0
        self.player.y = 200.0
        self.player.aim_angle = math.pi  # Directly left
        self.vfx_manager.clear()

        # Reset cooldown & mana
        self.player.skills.cooldowns.clear()
        self.player.stats.current_mp = 100

        cast = self.player.cast_skill_hotkey("Q", self.particle_system, self.camera)
        self.assertTrue(cast, "Power slash should cast successfully")
        self.assertFalse(self.player.facing_right, "Player should face left when cursor is left")

        # Check spawned VFX
        self.assertGreater(len(self.vfx_manager.effects), 0, "VFX should be spawned for power slash")
        for effect in self.vfx_manager.effects:
            self.assertTrue(effect.flip_x, "VFX MUST be flipped horizontally when slashing left")
            self.assertLessEqual(effect.x, self.player.center_x, "VFX should be positioned to the left of player")

    def test_dash_omnidirectional_upward_jump(self):
        """Dash with cursor pointing straight up propels Spud upward (jump dash)."""
        self.player.x = 200.0
        self.player.y = 200.0
        self.player.aim_angle = -math.pi / 2  # Straight UP in screen coordinates
        self.player.on_ground = True
        self.vfx_manager.clear()

        # Reset cooldown & mana
        self.player.skills.cooldowns.clear()
        self.player.stats.current_mp = 100

        cast = self.player.cast_skill_hotkey("V", self.particle_system, self.camera)
        self.assertTrue(cast, "Dash should cast successfully")
        self.assertLess(self.player.vy, -10.0, "Player vy should be strongly negative (launching upward)")
        self.assertAlmostEqual(self.player.vx, 0.0, delta=0.5, msg="Horizontal velocity should be near zero for straight up dash")
        self.assertFalse(self.player.on_ground, "Player on_ground should become False during upward dash")

    def test_dash_omnidirectional_diagonal(self):
        """Dash with cursor pointing diagonally up-right propels both horizontally and vertically."""
        self.player.x = 200.0
        self.player.y = 200.0
        self.player.aim_angle = -math.pi / 4  # 45 degrees up-right
        self.player.on_ground = True
        self.vfx_manager.clear()

        self.player.skills.cooldowns.clear()
        self.player.stats.current_mp = 100

        cast = self.player.cast_skill_hotkey("V", self.particle_system, self.camera)
        self.assertTrue(cast, "Dash should cast successfully")
        self.assertGreater(self.player.vx, 7.0, "vx should be positive (moving right)")
        self.assertLess(self.player.vy, -7.0, "vy should be negative (moving up)")
        self.assertTrue(self.player.facing_right, "Player should face right when dashing right")

    def test_dash_omnidirectional_downward(self):
        """Dash with cursor pointing down propels player downwards (dive dash)."""
        self.player.x = 200.0
        self.player.y = 200.0
        self.player.aim_angle = math.pi / 2  # Straight DOWN
        self.vfx_manager.clear()

        self.player.skills.cooldowns.clear()
        self.player.stats.current_mp = 100

        cast = self.player.cast_skill_hotkey("V", self.particle_system, self.camera)
        self.assertTrue(cast, "Dash should cast successfully")
        self.assertGreater(self.player.vy, 10.0, "vy should be positive (moving down)")


if __name__ == "__main__":
    unittest.main()
