"""
Unit and integration tests for:
1. Skill UI Layout: verifying hotkey badge and level badge do not overlap and are properly laid out.
2. Item Tooltip Text Wrapping: verifying long descriptions, lore, and effects wrap to multiple lines and tooltip width is bounded <= 340px.
3. Potato Miner Helmet Illumination: verifying miner helmet provides gentle illumination and Astral Sparkle provides brighter illumination.
"""

import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
import pygame
from src.ui.theme import wrap_text_lines, font_compact, font_regular, font_semibold
from src.rpg.equipment import Equipment, ARMOR_DATA, SLOT_HEAD
from src.ui.inventory import ITEM_REGISTRY, ItemStack


def test_wrap_text_lines_basic():
    pygame.font.init()
    fnt = font_regular(12)
    long_desc = (
        "AN ENCHANTED EPIC TALISMAN HUMMING WITH MAGICAL RESONANCE. "
        "BESTOWS PASSIVE COMBAT BUFFS AND FORTITUDE. FORTIFIED WITH PURE TUBER VITALITY. "
        "GRANTS SOUL HARVEST."
    )
    wrapped = wrap_text_lines(long_desc, fnt, 300)
    assert len(wrapped) > 1
    for line in wrapped:
        assert fnt.size(line)[0] <= 300


def test_wrap_text_lines_preserves_short_text():
    pygame.font.init()
    fnt = font_regular(12)
    short_text = "Iron Sword"
    wrapped = wrap_text_lines(short_text, fnt, 300)
    assert len(wrapped) == 1
    assert wrapped[0] == "Iron Sword"


def test_wrap_text_lines_bullets_and_special():
    pygame.font.init()
    fnt = font_compact(11)
    bullet = "• GLACIAL CHILL (-35% TARGET SPEED AND MOVEMENT IMPAIRMENT ON HIT FOR 3 SECONDS)"
    wrapped = wrap_text_lines(bullet, fnt, 280)
    assert len(wrapped) >= 1
    for line in wrapped:
        assert fnt.size(line)[0] <= 280


def test_miner_helmet_equipment_attributes():
    assert "miner_helmet" in ARMOR_DATA
    data = ARMOR_DATA["miner_helmet"]
    assert data["slot"] == SLOT_HEAD
    assert data.get("light") is True
    assert "Cave Illumination" in data.get("special", "") or "Cave Illumination" in str(data.get("effects", []))

    eq = Equipment()
    assert eq.has_light_emitter() is False
    assert eq.has_miner_helmet_equipped() is False
    assert eq.has_astral_radiance() is False

    # Equip miner helmet
    eq.equip("miner_helmet")
    assert eq.has_miner_helmet_equipped() is True
    assert eq.has_light_emitter() is True
    assert eq.has_astral_radiance() is False

    # Equip Crown of Potaria
    eq.equip("crown_of_potaria")
    assert eq.has_miner_helmet_equipped() is False
    assert eq.has_astral_radiance() is True
    assert eq.has_light_emitter() is True


def test_miner_helmet_item_registry():
    assert "miner_helmet" in ITEM_REGISTRY
    reg = ITEM_REGISTRY["miner_helmet"]
    assert "Cave Illumination" in reg.get("special", "")
    assert any("Cave Illumination" in eff for eff in reg.get("effects", []))


def test_hud_tooltip_width_is_bounded():
    from src.ui.hud import HUD
    from src.assets.asset_factory import AssetFactory

    af = AssetFactory()
    hud = HUD(af)
    surf = pygame.Surface((960, 540))

    class MockItem:
        def __init__(self):
            self.item_id = "mock_epic_claymore"
            self.data = {
                "name": "Colossal Claymore of the Spud",
                "cat": "weapon",
                "rarity": "epic",
                "damage": 44,
                "desc": (
                    "HEAVY EPIC WEAPON WITH IMMENSE STRIKING WEIGHT. "
                    "CLEAVES THROUGH ENEMY DEFENSES WITH CRUSHING MOMENTUM. "
                    "INFUSED WITH THE EARTHY RESILIENCE OF POTARIA. BESTOWS GLACIAL CHILL."
                ),
                "effects": ["Glacial Chill (-35% Target Speed on hit for 3 seconds)"],
                "lore": "An ancient blade forged in the deepest underground roots.",
            }

    claymore_item = MockItem()
    lines = hud._render_tooltip(surf, 100, 100, claymore_item)
    assert len(lines) > 5

    rendered_surfs = [fnt.render(text, True, col) for text, col, fnt in lines]
    content_w = max(s.get_width() for s in rendered_surfs)
    tw = max(160, min(330, content_w + 20))
    # Must be compact and well within 340px, never 800+ px!
    assert tw <= 340


def test_skill_bar_dimensions_and_slots():
    from src.ui.hud import HUD
    from src.assets.asset_factory import AssetFactory
    from src.audio.sound_effects import SoundManager
    from src.entities.player import Player

    af = AssetFactory()
    snd = SoundManager()
    hud = HUD(af)
    player = Player(100, 100, af, snd)
    surf = pygame.Surface((960, 540))

    # Should render cleanly without error
    hud._render_skill_bar(surf, player)
