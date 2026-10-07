"""
Potaria - Cinematic Procedural Synth Background Music (BGM) Engine
Synthesizes long 16-second multi-voice cinematic chiptune/orchestral themes
for Biomes, Caves, Dungeon, Mini-Bosses, and Grand Boss Sol-Rho (Phases 1 & 2).
Features smooth crossfading, channel separation, and volume controls.
Developer: Kurados
"""

import os
import wave
import math
import struct
import random
import pygame
from src.constants import (
    BIOME_FOREST, BIOME_DESERT, BIOME_SNOW,
    BIOME_CORRUPTION, BIOME_MUSHROOM, BIOME_DUNGEON, BIOME_CAVERN
)

class BgmManager:
    def __init__(self):
        self.enabled = False
        self.tracks = {}
        self.master_volume = 1.0
        self.bgm_volume = 0.65
        
        self.current_track = None
        self.next_track = None
        self.crossfade_timer = 0.0
        self.crossfade_duration = 1.6
        
        self.channel_a = None
        self.channel_b = None
        self.active_channel = "A"

        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)
            
            # Channels 6 & 7 reserved for BGM crossfade
            pygame.mixer.set_num_channels(12)
            self.channel_a = pygame.mixer.Channel(6)
            self.channel_b = pygame.mixer.Channel(7)
            self.enabled = True
            self._synthesize_all_tracks()
        except Exception as e:
            print(f"[BgmManager] Audio notice: {e}. Running in silent BGM mode.")

    def _make_loop_sound(self, samples, sample_rate=22050, track_name=None):
        buf = bytearray()
        for s in samples:
            s = max(-1.0, min(1.0, s))
            ival = int(s * 32767.0)
            buf += struct.pack("<hh", ival, ival)
        if track_name:
            cache_dir = os.path.join("assets", "bgm")
            try:
                os.makedirs(cache_dir, exist_ok=True)
                wav_path = os.path.join(cache_dir, f"{track_name}.wav")
                with wave.open(wav_path, "wb") as wf:
                    wf.setnchannels(2)
                    wf.setsampwidth(2)
                    wf.setframerate(sample_rate)
                    wf.writeframes(bytes(buf))
            except Exception:
                pass
        return pygame.mixer.Sound(buffer=bytes(buf))

    def _synthesize_all_tracks(self):
        cache_dir = os.path.join("assets", "bgm")
        unique_tracks = [
            "menu", BIOME_FOREST, "night", BIOME_DESERT, BIOME_SNOW, BIOME_CORRUPTION,
            BIOME_CAVERN, BIOME_DUNGEON, "grand_boss_phase1", "grand_boss_phase2", "victory", "cutscene"
        ]
        if os.path.exists(cache_dir):
            for t in unique_tracks:
                wav_p = os.path.join(cache_dir, f"{t}.wav")
                if os.path.exists(wav_p):
                    try:
                        self.tracks[t] = pygame.mixer.Sound(wav_p)
                    except Exception:
                        pass
            self.tracks[BIOME_MUSHROOM] = self.tracks.get(BIOME_CAVERN)
            self.tracks["miniboss"] = self.tracks.get(BIOME_DUNGEON)
            self.tracks["battle"] = self.tracks.get(BIOME_DUNGEON)
            if all(t in self.tracks for t in unique_tracks):
                return

        sr = 22050
        dur = 16.0  # 16-Second Cinematic Loops!
        total = int(dur * sr)
        rng = random.Random(999)

        # 1. Forest: 16-measure peaceful pastoral synth (C Major & F Major uplifting chords)
        forest_notes = [
            261.63, 329.63, 392.00, 523.25,  329.63, 392.00, 440.00, 392.00,
            349.23, 440.00, 523.25, 659.25,  440.00, 392.00, 329.63, 293.66,
            261.63, 329.63, 392.00, 440.00,  523.25, 659.25, 523.25, 392.00,
            293.66, 349.23, 392.00, 440.00,  392.00, 329.63, 293.66, 261.63
        ]
        forest_samples = []
        for i in range(total):
            t = i / sr
            step = int((t / dur) * len(forest_notes)) % len(forest_notes)
            note = forest_notes[step]
            phase = 2.0 * math.pi * note * t
            sub_t = (t % (dur / len(forest_notes))) / (dur / len(forest_notes))
            env = math.exp(-3.2 * sub_t)
            lead = math.sin(phase) * env * 0.20
            # Warm pad chord & acoustic sub-bass
            bass_note = note / 2.0 if note > 300 else note
            bass = math.sin(2.0 * math.pi * (bass_note / 2.0) * t) * 0.12
            pad = math.sin(2.0 * math.pi * 130.81 * t) * 0.05
            forest_samples.append(lead + bass + pad)
        self.tracks[BIOME_FOREST] = self._make_loop_sound(forest_samples, sr, track_name=BIOME_FOREST)

        # 2. Desert: 16s Phrygian dominant desert sands & percussion
        desert_notes = [
            293.66, 311.13, 369.99, 392.00, 440.00, 392.00, 369.99, 311.13,
            293.66, 369.99, 440.00, 466.16, 440.00, 392.00, 369.99, 311.13,
            246.94, 293.66, 311.13, 369.99, 392.00, 369.99, 311.13, 293.66,
            220.00, 293.66, 369.99, 392.00, 311.13, 293.66, 220.00, 293.66
        ]
        desert_samples = []
        for i in range(total):
            t = i / sr
            step = int((t / dur) * len(desert_notes)) % len(desert_notes)
            note = desert_notes[step]
            phase = 2.0 * math.pi * note * t
            sub_t = (t % (dur / len(desert_notes))) / (dur / len(desert_notes))
            pluck = (1.0 - sub_t) ** 2 * 0.25
            wave = (math.sin(phase) + 0.3 * math.sin(phase * 2.0)) * pluck
            # Sand pulse & low drone
            sand = rng.uniform(-0.035, 0.035) * (1.0 + math.sin(t * 4.0) * 0.5)
            drone = math.sin(2.0 * math.pi * 146.83 * t) * 0.12
            desert_samples.append(wave + sand + drone)
        self.tracks[BIOME_DESERT] = self._make_loop_sound(desert_samples, sr, track_name=BIOME_DESERT)

        # 3. Snow: 16s Glacial crystal bells and aurora pads
        snow_notes = [
            329.63, 392.00, 493.88, 587.33, 659.25, 783.99, 659.25, 493.88,
            392.00, 493.88, 587.33, 783.99, 880.00, 783.99, 587.33, 493.88,
            329.63, 440.00, 493.88, 659.25, 783.99, 659.25, 493.88, 440.00,
            261.63, 329.63, 392.00, 493.88, 587.33, 493.88, 392.00, 329.63
        ]
        snow_samples = []
        for i in range(total):
            t = i / sr
            step = int((t / dur) * len(snow_notes)) % len(snow_notes)
            note = snow_notes[step]
            phase = 2.0 * math.pi * note * t
            sub_t = (t % (dur / len(snow_notes))) / (dur / len(snow_notes))
            bell = math.exp(-3.8 * sub_t)
            harm = (math.sin(phase) * 0.16 + math.sin(phase * 2.0) * 0.07 + math.sin(phase * 3.0) * 0.04) * bell
            frost_drone = math.sin(2.0 * math.pi * (note / 4.0) * t) * 0.08
            snow_samples.append(harm + frost_drone)
        self.tracks[BIOME_SNOW] = self._make_loop_sound(snow_samples, sr, track_name=BIOME_SNOW)

        # 4. Corruption / The Blight: 16s Dark eerie dissonance and corrupted sub-pulses
        corrupt_notes = [
            92.50, 130.81, 155.56, 123.47, 92.50, 110.00, 138.59, 103.83,
            82.41, 116.54, 146.83, 110.00, 82.41, 98.00,  123.47, 92.50,
            92.50, 130.81, 155.56, 185.00, 155.56, 130.81, 110.00, 92.50,
            73.42, 103.83, 130.81, 92.50,  82.41, 110.00, 92.50,  65.41
        ]
        corrupt_samples = []
        for i in range(total):
            t = i / sr
            step = int((t / dur) * len(corrupt_notes)) % len(corrupt_notes)
            note = corrupt_notes[step]
            phase = 2.0 * math.pi * note * t
            sq = 1.0 if math.sin(phase) > 0 else -1.0
            pulse = math.sin(t * 6.0) * 0.5 + 0.5
            dist = sq * 0.11 * pulse
            sub = math.sin(phase * 0.5) * 0.16
            corrupt_samples.append(dist + sub)
        self.tracks[BIOME_CORRUPTION] = self._make_loop_sound(corrupt_samples, sr, track_name=BIOME_CORRUPTION)

        # 5. Cavern & Glowing Mushroom: 16s Echoing subterranean plinks & deep reverb bass
        cavern_notes = [
            110.00, 164.81, 220.00, 261.63, 329.63, 220.00, 164.81, 130.81,
            98.00,  146.83, 196.00, 246.94, 293.66, 196.00, 146.83, 110.00,
            87.31,  130.81, 174.61, 220.00, 261.63, 174.61, 130.81, 98.00,
            110.00, 146.83, 185.00, 220.00, 277.18, 220.00, 164.81, 110.00
        ]
        cavern_samples = []
        for i in range(total):
            t = i / sr
            step = int((t / dur) * len(cavern_notes)) % len(cavern_notes)
            note = cavern_notes[step]
            phase = 2.0 * math.pi * note * t
            sub_t = (t % (dur / len(cavern_notes))) / (dur / len(cavern_notes))
            plink = math.exp(-5.5 * sub_t) * math.sin(2.0 * math.pi * (note * 3.0) * t) * 0.14
            reverb_bass = math.sin(2.0 * math.pi * 55.0 * t) * 0.15 + math.sin(phase) * 0.08
            cavern_samples.append(plink + reverb_bass)
        self.tracks[BIOME_CAVERN] = self._make_loop_sound(cavern_samples, sr, track_name=BIOME_CAVERN)
        self.tracks[BIOME_MUSHROOM] = self.tracks[BIOME_CAVERN]

        # 6. Dungeon & Mini-Boss Battle Theme: Driving 16s battle ostinato with heavy percussion
        mini_boss_notes = [
            220.00, 261.63, 329.63, 440.00, 523.25, 440.00, 329.63, 261.63,
            196.00, 246.94, 293.66, 392.00, 493.88, 392.00, 293.66, 246.94,
            174.61, 220.00, 261.63, 349.23, 440.00, 349.23, 261.63, 220.00,
            164.81, 207.65, 246.94, 329.63, 415.30, 329.63, 246.94, 196.00
        ]
        mini_boss_samples = []
        for i in range(total):
            t = i / sr
            step = int((t / dur) * len(mini_boss_notes)) % len(mini_boss_notes)
            note = mini_boss_notes[step]
            phase = 2.0 * math.pi * note * t
            sub_t = (t % (dur / len(mini_boss_notes))) / (dur / len(mini_boss_notes))
            stab = (1.0 - sub_t) * 0.22
            saw = (2.0 * (t * note - math.floor(0.5 + t * note))) * stab * 0.15
            beat = math.exp(-14.0 * (t % 0.5)) * math.sin(2.0 * math.pi * 80.0 * t) * 0.28
            bass = math.sin(2.0 * math.pi * (note / 2.0) * t) * 0.13
            mini_boss_samples.append(saw + beat + bass)
        self.tracks[BIOME_DUNGEON] = self._make_loop_sound(mini_boss_samples, sr, track_name=BIOME_DUNGEON)
        self.tracks["miniboss"] = self.tracks[BIOME_DUNGEON]
        self.tracks["battle"] = self.tracks[BIOME_DUNGEON]

        # 7. Grand Boss Phase 1: SOL-RHO THE CELESTIAL TITAN (Majestic Golden Choir & Timpani Ostinato)
        p1_notes = [
            261.63, 329.63, 392.00, 523.25, 659.25, 523.25, 392.00, 329.63,
            293.66, 369.99, 440.00, 587.33, 739.99, 587.33, 440.00, 369.99,
            329.63, 392.00, 493.88, 659.25, 783.99, 659.25, 493.88, 392.00,
            349.23, 440.00, 523.25, 698.46, 880.00, 698.46, 523.25, 440.00
        ]
        p1_samples = []
        for i in range(total):
            t = i / sr
            step = int((t / dur) * len(p1_notes)) % len(p1_notes)
            note = p1_notes[step]
            phase = 2.0 * math.pi * note * t
            # Brass lead & choral harmonics
            brass = math.sin(phase) * 0.18 + math.sin(phase * 1.5) * 0.08
            # Timpani pounding on quarter beats
            timpani = math.exp(-12.0 * (t % 0.5)) * math.sin(2.0 * math.pi * 65.0 * t) * 0.32
            # Celestial high choir shimmer
            choir = math.sin(2.0 * math.pi * (note * 2.0) * t) * 0.08
            sub_drone = math.sin(2.0 * math.pi * 65.41 * t) * 0.14
            p1_samples.append(brass + timpani + choir + sub_drone)
        self.tracks["grand_boss_phase1"] = self._make_loop_sound(p1_samples, sr, track_name="grand_boss_phase1")

        # 8. Grand Boss Phase 2: AWAKENED VOID GOD (Dark Apocalyptic Cosmic Void Tempo & Syncopated Drums)
        p2_notes = [
            110.00, 116.54, 138.59, 164.81, 220.00, 164.81, 138.59, 116.54,
            98.00,  103.83, 123.47, 146.83, 196.00, 146.83, 123.47, 103.83,
            87.31,  92.50,  110.00, 130.81, 174.61, 130.81, 110.00, 92.50,
            73.42,  82.41,  98.00,  116.54, 146.83, 116.54, 98.00,  82.41
        ]
        p2_samples = []
        for i in range(total):
            t = i / sr
            step = int((t / dur) * len(p2_notes)) % len(p2_notes)
            note = p2_notes[step]
            phase = 2.0 * math.pi * note * t
            # Distorted aggressive bass saw
            saw = (2.0 * (t * note - math.floor(0.5 + t * note))) * 0.18
            # Double kick void drum (0.25s intervals)
            kick = math.exp(-16.0 * (t % 0.25)) * math.sin(2.0 * math.pi * 50.0 * t) * 0.35
            # Chaotic cosmic dissonance
            void_drone = math.sin(2.0 * math.pi * (note * 1.414) * t) * 0.09
            p2_samples.append(saw + kick + void_drone)
        self.tracks["grand_boss_phase2"] = self._make_loop_sound(p2_samples, sr, track_name="grand_boss_phase2")

        # 9. Main Menu: 16s Cinematic Uplifting Pastoral Theme (C Major / G Major)
        if "menu" not in self.tracks:
            menu_notes = [
                261.63, 329.63, 392.00, 523.25,  392.00, 329.63, 392.00, 523.25,
                349.23, 440.00, 523.25, 659.25,  523.25, 440.00, 349.23, 329.63,
                293.66, 369.99, 440.00, 587.33,  440.00, 369.99, 293.66, 261.63,
                261.63, 329.63, 392.00, 440.00,  523.25, 440.00, 329.63, 261.63
            ]
            menu_samples = []
            for i in range(total):
                t = i / sr
                step = int((t / dur) * len(menu_notes)) % len(menu_notes)
                note = menu_notes[step]
                phase = 2.0 * math.pi * note * t
                sub_t = (t % (dur / len(menu_notes))) / (dur / len(menu_notes))
                env = math.exp(-3.0 * sub_t)
                lead = math.sin(phase) * env * 0.18 + math.sin(phase * 2.0) * env * 0.06
                bass = math.sin(2.0 * math.pi * (note / 2.0) * t) * 0.12
                shimmer = math.sin(2.0 * math.pi * 130.81 * t) * 0.05
                menu_samples.append(lead + bass + shimmer)
            self.tracks["menu"] = self._make_loop_sound(menu_samples, sr, track_name="menu")

        # 10. Night: 16s Mystical Nocturne Ambient Theme (A Minor / E Minor)
        if "night" not in self.tracks:
            night_notes = [
                220.00, 261.63, 329.63, 440.00,  329.63, 261.63, 220.00, 196.00,
                174.61, 220.00, 261.63, 349.23,  261.63, 220.00, 174.61, 196.00,
                164.81, 207.65, 246.94, 329.63,  246.94, 207.65, 164.81, 146.83,
                220.00, 261.63, 329.63, 440.00,  329.63, 220.00, 196.00, 220.00
            ]
            night_samples = []
            for i in range(total):
                t = i / sr
                step = int((t / dur) * len(night_notes)) % len(night_notes)
                note = night_notes[step]
                phase = 2.0 * math.pi * note * t
                sub_t = (t % (dur / len(night_notes))) / (dur / len(night_notes))
                bell = math.exp(-4.2 * sub_t) * math.sin(phase) * 0.16
                pad = math.sin(2.0 * math.pi * (note / 2.0) * t) * 0.10
                night_samples.append(bell + pad)
            self.tracks["night"] = self._make_loop_sound(night_samples, sr, track_name="night")

        # 11. Victory: 16s Grand Triumphant Fanfare Anthem
        if "victory" not in self.tracks:
            vic_notes = [
                329.63, 392.00, 523.25, 659.25,  783.99, 659.25, 523.25, 659.25,
                392.00, 523.25, 659.25, 783.99, 1046.50, 783.99, 659.25, 783.99,
                440.00, 523.25, 659.25, 880.00,  659.25, 523.25, 440.00, 523.25,
                523.25, 659.25, 783.99, 1046.50, 783.99, 659.25, 523.25, 523.25
            ]
            vic_samples = []
            for i in range(total):
                t = i / sr
                step = int((t / dur) * len(vic_notes)) % len(vic_notes)
                note = vic_notes[step]
                phase = 2.0 * math.pi * note * t
                brass = (math.sin(phase) * 0.20 + math.sin(phase * 1.5) * 0.08)
                timp = math.exp(-10.0 * (t % 0.5)) * math.sin(2.0 * math.pi * 70.0 * t) * 0.26
                vic_samples.append(brass + timp)
            self.tracks["victory"] = self._make_loop_sound(vic_samples, sr, track_name="victory")

        # 12. Cutscene: 16s Cinematic Atmospheric Synth (D Minor / Bb Major / F Major / C Major)
        if "cutscene" not in self.tracks:
            cut_notes = [
                146.83, 220.00, 293.66, 349.23,  293.66, 220.00, 174.61, 220.00,
                116.54, 174.61, 233.08, 293.66,  349.23, 293.66, 233.08, 174.61,
                87.31,  130.81, 174.61, 220.00,  261.63, 220.00, 174.61, 130.81,
                130.81, 196.00, 261.63, 329.63,  392.00, 329.63, 261.63, 196.00
            ]
            cut_samples = []
            for i in range(total):
                t = i / sr
                step = int((t / dur) * len(cut_notes)) % len(cut_notes)
                note = cut_notes[step]
                phase = 2.0 * math.pi * note * t
                sub_t = (t % (dur / len(cut_notes))) / (dur / len(cut_notes))
                # Ambient bell arpeggio with subtle shimmer
                bell = math.exp(-3.8 * sub_t) * (math.sin(phase) * 0.16 + math.sin(phase * 2.0) * 0.05)
                # Warm cinematic pad
                pad = math.sin(2.0 * math.pi * (note / 2.0) * t) * 0.12 + math.sin(2.0 * math.pi * (note * 1.003) * t) * 0.06
                # Deep resonant sub-bass
                bass_f = 73.42 if step < 8 else (58.27 if step < 16 else (43.65 if step < 24 else 65.41))
                bass = math.sin(2.0 * math.pi * bass_f * t) * 0.15
                # Celestial high frequency shimmer
                celestial = math.sin(2.0 * math.pi * 880.0 * t) * (0.02 + 0.015 * math.sin(t * 1.8))
                cut_samples.append(bell + pad + bass + celestial)
            self.tracks["cutscene"] = self._make_loop_sound(cut_samples, sr, track_name="cutscene")

    def set_volumes(self, master=1.0, bgm=0.65):
        self.master_volume = max(0.0, min(1.0, master))
        self.bgm_volume = max(0.0, min(1.0, bgm))
        self._apply_channel_volumes(
            blend_a=(1.0 if self.active_channel == "A" else 0.0),
            blend_b=(1.0 if self.active_channel == "B" else 0.0)
        )

    def _apply_channel_volumes(self, blend_a, blend_b):
        if not self.enabled:
            return
        final_vol_a = self.master_volume * self.bgm_volume * max(0.0, min(1.0, blend_a))
        final_vol_b = self.master_volume * self.bgm_volume * max(0.0, min(1.0, blend_b))
        if self.channel_a:
            self.channel_a.set_volume(final_vol_a)
        if self.channel_b:
            self.channel_b.set_volume(final_vol_b)

    def transition_to(self, track_name):
        if not self.enabled or track_name not in self.tracks:
            return
        if track_name == self.current_track:
            if self.next_track is not None:
                # Cancel pending transition and cleanly restore current track
                if self.active_channel == "A":
                    self.channel_b.stop()
                    self._apply_channel_volumes(blend_a=1.0, blend_b=0.0)
                else:
                    self.channel_a.stop()
                    self._apply_channel_volumes(blend_a=0.0, blend_b=1.0)
                self.next_track = None
                self.crossfade_timer = 0.0
            return
        if track_name == self.next_track:
            return

        self.next_track = track_name
        self.crossfade_timer = 0.0

        target_snd = self.tracks[track_name]
        if self.active_channel == "A":
            self.channel_b.play(target_snd, loops=-1)
            self.channel_b.set_volume(0.0)
        else:
            self.channel_a.play(target_snd, loops=-1)
            self.channel_a.set_volume(0.0)

    def update(self, dt, current_biome=None, has_nearby_threat=False, is_boss_active=False, boss_phase=1, is_grand_boss=False, scene=None, is_night=False, is_cavern=False):
        if not self.enabled:
            return

        # Determine target track with hierarchy:
        # Scene override (Cutscene / Menu / Victory) > Grand Boss Phase 2 > Grand Boss Phase 1 > Mini-Boss > Battle > Cavern > Night > Biome
        if scene in ("cutscene", "story", "STATE_CUTSCENE", "STATE_STORY") or scene == "cutscene":
            target = "cutscene" if "cutscene" in self.tracks else "menu"
        elif scene in ("menu", "STATE_MENU") or scene == "menu":
            target = "menu"
        elif scene in ("victory", "STATE_VICTORY") or scene == "victory":
            target = "victory"
        elif is_boss_active and is_grand_boss:
            target = "grand_boss_phase2" if boss_phase == 2 else "grand_boss_phase1"
        elif is_boss_active:
            target = "miniboss"
        elif has_nearby_threat:
            target = "battle"
        elif is_cavern and BIOME_CAVERN in self.tracks:
            target = BIOME_CAVERN
        elif is_night and "night" in self.tracks:
            target = "night"
        elif current_biome in self.tracks:
            target = current_biome
        elif "menu" in self.tracks and (current_biome is None):
            target = "menu"
        else:
            target = BIOME_FOREST

        if self.current_track is None:
            self.current_track = target
            snd = self.tracks.get(target)
            if snd:
                self.channel_a.play(snd, loops=-1)
                self._apply_channel_volumes(blend_a=1.0, blend_b=0.0)
            return

        if target != self.current_track:
            if self.next_track != target:
                self.transition_to(target)
        elif self.next_track is not None:
            self.transition_to(target)

        # Handle active crossfading
        if self.next_track:
            self.crossfade_timer += dt
            progress = min(1.0, self.crossfade_timer / self.crossfade_duration)

            if self.active_channel == "A":
                self._apply_channel_volumes(blend_a=1.0 - progress, blend_b=progress)
            else:
                self._apply_channel_volumes(blend_a=progress, blend_b=1.0 - progress)

            if progress >= 1.0:
                if self.active_channel == "A":
                    self.channel_a.stop()
                    self.active_channel = "B"
                else:
                    self.channel_b.stop()
                    self.active_channel = "A"

                self.current_track = self.next_track
                self.next_track = None
                self.crossfade_timer = 0.0
                if self.active_channel == "A":
                    self._apply_channel_volumes(blend_a=1.0, blend_b=0.0)
                else:
                    self._apply_channel_volumes(blend_a=0.0, blend_b=1.0)

    def update_tick(self, dt):
        """Advances active crossfade without switching target tracks (e.g. while paused in-game)."""
        if not self.enabled:
            return
        if self.next_track:
            self.crossfade_timer += dt
            progress = min(1.0, self.crossfade_timer / self.crossfade_duration)

            if self.active_channel == "A":
                self._apply_channel_volumes(blend_a=1.0 - progress, blend_b=progress)
            else:
                self._apply_channel_volumes(blend_a=progress, blend_b=1.0 - progress)

            if progress >= 1.0:
                if self.active_channel == "A":
                    self.channel_a.stop()
                    self.active_channel = "B"
                else:
                    self.channel_b.stop()
                    self.active_channel = "A"

                self.current_track = self.next_track
                self.next_track = None
                self.crossfade_timer = 0.0
                if self.active_channel == "A":
                    self._apply_channel_volumes(blend_a=1.0, blend_b=0.0)
                else:
                    self._apply_channel_volumes(blend_a=0.0, blend_b=1.0)

    def stop(self):
        if self.channel_a:
            self.channel_a.stop()
        if self.channel_b:
            self.channel_b.stop()
        self.current_track = None
        self.next_track = None
