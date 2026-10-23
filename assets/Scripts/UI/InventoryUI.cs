using System;
using UnityEngine;
using UnityEngine.UI;
using UnityEngine.EventSystems;
using TMPro;
using Potaria.Data;
using Potaria.RPG;
using Potaria.Input;

namespace Potaria.UI
{
    /// <summary>
    /// Master 40-slot backpack inventory UI (4 rows x 10 columns).
    /// - Toggled with 'E' key
    /// - Full item interaction: slot dragging, swapping, stack splitting, quick-trash, and drop
    /// - Auto-sorting (by Category, Rarity, Name) and gap compaction ([ORGANIZE])
    /// - Seamless integration with the 10-slot Hotbar (slots 0-9)
    /// - Dedicated Coin Purse display (Copper, Silver, Gold with 100:1 conversion)
    /// - Powered by TextMeshProUGUI and responsive at 1920x1080 reference resolution
    /// </summary>
    public class InventoryUI : MonoBehaviour
    {
        private static InventoryUI s_instance;
        public static InventoryUI Instance => s_instance;

        [Header("Target References")]
        [SerializeField] private PlayerInventory inventory;
        [SerializeField] private PlayerEquipment equipment;
        [SerializeField] private CharacterPanelUI characterPanel;
        [SerializeField] private PotariaInput input;

        [Header("Assets & Sprites")]
        [SerializeField] private TMP_FontAsset tmpFont;
        [SerializeField] private Sprite slotFrameSprite;
        [SerializeField] private Sprite hotbarFrameSprite;
        [SerializeField] private Sprite coinCopperSprite;
        [SerializeField] private Sprite coinSilverSprite;
        [SerializeField] private Sprite coinGoldSprite;

        // UI Panels & Slots
        private GameObject _panelRoot;
        private readonly Image[] _slotFrames = new Image[PlayerInventory.TOTAL_SLOTS];
        private readonly Image[] _slotIcons = new Image[PlayerInventory.TOTAL_SLOTS];
        private readonly TextMeshProUGUI[] _slotCounts = new TextMeshProUGUI[PlayerInventory.TOTAL_SLOTS];

        // Held Item Follower (for drag-and-drop)
        private GameObject _heldItemObj;
        private Image _heldItemIcon;
        private TextMeshProUGUI _heldItemCount;

        // Coin Purse Texts
        private TextMeshProUGUI _copperText;
        private TextMeshProUGUI _silverText;
        private TextMeshProUGUI _goldText;

        // Trash Slot
        private Image _trashSlotFrame;

        private bool _isOpen = false;
        public bool IsOpen => _isOpen;

        private int _hoveredSlot = -1;

        private void Awake()
        {
            s_instance = this;
            if (inventory == null) inventory = FindFirstObjectByType<PlayerInventory>();
            if (equipment == null) equipment = FindFirstObjectByType<PlayerEquipment>();
            if (characterPanel == null) characterPanel = FindFirstObjectByType<CharacterPanelUI>();
            if (input == null) input = PotariaInput.Instance;

            LoadResourcesIfMissing();
            BuildUIHierarchy();
            SetOpen(false);
        }

        private void OnEnable()
        {
            if (inventory != null)
            {
                inventory.OnSlotChanged += HandleSlotChanged;
                inventory.OnCoinsChanged += HandleCoinsChanged;
                inventory.OnInventoryChanged += RefreshAllSlots;
            }
        }

        private void OnDisable()
        {
            if (inventory != null)
            {
                inventory.OnSlotChanged -= HandleSlotChanged;
                inventory.OnCoinsChanged -= HandleCoinsChanged;
                inventory.OnInventoryChanged -= RefreshAllSlots;
            }
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
            if (coinCopperSprite == null)
            {
                coinCopperSprite = UnityEditor.AssetDatabase.LoadAssetAtPath<Sprite>("Assets/Sprites/Items/copper_coin.png");
            }
            if (coinSilverSprite == null)
            {
                coinSilverSprite = UnityEditor.AssetDatabase.LoadAssetAtPath<Sprite>("Assets/Sprites/Items/silver_coin.png");
            }
            if (coinGoldSprite == null)
            {
                coinGoldSprite = UnityEditor.AssetDatabase.LoadAssetAtPath<Sprite>("Assets/Sprites/Items/gold_coin.png");
            }
#endif
        }

        public void BuildUIHierarchy()
        {
            var oldPanel = transform.Find("InventoryPanel");
            if (oldPanel != null) DestroyImmediate(oldPanel.gameObject);

            _panelRoot = new GameObject("InventoryPanel");
            _panelRoot.transform.SetParent(transform, false);

            var prt = _panelRoot.AddComponent<RectTransform>();
            prt.anchorMin = new Vector2(0.5f, 0.5f);
            prt.anchorMax = new Vector2(0.5f, 0.5f);
            prt.pivot = new Vector2(0.5f, 0.5f);
            prt.sizeDelta = new Vector2(520f, 320f);
            prt.anchoredPosition = new Vector2(0f, -40f);

            var bg = _panelRoot.AddComponent<Image>();
            bg.color = new Color(0.06f, 0.07f, 0.09f, 0.95f);

            // Title Bar
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
            titleText.text = "<color=#FFD700><b>BACKPACK INVENTORY</b></color> <color=#A0A0A0>(40 Slots)</color>";

            // Header Buttons: [CRAFT], [FORGE], [CHAR], [X]
            CreateButton(titleObj, "BtnCraft", "CRAFT", new Vector2(245f, 0), new Vector2(50, 20), () => CraftingUI.Instance?.Toggle());
            CreateButton(titleObj, "BtnForge", "FORGE", new Vector2(300f, 0), new Vector2(50, 20), () => ForgeUI.Instance?.Toggle());
            CreateButton(titleObj, "BtnChar", "CHAR", new Vector2(355f, 0), new Vector2(46, 20), () => CharacterPanelUI.Instance?.Toggle());
            CreateButton(titleObj, "BtnClose", "X", new Vector2(415f, 0), new Vector2(24, 20), () => SetOpen(false));

            // Grid Container (4 rows x 10 cols)
            var gridObj = new GameObject("Grid");
            gridObj.transform.SetParent(_panelRoot.transform, false);
            var grt = gridObj.AddComponent<RectTransform>();
            grt.anchorMin = new Vector2(0f, 1f);
            grt.anchorMax = new Vector2(1f, 1f);
            grt.pivot = new Vector2(0.5f, 1f);
            grt.anchoredPosition = new Vector2(0f, -38f);
            grt.sizeDelta = new Vector2(480f, 190f);

            float startX = -215f;
            float startY = -8f;
            float stepX = 48f;
            float stepY = 46f;

            for (int r = 0; r < PlayerInventory.INVENTORY_ROWS; r++)
            {
                for (int c = 0; c < PlayerInventory.INVENTORY_COLS; c++)
                {
                    int index = r * PlayerInventory.INVENTORY_COLS + c;

                    var slotObj = new GameObject($"Slot_{index}");
                    slotObj.transform.SetParent(gridObj.transform, false);
                    var srt = slotObj.AddComponent<RectTransform>();
                    srt.anchorMin = new Vector2(0.5f, 1f);
                    srt.anchorMax = new Vector2(0.5f, 1f);
                    srt.pivot = new Vector2(0.5f, 0.5f);
                    srt.anchoredPosition = new Vector2(startX + (c * stepX), startY - (r * stepY));
                    srt.sizeDelta = new Vector2(42f, 42f);

                    var frameImg = slotObj.AddComponent<Image>();
                    if (slotFrameSprite != null) frameImg.sprite = slotFrameSprite;
                    // Hotbar row (0) gets subtle golden frame tint
                    frameImg.color = (r == 0) ? new Color(1f, 0.92f, 0.65f, 1f) : new Color(0.85f, 0.85f, 0.9f, 0.95f);
                    _slotFrames[index] = frameImg;

                    // Icon
                    var iconObj = new GameObject("Icon");
                    iconObj.transform.SetParent(slotObj.transform, false);
                    var irt = iconObj.AddComponent<RectTransform>();
                    irt.anchorMin = Vector2.zero;
                    irt.anchorMax = Vector2.one;
                    irt.offsetMin = new Vector2(4, 4);
                    irt.offsetMax = new Vector2(-4, -4);
                    var iconImg = iconObj.AddComponent<Image>();
                    iconImg.color = new Color(1, 1, 1, 0); // invisible until item set
                    iconImg.raycastTarget = false;
                    _slotIcons[index] = iconImg;

                    // Count
                    var countObj = new GameObject("Count");
                    countObj.transform.SetParent(slotObj.transform, false);
                    var crt = countObj.AddComponent<RectTransform>();
                    crt.anchorMin = new Vector2(0f, 0f);
                    crt.anchorMax = new Vector2(1f, 0f);
                    crt.pivot = new Vector2(1f, 0f);
                    crt.anchoredPosition = new Vector2(-2, 2);
                    crt.sizeDelta = new Vector2(0, 14);

                    var countTxt = countObj.AddComponent<TextMeshProUGUI>();
                    if (tmpFont != null) countTxt.font = tmpFont;
                    countTxt.fontSize = 11;
                    countTxt.fontStyle = FontStyles.Bold;
                    countTxt.alignment = TextAlignmentOptions.BottomRight;
                    countTxt.text = "";
                    countTxt.raycastTarget = false;
                    _slotCounts[index] = countTxt;

                    // Add Event Trigger for Click & Hover
                    AddSlotEventTriggers(slotObj, index);
                }
            }

            // Bottom Bar: Coin Purse + Action Buttons
            BuildBottomBar();

            // Dragged Item Floating Icon
            BuildHeldItemFollower();
        }

        private void BuildBottomBar()
        {
            var barObj = new GameObject("BottomBar");
            barObj.transform.SetParent(_panelRoot.transform, false);
            var brt = barObj.AddComponent<RectTransform>();
            brt.anchorMin = new Vector2(0f, 0f);
            brt.anchorMax = new Vector2(1f, 0f);
            brt.pivot = new Vector2(0.5f, 0f);
            brt.anchoredPosition = new Vector2(0f, 10f);
            brt.sizeDelta = new Vector2(-24f, 40f);

            // 1. Coin Purse (Left)
            var coinPurseObj = new GameObject("CoinPurse");
            coinPurseObj.transform.SetParent(barObj.transform, false);
            var cprt = coinPurseObj.AddComponent<RectTransform>();
            cprt.anchorMin = new Vector2(0f, 0.5f);
            cprt.anchorMax = new Vector2(0f, 0.5f);
            cprt.pivot = new Vector2(0f, 0.5f);
            cprt.anchoredPosition = new Vector2(4f, 0f);
            cprt.sizeDelta = new Vector2(210f, 32f);

            // Gold
            CreateCoinBadge(coinPurseObj, "GoldBadge", coinGoldSprite, new Vector2(0, 0), "<color=#FFD700>0g</color>", out _goldText);
            // Silver
            CreateCoinBadge(coinPurseObj, "SilverBadge", coinSilverSprite, new Vector2(65, 0), "<color=#D0D0E0>0s</color>", out _silverText);
            // Copper
            CreateCoinBadge(coinPurseObj, "CopperBadge", coinCopperSprite, new Vector2(130, 0), "<color=#E69138>0c</color>", out _copperText);

            // 2. Buttons: [ORGANIZE], [SORT], [TRASH] (Right)
            float btnX = 220f;
            CreateButton(barObj, "BtnOrganize", "ORGANIZE", new Vector2(btnX, 0), new Vector2(76, 26), () =>
            {
                if (inventory != null) inventory.Organize(true);
            });

            CreateButton(barObj, "BtnSortCat", "CAT", new Vector2(btnX + 80, 0), new Vector2(46, 26), () =>
            {
                if (inventory != null) inventory.SortByCategory(false);
            });

            CreateButton(barObj, "BtnSortRar", "RAR", new Vector2(btnX + 130, 0), new Vector2(46, 26), () =>
            {
                if (inventory != null) inventory.SortByRarity(false);
            });

            CreateButton(barObj, "BtnSortName", "NAME", new Vector2(btnX + 180, 0), new Vector2(50, 26), () =>
            {
                if (inventory != null) inventory.SortByName(false);
            });

            // Trash Slot
            var trashObj = new GameObject("TrashSlot");
            trashObj.transform.SetParent(barObj.transform, false);
            var trt = trashObj.AddComponent<RectTransform>();
            trt.anchorMin = new Vector2(0f, 0.5f);
            trt.anchorMax = new Vector2(0f, 0.5f);
            trt.pivot = new Vector2(0f, 0.5f);
            trt.anchoredPosition = new Vector2(btnX + 238, 0);
            trt.sizeDelta = new Vector2(30f, 30f);

            _trashSlotFrame = trashObj.AddComponent<Image>();
            _trashSlotFrame.color = new Color(0.8f, 0.2f, 0.2f, 0.8f);

            var trashLabel = new GameObject("TrashLabel");
            trashLabel.transform.SetParent(trashObj.transform, false);
            var tlrt = trashLabel.AddComponent<RectTransform>();
            tlrt.anchorMin = Vector2.zero;
            tlrt.anchorMax = Vector2.one;
            var tlt = trashLabel.AddComponent<TextMeshProUGUI>();
            if (tmpFont != null) tlt.font = tmpFont;
            tlt.fontSize = 9;
            tlt.alignment = TextAlignmentOptions.Center;
            tlt.text = "TRASH";

            var trigger = trashObj.AddComponent<EventTrigger>();
            var clickEntry = new EventTrigger.Entry { eventID = EventTriggerType.PointerClick };
            clickEntry.callback.AddListener((_) => HandleTrashClick());
            trigger.triggers.Add(clickEntry);
        }

        private void CreateCoinBadge(GameObject parent, string name, Sprite iconSprite, Vector2 pos, string defaultTxt, out TextMeshProUGUI textComp)
        {
            var badge = new GameObject(name);
            badge.transform.SetParent(parent.transform, false);
            var rt = badge.AddComponent<RectTransform>();
            rt.anchorMin = new Vector2(0f, 0.5f);
            rt.anchorMax = new Vector2(0f, 0.5f);
            rt.pivot = new Vector2(0f, 0.5f);
            rt.anchoredPosition = pos;
            rt.sizeDelta = new Vector2(60f, 24f);

            var iconObj = new GameObject("CoinIcon");
            iconObj.transform.SetParent(badge.transform, false);
            var irt = iconObj.AddComponent<RectTransform>();
            irt.anchorMin = new Vector2(0f, 0.5f);
            irt.anchorMax = new Vector2(0f, 0.5f);
            irt.pivot = new Vector2(0f, 0.5f);
            irt.anchoredPosition = new Vector2(0, 0);
            irt.sizeDelta = new Vector2(18f, 18f);
            var iconImg = iconObj.AddComponent<Image>();
            if (iconSprite != null) iconImg.sprite = iconSprite;

            var txtObj = new GameObject("Text");
            txtObj.transform.SetParent(badge.transform, false);
            var trt = txtObj.AddComponent<RectTransform>();
            trt.anchorMin = new Vector2(0f, 0f);
            trt.anchorMax = new Vector2(1f, 1f);
            trt.offsetMin = new Vector2(22, 0);
            trt.offsetMax = Vector2.zero;

            textComp = txtObj.AddComponent<TextMeshProUGUI>();
            if (tmpFont != null) textComp.font = tmpFont;
            textComp.fontSize = 12;
            textComp.alignment = TextAlignmentOptions.Left;
            textComp.text = defaultTxt;
        }

        private void CreateButton(GameObject parent, string name, string label, Vector2 pos, Vector2 size, Action onClick)
        {
            var btnObj = new GameObject(name);
            btnObj.transform.SetParent(parent.transform, false);
            var rt = btnObj.AddComponent<RectTransform>();
            rt.anchorMin = new Vector2(0f, 0.5f);
            rt.anchorMax = new Vector2(0f, 0.5f);
            rt.pivot = new Vector2(0f, 0.5f);
            rt.anchoredPosition = pos;
            rt.sizeDelta = size;

            var img = btnObj.AddComponent<Image>();
            img.color = new Color(0.2f, 0.22f, 0.28f, 1f);

            var btn = btnObj.AddComponent<Button>();
            btn.targetGraphic = img;
            btn.onClick.AddListener(() => onClick?.Invoke());

            var txtObj = new GameObject("Text");
            txtObj.transform.SetParent(btnObj.transform, false);
            var trt = txtObj.AddComponent<RectTransform>();
            trt.anchorMin = Vector2.zero;
            trt.anchorMax = Vector2.one;

            var txt = txtObj.AddComponent<TextMeshProUGUI>();
            if (tmpFont != null) txt.font = tmpFont;
            txt.fontSize = 11;
            txt.fontStyle = FontStyles.Bold;
            txt.alignment = TextAlignmentOptions.Center;
            txt.text = label;
        }

        private void BuildHeldItemFollower()
        {
            _heldItemObj = new GameObject("HeldItemFollower");
            _heldItemObj.transform.SetParent(transform, false);
            var rt = _heldItemObj.AddComponent<RectTransform>();
            rt.sizeDelta = new Vector2(40f, 40f);
            rt.pivot = new Vector2(0.5f, 0.5f);

            _heldItemIcon = _heldItemObj.AddComponent<Image>();
            _heldItemIcon.raycastTarget = false;
            _heldItemIcon.color = new Color(1, 1, 1, 0);

            var countObj = new GameObject("Count");
            countObj.transform.SetParent(_heldItemObj.transform, false);
            var crt = countObj.AddComponent<RectTransform>();
            crt.anchorMin = Vector2.zero;
            crt.anchorMax = Vector2.one;
            _heldItemCount = countObj.AddComponent<TextMeshProUGUI>();
            if (tmpFont != null) _heldItemCount.font = tmpFont;
            _heldItemCount.fontSize = 12;
            _heldItemCount.fontStyle = FontStyles.Bold;
            _heldItemCount.alignment = TextAlignmentOptions.BottomRight;
            _heldItemCount.raycastTarget = false;

            _heldItemObj.SetActive(false);
        }

        private void AddSlotEventTriggers(GameObject slotObj, int slotIndex)
        {
            var trigger = slotObj.AddComponent<EventTrigger>();

            // Pointer Click (Left / Right / Shift)
            var click = new EventTrigger.Entry { eventID = EventTriggerType.PointerClick };
            click.callback.AddListener((data) =>
            {
                var pData = (PointerEventData)data;
                HandleSlotClick(slotIndex, pData.button == PointerEventData.InputButton.Right, UnityEngine.Input.GetKey(KeyCode.LeftShift) || UnityEngine.Input.GetKey(KeyCode.RightShift));
            });
            trigger.triggers.Add(click);

            // Pointer Enter (Tooltip)
            var enter = new EventTrigger.Entry { eventID = EventTriggerType.PointerEnter };
            enter.callback.AddListener((_) => HandleSlotPointerEnter(slotIndex));
            trigger.triggers.Add(enter);

            // Pointer Exit
            var exit = new EventTrigger.Entry { eventID = EventTriggerType.PointerExit };
            exit.callback.AddListener((_) => HandleSlotPointerExit(slotIndex));
            trigger.triggers.Add(exit);
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
                RefreshAllSlots();
                UpdateCoinsDisplay();
            }
            else
            {
                if (KatabiTooltipUI.Instance != null) KatabiTooltipUI.Instance.Hide();
                if (_heldItemObj != null) _heldItemObj.SetActive(false);
                // Return held item to inventory if closing
                if (inventory != null && inventory.HeldItem != null)
                {
                    if (inventory.AddItem(inventory.HeldItem))
                    {
                        inventory.HeldItem = null;
                    }
                }
            }
        }

        private void Update()
        {
            // Toggle key E
            if (input == null) input = PotariaInput.Instance;
            if (input != null && input.InventoryPressed)
            {
                Toggle();
            }

            // Update held item position to follow mouse
            if (_isOpen && inventory != null && inventory.HeldItem != null)
            {
                if (_heldItemObj != null)
                {
                    _heldItemObj.SetActive(true);
                    _heldItemObj.transform.position = UnityEngine.Input.mousePosition;
                    if (_heldItemIcon != null)
                    {
                        _heldItemIcon.sprite = inventory.HeldItem.Icon;
                        _heldItemIcon.color = Color.white;
                    }
                    if (_heldItemCount != null)
                    {
                        _heldItemCount.text = inventory.HeldItem.Count > 1 ? inventory.HeldItem.Count.ToString() : "";
                    }
                }
            }
            else
            {
                if (_heldItemObj != null && _heldItemObj.activeSelf)
                {
                    _heldItemObj.SetActive(false);
                }
            }
        }

        private void HandleSlotClick(int slotIndex, bool isRightClick, bool isShiftClick)
        {
            if (inventory == null) return;

            var slotItem = inventory.GetSlot(slotIndex);
            var held = inventory.HeldItem;

            if (isShiftClick)
            {
                // Quick-Transfer: Move into open chest, or equip piece, or move between Hotbar (0..9) and Backpack (10..39)
                if (slotItem != null)
                {
                    // 1. If chest is open, quick-transfer into chest
                    if (ChestUI.Instance != null && ChestUI.Instance.IsOpen && ChestUI.Instance.ActiveChest != null)
                    {
                        if (ChestUI.Instance.ActiveChest.AddItem(slotItem))
                        {
                            inventory.SetSlot(slotIndex, null);
                        }
                        else
                        {
                            inventory.SetSlot(slotIndex, slotItem);
                        }
                        return;
                    }

                    // 2. Check if equippable and character panel is open
                    if (equipment != null && (characterPanel == null || characterPanel.IsOpen) && equipment.GetMatchingSlot(slotItem) >= 0)
                    {
                        if (slotItem.Count > 1)
                        {
                            var one = slotItem.Clone(1);
                            if (equipment.EquipItem(one, -1, inventory))
                            {
                                slotItem.Count -= 1;
                                inventory.SetSlot(slotIndex, slotItem);
                            }
                        }
                        else
                        {
                            inventory.SetSlot(slotIndex, null);
                            if (!equipment.EquipItem(slotItem, -1, inventory))
                            {
                                inventory.SetSlot(slotIndex, slotItem);
                            }
                        }
                        return;
                    }

                    // 3. Otherwise swap between hotbar and backpack
                    int targetStart = (slotIndex < PlayerInventory.HOTBAR_SLOTS) ? PlayerInventory.HOTBAR_SLOTS : 0;
                    int targetEnd = (slotIndex < PlayerInventory.HOTBAR_SLOTS) ? PlayerInventory.TOTAL_SLOTS : PlayerInventory.HOTBAR_SLOTS;

                    for (int i = targetStart; i < targetEnd; i++)
                    {
                        if (inventory.GetSlot(i) == null)
                        {
                            inventory.SwapSlots(slotIndex, i);
                            break;
                        }
                    }
                }
                return;
            }

            if (isRightClick)
            {
                // Right-Click: Pick up single item or split half stack, or place 1 from held item
                if (held == null && slotItem != null)
                {
                    if (slotItem.Count == 1)
                    {
                        inventory.HeldItem = slotItem;
                        inventory.SetSlot(slotIndex, null);
                    }
                    else
                    {
                        int take = (slotItem.Count + 1) / 2;
                        inventory.HeldItem = slotItem.Clone(take);
                        slotItem.Count -= take;
                        inventory.SetSlot(slotIndex, slotItem);
                    }
                }
                else if (held != null)
                {
                    if (slotItem == null)
                    {
                        var one = held.Clone(1);
                        inventory.SetSlot(slotIndex, one);
                        held.Count -= 1;
                        if (held.Count <= 0) inventory.HeldItem = null;
                    }
                    else if (slotItem.CanStackWith(held) && slotItem.Count < slotItem.MaxStack)
                    {
                        slotItem.Count += 1;
                        held.Count -= 1;
                        if (held.Count <= 0) inventory.HeldItem = null;
                        inventory.SetSlot(slotIndex, slotItem);
                    }
                }
                return;
            }

            // Normal Left-Click: Pick up, Swap, or Deposit
            if (held == null)
            {
                if (slotItem != null)
                {
                    inventory.HeldItem = slotItem;
                    inventory.SetSlot(slotIndex, null);
                }
            }
            else
            {
                if (slotItem == null)
                {
                    inventory.SetSlot(slotIndex, held);
                    inventory.HeldItem = null;
                }
                else if (slotItem.CanStackWith(held))
                {
                    int space = slotItem.MaxStack - slotItem.Count;
                    if (space > 0)
                    {
                        int take = Mathf.Min(space, held.Count);
                        slotItem.Count += take;
                        held.Count -= take;
                        if (held.Count <= 0) inventory.HeldItem = null;
                        inventory.SetSlot(slotIndex, slotItem);
                    }
                    else
                    {
                        // Stacks full, swap
                        inventory.HeldItem = slotItem;
                        inventory.SetSlot(slotIndex, held);
                    }
                }
                else
                {
                    // Swap held with slot
                    inventory.HeldItem = slotItem;
                    inventory.SetSlot(slotIndex, held);
                }
            }
        }

        private void HandleTrashClick()
        {
            if (inventory == null) return;
            if (inventory.HeldItem != null)
            {
                inventory.HeldItem = null;
            }
            else if (_hoveredSlot >= 0)
            {
                inventory.TrashItem(_hoveredSlot);
            }
        }

        private void HandleSlotPointerEnter(int slotIndex)
        {
            _hoveredSlot = slotIndex;
            if (inventory == null) return;

            var item = inventory.GetSlot(slotIndex);
            if (item != null && KatabiTooltipUI.Instance != null)
            {
                InventoryItemInstance equippedPiece = null;
                // If CharacterPanel is open, find equipped item in matching slot
                if (characterPanel != null && characterPanel.IsOpen && equipment != null)
                {
                    int matchSlot = equipment.GetMatchingSlot(item);
                    if (matchSlot >= 0)
                    {
                        equippedPiece = equipment.GetEquipped(matchSlot);
                    }
                }

                KatabiTooltipUI.Instance.Show(item, equippedPiece, UnityEngine.Input.mousePosition);
            }
        }

        private void HandleSlotPointerExit(int slotIndex)
        {
            if (_hoveredSlot == slotIndex) _hoveredSlot = -1;
            if (KatabiTooltipUI.Instance != null)
            {
                KatabiTooltipUI.Instance.Hide();
            }
        }

        private void HandleSlotChanged(int slotIndex)
        {
            if (slotIndex < 0 || slotIndex >= PlayerInventory.TOTAL_SLOTS) return;
            UpdateSlotVisual(slotIndex);
        }

        private void HandleCoinsChanged(int c, int s, int g)
        {
            UpdateCoinsDisplay();
        }

        public void RefreshAllSlots()
        {
            for (int i = 0; i < PlayerInventory.TOTAL_SLOTS; i++)
            {
                UpdateSlotVisual(i);
            }
            UpdateCoinsDisplay();
        }

        private void UpdateSlotVisual(int slotIndex)
        {
            if (inventory == null) return;
            var item = inventory.GetSlot(slotIndex);

            if (_slotIcons[slotIndex] != null)
            {
                if (item != null && item.Icon != null)
                {
                    _slotIcons[slotIndex].sprite = item.Icon;
                    _slotIcons[slotIndex].color = Color.white;
                }
                else
                {
                    _slotIcons[slotIndex].sprite = null;
                    _slotIcons[slotIndex].color = new Color(1, 1, 1, 0);
                }
            }

            if (_slotCounts[slotIndex] != null)
            {
                if (item != null && item.Count > 1)
                {
                    _slotCounts[slotIndex].text = item.Count.ToString();
                }
                else
                {
                    _slotCounts[slotIndex].text = "";
                }
            }
        }

        public void UpdateCoinsDisplay()
        {
            if (inventory == null) return;

            if (_goldText != null) _goldText.text = $"<color=#FFD700>{inventory.GoldCoins}g</color>";
            if (_silverText != null) _silverText.text = $"<color=#D0D0E0>{inventory.SilverCoins}s</color>";
            if (_copperText != null) _copperText.text = $"<color=#E69138>{inventory.CopperCoins}c</color>";
        }
    }
}
