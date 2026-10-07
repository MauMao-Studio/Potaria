"""
Potaria - Dynamic Radar & HUD Mini-Map
Renders surrounding terrain tiles, player position, party members,
nearby monsters, treasure chests, and active bosses.
Supports HUD corner minimap and expanded map views toggled with [M].
Developer: Kurados
"""

import math
import pygame
from src.constants import (
    SCREEN_WIDTH, SCREEN_HEIGHT, SCALED_TILE, SURFACE_LEVEL,
    UNDERGROUND_LEVEL, COLOR_GOLD, TILE_AIR, TILE_DIRT, TILE_GRASS,
    TILE_STONE, TILE_WOOD, TILE_LEAVES, TILE_WOOD_TRUNK, TILE_COPPER_ORE,
    TILE_IRON_ORE, TILE_GOLD_ORE, TILE_WOOD_PLATFORM, TILE_WORK_BENCH,
    TILE_FURNACE, TILE_TORCH, TILE_STONE_BRICK, TILE_DUNGEON_BRICK,
    TILE_DUNGEON_ALTAR, TILE_SAND, TILE_SANDSTONE, TILE_CACTUS,
    TILE_SNOW, TILE_ICE, TILE_CORRUPT_GRASS, TILE_EBONSTONE,
    TILE_MUSHROOM_GRASS, TILE_MUSHROOM_CAP, TILE_CHEST,
    TILE_ROOF_TILES, TILE_WOOD_PLANKS, TILE_GLASS, TILE_DOOR_CLOSED,
    TILE_DOOR_OPEN, TILE_TABLE, TILE_CHAIR, TILE_BEDROCK,
    TILE_BED, TILE_BOOKSHELF, TILE_GRANDFATHER_CLOCK, TILE_FIREPLACE,
    TILE_CANDELABRA, TILE_CHANDELIER, TILE_POTTED_PLANT, TILE_DRESSER,
    TILE_TAPESTRY, TILE_BATHTUB, TILE_SINK, TILE_PAINTING, TILE_WOOD_SHELF,
    WALL_AIR
)

TILE_MAP_COLORS = {
    TILE_DIRT: (140, 95, 55),
    TILE_GRASS: (65, 175, 50),
    TILE_STONE: (115, 115, 115),
    TILE_WOOD: (150, 100, 50),
    TILE_WOOD_TRUNK: (120, 80, 45),
    TILE_LEAVES: (50, 140, 40),
    TILE_COPPER_ORE: (215, 115, 40),
    TILE_IRON_ORE: (195, 200, 210),
    TILE_GOLD_ORE: (255, 215, 0),
    TILE_WOOD_PLATFORM: (170, 120, 60),
    TILE_WORK_BENCH: (180, 130, 70),
    TILE_FURNACE: (160, 60, 40),
    TILE_TORCH: (255, 200, 60),
    TILE_STONE_BRICK: (140, 140, 150),
    TILE_DUNGEON_BRICK: (95, 45, 140),
    TILE_DUNGEON_ALTAR: (160, 40, 180),
    TILE_SAND: (225, 200, 130),
    TILE_SANDSTONE: (190, 160, 95),
    TILE_CACTUS: (80, 160, 50),
    TILE_SNOW: (230, 240, 252),
    TILE_ICE: (140, 210, 245),
    TILE_CORRUPT_GRASS: (130, 60, 160),
    TILE_EBONSTONE: (75, 55, 95),
    TILE_MUSHROOM_GRASS: (60, 150, 230),
    TILE_MUSHROOM_CAP: (30, 120, 240),
    TILE_CHEST: (255, 215, 0),
    TILE_ROOF_TILES: (175, 65, 45),
    TILE_WOOD_PLANKS: (185, 135, 75),
    TILE_GLASS: (180, 225, 245),
    TILE_DOOR_CLOSED: (140, 90, 50),
    TILE_DOOR_OPEN: (120, 75, 40),
    TILE_TABLE: (150, 100, 50),
    TILE_CHAIR: (140, 90, 45),
    TILE_BEDROCK: (25, 25, 25),
    TILE_BED: (180, 100, 70),
    TILE_BOOKSHELF: (130, 85, 45),
    TILE_GRANDFATHER_CLOCK: (160, 120, 60),
    TILE_FIREPLACE: (180, 80, 50),
    TILE_CANDELABRA: (255, 215, 80),
    TILE_CHANDELIER: (255, 225, 100),
    TILE_POTTED_PLANT: (60, 160, 60),
    TILE_DRESSER: (140, 95, 50),
    TILE_TAPESTRY: (160, 60, 70),
    TILE_BATHTUB: (210, 225, 240),
    TILE_SINK: (190, 200, 210),
    TILE_PAINTING: (180, 150, 90),
    TILE_WOOD_SHELF: (170, 120, 60),
}

class MiniMap:
    def __init__(self):
        self.is_open = True
        self.mode = "corner" # "corner", "large", "hidden"
        
        # Buffer dimensions in tiles
        self.grid_w = 64
        self.grid_h = 44
        self.map_surf = pygame.Surface((self.grid_w, self.grid_h))

        # High-performance caching for 60 FPS stability
        self._cached_min_tx = None
        self._cached_min_ty = None
        self._cached_chests = []
        self._dirty = True

        pygame.font.init()
        self.font = pygame.font.SysFont("Arial", 11, bold=True)
        self.font_sm = pygame.font.SysFont("Arial", 9)

    def mark_dirty(self):
        """Forces minimap terrain to re-bake on next render."""
        self._dirty = True

    def toggle(self):
        """Cycles between Corner Minimap -> Large Map -> Hidden."""
        if self.mode == "corner":
            self.mode = "large"
            self.is_open = True
            self._dirty = True
        elif self.mode == "large":
            self.mode = "hidden"
            self.is_open = False
        else:
            self.mode = "corner"
            self.is_open = True
            self._dirty = True

    def render(self, target_surf, world, player, combat, lan_client=None):
        if not self.is_open or self.mode == "hidden":
            return

        ptx = int(player.center_x // SCALED_TILE)
        pty = int(player.center_y // SCALED_TILE)

        min_tx = ptx - self.grid_w // 2
        min_ty = pty - self.grid_h // 2

        needs_rebuild = (self._dirty or
                         self._cached_min_tx != min_tx or
                         self._cached_min_ty != min_ty)

        # 1. Bake terrain scan to map surface (Cached: only rebuilds when player crosses tile or world changes)
        if needs_rebuild:
            self._cached_min_tx = min_tx
            self._cached_min_ty = min_ty
            self._cached_chests = []
            self._dirty = False

            for lx in range(self.grid_w):
                tx = min_tx + lx
                for ly in range(self.grid_h):
                    ty = min_ty + ly
                    if ty < 0:
                        self.map_surf.set_at((lx, ly), (110, 180, 245)) # Sky
                        continue
                    if ty >= world.height:
                        self.map_surf.set_at((lx, ly), (20, 20, 20)) # Deep Bedrock
                        continue

                    t_id = world.get_tile(tx, ty)
                    if t_id == TILE_AIR:
                        w_id = world.get_wall(tx, ty)
                        surf_y = world.get_surface_height(tx) if hasattr(world, "get_surface_height") else SURFACE_LEVEL
                        if w_id != WALL_AIR:
                            self.map_surf.set_at((lx, ly), (45, 38, 32))
                        elif ty >= surf_y or ty >= SURFACE_LEVEL:
                            self.map_surf.set_at((lx, ly), (32, 28, 25)) # Cavern air
                        else:
                            self.map_surf.set_at((lx, ly), (110, 180, 245)) # Open sky
                    else:
                        if t_id == TILE_CHEST:
                            self._cached_chests.append((tx, ty))
                        col = TILE_MAP_COLORS.get(t_id, (100, 100, 100))
                        self.map_surf.set_at((lx, ly), col)

        # 2. Setup Screen Positioning
        if self.mode == "large":
            mw, mh = 420, 290
            mx = SCREEN_WIDTH // 2 - mw // 2
            my = SCREEN_HEIGHT // 2 - mh // 2
        else: # "corner"
            mw, mh = 148, 108
            mx = SCREEN_WIDTH - mw - 16
            my = 16

        # Draw map backing and frame
        frame_rect = pygame.Rect(mx, my, mw, mh)
        pygame.draw.rect(target_surf, (20, 24, 38, 240), frame_rect, border_radius=6)
        
        # Scale pixel buffer up to window (Cached: only re-scale when terrain rebuilds or mode changes)
        inner_w = mw - 8
        inner_h = mh - 22
        if (getattr(self, "_cached_scaled_map", None) is None or
            needs_rebuild or
            self._cached_scaled_map.get_width() != inner_w or
            self._cached_scaled_map.get_height() != inner_h):
            self._cached_scaled_map = pygame.transform.scale(self.map_surf, (inner_w, inner_h))
        target_surf.blit(self._cached_scaled_map, (mx + 4, my + 18))

        # Golden boundary & title
        pygame.draw.rect(target_surf, COLOR_GOLD, frame_rect, 2, border_radius=6)
        
        if getattr(self, "_cached_hdr_mode", None) != self.mode:
            title_txt = "RADAR MAP [M]" if self.mode == "corner" else "WORLD OVERVIEW MAP [M]"
            self._cached_hdr = self.font.render(title_txt, True, (255, 230, 100))
            self._cached_hdr_mode = self.mode
        target_surf.blit(self._cached_hdr, (mx + 6, my + 3))

        # Helper: world coordinates to minimap screen coordinates
        def world_to_map(wx, wy):
            fx = (wx / SCALED_TILE - min_tx) / float(self.grid_w)
            fy = (wy / SCALED_TILE - min_ty) / float(self.grid_h)
            px = mx + 4 + int(fx * inner_w)
            py = my + 18 + int(fy * inner_h)
            return px, py

        # 3. Blips: Chests (drawn from cached list without scanning 2,816 tiles!)
        for tx, ty in self._cached_chests:
            cx, cy = world_to_map((tx + 0.5) * SCALED_TILE, (ty + 0.5) * SCALED_TILE)
            if mx + 4 <= cx <= mx + 4 + inner_w and my + 18 <= cy <= my + 18 + inner_h:
                pygame.draw.rect(target_surf, (255, 220, 0), (cx - 2, cy - 2, 4, 4))

        # 4. Blips: Regular Mobs (Red dots)
        for mob in combat.mobs:
            if mob.is_alive:
                bx, by = world_to_map(mob.center_x, mob.center_y)
                if mx + 4 <= bx <= mx + 4 + inner_w and my + 18 <= by <= my + 18 + inner_h:
                    pygame.draw.circle(target_surf, (255, 50, 50), (bx, by), 2)

        # 5. Blips: Remote LAN Party Members (Cyan dots with names)
        if lan_client and (lan_client.connected or lan_client.remote_players):
            for pid, pinfo in lan_client.remote_players.items():
                r_wx = pinfo.get("x", 0.0) + 14
                r_wy = pinfo.get("y", 0.0) + 18
                rx, ry = world_to_map(r_wx, r_wy)
                if mx + 4 <= rx <= mx + 4 + inner_w and my + 18 <= ry <= my + 18 + inner_h:
                    pygame.draw.circle(target_surf, (50, 220, 255), (rx, ry), 3)
                    pname = pinfo.get("name", f"P{pid}")[:4]
                    plbl = self.font_sm.render(pname, True, (180, 240, 255))
                    target_surf.blit(plbl, (rx - plbl.get_width() // 2, ry - 10))

        # 6. Blips: Boss (Large pulsing marker + "BOSS" text)
        if combat.boss and not combat.boss.is_dead:
            bx, by = world_to_map(combat.boss.center_x, combat.boss.center_y)
            # Clamp to map rect with warning arrow if outside
            clamped_bx = max(mx + 8, min(mx + inner_w, bx))
            clamped_by = max(my + 22, min(my + inner_h + 10, by))
            
            ticks = pygame.time.get_ticks()
            pulse = int(4 + math.sin(ticks * 0.008) * 2)
            pygame.draw.circle(target_surf, (255, 20, 60), (clamped_bx, clamped_by), pulse + 1)
            pygame.draw.circle(target_surf, (255, 230, 80), (clamped_bx, clamped_by), 2)
            boss_lbl = self.font.render("BOSS", True, (255, 50, 50))
            target_surf.blit(boss_lbl, (clamped_bx - boss_lbl.get_width() // 2, clamped_by - 12))

        # 7. Player Blip (Bright green/white pulsing indicator)
        px, py = world_to_map(player.center_x, player.center_y)
        if mx + 4 <= px <= mx + 4 + inner_w and my + 18 <= py <= my + 18 + inner_h:
            t_ms = pygame.time.get_ticks()
            pulse_rad = 3 + int((math.sin(t_ms * 0.006) + 1.0) * 1.5)
            pygame.draw.circle(target_surf, (255, 255, 255), (px, py), pulse_rad, 1)
            pygame.draw.circle(target_surf, (80, 255, 100), (px, py), 3)
            # Facing notch
            notch_x = px + (4 if player.facing_right else -4)
            pygame.draw.line(target_surf, (255, 255, 255), (px, py), (notch_x, py), 2)
