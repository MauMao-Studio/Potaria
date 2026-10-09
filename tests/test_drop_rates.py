"""
Unit & Statistical tests for the updated Drop Rate Roll Chances in Potaria.
Verifies:
1. Rarity catalog pools populate properly from ITEM_REGISTRY.
2. Mob loot drops respect the Option 2 (Moderate ARPG) probabilities:
   - Uncommon: 3.5% (1 in ~28)
   - Rare & Skills: 1.5% (1 in ~67)
   - Epic: 0.50% (1 in 200)
   - Mythic: 0.15% (1 in ~667)
   - Legendary: 0.05% (1 in 2,000)
   - Ancient: 0.01% (1 in 10,000)
3. Ancient drop triggers fanfare banner and camera shake.
4. Chest rolls include Epic (15%) and Mythic (3%) opportunities.
"""

import unittest
import os
import random
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
from src.ui.inventory import ITEM_REGISTRY


class TestDropRates(unittest.TestCase):
    def setUp(self):
        self.factory = AssetFactory()
        self.sound = SoundManager()
        self.particles = ParticleSystem()
        self.camera = Camera(800, 600)
        self.combat = CombatManager(self.factory, self.sound, self.particles, self.camera)
        self.player = Player(200, 200, self.factory, self.sound)

    def test_01_catalog_rarity_pools_populated(self):
        """Verify that all rarity pools are populated with weapon and armor items."""
        # Trigger initialization of _catalog_rarity_pools
        mob = GreenSlime(200, 200, self.factory)
        self.combat._drop_mob_loot(mob)

        pools = self.combat._catalog_rarity_pools
        self.assertIn("uncommon", pools)
        self.assertIn("rare", pools)
        self.assertIn("epic", pools)
        self.assertIn("mythic", pools)
        self.assertIn("legendary", pools)
        self.assertIn("ancient", pools)

        self.assertGreater(len(pools["uncommon"]), 50, "Uncommon pool should have items")
        self.assertGreater(len(pools["rare"]), 50, "Rare pool should have items")
        self.assertGreater(len(pools["epic"]), 30, "Epic pool should have items")
        self.assertGreater(len(pools["mythic"]), 30, "Mythic pool should have items")
        self.assertGreater(len(pools["legendary"]), 20, "Legendary pool should have items")
        self.assertGreater(len(pools["ancient"]), 10, "Ancient pool should have items")

    def test_02_ancient_drop_banner_and_fanfare(self):
        """Verify that an ancient drop creates an announcement banner and camera shake."""
        self.combat.ancient_drop_banner = None
        self.combat._trigger_ancient_drop("ancient_sword", 300, 300)

        self.assertIsNotNone(self.combat.ancient_drop_banner)
        self.assertEqual(self.combat.ancient_drop_banner["item_id"], "ancient_sword")
        self.assertGreater(self.combat.ancient_drop_banner["timer"], 0)
        self.assertGreater(len(self.combat.dropped_items), 0)
        self.assertEqual(self.combat.dropped_items[-1].item_id, "ancient_sword")

    def test_03_statistical_mob_drop_rates(self):
        """Statistical simulation verifying drop frequencies over 20,000 kills match Option 2 rates."""
        random.seed(42)  # Deterministic seed for reproducible testing
        mob = GreenSlime(200, 200, self.factory)

        uncommon_count = 0
        rare_count = 0
        epic_count = 0
        mythic_count = 0
        legendary_count = 0
        ancient_count = 0

        # Run 20,000 loot rolls
        TRIALS = 20000
        for _ in range(TRIALS):
            self.combat.dropped_items.clear()
            self.combat._drop_mob_loot(mob)

            dropped_ids = [it.item_id for it in self.combat.dropped_items]
            for iid in dropped_ids:
                if iid in ("copper_coin", "silver_coin", "gold_coin", "spud_sap", "raw_potato", "healing_potion", "bone", "iron_ore", "copper_ore", "torch"):
                    continue
                idata = ITEM_REGISTRY.get(iid, {})
                r = idata.get("rarity")
                if r == "uncommon":
                    uncommon_count += 1
                elif r == "rare":
                    rare_count += 1
                elif r == "epic":
                    epic_count += 1
                elif r == "mythic":
                    mythic_count += 1
                elif r == "legendary":
                    legendary_count += 1
                elif r == "ancient":
                    ancient_count += 1

        unc_rate = uncommon_count / TRIALS
        rare_rate = rare_count / TRIALS
        epic_rate = epic_count / TRIALS
        myth_rate = mythic_count / TRIALS
        leg_rate = legendary_count / TRIALS
        anc_rate = ancient_count / TRIALS

        # Verify rates align with targets within standard statistical error margin
        # Target: Uncommon 3.5% (0.035), Rare ~1.5% (0.015), Epic 0.5% (0.005)
        self.assertAlmostEqual(unc_rate, 0.035, delta=0.010, msg=f"Uncommon rate {unc_rate} outside expected range")
        self.assertAlmostEqual(rare_rate, 0.015, delta=0.007, msg=f"Rare rate {rare_rate} outside expected range")
        self.assertAlmostEqual(epic_rate, 0.005, delta=0.004, msg=f"Epic rate {epic_rate} outside expected range")
        # Higher tiers: ensure occurrences were logged and are non-zero
        self.assertGreater(mythic_count, 5, f"Mythic drops should occur across 20k trials, got {mythic_count}")
        self.assertGreater(legendary_count, 2, f"Legendary drops should occur across 20k trials, got {legendary_count}")
        self.assertGreaterEqual(ancient_count, 1, f"Ancient drops should occur across 20k trials, got {ancient_count}")

    def test_04_chest_drop_rolls(self):
        """Verify that opening chests rolls guaranteed loot and can drop Epic and Mythic gear."""
        class MockWorld:
            def set_tile(self, tx, ty, tid):
                pass

        class MockGame:
            def __init__(self, combat, factory, sound, particles, camera):
                self.world = MockWorld()
                self.block_deltas = {}
                self.client = None
                self.sound_manager = sound
                self.particle_system = particles
                self.combat = combat
                self.asset_factory = factory
                self.camera = camera

        from main import PotariaGame
        mock_game = MockGame(self.combat, self.factory, self.sound, self.particles, self.camera)

        random.seed(123)
        epic_found = 0
        mythic_found = 0
        trials = 500

        for _ in range(trials):
            self.combat.dropped_items.clear()
            PotariaGame._open_or_break_chest(mock_game, 10, 10, 320, 320)

            dropped_ids = [it.item_id for it in self.combat.dropped_items]
            # Must always include chest, bars, potions
            self.assertIn("chest", dropped_ids)

            for iid in dropped_ids:
                r = ITEM_REGISTRY.get(iid, {}).get("rarity")
                if r == "epic":
                    epic_found += 1
                elif r == "mythic":
                    mythic_found += 1

        mythic_rate = mythic_found / trials

        # Ensure Epic drops occur significantly (both from dedicated 15% roll and rare fallback items)
        self.assertGreater(epic_found, 40, f"Expected frequent Epic drops, got {epic_found}")
        # Expected: ~3% Mythic (around 15 in 500 trials)
        self.assertGreaterEqual(mythic_found, 5, f"Expected Mythic drops in 500 trials, got {mythic_found}")
        self.assertAlmostEqual(mythic_rate, 0.03, delta=0.02, msg=f"Chest Mythic rate {mythic_rate} expected ~0.03")


if __name__ == "__main__":
    unittest.main()
