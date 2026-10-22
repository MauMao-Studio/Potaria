using System;

namespace Potaria.Data
{
    /// <summary>
    /// Crafting and cooking station requirements for recipes.
    /// </summary>
    public enum CraftingStation
    {
        Hand,
        Furnace,
        Campfire,
        WorkBench
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
                "workbench" => CraftingStation.WorkBench,
                "work_bench" => CraftingStation.WorkBench,
                "hand" => CraftingStation.Hand,
                _ => CraftingStation.Hand
            };
        }
    }
}
