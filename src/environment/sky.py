"""
Terraria Pygame - Sky, Day/Night Cycle & Parallax Backgrounds
Simulates smooth celestial progression (Sun & Moon arcs), dynamic sky gradients,
twinkling starfields, and multi-layer parallax scrolling mountains and forests.
"""

import math
import random
import pygame
from src.constants import SCREEN_WIDTH, SCREEN_HEIGHT

class DayNightCycle:
    def __init__(self, asset_factory, cycle_duration=360.0):
        self.asset_factory = asset_factory
        self.cycle_duration = cycle_duration  # seconds for full 24h cycle
        self.time = 0.25 * cycle_duration     # start at noon
        
        self.sun_surf = asset_factory.environment["sun"]
        self.moon_surf = asset_factory.environment["moon"]

        # Generate persistent starfield
        self.stars = []
        rng = random.Random(42)
        for _ in range(90):
            sx = rng.randint(0, SCREEN_WIDTH)
            sy = rng.randint(0, SCREEN_HEIGHT // 2)
            brightness = rng.uniform(0.4, 1.0)
            self.stars.append((sx, sy, brightness))

        # Generate Parallax Silhouette Surfaces
        self.mountains_surf = self._create_mountain_silhouette()
        self.trees_surf = self._create_tree_silhouette()

        # Cached sky gradient surface for high performance
        self._cached_sky_surf = None
        self._cached_top_c = None
        self._cached_bot_c = None
        self._last_bake_ticks = 0

    @property
    def time_of_day(self):
        """Returns 0.0 to 1.0 representing progress through 24-hour cycle."""
        return (self.time % self.cycle_duration) / self.cycle_duration

    @property
    def is_night(self):
        """Returns True if it is currently nighttime."""
        t = self.time_of_day
        return 0.52 <= t <= 0.95

    @property
    def ambient_sunlight(self):
        """Calculates 2D light intensity (2 to 15) for the lighting engine."""
        t = self.time_of_day
        if 0.15 <= t <= 0.45:
            return 15  # Full noon sunlight
        elif 0.55 <= t <= 0.90:
            return 3   # Night darkness
        elif t < 0.15:
            # Sunrise transition (3 -> 15)
            frac = t / 0.15
            return int(3 + frac * 12)
        else:
            # Sunset transition (15 -> 3)
            frac = (t - 0.45) / 0.10
            return int(15 - frac * 12)

    @property
    def atmospheric_tint(self):
        """Returns (r_mult, g_mult, b_mult) color grading based on celestial time."""
        t = self.time_of_day
        if (0.0 <= t < 0.15) or (0.45 <= t < 0.55):
            # Dawn / Sunset: Glowing warm amber
            return (1.18, 0.96, 0.76)
        elif 0.55 <= t <= 0.92:
            # Moonlit Night: Deep sapphire blue
            return (0.75, 0.88, 1.22)
        else:
            # Daytime: Crisp radiant sunlight
            return (1.05, 1.02, 0.98)

    def update(self, dt):
        self.time += dt

    def get_time_string(self):
        """Returns user-friendly in-game celestial time (e.g. '12:00 PM (Day)')."""
        t = self.time_of_day
        # 0.0 is 6:00 AM (Dawn), 0.25 is 12:00 PM (Noon), 0.5 is 6:00 PM (Dusk), 0.75 is 12:00 AM (Midnight)
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
        return (
            int(c1[0] + (c2[0] - c1[0]) * t),
            int(c1[1] + (c2[1] - c1[1]) * t),
            int(c1[2] + (c2[2] - c1[2]) * t),
        )

    def get_sky_colors(self):
        """Returns (top_color, bottom_color) based on current celestial time."""
        t = self.time_of_day

        # Stardew Valley x Terraria pastel teal/cyan day palette matching reference image
        c_day_top = (115, 175, 195)
        c_day_bot = (175, 215, 225)

        c_dusk_top = (90, 50, 95)
        c_dusk_bot = (250, 135, 85)

        c_night_top = (12, 18, 35)
        c_night_bot = (25, 40, 65)

        c_dawn_top = (60, 50, 90)
        c_dawn_bot = (245, 155, 110)

        if t < 0.12:
            # Dawn
            frac = t / 0.12
            return self._lerp_color(c_night_top, c_dawn_top, frac), self._lerp_color(c_night_bot, c_dawn_bot, frac)
        elif t < 0.22:
            # Dawn to Day
            frac = (t - 0.12) / 0.10
            return self._lerp_color(c_dawn_top, c_day_top, frac), self._lerp_color(c_dawn_bot, c_day_bot, frac)
        elif t < 0.48:
            # Day
            return c_day_top, c_day_bot
        elif t < 0.56:
            # Sunset / Dusk
            frac = (t - 0.48) / 0.08
            return self._lerp_color(c_day_top, c_dusk_top, frac), self._lerp_color(c_day_bot, c_dusk_bot, frac)
        elif t < 0.65:
            # Dusk to Night
            frac = (t - 0.56) / 0.09
            return self._lerp_color(c_dusk_top, c_night_top, frac), self._lerp_color(c_dusk_bot, c_night_bot, frac)
        else:
            # Night
            return c_night_top, c_night_bot

    def _create_mountain_silhouette(self):
        """Generates soft rolling hills parallax silhouette matching reference image."""
        w, h = SCREEN_WIDTH * 2, 260
        surf = pygame.Surface((w, h), pygame.SRCALPHA)
        color = (65, 120, 145, 180)

        points = [(0, h)]
        step = 30
        rng = random.Random(999)
        for x in range(0, w + step, step):
            py = int(70 + 45 * math.sin(x * 0.015) + rng.randint(-15, 15))
            points.append((x, py))
        points.append((w, h))

        pygame.draw.polygon(surf, color, points)
        return surf

    def _create_tree_silhouette(self):
        """Generates mid-ground distant trees parallax silhouette."""
        w, h = SCREEN_WIDTH * 2, 180
        surf = pygame.Surface((w, h), pygame.SRCALPHA)
        color = (45, 85, 65, 210)

        for x in range(0, w, 20):
            tree_h = 45 + (x % 31)
            # Soft rounded canopy
            pygame.draw.circle(surf, color, (x + 10, h - tree_h + 12), 12)
            pygame.draw.rect(surf, color, (x + 8, h - tree_h + 12, 4, tree_h - 12))
        return surf

    def render(self, target_surf, camera):
        """Draws sky gradient, stars, sun/moon celestial bodies, and parallax mountains."""
        sw, sh = target_surf.get_width(), target_surf.get_height()

        # 1. Sky Gradient (Cached: only re-bake when colors shift and at least 200ms elapsed)
        top_c, bot_c = self.get_sky_colors()
        now_ticks = pygame.time.get_ticks()
        if (self._cached_sky_surf is None or
            ((now_ticks - self._last_bake_ticks) > 200 and (self._cached_top_c != top_c or self._cached_bot_c != bot_c)) or
            self._cached_sky_surf.get_width() != sw or
            self._cached_sky_surf.get_height() != sh):
            
            steps = 32
            gradient = pygame.Surface((1, steps))
            for y in range(steps):
                frac = y / float(steps)
                c = self._lerp_color(top_c, bot_c, frac)
                gradient.set_at((0, y), c)
            self._cached_sky_surf = pygame.transform.smoothscale(gradient, (sw, sh))
            self._cached_top_c = top_c
            self._cached_bot_c = bot_c
            self._last_bake_ticks = now_ticks

        target_surf.blit(self._cached_sky_surf, (0, 0))

        # 2. Twinkling Stars (if nighttime)
        if self.is_night or self.time_of_day > 0.52:
            time_sec = pygame.time.get_ticks() * 0.003
            for sx, sy, bright in self.stars:
                twinkle = (math.sin(time_sec + sx) + 1.0) * 0.5 * bright
                alpha = int(twinkle * 220)
                if alpha > 20:
                    star_c = (255, 255, 255)
                    target_surf.set_at((sx, sy), star_c)

        # 3. Celestial Orbit (Sun & Moon Arc)
        # Sun: active during day (0.0 to 0.5)
        t = self.time_of_day
        if t < 0.55:
            sun_t = t / 0.55  # 0.0 (left) to 1.0 (right)
            sun_x = sun_t * sw
            sun_y = sh * 0.7 - math.sin(sun_t * math.pi) * (sh * 0.55)
            target_surf.blit(self.sun_surf, (sun_x - 20, sun_y - 20))

        # Moon: active during night (0.50 to 1.0)
        if t >= 0.48:
            moon_t = (t - 0.48) / 0.52
            moon_x = moon_t * sw
            moon_y = sh * 0.7 - math.sin(moon_t * math.pi) * (sh * 0.55)
            target_surf.blit(self.moon_surf, (moon_x - 16, moon_y - 16))

        # 4. Parallax Mountain Silhouettes (Scroll factor 0.07)
        mount_offset = -(camera.x * 0.07) % SCREEN_WIDTH
        target_surf.blit(self.mountains_surf, (mount_offset - SCREEN_WIDTH, sh - 280))
        target_surf.blit(self.mountains_surf, (mount_offset, sh - 280))

        # 5. Parallax Forest Silhouettes (Scroll factor 0.18)
        tree_offset = -(camera.x * 0.18) % SCREEN_WIDTH
        target_surf.blit(self.trees_surf, (tree_offset - SCREEN_WIDTH, sh - 170))
        target_surf.blit(self.trees_surf, (tree_offset, sh - 170))
