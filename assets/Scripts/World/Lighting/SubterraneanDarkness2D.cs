using System;
using UnityEngine;
using UnityEngine.Rendering.Universal;

namespace Potaria.World.Lighting
{
    /// <summary>
    /// Depth-based subterranean ambient attenuation for Potaria.
    /// Diminishes celestial ambient sunlight as the player or camera descends
    /// through underground rock strata, creating pitch-black cavern depths.
    /// </summary>
    public class SubterraneanDarkness2D : MonoBehaviour
    {
        [Header("Target & Light")]
        [SerializeField] private Transform observer;
        [SerializeField] private DayNightCycle2D dayNightCycle;
        [SerializeField] private Light2D globalLight;

        [Header("Depth Stratum Thresholds (Grid Y)")]
        [SerializeField] private float surfaceGridY = WorldConstants.SurfaceLevel;       // ~70
        [SerializeField] private float undergroundGridY = WorldConstants.UndergroundLevel; // ~115

        private float _currentDepthAttenuation = 1.0f;

        public float DepthAttenuation => _currentDepthAttenuation;

        private void Awake()
        {
            if (dayNightCycle == null) dayNightCycle = GetComponent<DayNightCycle2D>();
            if (dayNightCycle == null) dayNightCycle = FindAnyObjectByType<DayNightCycle2D>();
            if (globalLight == null && dayNightCycle != null) globalLight = dayNightCycle.GlobalLight;
            if (observer == null)
            {
                var cam = Camera.main;
                if (cam != null) observer = cam.transform;
            }
        }

        private void LateUpdate()
        {
            if (observer == null)
            {
                var cam = Camera.main;
                if (cam != null) observer = cam.transform;
                if (observer == null) return;
            }

            // In Unity coordinates: cell Y = -ty. Therefore ty = -observer.position.y
            float currentGridY = -observer.position.y;

            if (currentGridY <= surfaceGridY)
            {
                _currentDepthAttenuation = 1.0f;
            }
            else if (currentGridY >= undergroundGridY)
            {
                _currentDepthAttenuation = 0.0f;
            }
            else
            {
                // Smooth cosine / cubic fade between surface and underground
                float t = (currentGridY - surfaceGridY) / (undergroundGridY - surfaceGridY);
                _currentDepthAttenuation = Mathf.Cos(t * Mathf.PI * 0.5f);
            }

            // Modulate global light intensity if present
            if (globalLight != null && dayNightCycle != null)
            {
                // DayNightCycle sets base intensity; depth attenuation guarantees 0.0f (pitch black) underground
                globalLight.intensity = dayNightCycle.CurrentBaseIntensity * _currentDepthAttenuation;
            }
        }

        public float CalculateAttenuationAt(float worldY)
        {
            float gridY = -worldY;
            if (gridY <= surfaceGridY) return 1.0f;
            if (gridY >= undergroundGridY) return 0.0f;
            float t = (gridY - surfaceGridY) / (undergroundGridY - surfaceGridY);
            return Mathf.Cos(t * Mathf.PI * 0.5f);
        }
    }
}
