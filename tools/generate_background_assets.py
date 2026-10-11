"""
Generate Seamless Horizontally-Looping Parallax Pixel Art Background Assets
Creates multi-plane background layers in assets/backgrounds/:
1. bg_far_mountains.png (Far misty mountains)
2. bg_rolling_hills.png (Rolling hills with pine gradients)
3. bg_mid_forest.png    (Mid-ground forest canopy and ancient spud ruins)
4. bg_sky_clouds.png    (Floating ethereal troposphere pixel clouds)
5. bg_space_nebula.png  (Deep celestial cosmic nebula & constellation void)

All layers are perfectly horizontally periodic: f(0) == f(width).
"""

import os
import math
import random
import pygame

OUTPUT_DIR = os.path.join("assets", "backgrounds")
WIDTH = 640
HEIGHT = 360


def ensure_dir(path):
    os.makedirs(path, exist_ok=True)


def periodic_perlin_1d(x, width, octaves=4, seed=42):
    """Generates seamless periodic 1D terrain height using trigonometric harmonics."""
    val = 0.0
    amp = 1.0
    freq = 1.0
    total_amp = 0.0
    for o in range(octaves):
        theta = (2.0 * math.pi * x * freq) / width
        val += amp * (math.sin(theta + seed * 1.7) * 0.7 + math.cos(theta * 2.0 + seed * 0.9) * 0.3)
        total_amp += amp
        amp *= 0.5
        freq *= 2.0
    return val / total_amp


def generate_far_mountains():
    surf = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    base_y = 170

    # Ridge 1: Furthest mountain peak (soft misty cyan-slate)
    col_peak_far = (75, 115, 145, 190)
    col_shadow_far = (55, 90, 120, 210)
    for x in range(WIDTH):
        h = int(periodic_perlin_1d(x, WIDTH, octaves=3, seed=12) * 65)
        peak_y = base_y - h
        for y in range(peak_y, HEIGHT):
            # Shading by slope derivative
            slope = periodic_perlin_1d(x + 1, WIDTH, octaves=3, seed=12) - periodic_perlin_1d(x - 1, WIDTH, octaves=3, seed=12)
            c = col_shadow_far if slope > 0 else col_peak_far
            # Subtle vertical depth gradient
            depth_f = min(1.0, (y - peak_y) / 80.0)
            rc = int(c[0] * (1.0 - depth_f * 0.15))
            gc = int(c[1] * (1.0 - depth_f * 0.15))
            bc = int(c[2] * (1.0 - depth_f * 0.15))
            surf.set_at((x, y), (rc, gc, bc, c[3]))

    # Ridge 2: Mid mountain peak (crisp celestial azure)
    col_peak_mid = (90, 140, 170, 230)
    col_shadow_mid = (65, 110, 140, 240)
    for x in range(WIDTH):
        h = int(periodic_perlin_1d(x, WIDTH, octaves=4, seed=55) * 50)
        peak_y = base_y + 35 - h
        for y in range(peak_y, HEIGHT):
            slope = periodic_perlin_1d(x + 1, WIDTH, octaves=4, seed=55) - periodic_perlin_1d(x - 1, WIDTH, octaves=4, seed=55)
            c = col_shadow_mid if slope > 0 else col_peak_mid
            surf.set_at((x, y), c)

    return surf


def generate_rolling_hills():
    surf = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    base_y = 200

    # Back Hills (teal-green pine horizon)
    col_back = (48, 105, 92, 235)
    for x in range(WIDTH):
        h = int(math.sin(2.0 * math.pi * x / WIDTH) * 35 + math.sin(4.0 * math.pi * x / WIDTH) * 15)
        hill_y = base_y - h
        for y in range(hill_y, HEIGHT):
            surf.set_at((x, y), col_back)

    # Front Rolling Hills (rich emerald grass slopes with rim highlight)
    col_front = (38, 92, 65, 255)
    col_rim = (62, 138, 90, 255)
    for x in range(WIDTH):
        h = int(math.cos(2.0 * math.pi * x / WIDTH) * 28 + math.sin(6.0 * math.pi * x / WIDTH) * 10)
        hill_y = base_y + 40 - h
        surf.set_at((x, hill_y), col_rim)
        surf.set_at((x, hill_y + 1), col_rim)
        for y in range(hill_y + 2, HEIGHT):
            surf.set_at((x, y), col_front)

    return surf


def generate_mid_forest():
    surf = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    base_y = 260
    col_pine = (25, 65, 50, 245)
    col_trunk = (18, 48, 38, 255)
    col_ruin = (70, 75, 90, 240)

    # Ancient Stone Spud Pillars / Ruins spaced across horizon
    ruin_positions = [60, 220, 380, 540]
    for rx in ruin_positions:
        rw = 18
        rh = 45
        for x in range(rx, rx + rw):
            for y in range(base_y - rh, base_y):
                surf.set_at((x, y), col_ruin)
        # Pillar cap
        for x in range(rx - 3, rx + rw + 3):
            surf.set_at((x, base_y - rh), (95, 100, 120, 250))
            surf.set_at((x, base_y - rh - 1), (95, 100, 120, 250))

    # Dense pine tree silhouettes (periodically spaced)
    rng = random.Random(888)
    tree_xs = list(range(0, WIDTH, 16))
    for tx in tree_xs:
        th = 40 + (tx % 29)
        top_y = base_y - th
        # Trunk
        for y in range(top_y + 15, HEIGHT):
            surf.set_at((tx, y), col_trunk)
            surf.set_at((tx + 1, y), col_trunk)
        # Tiered Pine Fronds
        for tier in range(4):
            cy = top_y + tier * 8
            w = 3 + tier * 3
            for dx in range(-w, w + 1):
                px = (tx + dx) % WIDTH
                for py in range(cy, cy + 8):
                    surf.set_at((px, py), col_pine)

    # Base ground filler
    for x in range(WIDTH):
        for y in range(base_y + 2, HEIGHT):
            surf.set_at((x, y), (20, 52, 40, 255))

    return surf


def generate_sky_clouds():
    surf = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    col_cloud = (240, 248, 255, 140)
    col_cloud_hi = (255, 255, 255, 190)

    # 3 cloud banks drifting across upper sky
    cloud_centers = [(100, 70, 48), (280, 100, 60), (460, 60, 42), (600, 85, 36)]
    for cx, cy, rad in cloud_centers:
        for dx in range(-rad, rad + 1):
            for dy in range(-rad // 2, rad // 2 + 1):
                if (dx * dx) / float(rad * rad) + (dy * dy) / float((rad * 0.45) ** 2) <= 1.0:
                    px = (cx + dx) % WIDTH
                    py = cy + dy
                    c = col_cloud_hi if dy < 0 else col_cloud
                    surf.set_at((px, py), c)

    return surf


def generate_space_nebula():
    surf = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    # Deep cosmic stars and nebula clouds
    rng = random.Random(101)

    # Nebula dust clouds (ethereal magenta and violet)
    for x in range(WIDTH):
        for y in range(HEIGHT):
            v1 = (math.sin(4.0 * math.pi * x / WIDTH) + math.cos(4.0 * math.pi * y / HEIGHT)) * 0.5
            v2 = (math.sin(8.0 * math.pi * x / WIDTH + 1.2) + math.sin(6.0 * math.pi * y / HEIGHT + 0.8)) * 0.5
            tot = (v1 + v2) * 0.5
            if tot > 0.45:
                alpha = int((tot - 0.45) * 160)
                surf.set_at((x, y), (90, 30, 130, min(140, alpha)))

    # Brilliant constellation stars
    for _ in range(120):
        sx = rng.randint(0, WIDTH - 1)
        sy = rng.randint(0, HEIGHT - 1)
        bright = rng.randint(180, 255)
        surf.set_at((sx, sy), (bright, bright, min(255, bright + 15), 255))
        # Larger cross twinkle for hero stars
        if rng.random() < 0.15:
            col_t = (255, 240, 200, 180)
            if 0 < sx < WIDTH - 1 and 0 < sy < HEIGHT - 1:
                surf.set_at((sx + 1, sy), col_t)
                surf.set_at((sx - 1, sy), col_t)
                surf.set_at((sx, sy + 1), col_t)
                surf.set_at((sx, sy - 1), col_t)

    return surf


def main():
    pygame.init()
    ensure_dir(OUTPUT_DIR)

    layers = [
        ("bg_far_mountains.png", generate_far_mountains()),
        ("bg_rolling_hills.png", generate_rolling_hills()),
        ("bg_mid_forest.png", generate_mid_forest()),
        ("bg_sky_clouds.png", generate_sky_clouds()),
        ("bg_space_nebula.png", generate_space_nebula()),
    ]

    for filename, surf in layers:
        filepath = os.path.join(OUTPUT_DIR, filename)
        pygame.image.save(surf, filepath)
        print(f"[Assets] Generated parallax layer: {filepath} ({surf.get_width()}x{surf.get_height()})")


if __name__ == "__main__":
    main()
