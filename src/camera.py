"""
Potaria - Smooth Tracking Camera (Infinite World)
Handles viewport scrolling for an infinite horizontal open world,
vertical boundary clamping, screen shake, and coordinate conversions.
Developer: Kurados
"""

import math
import random
import pygame
from src.constants import SCREEN_WIDTH, SCREEN_HEIGHT, SCALED_TILE
from src.world.chunk_manager import CHUNK_HEIGHT, SKY_MIN_Y

class Camera:
    def __init__(self, screen_width=SCREEN_WIDTH, screen_height=SCREEN_HEIGHT):
        self.x = 0.0
        self.y = 0.0
        self.screen_width = screen_width
        self.screen_height = screen_height
        
        self.world_min_y = SKY_MIN_Y * SCALED_TILE
        self.world_max_y = CHUNK_HEIGHT * SCALED_TILE - self.screen_height

        # Screen shake
        self.shake_enabled = True
        self.shake_time = 0.0
        self.shake_intensity = 0.0
        self.shake_offset_x = 0.0
        self.shake_offset_y = 0.0

    @property
    def offset_x(self):
        return self.x

    @property
    def offset_y(self):
        return self.y

    def set_target(self, target_px_x, target_px_y, instant=False):
        dest_x = target_px_x - self.screen_width / 2.0
        dest_y = target_px_y - self.screen_height / 2.0

        # Vertical clamp allows soaring into celestial space stratum down to world_min_y
        dest_y = max(self.world_min_y, min(self.world_max_y, dest_y))

        if instant:
            self.x = dest_x
            self.y = dest_y
        else:
            self.x += (dest_x - self.x) * 0.14
            self.y += (dest_y - self.y) * 0.14

    def add_shake(self, intensity=4.0, duration=0.2):
        if not self.shake_enabled:
            return
        self.shake_intensity = intensity
        self.shake_time = duration

    def update(self, dt):
        if self.shake_time > 0:
            self.shake_time -= dt
            self.shake_offset_x = random.uniform(-self.shake_intensity, self.shake_intensity)
            self.shake_offset_y = random.uniform(-self.shake_intensity, self.shake_intensity)
        else:
            self.shake_offset_x = 0.0
            self.shake_offset_y = 0.0

    def screen_to_world(self, sx, sy):
        return (sx + self.x - self.shake_offset_x, sy + self.y - self.shake_offset_y)

    def world_to_screen(self, wx, wy):
        return (wx - self.x + self.shake_offset_x, wy - self.y + self.shake_offset_y)

    def screen_to_tile(self, sx, sy):
        wx, wy = self.screen_to_world(sx, sy)
        return (int(math.floor(wx / SCALED_TILE)), int(math.floor(wy / SCALED_TILE)))
