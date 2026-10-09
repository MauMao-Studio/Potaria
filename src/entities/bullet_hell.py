"""
Potaria - Bullet-Hell Shooter Engine & Projectile Systems
High-Performance Bullet-Hell Patterns, Touhou/Gungeon Grazing & Fair Core Hitboxes
Developer: Kurados
Engine: Pure Python 3.13 + pygame-ce 2.5.8+ (100% Offline Standalone)
"""

import math
import random
import pygame
from src.constants import SCREEN_WIDTH, SCREEN_HEIGHT

# ==============================================================================
# HIGH-PERFORMANCE SURFACE CACHE (ZERO ALLOCATION DURING HEAVY BARRAGES)
# ==============================================================================
_BULLET_SURF_CACHE = {}

def get_bullet_surface(shape, color, core_color=(255, 255, 255), radius=10, angle_deg=0):
    """
    Returns an optimized pre-rendered bullet surface from cache.
    Rotational shapes are quantized to 12-degree increments (30 steps max) to keep cache bounded.
    """
    # Round / quantize parameters for caching
    q_angle = int((angle_deg % 360) // 12) * 12
    cache_key = (shape, tuple(color[:3]), tuple(core_color[:3]), int(radius), q_angle)
    if cache_key in _BULLET_SURF_CACHE:
        return _BULLET_SURF_CACHE[cache_key]

    max_extent = int(math.ceil(radius * 1.85 + 6))
    size = max_extent * 2
    surf = pygame.Surface((size, size), pygame.SRCALPHA)
    cx, cy = max_extent, max_extent
    r = int(radius)
    c_rgb = color[:3]
    core_rgb = core_color[:3]

    if shape == "needle" or shape == "shard":
        # Directional crystalline needle oriented along angle
        rad = math.radians(q_angle)
        cos_a = math.cos(rad)
        sin_a = math.sin(rad)
        perp_cos = -sin_a
        perp_sin = cos_a

        l_head = r * 1.5
        l_tail = r * 1.2
        w_half = max(2, r * 0.45)

        tip_x = cx + cos_a * l_head
        tip_y = cy + sin_a * l_head
        tail_x = cx - cos_a * l_tail
        tail_y = cy - sin_a * l_tail
        left_x = cx + perp_cos * w_half
        left_y = cy + perp_sin * w_half
        right_x = cx - perp_cos * w_half
        right_y = cy - perp_sin * w_half

        poly = [(tip_x, tip_y), (left_x, left_y), (tail_x, tail_y), (right_x, right_y)]
        pygame.draw.polygon(surf, c_rgb, poly)
        
        # Inner core spine
        inner_l = r * 0.9
        c_tip = (cx + cos_a * inner_l, cy + sin_a * inner_l)
        c_tail = (cx - cos_a * (inner_l * 0.7), cy - sin_a * (inner_l * 0.7))
        pygame.draw.line(surf, core_rgb, c_tip, c_tail, max(1, int(w_half * 0.6)))

    elif shape == "star" or shape == "snowflake":
        # Symmetrical 8-point crystalline star
        pts = []
        for i in range(16):
            a = math.radians(q_angle + i * (360 / 16))
            cur_r = r if (i % 2 == 0) else max(2, r * 0.42)
            pts.append((cx + math.cos(a) * cur_r, cy + math.sin(a) * cur_r))
        pygame.draw.polygon(surf, c_rgb, pts)
        # Inner bright core
        core_pts = []
        for i in range(16):
            a = math.radians(q_angle + i * (360 / 16))
            cur_r = (r * 0.45) if (i % 2 == 0) else max(1, r * 0.20)
            core_pts.append((cx + math.cos(a) * cur_r, cy + math.sin(a) * cur_r))
        pygame.draw.polygon(surf, core_rgb, core_pts)

    elif shape == "scythe":
        # Sweeping curved scythe arc
        rad = math.radians(q_angle)
        cos_a = math.cos(rad)
        sin_a = math.sin(rad)
        perp_cos = -sin_a
        perp_sin = cos_a

        l_head = r * 1.6
        w = max(3, r * 0.6)
        p1 = (cx + cos_a * l_head, cy + sin_a * l_head)
        p2 = (cx + perp_cos * w, cy + perp_sin * w)
        p3 = (cx - cos_a * (l_head * 0.6), cy - sin_a * (l_head * 0.6))
        p4 = (cx - perp_cos * (w * 0.4), cy - perp_sin * (w * 0.4))
        pygame.draw.polygon(surf, c_rgb, [p1, p2, p3, p4])
        pygame.draw.polygon(surf, core_rgb, [p1, (cx + perp_cos * (w * 0.5), cy + perp_sin * (w * 0.5)), p3])

    elif shape == "wisp":
        # Teardrop spirit flame wisp
        rad = math.radians(q_angle)
        cos_a = math.cos(rad)
        sin_a = math.sin(rad)
        pygame.draw.circle(surf, c_rgb, (cx, cy), r)
        tail_tip = (cx - cos_a * (r * 1.6), cy - sin_a * (r * 1.6))
        pygame.draw.polygon(surf, c_rgb, [(cx - sin_a * (r * 0.8), cy + cos_a * (r * 0.8)),
                                          tail_tip,
                                          (cx + sin_a * (r * 0.8), cy - cos_a * (r * 0.8))])
        pygame.draw.circle(surf, core_rgb, (cx, cy), max(2, int(r * 0.45)))

    elif shape == "singularity":
        # Swirling dark vortex with intense glowing accretion ring
        pygame.draw.circle(surf, c_rgb, (cx, cy), r, 2)
        pygame.draw.circle(surf, (15, 8, 24), (cx, cy), max(3, r - 3))
        pygame.draw.circle(surf, core_rgb, (cx, cy), max(2, int(r * 0.3)))

    elif shape == "meteor":
        # Molten textured meteor
        pygame.draw.circle(surf, c_rgb, (cx, cy), r)
        pygame.draw.circle(surf, (255, 140, 20), (cx - 1, cy - 1), max(2, int(r * 0.65)))
        pygame.draw.circle(surf, core_rgb, (cx - 2, cy - 2), max(1, int(r * 0.35)))

    else:
        # Default "orb" / circle: outer soft glow, vibrant body, pure bright core
        glow_color = (min(255, c_rgb[0] + 30), min(255, c_rgb[1] + 30), min(255, c_rgb[2] + 30))
        pygame.draw.circle(surf, glow_color, (cx, cy), r)
        pygame.draw.circle(surf, c_rgb, (cx, cy), max(1, r - 1))
        # High-clarity white/pastel core (Touhou / Gungeon readability)
        core_r = max(2, int(r * 0.48))
        pygame.draw.circle(surf, core_rgb, (cx, cy), core_r)

    _BULLET_SURF_CACHE[cache_key] = surf
    return surf


# ==============================================================================
# BOSS PROJECTILE WITH FAIR CORE HITBOX & GRAZING
# ==============================================================================
_NEXT_PROJ_ID = 1

def _get_next_proj_id():
    global _NEXT_PROJ_ID
    pid = _NEXT_PROJ_ID
    _NEXT_PROJ_ID += 1
    return pid

class BossProjectile:
    """
    Universal bullet-hell projectile featuring:
    - Fair, player-friendly Core Hitbox (~55% visual radius for precision dodging)
    - Perimeter Graze Hitbox (rewards threading narrow gaps with MP/stamina & visual feedback)
    - Rich Kinematics: sine waves, spiral curvature, acceleration, delayed blooms, homing
    - Cached 60+ FPS sprite blitting with off-screen frustum culling
    - Clean multiplayer serialization & client reconciliation
    """
    def __init__(
        self, x, y, vx, vy,
        sprite=None,
        damage=18,
        radius=10,
        life=4.0,
        p_type="linear",
        gravity=0.0,
        # Bullet-Hell & Dodge Enhancement Parameters
        core_radius=None,
        color=None,
        core_color=(255, 255, 255),
        glow_color=None,
        shape="orb",
        wave_amplitude=0.0,
        wave_frequency=0.0,
        curve_rate=0.0,
        accel=1.0,
        delay_move=0.0,
        p_id=None
    ):
        self.p_id = p_id if p_id is not None else _get_next_proj_id()
        self.x = float(x)
        self.y = float(y)
        self.vx = float(vx)
        self.vy = float(vy)
        self.sprite = sprite
        self.damage = int(damage)
        self.radius = float(radius)
        self.life = float(life)
        self.max_life = float(life)
        self.age = 0.0
        self.p_type = p_type  # "linear", "homing", "gravity", "singularity", "meteor", "wave", "spiral"
        self.gravity = float(gravity)

        # Fair collision core (classic Touhou / Gungeon dodge feel)
        if core_radius is not None:
            self.core_radius = float(core_radius)
        elif self.p_type == "singularity":
            self.core_radius = max(6.0, self.radius * 0.70)
        else:
            self.core_radius = max(2.5, self.radius * 0.52)

        # Grazing detection boundary
        self.graze_radius = self.radius + 12.0
        self.grazed = False

        # Visual styling
        self.shape = shape
        self.color = tuple(color[:3]) if color is not None else (255, 180, 50)
        self.core_color = tuple(core_color[:3])
        self.glow_color = tuple(glow_color[:3]) if glow_color else None

        # Dynamic motion parameters
        self.wave_amplitude = float(wave_amplitude)
        self.wave_frequency = float(wave_frequency)
        self.curve_rate = float(curve_rate)  # radians per second
        self.accel = float(accel)
        self.delay_move = float(delay_move)

        # Hitboxes
        self.frect = pygame.FRect(self.x - self.core_radius, self.y - self.core_radius, self.core_radius * 2, self.core_radius * 2)
        self.visual_frect = pygame.FRect(self.x - self.radius, self.y - self.radius, self.radius * 2, self.radius * 2)
        self.graze_frect = pygame.FRect(self.x - self.graze_radius, self.y - self.graze_radius, self.graze_radius * 2, self.graze_radius * 2)

    @property
    def rect(self):
        """Authoritative lethal core hitbox."""
        self.frect.x = self.x - self.core_radius
        self.frect.y = self.y - self.core_radius
        return self.frect

    @property
    def visual_rect(self):
        """Full visual bounding rect."""
        self.visual_frect.x = self.x - self.radius
        self.visual_frect.y = self.y - self.radius
        return self.visual_frect

    @property
    def graze_rect(self):
        """Perimeter graze bounding rect for precision dodging rewards."""
        self.graze_frect.x = self.x - self.graze_radius
        self.graze_frect.y = self.y - self.graze_radius
        return self.graze_frect

    def update(self, dt, player=None):
        self.life -= dt
        self.age += dt

        # Delayed launch (flower bloom / charge starbursts)
        if self.delay_move > 0 and self.age < self.delay_move:
            return

        # Acceleration
        if self.accel != 1.0:
            rate = math.pow(self.accel, dt * 60.0)
            self.vx *= rate
            self.vy *= rate

        # Angular trajectory curvature
        if self.curve_rate != 0.0:
            speed = math.hypot(self.vx, self.vy)
            if speed > 0.001:
                angle = math.atan2(self.vy, self.vx) + self.curve_rate * dt
                self.vx = math.cos(angle) * speed
                self.vy = math.sin(angle) * speed

        # Motion behavior branches
        if self.p_type == "gravity":
            self.vy += self.gravity * dt
            self.x += self.vx
            self.y += self.vy

        elif self.p_type == "homing" and player and not getattr(player, "is_dead", False):
            # Smooth progressive tracking
            ang = math.atan2(player.center_y - self.y, player.center_x - self.x)
            cur_speed = math.hypot(self.vx, self.vy)
            if cur_speed > 0.001:
                self.vx = self.vx * 0.94 + math.cos(ang) * cur_speed * 0.06
                self.vy = self.vy * 0.94 + math.sin(ang) * cur_speed * 0.06
            self.x += self.vx
            self.y += self.vy

        elif self.p_type == "singularity" and player and not getattr(player, "is_dead", False):
            # Gravitational vortex pull on player
            dist = math.hypot(player.center_x - self.x, player.center_y - self.y)
            if 10.0 < dist < 340.0:
                pull = (1.0 - (dist / 340.0)) * 5.0
                pull_ang = math.atan2(self.y - player.center_y, self.x - player.center_x)
                player.vx += math.cos(pull_ang) * pull * 0.5
                player.vy += math.sin(pull_ang) * pull * 0.5
            self.x += self.vx
            self.y += self.vy

        else:
            # Base velocity step
            self.x += self.vx
            self.y += self.vy

            # Perpendicular sinusoidal wave undulation (snake / serpentine waves)
            if self.wave_amplitude != 0.0 and self.wave_frequency != 0.0:
                cur_speed = math.hypot(self.vx, self.vy)
                if cur_speed > 0.001:
                    base_ang = math.atan2(self.vy, self.vx)
                    perp_ang = base_ang + math.pi / 2.0
                    osc = math.cos(self.age * self.wave_frequency) * self.wave_amplitude
                    self.x += math.cos(perp_ang) * osc * (dt * 60.0)
                    self.y += math.sin(perp_ang) * osc * (dt * 60.0)

        # Player grazing detection
        if player and not getattr(player, "is_dead", False) and not self.grazed:
            if self.graze_rect.colliderect(player.rect) and not self.rect.colliderect(player.rect):
                self.grazed = True
                if hasattr(player, "on_graze"):
                    player.on_graze()

    def render(self, target_surf, camera):
        if self.life <= 0:
            return

        # World to screen coordinates
        sx, sy = camera.world_to_screen(self.x, self.y)

        # Frustum culling (off-screen check for extreme 60+ FPS performance)
        pad = int(self.radius + 32)
        if sx < -pad or sx > SCREEN_WIDTH + pad or sy < -pad or sy > SCREEN_HEIGHT + pad:
            return

        # If custom external sprite surface provided, blit it
        if self.sprite is not None and self.shape == "sprite":
            sw = self.sprite.get_width()
            sh = self.sprite.get_height()
            target_surf.blit(self.sprite, (int(sx - sw // 2), int(sy - sh // 2)))
            return

        # Otherwise use ultra-crisp cached vector bullet surface
        angle_deg = math.degrees(math.atan2(self.vy, self.vx))
        surf = get_bullet_surface(
            shape=self.shape,
            color=self.color,
            core_color=self.core_color,
            radius=int(self.radius),
            angle_deg=angle_deg
        )
        hw = surf.get_width() // 2
        hh = surf.get_height() // 2
        target_surf.blit(surf, (int(sx - hw), int(sy - hh)))

    def to_sync_dict(self):
        """Serializes bullet state for multiplayer network broadcast."""
        return {
            "id": self.p_id,
            "x": round(self.x, 1),
            "y": round(self.y, 1),
            "vx": round(self.vx, 2),
            "vy": round(self.vy, 2),
            "t": self.p_type,
            "s": self.shape,
            "c": list(self.color),
            "cc": list(self.core_color),
            "r": round(self.radius, 1),
            "cr": round(self.core_radius, 1),
            "d": self.damage,
            "l": round(self.life, 2),
            "g": round(self.gravity, 2),
            "w_a": round(self.wave_amplitude, 1),
            "w_f": round(self.wave_frequency, 1),
            "curv": round(self.curve_rate, 2),
            "acc": round(self.accel, 3),
            "del": round(self.delay_move, 2),
            "age": round(self.age, 2),
        }

    @classmethod
    def from_sync_dict(cls, d, sprite=None):
        """Reconstructs projectile from authoritative host sync packet."""
        proj = cls(
            x=d.get("x", 0.0),
            y=d.get("y", 0.0),
            vx=d.get("vx", 0.0),
            vy=d.get("vy", 0.0),
            sprite=sprite,
            damage=d.get("d", 18),
            radius=d.get("r", 10.0),
            life=d.get("l", 3.0),
            p_type=d.get("t", "linear"),
            gravity=d.get("g", 0.0),
            core_radius=d.get("cr"),
            color=tuple(d.get("c", (255, 180, 50))),
            core_color=tuple(d.get("cc", (255, 255, 255))),
            shape=d.get("s", "orb"),
            wave_amplitude=d.get("w_a", 0.0),
            wave_frequency=d.get("w_f", 0.0),
            curve_rate=d.get("curv", 0.0),
            accel=d.get("acc", 1.0),
            delay_move=d.get("del", 0.0),
            p_id=d.get("id")
        )
        proj.age = float(d.get("age", 0.0))
        return proj


# ==============================================================================
# BULLET-HELL PATTERN GENERATOR SUITE
# ==============================================================================
class BulletHellPatterns:
    """Mathematical generator for rich geometric and dynamic bullet patterns."""

    @staticmethod
    def spawn_concentric_ring(
        cx, cy, count, speed, color, core_color=(255, 255, 255),
        radius=10, damage=18, base_angle=0.0, gaps=None, shape="orb"
    ):
        """
        Expanding concentric ring with designated dodge gaps.
        gaps: list of (start_angle_rad, end_angle_rad) tuples defining safe passage lanes.
        """
        if count <= 0:
            return []
        projs = []
        angle_step = (2.0 * math.pi) / count
        gaps = gaps or []

        for i in range(count):
            ang = base_angle + i * angle_step
            # Normalize angle to [0, 2*pi)
            norm_ang = ang % (2.0 * math.pi)

            # Check if angle falls within any dodge gap
            in_gap = False
            for g_start, g_end in gaps:
                s = g_start % (2.0 * math.pi)
                e = g_end % (2.0 * math.pi)
                if s <= e:
                    if s <= norm_ang <= e:
                        in_gap = True
                        break
                else:
                    if norm_ang >= s or norm_ang <= e:
                        in_gap = True
                        break

            if in_gap:
                continue

            vx = math.cos(ang) * speed
            vy = math.sin(ang) * speed
            projs.append(BossProjectile(
                cx, cy, vx, vy,
                damage=damage, radius=radius,
                color=color, core_color=core_color,
                shape=shape, p_type="linear"
            ))
        return projs

    @staticmethod
    def spawn_spiral_step(
        cx, cy, arms, current_angle, speed, color, core_color=(255, 255, 255),
        radius=10, damage=18, shape="orb", curve_rate=0.0, accel=1.0
    ):
        """Single time-step of a rotating multi-arm spiral barrage."""
        if arms <= 0:
            return []
        projs = []
        arm_step = (2.0 * math.pi) / arms
        for a in range(arms):
            ang = current_angle + a * arm_step
            vx = math.cos(ang) * speed
            vy = math.sin(ang) * speed
            projs.append(BossProjectile(
                cx, cy, vx, vy,
                damage=damage, radius=radius,
                color=color, core_color=core_color,
                shape=shape, curve_rate=curve_rate,
                accel=accel, p_type="linear"
            ))
        return projs

    @staticmethod
    def spawn_aimed_spread(
        cx, cy, target_x, target_y, count, spread_angle_deg, speed,
        color, core_color=(255, 255, 255), radius=10, damage=18, shape="shard"
    ):
        """Aimed fan of projectiles centered on the player's vector."""
        if count <= 0:
            return []
        projs = []
        base_angle = math.atan2(target_y - cy, target_x - cx)
        spread_rad = math.radians(spread_angle_deg)
        if count <= 1:
            step = 0.0
            start = base_angle
        else:
            step = spread_rad / (count - 1)
            start = base_angle - spread_rad / 2.0

        for i in range(count):
            ang = start + i * step
            vx = math.cos(ang) * speed
            vy = math.sin(ang) * speed
            projs.append(BossProjectile(
                cx, cy, vx, vy,
                damage=damage, radius=radius,
                color=color, core_color=core_color,
                shape=shape, p_type="linear"
            ))
        return projs

    @staticmethod
    def spawn_snowflake_burst(
        cx, cy, points=16, speed=5.0, color=(100, 220, 255),
        core_color=(255, 255, 255), radius=11, damage=18, offset_angle=0.0
    ):
        """Symmetrical 16-point geometric crystalline snowflake burst."""
        if points <= 0:
            return []
        projs = []
        step = (2.0 * math.pi) / points
        for i in range(points):
            ang = offset_angle + i * step
            vx = math.cos(ang) * speed
            vy = math.sin(ang) * speed
            projs.append(BossProjectile(
                cx, cy, vx, vy,
                damage=damage, radius=radius,
                color=color, core_color=core_color,
                shape="snowflake", p_type="linear"
            ))
        return projs

    @staticmethod
    def spawn_undulating_stream(
        cx, cy, angle, speed, count, wave_amp=4.0, wave_freq=8.0,
        color=(140, 235, 255), core_color=(255, 255, 255), radius=9, damage=16
    ):
        """High-velocity serpentine sine-wave stream."""
        if count <= 0:
            return []
        projs = []
        for i in range(count):
            delay = i * 0.06
            vx = math.cos(angle) * speed
            vy = math.sin(angle) * speed
            projs.append(BossProjectile(
                cx, cy, vx, vy,
                damage=damage, radius=radius,
                color=color, core_color=core_color,
                shape="needle", p_type="wave",
                wave_amplitude=wave_amp,
                wave_frequency=wave_freq,
                delay_move=delay
            ))
        return projs

    @staticmethod
    def spawn_criss_cross_curtains(
        target_x, target_y, count=12, speed=4.5,
        color=(210, 210, 225), core_color=(255, 255, 255), damage=18
    ):
        """Perpendicular criss-crossing bullet grids forming moving dodge corridors."""
        if count <= 0:
            return []
        projs = []
        c = max(2, count)
        # Horizontal streams from left and right
        for i in range(c // 2):
            y_offset = (i - (c // 4)) * 70.0
            py = target_y + y_offset
            # Left to right
            projs.append(BossProjectile(
                target_x - 420.0, py, speed, 0.0,
                damage=damage, radius=9,
                color=color, core_color=core_color,
                shape="shard", p_type="linear"
            ))
            # Right to left
            projs.append(BossProjectile(
                target_x + 420.0, py + 35.0, -speed, 0.0,
                damage=damage, radius=9,
                color=color, core_color=core_color,
                shape="shard", p_type="linear"
            ))
        return projs

    @staticmethod
    def spawn_homing_swarm(
        cx, cy, target_x, target_y, count, speed=4.8,
        color=(160, 40, 220), core_color=(240, 180, 255), radius=10, damage=18
    ):
        """Cluster of tracking shadow wisps."""
        if count <= 0:
            return []
        projs = []
        base_ang = math.atan2(target_y - cy, target_x - cx)
        for i in range(count):
            spread = random.uniform(-0.8, 0.8)
            ang = base_ang + spread
            cur_spd = speed * random.uniform(0.85, 1.15)
            vx = math.cos(ang) * cur_spd
            vy = math.sin(ang) * cur_spd
            projs.append(BossProjectile(
                cx, cy, vx, vy,
                damage=damage, radius=radius,
                color=color, core_color=core_color,
                shape="wisp", p_type="homing"
            ))
        return projs

    @staticmethod
    def spawn_meteor_curtain(
        target_x, target_y, count=10, spread_w=640, speed_y=7.5,
        color=(255, 75, 25), damage=24
    ):
        """Cascading angled meteor curtain falling across the battlefield."""
        if count <= 0:
            return []
        projs = []
        step = spread_w / count
        start_x = target_x - spread_w / 2.0
        for i in range(count):
            mx = start_x + i * step + random.uniform(-15, 15)
            my = target_y - random.uniform(380, 460)
            vx = random.uniform(-1.8, 1.8)
            vy = speed_y * random.uniform(0.9, 1.15)
            projs.append(BossProjectile(
                mx, my, vx, vy,
                damage=damage, radius=13,
                color=color, core_color=(255, 235, 140),
                shape="meteor", p_type="meteor"
            ))
        return projs

    @staticmethod
    def spawn_warp_nova(
        cx, cy, count=32, speed=6.8, color=(200, 50, 255),
        core_color=(255, 255, 255), radius=10, damage=22
    ):
        """Omni-directional 360-degree starburst nova following a warp/blitz."""
        if count <= 0:
            return []
        projs = []
        step = (2.0 * math.pi) / count
        for i in range(count):
            ang = i * step
            vx = math.cos(ang) * speed
            vy = math.sin(ang) * speed
            projs.append(BossProjectile(
                cx, cy, vx, vy,
                damage=damage, radius=radius,
                color=color, core_color=core_color,
                shape="shard", p_type="linear"
            ))
        return projs
