"""
Potaria - Skills, Bosses & Projectile Integration Verification Suite
Validates the implementation of Potaria_Skills_and_Bosses_Design_Spec:
1. Complete Skill System (30 skills, 5-level evolution, unique IDs, stats)
2. Ancient Skill: Celestial Reversal (reflection window, budget cap, loop prevention, boss damage)
3. Mini-Boss & Grand Boss Signature Patterns (safe corridors, telegraphs, counterplay)
4. Asset Library Integrity (Contact sheet, 41 skill icons, animated effects, tracker compliance)
Developer: Kurados | Pure Python 3.13 + pygame-ce
"""

import os
import sys
import math
import unittest
from PIL import Image

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"

import pygame
pygame.init()
pygame.display.set_mode((1280, 720))

from src.constants import SCREEN_WIDTH, SCREEN_HEIGHT
from src.assets.asset_factory import AssetFactory
from src.audio.sound_effects import SoundManager
from src.camera import Camera
from src.entities.particle import ParticleSystem
from src.entities.player import Player
from src.rpg.skills import SkillManager, SKILL_DEFINITIONS
from src.entities.bullet_hell import (
    BossProjectile, BulletHellPatterns
)
from src.entities.boss import (
    DungeonMiniBoss, LordMalus, IgnisColossus, CryoSpud, NecroTuber,
    GrandBossSolRho, create_boss_by_type
)


class TestSkillsBossesSpec(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.af = AssetFactory()
        cls.sm = SoundManager()
        cls.camera = Camera(SCREEN_WIDTH, SCREEN_HEIGHT)

    def setUp(self):
        self.particles = ParticleSystem()
        self.player = Player(400, 400, self.af, self.sm)
        self.player.i_frame_timer = 0.0

    # =========================================================================
    # 1. SKILL DEFINITIONS & EVOLUTION INTEGRITY
    # =========================================================================
    def test_01_skill_definitions_registry(self):
        """All 30 registered skills exist with required contract attributes."""
        self.assertGreaterEqual(len(SKILL_DEFINITIONS), 30)

        # Check ancient skill
        self.assertIn("celestial_reversal", SKILL_DEFINITIONS)
        cr = SKILL_DEFINITIONS["celestial_reversal"]
        self.assertEqual(cr["name"], "Celestial Reversal")
        self.assertEqual(cr["evolved_name"], "Celestial Mirror")
        self.assertEqual(cr["rarity"], "Ancient")
        self.assertEqual(cr["max_level"], 5)
        self.assertEqual(cr["evolution_level"], 3)
        self.assertTrue(cr["projectile_rules"]["reflectable_only"])
        self.assertEqual(cr["projectile_rules"]["max_reflections_per_activation"], 12)
        self.assertTrue(cr["projectile_rules"]["prevent_reflection_loop"])

        # Check Section 4 library skills
        expected_library = [
            "shuriken_storm", "star_seeker", "arcane_barrage", "venom_volley",
            "void_implosion", "crystal_shatter", "chain_discharge", "meteor_shower",
            "piercing_blizzard", "solar_detonation", "arcane_minefield", "frost_bomb",
            "ember_cluster", "spectral_pursuit", "returning_hatchet", "bolo_cyclone",
            "ancestral_guidance", "sumpang_sibat", "magma_eruption"
        ]
        for sid in expected_library:
            self.assertIn(sid, SKILL_DEFINITIONS, f"Missing skill: {sid}")
            sdata = SKILL_DEFINITIONS[sid]
            self.assertIn("evolved_name", sdata)
            self.assertIn("mp_cost", sdata)
            self.assertGreater(sdata["mp_cost"], 0)
            self.assertIn("cooldown", sdata)
            self.assertGreater(sdata["cooldown"], 0.0)
            self.assertIn("dmg_mult", sdata)
            self.assertGreater(sdata["dmg_mult"], 0.0)

    def test_02_skill_evolution_progression(self):
        """Skills evolve at Lv 3+ returning evolved name and improved damage scaling."""
        mgr = SkillManager()
        mgr.learn_skill("celestial_reversal")

        # Lv 1
        self.assertEqual(mgr.get_skill_level("celestial_reversal"), 1)
        self.assertFalse(mgr.is_skill_evolved("celestial_reversal"))
        self.assertEqual(mgr.get_skill_name("celestial_reversal"), "Celestial Reversal")
        dmg_lv1 = mgr.get_skill_dmg_mult("celestial_reversal")

        # Upgrade to Lv 2
        mgr.learn_skill("celestial_reversal")
        self.assertEqual(mgr.get_skill_level("celestial_reversal"), 2)
        self.assertFalse(mgr.is_skill_evolved("celestial_reversal"))

        # Upgrade to Lv 3 (Evolution threshold!)
        mgr.learn_skill("celestial_reversal")
        self.assertEqual(mgr.get_skill_level("celestial_reversal"), 3)
        self.assertTrue(mgr.is_skill_evolved("celestial_reversal"))
        self.assertEqual(mgr.get_skill_name("celestial_reversal"), "Celestial Mirror")
        dmg_lv3 = mgr.get_skill_dmg_mult("celestial_reversal")
        self.assertGreater(dmg_lv3, dmg_lv1)

        # Upgrade to Lv 5 (Max tier)
        mgr.learn_skill("celestial_reversal")
        mgr.learn_skill("celestial_reversal")
        self.assertEqual(mgr.get_skill_level("celestial_reversal"), 5)
        # Cannot exceed max level
        self.assertFalse(mgr.learn_skill("celestial_reversal"))
        self.assertEqual(mgr.get_skill_level("celestial_reversal"), 5)

    def test_03_hotkey_assignment(self):
        """Skill manager allows binding hotkeys including Z for celestial reversal."""
        mgr = SkillManager()
        mgr.learn_skill("celestial_reversal")
        success = mgr.assign_skill("Z", "celestial_reversal")
        self.assertTrue(success)
        self.assertEqual(mgr.hotkey_bindings.get("Z"), "celestial_reversal")

    # =========================================================================
    # 2. CELESTIAL REVERSAL & REFLECTION CONTRACT
    # =========================================================================
    def test_04_player_reflection_activation(self):
        """Casting celestial_reversal activates reflection window, budget, and i-frames."""
        self.player.skills.learn_skill("celestial_reversal")
        self.player.stats.mp = 50

        # Cast via hotkey
        res = self.player.cast_skill_hotkey("celestial_reversal", self.particles, self.camera)
        self.assertTrue(res)
        self.assertGreater(self.player.reflection_field_timer, 0.35)
        self.assertEqual(self.player.reflection_budget, 12)
        self.assertGreater(self.player.i_frame_timer, 0.40)

        # Level scaling of reflection budget
        self.player.skills.skill_levels["celestial_reversal"] = 5
        self.player.stats.mp = 50
        self.player.skills.cooldowns.clear()
        res5 = self.player.cast_skill_hotkey("celestial_reversal", self.particles, self.camera)
        self.assertTrue(res5)
        # Lv 5 budget: 12 + (5 - 1) * 3 = 24
        self.assertEqual(self.player.reflection_budget, 24)
        self.assertAlmostEqual(self.player.reflection_field_timer, 0.52, delta=0.01)

    def test_05_projectile_reflect_contract(self):
        """Eligible BossProjectile reflects toward target, switches palette, and boosts damage."""
        p = BossProjectile(x=100, y=100, vx=5.0, vy=0.0, damage=20, reflectable=True)
        self.assertFalse(p.reflected)
        self.assertEqual(p.reflect_count, 0)

        # Reflect towards (500, 100)
        ok = p.reflect(target_x=500, target_y=100, damage_mult=1.5)
        self.assertTrue(ok)
        self.assertTrue(p.reflected)
        self.assertEqual(p.reflect_count, 1)
        self.assertEqual(p.damage, 30)  # 20 * 1.5
        self.assertGreater(p.vx, 0)
        self.assertAlmostEqual(p.vy, 0.0, delta=0.1)
        self.assertEqual(p.color, (255, 235, 120))  # Radiant gold shimmer

        # Anti-loop: cannot be reflected a second time
        ok2 = p.reflect(target_x=0, target_y=0)
        self.assertFalse(ok2)
        self.assertEqual(p.reflect_count, 1)

    def test_06_non_reflectable_projectiles_ignored(self):
        """Hazards, meteors, and marked non-reflectable projectiles cannot be reflected."""
        p_hazard = BossProjectile(x=100, y=100, vx=0, vy=5, reflectable=False)
        self.assertFalse(p_hazard.reflect(200, 200))
        self.assertFalse(p_hazard.reflected)

        roots = BulletHellPatterns.spawn_rotting_roots(400, 400, count=4)
        for r in roots:
            self.assertFalse(r.reflectable)
            self.assertFalse(r.reflect(100, 100))

    def test_07_mini_boss_reflection_encounter(self):
        """During reflection window, hostile bullets reflect, damage the boss, and spare player."""
        boss = LordMalus(400, 200, self.af, self.sm)
        initial_boss_hp = boss.hp
        initial_player_hp = self.player.health

        # Player activates reflection
        self.player.reflection_field_timer = 0.50
        self.player.reflection_budget = 5

        # Spawn a reflectable hostile projectile heading into player's reflection radius (<52px)
        # Player is at (400, 400)
        p = BossProjectile(x=410, y=410, vx=0.0, vy=2.0, damage=30, reflectable=True)
        boss.projectiles.append(p)

        # Update boss
        boss.update(0.016, None, self.player, self.particles, self.camera)

        # Bullet should have reflected!
        self.assertTrue(p.reflected)
        self.assertEqual(self.player.reflection_budget, 4)
        self.assertEqual(self.player.health, initial_player_hp)  # Player unscathed

        # Move reflected bullet to collide with boss frect (400, 200, 96, 96)
        p.x = 440
        p.y = 240
        boss.update(0.016, None, self.player, self.particles, self.camera)

        # Reflected bullet should have damaged boss and dissipated
        self.assertEqual(p.life, 0)
        self.assertLess(boss.hp, initial_boss_hp)

    def test_08_reflection_budget_depletion(self):
        """Exhausting reflection budget prevents further reflections even if timer remains."""
        boss = LordMalus(400, 200, self.af, self.sm)
        self.player.reflection_field_timer = 0.50
        self.player.reflection_budget = 1  # Only 1 reflection allowed

        p1 = BossProjectile(x=410, y=410, vx=0.0, vy=1.0, damage=20, reflectable=True)
        p2 = BossProjectile(x=415, y=415, vx=0.0, vy=1.0, damage=20, reflectable=True)
        boss.projectiles.extend([p1, p2])

        boss.update(0.016, None, self.player, self.particles, self.camera)

        # p1 was reflected, budget hit 0
        self.assertTrue(p1.reflected)
        self.assertEqual(self.player.reflection_budget, 0)
        # p2 could not be reflected due to budget exhaustion
        self.assertFalse(p2.reflected)

    def test_09_multiplayer_reflection_serialization(self):
        """to_sync_dict and from_sync_dict preserve reflected status and golden shimmer."""
        p = BossProjectile(x=250.5, y=320.2, vx=-4.0, vy=3.5, damage=24, p_id=42, reflectable=True)
        p.reflect(600, 100)

        d = p.to_sync_dict()
        self.assertEqual(d["ref"], 1)

        # Reconstruct on client
        p_remote = BossProjectile.from_sync_dict(d)
        self.assertTrue(p_remote.reflected)
        self.assertEqual(p_remote.color, (255, 235, 120))
        self.assertEqual(p_remote.core_color, (255, 255, 255))

    # =========================================================================
    # 3. BOSS SIGNATURE ATTACKS & FAIR COUNTERPLAY
    # =========================================================================
    def test_10_lord_malus_blight_apocalypse(self):
        """Lord Malus M4 signature spawns dense stream leaving a clearly marked safe corridor."""
        boss = LordMalus(400, 200, self.af, self.sm)
        projs = boss.cast_blight_apocalypse(self.player, self.particles, self.camera)
        self.assertGreaterEqual(len(projs), 18)

        # Angle directly toward player should be inside the safe corridor (no bullets directly on angle)
        ang_to_player = math.atan2(self.player.center_y - boss.center_y, self.player.center_x - boss.center_x)
        for p in projs:
            p_ang = math.atan2(p.vy, p.vx)
            diff = abs((p_ang - ang_to_player + math.pi) % (2.0 * math.pi) - math.pi)
            self.assertGreater(diff, 0.35, "Projectile spawned inside designated safe corridor!")

    def test_11_ignis_colossus_caldera_catastrophe(self):
        """Ignis Colossus I4 signature scales slam speeds and leaves 2 passage gaps."""
        boss = IgnisColossus(400, 200, self.af, self.sm)
        projs_slam1 = boss.cast_caldera_catastrophe(self.player, self.particles, self.camera, slam_step=1)
        projs_slam3 = boss.cast_caldera_catastrophe(self.player, self.particles, self.camera, slam_step=3)

        # Slam 3 should be visibly and measurably faster than slam 1
        spd1 = math.hypot(projs_slam1[0].vx, projs_slam1[0].vy)
        spd3 = math.hypot(projs_slam3[0].vx, projs_slam3[0].vy)
        self.assertGreater(spd3, spd1)

        # Count should reflect gaps
        self.assertLess(len(projs_slam1), 24, "Should omit projectiles to leave passage gaps")

    def test_12_cryo_spud_absolute_zero(self):
        """Cryo-Spud C4 signature spawns snowflake ring with exit gaps."""
        boss = CryoSpud(400, 200, self.af, self.sm)
        projs = boss.cast_absolute_zero(self.player, self.particles, self.camera)
        self.assertGreaterEqual(len(projs), 18)
        self.assertEqual(projs[0].shape, "snowflake")

    def test_13_necro_tuber_kingdom_of_the_unburied(self):
        """Necro-Tuber N4 signature divides arena into lane curtains with sweeping scythes."""
        boss = NecroTuber(400, 200, self.af, self.sm)
        projs = boss.cast_kingdom_of_the_unburied(self.player, self.particles, self.camera)
        self.assertGreaterEqual(len(projs), 14)
        scythes = [p for p in projs if p.shape == "scythe"]
        self.assertGreaterEqual(len(scythes), 2)

    def test_14_sol_rho_reflection_mechanics(self):
        """Grand Boss Sol-Rho phase 1 orbs are reflectable and damage Sol-Rho upon return."""
        sol_rho = GrandBossSolRho(400, 200, self.af, self.sm)
        initial_hp = sol_rho.hp

        # Player activates reflection
        self.player.reflection_field_timer = 0.50
        self.player.reflection_budget = 10

        # Solar orb fired at player
        orb = BossProjectile(x=415, y=415, vx=0, vy=3.0, damage=40, shape="orb", reflectable=True)
        sol_rho.projectiles.append(orb)

        sol_rho.update(0.016, None, self.player, self.particles, self.camera)
        self.assertTrue(orb.reflected)
        self.assertEqual(self.player.reflection_budget, 9)

        # Collide reflected orb with Sol-Rho
        orb.x = sol_rho.center_x
        orb.y = sol_rho.center_y
        sol_rho.update(0.016, None, self.player, self.particles, self.camera)

        self.assertEqual(orb.life, 0)
        self.assertLess(sol_rho.hp, initial_hp)

    # =========================================================================
    # 4. ASSETS & TRACKER VERIFICATION
    # =========================================================================
    def test_15_contact_sheet_preview_exists(self):
        """Contact sheet preview image exists with expected dimensions (1328x794)."""
        paths = [
            os.path.join("assets", "projectiles", "preview_contact_sheet.png"),
            os.path.join("docs", "projectiles_preview.png")
        ]
        for p in paths:
            self.assertTrue(os.path.exists(p), f"Preview sheet missing: {p}")
            with Image.open(p) as img:
                self.assertEqual(img.size, (1328, 794))

    def test_16_skill_icons_on_disk(self):
        """All 41 skill icons exist in assets/skills/ at 32x32 RGBA resolution."""
        skills_dir = os.path.join("assets", "skills")
        self.assertTrue(os.path.exists(skills_dir))
        files = [f for f in os.listdir(skills_dir) if f.endswith(".png")]
        self.assertGreaterEqual(len(files), 41)

        # Check celestial_reversal specifically
        cr_path = os.path.join(skills_dir, "celestial_reversal.png")
        self.assertTrue(os.path.exists(cr_path))
        with Image.open(cr_path) as img:
            self.assertEqual(img.size, (32, 32))
            self.assertEqual(img.mode, "RGBA")

    def test_17_animated_effects_on_disk(self):
        """New animated effects frames exist in assets/effects/ at 64x64 RGBA resolution."""
        eff_dir = os.path.join("assets", "effects")
        self.assertTrue(os.path.exists(eff_dir))

        expected_effects = [
            "celestial_reversal_activate",
            "projectile_reflect",
            "blight_apocalypse_telegraph",
            "caldera_catastrophe_telegraph",
            "absolute_zero_telegraph",
            "kingdom_of_the_unburied_telegraph"
        ]
        for eff in expected_effects:
            frame0 = os.path.join(eff_dir, f"{eff}_0.png")
            self.assertTrue(os.path.exists(frame0), f"Missing effect frame: {frame0}")
            with Image.open(frame0) as img:
                self.assertEqual(img.size, (64, 64))
                self.assertEqual(img.mode, "RGBA")

    def test_18_unique_assets_tracker_standards(self):
        """UNIQUE_ASSETS_TRACKER.md contains zero emojis and relative paths only."""
        tracker_path = "UNIQUE_ASSETS_TRACKER.md"
        self.assertTrue(os.path.exists(tracker_path))
        with open(tracker_path, "r", encoding="utf-8") as f:
            content = f.read()

        import re
        emojis = re.findall(r"[\U00010000-\U0010ffff]", content)
        self.assertEqual(len(emojis), 0, f"Found emojis in {tracker_path}: {emojis[:5]}")

        machine_paths = re.findall(r"[A-Za-z]:[/\\]", content)
        self.assertEqual(len(machine_paths), 0, f"Found machine paths in {tracker_path}: {machine_paths[:5]}")


if __name__ == "__main__":
    unittest.main()
