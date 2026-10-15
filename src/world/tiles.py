"""
Potaria - Tile Definitions & Sapling Ecosystem
Developer: Kurados | Pure Python & pygame-ce
"""

from src.constants import (
    TILE_AIR, TILE_DIRT, TILE_GRASS, TILE_STONE, TILE_WOOD, TILE_LEAVES,
    TILE_WOOD_TRUNK, TILE_COPPER_ORE, TILE_IRON_ORE, TILE_GOLD_ORE,
    TILE_WOOD_PLATFORM, TILE_WORK_BENCH, TILE_FURNACE, TILE_TORCH,
    TILE_STONE_BRICK, TILE_BEDROCK, TILE_DUNGEON_BRICK, TILE_DUNGEON_ALTAR,
    TILE_SAND, TILE_SANDSTONE, TILE_CACTUS, TILE_SNOW, TILE_ICE,
    TILE_CORRUPT_GRASS, TILE_BLIGHT_GRASS, TILE_EBONSTONE, TILE_BLIGHTSTONE,
    TILE_MUSHROOM_GRASS, TILE_MUSHROOM_STEM, TILE_MUSHROOM_CAP,
    TILE_CHEST, TILE_WOODEN_CHEST, TILE_ROOF_TILES, TILE_WOOD_PLANKS,
    TILE_GLASS, TILE_DOOR_CLOSED, TILE_DOOR_OPEN, TILE_TABLE, TILE_CHAIR,
    TILE_BARRIER, TILE_WATER, TILE_BED, TILE_BOOKSHELF,
    TILE_GRANDFATHER_CLOCK, TILE_FIREPLACE, TILE_CANDELABRA, TILE_CHANDELIER,
    TILE_POTTED_PLANT, TILE_DRESSER, TILE_TAPESTRY, TILE_BATHTUB,
    TILE_SINK, TILE_PAINTING, TILE_WOOD_SHELF,
    TILE_CARVED_TUBER_LANTERN, TILE_BRASS_LANTERN, TILE_SPECTRAL_LANTERN,
    TILE_SAPLING, TILE_SAPLING_OAK, TILE_SAPLING_PALM, TILE_SAPLING_PINE, TILE_SAPLING_BLIGHT,
    TILE_IRON_CHEST, TILE_ROPE_RUNGS,
    TILE_DUNGEON_MAGMA, TILE_DUNGEON_ICE, TILE_DUNGEON_BONE, TILE_DUNGEON_GATE,
    TILE_LAMP,
    TILE_OAK_WOOD, TILE_OAK_LEAVES, TILE_OAK_TRUNK,
    TILE_PINE_WOOD, TILE_PINE_LEAVES, TILE_PINE_TRUNK,
    TILE_PALM_WOOD, TILE_PALM_LEAVES, TILE_PALM_TRUNK,
    TILE_BLIGHT_WOOD, TILE_BLIGHT_LEAVES, TILE_BLIGHT_TRUNK,
    WOOD_TILES, TRUNK_TILES, ALL_WOOD_TILES, ALL_LEAF_TILES,
    WOOD_VARIANTS, WOOD_VARIANTS_SET, LEAF_VARIANTS, LEAF_VARIANTS_SET,
    SAPLING_TILES, SAPLING_TILE_TO_ITEM, SAPLING_ITEM_TO_TILE,
    LANTERN_TILES,
    WALL_AIR, WALL_DIRT, WALL_STONE, WALL_WOOD, WALL_STONE_BRICK,
    WALL_DUNGEON, WALL_SANDSTONE, WALL_ICE, WALL_EBONSTONE, WALL_BLIGHTSTONE,
    WALL_MUSHROOM, WALL_GLASS, WALL_DUNGEON_MAGMA, WALL_DUNGEON_ICE, WALL_DUNGEON_BONE,
    TILE_PROPS
)


def is_sapling_tile(tile_id: int) -> bool:
    """Returns True if the given tile ID is any tree sapling variant."""
    return tile_id in SAPLING_TILES or tile_id == TILE_SAPLING


def get_sapling_item(tile_id: int):
    """Returns the dropped item identifier for a given sapling tile ID, or None if not a sapling."""
    return SAPLING_TILE_TO_ITEM.get(tile_id, None)


def get_sapling_tile(item_id: str):
    """Returns the corresponding world tile ID for a given sapling item identifier, or None if not a sapling item."""
    if item_id is None:
        return None
    clean = str(item_id).lower().strip().replace(" ", "_")
    return SAPLING_ITEM_TO_TILE.get(clean, None)


def is_wood_tile(tile_id: int) -> bool:
    """Returns True if the given tile ID is any wood variant (trunk or solid block)."""
    return tile_id in ALL_WOOD_TILES


def is_trunk_tile(tile_id: int) -> bool:
    """Returns True if the given tile ID is any tree trunk variant."""
    return tile_id in TRUNK_TILES


def is_leaf_tile(tile_id: int) -> bool:
    """Returns True if the given tile ID is any tree leaves / foliage variant."""
    return tile_id in ALL_LEAF_TILES

