using System;
using System.Collections.Generic;
using UnityEngine;
using Potaria.Player;
using Potaria.Localization;

namespace Potaria.Mob
{
    /// <summary>
    /// Base class for all Potaria hostile monsters:
    /// - Rigidbody2D & BoxCollider2D physics
    /// - Contact melee damage to Player
    /// - Damage taking, defense reduction formula: max(1, damage - defense)
    /// - Knockback & hurt flash
    /// - Overhead dynamic health bar
    /// - Sprite animation & squish/stretch
    /// </summary>
    [RequireComponent(typeof(Rigidbody2D))]
    [RequireComponent(typeof(BoxCollider2D))]
    public class Mob : MonoBehaviour
    {
        [Header("Mob Stats")]
        [SerializeField] protected string mobNameKey = "mob.green_slime";
        [SerializeField] protected string fallbackName = "Green Slime";
        [SerializeField] protected int maxHp = 40;
        [SerializeField] protected int currentHp = 40;
        [SerializeField] protected int attackDamage = 12;
        [SerializeField] protected int defense = 2;
        [SerializeField] protected int level = 1;
        [SerializeField] protected float aggroRadius = 24.0f;

        [Header("Locomotion")]
        [SerializeField] protected float moveSpeed = 3.0f;
        [SerializeField] protected bool canFly = false;

        [Header("Visuals & Animation")]
        [SerializeField] protected SpriteRenderer spriteRenderer;
        [SerializeField] protected Sprite[] animationFrames;
        [SerializeField] protected float frameDuration = 0.12f;

        protected Rigidbody2D _rb;
        protected BoxCollider2D _collider;
        protected PlayerController _targetPlayer;

        protected float _animTimer = 0f;
        protected int _frameIndex = 0;
        protected float _hurtFlashTimer = 0f;
        protected float _hpBarTimer = 0f;
        protected bool _isDead = false;
        protected bool _facingRight = true;

        public int CurrentHp => currentHp;
        public int MaxHp => maxHp;
        public int AttackDamage => attackDamage;
        public int Defense => defense;
        public int Level => level;
        public bool IsDead => _isDead;
        public string LocalizedName => LocalizationManager.Get(mobNameKey, fallbackName);

        public event Action<Mob> OnMobDeath;

        protected virtual void Awake()
        {
            _rb = GetComponent<Rigidbody2D>();
            _collider = GetComponent<BoxCollider2D>();
            if (spriteRenderer == null) spriteRenderer = GetComponentInChildren<SpriteRenderer>();

            _rb.interpolation = RigidbodyInterpolation2D.Interpolate;
            _rb.collisionDetectionMode = CollisionDetectionMode2D.Continuous;
            _rb.freezeRotation = true;

            currentHp = maxHp;
            FindPlayerTarget();
        }

        protected virtual void Start()
        {
            FindPlayerTarget();
        }

        protected void FindPlayerTarget()
        {
            if (_targetPlayer == null)
            {
                _targetPlayer = FindFirstObjectByType<PlayerController>();
            }
        }

        protected virtual void Update()
        {
            if (_isDead) return;

            UpdateTimers(Time.deltaTime);
            UpdateAnimation(Time.deltaTime);
            UpdateAI(Time.deltaTime);
        }

        protected virtual void UpdateTimers(float dt)
        {
            if (_hurtFlashTimer > 0f)
            {
                _hurtFlashTimer -= dt;
                if (_hurtFlashTimer <= 0f && spriteRenderer != null)
                {
                    spriteRenderer.color = Color.white;
                }
            }

            if (_hpBarTimer > 0f)
            {
                _hpBarTimer -= dt;
            }
        }

        protected virtual void UpdateAnimation(float dt)
        {
            if (spriteRenderer == null || animationFrames == null || animationFrames.Length == 0) return;

            _animTimer += dt;
            if (_animTimer >= frameDuration)
            {
                _animTimer = 0f;
                _frameIndex = (_frameIndex + 1) % animationFrames.Length;
                spriteRenderer.sprite = animationFrames[_frameIndex];
            }

            spriteRenderer.flipX = !_facingRight;
        }

        protected virtual void UpdateAI(float dt)
        {
            // Implemented by subclasses
        }

        public virtual int TakeDamage(int rawDamage, Vector2 knockbackVelocity = default)
        {
            if (_isDead) return 0;

            int actualDamage = Mathf.Max(1, rawDamage - defense);
            currentHp -= actualDamage;

            // Flash red
            _hurtFlashTimer = 0.15f;
            if (spriteRenderer != null) spriteRenderer.color = new Color(1f, 0.35f, 0.35f, 1f);

            // Apply knockback
            if (knockbackVelocity != Vector2.zero && _rb != null)
            {
                _rb.linearVelocity = knockbackVelocity;
            }

            _hpBarTimer = 3.0f; // show hp bar

            if (currentHp <= 0)
            {
                Die();
            }

            return actualDamage;
        }

        protected virtual void Die()
        {
            _isDead = true;
            OnMobDeath?.Invoke(this);
            Destroy(gameObject, 0.05f);
        }

        protected virtual void OnCollisionStay2D(Collision2D collision)
        {
            if (_isDead) return;

            if (collision.gameObject.TryGetComponent<PlayerController>(out var player))
            {
                player.TakeDamage(attackDamage);
            }
        }
    }
}
