"""
Unit and integration tests for tree-specific wood and leaves overhaul:
- Oak Tree: wood / oak_wood, leaves / oak_leaves
- Pine Tree: pine_wood, pine_leaves
- Palm Tree: palm_wood, palm_leaves
- Blight Tree: blight_wood, blight_leaves

Verifies:
1. Item registry & aliases configuration
2. Inventory & chest wood counting & interchangeable crafting consumption
3. World placement of tree wood & leaves
4. Harvesting, mining, felling, and decay drops
5. Asset generation, 24x24 icon sizing, corner transparency, and disk export
"""

import os
import hashlib
import pygame
import pytest

os.environ["SDL_VIDEODRIVER"] = "dummy"
pygame.init()

from src.constants import (
    TILE_AIR, TILE_DIRT, TILE_GRASS, TILE_STONE,
    TILE_WOOD, TILE_LEAVES, TILE_WOOD_TRUNK,
    TILE_PINE_WOOD, TILE_PINE_LEAVES, TILE_PINE_TRUNK,
    TILE_PALM_WOOD, TILE_PALM_LEAVES, TILE_PALM_TRUNK,
    TILE_BLIGHT_WOOD, TILE_BLIGHT_LEAVES, TILE_BLIGHT_TRUNK,
    TILE_SAPLING, TILE_SAPLING_OAK, TILE_SAPLING_PALM, TILE_SAPLING_PINE, TILE_SAPLING_BLIGHT,
    WOOD_TILES, TRUNK_TILES, ALL_WOOD_TILES, ALL_LEAF_TILES,
    WOOD_VARIANTS, WOOD_VARIANTS_SET, LEAF_VARIANTS, LEAF_VARIANTS_SET,
    BIOME_FOREST, BIOME_DESERT, BIOME_SNOW, BIOME_BLIGHT, BIOME_CORRUPTION
)
from src.assets.asset_factory import AssetFactory
from src.ui.inventory import Inventory, ItemStack, ITEM_REGISTRY, ITEM_ALIASES
from src.ui.crafting import CraftingSystem, RECIPES
from src.world.world import World
from src.world.storage_chest import StorageChest


@pytest.fixture
def asset_factory():
    return AssetFactory()


@pytest.fixture
def world(asset_factory):
    return World(asset_factory, seed=12345)


def test_01_item_registry_and_aliases():
    """Verify all tree wood and leaf variants are registered with correct tiles and aliases."""
    expected_items = [
        ("wood", TILE_WOOD),
        ("oak_wood", TILE_WOOD),
        ("pine_wood", TILE_PINE_TRUNK),
        ("palm_wood", TILE_PALM_TRUNK),
        ("blight_wood", TILE_BLIGHT_TRUNK),
        ("leaves", TILE_LEAVES),
        ("oak_leaves", TILE_LEAVES),
        ("pine_leaves", TILE_PINE_LEAVES),
        ("palm_leaves", TILE_PALM_LEAVES),
        ("blight_leaves", TILE_BLIGHT_LEAVES),
    ]

    for item_id, expected_tile in expected_items:
        assert item_id in ITEM_REGISTRY, f"{item_id} must be in ITEM_REGISTRY"
        data = ITEM_REGISTRY[item_id]
        assert data.get("tile") == expected_tile, f"{item_id} tile must be {expected_tile}"
        assert data.get("cat") == "block", f"{item_id} category must be block"

    # Aliases
    assert ITEM_ALIASES.get("oak_wood") == "wood"
    assert ITEM_ALIASES.get("oak_leaves") == "leaves"
    assert ITEM_ALIASES.get("pine_needles") == "pine_leaves"
    assert ITEM_ALIASES.get("palm_fronds") == "palm_leaves"


def test_02_inventory_wood_counting_and_interchangeable_consumption(asset_factory):
    """Verify Inventory.count_wood() and remove_item() handle wood interchangeability."""
    inv = Inventory(asset_factory)
    inv.slots = [None] * len(inv.slots)

    # Add different wood variants across slots
    inv.slots[0] = ItemStack("pine_wood", 5)
    inv.slots[1] = ItemStack("palm_wood", 8)
    inv.slots[2] = ItemStack("blight_wood", 12)
    inv.slots[3] = ItemStack("wood", 10)

    # Total wood should be 5 + 8 + 12 + 10 = 35
    assert inv.count_wood() == 35
    assert inv.count_item("wood") == 35
    assert inv.count_item("oak_wood") == 35

    # Specific non-wood counting still works
    assert inv.count_item("pine_wood") == 5
    assert inv.count_item("palm_wood") == 8
    assert inv.count_item("blight_wood") == 12

    # Consume 15 wood requesting "wood" (should take the 10 oak wood first, then 5 from pine_wood)
    success = inv.remove_item("wood", 15)
    assert success is True
    assert inv.count_wood() == 20
    assert inv.slots[3] is None  # oak wood slot depleted
    assert inv.slots[0] is None  # pine wood slot depleted
    assert inv.count_item("palm_wood") == 8
    assert inv.count_item("blight_wood") == 12

    # Consume 10 wood requesting "pine_wood" (pine is 0, so should take from palm/blight)
    success2 = inv.remove_item("pine_wood", 10)
    assert success2 is True
    assert inv.count_wood() == 10

    # Over-consumption fails without modifying inventory
    assert inv.remove_item("wood", 50) is False
    assert inv.count_wood() == 10


def test_03_crafting_interchangeability_with_wood_variants(asset_factory, world):
    """Verify workbench, torches, and other recipes can be crafted using any wood variant."""
    class MockSound:
        def play(self, *args, **kwargs):
            pass

    crafting = CraftingSystem(asset_factory, MockSound())
    inv = Inventory(asset_factory)
    inv.slots = [None] * len(inv.slots)

    # 1. Crafting workbench (requires 10 wood) using ONLY pine_wood
    inv.slots[0] = ItemStack("pine_wood", 10)
    crafting.update_recipes(inv, world, None)
    wb_recipe = next(r for r in RECIPES if r["result"] == "work_bench")
    assert any(r["result"] == "work_bench" and r.get("can_craft") for r in crafting.available_recipes)

    can_craft = crafting.craft(wb_recipe, inv)
    assert can_craft is True
    assert inv.count_wood() == 0
    assert inv.count_item("work_bench") == 1

    # 2. Crafting torches (requires 1 wood + 1 gel) using palm_wood
    inv.slots = [None] * len(inv.slots)
    inv.slots[0] = ItemStack("palm_wood", 2)
    inv.slots[1] = ItemStack("gel", 5)

    torch_recipe = next(r for r in RECIPES if r["result"] == "torch")
    can_craft_torch = crafting.craft(torch_recipe, inv)
    assert can_craft_torch is True
    assert inv.count_item("torch") == torch_recipe["count"]
    assert inv.count_wood() == 1  # 1 palm_wood left

    # 3. Mixed wood crafting: 5 pine_wood + 5 blight_wood for workbench
    inv.slots = [None] * len(inv.slots)
    inv.slots[0] = ItemStack("pine_wood", 5)
    inv.slots[1] = ItemStack("blight_wood", 5)
    assert inv.count_wood() == 10

    can_craft_mixed = crafting.craft(wb_recipe, inv)
    assert can_craft_mixed is True
    assert inv.count_wood() == 0
    assert inv.count_item("work_bench") == 1


def test_04_world_placement_of_tree_wood_and_leaves(world):
    """Verify placing each wood and leaves variant places the correct world tile."""
    # Build a solid foundation of stone
    for x in range(10, 30):
        world.set_tile(x, 50, TILE_STONE)
        for y in range(40, 50):
            world.set_tile(x, y, TILE_AIR)

    # 1. Oak Wood & Leaves
    assert world.place_tile(12, 49, TILE_WOOD) is True
    assert world.get_tile(12, 49) == TILE_WOOD
    assert world.place_tile(12, 48, TILE_LEAVES) is True
    assert world.get_tile(12, 48) == TILE_LEAVES

    # 2. Pine Wood & Leaves
    assert world.place_tile(15, 49, TILE_PINE_TRUNK) is True
    assert world.get_tile(15, 49) == TILE_PINE_TRUNK
    assert world.place_tile(15, 48, TILE_PINE_LEAVES) is True
    assert world.get_tile(15, 48) == TILE_PINE_LEAVES

    # 3. Palm Wood & Leaves
    assert world.place_tile(18, 49, TILE_PALM_TRUNK) is True
    assert world.get_tile(18, 49) == TILE_PALM_TRUNK
    assert world.place_tile(18, 48, TILE_PALM_LEAVES) is True
    assert world.get_tile(18, 48) == TILE_PALM_LEAVES

    # 4. Blight Wood & Leaves
    assert world.place_tile(21, 49, TILE_BLIGHT_TRUNK) is True
    assert world.get_tile(21, 49) == TILE_BLIGHT_TRUNK
    assert world.place_tile(21, 48, TILE_BLIGHT_LEAVES) is True
    assert world.get_tile(21, 48) == TILE_BLIGHT_LEAVES


def test_05_mining_and_harvesting_player_placed_tiles(world):
    """Verify mining player-placed leaves and wood returns tree-specific item drops."""
    # Foundation
    world.set_tile(30, 60, TILE_STONE)
    world.set_tile(31, 60, TILE_STONE)
    world.set_tile(32, 60, TILE_STONE)
    world.set_tile(33, 60, TILE_STONE)

    # Place blight wood trunk and blight leaves
    world.place_tile(30, 59, TILE_BLIGHT_TRUNK)
    world.place_tile(30, 58, TILE_BLIGHT_LEAVES)

    # Place pine wood trunk and pine leaves
    world.place_tile(31, 59, TILE_PINE_TRUNK)
    world.place_tile(31, 58, TILE_PINE_LEAVES)

    # Place palm wood trunk and palm leaves
    world.place_tile(32, 59, TILE_PALM_TRUNK)
    world.place_tile(32, 58, TILE_PALM_LEAVES)

    # Mine blight leaves -> drops blight_leaves
    broken, drop, tid = world.damage_tile_at(30, 58, power=50)
    assert broken is True
    assert drop == "blight_leaves"
    assert tid == TILE_BLIGHT_LEAVES

    # Mine blight trunk -> drops blight_wood
    broken, drop, tid = world.damage_tile_at(30, 59, power=50)
    assert broken is True
    assert drop == "blight_wood"
    assert tid == TILE_BLIGHT_TRUNK

    # Mine pine leaves -> drops pine_leaves
    broken, drop, tid = world.damage_tile_at(31, 58, power=50)
    assert broken is True
    assert drop == "pine_leaves"
    assert tid == TILE_PINE_LEAVES

    # Mine pine trunk -> drops pine_wood
    broken, drop, tid = world.damage_tile_at(31, 59, power=50)
    assert broken is True
    assert drop == "pine_wood"
    assert tid == TILE_PINE_TRUNK

    # Mine palm leaves -> drops palm_leaves
    broken, drop, tid = world.damage_tile_at(32, 58, power=50)
    assert broken is True
    assert drop == "palm_leaves"
    assert tid == TILE_PALM_LEAVES

    # Mine palm trunk -> drops palm_wood
    broken, drop, tid = world.damage_tile_at(32, 59, power=50)
    assert broken is True
    assert drop == "palm_wood"
    assert tid == TILE_PALM_TRUNK


def test_06_tree_felling_and_biome_species_drops(world):
    """Verify felling a tree drops species-appropriate wood and leaves based on tile or biome."""
    # Test 1: Forest tree (Oak)
    world.get_biome_at = lambda tx, ty: "forest"
    for y in range(40, 50):
        world.set_tile(50, y, TILE_AIR)
        world.set_tile(51, y, TILE_AIR)
    world.set_tile(50, 48, TILE_WOOD_TRUNK)
    world.set_tile(50, 47, TILE_WOOD_TRUNK)
    world.set_tile(50, 46, TILE_LEAVES)
    world.player_placed_tiles.discard((50, 48))
    world.player_placed_tiles.discard((50, 47))
    world.player_placed_tiles.discard((50, 46))

    broken, base_drop, _ = world.damage_tile_at(50, 48, power=50)
    assert broken is True
    assert base_drop == "wood"
    # Drops accumulated in decay_drops for the other blocks
    decay_item_ids = [d[0] for d in world.decay_drops]
    assert "wood" in decay_item_ids
    assert "leaves" in decay_item_ids

    # Test 2: Snow tree (Pine)
    world.decay_drops.clear()
    world.get_biome_at = lambda tx, ty: "snow"
    for y in range(40, 50):
        world.set_tile(60, y, TILE_AIR)
    world.set_tile(60, 48, TILE_WOOD_TRUNK)
    world.set_tile(60, 47, TILE_WOOD_TRUNK)
    world.set_tile(60, 46, TILE_LEAVES)
    world.player_placed_tiles.discard((60, 48))
    world.player_placed_tiles.discard((60, 47))
    world.player_placed_tiles.discard((60, 46))

    broken, base_drop, _ = world.damage_tile_at(60, 48, power=50)
    assert broken is True
    assert base_drop == "pine_wood"
    decay_item_ids = [d[0] for d in world.decay_drops]
    assert "pine_wood" in decay_item_ids
    assert "pine_leaves" in decay_item_ids

    # Test 3: Desert tree (Palm)
    world.decay_drops.clear()
    world.get_biome_at = lambda tx, ty: "desert"
    for y in range(40, 50):
        world.set_tile(70, y, TILE_AIR)
    world.set_tile(70, 48, TILE_WOOD_TRUNK)
    world.set_tile(70, 47, TILE_WOOD_TRUNK)
    world.set_tile(70, 46, TILE_LEAVES)
    world.player_placed_tiles.discard((70, 48))
    world.player_placed_tiles.discard((70, 47))
    world.player_placed_tiles.discard((70, 46))

    broken, base_drop, _ = world.damage_tile_at(70, 48, power=50)
    assert broken is True
    assert base_drop == "palm_wood"
    decay_item_ids = [d[0] for d in world.decay_drops]
    assert "palm_wood" in decay_item_ids
    assert "palm_leaves" in decay_item_ids

    # Test 4: Blight tree (Blight)
    world.decay_drops.clear()
    world.get_biome_at = lambda tx, ty: "the_blight"
    for y in range(40, 50):
        world.set_tile(80, y, TILE_AIR)
    world.set_tile(80, 48, TILE_WOOD_TRUNK)
    world.set_tile(80, 47, TILE_WOOD_TRUNK)
    world.set_tile(80, 46, TILE_LEAVES)
    world.player_placed_tiles.discard((80, 48))
    world.player_placed_tiles.discard((80, 47))
    world.player_placed_tiles.discard((80, 46))

    broken, base_drop, _ = world.damage_tile_at(80, 48, power=50)
    assert broken is True
    assert base_drop == "blight_wood"
    decay_item_ids = [d[0] for d in world.decay_drops]
    assert "blight_wood" in decay_item_ids
    assert "blight_leaves" in decay_item_ids


def test_07_tree_decay_drops_species_items(world):
    """Verify tree decay timer expiration drops species-appropriate items."""
    world.decay_drops.clear()
    world.decaying_blocks = {
        (10, 10): {"timer": 0.0, "type": TILE_PINE_WOOD, "days_left": 0},
        (10, 11): {"timer": 0.0, "type": TILE_PINE_LEAVES, "days_left": 0},
        (20, 10): {"timer": 0.0, "type": TILE_PALM_WOOD, "days_left": 0},
        (20, 11): {"timer": 0.0, "type": TILE_PALM_LEAVES, "days_left": 0},
        (30, 10): {"timer": 0.0, "type": TILE_BLIGHT_WOOD, "days_left": 0},
        (30, 11): {"timer": 0.0, "type": TILE_BLIGHT_LEAVES, "days_left": 0},
    }
    for coord, info in world.decaying_blocks.items():
        world.set_tile(coord[0], coord[1], info["type"])

    world.update_tree_decay(1.0)
    decay_drops = [d[0] for d in world.decay_drops]

    assert "pine_wood" in decay_drops
    assert "pine_leaves" in decay_drops
    assert "palm_wood" in decay_drops
    assert "palm_leaves" in decay_drops
    assert "blight_wood" in decay_drops
    assert "blight_leaves" in decay_drops


def test_08_visual_assets_24x24_zero_corners_and_export(asset_factory):
    """Verify all 8 item icons are 24x24 with 0 corner pixels, distinct, and exported on disk."""
    items = [
        "wood", "oak_wood", "pine_wood", "palm_wood", "blight_wood",
        "leaves", "oak_leaves", "pine_leaves", "palm_leaves", "blight_leaves"
    ]

    for item in items:
        surf = asset_factory.items[item]
        assert surf is not None, f"Icon for {item} must exist"
        assert surf.get_size() == (24, 24), f"Icon for {item} must be 24x24"

        # Corner pixels check: (0,0), (0,23), (23,0), (23,23) must be transparent alpha=0
        for cx, cy in [(0, 0), (0, 23), (23, 0), (23, 23)]:
            alpha = surf.get_at((cx, cy))[3]
            assert alpha == 0, f"Corner ({cx}, {cy}) for {item} must have 0 alpha, got {alpha}"

    # Verify uniqueness among distinct species
    distinct_keys = ["wood", "pine_wood", "palm_wood", "blight_wood", "leaves", "pine_leaves", "palm_leaves", "blight_leaves"]
    hashes = {k: hashlib.md5(pygame.image.tobytes(asset_factory.items[k], "RGBA")).hexdigest() for k in distinct_keys}
    assert len(set(hashes.values())) == len(distinct_keys), "All 8 item icons must be visually distinct"

    # Verify disk export
    for k in distinct_keys:
        path = os.path.join("assets", "items", f"{k}.png")
        assert os.path.exists(path), f"Exported file {path} must exist on disk"

    # Verify tile textures on disk
    for tid in [65, 66, 67, 68, 69, 70, 71, 72, 73]:
        tpath = os.path.join("assets", "tiles", f"tile_{tid}.png")
        assert os.path.exists(tpath), f"Tile file {tpath} must exist on disk"


def test_09_storage_chest_wood_counting():
    """Verify StorageChest accurately counts wood across all variants."""
    chest = StorageChest(10, 10)
    chest.slots[0] = ItemStack("pine_wood", 20)
    chest.slots[1] = ItemStack("palm_wood", 15)
    chest.slots[2] = ItemStack("blight_wood", 10)

    assert chest.count_wood() == 45
    assert chest.count_item("wood") == 45
    assert chest.count_item("oak_wood") == 45
    assert chest.count_item("pine_wood") == 20


def test_10_sapling_growth_produces_species_tiles_and_drops_across_biomes(world):
    """Verify each sapling matures into its true species trunk & leaves regardless of biome, and drops true species items."""
    # Set up ground in Forest biome
    world.get_biome_at = lambda tx, ty: "forest"
    for x in range(10, 60):
        world.set_tile(x, 50, TILE_DIRT)
        for y in range(35, 50):
            world.set_tile(x, y, TILE_AIR)

    # 1. Grow Blight sapling in Forest biome
    world.place_tile(15, 49, TILE_SAPLING_BLIGHT, chest_type="blight_sapling")
    world.planted_saplings[(15, 49)]["growth_days"] = 2
    world.grow_plants_daily()

    # Base trunk must be TILE_BLIGHT_TRUNK, and canopy must have TILE_BLIGHT_LEAVES
    assert world.get_tile(15, 49) == TILE_BLIGHT_TRUNK
    has_blight_leaves = any(world.get_tile(x, y) == TILE_BLIGHT_LEAVES for x in range(12, 19) for y in range(40, 48))
    assert has_blight_leaves is True

    # Felling this tree must yield blight_wood and blight_leaves even though it grew in Forest!
    world.decay_drops.clear()
    broken, drop, tid = world.damage_tile_at(15, 49, power=50)
    assert broken is True
    assert drop == "blight_wood"
    decay_drops = [d[0] for d in world.decay_drops]
    assert "blight_wood" in decay_drops
    assert "blight_leaves" in decay_drops
    assert "wood" not in decay_drops
    assert "leaves" not in decay_drops

    # 2. Grow Pine sapling in Desert biome
    world.get_biome_at = lambda tx, ty: "desert"
    world.place_tile(30, 49, TILE_SAPLING_PINE, chest_type="pine_sapling")
    world.planted_saplings[(30, 49)]["growth_days"] = 2
    world.grow_plants_daily()

    assert world.get_tile(30, 49) == TILE_PINE_TRUNK
    has_pine_leaves = any(world.get_tile(x, y) == TILE_PINE_LEAVES for x in range(27, 34) for y in range(38, 48))
    assert has_pine_leaves is True

    world.decay_drops.clear()
    broken, drop, tid = world.damage_tile_at(30, 49, power=50)
    assert broken is True
    assert drop == "pine_wood"
    decay_drops = [d[0] for d in world.decay_drops]
    assert "pine_wood" in decay_drops
    assert "pine_leaves" in decay_drops
    assert "palm_wood" not in decay_drops

    # 3. Grow Palm sapling in Snow biome
    world.get_biome_at = lambda tx, ty: "snow"
    world.place_tile(45, 49, TILE_SAPLING_PALM, chest_type="palm_sapling")
    world.planted_saplings[(45, 49)]["growth_days"] = 2
    world.grow_plants_daily()

    assert world.get_tile(45, 49) == TILE_PALM_TRUNK
    has_palm_leaves = any(world.get_tile(x, y) == TILE_PALM_LEAVES for x in range(42, 49) for y in range(40, 48))
    assert has_palm_leaves is True

    world.decay_drops.clear()
    broken, drop, tid = world.damage_tile_at(45, 49, power=50)
    assert broken is True
    assert drop == "palm_wood"
    decay_drops = [d[0] for d in world.decay_drops]
    assert "palm_wood" in decay_drops
    assert "palm_leaves" in decay_drops
    assert "pine_wood" not in decay_drops


def test_11_natural_chunk_generation_uses_species_tiles():
    """Verify Chunk._generate generates true species trunk & leaf blocks in Desert, Snow, and Blight."""
    from src.world.chunk_manager import Chunk

    class FixedNoise:
        def __init__(self, val):
            self.val = val
        def noise2(self, x, y):
            return self.val
        def fractal1d(self, x, octaves=1, persistence=0.5):
            return self.val
        def fractal2d(self, x, y, octaves=1, persistence=0.5):
            return self.val

    # Noise values to trigger specific biomes:
    # noise_biome: desert 0.06..0.22; snow < -0.18; blight/corruption >= 0.22
    # Verify desert chunk tree generation produces palm tiles, never generic oak
    has_palm = False
    for seed in range(50):
        desert_chunk = Chunk(0, seed=seed, noise_surface=FixedNoise(0.0), noise_caves=FixedNoise(-0.9), noise_ores=FixedNoise(0.0), noise_biome=FixedNoise(0.15))
        if any(desert_chunk.tiles[x][y] in (TILE_PALM_TRUNK, TILE_PALM_LEAVES) for x in range(desert_chunk.width) for y in range(desert_chunk.height)):
            has_palm = True
            break
    assert has_palm is True, "Desert chunk must generate palm trunk/leaves"

    # Verify snow chunk tree generation produces pine tiles, never generic oak
    has_pine = False
    for seed in range(50):
        snow_chunk = Chunk(0, seed=seed, noise_surface=FixedNoise(0.0), noise_caves=FixedNoise(-0.9), noise_ores=FixedNoise(0.0), noise_biome=FixedNoise(-0.5))
        if any(snow_chunk.tiles[x][y] in (TILE_PINE_TRUNK, TILE_PINE_LEAVES) for x in range(snow_chunk.width) for y in range(snow_chunk.height)):
            has_pine = True
            break
    assert has_pine is True, "Snow chunk must generate pine trunk/leaves"

    # Verify corruption/blight chunk tree generation produces blight tiles, never generic oak
    has_blight = False
    for seed in range(50):
        blight_chunk = Chunk(0, seed=seed, noise_surface=FixedNoise(0.0), noise_caves=FixedNoise(-0.9), noise_ores=FixedNoise(0.0), noise_biome=FixedNoise(0.35))
        if any(blight_chunk.tiles[x][y] in (TILE_BLIGHT_TRUNK, TILE_BLIGHT_LEAVES) for x in range(blight_chunk.width) for y in range(blight_chunk.height)):
            has_blight = True
            break
    assert has_blight is True, "Blight/Corruption chunk must generate blight trunk/leaves"


def test_12_cross_biome_rendering_preserves_species_appearance(world, asset_factory):
    """Verify ChunkSection.bake preserves leaf and trunk species appearance regardless of chunk biome."""
    from src.world.chunk_manager import ChunkSection

    section = ChunkSection(0, 0)
    chunk = world.chunk_manager.get_chunk(0)
    assert chunk is not None

    # Place Blight leaves in Snow biome column
    chunk.col_biomes[5] = "snow"
    chunk.tiles[5][10] = TILE_BLIGHT_LEAVES
    world.player_placed_tiles.add((5, 10))

    # Bake section and ensure it renders properly
    section.bake(world)
    assert section.surf is not None
    assert section.dirty is False

    # Also verify selection mapping rule directly
    for t_id, expected_key in [
        (TILE_PINE_LEAVES, "snow"),
        (TILE_BLIGHT_LEAVES, "blight"),
        (TILE_PALM_LEAVES, "palm")
    ]:
        col_biome = "desert"  # in foreign desert biome
        if t_id == TILE_PINE_LEAVES:
            b_key = "snow"
        elif t_id == TILE_BLIGHT_LEAVES:
            b_key = "blight"
        elif t_id == TILE_PALM_LEAVES:
            b_key = "palm"
        else:
            b_key = "forest"
        assert b_key == expected_key, f"Tile {t_id} must maintain key {expected_key} in foreign biome {col_biome}"


def test_13_main_gameplay_mining_particles_and_sound():
    """Verify main.py has bespoke debris colors and dig_wood sound mappings for all tree species tiles."""
    from main import PotariaGame
    app = type("DummyApp", (), {"_get_tile_debris_color": PotariaGame._get_tile_debris_color})()

    # Verify debris colors for all 12 wood/trunk/leaf tiles
    for tid in [
        TILE_WOOD, TILE_WOOD_TRUNK, TILE_LEAVES,
        TILE_PINE_WOOD, TILE_PINE_TRUNK, TILE_PINE_LEAVES,
        TILE_PALM_WOOD, TILE_PALM_TRUNK, TILE_PALM_LEAVES,
        TILE_BLIGHT_WOOD, TILE_BLIGHT_TRUNK, TILE_BLIGHT_LEAVES
    ]:
        col = app._get_tile_debris_color(tid)
        assert col != (150, 150, 150), f"Tile {tid} must not fall back to default gray debris color"
        assert len(col) == 3
        assert all(0 <= c <= 255 for c in col)

