"""
Potaria - Infinite Chunk-Based Open World Manager
Streams procedural chunks seamlessly from -infinity to +infinity.
No left or right boundaries! Pure open-world exploration.
Developer: Kurados
"""

import math
import random
import pygame
from src.constants import (
    SURFACE_LEVEL, UNDERGROUND_LEVEL, CAVERN_LEVEL, DUNGEON_LEVEL,
    TILE_AIR, TILE_DIRT, TILE_GRASS, TILE_STONE, TILE_WOOD,
    TILE_LEAVES, TILE_WOOD_TRUNK, TILE_COPPER_ORE, TILE_IRON_ORE,
    TILE_GOLD_ORE, TILE_TORCH, TILE_BEDROCK, TILE_DUNGEON_BRICK,
    TILE_DUNGEON_ALTAR, TILE_SAND, TILE_SANDSTONE, TILE_CACTUS,
    TILE_SNOW, TILE_ICE, TILE_CORRUPT_GRASS, TILE_BLIGHT_GRASS, TILE_EBONSTONE,
    TILE_MUSHROOM_GRASS, TILE_MUSHROOM_STEM, TILE_MUSHROOM_CAP, TILE_CHEST, TILE_WATER,
    TILE_WORK_BENCH, TILE_WOOD_PLATFORM, TILE_DOOR_CLOSED, TILE_DOOR_OPEN,
    TILE_TABLE, TILE_CHAIR, TILE_GLASS, TILE_BED, TILE_BOOKSHELF,
    TILE_GRANDFATHER_CLOCK, TILE_FIREPLACE, TILE_CANDELABRA, TILE_CHANDELIER,
    TILE_POTTED_PLANT, TILE_DRESSER, TILE_TAPESTRY, TILE_BATHTUB, TILE_SINK,
    TILE_PAINTING, TILE_WOOD_SHELF,
    TILE_CARVED_TUBER_LANTERN, TILE_BRASS_LANTERN, TILE_SPECTRAL_LANTERN,
    TILE_DUNGEON_MAGMA, TILE_DUNGEON_ICE, TILE_DUNGEON_BONE, TILE_DUNGEON_GATE,
    WALL_AIR, WALL_DIRT, WALL_STONE, WALL_DUNGEON,
    WALL_SANDSTONE, WALL_ICE, WALL_EBONSTONE, WALL_MUSHROOM,
    WALL_DUNGEON_MAGMA, WALL_DUNGEON_ICE, WALL_DUNGEON_BONE,
    BIOME_FOREST, BIOME_DESERT, BIOME_SNOW, BIOME_CORRUPTION, BIOME_BLIGHT,
    BIOME_MUSHROOM, BIOME_DUNGEON, BIOME_CAVERN,
    TILE_PROPS
)
from src.world.noise import PerlinNoise

CHUNK_WIDTH = 16
CHUNK_HEIGHT = 240
SECTION_HEIGHT = 16
NUM_SECTIONS = CHUNK_HEIGHT // SECTION_HEIGHT

OPAQUE_EXCLUSIONS = (
    TILE_WORK_BENCH, TILE_WOOD_PLATFORM, TILE_TORCH, TILE_DOOR_CLOSED,
    TILE_DOOR_OPEN, TILE_TABLE, TILE_CHAIR, TILE_GLASS, TILE_CHEST,
    TILE_BED, TILE_BOOKSHELF, TILE_GRANDFATHER_CLOCK, TILE_FIREPLACE,
    TILE_CANDELABRA, TILE_CHANDELIER, TILE_POTTED_PLANT, TILE_DRESSER,
    TILE_TAPESTRY, TILE_BATHTUB, TILE_SINK, TILE_PAINTING, TILE_WOOD_SHELF,
    TILE_CARVED_TUBER_LANTERN, TILE_BRASS_LANTERN, TILE_SPECTRAL_LANTERN,
    TILE_DUNGEON_GATE
)

class ChunkSection:
    __slots__ = ("chunk_x", "section_y", "surf", "dirty", "animated_tiles", "is_empty")

    def __init__(self, chunk_x, section_y):
        self.chunk_x = chunk_x
        self.section_y = section_y
        self.surf = None
        self.dirty = True
        self.animated_tiles = []
        self.is_empty = False

    def bake(self, world):
        sec_w = CHUNK_WIDTH * world.scaled_tile
        sec_h = SECTION_HEIGHT * world.scaled_tile
        if self.surf is None or self.surf.get_width() != sec_w or self.surf.get_height() != sec_h:
            self.surf = pygame.Surface((sec_w, sec_h), pygame.SRCALPHA)
        else:
            self.surf.fill((0, 0, 0, 0))

        self.animated_tiles = []
        drawn_count = 0
        min_ty = self.section_y * SECTION_HEIGHT
        max_ty = min_ty + SECTION_HEIGHT
        chunk = world.chunk_manager.get_chunk(self.chunk_x)
        if chunk is None:
            self.is_empty = True
            self.dirty = False
            return

        for lx in range(CHUNK_WIDTH):
            gx = self.chunk_x * CHUNK_WIDTH + lx
            surf_y = chunk.surface_heights[lx]
            col_biome = chunk.col_biomes[lx]
            is_dungeon_col = (-30 <= gx <= 30)
            local_px = lx * world.scaled_tile
            tiles_col = chunk.tiles[lx]
            walls_col = chunk.walls[lx]

            for ty in range(min_ty, max_ty):
                local_py = (ty - min_ty) * world.scaled_tile
                t_id = tiles_col[ty]
                w_id = walls_col[ty]
                if t_id != TILE_AIR or w_id != WALL_AIR or ty >= surf_y or ty >= SURFACE_LEVEL:
                    drawn_count += 1
                prop = TILE_PROPS.get(t_id, {})

                # 1. Background Walls & Subterranean Cave Backdrop
                is_full_opaque = prop.get("opaque", False) and prop.get("solid", False) and (t_id not in OPAQUE_EXCLUSIONS)

                if not is_full_opaque:
                    if w_id != WALL_AIR:
                        wall_tex = world.scaled_walls.get(w_id)
                        if wall_tex:
                            self.surf.blit(wall_tex, (local_px, local_py))
                    else:
                        if ty >= surf_y or ty >= SURFACE_LEVEL:
                            if ty >= DUNGEON_LEVEL - 8 and is_dungeon_col:
                                sub_w = WALL_DUNGEON
                            elif ty >= CAVERN_LEVEL - 12:
                                sub_w = WALL_MUSHROOM if (t_id == TILE_MUSHROOM_GRASS or w_id == WALL_MUSHROOM) else WALL_STONE
                            elif col_biome == BIOME_DESERT:
                                sub_w = WALL_SANDSTONE
                            elif col_biome == BIOME_SNOW:
                                sub_w = WALL_ICE
                            elif col_biome == BIOME_CORRUPTION:
                                sub_w = WALL_EBONSTONE
                            else:
                                sub_w = WALL_DIRT if ty < surf_y + 20 else WALL_STONE

                            cave_wall_tex = world.scaled_walls.get(sub_w)
                            if cave_wall_tex:
                                self.surf.blit(cave_wall_tex, (local_px, local_py))

                # 2. Foreground Tiles
                if t_id != TILE_AIR:
                    if t_id in (TILE_TORCH, TILE_WATER, TILE_SAPLING):
                        self.animated_tiles.append((local_px, local_py, t_id))
                    elif t_id == TILE_WOOD_TRUNK:
                        below_id = tiles_col[ty + 1] if ty + 1 < world.height else TILE_BEDROCK
                        above_id = tiles_col[ty - 1] if ty > 0 else TILE_AIR
                        left_id = world.get_tile(gx - 1, ty)
                        right_id = world.get_tile(gx + 1, ty)
                        in_canopy = (above_id == TILE_LEAVES or left_id == TILE_LEAVES or right_id == TILE_LEAVES)

                        if below_id in (TILE_GRASS, TILE_DIRT, TILE_SNOW, TILE_SAND, TILE_BLIGHT_GRASS, TILE_CORRUPT_GRASS):
                            self.surf.blit(world.scaled_trunk_base, (local_px, local_py))
                        elif not in_canopy and (gx + ty) % 5 == 0:
                            if col_biome == BIOME_SNOW and hasattr(world, "scaled_trunk_branch_l_snow"):
                                self.surf.blit(world.scaled_trunk_branch_l_snow, (local_px, local_py))
                            elif col_biome in (BIOME_CORRUPTION, BIOME_BLIGHT) and hasattr(world, "scaled_trunk_branch_l_blight"):
                                self.surf.blit(world.scaled_trunk_branch_l_blight, (local_px, local_py))
                            elif col_biome == BIOME_DESERT and hasattr(world, "scaled_trunk_branch_l_palm"):
                                self.surf.blit(world.scaled_trunk_branch_l_palm, (local_px, local_py))
                            else:
                                self.surf.blit(world.scaled_trunk_branch_l, (local_px, local_py))
                        elif not in_canopy and (gx + ty) % 5 == 2:
                            if col_biome == BIOME_SNOW and hasattr(world, "scaled_trunk_branch_r_snow"):
                                self.surf.blit(world.scaled_trunk_branch_r_snow, (local_px, local_py))
                            elif col_biome in (BIOME_CORRUPTION, BIOME_BLIGHT) and hasattr(world, "scaled_trunk_branch_r_blight"):
                                self.surf.blit(world.scaled_trunk_branch_r_blight, (local_px, local_py))
                            elif col_biome == BIOME_DESERT and hasattr(world, "scaled_trunk_branch_r_palm"):
                                self.surf.blit(world.scaled_trunk_branch_r_palm, (local_px, local_py))
                            else:
                                self.surf.blit(world.scaled_trunk_branch_r, (local_px, local_py))
                        else:
                            tile_tex = world.scaled_tiles.get(t_id)
                            if tile_tex:
                                self.surf.blit(tile_tex, (local_px, local_py))

                        if in_canopy:
                            crown_tex = getattr(world, "scaled_trunk_crown", None)
                            if col_biome == BIOME_SNOW and getattr(world, "scaled_trunk_crown_snow", None):
                                crown_tex = world.scaled_trunk_crown_snow
                            elif col_biome in (BIOME_CORRUPTION, BIOME_BLIGHT) and getattr(world, "scaled_trunk_crown_blight", None):
                                crown_tex = world.scaled_trunk_crown_blight
                            elif col_biome == BIOME_DESERT and getattr(world, "scaled_trunk_crown_palm", None):
                                crown_tex = world.scaled_trunk_crown_palm
                            if crown_tex:
                                self.surf.blit(crown_tex, (local_px, local_py))
                    elif t_id == TILE_LEAVES:
                        up_air = (world.get_tile(gx, ty - 1) == TILE_AIR)
                        down_air = (world.get_tile(gx, ty + 1) == TILE_AIR)
                        left_air = (world.get_tile(gx - 1, ty) == TILE_AIR)
                        right_air = (world.get_tile(gx + 1, ty) == TILE_AIR)

                        b_key = "forest"
                        if col_biome == BIOME_SNOW:
                            b_key = "snow"
                        elif col_biome in (BIOME_CORRUPTION, BIOME_BLIGHT):
                            b_key = "blight"
                        elif col_biome == BIOME_DESERT:
                            b_key = "palm"

                        leaf_dict = getattr(world, "scaled_leaf_variants", {}).get(b_key, {})
                        v_tex = leaf_dict.get((up_air, down_air, left_air, right_air))
                        if v_tex:
                            self.surf.blit(v_tex, (local_px, local_py))
                        else:
                            if col_biome == BIOME_SNOW:
                                self.surf.blit(world.scaled_snow_leaves, (local_px, local_py))
                            elif col_biome in (BIOME_CORRUPTION, BIOME_BLIGHT):
                                self.surf.blit(world.scaled_blight_leaves, (local_px, local_py))
                            elif col_biome == BIOME_DESERT and hasattr(world, "scaled_palm_leaves"):
                                self.surf.blit(world.scaled_palm_leaves, (local_px, local_py))
                            else:
                                tile_tex = world.scaled_tiles.get(t_id)
                                if tile_tex:
                                    self.surf.blit(tile_tex, (local_px, local_py))
                    else:
                        tile_tex = world.scaled_tiles.get(t_id)
                        if tile_tex:
                            self.surf.blit(tile_tex, (local_px, local_py))

        self.is_empty = (drawn_count == 0)
        self.dirty = False

class Chunk:
    def __init__(self, chunk_x, seed, noise_surface, noise_caves, noise_ores, noise_biome):
        self.chunk_x = chunk_x
        self.width = CHUNK_WIDTH
        self.height = CHUNK_HEIGHT
        self.tiles = [[TILE_AIR for _ in range(self.height)] for _ in range(self.width)]
        self.walls = [[WALL_AIR for _ in range(self.height)] for _ in range(self.width)]
        self.modified = False
        self.sections = {}

        self._generate(seed, noise_surface, noise_caves, noise_ores, noise_biome)

    def mark_section_dirty(self, sec_y):
        if sec_y in self.sections:
            self.sections[sec_y].dirty = True

    def mark_all_sections_dirty(self):
        for sec in self.sections.values():
            sec.dirty = True

    def get_or_bake_section(self, sec_y, world):
        if sec_y not in self.sections:
            self.sections[sec_y] = ChunkSection(self.chunk_x, sec_y)
        sec = self.sections[sec_y]
        if sec.dirty or sec.surf is None:
            sec.bake(world)
        return sec

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

        # 6. Grand Biome Underground Dungeons & Sky Citadel
        # 6a. Forest Nether Dungeon (Lord Malus - Center gx = 0)
        if -2 <= self.chunk_x <= 2:
            self._carve_grand_biome_dungeon(center_gx=0, brick_tile=TILE_DUNGEON_BRICK, wall_id=WALL_DUNGEON)
            self._carve_sky_citadel()

        # 6b. Magma / Underworld Dungeon (Ignis Colossus - Center gx = 80)
        if 3 <= self.chunk_x <= 7:
            self._carve_grand_biome_dungeon(center_gx=80, brick_tile=TILE_DUNGEON_MAGMA, wall_id=WALL_DUNGEON_MAGMA)

        # 6c. Glacial / Permafrost Crypt (Cryo-Spud - Center gx = -80)
        if -7 <= self.chunk_x <= -3:
            self._carve_grand_biome_dungeon(center_gx=-80, brick_tile=TILE_DUNGEON_ICE, wall_id=WALL_DUNGEON_ICE)

        # 6d. Catacombs / Blight Ossuary (Necro-Tuber - Center gx = 140)
        if 7 <= self.chunk_x <= 11:
            self._carve_grand_biome_dungeon(center_gx=140, brick_tile=TILE_DUNGEON_BONE, wall_id=WALL_DUNGEON_BONE)

        # 6e. Biome Rune Pocket Arenas (Backwards compatibility for gx = 5000, -5000, 8000)
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

    def _carve_grand_biome_dungeon(self, center_gx, brick_tile, wall_id):
        """Carves out a grand multi-tier biome underground dungeon with entrance gates, wings, bridges, and boss room."""
        for lx in range(self.width):
            gx = self.chunk_x * self.width + lx
            dx = gx - center_gx
            if abs(dx) > 22:
                continue

            # 1. Subtle Cavern Marker Signs (unbreakable indicator bricks embedded in upper cavern rock)
            if abs(dx) in (6, 12, 18):
                for my in (148, 149, 151, 152):
                    self.tiles[lx][my] = brick_tile
                    self.walls[lx][my] = wall_id

            # 2. Main Dungeon Perimeter & Chambers (ty = 162..218)
            for y in range(162, 219):
                # Outer perimeter frame (indestructible boundary)
                if abs(dx) == 22 or y in (162, 218):
                    self.tiles[lx][y] = brick_tile
                    self.walls[lx][y] = wall_id
                else:
                    self.walls[lx][y] = wall_id
                    self.tiles[lx][y] = TILE_AIR

            # Level 1: Entrance Vestibule (y = 163..172)
            # Vestibule floor with left/right stairwells
            if abs(dx) not in (17, 18):
                self.tiles[lx][172] = brick_tile
            # Grand Entrance Gate portcullises
            if abs(dx) in (9, 10):
                for gy in range(168, 172):
                    self.tiles[lx][gy] = TILE_DUNGEON_GATE
            # Gatehouse torches
            if abs(dx) in (5, 12, 19):
                self.tiles[lx][169] = TILE_TORCH

            # Level 2: Middle Wings & Central Bridge (y = 173..194)
            # Floor dividing Level 2 from Arena, with central descent chasm (-6 <= dx <= 6)
            if abs(dx) > 6:
                self.tiles[lx][194] = brick_tile

            # Intermediate floor & central bridge across chasm at y = 183
            if abs(dx) <= 7 or abs(dx) >= 9:
                self.tiles[lx][183] = brick_tile

            # Tactical platforms in wings for climbing and maneuvering
            if (-18 <= dx <= -10) or (10 <= dx <= 18):
                self.tiles[lx][177] = TILE_WOOD_PLATFORM
            if (-19 <= dx <= -11) or (11 <= dx <= 19):
                self.tiles[lx][188] = TILE_WOOD_PLATFORM

            # Wing torches
            if abs(dx) in (10, 16):
                self.tiles[lx][176] = TILE_TORCH
                self.tiles[lx][187] = TILE_TORCH

            # Level 3: Grand Boss Arena (y = 195..217)
            # High-tier jump-through platforms
            if (-16 <= dx <= -6) or (6 <= dx <= 16):
                self.tiles[lx][201] = TILE_WOOD_PLATFORM
            # Mid-tier jump-through platforms (including central aerial platform)
            if (-19 <= dx <= -11) or (-4 <= dx <= 4) or (11 <= dx <= 19):
                self.tiles[lx][207] = TILE_WOOD_PLATFORM
            # Low-tier jump-through platforms
            if (-15 <= dx <= -7) or (7 <= dx <= 15):
                self.tiles[lx][212] = TILE_WOOD_PLATFORM

            # Arena perimeter torches
            if abs(dx) in (2, 8, 14, 20):
                self.tiles[lx][214] = TILE_TORCH
                self.tiles[lx][200] = TILE_TORCH

            # Boss Altar at arena floor center
            if dx == 0:
                self.tiles[lx][216] = TILE_DUNGEON_ALTAR

    def _carve_sky_citadel(self):
        """Carves out Sol-Rho's Celestial Sky Citadel floating in the clouds."""
        for lx in range(self.width):
            gx = self.chunk_x * self.width + lx
            if abs(gx) > 22:
                continue

            # Sky Citadel background wall
            for y in range(16, 38):
                self.walls[lx][y] = WALL_DUNGEON
                self.tiles[lx][y] = TILE_AIR

            # Outer perimeter frame
            for y in range(18, 38):
                if abs(gx) == 22 or y in (18, 37):
                    self.tiles[lx][y] = TILE_DUNGEON_BRICK

            # Citadel Floor at y = 36 and 37
            self.tiles[lx][36] = TILE_DUNGEON_BRICK
            self.tiles[lx][37] = TILE_DUNGEON_BRICK

            # Grand Dais / Altar at gx = 0
            if gx == 0:
                self.tiles[lx][35] = TILE_DUNGEON_ALTAR

            # Celestial Pillars
            if abs(gx) in (6, 12, 18):
                for py in range(22, 36):
                    self.tiles[lx][py] = TILE_DUNGEON_BRICK

            # Aerial jump-through platforms for bullet hell dodging
            if (-16 <= gx <= -8) or (8 <= gx <= 16):
                self.tiles[lx][31] = TILE_WOOD_PLATFORM
            if -10 <= gx <= 10:
                self.tiles[lx][26] = TILE_WOOD_PLATFORM

            # Spectral Lanterns hanging from celestial ceiling
            if abs(gx) in (4, 10, 16):
                self.tiles[lx][21] = TILE_SPECTRAL_LANTERN

import threading
import concurrent.futures

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
        
        self._executor = concurrent.futures.ThreadPoolExecutor(max_workers=2)
        self._generating = {}
        self._lock = threading.Lock()

    def _create_chunk(self, chunk_x):
        return Chunk(
            chunk_x, self.seed, self.noise_surface,
            self.noise_caves, self.noise_ores, self.noise_biome
        )

    def _generate_async(self, chunk_x):
        chk = self._create_chunk(chunk_x)
        with self._lock:
            self.chunks[chunk_x] = chk
            self._generating.pop(chunk_x, None)
        return chk

    def has_chunk(self, chunk_x):
        """Returns True if the chunk at chunk_x is already generated and cached."""
        with self._lock:
            return chunk_x in self.chunks

    def get_chunk(self, chunk_x):
        """Retrieves or procedurally generates the chunk at chunk_x."""
        with self._lock:
            if chunk_x in self.chunks:
                return self.chunks[chunk_x]
            fut = self._generating.get(chunk_x)

        if fut is not None:
            return fut.result()

        chk = self._create_chunk(chunk_x)
        with self._lock:
            self.chunks[chunk_x] = chk
            self._generating.pop(chunk_x, None)
        return chk

    def get_column_biome(self, gx):
        """Returns the surface/column biome for a given global X coordinate from cached chunk biomes."""
        chunk_x = gx // CHUNK_WIDTH
        lx = gx % CHUNK_WIDTH
        chunk = self.get_chunk(chunk_x)
        if chunk is None:
            return BIOME_FOREST
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
        if chunk is None:
            return TILE_AIR
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
        if chunk is None:
            return False
        chunk.tiles[lx][gy] = tile_id
        chunk.modified = True

        sec_y = gy // SECTION_HEIGHT
        chunk.mark_section_dirty(sec_y)
        if gy % SECTION_HEIGHT == 0 and sec_y > 0:
            chunk.mark_section_dirty(sec_y - 1)
        elif gy % SECTION_HEIGHT == (SECTION_HEIGHT - 1) and sec_y < (NUM_SECTIONS - 1):
            chunk.mark_section_dirty(sec_y + 1)

        if lx == 0:
            left_chunk = self.chunks.get(chunk_x - 1)
            if left_chunk:
                left_chunk.mark_section_dirty(sec_y)
        elif lx == CHUNK_WIDTH - 1:
            right_chunk = self.chunks.get(chunk_x + 1)
            if right_chunk:
                right_chunk.mark_section_dirty(sec_y)

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
        if chunk is None:
            return WALL_AIR
        return chunk.walls[lx][gy]

    def set_wall(self, gx, gy, wall_id):
        if gy < 0 or gy >= CHUNK_HEIGHT:
            return False

        chunk_x = gx // CHUNK_WIDTH
        lx = gx % CHUNK_WIDTH
        chunk = self.get_chunk(chunk_x)
        if chunk is None:
            return False
        chunk.walls[lx][gy] = wall_id
        chunk.modified = True
        chunk.mark_section_dirty(gy // SECTION_HEIGHT)
        return True

    def ensure_chunks_in_range(self, min_gx, max_gx):
        """Pre-generates all chunks spanning min_gx to max_gx."""
        min_cx = min_gx // CHUNK_WIDTH
        max_cx = max_gx // CHUNK_WIDTH
        
        pad = 4
        for cx in range(min_cx - pad, max_cx + pad + 1):
            with self._lock:
                if cx not in self.chunks and cx not in self._generating:
                    fut = self._executor.submit(self._generate_async, cx)
                    self._generating[cx] = fut


    def get_surface_height(self, gx):
        """Returns the procedural surface height (y tile coord) for column gx."""
        chunk_x = gx // CHUNK_WIDTH
        lx = gx % CHUNK_WIDTH
        chunk = self.get_chunk(chunk_x)
        if chunk is None or not hasattr(chunk, "surface_heights"):
            return SURFACE_LEVEL
        return chunk.surface_heights[lx]
