using System;
using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using Potaria.Data;

namespace Potaria.World
{
    /// <summary>
    /// Boundless procedural chunk streaming and world interaction manager.
    /// Manages chunk generation, asynchronous loading, memory caching, view-distance culling,
    /// block destruction / harvesting, and 4-block horizontal water hydration.
    /// </summary>
    public class ChunkManager : MonoBehaviour
    {
        [Header("Configuration")]
        [SerializeField] private int seed = 12345;
        [SerializeField] private int viewDistanceChunks = 3;
        [SerializeField] private Transform streamingTarget;

        [Header("System Dependencies")]
        [SerializeField] private WorldTilemaps tilemaps;
        [SerializeField] private TileDatabase database;

        private WorldGenerator _generator;
        private readonly Dictionary<int, ChunkData> _loadedChunks = new Dictionary<int, ChunkData>();
        private readonly Dictionary<Vector2Int, int> _tileDamageMap = new Dictionary<Vector2Int, int>();
        private int _lastCenterChunkX = int.MinValue;
        private bool _isStreaming;

        public int Seed => seed;
        public int ViewDistanceChunks { get => viewDistanceChunks; set => viewDistanceChunks = value; }
        public WorldTilemaps Tilemaps { get => tilemaps; set => tilemaps = value; }
        public TileDatabase Database { get => database; set => database = value; }
        public IReadOnlyDictionary<int, ChunkData> LoadedChunks => _loadedChunks;

        private void Awake()
        {
            if (seed == 0) seed = UnityEngine.Random.Range(100000, 99999999);
            _generator = new WorldGenerator(seed);

            if (database == null) database = TileDatabase.Instance;
            if (tilemaps == null) tilemaps = GetComponent<WorldTilemaps>();
            if (tilemaps == null) tilemaps = FindAnyObjectByType<WorldTilemaps>();
        }

        private void Start()
        {
            if (streamingTarget == null)
            {
                var cam = Camera.main;
                if (cam != null) streamingTarget = cam.transform;
            }

            // Immediately load initial chunk corridor around spawn
            UpdateStreaming(true);
        }

        private void Update()
        {
            if (streamingTarget == null) return;

            int currentChunkX = WorldPosToChunkX(streamingTarget.position.x);
            if (currentChunkX != _lastCenterChunkX && !_isStreaming)
            {
                StartCoroutine(StreamChunksCoroutine(currentChunkX));
            }
        }

        public int WorldPosToChunkX(float worldX)
        {
            return Mathf.FloorToInt(worldX / ChunkData.Width);
        }

        /// <summary>
        /// Updates chunk streaming synchronously (used during initialization or tests).
        /// </summary>
        public void UpdateStreaming(bool forceReload = false)
        {
            if (tilemaps == null || database == null)
            {
                if (database == null) database = TileDatabase.Instance;
                if (tilemaps == null) tilemaps = GetComponent<WorldTilemaps>();
                if (tilemaps == null) tilemaps = FindAnyObjectByType<WorldTilemaps>();
            }

            int centerChunkX = 0;
            if (streamingTarget != null)
                centerChunkX = WorldPosToChunkX(streamingTarget.position.x);

            _lastCenterChunkX = centerChunkX;

            int minChunk = centerChunkX - viewDistanceChunks;
            int maxChunk = centerChunkX + viewDistanceChunks;

            // Load and paint required chunks
            for (int cx = minChunk; cx <= maxChunk; cx++)
            {
                var chunk = GetOrCreateChunk(cx);
                if (forceReload || !chunk.IsPainted)
                {
                    tilemaps.PaintChunk(chunk, database);
                }
            }

            // Cull distant chunks
            CullDistantChunks(minChunk, maxChunk);
        }

        private IEnumerator StreamChunksCoroutine(int centerChunkX)
        {
            _isStreaming = true;
            _lastCenterChunkX = centerChunkX;

            int minChunk = centerChunkX - viewDistanceChunks;
            int maxChunk = centerChunkX + viewDistanceChunks;

            // 1. Generate / load missing chunks one per frame to guarantee 60+ FPS
            for (int cx = minChunk; cx <= maxChunk; cx++)
            {
                var chunk = GetOrCreateChunk(cx);
                if (!chunk.IsPainted)
                {
                    tilemaps.PaintChunk(chunk, database);
                    yield return null;
                }
            }

            // 2. Cull distant chunks
            CullDistantChunks(minChunk, maxChunk);
            _isStreaming = false;
        }

        private void CullDistantChunks(int minActiveChunk, int maxActiveChunk)
        {
            var toUnload = new List<int>();
            foreach (var kvp in _loadedChunks)
            {
                int cx = kvp.Key;
                // Keep a 1-chunk buffer beyond view distance before clearing geometry
                if (cx < minActiveChunk - 1 || cx > maxActiveChunk + 1)
                {
                    toUnload.Add(cx);
                }
            }

            foreach (int cx in toUnload)
            {
                if (_loadedChunks.TryGetValue(cx, out var chunk))
                {
                    if (tilemaps != null)
                    {
                        tilemaps.ClearChunk(cx);
                    }
                    chunk.IsPainted = false;
                }
            }
        }

        public ChunkData GetOrCreateChunk(int chunkX)
        {
            if (_loadedChunks.TryGetValue(chunkX, out var existing))
                return existing;

            if (_generator == null) _generator = new WorldGenerator(seed);
            var newChunk = _generator.GenerateChunk(chunkX);
            _loadedChunks[chunkX] = newChunk;
            return newChunk;
        }

        public ChunkData GetChunk(int chunkX)
        {
            _loadedChunks.TryGetValue(chunkX, out var chunk);
            return chunk;
        }

        // Global Coordinate Tile & Wall APIs
        public int GetTile(int gx, int ty)
        {
            int cx = Mathf.FloorToInt((float)gx / ChunkData.Width);
            int lx = gx - (cx * ChunkData.Width);
            var chunk = GetOrCreateChunk(cx);
            return chunk.GetTile(lx, ty);
        }

        public void SetTile(int gx, int ty, int tileId)
        {
            int cx = Mathf.FloorToInt((float)gx / ChunkData.Width);
            int lx = gx - (cx * ChunkData.Width);
            var chunk = GetOrCreateChunk(cx);
            chunk.SetTile(lx, ty, tileId);

            if (tilemaps != null && database != null)
            {
                tilemaps.SetTileAt(gx, ty, tileId, database);
            }
        }

        public int GetWall(int gx, int ty)
        {
            int cx = Mathf.FloorToInt((float)gx / ChunkData.Width);
            int lx = gx - (cx * ChunkData.Width);
            var chunk = GetOrCreateChunk(cx);
            return chunk.GetWall(lx, ty);
        }

        public void SetWall(int gx, int ty, int wallId)
        {
            int cx = Mathf.FloorToInt((float)gx / ChunkData.Width);
            int lx = gx - (cx * ChunkData.Width);
            var chunk = GetOrCreateChunk(cx);
            chunk.SetWall(lx, ty, wallId);

            if (tilemaps != null && database != null)
            {
                tilemaps.SetWallAt(gx, ty, wallId, database);
            }
        }

        /// <summary>
        /// Mines or damages a tile at (gx, ty).
        /// Returns true if the tile broke, setting droppedItem if one was dropped.
        /// </summary>
        public bool DamageTile(int gx, int ty, int damageAmount, ToolType tool, int toolPower, out ItemData droppedItem)
        {
            droppedItem = null;
            int tid = GetTile(gx, ty);
            if (tid == WorldConstants.TileAir) return false;

            if (database == null) database = TileDatabase.Instance;
            if (database == null) return false;
            var def = database.GetTile(tid);
            if (def == null || def.IsIndestructible || def.Hardness <= 0) return false;

            int effectiveDamage = def.CalculateDamage(tool, toolPower > 0 ? toolPower : damageAmount);
            var posKey = new Vector2Int(gx, ty);

            int currentDamage = _tileDamageMap.TryGetValue(posKey, out int d) ? d : 0;
            currentDamage += effectiveDamage;

            if (currentDamage >= def.Hardness)
            {
                // Tile broken!
                _tileDamageMap.Remove(posKey);
                droppedItem = def.MinedDrop;
                SetTile(gx, ty, WorldConstants.TileAir);
                return true;
            }
            else
            {
                _tileDamageMap[posKey] = currentDamage;
                return false;
            }
        }

        /// <summary>
        /// 4-block horizontal water hydration simulation for farmland.
        /// If liquid water exists within 4 blocks horizontally, hydrates dry farmland into wet farmland.
        /// </summary>
        public bool SimulateFarmlandHydration(int gx, int ty)
        {
            int currentTile = GetTile(gx, ty);
            if (currentTile != WorldConstants.TileFarmland && currentTile != WorldConstants.TileFarmlandWet)
                return false;

            bool isHydrated = false;
            for (int dx = -4; dx <= 4; dx++)
            {
                if (dx == 0) continue;
                for (int dy = -1; dy <= 1; dy++)
                {
                    if (GetTile(gx + dx, ty + dy) == WorldConstants.TileWater)
                    {
                        isHydrated = true;
                        break;
                    }
                }
                if (isHydrated) break;
            }

            int targetTile = isHydrated ? WorldConstants.TileFarmlandWet : WorldConstants.TileFarmland;
            if (currentTile != targetTile)
            {
                SetTile(gx, ty, targetTile);
                return true;
            }
            return false;
        }
    }
}
