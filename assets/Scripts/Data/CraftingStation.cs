using System;

namespace Potaria.Data
{
    /// <summary>
    /// Crafting and cooking station requirements for recipes.
    /// Supports the 5 canonical crafting stations:
    /// - Hand (None)
    /// - WorkBench (Workbench)
    /// - Furnace
    /// - Anvil
    /// - Campfire (CookingPot)
    /// </summary>
    public enum CraftingStation
    {
        Hand = 0,
        Furnace = 1,
        Campfire = 2,
        WorkBench = 3,
        Anvil = 4,
        CookingPot = 5,
        None = 0,
        Workbench = 3
    }

    public static class CraftingStationExtensions
    {
        public static CraftingStation FromString(string stationStr)
        {
            if (string.IsNullOrEmpty(stationStr)) return CraftingStation.Hand;
            return stationStr.ToLowerInvariant() switch
            {
                "furnace" => CraftingStation.Furnace,
                "campfire" => CraftingStation.Campfire,
                "cookingpot" => CraftingStation.Campfire,
                "cooking_pot" => CraftingStation.Campfire,
                "workbench" => CraftingStation.WorkBench,
                "work_bench" => CraftingStation.WorkBench,
                "anvil" => CraftingStation.Anvil,
                "none" => CraftingStation.Hand,
                "hand" => CraftingStation.Hand,
                _ => CraftingStation.Hand
            };
        }
    }
}
