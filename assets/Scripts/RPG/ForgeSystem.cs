using System;
using System.Collections.Generic;
using UnityEngine;
using Potaria.Data;

namespace Potaria.RPG
{
    public enum EnhanceResult
    {
        Success,
        Failure,
        Broken,
        Error
    }

    [Serializable]
    public class EnhanceRequirement
    {
        public int Level;
        public int CopperCost;
        public Dictionary<string, int> Materials = new Dictionary<string, int>();
        public float SuccessRate;
        public float BreakRate;
    }

    /// <summary>
    /// Master Forge System for item enhancement (+1 to +7), 1 Gold repair,
    /// and affix carving with Affix Stones.
    /// </summary>
    public static class ForgeSystem
    {
        public const int MAX_ENHANCEMENT_LEVEL = 7;
        public const int REPAIR_COST_COPPER = 10000; // 1 Gold Coin = 10,000 Copper
        public const int AFFIX_CARVE_COST_COPPER = 5000;

        public static readonly List<string> GOD_TIER_AFFIXES = new List<string>
        {
            "Titan's Might",
            "Celestial Aegis",
            "Chronos Velocity",
            "Astral Omniscience",
            "Vampiric Leech",
            "Solar Flare",
            "Void Singularity",
            "Frostbite Cryo"
        };

        private static readonly Dictionary<int, EnhanceRequirement> s_requirements = new Dictionary<int, EnhanceRequirement>
        {
            { 1, new EnhanceRequirement { Level = 1, CopperCost = 20, Materials = new Dictionary<string, int> { { "copper_bar", 2 } }, SuccessRate = 1.00f, BreakRate = 0.00f } },
            { 2, new EnhanceRequirement { Level = 2, CopperCost = 50, Materials = new Dictionary<string, int> { { "iron_bar", 2 } }, SuccessRate = 0.90f, BreakRate = 0.00f } },
            { 3, new EnhanceRequirement { Level = 3, CopperCost = 100, Materials = new Dictionary<string, int> { { "iron_bar", 3 }, { "gold_bar", 1 } }, SuccessRate = 0.80f, BreakRate = 0.00f } },
            { 4, new EnhanceRequirement { Level = 4, CopperCost = 200, Materials = new Dictionary<string, int> { { "gold_bar", 3 }, { "spud_sap", 2 } }, SuccessRate = 0.70f, BreakRate = 0.10f } },
            { 5, new EnhanceRequirement { Level = 5, CopperCost = 500, Materials = new Dictionary<string, int> { { "gold_bar", 5 }, { "blightstone", 3 } }, SuccessRate = 0.50f, BreakRate = 0.15f } },
            { 6, new EnhanceRequirement { Level = 6, CopperCost = 1000, Materials = new Dictionary<string, int> { { "gold_bar", 8 }, { "portal_shard", 1 }, { "blightstone", 5 } }, SuccessRate = 0.35f, BreakRate = 0.20f } },
            { 7, new EnhanceRequirement { Level = 7, CopperCost = 2500, Materials = new Dictionary<string, int> { { "gold_bar", 10 }, { "portal_shard", 2 }, { "spud_sap", 5 } }, SuccessRate = 0.25f, BreakRate = 0.30f } }
        };

        public static EnhanceRequirement GetRequirement(int targetLevel)
        {
            s_requirements.TryGetValue(targetLevel, out var req);
            return req;
        }

        public static bool CanEnhanceItem(InventoryItemInstance item, PlayerInventory inventory, out string reason)
        {
            if (item == null || item.ItemData == null)
            {
                reason = "No item selected.";
                return false;
            }

            if (item.IsBroken)
            {
                reason = "This item is BROKEN! Repair it at the Forge for 1 Gold first.";
                return false;
            }

            if (item.EnhancementLevel >= MAX_ENHANCEMENT_LEVEL)
            {
                reason = $"Item is already at MAX enhancement (+{MAX_ENHANCEMENT_LEVEL})!";
                return false;
            }

            var data = item.ItemData;
            bool isGear = data is WeaponItemData || data is EquipmentItemData
                || data.Category == ItemCategory.Weapon || data.Category == ItemCategory.Tool
                || data.Category == ItemCategory.Armor || data.Category == ItemCategory.Armor_Head
                || data.Category == ItemCategory.Armor_Chest || data.Category == ItemCategory.Armor_Legs
                || data.Category == ItemCategory.Accessory;

            if (!isGear)
            {
                reason = "Only weapons, armor, and accessories can be enhanced.";
                return false;
            }

            int targetLevel = item.EnhancementLevel + 1;
            var req = GetRequirement(targetLevel);
            if (req == null)
            {
                reason = "Invalid enhancement requirement.";
                return false;
            }

            if (inventory != null)
            {
                if (inventory.TotalCopperValue < req.CopperCost)
                {
                    reason = $"Requires {req.CopperCost} Copper Coins (You have {inventory.TotalCopperValue}).";
                    return false;
                }

                foreach (var mat in req.Materials)
                {
                    if (inventory.CountItem(mat.Key) < mat.Value)
                    {
                        var matData = ItemDatabase.Instance.GetItem(mat.Key);
                        string matName = matData != null ? matData.ItemName : mat.Key;
                        reason = $"Requires {mat.Value}x {matName} (You have {inventory.CountItem(mat.Key)}).";
                        return false;
                    }
                }
            }

            reason = "Ready to enhance.";
            return true;
        }

        public static EnhanceResult EnhanceItem(InventoryItemInstance item, PlayerInventory inventory, out string message, float? forcedRoll = null)
        {
            if (!CanEnhanceItem(item, inventory, out var reason))
            {
                message = reason;
                return EnhanceResult.Error;
            }

            int targetLevel = item.EnhancementLevel + 1;
            var req = GetRequirement(targetLevel);

            // Deduct coins and materials
            if (inventory != null)
            {
                inventory.RemoveCoins(req.CopperCost);
                foreach (var mat in req.Materials)
                {
                    inventory.RemoveItem(mat.Key, mat.Value);
                }
            }

            float roll = forcedRoll.HasValue ? forcedRoll.Value : UnityEngine.Random.value;
            float succRate = req.SuccessRate;
            float breakRate = req.BreakRate;

            if (roll < succRate)
            {
                item.EnhancementLevel = targetLevel;
                int pct = Mathf.RoundToInt((item.GetEnhancementMultiplier() - 1.0f) * 100f);
                message = $"SUCCESS! {item.ItemName} enhanced to +{targetLevel}! (Stats +{pct}%)";
                return EnhanceResult.Success;
            }
            else if (roll < (succRate + breakRate))
            {
                item.IsBroken = true;
                message = $"CRITICAL FAILURE! {item.ItemName} has BROKEN! It cannot be equipped until repaired for 1 Gold Coin.";
                return EnhanceResult.Broken;
            }
            else
            {
                message = $"Enhancement attempt failed! Materials consumed, but {item.ItemName} remained intact at +{item.EnhancementLevel}.";
                return EnhanceResult.Failure;
            }
        }

        // --- 1 Gold Repair ---

        public static bool CanRepairItem(InventoryItemInstance item, PlayerInventory inventory, out string reason)
        {
            if (item == null || item.ItemData == null)
            {
                reason = "No item selected to repair.";
                return false;
            }

            if (!item.IsBroken)
            {
                reason = "This item is not broken.";
                return false;
            }

            if (inventory != null && inventory.TotalCopperValue < REPAIR_COST_COPPER)
            {
                reason = $"Repair requires 1 Gold Coin (10,000 Copper). You have {inventory.TotalCopperValue} Copper.";
                return false;
            }

            reason = "Ready to repair.";
            return true;
        }

        public static bool RepairItem(InventoryItemInstance item, PlayerInventory inventory, out string message)
        {
            if (!CanRepairItem(item, inventory, out var reason))
            {
                message = reason;
                return false;
            }

            if (inventory != null)
            {
                inventory.RemoveCoins(REPAIR_COST_COPPER);
            }

            item.IsBroken = false;
            message = $"Repaired! {item.ItemName} is fully restored to pristine battle condition!";
            return true;
        }

        // --- Affix Carving & Affix Stones ---

        public static int GetMaxAffixSlots(ItemRarity rarity)
        {
            switch (rarity)
            {
                case ItemRarity.Epic:
                case ItemRarity.Legendary:
                    return 1;
                case ItemRarity.Mythic:
                case ItemRarity.Ancient:
                    return 2;
                default:
                    return 0; // Common, Uncommon, Rare cannot have affix slots
            }
        }

        public static bool CanCarveAffixSlot(InventoryItemInstance item, PlayerInventory inventory, out string reason)
        {
            if (item == null || item.ItemData == null)
            {
                reason = "No item selected.";
                return false;
            }

            if (item.IsBroken)
            {
                reason = "Cannot carve an affix slot into a broken item! Repair it first.";
                return false;
            }

            int maxSlots = GetMaxAffixSlots(item.Rarity);
            if (maxSlots <= 0)
            {
                reason = "Only Epic, Legendary, Mythic, and Ancient items can receive Affix Slots!";
                return false;
            }

            if (item.AffixSlots >= maxSlots)
            {
                reason = $"Item has already reached the maximum limit of {maxSlots} Affix Slots for {item.Rarity} rarity!";
                return false;
            }

            if (inventory != null && inventory.TotalCopperValue < AFFIX_CARVE_COST_COPPER)
            {
                reason = $"Carving an Affix Slot requires {AFFIX_CARVE_COST_COPPER} Copper Coins.";
                return false;
            }

            reason = "Ready to carve Affix Slot.";
            return true;
        }

        public static bool CarveAffixSlot(InventoryItemInstance item, PlayerInventory inventory, out string message)
        {
            if (!CanCarveAffixSlot(item, inventory, out var reason))
            {
                message = reason;
                return false;
            }

            if (inventory != null)
            {
                inventory.RemoveCoins(AFFIX_CARVE_COST_COPPER);
            }

            item.AffixSlots++;
            item.AdditionalAffixSlots++;
            message = $"Affix Slot Carved into {item.ItemName}! Open Affix Slots: {item.AffixSlots}.";
            return true;
        }

        public static bool CanApplyAffixStone(InventoryItemInstance item, PlayerInventory inventory, out string reason)
        {
            if (item == null || item.ItemData == null)
            {
                reason = "No item selected.";
                return false;
            }

            if (item.IsBroken)
            {
                reason = "Cannot embed an Affix Stone into a broken item! Repair it first.";
                return false;
            }

            if (item.AffixSlots <= 0)
            {
                reason = "This item has no Affix Slots. Carve an affix slot first!";
                return false;
            }

            if (item.Affixes.Count >= item.AffixSlots)
            {
                reason = $"All {item.AffixSlots} Affix Slots are already filled!";
                return false;
            }

            if (inventory != null && !inventory.HasItem("affix_stone", 1))
            {
                reason = "You do not possess an Affix Stone! Craft one at a Work Bench.";
                return false;
            }

            reason = "Ready to embed Affix Stone.";
            return true;
        }

        public static bool ApplyAffixStone(InventoryItemInstance item, PlayerInventory inventory, out string message, string chosenAffix = null)
        {
            if (!CanApplyAffixStone(item, inventory, out var reason))
            {
                message = reason;
                return false;
            }

            if (inventory != null)
            {
                inventory.RemoveItem("affix_stone", 1);
            }

            if (string.IsNullOrEmpty(chosenAffix))
            {
                var available = new List<string>();
                foreach (var a in GOD_TIER_AFFIXES)
                {
                    if (!item.Affixes.Contains(a)) available.Add(a);
                }
                if (available.Count == 0) available.AddRange(GOD_TIER_AFFIXES);
                chosenAffix = available[UnityEngine.Random.Range(0, available.Count)];
            }

            item.Affixes.Add(chosenAffix);
            message = $"GOD-TIER AFFIX EMBEDDED! {item.ItemName} gained [{chosenAffix}]!";
            return true;
        }
    }
}
