"""
Canonical 7-Tier Rarity Engine for Potaria & Potaria: Root Realm.
Manages rarity tiers, affix slot budgets, stat scaling multipliers, and weighted rarity rolls.
"""

import random
from typing import Dict, Any, Optional


class RarityEngine:
    RANK_ORDER = [
        "common",
        "uncommon",
        "rare",
        "epic",
        "mythic",
        "legendary",
        "ancient",
    ]

    TIERS: Dict[str, Dict[str, Any]] = {
        "common": {
            "name": "Common",
            "rank": 0,
            "affix_count": 0,
            "stat_multiplier": 1.0,
            "weight": 55.0,
            "color": (200, 200, 200),
            "allow_unique_effect": False,
        },
        "uncommon": {
            "name": "Uncommon",
            "rank": 1,
            "affix_count": 1,
            "stat_multiplier": 1.1,
            "weight": 25.0,
            "color": (80, 220, 100),
            "allow_unique_effect": False,
        },
        "rare": {
            "name": "Rare",
            "rank": 2,
            "affix_count": 2,
            "stat_multiplier": 1.25,
            "weight": 12.0,
            "color": (80, 150, 255),
            "allow_unique_effect": False,
        },
        "epic": {
            "name": "Epic",
            "rank": 3,
            "affix_count": 3,
            "stat_multiplier": 1.5,
            "weight": 5.0,
            "color": (185, 90, 255),
            "allow_unique_effect": False,
        },
        "mythic": {
            "name": "Mythic",
            "rank": 4,
            "affix_count": 4,
            "stat_multiplier": 2.0,
            "weight": 2.0,
            "color": (255, 75, 110),
            "allow_unique_effect": True,
        },
        "legendary": {
            "name": "Legendary",
            "rank": 5,
            "affix_count": 5,
            "stat_multiplier": 2.5,
            "weight": 0.85,
            "color": (255, 185, 40),
            "allow_unique_effect": True,
        },
        "ancient": {
            "name": "Ancient",
            "rank": 6,
            "affix_count": 6,
            "stat_multiplier": 3.0,
            "weight": 0.15,
            "color": (0, 240, 230),
            "allow_unique_effect": True,
        },
    }

    def get_tier(self, rarity: str) -> Dict[str, Any]:
        if not rarity:
            return self.TIERS["common"]
        return self.TIERS.get(str(rarity).strip().lower(), self.TIERS["common"])

    def get_rank(self, rarity: str) -> int:
        return int(self.get_tier(rarity)["rank"])

    def is_at_least(self, rarity: str, min_rarity: str) -> bool:
        return self.get_rank(rarity) >= self.get_rank(min_rarity)

    def roll_rarity(
        self,
        rng_seed: Optional[int] = None,
        luck_bonus: float = 0.0,
        min_rarity: str = "Common",
        max_rarity: str = "Ancient",
    ) -> str:
        rng = random.Random(rng_seed) if rng_seed is not None else random.Random()
        min_rank = self.get_rank(min_rarity)
        max_rank = self.get_rank(max_rarity)

        candidates = []
        weights = []
        for key in self.RANK_ORDER:
            tier = self.TIERS[key]
            rank = tier["rank"]
            if min_rank <= rank <= max_rank:
                candidates.append(tier["name"])
                weight = float(tier["weight"])
                if rank >= 2 and luck_bonus > 0:
                    weight *= 1.0 + (luck_bonus * 0.15 * rank)
                weights.append(weight)

        if not candidates:
            return "Common"
        return rng.choices(candidates, weights=weights, k=1)[0]
