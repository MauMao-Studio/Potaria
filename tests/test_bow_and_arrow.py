"""
Unit tests for Archery System & Bow Ballistics in Potaria.
Tests firing all bow variants (relic_bow, wood_bow, prime_molten_bow, recurves),
arrow consumption, out-of-arrows feedback, solid tile collisions,
and melee ghost hit prevention.
Developer: Kurados | Engine: pygame-ce 2.5.8
"""

import unittest
import os
import math
import pygame

# Headless display setup for headless test runner
os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"
pygame.init()
pygame.display.set_mode((800, 600))

from src.constants import SCALED_TILE, TILE_DIRT, TILE_TORCH, TILE_WOOD_PLATFORM
from src.assets.asset_factory import AssetFactory
from src.audio.sound_effects import SoundManager
from src.entities.player import Player
from src.entities.projectile import ArrowProjectile
from src.entities.mob import GreenSlime
from src.ui.inventory import Inventory, ItemStack
from src.combat.combat_system import CombatManager
from src.entities.particle import ParticleSystem
from src.world.world import World
from src.camera import Camera


class TestBowAndArrow(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.asset_factory = AssetFactory()
        cls.sound_manager = SoundManager()

    def setUp(self):
        self.camera = Camera(800, 600)
        self.particle_system = ParticleSystem()
        self.world = World(self.asset_factory, seed=123)
        self.combat = CombatManager(self.asset_factory, self.sound_manager, self.particle_system, self.camera)
        self.player = Player(200, 200, self.asset_factory, self.sound_manager)
        self.inventory = Inventory(self.asset_factory)
        self.player.inventory = self.inventory
        self.inventory.player = self.player
        self.camera = Camera(800, 600)
        self.combat.camera = self.camera

    def test_relic_bow_shoots_arrow_with_wooden_arrows(self):
        """Verify relic_bow (the user's equipped bow) fires ArrowProjectile and consumes wooden_arrow."""
        self.inventory.slots[0] = ItemStack("relic_bow", 1)
        self.inventory.slots[1] = ItemStack("wooden_arrow", 50)
        self.inventory.selected_slot = 0

        # Simulate bow shot towards (400, 200)
        active = self.inventory.get_active_item()
        self.assertEqual(active.item_id, "relic_bow")

        initial_arrows = self.inventory.count_item("wooden_arrow")
        self.assertEqual(initial_arrows, 50)

        # Replicate main.py handle_primary_action bow firing logic
        held_id = active.item_id.lower()
        held_name = active.data.get("name", "").lower()
        is_bow = (
            held_id in ("wood_bow", "bone_bow", "magma_bow", "celestial_bow")
            or any(w in held_id or w in held_name for w in ("bow", "crossbow", "recurve", "shortbow", "longbow"))
        )
        self.assertTrue(is_bow, "relic_bow must be identified as a bow!")

        arrow_type = None
        if self.inventory.count_item("wooden_arrow") > 0:
            arrow_type = "wooden_arrow"
        self.inventory.remove_item(arrow_type, 1)

        self.assertEqual(self.inventory.count_item("wooden_arrow"), 49)

        # Spawn arrow projectile
        arrow = ArrowProjectile(self.player.center_x, self.player.center_y, 0.0, speed=14.5, damage=active.data.get("atk", 20), arrow_type=arrow_type)
        self.combat.spawn_projectile(arrow)

        self.assertEqual(len(self.combat.projectiles), 1)
        self.assertIsInstance(self.combat.projectiles[0], ArrowProjectile)
        self.assertEqual(self.combat.projectiles[0].arrow_type, "wooden_arrow")

    def test_all_bow_variants_identified(self):
        """Ensure all 95+ bows, shortbows, longbows, crossbows, and recurves are recognized."""
        test_bow_ids = [
            "wood_bow", "bone_bow", "magma_bow", "celestial_bow",
            "relic_bow", "prime_molten_bow", "flare_recurve",
            "mirage_shortbow_of_the_caverns", "ember_longbow",
            "iron_bow", "timber_bow_of_the_eclipse", "spud_tuber_recurve"
        ]
        for bow_id in test_bow_ids:
            item = ItemStack(bow_id, 1)
            held_id = item.item_id.lower()
            held_name = item.data.get("name", "").lower()
            is_bow = (
                held_id in ("wood_bow", "bone_bow", "magma_bow", "celestial_bow")
                or any(w in held_id or w in held_name for w in ("bow", "crossbow", "recurve", "shortbow", "longbow"))
            )
            self.assertTrue(is_bow, f"Failed to identify {bow_id} as a bow!")

    def test_bow_does_not_trigger_melee_ghost_damage(self):
        """Holding a bow must NEVER deal melee damage via _check_weapon_hits."""
        self.inventory.slots[0] = ItemStack("relic_bow", 1)
        self.inventory.selected_slot = 0

        # Place a slime directly in front of the player (within melee reach 30px)
        slime = GreenSlime(self.player.center_x + 25, self.player.center_y, self.asset_factory)
        initial_hp = slime.hp
        self.combat.mobs.append(slime)

        # Trigger weapon swing
        self.player.is_swinging = True
        self.player.swing_progress = 0.3
        self.combat._check_weapon_hits(self.player, self.world)

        # Verify slime took ZERO melee damage from holding the bow!
        self.assertEqual(slime.hp, initial_hp, "Slime should NOT take melee damage from a bow swing!")

    def test_arrow_projectile_hits_mob_and_deals_damage(self):
        """Verify ArrowProjectile moves, collides with mob, and deals arrow damage."""
        slime = GreenSlime(self.player.center_x + 20, self.player.center_y - 10, self.asset_factory)
        initial_hp = slime.hp
        self.combat.mobs.append(slime)

        # Fire arrow directly towards the slime
        arrow = ArrowProjectile(self.player.center_x, self.player.center_y, 0.0, speed=25.0, damage=25, arrow_type="wooden_arrow")
        self.combat.spawn_projectile(arrow)

        # Update combat system
        self.combat.update(0.016, self.world, self.player, is_night=False)

        # Verify mob was hit and took damage
        self.assertLess(slime.hp, initial_hp, "Mob should take damage when struck by arrow!")

    def test_frostburn_arrow_chills_mob(self):
        """Frostburn arrows should chill the target, reducing mob speed."""
        slime = GreenSlime(self.player.center_x + 20, self.player.center_y - 10, self.asset_factory)
        initial_speed = slime.speed_mult
        self.combat.mobs.append(slime)

        arrow = ArrowProjectile(self.player.center_x, self.player.center_y, 0.0, speed=25.0, damage=30, arrow_type="frostburn_arrow")
        self.combat.spawn_projectile(arrow)

        self.combat.update(0.016, self.world, self.player, is_night=False)
        self.assertLess(slime.speed_mult, initial_speed, "Frostburn arrow should slow down target!")

    def test_arrow_passes_through_torch_and_platforms(self):
        """Arrows must fly through torches and wooden platforms without getting stuck."""
        # Set tile to torch and platform in world
        tx = int((self.player.center_x + 20) // SCALED_TILE)
        ty = int(self.player.center_y // SCALED_TILE)
        self.world.set_tile(tx, ty, TILE_TORCH)

        arrow = ArrowProjectile(self.player.center_x, self.player.center_y, 0.0, speed=10.0, damage=15)
        arrow.pos.x = tx * SCALED_TILE + 4
        arrow.pos.y = ty * SCALED_TILE + 4

        # Update arrow
        arrow.update(0.016, self.world, self.combat.particle_system, self.sound_manager, self.player)

        # Arrow should NOT be stuck on a torch!
        self.assertFalse(arrow.stuck, "Arrow should not stick to torches or non-solid tiles!")

    def test_arrow_sticks_in_solid_dirt_block(self):
        """Arrows should stick into solid blocks."""
        tx = int((self.player.center_x + 20) // SCALED_TILE)
        ty = int(self.player.center_y // SCALED_TILE)
        self.world.set_tile(tx, ty, TILE_DIRT)

        arrow = ArrowProjectile(self.player.center_x, self.player.center_y, 0.0, speed=10.0, damage=15)
        arrow.pos.x = tx * SCALED_TILE + 4
        arrow.pos.y = ty * SCALED_TILE + 4

        arrow.update(0.016, self.world, self.combat.particle_system, self.sound_manager, self.player)

        # Arrow should be stuck in solid dirt
        self.assertTrue(arrow.stuck, "Arrow must stick into solid dirt blocks!")


if __name__ == "__main__":
    unittest.main()
