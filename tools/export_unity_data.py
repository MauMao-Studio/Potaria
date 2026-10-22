import os
import sys
import json
import shutil

sys.path.insert(0, '.')
from scripts.build_cookbook_docs import filipino_dishes, cooked_fishes, potato_delicacies, raw_fishes, raw_meats, pantry_ingredients, ITEM_ACQUISITION
from src.ui.inventory import ITEM_REGISTRY
from src.ui.crafting import RECIPES
from src.rpg.equipment_update import PROGRESSIVE_SETS

os.makedirs('Assets/Data', exist_ok=True)

# 1. 79 Food Items
all_79_keys = filipino_dishes + cooked_fishes + potato_delicacies + raw_fishes + raw_meats + pantry_ingredients

food_items_list = []
for k in all_79_keys:
    reg = ITEM_REGISTRY.get(k, {})
    buff_raw = reg.get('buff', {})
    buff_cat_str = 'None'
    buff_name = ''
    buff_duration = 0.0
    buff_stats = {}
    if isinstance(buff_raw, dict) and buff_raw:
        c = buff_raw.get('category', 'none').capitalize()
        if c in ['Offense', 'Defense', 'Mobility', 'Resource', 'Utility']:
            buff_cat_str = c
        buff_name = buff_raw.get('name', '')
        buff_duration = float(buff_raw.get('duration', 0))
        buff_stats = buff_raw.get('stats', {})

    heal_val = int(reg.get('heal', 0))
    cook_duration = 0.0
    if k in filipino_dishes:
        cook_duration = 8.0
    elif k in cooked_fishes:
        cook_duration = 5.0
    elif k in potato_delicacies:
        cook_duration = 4.0

    nutrition_val = heal_val // 2 if heal_val > 0 else 10
    if k in raw_meats or k in raw_fishes:
        nutrition_val = 15

    sprite_file = f'{k}.png'
    sprite_rel = ''
    for test_dir in ['Items', 'Craftable_items', 'Tiles', 'UI', 'Effects']:
        p = os.path.join('Assets', 'Sprites', test_dir, sprite_file)
        if os.path.exists(p):
            sprite_rel = f'Assets/Sprites/{test_dir}/{sprite_file}'
            break

    food_items_list.append({
        'itemId': k,
        'itemName': reg.get('name', k.replace('_', ' ').title()),
        'category': reg.get('cat', 'consumable').capitalize(),
        'rarity': reg.get('rarity', 'common').capitalize(),
        'maxStack': int(reg.get('max_stack', 99)),
        'nutrition': nutrition_val,
        'healthRestore': heal_val,
        'cookingDuration': cook_duration,
        'buffCategory': buff_cat_str,
        'buffName': buff_name,
        'buffDuration': buff_duration,
        'buffStats': buff_stats,
        'description': reg.get('desc', ''),
        'lore': reg.get('lore', ''),
        'special': reg.get('special', ''),
        'effects': reg.get('effects', []),
        'acquisition': ITEM_ACQUISITION.get(k, ''),
        'spritePath': sprite_rel
    })

with open('Assets/Data/food_items.json', 'w', encoding='utf-8') as f:
    json.dump(food_items_list, f, indent=2)
print(f'Wrote {len(food_items_list)} food items to Assets/Data/food_items.json.')

# 2. Crops
crops_def = [
    {'cropId': 'rice', 'cropName': 'Rice', 'seedItemId': 'rice_seeds', 'harvestItemId': 'rice', 'minYield': 2, 'maxYield': 4, 'minSeed': 1, 'maxSeed': 2},
    {'cropId': 'garlic', 'cropName': 'Garlic', 'seedItemId': 'garlic_seeds', 'harvestItemId': 'garlic', 'minYield': 2, 'maxYield': 4, 'minSeed': 1, 'maxSeed': 2},
    {'cropId': 'onion', 'cropName': 'Onion', 'seedItemId': 'onion_seeds', 'harvestItemId': 'onion', 'minYield': 1, 'maxYield': 2, 'minSeed': 1, 'maxSeed': 2},
    {'cropId': 'ginger', 'cropName': 'Ginger', 'seedItemId': 'ginger_seeds', 'harvestItemId': 'ginger', 'minYield': 1, 'maxYield': 2, 'minSeed': 1, 'maxSeed': 2},
    {'cropId': 'eggplant', 'cropName': 'Eggplant', 'seedItemId': 'eggplant_seeds', 'harvestItemId': 'eggplant', 'minYield': 1, 'maxYield': 2, 'minSeed': 1, 'maxSeed': 2},
    {'cropId': 'string_beans', 'cropName': 'String Beans', 'seedItemId': 'string_beans_seeds', 'harvestItemId': 'string_beans', 'minYield': 1, 'maxYield': 2, 'minSeed': 1, 'maxSeed': 2},
    {'cropId': 'tamarind', 'cropName': 'Tamarind', 'seedItemId': 'tamarind_seeds', 'harvestItemId': 'tamarind', 'minYield': 1, 'maxYield': 2, 'minSeed': 1, 'maxSeed': 2},
    {'cropId': 'calamansi', 'cropName': 'Calamansi', 'seedItemId': 'calamansi_seeds', 'harvestItemId': 'calamansi', 'minYield': 2, 'maxYield': 4, 'minSeed': 1, 'maxSeed': 2},
    {'cropId': 'potato', 'cropName': 'Potato', 'seedItemId': 'raw_potato', 'harvestItemId': 'raw_potato', 'minYield': 2, 'maxYield': 3, 'minSeed': 1, 'maxSeed': 2}
]

crops_list = []
for c in crops_def:
    crops_list.append({
        'cropId': c['cropId'],
        'cropName': c['cropName'],
        'seedItemId': c['seedItemId'],
        'harvestItemId': c['harvestItemId'],
        'growthStagesCount': 4,
        'stageDurationSeconds': 40.0,
        'minLightRequirement': 0.35,
        'requiresHydratedFarmland': True,
        'moistureGrowthMultiplier': 1.0,
        'dryGrowthMultiplier': 0.35,
        'minHarvestYield': c['minYield'],
        'maxHarvestYield': c['maxYield'],
        'minSeedYield': c['minSeed'],
        'maxSeedYield': c['maxSeed']
    })

with open('Assets/Data/crops.json', 'w', encoding='utf-8') as f:
    json.dump(crops_list, f, indent=2)
print(f'Wrote {len(crops_list)} crops to Assets/Data/crops.json.')

# 3. Recipes
recipes_list = []
for idx, r in enumerate(RECIPES):
    st_raw = r.get('station')
    station_str = 'Hand'
    if st_raw == 'furnace':
        station_str = 'Furnace'
    elif st_raw == 'work_bench':
        station_str = 'WorkBench'
    elif st_raw == 'campfire':
        station_str = 'Campfire'

    ings = []
    for ing in r.get('ingredients', []):
        if isinstance(ing, (list, tuple)) and len(ing) >= 2:
            ings.append({'itemId': str(ing[0]), 'count': int(ing[1])})

    result_name = r.get('result', '')
    recipes_list.append({
        'recipeId': f'recipe_{idx}_{result_name}',
        'resultItemId': result_name,
        'resultCount': int(r.get('count', 1)),
        'craftingStation': station_str,
        'category': r.get('category', 'survival').capitalize(),
        'ingredients': ings
    })

with open('Assets/Data/recipes.json', 'w', encoding='utf-8') as f:
    json.dump(recipes_list, f, indent=2)
print(f'Wrote {len(recipes_list)} recipes to Assets/Data/recipes.json.')

# 4. Equipment Sets
sets_list = []
for s_id, s_data in PROGRESSIVE_SETS.items():
    thresholds_list = []
    for pieces_count, t_info in s_data.get('thresholds', {}).items():
        thresholds_list.append({
            'requiredPieces': int(pieces_count),
            'title': f'{pieces_count}-Piece Bonus',
            'description': t_info.get('desc', ''),
            'atkMult': float(t_info.get('atk_mult', 0.0)),
            'defMult': float(t_info.get('def_mult', 0.0)),
            'bonusSpeed': float(t_info.get('bonus_speed', 0.0)),
            'bonusCrit': float(t_info.get('bonus_crit', 0.0)),
            'bonusHp': int(t_info.get('bonus_hp', 0)),
            'bonusMpRegen': float(t_info.get('bonus_mp_regen', 0.0)),
            'bonusAtkSpeed': float(t_info.get('bonus_atk_speed', 0.0)),
            'auraEffect': t_info.get('aura', ''),
            'specialPassive': t_info.get('desc', '')
        })

    tag_str = ''
    if s_id.startswith('sin_'):
        tag_str = 'SDS'
    elif s_id.startswith('virtue_'):
        tag_str = 'SHV'
    elif s_id == 'katipunero':
        tag_str = 'Katipunero'

    sets_list.append({
        'setId': s_id,
        'setName': s_data.get('name', s_id.title()),
        'setTag': tag_str,
        'pieces': s_data.get('pieces', []),
        'thresholds': thresholds_list
    })

with open('Assets/Data/equipment_sets.json', 'w', encoding='utf-8') as f:
    json.dump(sets_list, f, indent=2)
print(f'Wrote {len(sets_list)} equipment sets to Assets/Data/equipment_sets.json.')

# 5. Copy data/weapons.json and data/equipments.json
shutil.copy2('data/weapons.json', 'Assets/Data/weapons.json')
shutil.copy2('data/equipments.json', 'Assets/Data/equipments.json')
print('Copied weapons.json and equipments.json to Assets/Data/.')
