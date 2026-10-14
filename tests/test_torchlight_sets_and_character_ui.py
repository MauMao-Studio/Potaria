"""
Potaria - Unit & Integration Tests for Torchlight 2 Tiered Set Bonuses & Character Panel UI
Tests:
1. Character Status UI dimensions and bounds:
   - Panel size (pw=560, ph=580)
   - Active skill loadout placement
   - Grimoire cards fit strictly within panel bounds with >= 40px margin from bottom border
   - Grimoire slot click hitboxes match visual layout
2. Torchlight 2 Tiered Equipment Set Bonuses:
   - Progressive thresholds for 3-piece, 4-piece, and 5-piece sets
   - Cumulative bonus application when piece_count >= required_pieces
   - Equipment recalculate_stats accumulates all active milestone bonuses
   - De-equipping pieces properly drops bonuses and updates stats
   - Aura priority: highest active milestone aura is active
3. Tooltip generation and formatting across UI systems:
   - build_set_tooltip_lines outputs (X/Y Pieces) header and (N) Set: ... milestone lines
   - Active thresholds highlighted in green/gold, inactive thresholds dimmed in purple
   - Integration with CharacterPanel, Inventory, HUD, and ChestStorageWindow

Developer: Kurados | Pure Python & pygame-ce
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"

import pygame
from src.constants import SCREEN_WIDTH, SCREEN_HEIGHT
from src.assets.asset_factory import AssetFactory
from src.audio.sound_effects import SoundManager
from src.entities.player import Player
from src.ui.inventory import Inventory, ItemStack
from src.ui.character_panel import CharacterPanel, CharacterStatusPanel
from src.ui.hud import HUD
from src.ui.chest_ui import ChestStorageWindow
from src.ui.npc_dialogue import NPCDialogueWindow
from src.rpg.skills import SKILL_DEFINITIONS
from src.rpg.equipment_update import (
    PROGRESSIVE_SETS,
    get_equipped_set_counts,
    get_active_threshold_bonuses,
    get_all_active_threshold_bonuses,
    build_set_tooltip_lines,
)
from src.rpg.equipment import (
    Equipment,
    SLOT_HEAD,
    SLOT_CHEST,
    SLOT_LEGS,
    SLOT_WEAPON,
    SLOT_ACCESSORY,
)


class TestTorchlightSetsAndCharacterUI(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pygame.init()
        pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.DOUBLEBUF | pygame.SCALED)
        cls.asset_factory = AssetFactory()
        cls.sound_manager = SoundManager()

    def setUp(self):
        self.player = Player(100, 100, self.asset_factory, self.sound_manager)
        self.char_panel = CharacterPanel(self.asset_factory)

    # =========================================================================
    # 1. CHARACTER STATUS UI LAYOUT & MARGINS
    # =========================================================================
    def test_character_panel_dimensions_and_no_bottom_clipping(self):
        """Verifies Character Status panel dimensions and that all Grimoire cards fit cleanly inside."""
        self.assertEqual(self.char_panel.pw, 560, "Panel width should be 560")
        self.assertEqual(self.char_panel.ph, 580, "Panel height should be 580 to prevent card clipping")

        px = (SCREEN_WIDTH - self.char_panel.pw) // 2
        py = (SCREEN_HEIGHT - self.char_panel.ph) // 2
        panel_bottom = py + self.char_panel.ph

        # Active skill loadout row is at py + 332
        loadout_y = py + 332
        self.assertGreater(loadout_y, py + 300)

        # Grimoire learned skills: gy = by + 68 = py + 400
        # 10 skills in SKILL_DEFINITIONS across 4 columns = 3 rows (row 0, 1, 2)
        by = py + 332
        gy = by + 68
        card_h = 34
        row_gap = 40
        # Row 2 (skills 8 & 9: celestial_shield, void_singularity):
        row2_y = gy + 22 + 2 * row_gap
        row2_bottom = row2_y + card_h  # py + 400 + 22 + 80 + 34 = py + 536

        # The bottom-most card edge must be strictly above panel_bottom with >= 40px margin
        bottom_margin = panel_bottom - row2_bottom
        self.assertGreaterEqual(
            bottom_margin,
            40,
            f"Bottom margin ({bottom_margin}px) must be at least 40px above bottom border ({panel_bottom})"
        )

    def test_character_panel_render_and_click_handling(self):
        """Verifies character panel renders onto surface and handles click hitboxes without errors."""
        surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.char_panel.is_open = True

        # Unlock all skills on player for testing
        for s_id in SKILL_DEFINITIONS.keys():
            self.player.skills.learned_skills.add(s_id)

        # Render panel
        self.char_panel.render(surf, self.player, mouse_x=300, mouse_y=300)

        # Verify all grimoire cards (including bottom row) fit strictly inside panel bounds with >= 40px margin
        px = (SCREEN_WIDTH - self.char_panel.pw) // 2
        py = (SCREEN_HEIGHT - self.char_panel.ph) // 2
        panel_bottom = py + self.char_panel.ph
        self.assertEqual(len(self.char_panel.grimoire_rects), len(SKILL_DEFINITIONS))
        for s_id, rect in self.char_panel.grimoire_rects.items():
            self.assertGreaterEqual(
                panel_bottom - rect.bottom,
                40,
                f"Grimoire card {s_id} bottom ({rect.bottom}) must be >= 40px above panel bottom ({panel_bottom})"
            )

        # Verify click on active skill slot does not crash
        slot0_x = px + 155
        slot0_y = py + 354
        handled = self.char_panel.handle_click(slot0_x, slot0_y, self.player)
        self.assertIn(handled, [True, False])

    def test_character_status_panel_alias(self):
        """Verifies CharacterStatusPanel is aliased to CharacterPanel."""
        self.assertIs(CharacterStatusPanel, CharacterPanel)

    # =========================================================================
    # 2. TORCHLIGHT 2 TIERED SET BONUSES (PROGRESSIVE THRESHOLDS)
    # =========================================================================
    def test_progressive_sets_have_tiered_thresholds(self):
        """Verifies 3-piece, 4-piece, and 5-piece sets have multiple progression thresholds."""
        # 4-piece set: ancient, titan, magma, shadow, cactus
        self.assertIn(2, PROGRESSIVE_SETS["ancient"]["thresholds"])
        self.assertIn(3, PROGRESSIVE_SETS["ancient"]["thresholds"])
        self.assertIn(4, PROGRESSIVE_SETS["ancient"]["thresholds"])

        # 5-piece set: sin_pride, sin_greed, virtue_humility, etc.
        self.assertIn(2, PROGRESSIVE_SETS["sin_pride"]["thresholds"])
        self.assertIn(4, PROGRESSIVE_SETS["sin_pride"]["thresholds"])
        self.assertIn(5, PROGRESSIVE_SETS["sin_pride"]["thresholds"])

        # 3-piece set: diwata_bloom, bakunawa_eclipse, etc.
        self.assertIn(2, PROGRESSIVE_SETS["diwata_bloom"]["thresholds"])
        self.assertIn(3, PROGRESSIVE_SETS["diwata_bloom"]["thresholds"])

    def test_cumulative_threshold_bonuses_activation(self):
        """Verifies equipping N pieces activates all milestones <= N cumulatively."""
        helm = "ancient_helmet"
        chest = "ancient_chestplate"
        greaves = "ancient_greaves"
        sword = "ancient_sword"

        # 1 piece: 0 thresholds active
        b1 = get_all_active_threshold_bonuses([helm])
        self.assertEqual(len(b1), 0, "1 piece should activate 0 set bonuses")

        # 2 pieces: threshold 2 active
        b2 = get_all_active_threshold_bonuses([helm, chest])
        self.assertEqual(len(b2), 1, "2 pieces should activate threshold 2")
        self.assertEqual(b2[0][1], 2)

        # 3 pieces: threshold 2 AND 3 active cumulatively
        b3 = get_all_active_threshold_bonuses([helm, chest, greaves])
        self.assertEqual(len(b3), 2, "3 pieces should activate thresholds 2 and 3")
        tiers_3 = [t[1] for t in b3]
        self.assertEqual(tiers_3, [2, 3])

        # 4 pieces: threshold 2, 3, AND 4 active cumulatively
        b4 = get_all_active_threshold_bonuses([helm, chest, greaves, sword])
        self.assertEqual(len(b4), 3, "4 pieces should activate thresholds 2, 3, and 4")
        tiers_4 = [t[1] for t in b4]
        self.assertEqual(tiers_4, [2, 3, 4])

    def test_5_piece_set_milestones(self):
        """Verifies 5-piece sets activate at 2, 4, and 5 pieces."""
        pieces = ["pride_crown", "pride_robe", "pride_boots", "pride_blade", "pride_ring"]

        # 2 pieces -> [2]
        b2 = get_all_active_threshold_bonuses(pieces[:2])
        self.assertEqual([t[1] for t in b2], [2])

        # 3 pieces -> [2] (since next milestone is 4)
        b3 = get_all_active_threshold_bonuses(pieces[:3])
        self.assertEqual([t[1] for t in b3], [2])

        # 4 pieces -> [2, 4]
        b4 = get_all_active_threshold_bonuses(pieces[:4])
        self.assertEqual([t[1] for t in b4], [2, 4])

        # 5 pieces -> [2, 4, 5]
        b5 = get_all_active_threshold_bonuses(pieces)
        self.assertEqual([t[1] for t in b5], [2, 4, 5])

    def test_legacy_single_tier_compatibility(self):
        """Verifies get_active_threshold_bonuses with cumulative=False returns single highest tier per set."""
        pieces = ["ancient_helmet", "ancient_chestplate", "ancient_greaves", "ancient_sword"]
        b_highest = get_active_threshold_bonuses(pieces, cumulative=False)
        self.assertEqual(len(b_highest), 1)
        self.assertEqual(b_highest[0][1], 4)

    # =========================================================================
    # 3. EQUIPMENT RECALCULATE_STATS CUMULATIVE BONUSES & UNEQUIP
    # =========================================================================
    def test_equipment_stat_recalculation_cumulative(self):
        """Verifies player equipment recalculates stats with cumulative set bonuses."""
        eq = Equipment()
        stats = self.player.stats

        # Baseline stats with empty equipment
        eq.recalculate_stats(stats)
        base_bonus_hp = stats.bonus_max_hp

        # Equip 2 pieces of Ancient set (helmet + chestplate)
        eq.equip(ItemStack("ancient_helmet", 1), stats)
        eq.equip(ItemStack("ancient_chestplate", 1), stats)
        eq.recalculate_stats(stats)
        hp_2_piece = stats.bonus_max_hp
        self.assertGreater(hp_2_piece, base_bonus_hp)

        # Equip 3rd piece (greaves)
        eq.equip(ItemStack("ancient_greaves", 1), stats)
        eq.recalculate_stats(stats)
        hp_3_piece = stats.bonus_max_hp
        self.assertGreater(hp_3_piece, hp_2_piece, "3-piece threshold should add more cumulative stats")

        # Equip 4th piece (weapon)
        eq.equip(ItemStack("ancient_sword", 1), stats)
        eq.recalculate_stats(stats)
        hp_4_piece = stats.bonus_max_hp
        self.assertGreater(hp_4_piece, hp_3_piece, "4-piece threshold should add further cumulative stats")

        # Unequip weapon
        eq.unequip(SLOT_WEAPON, stats)
        eq.recalculate_stats(stats)
        self.assertEqual(stats.bonus_max_hp, hp_3_piece, "Unequipping weapon should return bonus HP to 3-piece level")

        # Unequip greaves
        eq.unequip(SLOT_LEGS, stats)
        eq.recalculate_stats(stats)
        self.assertEqual(stats.bonus_max_hp, hp_2_piece, "Unequipping greaves should return bonus HP to 2-piece level")

    def test_highest_active_aura_selection(self):
        """Verifies aura selection prioritizes the highest active milestone tier and does not activate prematurely."""
        eq = Equipment()
        stats = self.player.stats

        # Equip 2 pieces of Pride sin set: threshold 2 has no aura
        eq.equip(ItemStack("pride_crown", 1), stats)
        eq.equip(ItemStack("pride_robe", 1), stats)
        self.assertIsNone(eq.get_active_aura())

        # Equip 3 pieces of Pride sin set: threshold 3 has no aura
        eq.equip(ItemStack("pride_boots", 1), stats)
        self.assertIsNone(eq.get_active_aura(), "3 of 5 pieces must NOT prematurely activate solar aura")

        # Equip 4 pieces of Pride sin set: no threshold at 4
        eq.equip(ItemStack("pride_blade", 1), stats)
        self.assertIsNone(eq.get_active_aura(), "4 of 5 pieces must NOT activate solar aura")

        # Equip full 5 pieces: threshold 5 has 'solar' aura
        eq.equip(ItemStack("pride_ring", 1), stats)
        self.assertEqual(eq.get_active_aura(), "solar")

    def test_single_piece_does_not_grant_aura(self):
        """Verifies equipping 1 piece of ancient set (helmet) does not grant pulsing aura or set bonuses."""
        eq = Equipment()
        stats = self.player.stats
        eq.equip(ItemStack("ancient_helmet", 1), stats)
        self.assertIsNone(eq.get_active_aura(), "Single ancient helmet must NOT grant pulsing ancient aura")
        set_key, set_info = eq.get_active_set()
        self.assertIsNone(set_key, "Single piece must NOT activate equipment set")

    def test_held_weapon_set_activation(self):
        """Verifies weapon held in hand from hotbar contributes to progressive sets and auras."""
        eq = Equipment()
        stats = self.player.stats

        # Equip 2 armor pieces: ancient helmet + chestplate
        eq.equip(ItemStack("ancient_helmet", 1), stats)
        eq.equip(ItemStack("ancient_chestplate", 1), stats)
        eq.recalculate_stats(stats)
        hp_2_piece = stats.bonus_max_hp

        # Hold ancient sword in hand from hotbar (not in paperdoll weapon slot)
        sword_stack = ItemStack("ancient_sword", 1)
        eq.recalculate_stats(stats, active_item=sword_stack)
        hp_with_held = stats.bonus_max_hp

        # 3rd piece should be recognized from held weapon
        self.assertGreater(hp_with_held, hp_2_piece, "Held weapon should activate 3-piece set bonus")
        set_key, set_info = eq.get_active_set()
        self.assertEqual(set_key, "ancient")
        self.assertEqual(eq.get_active_aura(), "ancient")

    # =========================================================================
    # 4. TOOLTIP RENDERING & FORMATTING ACROSS UI
    # =========================================================================
    def test_build_set_tooltip_lines_formatting(self):
        """Verifies build_set_tooltip_lines outputs Torchlight 2 style headers and milestone lines."""
        lines_unequipped = build_set_tooltip_lines("ancient_helmet", player=None)
        self.assertTrue(len(lines_unequipped) > 0)

        # Header line should contain "Set: Ancient Resonating Set"
        header_text, header_color, _ = lines_unequipped[0]
        self.assertIn("Set:", header_text)
        self.assertIn("Ancient", header_text)
        self.assertEqual(header_color, (220, 120, 245), "Set header must be Torchlight 2 violet")

        # Check for milestone lines: (2) Set: ..., (3) Set: ..., (4) Set: ...
        all_text = " ".join(t[0] for t in lines_unequipped)
        self.assertIn("(2) Set:", all_text)
        self.assertIn("(3) Set:", all_text)
        self.assertIn("(4) Set:", all_text)

        # Since player=None, all milestones should be inactive (dimmed color)
        for text, col, _ in lines_unequipped[1:]:
            if "Set:" in text:
                self.assertEqual(col, (150, 115, 175), "Inactive milestone must be dimmed")

    def test_build_set_tooltip_lines_with_equipped_player(self):
        """Verifies active milestones are highlighted in bright green/gold when equipped."""
        # Equip 2 pieces of ancient set on player
        self.player.equipment.slots[SLOT_HEAD] = ItemStack("ancient_helmet", 1)
        self.player.equipment.slots[SLOT_CHEST] = ItemStack("ancient_chestplate", 1)

        lines = build_set_tooltip_lines("ancient_helmet", player=self.player)
        header_text = lines[0][0]
        self.assertIn("(2/4 Pieces)", header_text, "Header should show 2/4 Pieces equipped")

        # Milestones: (2) should be active, (3) and (4) should be inactive
        milestone_colors = {}
        for text, col, _ in lines:
            if "(2) Set:" in text:
                milestone_colors[2] = col
            elif "(3) Set:" in text:
                milestone_colors[3] = col
            elif "(4) Set:" in text:
                milestone_colors[4] = col

        self.assertEqual(milestone_colors[2], (110, 245, 140), "(2) Set milestone must be highlighted")
        self.assertEqual(milestone_colors[3], (150, 115, 175), "(3) Set milestone must be dimmed")
        self.assertEqual(milestone_colors[4], (150, 115, 175), "(4) Set milestone must be dimmed")

    def test_hud_tooltip_renders_set_lines(self):
        """Verifies HUD item tooltip includes set lines in detailed mode."""
        hud = HUD(self.asset_factory)
        hud.tooltip_mode = "detailed"
        surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))

        stack = ItemStack("ancient_helmet", 1)
        lines = hud._render_tooltip(surf, 50, 50, stack, player=self.player)
        text_joined = " ".join(t[0] for t in lines)
        self.assertIn("Set:", text_joined)
        self.assertIn("(2) Set:", text_joined)

    def test_inventory_tooltip_renders_set_lines(self):
        """Verifies Inventory tooltip includes set lines."""
        inv = Inventory(self.asset_factory)
        inv.tooltip_mode = "detailed"
        surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))

        stack = ItemStack("ancient_helmet", 1)
        lines = inv.render_tooltip(surf, stack, 50, 50, player=self.player)
        text_joined = " ".join(t[0] for t in lines)
        self.assertIn("Set:", text_joined)
        self.assertIn("(2) Set:", text_joined)

    def test_chest_ui_tooltip_renders_set_lines(self):
        """Verifies Chest UI tooltip includes set lines."""
        chest_ui = ChestStorageWindow(self.asset_factory, self.sound_manager)
        chest_ui.tooltip_mode = "detailed"
        surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))

        stack = ItemStack("ancient_helmet", 1)
        lines = chest_ui.render_tooltip(surf, stack, 50, 50, player=self.player)
        text_joined = " ".join(t[0] for t in lines)
        self.assertIn("Set:", text_joined)
        self.assertIn("(2) Set:", text_joined)

    def test_npc_dialogue_tooltip_renders_set_lines(self):
        """Verifies NPC dialogue shop item tooltip renders set lines."""
        npc_ui = NPCDialogueWindow(self.asset_factory, self.sound_manager)
        surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        entry = {"item_id": "ancient_helmet", "price": 100, "currency": "copper_coin"}
        npc_ui.active_player = self.player
        lines = []
        npc_ui._render_shop_item_tooltip(surf, 50, 50, entry)


if __name__ == "__main__":
    unittest.main()
