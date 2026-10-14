import sys, os
sys.path.insert(0, os.getcwd())
from tests.test_food_and_ingredients import RAW_INGREDIENTS, CRAFTABLE_DISHES
from src.ui.inventory import ITEM_REGISTRY
from src.ui.crafting import RECIPES

all_items = RAW_INGREDIENTS + list(CRAFTABLE_DISHES.keys())
print("Total items:", len(all_items))
recipe_map = {r["result"]: r for r in RECIPES}

for item in sorted(all_items):
    d = ITEM_REGISTRY[item]
    r = recipe_map.get(item)
    st = r["station"] if r else "None"
    req = r["requires"] if r else {}
    desc = d.get("desc", "")
    heal = d.get("heal", 0)
    print(f"{item:25} | {d['name']:30} | Heal: {heal:3} | Station: {str(st):8} | Req: {req}")
