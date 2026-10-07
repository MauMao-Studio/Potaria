"""
Potaria - Procedural World Generator
Generates randomized rolling terrain with surface trees, caves, ore veins,
indestructible bedrock map boundaries, and the subterranean Nether Dungeon of Lord Malus!
Developer: Kurados
"""

import random
from src.constants import (
    WORLD_WIDTH, WORLD_HEIGHT, SURFACE_LEVEL, UNDERGROUND_LEVEL,
    CAVERN_LEVEL, DUNGEON_LEVEL, TILE_AIR, TILE_DIRT, TILE_GRASS,
    TILE_STONE, TILE_WOOD, TILE_LEAVES, TILE_WOOD_TRUNK, TILE_COPPER_ORE,
    TILE_IRON_ORE, TILE_GOLD_ORE, TILE_TORCH, TILE_BEDROCK,
    TILE_DUNGEON_BRICK, TILE_DUNGEON_ALTAR, WALL_AIR, WALL_DIRT,
    WALL_STONE, WALL_DUNGEON
)
from src.world.noise import PerlinNoise

def generate_terrain(width=WORLD_WIDTH, height=WORLD_HEIGHT, seed=None):
    """
    Generates a full 2D tile map and background wall map with a random seed.
    Returns:
        tiles: 2D list [x][y]
        walls: 2D list [x][y]
        spawn_pos: (px, py)
        dungeon_pos: (dungeon_center_px_x, dungeon_center_px_y)
        seed: used seed
    """
    if seed is None:
        seed = random.randint(100000, 99999999)

    print(f"[WorldGen] Generating world with Random Seed: {seed}")
    noise_surface = PerlinNoise(seed)
    noise_caves = PerlinNoise(seed + 101)
    noise_ores = PerlinNoise(seed + 202)
    rng = random.Random(seed)

    tiles = [[TILE_AIR for _ in range(height)] for _ in range(width)]
    walls = [[WALL_AIR for _ in range(height)] for _ in range(width)]

    # 1. Surface Heights (Rolling hills)
    surface_heights = [0] * width
    for x in range(width):
        n = noise_surface.fractal1d(x * 0.018, octaves=3, persistence=0.5)
        h = int(SURFACE_LEVEL + n * 20)
        surface_heights[x] = max(35, min(height - 90, h))

    # 2. Base Strata (Grass, Dirt, Stone)
    for x in range(width):
        surf = surface_heights[x]
        for y in range(height):
            if y < surf:
                tiles[x][y] = TILE_AIR
                walls[x][y] = WALL_AIR
            elif y == surf:
                tiles[x][y] = TILE_GRASS
                walls[x][y] = WALL_AIR
            elif y < surf + 6:
                tiles[x][y] = TILE_DIRT
                walls[x][y] = WALL_DIRT
            elif y < UNDERGROUND_LEVEL:
                dirt_prob = (UNDERGROUND_LEVEL - y) / (UNDERGROUND_LEVEL - surf)
                if rng.random() < dirt_prob:
                    tiles[x][y] = TILE_DIRT
                    walls[x][y] = WALL_DIRT
                else:
                    tiles[x][y] = TILE_STONE
                    walls[x][y] = WALL_STONE
            else:
                tiles[x][y] = TILE_STONE
                walls[x][y] = WALL_STONE

    # 3. Caves & Caverns (2D Perlin Worms)
    for x in range(3, width - 3):
        surf = surface_heights[x]
        for y in range(surf + 4, height - 25):
            cave_val = noise_caves.fractal2d(x * 0.045, y * 0.045, octaves=3)
            threshold = 0.28 if y < UNDERGROUND_LEVEL else 0.22
            if abs(cave_val) < 0.12 or cave_val > threshold:
                tiles[x][y] = TILE_AIR
                walls[x][y] = WALL_DIRT if y < UNDERGROUND_LEVEL else WALL_STONE

    # 4. Ore Veins (Copper, Iron, Gold)
    for x in range(4, width - 4):
        surf = surface_heights[x]
        for y in range(surf + 3, height - 30):
            if tiles[x][y] in (TILE_STONE, TILE_DIRT):
                ore_val = noise_ores.fractal2d(x * 0.12, y * 0.12, octaves=2)
                if ore_val > 0.42 and y < CAVERN_LEVEL:
                    tiles[x][y] = TILE_COPPER_ORE
                elif ore_val < -0.44 and surf + 15 < y < height - 30:
                    tiles[x][y] = TILE_IRON_ORE
                elif ore_val > 0.52 and y > CAVERN_LEVEL - 20:
                    tiles[x][y] = TILE_GOLD_ORE

    # 5. Surface Trees
    tree_spacing = 0
    for x in range(6, width - 7):
        tree_spacing += 1
        surf = surface_heights[x]
        if tiles[x][surf] == TILE_GRASS and tree_spacing > 4:
            if rng.random() < 0.38:
                tree_spacing = 0
                trunk_h = rng.randint(5, 9)
                can_grow = True
                for ty in range(surf - trunk_h - 4, surf):
                    if tiles[x][ty] != TILE_AIR:
                        can_grow = False
                        break
                if can_grow:
                    crown_cy = surf - trunk_h
                    for ty in range(crown_cy, surf):
                        tiles[x][ty] = TILE_WOOD_TRUNK
                    for lx in range(x - 3, x + 4):
                        for ly in range(crown_cy - 3, crown_cy + 2):
                            if lx == x and ly >= crown_cy:
                                continue
                            if 0 <= lx < width and 0 <= ly < height:
                                dx = (lx - x) / 2.9
                                dy = (ly - (crown_cy - 0.5)) / 2.3
                                if dx * dx + dy * dy <= 1.05:
                                    tiles[lx][ly] = TILE_LEAVES

    # 6. NETHER DUNGEON OF LORD MALUS (Deep Underworld Chamber)
    # Dimensions: 50 tiles wide x 22 tiles high
    dung_cx = width // 2
    dung_cy = DUNGEON_LEVEL + 5
    dw = 44
    dh = 18
    dx1, dx2 = dung_cx - dw // 2, dung_cx + dw // 2
    dy1, dy2 = dung_cy - dh // 2, dung_cy + dh // 2

    # Carve and build Dungeon
    for x in range(dx1, dx2 + 1):
        for y in range(dy1, dy2 + 1):
            walls[x][y] = WALL_DUNGEON
            if x in (dx1, dx2) or y in (dy1, dy2):
                tiles[x][y] = TILE_DUNGEON_BRICK  # Solid outer fortress wall
            else:
                tiles[x][y] = TILE_AIR  # Hollow chamber inside

    # Place Dungeon Boss Altar in center floor
    altar_x = dung_cx
    altar_y = dy2 - 1
    tiles[altar_x][altar_y] = TILE_DUNGEON_ALTAR
    tiles[altar_x - 1][altar_y] = TILE_DUNGEON_BRICK
    tiles[altar_x + 1][altar_y] = TILE_DUNGEON_BRICK

    # Dungeon Torches
    tiles[dx1 + 4][dy1 + 4] = TILE_TORCH
    tiles[dx2 - 4][dy1 + 4] = TILE_TORCH
    tiles[dung_cx - 8][dy2 - 2] = TILE_TORCH
    tiles[dung_cx + 8][dy2 - 2] = TILE_TORCH

    dungeon_spawn = (dung_cx * 32, (dy2 - 4) * 32)

    # 7. IMPENETRABLE BEDROCK BARRIERS (Left, Right, Bottom)
    # Guarantees the player can NEVER fall off the edge of the world!
    for y in range(height):
        for x in (0, 1, 2, width - 3, width - 2, width - 1):
            tiles[x][y] = TILE_BEDROCK

    for x in range(width):
        for y in (height - 3, height - 2, height - 1):
            tiles[x][y] = TILE_BEDROCK

    # 8. Find Surface Player Spawn
    spawn_tx = width // 2
    spawn_ty = surface_heights[spawn_tx] - 3
    spawn_px = (spawn_tx * 32, spawn_ty * 32)

    return tiles, walls, spawn_px, dungeon_spawn, seed
