using System;
using UnityEngine;

namespace Potaria.Data
{
    /// <summary>
    /// Stat modifiers and metadata associated with a cooked food meal buff.
    /// Conforms to the 5-buff category system (Offense, Defense, Mobility, Resource, Utility).
    /// </summary>
    [Serializable]
    public class FoodBuffData
    {
        [SerializeField] private BuffCategory category = BuffCategory.None;
        [SerializeField] private string buffName = string.Empty;
        [SerializeField] private float durationSeconds = 180f;

        [Header("Offensive Stat Modifiers")]
        [SerializeField] private float damageMultiplier = 0.0f;     // e.g. 0.06 for +6%
        [SerializeField] private float rangedDamageMultiplier = 0.0f;
        [SerializeField] private float attackSpeedMultiplier = 0.0f;
        [SerializeField] private float critChanceBonus = 0.0f;       // e.g. 3.0 for +3%
        [SerializeField] private float critDamageMultiplier = 0.0f;  // e.g. 0.08 for +8%

        [Header("Defensive Stat Modifiers")]
        [SerializeField] private float damageReduction = 0.0f;       // e.g. 0.04 for +4% reduction
        [SerializeField] private int flatDefense = 0;
        [SerializeField] private float magicResistance = 0.0f;
        [SerializeField] private float knockbackResistance = 0.0f;

        [Header("Mobility Stat Modifiers")]
        [SerializeField] private float speedMultiplier = 0.0f;        // e.g. 0.08 for +8%
        [SerializeField] private float jumpForceMultiplier = 0.0f;

        [Header("Resource Stat Modifiers")]
        [SerializeField] private float healthRegenPerSecond = 0.0f;  // e.g. 1.0 for +1 HP/s
        [SerializeField] private float manaRegenPerSecond = 0.0f;
        [SerializeField] private float manaCostReduction = 0.0f;

        [Header("Display Text")]
        [SerializeField] private string effectsDescription = string.Empty;

        // Properties
        public BuffCategory Category => category;
        public string BuffName => buffName;
        public float DurationSeconds => durationSeconds;
        public float DamageMultiplier => damageMultiplier;
        public float RangedDamageMultiplier => rangedDamageMultiplier;
        public float AttackSpeedMultiplier => attackSpeedMultiplier;
        public float CritChanceBonus => critChanceBonus;
        public float CritDamageMultiplier => critDamageMultiplier;
        public float DamageReduction => damageReduction;
        public int FlatDefense => flatDefense;
        public float MagicResistance => magicResistance;
        public float KnockbackResistance => knockbackResistance;
        public float SpeedMultiplier => speedMultiplier;
        public float JumpForceMultiplier => jumpForceMultiplier;
        public float HealthRegenPerSecond => healthRegenPerSecond;
        public float ManaRegenPerSecond => manaRegenPerSecond;
        public float ManaCostReduction => manaCostReduction;
        public string EffectsDescription => effectsDescription;

        public FoodBuffData() { }

        public FoodBuffData(BuffCategory category, string buffName, float durationSeconds)
        {
            this.category = category;
            this.buffName = buffName;
            this.durationSeconds = durationSeconds;
        }

        public void SetModifiers(
            float damageMult = 0f, float rangedMult = 0f, float atkSpdMult = 0f,
            float critChance = 0f, float critDmgMult = 0f, float dmgRed = 0f,
            int flatDef = 0, float magicRes = 0f, float knockbackRes = 0f,
            float spdMult = 0f, float jumpMult = 0f,
            float hpRegen = 0f, float mpRegen = 0f, float manaCostRed = 0f,
            string desc = "")
        {
            damageMultiplier = damageMult;
            rangedDamageMultiplier = rangedMult;
            attackSpeedMultiplier = atkSpdMult;
            critChanceBonus = critChance;
            critDamageMultiplier = critDmgMult;
            damageReduction = dmgRed;
            flatDefense = flatDef;
            magicResistance = magicRes;
            knockbackResistance = knockbackRes;
            speedMultiplier = spdMult;
            jumpForceMultiplier = jumpMult;
            healthRegenPerSecond = hpRegen;
            manaRegenPerSecond = mpRegen;
            manaCostReduction = manaCostRed;
            effectsDescription = desc;
        }
    }
}
