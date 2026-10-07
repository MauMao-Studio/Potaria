"""
Terraria Pygame - 2D Dynamic Lighting Engine
Computes localized cellular light propagation (sunlight, torches, ambient falloff)
and renders a smooth, interpolated atmospheric shadow mask over the viewport.
"""

import collections
import pygame
from src.constants import MAX_LIGHT, MIN_LIGHT, TILE_PROPS, TILE_TORCH, TILE_FURNACE, WALL_AIR

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
        self.dirty = True

    def compute_viewport_light(self, world, min_tx, min_ty, max_tx, max_ty, ambient_sunlight=15, torch_positions=None, ambient_tint=(1.0, 1.0, 1.0)):
        """
        Calculates 2D light levels for the current camera viewport using BFS propagation.
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

        # 2D light array for the viewport
        # 0 = complete pitch black, 15 = maximum brightness
        light = [[0 for _ in range(grid_h)] for _ in range(grid_w)]
        queue = collections.deque()

        # 1. Inject Sunlight and Tile Emitters
        for lx in range(grid_w):
            tx = min_tx + lx
            
            # Trace downwards from top of viewport for sunlight
            sun_val = ambient_sunlight
            for ly in range(grid_h):
                ty = min_ty + ly
                if not (0 <= ty < world.height):
                    continue

                t_id = world.get_tile(tx, ty)
                w_id = world.get_wall(tx, ty)
                prop = TILE_PROPS.get(t_id, TILE_PROPS[0])
                
                # In open air above ground or exposed to sky
                if w_id == WALL_AIR and not prop["solid"]:
                    if sun_val > light[lx][ly]:
                        light[lx][ly] = sun_val
                        queue.append((lx, ly, sun_val))
                elif prop["solid"]:
                    # Blocks diminish direct sunlight
                    sun_val = max(0, sun_val - prop["absorb"] - 2)
                    if sun_val > light[lx][ly]:
                        light[lx][ly] = sun_val
                        queue.append((lx, ly, sun_val))
                else:
                    # In cave with background walls
                    sun_val = max(0, sun_val - 1)
                    if sun_val > light[lx][ly]:
                        light[lx][ly] = sun_val
                        queue.append((lx, ly, sun_val))

                # Check block intrinsic light emission (e.g. Torches, Furnaces)
                emit = prop["light_emit"]
                if emit > light[lx][ly]:
                    light[lx][ly] = emit
                    queue.append((lx, ly, emit))

        # 2. Inject extra dynamic lights (held torches, projectile glow, etc.)
        if torch_positions:
            for tx, ty, intensity in torch_positions:
                lx = tx - min_tx
                ly = ty - min_ty
                if 0 <= lx < grid_w and 0 <= ly < grid_h:
                    if intensity > light[lx][ly]:
                        light[lx][ly] = intensity
                        queue.append((lx, ly, intensity))

        # 3. BFS Light Diffusion / Propagation
        while queue:
            cx, cy, current_val = queue.popleft()
            if current_val <= 1:
                continue

            for dx, dy in ((-1, 0), (1, 0), (0, -1), (0, 1)):
                nx = cx + dx
                ny = cy + dy
                if 0 <= nx < grid_w and 0 <= ny < grid_h:
                    ntx = min_tx + nx
                    nty = min_ty + ny
                    if 0 <= nty < world.height:
                        t_id = world.get_tile(ntx, nty)
                        absorb = TILE_PROPS.get(t_id, {}).get("absorb", 0)
                        decay = 1 + absorb
                        next_val = current_val - decay
                        if next_val > light[nx][ny]:
                            light[nx][ny] = next_val
                            queue.append((nx, ny, next_val))

        # 4. Bake into Light Mask Surface
        # Resize surface if viewport tile count changed
        if self.light_surf.get_width() != grid_w or self.light_surf.get_height() != grid_h:
            self.light_surf = pygame.Surface((grid_w, grid_h))

        for lx in range(grid_w):
            for ly in range(grid_h):
                val = light[lx][ly]
                # Map 0..15 to brightness (255 = fully lit, 22 = deep cavern ambient)
                brightness = int(22 + (val / 15.0) * 233)
                # Atmospheric color grading tint
                r = min(255, max(12, int(brightness * ambient_tint[0])))
                g = min(255, max(12, int(brightness * ambient_tint[1])))
                b = min(255, max(12, int(brightness * ambient_tint[2])))
                self.light_surf.set_at((lx, ly), (r, g, b))

        self.dirty = True

    def render_lighting(self, target_surf, offset_x, offset_y):
        """
        Scales the low-res light surface up smoothly and multiplies onto target_surf.
        Uses fast BLEND_MULT for real-time hardware-accelerated dark blending!
        """
        scaled_w = self.light_surf.get_width() * self.scaled_tile
        scaled_h = self.light_surf.get_height() * self.scaled_tile
        
        # Smooth bilinear upscale with caching
        if (self.dirty or self.cached_smooth_light is None or
            self.cached_smooth_light.get_width() != scaled_w or
            self.cached_smooth_light.get_height() != scaled_h):
            self.cached_smooth_light = pygame.transform.smoothscale(self.light_surf, (scaled_w, scaled_h))
            self.dirty = False
        target_surf.blit(self.cached_smooth_light, (offset_x, offset_y), special_flags=pygame.BLEND_MULT)
