"""
Potaria - Storage Chest Interactive UI Window
Provides a 20-slot storage window for depositing, withdrawing,
quick stacking, and managing items in player-placed chests.
Developer: Kurados
"""

import pygame
from src.constants import (
    SCREEN_WIDTH, SCREEN_HEIGHT, COLOR_GOLD,
    RARITY_COLORS, RARITY_COMMON
)
from src.ui.inventory import ItemStack, ITEM_REGISTRY, ITEM_ALIASES
from src.rpg.equipment import get_item_equipment_slot, get_equipped_item_for_slot, is_item_already_equipped

CHEST_SLOT_SIZE = 38
CHEST_SLOT_PAD = 4

class ChestStorageWindow:
    def __init__(self, asset_factory, sound_manager):
        self.asset_factory = asset_factory
        self.sound_manager = sound_manager

        self.width = 300
        self.height = 280
        # Position nicely next to open backpack inventory (which starts at x=20, y=20)
        self.x = 484
        self.y = 20

        self.is_open = False
        self.active_chest = None
        self.status_message = ""

        from src.ui.theme import font_bold, font_semibold, font_compact, font_regular
        self.font_title = font_bold(14)
        self.font_drag = font_semibold(13)
        self.font_btn = font_semibold(11)
        self.font_count = font_compact(10)
        self.font_sm = font_regular(10)
        self.tooltip_mode = "detailed"

    def open(self, chest, player=None, inventory=None):
        self.is_open = True
        self.active_chest = chest
        self.status_message = ""
        if inventory:
            inventory.is_open = True # Open backpack alongside chest
        if self.sound_manager:
            self.sound_manager.play("craft")

    def close(self):
        self.is_open = False
        self.active_chest = None
        self.status_message = ""

    def handle_click(self, mouse_x, mouse_y, is_right_click, player, inventory):
        if not self.is_open or not self.active_chest:
            return False

        panel_rect = pygame.Rect(self.x, self.y, self.width, self.height)
        if not panel_rect.collidepoint(mouse_x, mouse_y):
            # Click is outside chest window
            return False

        chest = self.active_chest

        # 1. Close Button [X]
        close_btn = pygame.Rect(self.x + self.width - 24, self.y + 6, 18, 18)
        if close_btn.collidepoint(mouse_x, mouse_y):
            self.close()
            return True

        # 2. Action Buttons along bottom
        # Quick Stack, Deposit All, Take All
        btn_y = self.y + self.height - 34
        b_quick = pygame.Rect(self.x + 12, btn_y, 84, 24)
        b_dep = pygame.Rect(self.x + 102, btn_y, 88, 24)
        b_take = pygame.Rect(self.x + 196, btn_y, 88, 24)

        if b_quick.collidepoint(mouse_x, mouse_y):
            deposited = chest.quick_stack_from_inventory(inventory)
            if self.sound_manager:
                self.sound_manager.play("place")
            self.status_message = f"Quick stacked {deposited} items!" if deposited else "No matching items to stack."
            return True

        if b_dep.collidepoint(mouse_x, mouse_y):
            deposited = chest.deposit_all_from_inventory(inventory)
            if self.sound_manager:
                self.sound_manager.play("place")
            self.status_message = f"Deposited {deposited} items!" if deposited else "Chest full or inventory empty."
            return True

        if b_take.collidepoint(mouse_x, mouse_y):
            taken = chest.take_all_to_inventory(inventory)
            if self.sound_manager:
                self.sound_manager.play("pickup")
            self.status_message = f"Looted {taken} items!" if taken else "Chest is empty."
            return True

        # 3. Chest Slots (4 rows of 5 columns = 20 slots)
        start_sx = self.x + 16
        start_sy = self.y + 36

        for row in range(4):
            for col in range(5):
                slot_idx = row * 5 + col
                if slot_idx >= chest.capacity:
                    continue
                sx = start_sx + col * (CHEST_SLOT_SIZE + CHEST_SLOT_PAD)
                sy = start_sy + row * (CHEST_SLOT_SIZE + CHEST_SLOT_PAD)
                s_rect = pygame.Rect(sx, sy, CHEST_SLOT_SIZE, CHEST_SLOT_SIZE)

                if s_rect.collidepoint(mouse_x, mouse_y):
                    current = chest.slots[slot_idx]
                    held = inventory.held_item

                    if not held:
                        if current:
                            if is_right_click and current.count > 1:
                                half = current.count // 2
                                inventory.held_item = current.clone(count=half)
                                current.count -= half
                            else:
                                inventory.held_item = current
                                chest.slots[slot_idx] = None
                            if self.sound_manager:
                                self.sound_manager.play("pickup")
                    else:
                        if current is None:
                            if is_right_click and held.count > 1:
                                chest.slots[slot_idx] = held.clone(count=1)
                                held.count -= 1
                            else:
                                chest.slots[slot_idx] = held
                                inventory.held_item = None
                            if self.sound_manager:
                                self.sound_manager.play("place")
                        else:
                            # Stacking or Swapping
                            canon_cur = ITEM_ALIASES.get(current.item_id, current.item_id)
                            canon_held = ITEM_ALIASES.get(held.item_id, held.item_id)
                            max_s = current.data.get("max_stack", 999)

                            if canon_cur == canon_held and max_s > 1:
                                if is_right_click:
                                    if current.count < max_s:
                                        current.count += 1
                                        held.count -= 1
                                        if held.count <= 0:
                                            inventory.held_item = None
                                else:
                                    space = max_s - current.count
                                    trans = min(space, held.count)
                                    current.count += trans
                                    held.count -= trans
                                    if held.count <= 0:
                                        inventory.held_item = None
                                if self.sound_manager:
                                    self.sound_manager.play("place")
                            else:
                                # Swap slots
                                chest.slots[slot_idx] = held
                                inventory.held_item = current
                                if self.sound_manager:
                                    self.sound_manager.play("pickup")
                    return True

        return True

    def render(self, target_surf, inventory, mouse_x, mouse_y, render_dragged=True, player=None, character_panel=None):
        if not self.is_open or not self.active_chest:
            return

        chest = self.active_chest

        # Shadow & Main Panel
        shadow = pygame.Rect(self.x + 4, self.y + 4, self.width, self.height)
        pygame.draw.rect(target_surf, (10, 12, 18, 160), shadow, border_radius=8)

        panel = pygame.Rect(self.x, self.y, self.width, self.height)
        panel_surf = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        panel_surf.fill((22, 28, 42, 245))
        target_surf.blit(panel_surf, (self.x, self.y))
        pygame.draw.rect(target_surf, (75, 95, 135), panel, 2, border_radius=8)
        pygame.draw.rect(target_surf, COLOR_GOLD, panel, 1, border_radius=8)

        # Header Title
        title_txt = "Storage Chest (20 Slots)"
        t_surf = self.font_title.render(title_txt, True, COLOR_GOLD)
        target_surf.blit(t_surf, (self.x + 14, self.y + 8))

        # Close [X] Button
        close_btn = pygame.Rect(self.x + self.width - 24, self.y + 6, 18, 18)
        is_close_hov = close_btn.collidepoint(mouse_x, mouse_y)
        pygame.draw.rect(target_surf, (160, 45, 45) if is_close_hov else (80, 30, 30), close_btn, border_radius=3)
        x_surf = self.font_btn.render("X", True, (255, 255, 255))
        target_surf.blit(x_surf, (close_btn.centerx - x_surf.get_width() // 2, close_btn.centery - x_surf.get_height() // 2))

        # Status Message if any
        if self.status_message:
            sm_surf = self.font_sm.render(self.status_message, True, (160, 230, 255))
            target_surf.blit(sm_surf, (self.x + 14, self.y + self.height - 52))

        # Render 20 Slots (4 rows x 5 cols)
        start_sx = self.x + 16
        start_sy = self.y + 36
        hovered_item = None

        for row in range(4):
            for col in range(5):
                slot_idx = row * 5 + col
                if slot_idx >= chest.capacity:
                    continue
                sx = start_sx + col * (CHEST_SLOT_SIZE + CHEST_SLOT_PAD)
                sy = start_sy + row * (CHEST_SLOT_SIZE + CHEST_SLOT_PAD)
                s_rect = pygame.Rect(sx, sy, CHEST_SLOT_SIZE, CHEST_SLOT_SIZE)
                is_hov = s_rect.collidepoint(mouse_x, mouse_y)

                slot_bg = (38, 48, 70) if not is_hov else (52, 68, 100)
                border_col = (75, 95, 135) if not is_hov else (255, 230, 80)
                pygame.draw.rect(target_surf, slot_bg, s_rect, border_radius=4)
                pygame.draw.rect(target_surf, border_col, s_rect, 1, border_radius=4)

                item = chest.slots[slot_idx]
                if item:
                    if is_hov:
                        hovered_item = item

                    # Item Icon
                    icon = self.asset_factory.items.get(item.item_id) if hasattr(self.asset_factory, "items") else None
                    if icon:
                        # Center 24x24 icon in 38x38 slot
                        target_surf.blit(icon, (sx + 7, sy + 7))
                    else:
                        pygame.draw.rect(target_surf, (180, 140, 80), (sx + 8, sy + 8, 22, 22), border_radius=3)

                    # Enhancement badge (+N)
                    enh = getattr(item, "enhancement_level", 0)
                    if enh > 0:
                        enh_surf = self.font_count.render(f"+{enh}", True, (80, 240, 255))
                        target_surf.blit(enh_surf, (sx + 2, sy + 2))

                    # Broken badge [!]
                    if getattr(item, "is_broken", False):
                        brk_surf = self.font_count.render("!", True, (255, 60, 60))
                        target_surf.blit(brk_surf, (sx + CHEST_SLOT_SIZE - 8, sy + 2))

                    # Count Label (if > 1)
                    if item.count > 1:
                        c_surf = self.font_count.render(str(item.count), True, (255, 255, 255))
                        cx = sx + CHEST_SLOT_SIZE - c_surf.get_width() - 3
                        cy = sy + CHEST_SLOT_SIZE - c_surf.get_height() - 2
                        target_surf.blit(c_surf, (cx, cy))

        # Bottom Action Buttons
        btn_y = self.y + self.height - 34
        b_quick = pygame.Rect(self.x + 12, btn_y, 84, 24)
        b_dep = pygame.Rect(self.x + 102, btn_y, 88, 24)
        b_take = pygame.Rect(self.x + 196, btn_y, 88, 24)

        for btn_r, label in [(b_quick, "Quick Stack"), (b_dep, "Deposit All"), (b_take, "Loot All")]:
            is_b_hov = btn_r.collidepoint(mouse_x, mouse_y)
            bg = (55, 75, 110) if is_b_hov else (38, 48, 72)
            border = (255, 230, 80) if is_b_hov else (75, 95, 135)
            pygame.draw.rect(target_surf, bg, btn_r, border_radius=4)
            pygame.draw.rect(target_surf, border, btn_r, 1, border_radius=4)
            b_txt = self.font_btn.render(label, True, (255, 255, 255) if not is_b_hov else (255, 235, 100))
            target_surf.blit(b_txt, (btn_r.centerx - b_txt.get_width() // 2, btn_r.centery - b_txt.get_height() // 2))

        # Tooltip for hovered item
        if hovered_item:
            p = player if player is not None else (getattr(inventory, "player", None) if inventory else None)
            self.render_tooltip(target_surf, hovered_item, mouse_x, mouse_y, player=p, character_panel=character_panel)

        # Foreground Dragged Item (ensures dragged items appear on top of the chest panel)
        if render_dragged and inventory and getattr(inventory, "held_item", None):
            held = inventory.held_item
            icon = self.asset_factory.items.get(held.item_id) if hasattr(self.asset_factory, "items") else None
            if icon:
                target_surf.blit(icon, (mouse_x - 12, mouse_y - 12))
            if getattr(held, "count", 1) > 1:
                cnt_txt = self.font_drag.render(str(held.count), True, (255, 255, 255))
                target_surf.blit(cnt_txt, (mouse_x + 4, mouse_y + 4))

    def _build_chest_tooltip_lines(self, item, player=None, is_equipped=False):
        if not item:
            return []
        if isinstance(item, str):
            item = ItemStack(item, 1)
        data = item.data if hasattr(item, "data") else {}
        name = data.get("name", getattr(item, "item_id", "Item"))
        rarity = str(data.get("rarity", "common")).lower()
        r_color = RARITY_COLORS.get(rarity, (220, 220, 220))
        lines = []
        if is_equipped:
            lines.append(("[ CURRENTLY EQUIPPED ]", COLOR_GOLD, self.font_title))
        lines.append((name, r_color, self.font_title))
        is_compact = getattr(self, "tooltip_mode", "detailed") == "compact"
        cat = data.get("cat", "item").replace("_", " ").title()
        lines.append((f"[{rarity.upper()} {cat.upper()}]", r_color, self.font_sm))
        if is_compact:
            if data.get("damage", 0) > 0:
                lines.append((f"Power: {data['damage']} Damage", (255, 215, 100), self.font_sm))
            elif data.get("atk", 0) > 0:
                lines.append((f"Attack: +{data['atk']}", (255, 215, 100), self.font_sm))
            if data.get("def", 0) > 0:
                lines.append((f"Defense: +{data['def']}", (160, 230, 160), self.font_sm))
            if data.get("hp", 0) > 0:
                lines.append((f"Max HP: +{data['hp']}", (255, 120, 120), self.font_sm))
            if getattr(item, "enhancement_level", 0) > 0:
                lines.append((f"+{item.enhancement_level} Enhanced", (80, 240, 255), self.font_sm))
            if getattr(item, "is_broken", False):
                lines.append(("[BROKEN]", (255, 70, 70), self.font_sm))
        else:
            if data.get("damage", 0) > 0:
                lines.append((f"Power: {data['damage']} Damage", (255, 215, 100), self.font_sm))
            if data.get("atk", 0) > 0 and data.get("damage", 0) == 0:
                lines.append((f"Attack: +{data['atk']}", (255, 215, 100), self.font_sm))
            if data.get("def", 0) > 0:
                lines.append((f"Defense: +{data['def']}", (160, 230, 160), self.font_sm))
            if data.get("hp", 0) > 0:
                lines.append((f"Max HP: +{data['hp']}", (255, 120, 120), self.font_sm))
            if getattr(item, "enhancement_level", 0) > 0:
                lines.append((f"Enhanced: +{item.enhancement_level} (Double Stats at +7)", (80, 240, 255), self.font_sm))
            if getattr(item, "is_broken", False):
                lines.append(("[BROKEN] Requires 1 Gold Coin repair at Mystic Trader!", (255, 70, 70), self.font_sm))

            base_rolls = getattr(item, "base_rolls", None)
            if base_rolls:
                roll_parts = [f"+{v} {k.upper()}" for k, v in base_rolls.items()]
                lines.append((f"Rolled Base Stats: {', '.join(roll_parts)}", (255, 230, 140), self.font_sm))

            item_tags = getattr(item, "tags", None) or data.get("tags", [])
            if item_tags:
                from src.rpg.equipment_update import TAG_REGISTRY
                tag_labels = [TAG_REGISTRY.get(t, {}).get("display_name", t.replace("_", " ").title()) for t in item_tags]
                lines.append((f"Tags: {' • '.join(tag_labels)}", (100, 220, 255), self.font_sm))

            from src.ui.theme import wrap_text_lines

            # Special Weapon Effects / Skills (Bulleted for upper rarities or items with perks, displayed BEFORE affixes)
            effects = data.get("effects", [])
            iid = str(getattr(item, "item_id", "")).lower()
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

            from src.rpg.equipment_update import build_set_tooltip_lines
            raw_id = getattr(item, "item_id", item if isinstance(item, str) else "")
            set_lines = build_set_tooltip_lines(raw_id, player=player, font=self.font_sm, wrap_width=300)
            lines.extend(set_lines)

            desc = data.get("desc")
            if desc:
                for dl in wrap_text_lines(desc, self.font_sm, 300):
                    lines.append((dl, (200, 210, 225), self.font_sm))

        return lines

    def _measure_chest_tooltip(self, lines):
        content_w = max((self.font_sm.size(text)[0] for text, _, _ in lines), default=140)
        tw = max(160, min(330, content_w + 24))
        th = sum(16 for _ in lines) + 12
        return tw, th

    def _draw_chest_card(self, target_surf, tx, ty, tw, th, lines):
        bg_rect = pygame.Rect(tx, ty, tw, th)
        t_surf = pygame.Surface((tw, th), pygame.SRCALPHA)
        t_surf.fill((16, 20, 32, 240))
        target_surf.blit(t_surf, (tx, ty))
        pygame.draw.rect(target_surf, (75, 95, 135), bg_rect, 1, border_radius=4)

        cur_y = ty + 6
        for text, col, font in lines:
            rendered = font.render(text, True, col)
            target_surf.blit(rendered, (tx + 10, cur_y))
            cur_y += rendered.get_height() + 2

    def render_tooltip(self, target_surf, item, mx, my, player=None, character_panel=None):
        """Renders rich item tooltip for chest slots with side-by-side comparison if character panel is open."""
        if isinstance(item, (int, float)) and not isinstance(my, (int, float)):
            item, mx, my = my, item, mx
        if not item:
            return []

        # Check side-by-side comparison
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
            lines1 = self._build_chest_tooltip_lines(item, player=player, is_equipped=False)
            lines2 = self._build_chest_tooltip_lines(equipped_item, player=player, is_equipped=True)
            tw1, th1 = self._measure_chest_tooltip(lines1)
            tw2, th2 = self._measure_chest_tooltip(lines2)

            gap = 12
            total_w = tw1 + gap + tw2
            total_h = max(th1, th2)

            if mx + 16 + total_w <= SCREEN_WIDTH - 10:
                tx1 = mx + 16
            elif mx - 16 - total_w >= 10:
                tx1 = mx - 16 - total_w
            else:
                tx1 = max(10, min(SCREEN_WIDTH - total_w - 10, mx + 16))
            tx2 = tx1 + tw1 + gap

            ty = my + 14
            if ty + total_h > SCREEN_HEIGHT - 10:
                ty = max(10, my - total_h - 8)
            if ty < 10:
                ty = 10

            self._draw_chest_card(target_surf, tx1, ty, tw1, th1, lines1)
            self._draw_chest_card(target_surf, tx2, ty, tw2, th2, lines2)
            return lines1 + lines2
        else:
            lines = self._build_chest_tooltip_lines(item, player=player, is_equipped=False)
            tw, th = self._measure_chest_tooltip(lines)
            tx = min(SCREEN_WIDTH - tw - 10, max(10, mx + 14))
            ty = my + 14
            if ty + th > SCREEN_HEIGHT - 10:
                ty = max(10, my - th - 8)
            if ty < 10:
                ty = 10

            self._draw_chest_card(target_surf, tx, ty, tw, th, lines)
            return lines
