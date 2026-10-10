"""
Potaria - Unit and Integration Tests:
1. Bed Sleeping Restrictions (Night-only, 6-block hostile monster safety check, feedback messages)
2. Wild Mini-Boss Surface Night Suppression (Mini-bosses strictly subterranean/dungeons)
3. Nightly Elite Enemy ("Champion of the Night") (1.4x scale, boosted stats, special skills, 1/night cycle)
4. Subterranean Mini-Boss & Grand Boss Stat Buffs (HP, damage, defense mitigation, cadence)
Developer: Kurados | Pure Python + pygame-ce (100% offline)
"""

import os
import sys
import math
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"

import pygame
from main import PotariaGame
from src.constants import (
    SCALED_TILE, TILE_BED, TILE_AIR, TILE_DIRT,
    BIOME_FOREST, BIOME_DESERT, BIOME_SNOW, BIOME_CORRUPTION, BIOME_DUNGEON
)
from src.assets.asset_factory import AssetFactory
from src.audio.sound_effects import SoundManager
from src.entities.mob import (
    Zombie, GreenSlime, NightEliteMob, MOB_TYPE_REGISTRY, create_mob_by_type
)
from src.entities.boss import (
    LordMalus, IgnisColossus, CryoSpud, NecroTuber, GrandBossSolRho
)


class TestNightSleepEliteAndBossBuffs(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pygame.init()
        cls.asset_factory = AssetFactory()
        cls.sound_manager = SoundManager()

    def setUp(self):
        self.game = PotariaGame()
        self.game.combat.mobs.clear()
        self.game.combat.boss = None
        self.game.combat.boss_defeated = False
        self.game.combat.grand_boss_defeated = False
        self.game.combat.dropped_items.clear()
        self.game.combat.damage_numbers.clear()

    # =========================================================================
    # 1. BED SLEEPING RESTRICTIONS
    # =========================================================================
    def test_bed_sleep_rejected_during_daytime(self):
        """Right-clicking bed during daytime rejects sleep and displays feedback."""
        tx, ty = 20, 30
        self.game.world.set_tile(tx, ty, TILE_BED)
        tile_wx = tx * SCALED_TILE
        tile_wy = ty * SCALED_TILE

        self.game.player.x = tile_wx
        self.game.player.y = tile_wy - SCALED_TILE

        # Set time to daytime (noon, 12:00 PM)
        self.game.sky.time = 0.25 * self.game.sky.cycle_duration
        self.assertFalse(self.game.sky.is_night)

        screen_x, screen_y = self.game.camera.world_to_screen(tile_wx + 16, tile_wy + 16)
        self.game.handle_right_click(screen_x, screen_y)

        # Player must NOT be resting, spawn point should still be updated
        self.assertFalse(self.game.player.is_resting)
        self.assertEqual(self.game.player.spawn_point, (tile_wx, tile_wy - SCALED_TILE))
        self.assertEqual(self.game.inventory.last_learned_message, "You can only sleep at night")

    def test_bed_sleep_rejected_when_hostile_monster_within_6_blocks(self):
        """Right-clicking bed at night with a hostile monster within 6 blocks rejects sleep."""
        tx, ty = 20, 30
        self.game.world.set_tile(tx, ty, TILE_BED)
        tile_wx = tx * SCALED_TILE
        tile_wy = ty * SCALED_TILE

        self.game.player.x = tile_wx
        self.game.player.y = tile_wy - SCALED_TILE

        # Set time to midnight (nighttime)
        self.game.sky.time = 0.75 * self.game.sky.cycle_duration
        self.assertTrue(self.game.sky.is_night)

        # Spawn a hostile zombie 4 blocks away (within 6-block radius: 4 * 32 = 128px)
        zombie = Zombie(tile_wx + 4 * SCALED_TILE, tile_wy, self.game.asset_factory)
        self.game.combat.spawn_mob(zombie)

        screen_x, screen_y = self.game.camera.world_to_screen(tile_wx + 16, tile_wy + 16)
        self.game.handle_right_click(screen_x, screen_y)

        self.assertFalse(self.game.player.is_resting)
        self.assertEqual(
            self.game.inventory.last_learned_message,
            "You cannot sleep now, monsters are nearby within 6 blocks!"
        )

    def test_bed_sleep_allowed_at_night_when_monsters_outside_6_blocks(self):
        """Right-clicking bed at night when monsters are farther than 6 blocks succeeds."""
        tx, ty = 20, 30
        self.game.world.set_tile(tx, ty, TILE_BED)
        tile_wx = tx * SCALED_TILE
        tile_wy = ty * SCALED_TILE

        self.game.player.x = tile_wx
        self.game.player.y = tile_wy - SCALED_TILE

        # Set time to midnight
        self.game.sky.time = 0.75 * self.game.sky.cycle_duration
        self.assertTrue(self.game.sky.is_night)

        # Spawn a hostile zombie 8 blocks away (outside 6-block radius: 8 * 32 = 256px > 192px)
        zombie = Zombie(tile_wx + 8 * SCALED_TILE, tile_wy, self.game.asset_factory)
        self.game.combat.spawn_mob(zombie)

        screen_x, screen_y = self.game.camera.world_to_screen(tile_wx + 16, tile_wy + 16)
        self.game.handle_right_click(screen_x, screen_y)

        # Player must successfully enter resting state in bed
        self.assertTrue(self.game.player.is_resting)
        self.assertEqual(self.game.player.resting_bed_pos, (tx, ty))
        self.assertIn("Resting in bed", self.game.inventory.last_learned_message)

        # Right-clicking again wakes up
        self.game.handle_right_click(screen_x, screen_y)
        self.assertFalse(self.game.player.is_resting)
        self.assertIn("Woke up from bed", self.game.inventory.last_learned_message)

    def test_bed_sleep_morning_wakeup_restores_hp(self):
        """Sleeping through the night until daybreak wakes the player up refreshed with full HP."""
        tx, ty = 20, 30
        self.game.world.set_tile(tx, ty, TILE_BED)
        tile_wx = tx * SCALED_TILE
        tile_wy = ty * SCALED_TILE

        self.game.player.x = tile_wx
        self.game.player.y = tile_wy - SCALED_TILE
        self.game.player.health = 40
        self.game.player.stats.hp = 40

        self.game.sky.time = 0.75 * self.game.sky.cycle_duration
        screen_x, screen_y = self.game.camera.world_to_screen(tile_wx + 16, tile_wy + 16)
        self.game.handle_right_click(screen_x, screen_y)
        self.assertTrue(self.game.player.is_resting)

        # Advance sky to morning (daybreak 6:00 AM)
        self.game.sky.time = 0.0
        self.assertFalse(self.game.sky.is_night)

        # Call gameplay update to process morning transition
        self.game.update_gameplay(0.016)

        # Player automatically wakes up and is restored to max health
        self.assertFalse(self.game.player.is_resting)
        self.assertEqual(self.game.player.health, self.game.player.max_health)
        self.assertIn("Morning has broken", self.game.inventory.last_learned_message)

    # =========================================================================
    # 2. SURFACE NIGHT MINI-BOSS SUPPRESSION
    # =========================================================================
    def test_no_wild_mini_bosses_spawn_on_surface_at_night(self):
        """Verifies roaming mini-bosses NEVER spawn in overworld surface biomes at night."""
        self.game.sky.time = 0.75 * self.game.sky.cycle_duration
        self.assertTrue(self.game.sky.is_night)

        # Simulate 100 mob spawn attempts across surface biomes
        for _ in range(100):
            self.game.combat.boss = None
            self.game.combat._spawn_natural_mob(self.game.world, self.game.player, is_night=True, time_of_day=0.75)
            self.assertIsNone(self.game.combat.boss, "Wild mini-bosses must never spawn randomly in the overworld at night!")

    def test_subterranean_dungeon_mini_boss_can_awaken(self):
        """Mini-bosses can awaken in underground dungeons/caverns."""
        dung_x, dung_y = 100, 215 * SCALED_TILE
        self.game.combat.spawn_boss(dung_x, dung_y, boss_cls="lord_malus")
        self.assertIsNotNone(self.game.combat.boss)
        self.assertEqual(self.game.combat.boss.boss_type, "lord_malus")
        self.assertTrue(self.game.combat.boss.is_mini_boss)

    # =========================================================================
    # 3. NIGHTLY ELITE MOB ("CHAMPION OF THE NIGHT")
    # =========================================================================
    def test_nightly_elite_mob_spawning_and_stats(self):
        """Verifies exactly one Champion of the Night spawns per night with boosted stats and scaled size."""
        self.game.combat.mobs.clear()
        self.game.combat.nightly_elite_spawned = False
        self.game.player.y = 50 * SCALED_TILE  # Surface level

        # Spawn nightly elite
        self.game.combat._spawn_nightly_elite(self.game.world, self.game.player)
        self.assertTrue(self.game.combat.nightly_elite_spawned)
        self.assertEqual(len(self.game.combat.mobs), 1)

        elite = self.game.combat.mobs[0]
        self.assertIsInstance(elite, NightEliteMob)
        self.assertTrue(getattr(elite, "is_night_elite", False))
        self.assertIn("Champion of the Night", elite.name)

        # Scaled size check (1.4x scale)
        self.assertGreaterEqual(elite.width, int(28 * 1.3))
        self.assertGreaterEqual(elite.height, int(22 * 1.3))

        # Boosted stats check (tuned between normal mobs 30 HP and bosses 850+ HP)
        self.assertGreaterEqual(elite.max_hp, 150)
        self.assertLess(elite.max_hp, 400, "Elite stats must not rival actual bosses!")
        self.assertGreaterEqual(elite.damage, 19)
        self.assertGreaterEqual(elite.defense, 5)

        # Attempting second spawn in the same night cycle is rejected
        self.game.combat._spawn_nightly_elite(self.game.world, self.game.player)
        self.assertEqual(len(self.game.combat.mobs), 1, "Only one Nightly Elite may spawn per night cycle!")

        # Day transition resets nightly elite tracker
        self.game.combat.update(0.016, self.game.world, self.game.player, is_night=False, time_of_day=0.25)
        self.assertFalse(self.game.combat.nightly_elite_spawned, "Tracker must reset when daytime arrives")

    def test_nightly_elite_mob_skills(self):
        """Verifies Nightly Elite can execute special abilities (Shadow Bolt & Leap Slam)."""
        elite = NightEliteMob(200, 200, self.asset_factory, archetype="zombie")
        elite.skill_cooldown = 0.0
        elite.on_ground = True

        # When player is within 200px: Leap Slam executes
        dummy_player = self.game.player
        dummy_player.x = 250
        dummy_player.y = 200

        elite.update(0.016, self.game.world, dummy_player)
        self.assertTrue(elite.leap_slam_active, "Grounded close-range elite should trigger Leap Slam!")
        self.assertLess(elite.vy, 0, "Leap Slam should impart upward impulse")

        # When distant: Shadow Bolt void projectile is queued into pending_projectiles
        elite_ranged = NightEliteMob(100, 200, self.asset_factory, archetype="skeleton")
        elite_ranged.skill_cooldown = 0.0
        elite_ranged.on_ground = False  # in air, so doesn't trigger grounded leap
        dummy_player.x = 300
        dummy_player.y = 200

        elite_ranged.update(0.016, self.game.world, dummy_player)
        self.assertGreaterEqual(len(elite_ranged.pending_projectiles), 1, "Medium range elite should cast Shadow Bolt!")
        bolt = elite_ranged.pending_projectiles[0]
        self.assertEqual(bolt.color, (175, 45, 235))

    def test_night_elite_registry_factory(self):
        """Verifies NightEliteMob is registered in MOB_TYPE_REGISTRY for multiplayer sync."""
        self.assertIn("night_elite", MOB_TYPE_REGISTRY)
        self.assertIn("night_champion", MOB_TYPE_REGISTRY)
        mob = create_mob_by_type("night_elite", 300, 300, self.asset_factory)
        self.assertIsInstance(mob, NightEliteMob)
        self.assertTrue(mob.is_night_elite)

    # =========================================================================
    # 4. MINI-BOSS & GRAND BOSS STAT BUFFS
    # =========================================================================
    def test_mini_boss_boosted_stats(self):
        """Verifies subterranean Mini-Bosses received significant stat boosts."""
        malus = LordMalus(0, 0, self.asset_factory, self.sound_manager)
        self.assertGreaterEqual(malus.max_hp, 900)
        self.assertGreaterEqual(malus.damage, 38)
        self.assertGreaterEqual(malus.defense, 16)

        ignis = IgnisColossus(0, 0, self.asset_factory, self.sound_manager)
        self.assertGreaterEqual(ignis.max_hp, 1100)
        self.assertGreaterEqual(ignis.damage, 44)
        self.assertGreaterEqual(ignis.defense, 22)

        cryo = CryoSpud(0, 0, self.asset_factory, self.sound_manager)
        self.assertGreaterEqual(cryo.max_hp, 950)
        self.assertGreaterEqual(cryo.damage, 36)
        self.assertGreaterEqual(cryo.defense, 18)

        necro = NecroTuber(0, 0, self.asset_factory, self.sound_manager)
        self.assertGreaterEqual(necro.max_hp, 880)
        self.assertGreaterEqual(necro.damage, 40)
        self.assertGreaterEqual(necro.defense, 15)

    def test_mini_boss_defense_mitigation(self):
        """Verifies Mini-Boss mitigates incoming player damage with defense stat and innate boss armor."""
        malus = LordMalus(0, 0, self.asset_factory, self.sound_manager)
        initial_hp = malus.hp
        # Defense is 32. 50 dmg - 32 = 18. Innate 25% boss armor: int(18 * 0.75) = 13
        malus.take_damage(50)
        self.assertEqual(malus.hp, initial_hp - 13)

    def test_grand_boss_sol_rho_boosted_stats_and_defense(self):
        """Verifies Grand Boss Sol-Rho has boosted damage and defense in both phases."""
        sol = GrandBossSolRho(0, 0, self.asset_factory, self.sound_manager, party_size=1)
        self.assertEqual(sol.phase, 1)
        self.assertEqual(sol.hp, 14000)
        self.assertGreaterEqual(sol.damage, 50)
        self.assertGreaterEqual(sol.defense, 25)

        # Phase 1 defense mitigation: defense is 48 -> (60 - 48) * 0.75 = 9
        initial_hp = sol.hp
        sol.take_damage(60)
        self.assertEqual(sol.hp, initial_hp - 9)

        # Transition to Phase 2: Void Incarnate
        sol.hp = 0
        sol.is_transforming = True
        sol.transform_timer = 0.0
        sol.update(0.1, self.game.world, self.game.player, self.game.particle_system, self.game.camera)

        self.assertEqual(sol.phase, 2)
        self.assertEqual(sol.hp, 20000)
        self.assertGreaterEqual(sol.damage, 70)
        self.assertGreaterEqual(sol.defense, 35)

        # Phase 2 defense mitigation: defense is 64 -> (80 - 64) * 0.75 = 12
        p2_hp = sol.hp
        sol.take_damage(80)
        self.assertEqual(sol.hp, p2_hp - 12)


    def test_sleeping_interrupted_when_monster_wanders_within_6_blocks(self):
        """Sleeping in bed is immediately interrupted if a monster wanders within 6 blocks."""
        tx, ty = 20, 30
        self.game.world.set_tile(tx, ty, TILE_BED)
        tile_wx = tx * SCALED_TILE
        tile_wy = ty * SCALED_TILE

        self.game.player.x = tile_wx
        self.game.player.y = tile_wy - SCALED_TILE

        self.game.sky.time = 0.75 * self.game.sky.cycle_duration
        screen_x, screen_y = self.game.camera.world_to_screen(tile_wx + 16, tile_wy + 16)
        self.game.handle_right_click(screen_x, screen_y)
        self.assertTrue(self.game.player.is_resting)

        # A monster appears within 4 blocks (128px <= 192px)
        zombie = Zombie(tile_wx + 4 * SCALED_TILE, tile_wy, self.game.asset_factory)
        self.game.combat.spawn_mob(zombie)

        # Call gameplay update
        self.game.update_gameplay(0.016)

        # Player is immediately awakened
        self.assertFalse(self.game.player.is_resting)
        self.assertIn("Monsters are nearby within 6 blocks", self.game.inventory.last_learned_message)

    def test_night_elite_solid_ground_collision_no_void_clip(self):
        """Verifies falling NightEliteMob lands safely on solid ground without clipping into void."""
        ground_tx, ground_ty = 10, 40
        for tx in range(ground_tx - 3, ground_tx + 4):
            self.game.world.set_tile(tx, ground_ty, TILE_DIRT)
            for dy in range(1, 10):
                self.game.world.set_tile(tx, ground_ty - dy, TILE_AIR)
        tile_top_y = ground_ty * SCALED_TILE

        elite = NightEliteMob(ground_tx * SCALED_TILE, tile_top_y - 80, self.asset_factory, archetype="zombie")
        self.game.player.x = elite.x
        elite.vy = 12.0  # Falling at terminal velocity
        elite.on_ground = False

        # Run multiple physics frames until landing
        for _ in range(15):
            elite.update(0.016, self.game.world, self.game.player)
            if elite.on_ground:
                break

        self.assertTrue(elite.on_ground, "Elite mob must land on top of solid dirt block!")
        self.assertEqual(elite.vy, 0.0)
        self.assertAlmostEqual(elite.y + elite.height, tile_top_y, delta=1.0)

    def test_night_elite_dedicated_skills_per_archetype(self):
        """Verifies each elite receives and executes its dedicated special skill."""
        # Demon Eye archetype -> Frenzy Charge
        eye = NightEliteMob(100, 100, self.asset_factory, archetype="demon_eye")
        self.assertEqual(eye.skill, "frenzy_charge")
        eye.skill_cooldown = 0.0
        self.game.player.x, self.game.player.y = 200, 100
        eye.update(0.016, self.game.world, self.game.player)
        self.assertGreater(eye.frenzy_timer, 0.0, "Demon Eye elite should activate Frenzy Charge!")

        # Shadow Crawler archetype -> Ground Fissure
        crawler = NightEliteMob(100, 100, self.asset_factory, archetype="shadow_crawler")
        self.assertEqual(crawler.skill, "ground_fissure")
        crawler.skill_cooldown = 0.0
        self.game.player.x, self.game.player.y = 250, 100
        crawler.update(0.016, self.game.world, self.game.player)
        self.assertGreaterEqual(len(crawler.pending_projectiles), 1)
        fissure_proj = crawler.pending_projectiles[0]
        self.assertEqual(fissure_proj.color, (200, 60, 240))

    def test_night_elite_multiplayer_archetype_sync_preservation(self):
        """Verifies NightEliteMob preserves its exact archetype when synchronized across multiplayer."""
        elite = NightEliteMob(150, 150, self.asset_factory, archetype="demon_eye")
        self.assertEqual(elite.mob_type, "night_elite_demon_eye")

        # Spawn mob to assign unique mob_id
        self.game.combat.mobs.clear()
        self.game.combat.spawn_mob(elite)
        sync_data = self.game.combat.get_mobs_sync_data()
        self.assertEqual(len(sync_data), 1)
        self.assertEqual(sync_data[0]["mob_type"], "night_elite_demon_eye")

        # Client reconciles without desync
        from src.combat.combat_system import CombatManager
        client_combat = CombatManager(self.asset_factory, self.sound_manager, self.game.particle_system, self.game.camera)
        client_combat.is_client = True
        client_combat.sync_from_host(sync_data)

        self.assertEqual(len(client_combat.mobs), 1)
        client_mob = client_combat.mobs[0]
        self.assertIsInstance(client_mob, NightEliteMob)
        self.assertEqual(client_mob.archetype, "demon_eye")

    def test_nightly_elite_daytime_reset_during_active_boss(self):
        """Daybreak resets nightly elite tracker even if a boss battle is currently ongoing."""
        self.game.combat.nightly_elite_spawned = True
        self.game.combat.boss = LordMalus(0, 0, self.asset_factory, self.sound_manager)

        # Update combat during daytime (is_night=False)
        self.game.combat.update(0.016, self.game.world, self.game.player, is_night=False, time_of_day=0.25)
        self.assertFalse(self.game.combat.nightly_elite_spawned, "Tracker must reset at daytime regardless of boss")

    def test_nightly_elite_no_duplicate_when_one_alive(self):
        """Refuses to spawn a second nightly elite while one is already alive in the world."""
        self.game.combat.mobs.clear()
        self.game.combat.nightly_elite_spawned = False
        self.game.player.y = 50 * SCALED_TILE

        # Spawn first
        self.game.combat._spawn_nightly_elite(self.game.world, self.game.player)
        self.assertEqual(len(self.game.combat.mobs), 1)

        # Force reset flag (simulating next night with previous elite still alive)
        self.game.combat.nightly_elite_spawned = False
        self.game.combat._spawn_nightly_elite(self.game.world, self.game.player)
        self.assertEqual(len(self.game.combat.mobs), 1, "Duplicate elite must not spawn while one is already roaming!")


if __name__ == "__main__":
    unittest.main()
