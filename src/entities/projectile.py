"""
Potaria - Projectiles Engine (Pygame-ce Powered)
Handles ballistic arrows with gravity, and Starfury's falling celestial stars
with sub-pixel pygame.FRect physics and Vector2 math.
Developer: Kurados
"""

import math
import random
import pygame
from src.constants import SCALED_TILE, TILE_BARRIER, TILE_PROPS

class ArrowProjectile:
    def __init__(self, x, y, angle_rad=0.0, speed=13.0, damage=14, angle=None, arrow_type="wooden_arrow"):
        if angle is not None:
            angle_rad = angle
        self.pos = pygame.math.Vector2(float(x), float(y))
        self.vel = pygame.math.Vector2(math.cos(angle_rad) * speed, math.sin(angle_rad) * speed)
        self.damage = damage
        self.life = 6.0
        self.stuck = False
        self.stuck_timer = 3.0
        self.radius = 6
        self.frect = pygame.FRect(self.pos.x - self.radius, self.pos.y - self.radius, self.radius * 2, self.radius * 2)
        self.arrow_type = arrow_type

    @property
    def rect(self):
        return self.frect

    def update(self, dt, world, particle_system, sound_manager, player):
        if self.stuck:
            self.stuck_timer -= dt
            if self.stuck_timer <= 0:
                self.life = 0
            return

        self.life -= dt
        # Gravity curve
        self.vel.y += 0.22
        self.pos += self.vel

        self.frect.center = self.pos

        # Arrow particle trail effects
        if particle_system:
            if self.arrow_type == "frostburn_arrow":
                particle_system.spawn_sparks(self.pos.x, self.pos.y, (120, 220, 255), count=1)
            elif "flame" in self.arrow_type or "magma" in self.arrow_type or "fire" in self.arrow_type:
                particle_system.spawn_sparks(self.pos.x, self.pos.y, (255, 140, 40), count=1)
            elif self.arrow_type in ("astral_energy", "celestial_arrow"):
                particle_system.spawn_sparks(self.pos.x, self.pos.y, (255, 230, 80), count=1)

        # Check tile collision (only solid tiles, never torches/platforms/air)
        tx = int(self.pos.x // SCALED_TILE)
        ty = int(self.pos.y // SCALED_TILE)
        tile_id = world.get_tile(tx, ty)
        if tile_id != 0 and TILE_PROPS.get(tile_id, {}).get("solid", False):
            # Hit ground: stick in place!
            self.stuck = True
            sound_manager.play_spatial("dig_wood", self.pos.x, self.pos.y, player.center_x, player.center_y)
            particle_system.spawn_debris(self.pos.x, self.pos.y, (180, 150, 100), count=4)

    def render(self, target_surf, camera, arrow_sprite=None):
        if self.life <= 0:
            return
        sx, sy = camera.world_to_screen(self.pos.x, self.pos.y)
        angle_deg = -math.degrees(math.atan2(self.vel.y, self.vel.x)) - 45
        if arrow_sprite is None:
            arrow_sprite = pygame.Surface((18, 18), pygame.SRCALPHA)
            col = (200, 150, 90)
            if self.arrow_type == "frostburn_arrow":
                col = (100, 220, 255)
            elif "flame" in self.arrow_type or "magma" in self.arrow_type or "fire" in self.arrow_type:
                col = (255, 120, 30)
            elif "astral" in self.arrow_type or "celestial" in self.arrow_type:
                col = (255, 230, 80)
            pygame.draw.line(arrow_sprite, col, (3, 15), (15, 3), 3)
            pygame.draw.line(arrow_sprite, (255, 255, 255), (12, 6), (15, 3), 2)
        rot_surf = pygame.transform.rotate(arrow_sprite, angle_deg)
        rect = rot_surf.get_rect(center=(int(sx), int(sy)))
        target_surf.blit(rot_surf, rect.topleft)

class CelestialStarProjectile:
    def __init__(self, target_world_x, target_world_y, camera_y, damage=42):
        # Spawns from high above in the heavens!
        spawn_x = target_world_x + random.uniform(-60, 60)
        spawn_y = camera_y - random.uniform(80, 140)
        self.pos = pygame.math.Vector2(spawn_x, spawn_y)
        
        # Calculate plunge vector toward target cursor
        direction = pygame.math.Vector2(target_world_x - spawn_x, target_world_y - spawn_y)
        if direction.length() > 0:
            self.vel = direction.normalize() * 14.5
        else:
            self.vel = pygame.math.Vector2(0, 14.5)

        self.target_y = target_world_y
        self.damage = damage
        self.life = 3.5
        self.exploded = False
        self.blocked_by_barrier = False
        self.radius = 12
        self.frect = pygame.FRect(self.pos.x - self.radius, self.pos.y - self.radius, self.radius * 2, self.radius * 2)
        self.rotation = 0.0

    @property
    def rect(self):
        return self.frect

    def update(self, dt, world, particle_system, sound_manager, camera, mobs, boss, player):
        if self.exploded:
            self.life = 0
            return

        self.life -= dt
        self.pos += self.vel
        self.frect.center = self.pos
        self.rotation = (self.rotation + 18.0) % 360.0

        # Shimmering celestial star particle trail
        particle_system.spawn_sparks(
            self.pos.x + random.uniform(-4, 4),
            self.pos.y + random.uniform(-4, 4),
            color=random.choice([(255, 235, 100), (80, 220, 255), (255, 140, 255)]),
            count=2
        )

        # Check tile collision
        tx = int(self.pos.x // SCALED_TILE)
        ty = int(self.pos.y // SCALED_TILE)
        tile_at = world.get_tile(tx, ty)
        hit_barrier = (tile_at == TILE_BARRIER or tile_at == 36)
        hit_tile = (tile_at != 0)

        # Check mob or boss collision
        hit_entity = False
        for mob in mobs:
            if self.frect.colliderect(mob.rect):
                hit_entity = True
                break
        if not hit_entity and boss and not boss.is_dead and self.frect.colliderect(boss.rect):
            hit_entity = True

        if hit_barrier:
            self.blocked_by_barrier = True
            self.explode(particle_system, sound_manager, camera, mobs, boss, player)
        elif hit_tile or hit_entity or self.pos.y >= self.target_y:
            self.explode(particle_system, sound_manager, camera, mobs, boss, player)

    def explode(self, particle_system, sound_manager, camera, mobs, boss, player):
        self.exploded = True
        self.life = 0

        if self.blocked_by_barrier:
            # Blocked by Shield-Weaver's magical barrier block!
            camera.add_shake(4.0, 0.2)
            sound_manager.play_spatial("hit_block", self.pos.x, self.pos.y, player.center_x, player.center_y)
            # Distinctive barrier deflection sparks
            for _ in range(20):
                particle_system.spawn_sparks(
                    self.pos.x, self.pos.y,
                    color=random.choice([(100, 200, 255), (180, 80, 255), (255, 255, 255)]),
                    count=1
                )
            # Absorbed completely by barrier: 0 damage to mobs or boss underneath!
            return

        # Screen shake on celestial impact!
        camera.add_shake(6.5, 0.25)
        sound_manager.play_spatial("explode", self.pos.x, self.pos.y, player.center_x, player.center_y)
        sound_manager.play_spatial("starfury", self.pos.x, self.pos.y, player.center_x, player.center_y)

        # Radial starburst explosion particles
        for _ in range(25):
            particle_system.spawn_sparks(
                self.pos.x, self.pos.y,
                color=random.choice([(255, 240, 80), (100, 230, 255), (255, 255, 255)]),
                count=1
            )

        # Area of Effect (AoE) Splash Damage (Radius: 72 pixels)
        splash_radius = 72.0
        is_ancient = getattr(self, "is_ancient", False)
        if is_ancient:
            for mob in mobs:
                d = math.hypot(mob.center_x - self.pos.x, mob.center_y - self.pos.y)
                if d <= splash_radius:
                    dmg = int(self.damage * (1.0 - (d / splash_radius) * 0.4))
                    mob.take_damage(dmg, knockback_vx=4.0 if mob.center_x > self.pos.x else -4.0, knockback_vy=-3.5)
        else:
            closest_mob = None
            min_d = splash_radius + 1.0
            for mob in mobs:
                d = math.hypot(mob.center_x - self.pos.x, mob.center_y - self.pos.y)
                if d <= splash_radius and d < min_d:
                    min_d = d
                    closest_mob = mob
            if closest_mob:
                dmg = int(self.damage * (1.0 - (min_d / splash_radius) * 0.4))
                closest_mob.take_damage(dmg, knockback_vx=4.0 if closest_mob.center_x > self.pos.x else -4.0, knockback_vy=-3.5)

        if boss and not boss.is_dead:
            d = math.hypot(boss.center_x - self.pos.x, boss.center_y - self.pos.y)
            if d <= splash_radius:
                boss.take_damage(self.damage, knockback_vx=2.0 if boss.center_x > self.pos.x else -2.0)

    def render(self, target_surf, camera, star_sprite):
        if self.life <= 0:
            return
        sx, sy = camera.world_to_screen(self.pos.x, self.pos.y)
        rot_surf = pygame.transform.rotate(star_sprite, self.rotation)
        r = rot_surf.get_rect(center=(int(sx), int(sy)))
        target_surf.blit(rot_surf, r.topleft)

class MobSpitProjectile:
    """Anti-cheese arcing projectile spat by obstructed mobs over player walls."""
    def __init__(self, x, y, vx, vy, damage=12, color=(80, 220, 60), radius=5):
        self.pos = pygame.math.Vector2(float(x), float(y))
        self.vel = pygame.math.Vector2(float(vx), float(vy))
        self.damage = damage
        self.color = color
        self.radius = radius
        self.life = 3.5
        self.frect = pygame.FRect(self.pos.x - self.radius, self.pos.y - self.radius, self.radius * 2, self.radius * 2)

    @property
    def rect(self):
        return self.frect

    def update(self, dt, world):
        self.life -= dt
        self.vel.y += 0.28  # Gravity arc
        self.pos += self.vel
        self.frect.center = self.pos

        # Check tile collision
        tx = int(self.pos.x // SCALED_TILE)
        ty = int(self.pos.y // SCALED_TILE)
        if hasattr(world, "is_tile_solid") and world.is_tile_solid(tx, ty):
            self.life = 0

    def render(self, target_surf, camera):
        if self.life <= 0:
            return
        sx, sy = camera.world_to_screen(self.pos.x, self.pos.y)
        pygame.draw.circle(target_surf, self.color, (int(sx), int(sy)), self.radius)
        pygame.draw.circle(target_surf, (255, 255, 255), (int(sx - 1), int(sy - 1)), max(1, self.radius - 3))


class FreezingNeedleProjectile:
    """Piercing crystalline ice needle launched by weapons with Freezing Needles."""
    def __init__(self, x, y, angle_rad, damage=24, speed=16.0, max_distance=560.0):
        self.pos = pygame.math.Vector2(float(x), float(y))
        self.start_pos = pygame.math.Vector2(float(x), float(y))
        self.vel = pygame.math.Vector2(math.cos(angle_rad) * speed, math.sin(angle_rad) * speed)
        self.damage = damage
        self.max_distance = float(max_distance)
        self.life = 2.2
        self.radius = 5
        self.frect = pygame.FRect(self.pos.x - self.radius, self.pos.y - self.radius, self.radius * 2, self.radius * 2)
        self.pierce_left = 5
        self.hit_entities = set()
        self.angle_deg = math.degrees(angle_rad)

    @property
    def rect(self):
        return self.frect

    def update(self, dt, world, particle_system, sound_manager, mobs, boss, player, combat=None):
        if self.life <= 0 or self.pierce_left <= 0:
            self.life = 0
            return

        self.life -= dt
        self.pos += self.vel
        self.frect.center = self.pos

        # Balanced range limit: dissipates into frost sparkle particles
        if (self.pos - self.start_pos).length() >= self.max_distance:
            self.life = 0
            particle_system.spawn_sparks(self.pos.x, self.pos.y, (180, 240, 255), count=8)
            return

        # Ice frost particle trail
        particle_system.spawn_sparks(
            self.pos.x + random.uniform(-2, 2),
            self.pos.y + random.uniform(-2, 2),
            color=random.choice([(180, 240, 255), (120, 210, 255), (230, 250, 255)]),
            count=2
        )

        # Pierce through mobs
        for mob in mobs:
            if mob.is_alive and mob not in self.hit_entities and self.frect.colliderect(mob.rect):
                self.hit_entities.add(mob)
                self.pierce_left -= 1
                mob.take_damage(self.damage, knockback_vx=self.vel.x * 0.25, knockback_vy=-2.0)
                if hasattr(mob, "speed"):
                    mob.speed = max(0.4, mob.speed * 0.65)
                sound_manager.play_spatial("hit_mob", self.pos.x, self.pos.y, player.center_x, player.center_y)
                particle_system.spawn_sparks(self.pos.x, self.pos.y, (160, 230, 255), count=12)
                if combat:
                    combat.spawn_damage_number(mob.center_x, mob.y - 12, self.damage, color=(160, 230, 255))
                    if getattr(combat, "is_client", False) and getattr(combat, "client", None) and combat.client.connected:
                        combat.client.send_mob_damage(getattr(mob, "mob_id", 0), self.damage, self.vel.x * 0.25, -2.0)
                    if mob.is_dead and hasattr(combat, "_on_mob_slain"):
                        combat._on_mob_slain(mob, player)
                is_ancient = getattr(self, "is_ancient", False)
                if not is_ancient or self.pierce_left <= 0:
                    self.pierce_left = 0
                    self.life = 0
                    break

        if self.pierce_left > 0 and boss and not boss.is_dead and boss not in self.hit_entities and self.frect.colliderect(boss.rect):
            self.hit_entities.add(boss)
            self.pierce_left -= 1
            boss.take_damage(self.damage, knockback_vx=self.vel.x * 0.1)
            sound_manager.play_spatial("hit_mob", self.pos.x, self.pos.y, player.center_x, player.center_y)
            particle_system.spawn_sparks(self.pos.x, self.pos.y, (160, 230, 255), count=15)
            if combat:
                combat.spawn_damage_number(boss.center_x, boss.y - 14, self.damage, color=(160, 230, 255))
                if getattr(combat, "is_client", False) and getattr(combat, "client", None) and combat.client.connected:
                    combat.client.send_mob_damage("boss", self.damage, self.vel.x * 0.1, 0.0)
            is_ancient = getattr(self, "is_ancient", False)
            if not is_ancient or self.pierce_left <= 0:
                self.pierce_left = 0
                self.life = 0

    def render(self, target_surf, camera):
        if self.life <= 0:
            return
        sx, sy = camera.world_to_screen(self.pos.x, self.pos.y)
        l = 15
        ex = sx + math.cos(math.radians(self.angle_deg)) * l
        ey = sy + math.sin(math.radians(self.angle_deg)) * l
        pygame.draw.line(target_surf, (200, 245, 255), (int(sx), int(sy)), (int(ex), int(ey)), 3)
        pygame.draw.line(target_surf, (255, 255, 255), (int(sx), int(sy)), (int(ex), int(ey)), 1)
        pygame.draw.circle(target_surf, (140, 225, 255), (int(ex), int(ey)), 3)


class AstralArrowProjectile:
    """Bonus astral arrow fired by Starlight Volley effect."""
    def __init__(self, x, y, angle_rad, damage=22, speed=15.0, max_distance=560.0):
        self.pos = pygame.math.Vector2(float(x), float(y))
        self.start_pos = pygame.math.Vector2(float(x), float(y))
        self.vel = pygame.math.Vector2(math.cos(angle_rad) * speed, math.sin(angle_rad) * speed)
        self.damage = damage
        self.max_distance = float(max_distance)
        self.life = 3.0
        self.radius = 5
        self.frect = pygame.FRect(self.pos.x - self.radius, self.pos.y - self.radius, self.radius * 2, self.radius * 2)

    @property
    def rect(self):
        return self.frect

    def update(self, dt, world, particle_system, sound_manager, mobs, boss, player, combat=None):
        if self.life <= 0:
            return
        self.life -= dt
        self.pos += self.vel
        self.frect.center = self.pos

        # Balanced range limit
        if (self.pos - self.start_pos).length() >= self.max_distance:
            self.life = 0
            particle_system.spawn_sparks(self.pos.x, self.pos.y, (255, 230, 100), count=8)
            return

        particle_system.spawn_sparks(
            self.pos.x, self.pos.y,
            color=random.choice([(255, 240, 100), (120, 200, 255), (255, 180, 255)]),
            count=1
        )

        for mob in mobs:
            if mob.is_alive and self.frect.colliderect(mob.rect):
                mob.take_damage(self.damage, knockback_vx=self.vel.x * 0.3, knockback_vy=-2.0)
                sound_manager.play_spatial("hit_mob", self.pos.x, self.pos.y, player.center_x, player.center_y)
                particle_system.spawn_sparks(self.pos.x, self.pos.y, (255, 230, 100), count=10)
                if combat:
                    combat.spawn_damage_number(mob.center_x, mob.y - 12, self.damage, color=(255, 230, 100))
                    if getattr(combat, "is_client", False) and getattr(combat, "client", None) and combat.client.connected:
                        combat.client.send_mob_damage(getattr(mob, "mob_id", 0), self.damage, self.vel.x * 0.3, -2.0)
                    if mob.is_dead and hasattr(combat, "_on_mob_slain"):
                        combat._on_mob_slain(mob, player)
                self.life = 0
                return

        if boss and not boss.is_dead and self.frect.colliderect(boss.rect):
            boss.take_damage(self.damage, knockback_vx=self.vel.x * 0.1)
            sound_manager.play_spatial("hit_mob", self.pos.x, self.pos.y, player.center_x, player.center_y)
            particle_system.spawn_sparks(self.pos.x, self.pos.y, (255, 230, 100), count=12)
            if combat:
                combat.spawn_damage_number(boss.center_x, boss.y - 14, self.damage, color=(255, 230, 100))
                if getattr(combat, "is_client", False) and getattr(combat, "client", None) and combat.client.connected:
                    combat.client.send_mob_damage("boss", self.damage, self.vel.x * 0.1, 0.0)
            self.life = 0

    def render(self, target_surf, camera):
        if self.life <= 0:
            return
        sx, sy = camera.world_to_screen(self.pos.x, self.pos.y)
        pygame.draw.circle(target_surf, (255, 240, 120), (int(sx), int(sy)), 4)
        pygame.draw.circle(target_surf, (255, 255, 255), (int(sx), int(sy)), 2)


class SolarFlareShockwave:
    """Expanding radial solar flare shockwave."""
    def __init__(self, x, y, damage=28, max_radius=80.0):
        self.x = float(x)
        self.y = float(y)
        self.damage = damage
        self.radius = 10.0
        self.max_radius = max_radius
        self.life = 0.4
        self.max_life = 0.4
        self.hit_entities = set()

    @property
    def rect(self):
        return pygame.FRect(self.x - self.radius, self.y - self.radius, self.radius * 2, self.radius * 2)

    @property
    def frect(self):
        return self.rect

    @property
    def pos(self):
        return pygame.math.Vector2(self.x, self.y)

    @pos.setter
    def pos(self, val):
        self.x = float(val.x if hasattr(val, "x") else val[0])
        self.y = float(val.y if hasattr(val, "y") else val[1])

    def update(self, dt, particle_system, sound_manager, mobs, boss, player, combat=None):
        if self.life <= 0:
            return
        self.life -= dt
        progress = 1.0 - (self.life / self.max_life)
        self.radius = 10.0 + (self.max_radius - 10.0) * progress

        for _ in range(3):
            ang = random.uniform(0, 6.28)
            rx = self.x + math.cos(ang) * self.radius
            ry = self.y + math.sin(ang) * self.radius
            particle_system.spawn_sparks(rx, ry, color=random.choice([(255, 120, 20), (255, 200, 40), (255, 60, 20)]), count=1)

        is_ancient = getattr(self, "is_ancient", False)
        for mob in mobs:
            if mob.is_alive and mob not in self.hit_entities:
                dist = math.hypot(mob.center_x - self.x, mob.center_y - self.y)
                if dist <= self.radius:
                    self.hit_entities.add(mob)
                    k_dir = 1.0 if mob.center_x > self.x else -1.0
                    mob.take_damage(self.damage, knockback_vx=k_dir * 4.5, knockback_vy=-3.0)
                    if hasattr(mob, "apply_burn"):
                        mob.apply_burn(dps=8, duration=3.0)
                    particle_system.spawn_sparks(mob.center_x, mob.center_y, (255, 140, 30), count=8)
                    if combat:
                        combat.spawn_damage_number(mob.center_x, mob.y - 12, self.damage, color=(255, 140, 30))
                        if getattr(combat, "is_client", False) and getattr(combat, "client", None) and combat.client.connected:
                            combat.client.send_mob_damage(getattr(mob, "mob_id", 0), self.damage, k_dir * 4.5, -3.0)
                        if mob.is_dead and hasattr(combat, "_on_mob_slain"):
                            combat._on_mob_slain(mob, player)
                    if not is_ancient:
                        self.life = 0
                        break

        if boss and not boss.is_dead and boss not in self.hit_entities:
            dist = math.hypot(boss.center_x - self.x, boss.center_y - self.y)
            if dist <= self.radius:
                self.hit_entities.add(boss)
                boss.take_damage(self.damage, knockback_vx=2.0)
                if hasattr(boss, "apply_burn"):
                    boss.apply_burn(dps=10, duration=3.0)
                particle_system.spawn_sparks(boss.center_x, boss.center_y, (255, 140, 30), count=12)
                if combat:
                    combat.spawn_damage_number(boss.center_x, boss.y - 14, self.damage, color=(255, 140, 30))
                    if getattr(combat, "is_client", False) and getattr(combat, "client", None) and combat.client.connected:
                        combat.client.send_mob_damage("boss", self.damage, 2.0, 0.0)
                if not is_ancient:
                    self.life = 0

    def render(self, target_surf, camera):
        if self.life <= 0:
            return
        sx, sy = camera.world_to_screen(self.x, self.y)
        pygame.draw.circle(target_surf, (255, 140, 30), (int(sx), int(sy)), int(self.radius), 3)
        pygame.draw.circle(target_surf, (255, 220, 80), (int(sx), int(sy)), max(1, int(self.radius - 2)), 1)


class GravitationalPulseProjectile:
    """Pulls enemies toward blast center then detonates."""
    def __init__(self, x, y, damage=32, pull_radius=110.0):
        self.x = float(x)
        self.y = float(y)
        self.damage = damage
        self.pull_radius = pull_radius
        self.life = 0.6
        self.max_life = 0.6
        self.exploded = False

    @property
    def rect(self):
        return pygame.FRect(self.x - self.pull_radius, self.y - self.pull_radius, self.pull_radius * 2, self.pull_radius * 2)

    @property
    def frect(self):
        return self.rect

    @property
    def pos(self):
        return pygame.math.Vector2(self.x, self.y)

    @pos.setter
    def pos(self, val):
        self.x = float(val.x if hasattr(val, "x") else val[0])
        self.y = float(val.y if hasattr(val, "y") else val[1])

    def update(self, dt, particle_system, sound_manager, mobs, boss, player, combat=None):
        if self.life <= 0:
            return
        self.life -= dt
        for mob in mobs:
            if mob.is_alive:
                dist = math.hypot(self.x - mob.center_x, self.y - mob.center_y)
                if 10.0 < dist < self.pull_radius:
                    pull_force = (1.0 - dist / self.pull_radius) * 4.5
                    ang = math.atan2(self.y - mob.center_y, self.x - mob.center_x)
                    mob.vx += math.cos(ang) * pull_force
                    mob.vy += math.sin(ang) * pull_force

        if self.life <= 0 and not self.exploded:
            self.exploded = True
            sound_manager.play_spatial("explode", self.x, self.y, player.center_x, player.center_y)
            is_ancient = getattr(self, "is_ancient", False)
            if is_ancient:
                for mob in mobs:
                    if mob.is_alive and math.hypot(self.x - mob.center_x, self.y - mob.center_y) < 65.0:
                        mob.take_damage(self.damage, knockback_vx=random.uniform(-4, 4), knockback_vy=-3.5)
                        if combat:
                            combat.spawn_damage_number(mob.center_x, mob.y - 12, self.damage, color=(200, 150, 255))
                            if getattr(combat, "is_client", False) and getattr(combat, "client", None) and combat.client.connected:
                                combat.client.send_mob_damage(getattr(mob, "mob_id", 0), self.damage, 0.0, -3.0)
                            if mob.is_dead and hasattr(combat, "_on_mob_slain"):
                                combat._on_mob_slain(mob, player)
            else:
                closest_mob = None
                min_d = 65.0
                for mob in mobs:
                    if mob.is_alive:
                        d = math.hypot(self.x - mob.center_x, self.y - mob.center_y)
                        if d < min_d:
                            min_d = d
                            closest_mob = mob
                if closest_mob:
                    closest_mob.take_damage(self.damage, knockback_vx=random.uniform(-4, 4), knockback_vy=-3.5)
                    if combat:
                        combat.spawn_damage_number(closest_mob.center_x, closest_mob.y - 12, self.damage, color=(200, 150, 255))
                        if getattr(combat, "is_client", False) and getattr(combat, "client", None) and combat.client.connected:
                            combat.client.send_mob_damage(getattr(closest_mob, "mob_id", 0), self.damage, 0.0, -3.0)
                        if closest_mob.is_dead and hasattr(combat, "_on_mob_slain"):
                            combat._on_mob_slain(closest_mob, player)
            if boss and not boss.is_dead and math.hypot(self.x - boss.center_x, self.y - boss.center_y) < 75.0:
                boss.take_damage(self.damage, knockback_vx=1.0)
                if combat:
                    combat.spawn_damage_number(boss.center_x, boss.y - 14, self.damage, color=(200, 150, 255))
                    if getattr(combat, "is_client", False) and getattr(combat, "client", None) and combat.client.connected:
                        combat.client.send_mob_damage("boss", self.damage, 1.0, 0.0)
            for _ in range(25):
                particle_system.spawn_sparks(self.x, self.y, color=random.choice([(140, 80, 220), (80, 50, 160), (220, 180, 255)]), count=1)

    def render(self, target_surf, camera):
        if self.life <= 0:
            return
        sx, sy = camera.world_to_screen(self.x, self.y)
        r = int(14 + (1.0 - self.life / self.max_life) * 18)
        pygame.draw.circle(target_surf, (140, 70, 220), (int(sx), int(sy)), r, 2)
        pygame.draw.circle(target_surf, (220, 180, 255), (int(sx), int(sy)), max(1, r // 2))


class CatalystStarProjectile:
    """Homing celestial star/orb fired by Catalysts (max 560px range)."""
    def __init__(self, x, y, vx, vy, sprite=None, damage=32, max_distance=560.0, combat=None):
        self.x = float(x)
        self.y = float(y)
        self.start_x = float(x)
        self.start_y = float(y)
        self.vx = float(vx)
        self.vy = float(vy)
        self.combat = combat
        self.speed = math.hypot(vx, vy) if math.hypot(vx, vy) > 0 else 10.5
        self.sprite = sprite
        self.damage = damage
        self.max_distance = float(max_distance)
        self.distance_traveled = 0.0
        self.life = 2.8
        self.radius = 8
        self.rotation = 0.0
        self.frect = pygame.FRect(self.x - self.radius, self.y - self.radius, self.radius * 2, self.radius * 2)

    @property
    def rect(self):
        self.frect.center = (self.x, self.y)
        return self.frect

    @property
    def pos(self):
        return pygame.math.Vector2(self.x, self.y)

    @pos.setter
    def pos(self, val):
        self.x = float(val.x if hasattr(val, "x") else val[0])
        self.y = float(val.y if hasattr(val, "y") else val[1])

    def update(self, dt, world=None, particle_system=None, mobs=None, boss=None):
        if self.life <= 0:
            return
        self.life -= dt
        self.rotation = (self.rotation + 22.0) % 360.0

        if mobs is None and self.combat is not None:
            mobs = getattr(self.combat, "mobs", None)
        if boss is None and self.combat is not None:
            boss = getattr(self.combat, "boss", None)

        target = None
        min_d = 240.0
        if mobs:
            for mob in mobs:
                if getattr(mob, "is_alive", True):
                    d = math.hypot(mob.center_x - self.x, mob.center_y - self.y)
                    if d < min_d:
                        min_d = d
                        target = (mob.center_x, mob.center_y)
        if not target and boss and not getattr(boss, "is_dead", False):
            d = math.hypot(boss.center_x - self.x, boss.center_y - self.y)
            if d < min_d:
                target = (boss.center_x, boss.center_y)

        if target:
            tx, ty = target
            ang = math.atan2(ty - self.y, tx - self.x)
            cur_speed = math.hypot(self.vx, self.vy)
            self.vx = self.vx * 0.90 + math.cos(ang) * cur_speed * 0.10
            self.vy = self.vy * 0.90 + math.sin(ang) * cur_speed * 0.10

        step = math.hypot(self.vx, self.vy)
        self.x += self.vx
        self.y += self.vy
        self.distance_traveled += step
        self.frect.center = (self.x, self.y)

        if particle_system:
            particle_system.spawn_sparks(
                self.x + random.uniform(-3, 3),
                self.y + random.uniform(-3, 3),
                color=random.choice([(255, 230, 80), (120, 220, 255), (240, 100, 255)]),
                count=1
            )

        if self.distance_traveled >= self.max_distance:
            self.life = 0
            if particle_system:
                particle_system.spawn_sparks(self.x, self.y, (255, 215, 60), count=10)

        if world is not None:
            tx = int(self.x // SCALED_TILE)
            ty = int(self.y // SCALED_TILE)
            if hasattr(world, "is_tile_solid") and world.is_tile_solid(tx, ty):
                self.life = 0
                if particle_system:
                    particle_system.spawn_sparks(self.x, self.y, (140, 210, 255), count=6)

    def render(self, target_surf, camera):
        if self.life <= 0:
            return
        sx, sy = camera.world_to_screen(self.x, self.y)
        if self.sprite:
            rot_surf = pygame.transform.rotate(self.sprite, self.rotation)
            r = rot_surf.get_rect(center=(int(sx), int(sy)))
            target_surf.blit(rot_surf, r.topleft)
        else:
            pygame.draw.circle(target_surf, (255, 225, 80), (int(sx), int(sy)), self.radius)
            pygame.draw.circle(target_surf, (140, 240, 255), (int(sx), int(sy)), max(2, self.radius - 3))
            pygame.draw.line(target_surf, (255, 255, 255), (int(sx - 10), int(sy)), (int(sx + 10), int(sy)), 2)
            pygame.draw.line(target_surf, (255, 255, 255), (int(sx), int(sy - 10)), (int(sx), int(sy + 10)), 2)


class StaffBoltProjectile:
    """Elemental magic bolt fired by Staves (max 560px range)."""
    def __init__(self, x, y, vx, vy, sprite=None, damage=28, max_distance=560.0, element="arcane"):
        self.x = float(x)
        self.y = float(y)
        self.start_x = float(x)
        self.start_y = float(y)
        self.vx = float(vx)
        self.vy = float(vy)
        self.sprite = sprite
        self.damage = damage
        self.max_distance = float(max_distance)
        self.distance_traveled = 0.0
        self.element = element
        self.life = 2.4
        self.radius = 7
        self.frect = pygame.FRect(self.x - self.radius, self.y - self.radius, self.radius * 2, self.radius * 2)

    @property
    def rect(self):
        self.frect.center = (self.x, self.y)
        return self.frect

    @property
    def pos(self):
        return pygame.math.Vector2(self.x, self.y)

    @pos.setter
    def pos(self, val):
        self.x = float(val.x if hasattr(val, "x") else val[0])
        self.y = float(val.y if hasattr(val, "y") else val[1])

    def update(self, dt, world=None, particle_system=None):
        if self.life <= 0:
            return
        self.life -= dt
        step = math.hypot(self.vx, self.vy)
        self.x += self.vx
        self.y += self.vy
        self.distance_traveled += step
        self.frect.center = (self.x, self.y)

        if particle_system:
            if self.element == "frost":
                col = (120, 220, 255)
            elif self.element == "fire":
                col = (255, 130, 40)
            elif self.element == "nature":
                col = (90, 235, 100)
            else:
                col = (190, 110, 255)
            particle_system.spawn_sparks(self.x, self.y, col, count=1)

        if self.distance_traveled >= self.max_distance:
            self.life = 0
            if particle_system:
                particle_system.spawn_sparks(self.x, self.y, (180, 140, 255), count=6)

        if world is not None:
            tx = int(self.x // SCALED_TILE)
            ty = int(self.y // SCALED_TILE)
            if hasattr(world, "is_tile_solid") and world.is_tile_solid(tx, ty):
                self.life = 0
                if particle_system:
                    particle_system.spawn_sparks(self.x, self.y, (255, 180, 50), count=6)

    def render(self, target_surf, camera):
        if self.life <= 0:
            return
        sx, sy = camera.world_to_screen(self.x, self.y)
        if self.sprite:
            ang_deg = -math.degrees(math.atan2(self.vy, self.vx))
            rot_surf = pygame.transform.rotate(self.sprite, ang_deg)
            r = rot_surf.get_rect(center=(int(sx), int(sy)))
            target_surf.blit(rot_surf, r.topleft)
        else:
            col = (255, 140, 40) if self.element == "fire" else (100, 220, 255) if self.element == "frost" else (180, 100, 255)
            pygame.draw.circle(target_surf, col, (int(sx), int(sy)), self.radius)
            pygame.draw.circle(target_surf, (255, 255, 255), (int(sx), int(sy)), max(2, self.radius - 3))


class RodJavelinProjectile:
    """High-velocity piercing javelin / spark needle fired by Rods (max 560px range)."""
    def __init__(self, x, y, vx, vy, sprite=None, damage=26, max_distance=560.0):
        self.x = float(x)
        self.y = float(y)
        self.start_x = float(x)
        self.start_y = float(y)
        self.vx = float(vx)
        self.vy = float(vy)
        self.sprite = sprite
        self.damage = damage
        self.max_distance = float(max_distance)
        self.distance_traveled = 0.0
        self.life = 2.0
        self.radius = 6
        self.pierce_left = 3
        self.hit_entities = set()
        self.frect = pygame.FRect(self.x - self.radius, self.y - self.radius, self.radius * 2, self.radius * 2)

    @property
    def rect(self):
        self.frect.center = (self.x, self.y)
        return self.frect

    @property
    def pos(self):
        return pygame.math.Vector2(self.x, self.y)

    @pos.setter
    def pos(self, val):
        self.x = float(val.x if hasattr(val, "x") else val[0])
        self.y = float(val.y if hasattr(val, "y") else val[1])

    def update(self, dt, world=None, particle_system=None):
        if self.life <= 0:
            return
        self.life -= dt
        step = math.hypot(self.vx, self.vy)
        self.x += self.vx
        self.y += self.vy
        self.distance_traveled += step
        self.frect.center = (self.x, self.y)

        if particle_system:
            particle_system.spawn_sparks(self.x, self.y, (120, 240, 255), count=1)

        if self.distance_traveled >= self.max_distance:
            self.life = 0
            if particle_system:
                particle_system.spawn_sparks(self.x, self.y, (140, 240, 255), count=6)

        if world is not None:
            tx = int(self.x // SCALED_TILE)
            ty = int(self.y // SCALED_TILE)
            if hasattr(world, "is_tile_solid") and world.is_tile_solid(tx, ty):
                self.life = 0
                if particle_system:
                    particle_system.spawn_sparks(self.x, self.y, (180, 240, 255), count=6)

    def render(self, target_surf, camera):
        if self.life <= 0:
            return
        sx, sy = camera.world_to_screen(self.x, self.y)
        ang_deg = -math.degrees(math.atan2(self.vy, self.vx))
        if self.sprite:
            rot_surf = pygame.transform.rotate(self.sprite, ang_deg)
            r = rot_surf.get_rect(center=(int(sx), int(sy)))
            target_surf.blit(rot_surf, r.topleft)
        else:
            rad = math.radians(ang_deg)
            ex = sx + math.cos(rad) * 14
            ey = sy - math.sin(rad) * 14
            pygame.draw.line(target_surf, (140, 230, 255), (int(sx), int(sy)), (int(ex), int(ey)), 3)
            pygame.draw.line(target_surf, (255, 255, 255), (int(sx), int(sy)), (int(ex), int(ey)), 1)


class ScepterPulseProjectile:
    """Expanding arcane shockwave pulse fired by Scepters (max 560px range)."""
    def __init__(self, x, y, vx, vy, sprite=None, damage=34, max_distance=560.0):
        self.x = float(x)
        self.y = float(y)
        self.start_x = float(x)
        self.start_y = float(y)
        self.vx = float(vx)
        self.vy = float(vy)
        self.sprite = sprite
        self.damage = damage
        self.max_distance = float(max_distance)
        self.distance_traveled = 0.0
        self.life = 2.4
        self.radius = 9
        self.frect = pygame.FRect(self.x - self.radius, self.y - self.radius, self.radius * 2, self.radius * 2)

    @property
    def rect(self):
        self.frect.center = (self.x, self.y)
        return self.frect

    @property
    def pos(self):
        return pygame.math.Vector2(self.x, self.y)

    @pos.setter
    def pos(self, val):
        self.x = float(val.x if hasattr(val, "x") else val[0])
        self.y = float(val.y if hasattr(val, "y") else val[1])

    def update(self, dt, world=None, particle_system=None):
        if self.life <= 0:
            return
        self.life -= dt
        step = math.hypot(self.vx, self.vy)
        self.x += self.vx
        self.y += self.vy
        self.distance_traveled += step
        self.frect.center = (self.x, self.y)

        if particle_system:
            particle_system.spawn_sparks(self.x, self.y, (210, 100, 255), count=1)

        if self.distance_traveled >= self.max_distance:
            self.life = 0
            if particle_system:
                particle_system.spawn_sparks(self.x, self.y, (220, 120, 255), count=8)

        if world is not None:
            tx = int(self.x // SCALED_TILE)
            ty = int(self.y // SCALED_TILE)
            if hasattr(world, "is_tile_solid") and world.is_tile_solid(tx, ty):
                self.life = 0
                if particle_system:
                    particle_system.spawn_sparks(self.x, self.y, (220, 140, 255), count=6)

    def render(self, target_surf, camera):
        if self.life <= 0:
            return
        sx, sy = camera.world_to_screen(self.x, self.y)
        if self.sprite:
            ang_deg = -math.degrees(math.atan2(self.vy, self.vx))
            rot_surf = pygame.transform.rotate(self.sprite, ang_deg)
            r = rot_surf.get_rect(center=(int(sx), int(sy)))
            target_surf.blit(rot_surf, r.topleft)
        else:
            pygame.draw.circle(target_surf, (190, 80, 240), (int(sx), int(sy)), self.radius, 2)
            pygame.draw.circle(target_surf, (240, 180, 255), (int(sx), int(sy)), max(2, self.radius - 3))

