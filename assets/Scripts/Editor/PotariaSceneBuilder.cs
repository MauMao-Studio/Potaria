using System;
using System.IO;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.Rendering;
using UnityEngine.Rendering.Universal;
using UnityEngine.Tilemaps;
using UnityEngine.U2D;
using Potaria.World;
using Potaria.World.Lighting;
using Potaria.Input;
using Potaria.Player;
using Potaria.RPG;
using Potaria.Combat;
using Potaria.Cameras;
using Potaria.UI;
using Potaria.Mob;
using Potaria.Localization;

namespace Potaria.Editor
{
    /// <summary>
    /// Constructs the official Assets/Scenes/MainWorld.unity scene.
    /// Sets up the Grid hierarchy, Dual-Tilemaps, CompositeCollider2D, ChunkManager,
    /// 2D URP Day/Night lighting, and Pixel Perfect Camera.
    /// Can be executed headless via Potaria.Editor.PotariaSceneBuilder.BuildMainWorldScene.
    /// </summary>
    public static class PotariaSceneBuilder
    {
        private const string SCENE_DIR = "Assets/Scenes";
        private const string SCENE_PATH = "Assets/Scenes/MainWorld.unity";
        private const string PREFAB_DIR = "Assets/Prefabs";

        [MenuItem("Potaria/Build Main World Scene", priority = 20)]
        public static void BuildMainWorldScene()
        {
            Debug.Log("[PotariaSceneBuilder] Starting MainWorld scene construction...");

            EnsureDirectories();
            SetupSortingLayers();
            EnsureUniversalRenderPipeline2D();

            // 1. Create a fresh scene
            var scene = EditorSceneManager.NewScene(NewSceneSetup.EmptyScene, NewSceneMode.Single);

            // 2. Main Camera with Pixel Perfect & URP Data
            var camObj = new GameObject("Main Camera");
            camObj.tag = "MainCamera";
            // Place camera at spawn: gx = 0, ty = 67 (ground is ~70), so Y = -67
            camObj.transform.position = new Vector3(0f, -67f, -10f);

            var cam = camObj.AddComponent<Camera>();
            cam.orthographic = true;
            cam.orthographicSize = 10f;
            cam.clearFlags = CameraClearFlags.SolidColor;
            cam.backgroundColor = new Color(0.40f, 0.65f, 0.95f, 1.0f); // Bright sky blue

            var uCamData = camObj.AddComponent<UniversalAdditionalCameraData>();
            uCamData.renderPostProcessing = true;

            var pixelCam = camObj.AddComponent<PixelPerfectCamera>();
            pixelCam.assetsPPU = 16;
            pixelCam.refResolutionX = 640;
            pixelCam.refResolutionY = 360;
            pixelCam.cropFrame = PixelPerfectCamera.CropFrame.StretchFill;
            pixelCam.gridSnapping = PixelPerfectCamera.GridSnapping.UpscaleRenderTexture;

            var camController = camObj.AddComponent<CameraController>();
            var skyRenderer = camObj.AddComponent<SkyRenderer2D>();

            // 3. Grid Hierarchy & Dual Tilemaps
            var gridObj = new GameObject("Grid");
            gridObj.transform.position = Vector3.zero;
            var grid = gridObj.AddComponent<Grid>();
            grid.cellSize = new Vector3(1f, 1f, 0f);
            grid.cellLayout = GridLayout.CellLayout.Rectangle;

            var worldTilemaps = gridObj.AddComponent<WorldTilemaps>();
            worldTilemaps.ValidateOrBuildLayers();

            // 4. World Manager & Chunk Manager
            var worldManagerObj = new GameObject("WorldManager");
            worldManagerObj.transform.position = Vector3.zero;

            var chunkManager = worldManagerObj.AddComponent<ChunkManager>();
            chunkManager.ViewDistanceChunks = 4;
            chunkManager.Tilemaps = worldTilemaps;

            var db = AssetDatabase.LoadAssetAtPath<TileDatabase>("Assets/ScriptableObjects/TileDatabase.asset");
            if (db == null)
            {
                PotariaTileImporter.GenerateAllTileAssets();
                db = AssetDatabase.LoadAssetAtPath<TileDatabase>("Assets/ScriptableObjects/TileDatabase.asset");
            }
            chunkManager.Database = db;

            // 5. 2D Lighting Hierarchy
            var lightObj = new GameObject("Global Light 2D");
            lightObj.transform.position = Vector3.zero;

            var globalLight = lightObj.AddComponent<Light2D>();
            globalLight.lightType = Light2D.LightType.Global;
            globalLight.color = new Color(1.0f, 0.98f, 0.92f, 1.0f);
            globalLight.intensity = 1.0f;

            var dayNight = lightObj.AddComponent<DayNightCycle2D>();
            dayNight.GlobalLight = globalLight;

            var darkness = lightObj.AddComponent<SubterraneanDarkness2D>();

            // 6. Placed Light Prefab & Spawn Torches with 2D Shadows
            BuildTorchPrefab();
            var torchPrefab = AssetDatabase.LoadAssetAtPath<GameObject>($"{PREFAB_DIR}/Torch_Light.prefab");
            if (torchPrefab != null)
            {
                var torch1 = (GameObject)PrefabUtility.InstantiatePrefab(torchPrefab);
                torch1.transform.position = new Vector3(-3.5f, -66.5f, 0f);

                var torch2 = (GameObject)PrefabUtility.InstantiatePrefab(torchPrefab);
                torch2.transform.position = new Vector3(3.5f, -66.5f, 0f);
            }

            // 7. Input Manager & Projectile Manager
            var inputObj = new GameObject("InputManager");
            inputObj.AddComponent<PotariaInput>();

            var projManagerObj = new GameObject("ProjectileManager");
            projManagerObj.AddComponent<ProjectileManager>();

            // 8. Player Character Spud Hero
            var playerObj = new GameObject("Player_Spud");
            playerObj.tag = "Player";
            playerObj.transform.position = new Vector3(0f, -67f, 0f);

            var playerRb = playerObj.AddComponent<Rigidbody2D>();
            playerRb.interpolation = RigidbodyInterpolation2D.Interpolate;
            playerRb.collisionDetectionMode = CollisionDetectionMode2D.Continuous;
            playerRb.freezeRotation = true;

            var playerCol = playerObj.AddComponent<BoxCollider2D>();
            playerCol.size = new Vector2(0.875f, 1.0f);
            playerCol.offset = new Vector2(0f, 0.5f);
            playerCol.sharedMaterial = new PhysicsMaterial2D("Player_Frictionless") { friction = 0f, bounciness = 0f };

            var playerSr = playerObj.AddComponent<SpriteRenderer>();
            playerSr.sortingLayerName = "Player";
            var idleSprite = AssetDatabase.LoadAssetAtPath<Sprite>("Assets/Sprites/Player/idle.png");
            if (idleSprite == null) idleSprite = AssetDatabase.LoadAssetAtPath<Sprite>("Assets/player/idle.png");
            if (idleSprite != null) playerSr.sprite = idleSprite;

            var playerStats = playerObj.AddComponent<PlayerStats>();
            var playerController = playerObj.AddComponent<PlayerController>();
            playerController.ConfigurePhysics();
            playerController.LoadDefaultSpritesIfMissing();

            // Weapon Pivot Child
            var weaponPivot = new GameObject("WeaponPivot");
            weaponPivot.transform.SetParent(playerObj.transform, false);
            weaponPivot.transform.localPosition = new Vector3(0.2f, 0.5f, 0f);
            var weaponSr = weaponPivot.AddComponent<SpriteRenderer>();
            weaponSr.sortingLayerName = "Player";
            weaponSr.sortingOrder = 1;

            playerObj.AddComponent<WeaponController>();

            // Configure Camera Follow target
            camController.SetZoomLevel(1);

            // 9. Mobs & Dynamic Mob Spawner
            var spawnerObj = new GameObject("MobSpawner");
            spawnerObj.transform.position = Vector3.zero;
            var spawner = spawnerObj.AddComponent<MobSpawner>();
            var spawnerSo = new SerializedObject(spawner);
            spawnerSo.FindProperty("player").objectReferenceValue = playerController;
            spawnerSo.FindProperty("dayNight").objectReferenceValue = dayNight;
            spawnerSo.ApplyModifiedPropertiesWithoutUndo();
            spawner.SpawnInitialMobs();

            // 10. Complete In-Game HUD (Canvas 1280x720)
            var canvasObj = new GameObject("HUD_Canvas");
            var hud = canvasObj.AddComponent<PotariaHUD>();
            var hudSo = new SerializedObject(hud);
            hudSo.FindProperty("player").objectReferenceValue = playerController;
            hudSo.FindProperty("playerStats").objectReferenceValue = playerStats;
            hudSo.FindProperty("dayNightCycle").objectReferenceValue = dayNight;
            hudSo.FindProperty("input").objectReferenceValue = inputObj.GetComponent<PotariaInput>();
            hudSo.ApplyModifiedPropertiesWithoutUndo();
            hud.LoadResourcesIfMissing();
            hud.BuildOrValidateUI();

            // 11. Save Scene
            EditorSceneManager.SaveScene(scene, SCENE_PATH);
            Debug.Log($"[PotariaSceneBuilder] Successfully constructed and saved {SCENE_PATH}.");

            // 8. Register Scene in EditorBuildSettings
            var scenes = EditorBuildSettings.scenes;
            bool alreadyInBuild = false;
            foreach (var s in scenes)
            {
                if (s.path == SCENE_PATH)
                {
                    alreadyInBuild = true;
                    break;
                }
            }

            if (!alreadyInBuild)
            {
                var newScenes = new EditorBuildSettingsScene[scenes.Length + 1];
                Array.Copy(scenes, newScenes, scenes.Length);
                newScenes[scenes.Length] = new EditorBuildSettingsScene(SCENE_PATH, true);
                EditorBuildSettings.scenes = newScenes;
                Debug.Log($"[PotariaSceneBuilder] Registered {SCENE_PATH} in EditorBuildSettings.");
            }
        }

        private static void SetupSortingLayers()
        {
            var tagManagerObj = AssetDatabase.LoadAllAssetsAtPath("ProjectSettings/TagManager.asset");
            if (tagManagerObj == null || tagManagerObj.Length == 0) return;

            var so = new SerializedObject(tagManagerObj[0]);
            var layersProp = so.FindProperty("m_SortingLayers");
            if (layersProp == null) return;

            EnsureSortingLayer(layersProp, "Background", 1001);
            EnsureSortingLayer(layersProp, "Foreground", 1002);
            EnsureSortingLayer(layersProp, "Player", 1003);
            EnsureSortingLayer(layersProp, "UI", 1004);

            so.ApplyModifiedProperties();
        }

        private static void EnsureSortingLayer(SerializedProperty layersProp, string name, int uniqueId)
        {
            for (int i = 0; i < layersProp.arraySize; i++)
            {
                var elem = layersProp.GetArrayElementAtIndex(i);
                var nameProp = elem.FindPropertyRelative("name");
                if (nameProp != null && nameProp.stringValue == name)
                    return; // Already exists
            }

            int index = layersProp.arraySize;
            layersProp.InsertArrayElementAtIndex(index);
            var newElem = layersProp.GetArrayElementAtIndex(index);
            var newName = newElem.FindPropertyRelative("name");
            var newId = newElem.FindPropertyRelative("uniqueID");
            var newLocked = newElem.FindPropertyRelative("locked");

            if (newName != null) newName.stringValue = name;
            if (newId != null) newId.intValue = uniqueId;
            if (newLocked != null) newLocked.intValue = 0;
        }

        private static void BuildTorchPrefab()
        {
            EnsureDirectories();
            string prefabPath = $"{PREFAB_DIR}/Torch_Light.prefab";

            var torchObj = new GameObject("Torch_Light");
            var light2D = torchObj.AddComponent<Light2D>();
            light2D.lightType = Light2D.LightType.Point;
            light2D.color = new Color(1.0f, 0.85f, 0.40f, 1.0f);
            light2D.pointLightInnerRadius = 0.5f;
            light2D.pointLightOuterRadius = 6.0f;
            light2D.intensity = 1.0f;
            light2D.shadowsEnabled = true;
            light2D.shadowIntensity = 0.70f;

            var pointSource = torchObj.AddComponent<PointLightSource2D>();
            pointSource.Configure(new Color(1.0f, 0.85f, 0.40f, 1.0f), 6.0f, 1.0f, true);

            var sr = torchObj.AddComponent<SpriteRenderer>();
            sr.sortingLayerName = "Foreground";
            sr.sortingOrder = 5;
            var torchSprite = AssetDatabase.LoadAssetAtPath<Sprite>("Assets/items/torch.png");
            if (torchSprite == null) torchSprite = AssetDatabase.LoadAssetAtPath<Sprite>("Assets/Sprites/Items/torch.png");
            if (torchSprite != null) sr.sprite = torchSprite;

            PrefabUtility.SaveAsPrefabAsset(torchObj, prefabPath);
            GameObject.DestroyImmediate(torchObj);
        }

        private static void EnsureDirectories()
        {
            if (!Directory.Exists(SCENE_DIR)) Directory.CreateDirectory(SCENE_DIR);
            if (!Directory.Exists(PREFAB_DIR)) Directory.CreateDirectory(PREFAB_DIR);
            AssetDatabase.Refresh();
        }

        public static UniversalRenderPipelineAsset EnsureUniversalRenderPipeline2D()
        {
            EnsureDirectories();
            string settingsDir = "Assets/Settings";
            if (!Directory.Exists(settingsDir)) Directory.CreateDirectory(settingsDir);

            string rendererPath = $"{settingsDir}/UniversalRenderPipeline2D_Renderer.asset";
            string urpAssetPath = $"{settingsDir}/UniversalRenderPipeline2D.asset";

            var urpAsset = AssetDatabase.LoadAssetAtPath<UniversalRenderPipelineAsset>(urpAssetPath);
            if (urpAsset == null)
            {
                var rendererData = AssetDatabase.LoadAssetAtPath<Renderer2DData>(rendererPath);
                if (rendererData == null)
                {
                    rendererData = ScriptableObject.CreateInstance<Renderer2DData>();
                    AssetDatabase.CreateAsset(rendererData, rendererPath);
                    ResourceReloader.ReloadAllNullIn(rendererData, "Packages/com.unity.render-pipelines.universal");
                }

                urpAsset = UniversalRenderPipelineAsset.Create(rendererData);
                AssetDatabase.CreateAsset(urpAsset, urpAssetPath);
                ResourceReloader.ReloadAllNullIn(urpAsset, "Packages/com.unity.render-pipelines.universal");
                AssetDatabase.SaveAssets();
                Debug.Log($"[PotariaSceneBuilder] Created 2D URP Asset at {urpAssetPath}");
            }

            if (GraphicsSettings.defaultRenderPipeline != urpAsset)
            {
                GraphicsSettings.defaultRenderPipeline = urpAsset;
                Debug.Log("[PotariaSceneBuilder] Assigned GraphicsSettings.defaultRenderPipeline to UniversalRenderPipeline2D.");
            }
            if (QualitySettings.renderPipeline != urpAsset)
            {
                QualitySettings.renderPipeline = urpAsset;
                Debug.Log("[PotariaSceneBuilder] Assigned QualitySettings.renderPipeline to UniversalRenderPipeline2D.");
            }
            string[] qualityNames = QualitySettings.names;
            for (int i = 0; i < qualityNames.Length; i++)
            {
                QualitySettings.SetQualityLevel(i, false);
                QualitySettings.renderPipeline = urpAsset;
            }

            return urpAsset;
        }
    }
}
