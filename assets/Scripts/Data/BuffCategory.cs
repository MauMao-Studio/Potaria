using System;
using UnityEngine;

namespace Potaria.Data
{
    /// <summary>
    /// The 5-buff category system governing food meals and culinary dishes in Potaria:
    /// Offense, Defense, Mobility, Resource, Utility.
    /// Only the strongest meal buff within each category persists (or category stacking rules apply).
    /// </summary>
    public enum BuffCategory
    {
        None,
        Offense,
        Defense,
        Mobility,
        Resource,
        Utility
    }

    public static class BuffCategoryExtensions
    {
        public static Color GetColor(this BuffCategory category)
        {
            return category switch
            {
                BuffCategory.Offense => new Color(1f, 0.35f, 0.35f, 1f),    // Crimson / Red #FF5959
                BuffCategory.Defense => new Color(0.35f, 0.65f, 1f, 1f),    // Blue / Cyan #59A6FF
                BuffCategory.Mobility => new Color(0.35f, 0.95f, 0.45f, 1f), // Green #59F273
                BuffCategory.Resource => new Color(1f, 0.85f, 0.25f, 1f),   // Gold / Yellow #FFD940
                BuffCategory.Utility => new Color(0.85f, 0.45f, 0.95f, 1f), // Purple #D973F2
                _ => Color.white
            };
        }

        public static string GetHexColor(this BuffCategory category)
        {
            return category switch
            {
                BuffCategory.Offense => "#FF5959",
                BuffCategory.Defense => "#59A6FF",
                BuffCategory.Mobility => "#59F273",
                BuffCategory.Resource => "#FFD940",
                BuffCategory.Utility => "#D973F2",
                _ => "#FFFFFF"
            };
        }

        public static BuffCategory FromString(string catStr)
        {
            if (string.IsNullOrEmpty(catStr)) return BuffCategory.None;
            if (Enum.TryParse<BuffCategory>(catStr, true, out var result))
            {
                return result;
            }
            return BuffCategory.None;
        }
    }
}
