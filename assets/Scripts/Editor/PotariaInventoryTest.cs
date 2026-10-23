using System;
using System.Collections.Generic;
using UnityEditor;
using UnityEngine;
using UnityEngine.UI;
using Potaria.Data;
using Potaria.RPG;
using Potaria.UI;
using Potaria.World;

namespace Potaria.Editor
{
    /// <summary>
    /// Headless deep verification test suite for Milestone 4:
    /// 1. 40-slot backpack inventory, hotbar integration, slot swapping, stack splitting, organize & auto-sort
    /// 2. Coin purse with automatic 100:1 conversion (100c = 1s, 100s = 1g) and change making
    /// 3. 10-slot paperdoll equipment system with immediate PlayerStats recalculation
    /// 4. 27 progressive equipment sets bonus milestone activation (2-pc, 4-pc, 5-pc)
    /// 5. Side-by-side 'Katabi' comparison tooltips with circular affix sockets and screen clamping
    /// 6. 5-tab crafting interface with proximity checks, material sufficiency, and one-click crafting
    /// 7. Forge Master enhancement (+1 to +7), break risks, 1 Gold repair, and affix stone carving
    /// 8. 30-slot storage chest container with Quick-Deposit and Loot-All
    ///
    /// Executed in batchmode via:
    /// Potaria.Editor.PotariaInventoryTest.RunTests
    /// </summary>
    public static class PotariaInventoryTest
    {
        private static int s_passedTests = 0;
        private static int s_failedTests = 0;

        [MenuItem("Potaria/Run Milestone 4 Inventory & UI Tests", priority = 33)]
        public static void RunTests()
        {
            s_passedTests = 0;
            s_failedTests = 0;

            Debug.Log("================================================================================");
            Debug.Log("[PotariaInventoryTest] Executing Milestone 4 Deep Verification Test Suite...");
            Debug.Log("================================================================================");

            try
            {
                TestCoinPurseAutoConversionAndChange();
                Test40SlotBackpackOperations();
                TestInventoryOrganizeAndAutoSorting();
                TestPaperdoll10SlotEquipmentAndStatsRecalculation();
                TestEquipmentSetBonuses27Sets();
                TestSideBySideKatabiComparisonTooltips();
                Test5TabCraftingInterfaceAndProximity();
                TestForgeMasterEnhancementAndBreakRisk();
                TestForge1GoldRepair();
                TestForgeAffixCarvingAndEmbedding();
                Test30SlotStorageChestQuickDepositAndLootAll();
                TestHotbarIntegrationWithBackpack();
            }
            catch (Exception ex)
            {
                s_failedTests++;
                Debug.LogError($"[FATAL EXCEPTION in PotariaInventoryTest]: {ex.Message}\n{ex.StackTrace}");
            }

            Debug.Log("================================================================================");
            Debug.Log($"[PotariaInventoryTest] Test Execution Summary: {s_passedTests} Passed, {s_failedTests} Failed.");
            Debug.Log("================================================================================");

            if (s_failedTests > 0)
            {
                Debug.LogError($"[PotariaInventoryTest] FATAL: {s_failedTests} test(s) failed!");
            }
            else
            {
                Debug.Log("[PotariaInventoryTest] SUCCESS: All Milestone 4 systems verified with 0 errors.");
            }
        }

        private static void AssertTrue(bool condition, string testName, string failMessage = "")
        {
            if (condition)
            {
                s_passedTests++;
                Debug.Log($"[PASS] {testName}");
            }
            else
            {
                s_failedTests++;
                Debug.LogError($"[FAIL] {testName}: {failMessage}");
            }
        }

        private static void AssertEqual<T>(T expected, T actual, string testName)
        {
            if (EqualityComparer<T>.Default.Equals(expected, actual))
            {
                s_passedTests++;
                Debug.Log($"[PASS] {testName} (Value: {actual})");
            }
            else
            {
                s_failedTests++;
                Debug.LogError($"[FAIL] {testName}: Expected [{expected}], but received [{actual}]");
            }
        }

        // ====================================================================
        // 1. Coin Purse & Denomination Conversion (100c = 1s, 100s = 1g)
        // ====================================================================
        private static void TestCoinPurseAutoConversionAndChange()
        {
            Debug.Log("--- 1. Testing Coin Purse 100:1 Auto-Conversion ---");

            var go = new GameObject("TestCoinPurseHolder");
            try
            {
                var stats = go.AddComponent<PlayerStats>();
                var inv = go.AddComponent<PlayerInventory>();
                inv.Stats = stats;

                AssertEqual(0, inv.TotalCopperValue, "CoinPurse_InitialZero");

                // Add 99 Copper -> 0g, 0s, 99c
                inv.AddCoins(copper: 99);
                AssertEqual(99, inv.CopperCoins, "CoinPurse_99Copper");
                AssertEqual(0, inv.SilverCoins, "CoinPurse_99Copper_SilverZero");
                AssertEqual(0, inv.GoldCoins, "CoinPurse_99Copper_GoldZero");

                // Add 1 more Copper -> 100c converts to 1 Silver (0g, 1s, 0c)
                inv.AddCoins(copper: 1);
                AssertEqual(0, inv.CopperCoins, "CoinPurse_100c_CopperRollsToZero");
                AssertEqual(1, inv.SilverCoins, "CoinPurse_100c_Gives1Silver");
                AssertEqual(0, inv.GoldCoins, "CoinPurse_100c_GoldZero");
                AssertEqual(100, inv.TotalCopperValue, "CoinPurse_Total100Copper");

                // Add 99 Silver -> 100s converts to 1 Gold (1g, 0s, 0c)
                inv.AddCoins(silver: 99);
                AssertEqual(1, inv.GoldCoins, "CoinPurse_100s_Gives1Gold");
                AssertEqual(0, inv.SilverCoins, "CoinPurse_100s_SilverRollsToZero");
                AssertEqual(0, inv.CopperCoins, "CoinPurse_100s_CopperZero");
                AssertEqual(10000, inv.TotalCopperValue, "CoinPurse_1GoldIs10000Copper");

                // Spend 150 Copper from 1 Gold (10,000 - 150 = 9,850 => 0g, 98s, 50c)
                bool removed = inv.RemoveCoins(150);
                AssertTrue(removed, "CoinPurse_Spend150Copper_Success");
                AssertEqual(0, inv.GoldCoins, "CoinPurse_ChangeGoldZero");
                AssertEqual(98, inv.SilverCoins, "CoinPurse_Change98Silver");
                AssertEqual(50, inv.CopperCoins, "CoinPurse_Change50Copper");
                AssertEqual(9850, inv.TotalCopperValue, "CoinPurse_Remaining9850Copper");

                // Spend exceeding balance fails
                bool overspend = inv.RemoveCoins(20000);
                AssertTrue(!overspend, "CoinPurse_OverspendFails");
                AssertEqual(9850, inv.TotalCopperValue, "CoinPurse_BalanceIntactAfterFailedSpend");
            }
            finally
            {
                UnityEngine.Object.DestroyImmediate(go);
            }
        }

        // ====================================================================
        // 2. 40-Slot Backpack Operations
        // ====================================================================
        private static void Test40SlotBackpackOperations()
        {
            Debug.Log("--- 2. Testing 40-Slot Backpack Inventory Operations ---");

            var go = new GameObject("TestBackpackHolder");
            try
            {
                var inv = go.AddComponent<PlayerInventory>();
                AssertEqual(40, PlayerInventory.TOTAL_SLOTS, "Backpack_Total40Slots");
                AssertEqual(10, PlayerInventory.HOTBAR_SLOTS, "Backpack_Hotbar10Slots");

                // Create sample item data
                var stoneItem = ScriptableObject.CreateInstance<ItemData>();
                stoneItem.ItemId = "stone_block";
                stoneItem.ItemName = "Stone Block";
                stoneItem.Category = ItemCategory.Block;
                stoneItem.MaxStack = 99;

                var woodItem = ScriptableObject.CreateInstance<ItemData>();
                woodItem.ItemId = "wood";
                woodItem.ItemName = "Wood";
                woodItem.Category = ItemCategory.Block;
                woodItem.MaxStack = 99;

                // Add 50 Stone -> fills slot 0
                bool add1 = inv.AddItem(stoneItem, 50);
                AssertTrue(add1, "Backpack_Add50Stone_Success");
                AssertEqual(50, inv.GetSlot(0).Count, "Backpack_Slot0_Count50");

                // Add 60 more Stone -> stacks 49 into slot 0 (reaching 99), puts remaining 11 into slot 1
                bool add2 = inv.AddItem(stoneItem, 60);
                AssertTrue(add2, "Backpack_Add60Stone_StackAndOverflow");
                AssertEqual(99, inv.GetSlot(0).Count, "Backpack_Slot0_MaxStack99");
                AssertEqual(11, inv.GetSlot(1).Count, "Backpack_Slot1_OverflowCount11");
                AssertEqual(110, inv.CountItem("stone_block"), "Backpack_TotalStone110");

                // Add 30 Wood -> goes to slot 2
                inv.AddItem(woodItem, 30);
                AssertEqual("wood", inv.GetSlot(2).ItemId, "Backpack_Slot2_Wood");

                // Swap slot 0 and slot 2
                bool swapped = inv.SwapSlots(0, 2);
                AssertTrue(swapped, "Backpack_SwapSlots0And2_Success");
                AssertEqual("wood", inv.GetSlot(0).ItemId, "Backpack_Slot0_NowWood");
                AssertEqual("stone_block", inv.GetSlot(2).ItemId, "Backpack_Slot2_NowStone");

                // Split stack: take half from slot 2 (count 99 -> 50 remaining, 49 into empty slot 3)
                bool split = inv.SplitStack(2, 3);
                AssertTrue(split, "Backpack_SplitStack_Success");
                AssertEqual(49, inv.GetSlot(2).Count, "Backpack_Slot2_Remaining49");
                AssertEqual(50, inv.GetSlot(3).Count, "Backpack_Slot3_Split50");

                // Drop item from slot 3
                var dropped = inv.DropItem(3);
                AssertTrue(dropped != null && dropped.Count == 50, "Backpack_DropItemSlot3");
                AssertTrue(inv.IsSlotEmpty(3), "Backpack_Slot3_NowEmptyAfterDrop");

                // Quick-trash slot 0
                inv.TrashItem(0);
                AssertTrue(inv.IsSlotEmpty(0), "Backpack_Slot0_TrashedAndEmpty");

                UnityEngine.Object.DestroyImmediate(stoneItem);
                UnityEngine.Object.DestroyImmediate(woodItem);
            }
            finally
            {
                UnityEngine.Object.DestroyImmediate(go);
            }
        }

        // ====================================================================
        // 3. Inventory Organize (Compaction) & Auto-Sorting
        // ====================================================================
        private static void TestInventoryOrganizeAndAutoSorting()
        {
            Debug.Log("--- 3. Testing Inventory Organize & Auto-Sorting ---");

            var go = new GameObject("TestOrganizeHolder");
            try
            {
                var inv = go.AddComponent<PlayerInventory>();

                var dirt = ScriptableObject.CreateInstance<ItemData>();
                dirt.ItemId = "dirt_block";
                dirt.ItemName = "Dirt Block";
                dirt.Category = ItemCategory.Block;
                dirt.Rarity = ItemRarity.Common;
                dirt.MaxStack = 99;

                var copper = ScriptableObject.CreateInstance<ItemData>();
                copper.ItemId = "copper_bar";
                copper.ItemName = "Copper Bar";
                copper.Category = ItemCategory.Material;
                copper.Rarity = ItemRarity.Uncommon;
                copper.MaxStack = 99;

                var sword = ScriptableObject.CreateInstance<WeaponItemData>();
                sword.ItemId = "iron_sword";
                sword.ItemName = "Iron Sword";
                sword.Category = ItemCategory.Weapon;
                sword.Rarity = ItemRarity.Rare;
                sword.MaxStack = 1;

                // Intentionally place items in non-consecutive slots with gaps
                inv.SetSlot(10, new InventoryItemInstance(dirt, 20));
                inv.SetSlot(15, new InventoryItemInstance(dirt, 30)); // identical, should merge
                inv.SetSlot(22, new InventoryItemInstance(copper, 10));
                inv.SetSlot(35, new InventoryItemInstance(sword, 1));

                // Execute Organize on backpack (slots 10..39)
                inv.Organize(includeHotbar: false);

                // Slot 10 should now have merged dirt (20 + 30 = 50)
                AssertEqual("dirt_block", inv.GetSlot(10).ItemId, "Organize_Slot10_Dirt");
                AssertEqual(50, inv.GetSlot(10).Count, "Organize_Slot10_MergedCount50");
                // Slot 11 should have copper
                AssertEqual("copper_bar", inv.GetSlot(11).ItemId, "Organize_Slot11_Copper");
                // Slot 12 should have sword
                AssertEqual("iron_sword", inv.GetSlot(12).ItemId, "Organize_Slot12_Sword");
                // Slot 13..39 should be empty
                AssertTrue(inv.IsSlotEmpty(13), "Organize_Slot13_EmptyGapCompacted");

                // Execute Auto-Sort by Rarity (Rare sword first, then Uncommon copper, then Common dirt)
                inv.SortByRarity(includeHotbar: false);
                AssertEqual("iron_sword", inv.GetSlot(10).ItemId, "SortRarity_Slot10_HighestRareSword");
                AssertEqual("copper_bar", inv.GetSlot(11).ItemId, "SortRarity_Slot11_UncommonCopper");
                AssertEqual("dirt_block", inv.GetSlot(12).ItemId, "SortRarity_Slot12_CommonDirt");

                // Execute Auto-Sort by Name (Copper Bar, Dirt Block, Iron Sword)
                inv.SortByName(includeHotbar: false);
                AssertEqual("copper_bar", inv.GetSlot(10).ItemId, "SortName_Slot10_CopperBar");
                AssertEqual("dirt_block", inv.GetSlot(11).ItemId, "SortName_Slot11_DirtBlock");
                AssertEqual("iron_sword", inv.GetSlot(12).ItemId, "SortName_Slot12_IronSword");

                UnityEngine.Object.DestroyImmediate(dirt);
                UnityEngine.Object.DestroyImmediate(copper);
                UnityEngine.Object.DestroyImmediate(sword);
            }
            finally
            {
                UnityEngine.Object.DestroyImmediate(go);
            }
        }

        // ====================================================================
        // 4. 10-Slot Paperdoll Equipment & Immediate Stats Recalculation
        // ====================================================================
        private static void TestPaperdoll10SlotEquipmentAndStatsRecalculation()
        {
            Debug.Log("--- 4. Testing 10-Slot Paperdoll Equipment & Stats Recalculation ---");

            var go = new GameObject("TestPaperdollHolder");
            try
            {
                var stats = go.AddComponent<PlayerStats>();
                var inv = go.AddComponent<PlayerInventory>();
                var equip = go.AddComponent<PlayerEquipment>();
                equip.Stats = stats;
                equip.Inventory = inv;

                AssertEqual(10, PlayerEquipment.TOTAL_EQUIP_SLOTS, "Paperdoll_Total10Slots");

                // Baseline stats at level 1: Atk=10, Def=2, MaxHp=100, MaxMp=50
                AssertEqual(10, stats.TotalAtk, "Paperdoll_BaseAtk10");
                AssertEqual(2, stats.TotalDef, "Paperdoll_BaseDef2");
                AssertEqual(100, stats.MaxHp, "Paperdoll_BaseMaxHp100");

                // Create sample equipment
                var helm = ScriptableObject.CreateInstance<EquipmentItemData>();
                helm.ItemId = "iron_helmet";
                helm.ItemName = "Iron Helmet";
                helm.EquipSlot = EquipSlot.Helmet;
                helm.Defense = 6;
                helm.BonusHp = 20;

                var chest = ScriptableObject.CreateInstance<EquipmentItemData>();
                chest.ItemId = "iron_chestplate";
                chest.ItemName = "Iron Chestplate";
                chest.EquipSlot = EquipSlot.Chestplate;
                chest.Defense = 14;
                chest.Attack = 5;

                var sword = ScriptableObject.CreateInstance<WeaponItemData>();
                sword.ItemId = "iron_broadsword";
                sword.ItemName = "Iron Broadsword";
                sword.Attack = 18;
                sword.CritChance = 8.0f;

                var ring = ScriptableObject.CreateInstance<EquipmentItemData>();
                ring.ItemId = "silver_ring";
                ring.ItemName = "Silver Ring";
                ring.EquipSlot = EquipSlot.Accessory;
                ring.Attack = 4;
                ring.Defense = 2;
                ring.Speed = 0.25f;

                // Equip Helmet into slot 0
                bool eq1 = equip.EquipItem(new InventoryItemInstance(helm), (int)PaperdollSlot.Head);
                AssertTrue(eq1, "Paperdoll_EquipHelmetHead");
                AssertEqual(8, stats.TotalDef, "Paperdoll_DefRecalculated_2plus6");
                AssertEqual(120, stats.MaxHp, "Paperdoll_HpRecalculated_100plus20");

                // Equip Chest into slot 1
                bool eq2 = equip.EquipItem(new InventoryItemInstance(chest), (int)PaperdollSlot.Chest);
                AssertTrue(eq2, "Paperdoll_EquipChestplate");
                AssertEqual(22, stats.TotalDef, "Paperdoll_DefRecalculated_8plus14");
                AssertEqual(15, stats.TotalAtk, "Paperdoll_AtkRecalculated_10plus5");

                // Equip Weapon into slot 3
                bool eq3 = equip.EquipItem(new InventoryItemInstance(sword), (int)PaperdollSlot.Weapon);
                AssertTrue(eq3, "Paperdoll_EquipWeapon");
                AssertEqual(33, stats.TotalAtk, "Paperdoll_AtkRecalculated_15plus18");

                // Equip Ring into Accessory 1 (slot 4)
                bool eq4 = equip.EquipItem(new InventoryItemInstance(ring), (int)PaperdollSlot.Accessory1);
                AssertTrue(eq4, "Paperdoll_EquipAccessory1");
                AssertEqual(37, stats.TotalAtk, "Paperdoll_AtkRecalculated_33plus4");
                AssertEqual(24, stats.TotalDef, "Paperdoll_DefRecalculated_22plus2");

                // Unequip Weapon -> ATK drops back by 18 to 19
                equip.UnequipItem((int)PaperdollSlot.Weapon, inv);
                AssertEqual(19, stats.TotalAtk, "Paperdoll_UnequipWeapon_AtkReducedTo19");
                AssertEqual("iron_broadsword", inv.GetSlot(0).ItemId, "Paperdoll_UnequipReturnsItemToInventory");

                UnityEngine.Object.DestroyImmediate(helm);
                UnityEngine.Object.DestroyImmediate(chest);
                UnityEngine.Object.DestroyImmediate(sword);
                UnityEngine.Object.DestroyImmediate(ring);
            }
            finally
            {
                UnityEngine.Object.DestroyImmediate(go);
            }
        }

        // ====================================================================
        // 5. 27 Equipment Sets Bonus Activation (2-pc, 4-pc, 5-pc)
        // ====================================================================
        private static void TestEquipmentSetBonuses27Sets()
        {
            Debug.Log("--- 5. Testing 27 Equipment Sets Bonus Milestone Synergies ---");

            var allSets = ItemDatabase.Instance.GetAllEquipmentSets();
            AssertEqual(27, allSets.Count, "SetBonuses_27RegisteredEquipmentSets");

            // Look up Katipunero set
            var katipSet = ItemDatabase.Instance.GetEquipmentSet("katipunero");
            AssertTrue(katipSet != null, "SetBonuses_KatipuneroSetFound");

            var go = new GameObject("TestSetHolder");
            try
            {
                var stats = go.AddComponent<PlayerStats>();
                var inv = go.AddComponent<PlayerInventory>();
                var equip = go.AddComponent<PlayerEquipment>();
                equip.Stats = stats;
                equip.Inventory = inv;

                // Create dummy pieces for Katipunero set
                var bolo = ScriptableObject.CreateInstance<WeaponItemData>();
                bolo.ItemId = "katipunero_bolo";
                bolo.Attack = 15;

                var salakot = ScriptableObject.CreateInstance<EquipmentItemData>();
                salakot.ItemId = "salakot";
                salakot.EquipSlot = EquipSlot.Helmet;
                salakot.Defense = 5;

                var barong = ScriptableObject.CreateInstance<EquipmentItemData>();
                barong.ItemId = "barong_tagalog";
                barong.EquipSlot = EquipSlot.Chestplate;
                barong.Defense = 10;

                var bakya = ScriptableObject.CreateInstance<EquipmentItemData>();
                bakya.ItemId = "bakya";
                bakya.EquipSlot = EquipSlot.Greaves;
                bakya.Defense = 8;

                // Equip 1 piece: No set bonus active yet
                equip.EquipItem(new InventoryItemInstance(bolo), (int)PaperdollSlot.Weapon);
                AssertEqual(0, equip.ActiveSetBonuses.Count, "SetBonuses_1Piece_NoBonus");

                // Equip 2nd piece (Salakot): 2-Piece bonus unlocks!
                // Katipunero 2-pc: +15% ATK, +15% DEF, +25 Max HP
                equip.EquipItem(new InventoryItemInstance(salakot), (int)PaperdollSlot.Head);
                AssertEqual(1, equip.ActiveSetBonuses.Count, "SetBonuses_2Pieces_2PcBonusActive");
                AssertEqual(2, equip.ActiveSetBonuses[0].EquippedCount, "SetBonuses_2Pieces_Count2");

                // Equip 3rd and 4th pieces (Barong, Bakya): 4-Piece bonus unlocks!
                // Katipunero 4-pc: +28% ATK, +25% DEF, +0.25 Speed, +15% Crit
                equip.EquipItem(new InventoryItemInstance(barong), (int)PaperdollSlot.Chest);
                equip.EquipItem(new InventoryItemInstance(bakya), (int)PaperdollSlot.Legs);
                AssertEqual(4, equip.ActiveSetBonuses[0].EquippedCount, "SetBonuses_4Pieces_Count4");
                AssertTrue(equip.ActiveSetBonuses[0].UnlockedThresholds.Count >= 2, "SetBonuses_4Pieces_BothThresholdsActive");

                // Verify stat boosts are active
                AssertTrue(stats.TotalAtk > 30, "SetBonuses_AtkAmplifiedBySetMultipliers");
                AssertTrue(stats.TotalDef > 25, "SetBonuses_DefAmplifiedBySetMultipliers");

                UnityEngine.Object.DestroyImmediate(bolo);
                UnityEngine.Object.DestroyImmediate(salakot);
                UnityEngine.Object.DestroyImmediate(barong);
                UnityEngine.Object.DestroyImmediate(bakya);
            }
            finally
            {
                UnityEngine.Object.DestroyImmediate(go);
            }
        }

        // ====================================================================
        // 6. Side-by-Side 'Katabi' Tooltips & Affix Sockets
        // ====================================================================
        private static void TestSideBySideKatabiComparisonTooltips()
        {
            Debug.Log("--- 6. Testing Side-by-Side Katabi Tooltips & Affix Sockets ---");

            var go = new GameObject("TestTooltipHolder");
            try
            {
                var canvas = go.AddComponent<Canvas>();
                var scaler = go.AddComponent<CanvasScaler>();
                scaler.referenceResolution = new Vector2(1920f, 1080f);
                var tooltip = go.AddComponent<KatabiTooltipUI>();
                tooltip.BuildCardHierarchyIfMissing();

                var ironSword = ScriptableObject.CreateInstance<WeaponItemData>();
                ironSword.ItemId = "iron_sword";
                ironSword.ItemName = "Iron Sword";
                ironSword.Attack = 15;
                ironSword.AffixSlots = 1;

                var goldSword = ScriptableObject.CreateInstance<WeaponItemData>();
                goldSword.ItemId = "gold_sword";
                goldSword.ItemName = "Gold Sword";
                goldSword.Attack = 25;
                goldSword.AffixSlots = 2;

                var candInstance = new InventoryItemInstance(goldSword);
                candInstance.AffixSlots = 2;
                candInstance.Affixes.Add("Titan's Might");

                var eqInstance = new InventoryItemInstance(ironSword);

                // Show dual cards
                tooltip.Show(candInstance, eqInstance, new Vector2(960, 540));
                AssertTrue(tooltip.gameObject.activeSelf, "KatabiTooltip_ActiveOnShow");

                // Hide
                tooltip.Hide();
                AssertTrue(!tooltip.gameObject.activeSelf, "KatabiTooltip_InactiveOnHide");

                UnityEngine.Object.DestroyImmediate(ironSword);
                UnityEngine.Object.DestroyImmediate(goldSword);
            }
            finally
            {
                UnityEngine.Object.DestroyImmediate(go);
            }
        }

        // ====================================================================
        // 7. 5-Tab Crafting Interface & Station Proximity
        // ====================================================================
        private static void Test5TabCraftingInterfaceAndProximity()
        {
            Debug.Log("--- 7. Testing 5-Tab Crafting Interface & One-Click Crafting ---");

            var go = new GameObject("TestCraftingHolder");
            try
            {
                var inv = go.AddComponent<PlayerInventory>();
                var crafting = go.AddComponent<CraftingUI>();
                crafting.BuildUIHierarchy();

                // Test CraftingStation enum values and 5 canonical tabs
                AssertEqual((int)CraftingStation.Hand, 0, "Crafting_HandIsStation0");
                AssertEqual((int)CraftingStation.Furnace, 1, "Crafting_FurnaceIsStation1");
                AssertEqual((int)CraftingStation.Campfire, 2, "Crafting_CampfireIsStation2");
                AssertEqual((int)CraftingStation.WorkBench, 3, "Crafting_WorkBenchIsStation3");
                AssertEqual((int)CraftingStation.Anvil, 4, "Crafting_AnvilIsStation4");

                // Test station proximity check for Hand
                AssertTrue(crafting.IsStationNearby(CraftingStation.Hand), "Crafting_HandAlwaysAvailable");

                // Create sample recipe: 2 Wood -> 1 Wooden Sword
                var woodItem = ScriptableObject.CreateInstance<ItemData>();
                woodItem.ItemId = "wood";
                woodItem.ItemName = "Wood";

                var swordItem = ScriptableObject.CreateInstance<WeaponItemData>();
                swordItem.ItemId = "wooden_sword";
                swordItem.ItemName = "Wooden Sword";

                var recipe = ScriptableObject.CreateInstance<RecipeData>();
                recipe.RecipeId = "recipe_test_wood_sword";
                recipe.CraftingStation = CraftingStation.Hand;
                recipe.ResultItemId = "wooden_sword";
                recipe.ResultItemData = swordItem;
                recipe.ResultCount = 1;
                recipe.Ingredients.Add(new RecipeIngredient("wood", 2, woodItem));

                ItemDatabase.Instance.RegisterItem(woodItem);
                ItemDatabase.Instance.RegisterItem(swordItem);
                ItemDatabase.Instance.RegisterRecipe(recipe);

                // Inventory has 0 wood: crafting fails
                bool craftFail = crafting.ExecuteCraft(recipe);
                AssertTrue(!craftFail, "Crafting_CannotCraftWithoutMaterials");

                // Add 5 wood
                inv.AddItem(woodItem, 5);
                AssertEqual(5, inv.CountItem("wood"), "Crafting_InventoryHas5Wood");

                // Execute craft: consumes 2 wood, leaves 3, yields 1 wooden sword
                bool craftSuccess = crafting.ExecuteCraft(recipe);
                AssertTrue(craftSuccess, "Crafting_OneClickCraft_Success");
                AssertEqual(3, inv.CountItem("wood"), "Crafting_Consumed2Wood_Remaining3");
                AssertEqual(1, inv.CountItem("wooden_sword"), "Crafting_Yielded1WoodenSword");

                UnityEngine.Object.DestroyImmediate(woodItem);
                UnityEngine.Object.DestroyImmediate(swordItem);
                UnityEngine.Object.DestroyImmediate(recipe);
            }
            finally
            {
                UnityEngine.Object.DestroyImmediate(go);
            }
        }

        // ====================================================================
        // 8. Forge Master Enhancement (+1 to +7) & Strategic Break Risks
        // ====================================================================
        private static void TestForgeMasterEnhancementAndBreakRisk()
        {
            Debug.Log("--- 8. Testing Forge Master Enhancement (+1 to +7) & Break Risks ---");

            var go = new GameObject("TestForgeHolder");
            try
            {
                var inv = go.AddComponent<PlayerInventory>();

                var sword = ScriptableObject.CreateInstance<WeaponItemData>();
                sword.ItemId = "iron_broadsword";
                sword.ItemName = "Iron Broadsword";
                sword.Attack = 20;

                var copperBar = ScriptableObject.CreateInstance<ItemData>();
                copperBar.ItemId = "copper_bar";
                ItemDatabase.Instance.RegisterItem(copperBar);

                var ironBar = ScriptableObject.CreateInstance<ItemData>();
                ironBar.ItemId = "iron_bar";
                ItemDatabase.Instance.RegisterItem(ironBar);

                var goldBar = ScriptableObject.CreateInstance<ItemData>();
                goldBar.ItemId = "gold_bar";
                ItemDatabase.Instance.RegisterItem(goldBar);

                var spudSap = ScriptableObject.CreateInstance<ItemData>();
                spudSap.ItemId = "spud_sap";
                ItemDatabase.Instance.RegisterItem(spudSap);

                var itemInstance = new InventoryItemInstance(sword);

                // Enhance to +1 requires 20 copper + 2 copper_bar
                // With insufficient resources, CanEnhance returns false
                bool can1 = ForgeSystem.CanEnhanceItem(itemInstance, inv, out var reason);
                AssertTrue(!can1, "Forge_CannotEnhanceWithoutCoinsOrMaterials");

                // Give coins and copper bars
                inv.AddCoins(copper: 20);
                inv.AddItem(copperBar, 2);

                // Forced roll 0.0f (guaranteed success) -> enhances to +1
                var res1 = ForgeSystem.EnhanceItem(itemInstance, inv, out var msg1, forcedRoll: 0.0f);
                AssertEqual(EnhanceResult.Success, res1, "Forge_EnhancePlus1_Success");
                AssertEqual(1, itemInstance.EnhancementLevel, "Forge_ItemLevelIs1");
                // Base 20 ATK * (1.0 + 1/7) = 20 * 1.1428 = 23
                AssertEqual(23, itemInstance.GetEffectiveAttack(), "Forge_Plus1_AtkScaledTo23");

                // Test break risk at +4 (BreakRate = 0.10f, SuccessRate = 0.70f)
                // Set level to +3
                itemInstance.EnhancementLevel = 3;
                inv.AddCoins(copper: 200);
                inv.AddItem(goldBar, 3);
                inv.AddItem(spudSap, 2);

                // Roll 0.75f falls into break window [0.70, 0.80) -> item breaks!
                var resBreak = ForgeSystem.EnhanceItem(itemInstance, inv, out var msgBreak, forcedRoll: 0.75f);
                AssertEqual(EnhanceResult.Broken, resBreak, "Forge_RollInBreakWindow_ItemBreaks");
                AssertTrue(itemInstance.IsBroken, "Forge_ItemIsBrokenTrue");
                AssertEqual(0, itemInstance.GetEffectiveAttack(), "Forge_BrokenItemEffectiveAtkIsZero");

                // Broken item cannot be enhanced further
                bool canBroken = ForgeSystem.CanEnhanceItem(itemInstance, inv, out _);
                AssertTrue(!canBroken, "Forge_BrokenItemCannotBeEnhanced");

                UnityEngine.Object.DestroyImmediate(sword);
                UnityEngine.Object.DestroyImmediate(copperBar);
                UnityEngine.Object.DestroyImmediate(ironBar);
                UnityEngine.Object.DestroyImmediate(goldBar);
                UnityEngine.Object.DestroyImmediate(spudSap);
            }
            finally
            {
                UnityEngine.Object.DestroyImmediate(go);
            }
        }

        // ====================================================================
        // 9. Forge 1 Gold Repair
        // ====================================================================
        private static void TestForge1GoldRepair()
        {
            Debug.Log("--- 9. Testing 1 Gold Equipment Repair ---");

            var go = new GameObject("TestRepairHolder");
            try
            {
                var inv = go.AddComponent<PlayerInventory>();

                var sword = ScriptableObject.CreateInstance<WeaponItemData>();
                sword.ItemId = "broken_sword";
                sword.ItemName = "Broken Sword";
                sword.Attack = 20;

                var item = new InventoryItemInstance(sword, 1, 3, broken: true);
                AssertTrue(item.IsBroken, "Repair_ItemStartsBroken");

                // Without 1 Gold (10,000 Copper), repair fails
                inv.AddCoins(copper: 5000);
                bool rep1 = ForgeSystem.RepairItem(item, inv, out _);
                AssertTrue(!rep1, "Repair_InsufficientFundsFails");

                // Add remaining 5,000 Copper (total 10,000c = 1 Gold)
                inv.AddCoins(copper: 5000);
                AssertEqual(10000, inv.TotalCopperValue, "Repair_Has1Gold");

                // Repair executes successfully, restores item and deducts 10,000c
                bool rep2 = ForgeSystem.RepairItem(item, inv, out var msg);
                AssertTrue(rep2, "Repair_1GoldSuccess");
                AssertTrue(!item.IsBroken, "Repair_ItemIsNoLongerBroken");
                AssertEqual(0, inv.TotalCopperValue, "Repair_Deducted10000Copper");
                AssertTrue(item.GetEffectiveAttack() > 0, "Repair_EffectiveAtkRestored");

                UnityEngine.Object.DestroyImmediate(sword);
            }
            finally
            {
                UnityEngine.Object.DestroyImmediate(go);
            }
        }

        // ====================================================================
        // 10. Affix Carving & Affix Stone Embedding
        // ====================================================================
        private static void TestForgeAffixCarvingAndEmbedding()
        {
            Debug.Log("--- 10. Testing Affix Carving & Affix Stone Embedding ---");

            var go = new GameObject("TestAffixHolder");
            try
            {
                var inv = go.AddComponent<PlayerInventory>();

                // Common items cannot receive affix slots
                var commonGear = ScriptableObject.CreateInstance<EquipmentItemData>();
                commonGear.Rarity = ItemRarity.Common;
                var commonInst = new InventoryItemInstance(commonGear);
                bool canCommon = ForgeSystem.CanCarveAffixSlot(commonInst, inv, out _);
                AssertTrue(!canCommon, "Affix_CommonCannotHaveAffixSlots");

                // Legendary item can receive up to 1 Affix Slot
                var legGear = ScriptableObject.CreateInstance<EquipmentItemData>();
                legGear.ItemId = "legendary_helm";
                legGear.ItemName = "Legendary Helm";
                legGear.Rarity = ItemRarity.Legendary;
                var legInst = new InventoryItemInstance(legGear);
                AssertEqual(0, legInst.AffixSlots, "Affix_Initial0Slots");

                // Carve slot requires 5,000 Copper
                inv.AddCoins(copper: 5000);
                bool carved = ForgeSystem.CarveAffixSlot(legInst, inv, out var msgCarve);
                AssertTrue(carved, "Affix_CarveSlot_Success");
                AssertEqual(1, legInst.AffixSlots, "Affix_AffixSlotsNow1");
                AssertEqual(0, inv.TotalCopperValue, "Affix_Cost5000Deducted");

                // Legendary limit is 1, so carving second slot fails
                inv.AddCoins(copper: 5000);
                bool carveSecond = ForgeSystem.CanCarveAffixSlot(legInst, inv, out _);
                AssertTrue(!carveSecond, "Affix_CannotExceedLegendaryLimitOf1");

                // Embedding Affix Stone requires possessing affix_stone
                bool canEmbedNoStone = ForgeSystem.CanApplyAffixStone(legInst, inv, out _);
                AssertTrue(!canEmbedNoStone, "Affix_CannotEmbedWithoutAffixStone");

                var stoneItem = ScriptableObject.CreateInstance<ItemData>();
                stoneItem.ItemId = "affix_stone";
                ItemDatabase.Instance.RegisterItem(stoneItem);
                inv.AddItem(stoneItem, 1);

                // Embed Affix Stone: grants god-tier affix
                bool embedded = ForgeSystem.ApplyAffixStone(legInst, inv, out var msgEmbed, chosenAffix: "Titan's Might");
                AssertTrue(embedded, "Affix_EmbedStone_Success");
                AssertEqual(1, legInst.Affixes.Count, "Affix_AffixCountIs1");
                AssertEqual("Titan's Might", legInst.Affixes[0], "Affix_HasTitansMight");
                AssertEqual(0, inv.CountItem("affix_stone"), "Affix_AffixStoneConsumed");

                // Slots now full (1/1), further embedding fails
                inv.AddItem(stoneItem, 1);
                bool embedFull = ForgeSystem.CanApplyAffixStone(legInst, inv, out _);
                AssertTrue(!embedFull, "Affix_CannotEmbedWhenSlotsFull");

                UnityEngine.Object.DestroyImmediate(commonGear);
                UnityEngine.Object.DestroyImmediate(legGear);
                UnityEngine.Object.DestroyImmediate(stoneItem);
            }
            finally
            {
                UnityEngine.Object.DestroyImmediate(go);
            }
        }

        // ====================================================================
        // 11. 30-Slot Storage Chest Quick-Deposit & Loot-All
        // ====================================================================
        private static void Test30SlotStorageChestQuickDepositAndLootAll()
        {
            Debug.Log("--- 11. Testing 30-Slot Storage Chest Quick-Deposit & Loot-All ---");

            var go = new GameObject("TestChestHolder");
            try
            {
                var inv = go.AddComponent<PlayerInventory>();
                var chest = go.AddComponent<StorageChest>();
                AssertEqual(30, StorageChest.TOTAL_CHEST_SLOTS, "Chest_Total30Slots");

                var ore = ScriptableObject.CreateInstance<ItemData>();
                ore.ItemId = "copper_ore";
                ore.ItemName = "Copper Ore";
                ore.MaxStack = 99;

                var wood = ScriptableObject.CreateInstance<ItemData>();
                wood.ItemId = "wood";
                wood.ItemName = "Wood";
                wood.MaxStack = 99;

                // Chest already has 10 copper_ore
                chest.SetSlot(0, new InventoryItemInstance(ore, 10));

                // Player inventory has 25 copper_ore and 30 wood
                inv.AddItem(ore, 25);
                inv.AddItem(wood, 30);
                AssertEqual(25, inv.CountItem("copper_ore"), "Chest_InvHas25Ore");
                AssertEqual(30, inv.CountItem("wood"), "Chest_InvHas30Wood");

                // Execute Quick-Deposit:
                // Only matching items (copper_ore) are deposited into chest; wood remains in inventory!
                chest.QuickDeposit(inv);
                AssertEqual(35, chest.CountItem("copper_ore"), "Chest_QuickDepositMergedOreTo35");
                AssertEqual(0, inv.CountItem("copper_ore"), "Chest_InvOreZeroAfterQuickDeposit");
                AssertEqual(30, inv.CountItem("wood"), "Chest_InvWoodIntactNonMatching");

                // Execute Loot-All:
                // Transfers all items from chest into player inventory
                chest.LootAll(inv);
                AssertEqual(0, chest.CountItem("copper_ore"), "Chest_ChestEmptyAfterLootAll");
                AssertEqual(35, inv.CountItem("copper_ore"), "Chest_InvNowHasAll35Ore");
                AssertEqual(30, inv.CountItem("wood"), "Chest_InvWoodStill30");

                UnityEngine.Object.DestroyImmediate(ore);
                UnityEngine.Object.DestroyImmediate(wood);
            }
            finally
            {
                UnityEngine.Object.DestroyImmediate(go);
            }
        }

        // ====================================================================
        // 12. Hotbar Integration with 40-Slot Backpack
        // ====================================================================
        private static void TestHotbarIntegrationWithBackpack()
        {
            Debug.Log("--- 12. Testing Hotbar Integration with 40-Slot Backpack ---");

            var go = new GameObject("TestHotbarSyncHolder");
            try
            {
                var hudObj = new GameObject("HUD_Canvas");
                var hud = hudObj.AddComponent<PotariaHUD>();
                PotariaHUD.Instance = hud;
                hud.BuildOrValidateUI();

                var playerObj = new GameObject("Player");
                var inv = playerObj.AddComponent<PlayerInventory>();
                inv.Hud = hud;

                var pick = ScriptableObject.CreateInstance<ItemData>();
                pick.ItemId = "copper_pickaxe";
                pick.ItemName = "Copper Pickaxe";

                // Setting slot 0 in inventory automatically updates HUD slot 0
                inv.SetSlot(0, new InventoryItemInstance(pick, 1));
                hud.SelectSlot(0);
                AssertEqual("copper_pickaxe", hud.GetItem(0).id, "HotbarSync_Slot0MatchesInventory");

                // Swap slot 0 with slot 5
                inv.SwapSlots(0, 5);
                AssertEqual("copper_pickaxe", hud.GetItem(5).id, "HotbarSync_Slot5NowMatchesInventory");
                AssertTrue(string.IsNullOrEmpty(hud.GetItem(0).id), "HotbarSync_Slot0NowEmpty");

                UnityEngine.Object.DestroyImmediate(pick);
                UnityEngine.Object.DestroyImmediate(playerObj);
                UnityEngine.Object.DestroyImmediate(hudObj);
            }
            finally
            {
                UnityEngine.Object.DestroyImmediate(go);
            }
        }
    }
}
