using System;
using System.Collections.Generic;
using UnityEngine;

namespace Potaria.Data
{
    /// <summary>
    /// Runtime instance of an item in a slot (Inventory, Equipment, Chest, Forge).
    /// Tracks stack count, enhancement level (+0 to +7), durability / broken state,
    /// and affix sockets / carved affixes.
    /// </summary>
    [Serializable]
    public class InventoryItemInstance
    {
        [SerializeField] private ItemData itemData;
        [SerializeField] private int count = 1;
        [SerializeField] private int enhancementLevel = 0;
        [SerializeField] private bool isBroken = false;
        [SerializeField] private int affixSlots = 0;
        [SerializeField] private List<string> affixes = new List<string>();
        [SerializeField] private List<string> removedStats = new List<string>();
        [SerializeField] private int additionalAffixSlots = 0;

        public ItemData ItemData { get => itemData; set => itemData = value; }
        public int Count { get => count; set => count = value; }
        public int EnhancementLevel
        {
            get => enhancementLevel;
            set => enhancementLevel = Mathf.Clamp(value, 0, 7);
        }
        public bool IsBroken { get => isBroken; set => isBroken = value; }
        public int AffixSlots { get => affixSlots; set => affixSlots = Mathf.Max(0, value); }
        public List<string> Affixes => affixes;
        public List<string> RemovedStats => removedStats;
        public int AdditionalAffixSlots { get => additionalAffixSlots; set => additionalAffixSlots = value; }

        public string ItemId => itemData != null ? itemData.ItemId : string.Empty;
        public string ItemName
        {
            get
            {
                if (itemData == null) return string.Empty;
                string name = itemData.ItemName;
                if (enhancementLevel > 0) name += $" +{enhancementLevel}";
                if (isBroken) name = $"[BROKEN] {name}";
                return name;
            }
        }
        public int MaxStack => itemData != null ? itemData.MaxStack : 999;
        public Sprite Icon => itemData != null ? itemData.Icon : null;
        public ItemRarity Rarity => itemData != null ? itemData.Rarity : ItemRarity.Common;
        public ItemCategory Category => itemData != null ? itemData.Category : ItemCategory.Material;

        public InventoryItemInstance() { }

        public InventoryItemInstance(ItemData data, int count = 1, int enhancement = 0, bool broken = false)
        {
            this.itemData = data;
            this.count = count;
            this.enhancementLevel = enhancement;
            this.isBroken = broken;
            if (data is EquipmentItemData equip)
            {
                this.affixSlots = equip.AffixSlots;
            }
            else if (data is WeaponItemData wep)
            {
                this.affixSlots = wep.AffixSlots;
            }
        }

        public InventoryItemInstance Clone(int newCount = -1)
        {
            var clone = new InventoryItemInstance
            {
                itemData = this.itemData,
                count = (newCount > 0) ? newCount : this.count,
                enhancementLevel = this.enhancementLevel,
                isBroken = this.isBroken,
                affixSlots = this.affixSlots,
                additionalAffixSlots = this.additionalAffixSlots,
                affixes = new List<string>(this.affixes),
                removedStats = new List<string>(this.removedStats)
            };
            return clone;
        }

        public bool CanStackWith(InventoryItemInstance other)
        {
            if (other == null || other.itemData != this.itemData) return false;
            if (this.enhancementLevel != other.enhancementLevel) return false;
            if (this.isBroken != other.isBroken) return false;
            if (this.affixSlots != other.affixSlots) return false;
            if (this.additionalAffixSlots != other.additionalAffixSlots) return false;
            if (this.affixes.Count != other.affixes.Count) return false;
            for (int i = 0; i < this.affixes.Count; i++)
            {
                if (this.affixes[i] != other.affixes[i]) return false;
            }
            return true;
        }

        public float GetEnhancementMultiplier()
        {
            return 1.0f + (enhancementLevel / 7.0f);
        }

        public int GetEffectiveAttack()
        {
            if (isBroken || itemData == null) return 0;
            int baseAtk = 0;
            if (itemData is WeaponItemData wep) baseAtk = wep.Attack;
            else if (itemData is EquipmentItemData eq) baseAtk = eq.Attack;

            int atk = Mathf.RoundToInt(baseAtk * GetEnhancementMultiplier());
            if (affixes != null)
            {
                if (affixes.Contains("Titan's Might")) atk += 15;
                if (affixes.Contains("Solar Flare")) atk += 10;
                if (affixes.Contains("Void Singularity")) atk += 12;
                if (affixes.Contains("Frostbite Cryo")) atk += 8;
            }
            return atk;
        }

        public int GetEffectiveDefense()
        {
            if (isBroken || itemData == null) return 0;
            int baseDef = 0;
            if (itemData is EquipmentItemData eq) baseDef = eq.Defense;
            else if (itemData is WeaponItemData wep) baseDef = wep.Defense;

            int def = Mathf.RoundToInt(baseDef * GetEnhancementMultiplier());
            if (affixes != null && affixes.Contains("Celestial Aegis")) def += 15;
            return def;
        }

        public int GetEffectiveBonusHp()
        {
            if (isBroken || itemData == null) return 0;
            int baseHp = 0;
            if (itemData is EquipmentItemData eq) baseHp = eq.BonusHp;
            else if (itemData is WeaponItemData wep) baseHp = wep.BonusHp;

            int hp = Mathf.RoundToInt(baseHp * GetEnhancementMultiplier());
            if (affixes != null && affixes.Contains("Celestial Aegis")) hp += 50;
            return hp;
        }

        public int GetEffectiveBonusMp()
        {
            if (isBroken || itemData == null) return 0;
            int baseMp = 0;
            if (itemData is EquipmentItemData eq) baseMp = eq.BonusMp;
            else if (itemData is WeaponItemData wep) baseMp = wep.BonusMp;

            int mp = Mathf.RoundToInt(baseMp * GetEnhancementMultiplier());
            if (affixes != null && affixes.Contains("Astral Omniscience")) mp += 50;
            return mp;
        }

        public float GetEffectiveCrit()
        {
            if (isBroken || itemData == null) return 0f;
            float baseCrit = 0f;
            if (itemData is WeaponItemData wep) baseCrit = wep.CritChance;
            else if (itemData is EquipmentItemData eq) baseCrit = eq.CritChance;
            return baseCrit * GetEnhancementMultiplier();
        }

        public float GetEffectiveSpeed()
        {
            if (isBroken || itemData == null) return 0f;
            float baseSpd = 0f;
            if (itemData is EquipmentItemData eq) baseSpd = eq.Speed;
            else if (itemData is WeaponItemData wep) baseSpd = wep.Speed;

            float spd = baseSpd * GetEnhancementMultiplier();
            if (affixes != null && affixes.Contains("Chronos Velocity")) spd += 0.30f;
            return spd;
        }

        public float GetEffectiveAtkSpeed()
        {
            if (isBroken || itemData == null) return 0f;
            float spd = 0f;
            if (affixes != null && affixes.Contains("Chronos Velocity")) spd += 0.30f;
            return spd;
        }

        public float GetEffectiveMpRegen()
        {
            if (isBroken || itemData == null) return 0f;
            float baseRegen = 0f;
            if (itemData is EquipmentItemData eq) baseRegen = eq.MpRegen;
            else if (itemData is WeaponItemData wep) baseRegen = wep.MpRegen;
            return baseRegen * GetEnhancementMultiplier();
        }

        public float GetEffectiveDamageReduction()
        {
            if (isBroken || itemData == null) return 0f;
            return 0f;
        }
    }
}
