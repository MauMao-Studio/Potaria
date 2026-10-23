using System;
using UnityEngine;
using UnityEngine.Rendering.Universal;

namespace Potaria.World.Lighting
{
    /// <summary>
    /// Celestial 2D URP Day/Night Cycle controller for Potaria.
    /// Smoothly transitions Global Light 2D through Dawn, Noon, Sunset, and Night
    /// with authentic atmospheric ambient color grading.
    /// </summary>
    public class DayNightCycle2D : MonoBehaviour
    {
        [Header("Light Component")]
        [SerializeField] private Light2D globalLight;

        [Header("Cycle Timing")]
        [Tooltip("Full day/night cycle duration in real seconds.")]
        [SerializeField] private float cycleDuration = 300f; // 5 minutes standard cycle
        [Range(0f, 1f)]
        [SerializeField] private float timeOfDay = 0.25f; // Starts at Noon (0.25)
        [SerializeField] private bool pauseCycle = false;

        [Header("Atmospheric Gradients")]
        [SerializeField] private Color dawnColor = new Color(1.0f, 0.72f, 0.50f, 1.0f);
        [SerializeField] private float dawnIntensity = 0.85f;

        [SerializeField] private Color noonColor = new Color(1.0f, 0.98f, 0.92f, 1.0f);
        [SerializeField] private float noonIntensity = 1.0f;

        [SerializeField] private Color sunsetColor = new Color(0.95f, 0.55f, 0.35f, 1.0f);
        [SerializeField] private float sunsetIntensity = 0.85f;

        [SerializeField] private Color nightColor = new Color(0.10f, 0.14f, 0.28f, 1.0f);
        [SerializeField] private float nightIntensity = 0.22f;

        public enum CelestialPhase
        {
            Dawn,
            Noon,
            Sunset,
            Night
        }

        private float _currentBaseIntensity = 1.0f;

        public float TimeOfDay { get => timeOfDay; set => timeOfDay = Mathf.Repeat(value, 1f); }
        public float CycleDuration { get => cycleDuration; set => cycleDuration = Mathf.Max(1f, value); }
        public bool PauseCycle { get => pauseCycle; set => pauseCycle = value; }
        public Light2D GlobalLight { get => globalLight; set => globalLight = value; }
        public float CurrentBaseIntensity => _currentBaseIntensity;

        public CelestialPhase CurrentPhase
        {
            get
            {
                if (timeOfDay < 0.15f) return CelestialPhase.Dawn;
                if (timeOfDay < 0.55f) return CelestialPhase.Noon;
                if (timeOfDay < 0.75f) return CelestialPhase.Sunset;
                return CelestialPhase.Night;
            }
        }

        private void Awake()
        {
            if (globalLight == null)
            {
                globalLight = GetComponent<Light2D>();
                if (globalLight == null)
                {
                    globalLight = gameObject.AddComponent<Light2D>();
                    globalLight.lightType = Light2D.LightType.Global;
                }
            }
        }

        private void Update()
        {
            if (!pauseCycle && cycleDuration > 0)
            {
                timeOfDay = Mathf.Repeat(timeOfDay + (Time.deltaTime / cycleDuration), 1f);
            }

            ApplyLighting();
        }

        public void ApplyLighting()
        {
            if (globalLight == null) return;

            Color targetColor;
            float targetIntensity;

            // Phase Segments:
            // 0.00 .. 0.15 : Dawn -> Noon
            // 0.15 .. 0.55 : Noon
            // 0.55 .. 0.72 : Noon -> Sunset
            // 0.72 .. 0.78 : Sunset -> Night
            // 0.78 .. 0.92 : Deep Night
            // 0.92 .. 1.00 : Night -> Dawn
            if (timeOfDay < 0.15f)
            {
                float t = timeOfDay / 0.15f;
                targetColor = Color.Lerp(dawnColor, noonColor, t);
                targetIntensity = Mathf.Lerp(dawnIntensity, noonIntensity, t);
            }
            else if (timeOfDay < 0.55f)
            {
                targetColor = noonColor;
                targetIntensity = noonIntensity;
            }
            else if (timeOfDay < 0.72f)
            {
                float t = (timeOfDay - 0.55f) / 0.17f;
                targetColor = Color.Lerp(noonColor, sunsetColor, t);
                targetIntensity = Mathf.Lerp(noonIntensity, sunsetIntensity, t);
            }
            else if (timeOfDay < 0.78f)
            {
                float t = (timeOfDay - 0.72f) / 0.06f;
                targetColor = Color.Lerp(sunsetColor, nightColor, t);
                targetIntensity = Mathf.Lerp(sunsetIntensity, nightIntensity, t);
            }
            else if (timeOfDay < 0.92f)
            {
                targetColor = nightColor;
                targetIntensity = nightIntensity;
            }
            else
            {
                float t = (timeOfDay - 0.92f) / 0.08f;
                targetColor = Color.Lerp(nightColor, dawnColor, t);
                targetIntensity = Mathf.Lerp(nightIntensity, dawnIntensity, t);
            }

            _currentBaseIntensity = targetIntensity;
            globalLight.color = targetColor;
            globalLight.intensity = targetIntensity;
        }

        public bool IsNight => CurrentPhase == CelestialPhase.Night;

        public void GetClock(out int hour, out int minute, out bool isPm, out bool isNight)
        {
            SkyRenderer2D.GetClockTime(timeOfDay, out hour, out minute, out isPm, out isNight);
        }

        public void SetTime(float t)
        {
            timeOfDay = Mathf.Repeat(t, 1f);
            ApplyLighting();
        }
    }
}
