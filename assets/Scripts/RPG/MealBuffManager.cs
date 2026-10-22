using System;
using System.Collections.Generic;
using UnityEngine;
using Potaria.Data;

namespace Potaria.RPG
{
    /// <summary>
    /// Represents an active meal buff instance within one of the 5 categories.
    /// </summary>
    [Serializable]
    public class ActiveMealBuff
    {
        public BuffCategory Category;
        public string BuffName;
        public string SourceItemId;
        public float RemainingDuration;
        public float MaxDuration;
        public FoodBuffData BuffData;

        public ActiveMealBuff(FoodBuffData data, string sourceItemId = "")
        {
            Category = data.Category;
            BuffName = data.BuffName;
            SourceItemId = sourceItemId;
            RemainingDuration = data.DurationSeconds;
            MaxDuration = data.DurationSeconds;
            BuffData = data;
        }
    }

    /// <summary>
    /// Manages the 5-category active food meal buff slots (Offense, Defense, Mobility, Resource, Utility).
    /// Strictly 1 active buff per category; consuming another meal in the same category replaces it.
    /// </summary>
    public class MealBuffManager
    {
        private readonly Dictionary<BuffCategory, ActiveMealBuff> _activeBuffs = new Dictionary<BuffCategory, ActiveMealBuff>();

        public IReadOnlyDictionary<BuffCategory, ActiveMealBuff> ActiveBuffs => _activeBuffs;

        public event Action<ActiveMealBuff> OnBuffApplied;
        public event Action<BuffCategory> OnBuffExpired;

        /// <summary>
        /// Consumes a food item and applies its buff. Returns true if a valid meal buff was applied.
        /// </summary>
        public bool ConsumeFood(FoodBuffData buffData, string sourceItemId = "")
        {
            if (buffData == null || buffData.Category == BuffCategory.None)
                return false;

            var category = buffData.Category;
            var newBuff = new ActiveMealBuff(buffData, sourceItemId);
            _activeBuffs[category] = newBuff;
            OnBuffApplied?.Invoke(newBuff);
            return true;
        }

        public void ClearBuff(BuffCategory category)
        {
            if (_activeBuffs.Remove(category))
            {
                OnBuffExpired?.Invoke(category);
            }
        }

        public void ClearAll()
        {
            var keys = new List<BuffCategory>(_activeBuffs.Keys);
            _activeBuffs.Clear();
            foreach (var key in keys)
            {
                OnBuffExpired?.Invoke(key);
            }
        }

        public void Update(float dt)
        {
            if (_activeBuffs.Count == 0) return;

            var expired = new List<BuffCategory>();
            foreach (var kvp in _activeBuffs)
            {
                kvp.Value.RemainingDuration -= dt;
                if (kvp.Value.RemainingDuration <= 0f)
                {
                    expired.Add(kvp.Key);
                }
            }

            foreach (var cat in expired)
            {
                _activeBuffs.Remove(cat);
                OnBuffExpired?.Invoke(cat);
            }
        }

        public bool HasBuff(BuffCategory category)
        {
            return _activeBuffs.ContainsKey(category);
        }

        public ActiveMealBuff GetBuff(BuffCategory category)
        {
            _activeBuffs.TryGetValue(category, out var buff);
            return buff;
        }

        // --- Clamped Stat Accumulators ---

        public float GetDamageMultiplier()
        {
            float total = 0f;
            foreach (var b in _activeBuffs.Values) total += b.BuffData.DamageMultiplier;
            return MealBuffCaps.ClampStat("damage_mult", total);
        }

        public float GetRangedDamageMultiplier()
        {
            float total = 0f;
            foreach (var b in _activeBuffs.Values) total += b.BuffData.RangedDamageMultiplier;
            return MealBuffCaps.ClampStat("ranged_damage_mult", total);
        }

        public float GetAttackSpeedMultiplier()
        {
            float total = 0f;
            foreach (var b in _activeBuffs.Values) total += b.BuffData.AttackSpeedMultiplier;
            return MealBuffCaps.ClampStat("atk_speed_mult", total);
        }

        public float GetCritChanceBonus()
        {
            float total = 0f;
            foreach (var b in _activeBuffs.Values) total += b.BuffData.CritChanceBonus;
            return MealBuffCaps.ClampStat("crit_chance", total);
        }

        public float GetCritDamageMultiplier()
        {
            float total = 0f;
            foreach (var b in _activeBuffs.Values) total += b.BuffData.CritDamageMultiplier;
            return MealBuffCaps.ClampStat("crit_dmg_mult", total);
        }

        public int GetFlatDefense()
        {
            int total = 0;
            foreach (var b in _activeBuffs.Values) total += b.BuffData.FlatDefense;
            return Mathf.RoundToInt(MealBuffCaps.ClampStat("def", total));
        }

        public float GetDamageReduction()
        {
            float total = 0f;
            foreach (var b in _activeBuffs.Values) total += b.BuffData.DamageReduction;
            return MealBuffCaps.ClampStat("dmg_reduction", total);
        }

        public float GetMagicResistance()
        {
            float total = 0f;
            foreach (var b in _activeBuffs.Values) total += b.BuffData.MagicResistance;
            return MealBuffCaps.ClampStat("magic_res", total);
        }

        public float GetKnockbackResistance()
        {
            float total = 0f;
            foreach (var b in _activeBuffs.Values) total += b.BuffData.KnockbackResistance;
            return MealBuffCaps.ClampStat("knockback_res", total);
        }

        public float GetSpeedMultiplier()
        {
            float total = 0f;
            foreach (var b in _activeBuffs.Values) total += b.BuffData.SpeedMultiplier;
            return MealBuffCaps.ClampStat("speed_mult", total);
        }

        public float GetJumpForceMultiplier()
        {
            float total = 0f;
            foreach (var b in _activeBuffs.Values) total += b.BuffData.JumpForceMultiplier;
            return MealBuffCaps.ClampStat("jump_mult", total);
        }

        public float GetHealthRegenPerSecond()
        {
            float total = 0f;
            foreach (var b in _activeBuffs.Values) total += b.BuffData.HealthRegenPerSecond;
            return MealBuffCaps.ClampStat("hp_regen", total);
        }

        public float GetManaRegenPerSecond()
        {
            float total = 0f;
            foreach (var b in _activeBuffs.Values) total += b.BuffData.ManaRegenPerSecond;
            return MealBuffCaps.ClampStat("mp_regen", total);
        }

        public float GetManaCostReduction()
        {
            float total = 0f;
            foreach (var b in _activeBuffs.Values) total += b.BuffData.ManaCostReduction;
            return MealBuffCaps.ClampStat("mana_cost_reduction", total);
        }
    }
}
