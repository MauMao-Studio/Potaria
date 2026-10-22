using System;
using UnityEngine;

namespace Potaria.RPG
{
    /// <summary>
    /// Base RPG statistics component for entities (Player, Bosses, Mobs).
    /// Handles HP, ATK, DEF, Crit, and standard damage calculation formulas.
    /// </summary>
    public class CharacterStats : MonoBehaviour
    {
        [Header("Level & Vitality")]
        [SerializeField] protected int currentHp = 100;
        [SerializeField] protected int maxHp = 100;
        [SerializeField] protected int currentMp = 50;
        [SerializeField] protected int maxMp = 50;

        [Header("Base Combat Stats")]
        [SerializeField] protected int baseAtk = 10;
        [SerializeField] protected int baseDef = 2;
        [SerializeField] protected float baseCritRate = 5.0f;       // 5% base
        [SerializeField] protected float critMultiplier = 1.8f;      // 180%
        [SerializeField] protected float baseMoveSpeed = 3.0f;
        [SerializeField] protected float baseAtkSpeed = 1.0f;

        public event Action<int, int> OnHpChanged; // (current, max)
        public event Action<int, int> OnMpChanged; // (current, max)
        public event Action OnDeath;

        public virtual int CurrentHp
        {
            get => currentHp;
            set
            {
                int clamped = Mathf.Clamp(value, 0, MaxHp);
                if (clamped != currentHp)
                {
                    currentHp = clamped;
                    OnHpChanged?.Invoke(currentHp, MaxHp);
                    if (currentHp <= 0) OnDeath?.Invoke();
                }
            }
        }

        public virtual int MaxHp
        {
            get => maxHp;
            set
            {
                maxHp = Mathf.Max(1, value);
                currentHp = Mathf.Clamp(currentHp, 0, maxHp);
                OnHpChanged?.Invoke(currentHp, maxHp);
            }
        }

        public virtual int CurrentMp
        {
            get => currentMp;
            set
            {
                int clamped = Mathf.Clamp(value, 0, MaxMp);
                if (clamped != currentMp)
                {
                    currentMp = clamped;
                    OnMpChanged?.Invoke(currentMp, MaxMp);
                }
            }
        }

        public virtual int MaxMp
        {
            get => maxMp;
            set
            {
                maxMp = Mathf.Max(0, value);
                currentMp = Mathf.Clamp(currentMp, 0, maxMp);
                OnMpChanged?.Invoke(currentMp, maxMp);
            }
        }

        public virtual int BaseAtk { get => baseAtk; set => baseAtk = value; }
        public virtual int BaseDef { get => baseDef; set => baseDef = value; }
        public virtual float BaseCritRate { get => baseCritRate; set => baseCritRate = value; }
        public virtual float CritMultiplier { get => critMultiplier; set => critMultiplier = value; }
        public virtual float BaseMoveSpeed { get => baseMoveSpeed; set => baseMoveSpeed = value; }
        public virtual float BaseAtkSpeed { get => baseAtkSpeed; set => baseAtkSpeed = value; }

        public virtual int TotalAtk => BaseAtk;
        public virtual int TotalDef => BaseDef;
        public virtual float TotalCritRate => Mathf.Min(75f, BaseCritRate);
        public virtual float TotalMoveSpeed => BaseMoveSpeed;
        public virtual float TotalAtkSpeed => BaseAtkSpeed;

        public bool IsDead => CurrentHp <= 0;

        /// <summary>
        /// Standard Potaria defense mitigation formula: Damage = max(1, incomingAtk - totalDef).
        /// </summary>
        public virtual int CalculateDamageTaken(int incomingAtk, bool ignoreDef = false, float damageReduction = 0f, float magicRes = 0f, bool isMagic = false)
        {
            if (ignoreDef)
            {
                int raw = Mathf.Max(1, incomingAtk);
                if (magicRes > 0f) raw = Mathf.Max(1, Mathf.RoundToInt(raw * (1f - magicRes)));
                return raw;
            }

            int def = TotalDef;
            int mitigated = Mathf.Max(1, incomingAtk - def);

            if (damageReduction > 0f)
            {
                mitigated = Mathf.Max(1, Mathf.RoundToInt(mitigated * (1f - damageReduction)));
            }

            if (isMagic && magicRes > 0f)
            {
                mitigated = Mathf.Max(1, Mathf.RoundToInt(mitigated * (1f - magicRes)));
            }

            return mitigated;
        }

        public virtual int TakeDamage(int incomingAtk, bool ignoreDef = false, float damageReduction = 0f, float magicRes = 0f, bool isMagic = false)
        {
            int damage = CalculateDamageTaken(incomingAtk, ignoreDef, damageReduction, magicRes, isMagic);
            CurrentHp -= damage;
            return damage;
        }

        public virtual void Heal(int amount)
        {
            if (amount <= 0 || IsDead) return;
            CurrentHp += amount;
        }

        public virtual void RestoreMp(int amount)
        {
            if (amount <= 0) return;
            CurrentMp += amount;
        }
    }
}
