import os
import sys

sys.path.insert(0, os.getcwd())

from src.ui.inventory import ITEM_REGISTRY
from src.ui.crafting import RECIPES

# Category definitions
filipino_dishes = [
    'chicken_adobo', 'pork_adobo', 'sinigang', 'kare_kare', 'bulalo', 'tinola',
    'lechon', 'pancit_bihon', 'arroz_caldo', 'halo_halo', 'kaldereta', 'balut',
    'itlog_na_maalat', 'sinangag', 'daing_na_bangus', 'sinigang_na_bangus',
    'ginataang_tilapia', 'kinilaw_na_tanigue'
]

cooked_fishes = [
    'cooked_bangus', 'cooked_tilapia', 'cooked_galunggong', 'cooked_maya_maya',
    'cooked_tanigue', 'cooked_tambakol', 'cooked_lapu_lapu', 'cooked_hito',
    'cooked_dilis', 'cooked_dalagang_bukid'
]

potato_delicacies = [
    'mashed_potato', 'golden_fry', 'hearty_root_stew', 'glazed_golden_tuber',
    'smoked_spud_jerky', 'gilded_russet', 'potato_bread', 'sweet_tuber_pie',
    'herbal_salve'
]

raw_fishes = [
    'raw_bangus', 'raw_tilapia', 'raw_galunggong', 'raw_maya_maya', 'raw_tanigue',
    'raw_tambakol', 'raw_lapu_lapu', 'raw_hito', 'raw_dilis', 'raw_dalagang_bukid'
]

raw_meats = [
    'raw_chicken', 'raw_pork', 'pork_belly', 'raw_beef', 'raw_goat_meat',
    'duck_egg', 'carabao_milk'
]

pantry_ingredients = [
    'raw_potato', 'rice', 'garlic', 'onion', 'ginger', 'tamarind', 'eggplant',
    'string_beans', 'black_pepper', 'calamansi', 'soy_sauce', 'vinegar',
    'salt', 'shaved_ice', 'condensed_milk', 'ube_halaya', 'pancit_noodles',
    'peanut_butter', 'coconut_milk', 'spud_sap', 'seaweed', 'snow_block',
    'wood', 'glowing_mushroom', 'gold_bar'
]

recipe_map = {r["result"]: r for r in RECIPES}

ITEM_ACQUISITION = {
    'raw_potato': 'Cultivated from Tilled Soil or harvested from wild Spud patches.',
    'rice': 'Harvested from flooded paddy tiles or purchased from rural traders.',
    'garlic': 'Foraged in lowland grassy meadows or cultivated in home gardens.',
    'onion': 'Cultivated from vegetable seeds or found in agricultural crates.',
    'ginger': 'Harvested from root patches in forest clearings and riverbanks.',
    'tamarind': 'Gathered from tropical wild tamarind trees.',
    'eggplant': 'Farmed in fertile soil patches or collected from wild flora.',
    'string_beans': 'Cultivated along crop trellises or foraged in bushlands.',
    'black_pepper': 'Harvested from pepper vines in deep forest groves.',
    'calamansi': 'Picked from native citrus shrubs found near coastal settlements.',
    'soy_sauce': 'Brewed condiment obtained from general goods traders or fermented cellars.',
    'vinegar': 'Fermented by hand from fresh Spud Sap in glass jars.',
    'salt': 'Smelted in a furnace by evaporating mineral-rich Tangled Seaweed.',
    'shaved_ice': 'Hand-crushed from fresh Mountain Snow Blocks.',
    'condensed_milk': 'Simmered in a furnace using Fresh Carabao Milk and sweet Spud Sap.',
    'ube_halaya': 'Slow-cooked in a furnace with Purple Spuds, condensed milk, and sap.',
    'pancit_noodles': 'Rolled and cut by hand from ground Milagrosa Rice flour.',
    'peanut_butter': 'Roasted and ground in a furnace using tubers, sap, and sea salt.',
    'coconut_milk': 'Extracted by hand from shredded palm fiber and natural sap.',
    'spud_sap': 'Extracted by tapping mature wild tuber roots and sacred trees.',
    'seaweed': 'Dived and foraged along shallow coastal waters and coral reefs.',
    'snow_block': 'Quarried from the frosty peaks of the sub-zero alpine biome.',
    'wood': 'Chopped from forest trees using any woodcutting axe.',
    'glowing_mushroom': 'Harvested from bioluminescent deep cavern biomes.',
    'gold_bar': 'Smelted in a stone furnace from raw gold ore veins.',
    'raw_bangus': 'Caught with fishing rod in brackish estuaries and calm lagoons.',
    'raw_tilapia': 'Caught in freshwater rivers, inland lakes, and ponds.',
    'raw_galunggong': 'Caught in open sea waters and ocean shores.',
    'raw_maya_maya': 'Caught around deep offshore coral drop-offs.',
    'raw_tanigue': 'Prized game fish hooked in open ocean waters using advanced rods.',
    'raw_tambakol': 'Hooked in deep ocean currents with sturdy fishing tackle.',
    'raw_lapu_lapu': 'Rare catch landed around rocky sea caves and deep ocean reefs.',
    'raw_hito': 'Hooked in muddy swamps, marshy pools, and murky riverbeds.',
    'raw_dilis': 'Netted or caught with light tackle along shallow coastal shores.',
    'raw_dalagang_bukid': 'Vibrant reef fish hooked near sunlit coral gardens.',
    'raw_chicken': 'Obtained from native free-range poultry in grassy meadows.',
    'raw_pork': 'Obtained from native wild boars and domesticated pigs.',
    'pork_belly': 'Choice cut harvested from prime livestock or rural butchers.',
    'raw_beef': 'Harvested from pastoral cattle in highland pasturelands.',
    'raw_goat_meat': 'Sourced from agile mountain goats navigating cliffside crags.',
    'duck_egg': 'Gathered from riverside duck nesting grounds and farm coops.',
    'carabao_milk': 'Gently milked from docile carabaos resting near mud wallows.'
}

# 1. GENERATE MARKDOWN
def generate_markdown():
    os.makedirs("docs", exist_ok=True)
    md_path = os.path.join("docs", "POTARIA_COOKBOOK_GUIDE.md")
    
    lines = []
    lines.append("# Potaria Culinary Master Catalog and Cooking Guide")
    lines.append("")
    lines.append("## Overview")
    lines.append("Cooking is a core survival and adventuring system in Potaria. Consuming prepared meals restores substantial health points (HP), enables high-tier sustain during boss encounters, and utilizes locally foraged, farmed, hunted, and fished ingredients. Recipes are crafted either in a cooking station (Furnace) or assembled directly by hand.")
    lines.append("")
    lines.append("### Cooking Stations")
    lines.append("* **Furnace (`station=\"furnace\"`)**: The primary hearth station for simmering stews, frying fish, boiling broths, and baking bread. Requires charcoal or wood combustion.")
    lines.append("* **By Hand (`station=None`)**: Direct crafting for cold desserts, fresh condiments, cured raw delicacies, and artisanal noodle kneading without thermal equipment.")
    lines.append("")
    lines.append("---")
    lines.append("")

    sections = [
        ("Authentic Filipino Cuisine", filipino_dishes, "Signature traditional dishes featuring complex savory, sour, and aromatic flavor profiles."),
        ("Fried, Smoked, and Steamed Fish", cooked_fishes, "Fresh marine and freshwater catches cooked over embers to maximize healing value."),
        ("Potato Specialities and Delicacies", potato_delicacies, "Artisanal root-based dishes, energy-dense pastries, and restorative tuber salves."),
        ("Fresh Catches (Raw Fishes)", raw_fishes, "Wild aquatic species caught with fishing rods across diverse biomes."),
        ("Livestock, Poultry, and Dairy", raw_meats, "Nutrient-rich animal cuts and farm goods harvested from native wildlife."),
        ("Pantry, Spices, and Cooking Essentials", pantry_ingredients, "Foundational crops, milled grains, seasonings, and binding agents used across recipes.")
    ]

    for title, items, description in sections:
        lines.append(f"## {title}")
        lines.append(f"{description}")
        lines.append("")
        lines.append("| Item Name | Item ID | Health Restore | Crafting Station | Ingredients / Acquisition | Description |")
        lines.append("|---|---|---|---|---|---|")
        
        for item_id in items:
            data = ITEM_REGISTRY[item_id]
            name = data.get("name", item_id)
            heal = f"{data.get('heal', 0)} HP" if data.get('heal', 0) > 0 else "Ingredient"
            desc = data.get("desc", "").replace("\n", " ").replace("|", "-")
            rec = recipe_map.get(item_id)
            if rec:
                station = "Furnace" if rec.get("station") == "furnace" else "By Hand"
                ing_list = [f"{cnt}x {ITEM_REGISTRY.get(iid, {}).get('name', iid)}" for iid, cnt in rec.get("ingredients", [])]
                req_str = ", ".join(ing_list)
            else:
                station = "N/A (Harvested)"
                req_str = ITEM_ACQUISITION.get(item_id, "Harvested from wild exploration.")
            
            lines.append(f"| {name} | `{item_id}` | {heal} | {station} | {req_str} | {desc} |")
        
        lines.append("")
        lines.append("---")
        lines.append("")

    with open(md_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print(f"Generated Markdown Guide: {md_path}")

generate_markdown()
