import time
import pygame

pygame.init()
pygame.display.set_mode((800, 600))
surf = pygame.Surface((44, 26))
target = pygame.Surface((1408, 832))

start = time.perf_counter()
for _ in range(100):
    pygame.transform.smoothscale(surf, (1408, 832), target)
end = time.perf_counter()

print(f"Time for 100 smoothscales: {end - start:.4f}s")
