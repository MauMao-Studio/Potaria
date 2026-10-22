using System;
using System.Collections.Generic;
using UnityEditor;
using UnityEngine;
using UnityEngine.Rendering;
using UnityEngine.Rendering.Universal;
using UnityEngine.Tilemaps;
using Potaria.World;
using Potaria.World.Lighting;

namespace Potaria.Editor
{
    /// <summary>
    /// Headless verification test suite for Milestone 2:
    /// - Procedural noise & multi-octave synthesis
    /// - TileDatabase & TileDefinition asset integrity
    /// - WorldGenerator terrain, biomes, caves, ores, and dungeons
    /// - Dual-Tilemap CompositeCollider2D polygon configuration
    /// - ChunkManager chunk streaming, mining mechanics, and 4-block water hydration
    /// - 2D URP Day/Night lighting and subterranean depth darkness
    ///
    /// Executed in batchmode via:
    /// Potaria.Editor.PotariaWorldTest.RunTests
    /// </summary>
    public static class PotariaWorldTest
    {
        private static int s_passedTests = 0;
        private static int s_failedTests = 0;

        [MenuItem("Potaria/Run Milestone 2 Tests", priority = 30)]
        public static void RunTests()
        {
            s_passedTests = 0;
            s_failedTests = 0;

            Debug.Log("================================================================================");
            Debug.Log("[PotariaWorldTest] Executing Milestone 2 Verification Test Suite...");
            Debug.Log("================================================================================");

            try
            {
                // First ensure tile assets and database are generated
                PotariaTileImporter.GenerateAllTileAssets();

                TestPerlinNoise();
                TestTileDatabase();
                TestWorldGenerator();
                TestOreSeedingAndDistribution();
                TestDungeonCaveProtection();
                TestDualTilemapsAndCompositeCollider();
                TestChunkManagerStreamingAndMining();
                TestFarmlandHydration();
                TestPointLight2DSpawningAndPooling();
                TestTilemapLitMaterialsAndWaterTrigger();
                TestLightingAndDepthDarkness();
                TestRenderPipelineConfiguration();
                TestMainWorldSceneBuilding();
            }
            catch (Exception ex)
            {
                s_failedTests++;
                Debug.LogError($"[PotariaWorldTest] Unexpected exception during test execution: {ex}");
            }

            Debug.Log("================================================================================");
            Debug.Log($"[PotariaWorldTest] Test Execution Summary: {s_passedTests} Passed, {s_failedTests} Failed.");
            Debug.Log("================================================================================");

            if (s_failedTests > 0)
            {
                Debug.LogError($"[PotariaWorldTest] FATAL: {s_failedTests} test(s) failed!");
                if (Application.isBatchMode)
                {
                    EditorApplication.Exit(1);
                }
            }
            else
            {
                Debug.Log("[PotariaWorldTest] SUCCESS: All Milestone 2 systems verified with 0 errors.");
                if (Application.isBatchMode)
                {
                    EditorApplication.Exit(0);
                }
            }
        }

        private static void AssertTrue(bool condition, string testName, string message = "")
        {
            if (condition)
            {
                s_passedTests++;
                Debug.Log($"[PASS] {testName}");
            }
            else
            {
                s_failedTests++;
                Debug.LogError($"[FAIL] {testName}: {message}");
            }
        }

        private static void TestPerlinNoise()
        {
            var noise1 = new PerlinNoise(42424);
            var noise2 = new PerlinNoise(42424);
            var noiseDiff = new PerlinNoise(99999);

            // Determinism check
            float v1 = noise1.Fractal1D(12.5f, 3);
            float v2 = noise2.Fractal1D(12.5f, 3);
            AssertTrue(Mathf.Approximately(v1, v2), "PerlinNoise.Determinism1D", $"Same seed must give identical output: {v1} != {v2}");

            float vDiff = noiseDiff.Fractal1D(12.5f, 3);
            AssertTrue(!Mathf.Approximately(v1, vDiff), "PerlinNoise.SeedVariance1D", "Different seeds should produce different noise values");

            // Range checks
            bool inRange = true;
            for (int i = 0; i < 50; i++)
            {
                float val = noise1.Fractal2D(i * 0.1f, i * 0.1f, 4);
                if (val < -1.5f || val > 1.5f)
                {
                    inRange = false;
                    break;
                }
            }
            AssertTrue(inRange, "PerlinNoise.OutputRange2D", "Noise outputs should remain bounded within reasonable fractal range");
        }

        private static void TestTileDatabase()
        {
            var db = TileDatabase.Instance;
            AssertTrue(db != null, "TileDatabase.InstanceNotNull", "TileDatabase singleton must be instantiated");
            AssertTrue(db.TileDefinitions.Count >= 70, "TileDatabase.TileCount", $"Expected at least 70 tile definitions, found {db.TileDefinitions.Count}");
            AssertTrue(db.WallDefinitions.Count >= 13, "TileDatabase.WallCount", $"Expected at least 13 wall definitions, found {db.WallDefinitions.Count}");

            // Verify Dirt
            var dirt = db.GetTile(WorldConstants.TileDirt);
            AssertTrue(dirt != null && dirt.Hardness == 15 && dirt.IsSolid && dirt.RequiredTool == ToolType.Shovel,
                "TileDatabase.DirtDefinition", "Dirt must have hardness 15, be solid, and require Shovel");

            // Verify Stone
            var stone = db.GetTile(WorldConstants.TileStone);
            AssertTrue(stone != null && stone.Hardness == 35 && stone.IsSolid && stone.RequiredTool == ToolType.Pickaxe,
                "TileDatabase.StoneDefinition", "Stone must have hardness 35, be solid, and require Pickaxe");

            // Verify Bedrock
            var bedrock = db.GetTile(WorldConstants.TileBedrock);
            AssertTrue(bedrock != null && bedrock.IsIndestructible && bedrock.Hardness >= 9999,
                "TileDatabase.BedrockDefinition", "Bedrock must be indestructible");

            // Verify Torch
            var torch = db.GetTile(WorldConstants.TileTorch);
            AssertTrue(torch != null && torch.LightEmission >= 10 && !torch.IsSolid,
                "TileDatabase.TorchDefinition", "Torch must emit light >= 10 and not be solid");

            // Verify Platform
            var plat = db.GetTile(WorldConstants.TileWoodPlatform);
            AssertTrue(plat != null && plat.IsPlatform && !plat.IsSolid,
                "TileDatabase.WoodPlatformDefinition", "Wood platform must have IsPlatform = true and IsSolid = false");
        }

        private static void TestWorldGenerator()
        {
            var gen = new WorldGenerator(54321);

            // Generate spawn chunk
            var chunk0 = gen.GenerateChunk(0);
            AssertTrue(chunk0 != null, "WorldGenerator.Chunk0NotNull", "Spawn chunk 0 must generate");
            AssertTrue(chunk0.ChunkX == 0, "WorldGenerator.ChunkXCorrect", "ChunkX must be 0");

            // Surface heights bounded
            bool heightsValid = true;
            for (int lx = 0; lx < ChunkData.Width; lx++)
            {
                int h = chunk0.SurfaceHeights[lx];
                if (h < 35 || h > ChunkData.Height - 90)
                {
                    heightsValid = false;
                    break;
                }
            }
            AssertTrue(heightsValid, "WorldGenerator.SurfaceHeightsRange", "Surface heights must be within [35, 150]");

            // Bedrock at bottom
            bool bedrockValid = true;
            for (int lx = 0; lx < ChunkData.Width; lx++)
            {
                if (chunk0.GetTile(lx, ChunkData.Height - 1) != WorldConstants.TileBedrock ||
                    chunk0.GetTile(lx, ChunkData.Height - 2) != WorldConstants.TileBedrock)
                {
                    bedrockValid = false;
                    break;
                }
            }
            AssertTrue(bedrockValid, "WorldGenerator.BedrockFloor", "Bottom 2-3 layers must be indestructible Bedrock");

            // Nether Dungeon at chunk 0 deep underground
            bool dungeonBrickFound = false;
            bool altarFound = false;
            for (int lx = 0; lx < ChunkData.Width; lx++)
            {
                for (int y = 162; y <= 218; y++)
                {
                    int tid = chunk0.GetTile(lx, y);
                    if (tid == WorldConstants.TileDungeonBrick) dungeonBrickFound = true;
                    if (tid == WorldConstants.TileDungeonAltar) altarFound = true;
                }
            }
            AssertTrue(dungeonBrickFound, "WorldGenerator.NetherDungeonBricks", "Chunk 0 must contain Nether Dungeon bricks");
            AssertTrue(altarFound, "WorldGenerator.NetherDungeonAltar", "Chunk 0 must contain the Dungeon Altar");

            // Test Biome diversity across distant chunks
            var biomesFound = new HashSet<string>();
            for (int cx = -30; cx <= 30; cx += 5)
            {
                var chk = gen.GenerateChunk(cx);
                foreach (var b in chk.ColBiomes)
                {
                    biomesFound.Add(b);
                }
            }
            AssertTrue(biomesFound.Contains(WorldConstants.BiomeForest), "WorldGenerator.BiomeForest", "Forest biome must generate");
            AssertTrue(biomesFound.Contains(WorldConstants.BiomeDesert), "WorldGenerator.BiomeDesert", "Desert biome must generate");
            AssertTrue(biomesFound.Contains(WorldConstants.BiomeSnow), "WorldGenerator.BiomeSnow", "Snow biome must generate");
            AssertTrue(biomesFound.Contains(WorldConstants.BiomeBlight), "WorldGenerator.BiomeBlight", "Blight biome must generate");
        }

        private static void TestDualTilemapsAndCompositeCollider()
        {
            var go = new GameObject("Test_Grid");
            try
            {
                var grid = go.AddComponent<Grid>();
                var worldTilemaps = go.AddComponent<WorldTilemaps>();
                worldTilemaps.ValidateOrBuildLayers();

                AssertTrue(worldTilemaps.ForegroundTilemap != null, "WorldTilemaps.ForegroundNotNull", "Foreground tilemap must exist");
                AssertTrue(worldTilemaps.BackgroundTilemap != null, "WorldTilemaps.BackgroundNotNull", "Background tilemap must exist");
                AssertTrue(worldTilemaps.PlatformTilemap != null, "WorldTilemaps.PlatformNotNull", "Platform tilemap must exist");

                // Check CompositeCollider2D configuration on Foreground Tilemap
                var comp = worldTilemaps.ForegroundTilemap.GetComponent<CompositeCollider2D>();
                AssertTrue(comp != null, "WorldTilemaps.CompositeColliderNotNull", "Foreground tilemap must have CompositeCollider2D");
                AssertTrue(comp.geometryType == CompositeCollider2D.GeometryType.Polygons, "WorldTilemaps.CompositeGeometryPolygons",
                    "CompositeCollider2D geometryType must be Polygons");

                var tilemapCollider = worldTilemaps.ForegroundTilemap.GetComponent<TilemapCollider2D>();
#pragma warning disable CS0618
                bool isCompositeUsed = tilemapCollider != null && (tilemapCollider.usedByComposite || tilemapCollider.compositeOperation != Collider2D.CompositeOperation.None);
#pragma warning restore CS0618
                AssertTrue(isCompositeUsed, "WorldTilemaps.TilemapColliderUsedByComposite",
                    "Foreground TilemapCollider2D must have usedByComposite = true or compositeOperation configured");

                var rb = worldTilemaps.ForegroundTilemap.GetComponent<Rigidbody2D>();
                AssertTrue(rb != null && rb.bodyType == RigidbodyType2D.Static, "WorldTilemaps.StaticRigidbody",
                    "Foreground tilemap Rigidbody2D must be Static");

                // Coordinate conversion check
                var cell = worldTilemaps.GridToCell(15, 75);
                AssertTrue(cell.x == 15 && cell.y == -75, "WorldTilemaps.GridToCell", $"Expected (15, -75), got ({cell.x}, {cell.y})");

                worldTilemaps.CellToGrid(cell, out int gx, out int ty);
                AssertTrue(gx == 15 && ty == 75, "WorldTilemaps.CellToGrid", $"Expected (15, 75), got ({gx}, {ty})");
            }
            finally
            {
                GameObject.DestroyImmediate(go);
            }
        }

        private static void TestChunkManagerStreamingAndMining()
        {
            var gridObj = new GameObject("Test_ChunkGrid");
            var mgrObj = new GameObject("Test_ChunkManager");
            try
            {
                gridObj.AddComponent<Grid>();
                var worldTilemaps = gridObj.AddComponent<WorldTilemaps>();
                worldTilemaps.ValidateOrBuildLayers();

                var chunkManager = mgrObj.AddComponent<ChunkManager>();
                chunkManager.Tilemaps = worldTilemaps;
                chunkManager.Database = TileDatabase.Instance;
                chunkManager.ViewDistanceChunks = 2;

                // Sync update
                chunkManager.UpdateStreaming(true);

                AssertTrue(chunkManager.LoadedChunks.Count >= 5, "ChunkManager.LoadedChunksCount",
                    $"Expected at least 5 chunks loaded for view distance 2, got {chunkManager.LoadedChunks.Count}");

                // Coordinate Tile Query
                int tileAtSpawn = chunkManager.GetTile(0, ChunkData.Height - 1);
                AssertTrue(tileAtSpawn == WorldConstants.TileBedrock, "ChunkManager.GetTileBedrock", "Tile at bottom must be Bedrock");

                // Test Mining
                // Place test Stone block at (0, 100)
                chunkManager.SetTile(0, 100, WorldConstants.TileStone);
                AssertTrue(chunkManager.GetTile(0, 100) == WorldConstants.TileStone, "ChunkManager.SetTileStone", "Tile at (0, 100) must be Stone");

                // Mine with inappropriate tool (Shovel power 5) -> does small damage (2), stone has hardness 35
                bool broke = chunkManager.DamageTile(0, 100, 5, ToolType.Shovel, 5, out var drop);
                AssertTrue(!broke, "ChunkManager.MiningShovelVsStoneNotBroken", "Shovel power 5 should not break stone with hardness 35 in one hit");
                AssertTrue(chunkManager.GetTile(0, 100) == WorldConstants.TileStone, "ChunkManager.TileStillStone", "Stone block should remain placed");

                // Mine with high-power Pickaxe (power 30) -> effective damage 60 >= 35 -> breaks stone!
                broke = chunkManager.DamageTile(0, 100, 30, ToolType.Pickaxe, 30, out drop);
                AssertTrue(broke, "ChunkManager.MiningPickaxeBreaksStone", "High-power Pickaxe must break stone block");
                AssertTrue(chunkManager.GetTile(0, 100) == WorldConstants.TileAir, "ChunkManager.StoneReplacedByAir", "Broken stone must be replaced by Air");
            }
            finally
            {
                GameObject.DestroyImmediate(gridObj);
                GameObject.DestroyImmediate(mgrObj);
            }
        }

        private static void TestFarmlandHydration()
        {
            var gridObj = new GameObject("Test_FarmGrid");
            var mgrObj = new GameObject("Test_FarmManager");
            try
            {
                gridObj.AddComponent<Grid>();
                var worldTilemaps = gridObj.AddComponent<WorldTilemaps>();
                worldTilemaps.ValidateOrBuildLayers();

                var chunkManager = mgrObj.AddComponent<ChunkManager>();
                chunkManager.Tilemaps = worldTilemaps;
                chunkManager.Database = TileDatabase.Instance;

                // Place dry farmland at (50, 70)
                chunkManager.SetTile(50, 70, WorldConstants.TileFarmland);
                // Clear any nearby water
                for (int dx = -5; dx <= 5; dx++) chunkManager.SetTile(50 + dx, 70, WorldConstants.TileAir);
                chunkManager.SetTile(50, 70, WorldConstants.TileFarmland);

                // Simulate without water
                chunkManager.SimulateFarmlandHydration(50, 70);
                AssertTrue(chunkManager.GetTile(50, 70) == WorldConstants.TileFarmland, "Farmland.RemainsDryWithoutWater",
                    "Farmland must stay dry without nearby water");

                // Place water 3 blocks away horizontally at (53, 70)
                chunkManager.SetTile(53, 70, WorldConstants.TileWater);
                chunkManager.SimulateFarmlandHydration(50, 70);
                AssertTrue(chunkManager.GetTile(50, 70) == WorldConstants.TileFarmlandWet, "Farmland.HydratesWithWaterInRange",
                    "Farmland must hydrate when water is within 4 blocks horizontally");

                // Remove water -> simulate again -> dries up
                chunkManager.SetTile(53, 70, WorldConstants.TileAir);
                chunkManager.SimulateFarmlandHydration(50, 70);
                AssertTrue(chunkManager.GetTile(50, 70) == WorldConstants.TileFarmland, "Farmland.DriesWhenWaterRemoved",
                    "Farmland must dry up when water source is removed");
            }
            finally
            {
                GameObject.DestroyImmediate(gridObj);
                GameObject.DestroyImmediate(mgrObj);
            }
        }

        private static void TestLightingAndDepthDarkness()
        {
            var lightObj = new GameObject("Test_Light");
            try
            {
                var light2D = lightObj.AddComponent<Light2D>();
                light2D.lightType = Light2D.LightType.Global;

                var cycle = lightObj.AddComponent<DayNightCycle2D>();
                cycle.GlobalLight = light2D;

                // Test Noon
                cycle.SetTime(0.25f);
                AssertTrue(cycle.CurrentPhase == DayNightCycle2D.CelestialPhase.Noon, "DayNight.PhaseNoon", "0.25 must be Noon");
                AssertTrue(light2D.intensity >= 0.95f, "DayNight.IntensityNoon", "Noon light intensity must be near 1.0");

                // Test Night
                cycle.SetTime(0.80f);
                AssertTrue(cycle.CurrentPhase == DayNightCycle2D.CelestialPhase.Night, "DayNight.PhaseNight", "0.80 must be Night");
                AssertTrue(light2D.intensity < 0.40f, "DayNight.IntensityNight", "Night light intensity must be dimmed");

                // Test Subterranean Darkness attenuation calculation
                var darkness = lightObj.AddComponent<SubterraneanDarkness2D>();
                // At surface world Y = -50 (grid Y = 50 < 70) -> attenuation = 1.0
                float surfaceAtten = darkness.CalculateAttenuationAt(-50f);
                AssertTrue(Mathf.Approximately(surfaceAtten, 1.0f), "SubterraneanDarkness.SurfaceFullLight",
                    $"Surface attenuation must be 1.0, got {surfaceAtten}");

                // At deep cavern world Y = -140 (grid Y = 140 > 115) -> attenuation = 0.0
                float cavernAtten = darkness.CalculateAttenuationAt(-140f);
                AssertTrue(Mathf.Approximately(cavernAtten, 0.0f), "SubterraneanDarkness.CavernPitchBlack",
                    $"Cavern attenuation must be 0.0, got {cavernAtten}");
            }
            finally
            {
                GameObject.DestroyImmediate(lightObj);
            }
        }

        private static void TestOreSeedingAndDistribution()
        {
            var db = TileDatabase.Instance;

            // 1. Validate Database definitions for all 6 ores
            int[] oreIds = new int[]
            {
                WorldConstants.TileCoalOre,
                WorldConstants.TileCopperOre,
                WorldConstants.TileIronOre,
                WorldConstants.TileGoldOre,
                WorldConstants.TileDiamondOre,
                WorldConstants.TileNetheriteOre
            };

            foreach (int oid in oreIds)
            {
                var def = db.GetTile(oid);
                AssertTrue(def != null, $"OreDefinition.Exists_{oid}", $"Ore tile ID {oid} must be registered in TileDatabase");
                AssertTrue(def != null && def.IsSolid && def.RequiredTool == ToolType.Pickaxe && def.Hardness >= 25,
                    $"OreDefinition.Properties_{oid}", $"Ore {oid} must be solid, require Pickaxe, and have hardness >= 25");
            }

            // 2. Validate Procedural Seeding across chunks
            var gen = new WorldGenerator(12345);
            var oreCounts = new Dictionary<int, int>();
            foreach (int oid in oreIds) oreCounts[oid] = 0;

            for (int cx = -15; cx <= 15; cx++)
            {
                var chunk = gen.GenerateChunk(cx);
                for (int lx = 0; lx < ChunkData.Width; lx++)
                {
                    for (int y = 0; y < ChunkData.Height; y++)
                    {
                        int tid = chunk.GetTile(lx, y);
                        if (oreCounts.ContainsKey(tid))
                        {
                            oreCounts[tid]++;
                        }
                    }
                }
            }

            AssertTrue(oreCounts[WorldConstants.TileCoalOre] > 0, "WorldGenerator.Ores.CoalSeeded",
                $"Coal Ore must be seeded (found {oreCounts[WorldConstants.TileCoalOre]})");
            AssertTrue(oreCounts[WorldConstants.TileCopperOre] > 0, "WorldGenerator.Ores.CopperSeeded",
                $"Copper Ore must be seeded (found {oreCounts[WorldConstants.TileCopperOre]})");
            AssertTrue(oreCounts[WorldConstants.TileIronOre] > 0, "WorldGenerator.Ores.IronSeeded",
                $"Iron Ore must be seeded (found {oreCounts[WorldConstants.TileIronOre]})");
            AssertTrue(oreCounts[WorldConstants.TileGoldOre] > 0, "WorldGenerator.Ores.GoldSeeded",
                $"Gold Ore must be seeded (found {oreCounts[WorldConstants.TileGoldOre]})");
            AssertTrue(oreCounts[WorldConstants.TileDiamondOre] > 0, "WorldGenerator.Ores.DiamondSeeded",
                $"Diamond Ore must be seeded (found {oreCounts[WorldConstants.TileDiamondOre]})");
            AssertTrue(oreCounts[WorldConstants.TileNetheriteOre] > 0, "WorldGenerator.Ores.NetheriteSeeded",
                $"Netherite Ore must be seeded (found {oreCounts[WorldConstants.TileNetheriteOre]})");
        }

        private static void TestDungeonCaveProtection()
        {
            var gen = new WorldGenerator(88888);

            // Test chunks covering all 4 subterranean dungeons
            // Nether Dungeon: chunks -2..2
            // Glacial Crypt: chunks -7..-3
            // Magma Dungeon: chunks 3..7
            // Catacombs: chunks 7..11
            int[] testChunks = new int[] { 0, -5, 5, 9 };

            foreach (int cx in testChunks)
            {
                var chunk = gen.GenerateChunk(cx);
                int dungeonTileCount = 0;
                for (int lx = 0; lx < ChunkData.Width; lx++)
                {
                    for (int y = 162; y <= 218; y++)
                    {
                        int tid = chunk.GetTile(lx, y);
                        if (tid == WorldConstants.TileDungeonBrick || tid == WorldConstants.TileDungeonMagma ||
                            tid == WorldConstants.TileDungeonIce || tid == WorldConstants.TileDungeonBone ||
                            tid == WorldConstants.TileDungeonAltar || tid == WorldConstants.TileDungeonGate)
                        {
                            dungeonTileCount++;
                        }
                    }
                }

                AssertTrue(dungeonTileCount > 0, $"WorldGenerator.DungeonProtected_Chunk_{cx}",
                    $"Dungeon at chunk {cx} must retain structural bricks without being hollowed out by cave worms (found {dungeonTileCount} bricks)");
            }
        }

        private static void TestPointLight2DSpawningAndPooling()
        {
            var go = new GameObject("Test_LightGrid");
            try
            {
                go.AddComponent<Grid>();
                var worldTilemaps = go.AddComponent<WorldTilemaps>();
                worldTilemaps.ValidateOrBuildLayers();

                var db = TileDatabase.Instance;
                var torchDef = db.GetTile(WorldConstants.TileTorch);
                AssertTrue(torchDef != null, "TileDatabase.TorchDefNotNull", "Torch definition must not be null");

                // Spawn a torch light at global (5, 80)
                worldTilemaps.SpawnOrUpdateLight(5, 80, torchDef);

                Transform container = worldTilemaps.LightsContainer;
                AssertTrue(container != null, "WorldTilemaps.LightsContainerExists", "Lights_Container transform must exist under Grid");

                Transform lightChild = container != null && container.childCount > 0 ? container.GetChild(0) : null;
                AssertTrue(lightChild != null, "WorldTilemaps.PointLightSpawned", "Point light GameObject must be spawned for placed Torch");

                var light2D = lightChild != null ? lightChild.GetComponent<Light2D>() : null;
                AssertTrue(light2D != null && light2D.lightType == Light2D.LightType.Point,
                    "WorldTilemaps.Light2DIsPoint", "Spawned light must have Light2D component of type Point");

                var pointSource = lightChild != null ? lightChild.GetComponent<PointLightSource2D>() : null;
                AssertTrue(pointSource != null, "WorldTilemaps.PointLightSource2DExists", "Spawned light must have PointLightSource2D component");

                // Remove light
                worldTilemaps.RemoveLight(5, 80);
                AssertTrue(container.childCount == 0, "WorldTilemaps.LightRemovedOnClear", "Light GameObject must be destroyed when tile is removed");
            }
            finally
            {
                GameObject.DestroyImmediate(go);
            }
        }

        private static void TestTilemapLitMaterialsAndWaterTrigger()
        {
            var go = new GameObject("Test_Tilemaps_Materials");
            try
            {
                go.AddComponent<Grid>();
                var worldTilemaps = go.AddComponent<WorldTilemaps>();
                worldTilemaps.ValidateOrBuildLayers();

                var fgRend = worldTilemaps.ForegroundTilemap.GetComponent<TilemapRenderer>();
                var bgRend = worldTilemaps.BackgroundTilemap.GetComponent<TilemapRenderer>();
                var platRend = worldTilemaps.PlatformTilemap.GetComponent<TilemapRenderer>();
                var waterRend = worldTilemaps.WaterTilemap.GetComponent<TilemapRenderer>();

                AssertTrue(fgRend != null && fgRend.sharedMaterial != null, "WorldTilemaps.ForegroundMaterialAssigned",
                    "Foreground TilemapRenderer must have a sharedMaterial");
                AssertTrue(bgRend != null && bgRend.sharedMaterial != null, "WorldTilemaps.BackgroundMaterialAssigned",
                    "Background TilemapRenderer must have a sharedMaterial");
                AssertTrue(platRend != null && platRend.sharedMaterial != null, "WorldTilemaps.PlatformMaterialAssigned",
                    "Platform TilemapRenderer must have a sharedMaterial");
                AssertTrue(waterRend != null && waterRend.sharedMaterial != null, "WorldTilemaps.WaterMaterialAssigned",
                    "Water TilemapRenderer must have a sharedMaterial");

                // Verify Sprite-Lit-Default shader assignment
                bool allLit = fgRend.sharedMaterial.shader.name.Contains("Sprite-Lit-Default") &&
                              bgRend.sharedMaterial.shader.name.Contains("Sprite-Lit-Default");
                AssertTrue(allLit, "WorldTilemaps.SpriteLitShaderAssigned",
                    "Tilemaps must use Universal Render Pipeline 2D Sprite-Lit-Default shader");

                // Verify Water Collider Trigger
                var waterCol = worldTilemaps.WaterTilemap.GetComponent<TilemapCollider2D>();
                AssertTrue(waterCol != null && waterCol.isTrigger, "WorldTilemaps.WaterColliderIsTrigger",
                    "Water TilemapCollider2D must have isTrigger = true for player swimming detection");
            }
            finally
            {
                GameObject.DestroyImmediate(go);
            }
        }

        private static void TestRenderPipelineConfiguration()
        {
            var urpAsset = PotariaSceneBuilder.EnsureUniversalRenderPipeline2D();
            AssertTrue(urpAsset != null, "URP2D.PipelineAssetCreated", "UniversalRenderPipelineAsset must be created");
            AssertTrue(GraphicsSettings.defaultRenderPipeline == urpAsset, "URP2D.GraphicsSettingsAssigned",
                "GraphicsSettings.defaultRenderPipeline must be assigned to UniversalRenderPipeline2D");
            AssertTrue(QualitySettings.renderPipeline == urpAsset, "URP2D.QualitySettingsAssigned",
                "QualitySettings.renderPipeline must be assigned to UniversalRenderPipeline2D");
        }

        private static void TestMainWorldSceneBuilding()
        {
            PotariaSceneBuilder.BuildMainWorldScene();
            string scenePath = "Assets/Scenes/MainWorld.unity";
            AssertTrue(System.IO.File.Exists(scenePath), "SceneBuilder.MainWorldSceneExists", $"{scenePath} must exist on disk");
        }
    }
}
