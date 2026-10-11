"""
Potaria - Modding & DLC Expansion Engine
Provides a robust, data-driven loader scanning `mods/` and `dlc/` directories
for manifests (`mod.json` / `dlc.json`), loading custom items, recipes, tiles,
mobs, and texture packs seamlessly.
Developer: Kurados
"""

import os
import json
import pygame
from typing import Dict, List, Optional, Any

from src.constants import (
    CAT_TOOL, CAT_WEAPON, CAT_BLOCK, CAT_WALL, CAT_MATERIAL,
    CAT_CONSUMABLE, CAT_SPECIAL, CAT_ACCESSORY, CAT_CURRENCY,
    RARITY_COMMON, RARITY_UNCOMMON, RARITY_RARE, RARITY_EPIC,
    RARITY_MYTHIC, RARITY_LEGENDARY, RARITY_ANCIENT
)
from src.ui.crafting import (
    CRAFT_CAT_ALL, CRAFT_CAT_BUILDING, CRAFT_CAT_EQUIPMENT,
    CRAFT_CAT_SURVIVAL, CRAFT_CAT_FURNITURE, RECIPES
)
from src.ui.inventory import ITEM_REGISTRY

# String normalization maps for mod JSON ease of use
CATEGORY_MAP = {
    "tool": CAT_TOOL,
    "weapon": CAT_WEAPON,
    "block": CAT_BLOCK,
    "wall": CAT_WALL,
    "material": CAT_MATERIAL,
    "consumable": CAT_CONSUMABLE,
    "special": CAT_SPECIAL,
    "accessory": CAT_ACCESSORY,
    "currency": CAT_CURRENCY,
    "cat_tool": CAT_TOOL,
    "cat_weapon": CAT_WEAPON,
    "cat_block": CAT_BLOCK,
    "cat_wall": CAT_WALL,
    "cat_material": CAT_MATERIAL,
    "cat_consumable": CAT_CONSUMABLE,
    "cat_special": CAT_SPECIAL,
    "cat_accessory": CAT_ACCESSORY,
    "cat_currency": CAT_CURRENCY,
}

RARITY_MAP = {
    "common": RARITY_COMMON,
    "uncommon": RARITY_UNCOMMON,
    "rare": RARITY_RARE,
    "epic": RARITY_EPIC,
    "mythic": RARITY_MYTHIC,
    "legendary": RARITY_LEGENDARY,
    "ancient": RARITY_ANCIENT,
    "rarity_common": RARITY_COMMON,
    "rarity_uncommon": RARITY_UNCOMMON,
    "rarity_rare": RARITY_RARE,
    "rarity_epic": RARITY_EPIC,
    "rarity_mythic": RARITY_MYTHIC,
    "rarity_legendary": RARITY_LEGENDARY,
    "rarity_ancient": RARITY_ANCIENT,
}

CRAFT_CAT_MAP = {
    "all": CRAFT_CAT_ALL,
    "building": CRAFT_CAT_BUILDING,
    "equipment": CRAFT_CAT_EQUIPMENT,
    "survival": CRAFT_CAT_SURVIVAL,
    "furniture": CRAFT_CAT_FURNITURE,
    "craft_cat_all": CRAFT_CAT_ALL,
    "craft_cat_building": CRAFT_CAT_BUILDING,
    "craft_cat_equipment": CRAFT_CAT_EQUIPMENT,
    "craft_cat_survival": CRAFT_CAT_SURVIVAL,
    "craft_cat_furniture": CRAFT_CAT_FURNITURE,
}


class ModManifest:
    """Represents a discovered Mod or DLC manifest."""
    def __init__(
        self,
        content_id: str,
        name: str,
        version: str = "1.0.0",
        author: str = "Unknown",
        description: str = "",
        content_type: str = "mod",
        enabled: bool = True,
        directory: str = "",
        manifest_file: str = "",
        items: Optional[Any] = None,
        recipes: Optional[List[Dict]] = None,
        tiles: Optional[Any] = None,
        mobs: Optional[Any] = None,
        textures: Optional[Dict[str, str]] = None,
        raw_data: Optional[Dict] = None,
    ):
        self.id = content_id
        self.name = name
        self.version = version
        self.author = author
        self.description = description
        self.type = content_type.lower()
        self.enabled = enabled
        self.directory = directory
        self.manifest_file = manifest_file
        self.items = items or {}
        self.recipes = recipes or []
        self.tiles = tiles or {}
        self.mobs = mobs or {}
        self.textures = textures or {}
        self.raw_data = raw_data or {}

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "version": self.version,
            "author": self.author,
            "description": self.description,
            "type": self.type,
            "enabled": self.enabled,
            "directory": self.directory,
            "items_count": len(self.items) if isinstance(self.items, (dict, list)) else 0,
            "recipes_count": len(self.recipes),
        }


class ModManager:
    """
    Central manager for discovering, loading, and applying community mods
    and official DLC expansions.
    """
    def __init__(self, mods_dir: str = "mods", dlc_dir: str = "dlc"):
        self.mods_dir = mods_dir
        self.dlc_dir = dlc_dir
        self.mods: Dict[str, ModManifest] = {}
        self.dlc: Dict[str, ModManifest] = {}
        self.registered_items: List[str] = []
        self.registered_recipes: List[Dict] = []
        self.registered_textures: Dict[str, str] = {}
        self.ensure_directories()

    def ensure_directories(self):
        """Creates the default mods/ and dlc/ directories if they don't exist."""
        os.makedirs(self.mods_dir, exist_ok=True)
        os.makedirs(self.dlc_dir, exist_ok=True)

    def discover(self) -> None:
        """
        Scans mods/ and dlc/ directories for mod.json and dlc.json manifests.
        """
        self.mods.clear()
        self.dlc.clear()

        # Discover Mods in mods/
        if os.path.exists(self.mods_dir):
            for entry in os.listdir(self.mods_dir):
                mod_path = os.path.join(self.mods_dir, entry)
                if os.path.isdir(mod_path):
                    manifest_file = os.path.join(mod_path, "mod.json")
                    if os.path.exists(manifest_file):
                        manifest = self._parse_manifest(manifest_file, mod_path, default_type="mod")
                        if manifest:
                            self.mods[manifest.id] = manifest

        # Discover DLC in dlc/
        if os.path.exists(self.dlc_dir):
            for entry in os.listdir(self.dlc_dir):
                dlc_path = os.path.join(self.dlc_dir, entry)
                if os.path.isdir(dlc_path):
                    manifest_file = os.path.join(dlc_path, "dlc.json")
                    if not os.path.exists(manifest_file):
                        # Fallback to mod.json if named that way
                        manifest_file = os.path.join(dlc_path, "mod.json")
                    if os.path.exists(manifest_file):
                        manifest = self._parse_manifest(manifest_file, dlc_path, default_type="dlc")
                        if manifest:
                            self.dlc[manifest.id] = manifest

    def _parse_manifest(self, manifest_file: str, directory: str, default_type: str = "mod") -> Optional[ModManifest]:
        """Reads and validates a manifest JSON file."""
        try:
            with open(manifest_file, "r", encoding="utf-8") as f:
                data = json.load(f)

            content_id = data.get("id") or os.path.basename(directory)
            name = data.get("name", content_id)
            version = data.get("version", "1.0.0")
            author = data.get("author", "Unknown")
            description = data.get("description", "")
            content_type = data.get("type", default_type)
            enabled = data.get("enabled", True)
            items = data.get("items", {})
            recipes = data.get("recipes", [])
            tiles = data.get("tiles", {})
            mobs = data.get("mobs", {})
            textures = data.get("textures", {})

            return ModManifest(
                content_id=content_id,
                name=name,
                version=version,
                author=author,
                description=description,
                content_type=content_type,
                enabled=enabled,
                directory=directory,
                manifest_file=manifest_file,
                items=items,
                recipes=recipes,
                tiles=tiles,
                mobs=mobs,
                textures=textures,
                raw_data=data,
            )
        except Exception as e:
            print(f"[ModManager ERROR] Failed to parse manifest at '{manifest_file}': {e}")
            return None

    def load_all(self, asset_factory=None, crafting_system=None) -> Dict[str, Any]:
        """
        Discovers and registers all enabled mods and DLCs.
        """
        self.discover()
        summary = {
            "mods_loaded": 0,
            "dlc_loaded": 0,
            "items_registered": 0,
            "recipes_registered": 0,
            "textures_registered": 0,
        }

        # Load DLCs first
        for dlc_id, manifest in self.dlc.items():
            if manifest.enabled:
                res = self._apply_manifest(manifest, asset_factory, crafting_system)
                summary["dlc_loaded"] += 1
                summary["items_registered"] += res["items"]
                summary["recipes_registered"] += res["recipes"]
                summary["textures_registered"] += res["textures"]

        # Load Mods
        for mod_id, manifest in self.mods.items():
            if manifest.enabled:
                res = self._apply_manifest(manifest, asset_factory, crafting_system)
                summary["mods_loaded"] += 1
                summary["items_registered"] += res["items"]
                summary["recipes_registered"] += res["recipes"]
                summary["textures_registered"] += res["textures"]

        print(
            f"[ModManager] Finished loading content: {summary['mods_loaded']} mods, "
            f"{summary['dlc_loaded']} DLCs ({summary['items_registered']} items, "
            f"{summary['recipes_registered']} recipes, {summary['textures_registered']} textures)."
        )
        return summary

    def _apply_manifest(self, manifest: ModManifest, asset_factory=None, crafting_system=None) -> Dict[str, int]:
        """Applies items, recipes, and textures defined in a manifest."""
        res = {"items": 0, "recipes": 0, "textures": 0}

        # 1. Register Items
        items_dict = manifest.items
        if isinstance(items_dict, list):
            # Convert list of items with "id" key into dict
            items_dict = {item.get("id"): item for item in items_dict if isinstance(item, dict) and "id" in item}

        if isinstance(items_dict, dict):
            for item_id, item_data in items_dict.items():
                if isinstance(item_data, dict):
                    if self.register_item(item_id, item_data, asset_factory=asset_factory):
                        res["items"] += 1

        # 2. Register Recipes
        if isinstance(manifest.recipes, list):
            for recipe in manifest.recipes:
                if isinstance(recipe, dict):
                    if self.register_recipe(recipe, crafting_system=crafting_system):
                        res["recipes"] += 1

        # 3. Register Explicit Textures
        if isinstance(manifest.textures, dict):
            for tex_key, rel_path in manifest.textures.items():
                full_path = os.path.join(manifest.directory, rel_path)
                if os.path.exists(full_path):
                    self.register_texture("items", tex_key, full_path, asset_factory=asset_factory)
                    res["textures"] += 1

        # 4. Auto-discover loose textures in mod's textures/ or items/ directory
        for subfolder in ("textures", "items"):
            folder_path = os.path.join(manifest.directory, subfolder)
            if os.path.isdir(folder_path):
                for fname in os.listdir(folder_path):
                    if fname.lower().endswith(".png"):
                        tex_key = os.path.splitext(fname)[0]
                        full_path = os.path.join(folder_path, fname)
                        if tex_key not in self.registered_textures:
                            self.register_texture("items", tex_key, full_path, asset_factory=asset_factory)
                            res["textures"] += 1

        return res

    def register_item(self, item_id: str, item_data: Dict[str, Any], asset_factory=None) -> bool:
        """
        Safely normalizes and registers an item into ITEM_REGISTRY.
        """
        try:
            # Normalize Category
            cat = item_data.get("cat", CAT_MATERIAL)
            if isinstance(cat, str):
                cat = CATEGORY_MAP.get(cat.lower(), CAT_MATERIAL)

            # Normalize Rarity
            rarity = item_data.get("rarity", RARITY_COMMON)
            if isinstance(rarity, str):
                rarity = RARITY_MAP.get(rarity.lower(), RARITY_COMMON)

            entry = {
                "name": item_data.get("name", item_id.replace("_", " ").title()),
                "cat": cat,
                "power": item_data.get("power", 0),
                "damage": item_data.get("damage", 0),
                "max_stack": item_data.get("max_stack", 99 if cat in (CAT_MATERIAL, CAT_BLOCK, CAT_CONSUMABLE) else 1),
                "tile": item_data.get("tile", None),
                "rarity": rarity,
                "desc": item_data.get("desc", ""),
                "lore": item_data.get("lore", ""),
                "special": item_data.get("special", "")
            }

            # Optional extra fields
            for extra in ("heal", "mana", "defense", "speed", "crit_chance", "buff"):
                if extra in item_data:
                    entry[extra] = item_data[extra]

            ITEM_REGISTRY[item_id] = entry
            if item_id not in self.registered_items:
                self.registered_items.append(item_id)

            # Sync with DataDrivenItemRegistry
            try:
                from src.loot.item_registry import registry as loot_reg, ItemDefinition, map_to_canonical_category
                c_cat = map_to_canonical_category(item_id, entry)
                d_data = {
                    "id": item_id,
                    "name": entry["name"],
                    "category": c_cat,
                    "legacy_category": entry["cat"],
                    "slot": "accessory" if entry["cat"] == CAT_ACCESSORY else ("hand" if entry["cat"] in (CAT_WEAPON, CAT_TOOL) else None),
                    "base_stats": {"damage": entry["damage"], "power": entry["power"]},
                    "weapon_behavior": "melee" if entry["cat"] == CAT_WEAPON else None,
                    "sprite": f"assets/items/{item_id}.png",
                    "rarity": entry["rarity"],
                    "rarity_rules": {"allow_upgrade": c_cat in ("weapon", "armor", "accessory")},
                    "affix_rules": {"allow_affixes": c_cat in ("weapon", "armor", "accessory")},
                    "unique_effect": entry.get("special"),
                    "lore": entry.get("lore", ""),
                    "desc": entry.get("desc", ""),
                    "drop_sources": [],
                    "craft_recipe": None,
                    "craftable": False,
                    "collection_id": f"potadex_{item_id}",
                }
                loot_reg.items[item_id] = ItemDefinition(d_data)
            except Exception:
                pass

            return True
        except Exception as e:
            print(f"[ModManager ERROR] Failed to register item '{item_id}': {e}")
            return False

    def unregister_item(self, item_id: str) -> bool:
        """Removes an item from ITEM_REGISTRY and data-driven registry."""
        if item_id in ITEM_REGISTRY:
            del ITEM_REGISTRY[item_id]
        if item_id in self.registered_items:
            self.registered_items.remove(item_id)
        try:
            from src.loot.item_registry import registry as loot_reg
            if item_id in loot_reg.items:
                del loot_reg.items[item_id]
        except Exception:
            pass
        return True

    def register_recipe(self, recipe_data: Dict[str, Any], crafting_system=None) -> bool:
        """
        Safely normalizes and registers a crafting recipe into RECIPES.
        """
        try:
            result = recipe_data.get("result")
            if not result:
                return False

            count = recipe_data.get("count", 1)
            station = recipe_data.get("station")

            # Normalize Category
            category = recipe_data.get("category", CRAFT_CAT_ALL)
            if isinstance(category, str):
                category = CRAFT_CAT_MAP.get(category.lower(), CRAFT_CAT_ALL)

            # Normalize ingredients list: supports [("item", count)] or [["item", count]] or [{"item": x, "count": y}]
            raw_ingredients = recipe_data.get("ingredients", [])
            ingredients = []
            for ing in raw_ingredients:
                if isinstance(ing, (list, tuple)) and len(ing) >= 2:
                    ingredients.append((str(ing[0]), int(ing[1])))
                elif isinstance(ing, dict) and "item" in ing and "count" in ing:
                    ingredients.append((str(ing["item"]), int(ing["count"])))

            recipe_entry = {
                "result": result,
                "count": count,
                "station": station,
                "category": category,
                "ingredients": ingredients
            }

            RECIPES.append(recipe_entry)
            self.registered_recipes.append(recipe_entry)

            # Sync with DataDrivenItemRegistry
            try:
                from src.loot.item_registry import registry as loot_reg
                if result in loot_reg.items:
                    loot_reg.items[result].craftable = True
                    loot_reg.items[result].craft_recipe = recipe_entry
                loot_reg.recipes_by_item[result] = recipe_entry
            except Exception:
                pass

            if crafting_system and hasattr(crafting_system, "recipes"):
                crafting_system.recipes.append(recipe_entry)

            return True
        except Exception as e:
            print(f"[ModManager ERROR] Failed to register recipe for '{recipe_data.get('result')}': {e}")
            return False

    def unregister_recipe(self, recipe_or_result, crafting_system=None) -> bool:
        """Removes a crafting recipe from RECIPES and data-driven registry."""
        target_res = recipe_or_result if isinstance(recipe_or_result, str) else recipe_or_result.get("result")
        RECIPES[:] = [r for r in RECIPES if r.get("result") != target_res]
        self.registered_recipes = [r for r in self.registered_recipes if r.get("result") != target_res]
        if crafting_system and hasattr(crafting_system, "recipes"):
            crafting_system.recipes[:] = [r for r in crafting_system.recipes if r.get("result") != target_res]
        try:
            from src.loot.item_registry import registry as loot_reg
            if target_res in loot_reg.recipes_by_item:
                del loot_reg.recipes_by_item[target_res]
            if target_res in loot_reg.items:
                loot_reg.items[target_res].craftable = False
                loot_reg.items[target_res].craft_recipe = None
        except Exception:
            pass
        return True

    def unload_all(self, asset_factory=None, crafting_system=None) -> None:
        """Unloads all registered items, recipes, and textures from mods and DLCs."""
        for item_id in list(self.registered_items):
            self.unregister_item(item_id)
        for recipe in list(self.registered_recipes):
            self.unregister_recipe(recipe, crafting_system=crafting_system)
        if asset_factory:
            for key in list(self.registered_textures.keys()):
                if hasattr(asset_factory, "items") and key in asset_factory.items:
                    del asset_factory.items[key]
        self.registered_textures.clear()

    def register_texture(self, category: str, key: str, image_path: str, asset_factory=None) -> bool:
        """
        Loads an external sprite image and registers it into AssetFactory or internal cache.
        """
        try:
            if not os.path.exists(image_path):
                return False

            if not pygame.get_init():
                pygame.init()

            surf = pygame.image.load(image_path)
            if pygame.display.get_init() and pygame.display.get_surface():
                try:
                    surf = surf.convert_alpha()
                except Exception:
                    pass

            self.registered_textures[key] = image_path

            if asset_factory:
                if category == "items" and hasattr(asset_factory, "items"):
                    asset_factory.items[key] = surf
                elif category == "tiles" and hasattr(asset_factory, "tiles"):
                    asset_factory.tiles[key] = surf
                elif category == "walls" and hasattr(asset_factory, "walls"):
                    asset_factory.walls[key] = surf

            return True
        except Exception as e:
            print(f"[ModManager ERROR] Failed to load texture '{image_path}': {e}")
            return False

    def get_mod(self, mod_id: str) -> Optional[ModManifest]:
        return self.mods.get(mod_id)

    def get_dlc(self, dlc_id: str) -> Optional[ModManifest]:
        return self.dlc.get(dlc_id)

    def get_all_mods(self) -> List[ModManifest]:
        return list(self.mods.values())

    def get_all_dlc(self) -> List[ModManifest]:
        return list(self.dlc.values())

    def is_mod_loaded(self, mod_id: str) -> bool:
        return mod_id in self.mods and self.mods[mod_id].enabled

    def is_dlc_loaded(self, dlc_id: str) -> bool:
        return dlc_id in self.dlc and self.dlc[dlc_id].enabled

    def set_content_enabled(self, content_id: str, enabled: bool) -> bool:
        """Enables or disables a mod or DLC manifest and updates manifest on disk."""
        target = self.mods.get(content_id) or self.dlc.get(content_id)
        if not target:
            return False

        target.enabled = enabled
        if target.manifest_file and os.path.exists(target.manifest_file):
            try:
                target.raw_data["enabled"] = enabled
                with open(target.manifest_file, "w", encoding="utf-8") as f:
                    json.dump(target.raw_data, f, indent=2)
            except Exception as e:
                print(f"[ModManager ERROR] Failed to write updated manifest: {e}")
        return True


# Global singleton instance
_instance: Optional[ModManager] = None

def get_mod_manager() -> ModManager:
    global _instance
    if _instance is None:
        _instance = ModManager()
    return _instance
