using System;
using UnityEngine;

namespace Potaria.Combat
{
    public enum ProjectileType
    {
        Linear,
        Ballistic,      // Parabolic gravity arc
        Wave,           // Sinusoidal oscillation
        Spiral,         // Rotating curvature
        Homing,         // Steering toward target
        Singularity,    // Black hole vortex (non-reflectable)
        Meteor          // Falling heavy meteor (non-reflectable)
    }

    /// <summary>
    /// High-performance universal projectile supporting ballistic arrows, magic bolts,
    /// Touhou/Gungeon 52% fair lethal core hitboxes, perimeter graze detection, and dynamic reflection.
    /// </summary>
    public class Projectile : MonoBehaviour
    {
        [Header("Projectile Properties")]
        [SerializeField] private int projectileId;
        [SerializeField] private bool isEnemyProjectile = true;
        [SerializeField] private int damage = 18;
        [SerializeField] private float radius = 0.5f;          // Visual radius in Unity units (~8-10px)
        [SerializeField] private float coreRadiusRatio = 0.52f;// 52% Fair lethal core hitbox
        [SerializeField] private float grazeRadiusRatio = 1.75f;// Perimeter graze boundary (100% to 175%)
        [SerializeField] private float lifeTime = 4.0f;
        [SerializeField] private ProjectileType projectileType = ProjectileType.Linear;
        [SerializeField] private float gravity = 0.0f;
        [SerializeField] private bool reflectable = true;
        [SerializeField] private bool isReflected = false;
        [SerializeField] private int maxPierceTargets = 1;

        [Header("Kinematics")]
        [SerializeField] private Vector2 velocity;
        [SerializeField] private float waveAmplitude = 0.0f;
        [SerializeField] private float waveFrequency = 0.0f;
        [SerializeField] private float curveRate = 0.0f;        // radians/sec
        [SerializeField] private float acceleration = 1.0f;
        [SerializeField] private float initialDelay = 0.0f;

        private float _age = 0f;
        private bool _isGrazed = false;
        private int _targetsHit = 0;
        private Transform _homingTarget;
        private Vector2 _initialDirection;

        public int ProjectileId { get => projectileId; set => projectileId = value; }
        public bool IsEnemyProjectile { get => isEnemyProjectile; set => isEnemyProjectile = value; }
        public int Damage { get => damage; set => damage = value; }
        public float Radius { get => radius; set => radius = value; }
        public float CoreRadius => radius * coreRadiusRatio;
        public float GrazeRadius => radius * grazeRadiusRatio;
        public float LifeTime { get => lifeTime; set => lifeTime = value; }
        public float Age => _age;
        public ProjectileType Type { get => projectileType; set => projectileType = value; }
        public float Gravity { get => gravity; set => gravity = value; }
        public bool Reflectable => reflectable && (projectileType != ProjectileType.Singularity && projectileType != ProjectileType.Meteor);
        public bool IsReflected => isReflected;
        public bool IsGrazed { get => _isGrazed; set => _isGrazed = value; }
        public Vector2 Velocity { get => velocity; set => velocity = value; }
        public int MaxPierceTargets { get => maxPierceTargets; set => maxPierceTargets = value; }
        public int TargetsHit => _targetsHit;

#pragma warning disable CS0067
        public event Action<Projectile, Collider2D> OnHit;
#pragma warning restore CS0067
        public event Action<Projectile> OnReflected;
        public event Action<Projectile> OnGraze;

        public void Initialize(
            Vector2 startPos,
            Vector2 initialVelocity,
            int damage,
            float rad = 0.5f,
            float life = 4.0f,
            ProjectileType type = ProjectileType.Linear,
            bool enemy = true,
            float grav = 0.0f,
            float waveAmp = 0f,
            float waveFreq = 0f,
            float curve = 0f,
            float accel = 1.0f,
            float delay = 0f)
        {
            transform.position = new Vector3(startPos.x, startPos.y, 0f);
            velocity = initialVelocity;
            _initialDirection = initialVelocity.normalized;
            this.damage = damage;
            radius = rad;
            lifeTime = life;
            projectileType = type;
            isEnemyProjectile = enemy;
            gravity = grav;
            waveAmplitude = waveAmp;
            waveFrequency = waveFreq;
            curveRate = curve;
            acceleration = accel;
            initialDelay = delay;

            _age = 0f;
            _isGrazed = false;
            _targetsHit = 0;
            isReflected = false;
        }

        public void SetHomingTarget(Transform target)
        {
            _homingTarget = target;
        }

        public void UpdateMotion(float dt)
        {
            _age += dt;
            if (_age < initialDelay) return;

            // 1. Acceleration
            if (acceleration != 1.0f)
            {
                velocity *= Mathf.Pow(acceleration, dt * 60f);
            }

            // 2. Trajectory types
            switch (projectileType)
            {
                case ProjectileType.Ballistic:
                    // Parabolic gravity
                    velocity.y -= gravity * dt;
                    break;

                case ProjectileType.Spiral:
                    if (curveRate != 0f)
                    {
                        float angle = curveRate * dt;
                        float cos = Mathf.Cos(angle);
                        float sin = Mathf.Sin(angle);
                        velocity = new Vector2(
                            velocity.x * cos - velocity.y * sin,
                            velocity.x * sin + velocity.y * cos
                        );
                    }
                    break;

                case ProjectileType.Homing:
                    if (_homingTarget != null)
                    {
                        Vector2 toTarget = ((Vector2)_homingTarget.position - (Vector2)transform.position).normalized;
                        velocity = Vector2.Lerp(velocity.normalized, toTarget, dt * 3.5f).normalized * velocity.magnitude;
                    }
                    break;

                case ProjectileType.Wave:
                    // Wave offset applied perpendicular to initial direction
                    if (waveAmplitude > 0f && waveFrequency > 0f)
                    {
                        Vector2 perp = new Vector2(-_initialDirection.y, _initialDirection.x);
                        float wave = Mathf.Sin((_age - initialDelay) * waveFrequency) * waveAmplitude;
                        transform.position += (Vector3)(perp * wave * dt);
                    }
                    break;
            }

            // 3. Move position
            transform.position += (Vector3)(velocity * dt);

            // 4. Align orientation along velocity for ballistic arrows / shards
            if (velocity.sqrMagnitude > 0.001f)
            {
                float rotZ = Mathf.Atan2(velocity.y, velocity.x) * Mathf.Rad2Deg;
                transform.rotation = Quaternion.Euler(0f, 0f, rotZ);
            }

            // 5. Expiration
            if (_age >= lifeTime)
            {
                Despawn();
            }
        }

        private void Update()
        {
            UpdateMotion(Time.deltaTime);
        }

        /// <summary>
        /// Precision circle intersection check for fair core lethal hitbox.
        /// Returns true if otherPos within coreRadius.
        /// </summary>
        public bool CheckCoreHit(Vector2 otherCenter, float otherRadius = 0f)
        {
            float distSqr = ((Vector2)transform.position - otherCenter).sqrMagnitude;
            float totalR = CoreRadius + otherRadius;
            return distSqr <= (totalR * totalR);
        }

        /// <summary>
        /// Precision circle intersection check for perimeter grazing.
        /// Returns true if within graze radius but outside core lethal radius.
        /// </summary>
        public bool CheckGraze(Vector2 otherCenter, float otherRadius = 0f)
        {
            if (_isGrazed) return false;

            float distSqr = ((Vector2)transform.position - otherCenter).sqrMagnitude;
            float coreR = CoreRadius + otherRadius;
            float grazeR = GrazeRadius + otherRadius;

            if (distSqr <= (grazeR * grazeR) && distSqr > (coreR * coreR))
            {
                _isGrazed = true;
                OnGraze?.Invoke(this);
                return true;
            }
            return false;
        }

        /// <summary>
        /// Reflects the projectile back toward targetPos with 1.5x damage amplification.
        /// Switches ownership from enemy to player and marks as reflected.
        /// </summary>
        public bool Reflect(Vector2 targetPos, float damageMultiplier = 1.5f)
        {
            if (isReflected || !Reflectable) return false;

            isReflected = true;
            isEnemyProjectile = false; // Now hits enemies!
            damage = Mathf.RoundToInt(damage * damageMultiplier);

            Vector2 dir = (targetPos - (Vector2)transform.position).normalized;
            float speed = Mathf.Max(6.0f, velocity.magnitude * 1.25f);
            velocity = dir * speed;
            _initialDirection = dir;

            OnReflected?.Invoke(this);
            return true;
        }

        public bool RecordHit()
        {
            _targetsHit++;
            if (_targetsHit >= maxPierceTargets)
            {
                Despawn();
                return true;
            }
            return false;
        }

        public void Despawn()
        {
            Destroy(gameObject);
        }
    }
}
