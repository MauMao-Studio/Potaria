"""
Potaria: Root Realm - Phase 1 Data-Driven Item Registry
Standardizes all 1,461+ items into canonical ItemDefinition schemas while
preserving 100% backward compatibility with ITEM_REGISTRY, world saves, and /give.
Developer: Kurados | Engine: Pure Python 3.13 + Pygame-ce 2.5.8
"""

import json
import os
from typing import Dict, Any, Optional, List, Union

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.ui.inventory import ITEM_REGISTRY, ITEM_ALIASES
from src.ui.crafting import load_craftable_recipes

CANONICAL_CATEGORIES = (
    "weapon",
    "armor",
    "accessory",
    "consumable",
    "material",
    "ammunition",
    "skillbook",
    "quest_key",
    "relic",
)


def map_to_canonical_category(item_id: str, item_data: Union[Dict[str, Any], str]) -> str:
    """Maps legacy ITEM_REGISTRY categories or category strings to the 9 canonical Phase 1 categories."""
    if isinstance(item_data, str):
        raw_cat = item_data.strip().lower()
        rarity = "common"
    else:
        raw_cat = str(item_data.get("cat", "material")).lower()
        rarity = str(item_data.get("rarity", "common")).lower()

    if raw_cat in CANONICAL_CATEGORIES:
        return raw_cat

    iid = (item_id or "").lower()

    if ("arrow" in iid or "ammo" in iid or "bolt" in iid) and raw_cat != "weapon":
        return "ammunition"
    if rarity == "ancient" or "relic" in iid or iid in ("crown_of_potaria", "astral_wrath", "celestial_greatsword"):
        if raw_cat in ("weapon", "armor_head", "armor_chest", "armor_legs", "accessory", "special"):
            return "relic" if raw_cat == "special" else raw_cat.split("_")[0]
    if raw_cat in ("weapon", "tool"):
        return "weapon"
    if raw_cat in ("armor_head", "armor_chest", "armor_legs", "armor"):
        return "armor"
    if raw_cat == "accessory":
        return "accessory"
    if raw_cat == "consumable":
        return "consumable"
    if raw_cat == "skillbook":
        return "skillbook"
    if raw_cat == "special" or "rune" in iid or "keystone" in iid or "shard" in iid:
        return "quest_key"
    return "material"


class ItemDefinition:
    """Canonical 4-Layer Item Base Definition."""

    def __init__(self, data: Dict[str, Any]):
        self.id: str = data.get("id", "")
        self.name: str = data.get("name", self.id)
        self.category: str = data.get("category", "material")
        self.legacy_category: str = data.get("legacy_category", self.category)
        self.raw_category: str = self.legacy_category
        self.slot: Optional[str] = data.get("slot")
        self.base_stats: Dict[str, Any] = data.get("base_stats", {})
        self.stats: Dict[str, Any] = self.base_stats
        self.weapon_behavior: Optional[str] = data.get("weapon_behavior")
        self.sprite: str = data.get("sprite", f"{self.id}.png")
        self.rarity: str = str(data.get("rarity", "common")).lower()
        self.rarity_rules: Dict[str, Any] = data.get("rarity_rules", {})
        self.affix_rules: Dict[str, Any] = data.get("affix_rules", {})
        self.unique_effect: Optional[str] = data.get("unique_effect")
        self.lore: str = data.get("lore", "")
        self.desc: str = data.get("desc", "")
        self.drop_sources: List[str] = data.get("drop_sources", [])
        self.craft_recipe: Optional[Dict[str, Any]] = data.get("craft_recipe")
        self.craftable: bool = bool(data.get("craftable", self.craft_recipe is not None))
        self.collection_id: str = data.get("collection_id", f"col_{self.id}")

    def to_dict(self) -> Dict[str, Any]:
        """Converts definition back into a flat dictionary compatible with ITEM_REGISTRY."""
        d = {
            "id": self.id,
            "name": self.name,
            "cat": self.legacy_category,
            "category": self.category,
            "raw_category": self.raw_category,
            "slot": self.slot,
            "rarity": self.rarity,
            "desc": self.desc,
            "lore": self.lore,
            "unique_effect": self.unique_effect,
            "collection_id": self.collection_id,
            "craft_recipe": self.craft_recipe,
            "craftable": self.craftable,
            "stats": dict(self.base_stats),
        }
        for k, v in self.base_stats.items():
            d[k] = v
        return d


class DataDrivenItemRegistry:
    """Centralized item registry bridging legacy ITEM_REGISTRY and data-driven schemas."""

    def __init__(self):
        self.items: Dict[str, ItemDefinition] = {}
        self.recipes_by_item: Dict[str, Dict[str, Any]] = {}
        self.load_from_legacy_registry()

    def load_from_legacy_registry(self):
        recipes = load_craftable_recipes()
        for r in recipes:
            res_id = r.get("result")
            if res_id:
                self.recipes_by_item[res_id] = r

        for item_id, item_data in ITEM_REGISTRY.items():
            raw_cat = item_data.get("cat", "material")
            canonical_cat = map_to_canonical_category(item_id, item_data)

            slot = None
            if raw_cat == "armor_head":
                slot = "head"
            elif raw_cat == "armor_chest":
                slot = "chest"
            elif raw_cat == "armor_legs":
                slot = "legs"
            elif raw_cat == "accessory":
                slot = "accessory"
            elif raw_cat in ("weapon", "tool"):
                slot = "hand"

            base_stats = {}
            for stat_key in ("damage", "atk", "def", "crit", "speed", "hp", "mp", "mp_regen", "heal", "max_stack"):
                if stat_key in item_data and item_data[stat_key] is not None:
                    base_stats[stat_key] = item_data[stat_key]

            weapon_behavior = item_data.get("subcat") or item_data.get("weapon_behavior")
            if not weapon_behavior and raw_cat == "weapon":
                iid = item_id.lower()
                if "bow" in iid:
                    weapon_behavior = "bow"
                elif "catalyst" in iid:
                    weapon_behavior = "catalyst"
                elif "staff" in iid or "stave" in iid:
                    weapon_behavior = "staff"
                elif "rod" in iid:
                    weapon_behavior = "rod"
                elif "scepter" in iid:
                    weapon_behavior = "scepter"
                else:
                    weapon_behavior = "melee"

            craft_recipe = self.recipes_by_item.get(item_id)
            sprite_folder = "craftable_items" if craft_recipe else "items"

            defn_data = {
                "id": item_id,
                "name": item_data.get("name", item_id),
                "category": canonical_cat,
                "legacy_category": raw_cat,
                "slot": slot,
                "base_stats": base_stats,
                "weapon_behavior": weapon_behavior,
                "sprite": f"assets/{sprite_folder}/{item_id}.png",
                "rarity": item_data.get("rarity", "common"),
                "rarity_rules": {"allow_upgrade": canonical_cat in ("weapon", "armor", "accessory")},
                "affix_rules": {"allow_affixes": canonical_cat in ("weapon", "armor", "accessory")},
                "unique_effect": item_data.get("special"),
                "lore": item_data.get("lore", ""),
                "desc": item_data.get("desc", ""),
                "drop_sources": item_data.get("drop_sources", []),
                "craft_recipe": craft_recipe,
                "craftable": craft_recipe is not None,
                "collection_id": f"potadex_{item_id}",
            }
            self.items[item_id] = ItemDefinition(defn_data)

    def get(self, item_id: str) -> Optional[ItemDefinition]:
        if item_id in self.items:
            return self.items[item_id]
        alias = ITEM_ALIASES.get(item_id)
        if alias and alias in self.items:
            return self.items[alias]
        return None

    def get_by_category(self, category: str) -> List[ItemDefinition]:
        cat_lower = category.lower()
        return [
            v for v in self.items.values()
            if v.category == cat_lower or v.legacy_category == cat_lower
        ]

    def load_schema(self, path: str):
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            items_iter = data.values() if isinstance(data, dict) else data
            for item in items_iter:
                if isinstance(item, dict) and "id" in item:
                    self.items[item["id"]] = ItemDefinition(item)


registry = DataDrivenItemRegistry()
