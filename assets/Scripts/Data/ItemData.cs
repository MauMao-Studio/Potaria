using UnityEngine;

namespace Potaria.Data
{
    /// <summary>
    /// Base ScriptableObject representing any item in Potaria.
    /// Used for weapons, equipment, materials, crops, blocks, and consumables.
    /// </summary>
    [CreateAssetMenu(fileName = "NewItemData", menuName = "Potaria/Items/Item Data", order = 10)]
    public class ItemData : ScriptableObject
    {
        [Header("Item Identification")]
        [SerializeField] private string itemId = string.Empty;
        [SerializeField] private string itemName = "New Item";
        [SerializeField] private ItemCategory category = ItemCategory.Material;
        [SerializeField] private ItemRarity rarity = ItemRarity.Common;

        [Header("Inventory Parameters")]
        [SerializeField] private int maxStack = 99;
        [SerializeField] private int goldValue = 1;
        [SerializeField] private Sprite icon;

        [Header("Descriptions & Lore")]
        [TextArea(2, 4)]
        [SerializeField] private string description = string.Empty;

        [TextArea(2, 4)]
        [SerializeField] private string lore = string.Empty;

        [SerializeField] private string specialEffect = string.Empty;

        // Public Accessors
        public string ItemId { get => itemId; set => itemId = value; }
        public string ItemName { get => itemName; set => itemName = value; }
        public ItemCategory Category { get => category; set => category = value; }
        public ItemRarity Rarity { get => rarity; set => rarity = value; }
        public int MaxStack { get => maxStack; set => maxStack = value; }
        public int GoldValue { get => goldValue; set => goldValue = value; }
        public Sprite Icon { get => icon; set => icon = value; }
        public string Description { get => description; set => description = value; }
        public string Lore { get => lore; set => lore = value; }
        public string SpecialEffect { get => specialEffect; set => specialEffect = value; }

        public Color GetRarityColor() => rarity.GetColor();
        public string GetRarityHex() => rarity.GetHexColor();

        public virtual string GetFormattedTooltip()
        {
            var title = $"<color={GetRarityHex()}><b>{itemName}</b></color>";
            var cat = $"<color=#A0A0A0>{category} - {rarity}</color>";
            var desc = string.IsNullOrEmpty(description) ? "" : $"\n{description}";
            var special = string.IsNullOrEmpty(specialEffect) ? "" : $"\n<color=#FFD700>{specialEffect}</color>";
            var loreText = string.IsNullOrEmpty(lore) ? "" : $"\n<i><color=#888888>\"{lore}\"</color></i>";
            return $"{title}\n{cat}{desc}{special}{loreText}";
        }
    }
}
