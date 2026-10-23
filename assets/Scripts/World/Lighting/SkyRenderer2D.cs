using System;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.Rendering.Universal;

namespace Potaria.World.Lighting
{
    /// <summary>
    /// Procedural 2D Day/Night Sky & Starfield Renderer for Potaria.
    /// Ported directly from Pygame reference (src/environment/sky.py & sky_presets.py):
    /// - Continuous Hermite cubic day/night sky gradient (Dawn, Noon, Sunset, Dusk, Night)
    /// - 140 individual twinkling pixel stars that seamlessly fade in during Night
    /// - Automatic camera clear color synchronization
    /// - Subterranean cavern dimming when descending below surface stratum
    /// </summary>
    public class SkyRenderer2D : MonoBehaviour
    {
        [Header("References")]
        [SerializeField] private DayNightCycle2D dayNightCycle;
        [SerializeField] private UnityEngine.Camera targetCamera;

        [Header("Starfield Knobs")]
        [SerializeField] private int starCount = 140;
        [SerializeField] private float starTwinkleSpeed = 3.5f;

        // Core sky palette matching authentic Pygame engine (src/environment/sky_presets.py)
        private static readonly Color NightTop = new Color(12f / 255f, 18f / 255f, 35f / 255f, 1f);
        private static readonly Color NightBot = new Color(25f / 255f, 40f / 255f, 65f / 255f, 1f);

        private static readonly Color DawnTop = new Color(60f / 255f, 50f / 255f, 90f / 255f, 1f);
        private static readonly Color DawnBot = new Color(245f / 255f, 155f / 255f, 110f / 255f, 1f);

        private static readonly Color DayTop = new Color(115f / 255f, 175f / 255f, 195f / 255f, 1f);
        private static readonly Color DayBot = new Color(175f / 255f, 215f / 255f, 225f / 255f, 1f);

        private static readonly Color DuskTop = new Color(90f / 255f, 50f / 255f, 95f / 255f, 1f);
        private static readonly Color DuskBot = new Color(250f / 255f, 135f / 255f, 85f / 255f, 1f);

        private static readonly Color CaveBlack = new Color(8f / 255f, 8f / 255f, 12f / 255f, 1f);

        private struct StarData
        {
            public Vector2 localPos;
            public float brightness;
            public float phase;
            public float speed;
            public SpriteRenderer renderer;
        }

        private readonly List<StarData> _stars = new List<StarData>();
        private GameObject _starfieldRoot;
        private Sprite _starPixelSprite;
        private GameObject _skyMeshObj;
        private Mesh _skyMesh;

        public Color CurrentTopSkyColor { get; private set; }
        public Color CurrentBottomSkyColor { get; private set; }
        public float StarAlpha { get; private set; }

        private void Awake()
        {
            if (dayNightCycle == null) dayNightCycle = FindFirstObjectByType<DayNightCycle2D>();
            if (targetCamera == null) targetCamera = UnityEngine.Camera.main;
            InitializeSkyGradient();
            InitializeStarfield();
        }

        private void InitializeSkyGradient()
        {
            if (_skyMeshObj != null) return;

            _skyMeshObj = new GameObject("SkyGradient");
            _skyMeshObj.transform.SetParent(transform, false);

            var mf = _skyMeshObj.AddComponent<MeshFilter>();
            var mr = _skyMeshObj.AddComponent<MeshRenderer>();

            _skyMesh = new Mesh { name = "SkyGradient_Mesh" };
            // Quad covering wide viewport (-35 to +35 X, -22 to +22 Y)
            _skyMesh.vertices = new Vector3[]
            {
                new Vector3(-35f, -22f, 0f),
                new Vector3(35f, -22f, 0f),
                new Vector3(-35f, 22f, 0f),
                new Vector3(35f, 22f, 0f)
            };
            _skyMesh.triangles = new int[] { 0, 2, 1, 2, 3, 1 };
            _skyMesh.colors = new Color[] { DayBot, DayBot, DayTop, DayTop };

            mf.mesh = _skyMesh;

            Shader unlit = Shader.Find("Universal Render Pipeline/2D/Sprite-Unlit-Default") ?? Shader.Find("Sprites/Default");
            var mat = new Material(unlit);
            mat.mainTexture = Texture2D.whiteTexture;
            mr.material = mat;
            mr.sortingLayerName = "Background";
            mr.sortingOrder = -100;
        }

        private void InitializeStarfield()
        {
            if (_starfieldRoot != null) return;

            _starfieldRoot = new GameObject("Starfield");
            _starfieldRoot.transform.SetParent(transform, false);

            // Create 1x1 white star texture & sprite
            var tex = new Texture2D(1, 1, TextureFormat.RGBA32, false);
            tex.SetPixel(0, 0, Color.white);
            tex.filterMode = FilterMode.Point;
            tex.Apply();
            _starPixelSprite = Sprite.Create(tex, new Rect(0, 0, 1, 1), new Vector2(0.5f, 0.5f), 1f);

            var rng = new System.Random(42); // deterministic seed matching Pygame
            for (int i = 0; i < starCount; i++)
            {
                var starObj = new GameObject($"Star_{i}");
                starObj.transform.SetParent(_starfieldRoot.transform, false);

                // Distribute across orthographic camera viewport (-22 to 22 horizontally, -13 to 13 vertically)
                float x = (float)(rng.NextDouble() * 44.0 - 22.0);
                float y = (float)(rng.NextDouble() * 26.0 - 13.0);
                starObj.transform.localPosition = new Vector3(x, y, 0f);

                var sr = starObj.AddComponent<SpriteRenderer>();
                sr.sprite = _starPixelSprite;
                sr.sortingLayerName = "Background";
                sr.sortingOrder = -50;
                sr.color = new Color(1f, 1f, 1f, 0f);

                // Small variation in star size
                float scale = (float)(rng.NextDouble() * 0.08 + 0.06);
                starObj.transform.localScale = new Vector3(scale, scale, 1f);

                _stars.Add(new StarData
                {
                    localPos = new Vector2(x, y),
                    brightness = (float)(rng.NextDouble() * 0.6 + 0.4),
                    phase = (float)(rng.NextDouble() * Math.PI * 2.0),
                    speed = (float)(rng.NextDouble() * 0.5 + 0.8),
                    renderer = sr
                });
            }
        }

        private void LateUpdate()
        {
            if (targetCamera == null) targetCamera = UnityEngine.Camera.main;
            if (targetCamera == null) return;

            var camPos = targetCamera.transform.position;

            // Follow camera position so sky gradient and starfield stay centered in viewport
            if (_skyMeshObj != null)
            {
                _skyMeshObj.transform.position = new Vector3(camPos.x, camPos.y, 0f);
            }

            if (_starfieldRoot != null)
            {
                _starfieldRoot.transform.position = new Vector3(camPos.x, camPos.y, 0f);
            }

            float t = dayNightCycle != null ? dayNightCycle.TimeOfDay : 0.25f;
            CalculateSkyColors(t, out var topColor, out var botColor);

            // Subterranean darkening check: if camera Y descends below -75 (surface ground is ~-67)
            float camY = targetCamera.transform.position.y;
            if (camY < -75f)
            {
                float depthFactor = Mathf.Clamp01((-75f - camY) / 25f);
                topColor = Color.Lerp(topColor, CaveBlack, depthFactor);
                botColor = Color.Lerp(botColor, CaveBlack, depthFactor);
            }

            CurrentTopSkyColor = topColor;
            CurrentBottomSkyColor = botColor;

            // Update procedural vertical gradient quad vertex colors
            if (_skyMesh != null)
            {
                _skyMesh.colors = new Color[] { botColor, botColor, topColor, topColor };
            }

            // Update Camera Background clear color
            targetCamera.backgroundColor = topColor;

            // Update Starfield Alpha: only visible during Night (0.72 -> 0.78 dusk, 0.78 -> 0.95 night, 0.95 -> 1.00 dawn)
            float starAlpha = 0f;
            if (t >= 0.72f && t < 0.78f)
            {
                starAlpha = (t - 0.72f) / 0.06f; // fade in at dusk
            }
            else if (t >= 0.78f && t < 0.95f)
            {
                starAlpha = 1f; // full night
            }
            else if (t >= 0.95f && t <= 1.0f)
            {
                starAlpha = 1f - ((t - 0.95f) / 0.05f); // fade out at dawn
            }
            else
            {
                starAlpha = 0f; // daytime: no stars visible
            }

            // Suppress stars underground
            if (camY < -75f)
            {
                starAlpha *= Mathf.Clamp01(1f - ((-75f - camY) / 10f));
            }

            StarAlpha = starAlpha;

            if (starAlpha > 0.01f)
            {
                float time = Time.time;
                for (int i = 0; i < _stars.Count; i++)
                {
                    var star = _stars[i];
                    if (star.renderer == null) continue;

                    // Twinkle variation with sinusoidal pulse
                    float pulse = Mathf.Sin((time * starTwinkleSpeed * star.speed) + star.phase);
                    float twinkle = Mathf.Lerp(star.brightness * 0.5f, star.brightness, (pulse + 1f) * 0.5f);
                    star.renderer.color = new Color(1f, 1f, 1f, starAlpha * twinkle);
                }
            }
            else
            {
                for (int i = 0; i < _stars.Count; i++)
                {
                    if (_stars[i].renderer != null && _stars[i].renderer.color.a > 0f)
                    {
                        _stars[i].renderer.color = new Color(1f, 1f, 1f, 0f);
                    }
                }
            }
        }

        public static void CalculateSkyColors(float timeOfDay, out Color top, out Color bot)
        {
            float t = Mathf.Repeat(timeOfDay, 1f);

            // Hermite cubic blending matching sky_presets.py:
            // 0.00 .. 0.02 : Dawn -> Day
            // 0.02 .. 0.48 : Day
            // 0.48 .. 0.53 : Day -> Dusk
            // 0.53 .. 0.72 : Dusk -> Night
            // 0.72 .. 0.95 : Night
            // 0.95 .. 1.00 : Night -> Dawn
            if (t < 0.02f)
            {
                float frac = HermiteSmooth(t / 0.02f);
                top = Color.Lerp(DawnTop, DayTop, frac);
                bot = Color.Lerp(DawnBot, DayBot, frac);
            }
            else if (t < 0.48f)
            {
                top = DayTop;
                bot = DayBot;
            }
            else if (t < 0.53f)
            {
                float frac = HermiteSmooth((t - 0.48f) / 0.05f);
                top = Color.Lerp(DayTop, DuskTop, frac);
                bot = Color.Lerp(DayBot, DuskBot, frac);
            }
            else if (t < 0.72f)
            {
                float frac = HermiteSmooth((t - 0.53f) / 0.19f);
                top = Color.Lerp(DuskTop, NightTop, frac);
                bot = Color.Lerp(DuskBot, NightBot, frac);
            }
            else if (t < 0.95f)
            {
                top = NightTop;
                bot = NightBot;
            }
            else
            {
                float frac = HermiteSmooth((t - 0.95f) / 0.05f);
                top = Color.Lerp(NightTop, DawnTop, frac);
                bot = Color.Lerp(NightBot, DawnBot, frac);
            }
        }

        private static float HermiteSmooth(float t)
        {
            float clamped = Mathf.Clamp01(t);
            return clamped * clamped * (3f - (2f * clamped));
        }

        /// <summary>
        /// Converts normalized 0..1 timeOfDay to human 12-hour clock (e.g. "7:04 PM", isNight).
        /// </summary>
        public static void GetClockTime(float timeOfDay, out int hour, out int minute, out bool isPm, out bool isNight)
        {
            // 0.0 is 6:00 AM in Potaria celestial cycle
            float totalHours = (6f + (timeOfDay * 24f)) % 24f;
            int h = (int)totalHours;
            minute = (int)((totalHours - h) * 60f);

            isPm = h >= 12;
            hour = h % 12;
            if (hour == 0) hour = 12;

            // Night in Potaria is 7:00 PM (19:00) to 5:00 AM (5:00)
            isNight = (h >= 19 || h < 5);
        }
    }
}
