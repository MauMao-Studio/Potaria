"""
Tests for Planted Sapling Types, Visuals, Growth, and Multi-Frame Animations.
Ensures oak, palm, pine, and blight saplings have distinct tile IDs,
handcrafted multi-frame animations, proper placement, mining drops,
daily growth into corresponding mature trees, and save/load persistence.
"""

import os
import sys
import pytest
import pygame

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
os.environ["SDL_VIDEODRIVER"] = "dummy"
pygame.init()

from src.constants import (
    TILE_AIR, TILE_DIRT, TILE_GRASS, TILE_WOOD_TRUNK, TILE_LEAVES,
    TILE_SAPLING, TILE_SAPLING_OAK, TILE_SAPLING_PALM, TILE_SAPLING_PINE, TILE_SAPLING_BLIGHT,
    SAPLING_TILES, SAPLING_TILE_TO_ITEM, SAPLING_ITEM_TO_TILE, TILE_PROPS
)
from src.world.tiles import is_sapling_tile, get_sapling_item, get_sapling_tile
from src.ui.inventory import ITEM_REGISTRY, FRAGILE_TILES
from src.assets.asset_factory import AssetFactory
from src.world.world import World
from src.world.save_manager import save_world, load_world, delete_world
from src.rpg.stats import PlayerStats


def test_sapling_tile_constants_and_helpers():
    """Verify distinct sapling tile IDs, collections, and helper functions."""
    assert TILE_SAPLING == 54
    assert TILE_SAPLING_OAK == 54
    assert TILE_SAPLING_PALM == 62
    assert TILE_SAPLING_PINE == 63
    assert TILE_SAPLING_BLIGHT == 64

    assert set(SAPLING_TILES) == {54, 62, 63, 64}
    assert set(SAPLING_TILE_TO_ITEM.keys()) == {54, 62, 63, 64}
    assert set(SAPLING_ITEM_TO_TILE.values()) == {54, 62, 63, 64}

    for tid in SAPLING_TILES:
        assert is_sapling_tile(tid) is True
        item_id = get_sapling_item(tid)
        assert item_id in ITEM_REGISTRY
        assert get_sapling_tile(item_id) == tid

    assert is_sapling_tile(TILE_DIRT) is False
    assert get_sapling_item(TILE_DIRT) is None
    assert get_sapling_tile("non_existent_item") is None

    # Fragile and non-solid properties
    for tid in SAPLING_TILES:
        props = TILE_PROPS.get(tid, {})
        assert props.get("solid", False) is False, f"Sapling {tid} must not be solid"
        assert tid in FRAGILE_TILES, f"Sapling {tid} must be in FRAGILE_TILES"

    # Blight sapling light emission
    blight_props = TILE_PROPS.get(TILE_SAPLING_BLIGHT, {})
    assert blight_props.get("light_emit", 0) > 0, "Blight sapling must emit light"
    assert blight_props.get("light_radius", 0) > 0, "Blight sapling must have light radius"


def test_sapling_items_in_registry():
    """Verify item registry mappings for all sapling types."""
    sapling_pairs = [
        ("oak_sapling", TILE_SAPLING_OAK),
        ("palm_sapling", TILE_SAPLING_PALM),
        ("pine_sapling", TILE_SAPLING_PINE),
        ("blight_sapling", TILE_SAPLING_BLIGHT),
    ]
    for item_id, expected_tid in sapling_pairs:
        assert item_id in ITEM_REGISTRY, f"Missing {item_id} in ITEM_REGISTRY"
        data = ITEM_REGISTRY[item_id]
        assert data.get("tile") == expected_tid, f"Expected {item_id} tile to be {expected_tid}, got {data.get('tile')}"


def test_sapling_animations_and_uniqueness():
    """Verify AssetFactory creates distinct 4-frame animations for all saplings."""
    af = AssetFactory()

    assert hasattr(af, "sapling_oak_frames")
    assert hasattr(af, "sapling_palm_frames")
    assert hasattr(af, "sapling_pine_frames")
    assert hasattr(af, "sapling_blight_frames")
    assert hasattr(af, "sapling_type_frames")

    frame_collections = {
        "oak": af.sapling_oak_frames,
        "palm": af.sapling_palm_frames,
        "pine": af.sapling_pine_frames,
        "blight": af.sapling_blight_frames,
    }

    all_frame_bytes = set()
    for s_type, frames in frame_collections.items():
        assert len(frames) == 4, f"{s_type} sapling must have exactly 4 frames"
        for i, frame in enumerate(frames):
            assert isinstance(frame, pygame.Surface)
            assert frame.get_size() == (16, 16)
            b = pygame.image.tobytes(frame, "RGBA")
            assert b not in all_frame_bytes, f"Duplicate frame detected in {s_type} frame {i}"
            all_frame_bytes.add(b)
            # Ensure frame has non-trivial visible content
            opaque_count = sum(1 for x in range(16) for y in range(16) if frame.get_at((x, y))[3] > 0)
            assert opaque_count >= 8, f"{s_type} frame {i} has too few opaque pixels ({opaque_count})"

    assert len(all_frame_bytes) == 16, "All 16 sapling animation frames must be visually distinct"

    # Verify tile mapping in AssetFactory
    for tid in (TILE_SAPLING_OAK, TILE_SAPLING_PALM, TILE_SAPLING_PINE, TILE_SAPLING_BLIGHT):
        assert tid in af.sapling_type_frames
        assert tid in af.tiles


def test_sapling_placement_and_tile_resolution():
    """Verify placing sapling items sets the exact distinct tile ID and records planted_saplings."""
    af = AssetFactory()
    world = World(af, seed=12345)

    # Prepare ground at y=25
    for x in range(10, 20):
        world.set_tile(x, 25, TILE_DIRT)
        world.set_tile(x, 24, TILE_AIR)

    # 1. Place oak sapling
    success_oak = world.place_tile(10, 24, TILE_SAPLING_OAK, chest_type="oak_sapling")
    assert success_oak is True
    assert world.get_tile(10, 24) == TILE_SAPLING_OAK
    assert (10, 24) in world.planted_saplings
    assert world.planted_saplings[(10, 24)]["sapling_type"] == "oak_sapling"

    # 2. Place palm sapling
    success_palm = world.place_tile(12, 24, TILE_SAPLING_PALM, chest_type="palm_sapling")
    assert success_palm is True
    assert world.get_tile(12, 24) == TILE_SAPLING_PALM
    assert (12, 24) in world.planted_saplings
    assert world.planted_saplings[(12, 24)]["sapling_type"] == "palm_sapling"

    # 3. Place pine sapling
    success_pine = world.place_tile(14, 24, TILE_SAPLING_PINE, chest_type="pine_sapling")
    assert success_pine is True
    assert world.get_tile(14, 24) == TILE_SAPLING_PINE
    assert (14, 24) in world.planted_saplings
    assert world.planted_saplings[(14, 24)]["sapling_type"] == "pine_sapling"

    # 4. Place blight sapling
    success_blight = world.place_tile(16, 24, TILE_SAPLING_BLIGHT, chest_type="blight_sapling")
    assert success_blight is True
    assert world.get_tile(16, 24) == TILE_SAPLING_BLIGHT
    assert (16, 24) in world.planted_saplings
    assert world.planted_saplings[(16, 24)]["sapling_type"] == "blight_sapling"

    # 5. Placing in air without ground below must fail
    success_air = world.place_tile(18, 10, TILE_SAPLING_OAK, chest_type="oak_sapling")
    assert success_air is False


def test_sapling_mining_and_drop():
    """Verify mining/destroying placed saplings drops the matching sapling item."""
    af = AssetFactory()
    world = World(af, seed=12345)

    # Setup supporting ground
    world.set_tile(10, 20, TILE_DIRT)
    world.set_tile(11, 20, TILE_DIRT)
    world.set_tile(12, 20, TILE_DIRT)
    world.set_tile(13, 20, TILE_DIRT)

    # Place one of each
    world.place_tile(10, 19, TILE_SAPLING_OAK, chest_type="oak_sapling")
    world.place_tile(11, 19, TILE_SAPLING_PALM, chest_type="palm_sapling")
    world.place_tile(12, 19, TILE_SAPLING_PINE, chest_type="pine_sapling")
    world.place_tile(13, 19, TILE_SAPLING_BLIGHT, chest_type="blight_sapling")

    # Destroy oak sapling
    broken, drop, tid = world.damage_tile_at(10, 19, 100)
    assert broken is True
    assert drop == "oak_sapling"
    assert world.get_tile(10, 19) == TILE_AIR
    assert (10, 19) not in world.planted_saplings

    # Destroy palm sapling
    broken, drop, tid = world.damage_tile_at(11, 19, 100)
    assert broken is True
    assert drop == "palm_sapling"
    assert world.get_tile(11, 19) == TILE_AIR
    assert (11, 19) not in world.planted_saplings

    # Destroy pine sapling
    broken, drop, tid = world.damage_tile_at(12, 19, 100)
    assert broken is True
    assert drop == "pine_sapling"
    assert world.get_tile(12, 19) == TILE_AIR
    assert (12, 19) not in world.planted_saplings

    # Destroy blight sapling
    broken, drop, tid = world.damage_tile_at(13, 19, 100)
    assert broken is True
    assert drop == "blight_sapling"
    assert world.get_tile(13, 19) == TILE_AIR
    assert (13, 19) not in world.planted_saplings


def test_sapling_daily_growth():
    """Verify grow_plants_daily grows mature trees for each sapling type."""
    af = AssetFactory()
    world = World(af, seed=12345)

    # Prepare ground with plenty of room above
    for x in range(10, 50):
        for y in range(30, 40):
            world.set_tile(x, y, TILE_DIRT)
        for y in range(0, 30):
            world.set_tile(x, y, TILE_AIR)

    # Place an oak sapling at (15, 29)
    world.place_tile(15, 29, TILE_SAPLING_OAK, chest_type="oak_sapling")
    # Place a pine sapling at (25, 29)
    world.place_tile(25, 29, TILE_SAPLING_PINE, chest_type="pine_sapling")
    # Place a blight sapling at (35, 29)
    world.place_tile(35, 29, TILE_SAPLING_BLIGHT, chest_type="blight_sapling")

    # Fast forward growth days to trigger mature tree generation
    world.planted_saplings[(15, 29)]["growth_days"] = 3
    world.planted_saplings[(25, 29)]["growth_days"] = 3
    world.planted_saplings[(35, 29)]["growth_days"] = 3

    world.grow_plants_daily()

    # Oak should have grown into tree trunk / leaves
    assert world.get_tile(15, 29) != TILE_SAPLING_OAK
    assert (15, 29) not in world.planted_saplings
    # Trunk tiles should exist around (15, 29) and above
    assert world.get_tile(15, 29) in (TILE_WOOD_TRUNK, TILE_LEAVES) or world.get_tile(15, 28) == TILE_WOOD_TRUNK

    # Pine should have grown
    assert world.get_tile(25, 29) != TILE_SAPLING_PINE
    assert (25, 29) not in world.planted_saplings

    # Blight should have grown into twisted nether blight tree
    assert world.get_tile(35, 29) != TILE_SAPLING_BLIGHT
    assert (35, 29) not in world.planted_saplings


def test_save_load_and_legacy_sapling_upgrade():
    """Verify world saving/loading preserves sapling types and upgrades legacy saplings."""
    af = AssetFactory()

    class MockInventory:
        def __init__(self):
            self.slots = [None] * 40
            self.coin_purse = {"copper": 0, "silver": 0, "gold": 0, "platinum": 0}
        def migrate_coins(self):
            pass

    class MockPlayer:
        def __init__(self):
            self.x = 100.0
            self.y = 200.0
            self.vx = 0.0
            self.vy = 0.0
            self.spawn_point = (100, 200)
            self.stats = PlayerStats()
            self.skills = type("MockSkills", (), {
                "learned_skills": [],
                "skill_levels": {},
                "hotkey_bindings": {},
                "hotkey_slots": {}
            })()
            self.equipment = type("MockEquip", (), {
                "slots": {"head": None, "chest": None, "legs": None, "weapon": None, "accessory": None},
                "active_weapon_id": None,
                "recalculate_stats": lambda self, st: None
            })()
        @property
        def center_x(self):
            return self.x + 16.0
        @property
        def center_y(self):
            return self.y + 16.0

    class MockGame:
        def __init__(self, world, world_name="TestWorld_Sapling"):
            self.world = world
            self.asset_factory = af
            self.active_world_name = world_name
            self.world_type = "infinite"
            self.difficulty = "normal"
            self.game_mode = "adventure"
            self.playtime = 10.0
            self.block_deltas = {}
            self.wall_deltas = {}
            self.inventory = MockInventory()
            self.player = MockPlayer()
            self.camera = None
            self.combat = type("MockCombat", (), {
                "boss": None,
                "boss_defeated": False,
                "grand_boss_defeated": False,
                "dungeon_boss_slain": False,
                "mini_bosses_slain": 0,
                "alive_mobs": [],
                "dropped_items": []
            })()

    world = World(af, seed=12345)
    for x in range(10, 20):
        world.set_tile(x, 25, TILE_DIRT)
        world.set_tile(x, 24, TILE_AIR)

    world.place_tile(10, 24, TILE_SAPLING_PALM, chest_type="palm_sapling")
    world.place_tile(12, 24, TILE_SAPLING_BLIGHT, chest_type="blight_sapling")

    # Manually simulate a legacy world where tile ID is 54 (TILE_SAPLING) but type is pine_sapling
    world.set_tile(14, 24, TILE_SAPLING)
    world.planted_saplings[(14, 24)] = {"growth_days": 1, "sapling_type": "pine_sapling"}

    save_name = "test_sapling_save_roundtrip"
    mock_game = MockGame(world, world_name=save_name)
    for x in range(10, 20):
        mock_game.block_deltas[(x, 25)] = TILE_DIRT
    mock_game.block_deltas[(10, 24)] = TILE_SAPLING_PALM
    mock_game.block_deltas[(12, 24)] = TILE_SAPLING_BLIGHT
    mock_game.block_deltas[(14, 24)] = TILE_SAPLING
    save_world(save_name, mock_game)

    # Create new world and load
    new_world = World(af, seed=12345)
    new_game = MockGame(new_world, world_name=save_name)
    load_success = load_world(save_name, new_game)
    assert load_success is True

    # Check preserved palm and blight
    assert new_game.world.get_tile(10, 24) == TILE_SAPLING_PALM
    assert new_game.world.planted_saplings[(10, 24)]["sapling_type"] == "palm_sapling"

    assert new_game.world.get_tile(12, 24) == TILE_SAPLING_BLIGHT
    assert new_game.world.planted_saplings[(12, 24)]["sapling_type"] == "blight_sapling"

    # Check legacy pine sapling was upgraded from 54 to TILE_SAPLING_PINE (63)
    assert new_game.world.get_tile(14, 24) == TILE_SAPLING_PINE
    assert new_game.world.planted_saplings[(14, 24)]["sapling_type"] == "pine_sapling"

    # Cleanup save
    delete_world(save_name)


def test_sapling_multiplayer_block_deltas():
    """Verify multiplayer pending block deltas register and unregister saplings correctly."""
    af = AssetFactory()
    world = World(af, seed=12345)

    class MockClient:
        def __init__(self):
            self.pending_block_deltas = [
                {"tx": 5, "ty": 10, "tile_id": TILE_SAPLING_BLIGHT},
                {"tx": 6, "ty": 10, "tile_id": TILE_SAPLING_PALM},
            ]

    client = MockClient()
    block_deltas = {}

    # Simulate multiplayer delta processing loop from main.py
    while getattr(client, "pending_block_deltas", None):
        delta = client.pending_block_deltas.pop(0)
        tx, ty, tid = delta.get("tx"), delta.get("ty"), delta.get("tile_id")
        if tx is not None and ty is not None:
            world.set_tile(tx, ty, tid)
            block_deltas[(tx, ty)] = tid
            if hasattr(world, "planted_saplings"):
                if tid in SAPLING_TILES:
                    sap_type = SAPLING_TILE_TO_ITEM.get(tid, "oak_sapling")
                    world.planted_saplings[(tx, ty)] = {"growth_days": 0, "sapling_type": sap_type}
                else:
                    world.planted_saplings.pop((tx, ty), None)

    assert world.get_tile(5, 10) == TILE_SAPLING_BLIGHT
    assert (5, 10) in world.planted_saplings
    assert world.planted_saplings[(5, 10)]["sapling_type"] == "blight_sapling"

    assert world.get_tile(6, 10) == TILE_SAPLING_PALM
    assert (6, 10) in world.planted_saplings
    assert world.planted_saplings[(6, 10)]["sapling_type"] == "palm_sapling"

    # Now simulate destroying the blight sapling remotely
    client.pending_block_deltas.append({"tx": 5, "ty": 10, "tile_id": TILE_AIR})
    while getattr(client, "pending_block_deltas", None):
        delta = client.pending_block_deltas.pop(0)
        tx, ty, tid = delta.get("tx"), delta.get("ty"), delta.get("tile_id")
        if tx is not None and ty is not None:
            world.set_tile(tx, ty, tid)
            block_deltas[(tx, ty)] = tid
            if hasattr(world, "planted_saplings"):
                if tid in SAPLING_TILES:
                    sap_type = SAPLING_TILE_TO_ITEM.get(tid, "oak_sapling")
                    world.planted_saplings[(tx, ty)] = {"growth_days": 0, "sapling_type": sap_type}
                else:
                    world.planted_saplings.pop((tx, ty), None)

    assert world.get_tile(5, 10) == TILE_AIR
    assert (5, 10) not in world.planted_saplings

