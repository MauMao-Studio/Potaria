using System;
using System.Collections.Generic;
using UnityEngine;

namespace Potaria.Mob
{
    /// <summary>
    /// Surface Zombie AI:
    /// - Shambles continuously toward the player across terrain (speed: ~2.4)
    /// - Obstacle detection: checks forward block; if walled, jumps up to traverse 1-block steps
    /// - Melee attack on contact
    /// - 6-frame walking animation (zombie_0 .. zombie_5)
    /// </summary>
    public class ZombieMob : Mob
    {
        [Header("Zombie Attributes")]
        [SerializeField] private float obstacleJumpForce = 7.0f;
        [SerializeField] private float jumpCooldown = 1.0f;

        private float _jumpTimer = 0f;

        public ZombieMob()
        {
            mobNameKey = "mob.zombie";
            fallbackName = "Surface Zombie";
            maxHp = 90;
            currentHp = 90;
            attackDamage = 15;
            defense = 4;
            level = 2;
            moveSpeed = 2.4f;
        }

        protected override void Awake()
        {
            base.Awake();
            Configure();
            LoadSpritesIfMissing();
        }

        public void Configure()
        {
            mobNameKey = "mob.zombie";
            fallbackName = "Surface Zombie";
            maxHp = 90;
            currentHp = 90;
            attackDamage = 15;
            defense = 4;
            level = 2;
            moveSpeed = 2.4f;
        }

        public void LoadSpritesIfMissing()
        {
#if UNITY_EDITOR
            if (animationFrames == null || animationFrames.Length == 0)
            {
                var list = new List<Sprite>();
                for (int i = 0; i < 6; i++)
                {
                    var sp = UnityEditor.AssetDatabase.LoadAssetAtPath<Sprite>($"Assets/mobs/zombie_{i}.png");
                    if (sp == null) sp = UnityEditor.AssetDatabase.LoadAssetAtPath<Sprite>($"Assets/Sprites/Mobs/zombie_{i}.png");
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
            if (_jumpTimer > 0f) _jumpTimer -= dt;

            if (_targetPlayer == null || _targetPlayer.IsDead)
            {
                _rb.linearVelocity = new Vector2(0f, _rb.linearVelocity.y);
                return;
            }

            Vector2 playerPos = _targetPlayer.transform.position;
            float dist = Vector2.Distance(transform.position, playerPos);
            if (dist > aggroRadius)
            {
                _rb.linearVelocity = new Vector2(0f, _rb.linearVelocity.y);
                return;
            }

            float dirX = (playerPos.x > transform.position.x) ? 1f : -1f;
            _facingRight = dirX > 0;

            // Move horizontally toward player
            _rb.linearVelocity = new Vector2(dirX * moveSpeed, _rb.linearVelocity.y);

            // Obstacle jump check: raycast forward at waist height
            if (_jumpTimer <= 0f)
            {
                Vector2 forwardOrigin = (Vector2)transform.position + new Vector2(dirX * 0.4f, 0.3f);
                RaycastHit2D wallHit = Physics2D.Raycast(forwardOrigin, Vector2.right * dirX, 0.45f, ~0);

                if (wallHit.collider != null && wallHit.collider != _collider && !wallHit.collider.isTrigger && !wallHit.collider.transform.IsChildOf(transform))
                {
                    // If wall is in front, jump over it
                    _rb.linearVelocity = new Vector2(_rb.linearVelocity.x, obstacleJumpForce);
                    _jumpTimer = jumpCooldown;
                }
            }
        }
    }
}
