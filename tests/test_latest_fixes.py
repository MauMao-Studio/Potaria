"""
Test suite verifying the latest 8 bug fixes, balancing overhauls, and gameplay mechanics.
"""

import math
import random
import unittest
import pygame

from src.constants import (
    SCALED_TILE,
    TILE_AIR, TILE_DIRT, TILE_GRASS, TILE_STONE, TILE_WATER,
    TILE_WOOD_TRUNK, TILE_WOOD, TILE_LEAVES, WALL_AIR, WALL_DIRT,
    RARITY_COMMON, RARITY_UNCOMMON, RARITY_RARE, RARITY_EPIC, RARITY_MYTHIC, RARITY_LEGENDARY
)
from src.assets.asset_factory import AssetFactory
from src.world.world import World
from src.world.chunk_manager import ChunkManager, ChunkSection, CHUNK_WIDTH, SECTION_HEIGHT
from src.world.lighting import LightingEngine
from src.combat.combat_system import CombatManager
from src.entities.player import Player
from src.entities.mob import GreenSlime, NightEliteMob
from src.entities.boss import IgnisColossus, CryoSpud, NecroTuber, LordMalus
from src.ui.inventory import Inventory, ItemStack, ITEM_REGISTRY
from src.ui.crafting import RECIPES
from src.audio.sound_effects import SoundManager
from src.entities.particle import ParticleSystem
from src.camera import Camera
from main import PotariaGame


class TestLatestFixes(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pygame.init()
        cls.factory = AssetFactory()
        cls.sound = SoundManager()

    def setUp(self):
        self.particles = ParticleSystem()
        self.camera = Camera(800, 600)
        self.world = World(self.factory, seed=12345)
        self.combat = CombatManager(self.factory, self.sound, self.particles, self.camera)
        self.player = Player(200, 200, self.factory, self.sound)

    # 1. ChunkManager Crash Fix & Background Wall Sky Artifact Fix
    def test_chunk_manager_section_bake_and_no_sky_walls(self):
        cm = self.world.chunk_manager
        cm.ensure_chunks_in_range(0, 1)
        chunk = cm.chunks[0]

        # Verify chunk section bake does not raise NameError
        sec = ChunkSection(0, 0)
        sec.bake(self.world)
        self.assertIsNotNone(sec.surf)

        # Verify no background walls placed above surface level
        for lx in range(CHUNK_WIDTH):
            surf_y = chunk.surface_heights[lx]
            for ty in range(0, surf_y):
                w_id = chunk.walls[lx][ty]
                self.assertEqual(w_id, WALL_AIR, f"Sky wall detected at lx={lx}, ty={ty} (surf_y={surf_y})")

    # 2. Player Illumination & Soft Shadowless Radial Lighting
    def test_player_illumination_no_shadow_casting(self):
        le = LightingEngine(800, 600)
        
        # Surround light emitter with solid wall
        self.world.set_tile(15, 15, TILE_AIR)
        self.world.set_tile(16, 15, TILE_STONE)
        self.world.set_tile(17, 15, TILE_AIR)

        # When cast_shadow=False (normal player radial light), light penetrates block without casting hard shadow
        le.compute_viewport_light(self.world, min_tx=5, min_ty=5, max_tx=25, max_ty=25, ambient_sunlight=0, torch_positions=[(15, 15, 11, 7, False)])
        l_behind = le.get_light_level(17, 15)
        self.assertGreater(l_behind, 0, "Shadowless player light must illuminate radially past obstacles!")

    # 3. Bow & Crossbow Ammo Requirement
    def test_bow_and_crossbow_strictly_require_ammo(self):
        game = PotariaGame()

        # Verdant Bramble Crossbow with 0 arrows should fail to fire
        game.inventory.slots[0] = ItemStack("verdant_bramble_crossbow", 1)
        game.inventory.slots[1] = None
        game.inventory.selected_slot = 0
        game.player.attack_cooldown = 0.0

        res = game.handle_primary_action(300, 300)
        self.assertFalse(res, "Verdant Bramble Crossbow must NOT fire with 0 arrows!")

        # With wooden arrows, it should fire and consume 1 arrow
        game.inventory.slots[1] = ItemStack("wooden_arrow", 3)
        res_fired = game.handle_primary_action(300, 300)
        self.assertTrue(res_fired, "Crossbow must fire when arrows are present!")
        self.assertEqual(game.inventory.count_item("wooden_arrow"), 2)

        # Ancient composite bow is unique: channels astral arrows when quiver empty
        game.inventory.slots[0] = ItemStack("ancient_composite_bow", 1)
        game.inventory.slots[1] = None
        game.player.attack_cooldown = 0.0
        res_ancient = game.handle_primary_action(300, 300)
        self.assertTrue(res_ancient, "Ancient composite bow channels astral arrows when empty!")

    # 4. Tiered Fishing Rods Functionality & Crafting
    def test_tiered_fishing_rods_and_crafting(self):
        rods = [
            "fishing_rod", "spud_angler_rod", "reinforced_angler_rod",
            "gilded_master_rod", "astral_leviathan_rod", "neptune_tide_rod"
        ]

        # Verify all rods exist in ITEM_REGISTRY and are marked as Fishing Tool
        for rod_id in rods:
            self.assertIn(rod_id, ITEM_REGISTRY, f"Missing fishing rod: {rod_id}")
            self.assertEqual(ITEM_REGISTRY[rod_id].get("special"), "Fishing Tool")

        # Verify crafting recipes exist for all tiered rods
        recipe_results = {r["result"] for r in RECIPES}
        for rod_id in ("spud_angler_rod", "reinforced_angler_rod", "gilded_master_rod", "astral_leviathan_rod", "neptune_tide_rod"):
            self.assertIn(rod_id, recipe_results, f"Crafting recipe missing for rod: {rod_id}")

        # Verify game handles right-click and left-click casting for all rods
        game = PotariaGame()
        ptx = int(game.player.center_x // SCALED_TILE)
        pty = int(game.player.center_y // SCALED_TILE)
        game.world.set_tile(ptx + 2, pty, TILE_WATER)
        screen_x, screen_y = game.camera.world_to_screen((ptx + 2) * SCALED_TILE + 16, pty * SCALED_TILE + 16)

        for rod_id in rods:
            game.inventory.slots[0] = ItemStack(rod_id, 1)
            game.inventory.selected_slot = 0
            game.fishing_bobber = None

            # Test primary action cast
            res = game.handle_primary_action(screen_x, screen_y)
            self.assertTrue(res, f"Failed to cast with {rod_id} via primary action")
            self.assertIsNotNone(game.fishing_bobber)

            # Test reel / catch resolution
            game.fishing_bobber["state"] = "bite"
            res_bite = game.handle_fishing_action(screen_x, screen_y)
            self.assertTrue(res_bite, f"Failed to reel with {rod_id}")
            self.assertTrue(game.fishing_minigame.is_active)
            game.fishing_minigame.cancel()

    # 5. Enemy Drop Rate Tuning & Rarity Rules
    def test_enemy_drop_rate_tuning_and_rarity_rules(self):
        random.seed(999)
        mob = GreenSlime(200, 200, self.factory)

        # Over 500 kills with tuned=True, regular mobs must drop 0-2 items, Common/Uncommon/Rare only
        disallowed_rarities = {"epic", "mythic", "legendary", "ancient"}
        counts = []
        for _ in range(500):
            self.combat.dropped_items.clear()
            self.combat._drop_mob_loot(mob, tuned=True)
            drop_len = len(self.combat.dropped_items)
            self.assertIn(drop_len, (0, 1, 2), f"Regular mob dropped {drop_len} items (must be 0-2)")
            counts.append(drop_len)

            for drop in self.combat.dropped_items:
                r = ITEM_REGISTRY.get(drop.item_id, {}).get("rarity")
                self.assertNotIn(r, disallowed_rarities, f"Regular mob dropped high-tier rarity item: {drop.item_id} ({r})")

        self.assertTrue(any(c == 0 for c in counts), "Regular mobs should sometimes drop 0 items")
        self.assertTrue(any(c > 0 for c in counts), "Regular mobs should sometimes drop loot")

        # Night Elites drop up to Epic, never Mythic/Legendary/Ancient
        elite = NightEliteMob(200, 200, self.factory)
        for _ in range(200):
            self.combat.dropped_items.clear()
            self.combat._drop_mob_loot(elite, tuned=True)
            for drop in self.combat.dropped_items:
                r = ITEM_REGISTRY.get(drop.item_id, {}).get("rarity")
                self.assertNotIn(r, {"mythic", "legendary", "ancient"}, f"Night Elite dropped mythic/legendary item: {drop.item_id}")

        # Dungeon Mini-Bosses guarantee exactly 1 Epic or Legendary drop per victory
        mini_bosses = [
            IgnisColossus(500, 300, self.factory, self.sound),
            CryoSpud(500, 300, self.factory, self.sound),
            NecroTuber(500, 300, self.factory, self.sound),
            LordMalus(500, 300, self.factory, self.sound),
        ]
        for boss in mini_bosses:
            self.combat.boss = boss
            self.combat.boss.hp = 0
            self.combat.boss.is_dead = True
            self.combat.dropped_items.clear()
            self.combat.update(0.016, self.world, self.player)

            epic_leg_drops = [
                d for d in self.combat.dropped_items
                if ITEM_REGISTRY.get(d.item_id, {}).get("rarity") in ("epic", "legendary")
            ]
            self.assertEqual(len(epic_leg_drops), 1, f"Boss {boss.name} dropped {len(epic_leg_drops)} Epic/Legendary items instead of exactly 1!")

    # 6. Tree Mining Single-Block & Minecraft-Style Tree Decay
    def test_tree_mining_single_block_and_decay(self):
        self.world.tree_cascade_felling = False
        tx, ty = 10, 20
        # Place mini tree
        self.world.set_tile(tx, ty, TILE_WOOD_TRUNK)
        self.world.set_tile(tx, ty - 1, TILE_WOOD_TRUNK)
        self.world.set_tile(tx, ty - 2, TILE_LEAVES)

        # Mining bottom trunk breaks ONLY the bottom trunk
        broken, drop, tid = self.world.damage_tile_at(tx, ty, 100)
        self.assertTrue(broken)
        self.assertEqual(drop, "wood")
        self.assertEqual(self.world.get_tile(tx, ty), TILE_AIR)

        # Upper trunk and leaves are still in the world, now registered in decaying_blocks
        self.assertEqual(self.world.get_tile(tx, ty - 1), TILE_WOOD_TRUNK)
        self.assertEqual(self.world.get_tile(tx, ty - 2), TILE_LEAVES)
        self.assertIn((tx, ty - 1), self.world.decaying_blocks)

        # Fast forward decay
        game = PotariaGame()
        game.world = self.world
        self.world.update_tree_decay(10.0, game=game)
        # Upper trunk and leaves have now decayed to air
        self.assertEqual(self.world.get_tile(tx, ty - 1), TILE_AIR)
        self.assertEqual(self.world.get_tile(tx, ty - 2), TILE_AIR)

    def test_natural_grounded_tree_decay_when_chopped(self):
        self.world.tree_cascade_felling = False
        # Tree standing on solid dirt/grass ground
        gx, gy = 30, 50
        self.world.set_tile(gx, gy + 1, TILE_GRASS)  # Solid ground beneath
        self.world.set_tile(gx, gy, TILE_WOOD_TRUNK)    # Base trunk
        self.world.set_tile(gx, gy - 1, TILE_WOOD_TRUNK) # Mid trunk
        self.world.set_tile(gx, gy - 2, TILE_WOOD_TRUNK) # Top trunk
        self.world.set_tile(gx, gy - 3, TILE_LEAVES)     # Canopy leaf

        # Chop base trunk at (gx, gy)
        broken, drop, tid = self.world.damage_tile_at(gx, gy, 100)
        self.assertTrue(broken)
        self.assertEqual(self.world.get_tile(gx, gy), TILE_AIR)

        # Severed mid and top trunks must be decaying even though solid grass is at gy + 1
        self.assertIn((gx, gy - 1), self.world.decaying_blocks)
        self.assertIn((gx, gy - 2), self.world.decaying_blocks)
        self.assertIn((gx, gy - 3), self.world.decaying_blocks)

        # Chop leaves directly
        leaf_x, leaf_y = 40, 50
        self.world.set_tile(leaf_x, leaf_y, TILE_LEAVES)
        broken, drop, tid = self.world.damage_tile_at(leaf_x, leaf_y, 100)
        self.assertTrue(broken)
        self.assertEqual(drop, "leaves")
        self.assertEqual(self.world.get_tile(leaf_x, leaf_y), TILE_AIR)


if __name__ == "__main__":
    unittest.main()
