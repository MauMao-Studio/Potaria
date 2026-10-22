using System;
using System.Collections.Generic;
using UnityEngine;

namespace Potaria.World
{
    /// <summary>
    /// In-memory representation of a single 16x240 tile column chunk.
    /// Manages foreground blocks, background walls, sky stratum blocks, and biome metadata.
    /// </summary>
    [Serializable]
    public class ChunkData
    {
        public const int Width = WorldConstants.ChunkWidth;
        public const int Height = WorldConstants.ChunkHeight;

        private readonly int _chunkX;
        private readonly int _seed;

        // 2D grid arrays: [localX (0..15), localY (0..239)]
        private readonly int[,] _tiles;
        private readonly int[,] _walls;

        // Sparse dictionaries for negative Y coordinates (Sky citadel, celestial stratum)
        private readonly Dictionary<Vector2Int, int> _skyTiles;
        private readonly Dictionary<Vector2Int, int> _skyWalls;

        // Per-column metadata
        private readonly int[] _surfaceHeights;
        private readonly string[] _colBiomes;

        private bool _isModified;
        private bool _isPainted;

        public int ChunkX => _chunkX;
        public int Seed => _seed;
        public int[] SurfaceHeights => _surfaceHeights;
        public string[] ColBiomes => _colBiomes;
        public bool IsModified { get => _isModified; set => _isModified = value; }
        public bool IsPainted { get => _isPainted; set => _isPainted = value; }

        public ChunkData(int chunkX, int seed)
        {
            _chunkX = chunkX;
            _seed = seed;
            _tiles = new int[Width, Height];
            _walls = new int[Width, Height];
            _skyTiles = new Dictionary<Vector2Int, int>();
            _skyWalls = new Dictionary<Vector2Int, int>();
            _surfaceHeights = new int[Width];
            _colBiomes = new string[Width];
            _isModified = false;
            _isPainted = false;
        }

        public int GetTile(int lx, int ty)
        {
            if (lx < 0 || lx >= Width) return WorldConstants.TileAir;
            if (ty < 0)
            {
                var key = new Vector2Int(lx, ty);
                return _skyTiles.TryGetValue(key, out int tid) ? tid : WorldConstants.TileAir;
            }
            if (ty >= Height)
            {
                return WorldConstants.TileBedrock;
            }
            return _tiles[lx, ty];
        }

        public void SetTile(int lx, int ty, int tileId)
        {
            if (lx < 0 || lx >= Width) return;
            if (ty < 0)
            {
                var key = new Vector2Int(lx, ty);
                if (tileId == WorldConstants.TileAir) _skyTiles.Remove(key);
                else _skyTiles[key] = tileId;
                _isModified = true;
                return;
            }
            if (ty < Height)
            {
                if (_tiles[lx, ty] != tileId)
                {
                    _tiles[lx, ty] = tileId;
                    _isModified = true;
                }
            }
        }

        public int GetWall(int lx, int ty)
        {
            if (lx < 0 || lx >= Width) return WorldConstants.WallAir;
            if (ty < 0)
            {
                var key = new Vector2Int(lx, ty);
                return _skyWalls.TryGetValue(key, out int wid) ? wid : WorldConstants.WallAir;
            }
            if (ty >= Height)
            {
                return WorldConstants.WallAir;
            }
            return _walls[lx, ty];
        }

        public void SetWall(int lx, int ty, int wallId)
        {
            if (lx < 0 || lx >= Width) return;
            if (ty < 0)
            {
                var key = new Vector2Int(lx, ty);
                if (wallId == WorldConstants.WallAir) _skyWalls.Remove(key);
                else _skyWalls[key] = wallId;
                _isModified = true;
                return;
            }
            if (ty < Height)
            {
                if (_walls[lx, ty] != wallId)
                {
                    _walls[lx, ty] = wallId;
                    _isModified = true;
                }
            }
        }

        public Dictionary<Vector2Int, int> GetSkyTiles() => _skyTiles;
        public Dictionary<Vector2Int, int> GetSkyWalls() => _skyWalls;
    }
}
