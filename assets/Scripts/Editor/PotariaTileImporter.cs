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

            EnsureProceduralTileSprites();
            EnsureMissingItemData();

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
                    else if (def.TileId == WorldConstants.TileSaplingPalm)
                        sprite = AssetDatabase.LoadAssetAtPath<Sprite>($"{TILES_SPRITE_PATH}/tile_sapling_palm_frames_0.png");
                    else if (def.TileId == WorldConstants.TileSaplingPine)
                        sprite = AssetDatabase.LoadAssetAtPath<Sprite>($"{TILES_SPRITE_PATH}/tile_sapling_pine_frames_0.png");
                    else if (def.TileId == WorldConstants.TileSaplingBlight)
                        sprite = AssetDatabase.LoadAssetAtPath<Sprite>($"{TILES_SPRITE_PATH}/tile_sapling_blight_frames_0.png");
                    else if (def.TileId == WorldConstants.TileLamp)
                        sprite = AssetDatabase.LoadAssetAtPath<Sprite>("Assets/Sprites/Items/brass_lamp.png");
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

        private static void EnsureProceduralTileSprites()
        {
            EnsureDirectory(TILES_SPRITE_PATH);

            CreateTileTextureIfMissing($"{TILES_SPRITE_PATH}/tile_74.png", (tex) =>
            {
                // Farmland (Dry furrowed loam)
                Color dryLoam = new Color(105f / 255f, 70f / 255f, 38f / 255f);
                Color furrowDark = new Color(72f / 255f, 45f / 255f, 22f / 255f);
                Color furrowLight = new Color(135f / 255f, 95f / 255f, 55f / 255f);
                for (int x = 0; x < 16; x++)
                    for (int y = 0; y < 16; y++)
                        tex.SetPixel(x, y, dryLoam);

                int[] furrowY = { 3, 7, 11, 15 };
                foreach (int fy in furrowY)
                {
                    for (int x = 0; x < 16; x++)
                    {
                        tex.SetPixel(x, fy, furrowDark);
                        if (fy > 0) tex.SetPixel(x, fy - 1, furrowLight);
                    }
                }
            });

            CreateTileTextureIfMissing($"{TILES_SPRITE_PATH}/tile_75.png", (tex) =>
            {
                // Farmland Wet (Dark hydrated loam with moisture glints)
                Color wetLoam = new Color(52f / 255f, 34f / 255f, 18f / 255f);
                Color furrowWetDark = new Color(32f / 255f, 18f / 255f, 10f / 255f);
                Color furrowWetLight = new Color(78f / 255f, 56f / 255f, 38f / 255f);
                for (int x = 0; x < 16; x++)
                    for (int y = 0; y < 16; y++)
                        tex.SetPixel(x, y, wetLoam);

                int[] furrowY = { 3, 7, 11, 15 };
                foreach (int fy in furrowY)
                {
                    for (int x = 0; x < 16; x++)
                    {
                        tex.SetPixel(x, fy, furrowWetDark);
                        if (fy > 0) tex.SetPixel(x, fy - 1, furrowWetLight);
                    }
                }
                // Moisture droplet sheen
                tex.SetPixel(3, 2, new Color(95f / 255f, 120f / 255f, 135f / 255f));
                tex.SetPixel(9, 6, new Color(95f / 255f, 120f / 255f, 135f / 255f));
                tex.SetPixel(14, 10, new Color(95f / 255f, 120f / 255f, 135f / 255f));
            });

            CreateTileTextureIfMissing($"{TILES_SPRITE_PATH}/tile_76.png", (tex) =>
            {
                // Crop (Sprout stage)
                for (int x = 0; x < 16; x++)
                    for (int y = 0; y < 16; y++)
                        tex.SetPixel(x, y, Color.clear);

                Color stem = new Color(45f / 255f, 125f / 255f, 40f / 255f);
                Color leaf = new Color(65f / 255f, 185f / 255f, 55f / 255f);
                for (int y = 0; y <= 7; y++) tex.SetPixel(8, y, stem);
                tex.SetPixel(7, 5, leaf);
                tex.SetPixel(6, 6, leaf);
                tex.SetPixel(9, 5, leaf);
                tex.SetPixel(10, 6, leaf);
            });

            CreateTileTextureIfMissing($"{TILES_SPRITE_PATH}/tile_77.png", (tex) =>
            {
                // Wild Plant (Flowering herb on grass)
                for (int x = 0; x < 16; x++)
                    for (int y = 0; y < 16; y++)
                        tex.SetPixel(x, y, Color.clear);

                Color stalk = new Color(45f / 255f, 125f / 255f, 40f / 255f);
                Color blossom = new Color(245f / 255f, 215f / 255f, 65f / 255f);
                for (int y = 0; y <= 8; y++) tex.SetPixel(8, y, stalk);
                tex.SetPixel(7, 4, stalk);
                tex.SetPixel(9, 4, stalk);
                tex.SetPixel(7, 8, blossom);
                tex.SetPixel(8, 9, blossom);
                tex.SetPixel(9, 8, blossom);
                tex.SetPixel(8, 7, blossom);
            });

            CreateTileTextureIfMissing($"{TILES_SPRITE_PATH}/tile_78.png", (tex) =>
            {
                // Coal Ore (Stone base with black coal nuggets)
                Color stone = new Color(128f / 255f, 128f / 255f, 128f / 255f);
                Color coal = new Color(25f / 255f, 25f / 255f, 30f / 255f);
                for (int x = 0; x < 16; x++)
                    for (int y = 0; y < 16; y++)
                        tex.SetPixel(x, y, stone);

                int[,] coalPixels = {
                    {3, 4}, {4, 4}, {4, 5}, {5, 4},
                    {10, 11}, {11, 11}, {11, 12}, {12, 11},
                    {8, 7}, {8, 8}, {9, 7},
                    {12, 3}, {13, 3}, {13, 4}
                };
                for (int i = 0; i < coalPixels.GetLength(0); i++)
                    tex.SetPixel(coalPixels[i, 0], coalPixels[i, 1], coal);
            });

            CreateTileTextureIfMissing($"{TILES_SPRITE_PATH}/tile_79.png", (tex) =>
            {
                // Diamond Ore (Deep rock with bright azure crystals)
                Color deepStone = new Color(90f / 255f, 95f / 255f, 105f / 255f);
                Color diamond = new Color(60f / 255f, 220f / 255f, 255f / 255f);
                Color diamondGlint = new Color(200f / 255f, 250f / 255f, 255f / 255f);
                for (int x = 0; x < 16; x++)
                    for (int y = 0; y < 16; y++)
                        tex.SetPixel(x, y, deepStone);

                int[,] gemPixels = {
                    {4, 11}, {5, 11}, {5, 12},
                    {10, 5}, {11, 5}, {11, 6},
                    {7, 8}, {8, 8}, {8, 9}
                };
                for (int i = 0; i < gemPixels.GetLength(0); i++)
                    tex.SetPixel(gemPixels[i, 0], gemPixels[i, 1], diamond);

                tex.SetPixel(5, 12, diamondGlint);
                tex.SetPixel(11, 6, diamondGlint);
                tex.SetPixel(8, 9, diamondGlint);
            });

            CreateTileTextureIfMissing($"{TILES_SPRITE_PATH}/tile_80.png", (tex) =>
            {
                // Netherite Ore (Bedrock-stratum dark alloy veins)
                Color netherRock = new Color(55f / 255f, 40f / 255f, 45f / 255f);
                Color alloy = new Color(130f / 255f, 75f / 255f, 50f / 255f);
                Color alloyGlint = new Color(210f / 255f, 120f / 255f, 60f / 255f);
                for (int x = 0; x < 16; x++)
                    for (int y = 0; y < 16; y++)
                        tex.SetPixel(x, y, netherRock);

                int[,] alloyPixels = {
                    {3, 3}, {4, 4}, {5, 4}, {6, 5},
                    {9, 10}, {10, 11}, {11, 11}, {12, 12},
                    {8, 6}, {9, 6}, {9, 7}
                };
                for (int i = 0; i < alloyPixels.GetLength(0); i++)
                    tex.SetPixel(alloyPixels[i, 0], alloyPixels[i, 1], alloy);

                tex.SetPixel(5, 4, alloyGlint);
                tex.SetPixel(11, 11, alloyGlint);
            });
        }

        private static void CreateTileTextureIfMissing(string path, Action<Texture2D> paintAction)
        {
            if (File.Exists(path)) return;

            var tex = new Texture2D(16, 16, TextureFormat.RGBA32, false);
            tex.filterMode = FilterMode.Point;
            paintAction(tex);
            tex.Apply();

            byte[] bytes = tex.EncodeToPNG();
            File.WriteAllBytes(path, bytes);
            AssetDatabase.ImportAsset(path, ImportAssetOptions.ForceUpdate);

            var importer = AssetImporter.GetAtPath(path) as TextureImporter;
            if (importer != null)
            {
                importer.textureType = TextureImporterType.Sprite;
                importer.spritePixelsPerUnit = 16;
                importer.filterMode = FilterMode.Point;
                importer.textureCompression = TextureImporterCompression.Uncompressed;
                importer.SaveAndReimport();
            }
        }

        private static void EnsureMissingItemData()
        {
            EnsureDirectory(MATERIALS_PATH);

            CreateItemDataIfMissing("coal", "Coal", ItemCategory.Material, ItemRarity.Common,
                "A combustible mineral essential for smelting and crafting torches.", 999);

            CreateItemDataIfMissing("diamond", "Diamond", ItemCategory.Material, ItemRarity.Rare,
                "A dazzling, exceptionally hard gemstone mined from deep caverns.", 999);

            CreateItemDataIfMissing("netherite", "Netherite Scrap", ItemCategory.Material, ItemRarity.Mythic,
                "An indestructible ancient alloy forged in the Nether depths.", 999);

            CreateItemDataIfMissing("dirt_clod", "Dirt Clod", ItemCategory.Material, ItemRarity.Common,
                "A crumbly clump of rich tilled earth.", 999);

            CreateItemDataIfMissing("leaves", "Leaves", ItemCategory.Material, ItemRarity.Common,
                "Fresh fragrant tree foliage.", 999);
        }

        private static void CreateItemDataIfMissing(string itemId, string itemName, ItemCategory category, ItemRarity rarity, string desc, int maxStack)
        {
            string assetPath = $"{MATERIALS_PATH}/{itemId}.asset";
            var item = AssetDatabase.LoadAssetAtPath<ItemData>(assetPath);
            if (item == null)
            {
                item = ScriptableObject.CreateInstance<ItemData>();
                item.ItemId = itemId;
                item.ItemName = itemName;
                item.Category = category;
                item.Rarity = rarity;
                item.Description = desc;
                item.MaxStack = maxStack;
                AssetDatabase.CreateAsset(item, assetPath);
            }
        }
    }
}
