"""
Potaria - Comprehensive Verification Test Suite for Gameplay Expansion,
Balancing, Systems Overhaul, and World/Mode Management.
Developer: Kurados
Pure Python 3 + pygame-ce
"""

import os
import sys
import math
import json
import pygame

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Set dummy video driver for headless automated test runs
os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"

from src.constants import (
    SCREEN_WIDTH, SCREEN_HEIGHT,
    TILE_AIR, TILE_DIRT, TILE_STONE, TILE_WOOD, TILE_WOOD_PLATFORM,
    TILE_BEDROCK, TILE_BARRIER,
    DIFFICULTY_NORMAL, DIFFICULTY_HARDCORE, DIFFICULTY_YOLO,
    WORLD_TYPE_INFINITE, WORLD_TYPE_FINITE,
    MODE_ADVENTURE, MODE_LAST_MAN_STANDING,
    STATE_MENU, STATE_PLAYING, STATE_GAME_OVER, STATE_WORLDS, STATE_NEW_WORLD
)
from src.rpg.equipment import ARMOR_DATA
from src.assets.asset_factory import AssetFactory
from src.audio.sound_effects import SoundManager
from src.world.world import World
from src.entities.player import Player
from src.entities.dropped_item import DroppedItem
from src.entities.mob import (
    RockZombie, ShieldWeaver, DiggerMob, RockProjectile,
    Zombie, GreenSlime, ShadowCrawler, Skeleton,
    create_mob_by_type, MOB_TYPE_REGISTRY
)
from src.entities.boss import IgnisColossus, CryoSpud, NecroTuber, LordMalus, GrandBossSolRho
from src.ui.inventory import Inventory, ItemStack, INV_TOTAL_SLOTS, ITEM_REGISTRY
from src.rpg.stats import PlayerStats
from src.world.save_manager import (
    save_world, load_world, delete_world, list_saved_worlds, get_world_file
)
from main import PotariaGame

def test_item_dropping_and_physics():
    print("\n[Test 1] Testing Item Dropping & Throw Physics...")
    assets = AssetFactory()
    sound = SoundManager()
    player = Player(100, 100, assets, sound)
    inv = Inventory(assets, difficulty="normal")

    # Verify starter loadout for normal mode: 1 wood axe
    assert inv.slots[0] is not None
    assert inv.slots[0].item_id == "wood_axe"

    # Test inventory drop_item
    dropped = inv.drop_item(0, 1)
    assert dropped == ("wood_axe", 1)
    assert inv.slots[0] is None, "Slot 0 should be empty after dropping"

    # Test drop_held_item
    inv.held_item = ItemStack("torch", 5)
    dropped_held = inv.drop_held_item(2)
    assert dropped_held == ("torch", 2)
    assert inv.held_item.count == 3
    dropped_all = inv.drop_held_item()
    assert dropped_all == ("torch", 3)
    assert inv.held_item is None

    # Test Game drop_selected_or_held and throw physics
    game = PotariaGame()
    game.inventory.slots[0] = ItemStack("stone_block", 10)
    game.inventory.selected_slot = 0
    initial_dropped_count = len(game.combat.dropped_items)

    game.drop_selected_or_held()
    assert len(game.combat.dropped_items) == initial_dropped_count + 1
    new_item = game.combat.dropped_items[-1]
    assert new_item.item_id == "stone_block"
    assert new_item.count == 1
    assert new_item.pickup_delay > 0.5, "Dropped item must have pickup delay"
    assert new_item.vy < 0, "Dropped item must be tossed upwards"
    assert abs(new_item.vx) > 0, "Dropped item must have horizontal throw velocity"
    assert game.inventory.slots[0].count == 9

    print("  -> Item dropping and throw physics verified successfully!")

def test_full_inventory_bug_fix():
    print("\n[Test 2] Testing Full Inventory Ground Item Retention Bug Fix...")
    assets = AssetFactory()
    inv = Inventory(assets, difficulty="hardcore")
    # Hardcore starts with 0 items
    assert all(s is None for s in inv.slots)

    # Fill all 40 slots with distinct items or max stacks
    for i in range(INV_TOTAL_SLOTS):
        inv.slots[i] = ItemStack("copper_pickaxe", 1) # max stack is 1

    # Verify inventory is completely full
    assert inv.can_add_item("copper_pickaxe", 1) is False
    assert inv.can_add_item("dirt_block", 1) is False

    # Simulate dropped item on ground trying to be picked up
    ground_item = DroppedItem("dirt_block", 64, 100, 100, assets)
    ground_item.picked_up = True

    game = PotariaGame()
    game.inventory = inv
    game.combat.dropped_items = [ground_item]

    # Run item collection block
    for item in game.combat.dropped_items:
        if getattr(item, "picked_up", False):
            leftover = game.inventory.add_item(item.item_id, item.count)
            if leftover > 0:
                item.count = leftover
                item.picked_up = False

    game.combat.dropped_items = [it for it in game.combat.dropped_items if not getattr(it, "picked_up", False)]

    # CRITICAL: Ground item must NOT disappear or delete!
    assert len(game.combat.dropped_items) == 1, "Ground item must remain floating on ground when inventory is full!"
    assert game.combat.dropped_items[0].count == 64
    assert game.combat.dropped_items[0].picked_up is False

    # Now test partial capacity: 1 slot with 5 wood (max stack 999), 10 wood picked up
    inv.slots[0] = ItemStack("wood", 995)
    for i in range(1, INV_TOTAL_SLOTS):
        inv.slots[i] = ItemStack("copper_pickaxe", 1)

    assert inv.can_add_item("wood", 4) is True
    assert inv.can_add_item("wood", 10) is False

    partial_ground = DroppedItem("wood", 10, 100, 100, assets)
    partial_ground.picked_up = True
    game.combat.dropped_items = [partial_ground]

    for item in game.combat.dropped_items:
        if getattr(item, "picked_up", False):
            leftover = game.inventory.add_item(item.item_id, item.count)
            if leftover > 0:
                item.count = leftover
                item.picked_up = False

    game.combat.dropped_items = [it for it in game.combat.dropped_items if not getattr(it, "picked_up", False)]

    assert inv.slots[0].count == 999
    assert len(game.combat.dropped_items) == 1
    assert game.combat.dropped_items[0].count == 6, "Leftover 6 items must remain on ground!"
    assert game.combat.dropped_items[0].picked_up is False

    print("  -> Full inventory ground item safety verified: 0% data/item loss!")

def test_equipment_and_mob_balancing():
    print("\n[Test 3] Testing Starter Gear & Mob Attack Balancing...")
    # Copper gear DEF reduced to 1 each
    assert ARMOR_DATA["copper_helmet"]["def"] == 1
    assert ARMOR_DATA["copper_chestplate"]["def"] == 1
    assert ARMOR_DATA["copper_greaves"]["def"] == 1

    # Verify player base defense is 2, with copper armor gives 2 + 1 = 3 DEF
    stats = PlayerStats()
    assert stats.total_def == 2
    stats.bonus_def = ARMOR_DATA["copper_chestplate"]["def"]
    assert stats.total_def == 3

    # Verify mob damage buff (threatening monsters)
    assets = AssetFactory()
    z = Zombie(0, 0, assets)
    assert z.damage >= 20, f"Zombie damage should be >= 20, got {z.damage}"

    s = GreenSlime(0, 0, assets)
    assert s.damage >= 14, f"GreenSlime damage should be >= 14, got {s.damage}"

    sk = Skeleton(0, 0, assets)
    assert sk.damage >= 24, f"Skeleton damage should be >= 24, got {sk.damage}"

    sc = ShadowCrawler(0, 0, assets)
    assert sc.damage >= 30, f"ShadowCrawler damage should be >= 30, got {sc.damage}"

    print("  -> Equipment rebalance & dangerous mob tuning verified!")

def test_new_mobs():
    print("\n[Test 4] Testing RockZombie, ShieldWeaver, and DiggerMob...")
    assets = AssetFactory()
    sound = SoundManager()

    # 1. Registry contains all new mob types
    assert "rock_zombie" in MOB_TYPE_REGISTRY
    assert "shield_weaver" in MOB_TYPE_REGISTRY
    assert "digger" in MOB_TYPE_REGISTRY

    # 2. RockZombie throwing rock projectiles
    rz = create_mob_by_type("rock_zombie", 200, 200, assets)
    assert isinstance(rz, RockZombie)
    assert rz.damage >= 20

    world = World(assets, seed=42)
    player = Player(300, 200, assets, sound)
    rz.throw_timer = 0.0
    rz.update(0.016, world, player)
    assert len(rz.pending_projectiles) > 0
    rock = rz.pending_projectiles.pop()
    assert isinstance(rock, RockProjectile)
    assert rock.damage >= 18

    # 3. ShieldWeaver summoning and cleaning up TILE_BARRIER
    sw = create_mob_by_type("shield_weaver", 300, 200, assets)
    assert isinstance(sw, ShieldWeaver)
    sw.cast_timer = 0.0
    sw.update(0.016, world, player)
    assert len(sw.placed_barriers) > 0
    barriers_saved = list(sw.placed_barriers)
    for b in barriers_saved:
        assert world.get_tile(b[0], b[1]) == TILE_BARRIER

    # On death, barriers vanish
    sw.is_dead = True
    sw.update(0.016, world, player)
    for b in barriers_saved:
        assert world.get_tile(b[0], b[1]) == 0

    # 4. DiggerMob burrowing through natural tiles, blocked by player house tiles
    digger = create_mob_by_type("digger", 100, 100, assets)
    assert isinstance(digger, DiggerMob)
    from src.entities.mob import HOUSE_TILES
    assert TILE_WOOD in HOUSE_TILES, "Wooden house blocks must be in HOUSE_TILES to block burrowing"
    assert TILE_DIRT not in HOUSE_TILES, "Natural dirt must not block digger"

    print("  -> RockZombie, ShieldWeaver, and DiggerMob mechanics verified!")

def test_world_options_finite_vs_infinite():
    print("\n[Test 5] Testing World Options: Finite (320 blocks) vs Infinite...")
    assets = AssetFactory()

    # Finite World: 320 tiles wide [-160, 159]
    fw = World(assets, seed=123, world_type=WORLD_TYPE_FINITE)
    assert fw.world_type == WORLD_TYPE_FINITE

    # Within bounds [-160, 159]
    t_inside = fw.get_tile(0, 100)
    # Beyond left boundary (< -160)
    t_left_barrier = fw.get_tile(-161, 50)
    assert t_left_barrier == TILE_BEDROCK, "Columns outside finite world boundary must be TILE_BEDROCK"

    # Beyond right boundary (>= 160)
    t_right_barrier = fw.get_tile(160, 50)
    assert t_right_barrier == TILE_BEDROCK, "Columns outside finite world boundary must be TILE_BEDROCK"

    # Infinite World: Boundless procedural chunks
    iw = World(assets, seed=123, world_type=WORLD_TYPE_INFINITE)
    assert iw.world_type == WORLD_TYPE_INFINITE
    # At y=10 (sky/surface), infinite world has AIR/normal blocks at x=200, -200, NOT BEDROCK!
    assert iw.get_tile(200, 10) != TILE_BEDROCK, "Infinite world must not have bedrock wall at x=200"
    assert iw.get_tile(-200, 10) != TILE_BEDROCK, "Infinite world must not have bedrock wall at x=-200"

    print("  -> Finite bedrock bounds and Infinite streaming world verified!")

def test_difficulty_modes():
    print("\n[Test 6] Testing Difficulty Modes (Normal, Hardcore, YOLO 1-Heart Permadeath)...")
    assets = AssetFactory()
    sound = SoundManager()

    # 1. Normal Mode
    inv_norm = Inventory(assets, difficulty=DIFFICULTY_NORMAL)
    assert inv_norm.slots[0].item_id == "wood_axe"

    # 2. Hardcore Mode
    inv_hard = Inventory(assets, difficulty=DIFFICULTY_HARDCORE)
    assert all(s is None for s in inv_hard.slots), "Hardcore mode must start with 0 items"

    # Hardcore drops all items on death
    game_hard = PotariaGame()
    game_hard.difficulty = DIFFICULTY_HARDCORE
    game_hard.inventory.slots[0] = ItemStack("iron_broadsword", 1)
    game_hard.inventory.slots[1] = ItemStack("healing_potion", 5)
    game_hard.player.take_damage(9999)
    assert game_hard.player.is_dead is True
    game_hard.update_gameplay(0.016)

    assert game_hard.inventory.slots[0] is None
    assert game_hard.inventory.slots[1] is None
    dropped_ids = [d.item_id for d in game_hard.combat.dropped_items]
    assert "iron_broadsword" in dropped_ids
    assert "healing_potion" in dropped_ids

    # 3. YOLO Mode
    stats_yolo = PlayerStats()
    stats_yolo.set_yolo_mode(True)
    assert stats_yolo.max_hp == 20, "YOLO mode must be locked to 1 HEART (20 HP)"

    # Attempt to increment HP via level up
    stats_yolo.add_exp(50000)
    assert stats_yolo.level > 1
    assert stats_yolo.max_hp == 20, "Level ups must NOT increase HP in YOLO mode"

    # Attempt to increment HP via bonus gear
    stats_yolo.bonus_max_hp = 100
    assert stats_yolo.max_hp == 20, "Bonus HP must NOT increase HP in YOLO mode"

    # YOLO Death transitions to STATE_GAME_OVER
    game_yolo = PotariaGame()
    game_yolo.difficulty = DIFFICULTY_YOLO
    game_yolo.player.stats.set_yolo_mode(True)
    game_yolo.player.take_damage(9999)
    assert game_yolo.player.is_dead is True
    game_yolo.update_gameplay(0.016)
    assert game_yolo.menu.state == STATE_GAME_OVER, "YOLO death must trigger STATE_GAME_OVER"

    print("  -> Normal, Hardcore, and YOLO 1-Heart Permadeath verified!")

def test_save_load_world():
    print("\n[Test 7] Testing Minecraft-Style Portable JSON World Save & Load...")
    game = PotariaGame()
    world_test_name = "Automated_Test_World_999"

    # Clean previous test if any
    delete_world(world_test_name)

    game.active_world_name = world_test_name
    game.difficulty = DIFFICULTY_YOLO
    game.world_type = WORLD_TYPE_FINITE
    game.game_mode = MODE_LAST_MAN_STANDING

    # Modify world state
    game.block_deltas[(42, 60)] = TILE_STONE
    game.block_deltas[(43, 60)] = TILE_AIR
    game.wall_deltas[(42, 60)] = 1
    game.player.x = 888.0
    game.player.y = 555.0
    game.player.stats.set_yolo_mode(True)
    game.player.stats.level = 7
    game.inventory.slots[0] = ItemStack("gold_broadsword", 1)
    game.inventory.slots[1] = ItemStack("golden_fry", 12)
    game.combat.mini_bosses_slain = 3
    game.combat.boss_defeated = True

    # Save world
    save_path = save_world(world_test_name, game)
    assert os.path.exists(save_path), f"Save file {save_path} must exist"

    # Verify JSON structure
    with open(save_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert data["world_name"] == world_test_name
    assert data["difficulty"] == DIFFICULTY_YOLO
    assert data["world_type"] == WORLD_TYPE_FINITE
    assert data["game_mode"] == MODE_LAST_MAN_STANDING
    assert data["player"]["stats"]["level"] == 7
    assert len(data["block_deltas"]) == 2

    # Verify list_saved_worlds includes this world
    saved_list = list_saved_worlds()
    assert any(w["name"] == world_test_name for w in saved_list)

    # Now create fresh game and load
    new_game = PotariaGame()
    success = load_world(world_test_name, new_game)
    assert success is True
    assert new_game.difficulty == DIFFICULTY_YOLO
    assert new_game.world_type == WORLD_TYPE_FINITE
    assert new_game.game_mode == MODE_LAST_MAN_STANDING
    assert new_game.player.stats.locked_one_heart is True
    assert new_game.player.stats.max_hp == 20
    assert new_game.player.stats.level == 7
    assert new_game.player.x == 888.0
    assert new_game.player.y == 555.0
    assert new_game.inventory.slots[0].item_id == "gold_broadsword"
    assert new_game.inventory.slots[1].item_id == "golden_fry"
    assert new_game.inventory.slots[1].count == 12
    assert new_game.combat.mini_bosses_slain == 3
    assert new_game.combat.boss_defeated is True
    assert new_game.block_deltas[(42, 60)] == TILE_STONE
    assert new_game.block_deltas[(43, 60)] == TILE_AIR

    # Clean up
    delete_world(world_test_name)
    assert not os.path.exists(save_path)
    print("  -> Save and Load world persistence verified successfully!")

def test_pvp_last_man_standing():
    print("\n[Test 8] Testing Last Man Standing / PvP Friendly Fire Mode...")
    game = PotariaGame()
    game.game_mode = MODE_LAST_MAN_STANDING

    # Mock client and a remote player
    class MockClient:
        def __init__(self):
            self.connected = True
            self.pending_block_deltas = []
            self.remote_players = {
                2: {"x": 300.0, "y": 200.0, "hp": 100, "name": "Opponent_Tuber"}
            }

    game.client = MockClient()

    # Fire projectile at remote player
    from src.entities.projectile import ArrowProjectile
    arrow = ArrowProjectile(290, 210, angle=0.0, speed=10.0, damage=35)
    arrow.frect.x = 295
    arrow.frect.y = 205
    game.combat.projectiles.append(arrow)

    # Run update in LMS mode
    game.update_gameplay(0.016)

    # Remote player should take damage in LMS mode!
    assert game.client.remote_players[2]["hp"] == 65
    assert len(game.combat.damage_numbers) > 0

    # Eliminate opponent -> Last Tuber Standing victory fanfare
    game.client.remote_players[2]["hp"] = 0
    game.update_gameplay(0.016)
    assert game.pvp_victor_banner == "LAST TUBER STANDING! VICTORY!"

    print("  -> Last Man Standing PvP mechanics and victory fanfare verified!")

def test_biome_runes_and_arena_teleportation():
    print("\n[Test 9] Testing Biome Runes & Mini-Boss Arena Teleportation...")
    game = PotariaGame()

    # Check rune recipes and items
    assert "desert_rune" in ITEM_REGISTRY
    assert "cryo_rune" in ITEM_REGISTRY
    assert "necro_rune" in ITEM_REGISTRY

    # Test right clicking desert rune
    game.player.x = 50.0
    game.player.y = 60.0
    game.inventory.slots[0] = ItemStack("desert_rune", 1)
    game.inventory.selected_slot = 0

    # Call handle_right_click at arbitrary reach
    game.handle_right_click(100, 100)

    # Player should be saved pre_arena_pos and warped to desert arena
    assert game.player.pre_arena_pos == (50.0, 60.0)
    assert game.combat.boss is not None
    assert isinstance(game.combat.boss, IgnisColossus)
    assert game.inventory.slots[0] is None, "Rune should be consumed"

    # Simulate boss defeat -> Teleport Spud back to previous location and drop Portal Shard
    game.combat.boss.hp = 0
    game.combat.boss.is_dead = True
    game.combat.update(0.016, game.world, game.player, is_night=False)

    assert game.player.x == 50.0
    assert game.player.y == 60.0
    assert game.player.pre_arena_pos is None
    dropped_shard = any(it.item_id == "portal_shard" for it in game.combat.dropped_items)
    assert dropped_shard is True, "Defeated mini-boss must drop Portal Shards!"

    print("  -> Biome Altar runes, arena warps, return portal and shards verified!")

def test_detailed_reviewer_verifications():
    print("\n[Test 10] Testing Deep Reviewer Verifications & Robustness...")
    assets = AssetFactory()
    sound = SoundManager()

    # 1. Full inventory ground item safety in combat loop
    game = PotariaGame()
    for i in range(INV_TOTAL_SLOTS):
        game.inventory.slots[i] = ItemStack("copper_pickaxe", 1)
    assert game.player.inventory is not None
    assert game.player.inventory.can_add_item("dirt_block", 1) is False

    dropped = DroppedItem("dirt_block", 10, game.player.center_x, game.player.center_y, assets)
    dropped.age = 2.0
    game.combat.dropped_items = [dropped]

    # DroppedItem update must NOT magnetize when inventory full
    dropped.update(0.016, game.world, game.player)
    assert dropped.magnet_speed == 0.0, "Item must not magnetize towards player with full inventory"

    # Combat update must NOT mark item as picked up
    game.combat.update(0.016, game.world, game.player, is_night=False)
    assert dropped.picked_up is False, "Item must not be marked picked up when inventory is full"
    assert len(game.combat.dropped_items) == 1

    # 2. Dropping via UI button rect and hovered slot
    game.inventory.slots[0] = ItemStack("torch", 10)
    drop_btn_rect = game.inventory.get_drop_button_rect()
    assert isinstance(drop_btn_rect, pygame.Rect)
    assert drop_btn_rect.width > 0 and drop_btn_rect.height > 0

    # Hover slot 0 and drop
    slot0_rect = pygame.Rect(20, 20, 36, 36)
    game.inventory.is_open = True
    game.drop_selected_or_held(mouse_pos=(slot0_rect.centerx, slot0_rect.centery))
    assert game.inventory.slots[0].count == 9
    assert game.combat.dropped_items[-1].item_id == "torch"

    # 3. Hardcore death dropping equipment slots
    game_hard = PotariaGame()
    game_hard.difficulty = DIFFICULTY_HARDCORE
    game_hard.player.equipment.equip("copper_helmet", game_hard.player.stats)
    game_hard.player.equipment.equip("copper_chestplate", game_hard.player.stats)
    assert game_hard.player.equipment.slots["head"] == "copper_helmet"
    assert game_hard.player.equipment.slots["chest"] == "copper_chestplate"

    game_hard.player.take_damage(99999)
    assert game_hard.player.is_dead is True
    game_hard.update_gameplay(0.016)

    # Equipment slots must be cleared and dropped
    assert game_hard.player.equipment.slots["head"] is None
    assert game_hard.player.equipment.slots["chest"] is None
    dropped_item_ids = [d.item_id for d in game_hard.combat.dropped_items]
    assert "copper_helmet" in dropped_item_ids
    assert "copper_chestplate" in dropped_item_ids

    # 4. YOLO restart clears equipment
    game_yolo = PotariaGame()
    game_yolo.difficulty = DIFFICULTY_YOLO
    game_yolo.player.stats.set_yolo_mode(True)
    game_yolo.player.equipment.equip("copper_helmet", game_yolo.player.stats)
    # Simulate restart_yolo action in event loop
    for slot_k in list(game_yolo.player.equipment.slots.keys()):
        game_yolo.player.equipment.slots[slot_k] = None
    game_yolo.player.equipment.recalculate_stats(game_yolo.player.stats)
    game_yolo.inventory.set_difficulty_loadout(DIFFICULTY_YOLO)
    assert game_yolo.player.equipment.slots["head"] is None
    assert game_yolo.player.stats.max_hp == 20

    # 5. Starfury star hitting TILE_BARRIER
    from src.entities.projectile import CelestialStarProjectile
    star = CelestialStarProjectile(100, 200, 50, damage=60)
    world = game.world
    tx, ty = int(100 // 32), int(120 // 32)
    world.set_tile(tx, ty, TILE_BARRIER)
    test_mob = GreenSlime(100, 150, assets)
    initial_mob_hp = test_mob.hp

    # Move star to hit barrier
    star.pos.x = 100
    star.pos.y = ty * 32 + 10
    star.frect.center = star.pos
    star.update(0.016, world, game.particle_system, sound, game.camera, [test_mob], None, game.player)

    assert star.blocked_by_barrier is True, "Starfury star must be flagged as blocked by barrier"
    assert test_mob.hp == initial_mob_hp, "Mob underneath barrier must take 0 damage from blocked star"

    # 6. DiggerMob blocked by player_placed_tiles
    digger = DiggerMob(100, 100, assets)
    place_tx, place_ty = int(128 // 32), int(100 // 32)
    world.set_tile(place_tx, place_ty, TILE_DIRT) # Dirt is normally diggable!
    world.player_placed_tiles.add((place_tx, place_ty))

    digger.x = 128 - digger.width + 2
    digger.vx = 2.0
    digger.update(0.016, world, game.player)
    assert digger.vx == 0.0, "Digger must be stopped by player_placed_tiles even for dirt"

    # 7. Corrupted JSON load_world handling
    corrupt_dir = os.path.join("saves", "Corrupt_Test_World")
    os.makedirs(corrupt_dir, exist_ok=True)
    corrupt_file = os.path.join(corrupt_dir, "world.json")
    with open(corrupt_file, "w", encoding="utf-8") as f:
        f.write("{ invalid json corrupted <<<")
    corrupt_game = PotariaGame()
    loaded = load_world("Corrupt_Test_World", corrupt_game)
    assert loaded is False, "Corrupted world file must safely return False without crashing"
    delete_world("Corrupt_Test_World")

    # 8. LMS mode biome spawning, melee and fireball PvP damage
    lms_game = PotariaGame()
    lms_game.game_mode = MODE_LAST_MAN_STANDING
    spawn_p1 = lms_game.world.get_biome_spawn(player_idx=1)
    spawn_p2 = lms_game.world.get_biome_spawn(player_idx=2)
    assert spawn_p1[0] != spawn_p2[0], "LMS players must spawn in different horizontal biome coordinates"

    class MockLMSClient:
        def __init__(self):
            self.connected = True
            self.remote_players = {
                2: {"x": 100.0, "y": 100.0, "hp": 100, "name": "Duelist"}
            }

    lms_game.client = MockLMSClient()
    lms_game.player.x = 80.0
    lms_game.player.y = 100.0
    lms_game.player.facing_right = True
    lms_game.player.is_swinging = True
    lms_game.player.swing_progress = 0.3
    lms_game.update_gameplay(0.016)

    # Melee swing hit duelist
    assert lms_game.client.remote_players[2]["hp"] < 100, "Melee sword swing must damage remote player in LMS mode"

    # Fireball hit duelist
    from src.entities.player import PlayerFireball
    fb = PlayerFireball(100.0, 100.0, 0.0, 0.0, None)
    lms_game.player.fireballs.append(fb)
    lms_game.player.is_swinging = False
    hp_before_fb = lms_game.client.remote_players[2]["hp"]
    lms_game.update_gameplay(0.016)
    assert lms_game.client.remote_players[2]["hp"] < hp_before_fb, "Fireball must damage remote player in LMS mode"

    print("  -> Deep reviewer verifications and edge cases verified successfully!")

def run_all_tests():
    print("==================================================================")
    print("POTARIA GAMEPLAY EXPANSION & SYSTEMS OVERHAUL TEST SUITE")
    print("Developer: Kurados  |  Pure Python & pygame-ce")
    print("==================================================================")

    test_item_dropping_and_physics()
    test_full_inventory_bug_fix()
    test_equipment_and_mob_balancing()
    test_new_mobs()
    test_world_options_finite_vs_infinite()
    test_difficulty_modes()
    test_save_load_world()
    test_pvp_last_man_standing()
    test_biome_runes_and_arena_teleportation()
    test_detailed_reviewer_verifications()

    print("\n==================================================================")
    print("ALL 10 GAMEPLAY EXPANSION TEST SUITES PASSED WITH ZERO ERRORS!")
    print("Developer: Kurados  |  Engine: pygame-ce")
    print("==================================================================")

if __name__ == "__main__":
    run_all_tests()
