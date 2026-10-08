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
    WALL_WOOD, WALL_STONE_BRICK, WALL_GLASS,
    RARITY_COMMON, RARITY_UNCOMMON, RARITY_RARE, RARITY_EPIC,
    RARITY_MYTHIC, RARITY_LEGENDARY, RARITY_ANCIENT, RARITY_HEX_COLORS, RARITY_COLORS
)

# Backwards compatibility and anti-plagiarism alias mapping
ITEM_ALIASES = {
    "starfury": "astral_wrath",
    "hermes_boots": "zephyr_striders",
    "gel": "spud_sap",
    "mana_flower": "arcane_orchid",
    "band_of_regeneration": "talisman_of_vigor",
    "ebonstone_block": "blightstone_block",
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
    "celestial_fragment": "portal_shard",
    "celestial_fragments": "portal_shard",
    "dirt": "dirt_block",
    "tile_wood": "wood",
    "arrow": "wooden_arrow",
    "iron_sword": "iron_broadsword",
    "star": "fallen_star",
    "falling_star": "fallen_star",
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
        "desc": "Equipped with a bright headlamp that illuminates subterranean caverns.",
        "lore": "'Never fear the underground dark again.'",
        "special": "Portable Cavern Light Source"
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
        "desc": "Place to store keepsakes, or right-click when found in caves to claim rich loot!",
        "lore": "'Holds the forgotten relics of past adventurers.'",
        "special": "Treasure Container"
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
        "rarity": RARITY_EPIC,
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
    def __init__(self, item_id, count=1):
        self.item_id = item_id
        self.count = count

    @property
    def data(self):
        canon = ITEM_ALIASES.get(self.item_id, self.item_id)
        return ITEM_REGISTRY.get(self.item_id) or ITEM_REGISTRY.get(canon, {})

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
        self.held_item = None
        if difficulty == "normal":
            # Normal: Starts with a basic axe. Destroy trees to craft workbench/swords/tools.
            self.slots[0] = ItemStack("wood_axe", 1)
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

    def can_add_item(self, item_id, count=1):
        """Returns True if the inventory has sufficient slot or stack capacity to hold count items."""
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

    def add_item(self, item_id, count=1):
        # Coins deposit directly into the dedicated Coin Purse without occupying inventory slots
        if item_id == "copper_coin":
            self.add_coins(copper=count)
            return 0
        elif item_id == "silver_coin":
            self.add_coins(silver=count)
            return 0
        elif item_id == "gold_coin":
            self.add_coins(gold=count)
            return 0

        data = ITEM_REGISTRY.get(item_id, {})
        max_s = data.get("max_stack", 999)

        for slot in self.slots:
            if slot and slot.item_id == item_id and slot.count < max_s:
                space = max_s - slot.count
                transfer = min(space, count)
                slot.count += transfer
                count -= transfer
                if count <= 0:
                    return 0

        for idx in range(len(self.slots)):
            if self.slots[idx] is None:
                transfer = min(max_s, count)
                self.slots[idx] = ItemStack(item_id, transfer)
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

                        # If Armor piece or Accessory, equip into paperdoll!
                        if cat.startswith("armor_") or cat == CAT_ACCESSORY:
                            success, prev_item = player.equipment.equip(item_id, player.stats)
                            if success:
                                player.sound_manager.play("place")
                                self.slots[slot_idx] = ItemStack(prev_item, 1) if prev_item else None
                                return True

                    if not self.held_item:
                        if current:
                            if is_right_click and current.count > 1:
                                half = current.count // 2
                                self.held_item = ItemStack(current.item_id, half)
                                current.count -= half
                            else:
                                self.held_item = current
                                self.slots[slot_idx] = None
                    else:
                        if current is None:
                            if is_right_click and self.held_item.count > 1:
                                self.slots[slot_idx] = ItemStack(self.held_item.item_id, 1)
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
        TILE_WOOD_SHELF, TILE_BATHTUB, TILE_SINK
    }

    STONE_TILES = {
        TILE_STONE, TILE_STONE_BRICK, TILE_COPPER_ORE, TILE_IRON_ORE, TILE_GOLD_ORE,
        TILE_DUNGEON_BRICK, TILE_DUNGEON_ALTAR, TILE_BLIGHTSTONE, TILE_EBONSTONE,
        TILE_FIREPLACE, TILE_FURNACE, TILE_CHEST, TILE_ROOF_TILES, TILE_ICE
    }

    DIRT_TILES = {
        TILE_DIRT, TILE_GRASS, TILE_SAND, TILE_SANDSTONE, TILE_SNOW,
        TILE_BLIGHT_GRASS, TILE_CORRUPT_GRASS, TILE_MUSHROOM_GRASS,
        TILE_MUSHROOM_STEM, TILE_MUSHROOM_CAP, TILE_CACTUS
    }

    FRAGILE_TILES = {
        TILE_LEAVES, TILE_TORCH, TILE_GLASS, TILE_CANDELABRA, TILE_CHANDELIER,
        TILE_POTTED_PLANT, TILE_TAPESTRY, TILE_PAINTING
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

