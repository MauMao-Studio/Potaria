"""
Potaria - Equipment & Paperdoll Engine (Chroisen Style)
Manages Head, Chest, Legs, Weapon, and Accessory equipment slots,
and recalculates player stat bonuses dynamically.
Developer: Kurados
"""

SLOT_HEAD = "head"
SLOT_CHEST = "chest"
SLOT_LEGS = "legs"
SLOT_WEAPON = "weapon"
SLOT_ACCESSORY = "accessory"
_NO_UPDATE = object()

# Equipment Catalog with RPG Stats
ARMOR_DATA = {
    # HELMETS
    "potato_cap": {"slot": SLOT_HEAD, "name": "Potato Cap", "def": 1, "hp": 5, "atk": 0, "crit": 0, "speed": 0},
    "cactus_helmet": {"slot": SLOT_HEAD, "name": "Cactus Helmet", "def": 2, "hp": 8, "atk": 1, "crit": 0, "speed": 0},
    "copper_helmet": {"slot": SLOT_HEAD, "name": "Copper Helmet", "def": 1, "hp": 10, "atk": 1, "crit": 0, "speed": 0},
    "frost_hood": {"slot": SLOT_HEAD, "name": "Frost Hood", "def": 6, "hp": 20, "atk": 2, "crit": 2.0, "speed": 0, "mp_regen": 0.8},
    "iron_helmet": {"slot": SLOT_HEAD, "name": "Iron Helmet", "def": 7, "hp": 20, "atk": 2, "crit": 0, "speed": 0},
    "gold_helmet": {"slot": SLOT_HEAD, "name": "Gold Helmet", "def": 10, "hp": 30, "atk": 3, "crit": 3.0, "speed": 0},
    "miner_helmet": {"slot": SLOT_HEAD, "name": "Potato Miner Helmet", "def": 3, "hp": 10, "atk": 0, "crit": 0, "speed": 0, "light": True},
    "shadow_helmet": {"slot": SLOT_HEAD, "name": "Shadow Helmet", "def": 12, "hp": 35, "atk": 4, "crit": 4.0, "speed": 0.1},
    "magma_helmet": {"slot": SLOT_HEAD, "name": "Magma Helmet", "def": 14, "hp": 45, "atk": 5, "crit": 4.0, "speed": 0.1},
    "cryo_helmet": {"slot": SLOT_HEAD, "name": "Cryo Visor", "def": 16, "hp": 50, "atk": 4, "crit": 3.0, "speed": 0.0},
    "necro_helmet": {"slot": SLOT_HEAD, "name": "Necro Bone Crown", "def": 13, "hp": 40, "atk": 7, "crit": 7.0, "speed": 0.15},
    "titan_helmet": {"slot": SLOT_HEAD, "name": "Celestial Titan Helm", "def": 26, "hp": 80, "atk": 15, "crit": 10.0, "speed": 0.35},
    "crown_of_potaria": {"slot": SLOT_HEAD, "name": "Crown of Potaria", "def": 22, "hp": 60, "atk": 12, "crit": 8.0, "speed": 0.4},
    "ancient_helmet": {"slot": SLOT_HEAD, "name": "Ancient Helm of Eternity", "def": 30, "hp": 100, "atk": 18, "crit": 12.0, "speed": 0.4, "rarity": "ancient", "effects": ["Ancient Sight", "Radiant Gleam"]},

    # CHESTPLATES
    "potato_tunic": {"slot": SLOT_CHEST, "name": "Potato Tunic", "def": 2, "hp": 10, "atk": 0, "crit": 0, "speed": 0},
    "cactus_chestplate": {"slot": SLOT_CHEST, "name": "Cactus Chestplate", "def": 4, "hp": 15, "atk": 1, "crit": 0, "speed": 0},
    "copper_chestplate": {"slot": SLOT_CHEST, "name": "Copper Chestplate", "def": 1, "hp": 15, "atk": 2, "crit": 0, "speed": 0},
    "frost_parka": {"slot": SLOT_CHEST, "name": "Frost Parka", "def": 8, "hp": 30, "atk": 2, "crit": 0, "speed": 0},
    "iron_chestplate": {"slot": SLOT_CHEST, "name": "Iron Chestplate", "def": 10, "hp": 30, "atk": 3, "crit": 0, "speed": 0},
    "gold_chestplate": {"slot": SLOT_CHEST, "name": "Gold Chestplate", "def": 14, "hp": 45, "atk": 5, "crit": 4.0, "speed": 0},
    "shadow_plate": {"slot": SLOT_CHEST, "name": "Shadow Plate", "def": 16, "hp": 50, "atk": 5, "crit": 3.0, "speed": 0},
    "magma_chestplate": {"slot": SLOT_CHEST, "name": "Magma Cuirass", "def": 19, "hp": 60, "atk": 7, "crit": 4.0, "speed": 0},
    "cryo_chestplate": {"slot": SLOT_CHEST, "name": "Cryo Carapace", "def": 22, "hp": 70, "atk": 5, "crit": 2.0, "speed": 0},
    "necro_chestplate": {"slot": SLOT_CHEST, "name": "Necro Bone Plate", "def": 18, "hp": 55, "atk": 9, "crit": 6.0, "speed": 0.1},
    "titan_chestplate": {"slot": SLOT_CHEST, "name": "Celestial Titan Plate", "def": 32, "hp": 100, "atk": 18, "crit": 8.0, "speed": 0.3},
    "ancient_chestplate": {"slot": SLOT_CHEST, "name": "Ancient Plate of Ages", "def": 38, "hp": 120, "atk": 22, "crit": 10.0, "speed": 0.3, "rarity": "ancient", "effects": ["Aegis of the Forgotten", "Supernova Ward"]},

    # LEGGINGS / BOOTS
    "potato_pants": {"slot": SLOT_LEGS, "name": "Potato Pants", "def": 1, "hp": 5, "atk": 0, "crit": 0, "speed": 0.1},
    "cactus_greaves": {"slot": SLOT_LEGS, "name": "Cactus Greaves", "def": 3, "hp": 10, "atk": 0, "crit": 0, "speed": 0.15},
    "copper_greaves": {"slot": SLOT_LEGS, "name": "Copper Greaves", "def": 1, "hp": 10, "atk": 0, "crit": 0, "speed": 0.2},
    "iron_greaves": {"slot": SLOT_LEGS, "name": "Iron Greaves", "def": 7, "hp": 20, "atk": 1, "crit": 0, "speed": 0.25},
    "gold_greaves": {"slot": SLOT_LEGS, "name": "Gold Greaves", "def": 10, "hp": 30, "atk": 2, "crit": 3.0, "speed": 0.35},
    "shadow_greaves": {"slot": SLOT_LEGS, "name": "Shadow Greaves", "def": 11, "hp": 32, "atk": 3, "crit": 4.0, "speed": 0.3},
    "magma_greaves": {"slot": SLOT_LEGS, "name": "Magma Greaves", "def": 13, "hp": 40, "atk": 4, "crit": 2.0, "speed": 0.35},
    "cryo_greaves": {"slot": SLOT_LEGS, "name": "Cryo Striders", "def": 15, "hp": 45, "atk": 3, "crit": 2.0, "speed": 0.3},
    "necro_greaves": {"slot": SLOT_LEGS, "name": "Necro Bone Greaves", "def": 12, "hp": 35, "atk": 5, "crit": 5.0, "speed": 0.45},
    "titan_greaves": {"slot": SLOT_LEGS, "name": "Celestial Titan Greaves", "def": 22, "hp": 60, "atk": 11, "crit": 6.0, "speed": 0.65},
    "ancient_greaves": {"slot": SLOT_LEGS, "name": "Ancient Greaves of the Cosmos", "def": 26, "hp": 80, "atk": 14, "crit": 8.0, "speed": 0.7, "rarity": "ancient", "effects": ["Timeless Stride (+70% Speed)", "Ancient Grace"]},
    "speed_boots": {"slot": SLOT_LEGS, "name": "Rootrunner Boots", "def": 4, "hp": 15, "atk": 0, "crit": 2.0, "speed": 0.75},
    "zephyr_striders": {"slot": SLOT_LEGS, "name": "Zephyr Striders", "def": 5, "hp": 20, "atk": 2, "crit": 4.0, "speed": 1.15, "rarity": "epic", "effects": ["+115% Sprint Speed"]},
    "hermes_boots": {"slot": SLOT_LEGS, "name": "Zephyr Striders", "def": 5, "hp": 20, "atk": 2, "crit": 4.0, "speed": 1.15, "rarity": "epic", "effects": ["+115% Sprint Speed"]},

    # ACCESSORIES
    "warrior_charm": {"slot": SLOT_ACCESSORY, "name": "Warrior Charm", "def": 2, "hp": 20, "atk": 8, "crit": 4.0, "speed": 0},
    "guardian_ring": {"slot": SLOT_ACCESSORY, "name": "Guardian Ring", "def": 8, "hp": 35, "atk": 0, "crit": 0, "speed": 0},
    "talisman_of_vigor": {"slot": SLOT_ACCESSORY, "name": "Talisman of Vigor", "def": 4, "hp": 40, "atk": 2, "crit": 2.0, "speed": 0, "mp_regen": 1.0, "rarity": "epic", "effects": ["Life Surge (+2 HP/s)"]},
    "band_of_regeneration": {"slot": SLOT_ACCESSORY, "name": "Talisman of Vigor", "def": 4, "hp": 40, "atk": 2, "crit": 2.0, "speed": 0, "mp_regen": 1.0, "rarity": "epic", "effects": ["Life Surge (+2 HP/s)"]},
    "arcane_orchid": {"slot": SLOT_ACCESSORY, "name": "Arcane Orchid", "def": 3, "hp": 25, "atk": 6, "crit": 5.0, "speed": 0, "mp_regen": 2.5, "rarity": "epic", "effects": ["Arcane Conduit (-20% MP Cost)"]},
    "mana_flower": {"slot": SLOT_ACCESSORY, "name": "Arcane Orchid", "def": 3, "hp": 25, "atk": 6, "crit": 5.0, "speed": 0, "mp_regen": 2.5, "rarity": "epic", "effects": ["Arcane Conduit (-20% MP Cost)"]},
    "lucky_clover": {"slot": SLOT_ACCESSORY, "name": "Lucky Clover", "def": 2, "hp": 15, "atk": 4, "crit": 15.0, "speed": 0.2},
    "celestial_emblem": {"slot": SLOT_ACCESSORY, "name": "Celestial Emblem", "def": 6, "hp": 50, "atk": 16, "crit": 8.0, "speed": 0.3, "mp_regen": 1.8},
    "titans_ring": {"slot": SLOT_ACCESSORY, "name": "Titan's Ring", "def": 14, "hp": 65, "atk": 10, "crit": 4.0, "speed": 0.1},
    "volcanic_stone": {"slot": SLOT_ACCESSORY, "name": "Volcanic Magma Stone", "def": 5, "hp": 35, "atk": 13, "crit": 6.0, "speed": 0.1},
    "frost_amulet": {"slot": SLOT_ACCESSORY, "name": "Glacial Frost Amulet", "def": 11, "hp": 45, "atk": 6, "crit": 4.0, "speed": 0, "mp_regen": 1.2},

    # WEAPONS
    "wooden_sword": {"slot": SLOT_WEAPON, "name": "Wooden Sword", "def": 0, "hp": 0, "atk": 7, "crit": 2.0, "speed": 0, "rarity": "common", "lore": "'A humble blade carved from sturdy timber, trusted by fledgling adventurers.'"},
    "wood_sword": {"slot": SLOT_WEAPON, "name": "Wooden Sword", "def": 0, "hp": 0, "atk": 7, "crit": 2.0, "speed": 0, "rarity": "common", "lore": "'A humble blade carved from sturdy timber, trusted by fledgling adventurers.'"},
    "copper_shortsword": {"slot": SLOT_WEAPON, "name": "Copper Shortsword", "def": 0, "hp": 0, "atk": 8, "crit": 2.0, "speed": 0},
    "cactus_sword": {"slot": SLOT_WEAPON, "name": "Cactus Sword", "def": 0, "hp": 0, "atk": 12, "crit": 3.0, "speed": 0},
    "copper_broadsword": {"slot": SLOT_WEAPON, "name": "Copper Broadsword", "def": 0, "hp": 0, "atk": 14, "crit": 3.0, "speed": 0},
    "iron_broadsword": {"slot": SLOT_WEAPON, "name": "Iron Broadsword", "def": 0, "hp": 0, "atk": 18, "crit": 4.0, "speed": 0},
    "frost_blade": {"slot": SLOT_WEAPON, "name": "Frost Blade", "def": 2, "hp": 10, "atk": 18, "crit": 5.0, "speed": 0},
    "sandstorm_spear": {"slot": SLOT_WEAPON, "name": "Sandstorm Spear", "def": 0, "hp": 0, "atk": 20, "crit": 6.0, "speed": 0},
    "gold_broadsword": {"slot": SLOT_WEAPON, "name": "Gold Broadsword", "def": 0, "hp": 0, "atk": 22, "crit": 6.0, "speed": 0},
    "shadow_cleaver": {"slot": SLOT_WEAPON, "name": "Shadow Cleaver", "def": 0, "hp": 0, "atk": 28, "crit": 8.0, "speed": 0.1},
    "magma_greatsword": {"slot": SLOT_WEAPON, "name": "Magma Greatsword", "def": 2, "hp": 25, "atk": 38, "crit": 10.0, "speed": 0.15},
    "bone_scythe": {"slot": SLOT_WEAPON, "name": "Bone Scythe", "def": 0, "hp": 15, "atk": 35, "crit": 14.0, "speed": 0.2},
    "starch_blade": {"slot": SLOT_WEAPON, "name": "Starch Blade", "def": 0, "hp": 25, "atk": 32, "crit": 10.0, "speed": 0.2},
    "astral_wrath": {"slot": SLOT_WEAPON, "name": "Astral Wrath", "def": 2, "hp": 15, "atk": 38, "crit": 12.0, "speed": 0.2, "rarity": "legendary", "lore": "'Forged in cosmic crucibles when falling meteors first pierced the heavens.'", "effects": ["Summons Celestial Star on swing", "AoE 72px Starburst Explosion"]},
    "starfury": {"slot": SLOT_WEAPON, "name": "Astral Wrath", "def": 2, "hp": 15, "atk": 38, "crit": 12.0, "speed": 0.2, "rarity": "legendary", "lore": "'Forged in cosmic crucibles when falling meteors first pierced the heavens.'", "effects": ["Summons Celestial Star on swing", "AoE 72px Starburst Explosion"]},
    "void_edge": {"slot": SLOT_WEAPON, "name": "Void Edge", "def": 4, "hp": 35, "atk": 50, "crit": 16.0, "speed": 0.3},
    "celestial_greatsword": {"slot": SLOT_WEAPON, "name": "Celestial Titan Greatsword", "def": 8, "hp": 55, "atk": 62, "crit": 20.0, "speed": 0.35},
    "wood_bow": {"slot": SLOT_WEAPON, "name": "Wood Bow", "def": 0, "hp": 0, "atk": 8, "crit": 2.0, "speed": 0},
    "bone_bow": {"slot": SLOT_WEAPON, "name": "Bone Bow", "def": 0, "hp": 0, "atk": 16, "crit": 4.0, "speed": 0},
    "magma_bow": {"slot": SLOT_WEAPON, "name": "Magma Bow", "def": 0, "hp": 10, "atk": 26, "crit": 8.0, "speed": 0.1},
    "celestial_bow": {"slot": SLOT_WEAPON, "name": "Celestial Titan Bow", "def": 4, "hp": 25, "atk": 42, "crit": 15.0, "speed": 0.25},
    "fire_staff": {"slot": SLOT_WEAPON, "name": "Fire Staff", "def": 0, "hp": 0, "atk": 30, "crit": 6.0, "speed": 0},
    "frost_staff": {"slot": SLOT_WEAPON, "name": "Frost Staff", "def": 0, "hp": 0, "atk": 28, "crit": 6.0, "speed": 0},
    "void_scepter": {"slot": SLOT_WEAPON, "name": "Void Scepter", "def": 3, "hp": 20, "atk": 46, "crit": 12.0, "speed": 0.2},
    "nether_cleaver": {"slot": SLOT_WEAPON, "name": "Nether Cleaver", "def": 5, "hp": 40, "atk": 45, "crit": 14.0, "speed": 0.25},
    "ancient_sword": {"slot": SLOT_WEAPON, "name": "Ancient Sword", "def": 4, "hp": 25, "atk": 42, "crit": 12.0, "speed": 0.25, "rarity": "ancient", "effects": ["Freezing Needles (Pierces through enemies)", "Molten Blaze (+12 Fire Damage over 3s)", "Armor Penetration (+15 True Damage)"]},
    "ancient_sword_1": {"slot": SLOT_WEAPON, "name": "Ancient Sword", "def": 4, "hp": 25, "atk": 42, "crit": 12.0, "speed": 0.25, "rarity": "ancient", "effects": ["Freezing Needles (Pierces through enemies)", "Molten Blaze (+12 Fire Damage over 3s)", "Armor Penetration (+15 True Damage)"]},

    # v1.5.0 Expansion Equipment & Accessories
    "oak_buckler": {"slot": SLOT_ACCESSORY, "name": "Oak Buckler", "def": 3, "hp": 10, "atk": 0, "crit": 0, "speed": 0, "rarity": "common"},
    "iron_aegis": {"slot": SLOT_ACCESSORY, "name": "Iron Aegis", "def": 7, "hp": 25, "atk": 0, "crit": 0, "speed": 0, "rarity": "uncommon"},
    "arbalest_repeater": {"slot": SLOT_WEAPON, "name": "Arbalest Repeater", "def": 0, "hp": 0, "atk": 24, "crit": 5.0, "speed": 0.15, "rarity": "uncommon"},
    "copper_harvester_sickle": {"slot": SLOT_WEAPON, "name": "Copper Harvester Sickle", "def": 0, "hp": 0, "atk": 10, "crit": 3.0, "speed": 0, "rarity": "common"},
    "totem_of_resurgence": {"slot": SLOT_ACCESSORY, "name": "Totem of Resurgence", "def": 4, "hp": 40, "atk": 0, "crit": 0, "speed": 0, "rarity": "mythic"},
    "explorers_satchel": {"slot": SLOT_ACCESSORY, "name": "Explorer's Satchel", "def": 1, "hp": 15, "atk": 0, "crit": 0, "speed": 0, "rarity": "common"},
    "magnetic_lodestone": {"slot": SLOT_ACCESSORY, "name": "Magnetic Lodestone", "def": 1, "hp": 0, "atk": 0, "crit": 0, "speed": 0, "rarity": "uncommon"},
    "brass_far_seer": {"slot": SLOT_ACCESSORY, "name": "Brass Far-Seer", "def": 0, "hp": 0, "atk": 2, "crit": 4.0, "speed": 0, "rarity": "uncommon"},
    "solar_chronometer": {"slot": SLOT_ACCESSORY, "name": "Solar Chronometer", "def": 0, "hp": 0, "atk": 0, "crit": 2.0, "speed": 0, "rarity": "rare"},
    "spud_quiver": {"slot": SLOT_ACCESSORY, "name": "Spud Hunter's Quiver", "def": 0, "hp": 0, "atk": 2, "crit": 3.0, "speed": 0, "rarity": "common"},
    "fiber_clippers": {"slot": SLOT_WEAPON, "name": "Fiber Clippers", "def": 0, "hp": 0, "atk": 4, "crit": 1.0, "speed": 0, "rarity": "common"},
    "pyrite_sparker": {"slot": SLOT_WEAPON, "name": "Pyrite Sparker", "def": 0, "hp": 0, "atk": 3, "crit": 1.0, "speed": 0, "rarity": "common"},
    "spud_angler_rod": {"slot": SLOT_WEAPON, "name": "Spud Angler Rod", "def": 0, "hp": 0, "atk": 2, "crit": 1.0, "speed": 0, "rarity": "common"},
}

def load_equipment_catalog():
    import os, json
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    data_dir = os.path.join(base_dir, "data")
    weapons_file = os.path.join(data_dir, "weapons.json")
    equipments_file = os.path.join(data_dir, "equipments.json")

    slot_map = {
        "head": SLOT_HEAD,
        "chest": SLOT_CHEST,
        "legs": SLOT_LEGS,
        "accessory": SLOT_ACCESSORY,
        "weapon": SLOT_WEAPON
    }

    if os.path.exists(weapons_file):
        try:
            with open(weapons_file, "r", encoding="utf-8") as f:
                for w in json.load(f):
                    ARMOR_DATA[w["id"]] = {
                        "slot": SLOT_WEAPON,
                        "name": w["name"],
                        "def": w.get("def", 0),
                        "hp": w.get("hp", 0),
                        "atk": w.get("atk", 0),
                        "crit": w.get("crit", 0.0),
                        "speed": w.get("speed", 0.0),
                        "mp_regen": w.get("mp_regen", 0.0),
                        "rarity": w.get("rarity", "common"),
                        "effects": w.get("effects", []),
                        "lore": w.get("lore", "")
                    }
        except Exception as e:
            pass

    if os.path.exists(equipments_file):
        try:
            with open(equipments_file, "r", encoding="utf-8") as f:
                for eq in json.load(f):
                    c = eq.get("cat", "accessory")
                    slot = slot_map.get(c, SLOT_ACCESSORY)
                    ARMOR_DATA[eq["id"]] = {
                        "slot": slot,
                        "name": eq["name"],
                        "def": eq.get("def", 0),
                        "hp": eq.get("hp", 0),
                        "atk": eq.get("atk", 0),
                        "crit": eq.get("crit", 0.0),
                        "speed": eq.get("speed", 0.0),
                        "mp_regen": eq.get("mp_regen", 0.0),
                        "rarity": eq.get("rarity", "common"),
                        "effects": eq.get("effects", []),
                        "lore": eq.get("lore", "")
                    }
        except Exception as e:
            pass

    # Ensure all hardcoded and loaded armor pieces are registered in ITEM_REGISTRY
    try:
        from src.ui.inventory import ITEM_REGISTRY, RARITY_ANCIENT, RARITY_HEX_COLORS
        for eq_id, eq_data in ARMOR_DATA.items():
            if eq_id not in ITEM_REGISTRY:
                c = eq_data.get("slot", "accessory")
                cat_str = f"armor_{c}" if c in ("head", "chest", "legs") else ("weapon" if c == "weapon" else "accessory")
                rarity = eq_data.get("rarity", "common")
                ITEM_REGISTRY[eq_id] = {
                    "name": eq_data.get("name", eq_id.replace("_", " ").title()),
                    "cat": cat_str,
                    "power": 0,
                    "damage": eq_data.get("atk", 0),
                    "atk": eq_data.get("atk", 0),
                    "def": eq_data.get("def", 0),
                    "crit": eq_data.get("crit", 0.0),
                    "speed": eq_data.get("speed", 0.0),
                    "hp": eq_data.get("hp", 0),
                    "mp": 0,
                    "mp_regen": eq_data.get("mp_regen", 0.0),
                    "max_stack": 1,
                    "tile": None,
                    "rarity": rarity,
                    "color": RARITY_HEX_COLORS.get(rarity, "#9E9E9E"),
                    "desc": f"A {rarity.title()} {c} piece.",
                    "lore": eq_data.get("lore", ""),
                    "effects": eq_data.get("effects", []),
                    "special": " • ".join(eq_data.get("effects", [])),
                }
    except Exception:
        pass

load_equipment_catalog()

EQUIPMENT_SETS = {
    "ancient": {
        "name": "Ancient Resonating Set",
        "pieces": {"head": "ancient_helmet", "chest": "ancient_chestplate", "legs": "ancient_greaves"},
        "desc": "Full Set: Ancient Cosmic Resonance (+35% ATK, +30% DEF, +50 HP, +20% Crit, Radiant Pulsing Aura)",
        "atk_mult": 0.35,
        "def_mult": 0.30,
        "bonus_hp": 50,
        "bonus_crit": 20.0,
        "aura": "ancient",
    },
    "titan": {
        "name": "Celestial Titan Set",
        "pieces": {"head": "titan_helmet", "chest": "titan_chestplate", "legs": "titan_greaves"},
        "desc": "Full Set: Celestial Aegis (+25% DEF, +30 HP, +15% ATK, Celestial Ward Aura)",
        "atk_mult": 0.15,
        "def_mult": 0.25,
        "bonus_hp": 30,
        "bonus_crit": 5.0,
        "aura": "titan",
    },
    "magma": {
        "name": "Magma Core Set",
        "pieces": {"head": "magma_helmet", "chest": "magma_chestplate", "legs": "magma_greaves"},
        "desc": "Full Set: Molten Crucible (+20% ATK, +15 Fire Thorns, Magma Aura)",
        "atk_mult": 0.20,
        "def_mult": 0.10,
        "bonus_hp": 25,
        "bonus_crit": 8.0,
        "aura": "magma",
    },
    "cryo": {
        "name": "Cryo Carapace Set",
        "pieces": {"head": "cryo_helmet", "chest": "cryo_chestplate", "legs": "cryo_greaves"},
        "desc": "Full Set: Glacial Bastion (+20% DEF, +2.5 MP/s Regen, Cryo Aura)",
        "atk_mult": 0.05,
        "def_mult": 0.20,
        "bonus_hp": 35,
        "bonus_crit": 5.0,
        "bonus_mp_regen": 2.5,
        "aura": "cryo",
    },
    "shadow": {
        "name": "Umbral Shadow Set",
        "pieces": {"head": "shadow_helmet", "chest": "shadow_plate", "legs": "shadow_greaves"},
        "desc": "Full Set: Shadow Phantom (+20% Crit, +20% ATK, +0.2 Speed, Void Aura)",
        "atk_mult": 0.20,
        "def_mult": 0.10,
        "bonus_hp": 20,
        "bonus_crit": 20.0,
        "bonus_speed": 0.2,
        "aura": "shadow",
    },
    "spud": {
        "name": "Spud Sovereign Set",
        "pieces": {"head": "potato_cap", "chest": "potato_tunic", "legs": "potato_pants"},
        "desc": "Full Set: Spud Lord (+30 Max HP, +5 HP/s Regen, Earth Sprout Aura)",
        "atk_mult": 0.10,
        "def_mult": 0.10,
        "bonus_hp": 30,
        "bonus_crit": 5.0,
        "aura": "spud",
    },
    "cactus": {
        "name": "Cactus Needle Set",
        "pieces": {"head": "cactus_helmet", "chest": "cactus_chestplate", "legs": "cactus_greaves"},
        "desc": "Full Set: Thorn Barbs (+15 Reflected Thorns, +10% ATK, Prickly Aura)",
        "atk_mult": 0.10,
        "def_mult": 0.10,
        "bonus_hp": 15,
        "bonus_crit": 4.0,
        "aura": "cactus",
    },
}


class Equipment:
    def __init__(self):
        self.slots = {
            SLOT_HEAD: None,
            SLOT_CHEST: None,
            SLOT_LEGS: None,
            SLOT_WEAPON: None,
            SLOT_ACCESSORY: None,
        }

    def equip(self, item_or_id, stats=None):
        """Equips an item or ItemStack into its designated paperdoll slot."""
        if hasattr(item_or_id, "item_id"):
            item_id = item_or_id.item_id
            store_item = item_or_id
        else:
            item_id = str(item_or_id)
            store_item = item_id

        data = ARMOR_DATA.get(item_id)
        if not data:
            return False, None

        slot_name = data["slot"]
        prev_item = self.slots[slot_name]
        self.slots[slot_name] = store_item

        if stats is not None:
            self.recalculate_stats(stats)
        return True, prev_item

    def unequip(self, slot_name, stats=None):
        """Unequips item from given slot, returning the ItemStack or item_id intact."""
        if slot_name in self.slots and self.slots[slot_name]:
            item = self.slots[slot_name]
            self.slots[slot_name] = None
            if stats is not None:
                self.recalculate_stats(stats)
            return item
        return None

    def has_light_emitter(self):
        """Checks if equipped headpiece emits light (e.g. Miner Helmet) or any gear has radiance effects."""
        head_item = self.slots.get(SLOT_HEAD)
        if head_item:
            head_id = head_item.item_id if hasattr(head_item, "item_id") else head_item
            data = ARMOR_DATA.get(head_id, {})
            if data.get("light", False):
                return True
        for eff in self.get_all_active_effects():
            eff_l = eff.lower()
            if any(k in eff_l for k in ("light radiance", "celestial radiance", "astral sparkles", "supernova")):
                return True
        return False

    def get_all_active_effects(self):
        """Returns a list of all active effect strings from equipped gear and active weapon."""
        effects = []
        from src.ui.inventory import ITEM_REGISTRY
        for slot_name, slot_val in self.slots.items():
            if slot_val:
                item_id = slot_val.item_id if hasattr(slot_val, "item_id") else slot_val
                if hasattr(slot_val, "data"):
                    effects.extend(slot_val.data.get("effects", []))
                else:
                    data = ARMOR_DATA.get(item_id) or ITEM_REGISTRY.get(item_id, {})
                    effects.extend(data.get("effects", []))

        held_obj = getattr(self, "active_weapon_item", None)
        held_id = held_obj.item_id if (held_obj and hasattr(held_obj, "item_id")) else getattr(self, "active_weapon_id", None)
        equipped_weapon = self.slots.get(SLOT_WEAPON)
        eq_id = equipped_weapon.item_id if hasattr(equipped_weapon, "item_id") else equipped_weapon
        if held_id and held_id != eq_id:
            if held_obj and hasattr(held_obj, "data"):
                effects.extend(held_obj.data.get("effects", []))
            else:
                data = ARMOR_DATA.get(held_id) or ITEM_REGISTRY.get(held_id, {})
                effects.extend(data.get("effects", []))
        return effects

    def has_effect(self, effect_keyword):
        """Checks if any currently equipped item or held weapon contains the given effect keyword."""
        kw = effect_keyword.lower()
        for eff in self.get_all_active_effects():
            if kw in eff.lower():
                return True
        return False

    def get_active_set(self):
        """Returns (set_key, set_info) if all head, chest, and legs pieces form an active equipment set."""
        def _get_id(s):
            if not s:
                return None
            return s.item_id if hasattr(s, "item_id") else str(s)

        h = _get_id(self.slots.get(SLOT_HEAD))
        c = _get_id(self.slots.get(SLOT_CHEST))
        l = _get_id(self.slots.get(SLOT_LEGS))
        if not h or not c or not l:
            return None, None

        for set_key, set_data in EQUIPMENT_SETS.items():
            req = set_data["pieces"]
            if h == req["head"] and c == req["chest"] and l == req["legs"]:
                return set_key, set_data

        # Fallback check for any ancient-themed gear
        if "ancient" in h and "ancient" in c and "ancient" in l:
            return "ancient", EQUIPMENT_SETS["ancient"]

        return None, None

    def has_ancient_set(self):
        """Checks if the player has the full Ancient equipment set equipped."""
        set_key, _ = self.get_active_set()
        return set_key == "ancient"

    def get_active_aura(self):
        """Returns aura type string ('ancient', 'titan', 'magma', 'cryo', 'shadow', 'spud', 'cactus') or None."""
        set_key, set_data = self.get_active_set()
        if set_data:
            return set_data.get("aura")
        # Check active effects for radiance aura
        for eff in self.get_all_active_effects():
            eff_l = eff.lower()
            if "ancient" in eff_l:
                return "ancient"
            if "radiant shield" in eff_l or "celestial radiance" in eff_l:
                return "titan"
        return None

    def recalculate_stats(self, stats, active_item_id=_NO_UPDATE, active_item=_NO_UPDATE):
        """Recalculates all player bonus stats based on equipped gear and held weapon."""
        if active_item is not _NO_UPDATE:
            self.active_weapon_item = active_item
            if active_item and hasattr(active_item, "item_id"):
                self.active_weapon_id = active_item.item_id
            elif active_item is None:
                self.active_weapon_id = None
        if active_item_id is not _NO_UPDATE:
            self.active_weapon_id = active_item_id
            if active_item_id is None:
                self.active_weapon_item = None

        bonus_def = 0
        bonus_hp = 0
        bonus_atk = 0
        bonus_crit = 0.0
        bonus_speed = 0.0
        bonus_atk_speed = 0.0
        bonus_mp_regen = 0.0
        atk_mult_total = 0.0

        from src.rpg.enhancement import GOD_TIER_AFFIXES

        for slot_name, slot_val in self.slots.items():
            if slot_val:
                item_id = slot_val.item_id if hasattr(slot_val, "item_id") else slot_val
                if hasattr(slot_val, "data"):
                    data = dict(slot_val.data)
                    affixes = getattr(slot_val, "affixes", [])
                else:
                    data = dict(ARMOR_DATA.get(item_id, {}))
                    affixes = []

                bonus_def += data.get("def", 0)
                bonus_hp += data.get("hp", 0)
                bonus_atk += data.get("atk", data.get("damage", 0) if slot_name == SLOT_WEAPON else 0)
                bonus_crit += data.get("crit", 0.0)
                if slot_name == SLOT_WEAPON:
                    bonus_atk_speed += data.get("speed", data.get("atk_speed", 0.0))
                else:
                    bonus_speed += data.get("speed", 0.0)
                    bonus_atk_speed += data.get("atk_speed", data.get("attack_speed", 0.0))
                bonus_mp_regen += data.get("mp_regen", 0.0)

                for aff in affixes:
                    aff_data = GOD_TIER_AFFIXES.get(aff, {})
                    bonus_atk += aff_data.get("bonus_atk", 0)
                    bonus_def += aff_data.get("bonus_def", 0)
                    bonus_hp += aff_data.get("bonus_hp", 0)
                    bonus_crit += aff_data.get("bonus_crit", 0.0)
                    bonus_speed += aff_data.get("bonus_speed", 0.0)
                    bonus_atk_speed += aff_data.get("bonus_atk_speed", 0.0)
                    atk_mult_total += aff_data.get("atk_mult", 0.0)

        # Apply held weapon stats if selected in hand / hotbar
        held_obj = getattr(self, "active_weapon_item", None)
        held_id = held_obj.item_id if (held_obj and hasattr(held_obj, "item_id")) else getattr(self, "active_weapon_id", None)
        equipped_weapon = self.slots.get(SLOT_WEAPON)
        eq_id = equipped_weapon.item_id if hasattr(equipped_weapon, "item_id") else equipped_weapon

        if held_id and held_id != eq_id:
            if held_obj and hasattr(held_obj, "data"):
                w_data = dict(held_obj.data)
                w_affixes = getattr(held_obj, "affixes", [])
            else:
                w_data = dict(ARMOR_DATA.get(held_id) or {})
                w_affixes = []

            if w_data and w_data.get("slot") == SLOT_WEAPON:
                bonus_def += w_data.get("def", 0)
                bonus_hp += w_data.get("hp", 0)
                bonus_atk += w_data.get("atk", w_data.get("damage", 0))
                bonus_crit += w_data.get("crit", 0.0)
                bonus_atk_speed += w_data.get("speed", w_data.get("atk_speed", 0.0))
                bonus_mp_regen += w_data.get("mp_regen", 0.0)
            else:
                from src.ui.inventory import ITEM_REGISTRY, CAT_WEAPON, CAT_TOOL
                reg = w_data if w_data else ITEM_REGISTRY.get(held_id, {})
                cat = reg.get("cat")
                is_tool = (cat == CAT_TOOL or cat == "tool" or any(w in held_id.lower() for w in ("axe", "pickaxe", "shovel", "drill", "hammer")))
                if cat == CAT_WEAPON or (reg.get("damage", 0) > 0 and not is_tool) or (reg.get("atk", 0) > 0 and not is_tool):
                    bonus_atk += reg.get("damage", reg.get("atk", 0))
                    bonus_crit += reg.get("crit", 0.0)
                    bonus_atk_speed += reg.get("speed", reg.get("atk_speed", 0.0))
                    bonus_def += reg.get("def", 0)
                    bonus_mp_regen += reg.get("mp_regen", 0.0)

            for aff in w_affixes:
                aff_data = GOD_TIER_AFFIXES.get(aff, {})
                bonus_atk += aff_data.get("bonus_atk", 0)
                bonus_def += aff_data.get("bonus_def", 0)
                bonus_hp += aff_data.get("bonus_hp", 0)
                bonus_crit += aff_data.get("bonus_crit", 0.0)
                bonus_speed += aff_data.get("bonus_speed", 0.0)
                bonus_atk_speed += aff_data.get("bonus_atk_speed", 0.0)
                atk_mult_total += aff_data.get("atk_mult", 0.0)

        # Apply Equipment Set Bonuses
        active_set_key, active_set = self.get_active_set()
        if active_set:
            bonus_atk += int((stats.base_atk + bonus_atk) * active_set.get("atk_mult", 0.0))
            bonus_def += int((stats.base_def + bonus_def) * active_set.get("def_mult", 0.0))
            bonus_hp += active_set.get("bonus_hp", 0)
            bonus_crit += active_set.get("bonus_crit", 0.0)
            bonus_speed += active_set.get("bonus_speed", 0.0)
            bonus_mp_regen += active_set.get("bonus_mp_regen", 0.0)

        # Apply Affix Percentage Multipliers (e.g. Titan's Might +25% Damage)
        if atk_mult_total > 0:
            bonus_atk += int((stats.base_atk + bonus_atk) * atk_mult_total)

        # Apply Catalog Passive Gear Effects
        active_effs = self.get_all_active_effects()
        for eff in active_effs:
            eff_l = eff.lower()
            if "spud fortitude" in eff_l:
                bonus_hp += int(stats.base_max_hp * 0.15)
            if "primordial genesis" in eff_l:
                bonus_hp += int(stats.base_max_hp * 0.25)
                bonus_atk += int(stats.base_atk * 0.25)
                bonus_def += int(stats.base_def * 0.25)
            if "vigor overflow" in eff_l or "3.0 mp/s" in eff_l:
                bonus_mp_regen += 3.0
            elif "2.5 mp/s" in eff_l:
                bonus_mp_regen += 2.5
            if "+115% sprint speed" in eff_l and bonus_speed < 1.15:
                bonus_speed += 1.15
            if "attack speed" in eff_l:
                import re
                match = re.search(r'\+(\d+)%\s*attack\s*speed', eff_l)
                if match:
                    bonus_atk_speed += float(match.group(1)) / 100.0
            if "swift strike" in eff_l or "rapid fire" in eff_l:
                bonus_atk_speed += 0.20

        stats.bonus_def = bonus_def
        stats.bonus_max_hp = bonus_hp
        stats.bonus_atk = bonus_atk
        stats.bonus_crit = bonus_crit
        stats.bonus_speed = bonus_speed
        stats.bonus_atk_speed = bonus_atk_speed
        stats.bonus_mp_regen = bonus_mp_regen

