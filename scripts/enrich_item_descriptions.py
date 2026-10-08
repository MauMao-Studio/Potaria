"""
Potaria - Item Descriptions Enrichment Script
Ensures every weapon in data/weapons.json and equipment in data/equipments.json
has a flavor-rich, informative, non-empty description.
Developer: Kurados
"""

import os
import json

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
WEAPONS_FILE = os.path.join(DATA_DIR, "weapons.json")
EQUIPMENTS_FILE = os.path.join(DATA_DIR, "equipments.json")

CANONICAL_WEAPON_DESCS = {
    "wooden_sword": "A basic wooden sword carved from raw timber. Ideal for fending off early surface beasts.",
    "astral_wrath": "Legendary sword that summons falling celestial stars from the sky upon swinging.",
    "celestial_greatsword": "Godly greatsword carried by Grand Boss Sol-Rho. Blazes with solar flare supernovas.",
    "starch_blade": "Ancestral blade of King Spudicus. Infused with living potato vitality and radiant sparkles.",
    "void_edge": "A blade of pure darkness that cleaves through matter and gravity effortlessly.",
    "magma_greatsword": "A colossal greatsword quenched in subterranean magma. Engulfs targets in blazing fire.",
    "bone_scythe": "A wicked scythe carved from ancient subterranean horrors. Reaps the souls of the fallen.",
    "genesis_world_cleaver": "The primordial cleaver forged at the dawn of time. Rips open reality with cosmic shockwaves.",
}

CANONICAL_EQUIPMENT_DESCS = {
    "zephyr_striders": "Enchanted running boots imbued with the swiftness of the desert wind. Grants massive sprint acceleration.",
    "talisman_of_vigor": "Blessed ancient talisman that steadily regenerates health and restores mana.",
    "arcane_orchid": "A rare crystalline blossom that focuses arcane flows, lowering spell MP costs and accelerating mana regen.",
    "crown_of_potaria": "The golden crown of the potato monarch. Shields the wearer with an impenetrable radiant barrier.",
    "titan_chestplate": "Indomitable plate mail worn by celestial titans. Mitigates damage and grants immunity to knockback.",
    "chronos_prime_heart": "An ancient primordial relic that pulses in rhythm with time itself. Enhances all vital attributes.",
}

def generate_weapon_desc(w):
    item_id = w["id"]
    if item_id in CANONICAL_WEAPON_DESCS:
        return CANONICAL_WEAPON_DESCS[item_id]

    name = w.get("name", item_id)
    rarity = w.get("rarity", "common").title()
    name_l = name.lower()
    effects = w.get("effects", [])

    # Classify archetype
    if any(k in name_l for k in ("bow", "longbow", "recurve", "crossbow", "shortbow")):
        archetype = "bow"
        flavor = f"An agile {rarity} bow crafted for high-velocity volleys. Pierces monstrous targets from safe range."
    elif any(k in name_l for k in ("staff", "wand", "scepter", "rod", "focus", "catalyst")):
        archetype = "staff"
        flavor = f"A mystical {rarity} staff channeling elemental currents. Unleashes searing magical projectiles."
    elif any(k in name_l for k in ("grimoire", "tome")):
        archetype = "tome"
        flavor = f"An arcane {rarity} grimoire inscribed with forgotten runes. Unleashes raw spell power against foes."
    elif any(k in name_l for k in ("dagger", "rapier", "shortsword", "cutlass", "saber")):
        archetype = "dagger"
        flavor = f"A swift {rarity} blade with flawless balance. Strikes with rapid precision in close-quarters combat."
    elif any(k in name_l for k in ("greatsword", "claymore", "cleaver", "scythe", "warhammer", "mace")):
        archetype = "heavy"
        flavor = f"A heavy {rarity} weapon with immense striking weight. Cleaves through enemy defenses with crushing momentum."
    elif any(k in name_l for k in ("spear", "lance", "halberd", "pike", "glaive")):
        archetype = "spear"
        flavor = f"An extended {rarity} polearm forged for tactical reach. Impales adversaries before they can close distance."
    else:
        archetype = "sword"
        flavor = f"A formidable {rarity} blade tempered for heroic combat. Forged in Potaria to conquer the subterranean depths."

    # Incorporate thematic flavor
    if any(k in name_l for k in ("astral", "celestial", "stellar", "sol-rho", "nova", "star")):
        flavor += " Shimmers with cosmic stardust."
    elif any(k in name_l for k in ("magma", "pyre", "cinder", "inferno", "ignis", "blaze", "flame")):
        flavor += " Radiates blistering subterranean heat."
    elif any(k in name_l for k in ("frost", "glacial", "cryo", "chill", "ice", "winter")):
        flavor += " Emits biting permafrost cold."
    elif any(k in name_l for k in ("blight", "void", "shadow", "dread", "abyssal")):
        flavor += " Pulses with eerie dark energies."
    elif any(k in name_l for k in ("dune", "sand", "arid", "desert")):
        flavor += " Tempered in unforgiving desert sands."
    elif any(k in name_l for k in ("spud", "tuber", "russet", "starch")):
        flavor += " Infused with the earthy resilience of Potaria."
    elif any(k in name_l for k in ("ancient", "primordial", "genesis", "eternal")):
        flavor += " Echoes with primordial power from the First Age."

    if effects and len(effects) > 0:
        eff_clean = effects[0].split("(")[0].strip()
        flavor += f" Bestows {eff_clean}."

    return flavor


def generate_equipment_desc(eq):
    item_id = eq["id"]
    if item_id in CANONICAL_EQUIPMENT_DESCS:
        return CANONICAL_EQUIPMENT_DESCS[item_id]

    name = eq.get("name", item_id)
    rarity = eq.get("rarity", "common").title()
    cat = eq.get("cat", "accessory")
    name_l = name.lower()
    effects = eq.get("effects", [])

    if cat == "head":
        flavor = f"A protective {rarity} headpiece reinforcing defense. Shields Spud from overhead attacks and sharp debris."
    elif cat == "chest":
        flavor = f"Sturdy {rarity} chest armor fitted with reinforced plating. Provides vital torso protection against monstrous blows."
    elif cat == "legs":
        flavor = f"Flexible {rarity} leg armor built for rugged mobility. Enhances movement speed and surefooted traversal."
    else: # accessory
        flavor = f"An enchanted {rarity} talisman humming with magical resonance. Bestows passive combat buffs and fortitude."

    if any(k in name_l for k in ("astral", "celestial", "stellar", "sol-rho", "nova", "star")):
        flavor += " Infused with celestial wards."
    elif any(k in name_l for k in ("magma", "pyre", "cinder", "inferno", "ignis", "blaze")):
        flavor += " Warms the bearer with volcanic flame."
    elif any(k in name_l for k in ("frost", "glacial", "cryo", "chill", "ice")):
        flavor += " Quenched in glacial mountain ice."
    elif any(k in name_l for k in ("blight", "void", "shadow", "dread", "abyssal")):
        flavor += " Warded against nether corruption."
    elif any(k in name_l for k in ("spud", "tuber", "russet", "starch")):
        flavor += " Fortified with pure tuber vitality."
    elif any(k in name_l for k in ("ancient", "primordial", "genesis", "eternal")):
        flavor += " Preserves relics from the dawn of Potaria."

    if effects and len(effects) > 0:
        eff_clean = effects[0].split("(")[0].strip()
        flavor += f" Grants {eff_clean}."

    return flavor


def main():
    print("Enriching weapons.json...")
    with open(WEAPONS_FILE, "r", encoding="utf-8") as f:
        weapons = json.load(f)

    for w in weapons:
        if not w.get("desc") or "A " in w.get("desc") and "weapon forged in Potaria." in w.get("desc"):
            w["desc"] = generate_weapon_desc(w)

    with open(WEAPONS_FILE, "w", encoding="utf-8") as f:
        json.dump(weapons, f, indent=2)

    print(f"Updated {len(weapons)} weapons in {WEAPONS_FILE} with rich descriptions.")

    print("Enriching equipments.json...")
    with open(EQUIPMENTS_FILE, "r", encoding="utf-8") as f:
        equipments = json.load(f)

    for eq in equipments:
        if not eq.get("desc") or "piece." in eq.get("desc"):
            eq["desc"] = generate_equipment_desc(eq)

    with open(EQUIPMENTS_FILE, "w", encoding="utf-8") as f:
        json.dump(equipments, f, indent=2)

    print(f"Updated {len(equipments)} equipments in {EQUIPMENTS_FILE} with rich descriptions.")

if __name__ == "__main__":
    main()
