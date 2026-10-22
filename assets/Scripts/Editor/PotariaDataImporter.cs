using System;
using System.Collections.Generic;
using System.IO;
using UnityEditor;
using UnityEngine;
using Potaria.Data;

namespace Potaria.Editor
{
    /// <summary>
    /// Automated Editor tool that reads Potaria JSON data catalogs, configures pixel-art
    /// sprite importers, and generates native Unity ScriptableObject (.asset) files with linked
    /// sprites, stats, and cross-references.
    /// Supports headless batchmode execution via Potaria.Editor.PotariaDataImporter.ImportAll.
    /// </summary>
    public static class PotariaDataImporter
    {
        private const string DATA_PATH = "Assets/Data";
        private const string SO_ROOT = "Assets/ScriptableObjects";
        private const string FOOD_SO_PATH = "Assets/ScriptableObjects/Items/Food";
        private const string SEEDS_SO_PATH = "Assets/ScriptableObjects/Items/Seeds";
        private const string MATERIALS_SO_PATH = "Assets/ScriptableObjects/Items/Materials";
        private const string CROPS_SO_PATH = "Assets/ScriptableObjects/Crops";
        private const string RECIPES_SO_PATH = "Assets/ScriptableObjects/Recipes";
        private const string SETS_SO_PATH = "Assets/ScriptableObjects/EquipmentSets";
        private const string WEAPONS_SO_PATH = "Assets/ScriptableObjects/Items/Weapons";
        private const string EQUIP_SO_PATH = "Assets/ScriptableObjects/Items/Equipment";
        private const string CROPS_SPRITE_PATH = "Assets/Sprites/Crops";

        private static Dictionary<string, Sprite> s_spriteCache;

        [MenuItem("Potaria/Import All Data Assets", priority = 0)]
        public static void ImportAll()
        {
            Debug.Log("[PotariaDataImporter] Starting full data import pipeline...");
            EnsureDirectories();

            ConfigureTextureImporters();
            BuildSpriteCache();

            ImportFoodItems();
            ImportSeeds();
            ImportMaterials();
            ImportWeapons();
            ImportEquipment();
            ImportEquipmentSets();
            ImportCrops();
            ImportRecipes();

            AssetDatabase.SaveAssets();
            AssetDatabase.Refresh();
            Debug.Log("[PotariaDataImporter] Full data import pipeline successfully completed.");
        }

        [MenuItem("Potaria/Configure Texture Importers (Pixel-Art Sprites)", priority = 1)]
        public static void ConfigureTextureImporters()
        {
            EnsureDirectories();
            var guids = AssetDatabase.FindAssets("t:Texture2D", new[] { "Assets/Sprites" });
            int modified = 0;
            AssetDatabase.StartAssetEditing();
            try
            {
                foreach (var guid in guids)
                {
                    var path = AssetDatabase.GUIDToAssetPath(guid);
                    if (!path.EndsWith(".png", StringComparison.OrdinalIgnoreCase)) continue;

                    var importer = AssetImporter.GetAtPath(path) as TextureImporter;
                    if (importer == null) continue;

                    bool changed = false;
                    if (importer.textureType != TextureImporterType.Sprite)
                    {
                        importer.textureType = TextureImporterType.Sprite;
                        importer.spriteImportMode = SpriteImportMode.Single;
                        changed = true;
                    }
                    if (importer.filterMode != FilterMode.Point)
                    {
                        importer.filterMode = FilterMode.Point;
                        changed = true;
                    }
                    if (importer.textureCompression != TextureImporterCompression.Uncompressed)
                    {
                        importer.textureCompression = TextureImporterCompression.Uncompressed;
                        changed = true;
                    }
                    if (!importer.alphaIsTransparency)
                    {
                        importer.alphaIsTransparency = true;
                        changed = true;
                    }
                    if (Mathf.Abs(importer.spritePixelsPerUnit - 16f) > 0.01f)
                    {
                        importer.spritePixelsPerUnit = 16f;
                        changed = true;
                    }

                    if (changed)
                    {
                        importer.SaveAndReimport();
                        modified++;
                    }
                }
            }
            finally
            {
                AssetDatabase.StopAssetEditing();
            }
            Debug.Log($"[PotariaDataImporter] Configured {modified} textures as pixel-art 2D Sprites.");
        }

        private static void BuildSpriteCache()
        {
            s_spriteCache = new Dictionary<string, Sprite>(StringComparer.OrdinalIgnoreCase);
            var guids = AssetDatabase.FindAssets("t:Sprite", new[] { "Assets/Sprites" });
            foreach (var guid in guids)
            {
                var p = AssetDatabase.GUIDToAssetPath(guid);
                var sprite = AssetDatabase.LoadAssetAtPath<Sprite>(p);
                if (sprite != null)
                {
                    var fileName = Path.GetFileNameWithoutExtension(p);
                    if (!s_spriteCache.ContainsKey(fileName))
                    {
                        s_spriteCache[fileName] = sprite;
                    }
                }
            }
            Debug.Log($"[PotariaDataImporter] Cached {s_spriteCache.Count} sprites for item mapping.");
        }

        public static Sprite GetSprite(string id, string explicitPath = null)
        {
            if (s_spriteCache == null) BuildSpriteCache();

            if (!string.IsNullOrEmpty(explicitPath))
            {
                var sp = AssetDatabase.LoadAssetAtPath<Sprite>(explicitPath);
                if (sp != null) return sp;
            }

            if (!string.IsNullOrEmpty(id) && s_spriteCache.TryGetValue(id, out var cached))
            {
                return cached;
            }

            return null;
        }

        public static ItemData FindItemAsset(string itemId)
        {
            if (string.IsNullOrEmpty(itemId)) return null;

            var path = $"{FOOD_SO_PATH}/{itemId}.asset";
            var item = AssetDatabase.LoadAssetAtPath<ItemData>(path);
            if (item != null) return item;

            path = $"{SEEDS_SO_PATH}/{itemId}.asset";
            item = AssetDatabase.LoadAssetAtPath<ItemData>(path);
            if (item != null) return item;

            path = $"{MATERIALS_SO_PATH}/{itemId}.asset";
            item = AssetDatabase.LoadAssetAtPath<ItemData>(path);
            if (item != null) return item;

            path = $"{WEAPONS_SO_PATH}/{itemId}.asset";
            item = AssetDatabase.LoadAssetAtPath<ItemData>(path);
            if (item != null) return item;

            path = $"{EQUIP_SO_PATH}/{itemId}.asset";
            item = AssetDatabase.LoadAssetAtPath<ItemData>(path);
            if (item != null) return item;

            return null;
        }

        [MenuItem("Potaria/Import Food Items (79)", priority = 10)]
        public static void ImportFoodItems()
        {
            EnsureDirectories();
            if (s_spriteCache == null) BuildSpriteCache();

            var jsonPath = Path.Combine(DATA_PATH, "food_items.json");
            if (!File.Exists(jsonPath))
            {
                Debug.LogError($"[PotariaDataImporter] food_items.json not found at {jsonPath}");
                return;
            }

            var jsonText = File.ReadAllText(jsonPath);
            var dtos = JsonHelper.FromJson<FoodItemDTO>(jsonText);
            if (dtos == null || dtos.Length == 0)
            {
                Debug.LogWarning("[PotariaDataImporter] No food items parsed from JSON.");
                return;
            }

            int count = 0;
            foreach (var dto in dtos)
            {
                var assetPath = $"{FOOD_SO_PATH}/{dto.itemId}.asset";
                var item = AssetDatabase.LoadAssetAtPath<FoodItemData>(assetPath);
                bool isNew = false;
                if (item == null)
                {
                    item = ScriptableObject.CreateInstance<FoodItemData>();
                    isNew = true;
                }

                item.ItemId = dto.itemId;
                item.ItemName = dto.itemName;
                item.Category = ItemCategoryExtensions.FromString(dto.category);
                item.Rarity = ItemRarityExtensions.FromString(dto.rarity);
                item.MaxStack = dto.maxStack > 0 ? dto.maxStack : 99;
                item.Nutrition = dto.nutrition;
                item.HealthRestore = dto.healthRestore;
                item.CookingDuration = dto.cookingDuration;
                item.Description = dto.description ?? string.Empty;
                item.Lore = dto.lore ?? string.Empty;
                item.SpecialEffect = dto.special ?? string.Empty;
                item.AcquisitionNotes = dto.acquisition ?? string.Empty;

                // Configure 5-Buff category & full stat modifiers
                var buffCat = BuffCategoryExtensions.FromString(dto.buffCategory);
                item.BuffCategory = buffCat;
                if (buffCat != BuffCategory.None)
                {
                    var buff = new FoodBuffData(buffCat, dto.buffName, dto.buffDuration);
                    if (dto.buffStats != null)
                    {
                        buff.SetModifiers(
                            damageMult: dto.buffStats.damage_mult,
                            rangedMult: dto.buffStats.ranged_damage_mult,
                            atkSpdMult: dto.buffStats.atk_speed_mult,
                            critChance: dto.buffStats.crit_chance,
                            critDmgMult: dto.buffStats.crit_dmg_mult,
                            dmgRed: dto.buffStats.dmg_reduction,
                            flatDef: dto.buffStats.def,
                            magicRes: dto.buffStats.magic_res,
                            knockbackRes: dto.buffStats.knockback_res,
                            spdMult: dto.buffStats.speed_mult,
                            jumpMult: dto.buffStats.jump_mult,
                            hpRegen: dto.buffStats.hp_regen,
                            mpRegen: dto.buffStats.mp_regen,
                            manaCostRed: dto.buffStats.mana_cost_reduction,
                            desc: dto.special ?? string.Empty
                        );
                    }
                    else
                    {
                        buff.SetModifiers(desc: dto.special ?? string.Empty);
                    }
                    item.Buff = buff;
                }
                else
                {
                    item.Buff = new FoodBuffData();
                }

                // Associate sprite via cache or explicit path
                var sprite = GetSprite(dto.itemId, dto.spritePath);
                if (sprite != null) item.Icon = sprite;

                if (isNew)
                {
                    AssetDatabase.CreateAsset(item, assetPath);
                }
                else
                {
                    EditorUtility.SetDirty(item);
                }
                count++;
            }

            AssetDatabase.SaveAssets();
            Debug.Log($"[PotariaDataImporter] Successfully imported {count} Filipino food & culinary item assets.");
        }

        [MenuItem("Potaria/Import Seeds", priority = 11)]
        public static void ImportSeeds()
        {
            EnsureDirectories();
            if (s_spriteCache == null) BuildSpriteCache();

            var jsonPath = Path.Combine(DATA_PATH, "seeds.json");
            if (!File.Exists(jsonPath)) return;

            var jsonText = File.ReadAllText(jsonPath);
            var dtos = JsonHelper.FromJson<SeedDTO>(jsonText);
            if (dtos == null || dtos.Length == 0) return;

            int count = 0;
            foreach (var dto in dtos)
            {
                var assetPath = $"{SEEDS_SO_PATH}/{dto.itemId}.asset";
                var seed = AssetDatabase.LoadAssetAtPath<ItemData>(assetPath);
                bool isNew = false;
                if (seed == null)
                {
                    seed = ScriptableObject.CreateInstance<ItemData>();
                    isNew = true;
                }

                seed.ItemId = dto.itemId;
                seed.ItemName = dto.itemName;
                seed.Category = ItemCategoryExtensions.FromString(dto.category);
                seed.Rarity = ItemRarityExtensions.FromString(dto.rarity);
                seed.MaxStack = dto.maxStack > 0 ? dto.maxStack : 99;
                seed.Description = dto.description ?? string.Empty;
                seed.Lore = dto.lore ?? string.Empty;
                seed.SpecialEffect = dto.special ?? string.Empty;

                var sprite = GetSprite(dto.itemId);
                if (sprite != null) seed.Icon = sprite;

                if (isNew) AssetDatabase.CreateAsset(seed, assetPath);
                else EditorUtility.SetDirty(seed);
                count++;
            }

            AssetDatabase.SaveAssets();
            Debug.Log($"[PotariaDataImporter] Successfully imported {count} agricultural seed item assets.");
        }

        [MenuItem("Potaria/Import Materials", priority = 12)]
        public static void ImportMaterials()
        {
            EnsureDirectories();
            if (s_spriteCache == null) BuildSpriteCache();

            var jsonPath = Path.Combine(DATA_PATH, "materials.json");
            if (!File.Exists(jsonPath)) return;

            var jsonText = File.ReadAllText(jsonPath);
            var dtos = JsonHelper.FromJson<MaterialDTO>(jsonText);
            if (dtos == null || dtos.Length == 0) return;

            int count = 0;
            foreach (var dto in dtos)
            {
                var assetPath = $"{MATERIALS_SO_PATH}/{dto.itemId}.asset";
                var mat = AssetDatabase.LoadAssetAtPath<ItemData>(assetPath);
                bool isNew = false;
                if (mat == null)
                {
                    mat = ScriptableObject.CreateInstance<ItemData>();
                    isNew = true;
                }

                mat.ItemId = dto.itemId;
                mat.ItemName = dto.itemName;
                mat.Category = ItemCategoryExtensions.FromString(dto.category);
                mat.Rarity = ItemRarityExtensions.FromString(dto.rarity);
                mat.MaxStack = dto.maxStack > 0 ? dto.maxStack : 99;
                mat.Description = dto.description ?? string.Empty;
                mat.Lore = dto.lore ?? string.Empty;
                mat.SpecialEffect = dto.special ?? string.Empty;

                var sprite = GetSprite(dto.itemId);
                if (sprite != null) mat.Icon = sprite;

                if (isNew) AssetDatabase.CreateAsset(mat, assetPath);
                else EditorUtility.SetDirty(mat);
                count++;
            }

            AssetDatabase.SaveAssets();
            Debug.Log($"[PotariaDataImporter] Successfully imported {count} material & craftable item assets.");
        }

        [MenuItem("Potaria/Import Crops", priority = 12)]
        public static void ImportCrops()
        {
            EnsureDirectories();
            var jsonPath = Path.Combine(DATA_PATH, "crops.json");
            if (!File.Exists(jsonPath))
            {
                Debug.LogError($"[PotariaDataImporter] crops.json not found at {jsonPath}");
                return;
            }

            var jsonText = File.ReadAllText(jsonPath);
            var dtos = JsonHelper.FromJson<CropDTO>(jsonText);
            if (dtos == null || dtos.Length == 0) return;

            int count = 0;
            foreach (var dto in dtos)
            {
                var assetPath = $"{CROPS_SO_PATH}/{dto.cropId}.asset";
                var crop = AssetDatabase.LoadAssetAtPath<CropData>(assetPath);
                bool isNew = false;
                if (crop == null)
                {
                    crop = ScriptableObject.CreateInstance<CropData>();
                    isNew = true;
                }

                crop.CropId = dto.cropId;
                crop.CropName = dto.cropName;
                crop.SeedItemId = dto.seedItemId;
                crop.HarvestItemId = dto.harvestItemId;
                crop.GrowthStagesCount = dto.growthStagesCount > 0 ? dto.growthStagesCount : 4;
                crop.StageDurationSeconds = dto.stageDurationSeconds > 0 ? dto.stageDurationSeconds : 40f;
                crop.MinLightRequirement = dto.minLightRequirement;
                crop.RequiresHydratedFarmland = dto.requiresHydratedFarmland;
                crop.MoistureGrowthMultiplier = dto.moistureGrowthMultiplier;
                crop.DryGrowthMultiplier = dto.dryGrowthMultiplier;
                crop.MinHarvestYield = dto.minHarvestYield;
                crop.MaxHarvestYield = dto.maxHarvestYield;
                crop.MinSeedYield = dto.minSeedYield;
                crop.MaxSeedYield = dto.maxSeedYield;

                // Link Seed and Harvest items
                crop.SeedItem = FindItemAsset(dto.seedItemId);
                crop.HarvestItem = FindItemAsset(dto.harvestItemId);

                // Populate stage sprites
                crop.StageSprites.Clear();
                for (int st = 0; st < crop.GrowthStagesCount; st++)
                {
                    var stageSpritePath = $"{CROPS_SPRITE_PATH}/{dto.cropId}_stage_{st}.png";
                    var sp = AssetDatabase.LoadAssetAtPath<Sprite>(stageSpritePath);
                    if (sp != null)
                    {
                        crop.StageSprites.Add(sp);
                    }
                }

                if (isNew)
                {
                    AssetDatabase.CreateAsset(crop, assetPath);
                }
                else
                {
                    EditorUtility.SetDirty(crop);
                }
                count++;
            }

            AssetDatabase.SaveAssets();
            Debug.Log($"[PotariaDataImporter] Successfully imported {count} agricultural crop assets.");
        }

        [MenuItem("Potaria/Import Recipes", priority = 13)]
        public static void ImportRecipes()
        {
            EnsureDirectories();
            var jsonPath = Path.Combine(DATA_PATH, "recipes.json");
            if (!File.Exists(jsonPath))
            {
                Debug.LogError($"[PotariaDataImporter] recipes.json not found at {jsonPath}");
                return;
            }

            var jsonText = File.ReadAllText(jsonPath);
            var dtos = JsonHelper.FromJson<RecipeDTO>(jsonText);
            if (dtos == null || dtos.Length == 0) return;

            int count = 0;
            foreach (var dto in dtos)
            {
                var assetPath = $"{RECIPES_SO_PATH}/{dto.recipeId}.asset";
                var recipe = AssetDatabase.LoadAssetAtPath<RecipeData>(assetPath);
                bool isNew = false;
                if (recipe == null)
                {
                    recipe = ScriptableObject.CreateInstance<RecipeData>();
                    isNew = true;
                }

                recipe.RecipeId = dto.recipeId;
                recipe.ResultItemId = dto.resultItemId;
                recipe.ResultCount = dto.resultCount > 0 ? dto.resultCount : 1;
                recipe.Category = dto.category ?? "Survival";
                recipe.CraftingStation = CraftingStationExtensions.FromString(dto.craftingStation);

                // Link result item data across all item categories (Food, Weapons, Equipment, Seeds)
                recipe.ResultItemData = FindItemAsset(dto.resultItemId);

                recipe.Ingredients.Clear();
                if (dto.ingredients != null)
                {
                    foreach (var ing in dto.ingredients)
                    {
                        var ingItemSo = FindItemAsset(ing.itemId);
                        recipe.Ingredients.Add(new RecipeIngredient(ing.itemId, ing.count, ingItemSo));
                    }
                }

                if (isNew)
                {
                    AssetDatabase.CreateAsset(recipe, assetPath);
                }
                else
                {
                    EditorUtility.SetDirty(recipe);
                }
                count++;
            }

            AssetDatabase.SaveAssets();
            Debug.Log($"[PotariaDataImporter] Successfully imported {count} crafting and culinary recipe assets.");
        }

        [MenuItem("Potaria/Import Equipment Sets", priority = 14)]
        public static void ImportEquipmentSets()
        {
            EnsureDirectories();
            var jsonPath = Path.Combine(DATA_PATH, "equipment_sets.json");
            if (!File.Exists(jsonPath))
            {
                Debug.LogError($"[PotariaDataImporter] equipment_sets.json not found at {jsonPath}");
                return;
            }

            var jsonText = File.ReadAllText(jsonPath);
            var dtos = JsonHelper.FromJson<EquipmentSetDTO>(jsonText);
            if (dtos == null || dtos.Length == 0) return;

            int count = 0;
            foreach (var dto in dtos)
            {
                var assetPath = $"{SETS_SO_PATH}/{dto.setId}.asset";
                var set = AssetDatabase.LoadAssetAtPath<EquipmentSetData>(assetPath);
                bool isNew = false;
                if (set == null)
                {
                    set = ScriptableObject.CreateInstance<EquipmentSetData>();
                    isNew = true;
                }

                set.SetId = dto.setId;
                set.SetName = dto.setName;
                set.SetTag = dto.setTag;
                set.PieceItemIds.Clear();
                set.PieceItems.Clear();

                if (dto.pieces != null)
                {
                    foreach (var pId in dto.pieces)
                    {
                        set.PieceItemIds.Add(pId);
                        var pieceSo = FindItemAsset(pId);
                        if (pieceSo != null)
                        {
                            set.PieceItems.Add(pieceSo);
                        }
                    }
                }

                set.AllThresholds.Clear();
                if (dto.thresholds != null)
                {
                    foreach (var t in dto.thresholds)
                    {
                        var threshold = new SetBonusThreshold
                        {
                            RequiredPieces = t.requiredPieces,
                            Title = t.title ?? $"{t.requiredPieces}-Piece Bonus",
                            Description = t.description ?? string.Empty,
                            AtkMultiplier = t.atkMult,
                            DefMultiplier = t.defMult,
                            BonusSpeed = t.bonusSpeed,
                            BonusCritChance = t.bonusCrit,
                            BonusMaxHp = t.bonusHp,
                            BonusMpRegen = t.bonusMpRegen,
                            BonusAtkSpeed = t.bonusAtkSpeed,
                            AuraEffect = t.auraEffect ?? string.Empty,
                            SpecialPassive = t.specialPassive ?? string.Empty
                        };

                        set.AllThresholds.Add(threshold);

                        if (t.requiredPieces == 2) set.TwoPieceBonus = threshold;
                        else if (t.requiredPieces == 4) set.FourPieceBonus = threshold;
                        else if (t.requiredPieces == 5) set.FivePieceBonus = threshold;
                    }
                }

                if (isNew)
                {
                    AssetDatabase.CreateAsset(set, assetPath);
                }
                else
                {
                    EditorUtility.SetDirty(set);
                }
                count++;
            }

            AssetDatabase.SaveAssets();
            Debug.Log($"[PotariaDataImporter] Successfully imported {count} equipment sets (SDS, SHV, Katipunero).");
        }

        [MenuItem("Potaria/Import Weapons", priority = 15)]
        public static void ImportWeapons()
        {
            EnsureDirectories();
            if (s_spriteCache == null) BuildSpriteCache();

            var jsonPath = Path.Combine(DATA_PATH, "weapons.json");
            if (!File.Exists(jsonPath)) return;

            var jsonText = File.ReadAllText(jsonPath);
            var dtos = JsonHelper.FromJson<WeaponDTO>(jsonText);
            if (dtos == null || dtos.Length == 0) return;

            int count = 0;
            foreach (var dto in dtos)
            {
                var assetPath = $"{WEAPONS_SO_PATH}/{dto.id}.asset";
                var weapon = AssetDatabase.LoadAssetAtPath<WeaponItemData>(assetPath);
                bool isNew = false;
                if (weapon == null)
                {
                    weapon = ScriptableObject.CreateInstance<WeaponItemData>();
                    isNew = true;
                }

                weapon.ItemId = dto.id;
                weapon.ItemName = dto.name;
                weapon.Category = ItemCategory.Weapon;
                weapon.Rarity = ItemRarityExtensions.FromString(dto.rarity);
                weapon.Attack = dto.atk;
                weapon.Defense = dto.def;
                weapon.CritChance = dto.crit;
                weapon.Speed = dto.speed;
                weapon.BonusHp = dto.hp;
                weapon.BonusMp = dto.mp;
                weapon.MpRegen = dto.mp_regen;
                weapon.Description = dto.desc ?? string.Empty;
                weapon.Lore = dto.lore ?? string.Empty;
                weapon.SpecialEffect = dto.special ?? string.Empty;

                var sprite = GetSprite(dto.id);
                if (sprite != null) weapon.Icon = sprite;

                if (isNew) AssetDatabase.CreateAsset(weapon, assetPath);
                else EditorUtility.SetDirty(weapon);
                count++;
            }

            AssetDatabase.SaveAssets();
            Debug.Log($"[PotariaDataImporter] Successfully imported {count} weapon assets.");
        }

        [MenuItem("Potaria/Import Equipment", priority = 16)]
        public static void ImportEquipment()
        {
            EnsureDirectories();
            if (s_spriteCache == null) BuildSpriteCache();

            var jsonPath = Path.Combine(DATA_PATH, "equipments.json");
            if (!File.Exists(jsonPath)) return;

            var jsonText = File.ReadAllText(jsonPath);
            var dtos = JsonHelper.FromJson<EquipmentDTO>(jsonText);
            if (dtos == null || dtos.Length == 0) return;

            int count = 0;
            foreach (var dto in dtos)
            {
                var assetPath = $"{EQUIP_SO_PATH}/{dto.id}.asset";
                var equip = AssetDatabase.LoadAssetAtPath<EquipmentItemData>(assetPath);
                bool isNew = false;
                if (equip == null)
                {
                    equip = ScriptableObject.CreateInstance<EquipmentItemData>();
                    isNew = true;
                }

                equip.ItemId = dto.id;
                equip.ItemName = dto.name;
                equip.Category = ItemCategory.Armor;
                equip.Rarity = ItemRarityExtensions.FromString(dto.rarity);
                equip.Attack = dto.atk;
                equip.Defense = dto.def;
                equip.CritChance = dto.crit;
                equip.Speed = dto.speed;
                equip.BonusHp = dto.hp;
                equip.BonusMp = dto.mp;
                equip.MpRegen = dto.mp_regen;
                equip.Description = dto.desc ?? string.Empty;
                equip.Lore = dto.lore ?? string.Empty;

                var sprite = GetSprite(dto.id);
                if (sprite != null) equip.Icon = sprite;

                if (isNew) AssetDatabase.CreateAsset(equip, assetPath);
                else EditorUtility.SetDirty(equip);
                count++;
            }

            AssetDatabase.SaveAssets();
            Debug.Log($"[PotariaDataImporter] Successfully imported {count} equipment assets.");
        }

        private static void EnsureDirectories()
        {
            var dirs = new[]
            {
                SO_ROOT,
                "Assets/ScriptableObjects/Items",
                FOOD_SO_PATH,
                SEEDS_SO_PATH,
                MATERIALS_SO_PATH,
                CROPS_SO_PATH,
                RECIPES_SO_PATH,
                SETS_SO_PATH,
                WEAPONS_SO_PATH,
                EQUIP_SO_PATH,
                CROPS_SPRITE_PATH
            };

            foreach (var d in dirs)
            {
                if (!Directory.Exists(d))
                {
                    Directory.CreateDirectory(d);
                }
            }
        }

        #region Helper Classes & DTOs

        public static class JsonHelper
        {
            public static T[] FromJson<T>(string json)
            {
                string wrappedJson = "{\"items\":" + json + "}";
                Wrapper<T> wrapper = JsonUtility.FromJson<Wrapper<T>>(wrappedJson);
                return wrapper != null ? wrapper.items : Array.Empty<T>();
            }

            [Serializable]
            private class Wrapper<T>
            {
                public T[] items;
            }
        }

        [Serializable]
        public class BuffStatsDTO
        {
            public float damage_mult;
            public float ranged_damage_mult;
            public float atk_speed_mult;
            public float crit_chance;
            public float crit_dmg_mult;
            public float dmg_reduction;
            public int def;
            public float magic_res;
            public float knockback_res;
            public float speed_mult;
            public float jump_mult;
            public float hp_regen;
            public float mp_regen;
            public float mana_cost_reduction;
        }

        [Serializable]
        public class FoodItemDTO
        {
            public string itemId;
            public string itemName;
            public string category;
            public string rarity;
            public int maxStack;
            public int nutrition;
            public int healthRestore;
            public float cookingDuration;
            public string buffCategory;
            public string buffName;
            public float buffDuration;
            public BuffStatsDTO buffStats;
            public string description;
            public string lore;
            public string special;
            public string acquisition;
            public string spritePath;
            public string[] effects;
        }

        [Serializable]
        public class SeedDTO
        {
            public string itemId;
            public string itemName;
            public string category;
            public string rarity;
            public int maxStack;
            public string description;
            public string lore;
            public string special;
        }

        [Serializable]
        public class MaterialDTO
        {
            public string itemId;
            public string itemName;
            public string category;
            public string rarity;
            public int maxStack;
            public string description;
            public string lore;
            public string special;
        }

        [Serializable]
        public class CropDTO
        {
            public string cropId;
            public string cropName;
            public string seedItemId;
            public string harvestItemId;
            public int growthStagesCount;
            public float stageDurationSeconds;
            public float minLightRequirement;
            public bool requiresHydratedFarmland;
            public float moistureGrowthMultiplier;
            public float dryGrowthMultiplier;
            public int minHarvestYield;
            public int maxHarvestYield;
            public int minSeedYield;
            public int maxSeedYield;
        }

        [Serializable]
        public class RecipeDTO
        {
            public string recipeId;
            public string resultItemId;
            public int resultCount;
            public string craftingStation;
            public string category;
            public IngredientDTO[] ingredients;
        }

        [Serializable]
        public class IngredientDTO
        {
            public string itemId;
            public int count;
        }

        [Serializable]
        public class EquipmentSetDTO
        {
            public string setId;
            public string setName;
            public string setTag;
            public string[] pieces;
            public ThresholdDTO[] thresholds;
        }

        [Serializable]
        public class ThresholdDTO
        {
            public int requiredPieces;
            public string title;
            public string description;
            public float atkMult;
            public float defMult;
            public float bonusSpeed;
            public float bonusCrit;
            public int bonusHp;
            public float bonusMpRegen;
            public float bonusAtkSpeed;
            public string auraEffect;
            public string specialPassive;
        }

        [Serializable]
        public class WeaponDTO
        {
            public string id;
            public string name;
            public string cat;
            public string rarity;
            public int atk;
            public int def;
            public float crit;
            public float speed;
            public int hp;
            public int mp;
            public float mp_regen;
            public string desc;
            public string lore;
            public string special;
        }

        [Serializable]
        public class EquipmentDTO
        {
            public string id;
            public string name;
            public string cat;
            public string rarity;
            public int atk;
            public int def;
            public float crit;
            public float speed;
            public int hp;
            public int mp;
            public float mp_regen;
            public string desc;
            public string lore;
        }

        #endregion
    }
}
