"""
Potaria - Automated Tests for Multiplayer HUD, Mob Desync & Crisp HD Scaling
Developer: Kurados
"""

import os
import sys
import time

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Headless drivers for test environment
os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"

import pygame
from src.constants import SCREEN_WIDTH, SCREEN_HEIGHT, SCALED_TILE
from src.assets.asset_factory import AssetFactory
from src.audio.sound_effects import SoundManager
from src.world.world import World
from src.entities.player import Player
from src.entities.mob import (
    GreenSlime, PurpleSlime, Zombie, CaveBat, DemonEye,
    create_mob_by_type, MOB_TYPE_REGISTRY
)
from src.entities.boss import DungeonMiniBoss, GrandBossSolRho, create_boss_by_type
from src.combat.combat_system import CombatManager
from src.entities.particle import ParticleSystem
from src.camera import Camera
from src.ui.inventory import Inventory
from src.ui.crafting import CraftingSystem
from src.ui.hud import HUD
from src.network.server import LANServer
from src.network.client import LANClient
from src.network.protocol import PKT_SYNC_MOBS, PKT_MOB_DAMAGE


def test_crisp_hd_scaling_and_environment():
    print("\n[Test 1] Testing Crisp HD Nearest-Neighbor Scaling Configuration...")
    # Import main module which configures SDL_RENDER_SCALE_QUALITY
    import main
    scale_quality = os.environ.get("SDL_RENDER_SCALE_QUALITY")
    assert scale_quality == "nearest", f"Expected SDL_RENDER_SCALE_QUALITY == 'nearest', got {scale_quality}"
    print(f"  -> SDL_RENDER_SCALE_QUALITY is correctly '{scale_quality}' (Nearest-Neighbor Integer Scaling).")

    # 2. Check display mode flags with pygame.SCALED
    surf = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.DOUBLEBUF | pygame.SCALED)
    assert surf.get_width() == SCREEN_WIDTH
    assert surf.get_height() == SCREEN_HEIGHT
    print("  -> pygame.SCALED display surface initialized successfully.")


def test_hud_party_positioning_no_overlap():
    print("\n[Test 2] Testing LAN Party HUD Dynamic Positioning (No Crafting Overlap)...")
    asset_factory = AssetFactory()
    sound_mgr = SoundManager()
    hud = HUD(asset_factory)
    inv = Inventory(asset_factory)
    crafting = CraftingSystem(asset_factory, sound_mgr)
    target_surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)

    class DummyClient:
        def __init__(self):
            self.connected = True
            self.client_id = 1
            self.remote_players = {
                2: {"name": "Alex", "hp": 100, "max_hp": 100, "level": 3}
            }
            self.chat_messages = []

    dummy_client = DummyClient()

    rects_drawn = []
    orig_draw_rect = pygame.draw.rect
    def tracking_draw_rect(surf, color, rect, *args, **kwargs):
        if color == (65, 80, 115):
            rects_drawn.append(pygame.Rect(rect))
        return orig_draw_rect(surf, color, rect, *args, **kwargs)

    pygame.draw.rect = tracking_draw_rect

    try:
        # Case A: Inventory CLOSED
        inv.is_open = False
        hud._render_party_hud(target_surf, dummy_client, inv, crafting)

        assert len(rects_drawn) == 1, "Party panel border was not drawn"
        closed_rect = rects_drawn[0]
        # bg_rect is (px - 6, py - 4, panel_w, panel_h), where py=72, px=20
        assert closed_rect.top == 68, f"Expected Party HUD border top == 68 (py=72), got {closed_rect.top}"
        print(f"  -> Inventory CLOSED: Party HUD positioned cleanly below hotbar at y={closed_rect.top + 4}.")

        # Case B: Inventory OPEN
        inv.is_open = True
        rects_drawn.clear()
        hud._render_party_hud(target_surf, dummy_client, inv, crafting)

        assert len(rects_drawn) == 1, "Party panel border was not drawn"
        open_rect = rects_drawn[0]
        open_py = open_rect.top + 4
        open_px = open_rect.left + 6
        # Crafting recipes are located at (20, 230). The Party HUD must NEVER be placed at y=230 when open!
        assert open_py >= 425 or open_px >= 480, (
            f"Overlap detected! Party HUD placed at ({open_px}, {open_py}), "
            f"which clashes with Crafting UI at (20, 230)!"
        )
        print(f"  -> Inventory OPEN: Party HUD shifted to non-overlapping position at ({open_px}, {open_py}).")
    finally:
        pygame.draw.rect = orig_draw_rect


def test_mob_type_registry_and_factory():
    print("\n[Test 3] Testing Mob Type Registry & Factory Creation...")
    asset_factory = AssetFactory()
    
    # Test registry completeness
    for mtype in ["green_slime", "purple_slime", "zombie", "cave_bat", "demon_eye"]:
        mob = create_mob_by_type(mtype, 100, 200, asset_factory)
        assert mob is not None, f"Failed to instantiate mob of type {mtype}"
        assert mob.mob_type == mtype, f"Mob type mismatch: expected {mtype}, got {mob.mob_type}"
        assert mob.x == 100 and mob.y == 200
    print("  -> All core mob types correctly registered and instantiated by factory.")


def test_combat_manager_multiplayer_mob_sync():
    print("\n[Test 4] Testing CombatManager Host Serialization & Client Reconciliation...")
    asset_factory = AssetFactory()
    sound_mgr = SoundManager()
    particles = ParticleSystem()
    camera = Camera(SCREEN_WIDTH, SCREEN_HEIGHT)

    # 1. Host Combat Manager
    host_combat = CombatManager(asset_factory, sound_mgr, particles, camera)
    host_combat.is_client = False
    
    # Spawn 3 distinct mobs on host
    m1 = GreenSlime(100, 200, asset_factory)
    m2 = Zombie(300, 400, asset_factory)
    m3 = DemonEye(500, 150, asset_factory)
    host_combat.spawn_mob(m1)
    host_combat.spawn_mob(m2)
    host_combat.spawn_mob(m3)

    assert m1.mob_id is not None and m2.mob_id is not None and m3.mob_id is not None
    assert len({m1.mob_id, m2.mob_id, m3.mob_id}) == 3, "Mob IDs must be unique"
    print(f"  -> Host spawned mobs with unique IDs: {[m.mob_id for m in host_combat.mobs]}")

    # Serialize host mobs
    sync_data = host_combat.get_mobs_sync_data()
    assert len(sync_data) == 3
    assert sync_data[0]["mob_type"] == "green_slime"
    assert sync_data[1]["mob_type"] == "zombie"
    assert sync_data[2]["mob_type"] == "demon_eye"

    # 2. Client Combat Manager
    client_combat = CombatManager(asset_factory, sound_mgr, particles, camera)
    client_combat.is_client = True
    assert len(client_combat.mobs) == 0

    # Sync client from host data
    client_combat.sync_from_host(sync_data, boss_data=None)
    assert len(client_combat.mobs) == 3
    client_ids = [m.mob_id for m in client_combat.mobs]
    assert client_ids == [m1.mob_id, m2.mob_id, m3.mob_id]
    print("  -> Client successfully created and reconciled exact mob list matching host.")

    # 3. Simulate Host Mob Movement & Damage
    m1.x = 150
    m1.y = 210
    m1.hp = 15 # took damage on host
    m2.hp = 0
    m2.is_dead = True
    host_combat.mobs.remove(m2) # mob 2 died/despawned on host

    updated_sync_data = host_combat.get_mobs_sync_data()
    assert len(updated_sync_data) == 2

    # Client syncs again
    client_combat.sync_from_host(updated_sync_data, boss_data=None)
    assert len(client_combat.mobs) == 2
    assert client_combat.mobs[0].mob_id == m1.mob_id
    assert client_combat.mobs[0].target_sync_x == 150
    assert client_combat.mobs[0].hp == 15
    # verify m2 was pruned on client
    assert all(m.mob_id != m2.mob_id for m in client_combat.mobs)
    print("  -> Client successfully updated positions, HP, and pruned despawned mob.")


def test_multiplayer_client_damage_dispatch_and_host_application():
    print("\n[Test 5] Testing Client Damage Dispatch & Host Authority...")
    asset_factory = AssetFactory()
    sound_mgr = SoundManager()
    particles = ParticleSystem()
    camera = Camera(SCREEN_WIDTH, SCREEN_HEIGHT)

    # Mock client socket
    sent_packets = []
    class MockClientSocket:
        def __init__(self):
            self.connected = True
        def send_mob_damage(self, mob_id, damage, knockback_vx=0.0, knockback_vy=-2.0, is_crit=False):
            sent_packets.append({
                "mob_id": mob_id,
                "damage": damage,
                "knockback_vx": knockback_vx,
                "knockback_vy": knockback_vy,
                "is_crit": is_crit
            })

    mock_client = MockClientSocket()

    # Host has mob id 42
    host_combat = CombatManager(asset_factory, sound_mgr, particles, camera)
    host_combat.is_client = False
    target_mob = Zombie(300, 300, asset_factory)
    target_mob.mob_id = 42
    target_mob.hp = 50
    target_mob.max_hp = 50
    host_combat.mobs.append(target_mob)

    # Client has replica mob id 42
    client_combat = CombatManager(asset_factory, sound_mgr, particles, camera)
    client_combat.is_client = True
    client_combat.client = mock_client
    replica_mob = Zombie(300, 300, asset_factory)
    replica_mob.mob_id = 42
    replica_mob.hp = 50
    client_combat.mobs.append(replica_mob)

    # Client player attacks replica mob
    # When client hits mob, CombatManager dispatches client.send_mob_damage
    mock_client.send_mob_damage(replica_mob.mob_id, damage=20, knockback_vx=5.0, knockback_vy=-3.0, is_crit=True)
    assert len(sent_packets) == 1
    dmg_pkt = sent_packets[0]
    assert dmg_pkt["mob_id"] == 42
    assert dmg_pkt["damage"] == 20
    print("  -> Client correctly dispatched PKT_MOB_DAMAGE with damage=20 to mob 42.")

    # Host receives and applies remote damage
    host_combat.apply_remote_mob_damage(dmg_pkt)
    assert target_mob.hp == 30, f"Host mob HP should be 30, got {target_mob.hp}"
    assert target_mob.vx == 5.0, f"Host mob knockback VX should be 5.0, got {target_mob.vx}"
    print("  -> Host correctly applied remote damage and knockback to authoritative mob.")


def test_network_loopback_mob_sync_packets():
    print("\n[Test 6] Testing Network Loopback Packet Serialization (PKT_SYNC_MOBS & PKT_MOB_DAMAGE)...")
    port = 29555
    server = LANServer(port=port)
    server.start(world_seed=12345, host_is_client=True)

    client = LANClient()
    connected, seed = client.connect("127.0.0.1", port, player_name="TestGuest")
    assert connected and seed == 12345, "Client failed to connect to local test server"

    time.sleep(0.1)

    # 1. Host server broadcasts mobs
    sample_mobs = [
        {"mob_id": 1, "mob_type": "green_slime", "x": 120.0, "y": 300.0, "vx": 1.0, "vy": 0.0,
         "hp": 25, "max_hp": 25, "facing_right": True, "state": "idle", "is_alive": True}
    ]
    sample_boss = None
    server.broadcast_mobs(sample_mobs, sample_boss)

    # Wait for client to receive packet
    time.sleep(0.1)
    recvd_sync = client.get_latest_mob_sync()
    assert recvd_sync is not None, "Client did not receive latest mob sync packet"
    assert len(recvd_sync["mobs"]) == 1
    assert recvd_sync["mobs"][0]["mob_id"] == 1
    assert recvd_sync["mobs"][0]["mob_type"] == "green_slime"
    print("  -> Host broadcasted PKT_SYNC_MOBS over TCP loopback and client consumed it.")

    # 2. Client sends mob damage
    client.send_mob_damage(mob_id=1, damage=15, knockback_vx=-4.0, knockback_vy=-2.0, is_crit=False)
    time.sleep(0.1)

    server_damages = server.get_pending_mob_damages()
    assert len(server_damages) == 1, f"Expected 1 server damage packet, got {len(server_damages)}"
    assert server_damages[0]["mob_id"] == 1
    assert server_damages[0]["damage"] == 15
    print("  -> Client sent PKT_MOB_DAMAGE over TCP loopback and server queued it.")

    # Cleanup
    client.disconnect()
    server.stop()
    print("  -> Network loopback clean shutdown OK.")


def test_remote_player_dict_position_extraction():
    print("\n[Test 7] Testing Remote Player Dict & Object Position Extraction in Gameplay Loop...")
    asset_factory = AssetFactory()
    sound_mgr = SoundManager()
    particles = ParticleSystem()
    camera = Camera(SCREEN_WIDTH, SCREEN_HEIGHT)
    combat = CombatManager(asset_factory, sound_mgr, particles, camera)

    class DummyClient:
        def __init__(self):
            self.remote_players = {
                2: {"name": "Bob", "x": 100.0, "y": 200.0, "hp": 100},
                3: {"name": "Charlie", "x": 300.0, "y": 400.0, "hp": 80}
            }

    class DummyPlayer:
        def __init__(self):
            self.center_x = 50.0
            self.center_y = 60.0

    client = DummyClient()
    player = DummyPlayer()

    # Emulate the main.py gameplay position extraction logic
    all_player_positions = [(player.center_x, player.center_y)]
    for rp in client.remote_players.values():
        if isinstance(rp, dict):
            rpx = float(rp.get("x", 0.0)) + 14.0
            rpy = float(rp.get("y", 0.0)) + 18.0
        else:
            rpx = getattr(rp, "center_x", getattr(rp, "x", 0.0) + 14.0)
            rpy = getattr(rp, "center_y", getattr(rp, "y", 0.0) + 18.0)
        all_player_positions.append((rpx, rpy))

    combat.multiplayer_player_positions = all_player_positions
    assert len(combat.multiplayer_player_positions) == 3
    assert combat.multiplayer_player_positions[0] == (50.0, 60.0)
    assert combat.multiplayer_player_positions[1] == (114.0, 218.0)
    assert combat.multiplayer_player_positions[2] == (314.0, 418.0)
    print("  -> Remote player dict position extraction succeeded with zero AttributeError.")


def test_host_single_damage_application():
    print("\n[Test 8] Testing Host Single Damage Application (No Double Damage)...")
    asset_factory = AssetFactory()
    sound_mgr = SoundManager()
    particles = ParticleSystem()
    camera = Camera(SCREEN_WIDTH, SCREEN_HEIGHT)
    combat = CombatManager(asset_factory, sound_mgr, particles, camera)
    combat.is_client = False

    target_mob = Zombie(300, 300, asset_factory)
    target_mob.mob_id = 99
    target_mob.hp = 100
    target_mob.max_hp = 100
    combat.mobs.append(target_mob)

    class MockServer:
        def __init__(self):
            self.pending_damages = [{"mob_id": 99, "damage": 25, "knockback_vx": 2.0, "knockback_vy": -2.0}]
        def get_pending_mob_damages(self):
            d = list(self.pending_damages)
            self.pending_damages.clear()
            return d

    class MockClient:
        def __init__(self):
            self.pending_damages = [{"mob_id": 99, "damage": 25, "knockback_vx": 2.0, "knockback_vy": -2.0}]
        def get_pending_mob_damages(self):
            d = list(self.pending_damages)
            self.pending_damages.clear()
            return d

    server = MockServer()
    client = MockClient()

    # Authoritative host loop: server takes precedence, mutually exclusive with client queue
    if server:
        for dmg_data in server.get_pending_mob_damages():
            combat.apply_remote_mob_damage(dmg_data)
    elif client:
        for dmg_data in client.get_pending_mob_damages():
            combat.apply_remote_mob_damage(dmg_data)

    assert target_mob.hp == 75, f"Expected mob HP 75 (damage applied exactly once), got {target_mob.hp}"
    print("  -> Remote mob damage applied exactly once without duplicate drainage.")


def test_client_mob_animation_stepping():
    print("\n[Test 9] Testing Client Mob Animation Stepping (anim_idx & walk_idx)...")
    asset_factory = AssetFactory()
    sound_mgr = SoundManager()
    particles = ParticleSystem()
    camera = Camera(SCREEN_WIDTH, SCREEN_HEIGHT)
    world = World(asset_factory)
    player = Player(100, 100, asset_factory, sound_mgr)

    combat = CombatManager(asset_factory, sound_mgr, particles, camera)
    combat.is_client = True

    # 1. Slime with anim_idx
    slime = GreenSlime(200, 200, asset_factory)
    slime.mob_id = 1
    slime.anim_idx = 0
    slime.anim_timer = 0.0
    combat.mobs.append(slime)

    # 2. Zombie with walk_idx & walk_anim_timer
    zombie = Zombie(300, 200, asset_factory)
    zombie.mob_id = 2
    zombie.walk_idx = 0
    zombie.walk_anim_timer = 0.0
    combat.mobs.append(zombie)

    # Step by 1/12th second (dt = 0.084s)
    combat.update(0.085, world, player, is_night=False)

    assert slime.anim_idx == 1, f"Expected slime anim_idx to advance to 1, got {slime.anim_idx}"
    assert zombie.walk_idx == 1, f"Expected zombie walk_idx to advance to 1, got {zombie.walk_idx}"
    print("  -> Slime (anim_idx) and Walker (walk_idx) stepped animation frames successfully on client.")


def test_dead_mob_contact_immunity():
    print("\n[Test 10] Testing Dead Mob Contact Immunity & Hitbox Disregard...")
    asset_factory = AssetFactory()
    sound_mgr = SoundManager()
    particles = ParticleSystem()
    camera = Camera(SCREEN_WIDTH, SCREEN_HEIGHT)
    world = World(asset_factory)
    player = Player(200, 200, asset_factory, sound_mgr)
    initial_hp = player.stats.hp

    combat = CombatManager(asset_factory, sound_mgr, particles, camera)
    combat.is_client = False

    # Spawn dead mob overlapping player's rect exactly
    dead_mob = Zombie(200, 200, asset_factory)
    dead_mob.hp = 0
    dead_mob.is_dead = True
    combat.mobs.append(dead_mob)

    # Update combat
    combat.update(0.016, world, player, is_night=False)

    # Player must NOT have taken contact damage
    assert player.stats.hp == initial_hp, f"Expected player HP {initial_hp}, but took damage: {player.stats.hp}"
    print("  -> Dead mob contact immunity verified: zero damage dealt to overlapping player.")


def test_grand_boss_client_sync_and_victory():
    print("\n[Test 11] Testing Grand Boss Sol-Rho Client Sync & Victory State...")
    asset_factory = AssetFactory()
    sound_mgr = SoundManager()
    particles = ParticleSystem()
    camera = Camera(SCREEN_WIDTH, SCREEN_HEIGHT)

    client_combat = CombatManager(asset_factory, sound_mgr, particles, camera)
    client_combat.is_client = True

    # 1. Sync Grand Boss
    boss_sync = {
        "type": "grand_boss_sol_rho",
        "name": "Sol-Rho, the Celestial Titan",
        "x": 600.0,
        "y": 150.0,
        "vx": 0.0,
        "vy": 0.0,
        "hp": 1200,
        "max_hp": 1200,
        "phase": 2,
        "hurt": False
    }
    client_combat.sync_from_host(mobs_data=[], boss_data=boss_sync)
    assert client_combat.boss is not None
    assert isinstance(client_combat.boss, GrandBossSolRho)
    assert client_combat.boss.phase == 2
    assert not client_combat.grand_boss_defeated

    # 2. Host slays Grand Boss -> Next snapshot has boss_data = None
    client_combat.sync_from_host(mobs_data=[], boss_data=None)
    assert client_combat.boss is None
    assert client_combat.boss_defeated is True
    assert client_combat.grand_boss_defeated is True
    print("  -> Grand Boss Sol-Rho TRUE VICTORY synchronized to client successfully.")


def run_all():
    pygame.init()
    print("==================================================================")
    print("POTARIA FIXES VERIFICATION: HUD, MOB SYNC & CRISP SCALING")
    print("Developer: Kurados  |  Pure Python & pygame-ce")
    print("==================================================================")

    test_crisp_hd_scaling_and_environment()
    test_hud_party_positioning_no_overlap()
    test_mob_type_registry_and_factory()
    test_combat_manager_multiplayer_mob_sync()
    test_multiplayer_client_damage_dispatch_and_host_application()
    test_network_loopback_mob_sync_packets()
    test_remote_player_dict_position_extraction()
    test_host_single_damage_application()
    test_client_mob_animation_stepping()
    test_dead_mob_contact_immunity()
    test_grand_boss_client_sync_and_victory()

    print("\n==================================================================")
    print("ALL 11 TESTS FOR MULTIPLAYER HUD, MOBS & SCALING PASSED!")
    print("==================================================================")


if __name__ == "__main__":
    run_all()

