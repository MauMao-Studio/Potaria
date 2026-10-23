using System;
using UnityEngine;
using UnityEngine.Rendering.Universal;

namespace Potaria.World.Lighting
{
    /// <summary>
    /// Point Light 2D component for placed light emitters in Potaria.
    /// Used on torches, oil lamps, brass/spectral lanterns, fireplaces, and glowing mushrooms.
    /// Includes organic flame flickering, soft radial falloff (no pitch-black blockiness),
    /// and dynamic camera-distance occlusion culling (>25 units disabled for maximum FPS).
    /// </summary>
    [RequireComponent(typeof(Light2D))]
    public class PointLightSource2D : MonoBehaviour
    {
        [Header("Light Parameters")]
        [SerializeField] private Light2D pointLight;
        [SerializeField] private Color lightColor = new Color(1.0f, 0.85f, 0.40f, 1.0f);
        [SerializeField] private float outerRadius = 6.0f;
        [SerializeField] private float innerRadius = 0.5f;
        [SerializeField] private float baseIntensity = 1.0f;
        [SerializeField] private bool enableShadows = true; // Soft radial torchlight without polygon blockiness

        [Header("Flicker Animation")]
        [SerializeField] private bool enableFlicker = true;
        [SerializeField] private float flickerSpeed = 8.0f;
        [SerializeField] private float flickerIntensityVariance = 0.12f;

        [Header("Distance Occlusion Culling")]
        [SerializeField] private float cullingDistance = 25.0f;

        private float _flickerSeed;
        private Transform _cameraTransform;

        public Light2D PointLight => pointLight;
        public Color LightColor { get => lightColor; set { lightColor = value; if (pointLight != null) pointLight.color = value; } }
        public float OuterRadius { get => outerRadius; set { outerRadius = value; if (pointLight != null) pointLight.pointLightOuterRadius = value; } }
        public float InnerRadius { get => innerRadius; set { innerRadius = value; if (pointLight != null) pointLight.pointLightInnerRadius = value; } }
        public float BaseIntensity { get => baseIntensity; set => baseIntensity = value; }
        public bool EnableShadows { get => enableShadows; set { enableShadows = value; if (pointLight != null) pointLight.shadowsEnabled = value; } }
        public float CullingDistance { get => cullingDistance; set => cullingDistance = value; }
        public bool IsCulled => pointLight != null && !pointLight.enabled;

        private void Awake()
        {
            if (pointLight == null) pointLight = GetComponent<Light2D>();
            _flickerSeed = UnityEngine.Random.Range(0f, 100f);
            ApplySettings();
        }

        public void ApplySettings()
        {
            if (pointLight == null) pointLight = GetComponent<Light2D>();
            if (pointLight == null) return;

            pointLight.lightType = Light2D.LightType.Point;
            pointLight.color = lightColor;
            pointLight.pointLightInnerRadius = innerRadius;
            pointLight.pointLightOuterRadius = outerRadius;
            pointLight.intensity = baseIntensity;
            pointLight.shadowsEnabled = enableShadows;
            pointLight.shadowIntensity = 0.70f;
            pointLight.falloffIntensity = 0.5f; // Soft smooth radial gradient matching Pygame
        }

        private void Update()
        {
            if (pointLight == null) return;

            // 1. Dynamic Distance Occlusion Culling against Camera Viewport
            if (_cameraTransform == null)
            {
                var cam = Camera.main;
                if (cam != null) _cameraTransform = cam.transform;
            }

            if (_cameraTransform != null)
            {
                float dx = transform.position.x - _cameraTransform.position.x;
                float dy = transform.position.y - _cameraTransform.position.y;
                float sqrDist = (dx * dx) + (dy * dy);
                float maxSqr = cullingDistance * cullingDistance;

                bool inRange = (sqrDist <= maxSqr);
                if (pointLight.enabled != inRange)
                {
                    pointLight.enabled = inRange;
                }

                if (!inRange) return; // Completely culled when beyond camera reach
            }

            // 2. Organic flame flicker (only evaluated when active & visible)
            if (enableFlicker)
            {
                float noise = Mathf.PerlinNoise(_flickerSeed, Time.time * flickerSpeed);
                float offset = (noise - 0.5f) * 2f * flickerIntensityVariance;
                pointLight.intensity = Mathf.Max(0.1f, baseIntensity + offset);
            }
        }

        public void Configure(Color color, float radius, float intensity, bool flicker = true, bool shadows = true)
        {
            lightColor = color;
            outerRadius = radius;
            baseIntensity = intensity;
            enableFlicker = flicker;
            enableShadows = shadows;
            ApplySettings();
        }
    }
}
