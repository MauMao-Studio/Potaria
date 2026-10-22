using System;
using System.Collections.Generic;
using UnityEngine;

namespace Potaria.Data
{
    /// <summary>
    /// Component ingredient in a crafting or cooking recipe.
    /// </summary>
    [Serializable]
    public class RecipeIngredient
    {
        [SerializeField] private string itemId = string.Empty;
        [SerializeField] private ItemData itemData;
        [Range(1, 999)]
        [SerializeField] private int count = 1;

        public string ItemId { get => itemId; set => itemId = value; }
        public ItemData ItemData { get => itemData; set => itemData = value; }
        public int Count { get => count; set => count = value; }

        public RecipeIngredient() { }

        public RecipeIngredient(string itemId, int count, ItemData itemData = null)
        {
            this.itemId = itemId;
            this.count = count;
            this.itemData = itemData;
        }
    }

    /// <summary>
    /// ScriptableObject defining crafting and cooking recipes in Potaria.
    /// Specifies ingredients, crafting station (Hand, Furnace, Campfire, WorkBench), and result item.
    /// </summary>
    [CreateAssetMenu(fileName = "NewRecipeData", menuName = "Potaria/Crafting/Recipe Data", order = 30)]
    public class RecipeData : ScriptableObject
    {
        [Header("Recipe Identification")]
        [SerializeField] private string recipeId = string.Empty;
        [SerializeField] private string category = "Survival";

        [Header("Result Item")]
        [SerializeField] private string resultItemId = string.Empty;
        [SerializeField] private ItemData resultItemData;
        [Range(1, 999)]
        [SerializeField] private int resultCount = 1;

        [Header("Station Requirement")]
        [SerializeField] private CraftingStation craftingStation = CraftingStation.Hand;

        [Header("Ingredients")]
        [SerializeField] private List<RecipeIngredient> ingredients = new List<RecipeIngredient>();

        // Public Accessors
        public string RecipeId { get => recipeId; set => recipeId = value; }
        public string Category { get => category; set => category = value; }
        public string ResultItemId { get => resultItemId; set => resultItemId = value; }
        public ItemData ResultItemData { get => resultItemData; set => resultItemData = value; }
        public int ResultCount { get => resultCount; set => resultCount = value; }
        public CraftingStation CraftingStation { get => craftingStation; set => craftingStation = value; }
        public List<RecipeIngredient> Ingredients => ingredients;

        public bool CanCraft(Func<string, int> getInventoryItemCount)
        {
            if (getInventoryItemCount == null) return false;
            foreach (var ing in ingredients)
            {
                var targetId = ing.ItemData != null ? ing.ItemData.ItemId : ing.ItemId;
                if (getInventoryItemCount(targetId) < ing.Count)
                {
                    return false;
                }
            }
            return true;
        }
    }
}
