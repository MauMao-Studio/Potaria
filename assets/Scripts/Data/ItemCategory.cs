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
        Armor
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
                "equipment" => ItemCategory.Armor,
                _ => ItemCategory.Material
            };
        }
    }
}
