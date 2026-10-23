using System;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.UI;
using UnityEngine.EventSystems;
using TMPro;
using Potaria.Data;
using Potaria.RPG;
using Potaria.World;

namespace Potaria.UI
{
    /// <summary>
    /// 30-slot Storage Chest Container Interface (3 rows x 10 columns).
    /// - Opened when interacting (right-click) with placed storage chests in the world
    /// - Quick-Deposit: deposits matching items from player inventory into chest
    /// - Loot-All: transfers all items from chest into player inventory
    /// - Slot dragging and swapping between player inventory and chest
    /// </summary>
    public class ChestUI : MonoBehaviour
    {
        private static ChestUI s_instance;
        public static ChestUI Instance => s_instance;

        [Header("Target References")]
        [SerializeField] private PlayerInventory playerInventory;
        [SerializeField] private StorageChest targetChest;

        [Header("Assets & Sprites")]
        [SerializeField] private TMP_FontAsset tmpFont;
        [SerializeField] private Sprite slotFrameSprite;

        // UI Roots
        private GameObject _panelRoot;
        private TextMeshProUGUI _titleText;
        private readonly Image[] _slotFrames = new Image[StorageChest.TOTAL_CHEST_SLOTS];
        private readonly Image[] _slotIcons = new Image[StorageChest.TOTAL_CHEST_SLOTS];
        private readonly TextMeshProUGUI[] _slotCounts = new TextMeshProUGUI[StorageChest.TOTAL_CHEST_SLOTS];

        private bool _isOpen = false;
        public bool IsOpen => _isOpen;

        public StorageChest TargetChest => targetChest;
        public StorageChest ActiveChest => targetChest;

        private void Awake()
        {
            s_instance = this;
            if (playerInventory == null) playerInventory = FindFirstObjectByType<PlayerInventory>();

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
            var oldPanel = transform.Find("ChestPanel");
            if (oldPanel != null) DestroyImmediate(oldPanel.gameObject);

            _panelRoot = new GameObject("ChestPanel");
            _panelRoot.transform.SetParent(transform, false);

            var prt = _panelRoot.AddComponent<RectTransform>();
            prt.anchorMin = new Vector2(0.5f, 0.5f);
            prt.anchorMax = new Vector2(0.5f, 0.5f);
            prt.pivot = new Vector2(0.5f, 0.5f);
            prt.sizeDelta = new Vector2(520f, 260f);
            prt.anchoredPosition = new Vector2(0f, 260f);

            var bg = _panelRoot.AddComponent<Image>();
            bg.color = new Color(0.08f, 0.07f, 0.05f, 0.95f);

            // Title
            var titleObj = new GameObject("Title");
            titleObj.transform.SetParent(_panelRoot.transform, false);
            var trt = titleObj.AddComponent<RectTransform>();
            trt.anchorMin = new Vector2(0f, 1f);
            trt.anchorMax = new Vector2(1f, 1f);
            trt.pivot = new Vector2(0.5f, 1f);
            trt.anchoredPosition = new Vector2(0f, -8f);
            trt.sizeDelta = new Vector2(-24f, 24f);

            _titleText = titleObj.AddComponent<TextMeshProUGUI>();
            if (tmpFont != null) _titleText.font = tmpFont;
            _titleText.fontSize = 15;
            _titleText.fontStyle = FontStyles.Bold;
            _titleText.text = "<color=#E69138><b>WOODEN STORAGE CHEST</b></color> <color=#A0A0A0>(30 Slots)</color>";

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
            cbBtn.onClick.AddListener(() => CloseChest());
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

            // Grid Container (3 rows x 10 cols)
            var gridObj = new GameObject("Grid");
            gridObj.transform.SetParent(_panelRoot.transform, false);
            var grt = gridObj.AddComponent<RectTransform>();
            grt.anchorMin = new Vector2(0f, 1f);
            grt.anchorMax = new Vector2(1f, 1f);
            grt.pivot = new Vector2(0.5f, 1f);
            grt.anchoredPosition = new Vector2(0f, -38f);
            grt.sizeDelta = new Vector2(480f, 150f);

            float startX = -215f;
            float startY = -8f;
            float stepX = 48f;
            float stepY = 46f;

            for (int r = 0; r < StorageChest.CHEST_ROWS; r++)
            {
                for (int c = 0; c < StorageChest.CHEST_COLS; c++)
                {
                    int index = r * StorageChest.CHEST_COLS + c;

                    var slotObj = new GameObject($"ChestSlot_{index}");
                    slotObj.transform.SetParent(gridObj.transform, false);
                    var srt = slotObj.AddComponent<RectTransform>();
                    srt.anchorMin = new Vector2(0.5f, 1f);
                    srt.anchorMax = new Vector2(0.5f, 1f);
                    srt.pivot = new Vector2(0.5f, 0.5f);
                    srt.anchoredPosition = new Vector2(startX + (c * stepX), startY - (r * stepY));
                    srt.sizeDelta = new Vector2(42f, 42f);

                    var frameImg = slotObj.AddComponent<Image>();
                    if (slotFrameSprite != null) frameImg.sprite = slotFrameSprite;
                    frameImg.color = new Color(0.9f, 0.75f, 0.5f, 1f);
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
                    iconImg.color = new Color(1, 1, 1, 0);
                    iconImg.raycastTarget = false;
                    _slotIcons[index] = iconImg;

                    // Count
                    var countObj = new GameObject("Count");
                    countObj.transform.SetParent(slotObj.transform, false);
                    var crt = countObj.AddComponent<RectTransform>();
                    crt.anchorMin = Vector2.zero;
                    crt.anchorMax = Vector2.one;
                    var countTxt = countObj.AddComponent<TextMeshProUGUI>();
                    if (tmpFont != null) countTxt.font = tmpFont;
                    countTxt.fontSize = 11;
                    countTxt.fontStyle = FontStyles.Bold;
                    countTxt.alignment = TextAlignmentOptions.BottomRight;
                    countTxt.raycastTarget = false;
                    _slotCounts[index] = countTxt;

                    // Click Trigger
                    int slotIdx = index;
                    var trigger = slotObj.AddComponent<EventTrigger>();
                    var click = new EventTrigger.Entry { eventID = EventTriggerType.PointerClick };
                    click.callback.AddListener((data) =>
                    {
                        var pData = (PointerEventData)data;
                        HandleChestSlotClick(slotIdx, pData.button == PointerEventData.InputButton.Right, UnityEngine.Input.GetKey(KeyCode.LeftShift) || UnityEngine.Input.GetKey(KeyCode.RightShift));
                    });
                    trigger.triggers.Add(click);

                    var enter = new EventTrigger.Entry { eventID = EventTriggerType.PointerEnter };
                    enter.callback.AddListener((_) => HandleChestSlotPointerEnter(slotIdx));
                    trigger.triggers.Add(enter);

                    var exit = new EventTrigger.Entry { eventID = EventTriggerType.PointerExit };
                    exit.callback.AddListener((_) => HandleChestSlotPointerExit());
                    trigger.triggers.Add(exit);
                }
            }

            // Bottom Bar: [QUICK DEPOSIT] & [LOOT ALL]
            BuildButtonsBar();
        }

        private void BuildButtonsBar()
        {
            var barObj = new GameObject("ButtonBar");
            barObj.transform.SetParent(_panelRoot.transform, false);
            var brt = barObj.AddComponent<RectTransform>();
            brt.anchorMin = new Vector2(0f, 0f);
            brt.anchorMax = new Vector2(1f, 0f);
            brt.pivot = new Vector2(0.5f, 0f);
            brt.anchoredPosition = new Vector2(0f, 10f);
            brt.sizeDelta = new Vector2(-24f, 32f);

            CreateButton(barObj, "BtnQuickDeposit", "QUICK DEPOSIT", new Vector2(60, 0), new Vector2(120, 26), () =>
            {
                ExecuteQuickDeposit();
            });

            CreateButton(barObj, "BtnLootAll", "LOOT ALL", new Vector2(190, 0), new Vector2(90, 26), () =>
            {
                ExecuteLootAll();
            });

            CreateButton(barObj, "BtnClose", "CLOSE", new Vector2(420, 0), new Vector2(60, 26), () =>
            {
                CloseChest();
            });
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
            img.color = new Color(0.25f, 0.22f, 0.18f, 1f);

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

        public void OpenChest(StorageChest chest)
        {
            targetChest = chest;
            if (targetChest != null)
            {
                targetChest.OnChestChanged += RefreshAllSlots;
                if (_titleText != null) _titleText.text = $"<color=#E69138><b>{targetChest.ChestName.ToUpper()}</b></color> <color=#A0A0A0>(30 Slots)</color>";
            }

            SetOpen(true);

            // Also open player inventory for convenient transferring
            if (InventoryUI.Instance != null && !InventoryUI.Instance.IsOpen)
            {
                InventoryUI.Instance.SetOpen(true);
            }
        }

        public void CloseChest()
        {
            if (targetChest != null)
            {
                targetChest.OnChestChanged -= RefreshAllSlots;
                targetChest = null;
            }
            SetOpen(false);
        }

        public void SetOpen(bool open)
        {
            _isOpen = open;
            if (_panelRoot != null) _panelRoot.SetActive(_isOpen);

            if (_isOpen)
            {
                RefreshAllSlots();
            }
            else
            {
                if (KatabiTooltipUI.Instance != null) KatabiTooltipUI.Instance.Hide();
            }
        }

        public void RefreshAllSlots()
        {
            if (targetChest == null) return;
            for (int i = 0; i < StorageChest.TOTAL_CHEST_SLOTS; i++)
            {
                var item = targetChest.GetSlot(i);
                if (_slotIcons[i] != null)
                {
                    if (item != null && item.Icon != null)
                    {
                        _slotIcons[i].sprite = item.Icon;
                        _slotIcons[i].color = Color.white;
                    }
                    else
                    {
                        _slotIcons[i].sprite = null;
                        _slotIcons[i].color = new Color(1, 1, 1, 0);
                    }
                }

                if (_slotCounts[i] != null)
                {
                    if (item != null && item.Count > 1)
                    {
                        _slotCounts[i].text = item.Count.ToString();
                    }
                    else
                    {
                        _slotCounts[i].text = "";
                    }
                }
            }
        }

        private void Update()
        {
            if (_isOpen)
            {
                if (UnityEngine.Input.GetKeyDown(KeyCode.Escape))
                {
                    CloseChest();
                    return;
                }

                if (targetChest != null)
                {
                    var player = FindFirstObjectByType<Potaria.Player.PlayerController>();
                    if (player != null)
                    {
                        float dist = Vector2.Distance(player.transform.position, targetChest.transform.position);
                        if (dist > 8f)
                        {
                            CloseChest();
                        }
                    }
                }
            }
        }

        private void HandleChestSlotClick(int slotIndex, bool isRightClick = false, bool isShiftClick = false)
        {
            if (targetChest == null) return;
            if (playerInventory == null) playerInventory = FindFirstObjectByType<PlayerInventory>();
            if (playerInventory == null) return;

            var chestItem = targetChest.GetSlot(slotIndex);
            var held = playerInventory.HeldItem;

            if (isShiftClick)
            {
                // Quick-Transfer from chest directly into player inventory
                if (chestItem != null)
                {
                    bool added = playerInventory.AddItem(chestItem);
                    if (chestItem.Count <= 0)
                    {
                        targetChest.SetSlot(slotIndex, null);
                    }
                    else
                    {
                        targetChest.SetSlot(slotIndex, chestItem);
                    }
                }
                RefreshAllSlots();
                return;
            }

            if (isRightClick)
            {
                // Right-Click: Split half stack from chest to held item, or place 1 from held item into chest
                if (held == null && chestItem != null)
                {
                    int take = (chestItem.Count > 1) ? (chestItem.Count + 1) / 2 : 1;
                    playerInventory.HeldItem = chestItem.Clone(take);
                    chestItem.Count -= take;
                    targetChest.SetSlot(slotIndex, chestItem.Count > 0 ? chestItem : null);
                }
                else if (held != null)
                {
                    if (chestItem == null)
                    {
                        var one = held.Clone(1);
                        targetChest.SetSlot(slotIndex, one);
                        held.Count -= 1;
                        if (held.Count <= 0) playerInventory.HeldItem = null;
                    }
                    else if (chestItem.CanStackWith(held) && chestItem.Count < chestItem.MaxStack)
                    {
                        chestItem.Count += 1;
                        held.Count -= 1;
                        if (held.Count <= 0) playerInventory.HeldItem = null;
                        targetChest.SetSlot(slotIndex, chestItem);
                    }
                }
                RefreshAllSlots();
                return;
            }

            if (held == null)
            {
                if (chestItem != null)
                {
                    playerInventory.HeldItem = chestItem;
                    targetChest.SetSlot(slotIndex, null);
                }
            }
            else
            {
                if (chestItem == null)
                {
                    targetChest.SetSlot(slotIndex, held);
                    playerInventory.HeldItem = null;
                }
                else if (chestItem.CanStackWith(held))
                {
                    int space = chestItem.MaxStack - chestItem.Count;
                    if (space > 0)
                    {
                        int take = Mathf.Min(space, held.Count);
                        chestItem.Count += take;
                        held.Count -= take;
                        if (held.Count <= 0) playerInventory.HeldItem = null;
                        targetChest.SetSlot(slotIndex, chestItem);
                    }
                    else
                    {
                        playerInventory.HeldItem = chestItem;
                        targetChest.SetSlot(slotIndex, held);
                    }
                }
                else
                {
                    playerInventory.HeldItem = chestItem;
                    targetChest.SetSlot(slotIndex, held);
                }
            }

            RefreshAllSlots();
        }

        private void HandleChestSlotPointerEnter(int slotIndex)
        {
            if (targetChest == null) return;
            var item = targetChest.GetSlot(slotIndex);
            if (item != null && KatabiTooltipUI.Instance != null)
            {
                KatabiTooltipUI.Instance.Show(item, null, UnityEngine.Input.mousePosition);
            }
        }

        private void HandleChestSlotPointerExit()
        {
            if (KatabiTooltipUI.Instance != null)
            {
                KatabiTooltipUI.Instance.Hide();
            }
        }

        public void ExecuteQuickDeposit()
        {
            if (targetChest == null) return;
            if (playerInventory == null) playerInventory = FindFirstObjectByType<PlayerInventory>();
            targetChest.QuickDeposit(playerInventory);
            RefreshAllSlots();
            if (playerInventory != null) playerInventory.Organize(true);
        }

        public void ExecuteLootAll()
        {
            if (targetChest == null) return;
            if (playerInventory == null) playerInventory = FindFirstObjectByType<PlayerInventory>();
            targetChest.LootAll(playerInventory);
            RefreshAllSlots();
        }
    }
}
