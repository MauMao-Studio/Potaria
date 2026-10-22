using System;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.Tilemaps;
using Potaria.Data;

namespace Potaria.World
{
    /// <summary>
    /// Central registry and query database for all blocks and walls in Potaria.
    /// Provides high-performance O(1) indexed lookup for tile physics, mining hardness,
    /// dropped item references, and Unity TileBase assets.
    /// </summary>
    [CreateAssetMenu(fileName = "TileDatabase", menuName = "Potaria/World/Tile Database", order = 21)]
    public class TileDatabase : ScriptableObject
    {
        private static TileDatabase s_instance;

        [Header("Definitions")]
        [SerializeField] private List<TileDefinition> tileDefinitions = new List<TileDefinition>();
        [SerializeField] private List<TileDefinition> wallDefinitions = new List<TileDefinition>();

        // Fast runtime lookup caches
        private TileDefinition[] _tileLookup;
        private TileDefinition[] _wallLookup;
        private TileBase[] _tileBaseLookup;
        private TileBase[] _wallBaseLookup;
        private bool _isInitialized;

        public static TileDatabase Instance
        {
            get
            {
                if (s_instance == null)
                {
                    s_instance = Resources.Load<TileDatabase>("TileDatabase");
                    if (s_instance == null)
                    {
                        var all = Resources.FindObjectsOfTypeAll<TileDatabase>();
                        if (all.Length > 0) s_instance = all[0];
                    }
                    if (s_instance == null)
                    {
                        s_instance = CreateInstance<TileDatabase>();
                        s_instance.InitializeDefaults();
                    }
                    else
                    {
                        s_instance.Initialize();
                    }
                }
                return s_instance;
            }
            set => s_instance = value;
        }

        public List<TileDefinition> TileDefinitions => tileDefinitions;
        public List<TileDefinition> WallDefinitions => wallDefinitions;

        private void OnEnable()
        {
            Initialize();
        }

        public void Initialize()
        {
            if (tileDefinitions == null || tileDefinitions.Count == 0)
            {
                InitializeDefaults();
                return;
            }

            _tileLookup = new TileDefinition[256];
            _wallLookup = new TileDefinition[64];
            _tileBaseLookup = new TileBase[256];
            _wallBaseLookup = new TileBase[64];

            foreach (var def in tileDefinitions)
            {
                if (def == null) continue;
                if (def.TileId >= 0 && def.TileId < _tileLookup.Length)
                {
                    _tileLookup[def.TileId] = def;
                    _tileBaseLookup[def.TileId] = def.UnityTile;
                }
            }

            foreach (var def in wallDefinitions)
            {
                if (def == null) continue;
                if (def.TileId >= 0 && def.TileId < _wallLookup.Length)
                {
                    _wallLookup[def.TileId] = def;
                    _wallBaseLookup[def.TileId] = def.UnityTile;
                }
            }

            _isInitialized = true;
        }

        public TileDefinition GetTile(int tileId)
        {
            if (!_isInitialized || _tileLookup == null) Initialize();
            if (tileId >= 0 && tileId < _tileLookup.Length)
            {
                var def = _tileLookup[tileId];
                if (def != null) return def;
            }
            return GetFallbackTile(tileId);
        }

        public TileDefinition GetWall(int wallId)
        {
            if (!_isInitialized || _wallLookup == null) Initialize();
            if (wallId >= 0 && wallId < _wallLookup.Length)
            {
                var def = _wallLookup[wallId];
                if (def != null) return def;
            }
            return GetFallbackWall(wallId);
        }

        public TileBase GetTileBase(int tileId)
        {
            if (!_isInitialized) Initialize();
            if (tileId >= 0 && tileId < _tileBaseLookup.Length)
            {
                return _tileBaseLookup[tileId];
            }
            return null;
        }

        public TileBase GetWallBase(int wallId)
        {
            if (!_isInitialized) Initialize();
            if (wallId >= 0 && wallId < _wallBaseLookup.Length)
            {
                return _wallBaseLookup[wallId];
            }
            return null;
        }

        public void RegisterTile(TileDefinition def)
        {
            if (def == null) return;
            if (def.IsWall)
            {
                wallDefinitions.RemoveAll(w => w != null && w.TileId == def.TileId);
                wallDefinitions.Add(def);
            }
            else
            {
                tileDefinitions.RemoveAll(t => t != null && t.TileId == def.TileId);
                tileDefinitions.Add(def);
            }
            _isInitialized = false;
            Initialize();
        }

        /// <summary>
        /// Populates default property definitions for all canonical Potaria tiles and walls.
        /// </summary>
        public void InitializeDefaults()
        {
            tileDefinitions.Clear();
            wallDefinitions.Clear();

            // Populate all canonical blocks
            AddDefaultTile(WorldConstants.TileAir, "Air", 0, ToolType.None, null, false, false, 0, 0, false);
            AddDefaultTile(WorldConstants.TileDirt, "Dirt", 15, ToolType.Shovel, "dirt_block", true, false, 0, 3, true);
            AddDefaultTile(WorldConstants.TileGrass, "Grass", 18, ToolType.Shovel, "dirt_block", true, false, 0, 3, true);
            AddDefaultTile(WorldConstants.TileStone, "Stone", 35, ToolType.Pickaxe, "stone_block", true, false, 0, 4, true);
            AddDefaultTile(WorldConstants.TileWood, "Wood", 20, ToolType.Axe, "wood", true, false, 0, 3, true);
            AddDefaultTile(WorldConstants.TileLeaves, "Leaves", 5, ToolType.Axe, "leaves", false, false, 0, 1, false);
            AddDefaultTile(WorldConstants.TileWoodTrunk, "Wood Trunk", 20, ToolType.Axe, "wood", false, false, 0, 2, false);
            AddDefaultTile(WorldConstants.TileCopperOre, "Copper Ore", 40, ToolType.Pickaxe, "copper_ore", true, false, 0, 4, true);
            AddDefaultTile(WorldConstants.TileIronOre, "Iron Ore", 45, ToolType.Pickaxe, "iron_ore", true, false, 0, 4, true);
            AddDefaultTile(WorldConstants.TileGoldOre, "Gold Ore", 55, ToolType.Pickaxe, "gold_ore", true, false, 1, 4, true);
            AddDefaultTile(WorldConstants.TileWoodPlatform, "Wood Platform", 10, ToolType.Axe, "wood_platform", false, true, 0, 0, false);
            AddDefaultTile(WorldConstants.TileWorkBench, "Work Bench", 25, ToolType.Axe, "work_bench", false, true, 0, 0, false);
            AddDefaultTile(WorldConstants.TileFurnace, "Furnace", 40, ToolType.Pickaxe, "furnace", false, false, 8, 0, false);
            AddDefaultTile(WorldConstants.TileTorch, "Torch", 5, ToolType.Pickaxe, "torch", false, false, 10, 0, false, 6, new Color(1f, 0.85f, 0.4f));
            AddDefaultTile(WorldConstants.TileStoneBrick, "Stone Brick", 38, ToolType.Pickaxe, "stone_brick", true, false, 0, 4, true);
            AddDefaultTile(WorldConstants.TileBedrock, "Bedrock", 9999, ToolType.None, null, true, false, 0, 15, true, 0, Color.black, true);
            AddDefaultTile(WorldConstants.TileDungeonBrick, "Dungeon Brick", 9999, ToolType.None, null, true, false, 1, 15, true, 2, Color.cyan, true);
            AddDefaultTile(WorldConstants.TileDungeonAltar, "Dungeon Altar", 9999, ToolType.None, null, false, true, 6, 0, false, 4, Color.magenta, true);
            AddDefaultTile(WorldConstants.TileSand, "Sand", 12, ToolType.Shovel, "sand_block", true, false, 0, 2, true);
            AddDefaultTile(WorldConstants.TileSandstone, "Sandstone", 30, ToolType.Pickaxe, "sandstone_block", true, false, 0, 4, true);
            AddDefaultTile(WorldConstants.TileCactus, "Cactus", 15, ToolType.Axe, "cactus", false, false, 0, 1, false);
            AddDefaultTile(WorldConstants.TileSnow, "Snow", 10, ToolType.Shovel, "snow_block", true, false, 0, 2, true);
            AddDefaultTile(WorldConstants.TileIce, "Ice", 22, ToolType.Pickaxe, "ice_block", true, false, 0, 2, true);
            AddDefaultTile(WorldConstants.TileBlightGrass, "Blight Grass", 25, ToolType.Shovel, "dirt_block", true, false, 1, 4, true);
            AddDefaultTile(WorldConstants.TileBlightstone, "Blightstone", 50, ToolType.Pickaxe, "blightstone_block", true, false, 0, 5, true);
            AddDefaultTile(WorldConstants.TileMushroomGrass, "Glowing Mushroom Grass", 20, ToolType.Shovel, "glowing_mushroom", true, false, 6, 2, true, 5, new Color(0.2f, 0.6f, 1f));
            AddDefaultTile(WorldConstants.TileMushroomStem, "Mushroom Stem", 15, ToolType.Axe, "wood", false, false, 2, 1, false);
            AddDefaultTile(WorldConstants.TileMushroomCap, "Glowing Mushroom Cap", 12, ToolType.Axe, "glowing_mushroom", false, false, 9, 0, false, 6, new Color(0.1f, 0.5f, 1f));
            AddDefaultTile(WorldConstants.TileChest, "Treasure Chest", 30, ToolType.Pickaxe, "chest", false, true, 3, 0, false);
            AddDefaultTile(WorldConstants.TileRoofTiles, "Roof Tiles", 25, ToolType.Pickaxe, "roof_tiles", true, false, 0, 3, true);
            AddDefaultTile(WorldConstants.TileWoodPlanks, "Wood Planks", 20, ToolType.Axe, "wood_planks", true, false, 0, 3, true);
            AddDefaultTile(WorldConstants.TileGlass, "Glass Window", 10, ToolType.Pickaxe, "glass_window", true, false, 0, 0, false);
            AddDefaultTile(WorldConstants.TileDoorClosed, "Wooden Door", 20, ToolType.Axe, "wooden_door", true, false, 0, 1, false);
            AddDefaultTile(WorldConstants.TileDoorOpen, "Open Wooden Door", 20, ToolType.Axe, "wooden_door", false, false, 0, 0, false);
            AddDefaultTile(WorldConstants.TileTable, "Wooden Table", 20, ToolType.Axe, "wooden_table", false, true, 0, 0, false);
            AddDefaultTile(WorldConstants.TileChair, "Wooden Chair", 15, ToolType.Axe, "wooden_chair", false, false, 0, 0, false);
            AddDefaultTile(WorldConstants.TileBarrier, "Magical Barrier", 30, ToolType.None, null, true, false, 10, 0, false);
            AddDefaultTile(WorldConstants.TileWater, "Water", 9999, ToolType.None, null, false, false, 0, 2, false, 0, Color.clear, true, true);
            AddDefaultTile(WorldConstants.TileBed, "Wooden Bed", 20, ToolType.Axe, "wooden_bed", false, true, 0, 0, false);
            AddDefaultTile(WorldConstants.TileBookshelf, "Bookshelf", 20, ToolType.Axe, "bookshelf", false, true, 0, 0, false);
            AddDefaultTile(WorldConstants.TileGrandfatherClock, "Grandfather Clock", 25, ToolType.Axe, "grandfather_clock", false, false, 1, 0, false);
            AddDefaultTile(WorldConstants.TileFireplace, "Stone Fireplace", 35, ToolType.Pickaxe, "stone_fireplace", false, true, 13, 0, false, 11, new Color(1f, 0.6f, 0.2f));
            AddDefaultTile(WorldConstants.TileCandelabra, "Candelabra", 10, ToolType.Pickaxe, "candelabra", false, false, 12, 0, false, 10, new Color(1f, 0.8f, 0.3f));
            AddDefaultTile(WorldConstants.TileChandelier, "Chandelier", 12, ToolType.Pickaxe, "chandelier", false, false, 14, 0, false, 14, new Color(1f, 0.85f, 0.4f));
            AddDefaultTile(WorldConstants.TilePottedPlant, "Potted Spud Plant", 10, ToolType.Pickaxe, "potted_plant", false, false, 2, 0, false);
            AddDefaultTile(WorldConstants.TileDresser, "Wooden Dresser", 20, ToolType.Axe, "wooden_dresser", false, true, 0, 0, false);
            AddDefaultTile(WorldConstants.TileTapestry, "Wall Tapestry", 8, ToolType.Axe, "wall_tapestry", false, false, 0, 0, false);
            AddDefaultTile(WorldConstants.TileBathtub, "Bathtub", 25, ToolType.Pickaxe, "bathtub", false, true, 0, 0, false);
            AddDefaultTile(WorldConstants.TileSink, "Sink", 20, ToolType.Pickaxe, "sink", false, true, 0, 0, false);
            AddDefaultTile(WorldConstants.TilePainting, "Painting", 8, ToolType.Axe, "painting", false, false, 1, 0, false);
            AddDefaultTile(WorldConstants.TileWoodShelf, "Wood Shelf", 10, ToolType.Axe, "wood_shelf", false, true, 0, 0, false);
            AddDefaultTile(WorldConstants.TileCarvedTuberLantern, "Carved Tuber Lantern", 8, ToolType.Axe, "carved_tuber_lantern", false, false, 14, 0, false, 8, new Color(1f, 0.7f, 0.2f));
            AddDefaultTile(WorldConstants.TileBrassLantern, "Brass Lantern", 10, ToolType.Pickaxe, "brass_lantern", false, false, 14, 0, false, 8, new Color(1f, 0.8f, 0.4f));
            AddDefaultTile(WorldConstants.TileSpectralLantern, "Spectral Lantern", 10, ToolType.Pickaxe, "spectral_lantern", false, false, 14, 0, false, 8, new Color(0.2f, 0.8f, 1f));
            AddDefaultTile(WorldConstants.TileLamp, "Brass Lamp", 10, ToolType.Pickaxe, "brass_lamp", false, false, 14, 0, false, 9, new Color(1f, 0.85f, 0.45f));
            AddDefaultTile(WorldConstants.TileSaplingOak, "Oak Sapling", 5, ToolType.Axe, "oak_sapling", false, false, 0, 0, false);
            AddDefaultTile(WorldConstants.TileSaplingPalm, "Palm Sapling", 5, ToolType.Axe, "palm_sapling", false, false, 0, 0, false);
            AddDefaultTile(WorldConstants.TileSaplingPine, "Pine Sapling", 5, ToolType.Axe, "pine_sapling", false, false, 0, 0, false);
            AddDefaultTile(WorldConstants.TileSaplingBlight, "Blight Sapling", 5, ToolType.Axe, "blight_sapling", false, false, 2, 0, false, 3, new Color(0.6f, 0.2f, 0.9f));
            AddDefaultTile(WorldConstants.TileIronChest, "Iron Storage Chest", 35, ToolType.Pickaxe, "iron_chest", false, true, 0, 0, false);
            AddDefaultTile(WorldConstants.TileRopeRungs, "Rope Rungs", 10, ToolType.Axe, "rope_rungs", false, true, 0, 0, false);
            AddDefaultTile(WorldConstants.TileDungeonMagma, "Nether Magma Dungeon Brick", 9999, ToolType.None, null, true, false, 2, 15, true, 3, Color.red, true);
            AddDefaultTile(WorldConstants.TileDungeonIce, "Permafrost Crypt Dungeon Brick", 9999, ToolType.None, null, true, false, 1, 15, true, 2, Color.cyan, true);
            AddDefaultTile(WorldConstants.TileDungeonBone, "Catacomb Bone Brick", 9999, ToolType.None, null, true, false, 1, 15, true, 2, Color.gray, true);
            AddDefaultTile(WorldConstants.TileDungeonGate, "Dungeon Gate Portcullis", 9999, ToolType.None, null, false, false, 1, 0, false, 2, Color.gray, true);
            AddDefaultTile(WorldConstants.TilePineWood, "Pine Wood", 20, ToolType.Axe, "pine_wood", true, false, 0, 3, true);
            AddDefaultTile(WorldConstants.TilePineLeaves, "Pine Leaves", 5, ToolType.Axe, "pine_leaves", false, false, 0, 1, false);
            AddDefaultTile(WorldConstants.TilePineTrunk, "Pine Wood Trunk", 20, ToolType.Axe, "pine_wood", false, false, 0, 2, false);
            AddDefaultTile(WorldConstants.TilePalmWood, "Palm Wood", 20, ToolType.Axe, "palm_wood", true, false, 0, 3, true);
            AddDefaultTile(WorldConstants.TilePalmLeaves, "Palm Leaves", 5, ToolType.Axe, "palm_leaves", false, false, 0, 1, false);
            AddDefaultTile(WorldConstants.TilePalmTrunk, "Palm Wood Trunk", 20, ToolType.Axe, "palm_wood", false, false, 0, 2, false);
            AddDefaultTile(WorldConstants.TileBlightWood, "Blight Wood", 20, ToolType.Axe, "blight_wood", true, false, 1, 3, true);
            AddDefaultTile(WorldConstants.TileBlightLeaves, "Blight Leaves", 5, ToolType.Axe, "blight_leaves", false, false, 1, 1, false);
            AddDefaultTile(WorldConstants.TileBlightTrunk, "Blight Wood Trunk", 20, ToolType.Axe, "blight_wood", false, false, 1, 2, false);
            AddDefaultTile(WorldConstants.TileFarmland, "Farmland", 15, ToolType.Shovel, "dirt_clod", true, false, 0, 3, true);
            AddDefaultTile(WorldConstants.TileFarmlandWet, "Hydrated Farmland", 15, ToolType.Shovel, "dirt_clod", true, false, 0, 3, true);
            AddDefaultTile(WorldConstants.TileCrop, "Crops", 1, ToolType.None, null, false, false, 0, 0, false);
            AddDefaultTile(WorldConstants.TileWildPlant, "Wild Plant", 1, ToolType.None, null, false, false, 0, 0, false);

            // Populate all canonical walls
            AddDefaultWall(WorldConstants.WallAir, "Air Wall", 0, ToolType.None, null, 0);
            AddDefaultWall(WorldConstants.WallDirt, "Dirt Wall", 15, ToolType.Hammer, "dirt_wall", 3);
            AddDefaultWall(WorldConstants.WallStone, "Stone Wall", 30, ToolType.Hammer, "stone_wall", 4);
            AddDefaultWall(WorldConstants.WallWood, "Wood Wall", 20, ToolType.Hammer, "wood_wall", 3);
            AddDefaultWall(WorldConstants.WallStoneBrick, "Stone Brick Wall", 35, ToolType.Hammer, "stone_brick_wall", 4);
            AddDefaultWall(WorldConstants.WallDungeon, "Dungeon Wall", 9999, ToolType.None, null, 15, true);
            AddDefaultWall(WorldConstants.WallSandstone, "Sandstone Wall", 25, ToolType.Hammer, "sandstone_wall", 4);
            AddDefaultWall(WorldConstants.WallIce, "Ice Wall", 20, ToolType.Hammer, "ice_wall", 2);
            AddDefaultWall(WorldConstants.WallBlightstone, "Blightstone Wall", 45, ToolType.Hammer, "blightstone_wall", 5);
            AddDefaultWall(WorldConstants.WallMushroom, "Mushroom Wall", 18, ToolType.Hammer, "mushroom_wall", 2);
            AddDefaultWall(WorldConstants.WallGlass, "Glass Wall", 10, ToolType.Hammer, "glass_wall", 0);
            AddDefaultWall(WorldConstants.WallDungeonMagma, "Dungeon Magma Wall", 9999, ToolType.None, null, 15, true);
            AddDefaultWall(WorldConstants.WallDungeonIce, "Dungeon Ice Wall", 9999, ToolType.None, null, 15, true);
            AddDefaultWall(WorldConstants.WallDungeonBone, "Dungeon Bone Wall", 9999, ToolType.None, null, 15, true);

            _isInitialized = false;
            Initialize();
        }

        private void AddDefaultTile(int id, string name, int hardness, ToolType tool, string dropId,
            bool solid, bool platform, int lightEmit, int absorb, bool opaque,
            int lightRad = 0, Color? emitCol = null, bool indestructible = false, bool liquid = false)
        {
            var def = new TileDefinition();
            def.TileId = id;
            def.TileName = name;
            def.Hardness = hardness;
            def.RequiredTool = tool;
            def.DropItemId = dropId ?? string.Empty;
            def.IsSolid = solid;
            def.IsPlatform = platform;
            def.IsLiquid = liquid;
            def.LightEmission = lightEmit;
            def.LightRadius = lightRad > 0 ? lightRad : lightEmit;
            def.LightAbsorption = absorb;
            def.IsOpaque = opaque;
            def.EmissionColor = emitCol ?? Color.white;
            def.IsIndestructible = indestructible;
            def.IsWall = false;
            tileDefinitions.Add(def);
        }

        private void AddDefaultWall(int id, string name, int hardness, ToolType tool, string dropId,
            int absorb, bool indestructible = false)
        {
            var def = new TileDefinition();
            def.TileId = id;
            def.TileName = name;
            def.Hardness = hardness;
            def.RequiredTool = tool;
            def.DropItemId = dropId ?? string.Empty;
            def.IsSolid = false;
            def.IsPlatform = false;
            def.LightAbsorption = absorb;
            def.IsIndestructible = indestructible;
            def.IsWall = true;
            wallDefinitions.Add(def);
        }

        private TileDefinition GetFallbackTile(int id)
        {
            var def = new TileDefinition();
            def.TileId = id;
            def.TileName = $"Tile_{id}";
            def.Hardness = 20;
            def.IsSolid = true;
            return def;
        }

        private TileDefinition GetFallbackWall(int id)
        {
            var def = new TileDefinition();
            def.TileId = id;
            def.TileName = $"Wall_{id}";
            def.Hardness = 15;
            def.IsWall = true;
            return def;
        }
    }
}
