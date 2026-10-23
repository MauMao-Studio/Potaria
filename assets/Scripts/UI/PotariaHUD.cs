using System;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.UI;
using TMPro;
using Potaria.Input;
using Potaria.Player;
using Potaria.RPG;
using Potaria.World.Lighting;
using Potaria.Localization;
using Potaria.Combat;

namespace Potaria.UI
{
    /// <summary>
    /// Master In-Game HUD for Potaria matching authentic Pygame reference:
    /// - Top-Left: 10-slot Hotbar with slot numbers, item sprites, stack counts, selection frame
    /// - Top-Right: Life hearts readout (Life: X / Y Lv.Z), Mana bar (MP: A / B), Radar [M], Clock badge
    /// - Bottom-Center: 4 Skill badges (Q, F, V, R with Lv and localized abbreviation)
    /// - Top/Mid-Left: Real-time F3 Profiler overlay
    /// - Crystal-clear typography powered 100% by TextMeshPro (TMP) at 1920x1080 reference resolution
    /// - Fully localized via LocalizationManager (EN / FIL) with instant L-key switching
    /// </summary>
    public class PotariaHUD : MonoBehaviour
    {
        private static PotariaHUD _instance;
        public static PotariaHUD Instance => _instance;

        [Header("Target References")]
        [SerializeField] private PlayerController player;
        [SerializeField] private PlayerStats playerStats;
        [SerializeField] private DayNightCycle2D dayNightCycle;
        [SerializeField] private PotariaInput input;

        [Header("Fonts & Sprites")]
        [SerializeField] private TMP_FontAsset tmpFont;
        [SerializeField] private Font pixelFont;
        [SerializeField] private Sprite slotFrameSprite;
        [SerializeField] private Sprite slotSelectedSprite;
        [SerializeField] private Sprite heartFullSprite;
        [SerializeField] private Sprite heartEmptySprite;
        [SerializeField] private Sprite manaStarSprite;

        // UI Components
        private Canvas _canvas;
        private CanvasScaler _scaler;

        // Hotbar
        private GameObject _hotbarRoot;
        private Image[] _slotFrames = new Image[10];
        private Image[] _slotItems = new Image[10];
        private TextMeshProUGUI[] _slotCounts = new TextMeshProUGUI[10];
        private TextMeshProUGUI[] _slotNumbers = new TextMeshProUGUI[10];
        private RectTransform _selectionFrame;
        private int _selectedSlot = 0;

        // Life & Mana
        private TextMeshProUGUI _lifeText;
        private TextMeshProUGUI _manaText;
        private Image[] _heartIcons = new Image[10];
        private Image _manaBarFill;

        // Clock & Radar
        private TextMeshProUGUI _clockText;
        private TextMeshProUGUI _radarText;

        // Skills (Q, F, V, R)
        private Image[] _skillBadges = new Image[4];
        private TextMeshProUGUI[] _skillTexts = new TextMeshProUGUI[4];
        private Image[] _skillCooldownOverlays = new Image[4];

        // Profiler (F3)
        private GameObject _profilerPanel;
        private TextMeshProUGUI _profilerText;
        private bool _profilerActive = false;
        private float _fpsAccumulator = 0f;
        private int _fpsFrames = 0;
        private float _currentFps = 60f;

        // Hotbar sample data matching authentic starting gear
        public struct HotbarItem
        {
            public string id;
            public string nameKey;
            public Sprite icon;
            public int stack;
        }

        private readonly HotbarItem[] _hotbarData = new HotbarItem[10];

        public int SelectedSlot => _selectedSlot;

        private void Awake()
        {
            _instance = this;
            if (input == null) input = PotariaInput.Instance;
            if (player == null) player = FindFirstObjectByType<PlayerController>();
            if (playerStats == null && player != null) playerStats = player.Stats;
            if (dayNightCycle == null) dayNightCycle = FindFirstObjectByType<DayNightCycle2D>();

            LoadResourcesIfMissing();
            BuildOrValidateUI();
            InitializeDefaultHotbarItems();
        }

        private void OnEnable()
        {
            LocalizationManager.OnLanguageChanged += RefreshLocalizedLabels;
        }

        private void OnDisable()
        {
            LocalizationManager.OnLanguageChanged -= RefreshLocalizedLabels;
        }

        private void Start()
        {
            RefreshLocalizedLabels();
        }

        public void LoadResourcesIfMissing()
        {
#if UNITY_EDITOR
            if (tmpFont == null)
            {
                tmpFont = UnityEditor.AssetDatabase.LoadAssetAtPath<TMP_FontAsset>("Assets/Fonts/PixelifySans-Regular SDF.asset");
                if (tmpFont == null) tmpFont = UnityEditor.AssetDatabase.LoadAssetAtPath<TMP_FontAsset>("Assets/TextMesh Pro/Resources/Fonts & Materials/LiberationSans SDF.asset");
                if (tmpFont == null) tmpFont = Resources.Load<TMP_FontAsset>("Fonts & Materials/LiberationSans SDF");
            }

            if (pixelFont == null)
            {
                pixelFont = UnityEditor.AssetDatabase.LoadAssetAtPath<Font>("Assets/fonts/PixelifySans-Bold.ttf");
                if (pixelFont == null) pixelFont = UnityEditor.AssetDatabase.LoadAssetAtPath<Font>("Assets/fonts/PixelifySans-Regular.ttf");
                if (pixelFont == null) pixelFont = Resources.GetBuiltinResource<Font>("LegacyRuntime.ttf");
            }

            if (slotFrameSprite == null)
            {
                slotFrameSprite = UnityEditor.AssetDatabase.LoadAssetAtPath<Sprite>("Assets/Sprites/Ui/slot_frame.png");
                if (slotFrameSprite == null) slotFrameSprite = UnityEditor.AssetDatabase.LoadAssetAtPath<Sprite>("Assets/ui/slot_frame.png");
            }
            if (slotSelectedSprite == null)
            {
                slotSelectedSprite = UnityEditor.AssetDatabase.LoadAssetAtPath<Sprite>("Assets/Sprites/Ui/slot_selected.png");
                if (slotSelectedSprite == null) slotSelectedSprite = UnityEditor.AssetDatabase.LoadAssetAtPath<Sprite>("Assets/ui/slot_selected.png");
            }
            if (heartFullSprite == null)
            {
                heartFullSprite = UnityEditor.AssetDatabase.LoadAssetAtPath<Sprite>("Assets/Sprites/Ui/heart_full.png");
                if (heartFullSprite == null) heartFullSprite = UnityEditor.AssetDatabase.LoadAssetAtPath<Sprite>("Assets/ui/heart_full.png");
            }
            if (heartEmptySprite == null)
            {
                heartEmptySprite = UnityEditor.AssetDatabase.LoadAssetAtPath<Sprite>("Assets/Sprites/Ui/heart_empty.png");
                if (heartEmptySprite == null) heartEmptySprite = UnityEditor.AssetDatabase.LoadAssetAtPath<Sprite>("Assets/ui/heart_empty.png");
            }
            if (manaStarSprite == null)
            {
                manaStarSprite = UnityEditor.AssetDatabase.LoadAssetAtPath<Sprite>("Assets/Sprites/Ui/mana_star.png");
                if (manaStarSprite == null) manaStarSprite = UnityEditor.AssetDatabase.LoadAssetAtPath<Sprite>("Assets/ui/mana_star.png");
            }
#endif
        }

        public void BuildOrValidateUI()
        {
            _canvas = GetComponent<Canvas>();
            if (_canvas == null) _canvas = gameObject.AddComponent<Canvas>();
            _canvas.renderMode = RenderMode.ScreenSpaceOverlay;
            _canvas.sortingOrder = 100;

            _scaler = GetComponent<CanvasScaler>();
            if (_scaler == null) _scaler = gameObject.AddComponent<CanvasScaler>();
            _scaler.uiScaleMode = CanvasScaler.ScaleMode.ScaleWithScreenSize;
            _scaler.referenceResolution = new Vector2(1920f, 1080f);
            _scaler.matchWidthOrHeight = 0.5f;

            if (GetComponent<GraphicRaycaster>() == null) gameObject.AddComponent<GraphicRaycaster>();

            BuildHotbar();
            BuildLifeAndMana();
            BuildClockAndRadar();
            BuildSkillBadges();
            BuildProfiler();
        }

        private void BuildHotbar()
        {
            var oldHotbar = transform.Find("Hotbar");
            if (oldHotbar != null) DestroyImmediate(oldHotbar.gameObject);

            _hotbarRoot = new GameObject("Hotbar");
            _hotbarRoot.transform.SetParent(transform, false);

            var rt = _hotbarRoot.AddComponent<RectTransform>();
            rt.anchorMin = new Vector2(0f, 1f);
            rt.anchorMax = new Vector2(0f, 1f);
            rt.pivot = new Vector2(0f, 1f);
            rt.anchoredPosition = new Vector2(16f, -16f);
            rt.sizeDelta = new Vector2(460f, 48f);

            for (int i = 0; i < 10; i++)
            {
                var slotObj = new GameObject($"Slot_{i}");
                slotObj.transform.SetParent(_hotbarRoot.transform, false);

                var srt = slotObj.AddComponent<RectTransform>();
                srt.anchorMin = new Vector2(0f, 0.5f);
                srt.anchorMax = new Vector2(0f, 0.5f);
                srt.pivot = new Vector2(0f, 0.5f);
                srt.anchoredPosition = new Vector2(i * 44f, 0f);
                srt.sizeDelta = new Vector2(40f, 40f);

                var frameImg = slotObj.AddComponent<Image>();
                if (slotFrameSprite != null) frameImg.sprite = slotFrameSprite;
                frameImg.color = new Color(1f, 1f, 1f, 0.95f);
                _slotFrames[i] = frameImg;

                // Item Icon child
                var iconObj = new GameObject("Icon");
                iconObj.transform.SetParent(slotObj.transform, false);
                var irt = iconObj.AddComponent<RectTransform>();
                irt.anchorMin = Vector2.zero;
                irt.anchorMax = Vector2.one;
                irt.offsetMin = new Vector2(4f, 4f);
                irt.offsetMax = new Vector2(-4f, -4f);
                var iconImg = iconObj.AddComponent<Image>();
                iconImg.color = new Color(1f, 1f, 1f, 0f); // invisible until item set
                _slotItems[i] = iconImg;

                // Slot Number label (1..9, 0)
                var numObj = new GameObject("Num");
                numObj.transform.SetParent(slotObj.transform, false);
                var nrt = numObj.AddComponent<RectTransform>();
                nrt.anchorMin = new Vector2(0f, 1f);
                nrt.anchorMax = new Vector2(0f, 1f);
                nrt.pivot = new Vector2(0f, 1f);
                nrt.anchoredPosition = new Vector2(3f, -2f);
                nrt.sizeDelta = new Vector2(14f, 14f);
                var numText = numObj.AddComponent<TextMeshProUGUI>();
                if (tmpFont != null) numText.font = tmpFont;
                numText.fontSize = 12;
                numText.text = (i == 9) ? "0" : (i + 1).ToString();
                numText.color = new Color(1f, 0.9f, 0.4f, 1f);
                numText.alignment = TextAlignmentOptions.TopLeft;
                _slotNumbers[i] = numText;

                // Quantity / Stack Count Text
                var countObj = new GameObject("Count");
                countObj.transform.SetParent(slotObj.transform, false);
                var crt = countObj.AddComponent<RectTransform>();
                crt.anchorMin = new Vector2(1f, 0f);
                crt.anchorMax = new Vector2(1f, 0f);
                crt.pivot = new Vector2(1f, 0f);
                crt.anchoredPosition = new Vector2(-2f, 2f);
                crt.sizeDelta = new Vector2(30f, 14f);
                var countText = countObj.AddComponent<TextMeshProUGUI>();
                if (tmpFont != null) countText.font = tmpFont;
                countText.fontSize = 11;
                countText.text = "";
                countText.color = Color.white;
                countText.alignment = TextAlignmentOptions.BottomRight;
                _slotCounts[i] = countText;
            }

            // Selection box indicator
            var selObj = new GameObject("SelectionBox");
            selObj.transform.SetParent(_hotbarRoot.transform, false);
            _selectionFrame = selObj.AddComponent<RectTransform>();
            _selectionFrame.anchorMin = new Vector2(0f, 0.5f);
            _selectionFrame.anchorMax = new Vector2(0f, 0.5f);
            _selectionFrame.pivot = new Vector2(0f, 0.5f);
            _selectionFrame.anchoredPosition = new Vector2(0f, 0f);
            _selectionFrame.sizeDelta = new Vector2(44f, 44f);
            var selImg = selObj.AddComponent<Image>();
            if (slotSelectedSprite != null)
            {
                selImg.sprite = slotSelectedSprite;
                selImg.color = Color.white;
            }
            else
            {
                selImg.color = new Color(1f, 0.85f, 0.2f, 0.5f);
            }
        }

        private void BuildLifeAndMana()
        {
            var oldLife = transform.Find("LifeAndMana");
            if (oldLife != null) DestroyImmediate(oldLife.gameObject);

            var root = new GameObject("LifeAndMana");
            root.transform.SetParent(transform, false);
            var rt = root.AddComponent<RectTransform>();
            rt.anchorMin = new Vector2(1f, 1f);
            rt.anchorMax = new Vector2(1f, 1f);
            rt.pivot = new Vector2(1f, 1f);
            rt.anchoredPosition = new Vector2(-16f, -16f);
            rt.sizeDelta = new Vector2(280f, 90f);

            // Life text readout: Life: 605 / 605 (Lv.16)
            var lifeTextObj = new GameObject("LifeText");
            lifeTextObj.transform.SetParent(root.transform, false);
            var lrt = lifeTextObj.AddComponent<RectTransform>();
            lrt.anchorMin = new Vector2(1f, 1f);
            lrt.anchorMax = new Vector2(1f, 1f);
            lrt.pivot = new Vector2(1f, 1f);
            lrt.anchoredPosition = new Vector2(0f, 0f);
            lrt.sizeDelta = new Vector2(280f, 18f);
            _lifeText = lifeTextObj.AddComponent<TextMeshProUGUI>();
            if (tmpFont != null) _lifeText.font = tmpFont;
            _lifeText.fontSize = 14;
            _lifeText.alignment = TextAlignmentOptions.Right;
            _lifeText.color = new Color(1.0f, 0.4f, 0.4f, 1f);
            _lifeText.text = "Life: 100 / 100 (Lv.1)";

            // Hearts grid (row of 10 hearts)
            var heartsContainer = new GameObject("HeartsGrid");
            heartsContainer.transform.SetParent(root.transform, false);
            var hrt = heartsContainer.AddComponent<RectTransform>();
            hrt.anchorMin = new Vector2(1f, 1f);
            hrt.anchorMax = new Vector2(1f, 1f);
            hrt.pivot = new Vector2(1f, 1f);
            hrt.anchoredPosition = new Vector2(0f, -20f);
            hrt.sizeDelta = new Vector2(200f, 20f);

            for (int i = 0; i < 10; i++)
            {
                var hObj = new GameObject($"Heart_{i}");
                hObj.transform.SetParent(heartsContainer.transform, false);
                var hObjRt = hObj.AddComponent<RectTransform>();
                hObjRt.anchorMin = new Vector2(1f, 0.5f);
                hObjRt.anchorMax = new Vector2(1f, 0.5f);
                hObjRt.pivot = new Vector2(1f, 0.5f);
                hObjRt.anchoredPosition = new Vector2(-((9 - i) * 20f), 0f);
                hObjRt.sizeDelta = new Vector2(18f, 18f);

                var img = hObj.AddComponent<Image>();
                img.sprite = heartFullSprite;
                img.color = Color.white;
                _heartIcons[i] = img;
            }

            // Mana text readout: MP: 170 / 170
            var manaTextObj = new GameObject("ManaText");
            manaTextObj.transform.SetParent(root.transform, false);
            var mrt = manaTextObj.AddComponent<RectTransform>();
            mrt.anchorMin = new Vector2(1f, 1f);
            mrt.anchorMax = new Vector2(1f, 1f);
            mrt.pivot = new Vector2(1f, 1f);
            mrt.anchoredPosition = new Vector2(0f, -44f);
            mrt.sizeDelta = new Vector2(280f, 18f);
            _manaText = manaTextObj.AddComponent<TextMeshProUGUI>();
            if (tmpFont != null) _manaText.font = tmpFont;
            _manaText.fontSize = 14;
            _manaText.alignment = TextAlignmentOptions.Right;
            _manaText.color = new Color(0.4f, 0.7f, 1.0f, 1f);
            _manaText.text = "MP: 50 / 50";

            // Mana Bar Background & Fill
            var manaBarBg = new GameObject("ManaBarBg");
            manaBarBg.transform.SetParent(root.transform, false);
            var mbrt = manaBarBg.AddComponent<RectTransform>();
            mbrt.anchorMin = new Vector2(1f, 1f);
            mbrt.anchorMax = new Vector2(1f, 1f);
            mbrt.pivot = new Vector2(1f, 1f);
            mbrt.anchoredPosition = new Vector2(0f, -64f);
            mbrt.sizeDelta = new Vector2(200f, 14f);
            var bgImg = manaBarBg.AddComponent<Image>();
            bgImg.color = new Color(0.1f, 0.15f, 0.25f, 0.85f);

            var manaFillObj = new GameObject("Fill");
            manaFillObj.transform.SetParent(manaBarBg.transform, false);
            var mfrt = manaFillObj.AddComponent<RectTransform>();
            mfrt.anchorMin = new Vector2(0f, 0f);
            mfrt.anchorMax = new Vector2(1f, 1f);
            mfrt.offsetMin = new Vector2(2f, 2f);
            mfrt.offsetMax = new Vector2(-2f, -2f);
            _manaBarFill = manaFillObj.AddComponent<Image>();
            _manaBarFill.color = new Color(0.2f, 0.55f, 0.95f, 1.0f);
        }

        private void BuildClockAndRadar()
        {
            var oldClock = transform.Find("ClockAndRadar");
            if (oldClock != null) DestroyImmediate(oldClock.gameObject);

            var root = new GameObject("ClockAndRadar");
            root.transform.SetParent(transform, false);
            var rt = root.AddComponent<RectTransform>();
            rt.anchorMin = new Vector2(1f, 1f);
            rt.anchorMax = new Vector2(1f, 1f);
            rt.pivot = new Vector2(1f, 1f);
            rt.anchoredPosition = new Vector2(-16f, -112f);
            rt.sizeDelta = new Vector2(280f, 32f);

            // Radar Badge [M]
            var radarObj = new GameObject("RadarBadge");
            radarObj.transform.SetParent(root.transform, false);
            var rrt = radarObj.AddComponent<RectTransform>();
            rrt.anchorMin = new Vector2(0f, 0.5f);
            rrt.anchorMax = new Vector2(0f, 0.5f);
            rrt.pivot = new Vector2(0f, 0.5f);
            rrt.anchoredPosition = new Vector2(0f, 0f);
            rrt.sizeDelta = new Vector2(90f, 24f);

            var radarBg = radarObj.AddComponent<Image>();
            radarBg.color = new Color(0.12f, 0.16f, 0.22f, 0.85f);

            var radarTextObj = new GameObject("Text");
            radarTextObj.transform.SetParent(radarObj.transform, false);
            var rtrt = radarTextObj.AddComponent<RectTransform>();
            rtrt.anchorMin = Vector2.zero;
            rtrt.anchorMax = Vector2.one;
            rtrt.offsetMin = Vector2.zero;
            rtrt.offsetMax = Vector2.zero;
            _radarText = radarTextObj.AddComponent<TextMeshProUGUI>();
            if (tmpFont != null) _radarText.font = tmpFont;
            _radarText.fontSize = 11;
            _radarText.alignment = TextAlignmentOptions.Center;
            _radarText.color = new Color(0.85f, 0.95f, 1.0f, 1f);
            _radarText.text = "[M] RADAR";

            // Clock Badge: 12:00 PM DAY / 7:04 PM NIGHT
            var clockObj = new GameObject("ClockBadge");
            clockObj.transform.SetParent(root.transform, false);
            var crt = clockObj.AddComponent<RectTransform>();
            crt.anchorMin = new Vector2(1f, 0.5f);
            crt.anchorMax = new Vector2(1f, 0.5f);
            crt.pivot = new Vector2(1f, 0.5f);
            crt.anchoredPosition = new Vector2(0f, 0f);
            crt.sizeDelta = new Vector2(170f, 24f);

            var clockBg = clockObj.AddComponent<Image>();
            clockBg.color = new Color(0.12f, 0.16f, 0.22f, 0.85f);

            var clockTextObj = new GameObject("Text");
            clockTextObj.transform.SetParent(clockObj.transform, false);
            var ctrt = clockTextObj.AddComponent<RectTransform>();
            ctrt.anchorMin = Vector2.zero;
            ctrt.anchorMax = Vector2.one;
            ctrt.offsetMin = Vector2.zero;
            ctrt.offsetMax = Vector2.zero;
            _clockText = clockTextObj.AddComponent<TextMeshProUGUI>();
            if (tmpFont != null) _clockText.font = tmpFont;
            _clockText.fontSize = 11;
            _clockText.alignment = TextAlignmentOptions.Center;
            _clockText.color = new Color(1.0f, 0.9f, 0.4f, 1f);
            _clockText.text = "12:00 PM DAY";
        }

        private void BuildSkillBadges()
        {
            var oldSkills = transform.Find("SkillBadges");
            if (oldSkills != null) DestroyImmediate(oldSkills.gameObject);

            var root = new GameObject("SkillBadges");
            root.transform.SetParent(transform, false);
            var rt = root.AddComponent<RectTransform>();
            rt.anchorMin = new Vector2(0.5f, 0f);
            rt.anchorMax = new Vector2(0.5f, 0f);
            rt.pivot = new Vector2(0.5f, 0f);
            rt.anchoredPosition = new Vector2(0f, 14f);
            rt.sizeDelta = new Vector2(340f, 44f);

            string[] keys = { "Q", "F", "V", "R" };
            int[] levels = { 1, 2, 1, 1 };
            string[] defaultAbbrs = { "SWI", "CEL", "POW", "WHI" };

            for (int i = 0; i < 4; i++)
            {
                var badge = new GameObject($"Skill_{keys[i]}");
                badge.transform.SetParent(root.transform, false);
                var brt = badge.AddComponent<RectTransform>();
                brt.anchorMin = new Vector2(0f, 0.5f);
                brt.anchorMax = new Vector2(0f, 0.5f);
                brt.pivot = new Vector2(0f, 0.5f);
                brt.anchoredPosition = new Vector2(i * 85f, 0f);
                brt.sizeDelta = new Vector2(78f, 36f);

                var bgImg = badge.AddComponent<Image>();
                bgImg.color = new Color(0.12f, 0.15f, 0.22f, 0.9f);
                _skillBadges[i] = bgImg;

                var textObj = new GameObject("Text");
                textObj.transform.SetParent(badge.transform, false);
                var trt = textObj.AddComponent<RectTransform>();
                trt.anchorMin = Vector2.zero;
                trt.anchorMax = Vector2.one;
                trt.offsetMin = Vector2.zero;
                trt.offsetMax = Vector2.zero;
                var text = textObj.AddComponent<TextMeshProUGUI>();
                if (tmpFont != null) text.font = tmpFont;
                text.fontSize = 11;
                text.alignment = TextAlignmentOptions.Center;
                text.color = new Color(1f, 0.95f, 0.7f, 1f);
                text.text = $"{keys[i]} Lv.{levels[i]} {defaultAbbrs[i]}";
                _skillTexts[i] = text;

                // Cooldown overlay
                var cdObj = new GameObject("CD");
                cdObj.transform.SetParent(badge.transform, false);
                var cdrt = cdObj.AddComponent<RectTransform>();
                cdrt.anchorMin = Vector2.zero;
                cdrt.anchorMax = Vector2.one;
                cdrt.offsetMin = Vector2.zero;
                cdrt.offsetMax = Vector2.zero;
                var cdImg = cdObj.AddComponent<Image>();
                cdImg.color = new Color(0f, 0f, 0f, 0f);
                _skillCooldownOverlays[i] = cdImg;
            }
        }

        private void BuildProfiler()
        {
            var oldProf = transform.Find("ProfilerPanel");
            if (oldProf != null) DestroyImmediate(oldProf.gameObject);

            _profilerPanel = new GameObject("ProfilerPanel");
            _profilerPanel.transform.SetParent(transform, false);
            var rt = _profilerPanel.AddComponent<RectTransform>();
            rt.anchorMin = new Vector2(0f, 0.5f);
            rt.anchorMax = new Vector2(0f, 0.5f);
            rt.pivot = new Vector2(0f, 0.5f);
            rt.anchoredPosition = new Vector2(16f, 0f);
            rt.sizeDelta = new Vector2(300f, 160f);

            var bg = _profilerPanel.AddComponent<Image>();
            bg.color = new Color(0.05f, 0.08f, 0.12f, 0.88f);

            var textObj = new GameObject("ProfilerText");
            textObj.transform.SetParent(_profilerPanel.transform, false);
            var trt = textObj.AddComponent<RectTransform>();
            trt.anchorMin = Vector2.zero;
            trt.anchorMax = Vector2.one;
            trt.offsetMin = new Vector2(8f, 8f);
            trt.offsetMax = new Vector2(-8f, -8f);

            _profilerText = textObj.AddComponent<TextMeshProUGUI>();
            if (tmpFont != null) _profilerText.font = tmpFont;
            _profilerText.fontSize = 11;
            _profilerText.lineSpacing = 1.15f;
            _profilerText.alignment = TextAlignmentOptions.TopLeft;
            _profilerText.color = new Color(0.85f, 0.95f, 0.8f, 1f);
            _profilerText.text = "Potaria Profiler (F3)";

            _profilerPanel.SetActive(false);
        }

        private void InitializeDefaultHotbarItems()
        {
#if UNITY_EDITOR
            SetItem(0, "item.copper_pickaxe", "Copper Pickaxe", LoadSprite("copper_pickaxe.png"), 1);
            SetItem(1, "item.copper_broadsword", "Copper Broadsword", LoadSprite("copper_broadsword.png"), 1);
            SetItem(2, "item.copper_axe", "Copper Axe", LoadSprite("copper_axe.png"), 1);
            SetItem(3, "item.torch", "Torch", LoadSprite("torch.png"), 99);
            SetItem(4, "item.dirt", "Dirt Block", LoadSprite("dirt.png"), 99);
            SetItem(5, "item.stone", "Stone Block", LoadSprite("stone.png"), 99);
            SetItem(6, "item.wood", "Wood", LoadSprite("wood_planks.png"), 99);
            SetItem(7, "item.gel", "Gel", LoadSprite("slime_0.png"), 42);
            SetItem(8, "item.healing_potion", "Healing Potion", LoadSprite("speed_potion.png"), 5);
            SetItem(9, "item.mana_potion", "Mana Potion", LoadSprite("sweet_tuber_pie.png"), 5);
#endif
        }

#if UNITY_EDITOR
        private Sprite LoadSprite(string filename)
        {
            string[] searchDirs = new[]
            {
                "Assets/Sprites/Craftable_items/",
                "Assets/Sprites/Tiles/",
                "Assets/Sprites/Ui/",
                "Assets/Sprites/Items/",
                "Assets/Sprites/Mobs/",
                "Assets/Sprites/",
                "Assets/craftable_items/",
                "Assets/ui/",
                "Assets/"
            };

            foreach (var dir in searchDirs)
            {
                var sp = UnityEditor.AssetDatabase.LoadAssetAtPath<Sprite>(dir + filename);
                if (sp != null) return sp;
            }
            return null;
        }
#endif

        public void SetItem(int slotIndex, string nameKey, string fallbackName, Sprite icon, int count)
        {
            if (slotIndex < 0 || slotIndex >= 10) return;
            _hotbarData[slotIndex] = new HotbarItem
            {
                id = nameKey,
                nameKey = nameKey,
                icon = icon,
                stack = count
            };

            if (_slotItems[slotIndex] != null)
            {
                if (icon != null)
                {
                    _slotItems[slotIndex].sprite = icon;
                    _slotItems[slotIndex].color = Color.white;
                }
                else
                {
                    _slotItems[slotIndex].sprite = null;
                    _slotItems[slotIndex].color = new Color(1f, 1f, 1f, 0f);
                }
            }

            if (_slotCounts[slotIndex] != null)
            {
                _slotCounts[slotIndex].text = (count > 1) ? count.ToString() : "";
            }
        }

        public HotbarItem GetActiveItem()
        {
            if (_selectedSlot >= 0 && _selectedSlot < _hotbarData.Length)
                return _hotbarData[_selectedSlot];
            return default;
        }

        public HotbarItem GetItem(int index)
        {
            if (index >= 0 && index < _hotbarData.Length)
                return _hotbarData[index];
            return default;
        }

        public void DecrementActiveItem()
        {
            if (_selectedSlot >= 0 && _selectedSlot < _hotbarData.Length)
            {
                if (_hotbarData[_selectedSlot].stack > 0)
                {
                    _hotbarData[_selectedSlot].stack--;
                    if (_hotbarData[_selectedSlot].stack <= 0)
                    {
                        SetItem(_selectedSlot, "", "", null, 0);
                    }
                    else
                    {
                        if (_slotCounts[_selectedSlot] != null)
                            _slotCounts[_selectedSlot].text = _hotbarData[_selectedSlot].stack > 1 ? _hotbarData[_selectedSlot].stack.ToString() : "";
                    }
                }
            }
        }

        private void Update()
        {
            ReadInputHotkeys();
            UpdateStatsDisplay();
            UpdateClockDisplay();
            UpdateProfilerDisplay();
        }

        private void ReadInputHotkeys()
        {
            if (input == null) input = PotariaInput.Instance;
            if (input == null) return;

            // Slot Selection (1-9, 0)
            if (input.HotbarSlotPressed >= 0 && input.HotbarSlotPressed < 10)
            {
                SelectSlot(input.HotbarSlotPressed);
            }

            // Language Toggle (L)
            if (input.LanguageTogglePressed)
            {
                LocalizationManager.ToggleLanguage();
            }

            // Profiler Toggle (F3)
            if (input.ProfilerTogglePressed)
            {
                _profilerActive = !_profilerActive;
                if (_profilerPanel != null) _profilerPanel.SetActive(_profilerActive);
            }

            // Minimap / Radar Toggle (M)
            if (input.MinimapTogglePressed)
            {
                if (_radarText != null)
                {
                    _radarText.color = (_radarText.color.a > 0.6f) ? new Color(0.5f, 0.5f, 0.5f, 0.5f) : new Color(0.85f, 0.95f, 1.0f, 1f);
                }
            }
        }

        public void SelectSlot(int index)
        {
            _selectedSlot = Mathf.Clamp(index, 0, 9);
            if (_selectionFrame != null)
            {
                _selectionFrame.anchoredPosition = new Vector2(_selectedSlot * 44f, 0f);
            }
        }

        private void UpdateStatsDisplay()
        {
            if (playerStats == null && player != null) playerStats = player.Stats;
            if (playerStats == null) return;

            int currentHp = playerStats.CurrentHp;
            int maxHp = playerStats.MaxHp;
            int level = playerStats.Level;

            int currentMp = playerStats.CurrentMp;
            int maxMp = playerStats.MaxMp;

            if (_lifeText != null)
            {
                _lifeText.text = LocalizationManager.GetFormat("hud.life", currentHp, maxHp, level);
            }

            if (_manaText != null)
            {
                _manaText.text = LocalizationManager.GetFormat("hud.mp", currentMp, maxMp);
            }

            // Update heart icons (each represents 10% of max HP)
            float hpRatio = (maxHp > 0) ? Mathf.Clamp01((float)currentHp / maxHp) : 0f;
            int activeHearts = Mathf.CeilToInt(hpRatio * 10f);
            for (int i = 0; i < 10; i++)
            {
                if (_heartIcons[i] != null)
                {
                    _heartIcons[i].sprite = (i < activeHearts) ? heartFullSprite : heartEmptySprite;
                    _heartIcons[i].color = (i < activeHearts) ? Color.white : new Color(0.4f, 0.4f, 0.4f, 0.6f);
                }
            }

            // Update Mana Bar Fill
            if (_manaBarFill != null)
            {
                float mpRatio = (maxMp > 0) ? Mathf.Clamp01((float)currentMp / maxMp) : 0f;
                var rt = _manaBarFill.rectTransform;
                rt.anchorMax = new Vector2(mpRatio, 1f);
            }
        }

        private void UpdateClockDisplay()
        {
            if (dayNightCycle == null) dayNightCycle = FindFirstObjectByType<DayNightCycle2D>();
            if (_clockText == null || dayNightCycle == null) return;

            dayNightCycle.GetClock(out int hour, out int minute, out bool isPm, out bool isNight);
            string amPm = isPm ? "PM" : "AM";
            string phaseStr = isNight ? LocalizationManager.Get("hud.night", "NIGHT") : LocalizationManager.Get("hud.day", "DAY");

            _clockText.text = $"{hour}:{minute:D2} {amPm} {phaseStr}";
        }

        private void UpdateProfilerDisplay()
        {
            if (!_profilerActive || _profilerText == null) return;

            _fpsAccumulator += Time.unscaledDeltaTime;
            _fpsFrames++;
            if (_fpsAccumulator >= 0.5f)
            {
                _currentFps = _fpsFrames / _fpsAccumulator;
                _fpsAccumulator = 0f;
                _fpsFrames = 0;
            }

            Vector2 playerPos = (player != null) ? (Vector2)player.transform.position : Vector2.zero;
            int mobCount = FindObjectsByType<Mob.Mob>(FindObjectsSortMode.None).Length;
            int bulletCount = FindObjectsByType<Combat.Projectile>(FindObjectsSortMode.None).Length;
            float ramMb = (float)(GC.GetTotalMemory(false) / (1024.0 * 1024.0));

            string phase = dayNightCycle != null ? dayNightCycle.CurrentPhase.ToString() : "Noon";
            int hour = 12, min = 0;
            bool isPm = true, isNight = false;
            if (dayNightCycle != null) dayNightCycle.GetClock(out hour, out min, out isPm, out isNight);

            _profilerText.text =
                $"{LocalizationManager.Get("profiler.title", "Potaria Profiler (F3)")}\n" +
                $"FPS: {_currentFps:F1} ({1000f / Mathf.Max(1f, _currentFps):F1} ms)\n" +
                $"Pos: X={playerPos.x:F1}, Y={playerPos.y:F1}\n" +
                $"Time: {hour}:{min:D2} {(isPm ? "PM" : "AM")} ({phase})\n" +
                $"Entities: Mobs={mobCount}, Bullets={bulletCount}\n" +
                $"Memory: {ramMb:F1} MB\n" +
                $"{LocalizationManager.GetFormat("profiler.language", LocalizationManager.CurrentLanguageDisplayName)}";
        }

        public void RefreshLocalizedLabels()
        {
            if (_radarText != null) _radarText.text = LocalizationManager.Get("hud.radar", "[M] RADAR");

            string[] keys = { "Q", "F", "V", "R" };
            string[] abbrKeys = { "skill.q.abbr", "skill.f.abbr", "skill.v.abbr", "skill.r.abbr" };
            int[] levels = { 1, 2, 1, 1 };

            for (int i = 0; i < 4; i++)
            {
                if (_skillTexts[i] != null)
                {
                    string abbr = LocalizationManager.Get(abbrKeys[i]);
                    _skillTexts[i].text = $"{keys[i]} Lv.{levels[i]} {abbr}";
                }
            }

            UpdateStatsDisplay();
            UpdateClockDisplay();
        }
    }
}
