"""
Potaria - Cinematic 2D Prologue Cutscene Engine
Developer: Kurados
Features:
- Multi-layered procedural pixel art scene sequences depicting the lore of Potaria
- Ornate Terraria x Stardew Valley dialogue box with speaker portraits & typewriter text
- Animated 2D atmospheric visual effects (parallax panning, ambient floating particles, letterboxing)
- Space / Enter / Click dialogue advancement and ESC / 'S' instant skip
- Smooth cinematic BGM crossfade & typewriter audio feedback
"""

import math
import random
import pygame
from src.constants import (
    SCREEN_WIDTH, SCREEN_HEIGHT, COLOR_GOLD, COLOR_WHITE,
    STATE_MENU, STATE_CUTSCENE, STATE_STORY
)

class CutsceneEngine:
    def __init__(self, asset_factory, sound_manager=None, bgm_manager=None):
        from src.assets.asset_factory import AssetFactory
        if not hasattr(asset_factory, "cutscene_scenes") or not hasattr(asset_factory, "cutscene_portraits"):
            self.asset_factory = AssetFactory()
        else:
            self.asset_factory = asset_factory
        self.sound_manager = sound_manager
        self.bgm_manager = bgm_manager

        from src.ui.theme import font_bold, font_regular, font_semibold
        self.font_name = font_bold(16)
        self.font_text = font_regular(16)
        self.font_prompt = font_semibold(13)
        self.font_header = font_bold(14)
        self.font_skip = font_semibold(13)

        # Full narrative lore script
        self.script = [
            # Scene 1: The Golden Age of Sol-Rho
            {
                "scene": "scene_1_golden_age",
                "speaker": "NARRATOR",
                "portrait": "narrator",
                "name_color": (190, 220, 255),
                "text": "In the dawn before memory, the Root Realm of Potaria flourished under the boundless warmth of the Celestial Keystone.",
                "scene_title": "ACT I: THE GOLDEN AGE OF SOL-RHO"
            },
            {
                "scene": "scene_1_golden_age",
                "speaker": "SOL-RHO",
                "portrait": "sol_rho",
                "name_color": (255, 215, 60),
                "text": "Bathe in the solar starlight, children of the loam. As long as the Keystone shines, our harvest shall be eternal.",
                "scene_title": "ACT I: THE GOLDEN AGE OF SOL-RHO"
            },
            {
                "scene": "scene_1_golden_age",
                "speaker": "ELDER TUBER",
                "portrait": "elder_tuber",
                "name_color": (145, 230, 110),
                "text": "For centuries, our ancestors tended the fertile furrows in harmony, knowing neither blight nor darkness.",
                "scene_title": "ACT I: THE GOLDEN AGE OF SOL-RHO"
            },

            # Scene 2: The Celestial Cataclysm & The Sundering
            {
                "scene": "scene_2_cataclysm",
                "speaker": "NARRATOR",
                "portrait": "narrator",
                "name_color": (190, 220, 255),
                "text": "Yet harmony was shattered in an instant. A cosmic cataclysm struck from the void—the Celestial Keystone fractured into radiant shards!",
                "scene_title": "ACT II: THE CELESTIAL CATACLYSM"
            },
            {
                "scene": "scene_2_cataclysm",
                "speaker": "NARRATOR",
                "portrait": "narrator",
                "name_color": (190, 220, 255),
                "text": "The skies darkened with ominous storm clouds, while subterranean fissures bled boiling molten magma and creeping purple corruption.",
                "scene_title": "ACT II: THE CELESTIAL CATACLYSM"
            },
            {
                "scene": "scene_2_cataclysm",
                "speaker": "ELDER TUBER",
                "portrait": "elder_tuber",
                "name_color": (145, 230, 110),
                "text": "The heavens weep! The primal elements have broken unchained, and our fertile paradise fractures into chaos!",
                "scene_title": "ACT II: THE CELESTIAL CATACLYSM"
            },

            # Scene 3: The Rise of the Nether Titans
            {
                "scene": "scene_3_titans",
                "speaker": "NARRATOR",
                "portrait": "narrator",
                "name_color": (190, 220, 255),
                "text": "From the elemental rifts arose three colossal Nether Titans, claiming the shattered celestial shards to bend the biomes to their will.",
                "scene_title": "ACT III: THE RISE OF THE NETHER TITANS"
            },
            {
                "scene": "scene_3_titans",
                "speaker": "LORD MALUS",
                "portrait": "lord_malus",
                "name_color": (235, 80, 255),
                "text": "The Blight shall consume every root and stem! Weep, mortal tubers, as darkness claims the world below!",
                "scene_title": "ACT III: THE RISE OF THE NETHER TITANS"
            },
            {
                "scene": "scene_3_titans",
                "speaker": "NARRATOR",
                "portrait": "narrator",
                "name_color": (190, 220, 255),
                "text": "Ignis Colossus seized the volcanic deeps, Cryo-Spud froze the northern peaks, and Lord Malus entrenched in the Nether Dungeon.",
                "scene_title": "ACT III: THE RISE OF THE NETHER TITANS"
            },

            # Scene 4: The Chosen Tuber
            {
                "scene": "scene_4_chosen_tuber",
                "speaker": "NARRATOR",
                "portrait": "narrator",
                "name_color": (190, 220, 255),
                "text": "When all hope seemed withered beneath the corrupt soil, an ancient prophecy stirred within the sacred earth...",
                "scene_title": "ACT IV: THE CHOSEN TUBER"
            },
            {
                "scene": "scene_4_chosen_tuber",
                "speaker": "ELDER TUBER",
                "portrait": "elder_tuber",
                "name_color": (145, 230, 110),
                "text": "Look! In the sacred furrow, a humble sprout awakens! You, SPUD, are chosen by the soil of destiny.",
                "scene_title": "ACT IV: THE CHOSEN TUBER"
            },
            {
                "scene": "scene_4_chosen_tuber",
                "speaker": "SPUD",
                "portrait": "spud",
                "name_color": (255, 230, 110),
                "text": "I won't let our homeland fall! With this rusty axe and the strength of the earth, I will reclaim the Keystone shards!",
                "scene_title": "ACT IV: THE CHOSEN TUBER"
            },
            {
                "scene": "scene_4_chosen_tuber",
                "speaker": "NARRATOR",
                "portrait": "narrator",
                "name_color": (190, 220, 255),
                "text": "Take up your tools, courageous Spud. Explore the boundless world, master forgotten skills, defeat the Titans, and restore Potaria!",
                "scene_title": "ACT IV: THE CHOSEN TUBER"
            }
        ]

        self.current_entry_index = 0
        self.dialogue_finished = False
        self.typewriter_progress = 0.0
        self.typewriter_speed = 42.0  # chars per second
        self.last_blip_char = 0

        self.animation_time = 0.0
        self.frame_index = 0
        self.frame_timer = 0.0
        self.frame_duration = 0.25  # 4 FPS sequence animation

        # Pre-scale scene frames to (SCREEN_WIDTH + 60, SCREEN_HEIGHT + 40) for smooth parallax
        self.scaled_scenes = {}
        target_w = SCREEN_WIDTH + 60
        target_h = SCREEN_HEIGHT + 40
        for sc_name, frames in self.asset_factory.cutscene_scenes.items():
            self.scaled_scenes[sc_name] = [
                pygame.transform.scale(f, (target_w, target_h))
                for f in frames
            ]

        # Atmospheric particle system
        self.particles = []
        self._init_particles()

        # Letterboxing & UI Rectangles (adaptively sized to avoid bar overlaps)
        self.letterbox_h = 52
        self.dialogue_w = min(1040, max(500, SCREEN_WIDTH - 60))
        self.dialogue_h = min(145, max(110, SCREEN_HEIGHT - self.letterbox_h * 2 - 20))
        self.dialogue_x = (SCREEN_WIDTH - self.dialogue_w) // 2
        self.dialogue_y = max(self.letterbox_h + 8, SCREEN_HEIGHT - self.letterbox_h - self.dialogue_h - 12)
        self.skip_btn_rect = pygame.Rect(SCREEN_WIDTH - 150, 12, 132, 28)
        self.skip_hovered = False

        self.typewriter_sound_timer = 0.0
        self.skip_hold_time = 0.0
        self._wrap_cache = {}

    def _get_wrapped_lines(self, text, max_width):
        cache_key = (text, max_width)
        if cache_key in self._wrap_cache:
            return self._wrap_cache[cache_key]

        words = text.split(" ")
        lines = []
        cur_line = ""
        for word in words:
            test_line = f"{cur_line} {word}".strip() if cur_line else word
            if self.font_text.size(test_line)[0] <= max_width:
                cur_line = test_line
            else:
                if cur_line:
                    lines.append(cur_line)
                cur_line = word
        if cur_line:
            lines.append(cur_line)
        self._wrap_cache[cache_key] = lines
        return lines

    def _init_particles(self):
        self.particles.clear()
        rng = random.Random(888)
        for _ in range(45):
            self.particles.append({
                "x": rng.uniform(0, SCREEN_WIDTH),
                "y": rng.uniform(0, SCREEN_HEIGHT),
                "vx": rng.uniform(-0.4, 0.8),
                "vy": rng.uniform(-0.8, -0.2),
                "size": rng.randint(2, 4),
                "alpha": rng.uniform(100, 240),
                "color_type": "gold"
            })

    def start(self):
        """Starts or resets the cutscene sequence."""
        self.current_entry_index = 0
        self.dialogue_finished = False
        self.typewriter_progress = 0.0
        self.last_blip_char = 0
        self.typewriter_sound_timer = 0.0
        self.skip_hold_time = 0.0
        self.animation_time = 0.0
        self.frame_index = 0
        self.frame_timer = 0.0
        self._init_particles()

        if self.bgm_manager:
            self.bgm_manager.update(0.0, scene="cutscene")
        if self.sound_manager:
            self.sound_manager.play("dialogue_chime", volume=0.5)
            self._play_narrator_for_current_entry()

    def _play_narrator_for_current_entry(self):
        """Automatically plays the deep, mythic narrator voice track for the current dialogue entry."""
        if not self.sound_manager or not hasattr(self.sound_manager, "play_narrator"):
            return
        cur_entry = self.script[self.current_entry_index]
        if cur_entry.get("speaker") != "NARRATOR":
            return
        entry_key = f"entry_{self.current_entry_index}"
        self.sound_manager.play_narrator(entry_key, volume=0.95)

    def _play_narrator_for_current_scene(self):
        """Helper alias to play narrator voice track for current entry / scene."""
        self._play_narrator_for_current_entry()

    def is_finished(self):
        return self.dialogue_finished

    def skip(self):
        """Immediately ends cutscene and signals return to main menu."""
        self.dialogue_finished = True
        self.skip_hold_time = 0.0
        if self.sound_manager:
            self.sound_manager.play("place")
            if hasattr(self.sound_manager, "stop_narrator"):
                self.sound_manager.stop_narrator(fade_ms=200)
        if self.bgm_manager:
            self.bgm_manager.update(0.0, scene="menu")

    def advance_dialogue(self):
        """Advances typewriter or moves to the next dialogue entry."""
        if self.dialogue_finished:
            return

        cur_entry = self.script[self.current_entry_index]
        full_text = cur_entry["text"]
        revealed_len = int(self.typewriter_progress * self.typewriter_speed)

        # If text is still typing, reveal it immediately
        if revealed_len < len(full_text):
            self.typewriter_progress = (len(full_text) + 1) / self.typewriter_speed
            self.last_blip_char = len(full_text)
            return

        # Advance to next entry
        if self.current_entry_index < len(self.script) - 1:
            prev_scene = self.script[self.current_entry_index]["scene"]
            prev_speaker = self.script[self.current_entry_index].get("speaker", "")
            self.current_entry_index += 1
            self.typewriter_progress = 0.0
            self.last_blip_char = 0
            self.typewriter_sound_timer = 0.0
            new_scene = self.script[self.current_entry_index]["scene"]
            new_speaker = self.script[self.current_entry_index].get("speaker", "")

            if new_scene != prev_scene:
                if self.sound_manager:
                    if hasattr(self.sound_manager, "stop_narrator"):
                        self.sound_manager.stop_narrator(fade_ms=250)
                    self.sound_manager.play("dialogue_chime", volume=0.6)
                    if new_speaker == "NARRATOR":
                        self._play_narrator_for_current_entry()
            else:
                # Same scene
                if new_speaker == "NARRATOR":
                    if self.sound_manager:
                        if hasattr(self.sound_manager, "stop_narrator"):
                            self.sound_manager.stop_narrator(fade_ms=150)
                        self._play_narrator_for_current_entry()
                elif prev_speaker == "NARRATOR":
                    if self.sound_manager and hasattr(self.sound_manager, "stop_narrator"):
                        self.sound_manager.stop_narrator(fade_ms=300)
                if self.sound_manager:
                    self.sound_manager.play("place", volume=0.4)
        else:
            # Reached end of cutscene
            self.dialogue_finished = True
            if self.sound_manager and hasattr(self.sound_manager, "stop_narrator"):
                self.sound_manager.stop_narrator(fade_ms=300)
            if self.bgm_manager:
                self.bgm_manager.update(0.0, scene="menu")

    def handle_click(self, mouse_pos, button=1):
        if button != 1:
            return None

        if self.dialogue_finished:
            return "menu"

        if self.skip_btn_rect.collidepoint(mouse_pos):
            self.skip()
            return "menu"

        self.advance_dialogue()
        if self.dialogue_finished:
            return "menu"
        return None

    def handle_key(self, event):
        if self.dialogue_finished:
            return False

        key = event.key if hasattr(event, "key") else event

        if key in (pygame.K_ESCAPE, pygame.K_s, ord('s'), ord('S')):
            self.skip()
            return True

        if key in (pygame.K_SPACE, pygame.K_RETURN, pygame.K_KP_ENTER):
            self.advance_dialogue()
            return True

        return False

    def update(self, dt, mouse_pos=None):
        if self.dialogue_finished:
            return

        # Check hold-to-skip (holding ESC or 'S')
        try:
            if pygame.key.get_focused():
                pressed = pygame.key.get_pressed()
                esc_down = (pygame.K_ESCAPE < len(pressed) and pressed[pygame.K_ESCAPE])
                s_down = (pygame.K_s < len(pressed) and pressed[pygame.K_s])
                if esc_down or s_down:
                    self.skip_hold_time += dt
                    if self.skip_hold_time >= 0.4:
                        self.skip()
                        return
                else:
                    self.skip_hold_time = 0.0
        except Exception:
            pass

        self.animation_time += dt

        # Frame sequence timer (4 FPS loop across 4 frames)
        self.frame_timer += dt
        if self.frame_timer >= self.frame_duration:
            self.frame_timer -= self.frame_duration
            self.frame_index = (self.frame_index + 1) % 4

        # Update typewriter progress
        cur_entry = self.script[self.current_entry_index]
        full_text = cur_entry["text"]
        self.typewriter_progress += dt
        cur_char_count = min(len(full_text), int(self.typewriter_progress * self.typewriter_speed))

        # Play subtle retro voice phoneme blip on new letters according to speaker (every 2-3 characters)
        self.typewriter_sound_timer += dt
        if cur_char_count > self.last_blip_char:
            played = False
            speaker = cur_entry.get("speaker", "NARRATOR")
            for c_idx in range(self.last_blip_char, cur_char_count):
                char_c = full_text[c_idx]
                if char_c.isalnum() and (c_idx % 2 == 0):
                    if self.typewriter_sound_timer >= 0.040 and not played:
                        if self.sound_manager:
                            if hasattr(self.sound_manager, "play_voice"):
                                self.sound_manager.play_voice(speaker, volume=0.25)
                            else:
                                self.sound_manager.play("typewriter", volume=0.22)
                        self.typewriter_sound_timer = 0.0
                        played = True
            self.last_blip_char = cur_char_count

        # Check skip button hover
        if mouse_pos:
            self.skip_hovered = self.skip_btn_rect.collidepoint(mouse_pos)

        # Update atmospheric particles
        sc_id = cur_entry["scene"]
        for p in self.particles:
            p["x"] += p["vx"]
            p["y"] += p["vy"]
            if sc_id == "scene_1_golden_age":
                # Golden pollen drifting gently right and up
                p["vx"] = 0.5 + math.sin(self.animation_time + p["x"] * 0.05) * 0.3
                p["vy"] = -0.6
                p["color"] = (255, 235, 120)
            elif sc_id == "scene_2_cataclysm":
                # Volcanic embers rising
                p["vx"] = math.sin(self.animation_time * 2.0 + p["y"] * 0.05) * 0.8
                p["vy"] = -1.2
                p["color"] = (255, 110, 30) if random.random() < 0.6 else (180, 60, 220)
            elif sc_id == "scene_3_titans":
                # Swirling elemental embers and snowflakes
                p["vx"] = math.sin(self.animation_time + p["y"] * 0.03) * 1.1
                p["vy"] = -0.5 if p["x"] < 420 else 0.8  # snow falling on right
                p["color"] = (255, 140, 40) if p["x"] < 320 else (180, 230, 255)
            else:
                # Ethereal celestial starlight motes dancing
                p["vx"] = math.sin(self.animation_time * 1.4 + p["y"] * 0.04) * 0.6
                p["vy"] = math.cos(self.animation_time * 1.1 + p["x"] * 0.04) * 0.5
                p["color"] = (160, 255, 190) if p["x"] < 380 else (200, 230, 255)

            # Wrap around screen edges
            if p["x"] < -10:
                p["x"] = SCREEN_WIDTH + 10
            elif p["x"] > SCREEN_WIDTH + 10:
                p["x"] = -10
            if p["y"] < -10:
                p["y"] = SCREEN_HEIGHT + 10
            elif p["y"] > SCREEN_HEIGHT + 10:
                p["y"] = -10

    def render(self, target_surf):
        entry_idx = min(self.current_entry_index, len(self.script) - 1)
        cur_entry = self.script[entry_idx]
        sc_name = cur_entry["scene"]

        # 1. Render Cinematic Parallax Scene Background
        pan_x = math.sin(self.animation_time * 0.45) * 14.0 - 20.0
        pan_y = math.cos(self.animation_time * 0.35) * 6.0 - 15.0

        frames = self.scaled_scenes.get(sc_name)
        if frames:
            cur_frame_surf = frames[self.frame_index % len(frames)]
            target_surf.blit(cur_frame_surf, (int(pan_x), int(pan_y)))
        else:
            target_surf.fill((20, 25, 45))

        # 2. Render Atmospheric Particles
        for p in self.particles:
            col = p.get("color", (255, 230, 120))
            pygame.draw.circle(target_surf, col, (int(p["x"]), int(p["y"])), p["size"])

        # 3. Cinematic Letterboxing (Top and Bottom Black Cinema Bars)
        pygame.draw.rect(target_surf, (10, 10, 14), (0, 0, SCREEN_WIDTH, self.letterbox_h))
        pygame.draw.line(target_surf, (180, 155, 90), (0, self.letterbox_h - 1), (SCREEN_WIDTH, self.letterbox_h - 1), 2)
        pygame.draw.rect(target_surf, (10, 10, 14), (0, SCREEN_HEIGHT - self.letterbox_h, SCREEN_WIDTH, self.letterbox_h))
        pygame.draw.line(target_surf, (180, 155, 90), (0, SCREEN_HEIGHT - self.letterbox_h), (SCREEN_WIDTH, SCREEN_HEIGHT - self.letterbox_h), 2)

        # Header Title in Top Cinema Bar
        title_txt = cur_entry.get("scene_title", "POTARIA PROLOGUE")
        t_surf = self.font_header.render(title_txt, True, (245, 220, 120))
        target_surf.blit(t_surf, (24, (self.letterbox_h - t_surf.get_height()) // 2))

        # Skip Button in Top Cinema Bar
        sb_col = (75, 45, 30) if not self.skip_hovered else (120, 65, 40)
        sb_border = (255, 215, 0) if self.skip_hovered else (180, 140, 80)
        pygame.draw.rect(target_surf, sb_col, self.skip_btn_rect, border_radius=5)
        pygame.draw.rect(target_surf, sb_border, self.skip_btn_rect, 2, border_radius=5)
        skip_txt = self.font_skip.render("SKIP [ESC / S]", True, (255, 240, 180))
        st_x = self.skip_btn_rect.centerx - skip_txt.get_width() // 2
        st_y = self.skip_btn_rect.centery - skip_txt.get_height() // 2
        target_surf.blit(skip_txt, (st_x, st_y))

        # 4. Ornate Dialogue Box at Bottom
        bx, by, bw, bh = self.dialogue_x, self.dialogue_y, self.dialogue_w, self.dialogue_h
        pygame.draw.rect(target_surf, (12, 14, 22, 240), (bx + 3, by + 3, bw, bh), border_radius=12)
        pygame.draw.rect(target_surf, (28, 33, 50, 245), (bx, by, bw, bh), border_radius=12)
        pygame.draw.rect(target_surf, COLOR_GOLD, (bx, by, bw, bh), 2, border_radius=12)
        pygame.draw.rect(target_surf, (75, 90, 125), (bx + 4, by + 4, bw - 8, bh - 8), 1, border_radius=9)

        # Corner Golden Rivet Accents
        for rx, ry in [(bx + 8, by + 8), (bx + bw - 9, by + 8), (bx + 8, by + bh - 9), (bx + bw - 9, by + bh - 9)]:
            pygame.draw.circle(target_surf, (255, 235, 120), (rx, ry), 3)
            pygame.draw.circle(target_surf, (120, 90, 30), (rx, ry), 3, 1)

        # Speaker Nameplate Ribbon / Tab
        speaker_name = cur_entry["speaker"]
        sp_name_surf = self.font_name.render(speaker_name, True, cur_entry.get("name_color", (255, 230, 100)))
        nw = sp_name_surf.get_width() + 28
        nh = 26
        name_rect = pygame.Rect(bx + 20, by - 14, nw, nh)
        pygame.draw.rect(target_surf, (22, 26, 40), name_rect, border_radius=6)
        pygame.draw.rect(target_surf, COLOR_GOLD, name_rect, 2, border_radius=6)
        target_surf.blit(sp_name_surf, (bx + 34, by - 14 + (nh - sp_name_surf.get_height()) // 2))

        # 5. Character Speaker Portrait
        portrait_key = cur_entry.get("portrait", "spud")
        port_surf = self.asset_factory.cutscene_portraits.get(portrait_key)
        if not port_surf:
            if portrait_key == "sol_rho":
                port_surf = self.asset_factory.cutscene_portraits.get("dark_titan_sol_rho")
            elif portrait_key == "dark_titan_sol_rho":
                port_surf = self.asset_factory.cutscene_portraits.get("sol_rho")
        port_box_x = bx + 22
        port_box_y = by + 20
        port_size = 72

        pygame.draw.rect(target_surf, (20, 24, 38), (port_box_x, port_box_y, port_size + 8, port_size + 8), border_radius=8)
        pygame.draw.rect(target_surf, (215, 180, 75), (port_box_x, port_box_y, port_size + 8, port_size + 8), 2, border_radius=8)

        if port_surf:
            bounce_y = int(math.sin(self.animation_time * 2.8) * 1.5)
            scaled_port = pygame.transform.scale(port_surf, (port_size, port_size))
            target_surf.blit(scaled_port, (port_box_x + 4, port_box_y + 4 + bounce_y))

        # 6. Typewriter Dialogue Text with Stable Pre-Wrapped Lines
        full_text = cur_entry["text"]
        revealed_len = len(full_text) if self.dialogue_finished else min(len(full_text), int(self.typewriter_progress * self.typewriter_speed))

        text_x = bx + 120
        text_y = by + 28
        max_text_width = bw - 150
        lines = self._get_wrapped_lines(full_text, max_text_width)

        rem_chars = revealed_len
        for l_idx, line in enumerate(lines):
            if rem_chars <= 0:
                break
            visible_chars = min(len(line), rem_chars)
            line_surf = self.font_text.render(line[:visible_chars], True, (250, 248, 240))
            target_surf.blit(line_surf, (text_x, text_y + l_idx * 24))
            rem_chars -= (len(line) + 1)

        # 7. Animated Continue Prompt Indicator
        is_line_done = (revealed_len >= len(full_text)) or self.dialogue_finished
        prompt_pulse = int(math.sin(self.animation_time * 6.0) * 3)
        prompt_col = (255, 235, 110) if is_line_done else (160, 175, 195)
        prompt_txt = "[SPACE / CLICK] NEXT ▶" if is_line_done else "[SPACE] FAST-FORWARD"
        pr_surf = self.font_prompt.render(prompt_txt, True, prompt_col)
        pr_x = bx + bw - pr_surf.get_width() - 24 + (prompt_pulse if is_line_done else 0)
        pr_y = by + bh - 24
        target_surf.blit(pr_surf, (pr_x, pr_y))


# Export alias for the prologue cutscene engine
PrologueCutscene = CutsceneEngine


