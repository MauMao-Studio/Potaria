"""
Potaria - Unit Tests for Long-Range Weapons & Projectile Behaviors
Verifies Catalysts, Staves, Rods, Scepters, Bow ammo variants, ballistic gravity, and 560px range limits.
Developer: Kurados | Pure Python 3.13 & pygame-ce
"""

import os
import math
import unittest
import pygame

# Headless display setup for headless CI / testing environments
os.environ["SDL_VIDEODRIVER"] = "dummy"
pygame.init()
pygame.display.set_mode((1280, 720))

from main import PotariaGame
from src.ui.inventory import ItemStack
from src.entities.projectile import (
    ArrowProjectile, CatalystStarProjectile, StaffBoltProjectile,
    RodJavelinProjectile, ScepterPulseProjectile
)
from src.entities.mob import GreenSlime, Zombie


class TestLongRangeWeapons(unittest.TestCase):
    def setUp(self):
        self.game = PotariaGame()
        self.game.paused = False
        self.game.player.attack_cooldown = 0.0
        self.game.player.fireballs.clear()
        self.game.combat.projectiles.clear()
        self.game.combat.mobs.clear()
        # Clear inventory for clean test state
        for i in range(len(self.game.inventory.slots)):
            self.game.inventory.slots[i] = None
        self.game.inventory.held_item = None

    def test_01_catalyst_fires_homing_star(self):
        """Verifies catalysts fire CatalystStarProjectile with 560px max range and homing steering."""
        self.game.inventory.slots[0] = ItemStack("eternal_catalyst", 1)
        self.game.inventory.selected_slot = 0
        self.game.player.attack_cooldown = 0.0

        # Fire towards coordinate (300, 300)
        res = self.game.handle_primary_action(300, 300)
        self.assertTrue(res, "Catalyst firing must succeed!")
        self.assertEqual(len(self.game.player.fireballs), 1, "Exactly 1 catalyst projectile must spawn in fireballs!")
        
        proj = self.game.player.fireballs[0]
        self.assertIsInstance(proj, CatalystStarProjectile, "Spawned projectile must be a CatalystStarProjectile!")
        self.assertAlmostEqual(proj.max_distance, 560.0, places=1, msg="Catalyst max distance must be 560px!")
        
        # Test homing towards mob
        mob = GreenSlime(proj.x + 80, proj.y + 40, self.game.asset_factory)
        self.game.combat.mobs.append(mob)
        initial_vy = proj.vy
        
        # Update projectile with mob in range
        proj.update(0.05, self.game.world, self.game.particle_system, mobs=self.game.combat.mobs)
        # Velocity should adjust towards mob Y
        self.assertNotEqual(proj.vy, initial_vy, "Homing star must curve towards target mob!")

    def test_02_staff_fires_elemental_bolt(self):
        """Verifies staves fire elemental StaffBoltProjectile with 560px max range."""
        self.game.inventory.slots[0] = ItemStack("frost_staff", 1)
        self.game.inventory.selected_slot = 0
        self.game.player.attack_cooldown = 0.0

        res = self.game.handle_primary_action(300, 300)
        self.assertTrue(res, "Staff firing must succeed!")
        self.assertEqual(len(self.game.player.fireballs), 1)
        
        proj = self.game.player.fireballs[0]
        self.assertIsInstance(proj, StaffBoltProjectile, "Must spawn StaffBoltProjectile!")
        self.assertEqual(proj.element, "frost", "Frost staff must fire frost element bolt!")
        self.assertAlmostEqual(proj.max_distance, 560.0, places=1)

    def test_03_rod_fires_piercing_javelin(self):
        """Verifies rods fire high-velocity piercing RodJavelinProjectile."""
        self.game.inventory.slots[0] = ItemStack("ancient_forgotten_rod", 1)
        self.game.inventory.selected_slot = 0
        self.game.player.attack_cooldown = 0.0

        res = self.game.handle_primary_action(300, 300)
        self.assertTrue(res, "Rod firing must succeed!")
        self.assertEqual(len(self.game.player.fireballs), 1)

        proj = self.game.player.fireballs[0]
        self.assertIsInstance(proj, RodJavelinProjectile, "Must spawn RodJavelinProjectile!")
        self.assertGreaterEqual(proj.pierce_left, 2, "Rod javelin must pierce at least 2 targets!")
        self.assertAlmostEqual(proj.max_distance, 560.0, places=1)

    def test_04_scepter_fires_expanding_pulse(self):
        """Verifies scepters fire expanding ScepterPulseProjectile."""
        self.game.inventory.slots[0] = ItemStack("void_scepter", 1)
        self.game.inventory.selected_slot = 0
        self.game.player.attack_cooldown = 0.0

        res = self.game.handle_primary_action(300, 300)
        self.assertTrue(res, "Scepter firing must succeed!")
        self.assertEqual(len(self.game.player.fireballs), 1)

        proj = self.game.player.fireballs[0]
        self.assertIsInstance(proj, ScepterPulseProjectile, "Must spawn ScepterPulseProjectile!")
        self.assertAlmostEqual(proj.max_distance, 560.0, places=1)

    def test_05_bow_ammo_priority_and_consumption(self):
        """Verifies bows prioritize and consume astral_arrow > frostburn_arrow > flame_arrow > wooden_arrow."""
        self.game.inventory.slots[0] = ItemStack("wood_bow", 1)
        self.game.inventory.slots[1] = ItemStack("wooden_arrow", 10)
        self.game.inventory.slots[2] = ItemStack("flame_arrow", 5)
        self.game.inventory.slots[3] = ItemStack("astral_arrow", 2)
        self.game.inventory.selected_slot = 0
        self.game.player.attack_cooldown = 0.0

        # Shot 1: Should consume astral_arrow first!
        self.game.handle_primary_action(300, 300)
        self.assertEqual(self.game.inventory.count_item("astral_arrow"), 1)
        self.assertEqual(self.game.combat.projectiles[0].arrow_type, "astral_arrow")

        # Shot 2: Should consume last astral_arrow!
        self.game.player.attack_cooldown = 0.0
        self.game.handle_primary_action(300, 300)
        self.assertEqual(self.game.inventory.count_item("astral_arrow"), 0)

        # Shot 3: Next should consume flame_arrow!
        self.game.player.attack_cooldown = 0.0
        self.game.handle_primary_action(300, 300)
        self.assertEqual(self.game.inventory.count_item("flame_arrow"), 4)
        self.assertEqual(self.game.combat.projectiles[-1].arrow_type, "flame_arrow")

    def test_06_bow_out_of_ammo_fails(self):
        """Verifies non-relic bows cannot fire when out of arrows."""
        self.game.inventory.slots[0] = ItemStack("wood_bow", 1)
        self.game.inventory.selected_slot = 0
        self.game.player.attack_cooldown = 0.0

        res = self.game.handle_primary_action(300, 300)
        self.assertFalse(res, "Wood bow must not fire without arrows!")
        self.assertEqual(len(self.game.combat.projectiles), 0, "No projectile should spawn when out of ammo!")

    def test_07_arrow_ballistic_gravity_physics(self):
        """Verifies arrows experience downward gravitational curve using sub-pixel Vector2 physics."""
        arrow = ArrowProjectile(100.0, 100.0, angle_rad=0.0, speed=12.0, damage=15, arrow_type="wooden_arrow")
        initial_vy = arrow.vel.y
        self.assertEqual(initial_vy, 0.0)

        # Simulate 1 frame of physics update
        arrow.update(0.016, self.game.world, self.game.particle_system, self.game.sound_manager, self.game.player)
        self.assertGreater(arrow.vel.y, initial_vy, "Arrow vertical velocity must increase due to gravity!")
        self.assertGreater(arrow.pos.y, 100.0, "Arrow Y coordinate must drop downward!")

    def test_08_composite_bow_and_ancient_composite_bow(self):
        """Verifies composite bow fires arrows and ancient composite bow fires astral arrows even when quiver empty."""
        # 1. Normal composite bow fires physical arrows
        self.game.inventory.slots[0] = ItemStack("composite_bow", 1)
        self.game.inventory.slots[1] = ItemStack("wooden_arrow", 5)
        self.game.inventory.selected_slot = 0
        self.game.player.attack_cooldown = 0.0

        res = self.game.handle_primary_action(300, 300)
        self.assertTrue(res, "Composite bow must fire when ammo is available!")
        self.assertEqual(self.game.inventory.count_item("wooden_arrow"), 4)

        # 2. Ancient composite bow channels astral energy when out of physical arrows
        self.game.inventory.slots[0] = ItemStack("ancient_composite_bow", 1)
        self.game.inventory.slots[1] = None
        self.game.player.attack_cooldown = 0.0

        res_ancient = self.game.handle_primary_action(300, 300)
        self.assertTrue(res_ancient, "Ancient composite bow must fire astral arrows even when empty!")
        self.assertEqual(self.game.combat.projectiles[-1].arrow_type, "astral_arrow")


if __name__ == "__main__":
    unittest.main()
