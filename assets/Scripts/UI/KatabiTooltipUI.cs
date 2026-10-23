using System;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.UI;
using TMPro;
using Potaria.Data;
using Potaria.RPG;

namespace Potaria.UI
{
    /// <summary>
    /// Side-by-Side 'Katabi' Comparison Tooltip UI.
    /// When hovering an equippable candidate item while the Character Panel is open ('C'),
    /// renders the candidate item tooltip alongside the currently equipped item card labeled
    /// '[ CURRENTLY EQUIPPED ]' for immediate stat comparison without screen clipping.
    /// Features circular affix socket indicators (●) / (○), rarity color borders, and TMP typography.
    /// </summary>
    public class KatabiTooltipUI : MonoBehaviour
    {
        private static KatabiTooltipUI s_instance;
        public static KatabiTooltipUI Instance => s_instance;

        [Header("Card Roots")]
        [SerializeField] private RectTransform containerRect;
        [SerializeField] private GameObject candidateCardObj;
        [SerializeField] private GameObject equippedCardObj;

        [Header("Candidate Card Components")]
        [SerializeField] private Image candidateBorder;
        [SerializeField] private TextMeshProUGUI candidateHeader;
        [SerializeField] private TextMeshProUGUI candidateStatsText;
        [SerializeField] private TextMeshProUGUI candidateAffixText;
        [SerializeField] private TextMeshProUGUI candidateLoreText;

        [Header("Equipped Card Components")]
        [SerializeField] private Image equippedBorder;
        [SerializeField] private TextMeshProUGUI equippedHeader;
        [SerializeField] private TextMeshProUGUI equippedBadge;
        [SerializeField] private TextMeshProUGUI equippedStatsText;
        [SerializeField] private TextMeshProUGUI equippedAffixText;
        [SerializeField] private TextMeshProUGUI equippedLoreText;

        [Header("Font")]
        [SerializeField] private TMP_FontAsset fontAsset;

        private Canvas _rootCanvas;
        private RectTransform _canvasRect;

        private void Awake()
        {
            s_instance = this;
            if (containerRect == null) containerRect = GetComponent<RectTransform>();
            _rootCanvas = GetComponentInParent<Canvas>();
            if (_rootCanvas != null) _canvasRect = _rootCanvas.GetComponent<RectTransform>();

            BuildCardHierarchyIfMissing();
            Hide();
        }

        public void BuildCardHierarchyIfMissing()
        {
            if (candidateCardObj != null && equippedCardObj != null) return;

            // Ensure container rect
            if (containerRect == null) containerRect = GetComponent<RectTransform>();
            if (containerRect == null) containerRect = gameObject.AddComponent<RectTransform>();

            containerRect.anchorMin = Vector2.zero;
            containerRect.anchorMax = Vector2.zero;
            containerRect.pivot = new Vector2(0f, 1f);

            // 1. Build Candidate Card
            if (candidateCardObj == null)
            {
                candidateCardObj = CreateCardObject("CandidateCard", new Vector2(0, 0), out candidateBorder, out candidateHeader, out candidateStatsText, out candidateAffixText, out candidateLoreText);
            }

            // 2. Build Equipped Card
            if (equippedCardObj == null)
            {
                equippedCardObj = CreateCardObject("EquippedCard", new Vector2(310, 0), out equippedBorder, out equippedHeader, out equippedStatsText, out equippedAffixText, out equippedLoreText);
                
                // Add equipped badge to equipped card
                var badgeObj = new GameObject("EquippedBadge");
                badgeObj.transform.SetParent(equippedCardObj.transform, false);
                var brt = badgeObj.AddComponent<RectTransform>();
                brt.anchorMin = new Vector2(0f, 1f);
                brt.anchorMax = new Vector2(1f, 1f);
                brt.pivot = new Vector2(0.5f, 1f);
                brt.anchoredPosition = new Vector2(0, -6);
                brt.sizeDelta = new Vector2(-16, 20);

                equippedBadge = badgeObj.AddComponent<TextMeshProUGUI>();
                if (fontAsset != null) equippedBadge.font = fontAsset;
                equippedBadge.fontSize = 12;
                equippedBadge.fontStyle = FontStyles.Bold;
                equippedBadge.alignment = TextAlignmentOptions.Center;
                equippedBadge.text = "<color=#FFD700>[ CURRENTLY EQUIPPED ]</color>";
            }
        }

        private GameObject CreateCardObject(string name, Vector2 localPos, out Image border, out TextMeshProUGUI header, out TextMeshProUGUI stats, out TextMeshProUGUI affixes, out TextMeshProUGUI lore)
        {
            var card = new GameObject(name);
            card.transform.SetParent(transform, false);

            var rt = card.AddComponent<RectTransform>();
            rt.anchorMin = Vector2.zero;
            rt.anchorMax = Vector2.zero;
            rt.pivot = new Vector2(0f, 1f);
            rt.anchoredPosition = localPos;
            rt.sizeDelta = new Vector2(300f, 380f);

            var bg = card.AddComponent<Image>();
            bg.color = new Color(0.08f, 0.09f, 0.12f, 0.96f);

            // Border outline
            var borderObj = new GameObject("Border");
            borderObj.transform.SetParent(card.transform, false);
            var brt = borderObj.AddComponent<RectTransform>();
            brt.anchorMin = Vector2.zero;
            brt.anchorMax = Vector2.one;
            brt.sizeDelta = Vector2.zero;
            border = borderObj.AddComponent<Image>();
            border.color = new Color(0.4f, 0.4f, 0.45f, 1f);
            border.raycastTarget = false;

            // Content container
            var contentObj = new GameObject("Content");
            contentObj.transform.SetParent(card.transform, false);
            var crt = contentObj.AddComponent<RectTransform>();
            crt.anchorMin = Vector2.zero;
            crt.anchorMax = Vector2.one;
            crt.offsetMin = new Vector2(12, 12);
            crt.offsetMax = new Vector2(-12, -12);

            var layout = contentObj.AddComponent<VerticalLayoutGroup>();
            layout.childControlWidth = true;
            layout.childControlHeight = false;
            layout.childForceExpandWidth = true;
            layout.childForceExpandHeight = false;
            layout.spacing = 6f;

            // Header text
            header = CreateTextComponent(contentObj, "Header", 15, FontStyles.Bold);
            // Stats text
            stats = CreateTextComponent(contentObj, "Stats", 13, FontStyles.Normal);
            // Affix text
            affixes = CreateTextComponent(contentObj, "Affixes", 12, FontStyles.Normal);
            // Lore text
            lore = CreateTextComponent(contentObj, "Lore", 11, FontStyles.Italic);

            return card;
        }

        private TextMeshProUGUI CreateTextComponent(GameObject parent, string name, float size, FontStyles style)
        {
            var obj = new GameObject(name);
            obj.transform.SetParent(parent.transform, false);
            var rt = obj.AddComponent<RectTransform>();
            rt.sizeDelta = new Vector2(276, 20);

            var tmp = obj.AddComponent<TextMeshProUGUI>();
            if (fontAsset != null) tmp.font = fontAsset;
            tmp.fontSize = size;
            tmp.fontStyle = style;
            tmp.textWrappingMode = TextWrappingModes.Normal;
            tmp.raycastTarget = false;
            return tmp;
        }

        public void Show(InventoryItemInstance candidate, InventoryItemInstance equipped, Vector2 screenPos)
        {
            if (candidate == null || candidate.ItemData == null)
            {
                Hide();
                return;
            }

            BuildCardHierarchyIfMissing();
            gameObject.SetActive(true);

            // Populate Candidate Card
            PopulateCandidateCard(candidate, equipped);
            candidateCardObj.SetActive(true);

            // Populate Equipped Card (if available)
            if (equipped != null && equipped.ItemData != null)
            {
                PopulateEquippedCard(equipped);
                equippedCardObj.SetActive(true);
            }
            else
            {
                equippedCardObj.SetActive(false);
            }

            PositionCards(screenPos, equipped != null && equipped.ItemData != null);
        }

        private void PopulateCandidateCard(InventoryItemInstance candidate, InventoryItemInstance equipped)
        {
            var data = candidate.ItemData;
            string hexColor = data.GetRarityHex();
            Color borderCol = data.GetRarityColor();

            if (candidateBorder != null) candidateBorder.color = borderCol;

            // Header
            string title = $"<color={hexColor}><b>{data.ItemName}</b></color>";
            if (candidate.EnhancementLevel > 0) title += $" <color=#00D9FF>+{candidate.EnhancementLevel}</color>";
            if (candidate.IsBroken) title += " <color=#FF4D4D>[BROKEN]</color>";
            string sub = $"<color=#A0A0A0>{data.Category} - {data.Rarity}</color>";

            if (candidateHeader != null) candidateHeader.text = $"{title}\n{sub}";

            // Stats with diff
            string statsStr = BuildStatsComparison(candidate, equipped);
            if (candidateStatsText != null) candidateStatsText.text = statsStr;

            // Affixes
            string affixStr = BuildAffixString(candidate);
            if (candidateAffixText != null) candidateAffixText.text = affixStr;

            // Lore / Description
            string desc = string.IsNullOrEmpty(data.Description) ? "" : data.Description;
            if (!string.IsNullOrEmpty(data.Lore)) desc += $"\n<i><color=#888888>\"{data.Lore}\"</color></i>";
            if (candidateLoreText != null) candidateLoreText.text = desc;
        }

        private void PopulateEquippedCard(InventoryItemInstance equipped)
        {
            var data = equipped.ItemData;
            string hexColor = data.GetRarityHex();
            Color borderCol = data.GetRarityColor();

            if (equippedBorder != null) equippedBorder.color = borderCol;

            // Header
            string title = $"<color={hexColor}><b>{data.ItemName}</b></color>";
            if (equipped.EnhancementLevel > 0) title += $" <color=#00D9FF>+{equipped.EnhancementLevel}</color>";
            if (equipped.IsBroken) title += " <color=#FF4D4D>[BROKEN]</color>";
            string sub = $"<color=#A0A0A0>{data.Category} - {data.Rarity}</color>";

            if (equippedHeader != null) equippedHeader.text = $"{title}\n{sub}";

            // Base Stats
            string statsStr = BuildSingleStats(equipped);
            if (equippedStatsText != null) equippedStatsText.text = statsStr;

            // Affixes
            string affixStr = BuildAffixString(equipped);
            if (equippedAffixText != null) equippedAffixText.text = affixStr;

            // Lore / Description
            string desc = string.IsNullOrEmpty(data.Description) ? "" : data.Description;
            if (equippedLoreText != null) equippedLoreText.text = desc;
        }

        private string BuildStatsComparison(InventoryItemInstance cand, InventoryItemInstance eq)
        {
            var lines = new List<string>();

            int candAtk = cand.GetEffectiveAttack();
            int eqAtk = eq != null ? eq.GetEffectiveAttack() : 0;
            if (candAtk > 0 || eqAtk > 0)
            {
                int diff = candAtk - eqAtk;
                string diffStr = (eq != null && diff != 0)
                    ? (diff > 0 ? $" <color=#4CD964>(+{diff})</color>" : $" <color=#FF4D4D>({diff})</color>")
                    : "";
                lines.Add($"<color=#FF5959>ATK: +{candAtk}</color>{diffStr}");
            }

            int candDef = cand.GetEffectiveDefense();
            int eqDef = eq != null ? eq.GetEffectiveDefense() : 0;
            if (candDef > 0 || eqDef > 0)
            {
                int diff = candDef - eqDef;
                string diffStr = (eq != null && diff != 0)
                    ? (diff > 0 ? $" <color=#4CD964>(+{diff})</color>" : $" <color=#FF4D4D>({diff})</color>")
                    : "";
                lines.Add($"<color=#59A6FF>DEF: +{candDef}</color>{diffStr}");
            }

            int candHp = cand.GetEffectiveBonusHp();
            int eqHp = eq != null ? eq.GetEffectiveBonusHp() : 0;
            if (candHp > 0 || eqHp > 0)
            {
                int diff = candHp - eqHp;
                string diffStr = (eq != null && diff != 0)
                    ? (diff > 0 ? $" <color=#4CD964>(+{diff})</color>" : $" <color=#FF4D4D>({diff})</color>")
                    : "";
                lines.Add($"<color=#4CD964>HP: +{candHp}</color>{diffStr}");
            }

            int candMp = cand.GetEffectiveBonusMp();
            int eqMp = eq != null ? eq.GetEffectiveBonusMp() : 0;
            if (candMp > 0 || eqMp > 0)
            {
                int diff = candMp - eqMp;
                string diffStr = (eq != null && diff != 0)
                    ? (diff > 0 ? $" <color=#4CD964>(+{diff})</color>" : $" <color=#FF4D4D>({diff})</color>")
                    : "";
                lines.Add($"<color=#00D9FF>MP: +{candMp}</color>{diffStr}");
            }

            float candCrit = cand.GetEffectiveCrit();
            float eqCrit = eq != null ? eq.GetEffectiveCrit() : 0f;
            if (candCrit > 0f || eqCrit > 0f)
            {
                float diff = candCrit - eqCrit;
                string diffStr = (eq != null && Mathf.Abs(diff) > 0.01f)
                    ? (diff > 0 ? $" <color=#4CD964>(+{diff:0.#}%)</color>" : $" <color=#FF4D4D>({diff:0.#}%)</color>")
                    : "";
                lines.Add($"<color=#FFD700>CRIT: +{candCrit:0.#}%</color>{diffStr}");
            }

            float candSpd = cand.GetEffectiveSpeed();
            float eqSpd = eq != null ? eq.GetEffectiveSpeed() : 0f;
            if (candSpd != 0f || eqSpd != 0f)
            {
                float diff = candSpd - eqSpd;
                string diffStr = (eq != null && Mathf.Abs(diff) > 0.01f)
                    ? (diff > 0 ? $" <color=#4CD964>(+{diff:0.##})</color>" : $" <color=#FF4D4D>({diff:0.##})</color>")
                    : "";
                lines.Add($"<color=#59F273>SPD: +{candSpd:0.##}</color>{diffStr}");
            }

            // Weapon Perks / Special Tag
            if (cand.ItemData is WeaponItemData wep && !string.IsNullOrEmpty(wep.SpecialTag))
            {
                lines.Add($"<color=#FFD700>Perk: {wep.SpecialTag}</color>");
            }

            return string.Join("\n", lines);
        }

        private string BuildSingleStats(InventoryItemInstance item)
        {
            var lines = new List<string>();
            int atk = item.GetEffectiveAttack();
            if (atk > 0) lines.Add($"<color=#FF5959>ATK: +{atk}</color>");

            int def = item.GetEffectiveDefense();
            if (def > 0) lines.Add($"<color=#59A6FF>DEF: +{def}</color>");

            int hp = item.GetEffectiveBonusHp();
            if (hp > 0) lines.Add($"<color=#4CD964>HP: +{hp}</color>");

            int mp = item.GetEffectiveBonusMp();
            if (mp > 0) lines.Add($"<color=#00D9FF>MP: +{mp}</color>");

            float crit = item.GetEffectiveCrit();
            if (crit > 0) lines.Add($"<color=#FFD700>CRIT: +{crit:0.#}%</color>");

            float spd = item.GetEffectiveSpeed();
            if (spd != 0) lines.Add($"<color=#59F273>SPD: +{spd:0.##}</color>");

            if (item.ItemData is WeaponItemData wep && !string.IsNullOrEmpty(wep.SpecialTag))
            {
                lines.Add($"<color=#FFD700>Perk: {wep.SpecialTag}</color>");
            }

            return string.Join("\n", lines);
        }

        private string BuildAffixString(InventoryItemInstance item)
        {
            if (item.AffixSlots <= 0 && (item.Affixes == null || item.Affixes.Count == 0))
            {
                return "";
            }

            var lines = new List<string>();
            int totalSlots = item.AffixSlots;
            int filled = (item.Affixes != null) ? item.Affixes.Count : 0;

            for (int i = 0; i < totalSlots; i++)
            {
                if (i < filled)
                {
                    string affixName = item.Affixes[i];
                    lines.Add($"<color=#FFD700>(●) {affixName}</color>");
                }
                else
                {
                    lines.Add($"<color=#888888>(○) Empty Affix Socket</color>");
                }
            }

            return string.Join("\n", lines);
        }

        private void PositionCards(Vector2 screenPos, bool hasEquipped)
        {
            if (_canvasRect == null && _rootCanvas != null) _canvasRect = _rootCanvas.GetComponent<RectTransform>();
            if (_canvasRect == null) return;

            float canvasW = _canvasRect.sizeDelta.x;
            float canvasH = _canvasRect.sizeDelta.y;

            // Screen space to Canvas local point
            RectTransformUtility.ScreenPointToLocalPointInRectangle(_canvasRect, screenPos, _rootCanvas.worldCamera, out var localPos);

            float cardW = 300f;
            float cardH = 380f;
            float spacing = 12f;
            float totalW = hasEquipped ? (cardW * 2 + spacing) : cardW;

            float posX = localPos.x + 16f;
            float posY = localPos.y - 16f;

            // Boundary clamping: horizontal
            if (posX + totalW > (canvasW * 0.5f))
            {
                posX = localPos.x - totalW - 16f;
            }

            // Boundary clamping: vertical
            if (posY - cardH < -(canvasH * 0.5f))
            {
                posY = -(canvasH * 0.5f) + cardH;
            }
            if (posY > (canvasH * 0.5f))
            {
                posY = canvasH * 0.5f;
            }

            // Set positions
            var candRt = candidateCardObj.GetComponent<RectTransform>();
            candRt.anchoredPosition = new Vector2(posX, posY);

            if (hasEquipped)
            {
                var eqRt = equippedCardObj.GetComponent<RectTransform>();
                eqRt.anchoredPosition = new Vector2(posX + cardW + spacing, posY);
            }
        }

        public void Hide()
        {
            if (candidateCardObj != null) candidateCardObj.SetActive(false);
            if (equippedCardObj != null) equippedCardObj.SetActive(false);
            gameObject.SetActive(false);
        }
    }
}
