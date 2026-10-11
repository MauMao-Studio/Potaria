"""
Potaria - World-Scoped Exploration Cache Manager
Saves baked chunk surface data, generated terrain, sky strata, explored fog-of-war masks,
and local lighting snapshots dynamically under saves/<world_name>/cache/:
  - saves/<world_name>/cache/chunks/   (Region/chunk terrain data)
  - saves/<world_name>/cache/lighting/ (Explored fog-of-war & baked light masks)

Enables rapid chunk streaming, near-instant world loads, and persistent player exploration
identical to Minecraft region/anvil architectures.
Developer: Kurados
"""

import os
import json
import zlib


def clean_folder_name(name):
    clean = "".join(c for c in str(name) if c.isalnum() or c in (" ", "_", "-")).strip()
    return clean if clean else "world"


class WorldCache:
    """Manages disk caching of explored chunks and lighting data within a world save folder."""

    def __init__(self, world_name="Spud World", base_dir="saves"):
        self.base_dir = base_dir
        self.world_name = world_name
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
        try:
            os.makedirs(self.chunks_dir, exist_ok=True)
            os.makedirs(self.lighting_dir, exist_ok=True)
        except Exception:
            pass

    def _chunk_file_path(self, chunk_x):
        return os.path.join(self.chunks_dir, f"chunk_{chunk_x}.json")

    def _lighting_file_path(self, chunk_x):
        return os.path.join(self.lighting_dir, f"light_{chunk_x}.json")

    def has_chunk_cache(self, chunk_x):
        return os.path.isfile(self._chunk_file_path(chunk_x))

    def load_chunk_data(self, chunk_x):
        """Loads cached chunk dictionary from disk, or None if not cached or invalid."""
        path = self._chunk_file_path(chunk_x)
        if not os.path.isfile(path):
            return None
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            return data
        except Exception as e:
            return None

    def save_chunk(self, chunk_x, chunk, seed=None):
        """Serializes chunk tiles, walls, sky structures, and column metadata to cache."""
        try:
            path = self._chunk_file_path(chunk_x)
            
            # Serialize sky_tiles and sky_walls (tuples -> string keys)
            sky_t = {f"{k[0]},{k[1]}": v for k, v in getattr(chunk, "sky_tiles", {}).items()}
            sky_w = {f"{k[0]},{k[1]}": v for k, v in getattr(chunk, "sky_walls", {}).items()}

            chunk_seed = seed if seed is not None else getattr(chunk, "seed", None)

            payload = {
                "chunk_x": chunk_x,
                "seed": chunk_seed,
                "surface_heights": getattr(chunk, "surface_heights", []),
                "col_biomes": getattr(chunk, "col_biomes", []),
                "tiles": chunk.tiles,
                "walls": chunk.walls,
                "sky_tiles": sky_t,
                "sky_walls": sky_w,
            }
            with open(path, "w", encoding="utf-8") as f:
                json.dump(payload, f)
            return True
        except Exception as e:
            return False

    def has_lighting_cache(self, chunk_x):
        return os.path.isfile(self._lighting_file_path(chunk_x))

    def load_lighting_data(self, chunk_x):
        path = self._lighting_file_path(chunk_x)
        if not os.path.isfile(path):
            return None
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return None

    def save_lighting(self, chunk_x, lighting_data):
        """Saves explored fog-of-war masks or lighting snapshot for chunk."""
        try:
            path = self._lighting_file_path(chunk_x)
            with open(path, "w", encoding="utf-8") as f:
                json.dump(lighting_data, f)
            return True
        except Exception:
            return False

    def get_cached_chunk_count(self):
        try:
            return len([f for f in os.listdir(self.chunks_dir) if f.endswith(".json")])
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

    def clear_cache(self):
        """Clears all cached chunk and lighting files for this world."""
        for d in (self.chunks_dir, self.lighting_dir):
            if os.path.exists(d):
                for f in os.listdir(d):
                    try:
                        os.remove(os.path.join(d, f))
                    except Exception:
                        pass
