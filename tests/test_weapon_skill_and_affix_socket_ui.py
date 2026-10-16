"""
Unit and integration tests for:
1. Weapon skill / innate perk ordering before affix sockets in tooltips.
2. Clean single affix status with ARPG circular indicators:
   - Epic: 1 circle
   - Legendary: 1 circle
   - Mythic: 2 circles
   - Ancient: 2 circles
   - Common/Uncommon/Rare: 0 circles
3. Socket state transitions:
   - (○) Uncarved: Affix Slot (Available to Carve at Mystic Trader)
   - (○) Carved Empty: Empty Affix Slot (Available Slot - Open for Affix Stones)
   - (●) Filled: Affix name and bonus stats
4. Removal of the 3 redundant status lines across Inventory, HUD, ChestUI, and CharacterPanel.
"""

import os
import sys
import unittest
import pygame

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.constants import SCREEN_WIDTH, SCREEN_HEIGHT
from src.rpg.equipment import SLOT_WEAPON
from src.assets.asset_factory import AssetFactory
from src.audio.sound_effects import SoundManager
from src.entities.player import Player
from src.ui.inventory import Inventory, ItemStack
from src.ui.hud import HUD
from src.ui.chest_ui import ChestStorageWindow
from src.ui.character_panel import CharacterPanel
from src.ui.npc_dialogue import NPCDialogueWindow
from src.rpg.equipment_update import build_affix_socket_lines


class TestWeaponSkillAndAffixSocketUI(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pygame.init()
        if pygame.display.get_surface() is None:
            pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.NOFRAME)

    def setUp(self):
        self.af = AssetFactory()
        self.sm = SoundManager()
        self.player = Player(100, 100, self.af, self.sm)
        self.inv = Inventory(self.af)
        self.inv.player = self.player
        self.hud = HUD(self.af)
        self.chest_ui = ChestStorageWindow(self.af, self.sm)
        self.char_panel = CharacterPanel(self.af)
        self.surf = pygame.Surface((800, 600))

    def _create_spud_claymore(self):
        """Creates the Epic Claymore with Glacial Chill featured in the user report."""
        item = ItemStack("sirocco_claymore_of_the_spud", 1)
        item.affix_slots = 0
        item.additional_affix_slots = 0
        item.affixes = []
        return item

    def test_01_weapon_skill_is_before_affix_in_hud(self):
        """Verifies weapon skill (Glacial Chill) appears before affix sockets in HUD tooltip."""
        item = self._create_spud_claymore()
        lines = self.hud._render_tooltip(self.surf, 100, 100, item, player=self.player)
        texts = [t[0] for t in lines]

        # Find index containing Glacial Chill
        skill_indices = [i for i, t in enumerate(texts) if "Glacial Chill" in t]
        self.assertTrue(len(skill_indices) > 0, "Glacial Chill skill must be present in HUD tooltip")
        skill_idx = skill_indices[0]

        # Find index containing Affix Slot
        affix_indices = [i for i, t in enumerate(texts) if "Affix Slot" in t or "○" in t]
        self.assertTrue(len(affix_indices) > 0, "Affix socket indicator must be present in HUD tooltip")
        affix_idx = affix_indices[0]

        self.assertLess(
            skill_idx, affix_idx,
            f"Weapon skill at line {skill_idx} must precede affix slot at line {affix_idx} in HUD"
        )

    def test_02_weapon_skill_is_before_affix_in_inventory(self):
        """Verifies weapon skill (Glacial Chill) appears before affix sockets in Inventory tooltip."""
        item = self._create_spud_claymore()
        lines = self.inv.render_tooltip(self.surf, item, 100, 100, player=self.player)
        texts = [t[0] for t in lines]

        skill_indices = [i for i, t in enumerate(texts) if "Glacial Chill" in t]
        self.assertTrue(len(skill_indices) > 0, "Glacial Chill skill must be present in Inventory tooltip")
        skill_idx = skill_indices[0]

        affix_indices = [i for i, t in enumerate(texts) if "Affix Slot" in t or "○" in t]
        self.assertTrue(len(affix_indices) > 0, "Affix socket indicator must be present in Inventory tooltip")
        affix_idx = affix_indices[0]

        self.assertLess(
            skill_idx, affix_idx,
            f"Weapon skill at line {skill_idx} must precede affix slot at line {affix_idx} in Inventory"
        )

    def test_03_weapon_skill_is_before_affix_in_chest_ui(self):
        """Verifies weapon skill appears before affix sockets in Chest UI tooltip."""
        item = self._create_spud_claymore()
        lines = self.chest_ui.render_tooltip(self.surf, item, 100, 100, player=self.player)
        texts = [t[0] for t in lines]

        skill_indices = [i for i, t in enumerate(texts) if "Glacial Chill" in t]
        self.assertTrue(len(skill_indices) > 0, "Glacial Chill must be present in Chest UI tooltip")
        skill_idx = skill_indices[0]

        affix_indices = [i for i, t in enumerate(texts) if "Affix Slot" in t or "○" in t]
        self.assertTrue(len(affix_indices) > 0, "Affix socket indicator must be present in Chest UI tooltip")
        affix_idx = affix_indices[0]

        self.assertLess(skill_idx, affix_idx, "Weapon skill must precede affix slot in Chest UI")

    def test_04_weapon_skill_is_before_affix_in_character_panel(self):
        """Verifies weapon skill appears before affix sockets in Character Panel equipment tooltip."""
        item = self._create_spud_claymore()
        self.player.equipment.slots[SLOT_WEAPON] = item
        lines = self.char_panel._render_equipped_tooltip(
            self.surf, 100, 100, item, player=self.player
        )
        texts = [t[0] for t in lines]

        skill_indices = [i for i, t in enumerate(texts) if "Glacial Chill" in t]
        self.assertTrue(len(skill_indices) > 0, "Weapon skill must be present in Character Panel tooltip")
        skill_idx = skill_indices[0]

        affix_indices = [i for i, t in enumerate(texts) if "Affix Slot" in t or "○" in t]
        self.assertTrue(len(affix_indices) > 0, "Affix socket indicator must be present in Character Panel")
        affix_idx = affix_indices[0]

        self.assertLess(skill_idx, affix_idx, "Weapon skill must precede affix slot in Character Panel")

    def test_05_redundant_affix_lines_are_removed(self):
        """Verifies the 3 redundant, confusing text lines are removed from tooltips."""
        item = self._create_spud_claymore()
        lines = self.hud._render_tooltip(self.surf, 100, 100, item, player=self.player)
        combined_text = " ".join([t[0] for t in lines])

        self.assertNotIn("Affix Slots: 0/0", combined_text)
        self.assertNotIn("Carved Affix Slots:", combined_text)
        self.assertNotIn("[Available to Carve] 1 Slot(s) Open", combined_text)
        self.assertNotIn("[Carve Limit Reached]", combined_text)

    def test_06_circle_indicators_by_rarity(self):
        """Verifies circle indicator count corresponds strictly to rarity capacity."""
        # 1. Common / Uncommon / Rare: 0 circles
        common_item = ItemStack("wooden_sword", 1)
        c_lines = build_affix_socket_lines(common_item)
        c_circles = sum(1 for l in c_lines if "○" in l[0] or "●" in l[0])
        self.assertEqual(c_circles, 0, "Common item should have 0 affix circles")

        rare_item = ItemStack("iron_sword", 1)
        r_lines = build_affix_socket_lines(rare_item)
        r_circles = sum(1 for l in r_lines if "○" in l[0] or "●" in l[0])
        self.assertEqual(r_circles, 0, "Rare item should have 0 affix circles")

        # 2. Epic: 1 circle
        epic_item = ItemStack("magma_greatsword", 1)
        e_lines = build_affix_socket_lines(epic_item)
        e_circles = sum(1 for l in e_lines if "○" in l[0] or "●" in l[0])
        self.assertEqual(e_circles, 1, "Epic item should have exactly 1 affix circle")
        self.assertIn("○", e_lines[0][0])
        self.assertIn("Affix Slot", e_lines[0][0])

        # 3. Legendary: 1 circle
        legendary_item = ItemStack("starch_blade", 1)
        l_lines = build_affix_socket_lines(legendary_item)
        l_circles = sum(1 for l in l_lines if "○" in l[0] or "●" in l[0])
        self.assertEqual(l_circles, 1, "Legendary item should have exactly 1 affix circle")
        self.assertIn("○", l_lines[0][0])

        # 4. Mythic: 2 circles
        mythic_item = ItemStack("pride_blade", 1)
        m_lines = build_affix_socket_lines(mythic_item)
        m_circles = sum(1 for l in m_lines if "○" in l[0] or "●" in l[0])
        self.assertEqual(m_circles, 2, "Mythic item should have exactly 2 affix circles")

        # 5. Ancient: 2 circles
        ancient_item = ItemStack("katipunero_bolo", 1)
        a_lines = build_affix_socket_lines(ancient_item)
        a_circles = sum(1 for l in a_lines if "○" in l[0] or "●" in l[0])
        self.assertEqual(a_circles, 2, "Ancient item should have exactly 2 affix circles")

    def test_07_socket_state_empty_and_filled(self):
        """Verifies socket indicators update properly across uncarved, carved empty, and filled states."""
        # Start with uncarved Epic item
        item = ItemStack("magma_greatsword", 1)
        item.affix_slots = 0
        item.additional_affix_slots = 0
        item.affixes = []

        lines_uncarved = build_affix_socket_lines(item)
        uncarved_circles = sum(1 for l in lines_uncarved if "○" in l[0] or "●" in l[0])
        self.assertEqual(uncarved_circles, 1)
        text_uncarved = " ".join([l[0] for l in lines_uncarved])
        self.assertIn("○", text_uncarved)
        self.assertIn("Available to Carve at Mystic Trader", text_uncarved)

        # Carve 1 slot (empty)
        item.affix_slots = 1
        item.additional_affix_slots = 1
        lines_carved_empty = build_affix_socket_lines(item)
        empty_circles = sum(1 for l in lines_carved_empty if "○" in l[0] or "●" in l[0])
        self.assertEqual(empty_circles, 1)
        text_empty = " ".join([l[0] for l in lines_carved_empty])
        self.assertIn("○", text_empty)
        self.assertIn("Empty Affix Slot", text_empty)
        self.assertIn("Open for Affix Stones", text_empty)

        # Embed Affix Stone: "Titan's Might"
        item.affixes = ["Titan's Might"]
        lines_filled = build_affix_socket_lines(item)
        filled_circles = sum(1 for l in lines_filled if "○" in l[0] or "●" in l[0])
        self.assertEqual(filled_circles, 1)
        text_filled = " ".join([l[0] for l in lines_filled])
        self.assertIn("●", text_filled)
        self.assertIn("Titan's Might", text_filled)
        self.assertIn("+25%", text_filled)

    def test_08_mythic_partially_filled_sockets(self):
        """Verifies Mythic/Ancient weapon with 1 filled and 1 uncarved slot renders both correctly."""
        item = ItemStack("pride_blade", 1)
        item.affix_slots = 1
        item.additional_affix_slots = 1
        item.affixes = ["Titan's Might"]

        lines = build_affix_socket_lines(item)
        total_circles = sum(1 for l in lines if "○" in l[0] or "●" in l[0])
        self.assertEqual(total_circles, 2, "Mythic item must render 2 total socket circles")

        combined = " ".join([l[0] for l in lines])
        # Slot 1 is filled with Titan's Might
        self.assertIn("●", combined)
        self.assertIn("Titan's Might", combined)

        # Slot 2 is uncarved
        self.assertIn("○", combined)
        self.assertIn("Available to Carve at Mystic Trader", combined)

    def test_09_npc_dialogue_shop_tooltip_includes_affix_sockets(self):
        """Verifies NPC dialogue shop tooltips display clean socket capacity for high-tier gear."""
        npc_dlg = NPCDialogueWindow(self.af, self.sm)
        lines = npc_dlg._render_shop_item_tooltip(
            self.surf, 100, 100, {"item_id": "magma_greatsword", "price": 100, "currency": "copper_coin"}
        )
        texts = [t[0] for t in lines]

        # Has weapon skill / effects
        has_skill = any("•" in t or "Special" in t for t in texts)
        self.assertTrue(has_skill, "Shop weapon tooltip should display weapon skill")

        # Has affix circle
        has_circle = any("○" in t and "Affix Slot" in t for t in texts)
        self.assertTrue(has_circle, "Shop weapon tooltip should display affix socket capacity")


if __name__ == "__main__":
    unittest.main()
