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
        self.width = 380
        self.height = 190
        self.x = (SCREEN_WIDTH - self.width) // 2
        self.y = (SCREEN_HEIGHT - self.height) // 2 - 20

        # Fonts
        self.font_title = pygame.font.Font(None, 24)
        self.font_main = pygame.font.Font(None, 20)
        self.font_sm = pygame.font.Font(None, 16)

    def start(self, fish_id=None, caught_count=1):
        """Initializes and begins the fishing tug-of-war battle."""
        if not fish_id:
            fish_id = random.choice(list(PINOY_FISH_DATA.keys()))

        data = PINOY_FISH_DATA.get(fish_id, {
            "name": ITEM_REGISTRY.get(fish_id, {}).get("name", fish_id.replace("_", " ").title()),
            "rarity": "rare",
            "clicks": 15,
            "thrash_rate": 0.40
        })

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
        self.time_limit = 16.0
        self.time_remaining = self.time_limit
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

    def handle_click(self, is_right_click=True):
        """Processes player click input during the battle."""
        if not self.is_active or self.result is not None:
            return False

        if not is_right_click:
            # Reeling specifically responds to right-clicking
            return False

        self.ui_scale_pulse = 0.15
        progress_per_click = 100.0 / float(self.target_clicks)

        if self.is_thrashing:
            # Reeling while fish is thrashing spikes line tension!
            self.tension += 14.0
            self.reeling_progress += progress_per_click * 0.45
            if self.sound_manager:
                self.sound_manager.play("hit_block")
        else:
            # Reeling during calm water makes steady progress with mild tension
            self.tension = min(95.0, self.tension + 3.5)
            self.reeling_progress += progress_per_click
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
        panel_surf.fill((18, 24, 38, 245))
        surface.blit(panel_surf, (self.x, self.y))

        # Borders
        border_col = (215, 175, 75) if not self.is_thrashing else (235, 75, 75)
        pygame.draw.rect(surface, border_col, box_rect, 2, border_radius=6)
        pygame.draw.rect(surface, (10, 14, 22), box_rect.inflate(-4, -4), 1, border_radius=4)

        # Title & Rarity
        r_col = RARITY_COLORS.get(self.rarity, (220, 220, 220))
        title_txt = f"FISHING BATTLE: {self.fish_name.upper()}"
        rendered_title = self.font_title.render(title_txt, True, r_col)
        surface.blit(rendered_title, (self.x + 16, self.y + 12))

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

        icon_x = self.x + self.width - 55
        icon_y = self.y + 12
        pygame.draw.rect(surface, (28, 36, 54), (icon_x - 4, icon_y - 2, 40, 32), border_radius=4)
        pygame.draw.rect(surface, (70, 90, 130), (icon_x - 4, icon_y - 2, 40, 32), 1, border_radius=4)
        if icon_surf:
            sw_scale = pygame.transform.scale(icon_surf, (32, 24))
            surface.blit(sw_scale, (icon_x, icon_y + 2))

        # Fish Status Text
        status_txt = "FISH IS THRASHING! [EASE OFF!]" if self.is_thrashing else "FISH IS CALM [RIGHT-CLICK TO REEL!]"
        status_col = (255, 95, 95) if self.is_thrashing else (110, 240, 130)
        rendered_status = self.font_main.render(status_txt, True, status_col)
        surface.blit(rendered_status, (self.x + 16, self.y + 40))

        # 1. Reeling Progress Bar
        bar_x = self.x + 16
        bar_w = self.width - 32
        p_y = self.y + 68
        pygame.draw.rect(surface, (12, 16, 26), (bar_x, p_y, bar_w, 20), border_radius=4)
        pygame.draw.rect(surface, (60, 80, 115), (bar_x, p_y, bar_w, 20), 1, border_radius=4)
        fill_w = int((self.reeling_progress / 100.0) * (bar_w - 4))
        if fill_w > 0:
            p_fill_col = (65, 215, 120) if self.reeling_progress < 85 else (255, 215, 60)
            pygame.draw.rect(surface, p_fill_col, (bar_x + 2, p_y + 2, fill_w, 16), border_radius=3)
        prog_txt = f"REEL PROGRESS: {int(self.reeling_progress)}% ({self.clicks_done}/{self.target_clicks} Reeled)"
        rendered_prog = self.font_sm.render(prog_txt, True, (255, 255, 255))
        surface.blit(rendered_prog, (bar_x + 8, p_y + 3))

        # 2. Line Tension Meter
        t_y = self.y + 104
        pygame.draw.rect(surface, (12, 16, 26), (bar_x, t_y, bar_w, 20), border_radius=4)
        pygame.draw.rect(surface, (60, 80, 115), (bar_x, t_y, bar_w, 20), 1, border_radius=4)
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

        # Timer & Controls Instruction Footer
        timer_col = (255, 225, 90) if self.time_remaining > 4.0 else (255, 80, 80)
        time_txt = f"Time Remaining: {self.time_remaining:.1f}s"
        rendered_time = self.font_sm.render(time_txt, True, timer_col)
        surface.blit(rendered_time, (self.x + 16, self.y + 140))

        ctrl_txt = "[TAP RIGHT-CLICK TO REEL IN] • Taking enemy damage cancels battle!"
        rendered_ctrl = self.font_sm.render(ctrl_txt, True, (175, 195, 225))
        surface.blit(rendered_ctrl, (self.x + 16, self.y + 162))
