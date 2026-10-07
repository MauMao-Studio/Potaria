"""
Potaria - Attack Speed & Fire Rate (Auto-Clicker Spam Prevention) Test Suite
Developer: Kurados | Pure Python 3.13 & pygame-ce
"""

import unittest
import math
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Set dummy headless video driver
os.environ["SDL_VIDEODRIVER"] = "dummy"
import pygame
pygame.init()
pygame.display.set_mode((1, 1))

from main import PotariaGame
from src.rpg.stats import PlayerStats
from src.rpg.equipment import Equipment, ARMOR_DATA, SLOT_WEAPON, SLOT_LEGS, SLOT_ACCESSORY
from src.entities.player import Player
from src.assets.asset_factory import AssetFactory
from src.ui.inventory import ItemStack, ITEM_REGISTRY, CAT_WEAPON


class TestAttackSpeedAndFireRate(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.af = AssetFactory()

    def setUp(self):
        self.game = PotariaGame()
        self.player = self.game.player
        self.stats = self.player.stats

    def test_01_player_stats_attack_speed_defaults(self):
        """Verifies default attack speed multipliers and properties."""
        stats = PlayerStats()
        self.assertEqual(stats.base_atk_speed, 1.0)
        self.assertEqual(stats.bonus_atk_speed, 0.0)
        self.assertEqual(stats.total_atk_speed, 1.0)
        self.assertEqual(stats.attack_speed, 1.0)
        self.assertEqual(stats.atk_speed, 1.0)

        # Apply bonus attack speed
        stats.bonus_atk_speed = 0.35
        self.assertEqual(stats.total_atk_speed, 1.35)

        # Min clamp check
        stats.bonus_atk_speed = -2.0
        self.assertEqual(stats.total_atk_speed, 0.2)

    def test_02_equipment_recalculate_weapon_attack_speed(self):
        """Verifies weapon speed attribute increases bonus_atk_speed."""
        eq = Equipment()
        stats = PlayerStats()

        # Hold a weapon with speed bonus (e.g. astral_wrath speed = 0.25)
        eq.recalculate_stats(stats, active_item_id="astral_wrath")
        self.assertAlmostEqual(stats.bonus_atk_speed, 0.25, places=2)
        self.assertAlmostEqual(stats.total_atk_speed, 1.25, places=2)

        # Hold a greatsword with speed bonus (celestial_greatsword speed = 0.35)
        eq.recalculate_stats(stats, active_item_id="celestial_greatsword")
        self.assertAlmostEqual(stats.bonus_atk_speed, 0.35, places=2)
        self.assertAlmostEqual(stats.total_atk_speed, 1.35, places=2)

        # Hold standard copper sword (speed = 0)
        eq.recalculate_stats(stats, active_item_id="copper_shortsword")
        self.assertAlmostEqual(stats.bonus_atk_speed, 0.0, places=2)
        self.assertAlmostEqual(stats.total_atk_speed, 1.0, places=2)

    def test_03_player_attack_cooldown_mechanics(self):
        """Tests player.can_attack() and cooldown countdown."""
        self.player.attack_cooldown = 0.0
        self.assertTrue(self.player.can_attack())

        # Trigger attack with 0.30s cooldown
        self.player.trigger_attack(0.30)
        self.assertFalse(self.player.can_attack())
        self.assertAlmostEqual(self.player.attack_cooldown, 0.30, places=2)
        self.assertTrue(self.player.is_swinging)
        self.assertEqual(self.player.swing_progress, 0.0)

        # Step 0.15s
        self.player.update(0.15, self.game.world)
        self.assertFalse(self.player.can_attack())
        self.assertAlmostEqual(self.player.attack_cooldown, 0.15, places=2)

        # Step another 0.16s -> cooldown expires
        self.player.update(0.16, self.game.world)
        self.assertTrue(self.player.can_attack())
        self.assertEqual(self.player.attack_cooldown, 0.0)

    def test_04_auto_clicker_spam_prevention(self):
        """Simulates an auto-clicker spamming 50 clicks in a single frame.
        Only the 1st attack must succeed; 49 must be rejected!"""
        self.game.inventory.slots[0] = ItemStack("copper_broadsword", 1)
        self.game.inventory.selected_slot = 0
        self.game.player.attack_cooldown = 0.0

        success_count = 0
        rejected_count = 0

        # Simulate 50 clicks in one frame
        for _ in range(50):
            res = self.game.handle_primary_action(200, 200)
            if res:
                success_count += 1
            else:
                rejected_count += 1

        self.assertEqual(success_count, 1, "Exactly 1 attack must succeed per attack interval!")
        self.assertEqual(rejected_count, 49, "All 49 auto-clicker spam clicks must be rejected!")
        self.assertGreater(self.game.player.attack_cooldown, 0.0)

    def test_05_projectile_weapon_spam_prevention(self):
        """Verifies bows, magic staves, and celestial weapons cannot spam projectiles in a frame."""
        # Test Magic Staff
        self.game.inventory.slots[0] = ItemStack("frost_staff", 1)
        self.game.inventory.selected_slot = 0
        self.game.player.attack_cooldown = 0.0
        self.game.player.fireballs.clear()

        # 30 clicks in one frame
        for _ in range(30):
            self.game.handle_primary_action(300, 300)

        self.assertEqual(len(self.game.player.fireballs), 1, "Only 1 fireball must spawn, not 30!")

        # Test Starfury
        self.game.inventory.slots[0] = ItemStack("starfury", 1)
        self.game.inventory.selected_slot = 0
        self.game.player.attack_cooldown = 0.0
        self.game.combat.projectiles.clear()

        # 25 clicks in one frame
        for _ in range(25):
            self.game.handle_primary_action(400, 400)

        self.assertEqual(len(self.game.combat.projectiles), 1, "Only 1 starfury star must spawn, not 25!")

    def test_06_weapon_archetype_base_cooldowns(self):
        """Verifies different weapon archetypes have distinct, balanced base attack intervals."""
        item_shortsword = ItemStack("copper_shortsword", 1)
        item_broadsword = ItemStack("copper_broadsword", 1)
        item_greatsword = ItemStack("magma_greatsword", 1)
        item_bow = ItemStack("wood_bow", 1)
        item_staff = ItemStack("fire_staff", 1)

        self.player.stats.bonus_atk_speed = 0.0

        cd_short = self.game.get_weapon_attack_cooldown(item_shortsword)
        cd_broad = self.game.get_weapon_attack_cooldown(item_broadsword)
        cd_great = self.game.get_weapon_attack_cooldown(item_greatsword)
        cd_bow = self.game.get_weapon_attack_cooldown(item_bow)
        cd_staff = self.game.get_weapon_attack_cooldown(item_staff)

        # Shortsword must be faster than broadsword, and greatsword slowest
        self.assertLess(cd_short, cd_broad)
        self.assertLess(cd_broad, cd_great)
        self.assertAlmostEqual(cd_short, 0.22, places=2)
        self.assertAlmostEqual(cd_broad, 0.32, places=2)
        self.assertAlmostEqual(cd_great, 0.46, places=2)

    def test_07_attack_speed_scaling_reduces_cooldown(self):
        """Verifies higher attack speed reduces attack cooldown proportionally."""
        item_broadsword = ItemStack("copper_broadsword", 1)

        # 1.0x attack speed
        self.player.stats.bonus_atk_speed = 0.0
        cd_base = self.game.get_weapon_attack_cooldown(item_broadsword)

        # 1.5x attack speed (+50% attack speed)
        self.player.stats.bonus_atk_speed = 0.50
        cd_boosted = self.game.get_weapon_attack_cooldown(item_broadsword)

        # 2.0x attack speed (+100% attack speed)
        self.player.stats.bonus_atk_speed = 1.0
        cd_super = self.game.get_weapon_attack_cooldown(item_broadsword)

        self.assertAlmostEqual(cd_boosted, cd_base / 1.5, places=2)
        self.assertAlmostEqual(cd_super, cd_base / 2.0, places=2)
        self.assertLess(cd_super, cd_boosted)
        self.assertLess(cd_boosted, cd_base)

    def test_08_swing_duration_syncs_with_attack_speed(self):
        """Verifies player swing visual animation duration adapts to attack speed."""
        self.player.trigger_attack(0.20)
        self.assertAlmostEqual(self.player.swing_duration, 0.20, places=2)

        self.player.trigger_attack(0.40)
        self.assertAlmostEqual(self.player.swing_duration, 0.40, places=2)

    def test_09_single_swing_single_hit_per_target(self):
        """Verifies a single weapon swing cannot hit the same mob multiple times across frames."""
        from src.entities.mob import create_mob_by_type
        mob = create_mob_by_type("zombie", 100, 100, self.af)
        mob.hp = 100
        mob.hurt_timer = 0.0
        self.game.combat.mobs = [mob]

        # Trigger swing
        self.player.x = 80
        self.player.y = 90
        self.player.aim_angle = 0.0
        self.player.trigger_attack(0.30)
        self.assertIn(mob, self.game.combat.mobs)

        # First hit check
        self.game.combat._check_weapon_hits(self.player, self.game.world)
        self.assertIn(mob, self.player.swing_hit_targets)
        hp_after_first = mob.hp
        self.assertLess(hp_after_first, 100)

        # Simulate next frame while still in same swing (even if mob hurt_timer was 0)
        mob.hurt_timer = 0.0
        self.game.combat._check_weapon_hits(self.player, self.game.world)
        self.assertEqual(mob.hp, hp_after_first, "Mob must not be multi-hit within the same swing!")


if __name__ == "__main__":
    unittest.main()
