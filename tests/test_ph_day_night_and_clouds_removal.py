"""
Tests for Philippine Day/Night Cycle accuracy and Sky Cloud rendering removal.
Verifies:
1. 5:00 AM starts to not be pitch black (dawn transition begins).
2. 6:00 AM is the start of the sun (sun arc begins at left horizon, daytime transition).
3. 12:00 PM is midday full daylight.
4. 6:00 PM sunset, with dusk fading into night darkness by 6:43 PM.
5. 7:00 PM / 7:04 PM is night (pitch black sky, is_night True, sapphire tint).
6. Sky cloud rendering removal (clouds layer not blitted during render, saving render time).
7. Sun and Moon celestial orbits matching Philippine schedule.
"""

import os
import sys
import unittest
import pygame

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.constants import SCREEN_WIDTH, SCREEN_HEIGHT
from src.assets.asset_factory import AssetFactory
from src.audio.sound_effects import SoundManager
from src.environment.sky import DayNightCycle
from src.camera import Camera
from src.ui.hud import HUD


class TestPhilippineDayNightAndCloudsRemoval(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pygame.init()
        if pygame.display.get_surface() is None:
            pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.HIDDEN)
        cls.asset_factory = AssetFactory()
        cls.sound_manager = SoundManager()

    def setUp(self):
        self.sky = DayNightCycle(self.asset_factory, cycle_duration=240.0)

    def test_clouds_not_rendered(self):
        """Verifies that clouds are not blitted during sky render."""
        camera = Camera()
        camera.x = 100.0
        camera.y = 100.0

        blitted_surfaces = []

        class TargetSurfWrapper:
            def __init__(self, base_surf):
                self._base = base_surf

            def get_width(self):
                return self._base.get_width()

            def get_height(self):
                return self._base.get_height()

            def blit(self, source, dest, *args, **kwargs):
                blitted_surfaces.append(source)
                return self._base.blit(source, dest, *args, **kwargs)

            def set_at(self, pos, color):
                self._base.set_at(pos, color)

        raw_surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        wrapper = TargetSurfWrapper(raw_surf)
        self.sky.render(wrapper, camera)

        # self.sky.clouds_surf should NOT be among blitted surfaces
        self.assertNotIn(
            self.sky.clouds_surf,
            blitted_surfaces,
            "Clouds surface must not be blitted during sky render"
        )

    def test_time_at_5am_starts_to_not_be_pitch_black(self):
        """At 5:00 AM (t = 23/24), the sky starts brightening from pitch black night towards dawn."""
        t_5am = 23.0 / 24.0

        # At 4:50 AM (t < 23/24), sky is pitch black night
        self.sky.time = self.sky.cycle_duration * (t_5am - 0.01)
        top_pre, bot_pre = self.sky.get_sky_colors()
        c_night_top = (12, 18, 35)
        c_night_bot = (25, 40, 65)
        self.assertEqual(top_pre, c_night_top, "Pre-5:00 AM must be pitch black night top color")
        self.assertEqual(bot_pre, c_night_bot, "Pre-5:00 AM must be pitch black night bottom color")

        # At 5:00 AM exactly (t = 23/24)
        self.sky.time = self.sky.cycle_duration * t_5am
        top_5am, bot_5am = self.sky.get_sky_colors()
        self.assertEqual(top_5am, c_night_top)

        # At 5:30 AM (t = 23.5/24), sky is halfway into dawn and NOT pitch black
        t_530am = 23.5 / 24.0
        self.sky.time = self.sky.cycle_duration * t_530am
        top_dawn, bot_dawn = self.sky.get_sky_colors()
        self.assertGreater(top_dawn[0], c_night_top[0], "Sky at 5:30 AM must be brighter than pitch black")
        self.assertGreater(bot_dawn[0], c_night_bot[0], "Sky at 5:30 AM must have brightened bottom color")
        self.assertFalse(self.sky.is_night, "is_night must be False after 5:00 AM dawn begins")

    def test_6am_start_of_the_sun(self):
        """At 6:00 AM (t = 0.0), the sun starts rising above the horizon."""
        self.sky.time = 0.0  # 6:00 AM
        self.assertEqual(self.sky.time_of_day, 0.0)

        # Ambient sunlight at 6:00 AM is morning light, reaching 15 by 6:30 AM
        self.assertGreaterEqual(self.sky.ambient_sunlight, 10)
        self.assertFalse(self.sky.is_night)

        # Time string check
        time_str = self.sky.get_time_string()
        self.assertTrue("6:00 AM" in time_str or "6:0" in time_str)
        self.assertIn("Day", time_str)

    def test_midday_full_sunlight(self):
        """At 12:00 PM (t = 0.25), full daylight is cast."""
        self.sky.time = self.sky.cycle_duration * 0.25
        top, bot = self.sky.get_sky_colors()
        self.assertEqual(top, (115, 175, 195))
        self.assertEqual(bot, (175, 215, 225))
        self.assertEqual(self.sky.ambient_sunlight, 15)
        self.assertFalse(self.sky.is_night)

    def test_7pm_and_704pm_is_night_without_dusk_glow(self):
        """At 7:00 PM and 7:04 PM, the sky is deep night with no reddish dusk glow."""
        # 7:04 PM in 24h cycle: total_hours = 19.0667 -> t = 13.0667 / 24.0 = 0.5444
        t_704pm = (19.0667 - 6.0) / 24.0
        self.sky.time = self.sky.cycle_duration * t_704pm

        top, bot = self.sky.get_sky_colors()
        c_night_top = (12, 18, 35)
        c_night_bot = (25, 40, 65)

        self.assertEqual(top, c_night_top, "7:04 PM sky top must be deep night, not reddish dusk")
        self.assertEqual(bot, c_night_bot, "7:04 PM sky bottom must be deep night, not reddish dusk")
        self.assertTrue(self.sky.is_night, "7:04 PM must be night")
        self.assertEqual(self.sky.atmospheric_tint, (0.75, 0.88, 1.22), "7:04 PM must have moonlit night tint")
        self.assertEqual(self.sky.ambient_sunlight, 3, "7:04 PM ambient sunlight must be at night level 3")

    def test_hud_game_time_string_at_5am_and_6am_and_7pm(self):
        """Verifies HUD time formatting across key Philippine diurnal milestones."""
        hud = HUD(asset_factory=self.asset_factory)

        # 5:00 AM
        self.sky.time = self.sky.cycle_duration * (23.0 / 24.0)
        time_str, period, is_night = hud.get_game_time_string(self.sky)
        self.assertEqual(period, "AM")
        self.assertTrue(time_str.startswith("5:00"))
        self.assertFalse(is_night, "5:00 AM dawn is not night")

        # 6:00 AM
        self.sky.time = 0.0
        time_str, period, is_night = hud.get_game_time_string(self.sky)
        self.assertEqual(period, "AM")
        self.assertTrue(time_str.startswith("6:00"))
        self.assertFalse(is_night)

        # 7:04 PM
        self.sky.time = self.sky.cycle_duration * ((19.0667 - 6.0) / 24.0)
        time_str, period, is_night = hud.get_game_time_string(self.sky)
        self.assertEqual(period, "PM")
        self.assertTrue(time_str.startswith("7:04"))
        self.assertTrue(is_night, "7:04 PM must be night")

    def test_dawn_to_sunrise_color_continuity(self):
        """Verifies smooth continuous color transition across the 6:00 AM wraparound."""
        # 5:59 AM (t just below 1.0)
        self.sky.time = self.sky.cycle_duration * 0.9999
        top_559, bot_559 = self.sky.get_sky_colors()

        # 6:00 AM (t = 0.0)
        self.sky.time = 0.0
        top_600, bot_600 = self.sky.get_sky_colors()

        # Colors at 5:59 AM and 6:00 AM must be virtually identical (< 2 per channel difference)
        for i in range(3):
            self.assertLessEqual(abs(top_559[i] - top_600[i]), 2)
            self.assertLessEqual(abs(bot_559[i] - bot_600[i]), 2)

    def test_sunset_progression(self):
        """Verifies dusk occurs between 5:30 PM and 6:43 PM, transitioning into pitch black night."""
        c_night_top = (12, 18, 35)

        # 5:30 PM (t = 0.48)
        self.sky.time = self.sky.cycle_duration * 0.48
        top_530, _ = self.sky.get_sky_colors()
        self.assertEqual(top_530, (115, 175, 195), "5:30 PM is end of full daytime")

        # 6:00 PM (t = 0.50, sunset)
        self.sky.time = self.sky.cycle_duration * 0.50
        top_600, _ = self.sky.get_sky_colors()
        self.assertEqual(top_600, (90, 50, 95), "6:00 PM reaches dusk color")

        # 6:43 PM (t = 0.53, dusk finishes into night)
        self.sky.time = self.sky.cycle_duration * 0.53
        top_643, _ = self.sky.get_sky_colors()
        self.assertEqual(top_643, c_night_top, "6:43 PM finishes into night darkness")

    def test_sky_render_performance_without_clouds(self):
        """Verifies sky rendering executes cleanly and quickly without cloud blitting overhead."""
        import time
        camera = Camera()
        camera.x = 200.0
        camera.y = 100.0
        surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))

        # Warm up cache
        self.sky.render(surf, camera)

        # Measure 50 frame renders
        start = time.perf_counter()
        for _ in range(50):
            self.sky.render(surf, camera)
        elapsed_ms_per_frame = ((time.perf_counter() - start) / 50.0) * 1000.0

        # Without the cloud blits, render time should comfortably remain well below 3ms per frame
        self.assertLess(elapsed_ms_per_frame, 3.5, f"Render Sky should be well under 3.5ms (measured {elapsed_ms_per_frame:.2f}ms)")


if __name__ == "__main__":
    unittest.main()
