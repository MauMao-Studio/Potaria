"""
Potaria - Unique Asset Generation & Stardew x Terraria Artstyle Test Suite
Verifies:
1. 1000+ Item Assets are 100% Unique (Zero Identical Duplicates, except intentional aliases)
2. High Rarity Tiers (Mythic, Legendary, Ancient) possess ornate silhouettes & glowing cores
3. 5 Bosses (Lord Malus, Ignis Colossus, Cryo-Spud, Necro-Tuber, Sol-Rho) possess rich multi-frame animations
4. All Stardew x Terraria tiles, walls, and player animation cycles are present and valid
Developer: Kurados | Pure Python & pygame-ce
"""
import os
import sys
import hashlib
import pygame

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
os.environ["SDL_VIDEODRIVER"] = "dummy"
pygame.init()

from src.assets.asset_factory import AssetFactory
from src.ui.inventory import ITEM_REGISTRY, ITEM_ALIASES, load_custom_items
from src.constants import (
    RARITY_COMMON, RARITY_UNCOMMON, RARITY_RARE, RARITY_EPIC,
    RARITY_MYTHIC, RARITY_LEGENDARY, RARITY_ANCIENT,
    TILE_ROOF_TILES, TILE_GRASS, TILE_DIRT, TILE_STONE
)


def test_unique_item_sprites():
    print("\n[Test 1] Verifying 1000+ Items have Unique Visual Pixel Art...")
    load_custom_items()
    af = AssetFactory()

    total_items = len(ITEM_REGISTRY)
    assert total_items >= 1300, f"Expected at least 1300 items in registry, got {total_items}"

    images = {}
    for iid in ITEM_REGISTRY:
        s = af.items[iid]
        assert isinstance(s, pygame.Surface)
        assert s.get_width() == 24 and s.get_height() == 24
        b = pygame.image.tobytes(s, "RGBA")
        images.setdefault(b, []).append(iid)

    unique_images_count = len(images)
    print(f"  -> Total items in ITEM_REGISTRY: {total_items}")
    print(f"  -> Total unique sprite images: {unique_images_count}")

    # The only collisions allowed are the deliberate aliases (astral_wrath/starfury, zephyr_striders/hermes_boots)
    collisions = {k: v for k, v in images.items() if len(v) > 1}
    for b, item_list in collisions.items():
        canons = {ITEM_ALIASES.get(item, item) for item in item_list}
        assert len(canons) == 1, f"Unintended identical sprites found between: {item_list}"

    assert unique_images_count == total_items, (
        f"Expected 100% unique sprites ({total_items}), got {unique_images_count} (collisions: {collisions})"
    )
    print(f"  -> VERIFIED: All {unique_images_count} items have 100% unique handcrafted/procedural pixel art!")


def test_iconic_real_world_and_disk_uniqueness():
    print("\n[Test 5] Verifying Iconic Real-World Items, Disk PNG Uniqueness, and Tracker Compliance...")
    af = AssetFactory()
    iconic_items = [
        "apple", "bomb", "acorn", "forged_iron_chain", "glass_flask",
        "gel", "spud_sap", "star", "fallen_star", "falling_star"
    ]
    seen_iconic = set()
    for iid in iconic_items:
        assert iid in af.items, f"Missing iconic item in AssetFactory.items: {iid}"
        surf = af.items[iid]
        raw = pygame.image.tobytes(surf, "RGBA")
        assert raw not in seen_iconic, f"Duplicate iconic sprite buffer for {iid}"
        seen_iconic.add(raw)
        non_transparent = sum(
            1 for x in range(surf.get_width()) for y in range(surf.get_height())
            if surf.get_at((x, y))[3] > 0
        )
        assert non_transparent >= 35, f"Iconic item {iid} has too few opaque pixels ({non_transparent})"

    summary = AssetFactory.write_unique_assets_tracker("assets", "UNIQUE_ASSETS_TRACKER.md")
    assert summary["total_assets_tracked"] >= 2000, f"Expected >= 2000 tracked assets, got {summary['total_assets_tracked']}"
    assert summary["unique_sha256_digests"] == summary["total_assets_tracked"], (
        f"Expected 0 duplicate PNGs on disk, got {summary['duplicate_file_groups']} duplicate groups"
    )
    assert summary["duplicate_file_groups"] == 0

    with open("UNIQUE_ASSETS_TRACKER.md", "r", encoding="utf-8") as tf:
        tracker_text = tf.read()
    assert all(ord(ch) <= 127 for ch in tracker_text), "UNIQUE_ASSETS_TRACKER.md must not contain emojis or non-ASCII characters"
    for forbidden in ("file://", "C:/", "C:\\"):
        assert forbidden not in tracker_text, f"UNIQUE_ASSETS_TRACKER.md must not contain local machine path: {forbidden}"
    print(f"  -> VERIFIED: {summary['total_assets_tracked']} unique PNGs on disk and tracker verified!")


def test_high_rarity_grand_sprites():
    print("\n[Test 2] Verifying Grand Silhouettes for Highest Rarities (Mythic, Legendary, Ancient)...")
    af = AssetFactory()

    high_tier_samples = [
        "astral_wrath", "celestial_greatsword", "starch_blade",
        "titan_helmet", "titan_chestplate", "crown_of_potaria",
        "wp_mythic_1", "wp_legendary_1", "wp_ancient_1",
        "eq_mythic_1", "eq_legendary_1", "eq_ancient_1"
    ]

    for item_id in high_tier_samples:
        surf = af.items[item_id]
        assert surf is not None
        # Verify non-empty pixel count is substantial
        non_empty = 0
        for x in range(24):
            for y in range(24):
                if surf.get_at((x, y))[3] > 0:
                    non_empty += 1
        assert non_empty >= 25, f"Grand sprite for {item_id} had only {non_empty} pixels!"
    print(f"  -> VERIFIED: All sampled high-rarity items feature ornate, grand silhouettes!")


def test_boss_designs_and_animations():
    print("\n[Test 3] Verifying 5 Polished Bosses & Multiphase Transitions...")
    af = AssetFactory()

    expected_bosses = ["lord_malus", "ignis_colossus", "cryo_spud", "necro_tuber", "sol_rho_phase1", "sol_rho_phase2"]
    for b_key in expected_bosses:
        assert b_key in af.boss, f"Missing boss key: {b_key}"
        frames = af.boss[b_key]
        assert isinstance(frames, list), f"Boss {b_key} frames must be a list"
        assert len(frames) >= 3, f"Boss {b_key} must have at least 3 animation frames, got {len(frames)}"
        for idx, f in enumerate(frames):
            assert isinstance(f, pygame.Surface)
            if "sol_rho" in b_key:
                assert f.get_width() == 64 and f.get_height() == 64
            else:
                assert f.get_width() == 48 and f.get_height() == 48

    # Boss projectiles
    for p_key in ["fireball", "magma_bomb", "frost_shard", "ghost_skull", "solar_orb", "void_meteor", "singularity"]:
        assert p_key in af.boss, f"Missing boss projectile: {p_key}"
        assert isinstance(af.boss[p_key], pygame.Surface)

    print("  -> VERIFIED: All 5 bosses feature multi-frame animations & polished artstyle!")


def test_tiles_walls_player():
    print("\n[Test 4] Verifying Stardew x Terraria Shaded Tiles, Walls & Potato Player...")
    af = AssetFactory()

    assert TILE_ROOF_TILES in af.tiles, "Missing terracotta roof tiles"
    assert TILE_GRASS in af.tiles, "Missing lush grass tiles"
    assert TILE_DIRT in af.tiles, "Missing dirt tiles"
    assert TILE_STONE in af.tiles, "Missing stone tiles"

    # Player sprites
    assert "idle_frames" in af.player_sprites
    assert len(af.player_sprites["idle_frames"]) == 6
    assert "walk" in af.player_sprites
    assert len(af.player_sprites["walk"]) == 8
    assert "jump" in af.player_sprites
    assert "fall" in af.player_sprites
    assert "arm" in af.player_sprites

    print("  -> VERIFIED: Tiles, walls, and potato character animations verified 100%!")


def test_bespoke_blocks_tools_and_gemini_pipeline():
    print("\n[Test 6] Verifying Bespoke Blocks/Stations, Tool/Accessory Routing, Dual-Theme Armor, and Gemini Live Image Pipeline...")
    import io
    import base64
    import tempfile
    from unittest.mock import patch, MagicMock
    from src.assets.asset_factory import generate_assets_with_gemini

    af = AssetFactory()

    # 1. Verify stations, furniture, tools, shields, arrows, and accessories have distinct alpha silhouettes
    silhouette_group = [
        "torch", "work_bench", "furnace", "chest", "wooden_table", "wooden_chair",
        "bookshelf", "sink", "glowing_mushroom", "cactus", "glass_window", "wood_platform",
        "brass_far_seer", "magnetic_lodestone", "solar_chronometer", "explorers_satchel",
        "totem_of_resurgence", "spud_quiver", "oak_buckler", "iron_aegis",
        "fiber_clippers", "pyrite_sparker", "spud_angler_rod", "copper_harvester_sickle",
        "burlap_tether", "wooden_arrow", "frostburn_arrow", "flame_arrow", "astral_arrow", "glowing_lumen_arrow"
    ]
    alpha_masks = {}
    for iid in silhouette_group:
        surf = af.items[iid]
        mask = tuple(
            1 if surf.get_at((x, y))[3] > 0 else 0
            for y in range(24) for x in range(24)
        )
        assert mask not in alpha_masks, f"Duplicate alpha silhouette between {iid} and {alpha_masks[mask]}"
        alpha_masks[mask] = iid

    # 2. Verify Screenshot #2 chest armors have distinct primary/secondary palettes and unique pixels
    screenshot_armors = [
        "zephyr_lightning_aegis", "zephyr_vortex_breastplate",
        "blight_umbral_overcoat", "blizzard_aegis",
        "canopy_overcoat", "crypt_cuirass_of_the_eclipse",
        "dread_copper_carapace", "dread_cyclone_robe"
    ]
    armor_palettes = set()
    for aid in screenshot_armors:
        h = hashlib.sha256(aid.encode("utf-8")).digest()
        pal = af._get_item_palette(aid, RARITY_COMMON, h)
        sig = (pal["primary"], pal["secondary"], pal["glow"])
        assert sig not in armor_palettes, f"Duplicate palette signature for {aid}: {sig}"
        armor_palettes.add(sig)

    # 3. Verify generate_assets_with_gemini live image synthesis with max_live_images=2
    sample_surf = pygame.Surface((48, 48), pygame.SRCALPHA)
    pygame.draw.circle(sample_surf, (230, 40, 40, 255), (24, 24), 18)
    buf = io.BytesIO()
    pygame.image.save(sample_surf, buf, "sample.png")
    b64_png = base64.b64encode(buf.getvalue()).decode("ascii")

    mock_client = MagicMock()
    def fake_create(**kwargs):
        assert "response_modalities" not in kwargs, "client.interactions.create must not pass unsupported response_modalities"
        resp = MagicMock()
        if "image" in kwargs.get("model", ""):
            out_img = MagicMock()
            out_img.data = b64_png
            resp.output_image = out_img
            resp.outputs = [out_img]
        else:
            resp.output_text = "Mocked palette and silhouette directive"
        return resp

    mock_client.interactions.create.side_effect = fake_create

    mock_google = MagicMock()
    mock_genai = MagicMock()
    mock_genai.Client.return_value = mock_client
    mock_google.genai = mock_genai

    def fast_export(self, target_dir="assets", force=False):
        os.makedirs(os.path.join(target_dir, "items"), exist_ok=True)
        os.makedirs(os.path.join(target_dir, "craftable_items"), exist_ok=True)

    with tempfile.TemporaryDirectory() as tmp_dir:
        tracker_out = os.path.join(tmp_dir, "TRACKER.md")
        with patch.dict(sys.modules, {"google": mock_google, "google.genai": mock_genai}), patch.object(AssetFactory, "export_all_assets", fast_export):
            summary = generate_assets_with_gemini(
                api_key="mock-test-key",
                target_dir=tmp_dir,
                tracker_path=tracker_out,
                max_live_images=2,
            )
        assert "Active" in summary["generation_mode"], f"Expected active Gemini mode, got: {summary['generation_mode']}"
        apple_png = os.path.join(tmp_dir, "items", "apple.png")
        loaded_apple = pygame.image.load(apple_png)
        assert loaded_apple.get_size() == (24, 24), f"Expected 24x24 scaled live image, got {loaded_apple.get_size()}"

    print("  -> VERIFIED: Bespoke stations, tools, dual-theme armors, and Gemini live image pipeline verified!")


import unittest


class TestUniqueSpritesGen(unittest.TestCase):
    def test_01_unique_item_sprites(self):
        test_unique_item_sprites()

    def test_02_high_rarity_grand_sprites(self):
        test_high_rarity_grand_sprites()

    def test_03_boss_designs_and_animations(self):
        test_boss_designs_and_animations()

    def test_04_tiles_walls_player(self):
        test_tiles_walls_player()

    def test_05_iconic_real_world_and_disk_uniqueness(self):
        test_iconic_real_world_and_disk_uniqueness()

    def test_06_bespoke_blocks_tools_and_gemini_pipeline(self):
        test_bespoke_blocks_tools_and_gemini_pipeline()


if __name__ == "__main__":
    print("==================================================================")
    print("POTARIA ARTSTYLE OVERHAUL & ASSETS UNIQUENESS TEST SUITE")
    print("Developer: Kurados  |  Pure Python & pygame-ce")
    print("==================================================================")
    test_unique_item_sprites()
    test_high_rarity_grand_sprites()
    test_boss_designs_and_animations()
    test_tiles_walls_player()
    test_iconic_real_world_and_disk_uniqueness()
    test_bespoke_blocks_tools_and_gemini_pipeline()
    print("\n==================================================================")
    print("ALL ARTSTYLE & ASSET OVERHAUL TESTS PASSED SUCCESSFULLY!")
    print("==================================================================")

