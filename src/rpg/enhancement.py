"""
Potaria - Item Enhancement & Affix System
Handles:
1. Item Enhancement (+1 to +7):
   - Basic stats scale up to double base stats at +7.
   - Enhancing requires rare materials and coins.
   - Levels +1 to +4 are safe (no break).
   - Levels +5, +6, +7 have risk of breaking!
   - Broken items cannot be equipped or used until repaired by Mystic Trader for 1 Gold Coin.
2. Affix Slot & Affix Stone System:
   - "Add Affix Slot" service from Mystic Trader for Legendary & Ancient items:
     replaces a random basic stat with an open affix slot.
   - "Affix Stone" crafted at Work Bench with endgame materials.
   - Applying Affix Stone embeds powerful god-tier affixes.
Developer: Kurados
"""

import random
from src.constants import (
    RARITY_COMMON, RARITY_UNCOMMON, RARITY_RARE,
    RARITY_EPIC, RARITY_MYTHIC, RARITY_LEGENDARY, RARITY_ANCIENT
)
from src.ui.inventory import ITEM_REGISTRY, ITEM_ALIASES

# Max enhancement level
MAX_ENHANCEMENT_LEVEL = 7

# Materials and coins required per enhancement level
ENHANCEMENT_REQUIREMENTS = {
    1: {"copper": 20, "materials": {"copper_bar": 2}, "success_rate": 1.00, "break_rate": 0.00},
    2: {"copper": 50, "materials": {"iron_bar": 2}, "success_rate": 0.90, "break_rate": 0.00},
    3: {"copper": 100, "materials": {"iron_bar": 3, "gold_bar": 1}, "success_rate": 0.80, "break_rate": 0.00},
    4: {"copper": 200, "materials": {"gold_bar": 3, "spud_sap": 2}, "success_rate": 0.70, "break_rate": 0.00},
    5: {"copper": 500, "materials": {"gold_bar": 5, "blightstone": 3}, "success_rate": 0.50, "break_rate": 0.20},
    6: {"copper": 1000, "materials": {"gold_bar": 8, "portal_shard": 1, "blightstone": 5}, "success_rate": 0.40, "break_rate": 0.25},
    7: {"copper": 2500, "materials": {"gold_bar": 10, "portal_shard": 2, "spud_sap": 5}, "success_rate": 0.30, "break_rate": 0.30},
}

# Repair cost for broken equipment (1 Gold Coin = 10,000 Copper)
REPAIR_COST_COPPER = 10000

# God-Tier Affixes grantable by Affix Stones
GOD_TIER_AFFIXES = {
    "Titan's Might": {
        "desc": "+25% All Physical & Skill Damage",
        "atk_mult": 0.25,
        "bonus_atk": 15,
    },
    "Celestial Aegis": {
        "desc": "+15 Defense & +50 Max HP",
        "bonus_def": 15,
        "bonus_hp": 50,
    },
    "Chronos Velocity": {
        "desc": "+30% Attack Speed & Movement Speed",
        "bonus_atk_speed": 0.30,
        "bonus_speed": 0.30,
    },
    "Astral Omniscience": {
        "desc": "+50 Max MP & 15% Skill Mana Reduction",
        "bonus_mp": 50,
        "mp_cost_reduction": 0.15,
    },
    "Vampiric Leech": {
        "desc": "+8% Life Steal on Hit",
        "life_steal": 0.08,
    },
    "Solar Flare": {
        "desc": "+25 Fire Damage & Ignites targets",
        "bonus_atk": 10,
        "element": "fire",
    },
    "Void Singularity": {
        "desc": "+30 Void Damage & 10% Black Hole pull on hit",
        "bonus_atk": 12,
        "element": "void",
    },
    "Frostbite Cryo": {
        "desc": "+20 Frost Damage & -50% Target Slow",
        "bonus_atk": 8,
        "element": "frost",
    },
}

def get_enhancement_multiplier(level):
    """
    Returns stat scaling multiplier for enhancement level (+0 to +7).
    At +7, stat doubles (multiplier = 2.0).
    """
    lvl = max(0, min(MAX_ENHANCEMENT_LEVEL, int(level)))
    return 1.0 + (lvl / float(MAX_ENHANCEMENT_LEVEL))

def can_enhance_item(item):
    """Checks if an item can be enhanced."""
    if not item:
        return False, "No item selected."
    if getattr(item, "is_broken", False):
        return False, "This item is BROKEN! Repair it at the Mystic Trader first."
    lvl = getattr(item, "enhancement_level", 0)
    if lvl >= MAX_ENHANCEMENT_LEVEL:
        return False, f"Item is already at MAX enhancement (+{MAX_ENHANCEMENT_LEVEL})!"
    data = item.data if hasattr(item, "data") else {}
    cat = data.get("cat", "")
    is_gear = (cat == "weapon" or cat.startswith("armor_") or cat == "accessory" or data.get("damage", 0) > 0 or data.get("def", 0) > 0)
    if not is_gear:
        return False, "Only weapons, armor, and accessories can be enhanced."
    return True, "Ready to enhance."

def enhance_item(item, inventory, sound_manager=None):
    """
    Attempts to enhance item to the next level using player inventory resources.
    Returns (status_code, message) where status_code in ('success', 'failure', 'broken', 'error').
    """
    can_enh, reason = can_enhance_item(item)
    if not can_enh:
        return "error", reason

    cur_lvl = getattr(item, "enhancement_level", 0)
    target_lvl = cur_lvl + 1
    req = ENHANCEMENT_REQUIREMENTS[target_lvl]

    # 1. Check coins
    coin_cost = req["copper"]
    if inventory.total_coins_value() < coin_cost:
        return "error", f"Requires {coin_cost} Copper Coins (You have {inventory.total_coins_value()})."

    # 2. Check materials
    for mat_id, mat_cnt in req["materials"].items():
        if inventory.count_item(mat_id) < mat_cnt:
            mat_name = ITEM_REGISTRY.get(mat_id, {}).get("name", mat_id.replace("_", " ").title())
            return "error", f"Requires {mat_cnt}x {mat_name} (You have {inventory.count_item(mat_id)})."

    # 3. Deduct coins and materials
    inventory.remove_coins(coin_cost)
    for mat_id, mat_cnt in req["materials"].items():
        inventory.remove_item(mat_id, mat_cnt)

    # 4. Roll outcome
    roll = random.random()
    succ_rate = req["success_rate"]
    break_rate = req["break_rate"]

    item_name = item.data.get("name", item.item_id)

    if roll < succ_rate:
        # Success!
        item.enhancement_level = target_lvl
        if sound_manager:
            sound_manager.play("craft")
        mult = get_enhancement_multiplier(target_lvl)
        pct = int(round((mult - 1.0) * 100))
        return "success", f"★ SUCCESS! {item_name} enhanced to +{target_lvl}! (Stats +{pct}%)"
    elif roll < (succ_rate + break_rate):
        # Broken!
        item.is_broken = True
        if sound_manager:
            sound_manager.play("hit")
        return "broken", f"CRITICAL FAILURE! {item_name} has BROKEN! It cannot be used until repaired by the Mystic Trader for 1 Gold Coin."
    else:
        # Failure without breaking
        if sound_manager:
            sound_manager.play("dig_stone")
        return "failure", f"Enhancement attempt failed! Materials consumed, but {item_name} remained intact at +{cur_lvl}."

def repair_item(item, inventory, sound_manager=None):
    """
    Repairs a broken equipment item for 1 Gold Coin (10,000 Copper).
    """
    if not item:
        return False, "No item selected to repair."
    if not getattr(item, "is_broken", False):
        return False, "This item is not broken."

    if inventory.total_coins_value() < REPAIR_COST_COPPER:
        return False, f"Repair requires 1 Gold Coin (10,000 Copper). You have {inventory.total_coins_value()} Copper."

    inventory.remove_coins(REPAIR_COST_COPPER)
    item.is_broken = False
    if sound_manager:
        sound_manager.play("craft")
    item_name = item.data.get("name", item.item_id)
    return True, f"Repaired! {item_name} is fully restored to pristine battle condition!"

def can_add_affix_slot(item):
    """
    Checks if item is eligible for an Affix Slot.
    Allows Epic (1 slot), Mythic (2 slots), and Legendary/Ancient (up to 3 slots).
    """
    if not item:
        return False, "No item selected."
    data = item.data if hasattr(item, "data") else {}
    rarity = str(data.get("rarity", "")).lower()
    if rarity not in (RARITY_EPIC, RARITY_LEGENDARY, RARITY_MYTHIC, RARITY_ANCIENT, "epic", "legendary", "mythic", "ancient"):
        return False, "Only Epic, Mythic, Legendary and Ancient items can receive an Affix Slot!"

    if getattr(item, "is_broken", False):
        return False, "Cannot carve affix slot into a broken item! Repair it first."

    if rarity in (RARITY_EPIC, "epic"):
        max_slots = 1
    elif rarity in (RARITY_MYTHIC, "mythic"):
        max_slots = 2
    else:
        max_slots = 3

    cur_slots = getattr(item, "affix_slots", 0)
    if cur_slots >= max_slots:
        return False, f"This item has already reached the maximum limit of {max_slots} Affix Slots (maximum of {max_slots}) for {rarity.title()} rarity!"

    stat_candidates = []
    removed = set(getattr(item, "removed_stats", []))
    for s in ("atk", "def", "crit", "speed", "hp", "mp", "damage"):
        if s not in removed and data.get(s, 0) > 0:
            stat_candidates.append(s)

    if not stat_candidates:
        return False, "This item has no remaining basic stats that can be converted into an Affix Slot."

    return True, "Ready to carve Affix Slot."

def add_affix_slot_to_item(item, inventory=None, cost_copper=5000, sound_manager=None):
    """
    Carves an Affix Slot into an eligible piece by sacrificing a random basic stat.
    """
    can_add, reason = can_add_affix_slot(item)
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

    if not hasattr(item, "removed_stats") or item.removed_stats is None:
        item.removed_stats = []
    item.removed_stats.append(chosen_stat)

    item.affix_slots = getattr(item, "affix_slots", 0) + 1
    item.additional_affix_slots = getattr(item, "additional_affix_slots", 0) + 1

    if not hasattr(item, "affixes") or item.affixes is None:
        item.affixes = []

    if sound_manager and hasattr(sound_manager, "play"):
        sound_manager.play("craft")

    item_name = data.get("name", getattr(item, "item_id", "Item"))
    stat_label = chosen_stat.upper()
    return True, f"Affix Slot Carved into {item_name}! Replaced {stat_label} (-{old_val}) with 1 Open Affix Slot (Total Slots: {item.affix_slots})."

def can_apply_affix_stone(item):
    """Checks whether an item can receive an Affix Stone."""
    if not item:
        return False, "No item selected."
    data = item.data if hasattr(item, "data") else {}
    rarity = str(data.get("rarity", "")).lower()
    if rarity not in (RARITY_EPIC, RARITY_LEGENDARY, RARITY_MYTHIC, RARITY_ANCIENT, "epic", "legendary", "mythic", "ancient"):
        return False, "Affix Stones can only be embedded into Epic, Legendary, Mythic, or Ancient equipment."
    total_slots = getattr(item, "affix_slots", 0)
    current_affixes = getattr(item, "affixes", [])
    if len(current_affixes) >= total_slots:
        return False, f"No open affix slots available! (Affixes: {len(current_affixes)}/{total_slots})."
    return True, "Item is ready to receive an Affix Stone."

def apply_affix_stone(item, inventory, sound_manager=None):
    """
    Embeds an Affix Stone into an open affix slot on an eligible Epic/Legendary/Mythic/Ancient item.
    Grants a god-tier affix from GOD_TIER_AFFIXES.
    """
    if not item:
        return False, "No item selected."

    data = item.data if hasattr(item, "data") else {}
    rarity = str(data.get("rarity", "")).lower()
    if rarity not in (RARITY_EPIC, RARITY_LEGENDARY, RARITY_MYTHIC, RARITY_ANCIENT, "epic", "legendary", "mythic", "ancient"):
        return False, "Affix Stones can only be embedded into Epic, Legendary, Mythic, or Ancient equipment."

    total_slots = getattr(item, "affix_slots", 0)
    current_affixes = getattr(item, "affixes", [])
    if len(current_affixes) >= total_slots:
        return False, f"No open Affix Slots available! (Affixes: {len(current_affixes)}/{total_slots}). Visit the Mystic Trader to carve a slot."

    if getattr(inventory, "held_item", None) and inventory.held_item.item_id == "affix_stone":
        inventory.held_item.count -= 1
        if inventory.held_item.count <= 0:
            inventory.held_item = None
    elif inventory.count_item("affix_stone") < 1:
        return False, "You do not possess an Affix Stone! Craft one at a Work Bench."
    else:
        # Deduct 1 Affix Stone from inventory
        inventory.remove_item("affix_stone", 1)

    # Pick an affix not already present on the item
    available = [a for a in GOD_TIER_AFFIXES.keys() if a not in current_affixes]
    if not available:
        available = list(GOD_TIER_AFFIXES.keys())
    rolled_affix = random.choice(available)

    if not hasattr(item, "affixes"):
        item.affixes = []
    item.affixes.append(rolled_affix)

    if sound_manager:
        sound_manager.play("craft")

    item_name = data.get("name", item.item_id)
    affix_desc = GOD_TIER_AFFIXES[rolled_affix]["desc"]
    return True, f"★ GOD-TIER AFFIX EMBEDDED! {item_name} gained [{rolled_affix}] ({affix_desc})!"
