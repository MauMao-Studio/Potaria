using System;

namespace Potaria.World
{
    /// <summary>
    /// Fast procedural Perlin noise generator with multi-octave fractal synthesis.
    /// Direct C# port of the procedural noise engine in src/world/noise.py.
    /// </summary>
    public class PerlinNoise
    {
        private readonly int[] _p;

        public PerlinNoise(int seed)
        {
            var rng = new Random(seed);
            var baseP = new int[256];
            for (int i = 0; i < 256; i++) baseP[i] = i;

            // Fisher-Yates shuffle matching random.shuffle
            for (int i = 255; i > 0; i--)
            {
                int j = rng.Next(i + 1);
                int temp = baseP[i];
                baseP[i] = baseP[j];
                baseP[j] = temp;
            }

            // Duplicate array to avoid wrapping logic: size 512
            _p = new int[512];
            for (int i = 0; i < 256; i++)
            {
                _p[i] = baseP[i];
                _p[i + 256] = baseP[i];
            }
        }

        private static float Fade(float t)
        {
            return t * t * t * (t * (t * 6f - 15f) + 10f);
        }

        private static float Lerp(float t, float a, float b)
        {
            return a + t * (b - a);
        }

        private static float Grad1D(int hashVal, float x)
        {
            return (hashVal & 1) == 0 ? x : -x;
        }

        private static float Grad2D(int hashVal, float x, float y)
        {
            int h = hashVal & 3;
            float u = h < 2 ? x : y;
            float v = h < 2 ? y : x;
            return ((h & 1) == 0 ? u : -u) + ((h & 2) == 0 ? v : -v);
        }

        public float Noise1D(float x)
        {
            int xi = ((int)Math.Floor(x)) & 255;
            float xf = x - (float)Math.Floor(x);
            float u = Fade(xf);
            return Lerp(u, Grad1D(_p[xi], xf), Grad1D(_p[xi + 1], xf - 1.0f));
        }

        public float Noise2D(float x, float y)
        {
            int xi = ((int)Math.Floor(x)) & 255;
            int yi = ((int)Math.Floor(y)) & 255;
            float xf = x - (float)Math.Floor(x);
            float yf = y - (float)Math.Floor(y);

            float u = Fade(xf);
            float v = Fade(yf);

            int aa = _p[_p[xi] + yi];
            int ab = _p[_p[xi] + yi + 1];
            int ba = _p[_p[xi + 1] + yi];
            int bb = _p[_p[xi + 1] + yi + 1];

            float x1 = Lerp(u, Grad2D(aa, xf, yf), Grad2D(ba, xf - 1f, yf));
            float x2 = Lerp(u, Grad2D(ab, xf, yf - 1f), Grad2D(bb, xf - 1f, yf - 1f));
            return Lerp(v, x1, x2);
        }

        public float Fractal1D(float x, int octaves = 4, float persistence = 0.5f, float lacunarity = 2.0f)
        {
            float total = 0f;
            float frequency = 1f;
            float amplitude = 1f;
            float maxVal = 0f;

            for (int i = 0; i < octaves; i++)
            {
                total += Noise1D(x * frequency) * amplitude;
                maxVal += amplitude;
                amplitude *= persistence;
                frequency *= lacunarity;
            }

            return total / maxVal;
        }

        public float Fractal2D(float x, float y, int octaves = 4, float persistence = 0.5f, float lacunarity = 2.0f)
        {
            float total = 0f;
            float frequency = 1f;
            float amplitude = 1f;
            float maxVal = 0f;

            for (int i = 0; i < octaves; i++)
            {
                total += Noise2D(x * frequency, y * frequency) * amplitude;
                maxVal += amplitude;
                amplitude *= persistence;
                frequency *= lacunarity;
            }

            return total / maxVal;
        }
    }
}
