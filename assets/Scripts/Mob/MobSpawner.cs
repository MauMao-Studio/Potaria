using System;
using System.Collections.Generic;
using UnityEngine;
using Potaria.Player;
using Potaria.World.Lighting;

namespace Potaria.Mob
{
    /// <summary>
    /// Dynamic Mob Spawner for Potaria:
    /// - Spawns hostile mobs in a 15 to 35 tile annulus around the player
    /// - Surface ground detection for Green Slimes, Purple Slimes, and Zombies
    /// - Night sky aerial spawning for Night Gazers (Demon Eyes) during Night phase
    /// - Active mob cap enforcement (default: 10 mobs)
    /// - Automatic distance-based despawning (>60 tiles)
    /// </summary>
    public class MobSpawner : MonoBehaviour
    {
        [Header("References")]
        [SerializeField] private PlayerController player;
        [SerializeField] private DayNightCycle2D dayNight;

        [Header("Spawn Settings")]
        [SerializeField] private int maxActiveMobs = 10;
        [SerializeField] private float spawnInterval = 3.5f;
        [SerializeField] private float minSpawnRadius = 15f;
        [SerializeField] private float maxSpawnRadius = 35f;
        [SerializeField] private float despawnDistance = 60f;
        [SerializeField] private LayerMask groundLayerMask = ~0;

        private readonly List<Mob> _activeMobs = new List<Mob>();
        private float _spawnTimer = 1.0f;

        public int ActiveMobCount => _activeMobs.Count;
        public int MaxActiveMobs { get => maxActiveMobs; set => maxActiveMobs = value; }

        private void Awake()
        {
            if (player == null) player = FindFirstObjectByType<PlayerController>();
            if (dayNight == null) dayNight = FindFirstObjectByType<DayNightCycle2D>();
        }

        private void Start()
        {
            if (player == null) player = FindFirstObjectByType<PlayerController>();
            if (dayNight == null) dayNight = FindFirstObjectByType<DayNightCycle2D>();

            // Spawn starting mob pack around player
            SpawnInitialMobs();
        }

        public void SpawnInitialMobs()
        {
            if (player == null) return;
            Vector2 p = player.transform.position;

            // Spawn 1 green slime, 1 purple slime, 1 surface zombie within visible range
            SpawnMobAt(typeof(SlimeMob), p + new Vector2(8f, 2f), SlimeMob.SlimeType.Green);
            SpawnMobAt(typeof(SlimeMob), p + new Vector2(-10f, 2f), SlimeMob.SlimeType.Purple);
            SpawnMobAt(typeof(ZombieMob), p + new Vector2(14f, 2f));
        }

        private void Update()
        {
            CleanDeadOrDistantMobs();

            _spawnTimer -= Time.deltaTime;
            if (_spawnTimer <= 0f)
            {
                _spawnTimer = spawnInterval;
                TrySpawnRandomMob();
            }
        }

        private void CleanDeadOrDistantMobs()
        {
            if (player == null) player = FindFirstObjectByType<PlayerController>();
            Vector2 playerPos = (player != null) ? (Vector2)player.transform.position : Vector2.zero;

            for (int i = _activeMobs.Count - 1; i >= 0; i--)
            {
                var mob = _activeMobs[i];
                if (mob == null || mob.IsDead)
                {
                    _activeMobs.RemoveAt(i);
                    continue;
                }

                if (Vector2.Distance(mob.transform.position, playerPos) > despawnDistance)
                {
                    if (Application.isPlaying)
                        Destroy(mob.gameObject);
                    else
                        DestroyImmediate(mob.gameObject);
                    _activeMobs.RemoveAt(i);
                }
            }
        }

        public Mob TrySpawnRandomMob()
        {
            if (_activeMobs.Count >= maxActiveMobs) return null;
            if (player == null) player = FindFirstObjectByType<PlayerController>();
            if (player == null) return null;

            if (dayNight == null) dayNight = FindFirstObjectByType<DayNightCycle2D>();
            bool isNight = (dayNight != null && dayNight.IsNight);

            Vector2 playerPos = player.transform.position;
            float angle = UnityEngine.Random.Range(0f, Mathf.PI * 2f);
            float dist = UnityEngine.Random.Range(minSpawnRadius, maxSpawnRadius);
            float offsetX = Mathf.Cos(angle) * dist;

            // Night gazer spawns in the air at night
            if (isNight && UnityEngine.Random.value < 0.40f)
            {
                Vector2 airPos = playerPos + new Vector2(offsetX, UnityEngine.Random.Range(8f, 18f));
                return SpawnMobAt(typeof(DemonEyeMob), airPos);
            }

            // Ground mobs: Raycast downward from above to find solid ground
            Vector2 rayOrigin = new Vector2(playerPos.x + offsetX, playerPos.y + 20f);
            RaycastHit2D hit = Physics2D.Raycast(rayOrigin, Vector2.down, 45f, groundLayerMask);

            if (hit.collider != null && !hit.collider.isTrigger)
            {
                Vector2 groundPos = hit.point + new Vector2(0f, 0.75f);
                float roll = UnityEngine.Random.value;
                if (roll < 0.45f)
                {
                    return SpawnMobAt(typeof(SlimeMob), groundPos, SlimeMob.SlimeType.Green);
                }
                else if (roll < 0.70f)
                {
                    return SpawnMobAt(typeof(SlimeMob), groundPos, SlimeMob.SlimeType.Purple);
                }
                else
                {
                    return SpawnMobAt(typeof(ZombieMob), groundPos);
                }
            }

            return null;
        }

        public Mob SpawnMobAt(Type mobType, Vector2 position, SlimeMob.SlimeType slimeType = SlimeMob.SlimeType.Green)
        {
            string objName = mobType.Name;
            var go = new GameObject(objName);
            go.transform.position = position;

            var rb = go.AddComponent<Rigidbody2D>();
            var col = go.AddComponent<BoxCollider2D>();
            col.size = new Vector2(0.85f, 0.85f);
            col.offset = new Vector2(0f, 0.425f);

            var sr = go.AddComponent<SpriteRenderer>();
            sr.sortingLayerName = "Foreground";
            sr.sortingOrder = 10;

            Mob mob = null;
            if (mobType == typeof(SlimeMob))
            {
                var slime = go.AddComponent<SlimeMob>();
                slime.ConfigureVariant(slimeType);
                slime.LoadSpritesIfMissing();
                mob = slime;
            }
            else if (mobType == typeof(ZombieMob))
            {
                col.size = new Vector2(0.8f, 1.4f);
                col.offset = new Vector2(0f, 0.7f);
                var zombie = go.AddComponent<ZombieMob>();
                zombie.LoadSpritesIfMissing();
                mob = zombie;
            }
            else if (mobType == typeof(DemonEyeMob))
            {
                col.size = new Vector2(0.9f, 0.7f);
                col.offset = new Vector2(0f, 0.35f);
                var eye = go.AddComponent<DemonEyeMob>();
                eye.LoadSpritesIfMissing();
                mob = eye;
            }

            if (mob != null)
            {
                _activeMobs.Add(mob);
            }

            return mob;
        }

        public void ClearAllMobs()
        {
            foreach (var mob in _activeMobs)
            {
                if (mob != null)
                {
                    if (Application.isPlaying)
                        Destroy(mob.gameObject);
                    else
                        DestroyImmediate(mob.gameObject);
                }
            }
            _activeMobs.Clear();
        }
    }
}
