"""
Potaria - Unit Tests for Renderer Hardware Abstraction Layer (HAL)
Test Suite 26: test_renderer_hal.py
Developer: Kurados
Engine: Pure Python 3.13 + Pygame-ce 2.5.8 (100% Offline Standalone)
"""

import os
import unittest
from unittest.mock import MagicMock, patch
import pygame

# Set dummy audio/video drivers for headless automated testing
os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"

pygame.init()

from src.constants import SCREEN_WIDTH, SCREEN_HEIGHT
from src.rendering.base_renderer import (
    BaseRenderer,
    RENDERER_HARDWARE,
    RENDERER_SOFTWARE,
)
from src.rendering.surface_renderer import SurfaceRenderer
from src.rendering.gl_renderer import GLRenderer
from src.rendering.renderer_manager import RendererManager
from src.rendering import get_renderer_manager, create_renderer
from src.ui.menu import MenuManager


class TestBaseRendererInterface(unittest.TestCase):
    """Verifies that BaseRenderer enforces the abstract interface contract."""

    def test_cannot_instantiate_abstract_base_renderer(self):
        with self.assertRaises(TypeError):
            BaseRenderer(1280, 720)

    def test_interface_method_declarations(self):
        abstract_methods = BaseRenderer.__abstractmethods__
        required_methods = {
            "initialize",
            "clear",
            "draw_sprite",
            "draw_surface",
            "draw_rect",
            "draw_text",
            "draw_line",
            "draw_circle",
            "present",
            "get_surface",
            "set_mode",
            "is_hardware_accelerated",
            "get_renderer_type",
            "cleanup",
        }
        self.assertTrue(required_methods.issubset(abstract_methods), f"Missing methods: {required_methods - abstract_methods}")


class TestSurfaceRenderer(unittest.TestCase):
    """Tests the native Pygame-ce software blitting renderer."""

    def setUp(self):
        self.renderer = SurfaceRenderer(width=800, height=600, title="Test Surface", fullscreen=False)

    def tearDown(self):
        self.renderer.cleanup()

    def test_initialization_and_surface(self):
        success = self.renderer.initialize()
        self.assertTrue(success)
        self.assertTrue(self.renderer.initialized)
        surf = self.renderer.get_surface()
        self.assertIsInstance(surf, pygame.Surface)
        self.assertEqual(surf.get_size(), (800, 600))
        self.assertFalse(self.renderer.is_hardware_accelerated())
        self.assertEqual(self.renderer.get_renderer_type(), RENDERER_SOFTWARE)

    def test_drawing_operations(self):
        self.renderer.initialize()
        surf = self.renderer.get_surface()

        # Clear
        self.renderer.clear((20, 30, 40))
        self.assertEqual(surf.get_at((10, 10))[:3], (20, 30, 40))

        # Draw rect
        self.renderer.draw_rect((255, 0, 0), (50, 50, 40, 40))
        self.assertEqual(surf.get_at((60, 60))[:3], (255, 0, 0))

        # Draw line
        self.renderer.draw_line((0, 255, 0), (100, 100), (150, 100), width=2)
        self.assertEqual(surf.get_at((120, 100))[:3], (0, 255, 0))

        # Draw circle
        self.renderer.draw_circle((0, 0, 255), (200, 200), radius=10)
        self.assertEqual(surf.get_at((200, 200))[:3], (0, 0, 255))

        # Draw sprite / surface
        sprite = pygame.Surface((32, 32))
        sprite.fill((255, 255, 0))
        self.renderer.draw_sprite(sprite, (300, 300))
        self.assertEqual(surf.get_at((310, 310))[:3], (255, 255, 0))

        # Draw text
        font = pygame.font.SysFont("Arial", 16)
        text_rect = self.renderer.draw_text(font, "Hello Potaria", (400, 400), color=(255, 255, 255))
        self.assertIsInstance(text_rect, pygame.Rect)
        self.assertEqual(text_rect.topleft, (400, 400))

        # Present
        self.renderer.present()

    def test_set_mode(self):
        self.renderer.initialize()
        success = self.renderer.set_mode(640, 480, fullscreen=False)
        self.assertTrue(success)
        self.assertEqual(self.renderer.width, 640)
        self.assertEqual(self.renderer.height, 480)
        self.assertEqual(self.renderer.get_surface().get_size(), (640, 480))


class TestGLRenderer(unittest.TestCase):
    """Tests GLRenderer initialization, fallback behavior, and hardware abstraction."""

    def test_automatic_fallback_when_moderngl_unavailable(self):
        renderer = GLRenderer(width=800, height=600, title="Test GL")
        success = renderer.initialize()
        self.assertTrue(success)
        self.assertTrue(renderer.initialized)
        # In dummy/headless environment where ModernGL or OpenGL context is not available
        self.assertTrue(renderer.using_fallback)
        self.assertFalse(renderer.is_hardware_accelerated())
        self.assertEqual(renderer.get_renderer_type(), RENDERER_SOFTWARE)
        self.assertIn("Fallback", renderer.get_status_description())

        # Operations through fallback work seamlessly
        surf = renderer.get_surface()
        self.assertIsInstance(surf, pygame.Surface)
        renderer.clear((10, 20, 30))
        renderer.draw_rect((255, 128, 0), (10, 10, 50, 50))
        self.assertEqual(surf.get_at((25, 25))[:3], (255, 128, 0))

        font = pygame.font.SysFont("Arial", 14)
        t_rect = renderer.draw_text(font, "GL Fallback Test", (100, 100))
        self.assertIsInstance(t_rect, pygame.Rect)

        renderer.present()
        renderer.cleanup()

    def test_mocked_moderngl_hardware_pipeline(self):
        """Tests GLRenderer behavior when ModernGL context initializes successfully."""
        mock_ctx = MagicMock()
        mock_ctx.info = {"GL_RENDERER": "Mock GPU Accelerated Engine"}
        mock_prog = MagicMock()
        mock_vbo = MagicMock()
        mock_vao = MagicMock()
        mock_tex = MagicMock()

        mock_ctx.program.return_value = mock_prog
        mock_ctx.buffer.return_value = mock_vbo
        mock_ctx.simple_vertex_array.return_value = mock_vao
        mock_ctx.texture.return_value = mock_tex

        with patch("src.rendering.gl_renderer.MODERNGL_AVAILABLE", True), \
             patch("src.rendering.gl_renderer.moderngl") as mock_mgl, \
             patch("pygame.display.set_mode") as mock_set_mode:

            mock_mgl.create_context.return_value = mock_ctx
            mock_mgl.NEAREST = 0x2600
            mock_mgl.TRIANGLE_STRIP = 5

            renderer = GLRenderer(width=800, height=600, title="Mock GL")
            success = renderer.initialize()

            self.assertTrue(success)
            self.assertFalse(renderer.using_fallback)
            self.assertTrue(renderer.is_hardware_accelerated())
            self.assertEqual(renderer.get_renderer_type(), RENDERER_HARDWARE)
            self.assertEqual(renderer.get_status_description(), "Hardware (ModernGL)")

            # Drawing onto virtual surface
            surf = renderer.get_surface()
            self.assertIsInstance(surf, pygame.Surface)
            renderer.clear((50, 60, 70))
            renderer.draw_rect((255, 255, 255), (0, 0, 10, 10))
            self.assertEqual(surf.get_at((5, 5))[:3], (255, 255, 255))

            # Present writes texture and renders VAO
            renderer.present()
            mock_tex.write.assert_called()
            mock_vao.render.assert_called_with(mock_mgl.TRIANGLE_STRIP)

            # Cleanup
            renderer.cleanup()
            mock_tex.release.assert_called()
            mock_vbo.release.assert_called()
            mock_vao.release.assert_called()
            mock_ctx.release.assert_called()

    def test_repeated_initialization_and_cleanup_safety(self):
        """Verifies that calling initialize and cleanup repeatedly does not crash or leak."""
        renderer = GLRenderer(width=640, height=480)
        renderer.initialize()
        renderer.initialize()  # repeat initialize
        self.assertTrue(renderer.initialized)

        # Repeated cleanup
        renderer.cleanup()
        renderer.cleanup()
        self.assertFalse(renderer.initialized)

    def test_mocked_set_mode_and_viewport(self):
        """Verifies set_mode updates dimensions and configures viewport."""
        mock_ctx = MagicMock()
        mock_ctx.info = {"GL_RENDERER": "Mock GPU"}
        mock_ctx.program.return_value = MagicMock()
        mock_ctx.buffer.return_value = MagicMock()
        mock_ctx.simple_vertex_array.return_value = MagicMock()
        mock_ctx.texture.return_value = MagicMock()

        with patch("src.rendering.gl_renderer.MODERNGL_AVAILABLE", True), \
             patch("src.rendering.gl_renderer.moderngl") as mock_mgl, \
             patch("pygame.display.set_mode"):

            mock_mgl.create_context.return_value = mock_ctx
            mock_mgl.NEAREST = 0x2600
            mock_mgl.TRIANGLE_STRIP = 5

            renderer = GLRenderer(width=800, height=600)
            renderer.initialize()
            self.assertEqual(mock_ctx.viewport, (0, 0, 800, 600))

            renderer.set_mode(1024, 768)
            self.assertEqual(renderer.width, 1024)
            self.assertEqual(renderer.height, 768)
            self.assertEqual(mock_ctx.viewport, (0, 0, 1024, 768))
            renderer.cleanup()


class TestRendererManager(unittest.TestCase):
    """Tests the RendererManager central factory and runtime switcher."""

    def setUp(self):
        self.manager = RendererManager()

    def tearDown(self):
        self.manager.cleanup()

    def test_singleton_accessor(self):
        m1 = get_renderer_manager()
        m2 = RendererManager.get_instance()
        self.assertIs(m1, m2)

    def test_factory_creation(self):
        r_soft = create_renderer(RENDERER_SOFTWARE, width=640, height=480)
        self.assertEqual(r_soft.get_renderer_type(), RENDERER_SOFTWARE)
        r_soft.cleanup()

        r_hard = create_renderer(RENDERER_HARDWARE, width=640, height=480)
        # Without ModernGL, hardware requested gracefully falls back
        self.assertIn(r_hard.get_renderer_type(), (RENDERER_HARDWARE, RENDERER_SOFTWARE))
        r_hard.cleanup()

    def test_initialize_software(self):
        rend = self.manager.initialize(width=800, height=600, requested_type=RENDERER_SOFTWARE)
        self.assertEqual(self.manager.requested_type, RENDERER_SOFTWARE)
        self.assertEqual(rend.get_renderer_type(), RENDERER_SOFTWARE)
        self.assertEqual(self.manager.get_status_label(), "RENDERER: COMPATIBILITY (SOFTWARE)")
        self.assertIsInstance(self.manager.surface, pygame.Surface)

    def test_runtime_renderer_switching_and_toggling(self):
        # Start in software
        self.manager.initialize(width=800, height=600, requested_type=RENDERER_SOFTWARE)
        self.assertEqual(self.manager.requested_type, RENDERER_SOFTWARE)

        # Toggle to hardware
        self.manager.toggle_renderer()
        self.assertEqual(self.manager.requested_type, RENDERER_HARDWARE)
        self.assertEqual(self.manager.get_status_label(), "RENDERER: HARDWARE (MODERNGL)")

        # Toggle back to software
        self.manager.toggle_renderer()
        self.assertEqual(self.manager.requested_type, RENDERER_SOFTWARE)
        self.assertEqual(self.manager.get_status_label(), "RENDERER: COMPATIBILITY (SOFTWARE)")

        # Explicit switch
        self.manager.switch_renderer(RENDERER_HARDWARE)
        self.assertEqual(self.manager.requested_type, RENDERER_HARDWARE)

    def test_manager_drawing_delegation(self):
        self.manager.initialize(width=800, height=600, requested_type=RENDERER_SOFTWARE)
        self.manager.clear((15, 25, 35))
        self.manager.draw_rect((100, 200, 50), (20, 20, 30, 30))
        surf = self.manager.surface
        self.assertEqual(surf.get_at((25, 25))[:3], (100, 200, 50))

        font = pygame.font.SysFont("Arial", 12)
        txt_rect = self.manager.draw_text(font, "Delegation Test", (50, 50))
        self.assertIsInstance(txt_rect, pygame.Rect)
        self.manager.present()

    def test_input_sanitization_and_fallbacks(self):
        """Verifies that untrusted or messy input strings are cleanly normalized."""
        self.manager.initialize(width=640, height=480, requested_type="  SoFtWaRe  ")
        self.assertEqual(self.manager.requested_type, RENDERER_SOFTWARE)

        self.manager.switch_renderer("  HaRdWaRe  ")
        self.assertEqual(self.manager.requested_type, RENDERER_HARDWARE)

        # Fallback for unrecognized backend type defaults safely to hardware
        self.manager.switch_renderer("unknown_vulkan_backend")
        self.assertEqual(self.manager.requested_type, RENDERER_HARDWARE)


class TestSettingsIntegration(unittest.TestCase):
    """Tests the in-game Settings menu toggle and disk persistence."""

    def test_menu_settings_defaults_and_toggle(self):
        menu = MenuManager(None, None)
        self.assertIn("renderer", menu.settings)

        # Check that toggle_renderer button exists
        btn = next((b for b in menu.settings_buttons if b.action == "toggle_renderer"), None)
        self.assertIsNotNone(btn, "toggle_renderer button must be present in settings_buttons")

        # Initial state reflects current setting
        menu.open_settings()
        self.assertIn("RENDERER:", btn.text)

        # Click toggle button
        initial_val = menu.settings["renderer"]
        act = menu.handle_click((btn.rect.centerx, btn.rect.centery))
        self.assertEqual(act[0], "set_renderer")
        new_val = menu.settings["renderer"]
        self.assertNotEqual(initial_val, new_val)
        self.assertEqual(act[1], new_val)

        # Click toggle again
        act2 = menu.handle_click((btn.rect.centerx, btn.rect.centery))
        self.assertEqual(act2[1], initial_val)
        self.assertEqual(menu.settings["renderer"], initial_val)

    def test_settings_persistence_across_reloads(self):
        menu1 = MenuManager(None, None)
        menu1.settings["renderer"] = "software"
        menu1.save_settings()

        menu2 = MenuManager(None, None)
        self.assertEqual(menu2.settings.get("renderer"), "software")

        # Restore to hardware
        menu2.settings["renderer"] = "hardware"
        menu2.save_settings()

        menu3 = MenuManager(None, None)
        self.assertEqual(menu3.settings.get("renderer"), "hardware")


class TestPotariaGameRendererHAL(unittest.TestCase):
    """Tests PotariaGame integration with the Renderer HAL."""

    def test_potaria_game_hal_wiring(self):
        from main import PotariaGame
        game = PotariaGame()

        # HAL properties exist
        self.assertTrue(hasattr(game, "renderer_manager"))
        self.assertTrue(hasattr(game, "renderer"))
        self.assertIsInstance(game.screen, pygame.Surface)
        self.assertEqual(game.screen.get_size(), (SCREEN_WIDTH, SCREEN_HEIGHT))

        # Switch renderer mode via PotariaGame
        game.set_renderer_mode(RENDERER_SOFTWARE)
        self.assertEqual(game.renderer_manager.requested_type, RENDERER_SOFTWARE)
        self.assertEqual(game.menu.settings.get("renderer"), RENDERER_SOFTWARE)

        game.set_renderer_mode(RENDERER_HARDWARE)
        self.assertEqual(game.renderer_manager.requested_type, RENDERER_HARDWARE)
        self.assertEqual(game.menu.settings.get("renderer"), RENDERER_HARDWARE)

        # Toggle renderer mode
        game.toggle_renderer_mode()
        self.assertEqual(game.renderer_manager.requested_type, RENDERER_SOFTWARE)

        # Menu action dispatching
        game._execute_menu_action(("set_renderer", RENDERER_HARDWARE))
        self.assertEqual(game.renderer_manager.requested_type, RENDERER_HARDWARE)

        game._execute_menu_action("toggle_renderer")
        self.assertEqual(game.renderer_manager.requested_type, RENDERER_SOFTWARE)

        # Verify render execution
        game.render()

        # Clean shutdown cleanup
        game.renderer_manager.cleanup()

    def test_renderer_settings_persistence_on_mode_change(self):
        """Verifies that calling game.set_renderer_mode persists immediately to disk."""
        import json
        from main import PotariaGame
        game = PotariaGame()

        settings_path = os.path.join("saves", "settings.json")
        game.set_renderer_mode(RENDERER_SOFTWARE)

        with open(settings_path, "r", encoding="utf-8") as f:
            disk_data = json.load(f)
        self.assertEqual(disk_data["settings"].get("renderer"), RENDERER_SOFTWARE)

        # Restore to hardware and verify persistence
        game.set_renderer_mode(RENDERER_HARDWARE)
        with open(settings_path, "r", encoding="utf-8") as f:
            disk_data2 = json.load(f)
        self.assertEqual(disk_data2["settings"].get("renderer"), RENDERER_HARDWARE)

        game.renderer_manager.cleanup()


if __name__ == "__main__":
    unittest.main()
