using System;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.UI;
using UnityEngine.EventSystems;
using TMPro;
using Potaria.Data;
using Potaria.RPG;

namespace Potaria.UI
{
    /// <summary>
    /// Master Forge Master Enhancement & Repair UI:
    /// - Enhancement (+1 to +7): success rate (100% to 25%), break risk (0% to 30%), fail penalty
    /// - Affix carving & embedding using Affix Stones up to rarity limit
    /// - 1 Gold equipment durability repair interaction
    /// </summary>
    public class ForgeUI : MonoBehaviour
    {
        private static ForgeUI s_instance;
        public static ForgeUI Instance => s_instance;

        [Header("Target References")]
        [SerializeField] private PlayerInventory inventory;

        [Header("Assets & Sprites")]
        [SerializeField] private TMP_FontAsset tmpFont;
        [SerializeField] private Sprite slotFrameSprite;

        // UI Roots
        private GameObject _panelRoot;
        private bool _isOpen = false;
        public bool IsOpen => _isOpen;

        // Anvil Slot Item
        private InventoryItemInstance _slottedItem = null;
        public InventoryItemInstance SlottedItem => _slottedItem;

        // UI Components
        private Image _slotFrameImg;
        private Image _slotIconImg;
        private TextMeshProUGUI _itemNameText;
        private TextMeshProUGUI _enhancementInfoText;
        private TextMeshProUGUI _costInfoText;
        private TextMeshProUGUI _feedbackMessageText;

        // Action Buttons
        private Button _btnEnhance;
        private Button _btnRepair;
        private Button _btnCarveAffix;
        private Button _btnEmbedStone;

        private void Awake()
        {
            s_instance = this;
            if (inventory == null) inventory = FindFirstObjectByType<PlayerInventory>();

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
            if (slotFrameSprite == null)
            {
                slotFrameSprite = UnityEditor.AssetDatabase.LoadAssetAtPath<Sprite>("Assets/Sprites/Ui/slot_frame.png");
                if (slotFrameSprite == null) slotFrameSprite = UnityEditor.AssetDatabase.LoadAssetAtPath<Sprite>("Assets/ui/slot_frame.png");
            }
#endif
        }

        public void BuildUIHierarchy()
        {
            var oldPanel = transform.Find("ForgePanel");
            if (oldPanel != null) DestroyImmediate(oldPanel.gameObject);

            _panelRoot = new GameObject("ForgePanel");
            _panelRoot.transform.SetParent(transform, false);

            var prt = _panelRoot.AddComponent<RectTransform>();
            prt.anchorMin = new Vector2(0.5f, 0.5f);
            prt.anchorMax = new Vector2(0.5f, 0.5f);
            prt.pivot = new Vector2(0.5f, 0.5f);
            prt.sizeDelta = new Vector2(500f, 380f);
            prt.anchoredPosition = new Vector2(-550f, -40f);

            var bg = _panelRoot.AddComponent<Image>();
            bg.color = new Color(0.09f, 0.08f, 0.07f, 0.96f);

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
            titleText.text = "<color=#FF9900><b>FORGE MASTER ANVIL</b></color> <color=#A0A0A0>(+1 to +7 & Repair)</color>";

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

            // Anvil Slot (Center Top)
            var slotObj = new GameObject("AnvilSlot");
            slotObj.transform.SetParent(_panelRoot.transform, false);
            var srt = slotObj.AddComponent<RectTransform>();
            srt.anchorMin = new Vector2(0.5f, 1f);
            srt.anchorMax = new Vector2(0.5f, 1f);
            srt.pivot = new Vector2(0.5f, 0.5f);
            srt.anchoredPosition = new Vector2(0f, -65f);
            srt.sizeDelta = new Vector2(56f, 56f);

            _slotFrameImg = slotObj.AddComponent<Image>();
            if (slotFrameSprite != null) _slotFrameImg.sprite = slotFrameSprite;
            _slotFrameImg.color = new Color(1f, 0.8f, 0.4f, 1f);

            // Slot Icon
            var iconObj = new GameObject("Icon");
            iconObj.transform.SetParent(slotObj.transform, false);
            var irt = iconObj.AddComponent<RectTransform>();
            irt.anchorMin = Vector2.zero;
            irt.anchorMax = Vector2.one;
            irt.offsetMin = new Vector2(4, 4);
            irt.offsetMax = new Vector2(-4, -4);
            _slotIconImg = iconObj.AddComponent<Image>();
            _slotIconImg.color = new Color(1, 1, 1, 0);
            _slotIconImg.raycastTarget = false;

            // Slot Click Event
            var trigger = slotObj.AddComponent<EventTrigger>();
            var click = new EventTrigger.Entry { eventID = EventTriggerType.PointerClick };
            click.callback.AddListener((_) => HandleAnvilSlotClick());
            trigger.triggers.Add(click);

            // Item Name Text
            var nameObj = new GameObject("ItemNameText");
            nameObj.transform.SetParent(_panelRoot.transform, false);
            var nrt = nameObj.AddComponent<RectTransform>();
            nrt.anchorMin = new Vector2(0f, 1f);
            nrt.anchorMax = new Vector2(1f, 1f);
            nrt.pivot = new Vector2(0.5f, 1f);
            nrt.anchoredPosition = new Vector2(0f, -100f);
            nrt.sizeDelta = new Vector2(-24f, 22f);
            _itemNameText = nameObj.AddComponent<TextMeshProUGUI>();
            if (tmpFont != null) _itemNameText.font = tmpFont;
            _itemNameText.fontSize = 13;
            _itemNameText.fontStyle = FontStyles.Bold;
            _itemNameText.alignment = TextAlignmentOptions.Center;
            _itemNameText.text = "Place equippable gear in anvil slot";

            // Enhancement Details Text
            var detObj = new GameObject("EnhancementDetails");
            detObj.transform.SetParent(_panelRoot.transform, false);
            var drt = detObj.AddComponent<RectTransform>();
            drt.anchorMin = new Vector2(0.5f, 1f);
            drt.anchorMax = new Vector2(0.5f, 1f);
            drt.pivot = new Vector2(0.5f, 1f);
            drt.anchoredPosition = new Vector2(0f, -125f);
            drt.sizeDelta = new Vector2(440f, 60f);

            _enhancementInfoText = detObj.AddComponent<TextMeshProUGUI>();
            if (tmpFont != null) _enhancementInfoText.font = tmpFont;
            _enhancementInfoText.fontSize = 11;
            _enhancementInfoText.alignment = TextAlignmentOptions.Center;
            _enhancementInfoText.text = "";

            // Cost & Materials Text
            var costObj = new GameObject("CostText");
            costObj.transform.SetParent(_panelRoot.transform, false);
            var crt = costObj.AddComponent<RectTransform>();
            crt.anchorMin = new Vector2(0.5f, 1f);
            crt.anchorMax = new Vector2(0.5f, 1f);
            crt.pivot = new Vector2(0.5f, 1f);
            crt.anchoredPosition = new Vector2(0f, -190f);
            crt.sizeDelta = new Vector2(440f, 30f);

            _costInfoText = costObj.AddComponent<TextMeshProUGUI>();
            if (tmpFont != null) _costInfoText.font = tmpFont;
            _costInfoText.fontSize = 11;
            _costInfoText.alignment = TextAlignmentOptions.Center;
            _costInfoText.text = "";

            // Feedback Message Banner
            var fbObj = new GameObject("FeedbackBanner");
            fbObj.transform.SetParent(_panelRoot.transform, false);
            var fbrt = fbObj.AddComponent<RectTransform>();
            fbrt.anchorMin = new Vector2(0.5f, 1f);
            fbrt.anchorMax = new Vector2(0.5f, 1f);
            fbrt.pivot = new Vector2(0.5f, 1f);
            fbrt.anchoredPosition = new Vector2(0f, -225f);
            fbrt.sizeDelta = new Vector2(440f, 32f);

            _feedbackMessageText = fbObj.AddComponent<TextMeshProUGUI>();
            if (tmpFont != null) _feedbackMessageText.font = tmpFont;
            _feedbackMessageText.fontSize = 11;
            _feedbackMessageText.fontStyle = FontStyles.Bold;
            _feedbackMessageText.alignment = TextAlignmentOptions.Center;
            _feedbackMessageText.text = "";

            // Button Bar (Bottom)
            BuildButtonsBar();
        }

        private void BuildButtonsBar()
        {
            var btnBar = new GameObject("ButtonBar");
            btnBar.transform.SetParent(_panelRoot.transform, false);
            var brt = btnBar.AddComponent<RectTransform>();
            brt.anchorMin = new Vector2(0f, 0f);
            brt.anchorMax = new Vector2(1f, 0f);
            brt.pivot = new Vector2(0.5f, 0f);
            brt.anchoredPosition = new Vector2(0f, 14f);
            brt.sizeDelta = new Vector2(-24f, 80f);

            // Row 1: Enhance & Repair
            _btnEnhance = CreateActionButton(btnBar, "BtnEnhance", "ENHANCE GEAR", new Vector2(-115, 42), new Vector2(210, 32), new Color(0.8f, 0.45f, 0.1f, 1f), () =>
            {
                ExecuteEnhance();
            });

            _btnRepair = CreateActionButton(btnBar, "BtnRepair", "REPAIR (1 GOLD)", new Vector2(115, 42), new Vector2(210, 32), new Color(0.2f, 0.55f, 0.3f, 1f), () =>
            {
                ExecuteRepair();
            });

            // Row 2: Carve Affix Slot & Embed Affix Stone
            _btnCarveAffix = CreateActionButton(btnBar, "BtnCarve", "CARVE AFFIX SLOT", new Vector2(-115, 4), new Vector2(210, 30), new Color(0.45f, 0.25f, 0.6f, 1f), () =>
            {
                ExecuteCarveAffix();
            });

            _btnEmbedStone = CreateActionButton(btnBar, "BtnEmbed", "EMBED AFFIX STONE", new Vector2(115, 4), new Vector2(210, 30), new Color(0.25f, 0.4f, 0.65f, 1f), () =>
            {
                ExecuteEmbedStone();
            });
        }

        private Button CreateActionButton(GameObject parent, string name, string label, Vector2 pos, Vector2 size, Color color, Action onClick)
        {
            var obj = new GameObject(name);
            obj.transform.SetParent(parent.transform, false);
            var rt = obj.AddComponent<RectTransform>();
            rt.anchorMin = new Vector2(0.5f, 0f);
            rt.anchorMax = new Vector2(0.5f, 0f);
            rt.pivot = new Vector2(0.5f, 0f);
            rt.anchoredPosition = pos;
            rt.sizeDelta = size;

            var img = obj.AddComponent<Image>();
            img.color = color;

            var btn = obj.AddComponent<Button>();
            btn.targetGraphic = img;
            btn.onClick.AddListener(() => onClick?.Invoke());

            var txtObj = new GameObject("Text");
            txtObj.transform.SetParent(obj.transform, false);
            var trt = txtObj.AddComponent<RectTransform>();
            trt.anchorMin = Vector2.zero;
            trt.anchorMax = Vector2.one;

            var txt = txtObj.AddComponent<TextMeshProUGUI>();
            if (tmpFont != null) txt.font = tmpFont;
            txt.fontSize = 11;
            txt.fontStyle = FontStyles.Bold;
            txt.alignment = TextAlignmentOptions.Center;
            txt.text = label;

            return btn;
        }

        public void SetSlottedItem(InventoryItemInstance item)
        {
            _slottedItem = item;
            RefreshDisplay();
        }

        public void HandleAnvilSlotClick()
        {
            if (inventory == null) inventory = FindFirstObjectByType<PlayerInventory>();
            if (inventory == null) return;

            // If player is holding an item, swap it into anvil slot
            if (inventory.HeldItem != null)
            {
                var held = inventory.HeldItem;
                inventory.HeldItem = _slottedItem;
                _slottedItem = held;
            }
            else if (_slottedItem != null)
            {
                // Take item out of anvil slot into held item
                inventory.HeldItem = _slottedItem;
                _slottedItem = null;
            }

            RefreshDisplay();
        }

        public void RefreshDisplay()
        {
            if (_slottedItem == null)
            {
                if (_slotIconImg != null)
                {
                    _slotIconImg.sprite = null;
                    _slotIconImg.color = new Color(1, 1, 1, 0);
                }
                if (_itemNameText != null) _itemNameText.text = "Place equippable gear in anvil slot";
                if (_enhancementInfoText != null) _enhancementInfoText.text = "";
                if (_costInfoText != null) _costInfoText.text = "";

                if (_btnEnhance != null) _btnEnhance.interactable = false;
                if (_btnRepair != null) _btnRepair.interactable = false;
                if (_btnCarveAffix != null) _btnCarveAffix.interactable = false;
                if (_btnEmbedStone != null) _btnEmbedStone.interactable = false;
                return;
            }

            // Slotted item present
            if (_slotIconImg != null)
            {
                _slotIconImg.sprite = _slottedItem.Icon;
                _slotIconImg.color = _slottedItem.IsBroken ? new Color(1f, 0.4f, 0.4f, 1f) : Color.white;
            }

            string hex = _slottedItem.ItemData.GetRarityHex();
            string enhStr = _slottedItem.EnhancementLevel > 0 ? $" <color=#00D9FF>+{_slottedItem.EnhancementLevel}</color>" : "";
            string brokenStr = _slottedItem.IsBroken ? " <color=#FF4D4D>[BROKEN]</color>" : "";
            if (_itemNameText != null) _itemNameText.text = $"<color={hex}>{_slottedItem.ItemName}</color>{enhStr}{brokenStr}";

            // Enhancement Details
            int curLevel = _slottedItem.EnhancementLevel;
            int nextLevel = curLevel + 1;
            var req = ForgeSystem.GetRequirement(nextLevel);

            if (_slottedItem.IsBroken)
            {
                if (_enhancementInfoText != null)
                    _enhancementInfoText.text = "<color=#FF4D4D><b>ITEM IS BROKEN!</b> Repair it below with 1 Gold Coin to restore functionality.</color>";
                if (_costInfoText != null)
                    _costInfoText.text = "<color=#FFD700>Repair Cost: 1 Gold Coin (10,000 Copper)</color>";

                if (_btnEnhance != null) _btnEnhance.interactable = false;
                if (_btnRepair != null) _btnRepair.interactable = ForgeSystem.CanRepairItem(_slottedItem, inventory, out _);
                if (_btnCarveAffix != null) _btnCarveAffix.interactable = false;
                if (_btnEmbedStone != null) _btnEmbedStone.interactable = false;
            }
            else if (req != null && curLevel < ForgeSystem.MAX_ENHANCEMENT_LEVEL)
            {
                int succPct = Mathf.RoundToInt(req.SuccessRate * 100f);
                int breakPct = Mathf.RoundToInt(req.BreakRate * 100f);
                string breakColor = (breakPct > 0) ? "#FF4D4D" : "#4CD964";

                if (_enhancementInfoText != null)
                {
                    _enhancementInfoText.text =
                        $"Target: <b>+{nextLevel}</b>  |  Success Rate: <color=#4CD964><b>{succPct}%</b></color>  |  Break Risk: <color={breakColor}><b>{breakPct}%</b></color>\n" +
                        $"<color=#A0A0A0>Failure penalty: Materials consumed, level preserved (unless broken)</color>";
                }

                var matParts = new List<string> { $"<color=#FFD700>{req.CopperCost} Copper</color>" };
                foreach (var m in req.Materials)
                {
                    var matData = ItemDatabase.Instance.GetItem(m.Key);
                    string matName = matData != null ? matData.ItemName : m.Key;
                    int have = inventory != null ? inventory.CountItem(m.Key) : 0;
                    string col = have >= m.Value ? "#4CD964" : "#FF4D4D";
                    matParts.Add($"<color={col}>{m.Value}x {matName} ({have})</color>");
                }

                if (_costInfoText != null)
                    _costInfoText.text = "Cost: " + string.Join("  +  ", matParts);

                if (_btnEnhance != null)
                    _btnEnhance.interactable = ForgeSystem.CanEnhanceItem(_slottedItem, inventory, out _);
                if (_btnRepair != null) _btnRepair.interactable = false;

                if (_btnCarveAffix != null)
                    _btnCarveAffix.interactable = ForgeSystem.CanCarveAffixSlot(_slottedItem, inventory, out _);
                if (_btnEmbedStone != null)
                    _btnEmbedStone.interactable = ForgeSystem.CanApplyAffixStone(_slottedItem, inventory, out _);
            }
            else
            {
                if (_enhancementInfoText != null)
                    _enhancementInfoText.text = "<color=#FFD700><b>ITEM AT MAXIMUM ENHANCEMENT (+7)!</b> Double base stats active.</color>";
                if (_costInfoText != null) _costInfoText.text = "";

                if (_btnEnhance != null) _btnEnhance.interactable = false;
                if (_btnRepair != null) _btnRepair.interactable = false;
                if (_btnCarveAffix != null)
                    _btnCarveAffix.interactable = ForgeSystem.CanCarveAffixSlot(_slottedItem, inventory, out _);
                if (_btnEmbedStone != null)
                    _btnEmbedStone.interactable = ForgeSystem.CanApplyAffixStone(_slottedItem, inventory, out _);
            }
        }

        public void ExecuteEnhance(float? forcedRoll = null)
        {
            if (_slottedItem == null) return;
            var outcome = ForgeSystem.EnhanceItem(_slottedItem, inventory, out var msg, forcedRoll);
            if (_feedbackMessageText != null)
            {
                string col = (outcome == EnhanceResult.Success) ? "#4CD964" : (outcome == EnhanceResult.Broken ? "#FF4D4D" : "#FF9900");
                _feedbackMessageText.text = $"<color={col}>{msg}</color>";
            }
            RefreshDisplay();
        }

        public void ExecuteRepair()
        {
            if (_slottedItem == null) return;
            bool success = ForgeSystem.RepairItem(_slottedItem, inventory, out var msg);
            if (_feedbackMessageText != null)
            {
                string col = success ? "#4CD964" : "#FF4D4D";
                _feedbackMessageText.text = $"<color={col}>{msg}</color>";
            }
            RefreshDisplay();
        }

        public void ExecuteCarveAffix()
        {
            if (_slottedItem == null) return;
            bool success = ForgeSystem.CarveAffixSlot(_slottedItem, inventory, out var msg);
            if (_feedbackMessageText != null)
            {
                string col = success ? "#B240E6" : "#FF4D4D";
                _feedbackMessageText.text = $"<color={col}>{msg}</color>";
            }
            RefreshDisplay();
        }

        public void ExecuteEmbedStone(string chosenAffix = null)
        {
            if (_slottedItem == null) return;
            bool success = ForgeSystem.ApplyAffixStone(_slottedItem, inventory, out var msg, chosenAffix);
            if (_feedbackMessageText != null)
            {
                string col = success ? "#FFD700" : "#FF4D4D";
                _feedbackMessageText.text = $"<color={col}>{msg}</color>";
            }
            RefreshDisplay();
        }

        public void Toggle()
        {
            SetOpen(!_isOpen);
        }

        private void Update()
        {
            if (_isOpen && UnityEngine.Input.GetKeyDown(KeyCode.Escape))
            {
                SetOpen(false);
            }
        }

        public void SetOpen(bool open)
        {
            _isOpen = open;
            if (_panelRoot != null) _panelRoot.SetActive(_isOpen);

            if (_isOpen)
            {
                RefreshDisplay();
            }
            else
            {
                // Return slotted item to inventory or held item when closing
                if (_slottedItem != null)
                {
                    if (inventory != null)
                    {
                        if (!inventory.AddItem(_slottedItem))
                        {
                            if (inventory.HeldItem == null)
                                inventory.HeldItem = _slottedItem;
                        }
                    }
                    _slottedItem = null;
                }
            }
        }
    }
}
