using System;
using System.Collections.Generic;
using UnityEngine;
using Potaria.Data;
using Potaria.UI;

namespace Potaria.RPG
{
    public enum InventorySortType
    {
        Category,
        Rarity,
        Name
    }

    /// <summary>
    /// Master 40-slot backpack inventory and coin purse manager for Potaria.
    /// - 4 rows x 10 columns (slots 0..39)
    /// - Slots 0..9 integrate seamlessly as the 10-slot Hotbar
    /// - Full item interaction: dragging, slot swapping, stack splitting, quick-trash, drop, and gap compaction
    /// - Auto-sorting by Category, Rarity, or Name
    /// - Dedicated Coin Purse with real-time 100:1 automatic conversion (100c = 1s, 100s = 1g)
    /// </summary>
    public class PlayerInventory : MonoBehaviour
    {
        public const int HOTBAR_SLOTS = 10;
        public const int INVENTORY_ROWS = 4;
        public const int INVENTORY_COLS = 10;
        public const int TOTAL_SLOTS = INVENTORY_ROWS * INVENTORY_COLS; // 40

        [Header("References")]
        [SerializeField] private PlayerStats stats;
        [SerializeField] private PotariaHUD hud;

        public PotariaHUD Hud
        {
            get => hud != null ? hud : PotariaHUD.Instance;
            set => hud = value;
        }

        [Header("Coin Purse Fallback (when PlayerStats is not attached)")]
        [SerializeField] private int localCopper = 0;
        [SerializeField] private int localSilver = 0;
        [SerializeField] private int localGold = 0;

        private readonly InventoryItemInstance[] _slots = new InventoryItemInstance[TOTAL_SLOTS];
        private InventoryItemInstance _heldItem = null;

        public event Action<int> OnSlotChanged;
        public event Action OnInventoryChanged;
        public event Action<int, int, int> OnCoinsChanged; // (copper, silver, gold)

        public InventoryItemInstance HeldItem
        {
            get => _heldItem;
            set => _heldItem = value;
        }

        public PlayerStats Stats
        {
            get => stats;
            set
            {
                stats = value;
                if (stats != null && (localCopper > 0 || localSilver > 0 || localGold > 0))
                {
                    stats.AddCoins(localCopper, localSilver, localGold);
                    localCopper = 0;
                    localSilver = 0;
                    localGold = 0;
                }
            }
        }

        public int CopperCoins
        {
            get => stats != null ? stats.CopperCoins : localCopper;
            set
            {
                if (stats != null)
                {
                    stats.SetFromCopper(TotalCopperValue - (CopperCoins - value));
                }
                else
                {
                    localCopper = value;
                }
                OnCoinsChanged?.Invoke(CopperCoins, SilverCoins, GoldCoins);
            }
        }

        public int SilverCoins
        {
            get => stats != null ? stats.SilverCoins : localSilver;
            set
            {
                if (stats != null)
                {
                    stats.SetFromCopper(TotalCopperValue - ((SilverCoins - value) * 100));
                }
                else
                {
                    localSilver = value;
                }
                OnCoinsChanged?.Invoke(CopperCoins, SilverCoins, GoldCoins);
            }
        }

        public int GoldCoins
        {
            get => stats != null ? stats.GoldCoins : localGold;
            set
            {
                if (stats != null)
                {
                    stats.SetFromCopper(TotalCopperValue - ((GoldCoins - value) * 10000));
                }
                else
                {
                    localGold = value;
                }
                OnCoinsChanged?.Invoke(CopperCoins, SilverCoins, GoldCoins);
            }
        }

        public int TotalCopperValue => stats != null ? stats.TotalCopperValue : (localCopper + localSilver * 100 + localGold * 10000);

        private void Awake()
        {
            if (stats == null) stats = GetComponent<PlayerStats>();
        }

        public InventoryItemInstance GetSlot(int index)
        {
            if (index < 0 || index >= TOTAL_SLOTS) return null;
            return _slots[index];
        }

        public void SetSlot(int index, InventoryItemInstance instance)
        {
            if (index < 0 || index >= TOTAL_SLOTS) return;
            _slots[index] = instance;
            NotifySlotChanged(index);
        }

        public void ClearSlot(int index)
        {
            SetSlot(index, null);
        }

        public bool IsSlotEmpty(int index)
        {
            return GetSlot(index) == null;
        }

        // --- Coin Purse Operations (Automatic 100:1 Conversion) ---

        public void AddCoins(int copper = 0, int silver = 0, int gold = 0)
        {
            if (stats != null)
            {
                stats.AddCoins(copper, silver, gold);
            }
            else
            {
                int total = TotalCopperValue + copper + (silver * 100) + (gold * 10000);
                total = Mathf.Max(0, total);
                localGold = total / 10000;
                int rem = total % 10000;
                localSilver = rem / 100;
                localCopper = rem % 100;
            }
            OnCoinsChanged?.Invoke(CopperCoins, SilverCoins, GoldCoins);
        }

        public bool RemoveCoins(int totalCopper)
        {
            bool success = false;
            if (stats != null)
            {
                success = stats.RemoveCoins(totalCopper);
            }
            else
            {
                if (TotalCopperValue >= totalCopper)
                {
                    int total = TotalCopperValue - totalCopper;
                    localGold = total / 10000;
                    int rem = total % 10000;
                    localSilver = rem / 100;
                    localCopper = rem % 100;
                    success = true;
                }
            }

            if (success)
            {
                OnCoinsChanged?.Invoke(CopperCoins, SilverCoins, GoldCoins);
            }
            return success;
        }

        // --- Item Management ---

        public bool AddItem(ItemData data, int count = 1, int enhancement = 0, bool broken = false)
        {
            if (data == null || count <= 0) return false;
            var instance = new InventoryItemInstance(data, count, enhancement, broken);
            return AddItem(instance);
        }

        public bool AddItem(string itemId, int count = 1)
        {
            if (string.IsNullOrEmpty(itemId) || count <= 0) return false;

            // Currency coin items directly convert into Coin Purse
            if (itemId.Equals("copper_coin", StringComparison.OrdinalIgnoreCase))
            {
                AddCoins(copper: count);
                return true;
            }
            if (itemId.Equals("silver_coin", StringComparison.OrdinalIgnoreCase))
            {
                AddCoins(silver: count);
                return true;
            }
            if (itemId.Equals("gold_coin", StringComparison.OrdinalIgnoreCase))
            {
                AddCoins(gold: count);
                return true;
            }

            var itemData = ItemDatabase.Instance.GetItem(itemId);
            if (itemData == null) return false;
            return AddItem(itemData, count);
        }

        public bool AddItem(InventoryItemInstance item)
        {
            if (item == null || item.Count <= 0 || item.ItemData == null) return false;

            // Currency check
            if (item.ItemId.Equals("copper_coin", StringComparison.OrdinalIgnoreCase))
            {
                AddCoins(copper: item.Count);
                return true;
            }
            if (item.ItemId.Equals("silver_coin", StringComparison.OrdinalIgnoreCase))
            {
                AddCoins(silver: item.Count);
                return true;
            }
            if (item.ItemId.Equals("gold_coin", StringComparison.OrdinalIgnoreCase))
            {
                AddCoins(gold: item.Count);
                return true;
            }

            // 1. Try stacking into existing identical slots
            int maxStack = item.MaxStack;
            if (maxStack > 1)
            {
                for (int i = 0; i < TOTAL_SLOTS; i++)
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
                            NotifySlotChanged(i);
                            if (item.Count <= 0)
                            {
                                OnInventoryChanged?.Invoke();
                                return true;
                            }
                        }
                    }
                }
            }

            // 2. Place into first empty slot
            for (int i = 0; i < TOTAL_SLOTS; i++)
            {
                if (_slots[i] == null)
                {
                    _slots[i] = item.Clone();
                    item.Count = 0;
                    NotifySlotChanged(i);
                    OnInventoryChanged?.Invoke();
                    return true;
                }
            }

            OnInventoryChanged?.Invoke();
            return false; // Inventory full
        }

        public bool RemoveItem(string itemId, int count)
        {
            if (string.IsNullOrEmpty(itemId) || count <= 0) return false;
            if (CountItem(itemId) < count) return false;

            int remaining = count;
            for (int i = 0; i < TOTAL_SLOTS; i++)
            {
                var slot = _slots[i];
                if (slot != null && slot.ItemId.Equals(itemId, StringComparison.OrdinalIgnoreCase))
                {
                    if (slot.Count <= remaining)
                    {
                        remaining -= slot.Count;
                        _slots[i] = null;
                        NotifySlotChanged(i);
                    }
                    else
                    {
                        slot.Count -= remaining;
                        remaining = 0;
                        NotifySlotChanged(i);
                        break;
                    }
                }
            }

            OnInventoryChanged?.Invoke();
            return true;
        }

        public int CountItem(string itemId)
        {
            if (string.IsNullOrEmpty(itemId)) return 0;
            int total = 0;
            for (int i = 0; i < TOTAL_SLOTS; i++)
            {
                var slot = _slots[i];
                if (slot != null && slot.ItemId.Equals(itemId, StringComparison.OrdinalIgnoreCase))
                {
                    total += slot.Count;
                }
            }
            return total;
        }

        public bool HasItem(string itemId, int count = 1)
        {
            return CountItem(itemId) >= count;
        }

        // --- Slot Interactions: Swap, Split, Drop, Trash ---

        public bool SwapSlots(int fromIndex, int toIndex)
        {
            if (fromIndex < 0 || fromIndex >= TOTAL_SLOTS || toIndex < 0 || toIndex >= TOTAL_SLOTS) return false;
            if (fromIndex == toIndex) return true;

            var a = _slots[fromIndex];
            var b = _slots[toIndex];

            // If stacking is possible
            if (a != null && b != null && b.CanStackWith(a))
            {
                int maxStack = b.MaxStack;
                int space = maxStack - b.Count;
                if (space > 0)
                {
                    int take = Mathf.Min(space, a.Count);
                    b.Count += take;
                    a.Count -= take;
                    if (a.Count <= 0)
                    {
                        _slots[fromIndex] = null;
                    }
                    NotifySlotChanged(fromIndex);
                    NotifySlotChanged(toIndex);
                    OnInventoryChanged?.Invoke();
                    return true;
                }
            }

            // Normal swap
            _slots[fromIndex] = b;
            _slots[toIndex] = a;

            NotifySlotChanged(fromIndex);
            NotifySlotChanged(toIndex);
            OnInventoryChanged?.Invoke();
            return true;
        }

        public bool SplitStack(int fromIndex, int toIndex, int splitCount = -1)
        {
            if (fromIndex < 0 || fromIndex >= TOTAL_SLOTS || toIndex < 0 || toIndex >= TOTAL_SLOTS) return false;
            var source = _slots[fromIndex];
            if (source == null || source.Count <= 1) return false;

            int countToSplit = (splitCount > 0 && splitCount < source.Count)
                ? splitCount
                : (source.Count + 1) / 2;

            var dest = _slots[toIndex];
            if (dest == null)
            {
                _slots[toIndex] = source.Clone(countToSplit);
                source.Count -= countToSplit;
                NotifySlotChanged(fromIndex);
                NotifySlotChanged(toIndex);
                OnInventoryChanged?.Invoke();
                return true;
            }
            else if (dest.CanStackWith(source))
            {
                int space = dest.MaxStack - dest.Count;
                if (space > 0)
                {
                    int take = Mathf.Min(space, countToSplit);
                    dest.Count += take;
                    source.Count -= take;
                    if (source.Count <= 0) _slots[fromIndex] = null;
                    NotifySlotChanged(fromIndex);
                    NotifySlotChanged(toIndex);
                    OnInventoryChanged?.Invoke();
                    return true;
                }
            }

            return false;
        }

        public InventoryItemInstance DropItem(int slotIndex, int count = -1)
        {
            if (slotIndex < 0 || slotIndex >= TOTAL_SLOTS) return null;
            var item = _slots[slotIndex];
            if (item == null) return null;

            InventoryItemInstance dropped;
            if (count > 0 && count < item.Count)
            {
                dropped = item.Clone(count);
                item.Count -= count;
                NotifySlotChanged(slotIndex);
            }
            else
            {
                dropped = item;
                _slots[slotIndex] = null;
                NotifySlotChanged(slotIndex);
            }

            OnInventoryChanged?.Invoke();
            return dropped;
        }

        public void TrashItem(int slotIndex)
        {
            if (slotIndex < 0 || slotIndex >= TOTAL_SLOTS) return;
            _slots[slotIndex] = null;
            NotifySlotChanged(slotIndex);
            OnInventoryChanged?.Invoke();
        }

        // --- Auto-Sort & Gap Compaction ---

        public void Organize(bool includeHotbar = true)
        {
            int startIdx = includeHotbar ? 0 : HOTBAR_SLOTS;
            int count = TOTAL_SLOTS - startIdx;

            var compacted = new List<InventoryItemInstance>();
            for (int i = startIdx; i < TOTAL_SLOTS; i++)
            {
                var s = _slots[i];
                if (s == null || s.Count <= 0) continue;

                bool merged = false;
                for (int c = 0; c < compacted.Count; c++)
                {
                    var existing = compacted[c];
                    if (existing.CanStackWith(s))
                    {
                        int space = existing.MaxStack - existing.Count;
                        if (space > 0)
                        {
                            int take = Mathf.Min(space, s.Count);
                            existing.Count += take;
                            s.Count -= take;
                            if (s.Count <= 0)
                            {
                                merged = true;
                                break;
                            }
                        }
                    }
                }

                if (!merged && s.Count > 0)
                {
                    compacted.Add(s);
                }
            }

            for (int i = 0; i < count; i++)
            {
                int targetIdx = startIdx + i;
                _slots[targetIdx] = (i < compacted.Count) ? compacted[i] : null;
                NotifySlotChanged(targetIdx);
            }

            OnInventoryChanged?.Invoke();
        }

        public void AutoSort(InventorySortType type, bool includeHotbar = false)
        {
            // First compact
            Organize(includeHotbar);

            int startIdx = includeHotbar ? 0 : HOTBAR_SLOTS;
            var list = new List<InventoryItemInstance>();
            for (int i = startIdx; i < TOTAL_SLOTS; i++)
            {
                if (_slots[i] != null) list.Add(_slots[i]);
            }

            list.Sort((a, b) =>
            {
                if (a == null && b == null) return 0;
                if (a == null) return 1;
                if (b == null) return -1;

                switch (type)
                {
                    case InventorySortType.Category:
                        int catComp = a.Category.CompareTo(b.Category);
                        if (catComp != 0) return catComp;
                        int rarComp = b.Rarity.CompareTo(a.Rarity); // higher rarity first
                        if (rarComp != 0) return rarComp;
                        return string.Compare(a.ItemName, b.ItemName, StringComparison.OrdinalIgnoreCase);

                    case InventorySortType.Rarity:
                        int rComp = b.Rarity.CompareTo(a.Rarity); // highest first
                        if (rComp != 0) return rComp;
                        return string.Compare(a.ItemName, b.ItemName, StringComparison.OrdinalIgnoreCase);

                    case InventorySortType.Name:
                    default:
                        return string.Compare(a.ItemName, b.ItemName, StringComparison.OrdinalIgnoreCase);
                }
            });

            for (int i = 0; i < (TOTAL_SLOTS - startIdx); i++)
            {
                int targetIdx = startIdx + i;
                _slots[targetIdx] = (i < list.Count) ? list[i] : null;
                NotifySlotChanged(targetIdx);
            }

            OnInventoryChanged?.Invoke();
        }

        public void SortByCategory(bool includeHotbar = false) => AutoSort(InventorySortType.Category, includeHotbar);
        public void SortByRarity(bool includeHotbar = false) => AutoSort(InventorySortType.Rarity, includeHotbar);
        public void SortByName(bool includeHotbar = false) => AutoSort(InventorySortType.Name, includeHotbar);

        private void NotifySlotChanged(int slotIndex)
        {
            OnSlotChanged?.Invoke(slotIndex);

            // Sync with HUD Hotbar if in slots 0..9
            if (slotIndex >= 0 && slotIndex < HOTBAR_SLOTS)
            {
                var targetHud = Hud;
                if (targetHud != null)
                {
                    var item = _slots[slotIndex];
                    if (item != null && item.ItemData != null)
                    {
                        targetHud.SetItem(slotIndex, item.ItemId, item.ItemName, item.Icon, item.Count);
                    }
                    else
                    {
                        targetHud.ClearItem(slotIndex);
                    }
                }
            }
        }
    }
}
