using System;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.Tilemaps;

namespace Potaria.World
{
    /// <summary>
    /// Dual-Tilemap Architecture coordinator for Potaria.
    /// Manages the Grid hierarchy, Foreground solid terrain with CompositeCollider2D,
    /// Background ambient walls with atmospheric dimming, and one-way platform mechanics.
    /// </summary>
    [RequireComponent(typeof(Grid))]
    public class WorldTilemaps : MonoBehaviour
    {
        [Header("Tilemap Layer References")]
        [SerializeField] private Tilemap foregroundTilemap;
        [SerializeField] private Tilemap backgroundTilemap;
        [SerializeField] private Tilemap platformTilemap;
        [SerializeField] private Tilemap waterTilemap;

        [Header("Composite Physics")]
        [SerializeField] private TilemapCollider2D foregroundCollider;
        [SerializeField] private CompositeCollider2D compositeCollider;
        [SerializeField] private Rigidbody2D staticRigidbody;

        [Header("Renderers")]
        [SerializeField] private TilemapRenderer foregroundRenderer;
        [SerializeField] private TilemapRenderer backgroundRenderer;

        private Grid _grid;

        public Grid GridComponent
        {
            get
            {
                if (_grid == null) _grid = GetComponent<Grid>();
                return _grid;
            }
        }

        public Tilemap ForegroundTilemap => foregroundTilemap;
        public Tilemap BackgroundTilemap => backgroundTilemap;
        public Tilemap PlatformTilemap => platformTilemap;
        public Tilemap WaterTilemap => waterTilemap;
        public CompositeCollider2D CompositeCollider => compositeCollider;

        private void Awake()
        {
            _grid = GetComponent<Grid>();
            ValidateOrBuildLayers();
        }

        /// <summary>
        /// Validates or creates child Tilemaps and verifies CompositeCollider2D configuration.
        /// </summary>
        public void ValidateOrBuildLayers()
        {
            if (_grid == null) _grid = GetComponent<Grid>();

            // 1. Background Tilemap
            if (backgroundTilemap == null)
            {
                var bgObj = transform.Find("Background_Tilemap");
                if (bgObj == null)
                {
                    var newBg = new GameObject("Background_Tilemap");
                    newBg.transform.SetParent(transform, false);
                    bgObj = newBg.transform;
                }
                backgroundTilemap = GetOrAddComponent<Tilemap>(bgObj.gameObject);
            }
            if (backgroundRenderer == null && backgroundTilemap != null)
            {
                backgroundRenderer = GetOrAddComponent<TilemapRenderer>(backgroundTilemap.gameObject);
                SetSortingLayerSafe(backgroundRenderer, "Background", -10);
                backgroundTilemap.color = new Color(0.6f, 0.6f, 0.65f, 1.0f);
            }

            // 2. Foreground Tilemap (Solid Terrain)
            if (foregroundTilemap == null)
            {
                var fgObj = transform.Find("Foreground_Tilemap");
                if (fgObj == null)
                {
                    var newFg = new GameObject("Foreground_Tilemap");
                    newFg.transform.SetParent(transform, false);
                    fgObj = newFg.transform;
                }
                foregroundTilemap = GetOrAddComponent<Tilemap>(fgObj.gameObject);
            }
            if (foregroundRenderer == null && foregroundTilemap != null)
            {
                foregroundRenderer = GetOrAddComponent<TilemapRenderer>(foregroundTilemap.gameObject);
                SetSortingLayerSafe(foregroundRenderer, "Foreground", 0);
            }

            // 3. Configure CompositeCollider2D on Foreground Tilemap
            if (foregroundTilemap != null)
            {
                if (foregroundCollider == null)
                    foregroundCollider = GetOrAddComponent<TilemapCollider2D>(foregroundTilemap.gameObject);
#pragma warning disable CS0618
                foregroundCollider.usedByComposite = true;
#pragma warning restore CS0618
                foregroundCollider.compositeOperation = Collider2D.CompositeOperation.Merge;

                if (staticRigidbody == null)
                {
                    staticRigidbody = GetOrAddComponent<Rigidbody2D>(foregroundTilemap.gameObject);
                    staticRigidbody.bodyType = RigidbodyType2D.Static;
                }

                if (compositeCollider == null)
                {
                    compositeCollider = GetOrAddComponent<CompositeCollider2D>(foregroundTilemap.gameObject);
                    compositeCollider.geometryType = CompositeCollider2D.GeometryType.Polygons;
                }
            }

            // 4. Platform Tilemap (One-way jump-through platforms)
            if (platformTilemap == null)
            {
                var platObj = transform.Find("Platform_Tilemap");
                if (platObj == null)
                {
                    var newPlat = new GameObject("Platform_Tilemap");
                    newPlat.transform.SetParent(transform, false);
                    platObj = newPlat.transform;
                }
                platformTilemap = GetOrAddComponent<Tilemap>(platObj.gameObject);
                var platRenderer = GetOrAddComponent<TilemapRenderer>(platObj.gameObject);
                SetSortingLayerSafe(platRenderer, "Foreground", 1);

                var platCollider = GetOrAddComponent<TilemapCollider2D>(platObj.gameObject);
                platCollider.usedByEffector = true;

                var effector = GetOrAddComponent<PlatformEffector2D>(platObj.gameObject);
                effector.useOneWay = true;
                effector.useOneWayGrouping = true;
            }

            // 5. Water Tilemap (Liquid surfaces)
            if (waterTilemap == null)
            {
                var waterObj = transform.Find("Water_Tilemap");
                if (waterObj == null)
                {
                    var newWater = new GameObject("Water_Tilemap");
                    newWater.transform.SetParent(transform, false);
                    waterObj = newWater.transform;
                }
                waterTilemap = GetOrAddComponent<Tilemap>(waterObj.gameObject);
                var waterRenderer = GetOrAddComponent<TilemapRenderer>(waterObj.gameObject);
                SetSortingLayerSafe(waterRenderer, "Foreground", 5);
                waterTilemap.color = new Color(0.3f, 0.6f, 0.95f, 0.75f);
            }
        }

        private static T GetOrAddComponent<T>(GameObject go) where T : Component
        {
            var comp = go.GetComponent<T>();
            if (comp == null) comp = go.AddComponent<T>();
            return comp;
        }

        private static void SetSortingLayerSafe(Renderer renderer, string layerName, int order)
        {
            if (renderer == null) return;
            try
            {
                renderer.sortingLayerName = layerName;
            }
            catch
            {
                // Fallback to Default sorting layer if specific layer is not yet registered
                renderer.sortingLayerName = "Default";
            }
            renderer.sortingOrder = order;
        }

        // Coordinate Conversion Helpers
        public Vector3Int GridToCell(int gx, int ty)
        {
            // Unity 2D coordinates: Y is positive up, sky is positive Y, bedrock is negative Y
            return new Vector3Int(gx, -ty, 0);
        }

        public void CellToGrid(Vector3Int cell, out int gx, out int ty)
        {
            gx = cell.x;
            ty = -cell.y;
        }

        public Vector3Int WorldToCell(Vector3 worldPos)
        {
            return GridComponent.WorldToCell(worldPos);
        }

        public Vector3 CellToWorld(Vector3Int cellPos)
        {
            return GridComponent.CellToWorld(cellPos);
        }

        /// <summary>
        /// Paints an entire ChunkData model into the respective Foreground, Background, and Platform tilemaps.
        /// </summary>
        public void PaintChunk(ChunkData chunk, TileDatabase database)
        {
            if (chunk == null || database == null) return;
            ValidateOrBuildLayers();

            int chunkX = chunk.ChunkX;
            int width = ChunkData.Width;
            int height = ChunkData.Height;

            // Arrays for bulk block writing
            var fgPositions = new List<Vector3Int>(width * height);
            var fgTiles = new List<TileBase>(width * height);

            var bgPositions = new List<Vector3Int>(width * height);
            var bgTiles = new List<TileBase>(width * height);

            var platPositions = new List<Vector3Int>();
            var platTiles = new List<TileBase>();

            var waterPositions = new List<Vector3Int>();
            var waterTiles = new List<TileBase>();

            for (int lx = 0; lx < width; lx++)
            {
                int gx = chunkX * width + lx;
                for (int ty = 0; ty < height; ty++)
                {
                    var cell = GridToCell(gx, ty);
                    int tid = chunk.GetTile(lx, ty);
                    int wid = chunk.GetWall(lx, ty);

                    // Background Wall
                    if (wid != WorldConstants.WallAir)
                    {
                        var wallBase = database.GetWallBase(wid);
                        if (wallBase != null)
                        {
                            bgPositions.Add(cell);
                            bgTiles.Add(wallBase);
                        }
                    }

                    // Foreground Block
                    if (tid != WorldConstants.TileAir)
                    {
                        var tileDef = database.GetTile(tid);
                        var tileBase = database.GetTileBase(tid);
                        if (tileBase != null)
                        {
                            if (tileDef.IsLiquid)
                            {
                                waterPositions.Add(cell);
                                waterTiles.Add(tileBase);
                            }
                            else if (tileDef.IsPlatform)
                            {
                                platPositions.Add(cell);
                                platTiles.Add(tileBase);
                            }
                            else
                            {
                                fgPositions.Add(cell);
                                fgTiles.Add(tileBase);
                            }
                        }
                    }
                }
            }

            // Also check sky stratum tiles (y < 0)
            foreach (var kvp in chunk.GetSkyTiles())
            {
                int gx = chunkX * width + kvp.Key.x;
                int ty = kvp.Key.y;
                var cell = GridToCell(gx, ty);
                var tileDef = database.GetTile(kvp.Value);
                var tileBase = database.GetTileBase(kvp.Value);
                if (tileBase != null)
                {
                    if (tileDef.IsPlatform)
                    {
                        platPositions.Add(cell);
                        platTiles.Add(tileBase);
                    }
                    else
                    {
                        fgPositions.Add(cell);
                        fgTiles.Add(tileBase);
                    }
                }
            }

            foreach (var kvp in chunk.GetSkyWalls())
            {
                int gx = chunkX * width + kvp.Key.x;
                int ty = kvp.Key.y;
                var cell = GridToCell(gx, ty);
                var wallBase = database.GetWallBase(kvp.Value);
                if (wallBase != null)
                {
                    bgPositions.Add(cell);
                    bgTiles.Add(wallBase);
                }
            }

            // Apply bulk tile arrays
            if (foregroundTilemap != null && fgPositions.Count > 0)
                foregroundTilemap.SetTiles(fgPositions.ToArray(), fgTiles.ToArray());
            if (backgroundTilemap != null && bgPositions.Count > 0)
                backgroundTilemap.SetTiles(bgPositions.ToArray(), bgTiles.ToArray());
            if (platformTilemap != null && platPositions.Count > 0)
                platformTilemap.SetTiles(platPositions.ToArray(), platTiles.ToArray());
            if (waterTilemap != null && waterPositions.Count > 0)
                waterTilemap.SetTiles(waterPositions.ToArray(), waterTiles.ToArray());

            chunk.IsPainted = true;
        }

        /// <summary>
        /// Clears all tiles in a given chunk column from Foreground, Background, and Platform tilemaps.
        /// </summary>
        public void ClearChunk(int chunkX)
        {
            ValidateOrBuildLayers();
            int width = ChunkData.Width;
            int height = ChunkData.Height;

            // Clear ground bounds
            var bounds = new BoundsInt(chunkX * width, -height, 0, width, height + 10, 1);
            // Also include sky stratum bounds
            var skyBounds = new BoundsInt(chunkX * width, 0, 0, width, 250, 1);

            ClearBounds(foregroundTilemap, bounds);
            ClearBounds(foregroundTilemap, skyBounds);

            ClearBounds(backgroundTilemap, bounds);
            ClearBounds(backgroundTilemap, skyBounds);

            ClearBounds(platformTilemap, bounds);
            ClearBounds(platformTilemap, skyBounds);

            ClearBounds(waterTilemap, bounds);
            ClearBounds(waterTilemap, skyBounds);
        }

        private void ClearBounds(Tilemap tilemap, BoundsInt bounds)
        {
            if (tilemap == null) return;
            var empty = new TileBase[bounds.size.x * bounds.size.y];
            tilemap.SetTilesBlock(bounds, empty);
        }

        public void SetTileAt(int gx, int ty, int tileId, TileDatabase database)
        {
            var cell = GridToCell(gx, ty);
            var tileDef = database.GetTile(tileId);
            var tileBase = database.GetTileBase(tileId);

            // Clear previous across layers
            if (foregroundTilemap != null) foregroundTilemap.SetTile(cell, null);
            if (platformTilemap != null) platformTilemap.SetTile(cell, null);
            if (waterTilemap != null) waterTilemap.SetTile(cell, null);

            if (tileId != WorldConstants.TileAir && tileBase != null)
            {
                if (tileDef.IsLiquid && waterTilemap != null)
                    waterTilemap.SetTile(cell, tileBase);
                else if (tileDef.IsPlatform && platformTilemap != null)
                    platformTilemap.SetTile(cell, tileBase);
                else if (foregroundTilemap != null)
                    foregroundTilemap.SetTile(cell, tileBase);
            }
        }

        public void SetWallAt(int gx, int ty, int wallId, TileDatabase database)
        {
            var cell = GridToCell(gx, ty);
            var wallBase = database.GetWallBase(wallId);
            if (backgroundTilemap != null)
            {
                backgroundTilemap.SetTile(cell, wallId == WorldConstants.WallAir ? null : wallBase);
            }
        }
    }
}
