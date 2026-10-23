using System;
using System.Collections.Generic;
using UnityEngine;
using Potaria.Data;

namespace Potaria.RPG
{
    public enum PaperdollSlot
    {
        Head = 0,
        Chest = 1,
        Legs = 2,
        Weapon = 3,
        Accessory1 = 4,
        Accessory2 = 5,
        Accessory3 = 6,
        Accessory4 = 7,
        Accessory5 = 8,
        Accessory6 = 9
    }

    [Serializable]
    public class ActiveSetBonusInfo
    {
        public EquipmentSetData SetData;
        public int EquippedCount;
        public List<SetBonusThreshold> UnlockedThresholds = new List<SetBonusThreshold>();
    }

    /// <summary>
    /// Manages the 10-slot Chroisen-style Paperdoll Equipment system:
    /// - Head, Chest, Legs, Weapon, and 6 Accessory slots.
    /// - Immediate recalculation of PlayerStats (HP, MP, ATK, DEF, Damage Reduction, Speed, Crit Chance, Crit Damage).
    /// - 27 Progressive Equipment Set bonuses (2-piece, 4-piece, and 5-piece milestones).
    /// </summary>
    public class PlayerEquipment : MonoBehaviour
    {
        public const int TOTAL_EQUIP_SLOTS = 10;

        [Header("References")]
        [SerializeField] private PlayerStats stats;
        [SerializeField] private PlayerInventory inventory;

        private readonly InventoryItemInstance[] _equippedSlots = new InventoryItemInstance[TOTAL_EQUIP_SLOTS];
        private readonly List<ActiveSetBonusInfo> _activeSetBonuses = new List<ActiveSetBonusInfo>();

        public event Action OnEquipmentChanged;

        public PlayerStats Stats { get => stats; set => stats = value; }
        public PlayerInventory Inventory { get => inventory; set => inventory = value; }
        public List<ActiveSetBonusInfo> ActiveSetBonuses => _activeSetBonuses;

        private void Awake()
        {
            if (stats == null) stats = GetComponent<PlayerStats>();
            if (inventory == null) inventory = GetComponent<PlayerInventory>();
        }

        public InventoryItemInstance GetEquipped(int slotIndex)
        {
            if (slotIndex < 0 || slotIndex >= TOTAL_EQUIP_SLOTS) return null;
            return _equippedSlots[slotIndex];
        }

        public InventoryItemInstance GetEquipped(PaperdollSlot slot) => GetEquipped((int)slot);

        public bool CanEquipInSlot(InventoryItemInstance item, int slotIndex)
        {
            if (item == null || item.ItemData == null) return false;
            if (slotIndex < 0 || slotIndex >= TOTAL_EQUIP_SLOTS) return false;

            var data = item.ItemData;
            var paperdollSlot = (PaperdollSlot)slotIndex;

            switch (paperdollSlot)
            {
                case PaperdollSlot.Head:
                    if (data is EquipmentItemData eqHead)
                        return eqHead.EquipSlot == EquipSlot.Helmet;
                    if (data.Category == ItemCategory.Armor_Head) return true;
                    if (data.Category == ItemCategory.Armor)
                    {
                        string id = (data.ItemId ?? "").ToLowerInvariant();
                        return id.Contains("helm") || id.Contains("hat") || id.Contains("cap") || id.Contains("head") || id.Contains("mask") || id.Contains("hood");
                    }
                    return false;

                case PaperdollSlot.Chest:
                    if (data is EquipmentItemData eqChest)
                        return eqChest.EquipSlot == EquipSlot.Chestplate;
                    if (data.Category == ItemCategory.Armor_Chest) return true;
                    if (data.Category == ItemCategory.Armor)
                    {
                        string id = (data.ItemId ?? "").ToLowerInvariant();
                        return id.Contains("chest") || id.Contains("plate") || id.Contains("tunic") || id.Contains("robe") || id.Contains("cuirass") || id.Contains("barong") || id.Contains("mail") || id.Contains("armor") || id.Contains("vest");
                    }
                    return false;

                case PaperdollSlot.Legs:
                    if (data is EquipmentItemData eqLegs)
                        return eqLegs.EquipSlot == EquipSlot.Greaves || eqLegs.EquipSlot == EquipSlot.Boots;
                    if (data.Category == ItemCategory.Armor_Legs) return true;
                    if (data.Category == ItemCategory.Armor)
                    {
                        string id = (data.ItemId ?? "").ToLowerInvariant();
                        return id.Contains("leg") || id.Contains("boot") || id.Contains("pant") || id.Contains("greave") || id.Contains("trouser") || id.Contains("shoe");
                    }
                    return false;

                case PaperdollSlot.Weapon:
                    return data is WeaponItemData || data.Category == ItemCategory.Weapon || data.Category == ItemCategory.Tool;

                case PaperdollSlot.Accessory1:
                case PaperdollSlot.Accessory2:
                case PaperdollSlot.Accessory3:
                case PaperdollSlot.Accessory4:
                case PaperdollSlot.Accessory5:
                case PaperdollSlot.Accessory6:
                    if (data is EquipmentItemData eqAcc)
                        return eqAcc.EquipSlot == EquipSlot.Accessory || eqAcc.EquipSlot == EquipSlot.Ring || eqAcc.EquipSlot == EquipSlot.Amulet;
                    return data.Category == ItemCategory.Accessory;

                default:
                    return false;
            }
        }

        public int GetMatchingSlot(InventoryItemInstance item)
        {
            if (item == null || item.ItemData == null) return -1;
            var data = item.ItemData;

            if (data is WeaponItemData || data.Category == ItemCategory.Weapon || data.Category == ItemCategory.Tool)
            {
                return (int)PaperdollSlot.Weapon;
            }

            if (data is EquipmentItemData eq)
            {
                switch (eq.EquipSlot)
                {
                    case EquipSlot.Helmet:
                        return (int)PaperdollSlot.Head;
                    case EquipSlot.Chestplate:
                        return (int)PaperdollSlot.Chest;
                    case EquipSlot.Greaves:
                    case EquipSlot.Boots:
                        return (int)PaperdollSlot.Legs;
                    case EquipSlot.Accessory:
                    case EquipSlot.Ring:
                    case EquipSlot.Amulet:
                        // Find first empty accessory slot, or default to Accessory1
                        for (int i = (int)PaperdollSlot.Accessory1; i <= (int)PaperdollSlot.Accessory6; i++)
                        {
                            if (_equippedSlots[i] == null) return i;
                        }
                        return (int)PaperdollSlot.Accessory1;
                }
            }

            if (data.Category == ItemCategory.Armor_Head) return (int)PaperdollSlot.Head;
            if (data.Category == ItemCategory.Armor_Chest) return (int)PaperdollSlot.Chest;
            if (data.Category == ItemCategory.Armor_Legs) return (int)PaperdollSlot.Legs;
            if (data.Category == ItemCategory.Armor)
            {
                string id = (data.ItemId ?? "").ToLowerInvariant();
                if (id.Contains("helm") || id.Contains("hat") || id.Contains("cap") || id.Contains("head") || id.Contains("mask") || id.Contains("hood"))
                    return (int)PaperdollSlot.Head;
                if (id.Contains("leg") || id.Contains("boot") || id.Contains("pant") || id.Contains("greave") || id.Contains("trouser") || id.Contains("shoe"))
                    return (int)PaperdollSlot.Legs;
                return (int)PaperdollSlot.Chest;
            }
            if (data.Category == ItemCategory.Accessory) return (int)PaperdollSlot.Accessory1;

            return -1;
        }

        public bool EquipItem(InventoryItemInstance item, int targetSlot = -1, PlayerInventory returnInventory = null)
        {
            if (item == null || item.ItemData == null) return false;

            if (targetSlot < 0)
            {
                targetSlot = GetMatchingSlot(item);
                if (targetSlot < 0) return false;
            }

            if (!CanEquipInSlot(item, targetSlot)) return false;

            var oldItem = _equippedSlots[targetSlot];

            if (oldItem != null && returnInventory != null)
            {
                if (!returnInventory.AddItem(oldItem))
                {
                    if (returnInventory.HeldItem == null)
                    {
                        returnInventory.HeldItem = oldItem;
                    }
                    else
                    {
                        // Cannot safely return old item without loss
                        return false;
                    }
                }
            }

            _equippedSlots[targetSlot] = item.Clone(1);

            RecalculateStats();
            OnEquipmentChanged?.Invoke();
            return true;
        }

        public InventoryItemInstance UnequipItem(int slotIndex, PlayerInventory returnInventory = null)
        {
            if (slotIndex < 0 || slotIndex >= TOTAL_EQUIP_SLOTS) return null;
            var unequipped = _equippedSlots[slotIndex];
            if (unequipped == null) return null;

            if (returnInventory != null)
            {
                if (!returnInventory.AddItem(unequipped))
                {
                    if (returnInventory.HeldItem == null)
                    {
                        returnInventory.HeldItem = unequipped;
                    }
                    else
                    {
                        // Cannot unequip: inventory is completely full and cursor is occupied
                        return null;
                    }
                }
            }

            _equippedSlots[slotIndex] = null;

            RecalculateStats();
            OnEquipmentChanged?.Invoke();
            return unequipped;
        }

        public void RecalculateStats()
        {
            if (stats == null) stats = GetComponent<PlayerStats>();
            if (stats == null) return;

            int bonusHp = 0;
            int bonusMp = 0;
            int rawAtk = 0;
            int rawDef = 0;
            float rawCrit = 0f;
            float rawSpeed = 0f;
            float rawAtkSpd = 0f;
            float rawMpRegen = 0f;
            float rawDmgRed = 0f;
            float rawCritDmg = 0f;

            // 1. Gather raw stats from all 10 equipped slots
            var equippedItemIds = new List<string>();
            for (int i = 0; i < TOTAL_EQUIP_SLOTS; i++)
            {
                var piece = _equippedSlots[i];
                if (piece == null || piece.IsBroken) continue;

                equippedItemIds.Add(piece.ItemId);

                rawAtk += piece.GetEffectiveAttack();
                rawDef += piece.GetEffectiveDefense();
                bonusHp += piece.GetEffectiveBonusHp();
                bonusMp += piece.GetEffectiveBonusMp();
                rawCrit += piece.GetEffectiveCrit();
                rawSpeed += piece.GetEffectiveSpeed();
                rawAtkSpd += piece.GetEffectiveAtkSpeed();
                rawMpRegen += piece.GetEffectiveMpRegen();
                rawDmgRed += piece.GetEffectiveDamageReduction();
                rawCritDmg += piece.GetEffectiveCritDamage();
            }

            // 2. Check 27 Equipment Sets and apply threshold synergies (2-pc, 4-pc, 5-pc)
            _activeSetBonuses.Clear();
            float setAtkMult = 0f;
            float setDefMult = 0f;

            var allSets = ItemDatabase.Instance.GetAllEquipmentSets();
            foreach (var set in allSets)
            {
                if (set == null) continue;

                int matchingCount = 0;
                foreach (var pieceId in set.PieceItemIds)
                {
                    if (equippedItemIds.Contains(pieceId))
                    {
                        matchingCount++;
                    }
                }

                if (matchingCount >= 2)
                {
                    var activeThresholds = set.GetActiveThresholds(matchingCount);
                    if (activeThresholds.Count > 0)
                    {
                        _activeSetBonuses.Add(new ActiveSetBonusInfo
                        {
                            SetData = set,
                            EquippedCount = matchingCount,
                            UnlockedThresholds = activeThresholds
                        });

                        foreach (var threshold in activeThresholds)
                        {
                            setAtkMult += threshold.AtkMultiplier;
                            setDefMult += threshold.DefMultiplier;
                            bonusHp += threshold.BonusMaxHp;
                            rawSpeed += threshold.BonusSpeed;
                            rawCrit += threshold.BonusCritChance;
                            rawMpRegen += threshold.BonusMpRegen;
                            rawAtkSpd += threshold.BonusAtkSpeed;
                        }
                    }
                }
            }

            // Apply set multipliers to equipment ATK & DEF
            int finalAtk = Mathf.RoundToInt(rawAtk * (1f + setAtkMult));
            int finalDef = Mathf.RoundToInt(rawDef * (1f + setDefMult));

            stats.SetBonusStats(
                bonusHp,
                bonusMp,
                finalAtk,
                finalDef,
                rawCrit,
                rawSpeed,
                rawAtkSpd,
                rawMpRegen,
                rawDmgRed,
                rawCritDmg
            );
        }
    }
}
