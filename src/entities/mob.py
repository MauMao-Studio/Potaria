"""
Terraria Pygame - Mobs & Enemy AI System
Features Green Slimes (hopping), Zombies (obstacle-jumping), and Demon Eyes (flying & swooping).
Includes health bars, knockback, damage numbers, and loot drops.
"""

import math
import random
import pygame
from src.constants import GRAVITY, TERMINAL_VELOCITY, SCALED_TILE, TILE_BARRIER

class RockProjectile:
    """Ballistic boulder thrown by RockZombie."""
    def __init__(self, x, y, vx, vy, damage=18, radius=6):
        self.pos = pygame.math.Vector2(float(x), float(y))
        self.vel = pygame.math.Vector2(float(vx), float(vy))
        self.damage = damage
        self.radius = radius
        self.life = 4.0
        self.frect = pygame.FRect(self.pos.x - self.radius, self.pos.y - self.radius, self.radius * 2, self.radius * 2)

    @property
    def rect(self):
        return self.frect

    def update(self, dt, world):
        self.life -= dt
        self.vel.y += 0.26
        self.pos += self.vel
        self.frect.center = self.pos

        tx = int(self.pos.x // SCALED_TILE)
        ty = int(self.pos.y // SCALED_TILE)
        if hasattr(world, "is_tile_solid") and world.is_tile_solid(tx, ty):
            self.life = 0

    def render(self, target_surf, camera):
        if self.life <= 0:
            return
        sx, sy = camera.world_to_screen(self.pos.x, self.pos.y)
        pygame.draw.circle(target_surf, (110, 100, 90), (int(sx), int(sy)), self.radius)
        pygame.draw.circle(target_surf, (160, 150, 140), (int(sx - 1), int(sy - 1)), max(1, self.radius - 2))


class Mob:
    """Base class for all Terraria monsters."""
    def __init__(self, x, y, width, height, max_hp, damage, name):
        self.x = float(x)
        self.y = float(y)
        self.width = width
        self.height = height
        self.max_hp = max_hp
        self.hp = max_hp
        self.damage = damage
        self.name = name
        self.frect = pygame.FRect(self.x, self.y, self.width, self.height)
        
        self.vx = 0.0
        self.vy = 0.0
        self.on_ground = False
        self.facing_right = True
        self.is_dead = False
        
        # Combat & Hurt flash
        self.hurt_timer = 0.0
        self.hp_bar_timer = 0.0
        self.pending_projectiles = []
        self.stuck_timer = 0.0
        self.mob_id = None
        self.mob_type = "green_slime"

        # Status Effects (Burn & Bleed DoT)
        self.burn_timer = 0.0
        self.burn_dps = 0
        self.bleed_timer = 0.0
        self.bleed_dps = 0
        self.dot_tick_timer = 0.0

    def apply_burn(self, dps=8, duration=4.0):
        self.burn_dps = max(self.burn_dps, dps)
        self.burn_timer = max(self.burn_timer, duration)

    def apply_bleed(self, dps=7, duration=5.0):
        self.bleed_dps = max(self.bleed_dps, dps)
        self.bleed_timer = max(self.bleed_timer, duration)

    def update_dots(self, dt):
        """Ticks active burn and bleed DoT timers and inflicts periodic tick damage."""
        if (self.burn_timer > 0 or self.bleed_timer > 0) and not self.is_dead:
            self.dot_tick_timer += dt
            if self.burn_timer > 0:
                self.burn_timer -= dt
                if self.burn_timer <= 0:
                    self.burn_dps = 0
            if self.bleed_timer > 0:
                self.bleed_timer -= dt
                if self.bleed_timer <= 0:
                    self.bleed_dps = 0

            if self.dot_tick_timer >= 1.0:
                self.dot_tick_timer = 0.0
                total_dot = (self.burn_dps if self.burn_dps > 0 else 0) + (self.bleed_dps if self.bleed_dps > 0 else 0)
                if total_dot > 0:
                    self.take_damage(total_dot)

    @property
    def rect(self):
        self.frect.x = self.x
        self.frect.y = self.y
        return self.frect

    @property
    def center_x(self):
        return self.x + self.width / 2.0

    @property
    def center_y(self):
        return self.y + self.height / 2.0

    @property
    def is_alive(self):
        return not self.is_dead and self.hp > 0

    @property
    def alive(self):
        return not self.is_dead and self.hp > 0

    def take_damage(self, amount, knockback_vx=0.0, knockback_vy=-3.0):
        """Applies damage and knockback."""
        if self.is_dead:
            return False
        self.hp -= amount
        self.hurt_timer = 0.2
        self.hp_bar_timer = 3.0
        self.vx = knockback_vx
        self.vy = knockback_vy
        self.on_ground = False

        if self.hp <= 0:
            self.hp = 0
            self.is_dead = True
        return True

    def render_health_bar(self, target_surf, camera):
        """Draws miniature health bar above mob when recently damaged."""
        if self.hp_bar_timer > 0 and not self.is_dead:
            sx, sy = camera.world_to_screen(self.x, self.y - 8)
            bar_w = self.width
            bar_h = 4
            pct = max(0.0, min(1.0, self.hp / self.max_hp))
            pygame.draw.rect(target_surf, (50, 50, 50), (sx, sy, bar_w, bar_h))
            pygame.draw.rect(target_surf, (50, 220, 50), (sx, sy, int(bar_w * pct), bar_h))
            pygame.draw.rect(target_surf, (0, 0, 0), (sx, sy, bar_w, bar_h), 1)

# =============================================================================
# 1. SLIMES (Jelly Bounce Physics & Animations)
# =============================================================================
class SlimeMob(Mob):
    def __init__(self, x, y, asset_factory, sprite_key="slime", max_hp=25, damage=8, name="Green Slime", speed_mult=1.0):
        super().__init__(x, y, width=28, height=22, max_hp=max_hp, damage=damage, name=name)
        self.asset_factory = asset_factory
        self.speed_mult = speed_mult
        raw_frames = asset_factory.mobs.get(sprite_key, asset_factory.mobs["slime"])
        self.frames = [pygame.transform.scale(f, (self.width, self.height)) for f in raw_frames]
        self.frame_normal = self.frames[0]
        self.frame_squish = self.frames[1] if len(self.frames) > 1 else self.frames[0]
        self.frame_stretch = self.frames[2] if len(self.frames) > 2 else self.frames[0]

        self.jump_cooldown = random.uniform(1.0, 2.0)
        self.state = "idle"
        self.squish_timer = 0.0
        self.anim_timer = 0.0
        self.anim_idx = 0

    def update(self, dt, world, player):
        if self.is_dead:
            return

        if self.hurt_timer > 0:
            self.hurt_timer -= dt
        if self.hp_bar_timer > 0:
            self.hp_bar_timer -= dt

        self.vy = min(TERMINAL_VELOCITY, self.vy + GRAVITY)

        dist_x = player.center_x - self.center_x
        dist_y = player.center_y - self.center_y
        dist = math.hypot(dist_x, dist_y)

        if self.on_ground:
            self.vx *= 0.8
            if abs(self.vx) < 0.1:
                self.vx = 0.0

            if self.state == "jumping":
                self.state = "idle"
                self.jump_cooldown = random.uniform(0.8, 1.8) / self.speed_mult

            if self.state == "idle":
                self.jump_cooldown -= dt
                if self.jump_cooldown <= 0:
                    self.state = "squishing"
                    self.squish_timer = 0.22 / self.speed_mult

            elif self.state == "squishing":
                self.squish_timer -= dt
                if self.squish_timer <= 0:
                    self.state = "jumping"
                    jump_dir = 1 if dist_x > 0 else -1
                    speed_x = min(4.2, max(2.0, abs(dist_x) * 0.016)) * self.speed_mult
                    self.vx = jump_dir * speed_x
                    self.vy = -7.0 * math.sqrt(self.speed_mult)
                    self.on_ground = False

        self.anim_timer += dt
        if self.anim_timer >= 1.0 / 12.0:
            self.anim_timer = 0.0
            self.anim_idx = (self.anim_idx + 1) % len(self.frames)

        # Anti-cheese: if slime is obstructed by a wall or unable to reach player
        jump_dir = 1 if dist_x > 0 else -1
        check_x = self.x + (self.width + 4 if jump_dir > 0 else -4)
        wall_front = (world.get_tile(int(check_x // SCALED_TILE), int((self.y + self.height - 8) // SCALED_TILE)) != 0)
        wall_high = (world.get_tile(int(check_x // SCALED_TILE), int(self.y // SCALED_TILE)) != 0)

        if (wall_front or wall_high) and abs(dist_x) > 12:
            self.stuck_timer += dt
        else:
            self.stuck_timer = max(0.0, self.stuck_timer - dt * 0.4)

        if self.stuck_timer >= 0.8:
            self.stuck_timer = 0.0
            self.state = "jumping"
            self.vy = -11.0
            self.vx = jump_dir * 5.2 * self.speed_mult
            self.on_ground = False
            if dist < 350.0:
                from src.entities.projectile import MobSpitProjectile
                spit_vx = jump_dir * min(6.5, max(3.2, abs(dist_x) * 0.024))
                spit_vy = -6.5 + min(1.0, dist_y * 0.02)
                self.pending_projectiles.append(
                    MobSpitProjectile(self.center_x, self.center_y - 6, spit_vx, spit_vy,
                                      damage=max(6, int(self.damage * 0.8)), color=(100, 240, 70))
                )

        self.x += self.vx
        solids = world.get_solid_rects_in_bounds(self.rect)
        for tile_rect, is_platform in solids:
            if not is_platform and self.rect.colliderect(tile_rect):
                if self.vx > 0:
                    self.x = tile_rect.left - self.width
                elif self.vx < 0:
                    self.x = tile_rect.right
                self.vx = -self.vx * 0.5
                self.stuck_timer += dt * 1.5
                break

        self.y += self.vy
        self.on_ground = False
        solids = world.get_solid_rects_in_bounds(self.rect)
        for tile_rect, is_platform in solids:
            if not is_platform and self.rect.colliderect(tile_rect):
                if self.vy > 0:
                    self.y = tile_rect.top - self.height
                    self.vy = 0.0
                    self.on_ground = True
                elif self.vy < 0:
                    self.y = tile_rect.bottom
                    self.vy = 0.0
                break

    def render(self, target_surf, camera):
        if self.is_dead:
            return

        sx, sy = camera.world_to_screen(self.x, self.y)

        if not self.on_ground:
            cur_surf = self.frame_stretch
        elif self.state == "squishing":
            cur_surf = self.frame_squish
            sy += 4
        else:
            cur_surf = self.frames[self.anim_idx]

        if self.hurt_timer > 0:
            tinted = cur_surf.copy()
            tinted.fill((255, 100, 100, 180), special_flags=pygame.BLEND_RGBA_MULT)
            cur_surf = tinted

        target_surf.blit(cur_surf, (sx, sy))
        self.render_health_bar(target_surf, camera)

class GreenSlime(SlimeMob):
    mob_type = "green_slime"
    def __init__(self, x, y, asset_factory):
        super().__init__(x, y, asset_factory, sprite_key="slime", max_hp=25, damage=14, name="Green Slime", speed_mult=1.0)
        self.mob_type = "green_slime"

class PurpleSlime(SlimeMob):
    mob_type = "purple_slime"
    def __init__(self, x, y, asset_factory):
        super().__init__(x, y, asset_factory, sprite_key="purple_slime", max_hp=42, damage=22, name="Purple Slime", speed_mult=1.15)
        self.mob_type = "purple_slime"

class SandSlime(SlimeMob):
    mob_type = "sand_slime"
    def __init__(self, x, y, asset_factory):
        super().__init__(x, y, asset_factory, sprite_key="sand_slime", max_hp=36, damage=18, name="Sand Slime", speed_mult=1.2)
        self.mob_type = "sand_slime"

class FrostSlime(SlimeMob):
    mob_type = "frost_slime"
    def __init__(self, x, y, asset_factory):
        super().__init__(x, y, asset_factory, sprite_key="frost_slime", max_hp=34, damage=16, name="Frost Slime", speed_mult=1.05)
        self.mob_type = "frost_slime"

class CorruptSlime(SlimeMob):
    mob_type = "corrupt_slime"
    def __init__(self, x, y, asset_factory):
        super().__init__(x, y, asset_factory, sprite_key="corrupt_slime", max_hp=55, damage=25, name="Corrupt Slime", speed_mult=1.3)
        self.mob_type = "corrupt_slime"


# =============================================================================
# 2. HUMANOID WALKERS (Zombies, Mummies, Skeletons)
# =============================================================================
class WalkerMob(Mob):
    def __init__(self, x, y, asset_factory, sprite_key="zombie", max_hp=45, damage=14, name="Zombie", speed=1.4):
        super().__init__(x, y, width=24, height=44, max_hp=max_hp, damage=damage, name=name)
        self.asset_factory = asset_factory
        self.speed = speed
        raw_frames = asset_factory.mobs.get(sprite_key, asset_factory.mobs["zombie"])
        self.walk_frames = [pygame.transform.scale(f, (self.width, self.height)) for f in raw_frames]
        self.walk_idx = 0
        self.walk_anim_timer = 0.0

    def update(self, dt, world, player):
        if self.is_dead:
            return

        if self.hurt_timer > 0:
            self.hurt_timer -= dt
        if self.hp_bar_timer > 0:
            self.hp_bar_timer -= dt

        self.vy = min(TERMINAL_VELOCITY, self.vy + GRAVITY)

        dist_x = player.center_x - self.center_x
        dist_y = player.center_y - self.center_y
        dist = math.hypot(dist_x, dist_y)
        move_dir = 1 if dist_x > 0 else -1
        self.facing_right = (move_dir > 0)
        self.vx = move_dir * self.speed

        check_x = self.x + (self.width + 4 if move_dir > 0 else -4)
        wall_front = world.get_tile(int(check_x // SCALED_TILE), int((self.y + self.height - 8) // SCALED_TILE))
        wall_high = world.get_tile(int(check_x // SCALED_TILE), int((self.y + 4) // SCALED_TILE))

        if wall_front != 0 and self.on_ground:
            if wall_high != 0:
                self.stuck_timer += dt
            else:
                self.vy = -6.5
                self.on_ground = False
        else:
            self.stuck_timer = max(0.0, self.stuck_timer - dt * 0.4)

        if self.stuck_timer >= 0.8:
            self.stuck_timer = 0.0
            self.vy = -10.5
            self.vx = move_dir * (self.speed * 2.5)
            self.on_ground = False
            if dist < 350.0:
                from src.entities.projectile import MobSpitProjectile
                spit_vx = move_dir * min(6.0, max(3.0, abs(dist_x) * 0.024))
                spit_vy = -6.5 + min(1.0, dist_y * 0.02)
                spit_col = (160, 60, 200) if ("Corrupt" in self.name or "Shadow" in self.name) else (80, 220, 60)
                self.pending_projectiles.append(
                    MobSpitProjectile(self.center_x, self.center_y - 12, spit_vx, spit_vy,
                                      damage=max(8, int(self.damage * 0.85)), color=spit_col)
                )

        self.x += self.vx
        solids = world.get_solid_rects_in_bounds(self.rect)
        for tile_rect, is_platform in solids:
            if not is_platform and self.rect.colliderect(tile_rect):
                if self.vx > 0:
                    self.x = tile_rect.left - self.width
                elif self.vx < 0:
                    self.x = tile_rect.right
                self.vx = 0.0
                self.stuck_timer += dt * 1.5
                break

        self.y += self.vy
        self.on_ground = False
        solids = world.get_solid_rects_in_bounds(self.rect)
        for tile_rect, is_platform in solids:
            if not is_platform and self.rect.colliderect(tile_rect):
                if self.vy > 0:
                    self.y = tile_rect.top - self.height
                    self.vy = 0.0
                    self.on_ground = True
                elif self.vy < 0:
                    self.y = tile_rect.bottom
                    self.vy = 0.0
                break

        if self.on_ground and abs(self.vx) > 0.1:
            self.walk_anim_timer += dt
            if self.walk_anim_timer >= 1.0 / 12.0:
                self.walk_anim_timer = 0.0
                self.walk_idx = (self.walk_idx + 1) % len(self.walk_frames)

    def render(self, target_surf, camera):
        if self.is_dead:
            return

        sx, sy = camera.world_to_screen(self.x, self.y)
        cur_surf = self.walk_frames[self.walk_idx]

        if not self.facing_right:
            cur_surf = pygame.transform.flip(cur_surf, True, False)

        if self.hurt_timer > 0:
            tinted = cur_surf.copy()
            tinted.fill((255, 100, 100, 180), special_flags=pygame.BLEND_RGBA_MULT)
            cur_surf = tinted

        target_surf.blit(cur_surf, (sx, sy))
        self.render_health_bar(target_surf, camera)

class Zombie(WalkerMob):
    mob_type = "zombie"
    def __init__(self, x, y, asset_factory):
        super().__init__(x, y, asset_factory, sprite_key="zombie", max_hp=45, damage=20, name="Zombie", speed=1.4)
        self.mob_type = "zombie"

class IceZombie(WalkerMob):
    mob_type = "ice_zombie"
    def __init__(self, x, y, asset_factory):
        super().__init__(x, y, asset_factory, sprite_key="ice_zombie", max_hp=65, damage=26, name="Frozen Zombie", speed=1.3)
        self.mob_type = "ice_zombie"

class Mummy(WalkerMob):
    mob_type = "mummy"
    def __init__(self, x, y, asset_factory):
        super().__init__(x, y, asset_factory, sprite_key="mummy", max_hp=80, damage=30, name="Mummy", speed=1.5)
        self.mob_type = "mummy"

class Skeleton(WalkerMob):
    mob_type = "skeleton"
    def __init__(self, x, y, asset_factory):
        super().__init__(x, y, asset_factory, sprite_key="skeleton", max_hp=50, damage=24, name="Skeleton", speed=1.65)
        self.mob_type = "skeleton"


# =============================================================================
# 3. FLYING MOBS (Demon Eye, Cave Bats, Ice Bats)
# =============================================================================
class DemonEye(Mob):
    mob_type = "demon_eye"
    def __init__(self, x, y, asset_factory):
        super().__init__(x, y, width=28, height=28, max_hp=35, damage=18, name="Night Gazer")
        self.mob_type = "demon_eye"
        self.asset_factory = asset_factory
        raw_frames = asset_factory.mobs.get("night_gazer") or asset_factory.mobs.get("demon_eye")
        self.frames = [pygame.transform.scale(f, (self.width, self.height)) for f in raw_frames]
        self.anim_timer = 0.0
        self.frame_idx = 0
        self.angle = 0.0
        self.state = "hover"
        self.state_timer = 2.0

    def update(self, dt, world, player):
        if self.is_dead:
            return

        if self.hurt_timer > 0:
            self.hurt_timer -= dt
        if self.hp_bar_timer > 0:
            self.hp_bar_timer -= dt

        self.anim_timer += dt
        if self.anim_timer >= 1.0 / 12.0:
            self.anim_timer = 0.0
            self.frame_idx = (self.frame_idx + 1) % len(self.frames)

        dist_x = player.center_x - self.center_x
        dist_y = player.center_y - self.center_y
        self.angle = math.atan2(dist_y, dist_x)

        self.state_timer -= dt
        if self.state == "hover":
            target_x = player.center_x + math.cos(pygame.time.get_ticks() * 0.002) * 120
            target_y = player.center_y - 100 + math.sin(pygame.time.get_ticks() * 0.003) * 40
            self.vx += (target_x - self.x) * 0.04
            self.vy += (target_y - self.y) * 0.04
            self.vx *= 0.92
            self.vy *= 0.92

            if self.state_timer <= 0:
                self.state = "dash"
                self.state_timer = 1.2
                dash_spd = 5.2
                self.vx = math.cos(self.angle) * dash_spd
                self.vy = math.sin(self.angle) * dash_spd

        elif self.state == "dash":
            self.vx *= 0.98
            self.vy *= 0.98
            if self.state_timer <= 0:
                self.state = "hover"
                self.state_timer = random.uniform(2.0, 3.5)

        # Demon Eye ghost spectral flight (phases freely through solid blocks and walls)
        self.x += self.vx
        self.y += self.vy

    def render(self, target_surf, camera):
        if self.is_dead:
            return

        sx, sy = camera.world_to_screen(self.x, self.y)
        cur_surf = self.frames[self.frame_idx]

        rot_angle = -math.degrees(self.angle)
        rotated = pygame.transform.rotate(cur_surf, rot_angle)
        rect = rotated.get_rect(center=(sx + self.width // 2, sy + self.height // 2))

        if self.hurt_timer > 0:
            tinted = rotated.copy()
            tinted.fill((255, 100, 100, 180), special_flags=pygame.BLEND_RGBA_MULT)
            rotated = tinted

        target_surf.blit(rotated, rect.topleft)
        self.render_health_bar(target_surf, camera)

class BatMob(Mob):
    def __init__(self, x, y, asset_factory, sprite_key="cave_bat", max_hp=22, damage=10, name="Cave Bat"):
        super().__init__(x, y, width=24, height=20, max_hp=max_hp, damage=damage, name=name)
        self.asset_factory = asset_factory
        raw_frames = asset_factory.mobs.get(sprite_key, asset_factory.mobs["cave_bat"])
        self.frames = [pygame.transform.scale(f, (self.width, self.height)) for f in raw_frames]
        self.anim_timer = 0.0
        self.frame_idx = 0
        self.flutter_timer = random.uniform(0.0, 10.0)

    def update(self, dt, world, player):
        if self.is_dead:
            return

        if self.hurt_timer > 0:
            self.hurt_timer -= dt
        if self.hp_bar_timer > 0:
            self.hp_bar_timer -= dt

        self.anim_timer += dt
        if self.anim_timer >= 1.0 / 12.0:
            self.anim_timer = 0.0
            self.frame_idx = (self.frame_idx + 1) % len(self.frames)

        dist_x = player.center_x - self.center_x
        dist_y = player.center_y - self.center_y
        dist = math.hypot(dist_x, dist_y)

        self.flutter_timer += dt * 4.5
        wave_y = math.sin(self.flutter_timer) * 1.8

        if dist < 420:
            target_vx = (dist_x / max(1.0, dist)) * 2.8
            target_vy = (dist_y / max(1.0, dist)) * 2.2 + wave_y
        else:
            target_vx = math.cos(self.flutter_timer * 0.5) * 1.4
            target_vy = wave_y

        self.vx = self.vx * 0.9 + target_vx * 0.1
        self.vy = self.vy * 0.9 + target_vy * 0.1
        self.facing_right = (self.vx > 0)

        # Solid block collisions for bats
        self.x += self.vx
        solids = world.get_solid_rects_in_bounds(self.rect)
        for tile_rect, is_platform in solids:
            if not is_platform and self.rect.colliderect(tile_rect):
                if self.vx > 0:
                    self.x = tile_rect.left - self.width
                elif self.vx < 0:
                    self.x = tile_rect.right
                self.vx = -self.vx * 0.5
                break

        self.y += self.vy
        solids = world.get_solid_rects_in_bounds(self.rect)
        for tile_rect, is_platform in solids:
            if not is_platform and self.rect.colliderect(tile_rect):
                if self.vy > 0:
                    self.y = tile_rect.top - self.height
                elif self.vy < 0:
                    self.y = tile_rect.bottom
                self.vy = -self.vy * 0.5
                break

    def render(self, target_surf, camera):
        if self.is_dead:
            return

        sx, sy = camera.world_to_screen(self.x, self.y)
        cur_surf = self.frames[self.frame_idx]
        if not self.facing_right:
            cur_surf = pygame.transform.flip(cur_surf, True, False)

        if self.hurt_timer > 0:
            tinted = cur_surf.copy()
            tinted.fill((255, 100, 100, 180), special_flags=pygame.BLEND_RGBA_MULT)
            cur_surf = tinted

        target_surf.blit(cur_surf, (sx, sy))
        self.render_health_bar(target_surf, camera)

class CaveBat(BatMob):
    mob_type = "cave_bat"
    def __init__(self, x, y, asset_factory):
        super().__init__(x, y, asset_factory, sprite_key="cave_bat", max_hp=24, damage=15, name="Cave Bat")
        self.mob_type = "cave_bat"

class IceBat(BatMob):
    mob_type = "ice_bat"
    def __init__(self, x, y, asset_factory):
        super().__init__(x, y, asset_factory, sprite_key="ice_bat", max_hp=30, damage=18, name="Ice Bat")
        self.mob_type = "ice_bat"


# =============================================================================
# 4. GROUND ARACHNIDS & CRAWLERS (Scorpions, Shadow Crawlers)
# =============================================================================
class CrawlerMob(Mob):
    def __init__(self, x, y, asset_factory, sprite_key="desert_scorpion", max_hp=48, damage=18, name="Desert Scorpion", speed=2.2):
        super().__init__(x, y, width=32, height=22, max_hp=max_hp, damage=damage, name=name)
        self.asset_factory = asset_factory
        self.speed = speed
        raw_frames = asset_factory.mobs.get(sprite_key, asset_factory.mobs["desert_scorpion"])
        self.walk_frames = [pygame.transform.scale(f, (self.width, self.height)) for f in raw_frames]
        self.walk_idx = 0
        self.anim_timer = 0.0

    def update(self, dt, world, player):
        if self.is_dead:
            return

        if self.hurt_timer > 0:
            self.hurt_timer -= dt
        if self.hp_bar_timer > 0:
            self.hp_bar_timer -= dt

        self.vy = min(TERMINAL_VELOCITY, self.vy + GRAVITY)

        dist_x = player.center_x - self.center_x
        dist_y = player.center_y - self.center_y
        dist = math.hypot(dist_x, dist_y)
        move_dir = 1 if dist_x > 0 else -1
        self.facing_right = (move_dir > 0)
        self.vx = move_dir * self.speed

        check_x = self.x + (self.width + 4 if move_dir > 0 else -4)
        wall_front = world.get_tile(int(check_x // SCALED_TILE), int((self.y + self.height - 8) // SCALED_TILE))
        wall_high = world.get_tile(int(check_x // SCALED_TILE), int((self.y + 2) // SCALED_TILE))

        if wall_front != 0 and self.on_ground:
            if wall_high != 0:
                self.stuck_timer += dt
            else:
                self.vy = -7.2
                self.on_ground = False
        else:
            self.stuck_timer = max(0.0, self.stuck_timer - dt * 0.4)

        if self.stuck_timer >= 0.8:
            self.stuck_timer = 0.0
            self.vy = -10.5
            self.vx = move_dir * (self.speed * 2.0)
            self.on_ground = False
            if dist < 350.0:
                from src.entities.projectile import MobSpitProjectile
                spit_vx = move_dir * min(6.5, max(3.2, abs(dist_x) * 0.024))
                spit_vy = -6.5 + min(1.0, dist_y * 0.02)
                self.pending_projectiles.append(
                    MobSpitProjectile(self.center_x, self.center_y - 8, spit_vx, spit_vy,
                                      damage=max(8, int(self.damage * 0.85)), color=(220, 180, 50))
                )

        self.x += self.vx
        solids = world.get_solid_rects_in_bounds(self.rect)
        for tile_rect, is_platform in solids:
            if not is_platform and self.rect.colliderect(tile_rect):
                if self.vx > 0:
                    self.x = tile_rect.left - self.width
                elif self.vx < 0:
                    self.x = tile_rect.right
                self.vx = 0.0
                self.stuck_timer += dt * 1.5
                break

        self.y += self.vy
        self.on_ground = False
        solids = world.get_solid_rects_in_bounds(self.rect)
        for tile_rect, is_platform in solids:
            if not is_platform and self.rect.colliderect(tile_rect):
                if self.vy > 0:
                    self.y = tile_rect.top - self.height
                    self.vy = 0.0
                    self.on_ground = True
                elif self.vy < 0:
                    self.y = tile_rect.bottom
                    self.vy = 0.0
                break

        if self.on_ground and abs(self.vx) > 0.1:
            self.anim_timer += dt
            if self.anim_timer >= 1.0 / 12.0:
                self.anim_timer = 0.0
                self.walk_idx = (self.walk_idx + 1) % len(self.walk_frames)

    def render(self, target_surf, camera):
        if self.is_dead:
            return

        sx, sy = camera.world_to_screen(self.x, self.y)
        cur_surf = self.walk_frames[self.walk_idx]

        if not self.facing_right:
            cur_surf = pygame.transform.flip(cur_surf, True, False)

        if self.hurt_timer > 0:
            tinted = cur_surf.copy()
            tinted.fill((255, 100, 100, 180), special_flags=pygame.BLEND_RGBA_MULT)
            cur_surf = tinted

        target_surf.blit(cur_surf, (sx, sy))
        self.render_health_bar(target_surf, camera)

class DesertScorpion(CrawlerMob):
    mob_type = "desert_scorpion"
    def __init__(self, x, y, asset_factory):
        super().__init__(x, y, asset_factory, sprite_key="desert_scorpion", max_hp=52, damage=24, name="Desert Scorpion", speed=2.1)
        self.mob_type = "desert_scorpion"

class ShadowCrawler(CrawlerMob):
    mob_type = "shadow_crawler"
    def __init__(self, x, y, asset_factory):
        super().__init__(x, y, asset_factory, sprite_key="shadow_crawler", max_hp=68, damage=32, name="Shadow Crawler", speed=2.6)
        self.mob_type = "shadow_crawler"


# =============================================================================
# 5. SPECIAL ADVANCED MOBS (RockZombie, ShieldWeaver, DiggerMob)
# =============================================================================
class RockZombie(WalkerMob):
    mob_type = "rock_zombie"
    def __init__(self, x, y, asset_factory):
        super().__init__(x, y, asset_factory, sprite_key="rock_zombie", max_hp=65, damage=22, name="Rock Zombie", speed=1.25)
        self.mob_type = "rock_zombie"
        self.throw_timer = random.uniform(1.2, 2.5)

    def update(self, dt, world, player):
        super().update(dt, world, player)
        if self.is_dead:
            return
        self.throw_timer -= dt
        dist_x = player.center_x - self.center_x
        dist_y = player.center_y - self.center_y
        dist = math.hypot(dist_x, dist_y)
        if self.throw_timer <= 0:
            self.throw_timer = random.uniform(2.5, 4.0)
            if 50.0 < dist < 420.0:
                throw_dir = 1 if dist_x > 0 else -1
                rock_vx = throw_dir * min(7.5, max(3.5, abs(dist_x) * 0.025))
                rock_vy = -6.0 + min(1.5, dist_y * 0.02)
                self.pending_projectiles.append(
                    RockProjectile(self.center_x, self.center_y - 10, rock_vx, rock_vy, damage=self.damage)
                )


class ShieldWeaver(Mob):
    mob_type = "shield_weaver"
    def __init__(self, x, y, asset_factory):
        super().__init__(x, y, width=24, height=36, max_hp=75, damage=18, name="Shield Weaver")
        self.mob_type = "shield_weaver"
        self.asset_factory = asset_factory
        raw_frames = asset_factory.mobs.get("shield_weaver", asset_factory.mobs.get("zombie"))
        self.frames = [pygame.transform.scale(f, (self.width, self.height)) for f in raw_frames]
        self.anim_timer = 0.0
        self.frame_idx = 0
        self.cast_timer = random.uniform(1.5, 3.0)
        self.placed_barriers = []
        self.hover_angle = random.uniform(0.0, 6.28)

    def update(self, dt, world, player):
        if self.is_dead:
            self._cleanup_barriers(world)
            return

        if self.hurt_timer > 0:
            self.hurt_timer -= dt
        if self.hp_bar_timer > 0:
            self.hp_bar_timer -= dt

        self.anim_timer += dt
        if self.anim_timer >= 1.0 / 12.0:
            self.anim_timer = 0.0
            self.frame_idx = (self.frame_idx + 1) % len(self.frames)

        self.hover_angle += dt * 2.2
        dist_x = player.center_x - self.center_x
        dist_y = player.center_y - self.center_y
        dist = math.hypot(dist_x, dist_y)

        # Hover motion around player
        target_dist = 130.0
        approach_dir = 1 if dist_x > 0 else -1
        target_x = player.center_x - approach_dir * target_dist
        target_y = player.center_y - 35.0 + math.sin(self.hover_angle) * 22.0

        self.vx = self.vx * 0.91 + (target_x - self.x) * 0.03
        self.vy = self.vy * 0.91 + (target_y - self.y) * 0.03

        self.x += self.vx
        solids = world.get_solid_rects_in_bounds(self.rect)
        for tile_rect, is_platform in solids:
            if not is_platform and self.rect.colliderect(tile_rect):
                if self.vx > 0:
                    self.x = tile_rect.left - self.width
                elif self.vx < 0:
                    self.x = tile_rect.right
                self.vx = 0
                break

        self.y += self.vy
        solids = world.get_solid_rects_in_bounds(self.rect)
        for tile_rect, is_platform in solids:
            if not is_platform and self.rect.colliderect(tile_rect):
                if self.vy > 0:
                    self.y = tile_rect.top - self.height
                elif self.vy < 0:
                    self.y = tile_rect.bottom
                self.vy = 0
                break

        # Cast overhead magical barrier blocks
        self.cast_timer -= dt
        if self.cast_timer <= 0:
            self.cast_timer = random.uniform(4.5, 6.5)
            if dist < 420.0:
                cx = int(self.center_x // SCALED_TILE)
                cy = int(self.y // SCALED_TILE) - 3
                for bx in range(cx - 1, cx + 2):
                    if world.get_tile(bx, cy) == 0:
                        world.set_tile(bx, cy, TILE_BARRIER)
                        self.placed_barriers.append([bx, cy, 8.0])

        still_active = []
        for b in self.placed_barriers:
            b[2] -= dt
            if b[2] <= 0:
                if world.get_tile(b[0], b[1]) == TILE_BARRIER:
                    world.set_tile(b[0], b[1], 0)
            else:
                still_active.append(b)
        self.placed_barriers = still_active

    def _cleanup_barriers(self, world):
        for b in self.placed_barriers:
            if world.get_tile(b[0], b[1]) == TILE_BARRIER:
                world.set_tile(b[0], b[1], 0)
        self.placed_barriers.clear()

    def render(self, target_surf, camera):
        if self.is_dead:
            return
        sx, sy = camera.world_to_screen(self.x, self.y)
        cur_surf = self.frames[self.frame_idx]
        if self.vx < -0.1:
            cur_surf = pygame.transform.flip(cur_surf, True, False)
        if self.hurt_timer > 0:
            tinted = cur_surf.copy()
            tinted.fill((255, 100, 100, 180), special_flags=pygame.BLEND_RGBA_MULT)
            cur_surf = tinted
        target_surf.blit(cur_surf, (sx, sy))
        self.render_health_bar(target_surf, camera)


HOUSE_TILES = {4, 10, 11, 14, 15, 16, 29, 30, 31, 32, 33, 34, 35, 36}

class DiggerMob(Mob):
    mob_type = "digger"
    def __init__(self, x, y, asset_factory):
        super().__init__(x, y, width=28, height=20, max_hp=80, damage=26, name="Digger")
        self.mob_type = "digger"
        self.speed = 1.9
        self.asset_factory = asset_factory
        raw_frames = asset_factory.mobs.get("digger", asset_factory.mobs.get("desert_scorpion"))
        self.frames = [pygame.transform.scale(f, (self.width, self.height)) for f in raw_frames]
        self.anim_timer = 0.0
        self.frame_idx = 0
        self.burrowing = True

    def update(self, dt, world, player):
        if self.is_dead:
            return

        if self.hurt_timer > 0:
            self.hurt_timer -= dt
        if self.hp_bar_timer > 0:
            self.hp_bar_timer -= dt

        self.anim_timer += dt
        if self.anim_timer >= 1.0 / 12.0:
            self.anim_timer = 0.0
            self.frame_idx = (self.frame_idx + 1) % len(self.frames)

        dist_x = player.center_x - self.center_x
        dist_y = player.center_y - self.center_y
        dist = math.hypot(dist_x, dist_y)

        if dist > 0:
            target_vx = (dist_x / dist) * self.speed
            target_vy = (dist_y / dist) * self.speed
        else:
            target_vx, target_vy = 0.0, 0.0

        self.vx = self.vx * 0.88 + target_vx * 0.12
        self.vy = self.vy * 0.88 + target_vy * 0.12

        # Horizontal movement and collision with house tiles
        self.x += self.vx
        rect = self.rect
        min_tx = int(rect.left // SCALED_TILE)
        max_tx = int(rect.right // SCALED_TILE)
        min_ty = int(rect.top // SCALED_TILE)
        max_ty = int(rect.bottom // SCALED_TILE)

        for ty in range(min_ty, max_ty + 1):
            for tx in range(min_tx, max_tx + 1):
                tid = world.get_tile(tx, ty)
                is_placed = hasattr(world, "player_placed_tiles") and (tx, ty) in world.player_placed_tiles
                if tid in HOUSE_TILES or is_placed:
                    tile_rect = pygame.Rect(tx * SCALED_TILE, ty * SCALED_TILE, SCALED_TILE, SCALED_TILE)
                    if rect.colliderect(tile_rect):
                        if self.vx > 0:
                            self.x = tile_rect.left - self.width
                        elif self.vx < 0:
                            self.x = tile_rect.right
                        self.vx = 0.0
                        break

        # Vertical movement and collision with house tiles & player-placed blocks
        self.y += self.vy
        rect = self.rect
        min_tx = int(rect.left // SCALED_TILE)
        max_tx = int(rect.right // SCALED_TILE)
        min_ty = int(rect.top // SCALED_TILE)
        max_ty = int(rect.bottom // SCALED_TILE)

        for ty in range(min_ty, max_ty + 1):
            for tx in range(min_tx, max_tx + 1):
                tid = world.get_tile(tx, ty)
                is_placed = hasattr(world, "player_placed_tiles") and (tx, ty) in world.player_placed_tiles
                if tid in HOUSE_TILES or is_placed:
                    tile_rect = pygame.Rect(tx * SCALED_TILE, ty * SCALED_TILE, SCALED_TILE, SCALED_TILE)
                    if rect.colliderect(tile_rect):
                        if self.vy > 0:
                            self.y = tile_rect.top - self.height
                        elif self.vy < 0:
                            self.y = tile_rect.bottom
                        self.vy = 0.0
                        break

    def render(self, target_surf, camera):
        if self.is_dead:
            return
        sx, sy = camera.world_to_screen(self.x, self.y)
        cur_surf = self.frames[self.frame_idx]
        if self.vx < -0.1:
            cur_surf = pygame.transform.flip(cur_surf, True, False)
        if self.hurt_timer > 0:
            tinted = cur_surf.copy()
            tinted.fill((255, 100, 100, 180), special_flags=pygame.BLEND_RGBA_MULT)
            cur_surf = tinted
        target_surf.blit(cur_surf, (sx, sy))
        self.render_health_bar(target_surf, camera)


MOB_TYPE_REGISTRY = {
    "green_slime": GreenSlime,
    "purple_slime": PurpleSlime,
    "sand_slime": SandSlime,
    "frost_slime": FrostSlime,
    "corrupt_slime": CorruptSlime,
    "zombie": Zombie,
    "ice_zombie": IceZombie,
    "mummy": Mummy,
    "skeleton": Skeleton,
    "demon_eye": DemonEye,
    "night_gazer": DemonEye,
    "cave_bat": CaveBat,
    "ice_bat": IceBat,
    "desert_scorpion": DesertScorpion,
    "shadow_crawler": ShadowCrawler,
    "rock_zombie": RockZombie,
    "shield_weaver": ShieldWeaver,
    "digger": DiggerMob,
}

CLASS_TO_MOB_TYPE = {cls: k for k, cls in MOB_TYPE_REGISTRY.items()}
CLASS_TO_MOB_TYPE[DemonEye] = "demon_eye"
NightGazer = DemonEye

def create_mob_by_type(mob_type, x, y, asset_factory):
    """Factory creating an authoritative or synced mob instance by its string identifier."""
    cls = MOB_TYPE_REGISTRY.get(mob_type, GreenSlime)
    return cls(x, y, asset_factory)

