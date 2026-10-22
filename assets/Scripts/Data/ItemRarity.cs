using System;
using UnityEngine;

namespace Potaria.Data
{
    /// <summary>
    /// Rarity tiers for all Potaria items, weapons, and equipment.
    /// Matched to the original Pygame palette and tier progression.
    /// </summary>
    public enum ItemRarity
    {
        Common,
        Uncommon,
        Rare,
        Epic,
        Mythic,
        Legendary,
        Ancient
    }

    public static class ItemRarityExtensions
    {
        public static Color GetColor(this ItemRarity rarity)
        {
            return rarity switch
            {
                ItemRarity.Common => new Color(0.9f, 0.9f, 0.9f, 1f),       // White/Light Gray #E5E5E5
                ItemRarity.Uncommon => new Color(0.2f, 0.8f, 0.3f, 1f),     // Green #33CC4D
                ItemRarity.Rare => new Color(0.2f, 0.5f, 1.0f, 1f),         // Blue #3380FF
                ItemRarity.Epic => new Color(0.7f, 0.25f, 0.9f, 1f),        // Purple #B240E6
                ItemRarity.Mythic => new Color(0.95f, 0.2f, 0.4f, 1f),      // Magenta/Crimson #F23366
                ItemRarity.Legendary => new Color(1.0f, 0.65f, 0.0f, 1f),   // Gold/Orange #FFA600
                ItemRarity.Ancient => new Color(0.0f, 0.9f, 0.85f, 1f),     // Cyan/Teal #00E6D9
                _ => Color.white
            };
        }

        public static string GetHexColor(this ItemRarity rarity)
        {
            return rarity switch
            {
                ItemRarity.Common => "#E5E5E5",
                ItemRarity.Uncommon => "#33CC4D",
                ItemRarity.Rare => "#3380FF",
                ItemRarity.Epic => "#B240E6",
                ItemRarity.Mythic => "#F23366",
                ItemRarity.Legendary => "#FFA600",
                ItemRarity.Ancient => "#00E6D9",
                _ => "#FFFFFF"
            };
        }

        public static ItemRarity FromString(string rarityStr)
        {
            if (string.IsNullOrEmpty(rarityStr)) return ItemRarity.Common;
            if (Enum.TryParse<ItemRarity>(rarityStr, true, out var result))
            {
                return result;
            }
            return ItemRarity.Common;
        }
    }
}
