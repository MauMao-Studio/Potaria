using System;
using System.IO;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.Rendering.Universal;
using UnityEngine.Tilemaps;
using UnityEngine.U2D;
using Potaria.World;
using Potaria.World.Lighting;

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
            pixelCam.cropFrame = PixelPerfectCamera.CropFrame.None;

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

            // 6. Placed Light Prefab (Torch with PointLightSource2D)
            BuildTorchPrefab();

            // 7. Save Scene
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
            if (File.Exists(prefabPath)) return;

            var torchObj = new GameObject("Torch_Light");
            var light2D = torchObj.AddComponent<Light2D>();
            light2D.lightType = Light2D.LightType.Point;
            light2D.color = new Color(1.0f, 0.85f, 0.40f, 1.0f);
            light2D.pointLightInnerRadius = 0.5f;
            light2D.pointLightOuterRadius = 6.0f;
            light2D.intensity = 1.0f;

            var pointSource = torchObj.AddComponent<PointLightSource2D>();
            pointSource.Configure(new Color(1.0f, 0.85f, 0.40f, 1.0f), 6.0f, 1.0f, true);

            PrefabUtility.SaveAsPrefabAsset(torchObj, prefabPath);
            GameObject.DestroyImmediate(torchObj);
        }

        private static void EnsureDirectories()
        {
            if (!Directory.Exists(SCENE_DIR)) Directory.CreateDirectory(SCENE_DIR);
            if (!Directory.Exists(PREFAB_DIR)) Directory.CreateDirectory(PREFAB_DIR);
            AssetDatabase.Refresh();
        }
    }
}
