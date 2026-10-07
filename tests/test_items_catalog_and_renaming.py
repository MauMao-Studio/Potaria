"""
Potaria - Anti-Plagiarism Renaming & 1000+ Items Catalog Verification Suite
Developer: Kurados | Pure Python & pygame-ce
"""

import os
import sys
import json

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Initialize headless pygame for testing
os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"
import pygame
pygame.init()

from src.constants import (
    SCREEN_WIDTH, SCREEN_HEIGHT,
    RARITY_COMMON, RARITY_UNCOMMON, RARITY_RARE, RARITY_EPIC,
    RARITY_MYTHIC, RARITY_LEGENDARY, RARITY_ANCIENT,
    RARITY_COLORS, RARITY_HEX_COLORS, RARITY_ORDER
)
from src.assets.asset_factory import AssetFactory
from src.ui.inventory import Inventory, ItemStack, ITEM_REGISTRY, ITEM_ALIASES
from src.rpg.equipment import Equipment, ARMOR_DATA
from src.entities.mob import DemonEye, NightGazer, MOB_TYPE_REGISTRY, create_mob_by_type
from src.ui.hud import HUD


def test_anti_plagiarism_aliasing():
    print("\n[Test 1] Testing Anti-Plagiarism Renaming & Dual-Alias Resolution...")
    # Expected key mappings
    expected_aliases = {
        "starfury": "astral_wrath",
        "hermes_boots": "zephyr_striders",
        "gel": "spud_sap",
        "mana_flower": "arcane_orchid",
        "band_of_regeneration": "talisman_of_vigor",
        "ebonstone_block": "blightstone_block",
    }
    for old_id, new_id in expected_aliases.items():
        assert old_id in ITEM_ALIASES, f"Missing alias entry for {old_id}"
        assert ITEM_ALIASES[old_id] == new_id, f"Expected {old_id} -> {new_id}, got {ITEM_ALIASES[old_id]}"
        assert new_id in ITEM_REGISTRY, f"Canonical item {new_id} missing from ITEM_REGISTRY"
        assert old_id in ITEM_REGISTRY, f"Legacy item {old_id} missing backward compatibility in ITEM_REGISTRY"

    # Verify inventory operations resolve both old and new names seamlessly
    af = AssetFactory()
    inv = Inventory(af)
    inv.slots[0] = ItemStack("spud_sap", 20)
    assert inv.count_item("spud_sap") == 20
    assert inv.count_item("gel") == 20, "count_item must resolve legacy 'gel' alias"

    # Remove using legacy name
    success = inv.remove_item("gel", 5)
    assert success is True
    assert inv.count_item("spud_sap") == 15
    assert inv.count_item("gel") == 15

    # Astral Wrath & Starfury
    inv.slots[1] = ItemStack("astral_wrath", 1)
    assert inv.count_item("starfury") == 1
    assert inv.count_item("astral_wrath") == 1

    print("  -> Anti-plagiarism aliasing and backward compatibility verified 100%!")


def test_1000_plus_items_json_and_registry():
    print("\n[Test 2] Testing 1000+ Items JSON Database & Engine Ingestion...")
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    weapons_path = os.path.join(base_dir, "data", "weapons.json")
    equipments_path = os.path.join(base_dir, "data", "equipments.json")

    assert os.path.exists(weapons_path), f"Missing data/weapons.json at {weapons_path}"
    assert os.path.exists(equipments_path), f"Missing data/equipments.json at {equipments_path}"

    with open(weapons_path, "r", encoding="utf-8") as f:
        weapons_data = json.load(f)
    with open(equipments_path, "r", encoding="utf-8") as f:
        equipments_data = json.load(f)

    total_weapons = len(weapons_data)
    total_equipments = len(equipments_data)
    total_json_items = total_weapons + total_equipments

    print(f"  -> weapons.json: {total_weapons} items")
    print(f"  -> equipments.json: {total_equipments} items")
    print(f"  -> Total Generated JSON Catalog: {total_json_items} items")

    assert total_weapons >= 550, f"Expected at least 550 weapons, found {total_weapons}"
    assert total_equipments >= 550, f"Expected at least 550 equipment pieces, found {total_equipments}"
    assert total_json_items >= 1000, f"Expected 1000+ items, found {total_json_items}"

    # Verify ingestion into ITEM_REGISTRY and ARMOR_DATA
    assert len(ITEM_REGISTRY) >= 1000, f"ITEM_REGISTRY contains only {len(ITEM_REGISTRY)} items"
    assert len(ARMOR_DATA) >= 1000, f"ARMOR_DATA contains only {len(ARMOR_DATA)} items"
    print(f"  -> Engine Ingestion: ITEM_REGISTRY has {len(ITEM_REGISTRY)} items, ARMOR_DATA has {len(ARMOR_DATA)} items")


def test_7_tier_rarity_system():
    print("\n[Test 3] Testing 7-Tier Rarity System Hierarchy, Effects & Lore...")
    expected_rarities = [
        RARITY_COMMON, RARITY_UNCOMMON, RARITY_RARE, RARITY_EPIC,
        RARITY_MYTHIC, RARITY_LEGENDARY, RARITY_ANCIENT
    ]
    assert RARITY_ORDER == expected_rarities

    # Verify exact requested color hexes
    assert RARITY_HEX_COLORS[RARITY_COMMON] == "#9E9E9E"
    assert RARITY_HEX_COLORS[RARITY_UNCOMMON] == "#4CAF50"
    assert RARITY_HEX_COLORS[RARITY_RARE] == "#2196F3"
    assert RARITY_HEX_COLORS[RARITY_EPIC] == "#9C27B0"
    assert RARITY_HEX_COLORS[RARITY_MYTHIC] == "#FF9800"
    assert RARITY_HEX_COLORS[RARITY_LEGENDARY] == "#FFD700"
    assert RARITY_HEX_COLORS[RARITY_ANCIENT] == "#F44336"

    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    all_items = []
    with open(os.path.join(base_dir, "data", "weapons.json"), "r", encoding="utf-8") as f:
        all_items.extend(json.load(f))
    with open(os.path.join(base_dir, "data", "equipments.json"), "r", encoding="utf-8") as f:
        all_items.extend(json.load(f))

    rarity_counts = {r: 0 for r in expected_rarities}
    for item in all_items:
        r = item.get("rarity")
        assert r in rarity_counts, f"Item {item['id']} has invalid rarity {r}"
        rarity_counts[r] += 1

        # Check required fields
        assert "id" in item and "name" in item and "cat" in item
        assert "atk" in item or "def" in item

        # Upper tier items (Epic, Mythic, Legendary, Ancient) MUST have effects list
        if r in (RARITY_EPIC, RARITY_MYTHIC, RARITY_LEGENDARY, RARITY_ANCIENT):
            assert "effects" in item and len(item["effects"]) > 0, (
                f"Upper class {r} item {item['id']} missing effects list"
            )

        # Legendary and Ancient items MUST have lore
        if r in (RARITY_LEGENDARY, RARITY_ANCIENT):
            assert "lore" in item and len(item["lore"].strip()) > 0, (
                f"{r.capitalize()} item {item['id']} missing lore"
            )

    print("  -> Rarity Distribution:")
    for r in expected_rarities:
        print(f"     [{r.upper()}]: {rarity_counts[r]} items")
        assert rarity_counts[r] > 0, f"Rarity tier {r} has 0 items!"


def test_dynamic_procedural_sprite_generation():
    print("\n[Test 4] Testing Dynamic Procedural Sprite Generation & Caching...")
    af = AssetFactory()

    # Sample items from different categories and rarities
    sample_items = [
        "wp_common_1", "wp_uncommon_15", "wp_rare_30", "wp_epic_50",
        "wp_mythic_70", "wp_legendary_10", "wp_ancient_1",
        "eq_common_5", "eq_uncommon_20", "eq_rare_40", "eq_epic_60",
        "eq_mythic_75", "eq_legendary_12", "eq_ancient_2",
        "astral_wrath", "zephyr_striders", "talisman_of_vigor", "spud_sap"
    ]

    for item_id in sample_items:
        surf = af.items[item_id]
        assert surf is not None, f"Item sprite for {item_id} returned None"
        assert isinstance(surf, pygame.Surface), f"Item sprite for {item_id} is not a Surface"
        assert surf.get_width() == 24 and surf.get_height() == 24
        # Verify sprite is cached in dict
        assert item_id in af.items

    print(f"  -> Successfully generated and verified {len(sample_items)} procedural sprite icons.")


def test_mob_night_gazer_renaming():
    print("\n[Test 5] Testing Night Gazer Mob Renaming & Instantiation...")
    af = AssetFactory()

    # Verify MOB_TYPE_REGISTRY
    assert "night_gazer" in MOB_TYPE_REGISTRY
    assert "demon_eye" in MOB_TYPE_REGISTRY

    # Create via night_gazer
    mob1 = create_mob_by_type("night_gazer", 100, 200, af)
    assert mob1.name == "Night Gazer", f"Expected name 'Night Gazer', got '{mob1.name}'"
    assert len(mob1.frames) == 6

    # Create via demon_eye alias
    mob2 = create_mob_by_type("demon_eye", 100, 200, af)
    assert mob2.name == "Night Gazer", f"Expected name 'Night Gazer', got '{mob2.name}'"
    assert len(mob2.frames) == 6

    # Verify NightGazer class alias
    assert NightGazer is DemonEye
    print("  -> Night Gazer mob naming and backward compatibility verified!")


def test_hud_tooltip_for_all_7_rarities():
    print("\n[Test 6] Testing HUD Tooltip Rendering across all 7 Rarities...")
    af = AssetFactory()
    hud = HUD(af)
    target_surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)

    test_items = [
        "wp_common_1",
        "wp_uncommon_1",
        "wp_rare_1",
        "wp_epic_1",
        "wp_mythic_1",
        "wp_legendary_1",
        "wp_ancient_1"
    ]

    for item_id in test_items:
        stack = ItemStack(item_id, 1)
        # Should render without throwing exceptions
        hud._render_tooltip(target_surf, 100, 100, stack)

    print("  -> Successfully rendered tooltips for all 7 rarity tiers (including effects & lore)!")


def run_all():
    print("==================================================================")
    print("POTARIA ANTI-PLAGIARISM & 1000+ ITEMS CATALOG TEST SUITE")
    print("Developer: Kurados  |  Pure Python & pygame-ce")
    print("==================================================================")

    test_anti_plagiarism_aliasing()
    test_1000_plus_items_json_and_registry()
    test_7_tier_rarity_system()
    test_dynamic_procedural_sprite_generation()
    test_mob_night_gazer_renaming()
    test_hud_tooltip_for_all_7_rarities()

    print("\n==================================================================")
    print("ALL 6 TESTS FOR ANTI-PLAGIARISM & 1000+ ITEMS CATALOG PASSED!")
    print("==================================================================")


if __name__ == "__main__":
    run_all()
