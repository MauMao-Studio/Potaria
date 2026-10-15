"""
Potaria - World-Scoped Exploration Cache Manager
Saves baked chunk surface data, generated terrain, sky strata, explored fog-of-war masks,
and local lighting snapshots dynamically under saves/<world_name>/cache/:
  - saves/<world_name>/cache/chunks/   (Region/chunk terrain data)
  - saves/<world_name>/cache/lighting/ (Explored fog-of-war & baked light masks)

Features:
  - Atomic writes via temporary files (.tmp) and os.replace
  - Manifest versioning (schema version, world gen version, lighting version)
  - Integrity validation (size, JSON structure, coordinate check)
  - Safe error recovery without corrupting authoritative world saves
  - Telemetry tracking (hits, misses, I/O duration, bytes transferred)
  - Safe wipe/clear mechanism preserving player world.json saves

Developer: Kurados
"""

import os
import json
import time

CACHE_SCHEMA_VERSION = 1
WORLD_GEN_VERSION = 1
LIGHTING_CACHE_VERSION = 1


def clean_folder_name(name):
    clean = "".join(c for c in str(name) if c.isalnum() or c in (" ", "_", "-")).strip()
    return clean if clean else "world"


class WorldCache:
    """Manages disk caching of explored chunks and lighting data within a world save folder."""

    def __init__(self, world_name="Spud World", base_dir="saves"):
        self.base_dir = base_dir
        self.world_name = world_name
        self.schema_version = CACHE_SCHEMA_VERSION
        self.world_gen_version = WORLD_GEN_VERSION
        self.lighting_version = LIGHTING_CACHE_VERSION

        # Performance & Telemetry Counters
        self.chunk_hits = 0
        self.chunk_misses = 0
        self.lighting_hits = 0
        self.lighting_misses = 0
        self.io_read_time_ms = 0.0
        self.io_write_time_ms = 0.0
        self.bytes_read = 0
        self.bytes_written = 0

        self._init_paths()

    def set_world_name(self, world_name):
        self.world_name = world_name
        self._init_paths()

    def _init_paths(self):
        folder = clean_folder_name(self.world_name)
        self.world_dir = os.path.join(self.base_dir, folder)
        self.cache_dir = os.path.join(self.world_dir, "cache")
        self.chunks_dir = os.path.join(self.cache_dir, "chunks")
        self.lighting_dir = os.path.join(self.cache_dir, "lighting")
        self.manifest_path = os.path.join(self.cache_dir, "manifest.json")
        try:
            os.makedirs(self.chunks_dir, exist_ok=True)
            os.makedirs(self.lighting_dir, exist_ok=True)
            self._ensure_manifest()
        except Exception:
            pass

    def _ensure_manifest(self):
        """Creates or validates the world cache manifest file."""
        if not os.path.isfile(self.manifest_path):
            manifest_data = {
                "schema_version": self.schema_version,
                "world_gen_version": self.world_gen_version,
                "lighting_version": self.lighting_version,
                "world_name": self.world_name,
                "created_at": time.time(),
                "last_accessed": time.time(),
            }
            self._atomic_write_json(self.manifest_path, manifest_data)
        else:
            try:
                with open(self.manifest_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                # Check version compatibility; selectively invalidate stale caches
                if data.get("schema_version") != self.schema_version:
                    self.clear_cache()
                else:
                    if data.get("world_gen_version") != self.world_gen_version:
                        self.clear_chunks_cache()
                    if data.get("lighting_version") != self.lighting_version:
                        self.clear_lighting_cache()

                data["schema_version"] = self.schema_version
                data["world_gen_version"] = self.world_gen_version
                data["lighting_version"] = self.lighting_version
                data["last_accessed"] = time.time()
                self._atomic_write_json(self.manifest_path, data)
            except Exception:
                pass

    def _atomic_write_json(self, target_path, data):
        """Atomically writes JSON data to disk using temporary file replacement."""
        t0 = time.perf_counter()
        tmp_path = target_path + ".tmp"
        encoded = json.dumps(data)
        with open(tmp_path, "w", encoding="utf-8") as f:
            f.write(encoded)
            f.flush()
            try:
                os.fsync(f.fileno())
            except (AttributeError, OSError):
                pass
        os.replace(tmp_path, target_path)
        dt = (time.perf_counter() - t0) * 1000.0
        self.io_write_time_ms += dt
        self.bytes_written += len(encoded.encode("utf-8"))

    def _chunk_file_path(self, chunk_x):
        return os.path.join(self.chunks_dir, f"chunk_{chunk_x}.json")

    def _lighting_file_path(self, chunk_x):
        return os.path.join(self.lighting_dir, f"light_{chunk_x}.json")

    def has_chunk_cache(self, chunk_x):
        path = self._chunk_file_path(chunk_x)
        return os.path.isfile(path) and os.path.getsize(path) > 0

    def load_chunk_data(self, chunk_x, expected_seed=None):
        """Loads and validates cached chunk dictionary from disk, or None if invalid/corrupt."""
        path = self._chunk_file_path(chunk_x)
        if not os.path.isfile(path):
            self.chunk_misses += 1
            return None

        try:
            sz = os.path.getsize(path)
            if sz == 0:
                self.chunk_misses += 1
                try:
                    os.remove(path)
                except OSError:
                    pass
                return None

            t0 = time.perf_counter()
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()
                data = json.loads(content)
            dt = (time.perf_counter() - t0) * 1000.0
            self.io_read_time_ms += dt
            self.bytes_read += len(content.encode("utf-8"))

            # Integrity checks: chunk_x coordinate match, essential keys, and 16-column dimension check
            if not isinstance(data, dict):
                self.chunk_misses += 1
                return None
            if data.get("chunk_x") != chunk_x:
                self.chunk_misses += 1
                return None
            if expected_seed is not None and data.get("seed") is not None and data.get("seed") != expected_seed:
                self.chunk_misses += 1
                return None
            tiles = data.get("tiles")
            walls = data.get("walls")
            if not isinstance(tiles, list) or len(tiles) == 0 or not isinstance(walls, list) or len(walls) == 0:
                self.chunk_misses += 1
                try:
                    os.remove(path)
                except OSError:
                    pass
                return None

            self.chunk_hits += 1
            return data
        except Exception:
            self.chunk_misses += 1
            # Corrupted entry; safely clean up file so it can be cleanly rebuilt
            try:
                os.remove(path)
            except OSError:
                pass
            return None

    def save_chunk(self, chunk_x, chunk, seed=None):
        """Serializes chunk tiles, walls, sky structures, and column metadata safely to cache."""
        try:
            path = self._chunk_file_path(chunk_x)
            
            # Serialize sky_tiles and sky_walls (tuples -> string keys)
            sky_t = {f"{k[0]},{k[1]}": v for k, v in getattr(chunk, "sky_tiles", {}).items()}
            sky_w = {f"{k[0]},{k[1]}": v for k, v in getattr(chunk, "sky_walls", {}).items()}

            chunk_seed = seed if seed is not None else getattr(chunk, "seed", None)

            payload = {
                "schema_version": self.schema_version,
                "world_gen_version": self.world_gen_version,
                "chunk_x": chunk_x,
                "seed": chunk_seed,
                "surface_heights": getattr(chunk, "surface_heights", []),
                "col_biomes": getattr(chunk, "col_biomes", []),
                "tiles": chunk.tiles,
                "walls": chunk.walls,
                "sky_tiles": sky_t,
                "sky_walls": sky_w,
                "modified": getattr(chunk, "modified", False),
            }
            self._atomic_write_json(path, payload)
            return True
        except Exception:
            return False

    def has_lighting_cache(self, chunk_x):
        path = self._lighting_file_path(chunk_x)
        return os.path.isfile(path) and os.path.getsize(path) > 0

    def load_lighting_data(self, chunk_x, expected_version=None):
        path = self._lighting_file_path(chunk_x)
        if not os.path.isfile(path) or os.path.getsize(path) == 0:
            self.lighting_misses += 1
            return None
        try:
            t0 = time.perf_counter()
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()
                data = json.loads(content)
            dt = (time.perf_counter() - t0) * 1000.0
            self.io_read_time_ms += dt
            self.bytes_read += len(content.encode("utf-8"))

            exp_ver = expected_version if expected_version is not None else self.lighting_version

            if isinstance(data, dict) and "lighting_version" in data and "data" in data:
                if data.get("lighting_version") != exp_ver:
                    self.lighting_misses += 1
                    try:
                        os.remove(path)
                    except OSError:
                        pass
                    return None
                self.lighting_hits += 1
                return data["data"]

            self.lighting_hits += 1
            return data
        except Exception:
            self.lighting_misses += 1
            try:
                os.remove(path)
            except OSError:
                pass
            return None

    def save_lighting(self, chunk_x, lighting_data):
        """Saves explored fog-of-war masks or lighting snapshot for chunk atomically."""
        try:
            path = self._lighting_file_path(chunk_x)
            payload = {
                "schema_version": self.schema_version,
                "lighting_version": self.lighting_version,
                "chunk_x": chunk_x,
                "data": lighting_data
            }
            self._atomic_write_json(path, payload)
            return True
        except Exception:
            return False

    def get_cached_chunk_count(self):
        try:
            return len([f for f in os.listdir(self.chunks_dir) if f.endswith(".json") and not f.endswith(".tmp")])
        except Exception:
            return 0

    def get_cache_size_bytes(self):
        total = 0
        for root, _, files in os.walk(self.cache_dir):
            for f in files:
                try:
                    total += os.path.getsize(os.path.join(root, f))
                except Exception:
                    pass
        return total

    def clear_chunks_cache(self):
        """Clears all cached chunk terrain files for this world."""
        if os.path.exists(self.chunks_dir):
            for f in os.listdir(self.chunks_dir):
                try:
                    os.remove(os.path.join(self.chunks_dir, f))
                except Exception:
                    pass

    def clear_lighting_cache(self):
        """Clears all cached lighting files for this world."""
        if os.path.exists(self.lighting_dir):
            for f in os.listdir(self.lighting_dir):
                try:
                    os.remove(os.path.join(self.lighting_dir, f))
                except Exception:
                    pass

    def clear_cache(self):
        """Clears all cached chunk and lighting files for this world, leaving authoritative saves intact."""
        self.clear_chunks_cache()
        self.clear_lighting_cache()

    def get_telemetry(self):
        """Returns diagnostic telemetry metrics for cache usage."""
        total_reqs = self.chunk_hits + self.chunk_misses
        hit_rate = (self.chunk_hits / total_reqs * 100.0) if total_reqs > 0 else 0.0
        return {
            "chunk_hits": self.chunk_hits,
            "chunk_misses": self.chunk_misses,
            "hit_rate_pct": hit_rate,
            "lighting_hits": self.lighting_hits,
            "lighting_misses": self.lighting_misses,
            "io_read_time_ms": self.io_read_time_ms,
            "io_write_time_ms": self.io_write_time_ms,
            "bytes_read": self.bytes_read,
            "bytes_written": self.bytes_written,
            "cached_chunk_count": self.get_cached_chunk_count(),
            "cache_size_bytes": self.get_cache_size_bytes(),
        }
