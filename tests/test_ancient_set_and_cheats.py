"""
Potaria - Unit Tests for Ancient Equipment Sets, Time-of-Day Mob Balancing, and Developer Cheats
Verifies:
1. Ancient Equipment Set (+35% ATK, +30% DEF, +50 HP, +20% Crit) and radiant pulsing aura.
2. Thematic Sets: Titan, Magma, Cryo, Shadow, Spud, Cactus set bonuses and auras.
3. Time-of-day natural mob spawn pacing: Morning Peace (0 surface hostile mobs) vs Night.
4. Developer Debug Console / Cheats: /god, /heal, /speed, /time, /give, /ancient, /weapons, /spawn, /killall, /level, /clear.

Developer: Kurados | Pure Python 3.13 & pygame-ce
"""

import os
import unittest
import pygame

# Headless display setup for headless CI / testing environments
os.environ["SDL_VIDEODRIVER"] = "dummy"
pygame.init()
pygame.display.set_mode((1280, 720))

from main import PotariaGame
from src.rpg.equipment import (
    Equipment, EQUIPMENT_SETS, SLOT_HEAD, SLOT_CHEST, SLOT_LEGS, SLOT_WEAPON
)
from src.rpg.stats import PlayerStats
from src.entities.mob import GreenSlime, Zombie
from src.combat.combat_system import CombatManager


class TestAncientSetAndCheats(unittest.TestCase):
    def setUp(self):
        self.game = PotariaGame()
        self.game.paused = False
        self.game.player.attack_cooldown = 0.0
        self.game.combat.mobs.clear()
        self.game.combat.enemy_projectiles.clear()
        self.game.combat.boss = None
        # Clean inventory
        for i in range(len(self.game.inventory.slots)):
            self.game.inventory.slots[i] = None
        self.game.inventory.held_item = None

    def test_01_ancient_equipment_set_and_aura(self):
        """Verifies full Ancient Set grants +35% ATK, +30% DEF, +50 HP, +20% Crit and active aura 'ancient'."""
        stats = PlayerStats()
        stats.base_atk = 20
        stats.base_def = 10
        stats.base_hp = 100

        eq = Equipment()
        eq.slots[SLOT_HEAD] = "ancient_helmet"
        eq.slots[SLOT_CHEST] = "ancient_chestplate"
        eq.slots[SLOT_LEGS] = "ancient_greaves"

        # Check set detection
        set_key, set_info = eq.get_active_set()
        self.assertEqual(set_key, "ancient")
        self.assertTrue(eq.has_ancient_set())
        self.assertEqual(eq.get_active_aura(), "ancient")

        # Check stat recalculation
        eq.recalculate_stats(stats)
        
        # Piece stats + set bonus (+35% ATK, +30% DEF, +50 HP, +20% Crit)
        # Verify set bonus was factored into bonus stats
        self.assertGreater(stats.bonus_atk, 0)
        self.assertGreater(stats.bonus_def, 0)
        self.assertGreaterEqual(stats.bonus_max_hp, 50)
        self.assertGreaterEqual(stats.bonus_crit, 20.0)

    def test_02_thematic_armor_sets_and_auras(self):
        """Verifies other thematic sets (Titan, Magma, Cryo, Shadow, Spud, Cactus) activate proper auras."""
        eq = Equipment()
        sets_to_test = [
            ("titan", "titan_helmet", "titan_chestplate", "titan_greaves"),
            ("magma", "magma_helmet", "magma_chestplate", "magma_greaves"),
            ("cryo", "cryo_helmet", "cryo_chestplate", "cryo_greaves"),
            ("shadow", "shadow_helmet", "shadow_plate", "shadow_greaves"),
            ("spud", "potato_cap", "potato_tunic", "potato_pants"),
            ("cactus", "cactus_helmet", "cactus_chestplate", "cactus_greaves"),
        ]
        for key, h, c, l in sets_to_test:
            eq.slots[SLOT_HEAD] = h
            eq.slots[SLOT_CHEST] = c
            eq.slots[SLOT_LEGS] = l
            active_key, active_info = eq.get_active_set()
            self.assertEqual(active_key, key, f"Set {key} should be active")
            self.assertEqual(eq.get_active_aura(), key, f"Aura {key} should match set")

    def test_03_time_of_day_morning_peace(self):
        """Verifies that in morning time (< 0.22) on the surface, 0 aggressive monsters spawn."""
        combat = self.game.combat
        combat.mobs.clear()
        
        # Position player on surface
        self.game.player.x = 400.0
        self.game.player.y = 200.0  # Above surface level

        # Natural mob spawning at morning (time_of_day = 0.10)
        combat.mob_spawn_timer = 20.0  # Force spawn trigger
        combat._spawn_natural_mob(self.game.world, self.game.player, is_night=False, time_of_day=0.10)

        # 0 hostile mobs should be spawned during morning peace on surface
        self.assertEqual(len(combat.mobs), 0, "Morning peace must prevent surface monster spawns!")

    def test_04_cheat_god_mode_and_heal(self):
        """Verifies /god and /heal console commands."""
        self.game.player.health = 10
        if hasattr(self.game.player, "stats"):
            self.game.player.stats.hp = 10
            self.game.player.stats.mp = 5

        # Execute /heal
        self.game.execute_cheat("/heal")
        self.assertEqual(self.game.player.health, self.game.player.max_health)
        if hasattr(self.game.player, "stats"):
            self.assertEqual(self.game.player.stats.hp, self.game.player.stats.max_hp)
            self.assertEqual(self.game.player.stats.mp, self.game.player.stats.max_mp)

        # Execute /god (toggle ON)
        self.assertFalse(getattr(self.game, "god_mode", False))
        self.game.execute_cheat("/god")
        self.assertTrue(self.game.god_mode)

        # In god mode, update loop restores health and mana
        self.game.player.health = 5
        self.game.update_gameplay(0.016)
        self.assertEqual(self.game.player.health, self.game.player.max_health)

        # Execute /god (toggle OFF)
        self.game.execute_cheat("/god")
        self.assertFalse(self.game.god_mode)

    def test_05_cheat_speed_and_time(self):
        """Verifies /speed and /time console commands."""
        # /speed 3.5
        self.game.execute_cheat("/speed 3.5")
        self.assertEqual(self.game.speed_multiplier, 3.5)
        self.assertEqual(self.game.player.speed_multiplier, 3.5)

        # /time night
        self.game.execute_cheat("/time night")
        dur = self.game.sky.cycle_duration
        self.assertAlmostEqual(self.game.sky.time, dur * 0.75, delta=1.0)

        # /time morning
        self.game.execute_cheat("/time morning")
        self.assertAlmostEqual(self.game.sky.time, dur * 0.10, delta=1.0)

    def test_06_cheat_give_and_clear(self):
        """Verifies /give and /clear console commands."""
        self.assertEqual(self.game.inventory.count_item("flame_arrow"), 0)
        self.game.execute_cheat("/give flame_arrow 30")
        self.assertEqual(self.game.inventory.count_item("flame_arrow"), 30)

        # /clear empties inventory
        self.game.execute_cheat("/clear")
        self.assertEqual(self.game.inventory.count_item("flame_arrow"), 0)

    def test_07_cheat_ancient_and_weapons(self):
        """Verifies /ancient equips ancient set & weapons, and /weapons fills arsenal."""
        self.game.execute_cheat("/ancient")
        eq = self.game.player.equipment
        self.assertEqual(eq.slots[SLOT_HEAD], "ancient_helmet")
        self.assertEqual(eq.slots[SLOT_CHEST], "ancient_chestplate")
        self.assertEqual(eq.slots[SLOT_LEGS], "ancient_greaves")
        self.assertEqual(eq.get_active_aura(), "ancient")
        self.assertGreater(self.game.inventory.count_item("astral_arrow"), 0)
        self.assertGreater(self.game.inventory.count_item("eternal_catalyst"), 0)

        # /weapons provides comprehensive arsenal
        self.game.execute_cheat("/weapons")
        self.assertGreater(self.game.inventory.count_item("fire_staff"), 0)
        self.assertGreater(self.game.inventory.count_item("ancient_forgotten_rod"), 0)
        self.assertGreater(self.game.inventory.count_item("void_scepter"), 0)

    def test_08_cheat_spawn_and_killall(self):
        """Verifies /spawn and /killall commands."""
        self.assertEqual(len(self.game.combat.mobs), 0)
        self.game.execute_cheat("/spawn slime 3")
        self.assertEqual(len(self.game.combat.mobs), 3)

        self.game.execute_cheat("/killall")
        self.assertEqual(len(self.game.combat.mobs), 0)

        # Spawn mini-boss
        self.game.execute_cheat("/spawn malus")
        self.assertIsNotNone(self.game.combat.boss)
        self.assertEqual(self.game.combat.boss.name, "Lord Malus - The Blight-Bringer")

        # Spawn grand boss
        self.game.execute_cheat("/spawn sol_rho")
        self.assertIsNotNone(self.game.combat.boss)
        self.assertIn("Sol-Rho", self.game.combat.boss.name)

    def test_09_cheat_level(self):
        """Verifies /level increases player level and stats."""
        start_level = self.game.player.stats.level
        self.game.execute_cheat("/level 3")
        self.assertEqual(self.game.player.stats.level, start_level + 3)

    def test_10_direct_item_cheat_invincible_and_allskills(self):
        """Verifies direct item ID typing (e.g. /composite_bow 2), /invincible, and /allskills."""
        # Direct item typing cheat
        self.assertEqual(self.game.inventory.count_item("composite_bow"), 0)
        self.game.execute_cheat("/composite_bow 2")
        self.assertEqual(self.game.inventory.count_item("composite_bow"), 2)

        # /invincible alias
        self.assertFalse(getattr(self.game, "god_mode", False))
        self.game.execute_cheat("/invincible")
        self.assertTrue(self.game.god_mode)
        self.game.execute_cheat("/invincible")
        self.assertFalse(self.game.god_mode)

        # /allskills maximizes all skills
        self.game.execute_cheat("/allskills")
        for s_id in self.game.player.skills.all_skills:
            self.assertIn(s_id, self.game.player.skills.learned_skills)
            self.assertEqual(self.game.player.skills.skill_levels[s_id], 5)

    def test_11_ancient_pickup_unlocks_achievement(self):
        """Verifies picking up an Ancient item unlocks the 'rarity_ancient' achievement."""
        from src.entities.dropped_item import DroppedItem
        # Ensure achievement is locked initially
        self.game.achievement_manager.unlocked_ids.discard("rarity_ancient")
        
        # Simulate dropping an ancient item and marking as picked up
        drop = DroppedItem("ancient_sword", 1, self.game.player.center_x, self.game.player.center_y, self.game.asset_factory)
        drop.picked_up = True
        self.game.combat.dropped_items = [drop]
        
        # Run update loop to process item collection
        self.game.update_gameplay(0.016)
        
        # Verify rarity_ancient is now unlocked
        self.assertIn("rarity_ancient", self.game.achievement_manager.unlocked_ids)


if __name__ == "__main__":
    unittest.main()
