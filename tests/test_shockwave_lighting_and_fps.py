"""
Tests for SolarFlareShockwave, GravitationalPulseProjectile pos/frect attributes,
Dynamic Lighting crash prevention, and Persistent Small FPS Counter.
Developer: Kurados
"""

import os
import unittest
import pygame

# Set dummy video driver for headless test execution
os.environ["SDL_VIDEODRIVER"] = "dummy"

from src.constants import SCALED_TILE, SCREEN_WIDTH, SCREEN_HEIGHT
from src.entities.projectile import SolarFlareShockwave, GravitationalPulseProjectile, CelestialStarProjectile, ArrowProjectile
from main import PotariaGame

class TestShockwaveLightingAndFPS(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pygame.init()
        if not pygame.display.get_surface():
            pygame.display.set_mode((1280, 720))

    def test_solar_flare_shockwave_pos_and_frect(self):
        """Verify SolarFlareShockwave has .pos (Vector2) and .frect properties."""
        shock = SolarFlareShockwave(150.0, 250.0, damage=35, max_radius=90.0)
        self.assertTrue(hasattr(shock, "pos"), "SolarFlareShockwave must have 'pos' attribute")
        self.assertEqual(shock.pos.x, 150.0)
        self.assertEqual(shock.pos.y, 250.0)
        self.assertIsInstance(shock.pos, pygame.math.Vector2)

        # Test setter
        shock.pos = pygame.math.Vector2(200.0, 300.0)
        self.assertEqual(shock.x, 200.0)
        self.assertEqual(shock.y, 300.0)

        # Test rect and frect
        self.assertTrue(hasattr(shock, "frect"), "SolarFlareShockwave must have 'frect' attribute")
        self.assertTrue(hasattr(shock, "rect"), "SolarFlareShockwave must have 'rect' attribute")
        self.assertIsInstance(shock.frect, pygame.FRect)
        self.assertIsInstance(shock.rect, pygame.FRect)

    def test_gravitational_pulse_pos_and_frect(self):
        """Verify GravitationalPulseProjectile has .pos (Vector2) and .frect properties."""
        pulse = GravitationalPulseProjectile(320.0, 480.0, damage=40, pull_radius=120.0)
        self.assertTrue(hasattr(pulse, "pos"), "GravitationalPulseProjectile must have 'pos' attribute")
        self.assertEqual(pulse.pos.x, 320.0)
        self.assertEqual(pulse.pos.y, 480.0)
        self.assertIsInstance(pulse.pos, pygame.math.Vector2)

        # Test setter
        pulse.pos = (350.0, 500.0)
        self.assertEqual(pulse.x, 350.0)
        self.assertEqual(pulse.y, 500.0)

        # Test rect and frect
        self.assertTrue(hasattr(pulse, "frect"), "GravitationalPulseProjectile must have 'frect' attribute")
        self.assertTrue(hasattr(pulse, "rect"), "GravitationalPulseProjectile must have 'rect' attribute")
        self.assertIsInstance(pulse.frect, pygame.FRect)
        self.assertIsInstance(pulse.rect, pygame.FRect)

    def test_lighting_with_active_shockwave_and_pulse(self):
        """Verify dynamic lighting calculation executes without error when shockwave & pulse are active."""
        game = PotariaGame()
        # Add diverse projectiles to combat system
        shock = SolarFlareShockwave(game.player.center_x, game.player.center_y, damage=30)
        pulse = GravitationalPulseProjectile(game.player.center_x + 50, game.player.center_y, damage=35)
        star = CelestialStarProjectile(game.player.center_x, game.player.center_y, 0)
        arrow = ArrowProjectile(game.player.center_x, game.player.center_y, 0.0)

        game.combat.projectiles.extend([shock, pulse, star, arrow])

        # Execute lighting update lines from update_gameplay
        extra_lights = []
        for p in game.combat.projectiles:
            if getattr(p, "life", 0) > 0:
                pos = getattr(p, "pos", None)
                if pos is not None:
                    px = getattr(pos, "x", None)
                    py = getattr(pos, "y", None)
                else:
                    px = getattr(p, "x", None)
                    py = getattr(p, "y", None)
                if px is not None and py is not None:
                    intensity = 15 if isinstance(p, CelestialStarProjectile) else 8
                    extra_lights.append((int(px // SCALED_TILE), int(py // SCALED_TILE), intensity))

        self.assertGreaterEqual(len(extra_lights), 4)

        # Run update_gameplay directly
        game.update_gameplay(0.016)
        self.assertTrue(True, "update_gameplay completed with active shockwaves without crash")

    def test_fps_counter_rendering(self):
        """Verify persistent FPS counter renders properly with color grading."""
        game = PotariaGame()
        self.assertTrue(hasattr(game, "font_fps"), "PotariaGame must have 'font_fps'")
        self.assertTrue(hasattr(game, "_render_fps_counter"), "PotariaGame must have '_render_fps_counter'")

        # Test rendering without crash
        game._render_fps_counter()

        # Check font rendering
        txt_high = game.font_fps.render("FPS: 60", True, (80, 240, 100))
        self.assertGreater(txt_high.get_width(), 0)
        self.assertGreater(txt_high.get_height(), 0)

    def test_pvp_friendly_fire_projectile_defensive_rect(self):
        """Verify PvP friendly fire handles projectiles with both rect and frect."""
        game = PotariaGame()
        shock = SolarFlareShockwave(100, 100)
        p_rect = getattr(shock, "frect", getattr(shock, "rect", None))
        self.assertIsNotNone(p_rect)
        target_rect = pygame.Rect(95, 95, 20, 20)
        self.assertTrue(p_rect.colliderect(target_rect))

if __name__ == "__main__":
    unittest.main()
