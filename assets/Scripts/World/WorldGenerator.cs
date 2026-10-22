using System;
using UnityEngine;

namespace Potaria.World
{
    /// <summary>
    /// Procedural terrain and dungeon synthesis engine for Potaria.
    /// Directly implements multi-octave Perlin heightmaps, cave worm tunneling,
    /// ore pocket seeding, surface vegetation, and multi-tier subterranean dungeons.
    /// </summary>
    public class WorldGenerator
    {
        private readonly int _seed;
        private readonly PerlinNoise _noiseSurface;
        private readonly PerlinNoise _noiseCaves;
        private readonly PerlinNoise _noiseOres;
        private readonly PerlinNoise _noiseBiome;

        public int Seed => _seed;

        public WorldGenerator(int seed)
        {
            _seed = seed;
            _noiseSurface = new PerlinNoise(seed);
            _noiseCaves = new PerlinNoise(seed + 101);
            _noiseOres = new PerlinNoise(seed + 202);
            _noiseBiome = new PerlinNoise(seed + 303);
        }

        /// <summary>
        /// Generates procedural terrain data for a given chunk column.
        /// </summary>
        public ChunkData GenerateChunk(int chunkX)
        {
            var chunk = new ChunkData(chunkX, _seed);
            var rng = new System.Random(_seed ^ (chunkX * 99991));

            // 1. Surface line and Biome for each column
            for (int lx = 0; lx < ChunkData.Width; lx++)
            {
                int gx = chunkX * ChunkData.Width + lx;
                float n = _noiseSurface.Fractal1D(gx * 0.018f, 3, 0.5f);
                int h = (int)(WorldConstants.SurfaceLevel + n * 20f);
                chunk.SurfaceHeights[lx] = Mathf.Clamp(h, 35, ChunkData.Height - 90);

                float bVal = _noiseBiome.Fractal1D(gx * 0.0035f, 2);
                if (bVal < -0.18f)
                    chunk.ColBiomes[lx] = WorldConstants.BiomeSnow;
                else if (bVal < 0.06f)
                    chunk.ColBiomes[lx] = WorldConstants.BiomeForest;
                else if (bVal < 0.22f)
                    chunk.ColBiomes[lx] = WorldConstants.BiomeDesert;
                else
                    chunk.ColBiomes[lx] = WorldConstants.BiomeBlight;
            }

            // 2. Base Strata by Biome
            for (int lx = 0; lx < ChunkData.Width; lx++)
            {
                int gx = chunkX * ChunkData.Width + lx;
                int surf = chunk.SurfaceHeights[lx];
                string b = chunk.ColBiomes[lx];

                for (int y = 0; y < ChunkData.Height; y++)
                {
                    if (y < surf)
                    {
                        chunk.SetTile(lx, y, WorldConstants.TileAir);
                        chunk.SetWall(lx, y, WorldConstants.WallAir);
                    }
                    else if (y == surf)
                    {
                        if (b == WorldConstants.BiomeDesert)
                            chunk.SetTile(lx, y, WorldConstants.TileSand);
                        else if (b == WorldConstants.BiomeSnow)
                            chunk.SetTile(lx, y, WorldConstants.TileSnow);
                        else if (b == WorldConstants.BiomeBlight)
                            chunk.SetTile(lx, y, WorldConstants.TileBlightGrass);
                        else
                            chunk.SetTile(lx, y, WorldConstants.TileGrass);

                        chunk.SetWall(lx, y, WorldConstants.WallAir);
                    }
                    else if (y < surf + 6)
                    {
                        if (b == WorldConstants.BiomeDesert)
                        {
                            chunk.SetTile(lx, y, WorldConstants.TileSand);
                            chunk.SetWall(lx, y, WorldConstants.WallSandstone);
                        }
                        else if (b == WorldConstants.BiomeSnow)
                        {
                            chunk.SetTile(lx, y, WorldConstants.TileSnow);
                            chunk.SetWall(lx, y, WorldConstants.WallIce);
                        }
                        else if (b == WorldConstants.BiomeBlight)
                        {
                            chunk.SetTile(lx, y, WorldConstants.TileDirt);
                            chunk.SetWall(lx, y, WorldConstants.WallBlightstone);
                        }
                        else
                        {
                            chunk.SetTile(lx, y, WorldConstants.TileDirt);
                            chunk.SetWall(lx, y, WorldConstants.WallDirt);
                        }
                    }
                    else if (y < WorldConstants.UndergroundLevel)
                    {
                        if (b == WorldConstants.BiomeDesert)
                        {
                            chunk.SetTile(lx, y, WorldConstants.TileSandstone);
                            chunk.SetWall(lx, y, WorldConstants.WallSandstone);
                        }
                        else if (b == WorldConstants.BiomeSnow)
                        {
                            chunk.SetTile(lx, y, rng.NextDouble() < 0.65 ? WorldConstants.TileIce : WorldConstants.TileStone);
                            chunk.SetWall(lx, y, WorldConstants.WallIce);
                        }
                        else if (b == WorldConstants.BiomeBlight)
                        {
                            chunk.SetTile(lx, y, rng.NextDouble() < 0.75 ? WorldConstants.TileBlightstone : WorldConstants.TileStone);
                            chunk.SetWall(lx, y, WorldConstants.WallBlightstone);
                        }
                        else
                        {
                            float dirtProb = (float)(WorldConstants.UndergroundLevel - y) / Mathf.Max(1, WorldConstants.UndergroundLevel - surf);
                            if (rng.NextDouble() < dirtProb)
                            {
                                chunk.SetTile(lx, y, WorldConstants.TileDirt);
                                chunk.SetWall(lx, y, WorldConstants.WallDirt);
                            }
                            else
                            {
                                chunk.SetTile(lx, y, WorldConstants.TileStone);
                                chunk.SetWall(lx, y, WorldConstants.WallStone);
                            }
                        }
                    }
                    else
                    {
                        // Cavern depths: check for Glowing Mushroom biome pocket
                        float mVal = _noiseOres.Fractal2D(gx * 0.022f, y * 0.022f, 2);
                        if (y >= WorldConstants.CavernLevel - 12 && mVal > 0.38f)
                        {
                            chunk.SetTile(lx, y, WorldConstants.TileStone);
                            chunk.SetWall(lx, y, WorldConstants.WallMushroom);
                        }
                        else
                        {
                            chunk.SetTile(lx, y, WorldConstants.TileStone);
                            chunk.SetWall(lx, y, WorldConstants.WallStone);
                        }
                    }
                }
            }

            // 3. Caves & Caverns (2D Perlin Worms across chunks)
            for (int lx = 0; lx < ChunkData.Width; lx++)
            {
                int gx = chunkX * ChunkData.Width + lx;
                int surf = chunk.SurfaceHeights[lx];
                string b = chunk.ColBiomes[lx];

                for (int y = surf + 4; y < ChunkData.Height - 25; y++)
                {
                    // Dungeon Chamber protection zones deep underground (y >= 160 && y <= 220)
                    bool isDungeonZone = (y >= 160 && y <= 220) && (
                        (chunkX >= -2 && chunkX <= 2) ||   // Nether Dungeon (gx ~0)
                        (chunkX >= 3 && chunkX <= 7) ||    // Magma Dungeon (gx ~80)
                        (chunkX >= -7 && chunkX <= -3) ||  // Glacial Crypt (gx ~-80)
                        (chunkX >= 7 && chunkX <= 11)      // Catacombs (gx ~140)
                    );
                    if (isDungeonZone)
                        continue;

                    float caveVal = _noiseCaves.Fractal2D(gx * 0.045f, y * 0.045f, 3);
                    float threshold = y < WorldConstants.UndergroundLevel ? 0.28f : 0.22f;
                    if (Mathf.Abs(caveVal) < 0.12f || caveVal > threshold)
                    {
                        chunk.SetTile(lx, y, WorldConstants.TileAir);
                        if (y < WorldConstants.UndergroundLevel)
                        {
                            if (b == WorldConstants.BiomeDesert) chunk.SetWall(lx, y, WorldConstants.WallSandstone);
                            else if (b == WorldConstants.BiomeSnow) chunk.SetWall(lx, y, WorldConstants.WallIce);
                            else if (b == WorldConstants.BiomeBlight) chunk.SetWall(lx, y, WorldConstants.WallBlightstone);
                            else chunk.SetWall(lx, y, WorldConstants.WallDirt);
                        }
                        else
                        {
                            float mVal = _noiseOres.Fractal2D(gx * 0.022f, y * 0.022f, 2);
                            if (y >= WorldConstants.CavernLevel - 12 && mVal > 0.38f)
                                chunk.SetWall(lx, y, WorldConstants.WallMushroom);
                            else
                                chunk.SetWall(lx, y, WorldConstants.WallStone);
                        }
                    }
                }
            }

            // 3b. Mushroom Grass conversion in Cavern Mushroom Pockets
            for (int lx = 0; lx < ChunkData.Width; lx++)
            {
                for (int y = WorldConstants.CavernLevel - 12; y < ChunkData.Height - 25; y++)
                {
                    if (chunk.GetTile(lx, y) == WorldConstants.TileStone && chunk.GetWall(lx, y) == WorldConstants.WallMushroom)
                    {
                        if (y > 0 && chunk.GetTile(lx, y - 1) == WorldConstants.TileAir)
                        {
                            chunk.SetTile(lx, y, WorldConstants.TileMushroomGrass);
                        }
                    }
                }
            }

            // 4. Ore Veins (Coal, Copper, Iron, Gold, Diamond, Netherite)
            for (int lx = 0; lx < ChunkData.Width; lx++)
            {
                int gx = chunkX * ChunkData.Width + lx;
                int surf = chunk.SurfaceHeights[lx];
                for (int y = surf + 3; y < ChunkData.Height - 4; y++)
                {
                    int currentTile = chunk.GetTile(lx, y);
                    if (currentTile == WorldConstants.TileStone || currentTile == WorldConstants.TileDirt ||
                        currentTile == WorldConstants.TileSandstone || currentTile == WorldConstants.TileBlightstone ||
                        currentTile == WorldConstants.TileIce)
                    {
                        float oreVal = _noiseOres.Fractal2D(gx * 0.12f, y * 0.12f, 2);
                        float deepOreVal = _noiseOres.Fractal2D((gx + 500) * 0.15f, (y + 500) * 0.15f, 2);

                        // Netherite: Deepest subterranean strata near Bedrock / Nether dungeon depths
                        if (deepOreVal < -0.52f && y >= WorldConstants.DungeonLevel - 10)
                        {
                            chunk.SetTile(lx, y, WorldConstants.TileNetheriteOre);
                        }
                        // Diamond: Rare gem clusters in deep Caverns and lower rock layers
                        else if (deepOreVal > 0.54f && y >= WorldConstants.CavernLevel)
                        {
                            chunk.SetTile(lx, y, WorldConstants.TileDiamondOre);
                        }
                        // Gold: Precious metal veins in Caverns
                        else if (oreVal > 0.52f && y > WorldConstants.CavernLevel - 20)
                        {
                            chunk.SetTile(lx, y, WorldConstants.TileGoldOre);
                        }
                        // Copper: Upper to mid underground stratum
                        else if (oreVal > 0.42f && y < WorldConstants.CavernLevel)
                        {
                            chunk.SetTile(lx, y, WorldConstants.TileCopperOre);
                        }
                        // Coal: Common combustible ore across surface and upper underground
                        else if (oreVal > 0.30f && oreVal <= 0.42f && y > surf + 4 && y < WorldConstants.UndergroundLevel + 25)
                        {
                            chunk.SetTile(lx, y, WorldConstants.TileCoalOre);
                        }
                        // Iron: Sturdy metal veins distributed from mid underground downwards
                        else if (oreVal < -0.44f && y > surf + 15)
                        {
                            chunk.SetTile(lx, y, WorldConstants.TileIronOre);
                        }
                    }
                }
            }

            // 4b. Natural Liquid Water (Surface Ponds & Cavern Pools)
            if (Math.Abs(chunkX) % 4 == 1)
            {
                int pondStart = rng.Next(2, 6);
                int pondW = rng.Next(5, 8);
                int pondEnd = Mathf.Min(ChunkData.Width - 1, pondStart + pondW);

                int flatWaterY = 0;
                for (int px = pondStart; px < pondEnd; px++)
                    flatWaterY = Mathf.Max(flatWaterY, chunk.SurfaceHeights[px]);

                for (int px = pondStart; px < pondEnd; px++)
                {
                    for (int wy = chunk.SurfaceHeights[px]; wy < flatWaterY; wy++)
                        chunk.SetTile(px, wy, WorldConstants.TileAir);
                    for (int wy = flatWaterY; wy < Mathf.Min(ChunkData.Height, flatWaterY + 3); wy++)
                    {
                        if (chunk.GetTile(px, wy) != WorldConstants.TileBedrock && chunk.GetTile(px, wy) != WorldConstants.TileDungeonBrick)
                            chunk.SetTile(px, wy, WorldConstants.TileWater);
                    }
                }
            }

            // Subterranean cavern water pools
            for (int lx = 2; lx < ChunkData.Width - 6; lx += 6)
            {
                if (rng.NextDouble() < 0.15)
                {
                    for (int y = WorldConstants.UndergroundLevel + 10; y < WorldConstants.CavernLevel + 20; y++)
                    {
                        bool canPlacePool = true;
                        for (int dx = 0; dx < 5; dx++)
                        {
                            if (chunk.GetTile(lx + dx, y) != WorldConstants.TileAir ||
                                (chunk.GetTile(lx + dx, y + 1) != WorldConstants.TileStone &&
                                 chunk.GetTile(lx + dx, y + 1) != WorldConstants.TileSandstone &&
                                 chunk.GetTile(lx + dx, y + 1) != WorldConstants.TileIce))
                            {
                                canPlacePool = false;
                                break;
                            }
                        }
                        if (canPlacePool)
                        {
                            for (int dx = 0; dx < 5; dx++)
                                chunk.SetTile(lx + dx, y, WorldConstants.TileWater);
                            break;
                        }
                    }
                }
            }

            // 5. Dynamic Surface Vegetation & Trees
            for (int lx = 1; lx < ChunkData.Width - 1; lx++)
            {
                int surf = chunk.SurfaceHeights[lx];
                string b = chunk.ColBiomes[lx];

                // Forest: Oak Trees
                if (b == WorldConstants.BiomeForest && chunk.GetTile(lx, surf) == WorldConstants.TileGrass && (lx == 5 || lx == 11))
                {
                    if (rng.NextDouble() < 0.65)
                    {
                        int trunkH = rng.Next(5, 9);
                        bool canGrow = true;
                        for (int ty = surf - trunkH - 4; ty < surf; ty++)
                        {
                            if (ty >= 0 && chunk.GetTile(lx, ty) != WorldConstants.TileAir)
                            {
                                canGrow = false;
                                break;
                            }
                        }
                        if (canGrow)
                        {
                            int crownCy = surf - trunkH;
                            for (int ty = crownCy; ty < surf; ty++)
                                chunk.SetTile(lx, ty, WorldConstants.TileWoodTrunk);

                            for (int cx = lx - 3; cx <= lx + 3; cx++)
                            {
                                for (int cy = crownCy - 3; cy <= crownCy + 1; cy++)
                                {
                                    if (cx == lx && cy >= crownCy) continue;
                                    if (cx >= 0 && cx < ChunkData.Width && cy >= 0 && cy < ChunkData.Height)
                                    {
                                        float dx = (cx - lx) / 2.9f;
                                        float dy = (cy - (crownCy - 0.5f)) / 2.3f;
                                        if (dx * dx + dy * dy <= 1.05f)
                                            chunk.SetTile(cx, cy, WorldConstants.TileLeaves);
                                    }
                                }
                            }
                        }
                    }
                }
                // Desert: Cacti & Palm Trees
                else if (b == WorldConstants.BiomeDesert && chunk.GetTile(lx, surf) == WorldConstants.TileSand)
                {
                    if ((lx == 3 || lx == 8 || lx == 13) && rng.NextDouble() < 0.40)
                    {
                        int cH = rng.Next(3, 6);
                        for (int cy = surf - cH; cy < surf; cy++)
                            chunk.SetTile(lx, cy, WorldConstants.TileCactus);
                        if (cH >= 4)
                        {
                            int armDir = rng.Next(0, 2) == 0 ? -1 : 1;
                            int ax = lx + armDir;
                            if (ax >= 0 && ax < ChunkData.Width)
                            {
                                chunk.SetTile(ax, surf - cH + 1, WorldConstants.TileCactus);
                                chunk.SetTile(ax, surf - cH, WorldConstants.TileCactus);
                            }
                        }
                    }
                    else if ((lx == 5 || lx == 11) && rng.NextDouble() < 0.50)
                    {
                        int palmH = rng.Next(6, 10);
                        bool canGrow = true;
                        for (int ty = surf - palmH - 3; ty < surf; ty++)
                        {
                            if (ty >= 0 && chunk.GetTile(lx, ty) != WorldConstants.TileAir)
                            {
                                canGrow = false;
                                break;
                            }
                        }
                        if (canGrow)
                        {
                            int crownCy = surf - palmH;
                            for (int ty = crownCy; ty < surf; ty++)
                                chunk.SetTile(lx, ty, WorldConstants.TilePalmTrunk);
                            if (crownCy - 1 >= 0)
                                chunk.SetTile(lx, crownCy - 1, WorldConstants.TilePalmLeaves);
                            int[] frondDx = { -3, -2, -1, 1, 2, 3 };
                            foreach (int fdx in frondDx)
                            {
                                int drop = Math.Abs(fdx) == 3 ? 1 : (Math.Abs(fdx) == 2 ? 0 : -1);
                                int fx = lx + fdx;
                                int fy = crownCy + drop;
                                if (fx >= 0 && fx < ChunkData.Width && fy >= 0 && fy < ChunkData.Height)
                                    chunk.SetTile(fx, fy, WorldConstants.TilePalmLeaves);
                                if (Math.Abs(fdx) <= 2 && fx >= 0 && fx < ChunkData.Width && crownCy >= 0)
                                    chunk.SetTile(fx, crownCy, WorldConstants.TilePalmLeaves);
                            }
                        }
                    }
                }
                // Snow: Conifer Pine Trees
                else if (b == WorldConstants.BiomeSnow && chunk.GetTile(lx, surf) == WorldConstants.TileSnow && (lx == 5 || lx == 11))
                {
                    if (rng.NextDouble() < 0.60)
                    {
                        int pH = rng.Next(7, 11);
                        int crownCy = surf - pH;
                        for (int ty = crownCy; ty < surf; ty++)
                            chunk.SetTile(lx, ty, WorldConstants.TilePineTrunk);

                        var pineTiers = new (int dLvl, float rad)[]
                        {
                            (-2, 1.0f), (-1, 1.6f), (0, 2.2f), (1, 2.8f), (2, 3.2f), (3, 2.6f)
                        };
                        foreach (var tier in pineTiers)
                        {
                            int leafY = crownCy + tier.dLvl;
                            if (leafY >= 0 && leafY < ChunkData.Height)
                            {
                                int irad = (int)tier.rad;
                                for (int cx = lx - irad; cx <= lx + irad; cx++)
                                {
                                    if (cx == lx && leafY >= crownCy) continue;
                                    if (cx >= 0 && cx < ChunkData.Width && Math.Abs(cx - lx) <= tier.rad)
                                        chunk.SetTile(cx, leafY, WorldConstants.TilePineLeaves);
                                }
                            }
                        }
                    }
                }
                // Blight: Ebonwood Trees
                else if (b == WorldConstants.BiomeBlight && chunk.GetTile(lx, surf) == WorldConstants.TileBlightGrass && (lx == 5 || lx == 11))
                {
                    if (rng.NextDouble() < 0.60)
                    {
                        int bH = rng.Next(5, 9);
                        int crownCy = surf - bH;
                        for (int ty = crownCy; ty < surf; ty++)
                            chunk.SetTile(lx, ty, WorldConstants.TileBlightTrunk);

                        for (int cx = lx - 3; cx <= lx + 3; cx++)
                        {
                            for (int cy = crownCy - 3; cy <= crownCy + 1; cy++)
                            {
                                if (cx == lx && cy >= crownCy) continue;
                                if (cx >= 0 && cx < ChunkData.Width && cy >= 0 && cy < ChunkData.Height)
                                {
                                    float dx = (cx - lx) / 2.9f;
                                    float dy = (cy - (crownCy - 0.5f)) / 2.3f;
                                    if (dx * dx + dy * dy <= 1.05f)
                                        chunk.SetTile(cx, cy, WorldConstants.TileBlightLeaves);
                                }
                            }
                        }
                    }
                }
            }

            // 5b. Giant Glowing Mushrooms in Caverns
            for (int lx = 2; lx < ChunkData.Width - 2; lx++)
            {
                for (int y = WorldConstants.CavernLevel - 10; y < ChunkData.Height - 25; y++)
                {
                    if (chunk.GetTile(lx, y) == WorldConstants.TileMushroomGrass)
                    {
                        bool clearAirAbove = true;
                        for (int k = 1; k <= 4; k++)
                        {
                            if (chunk.GetTile(lx, y - k) != WorldConstants.TileAir)
                            {
                                clearAirAbove = false;
                                break;
                            }
                        }
                        if (clearAirAbove && rng.NextDouble() < 0.25)
                        {
                            int stemH = rng.Next(3, 5);
                            for (int sy = y - stemH; sy < y; sy++)
                                chunk.SetTile(lx, sy, WorldConstants.TileMushroomStem);
                            int capY = y - stemH;
                            for (int mx = lx - 1; mx <= lx + 1; mx++)
                            {
                                if (mx >= 0 && mx < ChunkData.Width && capY >= 0 && capY < ChunkData.Height)
                                    chunk.SetTile(mx, capY, WorldConstants.TileMushroomCap);
                            }
                        }
                    }
                }
            }

            // 5c. Underground Naturally Placed Treasure Chests
            if (rng.NextDouble() < 0.45)
            {
                bool chestPlaced = false;
                for (int y = WorldConstants.UndergroundLevel + 5; y < ChunkData.Height - 25; y++)
                {
                    if (chestPlaced) break;
                    for (int lx = 2; lx < ChunkData.Width - 2; lx++)
                    {
                        int floor = chunk.GetTile(lx, y);
                        if (floor == WorldConstants.TileStone || floor == WorldConstants.TileSandstone ||
                            floor == WorldConstants.TileIce || floor == WorldConstants.TileBlightstone ||
                            floor == WorldConstants.TileMushroomGrass)
                        {
                            if (chunk.GetTile(lx, y - 1) == WorldConstants.TileAir && chunk.GetTile(lx, y - 2) == WorldConstants.TileAir)
                            {
                                chunk.SetTile(lx, y - 1, WorldConstants.TileChest);
                                chestPlaced = true;
                                break;
                            }
                        }
                    }
                }
            }

            // 6. Grand Biome Dungeons & Sky Citadel
            // 6a. Forest Nether Dungeon (Lord Malus - Center gx = 0)
            if (chunkX >= -2 && chunkX <= 2)
            {
                CarveGrandBiomeDungeon(chunk, centerGx: 0, WorldConstants.TileDungeonBrick, WorldConstants.WallDungeon);
                CarveSkyCitadel(chunk);
            }

            // 6b. Magma / Underworld Dungeon (Ignis Colossus - Center gx = 80)
            if (chunkX >= 3 && chunkX <= 7)
            {
                CarveGrandBiomeDungeon(chunk, centerGx: 80, WorldConstants.TileDungeonMagma, WorldConstants.WallDungeonMagma);
            }

            // 6c. Glacial Crypt (Cryo-Spud - Center gx = -80)
            if (chunkX >= -7 && chunkX <= -3)
            {
                CarveGrandBiomeDungeon(chunk, centerGx: -80, WorldConstants.TileDungeonIce, WorldConstants.WallDungeonIce);
            }

            // 6d. Catacombs / Blight Ossuary (Necro-Tuber - Center gx = 140)
            if (chunkX >= 7 && chunkX <= 11)
            {
                CarveGrandBiomeDungeon(chunk, centerGx: 140, WorldConstants.TileDungeonBone, WorldConstants.WallDungeonBone);
            }

            // 7. Bedrock Floor (Bottom of the world: y >= Height - 3)
            for (int lx = 0; lx < ChunkData.Width; lx++)
            {
                for (int y = ChunkData.Height - 3; y < ChunkData.Height; y++)
                {
                    chunk.SetTile(lx, y, WorldConstants.TileBedrock);
                }
            }

            return chunk;
        }

        private void CarveGrandBiomeDungeon(ChunkData chunk, int centerGx, int brickTile, int wallId)
        {
            for (int lx = 0; lx < ChunkData.Width; lx++)
            {
                int gx = chunk.ChunkX * ChunkData.Width + lx;
                int dx = gx - centerGx;
                if (Math.Abs(dx) > 22) continue;

                // Subtle Cavern Marker Signs
                if (Math.Abs(dx) == 6 || Math.Abs(dx) == 12 || Math.Abs(dx) == 18)
                {
                    int[] markerY = { 148, 149, 151, 152 };
                    foreach (int my in markerY)
                    {
                        chunk.SetTile(lx, my, brickTile);
                        chunk.SetWall(lx, my, wallId);
                    }
                }

                // Main Dungeon Perimeter & Chambers (y = 162..218)
                for (int y = 162; y <= 218; y++)
                {
                    if (Math.Abs(dx) == 22 || y == 162 || y == 218)
                    {
                        chunk.SetTile(lx, y, brickTile);
                        chunk.SetWall(lx, y, wallId);
                    }
                    else
                    {
                        chunk.SetTile(lx, y, WorldConstants.TileAir);
                        chunk.SetWall(lx, y, wallId);
                    }
                }

                // Level 1: Entrance Vestibule (y = 163..172)
                if (Math.Abs(dx) != 17 && Math.Abs(dx) != 18)
                    chunk.SetTile(lx, 172, brickTile);
                if (Math.Abs(dx) == 9 || Math.Abs(dx) == 10)
                {
                    for (int gy = 168; gy <= 171; gy++)
                        chunk.SetTile(lx, gy, WorldConstants.TileDungeonGate);
                }
                if (Math.Abs(dx) == 5 || Math.Abs(dx) == 12 || Math.Abs(dx) == 19)
                    chunk.SetTile(lx, 169, WorldConstants.TileTorch);

                // Level 2: Middle Wings & Central Bridge (y = 173..194)
                if (Math.Abs(dx) > 6)
                    chunk.SetTile(lx, 194, brickTile);
                if (Math.Abs(dx) <= 7 || Math.Abs(dx) >= 9)
                    chunk.SetTile(lx, 183, brickTile);

                if ((dx >= -18 && dx <= -10) || (dx >= 10 && dx <= 18))
                    chunk.SetTile(lx, 177, WorldConstants.TileWoodPlatform);
                if ((dx >= -19 && dx <= -11) || (dx >= 11 && dx <= 19))
                    chunk.SetTile(lx, 188, WorldConstants.TileWoodPlatform);

                if (Math.Abs(dx) == 10 || Math.Abs(dx) == 16)
                {
                    chunk.SetTile(lx, 176, WorldConstants.TileTorch);
                    chunk.SetTile(lx, 187, WorldConstants.TileTorch);
                }

                // Level 3: Grand Boss Arena (y = 195..217)
                if ((dx >= -16 && dx <= -6) || (dx >= 6 && dx <= 16))
                    chunk.SetTile(lx, 201, WorldConstants.TileWoodPlatform);
                if ((dx >= -19 && dx <= -11) || (dx >= -4 && dx <= 4) || (dx >= 11 && dx <= 19))
                    chunk.SetTile(lx, 207, WorldConstants.TileWoodPlatform);
                if ((dx >= -15 && dx <= -7) || (dx >= 7 && dx <= 15))
                    chunk.SetTile(lx, 212, WorldConstants.TileWoodPlatform);

                if (Math.Abs(dx) == 2 || Math.Abs(dx) == 8 || Math.Abs(dx) == 14 || Math.Abs(dx) == 20)
                {
                    chunk.SetTile(lx, 214, WorldConstants.TileTorch);
                    chunk.SetTile(lx, 200, WorldConstants.TileTorch);
                }

                // Boss Altar at arena floor center
                if (dx == 0)
                {
                    chunk.SetTile(lx, 216, WorldConstants.TileDungeonAltar);
                }
            }
        }

        private void CarveSkyCitadel(ChunkData chunk)
        {
            const int citadelFloor = -163;
            const int citadelCeiling = -185;

            for (int lx = 0; lx < ChunkData.Width; lx++)
            {
                int gx = chunk.ChunkX * ChunkData.Width + lx;
                if (Math.Abs(gx) > 22) continue;

                for (int y = citadelCeiling; y <= citadelFloor + 1; y++)
                {
                    chunk.SetWall(lx, y, WorldConstants.WallDungeon);
                    chunk.SetTile(lx, y, WorldConstants.TileAir);
                }

                for (int y = citadelCeiling + 1; y <= citadelFloor + 1; y++)
                {
                    if (Math.Abs(gx) == 22 || y == citadelCeiling + 1 || y == citadelFloor + 1)
                        chunk.SetTile(lx, y, WorldConstants.TileDungeonBrick);
                }

                chunk.SetTile(lx, citadelFloor, WorldConstants.TileDungeonBrick);
                chunk.SetTile(lx, citadelFloor + 1, WorldConstants.TileDungeonBrick);

                if (gx == 0)
                    chunk.SetTile(lx, citadelFloor - 1, WorldConstants.TileDungeonAltar);

                if (Math.Abs(gx) == 6 || Math.Abs(gx) == 12 || Math.Abs(gx) == 18)
                {
                    for (int py = citadelCeiling + 6; py < citadelFloor; py++)
                        chunk.SetTile(lx, py, WorldConstants.TileDungeonBrick);
                }

                if ((gx >= -16 && gx <= -8) || (gx >= 8 && gx <= 16))
                    chunk.SetTile(lx, citadelFloor - 6, WorldConstants.TileWoodPlatform);
                if (gx >= -10 && gx <= 10)
                    chunk.SetTile(lx, citadelFloor - 11, WorldConstants.TileWoodPlatform);

                if (Math.Abs(gx) == 4 || Math.Abs(gx) == 10 || Math.Abs(gx) == 16)
                    chunk.SetTile(lx, citadelCeiling + 3, WorldConstants.TileSpectralLantern);
            }
        }
    }
}
