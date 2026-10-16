"""
Potaria - Player Entity: Spud the Potato Hero (RPG Integrated)
Features infinite horizontal open-world movement, Chroisen-style RPG stats,
equipment paperdoll integration, active skill casting (Q, F, C, R), and food buffs.
Developer: Kurados
"""

import math
import random
import pygame
from src.constants import (
    SCALED_TILE, GRAVITY, TERMINAL_VELOCITY, PLAYER_SPEED,
    PLAYER_ACCEL, PLAYER_FRICTION, PLAYER_JUMP_FORCE, PLAYER_DROP_THROUGH_TIME,
    PLAYER_WIDTH, PLAYER_HEIGHT, PLAYER_SPRITE_WIDTH, PLAYER_SPRITE_HEIGHT,
    TILE_ROPE_RUNGS, TILE_WOOD_PLATFORM
)
from src.rpg.stats import PlayerStats
from src.rpg.equipment import Equipment, ARMOR_DATA
from src.rpg.skills import SkillManager, SKILL_DEFINITIONS

# Provisional Meal Buff Caps (Potaria Game Balance Plan Section 6.4)
MEAL_BUFF_CAPS = {
    "damage_mult": 0.12,
    "ranged_damage_mult": 0.12,
    "atk_speed_mult": 0.10,
    "crit_chance": 0.06,
    "crit_dmg_mult": 0.16,
    "armor_pen": 0.10,
    "def": 6,
    "dmg_reduction": 0.06,
    "magic_res": 0.15,
    "speed_mult": 0.15,
    "jump_mult": 0.15,
    "dash_mult": 0.15,
    "knockback_res": 0.15,
    "hp_regen": 2.0,
    "mp_regen": 2.0,
    "mana_cost_reduction": 0.15,
    "luck": 0.10,
    "gathering_speed": 0.20,
    "fishing_power": 0.15,
}

class PlayerFireball:
    def __init__(self, x, y, vx, vy, sprite, damage=24, max_distance=560.0):
        self.x = float(x)
        self.y = float(y)
        self.start_x = float(x)
        self.start_y = float(y)
        self.vx = vx
        self.vy = vy
        self.sprite = sprite
        self.radius = 10
        self.life = 2.5
        self.damage = damage
        self.max_distance = float(max_distance)
        self.distance_traveled = 0.0
        self.frect = pygame.FRect(self.x - self.radius, self.y - self.radius, self.radius * 2, self.radius * 2)

    @property
    def rect(self):
        self.frect.x = self.x - self.radius
        self.frect.y = self.y - self.radius
        return self.frect

    def update(self, dt, world=None, particle_system=None):
        self.life -= dt
        step = math.hypot(self.vx, self.vy)
        self.x += self.vx
        self.y += self.vy
        self.distance_traveled += step

        # Staff limited long range: dissipates with sparkle particles
        if self.max_distance is not None and self.distance_traveled >= self.max_distance:
            self.life = 0
            if particle_system:
                particle_system.spawn_sparks(self.x, self.y, (180, 120, 255), count=8)
            return

        if world is not None:
            tx = int(self.x // SCALED_TILE)
            ty = int(self.y // SCALED_TILE)
            if hasattr(world, "is_tile_solid") and world.is_tile_solid(tx, ty):
                self.life = 0
                if particle_system:
                    particle_system.spawn_sparks(self.x, self.y, (255, 140, 40), count=6)

    def render(self, target_surf, camera):
        sx, sy = camera.world_to_screen(self.x - 12, self.y - 12)
        target_surf.blit(self.sprite, (sx, sy))

class Player:
    def __init__(self, spawn_x, spawn_y, asset_factory, sound_manager):
        self.x = float(spawn_x)
        self.y = float(spawn_y)
        self.vx = 0.0
        self.vy = 0.0
        
        # Spud potato dimensions: 28 px wide x 32 px high (1 block body collider; head sprout leaf is decorative)
        self.width = PLAYER_WIDTH
        self.height = PLAYER_HEIGHT
        self.sprite_width = PLAYER_SPRITE_WIDTH
        self.sprite_height = PLAYER_SPRITE_HEIGHT
        self.sprout_offset_y = self.sprite_height - self.height
        self.frect = pygame.FRect(self.x, self.y, self.width, self.height)
        
        self.asset_factory = asset_factory
        self.sound_manager = sound_manager

        # RPG Systems
        self.stats = PlayerStats()
        self.equipment = Equipment()
        self.skills = SkillManager()
        self.inventory = None
        self.equipment.recalculate_stats(self.stats)
        self._current_held_id = None

        # Combat & Invincibility
        self.i_frame_timer = 0.0
        self.is_dead = False
        self.respawn_timer = 0.0
        self.dash_timer = 0.0
        self.death_fade_alpha = 0
        self.death_teleported = False
        self.snap_camera_instant = False

        # Projectiles & Skills
        self.fireballs = []
        self.fireball_sprite = pygame.transform.scale(asset_factory.boss["fireball"], (24, 24))
        self.vfx_manager = None

        # Catalog Passive Gear Buff States
        self.radiant_shield_hp = 40.0
        self.radiant_shield_max = 40.0
        self.radiant_shield_timer = 0.0
        self.starch_barrier_cd = 0.0
        self.eternal_bloom_cd = 0.0
        self.life_surge_timer = 0.0

        # Timed Meal Buffs System (Max 5 categories: offense, defense, mobility, resource, utility)
        self.meal_buffs = {}
        self.meal_regen_timer = 0.0

        # Bullet-Hell Grazing Mechanics (Touhou / Enter the Gungeon style)
        self.graze_count = 0
        self.graze_timer = 0.0

        # Furniture & Bed Resting System
        self.spawn_point = None
        self.is_resting = False
        self.bed_heal_timer = 0.0
        self.resting_bed_pos = None

        # Water Swimming & Oxygen / Breath System
        self.in_water = False
        self.is_submerged = False
        self.max_oxygen = 100.0
        self.oxygen = 100.0
        self.drown_timer = 0.0
        self.submerged_duration = 0.0
        self.killed_by_boss = False
        self.in_boss_fight = False

        # State & 12 FPS Animation System
        self.facing_right = True
        self.on_ground = False
        self.on_rope_rungs = False
        self.on_scaffolding = False
        self.on_climbable = False
        self._climb_up_input = False
        self._climb_down_input = False
        self.anim_timer = 0.0
        self.walk_frame_idx = 0
        self.idle_frame_idx = 0
        self.ignore_platforms_timer = 0

        # Tool / Weapon Swing & Attack Fire Rate Cooldown
        self.is_swinging = False
        self.swing_progress = 0.0
        self.swing_duration = 0.24
        self.attack_cooldown = 0.0
        self.max_attack_cooldown = 0.24
        self.swing_hit_targets = set()
        self.aim_angle = 0.0

        # Scale Spud Potato Sprites (12 FPS 6-frame idle, 8-frame walk, jump, fall)
        idle_raw = asset_factory.player_sprites.get("idle_frames", [asset_factory.player_sprites["idle"]])
        self.idle_sprites = [pygame.transform.scale(f, (self.sprite_width, self.sprite_height)) for f in idle_raw]
        self.idle_sprite = self.idle_sprites[0]
        self.jump_sprite = pygame.transform.scale(asset_factory.player_sprites["jump"], (self.sprite_width, self.sprite_height))
        self.fall_sprite = pygame.transform.scale(asset_factory.player_sprites.get("fall", asset_factory.player_sprites["jump"]), (self.sprite_width, self.sprite_height))
        self.walk_sprites = [
            pygame.transform.scale(f, (self.sprite_width, self.sprite_height))
            for f in asset_factory.player_sprites["walk"]
        ]
        self.arm_sprite = pygame.transform.scale(asset_factory.player_sprites["arm"], (12, 18))

    @property
    def rect(self):
        self.frect.x = self.x
        self.frect.y = self.y
        self.frect.width = self.width
        self.frect.height = self.height
        return self.frect

    @property
    def center_x(self):
        return self.x + self.width / 2.0

    @center_x.setter
    def center_x(self, val):
        self.x = float(val) - self.width / 2.0

    @property
    def center_y(self):
        return self.y + self.height / 2.0

    @center_y.setter
    def center_y(self, val):
        self.y = float(val) - self.height / 2.0

    @property
    def health(self):
        return self.stats.hp

    @health.setter
    def health(self, val):
        self.stats.hp = max(0, min(self.stats.max_hp, val))

    @property
    def max_health(self):
        return self.stats.max_hp

    @max_health.setter
    def max_health(self, val):
        self.stats.max_hp = val

    @property
    def current_anim(self):
        """Current 12 FPS animation state for networking and sprites."""
        if not self.on_ground:
            return "jump" if self.vy < -0.5 else "fall"
        elif abs(self.vx) > 0.2:
            return "walk"
        else:
            return "idle"

    def check_climbable(self, world):
        """Checks if the player's hitbox overlaps rope rungs or scaffolding/platforms."""
        if world is None or not hasattr(world, "get_tile"):
            self.on_rope_rungs = False
            self.on_scaffolding = False
            self.rope_below = False
            self.scaffold_below = False
            self.on_climbable = False
            return False
        min_tx = int((self.rect.left + 4) // SCALED_TILE)
        max_tx = int((self.rect.right - 5) // SCALED_TILE)
        min_ty = int((self.rect.top + 2) // SCALED_TILE)
        max_ty = int(self.rect.bottom // SCALED_TILE)
        body_max_ty = int((self.rect.bottom - 1) // SCALED_TILE)
        found_rope = False
        found_scaffold = False
        rope_below = False
        scaffold_below = False
        for tx in range(min_tx, max_tx + 1):
            for ty in range(min_ty, max_ty + 1):
                tid = world.get_tile(tx, ty)
                if tid == TILE_ROPE_RUNGS:
                    if ty <= body_max_ty:
                        found_rope = True
                    else:
                        rope_below = True
                elif tid == TILE_WOOD_PLATFORM:
                    if ty <= body_max_ty:
                        found_scaffold = True
                    else:
                        scaffold_below = True
        self.on_rope_rungs = found_rope
        self.on_scaffolding = found_scaffold
        self.rope_below = rope_below
        self.scaffold_below = scaffold_below
        self.on_climbable = found_rope or found_scaffold
        return self.on_climbable

    def handle_input(self, keys, mouse_world_x, mouse_world_y, key_bindings=None, world=None):
        if self.is_dead:
            return

        self.aim_angle = math.atan2(mouse_world_y - self.center_y, mouse_world_x - self.center_x)
        self.facing_right = (mouse_world_x >= self.center_x)

        # Base speed combined with RPG stats, gear, and food buffs
        meal_spd = self.get_meal_buff_val("speed_mult")
        speed_cap = self.stats.total_speed * getattr(self, "speed_multiplier", 1.0) * (1.0 + meal_spd)
        if self.dash_timer > 0:
            meal_dash = self.get_meal_buff_val("dash_mult")
            speed_cap *= (2.2 * (1.0 + meal_dash))  # Dash burst!

        # Configurable key mappings
        k_left = key_bindings.get("Move Left", pygame.K_a) if key_bindings else pygame.K_a
        k_right = key_bindings.get("Move Right", pygame.K_d) if key_bindings else pygame.K_d
        k_drop = key_bindings.get("Drop Platform", pygame.K_s) if key_bindings else pygame.K_s
        k_jump = key_bindings.get("Jump", pygame.K_SPACE) if key_bindings else pygame.K_SPACE

        def is_down(k):
            if isinstance(keys, dict):
                return keys.get(k, False)
            try:
                return bool(keys[k])
            except (IndexError, KeyError):
                return False

        moving = False
        if is_down(k_left) or is_down(pygame.K_LEFT):
            self.vx = max(-speed_cap, self.vx - PLAYER_ACCEL)
            moving = True
        if is_down(k_right) or is_down(pygame.K_RIGHT):
            self.vx = min(speed_cap, self.vx + PLAYER_ACCEL)
            moving = True

        up_held = bool(is_down(k_jump) or is_down(pygame.K_UP) or is_down(pygame.K_w))
        down_held = bool(is_down(k_drop) or is_down(pygame.K_DOWN) or is_down(pygame.K_s))
        self._climb_up_input = up_held
        self._climb_down_input = down_held

        if world is not None:
            self.check_climbable(world)

        if moving or up_held or down_held:
            self.is_resting = False

        if not moving and self.dash_timer <= 0:
            if self.vx > 0:
                self.vx = max(0.0, self.vx - PLAYER_FRICTION)
            elif self.vx < 0:
                self.vx = min(0.0, self.vx + PLAYER_FRICTION)

        if self.on_rope_rungs:
            if up_held:
                self.vy = -3.8
                self.on_ground = False
            elif down_held:
                self.vy = 3.2
                self.ignore_platforms_timer = max(self.ignore_platforms_timer, PLAYER_DROP_THROUGH_TIME)
                self.on_ground = False
            else:
                self.vy = 0.0
        elif self.on_scaffolding and (up_held or down_held):
            if up_held:
                self.vy = -3.8
                self.on_ground = False
            elif down_held:
                self.vy = max(self.vy, 3.2)
                self.ignore_platforms_timer = max(self.ignore_platforms_timer, PLAYER_DROP_THROUGH_TIME)
                self.on_ground = False
        elif (getattr(self, "rope_below", False) or getattr(self, "scaffold_below", False)) and down_held:
            self.vy = max(self.vy, 3.2)
            self.ignore_platforms_timer = max(self.ignore_platforms_timer, PLAYER_DROP_THROUGH_TIME)
            self.on_ground = False
        elif self.in_water:
            # Water swimming controls: paddling up with Jump/Up/W, diving with Drop/Down/S
            if up_held:
                if self.vy > 0:
                    self.vy = -1.8
                else:
                    self.vy = max(-3.6, self.vy - 1.4)
            if down_held:
                if self.vy < 0:
                    self.vy = 1.2
                else:
                    self.vy = min(2.8, self.vy + 0.8)
                self.ignore_platforms_timer = PLAYER_DROP_THROUGH_TIME
        else:
            if is_down(k_drop) or is_down(pygame.K_DOWN):
                self.ignore_platforms_timer = PLAYER_DROP_THROUGH_TIME

            if (is_down(k_jump) or is_down(pygame.K_UP)) and self.on_ground:
                meal_jump = self.get_meal_buff_val("jump_mult")
                self.vy = PLAYER_JUMP_FORCE * (1.0 + meal_jump)
                self.on_ground = False

                if not self.is_head_blocked(world):
                    self.sound_manager.play("jump")

    def is_head_blocked(self, world) -> bool:
        """
        Checks if the player's head is directly blocked by a solid non-platform ceiling block.
        Returns True if head is blocked, False if open space exists above head.
        """
        if world is None:
            return False
        try:
            from src.constants import SCALED_TILE
            head_tx = int((self.x + self.width * 0.5) // SCALED_TILE)
            head_ty = int(self.y // SCALED_TILE)
            if hasattr(world, "is_solid") and world.is_solid(head_tx, head_ty - 1):
                return True
        except Exception:
            pass

        if hasattr(world, "get_solid_rects_in_bounds"):
            head_box = pygame.Rect(int(self.x + 4), int(self.y - 6), int(self.width - 8), 6)
            for s_rect, is_plat in world.get_solid_rects_in_bounds(head_box):
                if not is_plat and head_box.colliderect(s_rect):
                    return True
        return False

    def cast_skill_hotkey(self, key_name, particle_system, camera):
        """Executes active skill mapped to hotkey (Q, F, V, R)."""
        k = key_name.upper()
        if k == "C":
            k = "V"
        s_id = self.skills.hotkey_bindings.get(k)
        if not s_id:
            mapping = {"Q": "power_slash", "F": "whirlwind", "V": "dash", "R": "fireball"}
            s_id = mapping.get(k)
        if not s_id:
            return False

        can_use, reason = self.skills.can_use_skill(s_id, self.stats, player=self)
        if not can_use:
            if hasattr(self, "inventory") and self.inventory and hasattr(self.inventory, "notify"):
                self.inventory.notify(f"Skill [{k}]: {reason}", timer=1.8)
            self.sound_manager.play("hurt")
            particle_system.spawn_sparks(self.center_x, self.center_y - 12, (220, 80, 80), count=6)
            return False

        success = self.skills.use_skill(s_id, self.stats, player=self)
        if not success:
            return False

        self.sound_manager.play("swing")

        if s_id == "power_slash":
            # Power slash slashes towards cursor direction (left or right only)
            is_right = (math.cos(self.aim_angle) >= 0)
            self.facing_right = is_right
            self.start_swing()
            px = self.center_x + (36 if is_right else -36)
            particle_system.spawn_sparks(px, self.center_y, (255, 230, 80), count=25)
            camera.add_shake(5.0, 0.25)
            if self.vfx_manager:
                flip_x = not is_right
                self.vfx_manager.spawn("power_slash", px, self.center_y, duration=0.45, scale=1.4, flip_x=flip_x)
                self.vfx_manager.spawn("ancient_cleave_grand", px, self.center_y, duration=0.45, scale=1.2, flip_x=flip_x)

        elif s_id == "whirlwind":
            self.start_swing()
            particle_system.spawn_debris(self.center_x, self.center_y, (100, 200, 255), count=35)
            particle_system.spawn_sparks(self.center_x, self.center_y, (255, 255, 255), count=20)
            camera.add_shake(7.0, 0.4)
            if self.vfx_manager:
                self.vfx_manager.spawn("whirlwind", self.center_x, self.center_y, duration=0.55, scale=1.5, anchor=self)
                self.vfx_manager.spawn("cryo_frost_shatter", self.center_x, self.center_y, duration=0.50, scale=1.2)

        elif s_id == "dash":
            is_phantom = hasattr(self.skills, "is_skill_evolved") and self.skills.is_skill_evolved("dash")
            self.dash_timer = 0.35
            self.i_frame_timer = 0.45 if is_phantom else 0.4
            dash_speed = 13.0 if is_phantom else 11.5
            self.vx = math.cos(self.aim_angle) * dash_speed
            self.vy = math.sin(self.aim_angle) * dash_speed
            if abs(self.vx) > 0.3:
                self.facing_right = (self.vx > 0)
            if self.vy < 0:
                self.on_ground = False
            spark_color = (180, 100, 255) if is_phantom else (255, 255, 255)
            particle_system.spawn_sparks(self.center_x, self.center_y, spark_color, count=25 if is_phantom else 20)
            dash_rot = -math.degrees(self.aim_angle)
            if self.vfx_manager:
                self.vfx_manager.spawn("dash", self.center_x, self.center_y, duration=0.35, scale=1.4 if is_phantom else 1.3, rot_deg=dash_rot)
                self.vfx_manager.spawn("starlight_volley_burst", self.center_x, self.center_y, duration=0.35, scale=1.2 if is_phantom else 1.1, rot_deg=dash_rot)
                if is_phantom:
                    self.vfx_manager.spawn("quantum_fold_rift", self.center_x, self.center_y, duration=0.4, scale=1.2)

        elif s_id == "fireball":
            angle = self.aim_angle
            speed = 7.5
            fb_vx = math.cos(angle) * speed
            fb_vy = math.sin(angle) * speed
            self.fireballs.append(PlayerFireball(self.center_x, self.center_y, fb_vx, fb_vy, self.fireball_sprite))
            particle_system.spawn_sparks(self.center_x, self.center_y, (255, 120, 30), count=18)
            camera.add_shake(4.0, 0.2)
            if self.vfx_manager:
                self.vfx_manager.spawn("fireball_detonation", self.center_x + fb_vx * 2, self.center_y + fb_vy * 2, duration=0.4, scale=1.3)
                self.vfx_manager.spawn("solar_flare_supernova", self.center_x + fb_vx * 2, self.center_y + fb_vy * 2, duration=0.5, scale=1.1)

        elif s_id == "meteor":
            lvl = self.skills.get_skill_level("meteor") if hasattr(self.skills, "get_skill_level") else 1
            camera.add_shake(15.0, 0.75)
            particle_system.spawn_sparks(self.center_x, self.center_y, (255, 100, 20), count=50)
            particle_system.spawn_debris(self.center_x, self.center_y, (200, 80, 20), count=35)
            mx = self.center_x + (150 if self.facing_right else -150)
            my = self.center_y - 260
            meteor_dmg = int(self.stats.total_atk * (3.5 + lvl * 0.5))
            self.fireballs.append(PlayerFireball(mx, my, 0.0, 13.0, self.fireball_sprite, damage=meteor_dmg))
            if self.vfx_manager:
                self.vfx_manager.spawn("meteor_impact", mx, self.center_y, duration=0.7, scale=1.6)
                self.vfx_manager.spawn("solar_flare_supernova", mx, self.center_y, duration=0.6, scale=1.5)
                self.vfx_manager.spawn("grand_celestial_starfall", mx, self.center_y - 40, duration=0.8, scale=1.4)

        elif s_id == "frost_nova":
            lvl = self.skills.get_skill_level("frost_nova") if hasattr(self.skills, "get_skill_level") else 1
            camera.add_shake(8.0, 0.4)
            particle_system.spawn_sparks(self.center_x, self.center_y, (120, 220, 255), count=45)
            nova_dmg = int(self.stats.total_atk * (1.2 + lvl * 0.25))
            for ang in [i * (math.pi / 4.0) for i in range(8)]:
                f_vx = math.cos(ang) * (6.5 + lvl * 0.5)
                f_vy = math.sin(ang) * (6.5 + lvl * 0.5)
                self.fireballs.append(PlayerFireball(self.center_x, self.center_y, f_vx, f_vy, self.fireball_sprite, damage=nova_dmg))
            if self.vfx_manager:
                self.vfx_manager.spawn("frost_nova", self.center_x, self.center_y, duration=0.6, scale=1.5)
                self.vfx_manager.spawn("cryo_frost_shatter", self.center_x, self.center_y, duration=0.6, scale=1.4)

        elif s_id == "celestial_shield":
            lvl = self.skills.get_skill_level("celestial_shield") if hasattr(self.skills, "get_skill_level") else 1
            camera.add_shake(9.0, 0.4)
            self.i_frame_timer = 3.0 + lvl * 0.5
            particle_system.spawn_sparks(self.center_x, self.center_y, (255, 230, 80), count=60)
            particle_system.spawn_debris(self.center_x, self.center_y, (100, 220, 255), count=30)
            if self.vfx_manager:
                self.vfx_manager.spawn("celestial_shield", self.center_x, self.center_y, duration=1.5, scale=1.4, anchor=self)
                self.vfx_manager.spawn("ancient_radiant_aura", self.center_x, self.center_y, duration=1.5, scale=1.3, anchor=self)

        elif s_id == "void_singularity":
            lvl = self.skills.get_skill_level("void_singularity") if hasattr(self.skills, "get_skill_level") else 1
            camera.add_shake(16.0, 0.85)
            particle_system.spawn_sparks(self.center_x, self.center_y, (160, 60, 255), count=70)
            particle_system.spawn_debris(self.center_x, self.center_y, (40, 10, 80), count=40)
            v_dir = 1.0 if self.facing_right else -1.0
            vx_pos = self.center_x + v_dir * 120
            void_dmg = int(self.stats.total_atk * (4.0 + lvl * 0.6))
            self.fireballs.append(PlayerFireball(vx_pos, self.center_y - 20, 0.0, 0.2, self.fireball_sprite, damage=void_dmg))
            if self.vfx_manager:
                self.vfx_manager.spawn("void_singularity", vx_pos, self.center_y - 20, duration=1.2, scale=1.5)
                self.vfx_manager.spawn("thunderclap_strike", vx_pos, self.center_y - 40, duration=0.8, scale=1.4)

        elif s_id == "earth_slam":
            lvl = self.skills.get_skill_level("earth_slam") if hasattr(self.skills, "get_skill_level") else 1
            is_evolved = hasattr(self.skills, "is_skill_evolved") and self.skills.is_skill_evolved("earth_slam")
            camera.add_shake(12.0 if is_evolved else 9.0, 0.5)
            self.start_swing()
            particle_system.spawn_debris(self.center_x, self.center_y + 12, (150, 105, 50), count=45 if is_evolved else 30)
            particle_system.spawn_sparks(self.center_x, self.center_y + 10, (235, 180, 80), count=30 if is_evolved else 20)
            slam_dmg = int(self.stats.total_atk * (2.2 + lvl * 0.35))
            slam_dir = 1.0 if self.facing_right else -1.0
            slam_x = self.center_x + slam_dir * 32
            self.fireballs.append(PlayerFireball(slam_x, self.center_y + 8, slam_dir * 3.5, 0.0, self.fireball_sprite, damage=slam_dmg))
            if self.vfx_manager:
                self.vfx_manager.spawn("earth_slam", slam_x, self.center_y + 10, duration=0.6, scale=1.6 if is_evolved else 1.3)
                self.vfx_manager.spawn("thunderclap_strike", slam_x, self.center_y, duration=0.5, scale=1.3 if is_evolved else 1.0)

        elif s_id == "shield_bash":
            lvl = self.skills.get_skill_level("shield_bash") if hasattr(self.skills, "get_skill_level") else 1
            is_evolved = hasattr(self.skills, "is_skill_evolved") and self.skills.is_skill_evolved("shield_bash")
            self.dash_timer = 0.25
            self.i_frame_timer = 0.7 if is_evolved else 0.5
            bash_speed = 9.0 if is_evolved else 7.5
            b_dir = 1.0 if self.facing_right else -1.0
            self.vx = b_dir * bash_speed
            self.vy = -1.0
            camera.add_shake(7.0 if is_evolved else 5.0, 0.3)
            particle_system.spawn_sparks(self.center_x + b_dir * 16, self.center_y, (100, 220, 255), count=25)
            bash_dmg = int(self.stats.total_atk * (1.5 + lvl * 0.25))
            bash_x = self.center_x + b_dir * 28
            self.fireballs.append(PlayerFireball(bash_x, self.center_y, b_dir * 4.0, 0.0, self.fireball_sprite, damage=bash_dmg))
            if self.vfx_manager:
                self.vfx_manager.spawn("shield_bash", bash_x, self.center_y, duration=0.45, scale=1.4 if is_evolved else 1.2)
                self.vfx_manager.spawn("ancient_cleave_grand", bash_x, self.center_y, duration=0.4, scale=1.1)

        return True

    def can_attack(self):
        """Returns True if the player is off attack cooldown and ready to strike or fire."""
        return self.attack_cooldown <= 0.0

    def trigger_attack(self, cooldown):
        """Initiates an attack, sets attack cooldown (fire rate), and synchronizes visual swing duration."""
        atk_speed = self.get_meal_buff_val("atk_speed_mult")
        if atk_speed > 0:
            cooldown = cooldown / (1.0 + atk_speed)
        self.attack_cooldown = max(0.08, cooldown)
        self.max_attack_cooldown = self.attack_cooldown
        self.swing_duration = max(0.10, min(cooldown, 0.45))
        self.is_swinging = True
        self.swing_progress = 0.0
        self.swing_hit_targets = set()

    def start_swing(self):
        if not self.is_swinging:
            self.is_swinging = True
            self.swing_progress = 0.0
            self.swing_hit_targets = set()

    def get_meal_buff_val(self, stat_name: str) -> float:
        """Returns the total active meal buff contribution for stat_name, bounded by provisional caps."""
        if not hasattr(self, "meal_buffs") or not self.meal_buffs:
            return 0.0
        total = 0.0
        for b in self.meal_buffs.values():
            stats = b.get("stats", {})
            if stat_name in stats:
                total += stats[stat_name]
        cap = MEAL_BUFF_CAPS.get(stat_name)
        if cap is not None:
            if total > 0:
                total = min(total, cap)
            elif total < 0:
                total = max(total, -cap)
        return total

    def consume_item(self, item_id):
        from src.ui.inventory import ITEM_REGISTRY
        data = ITEM_REGISTRY.get(item_id, {})
        consumed = False

        if item_id == "healing_potion":
            self.health += 50
            consumed = True
        elif item_id == "greater_healing_potion":
            self.health += 120
            consumed = True
        elif item_id == "speed_potion":
            self.stats.bonus_speed = 1.0
            consumed = True
        elif item_id == "night_gazer_elixir":
            self.health += 20
            if hasattr(self, "stats"):
                self.stats.mp = min(self.stats.max_mp, self.stats.mp + 25)
            consumed = True
        elif item_id == "zephyr_tonic":
            self.health += 25
            if hasattr(self, "stats"):
                self.stats.mp = min(self.stats.max_mp, self.stats.mp + 15)
                self.stats.bonus_speed = max(getattr(self.stats, "bonus_speed", 0.0), 1.0)
            consumed = True
        elif item_id == "gilded_russet":
            self.health = self.max_health
            if hasattr(self, "stats"):
                self.stats.mp = self.stats.max_mp
                self.stats.bonus_speed = max(getattr(self.stats, "bonus_speed", 0.0), 0.8)
            consumed = True
        else:
            heal_val = data.get("heal", 0)
            if heal_val > 0:
                self.health += heal_val
                consumed = True
            mp_val = data.get("mp", 0)
            if mp_val > 0 and hasattr(self, "stats"):
                self.stats.mp = min(self.stats.max_mp, self.stats.mp + mp_val)
                consumed = True

        # Meal buff handling (max 5 active buffs, 1 per category: offense, defense, mobility, resource, utility)
        buff = data.get("buff")
        if buff:
            cat = str(buff.get("category", "")).lower()
            if cat in ("offense", "defense", "mobility", "resource", "utility"):
                if not hasattr(self, "meal_buffs"):
                    self.meal_buffs = {}
                dur = float(buff.get("duration", 180))
                # Eating a meal in an occupied category replaces that category's current buff; duration does not stack
                self.meal_buffs[cat] = {
                    "item_id": item_id,
                    "name": buff.get("name", data.get("name", item_id)),
                    "category": cat,
                    "duration": dur,
                    "max_duration": dur,
                    "stats": dict(buff.get("stats", {})),
                    "effects": list(data.get("effects", [])),
                    "icon": item_id
                }
                consumed = True

        # Cleanse status debuffs if requested
        if data.get("cleanse") or item_id == "herbal_salve":
            consumed = True

        if consumed:
            self.health = min(self.max_health, self.health)
            if hasattr(self, "sound_manager") and self.sound_manager:
                self.sound_manager.play("craft")
            return True
        return False

    def has_effect(self, kw):
        if hasattr(self, "equipment") and hasattr(self.equipment, "has_effect"):
            if self.equipment.has_effect(kw):
                return True
        if hasattr(self, "inventory") and hasattr(self.inventory, "get_active_item"):
            active = self.inventory.get_active_item()
            if active and hasattr(active, "data"):
                kw_l = str(kw).lower()
                for eff in active.data.get("effects", []):
                    if kw_l in str(eff).lower():
                        return True
                special_str = str(active.data.get("special", "")).lower()
                if kw_l in special_str:
                    return True
        return False

    def take_damage(self, amount, knockback_vx=0.0, knockback_vy=-3.0, ignore_defense=False, is_magic=False):
        if self.i_frame_timer > 0 or self.is_dead:
            return False

        if ignore_defense:
            actual_damage = max(1, int(amount))
            meal_magic_res = self.get_meal_buff_val("magic_res")
            if meal_magic_res > 0:
                actual_damage = max(1, int(actual_damage * (1.0 - meal_magic_res)))
        else:
            # Evasion Step: 15% Chance to evade incoming strikes
            if self.has_effect("evasion step"):
                import random
                if random.random() < 0.15:
                    self.i_frame_timer = 0.3
                    self.sound_manager.play("jump")
                    return False

            # Titan's Resolve: Triples defense when below 30% HP
            effective_def = self.stats.total_def + int(self.get_meal_buff_val("def"))
            is_titan = self.has_effect("titan's resolve") and (self.health < self.max_health * 0.3)
            if is_titan:
                effective_def *= 3

            # Apply DEF mitigation formula capped at 85% (minimum piercing damage)
            min_pierce = 1 if is_titan else max(1, math.ceil(amount * 0.15))
            actual_damage = max(min_pierce, amount - effective_def)

            # Damage Mitigation: 15% or 25% Total Damage Mitigation
            if self.has_effect("15% total damage mitigation") or self.has_effect("+15% total damage mitigation") or self.has_effect("15% damage mitigation"):
                actual_damage = max(min_pierce, int(actual_damage * 0.85))
            elif self.has_effect("damage mitigation") or self.has_effect("-25%") or self.has_effect("25% total damage mitigation"):
                actual_damage = max(min_pierce, int(actual_damage * 0.75))

            # Meal Buff Damage Reduction
            meal_dmg_red = self.get_meal_buff_val("dmg_reduction")
            if meal_dmg_red > 0:
                actual_damage = max(min_pierce, int(actual_damage * (1.0 - meal_dmg_red)))

            # Magic Resistance (applied on magic damage or general elemental checks)
            meal_magic_res = self.get_meal_buff_val("magic_res")
            if meal_magic_res > 0 and (is_magic or getattr(self, "taking_magic_damage", False)):
                actual_damage = max(min_pierce, int(actual_damage * (1.0 - meal_magic_res)))

            # Radiant Shield: Absorbs 40 damage every 15s
            if self.has_effect("radiant shield") and self.radiant_shield_hp > 0:
                absorb = min(self.radiant_shield_hp, actual_damage)
                self.radiant_shield_hp -= absorb
                actual_damage -= int(absorb)
                if actual_damage <= 0:
                    self.i_frame_timer = 0.35
                    self.sound_manager.play("hit_block")
                    return False

        # Deep Roots: Immunity to knockback while grounded
        if self.has_effect("deep roots") and self.on_ground:
            knockback_vx = 0.0
            knockback_vy = 0.0
        else:
            meal_kb_res = self.get_meal_buff_val("knockback_res")
            if meal_kb_res > 0:
                knockback_vx *= (1.0 - meal_kb_res)
                knockback_vy *= (1.0 - meal_kb_res)

        # Eternal Bloom: Restores 50% HP upon reaching 1 HP (180s cooldown)
        if self.has_effect("eternal bloom") and (self.health - actual_damage <= 1) and self.eternal_bloom_cd <= 0:
            self.health = max(1, int(self.max_health * 0.50))
            self.eternal_bloom_cd = 180.0
            self.i_frame_timer = 1.5
            self.sound_manager.play("craft")
            return False

        # Starch Barrier: Blocks fatal damage once every 90s
        if (self.health - actual_damage <= 0) and self.has_effect("starch barrier") and self.starch_barrier_cd <= 0:
            self.health = max(20, int(self.max_health * 0.25))
            self.starch_barrier_cd = 90.0
            self.i_frame_timer = 2.0
            self.sound_manager.play("craft")
            return False

        self.last_damage_taken = actual_damage
        self.health -= actual_damage
        self.i_frame_timer = 0.8
        self.vx = knockback_vx
        self.vy = knockback_vy
        self.on_ground = False
        self.is_resting = False
        self.sound_manager.play("hurt")

        if self.health <= 0:
            self.is_dead = True
            self.respawn_timer = 3.0
            self.death_fade_alpha = 0
            self.death_teleported = False
            self.snap_camera_instant = False
            if getattr(self, "in_boss_fight", False):
                self.killed_by_boss = True

        return True

    def on_graze(self):
        """Called when a boss projectile grazes player perimeter without hitting core hitbox (Touhou style)."""
        self.graze_count += 1
        self.graze_timer = 0.22
        if hasattr(self, "stats"):
            if hasattr(self.stats, "mp") and hasattr(self.stats, "max_mp"):
                self.stats.mp = min(self.stats.max_mp, self.stats.mp + 1)
        if hasattr(self, "sound_manager") and self.sound_manager:
            self.sound_manager.play("pickup", volume=0.45)

    def update(self, dt, world, active_item_id=None):
        if self.graze_timer > 0:
            self.graze_timer -= dt

        if active_item_id is not None and active_item_id != getattr(self, "_current_held_id", None):
            self._current_held_id = active_item_id
            self.equipment.recalculate_stats(self.stats, active_item_id)

        # Timed Meal Buffs Update & Regeneration
        if hasattr(self, "meal_buffs") and self.meal_buffs:
            expired_cats = []
            for c_name, buff in self.meal_buffs.items():
                buff["duration"] -= dt
                if buff["duration"] <= 0:
                    expired_cats.append(c_name)
            for c_name in expired_cats:
                del self.meal_buffs[c_name]

            hp_reg = self.get_meal_buff_val("hp_regen")
            mp_reg = self.get_meal_buff_val("mp_regen")
            if hp_reg > 0 or mp_reg > 0:
                self.meal_regen_timer = getattr(self, "meal_regen_timer", 0.0) + dt
                if self.meal_regen_timer >= 1.0:
                    self.meal_regen_timer -= 1.0
                    if hp_reg > 0 and self.health < self.max_health:
                        self.health = min(self.max_health, self.health + int(round(hp_reg)))
                        if hasattr(self, "stats"):
                            self.stats.hp = self.health
                    if mp_reg > 0 and hasattr(self, "stats") and self.stats.mp < self.stats.max_mp:
                        self.stats.mp = min(self.stats.max_mp, self.stats.mp + int(round(mp_reg)))

        # Resting in Bed (+HP over time)
        if getattr(self, "is_resting", False):
            bed_pos = getattr(self, "resting_bed_pos", None)
            if bed_pos:
                bx = bed_pos[0] * world.scaled_tile + world.scaled_tile / 2
                by = bed_pos[1] * world.scaled_tile + world.scaled_tile / 2
                if math.hypot(self.center_x - bx, self.center_y - by) > world.scaled_tile * 4.0:
                    self.is_resting = False
            if abs(self.vx) > 0.5 or abs(self.vy) > 1.5:
                self.is_resting = False

            if getattr(self, "is_resting", False):
                self.bed_heal_timer = getattr(self, "bed_heal_timer", 0.0) + dt
                if self.bed_heal_timer >= 0.5:
                    self.bed_heal_timer = 0.0
                    if self.health < self.max_health:
                        self.health = min(self.max_health, self.health + 4)
                        if hasattr(self, "stats"):
                            self.stats.hp = self.health
                    ps = getattr(self, "particle_system", None)
                    if ps and random.random() < 0.35:
                        ps.spawn_sparks(self.center_x + random.randint(-4, 4), self.center_y - 8, (120, 255, 180), count=2)

        # Passive Gear Regeneration and Timers
        if self.has_effect("radiant shield"):
            if self.radiant_shield_hp < self.radiant_shield_max:
                self.radiant_shield_timer += dt
                if self.radiant_shield_timer >= 15.0:
                    self.radiant_shield_timer = 0.0
                    self.radiant_shield_hp = self.radiant_shield_max
        else:
            self.radiant_shield_hp = 0.0

        if self.starch_barrier_cd > 0:
            self.starch_barrier_cd -= dt
        if self.eternal_bloom_cd > 0:
            self.eternal_bloom_cd -= dt

        # Life Surge (+2 HP/s)
        if self.has_effect("life surge"):
            self.life_surge_timer += dt
            if self.life_surge_timer >= 0.5:
                self.life_surge_timer = 0.0
                if self.health < self.max_health:
                    self.health = min(self.max_health, self.health + 1)

        # Air Cushion Fall Resistance
        if self.has_effect("air cushion") and self.vy > 4.0:
            self.vy = min(self.vy, 4.0)

        if self.is_dead:
            self.pre_arena_pos = None
            self.respawn_timer -= dt

            # Cinematic pitch-black transition
            # Total timer = 3.0s:
            # 3.0s -> 1.5s: Fade to black (alpha 0 -> 255)
            # 1.5s: Screen is pitch black -> teleport player and snap camera instantly to spawn
            # 1.5s -> 0.0s: Fade in from black (alpha 255 -> 0)
            if self.respawn_timer > 1.5:
                progress = (3.0 - self.respawn_timer) / 1.5
                self.death_fade_alpha = int(min(255, max(0, progress * 255)))
            else:
                if not self.death_teleported:
                    self.death_teleported = True
                    self.health = self.max_health
                    if hasattr(self, "stats"):
                        self.stats.hp = self.health

                    if getattr(self, "killed_by_boss", False):
                        self.killed_by_boss = False
                        if hasattr(self, "inventory") and self.inventory:
                            self.inventory.clear_all_items()
                        if hasattr(self, "equipment") and self.equipment:
                            self.equipment.clear_all_items(stats=self.stats)
                        print("[Player] Defeated by Boss: All inventory items lost. Skills and level retained.")

                    sp = getattr(self, "spawn_point", None) or world.spawn_point
                    self.x, self.y = sp
                    self.vx, self.vy = 0.0, 0.0
                    self.snap_camera_instant = True

                fade_in_progress = max(0.0, self.respawn_timer / 1.5)
                self.death_fade_alpha = int(min(255, max(0, fade_in_progress * 255)))

            if self.respawn_timer <= 0:
                self.is_dead = False
                self.death_fade_alpha = 0
                self.death_teleported = False
                self.snap_camera_instant = False
            return

        # RPG Updates
        self.stats.update(dt)
        self.skills.update(dt)

        if self.i_frame_timer > 0:
            self.i_frame_timer -= dt
        if self.dash_timer > 0:
            self.dash_timer -= dt
        if self.ignore_platforms_timer > 0:
            self.ignore_platforms_timer -= 1

        # Attack Cooldown / Fire Rate timer
        if self.attack_cooldown > 0:
            self.attack_cooldown = max(0.0, self.attack_cooldown - dt)

        # Swing progression
        if self.is_swinging:
            self.swing_progress += dt / max(0.05, self.swing_duration)
            if self.swing_progress >= 1.0:
                self.is_swinging = False
                self.swing_progress = 0.0
                self.swing_hit_targets = set()

        # Update Projectiles
        ps = getattr(self, "particle_system", None)
        for fb in self.fireballs:
            fb.update(dt, world, ps)
        self.fireballs = [fb for fb in self.fireballs if fb.life > 0]
        if len(self.fireballs) > 30:
            self.fireballs = self.fireballs[-30:]

        # Water Contact & Swimming Physics (requires lower-body submersion)
        lower_body_rect = pygame.Rect(
            int(self.rect.x + 2),
            int(self.rect.centery),
            max(1, int(self.rect.width - 4)),
            max(1, int(self.rect.bottom - self.rect.centery)),
        )
        water_rects = world.get_water_rects_in_bounds(lower_body_rect) if hasattr(world, "get_water_rects_in_bounds") else []
        self.in_water = len(water_rects) > 0

        # Check if head is submerged for oxygen / breath meter
        self.is_submerged = world.is_water_world(self.center_x, self.y + 6) if hasattr(world, "is_water_world") else False

        if self.is_submerged:
            self.oxygen = max(0.0, self.oxygen - 7.5 * dt)
            self.submerged_duration += dt
            if self.oxygen <= 0:
                self.drown_timer += dt
                if self.drown_timer >= 1.0:
                    self.drown_timer = 0.0
                    heart_damage = max(1, self.stats.max_hp // 10)
                    self.take_damage(heart_damage, ignore_defense=True)
        else:
            self.oxygen = min(self.max_oxygen, self.oxygen + 40.0 * dt)
            self.drown_timer = 0.0
            self.submerged_duration = 0.0

        # Climbable Rope Rungs & Scaffolding Detection
        self.check_climbable(world)
        was_climbing_up = (self.on_rope_rungs or self.on_scaffolding) and self._climb_up_input

        # Gravity, Climbing & Fluid Drag
        if self.on_rope_rungs:
            if self._climb_up_input:
                self.vy = -3.8
                self.on_ground = False
            elif self._climb_down_input:
                self.vy = 3.2
                self.ignore_platforms_timer = max(self.ignore_platforms_timer, PLAYER_DROP_THROUGH_TIME)
                self.on_ground = False
            else:
                self.vy = 0.0
        elif self.on_scaffolding and (self._climb_up_input or self._climb_down_input):
            if self._climb_up_input:
                self.vy = -3.8
                self.on_ground = False
            elif self._climb_down_input:
                self.vy = max(self.vy, 3.2)
                self.ignore_platforms_timer = max(self.ignore_platforms_timer, PLAYER_DROP_THROUGH_TIME)
                self.on_ground = False
        elif (getattr(self, "rope_below", False) or getattr(self, "scaffold_below", False)) and self._climb_down_input:
            self.vy = max(self.vy, 3.2)
            self.ignore_platforms_timer = max(self.ignore_platforms_timer, PLAYER_DROP_THROUGH_TIME)
            self.on_ground = False
        elif self.in_water:
            self.vy = min(2.5, self.vy + GRAVITY * 0.25)
            self.vx *= 0.88
            self.vy *= 0.90
        elif self.dash_timer > 0:
            # Dampen gravity during active dash so omnidirectional dashes (especially upward / jump dashes) are snappy
            self.vy = min(TERMINAL_VELOCITY, self.vy + GRAVITY * 0.25)
        else:
            self.vy = min(TERMINAL_VELOCITY, self.vy + GRAVITY)

        # 1. Horizontal Movement & Solid Collisions (NO HORIZONTAL CLAMPING: INFINITE WORLD!)
        self.x += self.vx

        solids = world.get_solid_rects_in_bounds(self.rect)
        for tile_rect, is_platform in solids:
            if not is_platform and self.rect.colliderect(tile_rect):
                if self.vx > 0:
                    self.x = tile_rect.left - self.width
                elif self.vx < 0:
                    self.x = tile_rect.right
                self.vx = 0.0
                break

        # 2. Vertical Movement & Solid / Platform Collisions
        prev_bottom = self.rect.bottom
        self.y += self.vy
        self.on_ground = False

        solids = world.get_solid_rects_in_bounds(self.rect)
        for tile_rect, is_platform in solids:
            if self.rect.colliderect(tile_rect):
                if is_platform:
                    if (self.vy > 0 and 
                        self.ignore_platforms_timer <= 0 and 
                        prev_bottom <= tile_rect.top + 8):
                        self.y = tile_rect.top - self.height
                        self.vy = 0.0
                        self.on_ground = True
                else:
                    if self.vy > 0:
                        self.y = tile_rect.top - self.height
                        self.vy = 0.0
                        self.on_ground = True
                    elif self.vy < 0:
                        self.y = tile_rect.bottom
                        self.vy = 0.0
                    break

        self.check_climbable(world)
        if was_climbing_up and not self.on_climbable and self.vy < 0:
            prev_top_ty = int((prev_bottom - 1) // SCALED_TILE)
            platform_top_y = float(prev_top_ty * SCALED_TILE)
            if prev_bottom > platform_top_y >= self.rect.bottom:
                self.y = platform_top_y - self.height
                self.vy = 0.0
                self.on_ground = True
                self.check_climbable(world)

        if self.on_rope_rungs and not self._climb_up_input and not self._climb_down_input and self.vy == 0.0:
            self.on_ground = True

        self._climb_up_input = False
        self._climb_down_input = False

        # 3. 12 FPS Smooth Animation Timing (0.0833s per frame)
        FRAME_DURATION = 1.0 / 12.0
        self.anim_timer += dt
        if self.anim_timer >= FRAME_DURATION:
            self.anim_timer = 0.0
            if not self.on_ground:
                pass
            elif abs(self.vx) > 0.2:
                self.walk_frame_idx = (self.walk_frame_idx + 1) % len(self.walk_sprites)
            else:
                self.idle_frame_idx = (self.idle_frame_idx + 1) % len(self.idle_sprites)

    def render(self, target_surf, camera, held_item_icon=None, held_item=None):
        if self.is_dead:
            return

        # Render player fireballs
        for fb in self.fireballs:
            fb.render(target_surf, camera)

        if self.i_frame_timer > 0 and int(self.i_frame_timer * 18) % 2 == 0:
            return

        sx, sy = camera.world_to_screen(self.x, self.y)
        # Vertical draw offset ensures player's body and boots align with collider bottom,
        # while decorative sprout leaf on top of head extends above collider without collision
        draw_sy = sy - self.sprout_offset_y

        # Render radiant pulsing set aura (Ancient, Titan, Magma, etc.)
        aura = None
        if hasattr(self, "equipment") and self.equipment:
            aura = self.equipment.get_active_aura()
        if aura:
            self._render_active_aura(target_surf, sx + self.width // 2, draw_sy + self.sprite_height // 2, aura)

        # Render Touhou-style graze aura ring upon precision dodge
        if self.graze_timer > 0:
            graze_pad = 6
            gw = self.width + graze_pad * 2
            gh = self.height + graze_pad * 2
            graze_surf = pygame.Surface((gw, gh), pygame.SRCALPHA)
            alpha = max(40, min(180, int((self.graze_timer / 0.22) * 180)))
            pygame.draw.ellipse(graze_surf, (140, 230, 255, alpha), (1, 1, gw - 2, gh - 2), 2)
            target_surf.blit(graze_surf, (sx - graze_pad, draw_sy - graze_pad))

        # Select Spud Potato frame (12 FPS Animation state)
        if not self.on_ground:
            if self.vy < -0.5:
                base_sprite = self.jump_sprite
            else:
                base_sprite = self.fall_sprite
        elif abs(self.vx) > 0.2:
            base_sprite = self.walk_sprites[self.walk_frame_idx]
        else:
            base_sprite = self.idle_sprites[self.idle_frame_idx]

        if not self.facing_right:
            base_sprite = pygame.transform.flip(base_sprite, True, False)

        target_surf.blit(base_sprite, (sx, draw_sy))

        # Render Spud's Swinging Potato Arm and Held Tool with fixed anchor pivot
        self._render_arm_and_tool(target_surf, camera, sx, draw_sy, held_item_icon, held_item)

    def _render_arm_and_tool(self, target_surf, camera, player_sx, player_sy, held_item_icon, held_item=None):
        if not held_item_icon:
            return

        # Spud potato dimensions: 28 px wide x 32 px high (collider), 28x36 visual sprite (4px sprout offset)
        # Anchor held item cleanly at front side of potato body:
        hand_x = player_sx + (22 if self.facing_right else 6)
        hand_y = player_sy + 20
        
        # Determine if held item is a weapon/tool vs block/food/item
        held_id = held_item.item_id if held_item else ""
        is_weapon_or_tool = False
        if held_item:
            cat = held_item.data.get("cat") if hasattr(held_item, "data") else None
            if cat in ("weapon", "tool"):
                is_weapon_or_tool = True
            elif any(held_id.endswith(sfx) for sfx in ("_sword", "_pickaxe", "_axe", "_bow", "_staff", "_spear", "_scythe")):
                is_weapon_or_tool = True
            elif held_id in ("astral_wrath", "starfury", "celestial_wrath", "bone_scythe", "magma_greatsword", "shadow_cleaver", "frost_blade", "sandstorm_spear", "golden_fry", "starch_blade"):
                is_weapon_or_tool = True

        # Determine swing angle arc
        swing_angle = math.sin(self.swing_progress * math.pi) * 1.4 if self.is_swinging else 0.0

        if is_weapon_or_tool:
            # Constrain aim to forward-facing cone so weapon never clips backward across Spud's face
            if self.facing_right:
                aim_cone = max(-1.15, min(1.15, self.aim_angle))
                eff_angle = max(-1.45, min(1.45, aim_cone + swing_angle - 0.2))
            else:
                rel_aim = math.atan2(math.sin(self.aim_angle), -math.cos(self.aim_angle))
                aim_cone = max(-1.15, min(1.15, rel_aim))
                eff_rel = max(-1.45, min(1.45, aim_cone - swing_angle + 0.2))
                eff_angle = math.atan2(math.sin(eff_rel), -math.cos(eff_rel))

            item_surf = held_item_icon
            w, h = item_surf.get_size()
            cx, cy = w / 2.0, h / 2.0

            if self.facing_right:
                # Handle anchored at (4.0, 20.0), icon blade points outward at -45 deg
                rot_deg = -45.0 - math.degrees(eff_angle)
                rot_item = pygame.transform.rotate(item_surf, rot_deg)
                
                vx, vy = 4.0 - cx, 20.0 - cy
                rad = math.radians(-rot_deg)
                rot_vx = vx * math.cos(rad) - vy * math.sin(rad)
                rot_vy = vx * math.sin(rad) + vy * math.cos(rad)
                
                rot_cx = hand_x - rot_vx
                rot_cy = hand_y - rot_vy
                target_surf.blit(rot_item, (rot_cx - rot_item.get_width() / 2.0, rot_cy - rot_item.get_height() / 2.0))
            else:
                # Flipped icon has handle at (w - 1 - 4.0, 20.0), blade points outward at -135 deg
                flipped_item = pygame.transform.flip(item_surf, True, False)
                rot_deg = -135.0 - math.degrees(eff_angle)
                rot_item = pygame.transform.rotate(flipped_item, rot_deg)

                vx, vy = (w - 1.0 - 4.0) - cx, 20.0 - cy
                rad = math.radians(-rot_deg)
                rot_vx = vx * math.cos(rad) - vy * math.sin(rad)
                rot_vy = vx * math.sin(rad) + vy * math.cos(rad)

                rot_cx = hand_x - rot_vx
                rot_cy = hand_y - rot_vy
                target_surf.blit(rot_item, (rot_cx - rot_item.get_width() / 2.0, rot_cy - rot_item.get_height() / 2.0))

            # Special radiant/sparkle particle effects for highest rarity items (Legendary & Mythic)
            rarity = ""
            if held_item and hasattr(held_item, "data"):
                rarity = held_item.data.get("rarity", "")
            if not rarity and held_item:
                from src.ui.inventory import ITEM_REGISTRY
                rarity = ITEM_REGISTRY.get(held_item.item_id, {}).get("rarity", "")

            if rarity in ("ancient", "legendary", "mythic"):
                tip_dist = 22.0
                tip_x = hand_x + math.cos(eff_angle) * tip_dist
                tip_y = hand_y + math.sin(eff_angle) * tip_dist
                t_ticks = pygame.time.get_ticks()
                for i in range(3):
                    spark_ang = (t_ticks * 0.006 + i * 2.09) % (math.pi * 2)
                    spark_r = 5 + math.sin(t_ticks * 0.01 + i) * 4
                    sp_x = int(tip_x + math.cos(spark_ang) * spark_r)
                    sp_y = int(tip_y + math.sin(spark_ang) * spark_r)
                    if rarity == "ancient":
                        sp_color = (244, 67, 54)
                    elif rarity == "legendary":
                        sp_color = (255, 215, 0)
                    else:
                        sp_color = (255, 152, 0)
                    pygame.draw.circle(target_surf, sp_color, (sp_x, sp_y), 2)
                    pygame.draw.line(target_surf, (255, 255, 255), (sp_x - 3, sp_y), (sp_x + 3, sp_y))
                    pygame.draw.line(target_surf, (255, 255, 255), (sp_x, sp_y - 3), (sp_x, sp_y + 3))

                if rarity == "ancient" and self.is_swinging:
                    # Grand glowing crescent slash arc for Ancient Weapons
                    arc_r = 30
                    arc_rect = pygame.Rect(hand_x - arc_r, hand_y - arc_r, arc_r * 2, arc_r * 2)
                    ang_mid = -math.degrees(eff_angle)
                    ang_rad1 = math.radians(ang_mid - 40)
                    ang_rad2 = math.radians(ang_mid + 40)
                    start_a = min(ang_rad1, ang_rad2)
                    end_a = max(ang_rad1, ang_rad2)
                    pygame.draw.arc(target_surf, (255, 215, 60), arc_rect, start_a, end_a, 4)
                    pygame.draw.arc(target_surf, (245, 60, 75), arc_rect, start_a + 0.05, end_a - 0.05, 2)
                    pygame.draw.arc(target_surf, (255, 255, 255), arc_rect, start_a + 0.1, end_a - 0.1, 1)

        else:
            # Non-weapon held items (blocks, furniture, food, potions, skill books) are held at Spud's side without covering the face
            if held_item_icon:
                item_surf = held_item_icon
                if not self.facing_right:
                    item_surf = pygame.transform.flip(item_surf, True, False)
                item_x = hand_x - (4 if self.facing_right else 18)
                item_y = hand_y - 12
                if self.is_swinging:
                    bob_x = math.sin(self.swing_progress * math.pi) * (5 if self.facing_right else -5)
                    bob_y = math.sin(self.swing_progress * math.pi) * 3
                    item_x += bob_x
                    item_y += bob_y
                target_surf.blit(item_surf, (item_x, item_y))

    def _render_active_aura(self, target_surf, cx, cy, aura_type):
        """Renders radiant pulsing aura mandalas and orbiting starlight motes around Spud."""
        t = pygame.time.get_ticks() * 0.004
        if aura_type == "ancient":
            # Radiant pulsating ancient golden-crimson celestial aura
            pulse = math.sin(t * 3.0) * 4.0
            r = int(24 + pulse)
            # Outer golden & crimson rings
            pygame.draw.circle(target_surf, (255, 215, 60), (int(cx), int(cy)), r, 2)
            pygame.draw.circle(target_surf, (245, 60, 75), (int(cx), int(cy)), max(2, r - 3), 1)
            # Inner white radiance
            pygame.draw.circle(target_surf, (255, 255, 220), (int(cx), int(cy)), max(1, r - 7), 1)
            # Orbiting celestial starlight motes
            for i in range(6):
                ang = t * 2.0 + i * (math.pi / 3.0)
                ox = cx + math.cos(ang) * (r + 4)
                oy = cy + math.sin(ang) * (r * 0.7 + 3)
                pygame.draw.circle(target_surf, (255, 245, 180), (int(ox), int(oy)), 2)
                pygame.draw.circle(target_surf, (255, 255, 255), (int(ox), int(oy)), 1)
        elif aura_type == "titan":
            pulse = math.sin(t * 2.5) * 3.0
            r = int(22 + pulse)
            pygame.draw.circle(target_surf, (100, 220, 255), (int(cx), int(cy)), r, 2)
            pygame.draw.circle(target_surf, (255, 215, 0), (int(cx), int(cy)), max(2, r - 3), 1)
        elif aura_type == "magma":
            pulse = math.sin(t * 4.0) * 3.0
            r = int(20 + pulse)
            pygame.draw.circle(target_surf, (255, 100, 20), (int(cx), int(cy)), r, 2)
            pygame.draw.circle(target_surf, (255, 220, 50), (int(cx), int(cy)), max(2, r - 4), 1)
        elif aura_type == "cryo":
            pulse = math.sin(t * 2.0) * 2.0
            r = int(20 + pulse)
            pygame.draw.circle(target_surf, (140, 240, 255), (int(cx), int(cy)), r, 2)
        elif aura_type == "shadow":
            pulse = math.sin(t * 3.5) * 3.0
            r = int(22 + pulse)
            pygame.draw.circle(target_surf, (180, 50, 240), (int(cx), int(cy)), r, 2)
        elif aura_type == "spud":
            pulse = math.sin(t * 2.0) * 2.0
            r = int(18 + pulse)
            pygame.draw.circle(target_surf, (140, 220, 60), (int(cx), int(cy)), r, 2)
        elif aura_type == "cactus":
            pulse = math.sin(t * 3.0) * 2.0
            r = int(18 + pulse)
            pygame.draw.circle(target_surf, (80, 200, 50), (int(cx), int(cy)), r, 2)

    def get_rod_tip_pos(self):
        """Calculates the dynamic world position of the held rod tip based on player posture, position, and aim."""
        hand_x = self.x + (22 if self.facing_right else 6)
        hand_y = self.y - getattr(self, "sprout_offset_y", 0) + 20
        swing_angle = math.sin(self.swing_progress * math.pi) * 1.4 if self.is_swinging else 0.0
        if self.facing_right:
            aim_cone = max(-1.15, min(1.15, self.aim_angle))
            eff_angle = max(-1.45, min(1.45, aim_cone + swing_angle - 0.2))
        else:
            rel_aim = math.atan2(math.sin(self.aim_angle), -math.cos(self.aim_angle))
            aim_cone = max(-1.15, min(1.15, rel_aim))
            eff_rel = max(-1.45, min(1.45, aim_cone - swing_angle + 0.2))
            eff_angle = math.atan2(math.sin(eff_rel), -math.cos(eff_rel))
        tip_x = hand_x + math.cos(eff_angle) * 23.0
        tip_y = hand_y + math.sin(eff_angle) * 23.0
        return tip_x, tip_y

