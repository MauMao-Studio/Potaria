"""
Unit & Integration Tests for Carved Tuber Lantern Ceiling Placement & World Rename
Tests:
1. Carved Tuber Lantern (and Brass/Spectral Lantern) places its dedicated tile (NOT Torch).
2. Ceiling hanging placement when a solid block is to the North (ty - 1).
3. Mining Carved Tuber Lantern drops 'carved_tuber_lantern' (NOT 'torch').
4. Breaking the supporting North ceiling block detaches the hanging lantern.
5. Renaming a created world in World Selection succeeds for unique names and strictly rejects already-existing world names.
Developer: Kurados
"""

import os
import json
import shutil
import tempfile
import unittest
import pygame

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

from src.constants import (
    TILE_AIR, TILE_STONE, TILE_TORCH, TILE_WATER,
    TILE_CARVED_TUBER_LANTERN, TILE_BRASS_LANTERN, TILE_SPECTRAL_LANTERN,
    TILE_PROPS, WALL_AIR, WALL_WOOD, STATE_WORLDS
)
from src.assets.asset_factory import AssetFactory
from src.ui.inventory import ITEM_REGISTRY, ITEM_ALIASES, ItemStack
from src.world.world import World
import src.world.save_manager as save_manager
from src.ui.menu import MenuManager


class DummySoundManager:
    def play(self, *args, **kwargs):
        pass

    def set_volumes(self, *args, **kwargs):
        pass


class TestLanternAndWorldRename(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pygame.init()
        pygame.display.set_mode((1, 1))
        cls.af = AssetFactory()

    def test_carved_tuber_lantern_uses_dedicated_tile_not_torch(self):
        """Verifies Carved Tuber Lantern places TILE_CARVED_TUBER_LANTERN (not TILE_TORCH) and drops carved_tuber_lantern."""
        self.assertIn("carved_tuber_lantern", ITEM_REGISTRY)
        self.assertEqual(ITEM_ALIASES.get("curved_tuber_lantern"), "carved_tuber_lantern")

        lantern_data = ITEM_REGISTRY["carved_tuber_lantern"]
        self.assertEqual(lantern_data["tile"], TILE_CARVED_TUBER_LANTERN)
        self.assertNotEqual(lantern_data["tile"], TILE_TORCH)

        # Verify ItemStack resolves curved_tuber_lantern alias to TILE_CARVED_TUBER_LANTERN
        stack = ItemStack("curved_tuber_lantern", 1)
        self.assertEqual(stack.data.get("tile"), TILE_CARVED_TUBER_LANTERN)

        # Verify TILE_PROPS drop and light emission
        props = TILE_PROPS[TILE_CARVED_TUBER_LANTERN]
        self.assertEqual(props["drop"], "carved_tuber_lantern")
        self.assertGreaterEqual(props["light_emit"], 14)
        self.assertFalse(props["solid"])

        # Verify distinct 16x16 world tile texture exists in AssetFactory
        self.assertIn(TILE_CARVED_TUBER_LANTERN, self.af.tiles)
        self.assertIn(TILE_BRASS_LANTERN, self.af.tiles)
        self.assertIn(TILE_SPECTRAL_LANTERN, self.af.tiles)

    def test_lantern_ceiling_north_block_placement_and_mining(self):
        """Verifies Carved Tuber Lantern can be placed at the ceiling when there is a solid block to the North (ty - 1)."""
        world = World(self.af, seed=12345)
        tx, ty = 10, 20

        # Clear area around (tx, ty) in open air (above surface)
        for dx in range(-2, 3):
            for dy in range(-2, 3):
                world.set_tile(tx + dx, ty + dy, TILE_AIR)
                world.place_wall(tx + dx, ty + dy, WALL_AIR)

        # 1. Cannot place in open mid-air with no support
        self.assertFalse(world.place_tile(tx, ty, TILE_CARVED_TUBER_LANTERN))

        # 2. Cannot place with only a side block (left/right) and no North ceiling, floor, or wall
        world.set_tile(tx - 1, ty, TILE_STONE)
        self.assertFalse(world.place_tile(tx, ty, TILE_CARVED_TUBER_LANTERN))
        world.set_tile(tx - 1, ty, TILE_AIR)

        # 3. Place a solid ceiling block to the North (tx, ty - 1)
        world.set_tile(tx, ty - 1, TILE_STONE)
        placed = world.place_tile(tx, ty, TILE_CARVED_TUBER_LANTERN)
        self.assertTrue(placed, "Carved Tuber Lantern must be placeable on a ceiling when a solid block is to the North (ty - 1)")
        self.assertEqual(world.get_tile(tx, ty), TILE_CARVED_TUBER_LANTERN)

        # 4. Mining the placed Carved Tuber Lantern drops 'carved_tuber_lantern' (not 'torch')
        destroyed, drop, broken_tid = world.damage_tile_at(tx, ty, power=100)
        self.assertTrue(destroyed)
        self.assertEqual(broken_tid, TILE_CARVED_TUBER_LANTERN)
        self.assertEqual(drop, "carved_tuber_lantern")
        self.assertEqual(world.get_tile(tx, ty), TILE_AIR)

        # 5. Re-hang lantern from North ceiling block, then break the North ceiling block -> lantern detaches
        self.assertTrue(world.place_tile(tx, ty, TILE_CARVED_TUBER_LANTERN))
        self.assertEqual(world.get_tile(tx, ty), TILE_CARVED_TUBER_LANTERN)
        world.damage_tile_at(tx, ty - 1, power=500)
        self.assertEqual(world.get_tile(tx, ty - 1), TILE_AIR)
        self.assertEqual(world.get_tile(tx, ty), TILE_AIR, "Lantern must detach if its North ceiling block is broken and no other support exists")

    def test_rename_world_and_reject_existing_names(self):
        """Verifies renaming a created world works and strictly blocks renaming to an already-existing world name."""
        temp_saves = tempfile.mkdtemp(prefix="potaria_rename_test_")
        orig_saves_dir = save_manager.SAVES_DIR
        try:
            save_manager.SAVES_DIR = temp_saves

            # Create two saved worlds: "Alpha World" and "Beta World"
            alpha_dir = os.path.join(temp_saves, "Alpha World")
            beta_dir = os.path.join(temp_saves, "Beta World")
            os.makedirs(alpha_dir, exist_ok=True)
            os.makedirs(beta_dir, exist_ok=True)

            with open(os.path.join(alpha_dir, "world.json"), "w", encoding="utf-8") as f:
                json.dump({"world_name": "Alpha World", "seed": 111, "timestamp": 1000}, f)
            with open(os.path.join(beta_dir, "world.json"), "w", encoding="utf-8") as f:
                json.dump({"world_name": "Beta World", "seed": 222, "timestamp": 2000}, f)

            # 1. Cannot rename "Alpha World" to existing "Beta World" (exact or case-insensitive)
            self.assertFalse(save_manager.rename_world("Alpha World", "Beta World"))
            self.assertFalse(save_manager.rename_world("Alpha World", "beta world"))
            # Cannot rename to its own existing name
            self.assertFalse(save_manager.rename_world("Alpha World", "Alpha World"))
            # Cannot rename to empty string
            self.assertFalse(save_manager.rename_world("Alpha World", "   "))

            # Verify both worlds are untouched
            worlds_before = {w["name"] for w in save_manager.list_saved_worlds()}
            self.assertEqual(worlds_before, {"Alpha World", "Beta World"})

            # 2. Rename "Alpha World" to a new unique name "Gamma Realm"
            self.assertTrue(save_manager.rename_world("Alpha World", "Gamma Realm"))
            worlds_after = {w["name"] for w in save_manager.list_saved_worlds()}
            self.assertEqual(worlds_after, {"Gamma Realm", "Beta World"})
            self.assertFalse(os.path.exists(os.path.join(temp_saves, "Alpha World")))
            self.assertTrue(os.path.exists(os.path.join(temp_saves, "Gamma Realm", "world.json")))

            # 3. Verify MenuManager UI rename workflow in STATE_WORLDS
            menu = MenuManager(self.af, DummySoundManager())
            menu.state = STATE_WORLDS
            menu._refresh_saved_worlds()
            self.assertEqual(len(menu.world_rename_buttons), 2)

            # Click RENAME button on the first world entry ("Beta World", since timestamp 2000 > 1000)
            ren_btn, winfo = menu.world_rename_buttons[0]
            self.assertEqual(winfo["name"], "Beta World")
            menu.handle_click(ren_btn.rect.center)
            self.assertEqual(menu.renaming_world_target, "Beta World")

            # Attempt to rename "Beta World" to existing "Gamma Realm" via Menu UI
            menu.rename_world_input = "Gamma Realm"
            menu.handle_click(menu.rename_confirm_btn.rect.center)
            self.assertEqual(menu.renaming_world_target, "Beta World")
            self.assertIn("already exists", menu.rename_error_msg.lower())

            # Rename "Beta World" to unique "Omega Spud" via Menu UI
            menu.rename_world_input = "Omega Spud"
            menu.handle_click(menu.rename_confirm_btn.rect.center)
            self.assertIsNone(menu.renaming_world_target)
            self.assertEqual(menu.rename_error_msg, "")

            final_worlds = {w["name"] for w in save_manager.list_saved_worlds()}
            self.assertEqual(final_worlds, {"Gamma Realm", "Omega Spud"})
        finally:
            save_manager.SAVES_DIR = orig_saves_dir
            shutil.rmtree(temp_saves, ignore_errors=True)


if __name__ == "__main__":
    unittest.main()
