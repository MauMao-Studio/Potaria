using System;
using System.Collections.Generic;
using UnityEngine;

namespace Potaria.Mob
{
    /// <summary>
    /// Slime Monster AI (Green Slime / Purple Slime):
    /// - Periodic hopping locomotion toward player (jump delay: 1.2s - 2.0s)
    /// - Jump impulses (horizontal 3.5f - 5.5f, vertical 7.0f - 9.0f)
    /// - Squish & stretch animation on jump and impact
    /// - Multiple frames of squish/blob animation
    /// </summary>
    public class SlimeMob : Mob
    {
        public enum SlimeType
        {
            Green,
            Purple
        }

        [Header("Slime Variant")]
        [SerializeField] private SlimeType slimeType = SlimeType.Green;
        [SerializeField] private float hopIntervalMin = 1.2f;
        [SerializeField] private float hopIntervalMax = 2.0f;
        [SerializeField] private float hopSpeedX = 4.0f;
        [SerializeField] private float hopForceY = 8.0f;

        private float _hopCooldown = 1.0f;
        private bool _isGrounded = false;
        private Vector3 _originalScale = Vector3.one;

        protected override void Awake()
        {
            base.Awake();
            _originalScale = transform.localScale;
            ConfigureVariant(slimeType);
            LoadSpritesIfMissing();
        }

        public void ConfigureVariant(SlimeType type)
        {
            slimeType = type;
            if (type == SlimeType.Green)
            {
                mobNameKey = "mob.green_slime";
                fallbackName = "Green Slime";
                maxHp = 40;
                attackDamage = 12;
                defense = 2;
                level = 1;
                hopSpeedX = 4.0f;
                hopForceY = 8.0f;
            }
            else
            {
                mobNameKey = "mob.purple_slime";
                fallbackName = "Purple Slime";
                maxHp = 75;
                attackDamage = 18;
                defense = 5;
                level = 3;
                hopSpeedX = 4.8f;
                hopForceY = 9.0f;
            }
            currentHp = maxHp;
        }

        public void LoadSpritesIfMissing()
        {
#if UNITY_EDITOR
            if (animationFrames == null || animationFrames.Length == 0)
            {
                string prefix = (slimeType == SlimeType.Purple) ? "corrupt_slime" : "slime";
                var list = new List<Sprite>();
                for (int i = 0; i < 6; i++)
                {
                    var sp = UnityEditor.AssetDatabase.LoadAssetAtPath<Sprite>($"Assets/mobs/{prefix}_{i}.png");
                    if (sp == null) sp = UnityEditor.AssetDatabase.LoadAssetAtPath<Sprite>($"Assets/Sprites/Mobs/{prefix}_{i}.png");
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
            CheckGrounded();

            // Squash & Stretch visual feedback
            if (!_isGrounded)
            {
                // Stretched vertically while airborne
                float vy = _rb.linearVelocity.y;
                float stretch = Mathf.Clamp(Mathf.Abs(vy) * 0.03f, 0f, 0.35f);
                transform.localScale = new Vector3(_originalScale.x * (1f - stretch * 0.5f), _originalScale.y * (1f + stretch), 1f);
            }
            else
            {
                // Settle smoothly back to original scale
                transform.localScale = Vector3.MoveTowards(transform.localScale, _originalScale, dt * 4f);
            }

            if (_targetPlayer == null || _targetPlayer.IsDead) return;

            Vector2 playerPos = _targetPlayer.transform.position;
            float dist = Vector2.Distance(transform.position, playerPos);
            if (dist > aggroRadius) return;

            _hopCooldown -= dt;
            if (_hopCooldown <= 0f && _isGrounded)
            {
                ExecuteHop(playerPos);
            }
        }

        private void CheckGrounded()
        {
            if (_collider == null) _collider = GetComponent<BoxCollider2D>();
            if (_collider == null) return;

            float footY = transform.position.y + _collider.offset.y - (_collider.size.y * 0.5f);
            Vector2 footCenter = new Vector2(transform.position.x + _collider.offset.x, footY);
            RaycastHit2D hit = Physics2D.BoxCast(new Vector2(footCenter.x, footCenter.y + 0.05f), new Vector2(_collider.size.x * 0.8f, 0.08f), 0f, Vector2.down, 0.12f, ~0);

            _isGrounded = hit.collider != null && hit.collider != _collider && !hit.collider.isTrigger && !hit.collider.transform.IsChildOf(transform);
        }

        private void ExecuteHop(Vector2 playerPos)
        {
            float dirX = (playerPos.x > transform.position.x) ? 1f : -1f;
            _facingRight = dirX > 0;

            _rb.linearVelocity = new Vector2(dirX * hopSpeedX, hopForceY);
            _hopCooldown = UnityEngine.Random.Range(hopIntervalMin, hopIntervalMax);

            // Squish down right as it launches
            transform.localScale = new Vector3(_originalScale.x * 1.35f, _originalScale.y * 0.65f, 1f);
        }
    }
}
