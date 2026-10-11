"""
Integration tests for Atmosphere expansion, Sky Dungeon relocation, World Cache,
Boss Health Bar repositioning, In-Game Time HUD, Parallax Backgrounds,
Typography caching, and Modding/DLC Expansion System.
"""

import os
import sys
import shutil
import tempfile
import pytest
import pygame

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.constants import (
    SCREEN_WIDTH, SCREEN_HEIGHT, SCALED_TILE,
    CAT_ACCESSORY, CAT_WEAPON, CAT_CONSUMABLE,
    RARITY_MYTHIC, RARITY_LEGENDARY,
    TILE_DUNGEON_BRICK, TILE_DUNGEON_ALTAR
)
from src.ui.theme import (
    font_regular, font_semibold, font_bold, font_title, font_compact,
    _FONT_CACHE, FONT_REGULAR, FONT_BOLD, FONT_TITLE
)
from src.assets.asset_factory import AssetFactory
from src.audio.sound_effects import SoundManager
from src.environment.sky import DayNightCycle
from src.world.chunk_manager import ChunkManager, SKY_MIN_Y, CHUNK_WIDTH, CHUNK_HEIGHT
from src.camera import Camera
from src.entities.boss import LordMalus, GrandBossSolRho
from src.ui.hud import HUD
from src.world.world_cache import WorldCache
from src.modding.mod_manager import ModManager, ModManifest, get_mod_manager
from src.ui.inventory import ITEM_REGISTRY
from src.ui.crafting import RECIPES


@pytest.fixture(scope="module")
def shared_assets():
    pygame.init()
    if not pygame.display.get_surface():
        pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    af = AssetFactory()
    sm = SoundManager()
    return af, sm


class TestTypographyTheme:
    def test_fonts_load_and_cache(self):
        """Verifies centralized typography system correctly loads and caches fonts."""
        f1 = font_regular(14)
        f2 = font_regular(14)
        assert f1 is f2, "Font instances with same (key, size) should be cached identical objects"

        f_semi = font_semibold(15)
        f_b = font_bold(18)
        f_t = font_title(24)
        f_c = font_compact(12)

        assert f1 is not None
        assert f_semi is not None
        assert f_b is not None
        assert f_t is not None
        assert f_c is not None

        # Verify cache keys
        assert ("regular", 14) in _FONT_CACHE
        assert ("bold", 18) in _FONT_CACHE
        assert ("title", 24) in _FONT_CACHE


class TestAtmosphereAndSkyCitadel:
    def test_sky_min_y_and_citadel_coordinates(self):
        """Verifies Sky Citadel is located in the upper atmosphere/orbit at y = -185..-162."""
        cm = ChunkManager(seed=12345, world_type="infinite")
        assert SKY_MIN_Y <= -200, "Sky altitude must extend into deep orbital space"

        # Chunk 0 carves the dungeon and Sky Citadel at center gx = 0
        chunk = cm.get_chunk(0)

        # Floor is at y = -163, altar at y = -164
        floor_tile = chunk.get_tile_local(0, -163)
        altar_tile = chunk.get_tile_local(0, -164)
        assert floor_tile == TILE_DUNGEON_BRICK
        assert altar_tile == TILE_DUNGEON_ALTAR

    def test_camera_world_min_y_bounds(self):
        """Verifies Camera allows vertical movement into the high orbital atmosphere."""
        cam = Camera(SCREEN_WIDTH, SCREEN_HEIGHT)
        assert cam.world_min_y <= SKY_MIN_Y * SCALED_TILE
        cam.set_target(0, -170 * SCALED_TILE, instant=True)
        assert cam.offset_y < 0

    def test_day_night_cycle_altitude_transitions(self, shared_assets):
        """Verifies altitude gradient shifts from troposphere to pitch black space void."""
        af, _ = shared_assets
        sky = DayNightCycle(asset_factory=af)
        # Surface altitude (ty >= 20)
        c_surface_top, c_surface_bot = sky.get_altitude_sky_colors(30)
        # Orbit / deep space altitude (ty <= -100)
        c_space_top, c_space_bot = sky.get_altitude_sky_colors(-160)

        # Deep space void top should reach near pitch black (<= 5 across all channels)
        assert c_space_top[0] <= 5 and c_space_top[1] <= 5 and c_space_top[2] <= 10
        assert c_space_bot[0] <= 5 and c_space_bot[1] <= 5 and c_space_bot[2] <= 5

    def test_parallax_background_assets_exist(self):
        """Verifies dedicated assets/backgrounds/ directory exists with seamless layers."""
        bg_dir = os.path.join("assets", "backgrounds")
        assert os.path.isdir(bg_dir)
        required_layers = [
            "bg_far_mountains.png",
            "bg_rolling_hills.png",
            "bg_mid_forest.png",
            "bg_sky_clouds.png",
            "bg_space_nebula.png"
        ]
        for layer in required_layers:
            assert os.path.isfile(os.path.join(bg_dir, layer)), f"Missing background layer: {layer}"


class TestBossHealthBarRepositioning:
    def test_boss_health_bar_docked_at_bottom(self, shared_assets):
        """Verifies Grand Boss and Mini Boss health bars render near bottom of screen."""
        af, sm = shared_assets
        font = font_regular(14)
        font_t = font_title(18)
        mini = LordMalus(100, 100, af, sm)
        surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        mini.render_boss_bar(surface, font, font_t)
        assert mini.bar_y == SCREEN_HEIGHT - 60

        sol = GrandBossSolRho(100, 100, af, sm)
        sol.render_boss_bar(surface, font, font_t)
        assert sol.bar_y == SCREEN_HEIGHT - 60


class TestTimeHudWidget:
    def test_time_hud_clock_widget(self, shared_assets):
        """Verifies HUD time widget computes 12-hour AM/PM time and renders without error."""
        af, _ = shared_assets
        hud = HUD(asset_factory=af)
        sky = DayNightCycle(asset_factory=af)
        sky.time = 0.0  # Morning ~ 6:00 AM
        surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)

        # Directly test clock widget rendering and time string conversion
        time_str, period, is_day = hud.get_game_time_string(sky)
        assert "AM" in period or "PM" in period
        assert ":" in time_str

        # Test widget render
        hud._render_clock_widget(surface, sky)


class TestWorldCache:
    def test_world_cache_chunks_and_lighting(self):
        """Verifies WorldCache creates world-scoped cache dirs and serializes chunks/lighting."""
        temp_dir = tempfile.mkdtemp()
        try:
            cache = WorldCache(world_name="TestWorld", base_dir=temp_dir)
            assert os.path.exists(cache.chunks_dir)
            assert os.path.exists(cache.lighting_dir)

            # Create mock chunk
            mock_chunk = type("MockChunk", (), {
                "chunk_x": 0,
                "surface_heights": [60]*32,
                "col_biomes": ["forest"]*32,
                "tiles": [[1]*240 for _ in range(32)],
                "walls": [[0]*240 for _ in range(32)],
                "sky_tiles": {(16, -164): 99},
                "sky_walls": {(16, -164): 50},
            })()

            assert cache.save_chunk(0, mock_chunk) is True
            assert cache.has_chunk_cache(0) is True

            loaded = cache.load_chunk_data(0)
            assert loaded is not None
            assert loaded["chunk_x"] == 0
            assert "16,-164" in loaded["sky_tiles"]
            assert loaded["sky_tiles"]["16,-164"] == 99

            # Lighting cache
            light_data = {"explored_mask": [True, False, True]}
            assert cache.save_lighting(0, light_data) is True
            assert cache.has_lighting_cache(0) is True
            loaded_light = cache.load_lighting_data(0)
            assert loaded_light == light_data
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)


class TestModdingAndDLCSystem:
    def test_mod_and_dlc_discovery_and_registration(self):
        """Verifies ModManager scans mods/ and dlc/ manifests and registers items/recipes."""
        temp_dir = tempfile.mkdtemp()
        try:
            mods_path = os.path.join(temp_dir, "mods")
            dlc_path = os.path.join(temp_dir, "dlc")
            os.makedirs(mods_path, exist_ok=True)
            os.makedirs(dlc_path, exist_ok=True)

            # Create test mod
            test_mod_dir = os.path.join(mods_path, "test_magic_mod")
            os.makedirs(test_mod_dir, exist_ok=True)
            with open(os.path.join(test_mod_dir, "mod.json"), "w", encoding="utf-8") as f:
                f.write("""{
                    "id": "test_magic_mod",
                    "name": "Test Magic Mod",
                    "version": "1.0.0",
                    "author": "Tester",
                    "description": "Test mod description",
                    "type": "mod",
                    "enabled": true,
                    "items": {
                        "test_magic_tuber": {
                            "name": "Test Magic Tuber",
                            "cat": "accessory",
                            "rarity": "mythic",
                            "desc": "Cosmic test tuber",
                            "special": "+10 Speed"
                        }
                    },
                    "recipes": [
                        {
                            "result": "test_magic_tuber",
                            "count": 1,
                            "station": "work_bench",
                            "category": "equipment",
                            "ingredients": [["raw_potato", 5]]
                        }
                    ]
                }""")

            mm = ModManager(mods_dir=mods_path, dlc_dir=dlc_path)
            summary = mm.load_all()

            assert summary["mods_loaded"] == 1
            assert summary["items_registered"] >= 1
            assert summary["recipes_registered"] >= 1

            assert "test_magic_tuber" in ITEM_REGISTRY
            item_entry = ITEM_REGISTRY["test_magic_tuber"]
            assert item_entry["name"] == "Test Magic Tuber"
            assert item_entry["cat"] == CAT_ACCESSORY
            assert item_entry["rarity"] == RARITY_MYTHIC

            # Check recipe registered
            registered_recipe = next((r for r in RECIPES if r["result"] == "test_magic_tuber"), None)
            assert registered_recipe is not None
            assert registered_recipe["ingredients"] == [("raw_potato", 5)]
        finally:
            ITEM_REGISTRY.pop("test_magic_tuber", None)
            RECIPES[:] = [r for r in RECIPES if r.get("result") != "test_magic_tuber"]
            tuber_file = os.path.join("assets", "craftable_items", "test_magic_tuber.png")
            if os.path.exists(tuber_file):
                try:
                    os.remove(tuber_file)
                except OSError:
                    pass
            shutil.rmtree(temp_dir, ignore_errors=True)

    def test_default_example_mod_and_dlc(self):
        """Verifies default example mod and celestial depths DLC load correctly."""
        mm = ModManager(mods_dir="mods", dlc_dir="dlc")
        mm.discover()

        assert "example_magic_spuds" in mm.mods
        assert "expansion_celestial_depths" in mm.dlc

        summary = mm.load_all()
        assert "spud_of_destiny" in ITEM_REGISTRY
        assert "orbital_stardust_blade" in ITEM_REGISTRY
        assert any(r["result"] == "orbital_stardust_blade" for r in RECIPES)
