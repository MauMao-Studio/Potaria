"""
Potaria Equipment Update - Core Data and Rules Engine
Implements:
- Randomized base stats with predefined attributes and min/max ranges
- Persistent item-instance rolls and validation
- Strict rarity-based additional affix slot limits (Epic: 1, Legendary: 1, Mythic: 2, Ancient: 2, Others: 0)
- Progressive set effects (2-piece and full-set thresholds)
- Seven Deadly Sins collection (Pride, Greed, Lust, Envy, Gluttony, Wrath, Sloth)
- Seven Heavenly Virtues collection (Humility, Charity, Chastity, Gratitude, Temperance, Kindness, Diligence)
- Filipino-inspired weapons, sets, and accessories (Kampilan, Panabas, Kris, Balisong, Bangkaw,
  Diwata's Bloom, Bakunawa's Eclipse, Sarimanok Regalia, Tikbalang Trailblazer, Agimat, etc.)
- Special tags registry and theme metadata
- Save file integrity verification and anti-cheat hashing
Developer: Kurados | Engine: Python 3.13 + Pygame-ce 2.5.8
"""

import copy
import hashlib
import hmac
import json
import random
from typing import Dict, Any, List, Optional, Tuple, Union

# -----------------------------------------------------------------------------
# 1. SPECIAL TAGS REGISTRY
# -----------------------------------------------------------------------------

TAG_REGISTRY: Dict[str, Dict[str, Any]] = {
    # Seven Deadly Sins (Dark, dramatic, rich crimson/violet/gold themes)
    "sin_pride": {
        "tag_id": "sin_pride",
        "display_name": "Pride",
        "category": "set_identity",
        "description": "Sovereign of the Sun: Solar brilliance, precision strikes, and execution.",
        "color": (255, 175, 45),
        "badge_bg": (60, 35, 10),
    },
    "sin_greed": {
        "tag_id": "sin_greed",
        "display_name": "Greed",
        "category": "set_identity",
        "description": "The Gilded Devourer: Treasure escalation, coin bounties, and golden momentum.",
        "color": (240, 205, 50),
        "badge_bg": (55, 45, 10),
    },
    "sin_lust": {
        "tag_id": "sin_lust",
        "display_name": "Lust",
        "category": "set_identity",
        "description": "The Enchanter: Status manipulation, captivating charm, and debuff resonance.",
        "color": (240, 90, 170),
        "badge_bg": (60, 15, 40),
    },
    "sin_envy": {
        "tag_id": "sin_envy",
        "display_name": "Envy",
        "category": "set_identity",
        "description": "The Mirror Stalker: Retributive reflection, phase dodging, and counter-attacks.",
        "color": (50, 210, 140),
        "badge_bg": (10, 50, 30),
    },
    "sin_gluttony": {
        "tag_id": "sin_gluttony",
        "display_name": "Gluttony",
        "category": "set_identity",
        "description": "The Abyssal Maw: Vampiric consumption, lifesteal sustain, and vital surge.",
        "color": (210, 45, 55),
        "badge_bg": (50, 10, 15),
    },
    "sin_wrath": {
        "tag_id": "sin_wrath",
        "display_name": "Wrath",
        "category": "set_identity",
        "description": "The Worldbreaker: Furious speed escalation, berserk fury under low health.",
        "color": (255, 55, 40),
        "badge_bg": (60, 10, 10),
    },
    "sin_sloth": {
        "tag_id": "sin_sloth",
        "display_name": "Sloth",
        "category": "set_identity",
        "description": "The Hollow Dream: Patient shielding, restful fortitude, and explosive awakening.",
        "color": (145, 140, 220),
        "badge_bg": (25, 25, 55),
    },

    # Seven Heavenly Virtues (Refined, luminous, celestial and radiant palettes)
    "virtue_humility": {
        "tag_id": "virtue_humility",
        "display_name": "Humility",
        "category": "set_identity",
        "description": "The Quiet Crown: Quiet balance, knockback immunity, and harmonic fortitude.",
        "color": (225, 230, 245),
        "badge_bg": (40, 45, 60),
    },
    "virtue_charity": {
        "tag_id": "virtue_charity",
        "display_name": "Charity",
        "category": "set_identity",
        "description": "The Hearthkeeper: Unconditional health restoration and communal party warmth.",
        "color": (255, 165, 80),
        "badge_bg": (55, 30, 10),
    },
    "virtue_chastity": {
        "tag_id": "virtue_chastity",
        "display_name": "Chastity",
        "category": "set_identity",
        "description": "The Pure Aegis: Absolute warding barrier and status debuff immunity.",
        "color": (245, 250, 255),
        "badge_bg": (45, 55, 75),
    },
    "virtue_gratitude": {
        "tag_id": "virtue_gratitude",
        "display_name": "Gratitude",
        "category": "set_identity",
        "description": "The Everbright: Resource conservation, MP refund, and radiant sunbursts.",
        "color": (255, 225, 85),
        "badge_bg": (60, 50, 10),
    },
    "virtue_temperance": {
        "tag_id": "virtue_temperance",
        "display_name": "Temperance",
        "category": "set_identity",
        "description": "The Stillwater: Flowing cooldown acceleration, water ripples, and agile tempo.",
        "color": (85, 205, 255),
        "badge_bg": (15, 45, 65),
    },
    "virtue_kindness": {
        "tag_id": "virtue_kindness",
        "display_name": "Kindness",
        "category": "set_identity",
        "description": "The Verdant Guardian: Earthly regeneration, thorns deflection, and second chance.",
        "color": (115, 230, 115),
        "badge_bg": (15, 50, 20),
    },
    "virtue_diligence": {
        "tag_id": "virtue_diligence",
        "display_name": "Diligence",
        "category": "set_identity",
        "description": "The Unyielding Vanguard: Unbroken sustained offensive momentum and smithing grit.",
        "color": (175, 200, 225),
        "badge_bg": (30, 40, 55),
    },

    # Philippine Heritage & Regional Folklore
    "pinoy_heritage": {
        "tag_id": "pinoy_heritage",
        "display_name": "Philippine Heritage",
        "category": "cultural_collection",
        "description": "Traditional Philippine martial blade forms: Kampilan, Panabas, Kris, Balisong, Bangkaw.",
        "color": (225, 185, 95),
        "badge_bg": (55, 40, 15),
    },
    "pinoy_folklore": {
        "tag_id": "pinoy_folklore",
        "display_name": "Philippine Folklore",
        "category": "cultural_collection",
        "description": "Mythical guardians, lunar serpents, forest diwatas, and indigenous avian motifs.",
        "color": (95, 215, 165),
        "badge_bg": (15, 50, 35),
    },
    "pinoy_amulet": {
        "tag_id": "pinoy_amulet",
        "display_name": "Agimat / Anting-Anting",
        "category": "cultural_collection",
        "description": "Revered talismanic amulets of spiritual protection, vitality, and resilience.",
        "color": (220, 165, 70),
        "badge_bg": (50, 35, 10),
    },

    # Combat Roles
    "combat_offensive": {
        "tag_id": "combat_offensive",
        "display_name": "Offense",
        "category": "combat_role",
        "description": "Primarily focused on physical or elemental attack power and critical strikes.",
        "color": (255, 110, 110),
        "badge_bg": (55, 20, 20),
    },
    "combat_defensive": {
        "tag_id": "combat_defensive",
        "display_name": "Defense",
        "category": "combat_role",
        "description": "Primarily focused on armor defense, max HP, and incoming damage reduction.",
        "color": (110, 180, 255),
        "badge_bg": (20, 35, 60),
    },
    "combat_sustain": {
        "tag_id": "combat_sustain",
        "display_name": "Sustain",
        "category": "combat_role",
        "description": "Provides steady HP regeneration, lifesteal on hit, or mana replenishment.",
        "color": (120, 235, 130),
        "badge_bg": (20, 50, 25),
    },
    "combat_mobility": {
        "tag_id": "combat_mobility",
        "display_name": "Mobility",
        "category": "combat_role",
        "description": "Enhances sprint speed, dash frequency, and evasive maneuverability.",
        "color": (245, 220, 100),
        "badge_bg": (50, 45, 15),
    },
}

def get_tag_info(tag_id: str) -> Optional[Dict[str, Any]]:
    """Returns metadata for a given stable tag ID."""
    return TAG_REGISTRY.get(tag_id)


# -----------------------------------------------------------------------------
# 2. STAT RANGES & RANDOMIZED BASE STAT GENERATION
# -----------------------------------------------------------------------------

# Configured min/max ranges for item definitions
ITEM_STAT_RANGES: Dict[str, Dict[str, Dict[str, Union[int, float]]]] = {
    # Filipino Weapons
    "kampilan": {
        "atk": {"min": 32, "max": 42},
        "crit": {"min": 6.0, "max": 10.0},
        "speed": {"min": 0.05, "max": 0.12},
    },
    "panabas": {
        "atk": {"min": 40, "max": 52},
        "def": {"min": 3, "max": 6},
    },
    "kris": {
        "atk": {"min": 24, "max": 32},
        "crit": {"min": 12.0, "max": 18.0},
        "speed": {"min": 0.10, "max": 0.20},
    },
    "balisong": {
        "atk": {"min": 19, "max": 27},
        "crit": {"min": 15.0, "max": 22.0},
        "speed": {"min": 0.15, "max": 0.25},
    },
    "bangkaw": {
        "atk": {"min": 28, "max": 38},
        "crit": {"min": 8.0, "max": 12.0},
    },

    # Filipino Folklore Sets
    "diwata_crown": {"def": {"min": 8, "max": 12}, "hp": {"min": 25, "max": 40}, "mp_regen": {"min": 0.8, "max": 1.4}},
    "diwata_gown": {"def": {"min": 14, "max": 20}, "hp": {"min": 45, "max": 65}, "mp_regen": {"min": 1.2, "max": 2.0}},
    "diwata_sandals": {"def": {"min": 6, "max": 10}, "hp": {"min": 20, "max": 35}, "speed": {"min": 0.20, "max": 0.35}},

    "bakunawa_helm": {"def": {"min": 15, "max": 22}, "hp": {"min": 40, "max": 60}, "crit": {"min": 4.0, "max": 8.0}},
    "bakunawa_plate": {"def": {"min": 24, "max": 34}, "hp": {"min": 65, "max": 95}, "atk": {"min": 8, "max": 14}},
    "bakunawa_greaves": {"def": {"min": 14, "max": 20}, "hp": {"min": 35, "max": 55}, "speed": {"min": 0.25, "max": 0.40}},

    "sarimanok_crest": {"def": {"min": 10, "max": 15}, "hp": {"min": 30, "max": 50}, "atk": {"min": 6, "max": 10}},
    "sarimanok_tunic": {"def": {"min": 16, "max": 24}, "hp": {"min": 50, "max": 75}, "atk": {"min": 8, "max": 14}},
    "sarimanok_striders": {"def": {"min": 9, "max": 14}, "hp": {"min": 25, "max": 40}, "speed": {"min": 0.30, "max": 0.50}},

    "tikbalang_mask": {"def": {"min": 8, "max": 12}, "hp": {"min": 20, "max": 35}, "speed": {"min": 0.20, "max": 0.35}},
    "tikbalang_vest": {"def": {"min": 12, "max": 18}, "hp": {"min": 35, "max": 55}, "speed": {"min": 0.25, "max": 0.40}},
    "tikbalang_hooves": {"def": {"min": 7, "max": 11}, "hp": {"min": 20, "max": 30}, "speed": {"min": 0.45, "max": 0.70}},

    # Filipino Accessories
    "agimat_iron_heart": {"def": {"min": 10, "max": 16}, "hp": {"min": 35, "max": 55}},
    "anting_anting_wanderer": {"def": {"min": 4, "max": 8}, "hp": {"min": 20, "max": 30}, "speed": {"min": 0.12, "max": 0.22}},
    "salakot_sunward": {"def": {"min": 5, "max": 9}, "hp": {"min": 20, "max": 35}, "atk": {"min": 4, "max": 8}},
    "pearl_of_deep": {"mp_regen": {"min": 1.5, "max": 2.5}, "crit": {"min": 4.0, "max": 8.0}, "hp": {"min": 20, "max": 35}},
    "pearl_of_the_deep": {"mp_regen": {"min": 1.5, "max": 2.5}, "crit": {"min": 4.0, "max": 8.0}, "hp": {"min": 20, "max": 35}},
    "bayanihan_charm": {"def": {"min": 6, "max": 11}, "hp": {"min": 25, "max": 45}, "atk": {"min": 5, "max": 9}},

    # Seven Deadly Sins Weapons & Sets
    "pride_blade": {"atk": {"min": 44, "max": 58}, "crit": {"min": 14.0, "max": 22.0}},
    "pride_crown": {"def": {"min": 18, "max": 26}, "hp": {"min": 50, "max": 75}, "crit": {"min": 8.0, "max": 12.0}},
    "pride_robe": {"def": {"min": 24, "max": 34}, "hp": {"min": 70, "max": 105}, "atk": {"min": 12, "max": 18}},
    "pride_boots": {"def": {"min": 15, "max": 22}, "hp": {"min": 45, "max": 65}, "speed": {"min": 0.30, "max": 0.45}},
    "pride_ring": {"atk": {"min": 10, "max": 16}, "crit": {"min": 6.0, "max": 10.0}},

    "greed_scepter": {"atk": {"min": 38, "max": 48}, "crit": {"min": 8.0, "max": 14.0}},
    "greed_mask": {"def": {"min": 14, "max": 20}, "hp": {"min": 40, "max": 60}},
    "greed_mantle": {"def": {"min": 20, "max": 28}, "hp": {"min": 60, "max": 90}, "atk": {"min": 8, "max": 14}},
    "greed_striders": {"def": {"min": 12, "max": 18}, "hp": {"min": 35, "max": 55}, "speed": {"min": 0.25, "max": 0.40}},
    "greed_amulet": {"def": {"min": 6, "max": 10}, "hp": {"min": 30, "max": 50}},

    "lust_rapier": {"atk": {"min": 32, "max": 44}, "crit": {"min": 12.0, "max": 18.0}, "speed": {"min": 0.15, "max": 0.25}},
    "lust_veil": {"def": {"min": 12, "max": 18}, "hp": {"min": 35, "max": 50}, "mp_regen": {"min": 1.0, "max": 1.8}},
    "lust_corslet": {"def": {"min": 18, "max": 26}, "hp": {"min": 55, "max": 80}, "atk": {"min": 7, "max": 13}},
    "lust_wraps": {"def": {"min": 11, "max": 16}, "hp": {"min": 30, "max": 45}, "speed": {"min": 0.25, "max": 0.40}},
    "lust_perfume": {"mp_regen": {"min": 1.2, "max": 2.2}, "crit": {"min": 5.0, "max": 9.0}},

    "envy_daggers": {"atk": {"min": 34, "max": 46}, "crit": {"min": 15.0, "max": 24.0}, "speed": {"min": 0.18, "max": 0.28}},
    "envy_cowl": {"def": {"min": 15, "max": 22}, "hp": {"min": 40, "max": 60}, "crit": {"min": 5.0, "max": 9.0}},
    "envy_shroud": {"def": {"min": 22, "max": 30}, "hp": {"min": 60, "max": 90}, "atk": {"min": 9, "max": 15}},
    "envy_treads": {"def": {"min": 13, "max": 19}, "hp": {"min": 35, "max": 55}, "speed": {"min": 0.35, "max": 0.55}},
    "envy_eye": {"crit": {"min": 8.0, "max": 14.0}, "atk": {"min": 8, "max": 14}},

    "gluttony_cleaver": {"atk": {"min": 42, "max": 56}, "hp": {"min": 25, "max": 45}},
    "gluttony_jaw": {"def": {"min": 16, "max": 24}, "hp": {"min": 55, "max": 80}},
    "gluttony_carapace": {"def": {"min": 26, "max": 36}, "hp": {"min": 80, "max": 120}},
    "gluttony_tassets": {"def": {"min": 16, "max": 22}, "hp": {"min": 50, "max": 75}},
    "gluttony_stomach": {"def": {"min": 8, "max": 14}, "hp": {"min": 45, "max": 75}},

    "wrath_greatsword": {"atk": {"min": 52, "max": 70}, "crit": {"min": 10.0, "max": 18.0}, "speed": {"min": 0.10, "max": 0.20}},
    "wrath_helm": {"def": {"min": 18, "max": 26}, "hp": {"min": 50, "max": 75}, "atk": {"min": 10, "max": 16}},
    "wrath_cuirass": {"def": {"min": 28, "max": 38}, "hp": {"min": 75, "max": 110}, "atk": {"min": 14, "max": 22}},
    "wrath_greaves": {"def": {"min": 16, "max": 24}, "hp": {"min": 45, "max": 70}, "speed": {"min": 0.30, "max": 0.45}},
    "wrath_brand": {"atk": {"min": 12, "max": 20}, "crit": {"min": 6.0, "max": 10.0}},

    "sloth_pillow": {"atk": {"min": 35, "max": 46}, "def": {"min": 8, "max": 14}},
    "sloth_nightcap": {"def": {"min": 18, "max": 26}, "hp": {"min": 50, "max": 75}, "mp_regen": {"min": 1.2, "max": 2.0}},
    "sloth_pajamas": {"def": {"min": 28, "max": 38}, "hp": {"min": 75, "max": 110}, "mp_regen": {"min": 1.5, "max": 2.5}},
    "sloth_slippers": {"def": {"min": 16, "max": 22}, "hp": {"min": 45, "max": 65}, "speed": {"min": 0.15, "max": 0.25}},
    "sloth_pendulum": {"def": {"min": 10, "max": 16}, "mp_regen": {"min": 1.5, "max": 2.5}},

    # Seven Heavenly Virtues Weapons & Sets
    "humility_staff": {"atk": {"min": 36, "max": 48}, "def": {"min": 8, "max": 14}, "mp_regen": {"min": 1.0, "max": 1.8}},
    "humility_circlet": {"def": {"min": 16, "max": 24}, "hp": {"min": 45, "max": 70}, "atk": {"min": 6, "max": 10}},
    "humility_vestment": {"def": {"min": 25, "max": 35}, "hp": {"min": 70, "max": 100}, "atk": {"min": 10, "max": 16}},
    "humility_sandals": {"def": {"min": 15, "max": 22}, "hp": {"min": 40, "max": 60}, "speed": {"min": 0.25, "max": 0.40}},
    "humility_pendant": {"def": {"min": 8, "max": 14}, "hp": {"min": 30, "max": 50}, "atk": {"min": 6, "max": 10}},

    "charity_wand": {"atk": {"min": 30, "max": 42}, "hp": {"min": 25, "max": 45}, "mp_regen": {"min": 1.2, "max": 2.0}},
    "charity_cowl": {"def": {"min": 14, "max": 20}, "hp": {"min": 50, "max": 75}},
    "charity_tunic": {"def": {"min": 22, "max": 30}, "hp": {"min": 75, "max": 115}},
    "charity_trousers": {"def": {"min": 13, "max": 19}, "hp": {"min": 45, "max": 65}, "speed": {"min": 0.20, "max": 0.35}},
    "charity_chalice": {"hp": {"min": 40, "max": 65}, "mp_regen": {"min": 1.5, "max": 2.5}},

    "chastity_lance": {"atk": {"min": 40, "max": 54}, "def": {"min": 10, "max": 16}},
    "chastity_sallet": {"def": {"min": 20, "max": 28}, "hp": {"min": 50, "max": 75}},
    "chastity_breastplate": {"def": {"min": 30, "max": 42}, "hp": {"min": 80, "max": 120}},
    "chastity_greaves": {"def": {"min": 18, "max": 26}, "hp": {"min": 45, "max": 70}, "speed": {"min": 0.25, "max": 0.38}},
    "chastity_aegis": {"def": {"min": 14, "max": 22}, "hp": {"min": 40, "max": 60}},

    "gratitude_scepter": {"atk": {"min": 38, "max": 50}, "mp_regen": {"min": 1.5, "max": 2.5}},
    "gratitude_crown": {"def": {"min": 16, "max": 24}, "hp": {"min": 45, "max": 65}, "mp_regen": {"min": 1.2, "max": 2.0}},
    "gratitude_chasuble": {"def": {"min": 24, "max": 34}, "hp": {"min": 65, "max": 95}, "mp_regen": {"min": 1.8, "max": 2.8}},
    "gratitude_striders": {"def": {"min": 14, "max": 20}, "hp": {"min": 40, "max": 60}, "speed": {"min": 0.25, "max": 0.40}},
    "gratitude_locket": {"mp_regen": {"min": 1.8, "max": 2.8}, "crit": {"min": 5.0, "max": 9.0}},

    "temperance_trident": {"atk": {"min": 36, "max": 48}, "crit": {"min": 10.0, "max": 16.0}, "speed": {"min": 0.10, "max": 0.20}},
    "temperance_circlet": {"def": {"min": 15, "max": 22}, "hp": {"min": 40, "max": 60}, "mp_regen": {"min": 1.0, "max": 1.8}},
    "temperance_robe": {"def": {"min": 22, "max": 32}, "hp": {"min": 60, "max": 90}, "speed": {"min": 0.15, "max": 0.25}},
    "temperance_leggings": {"def": {"min": 14, "max": 20}, "hp": {"min": 35, "max": 55}, "speed": {"min": 0.25, "max": 0.40}},
    "temperance_pearl": {"mp_regen": {"min": 1.5, "max": 2.5}, "speed": {"min": 0.10, "max": 0.20}},

    "kindness_bow": {"atk": {"min": 36, "max": 50}, "crit": {"min": 8.0, "max": 14.0}},
    "kindness_wreath": {"def": {"min": 14, "max": 20}, "hp": {"min": 45, "max": 70}},
    "kindness_cuirass": {"def": {"min": 24, "max": 34}, "hp": {"min": 70, "max": 105}},
    "kindness_striders": {"def": {"min": 14, "max": 20}, "hp": {"min": 40, "max": 65}, "speed": {"min": 0.25, "max": 0.40}},
    "kindness_seed": {"hp": {"min": 40, "max": 65}, "def": {"min": 6, "max": 12}},

    "diligence_warhammer": {"atk": {"min": 46, "max": 62}, "crit": {"min": 6.0, "max": 12.0}, "speed": {"min": 0.08, "max": 0.18}},
    "diligence_helm": {"def": {"min": 19, "max": 27}, "hp": {"min": 50, "max": 75}, "atk": {"min": 6, "max": 12}},
    "diligence_plate": {"def": {"min": 28, "max": 40}, "hp": {"min": 80, "max": 115}, "atk": {"min": 10, "max": 16}},
    "diligence_greaves": {"def": {"min": 17, "max": 25}, "hp": {"min": 45, "max": 70}, "speed": {"min": 0.25, "max": 0.38}},
    "diligence_anvil_charm": {"def": {"min": 10, "max": 16}, "atk": {"min": 8, "max": 14}},

    # Representative Existing Core Items
    "iron_broadsword": {"atk": {"min": 16, "max": 22}, "crit": {"min": 3.0, "max": 6.0}},
    "gold_broadsword": {"atk": {"min": 20, "max": 26}, "crit": {"min": 5.0, "max": 8.0}},
    "shadow_cleaver": {"atk": {"min": 25, "max": 32}, "crit": {"min": 6.0, "max": 10.0}},
    "magma_greatsword": {"atk": {"min": 34, "max": 44}, "crit": {"min": 8.0, "max": 13.0}},
    "frost_blade": {"atk": {"min": 16, "max": 22}, "def": {"min": 1, "max": 3}},
    "ancient_sword": {"atk": {"min": 38, "max": 48}, "crit": {"min": 10.0, "max": 15.0}},
}

def get_item_stat_ranges(item_id: str) -> Optional[Dict[str, Dict[str, Union[int, float]]]]:
    """Returns the predefined attribute min/max ranges for an item ID."""
    return ITEM_STAT_RANGES.get(item_id)

def roll_item_stat_ranges(item_id: str, rng_seed: Optional[int] = None) -> Optional[Dict[str, Union[int, float]]]:
    """
    Rolls randomized values strictly within the predefined attribute ranges of the item definition.
    Returns a dictionary of rolled stats, or None if the item has no defined ranges.
    """
    ranges = get_item_stat_ranges(item_id)
    if not ranges:
        return None
    rng = random.Random(rng_seed) if rng_seed is not None else random
    rolled: Dict[str, Union[int, float]] = {}
    for stat_name, spec in ranges.items():
        mn = spec.get("min", 0)
        mx = spec.get("max", mn)
        if isinstance(mn, float) or isinstance(mx, float):
            val = round(rng.uniform(float(mn), float(mx)), 2)
        else:
            val = rng.randint(int(mn), int(mx))
        rolled[stat_name] = val
    return rolled

def validate_stat_rolls(item_id: str, rolls: Dict[str, Union[int, float]]) -> bool:
    """Validates that all rolls are within configured min/max and only use declared attributes."""
    ranges = get_item_stat_ranges(item_id)
    if not ranges:
        return True
    for stat_name, val in rolls.items():
        if stat_name not in ranges:
            return False
        spec = ranges[stat_name]
        mn = spec["min"]
        mx = spec["max"]
        if not (mn <= val <= mx):
            return False
    return True


# -----------------------------------------------------------------------------
# 3. STRICT ADDITIONAL AFFIX SLOT LIMITS
# -----------------------------------------------------------------------------

MAX_ADDITIONAL_AFFIX_SLOTS: Dict[str, int] = {
    "common": 0,
    "uncommon": 0,
    "rare": 0,
    "epic": 1,
    "legendary": 1,
    "mythic": 2,
    "ancient": 2,
}

def get_max_additional_slots(rarity: str) -> int:
    """Returns the maximum additional affix slots permitted through the slot addition system."""
    return MAX_ADDITIONAL_AFFIX_SLOTS.get(str(rarity).lower(), 0)

def can_add_additional_affix_slot(item: Any) -> Tuple[bool, str]:
    """
    Strict validation rule for additional affix slots per equipmentUpdate spec:
    - Common, Uncommon, Rare: 0 additional slots
    - Epic: max 1 additional slot
    - Legendary: max 1 additional slot
    - Mythic: max 2 additional slots
    - Ancient: max 2 additional slots
    """
    if not item:
        return False, "No item selected."
    data = item.data if hasattr(item, "data") else {}
    rarity = str(data.get("rarity", "common")).lower()
    max_slots = get_max_additional_slots(rarity)
    if max_slots <= 0:
        return False, f"Items of {rarity.title()} rarity cannot receive additional affix slots."
    if getattr(item, "is_broken", False):
        return False, "Cannot carve affix slot into a broken item! Repair it first."

    cur_added = getattr(item, "additional_affix_slots", getattr(item, "affix_slots", 0))
    if cur_added >= max_slots:
        return False, f"This item has already reached its maximum limit of {max_slots} additional Affix Slot(s) for {rarity.title()} rarity!"

    stat_candidates = []
    removed = set(getattr(item, "removed_stats", []))
    for s in ("atk", "def", "crit", "speed", "hp", "mp", "damage"):
        if s not in removed and data.get(s, 0) > 0:
            stat_candidates.append(s)

    if not stat_candidates:
        return False, "This item has no remaining basic stats that can be converted into an Affix Slot."

    return True, "Ready to carve additional Affix Slot."

def add_additional_affix_slot(item: Any, inventory: Any = None, cost_copper: int = 5000, sound_manager: Any = None) -> Tuple[bool, str]:
    """Carves 1 additional affix slot up to the strict rarity-based ceiling."""
    can_add, reason = can_add_additional_affix_slot(item)
    if not can_add:
        return False, reason

    if inventory and cost_copper > 0:
        if hasattr(inventory, "total_coins_value") and inventory.total_coins_value() < cost_copper:
            return False, f"Carving an Affix Slot requires {cost_copper} Copper Coins."
        if hasattr(inventory, "remove_coins"):
            inventory.remove_coins(cost_copper)

    data = item.data if hasattr(item, "data") else {}
    removed = set(getattr(item, "removed_stats", []))
    stat_candidates = []
    for s in ("atk", "def", "crit", "speed", "hp", "mp", "damage"):
        if s not in removed and data.get(s, 0) > 0:
            stat_candidates.append(s)

    chosen_stat = random.choice(stat_candidates)
    old_val = data.get(chosen_stat, 0)

    if not hasattr(item, "removed_stats"):
        item.removed_stats = []
    item.removed_stats.append(chosen_stat)

    cur_added = getattr(item, "additional_affix_slots", 0) + 1
    item.additional_affix_slots = cur_added
    base_slots = getattr(item, "base_affix_slots", 0)
    item.affix_slots = base_slots + cur_added

    if not hasattr(item, "affixes"):
        item.affixes = []

    if sound_manager and hasattr(sound_manager, "play"):
        sound_manager.play("craft")

    item_name = data.get("name", getattr(item, "item_id", "Item"))
    stat_label = chosen_stat.upper()
    return True, f"Affix Slot Carved into {item_name}! Sacrificed {stat_label} (-{old_val}) for 1 Open Slot (Total: {item.affix_slots})."


# -----------------------------------------------------------------------------
# 4. PROGRESSIVE EQUIPMENT SET DEFINITIONS
# -----------------------------------------------------------------------------

PROGRESSIVE_SETS: Dict[str, Dict[str, Any]] = {
    # Existing core sets extended with 2-piece and full-set thresholds
    "ancient": {
        "set_id": "ancient",
        "name": "Ancient Resonating Set",
        "pieces": ["ancient_helmet", "ancient_chestplate", "ancient_greaves", "ancient_sword"],
        "thresholds": {
            2: {"desc": "2-Piece: Ancient Gleam (+15% ATK, +15% DEF, +20 HP)", "atk_mult": 0.15, "def_mult": 0.15, "bonus_hp": 20},
            3: {"desc": "Full Set: Ancient Cosmic Resonance (+35% ATK, +30% DEF, +50 HP, +20% Crit, Radiant Pulsing Aura)",
                "atk_mult": 0.35, "def_mult": 0.30, "bonus_hp": 50, "bonus_crit": 20.0, "aura": "ancient"}
        }
    },
    "titan": {
        "set_id": "titan",
        "name": "Celestial Titan Set",
        "pieces": ["titan_helmet", "titan_chestplate", "titan_greaves", "celestial_greatsword"],
        "thresholds": {
            2: {"desc": "2-Piece: Titan Bulwark (+12% DEF, +15 HP)", "def_mult": 0.12, "bonus_hp": 15},
            3: {"desc": "Full Set: Celestial Aegis (+25% DEF, +30 HP, +15% ATK, Celestial Ward Aura)",
                "atk_mult": 0.15, "def_mult": 0.25, "bonus_hp": 30, "bonus_crit": 5.0, "aura": "titan"}
        }
    },
    "magma": {
        "set_id": "magma",
        "name": "Magma Core Set",
        "pieces": ["magma_helmet", "magma_chestplate", "magma_greaves", "magma_greatsword"],
        "thresholds": {
            2: {"desc": "2-Piece: Magma Spark (+10% ATK, +5 Fire Thorns)", "atk_mult": 0.10, "bonus_crit": 4.0},
            3: {"desc": "Full Set: Molten Crucible (+20% ATK, +15 Fire Thorns, Magma Aura)",
                "atk_mult": 0.20, "def_mult": 0.10, "bonus_hp": 25, "bonus_crit": 8.0, "aura": "magma"}
        }
    },
    "cryo": {
        "set_id": "cryo",
        "name": "Cryo Carapace Set",
        "pieces": ["cryo_helmet", "cryo_chestplate", "cryo_greaves"],
        "thresholds": {
            2: {"desc": "2-Piece: Frost Plating (+10% DEF, +1.0 MP/s)", "def_mult": 0.10, "bonus_mp_regen": 1.0},
            3: {"desc": "Full Set: Glacial Bastion (+20% DEF, +2.5 MP/s Regen, Cryo Aura)",
                "atk_mult": 0.05, "def_mult": 0.20, "bonus_hp": 35, "bonus_crit": 5.0, "bonus_mp_regen": 2.5, "aura": "cryo"}
        }
    },
    "shadow": {
        "set_id": "shadow",
        "name": "Umbral Shadow Set",
        "pieces": ["shadow_helmet", "shadow_plate", "shadow_greaves", "shadow_cleaver"],
        "thresholds": {
            2: {"desc": "2-Piece: Shadow Veil (+10% Crit, +0.10 Speed)", "bonus_crit": 10.0, "bonus_speed": 0.10},
            3: {"desc": "Full Set: Shadow Phantom (+20% Crit, +20% ATK, +0.20 Speed, Void Aura)",
                "atk_mult": 0.20, "def_mult": 0.10, "bonus_hp": 20, "bonus_crit": 20.0, "bonus_speed": 0.20, "aura": "shadow"}
        }
    },
    "spud": {
        "set_id": "spud",
        "name": "Spud Sovereign Set",
        "pieces": ["potato_cap", "potato_tunic", "potato_pants"],
        "thresholds": {
            2: {"desc": "2-Piece: Potato Vitality (+15 Max HP, +2 HP/s)", "bonus_hp": 15},
            3: {"desc": "Full Set: Spud Lord (+30 Max HP, +5 HP/s Regen, Earth Sprout Aura)",
                "atk_mult": 0.10, "def_mult": 0.10, "bonus_hp": 30, "bonus_crit": 5.0, "aura": "spud"}
        }
    },
    "cactus": {
        "set_id": "cactus",
        "name": "Cactus Needle Set",
        "pieces": ["cactus_helmet", "cactus_chestplate", "cactus_greaves", "cactus_sword"],
        "thresholds": {
            2: {"desc": "2-Piece: Prickly Barbs (+5 Thorns, +5% ATK)", "atk_mult": 0.05},
            3: {"desc": "Full Set: Thorn Barbs (+15 Reflected Thorns, +10% ATK, Prickly Aura)",
                "atk_mult": 0.10, "def_mult": 0.10, "bonus_hp": 15, "bonus_crit": 4.0, "aura": "cactus"}
        }
    },

    # Seven Deadly Sins Sets
    "sin_pride": {
        "set_id": "sin_pride",
        "name": "Pride: Sovereign of the Sun",
        "pieces": ["pride_crown", "pride_robe", "pride_boots", "pride_blade", "pride_ring"],
        "thresholds": {
            2: {"desc": "2-Piece: Solar Precision (+15% Crit Chance, +10% ATK)", "atk_mult": 0.10, "bonus_crit": 15.0},
            3: {"desc": "Full Set: Solar Majesty (+30% ATK, +25% Crit, +35% Crit Damage against healthy targets, Solar Aura)",
                "atk_mult": 0.30, "bonus_crit": 25.0, "bonus_hp": 35, "aura": "solar"}
        }
    },
    "sin_greed": {
        "set_id": "sin_greed",
        "name": "Greed: The Gilded Devourer",
        "pieces": ["greed_mask", "greed_mantle", "greed_striders", "greed_scepter", "greed_amulet"],
        "thresholds": {
            2: {"desc": "2-Piece: Coin Scavenger (+20% Gold Drops, +0.10 Speed)", "bonus_speed": 0.10, "bonus_hp": 20},
            3: {"desc": "Full Set: Golden Hoard Escalation (+25% ATK, +20% DEF, +0.25 Speed on defeat, Gilded Shimmer Aura)",
                "atk_mult": 0.25, "def_mult": 0.20, "bonus_speed": 0.25, "aura": "gold"}
        }
    },
    "sin_lust": {
        "set_id": "sin_lust",
        "name": "Lust: The Enchanter",
        "pieces": ["lust_veil", "lust_corslet", "lust_wraps", "lust_rapier", "lust_perfume"],
        "thresholds": {
            2: {"desc": "2-Piece: Captivating Allure (+15% Status Duration, +2.0 MP/s)", "bonus_mp_regen": 2.0, "bonus_crit": 8.0},
            3: {"desc": "Full Set: Siren's Enchantment (+25% ATK, +30% Damage vs Debuffed, +3.5 MP/s, Pink Mist Aura)",
                "atk_mult": 0.25, "bonus_mp_regen": 3.5, "bonus_speed": 0.15, "aura": "charm"}
        }
    },
    "sin_envy": {
        "set_id": "sin_envy",
        "name": "Envy: The Mirror Stalker",
        "pieces": ["envy_cowl", "envy_shroud", "envy_treads", "envy_daggers", "envy_eye"],
        "thresholds": {
            2: {"desc": "2-Piece: Phantom Step (+15% Evasion, +12% ATK)", "atk_mult": 0.12, "bonus_speed": 0.15},
            3: {"desc": "Full Set: Mirror Retribution (Reflects 150% damage on dodge/hit, +25% ATK, Mirror Mirage Aura)",
                "atk_mult": 0.25, "bonus_crit": 15.0, "bonus_speed": 0.25, "aura": "mirror"}
        }
    },
    "sin_gluttony": {
        "set_id": "sin_gluttony",
        "name": "Gluttony: The Abyssal Maw",
        "pieces": ["gluttony_jaw", "gluttony_carapace", "gluttony_tassets", "gluttony_cleaver", "gluttony_stomach"],
        "thresholds": {
            2: {"desc": "2-Piece: Insatiable Hunger (+8% Lifesteal, +35 Max HP)", "bonus_hp": 35},
            3: {"desc": "Full Set: Abyssal Feast (+20% ATK, +60 Max HP, +5 HP leech per strike, Crimson Maw Aura)",
                "atk_mult": 0.20, "def_mult": 0.15, "bonus_hp": 60, "aura": "maw"}
        }
    },
    "sin_wrath": {
        "set_id": "sin_wrath",
        "name": "Wrath: The Worldbreaker",
        "pieces": ["wrath_helm", "wrath_cuirass", "wrath_greaves", "wrath_greatsword", "wrath_brand"],
        "thresholds": {
            2: {"desc": "2-Piece: Fury Unleashed (+20% Attack Speed, +15% ATK)", "atk_mult": 0.15, "bonus_atk_speed": 0.20},
            3: {"desc": "Full Set: Worldbreaker Berserk (+35% ATK, +30% Atk Speed, +30% ATK below 50% HP, Crimson Rage Aura)",
                "atk_mult": 0.35, "bonus_atk_speed": 0.30, "bonus_crit": 12.0, "aura": "rage"}
        }
    },
    "sin_sloth": {
        "set_id": "sin_sloth",
        "name": "Sloth: The Hollow Dream",
        "pieces": ["sloth_nightcap", "sloth_pajamas", "sloth_slippers", "sloth_pillow", "sloth_pendulum"],
        "thresholds": {
            2: {"desc": "2-Piece: Restful Slumber (+25% DEF, +3.0 MP/s)", "def_mult": 0.25, "bonus_mp_regen": 3.0},
            3: {"desc": "Full Set: Slumber Fortitude (50-HP Dream Shield every 5s undamaged, +80% burst attack, Dream Mist Aura)",
                "def_mult": 0.40, "bonus_hp": 50, "bonus_mp_regen": 4.5, "aura": "dream"}
        }
    },

    # Seven Heavenly Virtues Sets
    "virtue_humility": {
        "set_id": "virtue_humility",
        "name": "Humility: The Quiet Crown",
        "pieces": ["humility_circlet", "humility_vestment", "humility_sandals", "humility_staff", "humility_pendant"],
        "thresholds": {
            2: {"desc": "2-Piece: Serene Grounding (+15% DEF, +15% ATK, +25 Max HP)", "atk_mult": 0.15, "def_mult": 0.15, "bonus_hp": 25},
            3: {"desc": "Full Set: Quiet Harmony (+25% All Stats, Knockback Immunity, Serene Pearl Aura)",
                "atk_mult": 0.25, "def_mult": 0.25, "bonus_hp": 50, "bonus_crit": 10.0, "aura": "pearl"}
        }
    },
    "virtue_charity": {
        "set_id": "virtue_charity",
        "name": "Charity: The Hearthkeeper",
        "pieces": ["charity_cowl", "charity_tunic", "charity_trousers", "charity_wand", "charity_chalice"],
        "thresholds": {
            2: {"desc": "2-Piece: Hearth Warmth (+4 HP/s Health Regen, +30 Max HP)", "bonus_hp": 30},
            3: {"desc": "Full Set: Communal Hearth (+6 HP/s Regen, +20% Party Damage Mitigation, Warm Hearth Gold Aura)",
                "def_mult": 0.20, "bonus_hp": 60, "bonus_mp_regen": 2.0, "aura": "hearth"}
        }
    },
    "virtue_chastity": {
        "set_id": "virtue_chastity",
        "name": "Chastity: The Pure Aegis",
        "pieces": ["chastity_sallet", "chastity_breastplate", "chastity_greaves", "chastity_lance", "chastity_aegis"],
        "thresholds": {
            2: {"desc": "2-Piece: Spotless Ward (+25% DEF, 50% Debuff Resistance)", "def_mult": 0.25, "bonus_hp": 25},
            3: {"desc": "Full Set: Unblemished Ward (Absorbs 60 damage every 10s, Debuff Immunity, Brilliant White Aura)",
                "def_mult": 0.40, "bonus_hp": 60, "aura": "sanctum"}
        }
    },
    "virtue_gratitude": {
        "set_id": "virtue_gratitude",
        "name": "Gratitude: The Everbright",
        "pieces": ["gratitude_crown", "gratitude_chasuble", "gratitude_striders", "gratitude_scepter", "gratitude_locket"],
        "thresholds": {
            2: {"desc": "2-Piece: Joyful Abundance (-25% MP Skill Cost, +2.5 MP/s)", "bonus_mp_regen": 2.5},
            3: {"desc": "Full Set: Radiance of Thanks (30% MP Refund Chance, +50 True Solar Flash, Golden Sunburst Aura)",
                "atk_mult": 0.20, "bonus_mp_regen": 4.0, "bonus_crit": 15.0, "aura": "sunburst"}
        }
    },
    "virtue_temperance": {
        "set_id": "virtue_temperance",
        "name": "Temperance: The Stillwater",
        "pieces": ["temperance_circlet", "temperance_robe", "temperance_leggings", "temperance_trident", "temperance_pearl"],
        "thresholds": {
            2: {"desc": "2-Piece: Tidal Pacing (+20% Cooldown Reduction, +15% Atk Speed)", "bonus_atk_speed": 0.15},
            3: {"desc": "Full Set: Tranquil Flow (Crits/Dodges refund 1s Cooldown & 15 MP, Azure Water Ripple Aura)",
                "atk_mult": 0.15, "bonus_atk_speed": 0.25, "bonus_speed": 0.20, "bonus_mp_regen": 3.0, "aura": "tidal"}
        }
    },
    "virtue_kindness": {
        "set_id": "virtue_kindness",
        "name": "Kindness: The Verdant Guardian",
        "pieces": ["kindness_wreath", "kindness_cuirass", "kindness_striders", "kindness_bow", "kindness_seed"],
        "thresholds": {
            2: {"desc": "2-Piece: Gentle Bloom (+3 HP/s Regen, +20 Max HP, +10 Reflected Thorns)", "bonus_hp": 20},
            3: {"desc": "Full Set: Verdant Blessing (Defies fatal blow once per 90s restoring 40% HP, Emerald Sprout Aura)",
                "def_mult": 0.20, "bonus_hp": 50, "bonus_mp_regen": 2.0, "aura": "verdant"}
        }
    },
    "virtue_diligence": {
        "set_id": "virtue_diligence",
        "name": "Diligence: The Unyielding Vanguard",
        "pieces": ["diligence_helm", "diligence_plate", "diligence_greaves", "diligence_warhammer", "diligence_anvil_charm"],
        "thresholds": {
            2: {"desc": "2-Piece: Tireless Rhythm (+15% ATK, +15% DEF, +10% Atk Speed)", "atk_mult": 0.15, "def_mult": 0.15, "bonus_atk_speed": 0.10},
            3: {"desc": "Full Set: Unyielding Vanguard (+30% ATK, +25% DEF, +25% Atk Speed in sustained combat, Steel Spark Aura)",
                "atk_mult": 0.30, "def_mult": 0.25, "bonus_atk_speed": 0.25, "bonus_hp": 40, "aura": "steel"}
        }
    },

    # Filipino Folklore Sets
    "diwata_bloom": {
        "set_id": "diwata_bloom",
        "name": "Diwata's Bloom Regalia",
        "pieces": ["diwata_crown", "diwata_gown", "diwata_sandals"],
        "thresholds": {
            2: {"desc": "2-Piece: Makiling Petals (+4 HP/s Regen, +2.0 MP/s, +15% Nature Damage)", "bonus_mp_regen": 2.0},
            3: {"desc": "Full Set: Bloom of Makiling (+25% Healing, Petal Bursts dealing 30 nature damage, Floral Blossom Aura)",
                "atk_mult": 0.15, "def_mult": 0.15, "bonus_hp": 45, "bonus_mp_regen": 3.0, "aura": "blossom"}
        }
    },
    "bakunawa_eclipse": {
        "set_id": "bakunawa_eclipse",
        "name": "Bakunawa's Eclipse Armor",
        "pieces": ["bakunawa_helm", "bakunawa_plate", "bakunawa_greaves"],
        "thresholds": {
            2: {"desc": "2-Piece: Lunar Veil (+20% Crit Damage, +15% Elemental ATK)", "atk_mult": 0.15, "bonus_crit": 8.0},
            3: {"desc": "Full Set: Seven Moons Eclipse (+30% ATK, Lunar Wave dealing 45 area cosmic damage, Midnight Lunar Aura)",
                "atk_mult": 0.30, "def_mult": 0.20, "bonus_hp": 50, "bonus_crit": 15.0, "aura": "eclipse"}
        }
    },
    "sarimanok_regalia": {
        "set_id": "sarimanok_regalia",
        "name": "Sarimanok Royal Regalia",
        "pieces": ["sarimanok_crest", "sarimanok_tunic", "sarimanok_striders"],
        "thresholds": {
            2: {"desc": "2-Piece: Radiant Prosperity (+15% All Stats, +25% Coin Drops)", "atk_mult": 0.15, "def_mult": 0.15, "bonus_hp": 25},
            3: {"desc": "Full Set: Prismatic Flight (+25% All Stats, +0.30 Speed, Prismatic Feathers True Damage, Radiant Feathers Aura)",
                "atk_mult": 0.25, "def_mult": 0.25, "bonus_hp": 50, "bonus_speed": 0.30, "aura": "prismatic"}
        }
    },
    "tikbalang_trailblazer": {
        "set_id": "tikbalang_trailblazer",
        "name": "Tikbalang Trailblazer Set",
        "pieces": ["tikbalang_mask", "tikbalang_vest", "tikbalang_hooves"],
        "thresholds": {
            2: {"desc": "2-Piece: Trickster Stride (+30% Sprint Speed, +15% Evasion)", "bonus_speed": 0.30},
            3: {"desc": "Full Set: Path of Inversion (+55% Sprint Speed, Dashing inverts enemy tracking paths, Forest Illusion Aura)",
                "atk_mult": 0.15, "bonus_speed": 0.55, "bonus_crit": 10.0, "aura": "trickster"}
        }
    },
}

def get_equipped_set_counts(equipped_ids: List[str]) -> Dict[str, int]:
    """Returns mapping of set_id -> number of matching pieces equipped."""
    counts: Dict[str, int] = {}
    eq_set = set(str(i).lower() for i in equipped_ids if i)
    for set_id, s_data in PROGRESSIVE_SETS.items():
        match_cnt = 0
        for p in s_data.get("pieces", []):
            if p.lower() in eq_set:
                match_cnt += 1
        if match_cnt > 0:
            counts[set_id] = match_cnt
    return counts

def get_active_threshold_bonuses(equipped_ids: List[str]) -> List[Tuple[str, int, Dict[str, Any]]]:
    """
    Returns list of tuples (set_id, threshold, bonus_dict) for all active progressive thresholds.
    Ensures non-stacking within same threshold tier and no duplicate application.
    """
    active_bonuses: List[Tuple[str, int, Dict[str, Any]]] = []
    counts = get_equipped_set_counts(equipped_ids)
    for set_id, count in counts.items():
        s_data = PROGRESSIVE_SETS.get(set_id, {})
        thresholds = s_data.get("thresholds", {})
        # Find highest qualifying threshold
        qualifying = [t for t in thresholds.keys() if count >= t]
        if qualifying:
            highest_tier = max(qualifying)
            active_bonuses.append((set_id, highest_tier, thresholds[highest_tier]))
    return active_bonuses


# -----------------------------------------------------------------------------
# 5. NEW EQUIPMENT CATALOG ENTRIES
# -----------------------------------------------------------------------------

NEW_EQUIPMENT_DATA: Dict[str, Dict[str, Any]] = {
    # ---------------- Filipino Weapons ----------------
    "kampilan": {
        "slot": "weapon",
        "name": "Kampilan — Warrior's Oath",
        "atk": 36, "def": 2, "hp": 20, "crit": 8.0, "speed": 0.08,
        "rarity": "legendary",
        "effects": ["Finishing Cleave (+30% True Damage against foes below 35% HP)", "Staggering Blow"],
        "lore": "Revered long blade of coastal warriors, shaped with a bifurcated tip that carved through history.",
        "desc": "A traditional heavy two-handed sword with immense forward cleaving reach and armor execution.",
        "tags": ["pinoy_heritage", "combat_offensive"],
        "stat_ranges": ITEM_STAT_RANGES["kampilan"],
    },
    "panabas": {
        "slot": "weapon",
        "name": "Panabas — Breaker of Wards",
        "atk": 46, "def": 4, "hp": 25, "crit": 4.0, "speed": 0.0,
        "rarity": "epic",
        "effects": ["Armor Shatter (Ignores 45% target DEF)", "Stun Impact on heavy swing"],
        "lore": "Forward-curved executioner blade forged to dismantle barricades, shields, and dragon scales.",
        "desc": "A forward-curved chopping weapon capable of crushing heavily fortified enemy defense lines.",
        "tags": ["pinoy_heritage", "combat_offensive"],
        "stat_ranges": ITEM_STAT_RANGES["panabas"],
    },
    "kris": {
        "slot": "weapon",
        "name": "Kris — Serpent of the Archipelago",
        "atk": 28, "def": 0, "hp": 10, "crit": 15.0, "speed": 0.16,
        "rarity": "legendary",
        "effects": ["Serpentine Wave Striking", "25% Chance to inflict Naga Venom over 4s"],
        "lore": "Wavy double-edged blade holding the sacred spiritual power of archipelago master bladesmiths.",
        "desc": "An undulating, asymmetrical serpentine dagger with deadly swift precision and venomous edge.",
        "tags": ["pinoy_heritage", "combat_offensive"],
        "stat_ranges": ITEM_STAT_RANGES["kris"],
    },
    "balisong": {
        "slot": "weapon",
        "name": "Balisong — Twin-Edge Trickster",
        "atk": 22, "def": 0, "hp": 0, "crit": 18.0, "speed": 0.20,
        "rarity": "rare",
        "effects": ["Trickster Flick: +100% Critical Strike Chance after sprint dash", "+15% Sprint Speed"],
        "lore": "Hand-forged pocket folding blade born from Batangas workshops, famed across the oceans.",
        "desc": "Deceptively quick folding knife that empowers high-mobility guerrilla tactics and instant ambushes.",
        "tags": ["pinoy_heritage", "combat_mobility"],
        "stat_ranges": ITEM_STAT_RANGES["balisong"],
    },
    "bangkaw": {
        "slot": "weapon",
        "name": "Bangkaw — Spear of the Highlands",
        "atk": 32, "def": 1, "hp": 15, "crit": 10.0, "speed": 0.05,
        "rarity": "uncommon",
        "effects": ["Highland Thrust: Piercing reach extends 24px further than standard blades"],
        "lore": "Carved hardwood spear tipped with tempered steel, carried by mountain tribal hunters.",
        "desc": "A long-reaching hunting spear providing secure spacing against agile wild beasts and monsters.",
        "tags": ["pinoy_heritage", "combat_offensive"],
        "stat_ranges": ITEM_STAT_RANGES["bangkaw"],
    },

    # ---------------- Filipino Folklore Sets ----------------
    "diwata_crown": {
        "slot": "head", "name": "Diwata's Woven Tiara",
        "def": 10, "hp": 30, "atk": 4, "crit": 4.0, "mp_regen": 1.0,
        "rarity": "epic", "effects": ["Forest Whisper (+1.0 MP/s)"], "desc": "Woven from blooming orchids and sacred vines.",
        "tags": ["pinoy_folklore", "combat_sustain"], "stat_ranges": ITEM_STAT_RANGES["diwata_crown"],
    },
    "diwata_gown": {
        "slot": "chest", "name": "Diwata's Blossom Raiment",
        "def": 17, "hp": 55, "atk": 6, "crit": 3.0, "mp_regen": 1.5,
        "rarity": "epic", "effects": ["Bloom Ward (+1.5 MP/s, +2 HP/s)"], "desc": "Silken gown spun by benevolent mountain spirits.",
        "tags": ["pinoy_folklore", "combat_sustain"], "stat_ranges": ITEM_STAT_RANGES["diwata_gown"],
    },
    "diwata_sandals": {
        "slot": "legs", "name": "Diwata's Earth Sandals",
        "def": 8, "hp": 25, "atk": 2, "crit": 2.0, "speed": 0.28,
        "rarity": "epic", "effects": ["Root Tread (+28% Move Speed)"], "desc": "Light sandals that glide over forest undergrowth.",
        "tags": ["pinoy_folklore", "combat_mobility"], "stat_ranges": ITEM_STAT_RANGES["diwata_sandals"],
    },

    "bakunawa_helm": {
        "slot": "head", "name": "Bakunawa's Horned Mask",
        "def": 18, "hp": 50, "atk": 8, "crit": 6.0, "speed": 0.0,
        "rarity": "legendary", "effects": ["Eclipse Eye (+6% Crit, Cosmic Darkvision)"], "desc": "Forged in the shape of the gigantic sea dragon.",
        "tags": ["pinoy_folklore", "combat_offensive"], "stat_ranges": ITEM_STAT_RANGES["bakunawa_helm"],
    },
    "bakunawa_plate": {
        "slot": "chest", "name": "Bakunawa's Scale Cuirass",
        "def": 28, "hp": 80, "atk": 11, "crit": 4.0, "speed": 0.0,
        "rarity": "legendary", "effects": ["Serpentine Carapace (+28 DEF, Cosmic Resistance)"], "desc": "Indigo dragon scales that swallowed the celestial moons.",
        "tags": ["pinoy_folklore", "combat_defensive"], "stat_ranges": ITEM_STAT_RANGES["bakunawa_plate"],
    },
    "bakunawa_greaves": {
        "slot": "legs", "name": "Bakunawa's Tide Greaves",
        "def": 17, "hp": 45, "atk": 5, "crit": 4.0, "speed": 0.32,
        "rarity": "legendary", "effects": ["Tidal Surge (+32% Move Speed)"], "desc": "Greaves imbued with abyssal ocean currents.",
        "tags": ["pinoy_folklore", "combat_mobility"], "stat_ranges": ITEM_STAT_RANGES["bakunawa_greaves"],
    },

    "sarimanok_crest": {
        "slot": "head", "name": "Sarimanok Feathered Diadem",
        "def": 12, "hp": 40, "atk": 8, "crit": 5.0, "speed": 0.10,
        "rarity": "legendary", "effects": ["Radiant Plume (+20% Coin Find)"], "desc": "Adorned with iridescent feathers of the mythical bird of prosperity.",
        "tags": ["pinoy_folklore", "combat_offensive"], "stat_ranges": ITEM_STAT_RANGES["sarimanok_crest"],
    },
    "sarimanok_tunic": {
        "slot": "chest", "name": "Sarimanok Embroidered Robe",
        "def": 20, "hp": 65, "atk": 11, "crit": 4.0, "speed": 0.10,
        "rarity": "legendary", "effects": ["Aura of Abundance (+20 DEF, +11 ATK)"], "desc": "Woven with intricate okir patterns celebrating good fortune.",
        "tags": ["pinoy_folklore", "combat_offensive"], "stat_ranges": ITEM_STAT_RANGES["sarimanok_tunic"],
    },
    "sarimanok_striders": {
        "slot": "legs", "name": "Sarimanok Dawn Boots",
        "def": 12, "hp": 32, "atk": 4, "crit": 3.0, "speed": 0.40,
        "rarity": "legendary", "effects": ["Wind Glide (+40% Move Speed)"], "desc": "Boots that leave faint glowing rainbow motes in the player's wake.",
        "tags": ["pinoy_folklore", "combat_mobility"], "stat_ranges": ITEM_STAT_RANGES["sarimanok_striders"],
    },

    "tikbalang_mask": {
        "slot": "head", "name": "Tikbalang Equine Cowl",
        "def": 10, "hp": 28, "atk": 3, "crit": 4.0, "speed": 0.28,
        "rarity": "epic", "effects": ["Trickster Mirage (+28% Speed)"], "desc": "Mask carved with the likeness of the forest half-horse trickster.",
        "tags": ["pinoy_folklore", "combat_mobility"], "stat_ranges": ITEM_STAT_RANGES["tikbalang_mask"],
    },
    "tikbalang_vest": {
        "slot": "chest", "name": "Tikbalang Forest Harness",
        "def": 15, "hp": 45, "atk": 4, "crit": 2.0, "speed": 0.32,
        "rarity": "epic", "effects": ["Labyrinth Stride (+32% Speed)"], "desc": "Light leather harness crafted for leaping through dense canopy.",
        "tags": ["pinoy_folklore", "combat_mobility"], "stat_ranges": ITEM_STAT_RANGES["tikbalang_vest"],
    },
    "tikbalang_hooves": {
        "slot": "legs", "name": "Tikbalang Gallop Striders",
        "def": 9, "hp": 25, "atk": 2, "crit": 2.0, "speed": 0.58,
        "rarity": "epic", "effects": ["Wild Gallop (+58% Sprint Speed)"], "desc": "Hoof-plated boots built for runaway sprints across uncharted wilderness.",
        "tags": ["pinoy_folklore", "combat_mobility"], "stat_ranges": ITEM_STAT_RANGES["tikbalang_hooves"],
    },

    # ---------------- Filipino Accessories ----------------
    "agimat_iron_heart": {
        "slot": "accessory", "name": "Agimat of the Iron Heart",
        "def": 14, "hp": 45, "atk": 0, "crit": 0.0, "speed": 0.0,
        "rarity": "epic",
        "effects": ["Iron Heart Bulwark: Reduces incoming physical damage by -15%"],
        "desc": "A heavy bronze medallion blessed by anting-anting traditions to shield the wearer from harm.",
        "tags": ["pinoy_heritage", "pinoy_amulet", "combat_defensive"],
        "stat_ranges": ITEM_STAT_RANGES["agimat_iron_heart"],
    },
    "anting_anting_wanderer": {
        "slot": "accessory", "name": "Anting-Anting of the Wanderer",
        "def": 6, "hp": 25, "atk": 0, "crit": 0.0, "speed": 0.16,
        "rarity": "rare",
        "effects": ["Wayfarer's Grace: Immune to slow debuffs, +16% Movement Speed"],
        "desc": "A brass charm containing secret Latin-Tagalog inscriptions meant to protect traveling explorers.",
        "tags": ["pinoy_heritage", "pinoy_amulet", "combat_mobility"],
        "stat_ranges": ITEM_STAT_RANGES["anting_anting_wanderer"],
    },
    "salakot_sunward": {
        "slot": "accessory", "name": "Salakot of the Sunward Traveler",
        "def": 7, "hp": 28, "atk": 6, "crit": 3.0, "speed": 0.08,
        "rarity": "uncommon",
        "effects": ["Sun Shield: +10% Attack bonus during bright daylight hours"],
        "desc": "Wide-brimmed traditional reed hat reinforced with woven bronze fibers against desert heat.",
        "tags": ["pinoy_heritage", "pinoy_amulet", "combat_offensive"],
        "stat_ranges": ITEM_STAT_RANGES["salakot_sunward"],
    },
    "pearl_of_deep": {
        "slot": "accessory", "name": "Pearl of the Deep",
        "def": 4, "hp": 28, "atk": 0, "crit": 6.0, "mp_regen": 2.0,
        "rarity": "legendary",
        "effects": ["South Sea Pearl Radiance: Infinite aquatic oxygen and +20% Water mobility"],
        "desc": "A lustrous golden pearl harvested from deep Sulu sea trenches, humming with tidal energy.",
        "tags": ["pinoy_heritage", "pinoy_amulet", "combat_sustain"],
        "stat_ranges": ITEM_STAT_RANGES["pearl_of_deep"],
    },
    "pearl_of_the_deep": {
        "slot": "accessory", "name": "Pearl of the Deep",
        "def": 4, "hp": 28, "atk": 0, "crit": 6.0, "mp_regen": 2.0,
        "rarity": "legendary",
        "effects": ["South Sea Pearl Radiance: Infinite aquatic oxygen and +20% Water mobility"],
        "desc": "A lustrous golden pearl harvested from deep Sulu sea trenches, humming with tidal energy.",
        "tags": ["pinoy_heritage", "pinoy_amulet", "combat_sustain"],
        "stat_ranges": ITEM_STAT_RANGES["pearl_of_the_deep"],
    },
    "bayanihan_charm": {
        "slot": "accessory", "name": "Bayanihan Charm",
        "def": 8, "hp": 35, "atk": 7, "crit": 4.0, "speed": 0.05,
        "rarity": "rare",
        "effects": ["Spirit of Community: Grants +15% All Stats when near NPCs or LAN party members"],
        "desc": "A carved wooden icon embodying communal unity and cooperative strength.",
        "tags": ["pinoy_heritage", "pinoy_amulet", "combat_sustain"],
        "stat_ranges": ITEM_STAT_RANGES["bayanihan_charm"],
    },

    # ---------------- Seven Deadly Sins: Pride ----------------
    "pride_blade": {
        "slot": "weapon", "name": "Sol Invictus — Blade of Pride",
        "atk": 52, "def": 2, "hp": 25, "crit": 18.0, "speed": 0.12,
        "rarity": "mythic",
        "effects": ["Sovereign Execution (+40% Damage vs enemies above 80% HP)", "Solar Beam on critical hit"],
        "lore": "A golden claymore so radiant it burns the eyes of all who dare look upon its edge.",
        "desc": "Sun-forged Greatsword demanding absolute precision and delivering punishing critical bursts.",
        "tags": ["sin_pride", "combat_offensive"],
        "stat_ranges": ITEM_STAT_RANGES["pride_blade"],
    },
    "pride_crown": {
        "slot": "head", "name": "Crown of the Solar Sovereign",
        "def": 22, "hp": 65, "atk": 8, "crit": 10.0, "speed": 0.05,
        "rarity": "mythic", "effects": ["Solar Glare (+10% Crit Chance)"], "desc": "Radiant solar crown adorned with burning sunburst spikes.",
        "tags": ["sin_pride", "combat_offensive"], "stat_ranges": ITEM_STAT_RANGES["pride_crown"],
    },
    "pride_robe": {
        "slot": "chest", "name": "Raiment of the Unbowed",
        "def": 28, "hp": 90, "atk": 15, "crit": 6.0, "speed": 0.0,
        "rarity": "mythic", "effects": ["Unbowed Pride (+28 DEF, +15 ATK)"], "desc": "Regal mantle of pure woven gold that refuses to bend before any strike.",
        "tags": ["sin_pride", "combat_offensive"], "stat_ranges": ITEM_STAT_RANGES["pride_robe"],
    },
    "pride_boots": {
        "slot": "legs", "name": "Greaves of the Sunward Monarch",
        "def": 18, "hp": 55, "atk": 6, "crit": 4.0, "speed": 0.38,
        "rarity": "mythic", "effects": ["Sunward March (+38% Move Speed)"], "desc": "Burnished gold boots leaving golden sunprints in every step.",
        "tags": ["sin_pride", "combat_mobility"], "stat_ranges": ITEM_STAT_RANGES["pride_boots"],
    },
    "pride_ring": {
        "slot": "accessory", "name": "Signet of Solar Dominion",
        "def": 4, "hp": 30, "atk": 14, "crit": 8.0, "speed": 0.0,
        "rarity": "legendary", "effects": ["Dominion Spark (+14 ATK, +8% Crit)"], "desc": "Heavy seal of pride sealing the absolute authority of the sun.",
        "tags": ["sin_pride", "combat_offensive"], "stat_ranges": ITEM_STAT_RANGES["pride_ring"],
    },

    # ---------------- Seven Deadly Sins: Greed ----------------
    "greed_scepter": {
        "slot": "weapon", "name": "Gilded Scepter of Avarice",
        "atk": 42, "def": 0, "hp": 20, "crit": 10.0, "speed": 0.05,
        "rarity": "mythic",
        "effects": ["Golden Bribe: Defeated enemies grant +35% bonus gold", "Coin Burst on Critical Hit"],
        "lore": "An opulent gold-encrusted staff that turns slain foes into scattered fortunes.",
        "desc": "A heavy golden scepter commanding boundless wealth and critical riches.",
        "tags": ["sin_greed", "combat_offensive"],
        "stat_ranges": ITEM_STAT_RANGES["greed_scepter"],
    },
    "greed_mask": {
        "slot": "head", "name": "Mask of the Gilded Devourer",
        "def": 17, "hp": 50, "atk": 0, "crit": 0.0, "speed": 0.0,
        "rarity": "mythic", "effects": ["Greedy Visage (+20% Gold Drops, +50 HP)"], "desc": "A face-covering mask sculpted from solid bullion with emerald eyes.",
        "tags": ["sin_greed", "combat_defensive"], "stat_ranges": ITEM_STAT_RANGES["greed_mask"],
    },
    "greed_mantle": {
        "slot": "chest", "name": "Mantle of Endless Avarice",
        "def": 24, "hp": 75, "atk": 11, "crit": 0.0, "speed": 0.0,
        "rarity": "mythic", "effects": ["Gilded Carapace (+24 DEF, +75 HP, +11 ATK)"], "desc": "Heavy velvet robes sewn with stolen doubloons and gemstones.",
        "tags": ["sin_greed", "combat_offensive"], "stat_ranges": ITEM_STAT_RANGES["greed_mantle"],
    },
    "greed_striders": {
        "slot": "legs", "name": "Striders of the Coin Hoarder",
        "def": 15, "hp": 45, "atk": 0, "crit": 0.0, "speed": 0.32,
        "rarity": "mythic", "effects": ["Treasure Rush (+32% Move Speed, +15% Sprint Speed)"], "desc": "Silk boots with diamond-encrusted soles that sprint toward shiny valuables.",
        "tags": ["sin_greed", "combat_mobility"], "stat_ranges": ITEM_STAT_RANGES["greed_striders"],
    },
    "greed_amulet": {
        "slot": "accessory", "name": "Amulet of the Midas Touch",
        "def": 8, "hp": 40, "atk": 0, "crit": 0.0, "speed": 0.0,
        "rarity": "legendary", "effects": ["Midas Touch: Converts 5% of physical damage dealt into copper coins"], "desc": "A golden medallion carved with a ravenous gaping mouth.",
        "tags": ["sin_greed", "combat_defensive"], "stat_ranges": ITEM_STAT_RANGES["greed_amulet"],
    },

    # ---------------- Seven Deadly Sins: Lust ----------------
    "lust_rapier": {
        "slot": "weapon", "name": "Siren's Needle — Rapier of Lust",
        "atk": 38, "def": 0, "hp": 10, "crit": 15.0, "speed": 0.20,
        "rarity": "mythic",
        "effects": ["Charming Flurry (+25% Damage vs charmed/debuffed targets)", "Beguiling Thrust"],
        "lore": "A needle-thin rapier vibrating with hypnotic rose-tinted enchantment.",
        "desc": "A lightning-fast fencing foil inflicting bewitching puncture wounds.",
        "tags": ["sin_lust", "combat_offensive"],
        "stat_ranges": ITEM_STAT_RANGES["lust_rapier"],
    },
    "lust_veil": {
        "slot": "head", "name": "Veil of the Enchanter",
        "def": 15, "hp": 42, "atk": 0, "crit": 0.0, "mp_regen": 1.4,
        "rarity": "mythic", "effects": ["Hypnotic Gaze (+1.4 MP/s, +15% Debuff Duration)"], "desc": "Translucent gossamer veil that distracts enemy aim.",
        "tags": ["sin_lust", "combat_sustain"], "stat_ranges": ITEM_STAT_RANGES["lust_veil"],
    },
    "lust_corslet": {
        "slot": "chest", "name": "Corslet of Captivating Allure",
        "def": 22, "hp": 68, "atk": 10, "crit": 0.0, "speed": 0.0,
        "rarity": "mythic", "effects": ["Alluring Guard (+22 DEF, +68 HP, +10 ATK)"], "desc": "Fitted corset of reinforced enchanted silk that turns blows aside with alluring grace.",
        "tags": ["sin_lust", "combat_offensive"], "stat_ranges": ITEM_STAT_RANGES["lust_corslet"],
    },
    "lust_wraps": {
        "slot": "legs", "name": "Silken Wraps of the Temptress",
        "def": 13, "hp": 38, "atk": 0, "crit": 0.0, "speed": 0.32,
        "rarity": "mythic", "effects": ["Sinuous Dance (+32% Move Speed, +10% Dodge)"], "desc": "Ribbon wraps that swirl rhythmically with each step.",
        "tags": ["sin_lust", "combat_mobility"], "stat_ranges": ITEM_STAT_RANGES["lust_wraps"],
    },
    "lust_perfume": {
        "slot": "accessory", "name": "Phial of Beguiling Essence",
        "def": 0, "hp": 20, "atk": 0, "crit": 7.0, "mp_regen": 1.7,
        "rarity": "legendary", "effects": ["Beguiling Mist: Enemies striking you have a 20% chance to be confused for 3s"], "desc": "An ornate crystal flacon radiating an intoxicating floral aroma.",
        "tags": ["sin_lust", "combat_sustain"], "stat_ranges": ITEM_STAT_RANGES["lust_perfume"],
    },

    # ---------------- Seven Deadly Sins: Envy ----------------
    "envy_daggers": {
        "slot": "weapon", "name": "Twin Shards of Envy",
        "atk": 40, "def": 0, "hp": 10, "crit": 19.0, "speed": 0.23,
        "rarity": "mythic",
        "effects": ["Mirror Stalker: Retaliates with 120% counter-damage upon perfect dodge", "Deep Hemorrhage"],
        "lore": "Dual daggers crafted from mirrored glass that thirst for whatever others possess.",
        "desc": "Crystalline twin blades executing lethal counters and mirror-image strikes.",
        "tags": ["sin_envy", "combat_offensive"],
        "stat_ranges": ITEM_STAT_RANGES["envy_daggers"],
    },
    "envy_cowl": {
        "slot": "head", "name": "Cowl of the Jealous Stalker",
        "def": 18, "hp": 50, "atk": 0, "crit": 7.0, "speed": 0.0,
        "rarity": "mythic", "effects": ["Covetous Eye (+7% Crit, +18 DEF)"], "desc": "A shadowy cowl that obscures facial features and hones peripheral tracking.",
        "tags": ["sin_envy", "combat_offensive"], "stat_ranges": ITEM_STAT_RANGES["envy_cowl"],
    },
    "envy_shroud": {
        "slot": "chest", "name": "Shroud of the Green Mirage",
        "def": 26, "hp": 75, "atk": 12, "crit": 0.0, "speed": 0.0,
        "rarity": "mythic", "effects": ["Mirage Shroud (+26 DEF, +75 HP, +12 ATK)"], "desc": "Shifting emerald fabric that mirrors background surroundings for rapid ambush.",
        "tags": ["sin_envy", "combat_offensive"], "stat_ranges": ITEM_STAT_RANGES["envy_shroud"],
    },
    "envy_treads": {
        "slot": "legs", "name": "Treads of the Unseen Shadow",
        "def": 16, "hp": 45, "atk": 0, "crit": 0.0, "speed": 0.45,
        "rarity": "mythic", "effects": ["Phase Step (+45% Move Speed, Silent Steps)"], "desc": "Supple leather boots that emit no vibration or sound across terrain.",
        "tags": ["sin_envy", "combat_mobility"], "stat_ranges": ITEM_STAT_RANGES["envy_treads"],
    },
    "envy_eye": {
        "slot": "accessory", "name": "The Emerald Eye of Resentment",
        "def": 0, "hp": 20, "atk": 11, "crit": 11.0, "speed": 0.0,
        "rarity": "legendary", "effects": ["Vengeful Spite: +15% Damage against enemies possessing higher HP than you"], "desc": "A preserved jade eye that pulses whenever foes boast greater power.",
        "tags": ["sin_envy", "combat_offensive"], "stat_ranges": ITEM_STAT_RANGES["envy_eye"],
    },

    # ---------------- Seven Deadly Sins: Gluttony ----------------
    "gluttony_cleaver": {
        "slot": "weapon", "name": "Meat Carver of the Abyssal Maw",
        "atk": 48, "def": 0, "hp": 35, "crit": 5.0, "speed": 0.0,
        "rarity": "mythic",
        "effects": ["Abyssal Feast: +8% Lifesteal on all melee strikes", "Gouge Wound"],
        "lore": "A monstrous cleaver heavy enough to split megalodon bone in a single swing.",
        "desc": "A massive serrated cleaver that drinks crimson lifeblood to sustain its wielder.",
        "tags": ["sin_gluttony", "combat_sustain"],
        "stat_ranges": ITEM_STAT_RANGES["gluttony_cleaver"],
    },
    "gluttony_jaw": {
        "slot": "head", "name": "Visage of the Devouring Jaw",
        "def": 20, "hp": 68, "atk": 0, "crit": 0.0, "speed": 0.0,
        "rarity": "mythic", "effects": ["Maw Armor (+20 DEF, +68 HP)"], "desc": "A monstrous bone helm modeled after unhinged abyssal predator jaws.",
        "tags": ["sin_gluttony", "combat_defensive"], "stat_ranges": ITEM_STAT_RANGES["gluttony_jaw"],
    },
    "gluttony_carapace": {
        "slot": "chest", "name": "Carapace of the Bloated Swarm",
        "def": 31, "hp": 100, "atk": 0, "crit": 0.0, "speed": 0.0,
        "rarity": "mythic", "effects": ["Insatiable Bulwark (+31 DEF, +100 HP, +5 HP/s Regen)"], "desc": "Heavy chitin plate forged from creatures that never stop feeding.",
        "tags": ["sin_gluttony", "combat_defensive"], "stat_ranges": ITEM_STAT_RANGES["gluttony_carapace"],
    },
    "gluttony_tassets": {
        "slot": "legs", "name": "Tassets of the Endless Feast",
        "def": 19, "hp": 62, "atk": 0, "crit": 0.0, "speed": 0.20,
        "rarity": "mythic", "effects": ["Gorging Walk (+19 DEF, +62 HP, +20% Move Speed)"], "desc": "Chitin-plated leg guards with spikes designed to pin thrashing prey.",
        "tags": ["sin_gluttony", "combat_defensive"], "stat_ranges": ITEM_STAT_RANGES["gluttony_tassets"],
    },
    "gluttony_stomach": {
        "slot": "accessory", "name": "Vessel of the Iron Gizzard",
        "def": 11, "hp": 60, "atk": 0, "crit": 0.0, "speed": 0.0,
        "rarity": "legendary", "effects": ["Digestion Fortitude: Food and potions grant 50% extra healing and double duration"], "desc": "An obsidian reliquary preserving the digestive organ of a leviathan.",
        "tags": ["sin_gluttony", "combat_sustain"], "stat_ranges": ITEM_STAT_RANGES["gluttony_stomach"],
    },

    # ---------------- Seven Deadly Sins: Sloth ----------------
    "sloth_pillow": {
        "slot": "weapon", "name": "The Comatose Cudgel",
        "atk": 40, "def": 11, "hp": 20, "crit": 0.0, "speed": -0.05,
        "rarity": "mythic",
        "effects": ["Heavy Snooze: Attacks have 25% chance to inflict Drowsy (50% slow)", "Awakening Crash"],
        "lore": "A dense enchanted pillow stone that lulls both victim and wielder into twilight dreams.",
        "desc": "A deceptively hefty sleeping cudgel delivering crushing, deliberate strikes.",
        "tags": ["sin_sloth", "combat_defensive"],
        "stat_ranges": ITEM_STAT_RANGES["sloth_pillow"],
    },
    "sloth_nightcap": {
        "slot": "head", "name": "Nightcap of the Deep Slumberer",
        "def": 22, "hp": 62, "atk": 0, "crit": 0.0, "mp_regen": 1.6,
        "rarity": "mythic", "effects": ["Restful Slumber (+22 DEF, +62 HP, +1.6 MP/s)"], "desc": "A soft velvet cap embroidered with dreaming stars that calms racing thoughts.",
        "tags": ["sin_sloth", "combat_sustain"], "stat_ranges": ITEM_STAT_RANGES["sloth_nightcap"],
    },
    "sloth_pajamas": {
        "slot": "chest", "name": "Vestment of the Dream Realm",
        "def": 33, "hp": 92, "atk": 0, "crit": 0.0, "mp_regen": 2.0,
        "rarity": "mythic", "effects": ["Dream Sanctuary (+33 DEF, +92 HP, +2.0 MP/s)"], "desc": "Padded loungewear spun from dream silk that cushions even direct dragon impacts.",
        "tags": ["sin_sloth", "combat_defensive"], "stat_ranges": ITEM_STAT_RANGES["sloth_pajamas"],
    },
    "sloth_slippers": {
        "slot": "legs", "name": "Slippers of Peaceful Languor",
        "def": 19, "hp": 55, "atk": 0, "crit": 0.0, "speed": 0.20,
        "rarity": "mythic", "effects": ["Carefree Glide (+19 DEF, +55 HP, +20% Move Speed)"], "desc": "Fluffy slippers that cushion every step with cloud-like silence.",
        "tags": ["sin_sloth", "combat_defensive"], "stat_ranges": ITEM_STAT_RANGES["sloth_slippers"],
    },
    "sloth_pendulum": {
        "slot": "accessory", "name": "Hypnotic Pendulum of Stasis",
        "def": 13, "hp": 30, "atk": 0, "crit": 0.0, "mp_regen": 2.0,
        "rarity": "legendary", "effects": ["Stasis Aura: When standing still for 3s, gain 40% damage reduction barrier"], "desc": "A swinging silver bob that slows down the passage of violent seconds.",
        "tags": ["sin_sloth", "combat_defensive"], "stat_ranges": ITEM_STAT_RANGES["sloth_pendulum"],
    },

    # ---------------- Seven Deadly Sins: Wrath ----------------
    "wrath_greatsword": {
        "slot": "weapon", "name": "The Worldbreaker",
        "atk": 62, "def": 0, "hp": 20, "crit": 14.0, "speed": 0.15,
        "rarity": "mythic",
        "effects": ["Furious Cascade: Consecutive strikes escalate attack speed by +10% per hit (max 5)", "Molten Wave"],
        "lore": "Forged in the fury of a dying planet whose core shattered under unbearable pressure.",
        "desc": "A colossal jagged slab of heated metal that accelerates in speed as blood boils in battle.",
        "tags": ["sin_wrath", "combat_offensive"],
        "stat_ranges": ITEM_STAT_RANGES["wrath_greatsword"],
    },
    "wrath_helm": {
        "slot": "head", "name": "Helm of the Red Worldbreaker",
        "def": 22, "hp": 60, "atk": 14, "crit": 6.0, "speed": 0.05,
        "rarity": "mythic", "effects": ["Bloodrage Gaze (+14 ATK)"], "desc": "Horned visor wreathed in smoldering crimson embers.",
        "tags": ["sin_wrath", "combat_offensive"], "stat_ranges": ITEM_STAT_RANGES["wrath_helm"],
    },
    "wrath_cuirass": {
        "slot": "chest", "name": "Cuirass of Unchecked Rage",
        "def": 32, "hp": 95, "atk": 18, "crit": 6.0, "speed": 0.05,
        "rarity": "mythic", "effects": ["Boiling Blood (+18 ATK, +32 DEF)"], "desc": "Heavy jagged steel cuirass pulsing with violent volcanic energy.",
        "tags": ["sin_wrath", "combat_offensive"], "stat_ranges": ITEM_STAT_RANGES["wrath_cuirass"],
    },
    "wrath_greaves": {
        "slot": "legs", "name": "Greaves of the Cataclysm",
        "def": 20, "hp": 55, "atk": 8, "crit": 4.0, "speed": 0.38,
        "rarity": "mythic", "effects": ["Crushing Charge (+38% Move Speed)"], "desc": "Thick spiked greaves designed to trample battlefields.",
        "tags": ["sin_wrath", "combat_mobility"], "stat_ranges": ITEM_STAT_RANGES["wrath_greaves"],
    },
    "wrath_brand": {
        "slot": "accessory", "name": "Brand of Unbroken Fury",
        "def": 4, "hp": 25, "atk": 16, "crit": 8.0, "speed": 0.08,
        "rarity": "legendary", "effects": ["Furious Momentum (+16 ATK, +8% Crit)"], "desc": "Red-hot iron brand fueling continuous assault.",
        "tags": ["sin_wrath", "combat_offensive"], "stat_ranges": ITEM_STAT_RANGES["wrath_brand"],
    },

    # ---------------- Seven Heavenly Virtues: Humility ----------------
    "humility_staff": {
        "slot": "weapon", "name": "Staff of the Quiet Crown",
        "atk": 42, "def": 11, "hp": 20, "crit": 4.0, "mp_regen": 1.4,
        "rarity": "legendary",
        "effects": ["Serene Strike: Harmonizes attack and defense; strikes heal for 5% damage dealt", "Purifying Pulse"],
        "lore": "Carved from plain ashwood by a monk king who laid down his gold crown.",
        "desc": "A simple wooden staff carrying deep spiritual fortitude and balanced power.",
        "tags": ["virtue_humility", "combat_sustain"],
        "stat_ranges": ITEM_STAT_RANGES["humility_staff"],
    },
    "humility_circlet": {
        "slot": "head", "name": "Circlet of the Quiet Crown",
        "def": 20, "hp": 58, "atk": 8, "crit": 2.0, "speed": 0.0,
        "rarity": "legendary", "effects": ["Quiet Mind (+20 DEF, +58 HP, +8 ATK)"], "desc": "An unpolished silver band resting gently upon the forehead without pride.",
        "tags": ["virtue_humility", "combat_defensive"], "stat_ranges": ITEM_STAT_RANGES["humility_circlet"],
    },
    "humility_vestment": {
        "slot": "chest", "name": "Vestment of Quiet Balance",
        "def": 30, "hp": 85, "atk": 13, "crit": 2.0, "speed": 0.0,
        "rarity": "legendary", "effects": ["Harmonic Fortitude (+30 DEF, +85 HP, +13 ATK)"], "desc": "Unadorned gray robes woven with hidden tempered mithril thread.",
        "tags": ["virtue_humility", "combat_defensive"], "stat_ranges": ITEM_STAT_RANGES["humility_vestment"],
    },
    "humility_sandals": {
        "slot": "legs", "name": "Sandals of the Lowly Path",
        "def": 18, "hp": 50, "atk": 0, "crit": 0.0, "speed": 0.32,
        "rarity": "legendary", "effects": ["Grounded Tread (+18 DEF, +50 HP, +32% Move Speed)"], "desc": "Braided cord sandals engineered for traversing rugged mountain paths patiently.",
        "tags": ["virtue_humility", "combat_mobility"], "stat_ranges": ITEM_STAT_RANGES["humility_sandals"],
    },
    "humility_pendant": {
        "slot": "accessory", "name": "Pendant of Peaceful Equanimity",
        "def": 11, "hp": 40, "atk": 8, "crit": 0.0, "speed": 0.0,
        "rarity": "rare", "effects": ["Equanimity: Immunity to knockback and stagger effects"], "desc": "A small river pebble smoothed by ten thousand years of rushing water.",
        "tags": ["virtue_humility", "combat_defensive"], "stat_ranges": ITEM_STAT_RANGES["humility_pendant"],
    },

    # ---------------- Seven Heavenly Virtues: Charity ----------------
    "charity_wand": {
        "slot": "weapon", "name": "Censer of the Hearthkeeper",
        "atk": 36, "def": 4, "hp": 35, "crit": 6.0, "speed": 0.0,
        "rarity": "legendary",
        "effects": ["Healing Censer: Attacks create soothing incense restoring +4 HP to nearby allies", "Warm Flame"],
        "lore": "A bronze censer carrying coals that have never grown cold since the first winter.",
        "desc": "A blessed focus that comforts the wounded while smiting wicked invaders with gentle fire.",
        "tags": ["virtue_charity", "combat_sustain"],
        "stat_ranges": ITEM_STAT_RANGES["charity_wand"],
    },
    "charity_cowl": {
        "slot": "head", "name": "Hearthkeeper Warm Cowl",
        "def": 16, "hp": 65, "atk": 3, "crit": 2.0, "mp_regen": 1.2,
        "rarity": "legendary", "effects": ["Gentle Warmth (+65 HP)"], "desc": "Comforting woolen hood woven to keep freezing wanderers safe.",
        "tags": ["virtue_charity", "combat_sustain"], "stat_ranges": ITEM_STAT_RANGES["charity_cowl"],
    },
    "charity_tunic": {
        "slot": "chest", "name": "Hearthkeeper Woolen Tunic",
        "def": 26, "hp": 95, "atk": 5, "crit": 2.0, "mp_regen": 1.5,
        "rarity": "legendary", "effects": ["Hearth Sanctuary (+95 HP, +26 DEF)"], "desc": "Heavy lined tunic radiating calm soothing warmth.",
        "tags": ["virtue_charity", "combat_sustain"], "stat_ranges": ITEM_STAT_RANGES["charity_tunic"],
    },
    "charity_trousers": {
        "slot": "legs", "name": "Hearthkeeper Travel Trousers",
        "def": 16, "hp": 55, "atk": 2, "crit": 2.0, "speed": 0.28,
        "rarity": "legendary", "effects": ["Steady Mercy (+28% Move Speed)"], "desc": "Durable warm trousers built for tireless humanitarian relief journeys.",
        "tags": ["virtue_charity", "combat_mobility"], "stat_ranges": ITEM_STAT_RANGES["charity_trousers"],
    },
    "charity_chalice": {
        "slot": "accessory", "name": "Everflowing Chalice of Mercy",
        "def": 6, "hp": 55, "atk": 0, "crit": 0.0, "mp_regen": 2.2,
        "rarity": "legendary", "effects": ["Spring of Life (+2 HP/s, +2.2 MP/s)"], "desc": "Chalice overflowing with pure springwater that never runs dry.",
        "tags": ["virtue_charity", "combat_sustain"], "stat_ranges": ITEM_STAT_RANGES["charity_chalice"],
    },

    # ---------------- Seven Heavenly Virtues: Chastity ----------------
    "chastity_lance": {
        "slot": "weapon", "name": "Lance of the Spotless Ward",
        "atk": 47, "def": 13, "hp": 25, "crit": 6.0, "speed": 0.05,
        "rarity": "legendary",
        "effects": ["Purifying Thrust: Piercing strikes dispel enemy buffs and cleanse 1 debuff from wielder", "Shield Wall"],
        "lore": "A gleaming alabaster jousting lance blessed by order paladins.",
        "desc": "A heavy tournament lance combining defensive bulwark with piercing purity.",
        "tags": ["virtue_chastity", "combat_defensive"],
        "stat_ranges": ITEM_STAT_RANGES["chastity_lance"],
    },
    "chastity_sallet": {
        "slot": "head", "name": "Sallet of the Pure Aegis",
        "def": 24, "hp": 62, "atk": 0, "crit": 0.0, "speed": 0.0,
        "rarity": "legendary", "effects": ["Spotless Vision (+24 DEF, +62 HP, 50% Debuff Resistance)"], "desc": "A polished silver sallet with a tight protective bellows visor.",
        "tags": ["virtue_chastity", "combat_defensive"], "stat_ranges": ITEM_STAT_RANGES["chastity_sallet"],
    },
    "chastity_breastplate": {
        "slot": "chest", "name": "Breastplate of Unblemished Silver",
        "def": 36, "hp": 100, "atk": 0, "crit": 0.0, "speed": 0.0,
        "rarity": "legendary", "effects": ["Pure Aegis Sanctuary (+36 DEF, +100 HP, Status Immunity)"], "desc": "Flawless white-steel cuirass reflecting corruption and dark spells.",
        "tags": ["virtue_chastity", "combat_defensive"], "stat_ranges": ITEM_STAT_RANGES["chastity_breastplate"],
    },
    "chastity_greaves": {
        "slot": "legs", "name": "Greaves of the Spotless Knight",
        "def": 22, "hp": 58, "atk": 0, "crit": 0.0, "speed": 0.32,
        "rarity": "legendary", "effects": ["Iron Stride (+22 DEF, +58 HP, +32% Move Speed)"], "desc": "Articulated plate greaves that guard against ground hazards and caltrops.",
        "tags": ["virtue_chastity", "combat_defensive"], "stat_ranges": ITEM_STAT_RANGES["chastity_greaves"],
    },
    "chastity_aegis": {
        "slot": "accessory", "name": "Relic of the Untarnished Mirror",
        "def": 18, "hp": 50, "atk": 0, "crit": 0.0, "speed": 0.0,
        "rarity": "legendary", "effects": ["Ward of Purity: Blocks up to 60 incoming damage every 12 seconds"], "desc": "A miniature heater shield badge forged from pure starlight silver.",
        "tags": ["virtue_chastity", "combat_defensive"], "stat_ranges": ITEM_STAT_RANGES["chastity_aegis"],
    },

    # ---------------- Seven Heavenly Virtues: Gratitude ----------------
    "gratitude_scepter": {
        "slot": "weapon", "name": "Scepter of the Everbright",
        "atk": 44, "def": 0, "hp": 20, "crit": 8.0, "mp_regen": 2.0,
        "rarity": "legendary",
        "effects": ["Bounteous Dawn: Skill casts have a 30% chance to cost 0 MP and trigger a radiant light burst", "Solar Flare"],
        "lore": "Crowned with a prism that converts humble thanks into brilliant sunlight.",
        "desc": "A radiant gold scepter providing continuous mana recovery and spell bursts.",
        "tags": ["virtue_gratitude", "combat_sustain"],
        "stat_ranges": ITEM_STAT_RANGES["gratitude_scepter"],
    },
    "gratitude_crown": {
        "slot": "head", "name": "Crown of the Everbright Dawn",
        "def": 20, "hp": 55, "atk": 0, "crit": 4.0, "mp_regen": 1.6,
        "rarity": "legendary", "effects": ["Radiant Thanks (+20 DEF, +55 HP, +1.6 MP/s)"], "desc": "A golden corona that radiates gentle sunrise warmth.",
        "tags": ["virtue_gratitude", "combat_sustain"], "stat_ranges": ITEM_STAT_RANGES["gratitude_crown"],
    },
    "gratitude_chasuble": {
        "slot": "chest", "name": "Chasuble of the Golden Harvest",
        "def": 29, "hp": 80, "atk": 0, "crit": 0.0, "mp_regen": 2.3,
        "rarity": "legendary", "effects": ["Harvest Blessing (+29 DEF, +80 HP, +2.3 MP/s)"], "desc": "Embroidered ceremonial vestment woven from golden wheat silk.",
        "tags": ["virtue_gratitude", "combat_sustain"], "stat_ranges": ITEM_STAT_RANGES["gratitude_chasuble"],
    },
    "gratitude_striders": {
        "slot": "legs", "name": "Striders of Joyful Steps",
        "def": 17, "hp": 50, "atk": 0, "crit": 0.0, "speed": 0.32,
        "rarity": "legendary", "effects": ["Joyful March (+17 DEF, +50 HP, +32% Move Speed)"], "desc": "Comfortable leather travel boots that lighten fatigue over long journeys.",
        "tags": ["virtue_gratitude", "combat_mobility"], "stat_ranges": ITEM_STAT_RANGES["gratitude_striders"],
    },
    "gratitude_locket": {
        "slot": "accessory", "name": "Locket of the Grateful Heart",
        "def": 0, "hp": 30, "atk": 0, "crit": 7.0, "mp_regen": 2.3,
        "rarity": "legendary", "effects": ["Everbright Remembrance: +25% Resource efficiency across all skills"], "desc": "A heart-shaped gold locket keeping memories of kindness received.",
        "tags": ["virtue_gratitude", "combat_sustain"], "stat_ranges": ITEM_STAT_RANGES["gratitude_locket"],
    },

    # ---------------- Seven Heavenly Virtues: Temperance ----------------
    "temperance_trident": {
        "slot": "weapon", "name": "Trident of the Stillwater",
        "atk": 42, "def": 4, "hp": 20, "crit": 13.0, "speed": 0.15,
        "rarity": "legendary",
        "effects": ["Tidal Cadence: Landing critical hits reduces all active skill cooldowns by 1.5s", "Wave Thrust"],
        "lore": "Forged in crystalline glacial depths to calm boiling maelstroms.",
        "desc": "A balanced triple-prong trident maintaining steady rhythm and fluid tempo.",
        "tags": ["virtue_temperance", "combat_offensive"],
        "stat_ranges": ITEM_STAT_RANGES["temperance_trident"],
    },
    "temperance_circlet": {
        "slot": "head", "name": "Circlet of the Calm Depths",
        "def": 18, "hp": 50, "atk": 0, "crit": 0.0, "mp_regen": 1.4,
        "rarity": "legendary", "effects": ["Tranquil Focus (+18 DEF, +50 HP, +1.4 MP/s)"], "desc": "An aquamarine coronet that keeps the mind clear and focused amid chaos.",
        "tags": ["virtue_temperance", "combat_sustain"], "stat_ranges": ITEM_STAT_RANGES["temperance_circlet"],
    },
    "temperance_robe": {
        "slot": "chest", "name": "Robe of the Rippleless Pool",
        "def": 27, "hp": 75, "atk": 0, "crit": 0.0, "speed": 0.20,
        "rarity": "legendary", "effects": ["Flowing Stillness (+27 DEF, +75 HP, +20% Move Speed)"], "desc": "Deep azure silk robes flowing like calm mountain brook water.",
        "tags": ["virtue_temperance", "combat_mobility"], "stat_ranges": ITEM_STAT_RANGES["temperance_robe"],
    },
    "temperance_leggings": {
        "slot": "legs", "name": "Leggings of the Tidal Cadence",
        "def": 17, "hp": 45, "atk": 0, "crit": 0.0, "speed": 0.32,
        "rarity": "legendary", "effects": ["Tidal Stride (+17 DEF, +45 HP, +32% Move Speed)"], "desc": "Form-fitting aquatic leggings enabling frictionless movement through water and air.",
        "tags": ["virtue_temperance", "combat_mobility"], "stat_ranges": ITEM_STAT_RANGES["temperance_leggings"],
    },
    "temperance_pearl": {
        "slot": "accessory", "name": "Tear of the Still Lake",
        "def": 4, "hp": 25, "atk": 0, "crit": 0.0, "mp_regen": 2.0, "speed": 0.15,
        "rarity": "legendary", "effects": ["Stillwater Flow: Decreases skill cooldowns by 15% and increases move speed by +15%"], "desc": "A serene blue pearl that ripples softly when danger approaches.",
        "tags": ["virtue_temperance", "combat_sustain"], "stat_ranges": ITEM_STAT_RANGES["temperance_pearl"],
    },

    # ---------------- Seven Heavenly Virtues: Kindness ----------------
    "kindness_bow": {
        "slot": "weapon", "name": "Bow of the Verdant Guardian",
        "atk": 43, "def": 2, "hp": 20, "crit": 11.0, "speed": 0.10,
        "rarity": "legendary",
        "effects": ["Verdant Salve: Arrows sprout healing flora restoring 10 HP to allies and wielder upon hit", "Briar Shot"],
        "lore": "Bent from living elder wood that never snapped, strung with woven forest dew vines.",
        "desc": "A living longbow that protects allies while piercing enemies with thorned briars.",
        "tags": ["virtue_kindness", "combat_sustain"],
        "stat_ranges": ITEM_STAT_RANGES["kindness_bow"],
    },
    "kindness_wreath": {
        "slot": "head", "name": "Wreath of the Forest Healer",
        "def": 17, "hp": 58, "atk": 0, "crit": 0.0, "speed": 0.0,
        "rarity": "legendary", "effects": ["Gentle Sprout (+17 DEF, +58 HP, +3 HP/s Regen)"], "desc": "A braided laurel wreath blooming with fragrant jasmine and clover.",
        "tags": ["virtue_kindness", "combat_sustain"], "stat_ranges": ITEM_STAT_RANGES["kindness_wreath"],
    },
    "kindness_cuirass": {
        "slot": "chest", "name": "Cuirass of the Gentle Thorn",
        "def": 29, "hp": 88, "atk": 0, "crit": 0.0, "speed": 0.0,
        "rarity": "legendary", "effects": ["Verdant Heart (+29 DEF, +88 HP, +15 Reflected Thorns)"], "desc": "Armored cuirass reinforced with petrified ironwood bark that returns damage to assailants.",
        "tags": ["virtue_kindness", "combat_defensive"], "stat_ranges": ITEM_STAT_RANGES["kindness_cuirass"],
    },
    "kindness_striders": {
        "slot": "legs", "name": "Striders of the Gentle Ranger",
        "def": 17, "hp": 52, "atk": 0, "crit": 0.0, "speed": 0.32,
        "rarity": "legendary", "effects": ["Forest Mercy (+17 DEF, +52 HP, +32% Move Speed)"], "desc": "Supple deer-hide boots leaving sprouting clover beneath each footprint.",
        "tags": ["virtue_kindness", "combat_mobility"], "stat_ranges": ITEM_STAT_RANGES["kindness_striders"],
    },
    "kindness_seed": {
        "slot": "accessory", "name": "Evergreen Seed of Renewal",
        "def": 9, "hp": 52, "atk": 0, "crit": 0.0, "speed": 0.0,
        "rarity": "legendary", "effects": ["Seed of Life: Defies a fatal blow once every 90 seconds, instantly healing 40% Max HP"], "desc": "A glowing seed of the world tree holding infinite capacity to restore life.",
        "tags": ["virtue_kindness", "combat_sustain"], "stat_ranges": ITEM_STAT_RANGES["kindness_seed"],
    },

    # ---------------- Seven Heavenly Virtues: Diligence ----------------
    "diligence_warhammer": {
        "slot": "weapon", "name": "Unyielding Forge Hammer",
        "atk": 54, "def": 6, "hp": 30, "crit": 8.0, "speed": 0.12,
        "rarity": "legendary",
        "effects": ["Smith's Rhythm: Each attack landed increases attack speed by +5% (max +35%)", "Armor Denting"],
        "lore": "The very hammer that struck three hundred thousand ingots without resting for a single day.",
        "desc": "A formidable warhammer rewarding consistent rhythm with relentless escalating tempo.",
        "tags": ["virtue_diligence", "combat_offensive"],
        "stat_ranges": ITEM_STAT_RANGES["diligence_warhammer"],
    },
    "diligence_helm": {
        "slot": "head", "name": "Vanguard Greathelm of Labor",
        "def": 24, "hp": 65, "atk": 8, "crit": 3.0, "speed": 0.05,
        "rarity": "legendary", "effects": ["Steadfast Focus (+24 DEF, +8 ATK)"], "desc": "Solid steel helm built to withstand cave-ins and siege weapons alike.",
        "tags": ["virtue_diligence", "combat_defensive"], "stat_ranges": ITEM_STAT_RANGES["diligence_helm"],
    },
    "diligence_plate": {
        "slot": "chest", "name": "Plate of the Unwearied Smith",
        "def": 34, "hp": 95, "atk": 12, "crit": 3.0, "speed": 0.0,
        "rarity": "legendary", "effects": ["Tireless Heart (+34 DEF, +95 HP)"], "desc": "Reinforced anvil-forged chestplate built for unwavering duty.",
        "tags": ["virtue_diligence", "combat_defensive"], "stat_ranges": ITEM_STAT_RANGES["diligence_plate"],
    },
    "diligence_greaves": {
        "slot": "legs", "name": "Greaves of the Iron March",
        "def": 21, "hp": 55, "atk": 5, "crit": 2.0, "speed": 0.32,
        "rarity": "legendary", "effects": ["Marching Cadence (+32% Move Speed)"], "desc": "Steel boots engineered for long unyielding marches.",
        "tags": ["virtue_diligence", "combat_mobility"], "stat_ranges": ITEM_STAT_RANGES["diligence_greaves"],
    },
    "diligence_anvil_charm": {
        "slot": "accessory", "name": "Charm of the Tireless Smith",
        "def": 12, "hp": 40, "atk": 10, "crit": 4.0, "speed": 0.05,
        "rarity": "rare", "effects": ["Smith's Endurance (+12 DEF, +10 ATK)"], "desc": "A miniature anvil worn as a talisman of persistent craftsmanship.",
        "tags": ["virtue_diligence", "combat_defensive"], "stat_ranges": ITEM_STAT_RANGES["diligence_anvil_charm"],
    },
}

def register_new_equipment_into_catalogs() -> None:
    """
    Registers all new weapons, sets, and accessories into ARMOR_DATA, EQUIPMENT_SETS,
    and ITEM_REGISTRY for seamless engine-wide interoperability.
    """
    from src.rpg import equipment
    from src.ui import inventory

    # 1. Update ARMOR_DATA
    for item_id, item_spec in NEW_EQUIPMENT_DATA.items():
        equipment.ARMOR_DATA[item_id] = {
            "slot": item_spec.get("slot", "accessory"),
            "name": item_spec.get("name", item_id.replace("_", " ").title()),
            "def": item_spec.get("def", 0),
            "hp": item_spec.get("hp", 0),
            "atk": item_spec.get("atk", 0),
            "crit": item_spec.get("crit", 0.0),
            "speed": item_spec.get("speed", 0.0),
            "mp_regen": item_spec.get("mp_regen", 0.0),
            "rarity": item_spec.get("rarity", "common"),
            "effects": item_spec.get("effects", []),
            "lore": item_spec.get("lore", ""),
            "desc": item_spec.get("desc", ""),
            "tags": item_spec.get("tags", []),
            "stat_ranges": item_spec.get("stat_ranges"),
        }

    # 2. Update EQUIPMENT_SETS with progressive sets
    for set_id, s_data in PROGRESSIVE_SETS.items():
        existing_set = equipment.EQUIPMENT_SETS.get(set_id, {})
        pieces_dict = dict(existing_set.get("pieces", {}))
        
        # Populate slot-based mapping for pieces
        for p in s_data.get("pieces", []):
            p_slot = equipment.ARMOR_DATA.get(p, {}).get("slot")
            if p_slot and p_slot not in pieces_dict:
                pieces_dict[p_slot] = p
            elif not p_slot:
                pieces_dict[p] = p

        max_tier = max(s_data.get("thresholds", {3: {}}).keys(), default=3)
        top_threshold = s_data.get("thresholds", {}).get(max_tier, {})

        equipment.EQUIPMENT_SETS[set_id] = {
            "name": s_data["name"],
            "pieces": pieces_dict,
            "desc": top_threshold.get("desc", existing_set.get("desc", "")),
            "atk_mult": top_threshold.get("atk_mult", existing_set.get("atk_mult", 0.0)),
            "def_mult": top_threshold.get("def_mult", existing_set.get("def_mult", 0.0)),
            "bonus_hp": top_threshold.get("bonus_hp", existing_set.get("bonus_hp", 0)),
            "bonus_crit": top_threshold.get("bonus_crit", existing_set.get("bonus_crit", 0.0)),
            "aura": top_threshold.get("aura", existing_set.get("aura")),
            "progressive_data": s_data,
            "thresholds": s_data.get("thresholds", {}),
        }

    # 3. Synchronize with ITEM_REGISTRY
    from src.constants import RARITY_HEX_COLORS
    for item_id, item_spec in NEW_EQUIPMENT_DATA.items():
        if item_id not in inventory.ITEM_REGISTRY:
            slot_c = item_spec.get("slot", "accessory")
            cat_str = f"armor_{slot_c}" if slot_c in ("head", "chest", "legs") else ("weapon" if slot_c == "weapon" else "accessory")
            rarity = item_spec.get("rarity", "common")
            inventory.ITEM_REGISTRY[item_id] = {
                "name": item_spec.get("name", item_id.replace("_", " ").title()),
                "cat": cat_str,
                "power": 0,
                "damage": item_spec.get("atk", 0),
                "atk": item_spec.get("atk", 0),
                "def": item_spec.get("def", 0),
                "crit": item_spec.get("crit", 0.0),
                "speed": item_spec.get("speed", 0.0),
                "hp": item_spec.get("hp", 0),
                "mp": 0,
                "mp_regen": item_spec.get("mp_regen", 0.0),
                "max_stack": 1,
                "tile": None,
                "rarity": rarity,
                "color": RARITY_HEX_COLORS.get(rarity, "#9E9E9E"),
                "desc": item_spec.get("desc", ""),
                "lore": item_spec.get("lore", ""),
                "effects": item_spec.get("effects", []),
                "special": " • ".join(item_spec.get("effects", [])),
                "tags": item_spec.get("tags", []),
                "stat_ranges": item_spec.get("stat_ranges"),
            }


# -----------------------------------------------------------------------------
# 6. SAVE INTEGRITY & ANTI-CHEAT HMAC SECURITY
# -----------------------------------------------------------------------------

# Secret pepper for computing world save integrity checksums
_SAVE_HMAC_PEPPER = b"Potaria_Save_Security_Salt_2026_AntiCheat"

def compute_save_signature(payload_bytes: bytes) -> str:
    """Computes an HMAC-SHA256 signature for world save JSON byte payload."""
    return hmac.new(_SAVE_HMAC_PEPPER, payload_bytes, hashlib.sha256).hexdigest()

def verify_save_signature(payload_bytes: bytes, signature: str) -> bool:
    """Verifies that the save file payload matches its cryptographic HMAC signature."""
    expected = compute_save_signature(payload_bytes)
    return hmac.compare_digest(expected, signature)

def create_equipment_stack(item_id: str, count: int = 1, enhancement_level: int = 0, affixes: Optional[List[str]] = None, tags: Optional[List[str]] = None, rng_seed: Optional[int] = None):
    """
    Creates an ItemStack with randomized base stats rolled strictly within predefined attribute ranges,
    along with correct tags and strict additional affix slot limits.
    """
    from src.ui.inventory import ItemStack
    rolls = roll_item_stat_ranges(item_id, rng_seed=rng_seed)
    spec_tags = tags
    if spec_tags is None and item_id in NEW_EQUIPMENT_DATA:
        spec_tags = list(NEW_EQUIPMENT_DATA[item_id].get("tags", []))
    return ItemStack(
        item_id,
        count=count,
        enhancement_level=enhancement_level,
        affixes=affixes,
        base_rolls=rolls,
        tags=spec_tags,
    )

