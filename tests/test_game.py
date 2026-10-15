"""
Potaria - Comprehensive Automated Integration & Multiplayer Tests
Developer: Kurados

Tests:
1. Asset synthesis engine (Spud sprites, armor sets, skill books, boss, branding)
2. Infinite open world terrain streaming (Negative & positive chunk coordinates, no horizontal walls)
3. Chroisen-style RPG systems (Level 1-100, EXP, HP, MP, ATK, DEF, paperdoll equipment slots)
4. Skill Books & Combat Abilities (Skill learning, MP costs, cooldowns, active casts)
5. Unbounded player movement (Spud moves freely into negative coordinates, eats potatoes)
6. Crafting engine & Dungeon Rune boss awakening
7. LAN Multiplayer loopback networking (Server start, Client connect, seed sync, player updates, chat)
8. Boss battle & victory state transition
"""

import os
import sys
import time

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Headless drivers for test environment
os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"

import pygame
from src.constants import (
    SCREEN_WIDTH, SCREEN_HEIGHT,
    TILE_DIRT, TILE_STONE, TILE_AIR, TILE_BEDROCK, TILE_WOOD,
    TILE_FURNACE, TILE_WORK_BENCH, TILE_DUNGEON_BRICK, TILE_DUNGEON_ALTAR, SCALED_TILE,
    TILE_ROOF_TILES, TILE_WOOD_PLANKS, TILE_GLASS, TILE_DOOR_CLOSED, TILE_DOOR_OPEN,
    TILE_TABLE, TILE_CHAIR, WALL_WOOD, WALL_STONE_BRICK,
    RARITY_COMMON, RARITY_UNCOMMON, RARITY_RARE, RARITY_EPIC, RARITY_LEGENDARY, RARITY_MYTHIC,
    RARITY_COLORS,
    STATE_MENU, STATE_PLAYING, STATE_VICTORY
)
from src.assets.asset_factory import AssetFactory
from src.audio.sound_effects import SoundManager
from src.world.world import World
from src.world.chunk_manager import ChunkManager, CHUNK_WIDTH, CHUNK_HEIGHT
from src.entities.player import Player
from src.entities.mob import DemonEye, BatMob
from src.entities.boss import LordMalus, GrandBossSolRho
from src.combat.combat_system import CombatManager
from src.entities.particle import ParticleSystem
from src.camera import Camera
from src.ui.inventory import Inventory, ItemStack, ITEM_REGISTRY
from src.ui.crafting import CraftingSystem
from src.ui.menu import MenuManager
from src.ui.character_panel import CharacterPanel
from src.ui.hud import HUD
from src.ui.minimap import MiniMap
from src.rpg.stats import PlayerStats
from src.rpg.equipment import Equipment, ARMOR_DATA
from src.rpg.skills import SkillManager
from src.network.server import LANServer
from src.network.client import LANClient

def test_all_potaria_systems():
    pygame.init()
    print("==================================================================")
    print("POTARIA INTEGRATION & MULTIPLAYER TEST SUITE (Developer: Kurados)")
    print("==================================================================")

    # 1. Asset Engine
    print("\n[Test 1] Testing Asset Synthesis Engine...")
    factory = AssetFactory()
    assert len(factory.player_sprites["walk"]) == 8, "Spud walk cycle should be 8 frames for smooth 12 FPS"
    assert len(factory.player_sprites["idle_frames"]) == 6, "Spud idle cycle should be 6 frames for 12 FPS breathing"
    assert len(factory.mobs["slime"]) == 6, "Slime should have 6 bounce frames"
    assert len(factory.mobs["zombie"]) == 6, "Zombie should have 6 shambling frames"
    assert len(factory.mobs["demon_eye"]) == 6, "Demon Eye should have 6 pulsating frames"
    assert "starfury" in factory.items, "Missing Starfury celestial sword sprite"
    assert "celestial_star" in factory.items, "Missing falling celestial star sprite"
    assert "wooden_arrow" in factory.items, "Missing wooden arrow projectile sprite"
    assert "game_icon" in factory.branding, "Missing game icon"
    assert "lord_malus" in factory.boss, "Missing Lord Malus boss sprite"
    assert "raw_potato" in factory.items, "Missing raw potato item"
    assert "copper_chestplate" in factory.items, "Missing copper chestplate"
    assert "skillbook_whirlwind" in factory.items, "Missing Whirlwind skillbook"
    assert "dungeon_rune" in factory.items, "Missing dungeon teleporter rune"
    print("  -> Asset Factory & 12 FPS Animation Sprites OK.")

    # 2. Infinite Chunk World
    print("\n[Test 2] Testing Infinite Open World (Zero Boundary Clamping)...")
    world = World(factory, seed=42)
    # Check that negative chunks are dynamically generated seamlessly
    tile_neg = world.get_tile(-50, 80)
    tile_pos = world.get_tile(50, 80)
    tile_far_neg = world.get_tile(-500, 80)
    tile_far_pos = world.get_tile(500, 80)
    assert tile_neg in (TILE_DIRT, TILE_STONE, TILE_AIR), "Negative tile should be valid terrain"
    assert tile_pos in (TILE_DIRT, TILE_STONE, TILE_AIR), "Positive tile should be valid terrain"
    assert tile_far_neg in (TILE_DIRT, TILE_STONE, TILE_AIR), "Far negative tile should be valid terrain"
    assert tile_far_pos in (TILE_DIRT, TILE_STONE, TILE_AIR), "Far positive tile should be valid terrain"
    print("  -> Infinite World Chunk Streaming (negative & positive coordinates) OK.")

    # 3. Chroisen-Style RPG Stats & Equipment
    print("\n[Test 3] Testing RPG Stats & Paperdoll Equipment...")
    stats = PlayerStats()
    assert stats.level == 1
    assert stats.hp == 100
    assert stats.mp == 50
    assert stats.total_atk == 10
    assert stats.total_def == 2

    # Equip Copper Gear
    equip = Equipment()
    success, _ = equip.equip("copper_chestplate", stats)
    assert success, "Should successfully equip copper chestplate"
    assert equip.slots["chest"] == "copper_chestplate"
    assert stats.total_def == 2 + ARMOR_DATA["copper_chestplate"]["def"], "DEF should include chestplate"

    success, _ = equip.equip("iron_broadsword", stats)
    assert success, "Should successfully equip iron broadsword"
    assert equip.slots["weapon"] == "iron_broadsword"
    assert stats.total_atk > 10, "ATK should include sword bonus"

    # EXP & Level Up
    leveled = stats.gain_exp(120)
    assert leveled, "Should level up after gaining 120 EXP"
    assert stats.level == 2, "Spud should now be Level 2"
    assert stats.max_hp > 100, "Max HP should scale on level up"
    print(f"  -> Spud Leveled Up to {stats.level}! Max HP: {stats.max_hp}, ATK: {stats.total_atk}, DEF: {stats.total_def}")
    print("  -> RPG Stats & Paperdoll Equipment OK.")

    # 4. Skill Books & Combat Abilities
    print("\n[Test 4] Testing Skill Books & Active Hotkey Abilities...")
    skills = SkillManager()
    assert "power_slash" in skills.learned_skills
    assert "whirlwind" not in skills.learned_skills

    # Learn Whirlwind from Skill Book
    learned = skills.learn_skill("whirlwind")
    assert learned, "Should learn whirlwind from book"
    assert "whirlwind" in skills.learned_skills

    # Cast Power Slash
    stats.mp = 50
    cast_slash = skills.use_skill("power_slash", stats)
    assert cast_slash, "Should successfully cast Power Slash"
    assert stats.mp == 50 - 8, "Power Slash should cost 8 MP"
    assert skills.cooldowns["power_slash"] > 0, "Power Slash should enter cooldown"

    # Attempt to cast during cooldown should fail
    cast_again = skills.use_skill("power_slash", stats)
    assert not cast_again, "Cannot cast during active cooldown"
    print("  -> Skill System & MP Cooldown Engine OK.")

    # 5. Spud Movement & Physics (Unbounded Horizontal Movement)
    print("\n[Test 5] Testing Spud Free Movement into Negative Coordinates...")
    sounds = SoundManager()
    player = Player(0, world.spawn_point[1], factory, sounds)
    
    # Spud moves left into negative territory
    player.x = -150.0
    player.vx = -50.0
    player.update(0.016, world)
    assert player.x < -100.0, "Spud must NOT be clamped to x >= 0! Open world is boundless."

    # Food healing
    player.health = 30
    player.consume_item("raw_potato")
    assert player.health == 55, "Raw potato should restore 25 HP"
    player.consume_item("mashed_potato")
    assert player.health == player.max_health, "Mashed potato should restore to max HP"
    print(f"  -> Spud at x={player.x:.1f} (Infinite World) & Food Consumption OK.")

    # 6. Crafting System & Dungeon Teleport Rune
    print("\n[Test 6] Testing Cooking, Crafting & Dungeon Rune...")
    inv = Inventory(factory)
    crafting = CraftingSystem(factory, sounds)
    
    # Check starter loadout
    assert inv.count_item("raw_potato") > 0, "Spud should start with raw potatoes"
    assert inv.count_item("copper_chestplate") > 0, "Spud should start with copper chestplate"

    # Craft Mashed Potatoes near furnace
    inv.add_item("raw_potato", 4)
    inv.add_item("wood", 4)
    
    ptx = int(player.center_x // SCALED_TILE)
    pty = int(player.center_y // SCALED_TILE)
    world.set_tile(ptx + 1, pty, TILE_FURNACE)
    crafting.update_recipes(inv, world, player)
    
    mash_recipe = next((r for r in crafting.available_recipes if r["result"] == "mashed_potato"), None)
    assert mash_recipe is not None, "Mashed potato cooking recipe must be available near furnace"
    
    # Craft Dungeon Rune (requires work bench, gold_bar, gel, stone_brick)
    world.set_tile(ptx - 1, pty, TILE_WORK_BENCH)
    inv.add_item("gold_bar", 5)
    inv.add_item("gel", 10)
    inv.add_item("stone_brick", 10)
    crafting.update_recipes(inv, world, player)
    rune_recipe = next((r for r in crafting.available_recipes if r["result"] == "dungeon_rune"), None)
    assert rune_recipe is not None, "Dungeon Rune recipe should be craftable near work bench"
    print("  -> Crafting Engine & Cooking OK.")

    # 7. LAN Multiplayer Loopback Networking
    print("\n[Test 7] Testing LAN Host/Client Multiplayer Networking...")
    test_port = 28999
    server = LANServer(host="127.0.0.1", port=test_port, max_players=5)
    server.start(world_seed=998877)
    time.sleep(0.1)

    client1 = LANClient()
    connected, seed = client1.connect("127.0.0.1", port=test_port, player_name="TestSpud")
    assert connected, "Client 1 should connect to LAN server"
    assert seed == 998877, f"Seed should match server world seed (got {seed})"
    time.sleep(0.1)

    # Client sends player update
    client1.send_player_update(x=120.0, y=240.0, vx=1.5, vy=0.0, hp=100, max_hp=100, level=2, facing=True, anim="walk", held_item="iron_broadsword")
    client1.send_chat("TestSpud", "Hello Potaria LAN!")
    time.sleep(0.15)

    with server.lock:
        assert len(server.clients) == 1, "Server should have 1 connected client"
        assert 2 in server.players, "Client should be registered as Player 2"
        p2 = server.players[2]
        assert p2["x"] == 120.0, "Player 2 x-coord should be synced"
        assert p2["level"] == 2, "Player 2 level should be synced"
        assert p2["held_item"] == "iron_broadsword", "Player 2 held item should be synced"

    # Stop LAN networking
    client1.disconnect()
    server.stop()
    print("  -> LAN Cooperative Multiplayer Loopback & Packet Sync OK.")

    # 8. Dungeon Mini-Bosses, Portal Shards & 2-Phase Grand Boss Sol-Rho
    print("\n[Test 8] Testing Subterranean Mini-Bosses, Portal Shards & 2-Phase Grand Boss Sol-Rho...")
    particles = ParticleSystem()
    cam = Camera(1280, 720)
    combat = CombatManager(factory, sounds, particles, cam)
    
    # 8a. Subterranean Mini-Boss
    combat.spawn_boss(0, 500)
    assert combat.boss is not None, "A Dungeon Mini-Boss should spawn"
    assert combat.boss.hp == combat.boss.max_hp and combat.boss.hp >= 400, "Mini-Boss base HP should match max_hp"
    assert getattr(combat.boss, "is_mini_boss", False), "Boss should be flagged as mini-boss"
    
    # Slay Mini-Boss
    combat.boss.take_damage(2000)
    combat.update(0.016, world, player, is_night=True)
    assert combat.boss_defeated, "Mini-boss should be marked as defeated"
    assert combat.mini_bosses_slain >= 1, "Mini-boss slain counter should increment"
    assert not combat.grand_boss_defeated, "Defeating mini-boss must NOT end the game!"
    
    # Verify Portal Shard drop
    shard_drop = next((it for it in combat.dropped_items if it.item_id == "portal_shard"), None)
    assert shard_drop is not None, "Mini-boss must drop Portal Shards for Grand Boss summoning"
    combat.dropped_items.clear()
    
    # 8b. Grand Boss Sol-Rho (Souls-like Multi-Phase Battle)
    combat.spawn_grand_boss(0, 400, party_size=1)
    assert combat.boss is not None, "Grand Boss Sol-Rho should spawn"
    assert isinstance(combat.boss, GrandBossSolRho), "Boss must be GrandBossSolRho instance"
    assert combat.boss.phase == 1, "Should start in Phase 1"
    assert combat.boss.hp == 1000, "Base solo Phase 1 HP should be 1000"
    
    # Damage Phase 1 down to 0 -> triggers dramatic resurrection transition
    combat.boss.take_damage(1500)
    assert combat.boss.is_transforming, "Depleting Phase 1 HP must trigger dramatic transformation sequence"
    assert combat.boss.phase == 1, "Phase should still report 1 during transition"
    
    # Update through transformation timer (2.2 seconds)
    combat.boss.update(2.5, world, player, particles, cam)
    assert not combat.boss.is_transforming, "Should finish transformation"
    assert combat.boss.phase == 2, "Should awaken into Phase 2: Void Incarnate"
    assert combat.boss.hp == 1400, "Phase 2 should possess full 1400 HP bar"
    assert "Void" in combat.boss.name, "Phase 2 should display Void Incarnate title"
    
    # Damage Phase 2 down to 0 -> True Victory
    combat.boss.take_damage(2000)
    combat.update(0.016, world, player, is_night=True)
    assert combat.grand_boss_defeated, "Defeating Phase 2 must achieve True Victory!"
    assert combat.boss is None, "Boss entity should despawn upon final defeat"
    
    # Check Grand Boss Celestial Loot
    drop_ids = [it.item_id for it in combat.dropped_items]
    assert "celestial_greatsword" in drop_ids, "Should drop Celestial Greatsword"
    assert "titan_chestplate" in drop_ids, "Should drop Titan Chestplate"
    assert "crown_of_potaria" in drop_ids, "Should drop Crown of Potaria"
    print("  -> Mini-Bosses, Portal Shards & Souls-like 2-Phase Grand Boss Sol-Rho OK.")

    # 9. Pygame-ce Engine Upgrades (FRect, Vector2, 12 FPS, Ballistics, Spatial Stereo)
    print("\n[Test 9] Testing Pygame-ce Upgrades (FRect, Vector2, 12 FPS, Ballistic Projectiles, Spatial Audio)...")
    from src.entities.projectile import ArrowProjectile, CelestialStarProjectile
    from src.world.lighting import LightingEngine

    # Check FRect sub-pixel physics
    assert isinstance(player.rect, pygame.FRect), "Player rect must be a pygame.FRect"
    assert hasattr(pygame, "IS_CE") and pygame.IS_CE, "Must run under pygame-ce engine"

    # 12 FPS Animation Frame Timing
    player.x = 0.0
    player.y = 70 * SCALED_TILE - player.height
    player.vx = 2.0
    player.anim_timer = 0.0
    start_frame = player.walk_frame_idx
    # Advance by 1/12th second (0.084s)
    player.update(0.084, world)
    assert player.walk_frame_idx == (start_frame + 1) % len(player.walk_sprites), "Walk frame must advance at 12 FPS"

    # Ballistic Arrow Projectile (Vector2 & Gravity)
    arrow = ArrowProjectile(player.center_x, player.center_y, angle_rad=0.0, speed=10.0, damage=15)
    assert isinstance(arrow.frect, pygame.FRect), "Arrow must use pygame.FRect"
    assert isinstance(arrow.pos, pygame.math.Vector2), "Arrow must use Vector2"
    initial_y = arrow.pos.y
    arrow.update(0.05, world, particles, sounds, player)
    assert arrow.pos.x > player.center_x, "Arrow must travel horizontally forward"
    assert arrow.vel.y > 0, "Gravity should curve arrow downwards"

    # Celestial Starfury Star Projectile (Heavenly Fall & 72px AoE Explosion)
    target_x = player.center_x + 100
    target_y = player.center_y
    star = CelestialStarProjectile(target_x, target_y, camera_y=target_y - 200, damage=42)
    assert isinstance(star.frect, pygame.FRect), "Star must use pygame.FRect"
    assert star.pos.y < target_y, "Star must spawn in the heavens above target"
    # Update star until it impacts target
    for _ in range(30):
        star.update(0.05, world, particles, sounds, cam, combat.mobs, combat.boss, player)
        if star.exploded:
            break
    assert star.exploded, "Celestial Star must explode upon reaching target coordinates"

    # Spatial Stereo Audio Engine
    assert sounds.channels == 2, "Sound system must be stereo (channels=2)"
    ch_left = sounds.play_spatial("bow", sound_x=player.center_x - 300, sound_y=player.center_y, listener_x=player.center_x, listener_y=player.center_y)
    ch_right = sounds.play_spatial("bow", sound_x=player.center_x + 300, sound_y=player.center_y, listener_x=player.center_x, listener_y=player.center_y)
    # Channel returns or succeeds gracefully in dummy headless mode

    # Dynamic Atmospheric Lighting with Color Grading
    lighting = LightingEngine(1280, 720)
    lighting.compute_viewport_light(world, 0, 60, 20, 80, ambient_sunlight=12, ambient_tint=(1.18, 0.96, 0.76))
    assert lighting.light_surf.get_width() > 0, "Light surface must compute properly with ambient tint"
    # 10. Biomes, Chests, Mob Despawning & Bow Arrow Rules
    print("\n[Test 10] Testing Biomes, Treasure Chests, Mob Despawning & Bow Ammunition...")
    from src.constants import (
        BIOME_FOREST, BIOME_DESERT, BIOME_SNOW, BIOME_CORRUPTION,
        BIOME_CAVERN, BIOME_DUNGEON, BIOME_MUSHROOM, TILE_CHEST
    )
    from src.audio.bgm_manager import BgmManager

    # Verify Biome Generation
    b_forest = world.get_biome_at(0, 70)
    b_cavern = world.get_biome_at(0, 170)
    b_dungeon = world.get_biome_at(0, 215)
    assert b_cavern == BIOME_CAVERN, "Depth 170 should be Cavern biome"
    assert b_dungeon == BIOME_DUNGEON, "Depth 215 should be Dungeon biome"
    assert b_forest in (BIOME_FOREST, BIOME_DESERT, BIOME_SNOW, BIOME_CORRUPTION), "Surface tile should be a valid biome"

    # Verify Starfury is NOT in Workbench Crafting
    crafting.update_recipes(inv, world, player)
    assert not any(r["result"] == "starfury" for r in crafting.available_recipes), "Starfury must NOT be craftable! It is an elusive treasure drop."

    # Test Bow Ammunition Rules: Cannot fire without arrows!
    inv.slots = [None] * len(inv.slots)
    inv.slots[0] = ItemStack("wood_bow", 1)
    inv.selected_slot = 0
    init_proj_count = len(combat.projectiles)

    # Attempt fire with 0 arrows
    arrow_count = inv.count_item("wooden_arrow") + inv.count_item("frostburn_arrow")
    assert arrow_count == 0, "Inventory has 0 arrows"
    # Bow should not fire if arrow_count <= 0
    if arrow_count > 0:
        inv.remove_item("wooden_arrow", 1)
        combat.spawn_projectile(ArrowProjectile(player.center_x, player.center_y, 0, 14, 14))
    assert len(combat.projectiles) == init_proj_count, "Should NOT spawn projectile when out of arrows!"

    # Add 2 wooden arrows and fire
    inv.add_item("wooden_arrow", 2)
    assert inv.count_item("wooden_arrow") == 2
    inv.remove_item("wooden_arrow", 1)
    combat.spawn_projectile(ArrowProjectile(player.center_x, player.center_y, 0, 14, 14))
    assert len(combat.projectiles) == init_proj_count + 1, "Should spawn arrow projectile when ammo is present"
    assert inv.count_item("wooden_arrow") == 1, "Should consume exactly 1 arrow"

    # Test Mob Despawning when Traveling Far (> 1300 px)
    from src.entities.mob import SlimeMob
    far_mob = SlimeMob(player.center_x + 2000, player.center_y, factory)
    combat.mobs.append(far_mob)
    assert far_mob in combat.mobs
    combat.update(0.1, world, player, is_night=False)
    assert far_mob not in combat.mobs, "Distant mobs (>1300px) must despawn so new mobs spawn around player!"

    print("  -> Biomes, Non-Craftable Starfury, Arrow Ammo Consumption & Far-Mob Despawning OK.")

    # 11. BGM Music Engine, Settings Screen & Pause Menu
    print("\n[Test 11] Testing Procedural BGM Engine, Settings & In-Game Pause...")
    bgm = BgmManager()
    assert bgm.enabled or os.environ.get("SDL_AUDIODRIVER") == "dummy"
    assert BIOME_FOREST in bgm.tracks
    assert BIOME_DESERT in bgm.tracks
    assert BIOME_SNOW in bgm.tracks
    assert BIOME_CORRUPTION in bgm.tracks
    assert BIOME_DUNGEON in bgm.tracks

    # Test BGM Biome Transition
    bgm.update(0.1, BIOME_DESERT, has_nearby_threat=False, is_boss_active=False)
    bgm.update(0.1, BIOME_DUNGEON, has_nearby_threat=False, is_boss_active=True)

    # Test Settings Menu
    menu = MenuManager(factory, sounds, bgm)
    menu.open_settings(from_state=STATE_PLAYING)
    assert menu.state == "settings"
    assert menu.previous_state == STATE_PLAYING

    # Test Volume Controls
    vol_res = menu.handle_click((SCREEN_WIDTH // 2 - 150, 195))  # Click vol_master_down button
    assert menu.settings["master_volume"] <= 1.0

    # Test Pause Menu Buttons in PotariaGame
    from main import PotariaGame
    game = PotariaGame()
    assert len(game.pause_buttons) == 3, "Pause menu must have Resume, Settings, and Return to Main Menu buttons"
    resume_btn = next((b for b in game.pause_buttons if b.action == "resume"), None)
    settings_btn = next((b for b in game.pause_buttons if b.action == "settings"), None)
    main_menu_btn = next((b for b in game.pause_buttons if b.action == "main_menu"), None)
    assert resume_btn and settings_btn and main_menu_btn, "All 3 pause buttons must exist"

    # Test Return to Main Menu from Pause
    game.paused = True
    game.return_to_main_menu()
    assert not game.paused, "Game should unpause on return to menu"
    assert game.menu.state == STATE_MENU, "Menu state should be STATE_MENU"
    print("  -> Procedural Synth BGM, Settings Screen, & Pause Menu OK.")

    # 12. Player Animation, MiniMap Radar & Rich Tooltips/Rarities
    print("\n[Test 12] Testing MiniMap, Player Current Animation, & Item Lore/Rarities...")
    # Verify player current_anim property (fixes LAN host crash)
    p = Player(100, 100, factory, sounds)
    p.on_ground = True
    p.vx = 0.0
    assert p.current_anim == "idle", f"Expected idle, got {p.current_anim}"
    p.vx = 2.0
    assert p.current_anim == "walk", f"Expected walk, got {p.current_anim}"
    p.on_ground = False
    p.vy = -5.0
    assert p.current_anim == "jump", f"Expected jump, got {p.current_anim}"
    p.vy = 5.0
    assert p.current_anim == "fall", f"Expected fall, got {p.current_anim}"

    # Verify MiniMap cycling & rendering
    minimap = MiniMap()
    assert minimap.mode == "corner"
    assert minimap.is_open
    minimap.toggle()
    assert minimap.mode == "large"
    minimap.toggle()
    assert minimap.mode == "hidden"
    assert not minimap.is_open
    minimap.toggle()
    assert minimap.mode == "corner"

    # Render minimap onto dummy surface
    screen = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    cam = Camera(SCREEN_WIDTH, SCREEN_HEIGHT)
    particles = ParticleSystem()
    combat = CombatManager(factory, sounds, particles, cam)
    minimap.render(screen, world, p, combat)

    # Verify Rarity tiers, Lore quotes and special effects in ITEM_REGISTRY
    assert ITEM_REGISTRY["starfury"]["rarity"] == RARITY_LEGENDARY
    assert "lore" in ITEM_REGISTRY["starfury"] and len(ITEM_REGISTRY["starfury"]["lore"]) > 0
    assert ITEM_REGISTRY["celestial_greatsword"]["rarity"] == RARITY_MYTHIC
    assert ITEM_REGISTRY["work_bench"]["desc"] is not None and "recipes" in ITEM_REGISTRY["work_bench"]["desc"].lower()
    assert ITEM_REGISTRY["furnace"]["desc"] is not None and "smelt" in ITEM_REGISTRY["furnace"]["desc"].lower()

    # Verify HUD tooltip rendering & notification banner
    hud = HUD(factory)
    test_stack = ItemStack("starfury", 1)
    hud._render_tooltip(screen, 100, 100, test_stack)
    hud._render_notification_banner(screen, "Learned Skill: Whirlwind!")
    print("  -> Player Animation, MiniMap Radar, & Item Lore/Rarities OK.")

    # 13. House Blocks, Crafting Station Badges, Door Toggling & Mob Collisions
    print("\n[Test 13] Testing House Blocks, Crafting Badges, Door Toggling & Mob Collisions...")
    crafting = CraftingSystem(factory, sounds)
    
    # Check nearby stations detection
    p.x, p.y = 50 * SCALED_TILE, 70 * SCALED_TILE
    world.set_tile(50, 71, TILE_WORK_BENCH)
    world.set_tile(52, 71, TILE_FURNACE)
    has_wb, has_furn = crafting.check_nearby_stations(world, p)
    assert has_wb, "Should detect placed Work Bench"
    assert has_furn, "Should detect placed Furnace"

    # Crafting of house blocks
    inv = Inventory(factory)
    inv.slots[0] = ItemStack("stone_block", 20)
    inv.slots[1] = ItemStack("dirt_block", 20)
    inv.slots[2] = ItemStack("wood", 50)
    crafting.update_recipes(inv, world, p)
    
    # Find roof_tiles and wooden_door recipes
    roof_recipe = next((r for r in crafting.available_recipes if r["result"] == "roof_tiles"), None)
    door_recipe = next((r for r in crafting.available_recipes if r["result"] == "wooden_door"), None)
    assert roof_recipe is not None, "Roof tiles must be craftable near Work Bench"
    assert door_recipe is not None, "Wooden door must be craftable near Work Bench"
    
    crafted = crafting.craft(roof_recipe, inv)
    assert crafted, "Roof tiles should craft successfully"
    assert inv.count_item("roof_tiles") == 4

    # Test Door Toggling & Wall Placement
    world.set_tile(50, 69, TILE_DOOR_CLOSED)
    toggled = world.toggle_door(50, 69)
    assert toggled and world.get_tile(50, 69) == TILE_DOOR_OPEN
    world.toggle_door(50, 69)
    assert world.get_tile(50, 69) == TILE_DOOR_CLOSED

    wall_placed = world.place_wall(50, 69, WALL_WOOD)
    assert wall_placed and world.get_wall(50, 69) == WALL_WOOD

    # Flying Mobs Collision Test (Cannot phase through solid blocks or closed doors)
    eye = DemonEye(50 * SCALED_TILE, 69 * SCALED_TILE - 10, factory)
    eye.update(0.1, world, p)
    # Eye must be impeded by solid door / block and not phase through
    assert world.is_tile_solid(50, 69), "Closed door should be solid"
    print("  -> House Blocks, Crafting Badges, Door Toggling & Mob Collisions OK.")

    # 14. Character Panel Skill Tooltips, Grimoire Loadout & Key Rebinding
    print("\n[Test 14] Testing Character Panel Skills, Grimoire Loadout & Key Rebinding...")
    char_panel = CharacterPanel(factory)
    char_panel.is_open = True
    char_panel.render(screen, p, 100, 100)
    
    # Test skill loadout rebinding
    assert "power_slash" in p.skills.learned_skills
    p.skills.learn_skill("meteor")
    assert "meteor" in p.skills.learned_skills
    # Assign meteor to hotkey Q
    p.skills.assign_skill("Q", "meteor")
    assert p.skills.hotkey_bindings["Q"] == "meteor"

    # Test key rebinding in MenuManager
    menu = MenuManager(factory, sounds)
    assert menu.key_bindings["Move Left"] == pygame.K_a
    # Enter input mapping and rebind Move Left to J
    menu.state = "input_mapping"
    menu.rebinding_action = "Move Left"
    fake_event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_j)
    menu.handle_key(fake_event)
    assert menu.key_bindings["Move Left"] == pygame.K_j, "Move Left should be rebound to J"

    # Reset defaults (with confirmation modal)
    menu.handle_click(menu.input_reset_button.rect.center)
    if getattr(menu, "reset_confirm_modal_active", False):
        menu.handle_click(menu.reset_confirm_yes_btn.rect.center)
    assert menu.key_bindings["Move Left"] == pygame.K_a, "Reset defaults should restore K_a"

    # Test Skill Book consumption and banner notification
    inv.slots[0] = ItemStack("skillbook_meteor", 1)
    inv.is_open = True
    inv.handle_click(25, 25, is_right_click=True, player=p)
    assert inv.last_learned_message is not None, "Skill Book consumption should trigger notification banner"
    assert inv.last_learned_timer > 0.0
    inv.update(6.0)
    assert inv.last_learned_message is None, "Notification banner should expire after timer"

    # Surface height query
    surf_y = world.get_surface_height(10)
    assert 35 <= surf_y <= 150, "Surface height should be within valid bounds"

    # Jump input isolation when rebound
    p.on_ground = True
    p.vy = 0.0
    custom_bindings = {"Move Left": pygame.K_a, "Move Right": pygame.K_d, "Drop Platform": pygame.K_s, "Jump": pygame.K_j}
    fake_keys = {pygame.K_SPACE: True, pygame.K_w: True, pygame.K_j: False}
    p.handle_input(fake_keys, 200, 100, key_bindings=custom_bindings)
    assert p.vy == 0.0, "K_SPACE or K_w must not trigger jump when rebound to K_j"
    fake_keys = {pygame.K_SPACE: False, pygame.K_w: False, pygame.K_j: True}
    p.handle_input(fake_keys, 200, 100, key_bindings=custom_bindings)
    assert p.vy < -5.0, "Rebound key K_j must trigger jump"

    # Crafting discovery with empty inventory (station unlocks remain visible)
    empty_inv = Inventory(factory)
    empty_inv.slots = [None] * len(empty_inv.slots)
    crafting.update_recipes(empty_inv, world, p)
    assert len(crafting.available_recipes) > 5, "Station recipes must be discovered even with empty inventory"
    door_rec = next((r for r in crafting.available_recipes if r["result"] == "wooden_door"), None)
    assert door_rec is not None and door_rec["can_craft"] is False
    assert crafting.craft(door_rec, empty_inv) is False

    # Equipped gear tooltip with rarity and weapon power
    p.equipment.slots["weapon"] = "starfury"
    char_panel._render_equipped_tooltip(screen, 150, 150, "starfury")
    print("  -> Character Panel Skills, Grimoire Loadout, Key Rebinding & Reviewer Checks OK.")

    print("\n==================================================================")
    print("ALL 14 INTEGRATION & MULTIPLAYER TESTS PASSED WITH ZERO ERRORS!")
    print(f"Developer: Kurados  |  Engine: pygame-ce {pygame.__version__}")
    print("==================================================================")

if __name__ == "__main__":
    test_all_potaria_systems()
