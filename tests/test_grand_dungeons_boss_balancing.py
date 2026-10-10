"""
Potaria - Unit and Integration Tests:
1. Indestructible Dungeon Tiles & Gateway Blocks (can_mine_tile == False)
2. Minimap Underground Fog of War (Unlit cavern tiles are pitch black (0, 0, 0))
3. Boss Health Scaling, Innate Armor & Anti-Burst Damage Clamp (max 4.5% max HP)
4. Slaying All 4 Biome Mini-Bosses Triggers Sky Citadel Warp & Sol-Rho Spawn
5. Death Penalty: Boss defeat clears inventory & equipment, retains level & skills
6. Grand Boss Sol-Rho Victory: Retain items, increment rematch cycle, double stats, duo-boss summons

Developer: Kurados | Pure Python + pygame-ce (100% offline)
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"

import pygame
from main import PotariaGame
from src.constants import (
    SCALED_TILE, TILE_AIR, TILE_DIRT, TILE_TORCH,
    TILE_BEDROCK, TILE_DUNGEON_BRICK, TILE_DUNGEON_ALTAR,
    TILE_DUNGEON_MAGMA, TILE_DUNGEON_ICE, TILE_DUNGEON_BONE,
    TILE_DUNGEON_GATE
)
from src.ui.minimap import TILE_MAP_COLORS
from src.assets.asset_factory import AssetFactory
from src.audio.sound_effects import SoundManager
from src.entities.boss import (
    LordMalus, IgnisColossus, CryoSpud, NecroTuber, GrandBossSolRho
)


class TestGrandDungeonsAndBossBalancing(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pygame.init()
        cls.asset_factory = AssetFactory()
        cls.sound_manager = SoundManager()

    def setUp(self):
        self.game = PotariaGame()
        self.game.combat.mobs.clear()
        self.game.combat.boss = None
        self.game.combat.secondary_boss = None
        self.game.combat.boss_defeated = False
        self.game.combat.grand_boss_defeated = False
        self.game.combat.dropped_items.clear()
        self.game.combat.damage_numbers.clear()
        self.game.combat.rematch_cycle = 0
        self.game.combat.rematch_multiplier = 1.0
        for k in self.game.combat.defeated_mini_bosses:
            self.game.combat.defeated_mini_bosses[k] = False

    # =========================================================================
    # 1. INDESTRUCTIBLE DUNGEON TILES & GATES
    # =========================================================================
    def test_dungeon_tiles_are_strictly_indestructible(self):
        """Dungeon bricks, biome variants, gates, and altars cannot be broken or mined under any circumstance."""
        dungeon_tiles = [
            TILE_BEDROCK,
            TILE_DUNGEON_BRICK,
            TILE_DUNGEON_MAGMA,
            TILE_DUNGEON_ICE,
            TILE_DUNGEON_BONE,
            TILE_DUNGEON_GATE,
            TILE_DUNGEON_ALTAR,
        ]
        tx, ty = 25, 180
        for dt_id in dungeon_tiles:
            self.game.world.set_tile(tx, ty, dt_id)
            self.assertFalse(
                self.game.world.can_mine_tile(tx, ty),
                f"Dungeon tile ID {dt_id} must NOT be mineable!"
            )
            broken, drop_item, final_id = self.game.world.damage_tile_at(tx, ty, power=99999)
            self.assertFalse(broken, f"Dungeon tile ID {dt_id} must NOT break under extreme mining power!")
            self.assertEqual(final_id, dt_id)

    # =========================================================================
    # 2. MINIMAP FOG OF WAR
    # =========================================================================
    def test_minimap_fog_of_war_pitch_black_without_light(self):
        """Underground cavern tiles outside player reach and without torches are pitch black (0, 0, 0)."""
        minimap = self.game.hud.minimap
        minimap.is_open = True
        minimap.mode = "corner"
        minimap.mark_dirty()

        # Position player underground at (10, 100)
        self.game.player.x = 10 * SCALED_TILE
        self.game.player.y = 100 * SCALED_TILE
        self.game.player._current_held_id = None
        self.game.player.is_holding_torch = False

        # Set a dirt tile 20 tiles away at (30, 100), well beyond player reach (5 tiles)
        target_tx, target_ty = 30, 100
        self.game.world.set_tile(target_tx, target_ty, TILE_DIRT)

        # Render minimap
        dummy_surf = pygame.Surface((1280, 720))
        minimap.render(dummy_surf, self.game.world, self.game.player, self.game.combat)

        # Coordinates on minimap surface for (30, 100)
        ptx = int(self.game.player.center_x // SCALED_TILE)
        pty = int(self.game.player.center_y // SCALED_TILE)
        min_tx = ptx - minimap.grid_w // 2
        min_ty = pty - minimap.grid_h // 2
        lx = target_tx - min_tx
        ly = target_ty - min_ty

        pixel_color = minimap.map_surf.get_at((lx, ly))[:3]
        self.assertEqual(pixel_color, (0, 0, 0), "Unlit underground tile must be pitch black (0, 0, 0) in Fog of War!")

        # Now place a torch next to target tile
        self.game.world.set_tile(target_tx - 1, target_ty, TILE_TORCH)
        minimap.mark_dirty()
        minimap.render(dummy_surf, self.game.world, self.game.player, self.game.combat)

        illuminated_color = minimap.map_surf.get_at((lx, ly))[:3]
        expected_color = TILE_MAP_COLORS[TILE_DIRT]
        self.assertEqual(illuminated_color, expected_color, "Torched underground tile must be illuminated on minimap!")

    # =========================================================================
    # 3. BOSS HEALTH SCALING & ANTI-BURST DAMAGE CLAMP
    # =========================================================================
    def test_mini_boss_anti_burst_damage_clamp(self):
        """Mini-Boss caps single-strike damage to at most 4.5% of max HP to prevent instant-melting."""
        malus = LordMalus(0, 0, self.asset_factory, self.sound_manager)
        initial_hp = malus.hp
        # Max damage allowed per hit: max(15, int(5200 * 0.045)) = 234
        max_allowed_dmg = int(malus.max_hp * 0.045)

        # Player tries to cheat with 99,999 burst damage
        malus.take_damage(99999)
        damage_taken = initial_hp - malus.hp
        self.assertLessEqual(damage_taken, max_allowed_dmg)
        self.assertEqual(damage_taken, max_allowed_dmg)

    def test_grand_boss_anti_burst_damage_clamp(self):
        """Grand Boss Sol-Rho caps single-strike damage to at most 4.5% of max HP."""
        sol = GrandBossSolRho(0, 0, self.asset_factory, self.sound_manager, party_size=1)
        initial_hp = sol.hp
        # Max allowed damage: int(14000 * 0.045) = 630
        max_allowed_dmg = int(sol.max_hp * 0.045)

        sol.take_damage(999999)
        damage_taken = initial_hp - sol.hp
        self.assertLessEqual(damage_taken, max_allowed_dmg)
        self.assertEqual(damage_taken, max_allowed_dmg)

    # =========================================================================
    # 4. SLAYING ALL 4 MINI-BOSSES WARPS TO SKY CITADEL & SPAWNS SOL-RHO
    # =========================================================================
    def test_slaying_four_mini_bosses_warps_player_to_sky_citadel(self):
        """Defeating all 4 biome mini-bosses in the current cycle teleports player to Sky Citadel and spawns Sol-Rho."""
        combat = self.game.combat
        player = self.game.player
        world = self.game.world

        mini_boss_types = ["lord_malus", "ignis_colossus", "cryo_spud", "necro_tuber"]
        for idx, b_type in enumerate(mini_boss_types):
            combat.spawn_boss(0, 0, boss_cls=b_type, player=player)
            self.assertIsNotNone(combat.boss)
            # Slay boss
            combat.boss.hp = 0
            combat.boss.is_dead = True
            combat.update(0.016, world, player)

            if idx < 3:
                # Still remaining mini-bosses to slay
                self.assertFalse(all(combat.defeated_mini_bosses.values()))
                self.assertIsNone(combat.boss)
            else:
                # 4th mini-boss slain! Should trigger Sky Citadel warp & Sol-Rho spawn!
                self.assertTrue(all(combat.defeated_mini_bosses.values()))
                self.assertIsNotNone(combat.boss)
                self.assertEqual(combat.boss.boss_type, "grand_boss_sol_rho")
                # Player warped to Sky Citadel (y = 28 * SCALED_TILE)
                self.assertEqual(player.x, 0.0)
                self.assertEqual(player.y, 28 * SCALED_TILE)

    # =========================================================================
    # 5. DEATH PENALTY BY BOSS
    # =========================================================================
    def test_boss_death_clears_inventory_and_equipment_retains_level_and_skills(self):
        """If killed during a boss fight, all inventory and equipment is wiped, but level and skills are retained."""
        player = self.game.player
        inventory = self.game.inventory
        equipment = player.equipment

        # Grant player items and gear
        inventory.add_item("wooden_sword", count=1)
        inventory.add_item("potion_health", count=5)
        self.assertFalse(inventory.is_empty())

        equipment.equip("copper_helmet", player.stats)
        equipment.equip("copper_chestplate", player.stats)
        self.assertTrue(any(v is not None for v in equipment.slots.values()))

        # Grant level 15 and skills
        player.stats.level = 15
        player.stats.current_exp = 450
        player.skills.learned_skills.add("meteor")

        # Player enters boss fight and dies
        player.in_boss_fight = True
        player.take_damage(9999)
        self.assertTrue(player.is_dead)
        self.assertTrue(player.killed_by_boss)

        # Trigger respawn timer expiration
        player.update(3.5, self.game.world)
        self.assertFalse(player.is_dead)

        # Inventory and equipment MUST be empty
        self.assertTrue(inventory.is_empty(), "Carried inventory items must be wiped on boss defeat!")
        self.assertTrue(all(v is None for v in equipment.slots.values()), "Equipped gear must be wiped on boss defeat!")

        # Levels and skills MUST be retained
        self.assertEqual(player.stats.level, 15, "Player level must be preserved!")
        self.assertEqual(player.stats.current_exp, 450, "Player EXP must be preserved!")
        self.assertIn("meteor", player.skills.learned_skills, "Learned skills must be preserved!")

    # =========================================================================
    # 6. GRAND BOSS VICTORY & REMATCH SCALING
    # =========================================================================
    def test_grand_boss_victory_retains_items_increments_cycle_and_doubles_stats(self):
        """Victory over Sol-Rho preserves all items, increments rematch cycle, doubles mini-boss stats, and summons duo."""
        combat = self.game.combat
        player = self.game.player
        inventory = self.game.inventory

        # Player has valuable loot
        inventory.add_item("celestial_emblem", count=1)
        inventory.add_item("gold_coin", count=50)

        # Spawn Sol-Rho
        combat.spawn_grand_boss(0, 0, player=player)
        self.assertEqual(combat.rematch_cycle, 0)
        self.assertEqual(combat.rematch_multiplier, 1.0)

        # Defeat Sol-Rho Phase 2
        sol = combat.boss
        sol.phase = 2
        sol.hp = 0
        sol.is_dead = True
        sol.grand_boss_defeated = True

        combat.update(0.016, self.game.world, player)

        # Player retains all items!
        self.assertEqual(inventory.count_item("celestial_emblem"), 1)
        self.assertEqual(inventory.count_item("gold_coin"), 50)

        # Rematch cycle incremented to 1, stats doubled
        self.assertEqual(combat.rematch_cycle, 1)
        self.assertEqual(combat.rematch_multiplier, 2.0)
        self.assertFalse(any(combat.defeated_mini_bosses.values()), "Mini-boss flags reset for new cycle!")

        # Mini-boss stats in rematch cycle 1 have 2.0x multiplier
        rematch_malus = LordMalus(0, 0, self.asset_factory, self.sound_manager)
        rematch_malus.scale_to_player(player.stats.level, getattr(player.stats, "total_atk", 0),
                                      rematch_multiplier=combat.rematch_multiplier)
        self.assertGreaterEqual(rematch_malus.max_hp, 5200 * 2)

        # When challenging Grand Boss in rematch cycle >= 1, a duo secondary boss is summoned!
        combat.spawn_grand_boss(0, 0, player=player)
        self.assertIsNotNone(combat.boss)
        self.assertIsNotNone(combat.secondary_boss, "Rematch fight must summon a secondary mini-boss alongside Sol-Rho!")


if __name__ == "__main__":
    unittest.main()
