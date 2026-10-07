"""
Potaria Item Generator
Generates over 1200 unique weapons and equipment items across 7 rarity tiers.
Writes to data/weapons.json and data/equipments.json.
Developer: Kurados
"""

import os
import json
import random

# Project Paths
SCRATCH_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(SCRATCH_DIR, "data")
os.makedirs(DATA_DIR, exist_ok=True)

RARITY_COMMON = "common"
RARITY_UNCOMMON = "uncommon"
RARITY_RARE = "rare"
RARITY_EPIC = "epic"
RARITY_MYTHIC = "mythic"
RARITY_LEGENDARY = "legendary"
RARITY_ANCIENT = "ancient"

RARITY_COLORS = {
    RARITY_COMMON: "#9E9E9E",
    RARITY_UNCOMMON: "#4CAF50",
    RARITY_RARE: "#2196F3",
    RARITY_EPIC: "#9C27B0",
    RARITY_MYTHIC: "#FF9800",
    RARITY_LEGENDARY: "#FFD700",
    RARITY_ANCIENT: "#F44336",
}

# Thematic Prefixes & Suffixes for generating vibrant Potaria names
THEMATIC_THEMES = [
    # Spud / Earth
    {"prefix": "Spud", "roots": ["Tuber", "Russet", "Yukon", "Sprout", "Root", "Starch", "Briar", "Bloom", "Furrow", "Earthbound"]},
    # Fire / Magma
    {"prefix": "Magma", "roots": ["Pyre", "Cinder", "Ember", "Inferno", "Volcanic", "Molten", "Smolder", "Ignis", "Blaze", "Flare"]},
    # Ice / Frost
    {"prefix": "Frost", "roots": ["Glacial", "Cryo", "Blizzard", "Hoarfrost", "Permafrost", "Rime", "Chill", "Winter", "Avalanche", "Polar"]},
    # Sand / Desert
    {"prefix": "Dune", "roots": ["Sandstorm", "Arid", "Scorpion", "Oasis", "Mirage", "Sirocco", "Desert", "Dust", "Pharaoh", "Khamsin"]},
    # Dark / Blight
    {"prefix": "Blight", "roots": ["Shadow", "Void", "Umbral", "Dread", "Abyssal", "Nether", "Gloom", "Cursed", "Wither", "Crypt"]},
    # Celestial / Astral
    {"prefix": "Astral", "roots": ["Celestial", "Sol-Rho", "Stellar", "Cosmic", "Nova", "Nebula", "Starlight", "Solar", "Lunar", "Keystone"]},
    # Metal / Craft
    {"prefix": "Forged", "roots": ["Copper", "Iron", "Gold", "Obsidian", "Granite", "Basalt", "Titan", "Runic", "Clockwork", "Tempered"]},
    # Nature / Verdant
    {"prefix": "Verdant", "roots": ["Grove", "Bramble", "Thorn", "Wild", "Flora", "Canopy", "Moss", "Spore", "Petal", "Timber"]},
    # Storm / Sky
    {"prefix": "Zephyr", "roots": ["Tempest", "Gale", "Vortex", "Cyclone", "Thunder", "Lightning", "Breeze", "Storm", "Squall", "Skyward"]},
    # Ancient / Primordial
    {"prefix": "Ancient", "roots": ["Primordial", "Eldritch", "Forgotten", "Eternal", "Genesis", "Timeless", "Chrono", "Relic", "Ancestral", "Mythic"]},
]

WEAPON_NOUNS = [
    "Blade", "Sword", "Broadsword", "Greatsword", "Claymore", "Cleaver", "Scythe",
    "Dagger", "Rapier", "Cutlass", "Saber", "Spear", "Lance", "Halberd", "Pike",
    "Bow", "Longbow", "Recurve", "Crossbow", "Shortbow", "Staff", "Scepter",
    "Wand", "Rod", "Focus", "Grimoire", "Catalyst", "Warhammer", "Mace", "Glaive"
]

HEAD_NOUNS = [
    "Helmet", "Helm", "Visor", "Crown", "Diadem", "Circlet", "Hood", "Cowl",
    "Cap", "Mask", "Greathelm", "Bascinet", "Sallet", "Coif", "Headguard"
]

CHEST_NOUNS = [
    "Chestplate", "Cuirass", "Breastplate", "Plate", "Tunic", "Parka", "Carapace",
    "Robe", "Vestment", "Mail", "Hauberk", "Jerkin", "Harness", "Overcoat", "Aegis"
]

LEGS_NOUNS = [
    "Greaves", "Striders", "Boots", "Treads", "Sabatons", "Leggings", "Pants",
    "Runners", "Walkers", "Gaiters", "Greave-Guards", "Spurs", "Pathfinders", "Tracers"
]

ACCESSORY_NOUNS = [
    "Ring", "Amulet", "Talisman", "Charm", "Emblem", "Pendant", "Signet", "Relic",
    "Choker", "Brooch", "Locket", "Medallion", "Insignia", "Seal", "Band", "Orchid", "Token"
]

LORE_POOLS = [
    "'Forged in cosmic crucibles when falling meteors first pierced the heavens.'",
    "'Swift as the desert gale, unburdened by mortal weight or worldly sorrow.'",
    "'Before the continents divided and the stars cooled, the primordial seed was planted in the void.'",
    "'The ancestral blade of King Spudicus, savior of the tuber kin.'",
    "'Carried by Grand Boss Sol-Rho before the heavens surrendered to radiant destiny.'",
    "'Harvested beneath the scorching sun of the Arid Waste by ancient tomb wardens.'",
    "'Pulsing with eternal starlight drawn from the highest reaches of the cosmos.'",
    "'Cold enough to freeze the blood of subterranean beasts in their tracks.'",
    "'The earth groans under its weight, yet in rightful hands it moves like a feather.'",
    "'Whispering the forgotten songs of ancient roots that drank from deep subterranean rivers.'",
    "'Infused with pure volcanic heartstone, blazing with an undying subterranean fire.'",
    "'A relic from the First Age of Potaria, when giants roamed the boundless valleys.'",
    "'Imbued with the soul of an ancient guardian who stood watch at the Nether Gate.'",
    "'Peer too long into its gleaming edge, and the boundless void peers back into you.'",
    "'Woven from filaments of morning starlight and unbreakable potato fiber.'",
    "'The echoes of forgotten battles resonate within every inch of this masterwork.'",
    "'Passed down through nine dynasties of tuber elders as a sacred ward against ruin.'",
    "'Dredged from molten caverns where liquid rock flows with the fury of creation.'",
    "'A silent testament to those who dared challenge the infinite heavens and won.'",
    "'The breath of a hundred storms coalesced into a single unyielding artifact.'",
    "'Etched with runic glyphs that pulse in harmony with the heartbeat of Potaria.'",
    "'Drink deep of the celestial dew and fear no shadow in this world or the next.'",
    "'Blessed by the high priestesses of the Verdant Sprout during the Grand Equinox.'",
    "'Neither rust nor time can dull what was quenched in the tears of fallen stars.'",
    "'He who wields this relic carries the unwritten destiny of all tuber kind.'",
]

EFFECT_TEMPLATES = [
    # Offensive
    "Summons Celestial Star on swing",
    "AoE 72px Starburst Explosion",
    "Molten Blaze (+12 Fire Damage)",
    "Glacial Chill (-35% Target Speed)",
    "Armor Penetration (+15 True Damage)",
    "Critical Overdrive (+20% Crit Multiplier)",
    "Solar Flare Shockwave",
    "Dark Cleave (Strikes up to 3 adjacent foes)",
    "Soul Harvest (Restores 5 HP on kill)",
    "Starlight Volley (Fires 2 bonus astral arrows)",
    "Gravitational Pulse (Pulls enemies toward blast)",
    "Superheated Impact (Inflicts Burn for 4s)",
    "Freezing Needles (Pierces through enemies)",
    "Lacerating Strike (Causes Bleed over 5s)",
    "Thunderclap Burst (Stuns targets for 0.5s)",
    # Defensive / Utility
    "+115% Sprint Speed",
    "Air Cushion Fall Resistance",
    "+25% Total Damage Mitigation",
    "Radiant Shield (Absorbs 40 damage every 15s)",
    "Spud Fortitude (+15% Max HP)",
    "Astral Sparkles • True Spud Radiance",
    "Life Surge (Accelerates health regeneration by +2 HP/s)",
    "Arcane Conduit (-20% Skill MP Cost)",
    "Evasion Step (15% Chance to evade incoming strikes)",
    "Magnetic Aura (+100px Item Pickup Radius)",
    "Light Radiance (Illuminates dark caves)",
    "Starch Barrier (Blocks fatal damage once every 90s)",
    "Temporal Shift (Reduces ability cooldowns by 15%)",
    "Deep Roots (Immunity to knockback while grounded)",
    "Vigor Overflow (+3.0 MP/s Mana Regeneration)",
    "Titan's Resolve (Triples defense when below 30% HP)",
    "Celestial Aegis (Deflects enemy projectiles)",
    "Primordial Genesis (Build-defining: All stats +25%)",
    "Eternal Bloom (Full heal upon reaching 1 HP, 180s cd)"
]

def make_effects(rarity, cat):
    if rarity in (RARITY_COMMON, RARITY_UNCOMMON, RARITY_RARE):
        return []
    elif rarity == RARITY_EPIC:
        return random.sample(EFFECT_TEMPLATES, 1)
    elif rarity == RARITY_MYTHIC:
        return random.sample(EFFECT_TEMPLATES, 2)
    elif rarity == RARITY_LEGENDARY:
        return random.sample(EFFECT_TEMPLATES, random.randint(2, 3))
    elif rarity == RARITY_ANCIENT:
        effs = random.sample(EFFECT_TEMPLATES, random.randint(3, 4))
        # Add build-defining tag if not already there
        if not any("Build-defining" in e or "Genesis" in e or "Eternal" in e for e in effs):
            effs[0] = "Ancient Awakening: " + effs[0] + " • Build-Defining Synergy"
        return effs
    return []

def make_lore(rarity):
    if rarity in (RARITY_LEGENDARY, RARITY_ANCIENT):
        return random.choice(LORE_POOLS)
    return ""

def generate_weapons(count=600):
    weapons = []
    seen_ids = set()
    seen_names = set()

    # Canonical scrubbed items first!
    canonical_weapons = [
        {
            "id": "astral_wrath",
            "name": "Astral Wrath",
            "cat": "weapon",
            "rarity": RARITY_LEGENDARY,
            "color": RARITY_COLORS[RARITY_LEGENDARY],
            "atk": 42,
            "def": 2,
            "crit": 14.0,
            "speed": 0.25,
            "hp": 25,
            "mp": 35,
            "mp_regen": 1.5,
            "effects": [
                "Summons Celestial Star on swing",
                "AoE 72px Starburst Explosion",
                "Celestial Radiance"
            ],
            "lore": "'Forged in cosmic crucibles when falling meteors first pierced the heavens.'"
        },
        {
            "id": "celestial_greatsword",
            "name": "Celestial Titan Greatsword",
            "cat": "weapon",
            "rarity": RARITY_MYTHIC,
            "color": RARITY_COLORS[RARITY_MYTHIC],
            "atk": 62,
            "def": 8,
            "crit": 20.0,
            "speed": 0.35,
            "hp": 55,
            "mp": 60,
            "mp_regen": 2.0,
            "effects": [
                "Solar Supernova • Mythic Astral Radiance",
                "Armor Penetration (+15 True Damage)"
            ],
            "lore": "'Carried by Grand Boss Sol-Rho before the heavens surrendered.'"
        },
        {
            "id": "starch_blade",
            "name": "Legendary Starch Blade",
            "cat": "weapon",
            "rarity": RARITY_LEGENDARY,
            "color": RARITY_COLORS[RARITY_LEGENDARY],
            "atk": 36,
            "def": 4,
            "crit": 12.0,
            "speed": 0.20,
            "hp": 30,
            "mp": 40,
            "mp_regen": 1.8,
            "effects": [
                "Astral Sparkles • True Spud Radiance",
                "Life Surge (Accelerates health regeneration by +2 HP/s)"
            ],
            "lore": "'The ancestral blade of King Spudicus, savior of the tuber kin.'"
        },
        {
            "id": "void_edge",
            "name": "Void Edge",
            "cat": "weapon",
            "rarity": RARITY_LEGENDARY,
            "color": RARITY_COLORS[RARITY_LEGENDARY],
            "atk": 52,
            "def": 4,
            "crit": 16.0,
            "speed": 0.30,
            "hp": 35,
            "mp": 50,
            "mp_regen": 2.2,
            "effects": [
                "Armor Penetration (+15 True Damage)",
                "Gravitational Pulse (Pulls enemies toward blast)"
            ],
            "lore": "'Peer too long into this blade, and it peers into you.'"
        },
        {
            "id": "magma_greatsword",
            "name": "Magma Greatsword",
            "cat": "weapon",
            "rarity": RARITY_EPIC,
            "color": RARITY_COLORS[RARITY_EPIC],
            "atk": 38,
            "def": 2,
            "crit": 10.0,
            "speed": 0.15,
            "hp": 25,
            "mp": 20,
            "mp_regen": 1.0,
            "effects": [
                "Molten Blaze (+12 Fire Damage)"
            ],
            "lore": ""
        },
        {
            "id": "bone_scythe",
            "name": "Bone Scythe",
            "cat": "weapon",
            "rarity": RARITY_EPIC,
            "color": RARITY_COLORS[RARITY_EPIC],
            "atk": 35,
            "def": 0,
            "crit": 14.0,
            "speed": 0.20,
            "hp": 15,
            "mp": 25,
            "mp_regen": 1.2,
            "effects": [
                "Soul Harvest (Restores 5 HP on kill)"
            ],
            "lore": ""
        },
        {
            "id": "genesis_world_cleaver",
            "name": "Genesis World Cleaver",
            "cat": "weapon",
            "rarity": RARITY_ANCIENT,
            "color": RARITY_COLORS[RARITY_ANCIENT],
            "atk": 115,
            "def": 18,
            "crit": 32.0,
            "speed": 0.50,
            "hp": 120,
            "mp": 150,
            "mp_regen": 5.5,
            "effects": [
                "Primordial Genesis (Build-defining: All stats +25%)",
                "AoE 72px Starburst Explosion",
                "Armor Penetration (+15 True Damage)",
                "Starch Barrier (Blocks fatal damage once every 90s)"
            ],
            "lore": "'Before the continents divided and the stars cooled, the primordial seed was planted in the void.'"
        }
    ]

    for cw in canonical_weapons:
        weapons.append(cw)
        seen_ids.add(cw["id"])
        seen_names.add(cw["name"])

    # Distribution of rarities
    rarities = [
        (RARITY_COMMON, 120),
        (RARITY_UNCOMMON, 120),
        (RARITY_RARE, 110),
        (RARITY_EPIC, 100),
        (RARITY_MYTHIC, 80),
        (RARITY_LEGENDARY, 50),
        (RARITY_ANCIENT, 25),
    ]

    rng = random.Random(1337)

    for rarity, target_num in rarities:
        current_in_rarity = sum(1 for w in weapons if w["rarity"] == rarity)
        needed = target_num - current_in_rarity
        for _ in range(needed):
            # Generate unique name
            theme = rng.choice(THEMATIC_THEMES)
            root = rng.choice(theme["roots"])
            noun = rng.choice(WEAPON_NOUNS)
            
            # Form name
            prefix_style = rng.choice(["RootNoun", "ThemeRootNoun", "AncientTitle", "OfSuffix"])
            if prefix_style == "RootNoun":
                name = f"{root} {noun}"
            elif prefix_style == "ThemeRootNoun":
                name = f"{theme['prefix']} {root} {noun}"
            elif prefix_style == "AncientTitle":
                adj = rng.choice(["Grand", "Elder", "High", "Prime", "Luminous", "Dread", "Royal", "Sacred"])
                name = f"{adj} {root} {noun}"
            else:
                suffix = rng.choice(["of the Spud", "of Sol-Rho", "of the Blight", "of the Caverns", "of the Vale", "of the Eclipse", "of Genesis", "of the Tempest"])
                name = f"{root} {noun} {suffix}"

            # Ensure uniqueness
            attempt = 1
            base_name = name
            while name in seen_names:
                attempt += 1
                name = f"{base_name} {attempt}"
            seen_names.add(name)

            # Generate item ID
            item_id = name.lower().replace(" ", "_").replace("'", "").replace("-", "_").replace(".", "")
            if item_id in seen_ids:
                item_id = f"{item_id}_{len(weapons)}"
            seen_ids.add(item_id)

            # Generate stats according to rarity
            if rarity == RARITY_COMMON:
                atk = rng.randint(8, 16)
                defense = 0
                crit = round(rng.uniform(1.0, 3.5), 1)
                speed = 0.0
                hp = rng.randint(0, 5)
                mp = rng.randint(0, 10)
                mp_regen = 0.0
            elif rarity == RARITY_UNCOMMON:
                atk = rng.randint(17, 26)
                defense = rng.randint(0, 2)
                crit = round(rng.uniform(3.0, 6.0), 1)
                speed = round(rng.uniform(0.0, 0.1), 2)
                hp = rng.randint(5, 15)
                mp = rng.randint(10, 20)
                mp_regen = round(rng.uniform(0.1, 0.4), 1)
            elif rarity == RARITY_RARE:
                atk = rng.randint(27, 38)
                defense = rng.randint(1, 4)
                crit = round(rng.uniform(6.0, 10.0), 1)
                speed = round(rng.uniform(0.1, 0.2), 2)
                hp = rng.randint(15, 30)
                mp = rng.randint(20, 35)
                mp_regen = round(rng.uniform(0.5, 1.0), 1)
            elif rarity == RARITY_EPIC:
                atk = rng.randint(39, 52)
                defense = rng.randint(3, 7)
                crit = round(rng.uniform(10.0, 15.0), 1)
                speed = round(rng.uniform(0.15, 0.28), 2)
                hp = rng.randint(25, 45)
                mp = rng.randint(30, 50)
                mp_regen = round(rng.uniform(1.0, 1.8), 1)
            elif rarity == RARITY_MYTHIC:
                atk = rng.randint(53, 72)
                defense = rng.randint(6, 12)
                crit = round(rng.uniform(15.0, 22.0), 1)
                speed = round(rng.uniform(0.25, 0.38), 2)
                hp = rng.randint(40, 70)
                mp = rng.randint(50, 80)
                mp_regen = round(rng.uniform(1.8, 2.8), 1)
            elif rarity == RARITY_LEGENDARY:
                atk = rng.randint(73, 96)
                defense = rng.randint(9, 16)
                crit = round(rng.uniform(20.0, 28.0), 1)
                speed = round(rng.uniform(0.35, 0.48), 2)
                hp = rng.randint(60, 100)
                mp = rng.randint(75, 120)
                mp_regen = round(rng.uniform(2.8, 4.2), 1)
            elif rarity == RARITY_ANCIENT:
                atk = rng.randint(98, 140)
                defense = rng.randint(16, 25)
                crit = round(rng.uniform(28.0, 38.0), 1)
                speed = round(rng.uniform(0.45, 0.65), 2)
                hp = rng.randint(90, 150)
                mp = rng.randint(110, 180)
                mp_regen = round(rng.uniform(4.5, 6.5), 1)

            entry = {
                "id": item_id,
                "name": name,
                "cat": "weapon",
                "rarity": rarity,
                "color": RARITY_COLORS[rarity],
                "atk": atk,
                "def": defense,
                "crit": crit,
                "speed": speed,
                "hp": hp,
                "mp": mp,
                "mp_regen": mp_regen,
                "effects": make_effects(rarity, "weapon"),
                "lore": make_lore(rarity),
            }
            weapons.append(entry)

    return weapons

def generate_equipments(count=600):
    equipments = []
    seen_ids = set()
    seen_names = set()

    # Canonical scrubbed items first!
    canonical_equipments = [
        {
            "id": "zephyr_striders",
            "name": "Zephyr Striders",
            "cat": "legs",
            "rarity": RARITY_EPIC,
            "color": RARITY_COLORS[RARITY_EPIC],
            "atk": 2,
            "def": 8,
            "crit": 4.0,
            "speed": 1.15,
            "hp": 25,
            "mp": 10,
            "mp_regen": 0.5,
            "effects": [
                "+115% Sprint Speed",
                "Air Cushion Fall Resistance"
            ],
            "lore": ""
        },
        {
            "id": "talisman_of_vigor",
            "name": "Talisman of Vigor",
            "cat": "accessory",
            "rarity": RARITY_EPIC,
            "color": RARITY_COLORS[RARITY_EPIC],
            "atk": 3,
            "def": 6,
            "crit": 3.0,
            "speed": 0.05,
            "hp": 45,
            "mp": 20,
            "mp_regen": 1.2,
            "effects": [
                "Life Surge (Accelerates health regeneration by +2 HP/s)",
                "Vigor Overflow (+3.0 MP/s Mana Regeneration)"
            ],
            "lore": ""
        },
        {
            "id": "arcane_orchid",
            "name": "Arcane Orchid",
            "cat": "accessory",
            "rarity": RARITY_EPIC,
            "color": RARITY_COLORS[RARITY_EPIC],
            "atk": 8,
            "def": 4,
            "crit": 6.0,
            "speed": 0.0,
            "hp": 30,
            "mp": 50,
            "mp_regen": 2.5,
            "effects": [
                "Arcane Conduit (-20% Skill MP Cost)",
                "+2.5 MP/s Mana Regen"
            ],
            "lore": ""
        },
        {
            "id": "crown_of_potaria",
            "name": "Crown of Potaria",
            "cat": "head",
            "rarity": RARITY_LEGENDARY,
            "color": RARITY_COLORS[RARITY_LEGENDARY],
            "atk": 14,
            "def": 26,
            "crit": 10.0,
            "speed": 0.40,
            "hp": 75,
            "mp": 80,
            "mp_regen": 2.5,
            "effects": [
                "Astral Sparkles • True Spud Radiance",
                "Radiant Shield (Absorbs 40 damage every 15s)"
            ],
            "lore": "'Passed down through nine dynasties of tuber elders as a sacred ward against ruin.'"
        },
        {
            "id": "titan_chestplate",
            "name": "Celestial Titan Plate",
            "cat": "chest",
            "rarity": RARITY_LEGENDARY,
            "color": RARITY_COLORS[RARITY_LEGENDARY],
            "atk": 20,
            "def": 36,
            "crit": 9.0,
            "speed": 0.35,
            "hp": 120,
            "mp": 60,
            "mp_regen": 1.8,
            "effects": [
                "+25% Total Damage Mitigation",
                "Deep Roots (Immunity to knockback while grounded)"
            ],
            "lore": "'Carried by Grand Boss Sol-Rho before the heavens surrendered to radiant destiny.'"
        },
        {
            "id": "chronos_prime_heart",
            "name": "Chronos Primordial Heart",
            "cat": "accessory",
            "rarity": RARITY_ANCIENT,
            "color": RARITY_COLORS[RARITY_ANCIENT],
            "atk": 38,
            "def": 38,
            "crit": 28.0,
            "speed": 0.70,
            "hp": 200,
            "mp": 180,
            "mp_regen": 6.0,
            "effects": [
                "Primordial Genesis (Build-defining: All stats +25%)",
                "Eternal Bloom (Full heal upon reaching 1 HP, 180s cd)",
                "Temporal Shift (Reduces ability cooldowns by 15%)"
            ],
            "lore": "'Before the continents divided and the stars cooled, the primordial seed was planted in the void.'"
        }
    ]

    for ce in canonical_equipments:
        equipments.append(ce)
        seen_ids.add(ce["id"])
        seen_names.add(ce["name"])

    # 4 categories: head, chest, legs, accessory
    cats = ["head", "chest", "legs", "accessory"]
    # 150 of each category = 600 total!
    rng = random.Random(4242)

    cat_nouns = {
        "head": HEAD_NOUNS,
        "chest": CHEST_NOUNS,
        "legs": LEGS_NOUNS,
        "accessory": ACCESSORY_NOUNS,
    }

    rarities_per_cat = [
        (RARITY_COMMON, 30),
        (RARITY_UNCOMMON, 30),
        (RARITY_RARE, 28),
        (RARITY_EPIC, 25),
        (RARITY_MYTHIC, 20),
        (RARITY_LEGENDARY, 12),
        (RARITY_ANCIENT, 6),
    ] # sums to 151 per cat

    for c in cats:
        for rarity, target_num in rarities_per_cat:
            current_in_cat_rarity = sum(1 for e in equipments if e["cat"] == c and e["rarity"] == rarity)
            needed = target_num - current_in_cat_rarity
            for _ in range(needed):
                theme = rng.choice(THEMATIC_THEMES)
                root = rng.choice(theme["roots"])
                noun = rng.choice(cat_nouns[c])

                prefix_style = rng.choice(["RootNoun", "ThemeRootNoun", "AncientTitle", "OfSuffix"])
                if prefix_style == "RootNoun":
                    name = f"{root} {noun}"
                elif prefix_style == "ThemeRootNoun":
                    name = f"{theme['prefix']} {root} {noun}"
                elif prefix_style == "AncientTitle":
                    adj = rng.choice(["Grand", "Elder", "High", "Prime", "Luminous", "Dread", "Royal", "Sacred", "Warded", "Gilded"])
                    name = f"{adj} {root} {noun}"
                else:
                    suffix = rng.choice(["of Fortitude", "of Sol-Rho", "of the Blight", "of the Caverns", "of the Spud", "of the Eclipse", "of Genesis", "of the Zephyr"])
                    name = f"{root} {noun} {suffix}"

                attempt = 1
                base_name = name
                while name in seen_names:
                    attempt += 1
                    name = f"{base_name} {attempt}"
                seen_names.add(name)

                item_id = name.lower().replace(" ", "_").replace("'", "").replace("-", "_").replace(".", "")
                if item_id in seen_ids:
                    item_id = f"{item_id}_{len(equipments)}"
                seen_ids.add(item_id)

                # Stats customized by slot and rarity
                if rarity == RARITY_COMMON:
                    if c == "head":
                        atk = rng.randint(0, 1); defense = rng.randint(1, 3); crit = 0.0; speed = 0.0; hp = rng.randint(5, 12); mp = 0; mp_regen = 0.0
                    elif c == "chest":
                        atk = rng.randint(0, 1); defense = rng.randint(2, 5); crit = 0.0; speed = 0.0; hp = rng.randint(10, 20); mp = 0; mp_regen = 0.0
                    elif c == "legs":
                        atk = 0; defense = rng.randint(1, 3); crit = 0.0; speed = round(rng.uniform(0.05, 0.15), 2); hp = rng.randint(5, 12); mp = 0; mp_regen = 0.0
                    else: # accessory
                        atk = rng.randint(1, 3); defense = rng.randint(1, 3); crit = 1.0; speed = 0.05; hp = rng.randint(10, 20); mp = rng.randint(5, 15); mp_regen = 0.2
                elif rarity == RARITY_UNCOMMON:
                    if c == "head":
                        atk = rng.randint(1, 3); defense = rng.randint(4, 7); crit = 1.0; speed = 0.0; hp = rng.randint(15, 25); mp = 10; mp_regen = 0.2
                    elif c == "chest":
                        atk = rng.randint(1, 3); defense = rng.randint(6, 11); crit = 1.0; speed = 0.0; hp = rng.randint(25, 40); mp = 15; mp_regen = 0.2
                    elif c == "legs":
                        atk = rng.randint(0, 2); defense = rng.randint(4, 7); crit = 1.0; speed = round(rng.uniform(0.15, 0.25), 2); hp = rng.randint(15, 25); mp = 10; mp_regen = 0.2
                    else:
                        atk = rng.randint(3, 6); defense = rng.randint(3, 6); crit = round(rng.uniform(2.0, 4.0), 1); speed = 0.10; hp = rng.randint(20, 35); mp = rng.randint(15, 25); mp_regen = 0.4
                elif rarity == RARITY_RARE:
                    if c == "head":
                        atk = rng.randint(2, 5); defense = rng.randint(8, 13); crit = round(rng.uniform(2.0, 4.0), 1); speed = 0.05; hp = rng.randint(30, 45); mp = 20; mp_regen = 0.6
                    elif c == "chest":
                        atk = rng.randint(3, 6); defense = rng.randint(12, 18); crit = round(rng.uniform(2.0, 4.0), 1); speed = 0.05; hp = rng.randint(45, 65); mp = 25; mp_regen = 0.6
                    elif c == "legs":
                        atk = rng.randint(1, 4); defense = rng.randint(8, 13); crit = round(rng.uniform(2.0, 4.0), 1); speed = round(rng.uniform(0.25, 0.45), 2); hp = rng.randint(30, 45); mp = 20; mp_regen = 0.6
                    else:
                        atk = rng.randint(6, 10); defense = rng.randint(6, 10); crit = round(rng.uniform(4.0, 7.0), 1); speed = 0.15; hp = rng.randint(35, 55); mp = rng.randint(25, 45); mp_regen = 0.9
                elif rarity == RARITY_EPIC:
                    if c == "head":
                        atk = rng.randint(4, 8); defense = rng.randint(14, 20); crit = round(rng.uniform(4.0, 7.0), 1); speed = 0.10; hp = rng.randint(50, 70); mp = 35; mp_regen = 1.0
                    elif c == "chest":
                        atk = rng.randint(6, 11); defense = rng.randint(19, 27); crit = round(rng.uniform(4.0, 7.0), 1); speed = 0.10; hp = rng.randint(70, 95); mp = 45; mp_regen = 1.0
                    elif c == "legs":
                        atk = rng.randint(3, 7); defense = rng.randint(14, 20); crit = round(rng.uniform(4.0, 7.0), 1); speed = round(rng.uniform(0.45, 0.75), 2); hp = rng.randint(50, 70); mp = 35; mp_regen = 1.0
                    else:
                        atk = rng.randint(10, 16); defense = rng.randint(10, 16); crit = round(rng.uniform(7.0, 12.0), 1); speed = 0.25; hp = rng.randint(55, 80); mp = rng.randint(40, 65); mp_regen = 1.6
                elif rarity == RARITY_MYTHIC:
                    if c == "head":
                        atk = rng.randint(8, 13); defense = rng.randint(21, 28); crit = round(rng.uniform(7.0, 10.0), 1); speed = 0.20; hp = rng.randint(75, 105); mp = 55; mp_regen = 1.8
                    elif c == "chest":
                        atk = rng.randint(11, 17); defense = rng.randint(28, 38); crit = round(rng.uniform(7.0, 10.0), 1); speed = 0.20; hp = rng.randint(105, 145); mp = 70; mp_regen = 1.8
                    elif c == "legs":
                        atk = rng.randint(6, 12); defense = rng.randint(21, 28); crit = round(rng.uniform(7.0, 10.0), 1); speed = round(rng.uniform(0.75, 1.10), 2); hp = rng.randint(75, 105); mp = 55; mp_regen = 1.8
                    else:
                        atk = rng.randint(16, 24); defense = rng.randint(16, 24); crit = round(rng.uniform(12.0, 18.0), 1); speed = 0.35; hp = rng.randint(80, 120); mp = rng.randint(65, 100); mp_regen = 2.8
                elif rarity == RARITY_LEGENDARY:
                    if c == "head":
                        atk = rng.randint(13, 19); defense = rng.randint(29, 38); crit = round(rng.uniform(10.0, 14.0), 1); speed = 0.30; hp = rng.randint(110, 150); mp = 85; mp_regen = 2.6
                    elif c == "chest":
                        atk = rng.randint(17, 25); defense = rng.randint(39, 50); crit = round(rng.uniform(10.0, 14.0), 1); speed = 0.30; hp = rng.randint(150, 205); mp = 110; mp_regen = 2.6
                    elif c == "legs":
                        atk = rng.randint(10, 18); defense = rng.randint(29, 38); crit = round(rng.uniform(10.0, 14.0), 1); speed = round(rng.uniform(1.10, 1.45), 2); hp = rng.randint(110, 150); mp = 85; mp_regen = 2.6
                    else:
                        atk = rng.randint(24, 34); defense = rng.randint(24, 34); crit = round(rng.uniform(18.0, 25.0), 1); speed = 0.50; hp = rng.randint(120, 170); mp = rng.randint(100, 145); mp_regen = 4.0
                elif rarity == RARITY_ANCIENT:
                    if c == "head":
                        atk = rng.randint(19, 27); defense = rng.randint(39, 52); crit = round(rng.uniform(14.0, 20.0), 1); speed = 0.40; hp = rng.randint(155, 215); mp = 125; mp_regen = 3.8
                    elif c == "chest":
                        atk = rng.randint(25, 36); defense = rng.randint(51, 70); crit = round(rng.uniform(14.0, 20.0), 1); speed = 0.40; hp = rng.randint(210, 295); mp = 160; mp_regen = 3.8
                    elif c == "legs":
                        atk = rng.randint(15, 26); defense = rng.randint(39, 52); crit = round(rng.uniform(14.0, 20.0), 1); speed = round(rng.uniform(1.45, 1.95), 2); hp = rng.randint(155, 215); mp = 125; mp_regen = 3.8
                    else:
                        atk = rng.randint(35, 50); defense = rng.randint(35, 50); crit = round(rng.uniform(25.0, 35.0), 1); speed = 0.75; hp = rng.randint(170, 250); mp = rng.randint(145, 210); mp_regen = 5.5

                entry = {
                    "id": item_id,
                    "name": name,
                    "cat": c,
                    "rarity": rarity,
                    "color": RARITY_COLORS[rarity],
                    "atk": atk,
                    "def": defense,
                    "crit": crit,
                    "speed": speed,
                    "hp": hp,
                    "mp": mp,
                    "mp_regen": mp_regen,
                    "effects": make_effects(rarity, c),
                    "lore": make_lore(rarity),
                }
                equipments.append(entry)

    return equipments

def main():
    print("Generating Potaria weapons.json and equipments.json...")
    weapons = generate_weapons(600)
    equipments = generate_equipments(600)

    weapons_path = os.path.join(DATA_DIR, "weapons.json")
    with open(weapons_path, "w", encoding="utf-8") as f:
        json.dump(weapons, f, indent=2)

    equipments_path = os.path.join(DATA_DIR, "equipments.json")
    with open(equipments_path, "w", encoding="utf-8") as f:
        json.dump(equipments, f, indent=2)

    print(f"Successfully generated {len(weapons)} weapons in {weapons_path}")
    print(f"Successfully generated {len(equipments)} equipments in {equipments_path}")
    print(f"Total unique items generated: {len(weapons) + len(equipments)}")

if __name__ == "__main__":
    main()
