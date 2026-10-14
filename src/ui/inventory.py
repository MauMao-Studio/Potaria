"""
Potaria - Inventory & Item System (Chroisen Style)
Manages 10-slot hotbar, 40-slot backpack, paperdoll equip handling,
armor pieces, and Skill Books.
Developer: Kurados
"""

import os
import json
import pygame
from src.constants import (
    SCREEN_WIDTH, SCREEN_HEIGHT,
    HOTBAR_SLOTS, INV_COLS, INV_ROWS, INV_TOTAL_SLOTS,
    SLOT_SIZE, SLOT_PADDING, CAT_TOOL, CAT_WEAPON, CAT_BLOCK, CAT_WALL,
    CAT_MATERIAL, CAT_CONSUMABLE, CAT_SPECIAL, CAT_ACCESSORY, CAT_CURRENCY,
    TILE_AIR, TILE_DIRT, TILE_GRASS, TILE_STONE, TILE_WOOD, TILE_LEAVES, TILE_WOOD_TRUNK,
    TILE_COPPER_ORE, TILE_IRON_ORE, TILE_GOLD_ORE, TILE_DUNGEON_ALTAR,
    TILE_TORCH, TILE_WOOD_PLATFORM,
    TILE_WORK_BENCH, TILE_FURNACE, TILE_STONE_BRICK, TILE_DUNGEON_BRICK,
    TILE_SAND, TILE_SANDSTONE, TILE_CACTUS, TILE_SNOW, TILE_ICE,
    TILE_CORRUPT_GRASS, TILE_EBONSTONE, TILE_BLIGHT_GRASS, TILE_BLIGHTSTONE,
    TILE_MUSHROOM_GRASS, TILE_MUSHROOM_STEM, TILE_MUSHROOM_CAP, TILE_CHEST,
    TILE_ROOF_TILES, TILE_WOOD_PLANKS, TILE_GLASS, TILE_DOOR_CLOSED, TILE_DOOR_OPEN,
    TILE_TABLE, TILE_CHAIR,
    TILE_BED, TILE_BOOKSHELF, TILE_GRANDFATHER_CLOCK, TILE_FIREPLACE,
    TILE_CANDELABRA, TILE_CHANDELIER, TILE_POTTED_PLANT, TILE_DRESSER,
    TILE_TAPESTRY, TILE_BATHTUB, TILE_SINK, TILE_PAINTING, TILE_WOOD_SHELF,
    TILE_CARVED_TUBER_LANTERN, TILE_BRASS_LANTERN, TILE_SPECTRAL_LANTERN, TILE_LAMP,
    TILE_SAPLING, TILE_IRON_CHEST, TILE_ROPE_RUNGS,
    WALL_WOOD, WALL_STONE_BRICK, WALL_GLASS,
    RARITY_COMMON, RARITY_UNCOMMON, RARITY_RARE, RARITY_EPIC,
    RARITY_MYTHIC, RARITY_LEGENDARY, RARITY_ANCIENT, RARITY_HEX_COLORS, RARITY_COLORS
)

# Backwards compatibility and anti-plagiarism alias mapping
ITEM_ALIASES = {
    "treasure_chest": "chest",
    "leaf_block": "leaves",
    "sapling": "oak_sapling",
    "tree_sapling": "oak_sapling",
    "palm_tree_sapling": "palm_sapling",
    "pine_tree_sapling": "pine_sapling",
    "blight_tree_sapling": "blight_sapling",
    "iron_storage_chest": "iron_chest",
    "starfury": "astral_wrath",
    "hermes_boots": "zephyr_striders",
    "gel": "spud_sap",
    "mana_flower": "arcane_orchid",
    "band_of_regeneration": "talisman_of_vigor",
    "ebonstone_block": "blightstone_block",
    "corrupt_grass": "blight_grass",
    "bed": "wooden_bed",
    "fireplace": "stone_fireplace",
    "hearth": "stone_fireplace",
    "dresser": "wooden_dresser",
    "wardrobe": "wooden_dresser",
    "tapestry": "wall_tapestry",
    "banner": "wall_tapestry",
    "clock": "grandfather_clock",
    "plant": "potted_plant",
    "potted_spud_plant": "potted_plant",
    "bonsai": "potted_plant",
    "shelf": "wood_shelf",
    "art": "painting",
    "wall_art": "painting",
    "stone": "stone_block",
    "wood_sword": "wooden_sword",
    "wood_block": "wood",
    "wood_blocks": "wood",
    "celestial_shard": "portal_shard",
    "celestial_shards": "portal_shard",
    "portal_shards": "portal_shard",
    "curved_tuber_lantern": "carved_tuber_lantern",
    "celestial_fragment": "portal_shard",
    "celestial_fragments": "portal_shard",
    "dirt": "dirt_block",
    "tile_wood": "wood",
    "arrow": "wooden_arrow",
    "iron_sword": "iron_broadsword",
    "star": "fallen_star",
    "falling_star": "fallen_star",
    "wooden_chest": "chest",
    "lamp": "brass_lamp",
    # Seven Deadly Sins aliases
    "cinderheart_cuirass": "wrath_cuirass",
    "wrathbound_visage": "wrath_helm",
    "ashen_grips": "wrath_greatsword",
    "ravager_greaves": "wrath_greaves",
    "oath_of_the_last_spark": "wrath_brand",
    "crown_of_the_unbowed": "pride_crown",
    "sunlit_regalia": "pride_robe",
    "highstep_greaves": "pride_boots",
    "sovereign_gauntlets": "pride_blade",
    "mirror_of_supremacy": "pride_ring",
    # Seven Heavenly Virtues aliases
    "vigilant_circlet": "patience_circlet",
    "longwatch_mantle": "patience_mantle",
    "measured_hands": "patience_hands",
    "pilgrim_greaves": "patience_greaves",
    "pilgrims_greaves": "patience_greaves",
    "bell_of_the_last_hour": "patience_bell",
    # Filipino Equipment aliases
    "bolo": "katipunero_bolo",
    "itak": "katipunero_bolo",
    "barong": "barong_tagalog",
    "hat_salakot": "salakot",
    "knife_balisong": "balisong",
    "sword_kampilan": "kampilan",
    "shoes_bakya": "bakya",
    "sword_tabak": "tabak",
}
REVERSE_ITEM_ALIASES = {v: k for k, v in ITEM_ALIASES.items()}


ITEM_REGISTRY = {
    # ----------------------------------------------------
    # Tools & Weapons
    # ----------------------------------------------------
    "copper_pickaxe": {
        "name": "Copper Pickaxe", "cat": CAT_TOOL, "power": 12, "damage": 3, "max_stack": 1, "tile": None,
        "rarity": RARITY_COMMON,
        "desc": "Starter mining tool. Digs through dirt, clay, and soft copper veins.",
        "lore": "",
        "special": ""
    },
    "iron_pickaxe": {
        "name": "Iron Pickaxe", "cat": CAT_TOOL, "power": 18, "damage": 4, "max_stack": 1, "tile": None,
        "rarity": RARITY_UNCOMMON,
        "desc": "Tempered iron head that swiftly breaks through dense stone and minerals.",
        "lore": "",
        "special": ""
    },
    "gold_pickaxe": {
        "name": "Gold Pickaxe", "cat": CAT_TOOL, "power": 28, "damage": 5, "max_stack": 1, "tile": None,
        "rarity": RARITY_RARE,
        "desc": "Lustrous gilded pickaxe boasting exceptional digging speed.",
        "lore": "",
        "special": ""
    },
    "wood_pickaxe": {
        "name": "Wooden Pickaxe", "cat": CAT_TOOL, "power": 8, "damage": 2, "max_stack": 1, "tile": None,
        "rarity": RARITY_COMMON,
        "desc": "Crude wooden pick. Slowly chips through soft earth and stone.",
        "lore": "",
        "special": ""
    },
    "wood_axe": {
        "name": "Wooden Axe", "cat": CAT_TOOL, "power": 10, "damage": 2, "max_stack": 1, "tile": None,
        "rarity": RARITY_COMMON,
        "desc": "A basic axe carved from raw timber. Chops down trees.",
        "lore": "",
        "special": ""
    },
    "copper_axe": {
        "name": "Copper Axe", "cat": CAT_TOOL, "power": 18, "damage": 3, "max_stack": 1, "tile": None,
        "rarity": RARITY_COMMON,
        "desc": "Sturdy forged copper axe head. Efficient woodcutter.",
        "lore": "",
        "special": ""
    },
    "iron_axe": {
        "name": "Iron Axe", "cat": CAT_TOOL, "power": 26, "damage": 4, "max_stack": 1, "tile": None,
        "rarity": RARITY_UNCOMMON,
        "desc": "Hardened iron lumber axe. Swiftly fells towering trees and dense trunks.",
        "lore": "",
        "special": ""
    },
    "gold_axe": {
        "name": "Gold Axe", "cat": CAT_TOOL, "power": 38, "damage": 5, "max_stack": 1, "tile": None,
        "rarity": RARITY_RARE,
        "desc": "Lustrous gold axe with unmatched cutting velocity. Cleaves wood in seconds.",
        "lore": "",
        "special": ""
    },
    "celestial_axe": {
        "name": "Celestial Axe", "cat": CAT_TOOL, "power": 65, "damage": 8, "max_stack": 1, "tile": None,
        "rarity": RARITY_LEGENDARY,
        "desc": "Star-forged battle axe. Instantly annihilates ancient trees and dense timber.",
        "lore": "'Sundered stars woven into a lumberjack's dream.'",
        "special": "Godly Woodcutting Speed"
    },
    "celestial_pickaxe": {
        "name": "Celestial Pickaxe", "cat": CAT_TOOL, "power": 65, "damage": 7, "max_stack": 1, "tile": None,
        "rarity": RARITY_LEGENDARY,
        "desc": "Starlight mining pickaxe. Effortlessly shreds subterranean bedrock and gems.",
        "lore": "'The cosmos parts before its crystalline tip.'",
        "special": "Subterranean Laser Digging Speed"
    },
    "wood_shovel": {
        "name": "Wooden Shovel", "cat": CAT_TOOL, "power": 10, "damage": 2, "max_stack": 1, "tile": None,
        "rarity": RARITY_COMMON,
        "desc": "Wooden scoop tool for swiftly excavating soft dirt and sand.",
        "lore": "",
        "special": ""
    },
    "iron_shovel": {
        "name": "Iron Shovel", "cat": CAT_TOOL, "power": 22, "damage": 4, "max_stack": 1, "tile": None,
        "rarity": RARITY_UNCOMMON,
        "desc": "Tempered iron spade for rapid trench excavation and gravel clearing.",
        "lore": "",
        "special": ""
    },
    "wooden_sword": {
        "name": "Wooden Sword", "cat": CAT_WEAPON, "power": 0, "damage": 7, "atk": 7, "def": 0,
        "crit": 2.0, "speed": 0.0, "max_stack": 1, "tile": None,
        "rarity": RARITY_COMMON,
        "desc": "A basic wooden sword carved from raw timber. Ideal for fending off early surface beasts.",
        "lore": "",
        "effects": [],
        "special": ""
    },
    "copper_shortsword": {
        "name": "Spud Shortsword", "cat": CAT_WEAPON, "power": 0, "damage": 9, "max_stack": 1, "tile": None,
        "rarity": RARITY_COMMON,
        "desc": "A trusty starter copper blade. Pierces close-range foes.",
        "lore": "'A spud with a blade is never to be underestimated.'",
        "special": "Thrust Attack"
    },
    "cactus_sword": {
        "name": "Cactus Sword", "cat": CAT_WEAPON, "power": 0, "damage": 12, "max_stack": 1, "tile": None,
        "rarity": RARITY_UNCOMMON,
        "desc": "Thorny desert blade fashioned from needle-sharp desert cactus.",
        "lore": "'Harvested beneath the scorching sun of the Arid Waste.'",
        "special": "Thorny Edge"
    },
    "copper_broadsword": {
        "name": "Copper Broadsword", "cat": CAT_WEAPON, "power": 0, "damage": 14, "max_stack": 1, "tile": None,
        "rarity": RARITY_COMMON,
        "desc": "Broad cutting arc capable of keeping creeping slimes at bay.",
        "lore": "'Balanced weight, reliable steel, and sharp enough for any wanderer.'",
        "special": "Wide Slashing Arc"
    },
    "iron_broadsword": {
        "name": "Iron Broadsword", "cat": CAT_WEAPON, "power": 0, "damage": 18, "atk": 18, "crit": 4.0, "speed": 0.0,
        "max_stack": 1, "tile": None, "rarity": RARITY_COMMON,
        "desc": "Forged iron broadsword with a balanced crossguard. Dependable blade against underground threats.",
        "lore": "'Forged from tempered iron ingots to withstand subterranean terrors.'",
        "special": "Heavy Slashing Strike"
    },
    "frost_blade": {
        "name": "Frost Blade", "cat": CAT_WEAPON, "power": 0, "damage": 18, "max_stack": 1, "tile": None,
        "rarity": RARITY_RARE,
        "desc": "Carved from glacial permafrost. Inflicts biting cold on contact.",
        "lore": "'Cold enough to freeze the blood of subterranean beasts.'",
        "special": "Chilling Strike (-25% Mob Speed)"
    },
    "sandstorm_spear": {
        "name": "Sandstorm Spear", "cat": CAT_WEAPON, "power": 0, "damage": 20, "max_stack": 1, "tile": None,
        "rarity": RARITY_RARE,
        "desc": "Long polearm imbued with desert dust whirlwinds for extended reach.",
        "lore": "'Carried by ancient tomb wardens across shifting sands.'",
        "special": "Extended Reach"
    },
    "gold_broadsword": {
        "name": "Golden Spud Blade", "cat": CAT_WEAPON, "power": 0, "damage": 22, "max_stack": 1, "tile": None,
        "rarity": RARITY_RARE,
        "desc": "A masterwork golden blade that shines brilliantly underground.",
        "lore": "'Gleams with the righteous pride of the high tuber courts.'",
        "special": "+6% Critical Strike Chance"
    },
    "shadow_cleaver": {
        "name": "Shadow Cleaver", "cat": CAT_WEAPON, "power": 0, "damage": 28, "max_stack": 1, "tile": None,
        "rarity": RARITY_RARE,
        "desc": "Pulsing with dark energy harvested from the Blight.",
        "lore": "'The blade hums with the whispers of ancient nightmares.'",
        "special": "Dark Cleave"
    },
    "magma_greatsword": {
        "name": "Magma Greatsword", "cat": CAT_WEAPON, "power": 0, "damage": 38, "max_stack": 1, "tile": None,
        "rarity": RARITY_EPIC,
        "desc": "Dredged from molten caverns. Ignites monsters with intense heat.",
        "lore": "'Forged inside the belly of Potaria where liquid rock flows like water.'",
        "special": "Molten Blaze (+8 Fire Damage)"
    },
    "bone_scythe": {
        "name": "Bone Scythe", "cat": CAT_WEAPON, "power": 0, "damage": 35, "max_stack": 1, "tile": None,
        "rarity": RARITY_EPIC,
        "desc": "Grim harvesting scythe constructed from cursed skeletal remains.",
        "lore": "'Reaps the living as easily as autumn wheat.'",
        "special": "Soul Harvest"
    },
    "starch_blade": {
        "name": "Legendary Starch Blade", "cat": CAT_WEAPON, "power": 0, "damage": 32, "max_stack": 1, "tile": None,
        "rarity": RARITY_LEGENDARY,
        "desc": "Condensed pure potato mana. Shimmers with astral stardust when held.",
        "lore": "'The ancestral blade of King Spudicus, savior of the tuber kin.'",
        "special": "Astral Sparkles • True Spud Radiance"
    },
    "astral_wrath": {
        "name": "Astral Wrath", "cat": CAT_WEAPON, "power": 0, "damage": 38, "max_stack": 1, "tile": None,
        "rarity": RARITY_LEGENDARY,
        "desc": "Legendary sword that summons falling celestial stars from the sky upon swinging.",
        "lore": "'Forged in cosmic crucibles when falling meteors first pierced the heavens.'",
        "special": "Starfall (Calls Down Falling Stars from Sky)",
        "effects": ["Summons Celestial Star on swing", "AoE 72px Starburst Explosion", "Celestial Radiance"]
    },
    "starfury": {
        "name": "Astral Wrath", "cat": CAT_WEAPON, "power": 0, "damage": 38, "max_stack": 1, "tile": None,
        "rarity": RARITY_LEGENDARY,
        "desc": "Legendary sword that summons falling celestial stars from the sky upon swinging.",
        "lore": "'Forged in cosmic crucibles when falling meteors first pierced the heavens.'",
        "special": "Starfall (Calls Down Falling Stars from Sky)",
        "effects": ["Summons Celestial Star on swing", "AoE 72px Starburst Explosion", "Celestial Radiance"]
    },
    "void_edge": {
        "name": "Void Edge", "cat": CAT_WEAPON, "power": 0, "damage": 50, "max_stack": 1, "tile": None,
        "rarity": RARITY_LEGENDARY,
        "desc": "A blade of pure darkness that cleaves through matter effortlessly.",
        "lore": "'Peer too long into this blade, and it peers into you.'",
        "special": "Armor Penetration (+15 True Damage)"
    },
    "celestial_greatsword": {
        "name": "Celestial Titan Greatsword", "cat": CAT_WEAPON, "power": 0, "damage": 62, "max_stack": 1, "tile": None,
        "rarity": RARITY_MYTHIC,
        "desc": "Supreme cosmic greatsword. Emits radiant astral shockwaves and sparks.",
        "lore": "'Carried by Grand Boss Sol-Rho before the heavens surrendered.'",
        "special": "Solar Supernova • Mythic Astral Radiance"
    },
    "wood_bow": {
        "name": "Wood Bow", "cat": CAT_WEAPON, "power": 0, "damage": 8, "max_stack": 1, "tile": None,
        "rarity": RARITY_COMMON,
        "desc": "Simple wooden bow. Consumes arrows from your backpack when fired.",
        "lore": "",
        "special": ""
    },
    "bone_bow": {
        "name": "Bone Recurve Bow", "cat": CAT_WEAPON, "power": 0, "damage": 16, "max_stack": 1, "tile": None,
        "rarity": RARITY_RARE,
        "desc": "Reinforced skeletal recurve bow with formidable arrow velocity.",
        "lore": "'Crafted from dungeon remnants that remember the hunt.'",
        "special": "+15% Arrow Velocity"
    },
    "magma_bow": {
        "name": "Magma Bow", "cat": CAT_WEAPON, "power": 0, "damage": 26, "max_stack": 1, "tile": None,
        "rarity": RARITY_EPIC,
        "desc": "Superheats ammunition into searing flaming projectiles.",
        "lore": "'Light the darkness with blazing tracers.'",
        "special": "Ignites Fired Arrows"
    },
    "celestial_bow": {
        "name": "Celestial Titan Bow", "cat": CAT_WEAPON, "power": 0, "damage": 42, "max_stack": 1, "tile": None,
        "rarity": RARITY_MYTHIC,
        "desc": "Godlike recurve woven from solar flare filaments.",
        "lore": "'No target can hide from arrows that travel with the speed of morning light.'",
        "special": "Starlight Volley • Mythic Astral Radiance"
    },
    "composite_bow": {
        "name": "Composite Bow", "cat": CAT_WEAPON, "power": 0, "damage": 24, "atk": 24, "max_stack": 1, "tile": None,
        "rarity": RARITY_RARE,
        "desc": "Laminated recurve composite bow with enhanced draw weight and projectile velocity.",
        "lore": "'Layered timber, horn, and sinew bent into a lethal curve.'",
        "special": "+25% Arrow Velocity • Ballistic Gravity Archery"
    },
    "reinforced_composite_bow": {
        "name": "Reinforced Composite Bow", "cat": CAT_WEAPON, "power": 0, "damage": 36, "atk": 36, "max_stack": 1, "tile": None,
        "rarity": RARITY_EPIC,
        "desc": "Heavy composite bow bound in annealed iron bands for extreme draw tension.",
        "lore": "'Bound with annealed iron bands for devastating draw tension.'",
        "special": "+40% Arrow Velocity • Piercing Shafts"
    },
    "ancient_composite_bow": {
        "name": "Ancient Composite Bow", "cat": CAT_WEAPON, "power": 0, "damage": 56, "atk": 56, "max_stack": 1, "tile": None,
        "rarity": RARITY_ANCIENT,
        "desc": "Unearthed primordial composite bow strung with glowing celestial fibers.",
        "lore": "'Unearthed from the dawn of Potaria, strung with celestial stardust fibers.'",
        "special": "Starlight Volley • Ancient Radiance • Fallback Energy Arrows"
    },
    "fire_staff": {
        "name": "Fire Staff", "cat": CAT_WEAPON, "power": 0, "damage": 30, "max_stack": 1, "tile": None,
        "rarity": RARITY_RARE,
        "desc": "Hurls explosive incendiary fireballs that detonate on monsters.",
        "lore": "'The fury of the underground hearth encased in polished staff-wood.'",
        "special": "Magic Fireball Cast"
    },
    "frost_staff": {
        "name": "Frost Staff", "cat": CAT_WEAPON, "power": 0, "damage": 28, "max_stack": 1, "tile": None,
        "rarity": RARITY_RARE,
        "desc": "Conjures piercing icy needles that freeze enemy ranks.",
        "lore": "'A whisper of the glacial mountain tops.'",
        "special": "Freezing Shards"
    },
    "void_scepter": {
        "name": "Void Scepter", "cat": CAT_WEAPON, "power": 0, "damage": 46, "max_stack": 1, "tile": None,
        "rarity": RARITY_MYTHIC,
        "desc": "Channels cosmic dark holes that crush monsters with gravitational force.",
        "lore": "'The darkness of outer space held firmly in one spud's hand.'",
        "special": "Gravitational Collapse"
    },
    "nether_cleaver": {
        "name": "Nether Cleaver", "cat": CAT_WEAPON, "power": 0, "damage": 45, "max_stack": 1, "tile": None,
        "rarity": RARITY_EPIC,
        "desc": "Jagged cleaver soaked in dungeon darkness. Causes grievous wounds.",
        "lore": "'Its serrations hunger for demonic foes.'",
        "special": "Lacerate"
    },
    "ancient_sword": {
        "name": "Ancient Sword", "cat": CAT_WEAPON, "power": 0, "damage": 42, "atk": 42, "def": 4, "hp": 25, "crit": 12.0, "speed": 0.25, "max_stack": 1, "tile": None,
        "rarity": RARITY_ANCIENT,
        "desc": "A legendary relic imbued with piercing crystalline needles.",
        "lore": "'A primordial blade that unleashes freezing needles upon the unwary.'",
        "effects": ["Freezing Needles (Pierces through enemies)", "Molten Blaze (+12 Fire Damage over 3s)", "Armor Penetration (+15 True Damage)"],
        "special": "Freezing Needles (Pierces through enemies) • Molten Blaze • Armor Penetration"
    },
    "ancient_sword_1": {
        "name": "Ancient Sword", "cat": CAT_WEAPON, "power": 0, "damage": 42, "atk": 42, "def": 4, "hp": 25, "crit": 12.0, "speed": 0.25, "max_stack": 1, "tile": None,
        "rarity": RARITY_ANCIENT,
        "desc": "A legendary relic imbued with piercing crystalline needles.",
        "lore": "'A primordial blade that unleashes freezing needles upon the unwary.'",
        "effects": ["Freezing Needles (Pierces through enemies)", "Molten Blaze (+12 Fire Damage over 3s)", "Armor Penetration (+15 True Damage)"],
        "special": "Freezing Needles (Pierces through enemies) • Molten Blaze • Armor Penetration"
    },
    "wooden_arrow": {
        "name": "Wooden Arrow", "cat": CAT_MATERIAL, "power": 0, "damage": 5, "max_stack": 999, "tile": None,
        "rarity": RARITY_COMMON,
        "desc": "Standard bow ammunition crafted from wood and stone.",
        "lore": "",
        "special": ""
    },
    "frostburn_arrow": {
        "name": "Frostburn Arrow", "cat": CAT_MATERIAL, "power": 0, "damage": 10, "max_stack": 999, "tile": None,
        "rarity": RARITY_UNCOMMON,
        "desc": "Chilled arrow dipped in frost core essence. Deals +8 bonus damage.",
        "lore": "'Burns colder than the heart of winter.'",
        "special": "+8 Frost Damage"
    },
    "flame_arrow": {
        "name": "Flame Arrow", "cat": CAT_MATERIAL, "power": 0, "damage": 8, "max_stack": 999, "tile": None,
        "rarity": RARITY_UNCOMMON,
        "desc": "Ignited arrow tipped with torch flame and sap. Burns targets on hit.",
        "lore": "'A flickering spark that sets the night ablaze.'",
        "special": "+6 Fire Damage • Burns Targets"
    },
    "astral_arrow": {
        "name": "Astral Arrow", "cat": CAT_MATERIAL, "power": 0, "damage": 18, "max_stack": 999, "tile": None,
        "rarity": RARITY_EPIC,
        "desc": "Arrow imbued with fallen star matter. Flies at high velocity and pierces darkness.",
        "lore": "'Carries the radiant vengeance of distant constellations.'",
        "special": "+14 Starlight Damage • High Velocity"
    },

    # ----------------------------------------------------
    # Armor (Head)
    # ----------------------------------------------------
    "potato_cap": {
        "name": "Potato Cap", "cat": "armor_head", "def": 1, "max_stack": 1, "tile": None,
        "rarity": RARITY_COMMON,
        "desc": "A warm burlap cap that shields Spud's sprout from dirt.",
        "lore": "'Simple and proud.'",
        "special": "+1 Defense"
    },
    "cactus_helmet": {
        "name": "Cactus Helmet", "cat": "armor_head", "def": 2, "max_stack": 1, "tile": None,
        "rarity": RARITY_UNCOMMON,
        "desc": "Thorny headgear that dissuades flying pests from diving.",
        "lore": "'Prickly on the outside, surprisingly snug on the inside.'",
        "special": "+2 Defense"
    },
    "copper_helmet": {
        "name": "Copper Helmet", "cat": "armor_head", "def": 1, "max_stack": 1, "tile": None,
        "rarity": RARITY_COMMON,
        "desc": "Solid copper headpiece providing basic protection against cave-ins.",
        "lore": "'Polished to a lustrous orange sheen.'",
        "special": "+1 Defense"
    },
    "frost_hood": {
        "name": "Frost Hood", "cat": "armor_head", "def": 6, "max_stack": 1, "tile": None,
        "rarity": RARITY_RARE,
        "desc": "Enchanted snowy cowl that keeps the mind sharp and cool.",
        "lore": "'Woven from the wool of glacial snow-beasts.'",
        "special": "+6 Defense • Cold Resistance"
    },
    "iron_helmet": {
        "name": "Iron Helmet", "cat": "armor_head", "def": 7, "max_stack": 1, "tile": None,
        "rarity": RARITY_UNCOMMON,
        "desc": "Riveted iron faceguard that turns aside sharp claws and fangs.",
        "lore": "'Forged at high heat to withstand heavy dungeon strikes.'",
        "special": "+7 Defense"
    },
    "gold_helmet": {
        "name": "Gold Helmet", "cat": "armor_head", "def": 10, "max_stack": 1, "tile": None,
        "rarity": RARITY_RARE,
        "desc": "Heavily gilded plate helm worn by nobility.",
        "lore": "'A symbol of courage that inspires allies on the battlefield.'",
        "special": "+10 Defense"
    },
    "miner_helmet": {
        "name": "Potato Miner Helmet", "cat": "armor_head", "def": 3, "max_stack": 1, "tile": None,
        "rarity": RARITY_UNCOMMON,
        "desc": "Equipped with a sturdy miner headlamp that casts gentle illumination in dark caves.",
        "lore": "'A trusted miner companion through the subterranean gloom.'",
        "effects": ["Cave Illumination (Gentle Headlamp)"],
        "special": "Cave Illumination (Headlamp Light)"
    },
    "shadow_helmet": {
        "name": "Shadow Helmet", "cat": "armor_head", "def": 12, "max_stack": 1, "tile": None,
        "rarity": RARITY_RARE,
        "desc": "Infused with the essence of the Blight. Shadows dance across the visor.",
        "lore": "'The wielder sees clearly through corrupted gloom.'",
        "special": "+12 Defense"
    },
    "magma_helmet": {
        "name": "Magma Helmet", "cat": "armor_head", "def": 14, "max_stack": 1, "tile": None,
        "rarity": RARITY_EPIC,
        "desc": "Forged in the molten subterranean abyss.",
        "lore": "'Its visor radiates heat that scorches nearby embers.'",
        "special": "+14 Defense • Heat Shield"
    },
    "cryo_helmet": {
        "name": "Cryo Visor", "cat": "armor_head", "def": 16, "max_stack": 1, "tile": None,
        "rarity": RARITY_EPIC,
        "desc": "Reinforced visor carved from mini-boss Glacial Spud's armor.",
        "lore": "'Sub-zero precision vision in the heat of battle.'",
        "special": "+16 Defense"
    },
    "necro_helmet": {
        "name": "Necro Bone Crown", "cat": "armor_head", "def": 13, "max_stack": 1, "tile": None,
        "rarity": RARITY_EPIC,
        "desc": "Grim skeletal crown infused with necromantic essence.",
        "lore": "'Ghouls hesitate when gazing upon this dread headpiece.'",
        "special": "+13 Defense"
    },
    "titan_helmet": {
        "name": "Celestial Titan Helm", "cat": "armor_head", "def": 26, "max_stack": 1, "tile": None,
        "rarity": RARITY_LEGENDARY,
        "desc": "Legendary cosmic helm radiating celestial starlight.",
        "lore": "'Crowned with the very energy that sustains distant stars.'",
        "special": "+26 Defense • Radiant Astral Sparkles"
    },
    "crown_of_potaria": {
        "name": "Crown of Potaria", "cat": "armor_head", "def": 22, "max_stack": 1, "tile": None,
        "rarity": RARITY_LEGENDARY,
        "desc": "Ancient golden crown bequeathed to the True Hero of Potaria.",
        "lore": "'Long live Spud, protector of the infinite realm.'",
        "special": "+22 Defense • Hero's Aura"
    },

    # ----------------------------------------------------
    # Armor (Chest)
    # ----------------------------------------------------
    "potato_tunic": {
        "name": "Potato Tunic", "cat": "armor_chest", "def": 2, "max_stack": 1, "tile": None,
        "rarity": RARITY_COMMON,
        "desc": "A rugged potato-sack vest offering gentle protection.",
        "lore": "'Woven from the finest burlap sacks in the garden.'",
        "special": "+2 Defense"
    },
    "cactus_chestplate": {
        "name": "Cactus Chestplate", "cat": "armor_chest", "def": 4, "max_stack": 1, "tile": None,
        "rarity": RARITY_UNCOMMON,
        "desc": "Reinforced cuirass bristling with sharp defensive spikes.",
        "lore": "'Attacking a spud in this armor is an agonizing mistake.'",
        "special": "+4 Defense • Spiked Deflection"
    },
    "copper_chestplate": {
        "name": "Copper Chestplate", "cat": "armor_chest", "def": 1, "max_stack": 1, "tile": None,
        "rarity": RARITY_COMMON,
        "desc": "Hammered copper plate shielding vital potato organs.",
        "lore": "'Affordable, dependable, and easily mended.'",
        "special": "+1 Defense"
    },
    "frost_parka": {
        "name": "Frost Parka", "cat": "armor_chest", "def": 8, "max_stack": 1, "tile": None,
        "rarity": RARITY_RARE,
        "desc": "Heavy insulated coat lined with frosted fur.",
        "lore": "'Shrugs off icy subterranean blizzards with ease.'",
        "special": "+8 Defense"
    },
    "iron_chestplate": {
        "name": "Iron Chestplate", "cat": "armor_chest", "def": 10, "max_stack": 1, "tile": None,
        "rarity": RARITY_UNCOMMON,
        "desc": "Heavy forged breastplate capable of turning aside heavy claws.",
        "lore": "'A trusted companion on long descents into the dark.'",
        "special": "+10 Defense"
    },
    "gold_chestplate": {
        "name": "Gold Chestplate", "cat": "armor_chest", "def": 14, "max_stack": 1, "tile": None,
        "rarity": RARITY_RARE,
        "desc": "Ornate gold armor engraved with ancient royal crests.",
        "lore": "'Shines like the dawn over the subterranean caverns.'",
        "special": "+14 Defense"
    },
    "shadow_plate": {
        "name": "Shadow Plate", "cat": "armor_chest", "def": 16, "max_stack": 1, "tile": None,
        "rarity": RARITY_RARE,
        "desc": "Plate armor woven with dark ethereal blighted fibers.",
        "lore": "'Monsters flinch as if striking empty mist.'",
        "special": "+16 Defense"
    },
    "magma_chestplate": {
        "name": "Magma Cuirass", "cat": "armor_chest", "def": 19, "max_stack": 1, "tile": None,
        "rarity": RARITY_EPIC,
        "desc": "Heavy molten plates glowing with perpetual subterranean heat.",
        "lore": "'Forged in volcanic crucibles far beneath the stone.'",
        "special": "+19 Defense • Molten Shield"
    },
    "cryo_chestplate": {
        "name": "Cryo Carapace", "cat": "armor_chest", "def": 22, "max_stack": 1, "tile": None,
        "rarity": RARITY_EPIC,
        "desc": "Hardened permafrost carapace dropped by Cryo-Spud.",
        "lore": "'Glacial resilience that freezes the impact of incoming strikes.'",
        "special": "+22 Defense"
    },
    "necro_chestplate": {
        "name": "Necro Bone Plate", "cat": "armor_chest", "def": 18, "max_stack": 1, "tile": None,
        "rarity": RARITY_EPIC,
        "desc": "Interlocked skeletal ribs reinforced with dark dungeon metal.",
        "lore": "'Lightweight, eerily quiet, and surprisingly durable.'",
        "special": "+18 Defense"
    },
    "titan_chestplate": {
        "name": "Celestial Titan Plate", "cat": "armor_chest", "def": 32, "max_stack": 1, "tile": None,
        "rarity": RARITY_LEGENDARY,
        "desc": "God-tier breastplate worn by Celestial Titan Sol-Rho.",
        "lore": "'Wards off the crushing gravity of the cosmos.'",
        "special": "+32 Defense • Radiant Astral Sparkles"
    },

    # ----------------------------------------------------
    # Armor (Legs)
    # ----------------------------------------------------
    "potato_pants": {
        "name": "Potato Pants", "cat": "armor_legs", "def": 1, "max_stack": 1, "tile": None,
        "rarity": RARITY_COMMON,
        "desc": "Comfy trousers that let roots flex freely.",
        "lore": "'Comfort first, adventuring second.'",
        "special": "+1 Defense"
    },
    "cactus_greaves": {
        "name": "Cactus Greaves", "cat": "armor_legs", "def": 3, "max_stack": 1, "tile": None,
        "rarity": RARITY_UNCOMMON,
        "desc": "Spiky desert leg guards that kick away creeping crawlers.",
        "lore": "'Mind where you step, and mind where you kick.'",
        "special": "+3 Defense"
    },
    "copper_greaves": {
        "name": "Copper Greaves", "cat": "armor_legs", "def": 1, "max_stack": 1, "tile": None,
        "rarity": RARITY_COMMON,
        "desc": "Shining copper greaves protecting legs and shins.",
        "lore": "'Good solid metal for a solid sprint.'",
        "special": "+1 Defense"
    },
    "iron_greaves": {
        "name": "Iron Greaves", "cat": "armor_legs", "def": 7, "max_stack": 1, "tile": None,
        "rarity": RARITY_UNCOMMON,
        "desc": "Heavy iron plates that steady your footing against tremors.",
        "lore": "'Grounds the spud firmly on subterranean ground.'",
        "special": "+7 Defense"
    },
    "gold_greaves": {
        "name": "Gold Greaves", "cat": "armor_legs", "def": 10, "max_stack": 1, "tile": None,
        "rarity": RARITY_RARE,
        "desc": "Gilded leg guards favored by grand champions.",
        "lore": "'Steps of gold leave legends in their wake.'",
        "special": "+10 Defense"
    },
    "magma_greaves": {
        "name": "Magma Greaves", "cat": "armor_legs", "def": 13, "max_stack": 1, "tile": None,
        "rarity": RARITY_EPIC,
        "desc": "Leaves trailing embers with every confident stride.",
        "lore": "'Walk through fire without scorching your roots.'",
        "special": "+13 Defense"
    },
    "cryo_greaves": {
        "name": "Cryo Striders", "cat": "armor_legs", "def": 15, "max_stack": 1, "tile": None,
        "rarity": RARITY_EPIC,
        "desc": "Glacial boots providing frictionless movement across ice and stone.",
        "lore": "'Skate across the battlefield like a winter squall.'",
        "special": "+15 Defense"
    },
    "necro_greaves": {
        "name": "Necro Bone Greaves", "cat": "armor_legs", "def": 12, "max_stack": 1, "tile": None,
        "rarity": RARITY_EPIC,
        "desc": "Bone greaves that allow uncanny silent movement in dungeon halls.",
        "lore": "'Step silently like a spirit through the crypt.'",
        "special": "+12 Defense"
    },
    "titan_greaves": {
        "name": "Celestial Titan Greaves", "cat": "armor_legs", "def": 22, "max_stack": 1, "tile": None,
        "rarity": RARITY_LEGENDARY,
        "desc": "Legendary celestial armor forged from starfall iron.",
        "lore": "'Stride across worlds without trembling.'",
        "special": "+22 Defense • Radiant Astral Sparkles"
    },
    "speed_boots": {
        "name": "Rootrunner Boots", "cat": "armor_legs", "def": 4, "max_stack": 1, "tile": None,
        "rarity": RARITY_RARE,
        "desc": "Sprout-woven boots that grant +25% sprint velocity.",
        "lore": "'Swift as an underground sprout bursting into the light.'",
        "special": "+25% Movement Speed"
    },
    "zephyr_striders": {
        "name": "Zephyr Striders", "cat": "armor_legs", "def": 5, "max_stack": 1, "tile": None,
        "rarity": RARITY_EPIC,
        "desc": "Winged boots discovered in treasure chests. Drastically increases running speed.",
        "lore": "'The wearer moves like a gale across the plains, unburdened by mortal weight.'",
        "special": "+115% Sprint Speed",
        "effects": ["+115% Sprint Speed", "Air Cushion Fall Resistance"]
    },
    "hermes_boots": {
        "name": "Zephyr Striders", "cat": "armor_legs", "def": 5, "max_stack": 1, "tile": None,
        "rarity": RARITY_EPIC,
        "desc": "Winged boots discovered in treasure chests. Drastically increases running speed.",
        "lore": "'The wearer moves like a gale across the plains, unburdened by mortal weight.'",
        "special": "+115% Sprint Speed",
        "effects": ["+115% Sprint Speed", "Air Cushion Fall Resistance"]
    },

    # ----------------------------------------------------
    # Accessories
    # ----------------------------------------------------
    "warrior_charm": {
        "name": "Warrior Charm", "cat": CAT_ACCESSORY, "atk": 8, "max_stack": 1, "tile": None,
        "rarity": RARITY_RARE,
        "desc": "An ancient medallion carved with martial runes.",
        "lore": "'Empowers every strike with warrior resolve.'",
        "special": "+8 Physical Attack"
    },
    "guardian_ring": {
        "name": "Guardian Ring", "cat": CAT_ACCESSORY, "def": 8, "max_stack": 1, "tile": None,
        "rarity": RARITY_RARE,
        "desc": "Solid granite ring humming with protective wards.",
        "lore": "'Deflects the fiercest claws.'",
        "special": "+8 Defense"
    },
    "talisman_of_vigor": {
        "name": "Talisman of Vigor", "cat": CAT_ACCESSORY, "def": 4, "mp_regen": 1.0, "max_stack": 1, "tile": None,
        "rarity": RARITY_EPIC,
        "desc": "Blessed talisman that accelerates Spud's natural recovery.",
        "lore": "'A warm pulse soothes even the deepest cuts.'",
        "special": "+4 DEF • +1.0 MP/s Mana Regen • Life Regen",
        "effects": ["Life Surge (+2 HP/s)", "Vigor Overflow (+1.0 MP/s Mana Regen)"]
    },
    "band_of_regeneration": {
        "name": "Talisman of Vigor", "cat": CAT_ACCESSORY, "def": 4, "mp_regen": 1.0, "max_stack": 1, "tile": None,
        "rarity": RARITY_EPIC,
        "desc": "Blessed talisman that accelerates Spud's natural recovery.",
        "lore": "'A warm pulse soothes even the deepest cuts.'",
        "special": "+4 DEF • +1.0 MP/s Mana Regen • Life Regen",
        "effects": ["Life Surge (+2 HP/s)", "Vigor Overflow (+1.0 MP/s Mana Regen)"]
    },
    "arcane_orchid": {
        "name": "Arcane Orchid", "cat": CAT_ACCESSORY, "atk": 6, "mp_regen": 2.5, "max_stack": 1, "tile": None,
        "rarity": RARITY_EPIC,
        "desc": "An ethereal blossoming bloom that enhances magic potency.",
        "lore": "'Grown in the luminescent mushroom groves.'",
        "special": "+6 Magic ATK • +2.5 MP/s Mana Regen",
        "effects": ["Arcane Conduit (-20% Skill MP Cost)", "+2.5 MP/s Mana Regen"]
    },
    "mana_flower": {
        "name": "Arcane Orchid", "cat": CAT_ACCESSORY, "atk": 6, "mp_regen": 2.5, "max_stack": 1, "tile": None,
        "rarity": RARITY_EPIC,
        "desc": "An ethereal blossoming bloom that enhances magic potency.",
        "lore": "'Grown in the luminescent mushroom groves.'",
        "special": "+6 Magic ATK • +2.5 MP/s Mana Regen",
        "effects": ["Arcane Conduit (-20% Skill MP Cost)", "+2.5 MP/s Mana Regen"]
    },
    "lucky_clover": {
        "name": "Lucky Clover", "cat": CAT_ACCESSORY, "crit": 15.0, "max_stack": 1, "tile": None,
        "rarity": RARITY_RARE,
        "desc": "A rare subterranean four-leaf clover blessed by good fortune.",
        "lore": "'Fortune favors the adventurous spud.'",
        "special": "+15% Critical Strike Chance"
    },
    "celestial_emblem": {
        "name": "Celestial Emblem", "cat": CAT_ACCESSORY, "atk": 16, "def": 6, "mp_regen": 1.8, "max_stack": 1, "tile": None,
        "rarity": RARITY_EPIC,
        "desc": "Forged from celestial portal shards. Grants overwhelming power.",
        "lore": "'The heavens answer those who dare claim their sigil.'",
        "special": "+16 Attack • +6 Defense • +1.8 MP/s Mana Regen"
    },
    "titans_ring": {
        "name": "Titan's Ring", "cat": CAT_ACCESSORY, "def": 14, "atk": 10, "max_stack": 1, "tile": None,
        "rarity": RARITY_EPIC,
        "desc": "Heavy obsidian band pulsing with titanic fortitude.",
        "lore": "'Walk like a titan among mortals.'",
        "special": "+14 Defense • +10 Attack"
    },
    "volcanic_stone": {
        "name": "Volcanic Magma Stone", "cat": CAT_ACCESSORY, "atk": 13, "def": 5, "max_stack": 1, "tile": None,
        "rarity": RARITY_EPIC,
        "desc": "Infuses melee attacks with searing magma fire.",
        "lore": "'A dormant volcano sleeping inside a polished stone.'",
        "special": "+13 Attack • Fire Weapon Coating"
    },
    "frost_amulet": {
        "name": "Glacial Frost Amulet", "cat": CAT_ACCESSORY, "def": 11, "atk": 6, "mp_regen": 1.2, "max_stack": 1, "tile": None,
        "rarity": RARITY_EPIC,
        "desc": "Radiates an aura of freezing permafrost around Spud.",
        "lore": "'Cooled by the breath of the mountain snows.'",
        "special": "+11 Defense • +6 Attack • +1.2 MP/s Mana Regen"
    },

    # ----------------------------------------------------
    # Skill Books (Chroisen Style)
    # ----------------------------------------------------
    "skillbook_power_slash": {
        "name": "Skill Book: Power Slash", "cat": "skillbook", "skill": "power_slash", "max_stack": 1, "tile": None,
        "rarity": RARITY_RARE,
        "desc": "Right-click to learn Power Slash. Assign to hotkeys (Q, F, V, R) in the Character Status menu [C].",
        "lore": "'A mighty cleave that focuses Spud's weight into a 200% physical strike.'",
        "special": "Active Combat Skill (12 MP • 3.0s CD)"
    },
    "skillbook_whirlwind": {
        "name": "Skill Book: Whirlwind", "cat": "skillbook", "skill": "whirlwind", "max_stack": 1, "tile": None,
        "rarity": RARITY_RARE,
        "desc": "Right-click to learn Whirlwind. Assign to hotkeys (Q, F, V, R) in the Character Status menu [C].",
        "lore": "'Spins in a devastating 360-degree arc, lacerating all nearby monsters.'",
        "special": "Active Combat Skill (18 MP • 4.5s CD)"
    },
    "skillbook_dash": {
        "name": "Skill Book: Swift Dash", "cat": "skillbook", "skill": "dash", "max_stack": 1, "tile": None,
        "rarity": RARITY_RARE,
        "desc": "Right-click to learn Swift Dash. Assign to hotkeys (Q, F, V, R) in the Character Status menu [C].",
        "lore": "'A lightning evasion burst that slips past hostile attacks with invulnerability.'",
        "special": "Active Mobility Skill (10 MP • 2.5s CD)"
    },
    "skillbook_fireball": {
        "name": "Skill Book: Fireball", "cat": "skillbook", "skill": "fireball", "max_stack": 1, "tile": None,
        "rarity": RARITY_RARE,
        "desc": "Right-click to learn Fireball. Assign to hotkeys (Q, F, V, R) in the Character Status menu [C].",
        "lore": "'Channels mystic flame into an explosive incendiary sphere that detonates on contact.'",
        "special": "Active Magic Skill (15 MP • 3.5s CD)"
    },
    "skillbook_meteor": {
        "name": "Skill Book: Meteor Strike", "cat": "skillbook", "skill": "meteor", "max_stack": 1, "tile": None,
        "rarity": RARITY_EPIC,
        "desc": "Right-click to learn Meteor Strike. Assign to hotkeys (Q, F, V, R) in the Character Status menu [C].",
        "lore": "'Calls down a blazing meteor from orbit to incinerate an entire enemy battalion.'",
        "special": "Devastating Area Magic (30 MP • 8.0s CD)"
    },
    "skillbook_frost_nova": {
        "name": "Skill Book: Frost Nova", "cat": "skillbook", "skill": "frost_nova", "max_stack": 1, "tile": None,
        "rarity": RARITY_EPIC,
        "desc": "Right-click to learn Frost Nova. Assign to hotkeys (Q, F, V, R) in the Character Status menu [C].",
        "lore": "'Expels an expanding ring of subzero ice, flash-freezing all surrounding adversaries.'",
        "special": "Crowd Control Spell (22 MP • 6.0s CD)"
    },
    "skillbook_celestial_shield": {
        "name": "Skill Book: Celestial Shield", "cat": "skillbook", "skill": "celestial_shield", "max_stack": 1, "tile": None,
        "rarity": RARITY_LEGENDARY,
        "desc": "Right-click to learn Celestial Shield. Assign to hotkeys (Q, F, V, R) in the Character Status menu [C].",
        "lore": "'Envelops Spud in an invulnerable aegis of holy starlight.'",
        "special": "Invulnerability Aegis (35 MP • 14.0s CD)"
    },
    "skillbook_void_singularity": {
        "name": "Skill Book: Void Singularity", "cat": "skillbook", "skill": "void_singularity", "max_stack": 1, "tile": None,
        "rarity": RARITY_LEGENDARY,
        "desc": "Right-click to learn Void Singularity. Assign to hotkeys (Q, F, V, R) in the Character Status menu [C].",
        "lore": "'Summons a catastrophic gravitational vortex crushing all nearby foes.'",
        "special": "Catastrophic Vortex (48 MP • 16.0s CD)"
    },

    # ----------------------------------------------------
    # Placeable Blocks & Furniture
    # ----------------------------------------------------
    "dirt_block": {
        "name": "Dirt Block", "cat": CAT_BLOCK, "power": 0, "damage": 0, "max_stack": 999, "tile": TILE_DIRT,
        "rarity": RARITY_COMMON,
        "desc": "Rich fertile earth. Right-click to place. Sprouts fresh grass when exposed to sun.",
        "lore": "'The foundation of all life on Potaria.'",
        "special": "Basic Terrain Block"
    },
    "stone_block": {
        "name": "Stone Block", "cat": CAT_BLOCK, "power": 0, "damage": 0, "max_stack": 999, "tile": TILE_STONE,
        "rarity": RARITY_COMMON,
        "desc": "Common subterranean rock. Right-click to place.",
        "lore": "'Sturdy, cold, and eternal.'",
        "special": "Basic Building Block"
    },
    "wood": {
        "name": "Wood", "cat": CAT_BLOCK, "power": 0, "damage": 0, "max_stack": 999, "tile": TILE_WOOD,
        "rarity": RARITY_COMMON,
        "desc": "Lumber harvested from surface trees. Right-click to place or craft into workbench.",
        "lore": "'A carpenter's fundamental resource.'",
        "special": "Crafting & Building"
    },
    "leaves": {
        "name": "Leaves", "cat": CAT_BLOCK, "power": 0, "damage": 0, "max_stack": 999, "tile": TILE_LEAVES,
        "rarity": RARITY_COMMON,
        "desc": "Lush foliage blocks harvested from tree canopies. Can be placed for verdant decoration.",
        "lore": "'Fresh leaves whispering in the gentle canopy breeze.'",
        "special": "Decorative Foliage Block"
    },
    "oak_sapling": {
        "name": "Oak Sapling", "cat": CAT_BLOCK, "power": 0, "damage": 0, "max_stack": 99, "tile": TILE_SAPLING,
        "rarity": RARITY_COMMON,
        "desc": "A young tree sapling. Plant in soil under open sunlight to grow a magnificent oak tree.",
        "lore": "'Great forests slumber within small seeds.'",
        "special": "Grows into Tree Daily in Sunlight"
    },
    "palm_sapling": {
        "name": "Palm Sapling", "cat": CAT_BLOCK, "power": 0, "damage": 0, "max_stack": 99, "tile": TILE_SAPLING,
        "rarity": RARITY_COMMON,
        "desc": "A tropical coastal palm sapling. Plant in sandy ground under sunlight to grow into a palm tree.",
        "lore": "'Brought by oceanic trade winds.'",
        "special": "Grows into Tree Daily in Sunlight"
    },
    "pine_sapling": {
        "name": "Pine Sapling", "cat": CAT_BLOCK, "power": 0, "damage": 0, "max_stack": 99, "tile": TILE_SAPLING,
        "rarity": RARITY_COMMON,
        "desc": "Hardy evergreen needle sapling. Thrives in alpine permafrost soil under sunlight.",
        "lore": "'Resilient against sub-zero mountain gales.'",
        "special": "Grows into Tree Daily in Sunlight"
    },
    "blight_sapling": {
        "name": "Blight Sapling", "cat": CAT_BLOCK, "power": 0, "damage": 0, "max_stack": 99, "tile": TILE_SAPLING,
        "rarity": RARITY_UNCOMMON,
        "desc": "An otherworldly sapling with corrupted violet veins. Grows into a twisted nether tree in sunlight.",
        "lore": "'Infused with abyssal nether spores.'",
        "special": "Grows into Tree Daily in Sunlight"
    },
    "wood_platform": {
        "name": "Wood Platform", "cat": CAT_BLOCK, "power": 0, "damage": 0, "max_stack": 999, "tile": TILE_WOOD_PLATFORM,
        "rarity": RARITY_COMMON,
        "desc": "Semi-solid ledge for vertical climbing. Hold [S] or Down to drop through.",
        "lore": "'Enables easy travel between multilevel subterranean floors.'",
        "special": "Drop-Through Platform"
    },
    "work_bench": {
        "name": "Work Bench", "cat": CAT_BLOCK, "power": 0, "damage": 0, "max_stack": 99, "tile": TILE_WORK_BENCH,
        "rarity": RARITY_UNCOMMON,
        "desc": "Place on the ground. Stand near it to unlock advanced crafting recipes for tools, furniture, and house blocks.",
        "lore": "'The craftsman's table where rough materials become grand creations.'",
        "special": "Crafting Station (Unlocks Advanced Recipes)"
    },
    "furnace": {
        "name": "Furnace", "cat": CAT_BLOCK, "power": 0, "damage": 0, "max_stack": 99, "tile": TILE_FURNACE,
        "rarity": RARITY_UNCOMMON,
        "desc": "Place on the ground. Stand near it to smelt raw ores into ingots and cook savory potato meals.",
        "lore": "'Roaring coals that turn crude ores into lustrous metal.'",
        "special": "Smelting & Cooking Station"
    },
    "torch": {
        "name": "Torch", "cat": CAT_BLOCK, "power": 0, "damage": 0, "max_stack": 999, "tile": TILE_TORCH,
        "rarity": RARITY_COMMON,
        "desc": "Provides bright illumination. Emits light to deter monsters and light up homes.",
        "lore": "'Banishes the deepest subterranean darkness.'",
        "special": "Illumination (Level 14 Light)"
    },
    "stone_brick": {
        "name": "Stone Brick", "cat": CAT_BLOCK, "power": 0, "damage": 0, "max_stack": 999, "tile": TILE_STONE_BRICK,
        "rarity": RARITY_COMMON,
        "desc": "Smooth masonry bricks smelted in a furnace. Sturdy block for castles and fortresses.",
        "lore": "'Hewn and polished to endure centuries of siege.'",
        "special": "Impenetrable Building Block"
    },
    "dungeon_brick": {
        "name": "Dungeon Brick", "cat": CAT_BLOCK, "power": 0, "damage": 0, "max_stack": 999, "tile": TILE_DUNGEON_BRICK,
        "rarity": RARITY_RARE,
        "desc": "Ancient Nether Dungeon masonry that resists explosive destruction.",
        "lore": "'Carved from the abyssal foundations of Lord Malus's domain.'",
        "special": "Dungeon Construction"
    },
    "sand_block": {
        "name": "Sand Block", "cat": CAT_BLOCK, "power": 0, "damage": 0, "max_stack": 999, "tile": TILE_SAND,
        "rarity": RARITY_COMMON,
        "desc": "Fine golden grains. Smelt in a furnace to craft clear Glass Windows.",
        "lore": "'Drifts gently across the Arid Waste.'",
        "special": "Smeltable into Glass"
    },
    "sandstone_block": {
        "name": "Sandstone Block", "cat": CAT_BLOCK, "power": 0, "damage": 0, "max_stack": 999, "tile": TILE_SANDSTONE,
        "rarity": RARITY_COMMON,
        "desc": "Naturally compressed desert stone.",
        "lore": "'The hardened core of ancient desert dunes.'",
        "special": "Building Block"
    },
    "cactus": {
        "name": "Cactus Block", "cat": CAT_BLOCK, "power": 0, "damage": 0, "max_stack": 999, "tile": TILE_CACTUS,
        "rarity": RARITY_COMMON,
        "desc": "Prickly succulent from the desert. Used to craft thorny weapons and armor.",
        "lore": "'Resilient flora of the dry wastes.'",
        "special": "Crafting Material & Block"
    },
    "snow_block": {
        "name": "Snow Block", "cat": CAT_BLOCK, "power": 0, "damage": 0, "max_stack": 999, "tile": TILE_SNOW,
        "rarity": RARITY_COMMON,
        "desc": "Packed powdery snow from the glacial tundra.",
        "lore": "'Soft and cold to the touch.'",
        "special": "Building Block"
    },
    "ice_block": {
        "name": "Ice Block", "cat": CAT_BLOCK, "power": 0, "damage": 0, "max_stack": 999, "tile": TILE_ICE,
        "rarity": RARITY_COMMON,
        "desc": "Slippery subterranean glacial ice.",
        "lore": "'Watch your step across the frozen caves.'",
        "special": "Slippery Surface"
    },
    "blight_grass": {
        "name": "Blight Grass Block", "cat": CAT_BLOCK, "power": 0, "damage": 0, "max_stack": 999, "tile": TILE_BLIGHT_GRASS,
        "rarity": RARITY_UNCOMMON,
        "desc": "Blighted soil pulsing with eerie purple tendrils.",
        "lore": "'Touches of the Nether creeping into the surface world.'",
        "special": "Blight Biome Block"
    },
    "corrupt_grass": {
        "name": "Blight Grass Block", "cat": CAT_BLOCK, "power": 0, "damage": 0, "max_stack": 999, "tile": TILE_BLIGHT_GRASS,
        "rarity": RARITY_UNCOMMON,
        "desc": "Blighted soil pulsing with eerie purple tendrils.",
        "lore": "'Touches of the Nether creeping into the surface world.'",
        "special": "Blight Biome Block"
    },
    "blightstone_block": {
        "name": "Blightstone Block", "cat": CAT_BLOCK, "power": 0, "damage": 0, "max_stack": 999, "tile": TILE_BLIGHTSTONE,
        "rarity": RARITY_UNCOMMON,
        "desc": "Hardened purple stone from the Blight that requires high-tier pickaxes to mine.",
        "lore": "'Heavy and cold, soaked in blighted subterranean malice.'",
        "special": "Resistant Stone"
    },
    "ebonstone_block": {
        "name": "Blightstone Block", "cat": CAT_BLOCK, "power": 0, "damage": 0, "max_stack": 999, "tile": TILE_BLIGHTSTONE,
        "rarity": RARITY_UNCOMMON,
        "desc": "Hardened purple stone from the Blight that requires high-tier pickaxes to mine.",
        "lore": "'Heavy and cold, soaked in blighted subterranean malice.'",
        "special": "Resistant Stone"
    },
    "mushroom_grass": {
        "name": "Glowing Mushroom Grass", "cat": CAT_BLOCK, "power": 0, "damage": 0, "max_stack": 999, "tile": TILE_MUSHROOM_GRASS,
        "rarity": RARITY_UNCOMMON,
        "desc": "Vibrant bioluminescent soil from underground mushroom groves.",
        "lore": "'Bathed in a peaceful blue luminescence.'",
        "special": "Emits Gentle Blue Glow"
    },
    "glowing_mushroom": {
        "name": "Glowing Mushroom", "cat": CAT_BLOCK, "power": 0, "damage": 0, "max_stack": 999, "tile": TILE_MUSHROOM_CAP,
        "rarity": RARITY_UNCOMMON,
        "desc": "Bioluminescent mushroom cap. Ingredient for Greater Healing Potions.",
        "lore": "'Pulsates with soothing subterranean spores.'",
        "special": "Potion Ingredient & Light Source"
    },
    "chest": {
        "name": "Treasure Chest", "cat": CAT_BLOCK, "power": 0, "damage": 0, "max_stack": 99, "tile": TILE_CHEST,
        "rarity": RARITY_UNCOMMON,
        "desc": "Lustrous gilded chest with golden reinforcement straps. Found in deep caverns filled with rare subterranean treasures.",
        "lore": "'Holds the forgotten relics of past adventurers.'",
        "special": "Treasure Container"
    },
    "wooden_chest": {
        "name": "Wooden Chest", "cat": CAT_BLOCK, "power": 0, "damage": 0, "max_stack": 99, "tile": TILE_CHEST,
        "rarity": RARITY_UNCOMMON,
        "desc": "Sturdy banded oak chest with iron reinforcement straps. Reliable storage for spuds.",
        "lore": "'A trusted container crafted from seasoned Potarian oak.'",
        "special": "Storage Container"
    },
    "iron_chest": {
        "name": "Iron Storage Chest", "cat": CAT_BLOCK, "power": 0, "damage": 0, "max_stack": 99, "tile": TILE_IRON_CHEST,
        "rarity": RARITY_UNCOMMON,
        "desc": "Heavy reinforced chest for storing 20 items safely. Right-click to open or manage items.",
        "lore": "'Forged from iron bands to preserve keepsakes across expeditions.'",
        "special": "20-Slot Storage Container"
    },
    "affix_stone": {
        "name": "Affix Stone", "cat": CAT_CONSUMABLE, "power": 0, "damage": 0, "max_stack": 99, "tile": None,
        "rarity": RARITY_MYTHIC,
        "desc": "A primordial runic stone. Apply to Legendary or Ancient gear with an open affix slot to awaken god-tier affixes!",
        "lore": "'Pulsating with forgotten cosmic inscriptions that alter the nature of arms.'",
        "special": "Awakens God-Tier Affixes"
    },

    # ----------------------------------------------------
    # New House & Decorative Building Blocks
    # ----------------------------------------------------
    "roof_tiles": {
        "name": "Roof Tiles", "cat": CAT_BLOCK, "power": 0, "damage": 0, "max_stack": 999, "tile": TILE_ROOF_TILES,
        "rarity": RARITY_COMMON,
        "desc": "Decorative red clay roofing shingles. Solid blocks that block monsters and rainwater.",
        "lore": "'A humble roof crowns every hero's shelter.'",
        "special": "Impenetrable House Construction"
    },
    "wood_planks": {
        "name": "Wood Planks", "cat": CAT_BLOCK, "power": 0, "damage": 0, "max_stack": 999, "tile": TILE_WOOD_PLANKS,
        "rarity": RARITY_COMMON,
        "desc": "Sanded polished timber blocks. Ideal for walls, solid floors, and ceilings.",
        "lore": "'Carved straight from the ancient oaks of Potaria.'",
        "special": "Impenetrable House Construction"
    },
    "glass_window": {
        "name": "Glass Window", "cat": CAT_BLOCK, "power": 0, "damage": 0, "max_stack": 999, "tile": TILE_GLASS,
        "rarity": RARITY_COMMON,
        "desc": "Refined crystal pane. Lets in daylight while stopping intruders.",
        "lore": "'Through crystal clarity, we watch the heavens turn.'",
        "special": "Transparent Monster Barrier"
    },
    "wooden_door": {
        "name": "Wooden Door", "cat": CAT_BLOCK, "power": 0, "damage": 0, "max_stack": 99, "tile": TILE_DOOR_CLOSED,
        "rarity": RARITY_UNCOMMON,
        "desc": "Solid wooden door. Right-click to open or close. Keeps monsters out!",
        "lore": "'A friendly entryway for spuds, an impassable gate for ghouls.'",
        "special": "Interactive Monster-Proof Barrier"
    },
    "wooden_table": {
        "name": "Wooden Table", "cat": CAT_BLOCK, "power": 0, "damage": 0, "max_stack": 99, "tile": TILE_TABLE,
        "rarity": RARITY_UNCOMMON,
        "desc": "Crafted wooden table for living quarters and house qualification.",
        "lore": "'Where great adventurers plan tomorrow's grand expeditions.'",
        "special": "Homestead Furniture"
    },
    "wooden_chair": {
        "name": "Wooden Chair", "cat": CAT_BLOCK, "power": 0, "damage": 0, "max_stack": 99, "tile": TILE_CHAIR,
        "rarity": RARITY_UNCOMMON,
        "desc": "Handcrafted spud chair. Essential for comfortable homesteads.",
        "lore": "'Even the Mightiest Spud must rest their weary roots.'",
        "special": "Homestead Furniture"
    },
    "wooden_bed": {
        "name": "Wooden Bed", "cat": CAT_BLOCK, "power": 0, "damage": 0, "max_stack": 99, "tile": TILE_BED,
        "rarity": RARITY_UNCOMMON,
        "desc": "Comfortable handcrafted bed. Right-click to set spawn point and rest to recover health.",
        "lore": "'A snug nest of dry straw and woven cotton for weary spuds.'",
        "special": "Sets Respawn Point & Rest Recovery"
    },
    "bookshelf": {
        "name": "Bookshelf", "cat": CAT_BLOCK, "power": 0, "damage": 0, "max_stack": 99, "tile": TILE_BOOKSHELF,
        "rarity": RARITY_UNCOMMON,
        "desc": "Sturdy wooden shelves lined with leather-bound arcane tomes and recipes.",
        "lore": "'Knowledge is the sweetest fertilizer for growing potatoes.'",
        "special": "Jump-Through Platform Surface"
    },
    "grandfather_clock": {
        "name": "Grandfather Clock", "cat": CAT_BLOCK, "power": 0, "damage": 0, "max_stack": 99, "tile": TILE_GRANDFATHER_CLOCK,
        "rarity": RARITY_RARE,
        "desc": "Towering pendulum clock. Right-click to check in-game celestial time.",
        "lore": "'Tick-tock, the stars dance across the Potarian night.'",
        "special": "Interactive Celestial Timekeeper"
    },
    "stone_fireplace": {
        "name": "Stone Fireplace", "cat": CAT_BLOCK, "power": 0, "damage": 0, "max_stack": 99, "tile": TILE_FIREPLACE,
        "rarity": RARITY_RARE,
        "desc": "Rustic stone hearth crackling with warm embers. Emits cozy light and smoke.",
        "lore": "'Nothing keeps the subterranean chill away like crackling oak logs.'",
        "special": "Warm Ambient Light & Rising Smoke"
    },
    "candelabra": {
        "name": "Candelabra", "cat": CAT_BLOCK, "power": 0, "damage": 0, "max_stack": 99, "tile": TILE_CANDELABRA,
        "rarity": RARITY_UNCOMMON,
        "desc": "Ornate three-pronged brass candelabra. Emits a warm, golden illumination.",
        "lore": "'Wax, wick, and gold—a beacon in the underground gloom.'",
        "special": "Luminous Homestead Light"
    },
    "chandelier": {
        "name": "Chandelier", "cat": CAT_BLOCK, "power": 0, "damage": 0, "max_stack": 99, "tile": TILE_CHANDELIER,
        "rarity": RARITY_RARE,
        "desc": "Grand hanging ceiling chandelier fitted with four glowing candles.",
        "lore": "'Cast brilliant banquet light over your majestic earthen hall.'",
        "special": "Brilliant Ceiling Illumination"
    },
    "potted_plant": {
        "name": "Potted Spud Plant", "cat": CAT_BLOCK, "power": 0, "damage": 0, "max_stack": 99, "tile": TILE_POTTED_PLANT,
        "rarity": RARITY_COMMON,
        "desc": "A terracotta pot nurturing a lush miniature leafy potato bonsai.",
        "lore": "'A thriving green sprout that brings life to any homestead.'",
        "special": "Decorative Botanical Bonsai"
    },
    "wooden_dresser": {
        "name": "Wooden Dresser", "cat": CAT_BLOCK, "power": 0, "damage": 0, "max_stack": 99, "tile": TILE_DRESSER,
        "rarity": RARITY_UNCOMMON,
        "desc": "Carved wooden dresser with brass pull handles and polished top shelf.",
        "lore": "'Keeps clothes, starch aprons, and cloaks folded and fresh.'",
        "special": "Platform Surface & Wardrobe Decor"
    },
    "wall_tapestry": {
        "name": "Wall Tapestry", "cat": CAT_BLOCK, "power": 0, "damage": 0, "max_stack": 99, "tile": TILE_TAPESTRY,
        "rarity": RARITY_UNCOMMON,
        "desc": "Woven decorative banner depicting the Golden Spud of legend.",
        "lore": "'Woven from silken threads to honor the ancient tuber deities.'",
        "special": "Decorative Wall Ornament"
    },
    "bathtub": {
        "name": "Bathtub", "cat": CAT_BLOCK, "power": 0, "damage": 0, "max_stack": 99, "tile": TILE_BATHTUB,
        "rarity": RARITY_UNCOMMON,
        "desc": "Porcelain-enameled tub filled with warm, soothing bubble water.",
        "lore": "'Wash away the dungeon grime and soothe tired potato peelings.'",
        "special": "Homestead Luxury Furniture"
    },
    "sink": {
        "name": "Sink", "cat": CAT_BLOCK, "power": 0, "damage": 0, "max_stack": 99, "tile": TILE_SINK,
        "rarity": RARITY_UNCOMMON,
        "desc": "Brass-faucet washbasin mounted on a carved wooden cabinet.",
        "lore": "'Fresh flowing water for handwashing and culinary preparation.'",
        "special": "Homestead Plumbing & Platform"
    },
    "painting": {
        "name": "Painting", "cat": CAT_BLOCK, "power": 0, "damage": 0, "max_stack": 99, "tile": TILE_PAINTING,
        "rarity": RARITY_RARE,
        "desc": "Gilded framed oil landscape portraying rolling potato hills under a sunset.",
        "lore": "'A masterpiece brushed with potato starch oil by Master Kurados.'",
        "special": "Fine Wall Art"
    },
    "wood_shelf": {
        "name": "Wood Shelf", "cat": CAT_BLOCK, "power": 0, "damage": 0, "max_stack": 99, "tile": TILE_WOOD_SHELF,
        "rarity": RARITY_COMMON,
        "desc": "Smooth wooden wall shelf. Allows Spud to jump up through and stand upon it.",
        "lore": "'Sturdy timber bracketed to hold jars, books, and curious spuds.'",
        "special": "Jump-Through Platform Surface"
    },
    "bed": {
        "name": "Bed", "cat": CAT_BLOCK, "power": 0, "damage": 0, "max_stack": 99, "tile": TILE_BED,
        "rarity": RARITY_UNCOMMON,
        "desc": "Simple wooden bed. Right-click to set spawn point and rest to recover health.",
        "lore": "'A humble cot fashioned from dry timber and clean sheets.'",
        "special": "Sets Respawn Point & Rest Recovery"
    },
    "fireplace": {
        "name": "Fireplace", "cat": CAT_BLOCK, "power": 0, "damage": 0, "max_stack": 99, "tile": TILE_FIREPLACE,
        "rarity": RARITY_RARE,
        "desc": "Warm masonry fireplace with an arched hearth. Radiates cozy heat and light.",
        "lore": "'Crackling flames keep the darkness and cold away from your abode.'",
        "special": "Warm Ambient Light & Rising Smoke"
    },
    "hearth": {
        "name": "Cozy Hearth", "cat": CAT_BLOCK, "power": 0, "damage": 0, "max_stack": 99, "tile": TILE_FIREPLACE,
        "rarity": RARITY_RARE,
        "desc": "Open stone hearth radiating soothing heat across the homestead.",
        "lore": "'The warm beating heart of any cozy potato home.'",
        "special": "Warm Ambient Light & Rising Smoke"
    },
    "dresser": {
        "name": "Dresser", "cat": CAT_BLOCK, "power": 0, "damage": 0, "max_stack": 99, "tile": TILE_DRESSER,
        "rarity": RARITY_UNCOMMON,
        "desc": "Carved wooden dressing chest with brass pull handles and slide-out drawers.",
        "lore": "'Neatly stores potato skins and fine tunics.'",
        "special": "Platform Surface & Wardrobe Decor"
    },
    "wardrobe": {
        "name": "Wardrobe", "cat": CAT_BLOCK, "power": 0, "damage": 0, "max_stack": 99, "tile": TILE_DRESSER,
        "rarity": RARITY_UNCOMMON,
        "desc": "Upright timber wardrobe with twin doors for hanging cloaks and attire.",
        "lore": "'A tall cupboard keeping garments safe from dungeon dust.'",
        "special": "Platform Surface & Wardrobe Decor"
    },
    "clock": {
        "name": "Clock", "cat": CAT_BLOCK, "power": 0, "damage": 0, "max_stack": 99, "tile": TILE_GRANDFATHER_CLOCK,
        "rarity": RARITY_RARE,
        "desc": "Decorative ticking wall clock keeping celestial time.",
        "lore": "'Marking every hour of your grand Potarian journey.'",
        "special": "Interactive Celestial Timekeeper"
    },
    "shelf": {
        "name": "Shelf", "cat": CAT_BLOCK, "power": 0, "damage": 0, "max_stack": 99, "tile": TILE_WOOD_SHELF,
        "rarity": RARITY_COMMON,
        "desc": "Smooth wall-mounted wooden shelf for displaying keepsakes.",
        "lore": "'A simple wooden perch that also serves as a jumping ledge.'",
        "special": "Jump-Through Platform Surface"
    },
    "art": {
        "name": "Art", "cat": CAT_BLOCK, "power": 0, "damage": 0, "max_stack": 99, "tile": TILE_PAINTING,
        "rarity": RARITY_RARE,
        "desc": "Charming canvas sketch capturing pastoral countryside views.",
        "lore": "'Drawn by an inspired tuber artist of old.'",
        "special": "Fine Wall Art"
    },
    "wall_art": {
        "name": "Wall Art", "cat": CAT_BLOCK, "power": 0, "damage": 0, "max_stack": 99, "tile": TILE_PAINTING,
        "rarity": RARITY_RARE,
        "desc": "Vibrant decorative wall plaque honoring ancient tuber legends.",
        "lore": "'Inspiring artwork adorning the halls of Potaria.'",
        "special": "Fine Wall Art"
    },
    "plant": {
        "name": "Plant", "cat": CAT_BLOCK, "power": 0, "damage": 0, "max_stack": 99, "tile": TILE_POTTED_PLANT,
        "rarity": RARITY_COMMON,
        "desc": "Fresh leafy houseplant in an earthenware pot.",
        "lore": "'A touch of green life inside your underground refuge.'",
        "special": "Decorative Botanical Bonsai"
    },
    "bonsai": {
        "name": "Bonsai", "cat": CAT_BLOCK, "power": 0, "damage": 0, "max_stack": 99, "tile": TILE_POTTED_PLANT,
        "rarity": RARITY_COMMON,
        "desc": "Meticulously pruned miniature potato bonsai in a decorative dish.",
        "lore": "'A tranquil miniature tree nurtured with patience.'",
        "special": "Decorative Botanical Bonsai"
    },
    "potted_spud_plant": {
        "name": "Potted Spud Plant", "cat": CAT_BLOCK, "power": 0, "damage": 0, "max_stack": 99, "tile": TILE_POTTED_PLANT,
        "rarity": RARITY_COMMON,
        "desc": "Cultivated domestic spud sprout potted in rich compost.",
        "lore": "'Sprouting fresh leafy greens to purify the subterranean air.'",
        "special": "Decorative Botanical Bonsai"
    },
    "banner": {
        "name": "Banner", "cat": CAT_BLOCK, "power": 0, "damage": 0, "max_stack": 99, "tile": TILE_TAPESTRY,
        "rarity": RARITY_UNCOMMON,
        "desc": "Long colorful hanging banner bearing the royal seal of Potaria.",
        "lore": "'Flutters with pride in the homestead halls.'",
        "special": "Decorative Wall Ornament"
    },
    "tapestry": {
        "name": "Tapestry", "cat": CAT_BLOCK, "power": 0, "damage": 0, "max_stack": 99, "tile": TILE_TAPESTRY,
        "rarity": RARITY_UNCOMMON,
        "desc": "Intricate decorative textile hanging woven from soft spud silk.",
        "lore": "'A majestic woven scene depicting ancient potato lore.'",
        "special": "Decorative Wall Ornament"
    },
    "wood_sword": {
        "name": "Wooden Sword", "cat": CAT_WEAPON, "damage": 3, "atk": 7, "power": 10, "speed": 1.0, "max_stack": 1, "tile": None,
        "rarity": RARITY_COMMON,
        "desc": "Whittled wooden practice blade. Essential starter weapon for aspiring spud warriors.",
        "lore": "'Carved from sturdy surface oak to defend against roaming garden pests.'",
        "special": ""
    },
    "arrow": {
        "name": "Arrow", "cat": CAT_CONSUMABLE, "damage": 4, "max_stack": 999, "tile": None,
        "rarity": RARITY_COMMON,
        "desc": "Standard notched arrow tipped with pointed flint.",
        "lore": "'Reliable basic ammunition for wooden bows.'",
        "special": "Bow Ammunition"
    },
    "curved_tuber_lantern": {
        "name": "Curved Tuber Lantern", "cat": CAT_BLOCK, "power": 0, "damage": 0, "max_stack": 99, "tile": TILE_CARVED_TUBER_LANTERN,
        "rarity": RARITY_UNCOMMON,
        "desc": "Artfully sculpted root lantern casting curved beams of warm light.",
        "lore": "'A decorative hanging root light providing warm amber illumination.'",
        "special": "Warm Amber Light Source"
    },
    "wood_wall": {
        "name": "Wood Wall", "cat": CAT_WALL, "wall": WALL_WOOD, "power": 0, "damage": 0, "max_stack": 999, "tile": None,
        "rarity": RARITY_COMMON,
        "desc": "Place in the background to build secure, monster-proof rooms.",
        "lore": "'Encloses homes so foul beasts cannot spawn within.'",
        "special": "Background Safe-House Wall"
    },
    "stone_brick_wall": {
        "name": "Stone Brick Wall", "cat": CAT_WALL, "wall": WALL_STONE_BRICK, "power": 0, "damage": 0, "max_stack": 999, "tile": None,
        "rarity": RARITY_COMMON,
        "desc": "Heavy reinforced masonry backdrop for fortresses and castles.",
        "lore": "'Ancient stone forged to withstand the Nether depths.'",
        "special": "Background Safe-House Wall"
    },

    # ----------------------------------------------------
    # Food & Healing Consumables
    # ----------------------------------------------------
    "raw_potato": {
        "name": "Raw Potato", "cat": CAT_CONSUMABLE, "power": 0, "damage": 0, "heal": 25, "max_stack": 99, "tile": None,
        "rarity": RARITY_COMMON,
        "desc": "Crisp subterranean tuber. Right-click to consume for +25 HP or cook in a furnace.",
        "lore": "'Earthy, humble, and packed with wholesome vitality.'",
        "special": "Restores 25 Health"
    },
    "mashed_potato": {
        "name": "Mashed Potato Meal", "cat": CAT_CONSUMABLE, "power": 0, "damage": 0, "heal": 60, "max_stack": 99, "tile": None,
        "rarity": RARITY_UNCOMMON,
        "desc": "Cooked at a furnace. Hearty creamy meal that restores +60 HP.",
        "lore": "'Comfort food that warms the core of any weary potato hero.'",
        "special": "Restores 60 Health"
    },
    "golden_fry": {
        "name": "Golden French Fry", "cat": CAT_CONSUMABLE, "power": 0, "damage": 0, "heal": 100, "max_stack": 99, "tile": None,
        "rarity": RARITY_RARE,
        "desc": "Crispy golden fry seasoned with gold dust. Restores +100 HP.",
        "lore": "'Crisped to golden perfection. Legendary culinary triumph.'",
        "special": "Restores 100 Health"
    },
    "healing_potion": {
        "name": "Lesser Healing Potion", "cat": CAT_CONSUMABLE, "power": 0, "damage": 0, "heal": 50, "max_stack": 30, "tile": None,
        "rarity": RARITY_COMMON,
        "desc": "Alchemical brew. Right-click to instantly recover +50 HP.",
        "lore": "'Standard issue emergency drought for spelunkers.'",
        "special": "Restores 50 Health"
    },
    "greater_healing_potion": {
        "name": "Greater Healing Potion", "cat": CAT_CONSUMABLE, "power": 0, "damage": 0, "heal": 120, "max_stack": 30, "tile": None,
        "rarity": RARITY_RARE,
        "desc": "Distilled glowing mushroom tonic. Instantly heals +120 HP.",
        "lore": "'Potent alchemical life-water that seals deep wounds.'",
        "special": "Restores 120 Health"
    },
    "speed_potion": {
        "name": "Swiftness Potion", "cat": CAT_CONSUMABLE, "power": 0, "damage": 0, "heal": 0, "max_stack": 30, "tile": None,
        "rarity": RARITY_UNCOMMON,
        "desc": "Effervescent tonic granting temporary hyper-speed.",
        "lore": "'Makes your roots move faster than a subterranean river.'",
        "special": "+30% Sprint Speed Boost"
    },
    "apple": {
        "name": "Crisp Apple", "cat": CAT_CONSUMABLE, "power": 0, "damage": 0, "heal": 15, "max_stack": 99, "tile": None,
        "rarity": RARITY_COMMON,
        "desc": "A juicy red apple shaken free from tree canopies. Right-click to consume for +15 HP.",
        "lore": "'Freshly harvested from surface orchard canopies.'",
        "special": "Restores 15 Health"
    },
    "bomb": {
        "name": "Excavation Bomb", "cat": CAT_CONSUMABLE, "power": 0, "damage": 0, "max_stack": 99, "tile": None,
        "rarity": RARITY_COMMON,
        "desc": "A volatile demolition charge sold by Blacksmith Russet. Blows away dense subterranean rock formations.",
        "lore": "'Handle with care. Packed with explosive blasting powder.'",
        "special": "Excavation Explosive"
    },
    # ----------------------------------------------------
    # Fishing Gear & Authentic Pinoy Fishes
    # ----------------------------------------------------
    "fishing_rod": {
        "name": "Bamboo Fishing Rod", "cat": CAT_TOOL, "power": 10, "damage": 2, "max_stack": 1, "tile": None,
        "rarity": RARITY_COMMON,
        "desc": "A flexible bamboo pole fitted with strong fiber line. Cast into water to catch Pinoy fish.",
        "lore": "'Patience brings the ocean's bounty.'",
        "special": "Fishing Tool"
    },
    "reinforced_angler_rod": {
        "name": "Reinforced Iron Angler Rod", "cat": CAT_TOOL, "power": 20, "damage": 5, "max_stack": 1, "tile": None,
        "rarity": RARITY_RARE,
        "desc": "Tempered iron casting rod with weighted spool. Catches rare deep-water fish and precious treasures.",
        "lore": "'Cast deep where the sunken relics rest.'",
        "special": "Fishing Tool"
    },
    "gilded_master_rod": {
        "name": "Gilded Master Angler Rod", "cat": CAT_TOOL, "power": 35, "damage": 8, "max_stack": 1, "tile": None,
        "rarity": RARITY_EPIC,
        "desc": "Masterwork golden fishing rod lined with silk filament. Can reel in exotic catches and epic equipment.",
        "lore": "'A true angler seeks legends beneath the foam.'",
        "special": "Fishing Tool"
    },
    "astral_leviathan_rod": {
        "name": "Astral Leviathan Rod", "cat": CAT_TOOL, "power": 50, "damage": 12, "max_stack": 1, "tile": None,
        "rarity": RARITY_MYTHIC,
        "desc": "Celestial carbon-weave rod hums with cosmic tides. Capable of catching mythical ocean titans and royal treasure.",
        "lore": "'The abyss yields its greatest secrets to celestial craft.'",
        "special": "Fishing Tool"
    },
    "neptune_tide_rod": {
        "name": "Neptune's Sovereign Rod", "cat": CAT_TOOL, "power": 70, "damage": 18, "max_stack": 1, "tile": None,
        "rarity": RARITY_LEGENDARY,
        "desc": "Legendary sovereign trident-rod commanding the tides. Reqs supreme mastery to reel mythical relics.",
        "lore": "'Rule the waters, harvest the boundless cosmos.'",
        "special": "Fishing Tool"
    },
    "raw_bangus": {
        "name": "Bangus", "cat": CAT_CONSUMABLE, "power": 0, "damage": 0, "heal": 15, "max_stack": 99, "tile": None,
        "rarity": RARITY_COMMON,
        "desc": "National silvery fish of Potaria, prized for its tender belly. Best cooked before eating.",
        "lore": "'Known as the milkfish, glistening with silver scales.'",
        "special": "Raw Fish (Restores 15 HP)"
    },
    "raw_tilapia": {
        "name": "Tilapia", "cat": CAT_CONSUMABLE, "power": 0, "damage": 0, "heal": 12, "max_stack": 99, "tile": None,
        "rarity": RARITY_COMMON,
        "desc": "Freshwater cichlid with hardy scales, thriving in inland streams. Cook over fire.",
        "lore": "'Hardy and abundant in freshwater streams.'",
        "special": "Raw Fish (Restores 12 HP)"
    },
    "raw_galunggong": {
        "name": "Galunggong", "cat": CAT_CONSUMABLE, "power": 0, "damage": 0, "heal": 10, "max_stack": 99, "tile": None,
        "rarity": RARITY_COMMON,
        "desc": "Round scad, the beloved everyday staple fish with rich flavor.",
        "lore": "'The people's fish, found schooling across coastal reefs.'",
        "special": "Raw Fish (Restores 10 HP)"
    },
    "raw_maya_maya": {
        "name": "Maya-Maya", "cat": CAT_CONSUMABLE, "power": 0, "damage": 0, "heal": 20, "max_stack": 99, "tile": None,
        "rarity": RARITY_UNCOMMON,
        "desc": "Vibrant red snapper found patrolling deep rocky reefs.",
        "lore": "'Fiery crimson snapper prized in traditional stews.'",
        "special": "Raw Fish (Restores 20 HP)"
    },
    "raw_tanigue": {
        "name": "Tanigue", "cat": CAT_CONSUMABLE, "power": 0, "damage": 0, "heal": 25, "max_stack": 99, "tile": None,
        "rarity": RARITY_RARE,
        "desc": "Sleek Spanish mackerel with firm, prized steaks.",
        "lore": "'Swift pelagic predator of open azure waters.'",
        "special": "Raw Fish (Restores 25 HP)"
    },
    "raw_tambakol": {
        "name": "Tambakol", "cat": CAT_CONSUMABLE, "power": 0, "damage": 0, "heal": 22, "max_stack": 99, "tile": None,
        "rarity": RARITY_UNCOMMON,
        "desc": "Yellowfin tuna relative with deep crimson flesh and powerful fins.",
        "lore": "'Powerful ocean swimmer with rich, meaty loins.'",
        "special": "Raw Fish (Restores 22 HP)"
    },
    "raw_lapu_lapu": {
        "name": "Lapu-Lapu", "cat": CAT_CONSUMABLE, "power": 0, "damage": 0, "heal": 28, "max_stack": 99, "tile": None,
        "rarity": RARITY_RARE,
        "desc": "Esteemed spotted reef grouper named after the brave chieftain warrior.",
        "lore": "'King of coral reefs, renowned for delicate white meat.'",
        "special": "Raw Fish (Restores 28 HP)"
    },
    "raw_hito": {
        "name": "Hito", "cat": CAT_CONSUMABLE, "power": 0, "damage": 0, "heal": 16, "max_stack": 99, "tile": None,
        "rarity": RARITY_COMMON,
        "desc": "Whiskered freshwater catfish dwelling in muddy bottoms and waterways.",
        "lore": "'Slippery bottom-dweller with keen barbels.'",
        "special": "Raw Fish (Restores 16 HP)"
    },
    "raw_dilis": {
        "name": "Dilis", "cat": CAT_CONSUMABLE, "power": 0, "damage": 0, "heal": 8, "max_stack": 99, "tile": None,
        "rarity": RARITY_COMMON,
        "desc": "Tiny anchovies swimming in shimmering schools along shores.",
        "lore": "'Small yet bursting with mineral flavor when dried or fried.'",
        "special": "Raw Fish (Restores 8 HP)"
    },
    "raw_dalagang_bukid": {
        "name": "Dalagang Bukid", "cat": CAT_CONSUMABLE, "power": 0, "damage": 0, "heal": 15, "max_stack": 99, "tile": None,
        "rarity": RARITY_UNCOMMON,
        "desc": "Yellowtail fusilier with radiant crimson-gold scales.",
        "lore": "'Named maiden of the field for its vibrant colorful robes.'",
        "special": "Raw Fish (Restores 15 HP)"
    },
    "cooked_bangus": {
        "name": "Inihaw na Bangus", "cat": CAT_CONSUMABLE, "power": 0, "damage": 0, "heal": 65, "max_stack": 99, "tile": None,
        "rarity": RARITY_UNCOMMON,
        "desc": "Charcoal-grilled milkfish stuffed with tomatoes and onions. Restores 65 HP.",
        "lore": "'Succulent belly grilled over coconut charcoal.'",
        "special": "Restores 65 Health"
    },
    "cooked_tilapia": {
        "name": "Pritong Tilapia", "cat": CAT_CONSUMABLE, "power": 0, "damage": 0, "heal": 50, "max_stack": 99, "tile": None,
        "rarity": RARITY_COMMON,
        "desc": "Crispy fried whole tilapia seasoned with sea salt. Restores 50 HP.",
        "lore": "'Crisp, crunchy skin with steaming tender flakes.'",
        "special": "Restores 50 Health"
    },
    "cooked_galunggong": {
        "name": "Pritong Galunggong", "cat": CAT_CONSUMABLE, "power": 0, "damage": 0, "heal": 45, "max_stack": 99, "tile": None,
        "rarity": RARITY_COMMON,
        "desc": "Deep-fried round scad paired with spicy vinegar dipping. Restores 45 HP.",
        "lore": "'The golden fried staple of everyday adventurers.'",
        "special": "Restores 45 Health"
    },
    "cooked_maya_maya": {
        "name": "Sinigang na Maya-Maya", "cat": CAT_CONSUMABLE, "power": 0, "damage": 0, "heal": 80, "max_stack": 99, "tile": None,
        "rarity": RARITY_RARE,
        "desc": "Tamarind-sour savory soup with red snapper. Restores 80 HP.",
        "lore": "'Invigorating sour broth that cures fatigue instantly.'",
        "special": "Restores 80 Health"
    },
    "cooked_tanigue": {
        "name": "Kinilaw na Tanigue", "cat": CAT_CONSUMABLE, "power": 0, "damage": 0, "heal": 90, "max_stack": 99, "tile": None,
        "rarity": RARITY_RARE,
        "desc": "Citrus and coconut vinegar cured Spanish mackerel ceviche. Restores 90 HP.",
        "lore": "'Infused with ginger and calamansi for peak vigor.'",
        "special": "Restores 90 Health"
    },
    "cooked_tambakol": {
        "name": "Inihaw na Tambakol", "cat": CAT_CONSUMABLE, "power": 0, "damage": 0, "heal": 85, "max_stack": 99, "tile": None,
        "rarity": RARITY_UNCOMMON,
        "desc": "Flame-broiled yellowfin steaks basted in sweet soy glaze. Restores 85 HP.",
        "lore": "'Dense hearty tuna steak with rich smokiness.'",
        "special": "Restores 85 Health"
    },
    "cooked_lapu_lapu": {
        "name": "Pasingaw na Lapu-Lapu", "cat": CAT_CONSUMABLE, "power": 0, "damage": 0, "heal": 110, "max_stack": 99, "tile": None,
        "rarity": RARITY_EPIC,
        "desc": "Ginger-steamed grouper dressed in sesame soy sauce. Restores 110 HP.",
        "lore": "'Royalty-grade feast that fortifies the body.'",
        "special": "Restores 110 Health"
    },
    "cooked_hito": {
        "name": "Adobong Hito", "cat": CAT_CONSUMABLE, "power": 0, "damage": 0, "heal": 70, "max_stack": 99, "tile": None,
        "rarity": RARITY_COMMON,
        "desc": "Catfish simmered in garlic, vinegar, and black peppercorns. Restores 70 HP.",
        "lore": "'Savory adobo sauce tenderizes rich catfish.'",
        "special": "Restores 70 Health"
    },
    "cooked_dilis": {
        "name": "Pritong Dilis", "cat": CAT_CONSUMABLE, "power": 0, "damage": 0, "heal": 35, "max_stack": 99, "tile": None,
        "rarity": RARITY_COMMON,
        "desc": "Glazed crunchy sweet-and-spicy dried anchovies. Restores 35 HP.",
        "lore": "'Irresistible crunchy snack for long cavern treks.'",
        "special": "Restores 35 Health"
    },
    "cooked_dalagang_bukid": {
        "name": "Pritong Dalagang Bukid", "cat": CAT_CONSUMABLE, "power": 0, "damage": 0, "heal": 60, "max_stack": 99, "tile": None,
        "rarity": RARITY_UNCOMMON,
        "desc": "Crispy pan-fried yellowtail fusilier with golden crust. Restores 60 HP.",
        "lore": "'Golden savory fish loved at every gathering.'",
        "special": "Restores 60 Health"
    },
    # ----------------------------------------------------
    # Recyclable Fishing Junk & River Debris
    # ----------------------------------------------------
    "dirt_clod": {
        "name": "Dirt Clod", "cat": CAT_MATERIAL, "power": 0, "damage": 0, "max_stack": 99, "tile": None,
        "rarity": RARITY_COMMON,
        "desc": "A clump of damp river mud and loose silt pulled up on a fishing line.",
        "lore": "'No practical use on its own, but can be recycled or potted.'",
        "special": "Recyclable Fishing Junk"
    },
    "old_boot": {
        "name": "Waterlogged Boot", "cat": CAT_MATERIAL, "power": 0, "damage": 0, "max_stack": 99, "tile": None,
        "rarity": RARITY_COMMON,
        "desc": "A soggy, worn leather boot hooked from the seabed. Smells like algae.",
        "lore": "'Someone was missing their left footwear.'",
        "special": "Recyclable Fishing Junk"
    },
    "rusty_can": {
        "name": "Rusty Tin Can", "cat": CAT_MATERIAL, "power": 0, "damage": 0, "max_stack": 99, "tile": None,
        "rarity": RARITY_COMMON,
        "desc": "An oxidized tin can discarded into the river long ago.",
        "lore": "'Corroded by the tides.'",
        "special": "Recyclable Fishing Junk"
    },
    "seaweed": {
        "name": "Tangled Seaweed", "cat": CAT_MATERIAL, "power": 0, "damage": 0, "max_stack": 99, "tile": None,
        "rarity": RARITY_COMMON,
        "desc": "Briny dark green kelp ribbons harvested from coastal waters.",
        "lore": "'Rich in oceanic minerals; can be dried or recycled.'",
        "special": "Recyclable Fishing Junk"
    },
    "driftwood": {
        "name": "Weathered Driftwood", "cat": CAT_MATERIAL, "power": 0, "damage": 0, "max_stack": 99, "tile": None,
        "rarity": RARITY_COMMON,
        "desc": "Salt-bleached smooth timber branch floating among the river reeds.",
        "lore": "'Shaped and softened by river currents.'",
        "special": "Recyclable Fishing Junk"
    },

    # ----------------------------------------------------
    # Filipino Land Animals - Poultry, Livestock & Produce
    # ----------------------------------------------------
    "raw_chicken": {
        "name": "Native Chicken Meat", "cat": CAT_CONSUMABLE, "power": 0, "damage": 0, "heal": 16, "max_stack": 99, "tile": None,
        "rarity": RARITY_COMMON,
        "desc": "Fresh native poultry cut. Lean and flavorful, best stewed in adobo or tinola.",
        "lore": "'Prized Philippine free-range fowl.'",
        "special": "Restores 16 Health"
    },
    "raw_duck_meat": {
        "name": "Native Duck Meat", "cat": CAT_CONSUMABLE, "power": 0, "damage": 0, "heal": 18, "max_stack": 99, "tile": None,
        "rarity": RARITY_COMMON,
        "desc": "Rich, tender dark meat from free-range Pateros duck.",
        "lore": "'Hearty poultry favored for braised delicacies.'",
        "special": "Restores 18 Health"
    },
    "duck_egg": {
        "name": "Itik Duck Egg", "cat": CAT_CONSUMABLE, "power": 0, "damage": 0, "heal": 12, "max_stack": 99, "tile": None,
        "rarity": RARITY_COMMON,
        "desc": "Thick-shelled duck egg, key ingredient for Balut and Itlog na Maalat.",
        "lore": "'Rich yolk with velvety texture.'",
        "special": "Restores 12 Health"
    },
    "egg": {
        "name": "Native Hen Egg", "cat": CAT_CONSUMABLE, "power": 0, "damage": 0, "heal": 10, "max_stack": 99, "tile": None,
        "rarity": RARITY_COMMON,
        "desc": "Farm fresh native chicken egg with deep golden yolk.",
        "lore": "'Wholesome breakfast staple.'",
        "special": "Restores 10 Health"
    },
    "raw_pork": {
        "name": "Native Pork Cut", "cat": CAT_CONSUMABLE, "power": 0, "damage": 0, "heal": 20, "max_stack": 99, "tile": None,
        "rarity": RARITY_COMMON,
        "desc": "Succulent cut of native black pig. Essential for classic pork adobo and sinigang.",
        "lore": "'Naturally flavorful native swine meat.'",
        "special": "Restores 20 Health"
    },
    "pork_belly": {
        "name": "Liempo Pork Belly", "cat": CAT_CONSUMABLE, "power": 0, "damage": 0, "heal": 25, "max_stack": 99, "tile": None,
        "rarity": RARITY_UNCOMMON,
        "desc": "Layered fatty pork belly slab, prime cut for crispy lechon kawali.",
        "lore": "'Golden crackling skin and tender juicy fat.'",
        "special": "Restores 25 Health"
    },
    "raw_beef": {
        "name": "Bulalo Beef Shank", "cat": CAT_CONSUMABLE, "power": 0, "damage": 0, "heal": 28, "max_stack": 99, "tile": None,
        "rarity": RARITY_UNCOMMON,
        "desc": "Meaty beef shank bone with rich marrow center from native carabao.",
        "lore": "'The soul of hearty Sunday stews.'",
        "special": "Restores 28 Health"
    },
    "carabao_milk": {
        "name": "Fresh Carabao Milk", "cat": CAT_CONSUMABLE, "power": 0, "damage": 0, "heal": 35, "max_stack": 99, "tile": None,
        "rarity": RARITY_UNCOMMON,
        "desc": "Rich, creamy milk from Philippine water buffalo. High in butterfat.",
        "lore": "'Pure white milk prized for making pastillas and cheese.'",
        "special": "Restores 35 Health"
    },
    "raw_goat_meat": {
        "name": "Native Goat Meat", "cat": CAT_CONSUMABLE, "power": 0, "damage": 0, "heal": 24, "max_stack": 99, "tile": None,
        "rarity": RARITY_UNCOMMON,
        "desc": "Lean, aromatic goat meat cut, traditional centerpiece for Kaldereta.",
        "lore": "'Tenderized with spiced aromatics.'",
        "special": "Restores 24 Health"
    },
    "goat_milk": {
        "name": "Native Goat Milk", "cat": CAT_CONSUMABLE, "power": 0, "damage": 0, "heal": 28, "max_stack": 99, "tile": None,
        "rarity": RARITY_COMMON,
        "desc": "Easily digestible rich milk from native Philippine goats.",
        "lore": "'Nutrient-dense nourishing drink.'",
        "special": "Restores 28 Health"
    },
    "feather": {
        "name": "Poultry Feather", "cat": CAT_MATERIAL, "power": 0, "damage": 0, "max_stack": 999, "tile": None,
        "rarity": RARITY_COMMON,
        "desc": "Iridescent lightweight feather shed by native fowl. Useful for fletching arrows.",
        "lore": "'Glides effortlessly on thermal drafts.'",
        "special": "Crafting Material"
    },

    # ----------------------------------------------------
    # Filipino Cooking Spices & Produce Ingredients
    # ----------------------------------------------------
    "garlic": {
        "name": "Bawang Garlic", "cat": CAT_MATERIAL, "power": 0, "damage": 0, "max_stack": 99, "tile": None,
        "rarity": RARITY_COMMON,
        "desc": "Pungent native garlic cloves. The aromatic foundation of Filipino cuisine.",
        "lore": "'Said to ward off Aswang and evil spirits.'",
        "special": "Cooking Ingredient"
    },
    "onion": {
        "name": "Sibuyas Red Onion", "cat": CAT_MATERIAL, "power": 0, "damage": 0, "max_stack": 99, "tile": None,
        "rarity": RARITY_COMMON,
        "desc": "Sweet, vibrant red onion bulbs essential for sauteing.",
        "lore": "'Sizzles aromatically in the pan.'",
        "special": "Cooking Ingredient"
    },
    "ginger": {
        "name": "Luya Fresh Ginger", "cat": CAT_MATERIAL, "power": 0, "damage": 0, "max_stack": 99, "tile": None,
        "rarity": RARITY_COMMON,
        "desc": "Zesty, warming ginger root that infuses tinola and arroz caldo broth.",
        "lore": "'Soothes sore throats and warms the stomach.'",
        "special": "Cooking Ingredient"
    },
    "calamansi": {
        "name": "Calamansi Citrus", "cat": CAT_CONSUMABLE, "power": 0, "damage": 0, "heal": 10, "max_stack": 99, "tile": None,
        "rarity": RARITY_COMMON,
        "desc": "Tart and aromatic Philippine lime. Adds bright acidity to dipping sauces.",
        "lore": "'Nature's zestiest vitamin booster.'",
        "special": "Restores 10 Health"
    },
    "tamarind": {
        "name": "Sampalok Tamarind", "cat": CAT_MATERIAL, "power": 0, "damage": 0, "max_stack": 99, "tile": None,
        "rarity": RARITY_COMMON,
        "desc": "Tangy tamarind pods that give Sinigang its signature appetizing sourness.",
        "lore": "'Puckers the lips with mouth-watering sourness.'",
        "special": "Cooking Ingredient"
    },
    "soy_sauce": {
        "name": "Toyo Soy Sauce", "cat": CAT_MATERIAL, "power": 0, "damage": 0, "max_stack": 99, "tile": None,
        "rarity": RARITY_COMMON,
        "desc": "Fermented rich black soy sauce. Savory cornerstone of adobo.",
        "lore": "'Deep umami aged in wooden vats.'",
        "special": "Cooking Ingredient"
    },
    "vinegar": {
        "name": "Sukang Paombong Vinegar", "cat": CAT_MATERIAL, "power": 0, "damage": 0, "max_stack": 99, "tile": None,
        "rarity": RARITY_COMMON,
        "desc": "Traditional cane and palm vinegar with sharp, clean tartness.",
        "lore": "'Naturally preserves and balances savory meat dishes.'",
        "special": "Cooking Ingredient"
    },
    "black_pepper": {
        "name": "Paminta Peppercorns", "cat": CAT_MATERIAL, "power": 0, "damage": 0, "max_stack": 99, "tile": None,
        "rarity": RARITY_COMMON,
        "desc": "Whole black peppercorns from aromatic spice groves.",
        "lore": "'Packs gentle biting heat and aroma.'",
        "special": "Cooking Ingredient"
    },
    "salt": {
        "name": "Asin Sea Salt", "cat": CAT_MATERIAL, "power": 0, "damage": 0, "max_stack": 99, "tile": None,
        "rarity": RARITY_COMMON,
        "desc": "Pure crystallized white sea salt harvested from coastal pans.",
        "lore": "'Brings out every hidden nuance of flavor.'",
        "special": "Cooking Ingredient"
    },
    "rice": {
        "name": "Milagrosa White Rice", "cat": CAT_MATERIAL, "power": 0, "damage": 0, "max_stack": 99, "tile": None,
        "rarity": RARITY_COMMON,
        "desc": "Fragrant polished grain. A meal in Potaria is never complete without rice.",
        "lore": "'The heartbeat of every dining table.'",
        "special": "Cooking Ingredient"
    },
    "coconut_milk": {
        "name": "Gata Coconut Milk", "cat": CAT_CONSUMABLE, "power": 0, "damage": 0, "heal": 20, "max_stack": 99, "tile": None,
        "rarity": RARITY_COMMON,
        "desc": "Rich, velvety cream pressed from freshly grated mature coconut meat.",
        "lore": "'Adds luxurious silkiness to coastal curries.'",
        "special": "Cooking Ingredient"
    },
    "peanut_butter": {
        "name": "Ground Peanut Butter", "cat": CAT_CONSUMABLE, "power": 0, "damage": 0, "heal": 22, "max_stack": 99, "tile": None,
        "rarity": RARITY_COMMON,
        "desc": "Savory roasted peanut paste that thickens luscious Kare-Kare sauce.",
        "lore": "'Warm, nutty aroma beloved by all.'",
        "special": "Cooking Ingredient"
    },
    "eggplant": {
        "name": "Talong Native Eggplant", "cat": CAT_CONSUMABLE, "power": 0, "damage": 0, "heal": 12, "max_stack": 99, "tile": None,
        "rarity": RARITY_COMMON,
        "desc": "Glossy purple tender eggplant, key vegetable for Sinigang and Tortang Talong.",
        "lore": "'Soaks up rich broths like a sponge.'",
        "special": "Cooking Ingredient"
    },
    "string_beans": {
        "name": "Sitaw String Beans", "cat": CAT_CONSUMABLE, "power": 0, "damage": 0, "heal": 12, "max_stack": 99, "tile": None,
        "rarity": RARITY_COMMON,
        "desc": "Crisp green yardlong beans harvested fresh from farm trellises.",
        "lore": "'Snaps with sweet, vegetal freshness.'",
        "special": "Cooking Ingredient"
    },
    "pancit_noodles": {
        "name": "Bihon Rice Noodles", "cat": CAT_MATERIAL, "power": 0, "damage": 0, "max_stack": 99, "tile": None,
        "rarity": RARITY_COMMON,
        "desc": "Delicate sun-dried translucent rice noodles. Symbolizes long life and health.",
        "lore": "'Stir-fried for celebrations and good fortune.'",
        "special": "Cooking Ingredient"
    },
    "shaved_ice": {
        "name": "Yelo Shaved Ice", "cat": CAT_MATERIAL, "power": 0, "damage": 0, "max_stack": 99, "tile": None,
        "rarity": RARITY_COMMON,
        "desc": "Fine snowy ice flakes scooped to create the ultimate tropical cooling treat.",
        "lore": "'Chills instantly beneath the sweltering sun.'",
        "special": "Dessert Ingredient"
    },
    "condensed_milk": {
        "name": "Sweet Condensed Milk", "cat": CAT_CONSUMABLE, "power": 0, "damage": 0, "heal": 25, "max_stack": 99, "tile": None,
        "rarity": RARITY_COMMON,
        "desc": "Sweet, golden thick milk syrup poured lavishly over shaved ice desserts.",
        "lore": "'Pure caramelized dairy bliss.'",
        "special": "Dessert Ingredient"
    },
    "ube_halaya": {
        "name": "Ube Halaya Jam", "cat": CAT_CONSUMABLE, "power": 0, "damage": 0, "heal": 35, "max_stack": 99, "tile": None,
        "rarity": RARITY_UNCOMMON,
        "desc": "Decadent purple yam jam simmered slowly with butter and milk.",
        "lore": "'The crowned jewel of Philippine sweets.'",
        "special": "Restores 35 Health"
    },

    # ----------------------------------------------------
    # Authentic Filipino Cooked Dishes & Feasts
    # ----------------------------------------------------
    "chicken_adobo": {
        "name": "Classic Chicken Adobo", "cat": CAT_CONSUMABLE, "power": 0, "damage": 0, "heal": 90, "max_stack": 99, "tile": None,
        "rarity": RARITY_UNCOMMON,
        "desc": "Simmered native chicken in vinegar, soy sauce, garlic, and cracked pepper. Restores 90 HP.",
        "lore": "'The undisputed national dish of the Philippines.'",
        "special": "Restores 90 Health"
    },
    "pork_adobo": {
        "name": "Rich Pork Adobo", "cat": CAT_CONSUMABLE, "power": 0, "damage": 0, "heal": 95, "max_stack": 99, "tile": None,
        "rarity": RARITY_UNCOMMON,
        "desc": "Tender pork cubes braised with garlic, bay leaves, and tangy soy vinegar sauce. Restores 95 HP.",
        "lore": "'Even better the next day as the sauce deepens.'",
        "special": "Restores 95 Health"
    },
    "sinigang": {
        "name": "Sinigang na Baboy", "cat": CAT_CONSUMABLE, "power": 0, "damage": 0, "heal": 105, "max_stack": 99, "tile": None,
        "rarity": RARITY_RARE,
        "desc": "Tamarind-sour savory soup with tender pork and crisp vegetables. Restores 105 HP.",
        "lore": "'The sour broth warms the heart and cleanses all weariness.'",
        "special": "Restores 105 Health"
    },
    "kare_kare": {
        "name": "Fiesta Kare-Kare", "cat": CAT_CONSUMABLE, "power": 0, "damage": 0, "heal": 115, "max_stack": 99, "tile": None,
        "rarity": RARITY_RARE,
        "desc": "Savory peanut stew with tender beef shank, eggplant, and string beans. Restores 115 HP.",
        "lore": "'Rich golden-orange feast served at grand celebrations.'",
        "special": "Restores 115 Health"
    },
    "bulalo": {
        "name": "Batangas Bulalo", "cat": CAT_CONSUMABLE, "power": 0, "damage": 0, "heal": 120, "max_stack": 99, "tile": None,
        "rarity": RARITY_RARE,
        "desc": "Slow-simmered beef shank marrow soup with sweet corn and peppercorns. Restores 120 HP.",
        "lore": "'Rich, golden marrow that restores tremendous vitality.'",
        "special": "Restores 120 Health"
    },
    "tinola": {
        "name": "Tinolang Manok", "cat": CAT_CONSUMABLE, "power": 0, "damage": 0, "heal": 85, "max_stack": 99, "tile": None,
        "rarity": RARITY_UNCOMMON,
        "desc": "Comforting native chicken soup infused with warming ginger and onions. Restores 85 HP.",
        "lore": "'A comforting maternal recipe that chases away chills.'",
        "special": "Restores 85 Health"
    },
    "lechon": {
        "name": "Crispy Lechon Kawali", "cat": CAT_CONSUMABLE, "power": 0, "damage": 0, "heal": 110, "max_stack": 99, "tile": None,
        "rarity": RARITY_RARE,
        "desc": "Deep-fried pork belly slab with blistering crackling skin and juicy meat. Restores 110 HP.",
        "lore": "'The unmistakable crunch echoing through the banquet hall.'",
        "special": "Restores 110 Health"
    },
    "pancit_bihon": {
        "name": "Pancit Guisado", "cat": CAT_CONSUMABLE, "power": 0, "damage": 0, "heal": 80, "max_stack": 99, "tile": None,
        "rarity": RARITY_UNCOMMON,
        "desc": "Stir-fried bihon noodles with savory meat slivers, garlic, and calamansi. Restores 80 HP.",
        "lore": "'Long noodles for long life and boundless adventures.'",
        "special": "Restores 80 Health"
    },
    "arroz_caldo": {
        "name": "Arroz Caldo with Egg", "cat": CAT_CONSUMABLE, "power": 0, "damage": 0, "heal": 75, "max_stack": 99, "tile": None,
        "rarity": RARITY_UNCOMMON,
        "desc": "Thick chicken and rice porridge topped with toasted garlic and boiled egg. Restores 75 HP.",
        "lore": "'Warming soul food on rainy cavern days.'",
        "special": "Restores 75 Health"
    },
    "halo_halo": {
        "name": "Special Halo-Halo", "cat": CAT_CONSUMABLE, "power": 0, "damage": 0, "heal": 90, "max_stack": 99, "tile": None,
        "rarity": RARITY_RARE,
        "desc": "Towering shaved ice dessert with ube halaya, condensed milk, and sweet treats. Restores 90 HP.",
        "lore": "'Mix-mix! The ultimate festive Philippine refreshment.'",
        "special": "Restores 90 Health"
    },
    "kaldereta": {
        "name": "Kalderetang Kambing", "cat": CAT_CONSUMABLE, "power": 0, "damage": 0, "heal": 110, "max_stack": 99, "tile": None,
        "rarity": RARITY_RARE,
        "desc": "Hearty spiced stew of tender goat meat with tomatoes and sweet peppers. Restores 110 HP.",
        "lore": "'Spicy and robust, a legendary party centerpiece.'",
        "special": "Restores 110 Health"
    },
    "balut": {
        "name": "Balut with Rock Salt", "cat": CAT_CONSUMABLE, "power": 0, "damage": 0, "heal": 65, "max_stack": 99, "tile": None,
        "rarity": RARITY_UNCOMMON,
        "desc": "Fertilized duck egg sipped hot with spiced vinegar and sea salt. Restores 65 HP.",
        "lore": "'Infuses the adventurer with legendary stamina and courage.'",
        "special": "Restores 65 Health"
    },
    "itlog_na_maalat": {
        "name": "Itlog na Maalat", "cat": CAT_CONSUMABLE, "power": 0, "damage": 0, "heal": 45, "max_stack": 99, "tile": None,
        "rarity": RARITY_COMMON,
        "desc": "Cured red-dyed salted duck egg paired with fresh tomatoes. Restores 45 HP.",
        "lore": "'Rich, oily yolk bursting with savory saltiness.'",
        "special": "Restores 45 Health"
    },
    "sinangag": {
        "name": "Garlic Sinangag Rice", "cat": CAT_CONSUMABLE, "power": 0, "damage": 0, "heal": 50, "max_stack": 99, "tile": None,
        "rarity": RARITY_COMMON,
        "desc": "Wok-fried rice tossed with golden toasted garlic and sea salt. Restores 50 HP.",
        "lore": "'The irresistible aroma that awakens sleeping villages.'",
        "special": "Restores 50 Health"
    },
    "daing_na_bangus": {
        "name": "Daing na Bangus", "cat": CAT_CONSUMABLE, "power": 0, "damage": 0, "heal": 75, "max_stack": 99, "tile": None,
        "rarity": RARITY_UNCOMMON,
        "desc": "Marinated split milkfish in garlic vinegar, fried to a golden crisp. Restores 75 HP.",
        "lore": "'Crispy fins and savory belly loved by breakfast champions.'",
        "special": "Restores 75 Health"
    },
    "sinigang_na_bangus": {
        "name": "Sinigang na Bangus", "cat": CAT_CONSUMABLE, "power": 0, "damage": 0, "heal": 100, "max_stack": 99, "tile": None,
        "rarity": RARITY_RARE,
        "desc": "Tamarind-sour soup with tender milkfish belly, eggplant, and onions. Restores 100 HP.",
        "lore": "'The signature Filipino fish soup, sour and refreshing.'",
        "special": "Restores 100 Health"
    },
    "ginataang_tilapia": {
        "name": "Ginataang Tilapia", "cat": CAT_CONSUMABLE, "power": 0, "damage": 0, "heal": 105, "max_stack": 99, "tile": None,
        "rarity": RARITY_RARE,
        "desc": "Fresh tilapia simmered in rich creamy coconut milk with ginger and spices. Restores 105 HP.",
        "lore": "'Creamy oceanic stew with an intoxicating coconut aroma.'",
        "special": "Restores 105 Health"
    },
    "kinilaw_na_tanigue": {
        "name": "Kinilaw na Tanigue", "cat": CAT_CONSUMABLE, "power": 0, "damage": 0, "heal": 110, "max_stack": 99, "tile": None,
        "rarity": RARITY_EPIC,
        "desc": "Fresh Spanish mackerel cured in native vinegar, calamansi juice, ginger, and chili. Restores 110 HP and +15% Speed.",
        "lore": "'The ancient oceanic delicacy of the Philippine islands.'",
        "special": "Restores 110 Health & +15% Speed"
    },
    "dungeon_rune": {
        "name": "Dungeon Teleporter Rune", "cat": CAT_SPECIAL, "power": 0, "damage": 0, "max_stack": 10, "tile": None,
        "rarity": RARITY_EPIC,
        "desc": "Right-click to teleport directly to the Nether Dungeon Chamber and summon Lord Malus!",
        "lore": "'Pulsates with purple abyssal arcane power.'",
        "special": "Warp to Lord Malus Dungeon Arena"
    },
    "desert_rune": {
        "name": "Sun Altar Rune", "cat": CAT_SPECIAL, "power": 0, "damage": 0, "max_stack": 10, "tile": None,
        "rarity": RARITY_RARE,
        "desc": "Right-click to teleport to the Arid Waste Arena to summon Ignis Colossus!",
        "lore": "'The heat within this stone burns like the noonday desert sun.'",
        "special": "Warp to Ignis Colossus Arena"
    },
    "cryo_rune": {
        "name": "Glacial Altar Rune", "cat": CAT_SPECIAL, "power": 0, "damage": 0, "max_stack": 10, "tile": None,
        "rarity": RARITY_RARE,
        "desc": "Right-click to teleport to the Permafrost Arena to summon Cryo-Spud!",
        "lore": "'Frost clings to the air around this enchanted relic.'",
        "special": "Warp to Cryo-Spud Arena"
    },
    "necro_rune": {
        "name": "Blight Altar Rune", "cat": CAT_SPECIAL, "power": 0, "damage": 0, "max_stack": 10, "tile": None,
        "rarity": RARITY_RARE,
        "desc": "Right-click to teleport to the Shadow Crypt to summon Necro-Tuber!",
        "lore": "'Whispers of the undead echo from its dark surface.'",
        "special": "Warp to Necro-Tuber Arena"
    },
    "barrier_block": {
        "name": "Magical Barrier", "cat": CAT_BLOCK, "power": 0, "damage": 0, "max_stack": 999, "tile": 36,
        "rarity": RARITY_RARE,
        "desc": "A block of crystallized arcane force that shields against falling stars and arrows.",
        "lore": "'Woven by the ancient shield sorcerers.'",
        "special": "Blocks High-Angle Projectiles"
    },

    # ----------------------------------------------------
    # Currency & Coins
    # ----------------------------------------------------
    "copper_coin": {
        "name": "Copper Coin", "cat": CAT_CURRENCY, "power": 0, "damage": 0, "max_stack": 999, "tile": None,
        "rarity": RARITY_COMMON,
        "desc": "Standard metallic currency of the Potaria realm.",
        "lore": "'A shiny spud-stamped copper token exchanged among merchants.'"
    },
    "silver_coin": {
        "name": "Silver Coin", "cat": CAT_CURRENCY, "power": 0, "damage": 0, "max_stack": 999, "tile": None,
        "rarity": RARITY_UNCOMMON,
        "desc": "Valuable silver coin worth 100 Copper Coins.",
        "lore": "'Polished silver carrying the crest of the ancient Tuber kingdoms.'"
    },
    "gold_coin": {
        "name": "Gold Coin", "cat": CAT_CURRENCY, "power": 0, "damage": 0, "max_stack": 999, "tile": None,
        "rarity": RARITY_RARE,
        "desc": "Extremely valuable bullion worth 100 Silver Coins (10,000 Copper).",
        "lore": "'Forged from pure auric veins deep within the world core.'"
    },

    # ----------------------------------------------------
    # Special Quest & Gateway Items
    # ----------------------------------------------------
    "portal_shard": {
        "name": "Celestial Portal Shard", "cat": CAT_SPECIAL, "power": 0, "damage": 0, "max_stack": 99, "tile": None,
        "rarity": RARITY_RARE,
        "desc": "Dropped by subterranean mini-bosses. Craft 4 into a Celestial Keystone at a Work Bench!",
        "lore": "'A crystalline sliver fallen from the celestial gates.'",
        "special": "Boss Summoning Key Component"
    },
    "celestial_shard": {
        "name": "Celestial Portal Shard", "cat": CAT_SPECIAL, "power": 0, "damage": 0, "max_stack": 99, "tile": None,
        "rarity": RARITY_RARE,
        "desc": "Dropped by subterranean mini-bosses. Craft 4 into a Celestial Keystone at a Work Bench!",
        "lore": "'A crystalline sliver fallen from the celestial gates.'",
        "special": "Boss Summoning Key Component"
    },
    "celestial_fragment": {
        "name": "Celestial Fragment", "cat": CAT_SPECIAL, "power": 0, "damage": 0, "max_stack": 99, "tile": None,
        "rarity": RARITY_RARE,
        "desc": "A luminous crystal shard radiating celestial starlight. A vital component for summoning keystones.",
        "lore": "'Fallen from the highest reaches of the cosmos.'",
        "special": "Boss Summoning Key Component"
    },
    "celestial_keystone": {
        "name": "Celestial Keystone", "cat": CAT_SPECIAL, "power": 0, "damage": 0, "max_stack": 10, "tile": None,
        "rarity": RARITY_LEGENDARY,
        "desc": "Right-click to summon Grand Boss Sol-Rho - The Celestial Titan!",
        "lore": "'When held aloft, the sky quivers and the titan descends.'",
        "special": "Summons 2-Phase Grand Boss Sol-Rho"
    },
    "fallen_star": {
        "name": "Fallen Star", "cat": CAT_MATERIAL, "power": 0, "damage": 0, "max_stack": 99, "tile": None,
        "rarity": RARITY_RARE,
        "desc": "A luminous star that fell from the cosmos during nightfall. Used to craft astral ammunition and celestial relics.",
        "lore": "'A fragment of pure starlight plucked from the night sky.'",
        "special": "Astral Crafting Catalyst"
    },
    "celestial_star": {
        "name": "Celestial Star", "cat": CAT_MATERIAL, "power": 0, "damage": 0, "max_stack": 99, "tile": None,
        "rarity": RARITY_LEGENDARY,
        "desc": "Radiant starlight core summoned from the heavens. Pulses with pure cosmic energy.",
        "lore": "'Stars forged in the primordial crucible.'",
        "special": "Cosmic Power Source"
    },
    "acorn": {
        "name": "Tree Acorn", "cat": CAT_MATERIAL, "power": 0, "damage": 0, "max_stack": 99, "tile": None,
        "rarity": RARITY_COMMON,
        "desc": "A hardy seed gathered from fallen tree canopies. Essential for reforestation of the surface meadows.",
        "lore": "'A mighty oak awaits within this modest shell.'",
        "special": "Plantable Seed"
    },

    # ----------------------------------------------------
    # Ores, Bars & Boss Essences
    # ----------------------------------------------------
    "copper_ore": {
        "name": "Copper Ore", "cat": CAT_MATERIAL, "power": 0, "damage": 0, "max_stack": 999, "tile": None,
        "rarity": RARITY_COMMON,
        "desc": "Raw copper nuggets mined from surface terrain. Smelt at a furnace.",
        "lore": "'The most common mineral in the crust.'",
        "special": "Smelting Ore"
    },
    "iron_ore": {
        "name": "Iron Ore", "cat": CAT_MATERIAL, "power": 0, "damage": 0, "max_stack": 999, "tile": None,
        "rarity": RARITY_COMMON,
        "desc": "Durable iron deposits found in underground stone. Smelt at a furnace.",
        "lore": "'Heavy metal veins threading through cavern rock.'",
        "special": "Smelting Ore"
    },
    "gold_ore": {
        "name": "Gold Ore", "cat": CAT_MATERIAL, "power": 0, "damage": 0, "max_stack": 999, "tile": None,
        "rarity": RARITY_RARE,
        "desc": "Gleaming golden veins buried in deep caverns. Smelt at a furnace.",
        "lore": "'A precious vein untouched by sunlight.'",
        "special": "Smelting Ore"
    },
    "copper_bar": {
        "name": "Copper Bar", "cat": CAT_MATERIAL, "power": 0, "damage": 0, "max_stack": 999, "tile": None,
        "rarity": RARITY_COMMON,
        "desc": "Refined copper ingot smelted from 3 copper ores. Used at a Work Bench.",
        "lore": "'Cleanly molded metal ingot ready for forging.'",
        "special": "Crafting Ingot"
    },
    "iron_bar": {
        "name": "Iron Bar", "cat": CAT_MATERIAL, "power": 0, "damage": 0, "max_stack": 999, "tile": None,
        "rarity": RARITY_UNCOMMON,
        "desc": "Tempered iron ingot smelted from 3 iron ores. Used for sturdy armor and tools.",
        "lore": "'Dense and resilient.'",
        "special": "Crafting Ingot"
    },
    "gold_bar": {
        "name": "Gold Bar", "cat": CAT_MATERIAL, "power": 0, "damage": 0, "max_stack": 999, "tile": None,
        "rarity": RARITY_RARE,
        "desc": "Pure gold ingot smelted from 3 gold ores. Used for high-tier swords and runes.",
        "lore": "'Radiates warmth and opulence.'",
        "special": "Crafting Ingot"
    },
    "spud_sap": {
        "name": "Spud Sap", "cat": CAT_MATERIAL, "power": 0, "damage": 0, "max_stack": 999, "tile": None,
        "rarity": RARITY_COMMON,
        "desc": "Sticky organic slime sap harvested from slimes. Essential for torches, arrows, and potions.",
        "lore": "'Pleasantly gooey and surprisingly versatile tuber essence.'",
        "special": "Crafting Material"
    },
    "gel": {
        "name": "Spud Sap", "cat": CAT_MATERIAL, "power": 0, "damage": 0, "max_stack": 999, "tile": None,
        "rarity": RARITY_COMMON,
        "desc": "Sticky organic slime sap harvested from slimes. Essential for torches, arrows, and potions.",
        "lore": "'Pleasantly gooey and surprisingly versatile tuber essence.'",
        "special": "Crafting Material"
    },
    "bone": {
        "name": "Skeletal Bone", "cat": CAT_MATERIAL, "power": 0, "damage": 0, "max_stack": 999, "tile": None,
        "rarity": RARITY_UNCOMMON,
        "desc": "Remnants of subterranean dungeon skeletons. Used to craft bows and armor.",
        "lore": "'Hardened by centuries in the dark.'",
        "special": "Crafting Material"
    },
    "frost_core": {
        "name": "Frost Core", "cat": CAT_MATERIAL, "power": 0, "damage": 0, "max_stack": 999, "tile": None,
        "rarity": RARITY_RARE,
        "desc": "Pulsing sub-zero core dropped by glacial beasts.",
        "lore": "'Chilled to absolute zero.'",
        "special": "Crafting Material"
    },
    "magma_core": {
        "name": "Magma Core", "cat": CAT_MATERIAL, "power": 0, "damage": 0, "max_stack": 999, "tile": None,
        "rarity": RARITY_RARE,
        "desc": "Molten subterranean ember dropped by deep cavern monsters.",
        "lore": "'Never loses its scorching heat.'",
        "special": "Crafting Material"
    },
    "necro_essence": {
        "name": "Necro Essence", "cat": CAT_MATERIAL, "power": 0, "damage": 0, "max_stack": 999, "tile": None,
        "rarity": RARITY_RARE,
        "desc": "Dark spirit essence harvested from dungeon horrors.",
        "lore": "'Whispers of forgotten realms.'",
        "special": "Crafting Material"
    },
    "celestial_essence": {
        "name": "Celestial Essence", "cat": CAT_MATERIAL, "power": 0, "damage": 0, "max_stack": 999, "tile": None,
        "rarity": RARITY_LEGENDARY,
        "desc": "Starlight particulate dropped by Celestial Titan Sol-Rho.",
        "lore": "'The divine dust of stellar creation.'",
        "special": "God-Tier Material"
    },

    # =========================================================================
    # Minecraft-Inspired Potaria Craftable Expansion (v1.5.0)
    # =========================================================================
    # ----------------------------------------------------
    # Building Blocks, Bricks, Walls & Scaffolds
    # ----------------------------------------------------
    "carved_stone_bricks": {
        "name": "Carved Stone Bricks", "cat": CAT_BLOCK, "power": 0, "damage": 0, "max_stack": 99,
        "tile": TILE_STONE_BRICK, "rarity": RARITY_COMMON,
        "desc": "Precision-hewn stone masonry carved with ancient geometric friezes.",
        "lore": "'Centuries of weathering could not erase the artisan\\'s chisel.'",
        "effects": [], "special": "Building Block"
    },
    "mosaic_tiles": {
        "name": "Mosaic Tiles", "cat": CAT_BLOCK, "power": 0, "damage": 0, "max_stack": 99,
        "tile": TILE_ROOF_TILES, "rarity": RARITY_UNCOMMON,
        "desc": "Fired clay tiles with lustrous mineral glaze for elegant manor flooring.",
        "lore": "'Vibrant tessellations that shimmer in the warm torchlight.'",
        "effects": [], "special": "Decorative Tile"
    },
    "rope_rungs": {
        "name": "Rope Rungs", "cat": CAT_BLOCK, "power": 0, "damage": 0, "max_stack": 99,
        "tile": TILE_ROPE_RUNGS, "rarity": RARITY_COMMON,
        "desc": "Knotted fiber ladder rungs for swiftly ascending vertical cliffs and shafts.",
        "lore": "", "effects": [], "special": "Climbable Platform"
    },
    "bamboo_scaffold": {
        "name": "Cane Scaffold", "cat": CAT_BLOCK, "power": 0, "damage": 0, "max_stack": 99,
        "tile": TILE_WOOD_PLATFORM, "rarity": RARITY_COMMON,
        "desc": "Lightweight modular scaffold lattice designed for rapid construction.",
        "lore": "", "effects": [], "special": "Temporary Scaffold"
    },
    "cobblestone_parapet": {
        "name": "Cobblestone Parapet", "cat": CAT_WALL, "power": 0, "damage": 0, "max_stack": 99,
        "tile": None, "rarity": RARITY_COMMON,
        "desc": "Low defensive battlement blocks for fortifying homestead ramparts.",
        "lore": "", "effects": [], "special": "Defensive Wall"
    },
    "wrought_iron_palisade": {
        "name": "Wrought Iron Palisade", "cat": CAT_BLOCK, "power": 0, "damage": 0, "max_stack": 99,
        "tile": TILE_WOOD_PLANKS, "rarity": RARITY_COMMON,
        "desc": "Sturdy forged iron security grating that permits sunlight while stopping foes.",
        "lore": "", "effects": [], "special": "Security Grate"
    },
    "dried_thatch_bale": {
        "name": "Dried Thatch Bale", "cat": CAT_BLOCK, "power": 0, "damage": 0, "max_stack": 99,
        "tile": TILE_WOOD_PLANKS, "rarity": RARITY_COMMON,
        "desc": "Tightly compressed dried grain stalks for rustic roofing and soft landings.",
        "lore": "", "effects": [], "special": "Cushioning Block"
    },
    "forged_iron_chain": {
        "name": "Forged Iron Chain", "cat": CAT_MATERIAL, "power": 0, "damage": 0, "max_stack": 99,
        "tile": None, "rarity": RARITY_COMMON,
        "desc": "Interlocked iron chain links for suspending chandeliers and drawbridges.",
        "lore": "", "effects": [], "special": "Hardware Material"
    },
    "reinforced_slate_slab": {
        "name": "Reinforced Slate Slab", "cat": CAT_BLOCK, "power": 0, "damage": 0, "max_stack": 99,
        "tile": TILE_STONE_BRICK, "rarity": RARITY_UNCOMMON,
        "desc": "Heavy slate slabs tempered to resist blast concussions.",
        "lore": "", "effects": [], "special": "Hardened Block"
    },
    "hardened_clay_shingles": {
        "name": "Hardened Clay Shingles", "cat": CAT_BLOCK, "power": 0, "damage": 0, "max_stack": 99,
        "tile": TILE_ROOF_TILES, "rarity": RARITY_COMMON,
        "desc": "Terracotta architectural shingles for high-angle rooftops.",
        "lore": "", "effects": [], "special": "Roof Shingle"
    },

    # ----------------------------------------------------
    # Tools, Weapons, Armor, Shields & Combat Gear
    # ----------------------------------------------------
    "fiber_clippers": {
        "name": "Fiber Clippers", "cat": CAT_TOOL, "power": 15, "damage": 4, "max_stack": 1,
        "tile": None, "rarity": RARITY_COMMON,
        "desc": "Spring-tensioned iron shears for harvesting foliage, vines, and raw plant fibers.",
        "lore": "'Snip cleanly, leave the root intact.'",
        "effects": [], "special": "Plant Harvester"
    },
    "pyrite_sparker": {
        "name": "Pyrite Sparker", "cat": CAT_TOOL, "power": 10, "damage": 3, "max_stack": 1,
        "tile": None, "rarity": RARITY_COMMON,
        "desc": "Iron striker paired with mineral pyrite that ignites campfires and scorches brush.",
        "lore": "'A shower of golden sparks to pierce the gloom.'",
        "effects": [], "special": "Firestarter"
    },
    "oak_buckler": {
        "name": "Oak Buckler", "cat": CAT_ACCESSORY, "power": 0, "damage": 0, "def": 3, "hp": 10,
        "max_stack": 1, "tile": None, "rarity": RARITY_COMMON,
        "desc": "Iron-bossed oak roundshield that absorbs stray arrows and monster charges.",
        "lore": "'Carved from seasoned mountain oak.'",
        "effects": ["+3 Defense", "+10 Max Health"], "special": "Shield Block"
    },
    "iron_aegis": {
        "name": "Iron Aegis", "cat": CAT_ACCESSORY, "power": 0, "damage": 0, "def": 7, "hp": 25,
        "max_stack": 1, "tile": None, "rarity": RARITY_UNCOMMON,
        "desc": "Heavy tempered steel kite shield bearing the royal Spud crest.",
        "lore": "'An unyielding bulwark against subterranean horrors.'",
        "effects": ["+7 Defense", "+25 Max Health"], "special": "Heavy Guard"
    },
    "spud_angler_rod": {
        "name": "Spud Angler Rod", "cat": CAT_TOOL, "power": 14, "damage": 3, "max_stack": 1,
        "tile": None, "rarity": RARITY_UNCOMMON,
        "desc": "Flexible whittled birch rod rigged with braided fiber for freshwater angling.",
        "lore": "'Patience and a plump spud will catch any river titan.'",
        "effects": [], "special": "Fishing Tool"
    },
    "arbalest_repeater": {
        "name": "Arbalest Repeater", "cat": CAT_WEAPON, "power": 0, "damage": 24, "atk": 24, "crit": 5.0, "speed": 0.15,
        "max_stack": 1, "tile": None, "rarity": RARITY_UNCOMMON,
        "desc": "Lever-action mechanised arbalest delivering high-velocity armor-piercing bolts.",
        "lore": "'Crank, lock, release—calibrated for merciless distance.'",
        "effects": ["Piercing Bolts"], "special": "Armor Piercing"
    },
    "glowing_lumen_arrow": {
        "name": "Glowing Lumen Arrow", "cat": CAT_WEAPON, "power": 0, "damage": 8, "max_stack": 99,
        "tile": None, "rarity": RARITY_UNCOMMON,
        "desc": "Bioluminescent tipped arrows that pierce shadows and illuminate hit adversaries.",
        "lore": "'The subterranean mushroom glow marks the target in absolute pitch.'",
        "effects": ["Spore Glow"], "special": "Luminescent Beacon"
    },
    "totem_of_resurgence": {
        "name": "Totem of Resurgence", "cat": CAT_ACCESSORY, "power": 0, "damage": 0, "def": 4, "hp": 40, "mp": 20,
        "max_stack": 1, "tile": None, "rarity": RARITY_MYTHIC,
        "desc": "Gilded pocket idol of the Great Spud that channels restorative starlight when life wanes.",
        "lore": "'Even in the deepest abyss, the seedling reaches upward for the dawn.'",
        "effects": ["+40 Max Health", "+20 Max Mana", "+4 Defense"], "special": "Miraculous Second Chance"
    },
    "copper_harvester_sickle": {
        "name": "Copper Harvester Sickle", "cat": CAT_TOOL, "power": 14, "damage": 5, "max_stack": 1,
        "tile": None, "rarity": RARITY_COMMON,
        "desc": "Curved copper blade for swiftly clearing wild grass and gathering potato yields.",
        "lore": "", "effects": [], "special": "Reap Harvest"
    },
    "spud_quiver": {
        "name": "Spud Hunter's Quiver", "cat": CAT_ACCESSORY, "power": 0, "damage": 2, "crit": 3.0,
        "max_stack": 1, "tile": None, "rarity": RARITY_COMMON,
        "desc": "Lightweight shoulder quiver that improves archer draw speed and critical precision.",
        "lore": "'Arrows always at the fingertips.'",
        "effects": ["+3% Critical Strike Chance", "+2 Ranged Damage"], "special": "Swift Quiver"
    },

    # ----------------------------------------------------
    # Survival, Food, Potions, Utilities & Materials
    # ----------------------------------------------------
    "hearty_root_stew": {
        "name": "Hearty Root Stew", "cat": CAT_CONSUMABLE, "power": 0, "damage": 0, "heal": 60,
        "max_stack": 99, "tile": None, "rarity": RARITY_COMMON,
        "desc": "Simmering rustic stew of cubed potatoes, glowing mushrooms, and savory wild herbs. Restores 60 Health.",
        "lore": "'Warm broth that soothes weary bones after a long mine expedition.'",
        "effects": ["Restores +60 Health"], "special": "Nourishing Feast"
    },
    "glazed_golden_tuber": {
        "name": "Glazed Golden Tuber", "cat": CAT_CONSUMABLE, "power": 0, "damage": 0, "heal": 100, "mp": 30,
        "max_stack": 99, "tile": None, "rarity": RARITY_RARE,
        "desc": "Heirloom russet potato roasted in molten gold and clover nectar. Restores 100 Health and 30 Mana.",
        "lore": "'Fit for kings, treasured by subterranean adventurers.'",
        "effects": ["Restores +100 Health", "Restores +30 Mana"], "special": "Golden Vitality"
    },
    "herbal_salve": {
        "name": "Herbal Salve", "cat": CAT_CONSUMABLE, "power": 0, "damage": 0, "heal": 35,
        "max_stack": 99, "tile": None, "rarity": RARITY_COMMON,
        "desc": "Quick-acting botanical poultice ground from mashed spud pulp and soothing sap. Restores 35 Health.",
        "lore": "'A cool compress against burns, bruises, and monster scrapes.'",
        "effects": ["Restores +35 Health"], "special": "Rapid Soothing"
    },
    "night_gazer_elixir": {
        "name": "Night Gazer Elixir", "cat": CAT_CONSUMABLE, "power": 0, "damage": 0, "heal": 20, "mp": 25,
        "max_stack": 99, "tile": None, "rarity": RARITY_UNCOMMON,
        "desc": "Phosphorescent brew infused with starlight and spores, enhancing subterranean clarity.",
        "lore": "'The dark caves unveil their deepest secrets to eyes unclouded by shadows.'",
        "effects": ["Restores +20 Health", "Restores +25 Mana"], "special": "Night Sight"
    },
    "zephyr_tonic": {
        "name": "Zephyr Tonic", "cat": CAT_CONSUMABLE, "power": 0, "damage": 0, "heal": 25, "mp": 15,
        "max_stack": 99, "tile": None, "rarity": RARITY_UNCOMMON,
        "desc": "Sparkling effervescent tonic distilled with airy minerals, quickening footwork.",
        "lore": "'A draft of pure mountain breeze captured in glass.'",
        "effects": ["Restores +25 Health", "Swiftness Surge"], "special": "Zephyr Wind"
    },
    "smoked_spud_jerky": {
        "name": "Smoked Spud Jerky", "cat": CAT_CONSUMABLE, "power": 0, "damage": 0, "heal": 30,
        "max_stack": 99, "tile": None, "rarity": RARITY_COMMON,
        "desc": "Hickory-cured salted potato jerky crisps that provide quick sustenance during expeditions.",
        "lore": "'Chewy, savory, and keeps indefinitely in a backpack.'",
        "effects": ["Restores +30 Health"], "special": "Trail Ration"
    },
    "gilded_russet": {
        "name": "Gilded Russet", "cat": CAT_CONSUMABLE, "power": 0, "damage": 0, "heal": 140, "mp": 50,
        "max_stack": 99, "tile": None, "rarity": RARITY_EPIC,
        "desc": "Supreme confection of candied royal root providing massive vitality recovery.",
        "lore": "'An alchemical masterpiece, glowing with eternal sunlight.'",
        "effects": ["Restores +140 Health", "Restores +50 Mana"], "special": "Regal Regeneration"
    },
    "glass_flask": {
        "name": "Glass Flask", "cat": CAT_MATERIAL, "power": 0, "damage": 0, "max_stack": 99,
        "tile": None, "rarity": RARITY_COMMON,
        "desc": "Blown glass flask for collecting mountain springs, glowing extracts, and sap.",
        "lore": "", "effects": [], "special": "Alchemy Glassware"
    },
    "burlap_tether": {
        "name": "Burlap Tether", "cat": CAT_TOOL, "power": 0, "damage": 0, "max_stack": 99,
        "tile": None, "rarity": RARITY_COMMON,
        "desc": "Braided hemp tether with a sturdy copper clip for securing gear and companion creatures.",
        "lore": "'Strong enough to hold a bucking wild hog.'",
        "effects": [], "special": "Leash & Tether"
    },
    "explorers_satchel": {
        "name": "Explorer's Satchel", "cat": CAT_ACCESSORY, "power": 0, "damage": 0, "def": 1, "hp": 15,
        "max_stack": 1, "tile": None, "rarity": RARITY_COMMON,
        "desc": "Compact oiled satchel that keeps field specimens and minerals neatly organized.",
        "lore": "'A seasoned explorer travels light, but carries wisdom.'",
        "effects": ["+15 Max Health", "+1 Defense"], "special": "Expanded Pouch"
    },
    "magnetic_lodestone": {
        "name": "Magnetic Lodestone", "cat": CAT_ACCESSORY, "power": 0, "damage": 0, "def": 1, "mp": 10,
        "max_stack": 1, "tile": None, "rarity": RARITY_UNCOMMON,
        "desc": "Floating magnetite compass that attunes to deep underground geological anomalies.",
        "lore": "'The needle never wavers from the world\\'s magnetic core.'",
        "effects": ["+10 Max Mana", "+1 Defense"], "special": "True Compass"
    },
    "brass_far_seer": {
        "name": "Brass Far-Seer", "cat": CAT_ACCESSORY, "power": 0, "damage": 2, "crit": 4.0,
        "max_stack": 1, "tile": None, "rarity": RARITY_UNCOMMON,
        "desc": "Extending brass optical cylinder fitted with crystal lenses for surveying distant horizons.",
        "lore": "'Spotting dungeon spires long before they breach the horizon.'",
        "effects": ["+4% Critical Strike Chance", "+2 Ranged Damage"], "special": "Distant Sight"
    },
    "solar_chronometer": {
        "name": "Solar Chronometer", "cat": CAT_ACCESSORY, "power": 0, "damage": 0, "crit": 2.0, "mp": 15,
        "max_stack": 1, "tile": None, "rarity": RARITY_RARE,
        "desc": "Gilded pocket timepiece with celestial planetary gears predicting sunrise and sunset.",
        "lore": "'Ticks in harmony with the celestial dance of Sol.'",
        "effects": ["+15 Max Mana", "+2% Critical Strike Chance"], "special": "Celestial Timekeeping"
    },
    "abyssal_alloy_bar": {
        "name": "Abyssal Alloy Bar", "cat": CAT_MATERIAL, "power": 0, "damage": 0, "max_stack": 99,
        "tile": None, "rarity": RARITY_EPIC,
        "desc": "Dense iridescent alloy ingot forged from Blightstone, gold, and iron.",
        "lore": "'Impervious to heat, acid, and crushing weight.'",
        "effects": [], "special": "Indestructible Temper"
    },
    "potato_bread": {
        "name": "Oven-Baked Potato Loaf", "cat": CAT_CONSUMABLE, "power": 0, "damage": 0, "heal": 45,
        "max_stack": 99, "tile": None, "rarity": RARITY_COMMON,
        "desc": "Warm crusty hearth bread baked from wholesome potato flour. Restores 45 Health.",
        "lore": "'Crusty on the outside, fluffy and steaming within.'",
        "effects": ["Restores +45 Health"], "special": "Hearty Sustenance"
    },
    "sweet_tuber_pie": {
        "name": "Sweet Tuber Pie", "cat": CAT_CONSUMABLE, "power": 0, "damage": 0, "heal": 70, "mp": 10,
        "max_stack": 99, "tile": None, "rarity": RARITY_COMMON,
        "desc": "Caramelized tuber pie baked to golden perfection with sweet forest sap. Restores 70 Health.",
        "lore": "'A fragrant delight that fills the home with cinnamon and sugar.'",
        "effects": ["Restores +70 Health", "Restores +10 Mana"], "special": "Sweet Comfort"
    },

    # ----------------------------------------------------
    # Furniture, Hearths, Workstations & Mechanisms
    # ----------------------------------------------------
    "cozy_hearth_pit": {
        "name": "Cozy Hearth Pit", "cat": CAT_BLOCK, "power": 0, "damage": 0, "max_stack": 99,
        "tile": TILE_FIREPLACE, "rarity": RARITY_COMMON,
        "desc": "A crackling cobblestone fire pit radiating gentle light and soothing campfire smoke.",
        "lore": "'Gather round Spud, and let the night cold pass.'",
        "effects": [], "special": "Warm Embers"
    },
    "blight_ember_hearth": {
        "name": "Blight Ember Hearth", "cat": CAT_BLOCK, "power": 0, "damage": 0, "max_stack": 99,
        "tile": TILE_FIREPLACE, "rarity": RARITY_UNCOMMON,
        "desc": "Occult hearth pit glowing with spectral indigo embers, warding off darkness.",
        "lore": "'Cold purple flames that never consume their fuel.'",
        "effects": [], "special": "Soul Glow"
    },
    "smithing_anvil": {
        "name": "Smithing Anvil", "cat": CAT_BLOCK, "power": 0, "damage": 0, "max_stack": 99,
        "tile": TILE_WORK_BENCH, "rarity": RARITY_COMMON,
        "desc": "Heavy forged iron anvil for shaping blades, tuning armor, and seating socketed gems.",
        "lore": "'Every legendary weapon began with an anvil\\'s ring.'",
        "effects": [], "special": "Heavy Forging"
    },
    "whetstone_wheel": {
        "name": "Whetstone Wheel", "cat": CAT_BLOCK, "power": 0, "damage": 0, "max_stack": 99,
        "tile": TILE_WORK_BENCH, "rarity": RARITY_COMMON,
        "desc": "Revolving sandstone wheel mounted on timber trestles for grinding and sharpening tools.",
        "lore": "", "effects": [], "special": "Honing Wheel"
    },
    "alchemical_retort": {
        "name": "Alchemical Retort", "cat": CAT_BLOCK, "power": 0, "damage": 0, "max_stack": 99,
        "tile": TILE_WORK_BENCH, "rarity": RARITY_COMMON,
        "desc": "Brass burner and glassware condenser stand for concocting high-tier alchemical solutions.",
        "lore": "'Condensing the essence of stars into restorative drops.'",
        "effects": [], "special": "Distillation"
    },
    "iron_reinforced_door": {
        "name": "Iron-Reinforced Door", "cat": CAT_BLOCK, "power": 0, "damage": 0, "max_stack": 99,
        "tile": TILE_DOOR_CLOSED, "rarity": RARITY_COMMON,
        "desc": "Heavy timber door bolted with forged iron strapping to withstand monstrous dungeon sieges.",
        "lore": "", "effects": [], "special": "Reinforced Barrier"
    },
    "brass_lantern": {
        "name": "Brass Lantern", "cat": CAT_BLOCK, "power": 0, "damage": 0, "max_stack": 99,
        "tile": TILE_BRASS_LANTERN, "rarity": RARITY_COMMON,
        "desc": "Weatherproof brass oil lantern that burns steadily through heavy storms and downpours.",
        "lore": "", "effects": [], "special": "Steady Lantern Glow"
    },
    "brass_lamp": {
        "name": "Brass Lamp", "cat": CAT_BLOCK, "power": 0, "damage": 0, "max_stack": 99,
        "tile": TILE_LAMP, "rarity": RARITY_UNCOMMON,
        "desc": "Fine table brass oil lamp emitting bright warm radial illumination.",
        "lore": "'A steady glow illuminates hearth and home.'", "effects": [], "special": "Bright Warm Radial Light"
    },
    "spectral_lantern": {
        "name": "Spectral Lantern", "cat": CAT_BLOCK, "power": 0, "damage": 0, "max_stack": 99,
        "tile": TILE_SPECTRAL_LANTERN, "rarity": RARITY_UNCOMMON,
        "desc": "Chilled lantern casting an azure glow that illuminates cavern depths.",
        "lore": "", "effects": [], "special": "Azure Luminescence"
    },
    "timber_trapdoor": {
        "name": "Timber Trapdoor", "cat": CAT_BLOCK, "power": 0, "damage": 0, "max_stack": 99,
        "tile": TILE_DOOR_CLOSED, "rarity": RARITY_COMMON,
        "desc": "Hinged wooden floor hatch for cellar entrances and mine shaft ladders.",
        "lore": "", "effects": [], "special": "Floor Hatch"
    },
    "hooped_cask": {
        "name": "Hooped Cask", "cat": CAT_BLOCK, "power": 0, "damage": 0, "max_stack": 99,
        "tile": TILE_CHEST, "rarity": RARITY_COMMON,
        "desc": "Stout wooden storage cask sealed with copper banding for keeping cellar preserves.",
        "lore": "", "effects": [], "special": "Dry Storage"
    },
    "iron_cauldron": {
        "name": "Iron Cauldron", "cat": CAT_BLOCK, "power": 0, "damage": 0, "max_stack": 99,
        "tile": TILE_WORK_BENCH, "rarity": RARITY_COMMON,
        "desc": "Heavy cast kettle for collecting rainwater, washing ore, and boiling root broths.",
        "lore": "", "effects": [], "special": "Kettle Vessel"
    },
    "weaver_loom": {
        "name": "Weaver's Loom", "cat": CAT_BLOCK, "power": 0, "damage": 0, "max_stack": 99,
        "tile": TILE_WORK_BENCH, "rarity": RARITY_COMMON,
        "desc": "Crafting loom with wooden shuttles for weaving tapestries, sails, and explorer cloaks.",
        "lore": "", "effects": [], "special": "Loom Weaving"
    },
    "blast_kiln": {
        "name": "High-Temp Blast Kiln", "cat": CAT_BLOCK, "power": 0, "damage": 0, "max_stack": 99,
        "tile": TILE_FURNACE, "rarity": RARITY_COMMON,
        "desc": "Refractory smelting kiln insulated with dense brick for processing ores at intense temperatures.",
        "lore": "", "effects": [], "special": "High-Heat Smelting"
    },
    "smokehouse_stove": {
        "name": "Smokehouse Stove", "cat": CAT_BLOCK, "power": 0, "damage": 0, "max_stack": 99,
        "tile": TILE_FURNACE, "rarity": RARITY_COMMON,
        "desc": "Chimney-vented wooden smoke oven designed for rapidly curing and smoking provisions.",
        "lore": "", "effects": [], "special": "Food Smoking"
    },
    "cartographer_desk": {
        "name": "Cartographer's Desk", "cat": CAT_BLOCK, "power": 0, "damage": 0, "max_stack": 99,
        "tile": TILE_TABLE, "rarity": RARITY_COMMON,
        "desc": "Drafting table equipped with brass calipers and parchment rolls for mapping uncharted lands.",
        "lore": "", "effects": [], "special": "Chart Table"
    },
    "fletcher_bench": {
        "name": "Fletcher's Bench", "cat": CAT_BLOCK, "power": 0, "damage": 0, "max_stack": 99,
        "tile": TILE_WORK_BENCH, "rarity": RARITY_COMMON,
        "desc": "Specialist work station for notching arrow shafts and tensioning composite bows.",
        "lore": "", "effects": [], "special": "Fletching"
    },
    "masonry_saw": {
        "name": "Masonry Saw", "cat": CAT_BLOCK, "power": 0, "damage": 0, "max_stack": 99,
        "tile": TILE_WORK_BENCH, "rarity": RARITY_COMMON,
        "desc": "Rotary iron cutting wheel for cleanly trimming stone blocks into precision architectural trim.",
        "lore": "", "effects": [], "special": "Stone Cutting"
    },
    "archery_target": {
        "name": "Archery Target", "cat": CAT_BLOCK, "power": 0, "damage": 0, "max_stack": 99,
        "tile": TILE_CHAIR, "rarity": RARITY_COMMON,
        "desc": "Painted straw bullseye target for measuring marksmanship and projectile distance.",
        "lore": "", "effects": [], "special": "Marksmanship"
    },
    "galvanic_attractor": {
        "name": "Galvanic Attractor", "cat": CAT_BLOCK, "power": 0, "damage": 0, "max_stack": 99,
        "tile": TILE_TORCH, "rarity": RARITY_COMMON,
        "desc": "Pointed copper spire that attracts atmospheric static and redirects lightning strikes.",
        "lore": "", "effects": [], "special": "Static Grounding"
    },
    "carved_tuber_lantern": {
        "name": "Carved Tuber Lantern", "cat": CAT_BLOCK, "power": 0, "damage": 0, "max_stack": 99,
        "tile": TILE_CARVED_TUBER_LANTERN, "rarity": RARITY_COMMON,
        "desc": "Whimsically hollowed giant potato grinning merrily with a warm flame burning inside.",
        "lore": "'A smiling beacon that keeps night phantoms away from the doorstep.'",
        "effects": [], "special": "Festive Light"
    },
}

def load_custom_items():
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    data_dir = os.path.join(base_dir, "data")
    weapons_file = os.path.join(data_dir, "weapons.json")
    equipments_file = os.path.join(data_dir, "equipments.json")

    # Load weapons
    if os.path.exists(weapons_file):
        try:
            with open(weapons_file, "r", encoding="utf-8") as f:
                w_list = json.load(f)
                for w in w_list:
                    item_id = w["id"]
                    effs = w.get("effects", [])
                    special_str = " • ".join(effs) if effs else w.get("special", "")
                    rarity = w.get("rarity", RARITY_COMMON)
                    lore = w.get("lore", "")
                    if rarity not in (RARITY_LEGENDARY, RARITY_MYTHIC, RARITY_ANCIENT):
                        lore = ""
                    if "wood" in item_id:
                        effs = []
                        special_str = ""
                        lore = ""
                    existing_desc = ITEM_REGISTRY[item_id].get("desc") if item_id in ITEM_REGISTRY else ""
                    w_desc = w.get("desc")
                    final_desc = w_desc or existing_desc or f"A {rarity.title()} weapon forged in Potaria."
                    ITEM_REGISTRY[item_id] = {
                        "name": w["name"],
                        "cat": CAT_WEAPON,
                        "power": 0,
                        "damage": w.get("atk", 0),
                        "atk": w.get("atk", 0),
                        "def": w.get("def", 0),
                        "crit": w.get("crit", 0.0),
                        "speed": w.get("speed", 0.0),
                        "hp": w.get("hp", 0),
                        "mp": w.get("mp", 0),
                        "mp_regen": w.get("mp_regen", 0.0),
                        "max_stack": 1,
                        "tile": None,
                        "rarity": rarity,
                        "color": w.get("color", RARITY_HEX_COLORS.get(rarity, "#9E9E9E")),
                        "desc": final_desc,
                        "lore": lore,
                        "effects": effs,
                        "special": special_str,
                    }
        except Exception as e:
            print(f"[Inventory] Warning: Failed to load weapons.json: {e}")

    # Load equipments
    if os.path.exists(equipments_file):
        try:
            with open(equipments_file, "r", encoding="utf-8") as f:
                e_list = json.load(f)
                for eq in e_list:
                    item_id = eq["id"]
                    c = eq.get("cat", "accessory")
                    if c in ("head", "chest", "legs"):
                        cat_str = f"armor_{c}"
                    else:
                        cat_str = CAT_ACCESSORY
                    effs = eq.get("effects", [])
                    special_str = " • ".join(effs) if effs else eq.get("special", "")
                    rarity = eq.get("rarity", RARITY_COMMON)
                    lore = eq.get("lore", "")
                    if rarity not in (RARITY_LEGENDARY, RARITY_MYTHIC, RARITY_ANCIENT):
                        lore = ""
                    if "wood" in item_id:
                        effs = []
                        special_str = ""
                        lore = ""
                    existing_eq_desc = ITEM_REGISTRY[item_id].get("desc") if item_id in ITEM_REGISTRY else ""
                    eq_desc = eq.get("desc")
                    final_eq_desc = eq_desc or existing_eq_desc or f"A {rarity.title()} {c} piece."
                    ITEM_REGISTRY[item_id] = {
                        "name": eq["name"],
                        "cat": cat_str,
                        "power": 0,
                        "damage": 0,
                        "atk": eq.get("atk", 0),
                        "def": eq.get("def", 0),
                        "crit": eq.get("crit", 0.0),
                        "speed": eq.get("speed", 0.0),
                        "hp": eq.get("hp", 0),
                        "mp": eq.get("mp", 0),
                        "mp_regen": eq.get("mp_regen", 0.0),
                        "max_stack": 1,
                        "tile": None,
                        "rarity": rarity,
                        "color": eq.get("color", RARITY_HEX_COLORS.get(rarity, "#9E9E9E")),
                        "desc": final_eq_desc,
                        "lore": lore,
                        "effects": effs,
                        "special": special_str,
                    }
        except Exception as e:
            print(f"[Inventory] Warning: Failed to load equipments.json: {e}")

    # Set up legacy aliases
    for old_id, new_id in ITEM_ALIASES.items():
        if new_id in ITEM_REGISTRY and old_id not in ITEM_REGISTRY:
            ITEM_REGISTRY[old_id] = ITEM_REGISTRY[new_id]

# Automatically populate custom weapons and equipment into ITEM_REGISTRY
load_custom_items()

class ItemStack:
    def __init__(self, item_id, count=1, enhancement_level=0, is_broken=False, affix_slots=0, affixes=None, removed_stats=None, base_rolls=None, additional_affix_slots=0, tags=None, roll_if_empty=False):
        self.item_id = item_id
        self.count = count
        self.enhancement_level = int(enhancement_level)
        self.is_broken = bool(is_broken)
        self.affix_slots = int(affix_slots)
        self.affixes = list(affixes) if affixes else []
        self.removed_stats = list(removed_stats) if removed_stats else []
        self.additional_affix_slots = int(additional_affix_slots)
        self.tags = list(tags) if tags else None

        if base_rolls is not None:
            self.base_rolls = dict(base_rolls)
        elif roll_if_empty:
            try:
                from src.rpg.equipment_update import roll_item_stat_ranges
                self.base_rolls = roll_item_stat_ranges(item_id)
            except Exception:
                self.base_rolls = None
        else:
            self.base_rolls = None

    def clone(self, count=None):
        """Creates an independent clone of this ItemStack with all enhancement, affix, and roll metadata intact."""
        return ItemStack(
            self.item_id,
            self.count if count is None else int(count),
            enhancement_level=self.enhancement_level,
            is_broken=self.is_broken,
            affix_slots=self.affix_slots,
            affixes=list(self.affixes),
            removed_stats=list(self.removed_stats),
            base_rolls=dict(self.base_rolls) if self.base_rolls else None,
            additional_affix_slots=self.additional_affix_slots,
            tags=list(self.tags) if self.tags else None
        )

    @property
    def data(self):
        canon = ITEM_ALIASES.get(self.item_id, self.item_id)
        base = ITEM_REGISTRY.get(self.item_id) or ITEM_REGISTRY.get(canon, {})
        if (not self.enhancement_level and not self.is_broken and not self.affixes 
                and not self.removed_stats and not self.base_rolls and not self.tags):
            return base

        # Clone and apply modifications
        d = dict(base)

        # Apply persistent rolled base stats
        if self.base_rolls:
            for stat_k, stat_v in self.base_rolls.items():
                d[stat_k] = stat_v
                if stat_k == "atk" and "damage" in d:
                    d["damage"] = stat_v
                elif stat_k == "damage" and "atk" in d:
                    d["atk"] = stat_v

        # Apply tags metadata
        if self.tags:
            d["tags"] = list(self.tags)

        if self.enhancement_level > 0:
            mult = 1.0 + (self.enhancement_level / 7.0)
            if "damage" in d and d["damage"] > 0:
                d["damage"] = int(round(d["damage"] * mult))
            if "atk" in d and d["atk"] > 0:
                d["atk"] = int(round(d["atk"] * mult))
            if "def" in d and d["def"] > 0:
                d["def"] = int(round(d["def"] * mult))
            if "hp" in d and d["hp"] > 0:
                d["hp"] = int(round(d["hp"] * mult))
            if "mp" in d and d["mp"] > 0:
                d["mp"] = int(round(d["mp"] * mult))
            if "crit" in d and d["crit"] > 0:
                d["crit"] = round(d["crit"] * mult, 1)
            if "speed" in d and d["speed"] > 0:
                d["speed"] = round(d["speed"] * mult, 2)
            d["name"] = f"{base.get('name', self.item_id)} +{self.enhancement_level}"

        if self.is_broken:
            d["name"] = f"[BROKEN] {d.get('name', self.item_id)}"
            d["damage"] = 0
            d["atk"] = 0
            d["def"] = 0
            d["hp"] = 0
            d["mp"] = 0
            d["crit"] = 0.0
            d["speed"] = 0.0

        if self.removed_stats:
            for s in self.removed_stats:
                if s in d:
                    d[s] = 0
                if s == "damage" and "atk" in d:
                    d["atk"] = 0
                elif s == "atk" and "damage" in d:
                    d["damage"] = 0

        if self.affixes:
            eff_list = list(d.get("effects", []))
            for aff in self.affixes:
                eff_list.append(f"★ {aff}")
            d["effects"] = eff_list

        return d

    @property
    def max_stack(self):
        return self.data.get("max_stack", 999)

class Inventory:
    def __init__(self, asset_factory, difficulty="legacy"):
        self.asset_factory = asset_factory
        self.slots = [None] * INV_TOTAL_SLOTS
        self.selected_slot = 0
        self.is_open = False
        self.held_item = None
        self._player = None

        # Dedicated Coin Purse fallback storage when not linked to player.stats
        self._local_copper = 0
        self._local_silver = 0
        self._local_gold = 0

        # Notification banner when learning a skill
        self.last_learned_message = None
        self.last_learned_timer = 0.0
        self.tooltip_mode = "detailed"

        # Fonts (Centralized Typography Theme)
        from src.ui.theme import font_regular, font_semibold, font_compact
        self.font = font_regular(14)
        self.font_bold = font_semibold(16)
        self.font_sm = font_compact(11)

        # Set initial loadout based on difficulty mode
        self.set_difficulty_loadout(difficulty)

    @property
    def player(self):
        return self._player

    @player.setter
    def player(self, p):
        self._player = p
        if p and hasattr(p, "stats") and (self._local_copper or self._local_silver or self._local_gold):
            p.stats.add_coins(copper=self._local_copper, silver=self._local_silver, gold=self._local_gold)
            self._local_copper = 0
            self._local_silver = 0
            self._local_gold = 0

    @property
    def copper_coins(self):
        if hasattr(self, "player") and self.player and hasattr(self.player, "stats"):
            return self.player.stats.copper_coins
        return self._local_copper

    @copper_coins.setter
    def copper_coins(self, val):
        if hasattr(self, "player") and self.player and hasattr(self.player, "stats"):
            self.player.stats.copper_coins = int(val)
        else:
            self._local_copper = int(val)

    @property
    def silver_coins(self):
        if hasattr(self, "player") and self.player and hasattr(self.player, "stats"):
            return self.player.stats.silver_coins
        return self._local_silver

    @silver_coins.setter
    def silver_coins(self, val):
        if hasattr(self, "player") and self.player and hasattr(self.player, "stats"):
            self.player.stats.silver_coins = int(val)
        else:
            self._local_silver = int(val)

    @property
    def gold_coins(self):
        if hasattr(self, "player") and self.player and hasattr(self.player, "stats"):
            return self.player.stats.gold_coins
        return self._local_gold

    @gold_coins.setter
    def gold_coins(self, val):
        if hasattr(self, "player") and self.player and hasattr(self.player, "stats"):
            self.player.stats.gold_coins = int(val)
        else:
            self._local_gold = int(val)

    def total_coins_value(self):
        """Returns total spending power in copper denomination across all coins."""
        if hasattr(self, "player") and self.player and hasattr(self.player, "stats"):
            return self.player.stats.total_copper_value
        return int(self._local_copper + self._local_silver * 100 + self._local_gold * 10000)

    def add_coins(self, copper=0, silver=0, gold=0):
        """Deposits coins with automatic denomination breakdown (100c = 1s, 100s = 1g)."""
        if hasattr(self, "player") and self.player and hasattr(self.player, "stats"):
            self.player.stats.add_coins(copper=copper, silver=silver, gold=gold)
        else:
            tot = self.total_coins_value() + int(copper) + int(silver) * 100 + int(gold) * 10000
            tot = max(0, tot)
            self._local_gold = tot // 10000
            rem = tot % 10000
            self._local_silver = rem // 100
            self._local_copper = rem % 100

    def remove_coins(self, total_copper):
        """Deducts currency with automatic change making. Returns True if sufficient funds."""
        if hasattr(self, "player") and self.player and hasattr(self.player, "stats"):
            return self.player.stats.remove_coins(total_copper)
        else:
            cur = self.total_coins_value()
            if cur >= total_copper:
                tot = cur - total_copper
                self._local_gold = tot // 10000
                rem = tot % 10000
                self._local_silver = rem // 100
                self._local_copper = rem % 100
                return True
            return False

    def migrate_coins(self):
        """Scans all 40 slots and held item; transfers any coin items into the Coin Purse and frees up the slots."""
        for idx in range(len(self.slots)):
            slot = self.slots[idx]
            if slot and slot.item_id in ("copper_coin", "silver_coin", "gold_coin"):
                if slot.item_id == "copper_coin":
                    self.add_coins(copper=slot.count)
                elif slot.item_id == "silver_coin":
                    self.add_coins(silver=slot.count)
                elif slot.item_id == "gold_coin":
                    self.add_coins(gold=slot.count)
                self.slots[idx] = None
        if self.held_item and self.held_item.item_id in ("copper_coin", "silver_coin", "gold_coin"):
            if self.held_item.item_id == "copper_coin":
                self.add_coins(copper=self.held_item.count)
            elif self.held_item.item_id == "silver_coin":
                self.add_coins(silver=self.held_item.count)
            elif self.held_item.item_id == "gold_coin":
                self.add_coins(gold=self.held_item.count)
            self.held_item = None

    def set_difficulty_loadout(self, difficulty="normal"):
        """Initializes starter inventory according to difficulty mode."""
        self.slots = [None] * INV_TOTAL_SLOTS
        if difficulty == "easy":
            # Easy: Starts with wood axe, 5 torches, and starter skills
            self.slots[0] = ItemStack("wood_axe", 1)
            self.slots[1] = ItemStack("torch", 5)
        elif difficulty == "normal":
            # Normal: Starts with 1 wooden axe and 5 torches
            self.slots[0] = ItemStack("wood_axe", 1)
            self.slots[1] = ItemStack("torch", 5)
        elif difficulty in ("hardcore", "yolo"):
            # Hardcore & YOLO: Starts with 0 items (empty inventory). Punch trees for wood.
            pass
        else: # "legacy" or fallback for existing test suites
            self.slots[0] = ItemStack("copper_shortsword", 1)
            self.slots[1] = ItemStack("copper_pickaxe", 1)
            self.slots[2] = ItemStack("wood", 35)
            self.slots[3] = ItemStack("torch", 16)
            self.slots[4] = ItemStack("raw_potato", 6)
            self.slots[5] = ItemStack("miner_helmet", 1)
            self.slots[6] = ItemStack("copper_chestplate", 1)
            self.slots[7] = ItemStack("copper_greaves", 1)
            self.slots[8] = ItemStack("skillbook_whirlwind", 1)

    def clear_all_items(self):
        """Clears all carried items and held cursor item (used on boss defeat penalty)."""
        self.slots = [None] * len(self.slots)
        self.held_item = None

    def can_add_item(self, item_id, count=1):
        """Returns True if the inventory has sufficient slot or stack capacity to hold count items."""
        if hasattr(item_id, "item_id"):
            item_id = item_id.item_id
        if item_id in ("copper_coin", "silver_coin", "gold_coin"):
            return True
        canon = ITEM_ALIASES.get(item_id, item_id)
        data = ITEM_REGISTRY.get(item_id) or ITEM_REGISTRY.get(canon, {})
        max_s = data.get("max_stack", 999)
        space = 0
        for slot in self.slots:
            if slot is None:
                space += max_s
            elif slot.item_id == item_id and slot.count < max_s:
                space += (max_s - slot.count)
            elif ITEM_ALIASES.get(slot.item_id, slot.item_id) == canon and slot.count < max_s:
                space += (max_s - slot.count)
            if space >= count:
                return True
        return space >= count

    def drop_item(self, slot_idx, count=None):
        """Removes items from slot to drop into the world. Returns (item_id, count_dropped) or None."""
        if slot_idx < 0 or slot_idx >= len(self.slots):
            return None
        slot = self.slots[slot_idx]
        if not slot:
            return None
        if count is None or count >= slot.count:
            dropped_id = slot.item_id
            dropped_count = slot.count
            self.slots[slot_idx] = None
            return (dropped_id, dropped_count)
        else:
            dropped_id = slot.item_id
            dropped_count = count
            slot.count -= count
            return (dropped_id, dropped_count)

    def drop_held_item(self, count=None):
        """Drops currently held item. Returns (item_id, count_dropped) or None."""
        if not self.held_item:
            return None
        if count is None or count >= self.held_item.count:
            dropped_id = self.held_item.item_id
            dropped_count = self.held_item.count
            self.held_item = None
            return (dropped_id, dropped_count)
        else:
            dropped_id = self.held_item.item_id
            dropped_count = count
            self.held_item.count -= count
            return (dropped_id, dropped_count)

    def get_hovered_slot(self, mouse_x, mouse_y):
        """Returns the slot index under (mouse_x, mouse_y) or None."""
        start_x = 20
        start_y = 20
        rows = INV_ROWS if self.is_open else 1
        for row in range(rows):
            for col in range(INV_COLS):
                slot_idx = row * INV_COLS + col
                sx = start_x + col * (SLOT_SIZE + SLOT_PADDING)
                sy = start_y + row * (SLOT_SIZE + SLOT_PADDING)
                rect = pygame.Rect(sx, sy, SLOT_SIZE, SLOT_SIZE)
                if rect.collidepoint(mouse_x, mouse_y):
                    return slot_idx
        return None

    def get_drop_button_rect(self):
        """Returns the screen Rect for the UI [DROP] button when inventory is open."""
        start_x = 20
        start_y = 20
        rows = INV_ROWS if self.is_open else 1
        return pygame.Rect(start_x + 260, start_y + rows * (SLOT_SIZE + SLOT_PADDING) + 4, 58, 22)

    def get_recycle_button_rect(self):
        """Returns the screen Rect for the UI [RECYCLE] button to dispose unwanted items."""
        start_x = 20
        start_y = 20
        rows = INV_ROWS if self.is_open else 1
        return pygame.Rect(start_x + 326, start_y + rows * (SLOT_SIZE + SLOT_PADDING) + 4, 76, 22)

    def get_organize_button_rect(self):
        """Returns the screen Rect for the UI [ORGANIZE] button to fill gaps."""
        start_x = 20
        start_y = 20
        rows = INV_ROWS if self.is_open else 1
        return pygame.Rect(start_x + 410, start_y + rows * (SLOT_SIZE + SLOT_PADDING) + 4, 82, 22)

    def organize_inventory(self, include_hotbar=True):
        """
        Compacts inventory items forward in current sequential order to fill all missing slots (None)
        without sorting by item type, category, or rarity.
        Combines matching partial stacks of identical items and removes gaps.
        """
        target_slots = self.slots if include_hotbar else self.slots[HOTBAR_SLOTS:]
        compacted = []
        for s in target_slots:
            if s is not None:
                merged = False
                for existing in compacted:
                    if (existing.item_id == s.item_id and
                        getattr(existing, "enhancement_level", 0) == getattr(s, "enhancement_level", 0) and
                        not getattr(existing, "is_broken", False) and not getattr(s, "is_broken", False) and
                        getattr(existing, "base_rolls", None) is None and getattr(s, "base_rolls", None) is None and
                        getattr(existing, "additional_affix_slots", 0) == 0 and getattr(s, "additional_affix_slots", 0) == 0 and
                        getattr(existing, "tags", None) is None and getattr(s, "tags", None) is None):
                        space = existing.max_stack - existing.count
                        if space > 0:
                            take = min(space, s.count)
                            existing.count += take
                            s.count -= take
                            if s.count <= 0:
                                merged = True
                                break
                if not merged and s.count > 0:
                    compacted.append(s)

        new_slots = compacted + [None] * (len(target_slots) - len(compacted))
        if include_hotbar:
            self.slots = new_slots
        else:
            self.slots[HOTBAR_SLOTS:] = new_slots
        return True

    def recycle_selected_or_held(self):
        """Permanently disposes of the held item or currently selected item.
        Returns (item_id, count_recycled) or None."""
        if self.held_item:
            recycled_id = self.held_item.item_id
            recycled_count = self.held_item.count
            self.held_item = None
            return (recycled_id, recycled_count)
        if 0 <= self.selected_slot < len(self.slots) and self.slots[self.selected_slot]:
            slot = self.slots[self.selected_slot]
            recycled_id = slot.item_id
            recycled_count = slot.count
            self.slots[self.selected_slot] = None
            return (recycled_id, recycled_count)
        return None

    def notify(self, message, timer=3.5):
        """Displays a banner notification on the HUD."""
        self.last_learned_message = message
        self.last_learned_timer = timer

    def update(self, dt):
        """Updates notification timers for learned skill banners and migrates coins."""
        self.migrate_coins()
        if self.last_learned_timer > 0:
            self.last_learned_timer -= dt
            if self.last_learned_timer <= 0:
                self.last_learned_message = None

    def get_active_item(self):
        return self.slots[self.selected_slot]

    def add_item(self, item_id, count=1, from_back=False):
        stack_source = None
        if isinstance(item_id, ItemStack):
            stack_source = item_id
            target_id = item_id.item_id
            count = item_id.count
        else:
            target_id = item_id

        # Coins deposit directly into the dedicated Coin Purse without occupying inventory slots
        if target_id == "copper_coin":
            self.add_coins(copper=count)
            return 0
        elif target_id == "silver_coin":
            self.add_coins(silver=count)
            return 0
        elif target_id == "gold_coin":
            self.add_coins(gold=count)
            return 0

        target_id = ITEM_ALIASES.get(target_id, target_id)
        if stack_source:
            stack_source.item_id = target_id

        data = ITEM_REGISTRY.get(target_id, {})
        max_s = data.get("max_stack", 999)

        # Non-modified stackable items can merge into existing slots
        is_modified = stack_source and (
            stack_source.enhancement_level > 0 or 
            stack_source.is_broken or 
            stack_source.affixes or 
            stack_source.removed_stats or 
            getattr(stack_source, "base_rolls", None) or 
            getattr(stack_source, "additional_affix_slots", 0) > 0 or 
            getattr(stack_source, "tags", None)
        )
        if max_s > 1 and not is_modified:
            merge_slots = list(reversed(self.slots)) if from_back else self.slots
            for slot in merge_slots:
                if slot:
                    slot_canon = ITEM_ALIASES.get(slot.item_id, slot.item_id)
                    if (slot.item_id == target_id or slot_canon == target_id) and slot.count < max_s:
                        if not (
                            slot.enhancement_level > 0 or 
                            slot.is_broken or 
                            slot.affixes or 
                            slot.removed_stats or 
                            getattr(slot, "base_rolls", None) or 
                            getattr(slot, "additional_affix_slots", 0) > 0 or 
                            getattr(slot, "tags", None)
                        ):
                            space = max_s - slot.count
                            transfer = min(space, count)
                            slot.count += transfer
                            count -= transfer
                            if count <= 0:
                                return 0

        slot_indices = range(len(self.slots) - 1, -1, -1) if from_back else range(len(self.slots))
        for idx in slot_indices:
            if self.slots[idx] is None:
                transfer = min(max_s, count)
                if stack_source:
                    self.slots[idx] = stack_source.clone(count=transfer)
                else:
                    self.slots[idx] = ItemStack(target_id, transfer)
                count -= transfer
                if count <= 0:
                    return 0
        return count

    def get_item_data(self, item_id):
        canon = ITEM_ALIASES.get(item_id, item_id)
        return ITEM_REGISTRY.get(canon)

    def count_item(self, item_id):
        if item_id == "copper_coin":
            return self.total_coins_value()
        elif item_id == "silver_coin":
            return self.total_coins_value() // 100
        elif item_id == "gold_coin":
            return self.total_coins_value() // 10000

        canon = ITEM_ALIASES.get(item_id, item_id)
        total = 0
        for slot in self.slots:
            if slot:
                slot_canon = ITEM_ALIASES.get(slot.item_id, slot.item_id)
                if slot.item_id == item_id or slot.item_id == canon or slot_canon == canon:
                    total += slot.count
        return total

    def is_empty(self):
        """Returns True if every inventory slot is currently empty."""
        return all(slot is None for slot in self.slots)

    def has_miner_helmet(self):
        return self.count_item("miner_helmet") > 0

    def remove_item(self, item_id, count):
        if item_id == "copper_coin":
            return self.remove_coins(count)
        elif item_id == "silver_coin":
            return self.remove_coins(count * 100)
        elif item_id == "gold_coin":
            return self.remove_coins(count * 10000)

        canon = ITEM_ALIASES.get(item_id, item_id)
        if self.count_item(item_id) < count:
            return False

        remaining = count
        for idx in range(len(self.slots)):
            slot = self.slots[idx]
            if slot:
                slot_canon = ITEM_ALIASES.get(slot.item_id, slot.item_id)
                if slot.item_id == item_id or slot.item_id == canon or slot_canon == canon:
                    if slot.count <= remaining:
                        remaining -= slot.count
                        self.slots[idx] = None
                    else:
                        slot.count -= remaining
                        remaining = 0
                    if remaining <= 0:
                        break
        return True

    def handle_click(self, mouse_x, mouse_y, is_right_click, player=None):
        start_x = 20
        start_y = 20
        rows_to_check = INV_ROWS if self.is_open else 1

        for row in range(rows_to_check):
            for col in range(INV_COLS):
                slot_idx = row * INV_COLS + col
                sx = start_x + col * (SLOT_SIZE + SLOT_PADDING)
                sy = start_y + row * (SLOT_SIZE + SLOT_PADDING)
                rect = pygame.Rect(sx, sy, SLOT_SIZE, SLOT_SIZE)

                if rect.collidepoint(mouse_x, mouse_y):
                    current = self.slots[slot_idx]

                    # Quick Equip on Right-Click when Inventory is open!
                    if is_right_click and current and player and self.is_open:
                        if getattr(current, "is_broken", False):
                            self.notify("Cannot equip broken item! Repair it at the Mystic Trader first.")
                            return True

                        item_id = current.item_id
                        cat = current.data.get("cat", "")

                        # If Skill Book, read and learn or upgrade skill!
                        if cat == "skillbook":
                            s_to_learn = current.data.get("skill")
                            if s_to_learn:
                                already_learned = s_to_learn in player.skills.learned_skills
                                success = player.skills.learn_skill(s_to_learn)
                                if success:
                                    lvl = player.skills.get_skill_level(s_to_learn) if hasattr(player.skills, "get_skill_level") else 1
                                    s_name = player.skills.all_skills.get(s_to_learn, {}).get("name", s_to_learn)
                                    if already_learned:
                                        self.last_learned_message = f"Upgraded {s_name} to Lv. {lvl}! Damage, radius and speed increased!"
                                    else:
                                        self.last_learned_message = f"Learned {s_name} Lv. 1! Open Character Status [C] to view & assign to hotkeys (Q, F, V, R)."
                                    self.last_learned_timer = 5.0
                                    player.sound_manager.play("craft")
                                    self.slots[slot_idx] = None
                                    return True
                                else:
                                    self.last_learned_message = f"{s_to_learn.replace('_', ' ').title()} is already at MAX Level (Lv. 5)!"
                                    self.last_learned_timer = 3.0
                                    return True

                        # If Affix Stone, embed into active weapon or first eligible item on right-click!
                        if item_id == "affix_stone":
                            from src.rpg.enhancement import can_apply_affix_stone, apply_affix_stone
                            target = self.get_active_item()
                            if not target or not can_apply_affix_stone(target)[0]:
                                target = None
                                for s in self.slots:
                                    if s and can_apply_affix_stone(s)[0]:
                                        target = s
                                        break
                            if target:
                                ok, msg = apply_affix_stone(target, self, player.sound_manager if player else None)
                                self.notify(msg)
                            else:
                                self.notify("No eligible Legendary or Ancient gear with an open affix slot found!")
                            return True

                        # If Armor piece or Accessory, equip into paperdoll!
                        if cat.startswith("armor_") or cat == CAT_ACCESSORY:
                            success, prev_item = player.equipment.equip(current, player.stats)
                            if success:
                                player.sound_manager.play("place")
                                self.slots[slot_idx] = prev_item if isinstance(prev_item, ItemStack) else (ItemStack(prev_item, 1) if prev_item else None)
                                return True

                    if not self.held_item:
                        if current:
                            if is_right_click and current.count > 1:
                                half = current.count // 2
                                self.held_item = current.clone(count=half)
                                current.count -= half
                            else:
                                self.held_item = current
                                self.slots[slot_idx] = None
                    else:
                        # If cursor holds an Affix Stone, click on eligible gear embeds it directly!
                        if self.held_item.item_id == "affix_stone" and current and not is_right_click:
                            from src.rpg.enhancement import can_apply_affix_stone, apply_affix_stone
                            can_app, reason = can_apply_affix_stone(current)
                            if can_app:
                                ok, msg = apply_affix_stone(current, self, player.sound_manager if player else None)
                                self.notify(msg)
                                return True
                            else:
                                self.notify(reason)
                                return True

                        if current is None:
                            if is_right_click and self.held_item.count > 1:
                                self.slots[slot_idx] = self.held_item.clone(count=1)
                                self.held_item.count -= 1
                            else:
                                self.slots[slot_idx] = self.held_item
                                self.held_item = None
                        elif current.item_id == self.held_item.item_id:
                            space = current.max_stack - current.count
                            if is_right_click:
                                if space > 0:
                                    current.count += 1
                                    self.held_item.count -= 1
                                    if self.held_item.count <= 0:
                                        self.held_item = None
                            else:
                                transfer = min(space, self.held_item.count)
                                current.count += transfer
                                self.held_item.count -= transfer
                                if self.held_item.count <= 0:
                                    self.held_item = None
                        else:
                            if not is_right_click:
                                self.slots[slot_idx] = self.held_item
                                self.held_item = current
                    return True
        return False

    def equip_item(self, slot_idx, player):
        """Programmatically equips the item in slot_idx into the player's equipment. Prevents equipping broken items."""
        if slot_idx < 0 or slot_idx >= len(self.slots):
            return False
        current = self.slots[slot_idx]
        if not current or not player:
            return False
        if getattr(current, "is_broken", False):
            self.notify("Cannot equip broken item! Repair it at the Mystic Trader first.")
            return False
        cat = current.data.get("cat", "")
        if cat.startswith("armor_") or cat in (CAT_ACCESSORY, CAT_WEAPON):
            success, prev_item = player.equipment.equip(current, player.stats)
            if success:
                if hasattr(player, "sound_manager") and player.sound_manager:
                    player.sound_manager.play("place")
                self.slots[slot_idx] = prev_item if isinstance(prev_item, ItemStack) else (ItemStack(prev_item, 1) if prev_item else None)
                return True
        return False

    def render_tooltip(self, target_surf, item, mx, my, player=None):
        """Renders rich RPG tooltip for an item or ItemStack with Compact and Detailed modes."""
        if isinstance(item, (int, float)) and not isinstance(my, (int, float)):
            item, mx, my = my, item, mx
        if player is None:
            player = getattr(self, "player", None)
        if not item:
            return []
        data = item.data if hasattr(item, "data") else {}
        name = data.get("name", getattr(item, "item_id", "Item"))
        rarity = str(data.get("rarity", "common")).lower()
        r_color = RARITY_COLORS.get(rarity, (220, 220, 220))
        cat = data.get("cat", "item").replace("_", " ").title()
        enh_lvl = getattr(item, "enhancement_level", 0)
        is_broken = getattr(item, "is_broken", False)
        is_compact = getattr(self, "tooltip_mode", "detailed") == "compact"

        rarity_tiers = {
            "common": "Tier I",
            "uncommon": "Tier II",
            "rare": "Tier III",
            "epic": "Tier IV",
            "legendary": "Tier V",
            "mythic": "Tier VI",
            "ancient": "Tier VII",
        }
        tier_str = data.get("tier") or rarity_tiers.get(rarity, "Tier I")

        lines = [(name, r_color, self.font_bold)]

        if is_compact:
            lines.append((f"[{rarity.upper()} {cat.upper()}]", r_color, self.font_sm))
            if data.get("damage", 0) > 0:
                lines.append((f"Power: {data['damage']} Damage", (255, 215, 100), self.font_sm))
            elif data.get("atk", 0) > 0:
                lines.append((f"Attack: +{data['atk']}", (255, 215, 100), self.font_sm))
            if data.get("def", 0) > 0:
                lines.append((f"Defense: +{data['def']}", (160, 230, 160), self.font_sm))
            if data.get("hp", 0) > 0:
                lines.append((f"Max HP: +{data['hp']}", (255, 120, 120), self.font_sm))
            if enh_lvl > 0:
                lines.append((f"+{enh_lvl} Enhanced", (80, 240, 255), self.font_sm))
            if is_broken:
                lines.append(("[BROKEN]", (255, 70, 70), self.font_sm))
        else:
            # Detailed Mode: Tier, base vs bonus stats, attack speed, crit, max stack, sell value, lore
            lines.append((f"[{tier_str.upper()} • {rarity.upper()} {cat.upper()}]", r_color, self.font_sm))

            if data.get("damage", 0) > 0:
                base_dmg = data['damage']
                if enh_lvl > 0:
                    bonus_dmg = int(base_dmg * (enh_lvl * 0.15))
                    lines.append((f"Damage: {base_dmg + bonus_dmg} (Base {base_dmg} + {bonus_dmg} Enhanced)", (255, 215, 100), self.font_sm))
                else:
                    lines.append((f"Damage: {base_dmg} (Base)", (255, 215, 100), self.font_sm))
            elif data.get("atk", 0) > 0:
                base_atk = data['atk']
                if enh_lvl > 0:
                    bonus_atk = int(base_atk * (enh_lvl * 0.15))
                    lines.append((f"Attack: +{base_atk + bonus_atk} (Base +{base_atk} + {bonus_atk} Enhanced)", (255, 215, 100), self.font_sm))
                else:
                    lines.append((f"Attack: +{base_atk} (Base)", (255, 215, 100), self.font_sm))

            if data.get("def", 0) > 0:
                base_def = data['def']
                if enh_lvl > 0:
                    bonus_def = int(base_def * (enh_lvl * 0.15))
                    lines.append((f"Defense: +{base_def + bonus_def} (Base +{base_def} + {bonus_def} Enhanced)", (160, 230, 160), self.font_sm))
                else:
                    lines.append((f"Defense: +{base_def} (Base)", (160, 230, 160), self.font_sm))

            if data.get("hp", 0) > 0:
                lines.append((f"Max HP: +{data['hp']}", (255, 120, 120), self.font_sm))

            if data.get("cat") in (CAT_WEAPON, CAT_TOOL) or "speed" in data:
                spd = data.get("speed", 0.0)
                spd_str = f"{spd:.2f}s swing cooldown" if spd > 0 else "0.35s (Standard fast attack)"
                lines.append((f"Attack Speed: {spd_str}", (190, 220, 245), self.font_sm))

            if data.get("cat") == CAT_WEAPON or "crit" in data:
                crit_pct = data.get("crit", 4.0)
                lines.append((f"Critical Strike: {crit_pct:.1f}%", (255, 200, 100), self.font_sm))

            max_s = data.get("max_stack", 999)
            lines.append((f"Max Stack: {max_s}", (175, 185, 200), self.font_sm))

            rarity_vals = {
                "common": 5, "uncommon": 15, "rare": 45, "epic": 140,
                "legendary": 450, "mythic": 1200, "ancient": 3000
            }
            sell_val = data.get("sell_value") or data.get("price") or rarity_vals.get(rarity, 5)
            lines.append((f"Sell Value: {sell_val} Copper", (240, 200, 80), self.font_sm))

            if enh_lvl > 0:
                lines.append((f"Enhanced: +{enh_lvl} (Double Stats at +7)", (80, 240, 255), self.font_sm))
            if is_broken:
                lines.append(("[BROKEN] Requires 1 Gold Coin repair at Mystic Trader!", (255, 70, 70), self.font_sm))

            # Rolled Base Stats indicator
            base_rolls = getattr(item, "base_rolls", None)
            if base_rolls:
                roll_parts = [f"+{v} {k.upper()}" for k, v in base_rolls.items()]
                lines.append((f"Rolled Base Stats: {', '.join(roll_parts)}", (255, 230, 140), self.font_sm))

            # Special Tags
            item_tags = getattr(item, "tags", None) or data.get("tags", [])
            if item_tags:
                from src.rpg.equipment_update import TAG_REGISTRY
                tag_labels = [TAG_REGISTRY.get(t, {}).get("display_name", t.replace("_", " ").title()) for t in item_tags]
                lines.append((f"Tags: {' • '.join(tag_labels)}", (100, 220, 255), self.font_sm))

            affix_slots = getattr(item, "affix_slots", 0)
            affixes = getattr(item, "affixes", [])
            aff_cnt = len(affixes)
            avail_slots = max(0, affix_slots - aff_cnt)

            from src.rpg.equipment_update import get_max_additional_slots
            max_add = get_max_additional_slots(rarity)
            cur_add = getattr(item, "additional_affix_slots", 0)
            avail_carve = max(0, max_add - cur_add) if max_add > 0 else 0

            if affix_slots > 0:
                slot_info = f"Affix Slots: {aff_cnt}/{affix_slots}"
                if avail_slots > 0:
                    slot_info += f" ({avail_slots} Available)"
                lines.append((slot_info, (255, 215, 80), self.font_sm))
                if avail_slots > 0:
                    lines.append((f"• [Available Slot] {avail_slots} Open for Affix Stones", (140, 240, 180), self.font_sm))
            elif max_add > 0:
                lines.append((f"Affix Slots: 0/0 (Carve at Mystic Trader)", (180, 190, 210), self.font_sm))

            # Additional Affix Slot Capacity
            if max_add > 0:
                lines.append((f"Carved Affix Slots: {cur_add}/{max_add} (Limit for {rarity.title()})", (200, 170, 240), self.font_sm))
                if avail_carve > 0:
                    lines.append((f"• [Available to Carve] {avail_carve} Slot(s) Open at Mystic Trader", (130, 220, 255), self.font_sm))
                else:
                    lines.append((f"• [Carve Limit Reached] Max {max_add} Slots Carved", (180, 170, 190), self.font_sm))

            from src.ui.theme import wrap_text_lines
            for aff in getattr(item, "affixes", []):
                from src.rpg.enhancement import GOD_TIER_AFFIXES
                aff_desc = GOD_TIER_AFFIXES.get(aff, {}).get("desc", "")
                for al in wrap_text_lines(f"★ {aff}: {aff_desc}", self.font_sm, 300):
                    lines.append((al, (255, 230, 90), self.font_sm))

            # Set Membership & Torchlight 2 Tiered Milestones
            from src.rpg.equipment_update import build_set_tooltip_lines
            raw_id = getattr(item, "item_id", item if isinstance(item, str) else "")
            set_lines = build_set_tooltip_lines(raw_id, player=player, font=self.font_sm, wrap_width=300)
            lines.extend(set_lines)

            desc = data.get("desc")
            if desc:
                for dl in wrap_text_lines(desc, self.font_sm, 300):
                    lines.append((dl, (200, 210, 225), self.font_sm))

            lore = data.get("lore")
            if lore:
                for ll in wrap_text_lines(lore, self.font_sm, 300):
                    lines.append((ll, (165, 180, 205), self.font_sm))

        # Determine Top-Right Badge & Subtitle Tag
        raw_id = str(getattr(item, "item_id", item if isinstance(item, str) else "")).lower()
        item_tags = list(getattr(item, "tags", None) or data.get("tags", []))

        try:
            from src.rpg.equipment_update import PROGRESSIVE_SETS
        except Exception:
            PROGRESSIVE_SETS = {}

        is_sds = ("seven_deadly_sins" in item_tags or any("sin_" in t for t in item_tags) or 
                  any(raw_id in PROGRESSIVE_SETS.get(k, {}).get("pieces", []) for k in (
                      "sin_pride", "sin_greed", "sin_lust", "sin_envy", "sin_gluttony", "sin_wrath", "sin_sloth")) or
                  any(raw_id.startswith(p) for p in ("wrath_", "pride_", "greed_", "envy_", "gluttony_", "lust_", "sloth_")))

        is_shv = ("seven_heavenly_virtues" in item_tags or any("virtue_" in t for t in item_tags) or 
                  any(raw_id in PROGRESSIVE_SETS.get(k, {}).get("pieces", []) for k in (
                      "virtue_humility", "virtue_charity", "virtue_chastity", "virtue_gratitude", "virtue_temperance", "virtue_kindness", "virtue_diligence", "virtue_patience")) or
                  any(raw_id.startswith(p) for p in ("patience_", "humility_", "charity_", "kindness_", "temperance_", "chastity_", "diligence_")))

        is_katipunero = ("katipunero" in item_tags or 
                         raw_id in ("katipunero_bolo", "barong_tagalog", "salakot", "bakya", "tabak", "kampilan", "balisong") or
                         raw_id in PROGRESSIVE_SETS.get("katipunero", {}).get("pieces", []))

        is_special = is_sds or is_shv or is_katipunero or "special" in item_tags or rarity in ("ancient", "mythic") or raw_id == "crown_of_potaria"

        top_badge = None
        top_badge_bg = (210, 135, 35)
        top_badge_border = (255, 210, 110)
        top_badge_text = (255, 255, 255)

        subtitle_tag = None
        subtitle_bg = (30, 30, 45)
        subtitle_border = (100, 120, 160)
        subtitle_text_col = (220, 230, 255)

        if is_sds:
            top_badge = "SDS"
            top_badge_bg = (195, 35, 45)
            top_badge_border = (255, 110, 120)
            subtitle_tag = "Seven Deadly Sins"
            subtitle_bg = (60, 15, 20)
            subtitle_border = (210, 60, 70)
            subtitle_text_col = (255, 170, 175)
        elif is_shv:
            top_badge = "SHV"
            top_badge_bg = (210, 160, 30)
            top_badge_border = (255, 225, 110)
            subtitle_tag = "Seven Heavenly Virtues"
            subtitle_bg = (50, 42, 12)
            subtitle_border = (220, 180, 50)
            subtitle_text_col = (255, 230, 140)
        elif is_katipunero:
            top_badge = "SPECIAL"
            top_badge_bg = (185, 75, 25)
            top_badge_border = (245, 175, 60)
            subtitle_tag = "Katipunero"
            subtitle_bg = (55, 24, 12)
            subtitle_border = (225, 105, 35)
            subtitle_text_col = (255, 205, 130)
        elif is_special:
            top_badge = "SPECIAL"
            top_badge_bg = (210, 135, 35)
            top_badge_border = (255, 210, 110)
            if rarity == "ancient":
                subtitle_tag = "Ancient Relic"
                subtitle_bg = (55, 30, 15)
                subtitle_border = (220, 140, 50)
                subtitle_text_col = (255, 215, 120)

        # Wrap text lines to prevent excessively wide tooltips
        from src.ui.theme import wrap_text_lines
        wrapped_lines = [lines[0]]
        for text, col, font in lines[1:]:
            text_str = str(text)
            if font.size(text_str)[0] > 290 and (" " in text_str or "•" in text_str):
                for wl in wrap_text_lines(text_str, font, 290):
                    wrapped_lines.append((wl, col, font))
            else:
                wrapped_lines.append((text_str, col, font))
        lines = wrapped_lines

        name_w = self.font_bold.size(lines[0][0])[0]
        badge_w = (self.font_sm.size(top_badge)[0] + 16) if top_badge else 0
        header_w = name_w + badge_w + 24
        subtitle_w = (self.font_sm.size(subtitle_tag)[0] + 20) if subtitle_tag else 0

        body_w = max([font.size(text)[0] for text, _, font in lines[1:]], default=0)
        content_w = max(header_w, subtitle_w, body_w)
        tw = max(180, min(340, content_w + 24))

        th = sum(font.get_height() + 2 for _, _, font in lines) + 14
        if subtitle_tag:
            th += self.font_sm.get_height() + 8

        tx = min(SCREEN_WIDTH - tw - 10, max(10, mx + 14))
        ty = my + 14
        if ty + th > SCREEN_HEIGHT - 10:
            ty = max(10, my - th - 8)
        if ty < 10:
            ty = 10

        bg_rect = pygame.Rect(tx, ty, tw, th)
        t_surf = pygame.Surface((tw, th), pygame.SRCALPHA)
        t_surf.fill((16, 20, 32, 240))
        target_surf.blit(t_surf, (tx, ty))
        pygame.draw.rect(target_surf, (75, 95, 135), bg_rect, 1, border_radius=4)

        cur_y = ty + 7
        # Draw header (name + optional top right badge)
        name_text, name_col, name_font = lines[0]
        rendered_name = name_font.render(name_text, True, name_col)
        target_surf.blit(rendered_name, (tx + 10, cur_y))

        if top_badge:
            b_surf = self.font_sm.render(top_badge, True, top_badge_text)
            bw = b_surf.get_width() + 12
            bh = b_surf.get_height() + 4
            bx = tx + tw - bw - 10
            by = cur_y - 1
            badge_rect = pygame.Rect(bx, by, bw, bh)
            pygame.draw.rect(target_surf, top_badge_bg, badge_rect, border_radius=4)
            pygame.draw.rect(target_surf, top_badge_border, badge_rect, 1, border_radius=4)
            target_surf.blit(b_surf, (bx + 6, by + 2))

        cur_y += rendered_name.get_height() + 3

        # Draw subtitle tag below item name if present
        if subtitle_tag:
            s_surf = self.font_sm.render(subtitle_tag, True, subtitle_text_col)
            sw = s_surf.get_width() + 12
            sh = s_surf.get_height() + 4
            sx = tx + 10
            sy = cur_y
            tag_box = pygame.Rect(sx, sy, sw, sh)
            pygame.draw.rect(target_surf, subtitle_bg, tag_box, border_radius=3)
            pygame.draw.rect(target_surf, subtitle_border, tag_box, 1, border_radius=3)
            target_surf.blit(s_surf, (sx + 6, sy + 2))
            cur_y += sh + 4

        for text, col, font in lines[1:]:
            rendered = font.render(text, True, col)
            target_surf.blit(rendered, (tx + 10, cur_y))
            cur_y += rendered.get_height() + 2
        return lines




def get_mining_damage(active_item, tile_id):
    """
    Calculates mining damage per swing based on tool type, tier power, and block category.
    - Axes excel on wood/trees/furniture (~1.2s wood axe, ~0.8s copper axe, ~0.5s iron axe)
    - Pickaxes excel on stone/ores/bricks
    - Shovels excel on dirt/sand/soils
    - Bare hands deal base damage (1.2 per hit, ~2.5s on wood)
    - High-tier tools scale effectively with power rating
    """
    if not tile_id or tile_id == TILE_AIR:
        return 0.0

    WOOD_TILES = {
        TILE_WOOD, TILE_WOOD_TRUNK, TILE_WOOD_PLANKS, TILE_WOOD_PLATFORM,
        TILE_WORK_BENCH, TILE_TABLE, TILE_CHAIR, TILE_BED, TILE_BOOKSHELF,
        TILE_DRESSER, TILE_DOOR_CLOSED, TILE_DOOR_OPEN, TILE_GRANDFATHER_CLOCK,
        TILE_WOOD_SHELF, TILE_BATHTUB, TILE_SINK, TILE_ROPE_RUNGS
    }

    STONE_TILES = {
        TILE_STONE, TILE_STONE_BRICK, TILE_COPPER_ORE, TILE_IRON_ORE, TILE_GOLD_ORE,
        TILE_DUNGEON_BRICK, TILE_DUNGEON_ALTAR, TILE_BLIGHTSTONE, TILE_EBONSTONE,
        TILE_FIREPLACE, TILE_FURNACE, TILE_CHEST, TILE_IRON_CHEST, TILE_ROOF_TILES, TILE_ICE
    }

    DIRT_TILES = {
        TILE_DIRT, TILE_GRASS, TILE_SAND, TILE_SANDSTONE, TILE_SNOW,
        TILE_BLIGHT_GRASS, TILE_CORRUPT_GRASS, TILE_MUSHROOM_GRASS,
        TILE_MUSHROOM_STEM, TILE_MUSHROOM_CAP, TILE_CACTUS
    }

    FRAGILE_TILES = {
        TILE_LEAVES, TILE_TORCH, TILE_GLASS, TILE_CANDELABRA, TILE_CHANDELIER,
        TILE_POTTED_PLANT, TILE_TAPESTRY, TILE_PAINTING, TILE_SAPLING, TILE_ROPE_RUNGS,
        TILE_CARVED_TUBER_LANTERN, TILE_BRASS_LANTERN, TILE_SPECTRAL_LANTERN
    }

    # Fragile decorative blocks break very easily with any tool or hand
    if tile_id in FRAGILE_TILES:
        return 10.0

    # Bare hands (active_item is None) - limited to wood and dirt only (anti-softlock for crafting tools)
    if not active_item:
        if tile_id in WOOD_TILES or tile_id in DIRT_TILES:
            return 1.2
        return 0.0

    item_id = active_item.item_id if hasattr(active_item, "item_id") else str(active_item)
    data = active_item.data if hasattr(active_item, "data") else {}
    cat = data.get("cat")

    # If holding a non-tool (weapon, potion, block, etc.), cannot mine
    if cat != CAT_TOOL and not any(w in item_id for w in ("pickaxe", "axe", "shovel", "drill")):
        return 0.0

    power = float(data.get("power", 10))

    is_axe = ("axe" in item_id and "pickaxe" not in item_id)
    is_pickaxe = ("pickaxe" in item_id or "drill" in item_id)
    is_shovel = ("shovel" in item_id or "spade" in item_id)

    # Check matching category
    if is_axe and tile_id in WOOD_TILES:
        dmg = power * 0.26
        if power >= 50:
            dmg = max(dmg, 25.0)
        elif power >= 35:
            dmg = max(dmg, 10.5)
        return round(dmg, 2)

    elif is_pickaxe and tile_id in STONE_TILES:
        dmg = power * 0.26
        if power >= 50:
            dmg = max(dmg, 20.0)
        elif power >= 35:
            dmg = max(dmg, 12.0)
        return round(dmg, 2)

    elif is_shovel and tile_id in DIRT_TILES:
        dmg = power * 0.26
        if power >= 50:
            dmg = max(dmg, 20.0)
        elif power >= 20:
            dmg = max(dmg, 6.0)
        return round(dmg, 2)

    # Secondary proficiencies (e.g. pickaxe on dirt/wood)
    if is_pickaxe and tile_id in DIRT_TILES:
        return round(max(1.2, power * 0.20), 2)
    if is_pickaxe and tile_id in WOOD_TILES:
        return round(max(1.2, power * 0.10), 2)
    if is_axe and tile_id in DIRT_TILES:
        return 1.2
    if is_shovel and tile_id in (WOOD_TILES | STONE_TILES):
        return 1.2

    # Tool on unmatched tile: fallback to hand damage
    return 1.2


# -----------------------------------------------------------------------------
# Auto-register all expansion equipment into ITEM_REGISTRY and ARMOR_DATA
# -----------------------------------------------------------------------------
try:
    from src.rpg.equipment_update import register_new_equipment_into_catalogs
    register_new_equipment_into_catalogs()
except Exception:
    pass


