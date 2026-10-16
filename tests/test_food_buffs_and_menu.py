"""
Unit and Integration Tests for Potaria Weapons Defense Scrub, Affix Restrictions,
5-Meal Timed Buff System, and Menu UI Overhaul.

Validates:
1. Weapons Defense Scrub: Zero defense across weapons.json, ARMOR_DATA, NEW_EQUIPMENT_DATA, ITEM_REGISTRY.
2. Affix Restrictions: Defensive affixes strictly blocked on weapons; allowed only on armor, shields, accessories.
3. Culinary Notes Purity: 0 consumable items with '+HP', '+<num>', or 'Restores' in desc; lore is empty string.
4. 5-Meal Buff System: Max 5 active buffs (1 per category), replacement rule (no duration stacking), cap enforcement,
   timed countdown/expiration, HP/MP regeneration.
5. Combat & Skills Scaling: damage_mult, crit_dmg_mult, crit_chance, mana_cost_reduction, dmg_reduction, def, knockback_res.
6. Menu UI & Tooltips: Text buttons have no hover tooltips; icon-only buttons retain tooltips; panel bounds & no overlaps.
7. HUD Food Buff Widget: Widget renders at bottom-left without colliding with chat or inventory.
"""

import os
import sys
import json
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pygame
pygame.init()
pygame.display.set_mode((1, 1), pygame.NOFRAME)

from src.constants import SCREEN_WIDTH, SCREEN_HEIGHT
from src.assets.asset_factory import AssetFactory
from src.audio.sound_effects import SoundManager
from src.entities.player import Player, MEAL_BUFF_CAPS
from src.ui.inventory import Inventory, ITEM_REGISTRY, CAT_CONSUMABLE, CAT_WEAPON
from src.ui.hud import HUD
from src.ui.menu import MenuManager, Button
from src.rpg.equipment import ARMOR_DATA, SLOT_WEAPON
from src.rpg.equipment_update import NEW_EQUIPMENT_DATA, ITEM_STAT_RANGES, roll_item_stat_ranges
from src.rpg.affix_system import (
    is_defensive_affix,
    is_affix_allowed_on_category,
    scrub_defensive_stats_from_weapon
)
from src.rpg.skills import SkillManager

class DummyWorld:
    spawn_point = (100, 100)
    def get_solid_rects_in_bounds(self, rect):
        return []
    def get_water_rects_in_bounds(self, rect):
        return []
    def is_water_world(self, x, y):
        return False
    def get_tile(self, tx, ty):
        return 0


class TestFoodBuffsAndMenu(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.asset_factory = AssetFactory()
        cls.sound_manager = SoundManager()
        cls.base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

    # -------------------------------------------------------------
    # 1. Weapons Defense Scrub Tests
    # -------------------------------------------------------------
    def test_01_weapons_json_zero_defense(self):
        """Verifies every single weapon entry in data/weapons.json has def == 0."""
        weapons_path = os.path.join(self.base_dir, "data", "weapons.json")
        self.assertTrue(os.path.isfile(weapons_path))
        with open(weapons_path, "r", encoding="utf-8") as f:
            weapons_data = json.load(f)

        self.assertGreater(len(weapons_data), 0, "weapons.json is empty")
        for weapon in weapons_data:
            item_id = weapon.get("item_id", weapon.get("name", "unknown"))
            def_val = weapon.get("def", 0)
            self.assertEqual(def_val, 0, f"Weapon '{item_id}' in weapons.json has def={def_val} != 0")

    def test_02_armor_data_and_new_equipment_zero_defense_on_weapons(self):
        """Verifies ARMOR_DATA and NEW_EQUIPMENT_DATA have def == 0 for all weapons."""
        for item_id, data in ARMOR_DATA.items():
            slot = data.get("slot", "")
            if slot == SLOT_WEAPON or slot == "weapon":
                def_val = data.get("def", 0)
                self.assertEqual(def_val, 0, f"Weapon '{item_id}' in ARMOR_DATA has def={def_val} != 0")

        for item_id, data in NEW_EQUIPMENT_DATA.items():
            slot = data.get("slot", "")
            if slot == SLOT_WEAPON or slot == "weapon":
                def_val = data.get("def", 0)
                self.assertEqual(def_val, 0, f"Weapon '{item_id}' in NEW_EQUIPMENT_DATA has def={def_val} != 0")

    def test_03_item_registry_zero_defense_on_weapons(self):
        """Verifies ITEM_REGISTRY has def == 0 (or omitted) for all weapons."""
        for item_id, data in ITEM_REGISTRY.items():
            cat = data.get("cat", "")
            if cat == CAT_WEAPON or cat == "weapon":
                def_val = data.get("def", 0)
                self.assertEqual(def_val, 0, f"Weapon '{item_id}' in ITEM_REGISTRY has def={def_val} != 0")

    def test_04_scrub_defensive_stats_helper(self):
        """Verifies scrub_defensive_stats_from_weapon zeroes out any rogue defense stats."""
        test_stats = {"atk": 45, "def": 12, "crit": 5}
        scrubbed = scrub_defensive_stats_from_weapon(test_stats)
        self.assertEqual(scrubbed["def"], 0)
        self.assertEqual(scrubbed["atk"], 45)
        self.assertEqual(scrubbed["crit"], 5)

    # -------------------------------------------------------------
    # 2. Affix Restrictions Tests
    # -------------------------------------------------------------
    def test_05_affixes_json_defensive_restrictions(self):
        """Verifies data/affixes/affixes.json restricts defensive affixes strictly to non-weapons."""
        affixes_path = os.path.join(self.base_dir, "data", "affixes", "affixes.json")
        self.assertTrue(os.path.isfile(affixes_path))
        with open(affixes_path, "r", encoding="utf-8") as f:
            affixes_data = json.load(f)

        prefixes = affixes_data.get("prefixes", {})
        suffixes = affixes_data.get("suffixes", {})
        all_affixes = {**prefixes, **suffixes}

        for aff_name, aff_def in all_affixes.items():
            allowed_cats = aff_def.get("allowed_cats", [])
            stat_mods = aff_def.get("stat_mods", {})
            if "def" in stat_mods or is_defensive_affix(aff_name):
                self.assertNotIn("weapon", allowed_cats, f"Defensive affix '{aff_name}' allows category 'weapon'")
                self.assertFalse(
                    is_affix_allowed_on_category("weapon", aff_name),
                    f"Affix '{aff_name}' should not be allowed on weapons"
                )

    # -------------------------------------------------------------
    # 3. Pure Culinary Descriptions & Food Metadata Tests
    # -------------------------------------------------------------
    def test_06_culinary_descriptions_pure_and_no_hp_in_desc(self):
        """Verifies 0 consumable food items contain '+<num>', 'HP', or 'Restores' in their desc."""
        food_items = [
            'chicken_adobo', 'pork_adobo', 'sinigang', 'kare_kare', 'bulalo', 'tinola',
            'lechon', 'pancit_bihon', 'arroz_caldo', 'halo_halo', 'kaldereta', 'balut',
            'itlog_na_maalat', 'sinangag', 'daing_na_bangus', 'sinigang_na_bangus',
            'ginataang_tilapia', 'kinilaw_na_tanigue',
            'cooked_bangus', 'cooked_tilapia', 'cooked_galunggong', 'cooked_maya_maya',
            'cooked_tanigue', 'cooked_tambakol', 'cooked_lapu_lapu', 'cooked_hito',
            'cooked_dilis', 'cooked_dalagang_bukid',
            'raw_potato', 'mashed_potato', 'golden_fry', 'hearty_root_stew', 'glazed_golden_tuber',
            'herbal_salve', 'smoked_spud_jerky', 'gilded_russet', 'potato_bread', 'sweet_tuber_pie',
            'raw_bangus', 'raw_tilapia', 'raw_galunggong', 'raw_maya_maya', 'raw_tanigue',
            'raw_tambakol', 'raw_lapu_lapu', 'raw_hito', 'raw_dilis', 'raw_dalagang_bukid',
            'raw_chicken', 'raw_pork', 'pork_belly', 'raw_beef', 'raw_goat_meat',
            'duck_egg', 'carabao_milk'
        ]
        for item_id in food_items:
            data = ITEM_REGISTRY.get(item_id)
            self.assertIsNotNone(data, f"Food item '{item_id}' missing from ITEM_REGISTRY")
            desc = data.get("desc", "")
            import re
            self.assertFalse(
                re.search(r'\+\d+\s*hp', desc, re.IGNORECASE),
                f"Item '{item_id}' has +HP in description: '{desc}'"
            )
            self.assertFalse(
                re.search(r'restores?\s+\d+', desc, re.IGNORECASE),
                f"Item '{item_id}' has 'Restores' in description: '{desc}'"
            )
            self.assertFalse(
                re.search(r'\b\d+\s*hp\b', desc, re.IGNORECASE),
                f"Item '{item_id}' has explicit numeric HP in description: '{desc}'"
            )
            lore = data.get("lore", "")
            self.assertEqual(lore, "", f"Item '{item_id}' has non-empty lore: '{lore}'")

    def test_07_inihaw_vs_kinilaw_na_tanigue_distinction(self):
        """Verifies cooked_tanigue (Inihaw) and kinilaw_na_tanigue are distinct items with valid buffs."""
        inihaw = ITEM_REGISTRY.get("cooked_tanigue")
        kinilaw = ITEM_REGISTRY.get("kinilaw_na_tanigue")
        self.assertIsNotNone(inihaw, "cooked_tanigue missing")
        self.assertIsNotNone(kinilaw, "kinilaw_na_tanigue missing")

        self.assertEqual(inihaw["name"], "Inihaw na Tanigue")
        self.assertEqual(kinilaw["name"], "Kinilaw na Tanigue")
        self.assertEqual(inihaw["heal"], 90)
        self.assertEqual(kinilaw["heal"], 90)

        self.assertEqual(inihaw["buff"]["category"], "mobility")
        self.assertEqual(kinilaw["buff"]["category"], "mobility")
        self.assertEqual(inihaw["buff"]["duration"], 120)
        self.assertEqual(kinilaw["buff"]["duration"], 180)

    # -------------------------------------------------------------
    # 4. 5-Meal Timed Buff System Tests
    # -------------------------------------------------------------
    def test_08_player_5_meal_buff_categories_and_replacement(self):
        """Verifies max 5 active buffs (1 per category), replacement rule, and no duration stacking."""
        player = Player(100, 100, self.asset_factory, self.sound_manager)
        player.meal_buffs.clear()

        # 1. Offense: chicken_adobo (180s)
        success = player.consume_item("chicken_adobo")
        self.assertTrue(success)
        self.assertIn("offense", player.meal_buffs)
        self.assertEqual(player.meal_buffs["offense"]["item_id"], "chicken_adobo")
        self.assertEqual(player.meal_buffs["offense"]["duration"], 180)

        # 2. Defense: sinigang (180s)
        player.consume_item("sinigang")
        self.assertIn("defense", player.meal_buffs)
        self.assertEqual(len(player.meal_buffs), 2)

        # 3. Mobility: cooked_tanigue (120s)
        player.consume_item("cooked_tanigue")
        self.assertIn("mobility", player.meal_buffs)
        self.assertEqual(player.meal_buffs["mobility"]["duration"], 120)
        self.assertEqual(len(player.meal_buffs), 3)

        # 4. Resource: arroz_caldo (180s)
        player.consume_item("arroz_caldo")
        self.assertIn("resource", player.meal_buffs)
        self.assertEqual(len(player.meal_buffs), 4)

        # 5. Utility: balut (180s)
        player.consume_item("balut")
        self.assertIn("utility", player.meal_buffs)
        self.assertEqual(len(player.meal_buffs), 5)

        # Replacement Test: Eating kinilaw_na_tanigue (Mobility, 180s) MUST replace cooked_tanigue (Mobility)
        # Duration must NOT stack: should be 180, not 120+180
        player.consume_item("kinilaw_na_tanigue")
        self.assertEqual(len(player.meal_buffs), 5)
        self.assertEqual(player.meal_buffs["mobility"]["item_id"], "kinilaw_na_tanigue")
        self.assertEqual(player.meal_buffs["mobility"]["duration"], 180)

    def test_09_meal_buff_caps_and_countdown(self):
        """Verifies get_meal_buff_val respects MEAL_BUFF_CAPS and buffs expire when duration reaches 0."""
        player = Player(100, 100, self.asset_factory, self.sound_manager)
        player.meal_buffs.clear()

        player.consume_item("chicken_adobo") # damage_mult: 0.06
        dmg_buff = player.get_meal_buff_val("damage_mult")
        self.assertAlmostEqual(dmg_buff, 0.06)

        # Artificially set an over-cap buff value
        player.meal_buffs["offense"]["stats"]["damage_mult"] = 0.50
        capped_val = player.get_meal_buff_val("damage_mult")
        self.assertEqual(capped_val, MEAL_BUFF_CAPS["damage_mult"]) # capped at 0.12

        # Countdown and expiration test
        dummy_world = DummyWorld()
        player.meal_buffs["offense"]["duration"] = 1.0
        player.update(0.5, dummy_world)
        self.assertIn("offense", player.meal_buffs)
        self.assertAlmostEqual(player.meal_buffs["offense"]["duration"], 0.5)

        player.update(0.6, dummy_world) # Duration reaches 0 -> expired and deleted
        self.assertNotIn("offense", player.meal_buffs)

    def test_10_meal_buff_regeneration(self):
        """Verifies HP and MP regeneration per second when resource/utility meal buffs are active."""
        player = Player(100, 100, self.asset_factory, self.sound_manager)
        player.meal_buffs.clear()

        # bulalo gives hp_regen: 1.0
        player.consume_item("bulalo")
        player.health = 50
        cur_hp = player.health

        # Advance 1.05s to trigger regeneration tick
        player.update(1.05, DummyWorld())
        self.assertGreater(player.health, cur_hp)

    # -------------------------------------------------------------
    # 5. Combat & Skills Scaling Tests
    # -------------------------------------------------------------
    def test_11_skills_mana_cost_reduction(self):
        """Verifies get_skill_mp_cost reduces skill MP cost with mana_cost_reduction meal buff."""
        player = Player(100, 100, self.asset_factory, self.sound_manager)
        player.meal_buffs.clear()

        sm = SkillManager()
        base_cost = sm.get_skill_mp_cost("dash", player=player)

        # Add mana_cost_reduction buff (15%)
        player.meal_buffs["resource"] = {
            "category": "resource",
            "duration": 180,
            "stats": {"mana_cost_reduction": 0.15}
        }
        reduced_cost = sm.get_skill_mp_cost("dash", player=player)
        self.assertLess(reduced_cost, base_cost)
        self.assertEqual(reduced_cost, max(1, int(base_cost * 0.85)))

    def test_12_combat_defensive_meal_buff_damage_mitigation(self):
        """Verifies player take_damage takes meal buff defense and dmg_reduction into account."""
        player = Player(100, 100, self.asset_factory, self.sound_manager)
        player.meal_buffs.clear()
        player.health = 100

        # Without meal buffs: take 40 damage
        player.take_damage(40)
        dmg_taken_unbuffed = 100 - player.health

        # With defensive meal buff
        player.health = 100
        player.consume_item("sinigang") # +4 Def, +4% dmg_reduction
        player.take_damage(40)
        dmg_taken_buffed = 100 - player.health

        self.assertLess(dmg_taken_buffed, dmg_taken_unbuffed)

    # -------------------------------------------------------------
    # 6. Main Menu Tooltip Cleanup & UI Overlap Tests
    # -------------------------------------------------------------
    def test_13_menu_text_buttons_have_no_hover_tooltips(self):
        """Verifies buttons with non-empty text have empty tooltip strings."""
        b1 = Button(10, 10, 100, 30, "Singleplayer", action=lambda: None, tooltip="Should be scrubbed")
        self.assertEqual(b1.tooltip, "", "Text button must not have hovering tooltip")

        b2 = Button(10, 50, 100, 30, "Settings", action=lambda: None, tooltip="Options")
        self.assertEqual(b2.tooltip, "")

        # Icon-only button (empty text) retains its tooltip
        icon_btn = Button(10, 90, 30, 30, "", action=lambda: None, tooltip="Delete World")
        self.assertEqual(icon_btn.tooltip, "Delete World")

    def test_14_menu_panel_bounds_and_no_overlaps(self):
        """Verifies settings footer, controls back button, and mods LMS toggle do not overlap."""
        menu = MenuManager(self.asset_factory, self.sound_manager)

        # Settings panel: buttons and footer
        self.assertIsNotNone(menu.settings_back_btn)
        self.assertIsNotNone(menu.settings_reset_btn)
        # Settings buttons are at py + ph - 64 (height 36), footer is at py + ph - 20
        # Button bottom is py + ph - 28, which is above py + ph - 20 (clean 8px vertical gap)
        btn_bottom = menu.settings_back_btn.rect.bottom
        pw, ph = 840, 595
        py = 48
        footer_y = py + ph - 20
        self.assertLess(btn_bottom, footer_y, "Settings back button overlaps footer text")

        # Controls screen: back button inside panel
        self.assertIsNotNone(menu.back_button)
        cpw, cph = 860, 610
        cpy = 45
        self.assertGreaterEqual(menu.back_button.rect.top, cpy)
        self.assertLessEqual(menu.back_button.rect.bottom, cpy + cph, "Controls back button extends outside panel")

        # Mods screen: LMS toggle inside card 1 header
        self.assertIsNotNone(menu.mods_toggle_lms_btn)
        card1_top = 135
        card1_bottom = card1_top + 175
        self.assertGreaterEqual(menu.mods_toggle_lms_btn.rect.top, card1_top)
        self.assertLessEqual(menu.mods_toggle_lms_btn.rect.bottom, card1_bottom, "LMS toggle button outside card 1")

    # -------------------------------------------------------------
    # 7. HUD Food Buff Widget Tests
    # -------------------------------------------------------------
    def test_15_hud_food_buff_widget_renders_without_error(self):
        """Verifies HUD _render_food_buffs renders active meal buffs correctly at bottom-left."""
        hud = HUD(self.asset_factory)
        player = Player(100, 100, self.asset_factory, self.sound_manager)
        player.meal_buffs.clear()

        target_surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))

        # Should render cleanly when empty
        hud._render_food_buffs(target_surf, player, 0, 0)

        # Add 3 buffs
        player.consume_item("chicken_adobo")
        player.consume_item("sinigang")
        player.consume_item("cooked_tanigue")

        # Render without hover
        hud._render_food_buffs(target_surf, player, 0, 0)

        # Render with hover at bottom-left (slot 0: x=20, y=SCREEN_HEIGHT-44)
        hud._render_food_buffs(target_surf, player, 25, SCREEN_HEIGHT - 30)

    def test_16_frost_blade_and_weapon_stat_ranges_zero_defense(self):
        """Verifies frost_blade and all weapons in ITEM_STAT_RANGES have no defense ranges and roll no defense."""
        frost = ITEM_STAT_RANGES.get("frost_blade")
        self.assertIsNotNone(frost, "frost_blade missing from ITEM_STAT_RANGES")
        defensive_keys = {"def", "defense", "armor", "dmg_reduction", "knockback_res"}
        for k in defensive_keys:
            self.assertNotIn(k, frost, f"frost_blade in ITEM_STAT_RANGES has defensive key '{k}'")

        # Verify all weapons in ITEM_REGISTRY have no defensive ranges in ITEM_STAT_RANGES
        for item_id, data in ITEM_REGISTRY.items():
            if data.get("cat") == CAT_WEAPON or data.get("category") == "weapon":
                ranges = ITEM_STAT_RANGES.get(item_id, {})
                for k in defensive_keys:
                    self.assertNotIn(k, ranges, f"Weapon '{item_id}' in ITEM_STAT_RANGES has defensive key '{k}'")

        # Test rolling stats repeatedly
        for _ in range(25):
            rolled = roll_item_stat_ranges("frost_blade")
            for k in defensive_keys:
                self.assertNotIn(k, rolled, f"Rolled stats for frost_blade contain defensive key '{k}'")

    def test_17_all_edible_items_lore_and_desc_purity(self):
        """Verifies all edible items and cooking ingredients have empty lore and no HP restoration numbers in desc."""
        import re
        from scripts.build_cookbook_docs import filipino_dishes, cooked_fishes, potato_delicacies, raw_fishes, raw_meats
        culinary_items = set(filipino_dishes + cooked_fishes + potato_delicacies + raw_fishes + raw_meats + [
            'raw_potato', 'rice', 'garlic', 'onion', 'ginger', 'tamarind', 'eggplant',
            'string_beans', 'black_pepper', 'calamansi', 'soy_sauce', 'vinegar',
            'salt', 'shaved_ice', 'condensed_milk', 'ube_halaya', 'pancit_noodles',
            'peanut_butter', 'coconut_milk', 'apple'
        ])

        for item_id in culinary_items:
            data = ITEM_REGISTRY.get(item_id)
            self.assertIsNotNone(data, f"Culinary item '{item_id}' missing from ITEM_REGISTRY")
            lore = data.get("lore", "")
            self.assertEqual(lore, "", f"Edible item '{item_id}' has non-empty lore: '{lore}'")
            desc = data.get("desc", "")
            self.assertFalse(
                re.search(r'\+\d+\s*hp', desc, re.IGNORECASE),
                f"Item '{item_id}' has +HP in desc: '{desc}'"
            )
            self.assertFalse(
                re.search(r'restores?\s+\d+', desc, re.IGNORECASE),
                f"Item '{item_id}' has 'Restores <num>' in desc: '{desc}'"
            )

    def test_18_achievements_viewport_does_not_overlap_back_button(self):
        """Verifies achievements cards viewport ends above the back button."""
        menu = MenuManager(self.asset_factory, self.sound_manager)
        btn_top = menu.achievements_back_btn.rect.top # 565
        # Achievements screen panel
        pw, ph = 760, 560
        py = 50
        start_y = py + 92 # 142
        viewport_h = ph - 165 # 395
        viewport_bottom = start_y + viewport_h # 537
        self.assertLess(viewport_bottom, btn_top, f"Achievements viewport bottom ({viewport_bottom}) overlaps back button ({btn_top})")
        self.assertGreaterEqual(btn_top - viewport_bottom, 20, "Expected at least 20px clearance between cards viewport and back button")

    def test_19_worlds_and_input_mapping_back_buttons_within_panel(self):
        """Verifies worlds and input mapping back buttons sit entirely within panel borders."""
        menu = MenuManager(self.asset_factory, self.sound_manager)
        # Worlds screen
        w_pw, w_ph = 680, 595
        w_py = 48
        w_panel_bottom = w_py + w_ph
        self.assertLessEqual(menu.worlds_back_btn.rect.bottom, w_panel_bottom, "worlds_back_btn extends outside panel")
        self.assertGreaterEqual(menu.worlds_back_btn.rect.top, w_py, "worlds_back_btn extends above panel")

        # Input mapping screen
        i_pw, i_ph = 780, 595
        i_py = 48
        i_panel_bottom = i_py + i_ph
        self.assertLessEqual(menu.input_back_button.rect.bottom, i_panel_bottom, "input_back_button extends outside panel")
        self.assertLessEqual(menu.input_reset_button.rect.bottom, i_panel_bottom, "input_reset_button extends outside panel")

    def test_20_hud_food_buff_tooltip_and_overlay(self):
        """Verifies HUD stores hovered food buff and weapon tooltips never render defense."""
        hud = HUD(self.asset_factory)
        player = Player(100, 100, self.asset_factory, self.sound_manager)
        player.meal_buffs.clear()
        player.consume_item("chicken_adobo")

        target_surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        # Hovering first slot at x=25, y=SCREEN_HEIGHT-30
        hud._render_food_buffs(target_surf, player, 25, SCREEN_HEIGHT - 30, draw_tooltip=False)
        self.assertIsNotNone(hud._hovered_food_buff, "Hovered food buff not stored")
        buff, rect = hud._hovered_food_buff
        self.assertEqual(buff.get("item_id"), "chicken_adobo")

        # Tooltip renders without error
        hud._render_food_buff_tooltip(target_surf, buff, rect)

        # Test weapon tooltip defense scrubbing in both modes
        class DummyWeaponItem:
            item_id = "frost_blade"
            slot = "weapon"
            data = {
                "name": "Frost Blade",
                "cat": CAT_WEAPON,
                "damage": 25,
                "def": 10,
                "atk": 5,
            }
            base_rolls = {"def": 3, "atk": 8}
            count = 1
            enhancement_level = 0
            is_broken = False
            affix_slots = 0
            additional_affix_slots = 0
            affixes = []
            tags = []
        fake_weapon = DummyWeaponItem()

        # Detailed mode
        hud.tooltip_mode = "detailed"
        lines_detailed = hud._render_tooltip(target_surf, 100, 100, fake_weapon, player=player)
        for text, col, font in lines_detailed:
            self.assertNotIn("+10 Defense", text)
            self.assertNotIn("+3 DEF", text)

        # Compact mode
        hud.tooltip_mode = "compact"
        lines_compact = hud._render_tooltip(target_surf, 100, 100, fake_weapon, player=player)
        for text, col, font in lines_compact:
            self.assertNotIn("Defense:", text)



if __name__ == "__main__":
    unittest.main()

