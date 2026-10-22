using System.Collections.Generic;
using UnityEngine;

namespace Potaria.Data
{
    /// <summary>
    /// ScriptableObject defining agricultural crop growth, requirements, and harvest parameters.
    /// Incorporates growth stages, light requirements, and moisture requirements.
    /// </summary>
    [CreateAssetMenu(fileName = "NewCropData", menuName = "Potaria/Farming/Crop Data", order = 20)]
    public class CropData : ScriptableObject
    {
        [Header("Identification")]
        [SerializeField] private string cropId = string.Empty;
        [SerializeField] private string cropName = "Crop";

        [Header("Item Links")]
        [SerializeField] private string seedItemId = string.Empty;
        [SerializeField] private string harvestItemId = string.Empty;
        [SerializeField] private ItemData seedItem;
        [SerializeField] private ItemData harvestItem;

        [Header("Growth Stages & Timers")]
        [Range(2, 6)]
        [SerializeField] private int growthStagesCount = 4;
        [SerializeField] private float stageDurationSeconds = 40.0f; // Seconds per stage under ideal conditions
        [SerializeField] private List<Sprite> stageSprites = new List<Sprite>();

        [Header("Environmental Requirements")]
        [Tooltip("Minimum light level (0.0 to 1.0) required for the crop to progress.")]
        [Range(0f, 1f)]
        [SerializeField] private float minLightRequirement = 0.35f;

        [Tooltip("Whether this crop requires hydrated (wet) farmland to grow at full speed.")]
        [SerializeField] private bool requiresHydratedFarmland = true;

        [Tooltip("Growth rate multiplier when farmland is properly hydrated.")]
        [SerializeField] private float moistureGrowthMultiplier = 1.0f;

        [Tooltip("Growth rate multiplier when farmland is dry.")]
        [SerializeField] private float dryGrowthMultiplier = 0.35f;

        [Header("Harvest Yields")]
        [SerializeField] private int minHarvestYield = 1;
        [SerializeField] private int maxHarvestYield = 3;
        [SerializeField] private int minSeedYield = 1;
        [SerializeField] private int maxSeedYield = 2;

        // Public Accessors
        public string CropId { get => cropId; set => cropId = value; }
        public string CropName { get => cropName; set => cropName = value; }
        public string SeedItemId { get => seedItemId; set => seedItemId = value; }
        public string HarvestItemId { get => harvestItemId; set => harvestItemId = value; }
        public ItemData SeedItem { get => seedItem; set => seedItem = value; }
        public ItemData HarvestItem { get => harvestItem; set => harvestItem = value; }
        public int GrowthStagesCount { get => growthStagesCount; set => growthStagesCount = value; }
        public float StageDurationSeconds { get => stageDurationSeconds; set => stageDurationSeconds = value; }
        public List<Sprite> StageSprites => stageSprites;
        public float MinLightRequirement { get => minLightRequirement; set => minLightRequirement = value; }
        public bool RequiresHydratedFarmland { get => requiresHydratedFarmland; set => requiresHydratedFarmland = value; }
        public float MoistureGrowthMultiplier { get => moistureGrowthMultiplier; set => moistureGrowthMultiplier = value; }
        public float DryGrowthMultiplier { get => dryGrowthMultiplier; set => dryGrowthMultiplier = value; }
        public int MinHarvestYield { get => minHarvestYield; set => minHarvestYield = value; }
        public int MaxHarvestYield { get => maxHarvestYield; set => maxHarvestYield = value; }
        public int MinSeedYield { get => minSeedYield; set => minSeedYield = value; }
        public int MaxSeedYield { get => maxSeedYield; set => maxSeedYield = value; }

        public float TotalGrowthDurationSeconds => stageDurationSeconds * (growthStagesCount - 1);

        /// <summary>
        /// Calculates growth progress rate based on current moisture and light.
        /// </summary>
        public float CalculateGrowthRate(bool isHydrated, float currentLight)
        {
            if (currentLight < minLightRequirement) return 0f;
            return isHydrated ? moistureGrowthMultiplier : dryGrowthMultiplier;
        }

        public Sprite GetStageSprite(int stageIndex)
        {
            if (stageSprites == null || stageSprites.Count == 0) return null;
            var clamped = Mathf.Clamp(stageIndex, 0, stageSprites.Count - 1);
            return stageSprites[clamped];
        }
    }
}
