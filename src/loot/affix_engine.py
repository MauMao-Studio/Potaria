"""
Data-Driven Multi-Affix Engine for Potaria & Potaria: Root Realm.
Implements the 4-Layer Item Model:
    BASE ITEM + AFFIXES + RARITY + OPTIONAL UNIQUE EFFECT
Supports deterministic seeded rolling, category compatibility, rarity gating,
mutual exclusion validation, dynamic naming, and stat merging.
"""

import copy
import json
import os
import random
from typing import Dict, List, Any, Optional, Union

from src.loot.item_registry import registry, ItemDefinition, map_to_canonical_category
from src.loot.rarity_engine import RarityEngine

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class AffixEngine:
    def __init__(self, affixes_path: Optional[str] = None):
        self.affixes_path = affixes_path or os.path.join(BASE_DIR, "data", "affixes", "affixes.json")
        self.rarity_engine = RarityEngine()
        self.affixes: Dict[str, Dict[str, Any]] = {}
        self.load_affixes()

    def load_affixes(self) -> None:
        if os.path.exists(self.affixes_path):
            with open(self.affixes_path, "r", encoding="utf-8") as f:
                self.affixes = json.load(f)

    def get_affix(self, affix_key: str) -> Optional[Dict[str, Any]]:
        if affix_key in self.affixes:
            return self.affixes[affix_key]
        for k, v in self.affixes.items():
            if v.get("id") == affix_key or k.lower() == affix_key.lower():
                return v
        return None

    def is_affix_compatible(
        self,
        affix_key: str,
        item_category: str,
        rarity: str,
        already_selected: Optional[List[str]] = None,
    ) -> bool:
        aff = self.get_affix(affix_key)
        if not aff:
            return False

        allowed_cats = [c.lower() for c in aff.get("allowed_cats", [])]
        if allowed_cats and item_category.lower() not in allowed_cats:
            canon = map_to_canonical_category("", item_category).lower()
            if canon not in allowed_cats:
                return False

        canon = map_to_canonical_category("", item_category).lower()
        if canon == "weapon" or item_category.lower() == "weapon":
            stat_mods = aff.get("stat_mods", {})
            defensive_keys = {"def", "defense", "armor", "dmg_reduction", "dmg_reduc", "damage_reduction", "knockback_res", "magic_resist"}
            if any(k in stat_mods for k in defensive_keys):
                return False

        min_rarity = aff.get("min_rarity", "Uncommon")
        if not self.rarity_engine.is_at_least(rarity, min_rarity):
            return False

        if already_selected:
            excludes = set(aff.get("excludes", []))
            for existing_key in already_selected:
                if existing_key == affix_key or existing_key in excludes:
                    return False
                existing_aff = self.get_affix(existing_key)
                if existing_aff and affix_key in existing_aff.get("excludes", []):
                    return False
                # At most one suffix per item to keep item naming clean
                if aff.get("type") == "suffix" and existing_aff and existing_aff.get("type") == "suffix":
                    return False

        return True

    def generate_name(self, base_name: str, applied_affixes: List[str]) -> str:
        prefixes: List[str] = []
        suffixes: List[str] = []
        for aff_key in applied_affixes:
            aff = self.get_affix(aff_key)
            if not aff:
                continue
            display_name = aff.get("name", aff_key)
            if aff.get("type") == "prefix":
                prefixes.append(display_name)
            elif aff.get("type") == "suffix":
                suffixes.append(display_name)

        name = base_name
        if prefixes:
            name = " ".join(prefixes) + " " + name
        if suffixes:
            name = name + " " + " ".join(suffixes)
        return name

    def roll_affixes(
        self,
        item_id: str,
        rarity: str,
        rng_seed: Optional[int] = None,
        max_affixes: Optional[int] = None,
    ) -> List[str]:
        rng = random.Random(rng_seed) if rng_seed is not None else random.Random()
        tier_info = self.rarity_engine.get_tier(rarity)
        target_count = max_affixes if max_affixes is not None else int(tier_info.get("affix_count", 0))
        if target_count <= 0:
            return []

        item_def = registry.get(item_id)
        item_category = item_def.category if item_def else "weapon"

        pool = list(self.affixes.keys())
        rng.shuffle(pool)

        selected: List[str] = []
        for candidate in pool:
            if len(selected) >= target_count:
                break
            if self.is_affix_compatible(candidate, item_category, rarity, selected):
                selected.append(candidate)

        return selected

    def generate_loot(
        self,
        base_item: Union[str, Dict[str, Any], ItemDefinition],
        rarity: Optional[str] = None,
        rng_seed: Optional[int] = None,
        forced_affixes: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        Constructs a 4-layer item dictionary:
            Layer 1: Base Item
            Layer 2: Applied Affixes (prefixes + suffixes + stat_mods)
            Layer 3: Rarity Tier & Stat Scaling
            Layer 4: Optional Unique Effect (preserved on Mythic/Legendary/Ancient)
        """
        if isinstance(base_item, str):
            item_def = registry.get(base_item)
            if item_def:
                item_dict = item_def.to_dict()
                item_id = item_def.id
            else:
                item_id = base_item
                item_dict = {
                    "id": base_item,
                    "name": base_item.replace("_", " ").title(),
                    "category": "weapon",
                    "rarity": rarity or "Common",
                    "stats": {"atk": 10},
                }
        elif isinstance(base_item, ItemDefinition):
            item_dict = base_item.to_dict()
            item_id = base_item.id
        elif isinstance(base_item, dict):
            item_dict = copy.deepcopy(base_item)
            item_id = str(item_dict.get("id", "unknown_item"))
        else:
            raise TypeError(f"Unsupported base_item type: {type(base_item)}")

        resolved_rarity = rarity or item_dict.get("rarity", "Common")
        tier_info = self.rarity_engine.get_tier(resolved_rarity)
        canonical_rarity = tier_info["name"]
        multiplier = float(tier_info.get("stat_multiplier", 1.0))

        if forced_affixes is not None:
            applied_affixes = list(forced_affixes)
        else:
            applied_affixes = self.roll_affixes(item_id, canonical_rarity, rng_seed)

        base_name = item_dict.get("base_name") or item_dict.get("name", item_id)
        full_name = self.generate_name(base_name, applied_affixes)

        # Merge and scale stats
        base_stats = copy.deepcopy(item_dict.get("stats", {}))
        for k in ("atk", "def", "crit", "speed", "mp_cost", "hp_bonus", "heal", "mana"):
            if k in item_dict and k not in base_stats:
                base_stats[k] = item_dict[k]

        merged_stats: Dict[str, Any] = {}
        for stat_key, val in base_stats.items():
            if isinstance(val, (int, float)) and stat_key in ("atk", "def", "hp_bonus"):
                scaled = int(round(val * multiplier)) if isinstance(val, int) else round(val * multiplier, 2)
                merged_stats[stat_key] = max(val, scaled) if val > 0 else scaled
            else:
                merged_stats[stat_key] = val

        affix_details: List[Dict[str, Any]] = []
        for aff_key in applied_affixes:
            aff = self.get_affix(aff_key)
            if not aff:
                continue
            affix_details.append({
                "key": aff_key,
                "id": aff.get("id", aff_key.lower()),
                "name": aff.get("name", aff_key),
                "type": aff.get("type", "prefix"),
                "power_type": aff.get("power_type", "stat"),
                "stat_mods": copy.deepcopy(aff.get("stat_mods", {})),
                "desc": aff.get("desc", ""),
            })
            for mod_key, mod_val in aff.get("stat_mods", {}).items():
                if isinstance(mod_val, (int, float)):
                    cur = merged_stats.get(mod_key, 0)
                    merged_stats[mod_key] = round(cur + mod_val, 3) if isinstance(mod_val, float) else int(cur + mod_val)
                else:
                    merged_stats[mod_key] = mod_val

        result = copy.deepcopy(item_dict)
        result["id"] = item_id
        result["base_id"] = item_id
        result["base_name"] = base_name
        result["name"] = full_name
        result["rarity"] = canonical_rarity
        result["affixes"] = applied_affixes
        result["affix_details"] = affix_details
        result["stats"] = merged_stats

        for stat_key, stat_val in merged_stats.items():
            result[stat_key] = stat_val

        # Layer 4: Optional Unique Effect gating
        if tier_info.get("allow_unique_effect", False):
            result["unique_effect"] = item_dict.get("unique_effect") or item_dict.get("effects") or []
        else:
            result["unique_effect"] = []

        return result
