using System;
using System.Collections.Generic;
using UnityEngine;
using Potaria.Data;
using Potaria.RPG;

namespace Potaria.World
{
    /// <summary>
    /// 30-slot storage chest container entity in Potaria.
    /// Interacted with in the world via right-click within 4 blocks.
    /// Supports Quick-Deposit and Loot-All operations.
    /// </summary>
    public class StorageChest : MonoBehaviour
    {
        public const int CHEST_ROWS = 3;
        public const int CHEST_COLS = 10;
        public const int TOTAL_CHEST_SLOTS = CHEST_ROWS * CHEST_COLS; // 30

        [Header("Chest Identification")]
        [SerializeField] private string chestId = "chest_default";
        [SerializeField] private string chestName = "Wooden Chest";

        private static readonly Dictionary<Vector2Int, StorageChest> s_worldChests = new Dictionary<Vector2Int, StorageChest>();

        public static StorageChest GetOrCreateAt(int gx, int gy, string name = "Storage Chest")
        {
            var pos = new Vector2Int(gx, gy);
            if (!s_worldChests.TryGetValue(pos, out var chest) || chest == null)
            {
                var go = new GameObject($"Chest_{gx}_{gy}");
                chest = go.AddComponent<StorageChest>();
                chest.ChestId = $"chest_{gx}_{gy}";
                chest.ChestName = name;
                s_worldChests[pos] = chest;
            }
            return chest;
        }

        public static void ClearWorldChests()
        {
            s_worldChests.Clear();
        }

        private readonly InventoryItemInstance[] _slots = new InventoryItemInstance[TOTAL_CHEST_SLOTS];

        public event Action OnChestChanged;

        public string ChestId { get => chestId; set => chestId = value; }
        public string ChestName { get => chestName; set => chestName = value; }

        public InventoryItemInstance GetSlot(int index)
        {
            if (index < 0 || index >= TOTAL_CHEST_SLOTS) return null;
            return _slots[index];
        }

        public void SetSlot(int index, InventoryItemInstance item)
        {
            if (index < 0 || index >= TOTAL_CHEST_SLOTS) return;
            _slots[index] = item;
            OnChestChanged?.Invoke();
        }

        public bool AddItem(InventoryItemInstance item)
        {
            if (item == null || item.Count <= 0 || item.ItemData == null) return false;

            // 1. Stack into existing slots
            int maxStack = item.MaxStack;
            if (maxStack > 1)
            {
                for (int i = 0; i < TOTAL_CHEST_SLOTS; i++)
                {
                    var slot = _slots[i];
                    if (slot != null && slot.CanStackWith(item))
                    {
                        int space = maxStack - slot.Count;
                        if (space > 0)
                        {
                            int take = Mathf.Min(space, item.Count);
                            slot.Count += take;
                            item.Count -= take;
                            if (item.Count <= 0)
                            {
                                OnChestChanged?.Invoke();
                                return true;
                            }
                        }
                    }
                }
            }

            // 2. Empty slots (respecting maxStack)
            for (int i = 0; i < TOTAL_CHEST_SLOTS; i++)
            {
                if (_slots[i] == null)
                {
                    int take = Mathf.Min(item.MaxStack, item.Count);
                    _slots[i] = item.Clone(take);
                    item.Count -= take;
                    if (item.Count <= 0)
                    {
                        OnChestChanged?.Invoke();
                        return true;
                    }
                }
            }

            OnChestChanged?.Invoke();
            return false;
        }

        public bool AddItem(string itemId, int count = 1)
        {
            var data = ItemDatabase.Instance.GetItem(itemId);
            if (data == null) return false;
            return AddItem(new InventoryItemInstance(data, count));
        }

        public int CountItem(string itemId)
        {
            if (string.IsNullOrEmpty(itemId)) return 0;
            int total = 0;
            for (int i = 0; i < TOTAL_CHEST_SLOTS; i++)
            {
                var s = _slots[i];
                if (s != null && s.ItemId.Equals(itemId, StringComparison.OrdinalIgnoreCase))
                {
                    total += s.Count;
                }
            }
            return total;
        }

        public bool HasMatchingItem(string itemId)
        {
            return CountItem(itemId) > 0;
        }

        /// <summary>
        /// Quick-Deposit: Scans player inventory (slots 0..39). If chest already contains
        /// an identical item and has space, moves or merges stacks into chest.
        /// </summary>
        public void QuickDeposit(PlayerInventory playerInventory)
        {
            if (playerInventory == null) return;

            for (int pIdx = 0; pIdx < PlayerInventory.TOTAL_SLOTS; pIdx++)
            {
                var invItem = playerInventory.GetSlot(pIdx);
                if (invItem == null) continue;

                // Check if chest contains matching item
                if (HasMatchingItem(invItem.ItemId))
                {
                    bool deposited = AddItem(invItem);
                    if (invItem.Count <= 0)
                    {
                        playerInventory.SetSlot(pIdx, null);
                    }
                    else
                    {
                        playerInventory.SetSlot(pIdx, invItem);
                    }
                }
            }
            OnChestChanged?.Invoke();
        }

        /// <summary>
        /// Loot-All: Transfers all items from chest into player inventory as long as inventory has space.
        /// </summary>
        public void LootAll(PlayerInventory playerInventory)
        {
            if (playerInventory == null) return;

            for (int cIdx = 0; cIdx < TOTAL_CHEST_SLOTS; cIdx++)
            {
                var chestItem = _slots[cIdx];
                if (chestItem == null) continue;

                bool added = playerInventory.AddItem(chestItem);
                if (chestItem.Count <= 0)
                {
                    _slots[cIdx] = null;
                }
            }
            OnChestChanged?.Invoke();
        }

        public void Clear()
        {
            for (int i = 0; i < TOTAL_CHEST_SLOTS; i++)
            {
                _slots[i] = null;
            }
            OnChestChanged?.Invoke();
        }
    }
}
