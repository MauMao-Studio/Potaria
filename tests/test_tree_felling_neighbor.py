"""
Potaria - Unit Test for Tree Felling with Adjacent/Neighboring Trees
Verifies that felling one tree NEVER strips leaves from a neighboring surviving tree.
Developer: Kurados
"""

import os
import unittest
import pygame

os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"
pygame.init()
pygame.display.set_mode((1280, 720))

from src.constants import TILE_AIR, TILE_DIRT, TILE_GRASS, TILE_WOOD_TRUNK, TILE_LEAVES
from src.assets.asset_factory import AssetFactory
from src.world.world import World


class TestNeighborTreeFelling(unittest.TestCase):
    def setUp(self):
        self.factory = AssetFactory()
        self.world = World(self.factory, seed=12345)

    def test_neighbor_tree_leaves_preserved_when_adjacent_tree_felled(self):
        """
        Creates two neighboring trees separated by 6 tiles (as in user screenshot):
        Tree 1: Trunk at x=10, y=50..56. Canopy at x=7..13, y=47..51.
        Tree 2: Trunk at x=16, y=50..56. Canopy at x=13..19, y=47..51.
        """
        # Ground
        for x in range(5, 25):
            self.world.set_tile(x, 57, TILE_GRASS)

        # Build Tree 1 (x=10)
        for y in range(50, 57):
            self.world.set_tile(10, y, TILE_WOOD_TRUNK)
        tree1_leaves = []
        for lx in range(7, 14):
            for ly in range(48, 52):
                if lx != 10 or ly < 50:
                    self.world.set_tile(lx, ly, TILE_LEAVES)
                    tree1_leaves.append((lx, ly))

        # Build Tree 2 (x=16)
        for y in range(50, 57):
            self.world.set_tile(16, y, TILE_WOOD_TRUNK)
        tree2_exclusive_leaves = []
        for lx in range(14, 20):
            for ly in range(48, 52):
                if lx != 16 or ly < 50:
                    self.world.set_tile(lx, ly, TILE_LEAVES)
                    tree2_exclusive_leaves.append((lx, ly))

        # Fell Tree 2 (bottom trunk at 16, 56)
        broken, drop, tile_id = self.world.damage_tile_at(16, 56, power=200)
        self.assertTrue(broken, "Tree 2 should be broken")
        self.assertEqual(drop, "wood")

        # Verify Tree 2 trunk is gone
        for y in range(50, 57):
            self.assertEqual(self.world.get_tile(16, y), TILE_AIR, f"Tree 2 trunk at (16, {y}) should be felled")

        # Verify Tree 2 exclusive leaves are gone
        for lx, ly in tree2_exclusive_leaves:
            self.assertEqual(self.world.get_tile(lx, ly), TILE_AIR, f"Tree 2 leaf at ({lx}, {ly}) should be felled")

        # CRITICAL VERIFICATION: Tree 1 must remain 100% INTACT!
        # Tree 1 trunk must still be standing
        for y in range(50, 57):
            self.assertEqual(self.world.get_tile(10, y), TILE_WOOD_TRUNK, f"Tree 1 trunk at (10, {y}) must remain standing")

        # Tree 1 leaves (INCLUDING the right side near Tree 2 at x=11, 12, 13) MUST NOT BE STRIPPED!
        for lx, ly in tree1_leaves:
            self.assertEqual(
                self.world.get_tile(lx, ly), TILE_LEAVES,
                f"Tree 1 leaf at ({lx}, {ly}) was incorrectly stripped when neighboring tree was felled!"
            )

        # Now fell Tree 1 as well
        broken1, drop1, _ = self.world.damage_tile_at(10, 56, power=200)
        self.assertTrue(broken1)
        self.assertEqual(drop1, "wood")

        # Verify Tree 1 trunk is now gone
        for y in range(50, 57):
            self.assertEqual(self.world.get_tile(10, y), TILE_AIR)

        # Verify Tree 1 leaves are now cleanly felled
        for lx, ly in tree1_leaves:
            self.assertEqual(self.world.get_tile(lx, ly), TILE_AIR, f"Tree 1 leaf at ({lx}, {ly}) should now be cleared")


if __name__ == "__main__":
    unittest.main()
