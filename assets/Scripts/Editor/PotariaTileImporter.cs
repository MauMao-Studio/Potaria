using System;
using System.Collections.Generic;
using System.IO;
using UnityEditor;
using UnityEngine;
using UnityEngine.Tilemaps;
using Potaria.Data;
using Potaria.World;

namespace Potaria.Editor
{
    /// <summary>
    /// Automated Editor pipeline that creates Unity Tile assets for all blocks and walls,
    /// links them to their ItemData drops and mining metadata, and constructs the master TileDatabase asset.
    /// Can be executed via batchmode with Potaria.Editor.PotariaTileImporter.GenerateAllTileAssets.
    /// </summary>
    public static class PotariaTileImporter
    {
        private const string TILES_SPRITE_PATH = "Assets/Sprites/Tiles";
        private const string WALLS_SPRITE_PATH = "Assets/Sprites/Walls";
        private const string TILES_ASSET_PATH = "Assets/ScriptableObjects/Tiles";
        private const string WALLS_ASSET_PATH = "Assets/ScriptableObjects/Walls";
        private const string DATABASE_ASSET_PATH = "Assets/ScriptableObjects/TileDatabase.asset";
        private const string MATERIALS_PATH = "Assets/ScriptableObjects/Items/Materials";

        [MenuItem("Potaria/Generate Tile and Wall Assets", priority = 10)]
        public static void GenerateAllTileAssets()
        {
            Debug.Log("[PotariaTileImporter] Starting Tile & Wall Assets Pipeline...");

            EnsureDirectory(TILES_ASSET_PATH);
            EnsureDirectory(WALLS_ASSET_PATH);
            EnsureDirectory("Assets/Resources");

            // 1. Load or Create TileDatabase ScriptableObject
            var db = AssetDatabase.LoadAssetAtPath<TileDatabase>(DATABASE_ASSET_PATH);
            if (db == null)
            {
                db = ScriptableObject.CreateInstance<TileDatabase>();
                AssetDatabase.CreateAsset(db, DATABASE_ASSET_PATH);
            }

            db.InitializeDefaults();

            // 2. Build ItemData Material Cache
            var itemCache = new Dictionary<string, ItemData>(StringComparer.OrdinalIgnoreCase);
            var itemGuids = AssetDatabase.FindAssets("t:ItemData", new[] { MATERIALS_PATH, "Assets/ScriptableObjects/Items" });
            foreach (var guid in itemGuids)
            {
                var path = AssetDatabase.GUIDToAssetPath(guid);
                var item = AssetDatabase.LoadAssetAtPath<ItemData>(path);
                if (item != null && !string.IsNullOrEmpty(item.ItemId))
                {
                    itemCache[item.ItemId] = item;
                }
            }

            // 3. Generate Block Tile Assets
            int blocksCreated = 0;
            foreach (var def in db.TileDefinitions)
            {
                if (def == null || def.TileId == WorldConstants.TileAir) continue;

                // Find Sprite
                string spritePath = $"{TILES_SPRITE_PATH}/tile_{def.TileId}.png";
                var sprite = AssetDatabase.LoadAssetAtPath<Sprite>(spritePath);
                if (sprite == null)
                {
                    // Check fallback names
                    if (def.TileId == WorldConstants.TileWoodTrunk)
                        sprite = AssetDatabase.LoadAssetAtPath<Sprite>($"{TILES_SPRITE_PATH}/tile_trunk_base.png");
                    else if (def.TileId == WorldConstants.TileSaplingOak)
                        sprite = AssetDatabase.LoadAssetAtPath<Sprite>($"{TILES_SPRITE_PATH}/tile_sapling_frames_0.png");
                    else if (def.TileId == WorldConstants.TileWater)
                        sprite = AssetDatabase.LoadAssetAtPath<Sprite>($"{TILES_SPRITE_PATH}/tile_water_frames_0.png");
                }

                if (sprite != null)
                {
                    string tileAssetPath = $"{TILES_ASSET_PATH}/Tile_{def.TileId}.asset";
                    var tile = AssetDatabase.LoadAssetAtPath<Tile>(tileAssetPath);
                    if (tile == null)
                    {
                        tile = ScriptableObject.CreateInstance<Tile>();
                        tile.name = $"Tile_{def.TileId}";
                        tile.sprite = sprite;
                        tile.colliderType = (def.IsSolid || def.IsPlatform) ? Tile.ColliderType.Grid : Tile.ColliderType.None;
                        AssetDatabase.CreateAsset(tile, tileAssetPath);
                    }
                    else
                    {
                        tile.sprite = sprite;
                        tile.colliderType = (def.IsSolid || def.IsPlatform) ? Tile.ColliderType.Grid : Tile.ColliderType.None;
                        EditorUtility.SetDirty(tile);
                    }
                    def.UnityTile = tile;
                    blocksCreated++;
                }

                // Link mined drop ItemData
                if (!string.IsNullOrEmpty(def.DropItemId) && itemCache.TryGetValue(def.DropItemId, out var dropItem))
                {
                    def.MinedDrop = dropItem;
                }
            }

            // 4. Generate Wall Tile Assets
            int wallsCreated = 0;
            foreach (var def in db.WallDefinitions)
            {
                if (def == null || def.TileId == WorldConstants.WallAir) continue;

                string spritePath = $"{WALLS_SPRITE_PATH}/wall_{def.TileId}.png";
                var sprite = AssetDatabase.LoadAssetAtPath<Sprite>(spritePath);
                if (sprite != null)
                {
                    string wallAssetPath = $"{WALLS_ASSET_PATH}/Wall_{def.TileId}.asset";
                    var tile = AssetDatabase.LoadAssetAtPath<Tile>(wallAssetPath);
                    if (tile == null)
                    {
                        tile = ScriptableObject.CreateInstance<Tile>();
                        tile.name = $"Wall_{def.TileId}";
                        tile.sprite = sprite;
                        tile.colliderType = Tile.ColliderType.None; // Walls are non-solid
                        AssetDatabase.CreateAsset(tile, wallAssetPath);
                    }
                    else
                    {
                        tile.sprite = sprite;
                        tile.colliderType = Tile.ColliderType.None;
                        EditorUtility.SetDirty(tile);
                    }
                    def.UnityTile = tile;
                    wallsCreated++;
                }

                if (!string.IsNullOrEmpty(def.DropItemId) && itemCache.TryGetValue(def.DropItemId, out var dropItem))
                {
                    def.MinedDrop = dropItem;
                }
            }

            // 5. Also save copy into Resources for runtime singleton access
            string resDbPath = "Assets/Resources/TileDatabase.asset";
            if (File.Exists(resDbPath))
            {
                AssetDatabase.DeleteAsset(resDbPath);
            }
            AssetDatabase.CopyAsset(DATABASE_ASSET_PATH, resDbPath);

            EditorUtility.SetDirty(db);
            AssetDatabase.SaveAssets();
            AssetDatabase.Refresh();

            TileDatabase.Instance = db;
            db.Initialize();

            Debug.Log($"[PotariaTileImporter] Completed! Generated {blocksCreated} block tiles and {wallsCreated} wall tiles with linked ItemData and TileDatabase.");
        }

        private static void EnsureDirectory(string path)
        {
            if (!Directory.Exists(path))
            {
                Directory.CreateDirectory(path);
                AssetDatabase.Refresh();
            }
        }
    }
}
