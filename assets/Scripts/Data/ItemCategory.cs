using System;

namespace Potaria.Data
{
    /// <summary>
    /// Functional category classifications for items in Potaria.
    /// </summary>
    public enum ItemCategory
    {
        Tool,
        Weapon,
        Block,
        Wall,
        Material,
        Consumable,
        Food,
        Special,
        Accessory,
        Currency,
        Armor,
        Armor_Head,
        Armor_Chest,
        Armor_Legs
    }

    public static class ItemCategoryExtensions
    {
        public static ItemCategory FromString(string catStr)
        {
            if (string.IsNullOrEmpty(catStr)) return ItemCategory.Material;
            return catStr.ToLowerInvariant() switch
            {
                "tool" => ItemCategory.Tool,
                "weapon" => ItemCategory.Weapon,
                "block" => ItemCategory.Block,
                "wall" => ItemCategory.Wall,
                "material" => ItemCategory.Material,
                "consumable" => ItemCategory.Consumable,
                "food" => ItemCategory.Food,
                "special" => ItemCategory.Special,
                "accessory" => ItemCategory.Accessory,
                "currency" => ItemCategory.Currency,
                "armor" => ItemCategory.Armor,
                "armor_head" => ItemCategory.Armor_Head,
                "armor_chest" => ItemCategory.Armor_Chest,
                "armor_legs" => ItemCategory.Armor_Legs,
                "helmet" => ItemCategory.Armor_Head,
                "head" => ItemCategory.Armor_Head,
                "chest" => ItemCategory.Armor_Chest,
                "chestplate" => ItemCategory.Armor_Chest,
                "legs" => ItemCategory.Armor_Legs,
                "greaves" => ItemCategory.Armor_Legs,
                "boots" => ItemCategory.Armor_Legs,
                "equipment" => ItemCategory.Armor,
                _ => ItemCategory.Material
            };
        }
    }
}
