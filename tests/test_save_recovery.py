"""
Unit and integration tests for Potaria's multi-tier save corruption prevention
and self-healing recovery pipeline:
1. Atomic File Writes (os.fsync + os.replace)
2. Automated Backup Rotation (.bak & rolling historical snapshots)
3. Snapshot Auto-Pruning (keep at most max_backups)
4. Self-Healing Recovery on Load (.bak fallback and historical snapshot fallback)
5. HMAC Signature Verification & Tamper Detection
"""

import os
import sys
import json
import time
import shutil
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.world.save_manager import (
    atomic_write_json,
    verify_save_data,
    verify_save_file,
    prune_backup_snapshots,
    list_world_backups,
    create_backup_snapshot,
    save_world,
    load_world,
    get_world_dir,
    get_world_file,
    get_backup_file,
    get_backups_dir,
    MAX_BACKUP_SNAPSHOTS,
    RESTORE_NOTIFICATION_MSG
)
from src.assets.asset_factory import AssetFactory
from src.rpg.stats import PlayerStats


class MockInventory:
    def __init__(self):
        self.slots = [None] * 40
        self.held_item = None
        self.coin_purse = {"copper": 0, "silver": 0, "gold": 0, "platinum": 0}
        self.messages = []

    def notify(self, msg):
        self.messages.append(msg)

    def migrate_coins(self):
        pass


class MockHUD:
    def __init__(self):
        self.local_chat_history = []

    def add_chat_message(self, sender, msg):
        self.local_chat_history.append((sender, msg))


class MockPlayer:
    def __init__(self):
        self.x = 100.0
        self.y = 200.0
        self.vx = 0.0
        self.vy = 0.0
        self.spawn_point = (100, 200)
        self.health = 100
        self.max_health = 100
        self.facing_right = True
        self.stats = PlayerStats()
        self.skills = type("MockSkills", (), {
            "learned_skills": ["swift_dash"],
            "skill_levels": {"swift_dash": 2},
            "hotkey_bindings": {"Q": "swift_dash"},
            "hotkey_slots": {"Q": "swift_dash"}
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
    def __init__(self, world_name="TestWorld_Recovery"):
        self.active_world_name = world_name
        self.world_type = "infinite"
        self.difficulty = "normal"
        self.game_mode = "adventure"
        self.playtime = 120.0
        self.block_deltas = {(10, 20): 1, (10, 21): 2}
        self.wall_deltas = {(10, 20): 3}

        # Subsystems
        self.asset_factory = AssetFactory()
        self.inventory = MockInventory()
        self.hud = MockHUD()
        self.world = type("MockWorld", (), {
            "seed": 99999,
            "spawn_point": (100, 200),
            "sky_theme": "normal",
            "time_of_day": 0.5,
            "world_type": "infinite",
            "width": 1000,
            "height": 500,
            "chests": {},
            "decaying_blocks": {},
            "planted_saplings": {},
            "town_npcs": [],
            "set_tile": lambda self, x, y, tid: None,
            "set_wall": lambda self, x, y, wid: None,
            "chunk_manager": type("MockChunkMgr", (), {
                "ensure_chunks_in_range": lambda self, a, b: None,
                "set_world_name": lambda self, name: None
            })()
        })()
        self.player = MockPlayer()
        self.combat = type("MockCombat", (), {
            "boss": None,
            "boss_defeated": False,
            "grand_boss_defeated": False,
            "dungeon_boss_slain": False,
            "mini_bosses_slain": 0,
            "defeated_mini_bosses": {},
            "mobs": [],
            "projectiles": [],
            "enemy_projectiles": [],
            "dropped_items": [],
            "damage_numbers": []
        })()


@pytest.fixture
def clean_test_world():
    test_world = "TestWorld_AutoRecovery_Unit"
    wdir = get_world_dir(test_world)
    if os.path.exists(wdir):
        shutil.rmtree(wdir, ignore_errors=True)
    yield test_world
    if os.path.exists(wdir):
        shutil.rmtree(wdir, ignore_errors=True)


def test_atomic_write_json(clean_test_world):
    """Test 1: atomic_write_json writes to .tmp, fsyncs, and replaces atomically."""
    target = os.path.join(get_world_dir(clean_test_world), "test_file.json")
    payload = {"status": "ok", "value": 42, "items": ["potato", "torch"]}

    atomic_write_json(target, payload)

    assert os.path.exists(target), "Target file should exist"
    assert not os.path.exists(target + ".tmp"), "Temp file should be atomically replaced"

    with open(target, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert data == payload

    # Test atomic overwrite
    updated_payload = {"status": "updated", "value": 100}
    atomic_write_json(target, updated_payload)
    with open(target, "r", encoding="utf-8") as f:
        assert json.load(f) == updated_payload


def test_save_creates_bak_file(clean_test_world):
    """Test 2: Saving an existing world creates world.json.bak before replacement."""
    game = MockGame(clean_test_world)
    save_path = get_world_file(clean_test_world)
    bak_path = get_backup_file(clean_test_world)

    # Initial save
    save_world(clean_test_world, game)
    assert os.path.exists(save_path)
    # On first save, no previous world.json existed to back up
    assert not os.path.exists(bak_path)

    # Modify game state and save again
    game.playtime = 300.0
    save_world(clean_test_world, game)

    # .bak file must now exist and contain initial state (playtime == 120.0)
    assert os.path.exists(bak_path), "Immediate .bak file must exist after second save"
    with open(bak_path, "r", encoding="utf-8") as f:
        bak_data = json.load(f)
    assert bak_data.get("playtime") == 120.0

    # Primary save must contain current state (playtime == 300.0)
    with open(save_path, "r", encoding="utf-8") as f:
        prim_data = json.load(f)
    assert prim_data.get("playtime") == 300.0


def test_historical_snapshot_creation_and_pruning(clean_test_world):
    """Test 3: Historical snapshots are created in backups/ and auto-pruned to max_backups."""
    game = MockGame(clean_test_world)
    save_world(clean_test_world, game)

    backups_dir = get_backups_dir(clean_test_world)
    max_b = 3

    # Generate 5 snapshots
    for i in range(5):
        payload = {"world_name": clean_test_world, "seed": 99999, "snap_idx": i}
        create_backup_snapshot(clean_test_world, payload=payload, reason=f"Snap #{i}", max_backups=max_b)
        time.sleep(0.02)  # Ensure unique file timestamp or mtime

    backups = list_world_backups(clean_test_world)
    assert len(backups) == max_b, f"Backups should be pruned to {max_b}, got {len(backups)}"

    # The newest snapshot should have snap_idx == 4
    with open(backups[0], "r", encoding="utf-8") as f:
        newest = json.load(f)
    assert newest.get("snap_idx") == 4


def test_self_healing_from_bak_fallback(clean_test_world):
    """Test 4: Corrupt or truncated primary world.json self-heals from world.json.bak."""
    game = MockGame(clean_test_world)
    save_path = get_world_file(clean_test_world)
    bak_path = get_backup_file(clean_test_world)

    # 1. Create initial save and second save to produce a valid .bak
    game.playtime = 150.0
    save_world(clean_test_world, game)
    game.playtime = 250.0
    save_world(clean_test_world, game)

    assert os.path.exists(save_path)
    assert os.path.exists(bak_path)

    # 2. Simulate abnormal shutdown truncation: world.json truncated to 0 bytes
    with open(save_path, "w", encoding="utf-8") as f:
        f.truncate(0)

    # 3. Load world -> should automatically heal from .bak
    load_game = MockGame(clean_test_world)
    success = load_world(clean_test_world, load_game)

    assert success is True, "Load should succeed via .bak fallback"
    assert getattr(load_game, "world_restored_from_backup", False) is True
    assert RESTORE_NOTIFICATION_MSG in getattr(load_game, "restore_message", "")
    assert getattr(load_game, "restored_backup_path") == bak_path

    # Primary world.json should be repaired on disk
    with open(save_path, "r", encoding="utf-8") as f:
        repaired_data = json.load(f)
    assert repaired_data.get("playtime") == 150.0


def test_self_healing_from_historical_snapshot(clean_test_world):
    """Test 5: Corrupt primary AND corrupt .bak self-heals from historical snapshot."""
    game = MockGame(clean_test_world)
    save_path = get_world_file(clean_test_world)
    bak_path = get_backup_file(clean_test_world)

    # 1. Save game and create a valid historical snapshot
    game.playtime = 500.0
    save_world(clean_test_world, game, create_snapshot=True, reason="Boss Milestone")

    # 2. Corrupt both world.json and world.json.bak with garbage syntax
    with open(save_path, "w", encoding="utf-8") as f:
        f.write('{"unclosed_json": true, "corrupt_data": [')

    if os.path.exists(bak_path):
        with open(bak_path, "w", encoding="utf-8") as f:
            f.truncate(0)
    else:
        # Create a corrupt .bak
        with open(bak_path, "w", encoding="utf-8") as f:
            f.write("corrupted bytes")

    # 3. Load world -> should fall back to snapshot in backups/
    load_game = MockGame(clean_test_world)
    success = load_world(clean_test_world, load_game)

    assert success is True, "Load should succeed via historical snapshot fallback"
    assert getattr(load_game, "world_restored_from_backup", False) is True
    assert "backups" in getattr(load_game, "restored_backup_path", "")

    # Primary world.json is repaired with snapshot data
    with open(save_path, "r", encoding="utf-8") as f:
        repaired = json.load(f)
    assert repaired.get("playtime") == 500.0


def test_hmac_tamper_fallback(clean_test_world):
    """Test 6: HMAC signature mismatch falls back to untampered backup if available."""
    game = MockGame(clean_test_world)
    save_path = get_world_file(clean_test_world)
    bak_path = get_backup_file(clean_test_world)

    # Save initial version
    game.playtime = 100.0
    save_world(clean_test_world, game)

    # Save second version to populate .bak
    game.playtime = 200.0
    save_world(clean_test_world, game)

    # Tamper with world.json (change playtime without updating HMAC signature)
    with open(save_path, "r", encoding="utf-8") as f:
        tampered_data = json.load(f)
    tampered_data["playtime"] = 999999.0  # modified
    with open(save_path, "w", encoding="utf-8") as f:
        json.dump(tampered_data, f, indent=2)

    # Load world -> should detect HMAC mismatch on primary and fall back to untampered .bak
    load_game = MockGame(clean_test_world)
    success = load_world(clean_test_world, load_game)

    assert success is True
    assert getattr(load_game, "world_restored_from_backup", False) is True
    assert getattr(load_game, "restored_backup_path") == bak_path
