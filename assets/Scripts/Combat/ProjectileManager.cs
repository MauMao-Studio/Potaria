using System;
using System.Collections.Generic;
using UnityEngine;

namespace Potaria.Combat
{
    /// <summary>
    /// Central manager for all projectiles (ballistic arrows, magic bolts, boss danmaku bullets).
    /// Handles spawning, pooling, reflection field calculations, and graze detection.
    /// </summary>
    public class ProjectileManager : MonoBehaviour
    {
        private static ProjectileManager _instance;
        public static ProjectileManager Instance
        {
            get
            {
                if (_instance == null)
                {
                    _instance = FindFirstObjectByType<ProjectileManager>();
                }
                return _instance;
            }
            private set => _instance = value;
        }

        private readonly List<Projectile> _activeProjectiles = new List<Projectile>();

        public IReadOnlyList<Projectile> ActiveProjectiles => _activeProjectiles;

        public event Action<Projectile> OnGrazeTriggered;
        public event Action<Projectile> OnProjectileReflected;

        private void Reset()
        {
            if (_instance == null) _instance = this;
        }

        private void Awake()
        {
            if (_instance == null) _instance = this;
            else if (_instance != this) Destroy(gameObject);
        }

        private void OnDestroy()
        {
            if (_instance == this) _instance = null;
        }

        public Projectile SpawnProjectile(
            Vector2 position,
            Vector2 velocity,
            int damage,
            float radius = 0.5f,
            float lifeTime = 4.0f,
            ProjectileType type = ProjectileType.Linear,
            bool isEnemy = false,
            float gravity = 0.0f,
            float waveAmp = 0f,
            float waveFreq = 0f,
            float curve = 0f,
            float accel = 1.0f,
            float delay = 0f,
            int maxPierce = 1)
        {
            var go = new GameObject($"Proj_{type}_{(isEnemy ? "Enemy" : "Player")}");
            go.transform.SetParent(transform, false);
            var proj = go.AddComponent<Projectile>();
            proj.Initialize(position, velocity, damage, radius, lifeTime, type, isEnemy, gravity, waveAmp, waveFreq, curve, accel, delay);
            proj.MaxPierceTargets = maxPierce;

            _activeProjectiles.Add(proj);
            return proj;
        }

        public Projectile SpawnBallisticArrow(Vector2 startPos, Vector2 direction, int damage, float speed = 14f, float gravity = 9.8f)
        {
            Vector2 initialVelocity = direction.normalized * speed;
            return SpawnProjectile(startPos, initialVelocity, damage, radius: 0.35f, lifeTime: 5.0f, type: ProjectileType.Ballistic, isEnemy: false, gravity: gravity);
        }

        public Projectile SpawnStaffBolt(Vector2 startPos, Vector2 direction, int damage, float speed = 12f)
        {
            Vector2 initialVelocity = direction.normalized * speed;
            return SpawnProjectile(startPos, initialVelocity, damage, radius: 0.45f, lifeTime: 3.0f, type: ProjectileType.Linear, isEnemy: false);
        }

        public Projectile SpawnRodJavelin(Vector2 startPos, Vector2 direction, int damage, float speed = 16f, int pierceCount = 3)
        {
            Vector2 initialVelocity = direction.normalized * speed;
            return SpawnProjectile(startPos, initialVelocity, damage, radius: 0.4f, lifeTime: 3.5f, type: ProjectileType.Linear, isEnemy: false, maxPierce: pierceCount);
        }

        public Projectile SpawnCatalystStar(Vector2 startPos, Vector2 direction, int damage, Transform homingTarget, float speed = 10f)
        {
            Vector2 initialVelocity = direction.normalized * speed;
            var proj = SpawnProjectile(startPos, initialVelocity, damage, radius: 0.45f, lifeTime: 4.0f, type: ProjectileType.Homing, isEnemy: false);
            proj.SetHomingTarget(homingTarget);
            return proj;
        }

        /// <summary>
        /// Scans active enemy projectiles for Touhou-style grazing:
        /// Returns the count of projectiles that grazed player perimeter without hitting lethal core.
        /// </summary>
        public int CheckGrazing(Vector2 playerCenter, float playerHitboxRadius = 0.0f)
        {
            int grazedCount = 0;
            CleanupNulls();

            for (int i = _activeProjectiles.Count - 1; i >= 0; i--)
            {
                var p = _activeProjectiles[i];
                if (p == null || !p.IsEnemyProjectile || p.IsGrazed || p.IsReflected) continue;

                if (p.CheckGraze(playerCenter, playerHitboxRadius))
                {
                    grazedCount++;
                    OnGrazeTriggered?.Invoke(p);
                }
            }

            return grazedCount;
        }

        /// <summary>
        /// Scans active enemy projectiles for lethal core hits against the player.
        /// Returns count of hits and total accumulated damage.
        /// </summary>
        public int CheckPlayerHits(Vector2 playerCenter, float playerHitboxRadius, out int totalDamage)
        {
            totalDamage = 0;
            int hitCount = 0;
            CleanupNulls();

            for (int i = _activeProjectiles.Count - 1; i >= 0; i--)
            {
                var p = _activeProjectiles[i];
                if (p == null || !p.IsEnemyProjectile || p.IsReflected) continue;

                if (p.CheckCoreHit(playerCenter, playerHitboxRadius))
                {
                    totalDamage += p.Damage;
                    hitCount++;
                    p.RecordHit();
                }
            }

            return hitCount;
        }

        /// <summary>
        /// Scans active player projectiles (arrows, spells, and reflected enemy bullets)
        /// for lethal core hits against an enemy or boss.
        /// Returns count of hits and total accumulated damage.
        /// </summary>
        public int CheckEnemyHits(Vector2 enemyCenter, float enemyRadius, out int totalDamage)
        {
            totalDamage = 0;
            int hitCount = 0;
            CleanupNulls();

            for (int i = _activeProjectiles.Count - 1; i >= 0; i--)
            {
                var p = _activeProjectiles[i];
                if (p == null || (p.IsEnemyProjectile && !p.IsReflected)) continue;

                if (p.CheckCoreHit(enemyCenter, enemyRadius))
                {
                    totalDamage += p.Damage;
                    hitCount++;
                    p.RecordHit();
                }
            }

            return hitCount;
        }

        /// <summary>
        /// Executes Celestial Reversal reflection against all eligible enemy projectiles within reflection radius.
        /// Consumes reflection budget per reflected projectile and amplifies damage by 1.5x.
        /// </summary>
        public int ReflectProjectilesInRadius(Vector2 center, float reflectRadius, Vector2 targetReflectPos, ref int reflectionBudget, float damageMult = 1.5f)
        {
            int reflectedCount = 0;
            if (reflectionBudget <= 0) return 0;
            CleanupNulls();

            float radSqr = reflectRadius * reflectRadius;

            for (int i = _activeProjectiles.Count - 1; i >= 0; i--)
            {
                var p = _activeProjectiles[i];
                if (p == null || !p.IsEnemyProjectile || !p.Reflectable || p.IsReflected) continue;

                float distSqr = ((Vector2)p.transform.position - center).sqrMagnitude;
                if (distSqr <= radSqr)
                {
                    if (p.Reflect(targetReflectPos, damageMult))
                    {
                        reflectedCount++;
                        reflectionBudget--;
                        OnProjectileReflected?.Invoke(p);
                        if (reflectionBudget <= 0) break;
                    }
                }
            }

            return reflectedCount;
        }

        public void ClearAll()
        {
            CleanupNulls();
            foreach (var p in _activeProjectiles)
            {
                if (p != null) Destroy(p.gameObject);
            }
            _activeProjectiles.Clear();
        }

        private void CleanupNulls()
        {
            _activeProjectiles.RemoveAll(p => p == null);
        }

        private void Update()
        {
            CleanupNulls();
        }
    }
}
