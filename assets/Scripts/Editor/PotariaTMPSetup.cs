using System;
using System.IO;
using UnityEditor;
using UnityEngine;
using TMPro;

namespace Potaria.Editor
{
    public static class PotariaTMPSetup
    {
        [MenuItem("Potaria/Setup TextMeshPro Essentials", priority = 5)]
        public static void ImportTMPEssentials()
        {
            Debug.Log("[PotariaTMPSetup] Checking TMP Essentials...");

            string packagePath = Path.GetFullPath("Library/PackageCache/com.unity.ugui@aa507f3228f0/Package Resources/TMP Essential Resources.unitypackage");
            if (!File.Exists(packagePath))
            {
                // Fallback search in PackageCache
                var matches = Directory.GetFiles("Library/PackageCache", "TMP Essential Resources.unitypackage", SearchOption.AllDirectories);
                if (matches.Length > 0)
                {
                    packagePath = Path.GetFullPath(matches[0]);
                }
            }

            if (File.Exists(packagePath))
            {
                Debug.Log($"[PotariaTMPSetup] Importing TMP Essentials from {packagePath}...");
                AssetDatabase.ImportPackage(packagePath, false);
                AssetDatabase.Refresh(ImportAssetOptions.ForceSynchronousImport);
                Debug.Log("[PotariaTMPSetup] TMP Essentials imported successfully.");
            }
            else
            {
                Debug.LogWarning($"[PotariaTMPSetup] TMP Essential Resources.unitypackage not found at {packagePath}.");
            }
        }

        [MenuItem("Potaria/Generate Pixel TMP Font", priority = 6)]
        public static void GeneratePixelFontAsset()
        {
            string ttfPath = "Assets/fonts/PixelifySans-Regular.ttf";
            string assetPath = "Assets/fonts/PixelifySans-Regular SDF.asset";

            var font = AssetDatabase.LoadAssetAtPath<Font>(ttfPath);
            if (font == null)
            {
                ttfPath = "Assets/Fonts/PixelifySans-Regular.ttf";
                font = AssetDatabase.LoadAssetAtPath<Font>(ttfPath);
            }
            if (font == null)
            {
                Debug.LogWarning($"[PotariaTMPSetup] Font at {ttfPath} not found.");
                return;
            }

            var fontAsset = AssetDatabase.LoadAssetAtPath<TMP_FontAsset>(assetPath);
            if (fontAsset == null)
            {
                fontAsset = TMP_FontAsset.CreateFontAsset(font, 36, 4, UnityEngine.TextCore.LowLevel.GlyphRenderMode.SDFAA, 512, 512);
                if (fontAsset != null)
                {
                    AssetDatabase.CreateAsset(fontAsset, assetPath);
                    if (fontAsset.material != null)
                    {
                        AssetDatabase.AddObjectToAsset(fontAsset.material, fontAsset);
                    }
                    AssetDatabase.SaveAssets();
                    Debug.Log($"[PotariaTMPSetup] Successfully created TMP Font Asset at {assetPath}");
                }
            }
            else
            {
                Debug.Log($"[PotariaTMPSetup] TMP Font Asset already exists at {assetPath}");
            }
        }
    }
}
