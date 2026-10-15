"""
Terraria Pygame - 2D Dynamic Lighting Engine
Computes localized cellular light propagation (sunlight, torches, ambient falloff)
and renders a smooth, interpolated atmospheric shadow mask over the viewport.
"""

import collections
import pygame
from src.constants import MAX_LIGHT, MIN_LIGHT, TILE_PROPS, TILE_TORCH, TILE_FURNACE, WALL_AIR, TILE_AIR

class LightingEngine:
    def __init__(self, screen_width, screen_height, tile_size=16, scale=2):
        self.tile_size = tile_size
        self.scale = scale
        self.scaled_tile = tile_size * scale
        self.screen_width = screen_width
        self.screen_height = screen_height
        
        # Dimensions for viewport light map
        self.view_tiles_x = (screen_width // self.scaled_tile) + 4
        self.view_tiles_y = (screen_height // self.scaled_tile) + 4
        
        # Low-resolution light surface for smooth scaling
        self.light_surf = pygame.Surface((self.view_tiles_x, self.view_tiles_y))
        self.cached_smooth_light = None
        self._dirty = True
        self._render_dirty = True

        # State tracking for skipping redundant BFS & smoothscale passes
        self._last_min_tx = None
        self._last_min_ty = None
        self._last_max_tx = None
        self._last_max_ty = None
        self._last_sun_val = None
        self._last_torch_keys = None
        self._last_tint_key = None
        self._last_light_grid = None

        # Precomputed Euclidean radial falloff patterns
        self._radial_cache = {}

        # Telemetry
        self.rebuild_count = 0
        self.reuse_count = 0

    @property
    def dirty(self):
        return self._dirty or self._render_dirty

    @dirty.setter
    def dirty(self, val):
        self._dirty = bool(val)
        if val:
            self._render_dirty = True

    def _get_radial_offsets(self, intensity, radius):
        key = (intensity, radius)
        if key in self._radial_cache:
            return self._radial_cache[key]
        r_sq = radius * radius
        offsets = []
        for dx in range(-radius, radius + 1):
            dx_sq = dx * dx
            for dy in range(-radius, radius + 1):
                d_sq = dx_sq + dy * dy
                if d_sq <= r_sq:
                    val = int(round(intensity * (1.0 - (d_sq / r_sq))))
                    if val > 0:
                        offsets.append((dx, dy, val))
        self._radial_cache[key] = offsets
        return offsets

    def compute_viewport_light(self, world, min_tx, min_ty, max_tx, max_ty, ambient_sunlight=15, torch_positions=None, ambient_tint=(1.0, 1.0, 1.0)):
        """
        Calculates 2D light levels for the current camera viewport using direct column tracing and BFS propagation.
        Args:
            world: World object containing foreground tiles and background walls
            min_tx, min_ty: Top-left tile coordinates
            max_tx, max_ty: Bottom-right tile coordinates
            ambient_sunlight: Sky light intensity (0 at midnight, 15 at noon)
            torch_positions: List of (tx, ty, intensity) for extra dynamic light emitters
            ambient_tint: RGB color multipliers for atmospheric tinting (dawn/dusk amber, night sapphire, dungeon violet)
        """
        grid_w = max_tx - min_tx + 1
        grid_h = max_ty - min_ty + 1
        if grid_w <= 0 or grid_h <= 0:
            return

        sun_val = int(round(ambient_sunlight))
        torch_keys = tuple(torch_positions) if torch_positions else ()
        tint_r, tint_g, tint_b = ambient_tint
        tint_key = (round(tint_r, 2), round(tint_g, 2), round(tint_b, 2))

        grid_changed = (
            self._dirty or
            self._last_light_grid is None or
            min_tx != self._last_min_tx or
            min_ty != self._last_min_ty or
            max_tx != self._last_max_tx or
            max_ty != self._last_max_ty or
            sun_val != self._last_sun_val or
            torch_keys != self._last_torch_keys
        )

        tint_changed = (tint_key != self._last_tint_key)

        if not grid_changed and not tint_changed:
            self.reuse_count += 1
            return

        self._last_min_tx = min_tx
        self._last_min_ty = min_ty
        self._last_max_tx = max_tx
        self._last_max_ty = max_ty
        self._last_sun_val = sun_val
        self._last_torch_keys = torch_keys
        self._last_tint_key = tint_key

        if grid_changed:
            self.rebuild_count += 1
            light = [[0 for _ in range(grid_h)] for _ in range(grid_w)]
            absorb_grid = [[0 for _ in range(grid_h)] for _ in range(grid_w)]
            queue = collections.deque()
            emitters = []

            cm = getattr(world, "chunk_manager", None)
            world_height = getattr(world, "height", 240)

            # 1. Direct Sunlight Downward Trace & Tile Emitters
            for lx in range(grid_w):
                tx = min_tx + lx
                col_sun = sun_val
                
                # Check occlusion above viewport if underground
                if col_sun > 0 and hasattr(world, "get_surface_height"):
                    surf_y = world.get_surface_height(tx)
                    if min_ty > surf_y:
                        start_y = max(0, surf_y)
                        for check_y in range(start_y, min_ty):
                            t_id = world.get_tile(tx, check_y)
                            if t_id != TILE_AIR:
                                prop = TILE_PROPS.get(t_id, TILE_PROPS[0])
                                if prop.get("solid", False):
                                    col_sun = max(0, col_sun - prop.get("absorb", 0) - 2)
                                    if col_sun <= 0:
                                        break
                            else:
                                w_id = world.get_wall(tx, check_y)
                                if w_id != WALL_AIR:
                                    col_sun = max(0, col_sun - 1)
                                    if col_sun <= 0:
                                        break

                cur_sun = col_sun

                # Fast hoisted column access if chunk manager is present
                chunk = None
                tiles_col = None
                walls_col = None
                if cm:
                    cx = tx // 16
                    local_x = tx % 16
                    chunk = cm.get_chunk(cx)
                    if chunk:
                        tiles_col = chunk.tiles[local_x] if hasattr(chunk, "tiles") else None
                        walls_col = chunk.walls[local_x] if hasattr(chunk, "walls") else None

                for ly in range(grid_h):
                    ty = min_ty + ly
                    if ty < 0:
                        light[lx][ly] = cur_sun
                        continue
                    if not (0 <= ty < world_height):
                        continue

                    if tiles_col is not None and walls_col is not None and 0 <= ty < len(tiles_col):
                        t_id = tiles_col[ty]
                        w_id = walls_col[ty]
                    else:
                        t_id = world.get_tile(tx, ty)
                        w_id = world.get_wall(tx, ty)

                    prop = TILE_PROPS.get(t_id, TILE_PROPS[0])
                    absorb = prop.get("absorb", 0)
                    absorb_grid[lx][ly] = absorb
                    is_solid = prop.get("solid", False)

                    if w_id == WALL_AIR and not is_solid:
                        if cur_sun > light[lx][ly]:
                            light[lx][ly] = cur_sun
                            queue.append((lx, ly, cur_sun))
                    elif is_solid:
                        # Top surface exposed to sky receives incident daylight before absorption
                        if cur_sun > light[lx][ly]:
                            light[lx][ly] = cur_sun
                        cur_sun = max(0, cur_sun - absorb - 2)
                        if cur_sun > 0:
                            queue.append((lx, ly, cur_sun))
                    else:
                        cur_sun = max(0, cur_sun - 1)
                        if cur_sun > light[lx][ly]:
                            light[lx][ly] = cur_sun
                            queue.append((lx, ly, cur_sun))

                    # Check block intrinsic light emission
                    emit = prop.get("light_emit", 0)
                    if emit > 0:
                        rad = prop.get("light_radius") or emit
                        emitters.append((lx, ly, emit, rad, True))

            # 2. Inject extra dynamic lights (held torches, projectile glow, etc.)
            if torch_positions:
                for item in torch_positions:
                    if len(item) == 3:
                        tx, ty, intensity = item
                        rad = max(4, intensity - 2)
                        cast_shadow = False
                    elif len(item) == 4:
                        tx, ty, intensity, rad = item
                        cast_shadow = False
                    else:
                        tx, ty, intensity, rad, cast_shadow = item[:5]
                    lx = tx - min_tx
                    ly = ty - min_ty
                    if 0 <= lx < grid_w and 0 <= ly < grid_h:
                        emitters.append((lx, ly, intensity, rad, cast_shadow))

            # 3. BFS Light Diffusion / Propagation for Sunlight
            while queue:
                cx, cy, current_val = queue.popleft()
                if current_val <= 1:
                    continue

                for dx, dy in ((-1, 0), (1, 0), (0, -1), (0, 1)):
                    nx = cx + dx
                    ny = cy + dy
                    if 0 <= nx < grid_w and 0 <= ny < grid_h:
                        decay = 1 + absorb_grid[nx][ny]
                        next_val = current_val - decay
                        if next_val > light[nx][ny]:
                            light[nx][ny] = next_val
                            queue.append((nx, ny, next_val))

            # 4. Smooth Radial Circular Quadratic Falloff for Localized Light Emitters
            for ex, ey, intensity, radius, cast_shadow in emitters:
                if not cast_shadow:
                    offsets = self._get_radial_offsets(intensity, radius)
                    for dx, dy, val in offsets:
                        nx = ex + dx
                        ny = ey + dy
                        if 0 <= nx < grid_w and 0 <= ny < grid_h and val > light[nx][ny]:
                            light[nx][ny] = val
                else:
                    r_sq = radius * radius
                    min_x = max(0, ex - radius)
                    max_x = min(grid_w - 1, ex + radius)
                    min_y = max(0, ey - radius)
                    max_y = min(grid_h - 1, ey + radius)
                    for x in range(min_x, max_x + 1):
                        dx = x - ex
                        dx_sq = dx * dx
                        for y in range(min_y, max_y + 1):
                            dy = y - ey
                            d_sq = dx_sq + dy * dy
                            if d_sq <= r_sq:
                                val = int(round(intensity * (1.0 - (d_sq / r_sq))))
                                if val > light[x][y]:
                                    steps = max(abs(dx), abs(dy))
                                    if steps > 1:
                                        drop = 0
                                        for s in range(1, steps):
                                            rx = ex + int(round(dx * s / steps))
                                            ry = ey + int(round(dy * s / steps))
                                            if absorb_grid[rx][ry] > 0:
                                                drop += (absorb_grid[rx][ry] + 1) * 2
                                                if drop >= val:
                                                    break
                                        val = max(0, val - drop)
                                    if val > light[x][y]:
                                        light[x][y] = val

            self._last_light_grid = light
            self._dirty = False

        # 5. Bake into Light Mask Surface
        if self.light_surf.get_width() != grid_w or self.light_surf.get_height() != grid_h:
            self.light_surf = pygame.Surface((grid_w, grid_h))

        # Precompute 16-level RGB LUT for atmospheric tinting
        lut = [
            self.light_surf.map_rgb((
                min(255, max(12, int((22 + (v / 15.0) * 233) * tint_r))),
                min(255, max(12, int((22 + (v / 15.0) * 233) * tint_g))),
                min(255, max(12, int((22 + (v / 15.0) * 233) * tint_b))),
            ))
            for v in range(16)
        ]

        with pygame.PixelArray(self.light_surf) as pixels:
            for lx in range(grid_w):
                col = self._last_light_grid[lx]
                for ly in range(grid_h):
                    pixels[lx, ly] = lut[col[ly]]

        self._render_dirty = True

    def get_light_level(self, tx, ty):
        """Returns the computed light intensity level [0..15] for world tile (tx, ty)."""
        if self._last_light_grid and self._last_min_tx is not None and self._last_min_ty is not None:
            lx = tx - self._last_min_tx
            ly = ty - self._last_min_ty
            if 0 <= lx < len(self._last_light_grid) and 0 <= ly < len(self._last_light_grid[0]):
                return self._last_light_grid[lx][ly]
        return 0

    def render_lighting(self, target_surf, offset_x, offset_y):
        """
        Scales the low-res light surface up smoothly and multiplies onto target_surf.
        Uses fast BLEND_MULT for real-time hardware-accelerated dark blending!
        """
        scaled_w = self.light_surf.get_width() * self.scaled_tile
        scaled_h = self.light_surf.get_height() * self.scaled_tile
        
        # Smooth bilinear upscale with caching and pre-allocated destination surface
        if (self._render_dirty or self.cached_smooth_light is None or
            self.cached_smooth_light.get_width() != scaled_w or
            self.cached_smooth_light.get_height() != scaled_h):
            if (self.cached_smooth_light is None or
                self.cached_smooth_light.get_width() != scaled_w or
                self.cached_smooth_light.get_height() != scaled_h):
                self.cached_smooth_light = pygame.Surface((scaled_w, scaled_h))
            pygame.transform.smoothscale(self.light_surf, (scaled_w, scaled_h), self.cached_smooth_light)
            self._render_dirty = False
            self._dirty = False
        target_surf.blit(self.cached_smooth_light, (offset_x, offset_y), special_flags=pygame.BLEND_MULT)
