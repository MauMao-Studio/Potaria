"""
Potaria - Infinite Chunk-Based Open World Manager
Streams procedural chunks seamlessly from -infinity to +infinity.
No left or right boundaries! Pure open-world exploration.
Developer: Kurados
"""

import math
import random
from src.constants import (
    SURFACE_LEVEL, UNDERGROUND_LEVEL, CAVERN_LEVEL, DUNGEON_LEVEL,
    TILE_AIR, TILE_DIRT, TILE_GRASS, TILE_STONE, TILE_WOOD,
    TILE_LEAVES, TILE_WOOD_TRUNK, TILE_COPPER_ORE, TILE_IRON_ORE,
    TILE_GOLD_ORE, TILE_TORCH, TILE_BEDROCK, TILE_DUNGEON_BRICK,
    TILE_DUNGEON_ALTAR, TILE_SAND, TILE_SANDSTONE, TILE_CACTUS,
    TILE_SNOW, TILE_ICE, TILE_CORRUPT_GRASS, TILE_BLIGHT_GRASS, TILE_EBONSTONE,
    TILE_MUSHROOM_GRASS, TILE_MUSHROOM_STEM, TILE_MUSHROOM_CAP, TILE_CHEST, TILE_WATER,
    WALL_AIR, WALL_DIRT, WALL_STONE, WALL_DUNGEON,
    WALL_SANDSTONE, WALL_ICE, WALL_EBONSTONE, WALL_MUSHROOM,
    BIOME_FOREST, BIOME_DESERT, BIOME_SNOW, BIOME_CORRUPTION, BIOME_BLIGHT,
    BIOME_MUSHROOM, BIOME_DUNGEON, BIOME_CAVERN
)
from src.world.noise import PerlinNoise

CHUNK_WIDTH = 16
CHUNK_HEIGHT = 240

class Chunk:
    def __init__(self, chunk_x, seed, noise_surface, noise_caves, noise_ores, noise_biome):
        self.chunk_x = chunk_x
        self.width = CHUNK_WIDTH
        self.height = CHUNK_HEIGHT
        self.tiles = [[TILE_AIR for _ in range(self.height)] for _ in range(self.width)]
        self.walls = [[WALL_AIR for _ in range(self.height)] for _ in range(self.width)]
        self.modified = False

        self._generate(seed, noise_surface, noise_caves, noise_ores, noise_biome)

    def _generate(self, seed, noise_surface, noise_caves, noise_ores, noise_biome):
        rng = random.Random(seed ^ (self.chunk_x * 99991))
        
        # 1. Surface line and Biome for each column
        surface_heights = [0] * self.width
        col_biomes = [""] * self.width
        for lx in range(self.width):
            gx = self.chunk_x * self.width + lx
            n = noise_surface.fractal1d(gx * 0.018, octaves=3, persistence=0.5)
            h = int(SURFACE_LEVEL + n * 20)
            surface_heights[lx] = max(35, min(self.height - 90, h))

            b_val = noise_biome.fractal1d(gx * 0.0035, octaves=2)
            if b_val < -0.18:
                col_biomes[lx] = BIOME_SNOW
            elif b_val < 0.06:
                col_biomes[lx] = BIOME_FOREST
            elif b_val < 0.22:
                col_biomes[lx] = BIOME_DESERT
            else:
                col_biomes[lx] = BIOME_CORRUPTION
        self.surface_heights = surface_heights
        self.col_biomes = col_biomes

        # 2. Base Strata by Biome
        for lx in range(self.width):
            gx = self.chunk_x * self.width + lx
            surf = surface_heights[lx]
            b = col_biomes[lx]

            for y in range(self.height):
                if y < surf:
                    self.tiles[lx][y] = TILE_AIR
                    self.walls[lx][y] = WALL_AIR
                elif y == surf:
                    if b == BIOME_DESERT:
                        self.tiles[lx][y] = TILE_SAND
                    elif b == BIOME_SNOW:
                        self.tiles[lx][y] = TILE_SNOW
                    elif b == BIOME_CORRUPTION:
                        self.tiles[lx][y] = TILE_CORRUPT_GRASS
                    else:
                        self.tiles[lx][y] = TILE_GRASS
                    self.walls[lx][y] = WALL_AIR

                elif y < surf + 6:
                    if b == BIOME_DESERT:
                        self.tiles[lx][y] = TILE_SAND
                        self.walls[lx][y] = WALL_SANDSTONE
                    elif b == BIOME_SNOW:
                        self.tiles[lx][y] = TILE_SNOW
                        self.walls[lx][y] = WALL_ICE
                    elif b == BIOME_CORRUPTION:
                        self.tiles[lx][y] = TILE_DIRT
                        self.walls[lx][y] = WALL_EBONSTONE
                    else:
                        self.tiles[lx][y] = TILE_DIRT
                        self.walls[lx][y] = WALL_DIRT

                elif y < UNDERGROUND_LEVEL:
                    if b == BIOME_DESERT:
                        self.tiles[lx][y] = TILE_SANDSTONE
                        self.walls[lx][y] = WALL_SANDSTONE
                    elif b == BIOME_SNOW:
                        self.tiles[lx][y] = TILE_ICE if rng.random() < 0.65 else TILE_STONE
                        self.walls[lx][y] = WALL_ICE
                    elif b == BIOME_CORRUPTION:
                        self.tiles[lx][y] = TILE_EBONSTONE if rng.random() < 0.75 else TILE_STONE
                        self.walls[lx][y] = WALL_EBONSTONE
                    else:
                        dirt_prob = (UNDERGROUND_LEVEL - y) / max(1, (UNDERGROUND_LEVEL - surf))
                        if rng.random() < dirt_prob:
                            self.tiles[lx][y] = TILE_DIRT
                            self.walls[lx][y] = WALL_DIRT
                        else:
                            self.tiles[lx][y] = TILE_STONE
                            self.walls[lx][y] = WALL_STONE
                else:
                    # Cavern depths: check for Glowing Mushroom biome pocket
                    m_val = noise_ores.fractal2d(gx * 0.022, y * 0.022, octaves=2)
                    if y >= CAVERN_LEVEL - 12 and m_val > 0.38:
                        self.tiles[lx][y] = TILE_STONE
                        self.walls[lx][y] = WALL_MUSHROOM
                    else:
                        self.tiles[lx][y] = TILE_STONE
                        self.walls[lx][y] = WALL_STONE

        # 3. Caves & Caverns (2D Perlin Worms across chunks)
        for lx in range(self.width):
            gx = self.chunk_x * self.width + lx
            surf = surface_heights[lx]
            b = col_biomes[lx]

            for y in range(surf + 4, self.height - 25):
                # Dungeon Chamber protection zone at chunk 0..2 deep underground
                if -2 <= self.chunk_x <= 2 and DUNGEON_LEVEL - 5 <= y <= DUNGEON_LEVEL + 20:
                    continue

                cave_val = noise_caves.fractal2d(gx * 0.045, y * 0.045, octaves=3)
                threshold = 0.28 if y < UNDERGROUND_LEVEL else 0.22
                if abs(cave_val) < 0.12 or cave_val > threshold:
                    self.tiles[lx][y] = TILE_AIR
                    if y < UNDERGROUND_LEVEL:
                        if b == BIOME_DESERT:
                            self.walls[lx][y] = WALL_SANDSTONE
                        elif b == BIOME_SNOW:
                            self.walls[lx][y] = WALL_ICE
                        elif b == BIOME_CORRUPTION:
                            self.walls[lx][y] = WALL_EBONSTONE
                        else:
                            self.walls[lx][y] = WALL_DIRT
                    else:
                        m_val = noise_ores.fractal2d(gx * 0.022, y * 0.022, octaves=2)
                        if y >= CAVERN_LEVEL - 12 and m_val > 0.38:
                            self.walls[lx][y] = WALL_MUSHROOM
                        else:
                            self.walls[lx][y] = WALL_STONE

        # 3b. Mushroom Grass conversion in Cavern Mushroom Pockets
        for lx in range(self.width):
            for y in range(CAVERN_LEVEL - 12, self.height - 25):
                if self.tiles[lx][y] == TILE_STONE and self.walls[lx][y] == WALL_MUSHROOM:
                    if y > 0 and self.tiles[lx][y - 1] == TILE_AIR:
                        self.tiles[lx][y] = TILE_MUSHROOM_GRASS

        # 4. Ore Veins (Copper, Iron, Gold)
        for lx in range(self.width):
            gx = self.chunk_x * self.width + lx
            surf = surface_heights[lx]
            for y in range(surf + 3, self.height - 30):
                if self.tiles[lx][y] in (TILE_STONE, TILE_DIRT, TILE_SANDSTONE, TILE_EBONSTONE, TILE_ICE):
                    ore_val = noise_ores.fractal2d(gx * 0.12, y * 0.12, octaves=2)
                    if ore_val > 0.42 and y < CAVERN_LEVEL:
                        self.tiles[lx][y] = TILE_COPPER_ORE
                    elif ore_val < -0.44 and surf + 15 < y < self.height - 30:
                        self.tiles[lx][y] = TILE_IRON_ORE
                    elif ore_val > 0.52 and y > CAVERN_LEVEL - 20:
                        self.tiles[lx][y] = TILE_GOLD_ORE

        # 4b. Natural Liquid Water (Surface Ponds & Subterranean Cavern Pools)
        # 4b. Natural Liquid Water (Flat Surface Ponds & Subterranean Cavern Pools)
        if abs(self.chunk_x) % 4 == 1:
            pond_start = rng.randint(2, 5)
            pond_w = rng.randint(5, 7)
            pond_cols = [px for px in range(pond_start, min(self.width - 1, pond_start + pond_w))]
            if pond_cols:
                # Flat water level across the entire pond (no stepped/adjacent jagged mismatches!)
                flat_water_y = max(surface_heights[px] for px in pond_cols)
                for px in pond_cols:
                    # Carve open air above the flat water level so water is not under stepped soil
                    for wy in range(surface_heights[px], flat_water_y):
                        self.tiles[px][wy] = TILE_AIR
                    # Fill water downward from the flat water level
                    for wy in range(flat_water_y, min(self.height, flat_water_y + 3)):
                        if self.tiles[px][wy] not in (TILE_BEDROCK, TILE_DUNGEON_BRICK):
                            self.tiles[px][wy] = TILE_WATER

        # Subterranean cavern pools (flat 5-tile contiguous basins, no stepped vertical pillars)
        for lx in range(2, self.width - 6, 6):
            if rng.random() < 0.15:
                for y in range(UNDERGROUND_LEVEL + 10, CAVERN_LEVEL + 20):
                    if all(self.tiles[lx + dx][y] == TILE_AIR and self.tiles[lx + dx][y + 1] in (TILE_STONE, TILE_SANDSTONE, TILE_ICE) for dx in range(5)):
                        for dx in range(5):
                            self.tiles[lx + dx][y] = TILE_WATER
                        break

        # 5. Dynamic Surface Vegetation & Cute Terraria Trees
        for lx in range(1, self.width - 1):
            surf = surface_heights[lx]
            b = col_biomes[lx]
            
            # Forest: Cute Normal Oak Trees (Cohesive rounded lush canopy, upper wood filled with leaves)
            if b == BIOME_FOREST and self.tiles[lx][surf] == TILE_GRASS and (lx in (5, 11)):
                if rng.random() < 0.65:
                    trunk_h = rng.randint(5, 8)
                    can_grow = True
                    for ty in range(surf - trunk_h - 4, surf):
                        if 0 <= ty < self.height and self.tiles[lx][ty] != TILE_AIR:
                            can_grow = False
                            break
                    if can_grow:
                        crown_cy = surf - trunk_h
                        # Trunk rises up to meet the canopy; upper part of trunk is filled with leaves
                        for ty in range(crown_cy, surf):
                            self.tiles[lx][ty] = TILE_WOOD_TRUNK

                        # Normal, cute rounded oval canopy
                        for cx in range(lx - 3, lx + 4):
                            for cy in range(crown_cy - 3, crown_cy + 2):
                                if cx == lx and cy >= crown_cy:
                                    continue
                                if 0 <= cx < self.width and 0 <= cy < self.height:
                                    dx = (cx - lx) / 2.9
                                    dy = (cy - (crown_cy - 0.5)) / 2.3
                                    if dx * dx + dy * dy <= 1.05:
                                        self.tiles[cx][cy] = TILE_LEAVES

            # Desert: Cacti & Cute Terraria Palm Trees
            elif b == BIOME_DESERT and self.tiles[lx][surf] == TILE_SAND:
                if (lx in (3, 8, 13)) and rng.random() < 0.40:
                    c_h = rng.randint(3, 5)
                    for cy in range(surf - c_h, surf):
                        self.tiles[lx][cy] = TILE_CACTUS
                    if c_h >= 4:
                        arm_dir = rng.choice([-1, 1])
                        ax = lx + arm_dir
                        if 0 <= ax < self.width:
                            self.tiles[ax][surf - c_h + 1] = TILE_CACTUS
                            self.tiles[ax][surf - c_h] = TILE_CACTUS
                elif (lx in (5, 11)) and rng.random() < 0.50:
                    # Terraria Desert Palm Tree
                    palm_h = rng.randint(6, 9)
                    can_grow = True
                    for ty in range(surf - palm_h - 3, surf):
                        if 0 <= ty < self.height and self.tiles[lx][ty] != TILE_AIR:
                            can_grow = False
                            break
                    if can_grow:
                        crown_cy = surf - palm_h
                        for ty in range(crown_cy, surf):
                            self.tiles[lx][ty] = TILE_WOOD_TRUNK
                        # Palm fronds fountain canopy with upper wood covered in leaves
                        if crown_cy - 1 >= 0:
                            self.tiles[lx][crown_cy - 1] = TILE_LEAVES
                        for dx in (-3, -2, -1, 1, 2, 3):
                            drop = 1 if abs(dx) == 3 else (0 if abs(dx) == 2 else -1)
                            fx = lx + dx
                            fy = crown_cy + drop
                            if 0 <= fx < self.width and 0 <= fy < self.height:
                                self.tiles[fx][fy] = TILE_LEAVES
                            if abs(dx) <= 2 and 0 <= fx < self.width and 0 <= crown_cy < self.height:
                                self.tiles[fx][crown_cy] = TILE_LEAVES

            # Snow: Cute Frosted Pine Conifers (Tiered conifer, upper trunk filled with snow pine leaves)
            elif b == BIOME_SNOW and self.tiles[lx][surf] == TILE_SNOW and (lx in (5, 11)):
                if rng.random() < 0.60:
                    p_h = rng.randint(7, 10)
                    crown_cy = surf - p_h
                    for ty in range(crown_cy, surf):
                        self.tiles[lx][ty] = TILE_WOOD_TRUNK
                    pine_tiers = [
                        (-2, 1.0),
                        (-1, 1.6),
                        (0, 2.2),
                        (1, 2.8),
                        (2, 3.2),
                        (3, 2.6)
                    ]
                    for d_lvl, rad in pine_tiers:
                        leaf_y = crown_cy + d_lvl
                        if 0 <= leaf_y < self.height:
                            irad = int(rad)
                            for cx in range(lx - irad, lx + irad + 1):
                                if cx == lx and leaf_y >= crown_cy:
                                    continue
                                if 0 <= cx < self.width:
                                    if abs(cx - lx) <= rad:
                                        self.tiles[cx][leaf_y] = TILE_LEAVES

            # Corruption / The Blight: Cute Ebonwood Trees (Twisted trunks with dark purple canopies)
            elif b in (BIOME_CORRUPTION, BIOME_BLIGHT) and self.tiles[lx][surf] in (TILE_CORRUPT_GRASS, TILE_BLIGHT_GRASS) and (lx in (5, 11)):
                if rng.random() < 0.60:
                    b_h = rng.randint(5, 8)
                    can_grow = True
                    for ty in range(surf - b_h - 4, surf):
                        if 0 <= ty < self.height and self.tiles[lx][ty] != TILE_AIR:
                            can_grow = False
                            break
                    if can_grow:
                        crown_cy = surf - b_h
                        for ty in range(crown_cy, surf):
                            self.tiles[lx][ty] = TILE_WOOD_TRUNK
                        for cx in range(lx - 3, lx + 4):
                            for cy in range(crown_cy - 3, crown_cy + 2):
                                if cx == lx and cy >= crown_cy:
                                    continue
                                if 0 <= cx < self.width and 0 <= cy < self.height:
                                    dx = (cx - lx) / 2.9
                                    dy = (cy - (crown_cy - 0.5)) / 2.3
                                    if dx * dx + dy * dy <= 1.05:
                                        self.tiles[cx][cy] = TILE_LEAVES

        # 5b. Giant Glowing Mushrooms in Caverns
        for lx in range(2, self.width - 2):
            for y in range(CAVERN_LEVEL - 10, self.height - 25):
                if self.tiles[lx][y] == TILE_MUSHROOM_GRASS:
                    if all(self.tiles[lx][y - k] == TILE_AIR for k in range(1, 5)):
                        if rng.random() < 0.25:
                            stem_h = rng.randint(3, 4)
                            for sy in range(y - stem_h, y):
                                self.tiles[lx][sy] = TILE_MUSHROOM_STEM
                            cap_y = y - stem_h
                            for mx in (lx - 1, lx, lx + 1):
                                if 0 <= mx < self.width and 0 <= cap_y < self.height:
                                    self.tiles[mx][cap_y] = TILE_MUSHROOM_CAP

        # 5c. Underground Naturally Placed Treasure Chests
        if rng.random() < 0.45:
            chest_placed = False
            for y in range(UNDERGROUND_LEVEL + 5, self.height - 25):
                if chest_placed:
                    break
                for lx in range(2, self.width - 2):
                    if self.tiles[lx][y] in (TILE_STONE, TILE_SANDSTONE, TILE_ICE, TILE_EBONSTONE, TILE_MUSHROOM_GRASS):
                        if self.tiles[lx][y - 1] == TILE_AIR and self.tiles[lx][y - 2] == TILE_AIR:
                            self.tiles[lx][y - 1] = TILE_CHEST
                            chest_placed = True
                            break

        # 6. Nether Dungeon Chamber (Constructed at origin chunk -1 to 1 deep cavern)
        if -1 <= self.chunk_x <= 1:
            dung_cy = DUNGEON_LEVEL + 5
            dh = 18
            for lx in range(self.width):
                gx = self.chunk_x * self.width + lx
                if -20 <= gx <= 20:
                    for y in range(dung_cy - dh // 2, dung_cy + dh // 2 + 1):
                        self.walls[lx][y] = WALL_DUNGEON
                        if gx in (-20, 20) or y in (dung_cy - dh // 2, dung_cy + dh // 2):
                            self.tiles[lx][y] = TILE_DUNGEON_BRICK
                        else:
                            self.tiles[lx][y] = TILE_AIR
                    
                    if gx == 0 and dung_cy + dh // 2 - 1 < self.height:
                        self.tiles[lx][dung_cy + dh // 2 - 1] = TILE_DUNGEON_ALTAR
                    if abs(gx) in (1, 8, 16):
                        self.tiles[lx][dung_cy + dh // 2 - 2] = TILE_TORCH

        # 6b. Sun Altar Desert Arena (Ignis Colossus arena around gx=80 and pocket dimension gx=5000)
        if 4 <= self.chunk_x <= 6:
            arena_cy = DUNGEON_LEVEL - 5
            dh = 18
            for lx in range(self.width):
                gx = self.chunk_x * self.width + lx
                if 68 <= gx <= 96:
                    for y in range(arena_cy - dh // 2, arena_cy + dh // 2 + 1):
                        self.walls[lx][y] = WALL_SANDSTONE
                        if gx in (68, 96) or y in (arena_cy - dh // 2, arena_cy + dh // 2):
                            self.tiles[lx][y] = TILE_SANDSTONE
                        else:
                            self.tiles[lx][y] = TILE_AIR
                    if gx == 82 and arena_cy + dh // 2 - 2 < self.height:
                        self.tiles[lx][arena_cy + dh // 2 - 2] = TILE_TORCH

        if 310 <= self.chunk_x <= 314:
            arena_cy = 54
            dh = 18
            for lx in range(self.width):
                gx = self.chunk_x * self.width + lx
                if 4985 <= gx <= 5015:
                    for y in range(arena_cy - dh // 2, arena_cy + dh // 2 + 1):
                        self.walls[lx][y] = WALL_SANDSTONE
                        if gx in (4985, 5015) or y in (arena_cy - dh // 2, arena_cy + dh // 2):
                            self.tiles[lx][y] = TILE_SANDSTONE
                        else:
                            self.tiles[lx][y] = TILE_AIR
                    if gx in (4990, 5000, 5010) and arena_cy + dh // 2 - 2 < self.height:
                        self.tiles[lx][arena_cy + dh // 2 - 2] = TILE_TORCH

        # 6c. Glacial Permafrost Arena (Cryo-Spud arena around gx=-80 and pocket dimension gx=-5000)
        if -6 <= self.chunk_x <= -4:
            arena_cy = DUNGEON_LEVEL - 5
            dh = 18
            for lx in range(self.width):
                gx = self.chunk_x * self.width + lx
                if -96 <= gx <= -68:
                    for y in range(arena_cy - dh // 2, arena_cy + dh // 2 + 1):
                        self.walls[lx][y] = WALL_ICE
                        if gx in (-96, -68) or y in (arena_cy - dh // 2, arena_cy + dh // 2):
                            self.tiles[lx][y] = TILE_ICE
                        else:
                            self.tiles[lx][y] = TILE_AIR
                    if gx == -82 and arena_cy + dh // 2 - 2 < self.height:
                        self.tiles[lx][arena_cy + dh // 2 - 2] = TILE_TORCH

        if -315 <= self.chunk_x <= -311:
            arena_cy = 54
            dh = 18
            for lx in range(self.width):
                gx = self.chunk_x * self.width + lx
                if -5015 <= gx <= -4985:
                    for y in range(arena_cy - dh // 2, arena_cy + dh // 2 + 1):
                        self.walls[lx][y] = WALL_ICE
                        if gx in (-5015, -4985) or y in (arena_cy - dh // 2, arena_cy + dh // 2):
                            self.tiles[lx][y] = TILE_ICE
                        else:
                            self.tiles[lx][y] = TILE_AIR
                    if gx in (-5010, -5000, -4990) and arena_cy + dh // 2 - 2 < self.height:
                        self.tiles[lx][arena_cy + dh // 2 - 2] = TILE_TORCH

        # 6d. Blight Shadow Crypt Arena (Necro-Tuber arena around gx=130 and pocket dimension gx=8000)
        if 7 <= self.chunk_x <= 9:
            arena_cy = DUNGEON_LEVEL - 5
            dh = 18
            for lx in range(self.width):
                gx = self.chunk_x * self.width + lx
                if 116 <= gx <= 144:
                    for y in range(arena_cy - dh // 2, arena_cy + dh // 2 + 1):
                        self.walls[lx][y] = WALL_EBONSTONE
                        if gx in (116, 144) or y in (arena_cy - dh // 2, arena_cy + dh // 2):
                            self.tiles[lx][y] = TILE_EBONSTONE
                        else:
                            self.tiles[lx][y] = TILE_AIR
                    if gx == 130 and arena_cy + dh // 2 - 2 < self.height:
                        self.tiles[lx][arena_cy + dh // 2 - 2] = TILE_TORCH

        if 498 <= self.chunk_x <= 502:
            arena_cy = 54
            dh = 18
            for lx in range(self.width):
                gx = self.chunk_x * self.width + lx
                if 7985 <= gx <= 8015:
                    for y in range(arena_cy - dh // 2, arena_cy + dh // 2 + 1):
                        self.walls[lx][y] = WALL_EBONSTONE
                        if gx in (7985, 8015) or y in (arena_cy - dh // 2, arena_cy + dh // 2):
                            self.tiles[lx][y] = TILE_EBONSTONE
                        else:
                            self.tiles[lx][y] = TILE_AIR
                    if gx in (7990, 8000, 8010) and arena_cy + dh // 2 - 2 < self.height:
                        self.tiles[lx][arena_cy + dh // 2 - 2] = TILE_TORCH

        # 7. Bedrock floor ONLY (Bottom of the world: y >= height - 3)
        for lx in range(self.width):
            for y in range(self.height - 3, self.height):
                self.tiles[lx][y] = TILE_BEDROCK

class ChunkManager:
    def __init__(self, seed=None, world_type="infinite"):
        if seed is None:
            seed = random.randint(100000, 99999999)
        self.seed = seed
        self.world_type = world_type
        self.chunks = {}
        
        self.noise_surface = PerlinNoise(seed)
        self.noise_caves = PerlinNoise(seed + 101)
        self.noise_ores = PerlinNoise(seed + 202)
        self.noise_biome = PerlinNoise(seed + 303)

    def get_chunk(self, chunk_x):
        """Retrieves or procedurally generates the chunk at chunk_x."""
        if chunk_x not in self.chunks:
            self.chunks[chunk_x] = Chunk(
                chunk_x, self.seed, self.noise_surface,
                self.noise_caves, self.noise_ores, self.noise_biome
            )
        return self.chunks[chunk_x]

    def get_column_biome(self, gx):
        """Returns the surface/column biome for a given global X coordinate from cached chunk biomes."""
        chunk_x = gx // CHUNK_WIDTH
        lx = gx % CHUNK_WIDTH
        chunk = self.get_chunk(chunk_x)
        return chunk.col_biomes[lx]

    def get_biome_at(self, gx, gy):
        """Returns the active biome string for the given coordinates."""
        if gy >= DUNGEON_LEVEL - 8 and -30 <= gx <= 30:
            return BIOME_DUNGEON
        if gy >= CAVERN_LEVEL - 12:
            m_val = self.noise_ores.fractal2d(gx * 0.022, gy * 0.022, octaves=2)
            if m_val > 0.38:
                return BIOME_MUSHROOM
            return BIOME_CAVERN
        return self.get_column_biome(gx)

    def get_tile(self, gx, gy):
        """Retrieves tile ID at global coordinates (gx, gy)."""
        if self.world_type == "finite" and (gx < -160 or gx >= 160):
            return TILE_BEDROCK

        if gy < 0:
            return TILE_AIR
        if gy >= CHUNK_HEIGHT:
            return TILE_BEDROCK

        chunk_x = gx // CHUNK_WIDTH
        lx = gx % CHUNK_WIDTH
        chunk = self.get_chunk(chunk_x)
        return chunk.tiles[lx][gy]

    def set_tile(self, gx, gy, tile_id):
        """Sets tile ID at global coordinates (gx, gy)."""
        if self.world_type == "finite" and (gx < -160 or gx >= 160):
            return False

        if gy < 0 or gy >= CHUNK_HEIGHT:
            return False

        chunk_x = gx // CHUNK_WIDTH
        lx = gx % CHUNK_WIDTH
        chunk = self.get_chunk(chunk_x)
        chunk.tiles[lx][gy] = tile_id
        chunk.modified = True
        return True

    def get_wall(self, gx, gy):
        """Retrieves background wall ID at global coordinates (gx, gy)."""
        if self.world_type == "finite" and (gx < -160 or gx >= 160):
            return WALL_AIR

        if gy < 0 or gy >= CHUNK_HEIGHT:
            return WALL_AIR

        chunk_x = gx // CHUNK_WIDTH
        lx = gx % CHUNK_WIDTH
        chunk = self.get_chunk(chunk_x)
        return chunk.walls[lx][gy]

    def set_wall(self, gx, gy, wall_id):
        if gy < 0 or gy >= CHUNK_HEIGHT:
            return False

        chunk_x = gx // CHUNK_WIDTH
        lx = gx % CHUNK_WIDTH
        chunk = self.get_chunk(chunk_x)
        chunk.walls[lx][gy] = wall_id
        chunk.modified = True
        return True

    def ensure_chunks_in_range(self, min_gx, max_gx):
        """Pre-generates all chunks spanning min_gx to max_gx."""
        min_cx = min_gx // CHUNK_WIDTH
        max_cx = max_gx // CHUNK_WIDTH
        for cx in range(min_cx, max_cx + 1):
            self.get_chunk(cx)

    def get_surface_height(self, gx):
        """Returns the procedural surface height (y tile coord) for column gx."""
        chunk_x = gx // CHUNK_WIDTH
        lx = gx % CHUNK_WIDTH
        chunk = self.get_chunk(chunk_x)
        if hasattr(chunk, "surface_heights"):
            return chunk.surface_heights[lx]
        return SURFACE_LEVEL
