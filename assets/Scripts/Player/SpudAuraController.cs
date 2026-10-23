using System;
using UnityEngine;
using UnityEngine.Rendering.Universal;

namespace Potaria.Player
{
    /// <summary>
    /// Renders Spud the Potato Hero's signature visual identity:
    /// - Pulsating radiant cyan outer energy shield aura ring.
    /// - Radiant golden inner mandala ring.
    /// - 4 orbiting golden starlight sparkle motes with dynamic shimmering.
    /// - Soft personal cyan Point Light 2D providing illumination in dim caves and at night.
    /// </summary>
    [DisallowMultipleComponent]
    public class SpudAuraController : MonoBehaviour
    {
        [Header("Aura Configuration")]
        [SerializeField] private bool enableAura = true;
        [SerializeField] private bool enablePersonalLight = true;
        [SerializeField] private bool enableSparkles = true;

        [Header("Aura Palette & Radii")]
        [SerializeField] private Color cyanAuraColor = new Color(0.15f, 0.88f, 1.0f, 0.70f);
        [SerializeField] private Color goldRingColor = new Color(1.0f, 0.84f, 0.22f, 0.65f);
        [SerializeField] private float outerRingRadius = 0.95f;
        [SerializeField] private float innerRingRadius = 0.65f;
        [SerializeField] private float pulseFrequency = 2.8f;
        [SerializeField] private float pulseAmplitude = 0.08f;

        [Header("Personal Light 2D")]
        [SerializeField] private Color personalLightColor = new Color(0.20f, 0.85f, 1.0f, 1.0f);
        [SerializeField] private float lightOuterRadius = 4.2f;
        [SerializeField] private float lightInnerRadius = 0.8f;
        [SerializeField] private float lightBaseIntensity = 0.70f;

        [Header("Sparkle Motes")]
        [SerializeField] private int sparkleCount = 4;
        [SerializeField] private float sparkleOrbitRadius = 1.15f;
        [SerializeField] private float sparkleOrbitSpeed = 1.8f;

        private Light2D _personalLight;
        private LineRenderer _outerLine;
        private LineRenderer _innerLine;
        private GameObject _auraContainer;
        private GameObject[] _sparkleObjs;
        private SpriteRenderer[] _sparkleRenderers;

        private const int CircleSegments = 36;
        private readonly Vector3[] _circlePositions = new Vector3[CircleSegments];

        public bool EnableAura { get => enableAura; set { enableAura = value; UpdateVisibility(); } }
        public bool EnablePersonalLight { get => enablePersonalLight; set { enablePersonalLight = value; UpdateVisibility(); } }
        public Light2D PersonalLight => _personalLight;

        private void Awake()
        {
            BuildAuraHierarchy();
        }

        private void OnEnable()
        {
            UpdateVisibility();
        }

        public void BuildAuraHierarchy()
        {
            if (_auraContainer != null) return;

            _auraContainer = new GameObject("SpudAura_Effects");
            _auraContainer.transform.SetParent(transform, false);
            _auraContainer.transform.localPosition = new Vector3(0f, 0.5f, 0f); // Center on Spud's body

            var unlitMat = GetOrCreateUnlitSpriteMaterial();

            // 1. Personal Point Light 2D (Cyan)
            var lightObj = new GameObject("Personal_CyanLight2D");
            lightObj.transform.SetParent(_auraContainer.transform, false);
            _personalLight = lightObj.AddComponent<Light2D>();
            _personalLight.lightType = Light2D.LightType.Point;
            _personalLight.color = personalLightColor;
            _personalLight.pointLightInnerRadius = lightInnerRadius;
            _personalLight.pointLightOuterRadius = lightOuterRadius;
            _personalLight.intensity = lightBaseIntensity;
            _personalLight.falloffIntensity = 0.5f;
            _personalLight.shadowsEnabled = false;

            // 2. Cyan Outer Energy Shield Ring
            var outerObj = new GameObject("CyanOuterRing");
            outerObj.transform.SetParent(_auraContainer.transform, false);
            _outerLine = outerObj.AddComponent<LineRenderer>();
            ConfigureLineRenderer(_outerLine, unlitMat, cyanAuraColor, 0.045f, -1);

            // 3. Golden Inner Ring
            var innerObj = new GameObject("GoldenInnerRing");
            innerObj.transform.SetParent(_auraContainer.transform, false);
            _innerLine = innerObj.AddComponent<LineRenderer>();
            ConfigureLineRenderer(_innerLine, unlitMat, goldRingColor, 0.035f, -2);

            // 4. Orbiting Golden Sparkle Motes
            Sprite starSprite = CreateDiamondStarSprite();
            _sparkleObjs = new GameObject[sparkleCount];
            _sparkleRenderers = new SpriteRenderer[sparkleCount];

            for (int i = 0; i < sparkleCount; i++)
            {
                var sObj = new GameObject($"SparkleMote_{i}");
                sObj.transform.SetParent(_auraContainer.transform, false);
                var sr = sObj.AddComponent<SpriteRenderer>();
                sr.sprite = starSprite;
                sr.sortingLayerName = "Player";
                sr.sortingOrder = 2; // Render in front of player
                sr.color = goldRingColor;
                if (unlitMat != null) sr.sharedMaterial = unlitMat;

                _sparkleObjs[i] = sObj;
                _sparkleRenderers[i] = sr;
            }

            UpdateVisibility();
        }

        private void ConfigureLineRenderer(LineRenderer line, Material mat, Color col, float width, int sortingOrder)
        {
            line.useWorldSpace = false;
            line.loop = true;
            line.positionCount = CircleSegments;
            line.startWidth = width;
            line.endWidth = width;
            if (mat != null) line.sharedMaterial = mat;
            line.startColor = col;
            line.endColor = col;
            line.sortingLayerName = "Player";
            line.sortingOrder = sortingOrder;
        }

        private void LateUpdate()
        {
            if (!enableAura) return;

            float time = Time.time;

            // 1. Pulsate Outer Cyan Ring
            float outerR = outerRingRadius + Mathf.Sin(time * pulseFrequency) * pulseAmplitude;
            UpdateRingPoints(_outerLine, outerR);
            if (_outerLine != null)
            {
                float alpha = 0.55f + Mathf.PingPong(time * 2f, 0.35f);
                Color c = cyanAuraColor;
                c.a = alpha;
                _outerLine.startColor = c;
                _outerLine.endColor = c;
            }

            // 2. Pulsate Inner Golden Ring (counter-phase)
            float innerR = innerRingRadius + Mathf.Cos(time * (pulseFrequency * 0.85f)) * (pulseAmplitude * 0.75f);
            UpdateRingPoints(_innerLine, innerR);
            if (_innerLine != null)
            {
                float alpha = 0.50f + Mathf.PingPong(time * 1.8f + 1f, 0.30f);
                Color g = goldRingColor;
                g.a = alpha;
                _innerLine.startColor = g;
                _innerLine.endColor = g;
            }

            // 3. Modulate Personal Light with gentle organic breathing
            if (_personalLight != null && enablePersonalLight)
            {
                float pulse = Mathf.Sin(time * (pulseFrequency * 0.7f)) * 0.08f;
                _personalLight.intensity = lightBaseIntensity + pulse;
            }

            // 4. Update Orbiting Golden Sparkle Motes
            if (enableSparkles && _sparkleObjs != null)
            {
                for (int i = 0; i < _sparkleObjs.Length; i++)
                {
                    if (_sparkleObjs[i] == null) continue;

                    float baseAngle = (i * (Mathf.PI * 2f / sparkleCount));
                    float currentAngle = baseAngle + (time * sparkleOrbitSpeed * (i % 2 == 0 ? 1f : -0.85f));
                    float r = sparkleOrbitRadius + Mathf.Sin(time * 3f + i) * 0.12f;

                    float x = Mathf.Cos(currentAngle) * r;
                    float y = Mathf.Sin(currentAngle) * r;

                    _sparkleObjs[i].transform.localPosition = new Vector3(x, y, 0f);

                    // Twinkle rotation
                    _sparkleObjs[i].transform.localRotation = Quaternion.Euler(0f, 0f, time * 140f * (i % 2 == 0 ? 1f : -1f));

                    // Twinkle color pulsation between gold and white
                    if (_sparkleRenderers[i] != null)
                    {
                        float twinkle = Mathf.PingPong(time * 4f + (i * 0.5f), 1f);
                        Color twinkleCol = Color.Lerp(goldRingColor, Color.white, twinkle);
                        twinkleCol.a = 0.75f + (twinkle * 0.25f);
                        _sparkleRenderers[i].color = twinkleCol;
                    }
                }
            }
        }

        private void UpdateRingPoints(LineRenderer line, float radius)
        {
            if (line == null) return;

            float step = (Mathf.PI * 2f) / CircleSegments;
            for (int i = 0; i < CircleSegments; i++)
            {
                float a = i * step;
                _circlePositions[i] = new Vector3(Mathf.Cos(a) * radius, Mathf.Sin(a) * radius, 0f);
            }
            line.SetPositions(_circlePositions);
        }

        private void UpdateVisibility()
        {
            if (_auraContainer != null) _auraContainer.SetActive(enableAura);
            if (_personalLight != null) _personalLight.enabled = enableAura && enablePersonalLight;
            if (_sparkleObjs != null)
            {
                foreach (var obj in _sparkleObjs)
                {
                    if (obj != null) obj.SetActive(enableAura && enableSparkles);
                }
            }
        }

        public static Material GetOrCreateUnlitSpriteMaterial()
        {
            var shader = Shader.Find("Universal Render Pipeline/2D/Sprite-Unlit-Default") ?? Shader.Find("Sprites/Default");
            if (shader != null)
            {
                var mat = new Material(shader);
                mat.name = "SpudAura_UnlitMaterial";
                return mat;
            }
            return null;
        }

        public static Sprite CreateDiamondStarSprite()
        {
            int size = 9;
            var tex = new Texture2D(size, size, TextureFormat.RGBA32, false);
            tex.filterMode = FilterMode.Point;
            Color clear = new Color(0, 0, 0, 0);
            Color gold = new Color(1.0f, 0.90f, 0.40f, 1.0f);
            Color centerWhite = Color.white;

            for (int y = 0; y < size; y++)
            {
                for (int x = 0; x < size; x++)
                {
                    int dx = Mathf.Abs(x - 4);
                    int dy = Mathf.Abs(y - 4);

                    if (dx == 0 && dy == 0)
                        tex.SetPixel(x, y, centerWhite);
                    else if ((dx == 0 && dy <= 3) || (dy == 0 && dx <= 3) || (dx == 1 && dy == 1))
                        tex.SetPixel(x, y, gold);
                    else
                        tex.SetPixel(x, y, clear);
                }
            }
            tex.Apply();
            return Sprite.Create(tex, new Rect(0, 0, size, size), new Vector2(0.5f, 0.5f), 16f);
        }
    }
}
