using System;
using UnityEngine;
using UnityEngine.Rendering.Universal;

namespace Potaria.World.Lighting
{
    /// <summary>
    /// Point Light 2D component for placed light emitters in Potaria.
    /// Used on torches, oil lamps, brass/spectral lanterns, fireplaces, and glowing mushrooms.
    /// Includes optional organic flame flickering.
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

        [Header("Flicker Animation")]
        [SerializeField] private bool enableFlicker = true;
        [SerializeField] private float flickerSpeed = 8.0f;
        [SerializeField] private float flickerIntensityVariance = 0.12f;

        private float _flickerSeed;

        public Light2D PointLight => pointLight;
        public Color LightColor { get => lightColor; set { lightColor = value; if (pointLight != null) pointLight.color = value; } }
        public float OuterRadius { get => outerRadius; set { outerRadius = value; if (pointLight != null) pointLight.pointLightOuterRadius = value; } }
        public float BaseIntensity { get => baseIntensity; set => baseIntensity = value; }

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
        }

        private void Update()
        {
            if (enableFlicker && pointLight != null)
            {
                float noise = Mathf.PerlinNoise(_flickerSeed, Time.time * flickerSpeed);
                float offset = (noise - 0.5f) * 2f * flickerIntensityVariance;
                pointLight.intensity = Mathf.Max(0.1f, baseIntensity + offset);
            }
        }

        public void Configure(Color color, float radius, float intensity, bool flicker = true)
        {
            lightColor = color;
            outerRadius = radius;
            baseIntensity = intensity;
            enableFlicker = flicker;
            ApplySettings();
        }
    }
}
