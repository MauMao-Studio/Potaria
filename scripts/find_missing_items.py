import os
import sys
import re
import json

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.ui.inventory import ITEM_REGISTRY, ITEM_ALIASES

all_registered = set(ITEM_REGISTRY.keys()) | set(ITEM_ALIASES.keys())

candidates = set()
for root, _, files in os.walk('.'):
    if '.git' in root or '__pycache__' in root:
        continue
    for f in files:
        if f.endswith('.py'):
            with open(os.path.join(root, f), 'r', encoding='utf-8') as fh:
                for line in fh:
                    for fn in ('DroppedItem', 'ItemStack', 'add_item', 'remove_item', 'count_item', 'has_item', 'give_item', 'generate_item_icon', 'items.get'):
                        pattern = re.escape(fn) + r'\s*\(\s*[\'"]([a-zA-Z0-9_]+)[\'"]'
                        for m in re.finditer(pattern, line):
                            candidates.add((m.group(1), f, fn))

for it, f, fn in sorted(candidates):
    if it not in all_registered:
        print(f'MISSING ITEM: {it} in {f} ({fn})')

# Check all recipes in crafting
from src.ui.crafting import RECIPES
for r in RECIPES:
    res = r.get('result')
    if res not in all_registered:
        print(f'MISSING RECIPE RESULT: {res}')
    for ing, count in r.get('ingredients', []):
        if ing not in all_registered:
            print(f'MISSING RECIPE INGREDIENT: {ing}')

# Check all NPC shops
from src.entities.npc import MerchantNPC, BlacksmithNPC, GuideNPC, NurseNPC
for cls in (MerchantNPC, BlacksmithNPC, GuideNPC, NurseNPC):
    dummy = cls('test', 'test', 0, 0, None, None)
    for it in getattr(dummy, 'shop_catalog', []):
        iid = it.get('item_id')
        if iid not in all_registered:
            print(f'MISSING SHOP ITEM: {iid} in {cls.__name__}')

# Check all achievements
with open('data/achievements.json', 'r', encoding='utf-8') as fh:
    ach = json.load(fh)
    for a in ach:
        desc = a.get('desc', '')
        # print if any interesting items mentioned
