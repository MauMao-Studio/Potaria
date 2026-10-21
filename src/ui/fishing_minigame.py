"""
Potaria - 2D Fishing Battle Mini-Game
Interactive right-click tug-of-war mini-game against fish tension.
Developer: Kurados
"""

import math
import random
import pygame
from src.constants import SCREEN_WIDTH, SCREEN_HEIGHT, RARITY_COLORS
from src.ui.inventory import ITEM_REGISTRY

PINOY_FISH_DATA = {
    "raw_dilis": {"name": "Dilis", "rarity": "common", "clicks": 7, "thrash_rate": 0.25},
    "raw_tilapia": {"name": "Tilapia", "rarity": "common", "clicks": 8, "thrash_rate": 0.30},
    "raw_bangus": {"name": "Bangus", "rarity": "uncommon", "clicks": 11, "thrash_rate": 0.35},
    "raw_galunggong": {"name": "Galunggong", "rarity": "uncommon", "clicks": 12, "thrash_rate": 0.35},
    "raw_hito": {"name": "Hito", "rarity": "uncommon", "clicks": 13, "thrash_rate": 0.40},
    "raw_maya_maya": {"name": "Maya-Maya", "rarity": "rare", "clicks": 18, "thrash_rate": 0.45},
    "raw_tambakol": {"name": "Tambakol", "rarity": "rare", "clicks": 20, "thrash_rate": 0.50},
    "raw_tanigue": {"name": "Tanigue", "rarity": "epic", "clicks": 25, "thrash_rate": 0.55},
    "raw_dalagang_bukid": {"name": "Dalagang Bukid", "rarity": "epic", "clicks": 26, "thrash_rate": 0.55},
    "raw_lapu_lapu": {"name": "Lapu-Lapu", "rarity": "epic", "clicks": 28, "thrash_rate": 0.60},
}


class FishingBattleMiniGame:
    def __init__(self, asset_factory, sound_manager):
        self.asset_factory = asset_factory
        self.sound_manager = sound_manager

        self.is_active = False
        self.fish_id = "raw_bangus"
        self.fish_name = "Bangus"
        self.rarity = "uncommon"
        self.caught_count = 1

        self.reeling_progress = 0.0  # 0.0 to 100.0%
        self.tension = 20.0          # 0.0 to 100.0% (line snaps at 100%)
        self.target_clicks = 12
        self.clicks_done = 0

        self.is_thrashing = False
        self.thrash_timer = 2.0
        self.time_limit = 15.0
        self.time_remaining = 15.0
        self.result = None  # None, "caught", "escaped", "cancelled"

        self.anim_time = 0.0
        self.ui_scale_pulse = 0.0

        # UI Positioning (centered modal)
        self.width = 420
        self.height = 210
        self.x = (SCREEN_WIDTH - self.width) // 2
        self.y = (SCREEN_HEIGHT - self.height) // 2 - 20

        # Fonts (Centralized Typography Theme)
        from src.ui.theme import font_bold, font_semibold, font_compact
        self.font_title = font_bold(20)
        self.font_main = font_semibold(16)
        self.font_sm = font_compact(12)

    def start(self, fish_id=None, caught_count=1):
        """Initializes and begins the fishing tug-of-war battle."""
        if not fish_id:
            fish_id = random.choice(list(PINOY_FISH_DATA.keys()))

        if fish_id in PINOY_FISH_DATA:
            data = PINOY_FISH_DATA[fish_id]
            self.catch_category = "fish"
        else:
            item_data = ITEM_REGISTRY.get(fish_id, {})
            name = item_data.get("name", fish_id.replace("_", " ").title())
            rarity = item_data.get("rarity", "common")

            if fish_id in ("dirt_clod", "old_boot", "rusty_can", "seaweed", "driftwood"):
                data = {"name": name, "rarity": "common", "clicks": 5, "thrash_rate": 0.05}
                self.catch_category = "junk"
            elif "skillbook" in fish_id or "book" in fish_id:
                data = {"name": name, "rarity": "epic", "clicks": 24, "thrash_rate": 0.52}
                self.catch_category = "grand_prize"
            elif item_data.get("cat") in ("weapon", "armor_head", "armor_chest", "armor_legs", "accessory"):
                clicks = 18 if rarity == "epic" else (14 if rarity == "rare" else 10)
                data = {"name": name, "rarity": rarity, "clicks": clicks, "thrash_rate": 0.40}
                self.catch_category = "treasure"
            else:
                data = {"name": name, "rarity": rarity, "clicks": 6, "thrash_rate": 0.08}
                self.catch_category = "ingredient"

        self.fish_id = fish_id
        self.fish_name = data["name"]
        self.rarity = data["rarity"]
        self.caught_count = max(1, caught_count)
        self.target_clicks = max(5, data["clicks"])
        self.clicks_done = 0

        self.reeling_progress = 0.0
        self.tension = 25.0
        self.is_thrashing = False
        self.thrash_timer = random.uniform(1.2, 2.5)

        # Dynamic time duration based on rarity / tier
        rarity_limits = {
            "common": 8.5,
            "uncommon": 10.0,
            "rare": 11.5,
            "epic": 13.0,
            "mythic": 14.5,
            "legendary": 15.0,
            "ancient": 16.0,
        }
        self.time_limit = rarity_limits.get(self.rarity, 10.0)
        if getattr(self, "catch_category", "") == "junk":
            self.time_limit = 7.5
        self.time_remaining = self.time_limit
        self.max_time = self.time_limit
        self.perfect_timing_flash = 0.0
        self.result = None
        self.is_active = True
        self.ui_scale_pulse = 0.25

        if self.sound_manager:
            self.sound_manager.play("swing")

    def cancel(self):
        """Cancels mini-game immediately (e.g. when player takes damage)."""
        if self.is_active:
            self.is_active = False
            self.result = "cancelled"

    def handle_click(self, is_right_click=True, player=None):
        """Processes player click input during the battle."""
        if not self.is_active or self.result is not None:
            return False

        if not is_right_click:
            # Reeling specifically responds to right-clicking
            return False

        self.ui_scale_pulse = 0.15
        progress_per_click = 100.0 / float(self.target_clicks)
        if player and hasattr(player, "get_meal_buff_val"):
            fish_bonus = player.get_meal_buff_val("fishing_power")
            if fish_bonus > 0:
                progress_per_click *= (1.0 + fish_bonus)

        if self.is_thrashing:
            # Reeling while fish is thrashing spikes line tension!
            self.tension += 14.0
            self.reeling_progress += progress_per_click * 0.45
            if self.sound_manager:
                self.sound_manager.play("hit_block")
        else:
            # Reeling during calm water makes steady progress with mild tension
            # Sweet spot zone: 30% to 70% line tension rewards optimal timing with +35% reel progress
            if 30.0 <= self.tension <= 70.0:
                timing_mult = 1.35
                self.perfect_timing_flash = 0.35
            else:
                timing_mult = 1.0

            self.tension = min(95.0, self.tension + 3.5)
            self.reeling_progress += progress_per_click * timing_mult
            self.clicks_done += 1
            if self.sound_manager:
                self.sound_manager.play("craft")

        if self.reeling_progress >= 100.0:
            self.reeling_progress = 100.0
            self.is_active = False
            self.result = "caught"
            if self.sound_manager:
                self.sound_manager.play("pickup")
            return True

        if self.tension >= 100.0:
            self.tension = 100.0
            self.is_active = False
            self.result = "escaped"
            if self.sound_manager:
                self.sound_manager.play("dig_dirt")
            return True

        return True

    def update(self, dt):
        """Updates fish AI, tension decay, thrashing cycles, and timers."""
        if not self.is_active:
            return self.result

        self.anim_time += dt
        self.time_remaining -= dt

        if self.ui_scale_pulse > 0:
            self.ui_scale_pulse = max(0.0, self.ui_scale_pulse - dt * 2.0)
        if self.perfect_timing_flash > 0:
            self.perfect_timing_flash = max(0.0, self.perfect_timing_flash - dt)

        # Thrash state switching
        self.thrash_timer -= dt
        if self.thrash_timer <= 0:
            self.is_thrashing = not self.is_thrashing
            if self.is_thrashing:
                self.thrash_timer = random.uniform(1.0, 2.2)
                if self.sound_manager:
                    self.sound_manager.play("swing")
            else:
                self.thrash_timer = random.uniform(1.5, 3.0)

        # Tension physics
        if self.is_thrashing:
            # Fish pulls against the line
            self.tension += 15.0 * dt
            # Reeling slips back slightly under thrashing pressure
            self.reeling_progress = max(0.0, self.reeling_progress - 4.0 * dt)
        else:
            # Tension relaxes naturally when calm
            self.tension = max(10.0, self.tension - 28.0 * dt)

        # Bounds checks
        if self.tension >= 100.0:
            self.is_active = False
            self.result = "escaped"
            if self.sound_manager:
                self.sound_manager.play("dig_dirt")
            return "escaped"

        if self.time_remaining <= 0:
            self.is_active = False
            self.result = "escaped"
            if self.sound_manager:
                self.sound_manager.play("dig_dirt")
            return "escaped"

        return None

    def render(self, surface):
        """Draws the retro pixel-art fishing battle window with meters and prompts."""
        if not self.is_active and self.result is None:
            return

        # Semi-transparent background dim
        dim_surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        dim_surf.fill((0, 0, 0, 75))
        surface.blit(dim_surf, (0, 0))

        # Main Box
        box_rect = pygame.Rect(self.x, self.y, self.width, self.height)
        panel_surf = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        panel_surf.fill((16, 22, 34, 248))
        surface.blit(panel_surf, (self.x, self.y))

        # Borders with Danger Thrash / Snap Warning
        is_danger = (self.tension >= 80.0 or self.is_thrashing)
        border_col = (245, 75, 75) if is_danger else (215, 175, 75)
        pygame.draw.rect(surface, border_col, box_rect, 2, border_radius=6)
        pygame.draw.rect(surface, (10, 14, 22), box_rect.inflate(-4, -4), 1, border_radius=4)
        if self.tension >= 80.0:
            danger_pulse = (int(self.anim_time * 8.0) % 2) * 2
            pygame.draw.rect(surface, (255, 50, 50), box_rect.inflate(danger_pulse, danger_pulse), 1, border_radius=7)

        # Title & Rarity
        r_col = RARITY_COLORS.get(self.rarity, (220, 220, 220))
        if getattr(self, "catch_category", "") == "junk":
            title_txt = f"REELING IN JUNK: {self.fish_name.upper()}"
        elif getattr(self, "catch_category", "") == "treasure":
            title_txt = f"TREASURE HOOKED: {self.fish_name.upper()}"
        elif getattr(self, "catch_category", "") == "grand_prize":
            title_txt = f"GRAND PRIZE HOOKED: {self.fish_name.upper()}"
        else:
            title_txt = f"FISHING BATTLE: {self.fish_name.upper()}"
        rendered_title = self.font_title.render(title_txt, True, r_col)
        surface.blit(rendered_title, (self.x + 18, self.y + 14))

        # Fish sprite or icon
        icon_surf = None
        if hasattr(self.asset_factory, "mobs"):
            mkey = self.fish_id.replace("raw_", "")
            mob_val = self.asset_factory.mobs.get(mkey)
            if isinstance(mob_val, list) and mob_val:
                f_idx = int(self.anim_time * 6.0) % len(mob_val)
                icon_surf = mob_val[f_idx]
            elif isinstance(mob_val, pygame.Surface):
                icon_surf = mob_val
        if not icon_surf and hasattr(self.asset_factory, "items"):
            icon_surf = self.asset_factory.items.get(self.fish_id)

        icon_x = self.x + self.width - 58
        icon_y = self.y + 12
        pygame.draw.rect(surface, (28, 36, 54), (icon_x - 4, icon_y - 2, 44, 34), border_radius=4)
        pygame.draw.rect(surface, (70, 90, 130), (icon_x - 4, icon_y - 2, 44, 34), 1, border_radius=4)
        if icon_surf:
            iw, ih = icon_surf.get_size()
            scale_fac = min(36.0 / max(1, iw), 26.0 / max(1, ih))
            target_w = max(4, int(iw * scale_fac))
            target_h = max(4, int(ih * scale_fac))
            sw_scale = pygame.transform.scale(icon_surf, (target_w, target_h))
            surface.blit(sw_scale, (icon_x - 4 + (44 - target_w) // 2, icon_y - 2 + (34 - target_h) // 2))

        # Fish Status Text
        if getattr(self, "catch_category", "") == "junk":
            status_txt = "HEAVY LINE DRAG! [EASE OFF!]" if self.is_thrashing else "REELING IN RIVER DEBRIS [RIGHT-CLICK TO REEL!]"
        else:
            status_txt = "FISH IS THRASHING! [EASE OFF!]" if self.is_thrashing else "FISH IS CALM [RIGHT-CLICK TO REEL!]"
        status_col = (255, 95, 95) if self.is_thrashing else (110, 240, 130)
        rendered_status = self.font_main.render(status_txt, True, status_col)
        surface.blit(rendered_status, (self.x + 18, self.y + 44))

        # 1. Reeling Progress Bar
        bar_x = self.x + 18
        bar_w = self.width - 36
        p_y = self.y + 72
        pygame.draw.rect(surface, (12, 16, 26), (bar_x, p_y, bar_w, 20), border_radius=4)
        pygame.draw.rect(surface, (60, 80, 115), (bar_x, p_y, bar_w, 20), 1, border_radius=4)
        fill_w = int((self.reeling_progress / 100.0) * (bar_w - 4))
        if fill_w > 0:
            p_fill_col = (65, 215, 120) if self.reeling_progress < 85 else (255, 215, 60)
            pygame.draw.rect(surface, p_fill_col, (bar_x + 2, p_y + 2, fill_w, 16), border_radius=3)
        prog_txt = f"REEL PROGRESS: {int(self.reeling_progress)}%"
        rendered_prog = self.font_sm.render(prog_txt, True, (255, 255, 255))
        surface.blit(rendered_prog, (bar_x + 8, p_y + 3))

        # 2. Line Tension Meter
        t_y = self.y + 104
        pygame.draw.rect(surface, (12, 16, 26), (bar_x, t_y, bar_w, 20), border_radius=4)
        pygame.draw.rect(surface, (60, 80, 115), (bar_x, t_y, bar_w, 20), 1, border_radius=4)

        # Sweet Spot Zone Indicator (30% to 70% line tension)
        sweet_start = bar_x + 2 + int(0.30 * (bar_w - 4))
        sweet_width = int(0.40 * (bar_w - 4))
        sweet_surf = pygame.Surface((sweet_width, 16), pygame.SRCALPHA)
        sweet_surf.fill((45, 210, 110, 50))
        surface.blit(sweet_surf, (sweet_start, t_y + 2))
        pygame.draw.rect(surface, (80, 230, 130), (sweet_start, t_y + 2, sweet_width, 16), 1)

        ten_fill_w = int((self.tension / 100.0) * (bar_w - 4))
        if ten_fill_w > 0:
            if self.tension < 50:
                t_col = (70, 180, 245)
            elif self.tension < 80:
                t_col = (255, 195, 45)
            else:
                t_col = (255, 65, 65)
            pygame.draw.rect(surface, t_col, (bar_x + 2, t_y + 2, ten_fill_w, 16), border_radius=3)
        ten_txt = f"LINE TENSION: {int(self.tension)}% {'[DANGER SNAP!]' if self.tension >= 80 else ''}"
        rendered_ten = self.font_sm.render(ten_txt, True, (255, 255, 255))
        surface.blit(rendered_ten, (bar_x + 8, t_y + 3))

        # Sweet spot bonus flash indicator
        if getattr(self, "perfect_timing_flash", 0.0) > 0:
            flash_txt = self.font_sm.render("SWEET SPOT! (+35% PROGRESS)", True, (110, 255, 160))
            surface.blit(flash_txt, (bar_x + bar_w - flash_txt.get_width() - 4, t_y - 14))

        # 3. Dynamic Countdown Timer Bar
        tb_y = self.y + 138
        pygame.draw.rect(surface, (12, 16, 26), (bar_x, tb_y, bar_w, 12), border_radius=3)
        pygame.draw.rect(surface, (60, 80, 115), (bar_x, tb_y, bar_w, 12), 1, border_radius=3)
        time_ratio = max(0.0, min(1.0, self.time_remaining / max(0.1, getattr(self, "max_time", self.time_limit))))
        time_bar_w = int(time_ratio * (bar_w - 4))
        if time_bar_w > 0:
            tb_col = (80, 220, 110) if time_ratio > 0.45 else ((255, 210, 50) if time_ratio > 0.2 else (255, 65, 65))
            pygame.draw.rect(surface, tb_col, (bar_x + 2, tb_y + 2, time_bar_w, 8), border_radius=2)

        # Timer & Controls Instruction Footer
        timer_col = (255, 225, 90) if self.time_remaining > 4.0 else (255, 80, 80)
        time_txt = f"Time Remaining: {self.time_remaining:.1f}s"
        rendered_time = self.font_sm.render(time_txt, True, timer_col)
        surface.blit(rendered_time, (self.x + 18, self.y + 158))

        ctrl_txt = "[TAP RIGHT-CLICK TO REEL IN] - Taking enemy damage cancels battle!"
        rendered_ctrl = self.font_sm.render(ctrl_txt, True, (175, 195, 225))
        surface.blit(rendered_ctrl, (self.x + 18, self.y + 180))
