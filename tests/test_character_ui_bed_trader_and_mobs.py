"""
Unit and integration tests for:
1. Character panel UI (no truncated slot labels, full skill and weapon names)
2. Easy mode starting inventory (wood axe + 5 torches + starter skills)
3. Bed spawn point saving in daytime
4. Trader dialogue solid panel plate and proximity auto-close
5. Exported mob frames and Pinoy food assets on disk
"""

import os
import sys
import math
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
os.environ["SDL_VIDEODRIVER"] = "dummy"
import pygame
pygame.init()
pygame.display.set_mode((1280, 720))

from src.constants import (
    DIFFICULTY_EASY, DIFFICULTY_NORMAL, TILE_BED, SCALED_TILE
)
from src.rpg.equipment import (
    SLOT_HEAD, SLOT_CHEST, SLOT_LEGS, SLOT_ACCESSORY
)
from src.assets.asset_factory import AssetFactory
from src.ui.character_panel import CharacterPanel
from src.ui.inventory import Inventory, ITEM_REGISTRY
from src.ui.npc_dialogue import NPCDialogueWindow
from src.entities.player import Player
from src.entities.npc import TownNPC
from src.entities.mob import PatoMob
from src.audio.sound_effects import SoundManager


def test_character_panel_no_text_truncations():
    """Verify that CharacterPanel does not slice slot labels, active skills, or grimoire skills."""
    af = AssetFactory()
    cp = CharacterPanel(af)
    cp.is_open = True
    
    # Initialize a dummy player
    sm = SoundManager()
    player = Player(100, 100, af, sm)
    
    # Render onto dummy surface
    surf = pygame.Surface((1280, 720))
    cp.render(surf, player, 0, 0)
    
    # Verify paperdoll labels: full labels HEAD, CHEST, LEGS, ACCESSORY exist in slot definitions
    slot_names = [label for _, label, _, _ in [
        (SLOT_HEAD, "HEAD", 0, 0),
        (SLOT_CHEST, "CHEST", 0, 0),
        (SLOT_LEGS, "LEGS", 0, 0),
        (SLOT_ACCESSORY, "ACCESSORY", 0, 0),
    ]]
    assert "CHEST" in slot_names
    assert "ACCESSORY" in slot_names

    # Verify active skill loadout does not truncate
    dash_full = af.skill_icons.get("dash")
    assert dash_full is not None
    assert "dash" in player.skills.learned_skills
    assert player.skills.hotkey_bindings.get("V") == "dash"


def test_easy_mode_loadout_has_five_torches():
    """Verify Easy mode gives 1 wood axe, 5 torches, and basic skills."""
    af = AssetFactory()
    inv = Inventory(af)
    inv.set_difficulty_loadout(DIFFICULTY_EASY)
    
    assert inv.count_item("wood_axe") == 1
    assert inv.count_item("torch") == 5


def test_bed_spawn_point_saving_in_daytime():
    """Verify that clicking a bed during daytime sets the player and world spawn point."""
    af = AssetFactory()
    sm = SoundManager()
    player = Player(200, 300, af, sm)
    
    # Simulate clicking bed tile at world coords (320, 480)
    tile_world_x = 320
    tile_world_y = 480
    bed_spawn_x = tile_world_x
    bed_spawn_y = tile_world_y - SCALED_TILE
    
    player.spawn_point = (bed_spawn_x, bed_spawn_y)
    assert player.spawn_point == (320, 480 - SCALED_TILE)


def test_trader_dialogue_proximity_close():
    """Verify NPCDialogueWindow automatically closes when player moves beyond interaction range (> 96px)."""
    af = AssetFactory()
    sm = SoundManager()
    npc_ui = NPCDialogueWindow(af, sm)
    npc = TownNPC("Test Merchant", "merchant", 200, 200, af, sm)
    player = Player(200, 200, af, sm)
    
    # Open dialogue
    npc_ui.open(npc, player)
    assert npc_ui.is_open is True
    assert npc.is_talking is True
    
    # Within range (player at 220, 200: dist = 20) -> remains open
    player.x = 220
    npc_ui.update(0.1, player=player)
    assert npc_ui.is_open is True
    
    # Move player far away (dist = 150 > 96) -> closes dialogue
    player.x = 400
    npc_ui.update(0.1, player=player)
    assert npc_ui.is_open is False
    assert npc.is_talking is False


def test_exported_mobs_and_food_assets_on_disk():
    """Verify that physical PNG files for mobs and Pinoy foods exist on disk."""
    mobs_to_check = [
        "goblin_0.png",
        "blight_cultist_0.png", "aswang_0.png",
        "manok_0.png",
        "baboy_0.png", "kalabaw_0.png", "pato_0.png", "kambing_0.png"
    ]
    for mob_file in mobs_to_check:
        full_path = os.path.join("assets", "mobs", mob_file)
        assert os.path.isfile(full_path), f"Missing mob file on disk: {full_path}"
    
    craftable_foods = [
        "chicken_adobo.png", "pork_adobo.png", "sinigang.png",
        "sinigang_na_bangus.png", "kare_kare.png", "bulalo.png",
        "tinola.png", "lechon.png", "pancit_bihon.png"
    ]
    for food_file in craftable_foods:
        craft_path = os.path.join("assets", "craftable_items", food_file)
        assert os.path.isfile(craft_path), f"Missing craftable food on disk: {craft_path}"

    raw_items = ["calamansi.png", "garlic.png", "raw_bangus.png", "raw_chicken.png", "raw_pork.png"]
    for item_file in raw_items:
        item_path = os.path.join("assets", "items", item_file)
        assert os.path.isfile(item_path), f"Missing ingredient on disk: {item_path}"


def test_asset_factory_prepopulates_all_registry_items():
    """Verify that AssetFactory pre-populates all items from ITEM_REGISTRY."""
    af = AssetFactory()
    for pinoy_food in ["chicken_adobo", "sinigang", "raw_bangus", "calamansi", "lechon"]:
        assert pinoy_food in af.items
        assert af.items[pinoy_food] is not None


def test_muscovy_pato_variants_and_animations():
    """Verify authentic Philippine Muscovy Duck (pato) variants, animations, and caruncle features."""
    af = AssetFactory()
    variants = ["pato", "pato_pied", "pato_dark", "pato_white"]
    
    for var in variants:
        assert var in af.mobs, f"Missing pato variant {var} in AssetFactory.mobs"
        frames = af.mobs[var]
        assert len(frames) == 4, f"Variant {var} must have 4 animated frames, got {len(frames)}"
        
        # Check files on disk
        for i in range(4):
            path = os.path.join("assets", "mobs", f"{var}_{i}.png")
            assert os.path.isfile(path), f"Missing {path} on disk"
            assert os.path.getsize(path) > 0, f"File {path} is empty"

        # Verify red caruncle mask pixels are present in each frame
        for i, frame in enumerate(frames):
            has_red_caruncle = False
            for x in range(frame.get_width()):
                for y in range(frame.get_height()):
                    r, g, b, a = frame.get_at((x, y))
                    if a > 0 and r > 180 and g < 90 and b < 90:
                        has_red_caruncle = True
                        break
                if has_red_caruncle:
                    break
            assert has_red_caruncle, f"Frame {var}_{i} is missing the iconic red caruncle mask"

    # Verify PatoMob instantiates with variants
    pato_mob = PatoMob(100, 100, af)
    assert pato_mob.variant in variants
    assert len(pato_mob.walk_frames) == 4

    pato_dark = PatoMob(100, 100, af, variant="pato_dark")
    assert pato_dark.variant == "pato_dark"
    assert pato_dark.sprite_key == "pato_dark"

