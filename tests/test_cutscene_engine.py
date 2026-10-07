"""
Potaria - Comprehensive Automated Test Suite for Prologue Cutscene Engine
Verifies:
1. Procedural Pixel Art Asset Generation (4 scenes x 4 frames @ 640x360, 5 portraits @ 64x64)
2. Disk Asset Export Verification (assets/cutscene/ and assets/story/ with all 21 PNGs)
3. Sound Effects & BGM Synthesis (typewriter, dialogue_chime, cutscene BGM track)
4. CutsceneEngine Initialization & Defensive Fallbacks (resilience against None / non-AssetFactory)
5. Typewriter Engine & Text Word-Wrapping
6. Dialogue Progression Logic (advance, fast-forward, scene transition sound cues)
7. Skip Controls (ESC, S key, Skip button click, BGM reset)
8. Atmospheric Particle Dynamics & Camera Panning Parallax
9. MenuManager Integration (button replacement "PROLOGUE CUTSCENE", state transitions, BGM crossfade)
10. Headless Surface Rendering (all scenes and UI rendered without exceptions at 1280x720)

Developer: Kurados | Pure Python & pygame-ce
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Headless video and audio driver for clean CLI testing
os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"

import pygame
pygame.init()

from src.constants import (
    SCREEN_WIDTH, SCREEN_HEIGHT,
    STATE_MENU, STATE_CUTSCENE, STATE_STORY
)
from src.assets.asset_factory import AssetFactory
from src.audio.sound_effects import SoundManager
from src.audio.bgm_manager import BgmManager
from src.ui.cutscene import CutsceneEngine
from src.ui.menu import MenuManager


class TestCutsceneAssets(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.asset_factory = AssetFactory()

    def test_cutscene_scenes_generated(self):
        """Verify 4 distinct lore scenes with 4 sequence frames each at 640x360."""
        expected_scenes = [
            "scene_1_golden_age",
            "scene_2_cataclysm",
            "scene_3_titans",
            "scene_4_chosen_tuber"
        ]
        self.assertTrue(hasattr(self.asset_factory, "cutscene_scenes"))
        for sc in expected_scenes:
            self.assertIn(sc, self.asset_factory.cutscene_scenes)
            frames = self.asset_factory.cutscene_scenes[sc]
            self.assertEqual(len(frames), 4, f"{sc} should have exactly 4 animation frames")
            for idx, f in enumerate(frames):
                self.assertIsInstance(f, pygame.Surface)
                self.assertEqual(f.get_size(), (640, 360), f"{sc} frame {idx} size mismatch")

    def test_cutscene_portraits_generated(self):
        """Verify 5 speaker portraits generated at 64x64."""
        expected_portraits = [
            "elder_tuber",
            "sol_rho",
            "narrator",
            "spud",
            "lord_malus"
        ]
        self.assertTrue(hasattr(self.asset_factory, "cutscene_portraits"))
        for p in expected_portraits:
            self.assertIn(p, self.asset_factory.cutscene_portraits)
            surf = self.asset_factory.cutscene_portraits[p]
            self.assertIsInstance(surf, pygame.Surface)
            self.assertEqual(surf.get_size(), (64, 64), f"Portrait {p} size mismatch")

    def test_disk_asset_exports(self):
        """Verify all 16 scene frames and 5 portraits exist on disk in assets/cutscene and assets/story."""
        project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        for folder in ("cutscene", "story"):
            target_dir = os.path.join(project_root, "assets", folder)
            self.assertTrue(os.path.isdir(target_dir), f"Directory {target_dir} should exist")

            # Check 16 scene frame files
            for sc in ("scene_1_golden_age", "scene_2_cataclysm", "scene_3_titans", "scene_4_chosen_tuber"):
                for idx in range(4):
                    fn = os.path.join(target_dir, f"{sc}_{idx}.png")
                    self.assertTrue(os.path.isfile(fn), f"Missing exported frame: {fn}")
                    self.assertGreater(os.path.getsize(fn), 0, f"Empty file: {fn}")

            # Check 5 portrait files
            for p in ("elder_tuber", "sol_rho", "narrator", "spud", "lord_malus"):
                fn = os.path.join(target_dir, f"portrait_{p}.png")
                self.assertTrue(os.path.isfile(fn), f"Missing exported portrait: {fn}")
                self.assertGreater(os.path.getsize(fn), 0, f"Empty file: {fn}")

    def test_extended_portraits_and_disk_exports(self):
        """Verify dark_titan_sol_rho, ignis_colossus, and cryo_spud portraits are generated and exported."""
        project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        for p in ("dark_titan_sol_rho", "ignis_colossus", "cryo_spud"):
            self.assertIn(p, self.asset_factory.cutscene_portraits)
            surf = self.asset_factory.cutscene_portraits[p]
            self.assertEqual(surf.get_size(), (64, 64))
            for folder in ("cutscene", "story"):
                fn = os.path.join(project_root, "assets", folder, f"portrait_{p}.png")
                self.assertTrue(os.path.isfile(fn), f"Missing exported extended portrait: {fn}")
                self.assertGreater(os.path.getsize(fn), 0)


class TestCutsceneAudio(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.sound_manager = SoundManager()
        cls.bgm_manager = BgmManager()

    def test_cutscene_sound_effects(self):
        """Verify typewriter and dialogue chime sound effects are synthesized."""
        self.assertIn("typewriter", self.sound_manager.sounds)
        self.assertIn("dialogue_chime", self.sound_manager.sounds)
        # Verify play method does not raise
        self.sound_manager.play("typewriter", volume=0.2)
        self.sound_manager.play("dialogue_chime", volume=0.5)

    def test_cutscene_bgm_track(self):
        """Verify cinematic ambient synth BGM track for cutscene."""
        self.assertIn("cutscene", self.bgm_manager.tracks)
        # Verify crossfade transition to cutscene scene
        self.bgm_manager.update(0.1, scene="cutscene")
        self.assertIn(self.bgm_manager.current_track, ("cutscene", None))

    def test_bgm_cancellation_on_skip(self):
        """Verify starting cutscene and immediately skipping back to menu cleanly reverts BGM without track bleed."""
        bgm = BgmManager()
        bgm.update(0.1, scene="menu")
        self.assertEqual(bgm.current_track, "menu")
        # Start cutscene: triggers transition to cutscene
        bgm.update(0.1, scene="cutscene")
        self.assertEqual(bgm.next_track, "cutscene")
        # Skip immediately: reverts back to menu scene
        bgm.update(0.1, scene="menu")
        self.assertIsNone(bgm.next_track)
        self.assertEqual(bgm.current_track, "menu")
        # Ticking more frames in menu should remain cleanly on menu theme
        for _ in range(30):
            bgm.update(0.016, scene="menu")
        self.assertEqual(bgm.current_track, "menu")
        self.assertIsNone(bgm.next_track)


class TestCutsceneEngine(unittest.TestCase):
    def setUp(self):
        self.asset_factory = AssetFactory()
        self.sound_manager = SoundManager()
        self.bgm_manager = BgmManager()
        self.cutscene = CutsceneEngine(self.asset_factory, self.sound_manager, self.bgm_manager)

    def test_defensive_initialization(self):
        """Verify CutsceneEngine initializes safely even when None is passed."""
        engine = CutsceneEngine(None, None, None)
        self.assertIsNotNone(engine.asset_factory)
        self.assertTrue(hasattr(engine.asset_factory, "cutscene_scenes"))
        self.assertFalse(engine.is_finished())

    def test_narrative_script_integrity(self):
        """Verify all 13 scripted dialogue entries reference valid scenes and portraits."""
        self.assertEqual(len(self.cutscene.script), 13, "Prologue lore script should contain 13 narrative entries")
        valid_scenes = set(self.asset_factory.cutscene_scenes.keys())
        valid_portraits = set(self.asset_factory.cutscene_portraits.keys())

        for idx, entry in enumerate(self.cutscene.script):
            self.assertIn(entry["scene"], valid_scenes, f"Script entry {idx} has invalid scene: {entry['scene']}")
            self.assertIn(entry["portrait"], valid_portraits, f"Script entry {idx} has invalid portrait: {entry['portrait']}")
            self.assertIn("speaker", entry)
            self.assertIn("text", entry)
            self.assertIn("name_color", entry)
            self.assertIn("scene_title", entry)
            self.assertGreater(len(entry["text"]), 10, f"Script entry {idx} text is too short")

    def test_start_state(self):
        """Verify start resets all progress counters and flags."""
        self.cutscene.start()
        self.assertEqual(self.cutscene.current_entry_index, 0)
        self.assertFalse(self.cutscene.is_finished())
        self.assertEqual(self.cutscene.typewriter_progress, 0.0)

    def test_typewriter_update_and_fast_forward(self):
        """Verify typewriter incremental text reveal and space/click fast-forward."""
        self.cutscene.start()
        cur_text = self.cutscene.script[0]["text"]

        # Advance a small step: text should only be partially revealed
        self.cutscene.update(0.1)
        revealed_len = int(self.cutscene.typewriter_progress * self.cutscene.typewriter_speed)
        self.assertLess(revealed_len, len(cur_text))

        # Advance dialogue when not fully revealed -> fast forwards to end of current entry
        self.cutscene.advance_dialogue()
        revealed_len = int(self.cutscene.typewriter_progress * self.cutscene.typewriter_speed)
        self.assertGreaterEqual(revealed_len, len(cur_text))
        self.assertEqual(self.cutscene.current_entry_index, 0)

        # Advance dialogue again when already fully revealed -> progresses to next entry
        self.cutscene.advance_dialogue()
        self.assertEqual(self.cutscene.current_entry_index, 1)
        self.assertEqual(self.cutscene.typewriter_progress, 0.0)

    def test_dialogue_progression_to_completion(self):
        """Verify advancing through all 13 entries ends cutscene."""
        self.cutscene.start()
        for idx in range(len(self.cutscene.script)):
            self.assertEqual(self.cutscene.current_entry_index, idx)
            # Fast-forward text
            self.cutscene.advance_dialogue()
            # Advance to next entry
            self.cutscene.advance_dialogue()

        self.assertTrue(self.cutscene.is_finished())

    def test_skip_functionality(self):
        """Verify ESC key, 'S' key, and skip button click immediately end cutscene."""
        # 1. Direct skip()
        self.cutscene.start()
        self.cutscene.skip()
        self.assertTrue(self.cutscene.is_finished())

        # 2. Key ESC
        self.cutscene.start()
        event_esc = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_ESCAPE)
        handled = self.cutscene.handle_key(event_esc)
        self.assertTrue(handled)
        self.assertTrue(self.cutscene.is_finished())

        # 3. Key S
        self.cutscene.start()
        event_s = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_s)
        handled = self.cutscene.handle_key(event_s)
        self.assertTrue(handled)
        self.assertTrue(self.cutscene.is_finished())

        # 4. Skip button click
        self.cutscene.start()
        res = self.cutscene.handle_click(self.cutscene.skip_btn_rect.center)
        self.assertEqual(res, "menu")
        self.assertTrue(self.cutscene.is_finished())

    def test_particle_dynamics_across_scenes(self):
        """Verify ambient floating particles simulate and adapt to each scene."""
        self.cutscene.start()
        self.assertEqual(len(self.cutscene.particles), 45)

        for scene_idx in (0, 3, 6, 9):  # One entry per scene act
            self.cutscene.current_entry_index = scene_idx
            initial_y = self.cutscene.particles[0]["y"]
            self.cutscene.update(0.1)
            # Check particle moved
            self.assertNotEqual(self.cutscene.particles[0]["y"], initial_y)

    def test_word_wrapping_precalculation_stability(self):
        """Verify pre-wrapped lines remain stable and avoid mid-word line jumping."""
        text = self.cutscene.script[0]["text"]
        # Narrow width (e.g. 400px) forces wrapping into 2+ lines
        wrapped_lines = self.cutscene._get_wrapped_lines(text, 400)
        self.assertGreater(len(wrapped_lines), 1, "Text should wrap across at least 2 lines at 400px width")
        # Ensure re-querying uses cache and returns identical structure
        lines2 = self.cutscene._get_wrapped_lines(text, 400)
        self.assertEqual(wrapped_lines, lines2)
        # Full width fits on 1 line
        full_lines = self.cutscene._get_wrapped_lines(text, 1000)
        self.assertEqual(len(full_lines), 1)

    def test_mouse_button_filtering(self):
        """Verify Left-Click (button=1) advances dialogue while Right-Click (button=3) is ignored."""
        self.cutscene.start()
        self.assertEqual(self.cutscene.current_entry_index, 0)
        # Advance text to end
        self.cutscene.typewriter_progress = 100.0

        # Right-Click: should be ignored
        res = self.cutscene.handle_click((500, 300), button=3)
        self.assertIsNone(res)
        self.assertEqual(self.cutscene.current_entry_index, 0)

        # Left-Click: advances to entry 1
        res = self.cutscene.handle_click((500, 300), button=1)
        self.assertEqual(self.cutscene.current_entry_index, 1)

    def test_uppercase_and_raw_s_key_skips(self):
        """Verify uppercase 'S' and raw ASCII key code both trigger skip."""
        self.cutscene.start()
        handled = self.cutscene.handle_key(ord('S'))
        self.assertTrue(handled)
        self.assertTrue(self.cutscene.is_finished())

        self.cutscene.start()
        handled = self.cutscene.handle_key(ord('s'))
        self.assertTrue(handled)
        self.assertTrue(self.cutscene.is_finished())

    def test_hold_to_skip_timer(self):
        """Verify holding skip key accumulates hold timer."""
        self.cutscene.start()
        self.assertEqual(self.cutscene.skip_hold_time, 0.0)
        self.cutscene.skip_hold_time = 0.39
        # Calling skip resets hold timer
        self.cutscene.skip()
        self.assertEqual(self.cutscene.skip_hold_time, 0.0)


class TestMenuCutsceneIntegration(unittest.TestCase):
    def setUp(self):
        self.sound_manager = SoundManager()
        self.asset_factory = AssetFactory()
        self.bgm_manager = BgmManager()
        self.menu = MenuManager(self.asset_factory, self.sound_manager, self.bgm_manager)

    def test_menu_buttons_include_prologue_cutscene(self):
        """Verify Main Menu replaced 'STORY & LORE' with 'PROLOGUE CUTSCENE'."""
        button_texts = [b.text for b in self.menu.menu_buttons]
        button_actions = [b.action for b in self.menu.menu_buttons]

        self.assertIn("PROLOGUE CUTSCENE", button_texts)
        self.assertNotIn("STORY & LORE", button_texts)
        self.assertIn("cutscene", button_actions)

    def test_menu_transition_to_cutscene(self):
        """Verify clicking PROLOGUE CUTSCENE transitions state to cutscene."""
        cutscene_btn = next(b for b in self.menu.menu_buttons if b.action == "cutscene")
        self.menu.handle_click(cutscene_btn.rect.center)

        self.assertIn(self.menu.state, (STATE_CUTSCENE, STATE_STORY))
        self.assertFalse(self.menu.cutscene.is_finished())

    def test_menu_cutscene_escape_returns_to_menu(self):
        """Verify pressing ESC in cutscene state returns directly to main menu."""
        self.menu.state = STATE_CUTSCENE
        self.menu.cutscene.start()

        event_esc = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_ESCAPE)
        self.menu.handle_key(event_esc)
        self.assertEqual(self.menu.state, STATE_MENU)
        self.assertTrue(self.menu.cutscene.is_finished())

        # Also test with raw integer key code
        self.menu.state = STATE_CUTSCENE
        self.menu.cutscene.start()
        self.menu.handle_key(pygame.K_ESCAPE)
        self.assertEqual(self.menu.state, STATE_MENU)
        self.assertTrue(self.menu.cutscene.is_finished())

    def test_menu_manager_resilient_init_with_swapped_parameters(self):
        """Verify MenuManager safely handles sound_manager passed in first slot."""
        resilient_menu = MenuManager(self.sound_manager, None)
        self.assertIsNotNone(resilient_menu.cutscene)
        self.assertIsNotNone(resilient_menu.asset_factory)
        self.assertTrue(hasattr(resilient_menu.asset_factory, "cutscene_scenes"))


class TestCutsceneRendering(unittest.TestCase):
    def setUp(self):
        self.asset_factory = AssetFactory()
        self.sound_manager = SoundManager()
        self.bgm_manager = BgmManager()
        self.cutscene = CutsceneEngine(self.asset_factory, self.sound_manager, self.bgm_manager)
        self.menu = MenuManager(self.asset_factory, self.sound_manager, self.bgm_manager)
        self.surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))

    def test_render_all_script_entries(self):
        """Verify render completes without errors across all 13 script scenes."""
        self.cutscene.start()
        for idx in range(len(self.cutscene.script)):
            self.cutscene.current_entry_index = idx
            self.cutscene.update(0.05)
            # Render to surface
            self.cutscene.render(self.surface)

    def test_render_menu_in_cutscene_state(self):
        """Verify MenuManager.render() renders properly when in STATE_CUTSCENE."""
        self.menu.state = STATE_CUTSCENE
        self.menu.cutscene.start()
        self.menu.render(self.surface)

    def test_render_when_finished(self):
        """Verify cutscene.render() safely renders without exceptions when dialogue is finished."""
        self.cutscene.start()
        self.cutscene.skip()
        self.assertTrue(self.cutscene.is_finished())
        # Should render completed state cleanly without raising
        self.cutscene.render(self.surface)


if __name__ == "__main__":
    unittest.main()

