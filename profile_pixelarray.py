import pygame
import time

pygame.init()
surf = pygame.Surface((1000, 1000))

# Test with tuples
lut_tuple = [(v, v, v) for v in range(16)]
light = [[v % 16 for v in range(1000)] for _ in range(1000)]

start = time.perf_counter()
with pygame.PixelArray(surf) as pixels:
    for lx in range(1000):
        col = light[lx]
        for ly in range(1000):
            pixels[lx, ly] = lut_tuple[col[ly]]
end_tuple = time.perf_counter() - start

# Test with mapped integers
lut_mapped = [surf.map_rgb((v, v, v)) for v in range(16)]
start = time.perf_counter()
with pygame.PixelArray(surf) as pixels:
    for lx in range(1000):
        col = light[lx]
        for ly in range(1000):
            pixels[lx, ly] = lut_mapped[col[ly]]
end_mapped = time.perf_counter() - start

print(f"Tuple assignment: {end_tuple:.4f}s")
print(f"Mapped integer assignment: {end_mapped:.4f}s")
