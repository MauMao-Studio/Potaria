using System;
using System.Collections.Generic;
using UnityEngine;

namespace Potaria.Combat
{
    /// <summary>
    /// High-density geometric bullet pattern generator for dungeon mini-bosses and Grand Boss Sol-Rho.
    /// Emits 16-way spiral novas, rotating celestial cross beams, and targeted rings with navigable dodge gaps.
    /// </summary>
    public class DanmakuEmitter : MonoBehaviour
    {
        [Header("Danmaku Defaults")]
        [SerializeField] private float defaultBulletRadius = 0.5f;
        [SerializeField] private int defaultBulletDamage = 18;
        [SerializeField] private float defaultLifeTime = 4.0f;

        public float DefaultBulletRadius => defaultBulletRadius;
        public int DefaultBulletDamage => defaultBulletDamage;
        public ProjectileManager Manager => ProjectileManager.Instance;

        /// <summary>
        /// 1. 16-Way Spiral Nova: Omnidirectional expanding starburst with curving spiral trajectory.
        /// </summary>
        public List<Projectile> SpawnSpiralNova(
            Vector2 origin,
            float baseAngle = 0f,
            int streamCount = 16,
            float speed = 6.0f,
            float curveRate = 0.25f,
            int damage = 18,
            float radius = 0.5f)
        {
            var results = new List<Projectile>();
            if (Manager == null || streamCount <= 0) return results;

            float angleStep = (2f * Mathf.PI) / streamCount;
            for (int i = 0; i < streamCount; i++)
            {
                float ang = baseAngle + (i * angleStep);
                Vector2 vel = new Vector2(Mathf.Cos(ang), Mathf.Sin(ang)) * speed;
                var proj = Manager.SpawnProjectile(
                    origin,
                    vel,
                    damage,
                    radius,
                    defaultLifeTime,
                    ProjectileType.Spiral,
                    isEnemy: true,
                    curve: curveRate
                );
                results.Add(proj);
            }

            return results;
        }

        /// <summary>
        /// 2. Rotating Celestial Cross Beams: 4-way or 8-way rotating cross beams forming moving dodge corridors.
        /// </summary>
        public List<Projectile> SpawnRotatingCrossBeams(
            Vector2 origin,
            float rotationAngle,
            int arms = 4,
            int bulletsPerArm = 5,
            float armSpacing = 0.6f,
            float speed = 4.5f,
            int damage = 20,
            float radius = 0.5f)
        {
            var results = new List<Projectile>();
            if (Manager == null || arms <= 0) return results;

            float armAngleStep = (2f * Mathf.PI) / arms;

            for (int a = 0; a < arms; a++)
            {
                float angle = rotationAngle + (a * armAngleStep);
                Vector2 dir = new Vector2(Mathf.Cos(angle), Mathf.Sin(angle));
                Vector2 vel = dir * speed;

                for (int b = 0; b < bulletsPerArm; b++)
                {
                    Vector2 bulletPos = origin + (dir * (b * armSpacing));
                    var proj = Manager.SpawnProjectile(
                        bulletPos,
                        vel,
                        damage,
                        radius,
                        defaultLifeTime,
                        ProjectileType.Linear,
                        isEnemy: true
                    );
                    results.Add(proj);
                }
            }

            return results;
        }

        /// <summary>
        /// 3. Targeted Ring with Safe Dodge Gaps: Concentric ring expanding outward, leaving clear navigable
        /// gaps aligned with or around the player vector.
        /// </summary>
        public List<Projectile> SpawnTargetedRing(
            Vector2 origin,
            Vector2 targetPos,
            int bulletCount = 20,
            float speed = 5.0f,
            float gapHalfAngleRad = 0.35f, // ~20-degree gap on each side of the corridor
            int damage = 18,
            float radius = 0.5f)
        {
            var results = new List<Projectile>();
            if (Manager == null || bulletCount <= 0) return results;

            Vector2 toTarget = (targetPos - origin).normalized;
            float targetAngle = Mathf.Atan2(toTarget.y, toTarget.x);
            float angleStep = (2f * Mathf.PI) / bulletCount;

            for (int i = 0; i < bulletCount; i++)
            {
                float ang = i * angleStep;
                // Calculate angular distance to target angle
                float diff = Mathf.DeltaAngle(ang * Mathf.Rad2Deg, targetAngle * Mathf.Rad2Deg) * Mathf.Deg2Rad;

                // Check if inside safe passage corridor
                if (Mathf.Abs(diff) < gapHalfAngleRad)
                {
                    continue; // Skip bullet to create fair dodge lane
                }

                Vector2 vel = new Vector2(Mathf.Cos(ang), Mathf.Sin(ang)) * speed;
                var proj = Manager.SpawnProjectile(
                    origin,
                    vel,
                    damage,
                    radius,
                    defaultLifeTime,
                    ProjectileType.Linear,
                    isEnemy: true
                );
                results.Add(proj);
            }

            return results;
        }

        /// <summary>
        /// 4. Symmetrical 16-point crystalline snowflake burst.
        /// </summary>
        public List<Projectile> SpawnSnowflakeBurst(
            Vector2 origin,
            int points = 16,
            float speed = 5.5f,
            int damage = 18,
            float radius = 0.5f,
            float offsetAngle = 0f)
        {
            var results = new List<Projectile>();
            if (Manager == null || points <= 0) return results;

            float step = (2f * Mathf.PI) / points;
            for (int i = 0; i < points; i++)
            {
                float ang = offsetAngle + (i * step);
                Vector2 vel = new Vector2(Mathf.Cos(ang), Mathf.Sin(ang)) * speed;
                var proj = Manager.SpawnProjectile(
                    origin,
                    vel,
                    damage,
                    radius,
                    defaultLifeTime,
                    ProjectileType.Linear,
                    isEnemy: true
                );
                results.Add(proj);
            }

            return results;
        }
    }
}
