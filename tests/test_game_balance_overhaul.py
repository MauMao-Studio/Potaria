"""
Unit and Integration Tests for Potaria Whole-Game Balance & 5-Active-Meal-Buff Overhaul.

Verifies:
1. 5-Meal Buff System:
   - Exactly 1 meal per category (Offense, Defense, Mobility, Resource, Utility).
   - Category replacement without duration stacking.
   - Magnitude non-stacking across repeated meals.
   - Immediate healing decoupled from timed buffs.
   - Cleanse items (Herbal Salve) as instant actions without taking meal slots.
   - All 18 stat contribution caps strictly enforced.
2. Recipe Reconciliations:
   - Kinilaw na Tanigue canonical definition (90 HP, Mobility +12% speed for 3m).
   - Inihaw na Tanigue (90 HP, Mobility +8% speed for 2m).
3. Equipment, Affix Limits & Enhancement:
   - Max 1 additional affix slot for Epic/Legendary.
   - Max 2 additional affix slots for Mythic/Ancient.
4. Risk Register 8 Items Tuning:
   - Genesis World Cleaver, Celestial Titan Plate, Crown of Potaria,
     Chronos Primordial Heart, Void Edge, Magma Greatsword, Celestial Titan Greatsword,
     Zephyr Striders.
5. Combat & Defense Mechanics:
   - +15% total damage mitigation logic.
   - Eternal Bloom restores 50% HP at 1 HP threshold.
   - +8 True Damage / +8 Fire Damage weapon bonus applications.
6. Progressive Set Scaling Milestones:
   - Seven Deadly Sins, Seven Heavenly Virtues, and Katipunero sets scale cleanly at 2, 4, 5 pieces.
"""

import os
import sys
import json
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pygame
pygame.init()
pygame.display.set_mode((1, 1), pygame.NOFRAME)

from src.assets.asset_factory import AssetFactory
from src.audio.sound_effects import SoundManager
from src.entities.player import Player, MEAL_BUFF_CAPS
from src.ui.inventory import ITEM_REGISTRY
from src.rpg.equipment import Equipment, ARMOR_DATA, SLOT_HEAD, SLOT_CHEST, SLOT_LEGS, SLOT_WEAPON, SLOT_ACCESSORY
from src.rpg.equipment_update import (
    PROGRESSIVE_SETS,
    MAX_ADDITIONAL_AFFIX_SLOTS,
    can_add_additional_affix_slot,
    get_active_threshold_bonuses
)


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


class TestGameBalanceOverhaul(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.asset_factory = AssetFactory()
        cls.sound_manager = SoundManager()
        cls.base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

    def setUp(self):
        self.player = Player(100, 100, self.asset_factory, self.sound_manager)
        if hasattr(self.player, "meal_buffs"):
            self.player.meal_buffs.clear()

    # -------------------------------------------------------------------------
    # 1. 5-Meal Timed Buff Architecture & Replacement Rules
    # -------------------------------------------------------------------------
    def test_01_five_active_meal_buff_categories_and_replacement(self):
        """Verifies strictly 1 buff per category and clean replacement with fresh duration."""
        self.player.meal_buffs.clear()

        # 1. Offense: chicken_adobo (180s)
        self.assertTrue(self.player.consume_item("chicken_adobo"))
        self.assertIn("offense", self.player.meal_buffs)
        self.assertEqual(self.player.meal_buffs["offense"]["duration"], 180)

        # 2. Defense: sinigang (180s)
        self.assertTrue(self.player.consume_item("sinigang"))
        self.assertIn("defense", self.player.meal_buffs)

        # 3. Mobility: kinilaw_na_tanigue (180s)
        self.assertTrue(self.player.consume_item("kinilaw_na_tanigue"))
        self.assertIn("mobility", self.player.meal_buffs)

        # 4. Resource: bulalo (240s)
        self.assertTrue(self.player.consume_item("bulalo"))
        self.assertIn("resource", self.player.meal_buffs)

        # 5. Utility: balut (180s)
        self.assertTrue(self.player.consume_item("balut"))
        self.assertIn("utility", self.player.meal_buffs)

        # All 5 categories active simultaneously
        self.assertEqual(len(self.player.meal_buffs), 5)

        # Advance offense duration artificially to 45s remaining
        self.player.meal_buffs["offense"]["duration"] = 45.0

        # Replace offense with pork_adobo (180s)
        self.assertTrue(self.player.consume_item("pork_adobo"))
        self.assertEqual(len(self.player.meal_buffs), 5)
        self.assertEqual(self.player.meal_buffs["offense"]["item_id"], "pork_adobo")
        # Fresh authored duration, no duration stacking
        self.assertEqual(self.player.meal_buffs["offense"]["duration"], 180.0)

    def test_02_repeated_meal_no_magnitude_or_duration_stacking(self):
        """Consuming the same dish refreshes the authored duration without stacking magnitude."""
        self.player.meal_buffs.clear()
        self.player.consume_item("chicken_adobo")
        initial_val = self.player.get_meal_buff_val("damage_mult")

        # Simulate eating again
        self.player.consume_item("chicken_adobo")
        repeated_val = self.player.get_meal_buff_val("damage_mult")

        self.assertEqual(initial_val, repeated_val, "Meal buff magnitude stacked across repeated consumption!")
        self.assertEqual(self.player.meal_buffs["offense"]["duration"], 180.0)

    def test_03_cleanse_and_immediate_healing_independence(self):
        """Immediate healing occurs independently of timed buffs, and Herbal Salve does not occupy a meal slot."""
        self.player.meal_buffs.clear()
        self.player.health = 20

        # Herbal Salve cleanses without occupying a buff slot
        consumed = self.player.consume_item("herbal_salve")
        self.assertTrue(consumed)
        self.assertEqual(len(self.player.meal_buffs), 0, "Herbal salve improperly occupied a meal buff slot!")

        # Kinilaw na Tanigue heals 90 HP immediately and applies mobility buff
        self.player.health = 10
        self.player.consume_item("kinilaw_na_tanigue")
        self.assertEqual(self.player.health, 100, "Immediate healing was not applied separately from meal buff!")
        self.assertIn("mobility", self.player.meal_buffs)

    def test_04_all_stat_contribution_caps_enforced(self):
        """Ensures all 18 stats in MEAL_BUFF_CAPS clamp properly."""
        expected_caps = {
            "damage_mult": 0.12,
            "ranged_damage_mult": 0.12,
            "atk_speed_mult": 0.10,
            "crit_chance": 0.06,
            "crit_dmg_mult": 0.16,
            "armor_pen": 0.10,
            "def": 6,
            "dmg_reduction": 0.06,
            "magic_res": 0.15,
            "speed_mult": 0.15,
            "jump_mult": 0.15,
            "dash_mult": 0.15,
            "knockback_res": 0.15,
            "hp_regen": 2.0,
            "mp_regen": 2.0,
            "mana_cost_reduction": 0.15,
            "luck": 0.10,
            "gathering_speed": 0.20,
            "fishing_power": 0.15,
        }

        for stat, cap in expected_caps.items():
            self.assertIn(stat, MEAL_BUFF_CAPS, f"Missing stat {stat} in MEAL_BUFF_CAPS")
            self.assertEqual(MEAL_BUFF_CAPS[stat], cap, f"Mismatched cap for {stat}")

            # Test clamp logic with an exaggerated mock buff
            self.player.meal_buffs = {
                "test_cat": {
                    "stats": {stat: cap * 3.0}
                }
            }
            capped_val = self.player.get_meal_buff_val(stat)
            self.assertAlmostEqual(capped_val, cap, places=3,
                                  msg=f"Stat {stat} did not clamp to its cap of {cap}")

    # -------------------------------------------------------------------------
    # 2. Recipe Reconciliations
    # -------------------------------------------------------------------------
    def test_05_kinilaw_vs_inihaw_reconciliation(self):
        """Verifies Kinilaw na Tanigue (90 HP, +12% speed, 180s) and Inihaw na Tanigue (90 HP, +8% speed, 120s)."""
        kinilaw = ITEM_REGISTRY.get("kinilaw_na_tanigue")
        inihaw = ITEM_REGISTRY.get("cooked_tanigue")

        self.assertIsNotNone(kinilaw, "kinilaw_na_tanigue missing in registry")
        self.assertIsNotNone(inihaw, "cooked_tanigue missing in registry")

        # Canonical healing values
        self.assertEqual(kinilaw["heal"], 90, "Kinilaw na Tanigue should heal canonical 90 HP")
        self.assertEqual(inihaw["heal"], 90, "Inihaw na Tanigue should heal 90 HP")

        # Canonical buff configurations
        self.assertEqual(kinilaw["buff"]["category"], "mobility")
        self.assertEqual(inihaw["buff"]["category"], "mobility")

        self.assertEqual(kinilaw["buff"]["duration"], 180, "Kinilaw na Tanigue must last 3 min (180s)")
        self.assertEqual(inihaw["buff"]["duration"], 120, "Inihaw na Tanigue must last 2 min (120s)")

        self.assertAlmostEqual(kinilaw["buff"]["stats"].get("speed_mult", 0.0), 0.12)
        self.assertAlmostEqual(inihaw["buff"]["stats"].get("speed_mult", 0.0), 0.08)

    # -------------------------------------------------------------------------
    # 3. Equipment Affix Limits
    # -------------------------------------------------------------------------
    def test_06_affix_slot_limits_by_rarity(self):
        """Enforces max 1 additional affix for Epic/Legendary and max 2 for Mythic/Ancient."""
        self.assertEqual(MAX_ADDITIONAL_AFFIX_SLOTS["epic"], 1)
        self.assertEqual(MAX_ADDITIONAL_AFFIX_SLOTS["legendary"], 1)
        self.assertEqual(MAX_ADDITIONAL_AFFIX_SLOTS["mythic"], 2)
        self.assertEqual(MAX_ADDITIONAL_AFFIX_SLOTS["ancient"], 2)

        # Mock items to test can_add_additional_affix_slot
        class MockItem:
            def __init__(self, rarity, extra_slots):
                self.data = {"rarity": rarity, "atk": 10}
                self.additional_affix_slots = extra_slots
                self.affix_slots = extra_slots
                self.is_broken = False
                self.removed_stats = []

        # Epic / Legendary at 0 extra slots can add 1, at 1 extra slot cannot add another
        self.assertTrue(can_add_additional_affix_slot(MockItem("epic", 0))[0])
        self.assertFalse(can_add_additional_affix_slot(MockItem("epic", 1))[0])
        self.assertTrue(can_add_additional_affix_slot(MockItem("legendary", 0))[0])
        self.assertFalse(can_add_additional_affix_slot(MockItem("legendary", 1))[0])

        # Mythic / Ancient at 1 extra slot can add another; at 2 cannot
        self.assertTrue(can_add_additional_affix_slot(MockItem("mythic", 1))[0])
        self.assertFalse(can_add_additional_affix_slot(MockItem("mythic", 2))[0])
        self.assertTrue(can_add_additional_affix_slot(MockItem("ancient", 1))[0])
        self.assertFalse(can_add_additional_affix_slot(MockItem("ancient", 2))[0])

    # -------------------------------------------------------------------------
    # 4. Risk Register 8 Items Tuning Verification
    # -------------------------------------------------------------------------
    def test_07_risk_register_items_balanced_stats(self):
        """Verifies exact balanced stats for the 8 Risk Register equipment and weapons."""
        weapons_path = os.path.join(self.base_dir, "data", "weapons.json")
        equipments_path = os.path.join(self.base_dir, "data", "equipments.json")

        with open(weapons_path, "r", encoding="utf-8") as f:
            weapons_data = {w["id"]: w for w in json.load(f)}

        with open(equipments_path, "r", encoding="utf-8") as f:
            equip_data = {e["id"]: e for e in json.load(f)}

        # 1. Genesis World Cleaver
        gwc = weapons_data["genesis_world_cleaver"]
        self.assertEqual(gwc["atk"], 85)
        self.assertEqual(gwc["crit"], 24.0)
        self.assertEqual(gwc["speed"], 0.4)
        self.assertEqual(gwc["hp"], 80)
        self.assertEqual(gwc["mp"], 90)
        self.assertEqual(gwc["mp_regen"], 3.0)

        # 2. Void Edge
        ve = weapons_data["void_edge"]
        self.assertEqual(ve["atk"], 46)
        self.assertEqual(ve["crit"], 14.0)
        self.assertEqual(ve["hp"], 30)
        self.assertEqual(ve["mp"], 40)
        self.assertEqual(ve["mp_regen"], 1.8)
        self.assertIn("Armor Penetration (+8 True Damage)", ve["effects"])

        # 3. Magma Greatsword
        mg = weapons_data["magma_greatsword"]
        self.assertEqual(mg["atk"], 34)
        self.assertIn("Molten Blaze (+8 Fire Damage)", mg["effects"])

        # 4. Celestial Titan Greatsword
        ctg = weapons_data["celestial_greatsword"]
        self.assertEqual(ctg["atk"], 62)
        self.assertEqual(ctg["crit"], 20.0)
        self.assertEqual(ctg["speed"], 0.35)
        self.assertIn("Armor Penetration (+15 True Damage)", ctg["effects"])

        # 5. Celestial Titan Plate
        ctp = equip_data["titan_chestplate"]
        self.assertEqual(ctp["atk"], 16)
        self.assertEqual(ctp["def"], 30)
        self.assertEqual(ctp["hp"], 90)
        self.assertEqual(ctp["mp"], 50)
        self.assertEqual(ctp["mp_regen"], 1.5)
        self.assertIn("+15% Total Damage Mitigation", ctp["effects"])

        # 6. Crown of Potaria
        cop = equip_data["crown_of_potaria"]
        self.assertEqual(cop["atk"], 12)
        self.assertEqual(cop["def"], 22)
        self.assertEqual(cop["hp"], 60)
        self.assertEqual(cop["mp"], 60)
        self.assertEqual(cop["mp_regen"], 2.0)

        # 7. Chronos Primordial Heart
        cph = equip_data["chronos_prime_heart"]
        self.assertEqual(cph["atk"], 24)
        self.assertEqual(cph["def"], 22)
        self.assertEqual(cph["crit"], 15.0)
        self.assertEqual(cph["speed"], 0.4)
        self.assertEqual(cph["hp"], 100)
        self.assertEqual(cph["mp"], 90)
        self.assertEqual(cph["mp_regen"], 3.0)
        self.assertIn("Eternal Bloom (Restores 50% HP upon reaching 1 HP, 180s cd)", cph["effects"])

        # 8. Zephyr Striders
        zs = equip_data["zephyr_striders"]
        self.assertEqual(zs["speed"], 0.65)
        self.assertIn("+45% Sprint Speed", zs["effects"])

    # -------------------------------------------------------------------------
    # 5. Combat Mechanics Tuning Verification
    # -------------------------------------------------------------------------
    def test_08_mitigation_and_eternal_bloom_mechanics(self):
        """Verifies +15% total damage mitigation and Eternal Bloom 50% HP restoration."""
        # 1. 15% Damage Mitigation
        self.player.stats.base_def = 0
        self.player.stats.bonus_def = 0
        self.player.health = 200
        self.player.max_health = 200

        # Without mitigation
        base_dmg = 100
        # Equip titan_chestplate
        self.player.equipment.equip("titan_chestplate", self.player.stats)
        # titan_chestplate has 30 def, so 100 - 30 = 70.
        # With 15% mitigation: 70 * 0.85 = 59.5 -> 59 damage taken.
        hp_before = self.player.health
        self.player.take_damage(base_dmg)
        taken = hp_before - self.player.health
        self.assertEqual(taken, 59, f"Expected 59 damage taken with 30 DEF and 15% mitigation, got {taken}")

        # 2. Eternal Bloom triggers at 1 HP threshold and restores 50% HP
        self.player.equipment.equip("chronos_prime_heart")
        self.player.eternal_bloom_cd = 0.0
        self.player.health = 50
        self.player.max_health = 200
        self.player.i_frame_timer = 0.0

        # Hit that would drop player to <= 1 HP
        self.player.take_damage(200)
        self.assertEqual(self.player.health, 100, "Eternal Bloom failed to restore exactly 50% max HP!")
        self.assertEqual(self.player.eternal_bloom_cd, 180.0, "Eternal Bloom cooldown not set to 180s!")

    # -------------------------------------------------------------------------
    # 6. Progressive Sets Scaling Milestones
    # -------------------------------------------------------------------------
    def test_09_progressive_sets_scaling_milestones(self):
        """Verifies SDS, SHV, and Katipunero sets scale cleanly at 2, 4, 5 pieces."""
        sds_sets = ["sin_pride", "sin_greed", "sin_lust", "sin_envy", "sin_gluttony", "sin_wrath", "sin_sloth"]
        shv_sets = [
            "virtue_humility", "virtue_charity", "virtue_chastity", "virtue_gratitude",
            "virtue_temperance", "virtue_kindness", "virtue_diligence", "virtue_patience"
        ]

        all_target_sets = sds_sets + shv_sets + ["katipunero"]

        for set_id in all_target_sets:
            self.assertIn(set_id, PROGRESSIVE_SETS, f"Set {set_id} missing from PROGRESSIVE_SETS")
            s_data = PROGRESSIVE_SETS[set_id]
            thresholds = s_data.get("thresholds", {})
            self.assertIn(2, thresholds, f"Set {set_id} missing 2-piece milestone")
            self.assertIn(4, thresholds, f"Set {set_id} missing 4-piece milestone")
            self.assertIn(5, thresholds, f"Set {set_id} missing 5-piece milestone")

            # Check milestone progression scaling
            pieces = s_data.get("pieces", [])
            self.assertGreaterEqual(len(pieces), 5, f"Set {set_id} has fewer than 5 registered pieces")

            # Test 2 pieces active
            b2 = get_active_threshold_bonuses(pieces[:2], cumulative=False)
            self.assertEqual(len(b2), 1)
            self.assertEqual(b2[0][1], 2)

            # Test 4 pieces active
            b4 = get_active_threshold_bonuses(pieces[:4], cumulative=False)
            self.assertEqual(len(b4), 1)
            self.assertEqual(b4[0][1], 4)

            # Test 5 pieces active
            b5 = get_active_threshold_bonuses(pieces[:5], cumulative=False)
            self.assertEqual(len(b5), 1)
            self.assertEqual(b5[0][1], 5)

    # -------------------------------------------------------------------------
    # 7. Enhancement Module Affix Slot Limits Verification
    # -------------------------------------------------------------------------
    def test_10_enhancement_can_add_affix_slot_limits(self):
        """Verifies src.rpg.enhancement can_add_affix_slot strictly bounds Epic/Legendary to 1 and Mythic/Ancient to 2."""
        from src.rpg.enhancement import can_add_affix_slot

        class MockStack:
            def __init__(self, rarity, slots=0):
                self.data = {"rarity": rarity, "atk": 20, "def": 10}
                self.affix_slots = slots
                self.is_broken = False
                self.removed_stats = []

        # Common/Rare: 0 slots
        self.assertFalse(can_add_affix_slot(MockStack("common", 0))[0])
        self.assertFalse(can_add_affix_slot(MockStack("rare", 0))[0])

        # Epic: 1 slot max
        self.assertTrue(can_add_affix_slot(MockStack("epic", 0))[0])
        self.assertFalse(can_add_affix_slot(MockStack("epic", 1))[0])

        # Legendary: 1 slot max
        self.assertTrue(can_add_affix_slot(MockStack("legendary", 0))[0])
        self.assertFalse(can_add_affix_slot(MockStack("legendary", 1))[0])

        # Mythic: 2 slots max
        self.assertTrue(can_add_affix_slot(MockStack("mythic", 0))[0])
        self.assertTrue(can_add_affix_slot(MockStack("mythic", 1))[0])
        self.assertFalse(can_add_affix_slot(MockStack("mythic", 2))[0])

        # Ancient: 2 slots max
        self.assertTrue(can_add_affix_slot(MockStack("ancient", 0))[0])
        self.assertTrue(can_add_affix_slot(MockStack("ancient", 1))[0])
        self.assertFalse(can_add_affix_slot(MockStack("ancient", 2))[0])

    # -------------------------------------------------------------------------
    # 8. Ranged Weapon & Projectile Meal Buff Scaling
    # -------------------------------------------------------------------------
    def test_11_ranged_projectile_meal_buff_scaling(self):
        """Verifies ArrowProjectile applies ranged_damage_mult, damage_mult, and armor_pen from meal buffs."""
        from src.combat.combat_system import CombatManager
        from src.entities.projectile import ArrowProjectile
        from src.entities.mob import Zombie

        from src.camera import Camera
        from src.entities.particle import ParticleSystem

        particles = ParticleSystem()
        cam = Camera(1280, 720)
        combat = CombatManager(self.asset_factory, self.sound_manager, particles, cam)
        mob = Zombie(150, 100, self.asset_factory)
        mob.hp = 500
        mob.max_hp = 500
        mob.hurt_timer = 0.0
        combat.mobs = [mob]

        # 1. Base damage without food buffs
        self.player.meal_buffs.clear()
        self.player.stats.base_crit_rate = 0.0
        self.player.stats.bonus_crit = 0.0
        self.player.stats.bonus_atk = 0
        proj = ArrowProjectile(145, 100, angle_rad=0.0, speed=20.0, damage=30)
        combat.projectiles = [proj]
        combat.update(0.016, DummyWorld(), self.player)
        dmg_unbuffed = 500 - mob.hp
        self.assertGreaterEqual(dmg_unbuffed, 25)

        # 2. Damage with Daing na Bangus (ranged_damage_mult: 0.06, damage_mult: 0.06) + armor_pen: 0.10
        mob.hp = 500
        mob.hurt_timer = 0.0
        self.player.meal_buffs["offense"] = {
            "item_id": "daing_na_bangus",
            "category": "offense",
            "duration": 180,
            "stats": {"ranged_damage_mult": 0.06, "armor_pen": 0.10}
        }
        proj2 = ArrowProjectile(145, 100, angle_rad=0.0, speed=20.0, damage=30)
        combat.projectiles = [proj2]
        combat.update(0.016, DummyWorld(), self.player)
        dmg_buffed = 500 - mob.hp
        self.assertGreater(dmg_buffed, dmg_unbuffed, "Ranged damage meal buff failed to increase projectile damage!")

    # -------------------------------------------------------------------------
    # 9. Fishing Power & Gathering Speed Mechanics
    # -------------------------------------------------------------------------
    def test_12_fishing_power_reeling_speed_buff(self):
        """Verifies fishing minigame reeling progress scales with fishing_power meal buff."""
        from src.ui.fishing_minigame import FishingBattleMiniGame

        mini = FishingBattleMiniGame(self.asset_factory, self.sound_manager)
        mini.start(fish_id="raw_bangus")
        mini.is_thrashing = False

        # Reeling without buff
        self.player.meal_buffs.clear()
        mini.reeling_progress = 0.0
        mini.handle_click(is_right_click=True, player=self.player)
        base_progress = mini.reeling_progress

        # Reeling with fishing_power: 0.15 buff
        self.player.meal_buffs["utility"] = {
            "item_id": "angler_broth",
            "category": "utility",
            "duration": 180,
            "stats": {"fishing_power": 0.15}
        }
        mini.reeling_progress = 0.0
        mini.handle_click(is_right_click=True, player=self.player)
        buffed_progress = mini.reeling_progress
        self.assertAlmostEqual(buffed_progress, base_progress * 1.15, places=4,
                               msg="Fishing power meal buff failed to accelerate reeling progress!")


if __name__ == "__main__":
    unittest.main()
