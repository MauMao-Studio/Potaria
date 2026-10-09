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

        pygame.font.init()
        self.font_title = pygame.font.SysFont("Arial", 14, bold=True)
        self.font_btn = pygame.font.SysFont("Arial", 11, bold=True)
        self.font_count = pygame.font.SysFont("Arial", 10, bold=True)
        self.font_sm = pygame.font.SysFont("Arial", 10)

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
                                inventory.held_item = ItemStack(current.item_id, half)
                                current.count -= half
                            else:
                                inventory.held_item = current
                                chest.slots[slot_idx] = None
                            if self.sound_manager:
                                self.sound_manager.play("pickup")
                    else:
                        if current is None:
                            if is_right_click and held.count > 1:
                                chest.slots[slot_idx] = ItemStack(held.item_id, 1)
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

    def render(self, target_surf, inventory, mouse_x, mouse_y):
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
        if hovered_item and hasattr(inventory, "render_tooltip"):
            inventory.render_tooltip(target_surf, hovered_item, mouse_x, mouse_y)
