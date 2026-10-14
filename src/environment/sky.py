"""
Terraria Pygame - Sky, Day/Night Cycle & Multi-Plane Parallax Backgrounds
Simulates smooth celestial progression (Sun & Moon arcs), dynamic sky gradients,
twinkling starfields, multi-plane horizontally-looping parallax pixel art backgrounds
(locked Y-parallax), and atmospheric altitude transition into cosmic space.
Developer: Kurados
"""

import os
import math
import random
import pygame
from src.constants import SCREEN_WIDTH, SCREEN_HEIGHT, SCALED_TILE

BACKGROUNDS_DIR = os.path.join("assets", "backgrounds")


class DayNightCycle:
    def __init__(self, asset_factory, cycle_duration=360.0):
        self.asset_factory = asset_factory
        self.cycle_duration = cycle_duration  # seconds for full 24h cycle
        self.time = 0.25 * cycle_duration     # start at noon
        
        self.sun_surf = asset_factory.environment["sun"]
        self.moon_surf = asset_factory.environment["moon"]

        # Generate persistent, deterministic starfield
        self.stars = []
        rng = random.Random(42)
        for _ in range(140):
            sx = rng.randint(0, SCREEN_WIDTH)
            sy = rng.randint(0, SCREEN_HEIGHT)
            brightness = rng.uniform(0.4, 1.0)
            phase = rng.uniform(0.0, math.pi * 2.0)
            speed = rng.uniform(0.8, 1.25)
            self.stars.append((sx, sy, brightness, phase, speed))

        # Pre-computed twinkling star frames for high performance
        self.star_frames = self._create_star_frames()
        self.star_surfaces = self._create_star_surfaces()

        # Load Parallax Background Assets from assets/backgrounds/
        self._load_background_assets()

        # Cached sky gradient surface for high performance
        self._cached_sky_surf = None
        self._cached_top_c = None
        self._cached_bot_c = None
        self._last_bake_ticks = 0
        self._last_bg_alpha = 255

    def _load_background_assets(self):
        """Loads, pre-scales, and RLE-accelerates multi-plane parallax pixel art layers from assets/backgrounds/."""
        sw, sh = SCREEN_WIDTH, SCREEN_HEIGHT

        def _load_or_fallback(filename, fallback_fn):
            path = os.path.join(BACKGROUNDS_DIR, filename)
            if os.path.isfile(path):
                try:
                    raw = pygame.image.load(path)
                    if pygame.display.get_surface() is not None:
                        return pygame.transform.scale(raw, (sw, sh)).convert_alpha()
                    return pygame.transform.scale(raw, (sw, sh))
                except Exception:
                    pass
            return fallback_fn()

        def _optimize_parallax_band(surf):
            """Crops transparent top sky space and clears surface-level alpha modulation for SIMD 32-bit blitting."""
            br = surf.get_bounding_rect()
            if br.width <= 0 or br.height <= 0:
                return surf, 0
            band_rect = pygame.Rect(0, br.top, sw, sh - br.top)
            band = surf.subsurface(band_rect).copy()
            band.set_alpha(None)
            return band, band_rect.top

        self.mountains_surf = _load_or_fallback("bg_far_mountains.png", self._create_mountain_silhouette)
        self.hills_surf = _load_or_fallback("bg_rolling_hills.png", self._create_mountain_silhouette)
        self.trees_surf = _load_or_fallback("bg_mid_forest.png", self._create_tree_silhouette)
        self.clouds_surf = _load_or_fallback("bg_sky_clouds.png", lambda: pygame.Surface((sw, sh), pygame.SRCALPHA))
        self.space_nebula_surf = _load_or_fallback("bg_space_nebula.png", lambda: pygame.Surface((sw, sh), pygame.SRCALPHA))

        self._mountains_band, self._mountains_top = _optimize_parallax_band(self.mountains_surf)
        self._hills_band, self._hills_top = _optimize_parallax_band(self.hills_surf)
        self._trees_band, self._trees_top = _optimize_parallax_band(self.trees_surf)

    @property
    def time_of_day(self):
        """Returns 0.0 to 1.0 representing progress through 24-hour cycle."""
        return (self.time % self.cycle_duration) / self.cycle_duration

    @property
    def is_night(self):
        """Returns True if it is currently nighttime."""
        t = self.time_of_day
        # Philippine night cycle: ~6:28 PM to 5:00 AM (at 5:00 AM dawn starts)
        return 0.52 <= t < (23.0 / 24.0)

    @property
    def ambient_sunlight(self):
        """Calculates 2D light intensity (3 to 15) for the lighting engine."""
        t = self.time_of_day
        t_5am = 23.0 / 24.0
        if 0.02 <= t <= 0.48:
            return 15  # Morning & Daytime full warm sunlight
        elif 0.53 <= t <= t_5am:
            return 3   # Night darkness
        elif t < 0.02:
            # 6:00 AM to 6:30 AM: Dawn light completes rise to 15
            frac = t / 0.02
            return min(15, max(3, int(10 + frac * 5)))
        elif t > t_5am:
            # 5:00 AM to 6:00 AM: Starts to not be pitch black (light rises 3 -> 10)
            frac = (t - t_5am) / (1.0 - t_5am)
            return min(15, max(3, int(3 + frac * 7)))
        else:
            # 5:30 PM to 6:43 PM: Sunset and dusk transition (15 -> 3)
            frac = (t - 0.48) / 0.05
            return min(15, max(3, int(15 - frac * 12)))

    @property
    def atmospheric_tint(self):
        """Returns (r_mult, g_mult, b_mult) color grading based on celestial time."""
        t = self.time_of_day
        t_5am = 23.0 / 24.0
        if (t >= t_5am or t < 0.02) or (0.48 <= t < 0.53):
            # Dawn (5:00 AM - 6:30 AM) & Sunset (5:30 PM - 6:43 PM): Glowing warm golden amber
            return (1.20, 1.05, 0.85)
        elif 0.53 <= t < t_5am:
            # Moonlit Night (6:43 PM to 5:00 AM): Deep sapphire blue
            return (0.75, 0.88, 1.22)
        else:
            # Daytime (6:30 AM to 5:30 PM): Crisp radiant warm sunlight
            return (1.08, 1.04, 0.98)

    def update(self, dt):
        self.time += dt

    def get_time_string(self):
        """Returns user-friendly in-game celestial time (e.g. '12:00 PM (Day)')."""
        t = self.time_of_day
        # 0.0 is 6:00 AM (Dawn/Sunrise), 0.25 is 12:00 PM (Noon), 0.5 is 6:00 PM (Dusk/Sunset), 0.75 is 12:00 AM (Midnight)
        total_hours = (t * 24.0 + 6.0) % 24.0
        hour = int(total_hours) % 24
        minute = int((total_hours * 60) % 60)
        period = "AM" if hour < 12 else "PM"
        display_hour = hour % 12
        if display_hour == 0:
            display_hour = 12
        phase = "Night" if self.is_night else "Day"
        return f"{display_hour}:{minute:02d} {period} ({phase})"

    def _lerp_color(self, c1, c2, t):
        t = max(0.0, min(1.0, t))
        return (
            int(c1[0] + (c2[0] - c1[0]) * t),
            int(c1[1] + (c2[1] - c1[1]) * t),
            int(c1[2] + (c2[2] - c1[2]) * t),
        )

    def get_sky_colors(self):
        """Returns (top_color, bottom_color) based on current celestial time."""
        try:
            from src.environment.sky_presets import get_procedural_sky_colors
            return get_procedural_sky_colors(self.time_of_day)
        except Exception:
            pass
        t = self.time_of_day
        c_day_top = (115, 175, 195)
        c_day_bot = (175, 215, 225)
        c_dusk_top = (90, 50, 95)
        c_dusk_bot = (250, 135, 85)
        c_night_top = (12, 18, 35)
        c_night_bot = (25, 40, 65)
        c_dawn_top = (60, 50, 90)
        c_dawn_bot = (245, 155, 110)
        t_5am = 23.0 / 24.0

        if t < 0.02:
            frac = t / 0.02
            return self._lerp_color(c_dawn_top, c_day_top, frac), self._lerp_color(c_dawn_bot, c_day_bot, frac)
        elif t < 0.48:
            return c_day_top, c_day_bot
        elif t < 0.50:
            frac = (t - 0.48) / 0.02
            return self._lerp_color(c_day_top, c_dusk_top, frac), self._lerp_color(c_day_bot, c_dusk_bot, frac)
        elif t < 0.53:
            frac = (t - 0.50) / 0.03
            return self._lerp_color(c_dusk_top, c_night_top, frac), self._lerp_color(c_dusk_bot, c_night_bot, frac)
        elif t < t_5am:
            return c_night_top, c_night_bot
        else:
            frac = (t - t_5am) / (1.0 - t_5am)
            return self._lerp_color(c_night_top, c_dawn_top, frac), self._lerp_color(c_night_bot, c_dawn_bot, frac)

    def get_altitude_sky_colors(self, camera_y_tile):
        """
        Transitions sky colors naturally based on altitude:
        - Troposphere (ty >= 45): Surface day/night cycle colors
        - Stratosphere (45 > ty >= -20): Deepening cobalt twilight (day) or deep navy (night)
        - Mesosphere (-20 > ty >= -80): Dark indigo & midnight violet
        - Thermosphere / Space (ty < -80): Pitch black space void (2, 2, 6) to (0, 0, 2)
        Interpolation is smoothly shaped with Hermite smoothstep to eliminate color banding/abrupt clamps.
        """
        base_top, base_bot = self.get_sky_colors()

        if camera_y_tile >= 45:
            return base_top, base_bot

        # Smooth day vs night factor for intermediate stratosphere & mesosphere targets
        day_factor = min(1.0, max(0.0, (self.ambient_sunlight - 3) / 12.0))
        c_strato_top = self._lerp_color((10, 15, 30), (25, 38, 70), day_factor)
        c_strato_bot = self._lerp_color((18, 25, 48), (50, 75, 110), day_factor)

        c_meso_top = self._lerp_color((5, 8, 20), (8, 12, 32), day_factor)
        c_meso_bot = self._lerp_color((10, 14, 30), (18, 22, 48), day_factor)

        # Deep space void (ty <= -140)
        c_space_top = (2, 2, 6)
        c_space_bot = (0, 0, 2)

        if camera_y_tile >= -20:
            frac = (45.0 - camera_y_tile) / 65.0
            s_frac = frac * frac * (3.0 - 2.0 * frac)
            return self._lerp_color(base_top, c_strato_top, s_frac), self._lerp_color(base_bot, c_strato_bot, s_frac)
        elif camera_y_tile >= -80:
            frac = (-20.0 - camera_y_tile) / 60.0
            s_frac = frac * frac * (3.0 - 2.0 * frac)
            return self._lerp_color(c_strato_top, c_meso_top, s_frac), self._lerp_color(c_strato_bot, c_meso_bot, s_frac)
        else:
            frac = min(1.0, (-80.0 - camera_y_tile) / 60.0)
            s_frac = frac * frac * (3.0 - 2.0 * frac)
            return self._lerp_color(c_meso_top, c_space_top, s_frac), self._lerp_color(c_meso_bot, c_space_bot, s_frac)

    def _create_mountain_silhouette(self):
        w, h = SCREEN_WIDTH, SCREEN_HEIGHT
        surf = pygame.Surface((w, h), pygame.SRCALPHA)
        color = (65, 120, 145, 180)
        points = [(0, h)]
        step = 20
        freq = (2.0 * math.pi) / w
        for x in range(0, w + step, step):
            py = int(h - 180 + 40 * math.sin(x * freq) + 15 * math.sin(x * freq * 2.0))
            points.append((x, py))
        points.append((w, h))
        pygame.draw.polygon(surf, color, points)
        return surf

    def _create_tree_silhouette(self):
        w, h = SCREEN_WIDTH, SCREEN_HEIGHT
        surf = pygame.Surface((w, h), pygame.SRCALPHA)
        color = (45, 85, 65, 210)
        for x in range(0, w, 20):
            tree_h = 45 + (x % 31)
            pygame.draw.circle(surf, color, (x + 10, h - tree_h + 12), 12)
            pygame.draw.rect(surf, color, (x + 8, h - tree_h + 12, 4, tree_h - 12))
        return surf

    def _create_star_frames(self):
        frames = []
        for f in range(4):
            frame_stars = []
            for item in self.stars:
                sx, sy, bright = item[0], item[1], item[2]
                phase = (f * 1.57 + sx * 0.1) % (math.pi * 2.0)
                twinkle = (math.sin(phase) + 1.0) * 0.5 * bright
                alpha = int(twinkle * 220)
                if alpha > 30:
                    val = min(255, max(80, int(150 + twinkle * 105)))
                    frame_stars.append((sx, sy, (val, val, val)))
            frames.append(frame_stars)
        return frames

    def _create_star_surfaces(self):
        surfs = []
        num_frames = 16
        for f in range(num_frames):
            s = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            for item in self.stars:
                sx, sy = item[0], item[1]
                bright = item[2]
                p_off = item[3] if len(item) > 3 else (sx * 0.1)
                s_mult = item[4] if len(item) > 4 else 1.0
                phase = (f * (2.0 * math.pi / num_frames) * s_mult + p_off) % (2.0 * math.pi)
                twinkle = 0.55 + 0.45 * (0.5 + 0.5 * math.sin(phase)) * bright
                val = min(255, max(70, int(140 + twinkle * 115)))
                alpha = int(twinkle * 220)
                s.set_at((sx, sy), (val, val, min(255, val + 15), alpha))
            surfs.append(s)
        return surfs

    def render(self, target_surf, camera):
        """
        Draws pure sky gradient, twinkling stars, and sun/moon celestial bodies.
        Parallax assets (clouds, mountains, hills, trees) are excluded for a clean sky and fast rendering.
        """
        sw, sh = target_surf.get_width(), target_surf.get_height()
        cam_y = getattr(camera, "y", 9999.0)
        cam_y_tile = cam_y / float(SCALED_TILE)

        # High atmosphere / space stratum check (Sky Citadel arena is at ty <= -150)
        in_space = cam_y_tile <= -100

        # 1. Pure Sky Gradient based on altitude & celestial time
        top_c, bot_c = self.get_altitude_sky_colors(cam_y_tile)

        now_ticks = pygame.time.get_ticks()
        if (self._cached_sky_surf is None or
            self._cached_top_c != top_c or self._cached_bot_c != bot_c or
            self._cached_sky_surf.get_width() != sw or
            self._cached_sky_surf.get_height() != sh):
            
            # SIMD hardware-accelerated 2-pixel smoothscale (< 0.03ms per frame)
            grad_2px = pygame.Surface((1, 2))
            grad_2px.set_at((0, 0), top_c)
            grad_2px.set_at((0, 1), bot_c)
            self._cached_sky_surf = pygame.transform.smoothscale(grad_2px, (sw, sh))
            self._cached_top_c = top_c
            self._cached_bot_c = bot_c
            self._last_bake_ticks = now_ticks

        target_surf.blit(self._cached_sky_surf, (0, 0))

        # 2. Twinkling Stars (Active during night or when high in the atmosphere/space)
        show_stars = in_space or self.is_night or cam_y_tile < 0 or (0.50 <= self.time_of_day < (23.5 / 24.0))
        if show_stars:
            star_mult = 1.0
            if not in_space and cam_y_tile >= 0:
                t_day = self.time_of_day
                if 0.50 <= t_day < 0.53:
                    star_mult = (t_day - 0.50) / 0.03
                elif t_day >= (23.0 / 24.0):
                    # Fade out between 5:00 AM and 5:30 AM
                    star_mult = max(0.0, 1.0 - (t_day - (23.0 / 24.0)) / (0.5 / 24.0))
            if star_mult > 0.05:
                if getattr(self, "star_surfaces", None):
                    frame_idx = (now_ticks // 100) % len(self.star_surfaces)
                    star_surf = self.star_surfaces[frame_idx]
                    if star_mult < 0.98:
                        mod_surf = star_surf.copy()
                        mod_surf.set_alpha(int(255 * star_mult))
                        target_surf.blit(mod_surf, (0, 0))
                    else:
                        target_surf.blit(star_surf, (0, 0))
                else:
                    frame_idx = (now_ticks // 220) % len(self.star_frames)
                    for sx, sy, star_c in self.star_frames[frame_idx]:
                        sc = (int(star_c[0] * star_mult), int(star_c[1] * star_mult), int(star_c[2] * star_mult)) if star_mult < 0.98 else star_c
                        target_surf.set_at((sx, sy), sc)

        # 3. Celestial Orbit (Sun & Moon Arc - Philippine timing)
        # 6:00 AM (t = 0.0) is the start of the sun rising; sets at 6:00 PM (t = 0.50)
        t = self.time_of_day
        if t <= 0.51:
            sun_t = min(1.0, max(0.0, t / 0.50))
            sun_x = sun_t * sw
            sun_y = sh * 0.7 - math.sin(sun_t * math.pi) * (sh * 0.55)
            target_surf.blit(self.sun_surf, (sun_x - 20, sun_y - 20))

        if (t >= 0.49 or t < 0.02) or in_space:
            if t >= 0.49:
                moon_t = (t - 0.49) / 0.53
            else:
                moon_t = (t + 1.0 - 0.49) / 0.53
            moon_t = max(0.0, min(1.0, moon_t))
            moon_x = moon_t * sw
            moon_y = sh * 0.7 - math.sin(moon_t * math.pi) * (sh * 0.55)
            target_surf.blit(self.moon_surf, (moon_x - 16, moon_y - 16))
