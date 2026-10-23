using System;
using UnityEngine;
using Potaria.World;
using Potaria.Player;

namespace Potaria.UI
{
    /// <summary>
    /// Interactive Mining & Block Placement Cursor Reticle for Potaria.
    /// Ported directly from Pygame reference (src/ui/hud.py _render_reticle):
    /// - Snaps to 1x1 world grid cell (gx, ty) matching mouse pointer.
    /// - Distance check: vibrant orange/gold bracket box [ ] when within reach (<= 5.5 blocks),
    ///   translucent red when out of reach (> 5.5 blocks).
    /// - Continuous / pulsed mining with left-click: damages tile with appropriate tool power.
    /// - Progressive block breaking progress bar rendered directly above/below targeted tile.
    /// - Block and torch placement with right-click from active hotbar slot.
    /// </summary>
    public class MiningCursorController : MonoBehaviour
    {
        [Header("Configuration")]
        [SerializeField] private float maxReachDistance = 5.5f;
        [SerializeField] private float mineInterval = 0.20f;
        [SerializeField] private Color inReachColor = new Color(1.0f, 0.75f, 0.15f, 0.95f);
        [SerializeField] private Color outOfReachColor = new Color(1.0f, 0.24f, 0.24f, 0.45f);

        [Header("Dependencies")]
        [SerializeField] private UnityEngine.Camera targetCamera;
        [SerializeField] private ChunkManager chunkManager;
        [SerializeField] private Transform playerTransform;
        [SerializeField] private Sprite reticleSprite;

        private GameObject _reticleObj;
        private SpriteRenderer _reticleRenderer;

        private GameObject _breakBarRoot;
        private SpriteRenderer _breakBarBg;
        private SpriteRenderer _breakBarFill;

        private int _currentGx;
        private int _currentTy;
        private bool _inReach;
        private float _mineTimer;

        public Vector2Int TargetedGridCell => new Vector2Int(_currentGx, _currentTy);
        public bool IsInReach => _inReach;
        public float MaxReachDistance { get => maxReachDistance; set => maxReachDistance = value; }

        private void Awake()
        {
            InitializeVisuals();
        }

        public void InitializeVisuals()
        {
            FindDependenciesIfMissing();
            CreateReticleVisuals();
            CreateBreakBarVisuals();
        }

        private void Start()
        {
            FindDependenciesIfMissing();
        }

        public void FindDependenciesIfMissing()
        {
            if (targetCamera == null) targetCamera = UnityEngine.Camera.main;
            if (chunkManager == null) chunkManager = FindFirstObjectByType<ChunkManager>();
            if (playerTransform == null)
            {
                var player = FindFirstObjectByType<PlayerController>();
                if (player != null) playerTransform = player.transform;
            }
        }

        private void CreateReticleVisuals()
        {
            if (_reticleObj != null) return;

            _reticleObj = new GameObject("MiningReticle");
            _reticleObj.transform.SetParent(transform, false);

            _reticleRenderer = _reticleObj.AddComponent<SpriteRenderer>();
            _reticleRenderer.sortingLayerName = "UI";
            _reticleRenderer.sortingOrder = 50;

            if (reticleSprite == null)
            {
#if UNITY_EDITOR
                reticleSprite = UnityEditor.AssetDatabase.LoadAssetAtPath<Sprite>("Assets/Sprites/Ui/reticle.png");
                if (reticleSprite == null) reticleSprite = UnityEditor.AssetDatabase.LoadAssetAtPath<Sprite>("Assets/ui/reticle.png");
#endif
            }

            if (reticleSprite == null)
            {
                reticleSprite = CreateProceduralReticleSprite();
            }

            _reticleRenderer.sprite = reticleSprite;
            _reticleRenderer.color = inReachColor;
        }

        private void CreateBreakBarVisuals()
        {
            if (_breakBarRoot != null) return;

            _breakBarRoot = new GameObject("BreakProgressBar");
            _breakBarRoot.transform.SetParent(transform, false);

            // Dark border & backing
            var bgObj = new GameObject("Bg");
            bgObj.transform.SetParent(_breakBarRoot.transform, false);
            _breakBarBg = bgObj.AddComponent<SpriteRenderer>();
            _breakBarBg.sortingLayerName = "UI";
            _breakBarBg.sortingOrder = 51;
            _breakBarBg.sprite = CreateSolidPixelSprite();
            _breakBarBg.color = new Color(0.06f, 0.07f, 0.11f, 0.90f);
            bgObj.transform.localScale = new Vector3(0.84f, 0.14f, 1f);

            // Colored fill bar
            var fillObj = new GameObject("Fill");
            fillObj.transform.SetParent(_breakBarRoot.transform, false);
            _breakBarFill = fillObj.AddComponent<SpriteRenderer>();
            _breakBarFill.sortingLayerName = "UI";
            _breakBarFill.sortingOrder = 52;
            _breakBarFill.sprite = CreateSolidPixelSprite();
            _breakBarFill.color = new Color(1.0f, 0.84f, 0.24f, 1.0f);
            fillObj.transform.localScale = new Vector3(0.80f, 0.10f, 1f);

            _breakBarRoot.SetActive(false);
        }

        private void Update()
        {
            FindDependenciesIfMissing();
            if (targetCamera == null) return;

            // 1. Convert screen mouse coordinates to 1x1 grid cell
            Vector3 mouseScreen = UnityEngine.Input.mousePosition;
            Vector3 mouseWorld = targetCamera.ScreenToWorldPoint(mouseScreen);

            _currentGx = Mathf.FloorToInt(mouseWorld.x);
            _currentTy = -Mathf.FloorToInt(mouseWorld.y);

            // Tile center in world coordinates
            Vector3 tileCenter = new Vector3(_currentGx + 0.5f, -_currentTy + 0.5f, 0f);
            if (_reticleObj != null)
            {
                _reticleObj.transform.position = tileCenter;
            }

            // 2. Reach distance calculation (<= 5.5 units)
            Vector2 origin = (playerTransform != null)
                ? (Vector2)playerTransform.position + new Vector2(0f, 0.5f)
                : (Vector2)targetCamera.transform.position;

            float reachDist = Vector2.Distance(origin, (Vector2)tileCenter);
            _inReach = reachDist <= maxReachDistance;

            if (_reticleRenderer != null)
            {
                _reticleRenderer.color = _inReach ? inReachColor : outOfReachColor;
            }

            // 3. Left-Click Continuous Mining
            HandleMiningInput();

            // 4. Right-Click Block & Torch Placement
            HandlePlacementInput();

            // 5. Update Break Progress Bar
            UpdateBreakProgressBar(tileCenter);
        }

        private void HandleMiningInput()
        {
            if (chunkManager == null) return;

            bool isMining = UnityEngine.Input.GetMouseButton(0);
            if (isMining && _inReach)
            {
                _mineTimer -= Time.deltaTime;
                if (_mineTimer <= 0f)
                {
                    _mineTimer = mineInterval;
                    ExecuteMiningAction(_currentGx, _currentTy);
                }
            }
            else
            {
                _mineTimer = 0f;
            }
        }

        public bool ExecuteMiningAction(int gx, int ty)
        {
            if (chunkManager == null) return false;

            ToolType tool = ToolType.None;
            int power = 10;

            if (PotariaHUD.Instance != null)
            {
                var active = PotariaHUD.Instance.GetActiveItem();
                if (!string.IsNullOrEmpty(active.id))
                {
                    if (active.id.Contains("pickaxe"))
                    {
                        tool = ToolType.Pickaxe;
                        power = 30;
                    }
                    else if (active.id.Contains("axe"))
                    {
                        tool = ToolType.Axe;
                        power = 30;
                    }
                    else if (active.id.Contains("sword"))
                    {
                        power = 15;
                    }
                }
            }

            bool broken = chunkManager.DamageTile(gx, ty, power, tool, power, out Potaria.Data.ItemData droppedItem);
            if (broken && droppedItem != null && PotariaHUD.Instance != null)
            {
                Sprite dropSprite = droppedItem.Icon != null ? droppedItem.Icon : ResolveItemSprite(droppedItem.ItemId);
                PotariaHUD.Instance.AddItem(droppedItem.ItemId, droppedItem.ItemName, dropSprite, 1);
            }
            return broken;
        }

        private Sprite ResolveItemSprite(string itemId)
        {
            if (string.IsNullOrEmpty(itemId)) return null;
            if (PotariaHUD.Instance != null)
            {
                for (int i = 0; i < 10; i++)
                {
                    var it = PotariaHUD.Instance.GetItem(i);
                    if (it.id == itemId && it.icon != null) return it.icon;
                }
            }
#if UNITY_EDITOR
            string stripped = itemId.Replace("item.", "");
            string[] paths = new[]
            {
                "Assets/Sprites/Tiles/" + stripped + ".png",
                "Assets/Sprites/Craftable_items/" + stripped + ".png",
                "Assets/Sprites/Items/" + stripped + ".png",
                "Assets/Sprites/Ui/" + stripped + ".png",
                "Assets/Sprites/" + stripped + ".png"
            };
            foreach (var p in paths)
            {
                var s = UnityEditor.AssetDatabase.LoadAssetAtPath<Sprite>(p);
                if (s != null) return s;
            }
#endif
            return null;
        }

        private void HandlePlacementInput()
        {
            if (chunkManager == null) return;

            if (UnityEngine.Input.GetMouseButtonDown(1) && _inReach)
            {
                ExecutePlacementAction(_currentGx, _currentTy);
            }
        }

        public bool ExecutePlacementAction(int gx, int ty)
        {
            if (chunkManager == null) return false;

            int currentTile = chunkManager.GetTile(gx, ty);
            if (currentTile != WorldConstants.TileAir) return false;

            if (PotariaHUD.Instance == null) return false;
            var active = PotariaHUD.Instance.GetActiveItem();
            if (active.stack <= 0 || string.IsNullOrEmpty(active.id)) return false;

            int tileToPlace = ResolveTileIdFromItem(active.id);
            if (tileToPlace == WorldConstants.TileAir) return false;

            // Prevent placing solid blocks directly inside player collider
            if (tileToPlace != WorldConstants.TileTorch && playerTransform != null)
            {
                var playerCol = playerTransform.GetComponent<Collider2D>();
                if (playerCol != null)
                {
                    Bounds tileBounds = new Bounds(new Vector3(gx + 0.5f, -ty + 0.5f, 0f), Vector3.one * 0.95f);
                    if (playerCol.bounds.Intersects(tileBounds))
                    {
                        return false;
                    }
                }
            }

            chunkManager.SetTile(gx, ty, tileToPlace);
            PotariaHUD.Instance.DecrementActiveItem();
            return true;
        }

        public static int ResolveTileIdFromItem(string itemId)
        {
            if (string.IsNullOrEmpty(itemId)) return WorldConstants.TileAir;

            if (itemId.Contains("torch")) return WorldConstants.TileTorch;
            if (itemId.Contains("dirt")) return WorldConstants.TileDirt;
            if (itemId.Contains("stone")) return WorldConstants.TileStone;
            if (itemId.Contains("wood")) return WorldConstants.TileWoodPlanks;
            if (itemId.Contains("copper_ore")) return WorldConstants.TileCopperOre;
            if (itemId.Contains("iron_ore")) return WorldConstants.TileIronOre;

            return WorldConstants.TileAir;
        }

        private void UpdateBreakProgressBar(Vector3 tileCenter)
        {
            if (chunkManager == null || _breakBarRoot == null) return;

            int dmg = chunkManager.GetTileDamage(_currentGx, _currentTy);
            int currentTile = chunkManager.GetTile(_currentGx, _currentTy);

            if (dmg > 0 && currentTile != WorldConstants.TileAir && chunkManager.Database != null)
            {
                var def = chunkManager.Database.GetTile(currentTile);
                int hardness = (def != null && def.Hardness > 0) ? def.Hardness : 20;
                float breakPct = Mathf.Clamp01((float)dmg / (float)hardness);

                if (breakPct > 0f)
                {
                    _breakBarRoot.SetActive(true);
                    _breakBarRoot.transform.position = tileCenter + new Vector3(0f, -0.42f, 0f);

                    float fillWidth = 0.80f * breakPct;
                    _breakBarFill.transform.localScale = new Vector3(fillWidth, 0.10f, 1f);
                    _breakBarFill.transform.localPosition = new Vector3(-0.40f + (fillWidth * 0.5f), 0f, 0f);

                    // Pygame color gradient: yellow (< 0.6) to hot orange (>= 0.6)
                    _breakBarFill.color = (breakPct < 0.6f)
                        ? new Color(1.0f, 0.84f, 0.24f, 1.0f)
                        : new Color(1.0f, 0.47f, 0.12f, 1.0f);
                    return;
                }
            }

            _breakBarRoot.SetActive(false);
        }

        public static Sprite CreateProceduralReticleSprite()
        {
            int size = 16;
            var tex = new Texture2D(size, size, TextureFormat.RGBA32, false);
            tex.filterMode = FilterMode.Point;
            Color clear = new Color(0f, 0f, 0f, 0f);
            Color bracketCol = Color.white;

            for (int y = 0; y < size; y++)
            {
                for (int x = 0; x < size; x++)
                {
                    bool isBorder = false;
                    // Top-left bracket [
                    if ((x == 0 || x == 1) && (y >= 11 || y <= 4)) isBorder = true;
                    if ((y == 0 || y == 1 || y == 14 || y == 15) && (x <= 4 || x >= 11)) isBorder = true;
                    // Right bracket ]
                    if ((x == 14 || x == 15) && (y >= 11 || y <= 4)) isBorder = true;

                    tex.SetPixel(x, y, isBorder ? bracketCol : clear);
                }
            }
            tex.Apply();
            return Sprite.Create(tex, new Rect(0, 0, size, size), new Vector2(0.5f, 0.5f), 16f);
        }

        public static Sprite CreateSolidPixelSprite()
        {
            var tex = new Texture2D(1, 1, TextureFormat.RGBA32, false);
            tex.filterMode = FilterMode.Point;
            tex.SetPixel(0, 0, Color.white);
            tex.Apply();
            return Sprite.Create(tex, new Rect(0, 0, 1, 1), new Vector2(0.5f, 0.5f), 1f);
        }
    }
}
