import time
import pygame
from src.world.world import World
from src.world.lighting import LightingEngine
from src.assets.asset_factory import AssetFactory

pygame.init()
pygame.display.set_mode((800, 600))
asset_factory = AssetFactory()
world = World(asset_factory, seed=123)

lighting = LightingEngine(1280, 720)

world.chunk_manager.ensure_chunks_in_range(-5, 5)

start = time.perf_counter()
for _ in range(100):
    lighting.dirty = True
    lighting.compute_viewport_light(world, -10, 30, 30, 60, ambient_sunlight=15)
end = time.perf_counter()

print(f"Time for 100 lighting updates: {end - start:.4f}s")
