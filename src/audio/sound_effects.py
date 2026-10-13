"""
Terraria Pygame - Procedural Retro Sound Engine
Synthesizes 8-bit / 16-bit retro audio waveforms (square, noise, sine sweeps)
directly into pygame.mixer.Sound objects without requiring external audio files.
"""

import math
import random
import struct
import pygame

class SoundManager:
    def __init__(self):
        self.enabled = False
        self.channels = 2
        self.sounds = {}
        self.voice_banks = {}
        self.narrator_sounds = {}
        self.narrator_channel = None
        self.voice_channel = None
        self.master_volume = 1.0
        self.sfx_volume = 0.85
        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)
            try:
                pygame.mixer.set_num_channels(16)
                pygame.mixer.set_reserved(2)
                self.narrator_channel = pygame.mixer.Channel(0)
                self.voice_channel = pygame.mixer.Channel(1)
            except Exception:
                pass
            self.enabled = True
            self._synthesize_all_sounds()
            self._load_or_synthesize_narrator_sounds()
        except Exception as e:
            print(f"[SoundManager] Audio initialization notice: {e}. Running in silent mode.")

    def set_volumes(self, master=None, sfx=None, bgm=None, **kwargs):
        if master is not None:
            self.master_volume = max(0.0, min(1.0, master))
        if sfx is not None:
            self.sfx_volume = max(0.0, min(1.0, sfx))

    def _make_sound(self, samples, sample_rate=22050):
        """Converts floating point samples (-1.0 to 1.0) into a stereo pygame Sound object."""
        buf = bytearray()
        for s in samples:
            s = max(-1.0, min(1.0, s))
            ival = int(s * 32767.0)
            # Duplicate mono sample into left and right audio channels for stereo playback
            buf += struct.pack("<hh", ival, ival)
        return pygame.mixer.Sound(buffer=bytes(buf))

    def _synthesize_all_sounds(self):
        sr = pygame.mixer.get_init()[0] if pygame.mixer.get_init() else 22050
        rng = random.Random(1337)

        # 1. Player Jump: smooth rising chirp (160 Hz -> 380 Hz) with soft attack & pleasant harmonics
        jump_samples = []
        dur = 0.15
        total = int(dur * sr)
        phase = 0.0
        for i in range(total):
            t = i / total
            freq = 160 + 240 * (t ** 0.8)
            phase += 2.0 * math.pi * freq / sr
            # Smooth rounded wave (sine + subtle harmonic) prevents harsh buzzing square-wave start
            wave = math.sin(phase) * 0.82 + math.sin(phase * 2.0) * 0.18
            # 5ms attack envelope removes onset click/pop when re-triggering rapidly
            attack = min(1.0, i / max(1, int(0.005 * sr)))
            decay = (1.0 - t) ** 1.15
            amp = attack * decay * 0.35
            jump_samples.append(wave * amp)
        self.sounds["jump"] = self._make_sound(jump_samples, sr)

        # 2. Dig Dirt: low crunchy filtered noise
        dirt_samples = []
        dur = 0.08
        total = int(dur * sr)
        last_val = 0.0
        for i in range(total):
            t = i / total
            amp = (1.0 - t) * 0.45
            # Low pass filtered noise
            noise = rng.uniform(-1.0, 1.0)
            last_val = 0.7 * last_val + 0.3 * noise
            dirt_samples.append(last_val * amp)
        self.sounds["dig_dirt"] = self._make_sound(dirt_samples, sr)

        # 3. Mine Stone: sharp high-pitch ping + rock crack
        stone_samples = []
        dur = 0.09
        total = int(dur * sr)
        phase = 0.0
        for i in range(total):
            t = i / total
            amp = (1.0 - t) ** 2 * 0.4
            phase += 2.0 * math.pi * 920 / sr
            tone = math.sin(phase) + 0.4 * rng.uniform(-1.0, 1.0)
            stone_samples.append(tone * amp)
        self.sounds["dig_stone"] = self._make_sound(stone_samples, sr)

        # 4. Dig Wood: hollow woody thud (220 Hz modulated)
        wood_samples = []
        dur = 0.09
        total = int(dur * sr)
        phase = 0.0
        for i in range(total):
            t = i / total
            amp = (1.0 - t) ** 1.5 * 0.5
            freq = 240 - 100 * t
            phase += 2.0 * math.pi * freq / sr
            wood_samples.append(math.sin(phase) * amp + 0.2 * rng.uniform(-1.0, 1.0) * amp)
        self.sounds["dig_wood"] = self._make_sound(wood_samples, sr)

        # 5. Sword Swing (Standard): swift airy whoosh
        swing_samples = []
        dur = 0.12
        total = int(dur * sr)
        filt = 0.0
        for i in range(total):
            t = i / total
            amp = math.sin(t * math.pi) * 0.35
            noise = rng.uniform(-1.0, 1.0)
            filt = 0.5 * filt + 0.5 * noise
            swing_samples.append(filt * amp)
        self.sounds["swing"] = self._make_sound(swing_samples, sr)

        # 5b. Fast Weapon Swing (Daggers, katanas, high attack speed): crisp high-frequency swoosh
        fast_samples = []
        dur_f = 0.08
        total_f = int(dur_f * sr)
        filt_f = 0.0
        phase_f = 0.0
        for i in range(total_f):
            t = i / total_f
            amp = math.sin(t * math.pi) * 0.34
            noise = rng.uniform(-1.0, 1.0)
            filt_f = 0.3 * filt_f + 0.7 * noise
            phase_f += 2.0 * math.pi * (520.0 + 180.0 * math.sin(t * math.pi)) / sr
            fast_samples.append((filt_f * 0.65 + math.sin(phase_f) * 0.35) * amp)
        self.sounds["swing_fast"] = self._make_sound(fast_samples, sr)

        # 5c. Heavy Weapon Swing (Greatswords, warhammers): deep, resonant low whoosh
        heavy_samples = []
        dur_h = 0.18
        total_h = int(dur_h * sr)
        filt_h = 0.0
        phase_h = 0.0
        for i in range(total_h):
            t = i / total_h
            amp = math.sin(t * math.pi) * 0.44
            noise = rng.uniform(-1.0, 1.0)
            filt_h = 0.75 * filt_h + 0.25 * noise
            phase_h += 2.0 * math.pi * (160.0 - 60.0 * t) / sr
            heavy_samples.append((filt_h * 0.5 + math.sin(phase_h) * 0.5) * amp)
        self.sounds["swing_heavy"] = self._make_sound(heavy_samples, sr)

        # 5d. Critical Hit Impact: sharp high-transient crack + heavy crunch + ringing tone
        crit_samples = []
        dur_crit = 0.22
        total_crit = int(dur_crit * sr)
        p_c1, p_c2 = 0.0, 0.0
        for i in range(total_crit):
            t = i / total_crit
            amp = (1.0 - t) ** 1.6 * 0.65
            p_c1 += 2.0 * math.pi * (1380.0 - 520.0 * (t ** 0.5)) / sr
            p_c2 += 2.0 * math.pi * (120.0 - 60.0 * t) / sr
            noise_burst = rng.uniform(-0.25, 0.25) if t < 0.25 else 0.0
            crit_samples.append((math.sin(p_c1) * 0.45 + math.sin(p_c2) * 0.40 + noise_burst) * amp)
        self.sounds["crit_hit"] = self._make_sound(crit_samples, sr)

        # 6. Mob Hit: squishy impact crunch
        hit_samples = []
        dur = 0.14
        total = int(dur * sr)
        phase = 0.0
        for i in range(total):
            t = i / total
            amp = (1.0 - t) * 0.6
            freq = 320 - 240 * t
            phase += 2.0 * math.pi * freq / sr
            hit_samples.append((math.sin(phase) + 0.3 * rng.uniform(-1.0, 1.0)) * amp)
        self.sounds["hit_mob"] = self._make_sound(hit_samples, sr)

        # 7. Player Hurt: heavy low thud
        hurt_samples = []
        dur = 0.18
        total = int(dur * sr)
        phase = 0.0
        for i in range(total):
            t = i / total
            amp = (1.0 - t) * 0.7
            freq = 130 - 70 * t
            phase += 2.0 * math.pi * freq / sr
            hurt_samples.append(math.sin(phase) * amp)
        self.sounds["hurt"] = self._make_sound(hurt_samples, sr)

        # 8. Item Pickup: pleasant sparkling two-tone chime (587 Hz -> 880 Hz)
        pickup_samples = []
        dur = 0.15
        total = int(dur * sr)
        phase = 0.0
        half = total // 2
        for i in range(total):
            amp = (1.0 - (i % half) / half) * 0.35
            freq = 660 if i < half else 990
            phase += 2.0 * math.pi * freq / sr
            pickup_samples.append(math.sin(phase) * amp)
        self.sounds["pickup"] = self._make_sound(pickup_samples, sr)

        # 9. Block Placement: brief subtle click
        place_samples = []
        dur = 0.04
        total = int(dur * sr)
        for i in range(total):
            t = i / total
            amp = (1.0 - t) * 0.3
            place_samples.append(rng.uniform(-1.0, 1.0) * amp)
        self.sounds["place"] = self._make_sound(place_samples, sr)

        # 10. Craft: metallic chime ping
        craft_samples = []
        dur = 0.22
        total = int(dur * sr)
        phase1, phase2 = 0.0, 0.0
        for i in range(total):
            t = i / total
            amp = (1.0 - t) ** 1.8 * 0.4
            phase1 += 2.0 * math.pi * 523.25 / sr  # C5
            phase2 += 2.0 * math.pi * 1046.5 / sr  # C6
            craft_samples.append((math.sin(phase1) * 0.6 + math.sin(phase2) * 0.4) * amp)
        self.sounds["craft"] = self._make_sound(craft_samples, sr)

        # 11. Bow Shoot: string snap & whoosh
        bow_samples = []
        dur = 0.12
        total = int(dur * sr)
        phase = 0.0
        for i in range(total):
            t = i / total
            amp = (1.0 - t) ** 2.0 * 0.45
            freq = 420.0 - 240.0 * t
            phase += 2.0 * math.pi * freq / sr
            bow_samples.append((math.sin(phase) + rng.uniform(-0.15, 0.15)) * amp)
        self.sounds["bow"] = self._make_sound(bow_samples, sr)

        # 12. Starfury: descending shimmering celestial chord
        star_samples = []
        dur = 0.35
        total = int(dur * sr)
        phase1, phase2, phase3 = 0.0, 0.0, 0.0
        for i in range(total):
            t = i / total
            amp = (1.0 - t) ** 1.2 * 0.38
            f1 = 1320.0 - 500.0 * (t ** 0.5)
            f2 = 1760.0 - 600.0 * (t ** 0.5)
            f3 = 2640.0 - 800.0 * (t ** 0.7)
            phase1 += 2.0 * math.pi * f1 / sr
            phase2 += 2.0 * math.pi * f2 / sr
            phase3 += 2.0 * math.pi * f3 / sr
            sample = (math.sin(phase1) * 0.4 + math.sin(phase2) * 0.35 + math.sin(phase3) * 0.25) * amp
            star_samples.append(sample)
        self.sounds["starfury"] = self._make_sound(star_samples, sr)
        self.sounds["astral_wrath"] = self.sounds["starfury"]

        # 13. Explode: low deep rumble impact burst
        explode_samples = []
        dur = 0.28
        total = int(dur * sr)
        last_n = 0.0
        phase = 0.0
        for i in range(total):
            t = i / total
            amp = (1.0 - t) ** 1.5 * 0.55
            raw_n = rng.uniform(-1.0, 1.0)
            filtered_n = last_n * 0.8 + raw_n * 0.2
            last_n = filtered_n
            phase += 2.0 * math.pi * (80.0 - 45.0 * t) / sr
            explode_samples.append((filtered_n * 0.7 + math.sin(phase) * 0.3) * amp)
        self.sounds["explode"] = self._make_sound(explode_samples, sr)

        # 14. Typewriter Blip: soft, crisp mechanical text tick
        type_samples = []
        dur_type = 0.03
        total_type = int(dur_type * sr)
        phase_type = 0.0
        for i in range(total_type):
            t = i / total_type
            amp = (1.0 - t) ** 2.2 * 0.22
            freq = 820.0 - 240.0 * t
            phase_type += 2.0 * math.pi * freq / sr
            click = rng.uniform(-0.15, 0.15) if i < int(total_type * 0.15) else 0.0
            type_samples.append((math.sin(phase_type) * 0.8 + click) * amp)
        self.sounds["typewriter"] = self._make_sound(type_samples, sr)

        # 15. Dialogue Chime: gentle celestial bell chime on advancing
        chime_samples = []
        dur_chime = 0.35
        total_chime = int(dur_chime * sr)
        p_c1 = 0.0
        p_c2 = 0.0
        for i in range(total_chime):
            t = i / total_chime
            amp = math.exp(-6.5 * t) * 0.30
            p_c1 += 2.0 * math.pi * 659.25 / sr
            p_c2 += 2.0 * math.pi * 987.77 / sr
            chime_samples.append((math.sin(p_c1) * 0.6 + math.sin(p_c2) * 0.4) * amp)
        self.sounds["dialogue_chime"] = self._make_sound(chime_samples, sr)

        # 16. Retro Synth Voices (Animal Crossing / Undertale / Banjo-Kazooie style phoneme chirps)
        # 16a. Pip the Guide: Cheerful, warm, mid-pitched acoustic blips (340-480Hz with soft attack/decay)
        guide_pitches = [355.0, 390.0, 425.0, 465.0]
        guide_sounds = []
        for idx, base_f in enumerate(guide_pitches):
            samples = []
            dur = 0.058
            total = int(dur * sr)
            phase = 0.0
            for i in range(total):
                t = i / total
                freq = base_f + 25.0 * math.sin(t * math.pi)
                phase += 2.0 * math.pi * freq / sr
                amp = (math.sin(t * math.pi) ** 1.15) * 0.36
                s = (math.sin(phase) * 0.72 + math.sin(2.0 * phase) * 0.22 + (1.0 - 2.0 * abs((phase / math.pi) % 2.0 - 1.0)) * 0.06) * amp
                samples.append(s)
            snd = self._make_sound(samples, sr)
            self.sounds[f"voice_guide_{idx}"] = snd
            guide_sounds.append(snd)
        self.sounds["voice_guide"] = guide_sounds[0]
        self.sounds["voice_pip"] = guide_sounds[0]
        self.voice_banks["guide"] = guide_sounds
        self.voice_banks["pip"] = guide_sounds

        # 16b. Sol-Rho / Nether Titans: Heavy, low-frequency rumbling tones (sub-bass 65-110Hz square/saw buzz with resonant filter)
        titan_pitches = [68.0, 80.0, 94.0, 108.0]
        titan_sounds = []
        for idx, base_f in enumerate(titan_pitches):
            samples = []
            dur = 0.105
            total = int(dur * sr)
            phase = 0.0
            last_filt = 0.0
            for i in range(total):
                t = i / total
                phase += 2.0 * math.pi * base_f / sr
                sq = 1.0 if math.sin(phase) > 0 else -1.0
                saw = 2.0 * (phase / (2.0 * math.pi) - math.floor(phase / (2.0 * math.pi) + 0.5))
                buzz = sq * 0.5 + saw * 0.5
                last_filt = last_filt * 0.68 + buzz * 0.32
                amp = ((1.0 - t) ** 1.3) * 0.52
                sub = math.sin(phase * 0.5) * 0.34
                samples.append((last_filt + sub) * amp)
            snd = self._make_sound(samples, sr)
            self.sounds[f"voice_titan_{idx}"] = snd
            titan_sounds.append(snd)
        self.sounds["voice_titan"] = titan_sounds[0]
        self.sounds["voice_titans"] = titan_sounds[0]
        self.sounds["voice_sol_rho"] = titan_sounds[0]
        self.sounds["voice_malus"] = titan_sounds[0]
        self.sounds["voice_ignis"] = titan_sounds[0]
        self.sounds["voice_cryo"] = titan_sounds[0]
        self.voice_banks["titan"] = titan_sounds
        self.voice_banks["titans"] = titan_sounds
        self.voice_banks["sol_rho"] = titan_sounds
        self.voice_banks["malus"] = titan_sounds

        # 16c. Barnaby the Merchant: Quirky, brassy merchant babble (220-300Hz)
        merc_pitches = [225.0, 248.0, 272.0, 295.0]
        merc_sounds = []
        for idx, base_f in enumerate(merc_pitches):
            samples = []
            dur = 0.065
            total = int(dur * sr)
            phase = 0.0
            for i in range(total):
                t = i / total
                vib = math.sin(2.0 * math.pi * 15.0 * (i / sr)) * 16.0
                phase += 2.0 * math.pi * (base_f + vib) / sr
                saw = 2.0 * (phase / (2.0 * math.pi) - math.floor(phase / (2.0 * math.pi) + 0.5))
                amp = (math.sin(t * math.pi) ** 1.2) * 0.36
                samples.append(saw * amp)
            snd = self._make_sound(samples, sr)
            self.sounds[f"voice_merchant_{idx}"] = snd
            merc_sounds.append(snd)
        self.sounds["voice_merchant"] = merc_sounds[0]
        self.sounds["voice_barnaby"] = merc_sounds[0]
        self.voice_banks["merchant"] = merc_sounds
        self.voice_banks["barnaby"] = merc_sounds

        # 16d. Florencia the Nurse: Gentle, higher-pitched melodic chimes (500-650Hz)
        nurse_pitches = [523.25, 565.0, 610.0, 659.25]
        nurse_sounds = []
        for idx, base_f in enumerate(nurse_pitches):
            samples = []
            dur = 0.082
            total = int(dur * sr)
            p1, p2 = 0.0, 0.0
            for i in range(total):
                t = i / total
                p1 += 2.0 * math.pi * base_f / sr
                p2 += 2.0 * math.pi * (base_f * 2.76) / sr
                amp = math.exp(-5.6 * t) * 0.32
                samples.append((math.sin(p1) * 0.75 + math.sin(p2) * 0.25) * amp)
            snd = self._make_sound(samples, sr)
            self.sounds[f"voice_nurse_{idx}"] = snd
            nurse_sounds.append(snd)
        self.sounds["voice_nurse"] = nurse_sounds[0]
        self.sounds["voice_florencia"] = nurse_sounds[0]
        self.voice_banks["nurse"] = nurse_sounds
        self.voice_banks["florencia"] = nurse_sounds

        # 16e. Russet the Blacksmith: Gruff, metallic resonant clinks (140-190Hz)
        smith_pitches = [145.0, 160.0, 175.0, 190.0]
        smith_sounds = []
        for idx, base_f in enumerate(smith_pitches):
            samples = []
            dur = 0.075
            total = int(dur * sr)
            ps, pr = 0.0, 0.0
            for i in range(total):
                t = i / total
                ps += 2.0 * math.pi * base_f / sr
                pr += 2.0 * math.pi * (1650.0 + idx * 120.0) / sr
                metal_ring = math.sin(pr) * math.exp(-42.0 * t) * 0.40
                sq = 1.0 if math.sin(ps) > 0 else -1.0
                amp = math.exp(-6.8 * t) * 0.42
                samples.append((sq * 0.60 + metal_ring) * amp)
            snd = self._make_sound(samples, sr)
            self.sounds[f"voice_blacksmith_{idx}"] = snd
            smith_sounds.append(snd)
        self.sounds["voice_blacksmith"] = smith_sounds[0]
        self.sounds["voice_russet"] = smith_sounds[0]
        self.voice_banks["blacksmith"] = smith_sounds
        self.voice_banks["russet"] = smith_sounds

        # 16f. Spud: Plucky, adventurous potato hero blips (380-450Hz)
        spud_pitches = [385.0, 415.0, 445.0]
        spud_sounds = []
        for idx, base_f in enumerate(spud_pitches):
            samples = []
            dur = 0.052
            total = int(dur * sr)
            p = 0.0
            for i in range(total):
                t = i / total
                p += 2.0 * math.pi * (base_f + 35.0 * (1.0 - t)) / sr
                amp = (math.sin(t * math.pi) ** 1.3) * 0.35
                samples.append(math.sin(p) * amp)
            snd = self._make_sound(samples, sr)
            self.sounds[f"voice_spud_{idx}"] = snd
            spud_sounds.append(snd)
        self.sounds["voice_spud"] = spud_sounds[0]
        self.voice_banks["spud"] = spud_sounds

        # 16g. Elder Tuber: Warm, resonant woody baritone (165-215Hz)
        elder_pitches = [168.0, 192.0, 214.0]
        elder_sounds = []
        for idx, base_f in enumerate(elder_pitches):
            samples = []
            dur = 0.085
            total = int(dur * sr)
            p1, p2 = 0.0, 0.0
            for i in range(total):
                t = i / total
                p1 += 2.0 * math.pi * base_f / sr
                p2 += 2.0 * math.pi * (base_f * 2.0) / sr
                amp = (math.sin(t * math.pi) ** 1.1) * 0.38
                samples.append((math.sin(p1) * 0.70 + math.sin(p2) * 0.30) * amp)
            snd = self._make_sound(samples, sr)
            self.sounds[f"voice_elder_{idx}"] = snd
            elder_sounds.append(snd)
        self.sounds["voice_elder"] = elder_sounds[0]
        self.sounds["voice_elder_tuber"] = elder_sounds[0]
        self.voice_banks["elder"] = elder_sounds
        self.voice_banks["elder_tuber"] = elder_sounds

        # 16h. Narrator Blip: Deep resonant mythic vocal blip (82-115Hz)
        narrator_pitches = [82.0, 96.0, 110.0]
        narrator_sounds = []
        for idx, base_f in enumerate(narrator_pitches):
            samples = []
            dur = 0.095
            total = int(dur * sr)
            p = 0.0
            for i in range(total):
                t = i / total
                p += 2.0 * math.pi * base_f / sr
                glot = math.sin(p) * 0.65 + math.sin(2.0 * p) * 0.35
                amp = (math.sin(t * math.pi) ** 1.2) * 0.42
                samples.append(glot * amp)
            snd = self._make_sound(samples, sr)
            self.sounds[f"voice_narrator_{idx}"] = snd
            narrator_sounds.append(snd)
        self.sounds["voice_narrator"] = narrator_sounds[0]
        self.voice_banks["narrator"] = narrator_sounds

    def _load_or_synthesize_narrator_sounds(self):
        """Loads or synthesizes the cutscene cinematic narrator voice tracks (scenes and segments)."""
        import os
        try:
            from src.audio.narrator_voice import ensure_narrator_audio_assets, normalize_scene_key
            asset_paths = ensure_narrator_audio_assets()
            for sc_key, wav_path in asset_paths.items():
                if os.path.isfile(wav_path):
                    try:
                        snd = pygame.mixer.Sound(wav_path)
                        self.sounds[sc_key] = snd
                        self.sounds[sc_key.replace("scene", "scene_")] = snd
                        self.narrator_sounds[sc_key] = snd
                        norm = normalize_scene_key(sc_key)
                        self.narrator_sounds[norm] = snd
                    except Exception as e:
                        print(f"[SoundManager] Could not load {wav_path}: {e}")
        except Exception as e:
            print(f"[SoundManager] Narrator audio setup notice: {e}")

    def play(self, sound_name, volume=1.0):
        """Plays a sound uniformly at given volume."""
        if not self.enabled:
            return None
        if sound_name == "jump":
            import time
            now = time.time()
            if not hasattr(self, "_last_jump_play"):
                self._last_jump_play = 0.0
                self._jump_consecutive_count = 0
            time_since = now - self._last_jump_play
            if time_since < 0.22:
                return None
            if time_since < 0.65:
                self._jump_consecutive_count = getattr(self, "_jump_consecutive_count", 0) + 1
            else:
                self._jump_consecutive_count = 1
            self._last_jump_play = now

            # Smoothly attenuate rapidly repeating jumps to eliminate annoying auditory fatigue
            if self._jump_consecutive_count == 2:
                volume *= 0.55
            elif self._jump_consecutive_count >= 3:
                volume *= 0.25
        snd = self.sounds.get(sound_name)
        if snd:
            ch = snd.play()
            if ch:
                final_vol = volume * self.master_volume * self.sfx_volume
                ch.set_volume(final_vol, final_vol)
            return ch
        return None

    def play_spatial(self, sound_name, sound_x, sound_y, listener_x, listener_y, max_distance=1100.0):
        """Plays 3D spatial directional stereo sound with distance attenuation and panning."""
        if not self.enabled:
            return None
        snd = self.sounds.get(sound_name)
        if not snd:
            return None
        
        dx = float(sound_x - listener_x)
        dy = float(sound_y - listener_y)
        dist = math.hypot(dx, dy)
        if dist > max_distance:
            return None

        # Distance volume falloff (cubic for natural audio decay)
        volume = (max(0.0, 1.0 - (dist / max_distance)) ** 1.3) * self.master_volume * self.sfx_volume
        
        # Panning calculation: -1.0 (hard left) to +1.0 (hard right)
        pan = max(-1.0, min(1.0, dx / 480.0))
        left_vol = max(0.0, min(1.0, volume * (1.0 - pan * 0.75)))
        right_vol = max(0.0, min(1.0, volume * (1.0 + pan * 0.75)))

        ch = snd.play()
        if ch:
            ch.set_volume(left_vol, right_vol)
        return ch

    def play_swing(self, cooldown=0.30, speed_mult=1.0):
        """Plays weapon swing swoosh scaled to weapon archetype and attack speed."""
        if cooldown <= 0.25 or speed_mult >= 1.25:
            return self.play("swing_fast", volume=0.9)
        elif cooldown >= 0.40 or speed_mult <= 0.8:
            return self.play("swing_heavy", volume=1.1)
        return self.play("swing", volume=1.0)

    def play_voice(self, speaker, volume=0.35):
        """
        Plays a character's retro synth voice blip according to speaker identity.
        Animal Crossing / Undertale / Banjo-Kazooie style phoneme chirps.
        """
        if not self.enabled:
            return None

        if hasattr(speaker, "npc_type"):
            raw_spk = str(speaker.npc_type)
        elif hasattr(speaker, "boss_type"):
            raw_spk = str(speaker.boss_type)
        elif hasattr(speaker, "name"):
            raw_spk = str(speaker.name)
        else:
            raw_spk = str(speaker)

        spk_str = raw_spk.lower().strip().replace("-", "_").replace(" ", "_")
        cat = "guide"
        if any(k in spk_str for k in ("pip", "guide")):
            cat = "guide"
        elif any(k in spk_str for k in ("barnaby", "merchant")):
            cat = "merchant"
        elif any(k in spk_str for k in ("florencia", "nurse")):
            cat = "nurse"
        elif any(k in spk_str for k in ("russet", "blacksmith")):
            cat = "blacksmith"
        elif any(k in spk_str for k in ("sol_rho", "titan", "malus", "ignis", "cryo", "necro")):
            cat = "titan"
        elif "spud" in spk_str:
            cat = "spud"
        elif "elder" in spk_str:
            cat = "elder"
        elif "narrator" in spk_str:
            cat = "narrator"

        bank = self.voice_banks.get(cat)
        if bank:
            snd = random.choice(bank)
        else:
            snd = self.sounds.get(f"voice_{cat}") or self.sounds.get(f"voice_{spk_str}") or self.sounds.get("typewriter")

        if snd:
            final_vol = volume * self.master_volume * self.sfx_volume
            if self.voice_channel:
                try:
                    self.voice_channel.play(snd)
                    self.voice_channel.set_volume(final_vol, final_vol)
                    return self.voice_channel
                except Exception:
                    pass
            ch = snd.play()
            if ch:
                ch.set_volume(final_vol, final_vol)
            return ch
        return None

    def play_narrator(self, scene_id, volume=1.0):
        """
        Plays the deep, mythic cinematic cutscene narrator voice track for the specified scene or dialogue entry.
        """
        if not self.enabled:
            return None
        from src.audio.narrator_voice import normalize_scene_key
        sc_key = normalize_scene_key(scene_id)
        snd = self.sounds.get(sc_key) or self.narrator_sounds.get(sc_key)
        # Fallback to scene-level composite track if entry segment is missing
        if not snd and "_" in sc_key:
            base_key = sc_key.rsplit("_", 1)[0]
            snd = self.sounds.get(base_key) or self.narrator_sounds.get(base_key)
        if not snd:
            snd = self.sounds.get("voice_narrator")
        if snd:
            final_vol = volume * self.master_volume * self.sfx_volume
            if self.narrator_channel:
                try:
                    self.narrator_channel.stop()
                    self.narrator_channel.play(snd)
                    self.narrator_channel.set_volume(final_vol, final_vol)
                    return self.narrator_channel
                except Exception:
                    pass
            ch = snd.play()
            if ch:
                ch.set_volume(final_vol, final_vol)
            return ch
        return None

    def stop_narrator(self, fade_ms=250):
        """Stops or smoothly fades out the cutscene narrator voice track."""
        if not self.enabled or not self.narrator_channel:
            return
        try:
            if self.narrator_channel.get_busy():
                if fade_ms > 0:
                    self.narrator_channel.fadeout(fade_ms)
                else:
                    self.narrator_channel.stop()
        except Exception:
            pass

    def is_narrator_playing(self):
        """Returns True if the narrator voice track is currently actively playing."""
        if self.enabled and self.narrator_channel:
            try:
                return self.narrator_channel.get_busy()
            except Exception:
                pass
        return False



