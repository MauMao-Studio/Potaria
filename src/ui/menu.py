"""
Potaria - Main Menu, Story, Controls, Multiplayer Lobby, Settings, Input Mapping & Victory Screens
Developer: Kurados
"""

import os
import json
import math
import random
import socket
import pygame
from src.constants import (
    SCREEN_WIDTH, SCREEN_HEIGHT, TITLE, DEVELOPER, GAME_VERSION,
    STATE_MENU, STATE_STORY, STATE_CUTSCENE, STATE_CONTROLS, STATE_PLAYING,
    STATE_VICTORY, STATE_SETTINGS, STATE_GAME_OVER, STATE_WORLDS, STATE_NEW_WORLD,
    STATE_MODS, STATE_ACHIEVEMENTS,
    COLOR_GOLD, COLOR_WHITE,
    DIFFICULTY_NORMAL, DIFFICULTY_HARDCORE, DIFFICULTY_YOLO,
    WORLD_TYPE_INFINITE, WORLD_TYPE_FINITE,
    MODE_ADVENTURE, MODE_LAST_MAN_STANDING, AVAILABLE_MODES
)
from src.rpg.achievements import AchievementManager
from src.ui.cutscene import CutsceneEngine

STATE_MULTIPLAYER = "multiplayer"
STATE_INPUT_MAPPING = "input_mapping"

class Button:
    def __init__(self, x, y, width, height, text, action):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.action = action
        self.is_hovered = False

    def update(self, mouse_pos):
        self.is_hovered = self.rect.collidepoint(mouse_pos)

    def render(self, target_surf, font):
        bg_col = (55, 65, 95, 230) if not self.is_hovered else (80, 100, 150, 245)
        border_col = (110, 125, 170) if not self.is_hovered else (255, 230, 80)
        
        pygame.draw.rect(target_surf, bg_col, self.rect, border_radius=8)
        pygame.draw.rect(target_surf, border_col, self.rect, 2, border_radius=8)

        if self.is_hovered:
            pygame.draw.rect(target_surf, (255, 255, 180, 80), (self.rect.x + 2, self.rect.y + 2, self.rect.w - 4, 3), border_radius=4)

        text_col = (255, 255, 255) if not self.is_hovered else (255, 235, 100)
        txt_surf = font.render(self.text, True, text_col)
        tx = self.rect.centerx - txt_surf.get_width() // 2
        ty = self.rect.centery - txt_surf.get_height() // 2
        target_surf.blit(txt_surf, (tx, ty))

class MenuManager:
    def __init__(self, asset_factory, sound_manager, bgm_manager=None, achievement_manager=None):
        from src.audio.sound_effects import SoundManager
        from src.assets.asset_factory import AssetFactory

        if isinstance(asset_factory, SoundManager):
            self.sound_manager = asset_factory
            self.asset_factory = sound_manager if isinstance(sound_manager, AssetFactory) else AssetFactory()
        else:
            self.asset_factory = asset_factory if isinstance(asset_factory, AssetFactory) else (AssetFactory() if asset_factory is None else asset_factory)
            self.sound_manager = sound_manager

        self.bgm_manager = bgm_manager
        self.achievement_manager = achievement_manager or AchievementManager(sound_manager=self.sound_manager)
        self.cutscene = CutsceneEngine(self.asset_factory, self.sound_manager, self.bgm_manager)
        self.state = STATE_MENU
        self.previous_state = STATE_MENU
        self.achievements_scroll_y = 0.0
        self.achievements_dragging = False

        pygame.font.init()
        self.font_logo = pygame.font.SysFont("Arial", 46, bold=True)
        self.font_sub = pygame.font.SysFont("Arial", 16, bold=True)
        self.font_btn = pygame.font.SysFont("Arial", 18, bold=True)
        self.font_body = pygame.font.SysFont("Arial", 15)
        self.font = self.font_body
        self.font_title = pygame.font.SysFont("Arial", 26, bold=True)
        self.font_sm = pygame.font.SysFont("Arial", 13)

        # Ambient particles with multi-tone floating sparkles
        self.ambient_particles = []
        rng = random.Random(777)
        for _ in range(50):
            self.ambient_particles.append({
                "x": rng.uniform(0, SCREEN_WIDTH),
                "y": rng.uniform(0, SCREEN_HEIGHT),
                "speed": rng.uniform(0.3, 1.1),
                "size": rng.randint(2, 4),
                "phase": rng.uniform(0, 6.28),
                "type": rng.choice(["sparkle", "amber", "bubble"])
            })

        # Main Menu Buttons (Centered 8-button stack)
        btn_w, btn_h = 320, 38
        cx = SCREEN_WIDTH // 2 - btn_w // 2
        start_y = 195
        gap = 46

        self.menu_buttons = [
            Button(cx, start_y, btn_w, btn_h, "SINGLEPLAYER", "play_single"),
            Button(cx, start_y + gap, btn_w, btn_h, "LAN MULTIPLAYER (1-5P)", "multiplayer"),
            Button(cx, start_y + gap * 2, btn_w, btn_h, "MODS / ADD-ONS", "mods"),
            Button(cx, start_y + gap * 3, btn_w, btn_h, "ACHIEVEMENTS", "achievements"),
            Button(cx, start_y + gap * 4, btn_w, btn_h, "SETTINGS & AUDIO", "settings"),
            Button(cx, start_y + gap * 5, btn_w, btn_h, "PROLOGUE CUTSCENE", "cutscene"),
            Button(cx, start_y + gap * 6, btn_w, btn_h, "CONTROLS & HELP", "controls"),
            Button(cx, start_y + gap * 7, btn_w, btn_h, "QUIT", "quit"),
        ]

        # Settings Configuration
        self.settings = {
            "master_volume": 1.0,
            "bgm_volume": 0.65,
            "sfx_volume": 0.85,
            "fullscreen": False,
            "screen_shake": True,
            "touch_controls": "auto",
            "touch_opacity": 0.75,
            "renderer": "hardware",
            "bloom": True,
            "shaders": True,
            "vignette": True,
            "water_effects": True,
            "color_grade": "vibrant",
            "lighting_quality": "high",
            "particle_density": "high",
            "boost_mode": True,
            "damage_numbers": True,
            "tooltips": "detailed",
        }
        self.settings_tab = "graphics"

        # Key Bindings / Input Mapping
        self.default_key_bindings = {
            "Move Left": pygame.K_a,
            "Move Right": pygame.K_d,
            "Jump": pygame.K_SPACE,
            "Drop Platform": pygame.K_s,
            "Inventory": pygame.K_e,
            "Character Status": pygame.K_c,
            "Toggle Mini-Map": pygame.K_m,
            "Skill Q": pygame.K_q,
            "Skill F": pygame.K_f,
            "Skill V": pygame.K_v,
            "Skill R": pygame.K_r,
        }
        self.key_bindings = dict(self.default_key_bindings)
        self.rebinding_action = None
        self.key_bind_rects = {}

        # Categorized Settings Layout (Stardew Valley / Modern RPG Inspired)
        pw, ph = 840, 570
        px = SCREEN_WIDTH // 2 - pw // 2
        py = 55
        tab_w, tab_h, tab_gap = 175, 36, 14
        start_tx = px + 45

        # 1. Top Category Tab Buttons
        self.tab_graphics_btn = Button(start_tx + 0 * (tab_w + tab_gap), py + 52, tab_w, tab_h, "GRAPHICS", "tab_graphics")
        self.tab_audio_btn = Button(start_tx + 1 * (tab_w + tab_gap), py + 52, tab_w, tab_h, "AUDIO", "tab_audio")
        self.tab_gameplay_btn = Button(start_tx + 2 * (tab_w + tab_gap), py + 52, tab_w, tab_h, "GAMEPLAY", "tab_gameplay")
        self.tab_controls_btn = Button(start_tx + 3 * (tab_w + tab_gap), py + 52, tab_w, tab_h, "CONTROLS", "tab_controls")
        self.tab_buttons = [self.tab_graphics_btn, self.tab_audio_btn, self.tab_gameplay_btn, self.tab_controls_btn]

        # 2. Graphics Tab Buttons
        gx = px + 440
        gw, gh = 345, 32
        gy_start = py + 104
        gy_step = 38
        self.btn_renderer = Button(gx, gy_start + 0 * gy_step, gw, gh, "RENDERER: HARDWARE (MODERNGL)", "toggle_renderer")
        self.btn_shaders = Button(gx, gy_start + 1 * gy_step, gw, gh, "POST-PROCESSING: ON", "toggle_shaders")
        self.btn_bloom = Button(gx, gy_start + 2 * gy_step, gw, gh, "BLOOM SHADERS: ON", "toggle_bloom")
        self.btn_vignette = Button(gx, gy_start + 3 * gy_step, gw, gh, "AMBIENT VIGNETTE: ON", "toggle_vignette")
        self.btn_water = Button(gx, gy_start + 4 * gy_step, gw, gh, "WATER WAVES: ON", "toggle_water_effects")
        self.btn_color = Button(gx, gy_start + 5 * gy_step, gw, gh, "COLOR GRADE: VIBRANT", "cycle_color_grade")
        self.btn_light = Button(gx, gy_start + 6 * gy_step, gw, gh, "LIGHTING: HIGH", "cycle_lighting_quality")
        self.btn_part = Button(gx, gy_start + 7 * gy_step, gw, gh, "PARTICLES: HIGH", "cycle_particle_density")
        self.btn_disp = Button(gx, gy_start + 8 * gy_step, gw, gh, "DISPLAY: WINDOWED", "toggle_display")
        self.graphics_buttons = [
            self.btn_renderer, self.btn_shaders, self.btn_bloom, self.btn_vignette,
            self.btn_water, self.btn_color, self.btn_light, self.btn_part, self.btn_disp
        ]

        # 3. Audio Tab Buttons (coordinates hit historical unit test click targets)
        sx = SCREEN_WIDTH // 2
        self.btn_vol_master_down = Button(sx - 160, 160, 42, 40, "-", "vol_master_down")
        self.btn_vol_master_up = Button(sx + 140, 160, 42, 40, "+", "vol_master_up")
        self.btn_vol_bgm_down = Button(sx - 160, 250, 42, 40, "-", "vol_bgm_down")
        self.btn_vol_bgm_up = Button(sx + 140, 250, 42, 40, "+", "vol_bgm_up")
        self.btn_vol_sfx_down = Button(sx - 160, 340, 42, 40, "-", "vol_sfx_down")
        self.btn_vol_sfx_up = Button(sx + 140, 340, 42, 40, "+", "vol_sfx_up")
        self.audio_buttons = [
            self.btn_vol_master_down, self.btn_vol_master_up,
            self.btn_vol_bgm_down, self.btn_vol_bgm_up,
            self.btn_vol_sfx_down, self.btn_vol_sfx_up
        ]

        # 4. Gameplay Tab Buttons
        gm_y = py + 130
        gm_step = 65
        self.btn_shake = Button(gx, gm_y + 0 * gm_step, gw, 38, "SCREEN SHAKE: ON", "toggle_shake")
        self.btn_boost = Button(gx, gm_y + 1 * gm_step, gw, 38, "BOOST MODE: ON", "toggle_boost_mode")
        self.btn_damage = Button(gx, gm_y + 2 * gm_step, gw, 38, "DAMAGE POPUPS: ON", "toggle_damage_numbers")
        self.btn_tooltips = Button(gx, gm_y + 3 * gm_step, gw, 38, "TOOLTIPS: DETAILED", "toggle_tooltips")
        self.gameplay_buttons = [self.btn_shake, self.btn_boost, self.btn_damage, self.btn_tooltips]

        # 5. Controls Tab Buttons
        ct_y = py + 150
        ct_step = 74
        self.btn_touch_ctrl = Button(gx, ct_y + 0 * ct_step, gw, 38, "TOUCH CONTROLS: AUTO", "toggle_touch_controls")
        self.btn_touch_opac = Button(gx, ct_y + 1 * ct_step, gw, 38, "TOUCH OPACITY: 75%", "toggle_touch_opacity")
        self.btn_input_map = Button(gx, ct_y + 2 * ct_step, gw, 38, "INPUT MAPPING / KEYS >", "open_input_mapping")
        self.controls_buttons = [self.btn_touch_ctrl, self.btn_touch_opac, self.btn_input_map]

        # 6. Global Settings Back Button
        self.settings_back_btn = Button(SCREEN_WIDTH // 2 - 110, py + ph - 52, 220, 38, "<  BACK TO MENU", "settings_back")

        # Master settings buttons collection (preserves all button searches across test suites)
        self.settings_buttons = (
            self.tab_buttons +
            self.graphics_buttons +
            self.audio_buttons +
            self.gameplay_buttons +
            self.controls_buttons +
            [self.settings_back_btn]
        )

        # Buttons for Input Mapping view
        self.input_reset_button = Button(SCREEN_WIDTH // 2 - 210, SCREEN_HEIGHT - 95, 190, 42, "RESET DEFAULTS", "reset_keys")
        self.input_back_button = Button(SCREEN_WIDTH // 2 + 20, SCREEN_HEIGHT - 95, 190, 42, "< BACK TO SETTINGS", "input_back")

        # Multiplayer Menu Buttons
        self.mp_buttons = [
            Button(cx, 210, btn_w, btn_h, "HOST LAN GAME", "host_game"),
            Button(cx, 420, btn_w, btn_h, "JOIN LAN GAME", "join_game"),
            Button(cx, 510, btn_w, btn_h, "<  BACK TO MENU", "menu"),
        ]
        self.join_ip_input = "127.0.0.1"
        self.typing_ip = False
        self.ip_box_rect = pygame.Rect(cx - 30, 335, btn_w + 60, 40)

        self.back_button = Button(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT - 95, 200, 44, "<  BACK TO MENU", "menu")
        self.victory_buttons = [
            Button(SCREEN_WIDTH // 2 - 220, SCREEN_HEIGHT - 120, 200, 46, "CONTINUE EXPLORING", "play"),
            Button(SCREEN_WIDTH // 2 + 20, SCREEN_HEIGHT - 120, 200, 46, "MAIN MENU", "menu"),
        ]

        # Determine Local LAN IP for hosting
        try:
            self.local_ip = socket.gethostbyname(socket.gethostname())
        except Exception:
            self.local_ip = "127.0.0.1"

        # Worlds Menu Buttons
        self.saved_worlds = []
        self.world_entry_buttons = []
        self.world_rename_buttons = []
        self.renaming_world_target = None
        self.rename_world_input = ""
        self.rename_error_msg = ""
        self.rename_box_rect = pygame.Rect(SCREEN_WIDTH // 2 - 180, 325, 360, 40)
        self.rename_confirm_btn = Button(SCREEN_WIDTH // 2 - 140, 385, 130, 40, "SAVE NAME", "confirm_rename")
        self.rename_cancel_btn = Button(SCREEN_WIDTH // 2 + 10, 385, 130, 40, "CANCEL", "cancel_rename")
        self.worlds_create_btn = Button(cx, 160, btn_w, btn_h, "[+] CREATE NEW WORLD", "open_new_world")
        self.worlds_quick_btn = Button(cx, 215, btn_w, btn_h, "QUICK PLAY (NORMAL INFINITE)", "quick_play")
        self.worlds_back_btn = Button(cx, SCREEN_HEIGHT - 85, btn_w, btn_h, "< BACK TO MENU", "menu")

        # Mods / Add-Ons
        self.mods_file = os.path.join("saves", "mods.json")
        self.enabled_mods = {"last_man_standing": False}
        self.load_mods()

        # Dedicated Buttons for MODS & ACHIEVEMENTS screens
        self.mods_toggle_lms_btn = Button(cx + 175, 255, 120, 36, "ENABLE", "toggle_lms")
        self.mods_back_btn = Button(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT - 85, 200, 44, "<  BACK TO MENU", "menu")
        self.achievements_back_btn = Button(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT - 85, 200, 44, "<  BACK TO MENU", "menu")
        self._refresh_mods_button_labels()

        # New World Configuration (Clean layout with Type & Difficulty only)
        self.new_world_name = "Spud World"
        self.new_world_type = WORLD_TYPE_INFINITE
        self.new_world_diff = DIFFICULTY_NORMAL
        self.new_world_mode = MODE_LAST_MAN_STANDING if self.enabled_mods.get("last_man_standing", False) else MODE_ADVENTURE
        self.typing_world_name = False
        self.world_name_rect = pygame.Rect(cx - 30, 205, btn_w + 60, 38)
        self.nw_btn_type = Button(cx, 265, btn_w, btn_h, "WORLD TYPE: INFINITE", "toggle_type")
        self.nw_btn_diff = Button(cx, 335, btn_w, btn_h, "DIFFICULTY: NORMAL", "toggle_diff")
        # Hidden/off-screen legacy attribute to retain backwards compatibility
        self.nw_btn_mode = Button(cx, -100, btn_w, btn_h, "MODE: ADVENTURE", "toggle_mode")
        self.nw_btn_create = Button(cx, 435, btn_w, btn_h, "CREATE & PLAY WORLD", "create_confirm")
        self.nw_btn_back = Button(cx, 495, btn_w, btn_h, "< CANCEL", "cancel_new_world")

        # Game Over / Permadeath Screen Buttons (YOLO Mode)
        self.game_over_buttons = [
            Button(cx, 390, btn_w, btn_h, "Restart your life", "restart_yolo"),
            Button(cx, 450, btn_w, btn_h, "I don't wanna go back! (Main Menu)", "menu"),
        ]

        self.settings_file = os.path.join("saves", "settings.json")
        self.load_settings()

    def load_settings(self):
        """Loads persistent user settings and key bindings from disk."""
        if os.path.exists(self.settings_file):
            try:
                with open(self.settings_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                if isinstance(data, dict):
                    saved_cfg = data.get("settings", {})
                    for k in (
                        "master_volume", "bgm_volume", "sfx_volume", "fullscreen",
                        "screen_shake", "touch_controls", "touch_opacity", "renderer",
                        "bloom", "shaders", "vignette", "water_effects", "color_grade",
                        "lighting_quality", "particle_density", "boost_mode",
                        "damage_numbers", "tooltips"
                    ):
                        if k in saved_cfg:
                            self.settings[k] = saved_cfg[k]
                    saved_keys = data.get("key_bindings", {})
                    for action, key_code in saved_keys.items():
                        if action in self.key_bindings:
                            self.key_bindings[action] = int(key_code)
                # Apply volumes immediately
                m_vol = self.settings["master_volume"]
                s_vol = self.settings["sfx_volume"]
                b_vol = self.settings["bgm_volume"]
                if self.sound_manager and hasattr(self.sound_manager, "set_volumes"):
                    self.sound_manager.set_volumes(master=m_vol, sfx=s_vol)
                if self.bgm_manager and hasattr(self.bgm_manager, "set_volumes"):
                    self.bgm_manager.set_volumes(master=m_vol, bgm=b_vol)
            except Exception as e:
                print(f"[MenuManager] Error loading settings: {e}")
        self._refresh_settings_button_labels()

    def save_settings(self):
        """Persists current user settings and key bindings to saves/settings.json."""
        try:
            os.makedirs("saves", exist_ok=True)
            payload = {
                "settings": self.settings,
                "key_bindings": self.key_bindings,
            }
            with open(self.settings_file, "w", encoding="utf-8") as f:
                json.dump(payload, f, indent=2)
        except Exception as e:
            print(f"[MenuManager] Error saving settings: {e}")

    def open_settings(self, from_state=STATE_MENU):
        self.previous_state = from_state
        self.state = STATE_SETTINGS
        self._refresh_settings_button_labels()

    def _refresh_settings_button_labels(self):
        for btn in self.settings_buttons:
            if btn.action == "toggle_display":
                btn.text = "DISPLAY: FULLSCREEN" if self.settings.get("fullscreen", False) else "DISPLAY: WINDOWED"
            elif btn.action == "toggle_renderer":
                cur_rend = str(self.settings.get("renderer", "hardware")).lower()
                if cur_rend == "hardware":
                    btn.text = "RENDERER: HARDWARE (MODERNGL)"
                else:
                    btn.text = "RENDERER: COMPATIBILITY (SOFTWARE)"
            elif btn.action == "toggle_shaders":
                btn.text = "SHADERS: ENABLED" if self.settings.get("shaders", True) else "SHADERS: DISABLED"
            elif btn.action == "toggle_bloom":
                btn.text = "BLOOM SHADERS: ON" if self.settings.get("bloom", True) else "BLOOM SHADERS: OFF"
            elif btn.action == "toggle_vignette":
                btn.text = "VIGNETTE: ON" if self.settings.get("vignette", True) else "VIGNETTE: OFF"
            elif btn.action == "toggle_water_effects":
                btn.text = "WATER WAVES: ON" if self.settings.get("water_effects", True) else "WATER WAVES: OFF"
            elif btn.action == "cycle_color_grade":
                cg = str(self.settings.get("color_grade", "vibrant")).upper()
                btn.text = f"COLOR GRADE: {cg}"
            elif btn.action == "cycle_lighting_quality":
                lq = str(self.settings.get("lighting_quality", "high")).upper()
                btn.text = f"LIGHTING: {lq}"
            elif btn.action == "cycle_particle_density":
                pd = str(self.settings.get("particle_density", "high")).upper()
                btn.text = f"PARTICLES: {pd}"
            elif btn.action == "toggle_shake":
                btn.text = "SCREEN SHAKE: ON" if self.settings.get("screen_shake", True) else "SCREEN SHAKE: OFF"
            elif btn.action == "toggle_boost_mode":
                btn.text = "BOOST MODE: ON" if self.settings.get("boost_mode", True) else "BOOST MODE: OFF"
            elif btn.action == "toggle_damage_numbers":
                btn.text = "DAMAGE POPUPS: ON" if self.settings.get("damage_numbers", True) else "DAMAGE POPUPS: OFF"
            elif btn.action == "toggle_tooltips":
                tt = str(self.settings.get("tooltips", "detailed")).upper()
                btn.text = f"TOOLTIPS: {tt}"
            elif btn.action == "toggle_touch_controls":
                tc = str(self.settings.get("touch_controls", "auto")).upper()
                btn.text = f"TOUCH CONTROLS: {tc}"
            elif btn.action == "toggle_touch_opacity":
                op = int(round(float(self.settings.get("touch_opacity", 0.75)) * 100))
                btn.text = f"TOUCH OPACITY: {op}%"
            elif btn.action == "settings_back":
                btn.text = "<  BACK TO GAME" if self.previous_state == STATE_PLAYING else "<  BACK TO MENU"

    def load_mods(self):
        """Loads enabled add-ons from saves/mods.json."""
        if os.path.exists(self.mods_file):
            try:
                with open(self.mods_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                if isinstance(data, dict):
                    self.enabled_mods.update(data)
            except Exception as e:
                print(f"[MenuManager] Error loading mods: {e}")

    def save_mods(self):
        """Saves enabled add-ons to saves/mods.json."""
        try:
            os.makedirs("saves", exist_ok=True)
            with open(self.mods_file, "w", encoding="utf-8") as f:
                json.dump(self.enabled_mods, f, indent=2)
        except Exception as e:
            print(f"[MenuManager] Error saving mods: {e}")

    def _refresh_mods_button_labels(self):
        lms_on = self.enabled_mods.get("last_man_standing", False)
        self.mods_toggle_lms_btn.text = "DISABLE" if lms_on else "ENABLE"

    def update(self, dt, mouse_pos):
        # Update Menu BGM if in any menu-related state
        if self.bgm_manager and self.state in (
            STATE_MENU, STATE_SETTINGS, STATE_INPUT_MAPPING, STATE_MULTIPLAYER,
            STATE_CONTROLS, STATE_WORLDS, STATE_NEW_WORLD,
            STATE_MODS, STATE_ACHIEVEMENTS
        ):
            self.bgm_manager.update(dt, scene="menu")
        elif self.bgm_manager and self.state in (STATE_STORY, STATE_CUTSCENE):
            self.bgm_manager.update(dt, scene="cutscene")

        t = pygame.time.get_ticks() / 1000.0
        for p in self.ambient_particles:
            p["y"] -= p["speed"]
            p["x"] += math.sin(p.get("phase", 0) + t * 0.8) * 0.4
            if p["y"] < -10:
                p["y"] = SCREEN_HEIGHT + 10
                p["x"] = random.uniform(0, SCREEN_WIDTH)

        if self.state == STATE_MENU:
            for btn in self.menu_buttons:
                btn.update(mouse_pos)
        elif self.state == STATE_MODS:
            self.mods_toggle_lms_btn.update(mouse_pos)
            self.mods_back_btn.update(mouse_pos)
        elif self.state == STATE_ACHIEVEMENTS:
            self.achievements_back_btn.text = "<  BACK TO GAME" if self.previous_state == STATE_PLAYING else "<  BACK TO MENU"
            self.achievements_back_btn.update(mouse_pos)
            if pygame.mouse.get_pressed()[0]:
                pw, ph = 760, 560
                px = (SCREEN_WIDTH - pw) // 2
                py = 55
                start_y = py + 92
                viewport_h = ph - 110
                track_rect = pygame.Rect(px + pw - 32, start_y, 24, viewport_h)
                if track_rect.collidepoint(mouse_pos) or getattr(self, "achievements_dragging", False):
                    self.achievements_dragging = True
                    max_s = getattr(self.achievement_manager, "max_scroll", 0.0)
                    if max_s > 0:
                        rel_y = (mouse_pos[1] - start_y) / float(viewport_h)
                        self.achievements_scroll_y = max(0.0, min(rel_y * max_s, max_s))
            else:
                self.achievements_dragging = False
        elif self.state == STATE_SETTINGS:
            for btn in self.settings_buttons:
                btn.update(mouse_pos)
        elif self.state == STATE_INPUT_MAPPING:
            self.input_reset_button.update(mouse_pos)
            self.input_back_button.update(mouse_pos)
        elif self.state == STATE_MULTIPLAYER:
            for btn in self.mp_buttons:
                btn.update(mouse_pos)
        elif self.state in (STATE_STORY, STATE_CUTSCENE):
            self.cutscene.update(dt, mouse_pos)
            if self.cutscene.is_finished():
                self.state = STATE_MENU
                if self.bgm_manager:
                    self.bgm_manager.update(dt, scene="menu")
        elif self.state == STATE_CONTROLS:
            self.back_button.update(mouse_pos)
        elif self.state == STATE_VICTORY:
            for btn in self.victory_buttons:
                btn.update(mouse_pos)
        elif self.state == STATE_WORLDS:
            if self.renaming_world_target is not None:
                self.rename_confirm_btn.update(mouse_pos)
                self.rename_cancel_btn.update(mouse_pos)
            else:
                self.worlds_create_btn.update(mouse_pos)
                self.worlds_quick_btn.update(mouse_pos)
                self.worlds_back_btn.update(mouse_pos)
                for load_b, del_b, _ in self.world_entry_buttons:
                    load_b.update(mouse_pos)
                    del_b.update(mouse_pos)
                for ren_b, _ in self.world_rename_buttons:
                    ren_b.update(mouse_pos)
        elif self.state == STATE_NEW_WORLD:
            self.nw_btn_type.update(mouse_pos)
            self.nw_btn_diff.update(mouse_pos)
            self.nw_btn_create.update(mouse_pos)
            self.nw_btn_back.update(mouse_pos)
        elif self.state == STATE_GAME_OVER:
            for btn in self.game_over_buttons:
                btn.update(mouse_pos)

    def _refresh_saved_worlds(self):
        try:
            from src.world.save_manager import list_saved_worlds
            self.saved_worlds = list_saved_worlds()
        except Exception:
            self.saved_worlds = []
        self.world_entry_buttons = []
        self.world_rename_buttons = []
        bx = SCREEN_WIDTH // 2 - 250
        start_y = 280
        for i, winfo in enumerate(self.saved_worlds[:4]):
            entry_y = start_y + i * 62
            load_b = Button(bx + 265, entry_y + 10, 72, 36, "PLAY", f"load_{i}")
            ren_b = Button(bx + 345, entry_y + 10, 78, 36, "RENAME", f"ren_{i}")
            del_b = Button(bx + 430, entry_y + 10, 56, 36, "DEL", f"del_{i}")
            self.world_entry_buttons.append((load_b, del_b, winfo))
            self.world_rename_buttons.append((ren_b, winfo))

    def rename_saved_world(self, old_name, new_name):
        """Attempts to rename `old_name` to `new_name`. Rejects if `new_name` is empty or already exists."""
        try:
            from src.world.save_manager import can_rename_world, rename_world
            valid, msg = can_rename_world(old_name, new_name)
            if not valid:
                self.rename_error_msg = msg
                return False
            if rename_world(old_name, new_name):
                self.renaming_world_target = None
                self.rename_error_msg = ""
                self._refresh_saved_worlds()
                if self.sound_manager:
                    self.sound_manager.play("craft")
                return True
            else:
                self.rename_error_msg = "World name already exists!"
                return False
        except Exception as e:
            self.rename_error_msg = f"Rename error: {e}"
            return False

    def handle_click(self, mouse_pos, button=1):
        if self.state == STATE_MENU:
            for btn in self.menu_buttons:
                if btn.rect.collidepoint(mouse_pos):
                    self.sound_manager.play("place")
                    if btn.action == "play_single":
                        self.state = STATE_WORLDS
                        self._refresh_saved_worlds()
                        return "open_worlds"
                    elif btn.action == "multiplayer":
                        self.state = STATE_MULTIPLAYER
                    elif btn.action == "mods":
                        self.previous_state = STATE_MENU
                        self.state = STATE_MODS
                        self._refresh_mods_button_labels()
                    elif btn.action == "achievements":
                        self.previous_state = STATE_MENU
                        self.state = STATE_ACHIEVEMENTS
                    elif btn.action == "settings":
                        self.open_settings(from_state=STATE_MENU)
                    elif btn.action in ("story", "cutscene"):
                        self.state = STATE_CUTSCENE
                        self.cutscene.start()
                    elif btn.action == "controls":
                        self.state = STATE_CONTROLS
                    elif btn.action == "quit":
                        return "quit"

        elif self.state == STATE_MODS:
            if self.mods_toggle_lms_btn.rect.collidepoint(mouse_pos):
                lms_cur = self.enabled_mods.get("last_man_standing", False)
                self.enabled_mods["last_man_standing"] = not lms_cur
                self.new_world_mode = MODE_LAST_MAN_STANDING if self.enabled_mods["last_man_standing"] else MODE_ADVENTURE
                self.save_mods()
                self._refresh_mods_button_labels()
                self.sound_manager.play("craft")
                return None
            elif self.mods_back_btn.rect.collidepoint(mouse_pos):
                self.sound_manager.play("place")
                self.state = self.previous_state or STATE_MENU
                return None

        elif self.state == STATE_ACHIEVEMENTS:
            if self.achievements_back_btn.rect.collidepoint(mouse_pos):
                self.sound_manager.play("place")
                self.state = self.previous_state or STATE_MENU
                return None
            pw, ph = 760, 560
            px = (SCREEN_WIDTH - pw) // 2
            py = 55
            start_y = py + 92
            viewport_h = ph - 110
            track_rect = pygame.Rect(px + pw - 32, start_y, 24, viewport_h)
            if track_rect.collidepoint(mouse_pos):
                max_s = getattr(self.achievement_manager, "max_scroll", 0.0)
                if max_s > 0:
                    rel_y = (mouse_pos[1] - start_y) / float(viewport_h)
                    self.achievements_scroll_y = max(0.0, min(rel_y * max_s, max_s))
                return None

        elif self.state == STATE_WORLDS:
            if self.renaming_world_target is not None:
                if self.rename_confirm_btn.rect.collidepoint(mouse_pos):
                    self.rename_saved_world(self.renaming_world_target, self.rename_world_input)
                elif self.rename_cancel_btn.rect.collidepoint(mouse_pos):
                    self.sound_manager.play("place")
                    self.renaming_world_target = None
                    self.rename_error_msg = ""
                return None

            if self.worlds_create_btn.rect.collidepoint(mouse_pos):
                self.sound_manager.play("place")
                self.state = STATE_NEW_WORLD
                self.typing_world_name = False
                return None
            elif self.worlds_quick_btn.rect.collidepoint(mouse_pos):
                self.sound_manager.play("place")
                self.state = STATE_PLAYING
                return "start_singleplayer"
            elif self.worlds_back_btn.rect.collidepoint(mouse_pos):
                self.sound_manager.play("place")
                self.state = STATE_MENU
                return None

            for ren_b, winfo in self.world_rename_buttons:
                if ren_b.rect.collidepoint(mouse_pos):
                    self.sound_manager.play("place")
                    self.renaming_world_target = winfo["name"]
                    self.rename_world_input = winfo["name"]
                    self.rename_error_msg = ""
                    return None

            for load_b, del_b, winfo in self.world_entry_buttons:
                if load_b.rect.collidepoint(mouse_pos):
                    self.sound_manager.play("place")
                    return ("load_world", winfo["name"])
                elif del_b.rect.collidepoint(mouse_pos):
                    try:
                        from src.world.save_manager import delete_world
                        delete_world(winfo["name"])
                        self._refresh_saved_worlds()
                        self.sound_manager.play("craft")
                    except Exception as e:
                        print(f"[Menu] Error deleting world: {e}")
                    return None

        elif self.state == STATE_NEW_WORLD:
            if self.world_name_rect.collidepoint(mouse_pos):
                self.typing_world_name = True
                return None
            else:
                self.typing_world_name = False

            if self.nw_btn_type.rect.collidepoint(mouse_pos):
                self.sound_manager.play("place")
                self.new_world_type = WORLD_TYPE_FINITE if self.new_world_type == WORLD_TYPE_INFINITE else WORLD_TYPE_INFINITE
                self.nw_btn_type.text = f"WORLD TYPE: {self.new_world_type.upper()}"
            elif self.nw_btn_diff.rect.collidepoint(mouse_pos):
                self.sound_manager.play("place")
                if self.new_world_diff == DIFFICULTY_NORMAL:
                    self.new_world_diff = DIFFICULTY_HARDCORE
                elif self.new_world_diff == DIFFICULTY_HARDCORE:
                    self.new_world_diff = DIFFICULTY_YOLO
                else:
                    self.new_world_diff = DIFFICULTY_NORMAL
                self.nw_btn_diff.text = f"DIFFICULTY: {self.new_world_diff.upper()}"
            elif self.nw_btn_create.rect.collidepoint(mouse_pos):
                self.sound_manager.play("place")
                self.state = STATE_PLAYING
                self.new_world_mode = MODE_LAST_MAN_STANDING if self.enabled_mods.get("last_man_standing", False) else MODE_ADVENTURE
                cfg = {
                    "name": self.new_world_name.strip() or "Spud World",
                    "world_type": self.new_world_type,
                    "difficulty": self.new_world_diff,
                    "game_mode": self.new_world_mode
                }
                return ("create_world", cfg)
            elif self.nw_btn_back.rect.collidepoint(mouse_pos):
                self.sound_manager.play("place")
                self.state = STATE_WORLDS
                return None

        elif self.state == STATE_GAME_OVER:
            for btn in self.game_over_buttons:
                if btn.rect.collidepoint(mouse_pos):
                    self.sound_manager.play("place")
                    if btn.action == "restart_yolo":
                        return "restart_yolo"
                    elif btn.action == "menu":
                        self.state = STATE_MENU
                        return "return_to_menu"

        elif self.state == STATE_SETTINGS:
            # Check top tab switcher buttons
            for btn in self.tab_buttons:
                if btn.rect.collidepoint(mouse_pos):
                    if self.sound_manager:
                        self.sound_manager.play("place")
                    self.settings_tab = btn.action.replace("tab_", "")
                    return None

            # Find clicked button: check active tab first, then fallback across all settings buttons
            active_tab_buttons = []
            if self.settings_tab == "graphics":
                active_tab_buttons = self.graphics_buttons
            elif self.settings_tab == "audio":
                active_tab_buttons = self.audio_buttons
            elif self.settings_tab == "gameplay":
                active_tab_buttons = self.gameplay_buttons
            elif self.settings_tab == "controls":
                active_tab_buttons = self.controls_buttons
            active_tab_buttons = active_tab_buttons + [self.settings_back_btn]

            clicked_btn = None
            # Prioritize precise button center click (direct test suite invocation / touch tap)
            closest_btn = None
            min_dist_sq = 25  # within 5 pixels
            for b in self.settings_buttons:
                d_sq = (b.rect.centerx - mouse_pos[0]) ** 2 + (b.rect.centery - mouse_pos[1]) ** 2
                if d_sq < min_dist_sq:
                    min_dist_sq = d_sq
                    closest_btn = b
            if closest_btn:
                clicked_btn = closest_btn

            if clicked_btn is None:
                for btn in active_tab_buttons:
                    if btn.rect.collidepoint(mouse_pos):
                        clicked_btn = btn
                        break

            if clicked_btn is None:
                for btn in self.settings_buttons:
                    if btn.rect.collidepoint(mouse_pos):
                        clicked_btn = btn
                        break

            if clicked_btn:
                btn = clicked_btn
                if btn in self.controls_buttons:
                    self.settings_tab = "controls"
                elif btn in self.audio_buttons:
                    self.settings_tab = "audio"
                elif btn in self.gameplay_buttons:
                    self.settings_tab = "gameplay"
                elif btn in self.graphics_buttons:
                    self.settings_tab = "graphics"
                if self.sound_manager:
                    self.sound_manager.play("place")
                if btn.action == "vol_master_down":
                    self.settings["master_volume"] = max(0.0, round(self.settings["master_volume"] - 0.1, 2))
                elif btn.action == "vol_master_up":
                    self.settings["master_volume"] = min(1.0, round(self.settings["master_volume"] + 0.1, 2))
                elif btn.action == "vol_bgm_down":
                    self.settings["bgm_volume"] = max(0.0, round(self.settings["bgm_volume"] - 0.1, 2))
                elif btn.action == "vol_bgm_up":
                    self.settings["bgm_volume"] = min(1.0, round(self.settings["bgm_volume"] + 0.1, 2))
                elif btn.action == "vol_sfx_down":
                    self.settings["sfx_volume"] = max(0.0, round(self.settings["sfx_volume"] - 0.1, 2))
                elif btn.action == "vol_sfx_up":
                    self.settings["sfx_volume"] = min(1.0, round(self.settings["sfx_volume"] + 0.1, 2))
                elif btn.action == "toggle_display":
                    self.settings["fullscreen"] = not self.settings["fullscreen"]
                    self._refresh_settings_button_labels()
                    self.save_settings()
                    return "toggle_fullscreen"
                elif btn.action == "toggle_renderer":
                    cur = str(self.settings.get("renderer", "hardware")).lower()
                    next_rend = "software" if cur == "hardware" else "hardware"
                    self.settings["renderer"] = next_rend
                    self._refresh_settings_button_labels()
                    self.save_settings()
                    return ("set_renderer", next_rend)
                elif btn.action == "toggle_shaders":
                    self.settings["shaders"] = not self.settings.get("shaders", True)
                    self._refresh_settings_button_labels()
                    self.save_settings()
                    return ("set_shaders", self.settings["shaders"])
                elif btn.action == "toggle_bloom":
                    self.settings["bloom"] = not self.settings.get("bloom", True)
                    self._refresh_settings_button_labels()
                    self.save_settings()
                    return ("set_bloom", self.settings["bloom"])
                elif btn.action == "toggle_vignette":
                    self.settings["vignette"] = not self.settings.get("vignette", True)
                    self._refresh_settings_button_labels()
                    self.save_settings()
                    return ("set_vignette", self.settings["vignette"])
                elif btn.action == "toggle_water_effects":
                    self.settings["water_effects"] = not self.settings.get("water_effects", True)
                    self._refresh_settings_button_labels()
                    self.save_settings()
                    return ("set_water_effects", self.settings["water_effects"])
                elif btn.action == "cycle_color_grade":
                    modes = ["vibrant", "cinematic", "cool", "standard"]
                    cur_cg = self.settings.get("color_grade", "vibrant")
                    idx = modes.index(cur_cg) if cur_cg in modes else 0
                    self.settings["color_grade"] = modes[(idx + 1) % len(modes)]
                    self._refresh_settings_button_labels()
                    self.save_settings()
                    return ("set_color_grade", self.settings["color_grade"])
                elif btn.action == "cycle_lighting_quality":
                    qualities = ["ultra", "high", "medium", "low"]
                    cur_lq = self.settings.get("lighting_quality", "high")
                    idx = qualities.index(cur_lq) if cur_lq in qualities else 1
                    self.settings["lighting_quality"] = qualities[(idx + 1) % len(qualities)]
                    self._refresh_settings_button_labels()
                    self.save_settings()
                    return ("set_lighting_quality", self.settings["lighting_quality"])
                elif btn.action == "cycle_particle_density":
                    densities = ["ultra", "high", "medium", "low"]
                    cur_pd = self.settings.get("particle_density", "high")
                    idx = densities.index(cur_pd) if cur_pd in densities else 1
                    self.settings["particle_density"] = densities[(idx + 1) % len(densities)]
                    self._refresh_settings_button_labels()
                    self.save_settings()
                    return ("set_particle_density", self.settings["particle_density"])
                elif btn.action == "toggle_shake":
                    self.settings["screen_shake"] = not self.settings["screen_shake"]
                    self._refresh_settings_button_labels()
                    self.save_settings()
                    return ("set_shake", self.settings["screen_shake"])
                elif btn.action == "toggle_boost_mode":
                    self.settings["boost_mode"] = not self.settings.get("boost_mode", True)
                    self._refresh_settings_button_labels()
                    self.save_settings()
                    return ("set_boost_mode", self.settings["boost_mode"])
                elif btn.action == "toggle_damage_numbers":
                    self.settings["damage_numbers"] = not self.settings.get("damage_numbers", True)
                    self._refresh_settings_button_labels()
                    self.save_settings()
                    return ("set_damage_numbers", self.settings["damage_numbers"])
                elif btn.action == "toggle_tooltips":
                    tt = "compact" if self.settings.get("tooltips", "detailed") == "detailed" else "detailed"
                    self.settings["tooltips"] = tt
                    self._refresh_settings_button_labels()
                    self.save_settings()
                    return ("set_tooltips", self.settings["tooltips"])
                elif btn.action == "toggle_touch_controls":
                    modes = ["auto", "on", "off"]
                    cur = str(self.settings.get("touch_controls", "auto")).lower()
                    idx = modes.index(cur) if cur in modes else 0
                    self.settings["touch_controls"] = modes[(idx + 1) % len(modes)]
                    self._refresh_settings_button_labels()
                    self.save_settings()
                    return ("set_touch_controls", self.settings["touch_controls"])
                elif btn.action == "toggle_touch_opacity":
                    opacities = [0.5, 0.75, 1.0]
                    cur = float(self.settings.get("touch_opacity", 0.75))
                    idx = 0
                    min_d = 999.0
                    for i, op in enumerate(opacities):
                        if abs(op - cur) < min_d:
                            min_d = abs(op - cur)
                            idx = i
                    self.settings["touch_opacity"] = opacities[(idx + 1) % len(opacities)]
                    self._refresh_settings_button_labels()
                    self.save_settings()
                    return ("set_touch_opacity", self.settings["touch_opacity"])
                elif btn.action == "open_input_mapping":
                    self.state = STATE_INPUT_MAPPING
                    self.rebinding_action = None
                    return None
                elif btn.action == "settings_back":
                    self.save_settings()
                    if self.previous_state == STATE_PLAYING:
                        self.state = STATE_PLAYING
                        return "resume_paused"
                    else:
                        self.state = STATE_MENU
                        return None

                    # Apply audio volumes immediately
                    m_vol = self.settings["master_volume"]
                    s_vol = self.settings["sfx_volume"]
                    b_vol = self.settings["bgm_volume"]
                    if self.sound_manager:
                        self.sound_manager.set_volumes(master=m_vol, sfx=s_vol)
                    if self.bgm_manager:
                        self.bgm_manager.set_volumes(master=m_vol, bgm=b_vol)
                    self.save_settings()
                    return ("volume_updated", self.settings)

        elif self.state == STATE_INPUT_MAPPING:
            if self.input_reset_button.rect.collidepoint(mouse_pos):
                self.key_bindings = dict(self.default_key_bindings)
                self.rebinding_action = None
                self.save_settings()
                self.sound_manager.play("craft")
                return "reset_keys"

            if self.input_back_button.rect.collidepoint(mouse_pos):
                self.state = STATE_SETTINGS
                self.rebinding_action = None
                self.sound_manager.play("place")
                return None

            for action, rect in self.key_bind_rects.items():
                if rect.collidepoint(mouse_pos):
                    self.rebinding_action = action
                    self.sound_manager.play("place")
                    return None

        elif self.state == STATE_MULTIPLAYER:
            if self.ip_box_rect.collidepoint(mouse_pos):
                self.typing_ip = True
                return None
            else:
                self.typing_ip = False

            for btn in self.mp_buttons:
                if btn.rect.collidepoint(mouse_pos):
                    self.sound_manager.play("place")
                    if btn.action == "host_game":
                        self.state = STATE_PLAYING
                        return "host_lan"
                    elif btn.action == "join_game":
                        self.state = STATE_PLAYING
                        return ("join_lan", self.join_ip_input)
                    elif btn.action == "menu":
                        self.state = STATE_MENU

        elif self.state in (STATE_STORY, STATE_CUTSCENE):
            act = self.cutscene.handle_click(mouse_pos, button=button)
            if act == "menu" or self.cutscene.is_finished():
                self.state = STATE_MENU
                if self.bgm_manager:
                    self.bgm_manager.update(0.0, scene="menu")
        elif self.state == STATE_CONTROLS:
            if self.back_button.rect.collidepoint(mouse_pos):
                self.sound_manager.play("place")
                self.state = STATE_MENU

        elif self.state == STATE_VICTORY:
            for btn in self.victory_buttons:
                if btn.rect.collidepoint(mouse_pos):
                    self.sound_manager.play("place")
                    if btn.action == "play":
                        self.state = STATE_PLAYING
                        return "continue_exploring"
                    elif btn.action == "menu":
                        self.state = STATE_MENU
                        return "return_to_menu"
        return None

    def handle_key(self, event):
        if self.state in (STATE_STORY, STATE_CUTSCENE):
            res = self.cutscene.handle_key(event)
            if self.cutscene.is_finished():
                self.state = STATE_MENU
                if self.bgm_manager:
                    self.bgm_manager.update(0.0, scene="menu")
            return res
        if self.state == STATE_WORLDS and self.renaming_world_target is not None:
            if event.key == pygame.K_ESCAPE:
                self.renaming_world_target = None
                self.rename_error_msg = ""
                return True
            elif event.key == pygame.K_BACKSPACE:
                self.rename_world_input = self.rename_world_input[:-1]
                self.rename_error_msg = ""
                return True
            elif event.key == pygame.K_RETURN:
                self.rename_saved_world(self.renaming_world_target, self.rename_world_input)
                return True
            elif event.unicode and len(self.rename_world_input) < 22:
                if event.unicode.isalnum() or event.unicode in (" ", "_", "-"):
                    self.rename_world_input += event.unicode
                    self.rename_error_msg = ""
                return True
        if self.state == STATE_NEW_WORLD and self.typing_world_name:
            if event.key == pygame.K_BACKSPACE:
                self.new_world_name = self.new_world_name[:-1]
                return True
            elif event.key == pygame.K_RETURN:
                self.typing_world_name = False
                return True
            elif event.unicode and len(self.new_world_name) < 22:
                if event.unicode.isalnum() or event.unicode in (" ", "_", "-"):
                    self.new_world_name += event.unicode
                return True

        if self.state == STATE_MULTIPLAYER and self.typing_ip:
            if event.key == pygame.K_BACKSPACE:
                self.join_ip_input = self.join_ip_input[:-1]
                return True
            elif event.key == pygame.K_RETURN:
                self.typing_ip = False
                return True
            elif event.unicode and (event.unicode.isdigit() or event.unicode in ".:" or event.unicode.isalpha()):
                if len(self.join_ip_input) < 25:
                    self.join_ip_input += event.unicode
                return True

        if self.state == STATE_INPUT_MAPPING:
            if self.rebinding_action:
                if event.key == pygame.K_ESCAPE:
                    self.rebinding_action = None
                else:
                    self.key_bindings[self.rebinding_action] = event.key
                    self.rebinding_action = None
                    self.save_settings()
                    self.sound_manager.play("craft")
                return True
            if event.key == pygame.K_ESCAPE:
                self.state = STATE_SETTINGS
                return True

        return False

    def render(self, target_surf):
        if self.state == STATE_MENU:
            self._render_main_menu(target_surf)
        elif self.state == STATE_SETTINGS:
            self._render_settings_screen(target_surf)
        elif self.state == STATE_INPUT_MAPPING:
            self._render_input_mapping(target_surf, pygame.mouse.get_pos())
        elif self.state == STATE_MULTIPLAYER:
            self._render_multiplayer_menu(target_surf)
        elif self.state in (STATE_STORY, STATE_CUTSCENE):
            self.cutscene.render(target_surf)
        elif self.state == STATE_CONTROLS:
            self._render_controls_screen(target_surf)
        elif self.state == STATE_VICTORY:
            self._render_victory_screen(target_surf)
        elif self.state == STATE_WORLDS:
            self._render_worlds_screen(target_surf)
        elif self.state == STATE_NEW_WORLD:
            self._render_new_world_screen(target_surf)
        elif self.state == STATE_MODS:
            self._render_mods_screen(target_surf, pygame.mouse.get_pos())
        elif self.state == STATE_ACHIEVEMENTS:
            self._render_achievements_screen(target_surf, pygame.mouse.get_pos())
        elif self.state == STATE_GAME_OVER:
            self._render_game_over_screen(target_surf)

    def _render_settings_screen(self, target_surf):
        self._render_background(target_surf)

        pw, ph = 840, 570
        px = SCREEN_WIDTH // 2 - pw // 2
        py = 55

        # Drop shadow & outer panel
        pygame.draw.rect(target_surf, (12, 15, 22, 190), (px + 6, py + 8, pw, ph), border_radius=16)
        pygame.draw.rect(target_surf, (28, 34, 50, 248), (px, py, pw, ph), border_radius=16)
        pygame.draw.rect(target_surf, COLOR_GOLD, (px, py, pw, ph), 3, border_radius=16)
        pygame.draw.rect(target_surf, (70, 85, 120), (px + 4, py + 4, pw - 8, ph - 8), 1, border_radius=12)

        # Header Title
        title = self.font_title.render("OPTIONS & SETTINGS", True, COLOR_GOLD)
        target_surf.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, py + 14))

        # Top Category Tabs (Stardew Valley / Modern RPG Inspired)
        for btn in self.tab_buttons:
            tab_id = btn.action.replace("tab_", "")
            is_active = (self.settings_tab == tab_id)
            if is_active:
                pygame.draw.rect(target_surf, (85, 72, 28, 255), btn.rect, border_radius=8)
                pygame.draw.rect(target_surf, (255, 225, 70), btn.rect, 2, border_radius=8)
                # Glowing bottom tab connector
                pygame.draw.rect(target_surf, (255, 230, 80), (btn.rect.x + 4, btn.rect.bottom - 3, btn.rect.w - 8, 4), border_radius=2)
                txt_col = (255, 240, 120)
            else:
                bg_col = (65, 80, 115, 240) if btn.is_hovered else (42, 50, 72, 225)
                border_col = (140, 160, 205) if btn.is_hovered else (85, 100, 135)
                pygame.draw.rect(target_surf, bg_col, btn.rect, border_radius=8)
                pygame.draw.rect(target_surf, border_col, btn.rect, 1, border_radius=8)
                txt_col = (255, 255, 255) if btn.is_hovered else (205, 215, 235)

            t_surf = self.font_btn.render(btn.text, True, txt_col)
            target_surf.blit(t_surf, (btn.rect.centerx - t_surf.get_width() // 2, btn.rect.centery - t_surf.get_height() // 2))

        # Inset Content Container
        cont_rect = pygame.Rect(px + 24, py + 98, pw - 48, ph - 164)
        pygame.draw.rect(target_surf, (19, 23, 36, 240), cont_rect, border_radius=10)
        pygame.draw.rect(target_surf, (55, 68, 98), cont_rect, 1, border_radius=10)

        # Content Rendering Based on Active Tab
        if self.settings_tab == "graphics":
            labels = [
                ("Graphics Renderer", "Hardware (ModernGL) or Compatibility (Software)"),
                ("Post-Processing", "Master GLSL shader pipeline toggle"),
                ("Bloom Aura Glow", "Emissive dynamic lighting on torches & magic"),
                ("Atmospheric Vignette", "Cinematic dark edge shading & focus"),
                ("Water Wave Refraction", "Sinusoidal surface ripples & fluid distortion"),
                ("Color Atmosphere", "Rich saturation & contrast tone grading"),
                ("Dynamic Lighting", "Cellular shadow propagation accuracy"),
                ("Particle Density", "Debris, weapon slash sparks & spell effects"),
                ("Display Mode", "Fullscreen or borderless windowed mode"),
            ]
            for i, (main_lbl, sub_lbl) in enumerate(labels):
                row_y = py + 104 + i * 38
                lbl_surf = self.font_btn.render(main_lbl, True, (245, 245, 250))
                sub_surf = self.font_sm.render(sub_lbl, True, (140, 160, 195))
                target_surf.blit(lbl_surf, (px + 45, row_y + 1))
                target_surf.blit(sub_surf, (px + 45, row_y + 18))

            for btn in self.graphics_buttons:
                btn.render(target_surf, self.font_btn)

        elif self.settings_tab == "audio":
            def draw_audio_slider(title, subtitle, y_pos, val, minus_btn, plus_btn):
                t_surf = self.font_btn.render(title, True, (250, 250, 255))
                s_surf = self.font_sm.render(subtitle, True, (140, 160, 195))
                target_surf.blit(t_surf, (px + 50, y_pos + 4))
                target_surf.blit(s_surf, (px + 50, y_pos + 22))

                minus_btn.render(target_surf, self.font_btn)
                plus_btn.render(target_surf, self.font_btn)

                bar_x = SCREEN_WIDTH // 2 - 105
                bar_y = y_pos + 8
                bar_w = 230
                bar_h = 24
                pygame.draw.rect(target_surf, (15, 17, 26), (bar_x, bar_y, bar_w, bar_h), border_radius=6)
                fill_w = int(bar_w * val)
                if fill_w > 0:
                    pygame.draw.rect(target_surf, (80, 180, 245), (bar_x, bar_y, fill_w, bar_h), border_radius=6)
                pygame.draw.rect(target_surf, (120, 140, 185), (bar_x, bar_y, bar_w, bar_h), 1, border_radius=6)

                pct_txt = self.font_sub.render(f"{int(round(val * 100))}%", True, (255, 255, 255))
                target_surf.blit(pct_txt, (bar_x + bar_w // 2 - pct_txt.get_width() // 2, bar_y + 3))

            draw_audio_slider("Master Volume", "Overall game audio output level", 160, self.settings["master_volume"], self.btn_vol_master_down, self.btn_vol_master_up)
            draw_audio_slider("Music (BGM)", "Procedural biome synth soundtrack", 250, self.settings["bgm_volume"], self.btn_vol_bgm_down, self.btn_vol_bgm_up)
            draw_audio_slider("Sound Effects (SFX)", "Spatial stereo combat, mining & tools", 340, self.settings["sfx_volume"], self.btn_vol_sfx_down, self.btn_vol_sfx_up)

            # Audio info banner
            info_rect = pygame.Rect(px + 45, py + 360, pw - 90, 48)
            pygame.draw.rect(target_surf, (25, 30, 45, 220), info_rect, border_radius=8)
            pygame.draw.rect(target_surf, (70, 85, 120), info_rect, 1, border_radius=8)
            info_t = self.font_sm.render("Spatial stereo channels calculate realistic distance falloff for projectiles, monsters, and mining impacts.", True, (180, 200, 230))
            target_surf.blit(info_t, (info_rect.centerx - info_t.get_width() // 2, info_rect.centery - info_t.get_height() // 2))

        elif self.settings_tab == "gameplay":
            gp_labels = [
                ("Camera Screen Shake", "Cinematic impacts, explosions & boss roars"),
                ("Boost Mode Turbo", "High-priority frame pacing for rock-solid 60 FPS"),
                ("Combat Damage Numbers", "Real-time floating RPG damage & critical popups"),
                ("Inventory Tooltips", "Detailed item stats, lore quotes & rarity tier hints"),
            ]
            for i, (main_lbl, sub_lbl) in enumerate(gp_labels):
                row_y = py + 130 + i * 65
                lbl_surf = self.font_btn.render(main_lbl, True, (245, 245, 250))
                sub_surf = self.font_sm.render(sub_lbl, True, (140, 160, 195))
                target_surf.blit(lbl_surf, (px + 50, row_y + 2))
                target_surf.blit(sub_surf, (px + 50, row_y + 22))

            for btn in self.gameplay_buttons:
                btn.render(target_surf, self.font_btn)

        elif self.settings_tab == "controls":
            ct_labels = [
                ("Virtual Touch Controls", "Auto-detect or force mobile touchscreen buttons"),
                ("Touch Overlay Opacity", "Visual transparency of on-screen touch buttons"),
                ("Input Customization", "Rebind keyboard hotkeys & movement actions"),
            ]
            for i, (main_lbl, sub_lbl) in enumerate(ct_labels):
                row_y = py + 150 + i * 74
                lbl_surf = self.font_btn.render(main_lbl, True, (245, 245, 250))
                sub_surf = self.font_sm.render(sub_lbl, True, (140, 160, 195))
                target_surf.blit(lbl_surf, (px + 50, row_y + 2))
                target_surf.blit(sub_surf, (px + 50, row_y + 22))

            for btn in self.controls_buttons:
                btn.render(target_surf, self.font_btn)

        # Global Back Button & Footer
        self.settings_back_btn.render(target_surf, self.font_btn)
        cur_rend = str(self.settings.get("renderer", "hardware")).upper()
        footer_txt = self.font_sm.render(f"Graphics Engine: {cur_rend} | Target: 60 FPS Standalone", True, (130, 145, 175))
        target_surf.blit(footer_txt, (SCREEN_WIDTH // 2 - footer_txt.get_width() // 2, py + ph - 16))

    def _render_input_mapping(self, target_surf, mouse_pos):
        self._render_background(target_surf)

        pw, ph = 780, 560
        px = SCREEN_WIDTH // 2 - pw // 2
        py = 55
        panel_rect = pygame.Rect(px, py, pw, ph)
        pygame.draw.rect(target_surf, (26, 30, 48, 245), panel_rect, border_radius=14)
        pygame.draw.rect(target_surf, COLOR_GOLD, panel_rect, 2, border_radius=14)

        title = self.font_title.render("INPUT MAPPING / KEY BINDINGS", True, COLOR_GOLD)
        target_surf.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, py + 18))

        sub = self.font_body.render("Click an action below to rebind, then press the desired key on your keyboard. [ESC] to cancel.", True, (200, 215, 235))
        target_surf.blit(sub, (SCREEN_WIDTH // 2 - sub.get_width() // 2, py + 52))

        # Two columns of actions
        actions = list(self.key_bindings.keys())
        col1 = actions[:6]
        col2 = actions[6:]

        self.key_bind_rects = {}

        def draw_column(col_actions, col_x):
            start_y = py + 90
            for i, act in enumerate(col_actions):
                row_y = start_y + i * 44
                act_lbl = self.font_btn.render(act, True, (240, 240, 245))
                target_surf.blit(act_lbl, (col_x, row_y + 6))

                # Key binding button
                k_val = self.key_bindings.get(act, pygame.K_UNKNOWN)
                k_name = pygame.key.name(k_val).upper()
                if k_val == pygame.K_SPACE:
                    k_name = "SPACE"

                bw, bh = 130, 34
                bx = col_x + 180
                by = row_y
                btn_rect = pygame.Rect(bx, by, bw, bh)
                self.key_bind_rects[act] = btn_rect

                is_rebinding = (self.rebinding_action == act)
                is_hovered = btn_rect.collidepoint(mouse_pos)

                if is_rebinding:
                    bg_col = (140, 95, 20)
                    bd_col = COLOR_GOLD
                    txt = "[PRESS KEY]"
                    t_col = COLOR_GOLD
                else:
                    bg_col = (45, 55, 80) if not is_hovered else (70, 90, 130)
                    bd_col = (110, 130, 170) if not is_hovered else (255, 230, 80)
                    txt = k_name
                    t_col = (255, 255, 255)

                pygame.draw.rect(target_surf, bg_col, btn_rect, border_radius=6)
                pygame.draw.rect(target_surf, bd_col, btn_rect, 2 if (is_rebinding or is_hovered) else 1, border_radius=6)

                txt_surf = self.font_btn.render(txt, True, t_col)
                target_surf.blit(txt_surf, (bx + bw // 2 - txt_surf.get_width() // 2, by + bh // 2 - txt_surf.get_height() // 2))

        draw_column(col1, px + 40)
        draw_column(col2, px + 410)

        # Bottom buttons
        self.input_reset_button.render(target_surf, self.font_btn)
        self.input_back_button.render(target_surf, self.font_btn)

    def _render_background(self, target_surf):
        h = SCREEN_HEIGHT
        w = SCREEN_WIDTH
        if not hasattr(self, "_bg_grad"):
            self._bg_grad = pygame.Surface((w, h))
            for y in range(h):
                ratio = y / float(h)
                r = int(14 * (1.0 - ratio) + 26 * ratio)
                g = int(18 * (1.0 - ratio) + 32 * ratio)
                b = int(34 * (1.0 - ratio) + 56 * ratio)
                pygame.draw.line(self._bg_grad, (r, g, b), (0, y), (w, y))
        target_surf.blit(self._bg_grad, (0, 0))

        t = pygame.time.get_ticks() / 1000.0
        for p in self.ambient_particles:
            ptype = p.get("type", "amber")
            if ptype == "sparkle":
                alpha = int(180 + 75 * math.sin(t * 4.0 + p.get("phase", 0)))
                col = (255, 245, 180)
            elif ptype == "bubble":
                col = (140, 210, 255)
            else:
                col = (255, 200, 90)
            pygame.draw.circle(target_surf, col, (int(p["x"]), int(p["y"])), p["size"])

    def _render_main_menu(self, target_surf):
        self._render_background(target_surf)

        t = pygame.time.get_ticks() / 1000.0

        logo_w, logo_h = 440, 92
        lx = SCREEN_WIDTH // 2 - logo_w // 2
        ly = 50

        # Pulsing golden aura glow
        glow_pulse = int(120 + 60 * math.sin(t * 3.0))
        glow_rect = pygame.Rect(lx - 10, ly - 10, logo_w + 20, logo_h + 20)
        glow_surf = pygame.Surface((glow_rect.w, glow_rect.h), pygame.SRCALPHA)
        pygame.draw.rect(glow_surf, (255, 215, 60, glow_pulse // 3), (0, 0, glow_rect.w, glow_rect.h), border_radius=18)
        pygame.draw.rect(glow_surf, (255, 235, 120, glow_pulse // 2), (4, 4, glow_rect.w - 8, glow_rect.h - 8), border_radius=15)
        target_surf.blit(glow_surf, (glow_rect.x, glow_rect.y))

        # Logo plaque
        pygame.draw.rect(target_surf, (20, 15, 28, 230), (lx - 4, ly - 4, logo_w + 8, logo_h + 8), border_radius=12)
        pygame.draw.rect(target_surf, (85, 55, 30), (lx, ly, logo_w, logo_h), border_radius=10)
        pygame.draw.rect(target_surf, (135, 90, 50), (lx + 4, ly + 4, logo_w - 8, logo_h - 8), border_radius=8)
        pygame.draw.rect(target_surf, COLOR_GOLD, (lx, ly, logo_w, logo_h), 3, border_radius=10)

        title_txt = self.font_logo.render("POTARIA", True, (255, 238, 120))
        shadow_txt = self.font_logo.render("POTARIA", True, (40, 20, 10))
        target_surf.blit(shadow_txt, (SCREEN_WIDTH // 2 - shadow_txt.get_width() // 2 + 2, ly + 14))
        target_surf.blit(title_txt, (SCREEN_WIDTH // 2 - title_txt.get_width() // 2, ly + 12))

        sub_txt = self.font_sub.render(f"Infinite Open World Action RPG  •  By {DEVELOPER}", True, (235, 220, 175))
        target_surf.blit(sub_txt, (SCREEN_WIDTH // 2 - sub_txt.get_width() // 2, ly + 63))

        # Animated Spud Mascot (with breathing, blinking, and subtle bobbing)
        mascot_frames = self.asset_factory.player_sprites.get("idle_frames", [])
        if mascot_frames:
            frame_idx = int(pygame.time.get_ticks() / 150) % len(mascot_frames)
            raw_mascot = mascot_frames[frame_idx]
            mascot_w, mascot_h = 75, 90
            scaled_mascot = pygame.transform.scale(raw_mascot, (mascot_w, mascot_h))
            bob = math.sin(t * 3.0) * 3
            mascot_x = SCREEN_WIDTH // 2 - 310
            mascot_y = int(ly + 2 + bob)

            # Mascot soft shadow
            shadow_rect = pygame.Rect(mascot_x + 12, mascot_y + mascot_h - 6, mascot_w - 24, 10)
            pygame.draw.ellipse(target_surf, (10, 12, 20, 180), shadow_rect)
            target_surf.blit(scaled_mascot, (mascot_x, mascot_y))
        else:
            spud_icon = pygame.transform.scale(self.asset_factory.branding["game_icon"], (85, 85))
            target_surf.blit(spud_icon, (SCREEN_WIDTH // 2 - 270, ly + 5))

        for btn in self.menu_buttons:
            btn.render(target_surf, self.font_btn)

        ver_surf = self.font_sm.render(f"Potaria v{GAME_VERSION} (Alpha Prototype)", True, (160, 175, 205))
        target_surf.blit(ver_surf, (SCREEN_WIDTH - ver_surf.get_width() - 16, SCREEN_HEIGHT - ver_surf.get_height() - 10))

    def _render_multiplayer_menu(self, target_surf):
        self._render_background(target_surf)

        pw, ph = 600, 520
        px = SCREEN_WIDTH // 2 - pw // 2
        py = 50
        pygame.draw.rect(target_surf, (30, 35, 50, 245), (px, py, pw, ph), border_radius=12)
        pygame.draw.rect(target_surf, COLOR_GOLD, (px, py, pw, ph), 2, border_radius=12)

        title = self.font_title.render("LAN MULTIPLAYER (1-5 PLAYERS)", True, COLOR_GOLD)
        target_surf.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, py + 22))

        # Host instructions & IP
        host_info = self.font_body.render(f"Your Local Host IP: {self.local_ip}  (Port: 25565)", True, (100, 220, 255))
        target_surf.blit(host_info, (SCREEN_WIDTH // 2 - host_info.get_width() // 2, py + 75))

        desc = self.font_sub.render("Host a cooperative session for friends on your local Wi-Fi or LAN network.", True, (200, 210, 225))
        target_surf.blit(desc, (SCREEN_WIDTH // 2 - desc.get_width() // 2, py + 105))

        # Join Input Box
        join_lbl = self.font_btn.render("Or Enter Host's LAN IP to Join:", True, (255, 230, 100))
        target_surf.blit(join_lbl, (SCREEN_WIDTH // 2 - join_lbl.get_width() // 2, py + 245))

        box_col = (50, 60, 90) if self.typing_ip else (35, 40, 60)
        border_col = COLOR_GOLD if self.typing_ip else (100, 120, 160)
        pygame.draw.rect(target_surf, box_col, self.ip_box_rect, border_radius=8)
        pygame.draw.rect(target_surf, border_col, self.ip_box_rect, 2, border_radius=8)

        cursor = "_" if (self.typing_ip and (pygame.time.get_ticks() // 500) % 2 == 0) else ""
        txt_surf = self.font_btn.render(f"{self.join_ip_input}{cursor}", True, (255, 255, 255))
        target_surf.blit(txt_surf, (self.ip_box_rect.centerx - txt_surf.get_width() // 2, self.ip_box_rect.centery - txt_surf.get_height() // 2))

        for btn in self.mp_buttons:
            btn.render(target_surf, self.font_btn)

    def _render_story_screen(self, target_surf):
        self.cutscene.render(target_surf)

    def _render_controls_screen(self, target_surf):
        self._render_background(target_surf)

        pw, ph = 860, 540
        px = SCREEN_WIDTH // 2 - pw // 2
        py = 60
        pygame.draw.rect(target_surf, (30, 35, 50, 245), (px, py, pw, ph), border_radius=12)
        pygame.draw.rect(target_surf, COLOR_GOLD, (px, py, pw, ph), 2, border_radius=12)

        title = self.font_title.render("GAME CONTROLS & HOW TO PLAY", True, COLOR_GOLD)
        target_surf.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, py + 20))

        # Dynamically lookup key names
        def kn(act, fallback):
            val = self.key_bindings.get(act)
            if val is not None:
                name = pygame.key.name(val).upper()
                return "SPACE" if val == pygame.K_SPACE else name
            return fallback

        controls = [
            (f"{kn('Move Left', 'A')} / {kn('Move Right', 'D')}", "Run left / right (Spud waddles smoothly across infinite world)"),
            (f"{kn('Jump', 'SPACE')} / Up Arrow", "Jump"),
            (f"{kn('Drop Platform', 'S')} + Jump", "Drop through wooden platforms"),
            ("Left Click (Hold)", "Mine blocks / swing weapons at mouse cursor"),
            ("Right Click (in World)", "Place selected block / wall / torch, or toggle wooden door"),
            ("Right Click (on Food / Rune)", "Eat food (heal HP) / Teleport to Nether Dungeon!"),
            (f"{kn('Character Status', 'C')} Key", "Open / Close Character Status & Paperdoll Equipment Panel"),
            (f"{kn('Toggle Mini-Map', 'M')} Key", "Toggle Mini-Map (Corner Radar -> Large Overview -> Hidden)"),
            (f"{kn('Skill Q', 'Q')} / {kn('Skill F', 'F')} / {kn('Skill V', 'V')} / {kn('Skill R', 'R')}", "Cast active combat skills"),
            ("F11 Key", "Toggle Fullscreen Mode"),
            ("Enter Key", "Open / Send LAN Multiplayer Chat Message"),
            ("1 - 9, 0 or Mouse Wheel", "Select active hotbar slot"),
            (f"{kn('Inventory', 'E')} or ESC", "Open 40-slot Backpack & Crafting Menu"),
        ]

        for i, (key, desc) in enumerate(controls):
            ks = self.font_btn.render(key, True, (255, 215, 0))
            ds = self.font_body.render(f":  {desc}", True, (240, 240, 240))
            target_surf.blit(ks, (px + 45, py + 65 + i * 32))
            target_surf.blit(ds, (px + 45 + ks.get_width() + 10, py + 65 + i * 32))

        self.back_button.render(target_surf, self.font_btn)

    def _render_victory_screen(self, target_surf):
        self._render_background(target_surf)

        pw, ph = 760, 440
        px = SCREEN_WIDTH // 2 - pw // 2
        py = 120
        pygame.draw.rect(target_surf, (30, 40, 60, 250), (px, py, pw, ph), border_radius=12)
        pygame.draw.rect(target_surf, COLOR_GOLD, (px, py, pw, ph), 3, border_radius=12)

        v_title = self.font_logo.render("VICTORY!", True, (255, 230, 60))
        target_surf.blit(v_title, (SCREEN_WIDTH // 2 - v_title.get_width() // 2, py + 30))

        v_sub = self.font_title.render("SOL-RHO THE CELESTIAL TITAN HAS FALLEN!", True, (255, 215, 0))
        target_surf.blit(v_sub, (SCREEN_WIDTH // 2 - v_sub.get_width() // 2, py + 95))

        lines = [
            "The cosmic void god has been banished from the heavens!",
            "Through courage, portal shards, and mastery of potato warfare,",
            "Spud has conquered both phases of the celestial titan in epic combat!",
            "",
            f"Developer: {DEVELOPER}",
            "Thank you for playing Potaria!"
        ]
        for i, l in enumerate(lines):
            col = COLOR_GOLD if DEVELOPER in l else COLOR_WHITE
            s = self.font_body.render(l, True, col)
            target_surf.blit(s, (SCREEN_WIDTH // 2 - s.get_width() // 2, py + 160 + i * 28))

        for btn in self.victory_buttons:
            btn.render(target_surf, self.font_btn)

    def _render_worlds_screen(self, target_surf):
        self._render_background(target_surf)

        pw, ph = 680, 560
        px = SCREEN_WIDTH // 2 - pw // 2
        py = 50
        panel_rect = pygame.Rect(px, py, pw, ph)
        pygame.draw.rect(target_surf, (24, 28, 44, 245), panel_rect, border_radius=14)
        pygame.draw.rect(target_surf, COLOR_GOLD, panel_rect, 2, border_radius=14)

        title = self.font_title.render("SELECT WORLD / EXPEDITIONS", True, COLOR_GOLD)
        target_surf.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, py + 18))

        sub = self.font_sm.render("Create custom worlds, load saved adventures, or jump straight in with Quick Play.", True, (190, 205, 230))
        target_surf.blit(sub, (SCREEN_WIDTH // 2 - sub.get_width() // 2, py + 52))

        self.worlds_create_btn.render(target_surf, self.font_btn)
        self.worlds_quick_btn.render(target_surf, self.font_btn)

        # Section header
        sep_y = 265
        pygame.draw.line(target_surf, (70, 85, 120), (px + 40, sep_y), (px + pw - 40, sep_y), 1)
        lbl = self.font_sm.render("SAVED EXPEDITIONS", True, (255, 220, 100))
        target_surf.blit(lbl, (SCREEN_WIDTH // 2 - lbl.get_width() // 2, sep_y - 8))

        if not self.world_entry_buttons:
            empty_msg = self.font_body.render("No saved worlds found. Click '[+] CREATE NEW WORLD' to begin!", True, (170, 180, 205))
            target_surf.blit(empty_msg, (SCREEN_WIDTH // 2 - empty_msg.get_width() // 2, 330))
        else:
            bx = SCREEN_WIDTH // 2 - 250
            for i, (load_b, del_b, winfo) in enumerate(self.world_entry_buttons):
                entry_y = 280 + i * 62
                entry_rect = pygame.Rect(bx, entry_y, 495, 54)
                pygame.draw.rect(target_surf, (36, 42, 65), entry_rect, border_radius=6)
                pygame.draw.rect(target_surf, (70, 85, 125), entry_rect, 1, border_radius=6)

                w_name = winfo.get("name", "Unknown")
                w_type = winfo.get("world_type", "infinite").upper()
                w_diff = winfo.get("difficulty", "normal").upper()
                w_mode = winfo.get("game_mode", "adventure").replace("_", " ").upper()
                pt_str = winfo.get("playtime_str", "0h 0m")
                lp_str = winfo.get("last_played", "Never")

                name_surf = self.font_btn.render(w_name, True, (255, 235, 120))
                target_surf.blit(name_surf, (bx + 12, entry_y + 3))

                detail_str = f"{w_type}  •  {w_diff}  •  {w_mode}"
                detail_surf = self.font_sm.render(detail_str, True, (180, 195, 220))
                target_surf.blit(detail_surf, (bx + 14, entry_y + 20))

                time_str = f"Playtime: {pt_str}  •  Last Played: {lp_str}"
                time_surf = self.font_sm.render(time_str, True, (130, 215, 240))
                target_surf.blit(time_surf, (bx + 14, entry_y + 36))

                load_b.render(target_surf, self.font_btn)
                if i < len(self.world_rename_buttons):
                    self.world_rename_buttons[i][0].render(target_surf, self.font_btn)
                del_b.render(target_surf, self.font_btn)

        self.worlds_back_btn.render(target_surf, self.font_btn)

        # Render Rename World Modal if active
        if self.renaming_world_target is not None:
            dim = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            dim.fill((10, 12, 22, 185))
            target_surf.blit(dim, (0, 0))

            mw, mh = 440, 225
            mx = SCREEN_WIDTH // 2 - mw // 2
            my = 235
            m_rect = pygame.Rect(mx, my, mw, mh)
            pygame.draw.rect(target_surf, (26, 32, 52, 250), m_rect, border_radius=12)
            pygame.draw.rect(target_surf, COLOR_GOLD, m_rect, 2, border_radius=12)

            m_title = self.font_title.render("RENAME WORLD", True, COLOR_GOLD)
            target_surf.blit(m_title, (SCREEN_WIDTH // 2 - m_title.get_width() // 2, my + 16))

            m_sub = self.font_sm.render(f"Current Name: {self.renaming_world_target}", True, (185, 205, 235))
            target_surf.blit(m_sub, (SCREEN_WIDTH // 2 - m_sub.get_width() // 2, my + 52))

            pygame.draw.rect(target_surf, (45, 56, 88), self.rename_box_rect, border_radius=6)
            pygame.draw.rect(target_surf, COLOR_GOLD, self.rename_box_rect, 2, border_radius=6)

            cursor_ch = "_" if (pygame.time.get_ticks() % 800 < 400) else ""
            inp_surf = self.font_btn.render(self.rename_world_input + cursor_ch, True, (255, 255, 255))
            target_surf.blit(inp_surf, (self.rename_box_rect.x + 12, self.rename_box_rect.centery - inp_surf.get_height() // 2))

            if self.rename_error_msg:
                err_surf = self.font_sm.render(self.rename_error_msg, True, (255, 95, 95))
                target_surf.blit(err_surf, (SCREEN_WIDTH // 2 - err_surf.get_width() // 2, my + 122))

            self.rename_confirm_btn.render(target_surf, self.font_btn)
            self.rename_cancel_btn.render(target_surf, self.font_btn)

    def _render_new_world_screen(self, target_surf):
        self._render_background(target_surf)

        pw, ph = 640, 540
        px = SCREEN_WIDTH // 2 - pw // 2
        py = 55
        panel_rect = pygame.Rect(px, py, pw, ph)
        pygame.draw.rect(target_surf, (24, 28, 44, 245), panel_rect, border_radius=14)
        pygame.draw.rect(target_surf, COLOR_GOLD, panel_rect, 2, border_radius=14)

        title = self.font_title.render("CREATE NEW WORLD", True, COLOR_GOLD)
        target_surf.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, py + 20))

        sub = self.font_sm.render("Configure your world name, generator bounds, and survival difficulty.", True, (185, 205, 235))
        target_surf.blit(sub, (SCREEN_WIDTH // 2 - sub.get_width() // 2, py + 54))

        # World Name Box
        lbl = self.font_btn.render("World Name:", True, (240, 240, 245))
        target_surf.blit(lbl, (self.world_name_rect.x, self.world_name_rect.y - 24))

        bg_col = (40, 48, 75) if not self.typing_world_name else (55, 68, 105)
        bd_col = COLOR_GOLD if self.typing_world_name else (100, 120, 160)
        pygame.draw.rect(target_surf, bg_col, self.world_name_rect, border_radius=6)
        pygame.draw.rect(target_surf, bd_col, self.world_name_rect, 2 if self.typing_world_name else 1, border_radius=6)

        name_display = self.new_world_name + ("_" if (self.typing_world_name and pygame.time.get_ticks() % 800 < 400) else "")
        txt_surf = self.font_btn.render(name_display, True, (255, 255, 255))
        target_surf.blit(txt_surf, (self.world_name_rect.x + 12, self.world_name_rect.centery - txt_surf.get_height() // 2))

        # Option Buttons (Clean Centered Layout: Type & Difficulty only)
        self.nw_btn_type.render(target_surf, self.font_btn)
        self.nw_btn_diff.render(target_surf, self.font_btn)

        # Explanatory subtitles
        if self.new_world_type == WORLD_TYPE_INFINITE:
            type_desc = "Infinite: Boundless procedural chunk streaming in both directions."
        else:
            type_desc = "Finite: Bounded 320 tiles wide with ancient bedrock barriers."
        t_surf = self.font_sm.render(type_desc, True, (160, 190, 230))
        target_surf.blit(t_surf, (SCREEN_WIDTH // 2 - t_surf.get_width() // 2, 308))

        if self.new_world_diff == DIFFICULTY_NORMAL:
            diff_desc = "Normal: Starts with wooden axe, retain all inventory upon death."
        elif self.new_world_diff == DIFFICULTY_HARDCORE:
            diff_desc = "Hardcore: Starts with 0 items, all items scatter onto the ground on death."
        else:
            diff_desc = "YOLO: Starts with 0 items, locked to 1 HEART (20 HP) PERMADEATH!"
        d_surf = self.font_sm.render(diff_desc, True, (255, 200, 120) if self.new_world_diff != DIFFICULTY_YOLO else (255, 120, 120))
        target_surf.blit(d_surf, (SCREEN_WIDTH // 2 - d_surf.get_width() // 2, 378))

        # Active Add-On Status indicator
        if self.enabled_mods.get("last_man_standing", False):
            m_badge = self.font_sm.render("[!] Active Add-On: Last Man Standing (PvP Friendly Fire ENABLED)", True, (255, 175, 80))
            target_surf.blit(m_badge, (SCREEN_WIDTH // 2 - m_badge.get_width() // 2, 410))

        self.nw_btn_create.render(target_surf, self.font_btn)
        self.nw_btn_back.render(target_surf, self.font_btn)

    def _render_mods_screen(self, target_surf, mouse_pos):
        self._render_background(target_surf)

        pw, ph = 780, 550
        px = SCREEN_WIDTH // 2 - pw // 2
        py = 55
        panel_rect = pygame.Rect(px, py, pw, ph)
        pygame.draw.rect(target_surf, (24, 28, 44, 245), panel_rect, border_radius=14)
        pygame.draw.rect(target_surf, COLOR_GOLD, panel_rect, 2, border_radius=14)

        title = self.font_title.render("MODS & ADD-ONS WORKSHOP", True, COLOR_GOLD)
        target_surf.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, py + 18))

        sub = self.font_sm.render("Manage installed modifications, custom game-modes, and expansion rulesets.", True, (185, 205, 235))
        target_surf.blit(sub, (SCREEN_WIDTH // 2 - sub.get_width() // 2, py + 52))

        # Card 1: Last Man Standing Add-On
        card1_rect = pygame.Rect(px + 35, py + 85, pw - 70, 140)
        is_lms = self.enabled_mods.get("last_man_standing", False)
        bg_col = (35, 42, 65) if not is_lms else (44, 38, 62)
        bd_col = (80, 100, 140) if not is_lms else (255, 195, 80)
        pygame.draw.rect(target_surf, bg_col, card1_rect, border_radius=10)
        pygame.draw.rect(target_surf, bd_col, card1_rect, 2, border_radius=10)

        # Title & Meta
        t_surf = self.font_btn.render("Last Man Standing (PvP Battle Royale Add-On)", True, (255, 235, 120))
        target_surf.blit(t_surf, (card1_rect.x + 20, card1_rect.y + 16))

        meta = self.font_sm.render("Author: Kurados  •  Version: 1.2.0  •  Classification: Game Mode Add-On", True, (180, 195, 220))
        target_surf.blit(meta, (card1_rect.x + 20, card1_rect.y + 42))

        # Description
        desc_lines = [
            "Enables lethal friendly fire between players in Singleplayer and LAN Multiplayer.",
            "Eliminates player respawns and crowns the solitary survivor with battle royale victory fanfare!"
        ]
        for idx, dl in enumerate(desc_lines):
            ds = self.font_sm.render(dl, True, (220, 225, 235))
            target_surf.blit(ds, (card1_rect.x + 20, card1_rect.y + 70 + idx * 20))

        # Status badge
        status_txt = "[ ENABLED ]" if is_lms else "[ DISABLED ]"
        status_col = (80, 240, 120) if is_lms else (170, 180, 195)
        st_surf = self.font_btn.render(status_txt, True, status_col)
        target_surf.blit(st_surf, (card1_rect.x + card1_rect.w - 275, card1_rect.y + 18))

        self.mods_toggle_lms_btn.render(target_surf, self.font_btn)

        # Card 2: Engine Built-In Features
        card2_rect = pygame.Rect(px + 35, py + 245, pw - 70, 110)
        pygame.draw.rect(target_surf, (30, 36, 54), card2_rect, border_radius=10)
        pygame.draw.rect(target_surf, (70, 85, 120), card2_rect, 1, border_radius=10)

        t2_surf = self.font_btn.render("HD Liquid Physics & Procedural Trees Module", True, (200, 220, 255))
        target_surf.blit(t2_surf, (card2_rect.x + 20, card2_rect.y + 16))

        meta2 = self.font_sm.render("Author: Kurados  •  Status: Core Engine Module  •  Always Active", True, (160, 175, 200))
        target_surf.blit(meta2, (card2_rect.x + 20, card2_rect.y + 42))

        desc2 = self.font_sm.render("Cute Terraria tree canopies with root flares, waving liquid water, and bubble oxygen meter.", True, (190, 200, 215))
        target_surf.blit(desc2, (card2_rect.x + 20, card2_rect.y + 68))

        self.mods_back_btn.render(target_surf, self.font_btn)

    def handle_scroll(self, scroll_delta):
        """Handles mouse wheel scrolling in menus (e.g. Achievements browser)."""
        if self.state == STATE_ACHIEVEMENTS:
            max_s = getattr(self.achievement_manager, "max_scroll", 0.0)
            self.achievements_scroll_y -= scroll_delta * 45.0
            if max_s > 0:
                self.achievements_scroll_y = max(0.0, min(self.achievements_scroll_y, max_s))
            else:
                self.achievements_scroll_y = max(0.0, self.achievements_scroll_y)

    def _render_achievements_screen(self, target_surf, mouse_pos):
        self._render_background(target_surf)
        self.achievement_manager.render_browser(target_surf, mouse_pos, scroll_y=int(self.achievements_scroll_y))
        self.achievements_back_btn.render(target_surf, self.font_btn)

    def _render_game_over_screen(self, target_surf):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((45, 10, 10, 225))
        target_surf.blit(overlay, (0, 0))

        pw, ph = 640, 420
        px = SCREEN_WIDTH // 2 - pw // 2
        py = 140
        panel_rect = pygame.Rect(px, py, pw, ph)
        pygame.draw.rect(target_surf, (30, 12, 16, 245), panel_rect, border_radius=14)
        pygame.draw.rect(target_surf, (220, 50, 50), panel_rect, 3, border_radius=14)

        title = self.font_logo.render("GAME OVER", True, (255, 60, 60))
        target_surf.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, py + 30))

        sub = self.font_title.render("YOLO MODE — 1 HEART PERMADEATH", True, COLOR_GOLD)
        target_surf.blit(sub, (SCREEN_WIDTH // 2 - sub.get_width() // 2, py + 95))

        lines = [
            "Your solitary heart was pierced by the darkness.",
            "In YOLO mode, there are no respawn shrines or second chances.",
            "Your potato soul has scattered to the winds of the Root Realm."
        ]
        for i, line in enumerate(lines):
            ls = self.font_body.render(line, True, (230, 200, 200))
            target_surf.blit(ls, (SCREEN_WIDTH // 2 - ls.get_width() // 2, py + 150 + i * 26))

        for btn in self.game_over_buttons:
            btn.render(target_surf, self.font_btn)
