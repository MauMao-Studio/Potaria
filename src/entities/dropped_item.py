"""
Terraria Pygame - Dropped Item Entity
Represents floating items in the world with gravity, bounce physics,
subtle hover oscillation, and magnetic attraction toward the player.
"""

import math
import pygame
from src.constants import GRAVITY, TERMINAL_VELOCITY, SCALED_TILE

class DroppedItem:
    def __init__(self, item_id, count, world_x, world_y, asset_factory, vx=0.0, vy=-3.0):
        self.item_id = item_id
        self.count = count
        self.x = float(world_x)
        self.y = float(world_y)
        self.vx = vx
        self.vy = vy
        self.width = 16
        self.height = 16
        
        # Texture from asset factory
        self.icon = asset_factory.items.get(item_id)
        if not self.icon:
            # Fallback to dirt
            self.icon = asset_factory.items.get("dirt_block")

        self.on_ground = False
        self.age = 0.0
        self.pickup_delay = 0.5  # half second before player can pick it up
        self.magnet_speed = 0.0
        self.picked_up = False

    @property
    def rect(self):
        return pygame.Rect(int(self.x), int(self.y), self.width, self.height)

    def update(self, dt, world, player):
        self.age += dt
        
        # Magnetic attraction towards player (only if inventory can accept item or item is coin!)
        is_coin = self.item_id in ("copper_coin", "silver_coin", "gold_coin")
        if is_coin:
            can_pickup = True
        elif hasattr(player, "inventory") and player.inventory is not None:
            can_pickup = player.inventory.can_add_item(self.item_id, 1)
        else:
            can_pickup = False

        dist_to_player = math.hypot(player.center_x - (self.x + 8), player.center_y - (self.y + 8))
        if can_pickup and self.age > self.pickup_delay and dist_to_player < 90:
            # Magnetize!
            angle = math.atan2(player.center_y - (self.y + 8), player.center_x - (self.x + 8))
            self.magnet_speed = min(12.0, self.magnet_speed + 0.8)
            self.x += math.cos(angle) * self.magnet_speed
            self.y += math.sin(angle) * self.magnet_speed
            return
        else:
            self.magnet_speed = 0.0

        # Normal Physics
        if self.on_ground and abs(self.vx) < 0.05:
            # Fast check if supporting block directly beneath item is still solid
            check_tx = int((self.x + self.width / 2.0) // SCALED_TILE)
            check_ty = int((self.y + self.height + 2) // SCALED_TILE)
            if hasattr(world, "is_tile_solid") and world.is_tile_solid(check_tx, check_ty):
                self.vx = 0.0
                return
            else:
                self.on_ground = False

        if not self.on_ground:
            self.vy = min(TERMINAL_VELOCITY, self.vy + GRAVITY)

        # Horizontal movement
        if abs(self.vx) > 0.05:
            self.x += self.vx
            self.vx *= 0.90  # ground/air friction
            solids = world.get_solid_rects_in_bounds(self.rect)
            for tile_rect, is_platform in solids:
                if not is_platform and self.rect.colliderect(tile_rect):
                    if self.vx > 0:
                        self.x = tile_rect.left - self.width
                    elif self.vx < 0:
                        self.x = tile_rect.right
                    self.vx = -self.vx * 0.3
                    break
        else:
            self.vx = 0.0

        # Vertical movement & Ground collision
        self.y += self.vy
        self.on_ground = False
        solids = world.get_solid_rects_in_bounds(self.rect)
        for tile_rect, is_platform in solids:
            if not is_platform and self.rect.colliderect(tile_rect):
                if self.vy > 0:
                    self.y = tile_rect.top - self.height
                    self.vy = 0
                    self.on_ground = True
                elif self.vy < 0:
                    self.y = tile_rect.bottom
                    self.vy = 0
                break

    def render(self, target_surf, camera):
        # Subtle hover oscillation when on ground
        bob_y = math.sin(self.age * 5.0) * 2.0 if self.on_ground else 0.0
        sx, sy = camera.world_to_screen(self.x, self.y + bob_y)
        if self.icon:
            target_surf.blit(self.icon, (sx - 4, sy - 4))
