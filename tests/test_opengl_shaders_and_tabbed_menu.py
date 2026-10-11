"""
Potaria - OpenGL ModernGL Shader Pipeline and Tabbed Settings Menu Tests
Tests:
1. GLSL multi-shader uniform pipeline: Bloom, Vignette, Water Waves, Color Grading
2. HAL RendererManager graphics parameter delegation and state preservation across renderer switch
3. Categorized Tabbed Settings Menu (Graphics, Audio, Gameplay, Controls)
4. Integration with PotariaGame action dispatch and settings persistence

Developer: Kurados
"""

import os
import sys
import unittest
import json
import pygame

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"

from src.constants import (
    SCREEN_WIDTH, SCREEN_HEIGHT,
    STATE_MENU, STATE_SETTINGS, STATE_PLAYING
)
from src.rendering import (
    BaseRenderer,
    SurfaceRenderer,
    GLRenderer,
    RendererManager,
    RENDERER_HARDWARE,
    RENDERER_SOFTWARE,
    get_renderer_manager,
)
from src.ui.menu import MenuManager


class TestOpenGLShaderPipeline(unittest.TestCase):
    def setUp(self):
        pygame.init()

    def test_gl_renderer_graphics_parameters_interface(self):
        renderer = GLRenderer(800, 600, "Test GL")
        params = renderer.get_graphics_params()
        self.assertIn("shaders_enabled", params)
        self.assertIn("bloom_enabled", params)
        self.assertIn("vignette_enabled", params)
        self.assertIn("vignette_intensity", params)
        self.assertIn("water_distortion_enabled", params)
        self.assertIn("water_distortion_intensity", params)
        self.assertIn("color_grading_mode", params)
        self.assertIn("saturation", params)
        self.assertIn("contrast", params)
        self.assertIn("lighting_quality", params)
        self.assertIn("particle_density", params)

        renderer.set_shaders_enabled(False)
        self.assertFalse(renderer.is_shaders_enabled())
        renderer.set_shaders_enabled(True)
        self.assertTrue(renderer.is_shaders_enabled())

        renderer.set_vignette_enabled(True)
        renderer.set_vignette_intensity(0.65)
        self.assertTrue(renderer.vignette_enabled)
        self.assertAlmostEqual(renderer.vignette_intensity, 0.65)

        renderer.set_water_distortion_enabled(True)
        renderer.set_water_distortion_intensity(1.75)
        self.assertTrue(renderer.water_distortion_enabled)
        self.assertAlmostEqual(renderer.water_distortion_intensity, 1.75)

        renderer.set_color_grading_mode("cinematic")
        self.assertEqual(renderer.color_grading_mode, 2)
        renderer.set_color_grading_mode("cool")
        self.assertEqual(renderer.color_grading_mode, 3)
        renderer.set_color_grading_mode("vibrant")
        self.assertEqual(renderer.color_grading_mode, 1)
        renderer.set_color_grading_mode("standard")
        self.assertEqual(renderer.color_grading_mode, 0)

        renderer.set_lighting_quality("ultra")
        self.assertEqual(renderer.lighting_quality, "ultra")
        renderer.set_particle_density("low")
        self.assertEqual(renderer.particle_density, "low")

    def test_surface_renderer_fallback_graphics_parameters(self):
        renderer = SurfaceRenderer(800, 600, "Test Surface")
        renderer.initialize()
        params = renderer.get_graphics_params()
        self.assertIsInstance(params, dict)
        self.assertIn("shaders_enabled", params)
        self.assertIn("bloom_enabled", params)

        renderer.set_vignette_enabled(True)
        renderer.set_water_distortion_enabled(True)
        renderer.set_color_grading_mode("cinematic")
        self.assertTrue(renderer.vignette_enabled)
        self.assertTrue(renderer.water_distortion_enabled)
        self.assertEqual(renderer.color_grading_mode, 2)
        renderer.cleanup()

    def test_renderer_manager_state_synchronization(self):
        manager = RendererManager()
        manager.initialize(width=800, height=600, requested_type=RENDERER_SOFTWARE)
        self.assertEqual(manager.renderer.get_renderer_type(), RENDERER_SOFTWARE)

        manager.set_shaders_enabled(True)
        manager.set_bloom_enabled(True)
        manager.set_vignette_enabled(True)
        manager.set_vignette_intensity(0.55)
        manager.set_water_distortion_enabled(True)
        manager.set_water_distortion_intensity(1.20)
        manager.set_color_grading_mode("vibrant")
        manager.set_lighting_quality("ultra")
        manager.set_particle_density("ultra")

        # Verify manager params
        params = manager.get_graphics_params()
        self.assertTrue(params["shaders_enabled"])
        self.assertTrue(params["bloom_enabled"])
        self.assertTrue(params["vignette_enabled"])
        self.assertAlmostEqual(params["vignette_intensity"], 0.55)
        self.assertTrue(params["water_distortion_enabled"])
        self.assertAlmostEqual(params["water_distortion_intensity"], 1.20)
        self.assertEqual(params["color_grading_mode"], 1)
        self.assertEqual(params["lighting_quality"], "ultra")
        self.assertEqual(params["particle_density"], "ultra")

        # Switch renderer to hardware and verify preserved state
        manager.switch_renderer(RENDERER_HARDWARE)
        params2 = manager.get_graphics_params()
        self.assertTrue(params2["shaders_enabled"])
        self.assertTrue(params2["bloom_enabled"])
        self.assertTrue(params2["vignette_enabled"])
        self.assertAlmostEqual(params2["vignette_intensity"], 0.55)
        self.assertTrue(params2["water_distortion_enabled"])
        self.assertAlmostEqual(params2["water_distortion_intensity"], 1.20)
        self.assertEqual(params2["color_grading_mode"], 1)
        self.assertEqual(params2["lighting_quality"], "ultra")
        self.assertEqual(params2["particle_density"], "ultra")
        manager.cleanup()


class TestTabbedSettingsMenu(unittest.TestCase):
    def setUp(self):
        pygame.init()
        self.menu = MenuManager(None, None)
        self.menu.state = STATE_SETTINGS

    def test_tab_buttons_exist_and_switch_categories(self):
        tabs = [b.action for b in self.menu.tab_buttons]
        self.assertIn("tab_graphics", tabs)
        self.assertIn("tab_audio", tabs)
        self.assertIn("tab_gameplay", tabs)
        self.assertIn("tab_controls", tabs)

        # Click audio tab
        tab_audio = next(b for b in self.menu.tab_buttons if b.action == "tab_audio")
        self.menu.handle_click((tab_audio.rect.centerx, tab_audio.rect.centery))
        self.assertEqual(self.menu.settings_tab, "audio")

        # Click gameplay tab
        tab_gameplay = next(b for b in self.menu.tab_buttons if b.action == "tab_gameplay")
        self.menu.handle_click((tab_gameplay.rect.centerx, tab_gameplay.rect.centery))
        self.assertEqual(self.menu.settings_tab, "gameplay")

        # Click controls tab
        tab_controls = next(b for b in self.menu.tab_buttons if b.action == "tab_controls")
        self.menu.handle_click((tab_controls.rect.centerx, tab_controls.rect.centery))
        self.assertEqual(self.menu.settings_tab, "controls")

        # Click graphics tab
        tab_graphics = next(b for b in self.menu.tab_buttons if b.action == "tab_graphics")
        self.menu.handle_click((tab_graphics.rect.centerx, tab_graphics.rect.centery))
        self.assertEqual(self.menu.settings_tab, "graphics")

    def test_all_settings_keys_present_in_menu(self):
        keys = [
            "master_volume", "bgm_volume", "sfx_volume", "fullscreen",
            "screen_shake", "renderer", "bloom", "shaders", "vignette",
            "water_effects", "resolution", "color_grade", "lighting_quality",
            "particle_density", "boost_mode", "damage_numbers", "tooltips"
        ]
        for k in keys:
            self.assertIn(k, self.menu.settings, f"Settings must contain key '{k}'")

    def test_graphics_tab_button_actions(self):
        self.menu.settings_tab = "graphics"
        btn_shaders = next(b for b in self.menu.settings_buttons if b.action == "toggle_shaders")
        btn_bloom = next(b for b in self.menu.settings_buttons if b.action == "toggle_bloom")
        btn_vignette = next(b for b in self.menu.settings_buttons if b.action == "toggle_vignette")
        btn_res = next(b for b in self.menu.settings_buttons if b.action == "cycle_resolution")
        btn_cg = next(b for b in self.menu.settings_buttons if b.action == "cycle_color_grade")
        btn_lq = next(b for b in self.menu.settings_buttons if b.action == "cycle_lighting_quality")
        btn_pd = next(b for b in self.menu.settings_buttons if b.action == "cycle_particle_density")

        # Verify toggle_water_effects is removed from UI buttons
        self.assertFalse(any(b.action == "toggle_water_effects" for b in self.menu.settings_buttons))

        # Shaders toggle
        cur_s = self.menu.settings.get("shaders", True)
        act = self.menu.handle_click((btn_shaders.rect.centerx, btn_shaders.rect.centery))
        self.assertEqual(act, ("set_shaders", not cur_s))
        self.assertEqual(self.menu.settings["shaders"], not cur_s)

        # Vignette toggle
        cur_v = self.menu.settings.get("vignette", True)
        act = self.menu.handle_click((btn_vignette.rect.centerx, btn_vignette.rect.centery))
        self.assertEqual(act, ("set_vignette", not cur_v))
        self.assertEqual(self.menu.settings["vignette"], not cur_v)

        # Resolution cycle
        self.menu.settings["resolution"] = "1920x1080"
        act = self.menu.handle_click((btn_res.rect.centerx, btn_res.rect.centery))
        self.assertEqual(act, ("set_resolution", "1600x900"))
        self.assertEqual(self.menu.settings["resolution"], "1600x900")

        # Color grade cycle
        self.menu.settings["color_grade"] = "vibrant"
        act = self.menu.handle_click((btn_cg.rect.centerx, btn_cg.rect.centery))
        self.assertEqual(act, ("set_color_grade", "cinematic"))
        self.assertEqual(self.menu.settings["color_grade"], "cinematic")

    def test_gameplay_tab_button_actions(self):
        self.menu.settings_tab = "gameplay"
        btn_boost = next(b for b in self.menu.settings_buttons if b.action == "toggle_boost_mode")
        btn_damage = next(b for b in self.menu.settings_buttons if b.action == "toggle_damage_numbers")
        btn_tt = next(b for b in self.menu.settings_buttons if b.action == "toggle_tooltips")

        # Boost mode toggle
        cur_b = self.menu.settings.get("boost_mode", True)
        act = self.menu.handle_click((btn_boost.rect.centerx, btn_boost.rect.centery))
        self.assertEqual(act, ("set_boost_mode", not cur_b))

        # Damage numbers toggle
        cur_d = self.menu.settings.get("damage_numbers", True)
        act = self.menu.handle_click((btn_damage.rect.centerx, btn_damage.rect.centery))
        self.assertEqual(act, ("set_damage_numbers", not cur_d))

        # Tooltips toggle
        self.menu.settings["tooltips"] = "detailed"
        act = self.menu.handle_click((btn_tt.rect.centerx, btn_tt.rect.centery))
        self.assertEqual(act, ("set_tooltips", "compact"))

    def test_render_settings_screen_all_tabs(self):
        surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        for tab in ["graphics", "audio", "gameplay", "controls"]:
            self.menu.settings_tab = tab
            self.menu._render_settings_screen(surf)
            self.assertGreater(surf.get_width(), 0)


class TestPotariaGameSettingsWiring(unittest.TestCase):
    def test_game_executes_graphics_actions(self):
        from main import PotariaGame
        game = PotariaGame()
        game._execute_menu_action(("set_shaders", False))
        self.assertFalse(game.renderer_manager.is_shaders_enabled())
        game._execute_menu_action(("set_shaders", True))
        self.assertTrue(game.renderer_manager.is_shaders_enabled())

        game._execute_menu_action(("set_vignette", False))
        self.assertFalse(game.renderer_manager.get_graphics_params()["vignette_enabled"])

        game._execute_menu_action(("set_water_effects", False))
        self.assertFalse(game.renderer_manager.get_graphics_params()["water_distortion_enabled"])

        game._execute_menu_action(("set_color_grade", "cool"))
        self.assertEqual(game.renderer_manager.get_graphics_params()["color_grading_mode"], 3)

        game._execute_menu_action(("set_boost_mode", False))
        self.assertFalse(game.boost_mode)

        game._execute_menu_action(("set_damage_numbers", False))
        self.assertFalse(game.combat.show_damage_numbers)

        game._execute_menu_action(("set_tooltips", "compact"))
        self.assertEqual(game.inventory.tooltip_mode, "compact")

        game._execute_menu_action(("set_resolution", "1600x900"))
        self.assertEqual(game.renderer_manager.display_width, 1600)
        self.assertEqual(game.renderer_manager.display_height, 900)

        game._execute_menu_action("cycle_resolution")
        self.assertEqual(game.menu.settings["resolution"], "1366x768")


if __name__ == "__main__":
    unittest.main()
