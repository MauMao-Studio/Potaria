"""
3-Path Loot Acquisition System for Potaria & Potaria: Root Realm.
Supports:
  1. Random Drops (category & level filtered from the 1,461-item registry)
  2. Targeted Drops (boss-specific and biome-specific tables in data/loot_tables/loot_tables.json)
  3. Guaranteed Milestone Drops (first-kill and quest progression rewards)
"""

import json
import os
import random
from typing import Dict, Any, Optional, Union

from src.loot.item_registry import registry, map_to_canonical_category
from src.loot.affix_engine import AffixEngine
from src.loot.rarity_engine import RarityEngine

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class LootSystem:
    def __init__(self, tables_path: Optional[str] = None):
        self.tables_path = tables_path or os.path.join(BASE_DIR, "data", "loot_tables", "loot_tables.json")
        self.affix_engine = AffixEngine()
        self.rarity_engine = RarityEngine()
        self.loot_tables: Dict[str, Any] = {}
        self.load_tables()

    def load_tables(self) -> None:
        if os.path.exists(self.tables_path):
            with open(self.tables_path, "r", encoding="utf-8") as f:
                self.loot_tables = json.load(f)

    def roll_random_loot(
        self,
        source_category: str,
        level: int = 1,
        rng_seed: Optional[int] = None,
        as_instance: bool = False,
    ) -> Optional[Union[str, Dict[str, Any]]]:
        rng = random.Random(rng_seed) if rng_seed is not None else random.Random()
        canon_cat = map_to_canonical_category("", source_category)
        items = [
            k for k, v in registry.items.items()
            if v.category == canon_cat or v.raw_category == source_category.lower()
        ]
        if not items:
            return None
        chosen_id = rng.choice(items)
        if as_instance:
            rolled_rarity = self.rarity_engine.roll_rarity(rng_seed=rng.randint(1, 10**9))
            return self.affix_engine.generate_loot(chosen_id, rarity=rolled_rarity, rng_seed=rng.randint(1, 10**9))
        return chosen_id

    def roll_targeted_loot(
        self,
        source_id: str,
        rng_seed: Optional[int] = None,
        as_instance: bool = False,
    ) -> Optional[Union[str, Dict[str, Any]]]:
        rng = random.Random(rng_seed) if rng_seed is not None else random.Random()
        key = str(source_id).strip().lower()

        # Check flat 'targeted' list first
        targeted_list = self.loot_tables.get("targeted", {}).get(key, [])
        if targeted_list:
            chosen_id = rng.choice(targeted_list)
            if as_instance:
                return self.affix_engine.generate_loot(chosen_id, rng_seed=rng.randint(1, 10**9))
            return chosen_id

        # Check structured 'bosses' or 'biomes' weighted pool
        for section in ("bosses", "biomes"):
            sec_data = self.loot_tables.get(section, {}).get(key)
            if sec_data and "pool" in sec_data:
                pool = sec_data["pool"]
                ids = [entry["item_id"] for entry in pool]
                weights = [float(entry.get("weight", 1.0)) for entry in pool]
                chosen_id = rng.choices(ids, weights=weights, k=1)[0]
                if as_instance:
                    return self.affix_engine.generate_loot(chosen_id, rng_seed=rng.randint(1, 10**9))
                return chosen_id

        return None

    def get_guaranteed_milestone_loot(
        self,
        milestone_id: str,
        rng_seed: Optional[int] = None,
        as_instance: bool = False,
    ) -> Optional[Union[str, Dict[str, Any]]]:
        key = str(milestone_id).strip().lower()
        chosen_id = self.loot_tables.get("milestone", {}).get(key)
        if not chosen_id:
            m_data = self.loot_tables.get("milestones", {}).get(key)
            if isinstance(m_data, dict):
                chosen_id = m_data.get("guaranteed_item")
            elif isinstance(m_data, str):
                chosen_id = m_data
        if not chosen_id:
            return None
        if as_instance:
            m_info = self.loot_tables.get("milestones", {}).get(key, {})
            forced = m_info.get("fixed_affixes") if isinstance(m_info, dict) else None
            rarity = m_info.get("rarity") if isinstance(m_info, dict) else None
            return self.affix_engine.generate_loot(chosen_id, rarity=rarity, rng_seed=rng_seed, forced_affixes=forced)
        return chosen_id

    def generate_loot_drop(
        self,
        item_id: str,
        rarity: Optional[str] = None,
        rng_seed: Optional[int] = None,
    ) -> Dict[str, Any]:
        return self.affix_engine.generate_loot(item_id, rarity=rarity, rng_seed=rng_seed)
