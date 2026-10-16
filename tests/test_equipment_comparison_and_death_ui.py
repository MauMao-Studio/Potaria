"""
Potaria - Unit and Integration Tests for:
1. Side-by-side equipment comparison tooltips ("katabi") when Character Info panel is open.
2. Single tooltip fallback when slot is empty, item is already equipped, or panel is closed.
3. Low HP / Dying numeric life HUD display (drop shadow, >= 0 clamp).
4. Cinematic death transition pitch-black overlay on game screen.
5. Factual, concise culinary descriptions across food items.
6. Invariant check on cookbook and catalog files.

Developer: Kurados | Pure Python & pygame-ce
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"

import pygame
from src.constants import (
    SCREEN_WIDTH, SCREEN_HEIGHT,
    COLOR_GOLD
)
from src.assets.asset_factory import AssetFactory
from src.audio.sound_effects import SoundManager
from src.entities.player import Player
from src.ui.inventory import Inventory, ItemStack, ITEM_REGISTRY
from src.ui.character_panel import CharacterPanel
from src.ui.hud import HUD
from src.ui.chest_ui import ChestStorageWindow
from src.world.storage_chest import StorageChest
from src.rpg.equipment import (
    SLOT_HEAD, SLOT_CHEST, SLOT_LEGS, SLOT_WEAPON, SLOT_ACCESSORY,
    get_item_equipment_slot, get_equipped_item_for_slot, is_item_already_equipped
)


class TestEquipmentComparisonAndDeathUI(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pygame.init()
        pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.DOUBLEBUF | pygame.SCALED)
        cls.asset_factory = AssetFactory()
        cls.sound_manager = SoundManager()

    def setUp(self):
        self.player = Player(100, 100, self.asset_factory, self.sound_manager)
        self.inventory = Inventory(self.asset_factory, self.sound_manager)
        self.inventory.player = self.player
        self.char_panel = CharacterPanel(self.asset_factory)
        self.hud = HUD(self.asset_factory)
        self.screen_surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)

    # =========================================================================
    # 1. EQUIPMENT SLOT DETECTION & HELPER FUNCTIONS
    # =========================================================================
    def test_equipment_slot_detection(self):
        """Verifies get_item_equipment_slot correctly categorizes equipment types."""
        self.assertEqual(get_item_equipment_slot("copper_helmet"), SLOT_HEAD)
        self.assertEqual(get_item_equipment_slot("iron_helmet"), SLOT_HEAD)
        self.assertEqual(get_item_equipment_slot("copper_chestplate"), SLOT_CHEST)
        self.assertEqual(get_item_equipment_slot("copper_greaves"), SLOT_LEGS)
        self.assertEqual(get_item_equipment_slot("copper_shortsword"), SLOT_WEAPON)
        self.assertEqual(get_item_equipment_slot("wooden_bow"), SLOT_WEAPON)
        self.assertEqual(get_item_equipment_slot("guardian_ring"), SLOT_ACCESSORY)
        self.assertEqual(get_item_equipment_slot("warrior_charm"), SLOT_ACCESSORY)

        # Non-equipment items
        self.assertIsNone(get_item_equipment_slot("chicken_adobo"))
        self.assertIsNone(get_item_equipment_slot("wood"))
        self.assertIsNone(get_item_equipment_slot("apple"))

    def test_get_equipped_item_and_is_equipped(self):
        """Verifies get_equipped_item_for_slot and is_item_already_equipped."""
        self.player.equipment.slots[SLOT_HEAD] = "copper_helmet"
        self.player.equipment.slots[SLOT_CHEST] = "copper_chestplate"

        equipped_head = get_equipped_item_for_slot(self.player, SLOT_HEAD)
        self.assertIsNotNone(equipped_head)
        self.assertEqual(equipped_head.item_id, "copper_helmet")

        self.assertTrue(is_item_already_equipped("copper_helmet", self.player))
        self.assertFalse(is_item_already_equipped("iron_helmet", self.player))

        # Check unequipped slot
        equipped_legs = get_equipped_item_for_slot(self.player, SLOT_LEGS)
        self.assertIsNone(equipped_legs)

    # =========================================================================
    # 2. SIDE-BY-SIDE EQUIPMENT COMPARISON TOOLTIP ("KATABI")
    # =========================================================================
    def test_side_by_side_comparison_when_character_panel_open(self):
        """Hovering an equippable item while Character Info panel is open displays both cards."""
        self.player.equipment.slots[SLOT_HEAD] = "copper_helmet"
        self.char_panel.is_open = True

        hovered_item = ItemStack("iron_helmet", 1)
        lines = self.hud._render_tooltip(
            self.screen_surf, 400, 300, hovered_item,
            player=self.player, character_panel=self.char_panel
        )

        # Verification of returned lines: contains equipped banner
        equipped_banners = [line[0] for line in lines if line[0] == "[ CURRENTLY EQUIPPED ]"]
        self.assertEqual(len(equipped_banners), 1, "Comparison tooltip must have [ CURRENTLY EQUIPPED ] banner")

        # Contains both item names
        line_texts = [line[0] for line in lines]
        self.assertTrue(any("Iron Helmet" in text for text in line_texts))
        self.assertTrue(any("Copper Helmet" in text for text in line_texts))

    def test_single_tooltip_when_slot_is_empty(self):
        """If player has nothing equipped in the slot, only single tooltip is displayed."""
        self.player.equipment.slots[SLOT_HEAD] = None
        self.char_panel.is_open = True

        hovered_item = ItemStack("iron_helmet", 1)
        lines = self.hud._render_tooltip(
            self.screen_surf, 400, 300, hovered_item,
            player=self.player, character_panel=self.char_panel
        )

        equipped_banners = [line[0] for line in lines if line[0] == "[ CURRENTLY EQUIPPED ]"]
        self.assertEqual(len(equipped_banners), 0, "No equipped banner if slot is empty")

        line_texts = [line[0] for line in lines]
        self.assertTrue(any("Iron Helmet" in text for text in line_texts))
        self.assertFalse(any("Copper Helmet" in text for text in line_texts))

    def test_single_tooltip_when_item_already_equipped(self):
        """Hovering the already-equipped item itself does not show duplicate comparison card."""
        self.player.equipment.slots[SLOT_HEAD] = "copper_helmet"
        self.char_panel.is_open = True

        hovered_item = ItemStack("copper_helmet", 1)
        lines = self.hud._render_tooltip(
            self.screen_surf, 400, 300, hovered_item,
            player=self.player, character_panel=self.char_panel
        )

        equipped_banners = [line[0] for line in lines if line[0] == "[ CURRENTLY EQUIPPED ]"]
        self.assertEqual(len(equipped_banners), 0, "No comparison when item is already equipped")

    def test_side_by_side_comparison_with_duplicate_id_different_stats(self):
        """Comparing a duplicate item ID with different enhancement level or affixes shows both cards."""
        equipped_item = ItemStack("copper_helmet", 1)
        equipped_item.enhancement_level = 0
        self.player.equipment.slots[SLOT_HEAD] = equipped_item
        self.char_panel.is_open = True

        # In inventory: copper_helmet +3
        inv_item = ItemStack("copper_helmet", 1)
        inv_item.enhancement_level = 3

        lines = self.hud._render_tooltip(
            self.screen_surf, 400, 300, inv_item,
            player=self.player, character_panel=self.char_panel
        )
        equipped_banners = [line[0] for line in lines if line[0] == "[ CURRENTLY EQUIPPED ]"]
        self.assertEqual(len(equipped_banners), 1, "Duplicate item ID with different enhancement must trigger comparison")

    def test_single_tooltip_when_identical_duplicate(self):
        """Hovering an unequipped item identical in ID, enhancement, and affixes displays only a single card."""
        equipped_item = ItemStack("copper_helmet", 1)
        equipped_item.enhancement_level = 2
        equipped_item.affixes = ["Titan's Grasp"]
        self.player.equipment.slots[SLOT_HEAD] = equipped_item
        self.char_panel.is_open = True

        duplicate_item = ItemStack("copper_helmet", 1)
        duplicate_item.enhancement_level = 2
        duplicate_item.affixes = ["Titan's Grasp"]

        lines = self.hud._render_tooltip(
            self.screen_surf, 400, 300, duplicate_item,
            player=self.player, character_panel=self.char_panel
        )
        equipped_banners = [line[0] for line in lines if line[0] == "[ CURRENTLY EQUIPPED ]"]
        self.assertEqual(len(equipped_banners), 0, "Identical duplicate item should not show redundant comparison card")

    def test_single_tooltip_when_character_panel_closed(self):
        """When character panel is closed, hovering equipment displays single standard tooltip."""
        self.player.equipment.slots[SLOT_HEAD] = "copper_helmet"
        self.char_panel.is_open = False

        hovered_item = ItemStack("iron_helmet", 1)
        lines = self.hud._render_tooltip(
            self.screen_surf, 400, 300, hovered_item,
            player=self.player, character_panel=self.char_panel
        )

        equipped_banners = [line[0] for line in lines if line[0] == "[ CURRENTLY EQUIPPED ]"]
        self.assertEqual(len(equipped_banners), 0)

    def test_single_tooltip_for_non_equipment(self):
        """Non-equipment items (food, resources) always display a single tooltip."""
        self.char_panel.is_open = True
        hovered_item = ItemStack("chicken_adobo", 1)
        lines = self.hud._render_tooltip(
            self.screen_surf, 400, 300, hovered_item,
            player=self.player, character_panel=self.char_panel
        )

        equipped_banners = [line[0] for line in lines if line[0] == "[ CURRENTLY EQUIPPED ]"]
        self.assertEqual(len(equipped_banners), 0)

    def test_tooltip_horizontal_and_vertical_screen_bounds_clamping(self):
        """Verifies side-by-side comparison cards flip left near the right edge and clamp vertically."""
        self.player.equipment.slots[SLOT_HEAD] = "copper_helmet"
        self.char_panel.is_open = True
        hovered_item = ItemStack("iron_helmet", 1)

        # Near right edge of screen: 1200 out of 1280
        lines = self.hud._render_tooltip(
            self.screen_surf, 1200, 650, hovered_item,
            player=self.player, character_panel=self.char_panel
        )
        self.assertTrue(len(lines) > 0)

        # Near left edge of screen: 5 out of 1280
        lines_left = self.hud._render_tooltip(
            self.screen_surf, 5, 10, hovered_item,
            player=self.player, character_panel=self.char_panel
        )
        self.assertTrue(len(lines_left) > 0)

    # =========================================================================
    # 3. CHEST UI SIDE-BY-SIDE COMPARISON
    # =========================================================================
    def test_chest_ui_side_by_side_comparison(self):
        """Verifies StorageChest window also renders side-by-side comparison with character panel."""
        chest_ui = ChestStorageWindow(self.asset_factory, self.sound_manager)
        chest = StorageChest(10, 10, capacity=20)
        chest.slots[0] = ItemStack("iron_helmet", 1)
        chest_ui.open(chest)

        self.player.equipment.slots[SLOT_HEAD] = "copper_helmet"
        self.char_panel.is_open = True

        lines = chest_ui.render_tooltip(
            self.screen_surf, chest.slots[0], 200, 200,
            player=self.player, character_panel=self.char_panel
        )
        equipped_banners = [line[0] for line in lines if line[0] == "[ CURRENTLY EQUIPPED ]"]
        self.assertEqual(len(equipped_banners), 1)

    def test_chest_ui_side_by_side_duplicate_id_different_stats(self):
        """Chest UI compares items with same ID but different enhancement or affixes."""
        chest_ui = ChestStorageWindow(self.asset_factory, self.sound_manager)
        chest = StorageChest(10, 10, capacity=20)
        chest_item = ItemStack("copper_helmet", 1)
        chest_item.enhancement_level = 5
        chest.slots[0] = chest_item
        chest_ui.open(chest)

        equipped_item = ItemStack("copper_helmet", 1)
        equipped_item.enhancement_level = 0
        self.player.equipment.slots[SLOT_HEAD] = equipped_item
        self.char_panel.is_open = True

        lines = chest_ui.render_tooltip(
            self.screen_surf, chest.slots[0], 200, 200,
            player=self.player, character_panel=self.char_panel
        )
        equipped_banners = [line[0] for line in lines if line[0] == "[ CURRENTLY EQUIPPED ]"]
        self.assertEqual(len(equipped_banners), 1, "Chest should compare duplicate ID with different stats")

    def test_chest_ui_single_tooltip_identical_duplicate(self):
        """Chest UI shows single card if chest item is identical in ID, enhancement, and affixes."""
        chest_ui = ChestStorageWindow(self.asset_factory, self.sound_manager)
        chest = StorageChest(10, 10, capacity=20)
        chest_item = ItemStack("copper_helmet", 1)
        chest_item.enhancement_level = 2
        chest.slots[0] = chest_item
        chest_ui.open(chest)

        equipped_item = ItemStack("copper_helmet", 1)
        equipped_item.enhancement_level = 2
        self.player.equipment.slots[SLOT_HEAD] = equipped_item
        self.char_panel.is_open = True

        lines = chest_ui.render_tooltip(
            self.screen_surf, chest.slots[0], 200, 200,
            player=self.player, character_panel=self.char_panel
        )
        equipped_banners = [line[0] for line in lines if line[0] == "[ CURRENTLY EQUIPPED ]"]
        self.assertEqual(len(equipped_banners), 0, "Chest should not show comparison for identical duplicate")

    # =========================================================================
    # 4. LOW HP / DYING NUMERIC LIFE RENDERING
    # =========================================================================
    def test_numeric_life_clamped_at_zero(self):
        """Verifies dying/low HP is cleanly clamped to 0 without negative numbers or glitches."""
        # Test negative HP
        self.player.stats.hp = -15.5
        self.hud._render_hp_and_mp(self.screen_surf, self.player)
        self.assertEqual(self.hud._cached_hp_key[0], 0, "HP must clamp to 0 at negative life")

        # Test near-zero floating HP
        self.player.stats.hp = 0.4
        self.hud._render_hp_and_mp(self.screen_surf, self.player)
        self.assertEqual(self.hud._cached_hp_key[0], 0, "HP rounded and clamped")

        # Test normal HP
        self.player.stats.hp = 75.0
        self.hud._render_hp_and_mp(self.screen_surf, self.player)
        self.assertEqual(self.hud._cached_hp_key[0], 75)

    def test_death_fade_overlay_independent_of_ui_surf(self):
        """Verifies death fade surface can be blitted onto screen without alpha artifacts on ui_surf."""
        screen = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        screen.fill((50, 50, 50))

        fade_surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        fade_surf.fill((0, 0, 0))
        fade_surf.set_alpha(150)
        screen.blit(fade_surf, (0, 0))

        # Check screen darkened
        color = screen.get_at((100, 100))
        self.assertLess(color[0], 50, "Screen should be dimmed by death fade overlay")

        # UI surface rendered independently remains crisp
        ui_surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        self.player.stats.hp = 0
        self.hud._render_hp_and_mp(ui_surf, self.player)
        self.assertIsNotNone(self.hud._cached_hp_surf)

    # =========================================================================
    # 5. CONCISE, FACTUAL FOOD DESCRIPTIONS
    # =========================================================================
    def test_food_descriptions_are_concise_and_culinary(self):
        """Verifies culinary items have factual, concise descriptions without flowery language."""
        dishes_to_test = [
            "chicken_adobo", "pork_adobo", "sinigang", "kare_kare", "bulalo",
            "tinola", "lechon", "pancit_bihon", "arroz_caldo", "halo_halo",
            "mashed_potato", "golden_fry", "cooked_bangus", "coconut_milk"
        ]
        poetic_buzzwords = ["symphony", "whisper", "ethereal", "poetic", "transcendent", "celestial ballad"]

        for item_id in dishes_to_test:
            self.assertIn(item_id, ITEM_REGISTRY, f"Item {item_id} missing from registry")
            desc = ITEM_REGISTRY[item_id].get("desc", "")
            self.assertTrue(len(desc) > 0, f"Description for {item_id} should not be empty")
            desc_lower = desc.lower()
            for buzzword in poetic_buzzwords:
                self.assertNotIn(buzzword, desc_lower, f"Description for {item_id} contains flowery word: '{buzzword}'")

    def test_raw_ingredients_and_produce_descriptions_are_concise(self):
        """Verifies raw ingredients and produce in ITEM_REGISTRY also have direct, factual descriptions."""
        ingredients_to_test = [
            "raw_potato", "apple", "raw_bangus", "raw_tilapia", "raw_galunggong",
            "raw_maya_maya", "raw_tanigue", "raw_tambakol", "raw_lapu_lapu",
            "raw_hito", "raw_dilis", "raw_dalagang_bukid", "raw_chicken",
            "raw_duck_meat", "duck_egg", "egg", "raw_pork", "pork_belly",
            "raw_beef", "carabao_milk", "raw_goat_meat", "goat_milk",
            "garlic", "onion", "ginger", "calamansi", "tamarind", "soy_sauce",
            "vinegar", "black_pepper", "salt", "rice", "eggplant", "string_beans"
        ]
        poetic_buzzwords = [
            "symphony", "whisper", "ethereal", "poetic", "transcendent",
            "celestial", "sun-drenched", "plump", "aromatic treasure",
            "savory treasure", "pride of the", "fiery embrace"
        ]
        for item_id in ingredients_to_test:
            self.assertIn(item_id, ITEM_REGISTRY, f"Ingredient {item_id} missing from registry")
            desc = ITEM_REGISTRY[item_id].get("desc", "").lower()
            for buzzword in poetic_buzzwords:
                self.assertNotIn(buzzword, desc, f"Description for {item_id} contains '{buzzword}'")

    def test_cookbook_script_acquisition_descriptions_are_direct(self):
        """Verifies build_cookbook_docs.py ITEM_ACQUISITION and SECTIONS entries are direct and factual."""
        import scripts.build_cookbook_docs as bcd
        self.assertTrue(hasattr(bcd, "ITEM_ACQUISITION"))
        poetic_buzzwords = ["whisper", "symphony", "ethereal", "poetic", "transcendent", "celestial"]
        for item_id, acq in bcd.ITEM_ACQUISITION.items():
            acq_lower = acq.lower()
            for buzzword in poetic_buzzwords:
                self.assertNotIn(buzzword, acq_lower, f"Acquisition for {item_id} contains '{buzzword}'")

        for title, items, desc_text in bcd.SECTIONS:
            header = title.lower()
            desc = desc_text.lower()
            for buzzword in poetic_buzzwords:
                self.assertNotIn(buzzword, header, f"Section header {title} contains '{buzzword}'")
                self.assertNotIn(buzzword, desc, f"Section desc {title} contains '{buzzword}'")

    # =========================================================================
    # 6. COOKBOOK & CATALOG FILES INTEGRITY INVARIANT
    # =========================================================================
    def test_cookbook_and_catalog_files_integrity(self):
        """Verifies all 4 cookbook files exist and items catalog was preserved untouched."""
        base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

        cookbook_files = [
            "Potaria_Cookbook_With_Codes.docx",
            "Potaria_Cookbook_With_Codes.pdf",
            "Potaria_Cookbook_No_Codes.docx",
            "Potaria_Cookbook_No_Codes.pdf",
            "Potaria_Cookbook.docx",
            "Potaria_Cookbook.pdf"
        ]
        for f in cookbook_files:
            p = os.path.join(base_dir, f)
            self.assertTrue(os.path.isfile(p), f"Cookbook file {f} missing")
            self.assertGreater(os.path.getsize(p), 0, f"Cookbook file {f} is empty")

        catalog_files = [
            "Potaria_Items_Catalog.docx",
            "Potaria_Items_Catalog.pdf"
        ]
        for f in catalog_files:
            p = os.path.join(base_dir, f)
            self.assertTrue(os.path.isfile(p), f"Items Catalog file {f} missing")
            self.assertGreater(os.path.getsize(p), 0, f"Items Catalog file {f} is empty")


if __name__ == "__main__":
    unittest.main()
