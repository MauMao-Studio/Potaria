"""
Unit Tests for Potaria Equipment Update Master Implementation
Validates:
1. Predefined base attributes and randomized min/max ranges
2. Persistent item-instance rolls and validation
3. Strict additional affix slot limits (Epic: 1, Legendary: 1, Mythic: 2, Ancient: 2, Others: 0)
4. Progressive set effects (2-piece and full-set thresholds)
5. Seven Deadly Sins collection
6. Seven Heavenly Virtues collection
7. Filipino-inspired weapons, sets, and accessories
8. Special tags registry and theme metadata
9. Save file HMAC-SHA256 signature generation and anti-cheat tamper verification
10. Backward compatibility with legacy items and saves
"""

import os
import sys
import copy
import json
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

os.environ["SDL_VIDEODRIVER"] = "dummy"
import pygame
pygame.init()
pygame.display.set_mode((1280, 720))

from src.rpg.stats import PlayerStats
from src.rpg.equipment import (
    Equipment, SLOT_HEAD, SLOT_CHEST, SLOT_LEGS, SLOT_WEAPON, SLOT_ACCESSORY,
    ARMOR_DATA, EQUIPMENT_SETS
)
from src.rpg.equipment_update import (
    TAG_REGISTRY, ITEM_STAT_RANGES, MAX_ADDITIONAL_AFFIX_SLOTS,
    PROGRESSIVE_SETS, NEW_EQUIPMENT_DATA,
    get_item_stat_ranges, roll_item_stat_ranges, validate_stat_rolls,
    get_max_additional_slots, can_add_additional_affix_slot, add_additional_affix_slot,
    get_equipped_set_counts, get_active_threshold_bonuses,
    compute_save_signature, verify_save_signature, create_equipment_stack
)
from src.ui.inventory import ItemStack, ITEM_REGISTRY


class TestEquipmentUpdate(unittest.TestCase):
    def setUp(self):
        self.stats = PlayerStats()
        self.stats.base_atk = 20
        self.stats.base_def = 10
        self.stats.base_max_hp = 100
        self.stats.hp = 100
        self.stats.base_crit_rate = 5.0
        self.stats.base_speed = 1.0
        self.stats.base_mp_regen = 1.0
        self.equipment = Equipment()

    def test_01_predefined_stat_ranges_and_rolls(self):
        """Verifies base attributes are predefined and rolls stay strictly within min/max bounds."""
        ranges = get_item_stat_ranges("kampilan")
        self.assertIsNotNone(ranges)
        self.assertIn("atk", ranges)
        self.assertIn("crit", ranges)
        self.assertEqual(ranges["atk"]["min"], 32)
        self.assertEqual(ranges["atk"]["max"], 42)

        # Roll 50 independent instances and verify every roll is bounded
        for seed in range(50):
            rolls = roll_item_stat_ranges("kampilan", rng_seed=seed)
            self.assertIsNotNone(rolls)
            self.assertTrue(validate_stat_rolls("kampilan", rolls))
            self.assertGreaterEqual(rolls["atk"], 32)
            self.assertLessEqual(rolls["atk"], 42)
            self.assertGreaterEqual(rolls["crit"], 6.0)
            self.assertLessEqual(rolls["crit"], 10.0)

        # Invalid roll rejection (undeclared attribute or out-of-range value)
        bad_roll_out_of_bounds = {"atk": 999, "crit": 8.0}
        self.assertFalse(validate_stat_rolls("kampilan", bad_roll_out_of_bounds))
        bad_roll_extra_attr = {"atk": 35, "crit": 8.0, "defense": 50}
        self.assertFalse(validate_stat_rolls("kampilan", bad_roll_extra_attr))

    def test_02_roll_persistence_on_item_instances(self):
        """Verifies rolled base stats persist across clone, data property overlay, and equip/unequip."""
        rolls = {"atk": 38, "crit": 9.5}
        stack = ItemStack("kampilan", 1, base_rolls=rolls, tags=["pinoy_heritage", "combat_offensive"])

        # Check data property overlay
        item_data = stack.data
        self.assertEqual(item_data["atk"], 38)
        self.assertEqual(item_data["crit"], 9.5)
        self.assertEqual(stack.tags, ["pinoy_heritage", "combat_offensive"])

        # Clone must keep rolls identical without re-rolling
        clone_stack = stack.clone()
        self.assertEqual(clone_stack.base_rolls, rolls)
        self.assertEqual(clone_stack.data["atk"], 38)

        # Equip into weapon slot and recalculate stats
        self.equipment.equip(stack, self.stats)
        self.assertGreaterEqual(self.stats.bonus_atk, 38)

        # Unequip and verify instance retains rolled values
        unequipped = self.equipment.unequip(SLOT_WEAPON, self.stats)
        self.assertEqual(unequipped.base_rolls, rolls)
        self.assertEqual(self.stats.bonus_atk, 0)

    def test_03_strict_additional_affix_slot_limits(self):
        """Enforces strict rarity limits: Common/Uncommon/Rare=0, Epic=1, Legendary=1, Mythic=2, Ancient=2."""
        self.assertEqual(get_max_additional_slots("common"), 0)
        self.assertEqual(get_max_additional_slots("uncommon"), 0)
        self.assertEqual(get_max_additional_slots("rare"), 0)
        self.assertEqual(get_max_additional_slots("epic"), 1)
        self.assertEqual(get_max_additional_slots("legendary"), 1)
        self.assertEqual(get_max_additional_slots("mythic"), 2)
        self.assertEqual(get_max_additional_slots("ancient"), 2)

        # Ineligible rarity (Rare) cannot receive additional affix slot
        rare_item = ItemStack("panabas", 1)  # Panabas is epic, let's test a rare item
        rare_test = ItemStack("wood_axe", 1) # Common
        can_add, reason = can_add_additional_affix_slot(rare_test)
        self.assertFalse(can_add)
        self.assertIn("cannot receive", reason)

        # Epic item (Panabas) allows at most 1 additional slot
        epic_item = ItemStack("panabas", 1)
        can_add, _ = can_add_additional_affix_slot(epic_item)
        self.assertTrue(can_add)
        success, msg = add_additional_affix_slot(epic_item, cost_copper=0)
        self.assertTrue(success)
        self.assertEqual(epic_item.additional_affix_slots, 1)

        # Second attempt on Epic must be strictly rejected
        can_add_2, reason_2 = can_add_additional_affix_slot(epic_item)
        self.assertFalse(can_add_2)
        self.assertIn("maximum limit", reason_2)

        # Ancient item allows up to 2 additional slots
        ancient_item = ItemStack("ancient_helmet", 1)
        self.assertTrue(can_add_additional_affix_slot(ancient_item)[0])
        add_additional_affix_slot(ancient_item, cost_copper=0)
        self.assertEqual(ancient_item.additional_affix_slots, 1)
        self.assertTrue(can_add_additional_affix_slot(ancient_item)[0])
        add_additional_affix_slot(ancient_item, cost_copper=0)
        self.assertEqual(ancient_item.additional_affix_slots, 2)
        # Third attempt on Ancient must be rejected
        self.assertFalse(can_add_additional_affix_slot(ancient_item)[0])

    def test_04_progressive_set_threshold_activation(self):
        """Verifies progressive thresholds activate at 2-piece and 3-piece, and deactivate on unequip."""
        # 1. Equip 2 pieces of Diwata's Bloom set (Crown + Gown)
        self.equipment.equip(ItemStack("diwata_crown", 1), self.stats)
        self.equipment.equip(ItemStack("diwata_gown", 1), self.stats)

        counts = get_equipped_set_counts(["diwata_crown", "diwata_gown"])
        self.assertEqual(counts.get("diwata_bloom"), 2)

        bonuses = get_active_threshold_bonuses(["diwata_crown", "diwata_gown"])
        self.assertEqual(len(bonuses), 1)
        set_id, tier, t_dict = bonuses[0]
        self.assertEqual(set_id, "diwata_bloom")
        self.assertEqual(tier, 2)
        self.assertEqual(t_dict.get("bonus_mp_regen"), 2.0)

        # Stats should reflect 2-piece bonus
        self.equipment.recalculate_stats(self.stats)
        self.assertGreaterEqual(self.stats.bonus_mp_regen, 2.0)

        # 2. Equip 3rd piece (Diwata Sandals) for Full Set
        self.equipment.equip(ItemStack("diwata_sandals", 1), self.stats)
        bonuses_full = get_active_threshold_bonuses(["diwata_crown", "diwata_gown", "diwata_sandals"])
        self.assertEqual(len(bonuses_full), 1)
        self.assertEqual(bonuses_full[0][1], 3)
        self.assertEqual(bonuses_full[0][2].get("aura"), "blossom")
        self.assertEqual(self.equipment.get_active_aura(), "blossom")

        # 3. Unequip one piece and verify deactivation down to tier 2
        self.equipment.unequip(SLOT_LEGS, self.stats)
        self.assertEqual(self.equipment.get_active_aura(), None)
        bonuses_down = get_active_threshold_bonuses(["diwata_crown", "diwata_gown"])
        self.assertEqual(bonuses_down[0][1], 2)

    def test_05_seven_deadly_sins_catalog_and_set(self):
        """Verifies all Seven Deadly Sins items exist and their set bonuses function."""
        sins = ["sin_pride", "sin_greed", "sin_lust", "sin_envy", "sin_gluttony", "sin_wrath", "sin_sloth"]
        for sin in sins:
            self.assertIn(sin, PROGRESSIVE_SETS)
            s_data = PROGRESSIVE_SETS[sin]
            self.assertIn(2, s_data["thresholds"])
            self.assertIn(3, s_data["thresholds"])
            for piece in s_data["pieces"]:
                self.assertIn(piece, ARMOR_DATA)
                self.assertIn(piece, ITEM_REGISTRY)

        # Test Wrath 2-piece and 3-piece
        self.equipment.clear_all_items(self.stats)
        self.equipment.equip(ItemStack("wrath_helm", 1), self.stats)
        self.equipment.equip(ItemStack("wrath_cuirass", 1), self.stats)
        self.equipment.recalculate_stats(self.stats)
        self.assertGreater(self.stats.bonus_atk, 0)

    def test_06_seven_heavenly_virtues_catalog_and_set(self):
        """Verifies all Seven Heavenly Virtues items exist and their set bonuses function."""
        virtues = [
            "virtue_humility", "virtue_charity", "virtue_chastity",
            "virtue_gratitude", "virtue_temperance", "virtue_kindness", "virtue_diligence"
        ]
        for v in virtues:
            self.assertIn(v, PROGRESSIVE_SETS)
            v_data = PROGRESSIVE_SETS[v]
            self.assertIn(2, v_data["thresholds"])
            self.assertIn(3, v_data["thresholds"])
            for piece in v_data["pieces"]:
                self.assertIn(piece, ARMOR_DATA)
                self.assertIn(piece, ITEM_REGISTRY)

        # Test Humility 2-piece and 3-piece
        self.equipment.clear_all_items(self.stats)
        self.equipment.equip(ItemStack("humility_circlet", 1), self.stats)
        self.equipment.equip(ItemStack("humility_vestment", 1), self.stats)
        self.equipment.recalculate_stats(self.stats)
        self.assertGreater(self.stats.bonus_def, 0)
        self.assertGreaterEqual(self.stats.bonus_max_hp, 25)

    def test_07_filipino_inspired_weapons_and_sets(self):
        """Verifies Filipino weapons, sets, and accessories exist with rich cultural lore and proper stats."""
        pinoy_weapons = ["kampilan", "panabas", "kris", "balisong", "bangkaw"]
        for w in pinoy_weapons:
            self.assertIn(w, NEW_EQUIPMENT_DATA)
            self.assertIn(w, ITEM_REGISTRY)
            data = ITEM_REGISTRY[w]
            self.assertIn("pinoy_heritage", data.get("tags", []))
            self.assertTrue(len(data.get("lore", "")) > 10)

        pinoy_sets = ["diwata_bloom", "bakunawa_eclipse", "sarimanok_regalia", "tikbalang_trailblazer"]
        for s in pinoy_sets:
            self.assertIn(s, PROGRESSIVE_SETS)

        pinoy_accessories = ["agimat_iron_heart", "anting_anting_wanderer", "pearl_of_the_deep", "bayanihan_charm"]
        for a in pinoy_accessories:
            self.assertIn(a, NEW_EQUIPMENT_DATA)
            self.assertIn("pinoy_heritage", NEW_EQUIPMENT_DATA[a].get("tags", []))

    def test_08_special_tags_registry(self):
        """Verifies TAG_REGISTRY contains complete visual and thematic metadata without stat pollution."""
        required_tags = [
            "sin_pride", "sin_wrath", "virtue_humility", "virtue_charity",
            "pinoy_heritage", "combat_offensive", "combat_defensive"
        ]
        for tag_id in required_tags:
            self.assertIn(tag_id, TAG_REGISTRY)
            tag_spec = TAG_REGISTRY[tag_id]
            self.assertIn("display_name", tag_spec)
            self.assertIn("description", tag_spec)
            self.assertIn("category", tag_spec)
            self.assertIn("color", tag_spec)

    def test_09_save_hmac_signature_and_anti_cheat(self):
        """Verifies HMAC-SHA256 signature generation and tamper rejection."""
        mock_save = {
            "world_name": "TestWorld",
            "player": {"stats": {"hp": 100, "level": 5}, "inventory": []}
        }
        payload_bytes = json.dumps(mock_save, sort_keys=True).encode("utf-8")
        sig = compute_save_signature(payload_bytes)
        self.assertIsInstance(sig, str)
        self.assertEqual(len(sig), 64)

        # Signature verification should succeed on untouched payload
        self.assertTrue(verify_save_signature(payload_bytes, sig))

        # Tampered payload (e.g. edited stats) must fail signature verification
        tampered_save = copy.deepcopy(mock_save)
        tampered_save["player"]["stats"]["hp"] = 99999
        tampered_bytes = json.dumps(tampered_save, sort_keys=True).encode("utf-8")
        self.assertFalse(verify_save_signature(tampered_bytes, sig))

    def test_10_legacy_item_and_save_backward_compatibility(self):
        """Verifies legacy items without base_rolls cleanly fallback to catalog attributes without error."""
        legacy_stack = ItemStack("wooden_sword", 1)  # No base_rolls passed
        self.assertIsNone(legacy_stack.base_rolls)
        self.assertEqual(legacy_stack.data["damage"], 7)

        # Legacy save load simulation: item dict without base_rolls
        legacy_data = {"item_id": "iron_broadsword", "count": 1}
        restored = ItemStack(
            legacy_data["item_id"],
            legacy_data.get("count", 1),
            base_rolls=legacy_data.get("base_rolls")
        )
        self.assertIsNone(restored.base_rolls)
        self.assertEqual(restored.data["atk"], 18)

    def test_11_edge_cases_and_boundary_rolls(self):
        """Verifies boundary values, invalid inputs, and error conditions."""
        # 1. Non-existent item stat range is None
        self.assertIsNone(get_item_stat_ranges("non_existent_item_xyz"))
        self.assertIsNone(roll_item_stat_ranges("non_existent_item_xyz"))
        self.assertTrue(validate_stat_rolls("non_existent_item_xyz", {"atk": 50}))

        # 2. Boundary values exactly on min and max
        ranges = get_item_stat_ranges("kampilan")
        min_roll = {"atk": ranges["atk"]["min"], "crit": ranges["crit"]["min"], "speed": ranges["speed"]["min"]}
        max_roll = {"atk": ranges["atk"]["max"], "crit": ranges["crit"]["max"], "speed": ranges["speed"]["max"]}
        self.assertTrue(validate_stat_rolls("kampilan", min_roll))
        self.assertTrue(validate_stat_rolls("kampilan", max_roll))

        # Out-of-bounds by 1 or float epsilon
        below_min = {"atk": ranges["atk"]["min"] - 1, "crit": ranges["crit"]["min"], "speed": ranges["speed"]["min"]}
        above_max = {"atk": ranges["atk"]["max"] + 1, "crit": ranges["crit"]["max"], "speed": ranges["speed"]["max"]}
        self.assertFalse(validate_stat_rolls("kampilan", below_min))
        self.assertFalse(validate_stat_rolls("kampilan", above_max))

        # 3. Broken item cannot receive affix slot
        broken_item = ItemStack("panabas", 1)
        broken_item.is_broken = True
        can_add, reason = can_add_additional_affix_slot(broken_item)
        self.assertFalse(can_add)
        self.assertIn("broken", reason.lower())

        # 4. None / empty item
        can_add, reason = can_add_additional_affix_slot(None)
        self.assertFalse(can_add)

    def test_12_all_sins_and_virtues_instantiation(self):
        """Verifies every item in NEW_EQUIPMENT_DATA can be created as an ItemStack with valid rolls and tags."""
        for item_id in NEW_EQUIPMENT_DATA:
            stack = create_equipment_stack(item_id, count=1)
            self.assertIsNotNone(stack)
            self.assertEqual(stack.item_id, item_id)
            if item_id in ITEM_STAT_RANGES:
                self.assertIsNotNone(stack.base_rolls)
                self.assertTrue(validate_stat_rolls(item_id, stack.base_rolls))
            tags = NEW_EQUIPMENT_DATA[item_id].get("tags", [])
            for t in tags:
                self.assertIn(t, stack.tags)


if __name__ == "__main__":
    unittest.main()
