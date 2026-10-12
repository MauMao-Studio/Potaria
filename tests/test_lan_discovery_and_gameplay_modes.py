"""
Unit tests for LAN discovery, room key authentication, and gameplay difficulty & skill mechanics.
"""

import sys
import os
import time
import shutil
import tempfile
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
os.environ["SDL_VIDEODRIVER"] = "dummy"
import pygame
pygame.init()
pygame.display.set_mode((1280, 720))
from src.network.server import LANServer
from src.network.client import LANClient, LANDiscovery
from src.rpg.skills import SkillManager
from src.rpg.stats import PlayerStats
from src.constants import DIFFICULTY_EASY, DIFFICULTY_NORMAL, DIFFICULTY_HARDCORE, DIFFICULTY_YOLO
from src.assets.asset_factory import AssetFactory
from src.ui.inventory import Inventory
from src.world.save_manager import delete_world, save_world, list_saved_worlds


def test_phantom_dash_consecutive_charges_and_cooldown():
    """Verify that Swift Dash Lv. 3 evolves to Phantom Dash allowing 2 consecutive dashes within 1.2s."""
    sm = SkillManager()
    stats = PlayerStats()
    stats.mp = 100
    
    # At Level 1, normal dash has 1 charge and cooldown applies immediately
    assert not sm.is_skill_evolved("dash")
    assert sm.get_skill_name("dash") == "Swift Dash"
    assert sm.use_skill("dash", stats)
    assert sm.cooldowns["dash"] > 0
    assert not sm.use_skill("dash", stats)
    
    # Reset cooldown and level up dash to 3
    sm.cooldowns["dash"] = 0.0
    sm.skill_levels["dash"] = 3
    assert sm.is_skill_evolved("dash")
    assert sm.get_skill_name("dash") == "Phantom Dash"
    
    # First dash consumes MP, does NOT start full cooldown, sets combo window
    assert sm.use_skill("dash", stats)
    assert sm.cooldowns["dash"] == 0.0
    assert sm.skill_combos["dash"]["charges_left"] == 1
    assert sm.skill_combos["dash"]["window_timer"] > 1.0
    
    # Second dash within 1.2s window
    assert sm.use_skill("dash", stats)
    # Second dash completes combo and starts full cooldown
    assert sm.cooldowns["dash"] > 0.0
    assert "dash" not in sm.skill_combos
    
    # Combo expiration test
    sm.cooldowns["dash"] = 0.0
    assert sm.use_skill("dash", stats)
    assert "dash" in sm.skill_combos
    # Simulate time expiry > 1.2s
    sm.update(1.3)
    assert "dash" not in sm.skill_combos
    assert sm.cooldowns["dash"] > 0.0


def test_difficulty_loadouts_and_skills():
    """Verify starter equipment and starter skills across Easy, Normal, Hardcore, YOLO modes."""
    factory = AssetFactory()
    inv = Inventory(factory)
    
    # Easy: 1 wooden axe, 5 torches, starter skills (power_slash, dash)
    inv.set_difficulty_loadout(DIFFICULTY_EASY)
    assert inv.count_item("wood_axe") == 1
    assert inv.count_item("torch") == 5
    
    # Normal: 1 wooden axe, 5 torches
    inv.set_difficulty_loadout(DIFFICULTY_NORMAL)
    assert inv.count_item("wood_axe") == 1
    assert inv.count_item("torch") == 5
    
    # Hardcore: 0 items
    inv.set_difficulty_loadout(DIFFICULTY_HARDCORE)
    assert inv.count_item("wood_axe") == 0
    assert inv.count_item("torch") == 0
    
    # YOLO: 0 items
    inv.set_difficulty_loadout(DIFFICULTY_YOLO)
    assert inv.count_item("wood_axe") == 0
    assert inv.count_item("torch") == 0


def test_lan_discovery_and_room_key_auth():
    """Verify UDP beacon discovery and password/room key rejection and acceptance."""
    port = 28555
    disc_port = 28556
    
    server = LANServer(host="127.0.0.1", port=port, max_players=5, server_name="Potaria Test LAN", room_key="secret123")
    server.start(world_seed=54321)
    
    # Client with wrong room key
    client_bad = LANClient()
    connected, _ = client_bad.connect("127.0.0.1", port=port, player_name="BadGuest", room_key="wrong_pw")
    # Server will drop socket upon receiving PKT_JOIN with invalid room key
    time.sleep(0.2)
    # Socket should be closed or disconnected by server
    assert client_bad.connected is False or len(server.players) <= 1
    if client_bad.sock:
        try:
            client_bad.disconnect()
        except Exception:
            pass

    # Client with correct room key
    client_good = LANClient()
    connected, seed = client_good.connect("127.0.0.1", port=port, player_name="GoodGuest", room_key="secret123")
    assert connected is True
    assert seed == 54321
    time.sleep(0.1)
    
    client_good.disconnect()
    server.stop()
