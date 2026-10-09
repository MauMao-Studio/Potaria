"""
Potaria - Unit Tests for Player 1-Block Collider & Decorative Head Leaf
Developer: Kurados
Engine: Pure Python 3.13 + pygame-ce 2.5.8
"""

import unittest
import pygame
from unittest.mock import MagicMock
from src.constants import (
    SCALED_TILE, PLAYER_WIDTH, PLAYER_HEIGHT, PLAYER_SPRITE_WIDTH, PLAYER_SPRITE_HEIGHT,
    TILE_STONE, TILE_AIR, TILE_WOOD_PLATFORM, GRAVITY, PLAYER_SPEED
)
from src.entities.player import Player
from main import PotariaGame

class TestPlayerCollider1Block(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pygame.init()

    def test_01_constants_and_player_dimensions(self):
        """Verifies player constants and initialized dimensions."""
        self.assertEqual(PLAYER_WIDTH, 28)
        self.assertEqual(PLAYER_HEIGHT, 32)
        self.assertEqual(PLAYER_SPRITE_WIDTH, 28)
        self.assertEqual(PLAYER_SPRITE_HEIGHT, 36)
        self.assertEqual(PLAYER_HEIGHT, SCALED_TILE, "Player collider height must equal 1 block (32 px)")

        af = MagicMock()
        af.player_sprites = {
            "idle": pygame.Surface((20, 24)),
            "walk": [pygame.Surface((20, 24))],
            "jump": pygame.Surface((20, 24)),
            "arm": pygame.Surface((8, 12))
        }
        af.boss = {"fireball": pygame.Surface((10, 10))}
        sm = MagicMock()

        player = Player(100, 200, af, sm)
        self.assertEqual(player.width, 28)
        self.assertEqual(player.height, 32)
        self.assertEqual(player.sprite_width, 28)
        self.assertEqual(player.sprite_height, 36)
        self.assertEqual(player.sprout_offset_y, 4, "4px sprout offset for decorative head leaf")
        self.assertEqual(player.rect.width, 28)
        self.assertEqual(player.rect.height, 32)

    def test_02_decorative_head_leaf_outside_collider(self):
        """Verifies decorative head sprout leaf is above collider, not covered by collider."""
        af = MagicMock()
        af.player_sprites = {
            "idle": pygame.Surface((20, 24)),
            "walk": [pygame.Surface((20, 24))],
            "jump": pygame.Surface((20, 24)),
            "arm": pygame.Surface((8, 12))
        }
        af.boss = {"fireball": pygame.Surface((10, 10))}
        sm = MagicMock()

        player = Player(100, 200, af, sm)
        # Collider spans from y=200 to y=232 (32 px)
        self.assertEqual(player.rect.top, 200.0)
        self.assertEqual(player.rect.bottom, 232.0)
        
        # When rendered, sprite is placed at draw_sy = sy - sprout_offset_y
        # In world coordinates, sprite top is y - 4 = 196, sprite bottom is 196 + 36 = 232
        sprite_top_y = player.y - player.sprout_offset_y
        sprite_bottom_y = sprite_top_y + player.sprite_height
        self.assertEqual(sprite_bottom_y, player.rect.bottom, "Feet must align with collider bottom")
        self.assertLess(sprite_top_y, player.rect.top, "Head sprout leaf must extend above collider")

    def test_03_walk_into_and_through_1_block_tunnel(self):
        """Verifies player can smoothly walk into, through, and out of a 1-block opening."""
        game = PotariaGame()
        world = game.world
        
        # Clear test zone
        for tx in range(-15, 15):
            for ty in range(50, 75):
                world.set_tile(tx, ty, TILE_AIR)

        # Build 1-tile high tunnel:
        # Floor at ty=65 (y = 65 * 32 = 2080)
        # Gap at ty=64 (y = 64 * 32 = 2048 to 2080)
        # Ceiling at ty=63 (y = 63 * 32 = 2016 to 2048) for tx in [-10, 0]
        for tx in range(-15, 15):
            world.set_tile(tx, 65, TILE_STONE)
        for tx in range(-10, 0):
            world.set_tile(tx, 63, TILE_STONE)

        p = game.player
        # Start outside tunnel at tx=3 (x=96), walking left into tunnel (tx < 0)
        p.x = 96.0
        p.y = 65 * SCALED_TILE - p.height
        p.vx = -PLAYER_SPEED

        # Run 60 frames moving left
        for frame in range(60):
            p.vx = -PLAYER_SPEED
            p.update(1/60, world)

        # Player should have walked well past x=0 into the 1-block tunnel
        self.assertLess(p.x, 0.0, "Player must not get blocked by 1-block ceiling when moving left")
        self.assertTrue(p.on_ground, "Player must remain on ground in tunnel")

        # Now test moving right back out of the tunnel
        for frame in range(60):
            p.vx = PLAYER_SPEED
            p.update(1/60, world)

        self.assertGreater(p.x, 0.0, "Player must be able to walk out of 1-block tunnel to the right")

    def test_04_jump_inside_1_block_tunnel(self):
        """Verifies jumping inside a 1-block tunnel correctly hits ceiling and lands back on floor."""
        game = PotariaGame()
        world = game.world

        for tx in range(-10, 10):
            for ty in range(50, 75):
                world.set_tile(tx, ty, TILE_AIR)
        for tx in range(-10, 10):
            world.set_tile(tx, 65, TILE_STONE)  # floor at y=2080
            world.set_tile(tx, 63, TILE_STONE)  # ceiling at y=2016..2048

        p = game.player
        p.x = 0.0
        p.y = 65 * SCALED_TILE - p.height  # standing on floor: y = 2080 - 32 = 2048
        p.vx = 0.0
        p.vy = 0.0
        p.on_ground = True

        # Perform jump
        p.vy = -8.0
        p.on_ground = False

        # Frame 1: player moves upward and hits ceiling at y=2048
        p.update(1/60, world)
        self.assertEqual(p.y, 2048.0, "Ceiling collision must clamp y to ceiling bottom")
        self.assertEqual(p.vy, 0.0, "Upward velocity must be stopped on ceiling hit")

        # Frame 2: gravity pulls down, player lands back on ground
        p.update(1/60, world)
        self.assertEqual(p.y, 2048.0, "Floor collision must clamp y to floor top - height")
        self.assertTrue(p.on_ground, "Player must be on ground after landing")

    def test_05_platform_interaction_and_drop_through(self):
        """Verifies player lands on wood platforms and can drop through when holding down."""
        game = PotariaGame()
        world = game.world

        for tx in range(-5, 5):
            for ty in range(50, 70):
                world.set_tile(tx, ty, TILE_AIR)

        # Platform at ty=60 (y=1920)
        for tx in range(-5, 5):
            world.set_tile(tx, 60, TILE_WOOD_PLATFORM)

        p = game.player
        p.x = 0.0
        p.y = 1920 - p.height - 20 # 20 px above platform
        p.vy = 4.0
        p.on_ground = False

        # Fall onto platform
        for _ in range(20):
            p.update(1/60, world)

        self.assertTrue(p.on_ground, "Player must land on wood platform")
        self.assertAlmostEqual(p.y, 1920 - p.height, delta=0.5)

        # Drop through platform
        p.ignore_platforms_timer = 15
        p.update(1/60, world)
        self.assertGreater(p.y, 1920 - p.height, "Player must drop through platform when ignore_platforms_timer > 0")

    def test_06_jump_over_1_block_step(self):
        """Verifies player can smoothly jump up a 1-block step."""
        game = PotariaGame()
        world = game.world

        for tx in range(-10, 10):
            for ty in range(50, 75):
                world.set_tile(tx, ty, TILE_AIR)

        # Lower floor at tx >= 0 (ty=65), higher floor at tx < 0 (ty=64, 1-block step up!)
        for tx in range(0, 10):
            world.set_tile(tx, 65, TILE_STONE)
        for tx in range(-10, 0):
            world.set_tile(tx, 64, TILE_STONE)

        p = game.player
        p.x = 48.0
        p.y = 65 * SCALED_TILE - p.height
        p.vx = -PLAYER_SPEED
        p.on_ground = True

        jumped = False
        for frame in range(60):
            if p.x <= 20 and not jumped:
                p.vy = -8.0 # jump up the step
                p.on_ground = False
                jumped = True
            p.vx = -PLAYER_SPEED
            p.update(1/60, world)

        self.assertLess(p.x, -32.0, "Player must be able to jump onto 1-block step and proceed left")
        self.assertTrue(p.on_ground)
        self.assertEqual(p.y, 64 * SCALED_TILE - p.height)

    def test_07_pvp_remote_player_hitbox_dimensions(self):
        """Verifies PvP remote player hitbox dimensions match 1-block body collider (PLAYER_WIDTH x PLAYER_HEIGHT)."""
        game = PotariaGame()
        p = game.player
        self.assertEqual(p.width, PLAYER_WIDTH)
        self.assertEqual(p.height, PLAYER_HEIGHT)

        # Emulate remote player dict at (100.0, 200.0)
        rp = {"x": 100.0, "y": 200.0, "hp": 100}
        rpx = float(rp.get("x", 0.0))
        rpy = float(rp.get("y", 0.0))
        rp_rect = pygame.Rect(rpx, rpy, p.width, p.height)

        self.assertEqual(rp_rect.width, 28)
        self.assertEqual(rp_rect.height, 32)
        self.assertEqual(rp_rect.top, 200)
        self.assertEqual(rp_rect.bottom, 232)

    def test_08_decorative_head_leaf_projectile_passthrough(self):
        """Verifies projectiles flying through decorative head leaf (above collider) pass through without collision."""
        af = MagicMock()
        af.player_sprites = {
            "idle": pygame.Surface((20, 24)),
            "walk": [pygame.Surface((20, 24))],
            "jump": pygame.Surface((20, 24)),
            "arm": pygame.Surface((8, 12))
        }
        af.boss = {"fireball": pygame.Surface((10, 10))}
        sm = MagicMock()

        player = Player(100, 200, af, sm) # Collider: (100, 200, 28, 32). Leaf rendered at y=196..200
        
        # Projectile 1: Flying across the sprout leaf at y=197 (height 2)
        leaf_proj_rect = pygame.Rect(105, 197, 10, 2)
        self.assertFalse(player.rect.colliderect(leaf_proj_rect), "Projectiles passing through head sprout leaf must NOT hit player collider")

        # Projectile 2: Flying directly into potato body at y=210 (height 2)
        body_proj_rect = pygame.Rect(105, 210, 10, 2)
        self.assertTrue(player.rect.colliderect(body_proj_rect), "Projectiles hitting player body collider must register collision")

    def test_09_walking_animation_timing_on_surface(self):
        """Verifies grounded player advances walk frames at 12 FPS on terrain surface."""
        game = PotariaGame()
        world = game.world
        p = game.player

        # Surface at ty=70 (y = 70 * 32 = 2240)
        for tx in range(-5, 5):
            world.set_tile(tx, 70, TILE_STONE)
            world.set_tile(tx, 69, TILE_AIR)

        p.x = 0.0
        p.y = 70 * SCALED_TILE - p.height
        p.vx = 2.0
        p.anim_timer = 0.0
        start_frame = p.walk_frame_idx

        # Advance by 1/12th second (0.084s)
        p.update(0.084, world)
        self.assertTrue(p.on_ground, "Player must be on ground when placed at surface tile - height")
        self.assertEqual(p.walk_frame_idx, (start_frame + 1) % len(p.walk_sprites), "Walk frame must advance at 12 FPS")

if __name__ == "__main__":
    unittest.main()

