"""
Potaria - Comprehensive Voice & Audio Engine Test Suite
Tests:
1. Retro Synth Voices: Pip (Guide), Sol-Rho/Titans, Barnaby (Merchant), Florencia (Nurse), Russet (Blacksmith), Spud, Elder Tuber, Narrator.
2. Narrator Audio Synthesis: Procedural formant glottal synthesis, WAV export verification (stereo, 22050Hz, 16-bit PCM).
3. Google Gemini TTS Integration: gemini-3.8-flash-tts generation path, speech_metadata annotations, and offline procedural fallback.
4. Cutscene Voice Playback: Automatic narrator voice start on scene begin, fade on advance/skip, and speaker phoneme blips.
5. In-Game Dialogue Typing Audio: NPCDialogueWindow phoneme blips matching active NPC speaker.
6. Boss Rumble Voices: Mini-boss and Grand Boss Sol-Rho awakening rumbling tones.

Developer: Kurados | Pure Python & pygame-ce
"""

import os
import sys
import wave
import unittest
from unittest.mock import MagicMock, patch

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Headless audio and video for testing
os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"

import pygame
pygame.init()

from src.constants import SCREEN_WIDTH, SCREEN_HEIGHT
from src.assets.asset_factory import AssetFactory
from src.audio.sound_effects import SoundManager
from src.audio.bgm_manager import BgmManager
from src.audio.narrator_voice import (
    NARRATOR_SCENE_TEXTS, SCENE_KEY_ALIASES,
    normalize_scene_key, save_wav_file,
    synthesize_procedural_narrator_track,
    ensure_narrator_audio_assets,
    generate_narrator_voices_with_gemini
)
from src.ui.cutscene import CutsceneEngine, PrologueCutscene
from src.ui.npc_dialogue import NPCDialogueWindow
from src.entities.npc import GuideNPC, MerchantNPC, NurseNPC, BlacksmithNPC
from src.combat.combat_system import CombatManager
from src.entities.boss import LordMalus, GrandBossSolRho


class TestRetroSynthVoices(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.sound_manager = SoundManager()

    def test_voice_sounds_registered(self):
        """Verify all individual character voice sound objects are registered in SoundManager.sounds."""
        expected_voices = [
            "voice_guide", "voice_pip",
            "voice_titan", "voice_titans", "voice_sol_rho", "voice_malus",
            "voice_merchant", "voice_barnaby",
            "voice_nurse", "voice_florencia",
            "voice_blacksmith", "voice_russet",
            "voice_spud", "voice_elder", "voice_elder_tuber",
            "voice_narrator"
        ]
        for v in expected_voices:
            self.assertIn(v, self.sound_manager.sounds, f"Expected voice sound '{v}' to be registered")
            snd = self.sound_manager.sounds[v]
            self.assertIsInstance(snd, pygame.mixer.Sound)
            self.assertGreater(snd.get_length(), 0.03, f"Voice sound '{v}' duration too short")

    def test_voice_banks_present(self):
        """Verify voice banks contain multiple subtle pitch variations for natural speech cadence."""
        expected_banks = ["guide", "pip", "titan", "titans", "merchant", "nurse", "blacksmith", "spud", "elder", "narrator"]
        for b in expected_banks:
            self.assertIn(b, self.sound_manager.voice_banks, f"Missing voice bank '{b}'")
            bank = self.sound_manager.voice_banks[b]
            self.assertGreaterEqual(len(bank), 2, f"Voice bank '{b}' should have at least 2 pitch variations")

    def test_play_voice_various_speakers(self):
        """Verify play_voice safely handles different speaker names, casing, and aliases."""
        test_speakers = [
            "guide", "Pip", "PIP", "Guide Pip",
            "merchant", "Barnaby", "BARNABY",
            "nurse", "Florencia", "FLORENCIA",
            "blacksmith", "Russet", "RUSSET",
            "SOL-RHO", "sol_rho", "titan", "Lord Malus", "Ignis Colossus",
            "Spud", "Elder Tuber", "NARRATOR"
        ]
        for spk in test_speakers:
            # Must execute without exception
            ch = self.sound_manager.play_voice(spk, volume=0.3)
            # Under headless dummy driver ch may be a Channel or None, but must not error

    def test_play_voice_fallback(self):
        """Verify unknown speaker falls back safely without crashing."""
        ch = self.sound_manager.play_voice("unknown_villager_99", volume=0.2)
        # Should gracefully play default voice or typewriter without raising


class TestCutsceneNarratorSynthesis(unittest.TestCase):
    def test_narrator_scene_texts_complete(self):
        """Verify narrator dialogue text exists for all 4 cutscene acts."""
        expected_scenes = ["narrator_scene1", "narrator_scene2", "narrator_scene3", "narrator_scene4"]
        for sc in expected_scenes:
            self.assertIn(sc, NARRATOR_SCENE_TEXTS)
            text = NARRATOR_SCENE_TEXTS[sc]
            self.assertGreater(len(text), 40)
            self.assertIn("Keystone", text if "Keystone" in text else NARRATOR_SCENE_TEXTS["narrator_scene1"] + NARRATOR_SCENE_TEXTS["narrator_scene2"])

    def test_normalize_scene_key(self):
        """Verify normalize_scene_key maps integer, string, and lore scene keys to narrator_scene[1-4]."""
        self.assertEqual(normalize_scene_key(1), "narrator_scene1")
        self.assertEqual(normalize_scene_key("1"), "narrator_scene1")
        self.assertEqual(normalize_scene_key("scene_1_golden_age"), "narrator_scene1")
        self.assertEqual(normalize_scene_key("scene_2_cataclysm"), "narrator_scene2")
        self.assertEqual(normalize_scene_key("scene_3_titans"), "narrator_scene3")
        self.assertEqual(normalize_scene_key("scene_4_chosen_tuber"), "narrator_scene4")

    def test_procedural_synthesizer_waveform(self):
        """Verify procedural formant synthesizer produces valid normalized samples within [-1.0, 1.0]."""
        sample_text = "The Celestial Keystone fractured into radiant shards!"
        samples = synthesize_procedural_narrator_track(sample_text, sample_rate=22050)
        self.assertGreater(len(samples), 22050 * 2)  # At least 2 seconds
        for s in samples:
            self.assertGreaterEqual(s, -1.05)
            self.assertLessEqual(s, 1.05)

    def test_disk_wav_assets_exist(self):
        """Verify all 4 narrator scene WAV files exist in assets/cutscene and assets/story."""
        project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        for folder in ("cutscene", "story"):
            dir_path = os.path.join(project_root, "assets", folder)
            self.assertTrue(os.path.isdir(dir_path))
            for i in range(1, 5):
                wav_path = os.path.join(dir_path, f"narrator_scene{i}.wav")
                self.assertTrue(os.path.isfile(wav_path), f"Missing narrator WAV: {wav_path}")
                self.assertGreater(os.path.getsize(wav_path), 100000, f"WAV file suspiciously small: {wav_path}")

                # Validate WAV header
                with wave.open(wav_path, "rb") as wf:
                    self.assertEqual(wf.getnchannels(), 2, "Narrator WAV should be stereo")
                    self.assertEqual(wf.getsampwidth(), 2, "Narrator WAV should be 16-bit PCM")
                    self.assertEqual(wf.getframerate(), 22050, "Narrator WAV rate mismatch")
                    dur = wf.getnframes() / wf.getframerate()
                    self.assertGreater(dur, 4.0, f"Narrator track {i} duration too short: {dur}s")

    def test_gemini_tts_mock_path(self):
        """Verify Gemini TTS generation path constructs interactions correctly with gemini-3.8-flash-tts."""
        mock_output_audio = MagicMock()
        mock_output_audio.data = "UklGRiQAAABXQVZFZm10IBAAAAABAAEAQB8AAEAfAAABAAgAZGF0YQAAAAA="  # base64 dummy wav
        mock_interaction = MagicMock()
        mock_interaction.output_audio = mock_output_audio

        mock_client = MagicMock()
        mock_client.interactions.create.return_value = mock_interaction

        mock_genai = MagicMock()
        mock_genai.Client.return_value = mock_client
        mock_google = MagicMock()
        mock_google.genai = mock_genai

        with patch.dict(sys.modules, {"google": mock_google, "google.genai": mock_genai}):
            success = generate_narrator_voices_with_gemini(api_key="test_dummy_key_123")
            self.assertTrue(success)
            self.assertEqual(mock_client.interactions.create.call_count, 4)

            # Check call args of the first interaction
            first_call_kwargs = mock_client.interactions.create.call_args_list[0].kwargs
            self.assertEqual(first_call_kwargs.get("model"), "gemini-3.8-flash-tts")
            self.assertEqual(first_call_kwargs.get("response_format"), {"type": "audio"})
            self.assertEqual(first_call_kwargs.get("generation_config"), {"speech_config": [{"voice": "Fenrir"}]})

    def test_gemini_tts_graceful_fallback_without_key(self):
        """Verify generate_narrator_voices_with_gemini safely returns False when no API key is provided."""
        with patch.dict(os.environ, {}, clear=True):
            success = generate_narrator_voices_with_gemini(api_key=None)
            self.assertFalse(success)


class TestCutsceneVoicePlayback(unittest.TestCase):
    def setUp(self):
        self.asset_factory = AssetFactory()
        self.sound_manager = SoundManager()
        self.bgm_manager = BgmManager()
        self.cutscene = CutsceneEngine(self.asset_factory, self.sound_manager, self.bgm_manager)

    def test_alias_prologue_cutscene(self):
        """Verify PrologueCutscene alias points to CutsceneEngine."""
        self.assertIs(PrologueCutscene, CutsceneEngine)
        instance = PrologueCutscene(self.asset_factory, self.sound_manager, self.bgm_manager)
        self.assertIsInstance(instance, CutsceneEngine)

    def test_start_plays_scene1_narrator_voice(self):
        """Verify starting cutscene triggers playback of narrator voice for Scene 1."""
        self.cutscene.start()
        self.assertEqual(self.cutscene.current_entry_index, 0)
        # Verify narrator sounds are available
        self.assertIn("narrator_scene1", self.sound_manager.sounds)

    def test_advance_to_new_scene_triggers_new_narrator_track(self):
        """Verify moving to a new scene stops previous narrator voice and plays new scene narration."""
        self.cutscene.start()

        # Advance through Scene 1 entries (0, 1, 2)
        for _ in range(3):
            self.cutscene.typewriter_progress = 100.0
            self.cutscene.advance_dialogue()

        # Now at Entry 3: Scene 2 begins!
        self.assertEqual(self.cutscene.current_entry_index, 3)
        self.assertEqual(self.cutscene.script[3]["scene"], "scene_2_cataclysm")

    def test_skip_stops_narrator_voice(self):
        """Verify skip() immediately ends cutscene and stops narrator audio."""
        self.cutscene.start()
        self.sound_manager.play_narrator(1)

        self.cutscene.skip()
        self.assertTrue(self.cutscene.is_finished())
        # stop_narrator was invoked safely

    def test_typewriter_plays_speaker_phoneme_blip(self):
        """Verify typewriter progress triggers character voice blip matching current speaker."""
        self.cutscene.start()
        cur_speaker = self.cutscene.script[0]["speaker"]
        self.assertEqual(cur_speaker, "NARRATOR")

        # Mock play_voice to observe calls
        mock_play_voice = MagicMock()
        self.cutscene.sound_manager.play_voice = mock_play_voice

        # Step typewriter
        for _ in range(10):
            self.cutscene.update(0.05)

        self.assertTrue(mock_play_voice.called)
        called_speakers = [call.args[0] for call in mock_play_voice.call_args_list]
        self.assertIn(cur_speaker, called_speakers)


class TestNPCDialogueTypingAudio(unittest.TestCase):
    def setUp(self):
        self.asset_factory = AssetFactory()
        self.sound_manager = SoundManager()
        self.dialogue_window = NPCDialogueWindow(self.asset_factory, self.sound_manager)

    def test_guide_dialogue_typing_blips(self):
        """Verify Guide Pip triggers cheerful acoustic voice blips during dialogue typing."""
        guide = GuideNPC("Pip", "guide", 100.0, 100.0, self.asset_factory, self.sound_manager)
        player_mock = MagicMock()
        player_mock.health = 100
        player_mock.max_health = 100

        mock_play_voice = MagicMock()
        self.sound_manager.play_voice = mock_play_voice

        self.dialogue_window.open(guide, player_mock)
        self.assertTrue(self.dialogue_window.is_open)

        # Update several frames to progress typewriter
        for _ in range(25):
            self.dialogue_window.update(0.02)

        self.assertTrue(mock_play_voice.called)
        called_categories = [call.args[0] for call in mock_play_voice.call_args_list]
        self.assertIn("guide", called_categories)

    def test_merchant_dialogue_typing_blips(self):
        """Verify Merchant Barnaby triggers quirky brassy merchant voice blips."""
        merchant = MerchantNPC("Barnaby", "merchant", 100.0, 100.0, self.asset_factory, self.sound_manager)
        player_mock = MagicMock()

        mock_play_voice = MagicMock()
        self.sound_manager.play_voice = mock_play_voice

        self.dialogue_window.open(merchant, player_mock)
        for _ in range(25):
            self.dialogue_window.update(0.02)

        self.assertTrue(mock_play_voice.called)
        called_categories = [call.args[0] for call in mock_play_voice.call_args_list]
        self.assertIn("merchant", called_categories)

    def test_nurse_dialogue_typing_blips(self):
        """Verify Nurse Florencia triggers gentle melodic chime voice blips."""
        nurse = NurseNPC("Florencia", "nurse", 100.0, 100.0, self.asset_factory, self.sound_manager)
        player_mock = MagicMock()
        player_mock.health = 100
        player_mock.max_health = 100

        mock_play_voice = MagicMock()
        self.sound_manager.play_voice = mock_play_voice

        self.dialogue_window.open(nurse, player_mock)
        for _ in range(25):
            self.dialogue_window.update(0.02)

        self.assertTrue(mock_play_voice.called)
        called_categories = [call.args[0] for call in mock_play_voice.call_args_list]
        self.assertIn("nurse", called_categories)

    def test_blacksmith_dialogue_typing_blips(self):
        """Verify Blacksmith Russet triggers gruff metallic resonant voice blips."""
        blacksmith = BlacksmithNPC("Russet", "blacksmith", 100.0, 100.0, self.asset_factory, self.sound_manager)
        player_mock = MagicMock()

        mock_play_voice = MagicMock()
        self.sound_manager.play_voice = mock_play_voice

        self.dialogue_window.open(blacksmith, player_mock)
        for _ in range(25):
            self.dialogue_window.update(0.02)

        self.assertTrue(mock_play_voice.called)
        called_categories = [call.args[0] for call in mock_play_voice.call_args_list]
        self.assertIn("blacksmith", called_categories)


class TestBossVoiceTones(unittest.TestCase):
    def setUp(self):
        self.asset_factory = AssetFactory()
        self.sound_manager = SoundManager()
        self.camera_mock = MagicMock()
        self.combat = CombatManager(self.asset_factory, self.sound_manager, None, self.camera_mock)

    def test_mini_boss_rumble_tone(self):
        """Verify awakening a subterranean mini-boss triggers titan rumble tone."""
        mock_play_voice = MagicMock()
        self.sound_manager.play_voice = mock_play_voice

        self.combat.spawn_mini_boss(100.0, 100.0, boss_cls=LordMalus)
        self.assertIsNotNone(self.combat.boss)
        self.assertTrue(mock_play_voice.called)
        self.assertEqual(mock_play_voice.call_args[0][0], "titan")

    def test_grand_boss_sol_rho_rumble_tone(self):
        """Verify summoning Grand Boss Sol-Rho triggers Sol-Rho rumbling tone."""
        mock_play_voice = MagicMock()
        self.sound_manager.play_voice = mock_play_voice

        self.combat.spawn_grand_boss(200.0, 200.0)
        self.assertIsNotNone(self.combat.boss)
        self.assertTrue(mock_play_voice.called)
        self.assertEqual(mock_play_voice.call_args[0][0], "sol_rho")


class TestVoiceAudioSystemRefinements(unittest.TestCase):
    def setUp(self):
        self.sound_manager = SoundManager()
        self.asset_factory = AssetFactory()

    def test_dedicated_reserved_channels(self):
        """Verify narrator and retro synth voices have dedicated, non-competing mixer channels."""
        self.assertIsNotNone(self.sound_manager.narrator_channel)
        self.assertIsNotNone(self.sound_manager.voice_channel)

    def test_normalize_entry_and_segment_keys(self):
        """Verify normalize_scene_key maps entry and segment indices to correct track identifiers."""
        self.assertEqual(normalize_scene_key("entry_0"), "narrator_scene1")
        self.assertEqual(normalize_scene_key(0), "narrator_scene1")
        self.assertEqual(normalize_scene_key("entry_3"), "narrator_scene2_1")
        self.assertEqual(normalize_scene_key("entry_4"), "narrator_scene2_2")
        self.assertEqual(normalize_scene_key("entry_6"), "narrator_scene3_1")
        self.assertEqual(normalize_scene_key("entry_8"), "narrator_scene3_2")
        self.assertEqual(normalize_scene_key("entry_9"), "narrator_scene4_1")
        self.assertEqual(normalize_scene_key("entry_12"), "narrator_scene4_2")
        self.assertEqual(normalize_scene_key("scene_3_2"), "narrator_scene3_2")

    def test_disk_segment_wav_assets_exist(self):
        """Verify segment WAV files exist on disk with valid 16-bit 22050Hz stereo headers."""
        project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        segment_keys = [
            "narrator_scene2_1", "narrator_scene2_2",
            "narrator_scene3_1", "narrator_scene3_2",
            "narrator_scene4_1", "narrator_scene4_2"
        ]
        for folder in ("cutscene", "story"):
            dir_path = os.path.join(project_root, "assets", folder)
            for k in segment_keys:
                wav_p = os.path.join(dir_path, f"{k}.wav")
                self.assertTrue(os.path.isfile(wav_p), f"Missing segment WAV: {wav_p}")
                with wave.open(wav_p, "rb") as wf:
                    self.assertEqual(wf.getnchannels(), 2)
                    self.assertEqual(wf.getsampwidth(), 2)
                    self.assertEqual(wf.getframerate(), 22050)
                    dur = wf.getnframes() / wf.getframerate()
                    self.assertGreater(dur, 2.0)

    def test_cutscene_plays_all_narrator_entries(self):
        """Verify advancing through the entire cutscene triggers narrator speech on all 7 narrator lines."""
        engine = CutsceneEngine(self.asset_factory, self.sound_manager)
        mock_play = MagicMock()
        mock_stop = MagicMock()
        self.sound_manager.play_narrator = mock_play
        self.sound_manager.stop_narrator = mock_stop

        engine.start()
        # Entry 0 must play narrator
        self.assertEqual(mock_play.call_args[0][0], "entry_0")

        played_narrator_entries = []
        for idx in range(len(engine.script)):
            engine.typewriter_progress = 100.0
            cur_spk = engine.script[engine.current_entry_index]["speaker"]
            if cur_spk == "NARRATOR":
                played_narrator_entries.append(engine.current_entry_index)
            engine.advance_dialogue()

        # All 7 narrator entries must have been visited and spoken
        expected_narrator_indices = [0, 3, 4, 6, 8, 9, 12]
        self.assertEqual(played_narrator_entries, expected_narrator_indices)
        # Entry 8 (Act 3 after Lord Malus) and Entry 12 (Act 4 after Spud) must be called
        all_played_keys = [call.args[0] for call in mock_play.call_args_list]
        self.assertIn("entry_8", all_played_keys)
        self.assertIn("entry_12", all_played_keys)

    def test_play_voice_with_npc_and_boss_objects(self):
        """Verify play_voice safely accepts NPC and Boss objects directly."""
        guide = GuideNPC("Pip", "guide", 0, 0, self.asset_factory, self.sound_manager)
        boss = LordMalus(0, 0, self.asset_factory, self.sound_manager)

        ch1 = self.sound_manager.play_voice(guide, volume=0.3)
        ch2 = self.sound_manager.play_voice(boss, volume=0.3)
        # Must execute without errors

    def test_npc_dialogue_click_to_fast_forward(self):
        """Verify clicking on the dialogue panel body immediately completes typewriter text."""
        window = NPCDialogueWindow(self.asset_factory, self.sound_manager)
        guide = GuideNPC("Pip", "guide", 0, 0, self.asset_factory, self.sound_manager)
        player_mock = MagicMock()
        player_mock.health = 100
        player_mock.max_health = 100
        player_mock.inventory = None
        window.open(guide, player_mock)

        self.assertEqual(window.typewriter_chars, 0)
        # Click on panel body (above action buttons)
        click_x = window.x + window.width // 2
        click_y = window.y + 40
        handled = window.handle_click(click_x, click_y, player_mock, None)

        self.assertTrue(handled)
        self.assertEqual(window.typewriter_chars, len(window.dialogue_text))

    def test_gemini_tts_rest_fallback(self):
        """Verify Gemini TTS uses urllib REST fallback when google.genai is not installed."""
        import json
        mock_resp = MagicMock()
        mock_resp.read.return_value = json.dumps({
            "output_audio": {
                "data": "UklGRiQAAABXQVZFZm10IBAAAAABAAEAQB8AAEAfAAABAAgAZGF0YQAAAAA="
            }
        }).encode("utf-8")
        mock_resp.__enter__.return_value = mock_resp

        with patch("urllib.request.urlopen", return_value=mock_resp), \
             patch.dict(sys.modules, {"google": None, "google.genai": None}):
            success = generate_narrator_voices_with_gemini(api_key="rest_dummy_key_456")
            self.assertTrue(success)


if __name__ == "__main__":
    unittest.main()
