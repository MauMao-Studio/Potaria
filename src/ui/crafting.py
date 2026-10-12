"""
Potaria - Crafting Engine (Minecraft-Style Categorized Recipe Book)
Categorized recipes across Building, Equipment, Survival & Consumables, and Furniture & Mechanisms.
Includes 110+ craftable recipes across Hand, Work Bench, and Furnace stations.
Developer: Kurados | Pure Python 3.13 & pygame-ce
"""

import math
import pygame
from src.constants import (
    SCALED_TILE, TILE_WORK_BENCH, TILE_FURNACE,
    RARITY_COLORS, RARITY_COMMON,
    CRAFT_CAT_ALL, CRAFT_CAT_BUILDING, CRAFT_CAT_EQUIPMENT,
    CRAFT_CAT_SURVIVAL, CRAFT_CAT_FURNITURE
)
from src.ui.inventory import ITEM_REGISTRY

# Minecraft-Inspired Recipe Book Filter Tabs
CRAFT_TABS = [
    {"id": CRAFT_CAT_ALL, "label": "ALL", "full_name": "ALL RECIPES", "tooltip": "Show all available recipes"},
    {"id": CRAFT_CAT_BUILDING, "label": "BUILDING", "full_name": "BUILDING BLOCKS", "tooltip": "Blocks, bricks, walls, rungs & scaffolds"},
    {"id": CRAFT_CAT_EQUIPMENT, "label": "EQUIPMENT", "full_name": "EQUIPMENT & GEAR", "tooltip": "Tools, weapons, armor, shields & accessories"},
    {"id": CRAFT_CAT_SURVIVAL, "label": "SURVIVAL", "full_name": "SURVIVAL & CONSUMABLES", "tooltip": "Food, potions, utility tools & materials"},
    {"id": CRAFT_CAT_FURNITURE, "label": "FURNITURE", "full_name": "FURNITURE & MECHANISMS", "tooltip": "Chests, hearths, beds, workstations, clocks & lights"},
]

RECIPES = [
    # =========================================================================
    # 1. Basic Crafting (By Hand / Anywhere)
    # =========================================================================
    {
        "result": "work_bench", "count": 1, "station": None, "category": CRAFT_CAT_FURNITURE,
        "ingredients": [("wood", 10)]
    },
    {
        "result": "wood_platform", "count": 2, "station": None, "category": CRAFT_CAT_BUILDING,
        "ingredients": [("wood", 1)]
    },
    {
        "result": "torch", "count": 3, "station": None, "category": CRAFT_CAT_FURNITURE,
        "ingredients": [("wood", 1), ("spud_sap", 1)]
    },
    {
        "result": "wood_axe", "count": 1, "station": None, "category": CRAFT_CAT_EQUIPMENT,
        "ingredients": [("wood", 6)]
    },
    {
        "result": "wooden_sword", "count": 1, "station": None, "category": CRAFT_CAT_EQUIPMENT,
        "ingredients": [("wood", 7)]
    },
    {
        "result": "wood_shovel", "count": 1, "station": None, "category": CRAFT_CAT_EQUIPMENT,
        "ingredients": [("wood", 4)]
    },
    {
        "result": "wood_pickaxe", "count": 1, "station": None, "category": CRAFT_CAT_EQUIPMENT,
        "ingredients": [("wood", 10)]
    },
    {
        "result": "wooden_arrow", "count": 25, "station": None, "category": CRAFT_CAT_EQUIPMENT,
        "ingredients": [("wood", 1), ("stone_block", 1)]
    },
    {
        "result": "rope_rungs", "count": 3, "station": None, "category": CRAFT_CAT_BUILDING,
        "ingredients": [("wood", 2), ("spud_sap", 1)]
    },
    {
        "result": "bamboo_scaffold", "count": 4, "station": None, "category": CRAFT_CAT_BUILDING,
        "ingredients": [("wood", 3), ("spud_sap", 1)]
    },
    {
        "result": "dried_thatch_bale", "count": 1, "station": None, "category": CRAFT_CAT_BUILDING,
        "ingredients": [("wood", 3), ("spud_sap", 2)]
    },
    {
        "result": "pyrite_sparker", "count": 1, "station": None, "category": CRAFT_CAT_EQUIPMENT,
        "ingredients": [("iron_bar", 1), ("stone_block", 1)]
    },
    {
        "result": "spud_angler_rod", "count": 1, "station": None, "category": CRAFT_CAT_EQUIPMENT,
        "ingredients": [("wood", 4), ("spud_sap", 2)]
    },
    {
        "result": "copper_harvester_sickle", "count": 1, "station": None, "category": CRAFT_CAT_EQUIPMENT,
        "ingredients": [("copper_bar", 4), ("wood", 2)]
    },
    {
        "result": "herbal_salve", "count": 1, "station": None, "category": CRAFT_CAT_SURVIVAL,
        "ingredients": [("raw_potato", 1), ("spud_sap", 1)]
    },
    {
        "result": "burlap_tether", "count": 1, "station": None, "category": CRAFT_CAT_SURVIVAL,
        "ingredients": [("wood", 2), ("spud_sap", 3)]
    },
    {
        "result": "cozy_hearth_pit", "count": 1, "station": None, "category": CRAFT_CAT_FURNITURE,
        "ingredients": [("wood", 6), ("torch", 2), ("stone_block", 4)]
    },
    {
        "result": "carved_tuber_lantern", "count": 1, "station": None, "category": CRAFT_CAT_FURNITURE,
        "ingredients": [("raw_potato", 3), ("torch", 1)]
    },

    # =========================================================================
    # 2. Food Cooking & Smelting (Furnace)
    # =========================================================================
    {
        "result": "mashed_potato", "count": 1, "station": "furnace", "category": CRAFT_CAT_SURVIVAL,
        "ingredients": [("raw_potato", 2), ("wood", 1)]
    },
    {
        "result": "golden_fry", "count": 1, "station": "furnace", "category": CRAFT_CAT_SURVIVAL,
        "ingredients": [("raw_potato", 3), ("gold_bar", 1)]
    },
    {
        "result": "copper_bar", "count": 1, "station": "furnace", "category": CRAFT_CAT_SURVIVAL,
        "ingredients": [("copper_ore", 3)]
    },
    {
        "result": "iron_bar", "count": 1, "station": "furnace", "category": CRAFT_CAT_SURVIVAL,
        "ingredients": [("iron_ore", 3)]
    },
    {
        "result": "gold_bar", "count": 1, "station": "furnace", "category": CRAFT_CAT_SURVIVAL,
        "ingredients": [("gold_ore", 3)]
    },
    {
        "result": "stone_brick", "count": 1, "station": "furnace", "category": CRAFT_CAT_BUILDING,
        "ingredients": [("stone_block", 2)]
    },
    {
        "result": "glass_window", "count": 2, "station": "furnace", "category": CRAFT_CAT_BUILDING,
        "ingredients": [("sand_block", 2)]
    },
    {
        "result": "stone_fireplace", "count": 1, "station": "work_bench", "category": CRAFT_CAT_FURNITURE,
        "ingredients": [("stone_block", 12), ("wood", 4), ("torch", 2)]
    },
    {
        "result": "mosaic_tiles", "count": 4, "station": "furnace", "category": CRAFT_CAT_BUILDING,
        "ingredients": [("dirt_block", 2), ("sand_block", 2)]
    },
    {
        "result": "hardened_clay_shingles", "count": 4, "station": "furnace", "category": CRAFT_CAT_BUILDING,
        "ingredients": [("dirt_block", 4), ("stone_block", 2)]
    },
    {
        "result": "hearty_root_stew", "count": 1, "station": "furnace", "category": CRAFT_CAT_SURVIVAL,
        "ingredients": [("raw_potato", 3), ("glowing_mushroom", 1), ("wood", 1)]
    },
    {
        "result": "glazed_golden_tuber", "count": 1, "station": "furnace", "category": CRAFT_CAT_SURVIVAL,
        "ingredients": [("raw_potato", 2), ("gold_bar", 2)]
    },
    {
        "result": "smoked_spud_jerky", "count": 2, "station": "furnace", "category": CRAFT_CAT_SURVIVAL,
        "ingredients": [("raw_potato", 2), ("wood", 1)]
    },
    {
        "result": "gilded_russet", "count": 1, "station": "furnace", "category": CRAFT_CAT_SURVIVAL,
        "ingredients": [("raw_potato", 3), ("gold_bar", 3)]
    },
    {
        "result": "glass_flask", "count": 3, "station": "furnace", "category": CRAFT_CAT_SURVIVAL,
        "ingredients": [("sand_block", 3)]
    },
    {
        "result": "abyssal_alloy_bar", "count": 1, "station": "furnace", "category": CRAFT_CAT_SURVIVAL,
        "ingredients": [("blightstone_block", 4), ("gold_bar", 2), ("iron_bar", 2)]
    },
    {
        "result": "potato_bread", "count": 2, "station": "furnace", "category": CRAFT_CAT_SURVIVAL,
        "ingredients": [("raw_potato", 3), ("wood", 1)]
    },
    {
        "result": "sweet_tuber_pie", "count": 1, "station": "furnace", "category": CRAFT_CAT_SURVIVAL,
        "ingredients": [("raw_potato", 2), ("spud_sap", 2), ("wood", 1)]
    },
    {
        "result": "cooked_bangus", "count": 1, "station": "furnace", "category": CRAFT_CAT_SURVIVAL,
        "ingredients": [("raw_bangus", 1)]
    },
    {
        "result": "cooked_tilapia", "count": 1, "station": "furnace", "category": CRAFT_CAT_SURVIVAL,
        "ingredients": [("raw_tilapia", 1)]
    },
    {
        "result": "cooked_galunggong", "count": 1, "station": "furnace", "category": CRAFT_CAT_SURVIVAL,
        "ingredients": [("raw_galunggong", 1)]
    },
    {
        "result": "cooked_maya_maya", "count": 1, "station": "furnace", "category": CRAFT_CAT_SURVIVAL,
        "ingredients": [("raw_maya_maya", 1)]
    },
    {
        "result": "cooked_tanigue", "count": 1, "station": "furnace", "category": CRAFT_CAT_SURVIVAL,
        "ingredients": [("raw_tanigue", 1)]
    },
    {
        "result": "cooked_tambakol", "count": 1, "station": "furnace", "category": CRAFT_CAT_SURVIVAL,
        "ingredients": [("raw_tambakol", 1)]
    },
    {
        "result": "cooked_lapu_lapu", "count": 1, "station": "furnace", "category": CRAFT_CAT_SURVIVAL,
        "ingredients": [("raw_lapu_lapu", 1)]
    },
    {
        "result": "cooked_hito", "count": 1, "station": "furnace", "category": CRAFT_CAT_SURVIVAL,
        "ingredients": [("raw_hito", 1)]
    },
    {
        "result": "cooked_dilis", "count": 1, "station": "furnace", "category": CRAFT_CAT_SURVIVAL,
        "ingredients": [("raw_dilis", 1)]
    },
    {
        "result": "cooked_dalagang_bukid", "count": 1, "station": "furnace", "category": CRAFT_CAT_SURVIVAL,
        "ingredients": [("raw_dalagang_bukid", 1)]
    },
    # --- Authentic Filipino Culinary Cuisine & Delicacies ---
    {
        "result": "chicken_adobo", "count": 1, "station": "furnace", "category": CRAFT_CAT_SURVIVAL,
        "ingredients": [("raw_chicken", 1), ("soy_sauce", 1), ("vinegar", 1), ("garlic", 1)]
    },
    {
        "result": "pork_adobo", "count": 1, "station": "furnace", "category": CRAFT_CAT_SURVIVAL,
        "ingredients": [("raw_pork", 1), ("soy_sauce", 1), ("vinegar", 1), ("garlic", 1)]
    },
    {
        "result": "sinigang", "count": 1, "station": "furnace", "category": CRAFT_CAT_SURVIVAL,
        "ingredients": [("pork_belly", 1), ("tamarind", 1), ("onion", 1), ("eggplant", 1)]
    },
    {
        "result": "kare_kare", "count": 1, "station": "furnace", "category": CRAFT_CAT_SURVIVAL,
        "ingredients": [("raw_beef", 1), ("peanut_butter", 1), ("eggplant", 1), ("string_beans", 1)]
    },
    {
        "result": "bulalo", "count": 1, "station": "furnace", "category": CRAFT_CAT_SURVIVAL,
        "ingredients": [("raw_beef", 1), ("onion", 1), ("black_pepper", 1)]
    },
    {
        "result": "tinola", "count": 1, "station": "furnace", "category": CRAFT_CAT_SURVIVAL,
        "ingredients": [("raw_chicken", 1), ("ginger", 1), ("onion", 1)]
    },
    {
        "result": "lechon", "count": 1, "station": "furnace", "category": CRAFT_CAT_SURVIVAL,
        "ingredients": [("pork_belly", 1), ("garlic", 1), ("vinegar", 1)]
    },
    {
        "result": "pancit_bihon", "count": 1, "station": "furnace", "category": CRAFT_CAT_SURVIVAL,
        "ingredients": [("pancit_noodles", 1), ("raw_pork", 1), ("garlic", 1), ("onion", 1)]
    },
    {
        "result": "arroz_caldo", "count": 1, "station": "furnace", "category": CRAFT_CAT_SURVIVAL,
        "ingredients": [("raw_chicken", 1), ("rice", 1), ("ginger", 1)]
    },
    {
        "result": "halo_halo", "count": 1, "station": None, "category": CRAFT_CAT_SURVIVAL,
        "ingredients": [("shaved_ice", 1), ("condensed_milk", 1), ("ube_halaya", 1)]
    },
    {
        "result": "kaldereta", "count": 1, "station": "furnace", "category": CRAFT_CAT_SURVIVAL,
        "ingredients": [("raw_goat_meat", 1), ("onion", 1), ("garlic", 1), ("black_pepper", 1)]
    },
    {
        "result": "balut", "count": 1, "station": None, "category": CRAFT_CAT_SURVIVAL,
        "ingredients": [("duck_egg", 1), ("salt", 1)]
    },
    {
        "result": "itlog_na_maalat", "count": 1, "station": None, "category": CRAFT_CAT_SURVIVAL,
        "ingredients": [("duck_egg", 1), ("salt", 1)]
    },
    {
        "result": "sinangag", "count": 1, "station": "furnace", "category": CRAFT_CAT_SURVIVAL,
        "ingredients": [("rice", 1), ("garlic", 1)]
    },
    {
        "result": "daing_na_bangus", "count": 1, "station": "furnace", "category": CRAFT_CAT_SURVIVAL,
        "ingredients": [("raw_bangus", 1), ("garlic", 1), ("vinegar", 1)]
    },
    {
        "result": "salt", "count": 2, "station": "furnace", "category": CRAFT_CAT_SURVIVAL,
        "ingredients": [("seaweed", 2)]
    },
    {
        "result": "vinegar", "count": 2, "station": None, "category": CRAFT_CAT_SURVIVAL,
        "ingredients": [("spud_sap", 1)]
    },
    {
        "result": "shaved_ice", "count": 2, "station": None, "category": CRAFT_CAT_SURVIVAL,
        "ingredients": [("snow_block", 1)]
    },
    {
        "result": "iron_cauldron", "count": 1, "station": "furnace", "category": CRAFT_CAT_FURNITURE,
        "ingredients": [("iron_bar", 7)]
    },

    # =========================================================================
    # 3. Work Bench — Building Blocks & Homestead Furniture
    # =========================================================================
    {
        "result": "roof_tiles", "count": 4, "station": "work_bench", "category": CRAFT_CAT_BUILDING,
        "ingredients": [("stone_block", 2), ("dirt_block", 2)]
    },
    {
        "result": "wood_planks", "count": 4, "station": "work_bench", "category": CRAFT_CAT_BUILDING,
        "ingredients": [("wood", 1)]
    },
    {
        "result": "wooden_door", "count": 1, "station": "work_bench", "category": CRAFT_CAT_FURNITURE,
        "ingredients": [("wood", 6)]
    },
    {
        "result": "wooden_table", "count": 1, "station": "work_bench", "category": CRAFT_CAT_FURNITURE,
        "ingredients": [("wood", 8)]
    },
    {
        "result": "wooden_chair", "count": 1, "station": "work_bench", "category": CRAFT_CAT_FURNITURE,
        "ingredients": [("wood", 4)]
    },
    {
        "result": "wooden_bed", "count": 1, "station": "work_bench", "category": CRAFT_CAT_FURNITURE,
        "ingredients": [("wood", 12), ("spud_sap", 4)]
    },
    {
        "result": "bookshelf", "count": 1, "station": "work_bench", "category": CRAFT_CAT_FURNITURE,
        "ingredients": [("wood", 10), ("bone", 2)]
    },
    {
        "result": "grandfather_clock", "count": 1, "station": "work_bench", "category": CRAFT_CAT_FURNITURE,
        "ingredients": [("wood", 10), ("iron_bar", 2), ("gold_bar", 1)]
    },
    {
        "result": "candelabra", "count": 1, "station": "work_bench", "category": CRAFT_CAT_FURNITURE,
        "ingredients": [("copper_bar", 3), ("torch", 3)]
    },
    {
        "result": "chandelier", "count": 1, "station": "work_bench", "category": CRAFT_CAT_FURNITURE,
        "ingredients": [("gold_bar", 3), ("torch", 4), ("iron_bar", 1)]
    },
    {
        "result": "potted_plant", "count": 1, "station": "work_bench", "category": CRAFT_CAT_FURNITURE,
        "ingredients": [("stone_block", 2), ("dirt_block", 2), ("raw_potato", 1)]
    },
    {
        "result": "wooden_dresser", "count": 1, "station": "work_bench", "category": CRAFT_CAT_FURNITURE,
        "ingredients": [("wood", 10), ("copper_bar", 1)]
    },
    {
        "result": "wall_tapestry", "count": 1, "station": "work_bench", "category": CRAFT_CAT_FURNITURE,
        "ingredients": [("wood", 2), ("spud_sap", 4)]
    },
    {
        "result": "bathtub", "count": 1, "station": "work_bench", "category": CRAFT_CAT_FURNITURE,
        "ingredients": [("iron_bar", 4), ("wood", 2)]
    },
    {
        "result": "sink", "count": 1, "station": "work_bench", "category": CRAFT_CAT_FURNITURE,
        "ingredients": [("iron_bar", 2), ("wood", 4)]
    },
    {
        "result": "painting", "count": 1, "station": "work_bench", "category": CRAFT_CAT_FURNITURE,
        "ingredients": [("wood", 4), ("spud_sap", 2), ("gold_bar", 1)]
    },
    {
        "result": "wood_shelf", "count": 2, "station": "work_bench", "category": CRAFT_CAT_FURNITURE,
        "ingredients": [("wood", 2)]
    },
    {
        "result": "wood_wall", "count": 4, "station": "work_bench", "category": CRAFT_CAT_BUILDING,
        "ingredients": [("wood", 1)]
    },
    {
        "result": "stone_brick_wall", "count": 4, "station": "work_bench", "category": CRAFT_CAT_BUILDING,
        "ingredients": [("stone_brick", 1)]
    },
    {
        "result": "carved_stone_bricks", "count": 2, "station": "work_bench", "category": CRAFT_CAT_BUILDING,
        "ingredients": [("stone_brick", 2)]
    },
    {
        "result": "cobblestone_parapet", "count": 4, "station": "work_bench", "category": CRAFT_CAT_BUILDING,
        "ingredients": [("stone_block", 4)]
    },
    {
        "result": "wrought_iron_palisade", "count": 4, "station": "work_bench", "category": CRAFT_CAT_BUILDING,
        "ingredients": [("iron_bar", 2)]
    },
    {
        "result": "forged_iron_chain", "count": 2, "station": "work_bench", "category": CRAFT_CAT_BUILDING,
        "ingredients": [("iron_bar", 1)]
    },
    {
        "result": "reinforced_slate_slab", "count": 4, "station": "work_bench", "category": CRAFT_CAT_BUILDING,
        "ingredients": [("stone_block", 4), ("iron_bar", 1)]
    },

    # =========================================================================
    # 4. Work Bench — Workstations, Mechanisms & Decor
    # =========================================================================
    {
        "result": "furnace", "count": 1, "station": "work_bench", "category": CRAFT_CAT_FURNITURE,
        "ingredients": [("stone_block", 20), ("wood", 4), ("torch", 3)]
    },
    {
        "result": "chest", "count": 1, "station": "work_bench", "category": CRAFT_CAT_FURNITURE,
        "ingredients": [("wood", 10)]
    },
    {
        "result": "iron_chest", "count": 1, "station": "work_bench", "category": CRAFT_CAT_FURNITURE,
        "ingredients": [("wood", 8), ("iron_bar", 2)]
    },
    {
        "result": "blight_ember_hearth", "count": 1, "station": "work_bench", "category": CRAFT_CAT_FURNITURE,
        "ingredients": [("blightstone_block", 4), ("wood", 4), ("spud_sap", 3)]
    },
    {
        "result": "smithing_anvil", "count": 1, "station": "work_bench", "category": CRAFT_CAT_FURNITURE,
        "ingredients": [("iron_bar", 12)]
    },
    {
        "result": "whetstone_wheel", "count": 1, "station": "work_bench", "category": CRAFT_CAT_FURNITURE,
        "ingredients": [("stone_block", 6), ("wood", 4), ("iron_bar", 1)]
    },
    {
        "result": "alchemical_retort", "count": 1, "station": "work_bench", "category": CRAFT_CAT_FURNITURE,
        "ingredients": [("iron_bar", 3), ("glass_window", 2), ("torch", 1)]
    },
    {
        "result": "iron_reinforced_door", "count": 1, "station": "work_bench", "category": CRAFT_CAT_FURNITURE,
        "ingredients": [("wood", 6), ("iron_bar", 3)]
    },
    {
        "result": "brass_lantern", "count": 1, "station": "work_bench", "category": CRAFT_CAT_FURNITURE,
        "ingredients": [("copper_bar", 2), ("torch", 1), ("glass_window", 1)]
    },
    {
        "result": "spectral_lantern", "count": 1, "station": "work_bench", "category": CRAFT_CAT_FURNITURE,
        "ingredients": [("iron_bar", 2), ("glowing_mushroom", 2), ("torch", 1)]
    },
    {
        "result": "timber_trapdoor", "count": 2, "station": "work_bench", "category": CRAFT_CAT_FURNITURE,
        "ingredients": [("wood", 6)]
    },
    {
        "result": "hooped_cask", "count": 1, "station": "work_bench", "category": CRAFT_CAT_FURNITURE,
        "ingredients": [("wood", 8), ("copper_bar", 1)]
    },
    {
        "result": "weaver_loom", "count": 1, "station": "work_bench", "category": CRAFT_CAT_FURNITURE,
        "ingredients": [("wood", 6), ("spud_sap", 2)]
    },
    {
        "result": "blast_kiln", "count": 1, "station": "work_bench", "category": CRAFT_CAT_FURNITURE,
        "ingredients": [("stone_brick", 8), ("iron_bar", 4), ("furnace", 1)]
    },
    {
        "result": "smokehouse_stove", "count": 1, "station": "work_bench", "category": CRAFT_CAT_FURNITURE,
        "ingredients": [("furnace", 1), ("wood", 6)]
    },
    {
        "result": "cartographer_desk", "count": 1, "station": "work_bench", "category": CRAFT_CAT_FURNITURE,
        "ingredients": [("wood", 6), ("stone_block", 2)]
    },
    {
        "result": "fletcher_bench", "count": 1, "station": "work_bench", "category": CRAFT_CAT_FURNITURE,
        "ingredients": [("wood", 6), ("spud_sap", 2)]
    },
    {
        "result": "masonry_saw", "count": 1, "station": "work_bench", "category": CRAFT_CAT_FURNITURE,
        "ingredients": [("stone_brick", 4), ("iron_bar", 2)]
    },
    {
        "result": "archery_target", "count": 1, "station": "work_bench", "category": CRAFT_CAT_FURNITURE,
        "ingredients": [("wood", 4), ("spud_sap", 2)]
    },
    {
        "result": "galvanic_attractor", "count": 1, "station": "work_bench", "category": CRAFT_CAT_FURNITURE,
        "ingredients": [("copper_bar", 4)]
    },

    # =========================================================================
    # 5. Work Bench — Tools, Weapons, Armor & Combat Equipment
    # =========================================================================
    {
        "result": "fishing_rod", "count": 1, "station": "work_bench", "category": CRAFT_CAT_EQUIPMENT,
        "ingredients": [("wood", 8), ("spud_sap", 4)]
    },
    {
        "result": "reinforced_angler_rod", "count": 1, "station": "work_bench", "category": CRAFT_CAT_EQUIPMENT,
        "ingredients": [("spud_angler_rod", 1), ("iron_bar", 6), ("silver_coin", 2)]
    },
    {
        "result": "gilded_master_rod", "count": 1, "station": "work_bench", "category": CRAFT_CAT_EQUIPMENT,
        "ingredients": [("reinforced_angler_rod", 1), ("gold_bar", 6), ("golden_fry", 1)]
    },
    {
        "result": "astral_leviathan_rod", "count": 1, "station": "work_bench", "category": CRAFT_CAT_EQUIPMENT,
        "ingredients": [("gilded_master_rod", 1), ("fallen_star", 5), ("portal_shard", 1)]
    },
    {
        "result": "neptune_tide_rod", "count": 1, "station": "work_bench", "category": CRAFT_CAT_EQUIPMENT,
        "ingredients": [("astral_leviathan_rod", 1), ("magma_core", 2), ("crown_of_potaria", 1)]
    },
    {
        "result": "wood_bow", "count": 1, "station": "work_bench", "category": CRAFT_CAT_EQUIPMENT,
        "ingredients": [("wood", 10)]
    },
    {
        "result": "copper_shortsword", "count": 1, "station": "work_bench", "category": CRAFT_CAT_EQUIPMENT,
        "ingredients": [("copper_bar", 5), ("wood", 2)]
    },
    {
        "result": "copper_broadsword", "count": 1, "station": "work_bench", "category": CRAFT_CAT_EQUIPMENT,
        "ingredients": [("copper_bar", 8), ("wood", 2)]
    },
    {
        "result": "copper_axe", "count": 1, "station": "work_bench", "category": CRAFT_CAT_EQUIPMENT,
        "ingredients": [("copper_bar", 6), ("wood", 2)]
    },
    {
        "result": "copper_pickaxe", "count": 1, "station": "work_bench", "category": CRAFT_CAT_EQUIPMENT,
        "ingredients": [("copper_bar", 8), ("wood", 3)]
    },
    {
        "result": "iron_pickaxe", "count": 1, "station": "work_bench", "category": CRAFT_CAT_EQUIPMENT,
        "ingredients": [("iron_bar", 10), ("wood", 3)]
    },
    {
        "result": "iron_axe", "count": 1, "station": "work_bench", "category": CRAFT_CAT_EQUIPMENT,
        "ingredients": [("iron_bar", 8), ("wood", 3)]
    },
    {
        "result": "iron_shovel", "count": 1, "station": "work_bench", "category": CRAFT_CAT_EQUIPMENT,
        "ingredients": [("iron_bar", 4), ("wood", 2)]
    },
    {
        "result": "gold_broadsword", "count": 1, "station": "work_bench", "category": CRAFT_CAT_EQUIPMENT,
        "ingredients": [("gold_bar", 8), ("wood", 2)]
    },
    {
        "result": "gold_pickaxe", "count": 1, "station": "work_bench", "category": CRAFT_CAT_EQUIPMENT,
        "ingredients": [("gold_bar", 10), ("wood", 3)]
    },
    {
        "result": "gold_axe", "count": 1, "station": "work_bench", "category": CRAFT_CAT_EQUIPMENT,
        "ingredients": [("gold_bar", 8), ("wood", 3)]
    },
    {
        "result": "fiber_clippers", "count": 1, "station": "work_bench", "category": CRAFT_CAT_EQUIPMENT,
        "ingredients": [("iron_bar", 2)]
    },
    {
        "result": "oak_buckler", "count": 1, "station": "work_bench", "category": CRAFT_CAT_EQUIPMENT,
        "ingredients": [("wood", 10), ("iron_bar", 1)]
    },
    {
        "result": "iron_aegis", "count": 1, "station": "work_bench", "category": CRAFT_CAT_EQUIPMENT,
        "ingredients": [("iron_bar", 6), ("wood", 4)]
    },
    {
        "result": "arbalest_repeater", "count": 1, "station": "work_bench", "category": CRAFT_CAT_EQUIPMENT,
        "ingredients": [("iron_bar", 6), ("wood", 8), ("spud_sap", 3)]
    },
    {
        "result": "glowing_lumen_arrow", "count": 25, "station": "work_bench", "category": CRAFT_CAT_EQUIPMENT,
        "ingredients": [("wooden_arrow", 25), ("glowing_mushroom", 1)]
    },
    {
        "result": "spud_quiver", "count": 1, "station": "work_bench", "category": CRAFT_CAT_EQUIPMENT,
        "ingredients": [("wood", 4), ("spud_sap", 4), ("copper_bar", 1)]
    },
    {
        "result": "totem_of_resurgence", "count": 1, "station": "work_bench", "category": CRAFT_CAT_EQUIPMENT,
        "ingredients": [("gold_bar", 8), ("portal_shard", 2), ("fallen_star", 2)]
    },
    {
        "result": "bone_bow", "count": 1, "station": "work_bench", "category": CRAFT_CAT_EQUIPMENT,
        "ingredients": [("bone", 12), ("spud_sap", 4)]
    },
    {
        "result": "frostburn_arrow", "count": 25, "station": "work_bench", "category": CRAFT_CAT_EQUIPMENT,
        "ingredients": [("wooden_arrow", 25), ("frost_core", 1)]
    },
    {
        "result": "flame_arrow", "count": 25, "station": "work_bench", "category": CRAFT_CAT_EQUIPMENT,
        "ingredients": [("wooden_arrow", 25), ("torch", 1)]
    },
    {
        "result": "astral_arrow", "count": 25, "station": "work_bench", "category": CRAFT_CAT_EQUIPMENT,
        "ingredients": [("wooden_arrow", 25), ("fallen_star", 1)]
    },
    {
        "result": "starch_blade", "count": 1, "station": "work_bench", "category": CRAFT_CAT_EQUIPMENT,
        "ingredients": [("gold_bar", 8), ("raw_potato", 4), ("spud_sap", 6)]
    },
    {
        "result": "cactus_sword", "count": 1, "station": "work_bench", "category": CRAFT_CAT_EQUIPMENT,
        "ingredients": [("cactus", 10)]
    },
    {
        "result": "cactus_helmet", "count": 1, "station": "work_bench", "category": CRAFT_CAT_EQUIPMENT,
        "ingredients": [("cactus", 8)]
    },
    {
        "result": "cactus_chestplate", "count": 1, "station": "work_bench", "category": CRAFT_CAT_EQUIPMENT,
        "ingredients": [("cactus", 12)]
    },
    {
        "result": "cactus_greaves", "count": 1, "station": "work_bench", "category": CRAFT_CAT_EQUIPMENT,
        "ingredients": [("cactus", 10)]
    },
    {
        "result": "celestial_axe", "count": 1, "station": "work_bench", "category": CRAFT_CAT_EQUIPMENT,
        "ingredients": [("celestial_essence", 1), ("gold_bar", 8), ("wood", 5)]
    },
    {
        "result": "celestial_pickaxe", "count": 1, "station": "work_bench", "category": CRAFT_CAT_EQUIPMENT,
        "ingredients": [("celestial_essence", 1), ("gold_bar", 10), ("wood", 5)]
    },
    {
        "result": "magma_greatsword", "count": 1, "station": "work_bench", "category": CRAFT_CAT_EQUIPMENT,
        "ingredients": [("magma_core", 1), ("gold_bar", 8)]
    },
    {
        "result": "magma_chestplate", "count": 1, "station": "work_bench", "category": CRAFT_CAT_EQUIPMENT,
        "ingredients": [("magma_core", 2), ("iron_bar", 10)]
    },
    {
        "result": "cryo_chestplate", "count": 1, "station": "work_bench", "category": CRAFT_CAT_EQUIPMENT,
        "ingredients": [("frost_core", 3), ("iron_bar", 10)]
    },
    {
        "result": "bone_scythe", "count": 1, "station": "work_bench", "category": CRAFT_CAT_EQUIPMENT,
        "ingredients": [("bone", 16), ("iron_bar", 6)]
    },
    {
        "result": "titans_ring", "count": 1, "station": "work_bench", "category": CRAFT_CAT_EQUIPMENT,
        "ingredients": [("celestial_essence", 1), ("gold_bar", 6)]
    },

    # =========================================================================
    # 6. Work Bench — Survival Gear, Runes, Potions & Utilities
    # =========================================================================
    {
        "result": "affix_stone", "count": 1, "station": "work_bench", "category": CRAFT_CAT_SURVIVAL,
        "ingredients": [("portal_shard", 3), ("gold_bar", 5), ("blightstone", 5)]
    },
    {
        "result": "greater_healing_potion", "count": 1, "station": "work_bench", "category": CRAFT_CAT_SURVIVAL,
        "ingredients": [("healing_potion", 2), ("glowing_mushroom", 1)]
    },
    {
        "result": "speed_potion", "count": 1, "station": "work_bench", "category": CRAFT_CAT_SURVIVAL,
        "ingredients": [("raw_potato", 1), ("spud_sap", 2)]
    },
    {
        "result": "night_gazer_elixir", "count": 1, "station": "work_bench", "category": CRAFT_CAT_SURVIVAL,
        "ingredients": [("spud_sap", 2), ("glowing_mushroom", 2), ("fallen_star", 1)]
    },
    {
        "result": "zephyr_tonic", "count": 1, "station": "work_bench", "category": CRAFT_CAT_SURVIVAL,
        "ingredients": [("raw_potato", 2), ("copper_bar", 1), ("spud_sap", 2)]
    },
    {
        "result": "explorers_satchel", "count": 1, "station": "work_bench", "category": CRAFT_CAT_SURVIVAL,
        "ingredients": [("spud_sap", 6), ("wood", 4)]
    },
    {
        "result": "magnetic_lodestone", "count": 1, "station": "work_bench", "category": CRAFT_CAT_SURVIVAL,
        "ingredients": [("iron_bar", 4), ("spud_sap", 2)]
    },
    {
        "result": "brass_far_seer", "count": 1, "station": "work_bench", "category": CRAFT_CAT_SURVIVAL,
        "ingredients": [("copper_bar", 3), ("glass_window", 1)]
    },
    {
        "result": "solar_chronometer", "count": 1, "station": "work_bench", "category": CRAFT_CAT_SURVIVAL,
        "ingredients": [("gold_bar", 4), ("spud_sap", 1)]
    },
    {
        "result": "dungeon_rune", "count": 1, "station": "work_bench", "category": CRAFT_CAT_SURVIVAL,
        "ingredients": [("gold_bar", 4), ("spud_sap", 5), ("stone_brick", 6)]
    },
    {
        "result": "desert_rune", "count": 1, "station": "work_bench", "category": CRAFT_CAT_SURVIVAL,
        "ingredients": [("cactus", 6), ("sandstone_block", 8), ("gold_bar", 2)]
    },
    {
        "result": "cryo_rune", "count": 1, "station": "work_bench", "category": CRAFT_CAT_SURVIVAL,
        "ingredients": [("frost_core", 2), ("ice_block", 10), ("iron_bar", 4)]
    },
    {
        "result": "necro_rune", "count": 1, "station": "work_bench", "category": CRAFT_CAT_SURVIVAL,
        "ingredients": [("bone", 8), ("blightstone_block", 10), ("gold_bar", 2)]
    },
    {
        "result": "celestial_keystone", "count": 1, "station": "work_bench", "category": CRAFT_CAT_SURVIVAL,
        "ingredients": [("portal_shard", 4), ("gold_bar", 5), ("stone_brick", 10)]
    },
]


def load_craftable_recipes():
    """Loads categorized crafting recipes from data/crafting/craftable_items.json if present,
    falling back safely to hardcoded RECIPES."""
    import os, json
    json_path = os.path.join("data", "crafting", "craftable_items.json")
    if os.path.exists(json_path):
        try:
            with open(json_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            loaded = []
            for item in data.get("craftable_items", []):
                loaded.append({
                    "result": item["id"],
                    "count": item.get("count", 1),
                    "station": item.get("station"),
                    "category": item.get("category", CRAFT_CAT_ALL),
                    "ingredients": [(ing["item"], ing["count"]) for ing in item.get("ingredients", [])]
                })
            if loaded:
                existing_results = {r.get("result") for r in loaded}
                for r in RECIPES:
                    if r.get("result") not in existing_results:
                        loaded.append(r)
                return loaded
        except Exception as e:
            print(f"[Crafting ERROR] Failed to load {json_path}: {e}")
    return RECIPES


class CraftingSystem:
    def __init__(self, asset_factory, sound_manager):
        self.asset_factory = asset_factory
        self.sound_manager = sound_manager
        self.recipes = load_craftable_recipes()
        self.available_recipes = []
        self.selected_category = CRAFT_CAT_ALL
        self.scroll_row = 0
        self.cols = 10
        self.visible_rows = 8
        self.near_workbench = False
        self.near_furnace = False
        self.last_inventory = None
        self.last_crafted_item = None
        self.tab_rects = {}
        self.scroll_up_rect = pygame.Rect(390, 276, 22, 18)
        self.scroll_down_rect = pygame.Rect(416, 276, 22, 18)
        self._init_tab_rects()

    def _init_tab_rects(self):
        """Initializes exact screen bounding rectangles for all category tabs."""
        start_x = 20
        tabs_y = 252
        tab_h = 22
        widths = {
            CRAFT_CAT_ALL: 48,
            CRAFT_CAT_BUILDING: 84,
            CRAFT_CAT_EQUIPMENT: 92,
            CRAFT_CAT_SURVIVAL: 86,
            CRAFT_CAT_FURNITURE: 90,
        }
        curr_x = start_x
        self.tab_rects = {}
        for tab in CRAFT_TABS:
            tid = tab["id"]
            w = widths.get(tid, 80)
            self.tab_rects[tid] = pygame.Rect(curr_x, tabs_y, w, tab_h)
            curr_x += w + 4

    def get_panel_rect(self):
        """Returns the full interactive panel Rect encompassing crafting header, tabs, and grid."""
        return pygame.Rect(16, 226, 444, 480)

    def set_category(self, cat_id):
        """Sets the active category filter tab and resets scroll position."""
        cat = str(cat_id).strip().lower()
        if "surviv" in cat:
            self.selected_category = CRAFT_CAT_SURVIVAL
        elif "furnit" in cat or "mech" in cat:
            self.selected_category = CRAFT_CAT_FURNITURE
        elif "build" in cat:
            self.selected_category = CRAFT_CAT_BUILDING
        elif "equip" in cat:
            self.selected_category = CRAFT_CAT_EQUIPMENT
        else:
            self.selected_category = CRAFT_CAT_ALL
        self.scroll_row = 0

    def handle_scroll(self, scroll_y):
        """Smoothly scrolls the recipe grid up (scroll_y > 0) or down (scroll_y < 0)."""
        filtered = self.filtered_recipes
        max_rows = (len(filtered) + self.cols - 1) // self.cols
        max_scroll = max(0, max_rows - self.visible_rows)
        self.scroll_row = max(0, min(max_scroll, self.scroll_row - scroll_y))

    @property
    def filtered_recipes(self):
        """Returns recipes filtered by the active category tab."""
        if self.selected_category == CRAFT_CAT_ALL or not self.selected_category:
            return self.available_recipes
        return [r for r in self.available_recipes if r.get("category") == self.selected_category]

    def get_filtered_recipes(self, category=None):
        """Explicit getter for filtered recipes supporting loose category strings."""
        cat = (category or self.selected_category or CRAFT_CAT_ALL).lower()
        if "surviv" in cat:
            cat = CRAFT_CAT_SURVIVAL
        elif "furnit" in cat or "mech" in cat:
            cat = CRAFT_CAT_FURNITURE
        elif "build" in cat:
            cat = CRAFT_CAT_BUILDING
        elif "equip" in cat:
            cat = CRAFT_CAT_EQUIPMENT
        elif "all" in cat:
            cat = CRAFT_CAT_ALL

        if cat == CRAFT_CAT_ALL:
            return self.available_recipes
        return [r for r in self.available_recipes if r.get("category") == cat]

    def check_nearby_stations(self, world, player):
        """Checks if Spud is within physical range (within 2.5 tiles) of a placed Work Bench or Furnace."""
        ptx = int(player.center_x // SCALED_TILE)
        pty = int(player.center_y // SCALED_TILE)
        has_workbench = False
        has_furnace = False

        for dx in range(-4, 5):
            for dy in range(-4, 5):
                dist = math.hypot(dx, dy)
                t_id = world.get_tile(ptx + dx, pty + dy)
                if t_id == TILE_WORK_BENCH and dist <= 2.5:
                    has_workbench = True
                elif t_id == TILE_FURNACE and dist <= 2.5:
                    has_furnace = True

        self.near_workbench = has_workbench
        self.near_furnace = has_furnace
        return has_workbench, has_furnace

    def _infer_recipe_category(self, result_id):
        """Infers category for any recipe lacking an explicit category tag."""
        res_data = ITEM_REGISTRY.get(result_id, {})
        cat = res_data.get("cat", "")
        if cat in ("tool", "weapon", "accessory") or cat.startswith("armor_"):
            return CRAFT_CAT_EQUIPMENT
        if cat in ("consumable", "material", "currency", "special"):
            return CRAFT_CAT_SURVIVAL
        if cat == "wall" or any(w in result_id for w in ("brick", "block", "platform", "planks", "tiles", "wall", "rung", "scaffold", "parapet", "palisade", "shingle", "slab")):
            return CRAFT_CAT_BUILDING
        return CRAFT_CAT_FURNITURE

    def update_recipes(self, inventory, world, player):
        self.last_inventory = inventory
        has_wb, has_furn = self.check_nearby_stations(world, player)

        station_recipes = []
        recipe_source = getattr(self, "recipes", None) or RECIPES
        for r in recipe_source:
            req_station = r["station"]
            if isinstance(req_station, (list, tuple)):
                if not any((st == "work_bench" and has_wb) or (st == "furnace" and has_furn) or (st is None) for st in req_station):
                    continue
            elif req_station == "work_bench" and not has_wb:
                continue
            elif req_station == "furnace" and not has_furn:
                continue

            can_craft = True
            for item_id, count in r["ingredients"]:
                if inventory.count_item(item_id) < count:
                    can_craft = False
                    break

            recipe_entry = dict(r)
            recipe_entry["can_craft"] = can_craft
            if "category" not in recipe_entry:
                recipe_entry["category"] = self._infer_recipe_category(r["result"])
            station_recipes.append(recipe_entry)

        # Sort so craftable recipes appear first, followed by uncraftable station unlocks
        station_recipes.sort(key=lambda r: (not r["can_craft"]))
        self.available_recipes = station_recipes

        # Clamp scroll row in case recipes count shrunk
        filtered = self.filtered_recipes
        max_rows = (len(filtered) + self.cols - 1) // self.cols
        max_scroll = max(0, max_rows - self.visible_rows)
        self.scroll_row = max(0, min(max_scroll, self.scroll_row))

    def craft(self, recipe, inventory):
        for item_id, count in recipe["ingredients"]:
            if inventory.count_item(item_id) < count:
                return False

        for item_id, count in recipe["ingredients"]:
            inventory.remove_item(item_id, count)

        inventory.add_item(recipe["result"], recipe["count"])
        self.sound_manager.play("craft")
        return True

    def handle_click(self, mouse_x, mouse_y, inventory):
        # 1. Check Category Tabs
        for tab_id, rect in self.tab_rects.items():
            if rect.collidepoint(mouse_x, mouse_y):
                if self.selected_category != tab_id:
                    self.set_category(tab_id)
                    self.sound_manager.play("place")
                return True

        # 2. Check Scroll Buttons
        if self.scroll_up_rect and self.scroll_up_rect.collidepoint(mouse_x, mouse_y):
            if self.scroll_row > 0:
                self.scroll_row -= 1
                self.sound_manager.play("place")
            return True

        if self.scroll_down_rect and self.scroll_down_rect.collidepoint(mouse_x, mouse_y):
            filtered = self.filtered_recipes
            max_rows = (len(filtered) + self.cols - 1) // self.cols
            max_scroll = max(0, max_rows - self.visible_rows)
            if self.scroll_row < max_scroll:
                self.scroll_row += 1
                self.sound_manager.play("place")
            return True

        # 3. Check Visible Recipe Slots in Grid
        start_x = 20
        grid_start_y = 298
        icon_size = 36
        padding = 6
        step = icon_size + padding

        filtered = self.filtered_recipes
        start_idx = self.scroll_row * self.cols
        visible_recipes = filtered[start_idx : start_idx + self.cols * self.visible_rows]

        for i, recipe in enumerate(visible_recipes):
            rx = start_x + (i % self.cols) * step
            ry = grid_start_y + (i // self.cols) * step
            rect = pygame.Rect(rx, ry, icon_size, icon_size)

            if rect.collidepoint(mouse_x, mouse_y):
                if recipe.get("can_craft", True):
                    if self.craft(recipe, inventory):
                        self.last_crafted_item = recipe.get("result")
                else:
                    self.sound_manager.play("hit")
                return True
        return False

    def render(self, target_surf, mouse_x, mouse_y, font):
        start_x = 20
        header_y = 230
        tabs_y = 252
        subheader_y = 277
        grid_start_y = 298
        icon_size = 36
        padding = 6
        step = icon_size + padding

        # 1. Crafting Header & Station Proximity Badges
        t_surf = font.render("Crafting Recipes:", True, (255, 230, 100))
        target_surf.blit(t_surf, (start_x, header_y))

        badge_x = start_x + t_surf.get_width() + 8
        if self.near_workbench:
            wb_surf = font.render("[Near Work Bench]", True, (80, 240, 120))
            target_surf.blit(wb_surf, (badge_x, header_y))
            badge_x += wb_surf.get_width() + 6
        if self.near_furnace:
            fn_surf = font.render("[Near Furnace]", True, (255, 170, 60))
            target_surf.blit(fn_surf, (badge_x, header_y))
            badge_x += fn_surf.get_width() + 6
        if not self.near_workbench and not self.near_furnace:
            h_surf = font.render("[By Hand]", True, (170, 185, 205))
            target_surf.blit(h_surf, (badge_x, header_y))

        # 2. Category Filter Tabs (Minecraft-Style)
        hovered_tab = None
        for tab in CRAFT_TABS:
            tid = tab["id"]
            rect = self.tab_rects.get(tid)
            if not rect:
                continue

            is_active = (self.selected_category == tid)
            is_hover = rect.collidepoint(mouse_x, mouse_y)
            if is_hover:
                hovered_tab = tab

            # Tab Background
            if is_active:
                tab_bg = (52, 70, 108, 240)
            elif is_hover:
                tab_bg = (42, 50, 74, 230)
            else:
                tab_bg = (24, 28, 42, 210)

            # Tab Border
            if is_active:
                tab_border = (255, 215, 60)
                border_w = 2
            elif is_hover:
                tab_border = (140, 185, 240)
                border_w = 1
            else:
                tab_border = (65, 75, 95)
                border_w = 1

            pygame.draw.rect(target_surf, tab_bg, rect, border_radius=4)
            pygame.draw.rect(target_surf, tab_border, rect, border_w, border_radius=4)

            # Active Gold Underline Indicator
            if is_active:
                pygame.draw.line(target_surf, (255, 220, 80), (rect.x + 4, rect.bottom - 2), (rect.right - 4, rect.bottom - 2), 2)

            # Label Text
            txt_color = (255, 240, 140) if is_active else ((255, 255, 255) if is_hover else (170, 180, 200))
            lbl_surf = font.render(tab["label"], True, txt_color)
            target_surf.blit(lbl_surf, (rect.centerx - lbl_surf.get_width() // 2, rect.centery - lbl_surf.get_height() // 2))

        # 3. Subheader: Active Category Title & Counts & Scroll Controls
        filtered = self.filtered_recipes
        active_tab_info = next((t for t in CRAFT_TABS if t["id"] == self.selected_category), CRAFT_TABS[0])
        total_in_cat = len(filtered)
        craftable_in_cat = sum(1 for r in filtered if r.get("can_craft", True))

        info_str = f"[{active_tab_info['full_name']}] • {total_in_cat} Available ({craftable_in_cat} Craftable)"
        info_surf = font.render(info_str, True, (210, 220, 235))
        target_surf.blit(info_surf, (start_x, subheader_y))

        # Scroll controls
        max_rows = (total_in_cat + self.cols - 1) // self.cols
        max_scroll = max(0, max_rows - self.visible_rows)

        if max_scroll > 0:
            pg_str = f"Row {self.scroll_row + 1}-{min(max_rows, self.scroll_row + self.visible_rows)}/{max_rows}"
            pg_surf = font.render(pg_str, True, (160, 175, 195))
            target_surf.blit(pg_surf, (300, subheader_y))

            # Scroll Up Button [▲]
            up_hover = self.scroll_up_rect.collidepoint(mouse_x, mouse_y)
            up_bg = (60, 75, 110) if up_hover else (35, 42, 60)
            pygame.draw.rect(target_surf, up_bg, self.scroll_up_rect, border_radius=3)
            pygame.draw.rect(target_surf, (255, 215, 80) if up_hover else (90, 105, 135), self.scroll_up_rect, 1, border_radius=3)
            up_arrow = font.render("▲", True, (255, 255, 255) if up_hover else (180, 190, 205))
            target_surf.blit(up_arrow, (self.scroll_up_rect.centerx - up_arrow.get_width() // 2, self.scroll_up_rect.centery - up_arrow.get_height() // 2))

            # Scroll Down Button [▼]
            dn_hover = self.scroll_down_rect.collidepoint(mouse_x, mouse_y)
            dn_bg = (60, 75, 110) if dn_hover else (35, 42, 60)
            pygame.draw.rect(target_surf, dn_bg, self.scroll_down_rect, border_radius=3)
            pygame.draw.rect(target_surf, (255, 215, 80) if dn_hover else (90, 105, 135), self.scroll_down_rect, 1, border_radius=3)
            dn_arrow = font.render("▼", True, (255, 255, 255) if dn_hover else (180, 190, 205))
            target_surf.blit(dn_arrow, (self.scroll_down_rect.centerx - dn_arrow.get_width() // 2, self.scroll_down_rect.centery - dn_arrow.get_height() // 2))

        # 4. Recipe Grid
        if not filtered:
            no_txt = font.render("No recipes in this category with current station.", True, (160, 170, 190))
            target_surf.blit(no_txt, (start_x, grid_start_y + 8))
            return

        hovered_recipe = None
        start_idx = self.scroll_row * self.cols
        visible_recipes = filtered[start_idx : start_idx + self.cols * self.visible_rows]

        for i, recipe in enumerate(visible_recipes):
            rx = start_x + (i % self.cols) * step
            ry = grid_start_y + (i // self.cols) * step
            rect = pygame.Rect(rx, ry, icon_size, icon_size)

            can_craft = recipe.get("can_craft", True)
            bg_color = (30, 36, 52, 225) if can_craft else (20, 22, 32, 240)
            pygame.draw.rect(target_surf, bg_color, rect, border_radius=3)
            border_color = (95, 110, 145) if can_craft else (55, 60, 75)
            pygame.draw.rect(target_surf, border_color, rect, 1, border_radius=3)

            res_id = recipe["result"]
            icon = self.asset_factory.items.get(res_id)
            if icon:
                if not can_craft:
                    dimmed = icon.copy()
                    dim_overlay = pygame.Surface(dimmed.get_size(), pygame.SRCALPHA)
                    dim_overlay.fill((0, 0, 0, 130))
                    dimmed.blit(dim_overlay, (0, 0))
                    target_surf.blit(dimmed, (rx + 6, ry + 6))
                else:
                    target_surf.blit(icon, (rx + 6, ry + 6))

            if recipe["count"] > 1:
                cnt_txt = font.render(str(recipe["count"]), True, (255, 255, 255) if can_craft else (140, 140, 140))
                target_surf.blit(cnt_txt, (rx + icon_size - cnt_txt.get_width() - 3, ry + icon_size - cnt_txt.get_height() - 2))

            if rect.collidepoint(mouse_x, mouse_y):
                pygame.draw.rect(target_surf, (255, 230, 80) if can_craft else (200, 90, 90), rect, 2, border_radius=3)
                hovered_recipe = recipe

        # 5. Tooltips
        if hovered_recipe:
            self._render_recipe_tooltip(target_surf, mouse_x, mouse_y, hovered_recipe, font)
        elif hovered_tab:
            self._render_tab_tooltip(target_surf, mouse_x, mouse_y, hovered_tab, font)

    def _render_tab_tooltip(self, target_surf, mx, my, tab, font):
        """Displays tooltip describing category tab filter contents."""
        lines = [
            (tab["full_name"], (255, 225, 90)),
            (tab["tooltip"], (200, 220, 240)),
            (f"Click to filter [{tab['label']}]", (120, 215, 255)),
        ]
        line_surfs = [font.render(text, True, color) for text, color in lines]
        tip_w = max(s.get_width() for s in line_surfs) + 16
        tip_h = len(line_surfs) * 18 + 10

        tip_x = min(target_surf.get_width() - tip_w - 10, mx + 16)
        tip_y = min(target_surf.get_height() - tip_h - 10, my + 16)

        tip_rect = pygame.Rect(tip_x, tip_y, tip_w, tip_h)
        pygame.draw.rect(target_surf, (20, 24, 38, 245), tip_rect, border_radius=6)
        pygame.draw.rect(target_surf, (255, 215, 60), tip_rect, 1, border_radius=6)

        for i, s in enumerate(line_surfs):
            target_surf.blit(s, (tip_x + 8, tip_y + 5 + i * 18))

    def _render_recipe_tooltip(self, target_surf, mx, my, recipe, font):
        res_data = ITEM_REGISTRY.get(recipe["result"], {})
        name = res_data.get("name", recipe["result"])
        count_suffix = f" (x{recipe['count']})" if recipe["count"] > 1 else ""
        rarity = res_data.get("rarity", RARITY_COMMON)
        r_color = RARITY_COLORS.get(rarity, (255, 255, 255))
        can_craft = recipe.get("can_craft", True)
        category_name = recipe.get("category", CRAFT_CAT_ALL).title()

        lines = [(f"{name}{count_suffix}", r_color)]

        # Category and Station info
        lines.append((f"Category: {category_name}", (140, 210, 255)))

        st_text = "Station: By Hand"
        if recipe["station"] == "work_bench":
            st_text = "Station: Work Bench Required"
        elif recipe["station"] == "furnace":
            st_text = "Station: Furnace Required"
        lines.append((st_text, (255, 215, 100)))

        # Description
        desc = res_data.get("desc")
        if desc:
            lines.append((desc, (200, 215, 235)))

        lines.append(("Ingredients:", (220, 220, 220)))
        for iname, icnt in recipe["ingredients"]:
            ing_data = ITEM_REGISTRY.get(iname, {})
            in_title = ing_data.get("name", iname)
            owned = self.last_inventory.count_item(iname) if self.last_inventory else 0
            if owned >= icnt:
                lines.append((f"  • {in_title}: {owned} / {icnt}", (140, 240, 140)))
            else:
                needed = icnt - owned
                lines.append((f"  • {in_title}: {owned} / {icnt} (Need {needed})", (255, 100, 100)))

        if can_craft:
            lines.append(("[Click to Craft]", (100, 220, 255)))
        else:
            lines.append(("[Missing Ingredients]", (240, 80, 80)))

        line_surfs = [font.render(text, True, color) for text, color in lines]
        tip_w = max(s.get_width() for s in line_surfs) + 18
        tip_h = len(line_surfs) * 18 + 12

        tip_x = min(target_surf.get_width() - tip_w - 10, mx + 16)
        tip_y = min(target_surf.get_height() - tip_h - 10, my + 16)

        tip_rect = pygame.Rect(tip_x, tip_y, tip_w, tip_h)
        pygame.draw.rect(target_surf, (20, 24, 38, 245), tip_rect, border_radius=6)
        pygame.draw.rect(target_surf, r_color, tip_rect, 1, border_radius=6)

        for i, s in enumerate(line_surfs):
            target_surf.blit(s, (tip_x + 9, tip_y + 6 + i * 18))
