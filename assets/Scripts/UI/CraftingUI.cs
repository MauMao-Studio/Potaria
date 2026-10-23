using System;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.UI;
using TMPro;
using Potaria.Data;
using Potaria.RPG;
using Potaria.Player;

namespace Potaria.UI
{
    /// <summary>
    /// 5-Tab Crafting Interface for Potaria:
    /// - 5 Tabs: Hand, Workbench, Furnace, Anvil, and Campfire / Cooking Pot
    /// - Station proximity detection: filters recipes by placed station within 4-block range or shows all
    /// - Material sufficiency check: ingredients highlighted in green (sufficient) or red (insufficient)
    /// - One-click crafting: deducts ingredients and adds output to player inventory
    /// </summary>
    public class CraftingUI : MonoBehaviour
    {
        private static CraftingUI s_instance;
        public static CraftingUI Instance => s_instance;

        [Header("Target References")]
        [SerializeField] private PlayerInventory inventory;
        [SerializeField] private PlayerController player;

        [Header("Assets & Sprites")]
        [SerializeField] private TMP_FontAsset tmpFont;
        [SerializeField] private Sprite tabButtonSprite;
        [SerializeField] private Sprite recipeFrameSprite;

        // UI Roots
        private GameObject _panelRoot;
        private CraftingStation _selectedStation = CraftingStation.Hand;
        private bool _filterByProximity = true;
        private bool _isOpen = false;
        public bool IsOpen => _isOpen;

        // Tabs
        private readonly Button[] _tabButtons = new Button[5];
        private readonly TextMeshProUGUI[] _tabTexts = new TextMeshProUGUI[5];
        private static readonly CraftingStation[] s_stationTabs = new[]
        {
            CraftingStation.Hand,
            CraftingStation.WorkBench,
            CraftingStation.Furnace,
            CraftingStation.Anvil,
            CraftingStation.Campfire
        };
        private static readonly string[] s_tabNames = new[]
        {
            "BY HAND", "WORKBENCH", "FURNACE", "ANVIL", "COOKING POT"
        };

        // Recipe List Scroll Area
        private Transform _recipeContentParent;
        private TextMeshProUGUI _stationStatusText;

        private void Awake()
        {
            s_instance = this;
            if (inventory == null) inventory = FindFirstObjectByType<PlayerInventory>();
            if (player == null) player = FindFirstObjectByType<PlayerController>();

            LoadResourcesIfMissing();
            BuildUIHierarchy();
            SetOpen(false);
        }

        public void LoadResourcesIfMissing()
        {
#if UNITY_EDITOR
            if (tmpFont == null)
            {
                tmpFont = UnityEditor.AssetDatabase.LoadAssetAtPath<TMP_FontAsset>("Assets/TextMesh Pro/Resources/Fonts & Materials/LiberationSans SDF.asset");
                if (tmpFont == null) tmpFont = Resources.Load<TMP_FontAsset>("Fonts & Materials/LiberationSans SDF");
            }
#endif
        }

        public void BuildUIHierarchy()
        {
            var oldPanel = transform.Find("CraftingPanel");
            if (oldPanel != null) DestroyImmediate(oldPanel.gameObject);

            _panelRoot = new GameObject("CraftingPanel");
            _panelRoot.transform.SetParent(transform, false);

            var prt = _panelRoot.AddComponent<RectTransform>();
            prt.anchorMin = new Vector2(0.5f, 0.5f);
            prt.anchorMax = new Vector2(0.5f, 0.5f);
            prt.pivot = new Vector2(0.5f, 0.5f);
            prt.sizeDelta = new Vector2(560f, 420f);
            prt.anchoredPosition = new Vector2(-550f, -40f);

            var bg = _panelRoot.AddComponent<Image>();
            bg.color = new Color(0.06f, 0.08f, 0.10f, 0.96f);

            // Title
            var titleObj = new GameObject("Title");
            titleObj.transform.SetParent(_panelRoot.transform, false);
            var trt = titleObj.AddComponent<RectTransform>();
            trt.anchorMin = new Vector2(0f, 1f);
            trt.anchorMax = new Vector2(1f, 1f);
            trt.pivot = new Vector2(0.5f, 1f);
            trt.anchoredPosition = new Vector2(0f, -8f);
            trt.sizeDelta = new Vector2(-24f, 24f);

            var titleText = titleObj.AddComponent<TextMeshProUGUI>();
            if (tmpFont != null) titleText.font = tmpFont;
            titleText.fontSize = 16;
            titleText.fontStyle = FontStyles.Bold;
            titleText.text = "<color=#FFD700><b>CRAFTING LEDGER</b></color> <color=#A0A0A0>(5 Stations)</color>";

            var closeBtnObj = new GameObject("CloseButton");
            closeBtnObj.transform.SetParent(titleObj.transform, false);
            var cbrt = closeBtnObj.AddComponent<RectTransform>();
            cbrt.anchorMin = new Vector2(1f, 0.5f);
            cbrt.anchorMax = new Vector2(1f, 0.5f);
            cbrt.pivot = new Vector2(1f, 0.5f);
            cbrt.anchoredPosition = new Vector2(0f, 0f);
            cbrt.sizeDelta = new Vector2(24f, 22f);
            var cbImg = closeBtnObj.AddComponent<Image>();
            cbImg.color = new Color(0.35f, 0.15f, 0.15f, 1f);
            var cbBtn = closeBtnObj.AddComponent<Button>();
            cbBtn.targetGraphic = cbImg;
            cbBtn.onClick.AddListener(() => SetOpen(false));
            var cbTxtObj = new GameObject("Text");
            cbTxtObj.transform.SetParent(closeBtnObj.transform, false);
            var cbTxtRt = cbTxtObj.AddComponent<RectTransform>();
            cbTxtRt.anchorMin = Vector2.zero;
            cbTxtRt.anchorMax = Vector2.one;
            var cbTxt = cbTxtObj.AddComponent<TextMeshProUGUI>();
            if (tmpFont != null) cbTxt.font = tmpFont;
            cbTxt.fontSize = 11;
            cbTxt.fontStyle = FontStyles.Bold;
            cbTxt.alignment = TextAlignmentOptions.Center;
            cbTxt.text = "X";

            // 5 Tabs Header
            BuildTabsHeader();

            // Status & Filter Toggle
            BuildStatusBar();

            // Scrollable Recipe Area
            BuildRecipeScrollArea();
        }

        private void BuildTabsHeader()
        {
            var tabsObj = new GameObject("TabsHeader");
            tabsObj.transform.SetParent(_panelRoot.transform, false);
            var trt = tabsObj.AddComponent<RectTransform>();
            trt.anchorMin = new Vector2(0f, 1f);
            trt.anchorMax = new Vector2(1f, 1f);
            trt.pivot = new Vector2(0.5f, 1f);
            trt.anchoredPosition = new Vector2(0f, -36f);
            trt.sizeDelta = new Vector2(-24f, 32f);

            float tabW = 102f;
            float spacing = 4f;

            for (int i = 0; i < 5; i++)
            {
                int tabIdx = i;
                var tabObj = new GameObject($"Tab_{i}");
                tabObj.transform.SetParent(tabsObj.transform, false);
                var rt = tabObj.AddComponent<RectTransform>();
                rt.anchorMin = new Vector2(0f, 0.5f);
                rt.anchorMax = new Vector2(0f, 0.5f);
                rt.pivot = new Vector2(0f, 0.5f);
                rt.anchoredPosition = new Vector2(i * (tabW + spacing), 0f);
                rt.sizeDelta = new Vector2(tabW, 28f);

                var img = tabObj.AddComponent<Image>();
                img.color = (i == 0) ? new Color(0.25f, 0.35f, 0.5f, 1f) : new Color(0.12f, 0.15f, 0.2f, 1f);

                var btn = tabObj.AddComponent<Button>();
                btn.targetGraphic = img;
                btn.onClick.AddListener(() => SelectTab(s_stationTabs[tabIdx]));
                _tabButtons[i] = btn;

                var txtObj = new GameObject("Text");
                txtObj.transform.SetParent(tabObj.transform, false);
                var trt2 = txtObj.AddComponent<RectTransform>();
                trt2.anchorMin = Vector2.zero;
                trt2.anchorMax = Vector2.one;

                var txt = txtObj.AddComponent<TextMeshProUGUI>();
                if (tmpFont != null) txt.font = tmpFont;
                txt.fontSize = 10;
                txt.fontStyle = FontStyles.Bold;
                txt.alignment = TextAlignmentOptions.Center;
                txt.text = s_tabNames[i];
                _tabTexts[i] = txt;
            }
        }

        private void BuildStatusBar()
        {
            var barObj = new GameObject("StatusBar");
            barObj.transform.SetParent(_panelRoot.transform, false);
            var brt = barObj.AddComponent<RectTransform>();
            brt.anchorMin = new Vector2(0f, 1f);
            brt.anchorMax = new Vector2(1f, 1f);
            brt.pivot = new Vector2(0.5f, 1f);
            brt.anchoredPosition = new Vector2(0f, -70f);
            brt.sizeDelta = new Vector2(-24f, 20f);

            var txtObj = new GameObject("StatusText");
            txtObj.transform.SetParent(barObj.transform, false);
            var trt = txtObj.AddComponent<RectTransform>();
            trt.anchorMin = new Vector2(0f, 0f);
            trt.anchorMax = new Vector2(0.7f, 1f);
            _stationStatusText = txtObj.AddComponent<TextMeshProUGUI>();
            if (tmpFont != null) _stationStatusText.font = tmpFont;
            _stationStatusText.fontSize = 11;
            _stationStatusText.text = "<color=#4CD964>Station: Available (By Hand)</color>";

            // Filter Toggle Button
            var toggleObj = new GameObject("FilterToggle");
            toggleObj.transform.SetParent(barObj.transform, false);
            var tort = toggleObj.AddComponent<RectTransform>();
            tort.anchorMin = new Vector2(0.7f, 0f);
            tort.anchorMax = new Vector2(1f, 1f);
            var btnImg = toggleObj.AddComponent<Image>();
            btnImg.color = new Color(0.2f, 0.25f, 0.3f, 1f);
            var btn = toggleObj.AddComponent<Button>();
            btn.targetGraphic = btnImg;

            var btnTxtObj = new GameObject("BtnText");
            btnTxtObj.transform.SetParent(toggleObj.transform, false);
            var btrt = btnTxtObj.AddComponent<RectTransform>();
            btrt.anchorMin = Vector2.zero;
            btrt.anchorMax = Vector2.one;
            var btxt = btnTxtObj.AddComponent<TextMeshProUGUI>();
            if (tmpFont != null) btxt.font = tmpFont;
            btxt.fontSize = 10;
            btxt.alignment = TextAlignmentOptions.Center;
            btxt.text = "PROXIMITY: ON";

            btn.onClick.AddListener(() =>
            {
                _filterByProximity = !_filterByProximity;
                btxt.text = _filterByProximity ? "PROXIMITY: ON" : "SHOW ALL";
                RefreshRecipes();
            });
        }

        private void BuildRecipeScrollArea()
        {
            var scrollObj = new GameObject("RecipeScrollView");
            scrollObj.transform.SetParent(_panelRoot.transform, false);
            var srt = scrollObj.AddComponent<RectTransform>();
            srt.anchorMin = new Vector2(0f, 0f);
            srt.anchorMax = new Vector2(1f, 1f);
            srt.offsetMin = new Vector2(14f, 14f);
            srt.offsetMax = new Vector2(-14f, -96f);

            var scrollRect = scrollObj.AddComponent<ScrollRect>();
            scrollRect.horizontal = false;
            scrollRect.vertical = true;
            scrollRect.scrollSensitivity = 25f;

            var viewport = new GameObject("Viewport");
            viewport.transform.SetParent(scrollObj.transform, false);
            var vrt = viewport.AddComponent<RectTransform>();
            vrt.anchorMin = Vector2.zero;
            vrt.anchorMax = Vector2.one;
            viewport.AddComponent<RectMask2D>();
            scrollRect.viewport = vrt;

            var content = new GameObject("Content");
            content.transform.SetParent(viewport.transform, false);
            var crt = content.AddComponent<RectTransform>();
            crt.anchorMin = new Vector2(0f, 1f);
            crt.anchorMax = new Vector2(1f, 1f);
            crt.pivot = new Vector2(0.5f, 1f);
            crt.sizeDelta = new Vector2(0f, 600f);

            var layout = content.AddComponent<VerticalLayoutGroup>();
            layout.childControlWidth = true;
            layout.childControlHeight = false;
            layout.childForceExpandWidth = true;
            layout.childForceExpandHeight = false;
            layout.spacing = 6f;

            var fitter = content.AddComponent<ContentSizeFitter>();
            fitter.verticalFit = ContentSizeFitter.FitMode.PreferredSize;

            scrollRect.content = crt;
            _recipeContentParent = content.transform;
        }

        public void SelectTab(CraftingStation station)
        {
            _selectedStation = station;
            for (int i = 0; i < 5; i++)
            {
                bool active = (s_stationTabs[i] == station);
                if (_tabButtons[i] != null && _tabButtons[i].image != null)
                {
                    _tabButtons[i].image.color = active ? new Color(0.25f, 0.45f, 0.7f, 1f) : new Color(0.12f, 0.15f, 0.2f, 1f);
                }
            }
            RefreshRecipes();
        }

        public bool IsStationNearby(CraftingStation station)
        {
            if (station == CraftingStation.Hand || station == CraftingStation.None) return true;

            // Proximity check within 4.0 blocks of player
            if (player == null) player = FindFirstObjectByType<PlayerController>();
            if (player == null) return true; // fallback if no player in scene

            Vector2 playerPos = player.transform.position;
            float maxDist = 4.5f;

            // Look for nearby crafting station objects or tiles
            var allColliders = Physics2D.OverlapCircleAll(playerPos, maxDist);
            foreach (var col in allColliders)
            {
                string n = col.gameObject.name.ToLowerInvariant();
                switch (station)
                {
                    case CraftingStation.WorkBench:
                        if (n.Contains("workbench") || n.Contains("work_bench")) return true;
                        break;
                    case CraftingStation.Furnace:
                        if (n.Contains("furnace")) return true;
                        break;
                    case CraftingStation.Anvil:
                        if (n.Contains("anvil")) return true;
                        break;
                    case CraftingStation.Campfire:
                        if (n.Contains("campfire") || n.Contains("cookingpot") || n.Contains("fireplace")) return true;
                        break;
                }
            }

            // Fallback: check placed station tags or components
            return false;
        }

        public void RefreshRecipes()
        {
            if (_recipeContentParent == null) return;

            // Clear old recipe rows
            for (int i = _recipeContentParent.childCount - 1; i >= 0; i--)
            {
                Destroy(_recipeContentParent.GetChild(i).gameObject);
            }

            bool nearby = IsStationNearby(_selectedStation);
            if (_stationStatusText != null)
            {
                if (_selectedStation == CraftingStation.Hand)
                {
                    _stationStatusText.text = "<color=#4CD964>Station: Available (By Hand)</color>";
                }
                else
                {
                    _stationStatusText.text = nearby
                        ? $"<color=#4CD964>Station Nearby: {_selectedStation}</color>"
                        : $"<color=#FF4D4D>Station Not Nearby (4-block range): {_selectedStation}</color>";
                }
            }

            if (_filterByProximity && !nearby)
            {
                CreateEmptyMessage($"No placed {_selectedStation} nearby (within 4 blocks).\nToggle 'SHOW ALL' to preview recipes.");
                return;
            }

            var recipes = ItemDatabase.Instance.GetRecipesForStation(_selectedStation);
            if (recipes.Count == 0)
            {
                CreateEmptyMessage($"No recipes found for {_selectedStation}.");
                return;
            }

            foreach (var recipe in recipes)
            {
                CreateRecipeRow(recipe);
            }
        }

        private void CreateEmptyMessage(string message)
        {
            var msgObj = new GameObject("EmptyMsg");
            msgObj.transform.SetParent(_recipeContentParent, false);
            var rt = msgObj.AddComponent<RectTransform>();
            rt.sizeDelta = new Vector2(500f, 60f);

            var tmp = msgObj.AddComponent<TextMeshProUGUI>();
            if (tmpFont != null) tmp.font = tmpFont;
            tmp.fontSize = 12;
            tmp.alignment = TextAlignmentOptions.Center;
            tmp.color = new Color(0.7f, 0.7f, 0.75f, 0.8f);
            tmp.text = message;
        }

        private void CreateRecipeRow(RecipeData recipe)
        {
            var rowObj = new GameObject($"Recipe_{recipe.RecipeId}");
            rowObj.transform.SetParent(_recipeContentParent, false);

            var rrt = rowObj.AddComponent<RectTransform>();
            rrt.sizeDelta = new Vector2(510f, 48f);

            var rowImg = rowObj.AddComponent<Image>();
            rowImg.color = new Color(0.12f, 0.14f, 0.18f, 0.95f);

            // Result Item Icon
            var iconObj = new GameObject("ResultIcon");
            iconObj.transform.SetParent(rowObj.transform, false);
            var irt = iconObj.AddComponent<RectTransform>();
            irt.anchorMin = new Vector2(0f, 0.5f);
            irt.anchorMax = new Vector2(0f, 0.5f);
            irt.pivot = new Vector2(0f, 0.5f);
            irt.anchoredPosition = new Vector2(8f, 0f);
            irt.sizeDelta = new Vector2(36f, 36f);

            var iconImg = iconObj.AddComponent<Image>();
            var resItem = recipe.ResultItemData != null ? recipe.ResultItemData : ItemDatabase.Instance.GetItem(recipe.ResultItemId);
            if (resItem != null && resItem.Icon != null)
            {
                iconImg.sprite = resItem.Icon;
                iconImg.color = Color.white;
            }

            // Recipe Name & Count
            var nameObj = new GameObject("Name");
            nameObj.transform.SetParent(rowObj.transform, false);
            var nrt = nameObj.AddComponent<RectTransform>();
            nrt.anchorMin = new Vector2(0f, 0.5f);
            nrt.anchorMax = new Vector2(0f, 0.5f);
            nrt.pivot = new Vector2(0f, 0.5f);
            nrt.anchoredPosition = new Vector2(50f, 6f);
            nrt.sizeDelta = new Vector2(160f, 18f);

            var nameTxt = nameObj.AddComponent<TextMeshProUGUI>();
            if (tmpFont != null) nameTxt.font = tmpFont;
            nameTxt.fontSize = 12;
            nameTxt.fontStyle = FontStyles.Bold;
            string resName = resItem != null ? resItem.ItemName : recipe.ResultItemId;
            string countStr = recipe.ResultCount > 1 ? $" x{recipe.ResultCount}" : "";
            nameTxt.text = $"{resName}{countStr}";

            // Ingredients List with Green / Red highlights
            var ingObj = new GameObject("Ingredients");
            ingObj.transform.SetParent(rowObj.transform, false);
            var ingrt = ingObj.AddComponent<RectTransform>();
            ingrt.anchorMin = new Vector2(0f, 0.5f);
            ingrt.anchorMax = new Vector2(0f, 0.5f);
            ingrt.pivot = new Vector2(0f, 0.5f);
            ingrt.anchoredPosition = new Vector2(50f, -10f);
            ingrt.sizeDelta = new Vector2(340f, 16f);

            var ingTxt = ingObj.AddComponent<TextMeshProUGUI>();
            if (tmpFont != null) ingTxt.font = tmpFont;
            ingTxt.fontSize = 10;

            bool canCraft = true;
            var ingLines = new List<string>();

            if (inventory == null) inventory = FindFirstObjectByType<PlayerInventory>();

            foreach (var ing in recipe.Ingredients)
            {
                string ingId = (ing.ItemData != null) ? ing.ItemData.ItemId : ing.ItemId;
                int have = (inventory != null) ? inventory.CountItem(ingId) : 0;
                int need = ing.Count;

                var ingData = ItemDatabase.Instance.GetItem(ingId);
                string ingName = ingData != null ? ingData.ItemName : ingId;

                if (have >= need)
                {
                    ingLines.Add($"<color=#4CD964>{have}/{need} {ingName}</color>");
                }
                else
                {
                    ingLines.Add($"<color=#FF4D4D>{have}/{need} {ingName}</color>");
                    canCraft = false;
                }
            }

            ingTxt.text = string.Join("  ", ingLines);

            // Craft Button
            var craftBtnObj = new GameObject("CraftButton");
            craftBtnObj.transform.SetParent(rowObj.transform, false);
            var cbrt = craftBtnObj.AddComponent<RectTransform>();
            cbrt.anchorMin = new Vector2(1f, 0.5f);
            cbrt.anchorMax = new Vector2(1f, 0.5f);
            cbrt.pivot = new Vector2(1f, 0.5f);
            cbrt.anchoredPosition = new Vector2(-8f, 0f);
            cbrt.sizeDelta = new Vector2(72f, 30f);

            var cbImg = craftBtnObj.AddComponent<Image>();
            cbImg.color = canCraft ? new Color(0.2f, 0.65f, 0.35f, 1f) : new Color(0.3f, 0.3f, 0.35f, 0.6f);

            var cb = craftBtnObj.AddComponent<Button>();
            cb.targetGraphic = cbImg;
            cb.interactable = canCraft;

            var cbTxtObj = new GameObject("Text");
            cbTxtObj.transform.SetParent(craftBtnObj.transform, false);
            var cbtrt = cbTxtObj.AddComponent<RectTransform>();
            cbtrt.anchorMin = Vector2.zero;
            cbtrt.anchorMax = Vector2.one;
            var cbTxt = cbTxtObj.AddComponent<TextMeshProUGUI>();
            if (tmpFont != null) cbTxt.font = tmpFont;
            cbTxt.fontSize = 11;
            cbTxt.fontStyle = FontStyles.Bold;
            cbTxt.alignment = TextAlignmentOptions.Center;
            cbTxt.text = "CRAFT";

            cb.onClick.AddListener(() =>
            {
                ExecuteCraft(recipe);
            });
        }

        public bool ExecuteCraft(RecipeData recipe)
        {
            if (recipe == null) return false;
            if (inventory == null) inventory = FindFirstObjectByType<PlayerInventory>();
            if (inventory == null) return false;

            // 1. Verify materials
            foreach (var ing in recipe.Ingredients)
            {
                string ingId = (ing.ItemData != null) ? ing.ItemData.ItemId : ing.ItemId;
                if (inventory.CountItem(ingId) < ing.Count) return false;
            }

            // 2. Resolve result item
            string resId = !string.IsNullOrEmpty(recipe.ResultItemId) ? recipe.ResultItemId : (recipe.ResultItemData != null ? recipe.ResultItemData.ItemId : "");
            var resItem = recipe.ResultItemData != null ? recipe.ResultItemData : (ItemDatabase.Instance != null ? ItemDatabase.Instance.GetItem(resId) : null);
            if (resItem == null) return false;

            // 3. Deduct materials
            var deducted = new List<(ItemData data, string id, int count)>();
            foreach (var ing in recipe.Ingredients)
            {
                string ingId = (ing.ItemData != null) ? ing.ItemData.ItemId : ing.ItemId;
                ItemData ingData = ing.ItemData != null ? ing.ItemData : (ItemDatabase.Instance != null ? ItemDatabase.Instance.GetItem(ingId) : null);
                if (inventory.RemoveItem(ingId, ing.Count))
                {
                    deducted.Add((ingData, ingId, ing.Count));
                }
            }

            // 4. Add result item (refund if inventory full)
            bool added = inventory.AddItem(resItem, recipe.ResultCount);
            if (!added)
            {
                foreach (var (data, id, count) in deducted)
                {
                    if (data != null)
                    {
                        inventory.AddItem(data, count);
                    }
                    else
                    {
                        inventory.AddItem(id, count);
                    }
                }
                return false;
            }

            RefreshRecipes();
            return true;
        }

        public void SelectStation(CraftingStation station)
        {
            SelectTab(station);
        }

        private void Update()
        {
            if (_isOpen && UnityEngine.Input.GetKeyDown(KeyCode.Escape))
            {
                SetOpen(false);
            }
        }

        public void Toggle()
        {
            SetOpen(!_isOpen);
        }

        public void SetOpen(bool open)
        {
            _isOpen = open;
            if (_panelRoot != null) _panelRoot.SetActive(_isOpen);

            if (_isOpen)
            {
                RefreshRecipes();
            }
        }
    }
}
