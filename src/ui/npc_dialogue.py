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
    RARITY_COLORS, RARITY_COMMON
)
from src.ui.inventory import ItemStack, ITEM_REGISTRY


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

        # Fonts
        pygame.font.init()
        self.font_title = pygame.font.SysFont("Arial", 16, bold=True)
        self.font_role = pygame.font.SysFont("Arial", 12, bold=True)
        self.font_body = pygame.font.SysFont("Georgia", 13)
        self.font_btn = pygame.font.SysFont("Arial", 12, bold=True)
        self.font_sm = pygame.font.SysFont("Arial", 11)

    def open(self, npc, player, world=None, combat=None):
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
            self.dialogue_text = npc.get_quote()
        elif npc.npc_type == "nurse":
            cost = npc.calculate_heal_cost(player)
            if cost > 0:
                self.dialogue_text = f"Oh dear, look at those cuts and bruises! I can patch you right up to full health for {cost} Copper Coins."
            else:
                self.dialogue_text = "Your vitality is blooming, hero! Take care out there in the underground caverns."
        elif npc.npc_type == "blacksmith":
            self.dialogue_text = "The forge burns hot today! Bring me a weapon to hone its cutting edge, or browse my smelted metal ingots."
        else:
            self.dialogue_text = f"Greetings, traveler! I'm glad to call this shelter my home."

        self.sound_manager.play("craft")

    def close(self):
        if self.active_npc:
            self.active_npc.is_talking = False
        self.active_npc = None
        self.is_open = False

    def update(self, dt):
        if not self.is_open:
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
                b1 = pygame.Rect(self.x + 20, start_y, btn_w, btn_h)
                b2 = pygame.Rect(self.x + 20 + btn_w + gap, start_y, btn_w + 30, btn_h)
                b_close = pygame.Rect(self.x + self.width - 90, start_y, 70, btn_h)

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
                elif b_close.collidepoint(mouse_x, mouse_y):
                    self.close()
                    return True

        # View: Shop Mode (Merchant or Blacksmith)
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

                    if inventory.count_item(currency) >= price:
                        if inventory.can_add_item(entry["item_id"], count_to_give):
                            inventory.remove_item(currency, price)
                            inventory.add_item(entry["item_id"], count_to_give)
                            self.sound_manager.play("craft")
                            self.status_message = f"Purchased {count_to_give}x {entry['name']}!"
                        else:
                            self.status_message = "Inventory is full!"
                    else:
                        self.status_message = f"Not enough {currency.replace('_', ' ').title()}s!"
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
        panel_surf = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        panel_surf.fill((22, 26, 38, 245))
        target_surf.blit(panel_surf, (self.x, self.y))
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
            pygame.draw.rect(target_surf, (15, 18, 28, 200), box_rect, border_radius=6)
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
                draw_btn(pygame.Rect(self.x + 20, start_y, btn_w, btn_h), "Smithy Shop", is_accent=True)
                draw_btn(pygame.Rect(self.x + 20 + btn_w + gap, start_y, btn_w + 30, btn_h), "Hone Weapon (35c)")
                draw_btn(pygame.Rect(self.x + self.width - 90, start_y, 70, btn_h), "Close")

        # Mode: Shop View
        elif self.current_view == "shop":
            # Catalog Items Grid
            catalog = getattr(npc, "shop_catalog", [])
            for idx, entry in enumerate(catalog):
                col = idx % 2
                row = idx // 2
                bx = self.x + 20 + col * 250
                by = self.y + 60 + row * 44

                slot_rect = pygame.Rect(bx, by, 240, 38)
                is_slot_hover = slot_rect.collidepoint(mouse_x, mouse_y)
                pygame.draw.rect(target_surf, (28, 34, 48) if is_slot_hover else (18, 22, 32), slot_rect, border_radius=4)
                pygame.draw.rect(target_surf, (65, 80, 115), slot_rect, 1, border_radius=4)

                # Item Icon
                icon = self.asset_factory.items.get(entry["item_id"])
                if icon:
                    target_surf.blit(icon, (bx + 6, by + 7))

                # Item Name & Count
                cnt_str = f"{entry.get('count', 1)}x " if entry.get('count', 1) > 1 else ""
                i_title = f"{cnt_str}{entry['name']}"
                i_surf = self.font_sm.render(i_title, True, (240, 240, 245))
                target_surf.blit(i_surf, (bx + 36, by + 5))

                # Price Tag
                price_str = f"{entry['price']} Copper"
                p_surf = self.font_sm.render(price_str, True, (255, 215, 100))
                target_surf.blit(p_surf, (bx + 36, by + 20))

                # Buy Button
                buy_rect = pygame.Rect(bx + 175, by + 6, 58, 26)
                is_buy_hover = buy_rect.collidepoint(mouse_x, mouse_y)
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
