"""
Potaria - World Manager (Boundless Open World)
Routes tile queries, mining, building, and rendering through ChunkManager.
Developer: Kurados
"""

import math
import random
import collections
import pygame
from src.constants import (
    SCALE, SCALED_TILE, SURFACE_LEVEL, UNDERGROUND_LEVEL, CAVERN_LEVEL, DUNGEON_LEVEL,
    TILE_AIR, TILE_DIRT, TILE_GRASS, TILE_STONE, TILE_WOOD, TILE_LEAVES, TILE_WOOD_TRUNK,
    TILE_COPPER_ORE, TILE_IRON_ORE, TILE_GOLD_ORE, TILE_WOOD_PLATFORM, TILE_WORK_BENCH,
    TILE_FURNACE, TILE_TORCH, TILE_STONE_BRICK, TILE_BEDROCK, TILE_DUNGEON_BRICK,
    TILE_DUNGEON_ALTAR, TILE_CHEST, TILE_ROOF_TILES, TILE_WOOD_PLANKS, TILE_GLASS,
    TILE_DOOR_CLOSED, TILE_DOOR_OPEN, TILE_TABLE, TILE_CHAIR, TILE_WATER,
    TILE_BED, TILE_BOOKSHELF, TILE_GRANDFATHER_CLOCK, TILE_FIREPLACE,
    TILE_CANDELABRA, TILE_CHANDELIER, TILE_POTTED_PLANT, TILE_DRESSER,
    TILE_TAPESTRY, TILE_BATHTUB, TILE_SINK, TILE_PAINTING, TILE_WOOD_SHELF,
    TILE_SAND, TILE_SNOW, TILE_BLIGHT_GRASS, TILE_CORRUPT_GRASS, TILE_BLIGHTSTONE, TILE_EBONSTONE,
    WALL_AIR, WALL_DIRT, WALL_STONE, WALL_WOOD, WALL_STONE_BRICK, WALL_DUNGEON,
    WALL_SANDSTONE, WALL_ICE, WALL_EBONSTONE, WALL_MUSHROOM,
    BIOME_FOREST, BIOME_DESERT, BIOME_SNOW, BIOME_CORRUPTION, BIOME_BLIGHT, BIOME_MUSHROOM, BIOME_DUNGEON,
    TILE_PROPS
)
from src.world.chunk_manager import ChunkManager, CHUNK_WIDTH, CHUNK_HEIGHT, SECTION_HEIGHT, NUM_SECTIONS

class World:
    def __init__(self, asset_factory, seed=None, world_type="infinite"):
        self.scale = SCALE
        self.scaled_tile = SCALED_TILE
        self.height = CHUNK_HEIGHT
        self.asset_factory = asset_factory
        self.world_type = world_type

        # Initialize Chunk Manager
        self.chunk_manager = ChunkManager(seed, world_type=world_type)
        self.seed = self.chunk_manager.seed

        # Pre-scale textures for fast blitting at 32x32
        self.scaled_tiles = {}
        for tid, surf in asset_factory.tiles.items():
            if isinstance(surf, pygame.Surface):
                self.scaled_tiles[tid] = pygame.transform.scale(surf, (self.scaled_tile, self.scaled_tile))
            elif isinstance(surf, list):
                self.scaled_tiles[tid] = [
                    pygame.transform.scale(f, (self.scaled_tile, self.scaled_tile))
                    for f in surf if isinstance(f, pygame.Surface)
                ]

        self.scaled_walls = {}
        for wid, surf in asset_factory.walls.items():
            self.scaled_walls[wid] = pygame.transform.scale(surf, (self.scaled_tile, self.scaled_tile))

        self.scaled_cracks = [
            pygame.transform.scale(c, (self.scaled_tile, self.scaled_tile))
            for c in asset_factory.ui["cracks"]
        ]

        self.scaled_torch_frames = [
            pygame.transform.scale(f, (self.scaled_tile, self.scaled_tile))
            for f in asset_factory.torch_frames
        ]
        self.torch_anim_timer = 0
        self.torch_frame_idx = 0

        # Water animation frames
        self.scaled_water_frames = [
            pygame.transform.scale(f, (self.scaled_tile, self.scaled_tile))
            for f in getattr(asset_factory, "water_frames", [])
        ]
        self.scaled_water_submerged = [
            pygame.transform.scale(f, (self.scaled_tile, self.scaled_tile))
            for f in getattr(asset_factory, "water_submerged_frames", [])
        ]
        self.water_anim_timer = 0.0
        self.water_frame_idx = 0

        # Cute Terraria Tree assets
        if hasattr(asset_factory, "trunk_base"):
            self.scaled_trunk_base = pygame.transform.scale(asset_factory.trunk_base, (self.scaled_tile, self.scaled_tile))
        else:
            self.scaled_trunk_base = self.scaled_tiles.get(TILE_WOOD_TRUNK)

        if hasattr(asset_factory, "trunk_branch_l"):
            self.scaled_trunk_branch_l = pygame.transform.scale(asset_factory.trunk_branch_l, (self.scaled_tile, self.scaled_tile))
            self.scaled_trunk_branch_r = pygame.transform.scale(asset_factory.trunk_branch_r, (self.scaled_tile, self.scaled_tile))
        else:
            self.scaled_trunk_branch_l = self.scaled_tiles.get(TILE_WOOD_TRUNK)
            self.scaled_trunk_branch_r = self.scaled_tiles.get(TILE_WOOD_TRUNK)

        if hasattr(asset_factory, "snow_leaves"):
            self.scaled_snow_leaves = pygame.transform.scale(asset_factory.snow_leaves, (self.scaled_tile, self.scaled_tile))
        else:
            self.scaled_snow_leaves = self.scaled_tiles.get(TILE_LEAVES)

        if hasattr(asset_factory, "blight_leaves"):
            self.scaled_blight_leaves = pygame.transform.scale(asset_factory.blight_leaves, (self.scaled_tile, self.scaled_tile))
        else:
            self.scaled_blight_leaves = self.scaled_tiles.get(TILE_LEAVES)

        if hasattr(asset_factory, "palm_leaves"):
            self.scaled_palm_leaves = pygame.transform.scale(asset_factory.palm_leaves, (self.scaled_tile, self.scaled_tile))
        else:
            self.scaled_palm_leaves = self.scaled_tiles.get(TILE_LEAVES)

        if hasattr(asset_factory, "autumn_leaves"):
            self.scaled_autumn_leaves = pygame.transform.scale(asset_factory.autumn_leaves, (self.scaled_tile, self.scaled_tile))
        else:
            self.scaled_autumn_leaves = self.scaled_tiles.get(TILE_LEAVES)

        for suffix in ("snow", "blight", "palm"):
            attr_l = f"trunk_branch_l_{suffix}"
            attr_r = f"trunk_branch_r_{suffix}"
            if hasattr(asset_factory, attr_l):
                setattr(self, f"scaled_{attr_l}", pygame.transform.scale(getattr(asset_factory, attr_l), (self.scaled_tile, self.scaled_tile)))
                setattr(self, f"scaled_{attr_r}", pygame.transform.scale(getattr(asset_factory, attr_r), (self.scaled_tile, self.scaled_tile)))

        # Cute Terraria Tree Trunk Crown foliage overlays
        for c_name in ("trunk_crown", "trunk_crown_snow", "trunk_crown_blight", "trunk_crown_palm"):
            if hasattr(asset_factory, c_name):
                setattr(self, f"scaled_{c_name}", pygame.transform.scale(getattr(asset_factory, c_name), (self.scaled_tile, self.scaled_tile)))
            else:
                setattr(self, f"scaled_{c_name}", None)

        # Pre-scaled border-aware cute leaf variants (16 combinations per biome)
        self.scaled_leaf_variants = {}
        raw_leaf_variants = getattr(asset_factory, "leaf_variants", {})
        for b_key, vdict in raw_leaf_variants.items():
            self.scaled_leaf_variants[b_key] = {}
            for k, surf in vdict.items():
                self.scaled_leaf_variants[b_key][k] = pygame.transform.scale(surf, (self.scaled_tile, self.scaled_tile))

        self.last_felled_tree = (0, [])
        self.last_felled_trunks = []
        self.tile_damage = {}
        self.last_damaged_tile = None
        self.damage_decay_timer = 0
        self.player_placed_tiles = set()
        self.fireplaces = set()
        self.comfort_tiles = set()

        # Determine Spud surface spawn point (around gx=0)
        self.chunk_manager.ensure_chunks_in_range(-2, 2)
        spawn_y = 60
        for y in range(30, 100):
            if self.chunk_manager.get_tile(0, y) != TILE_AIR:
                spawn_y = y - 3
                break
        self.spawn_point = (0, spawn_y * self.scaled_tile)
        self.dungeon_spawn = (0, (DUNGEON_LEVEL + 10) * self.scaled_tile)
        self.desert_arena_spawn = (5000 * self.scaled_tile, 52 * self.scaled_tile)
        self.cryo_arena_spawn = (-5000 * self.scaled_tile, 52 * self.scaled_tile)
        self.necro_arena_spawn = (8000 * self.scaled_tile, 52 * self.scaled_tile)

        # Town NPCs & Housing Settlement System
        self.town_npcs = []
        self.housing_check_timer = 0.0
        self.town_housing_enabled = False  # Town checking disabled: Potaria does not have towns
        self.mystic_trader_timer = 0.0
        self.mystic_trader_interval = 240.0
        self.chests = {}  # (tx, ty) -> StorageChest

    def get_biome_spawn(self, player_idx=1):
        """Returns surface spawn coordinates in different biomes for LMS / PvP mode."""
        coords = {1: 0, 2: 70, 3: -70, 4: 120, 5: -120}
        gx = coords.get(player_idx, (player_idx - 1) * 60)
        self.chunk_manager.ensure_chunks_in_range(gx - 1, gx + 1)
        surf_y = self.get_surface_height(gx)
        return (gx * self.scaled_tile, (surf_y - 3) * self.scaled_tile)

    def update(self, dt):
        self.torch_anim_timer += dt
        if self.torch_anim_timer >= 0.15:
            self.torch_anim_timer = 0
            self.torch_frame_idx = (self.torch_frame_idx + 1) % len(self.scaled_torch_frames)

        self.water_anim_timer += dt
        if self.water_anim_timer >= 0.12:
            self.water_anim_timer = 0
            if self.scaled_water_frames:
                self.water_frame_idx = (self.water_frame_idx + 1) % len(self.scaled_water_frames)

        self.damage_decay_timer += dt
        if self.damage_decay_timer > 3.0 and self.tile_damage:
            self.tile_damage.clear()
            self.damage_decay_timer = 0

    def get_tile(self, tx, ty):
        return self.chunk_manager.get_tile(tx, ty)

    def has_chunk(self, chunk_x):
        return self.chunk_manager.has_chunk(chunk_x)

    def set_tile(self, tx, ty, tile_id):
        res = self.chunk_manager.set_tile(tx, ty, tile_id)
        if tile_id == TILE_FIREPLACE:
            self.fireplaces.add((tx, ty))
        elif (tx, ty) in self.fireplaces:
            self.fireplaces.discard((tx, ty))

        if tile_id in (TILE_CHAIR, TILE_BED):
            self.comfort_tiles.add((tx, ty))
        elif (tx, ty) in self.comfort_tiles:
            self.comfort_tiles.discard((tx, ty))
        return res

    def get_wall(self, tx, ty):
        return self.chunk_manager.get_wall(tx, ty)

    def set_wall(self, tx, ty, wall_id):
        return self.chunk_manager.set_wall(tx, ty, wall_id)

    def get_surface_height(self, tx):
        return self.chunk_manager.get_surface_height(tx)

    def get_biome_at(self, tx, ty):
        return self.chunk_manager.get_biome_at(tx, ty)

    def get_biome_at_world(self, world_x, world_y):
        tx = int(math.floor(world_x / self.scaled_tile))
        ty = int(math.floor(world_y / self.scaled_tile))
        return self.chunk_manager.get_biome_at(tx, ty)

    def is_water(self, tx, ty):
        """Returns True if the tile at (tx, ty) is liquid water."""
        return self.get_tile(tx, ty) == TILE_WATER

    def is_water_world(self, wx, wy):
        """Returns True if world pixel coordinates are inside liquid water."""
        tx = int(math.floor(wx / self.scaled_tile))
        ty = int(math.floor(wy / self.scaled_tile))
        return self.is_water(tx, ty)

    def get_water_rects_in_bounds(self, rect_world_px):
        """Returns bounding rects of liquid water tiles overlapping rect_world_px."""
        min_tx = int(rect_world_px.left // self.scaled_tile)
        max_tx = int(rect_world_px.right // self.scaled_tile)
        min_ty = max(0, int(rect_world_px.top // self.scaled_tile))
        max_ty = min(self.height - 1, int(rect_world_px.bottom // self.scaled_tile))

        self.chunk_manager.ensure_chunks_in_range(min_tx, max_tx)

        waters = []
        for tx in range(min_tx, max_tx + 1):
            for ty in range(min_ty, max_ty + 1):
                if self.get_tile(tx, ty) == TILE_WATER:
                    waters.append(pygame.Rect(
                        tx * self.scaled_tile,
                        ty * self.scaled_tile,
                        self.scaled_tile,
                        self.scaled_tile
                    ))
        return waters

    def fell_tree(self, start_tx, start_ty):
        """
        Fells tree starting from (start_tx, start_ty) upwards.
        Finds all contiguous wood trunk blocks upwards and attached leaves,
        destroys them, and returns: (felled_trunks_count, list_of_felled_leaf_coords)
        Also stores full trunk list in self.last_felled_trunks for block_delta/sync.
        """
        felled_trunks = []
        felled_leaves = []

        # 1. Traverse trunk upward from start_ty
        queue = [(start_tx, start_ty)]
        visited_trunk = set([(start_tx, start_ty)])

        while queue:
            cx, cy = queue.pop(0)
            felled_trunks.append((cx, cy))
            for dx, dy in [(0, -1), (-1, -1), (1, -1), (-1, 0), (1, 0)]:
                nx, ny = cx + dx, cy + dy
                if (nx, ny) not in visited_trunk:
                    # Never traverse into player-placed blocks (houses, platforms, walls)
                    if (nx, ny) in self.player_placed_tiles:
                        continue
                    if self.get_tile(nx, ny) in (TILE_WOOD_TRUNK, TILE_WOOD):
                        visited_trunk.add((nx, ny))
                        queue.append((nx, ny))

        if not felled_trunks:
            return 0, []

        felled_trunk_cols = {tx for tx, _ in felled_trunks}
        min_tx = min(tx for tx, _ in felled_trunks)
        max_tx = max(tx for tx, _ in felled_trunks)
        min_ty = min(ty for _, ty in felled_trunks)
        max_ty = max(ty for _, ty in felled_trunks)

        # 2. Find all surviving standing tree trunks in the vicinity (excluding felled tree columns and player-placed blocks)
        surviving_trunks = set()
        for sx in range(min_tx - 10, max_tx + 11):
            if sx in felled_trunk_cols:
                continue
            for sy in range(min_ty - 8, max_ty + 8):
                if (sx, sy) not in visited_trunk and (sx, sy) not in self.player_placed_tiles:
                    if self.get_tile(sx, sy) in (TILE_WOOD_TRUNK, TILE_WOOD):
                        surviving_trunks.add((sx, sy))

        # 3. Find candidate leaves belonging to the felled trunk's crown
        # Natural tree canopies extend at most 4 tiles horizontally and 5 tiles vertically from trunk blocks
        candidate_leaves = set()
        for tx, ty in felled_trunks:
            for lx in range(tx - 4, tx + 5):
                for ly in range(ty - 5, ty + 5):
                    if (lx, ly) not in self.player_placed_tiles and self.get_tile(lx, ly) == TILE_LEAVES:
                        candidate_leaves.add((lx, ly))

        # 4. Filter leaves: Any leaf that belongs to or is supported by a surviving tree trunk MUST NOT be felled!
        for lx, ly in candidate_leaves:
            is_surviving_leaf = False
            for stx, sty in surviving_trunks:
                if abs(lx - stx) <= 3 and abs(ly - sty) <= 4:
                    is_surviving_leaf = True
                    break

            if not is_surviving_leaf:
                felled_leaves.append((lx, ly))

        # 3. Clear all felled blocks
        for tx, ty in felled_trunks:
            self.chunk_manager.set_tile(tx, ty, TILE_AIR)
            self.player_placed_tiles.discard((tx, ty))
            self.tile_damage.pop((tx, ty), None)

        for lx, ly in felled_leaves:
            self.chunk_manager.set_tile(lx, ly, TILE_AIR)
            self.player_placed_tiles.discard((lx, ly))
            self.tile_damage.pop((lx, ly), None)

        self.last_felled_trunks = list(felled_trunks)
        return len(felled_trunks), felled_leaves

    def damage_tile_at(self, tx, ty, power):
        t_id = self.get_tile(tx, ty)
        if t_id == TILE_AIR or t_id == TILE_BEDROCK or t_id == TILE_WATER:
            return False, None, t_id

        # Foliage protection: Player can only destroy wood, never bush/leaves directly!
        if t_id == TILE_LEAVES:
            return False, None, t_id

        prop = TILE_PROPS.get(t_id, TILE_PROPS[0])
        max_health = prop.get("hardness", 20)

        coord = (tx, ty)
        current = float(self.tile_damage.get(coord, 0.0)) + float(power)
        self.tile_damage[coord] = current
        self.last_damaged_tile = coord
        self.damage_decay_timer = 0

        if current >= max_health:
            del self.tile_damage[coord]
            is_player_placed = (tx, ty) in self.player_placed_tiles
            self.player_placed_tiles.discard((tx, ty))
            drop = prop.get("drop")
            if t_id == TILE_CHEST and (tx, ty) in self.chests:
                broken_chest = self.chests.pop((tx, ty))
                if broken_chest and getattr(broken_chest, "chest_type", None):
                    drop = broken_chest.chest_type

            # Felling only cascades for natural tree trunks or unplaced tree wood, NOT player-placed structures
            if (t_id in (TILE_WOOD_TRUNK, TILE_WOOD)) and not is_player_placed:
                felled_count, leaf_coords = self.fell_tree(tx, ty)
                self.last_felled_tree = (felled_count, leaf_coords)
                return True, "wood", t_id

            self.set_tile(tx, ty, TILE_AIR)
            return True, drop, t_id

        return False, None, t_id

    def place_tile(self, tx, ty, tile_id, chest_type="chest"):
        cur = self.get_tile(tx, ty)
        if cur != TILE_AIR and cur != TILE_WATER:
            return False

        # Adjacency check
        has_neighbor = (self.get_wall(tx, ty) != WALL_AIR)
        for dx, dy in ((-1, 0), (1, 0), (0, -1), (0, 1)):
            if self.get_tile(tx + dx, ty + dy) not in (TILE_AIR, TILE_WATER):
                has_neighbor = True
                break

        if not has_neighbor:
            return False

        placed = self.set_tile(tx, ty, tile_id)
        if placed:
            self.player_placed_tiles.add((tx, ty))
            if tile_id == TILE_CHEST:
                from src.world.storage_chest import StorageChest
                self.chests[(tx, ty)] = StorageChest(tx, ty, chest_type=chest_type)
        return placed

    def toggle_door(self, tx, ty, player_rect=None):
        """Toggles a wooden door between open and closed state without trapping the player."""
        t_id = self.get_tile(tx, ty)
        if t_id == TILE_DOOR_CLOSED:
            self.set_tile(tx, ty, TILE_DOOR_OPEN)
            return True
        elif t_id == TILE_DOOR_OPEN:
            door_rect = pygame.Rect(tx * self.scaled_tile, ty * self.scaled_tile, self.scaled_tile, self.scaled_tile)
            if player_rect and door_rect.colliderect(player_rect):
                return False  # Prevent trapping player inside solid closed door
            self.set_tile(tx, ty, TILE_DOOR_CLOSED)
            return True
        return False

    def place_wall(self, tx, ty, wall_id):
        """Places a background wall at (tx, ty)."""
        if self.get_wall(tx, ty) == wall_id:
            return False
        return self.chunk_manager.set_wall(tx, ty, wall_id)

    def check_house_validity(self, tx, ty, visited_cache=None):
        """Validates if (tx, ty) belongs to a fully sheltered, furnished, and illuminated
        room suitable for a Town NPC to move into.
        Returns: (is_valid, reason, center_x, center_y)"""
        if visited_cache is not None and (tx, ty) in visited_cache:
            return False, "Room already visited and invalid.", None, None

        if self.is_tile_solid(tx, ty):
            if visited_cache is not None:
                visited_cache.add((tx, ty))
            found_air = False
            for dx, dy in [(0, -1), (0, 1), (-1, 0), (1, 0)]:
                if not self.is_tile_solid(tx + dx, ty + dy):
                    tx, ty = tx + dx, ty + dy
                    found_air = True
                    break
            if not found_air:
                return False, "Not an open room interior.", None, None
            if visited_cache is not None and (tx, ty) in visited_cache:
                return False, "Room already visited and invalid.", None, None

        visited = set()
        queue = collections.deque([(tx, ty)])
        visited.add((tx, ty))

        has_door = False
        has_light = False
        has_flat_surface = False
        has_comfort = False
        wall_count = 0
        max_room_tiles = 250
        min_room_tiles = 15

        light_tiles = (TILE_TORCH, TILE_FIREPLACE, TILE_CANDELABRA, TILE_CHANDELIER)
        door_tiles = (TILE_DOOR_CLOSED, TILE_DOOR_OPEN, TILE_WOOD_PLATFORM)
        flat_tiles = (TILE_WORK_BENCH, TILE_TABLE, TILE_BOOKSHELF, TILE_DRESSER)
        comfort_tiles = (TILE_CHAIR, TILE_BED)
        blight_tiles = (TILE_BLIGHTSTONE, TILE_BLIGHT_GRASS, TILE_EBONSTONE, TILE_CORRUPT_GRASS)

        room_tiles = []

        while queue:
            cx, cy = queue.popleft()
            room_tiles.append((cx, cy))
            if len(room_tiles) > max_room_tiles:
                if visited_cache is not None:
                    visited_cache.update(visited)
                return False, "Room is too large or not enclosed.", None, None

            # Fast abort in wide open wilderness: if exploring pure wilderness with no walls and no shelter props
            if len(room_tiles) > 60 and wall_count == 0 and not (has_door or has_light or has_flat_surface or has_comfort):
                if visited_cache is not None:
                    visited_cache.update(visited)
                return False, "Room is too large or not enclosed.", None, None

            if self.get_wall(cx, cy) != 0:
                wall_count += 1

            t_cur = self.get_tile(cx, cy)
            if t_cur in light_tiles:
                has_light = True
            if t_cur in door_tiles:
                has_door = True
            if t_cur in flat_tiles:
                has_flat_surface = True
            if t_cur in comfort_tiles:
                has_comfort = True
            if t_cur in blight_tiles:
                if visited_cache is not None:
                    visited_cache.update(visited)
                return False, "Room is contaminated by Blight.", None, None

            for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                nx, ny = cx + dx, cy + dy
                if (nx, ny) in visited:
                    continue

                ncx = nx // CHUNK_WIDTH
                if not self.has_chunk(ncx):
                    if visited_cache is not None:
                        visited_cache.update(visited)
                    return False, "Room is too large or not enclosed.", None, None

                nt = self.get_tile(nx, ny)
                if nt in blight_tiles:
                    if visited_cache is not None:
                        visited_cache.update(visited)
                    return False, "Room is contaminated by Blight.", None, None

                if nt in door_tiles:
                    has_door = True
                if nt in light_tiles:
                    has_light = True
                if nt in flat_tiles:
                    has_flat_surface = True
                if nt in comfort_tiles:
                    has_comfort = True

                if self.is_tile_solid(nx, ny):
                    continue

                visited.add((nx, ny))
                queue.append((nx, ny))

        if visited_cache is not None:
            visited_cache.update(visited)

        if len(room_tiles) < min_room_tiles:
            return False, f"Room is too small ({len(room_tiles)}/{min_room_tiles} tiles).", None, None

        wall_ratio = wall_count / len(room_tiles)
        if wall_ratio < 0.50:
            return False, f"Room needs background walls ({int(wall_ratio*100)}% / 50%).", None, None

        if not has_door:
            return False, "Room needs an entrance door or wooden platform.", None, None

        if not has_light:
            return False, "Room needs a light source (Torch, Fireplace, or Candelabra).", None, None

        if not has_flat_surface:
            return False, "Room needs a flat surface item (Table, Work Bench, or Dresser).", None, None

        if not has_comfort:
            return False, "Room needs a comfort item (Chair or Bed).", None, None

        avg_x = sum(x for x, y in room_tiles) // len(room_tiles)
        avg_y = sum(y for x, y in room_tiles) // len(room_tiles)

        return True, "Valid shelter suitable for Town NPC!", avg_x, avg_y

    def check_shelter(self, tx, ty, radius=6):
        """Checks if (tx, ty) is part of a valid sheltered house with walls, door, and torch."""
        is_valid, _, _, _ = self.check_house_validity(tx, ty)
        if is_valid:
            return True
        # Fallback check for compatibility with legacy tests
        has_door = False
        has_torch = False
        wall_count = 0
        for dy in range(-radius, radius + 1):
            for dx in range(-radius, radius + 1):
                cur_x = tx + dx
                cur_y = ty + dy
                t = self.get_tile(cur_x, cur_y)
                if t in (TILE_DOOR_CLOSED, TILE_DOOR_OPEN):
                    has_door = True
                if t in (TILE_TORCH, TILE_FIREPLACE, TILE_CANDELABRA, TILE_CHANDELIER):
                    has_torch = True
                if self.get_wall(cur_x, cur_y) != 0:
                    wall_count += 1
        return has_door and has_torch and (wall_count >= 4)

    def check_and_spawn_town_npcs(self, player, inventory, asset_factory, sound_manager, combat=None):
        """Periodically scans surrounding player-built houses and settles eligible Town NPCs."""
        from src.entities.npc import GuideNPC, MerchantNPC, NurseNPC, BlacksmithNPC

        active_types = {npc.npc_type for npc in self.town_npcs}
        occupied_homes = {npc.home_tile for npc in self.town_npcs if npc.home_tile}

        candidates = [
            ("guide", GuideNPC, lambda: True),
            ("merchant", MerchantNPC, lambda: (inventory and (inventory.count_item("copper_coin") >= 25 or inventory.count_item("copper_ore") >= 5)) or getattr(player.stats, "level", 1) >= 2),
            ("nurse", NurseNPC, lambda: player.max_health > 100 or player.health < player.max_health or getattr(combat, "mini_bosses_slain", 0) > 0),
            ("blacksmith", BlacksmithNPC, lambda: (inventory and (inventory.count_item("copper_bar") > 0 or inventory.count_item("iron_bar") > 0)) or getattr(combat, "dungeon_boss_slain", False)),
        ]

        eligible = [
            (c_type, c_cls) for c_type, c_cls, c_cond in candidates
            if c_type not in active_types and c_cond()
        ]
        if not eligible:
            return

        ptx = int(player.center_x // self.scaled_tile)
        pty = int(player.center_y // self.scaled_tile)

        found_home = None
        visited_in_scan = set()

        # Collect candidate comfort furniture positions in range of player.
        # A valid room strictly requires a comfort item (TILE_CHAIR or TILE_BED).
        candidate_tiles = set()
        for fx, fy in list(self.comfort_tiles):
            if abs(fx - ptx) <= 25 and abs(fy - pty) <= 15:
                candidate_tiles.add((fx, fy))

        # Also inspect already loaded chunks around player to catch any untracked comfort items
        min_cx = (ptx - 25) // CHUNK_WIDTH
        max_cx = (ptx + 25) // CHUNK_WIDTH
        for cx in range(min_cx, max_cx + 1):
            chunk = self.chunk_manager.chunks.get(cx)
            if chunk is None:
                continue
            for lx in range(CHUNK_WIDTH):
                gx = cx * CHUNK_WIDTH + lx
                if abs(gx - ptx) > 25:
                    continue
                col_tiles = chunk.tiles[lx]
                min_y = max(0, pty - 15)
                max_y = min(self.height - 1, pty + 15)
                for gy in range(min_y, max_y + 1):
                    if col_tiles[gy] in (TILE_CHAIR, TILE_BED):
                        candidate_tiles.add((gx, gy))
                        self.comfort_tiles.add((gx, gy))

        # Test each comfort furniture anchor (runs in <0.02ms directly inside candidate rooms)
        for fx, fy in candidate_tiles:
            if (fx, fy) not in occupied_homes and (fx, fy) not in visited_in_scan:
                is_valid, _, cx, cy = self.check_house_validity(fx, fy, visited_cache=visited_in_scan)
                if is_valid and (cx, cy) not in occupied_homes:
                    found_home = (cx, cy)
                    break

        c_type, c_cls = eligible[0]

        # If Guide hasn't spawned yet and no house is built yet, spawn near world spawn
        if not found_home and c_type == "guide" and len(self.town_npcs) == 0:
            sp_x, sp_y = self.spawn_point
            found_home = (int(sp_x // self.scaled_tile), int(sp_y // self.scaled_tile) - 1)

        if found_home:
            hx, hy = found_home
            world_x = hx * self.scaled_tile
            world_y = hy * self.scaled_tile
            from src.entities.npc import NPC_TITLES
            name, role_title, _ = NPC_TITLES.get(c_type, ("Spud", "Villager", (255, 255, 255)))
            new_npc = c_cls(name, c_type, world_x, world_y, asset_factory, sound_manager, home_tile=found_home)
            self.town_npcs.append(new_npc)
            occupied_homes.add(found_home)
            active_types.add(c_type)
            if inventory and hasattr(inventory, "notify"):
                inventory.notify(f"{name} the {role_title} has settled in!")
            sound_manager.play("craft")

    def spawn_mystic_trader(self, player, asset_factory=None, sound_manager=None, duration=240.0):
        """Spawns the Mystic Wandering Trader near the player on a safe surface tile."""
        from src.entities.npc import MysticTraderNPC
        from src.constants import SCALED_TILE, TILE_AIR

        ptx = int(player.center_x // self.scaled_tile)
        pty = int(player.center_y // self.scaled_tile)

        found_pos = None
        for dx in (4, -4, 6, -6, 3, -3, 8, -8):
            tx = ptx + dx
            for ty in range(max(10, pty - 10), min(self.height - 10, pty + 10)):
                if self.is_tile_solid(tx, ty) and not self.is_tile_solid(tx, ty - 1) and not self.is_tile_solid(tx, ty - 2):
                    found_pos = (tx * self.scaled_tile, (ty - 1) * self.scaled_tile)
                    break
            if found_pos:
                break

        if not found_pos:
            found_pos = (player.center_x + 64, player.center_y)

        af = asset_factory or self.asset_factory
        sm = sound_manager or self.sound_manager
        trader = MysticTraderNPC(
            name="Zephyrion",
            npc_type="mystic_trader",
            x=found_pos[0],
            y=found_pos[1],
            asset_factory=af,
            sound_manager=sm,
            duration=duration
        )
        self.town_npcs.append(trader)
        if sm:
            sm.play("craft")
        return trader

    def update_town_npcs(self, dt, player, inventory, asset_factory, sound_manager, combat=None):
        """Updates AI for active Town NPCs and Mystic Wandering Trader."""
        # 1. Periodic Mystic Wandering Trader spawn
        self.mystic_trader_timer += dt
        if self.mystic_trader_timer >= self.mystic_trader_interval:
            self.mystic_trader_timer = 0.0
            from src.entities.npc import MysticTraderNPC
            if not any(isinstance(n, MysticTraderNPC) or getattr(n, "npc_type", "") == "mystic_trader" for n in self.town_npcs):
                self.spawn_mystic_trader(player, asset_factory, sound_manager, duration=random.uniform(180.0, 300.0))

        # 2. Check town housing if enabled
        if getattr(self, "town_housing_enabled", False):
            self.housing_check_timer += dt
            if self.housing_check_timer >= 3.5:
                self.housing_check_timer = 0.0
                self.check_and_spawn_town_npcs(player, inventory, asset_factory, sound_manager, combat)

        # 3. Update all active NPCs in town_npcs (including MysticTraderNPC)
        for npc in list(self.town_npcs):
            if hasattr(npc, "update"):
                try:
                    npc.update(dt, self, combat)
                except TypeError:
                    npc.update(dt, self)

    def render_town_npcs(self, target_surf, camera, player=None):
        """Renders Town NPCs and their name badges."""
        housing_enabled = getattr(self, "town_housing_enabled", False)
        for npc in self.town_npcs:
            if not housing_enabled and getattr(npc, "npc_type", "") != "mystic_trader":
                continue
            npc.render(target_surf, camera, player=player)

    def get_npc_at(self, world_x, world_y, radius=45.0):
        """Returns the TownNPC closest to (world_x, world_y) within reach radius, if any."""
        housing_enabled = getattr(self, "town_housing_enabled", False)
        for npc in self.town_npcs:
            if not housing_enabled and getattr(npc, "npc_type", "") != "mystic_trader":
                continue
            if math.hypot(npc.center_x - world_x, npc.center_y - world_y) <= radius:
                return npc
        return None

    def is_tile_solid(self, tx, ty):
        """Returns True if the tile at (tx, ty) is solid."""
        t_id = self.get_tile(tx, ty)
        return TILE_PROPS.get(t_id, {}).get("solid", False)

    def get_solid_rects_in_bounds(self, rect_world_px):
        min_tx = int(rect_world_px.left // self.scaled_tile)
        max_tx = int(rect_world_px.right // self.scaled_tile)
        min_ty = max(0, int(rect_world_px.top // self.scaled_tile))
        max_ty = min(self.height - 1, int(rect_world_px.bottom // self.scaled_tile))

        self.chunk_manager.ensure_chunks_in_range(min_tx, max_tx)

        solids = []
        for tx in range(min_tx, max_tx + 1):
            for ty in range(min_ty, max_ty + 1):
                t_id = self.get_tile(tx, ty)
                prop = TILE_PROPS.get(t_id, {})
                if prop.get("solid", False) or prop.get("platform", False):
                    tile_rect = pygame.Rect(
                        tx * self.scaled_tile,
                        ty * self.scaled_tile,
                        self.scaled_tile,
                        self.scaled_tile
                    )
                    solids.append((tile_rect, prop.get("platform", False)))
        return solids

    def emit_fireplace_smoke(self, particle_system, cam_rect=None):
        """Emits subtle rising smoke and warm embers from active fireplaces."""
        for fx, fy in list(self.fireplaces):
            wx = fx * self.scaled_tile + self.scaled_tile // 2
            wy = fy * self.scaled_tile + 4
            if cam_rect is None or cam_rect.collidepoint(wx, wy):
                if random.random() < 0.25:
                    particle_system.spawn_smoke(wx + random.randint(-4, 4), wy, color=(170, 170, 180), count=1)
                if random.random() < 0.08:
                    particle_system.spawn_sparks(wx + random.randint(-3, 3), wy + 6, color=(255, 140, 40), count=1)

    def render(self, target_surf, camera):
        # Precise integer rounding eliminates any 1px subpixel seams between adjacent blocks/chunks
        cam_x = int(round(camera.x - camera.shake_offset_x))
        cam_y = int(round(camera.y - camera.shake_offset_y))
        sw, sh = target_surf.get_width(), target_surf.get_height()

        min_tx = int(cam_x // self.scaled_tile) - 1
        max_tx = int((cam_x + sw) // self.scaled_tile) + 1
        min_ty = max(0, int(cam_y // self.scaled_tile) - 1)
        max_ty = min(self.height - 1, int((cam_y + sh) // self.scaled_tile) + 1)

        # Stream and ensure chunks in viewport
        self.chunk_manager.ensure_chunks_in_range(min_tx, max_tx)

        min_cx = min_tx // CHUNK_WIDTH
        max_cx = max_tx // CHUNK_WIDTH
        min_sy = max(0, min_ty // SECTION_HEIGHT)
        max_sy = min(NUM_SECTIONS - 1, max(0, max_ty // SECTION_HEIGHT))

        anim_tiles_to_draw = []

        # Batch blit pre-baked 16x16 chunk sections (only 6-9 blits per frame instead of 1200+ tile draws)
        sec_w_px = CHUNK_WIDTH * self.scaled_tile
        sec_h_px = SECTION_HEIGHT * self.scaled_tile

        for cx in range(min_cx, max_cx + 1):
            chunk = self.chunk_manager.get_chunk(cx)
            if chunk is None:
                continue
            chunk_screen_px = cx * sec_w_px - cam_x
            for sy in range(min_sy, max_sy + 1):
                sec = chunk.get_or_bake_section(sy, self)
                sec_screen_py = sy * sec_h_px - cam_y
                if not sec.is_empty:
                    target_surf.blit(sec.surf, (chunk_screen_px, sec_screen_py))
                if sec.animated_tiles:
                    for lpx, lpy, t_id in sec.animated_tiles:
                        anim_tiles_to_draw.append((chunk_screen_px + lpx, sec_screen_py + lpy, cx, sy, lpx, lpy, t_id))

        # Dynamic overlay: animated torches and water
        torch_frame = self.scaled_torch_frames[self.torch_frame_idx] if self.scaled_torch_frames else self.scaled_tiles.get(TILE_TORCH)
        water_frames_len = len(self.scaled_water_frames) if self.scaled_water_frames else 0
        water_sub_len = len(self.scaled_water_submerged) if self.scaled_water_submerged else 0

        for spx, spy, cx, sy, lpx, lpy, t_id in anim_tiles_to_draw:
            if t_id == TILE_TORCH:
                if torch_frame:
                    target_surf.blit(torch_frame, (spx, spy))
            elif t_id == TILE_WATER:
                gx = cx * CHUNK_WIDTH + (lpx // self.scaled_tile)
                gy = sy * SECTION_HEIGHT + (lpy // self.scaled_tile)
                above_id = self.get_tile(gx, gy - 1) if gy > 0 else TILE_AIR
                if above_id == TILE_AIR and water_frames_len > 0:
                    w_tex = self.scaled_water_frames[self.water_frame_idx % water_frames_len]
                elif water_sub_len > 0:
                    w_tex = self.scaled_water_submerged[self.water_frame_idx % water_sub_len]
                else:
                    w_tex = self.scaled_tiles.get(t_id)
                if w_tex:
                    target_surf.blit(w_tex, (spx, spy))

        # Dynamic overlay: mining damage cracks
        if self.tile_damage:
            for (tx, ty), cur in self.tile_damage.items():
                if min_tx <= tx <= max_tx and min_ty <= ty <= max_ty:
                    t_id = self.get_tile(tx, ty)
                    prop = TILE_PROPS.get(t_id, {})
                    max_h = max(1, prop.get("hardness", 20))
                    stage = min(3, int((cur / max_h) * 4))
                    target_surf.blit(self.scaled_cracks[stage], (tx * self.scaled_tile - cam_x, ty * self.scaled_tile - cam_y))
