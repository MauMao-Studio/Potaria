"""
Terraria Pygame - Particle & Debris System
Handles high-performance visual particles: block digging debris,
blood/slime splashes, weapon slash sparks, and smoke.
"""

import math
import random
import pygame
from src.constants import GRAVITY

class Particle:
    def __init__(self, x, y, vx, vy, color, size=3, life=0.4, gravity=True):
        self.x = float(x)
        self.y = float(y)
        self.vx = float(vx)
        self.vy = float(vy)
        self.color = color
        self.size = size
        self.life = life
        self.max_life = life
        self.gravity = gravity

    def update(self, dt):
        self.life -= dt
        if self.gravity:
            self.vy += GRAVITY * 0.7
        self.x += self.vx
        self.y += self.vy

    def render(self, target_surf, camera):
        if self.life <= 0:
            return
        sx, sy = camera.world_to_screen(self.x, self.y)
        # Fade size slightly towards end of life
        cur_size = max(1, int(self.size * (self.life / self.max_life)))
        pygame.draw.rect(target_surf, self.color, (int(sx), int(sy), cur_size, cur_size))

class ParticleSystem:
    def __init__(self, max_particles=250):
        self.particles = []
        self.max_particles = max_particles
        self.rng = random.Random()

    def spawn_debris(self, world_x, world_y, color, count=8):
        """Spawns digging block debris fragments."""
        rng = self.rng
        for _ in range(count):
            angle = rng.uniform(0, math.pi * 2)
            speed = rng.uniform(1.5, 4.5)
            vx = math.cos(angle) * speed
            vy = math.sin(angle) * speed - 2.0
            size = rng.choice([2, 3, 4])
            life = rng.uniform(0.3, 0.6)
            self.particles.append(Particle(world_x, world_y, vx, vy, color, size, life))
        if len(self.particles) > self.max_particles:
            self.particles = self.particles[-self.max_particles:]

    def spawn_sparks(self, world_x, world_y, color=(255, 230, 100), count=6):
        """Spawns combat sparks or critical hit stars."""
        rng = self.rng
        for _ in range(count):
            vx = rng.uniform(-3.5, 3.5)
            vy = rng.uniform(-4.5, -1.0)
            self.particles.append(Particle(world_x, world_y, vx, vy, color, size=2, life=0.3))
        if len(self.particles) > self.max_particles:
            self.particles = self.particles[-self.max_particles:]

    def spawn_bubbles(self, world_x, world_y, count=3):
        """Spawns rising underwater oxygen bubbles."""
        rng = self.rng
        for _ in range(count):
            vx = rng.uniform(-0.6, 0.6)
            vy = rng.uniform(-2.0, -0.6)
            size = rng.choice([2, 3])
            life = rng.uniform(0.4, 0.8)
            self.particles.append(Particle(world_x, world_y, vx, vy, (180, 235, 255), size=size, life=life, gravity=False))
        if len(self.particles) > self.max_particles:
            self.particles = self.particles[-self.max_particles:]

    def spawn_smoke(self, world_x, world_y, color=(160, 160, 170), count=2):
        """Spawns gentle rising smoke or fireplace chimney puffs."""
        rng = self.rng
        for _ in range(count):
            vx = rng.uniform(-0.5, 0.5)
            vy = rng.uniform(-1.8, -0.7)
            size = rng.choice([2, 3, 4])
            life = rng.uniform(0.6, 1.2)
            self.particles.append(Particle(world_x, world_y, vx, vy, color, size=size, life=life, gravity=False))
        if len(self.particles) > self.max_particles:
            self.particles = self.particles[-self.max_particles:]

    def update(self, dt):
        for p in self.particles:
            p.update(dt)
        self.particles = [p for p in self.particles if p.life > 0]
        if len(self.particles) > self.max_particles:
            self.particles = self.particles[-self.max_particles:]

    def render(self, target_surf, camera):
        for p in self.particles:
            p.render(target_surf, camera)
