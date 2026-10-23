using System;
using System.Collections.Generic;
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
    /// 10-Slot Paperdoll Equipment & Character Panel UI.
    /// - Toggled with 'C' key
    /// - 10 Paperdoll Slots: Head, Chest, Legs, Weapon, and 6 Accessories
    /// - Real-time RPG Statistics readout (HP, MP, ATK, DEF, Damage Reduction, Movement Speed, Crit Rate, Crit Damage)
    /// - 27 Equipment Sets active milestone passives (2-piece, 4-piece, 5-piece)
    /// - TextMeshProUGUI typography, responsive at 1920x1080 resolution
    /// </summary>
    public class CharacterPanelUI : MonoBehaviour
    {
        private static CharacterPanelUI s_instance;
        public static CharacterPanelUI Instance => s_instance;

        [Header("Target References")]
        [SerializeField] private PlayerEquipment equipment;
        [SerializeField] private PlayerStats stats;
        [SerializeField] private PlayerInventory inventory;
        [SerializeField] private PotariaInput input;

        [Header("Assets & Sprites")]
        [SerializeField] private TMP_FontAsset tmpFont;
        [SerializeField] private Sprite slotFrameSprite;

        // UI Roots
        private GameObject _panelRoot;

        // 10 Paperdoll Slots
        private readonly Image[] _paperdollFrames = new Image[PlayerEquipment.TOTAL_EQUIP_SLOTS];
        private readonly Image[] _paperdollIcons = new Image[PlayerEquipment.TOTAL_EQUIP_SLOTS];
        private readonly TextMeshProUGUI[] _paperdollLabels = new TextMeshProUGUI[PlayerEquipment.TOTAL_EQUIP_SLOTS];

        // Stats Readouts
        private TextMeshProUGUI _levelAndExpText;
        private Image _expBarFill;
        private TextMeshProUGUI _hpText;
        private TextMeshProUGUI _mpText;
        private TextMeshProUGUI _atkText;
        private TextMeshProUGUI _defText;
        private TextMeshProUGUI _dmgRedText;
        private TextMeshProUGUI _speedText;
        private TextMeshProUGUI _critText;
        private TextMeshProUGUI _critDmgText;

        // Set Bonuses Text
        private TextMeshProUGUI _setBonusesText;

        private bool _isOpen = false;
        public bool IsOpen => _isOpen;

        private static readonly string[] s_slotNames = new[]
        {
            "HEAD", "CHEST", "LEGS", "WEAPON",
            "ACC 1", "ACC 2", "ACC 3", "ACC 4", "ACC 5", "ACC 6"
        };

        private void Awake()
        {
            s_instance = this;
            if (equipment == null) equipment = FindFirstObjectByType<PlayerEquipment>();
            if (stats == null) stats = FindFirstObjectByType<PlayerStats>();
            if (inventory == null) inventory = FindFirstObjectByType<PlayerInventory>();
            if (input == null) input = PotariaInput.Instance;

            LoadResourcesIfMissing();
            BuildUIHierarchy();
            SetOpen(false);
        }

        private void OnEnable()
        {
            if (equipment != null) equipment.OnEquipmentChanged += RefreshPanel;
            if (stats != null)
            {
                stats.OnLevelUp += (_) => RefreshPanel();
                stats.OnExpChanged += (_, __) => RefreshPanel();
                stats.OnHpChanged += (_, __) => RefreshPanel();
                stats.OnMpChanged += (_, __) => RefreshPanel();
            }
        }

        private void OnDisable()
        {
            if (equipment != null) equipment.OnEquipmentChanged -= RefreshPanel;
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
            var oldPanel = transform.Find("CharacterPanel");
            if (oldPanel != null) DestroyImmediate(oldPanel.gameObject);

            _panelRoot = new GameObject("CharacterPanel");
            _panelRoot.transform.SetParent(transform, false);

            var prt = _panelRoot.AddComponent<RectTransform>();
            prt.anchorMin = new Vector2(0.5f, 0.5f);
            prt.anchorMax = new Vector2(0.5f, 0.5f);
            prt.pivot = new Vector2(0.5f, 0.5f);
            prt.sizeDelta = new Vector2(500f, 440f);
            prt.anchoredPosition = new Vector2(550f, -40f);

            var bg = _panelRoot.AddComponent<Image>();
            bg.color = new Color(0.07f, 0.08f, 0.11f, 0.95f);

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
            titleText.text = "<color=#FFD700><b>CHARACTER & PAPERDOLL</b></color> <color=#A0A0A0>(10 Slots)</color>";

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

            // Left Section: 10 Paperdoll Slots
            BuildPaperdollGrid();

            // Right Section: RPG Stats Readout & Set Bonuses
            BuildStatsAndSetBonusPanel();
        }

        private void BuildPaperdollGrid()
        {
            var gridObj = new GameObject("PaperdollGrid");
            gridObj.transform.SetParent(_panelRoot.transform, false);
            var grt = gridObj.AddComponent<RectTransform>();
            grt.anchorMin = new Vector2(0f, 0f);
            grt.anchorMax = new Vector2(0.48f, 1f);
            grt.offsetMin = new Vector2(14f, 14f);
            grt.offsetMax = new Vector2(0f, -38f);

            // 10 Slots arranged nicely:
            // Column 1: Head, Chest, Legs, Weapon (Main Gear)
            // Column 2 & 3: Accessory 1..6
            Vector2[] slotPositions = new Vector2[]
            {
                new Vector2(30f, -30f),   // Head
                new Vector2(30f, -80f),   // Chest
                new Vector2(30f, -130f),  // Legs
                new Vector2(30f, -180f),  // Weapon
                new Vector2(100f, -30f),  // Acc 1
                new Vector2(160f, -30f),  // Acc 2
                new Vector2(100f, -80f),  // Acc 3
                new Vector2(160f, -80f),  // Acc 4
                new Vector2(100f, -130f), // Acc 5
                new Vector2(160f, -130f)  // Acc 6
            };

            for (int i = 0; i < PlayerEquipment.TOTAL_EQUIP_SLOTS; i++)
            {
                int slotIndex = i;
                var slotObj = new GameObject($"EquipSlot_{i}");
                slotObj.transform.SetParent(gridObj.transform, false);
                var srt = slotObj.AddComponent<RectTransform>();
                srt.anchorMin = new Vector2(0f, 1f);
                srt.anchorMax = new Vector2(0f, 1f);
                srt.pivot = new Vector2(0.5f, 0.5f);
                srt.anchoredPosition = slotPositions[i];
                srt.sizeDelta = new Vector2(44f, 44f);

                var frameImg = slotObj.AddComponent<Image>();
                if (slotFrameSprite != null) frameImg.sprite = slotFrameSprite;
                frameImg.color = (i < 4) ? new Color(1f, 0.85f, 0.5f, 1f) : new Color(0.7f, 0.85f, 1f, 1f);
                _paperdollFrames[i] = frameImg;

                // Slot Label under or inside slot
                var lblObj = new GameObject("Label");
                lblObj.transform.SetParent(slotObj.transform, false);
                var lrt = lblObj.AddComponent<RectTransform>();
                lrt.anchorMin = new Vector2(0f, 0f);
                lrt.anchorMax = new Vector2(1f, 0f);
                lrt.pivot = new Vector2(0.5f, 1f);
                lrt.anchoredPosition = new Vector2(0f, -2f);
                lrt.sizeDelta = new Vector2(50f, 12f);
                var lblText = lblObj.AddComponent<TextMeshProUGUI>();
                if (tmpFont != null) lblText.font = tmpFont;
                lblText.fontSize = 8;
                lblText.fontStyle = FontStyles.Bold;
                lblText.alignment = TextAlignmentOptions.Center;
                lblText.text = s_slotNames[i];
                lblText.color = new Color(0.75f, 0.75f, 0.8f, 0.85f);
                _paperdollLabels[i] = lblText;

                // Icon child
                var iconObj = new GameObject("Icon");
                iconObj.transform.SetParent(slotObj.transform, false);
                var irt = iconObj.AddComponent<RectTransform>();
                irt.anchorMin = Vector2.zero;
                irt.anchorMax = Vector2.one;
                irt.offsetMin = new Vector2(4, 4);
                irt.offsetMax = new Vector2(-4, -4);
                var iconImg = iconObj.AddComponent<Image>();
                iconImg.color = new Color(1, 1, 1, 0); // invisible until equipped
                iconImg.raycastTarget = false;
                _paperdollIcons[i] = iconImg;

                // Event Trigger (Click to unequip, Hover for tooltip)
                var trigger = slotObj.AddComponent<EventTrigger>();
                var click = new EventTrigger.Entry { eventID = EventTriggerType.PointerClick };
                click.callback.AddListener((_) => HandlePaperdollClick(slotIndex));
                trigger.triggers.Add(click);

                var enter = new EventTrigger.Entry { eventID = EventTriggerType.PointerEnter };
                enter.callback.AddListener((_) => HandlePaperdollPointerEnter(slotIndex));
                trigger.triggers.Add(enter);

                var exit = new EventTrigger.Entry { eventID = EventTriggerType.PointerExit };
                exit.callback.AddListener((_) => HandlePaperdollPointerExit());
                trigger.triggers.Add(exit);
            }
        }

        private void BuildStatsAndSetBonusPanel()
        {
            var statsObj = new GameObject("StatsPanel");
            statsObj.transform.SetParent(_panelRoot.transform, false);
            var srt = statsObj.AddComponent<RectTransform>();
            srt.anchorMin = new Vector2(0.50f, 0f);
            srt.anchorMax = new Vector2(1f, 1f);
            srt.offsetMin = new Vector2(8f, 14f);
            srt.offsetMax = new Vector2(-14f, -38f);

            var layout = statsObj.AddComponent<VerticalLayoutGroup>();
            layout.childControlWidth = true;
            layout.childControlHeight = false;
            layout.childForceExpandWidth = true;
            layout.childForceExpandHeight = false;
            layout.spacing = 3f;

            // Level & EXP
            _levelAndExpText = CreateStatRow(statsObj, "LevelAndExp", "Lv.1 | EXP: 0 / 100");

            // HP & MP
            _hpText = CreateStatRow(statsObj, "HP", "HP: 100 / 100");
            _mpText = CreateStatRow(statsObj, "MP", "MP: 50 / 50");

            // Combat Stats
            _atkText = CreateStatRow(statsObj, "ATK", "ATK: 10");
            _defText = CreateStatRow(statsObj, "DEF", "DEF: 2");
            _dmgRedText = CreateStatRow(statsObj, "DamageReduction", "DMG Reduction: 0.0%");
            _speedText = CreateStatRow(statsObj, "Speed", "Move Speed: 3.00");
            _critText = CreateStatRow(statsObj, "CritRate", "Crit Chance: 5.0%");
            _critDmgText = CreateStatRow(statsObj, "CritDamage", "Crit Multiplier: 180%");

            // Divider
            var div = new GameObject("Divider");
            div.transform.SetParent(statsObj.transform, false);
            var divRt = div.AddComponent<RectTransform>();
            divRt.sizeDelta = new Vector2(220f, 2f);
            var divImg = div.AddComponent<Image>();
            divImg.color = new Color(0.3f, 0.35f, 0.45f, 0.7f);

            // Set Bonuses Header & Body
            var setHdr = CreateStatRow(statsObj, "SetHeader", "<color=#FFD700><b>ACTIVE SET BONUSES</b></color>");
            setHdr.fontSize = 12;

            _setBonusesText = CreateStatRow(statsObj, "SetBonuses", "<i>None active</i>");
            _setBonusesText.fontSize = 11;
        }

        private TextMeshProUGUI CreateStatRow(GameObject parent, string name, string initialText)
        {
            var row = new GameObject(name);
            row.transform.SetParent(parent.transform, false);
            var rt = row.AddComponent<RectTransform>();
            rt.sizeDelta = new Vector2(220f, 18f);

            var tmp = row.AddComponent<TextMeshProUGUI>();
            if (tmpFont != null) tmp.font = tmpFont;
            tmp.fontSize = 12;
            tmp.text = initialText;
            tmp.textWrappingMode = TextWrappingModes.Normal;
            return tmp;
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
                RefreshPanel();
            }
            else
            {
                if (KatabiTooltipUI.Instance != null) KatabiTooltipUI.Instance.Hide();
            }
        }

        private void Update()
        {
            // Toggle key C
            if (input == null) input = PotariaInput.Instance;
            if (input != null && input.CharacterPanelPressed)
            {
                Toggle();
            }
        }

        public void RefreshPanel()
        {
            if (equipment == null) equipment = FindFirstObjectByType<PlayerEquipment>();
            if (stats == null) stats = FindFirstObjectByType<PlayerStats>();

            // 1. Update Paperdoll Slots
            for (int i = 0; i < PlayerEquipment.TOTAL_EQUIP_SLOTS; i++)
            {
                var piece = (equipment != null) ? equipment.GetEquipped(i) : null;
                if (_paperdollIcons[i] != null)
                {
                    if (piece != null && piece.Icon != null)
                    {
                        _paperdollIcons[i].sprite = piece.Icon;
                        _paperdollIcons[i].color = piece.IsBroken ? new Color(1f, 0.4f, 0.4f, 1f) : Color.white;
                    }
                    else
                    {
                        _paperdollIcons[i].sprite = null;
                        _paperdollIcons[i].color = new Color(1, 1, 1, 0);
                    }
                }
            }

            // 2. Update Stats
            if (stats != null)
            {
                if (_levelAndExpText != null)
                    _levelAndExpText.text = $"<b>Lv.{stats.Level}</b> | EXP: {stats.CurrentExp} / {stats.ExpToNext}";

                if (_hpText != null)
                    _hpText.text = $"<color=#4CD964>HP: {stats.CurrentHp} / {stats.MaxHp}</color>";

                if (_mpText != null)
                    _mpText.text = $"<color=#00D9FF>MP: {stats.CurrentMp} / {stats.MaxMp}</color>";

                if (_atkText != null)
                    _atkText.text = $"<color=#FF5959>ATK: {stats.TotalAtk}</color>";

                if (_defText != null)
                    _defText.text = $"<color=#59A6FF>DEF: {stats.TotalDef}</color>";

                if (_dmgRedText != null)
                    _dmgRedText.text = $"<color=#99E6FF>DMG Red: {stats.TotalDamageReduction * 100f:0.#}%</color>";

                if (_speedText != null)
                    _speedText.text = $"<color=#59F273>Speed: {stats.TotalMoveSpeed:0.##}</color>";

                if (_critText != null)
                    _critText.text = $"<color=#FFD700>Crit: {stats.TotalCritRate:0.#}%</color>";

                if (_critDmgText != null)
                    _critDmgText.text = $"<color=#FFB233>Crit Dmg: {stats.TotalCritMultiplier * 100f:0.#}%</color>";
            }

            // 3. Update Equipment Set Bonuses
            if (_setBonusesText != null)
            {
                if (equipment != null && equipment.ActiveSetBonuses.Count > 0)
                {
                    var lines = new List<string>();
                    foreach (var activeSet in equipment.ActiveSetBonuses)
                    {
                        var set = activeSet.SetData;
                        lines.Add($"<color=#FFD700><b>{set.SetName} ({activeSet.EquippedCount} pcs)</b></color>");
                        foreach (var t in activeSet.UnlockedThresholds)
                        {
                            lines.Add($"<color=#4CD964>• {t.Description}</color>");
                        }
                    }
                    _setBonusesText.text = string.Join("\n", lines);
                }
                else
                {
                    _setBonusesText.text = "<i>None active</i>";
                }
            }
        }

        private void HandlePaperdollClick(int slotIndex)
        {
            if (equipment == null) return;
            var equippedItem = equipment.GetEquipped(slotIndex);

            // If player is holding an item from inventory, try to equip it
            if (inventory != null && inventory.HeldItem != null)
            {
                if (equipment.CanEquipInSlot(inventory.HeldItem, slotIndex))
                {
                    var held = inventory.HeldItem;
                    if (held.Count > 1)
                    {
                        var one = held.Clone(1);
                        if (equipment.EquipItem(one, slotIndex, inventory))
                        {
                            held.Count -= 1;
                        }
                    }
                    else
                    {
                        inventory.HeldItem = null;
                        if (!equipment.EquipItem(held, slotIndex, inventory))
                        {
                            inventory.HeldItem = held;
                        }
                    }
                    RefreshPanel();
                    return;
                }
            }

            // Otherwise unequip item back to inventory
            if (equippedItem != null)
            {
                equipment.UnequipItem(slotIndex, inventory);
                RefreshPanel();
            }
        }

        private void HandlePaperdollPointerEnter(int slotIndex)
        {
            if (equipment == null) return;
            var item = equipment.GetEquipped(slotIndex);
            if (item != null && KatabiTooltipUI.Instance != null)
            {
                KatabiTooltipUI.Instance.Show(item, null, UnityEngine.Input.mousePosition);
            }
        }

        private void HandlePaperdollPointerExit()
        {
            if (KatabiTooltipUI.Instance != null)
            {
                KatabiTooltipUI.Instance.Hide();
            }
        }
    }
}
