using System.Collections.Generic;
using UnityEngine;

namespace Potaria.RPG
{
    /// <summary>
    /// Provisional meal buff contribution caps from Section 6.4 of the Potaria game balance plan.
    /// Prevents excessive stacking across food categories.
    /// </summary>
    public static class MealBuffCaps
    {
        public const float MaxDamageMult = 0.12f;
        public const float MaxRangedDamageMult = 0.12f;
        public const float MaxAtkSpeedMult = 0.10f;
        public const float MaxCritChance = 6.0f; // 6% or 0.06
        public const float MaxCritDmgMult = 0.16f;
        public const float MaxArmorPen = 0.10f;
        public const int MaxFlatDefense = 6;
        public const float MaxDamageReduction = 0.06f;
        public const float MaxMagicRes = 0.15f;
        public const float MaxSpeedMult = 0.15f;
        public const float MaxJumpMult = 0.15f;
        public const float MaxDashMult = 0.15f;
        public const float MaxKnockbackRes = 0.15f;
        public const float MaxHpRegen = 2.0f;
        public const float MaxMpRegen = 2.0f;
        public const float MaxManaCostReduction = 0.15f;

        public static float ClampStat(string statName, float value)
        {
            return statName switch
            {
                "damage_mult" => Mathf.Clamp(value, -MaxDamageMult, MaxDamageMult),
                "ranged_damage_mult" => Mathf.Clamp(value, -MaxRangedDamageMult, MaxRangedDamageMult),
                "atk_speed_mult" => Mathf.Clamp(value, -MaxAtkSpeedMult, MaxAtkSpeedMult),
                "crit_chance" => Mathf.Clamp(value, -MaxCritChance, MaxCritChance),
                "crit_dmg_mult" => Mathf.Clamp(value, -MaxCritDmgMult, MaxCritDmgMult),
                "armor_pen" => Mathf.Clamp(value, -MaxArmorPen, MaxArmorPen),
                "def" => Mathf.Clamp(value, -MaxFlatDefense, MaxFlatDefense),
                "dmg_reduction" => Mathf.Clamp(value, -MaxDamageReduction, MaxDamageReduction),
                "magic_res" => Mathf.Clamp(value, -MaxMagicRes, MaxMagicRes),
                "speed_mult" => Mathf.Clamp(value, -MaxSpeedMult, MaxSpeedMult),
                "jump_mult" => Mathf.Clamp(value, -MaxJumpMult, MaxJumpMult),
                "dash_mult" => Mathf.Clamp(value, -MaxDashMult, MaxDashMult),
                "knockback_res" => Mathf.Clamp(value, -MaxKnockbackRes, MaxKnockbackRes),
                "hp_regen" => Mathf.Clamp(value, 0f, MaxHpRegen),
                "mp_regen" => Mathf.Clamp(value, 0f, MaxMpRegen),
                "mana_cost_reduction" => Mathf.Clamp(value, -MaxManaCostReduction, MaxManaCostReduction),
                _ => value
            };
        }
    }
}
