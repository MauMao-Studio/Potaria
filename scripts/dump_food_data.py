import os
import sys

sys.path.insert(0, os.getcwd())

from src.ui.inventory import ITEM_REGISTRY
from src.ui.crafting import RECIPES

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

categories = [
    ("Authentic Filipino Cuisine", filipino_dishes),
    ("Fried and Smoked Fishes", cooked_fishes),
    ("Potato Specialities and Delicacies", potato_delicacies),
    ("Fresh Catches (Raw Fish)", raw_fishes),
    ("Livestock and Poultry (Raw Meats and Dairy)", raw_meats),
    ("Pantry and Culinary Ingredients", pantry_ingredients)
]

for cat_title, items in categories:
    print(f"\n=== {cat_title} ({len(items)} items) ===")
    for item_id in items:
        data = ITEM_REGISTRY[item_id]
        name = data.get("name", item_id)
        heal = data.get("heal", 0)
        desc = data.get("desc", "")
        rec = recipe_map.get(item_id)
        if rec:
            station = rec.get("station") or "By Hand"
            ing_str = ", ".join(f"{cnt}x {ITEM_REGISTRY.get(iid, {}).get('name', iid)}" for iid, cnt in rec.get("ingredients", []))
            recipe_text = f"Station: {station} | Requires: {ing_str}"
        else:
            recipe_text = "Acquisition: Foraging, Fishing, Hunting, or Farming"
        print(f"* {name} ({item_id}) [Heal: {heal}] - {recipe_text}")
