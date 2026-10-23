using System;
using System.Collections.Generic;
using UnityEngine;
using Potaria.World.Lighting;

namespace Potaria.Mob
{
    /// <summary>
    /// Night Gazer / Demon Eye Flying AI:
    /// - Aerial flight (gravityScale = 0)
    /// - Swoops and circles toward player with organic sine wave oscillation
    /// - Aggressive swooping rushes when in close proximity
    /// - Flees upward if daylight arrives
    /// - 6-frame pupil/wing flutter animation (demon_eye_0 .. demon_eye_5)
    /// </summary>
    public class DemonEyeMob : Mob
    {
        [Header("Flight Knobs")]
        [SerializeField] private float flightSpeed = 4.5f;
        [SerializeField] private float swoopSpeed = 7.0f;
        [SerializeField] private float weaveFrequency = 2.5f;
        [SerializeField] private float weaveAmplitude = 1.8f;

        private DayNightCycle2D _dayNight;
        private float _weaveTime = 0f;
        private float _swoopTimer = 0f;

        public DemonEyeMob()
        {
            mobNameKey = "mob.demon_eye";
            fallbackName = "Night Gazer";
            maxHp = 60;
            currentHp = 60;
            attackDamage = 16;
            defense = 3;
            level = 3;
            canFly = true;
        }

        protected override void Awake()
        {
            base.Awake();
            Configure();
            _dayNight = FindFirstObjectByType<DayNightCycle2D>();
            _weaveTime = UnityEngine.Random.Range(0f, 10f);

            LoadSpritesIfMissing();
        }

        public void Configure()
        {
            mobNameKey = "mob.demon_eye";
            fallbackName = "Night Gazer";
            maxHp = 60;
            currentHp = 60;
            attackDamage = 16;
            defense = 3;
            level = 3;
            canFly = true;

            if (_rb == null) _rb = GetComponent<Rigidbody2D>();
            if (_rb != null) _rb.gravityScale = 0f;
        }

        public void LoadSpritesIfMissing()
        {
#if UNITY_EDITOR
            if (animationFrames == null || animationFrames.Length == 0)
            {
                var list = new List<Sprite>();
                for (int i = 0; i < 6; i++)
                {
                    var sp = UnityEditor.AssetDatabase.LoadAssetAtPath<Sprite>($"Assets/mobs/demon_eye_{i}.png");
                    if (sp == null) sp = UnityEditor.AssetDatabase.LoadAssetAtPath<Sprite>($"Assets/Sprites/Mobs/demon_eye_{i}.png");
                    if (sp != null) list.Add(sp);
                }
                animationFrames = list.ToArray();
            }

            if (spriteRenderer != null && spriteRenderer.sprite == null && animationFrames != null && animationFrames.Length > 0)
            {
                spriteRenderer.sprite = animationFrames[0];
            }
#endif
        }

        protected override void UpdateAI(float dt)
        {
            FindPlayerTarget();
            if (_dayNight == null) _dayNight = FindFirstObjectByType<DayNightCycle2D>();

            // If day arrives, flee high into the upper atmosphere
            if (_dayNight != null && !_dayNight.IsNight)
            {
                _rb.linearVelocity = new Vector2(0f, flightSpeed * 1.5f);
                if (transform.position.y > 50f)
                {
                    Destroy(gameObject);
                }
                return;
            }

            if (_targetPlayer == null || _targetPlayer.IsDead)
            {
                _rb.linearVelocity = Vector2.zero;
                return;
            }

            Vector2 playerPos = _targetPlayer.transform.position;
            float dist = Vector2.Distance(transform.position, playerPos);
            if (dist > aggroRadius)
            {
                _rb.linearVelocity = Vector2.zero;
                return;
            }

            _weaveTime += dt * weaveFrequency;
            _swoopTimer += dt;

            Vector2 toPlayer = (playerPos - (Vector2)transform.position).normalized;
            _facingRight = toPlayer.x > 0;

            // Perpendicular weave vector
            Vector2 perp = new Vector2(-toPlayer.y, toPlayer.x);
            float weave = Mathf.Sin(_weaveTime) * weaveAmplitude;

            float currentSpeed = (dist < 8.0f) ? swoopSpeed : flightSpeed;
            Vector2 targetVel = (toPlayer * currentSpeed) + (perp * weave);

            _rb.linearVelocity = Vector2.Lerp(_rb.linearVelocity, targetVel, dt * 5.0f);
        }
    }
}
