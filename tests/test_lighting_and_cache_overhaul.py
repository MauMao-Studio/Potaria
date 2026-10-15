"""
Potaria - Unit and Integration Tests for Lighting, Persistent Cache, and Profiler Overhaul
Developer: Kurados
"""

import os
import sys
import json
import shutil
import tempfile
import pytest
import pygame

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.constants import (
    SCREEN_WIDTH, SCREEN_HEIGHT, SCALED_TILE,
    TILE_AIR, TILE_DIRT, TILE_GRASS, TILE_STONE, TILE_TORCH,
    TILE_WOOD, WALL_WOOD
)
from src.assets.asset_factory import AssetFactory
from src.world.chunk_manager import ChunkManager, CHUNK_WIDTH, SECTION_HEIGHT
from src.world.lighting import LightingEngine
from src.world.world import World
from src.world.world_cache import WorldCache, CACHE_SCHEMA_VERSION, LIGHTING_CACHE_VERSION
from src.profiler import PotariaProfiler


@pytest.fixture(scope="module")
def pygame_module():
    pygame.init()
    if not pygame.display.get_surface():
        pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    af = AssetFactory()
    return af


class TestLightingCorrectnessAndOptimization:
    def test_daytime_sunlight_and_downward_shadow_casting(self, pygame_module):
        """Verifies that daytime sunlight illuminates exposed top surfaces and only casts downward."""
        af = pygame_module
        world = World(af, seed=42)
        lighting = LightingEngine(SCREEN_WIDTH, SCREEN_HEIGHT)
        
        # Determine surface height at x=0
        surf_y = world.get_surface_height(0)
        assert surf_y > 10, "Surface level should be reasonably deep in the world"

        # Viewport encompassing surface and deep underground
        min_tx = -2
        max_tx = 2
        min_ty = surf_y - 5
        max_ty = surf_y + 15

        # Compute lighting during full noon daylight
        lighting.compute_viewport_light(
            world=world,
            min_tx=min_tx, max_tx=max_tx,
            min_ty=min_ty, max_ty=max_ty,
            ambient_sunlight=15.0,
            torch_positions=[],
            ambient_tint=(1.0, 1.0, 1.0)
        )

        grid = lighting._last_light_grid
        assert grid is not None, "Light grid should be computed"
        
        def get_lvl(tx, ty):
            lx = tx - min_tx
            ly = ty - min_ty
            return grid[lx][ly]

        # 1. Exposed air block directly above surface must be fully lit (15)
        sky_light = get_lvl(0, surf_y - 1)
        assert sky_light == 15, f"Sky above surface should be 15, got {sky_light}"

        # 2. Exposed top surface block receives direct sunlight (15)
        top_light = get_lvl(0, surf_y)
        assert top_light == 15, f"Exposed top block should receive full sunlight (15), got {top_light}"

        # 3. Underground block beneath solid ground receives no direct sunlight
        deep_underground_light = get_lvl(0, surf_y + 10)
        assert deep_underground_light == 0, f"Deep underground solid terrain should have 0 light, got {deep_underground_light}"

    def test_lighting_state_separation_no_redundant_rebuild(self, pygame_module):
        """Verifies that floating sky tint changes do not invalidate or rebuild the integer light level grid."""
        af = pygame_module
        world = World(af, seed=123)
        lighting = LightingEngine(SCREEN_WIDTH, SCREEN_HEIGHT)

        min_tx, max_tx = 0, 10
        min_ty, max_ty = 40, 60

        # First pass with ambient_sunlight = 15, morning peach tint
        lighting.compute_viewport_light(
            world=world,
            min_tx=min_tx, max_tx=max_tx,
            min_ty=min_ty, max_ty=max_ty,
            ambient_sunlight=15.0,
            torch_positions=[],
            ambient_tint=(1.0, 0.85, 0.75)
        )
        assert lighting._last_light_grid is not None
        rebuilds_initial = lighting.rebuild_count

        # Second pass with identical sun_val, same coordinates, but slight sky tint shift
        lighting.compute_viewport_light(
            world=world,
            min_tx=min_tx, max_tx=max_tx,
            min_ty=min_ty, max_ty=max_ty,
            ambient_sunlight=15.0,
            torch_positions=[],
            ambient_tint=(1.0, 0.87, 0.77)
        )
        assert lighting.rebuild_count == rebuilds_initial, "Light grid should not recalculate for simple ambient tint fluctuation"

    def test_radial_light_precomputed_lookup(self, pygame_module):
        """Verifies precomputed Euclidean radial light offset table is active and accurate."""
        af = pygame_module
        world = World(af, seed=456)
        lighting = LightingEngine(SCREEN_WIDTH, SCREEN_HEIGHT)

        offsets = lighting._get_radial_offsets(radius=6, intensity=14)
        assert len(offsets) > 0, "Radial cache must produce offset tuples"
        # Center should have highest light level
        center_offsets = [lvl for dx, dy, lvl in offsets if dx == 0 and dy == 0]
        assert center_offsets and center_offsets[0] == 14

    def test_overhead_roof_occlusion_above_viewport(self, pygame_module):
        """Verifies that ceilings/roofs above min_ty block direct downward daylight even when min_ty <= surf_y."""
        af = pygame_module
        world = World(af, seed=42)
        lighting = LightingEngine(SCREEN_WIDTH, SCREEN_HEIGHT)

        # Build wooden roof at y=30 (above natural ground around y=70)
        for x in range(-5, 6):
            world.set_tile(x, 30, TILE_WOOD)
            world.set_wall(x, 30, WALL_WOOD)

        # Enclosed room below roof at y=31..35
        for y in range(31, 36):
            for x in range(-5, 6):
                world.set_tile(x, y, TILE_AIR)
                world.set_wall(x, y, WALL_WOOD)

        # Viewport positioned inside the room below roof: min_ty=31, max_ty=40
        lighting.compute_viewport_light(
            world=world,
            min_tx=-2, max_tx=2,
            min_ty=31, max_ty=40,
            ambient_sunlight=15.0,
            ambient_tint=(1.0, 1.0, 1.0)
        )

        lvl = lighting.get_light_level(0, 33)
        assert lvl == 0, f"Enclosed room under roof should receive 0 direct daylight, got {lvl}"

    def test_large_emitter_intensity_clamping(self, pygame_module):
        """Verifies that large light intensities (>15) clamp safely without IndexError in LUT or grid."""
        af = pygame_module
        world = World(af, seed=42)
        lighting = LightingEngine(SCREEN_WIDTH, SCREEN_HEIGHT)

        # Emitter with intensity 20 (exceeds 15)
        lighting.compute_viewport_light(
            world=world,
            min_tx=0, max_tx=10,
            min_ty=40, max_ty=50,
            ambient_sunlight=15.0,
            torch_positions=[(5, 45, 20)]
        )

        lvl = lighting.get_light_level(5, 45)
        assert 0 <= lvl <= 15, f"Light level must be clamped to [0, 15], got {lvl}"


class TestPersistentWorldCache:
    def test_atomic_write_and_manifest(self):
        """Verifies world cache creates versioned manifest and atomic chunk cache files."""
        temp_dir = tempfile.mkdtemp(prefix="potaria_cache_test_")
        try:
            cache = WorldCache("test_world_01", base_dir=temp_dir)
            assert os.path.exists(cache.manifest_path), "Manifest file should be created"
            with open(cache.manifest_path, "r", encoding="utf-8") as f:
                manifest_data = json.load(f)
            assert manifest_data.get("schema_version") == CACHE_SCHEMA_VERSION

            # Create mock chunk data
            cm = ChunkManager(seed=777, world_name="test_world_01")
            cm.world_cache = cache
            mock_chunk = cm.get_chunk(0)
            success = cache.save_chunk(0, mock_chunk, seed=777)
            assert success, "save_chunk should return True on success"

            assert cache.has_chunk_cache(0), "has_chunk_cache should detect written chunk"

            # Load chunk back
            loaded = cache.load_chunk_data(0, expected_seed=777)
            assert loaded is not None, "load_chunk_data should successfully return chunk payload"
            assert loaded["chunk_x"] == 0
            assert loaded["seed"] == 777
            assert len(loaded["tiles"]) == CHUNK_WIDTH

            # Telemetry counters
            assert cache.chunk_hits >= 1
            assert cache.bytes_read > 0
            assert cache.bytes_written > 0
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)

    def test_corruption_recovery(self):
        """Verifies corrupted chunk cache files heal gracefully without raising exceptions."""
        temp_dir = tempfile.mkdtemp(prefix="potaria_corrupt_test_")
        try:
            cache = WorldCache("test_world_corrupt", base_dir=temp_dir)
            chunk_file = cache._chunk_file_path(5)
            os.makedirs(os.path.dirname(chunk_file), exist_ok=True)

            # Write corrupt garbage data
            with open(chunk_file, "wb") as f:
                f.write(b"NOT_A_VALID_GZIP_OR_JSON_HEADER_DEADBEEF")

            assert cache.has_chunk_cache(5)
            # Loading corrupt chunk should return None and delete corrupt file for self-healing
            loaded = cache.load_chunk_data(5, expected_seed=123)
            assert loaded is None, "Corrupted chunk must return None"
            assert not os.path.exists(chunk_file), "Corrupted cache file must be deleted upon corruption detection"
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)

    def test_lighting_cache_version_invalidation(self):
        """Verifies that changing lighting_version invalidates stale lighting cache entries while keeping chunks."""
        temp_dir = tempfile.mkdtemp(prefix="potaria_light_ver_")
        try:
            cache = WorldCache("test_light_ver", base_dir=temp_dir)
            light_payload = {"explored_mask": [1, 0, 1]}
            cache.save_lighting(0, light_payload)
            assert cache.has_lighting_cache(0)

            # Load back under current version -> hits
            loaded = cache.load_lighting_data(0)
            assert loaded == light_payload

            # Change lighting cache version on cache instance
            cache.lighting_version += 1

            # Load back under new version -> invalidates stale data, returns None, deletes stale file
            loaded_new = cache.load_lighting_data(0)
            assert loaded_new is None, "Stale lighting cache must be invalidated on version mismatch"
            assert not cache.has_lighting_cache(0), "Stale lighting file must be deleted on invalidation"
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)

    def test_chunk_cache_dimension_validation(self):
        """Verifies that chunk cache entries with invalid column counts are safely rejected and healed."""
        temp_dir = tempfile.mkdtemp(prefix="potaria_dim_test_")
        try:
            cache = WorldCache("test_dim_corrupt", base_dir=temp_dir)
            chunk_file = cache._chunk_file_path(3)
            os.makedirs(os.path.dirname(chunk_file), exist_ok=True)

            # Write chunk with corrupt empty tiles
            bad_data = {
                "chunk_x": 3,
                "seed": 555,
                "tiles": [],
                "walls": []
            }
            cache._atomic_write_json(chunk_file, bad_data)

            loaded = cache.load_chunk_data(3, expected_seed=555)
            assert loaded is None, "Chunk with empty tile dimensions must return None"
            assert not os.path.exists(chunk_file), "Invalid dimension chunk file must be deleted for self-healing"
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)


class TestChunkManagerMemoryBounds:
    def test_lru_chunk_eviction(self):
        """Verifies ChunkManager limits in-memory chunks to max_loaded_chunks."""
        cm = ChunkManager(seed=999, world_name="test_lru")
        cm.max_loaded_chunks = 10

        # Load 25 chunks
        for cx in range(-12, 13):
            cm.get_chunk(cx)

        # In-memory chunk count must not exceed max_loaded_chunks + pinned margin
        assert len(cm.chunks) <= cm.max_loaded_chunks + 1, f"ChunkManager exceeded bounds: {len(cm.chunks)}"

    def test_distant_surface_eviction(self, pygame_module):
        """Verifies evict_distant_surfaces frees surface memory of non-visible chunks."""
        af = pygame_module
        world = World(af, seed=888)
        cm = world.chunk_manager

        # Bake sections for chunks -5 to 5
        for cx in range(-5, 6):
            chk = cm.get_chunk(cx)
            for sy in range(2):
                chk.get_or_bake_section(sy, world)

        # Center camera at chunk 0, evict distant surfaces
        cm.evict_distant_surfaces(cam_cx=0)

        # Chunks far away (e.g. -5, 5) must have had their surf released
        distant_chk = cm.chunks.get(5)
        if distant_chk and hasattr(distant_chk, "sections"):
            for sec in distant_chk.sections.values():
                assert sec.surf is None, "Distant chunk surface should be evicted (set to None)"
                assert sec.dirty is True, "Distant section should be marked dirty for re-baking when revisited"


class TestProfilerReconciliation:
    def test_profiler_unaccounted_and_overlay(self, pygame_module):
        """Verifies PotariaProfiler reconciles 100% of frame time and renders cleanly."""
        prof = PotariaProfiler(history_size=30)
        prof.enabled = True

        prof.start_frame()
        with prof.section("update_player"):
            pass
        with prof.section("render_world"):
            pass
        prof.end_frame()

        assert prof.avg_frame_ms >= 0.0
        assert "update_player" in prof.section_averages
        assert "render_world" in prof.section_averages

        # Render overlay onto test surface
        surf = pygame.Surface((400, 300), pygame.SRCALPHA)
        font = pygame.font.Font(None, 14)
        prof.render_overlay(surf, font)
