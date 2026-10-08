import os, sys, glob, json
sys.path.insert(0, os.path.abspath("."))
from src.ui.inventory import ITEM_REGISTRY, ITEM_ALIASES

print("Checking ITEM_REGISTRY items for missing description...")
missing_desc = []
for k, v in ITEM_REGISTRY.items():
    d = v.get("desc")
    if not d or not str(d).strip():
        missing_desc.append(k)

print(f"Total items in ITEM_REGISTRY: {len(ITEM_REGISTRY)}")
print(f"Items with missing/empty desc: {len(missing_desc)}")
if missing_desc:
    print("Examples:", missing_desc[:10])

# Check data/weapons.json and data/equipments.json
for json_path in ["data/weapons.json", "data/equipments.json"]:
    if os.path.exists(json_path):
        with open(json_path, "r", encoding="utf-8") as f:
            items = json.load(f)
        no_d = [it for it in items if not it.get("desc")]
        print(f"{json_path}: {len(items)} items, {len(no_d)} missing desc")
        for it in no_d:
            print(f"  Missing: {it.get('id')} ({it.get('name')})")

# Now check all DroppedItem spawns in combat_system.py, mob.py, boss.py
for path in ["src/combat/combat_system.py", "src/entities/mob.py", "src/entities/boss.py", "src/world/world.py"]:
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()
    import re
    # Find DroppedItem(..., "item_id", ...)
    matches = re.findall(r'DroppedItem\([^)]*["\']([a-zA-Z0-9_]+)["\']', content)
    for m in matches:
        canon = ITEM_ALIASES.get(m, m)
        if m not in ITEM_REGISTRY and canon not in ITEM_REGISTRY:
            print(f"CRITICAL: Dropped item '{m}' in {path} NOT registered in ITEM_REGISTRY!")
