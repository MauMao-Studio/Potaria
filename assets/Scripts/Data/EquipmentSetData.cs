using System;
using System.Collections.Generic;
using UnityEngine;

namespace Potaria.Data
{
    /// <summary>
    /// Progressive tier thresholds for equipment set bonuses (e.g. 2-piece, 3-piece, 4-piece, 5-piece).
    /// </summary>
    [Serializable]
    public class SetBonusThreshold
    {
        [Range(2, 6)]
        [SerializeField] private int requiredPieces = 2;
        [SerializeField] private string title = "2-Piece Bonus";
        [TextArea(2, 3)]
        [SerializeField] private string description = string.Empty;

        [Header("Stat Multipliers")]
        [SerializeField] private float atkMultiplier = 0.0f;
        [SerializeField] private float defMultiplier = 0.0f;
        [SerializeField] private float bonusSpeed = 0.0f;
        [SerializeField] private float bonusCritChance = 0.0f;

        [Header("Flat Stat Bonuses")]
        [SerializeField] private int bonusMaxHp = 0;
        [SerializeField] private float bonusMpRegen = 0.0f;
        [SerializeField] private float bonusAtkSpeed = 0.0f;

        [Header("Special FX & Passive")]
        [SerializeField] private string auraEffect = string.Empty;
        [TextArea(1, 3)]
        [SerializeField] private string specialPassive = string.Empty;

        // Accessors
        public int RequiredPieces { get => requiredPieces; set => requiredPieces = value; }
        public string Title { get => title; set => title = value; }
        public string Description { get => description; set => description = value; }
        public float AtkMultiplier { get => atkMultiplier; set => atkMultiplier = value; }
        public float DefMultiplier { get => defMultiplier; set => defMultiplier = value; }
        public float BonusSpeed { get => bonusSpeed; set => bonusSpeed = value; }
        public float BonusCritChance { get => bonusCritChance; set => bonusCritChance = value; }
        public int BonusMaxHp { get => bonusMaxHp; set => bonusMaxHp = value; }
        public float BonusMpRegen { get => bonusMpRegen; set => bonusMpRegen = value; }
        public float BonusAtkSpeed { get => bonusAtkSpeed; set => bonusAtkSpeed = value; }
        public string AuraEffect { get => auraEffect; set => auraEffect = value; }
        public string SpecialPassive { get => specialPassive; set => specialPassive = value; }
    }

    /// <summary>
    /// ScriptableObject defining progressive equipment set bonuses in Potaria.
    /// Explicitly supports Seven Deadly Sins (SDS), Seven Heavenly Virtues (SHV), and Katipunero sets
    /// with 2-piece, 4-piece, and 5-piece set bonus passives and aura effects.
    /// </summary>
    [CreateAssetMenu(fileName = "NewEquipmentSetData", menuName = "Potaria/Equipment/Equipment Set Data", order = 40)]
    public class EquipmentSetData : ScriptableObject
    {
        [Header("Set Identification")]
        [SerializeField] private string setId = string.Empty;
        [SerializeField] private string setName = "Set Name";
        [Tooltip("SDS, SHV, Katipunero, or other group tag.")]
        [SerializeField] private string setTag = string.Empty;

        [TextArea(2, 4)]
        [SerializeField] private string description = string.Empty;

        [Header("Set Pieces")]
        [SerializeField] private List<string> pieceItemIds = new List<string>();
        [SerializeField] private List<ItemData> pieceItems = new List<ItemData>();

        [Header("Standard Thresholds (Quick Access)")]
        [SerializeField] private SetBonusThreshold twoPieceBonus;
        [SerializeField] private SetBonusThreshold fourPieceBonus;
        [SerializeField] private SetBonusThreshold fivePieceBonus;

        [Header("All Progressive Thresholds")]
        [SerializeField] private List<SetBonusThreshold> allThresholds = new List<SetBonusThreshold>();

        // Public Accessors
        public string SetId { get => setId; set => setId = value; }
        public string SetName { get => setName; set => setName = value; }
        public string SetTag { get => setTag; set => setTag = value; }
        public string Description { get => description; set => description = value; }
        public List<string> PieceItemIds => pieceItemIds;
        public List<ItemData> PieceItems => pieceItems;
        public SetBonusThreshold TwoPieceBonus { get => twoPieceBonus; set => twoPieceBonus = value; }
        public SetBonusThreshold FourPieceBonus { get => fourPieceBonus; set => fourPieceBonus = value; }
        public SetBonusThreshold FivePieceBonus { get => fivePieceBonus; set => fivePieceBonus = value; }
        public List<SetBonusThreshold> AllThresholds => allThresholds;

        /// <summary>
        /// Checks if an item ID belongs to this equipment set.
        /// </summary>
        public bool ContainsItem(string itemId)
        {
            if (string.IsNullOrEmpty(itemId)) return false;
            return pieceItemIds.Contains(itemId);
        }

        /// <summary>
        /// Returns all active set bonus thresholds unlocked at the given equipped piece count.
        /// </summary>
        public List<SetBonusThreshold> GetActiveThresholds(int equippedPieceCount)
        {
            var active = new List<SetBonusThreshold>();
            foreach (var t in allThresholds)
            {
                if (equippedPieceCount >= t.RequiredPieces)
                {
                    active.Add(t);
                }
            }
            return active;
        }

        /// <summary>
        /// Formats full set tooltip including active state based on equipped piece count.
        /// </summary>
        public string GetFormattedSetTooltip(int equippedCount = 0)
        {
            var header = $"<color=#FFD700><b>Set: {setName} ({equippedCount}/{pieceItemIds.Count})</b></color>";
            var lines = new List<string> { header };
            if (!string.IsNullOrEmpty(description))
            {
                lines.Add($"<i>{description}</i>");
            }

            foreach (var t in allThresholds)
            {
                var isUnlocked = equippedCount >= t.RequiredPieces;
                var colorHex = isUnlocked ? "#4CD964" : "#808080";
                lines.Add($"<color={colorHex}>({t.RequiredPieces}) {t.Description}</color>");
            }

            return string.Join("\n", lines);
        }
    }
}
