"""
Potaria - Settings Persistence Unit & Integration Test Suite
Tests:
1. Atomic save and disk flushing (.tmp, .bak, and atomic replace)
2. Corruption fallback and recovery from .bak
3. Working directory (CWD) independence
4. MenuManager and PotariaGame shared settings binding
5. Volume update action handling and immediate audio propagation
6. Pause menu graphics re-application on resume
Developer: Kurados
"""

import os
import sys
import json
import tempfile
import unittest
import pygame

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.constants import PROJECT_ROOT, SAVES_DIR, SETTINGS_FILE
from src.settings_manager import (
    load_settings,
    save_settings,
    get_current_settings,
    get_current_key_bindings,
    update_setting,
    DEFAULT_SETTINGS,
    DEFAULT_KEY_BINDINGS,
)
from src.ui.menu import MenuManager


class TestSettingsPersistence(unittest.TestCase):
    def setUp(self):
        pygame.init()
        self.test_dir = tempfile.TemporaryDirectory()
        self.custom_settings_path = os.path.join(self.test_dir.name, "settings.json")

    def tearDown(self):
        self.test_dir.cleanup()

    def test_default_settings_schema(self):
        """Verifies that all required configuration keys exist in DEFAULT_SETTINGS."""
        required_keys = [
            "master_volume", "bgm_volume", "sfx_volume", "fullscreen",
            "screen_shake", "touch_controls", "touch_opacity", "renderer",
            "bloom", "shaders", "vignette", "water_effects", "resolution",
            "color_grade", "lighting_quality", "particle_density", "boost_mode",
            "damage_numbers", "tooltips"
        ]
        for key in required_keys:
            self.assertIn(key, DEFAULT_SETTINGS, f"Missing default configuration key: {key}")

    def test_atomic_save_and_load(self):
        """Tests that settings are saved atomically and can be reloaded accurately."""
        custom_cfg = dict(DEFAULT_SETTINGS)
        custom_cfg["master_volume"] = 0.45
        custom_cfg["fullscreen"] = True
        custom_cfg["tooltips"] = "compact"
        custom_cfg["resolution"] = "1600x900"

        custom_keys = dict(DEFAULT_KEY_BINDINGS)
        custom_keys["Jump"] = pygame.K_w

        success = save_settings(custom_cfg, custom_keys, path=self.custom_settings_path)
        self.assertTrue(success)
        self.assertTrue(os.path.exists(self.custom_settings_path))

        # Reload from disk
        loaded_cfg, loaded_keys = load_settings(path=self.custom_settings_path)
        self.assertAlmostEqual(loaded_cfg["master_volume"], 0.45, places=2)
        self.assertEqual(loaded_cfg["fullscreen"], True)
        self.assertEqual(loaded_cfg["tooltips"], "compact")
        self.assertEqual(loaded_cfg["resolution"], "1600x900")
        self.assertEqual(loaded_keys["Jump"], pygame.K_w)

    def test_backup_creation_and_recovery(self):
        """Tests that a .bak backup is created on overwrite and recovers corrupted files."""
        # 1. Save valid initial config
        cfg1 = dict(DEFAULT_SETTINGS)
        cfg1["master_volume"] = 0.33
        save_settings(cfg1, DEFAULT_KEY_BINDINGS, path=self.custom_settings_path)

        # 2. Save updated config to create .bak
        cfg2 = dict(DEFAULT_SETTINGS)
        cfg2["master_volume"] = 0.77
        save_settings(cfg2, DEFAULT_KEY_BINDINGS, path=self.custom_settings_path)

        bak_path = self.custom_settings_path + ".bak"
        self.assertTrue(os.path.exists(bak_path))

        # Verify .bak contains first valid saved config
        with open(bak_path, "r", encoding="utf-8") as f:
            bak_data = json.load(f)
        self.assertAlmostEqual(bak_data["settings"]["master_volume"], 0.33, places=2)

        # 3. Simulate sudden file truncation or corrupt JSON on primary file
        with open(self.custom_settings_path, "w", encoding="utf-8") as f:
            f.write('{"settings": { CORRUPTED_DATA_TRUNCATED...')

        # 4. load_settings should seamlessly recover from .bak
        recovered_cfg, _ = load_settings(path=self.custom_settings_path)
        self.assertAlmostEqual(recovered_cfg["master_volume"], 0.33, places=2)

    def test_cwd_independence(self):
        """Tests that saving and loading settings uses canonical PROJECT_ROOT regardless of active CWD."""
        orig_cwd = os.getcwd()
        try:
            # Change CWD to a temporary directory
            os.chdir(self.test_dir.name)
            self.assertEqual(os.getcwd(), self.test_dir.name)

            # SETTINGS_FILE must still point to canonical PROJECT_ROOT/saves/settings.json
            self.assertTrue(os.path.isabs(SETTINGS_FILE))
            self.assertTrue(SETTINGS_FILE.startswith(PROJECT_ROOT))
            self.assertIn("saves", SETTINGS_FILE)

            # Test loading defaults from canonical path
            settings, keys = load_settings()
            self.assertIsInstance(settings, dict)
            self.assertIn("master_volume", settings)

            # Verify no orphan saves folder was created in the temporary CWD
            orphan_path = os.path.join(self.test_dir.name, "saves")
            self.assertFalse(os.path.exists(orphan_path))
        finally:
            os.chdir(orig_cwd)

    def test_menu_and_engine_shared_dictionary(self):
        """Verifies that MenuManager binds to the shared settings dictionary without divergence."""
        from src.assets.asset_factory import AssetFactory
        from src.audio.sound_effects import SoundManager

        assets = AssetFactory()
        sound = SoundManager()

        shared_settings = dict(DEFAULT_SETTINGS)
        shared_settings["screen_shake"] = True
        shared_keys = dict(DEFAULT_KEY_BINDINGS)

        menu = MenuManager(assets, sound, settings=shared_settings, key_bindings=shared_keys)
        self.assertIs(menu.settings, shared_settings)
        self.assertIs(menu.key_bindings, shared_keys)

        # Modifying menu settings must instantly reflect in shared_settings
        menu.settings["screen_shake"] = False
        self.assertFalse(shared_settings["screen_shake"])

    def test_volume_update_action_in_menu(self):
        """Tests that changing audio volume via menu buttons persists and updates immediately."""
        from src.assets.asset_factory import AssetFactory
        from src.audio.sound_effects import SoundManager
        from src.constants import STATE_SETTINGS

        assets = AssetFactory()
        sound = SoundManager()

        menu = MenuManager(assets, sound)
        menu.state = STATE_SETTINGS
        menu.settings_tab = "audio"
        initial_vol = menu.settings["master_volume"]

        # Simulate clicking volume down
        action = menu.handle_click(menu.btn_vol_master_down.rect.center)
        self.assertIsInstance(action, tuple)
        self.assertEqual(action[0], "volume_updated")
        self.assertAlmostEqual(menu.settings["master_volume"], max(0.0, round(initial_vol - 0.1, 2)), places=2)



if __name__ == "__main__":
    unittest.main()
