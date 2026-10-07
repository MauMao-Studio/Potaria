"""
Terraria Pygame - Fast Procedural Noise Module
Pure Python Perlin noise generator with multi-octave fractal synthesis.
"""

import math
import random

class PerlinNoise:
    def __init__(self, seed=None):
        rng = random.Random(seed if seed is not None else 42)
        p = list(range(256))
        rng.shuffle(p)
        self.p = p * 2  # duplicate to avoid wrapping logic

    def _fade(self, t):
        return t * t * t * (t * (t * 6 - 15) + 10)

    def _lerp(self, t, a, b):
        return a + t * (b - a)

    def _grad1d(self, hash_val, x):
        return x if (hash_val & 1) == 0 else -x

    def _grad2d(self, hash_val, x, y):
        h = hash_val & 3
        u = x if h < 2 else y
        v = y if h < 2 else x
        return (u if (h & 1) == 0 else -u) + (v if (h & 2) == 0 else -v)

    def noise1d(self, x):
        xi = int(math.floor(x)) & 255
        xf = x - math.floor(x)
        u = self._fade(xf)
        return self._lerp(u, self._grad1d(self.p[xi], xf), self._grad1d(self.p[xi + 1], xf - 1.0))

    def noise2d(self, x, y):
        xi = int(math.floor(x)) & 255
        yi = int(math.floor(y)) & 255
        xf = x - math.floor(x)
        yf = y - math.floor(y)

        u = self._fade(xf)
        v = self._fade(yf)

        aa = self.p[self.p[xi] + yi]
        ab = self.p[self.p[xi] + yi + 1]
        ba = self.p[self.p[xi + 1] + yi]
        bb = self.p[self.p[xi + 1] + yi + 1]

        x1 = self._lerp(u, self._grad2d(aa, xf, yf), self._grad2d(ba, xf - 1, yf))
        x2 = self._lerp(u, self._grad2d(ab, xf, yf - 1), self._grad2d(bb, xf - 1, yf - 1))
        return self._lerp(v, x1, x2)

    def fractal1d(self, x, octaves=4, persistence=0.5, lacunarity=2.0):
        total = 0.0
        frequency = 1.0
        amplitude = 1.0
        max_val = 0.0
        for _ in range(octaves):
            total += self.noise1d(x * frequency) * amplitude
            max_val += amplitude
            amplitude *= persistence
            frequency *= lacunarity
        return total / max_val

    def fractal2d(self, x, y, octaves=4, persistence=0.5, lacunarity=2.0):
        total = 0.0
        frequency = 1.0
        amplitude = 1.0
        max_val = 0.0
        for _ in range(octaves):
            total += self.noise2d(x * frequency, y * frequency) * amplitude
            max_val += amplitude
            amplitude *= persistence
            frequency *= lacunarity
        return total / max_val
