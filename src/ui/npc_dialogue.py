"""
Potaria - NPC Dialogue & Shop Interface
Provides interactive dialogue boxes, merchant shop inventories, nurse healing clinics,
and blacksmith weapon tempering for Town NPCs.
Developer: Kurados
"""

import math
import pygame
from src.constants import (
    SCREEN_WIDTH, SCREEN_HEIGHT, COLOR_GOLD,
    RARITY_COLORS, RARITY_COMMON, RARITY_EPIC, RARITY_MYTHIC, RARITY_LEGENDARY, RARITY_ANCIENT,
    CAT_WEAPON, CAT_TOOL
)
from src.ui.inventory import ItemStack, ITEM_REGISTRY
from src.rpg.equipment import ARMOR_DATA


class NPCDialogueWindow:
    def __init__(self, asset_factory, sound_manager):
        self.asset_factory = asset_factory
        self.sound_manager = sound_manager

        self.width = 540
        self.height = 320
        self.x = (SCREEN_WIDTH - self.width) // 2
        self.y = (SCREEN_HEIGHT - self.height) // 2

        self.is_open = False
        self.active_npc = None
        self.current_view = "dialogue"  # "dialogue", "shop", "service"
        self.dialogue_text = ""
        self.status_message = ""
        self.typewriter_chars = 0
        self.typewriter_timer = 0.0

        # Fonts (Centralized Typography Theme)
        from src.ui.theme import font_bold, font_semibold, font_regular, font_compact
        self.font_title = font_bold(16)
        self.font_role = font_semibold(12)
        self.font_body = font_regular(14)
        self.font_btn = font_semibold(12)
        self.font_sm = font_compact(11)
        self.font_bold = font_semibold(11)
        self.font_lore = font_regular(11)

    def open(self, npc, player, world=None, combat=None):
        if combat and hasattr(npc, "check_hostile_enemies"):
            npc.check_hostile_enemies(combat)
        if getattr(npc, "shield_active", False) or getattr(npc, "is_despawned", False):
            return

        self.is_open = True
        self.active_npc = npc
        self.active_npc.is_talking = True
        self.current_view = "dialogue"
        self.status_message = ""
        self.typewriter_chars = 0
        self.typewriter_timer = 0.0

        # Set default greeting
        if npc.npc_type == "guide":
            self.dialogue_text = npc.get_advice(player, world, combat)
        elif npc.npc_type == "merchant":
            self.dialogue_text = npc.get_quote() if hasattr(npc, "get_quote") else "Welcome to my traveling emporium! Browse my wares or trade your hard-earned copper coins."
        elif npc.npc_type == "nurse":
            cost = npc.calculate_heal_cost(player)
            if cost > 0:
                self.dialogue_text = f"Oh dear, look at those cuts and bruises! I can patch you right up to full health for {cost} Copper Coins."
            else:
                self.dialogue_text = "Your vitality is blooming, hero! Take care out there in the underground caverns."
        elif npc.npc_type == "blacksmith":
            self.dialogue_text = "The forge burns hot today! Bring me a weapon to hone its cutting edge, or browse my smelted metal ingots."
        elif npc.npc_type in ("mystic_trader", "trader_wares", "trader_enhance", "trader_affix"):
            self.dialogue_text = npc.get_quote() if hasattr(npc, "get_quote") else "The cosmic currents brought me here for a fleeting moment. Browse my rare armaments, repair your shattered blades, or carve an Affix Slot!"
        else:
            self.dialogue_text = f"Greetings, traveler! I'm glad to call this shelter my home."

        self.sound_manager.play("craft")

    def close(self):
        if self.active_npc:
            self.active_npc.is_talking = False
        self.active_npc = None
        self.is_open = False

    def update(self, dt, player=None):
        if not self.is_open:
            return
        if self.active_npc:
            if getattr(self.active_npc, "shield_active", False) or getattr(self.active_npc, "is_despawned", False):
                self.close()
                return
            if player:
                npc_cx = getattr(self.active_npc, "center_x", self.active_npc.x + self.active_npc.width / 2)
                npc_cy = getattr(self.active_npc, "center_y", self.active_npc.y + self.active_npc.height / 2)
                dist = math.hypot(player.center_x - npc_cx, player.center_y - npc_cy)
                if dist > 96.0: # Automatically close dialogue if player walks or dashes away
                    self.close()
                    return
        if self.typewriter_chars < len(self.dialogue_text):
            self.typewriter_timer += dt
            char_interval = 0.018
            while self.typewriter_timer >= char_interval and self.typewriter_chars < len(self.dialogue_text):
                self.typewriter_timer -= char_interval
                self.typewriter_chars += 1
                # Play character vocal phoneme blip every 2 characters typed
                if self.typewriter_chars % 2 == 0 and self.sound_manager:
                    char_c = self.dialogue_text[self.typewriter_chars - 1]
                    if char_c.isalnum():
                        npc_speaker = getattr(self.active_npc, "npc_type", None) or getattr(self.active_npc, "name", "guide")
                        if hasattr(self.sound_manager, "play_voice"):
                            self.sound_manager.play_voice(npc_speaker, volume=0.28)
                        else:
                            self.sound_manager.play("typewriter", volume=0.3)

    def _wrap_text(self, text, max_width, font):
        words = text.split(" ")
        lines = []
        cur_line = []
        for word in words:
            test_line = " ".join(cur_line + [word])
            if font.size(test_line)[0] <= max_width:
                cur_line.append(word)
            else:
                if cur_line:
                    lines.append(" ".join(cur_line))
                cur_line = [word]
        if cur_line:
            lines.append(" ".join(cur_line))
        return lines

    def handle_click(self, mouse_x, mouse_y, player, inventory, world=None, combat=None):
        if not self.is_open or not self.active_npc:
            return False

        if combat and hasattr(self.active_npc, "check_hostile_enemies"):
            self.active_npc.check_hostile_enemies(combat)

        if getattr(self.active_npc, "shield_active", False) or getattr(self.active_npc, "is_despawned", False):
            self.close()
            return True

        panel_rect = pygame.Rect(self.x, self.y, self.width, self.height)
        if not panel_rect.collidepoint(mouse_x, mouse_y):
            # Click outside closes window
            self.close()
            return True

        npc = self.active_npc

        # 1. Close Button [X]
        close_btn = pygame.Rect(self.x + self.width - 28, self.y + 8, 20, 20)
        if close_btn.collidepoint(mouse_x, mouse_y):
            self.close()
            return True

        # View: Dialogue Mode
        if self.current_view == "dialogue":
            # Fast-forward text if clicked on panel body while still typing
            if self.typewriter_chars < len(self.dialogue_text):
                bottom_buttons_y = self.y + self.height - 50
                if mouse_y < bottom_buttons_y:
                    self.typewriter_chars = len(self.dialogue_text)
                    return True

            # Action Buttons along bottom
            btn_w, btn_h = 130, 28
            gap = 12
            start_y = self.y + self.height - 44

            if npc.npc_type == "guide":
                b1 = pygame.Rect(self.x + 20, start_y, btn_w, btn_h)
                b2 = pygame.Rect(self.x + 20 + btn_w + gap, start_y, btn_w + 30, btn_h)
                b_close = pygame.Rect(self.x + self.width - 90, start_y, 70, btn_h)

                if b1.collidepoint(mouse_x, mouse_y):
                    self.dialogue_text = npc.get_advice(player, world, combat)
                    self.typewriter_chars = 0
                    self.sound_manager.play("dialogue_chime")
                    return True
                elif b2.collidepoint(mouse_x, mouse_y):
                    self.dialogue_text = "Subterranean Altars allow calling forth the Nether Titans: Lord Malus (underground), Ignis Colossus (desert altar), Cryo-Spud (glacial altar), and Necro-Tuber (shadow altar). Defeating them rewards celestial shards!"
                    self.typewriter_chars = 0
                    self.sound_manager.play("dialogue_chime")
                    return True
                elif b_close.collidepoint(mouse_x, mouse_y):
                    self.close()
                    return True

            elif npc.npc_type == "merchant":
                b1 = pygame.Rect(self.x + 20, start_y, btn_w, btn_h)
                b2 = pygame.Rect(self.x + 20 + btn_w + gap, start_y, btn_w, btn_h)
                b_close = pygame.Rect(self.x + self.width - 90, start_y, 70, btn_h)

                if b1.collidepoint(mouse_x, mouse_y):
                    self.current_view = "shop"
                    self.sound_manager.play("dialogue_chime")
                    return True
                elif b2.collidepoint(mouse_x, mouse_y):
                    self.dialogue_text = npc.get_quote()
                    self.typewriter_chars = 0
                    self.sound_manager.play("dialogue_chime")
                    return True
                elif b_close.collidepoint(mouse_x, mouse_y):
                    self.close()
                    return True

            elif npc.npc_type == "nurse":
                b1 = pygame.Rect(self.x + 20, start_y, btn_w + 40, btn_h)
                b2 = pygame.Rect(self.x + 20 + btn_w + 50, start_y, btn_w, btn_h)
                b_close = pygame.Rect(self.x + self.width - 90, start_y, 70, btn_h)

                if b1.collidepoint(mouse_x, mouse_y):
                    success, msg = npc.heal_player(player, inventory)
                    self.status_message = msg
                    self.dialogue_text = msg
                    self.typewriter_chars = 0
                    return True
                elif b2.collidepoint(mouse_x, mouse_y):
                    self.dialogue_text = "Always pack healing potions when diving into the caverns! Rest in a bed to naturally recover over time."
                    self.typewriter_chars = 0
                    self.sound_manager.play("dialogue_chime")
                    return True
                elif b_close.collidepoint(mouse_x, mouse_y):
                    self.close()
                    return True

            elif npc.npc_type == "blacksmith":
                b1 = pygame.Rect(self.x + 20, start_y, 95, btn_h)
                b2 = pygame.Rect(self.x + 120, start_y, 85, btn_h)
                b3 = pygame.Rect(self.x + 210, start_y, 115, btn_h)
                b_close = pygame.Rect(self.x + self.width - 80, start_y, 65, btn_h)

                if b1.collidepoint(mouse_x, mouse_y):
                    self.current_view = "shop"
                    self.sound_manager.play("dialogue_chime")
                    return True
                elif b2.collidepoint(mouse_x, mouse_y):
                    success, msg = npc.hone_weapon(player, inventory)
                    self.status_message = msg
                    self.dialogue_text = msg
                    self.typewriter_chars = 0
                    return True
                elif b3.collidepoint(mouse_x, mouse_y):
                    active = inventory.get_active_item()
                    from src.rpg.enhancement import enhance_item
                    status, msg = enhance_item(active, inventory, self.sound_manager)
                    self.status_message = msg
                    self.dialogue_text = msg
                    self.typewriter_chars = 0
                    return True
                elif b_close.collidepoint(mouse_x, mouse_y):
                    self.close()
                    return True

            elif npc.npc_type in ("mystic_trader", "trader_wares"):
                has_affix_service = any(e.get("is_affix_service") for e in getattr(npc, "shop_catalog", []))
                b1 = pygame.Rect(self.x + 20, start_y, 110, btn_h)
                b2 = pygame.Rect(self.x + 135, start_y, 115, btn_h)
                b3 = pygame.Rect(self.x + 255, start_y, 125, btn_h) if has_affix_service else None
                b_close = pygame.Rect(self.x + self.width - 80, start_y, 65, btn_h)

                if b1.collidepoint(mouse_x, mouse_y):
                    self.current_view = "shop"
                    self.sound_manager.play("dialogue_chime")
                    return True
                elif b2.collidepoint(mouse_x, mouse_y):
                    active = inventory.get_active_item()
                    target_item = None
                    if active and getattr(active, "is_broken", False):
                        target_item = active
                    else:
                        for s in inventory.slots:
                            if s and getattr(s, "is_broken", False):
                                target_item = s
                                break
                    if not target_item:
                        self.status_message = "No broken items in your hands or backpack!"
                        self.dialogue_text = "All of your equipment is intact and ready for battle!"
                        self.typewriter_chars = 0
                    else:
                        from src.rpg.enhancement import repair_item
                        ok, msg = repair_item(target_item, inventory, self.sound_manager)
                        self.status_message = msg
                        self.dialogue_text = msg
                        self.typewriter_chars = 0
                    return True
                elif b3 and b3.collidepoint(mouse_x, mouse_y):
                    active = inventory.get_active_item()
                    from src.rpg.enhancement import can_add_affix_slot, add_affix_slot_to_item
                    can_add, reason = can_add_affix_slot(active)
                    if not can_add:
                        self.status_message = reason
                        self.dialogue_text = f"I cannot carve this: {reason}"
                        self.typewriter_chars = 0
                    else:
                        ok, msg = add_affix_slot_to_item(active, inventory, cost_copper=5000, sound_manager=self.sound_manager)
                        self.status_message = msg
                        self.dialogue_text = msg
                        self.typewriter_chars = 0
                    return True
                elif b_close.collidepoint(mouse_x, mouse_y):
                    self.close()
                    return True

            elif npc.npc_type == "trader_enhance":
                b1 = pygame.Rect(self.x + 20, start_y, 110, btn_h)
                b2 = pygame.Rect(self.x + 135, start_y, 125, btn_h)
                b3 = pygame.Rect(self.x + 265, start_y, 115, btn_h)
                b_close = pygame.Rect(self.x + self.width - 80, start_y, 65, btn_h)

                if b1.collidepoint(mouse_x, mouse_y):
                    self.current_view = "shop"
                    self.sound_manager.play("dialogue_chime")
                    return True
                elif b2.collidepoint(mouse_x, mouse_y):
                    active = inventory.get_active_item()
                    from src.rpg.enhancement import enhance_item
                    status, msg = enhance_item(active, inventory, self.sound_manager)
                    self.status_message = msg
                    self.dialogue_text = msg
                    self.typewriter_chars = 0
                    return True
                elif b3.collidepoint(mouse_x, mouse_y):
                    active = inventory.get_active_item()
                    target_item = None
                    if active and getattr(active, "is_broken", False):
                        target_item = active
                    else:
                        for s in inventory.slots:
                            if s and getattr(s, "is_broken", False):
                                target_item = s
                                break
                    if not target_item:
                        self.status_message = "No broken items in your hands or backpack!"
                        self.dialogue_text = "All of your equipment is intact and ready for battle!"
                        self.typewriter_chars = 0
                    else:
                        from src.rpg.enhancement import repair_item
                        ok, msg = repair_item(target_item, inventory, self.sound_manager)
                        self.status_message = msg
                        self.dialogue_text = msg
                        self.typewriter_chars = 0
                    return True
                elif b_close.collidepoint(mouse_x, mouse_y):
                    self.close()
                    return True

            elif npc.npc_type == "trader_affix":
                b1 = pygame.Rect(self.x + 20, start_y, 110, btn_h)
                b2 = pygame.Rect(self.x + 135, start_y, 125, btn_h)
                b3 = pygame.Rect(self.x + 265, start_y, 115, btn_h)
                b_close = pygame.Rect(self.x + self.width - 80, start_y, 65, btn_h)

                if b1.collidepoint(mouse_x, mouse_y):
                    self.current_view = "shop"
                    self.sound_manager.play("dialogue_chime")
                    return True
                elif b2.collidepoint(mouse_x, mouse_y):
                    active = inventory.get_active_item()
                    from src.rpg.enhancement import can_add_affix_slot, add_affix_slot_to_item
                    can_add, reason = can_add_affix_slot(active)
                    if not can_add:
                        self.status_message = reason
                        self.dialogue_text = f"I cannot carve this: {reason}"
                        self.typewriter_chars = 0
                    else:
                        ok, msg = add_affix_slot_to_item(active, inventory, cost_copper=5000, sound_manager=self.sound_manager)
                        self.status_message = msg
                        self.dialogue_text = msg
                        self.typewriter_chars = 0
                    return True
                elif b3.collidepoint(mouse_x, mouse_y):
                    active = inventory.get_active_item()
                    target_item = None
                    if active and getattr(active, "is_broken", False):
                        target_item = active
                    else:
                        for s in inventory.slots:
                            if s and getattr(s, "is_broken", False):
                                target_item = s
                                break
                    if not target_item:
                        self.status_message = "No broken items in your hands or backpack!"
                        self.dialogue_text = "All of your equipment is intact and ready for battle!"
                        self.typewriter_chars = 0
                    else:
                        from src.rpg.enhancement import repair_item
                        ok, msg = repair_item(target_item, inventory, self.sound_manager)
                        self.status_message = msg
                        self.dialogue_text = msg
                        self.typewriter_chars = 0
                    return True
                elif b_close.collidepoint(mouse_x, mouse_y):
                    self.close()
                    return True

        # View: Shop Mode (Merchant or Blacksmith or Mystic Trader)
        elif self.current_view == "shop":
            back_btn = pygame.Rect(self.x + 20, self.y + self.height - 40, 80, 26)
            if back_btn.collidepoint(mouse_x, mouse_y):
                self.current_view = "dialogue"
                self.sound_manager.play("dialogue_chime")
                return True

            sell_btn = pygame.Rect(self.x + 115, self.y + self.height - 40, 160, 26)
            if sell_btn.collidepoint(mouse_x, mouse_y):
                # Sell active held item from hotbar
                active = inventory.get_active_item()
                if active and active.item_id not in ("copper_coin", "silver_coin", "gold_coin"):
                    # Calculate sell value
                    item_unit_val = max(1, active.data.get("damage", active.data.get("def", 2)) * 2)
                    base_val = item_unit_val * active.count
                    cnt = active.count
                    item_name = active.data.get('name', 'item')
                    inventory.slots[inventory.selected_slot] = None
                    inventory.add_item("copper_coin", base_val)
                    self.sound_manager.play("pickup")
                    if cnt > 1:
                        self.status_message = f"Sold {cnt}x {item_name} for {base_val} Copper Coins!"
                    else:
                        self.status_message = f"Sold {item_name} for {base_val} Copper Coins!"
                else:
                    self.status_message = "Hold an item in your hotbar to sell it!"
                return True

            # Check shop purchase buttons
            catalog = getattr(npc, "shop_catalog", [])
            for idx, entry in enumerate(catalog):
                col = idx % 2
                row = idx // 2
                bx = self.x + 20 + col * 250
                by = self.y + 70 + row * 46
                buy_rect = pygame.Rect(bx + 180, by + 4, 55, 24)

                if buy_rect.collidepoint(mouse_x, mouse_y):
                    price = entry["price"]
                    currency = entry.get("currency", "copper_coin")
                    count_to_give = entry.get("count", 1)

                    if entry.get("is_affix_service"):
                        active = inventory.get_active_item()
                        from src.rpg.enhancement import can_add_affix_slot, add_affix_slot_to_item
                        can_add, reason = can_add_affix_slot(active)
                        if not can_add:
                            self.status_message = f"Hold Legendary/Ancient item: {reason}"
                        elif inventory.count_item(currency) < price:
                            curr_label = "Gold" if currency == "gold_coin" else ("Silver" if currency == "silver_coin" else "Copper")
                            self.status_message = f"Requires {price} {curr_label} Coins!"
                        else:
                            inventory.remove_item(currency, price)
                            ok, msg = add_affix_slot_to_item(active, inventory=None, cost_copper=0, sound_manager=self.sound_manager)
                            self.status_message = msg
                        return True

                    if inventory.count_item(currency) >= price:
                        if inventory.can_add_item(entry["item_id"], count_to_give):
                            inventory.remove_item(currency, price)
                            inventory.add_item(entry["item_id"], count_to_give)
                            self.sound_manager.play("craft")
                            self.status_message = f"Purchased {count_to_give}x {entry['name']}!"
                        else:
                            self.status_message = "Inventory is full!"
                    else:
                        curr_label = "Gold" if currency == "gold_coin" else ("Silver" if currency == "silver_coin" else "Copper")
                        self.status_message = f"Not enough {curr_label} Coins!"
                    return True

        return True

    def render(self, target_surf, player, inventory, mouse_x, mouse_y):
        if not self.is_open or not self.active_npc:
            return

        npc = self.active_npc

        # Panel Background & Shadow
        shadow_rect = pygame.Rect(self.x + 4, self.y + 4, self.width, self.height)
        pygame.draw.rect(target_surf, (10, 12, 18, 160), shadow_rect, border_radius=8)

        panel_rect = pygame.Rect(self.x, self.y, self.width, self.height)
        # Solid opaque panel plate - prevents world background from bleeding through
        pygame.draw.rect(target_surf, (22, 26, 38), panel_rect, border_radius=8)
        pygame.draw.rect(target_surf, (80, 100, 140), panel_rect, 2, border_radius=8)
        pygame.draw.rect(target_surf, COLOR_GOLD, panel_rect, 1, border_radius=8)

        # Close [X] Button
        close_rect = pygame.Rect(self.x + self.width - 28, self.y + 8, 20, 20)
        is_close_hover = close_rect.collidepoint(mouse_x, mouse_y)
        pygame.draw.rect(target_surf, (160, 45, 45) if is_close_hover else (80, 30, 30), close_rect, border_radius=4)
        x_surf = self.font_btn.render("X", True, (255, 255, 255))
        target_surf.blit(x_surf, (close_rect.centerx - x_surf.get_width() // 2, close_rect.centery - x_surf.get_height() // 2))

        # Coin Purser Bar on top right
        copper_cnt = getattr(inventory, "copper_coins", 0)
        silver_cnt = getattr(inventory, "silver_coins", 0)
        gold_cnt = getattr(inventory, "gold_coins", 0)
        coin_str = f"Coins: {gold_cnt}g  {silver_cnt}s  {copper_cnt}c"
        coin_surf = self.font_sm.render(coin_str, True, (255, 220, 110))
        target_surf.blit(coin_surf, (self.x + self.width - coin_surf.get_width() - 36, self.y + 11))

        # NPC Portrait (64x64)
        if npc.portrait:
            target_surf.blit(npc.portrait, (self.x + 18, self.y + 16))
        else:
            pygame.draw.rect(target_surf, (50, 40, 30), (self.x + 18, self.y + 16, 64, 64), border_radius=6)

        # NPC Title & Role
        name_surf = self.font_title.render(npc.name, True, (255, 255, 255))
        target_surf.blit(name_surf, (self.x + 94, self.y + 16))

        role_badge = f"[{npc.role_title}]"
        role_surf = self.font_role.render(role_badge, True, npc.role_color)
        target_surf.blit(role_surf, (self.x + 94 + name_surf.get_width() + 10, self.y + 19))

        # Mode: Dialogue View
        if self.current_view == "dialogue":
            # Dialogue Speech Box
            box_rect = pygame.Rect(self.x + 94, self.y + 44, self.width - 114, 185)
            pygame.draw.rect(target_surf, (15, 18, 28), box_rect, border_radius=6)
            pygame.draw.rect(target_surf, (60, 75, 105), box_rect, 1, border_radius=6)

            # Render visible typewriter text
            visible_text = self.dialogue_text[:self.typewriter_chars]
            lines = self._wrap_text(visible_text, box_rect.width - 24, self.font_body)
            cur_y = box_rect.y + 12
            for line in lines:
                l_surf = self.font_body.render(line, True, (240, 242, 250))
                target_surf.blit(l_surf, (box_rect.x + 12, cur_y))
                cur_y += l_surf.get_height() + 4

            if self.status_message:
                stat_surf = self.font_sm.render(self.status_message, True, (255, 230, 90))
                target_surf.blit(stat_surf, (box_rect.x + 12, box_rect.bottom - 22))

            # Action Buttons
            btn_w, btn_h = 130, 28
            gap = 12
            start_y = self.y + self.height - 44

            def draw_btn(rect, text, is_accent=False):
                hover = rect.collidepoint(mouse_x, mouse_y)
                bg = (80, 105, 150) if hover else ((60, 75, 110) if not is_accent else (120, 85, 30))
                border = (255, 235, 120) if hover else (100, 125, 175)
                pygame.draw.rect(target_surf, bg, rect, border_radius=4)
                pygame.draw.rect(target_surf, border, rect, 1, border_radius=4)
                txt = self.font_btn.render(text, True, (255, 255, 255) if not hover else (255, 235, 120))
                target_surf.blit(txt, (rect.centerx - txt.get_width() // 2, rect.centery - txt.get_height() // 2))

            if npc.npc_type == "guide":
                draw_btn(pygame.Rect(self.x + 20, start_y, btn_w, btn_h), "Helpful Advice")
                draw_btn(pygame.Rect(self.x + 20 + btn_w + gap, start_y, btn_w + 30, btn_h), "Titans & Altars")
                draw_btn(pygame.Rect(self.x + self.width - 90, start_y, 70, btn_h), "Close")
            elif npc.npc_type == "merchant":
                draw_btn(pygame.Rect(self.x + 20, start_y, btn_w, btn_h), "Browse Wares", is_accent=True)
                draw_btn(pygame.Rect(self.x + 20 + btn_w + gap, start_y, btn_w, btn_h), "Chat")
                draw_btn(pygame.Rect(self.x + self.width - 90, start_y, 70, btn_h), "Close")
            elif npc.npc_type == "nurse":
                cost = npc.calculate_heal_cost(player)
                heal_label = f"Heal Wounds ({cost}c)" if cost > 0 else "Heal (Peak HP)"
                draw_btn(pygame.Rect(self.x + 20, start_y, btn_w + 40, btn_h), heal_label, is_accent=True)
                draw_btn(pygame.Rect(self.x + 20 + btn_w + 50, start_y, btn_w, btn_h), "Health Tips")
                draw_btn(pygame.Rect(self.x + self.width - 90, start_y, 70, btn_h), "Close")
            elif npc.npc_type == "blacksmith":
                draw_btn(pygame.Rect(self.x + 20, start_y, 95, btn_h), "Smithy Shop", is_accent=True)
                draw_btn(pygame.Rect(self.x + 120, start_y, 85, btn_h), "Hone (35c)")
                draw_btn(pygame.Rect(self.x + 210, start_y, 115, btn_h), "Enhance (+1..7)")
                draw_btn(pygame.Rect(self.x + self.width - 80, start_y, 65, btn_h), "Close")
            elif npc.npc_type in ("mystic_trader", "trader_wares"):
                has_affix_service = any(e.get("is_affix_service") for e in getattr(npc, "shop_catalog", []))
                draw_btn(pygame.Rect(self.x + 20, start_y, 110, btn_h), "Browse Wares", is_accent=True)
                draw_btn(pygame.Rect(self.x + 135, start_y, 115, btn_h), "Repair (1 Gold)")
                if has_affix_service:
                    draw_btn(pygame.Rect(self.x + 255, start_y, 125, btn_h), "Carve Affix Slot")
                draw_btn(pygame.Rect(self.x + self.width - 80, start_y, 65, btn_h), "Close")
            elif npc.npc_type == "trader_enhance":
                draw_btn(pygame.Rect(self.x + 20, start_y, 110, btn_h), "Browse Wares", is_accent=True)
                draw_btn(pygame.Rect(self.x + 135, start_y, 125, btn_h), "Enhance (+1..7)")
                draw_btn(pygame.Rect(self.x + 265, start_y, 115, btn_h), "Repair (1 Gold)")
                draw_btn(pygame.Rect(self.x + self.width - 80, start_y, 65, btn_h), "Close")
            elif npc.npc_type == "trader_affix":
                draw_btn(pygame.Rect(self.x + 20, start_y, 110, btn_h), "Browse Wares", is_accent=True)
                draw_btn(pygame.Rect(self.x + 135, start_y, 125, btn_h), "Carve Affix Slot")
                draw_btn(pygame.Rect(self.x + 265, start_y, 115, btn_h), "Repair (1 Gold)")
                draw_btn(pygame.Rect(self.x + self.width - 80, start_y, 65, btn_h), "Close")

        # Mode: Shop View
        elif self.current_view == "shop":
            hovered_entry = None

            # Catalog Items Grid
            catalog = getattr(npc, "shop_catalog", [])
            for idx, entry in enumerate(catalog):
                col = idx % 2
                row = idx // 2
                bx = self.x + 20 + col * 250
                by = self.y + 70 + row * 46

                slot_rect = pygame.Rect(bx, by, 240, 38)
                buy_rect = pygame.Rect(bx + 180, by + 4, 55, 24)
                is_slot_hover = slot_rect.collidepoint(mouse_x, mouse_y)
                is_buy_hover = buy_rect.collidepoint(mouse_x, mouse_y)

                if is_slot_hover and not is_buy_hover:
                    hovered_entry = entry

                pygame.draw.rect(target_surf, (28, 34, 48) if is_slot_hover else (18, 22, 32), slot_rect, border_radius=4)
                pygame.draw.rect(target_surf, (65, 80, 115), slot_rect, 1, border_radius=4)

                # Item Icon
                icon = self.asset_factory.items.get(entry["item_id"]) if hasattr(self.asset_factory, "items") else None
                if not icon and entry.get("is_affix_service") and hasattr(self.asset_factory, "items"):
                    icon = self.asset_factory.items.get("affix_stone") or self.asset_factory.items.get("portal_shard")
                if icon:
                    target_surf.blit(icon, (bx + 6, by + 7))

                # Item Name & Count
                cnt_str = f"{entry.get('count', 1)}x " if entry.get('count', 1) > 1 else ""
                i_title = f"{cnt_str}{entry['name']}"
                i_surf = self.font_sm.render(i_title, True, (240, 240, 245))
                target_surf.blit(i_surf, (bx + 36, by + 5))

                # Price Tag
                currency = entry.get("currency", "copper_coin")
                curr_name = "Copper"
                if currency == "gold_coin":
                    curr_name = "Gold"
                elif currency == "silver_coin":
                    curr_name = "Silver"
                price_str = f"{entry['price']} {curr_name}"
                p_surf = self.font_sm.render(price_str, True, (255, 215, 100))
                target_surf.blit(p_surf, (bx + 36, by + 20))

                # Buy Button
                pygame.draw.rect(target_surf, (60, 120, 60) if is_buy_hover else (35, 75, 35), buy_rect, border_radius=4)
                pygame.draw.rect(target_surf, (120, 220, 120) if is_buy_hover else (60, 140, 60), buy_rect, 1, border_radius=4)
                buy_txt = self.font_btn.render("BUY", True, (255, 255, 255))
                target_surf.blit(buy_txt, (buy_rect.centerx - buy_txt.get_width() // 2, buy_rect.centery - buy_txt.get_height() // 2))

            # Bottom Bar: Back & Sell Held Item
            back_rect = pygame.Rect(self.x + 20, self.y + self.height - 40, 80, 26)
            is_back_hover = back_rect.collidepoint(mouse_x, mouse_y)
            pygame.draw.rect(target_surf, (70, 80, 105) if is_back_hover else (45, 55, 75), back_rect, border_radius=4)
            pygame.draw.rect(target_surf, (120, 140, 180), back_rect, 1, border_radius=4)
            b_txt = self.font_btn.render("Back", True, (255, 255, 255))
            target_surf.blit(b_txt, (back_rect.centerx - b_txt.get_width() // 2, back_rect.centery - b_txt.get_height() // 2))

            sell_rect = pygame.Rect(self.x + 115, self.y + self.height - 40, 160, 26)
            is_sell_hover = sell_rect.collidepoint(mouse_x, mouse_y)
            pygame.draw.rect(target_surf, (140, 90, 30) if is_sell_hover else (90, 60, 20), sell_rect, border_radius=4)
            pygame.draw.rect(target_surf, COLOR_GOLD, sell_rect, 1, border_radius=4)
            s_txt = self.font_btn.render("Sell Held Item", True, (255, 235, 120))
            target_surf.blit(s_txt, (sell_rect.centerx - s_txt.get_width() // 2, sell_rect.centery - s_txt.get_height() // 2))

            if self.status_message:
                stat_surf = self.font_sm.render(self.status_message, True, (255, 230, 90))
                target_surf.blit(stat_surf, (self.x + 290, self.y + self.height - 35))

            # Render Rich Tooltip on top when hovering over any shop card
            if hovered_entry:
                self._render_shop_item_tooltip(target_surf, mouse_x, mouse_y, hovered_entry)

    def _render_shop_item_tooltip(self, target_surf, mx, my, entry):
        """Displays rich Diablo/Torchlight-style item tooltip for shop wares."""
        iid = entry.get("item_id", "")
        currency = entry.get("currency", "copper_coin")
        curr_name = "Gold" if currency == "gold_coin" else ("Silver" if currency == "silver_coin" else "Copper")
        price = entry.get("price", 0)

        # Affix Voucher special case
        if entry.get("is_affix_service"):
            lines = [
                ("Affix Slot Carving Voucher", (220, 160, 255), self.font_bold),
                ("[EQUIPMENT ENCHANTMENT SERVICE]", (220, 160, 255), self.font_sm),
                ("Service: Carves an open Affix Slot into gear", (180, 240, 255), self.font_sm),
                ("Requirements: Hold an Epic, Legendary, Mythic, or Ancient item in your hands.", (255, 215, 100), self.font_sm),
                ("• Limits: Epic (1), Legendary (1), Mythic (2), Ancient (2).", (140, 230, 255), self.font_sm),
                ("• Sacrifices one basic attribute for an open imbuable Affix Slot.", (140, 230, 255), self.font_sm),
                ("• Allows embedding Affix Stones crafted at the Work Bench.", (140, 230, 255), self.font_sm),
                (f"Cost: {price} {curr_name} Coins", (255, 220, 90), self.font_bold),
                ("'The stars whisper of hidden potentials waiting to be unlocked.'", (240, 205, 120), self.font_lore)
            ]
            r_color = (220, 160, 255)
        else:
            reg = ITEM_REGISTRY.get(iid, {})
            armor = ARMOR_DATA.get(iid, {})
            rarity = entry.get("rarity") or reg.get("rarity") or armor.get("rarity") or RARITY_COMMON
            r_color = RARITY_COLORS.get(rarity, (220, 220, 220))
            name = entry.get("name") or reg.get("name") or armor.get("name") or iid.replace("_", " ").title()
            cat = reg.get("cat") or armor.get("slot") or "item"
            cat_str = str(cat).replace("_", " ").upper()

            lines = []
            lines.append((name, r_color, self.font_bold))
            lines.append((f"[{rarity.upper()} {cat_str}]", r_color, self.font_sm))

            # Combat / Armor stats
            dmg_val = reg.get("damage", 0)
            if reg.get("cat") == CAT_WEAPON or (dmg_val > 0 and reg.get("cat") != CAT_TOOL):
                lines.append((f"Weapon Power: {dmg_val} Damage", (255, 215, 100), self.font_sm))
                if any(w in iid.lower() for w in ("dagger", "shortsword", "knife")):
                    speed_str = "Very Fast Speed (0.22s)"
                elif any(w in iid.lower() for w in ("greatsword", "cleaver", "hammer", "scythe")):
                    speed_str = "Slow, Heavy Speed (0.46s)"
                elif "bow" in iid.lower():
                    speed_str = "Average Speed (0.36s)"
                elif any(w in iid.lower() for w in ("staff", "wand", "scepter", "rod", "catalyst")):
                    speed_str = "Average Speed (0.34s)"
                else:
                    speed_str = "Fast Speed (0.30s)"
                lines.append((f"Use Speed: {speed_str}", (240, 230, 160), self.font_sm))
            elif reg.get("cat") == CAT_TOOL:
                lines.append((f"Tool Damage: {dmg_val}", (190, 205, 225), self.font_sm))

            def_val = armor.get("def") or reg.get("def", 0)
            if def_val > 0:
                lines.append((f"+{def_val} Defense", (140, 230, 140), self.font_sm))
            if armor.get("hp", 0) > 0:
                lines.append((f"+{armor['hp']} Max HP", (255, 120, 120), self.font_sm))
            if armor.get("atk", 0) > 0:
                lines.append((f"+{armor['atk']} Attack", (255, 215, 100), self.font_sm))
            if armor.get("crit", 0) > 0 or reg.get("crit", 0) > 0:
                lines.append((f"+{armor.get('crit', reg.get('crit', 0))}% Crit Chance", (255, 175, 80), self.font_sm))
            if armor.get("speed", 0) > 0 or reg.get("speed", 0) > 0:
                sp = armor.get("speed", reg.get("speed", 0))
                lines.append((f"+{sp} Movement Speed", (200, 210, 255), self.font_sm))

            # Effects for high tier
            from src.ui.theme import wrap_text_lines
            effects = reg.get("effects") or armor.get("effects", [])
            rarity_str = str(rarity).lower()
            if rarity_str in (RARITY_EPIC, RARITY_MYTHIC, RARITY_LEGENDARY, RARITY_ANCIENT, "epic", "mythic", "legendary", "ancient") and "wood" not in iid.lower():
                if effects:
                    for eff in effects:
                        for el in wrap_text_lines(f"• {eff}", self.font_sm, 300):
                            lines.append((el, (100, 240, 240), self.font_sm))
                elif reg.get("special") or armor.get("special"):
                    for sl in wrap_text_lines(f"Special: {reg.get('special') or armor.get('special')}", self.font_sm, 300):
                        lines.append((sl, (100, 240, 240), self.font_sm))

            desc = reg.get("desc") or armor.get("desc")
            if not desc or str(desc).strip() == "":
                desc = f"A fine {rarity.title()} item radiating elemental potency."
            for dl in wrap_text_lines(desc, self.font_sm, 300):
                lines.append((dl, (215, 225, 240), self.font_sm))

            if rarity_str in (RARITY_LEGENDARY, RARITY_MYTHIC, RARITY_ANCIENT, "legendary", "mythic", "ancient"):
                lore = reg.get("lore") or armor.get("lore")
                if lore:
                    for ll in wrap_text_lines(lore, self.font_lore, 300):
                        lines.append((ll, (240, 205, 120), self.font_lore))

            lines.append((f"Price: {price} {curr_name} Coins", (255, 215, 100), self.font_bold))

        # Render tooltip box
        rendered_surfs = [fnt.render(txt, True, col) for txt, col, fnt in lines]
        content_w = max(s.get_width() for s in rendered_surfs)
        tw = max(160, min(330, content_w + 20))
        th = sum(s.get_height() + 3 for s in rendered_surfs) + 12

        tx = max(10, min(SCREEN_WIDTH - tw - 12, mx + 16))
        ty = my + 16
        if ty + th > SCREEN_HEIGHT - 10:
            ty = max(10, my - th - 8)
        if ty < 10:
            ty = 10

        rect = pygame.Rect(tx, ty, tw, th)
        pygame.draw.rect(target_surf, (20, 24, 38, 245), rect, border_radius=6)
        pygame.draw.rect(target_surf, r_color, rect, 1, border_radius=6)

        cur_y = ty + 6
        for s in rendered_surfs:
            target_surf.blit(s, (tx + 10, cur_y))
            cur_y += s.get_height() + 3
