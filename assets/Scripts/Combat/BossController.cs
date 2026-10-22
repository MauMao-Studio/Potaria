using System;
using System.Collections.Generic;
using UnityEngine;
using Potaria.RPG;

namespace Potaria.Combat
{
    public enum BossType
    {
        GrandBossSolRho,
        LordMalus,
        IgnisColossus,
        CryoSpud,
        NecroTuber
    }

    /// <summary>
    /// Boss Controller orchestrating bullet-hell danmaku patterns, multi-phase transitions,
    /// dynamic player scaling, and combat state machines.
    /// </summary>
    public class BossController : MonoBehaviour
    {
        [Header("Boss Identity")]
        [SerializeField] private BossType bossType = BossType.GrandBossSolRho;
        [SerializeField] private string bossName = "Sol-Rho - The Celestial Titan";
        [SerializeField] private int phase = 1;
        [SerializeField] private bool isTransforming = false;
        [SerializeField] private float transformDuration = 2.0f;

        [Header("Phase Health")]
        [SerializeField] private int phase1MaxHp = 14000;
        [SerializeField] private int phase2MaxHp = 20000;
        [SerializeField] private int currentHp;
        [SerializeField] private int defense = 48;
        [SerializeField] private int attackDamage = 68;

        [Header("Danmaku Pattern Timing")]
        [SerializeField] private float attackCooldown = 1.8f;
        private float _attackTimer = 0f;
        private float _transformTimer = 0f;
        private float _patternRotationAngle = 0f;
        private int _patternStep = 0;

        [Header("Dependencies")]
        [SerializeField] private DanmakuEmitter emitter;

        public BossType Type => bossType;
        public string BossName => bossName;
        public int Phase => phase;
        public bool IsTransforming => isTransforming;
        public float TransformDuration => transformDuration;
        public int CurrentHp => currentHp;
        public int MaxHp => (phase == 1) ? phase1MaxHp : phase2MaxHp;
        public int Defense => defense;
        public int AttackDamage => attackDamage;
        public bool IsDead => currentHp <= 0 && phase >= 2;

        public event Action<int, int> OnHpChanged; // (current, max)
        public event Action<int> OnPhaseChanged;   // (newPhase)
        public event Action OnDefeated;

        private void Awake()
        {
            if (emitter == null) emitter = GetComponent<DanmakuEmitter>();
            if (emitter == null) emitter = gameObject.AddComponent<DanmakuEmitter>();

            ResetBoss(phase1MaxHp, phase2MaxHp, defense, attackDamage);
        }

        public void ResetBoss(int p1Hp = 14000, int p2Hp = 20000, int def = 48, int atk = 68)
        {
            phase1MaxHp = p1Hp;
            phase2MaxHp = p2Hp;
            defense = def;
            attackDamage = atk;
            phase = 1;
            isTransforming = false;
            currentHp = phase1MaxHp;
            _attackTimer = 0.5f;
            _patternRotationAngle = 0f;
            _patternStep = 0;

            OnHpChanged?.Invoke(currentHp, phase1MaxHp);
        }

        public void ScaleToPlayer(int playerLevel, int playerAtk, float rematchMultiplier = 1.0f)
        {
            float scale = (1.0f + (playerLevel - 1) * 0.15f + Mathf.Max(0f, (playerAtk - 30) / 75.0f) * 0.35f) * rematchMultiplier;
            phase1MaxHp = Mathf.RoundToInt(14000 * scale);
            phase2MaxHp = Mathf.RoundToInt(20000 * scale);
            defense = Mathf.RoundToInt(48 * (1.0f + (playerLevel - 1) * 0.08f) * rematchMultiplier);
            attackDamage = Mathf.RoundToInt(68 * (1.0f + (playerLevel - 1) * 0.05f) * Mathf.Min(2.5f, rematchMultiplier));
            currentHp = (phase == 1) ? phase1MaxHp : phase2MaxHp;
            OnHpChanged?.Invoke(currentHp, MaxHp);
        }

        public int TakeDamage(int incomingDamage)
        {
            if (isTransforming || IsDead) return 0;

            int mitigated = Mathf.Max(1, incomingDamage - defense);
            currentHp -= mitigated;
            OnHpChanged?.Invoke(currentHp, MaxHp);

            if (currentHp <= 0)
            {
                if (phase == 1 && bossType == BossType.GrandBossSolRho)
                {
                    // Trigger Phase 2 Transformation!
                    TransitionToPhase2();
                }
                else
                {
                    currentHp = 0;
                    OnDefeated?.Invoke();
                }
            }

            return mitigated;
        }

        public void TransitionToPhase2()
        {
            phase = 2;
            isTransforming = true;
            _transformTimer = transformDuration;
            currentHp = phase2MaxHp;
            defense = Mathf.RoundToInt(defense * 1.33f);
            attackDamage = Mathf.RoundToInt(attackDamage * 1.35f);
            bossName = "Sol-Rho - Awakened Void Incarnate";

            OnPhaseChanged?.Invoke(2);
            OnHpChanged?.Invoke(currentHp, phase2MaxHp);
        }

        public void ExecuteNextDanmakuPattern(Vector2 playerPosition)
        {
            if (emitter == null || isTransforming || IsDead) return;

            Vector2 origin = transform.position;

            switch (_patternStep % 3)
            {
                case 0:
                    // 16-Way Spiral Nova
                    emitter.SpawnSpiralNova(origin, baseAngle: _patternRotationAngle, streamCount: 16, speed: 6.0f, curveRate: 0.28f, damage: attackDamage);
                    _patternRotationAngle += 0.35f;
                    break;

                case 1:
                    // Rotating Celestial Cross Beams
                    emitter.SpawnRotatingCrossBeams(origin, rotationAngle: _patternRotationAngle, arms: 4, bulletsPerArm: 4, speed: 5.0f, damage: attackDamage);
                    _patternRotationAngle += 0.45f;
                    break;

                case 2:
                    // Targeted Ring with Safe Dodge Corridor
                    emitter.SpawnTargetedRing(origin, playerPosition, bulletCount: 18, speed: 5.2f, gapHalfAngleRad: 0.38f, damage: attackDamage);
                    break;
            }

            _patternStep++;
        }

        private void Update()
        {
            if (IsDead) return;

            if (isTransforming)
            {
                _transformTimer -= Time.deltaTime;
                if (_transformTimer <= 0f)
                {
                    isTransforming = false;
                }
                return;
            }

            CheckPlayerProjectileHits();

            _attackTimer -= Time.deltaTime;
            if (_attackTimer <= 0f)
            {
                _attackTimer = attackCooldown;
                // Target player or (0,0) if no player assigned
                Vector2 target = Vector2.zero;
                ExecuteNextDanmakuPattern(target);
            }
        }

        public void CheckPlayerProjectileHits()
        {
            if (isTransforming || IsDead) return;

            var pm = ProjectileManager.Instance;
            if (pm == null) return;

            float bossRadius = 1.5f;
            int hits = pm.CheckEnemyHits(transform.position, bossRadius, out int dmg);
            if (hits > 0 && dmg > 0)
            {
                TakeDamage(dmg);
            }
        }
    }
}
