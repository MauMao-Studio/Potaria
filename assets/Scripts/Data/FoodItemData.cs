using System.Collections.Generic;
using UnityEngine;

namespace Potaria.Data
{
    /// <summary>
    /// ScriptableObject representing cooked dishes, food items, produce, and culinary ingredients in Potaria.
    /// Incorporates nutrition, health restore, cooking duration, and the 5-buff category system:
    /// Offense, Defense, Mobility, Resource, Utility.
    /// </summary>
    [CreateAssetMenu(fileName = "NewFoodItemData", menuName = "Potaria/Items/Food Item Data", order = 11)]
    public class FoodItemData : ItemData
    {
        [Header("Culinary & Nutrition")]
        [SerializeField] private int nutrition = 10;
        [SerializeField] private int healthRestore = 0;
        [SerializeField] private float cookingDuration = 0f; // 0 for raw/pantry, >0 for cooked dishes

        [Header("5-Buff Category System")]
        [SerializeField] private BuffCategory buffCategory = BuffCategory.None;
        [SerializeField] private FoodBuffData buff = new FoodBuffData();

        [Header("Heritage & Acquisition")]
        [TextArea(2, 3)]
        [SerializeField] private string acquisitionNotes = string.Empty;

        [SerializeField] private List<string> effects = new List<string>();

        // Public Accessors
        public int Nutrition { get => nutrition; set => nutrition = value; }
        public int HealthRestore { get => healthRestore; set => healthRestore = value; }
        public float CookingDuration { get => cookingDuration; set => cookingDuration = value; }
        public BuffCategory BuffCategory { get => buffCategory; set => buffCategory = value; }
        public FoodBuffData Buff { get => buff; set => buff = value; }
        public string AcquisitionNotes { get => acquisitionNotes; set => acquisitionNotes = value; }
        public List<string> Effects => effects;

        public bool HasBuff => buffCategory != BuffCategory.None && buff != null && buff.DurationSeconds > 0;

        public override string GetFormattedTooltip()
        {
            var baseTooltip = base.GetFormattedTooltip();
            var culinaryDetails = "";
            if (healthRestore > 0)
            {
                culinaryDetails += $"\n<color=#4CD964>Restores +{healthRestore} HP</color>";
            }
            if (nutrition > 0)
            {
                culinaryDetails += $"\n<color=#E0B050>Nutrition: {nutrition}</color>";
            }
            if (HasBuff)
            {
                var catColor = buffCategory.GetHexColor();
                culinaryDetails += $"\n<color={catColor}><b>[{buffCategory.ToString().ToUpper()}] {buff.BuffName}</b> ({buff.DurationSeconds:0}s)</color>";
                if (!string.IsNullOrEmpty(buff.EffectsDescription))
                {
                    culinaryDetails += $"\n<color={catColor}>{buff.EffectsDescription}</color>";
                }
            }
            if (!string.IsNullOrEmpty(acquisitionNotes))
            {
                culinaryDetails += $"\n<color=#70A0B0>Acquisition: {acquisitionNotes}</color>";
            }
            return $"{baseTooltip}{culinaryDetails}";
        }
    }
}
