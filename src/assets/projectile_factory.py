"""
Potaria - Projectile Asset Factory (Crisp 32x32 2D Pixel Art)
Generates all 40 projectile specifications (P01 to P40) from the
Potaria Projectile Asset Library with 100% offline consistency, exact palettes,
clean dark outlines, transparent backgrounds, and 0 stray pixels.
Developer: Kurados | Pure Python & pygame-ce
"""

import math
import pygame


def _create_p01_iron_arrow():
    surf = pygame.Surface((32, 32), pygame.SRCALPHA)
    # Shaft (x=6..21, y=15..16)
    for x in range(6, 22):
        surf.set_at((x, 14), (32, 35, 45, 255))
        surf.set_at((x, 15), (145, 95, 45, 255))
        surf.set_at((x, 16), (115, 75, 35, 255))
        surf.set_at((x, 17), (32, 35, 45, 255))
    # Fletchings at rear x=4..9
    fletch_top = [(4, 12), (5, 12), (6, 13), (7, 13), (8, 14), (9, 14)]
    fletch_bot = [(4, 19), (5, 19), (6, 18), (7, 18), (8, 17), (9, 17)]
    for fx, fy in fletch_top + fletch_bot:
        surf.set_at((fx, fy), (220, 215, 195, 255))
        surf.set_at((fx - 1, fy), (55, 50, 45, 255))
        surf.set_at((fx, fy - 1 if fy < 15 else fy + 1), (55, 50, 45, 255))
    # Iron arrowhead: sharp triangle x=20..29, y=12..20
    head_poly = [(20, 12), (29, 16), (20, 20), (22, 16)]
    pygame.draw.polygon(surf, (130, 140, 155), head_poly)
    pygame.draw.polygon(surf, (32, 35, 45), head_poly, 1)
    surf.set_at((29, 16), (32, 35, 45, 255))
    # Highlights & shadows
    pygame.draw.line(surf, (190, 200, 215), (21, 15), (27, 16), 1)
    pygame.draw.line(surf, (80, 88, 100), (21, 17), (26, 16), 1)
    return surf


def _create_p02_heavy_bolt():
    surf = pygame.Surface((32, 32), pygame.SRCALPHA)
    # Thick dark shaft x=8..19, y=14..17
    for x in range(8, 20):
        surf.set_at((x, 13), (25, 28, 35, 255))
        surf.set_at((x, 14), (90, 70, 50, 255))
        surf.set_at((x, 15), (75, 55, 40, 255))
        surf.set_at((x, 16), (55, 40, 30, 255))
        surf.set_at((x, 17), (25, 28, 35, 255))
    # Broad squared gunmetal tip x=19..28, y=11..20
    tip_poly = [(19, 11), (28, 13), (28, 18), (19, 20)]
    pygame.draw.polygon(surf, (95, 105, 120), tip_poly)
    pygame.draw.polygon(surf, (25, 28, 35), tip_poly, 1)
    # Chisel edge bevel & shadows
    pygame.draw.line(surf, (160, 170, 185), (20, 13), (27, 14), 1)
    pygame.draw.line(surf, (60, 68, 78), (20, 18), (27, 17), 1)
    # Rigid stabilizer fins at rear x=4..9
    fins = [(4, 11), (5, 11), (6, 12), (7, 12), (8, 13), (4, 20), (5, 20), (6, 19), (7, 19), (8, 18)]
    for fx, fy in fins:
        surf.set_at((fx, fy), (65, 72, 82, 255))
        surf.set_at((fx - 1, fy), (25, 28, 35, 255))
        surf.set_at((fx, fy - 1 if fy < 15 else fy + 1), (25, 28, 35, 255))
    return surf


def _create_p03_throwing_knife():
    surf = pygame.Surface((32, 32), pygame.SRCALPHA)
    # Handle wrap x=6..14, y=15..17
    for x in range(6, 15):
        surf.set_at((x, 14), (25, 28, 35, 255))
        col = (120, 75, 45) if x % 2 == 0 else (80, 50, 30)
        surf.set_at((x, 15), col)
        surf.set_at((x, 16), (50, 45, 45, 255))
        surf.set_at((x, 17), (25, 28, 35, 255))
    # Pommel cap at x=4..5
    for px in (4, 5):
        surf.set_at((px, 15), (140, 150, 165, 255))
        surf.set_at((px, 16), (110, 120, 135, 255))
    surf.set_at((3, 15), (25, 28, 35, 255))
    surf.set_at((3, 16), (25, 28, 35, 255))
    # Pointed blade x=14..28, y=13..19
    blade_poly = [(14, 13), (28, 16), (14, 19)]
    pygame.draw.polygon(surf, (190, 200, 215), blade_poly)
    pygame.draw.polygon(surf, (25, 28, 35), blade_poly, 1)
    surf.set_at((28, 16), (25, 28, 35, 255))
    # Cutting edge highlight & lower bevel
    pygame.draw.line(surf, (240, 248, 255), (15, 14), (27, 16), 1)
    pygame.draw.line(surf, (110, 120, 135), (15, 18), (26, 16), 1)
    return surf


def _create_p04_spinning_shuriken():
    surf = pygame.Surface((32, 32), pygame.SRCALPHA)
    # 4 points at (16, 3), (29, 16), (16, 29), (3, 16)
    pts = [(16, 3), (20, 12), (29, 16), (20, 20), (16, 29), (12, 20), (3, 16), (12, 12)]
    pygame.draw.polygon(surf, (140, 150, 165), pts)
    pygame.draw.polygon(surf, (25, 28, 35), pts, 1)
    # Facet shading: alternating light/shadow on triangles
    pygame.draw.polygon(surf, (225, 235, 245), [(16, 3), (16, 16), (20, 12)])
    pygame.draw.polygon(surf, (85, 95, 108), [(29, 16), (16, 16), (20, 20)])
    pygame.draw.polygon(surf, (225, 235, 245), [(16, 29), (16, 16), (12, 20)])
    pygame.draw.polygon(surf, (85, 95, 108), [(3, 16), (16, 16), (12, 12)])
    # Central hub with center hole
    pygame.draw.circle(surf, (45, 48, 55), (16, 16), 4)
    pygame.draw.circle(surf, (25, 28, 35), (16, 16), 4, 1)
    surf.set_at((16, 16), (0, 0, 0, 0))
    return surf


def _create_p05_returning_throwing_axe():
    surf = pygame.Surface((32, 32), pygame.SRCALPHA)
    # Sturdy angled handle from (8, 25) to (19, 10)
    pygame.draw.line(surf, (30, 25, 20), (7, 26), (18, 10), 3)
    pygame.draw.line(surf, (110, 70, 35), (8, 25), (19, 11), 2)
    # Leather wrap on handle
    for t in (0.3, 0.5, 0.7):
        wx = int(8 + (19 - 8) * t)
        wy = int(25 + (11 - 25) * t)
        surf.set_at((wx, wy), (150, 105, 65, 255))
    # Crescent axe head at top right
    head_poly = [(16, 8), (27, 7), (28, 16), (23, 20), (18, 15), (17, 10)]
    pygame.draw.polygon(surf, (155, 165, 180), head_poly)
    pygame.draw.polygon(surf, (30, 25, 20), head_poly, 1)
    # Bevel highlight & dark steel back
    pygame.draw.line(surf, (230, 240, 250), (27, 8), (27, 16), 1)
    pygame.draw.line(surf, (90, 100, 115), (17, 9), (18, 14), 1)
    return surf


def _create_p06_fireball():
    surf = pygame.Surface((32, 32), pygame.SRCALPHA)
    # Dynamic forward-facing flame mass pointing right
    flame_pts = [
        (4, 11), (10, 9), (17, 8), (24, 10), (28, 15), (28, 17),
        (24, 22), (17, 24), (10, 23), (3, 21), (7, 16)
    ]
    pygame.draw.polygon(surf, (210, 45, 20), flame_pts)
    pygame.draw.polygon(surf, (90, 15, 10), flame_pts, 1)
    # Mid-layer orange flame
    mid_pts = [(9, 12), (16, 10), (23, 12), (25, 16), (22, 20), (15, 22), (8, 19), (11, 16)]
    pygame.draw.polygon(surf, (255, 120, 20), mid_pts)
    # Inner gold flame
    gold_pts = [(13, 13), (19, 12), (23, 16), (18, 19), (12, 17)]
    pygame.draw.polygon(surf, (255, 200, 40), gold_pts)
    # Hot yellow-white core
    pygame.draw.circle(surf, (255, 255, 210), (19, 16), 3)
    return surf


def _create_p07_ice_shard():
    surf = pygame.Surface((32, 32), pygame.SRCALPHA)
    # Elongated pointed crystal shard pointing right
    shard_pts = [(6, 16), (12, 10), (29, 16), (12, 22)]
    pygame.draw.polygon(surf, (130, 205, 245), shard_pts)
    pygame.draw.polygon(surf, (25, 55, 95), shard_pts, 1)
    # Facets
    pygame.draw.polygon(surf, (195, 240, 255), [(6, 16), (12, 10), (29, 16)])
    pygame.draw.polygon(surf, (70, 130, 190), [(6, 16), (12, 22), (29, 16)])
    # White highlight ridge line
    pygame.draw.line(surf, (255, 255, 255), (7, 16), (28, 16), 1)
    return surf


def _create_p08_lightning_bolt():
    surf = pygame.Surface((32, 32), pygame.SRCALPHA)
    # Directional zigzag arc traversing right
    zigzag = [(4, 21), (12, 21), (9, 14), (20, 14), (16, 8), (28, 15), (20, 18), (22, 24), (14, 24), (16, 27)]
    # Outer dark blue outline
    pygame.draw.polygon(surf, (20, 35, 90), zigzag)
    # Inner cyan energy
    inner = [(5, 21), (11, 21), (10, 15), (19, 15), (17, 9), (27, 15), (20, 17), (21, 23), (15, 23), (16, 26)]
    pygame.draw.polygon(surf, (50, 210, 255), inner)
    # Core lightning stroke
    pygame.draw.lines(surf, (160, 245, 255), False, [(6, 21), (11, 15), (18, 12), (26, 15)], 2)
    pygame.draw.lines(surf, (255, 255, 230), False, [(7, 21), (11, 15), (18, 12), (26, 15)], 1)
    return surf


def _create_p09_shadow_orb():
    surf = pygame.Surface((32, 32), pygame.SRCALPHA)
    # Dense dark sphere centered at (16, 16), radius 11
    pygame.draw.circle(surf, (30, 10, 45), (16, 16), 11)
    pygame.draw.circle(surf, (65, 20, 95), (16, 16), 10)
    pygame.draw.circle(surf, (25, 8, 38), (16, 16), 7)
    # Violet rim highlight
    pygame.draw.arc(surf, (160, 60, 220), (6, 6, 20, 20), 0.5, 2.5, 2)
    # Inner glowing crescent/eye
    pygame.draw.ellipse(surf, (225, 120, 255), (14, 13, 7, 5))
    surf.set_at((17, 15), (255, 210, 255, 255))
    return surf


def _create_p10_poison_glob():
    surf = pygame.Surface((32, 32), pygame.SRCALPHA)
    # Organic asymmetrical toxic glob
    glob_pts = [(11, 9), (19, 8), (26, 12), (27, 17), (23, 22), (16, 23), (10, 18), (9, 13)]
    pygame.draw.polygon(surf, (40, 130, 35), glob_pts)
    pygame.draw.polygon(surf, (18, 45, 15), glob_pts, 1)
    # Lime midtone & acid highlight
    pygame.draw.circle(surf, (95, 205, 45), (17, 15), 6)
    pygame.draw.circle(surf, (180, 245, 75), (18, 14), 4)
    # Specular gloss
    surf.set_at((20, 12), (240, 255, 190, 255))
    surf.set_at((21, 12), (240, 255, 190, 255))
    # Trailing droplets
    pygame.draw.circle(surf, (18, 45, 15), (7, 19), 3)
    pygame.draw.circle(surf, (95, 205, 45), (7, 19), 2)
    pygame.draw.circle(surf, (18, 45, 15), (5, 12), 2)
    surf.set_at((5, 12), (180, 245, 75, 255))
    return surf


def _create_p11_holy_bolt():
    surf = pygame.Surface((32, 32), pygame.SRCALPHA)
    # Directional radiant diamond energy bolt
    pts = [(16, 5), (22, 13), (29, 16), (22, 19), (16, 27), (10, 19), (3, 16), (10, 13)]
    pygame.draw.polygon(surf, (230, 175, 30), pts)
    pygame.draw.polygon(surf, (110, 70, 15), pts, 1)
    # Radiant yellow inner diamond
    inner_pts = [(16, 9), (21, 14), (25, 16), (21, 18), (16, 23), (11, 18), (7, 16), (11, 14)]
    pygame.draw.polygon(surf, (255, 230, 100), inner_pts)
    # Ivory white brilliant core
    core_pts = [(16, 12), (19, 15), (21, 16), (19, 17), (16, 20), (13, 17), (11, 16), (13, 15)]
    pygame.draw.polygon(surf, (255, 255, 240), core_pts)
    return surf


def _create_p12_earth_shard():
    surf = pygame.Surface((32, 32), pygame.SRCALPHA)
    # Rough angular chipped stone splinter pointing right
    rock_pts = [(6, 12), (12, 8), (20, 11), (28, 16), (22, 22), (14, 24), (7, 21), (9, 16)]
    pygame.draw.polygon(surf, (165, 135, 105), rock_pts)
    pygame.draw.polygon(surf, (45, 35, 30), rock_pts, 1)
    # Shading facets
    pygame.draw.polygon(surf, (215, 185, 145), [(12, 8), (20, 11), (28, 16), (16, 16)])
    pygame.draw.polygon(surf, (90, 75, 65), [(6, 12), (9, 16), (7, 21), (14, 24), (16, 16)])
    # Dark mineral cracks
    pygame.draw.line(surf, (55, 42, 35), (14, 13), (18, 18), 1)
    pygame.draw.line(surf, (55, 42, 35), (18, 18), (23, 16), 1)
    return surf


def _create_p13_water_orb():
    surf = pygame.Surface((32, 32), pygame.SRCALPHA)
    # Streamlined hydrodynamic droplet pointing right
    drop_pts = [(6, 16), (10, 10), (17, 9), (28, 16), (17, 23), (10, 22)]
    pygame.draw.polygon(surf, (40, 160, 215), drop_pts)
    pygame.draw.polygon(surf, (15, 30, 70), drop_pts, 1)
    # Lower water shadow
    pygame.draw.polygon(surf, (30, 75, 155), [(6, 16), (10, 22), (17, 23), (28, 16)])
    # Upper light dome
    pygame.draw.polygon(surf, (110, 220, 245), [(7, 16), (11, 11), (17, 10), (27, 16)])
    # Specular curved glint
    pygame.draw.line(surf, (225, 250, 255), (12, 13), (20, 13), 1)
    surf.set_at((21, 14), (225, 250, 255, 255))
    return surf


def _create_p14_magma_core():
    surf = pygame.Surface((32, 32), pygame.SRCALPHA)
    # Irregular volcanic rock core centered at (16, 16)
    pts = [(9, 9), (17, 7), (24, 10), (26, 17), (22, 24), (15, 25), (8, 22), (6, 15)]
    pygame.draw.polygon(surf, (55, 48, 52), pts)
    pygame.draw.polygon(surf, (25, 20, 22), pts, 1)
    # Basalt rock shading
    pygame.draw.polygon(surf, (38, 32, 36), [(6, 15), (8, 22), (15, 25), (16, 16)])
    # Molten fissures cutting through rock
    fissures = [(10, 12), (14, 15), (17, 13), (22, 16), (19, 21), (15, 18), (11, 20)]
    for i in range(len(fissures) - 1):
        pygame.draw.line(surf, (180, 40, 15), fissures[i], fissures[i+1], 3)
        pygame.draw.line(surf, (255, 115, 20), fissures[i], fissures[i+1], 2)
        pygame.draw.line(surf, (255, 240, 130), fissures[i], fissures[i+1], 1)
    return surf


def _create_p15_wind_crescent():
    surf = pygame.Surface((32, 32), pygame.SRCALPHA)
    # Clean forward-curving gust crescent blade
    cres_pts = [(9, 5), (16, 8), (25, 16), (16, 24), (9, 27), (13, 21), (17, 16), (13, 11)]
    pygame.draw.polygon(surf, (140, 235, 215), cres_pts)
    pygame.draw.polygon(surf, (20, 65, 75), cres_pts, 1)
    # Outer cyan-teal edge
    pygame.draw.lines(surf, (50, 165, 175), False, [(9, 5), (16, 8), (25, 16), (16, 24), (9, 27)], 2)
    # Sharp white cutting blade crest
    pygame.draw.lines(surf, (245, 255, 250), False, [(11, 7), (17, 10), (24, 16), (17, 22), (11, 25)], 1)
    return surf


def _create_p16_arcane_orb():
    surf = pygame.Surface((32, 32), pygame.SRCALPHA)
    # Arcane mystical sphere centered at (16, 16), radius 11
    pygame.draw.circle(surf, (28, 16, 60), (16, 16), 11)
    pygame.draw.circle(surf, (115, 45, 185), (16, 16), 10)
    pygame.draw.circle(surf, (175, 75, 235), (16, 16), 7)
    # Cyan orbital glyph accents
    for gx, gy in [(16, 7), (16, 25), (7, 16), (25, 16)]:
        surf.set_at((gx, gy), (80, 230, 255, 255))
        surf.set_at((gx + 1, gy), (28, 16, 60, 255))
    # Central geometric diamond core
    d_pts = [(16, 11), (20, 16), (16, 21), (12, 16)]
    pygame.draw.polygon(surf, (245, 235, 255), d_pts)
    pygame.draw.polygon(surf, (80, 230, 255), d_pts, 1)
    return surf


def _create_p17_arcane_lance():
    surf = pygame.Surface((32, 32), pygame.SRCALPHA)
    # Long narrow spear-shaped energy beam pointing right
    lance_pts = [(4, 13), (20, 14), (30, 16), (20, 18), (4, 19), (8, 16)]
    pygame.draw.polygon(surf, (140, 60, 215), lance_pts)
    pygame.draw.polygon(surf, (30, 20, 70), lance_pts, 1)
    # Electric cyan inner beam
    inner_pts = [(6, 15), (22, 15), (29, 16), (22, 17), (6, 17)]
    pygame.draw.polygon(surf, (85, 210, 255), inner_pts)
    # Cyan-white lance core point
    pygame.draw.line(surf, (230, 250, 255), (10, 16), (28, 16), 1)
    return surf


def _create_p18_energy_disc():
    surf = pygame.Surface((32, 32), pygame.SRCALPHA)
    # Flat energy disc centered at (16, 16), radius 11
    pygame.draw.circle(surf, (18, 30, 65), (16, 16), 11)
    pygame.draw.circle(surf, (40, 130, 240), (16, 16), 10)
    pygame.draw.circle(surf, (90, 220, 255), (16, 16), 8, 2)
    # 4 notch segments
    for nx, ny in [(16, 6), (26, 16), (16, 26), (6, 16)]:
        surf.set_at((nx, ny), (210, 245, 255, 255))
    # Central dark recessed hub
    pygame.draw.circle(surf, (25, 40, 80), (16, 16), 4)
    pygame.draw.circle(surf, (210, 245, 255), (16, 16), 2)
    return surf


def _create_p19_homing_star():
    surf = pygame.Surface((32, 32), pygame.SRCALPHA)
    # Soft cyan energy halo motes
    for hx, hy in [(16, 2), (28, 11), (25, 27), (7, 27), (4, 11)]:
        surf.set_at((hx, hy), (80, 215, 240, 255))
    # 5-pointed star centered at (16, 16), outer radius 11, inner radius 5
    star_pts = []
    for i in range(10):
        angle = -math.pi / 2.0 + i * (math.pi / 5.0)
        r = 11 if i % 2 == 0 else 5
        star_pts.append((int(16 + math.cos(angle) * r), int(16 + math.sin(angle) * r)))
    pygame.draw.polygon(surf, (245, 190, 35), star_pts)
    pygame.draw.polygon(surf, (45, 38, 20), star_pts, 1)
    # Facets & core
    pygame.draw.circle(surf, (255, 230, 85), (16, 16), 5)
    pygame.draw.circle(surf, (255, 255, 220), (16, 16), 3)
    return surf


def _create_p20_void_sphere():
    surf = pygame.Surface((32, 32), pygame.SRCALPHA)
    # Broken orbital ring in electric magenta
    pygame.draw.arc(surf, (225, 45, 160), (4, 4, 24, 24), 0.2, 1.8, 2)
    pygame.draw.arc(surf, (225, 45, 160), (4, 4, 24, 24), 2.4, 3.8, 2)
    pygame.draw.arc(surf, (225, 45, 160), (4, 4, 24, 24), 4.4, 5.8, 2)
    # Orbital ring accents
    surf.set_at((26, 12), (245, 190, 255, 255))
    surf.set_at((8, 24), (245, 190, 255, 255))
    # Deep void black sphere centered at (16, 16), radius 8
    pygame.draw.circle(surf, (12, 8, 20), (16, 16), 8)
    pygame.draw.circle(surf, (24, 12, 35), (16, 16), 7)
    # Inverted singularity point
    surf.set_at((16, 16), (255, 230, 255, 255))
    return surf


def _create_p21_spectral_skull():
    surf = pygame.Surface((32, 32), pygame.SRCALPHA)
    # Smoky ghost tail trailing left x=4..13
    tail_pts = [(4, 16), (8, 12), (14, 13), (14, 19), (8, 20)]
    pygame.draw.polygon(surf, (65, 120, 185), tail_pts)
    pygame.draw.polygon(surf, (18, 25, 50), tail_pts, 1)
    # Stylized non-gory skull face pointing right
    skull_pts = [(13, 11), (20, 9), (26, 12), (27, 16), (26, 20), (20, 23), (13, 21), (15, 16)]
    pygame.draw.polygon(surf, (210, 235, 240), skull_pts)
    pygame.draw.polygon(surf, (18, 25, 50), skull_pts, 1)
    # Cranium highlight
    pygame.draw.line(surf, (245, 250, 255), (16, 11), (23, 11), 1)
    # Eye sockets
    surf.set_at((20, 13), (18, 25, 50, 255))
    surf.set_at((21, 13), (18, 25, 50, 255))
    surf.set_at((20, 18), (18, 25, 50, 255))
    surf.set_at((21, 18), (18, 25, 50, 255))
    return surf


def _create_p22_crystal_bolt():
    surf = pygame.Surface((32, 32), pygame.SRCALPHA)
    # Amethyst faceted crystal bolt pointing right
    bolt_pts = [(6, 16), (14, 11), (29, 16), (14, 21)]
    pygame.draw.polygon(surf, (105, 40, 120), bolt_pts)
    pygame.draw.polygon(surf, (50, 18, 55), bolt_pts, 1)
    # Rose crystal upper facets
    pygame.draw.polygon(surf, (175, 75, 160), [(6, 16), (14, 11), (29, 16)])
    # Pale lilac highlights
    pygame.draw.polygon(surf, (230, 170, 235), [(10, 14), (16, 12), (25, 15), (17, 16)])
    # Specular white crest line
    pygame.draw.line(surf, (255, 235, 255), (8, 16), (27, 16), 1)
    return surf


def _create_p23_fuse_bomb():
    surf = pygame.Surface((32, 32), pygame.SRCALPHA)
    # Cast-iron sphere centered at (15, 18), radius 9
    pygame.draw.circle(surf, (30, 30, 35), (15, 18), 9)
    pygame.draw.circle(surf, (85, 90, 98), (15, 18), 8)
    # Curved specular highlight
    pygame.draw.arc(surf, (150, 155, 165), (8, 11, 14, 14), 1.0, 2.5, 2)
    # Raised metal collar
    pygame.draw.rect(surf, (65, 70, 78), (13, 8, 4, 3))
    pygame.draw.rect(surf, (30, 30, 35), (13, 8, 4, 3), 1)
    # Short braided hemp fuse cord curving to (22, 5)
    fuse_pts = [(15, 8), (17, 6), (20, 5), (22, 5)]
    pygame.draw.lines(surf, (120, 85, 50), False, fuse_pts, 2)
    # Lit fuse spark
    pygame.draw.circle(surf, (255, 140, 30), (22, 5), 3)
    surf.set_at((22, 5), (255, 240, 180, 255))
    return surf


def _create_p24_spiked_blast_core():
    surf = pygame.Surface((32, 32), pygame.SRCALPHA)
    # 8 radiating broad forged iron spikes
    for i in range(8):
        ang = i * (math.pi / 4.0)
        sx = int(16 + math.cos(ang) * 13)
        sy = int(16 + math.sin(ang) * 13)
        px1 = int(16 + math.cos(ang - 0.25) * 7)
        py1 = int(16 + math.sin(ang - 0.25) * 7)
        px2 = int(16 + math.cos(ang + 0.25) * 7)
        py2 = int(16 + math.sin(ang + 0.25) * 7)
        pygame.draw.polygon(surf, (75, 80, 90), [(sx, sy), (px1, py1), (px2, py2)])
        pygame.draw.polygon(surf, (25, 26, 30), [(sx, sy), (px1, py1), (px2, py2)], 1)
    # Central sphere core
    pygame.draw.circle(surf, (25, 26, 30), (16, 16), 7)
    pygame.draw.circle(surf, (75, 80, 90), (16, 16), 6)
    # Warning glow vent in center
    pygame.draw.circle(surf, (235, 105, 30), (16, 16), 4)
    pygame.draw.circle(surf, (255, 190, 60), (16, 16), 2)
    return surf


def _create_p25_meteor_fragment():
    surf = pygame.Surface((32, 32), pygame.SRCALPHA)
    # Trailing flame at x=4..12
    flame_pts = [(4, 16), (9, 11), (14, 13), (14, 19), (9, 21)]
    pygame.draw.polygon(surf, (200, 45, 20), flame_pts)
    pygame.draw.polygon(surf, (32, 28, 30), flame_pts, 1)
    # Jagged rock body x=12..27, y=9..23
    rock_pts = [(12, 11), (19, 8), (26, 12), (28, 16), (25, 21), (18, 23), (12, 20)]
    pygame.draw.polygon(surf, (70, 62, 65), rock_pts)
    pygame.draw.polygon(surf, (32, 28, 30), rock_pts, 1)
    # Molten leading edge cracks
    pygame.draw.lines(surf, (255, 125, 25), False, [(17, 12), (22, 14), (27, 16), (22, 18), (17, 20)], 2)
    pygame.draw.lines(surf, (255, 225, 70), False, [(19, 13), (23, 15), (26, 16), (23, 17)], 1)
    return surf


def _create_p26_arcane_mine():
    surf = pygame.Surface((32, 32), pygame.SRCALPHA)
    # 4 symmetrical prongs radiating from center (top, right, bottom, left)
    for px, py in [(16, 3), (29, 16), (16, 29), (3, 16)]:
        pygame.draw.line(surf, (28, 20, 55), (16, 16), (px, py), 4)
        pygame.draw.line(surf, (85, 45, 135), (16, 16), (px, py), 2)
        surf.set_at((px, py), (150, 90, 210, 255))
    # Central diamond mine core
    d_pts = [(16, 10), (22, 16), (16, 22), (10, 16)]
    pygame.draw.polygon(surf, (70, 200, 240), d_pts)
    pygame.draw.polygon(surf, (28, 20, 55), d_pts, 1)
    # Center spark
    pygame.draw.circle(surf, (240, 250, 255), (16, 16), 2)
    return surf


def _create_p27_frost_bomb():
    surf = pygame.Surface((32, 32), pygame.SRCALPHA)
    # 6 broad crystal perimeter spikes
    for i in range(6):
        ang = i * (math.pi / 3.0)
        sx = int(16 + math.cos(ang) * 13)
        sy = int(16 + math.sin(ang) * 13)
        p1 = (int(16 + math.cos(ang - 0.3) * 7), int(16 + math.sin(ang - 0.3) * 7))
        p2 = (int(16 + math.cos(ang + 0.3) * 7), int(16 + math.sin(ang + 0.3) * 7))
        pygame.draw.polygon(surf, (70, 175, 225), [(sx, sy), p1, p2])
        pygame.draw.polygon(surf, (22, 45, 85), [(sx, sy), p1, p2], 1)
    # Rounded icy core
    pygame.draw.circle(surf, (22, 45, 85), (16, 16), 7)
    pygame.draw.circle(surf, (130, 210, 250), (16, 16), 6)
    pygame.draw.circle(surf, (195, 245, 255), (16, 16), 4)
    # White crest
    surf.set_at((15, 15), (255, 255, 255, 255))
    surf.set_at((16, 15), (255, 255, 255, 255))
    return surf


def _create_p28_acid_glob():
    surf = pygame.Surface((32, 32), pygame.SRCALPHA)
    # Sharp, pointed asymmetrical corrosive glob
    glob_pts = [(9, 12), (17, 8), (28, 14), (22, 20), (14, 23), (8, 18)]
    pygame.draw.polygon(surf, (120, 185, 30), glob_pts)
    pygame.draw.polygon(surf, (35, 50, 15), glob_pts, 1)
    # Neon lime highlights
    pygame.draw.polygon(surf, (175, 235, 45), [(12, 11), (18, 10), (25, 14), (18, 17), (12, 15)])
    # Corrosive bubbles
    for bx, by in [(15, 13), (20, 17), (11, 19)]:
        pygame.draw.circle(surf, (35, 50, 15), (bx, by), 3)
        pygame.draw.circle(surf, (235, 255, 140), (bx, by), 2)
        surf.set_at((bx - 1, by - 1), (255, 255, 220, 255))
    return surf


def _create_p29_bolo_throw():
    surf = pygame.Surface((32, 32), pygame.SRCALPHA)
    # Short dark carved wood handle x=4..12, y=17..20
    for x in range(4, 13):
        surf.set_at((x, 17), (35, 36, 42, 255))
        surf.set_at((x, 18), (80, 50, 28, 255))
        surf.set_at((x, 19), (60, 38, 20, 255))
        surf.set_at((x, 20), (35, 36, 42, 255))
    # Brass bolster collar at x=11..13
    pygame.draw.rect(surf, (185, 145, 55), (11, 16, 3, 5))
    # Broad slightly curved bolo steel blade x=13..28, y=9..21
    blade_pts = [(13, 16), (17, 11), (25, 10), (28, 13), (25, 19), (19, 21), (13, 19)]
    pygame.draw.polygon(surf, (150, 160, 175), blade_pts)
    pygame.draw.polygon(surf, (35, 36, 42), blade_pts, 1)
    # Cutting edge bevel & spine
    pygame.draw.lines(surf, (225, 235, 245), False, [(14, 18), (19, 20), (25, 18), (28, 13)], 1)
    pygame.draw.lines(surf, (95, 105, 118), False, [(14, 15), (17, 12), (25, 11)], 1)
    return surf


def _create_p30_araw_sigil():
    surf = pygame.Surface((32, 32), pygame.SRCALPHA)
    # 8 short angular solar rays extending to radius 12
    for i in range(8):
        ang = i * (math.pi / 4.0)
        rx = int(16 + math.cos(ang) * 12)
        ry = int(16 + math.sin(ang) * 12)
        p1 = (int(16 + math.cos(ang - 0.2) * 6), int(16 + math.sin(ang - 0.2) * 6))
        p2 = (int(16 + math.cos(ang + 0.2) * 6), int(16 + math.sin(ang + 0.2) * 6))
        pygame.draw.polygon(surf, (235, 175, 30), [(rx, ry), p1, p2])
        pygame.draw.polygon(surf, (115, 65, 15), [(rx, ry), p1, p2], 1)
        surf.set_at((rx, ry), (255, 210, 70, 255))
    # Central golden sun disk
    pygame.draw.circle(surf, (115, 65, 15), (16, 16), 6)
    pygame.draw.circle(surf, (255, 190, 40), (16, 16), 5)
    pygame.draw.circle(surf, (255, 255, 230), (16, 16), 2)
    return surf


def _create_p31_anting_anting_charm():
    surf = pygame.Surface((32, 32), pygame.SRCALPHA)
    # Hanging loop cord ring at (16, 6)
    pygame.draw.circle(surf, (50, 38, 22), (16, 6), 3)
    pygame.draw.circle(surf, (75, 50, 30), (16, 6), 2)
    surf.set_at((16, 6), (0, 0, 0, 0))
    # Carved brass amulet pendant body
    pendant_pts = [(10, 9), (22, 9), (24, 18), (16, 26), (8, 18)]
    pygame.draw.polygon(surf, (170, 135, 60), pendant_pts)
    pygame.draw.polygon(surf, (50, 38, 22), pendant_pts, 1)
    # Patina shading
    pygame.draw.polygon(surf, (110, 85, 35), [(9, 18), (16, 25), (16, 18)])
    # Central geometric mark in amber inlay
    pygame.draw.polygon(surf, (220, 160, 45), [(16, 12), (19, 16), (16, 20), (13, 16)])
    surf.set_at((16, 16), (255, 225, 120, 255))
    return surf


def _create_p32_diwa_wisp():
    surf = pygame.Surface((32, 32), pygame.SRCALPHA)
    # Flowing comma-shaped spirit tail sweeping down-left to (6, 23)
    tail_pts = [(20, 14), (18, 19), (13, 23), (6, 23), (11, 18), (15, 15)]
    pygame.draw.polygon(surf, (65, 180, 175), tail_pts)
    pygame.draw.polygon(surf, (20, 70, 75), tail_pts, 1)
    # Spirit head aura
    pygame.draw.circle(surf, (20, 70, 75), (20, 14), 7)
    pygame.draw.circle(surf, (140, 230, 215), (20, 14), 6)
    pygame.draw.circle(surf, (230, 255, 250), (20, 14), 4)
    surf.set_at((20, 14), (255, 255, 255, 255))
    return surf


def _create_p33_sumpa_spear():
    surf = pygame.Surface((32, 32), pygame.SRCALPHA)
    # Dark spectral obsidian shaft x=4..18, y=15..17
    for x in range(4, 19):
        surf.set_at((x, 14), (20, 10, 28, 255))
        surf.set_at((x, 15), (45, 30, 55, 255))
        surf.set_at((x, 16), (32, 20, 40, 255))
        surf.set_at((x, 17), (20, 10, 28, 255))
    # Jagged cursed spearhead x=18..29 with angular barbs
    head_pts = [(18, 10), (23, 13), (29, 16), (23, 19), (18, 22), (20, 16)]
    pygame.draw.polygon(surf, (110, 35, 150), head_pts)
    pygame.draw.polygon(surf, (20, 10, 28), head_pts, 1)
    # Muted magenta energy barbs & pale tip
    pygame.draw.line(surf, (195, 65, 175), (19, 12), (26, 16), 1)
    pygame.draw.line(surf, (195, 65, 175), (19, 20), (26, 16), 1)
    surf.set_at((29, 16), (240, 195, 255, 255))
    return surf


def _create_p34_ancestral_spirit_orb():
    surf = pygame.Surface((32, 32), pygame.SRCALPHA)
    # Concentric layered rings centered at (16, 16), radius 11
    pygame.draw.circle(surf, (50, 38, 28), (16, 16), 11)
    pygame.draw.circle(surf, (45, 140, 135), (16, 16), 10)
    pygame.draw.circle(surf, (195, 160, 60), (16, 16), 8)
    pygame.draw.circle(surf, (245, 235, 205), (16, 16), 5)
    # Abstract center spiral mark
    pygame.draw.arc(surf, (195, 160, 60), (13, 13, 6, 6), 0.5, 4.5, 1)
    surf.set_at((16, 16), (255, 250, 230, 255))
    return surf


def _create_p35_kampilan_wave():
    surf = pygame.Surface((32, 32), pygame.SRCALPHA)
    # Wide sweeping energy slash wave shaped by a Kampilan blade silhouette
    wave_pts = [(8, 5), (18, 8), (28, 12), (26, 20), (18, 24), (8, 27), (14, 18), (18, 14), (12, 10)]
    pygame.draw.polygon(surf, (60, 120, 180), wave_pts)
    pygame.draw.polygon(surf, (18, 32, 60), wave_pts, 1)
    # Pale cyan inner wave body
    inner_pts = [(10, 8), (18, 10), (26, 13), (24, 18), (17, 21), (10, 24), (14, 16)]
    pygame.draw.polygon(surf, (130, 215, 245), inner_pts)
    # Silver-white razor cutting crest
    pygame.draw.lines(surf, (240, 250, 255), False, [(9, 7), (18, 9), (27, 13), (25, 19)], 1)
    return surf


def _create_p36_monster_spit():
    surf = pygame.Surface((32, 32), pygame.SRCALPHA)
    # Organic lobed creature spit projectile pointing right
    spit_pts = [(9, 13), (15, 9), (21, 10), (27, 16), (22, 21), (13, 22), (7, 17)]
    pygame.draw.polygon(surf, (80, 115, 45), spit_pts)
    pygame.draw.polygon(surf, (40, 48, 20), spit_pts, 1)
    # Secondary ochre lobe
    pygame.draw.circle(surf, (150, 130, 50), (13, 19), 4)
    # Yellow-green highlight
    pygame.draw.circle(surf, (225, 235, 130), (17, 14), 4)
    # Glossy white shine
    surf.set_at((18, 13), (250, 255, 210, 255))
    return surf


def _create_p37_curse_bolt():
    surf = pygame.Surface((32, 32), pygame.SRCALPHA)
    # 3 broken hostile prongs pointing right
    prong_pts = [(6, 16), (14, 12), (22, 9), (18, 14), (28, 15), (18, 17), (21, 23), (14, 20)]
    pygame.draw.polygon(surf, (120, 25, 65), prong_pts)
    pygame.draw.polygon(surf, (22, 10, 25), prong_pts, 1)
    # Rich magenta inner energy field
    pygame.draw.circle(surf, (190, 40, 120), (16, 16), 5)
    # Hostile electric violet core
    pygame.draw.circle(surf, (215, 100, 255), (17, 15), 3)
    surf.set_at((17, 15), (255, 230, 255, 255))
    return surf


def _create_p38_boss_core():
    surf = pygame.Surface((32, 32), pygame.SRCALPHA)
    # 6 hexagonal armored crimson plates radiating from center
    for i in range(6):
        ang = i * (math.pi / 3.0)
        px = int(16 + math.cos(ang) * 12)
        py = int(16 + math.sin(ang) * 12)
        p1 = (int(16 + math.cos(ang - 0.3) * 7), int(16 + math.sin(ang - 0.3) * 7))
        p2 = (int(16 + math.cos(ang + 0.3) * 7), int(16 + math.sin(ang + 0.3) * 7))
        pygame.draw.polygon(surf, (160, 30, 45), [(px, py), p1, p2])
        pygame.draw.polygon(surf, (30, 20, 25), [(px, py), p1, p2], 1)
        surf.set_at((px, py), (220, 80, 95, 255))
    # Central crystal eye mount in gold
    pygame.draw.circle(surf, (205, 160, 45), (16, 16), 6)
    # Burning violet crystal eye
    pygame.draw.circle(surf, (190, 60, 230), (16, 16), 4)
    # Pupil core
    surf.set_at((16, 16), (255, 240, 255, 255))
    return surf


def _create_p39_tracking_shards():
    surf = pygame.Surface((32, 32), pygame.SRCALPHA)
    # Cluster of 4 sharp directional energy splinters flying forward
    shard_defs = [
        ((21, 14), [(16, 13), (25, 14), (16, 15)]),
        ((14, 8), [(9, 7), (18, 8), (9, 9)]),
        ((15, 22), [(10, 21), (19, 22), (10, 23)]),
        ((8, 15), [(3, 14), (12, 15), (3, 16)]),
    ]
    for center, pts in shard_defs:
        pygame.draw.polygon(surf, (125, 60, 195), pts)
        pygame.draw.polygon(surf, (20, 25, 55), pts, 1)
        pygame.draw.line(surf, (75, 215, 245), pts[0], (pts[1][0] - 1, pts[1][1]), 1)
        surf.set_at(pts[1], (245, 255, 255, 255))
    return surf


def _create_p40_abyssal_seed():
    surf = pygame.Surface((32, 32), pygame.SRCALPHA)
    # Ancient teardrop/seed-shaped projectile pointing right
    seed_pts = [(8, 16), (11, 10), (18, 11), (28, 16), (18, 21), (11, 22)]
    pygame.draw.polygon(surf, (24, 45, 58), seed_pts)
    pygame.draw.polygon(surf, (10, 18, 22), seed_pts, 1)
    # Inner layered shell ridge
    inner_pts = [(10, 16), (13, 12), (17, 13), (25, 16), (17, 19), (13, 20)]
    pygame.draw.polygon(surf, (45, 30, 60), inner_pts)
    # Shell ridge highlight
    pygame.draw.lines(surf, (85, 95, 130), False, [(11, 11), (18, 12), (26, 16)], 1)
    # Ancient glowing pale cyan fissure
    pygame.draw.line(surf, (100, 240, 255), (13, 16), (24, 16), 2)
    pygame.draw.line(surf, (235, 255, 255), (15, 16), (22, 16), 1)
    return surf


PROJECTILE_BUILDERS = {
    "p01_iron_arrow": _create_p01_iron_arrow,
    "p02_heavy_bolt": _create_p02_heavy_bolt,
    "p03_throwing_knife": _create_p03_throwing_knife,
    "p04_spinning_shuriken": _create_p04_spinning_shuriken,
    "p05_returning_throwing_axe": _create_p05_returning_throwing_axe,
    "p06_fireball": _create_p06_fireball,
    "p07_ice_shard": _create_p07_ice_shard,
    "p08_lightning_bolt": _create_p08_lightning_bolt,
    "p09_shadow_orb": _create_p09_shadow_orb,
    "p10_poison_glob": _create_p10_poison_glob,
    "p11_holy_bolt": _create_p11_holy_bolt,
    "p12_earth_shard": _create_p12_earth_shard,
    "p13_water_orb": _create_p13_water_orb,
    "p14_magma_core": _create_p14_magma_core,
    "p15_wind_crescent": _create_p15_wind_crescent,
    "p16_arcane_orb": _create_p16_arcane_orb,
    "p17_arcane_lance": _create_p17_arcane_lance,
    "p18_energy_disc": _create_p18_energy_disc,
    "p19_homing_star": _create_p19_homing_star,
    "p20_void_sphere": _create_p20_void_sphere,
    "p21_spectral_skull": _create_p21_spectral_skull,
    "p22_crystal_bolt": _create_p22_crystal_bolt,
    "p23_fuse_bomb": _create_p23_fuse_bomb,
    "p24_spiked_blast_core": _create_p24_spiked_blast_core,
    "p25_meteor_fragment": _create_p25_meteor_fragment,
    "p26_arcane_mine": _create_p26_arcane_mine,
    "p27_frost_bomb": _create_p27_frost_bomb,
    "p28_acid_glob": _create_p28_acid_glob,
    "p29_bolo_throw": _create_p29_bolo_throw,
    "p30_araw_sigil": _create_p30_araw_sigil,
    "p31_anting_anting_charm": _create_p31_anting_anting_charm,
    "p32_diwa_wisp": _create_p32_diwa_wisp,
    "p33_sumpa_spear": _create_p33_sumpa_spear,
    "p34_ancestral_spirit_orb": _create_p34_ancestral_spirit_orb,
    "p35_kampilan_wave": _create_p35_kampilan_wave,
    "p36_monster_spit": _create_p36_monster_spit,
    "p37_curse_bolt": _create_p37_curse_bolt,
    "p38_boss_core": _create_p38_boss_core,
    "p39_tracking_shards": _create_p39_tracking_shards,
    "p40_abyssal_seed": _create_p40_abyssal_seed,
}


class ProjectileRegistry(dict):
    """
    Specialized dictionary for Potaria projectiles supporting canonical keys
    (e.g., 'p01_iron_arrow') while resolving aliases ('iron_arrow', 'P01', 'p01')
    transparently during lookups without multiplying keys in iterations or disk exports.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._aliases = {}

    def register_alias(self, alias, canonical_key):
        self._aliases[alias] = canonical_key

    def get(self, key, default=None):
        if super().__contains__(key):
            return super().get(key, default)
        if key in self._aliases:
            return super().get(self._aliases[key], default)
        return default

    def __getitem__(self, key):
        if super().__contains__(key):
            return super().__getitem__(key)
        if key in self._aliases:
            return super().__getitem__(self._aliases[key])
        return super().__getitem__(key)

    def __contains__(self, key):
        return super().__contains__(key) or key in self._aliases


def generate_library_projectiles():
    """Generates all 40 projectiles from the library specifications."""
    sprites = {}
    for key, builder in PROJECTILE_BUILDERS.items():
        sprites[key] = builder()
    return sprites

