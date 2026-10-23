using System;
using UnityEngine;
using Potaria.Data;

namespace Potaria.RPG
{
    /// <summary>
    /// Player RPG Stats System: 100-level progression curve (Level 1-100), EXP curves,
    /// Chroisen-style attributes (HP, MP, ATK, DEF, Crit Rate 5%, Crit Multiplier 180%, Speed),
    /// MP natural regen (1.8 MP/s) + bullet grazing reward (+1 MP),
    /// Defense mitigation formula (Damage Taken = max(1, Enemy ATK - Player DEF)),
    /// 5-active-meal buff slots (Offense, Defense, Mobility, Resource, Utility),
    /// and dedicated 3-tier coin purse.
    /// </summary>
    public class PlayerStats : CharacterStats
    {
        [Header("Level & Progression (1-100)")]
        [SerializeField] private int level = 1;
        [SerializeField] private int maxLevel = 100;
        [SerializeField] private int currentExp = 0;
        [SerializeField] private int expToNext = 100;

        [Header("Equipment Bonuses")]
        [SerializeField] private int bonusMaxHp = 0;
        [SerializeField] private int bonusMaxMp = 0;
        [SerializeField] private int bonusAtk = 0;
        [SerializeField] private int bonusDef = 0;
        [SerializeField] private float bonusCrit = 0f;
        [SerializeField] private float bonusSpeed = 0f;
        [SerializeField] private float bonusAtkSpeed = 0f;
        [SerializeField] private float bonusMpRegen = 0f;
        [SerializeField] private float bonusDamageReduction = 0f;
        [SerializeField] private float bonusCritDamage = 0f;

        [Header("Regeneration")]
        [SerializeField] private float baseMpRegen = 1.8f; // 1.8 MP/s baseline
        private float _mpFraction = 0f;
        private float _hpRegenTimer = 0f;

        [Header("Coin Purse (100c = 1s, 100s = 1g)")]
        [SerializeField] private int copperCoins = 0;
        [SerializeField] private int silverCoins = 0;
        [SerializeField] private int goldCoins = 0;

        // 5-Active-Meal Buff Slot Manager
        public MealBuffManager MealBuffs { get; } = new MealBuffManager();

        public int Level => level;
        public int MaxLevel => maxLevel;
        public int CurrentExp => currentExp;
        public int ExpToNext => expToNext;

        public int CopperCoins => copperCoins;
        public int SilverCoins => silverCoins;
        public int GoldCoins => goldCoins;
        public int TotalCopperValue => copperCoins + (silverCoins * 100) + (goldCoins * 10000);

        public event Action<int> OnLevelUp;
        public event Action<int, int> OnExpChanged; // (current, toNext)
        public event Action OnGrazeEvent;

        private void Awake()
        {
            ResetToBaseStats();
        }

        public void ResetToBaseStats()
        {
            level = 1;
            maxLevel = 100;
            currentExp = 0;
            expToNext = CalculateExpToNext(1);

            baseAtk = 10;
            baseDef = 2;
            baseCritRate = 5.0f;
            critMultiplier = 1.8f;
            baseMoveSpeed = 3.0f;
            baseAtkSpeed = 1.0f;
            baseMpRegen = 1.8f;

            maxHp = 100;
            currentHp = 100;
            maxMp = 50;
            currentMp = 50;

            bonusMaxHp = 0;
            bonusMaxMp = 0;
            bonusAtk = 0;
            bonusDef = 0;
            bonusCrit = 0f;
            bonusSpeed = 0f;
            bonusAtkSpeed = 0f;
            bonusMpRegen = 0f;
            bonusDamageReduction = 0f;
            bonusCritDamage = 0f;

            _mpFraction = 0f;
            _hpRegenTimer = 0f;
            MealBuffs.ClearAll();
        }

        // --- EXP & Level Progression (1 to 100) ---

        public static int CalculateExpToNext(int lvl)
        {
            return Mathf.Max(100, Mathf.FloorToInt(100f * Mathf.Pow(lvl, 2.1f)));
        }

        public bool GainExp(int amount)
        {
            if (amount <= 0 || level >= maxLevel) return false;

            currentExp += amount;
            bool leveledUp = false;

            while (currentExp >= expToNext && level < maxLevel)
            {
                currentExp -= expToNext;
                level++;
                leveledUp = true;

                // Level progression stat gains
                baseMaxHp += 15;
                baseMaxMp += 8;
                baseAtk += 3;
                baseDef += 1;

                // Every 5 levels: +1% base crit
                if (level % 5 == 0)
                {
                    baseCritRate += 1.0f;
                }

                expToNext = CalculateExpToNext(level);

                // Full heal upon level up
                CurrentHp = MaxHp;
                CurrentMp = MaxMp;

                OnLevelUp?.Invoke(level);
            }

            OnExpChanged?.Invoke(currentExp, expToNext);
            return leveledUp;
        }

        private int baseMaxHp = 100;
        private int baseMaxMp = 50;

        public override int MaxHp
        {
            get => baseMaxHp + bonusMaxHp;
            set
            {
                baseMaxHp = Mathf.Max(1, value - bonusMaxHp);
                currentHp = Mathf.Clamp(currentHp, 0, MaxHp);
            }
        }

        public override int MaxMp
        {
            get => baseMaxMp + bonusMaxMp;
            set
            {
                baseMaxMp = Mathf.Max(0, value - bonusMaxMp);
                currentMp = Mathf.Clamp(currentMp, 0, MaxMp);
            }
        }

        public override int TotalAtk
        {
            get
            {
                float mult = MealBuffs.GetDamageMultiplier();
                int raw = baseAtk + bonusAtk;
                return Mathf.Max(1, Mathf.RoundToInt(raw * (1f + mult)));
            }
        }

        public int TotalRangedAtk
        {
            get
            {
                float mult = MealBuffs.GetDamageMultiplier() + MealBuffs.GetRangedDamageMultiplier();
                int raw = baseAtk + bonusAtk;
                return Mathf.Max(1, Mathf.RoundToInt(raw * (1f + mult)));
            }
        }

        public override int TotalDef
        {
            get => baseDef + bonusDef + MealBuffs.GetFlatDefense();
        }

        public override float TotalCritRate
        {
            get => Mathf.Min(75.0f, baseCritRate + bonusCrit + MealBuffs.GetCritChanceBonus());
        }

        public float TotalCritMultiplier
        {
            get => critMultiplier + bonusCritDamage + MealBuffs.GetCritDamageMultiplier();
        }

        public float TotalDamageReduction
        {
            get => bonusDamageReduction + MealBuffs.GetDamageReduction();
        }

        public override float TotalMoveSpeed
        {
            get
            {
                float spdMult = MealBuffs.GetSpeedMultiplier();
                return (baseMoveSpeed + bonusSpeed) * (1f + spdMult);
            }
        }

        public override float TotalAtkSpeed
        {
            get
            {
                float atkSpd = MealBuffs.GetAttackSpeedMultiplier();
                return Mathf.Max(0.2f, (baseAtkSpeed + bonusAtkSpeed) * (1f + atkSpd));
            }
        }

        public float TotalMpRegen
        {
            get => baseMpRegen + bonusMpRegen + MealBuffs.GetManaRegenPerSecond();
        }

        // --- Bullet Grazing Mechanics ---

        /// <summary>
        /// Called when an enemy projectile enters player graze perimeter without hitting core hitbox.
        /// Rewards +1 MP directly!
        /// </summary>
        public void OnGraze()
        {
            RestoreMp(1);
            OnGrazeEvent?.Invoke();
        }

        // --- Natural Regeneration & Update Loop ---

        public void UpdateStats(float dt)
        {
            // 1. Update active food meal buffs
            MealBuffs.Update(dt);

            // 2. MP Natural Regeneration (1.8 MP/s base + equipment + meals)
            float totalMpRate = TotalMpRegen;
            if (totalMpRate > 0f && CurrentMp < MaxMp)
            {
                _mpFraction += totalMpRate * dt;
                if (_mpFraction >= 1.0f)
                {
                    int addMp = Mathf.FloorToInt(_mpFraction);
                    _mpFraction -= addMp;
                    RestoreMp(addMp);
                }
            }

            // 3. HP Regeneration from meal buffs
            float mealHpReg = MealBuffs.GetHealthRegenPerSecond();
            if (mealHpReg > 0f && CurrentHp < MaxHp)
            {
                _hpRegenTimer += dt;
                if (_hpRegenTimer >= 1.0f)
                {
                    _hpRegenTimer -= 1.0f;
                    Heal(Mathf.RoundToInt(mealHpReg));
                }
            }
        }

        private void Update()
        {
            UpdateStats(Time.deltaTime);
        }

        // --- Damage Calculation with Player Def & Buffs ---

        public override int TakeDamage(int incomingAtk, bool ignoreDef = false, float damageReduction = 0f, float magicRes = 0f, bool isMagic = false)
        {
            float totalDmgRed = damageReduction + TotalDamageReduction;
            float totalMagicRes = magicRes + MealBuffs.GetMagicResistance();
            return base.TakeDamage(incomingAtk, ignoreDef, totalDmgRed, totalMagicRes, isMagic);
        }

        // --- Coin Purse Denomination Logic ---

        public void AddCoins(int copper = 0, int silver = 0, int gold = 0)
        {
            int total = TotalCopperValue + copper + (silver * 100) + (gold * 10000);
            SetFromCopper(total);
        }

        public void SetFromCopper(int totalCopper)
        {
            totalCopper = Mathf.Max(0, totalCopper);
            goldCoins = totalCopper / 10000;
            int rem = totalCopper % 10000;
            silverCoins = rem / 100;
            copperCoins = rem % 100;
        }

        public bool RemoveCoins(int totalCopper)
        {
            if (TotalCopperValue >= totalCopper)
            {
                SetFromCopper(TotalCopperValue - totalCopper);
                return true;
            }
            return false;
        }

        // --- Equipment Link Hooks ---

        public void SetBonusStats(int hp, int mp, int atk, int def, float crit, float speed, float atkSpd, float mpRegen, float damageReduction = 0f, float critDamage = 0f)
        {
            bonusMaxHp = hp;
            bonusMaxMp = mp;
            bonusAtk = atk;
            bonusDef = def;
            bonusCrit = crit;
            bonusSpeed = speed;
            bonusAtkSpeed = atkSpd;
            bonusMpRegen = mpRegen;
            bonusDamageReduction = damageReduction;
            bonusCritDamage = critDamage;
        }
    }
}
