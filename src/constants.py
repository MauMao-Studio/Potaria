"""
Potaria - Constants and Game Definitions
Developer: Kurados
"""

# Screen & Display Settings
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
FPS = 60
TITLE = "Potaria - The Spudtastic Adventure"
DEVELOPER = "Kurados"
GAME_VERSION = "0.2.0a"
SCALE = 2  # 16x16 tiles rendered at 32x32
TILE_SIZE = 16
SCALED_TILE = TILE_SIZE * SCALE  # 32 pixels

# World Dimensions (in tiles)
WORLD_WIDTH = 450
WORLD_HEIGHT = 240
SURFACE_LEVEL = 70       # Avg surface height
UNDERGROUND_LEVEL = 115  # Transition to stone
CAVERN_LEVEL = 160       # Deep caves
DUNGEON_LEVEL = 205      # Deep Nether Dungeon where Lord Malus resides

# Physics Constants
GRAVITY = 0.44
TERMINAL_VELOCITY = 10.0
PLAYER_SPEED = 3.0
PLAYER_ACCEL = 0.35
PLAYER_FRICTION = 0.22
PLAYER_JUMP_FORCE = -8.0
PLAYER_DROP_THROUGH_TIME = 15

# Player Dimensions & Collider
PLAYER_WIDTH = 28
PLAYER_HEIGHT = 32            # 1 block tall (SCALED_TILE) body collider, excludes decorative head sprout leaf
PLAYER_SPRITE_WIDTH = 28
PLAYER_SPRITE_HEIGHT = 36     # Full visual sprite dimensions including sprout leaf

# Block IDs
TILE_AIR = 0
TILE_DIRT = 1
TILE_GRASS = 2
TILE_STONE = 3
TILE_WOOD = 4
TILE_LEAVES = 5
TILE_WOOD_TRUNK = 6
TILE_COPPER_ORE = 7
TILE_IRON_ORE = 8
TILE_GOLD_ORE = 9
TILE_WOOD_PLATFORM = 10
TILE_WORK_BENCH = 11
TILE_FURNACE = 12
TILE_TORCH = 13
TILE_STONE_BRICK = 14
TILE_BEDROCK = 15          # Unbreakable boundary barrier
TILE_DUNGEON_BRICK = 16   # Nether Dungeon wall/floor
TILE_DUNGEON_ALTAR = 17   # Boss summoning altar
TILE_SAND = 18            # Desert surface sand
TILE_SANDSTONE = 19       # Desert subterranean stone
TILE_CACTUS = 20          # Desert cactus plant
TILE_SNOW = 21            # Snow biome surface
TILE_ICE = 22             # Snow biome slippery ice
TILE_CORRUPT_GRASS = 23   # Legacy alias for The Blight purple surface grass
TILE_BLIGHT_GRASS = 23    # The Blight purple surface grass
TILE_EBONSTONE = 24       # Legacy alias for The Blight dark purple stone
TILE_BLIGHTSTONE = 24     # The Blight dark purple stone
TILE_MUSHROOM_GRASS = 25  # Glowing underground mushroom grass
TILE_MUSHROOM_STEM = 26   # Giant mushroom stem
TILE_MUSHROOM_CAP = 27    # Giant glowing mushroom cap (glows blue)
TILE_CHEST = 28           # Underground treasure chest with rare loot!
TILE_WOODEN_CHEST = 28    # Alias for TILE_CHEST
TILE_ROOF_TILES = 29       # Decorative red clay roof shingles
TILE_WOOD_PLANKS = 30      # Sanded polished wooden floor & wall blocks
TILE_GLASS = 31            # Transparent window glass block
TILE_DOOR_CLOSED = 32      # Solid wooden door (keeps out mobs)
TILE_DOOR_OPEN = 33        # Open wooden door
TILE_TABLE = 34            # Crafted wooden table
TILE_CHAIR = 35            # Crafted wooden chair
TILE_BARRIER = 36          # Shield-Weaver magical barrier block (blocks falling stars/arrows)
TILE_WATER = 37            # Liquid water with surface waves, swimming, and oxygen mechanics
TILE_BED = 38              # Handcrafted bed for respawn & rest healing
TILE_BOOKSHELF = 39        # Wooden bookshelf lined with scholarly tomes
TILE_GRANDFATHER_CLOCK = 40# Towering pendulum clock for checking celestial time
TILE_FIREPLACE = 41        # Stone fireplace emitting warm light and smoke
TILE_CANDELABRA = 42       # Ornate 3-prong brass candelabra
TILE_CHANDELIER = 43       # Grand 4-candle hanging ceiling chandelier
TILE_POTTED_PLANT = 44     # Terracotta pot with leafy potato bonsai
TILE_DRESSER = 45          # Carved wooden dresser with brass pulls
TILE_TAPESTRY = 46         # Woven royal wall banner with golden emblem
TILE_BATHTUB = 47          # Enamel clawfoot bathtub with soothing bathwater
TILE_SINK = 48             # Porcelain washbasin with faucet & vanity
TILE_PAINTING = 49         # Gilded landscape wall painting
TILE_WOOD_SHELF = 50       # Bracketed wooden shelf platform
TILE_CARVED_TUBER_LANTERN = 51 # Hollowed glowing potato lantern (can hang from North ceiling)
TILE_BRASS_LANTERN = 52        # Weatherproof brass oil lantern (can hang from North ceiling)
TILE_SPECTRAL_LANTERN = 53     # Azure spectral lantern (can hang from North ceiling)
TILE_SAPLING = 54              # Young tree sapling that grows daily in sunlight
TILE_IRON_CHEST = 55           # Fortified silver iron storage chest (distinct from golden treasure chest)
TILE_ROPE_RUNGS = 56           # Vertical climbable knotted fiber rope rungs
TILE_DUNGEON_MAGMA = 57        # Nether Magma Dungeon Brick (indestructible)
TILE_DUNGEON_ICE = 58          # Permafrost Crypt Dungeon Brick (indestructible)
TILE_DUNGEON_BONE = 59         # Ancient Catacomb Bone Brick (indestructible)
TILE_DUNGEON_GATE = 60         # Indestructible Dungeon Gate / Portcullis Arch

LANTERN_TILES = (
    TILE_CARVED_TUBER_LANTERN,
    TILE_BRASS_LANTERN,
    TILE_SPECTRAL_LANTERN,
    TILE_CHANDELIER,
)

# Wall IDs (Background)
WALL_AIR = 0
WALL_DIRT = 1
WALL_STONE = 2
WALL_WOOD = 3
WALL_STONE_BRICK = 4
WALL_DUNGEON = 5
WALL_SANDSTONE = 6
WALL_ICE = 7
WALL_EBONSTONE = 8         # Legacy alias for Blightstone wall
WALL_BLIGHTSTONE = 8       # Blightstone wall
WALL_MUSHROOM = 9
WALL_GLASS = 10
WALL_DUNGEON_MAGMA = 11
WALL_DUNGEON_ICE = 12
WALL_DUNGEON_BONE = 13

# Biome Definitions
BIOME_FOREST = "forest"
BIOME_DESERT = "desert"
BIOME_SNOW = "snow"
BIOME_CORRUPTION = "corruption" # Legacy alias for the_blight
BIOME_BLIGHT = "the_blight"     # Original Potaria biome
BIOME_MUSHROOM = "mushroom"
BIOME_DUNGEON = "dungeon"
BIOME_CAVERN = "cavern"

# Game Modes & Mod Options
MODE_ADVENTURE = "adventure"
MODE_LAST_MAN_STANDING = "last_man_standing"
AVAILABLE_MODES = [MODE_ADVENTURE, MODE_LAST_MAN_STANDING]

# Difficulty Modes
DIFFICULTY_NORMAL = "normal"
DIFFICULTY_HARDCORE = "hardcore"
DIFFICULTY_YOLO = "yolo"

# World Types
WORLD_TYPE_INFINITE = "infinite"
WORLD_TYPE_FINITE = "finite"

# Tile Properties Dictionary
TILE_PROPS = {
    TILE_AIR: {"name": "Air", "hardness": 0, "drop": None, "solid": False, "platform": False, "light_emit": 0, "absorb": 0, "opaque": False},
    TILE_DIRT: {"name": "Dirt", "hardness": 15, "drop": "dirt_block", "solid": True, "platform": False, "light_emit": 0, "absorb": 3, "opaque": True},
    TILE_GRASS: {"name": "Grass", "hardness": 18, "drop": "dirt_block", "solid": True, "platform": False, "light_emit": 0, "absorb": 3, "opaque": True},
    TILE_STONE: {"name": "Stone", "hardness": 35, "drop": "stone_block", "solid": True, "platform": False, "light_emit": 0, "absorb": 4, "opaque": True},
    TILE_WOOD: {"name": "Wood", "hardness": 20, "drop": "wood", "solid": True, "platform": False, "light_emit": 0, "absorb": 3, "opaque": True},
    TILE_LEAVES: {"name": "Leaves", "hardness": 5, "drop": "leaves", "solid": False, "platform": False, "light_emit": 0, "absorb": 1, "opaque": False},
    TILE_WOOD_TRUNK: {"name": "Wood Trunk", "hardness": 20, "drop": "wood", "solid": False, "platform": False, "light_emit": 0, "absorb": 2, "opaque": False},
    TILE_COPPER_ORE: {"name": "Copper Ore", "hardness": 40, "drop": "copper_ore", "solid": True, "platform": False, "light_emit": 0, "absorb": 4, "opaque": True},
    TILE_IRON_ORE: {"name": "Iron Ore", "hardness": 45, "drop": "iron_ore", "solid": True, "platform": False, "light_emit": 0, "absorb": 4, "opaque": True},
    TILE_GOLD_ORE: {"name": "Gold Ore", "hardness": 55, "drop": "gold_ore", "solid": True, "platform": False, "light_emit": 1, "absorb": 4, "opaque": True},
    TILE_WOOD_PLATFORM: {"name": "Wood Platform", "hardness": 10, "drop": "wood_platform", "solid": False, "platform": True, "light_emit": 0, "absorb": 0, "opaque": False},
    TILE_WORK_BENCH: {"name": "Work Bench", "hardness": 25, "drop": "work_bench", "solid": False, "platform": True, "light_emit": 0, "absorb": 0, "opaque": False},
    TILE_FURNACE: {"name": "Furnace", "hardness": 40, "drop": "furnace", "solid": False, "platform": False, "light_emit": 8, "absorb": 0, "opaque": False},
    TILE_TORCH: {"name": "Torch", "hardness": 5, "drop": "torch", "solid": False, "platform": False, "light_emit": 14, "absorb": 0, "opaque": False},
    TILE_STONE_BRICK: {"name": "Stone Brick", "hardness": 38, "drop": "stone_brick", "solid": True, "platform": False, "light_emit": 0, "absorb": 4, "opaque": True},
    TILE_BEDROCK: {"name": "Bedrock", "hardness": 9999, "drop": None, "solid": True, "platform": False, "light_emit": 0, "absorb": 15, "opaque": True},
    TILE_DUNGEON_BRICK: {"name": "Dungeon Brick", "hardness": 9999, "drop": None, "solid": True, "platform": False, "light_emit": 1, "absorb": 15, "opaque": True, "indestructible": True},
    TILE_DUNGEON_ALTAR: {"name": "Dungeon Altar", "hardness": 9999, "drop": None, "solid": False, "platform": True, "light_emit": 6, "absorb": 0, "opaque": False, "indestructible": True},
    TILE_DUNGEON_MAGMA: {"name": "Nether Magma Dungeon Brick", "hardness": 9999, "drop": None, "solid": True, "platform": False, "light_emit": 2, "absorb": 15, "opaque": True, "indestructible": True},
    TILE_DUNGEON_ICE: {"name": "Permafrost Crypt Dungeon Brick", "hardness": 9999, "drop": None, "solid": True, "platform": False, "light_emit": 1, "absorb": 15, "opaque": True, "indestructible": True},
    TILE_DUNGEON_BONE: {"name": "Catacomb Bone Brick", "hardness": 9999, "drop": None, "solid": True, "platform": False, "light_emit": 1, "absorb": 15, "opaque": True, "indestructible": True},
    TILE_DUNGEON_GATE: {"name": "Dungeon Gate Portcullis", "hardness": 9999, "drop": None, "solid": False, "platform": False, "light_emit": 1, "absorb": 0, "opaque": False, "indestructible": True},
    TILE_SAND: {"name": "Sand", "hardness": 12, "drop": "sand_block", "solid": True, "platform": False, "light_emit": 0, "absorb": 2, "opaque": True},
    TILE_SANDSTONE: {"name": "Sandstone", "hardness": 30, "drop": "sandstone_block", "solid": True, "platform": False, "light_emit": 0, "absorb": 4, "opaque": True},
    TILE_CACTUS: {"name": "Cactus", "hardness": 15, "drop": "cactus", "solid": False, "platform": False, "light_emit": 0, "absorb": 1, "opaque": False},
    TILE_SNOW: {"name": "Snow", "hardness": 10, "drop": "snow_block", "solid": True, "platform": False, "light_emit": 0, "absorb": 2, "opaque": True},
    TILE_ICE: {"name": "Ice", "hardness": 22, "drop": "ice_block", "solid": True, "platform": False, "light_emit": 0, "absorb": 2, "opaque": True},
    TILE_BLIGHT_GRASS: {"name": "Blight Grass", "hardness": 25, "drop": "dirt_block", "solid": True, "platform": False, "light_emit": 1, "absorb": 4, "opaque": True},
    TILE_BLIGHTSTONE: {"name": "Blightstone", "hardness": 50, "drop": "blightstone_block", "solid": True, "platform": False, "light_emit": 0, "absorb": 5, "opaque": True},
    TILE_MUSHROOM_GRASS: {"name": "Glowing Mushroom Grass", "hardness": 20, "drop": "glowing_mushroom", "solid": True, "platform": False, "light_emit": 6, "absorb": 2, "opaque": True},
    TILE_MUSHROOM_STEM: {"name": "Mushroom Stem", "hardness": 15, "drop": "wood", "solid": False, "platform": False, "light_emit": 2, "absorb": 1, "opaque": False},
    TILE_MUSHROOM_CAP: {"name": "Glowing Mushroom Cap", "hardness": 12, "drop": "glowing_mushroom", "solid": False, "platform": False, "light_emit": 9, "absorb": 0, "opaque": False},
    TILE_CHEST: {"name": "Treasure Chest", "hardness": 30, "drop": "chest", "solid": False, "platform": True, "light_emit": 3, "absorb": 0, "opaque": False},
    TILE_ROOF_TILES: {"name": "Roof Tiles", "hardness": 25, "drop": "roof_tiles", "solid": True, "platform": False, "light_emit": 0, "absorb": 3, "opaque": True},
    TILE_WOOD_PLANKS: {"name": "Wood Planks", "hardness": 20, "drop": "wood_planks", "solid": True, "platform": False, "light_emit": 0, "absorb": 3, "opaque": True},
    TILE_GLASS: {"name": "Glass Window", "hardness": 10, "drop": "glass_window", "solid": True, "platform": False, "light_emit": 0, "absorb": 0, "opaque": False},
    TILE_DOOR_CLOSED: {"name": "Wooden Door", "hardness": 20, "drop": "wooden_door", "solid": True, "platform": False, "light_emit": 0, "absorb": 1, "opaque": False},
    TILE_DOOR_OPEN: {"name": "Open Wooden Door", "hardness": 20, "drop": "wooden_door", "solid": False, "platform": False, "light_emit": 0, "absorb": 0, "opaque": False},
    TILE_TABLE: {"name": "Wooden Table", "hardness": 20, "drop": "wooden_table", "solid": False, "platform": True, "light_emit": 0, "absorb": 0, "opaque": False},
    TILE_CHAIR: {"name": "Wooden Chair", "hardness": 15, "drop": "wooden_chair", "solid": False, "platform": False, "light_emit": 0, "absorb": 0, "opaque": False},
    TILE_BARRIER: {"name": "Magical Barrier", "hardness": 30, "drop": None, "solid": True, "platform": False, "light_emit": 10, "absorb": 0, "opaque": False},
    TILE_WATER: {"name": "Water", "hardness": 9999, "drop": None, "solid": False, "platform": False, "liquid": True, "light_emit": 0, "absorb": 2, "opaque": False},
    TILE_BED: {"name": "Wooden Bed", "hardness": 20, "drop": "wooden_bed", "solid": False, "platform": True, "light_emit": 0, "absorb": 0, "opaque": False},
    TILE_BOOKSHELF: {"name": "Bookshelf", "hardness": 20, "drop": "bookshelf", "solid": False, "platform": True, "light_emit": 0, "absorb": 0, "opaque": False},
    TILE_GRANDFATHER_CLOCK: {"name": "Grandfather Clock", "hardness": 25, "drop": "grandfather_clock", "solid": False, "platform": False, "light_emit": 1, "absorb": 0, "opaque": False},
    TILE_FIREPLACE: {"name": "Stone Fireplace", "hardness": 35, "drop": "stone_fireplace", "solid": False, "platform": True, "light_emit": 13, "absorb": 0, "opaque": False},
    TILE_CANDELABRA: {"name": "Candelabra", "hardness": 10, "drop": "candelabra", "solid": False, "platform": False, "light_emit": 12, "absorb": 0, "opaque": False},
    TILE_CHANDELIER: {"name": "Chandelier", "hardness": 12, "drop": "chandelier", "solid": False, "platform": False, "light_emit": 14, "absorb": 0, "opaque": False},
    TILE_POTTED_PLANT: {"name": "Potted Spud Plant", "hardness": 10, "drop": "potted_plant", "solid": False, "platform": False, "light_emit": 2, "absorb": 0, "opaque": False},
    TILE_DRESSER: {"name": "Wooden Dresser", "hardness": 20, "drop": "wooden_dresser", "solid": False, "platform": True, "light_emit": 0, "absorb": 0, "opaque": False},
    TILE_TAPESTRY: {"name": "Wall Tapestry", "hardness": 8, "drop": "wall_tapestry", "solid": False, "platform": False, "light_emit": 0, "absorb": 0, "opaque": False},
    TILE_BATHTUB: {"name": "Bathtub", "hardness": 25, "drop": "bathtub", "solid": False, "platform": True, "light_emit": 0, "absorb": 0, "opaque": False},
    TILE_SINK: {"name": "Sink", "hardness": 20, "drop": "sink", "solid": False, "platform": True, "light_emit": 0, "absorb": 0, "opaque": False},
    TILE_PAINTING: {"name": "Painting", "hardness": 8, "drop": "painting", "solid": False, "platform": False, "light_emit": 1, "absorb": 0, "opaque": False},
    TILE_WOOD_SHELF: {"name": "Wood Shelf", "hardness": 10, "drop": "wood_shelf", "solid": False, "platform": True, "light_emit": 0, "absorb": 0, "opaque": False},
    TILE_CARVED_TUBER_LANTERN: {"name": "Carved Tuber Lantern", "hardness": 8, "drop": "carved_tuber_lantern", "solid": False, "platform": False, "light_emit": 14, "absorb": 0, "opaque": False},
    TILE_BRASS_LANTERN: {"name": "Brass Lantern", "hardness": 10, "drop": "brass_lantern", "solid": False, "platform": False, "light_emit": 14, "absorb": 0, "opaque": False},
    TILE_SPECTRAL_LANTERN: {"name": "Spectral Lantern", "hardness": 10, "drop": "spectral_lantern", "solid": False, "platform": False, "light_emit": 14, "absorb": 0, "opaque": False},
    TILE_SAPLING: {"name": "Oak Sapling", "hardness": 5, "drop": "oak_sapling", "solid": False, "platform": False, "light_emit": 0, "absorb": 0, "opaque": False},
    TILE_IRON_CHEST: {"name": "Iron Storage Chest", "hardness": 35, "drop": "iron_chest", "solid": False, "platform": True, "light_emit": 0, "absorb": 0, "opaque": False},
    TILE_ROPE_RUNGS: {"name": "Rope Rungs", "hardness": 10, "drop": "rope_rungs", "solid": False, "platform": True, "light_emit": 0, "absorb": 0, "opaque": False},
}

# Item Rarity Tiers (7 Tiers)
RARITY_COMMON = "common"
RARITY_UNCOMMON = "uncommon"
RARITY_RARE = "rare"
RARITY_EPIC = "epic"
RARITY_MYTHIC = "mythic"
RARITY_LEGENDARY = "legendary"
RARITY_ANCIENT = "ancient"

RARITY_ORDER = [
    RARITY_COMMON,
    RARITY_UNCOMMON,
    RARITY_RARE,
    RARITY_EPIC,
    RARITY_MYTHIC,
    RARITY_LEGENDARY,
    RARITY_ANCIENT,
]

RARITY_HEX_COLORS = {
    RARITY_COMMON: "#9E9E9E",
    RARITY_UNCOMMON: "#4CAF50",
    RARITY_RARE: "#2196F3",
    RARITY_EPIC: "#9C27B0",
    RARITY_MYTHIC: "#FF9800",
    RARITY_LEGENDARY: "#FFD700",
    RARITY_ANCIENT: "#F44336",
}

RARITY_COLORS = {
    RARITY_COMMON: (158, 158, 158),
    RARITY_UNCOMMON: (76, 175, 80),
    RARITY_RARE: (33, 150, 243),
    RARITY_EPIC: (156, 39, 176),
    RARITY_MYTHIC: (255, 152, 0),
    RARITY_LEGENDARY: (255, 215, 0),
    RARITY_ANCIENT: (244, 67, 54),
}

# Item Categories
CAT_TOOL = "tool"
CAT_WEAPON = "weapon"
CAT_BLOCK = "block"
CAT_WALL = "wall"
CAT_MATERIAL = "material"
CAT_CONSUMABLE = "consumable"
CAT_SPECIAL = "special"
CAT_ACCESSORY = "accessory"
CAT_CURRENCY = "currency"

# Crafting Recipe Categories (Minecraft-Style Recipe Book)
CRAFT_CAT_ALL = "all"
CRAFT_CAT_BUILDING = "building"
CRAFT_CAT_EQUIPMENT = "equipment"
CRAFT_CAT_SURVIVAL = "survival"
CRAFT_CAT_FURNITURE = "furniture"

# Inventory Configurations
HOTBAR_SLOTS = 10
INV_COLS = 10
INV_ROWS = 4
INV_TOTAL_SLOTS = INV_COLS * INV_ROWS
SLOT_SIZE = 40
SLOT_PADDING = 4

# Lighting Levels
MAX_LIGHT = 15
MIN_LIGHT = 1

# Game States
STATE_MENU = "menu"
STATE_STORY = "story"
STATE_CUTSCENE = "cutscene"
STATE_CONTROLS = "controls"
STATE_SETTINGS = "settings"
STATE_MULTIPLAYER = "multiplayer"
STATE_PLAYING = "playing"
STATE_VICTORY = "victory"
STATE_GAME_OVER = "game_over"
STATE_WORLDS = "worlds"
STATE_NEW_WORLD = "new_world"
STATE_MODS = "mods"
STATE_ACHIEVEMENTS = "achievements"

# Color Palette (RGB)
COLOR_WHITE = (255, 255, 255)
COLOR_BLACK = (0, 0, 0)
COLOR_POTATO_BODY = (205, 155, 90)
COLOR_POTATO_HIGHLIGHT = (235, 185, 120)
COLOR_POTATO_SHADOW = (165, 115, 60)
COLOR_SPROUT = (60, 200, 70)
COLOR_GOLD = (255, 215, 0)
COLOR_RED_HEART = (220, 30, 40)
COLOR_UI_BG = (35, 40, 58, 220)
COLOR_UI_BORDER = (85, 95, 130)
COLOR_UI_HIGHLIGHT = (255, 230, 100)

# Mobile Virtual Touch Controls
TOUCH_MODE_AUTO = "auto"
TOUCH_MODE_ON = "on"
TOUCH_MODE_OFF = "off"
TOUCH_OPACITY_50 = 0.50
TOUCH_OPACITY_75 = 0.75
TOUCH_OPACITY_100 = 1.00
