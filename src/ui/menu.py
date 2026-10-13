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
    DIFFICULTY_EASY, DIFFICULTY_NORMAL, DIFFICULTY_HARDCORE, DIFFICULTY_YOLO,
    WORLD_TYPE_INFINITE, WORLD_TYPE_FINITE,
    MODE_ADVENTURE, MODE_LAST_MAN_STANDING, AVAILABLE_MODES,
    SETTINGS_FILE
)
from src.settings_manager import (
    load_settings as load_settings_disk,
    save_settings as save_settings_disk,
    DEFAULT_SETTINGS,
    DEFAULT_KEY_BINDINGS
)
from src.rpg.achievements import AchievementManager
from src.ui.cutscene import CutsceneEngine
from src.network.client import LANDiscovery


STATE_MULTIPLAYER = "multiplayer"
STATE_INPUT_MAPPING = "input_mapping"

class Button:
    def __init__(self, x, y, width, height, text, action, icon=None, tooltip=""):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.action = action
        self.icon = icon
        self.tooltip = tooltip
        self.is_hovered = False

    def update(self, mouse_pos):
        self.is_hovered = self.rect.collidepoint(mouse_pos)

    def _render_icon(self, target_surf, cx, cy):
        if self.icon == "play":
            # Sleek emerald/gold right-pointing triangle with inner highlight
            tri_pts = [(cx - 6, cy - 8), (cx + 9, cy), (cx - 6, cy + 8)]
            tri_col = (255, 240, 100) if self.is_hovered else (80, 230, 120)
            # Drop shadow
            pygame.draw.polygon(target_surf, (15, 20, 30), [(cx - 5, cy - 7), (cx + 10, cy + 1), (cx - 5, cy + 9)])
            pygame.draw.polygon(target_surf, tri_col, tri_pts)
            pygame.draw.polygon(target_surf, (255, 255, 220), tri_pts, 1)
        elif self.icon == "rename":
            # Sleek cyan/gold quill/pencil icon
            pen_col = (130, 245, 255) if self.is_hovered else (90, 195, 235)
            # Drop shadow
            pygame.draw.line(target_surf, (15, 20, 30), (cx - 5, cy + 7), (cx + 7, cy - 5), 3)
            pygame.draw.line(target_surf, pen_col, (cx - 6, cy + 6), (cx + 6, cy - 6), 3)
            pygame.draw.circle(target_surf, (255, 225, 100) if self.is_hovered else pen_col, (cx + 7, cy - 7), 3)
            pygame.draw.line(target_surf, (255, 255, 255), (cx - 7, cy + 8), (cx - 4, cy + 8), 2)
        elif self.icon == "delete":
            # Sleek crimson trashcan icon with lid & vertical slats
            del_col = (255, 95, 95) if self.is_hovered else (225, 75, 75)
            # Drop shadow
            pygame.draw.rect(target_surf, (15, 20, 30), (cx - 5, cy - 3, 12, 11), 2, border_radius=2)
            # Can body
            pygame.draw.rect(target_surf, del_col, (cx - 6, cy - 4, 12, 11), 2, border_radius=2)
            # Lid & handle
            pygame.draw.line(target_surf, del_col, (cx - 8, cy - 5), (cx + 8, cy - 5), 2)
            pygame.draw.line(target_surf, (255, 220, 220) if self.is_hovered else del_col, (cx - 3, cy - 7), (cx + 3, cy - 7), 2)
            # Ribs
            pygame.draw.line(target_surf, del_col, (cx - 2, cy - 2), (cx - 2, cy + 4), 1)
            pygame.draw.line(target_surf, del_col, (cx + 2, cy - 2), (cx + 2, cy + 4), 1)
        elif self.icon in ("plus", "+"):
            p_col = (120, 240, 160) if self.is_hovered else (80, 215, 130)
            pygame.draw.line(target_surf, (15, 20, 30), (cx - 6, cy + 1), (cx + 8, cy + 1), 3)
            pygame.draw.line(target_surf, (15, 20, 30), (cx + 1, cy - 6), (cx + 1, cy + 8), 3)
            pygame.draw.line(target_surf, p_col, (cx - 7, cy), (cx + 7, cy), 3)
            pygame.draw.line(target_surf, p_col, (cx, cy - 7), (cx, cy + 7), 3)
            pygame.draw.line(target_surf, (255, 255, 255), (cx - 6, cy), (cx + 6, cy), 1)
            pygame.draw.line(target_surf, (255, 255, 255), (cx, cy - 6), (cx, cy + 6), 1)
        elif self.icon in ("back", "<"):
            b_col = (255, 220, 110) if self.is_hovered else (220, 180, 80)
            pts = [(cx + 4, cy - 7), (cx - 5, cy), (cx + 4, cy + 7)]
            sh_pts = [(cx + 5, cy - 6), (cx - 4, cy + 1), (cx + 5, cy + 8)]
            pygame.draw.lines(target_surf, (15, 20, 30), False, sh_pts, 3)
            pygame.draw.lines(target_surf, b_col, False, pts, 3)
            pygame.draw.lines(target_surf, (255, 255, 230), False, pts, 1)
        elif self.icon == "join":
            j_col = (120, 220, 255) if self.is_hovered else (70, 180, 230)
            arr = [(cx - 1, cy - 5), (cx + 6, cy), (cx - 1, cy + 5)]
            pygame.draw.line(target_surf, (15, 20, 30), (cx - 6, cy + 1), (cx + 3, cy + 1), 3)
            pygame.draw.polygon(target_surf, (15, 20, 30), [(p[0]+1, p[1]+1) for p in arr])
            pygame.draw.line(target_surf, j_col, (cx - 7, cy), (cx + 3, cy), 2)
            pygame.draw.polygon(target_surf, j_col, arr)
        elif isinstance(self.icon, pygame.Surface):
            ix = cx - self.icon.get_width() // 2
            iy = cy - self.icon.get_height() // 2
            target_surf.blit(self.icon, (ix, iy))

    def render(self, target_surf, font):
        bg_col = (55, 65, 95, 230) if not self.is_hovered else (80, 105, 155, 245)
        border_col = (110, 125, 170) if not self.is_hovered else (255, 230, 80)
        
        pygame.draw.rect(target_surf, bg_col, self.rect, border_radius=8)
        pygame.draw.rect(target_surf, border_col, self.rect, 2, border_radius=8)

        if self.is_hovered:
            pygame.draw.rect(target_surf, (255, 255, 180, 90), (self.rect.x + 2, self.rect.y + 2, self.rect.w - 4, 3), border_radius=4)

        if self.icon and self.text:
            text_col = (255, 255, 255) if not self.is_hovered else (255, 235, 100)
            txt_surf = font.render(self.text, True, text_col)
            icon_w = 20
            gap = 8
            total_w = icon_w + gap + txt_surf.get_width()
            start_x = self.rect.centerx - total_w // 2
            cx = start_x + icon_w // 2
            cy = self.rect.centery
            tx = start_x + icon_w + gap
            ty = self.rect.centery - txt_surf.get_height() // 2
            self._render_icon(target_surf, cx, cy)
            target_surf.blit(txt_surf, (tx, ty))
        elif self.icon:
            cx, cy = self.rect.centerx, self.rect.centery
            self._render_icon(target_surf, cx, cy)
        elif self.text:
            text_col = (255, 255, 255) if not self.is_hovered else (255, 235, 100)
            txt_surf = font.render(self.text, True, text_col)
            tx = self.rect.centerx - txt_surf.get_width() // 2
            ty = self.rect.centery - txt_surf.get_height() // 2
            target_surf.blit(txt_surf, (tx, ty))

class MenuManager:
    def __init__(self, asset_factory, sound_manager, bgm_manager=None, achievement_manager=None, settings=None, key_bindings=None):
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

        from src.ui.theme import font_title, font_semibold, font_bold, font_regular
        self.font_logo = font_title(46)
        self.font_sub = font_semibold(16)
        self.font_btn = font_semibold(18)
        self.font_body = font_regular(15)
        self.font = self.font_body
        self.font_title = font_bold(26)
        self.font_sm = font_regular(13)

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
            Button(cx, start_y, btn_w, btn_h, "SINGLEPLAYER", "play_single", tooltip="Start your solo sandbox adventure"),
            Button(cx, start_y + gap, btn_w, btn_h, "LAN MULTIPLAYER (1-5P)", "multiplayer", tooltip="Host or join a local multiplayer session (1-5 players)"),
            Button(cx, start_y + gap * 2, btn_w, btn_h, "MODS / ADD-ONS", "mods", tooltip="Configure game modifiers and custom modes"),
            Button(cx, start_y + gap * 3, btn_w, btn_h, "ACHIEVEMENTS", "achievements", tooltip="View unlocked achievements and progression milestones"),
            Button(cx, start_y + gap * 4, btn_w, btn_h, "SETTINGS & AUDIO", "settings", tooltip="Configure graphics, audio, gameplay and input bindings"),
            Button(cx, start_y + gap * 5, btn_w, btn_h, "PROLOGUE CUTSCENE", "cutscene", tooltip="Replay the story prologue animated cutscene"),
            Button(cx, start_y + gap * 6, btn_w, btn_h, "CONTROLS & HELP", "controls", tooltip="View keyboard controls, key bindings and game guide"),
            Button(cx, start_y + gap * 7, btn_w, btn_h, "QUIT", "quit", tooltip="Exit game and return to desktop"),
        ]

        # Settings Configuration
        if settings is not None:
            self.settings = settings
        else:
            self.settings = dict(DEFAULT_SETTINGS)
        self.resolutions = ["1920x1080", "1600x900", "1366x768", "1280x720"]
        self.settings_tab = "graphics"

        # Key Bindings / Input Mapping
        self.default_key_bindings = dict(DEFAULT_KEY_BINDINGS)
        if key_bindings is not None:
            self.key_bindings = key_bindings
        else:
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
        self.btn_res = Button(gx, gy_start + 4 * gy_step, gw, gh, f"RESOLUTION: {self.settings['resolution']}", "cycle_resolution")
        self.btn_color = Button(gx, gy_start + 5 * gy_step, gw, gh, "COLOR GRADE: VIBRANT", "cycle_color_grade")
        self.btn_light = Button(gx, gy_start + 6 * gy_step, gw, gh, "LIGHTING: HIGH", "cycle_lighting_quality")
        self.btn_part = Button(gx, gy_start + 7 * gy_step, gw, gh, "PARTICLES: HIGH", "cycle_particle_density")
        self.btn_disp = Button(gx, gy_start + 8 * gy_step, gw, gh, "DISPLAY: WINDOWED", "toggle_display")
        self.graphics_buttons = [
            self.btn_renderer, self.btn_shaders, self.btn_bloom, self.btn_vignette,
            self.btn_res, self.btn_color, self.btn_light, self.btn_part, self.btn_disp
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
        self.settings_back_btn = Button(SCREEN_WIDTH // 2 - 110, py + ph - 52, 220, 38, "<  BACK TO MENU", "settings_back", icon="back", tooltip="Return to main menu")

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
        self.input_reset_button = Button(SCREEN_WIDTH // 2 - 210, SCREEN_HEIGHT - 95, 190, 42, "RESET DEFAULTS", "reset_keys", tooltip="Restore default keybindings")
        self.input_back_button = Button(SCREEN_WIDTH // 2 + 20, SCREEN_HEIGHT - 95, 190, 42, "< BACK TO SETTINGS", "input_back", icon="back", tooltip="Return to settings menu")

        # Multiplayer Menu Buttons & State
        self.discovery = LANDiscovery()
        mp_pw, mp_ph = 760, 580
        mp_px = SCREEN_WIDTH // 2 - mp_pw // 2
        mp_card_w = mp_pw - 50
        mp_card_x = mp_px + 25
        mp_btn_w = 210
        mp_btn_h = 38

        self.mp_buttons = [
            Button(mp_card_x + mp_card_w - mp_btn_w - 15, 176, mp_btn_w, mp_btn_h, "HOST LAN GAME", "host_game", icon="plus", tooltip="Host world on local LAN port 25565"),
            Button(mp_card_x + mp_card_w - mp_btn_w - 15, 502, mp_btn_w, mp_btn_h, "CONNECT TO IP", "join_game", icon="join", tooltip="Connect to specified IP address"),
            Button(SCREEN_WIDTH // 2 - 100, 572, 200, 38, "<  BACK TO MENU", "menu", icon="back", tooltip="Return to main menu"),
        ]
        self.join_ip_input = "127.0.0.1"
        self.typing_ip = False
        self.ip_box_rect = pygame.Rect(mp_card_x + 18, 504, 320, 36)

        # Room key input modal & server selection
        self.room_key_modal_active = False
        self.room_key_modal_target = None  # (ip, port, is_private)
        self.room_key_input = ""
        self.room_key_error = ""
        self.room_key_box_rect = pygame.Rect(SCREEN_WIDTH // 2 - 140, 320, 280, 38)
        self.room_key_join_btn = Button(SCREEN_WIDTH // 2 - 130, 375, 120, 38, "JOIN", "confirm_room_key", icon="join", tooltip="Connect to server with entered room key")
        self.room_key_cancel_btn = Button(SCREEN_WIDTH // 2 + 10, 375, 120, 38, "CANCEL", "cancel_room_key", tooltip="Cancel and return to multiplayer lobby")

        # LAN Host configuration state
        self.hosting_lan = False
        self.host_room_key = ""
        self.typing_host_key = False
        self.host_key_box_rect = pygame.Rect(mp_card_x + 18, 178, 320, 36)

        self.back_button = Button(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT - 95, 200, 44, "<  BACK TO MENU", "menu", icon="back", tooltip="Return to main menu")
        self.victory_buttons = [
            Button(SCREEN_WIDTH // 2 - 220, SCREEN_HEIGHT - 120, 200, 46, "CONTINUE EXPLORING", "play", tooltip="Continue playing in the current world"),
            Button(SCREEN_WIDTH // 2 + 20, SCREEN_HEIGHT - 120, 200, 46, "MAIN MENU", "menu", icon="back", tooltip="Save and return to main menu"),
        ]

        # Determine Local LAN IP for hosting
        try:
            self.local_ip = socket.gethostbyname(socket.gethostname())
        except Exception:
            self.local_ip = "127.0.0.1"

        # Worlds Menu Buttons & Scrolling
        self.saved_worlds = []
        self.world_entry_buttons = []
        self.world_rename_buttons = []
        self.worlds_scroll_y = 0.0
        self.worlds_dragging = False
        self.max_worlds_scroll = 0.0
        self.renaming_world_target = None
        self.rename_world_input = ""
        self.rename_error_msg = ""
        self.rename_box_rect = pygame.Rect(SCREEN_WIDTH // 2 - 180, 325, 360, 40)
        self.rename_confirm_btn = Button(SCREEN_WIDTH // 2 - 140, 385, 130, 40, "SAVE NAME", "confirm_rename", tooltip="Save new world name")
        self.rename_cancel_btn = Button(SCREEN_WIDTH // 2 + 10, 385, 130, 40, "CANCEL", "cancel_rename", tooltip="Cancel renaming")
        self.worlds_create_btn = Button(cx, 160, btn_w, btn_h, "[+] CREATE NEW WORLD", "open_new_world", icon="plus", tooltip="Configure and generate a new world")
        self.worlds_quick_btn = Button(cx, 215, btn_w, btn_h, "QUICK PLAY (NORMAL INFINITE)", "quick_play", icon="play", tooltip="Quickly jump into a default infinite world")
        self.worlds_back_btn = Button(cx, SCREEN_HEIGHT - 85, btn_w, btn_h, "< BACK TO MENU", "menu", icon="back", tooltip="Return to main menu")

        # YOLO Confirmation Modal Buttons
        self.show_yolo_warning = False
        self.yolo_confirm_btn = Button(SCREEN_WIDTH // 2 - 140, 375, 130, 40, "ACCEPT RISK", "confirm_yolo", tooltip="Confirm YOLO mode and start game")
        self.yolo_cancel_btn = Button(SCREEN_WIDTH // 2 + 10, 375, 130, 40, "CANCEL", "cancel_yolo", tooltip="Cancel and select another difficulty")

        # Mods / Add-Ons
        self.mods_file = os.path.join("saves", "mods.json")
        self.enabled_mods = {"last_man_standing": False}
        self.load_mods()

        # Dedicated Buttons for MODS & ACHIEVEMENTS screens
        self.mods_toggle_lms_btn = Button(cx + 175, 255, 120, 36, "ENABLE", "toggle_lms", tooltip="Toggle Last Man Standing battle royale survival mode")
        self.mods_back_btn = Button(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT - 85, 200, 44, "<  BACK TO MENU", "menu", icon="back", tooltip="Return to main menu")
        self.achievements_back_btn = Button(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT - 85, 200, 44, "<  BACK TO MENU", "menu", icon="back", tooltip="Return to previous screen")
        self._refresh_mods_button_labels()

        # New World Configuration (Clean layout with Type & Difficulty only)
        self.new_world_name = "Spud World"
        self.new_world_type = WORLD_TYPE_INFINITE
        self.new_world_diff = DIFFICULTY_NORMAL
        self.new_world_mode = MODE_LAST_MAN_STANDING if self.enabled_mods.get("last_man_standing", False) else MODE_ADVENTURE
        self.typing_world_name = False
        self.world_name_rect = pygame.Rect(cx - 30, 205, btn_w + 60, 38)
        self.nw_btn_type = Button(cx, 265, btn_w, btn_h, "WORLD TYPE: INFINITE", "toggle_type", tooltip="Switch between Infinite open world and Finite bounded world")
        self.nw_btn_diff = Button(cx, 335, btn_w, btn_h, "DIFFICULTY: NORMAL", "toggle_diff", tooltip="Select difficulty: Easy, Normal, Hardcore, or YOLO")
        # Hidden/off-screen legacy attribute to retain backwards compatibility
        self.nw_btn_mode = Button(cx, -100, btn_w, btn_h, "MODE: ADVENTURE", "toggle_mode", tooltip="Toggle game mode")
        self.nw_btn_create = Button(cx, 435, btn_w, btn_h, "CREATE & PLAY WORLD", "create_confirm", icon="plus", tooltip="Generate world and begin adventure")
        self.nw_btn_back = Button(cx, 495, btn_w, btn_h, "< CANCEL", "cancel_new_world", icon="back", tooltip="Cancel world creation and go back")

        # Game Over / Permadeath Screen Buttons (YOLO Mode)
        self.game_over_buttons = [
            Button(cx, 420, btn_w, btn_h, "Try Harder (Main Menu)", "menu", tooltip="Purge world and return to main menu"),
        ]

        self.settings_file = SETTINGS_FILE
        if settings is None:
            self.load_settings()
        else:
            self._apply_audio_volumes()
            self._refresh_settings_button_labels()

    def _apply_audio_volumes(self):
        """Immediately applies volume settings to sound and bgm managers."""
        m_vol = float(self.settings.get("master_volume", 1.0))
        s_vol = float(self.settings.get("sfx_volume", 0.85))
        b_vol = float(self.settings.get("bgm_volume", 0.65))
        if self.sound_manager and hasattr(self.sound_manager, "set_volumes"):
            self.sound_manager.set_volumes(master=m_vol, sfx=s_vol)
        if self.bgm_manager and hasattr(self.bgm_manager, "set_volumes"):
            self.bgm_manager.set_volumes(master=m_vol, bgm=b_vol)

    def load_settings(self):
        """Loads persistent user settings and key bindings from disk."""
        loaded_cfg, loaded_keys = load_settings_disk(self.settings_file)
        self.settings.update(loaded_cfg)
        self.key_bindings.update(loaded_keys)
        self._apply_audio_volumes()
        self._refresh_settings_button_labels()

    def save_settings(self):
        """Persists current user settings and key bindings to disk atomically."""
        save_settings_disk(self.settings, self.key_bindings, path=self.settings_file)


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
            elif btn.action == "cycle_resolution":
                res = str(self.settings.get("resolution", "1920x1080"))
                btn.text = f"RESOLUTION: {res}"
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
        self.last_mouse_pos = mouse_pos
        # Update Menu BGM if in any menu-related state
        if self.bgm_manager and hasattr(self.bgm_manager, "update") and self.state in (
            STATE_MENU, STATE_SETTINGS, STATE_INPUT_MAPPING, STATE_MULTIPLAYER,
            STATE_CONTROLS, STATE_WORLDS, STATE_NEW_WORLD,
            STATE_MODS, STATE_ACHIEVEMENTS
        ):
            self.bgm_manager.update(dt, scene="menu")
        elif self.bgm_manager and hasattr(self.bgm_manager, "update") and self.state in (STATE_STORY, STATE_CUTSCENE):
            self.bgm_manager.update(dt, scene="cutscene")

        t = pygame.time.get_ticks() / 1000.0
        for p in self.ambient_particles:
            p["y"] -= p["speed"]
            p["x"] += math.sin(p.get("phase", 0) + t * 0.8) * 0.4
            if p["y"] < -10:
                p["y"] = SCREEN_HEIGHT + 10
                p["x"] = random.uniform(0, SCREEN_WIDTH)

        self.active_tooltip = ""
        if self.state == STATE_MENU:
            for btn in self.menu_buttons:
                btn.update(mouse_pos)
                if btn.is_hovered and btn.tooltip:
                    self.active_tooltip = btn.tooltip
        elif self.state == STATE_MODS:
            self.mods_toggle_lms_btn.update(mouse_pos)
            self.mods_back_btn.update(mouse_pos)
            if self.mods_toggle_lms_btn.is_hovered and self.mods_toggle_lms_btn.tooltip:
                self.active_tooltip = self.mods_toggle_lms_btn.tooltip
            elif self.mods_back_btn.is_hovered and self.mods_back_btn.tooltip:
                self.active_tooltip = self.mods_back_btn.tooltip
        elif self.state == STATE_ACHIEVEMENTS:
            self.achievements_back_btn.text = "<  BACK TO GAME" if self.previous_state == STATE_PLAYING else "<  BACK TO MENU"
            self.achievements_back_btn.update(mouse_pos)
            if self.achievements_back_btn.is_hovered and self.achievements_back_btn.tooltip:
                self.active_tooltip = self.achievements_back_btn.tooltip
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
                if btn.is_hovered and btn.tooltip:
                    self.active_tooltip = btn.tooltip
        elif self.state == STATE_INPUT_MAPPING:
            self.input_reset_button.update(mouse_pos)
            self.input_back_button.update(mouse_pos)
            if self.input_reset_button.is_hovered and self.input_reset_button.tooltip:
                self.active_tooltip = self.input_reset_button.tooltip
            elif self.input_back_button.is_hovered and self.input_back_button.tooltip:
                self.active_tooltip = self.input_back_button.tooltip
        elif self.state == STATE_MULTIPLAYER:
            if getattr(self, "room_key_modal_active", False):
                self.room_key_join_btn.update(mouse_pos)
                self.room_key_cancel_btn.update(mouse_pos)
                if self.room_key_join_btn.is_hovered and self.room_key_join_btn.tooltip:
                    self.active_tooltip = self.room_key_join_btn.tooltip
                elif self.room_key_cancel_btn.is_hovered and self.room_key_cancel_btn.tooltip:
                    self.active_tooltip = self.room_key_cancel_btn.tooltip
            else:
                for btn in self.mp_buttons:
                    btn.update(mouse_pos)
                    if btn.is_hovered and btn.tooltip:
                        self.active_tooltip = btn.tooltip
                for j_btn, _ in getattr(self, "lan_join_buttons", []):
                    j_btn.update(mouse_pos)
                    if j_btn.is_hovered and j_btn.tooltip:
                        self.active_tooltip = j_btn.tooltip
        elif self.state in (STATE_STORY, STATE_CUTSCENE):
            self.cutscene.update(dt, mouse_pos)
            if self.cutscene.is_finished():
                self.state = STATE_MENU
                if self.bgm_manager:
                    self.bgm_manager.update(dt, scene="menu")
        elif self.state == STATE_CONTROLS:
            self.back_button.update(mouse_pos)
            if self.back_button.is_hovered and self.back_button.tooltip:
                self.active_tooltip = self.back_button.tooltip
        elif self.state == STATE_VICTORY:
            for btn in self.victory_buttons:
                btn.update(mouse_pos)
                if btn.is_hovered and btn.tooltip:
                    self.active_tooltip = btn.tooltip
        elif self.state == STATE_WORLDS:
            if self.renaming_world_target is not None:
                self.rename_confirm_btn.update(mouse_pos)
                self.rename_cancel_btn.update(mouse_pos)
                if self.rename_confirm_btn.is_hovered and self.rename_confirm_btn.tooltip:
                    self.active_tooltip = self.rename_confirm_btn.tooltip
                elif self.rename_cancel_btn.is_hovered and self.rename_cancel_btn.tooltip:
                    self.active_tooltip = self.rename_cancel_btn.tooltip
            else:
                self.worlds_create_btn.update(mouse_pos)
                self.worlds_quick_btn.update(mouse_pos)
                self.worlds_back_btn.update(mouse_pos)
                if self.worlds_create_btn.is_hovered and self.worlds_create_btn.tooltip:
                    self.active_tooltip = self.worlds_create_btn.tooltip
                elif self.worlds_quick_btn.is_hovered and self.worlds_quick_btn.tooltip:
                    self.active_tooltip = self.worlds_quick_btn.tooltip
                elif self.worlds_back_btn.is_hovered and self.worlds_back_btn.tooltip:
                    self.active_tooltip = self.worlds_back_btn.tooltip
                
                # Check scrollbar dragging
                track_rect = pygame.Rect(SCREEN_WIDTH // 2 + 252, 275, 14, 255)
                if pygame.mouse.get_pressed()[0] and (track_rect.collidepoint(mouse_pos) or getattr(self, "worlds_dragging", False)):
                    self.worlds_dragging = True
                    if self.max_worlds_scroll > 0:
                        rel_y = (mouse_pos[1] - 275) / 255.0
                        self.worlds_scroll_y = max(0.0, min(rel_y * self.max_worlds_scroll, self.max_worlds_scroll))
                else:
                    self.worlds_dragging = False

                viewport_rect = pygame.Rect(SCREEN_WIDTH // 2 - 250, 275, 515, 255)
                scroll_y = getattr(self, "worlds_scroll_y", 0.0)
                for load_b, del_b, _ in self.world_entry_buttons:
                    adj_load = load_b.rect.move(0, -scroll_y)
                    adj_del = del_b.rect.move(0, -scroll_y)
                    load_b.is_hovered = viewport_rect.collidepoint(mouse_pos) and adj_load.collidepoint(mouse_pos)
                    del_b.is_hovered = viewport_rect.collidepoint(mouse_pos) and adj_del.collidepoint(mouse_pos)
                    if load_b.is_hovered and load_b.tooltip:
                        self.active_tooltip = load_b.tooltip
                    elif del_b.is_hovered and del_b.tooltip:
                        self.active_tooltip = del_b.tooltip
                for ren_b, _ in self.world_rename_buttons:
                    adj_ren = ren_b.rect.move(0, -scroll_y)
                    ren_b.is_hovered = viewport_rect.collidepoint(mouse_pos) and adj_ren.collidepoint(mouse_pos)
                    if ren_b.is_hovered and ren_b.tooltip:
                        self.active_tooltip = ren_b.tooltip
        elif self.state == STATE_NEW_WORLD:
            if getattr(self, "show_yolo_warning", False):
                self.yolo_confirm_btn.update(mouse_pos)
                self.yolo_cancel_btn.update(mouse_pos)
                if self.yolo_confirm_btn.is_hovered and self.yolo_confirm_btn.tooltip:
                    self.active_tooltip = self.yolo_confirm_btn.tooltip
                elif self.yolo_cancel_btn.is_hovered and self.yolo_cancel_btn.tooltip:
                    self.active_tooltip = self.yolo_cancel_btn.tooltip
            else:
                self.nw_btn_type.update(mouse_pos)
                self.nw_btn_diff.update(mouse_pos)
                self.nw_btn_create.update(mouse_pos)
                self.nw_btn_back.update(mouse_pos)
                if self.nw_btn_type.is_hovered and self.nw_btn_type.tooltip:
                    self.active_tooltip = self.nw_btn_type.tooltip
                elif self.nw_btn_diff.is_hovered and self.nw_btn_diff.tooltip:
                    self.active_tooltip = self.nw_btn_diff.tooltip
                elif self.nw_btn_create.is_hovered and self.nw_btn_create.tooltip:
                    self.active_tooltip = self.nw_btn_create.tooltip
                elif self.nw_btn_back.is_hovered and self.nw_btn_back.tooltip:
                    self.active_tooltip = self.nw_btn_back.tooltip
        elif self.state == STATE_GAME_OVER:
            for btn in self.game_over_buttons:
                btn.update(mouse_pos)
                if btn.is_hovered and btn.tooltip:
                    self.active_tooltip = btn.tooltip

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
        for i, winfo in enumerate(self.saved_worlds):
            entry_y = start_y + i * 62
            load_b = Button(bx + 355, entry_y + 9, 36, 36, "", f"load_{i}", icon="play", tooltip="Enter World")
            ren_b = Button(bx + 400, entry_y + 9, 36, 36, "", f"ren_{i}", icon="rename", tooltip="Rename World")
            del_b = Button(bx + 445, entry_y + 9, 36, 36, "", f"del_{i}", icon="delete", tooltip="Delete World")
            self.world_entry_buttons.append((load_b, del_b, winfo))
            self.world_rename_buttons.append((ren_b, winfo))
        
        # Calculate max scrollable height (viewport displays ~4 entries of 62px = 248px)
        total_content_h = len(self.saved_worlds) * 62
        viewport_h = 248
        self.max_worlds_scroll = max(0.0, float(total_content_h - viewport_h))
        self.worlds_scroll_y = max(0.0, min(self.worlds_scroll_y, self.max_worlds_scroll))

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
                        if hasattr(self, "discovery"):
                            self.discovery.start()
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
                if getattr(self, "hosting_lan", False):
                    self.hosting_lan = False
                    self.state = STATE_MULTIPLAYER
                else:
                    self.state = STATE_MENU
                return None

            # Handle scrollbar click
            track_rect = pygame.Rect(SCREEN_WIDTH // 2 + 252, 275, 14, 255)
            if track_rect.collidepoint(mouse_pos) and getattr(self, "max_worlds_scroll", 0.0) > 0:
                rel_y = (mouse_pos[1] - 275) / 255.0
                self.worlds_scroll_y = max(0.0, min(rel_y * self.max_worlds_scroll, self.max_worlds_scroll))
                return None

            viewport_rect = pygame.Rect(SCREEN_WIDTH // 2 - 250, 275, 515, 255)
            scroll_y = getattr(self, "worlds_scroll_y", 0.0)

            for i, (ren_b, winfo) in enumerate(self.world_rename_buttons):
                adjusted_rect = ren_b.rect.move(0, -scroll_y)
                if viewport_rect.collidepoint(mouse_pos) and adjusted_rect.collidepoint(mouse_pos):
                    self.sound_manager.play("place")
                    self.renaming_world_target = winfo["name"]
                    self.rename_world_input = winfo["name"]
                    self.rename_error_msg = ""
                    return None

            for i, (load_b, del_b, winfo) in enumerate(self.world_entry_buttons):
                adj_load = load_b.rect.move(0, -scroll_y)
                adj_del = del_b.rect.move(0, -scroll_y)
                if viewport_rect.collidepoint(mouse_pos):
                    if adj_load.collidepoint(mouse_pos):
                        self.sound_manager.play("place")
                        return ("load_world", winfo["name"])
                    elif adj_del.collidepoint(mouse_pos):
                        try:
                            from src.world.save_manager import delete_world
                            delete_world(winfo["name"])
                            self._refresh_saved_worlds()
                            self.sound_manager.play("craft")
                        except Exception as e:
                            print(f"[Menu] Error deleting world: {e}")
                        return None

        elif self.state == STATE_NEW_WORLD:
            if getattr(self, "show_yolo_warning", False):
                if self.yolo_confirm_btn.rect.collidepoint(mouse_pos):
                    self.sound_manager.play("place")
                    self.show_yolo_warning = False
                    self.state = STATE_PLAYING
                    self.new_world_mode = MODE_LAST_MAN_STANDING if self.enabled_mods.get("last_man_standing", False) else MODE_ADVENTURE
                    cfg = {
                        "name": self.new_world_name.strip() or "Spud World",
                        "world_type": self.new_world_type,
                        "difficulty": self.new_world_diff,
                        "game_mode": self.new_world_mode
                    }
                    return ("create_world", cfg)
                elif self.yolo_cancel_btn.rect.collidepoint(mouse_pos):
                    self.sound_manager.play("place")
                    self.show_yolo_warning = False
                    self.new_world_diff = DIFFICULTY_NORMAL
                    self.nw_btn_diff.text = f"DIFFICULTY: {self.new_world_diff.upper()}"
                return None

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
                if self.new_world_diff == DIFFICULTY_EASY:
                    self.new_world_diff = DIFFICULTY_NORMAL
                elif self.new_world_diff == DIFFICULTY_NORMAL:
                    self.new_world_diff = DIFFICULTY_HARDCORE
                elif self.new_world_diff == DIFFICULTY_HARDCORE:
                    self.new_world_diff = DIFFICULTY_YOLO
                else:
                    self.new_world_diff = DIFFICULTY_EASY
                self.nw_btn_diff.text = f"DIFFICULTY: {self.new_world_diff.upper()}"
            elif self.nw_btn_create.rect.collidepoint(mouse_pos):
                self.sound_manager.play("place")
                if self.new_world_diff == DIFFICULTY_YOLO:
                    self.show_yolo_warning = True
                    return None
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
                    self._apply_audio_volumes()
                    self.save_settings()
                    return ("volume_updated", self.settings)
                elif btn.action == "vol_master_up":
                    self.settings["master_volume"] = min(1.0, round(self.settings["master_volume"] + 0.1, 2))
                    self._apply_audio_volumes()
                    self.save_settings()
                    return ("volume_updated", self.settings)
                elif btn.action == "vol_bgm_down":
                    self.settings["bgm_volume"] = max(0.0, round(self.settings["bgm_volume"] - 0.1, 2))
                    self._apply_audio_volumes()
                    self.save_settings()
                    return ("volume_updated", self.settings)
                elif btn.action == "vol_bgm_up":
                    self.settings["bgm_volume"] = min(1.0, round(self.settings["bgm_volume"] + 0.1, 2))
                    self._apply_audio_volumes()
                    self.save_settings()
                    return ("volume_updated", self.settings)
                elif btn.action == "vol_sfx_down":
                    self.settings["sfx_volume"] = max(0.0, round(self.settings["sfx_volume"] - 0.1, 2))
                    self._apply_audio_volumes()
                    self.save_settings()
                    return ("volume_updated", self.settings)
                elif btn.action == "vol_sfx_up":
                    self.settings["sfx_volume"] = min(1.0, round(self.settings["sfx_volume"] + 0.1, 2))
                    self._apply_audio_volumes()
                    self.save_settings()
                    return ("volume_updated", self.settings)
                elif btn.action == "toggle_display":
                    target_fs = not self.settings.get("fullscreen", False)
                    self.settings["fullscreen"] = target_fs
                    self._refresh_settings_button_labels()
                    self.save_settings()
                    return ("set_fullscreen", target_fs)
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
                elif btn.action == "cycle_resolution":
                    cur_r = str(self.settings.get("resolution", "1920x1080"))
                    idx = self.resolutions.index(cur_r) if cur_r in self.resolutions else 0
                    next_r = self.resolutions[(idx + 1) % len(self.resolutions)]
                    self.settings["resolution"] = next_r
                    self._refresh_settings_button_labels()
                    self.save_settings()
                    return ("set_resolution", next_r)
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
            # 1. Room Key Modal Interaction
            if getattr(self, "room_key_modal_active", False):
                if self.room_key_box_rect.collidepoint(mouse_pos):
                    return None
                if self.room_key_join_btn.rect.collidepoint(mouse_pos):
                    self.sound_manager.play("place")
                    req_key = self.room_key_input.strip()
                    sinfo = self.room_key_modal_target
                    srv_key = sinfo.get("room_key", "")
                    if srv_key and req_key != srv_key:
                        self.room_key_error = "Incorrect Room Key! Try again."
                        return None
                    self.room_key_modal_active = False
                    self.room_key_error = ""
                    self.state = STATE_PLAYING
                    return ("join_lan", sinfo.get("ip", "127.0.0.1"), req_key)
                elif self.room_key_cancel_btn.rect.collidepoint(mouse_pos):
                    self.sound_manager.play("place")
                    self.room_key_modal_active = False
                    self.room_key_error = ""
                    self.room_key_modal_target = None
                    return None
                return None

            # 2. Text input activations
            if self.ip_box_rect.collidepoint(mouse_pos):
                self.typing_ip = True
                self.typing_host_key = False
                return None
            elif getattr(self, "host_key_box_rect", pygame.Rect(0,0,0,0)).collidepoint(mouse_pos):
                self.typing_host_key = True
                self.typing_ip = False
                return None
            else:
                self.typing_ip = False
                self.typing_host_key = False

            # 3. Discovered LAN Servers 1-Click Join Buttons
            for j_btn, sinfo in getattr(self, "lan_join_buttons", []):
                if j_btn.rect.collidepoint(mouse_pos):
                    self.sound_manager.play("place")
                    if sinfo.get("is_private", False):
                        self.room_key_modal_active = True
                        self.room_key_modal_target = sinfo
                        self.room_key_input = ""
                        self.room_key_error = ""
                        return None
                    else:
                        self.state = STATE_PLAYING
                        return ("join_lan", sinfo.get("ip", "127.0.0.1"), "")

            # 4. Standard Multiplayer Menu Buttons
            for btn in self.mp_buttons:
                if btn.rect.collidepoint(mouse_pos):
                    self.sound_manager.play("place")
                    if btn.action == "host_game":
                        self.hosting_lan = True
                        self.state = STATE_WORLDS
                        self._refresh_saved_worlds()
                        return "open_worlds"
                    elif btn.action == "join_game":
                        self.state = STATE_PLAYING
                        return ("join_lan", self.join_ip_input, getattr(self, "host_room_key", ""))
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

        if self.state == STATE_MULTIPLAYER:
            if getattr(self, "room_key_modal_active", False):
                if event.key == pygame.K_BACKSPACE:
                    self.room_key_input = self.room_key_input[:-1]
                    self.room_key_error = ""
                    return True
                elif event.key == pygame.K_ESCAPE:
                    self.room_key_modal_active = False
                    self.room_key_error = ""
                    return True
                elif event.key == pygame.K_RETURN:
                    req_key = self.room_key_input.strip()
                    sinfo = self.room_key_modal_target
                    srv_key = sinfo.get("room_key", "")
                    if srv_key and req_key != srv_key:
                        self.room_key_error = "Incorrect Room Key! Try again."
                        return True
                    self.room_key_modal_active = False
                    self.room_key_error = ""
                    self.state = STATE_PLAYING
                    return ("join_lan", sinfo.get("ip", "127.0.0.1"), req_key)
                elif event.unicode and len(self.room_key_input) < 20:
                    if event.unicode.isprintable() and event.unicode not in ("\r", "\n"):
                        self.room_key_input += event.unicode
                        self.room_key_error = ""
                    return True

            if getattr(self, "typing_host_key", False):
                if event.key == pygame.K_BACKSPACE:
                    self.host_room_key = self.host_room_key[:-1]
                    return True
                elif event.key == pygame.K_RETURN:
                    self.typing_host_key = False
                    return True
                elif event.unicode and len(self.host_room_key) < 20:
                    if event.unicode.isprintable() and event.unicode not in ("\r", "\n"):
                        self.host_room_key += event.unicode
                    return True

            if self.typing_ip:
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
            mpos = getattr(self, "last_mouse_pos", None) or pygame.mouse.get_pos()
            self._render_input_mapping(target_surf, mpos)
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
            mpos = getattr(self, "last_mouse_pos", None) or pygame.mouse.get_pos()
            self._render_mods_screen(target_surf, mpos)
        elif self.state == STATE_ACHIEVEMENTS:
            mpos = getattr(self, "last_mouse_pos", None) or pygame.mouse.get_pos()
            self._render_achievements_screen(target_surf, mpos)
        elif self.state == STATE_GAME_OVER:
            self._render_game_over_screen(target_surf)

        # Floating Tooltip Banner (Screen-Space overlay)
        if getattr(self, "active_tooltip", ""):
            mpos = getattr(self, "last_mouse_pos", None) or pygame.mouse.get_pos()
            tt_text = self.active_tooltip
            tt_surf = self.font_sm.render(tt_text, True, (255, 245, 180))
            tw, th = tt_surf.get_width() + 16, tt_surf.get_height() + 10
            tx = min(mpos[0] + 12, SCREEN_WIDTH - tw - 8)
            ty = max(8, mpos[1] - th - 6)
            tip_rect = pygame.Rect(tx, ty, tw, th)
            pygame.draw.rect(target_surf, (10, 12, 18, 160), (tx + 3, ty + 3, tw, th), border_radius=6)
            pygame.draw.rect(target_surf, (15, 20, 32, 248), tip_rect, border_radius=6)
            pygame.draw.rect(target_surf, (255, 215, 60), tip_rect, 1, border_radius=6)
            target_surf.blit(tt_surf, (tx + 8, ty + 5))

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
                ("Display Resolution", "Windowed / fullscreen viewport resolution"),
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

        pw, ph = 760, 580
        px = SCREEN_WIDTH // 2 - pw // 2
        py = 40
        panel_rect = pygame.Rect(px, py, pw, ph)
        pygame.draw.rect(target_surf, (20, 24, 38, 248), panel_rect, border_radius=14)
        pygame.draw.rect(target_surf, COLOR_GOLD, panel_rect, 2, border_radius=14)
        pygame.draw.rect(target_surf, (50, 65, 95), (px + 4, py + 4, pw - 8, ph - 8), 1, border_radius=11)

        title = self.font_title.render("LAN MULTIPLAYER (1-5 PLAYERS)", True, COLOR_GOLD)
        target_surf.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, py + 14))

        sub = self.font_sm.render(f"Local Host IP: {self.local_ip}  •  Default Game Port: 25565", True, (130, 215, 240))
        target_surf.blit(sub, (SCREEN_WIDTH // 2 - sub.get_width() // 2, py + 46))

        card_w = pw - 50
        card_x = px + 25

        # =========================================================================
        # CARD 1: HOST SETTINGS
        # =========================================================================
        c1_y = py + 72
        c1_h = 112
        c1_rect = pygame.Rect(card_x, c1_y, card_w, c1_h)
        pygame.draw.rect(target_surf, (26, 32, 50, 230), c1_rect, border_radius=8)
        pygame.draw.rect(target_surf, (65, 80, 115), c1_rect, 1, border_radius=8)

        c1_title = self.font_btn.render("HOST A LOCAL LAN WORLD", True, (255, 220, 100))
        target_surf.blit(c1_title, (card_x + 18, c1_y + 10))

        key_lbl = self.font_sm.render("Host Room Password / Key (Optional):", True, (190, 205, 230))
        target_surf.blit(key_lbl, (card_x + 18, c1_y + 36))

        key_box_col = (50, 62, 92) if getattr(self, "typing_host_key", False) else (32, 38, 56)
        key_border_col = COLOR_GOLD if getattr(self, "typing_host_key", False) else (90, 110, 150)
        pygame.draw.rect(target_surf, key_box_col, self.host_key_box_rect, border_radius=6)
        pygame.draw.rect(target_surf, key_border_col, self.host_key_box_rect, 1 if not getattr(self, "typing_host_key", False) else 2, border_radius=6)

        hcursor = "_" if (getattr(self, "typing_host_key", False) and (pygame.time.get_ticks() // 500) % 2 == 0) else ""
        hk_val = getattr(self, "host_room_key", "")
        hk_display = hk_val if hk_val else ("(No Password - Public)" if not getattr(self, "typing_host_key", False) else "")
        hk_col = (255, 255, 255) if hk_val else (140, 155, 175)
        hk_surf = self.font_btn.render(f"{hk_display}{hcursor}", True, hk_col)
        target_surf.blit(hk_surf, (self.host_key_box_rect.x + 12, self.host_key_box_rect.centery - hk_surf.get_height() // 2))

        # =========================================================================
        # CARD 2: ACTIVE LOCAL LAN SERVERS (AUTO-DISCOVERED)
        # =========================================================================
        c2_y = py + 196
        c2_h = 188
        c2_rect = pygame.Rect(card_x, c2_y, card_w, c2_h)
        pygame.draw.rect(target_surf, (26, 32, 50, 230), c2_rect, border_radius=8)
        pygame.draw.rect(target_surf, (65, 80, 115), c2_rect, 1, border_radius=8)

        c2_title = self.font_btn.render("ACTIVE LOCAL LAN SERVERS (AUTO-DISCOVERED)", True, (255, 220, 100))
        target_surf.blit(c2_title, (card_x + 18, c2_y + 10))

        servers = self.discovery.get_servers() if hasattr(self, "discovery") else []
        self.lan_join_buttons = []
        list_y = c2_y + 36

        if not servers:
            pulse = int(140 + 60 * math.sin(pygame.time.get_ticks() / 300.0))
            no_srv = self.font_sm.render("Scanning local network on broadcast port 25566... (No hosts detected)", True, (pulse, pulse + 20, 220))
            target_surf.blit(no_srv, (SCREEN_WIDTH // 2 - no_srv.get_width() // 2, list_y + 45))
        else:
            for i, sinfo in enumerate(servers[:3]):
                ey = list_y + i * 46
                entry_rect = pygame.Rect(card_x + 14, ey, card_w - 28, 42)
                pygame.draw.rect(target_surf, (36, 44, 68), entry_rect, border_radius=6)
                pygame.draw.rect(target_surf, (75, 95, 135), entry_rect, 1, border_radius=6)

                s_name = sinfo.get("server_name", "Potaria LAN Server")
                s_ip = sinfo.get("ip", "127.0.0.1")
                s_port = sinfo.get("port", 25565)
                p_cnt = sinfo.get("players", 1)
                p_max = sinfo.get("max_players", 5)
                is_priv = sinfo.get("is_private", False)

                name_txt = self.font_btn.render(f"{s_name}", True, (255, 235, 120))
                target_surf.blit(name_txt, (entry_rect.x + 12, entry_rect.y + 3))

                detail_txt = self.font_sm.render(f"{s_ip}:{s_port}  •  Players: {p_cnt}/{p_max}", True, (180, 205, 235))
                target_surf.blit(detail_txt, (entry_rect.x + 14, entry_rect.y + 22))

                badge_txt = "PRIVATE (KEY)" if is_priv else "PUBLIC"
                badge_col = (255, 200, 80) if is_priv else (100, 240, 120)
                badge_surf = self.font_sm.render(badge_txt, True, badge_col)
                target_surf.blit(badge_surf, (entry_rect.right - 180, entry_rect.centery - badge_surf.get_height() // 2))

                j_btn = Button(entry_rect.right - 85, entry_rect.y + 5, 75, 32, "JOIN", ("join_server", sinfo), icon="join", tooltip="Connect to this LAN server")
                j_btn.render(target_surf, self.font_btn)
                self.lan_join_buttons.append((j_btn, sinfo))

        # =========================================================================
        # CARD 3: DIRECT IP CONNECT
        # =========================================================================
        c3_y = py + 396
        c3_h = 112
        c3_rect = pygame.Rect(card_x, c3_y, card_w, c3_h)
        pygame.draw.rect(target_surf, (26, 32, 50, 230), c3_rect, border_radius=8)
        pygame.draw.rect(target_surf, (65, 80, 115), c3_rect, 1, border_radius=8)

        c3_title = self.font_btn.render("DIRECT IP CONNECT", True, (255, 220, 100))
        target_surf.blit(c3_title, (card_x + 18, c3_y + 10))

        ip_lbl = self.font_sm.render("Target Server IP Address / Hostname:", True, (190, 205, 230))
        target_surf.blit(ip_lbl, (card_x + 18, c3_y + 36))

        ip_box_col = (50, 62, 92) if self.typing_ip else (32, 38, 56)
        ip_border_col = COLOR_GOLD if self.typing_ip else (90, 110, 150)
        pygame.draw.rect(target_surf, ip_box_col, self.ip_box_rect, border_radius=6)
        pygame.draw.rect(target_surf, ip_border_col, self.ip_box_rect, 1 if not self.typing_ip else 2, border_radius=6)

        cursor = "_" if (self.typing_ip and (pygame.time.get_ticks() // 500) % 2 == 0) else ""
        txt_surf = self.font_btn.render(f"{self.join_ip_input}{cursor}", True, (255, 255, 255))
        target_surf.blit(txt_surf, (self.ip_box_rect.x + 12, self.ip_box_rect.centery - txt_surf.get_height() // 2))

        # Render Host, Connect, and Back buttons
        for btn in self.mp_buttons:
            btn.render(target_surf, self.font_btn)

        # Room Key Modal if active
        if getattr(self, "room_key_modal_active", False):
            dim = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            dim.fill((10, 12, 22, 210))
            target_surf.blit(dim, (0, 0))

            mw, mh = 440, 220
            mx = SCREEN_WIDTH // 2 - mw // 2
            my = 230
            m_rect = pygame.Rect(mx, my, mw, mh)
            pygame.draw.rect(target_surf, (26, 32, 52, 252), m_rect, border_radius=12)
            pygame.draw.rect(target_surf, COLOR_GOLD, m_rect, 2, border_radius=12)

            m_title = self.font_title.render("ENTER ROOM KEY", True, COLOR_GOLD)
            target_surf.blit(m_title, (SCREEN_WIDTH // 2 - m_title.get_width() // 2, my + 16))

            m_sub = self.font_sm.render("This private LAN server requires a password key to join:", True, (190, 210, 240))
            target_surf.blit(m_sub, (SCREEN_WIDTH // 2 - m_sub.get_width() // 2, my + 50))

            pygame.draw.rect(target_surf, (45, 56, 88), self.room_key_box_rect, border_radius=6)
            pygame.draw.rect(target_surf, COLOR_GOLD, self.room_key_box_rect, 2, border_radius=6)

            rk_cursor = "_" if (pygame.time.get_ticks() % 800 < 400) else ""
            inp_surf = self.font_btn.render(self.room_key_input + rk_cursor, True, (255, 255, 255))
            target_surf.blit(inp_surf, (self.room_key_box_rect.x + 12, self.room_key_box_rect.centery - inp_surf.get_height() // 2))

            if getattr(self, "room_key_error", ""):
                err_surf = self.font_sm.render(self.room_key_error, True, (255, 95, 95))
                target_surf.blit(err_surf, (SCREEN_WIDTH // 2 - err_surf.get_width() // 2, my + 122))

            self.room_key_join_btn.render(target_surf, self.font_btn)
            self.room_key_cancel_btn.render(target_surf, self.font_btn)

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
            viewport_rect = pygame.Rect(SCREEN_WIDTH // 2 - 250, 275, 515, 255)
            clip_surf = pygame.Surface((viewport_rect.width, viewport_rect.height), pygame.SRCALPHA)
            scroll_y = getattr(self, "worlds_scroll_y", 0.0)

            for i, (load_b, del_b, winfo) in enumerate(self.world_entry_buttons):
                local_y = 5 + i * 62 - int(scroll_y)
                # Only render if within or near viewport
                if local_y + 54 < 0 or local_y > viewport_rect.height:
                    continue

                entry_rect = pygame.Rect(0, local_y, 495, 54)
                pygame.draw.rect(clip_surf, (36, 42, 65), entry_rect, border_radius=6)
                pygame.draw.rect(clip_surf, (70, 85, 125), entry_rect, 1, border_radius=6)

                w_name = winfo.get("name", "Unknown")
                w_type = winfo.get("world_type", "infinite").upper()
                w_diff = winfo.get("difficulty", "normal").upper()
                w_mode = winfo.get("game_mode", "adventure").replace("_", " ").upper()
                pt_str = winfo.get("playtime_str", "0h 0m")
                lp_str = winfo.get("last_played", "Never")

                name_surf = self.font_btn.render(w_name, True, (255, 235, 120))
                clip_surf.blit(name_surf, (12, local_y + 3))

                detail_str = f"{w_type}  •  {w_diff}  •  {w_mode}"
                detail_surf = self.font_sm.render(detail_str, True, (180, 195, 220))
                clip_surf.blit(detail_surf, (14, local_y + 20))

                time_str = f"Playtime: {pt_str}  •  Last Played: {lp_str}"
                time_surf = self.font_sm.render(time_str, True, (130, 215, 240))
                clip_surf.blit(time_surf, (14, local_y + 36))

                # Render button components into clipped surface
                orig_load_pos = load_b.rect.topleft
                orig_del_pos = del_b.rect.topleft
                load_b.rect.topleft = (355, local_y + 9)
                del_b.rect.topleft = (445, local_y + 9)
                load_b.render(clip_surf, self.font_btn)
                del_b.render(clip_surf, self.font_btn)
                load_b.rect.topleft = orig_load_pos
                del_b.rect.topleft = orig_del_pos

                if i < len(self.world_rename_buttons):
                    ren_b = self.world_rename_buttons[i][0]
                    orig_ren_pos = ren_b.rect.topleft
                    ren_b.rect.topleft = (400, local_y + 9)
                    ren_b.render(clip_surf, self.font_btn)
                    ren_b.rect.topleft = orig_ren_pos

            target_surf.blit(clip_surf, viewport_rect.topleft)

            # Render scrollbar track and thumb if content exceeds viewport
            if getattr(self, "max_worlds_scroll", 0.0) > 0:
                track_rect = pygame.Rect(viewport_rect.right - 10, viewport_rect.y, 8, viewport_rect.height)
                pygame.draw.rect(target_surf, (22, 26, 38), track_rect, border_radius=4)
                
                thumb_ratio = viewport_rect.height / float(len(self.saved_worlds) * 62)
                thumb_h = max(24, int(viewport_rect.height * thumb_ratio))
                thumb_y = track_rect.y + int((scroll_y / self.max_worlds_scroll) * (track_rect.height - thumb_h))
                thumb_rect = pygame.Rect(track_rect.x, thumb_y, 8, thumb_h)
                pygame.draw.rect(target_surf, (120, 140, 185), thumb_rect, border_radius=4)

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

        if self.new_world_diff == DIFFICULTY_EASY:
            diff_desc = "Easy: Starts with basic skills (Power Slash, Dash), wooden axe & 5 torches."
        elif self.new_world_diff == DIFFICULTY_NORMAL:
            diff_desc = "Normal: Starts with 1 wooden axe & 5 torches. NO starting skills."
        elif self.new_world_diff == DIFFICULTY_HARDCORE:
            diff_desc = "Hardcore: Starts with 0 items, all items scatter onto the ground on death."
        else:
            diff_desc = "YOLO: 1 Life, 1 Heart (20 HP). Death PERMANENTLY deletes world folder!"
        d_surf = self.font_sm.render(diff_desc, True, (120, 230, 160) if self.new_world_diff == DIFFICULTY_EASY else ((255, 200, 120) if self.new_world_diff != DIFFICULTY_YOLO else (255, 120, 120)))
        target_surf.blit(d_surf, (SCREEN_WIDTH // 2 - d_surf.get_width() // 2, 378))

        # Active Add-On Status indicator
        if self.enabled_mods.get("last_man_standing", False):
            m_badge = self.font_sm.render("[!] Active Add-On: Last Man Standing (PvP Friendly Fire ENABLED)", True, (255, 175, 80))
            target_surf.blit(m_badge, (SCREEN_WIDTH // 2 - m_badge.get_width() // 2, 410))

        self.nw_btn_create.render(target_surf, self.font_btn)
        self.nw_btn_back.render(target_surf, self.font_btn)

        # YOLO Warning Modal
        if getattr(self, "show_yolo_warning", False):
            dim = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            dim.fill((20, 5, 5, 210))
            target_surf.blit(dim, (0, 0))

            mw, mh = 480, 240
            mx = SCREEN_WIDTH // 2 - mw // 2
            my = 220
            m_rect = pygame.Rect(mx, my, mw, mh)
            pygame.draw.rect(target_surf, (35, 14, 18, 252), m_rect, border_radius=12)
            pygame.draw.rect(target_surf, (240, 60, 60), m_rect, 2, border_radius=12)

            warn_title = self.font_title.render("WARNING: YOLO PERMADEATH", True, (255, 75, 75))
            target_surf.blit(warn_title, (SCREEN_WIDTH // 2 - warn_title.get_width() // 2, my + 18))

            warn_lines = [
                "You have selected YOLO mode.",
                "Spud is locked to 1 HEART (20 HP) with ZERO starting skills.",
                "If you perish, your WORLD FOLDER WILL BE PERMANENTLY DELETED!",
                "Are you absolutely certain you want to proceed?"
            ]
            for idx, wline in enumerate(warn_lines):
                col = (255, 200, 200) if idx != 2 else (255, 90, 90)
                ws = self.font_sm.render(wline, True, col)
                target_surf.blit(ws, (SCREEN_WIDTH // 2 - ws.get_width() // 2, my + 58 + idx * 22))

            self.yolo_confirm_btn.render(target_surf, self.font_btn)
            self.yolo_cancel_btn.render(target_surf, self.font_btn)

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
        """Handles mouse wheel scrolling in menus (e.g. Achievements browser, Worlds list)."""
        if self.state == STATE_ACHIEVEMENTS:
            max_s = getattr(self.achievement_manager, "max_scroll", 0.0)
            self.achievements_scroll_y -= scroll_delta * 45.0
            if max_s > 0:
                self.achievements_scroll_y = max(0.0, min(self.achievements_scroll_y, max_s))
            else:
                self.achievements_scroll_y = max(0.0, self.achievements_scroll_y)
        elif self.state == STATE_WORLDS:
            if getattr(self, "max_worlds_scroll", 0.0) > 0:
                self.worlds_scroll_y -= scroll_delta * 45.0
                self.worlds_scroll_y = max(0.0, min(self.worlds_scroll_y, self.max_worlds_scroll))

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
