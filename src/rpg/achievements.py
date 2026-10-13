"""
Potaria - Achievements Engine & Toast Notification System
Loads catalog from data/achievements.json, tracks progress,
persists unlocks to saves/achievements.json, and renders in-game toast banners.
Developer: Kurados
"""

import os
import json
import time
import pygame
from src.constants import (
    SCREEN_WIDTH, SCREEN_HEIGHT, COLOR_GOLD, COLOR_WHITE,
    ACHIEVEMENTS_CATALOG, ACHIEVEMENTS_FILE
)


class AchievementToast:
    def __init__(self, achievement_data):
        self.data = achievement_data
        self.timer = 0.0
        self.duration = 4.2
        self.slide_time = 0.4
        self.width = 420
        self.height = 64
        from src.ui.theme import font_bold, font_regular
        self._font_head = font_bold(14)
        self._font_body = font_regular(12)

    def update(self, dt):
        self.timer += dt
        return self.timer >= self.duration

    def render(self, target_surf, font_title=None, font_desc=None, toast_bg=None):
        # Slide down from y = -70 to y = 20, hold, then slide back up
        if self.timer < self.slide_time:
            progress = self.timer / self.slide_time
            # Ease out
            cur_y = int(-self.height + (20 + self.height) * progress)
        elif self.timer > (self.duration - self.slide_time):
            progress = (self.duration - self.timer) / self.slide_time
            cur_y = int(-self.height + (20 + self.height) * progress)
        else:
            cur_y = 20

        cur_x = (SCREEN_WIDTH - self.width) // 2
        toast_rect = pygame.Rect(cur_x, cur_y, self.width, self.height)

        if toast_bg:
            target_surf.blit(toast_bg, (cur_x, cur_y))
        else:
            pygame.draw.rect(target_surf, (22, 28, 48, 245), toast_rect, border_radius=10)
            pygame.draw.rect(target_surf, COLOR_GOLD, toast_rect, 2, border_radius=10)
            pygame.draw.rect(target_surf, (255, 235, 120, 180), (cur_x + 6, cur_y + 4, self.width - 12, 2), border_radius=2)

        # Star icon / medal badge
        cx = cur_x + 28
        cy = cur_y + self.height // 2
        pygame.draw.circle(target_surf, (255, 215, 0), (cx, cy), 14)
        pygame.draw.circle(target_surf, (255, 245, 180), (cx, cy), 11)
        pygame.draw.circle(target_surf, (215, 160, 20), (cx, cy), 8)

        # Labels
        f_head = self._font_head
        f_body = self._font_body
        head_txt = f_head.render("ACHIEVEMENT UNLOCKED!", True, COLOR_GOLD)
        target_surf.blit(head_txt, (cur_x + 56, cur_y + 11))

        name_str = f"{self.data.get('name', 'Feat')}: {self.data.get('desc', '')}"
        if len(name_str) > 52:
            name_str = name_str[:49] + "..."
        desc_txt = f_body.render(name_str, True, (240, 240, 250))
        target_surf.blit(desc_txt, (cur_x + 56, cur_y + 34))


class AchievementManager:
    def __init__(self, catalog_path=ACHIEVEMENTS_CATALOG, save_path=ACHIEVEMENTS_FILE, sound_manager=None):
        self.catalog_path = catalog_path
        self.save_path = save_path
        self.sound_manager = sound_manager
        self.achievements = []
        self.achievements_dict = {}
        self.unlocked_ids = set()
        self.unlock_times = {}
        self.toast_queue = []
        self.current_toast = None

        self.load_catalog()
        self.load_progress()

    def load_catalog(self):
        """Loads achievements catalog definition from JSON."""
        if os.path.exists(self.catalog_path):
            try:
                with open(self.catalog_path, "r", encoding="utf-8") as f:
                    self.achievements = json.load(f)
                    for ach in self.achievements:
                        self.achievements_dict[ach["id"]] = ach
            except Exception as e:
                print(f"[AchievementManager] Failed to load catalog: {e}")
        else:
            print(f"[AchievementManager] Catalog {self.catalog_path} not found.")

    def load_progress(self):
        """Loads persistent unlocked achievements from disk."""
        if os.path.exists(self.save_path):
            try:
                with open(self.save_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    if isinstance(data, dict):
                        self.unlocked_ids = set(data.get("unlocked", []))
                        self.unlock_times = data.get("timestamps", {})
                    elif isinstance(data, list):
                        self.unlocked_ids = set(data)
            except Exception as e:
                print(f"[AchievementManager] Failed to load progress: {e}")

    def save_progress(self):
        """Saves unlocked achievements to disk."""
        try:
            os.makedirs(os.path.dirname(self.save_path), exist_ok=True)
            with open(self.save_path, "w", encoding="utf-8") as f:
                json.dump({
                    "unlocked": list(self.unlocked_ids),
                    "timestamps": self.unlock_times
                }, f, indent=2)
        except Exception as e:
            print(f"[AchievementManager] Failed to save progress: {e}")

    def unlock(self, ach_id, sound_manager=None):
        """Unlocks an achievement if not already earned, triggers sound and toast."""
        if ach_id in self.unlocked_ids:
            return False

        if ach_id not in self.achievements_dict:
            return False

        self.unlocked_ids.add(ach_id)
        self.unlock_times[ach_id] = time.time()
        self.save_progress()

        # Queue popup toast
        ach_data = self.achievements_dict[ach_id]
        toast = AchievementToast(ach_data)
        if not self.current_toast:
            self.current_toast = toast
        else:
            self.toast_queue.append(toast)

        snd = sound_manager or self.sound_manager
        if snd and hasattr(snd, "play"):
            snd.play("craft")

        print(f"[Achievements] UNLOCKED: {ach_data.get('name')} - {ach_data.get('desc')}")
        return True

    def is_unlocked(self, ach_id):
        return ach_id in self.unlocked_ids

    def get_progress(self):
        total = len(self.achievements)
        unlocked = len(self.unlocked_ids)
        pct = (unlocked / float(total) * 100.0) if total > 0 else 0.0
        return unlocked, total, pct

    def update(self, dt):
        """Advances active toast timer and pops next toast from queue."""
        if self.current_toast:
            done = self.current_toast.update(dt)
            if done:
                if self.toast_queue:
                    self.current_toast = self.toast_queue.pop(0)
                else:
                    self.current_toast = None

    def render_toast(self, target_surf, font_title, font_desc, toast_bg=None):
        """Renders currently active popup toast banner."""
        if self.current_toast:
            self.current_toast.render(target_surf, font_title, font_desc, toast_bg)

    def render_browser(self, target_surf, mouse_pos, scroll_y=0):
        """Renders full-screen or modal achievements browser."""
        pw, ph = 760, 560
        px = (SCREEN_WIDTH - pw) // 2
        py = 55
        panel_rect = pygame.Rect(px, py, pw, ph)

        # Panel frame
        pygame.draw.rect(target_surf, (24, 28, 46, 250), panel_rect, border_radius=14)
        pygame.draw.rect(target_surf, COLOR_GOLD, panel_rect, 2, border_radius=14)

        # Title (Centralized Typography Theme)
        from src.ui.theme import font_title, font_bold, font_regular, font_compact
        font_header = font_title(24)
        font_card_t = font_bold(16)
        font_card_d = font_regular(13)
        font_badge = font_compact(11)

        title = font_header.render("POTARIA ACHIEVEMENTS", True, COLOR_GOLD)
        target_surf.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, py + 18))

        # Progress bar
        unlocked, total, pct = self.get_progress()
        sub = font_card_d.render(f"Progress: {unlocked} / {total} Completed ({int(pct)}%)", True, (220, 230, 245))
        target_surf.blit(sub, (SCREEN_WIDTH // 2 - sub.get_width() // 2, py + 52))

        bar_x = SCREEN_WIDTH // 2 - 160
        bar_y = py + 74
        bar_w = 320
        bar_h = 10
        pygame.draw.rect(target_surf, (15, 18, 30), (bar_x, bar_y, bar_w, bar_h), border_radius=4)
        if pct > 0:
            fill_w = int(bar_w * (pct / 100.0))
            pygame.draw.rect(target_surf, (255, 215, 0), (bar_x, bar_y, fill_w, bar_h), border_radius=4)
        pygame.draw.rect(target_surf, (100, 120, 160), (bar_x, bar_y, bar_w, bar_h), 1, border_radius=4)

        # Achievement Cards List (2 Columns of cards)
        col_w = 330
        card_h = 58
        start_y = py + 92
        gap_x = 24
        gap_y = 8
        row_height = card_h + gap_y

        col1_x = px + 35
        col2_x = col1_x + col_w + gap_x

        total_rows = (len(self.achievements) + 1) // 2
        total_content_h = total_rows * row_height
        viewport_h = ph - 110  # from start_y to py + ph - 18
        max_scroll = max(0, total_content_h - viewport_h + 10)
        clamped_scroll = max(0, min(scroll_y, max_scroll))
        self.max_scroll = max_scroll
        self.scroll_y = clamped_scroll

        # Cards Viewport & Clipping
        cards_viewport = pygame.Rect(px + 20, start_y, pw - 40, viewport_h)
        old_clip = target_surf.get_clip()
        target_surf.set_clip(cards_viewport)

        for idx, ach in enumerate(self.achievements):
            col = idx % 2
            row = idx // 2
            cx = col1_x if col == 0 else col2_x
            cy = start_y + row * row_height - clamped_scroll

            # Cull cards entirely outside viewport
            if cy + card_h < start_y or cy > start_y + viewport_h:
                continue

            card_rect = pygame.Rect(cx, cy, col_w, card_h)
            is_unl = self.is_unlocked(ach["id"])
            is_hover = card_rect.collidepoint(mouse_pos) and cards_viewport.collidepoint(mouse_pos)

            if is_unl:
                bg_col = (36, 44, 70) if not is_hover else (48, 60, 95)
                bd_col = COLOR_GOLD if is_hover else (120, 150, 200)
            else:
                bg_col = (20, 24, 38) if not is_hover else (28, 34, 52)
                bd_col = (60, 70, 90)

            pygame.draw.rect(target_surf, bg_col, card_rect, border_radius=8)
            pygame.draw.rect(target_surf, bd_col, card_rect, 2 if is_hover else 1, border_radius=8)

            # Medal Icon
            icon_cx = cx + 24
            icon_cy = cy + card_h // 2
            if is_unl:
                pygame.draw.circle(target_surf, (255, 215, 0), (icon_cx, icon_cy), 14)
                pygame.draw.circle(target_surf, (255, 240, 150), (icon_cx, icon_cy), 10)
                pygame.draw.circle(target_surf, (200, 140, 20), (icon_cx, icon_cy), 6)
            else:
                pygame.draw.circle(target_surf, (55, 60, 75), (icon_cx, icon_cy), 14)
                pygame.draw.circle(target_surf, (35, 40, 50), (icon_cx, icon_cy), 10)

            # Title
            t_col = (255, 235, 120) if is_unl else (140, 145, 160)
            name_t = font_card_t.render(ach.get("name", "Achievement"), True, t_col)
            target_surf.blit(name_t, (cx + 46, cy + 8))

            # Status badge
            badge_txt = "[UNLOCKED]" if is_unl else "[LOCKED]"
            b_col = (100, 230, 120) if is_unl else (120, 125, 140)
            badge = font_badge.render(badge_txt, True, b_col)
            target_surf.blit(badge, (cx + col_w - badge.get_width() - 8, cy + 9))

            # Description
            desc_str = ach.get("desc", "")
            if len(desc_str) > 38:
                desc_str = desc_str[:35] + "..."
            d_col = (220, 225, 235) if is_unl else (100, 110, 125)
            desc_t = font_card_d.render(desc_str, True, d_col)
            target_surf.blit(desc_t, (cx + 46, cy + 32))

        # Restore previous clipping rectangle
        target_surf.set_clip(old_clip)

        # Draw Scrollbar Track & Thumb
        if max_scroll > 0:
            track_w = 8
            track_x = px + pw - 24
            track_y = start_y
            track_h = viewport_h
            pygame.draw.rect(target_surf, (15, 18, 30), (track_x, track_y, track_w, track_h), border_radius=4)
            pygame.draw.rect(target_surf, (60, 70, 90), (track_x, track_y, track_w, track_h), 1, border_radius=4)

            thumb_h = max(24, int(track_h * (viewport_h / float(total_content_h))))
            thumb_ratio = clamped_scroll / float(max_scroll)
            thumb_y = track_y + int((track_h - thumb_h) * thumb_ratio)
            thumb_rect = pygame.Rect(track_x, thumb_y, track_w, thumb_h)
            thumb_hover = thumb_rect.collidepoint(mouse_pos)

            pygame.draw.rect(target_surf, (255, 215, 0) if thumb_hover else (180, 150, 60), thumb_rect, border_radius=4)
