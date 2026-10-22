using System;
using UnityEngine;
using UnityEngine.Tilemaps;
using Potaria.Data;

namespace Potaria.World
{
    /// <summary>
    /// Metadata definition for a block or wall type in Potaria.
    /// Encapsulates mining hardness, required tool type, mined item drop,
    /// light emission/absorption, collider properties, and linked Unity TileBase asset.
    /// Serialized directly within TileDatabase.
    /// </summary>
    [Serializable]
    public class TileDefinition
    {
        [Header("Identification")]
        [SerializeField] private int tileId = 0;
        [SerializeField] private string tileName = "Air";
        [SerializeField] private bool isWall = false;

        [Header("Mining & Durability")]
        [SerializeField] private int hardness = 0;
        [SerializeField] private ToolType requiredTool = ToolType.None;
        [SerializeField] private bool isIndestructible = false;

        [Header("Drop Item")]
        [SerializeField] private string dropItemId = string.Empty;
        [SerializeField] private ItemData minedDrop;

        [Header("Collision & Physics")]
        [SerializeField] private bool isSolid = false;
        [SerializeField] private bool isPlatform = false;
        [SerializeField] private bool isLiquid = false;

        [Header("Optical & Lighting Properties")]
        [Range(0, 15)]
        [SerializeField] private int lightEmission = 0;
        [Range(0, 15)]
        [SerializeField] private int lightRadius = 0;
        [Range(0, 15)]
        [SerializeField] private int lightAbsorption = 0;
        [SerializeField] private bool isOpaque = false;
        [SerializeField] private Color emissionColor = Color.white;

        [Header("Visual Asset")]
        [SerializeField] private TileBase unityTile;

        // Public Accessors
        public int TileId { get => tileId; set => tileId = value; }
        public string TileName { get => tileName; set => tileName = value; }
        public bool IsWall { get => isWall; set => isWall = value; }
        public int Hardness { get => hardness; set => hardness = value; }
        public ToolType RequiredTool { get => requiredTool; set => requiredTool = value; }
        public bool IsIndestructible { get => isIndestructible; set => isIndestructible = value; }
        public string DropItemId { get => dropItemId; set => dropItemId = value; }
        public ItemData MinedDrop { get => minedDrop; set => minedDrop = value; }
        public bool IsSolid { get => isSolid; set => isSolid = value; }
        public bool IsPlatform { get => isPlatform; set => isPlatform = value; }
        public bool IsLiquid { get => isLiquid; set => isLiquid = value; }
        public int LightEmission { get => lightEmission; set => lightEmission = value; }
        public int LightRadius { get => lightRadius > 0 ? lightRadius : lightEmission; set => lightRadius = value; }
        public int LightAbsorption { get => lightAbsorption; set => lightAbsorption = value; }
        public bool IsOpaque { get => isOpaque; set => isOpaque = value; }
        public Color EmissionColor { get => emissionColor; set => emissionColor = value; }
        public TileBase UnityTile { get => unityTile; set => unityTile = value; }

        public bool CanMineWith(ToolType tool, int power)
        {
            if (isIndestructible || hardness <= 0) return false;
            if (requiredTool == ToolType.None) return true;
            return tool == requiredTool;
        }

        public int CalculateDamage(ToolType tool, int toolPower)
        {
            if (isIndestructible || hardness <= 0) return 0;
            if (tool == requiredTool && requiredTool != ToolType.None)
            {
                // Appropriate tool does enhanced damage
                return Mathf.Max(1, toolPower * 2);
            }
            // Bare hands / mismatch tool fallback punch
            return Mathf.Max(1, toolPower / 2);
        }
    }
}
