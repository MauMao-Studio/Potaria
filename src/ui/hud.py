"""
Potaria - Heads-Up Display (HUD) & Party Interface
Renders health hearts, MP bar, EXP bar, hotbar slots, skill bar cooldowns,
LAN multiplayer party members, text chat, toggleable mini-map, and rich item tooltips.
Developer: Kurados
"""

import math
import pygame
from src.constants import (
    SCREEN_WIDTH, SCREEN_HEIGHT, SLOT_SIZE, SLOT_PADDING,
    HOTBAR_SLOTS, INV_COLS, INV_ROWS, SCALED_TILE, COLOR_GOLD,
    RARITY_COLORS, RARITY_COMMON, RARITY_EPIC, RARITY_LEGENDARY, RARITY_MYTHIC, RARITY_ANCIENT,
    CAT_TOOL, CAT_WEAPON
)
from src.ui.inventory import ITEM_REGISTRY, ItemStack
from src.rpg.equipment import get_item_equipment_slot, get_equipped_item_for_slot, is_item_already_equipped
from src.rpg.skills import SKILL_DEFINITIONS
from src.ui.minimap import MiniMap

class HUD:
    def __init__(self, asset_factory):
        self.asset_factory = asset_factory
        
        self.heart_full = pygame.transform.scale(asset_factory.ui["heart_full"], (22, 22))
        self.heart_empty = pygame.transform.scale(asset_factory.ui["heart_empty"], (22, 22))
        self.slot_frame = asset_factory.ui["slot_frame"]
        self.slot_selected = asset_factory.ui["slot_selected"]
        self.reticle = pygame.transform.scale(asset_factory.ui["reticle"], (SCALED_TILE, SCALED_TILE))
        self.bubble_full = asset_factory.ui.get("bubble_full")
        self.bubble_empty = asset_factory.ui.get("bubble_empty")
        self.bubble_pop = asset_factory.ui.get("bubble_pop")

        # MiniMap component (Corner Radar & Expanded Map)
        self.minimap = MiniMap()

        # Celestial Clock Widget Icons
        sun_raw = asset_factory.environment.get("sun") if hasattr(asset_factory, "environment") else None
        moon_raw = asset_factory.environment.get("moon") if hasattr(asset_factory, "environment") else None
        self.clock_sun_icon = pygame.transform.scale(sun_raw, (16, 16)) if sun_raw else None
        self.clock_moon_icon = pygame.transform.scale(moon_raw, (16, 16)) if moon_raw else None

        # Fonts (Centralized Typography Theme)
        from src.ui.theme import font_semibold, font_compact, font_bold, font_regular
        self.font = font_semibold(13)
        self.font_sm = font_compact(11)
        self.font_lg = font_bold(16)
        self.font_bold = font_bold(12)
        self.font_lore = font_regular(12)

        # Pre-rendered reticle variants (avoids copying & blending every frame)
        self.reticle_in_reach = self.reticle
        self.reticle_out_of_reach = self.reticle.copy()
        self.reticle_out_of_reach.fill((255, 60, 60, 120), special_flags=pygame.BLEND_RGBA_MULT)

        # Pre-rendered hotbar key hints (1..9, 0)
        self.cached_key_hints = [self.font_sm.render(str((col + 1) % 10), True, (130, 140, 160)) for col in range(10)]

        # Pre-allocated gauge surface
        self.gauge_bg = pygame.Surface((26, 5), pygame.SRCALPHA)
        self.gauge_bg.fill((16, 20, 30, 210))

        # Cached item count glyphs and HUD text surfaces
        self._cached_count_surfs = {}
        self._cached_hp_key = None
        self._cached_hp_surf = None
        self._cached_hp_shadow = None
        self._cached_mp_key = None
        self._cached_mp_surf = None
        self._last_hovered_slot = None
        self._last_mouse_pos = (0, 0)

        # Chat & Console input state
        self.chat_active = False
        self.chat_input_text = ""
        self.local_chat_history = []
        self.tooltip_mode = "detailed"
        self._hovered_food_buff = None

    def render(self, target_surf, player, inventory, crafting_system, camera, mouse_x, mouse_y, world=None, combat=None, lan_client=None, render_dragged=True, sky=None, character_panel=None, render_tooltips=True):
        # 1. Health & Mana (Top Right)
        self._render_hp_and_mp(target_surf, player)

        # 2. Mini-Map (Corner Radar or Overview Map toggled via [M])
        if world and combat:
            self.minimap.render(target_surf, world, player, combat, lan_client)

        # 2.5. In-Game Clock / Celestial Time Widget
        if sky:
            self._render_clock_widget(target_surf, sky)
        elif world and hasattr(world, "day_night_cycle") and world.day_night_cycle:
            self._render_clock_widget(target_surf, world.day_night_cycle)

        # 3. Notification Banner (Learned Skill / Event Notifications)
        if getattr(inventory, "last_learned_message", None):
            self._render_notification_banner(target_surf, inventory.last_learned_message)

        # 4. Inventory Slots (Hotbar & Backpack)
        hovered_slot = self._render_inventory(target_surf, inventory, mouse_x, mouse_y, player=player)
        self._last_hovered_slot = hovered_slot if (hovered_slot and hovered_slot.data) else None
        self._last_mouse_pos = (mouse_x, mouse_y)

        # 5. Quick Skill Bar with Cooldown Overlays (Bottom Center)
        self._render_skill_bar(target_surf, player)

        # 5.5. Active Food Buffs HUD Widget (Bottom Left)
        self._render_food_buffs(target_surf, player, mouse_x, mouse_y, draw_tooltip=False)

        # 6. Crafting Menu
        if inventory.is_open:
            crafting_system.render(target_surf, mouse_x, mouse_y, self.font)

        # 7. Item Tooltip (Rich Rarity, Stats, Description, Special Effects & Lore)
        # Defer if character_panel is open or render_tooltips is False to guarantee topmost z-order over panels
        if render_tooltips and not (character_panel and getattr(character_panel, "is_open", False)):
            if hovered_slot and hovered_slot.data:
                self._render_tooltip(target_surf, mouse_x, mouse_y, hovered_slot, player=player, character_panel=character_panel)
                self._last_hovered_slot = None

        # 8. Held Dragging Item
        if render_dragged:
            self.render_dragged_item(target_surf, inventory, mouse_x, mouse_y)

        # 9. LAN Multiplayer Party HUD & Chat / Cheat Console
        if lan_client and (lan_client.connected or lan_client.remote_players):
            self._render_party_hud(target_surf, lan_client, inventory, crafting_system)
            self._render_chat(target_surf, lan_client)
        elif self.chat_active or (hasattr(self, "local_chat_history") and self.local_chat_history):
            self._render_chat(target_surf, None)

        # 9.5. Celebratory Ancient Relic Discovery Banner / Toast
        if combat and getattr(combat, "ancient_drop_banner", None):
            b_name = combat.ancient_drop_banner.get("name", "Ancient Relic")
            self._render_ancient_drop_toast(target_surf, b_name)

        # 9.8. Active Food Buffs Tooltip Overlay (Ensures top z-order over chat/toasts)
        if self._hovered_food_buff:
            self._render_food_buff_tooltip(target_surf, self._hovered_food_buff[0], self._hovered_food_buff[1])

        # 10. Reticle & Attack Recharge Gauge & Mining Progress
        self._render_reticle(target_surf, player, camera, mouse_x, mouse_y, inventory=inventory, world=world)

    def render_hovered_tooltip(self, target_surf, mouse_x=None, mouse_y=None, player=None, character_panel=None):
        """Renders deferred item tooltip in topmost z-order over character and chest panels."""
        if getattr(self, "_last_hovered_slot", None) and self._last_hovered_slot.data:
            mx = mouse_x if mouse_x is not None else getattr(self, "_last_mouse_pos", (0, 0))[0]
            my = mouse_y if mouse_y is not None else getattr(self, "_last_mouse_pos", (0, 0))[1]
            self._render_tooltip(target_surf, mx, my, self._last_hovered_slot, player=player, character_panel=character_panel)
            self._last_hovered_slot = None

    def render_dragged_item(self, target_surf, inventory, mouse_x, mouse_y):
        """Renders the currently dragged item at the cursor in the foreground."""
        if inventory and getattr(inventory, "held_item", None):
            icon = self.asset_factory.items.get(inventory.held_item.item_id)
            if icon:
                target_surf.blit(icon, (mouse_x - 12, mouse_y - 12))
            if inventory.held_item.count > 1:
                cnt_txt = self.font.render(str(inventory.held_item.count), True, (255, 255, 255))
                target_surf.blit(cnt_txt, (mouse_x + 4, mouse_y + 4))

    def _render_notification_banner(self, target_surf, message):
        """Displays a prominent banner across top-center when learning skills or completing feats."""
        txt_surf = self.font.render(message, True, (255, 235, 100))
        bw = txt_surf.get_width() + 36
        bh = 34
        bx = SCREEN_WIDTH // 2 - bw // 2
        by = 16

        bg_rect = pygame.Rect(bx, by, bw, bh)
        pygame.draw.rect(target_surf, (22, 28, 46, 245), bg_rect, border_radius=8)
        pygame.draw.rect(target_surf, COLOR_GOLD, bg_rect, 2, border_radius=8)
        target_surf.blit(txt_surf, (bx + 18, by + 8))

    def _render_hp_and_mp(self, target_surf, player):
        """Draws health hearts, numeric life, and glowing mana bar positioned to the left of the radar map."""
        total_hearts = max(1, player.stats.max_hp // 20)
        cur_hearts = int(math.ceil(player.stats.hp / 20.0))

        # Position to the left of the minimap radar so they never overlap (Minimap is at x=1116..1264)
        container_w = 260 # Fixed 10-heart container width prevents horizontal HUD shifting on level-up
        start_x = 840     # SCREEN_WIDTH (1280) - right_margin (180) - container_w (260)
        start_y = 20

        # 1. Health Hearts (Positioned to the left of the radar map, container_w=260)
        rows = (total_hearts + 9) // 10
        for i in range(total_hearts):
            r_idx = i // 10
            c_idx = i % 10
            hx = start_x + c_idx * 26
            hy = start_y + r_idx * 24
            if i < cur_hearts:
                target_surf.blit(self.heart_full, (hx, hy))
            else:
                target_surf.blit(self.heart_empty, (hx, hy))

        # 1.5. Numerical Life Display (High-contrast badge plate in topmost z-order above hearts & bars)
        hp_val = max(0, int(round(player.stats.hp)))
        max_hp_val = max(1, int(round(player.stats.max_hp)))
        hp_key = (hp_val, max_hp_val, player.stats.level)
        if hp_key != self._cached_hp_key:
            self._cached_hp_key = hp_key
            text_str = f"Life: {hp_val} / {max_hp_val}  (Lv.{player.stats.level})"
            is_dying = (hp_val <= 0)
            is_critical = (hp_val <= max_hp_val * 0.25)
            txt_color = (255, 120, 120) if is_dying else ((255, 160, 160) if is_critical else (255, 130, 130))
            self._cached_hp_shadow = self.font.render(text_str, True, (0, 0, 0))
            self._cached_hp_surf = self.font.render(text_str, True, txt_color)

        tw = self._cached_hp_surf.get_width()
        th = self._cached_hp_surf.get_height()
        bx = start_x
        by = start_y - 17
        bw = tw + 12
        bh = 16
        is_dying = (hp_val <= 0)
        is_critical = (hp_val <= max_hp_val * 0.25)
        badge_bg = (28, 16, 20, 240) if is_dying else ((24, 18, 22, 235) if is_critical else (18, 22, 34, 230))
        badge_border = (200, 60, 60, 240) if is_dying else ((180, 75, 75, 235) if is_critical else (60, 75, 105, 230))
        badge_rect = pygame.Rect(bx, by, bw, bh)
        pygame.draw.rect(target_surf, badge_bg, badge_rect, border_radius=4)
        pygame.draw.rect(target_surf, badge_border, badge_rect, 1, border_radius=4)
        target_surf.blit(self._cached_hp_shadow, (bx + 7, by + 1))
        target_surf.blit(self._cached_hp_surf, (bx + 6, by))

        # Mana Bar (Positioned with clean 12px padding below hearts to eliminate visual collision)
        mp_h = 12
        mp_y = start_y + rows * 24 + 10
        mp_w = container_w
        mp_pct = max(0.0, min(1.0, player.stats.mp / float(max(1, player.stats.max_mp))))
        
        pygame.draw.rect(target_surf, (15, 25, 45), (start_x, mp_y, mp_w, mp_h), border_radius=4)
        if mp_pct > 0:
            pygame.draw.rect(target_surf, (50, 160, 255), (start_x, mp_y, int(mp_w * mp_pct), mp_h), border_radius=4)
        pygame.draw.rect(target_surf, (80, 120, 180), (start_x, mp_y, mp_w, mp_h), 1, border_radius=4)

        int_mp = int(player.stats.mp)
        mp_key = (int_mp, player.stats.max_mp)
        if mp_key != self._cached_mp_key:
            self._cached_mp_key = mp_key
            self._cached_mp_surf = self.font_sm.render(f"MP: {int_mp} / {player.stats.max_mp}", True, (200, 230, 255))
        target_surf.blit(self._cached_mp_surf, (start_x + mp_w // 2 - self._cached_mp_surf.get_width() // 2, mp_y + (mp_h - self._cached_mp_surf.get_height()) // 2))

        # Oxygen / Breath Meter (Minecraft-style 10 Air Bubbles displayed when swimming or depleted)
        if getattr(player, "in_water", False) or getattr(player, "oxygen", 100.0) < 99.0:
            bubble_y = mp_y + mp_h + 4
            cur_bubbles = int(math.ceil(getattr(player, "oxygen", 100.0) / 10.0))
            is_low = getattr(player, "oxygen", 100.0) < 30.0

            ox_label = self.font_sm.render(f"Air: {int(getattr(player, 'oxygen', 100.0))}%", True, (130, 220, 255))
            target_surf.blit(ox_label, (start_x, bubble_y - 1))

            import random
            for b_idx in range(10):
                bx = start_x + 65 + b_idx * 16
                by = bubble_y - 1
                if is_low and b_idx < cur_bubbles:
                    by += random.randint(-1, 1)

                if b_idx < cur_bubbles:
                    if self.bubble_full:
                        target_surf.blit(self.bubble_full, (bx, by))
                    else:
                        pygame.draw.circle(target_surf, (80, 190, 255), (bx + 6, by + 6), 5)
                elif b_idx == cur_bubbles and self.bubble_pop:
                    target_surf.blit(self.bubble_pop, (bx, by))
                elif self.bubble_empty:
                    target_surf.blit(self.bubble_empty, (bx, by))
                else:
                    pygame.draw.circle(target_surf, (50, 80, 110), (bx + 6, by + 6), 5, 1)

    def _render_skill_bar(self, target_surf, player):
        """Draws active skill icons and cooldown sweeps dynamically from player's hotkey loadout with sleek badges."""
        skills = list(player.skills.hotkey_bindings.items()) if hasattr(player.skills, "hotkey_bindings") else [
            ("Q", "power_slash"), ("F", "whirlwind"), ("V", "dash"), ("R", "fireball")
        ]
        bw, bh = 54, 60
        gap = 8
        total_w = len(skills) * (bw + gap) - gap
        start_x = (SCREEN_WIDTH - total_w) // 2
        start_y = SCREEN_HEIGHT - 68

        for i, (key, s_id) in enumerate(skills):
            sx = start_x + i * (bw + gap)
            rect = pygame.Rect(sx, start_y, bw, bh)

            is_learned = s_id in player.skills.learned_skills if s_id else False
            cd_left = player.skills.cooldowns.get(s_id, 0.0) if s_id else 0.0

            # Slot box & backdrop
            pygame.draw.rect(target_surf, (18, 24, 38, 240), rect, border_radius=6)
            inner_rect = pygame.Rect(sx + 2, start_y + 2, bw - 4, bh - 4)
            pygame.draw.rect(target_surf, (26, 34, 50, 220), inner_rect, border_radius=5)

            # Evolved skill check
            is_evolved = hasattr(player.skills, "is_skill_evolved") and player.skills.is_skill_evolved(s_id)
            if is_evolved:
                border_col = (255, 215, 60)
            elif is_learned:
                border_col = (130, 165, 215)
            else:
                border_col = (55, 65, 82)
            pygame.draw.rect(target_surf, border_col, rect, 2 if is_evolved else 1, border_radius=6)

            # 1. Top-Left: Hotkey Badge (strictly separated from level)
            k_badge = pygame.Rect(sx + 3, start_y + 3, 16, 13)
            pygame.draw.rect(target_surf, (12, 16, 26, 240), k_badge, border_radius=3)
            pygame.draw.rect(target_surf, (95, 125, 165) if is_learned else (45, 52, 65), k_badge, 1, border_radius=3)
            k_txt = self.font_sm.render(key, True, (255, 220, 70) if is_learned else (120, 130, 145))
            target_surf.blit(k_txt, (k_badge.centerx - k_txt.get_width() // 2, k_badge.centery - k_txt.get_height() // 2))

            # 2. Top-Right: Evolved Crest / Star Badge (if evolved)
            if is_evolved:
                evo_badge = pygame.Rect(sx + bw - 18, start_y + 3, 15, 13)
                pygame.draw.rect(target_surf, (42, 34, 10, 240), evo_badge, border_radius=3)
                pygame.draw.rect(target_surf, (255, 215, 60), evo_badge, 1, border_radius=3)
                evo_txt = self.font_sm.render("*", True, (255, 225, 80))
                target_surf.blit(evo_txt, (evo_badge.centerx - evo_txt.get_width() // 2, evo_badge.centery - evo_txt.get_height() // 2))

            # 3. Center Area: 30x30 Skill Icon
            icon_x = sx + (bw - 30) // 2
            icon_y = start_y + 16
            icon_drawn = False

            if s_id and hasattr(self.asset_factory, "skill_icons"):
                s_def = SKILL_DEFINITIONS.get(s_id, {})
                ev_name = s_def.get("evolved_name", "").lower().replace(" ", "_")
                icon_surf = self.asset_factory.skill_icons.get(ev_name) if is_evolved else None
                if not icon_surf:
                    icon_surf = self.asset_factory.skill_icons.get(s_id)
                if icon_surf:
                    icon_scaled = pygame.transform.scale(icon_surf, (30, 30))
                    if not is_learned:
                        dim_surf = icon_scaled.copy()
                        dim_surf.fill((55, 55, 60, 170), special_flags=pygame.BLEND_RGBA_MULT)
                        target_surf.blit(dim_surf, (icon_x, icon_y))
                    else:
                        target_surf.blit(icon_scaled, (icon_x, icon_y))
                    icon_drawn = True

            # Text fallback if no icon
            if not icon_drawn:
                if s_id and hasattr(player.skills, "get_skill_name"):
                    s_name = player.skills.get_skill_name(s_id)[:3]
                else:
                    s_name = SKILL_DEFINITIONS.get(s_id, {}).get("name", "---")[:3] if s_id else "---"
                n_txt = self.font_sm.render(s_name, True, (255, 255, 255) if is_learned else (110, 110, 110))
                target_surf.blit(n_txt, (sx + bw // 2 - n_txt.get_width() // 2, icon_y + 8))

            # Cooldown shadow sweep over icon
            if cd_left > 0 and s_id in SKILL_DEFINITIONS:
                max_cd = max(0.1, SKILL_DEFINITIONS[s_id]["cooldown"])
                sweep_pct = min(1.0, cd_left / max_cd)
                sweep_h = int(30 * sweep_pct)
                if sweep_h > 0:
                    cd_rect = pygame.Rect(icon_x, icon_y + (30 - sweep_h), 30, sweep_h)
                    cd_surf = pygame.Surface((30, sweep_h), pygame.SRCALPHA)
                    cd_surf.fill((0, 0, 0, 175))
                    target_surf.blit(cd_surf, cd_rect.topleft)

                cd_txt = self.font_sm.render(f"{cd_left:.1f}", True, (255, 255, 255))
                shd_txt = self.font_sm.render(f"{cd_left:.1f}", True, (0, 0, 0))
                tx = sx + bw // 2 - cd_txt.get_width() // 2
                ty = icon_y + 7
                target_surf.blit(shd_txt, (tx + 1, ty + 1))
                target_surf.blit(cd_txt, (tx, ty))

            # 4. Bottom Row: Level Badge (Centered at bottom footer, completely separated from hotkey)
            lvl_y = start_y + bh - 13
            if is_learned and hasattr(player.skills, "get_skill_level"):
                lvl = player.skills.get_skill_level(s_id)
                lvl_str = f"Lv.{lvl}"
                lvl_txt = self.font_sm.render(lvl_str, True, (255, 225, 85))
                lw = lvl_txt.get_width()
                l_badge = pygame.Rect(sx + (bw - (lw + 6)) // 2, lvl_y, lw + 6, 11)
                pygame.draw.rect(target_surf, (12, 16, 26, 240), l_badge, border_radius=3)
                pygame.draw.rect(target_surf, (185, 150, 45), l_badge, 1, border_radius=3)
                target_surf.blit(lvl_txt, (l_badge.x + 3, l_badge.centery - lvl_txt.get_height() // 2))
            else:
                l_badge = pygame.Rect(sx + (bw - 16) // 2, lvl_y, 16, 11)
                pygame.draw.rect(target_surf, (12, 16, 26, 200), l_badge, border_radius=3)
                pygame.draw.rect(target_surf, (45, 52, 65), l_badge, 1, border_radius=3)
                lock_txt = self.font_sm.render("-", True, (85, 95, 110))
                target_surf.blit(lock_txt, (l_badge.centerx - lock_txt.get_width() // 2, l_badge.centery - lock_txt.get_height() // 2))

    def _render_food_buffs(self, target_surf, player, mouse_x, mouse_y, draw_tooltip=True):
        """Displays small Food Buff HUD widget at bottom-left (x=20, y=SCREEN_HEIGHT-44).
        Shows active meal buff icons, category-colored ornate borders, duration progress bar,
        and high-contrast tooltip on hover."""
        self._hovered_food_buff = None
        if not player or not hasattr(player, "meal_buffs") or not player.meal_buffs:
            return

        category_order = ["offense", "defense", "mobility", "resource", "utility"]
        cat_colors = {
            "offense": (235, 75, 75),
            "defense": (75, 145, 235),
            "mobility": (60, 215, 120),
            "resource": (245, 195, 55),
            "utility": (185, 95, 240),
        }

        active_buffs = [player.meal_buffs[c] for c in category_order if c in player.meal_buffs]
        if not active_buffs:
            return

        start_x = 20
        start_y = SCREEN_HEIGHT - 44
        slot_w = 32
        slot_h = 32
        gap = 6

        hovered_buff = None
        hovered_rect = None

        for idx, buff in enumerate(active_buffs):
            bx = start_x + idx * (slot_w + gap)
            by = start_y
            rect = pygame.Rect(bx, by, slot_w, slot_h)

            cat = str(buff.get("category", "")).lower()
            cat_col = cat_colors.get(cat, (218, 165, 32))

            # 1. Background plate
            bg_surf = pygame.Surface((slot_w, slot_h), pygame.SRCALPHA)
            bg_surf.fill((16, 20, 32, 230))
            target_surf.blit(bg_surf, (bx, by))

            # 2. Ornate category border
            pygame.draw.rect(target_surf, cat_col, rect, 2, border_radius=4)

            # 3. Food Icon (24x24)
            icon_key = buff.get("icon") or buff.get("item_id")
            icon_drawn = False
            if hasattr(self, "asset_factory") and hasattr(self.asset_factory, "items") and icon_key in self.asset_factory.items:
                raw_icon = self.asset_factory.items[icon_key]
                if raw_icon:
                    icon_img = pygame.transform.scale(raw_icon, (24, 24))
                    target_surf.blit(icon_img, (bx + 4, by + 3))
                    icon_drawn = True

            if not icon_drawn:
                name_initial = buff.get("name", "?")[:1].upper()
                fallback_txt = self.font_sm.render(name_initial, True, cat_col)
                target_surf.blit(fallback_txt, (bx + (slot_w - fallback_txt.get_width()) // 2, by + 6))

            # 4. Duration progress indicator
            dur = max(0.0, float(buff.get("duration", 0.0)))
            max_dur = max(1.0, float(buff.get("max_duration", 180.0)))
            pct = max(0.0, min(1.0, dur / max_dur))
            bar_w = slot_w - 6
            bar_h = 3
            bar_bx = bx + 3
            bar_by = by + slot_h - 5
            pygame.draw.rect(target_surf, (22, 26, 38), (bar_bx, bar_by, bar_w, bar_h), border_radius=1)
            fill_w = int(bar_w * pct)
            if fill_w > 0:
                pygame.draw.rect(target_surf, cat_col, (bar_bx, bar_by, fill_w, bar_h), border_radius=1)

            if rect.collidepoint(mouse_x, mouse_y):
                hovered_buff = buff
                hovered_rect = rect

        if hovered_buff and hovered_rect:
            self._hovered_food_buff = (hovered_buff, hovered_rect)
            if draw_tooltip:
                self._render_food_buff_tooltip(target_surf, hovered_buff, hovered_rect)

    def _render_food_buff_tooltip(self, target_surf, hovered_buff, hovered_rect):
        """Renders high-contrast tooltip for hovered food buff."""
        cat_colors = {
            "offense": (235, 75, 75),
            "defense": (75, 145, 235),
            "mobility": (60, 215, 120),
            "resource": (245, 195, 55),
            "utility": (185, 95, 240),
        }
        cat = str(hovered_buff.get("category", "")).lower()
        cat_col = cat_colors.get(cat, (218, 165, 32))
        dur = max(0.0, float(hovered_buff.get("duration", 0.0)))
        mins = int(dur) // 60
        secs = int(dur) % 60

        lines = []
        lines.append((hovered_buff.get("name", "Meal Buff"), (255, 230, 90), self.font))
        lines.append((f"[{cat.upper()}]  {mins}:{secs:02d} remaining", cat_col, self.font_sm))

        effects = hovered_buff.get("effects", [])
        if effects:
            for eff in effects:
                lines.append((f"• {eff}", (190, 240, 255), self.font_sm))
        else:
            stats = hovered_buff.get("stats", {})
            for sk, sv in stats.items():
                s_label = sk.replace("_mult", "").replace("_", " ").title()
                sign = "+" if sv > 0 else ""
                val_str = f"{sign}{sv*100:.0f}%" if "mult" in sk or "chance" in sk or "pen" in sk or "reduction" in sk else f"{sign}{sv}"
                lines.append((f"• {val_str} {s_label}", (190, 240, 255), self.font_sm))

        lines.append((f"Eating another {cat.title()} meal replaces this buff.", (150, 165, 185), self.font_sm))

        padding = 8
        tip_w = 0
        tip_h = padding * 2
        rendered = []
        for t_str, t_col, t_font in lines:
            s = t_font.render(t_str, True, t_col)
            rendered.append(s)
            tip_w = max(tip_w, s.get_width() + padding * 2)
            tip_h += s.get_height() + 3

        tip_x = max(10, min(hovered_rect.x, SCREEN_WIDTH - tip_w - 10))
        tip_y = max(10, hovered_rect.y - tip_h - 6)
        tip_bg = pygame.Rect(tip_x, tip_y, tip_w, tip_h)

        pygame.draw.rect(target_surf, (14, 18, 28, 250), tip_bg, border_radius=6)
        pygame.draw.rect(target_surf, cat_col, tip_bg, 1, border_radius=6)

        cur_y = tip_y + padding
        for s in rendered:
            target_surf.blit(s, (tip_x + padding, cur_y))
            cur_y += s.get_height() + 3


    def _render_inventory(self, target_surf, inventory, mouse_x, mouse_y, player=None):
        start_x = 20
        start_y = 20
        rows = INV_ROWS if inventory.is_open else 1
        hovered = None

        for row in range(rows):
            for col in range(INV_COLS):
                slot_idx = row * INV_COLS + col
                sx = start_x + col * (SLOT_SIZE + SLOT_PADDING)
                sy = start_y + row * (SLOT_SIZE + SLOT_PADDING)
                rect = pygame.Rect(sx, sy, SLOT_SIZE, SLOT_SIZE)

                target_surf.blit(self.slot_frame, (sx, sy))

                if row == 0 and col == inventory.selected_slot:
                    target_surf.blit(self.slot_selected, (sx, sy))

                    # Cooldown sweep overlay on active attack slot
                    if player and getattr(player, "attack_cooldown", 0.0) > 0:
                        max_cd = max(0.001, getattr(player, "max_attack_cooldown", 0.24))
                        sweep_pct = max(0.0, min(1.0, player.attack_cooldown / max_cd))
                        sweep_h = int(SLOT_SIZE * sweep_pct)
                        if sweep_h > 0:
                            cd_surf = pygame.Surface((SLOT_SIZE, sweep_h), pygame.SRCALPHA)
                            cd_surf.fill((0, 0, 0, 150))
                            target_surf.blit(cd_surf, (sx, sy + (SLOT_SIZE - sweep_h)))
                            pygame.draw.line(target_surf, (255, 230, 120), (sx, sy + (SLOT_SIZE - sweep_h)), (sx + SLOT_SIZE - 1, sy + (SLOT_SIZE - sweep_h)), 1)

                if row == 0:
                    target_surf.blit(self.cached_key_hints[col], (sx + 3, sy + 2))

                item = inventory.slots[slot_idx]
                if item:
                    icon = self.asset_factory.items.get(item.item_id)
                    if icon:
                        target_surf.blit(icon, (sx + 8, sy + 8))

                    if item.count > 1:
                        if item.count not in self._cached_count_surfs:
                            txt = str(item.count)
                            shd = self.font.render(txt, True, (0, 0, 0))
                            cnt = self.font.render(txt, True, (255, 255, 255))
                            self._cached_count_surfs[item.count] = (shd, cnt)
                        shadow, cnt_surf = self._cached_count_surfs[item.count]
                        target_surf.blit(shadow, (sx + SLOT_SIZE - shadow.get_width() - 3, sy + SLOT_SIZE - 15))
                        target_surf.blit(cnt_surf, (sx + SLOT_SIZE - cnt_surf.get_width() - 4, sy + SLOT_SIZE - 16))

                if rect.collidepoint(mouse_x, mouse_y):
                    pygame.draw.rect(target_surf, (255, 255, 255), rect, 1)
                    if item:
                        hovered = item

        if inventory.is_open:
            drop_hint = self.font_sm.render("[G/Q/Backspace] Drop • Click [DROP] Button", True, (255, 230, 100))
            target_surf.blit(drop_hint, (start_x + 4, start_y + rows * (SLOT_SIZE + SLOT_PADDING) + 5))

            # Interactive DROP button
            btn_rect = inventory.get_drop_button_rect()
            is_hover = btn_rect.collidepoint(mouse_x, mouse_y)
            bg = (70, 85, 120) if is_hover else (45, 55, 80)
            border = (255, 230, 100) if is_hover else (100, 120, 160)
            pygame.draw.rect(target_surf, bg, btn_rect, border_radius=4)
            pygame.draw.rect(target_surf, border, btn_rect, 1, border_radius=4)
            d_txt = self.font_sm.render("DROP", True, (255, 255, 255) if not is_hover else (255, 230, 100))
            target_surf.blit(d_txt, (btn_rect.centerx - d_txt.get_width() // 2, btn_rect.centery - d_txt.get_height() // 2))

            # Interactive RECYCLE / TRASH button
            rec_rect = inventory.get_recycle_button_rect()
            is_rec_hover = rec_rect.collidepoint(mouse_x, mouse_y)
            rec_bg = (130, 42, 42) if is_rec_hover else (82, 28, 28)
            rec_border = (255, 120, 120) if is_rec_hover else (160, 60, 60)
            pygame.draw.rect(target_surf, rec_bg, rec_rect, border_radius=4)
            pygame.draw.rect(target_surf, rec_border, rec_rect, 1, border_radius=4)
            r_txt = self.font_sm.render("RECYCLE", True, (255, 235, 235) if not is_rec_hover else (255, 200, 200))
            target_surf.blit(r_txt, (rec_rect.centerx - r_txt.get_width() // 2, rec_rect.centery - r_txt.get_height() // 2))

            if is_rec_hover:
                tt_text = "Permanently disposes selected or held item"
                tt_surf = self.font_sm.render(tt_text, True, (255, 220, 220))
                tt_bg = pygame.Rect(mouse_x + 10, mouse_y + 12, tt_surf.get_width() + 10, tt_surf.get_height() + 6)
                pygame.draw.rect(target_surf, (40, 15, 15, 230), tt_bg, border_radius=4)
                pygame.draw.rect(target_surf, (220, 60, 60), tt_bg, 1, border_radius=4)
                target_surf.blit(tt_surf, (tt_bg.x + 5, tt_bg.y + 3))

            # Interactive ORGANIZE button
            if hasattr(inventory, "get_organize_button_rect"):
                org_rect = inventory.get_organize_button_rect()
                is_org_hover = org_rect.collidepoint(mouse_x, mouse_y)
                org_bg = (40, 110, 70) if is_org_hover else (25, 75, 48)
                org_border = (120, 255, 160) if is_org_hover else (60, 160, 100)
                pygame.draw.rect(target_surf, org_bg, org_rect, border_radius=4)
                pygame.draw.rect(target_surf, org_border, org_rect, 1, border_radius=4)
                o_txt = self.font_sm.render("ORGANIZE", True, (235, 255, 235) if not is_org_hover else (200, 255, 200))
                target_surf.blit(o_txt, (org_rect.centerx - o_txt.get_width() // 2, org_rect.centery - o_txt.get_height() // 2))

                if is_org_hover:
                    tt_text = "Compacts items forward to fill empty gaps"
                    tt_surf = self.font_sm.render(tt_text, True, (220, 255, 220))
                    tt_bg = pygame.Rect(mouse_x + 10, mouse_y + 12, tt_surf.get_width() + 10, tt_surf.get_height() + 6)
                    pygame.draw.rect(target_surf, (15, 40, 25, 230), tt_bg, border_radius=4)
                    pygame.draw.rect(target_surf, (60, 200, 100), tt_bg, 1, border_radius=4)
                    target_surf.blit(tt_surf, (tt_bg.x + 5, tt_bg.y + 3))

        return hovered

    def _render_party_hud(self, target_surf, lan_client, inventory=None, crafting_system=None):
        """Displays party members (up to 5 players) with health bars in a dedicated clean panel."""
        p_count = len(lan_client.remote_players) + 1
        remotes = list(lan_client.remote_players.items())
        
        # Calculate panel dimensions
        panel_w = 216
        row_count = max(1, len(remotes))
        panel_h = 24 + row_count * 22 + 4

        # Determine non-overlapping position
        if inventory and inventory.is_open:
            # When inventory is open, place cleanly to the right of the backpack (which occupies x=20..460)
            # This completely avoids overlapping with Crafting Recipes (at x=20..272, y=230+) and Chat
            px = 480
            py = 20
        else:
            # When inventory is closed, cleanly tuck right below the hotbar (which occupies y=20..60)
            px = 20
            py = 72

        # Draw translucent styled background panel with subtle border
        bg_rect = pygame.Rect(px - 6, py - 4, panel_w, panel_h)
        panel_surf = pygame.Surface((panel_w, panel_h), pygame.SRCALPHA)
        panel_surf.fill((18, 22, 34, 220))
        target_surf.blit(panel_surf, (px - 6, py - 4))
        pygame.draw.rect(target_surf, (65, 80, 115), bg_rect, 1, border_radius=6)

        # Header Title
        hdr = self.font_sm.render(f"LAN PARTY ({p_count}/5 Players)", True, (255, 215, 0))
        target_surf.blit(hdr, (px, py))

        if not remotes:
            waiting_txt = self.font_sm.render("Waiting for players...", True, (140, 155, 175))
            target_surf.blit(waiting_txt, (px, py + 20))
        else:
            for i, (pid, pinfo) in enumerate(remotes):
                sy = py + 20 + i * 22
                pname = pinfo.get("name", f"Player {pid}")
                php = pinfo.get("hp", 100)
                pmax = max(1, pinfo.get("max_hp", 100))
                lvl = pinfo.get("level", 1)

                # Name label with Level badge
                nl = self.font_sm.render(f"{pname} (Lv.{lvl})", True, (220, 230, 245))
                target_surf.blit(nl, (px, sy))

                # Mini health bar
                bar_x = px + 126
                bar_w = 70
                hp_pct = max(0.0, min(1.0, php / float(pmax)))
                pygame.draw.rect(target_surf, (40, 20, 20), (bar_x, sy + 3, bar_w, 7))
                pygame.draw.rect(target_surf, (50, 220, 50), (bar_x, sy + 3, int(bar_w * hp_pct), 7))
                pygame.draw.rect(target_surf, (0, 0, 0), (bar_x, sy + 3, bar_w, 7), 1)

    def add_chat_message(self, sender, text):
        """Adds a timestamped message to the local chat and console history."""
        import time
        if not hasattr(self, "local_chat_history"):
            self.local_chat_history = []
        entry = {
            "time": time.time(),
            "sender": str(sender),
            "text": str(text)
        }
        self.local_chat_history.append(entry)
        if len(self.local_chat_history) > 40:
            self.local_chat_history = self.local_chat_history[-40:]

    def _render_chat(self, target_surf, lan_client=None):
        """Draws word-wrapped chat/command console box with 6.0s auto-hide when idle."""
        import time
        now = time.time()

        # Fetch raw message logs
        if lan_client and hasattr(lan_client, "chat_messages") and lan_client.chat_messages:
            raw_entries = lan_client.chat_messages
        else:
            raw_entries = getattr(self, "local_chat_history", [])

        # Normalize entries into dicts with timestamps
        norm_entries = []
        for idx, item in enumerate(raw_entries):
            if isinstance(item, dict):
                norm_entries.append(item)
            elif isinstance(item, (tuple, list)) and len(item) >= 2:
                if len(item) >= 3 and isinstance(item[0], (int, float)):
                    t_val, s_val, m_val = item[0], item[1], item[2]
                else:
                    s_val, m_val = item[0], item[1]
                    t_val = now
                entry = {"time": t_val, "sender": s_val, "text": m_val}
                norm_entries.append(entry)
                if isinstance(raw_entries, list):
                    raw_entries[idx] = entry
            else:
                entry = {"time": now, "sender": "", "text": str(item)}
                norm_entries.append(entry)
                if isinstance(raw_entries, list):
                    raw_entries[idx] = entry

        is_typing = getattr(self, "chat_active", False)

        # Auto-hide: When not actively typing in console, only show messages newer than 6.0 seconds
        if not is_typing:
            visible_entries = [e for e in norm_entries if (now - e.get("time", now)) <= 6.0]
            if not visible_entries:
                return  # Screen is 100% clean and unobstructed
        else:
            visible_entries = norm_entries[-10:]

        cx = 20
        box_width = 460
        max_text_w = box_width - 16

        # Word wrap messages to prevent long text from crossing the screen
        wrapped_lines = []
        for e in visible_entries:
            sender = e.get("sender", "")
            msg = e.get("text", "")
            prefix = f"[{sender}]: " if sender else ""
            full_str = f"{prefix}{msg}"

            # Semantic message colors
            if "[SYSTEM]" in prefix or sender == "[SYSTEM]":
                color = (255, 215, 100) if "error" not in msg.lower() else (255, 120, 120)
            elif "[NOTICE]" in prefix or sender == "[NOTICE]":
                color = (120, 220, 255)
            elif sender in ("Spud", "Player"):
                color = (160, 240, 160)
            else:
                color = (240, 242, 250)

            words = full_str.split(" ")
            cur = []
            for w in words:
                test_str = " ".join(cur + [w])
                if self.font_sm.size(test_str)[0] <= max_text_w:
                    cur.append(w)
                else:
                    if cur:
                        wrapped_lines.append((" ".join(cur), color))
                    cur = [w]
            if cur:
                wrapped_lines.append((" ".join(cur), color))

        display_lines = wrapped_lines[-8:]  # Fit comfortably in console area

        # Mode A: Active Typing (Display console window & input bar)
        if is_typing:
            console_h = 24 + len(display_lines) * 17 + 8
            console_y = SCREEN_HEIGHT - 84 - console_h
            console_rect = pygame.Rect(cx, console_y, box_width, console_h)
            
            # Semi-transparent dark slate backdrop
            pygame.draw.rect(target_surf, (14, 18, 28, 220), console_rect, border_radius=6)
            pygame.draw.rect(target_surf, (70, 95, 140, 200), console_rect, 1, border_radius=6)

            # Header
            hdr = self.font_sm.render("CONSOLE / CHAT (Type /help for cheat commands)", True, (140, 175, 220))
            target_surf.blit(hdr, (cx + 8, console_y + 5))

            # History lines
            line_y = console_y + 24
            for l_text, l_color in display_lines:
                ts = self.font_sm.render(l_text, True, l_color)
                target_surf.blit(ts, (cx + 8, line_y))
                line_y += 17

            # Typing input box
            box_y = SCREEN_HEIGHT - 74
            box_rect = pygame.Rect(cx, box_y, box_width, 24)
            pygame.draw.rect(target_surf, (20, 25, 40, 245), box_rect, border_radius=4)
            pygame.draw.rect(target_surf, COLOR_GOLD, box_rect, 1, border_radius=4)
            cursor_vis = "_" if int(pygame.time.get_ticks() / 400) % 2 == 0 else ""
            in_surf = self.font_sm.render(f"> {self.chat_input_text}{cursor_vis}", True, (255, 255, 255))
            target_surf.blit(in_surf, (cx + 6, box_y + 4))

        # Mode B: Idle (Render recent active messages as compact floating pills)
        else:
            base_y = SCREEN_HEIGHT - 84 - len(display_lines) * 18
            for i, (l_text, l_color) in enumerate(display_lines):
                ts = self.font_sm.render(l_text, True, l_color)
                pill_rect = pygame.Rect(cx, base_y + i * 18, ts.get_width() + 10, 16)
                pygame.draw.rect(target_surf, (12, 16, 26, 180), pill_rect, border_radius=3)
                pygame.draw.rect(target_surf, (50, 70, 100, 140), pill_rect, 1, border_radius=3)
                target_surf.blit(ts, (cx + 5, base_y + i * 18 + 1))

    def _render_ancient_drop_toast(self, target_surf, banner_name):
        """Renders radiant celebratory toast banner for Ancient Relic discoveries."""
        t_ticks = pygame.time.get_ticks() * 0.005
        pulse = math.sin(t_ticks * 3.0) * 2.0
        bw = 620
        bh = 48 + int(pulse)
        bx = SCREEN_WIDTH // 2 - bw // 2
        by = 28
        b_rect = pygame.Rect(bx, by, bw, bh)

        pygame.draw.rect(target_surf, (25, 10, 18, 245), b_rect, border_radius=10)
        pygame.draw.rect(target_surf, (255, 215, 60), b_rect, 3, border_radius=10)
        pygame.draw.rect(target_surf, (245, 60, 75), b_rect.inflate(-4, -4), 1, border_radius=8)

        text_str = f"★ ANCIENT RELIC DISCOVERED: {banner_name.upper()} ★"
        txt = self.font_lg.render(text_str, True, (255, 225, 90))
        sh = self.font_lg.render(text_str, True, (0, 0, 0))
        target_surf.blit(sh, (SCREEN_WIDTH // 2 - txt.get_width() // 2 + 1, by + 14))
        target_surf.blit(txt, (SCREEN_WIDTH // 2 - txt.get_width() // 2, by + 13))

    def _get_item_rarity_color(self, item):
        if isinstance(item, str):
            data = ITEM_REGISTRY.get(item, {})
        elif hasattr(item, "data"):
            data = item.data
        else:
            data = {}
        rarity = data.get("rarity", RARITY_COMMON)
        return RARITY_COLORS.get(rarity, (220, 220, 220))

    def _build_tooltip_lines(self, item, player=None, is_equipped=False):
        """Constructs formatted text lines and colors for rich Diablo/Torchlight-style item tooltip."""
        if not item:
            return []
        if isinstance(item, str):
            item = ItemStack(item, 1)
        if not hasattr(item, "data"):
            return []
        if player is None:
            player = getattr(item, "player", None)

        data = item.data
        name = data.get("name", item.item_id)
        cat = data.get("cat", "item").replace("_", " ").title()
        rarity = data.get("rarity", RARITY_COMMON)
        r_color = RARITY_COLORS.get(rarity, (220, 220, 220))

        is_compact = getattr(self, "tooltip_mode", "detailed") == "compact"
        lines = []

        # 0. Equipped Banner (for currently equipped comparison card)
        if is_equipped:
            lines.append(("[ CURRENTLY EQUIPPED ]", (255, 215, 0), self.font_bold))

        # 1. Item Name in Rarity Color
        lines.append((name, r_color, self.font))

        # 2. Rarity Tier & Type Badge
        badge = f"[{rarity.upper()} {cat.upper()}]"
        lines.append((badge, r_color, self.font_sm))

        if is_compact:
            if data.get("damage", 0) > 0:
                if data.get("cat") == CAT_TOOL or data.get("cat") == "tool":
                    lines.append((f"Tool Damage: {data['damage']}", (190, 205, 225), self.font_sm))
                else:
                    lines.append((f"Power: {data['damage']} Damage", (255, 215, 100), self.font_sm))
            elif data.get("atk", 0) > 0:
                lines.append((f"Attack: +{data['atk']}", (255, 215, 100), self.font_sm))
            if data.get("def", 0) > 0 and data.get("cat") not in (CAT_WEAPON, "weapon") and data.get("category") not in (CAT_WEAPON, "weapon") and getattr(item, "slot", "") != "weapon":
                lines.append((f"Defense: +{data['def']}", (140, 230, 140), self.font_sm))
            if data.get("hp", 0) > 0:
                lines.append((f"Max HP: +{data['hp']}", (255, 120, 120), self.font_sm))
            if data.get("heal", 0) > 0:
                lines.append((f"Restores +{data['heal']} Health", (255, 110, 110), self.font_sm))
            if data.get("mp", 0) > 0:
                lines.append((f"Restores +{data['mp']} Mana", (100, 180, 255), self.font_sm))
            if data.get("buff"):
                buff_info = data["buff"]
                cat_tag = buff_info.get("category", "Buff").title()
                lines.append((f"Meal Buff [{cat_tag}]: {buff_info.get('name', '')}", (255, 215, 100), self.font_sm))
                for eff in data.get("effects", []):
                    lines.append((f"• {eff}", (255, 230, 140), self.font_sm))
        else:
            # 3. Detailed Numeric Combat & Mining Stats
            if data.get("damage", 0) > 0:
                if data.get("cat") == CAT_TOOL or data.get("cat") == "tool":
                    lines.append((f"Tool Damage: {data['damage']}", (190, 205, 225), self.font_sm))
                else:
                    lines.append((f"Weapon Power: {data['damage']} Damage", (255, 215, 100), self.font_sm))
            if data.get("cat") == "weapon" or (data.get("damage", 0) > 0 and data.get("cat") != CAT_TOOL):
                iid = getattr(item, "item_id", str(item)).lower()
                if any(w in iid for w in ("dagger", "shortsword", "knife", "stiletto")):
                    speed_str = "Very Fast Speed (0.22s)"
                elif any(w in iid for w in ("greatsword", "cleaver", "hammer", "scythe", "titan", "colossus")):
                    speed_str = "Slow, Heavy Speed (0.46s)"
                elif "bow" in iid:
                    speed_str = "Average Speed (0.36s)"
                elif any(w in iid for w in ("staff", "wand", "scepter", "rod")):
                    speed_str = "Average Speed (0.34s)"
                elif any(w in iid for w in ("katana", "saber", "rapier", "spear")):
                    speed_str = "Fast Speed (0.26s)"
                else:
                    speed_str = "Fast Speed (0.32s)"
                lines.append((f"Use Speed: {speed_str}", (240, 230, 160), self.font_sm))

            if data.get("def", 0) > 0 and data.get("cat") not in (CAT_WEAPON, "weapon") and data.get("category") not in (CAT_WEAPON, "weapon") and getattr(item, "slot", "") != "weapon":
                lines.append((f"+{data['def']} Defense", (140, 230, 140), self.font_sm))
            if data.get("atk", 0) > 0:
                lines.append((f"+{data['atk']} Attack", (255, 205, 110), self.font_sm))
            if data.get("crit", 0) > 0:
                lines.append((f"+{data['crit']}% Critical Strike Chance", (255, 175, 80), self.font_sm))
            if data.get("speed", 0) > 0:
                if data.get("cat") == "weapon":
                    lines.append((f"+{int(data['speed'] * 100)}% Attack Speed", (255, 235, 140), self.font_sm))
                else:
                    lines.append((f"+{data['speed']}% Movement Speed", (200, 210, 255), self.font_sm))
            if data.get("hp", 0) > 0:
                lines.append((f"+{data['hp']} Max HP", (255, 120, 120), self.font_sm))
            if data.get("mp", 0) > 0:
                lines.append((f"+{data['mp']} Max MP", (100, 180, 255), self.font_sm))
            if data.get("mp_regen", 0) > 0:
                lines.append((f"+{data['mp_regen']:.1f} MP/s Mana Regen", (120, 210, 255), self.font_sm))
            if data.get("heal", 0) > 0:
                lines.append((f"Restores +{data['heal']} Health", (255, 110, 110), self.font_sm))
            if data.get("buff"):
                buff_info = data["buff"]
                cat_tag = buff_info.get("category", "Buff").upper()
                dur_s = buff_info.get("duration", 0)
                dur_str = f"{dur_s // 60}m" if dur_s >= 60 else f"{dur_s}s"
                lines.append((f"Meal Buff [{cat_tag}] ({dur_str}): {buff_info.get('name', '')}", (255, 215, 100), self.font_sm))
                for eff in data.get("effects", []):
                    lines.append((f"• {eff}", (255, 230, 140), self.font_sm))

            enh_lvl = getattr(item, "enhancement_level", 0)
            if enh_lvl > 0:
                lines.append((f"Enhanced: +{enh_lvl} (Double Stats at +7)", (80, 240, 255), self.font_sm))
            if getattr(item, "is_broken", False):
                lines.append(("[BROKEN] Requires repair at Mystic Trader!", (255, 70, 70), self.font_sm))

            # Rolled Base Stats indicator
            base_rolls = getattr(item, "base_rolls", None)
            if base_rolls:
                is_weapon = data.get("cat") in (CAT_WEAPON, "weapon") or data.get("category") in (CAT_WEAPON, "weapon") or getattr(item, "slot", "") == "weapon"
                if is_weapon:
                    filtered_rolls = {k: v for k, v in base_rolls.items() if k.lower() not in ("def", "defense", "armor", "dmg_reduction")}
                else:
                    filtered_rolls = base_rolls
                if filtered_rolls:
                    roll_parts = [f"+{v} {k.upper()}" for k, v in filtered_rolls.items()]
                    lines.append((f"Rolled Base Stats: {', '.join(roll_parts)}", (255, 230, 140), self.font_sm))

            # Special Tags
            item_tags = getattr(item, "tags", None) or data.get("tags", [])
            if item_tags:
                from src.rpg.equipment_update import TAG_REGISTRY
                tag_labels = [TAG_REGISTRY.get(t, {}).get("display_name", t.replace("_", " ").title()) for t in item_tags]
                lines.append((f"Tags: {' • '.join(tag_labels)}", (100, 220, 255), self.font_sm))

            from src.ui.theme import wrap_text_lines

            # 4. Special Weapon Effects / Skills (Bulleted for upper rarities or items with perks, displayed BEFORE affixes)
            effects = data.get("effects", [])
            iid = getattr(item, "item_id", str(item)).lower()
            rarity_str = str(rarity).lower()
            is_high_tier = rarity_str in ("epic", "mythic", "legendary", "ancient")
            if "wood" not in iid and (is_high_tier or effects or data.get("special")):
                if effects and not data.get("buff"):
                    raw_affs = set(getattr(item, "affixes", []) or [])
                    weapon_effects = [e for e in effects if not str(e).startswith("★ ") and e not in raw_affs]
                    for eff in weapon_effects:
                        for el in wrap_text_lines(f"• {eff}", self.font_sm, 300):
                            lines.append((el, (100, 240, 240), self.font_sm))
                elif data.get("special"):
                    for sl in wrap_text_lines(f"Special: {data['special']}", self.font_sm, 300):
                        lines.append((sl, (100, 240, 240), self.font_sm))

            # Affix Sockets (Clean ARPG circular socket indicator per slot)
            from src.rpg.equipment_update import build_affix_socket_lines
            lines.extend(build_affix_socket_lines(item, font=self.font_sm, wrap_width=300))

            # Set Membership & Torchlight 2 Tiered Milestones
            from src.rpg.equipment_update import build_set_tooltip_lines
            raw_id = getattr(item, "item_id", item if isinstance(item, str) else "")
            set_lines = build_set_tooltip_lines(raw_id, player=player, font=self.font_sm, wrap_width=300)
            lines.extend(set_lines)

            # 5. Usage / Description (Word-wrapped to prevent ultra-wide tooltips)
            desc = data.get("desc")
            if not desc or str(desc).strip() == "":
                desc = f"A fine {rarity.title()} {cat.lower()} radiating elemental potency."
            for dl in wrap_text_lines(desc, self.font_sm, 300):
                lines.append((dl, (215, 225, 240), self.font_sm))

            # 6. Lore Quote (Diablo / Torchlight style) - Only Legendary, Mythic, Ancient
            rarity_str = str(rarity).lower()
            if data.get("lore") and rarity_str in (RARITY_LEGENDARY, RARITY_MYTHIC, RARITY_ANCIENT, "legendary", "mythic", "ancient"):
                for ll in wrap_text_lines(data["lore"], self.font_lore, 300):
                    lines.append((ll, (240, 205, 120), self.font_lore))

        return lines

    def _measure_tooltip(self, lines):
        """Calculates surface renderings and bounding box dimensions for a tooltip."""
        rendered_surfs = [fnt.render(text, True, col) for text, col, fnt in lines]
        content_w = max((s.get_width() for s in rendered_surfs), default=140)
        tw = max(160, min(330, content_w + 20))
        th = sum(s.get_height() + 3 for s in rendered_surfs) + 12
        return rendered_surfs, tw, th

    def _draw_tooltip_box(self, target_surf, tx, ty, tw, th, rendered_surfs, r_color):
        """Draws background plate, rarity border, and text surfaces for a tooltip card."""
        rect = pygame.Rect(tx, ty, tw, th)
        pygame.draw.rect(target_surf, (20, 24, 38, 245), rect, border_radius=6)
        pygame.draw.rect(target_surf, r_color, rect, 1, border_radius=6)

        cur_y = ty + 6
        for s in rendered_surfs:
            target_surf.blit(s, (tx + 10, cur_y))
            cur_y += s.get_height() + 3

    def _render_tooltip(self, target_surf, mx, my, item, player=None, character_panel=None):
        """Rich Diablo/Torchlight-style item tooltip with rarity tiers, stats, lore, and descriptions."""
        if not isinstance(mx, (int, float)) and isinstance(item, (int, float)):
            item, mx, my = mx, my, item
        if not item:
            return []
        if isinstance(item, str):
            item = ItemStack(item, 1)
        if not hasattr(item, "data"):
            return []
        if player is None:
            player = getattr(item, "player", None)

        # Check side-by-side equipment comparison condition ("katabi"):
        # Hovering an equippable item while Character Info panel is open (Button C)
        is_comparison = False
        equipped_item = None
        if character_panel and getattr(character_panel, "is_open", False) and player:
            slot = get_item_equipment_slot(item)
            if slot:
                equipped_item = get_equipped_item_for_slot(player, slot)
                if equipped_item is not None and item is not equipped_item and not getattr(item, "is_equipped", False):
                    same_id = (getattr(item, "item_id", None) == getattr(equipped_item, "item_id", None))
                    same_enh = (getattr(item, "enhancement_level", 0) == getattr(equipped_item, "enhancement_level", 0))
                    same_aff = (getattr(item, "affixes", []) == getattr(equipped_item, "affixes", []))
                    if not (same_id and same_enh and same_aff):
                        is_comparison = True

        if is_comparison and equipped_item:
            lines1 = self._build_tooltip_lines(item, player=player, is_equipped=False)
            lines2 = self._build_tooltip_lines(equipped_item, player=player, is_equipped=True)
            surfs1, tw1, th1 = self._measure_tooltip(lines1)
            surfs2, tw2, th2 = self._measure_tooltip(lines2)

            gap = 12
            total_w = tw1 + gap + tw2
            total_h = max(th1, th2)

            # Horizontal placement: right of cursor, or flip left if overflowing
            if mx + 16 + total_w <= SCREEN_WIDTH - 10:
                tx1 = mx + 16
            elif mx - 16 - total_w >= 10:
                tx1 = mx - 16 - total_w
            else:
                tx1 = max(10, min(SCREEN_WIDTH - total_w - 10, mx + 16))
            tx2 = tx1 + tw1 + gap

            # Vertical placement: below cursor, or flip up if overflowing
            ty = my + 16
            if ty + total_h > SCREEN_HEIGHT - 10:
                ty = max(10, my - total_h - 8)
            if ty < 10:
                ty = 10

            r1 = self._get_item_rarity_color(item)
            r2 = self._get_item_rarity_color(equipped_item)

            self._draw_tooltip_box(target_surf, tx1, ty, tw1, th1, surfs1, r1)
            self._draw_tooltip_box(target_surf, tx2, ty, tw2, th2, surfs2, r2)
            return lines1 + lines2
        else:
            lines = self._build_tooltip_lines(item, player=player, is_equipped=False)
            surfs, tw, th = self._measure_tooltip(lines)

            tx = max(10, min(SCREEN_WIDTH - tw - 12, mx + 16))
            ty = my + 16
            if ty + th > SCREEN_HEIGHT - 10:
                ty = max(10, my - th - 8)
            if ty < 10:
                ty = 10

            r = self._get_item_rarity_color(item)
            self._draw_tooltip_box(target_surf, tx, ty, tw, th, surfs, r)
            return lines

    def _render_reticle(self, target_surf, player, camera, mouse_x, mouse_y, inventory=None, world=None):
        tx, ty = camera.screen_to_tile(mouse_x, mouse_y)
        tile_world_x = tx * SCALED_TILE
        tile_world_y = ty * SCALED_TILE
        sx, sy = camera.world_to_screen(tile_world_x, tile_world_y)

        reach_dist = math.hypot(player.center_x - (tile_world_x + SCALED_TILE / 2),
                                player.center_y - (tile_world_y + SCALED_TILE / 2))
        in_reach = (reach_dist <= SCALED_TILE * 5.5)

        tile_size = int(SCALED_TILE * getattr(camera, "zoom", 1.0))
        reticle_surf = self.reticle_in_reach if in_reach else self.reticle_out_of_reach
        if getattr(camera, "zoom", 1.0) != 1.0:
            reticle_surf = pygame.transform.scale(reticle_surf, (tile_size, tile_size))
        target_surf.blit(reticle_surf, (sx, sy))

        # Progressive Block Breaking Progress Bar over targeted tile
        if world and hasattr(world, "tile_damage") and (tx, ty) in world.tile_damage:
            cur_dmg = world.tile_damage.get((tx, ty), 0.0)
            from src.constants import TILE_PROPS
            t_id = world.get_tile(tx, ty)
            prop = TILE_PROPS.get(t_id, {})
            max_h = max(1, prop.get("hardness", 20))
            break_pct = max(0.0, min(1.0, float(cur_dmg) / float(max_h)))
            if break_pct > 0.0:
                bar_w = tile_size - 4
                bar_h = max(4, int(4 * getattr(camera, "zoom", 1.0)))
                bx = sx + 2
                by = sy + tile_size - bar_h - 2
                # Dark backing
                pygame.draw.rect(target_surf, (15, 18, 28, 230), (bx - 1, by - 1, bar_w + 2, bar_h + 2), border_radius=2)
                # Outer border
                pygame.draw.rect(target_surf, (180, 140, 50), (bx - 1, by - 1, bar_w + 2, bar_h + 2), 1, border_radius=2)
                # Filled progress (transitions from yellow to hot orange as it nears breaking)
                fill_w = int(bar_w * break_pct)
                if fill_w > 0:
                    bar_col = (255, 215, 60) if break_pct < 0.6 else (255, 120, 30)
                    pygame.draw.rect(target_surf, bar_col, (bx, by, fill_w, bar_h), border_radius=1)

        # Dynamic Attack Recharge Gauge under cursor when wielding a weapon on cooldown
        if inventory:
            active_item = inventory.get_active_item() if hasattr(inventory, "get_active_item") else None
            is_weapon = active_item and (active_item.data.get("cat") == "weapon" or active_item.data.get("damage", 0) > 0)
            if is_weapon and getattr(player, "attack_cooldown", 0.0) > 0:
                gauge_w = 26
                gauge_h = 5
                gx = mouse_x - gauge_w // 2
                gy = mouse_y + 18
                max_cd = max(0.001, getattr(player, "max_attack_cooldown", 0.24))
                charge = max(0.0, min(1.0, 1.0 - (player.attack_cooldown / max_cd)))
                # Background plate
                bg_rect = pygame.Rect(gx, gy, gauge_w, gauge_h)
                target_surf.blit(self.gauge_bg, (gx, gy))
                pygame.draw.rect(target_surf, (40, 50, 75), bg_rect, 1, border_radius=2)
                # Charged progress bar
                fill_w = int((gauge_w - 2) * charge)
                if fill_w > 0:
                    fill_rect = pygame.Rect(gx + 1, gy + 1, fill_w, gauge_h - 2)
                    fill_col = (255, 215, 80) if charge < 0.9 else (120, 240, 255)
                    pygame.draw.rect(target_surf, fill_col, fill_rect, border_radius=1)

    def get_game_time_string(self, sky):
        """Returns formatted (time_str, period, is_night) from sky DayNightCycle time_of_day."""
        t = getattr(sky, "time_of_day", 0.25)
        total_hours = (t * 24.0 + 6.0) % 24.0
        hour = int(total_hours) % 24
        minute = int((total_hours * 60) % 60)
        period = "AM" if hour < 12 else "PM"
        disp_hour = hour % 12
        if disp_hour == 0:
            disp_hour = 12
        time_str = f"{disp_hour}:{minute:02d} {period}"
        is_night = getattr(sky, "is_night", False)
        return time_str, period, is_night

    def _render_clock_widget(self, target_surf, sky):
        """Displays in-game celestial time (12-hour AM/PM) with Sun/Moon icon docked below or beside the minimap."""
        time_str, period, is_night = self.get_game_time_string(sky)

        # Placement docked under the radar minimap (corner mode) or at top right
        mw = 148
        mh = 24
        mx = SCREEN_WIDTH - mw - 16
        if getattr(self, "minimap", None) and self.minimap.is_open and self.minimap.mode == "corner":
            my = 16 + 108 + 6  # 130
        else:
            my = 16

        bg_rect = pygame.Rect(mx, my, mw, mh)
        pygame.draw.rect(target_surf, (20, 24, 38, 235), bg_rect, border_radius=6)
        pygame.draw.rect(target_surf, (218, 165, 32), bg_rect, 1, border_radius=6)

        # Celestial Icon
        icon = self.clock_moon_icon if is_night else self.clock_sun_icon
        if icon:
            target_surf.blit(icon, (mx + 6, my + 4))
        else:
            sym = "☾" if is_night else "☀"
            sym_col = (180, 215, 255) if is_night else (255, 215, 70)
            txt_sym = self.font.render(sym, True, sym_col)
            target_surf.blit(txt_sym, (mx + 8, my + 3))

        # Time readout & Phase tag badge (Cached: only re-render when minute string or day/night changes)
        if getattr(self, "_cached_clock_str", None) != time_str or getattr(self, "_cached_clock_night", None) != is_night:
            self._cached_clock_str = time_str
            self._cached_clock_night = is_night
            t_col = (180, 220, 255) if is_night else (255, 230, 110)
            self._cached_clock_tsurf = self.font_sm.render(time_str, True, t_col)
            phase_str = "NIGHT" if is_night else "DAY"
            phase_col = (140, 175, 230) if is_night else (230, 180, 80)
            self._cached_clock_psurf = self.font_sm.render(phase_str, True, phase_col)

        target_surf.blit(self._cached_clock_tsurf, (mx + 28, my + 5))
        target_surf.blit(self._cached_clock_psurf, (mx + mw - self._cached_clock_psurf.get_width() - 8, my + 5))
