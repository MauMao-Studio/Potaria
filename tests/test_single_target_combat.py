"""
Unit tests for Single-Target Combat System with Ancient Item Multi-Target Exceptions.
Verifies:
1. Non-ancient melee weapons damage at most 1 enemy per swing.
2. Ancient melee weapons can hit multiple enemies (cleave).
3. Non-ancient ranged projectiles damage at most 1 enemy.
4. Ancient piercing projectiles pierce through multiple enemies.
5. Non-ancient procs (shockwave/pulse/star) damage only a single target.
6. Ancient procs damage all enemies in their radius.
"""

import unittest
import os
import pygame

# Headless pygame setup
os.environ["SDL_VIDEODRIVER"] = "dummy"
pygame.init()
pygame.display.set_mode((800, 600))

from src.assets.asset_factory import AssetFactory
from src.audio.sound_effects import SoundManager
from src.entities.player import Player
from src.entities.mob import GreenSlime
from src.combat.combat_system import CombatManager
from src.entities.particle import ParticleSystem
from src.camera import Camera
from src.ui.inventory import ItemStack, ITEM_REGISTRY, Inventory
from src.rpg.equipment import SLOT_WEAPON
from src.entities.projectile import (
    ArrowProjectile, FreezingNeedleProjectile, SolarFlareShockwave,
    GravitationalPulseProjectile, CelestialStarProjectile, RodJavelinProjectile
)


class DummyWorld:
    def get_tile(self, tx, ty):
        return 0

    def is_solid(self, tx, ty):
        return False

    def get_solid_rects_in_bounds(self, rect):
        return []


class TestSingleTargetCombat(unittest.TestCase):
    def setUp(self):
        self.world = DummyWorld()
        self.factory = AssetFactory()
        self.sound = SoundManager()
        self.particles = ParticleSystem()
        self.camera = Camera(800, 600)
        self.combat = CombatManager(self.factory, self.sound, self.particles, self.camera)
        self.player = Player(200, 200, self.factory, self.sound)
        self.player.inventory = Inventory(self.factory)

    def test_01_non_ancient_melee_hits_only_one_enemy(self):
        """Non-ancient melee weapon damages only 1 enemy per swing even when multiple enemies are clustered."""
        # Equip non-ancient weapon (iron broadsword) in hotbar
        self.player.inventory.slots[0] = ItemStack("iron_broadsword", 1)
        self.player.inventory.selected_slot = 0

        m1 = GreenSlime(230, 200, self.factory)
        m2 = GreenSlime(235, 200, self.factory)
        m3 = GreenSlime(240, 200, self.factory)
        self.combat.mobs = [m1, m2, m3]

        self.player.center_x = 200
        self.player.center_y = 200
        self.player.aim_angle = 0.0  # Aim right directly at all 3 mobs
        self.player.trigger_attack(0.3)
        self.player.swing_progress = 0.2

        hp1_before, hp2_before, hp3_before = m1.hp, m2.hp, m3.hp

        # Perform weapon hit check
        self.combat._check_weapon_hits(self.player)

        damaged_count = sum([
            1 if m1.hp < hp1_before else 0,
            1 if m2.hp < hp2_before else 0,
            1 if m3.hp < hp3_before else 0,
        ])

        self.assertEqual(damaged_count, 1, f"Non-ancient weapon should damage exactly 1 enemy, but damaged {damaged_count}")
        self.assertEqual(len(self.player.swing_hit_targets), 1, "swing_hit_targets should contain exactly 1 mob")

    def test_02_ancient_melee_hits_multiple_enemies(self):
        """Ancient melee weapon damages all enemies in its hitbox (cleave)."""
        # Equip ancient weapon in hotbar
        self.player.inventory.slots[0] = ItemStack("ancient_sword", 1)
        self.player.inventory.selected_slot = 0

        m1 = GreenSlime(230, 200, self.factory)
        m2 = GreenSlime(235, 200, self.factory)
        m3 = GreenSlime(240, 200, self.factory)
        self.combat.mobs = [m1, m2, m3]

        self.player.center_x = 200
        self.player.center_y = 200
        self.player.aim_angle = 0.0
        self.player.trigger_attack(0.3)
        self.player.swing_progress = 0.2

        hp1_before, hp2_before, hp3_before = m1.hp, m2.hp, m3.hp

        self.combat._check_weapon_hits(self.player)

        self.assertLess(m1.hp, hp1_before, "Ancient weapon must damage Mob 1")
        self.assertLess(m2.hp, hp2_before, "Ancient weapon must cleave and damage Mob 2")
        self.assertLess(m3.hp, hp3_before, "Ancient weapon must cleave and damage Mob 3")
        self.assertEqual(len(self.player.swing_hit_targets), 3, "Ancient weapon should hit all 3 mobs in swing hitbox")

    def test_03_non_ancient_rod_javelin_stops_on_first_mob(self):
        """Non-ancient Rod Javelin does not pierce multiple enemies."""
        rod = RodJavelinProjectile(200, 200, 10.0, 0.0, damage=30)
        rod.is_ancient = False

        m1 = GreenSlime(205, 200, self.factory)
        m2 = GreenSlime(215, 200, self.factory)
        self.combat.mobs = [m1, m2]
        self.combat.projectiles = [rod]

        hp1_before, hp2_before = m1.hp, m2.hp

        # Update combat projectiles
        self.combat.update(0.016, self.world, self.player, is_night=False)

        self.assertLess(m1.hp, hp1_before, "Mob 1 must take damage from javelin")
        self.assertEqual(m2.hp, hp2_before, "Mob 2 must NOT take damage from non-ancient javelin")
        self.assertLessEqual(rod.life, 0, "Non-ancient javelin must expire immediately upon first enemy hit")

    def test_04_ancient_rod_javelin_pierces_multiple_mobs(self):
        """Ancient Rod Javelin pierces through multiple enemies."""
        rod = RodJavelinProjectile(200, 200, 10.0, 0.0, damage=30)
        rod.is_ancient = True

        m1 = GreenSlime(205, 200, self.factory)
        m2 = GreenSlime(215, 200, self.factory)
        self.combat.mobs = [m1, m2]
        self.combat.projectiles = [rod]

        hp1_before, hp2_before = m1.hp, m2.hp

        # Update combat projectiles
        self.combat.update(0.016, self.world, self.player, is_night=False)

        self.assertLess(m1.hp, hp1_before, "Mob 1 must take damage")
        self.assertLess(m2.hp, hp2_before, "Ancient javelin must pierce through and damage Mob 2")

    def test_05_non_ancient_shockwave_hits_only_one_enemy(self):
        """Non-ancient Solar Flare Shockwave damages only a single enemy."""
        shock = SolarFlareShockwave(200, 200, damage=35, max_radius=80.0)
        shock.is_ancient = False
        shock.life = 0.05  # Near end of life so radius expands to ~75px

        m1 = GreenSlime(210, 200, self.factory)
        m2 = GreenSlime(225, 200, self.factory)

        hp1_before, hp2_before = m1.hp, m2.hp
        shock.update(0.016, self.particles, self.sound, [m1, m2], None, self.player, combat=self.combat)

        damaged_count = (1 if m1.hp < hp1_before else 0) + (1 if m2.hp < hp2_before else 0)
        self.assertEqual(damaged_count, 1, f"Non-ancient shockwave should damage exactly 1 enemy, got {damaged_count}")
        self.assertLessEqual(shock.life, 0, "Non-ancient shockwave must dissipate after damaging single enemy")

    def test_06_ancient_shockwave_hits_all_enemies_in_radius(self):
        """Ancient Solar Flare Shockwave damages all enemies in radius."""
        shock = SolarFlareShockwave(200, 200, damage=35, max_radius=80.0)
        shock.is_ancient = True
        shock.life = 0.05  # Near end of life so radius expands to ~75px

        m1 = GreenSlime(210, 200, self.factory)
        m2 = GreenSlime(225, 200, self.factory)

        hp1_before, hp2_before = m1.hp, m2.hp
        shock.update(0.016, self.particles, self.sound, [m1, m2], None, self.player, combat=self.combat)

        self.assertLess(m1.hp, hp1_before, "Mob 1 must take damage from ancient shockwave")
        self.assertLess(m2.hp, hp2_before, "Mob 2 must take damage from ancient shockwave")

    def test_07_non_ancient_arrow_hits_only_one_enemy(self):
        """Non-ancient arrow damages at most 1 enemy and disappears."""
        arrow = ArrowProjectile(200, 200, angle_rad=0.0, speed=15.0, damage=25)
        arrow.is_ancient = False
        m1 = GreenSlime(205, 200, self.factory)
        m2 = GreenSlime(215, 200, self.factory)
        self.combat.mobs = [m1, m2]
        self.combat.projectiles = [arrow]

        hp1_before, hp2_before = m1.hp, m2.hp
        self.combat.update(0.016, self.world, self.player, is_night=False)

        self.assertLess(m1.hp, hp1_before, "Mob 1 must take damage from arrow")
        self.assertEqual(m2.hp, hp2_before, "Mob 2 must NOT take damage from non-ancient arrow")
        self.assertLessEqual(arrow.life, 0, "Non-ancient arrow must expire upon hitting first enemy")

    def test_08_ancient_arrow_pierces_multiple_enemies(self):
        """Ancient arrow pierces through multiple enemies."""
        arrow = ArrowProjectile(200, 200, angle_rad=0.0, speed=15.0, damage=25)
        arrow.is_ancient = True
        m1 = GreenSlime(205, 200, self.factory)
        m2 = GreenSlime(215, 200, self.factory)
        self.combat.mobs = [m1, m2]
        self.combat.projectiles = [arrow]

        hp1_before, hp2_before = m1.hp, m2.hp
        self.combat.update(0.016, self.world, self.player, is_night=False)

        self.assertLess(m1.hp, hp1_before, "Mob 1 must take damage from ancient arrow")
        self.assertLess(m2.hp, hp2_before, "Mob 2 must take damage from ancient arrow pierce")


if __name__ == "__main__":
    unittest.main()
