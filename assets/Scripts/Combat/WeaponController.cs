using System;
using System.Collections.Generic;
using UnityEngine;
using Potaria.Data;
using Potaria.RPG;

namespace Potaria.Combat
{
    /// <summary>
    /// Weapon Controller managing dynamic weapon handling, melee swing arcs,
    /// directional cursor aiming, single-target combat enforcement, and Ancient/Mythic cleave exceptions.
    /// </summary>
    public class WeaponController : MonoBehaviour
    {
        [Header("Equipped Weapon")]
        [SerializeField] private WeaponItemData equippedWeapon;
        [SerializeField] private Transform weaponPivot;
        [SerializeField] private SpriteRenderer weaponRenderer;

        [Header("Swing & Cooldown")]
        [SerializeField] private float baseAttackCooldown = 0.24f;
        [SerializeField] private float swingDuration = 0.24f;
        private float _cooldownTimer = 0f;
        private float _swingProgress = 0f;
        private bool _isSwinging = false;
        private float _aimAngleRad = 0f;
        private bool _facingRight = true;

        [Header("Single-Target Rule & Cleave Tracking")]
        private readonly HashSet<int> _hitTargetsInCurrentSwing = new HashSet<int>();

        [Header("Dependencies")]
        [SerializeField] private PlayerStats playerStats;
        [SerializeField] private ProjectileManager projectileManager;

        public WeaponItemData EquippedWeapon => equippedWeapon;
        public bool IsSwinging => _isSwinging;
        public float SwingProgress => _swingProgress;
        public float CooldownTimer => _cooldownTimer;
        public bool CanAttack => _cooldownTimer <= 0f && !_isSwinging;
        public bool FacingRight => _facingRight;
        public float AimAngleRad => _aimAngleRad;

        public event Action OnAttackStarted;
        public event Action OnSwingCompleted;
        public event Action<int, bool> OnEnemyHit; // (damage, isCrit)

        private void Awake()
        {
            if (playerStats == null) playerStats = GetComponentInParent<PlayerStats>();
            if (projectileManager == null) projectileManager = ProjectileManager.Instance;
        }

        public void EquipWeapon(WeaponItemData weapon)
        {
            equippedWeapon = weapon;
            if (weapon != null)
            {
                baseAttackCooldown = Mathf.Max(0.1f, 1f / Mathf.Max(0.5f, weapon.Speed));
                swingDuration = Mathf.Min(baseAttackCooldown, 0.35f);
                if (weaponRenderer != null && weapon.Icon != null)
                {
                    weaponRenderer.sprite = weapon.Icon;
                }
            }
        }

        public void UpdateAim(Vector2 origin, Vector2 targetWorldPos)
        {
            Vector2 diff = targetWorldPos - origin;
            _aimAngleRad = Mathf.Atan2(diff.y, diff.x);
            _facingRight = diff.x >= 0;

            if (!_isSwinging && weaponPivot != null)
            {
                // Idle aiming orientation
                float deg = _aimAngleRad * Mathf.Rad2Deg;
                weaponPivot.rotation = Quaternion.Euler(0f, 0f, deg);
            }
        }

        public bool TriggerAttack(Vector2 origin, Vector2 targetWorldPos)
        {
            if (!CanAttack) return false;

            UpdateAim(origin, targetWorldPos);

            float atkSpeedMult = (playerStats != null) ? playerStats.TotalAtkSpeed : 1.0f;
            _cooldownTimer = Mathf.Max(0.08f, baseAttackCooldown / atkSpeedMult);
            swingDuration = Mathf.Max(0.10f, Mathf.Min(_cooldownTimer, 0.40f));
            _isSwinging = true;
            _swingProgress = 0f;
            _hitTargetsInCurrentSwing.Clear();

            OnAttackStarted?.Invoke();

            // If equipped weapon is ranged, spawn ballistic or magic projectile
            if (equippedWeapon != null)
            {
                string tag = equippedWeapon.SpecialTag.ToLowerInvariant();
                int dmg = (playerStats != null) ? playerStats.TotalAtk : equippedWeapon.Attack;
                Vector2 dir = (targetWorldPos - origin).normalized;

                if (tag.Contains("bow") || equippedWeapon.name.ToLowerInvariant().Contains("bow"))
                {
                    projectileManager?.SpawnBallisticArrow(origin, dir, dmg);
                }
                else if (tag.Contains("staff") || equippedWeapon.name.ToLowerInvariant().Contains("staff"))
                {
                    projectileManager?.SpawnStaffBolt(origin, dir, dmg);
                }
                else if (tag.Contains("rod") || equippedWeapon.name.ToLowerInvariant().Contains("rod"))
                {
                    projectileManager?.SpawnRodJavelin(origin, dir, dmg);
                }
                else if (tag.Contains("catalyst") || equippedWeapon.name.ToLowerInvariant().Contains("catalyst"))
                {
                    projectileManager?.SpawnCatalystStar(origin, dir, dmg, null);
                }
            }

            return true;
        }

        public void UpdateWeapon(float dt)
        {
            if (_cooldownTimer > 0f)
            {
                _cooldownTimer -= dt;
            }

            if (_isSwinging)
            {
                _swingProgress += dt / swingDuration;

                // Animate melee swing arc (parabolic sinusoidal swing from forward-top to forward-bottom)
                if (weaponPivot != null)
                {
                    float swingOffset = Mathf.Sin(_swingProgress * Mathf.PI) * 75f;
                    float baseDeg = _aimAngleRad * Mathf.Rad2Deg;
                    float finalDeg = _facingRight ? (baseDeg - swingOffset) : (baseDeg + swingOffset);
                    weaponPivot.rotation = Quaternion.Euler(0f, 0f, finalDeg);
                }

                if (_swingProgress >= 1.0f)
                {
                    _isSwinging = false;
                    _swingProgress = 0f;
                    _hitTargetsInCurrentSwing.Clear();
                    OnSwingCompleted?.Invoke();
                }
            }
        }

        private void Update()
        {
            UpdateWeapon(Time.deltaTime);
        }

        /// <summary>
        /// Attempts to damage an enemy target with single-target combat enforcement:
        /// Returns true if the target was damaged, false if already damaged in this swing (unless Ancient/Mythic cleave).
        /// </summary>
        public bool TryHitTarget(int targetInstanceId, out int damageDealt, out bool isCrit)
        {
            damageDealt = 0;
            isCrit = false;

            // Single-Target Enforcement:
            // Check if weapon has cleave: Ancient rarity, Mythic rarity, or "cleave" in special tag
            bool hasCleave = false;
            if (equippedWeapon != null)
            {
                if (equippedWeapon.Rarity == ItemRarity.Ancient || equippedWeapon.Rarity == ItemRarity.Mythic)
                {
                    hasCleave = true;
                }
                else if (equippedWeapon.SpecialTag.IndexOf("cleave", StringComparison.OrdinalIgnoreCase) >= 0)
                {
                    hasCleave = true;
                }
            }

            // If not cleave and already hit 1 target in this swing, ignore further targets!
            if (!hasCleave && _hitTargetsInCurrentSwing.Count >= 1)
            {
                return false;
            }

            // Check if this specific target already hit in this swing
            if (_hitTargetsInCurrentSwing.Contains(targetInstanceId))
            {
                return false;
            }

            _hitTargetsInCurrentSwing.Add(targetInstanceId);

            // Calculate damage & crit
            int baseDamage = (playerStats != null) ? playerStats.TotalAtk : (equippedWeapon != null ? equippedWeapon.Attack : 10);
            float critRate = (playerStats != null) ? playerStats.TotalCritRate : 5.0f;
            float critMult = (playerStats != null) ? playerStats.TotalCritMultiplier : 1.8f;

            if (UnityEngine.Random.Range(0f, 100f) < critRate)
            {
                isCrit = true;
                damageDealt = Mathf.RoundToInt(baseDamage * critMult);
            }
            else
            {
                isCrit = false;
                damageDealt = baseDamage;
            }

            OnEnemyHit?.Invoke(damageDealt, isCrit);
            return true;
        }
    }
}
