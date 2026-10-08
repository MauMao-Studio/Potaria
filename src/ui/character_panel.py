"""
Potaria - Character & Paperdoll Equipment Panel (Chroisen Style)
Displays Spud's equipped gear slots (Head, Chest, Legs, Weapon, Accessory),
real-time RPG statistics, EXP bar, active skill hotkey loadout (Q, F, V, R),
and learned skills grimoire with hover tooltips and interactive assignment.
Developer: Kurados
"""

import pygame
from src.constants import (
    SCREEN_WIDTH, SCREEN_HEIGHT, COLOR_GOLD,
    RARITY_COMMON, RARITY_UNCOMMON, RARITY_RARE, RARITY_EPIC,
    RARITY_LEGENDARY, RARITY_MYTHIC, RARITY_ANCIENT, RARITY_COLORS, CAT_WEAPON, CAT_TOOL
)
from src.rpg.equipment import (
    SLOT_HEAD, SLOT_CHEST, SLOT_LEGS, SLOT_WEAPON, SLOT_ACCESSORY, ARMOR_DATA
)
from src.rpg.skills import SKILL_DEFINITIONS
from src.ui.inventory import ITEM_REGISTRY

class CharacterPanel:
    def __init__(self, asset_factory):
        self.asset_factory = asset_factory
        self.is_open = False
        self.selected_hotkey = "Q" # Currently selected hotkey for binding (Q, F, V, R)
        self.selected_grimoire_skill = None
        self.hovered_skill_id = None
        
        # Fonts
        pygame.font.init()
        self.font_title = pygame.font.SysFont("Arial", 18, bold=True)
        self.font = pygame.font.SysFont("Arial", 14)
        self.font_bold = pygame.font.SysFont("Arial", 13, bold=True)
        self.font_sm = pygame.font.SysFont("Arial", 11)

        # Slot bounding rects for mouse interaction
        self.slot_rects = {}
        self.hotkey_rects = {}
        self.grimoire_rects = {}

    def toggle(self):
        self.is_open = not self.is_open

    def handle_click(self, mouse_x, mouse_y, player, inventory, is_right_click=False):
        """Allows clicking equipped slots to unequip, or selecting and assigning combat skills."""
        if not self.is_open:
            return False

        # 1. Paperdoll Unequip Slots
        for slot_name, rect in self.slot_rects.items():
            if rect.collidepoint(mouse_x, mouse_y):
                current_item = player.equipment.slots[slot_name]
                if current_item:
                    remaining = inventory.add_item(current_item, 1)
                    if remaining == 0:
                        player.equipment.unequip(slot_name, player.stats)
                        player.sound_manager.play("place")
                    return True

        # 2. Hotkey Loadout Buttons ([Q], [F], [V], [R])
        for hotkey, rect in self.hotkey_rects.items():
            if rect.collidepoint(mouse_x, mouse_y):
                if is_right_click:
                    # Right-click unbinds/clears slot
                    player.skills.assign_skill(hotkey, None)
                    player.sound_manager.play("place")
                    return True
                else:
                    self.selected_hotkey = hotkey
                    # If player had previously clicked a learned skill in grimoire, assign it immediately!
                    if self.selected_grimoire_skill and self.selected_grimoire_skill in player.skills.learned_skills:
                        success = player.skills.assign_skill(hotkey, self.selected_grimoire_skill)
                        if success:
                            player.sound_manager.play("craft")
                        self.selected_grimoire_skill = None
                    else:
                        player.sound_manager.play("place")
                    return True

        # 3. Grimoire Learned Skill Selection
        for s_id, rect in self.grimoire_rects.items():
            if rect.collidepoint(mouse_x, mouse_y):
                if s_id in player.skills.learned_skills:
                    self.selected_grimoire_skill = s_id
                    success = player.skills.assign_skill(self.selected_hotkey, s_id)
                    if success:
                        player.sound_manager.play("craft")
                    return True

        # 4. Consume click inside panel boundaries to prevent accidental attacks/mining
        pw, ph = 560, 520
        px = SCREEN_WIDTH // 2 - pw // 2
        py = SCREEN_HEIGHT // 2 - ph // 2
        if pygame.Rect(px, py, pw, ph).collidepoint(mouse_x, mouse_y):
            return True

        return False

    def handle_key(self, event, player, key_bindings=None):
        """Allows hovering over a learned skill and pressing configured skill keys to bind it immediately."""
        if not self.is_open:
            return False

        target_skill = self.hovered_skill_id or self.selected_grimoire_skill
        if not target_skill or target_skill not in player.skills.learned_skills:
            return False

        k_map = {
            pygame.K_q: "Q",
            pygame.K_f: "F",
            pygame.K_v: "V",
            pygame.K_r: "R"
        }
        if key_bindings:
            k_map = {
                key_bindings.get("Skill Q", pygame.K_q): "Q",
                key_bindings.get("Skill F", pygame.K_f): "F",
                key_bindings.get("Skill V", pygame.K_v): "V",
                key_bindings.get("Skill R", pygame.K_r): "R",
            }
        if event.key in k_map:
            hotkey = k_map[event.key]
            success = player.skills.assign_skill(hotkey, target_skill)
            if success:
                self.selected_hotkey = hotkey
                player.sound_manager.play("craft")
                return True
        return False

    def render(self, target_surf, player, mouse_x, mouse_y):
        if not self.is_open:
            return

        pw, ph = 560, 520
        px = SCREEN_WIDTH // 2 - pw // 2
        py = SCREEN_HEIGHT // 2 - ph // 2

        # Panel Frame
        panel_rect = pygame.Rect(px, py, pw, ph)
        pygame.draw.rect(target_surf, (24, 28, 44, 245), panel_rect, border_radius=10)
        pygame.draw.rect(target_surf, COLOR_GOLD, panel_rect, 2, border_radius=10)

        # Header Title
        title_txt = self.font_title.render(f"CHARACTER STATUS  •  SPUD (Lv. {player.stats.level})", True, (255, 230, 100))
        target_surf.blit(title_txt, (px + 20, py + 16))

        # Close Hint
        hint = self.font_sm.render("[C] Close Panel", True, (160, 175, 200))
        target_surf.blit(hint, (px + pw - hint.get_width() - 20, py + 19))

        # ----------------------------------------------------
        # 1. Left Side: Equipment Paperdoll Slots (Head, Chest, Legs, Accessory)
        # ----------------------------------------------------
        slot_defs = [
            (SLOT_HEAD, "HEAD", px + 30, py + 52),
            (SLOT_CHEST, "CHEST", px + 30, py + 106),
            (SLOT_LEGS, "LEGS", px + 30, py + 160),
            (SLOT_ACCESSORY, "ACCESSORY", px + 30, py + 214),
        ]

        hovered_item = None

        for slot_name, label, sx, sy in slot_defs:
            rect = pygame.Rect(sx, sy, 42, 42)
            self.slot_rects[slot_name] = rect

            pygame.draw.rect(target_surf, (38, 44, 62), rect, border_radius=6)
            pygame.draw.rect(target_surf, (100, 115, 145), rect, 1, border_radius=6)

            equipped_id = player.equipment.slots.get(slot_name)
            if equipped_id:
                icon = self.asset_factory.items.get(equipped_id)
                if icon:
                    target_surf.blit(icon, (sx + 9, sy + 9))

                if rect.collidepoint(mouse_x, mouse_y):
                    pygame.draw.rect(target_surf, (255, 230, 80), rect, 2, border_radius=6)
                    hovered_item = equipped_id
            else:
                lbl_surf = self.font_sm.render(label[:4], True, (115, 125, 145))
                target_surf.blit(lbl_surf, (sx + 21 - lbl_surf.get_width() // 2, sy + 14))

            lbl_name = self.font_sm.render(label, True, (200, 210, 230))
            target_surf.blit(lbl_name, (sx + 50, sy + 14))

        # Active Hotbar Weapon Display (Weapons are held in hand from hotbar!)
        hw_y = py + 268
        hw_rect = pygame.Rect(px + 30, hw_y, 42, 42)
        pygame.draw.rect(target_surf, (32, 38, 55), hw_rect, border_radius=6)
        pygame.draw.rect(target_surf, (140, 160, 210), hw_rect, 1, border_radius=6)
        
        held_weapon = getattr(player.equipment, "active_weapon_id", None)
        if held_weapon:
            hw_icon = self.asset_factory.items.get(held_weapon)
            if hw_icon:
                target_surf.blit(hw_icon, (px + 39, hw_y + 9))
            w_name = ARMOR_DATA.get(held_weapon, {}).get("name", held_weapon.replace("_", " ").title())
            hw_title = self.font_sm.render("IN HAND (HOTBAR)", True, (255, 215, 100))
            hw_name = self.font_sm.render(w_name[:16], True, (255, 255, 255))
            target_surf.blit(hw_title, (px + 78, hw_y + 6))
            target_surf.blit(hw_name, (px + 78, hw_y + 22))
            if hw_rect.collidepoint(mouse_x, mouse_y):
                pygame.draw.rect(target_surf, (255, 230, 80), hw_rect, 2, border_radius=6)
                hovered_item = held_weapon
        else:
            hw_none = self.font_sm.render("IN HAND: (None)", True, (130, 140, 160))
            hw_sub = self.font_sm.render("Select weapon on hotbar", True, (100, 110, 130))
            target_surf.blit(hw_none, (px + 78, hw_y + 6))
            target_surf.blit(hw_sub, (px + 78, hw_y + 22))

        # ----------------------------------------------------
        # 2. Right Side: RPG Stats Breakdown
        # ----------------------------------------------------
        rx = px + 235
        ry = py + 52

        stats = player.stats
        mp_rate = stats.base_mp_regen + getattr(stats, "bonus_mp_regen", 0.0)
        atk_spd = getattr(stats, "total_atk_speed", 1.0)
        stat_lines = [
            (f"HP: {stats.hp} / {stats.max_hp}", (255, 100, 100)),
            (f"MP: {int(stats.mp)} / {stats.max_mp}", (100, 180, 255)),
            (f"Mana Regen: {mp_rate:.1f} MP/s", (120, 210, 255)),
            (f"Physical ATK: {stats.total_atk} ({stats.base_atk} + {stats.bonus_atk})", (255, 215, 100)),
            (f"Attack Speed: {atk_spd:.2f}x ({int(atk_spd * 100)}%)", (255, 235, 140)),
            (f"Defense: {stats.total_def} ({stats.base_def} + {stats.bonus_def})", (160, 230, 160)),
            (f"Critical Rate: {stats.total_crit_rate:.1f}%", (255, 180, 80)),
            (f"Movement Speed: {stats.total_speed:.1f}", (220, 220, 255)),
        ]

        # EXP Bar
        exp_pct = max(0.0, min(1.0, stats.current_exp / float(max(1, stats.exp_to_next))))
        exp_bar_w = 320
        pygame.draw.rect(target_surf, (30, 20, 40), (rx, ry, exp_bar_w, 16), border_radius=4)
        if exp_pct > 0:
            pygame.draw.rect(target_surf, (218, 165, 32), (rx, ry, int(exp_bar_w * exp_pct), 16), border_radius=4)
        pygame.draw.rect(target_surf, (150, 140, 110), (rx, ry, exp_bar_w, 16), 1, border_radius=4)
        exp_txt = self.font_sm.render(f"EXP: {stats.current_exp} / {stats.exp_to_next}", True, (255, 255, 255))
        target_surf.blit(exp_txt, (rx + exp_bar_w // 2 - exp_txt.get_width() // 2, ry + 1))

        # Draw Stats Lines (compact spacing to make room for Coin Purse)
        for i, (line, color) in enumerate(stat_lines):
            st = self.font.render(line, True, color)
            target_surf.blit(st, (rx, ry + 22 + i * 19))

        # ----------------------------------------------------
        # 2.5 Dedicated Coin Purse Box (Gold, Silver, Copper)
        # ----------------------------------------------------
        coin_box_w = exp_bar_w
        coin_box_h = 72
        coin_box_y = py + 238
        coin_rect = pygame.Rect(rx, coin_box_y, coin_box_w, coin_box_h)

        pygame.draw.rect(target_surf, (18, 22, 34), coin_rect, border_radius=6)
        pygame.draw.rect(target_surf, (180, 150, 70), coin_rect, 1, border_radius=6)

        # Header with conversion hint
        cp_title = self.font_bold.render("COIN PURSE", True, (255, 230, 100))
        target_surf.blit(cp_title, (rx + 10, coin_box_y + 5))
        cp_ratio = self.font_sm.render("100c = 1s  •  100s = 1g", True, (135, 150, 175))
        target_surf.blit(cp_ratio, (rx + coin_box_w - cp_ratio.get_width() - 10, coin_box_y + 7))

        pygame.draw.line(target_surf, (50, 60, 85), (rx + 8, coin_box_y + 24), (rx + coin_box_w - 8, coin_box_y + 24), 1)

        # Coin amounts with graphical icons
        coins_meta = [
            ("gold_coin", f"{stats.gold_coins}g", (255, 215, 40), rx + 14),
            ("silver_coin", f"{stats.silver_coins}s", (215, 225, 240), rx + 112),
            ("copper_coin", f"{stats.copper_coins}c", (230, 140, 75), rx + 208),
        ]
        coin_row_y = coin_box_y + 29
        for c_id, txt, col, cx_pos in coins_meta:
            icon = self.asset_factory.items.get(c_id)
            if icon:
                scaled_icon = pygame.transform.scale(icon, (18, 18))
                target_surf.blit(scaled_icon, (cx_pos, coin_row_y))
            val_surf = self.font_bold.render(txt, True, col)
            target_surf.blit(val_surf, (cx_pos + 22, coin_row_y + 1))

        # Bottom subtle total purchasing power
        tot_val_txt = self.font_sm.render(f"Total Purchasing Power: {stats.total_copper_value} Copper", True, (160, 175, 205))
        target_surf.blit(tot_val_txt, (rx + 10, coin_box_y + 52))

        # ----------------------------------------------------
        # 3. Bottom Section: Active Skill Loadout (Q, F, V, R)
        # ----------------------------------------------------
        by = py + 322
        active_title = self.font_bold.render("ACTIVE SKILL LOADOUT (Select Hotkey):", True, (255, 230, 100))
        target_surf.blit(active_title, (px + 30, by))

        hotkeys = [("Q", "power_slash"), ("F", "whirlwind"), ("V", "dash"), ("R", "fireball")]
        self.hovered_skill_id = None

        for i, (key, def_sid) in enumerate(hotkeys):
            hx = px + 30 + i * 126
            hy = by + 20
            h_rect = pygame.Rect(hx, hy, 120, 36)
            self.hotkey_rects[key] = h_rect

            # Determine currently assigned skill
            curr_sid = player.skills.hotkey_bindings.get(key)
            s_data = SKILL_DEFINITIONS.get(curr_sid, {}) if curr_sid else {}
            is_learned = (curr_sid in player.skills.learned_skills) if curr_sid else False
            is_selected = (key == self.selected_hotkey)

            # Slot border and background
            b_col = (45, 55, 80) if is_learned else (30, 32, 40)
            pygame.draw.rect(target_surf, b_col, h_rect, border_radius=6)
            border_col = COLOR_GOLD if is_selected else ((120, 150, 200) if is_learned else (70, 75, 90))
            border_thick = 2 if is_selected else 1
            pygame.draw.rect(target_surf, border_col, h_rect, border_thick, border_radius=6)

            # Hotkey Badge & Skill Name
            badge = self.font_bold.render(f"[{key}]", True, COLOR_GOLD if is_selected else (220, 220, 220))
            skill_name = s_data.get("name", "---")[:10] if (curr_sid and is_learned) else "(Empty)"
            name_txt = self.font_sm.render(skill_name, True, (255, 255, 255) if is_learned else (110, 110, 110))
            target_surf.blit(badge, (hx + 6, hy + 9))
            target_surf.blit(name_txt, (hx + 36, hy + 10))

            if h_rect.collidepoint(mouse_x, mouse_y):
                pygame.draw.rect(target_surf, (255, 240, 120), h_rect, 2, border_radius=6)
                if curr_sid:
                    self.hovered_skill_id = curr_sid

        # ----------------------------------------------------
        # 4. Learned Skills Grimoire & Selection
        # ----------------------------------------------------
        gy = by + 68
        grim_title = self.font_bold.render(f"LEARNED SKILLS GRIMOIRE (Click to Assign to [{self.selected_hotkey}]):", True, (100, 220, 255))
        target_surf.blit(grim_title, (px + 30, gy))

        all_skills = list(SKILL_DEFINITIONS.keys())
        for i, s_id in enumerate(all_skills):
            col = i % 4
            row = i // 4
            gx = px + 30 + col * 126
            gy_pos = gy + 22 + row * 40
            g_rect = pygame.Rect(gx, gy_pos, 120, 34)
            self.grimoire_rects[s_id] = g_rect

            s_data = SKILL_DEFINITIONS[s_id]
            is_learned = s_id in player.skills.learned_skills
            is_selected_grim = (s_id == getattr(self, "selected_grimoire_skill", None))
            
            # Find if currently bound to any hotkey
            bound_key = None
            for hk, sid in player.skills.hotkey_bindings.items():
                if sid == s_id:
                    bound_key = hk
                    break

            bg_col = (42, 68, 98) if is_selected_grim else ((30, 48, 70) if is_learned else (24, 26, 32))
            pygame.draw.rect(target_surf, bg_col, g_rect, border_radius=5)
            bd_col = COLOR_GOLD if is_selected_grim else ((80, 180, 240) if is_learned else (55, 60, 70))
            pygame.draw.rect(target_surf, bd_col, g_rect, 2 if is_selected_grim else 1, border_radius=5)

            # Name and status badge
            if is_learned:
                lvl = player.skills.get_skill_level(s_id) if hasattr(player.skills, "get_skill_level") else 1
                s_name = self.font_sm.render(f"{s_data['name'][:7]} L{lvl}", True, (255, 255, 255))
                target_surf.blit(s_name, (gx + 6, gy_pos + 4))
                status_txt = f"[{bound_key}]" if bound_key else "[Ready]"
                stat_surf = self.font_sm.render(status_txt, True, COLOR_GOLD if bound_key else (80, 220, 120))
                target_surf.blit(stat_surf, (gx + 6, gy_pos + 17))
            else:
                s_name = self.font_sm.render(s_data["name"][:9], True, (110, 115, 125))
                target_surf.blit(s_name, (gx + 6, gy_pos + 4))
                stat_surf = self.font_sm.render("[Locked]", True, (130, 70, 70))
                target_surf.blit(stat_surf, (gx + 6, gy_pos + 17))

            if g_rect.collidepoint(mouse_x, mouse_y):
                pygame.draw.rect(target_surf, (255, 230, 80), g_rect, 2, border_radius=5)
                self.hovered_skill_id = s_id

        # ----------------------------------------------------
        # 5. Tooltips
        # ----------------------------------------------------
        if hovered_item:
            held_id = getattr(player.equipment, "active_weapon_id", None)
            is_held = (hovered_item == held_id and hovered_item not in [player.equipment.slots.get(s) for s in [SLOT_HEAD, SLOT_CHEST, SLOT_LEGS, SLOT_ACCESSORY]])
            self._render_equipped_tooltip(target_surf, mouse_x, mouse_y, hovered_item, is_held=is_held)
        elif self.hovered_skill_id and self.hovered_skill_id in SKILL_DEFINITIONS:
            self._render_skill_tooltip(target_surf, mouse_x, mouse_y, player, self.hovered_skill_id)

    def _render_skill_tooltip(self, target_surf, mx, my, player, skill_id):
        """Displays rich hover description popup for combat skills in Character Status."""
        data = SKILL_DEFINITIONS.get(skill_id, {})
        is_learned = skill_id in player.skills.learned_skills
        lvl = player.skills.get_skill_level(skill_id) if hasattr(player.skills, "get_skill_level") else 1
        
        bound_key = None
        for hk, sid in player.skills.hotkey_bindings.items():
            if sid == skill_id:
                bound_key = hk
                break

        lines = []
        # Title with Level
        s_title = f"{data.get('name', skill_id)} (Lv. {lvl})" if is_learned else data.get("name", skill_id)
        lines.append((s_title, COLOR_GOLD if is_learned else (180, 180, 180), self.font_bold))
        
        # MP Cost and Cooldown
        mp = player.skills.get_skill_mp_cost(skill_id) if hasattr(player.skills, "get_skill_mp_cost") else data.get("mp_cost", 0)
        cd = player.skills.get_skill_cooldown(skill_id) if hasattr(player.skills, "get_skill_cooldown") else data.get("cooldown", 0.0)
        lines.append((f"{mp} MP  •  {cd:.1f}s Cooldown", (100, 200, 255), self.font_sm))

        # Power multiplier
        dmg = player.skills.get_skill_dmg_mult(skill_id) if hasattr(player.skills, "get_skill_dmg_mult") else data.get("dmg_mult", 0.0)
        if dmg > 0:
            lines.append((f"Power: {int(dmg * 100)}% Physical Attack", (255, 180, 80), self.font_sm))
        else:
            lines.append(("Utility / Mobility Skill", (200, 220, 255), self.font_sm))

        # Description
        desc = data.get("desc", "")
        if desc:
            lines.append((desc, (230, 235, 245), self.font_sm))

        # Assignment Status
        if not is_learned:
            lines.append(("[Locked] Find Skill Book in Caverns or Chests to learn!", (240, 90, 90), self.font_sm))
        elif lvl < 5:
            lines.append((f"[Lv. {lvl}/5] Use duplicate Skill Book to upgrade!", (255, 215, 100), self.font_sm))
        else:
            lines.append(("[MAX LEVEL REACHED]", (255, 215, 0), self.font_sm))

        if is_learned:
            if bound_key:
                lines.append((f"[Assigned to '{bound_key}'] Click to move to [{self.selected_hotkey}] (or press Q/F/V/R)", (80, 230, 120), self.font_sm))
            else:
                lines.append((f"[Learned] Click to assign to [{self.selected_hotkey}] (or press Q/F/V/R)", (120, 220, 255), self.font_sm))
            lines.append(("[Tip] Select slot then click skill, or press hotkey while hovering!", (255, 215, 120), self.font_sm))
            lines.append(("[Tip] Right-click active slot to unbind", (180, 195, 215), self.font_sm))

        surfs = [fnt.render(txt, True, col) for txt, col, fnt in lines]
        tw = max(s.get_width() for s in surfs) + 20
        th = sum(s.get_height() + 3 for s in surfs) + 12

        tx = min(SCREEN_WIDTH - tw - 12, mx + 16)
        ty = min(SCREEN_HEIGHT - th - 12, my + 16)
        if ty < 10:
            ty = 10

        rect = pygame.Rect(tx, ty, tw, th)
        pygame.draw.rect(target_surf, (20, 25, 40, 245), rect, border_radius=6)
        pygame.draw.rect(target_surf, (100, 180, 240) if is_learned else (120, 70, 70), rect, 1, border_radius=6)

        cy = ty + 6
        for s in surfs:
            target_surf.blit(s, (tx + 10, cy))
            cy += s.get_height() + 3

    def _render_equipped_tooltip(self, target_surf, mx, my, item_id, is_held=False):
        armor = ARMOR_DATA.get(item_id, {})
        reg = ITEM_REGISTRY.get(item_id, {})

        name = reg.get("name") or armor.get("name") or item_id
        rarity = reg.get("rarity") or armor.get("rarity") or RARITY_COMMON
        r_color = RARITY_COLORS.get(rarity, (255, 255, 255))

        if is_held:
            slot_name = "IN HAND (HOTBAR)"
        else:
            slot_name = armor.get("slot", "WEAPON" if reg.get("cat") == CAT_WEAPON else "EQUIPMENT").upper()

        lines = []
        lines.append((f"{name} [{rarity.upper()}]", r_color, self.font_bold))
        lines.append((f"Slot: {slot_name}", (255, 215, 100), self.font_sm))

        # Weapon damage / power
        if reg.get("cat") == CAT_WEAPON or (reg.get("damage", 0) > 0 and reg.get("cat") != CAT_TOOL):
            lines.append((f"+{reg.get('damage', 0)} Base Attack Power", (255, 180, 80), self.font_sm))
        elif reg.get("cat") == CAT_TOOL:
            lines.append((f"+{reg.get('damage', 0)} Tool Damage", (190, 205, 225), self.font_sm))

        # Armor and accessory stats
        if armor.get("def", 0) > 0:
            lines.append((f"+{armor['def']} Defense", (140, 240, 140), self.font_sm))
        if armor.get("hp", 0) > 0:
            lines.append((f"+{armor['hp']} Max HP", (255, 120, 120), self.font_sm))
        if armor.get("atk", 0) > 0:
            lines.append((f"+{armor['atk']} Attack", (255, 215, 100), self.font_sm))
        if armor.get("crit", 0) > 0:
            lines.append((f"+{armor['crit']}% Crit Chance", (255, 160, 60), self.font_sm))
        if armor.get("speed", 0) > 0 or reg.get("speed", 0) > 0:
            sp = armor.get("speed", reg.get("speed", 0))
            if reg.get("cat") == "weapon":
                lines.append((f"+{int(sp * 100)}% Attack Speed", (255, 235, 140), self.font_sm))
            else:
                lines.append((f"+{sp} Move Speed", (180, 200, 255), self.font_sm))
        if armor.get("mp_regen", 0) > 0 or reg.get("mp_regen", 0) > 0:
            reg_val = armor.get("mp_regen", reg.get("mp_regen", 0))
            lines.append((f"+{reg_val:.1f} MP/s Mana Regen", (120, 210, 255), self.font_sm))

        # Effects & Special Perks (Only Epic, Mythic, Legendary, Ancient; suppressed for wooden and low-tier)
        effects = reg.get("effects") or armor.get("effects", [])
        iid = item_id.lower()
        rarity_str = str(rarity).lower()
        is_high_tier = rarity_str in (RARITY_EPIC, RARITY_MYTHIC, RARITY_LEGENDARY, RARITY_ANCIENT, "epic", "mythic", "legendary", "ancient")
        if "wood" not in iid and is_high_tier:
            if effects:
                for eff in effects:
                    lines.append((f"• {eff}", (100, 240, 240), self.font_sm))
            else:
                special = reg.get("special") or armor.get("special")
                if special:
                    lines.append((f"Special: {special}", (100, 220, 255), self.font_sm))

        desc = reg.get("desc")
        if not desc or str(desc).strip() == "":
            desc = f"A fine {rarity.title()} equipment piece radiating elemental potency."
        lines.append((desc, (200, 215, 235), self.font_sm))

        lore = reg.get("lore")
        rarity_str = str(rarity).lower()
        if lore and rarity_str in (RARITY_LEGENDARY, RARITY_MYTHIC, RARITY_ANCIENT, "legendary", "mythic", "ancient"):
            lines.append((lore, (235, 200, 110), self.font_sm))

        if is_held:
            lines.append(("(Selected on hotbar in hand)", (140, 180, 220), self.font_sm))
        else:
            lines.append(("(Click slot to unequip)", (140, 150, 170), self.font_sm))

        surfs = [fnt.render(txt, True, col) for txt, col, fnt in lines]
        tw = max(s.get_width() for s in surfs) + 20
        th = sum(s.get_height() + 3 for s in surfs) + 12

        tx = min(SCREEN_WIDTH - tw - 12, mx + 16)
        ty = min(SCREEN_HEIGHT - th - 12, my + 16)
        if ty < 10:
            ty = 10

        rect = pygame.Rect(tx, ty, tw, th)
        pygame.draw.rect(target_surf, (20, 24, 38, 245), rect, border_radius=6)
        pygame.draw.rect(target_surf, r_color, rect, 1, border_radius=6)

        cy = ty + 6
        for s in surfs:
            target_surf.blit(s, (tx + 10, cy))
            cy += s.get_height() + 3
