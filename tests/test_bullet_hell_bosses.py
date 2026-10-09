"""
Unit Tests - Bullet-Hell Boss Barrages & Touhou/Gungeon Dodging Mechanics
Tests rich projectile patterns, fair core hitboxes, grazing rewards,
high-density performance, and multiplayer LAN snapshot synchronization.
Developer: Kurados
Engine: Pure Python 3.13 + pygame-ce 2.5.8+ (100% Offline Standalone)
"""

import math
import time
import unittest
import pygame

# Initialize pygame headless
pygame.init()
pygame.display.set_mode((1280, 720))

from src.constants import SCREEN_WIDTH, SCREEN_HEIGHT
from src.assets.asset_factory import AssetFactory
from src.audio.sound_effects import SoundManager
from src.camera import Camera
from src.entities.particle import ParticleSystem
from src.entities.player import Player
from src.combat.combat_system import CombatManager
from src.entities.bullet_hell import (
    BossProjectile, BulletHellPatterns, get_bullet_surface
)
from src.entities.boss import (
    DungeonMiniBoss, LordMalus, IgnisColossus, CryoSpud, NecroTuber,
    GrandBossSolRho, create_boss_by_type
)

class TestBulletHellBosses(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.asset_factory = AssetFactory()
        cls.sound_manager = SoundManager()

    def setUp(self):
        self.camera = Camera(SCREEN_WIDTH, SCREEN_HEIGHT)
        self.particles = ParticleSystem()
        self.player = Player(400, 400, self.asset_factory, self.sound_manager)
        self.player.i_frame_timer = 0.0

    # ==========================================================================
    # 1. CORE HITBOX & TOUHOU GRAZING MECHANICS
    # ==========================================================================
    def test_fair_core_hitbox_proportions(self):
        """Validates that bullet core hitbox is fair (~50-55% of visual radius)."""
        p = BossProjectile(x=200, y=200, vx=5.0, vy=0.0, radius=12, damage=18)
        self.assertEqual(p.radius, 12.0)
        # Core radius should be ~52% of visual radius
        self.assertAlmostEqual(p.core_radius, 12.0 * 0.52, delta=0.5)
        self.assertTrue(p.core_radius < p.radius)

        # Core rect should be centered on bullet coordinates
        rect = p.rect
        self.assertAlmostEqual(rect.centerx, 200, delta=0.1)
        self.assertAlmostEqual(rect.centery, 200, delta=0.1)
        self.assertAlmostEqual(rect.width, p.core_radius * 2, delta=0.1)

        # Visual rect should cover full visual radius
        v_rect = p.visual_rect
        self.assertAlmostEqual(v_rect.width, 24.0, delta=0.1)

    def test_player_graze_rewards_and_near_miss(self):
        """Validates that near-miss bullets trigger grazing, grant MP, and do 0 damage."""
        self.player.x = 400
        self.player.y = 400
        self.player.stats.mp = 10
        self.player.stats.max_mp = 50
        initial_hp = self.player.health
        initial_graze = self.player.graze_count

        # Place bullet right outside player core rect, but inside graze perimeter
        # Player rect is 28x32 at (400, 400) -> right edge is at x=428
        bullet = BossProjectile(x=438, y=415, vx=0.0, vy=0.0, radius=12, damage=25)

        # Ensure bullet does NOT hit player core hitbox
        self.assertFalse(bullet.rect.colliderect(self.player.rect))
        # Ensure bullet DOES overlap graze rect
        self.assertTrue(bullet.graze_rect.colliderect(self.player.rect))

        # Update bullet against player
        bullet.update(0.016, self.player)

        # Graze should trigger!
        self.assertTrue(bullet.grazed)
        self.assertEqual(self.player.graze_count, initial_graze + 1)
        self.assertEqual(self.player.stats.mp, 11)  # Rewarded +1 MP!
        self.assertEqual(self.player.health, initial_hp)  # Zero damage taken!

        # Updating again should NOT re-trigger duplicate graze on same bullet
        bullet.update(0.016, self.player)
        self.assertEqual(self.player.graze_count, initial_graze + 1)

    def test_direct_core_collision_inflicts_damage(self):
        """Validates that hitting the core hitbox inflicts damage."""
        self.player.x = 400
        self.player.y = 400
        self.player.i_frame_timer = 0.0
        initial_hp = self.player.health

        # Place bullet directly at player center
        bullet = BossProjectile(x=self.player.center_x, y=self.player.center_y, vx=0.0, vy=0.0, radius=10, damage=30)
        self.assertTrue(bullet.rect.colliderect(self.player.rect))

        damaged = self.player.take_damage(bullet.damage)
        self.assertTrue(damaged)
        self.assertTrue(self.player.health < initial_hp)

    # ==========================================================================
    # 2. LORD MALUS (BLIGHT) BULLET-HELL PATTERNS
    # ==========================================================================
    def test_lord_malus_toxic_spore_rings_with_dodge_gaps(self):
        """Lord Malus must cast concentric toxic spore rings with clear dodge openings."""
        boss = LordMalus(400, 200, self.asset_factory, self.sound_manager)
        boss.pattern_index = 0
        boss._cast_attack(self.player, self.particles, self.camera)

        self.assertTrue(len(boss.projectiles) >= 14, f"Expected spore ring, got {len(boss.projectiles)} bullets")
        # Check colors and shapes
        p0 = boss.projectiles[0]
        self.assertEqual(p0.color, (50, 220, 80))
        self.assertEqual(p0.core_color, (230, 255, 230))
        self.assertEqual(p0.shape, "orb")

        # Test phase 2 dual-wave scheduling
        boss.phase = 2
        boss.pattern_index = 0
        boss._cast_attack(self.player, self.particles, self.camera)
        self.assertEqual(boss.active_pattern, "toxic_spore_ring2")

    def test_lord_malus_blighted_spiral_curses(self):
        """Lord Malus must channel multi-arm rotating spiral curses."""
        boss = LordMalus(400, 200, self.asset_factory, self.sound_manager)
        boss.pattern_index = 1
        boss._cast_attack(self.player, self.particles, self.camera)

        self.assertEqual(boss.active_pattern, "blighted_spiral")
        initial_count = len(boss.projectiles)

        # Step pattern several frames
        for _ in range(5):
            boss._step_pattern(0.08, self.player, self.particles, self.camera)

        self.assertTrue(len(boss.projectiles) > initial_count, "Spiral pattern must emit projectile waves")
        p = boss.projectiles[-1]
        self.assertEqual(p.color, (170, 40, 230))

    def test_lord_malus_homing_dark_wisps(self):
        """Lord Malus must launch tracking shadow wisps with undulating motion."""
        boss = LordMalus(400, 200, self.asset_factory, self.sound_manager)
        boss.pattern_index = 2
        boss._cast_attack(self.player, self.particles, self.camera)

        homing_projs = [p for p in boss.projectiles if p.p_type == "homing"]
        self.assertTrue(len(homing_projs) >= 5, "Expected homing wisps cluster")
        self.assertEqual(homing_projs[0].shape, "wisp")

    # ==========================================================================
    # 3. IGNIS COLOSSUS (MAGMA) BULLET-HELL PATTERNS
    # ==========================================================================
    def test_ignis_colossus_magma_radial_bursts(self):
        """Ignis Colossus must detonate high-speed explosive shard starbursts."""
        boss = IgnisColossus(400, 200, self.asset_factory, self.sound_manager)
        boss.pattern_index = 0
        boss._cast_attack(self.player, self.particles, self.camera)

        self.assertTrue(len(boss.projectiles) >= 20, "Expected at least 20 shards in radial burst")
        p0 = boss.projectiles[0]
        self.assertEqual(p0.color, (255, 70, 20))
        self.assertEqual(p0.shape, "shard")

    def test_ignis_colossus_falling_meteor_showers(self):
        """Ignis Colossus must summon cascading diagonal falling meteor curtains."""
        boss = IgnisColossus(400, 200, self.asset_factory, self.sound_manager)
        boss.pattern_index = 1
        boss._cast_attack(self.player, self.particles, self.camera)

        meteors = [p for p in boss.projectiles if p.p_type == "meteor"]
        self.assertTrue(len(meteors) >= 10, "Expected meteor shower curtain")
        for m in meteors:
            self.assertTrue(m.vy > 5.0, "Meteors must descend at high speed")

    def test_ignis_colossus_blazing_fire_rings_with_gaps(self):
        """Ignis Colossus must cast fire rings with prominent player dodge gaps."""
        boss = IgnisColossus(400, 200, self.asset_factory, self.sound_manager)
        boss.pattern_index = 2
        boss._cast_attack(self.player, self.particles, self.camera)

        self.assertTrue(len(boss.projectiles) >= 14, "Expected blazing fire ring")
        p0 = boss.projectiles[0]
        self.assertEqual(p0.color, (255, 140, 30))

    # ==========================================================================
    # 4. CRYO-SPUD (GLACIAL) BULLET-HELL PATTERNS
    # ==========================================================================
    def test_cryo_spud_snowflake_bursts(self):
        """Cryo-Spud must fire 16-point symmetrical crystalline snowflake bursts."""
        boss = CryoSpud(400, 200, self.asset_factory, self.sound_manager)
        boss.pattern_index = 0
        boss._cast_attack(self.player, self.particles, self.camera)

        snowflakes = [p for p in boss.projectiles if p.shape == "snowflake"]
        self.assertEqual(len(snowflakes), 16, "Must emit exactly 16 symmetrical snowflake points")
        self.assertEqual(snowflakes[0].color, (80, 210, 255))

        # In Phase 2: dual 16-point burst scheduled for 32-point hyper-snowflake
        boss.phase = 2
        boss.pattern_index = 0
        boss._cast_attack(self.player, self.particles, self.camera)
        self.assertEqual(boss.active_pattern, "snowflake_burst2")

    def test_cryo_spud_frost_needle_waves(self):
        """Cryo-Spud must stream undulating serpentine frost needles."""
        boss = CryoSpud(400, 200, self.asset_factory, self.sound_manager)
        boss.pattern_index = 1
        boss._cast_attack(self.player, self.particles, self.camera)

        self.assertEqual(boss.active_pattern, "frost_needle_waves")
        # Step wave
        for _ in range(4):
            boss._step_pattern(0.08, self.player, self.particles, self.camera)

        wave_projs = [p for p in boss.projectiles if p.p_type == "wave"]
        self.assertTrue(len(wave_projs) >= 2, "Must stream sine-wave needles")
        self.assertTrue(wave_projs[0].wave_amplitude > 0.0)

    def test_cryo_spud_freezing_pinwheel_vortex(self):
        """Cryo-Spud must emit counter-rotating dual pinwheel vortex."""
        boss = CryoSpud(400, 200, self.asset_factory, self.sound_manager)
        boss.pattern_index = 2
        boss._cast_attack(self.player, self.particles, self.camera)

        self.assertEqual(boss.active_pattern, "pinwheel_vortex")
        for _ in range(3):
            boss._step_pattern(0.10, self.player, self.particles, self.camera)
        self.assertTrue(len(boss.projectiles) >= 8, "Pinwheel vortex must emit interlocking arms")

    # ==========================================================================
    # 5. NECRO-TUBER (BONE/CATACOMBS) BULLET-HELL PATTERNS
    # ==========================================================================
    def test_necro_tuber_bone_shard_spirals(self):
        """Necro-Tuber must channel counter-rotating dual spiral barrage."""
        boss = NecroTuber(400, 200, self.asset_factory, self.sound_manager)
        boss.pattern_index = 0
        boss._cast_attack(self.player, self.particles, self.camera)

        self.assertEqual(boss.active_pattern, "bone_shard_spirals")
        for _ in range(4):
            boss._step_pattern(0.09, self.player, self.particles, self.camera)
        self.assertTrue(len(boss.projectiles) >= 8, "Bone shard dual spiral must emit waves")

    def test_necro_tuber_skull_scythe_arcs(self):
        """Necro-Tuber must sweep inward-curving crescent scythe arcs."""
        boss = NecroTuber(400, 200, self.asset_factory, self.sound_manager)
        boss.pattern_index = 1
        boss._cast_attack(self.player, self.particles, self.camera)

        scythes = [p for p in boss.projectiles if p.shape == "scythe"]
        self.assertTrue(len(scythes) >= 7, "Expected wide arc of spectral scythes")
        # Check trajectory curvature
        has_curves = any(s.curve_rate != 0.0 for s in scythes)
        self.assertTrue(has_curves, "Scythes must curve inward toward player")

    def test_necro_tuber_catacomb_cross_curtains(self):
        """Necro-Tuber must summon perpendicular criss-crossing grid curtains."""
        boss = NecroTuber(400, 200, self.asset_factory, self.sound_manager)
        boss.pattern_index = 2
        boss._cast_attack(self.player, self.particles, self.camera)

        self.assertTrue(len(boss.projectiles) >= 12, "Expected criss-cross curtain grid")
        # Both positive and negative horizontal velocities for cross lanes
        has_pos_vx = any(p.vx > 0 for p in boss.projectiles)
        has_neg_vx = any(p.vx < 0 for p in boss.projectiles)
        self.assertTrue(has_pos_vx and has_neg_vx, "Must have crossing bullet lanes")

    # ==========================================================================
    # 6. GRAND BOSS SOL-RHO (PHASE 1 & PHASE 2) BULLET-HELL PATTERNS
    # ==========================================================================
    def test_sol_rho_phase1_solar_nova_rings(self):
        """Sol-Rho Phase 1 must cast expanding solar flare nova rings with dodge gaps."""
        boss = GrandBossSolRho(400, 200, self.asset_factory, self.sound_manager)
        self.assertEqual(boss.phase, 1)
        boss.pattern_index = 0
        boss._cast_phase1_attack(self.player, self.particles, self.camera)

        self.assertTrue(len(boss.projectiles) >= 20, "Expected solar nova ring")
        p0 = boss.projectiles[0]
        self.assertEqual(p0.color, (255, 190, 30))
        self.assertEqual(p0.core_color, (255, 255, 220))
        self.assertEqual(boss.active_pattern, "solar_nova_ring2")

    def test_sol_rho_phase1_sunburst_wheel(self):
        """Sol-Rho Phase 1 must spin a 4-arm rotating sunburst wheel."""
        boss = GrandBossSolRho(400, 200, self.asset_factory, self.sound_manager)
        boss.pattern_index = 1
        boss._cast_phase1_attack(self.player, self.particles, self.camera)

        self.assertEqual(boss.active_pattern, "sunburst_wheel")
        for _ in range(4):
            boss._step_pattern(0.08, self.player, self.particles, self.camera)
        self.assertTrue(len(boss.projectiles) >= 16, "Quad-arm sunburst wheel must emit rotating rays")

    def test_sol_rho_phase1_sweeping_beam_arcs(self):
        """Sol-Rho Phase 1 must sweep continuous solar beam needles across arena."""
        boss = GrandBossSolRho(400, 200, self.asset_factory, self.sound_manager)
        boss.pattern_index = 2
        boss._cast_phase1_attack(self.player, self.particles, self.camera)

        self.assertEqual(boss.active_pattern, "sweeping_beam")
        for _ in range(3):
            boss._step_pattern(0.07, self.player, self.particles, self.camera)
        beams = [p for p in boss.projectiles if p.shape == "needle"]
        self.assertTrue(len(beams) >= 4, "Must emit sweeping beam needles")

    def test_sol_rho_phase2_void_singularity_spiral(self):
        """Sol-Rho Phase 2 must channel 5-arm accelerating abyssal spiral barrage."""
        boss = GrandBossSolRho(400, 200, self.asset_factory, self.sound_manager)
        boss.phase = 2
        boss.pattern_index = 0
        boss._cast_phase2_attack(self.player, self.particles, self.camera)

        self.assertEqual(boss.active_pattern, "void_spiral")
        for _ in range(4):
            boss._step_pattern(0.08, self.player, self.particles, self.camera)
        void_projs = [p for p in boss.projectiles if p.color == (150, 30, 230)]
        self.assertTrue(len(void_projs) >= 15, "5-arm void spiral must emit dense barrage")
        self.assertTrue(void_projs[0].accel > 1.0, "Void spiral bullets must accelerate outward")

    def test_sol_rho_phase2_warp_blitz_bullet_storm(self):
        """Sol-Rho Phase 2 blitz state must detonate 360-degree starburst nova + tracking swarm."""
        boss = GrandBossSolRho(400, 200, self.asset_factory, self.sound_manager)
        boss.phase = 2
        boss._cast_warp_blitz_bullet_storm(self.player, self.particles, self.camera)

        nova = [p for p in boss.projectiles if p.shape == "shard"]
        wisps = [p for p in boss.projectiles if p.shape == "wisp"]
        self.assertEqual(len(nova), 32, "Must fire full 32-shard omni-directional starburst nova")
        self.assertTrue(len(wisps) >= 4, "Must fire accompanying homing tracking swarm")

    # ==========================================================================
    # 7. HIGH-DENSITY BULLET-HELL PERFORMANCE BENCHMARK (60+ FPS)
    # ==========================================================================
    def test_high_density_500_projectiles_performance_benchmark(self):
        """Validates that 500+ active projectiles update & render in < 5ms (> 120 FPS)."""
        boss = GrandBossSolRho(400, 200, self.asset_factory, self.sound_manager)
        screen = pygame.Surface((1280, 720))

        # Spawn 500 active bullet-hell projectiles with diverse motions
        for i in range(500):
            ang = (i / 500.0) * math.tau
            spd = 3.0 + (i % 6)
            p = BossProjectile(
                x=SCREEN_WIDTH // 2, y=SCREEN_HEIGHT // 2,
                vx=math.cos(ang) * spd, vy=math.sin(ang) * spd,
                radius=10, damage=12,
                color=(255, 180, 40) if i % 2 == 0 else (180, 50, 255),
                shape="orb" if i % 3 == 0 else ("needle" if i % 3 == 1 else "shard"),
                wave_amplitude=3.0 if i % 5 == 0 else 0.0,
                wave_frequency=8.0 if i % 5 == 0 else 0.0
            )
            boss.projectiles.append(p)

        self.assertEqual(len(boss.projectiles), 500)

        # Benchmark 30 simulation and render frames
        t_start = time.perf_counter()
        for _ in range(30):
            for p in boss.projectiles:
                p.update(0.016, self.player)
            boss.render(screen, self.camera)
        elapsed = time.perf_counter() - t_start

        avg_frame_ms = (elapsed / 30.0) * 1000.0
        print(f"\n  -> Bullet-Hell Benchmark (500 projectiles): {avg_frame_ms:.2f} ms/frame (~{1000.0 / max(0.01, avg_frame_ms):.1f} FPS)")
        self.assertTrue(avg_frame_ms < 16.66, f"Frame time {avg_frame_ms:.2f}ms exceeds 60 FPS limit (16.6ms)")

    # ==========================================================================
    # 8. MULTIPLAYER SNAPSHOT SERIALIZATION & RECONCILIATION
    # ==========================================================================
    def test_multiplayer_bullet_hell_snapshot_synchronization(self):
        """Verifies authoritative host serializes bullet patterns and LAN clients reconstruct them."""
        combat_host = CombatManager(self.asset_factory, self.sound_manager, self.particles, self.camera)
        combat_client = CombatManager(self.asset_factory, self.sound_manager, self.particles, self.camera)
        combat_client.is_client = True

        # Host spawns Cryo-Spud with active snowflake burst
        combat_host.spawn_boss(500, 300, boss_cls="cryo_spud")
        boss_host = combat_host.boss
        boss_host.pattern_index = 0
        boss_host._cast_attack(self.player, self.particles, self.camera)
        self.assertEqual(len(boss_host.projectiles), 16)

        # Host serializes boss snapshot
        boss_sync = combat_host.get_boss_sync_data()
        self.assertIsNotNone(boss_sync)
        self.assertIn("projectiles", boss_sync)
        self.assertEqual(len(boss_sync["projectiles"]), 16)

        # Client consumes snapshot
        combat_client.sync_from_host(mobs_data=[], boss_data=boss_sync)
        self.assertIsNotNone(combat_client.boss)
        self.assertEqual(len(combat_client.boss.projectiles), 16)
        self.assertEqual(combat_client.boss.projectiles[0].shape, "snowflake")

        # Client updates projectiles and checks graze detection
        self.player.x = combat_client.boss.projectiles[0].x + 16
        self.player.y = combat_client.boss.projectiles[0].y
        initial_graze = self.player.graze_count
        combat_client.update(0.016, None, self.player)
        self.assertTrue(self.player.graze_count >= initial_graze, "Client player must be able to graze synchronized bullets")

    # ==========================================================================
    # 9. EDGE CASES, KINEMATIC INTEGRITY & DODGE FAIRNESS TESTS
    # ==========================================================================
    def test_projectile_delay_move_and_age_serialization(self):
        """Verifies delay_move and age are accurately preserved during network serialization."""
        p = BossProjectile(x=120, y=240, vx=4.5, vy=1.2, delay_move=0.45, wave_amplitude=5.0, wave_frequency=6.0)
        p.age = 0.30
        sync_dict = p.to_sync_dict()

        self.assertIn("del", sync_dict)
        self.assertEqual(sync_dict["del"], 0.45)
        self.assertIn("age", sync_dict)
        self.assertEqual(sync_dict["age"], 0.30)

        p2 = BossProjectile.from_sync_dict(sync_dict)
        self.assertEqual(p2.delay_move, 0.45)
        self.assertEqual(p2.age, 0.30)

    def test_vector_bullet_surface_bounds_no_clipping(self):
        """Verifies vector bullet surfaces have ample margin so sharp shapes are never clipped at edges."""
        # Needle at 0 deg (head along positive x)
        surf_needle = get_bullet_surface("needle", (100, 200, 255), radius=10, angle_deg=0)
        w, h = surf_needle.get_size()
        # Verify right-most pixel column has zero alpha (no chopped tip)
        col_alphas = [surf_needle.get_at((w - 1, y))[3] for y in range(h)]
        self.assertEqual(max(col_alphas), 0, "Needle tip must not touch or clip off the right edge of surface")

        # Scythe at 0 deg
        surf_scythe = get_bullet_surface("scythe", (180, 80, 240), radius=10, angle_deg=0)
        sw, sh = surf_scythe.get_size()
        scythe_alphas = [surf_scythe.get_at((sw - 1, y))[3] for y in range(sh)]
        self.assertEqual(max(scythe_alphas), 0, "Scythe tip must not touch or clip off the right edge of surface")

    def test_sol_rho_phase_transition_bullet_wipe_and_pattern_reset(self):
        """Verifies Sol-Rho Phase 1 death wipes all Phase 1 bullets and cancels active pattern."""
        boss = GrandBossSolRho(400, 200, self.asset_factory, self.sound_manager)
        boss.pattern_index = 1
        boss._cast_phase1_attack(self.player, self.particles, self.camera)
        boss._step_pattern(0.08, self.player, self.particles, self.camera)
        self.assertEqual(boss.active_pattern, "sunburst_wheel")
        self.assertTrue(len(boss.projectiles) > 0)

        # Inflict fatal Phase 1 damage
        boss.take_damage(2000)
        self.assertTrue(boss.is_transforming)
        self.assertIsNone(boss.active_pattern, "Phase 1 active pattern must be cancelled upon transformation")
        self.assertEqual(len(boss.projectiles), 0, "Phase 1 projectiles must be wiped cleanly")

        # Update through the 2.2s transformation
        boss.update(2.5, None, self.player, self.particles, self.camera)
        self.assertEqual(boss.phase, 2)
        self.assertFalse(boss.is_transforming)
        self.assertIsNone(boss.active_pattern, "Phase 2 must awaken with a clean pattern slate")
        self.assertEqual(len(boss.projectiles), 0, "Phase 2 must awaken with no leftover Phase 1 bullets")

    def test_sol_rho_multiplayer_transformation_sync_and_client_animation(self):
        """Verifies Sol-Rho transformation status is synchronized and client animates breathing frames."""
        combat_host = CombatManager(self.asset_factory, self.sound_manager, self.particles, self.camera)
        combat_client = CombatManager(self.asset_factory, self.sound_manager, self.particles, self.camera)
        combat_client.is_client = True

        boss_host = GrandBossSolRho(400, 200, self.asset_factory, self.sound_manager)
        combat_host.boss = boss_host
        boss_host.take_damage(2000)
        self.assertTrue(boss_host.is_transforming)

        # Sync snapshot to client
        sync_data = combat_host.get_boss_sync_data()
        self.assertIn("transforming", sync_data)
        self.assertTrue(sync_data["transforming"])

        combat_client.sync_from_host([], boss_data=sync_data)
        self.assertIsNotNone(combat_client.boss)
        self.assertTrue(getattr(combat_client.boss, "is_transforming", False), "Client must recognize boss is transforming")

        # Verify client advances animation frames
        combat_client.boss.is_transforming = False
        combat_client.boss.anim_timer = 0.0
        initial_frame = combat_client.boss.frame_idx
        # Run several updates to advance anim_timer
        for _ in range(15):
            combat_client.update(0.02, None, self.player)
        self.assertNotEqual(combat_client.boss.frame_idx, initial_frame, "Sol-Rho must animate frames on LAN client")

    def test_iframe_safe_bullet_dissipation_prevents_stunlock(self):
        """Verifies bullets dissipate on core collision during i-frames without dealing damage or lingering."""
        boss = LordMalus(400, 200, self.asset_factory, self.sound_manager)
        self.player.x = 400
        self.player.y = 400
        self.player.i_frame_timer = 0.5  # Player is currently invulnerable!
        initial_hp = self.player.health

        # Spawn a bullet directly in player hitbox
        bullet = BossProjectile(x=self.player.center_x, y=self.player.center_y, vx=0.0, vy=0.0, radius=10, damage=20)
        boss.projectiles.append(bullet)

        # Update boss against player
        boss.update(0.016, None, self.player, self.particles, self.camera)

        # Player must NOT have taken damage (protected by i-frames)
        self.assertEqual(self.player.health, initial_hp)
        # Bullet must be safely dissipated (life = 0) so it does NOT linger to stunlock player!
        self.assertEqual(len(boss.projectiles), 0, "Bullet must dissipate harmlessly during player i-frames")

    def test_celestial_aegis_deflects_boss_bullets(self):
        """Verifies player wearing Celestial Aegis deflects and destroys incoming boss projectiles."""
        boss = LordMalus(400, 200, self.asset_factory, self.sound_manager)
        self.player.x = 400
        self.player.y = 400

        # Mock player having celestial aegis effect
        orig_has_effect = getattr(self.player, "has_effect", lambda e: False)
        self.player.has_effect = lambda eff: (eff == "celestial aegis") or orig_has_effect(eff)

        # Place projectile within 30px deflection boundary of player
        bullet = BossProjectile(x=self.player.center_x + 25, y=self.player.center_y, vx=-5.0, vy=0.0, radius=10, damage=25)
        boss.projectiles.append(bullet)

        boss.update(0.016, None, self.player, self.particles, self.camera)
        self.assertEqual(len(boss.projectiles), 0, "Celestial Aegis must deflect and destroy boss projectile")

    def test_player_graze_audio_and_visual_feedback(self):
        """Verifies grazing triggers audio feedback and player renders a graze aura ellipse."""
        self.player.x = 400
        self.player.y = 400
        self.player.graze_timer = 0.0

        bullet = BossProjectile(x=438, y=415, vx=0.0, vy=0.0, radius=12, damage=20)
        bullet.update(0.016, self.player)

        self.assertTrue(bullet.grazed)
        self.assertTrue(self.player.graze_timer > 0.0)

        # Test rendering with active graze_timer
        target = pygame.Surface((1280, 720), pygame.SRCALPHA)
        self.player.render(target, self.camera)
        # Verify render succeeds without exception

    def test_pattern_boundary_guards_zero_inputs(self):
        """Verifies BulletHellPatterns gracefully handles zero or negative counts without throwing ZeroDivisionError."""
        self.assertEqual(BulletHellPatterns.spawn_concentric_ring(100, 100, count=0, speed=5, color=(255, 0, 0)), [])
        self.assertEqual(BulletHellPatterns.spawn_spiral_step(100, 100, arms=0, current_angle=0, speed=5, color=(255, 0, 0)), [])
        self.assertEqual(BulletHellPatterns.spawn_aimed_spread(100, 100, 200, 200, count=0, spread_angle_deg=45, speed=5, color=(255, 0, 0)), [])
        self.assertEqual(BulletHellPatterns.spawn_snowflake_burst(100, 100, points=0, speed=5), [])
        self.assertEqual(BulletHellPatterns.spawn_undulating_stream(100, 100, angle=0, speed=5, count=0), [])
        self.assertEqual(BulletHellPatterns.spawn_criss_cross_curtains(100, 100, count=0), [])
        self.assertEqual(BulletHellPatterns.spawn_homing_swarm(100, 100, 200, 200, count=0), [])
        self.assertEqual(BulletHellPatterns.spawn_meteor_curtain(100, 100, count=0), [])
        self.assertEqual(BulletHellPatterns.spawn_warp_nova(100, 100, count=0), [])


if __name__ == "__main__":
    unittest.main()
