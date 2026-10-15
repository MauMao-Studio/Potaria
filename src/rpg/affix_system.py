"""
Affix System and Category Restriction Rules Engine for Potaria.
Enforces strict category-based affix restrictions:
- Weapons can ONLY roll offensive stats: damage, attack, attack speed, critical chance,
  critical damage, armor penetration, lifesteal, and knockback.
- Defensive affixes (flat DEF, % DEF, Armor, Damage Reduction, Magic Resistance,
  Knockback Resistance, Rootbound, of the Root, of the Vanguard) are strictly restricted
  to Armor (head, chest, legs), Shields, and Accessories.
"""

from typing import Dict, Any, List, Optional, Set

DEFENSIVE_STATS: Set[str] = {
    "def",
    "defense",
    "armor",
    "dmg_reduction",
    "dmg_reduc",
    "damage_reduction",
    "knockback_res",
    "magic_resist",
    "magic_resistance",
}

OFFENSIVE_STATS: Set[str] = {
    "damage",
    "atk",
    "attack",
    "crit",
    "crit_chance",
    "crit_dmg",
    "speed",
    "atk_speed",
    "lifesteal",
    "armor_pen",
    "armor_penetration",
    "knockback",
}

DEFENSIVE_AFFIX_NAMES: Set[str] = {
    "rootbound",
    "of the root",
    "of the vanguard",
    "sturdy",
    "reinforced",
    "warded",
    "guardian's",
    "guardians",
}


def is_defensive_affix(affix_data: Dict[str, Any]) -> bool:
    """Checks whether an affix modifies any defensive attributes or is a known defensive affix."""
    if not isinstance(affix_data, dict):
        return False
    name = affix_data.get("name", "").lower()
    aff_id = affix_data.get("id", "").lower()
    if name in DEFENSIVE_AFFIX_NAMES or aff_id in DEFENSIVE_AFFIX_NAMES:
        return True
    stat_mods = affix_data.get("stat_mods", {})
    if any(k.lower() in DEFENSIVE_STATS for k in stat_mods.keys()):
        return True
    stat_ranges = affix_data.get("stat_ranges", {})
    if any(k.lower() in DEFENSIVE_STATS for k in stat_ranges.keys()):
        return True
    return False


def is_affix_allowed_on_category(affix_data: Dict[str, Any], category: str) -> bool:
    """
    Validates whether an affix can be applied to an item of the given category.
    Weapons are strictly forbidden from receiving defensive affixes.
    """
    cat = (category or "").lower()
    if cat in ("weapon", "cat_weapon"):
        if is_defensive_affix(affix_data):
            return False
        return True
    return True


def scrub_defensive_stats_from_weapon(weapon_data: Dict[str, Any]) -> Dict[str, Any]:
    """Ensures a weapon dictionary has strictly 0 defense."""
    if isinstance(weapon_data, dict):
        weapon_data["def"] = 0
        if "defense" in weapon_data:
            weapon_data["defense"] = 0
    return weapon_data
