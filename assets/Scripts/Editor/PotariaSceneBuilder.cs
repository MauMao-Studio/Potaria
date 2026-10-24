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
            cam.orthographicSize = 11.25f; // Exactly 22.5 tiles tall (matches Pygame 1280x720 / 32px)
            cam.clearFlags = CameraClearFlags.SolidColor;
            cam.backgroundColor = new Color(0.50f, 0.76f, 0.84f, 1.0f); // Soft daylight pastel cyan sky matching Pygame reference

            var uCamData = camObj.AddComponent<UniversalAdditionalCameraData>();
            uCamData.renderPostProcessing = true;

            var pixelCam = camObj.AddComponent<PixelPerfectCamera>();
            pixelCam.assetsPPU = 16;
            pixelCam.refResolutionX = 640;
            pixelCam.refResolutionY = 360;
            pixelCam.cropFrame = PixelPerfectCamera.CropFrame.None;
            pixelCam.gridSnapping = PixelPerfectCamera.GridSnapping.UpscaleRenderTexture;

            var camController = camObj.AddComponent<CameraController>();

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
            chunkManager.ViewDistanceChunks = 2;
            chunkManager.Tilemaps = worldTilemaps;

            var db = AssetDatabase.LoadAssetAtPath<TileDatabase>("Assets/ScriptableObjects/TileDatabase.asset");
            if (db == null)
            {
                PotariaTileImporter.GenerateAllTileAssets();
                db = AssetDatabase.LoadAssetAtPath<TileDatabase>("Assets/ScriptableObjects/TileDatabase.asset");
            }
            chunkManager.Database = db;

            // 5. 2D Ambient Global Light (Clean static illumination for Sprite-Lit 2D tilemaps)
            var lightObj = new GameObject("Global Light 2D");
            lightObj.transform.position = Vector3.zero;

            var globalLight = lightObj.AddComponent<Light2D>();
            globalLight.lightType = Light2D.LightType.Global;
            globalLight.color = Color.white;
            globalLight.intensity = 1.0f;

            // 6. Input Manager (Supports WASD / Arrow camera panning and Z zoom)
            var inputObj = new GameObject("InputManager");
            inputObj.AddComponent<PotariaInput>();

            // 7. Configure Camera Zoom (Default 1x)
            camController.SetZoomLevel(1);

            // 8. Pre-paint spawn terrain corridor around the Camera into tilemaps
            chunkManager.StreamingTarget = camObj.transform;
            chunkManager.UpdateStreaming(true);

            // 9. Save Scene
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
