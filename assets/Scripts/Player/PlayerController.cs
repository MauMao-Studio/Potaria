using System;
using System.Collections.Generic;
using UnityEngine;
using Potaria.Input;
using Potaria.RPG;
using Potaria.Combat;

namespace Potaria.Player
{
    /// <summary>
    /// Player Controller & Physics Engine for Spud the Potato Hero:
    /// - Rigidbody2D (Interpolated, FixedUpdate) + BoxCollider2D
    /// - Responsive movement: running acceleration/deceleration, variable jump height,
    ///   coyote time (0.15s), jump buffering (0.12s), and platform drop-through (S / Down)
    /// - Liquid swimming & buoyancy: fluid drag, oxygen meter, drowning damage (1 heart/s at 0% oxygen)
    /// - Jump audio check: only triggers jump sound if head is unblocked by solid ceiling
    /// - 12 FPS animated character rendering (8-frame walk, idle breathing, jump stretch, fall)
    /// - Celestial Reversal timed projectile reflection (0.40s-0.52s window, 1.5x damage amplification)
    /// </summary>
    [RequireComponent(typeof(Rigidbody2D))]
    [RequireComponent(typeof(BoxCollider2D))]
    public class PlayerController : MonoBehaviour
    {
        [Header("Movement Knobs")]
        [SerializeField] private float baseRunSpeed = 6.0f;
        [SerializeField] private float runAcceleration = 40.0f;
        [SerializeField] private float runDeceleration = 32.0f;
        [SerializeField] private float jumpForce = 12.0f;
        [SerializeField] private float variableJumpCutMultiplier = 0.45f;
        [SerializeField] private float coyoteTime = 0.15f;
        [SerializeField] private float jumpBufferTime = 0.12f;
        [SerializeField] private float platformDropDuration = 0.25f;

        [Header("Liquid Swimming & Oxygen")]
        [SerializeField] private float waterDragHorizontal = 0.88f;
        [SerializeField] private float waterDragVertical = 0.90f;
        [SerializeField] private float waterSwimForce = 8.0f;
        [SerializeField] private float maxOxygen = 100.0f;
        [SerializeField] private float currentOxygen = 100.0f;
        [SerializeField] private float oxygenDepleteRate = 7.5f;   // Drains over ~13.3s
        [SerializeField] private float oxygenReplenishRate = 40.0f;
        [SerializeField] private float drownTickInterval = 1.0f;

        [Header("Celestial Reversal Skill")]
        [SerializeField] private float reflectionWindow = 0.45f;   // 0.40s - 0.52s
        [SerializeField] private int reflectionBudget = 15;
        [SerializeField] private float reflectionRadius = 2.5f;

        [Header("Collision Layers")]
        [SerializeField] private LayerMask groundLayerMask = ~0;
        [SerializeField] private LayerMask platformLayerMask = 0;
        [SerializeField] private LayerMask solidCeilingMask = ~0;

        [Header("Visual & Animation")]
        [SerializeField] private SpriteRenderer spriteRenderer;
        [SerializeField] private Sprite[] walkSprites;
        [SerializeField] private Sprite[] idleSprites;
        [SerializeField] private Sprite jumpSprite;
        [SerializeField] private Sprite fallSprite;
        [SerializeField] private float animFrameDuration = 1.0f / 12.0f; // 12 FPS

        [Header("Sub-Systems")]
        [SerializeField] private PlayerStats stats;
        [SerializeField] private WeaponController weaponController;
        [SerializeField] private PotariaInput input;

        private Rigidbody2D _rb;
        private BoxCollider2D _collider;

        // Timers & State
        private float _coyoteTimer = 0f;
        private float _jumpBufferTimer = 0f;
        private float _platformDropTimer = 0f;
        private float _drownTimer = 0f;
        private float _reflectionTimer = 0f;
        private float _dashTimer = 0f;
        private float _iFrameTimer = 0f;

        private bool _isGrounded = false;
        private bool _wasGrounded = false;
        private bool _inWater = false;
        private bool _isSubmerged = false;
        private bool _facingRight = true;
        private bool _isDead = false;

        // Animation State
        private float _animTimer = 0f;
        private int _walkFrameIndex = 0;
        private int _idleFrameIndex = 0;

        // Stored Input
        private Vector2 _currentMoveInput;
        private bool _jumpPressedThisFrame;
        private bool _jumpHeld;
        private bool _jumpReleasedThisFrame;
        private bool _dropPressedThisFrame;

        // Public Properties
        public Rigidbody2D Rigidbody { get { if (_rb == null) _rb = GetComponent<Rigidbody2D>(); return _rb; } }
        public BoxCollider2D Collider { get { if (_collider == null) _collider = GetComponent<BoxCollider2D>(); return _collider; } }
        public PlayerStats Stats => stats;
        public bool IsGrounded => _isGrounded;
        public bool InWater => _inWater;
        public bool IsSubmerged => _isSubmerged;
        public float CurrentOxygen => currentOxygen;
        public float MaxOxygen => maxOxygen;
        public bool IsReflecting => _reflectionTimer > 0f && reflectionBudget > 0;
        public int ReflectionBudget => reflectionBudget;
        public float ReflectionRadius => reflectionRadius;
        public bool FacingRight => _facingRight;
        public bool IsDead => _isDead;

        public event Action OnJumpSound;
        public event Action OnGrazeSparks;
        public event Action OnDeathEvent;
        public event Action OnRespawnEvent;

        private void Reset()
        {
            ConfigurePhysics();
        }

        private void Awake()
        {
            ConfigurePhysics();
            LoadDefaultSpritesIfMissing();
        }

        public void ConfigurePhysics()
        {
            if (_rb == null) _rb = GetComponent<Rigidbody2D>();
            if (_collider == null) _collider = GetComponent<BoxCollider2D>();

            // Setup Rigidbody2D discipline: Interpolate, Continuous collision, freeze rotation
            if (_rb != null)
            {
                _rb.interpolation = RigidbodyInterpolation2D.Interpolate;
                _rb.collisionDetectionMode = CollisionDetectionMode2D.Continuous;
                _rb.freezeRotation = true;
            }

            if (stats == null) stats = GetComponent<PlayerStats>();
            if (weaponController == null) weaponController = GetComponentInChildren<WeaponController>();
            if (input == null) input = PotariaInput.Instance;
            if (spriteRenderer == null) spriteRenderer = GetComponentInChildren<SpriteRenderer>();
        }

        private void Start()
        {
            if (input == null) input = PotariaInput.Instance;
            currentOxygen = maxOxygen;
        }

        public void LoadDefaultSpritesIfMissing()
        {
#if UNITY_EDITOR
            if (walkSprites == null || walkSprites.Length == 0)
            {
                var list = new List<Sprite>();
                for (int i = 0; i < 8; i++)
                {
                    var sp = UnityEditor.AssetDatabase.LoadAssetAtPath<Sprite>($"Assets/Sprites/Player/walk_{i}.png");
                    if (sp != null) list.Add(sp);
                }
                walkSprites = list.ToArray();
            }

            if (idleSprites == null || idleSprites.Length == 0)
            {
                var list = new List<Sprite>();
                for (int i = 0; i < 6; i++)
                {
                    var sp = UnityEditor.AssetDatabase.LoadAssetAtPath<Sprite>($"Assets/Sprites/Player/idle_frames_{i}.png");
                    if (sp != null) list.Add(sp);
                }
                if (list.Count == 0)
                {
                    var idleSp = UnityEditor.AssetDatabase.LoadAssetAtPath<Sprite>("Assets/Sprites/Player/idle.png");
                    if (idleSp != null) list.Add(idleSp);
                }
                idleSprites = list.ToArray();
            }

            if (jumpSprite == null)
            {
                jumpSprite = UnityEditor.AssetDatabase.LoadAssetAtPath<Sprite>("Assets/Sprites/Player/jump.png");
            }

            if (fallSprite == null)
            {
                fallSprite = UnityEditor.AssetDatabase.LoadAssetAtPath<Sprite>("Assets/Sprites/Player/fall.png");
            }
#endif
        }

        private void Update()
        {
            if (_isDead) return;

            ReadInput();
            UpdateTimers(Time.deltaTime);
            UpdateLiquidAndDrowning(Time.deltaTime);
            UpdateCombatSkills();
            UpdateAnimation(Time.deltaTime);
        }

        private void FixedUpdate()
        {
            if (_isDead) return;

            CheckGroundStatus();
            ApplyHorizontalMovement(Time.fixedDeltaTime);
            ApplyJumpAndVerticalPhysics(Time.fixedDeltaTime);
            ApplyLiquidPhysics();
            ApplyPlatformDropThrough();
        }

        private void ReadInput()
        {
            if (input == null) input = PotariaInput.Instance;
            if (input == null) return;

            _currentMoveInput = input.MoveVector;
            if (input.JumpPressed) _jumpPressedThisFrame = true;
            _jumpHeld = input.JumpHeld;
            if (input.JumpReleased) _jumpReleasedThisFrame = true;
            if (input.DropPlatformPressed) _dropPressedThisFrame = true;

            // Weapon aiming & attack
            if (weaponController != null)
            {
                Vector2 origin = transform.position;
                weaponController.UpdateAim(origin, input.MouseWorldPosition);
                if (input.AttackPressed)
                {
                    weaponController.TriggerAttack(origin, input.MouseWorldPosition);
                }
            }
        }

        private void UpdateTimers(float dt)
        {
            // Coyote Timer
            if (_isGrounded)
            {
                _coyoteTimer = coyoteTime;
            }
            else
            {
                _coyoteTimer = Mathf.Max(0f, _coyoteTimer - dt);
            }

            // Jump Buffer Timer
            if (_jumpPressedThisFrame)
            {
                _jumpBufferTimer = jumpBufferTime;
                _jumpPressedThisFrame = false;
            }
            else
            {
                _jumpBufferTimer = Mathf.Max(0f, _jumpBufferTimer - dt);
            }

            // Platform Drop-through timer
            if (_dropPressedThisFrame)
            {
                _platformDropTimer = platformDropDuration;
                _dropPressedThisFrame = false;
            }
            else
            {
                _platformDropTimer = Mathf.Max(0f, _platformDropTimer - dt);
            }

            // Reflection Timer
            if (_reflectionTimer > 0f)
            {
                _reflectionTimer = Mathf.Max(0f, _reflectionTimer - dt);
                if (_reflectionTimer <= 0f) reflectionBudget = 0;
            }

            // Dash Timer & I-Frames
            if (_dashTimer > 0f) _dashTimer = Mathf.Max(0f, _dashTimer - dt);
            if (_iFrameTimer > 0f) _iFrameTimer = Mathf.Max(0f, _iFrameTimer - dt);
        }

        private void CheckGroundStatus()
        {
            _wasGrounded = _isGrounded;

            // Ground detection: BoxCast below the collider
            Vector2 boxCenter = (Vector2)transform.position + _collider.offset + (Vector2.down * 0.05f);
            Vector2 boxSize = new Vector2(_collider.size.x * 0.9f, 0.1f);

            RaycastHit2D hit = Physics2D.BoxCast(boxCenter, boxSize, 0f, Vector2.down, 0.05f, groundLayerMask);
            _isGrounded = hit.collider != null && hit.collider != _collider;
        }

        private void ApplyHorizontalMovement(float dt)
        {
            float targetSpeed = _currentMoveInput.x * GetEffectiveMoveSpeed();

            // Dash burst override
            if (_dashTimer > 0f)
            {
                targetSpeed = (_facingRight ? 1f : -1f) * (baseRunSpeed * 2.2f);
            }

            float currentVx = _rb.linearVelocity.x;
            float accelRate = (Mathf.Abs(targetSpeed) > 0.01f) ? runAcceleration : runDeceleration;
            float newVx = Mathf.MoveTowards(currentVx, targetSpeed, accelRate * dt);

            _rb.linearVelocity = new Vector2(newVx, _rb.linearVelocity.y);

            // Update facing direction
            if (Mathf.Abs(_currentMoveInput.x) > 0.05f)
            {
                _facingRight = _currentMoveInput.x > 0;
            }
        }

        private void ApplyJumpAndVerticalPhysics(float dt)
        {
            // 1. Execute Jump if buffered and coyote valid
            if (_jumpBufferTimer > 0f && (_coyoteTimer > 0f || _inWater))
            {
                ExecuteJump();
                _jumpBufferTimer = 0f;
                _coyoteTimer = 0f;
            }

            // 2. Variable Jump Cut: cut upward velocity if jump released while rising
            if (_jumpReleasedThisFrame)
            {
                _jumpReleasedThisFrame = false;
                if (_rb.linearVelocity.y > 0.5f)
                {
                    _rb.linearVelocity = new Vector2(_rb.linearVelocity.x, _rb.linearVelocity.y * variableJumpCutMultiplier);
                }
            }
        }

        private void ExecuteJump()
        {
            float effectiveJumpForce = jumpForce;
            if (stats != null)
            {
                effectiveJumpForce *= (1.0f + stats.MealBuffs.GetJumpForceMultiplier());
            }

            if (_inWater)
            {
                _rb.linearVelocity = new Vector2(_rb.linearVelocity.x, waterSwimForce);
            }
            else
            {
                _rb.linearVelocity = new Vector2(_rb.linearVelocity.x, effectiveJumpForce);
            }

            // Audio Check: Only play jump audio if head is NOT blocked by solid block
            if (!IsHeadBlocked())
            {
                OnJumpSound?.Invoke();
            }
        }

        /// <summary>
        /// Checks if character's head is directly blocked by a solid ceiling block overhead.
        /// Returns true if solid block exists immediately above head.
        /// </summary>
        public bool IsHeadBlocked()
        {
            if (_collider == null) _collider = GetComponent<BoxCollider2D>();
            if (_collider == null) return false;

            Physics2D.SyncTransforms();

            Vector2 headCenter = (Vector2)transform.position + _collider.offset + (Vector2.up * (_collider.size.y * 0.5f));
            Vector2 boxSize = new Vector2(_collider.size.x * 0.8f, 0.15f);

            var overlap = Physics2D.OverlapBox(headCenter, boxSize, 0f, solidCeilingMask);
            if (overlap != null && overlap != _collider && !overlap.isTrigger)
            {
                if (overlap.GetComponent<PlatformEffector2D>() == null)
                {
                    return true;
                }
            }

            RaycastHit2D hit = Physics2D.BoxCast(headCenter, boxSize, 0f, Vector2.up, 0.2f, solidCeilingMask);
            if (hit.collider != null && hit.collider != _collider && !hit.collider.isTrigger)
            {
                // Check that it is not a one-way platform
                var effector = hit.collider.GetComponent<PlatformEffector2D>();
                if (effector == null)
                {
                    return true;
                }
            }
            return false;
        }

        private void ApplyLiquidPhysics()
        {
            if (_inWater)
            {
                // Apply underwater fluid drag
                Vector2 vel = _rb.linearVelocity;
                vel.x *= waterDragHorizontal;
                vel.y *= waterDragVertical;
                _rb.linearVelocity = vel;
            }
        }

        private void ApplyPlatformDropThrough()
        {
            // If dropping through platforms, ignore platform collider layer briefly
            if (platformLayerMask != 0)
            {
                Physics2D.IgnoreLayerCollision(gameObject.layer, LayerMaskToLayer(platformLayerMask), _platformDropTimer > 0f);
            }
        }

        private static int LayerMaskToLayer(LayerMask mask)
        {
            int bit = mask.value;
            for (int i = 0; i < 32; i++)
            {
                if ((bit & (1 << i)) != 0) return i;
            }
            return 0;
        }

        private void UpdateLiquidAndDrowning(float dt)
        {
            if (_isSubmerged)
            {
                currentOxygen = Mathf.Max(0f, currentOxygen - (oxygenDepleteRate * dt));
                if (currentOxygen <= 0f)
                {
                    _drownTimer += dt;
                    if (_drownTimer >= drownTickInterval)
                    {
                        _drownTimer -= drownTickInterval;
                        // Drowning damage: exactly 1 heart per second (10% max HP or max(1, maxHp / 10))
                        int heartDamage = (stats != null) ? Mathf.Max(1, stats.MaxHp / 10) : 10;
                        TakeDamage(heartDamage, ignoreDef: true);
                    }
                }
            }
            else
            {
                currentOxygen = Mathf.Min(maxOxygen, currentOxygen + (oxygenReplenishRate * dt));
                _drownTimer = 0f;
            }
        }

        private void UpdateCombatSkills()
        {
            if (input == null) return;

            // Skill 1 (Q): Power Slash
            if (input.Skill1Pressed)
            {
                CastPowerSlash();
            }

            // Skill 2 (F): Whirlwind
            if (input.Skill2Pressed)
            {
                CastWhirlwind();
            }

            // Skill 3 (V): Dash
            if (input.Skill3Pressed)
            {
                CastDash();
            }

            // Celestial Reversal (Z / R)
            if (input.Skill4Pressed || input.ZoomTogglePressed)
            {
                // Skill 4 is Fireball / Celestial Reversal
            }
        }

        public void CastPowerSlash()
        {
            if (weaponController != null)
            {
                weaponController.TriggerAttack(transform.position, input.MouseWorldPosition);
            }
        }

        public void CastWhirlwind()
        {
            if (weaponController != null)
            {
                weaponController.TriggerAttack(transform.position, transform.position + (_facingRight ? Vector3.right : Vector3.left));
            }
        }

        public void CastDash()
        {
            _dashTimer = 0.35f;
            _iFrameTimer = 0.45f;
            float dashSpeed = 12.0f;
            _rb.linearVelocity = new Vector2((_facingRight ? 1f : -1f) * dashSpeed, 0f);
        }

        /// <summary>
        /// Activates Celestial Reversal timed projectile reflection field (0.40s - 0.52s window).
        /// </summary>
        public void ActivateCelestialReversal(int skillLevel = 1)
        {
            reflectionWindow = 0.40f + (skillLevel - 1) * 0.03f;
            reflectionBudget = 12 + (skillLevel - 1) * 3;
            _reflectionTimer = reflectionWindow;
            _iFrameTimer = reflectionWindow + 0.15f;
        }

        public int TakeDamage(int damageAmount, bool ignoreDef = false)
        {
            if (_iFrameTimer > 0f || _isDead) return 0;

            int actualDamage = (stats != null) ? stats.TakeDamage(damageAmount, ignoreDef) : damageAmount;
            _iFrameTimer = 0.8f;

            if (stats != null && stats.CurrentHp <= 0)
            {
                Die();
            }

            return actualDamage;
        }

        public void Die()
        {
            _isDead = true;
            _rb.linearVelocity = Vector2.zero;
            OnDeathEvent?.Invoke();
        }

        public void Respawn(Vector2 spawnPosition)
        {
            transform.position = spawnPosition;
            _rb.linearVelocity = Vector2.zero;
            _isDead = false;
            currentOxygen = maxOxygen;
            if (stats != null)
            {
                stats.CurrentHp = stats.MaxHp;
                stats.CurrentMp = stats.MaxMp;
            }
            OnRespawnEvent?.Invoke();
        }

        public void SetWaterState(bool inWater, bool submerged)
        {
            _inWater = inWater;
            _isSubmerged = submerged;
        }

        public void TriggerGrazeReward()
        {
            stats?.OnGraze();
            OnGrazeSparks?.Invoke();
        }

        private float GetEffectiveMoveSpeed()
        {
            if (stats != null)
            {
                return baseRunSpeed * (stats.TotalMoveSpeed / 3.0f);
            }
            return baseRunSpeed;
        }

        private void UpdateAnimation(float dt)
        {
            if (spriteRenderer == null) return;

            _animTimer += dt;
            if (_animTimer >= animFrameDuration)
            {
                _animTimer = 0f;
                if (_isGrounded)
                {
                    if (Mathf.Abs(_rb.linearVelocity.x) > 0.2f && walkSprites != null && walkSprites.Length > 0)
                    {
                        _walkFrameIndex = (_walkFrameIndex + 1) % walkSprites.Length;
                        spriteRenderer.sprite = walkSprites[_walkFrameIndex];
                    }
                    else if (idleSprites != null && idleSprites.Length > 0)
                    {
                        _idleFrameIndex = (_idleFrameIndex + 1) % idleSprites.Length;
                        spriteRenderer.sprite = idleSprites[_idleFrameIndex];
                    }
                }
                else
                {
                    if (_rb.linearVelocity.y > 0.5f && jumpSprite != null)
                    {
                        spriteRenderer.sprite = jumpSprite;
                    }
                    else if (fallSprite != null)
                    {
                        spriteRenderer.sprite = fallSprite;
                    }
                }
            }

            // Sprite facing flip
            spriteRenderer.flipX = !_facingRight;
        }
    }
}
