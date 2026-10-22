using System.Collections.Generic;

namespace Potaria.World
{
    /// <summary>
    /// Core world generation, chunk dimensions, biome definitions, and tile IDs for Potaria.
    /// Directly mapped from the canonical specifications in src/constants.py.
    /// </summary>
    public static class WorldConstants
    {
        // Chunk and World Dimensions (in tiles)
        public const int ChunkWidth = 16;
        public const int ChunkHeight = 240;
        public const int SkyMinY = -240;
        public const int SectionHeight = 16;
        public const int NumSections = ChunkHeight / SectionHeight;

        public const int SurfaceLevel = 70;       // Avg surface height
        public const int UndergroundLevel = 115;  // Transition to stone
        public const int CavernLevel = 160;       // Deep caves and glowing mushrooms
        public const int DungeonLevel = 205;      // Deep Nether Dungeon where Lord Malus resides

        // Block Tile IDs
        public const int TileAir = 0;
        public const int TileDirt = 1;
        public const int TileGrass = 2;
        public const int TileStone = 3;
        public const int TileWood = 4;
        public const int TileLeaves = 5;
        public const int TileWoodTrunk = 6;
        public const int TileCopperOre = 7;
        public const int TileIronOre = 8;
        public const int TileGoldOre = 9;
        public const int TileWoodPlatform = 10;
        public const int TileWorkBench = 11;
        public const int TileFurnace = 12;
        public const int TileTorch = 13;
        public const int TileStoneBrick = 14;
        public const int TileBedrock = 15;
        public const int TileDungeonBrick = 16;
        public const int TileDungeonAltar = 17;
        public const int TileSand = 18;
        public const int TileSandstone = 19;
        public const int TileCactus = 20;
        public const int TileSnow = 21;
        public const int TileIce = 22;
        public const int TileBlightGrass = 23;
        public const int TileBlightstone = 24;
        public const int TileMushroomGrass = 25;
        public const int TileMushroomStem = 26;
        public const int TileMushroomCap = 27;
        public const int TileChest = 28;
        public const int TileRoofTiles = 29;
        public const int TileWoodPlanks = 30;
        public const int TileGlass = 31;
        public const int TileDoorClosed = 32;
        public const int TileDoorOpen = 33;
        public const int TileTable = 34;
        public const int TileChair = 35;
        public const int TileBarrier = 36;
        public const int TileWater = 37;
        public const int TileBed = 38;
        public const int TileBookshelf = 39;
        public const int TileGrandfatherClock = 40;
        public const int TileFireplace = 41;
        public const int TileCandelabra = 42;
        public const int TileChandelier = 43;
        public const int TilePottedPlant = 44;
        public const int TileDresser = 45;
        public const int TileTapestry = 46;
        public const int TileBathtub = 47;
        public const int TileSink = 48;
        public const int TilePainting = 49;
        public const int TileWoodShelf = 50;
        public const int TileCarvedTuberLantern = 51;
        public const int TileBrassLantern = 52;
        public const int TileSpectralLantern = 53;
        public const int TileSapling = 54;
        public const int TileSaplingOak = 54;
        public const int TileIronChest = 55;
        public const int TileRopeRungs = 56;
        public const int TileDungeonMagma = 57;
        public const int TileDungeonIce = 58;
        public const int TileDungeonBone = 59;
        public const int TileDungeonGate = 60;
        public const int TileLamp = 61;
        public const int TileSaplingPalm = 62;
        public const int TileSaplingPine = 63;
        public const int TileSaplingBlight = 64;
        public const int TilePineWood = 65;
        public const int TilePineLeaves = 66;
        public const int TilePineTrunk = 67;
        public const int TilePalmWood = 68;
        public const int TilePalmLeaves = 69;
        public const int TilePalmTrunk = 70;
        public const int TileBlightWood = 71;
        public const int TileBlightLeaves = 72;
        public const int TileBlightTrunk = 73;
        public const int TileFarmland = 74;
        public const int TileFarmlandWet = 75;
        public const int TileCrop = 76;
        public const int TileWildPlant = 77;

        // Background Wall IDs
        public const int WallAir = 0;
        public const int WallDirt = 1;
        public const int WallStone = 2;
        public const int WallWood = 3;
        public const int WallStoneBrick = 4;
        public const int WallDungeon = 5;
        public const int WallSandstone = 6;
        public const int WallIce = 7;
        public const int WallBlightstone = 8;
        public const int WallMushroom = 9;
        public const int WallGlass = 10;
        public const int WallDungeonMagma = 11;
        public const int WallDungeonIce = 12;
        public const int WallDungeonBone = 13;

        // Biome Identifiers
        public const string BiomeForest = "forest";
        public const string BiomeDesert = "desert";
        public const string BiomeSnow = "snow";
        public const string BiomeBlight = "the_blight";
        public const string BiomeMushroom = "mushroom";
        public const string BiomeDungeon = "dungeon";
        public const string BiomeCavern = "cavern";

        // Light Limits
        public const int MaxLight = 15;
        public const int MinLight = 1;

        // Lookup sets
        public static readonly HashSet<int> PlatformTiles = new HashSet<int>
        {
            TileWoodPlatform,
            TileWorkBench,
            TileTable,
            TileBed,
            TileBookshelf,
            TileFireplace,
            TileDresser,
            TileBathtub,
            TileSink,
            TileWoodShelf,
            TileChest,
            TileIronChest,
            TileRopeRungs,
            TileDungeonAltar
        };

        public static readonly HashSet<int> LiquidTiles = new HashSet<int>
        {
            TileWater
        };

        public static readonly HashSet<int> NonSolidTiles = new HashSet<int>
        {
            TileAir,
            TileLeaves,
            TileWoodTrunk,
            TilePineLeaves,
            TilePineTrunk,
            TilePalmLeaves,
            TilePalmTrunk,
            TileBlightLeaves,
            TileBlightTrunk,
            TileTorch,
            TileCactus,
            TileMushroomStem,
            TileMushroomCap,
            TileDoorOpen,
            TileChair,
            TileWater,
            TileCandelabra,
            TileChandelier,
            TilePottedPlant,
            TileTapestry,
            TilePainting,
            TileCarvedTuberLantern,
            TileBrassLantern,
            TileSpectralLantern,
            TileLamp,
            TileSaplingOak,
            TileSaplingPalm,
            TileSaplingPine,
            TileSaplingBlight,
            TileDungeonGate,
            TileCrop,
            TileWildPlant
        };
    }
}
