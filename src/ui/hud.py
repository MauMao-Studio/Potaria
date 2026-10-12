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
    CAT_TOOL
)
from src.ui.inventory import ITEM_REGISTRY
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
        self._cached_mp_key = None
        self._cached_mp_surf = None

        # Chat & Console input state
        self.chat_active = False
        self.chat_input_text = ""
        self.local_chat_history = []
        self.tooltip_mode = "detailed"

    def render(self, target_surf, player, inventory, crafting_system, camera, mouse_x, mouse_y, world=None, combat=None, lan_client=None, render_dragged=True, sky=None):
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

        # 5. Quick Skill Bar with Cooldown Overlays (Bottom Center)
        self._render_skill_bar(target_surf, player)

        # 6. Crafting Menu
        if inventory.is_open:
            crafting_system.render(target_surf, mouse_x, mouse_y, self.font)

        # 7. Item Tooltip (Rich Rarity, Stats, Description, Special Effects & Lore)
        if hovered_slot and hovered_slot.data:
            self._render_tooltip(target_surf, mouse_x, mouse_y, hovered_slot)

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

        # 10. Reticle & Attack Recharge Gauge & Mining Progress
        self._render_reticle(target_surf, player, camera, mouse_x, mouse_y, inventory=inventory, world=world)

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
        start_y = 18

        # Life Label (Cached)
        hp_key = (player.stats.hp, player.stats.max_hp, player.stats.level)
        if hp_key != self._cached_hp_key:
            self._cached_hp_key = hp_key
            self._cached_hp_surf = self.font.render(f"Life: {player.stats.hp} / {player.stats.max_hp}  (Lv.{player.stats.level})", True, (255, 90, 90))
        target_surf.blit(self._cached_hp_surf, (start_x, start_y - 15))

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

        # Mana Bar (Fixed 260px wide bar beneath hearts)
        mp_y = start_y + rows * 24 + 2
        mp_w = container_w
        mp_pct = max(0.0, min(1.0, player.stats.mp / float(max(1, player.stats.max_mp))))
        
        pygame.draw.rect(target_surf, (15, 25, 45), (start_x, mp_y, mp_w, 10), border_radius=3)
        if mp_pct > 0:
            pygame.draw.rect(target_surf, (50, 160, 255), (start_x, mp_y, int(mp_w * mp_pct), 10), border_radius=3)
        pygame.draw.rect(target_surf, (80, 120, 180), (start_x, mp_y, mp_w, 10), 1, border_radius=3)

        int_mp = int(player.stats.mp)
        mp_key = (int_mp, player.stats.max_mp)
        if mp_key != self._cached_mp_key:
            self._cached_mp_key = mp_key
            self._cached_mp_surf = self.font_sm.render(f"MP: {int_mp} / {player.stats.max_mp}", True, (200, 230, 255))
        target_surf.blit(self._cached_mp_surf, (start_x + mp_w // 2 - self._cached_mp_surf.get_width() // 2, mp_y - 1))

        # Oxygen / Breath Meter (Minecraft-style 10 Air Bubbles displayed when swimming or depleted)
        if getattr(player, "in_water", False) or getattr(player, "oxygen", 100.0) < 99.0:
            bubble_y = mp_y + 14
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
        """Draws active skill icons and cooldown sweeps dynamically from player's hotkey loadout."""
        skills = list(player.skills.hotkey_bindings.items()) if hasattr(player.skills, "hotkey_bindings") else [
            ("Q", "power_slash"), ("F", "whirlwind"), ("V", "dash"), ("R", "fireball")
        ]
        bw, bh = 42, 42
        gap = 8
        total_w = len(skills) * (bw + gap) - gap
        start_x = (SCREEN_WIDTH - total_w) // 2
        start_y = SCREEN_HEIGHT - 54

        for i, (key, s_id) in enumerate(skills):
            sx = start_x + i * (bw + gap)
            rect = pygame.Rect(sx, start_y, bw, bh)

            is_learned = s_id in player.skills.learned_skills if s_id else False
            cd_left = player.skills.cooldowns.get(s_id, 0.0) if s_id else 0.0

            # Slot box
            pygame.draw.rect(target_surf, (35, 40, 60, 220), rect, border_radius=6)
            pygame.draw.rect(target_surf, (120, 140, 180) if is_learned else (60, 65, 80), rect, 1, border_radius=6)

            # Hotkey badge
            k_txt = self.font.render(key, True, (255, 215, 0) if is_learned else (110, 110, 110))
            target_surf.blit(k_txt, (sx + 4, start_y + 2))

            # Skill level indicator
            if is_learned and hasattr(player.skills, "get_skill_level"):
                lvl = player.skills.get_skill_level(s_id)
                lvl_txt = self.font_sm.render(f"Lv.{lvl}", True, (255, 230, 80))
                target_surf.blit(lvl_txt, (sx + bw - lvl_txt.get_width() - 3, start_y + 2))

            # Draw Skill Icon if learned / available
            icon_drawn = False
            if s_id and hasattr(self.asset_factory, "skill_icons"):
                # Check for evolved form icon name if evolved
                is_evolved = hasattr(player.skills, "is_skill_evolved") and player.skills.is_skill_evolved(s_id)
                s_def = SKILL_DEFINITIONS.get(s_id, {})
                ev_name = s_def.get("evolved_name", "").lower().replace(" ", "_")
                icon_surf = self.asset_factory.skill_icons.get(ev_name) if is_evolved else None
                if not icon_surf:
                    icon_surf = self.asset_factory.skill_icons.get(s_id)
                if icon_surf:
                    icon_scaled = pygame.transform.scale(icon_surf, (28, 28))
                    if not is_learned:
                        # Dim locked / unlearned skill icon
                        dim_surf = icon_scaled.copy()
                        dim_surf.fill((60, 60, 60, 160), special_flags=pygame.BLEND_RGBA_MULT)
                        target_surf.blit(dim_surf, (sx + 7, start_y + 9))
                    else:
                        target_surf.blit(icon_scaled, (sx + 7, start_y + 9))
                    icon_drawn = True

            # Skill name abbreviation fallback or overlay if no icon
            if not icon_drawn:
                if s_id and hasattr(player.skills, "get_skill_name"):
                    s_name = player.skills.get_skill_name(s_id)[:3]
                else:
                    s_name = SKILL_DEFINITIONS.get(s_id, {}).get("name", "---")[:3] if s_id else "---"
                n_txt = self.font_sm.render(s_name, True, (255, 255, 255) if is_learned else (110, 110, 110))
                target_surf.blit(n_txt, (sx + 14, start_y + 20))

            # Cooldown shadow sweep
            if cd_left > 0 and s_id in SKILL_DEFINITIONS:
                max_cd = SKILL_DEFINITIONS[s_id]["cooldown"]
                sweep_pct = cd_left / max_cd
                sweep_h = int(bh * sweep_pct)
                cd_rect = pygame.Rect(sx, start_y + (bh - sweep_h), bw, sweep_h)
                cd_surf = pygame.Surface((bw, sweep_h), pygame.SRCALPHA)
                cd_surf.fill((0, 0, 0, 160))
                target_surf.blit(cd_surf, cd_rect.topleft)

                cd_txt = self.font_sm.render(f"{cd_left:.1f}", True, (255, 255, 255))
                target_surf.blit(cd_txt, (sx + bw // 2 - cd_txt.get_width() // 2, start_y + 12))

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
            console_y = SCREEN_HEIGHT - 75 - console_h
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
            box_y = SCREEN_HEIGHT - 65
            box_rect = pygame.Rect(cx, box_y, box_width, 24)
            pygame.draw.rect(target_surf, (20, 25, 40, 245), box_rect, border_radius=4)
            pygame.draw.rect(target_surf, COLOR_GOLD, box_rect, 1, border_radius=4)
            cursor_vis = "_" if int(pygame.time.get_ticks() / 400) % 2 == 0 else ""
            in_surf = self.font_sm.render(f"> {self.chat_input_text}{cursor_vis}", True, (255, 255, 255))
            target_surf.blit(in_surf, (cx + 6, box_y + 4))

        # Mode B: Idle (Render recent active messages as compact floating pills)
        else:
            base_y = SCREEN_HEIGHT - 75 - len(display_lines) * 18
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

    def _render_tooltip(self, target_surf, mx, my, item):
        """Rich Diablo/Torchlight-style item tooltip with rarity tiers, stats, lore, and descriptions."""
        data = item.data
        name = data.get("name", item.item_id)
        cat = data.get("cat", "item").replace("_", " ").title()
        rarity = data.get("rarity", RARITY_COMMON)
        r_color = RARITY_COLORS.get(rarity, (220, 220, 220))

        is_compact = getattr(self, "tooltip_mode", "detailed") == "compact"
        lines = []
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
            if data.get("def", 0) > 0:
                lines.append((f"Defense: +{data['def']}", (140, 230, 140), self.font_sm))
            if data.get("hp", 0) > 0:
                lines.append((f"Max HP: +{data['hp']}", (255, 120, 120), self.font_sm))
            if data.get("heal", 0) > 0:
                lines.append((f"Restores +{data['heal']} Health", (255, 110, 110), self.font_sm))
        else:
            # 3. Detailed Numeric Combat & Mining Stats
            if data.get("damage", 0) > 0:
                if data.get("cat") == CAT_TOOL or data.get("cat") == "tool":
                    lines.append((f"Tool Damage: {data['damage']}", (190, 205, 225), self.font_sm))
                else:
                    lines.append((f"Weapon Power: {data['damage']} Damage", (255, 215, 100), self.font_sm))
            if data.get("cat") == "weapon" or (data.get("damage", 0) > 0 and data.get("cat") != CAT_TOOL):
                iid = item.item_id.lower()
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

            if data.get("def", 0) > 0:
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

            # 4. Special Effects (Bulleted for upper rarities: Epic, Mythic, Legendary, Ancient)
            effects = data.get("effects", [])
            iid = item.item_id.lower()
            rarity_str = str(rarity).lower()
            is_high_tier = rarity_str in (RARITY_EPIC, RARITY_MYTHIC, RARITY_LEGENDARY, RARITY_ANCIENT, "epic", "mythic", "legendary", "ancient")
            if "wood" not in iid and is_high_tier:
                if effects:
                    for eff in effects:
                        lines.append((f"• {eff}", (100, 240, 240), self.font_sm))
                elif data.get("special"):
                    lines.append((f"Special: {data['special']}", (100, 240, 240), self.font_sm))

            # 5. Usage / Description
            desc = data.get("desc")
            if not desc or str(desc).strip() == "":
                desc = f"A fine {rarity.title()} {cat.lower()} radiating elemental potency."
            lines.append((desc, (215, 225, 240), self.font_sm))

            # 6. Lore Quote (Diablo / Torchlight style) - Only Legendary, Mythic, Ancient
            rarity_str = str(rarity).lower()
            if data.get("lore") and rarity_str in (RARITY_LEGENDARY, RARITY_MYTHIC, RARITY_ANCIENT, "legendary", "mythic", "ancient"):
                lines.append((data["lore"], (240, 205, 120), self.font_lore))

        # Calculate bounding dimensions
        rendered_surfs = [fnt.render(text, True, col) for text, col, fnt in lines]
        tw = max(s.get_width() for s in rendered_surfs) + 20
        th = sum(s.get_height() + 3 for s in rendered_surfs) + 12

        tx = min(SCREEN_WIDTH - tw - 12, mx + 16)
        ty = min(SCREEN_HEIGHT - th - 12, my + 16)
        if ty < 10:
            ty = 10

        rect = pygame.Rect(tx, ty, tw, th)
        # Background plate with rarity-colored border
        pygame.draw.rect(target_surf, (20, 24, 38, 245), rect, border_radius=6)
        pygame.draw.rect(target_surf, r_color, rect, 1, border_radius=6)

        cur_y = ty + 6
        for s in rendered_surfs:
            target_surf.blit(s, (tx + 10, cur_y))
            cur_y += s.get_height() + 3
        return lines

    def _render_reticle(self, target_surf, player, camera, mouse_x, mouse_y, inventory=None, world=None):
        tx, ty = camera.screen_to_tile(mouse_x, mouse_y)
        tile_world_x = tx * SCALED_TILE
        tile_world_y = ty * SCALED_TILE
        sx, sy = camera.world_to_screen(tile_world_x, tile_world_y)

        reach_dist = math.hypot(player.center_x - (tile_world_x + SCALED_TILE / 2),
                                player.center_y - (tile_world_y + SCALED_TILE / 2))
        in_reach = (reach_dist <= SCALED_TILE * 5.5)

        reticle_surf = self.reticle_in_reach if in_reach else self.reticle_out_of_reach
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
                bar_w = SCALED_TILE - 4
                bar_h = 4
                bx = sx + 2
                by = sy + SCALED_TILE - 6
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

        # Time readout
        t_col = (180, 220, 255) if is_night else (255, 230, 110)
        t_surf = self.font_sm.render(time_str, True, t_col)
        target_surf.blit(t_surf, (mx + 28, my + 5))

        # Phase tag badge
        phase_str = "NIGHT" if is_night else "DAY"
        phase_col = (140, 175, 230) if is_night else (230, 180, 80)
        p_surf = self.font_sm.render(phase_str, True, phase_col)
        target_surf.blit(p_surf, (mx + mw - p_surf.get_width() - 8, my + 5))
