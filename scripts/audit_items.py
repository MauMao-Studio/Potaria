import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import re
import json

from src.ui.inventory import ITEM_REGISTRY, ITEM_ALIASES

print(f"Total items in ITEM_REGISTRY: {len(ITEM_REGISTRY)}")

# 1. Check all items currently in ITEM_REGISTRY
empty_desc = []
none_desc = []
short_desc = []
generic_desc = []

for item_id, data in ITEM_REGISTRY.items():
    if "desc" not in data:
        empty_desc.append((item_id, "MISSING_KEY"))
    elif data["desc"] is None:
        none_desc.append((item_id, "NONE"))
    elif str(data["desc"]).strip() == "":
        empty_desc.append((item_id, "EMPTY_STR"))
    elif len(str(data["desc"]).strip()) < 15:
        short_desc.append((item_id, data["desc"]))
    elif "weapon forged in Potaria" in str(data["desc"]) or "piece." in str(data["desc"]):
        generic_desc.append((item_id, data["desc"]))

print(f"Missing key: {len(empty_desc)}, None: {len(none_desc)}, Short: {len(short_desc)}, Generic fallback: {len(generic_desc)}")

# 2. Check weapons.json and equipments.json
with open("data/weapons.json", "r", encoding="utf-8") as f:
    weapons = json.load(f)

with open("data/equipments.json", "r", encoding="utf-8") as f:
    equipments = json.load(f)

w_no_desc = [w["id"] for w in weapons if not w.get("desc") or str(w.get("desc")).strip() == ""]
e_no_desc = [e["id"] for e in equipments if not e.get("desc") or str(e.get("desc")).strip() == ""]

print(f"weapons.json without desc: {len(w_no_desc)} / {len(weapons)}")
print(f"equipments.json without desc: {len(e_no_desc)} / {len(equipments)}")

# 3. Check all items referenced in source code
used_items = set()
for root, _, files in os.walk("src"):
    for file in files:
        if file.endswith(".py"):
            with open(os.path.join(root, file), "r", encoding="utf-8") as fh:
                txt = fh.read()
                for m in re.findall(r"['\"]([a-zA-Z0-9_]+)['\"]", txt):
                    if m in ITEM_REGISTRY or m in ITEM_ALIASES:
                        used_items.add(m)

print(f"Total used item IDs matched: {len(used_items)}")

# 4. Check items looking like screenshot 1: diamond-shaped white crystal / shard / celestial
print("\nItems with 'shard', 'crystal', 'portal', 'celestial', 'essence', 'diamond', 'white', 'gem', 'fragment':")
for k, v in ITEM_REGISTRY.items():
    if any(sub in k.lower() for sub in ["shard", "crystal", "portal", "celestial", "diamond", "white", "gem", "fragment"]):
        print(f"  {k} -> {v.get('name')} | desc: {repr(v.get('desc'))}")

# 6. Check all DroppedItem calls
dropped_items = set()
for root, _, files in os.walk("src"):
    for file in files:
        if file.endswith(".py"):
            with open(os.path.join(root, file), "r", encoding="utf-8") as fh:
                for line in fh:
                    if "DroppedItem(" in line:
                        parts = line.split("DroppedItem(")
                        for p in parts[1:]:
                            item_match = p.split(",")[0].strip().strip("'\"")
                            dropped_items.add(item_match)

print(f"\nAll dropped items: {dropped_items}")
for it in dropped_items:
    canon = ITEM_ALIASES.get(it, it)
    if canon not in ITEM_REGISTRY:
        print(f"  MISSING FROM ITEM_REGISTRY: {it}")
    else:
        print(f"  {it}: {repr(ITEM_REGISTRY[canon].get('desc'))[:60]}...")


