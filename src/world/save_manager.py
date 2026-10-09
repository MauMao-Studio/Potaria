"""
Potaria - World Save & Load Manager (Minecraft-Style Portable JSON)
Saves complete world state: seed, world type, difficulty, game mode,
block deltas, player stats, inventory, equipment, learned skills, and boss progress.
Developer: Kurados
"""

import os
import json
import time
from src.constants import (
    DIFFICULTY_NORMAL, DIFFICULTY_HARDCORE, DIFFICULTY_YOLO,
    MODE_ADVENTURE, MODE_LAST_MAN_STANDING,
    WORLD_TYPE_INFINITE, WORLD_TYPE_FINITE
)
from src.rpg.equipment import SLOT_HEAD, SLOT_CHEST, SLOT_LEGS, SLOT_WEAPON, SLOT_ACCESSORY
from src.ui.inventory import ItemStack

SAVES_DIR = "saves"

def ensure_saves_dir():
    if not os.path.exists(SAVES_DIR):
        os.makedirs(SAVES_DIR, exist_ok=True)

def get_world_dir(world_name):
    clean_name = "".join(c for c in world_name if c.isalnum() or c in (" ", "_", "-")).strip()
    if not clean_name:
        clean_name = "world"
    return os.path.join(SAVES_DIR, clean_name)

def get_world_file(world_name):
    return os.path.join(get_world_dir(world_name), "world.json")

def list_saved_worlds():
    """Returns a list of dictionaries with metadata for all saved worlds."""
    ensure_saves_dir()
    worlds = []
    if not os.path.exists(SAVES_DIR):
        return worlds

    for entry in os.listdir(SAVES_DIR):
        entry_path = os.path.join(SAVES_DIR, entry)
        if os.path.isdir(entry_path):
            json_file = os.path.join(entry_path, "world.json")
            if os.path.exists(json_file):
                try:
                    with open(json_file, "r", encoding="utf-8") as f:
                        data = json.load(f)
                    pt = float(data.get("playtime", 0.0))
                    hours = int(pt // 3600)
                    minutes = int((pt % 3600) // 60)
                    playtime_str = f"{hours}h {minutes}m"
                    lp = data.get("last_played")
                    if not lp:
                        ts = data.get("timestamp", 0)
                        lp = time.strftime("%Y-%m-%d %H:%M", time.localtime(ts)) if ts else "Never"

                    worlds.append({
                        "name": data.get("world_name", entry),
                        "folder": entry,
                        "world_type": data.get("world_type", WORLD_TYPE_INFINITE),
                        "difficulty": data.get("difficulty", DIFFICULTY_NORMAL),
                        "game_mode": data.get("game_mode", MODE_ADVENTURE),
                        "seed": data.get("seed", 0),
                        "timestamp": data.get("timestamp", 0),
                        "playtime": pt,
                        "playtime_str": playtime_str,
                        "last_played": lp,
                    })
                except Exception as e:
                    print(f"[SaveManager] Error reading {json_file}: {e}")
    # Sort worlds by most recently saved
    worlds.sort(key=lambda w: w.get("timestamp", 0), reverse=True)
    return worlds

def save_world(world_name, game):
    """Serializes the active game session to saves/<world_name>/world.json."""
    ensure_saves_dir()
    world_dir = get_world_dir(world_name)
    os.makedirs(world_dir, exist_ok=True)
    save_path = os.path.join(world_dir, "world.json")

    # 1. Inventory serialization
    inv_data = []
    for idx, slot in enumerate(game.inventory.slots):
        if slot:
            inv_data.append({
                "slot": idx,
                "item_id": slot.item_id,
                "count": slot.count,
                "enhancement_level": getattr(slot, "enhancement_level", 0),
                "is_broken": getattr(slot, "is_broken", False),
                "affix_slots": getattr(slot, "affix_slots", 0),
                "affixes": getattr(slot, "affixes", []),
                "removed_stats": getattr(slot, "removed_stats", []),
            })

    # 2. Equipment serialization
    raw_equip = dict(getattr(game.player.equipment, "slots", {}))
    equip_data = {}
    for slot_k, item in raw_equip.items():
        if item is None:
            equip_data[slot_k] = None
        elif isinstance(item, str):
            equip_data[slot_k] = item
        elif hasattr(item, "item_id"):
            equip_data[slot_k] = {
                "item_id": item.item_id,
                "count": item.count,
                "enhancement_level": getattr(item, "enhancement_level", 0),
                "is_broken": getattr(item, "is_broken", False),
                "affix_slots": getattr(item, "affix_slots", 0),
                "affixes": getattr(item, "affixes", []),
                "removed_stats": getattr(item, "removed_stats", []),
            }
        else:
            equip_data[slot_k] = None

    # 3. Skills serialization
    learned_skills = []
    if hasattr(game.player, "skills") and hasattr(game.player.skills, "learned_skills"):
        if isinstance(game.player.skills.learned_skills, (set, list)):
            learned_skills = list(game.player.skills.learned_skills)
        elif isinstance(game.player.skills.learned_skills, dict):
            learned_skills = list(game.player.skills.learned_skills.keys())
    skill_levels = dict(getattr(game.player.skills, "skill_levels", {}))
    skill_hotkeys = dict(getattr(game.player.skills, "hotkey_bindings", getattr(game.player.skills, "hotkey_slots", {})))

    # 4. Stats serialization
    stats = game.player.stats
    stats_data = {
        "level": stats.level,
        "current_exp": stats.current_exp,
        "exp_to_next": stats.exp_to_next,
        "hp": stats.hp,
        "mp": stats.mp,
        "base_max_hp": stats.base_max_hp,
        "base_max_mp": stats.base_max_mp,
        "base_atk": stats.base_atk,
        "base_def": stats.base_def,
        "base_crit_rate": stats.base_crit_rate,
        "locked_one_heart": getattr(stats, "locked_one_heart", False),
        "copper_coins": getattr(stats, "copper_coins", 0),
        "silver_coins": getattr(stats, "silver_coins", 0),
        "gold_coins": getattr(stats, "gold_coins", 0),
    }

    # 5. Block & Wall deltas
    block_deltas = []
    for (tx, ty), tid in getattr(game, "block_deltas", {}).items():
        block_deltas.append({"tx": tx, "ty": ty, "tile_id": tid})

    wall_deltas = []
    for (tx, ty), wid in getattr(game, "wall_deltas", {}).items():
        wall_deltas.append({"tx": tx, "ty": ty, "wall_id": wid})

    # 6. Boss progress & active boss
    boss_data = {
        "mini_bosses_slain": getattr(game.combat, "mini_bosses_slain", 0),
        "boss_defeated": getattr(game.combat, "boss_defeated", False),
        "grand_boss_defeated": getattr(game.combat, "grand_boss_defeated", False),
        "dungeon_boss_slain": getattr(game.combat, "dungeon_boss_slain", False),
    }

    active_boss_data = None
    if getattr(game, "combat", None) and getattr(game.combat, "boss", None) and not getattr(game.combat.boss, "is_dead", False):
        b = game.combat.boss
        active_boss_data = {
            "type": getattr(b, "boss_type", b.__class__.__name__.lower()),
            "name": getattr(b, "name", "Boss"),
            "x": float(b.x),
            "y": float(b.y),
            "hp": int(b.hp),
            "max_hp": int(b.max_hp),
            "phase": int(getattr(b, "phase", 1)),
        }

    alive_mobs_data = []
    if getattr(game, "combat", None) and hasattr(game.combat, "mobs"):
        for m in game.combat.mobs:
            if not m.is_dead and m.hp > 0:
                alive_mobs_data.append({
                    "mob_id": getattr(m, "mob_id", 0),
                    "mob_type": getattr(m, "mob_type", "green_slime"),
                    "x": float(m.x),
                    "y": float(m.y),
                    "hp": int(m.hp),
                    "max_hp": int(m.max_hp),
                    "vx": float(m.vx),
                    "vy": float(m.vy),
                    "facing_right": bool(getattr(m, "facing_right", True)),
                })

    dropped_items_data = []
    if getattr(game, "combat", None) and hasattr(game.combat, "dropped_items"):
        for it in game.combat.dropped_items:
            if not getattr(it, "picked_up", False) and getattr(it, "life", 1.0) > 0:
                dropped_items_data.append({
                    "item_id": it.item_id,
                    "count": it.count,
                    "x": float(it.x),
                    "y": float(it.y),
                })

    chests_data = []
    if hasattr(game, "world") and hasattr(game.world, "chests"):
        for (ctx, cty), chest_obj in game.world.chests.items():
            if hasattr(chest_obj, "to_dict"):
                chests_data.append(chest_obj.to_dict())

    w_type = getattr(game, "world_type", getattr(game.world, "world_type", WORLD_TYPE_INFINITE))
    if hasattr(game, "world") and hasattr(game.world, "world_type") and hasattr(game, "world_type"):
        game.world.world_type = game.world_type

    cur_time = time.time()
    last_played_str = time.strftime("%Y-%m-%d %H:%M", time.localtime(cur_time))
    total_playtime = float(getattr(game, "playtime", 0.0))

    payload = {
        "world_name": world_name,
        "seed": game.world.seed,
        "world_type": w_type,
        "difficulty": getattr(game, "difficulty", DIFFICULTY_NORMAL),
        "game_mode": getattr(game, "game_mode", MODE_ADVENTURE),
        "timestamp": cur_time,
        "playtime": total_playtime,
        "last_played": last_played_str,
        "sky_time": float(getattr(game.sky, "time", 0.0)) if hasattr(game, "sky") else 0.0,
        "player": {
            "x": game.player.x,
            "y": game.player.y,
            "spawn_point": list(game.player.spawn_point) if getattr(game.player, "spawn_point", None) else None,
            "stats": stats_data,
            "inventory": inv_data,
            "equipment": equip_data,
            "skills": learned_skills,
            "skill_levels": skill_levels,
            "skill_hotkeys": skill_hotkeys,
        },
        "boss_progress": boss_data,
        "active_boss": active_boss_data,
        "alive_mobs": alive_mobs_data,
        "dropped_items": dropped_items_data,
        "block_deltas": block_deltas,
        "wall_deltas": wall_deltas,
        "town_npcs": [npc.to_dict() for npc in getattr(game.world, "town_npcs", []) if hasattr(npc, "to_dict")],
        "chests": chests_data,
    }

    with open(save_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)

    print(f"[SaveManager] World '{world_name}' successfully saved to {save_path}.")
    return save_path

def load_world(world_name, game):
    """Loads a world from saves/<world_name>/world.json into the running game."""
    save_path = get_world_file(world_name)
    if not os.path.exists(save_path):
        print(f"[SaveManager] Save file not found: {save_path}")
        return False

    try:
        with open(save_path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        print(f"[SaveManager] Failed to load world file '{save_path}': {e}")
        return False

    if not isinstance(data, dict):
        print(f"[SaveManager] Invalid world data format in '{save_path}'")
        return False

    seed = data.get("seed", 123456)
    world_type = data.get("world_type", WORLD_TYPE_INFINITE)
    difficulty = data.get("difficulty", DIFFICULTY_NORMAL)
    game_mode = data.get("game_mode", MODE_ADVENTURE)

    # 1. Rebuild World
    from src.world.world import World
    game.world = World(game.asset_factory, seed=seed, world_type=world_type)
    game.world_type = world_type
    game.difficulty = difficulty
    game.game_mode = game_mode
    game.active_world_name = world_name

    # 2. Replay Block & Wall Deltas
    game.block_deltas = {}
    for d in (data.get("block_deltas") or []):
        tx, ty, tid = d.get("tx"), d.get("ty"), d.get("tile_id")
        if tx is not None and ty is not None and tid is not None:
            game.world.set_tile(tx, ty, tid)
            game.block_deltas[(tx, ty)] = tid

    game.wall_deltas = {}
    for d in (data.get("wall_deltas") or []):
        tx, ty, wid = d.get("tx"), d.get("ty"), d.get("wall_id")
        if tx is not None and ty is not None and wid is not None:
            game.world.set_wall(tx, ty, wid)
            game.wall_deltas[(tx, ty)] = wid

    # 3. Restore Player Position & Stats
    p_data = data.get("player") or {}
    game.player.x = float(p_data.get("x", game.world.spawn_point[0]))
    game.player.y = float(p_data.get("y", game.world.spawn_point[1]))
    if p_data.get("spawn_point"):
        game.player.spawn_point = tuple(p_data["spawn_point"])
        game.world.spawn_point = tuple(p_data["spawn_point"])
    game.player.vx = 0.0
    game.player.vy = 0.0

    s_data = p_data.get("stats") or {}
    stats = game.player.stats
    stats.level = s_data.get("level", 1)
    stats.current_exp = s_data.get("current_exp", 0)
    stats.exp_to_next = s_data.get("exp_to_next", 100)
    stats.base_max_hp = s_data.get("base_max_hp", 100)
    stats.base_max_mp = s_data.get("base_max_mp", 50)
    stats.base_atk = s_data.get("base_atk", 10)
    stats.base_def = s_data.get("base_def", 2)
    stats.base_crit_rate = s_data.get("base_crit_rate", 5.0)
    stats.copper_coins = s_data.get("copper_coins", 0)
    stats.silver_coins = s_data.get("silver_coins", 0)
    stats.gold_coins = s_data.get("gold_coins", 0)

    if difficulty == DIFFICULTY_YOLO or s_data.get("locked_one_heart", False):
        stats.set_yolo_mode(True)
    else:
        stats.set_yolo_mode(False)

    stats.hp = min(stats.max_hp, s_data.get("hp", stats.max_hp))
    stats.mp = min(stats.max_mp, s_data.get("mp", stats.max_mp))
    game.player.health = stats.hp

    # 4. Restore Inventory
    from src.ui.inventory import ItemStack, INV_TOTAL_SLOTS
    game.inventory.slots = [None] * INV_TOTAL_SLOTS
    game.inventory.held_item = None
    for item in (p_data.get("inventory") or []):
        slot_idx = item.get("slot")
        if slot_idx is not None and 0 <= slot_idx < INV_TOTAL_SLOTS:
            st = ItemStack(
                item["item_id"],
                item["count"],
                enhancement_level=item.get("enhancement_level", 0),
                is_broken=item.get("is_broken", False),
                affix_slots=item.get("affix_slots", 0),
                affixes=item.get("affixes", []),
                removed_stats=item.get("removed_stats", [])
            )
            game.inventory.slots[slot_idx] = st

    # Link player.inventory to game.inventory both ways
    game.player.inventory = game.inventory
    game.inventory.player = game.player

    # Automatically migrate any legacy coins in inventory slots into the Coin Purse
    game.inventory.migrate_coins()

    # 5. Restore Equipment (Guarantee all 5 slots exist)
    equip_data = p_data.get("equipment") or {}
    for slot_k in (SLOT_HEAD, SLOT_CHEST, SLOT_LEGS, SLOT_WEAPON, SLOT_ACCESSORY):
        raw_val = equip_data.get(slot_k, None)
        if isinstance(raw_val, dict) and "item_id" in raw_val:
            item = ItemStack(raw_val["item_id"], raw_val.get("count", 1))
            item.enhancement_level = raw_val.get("enhancement_level", 0)
            item.is_broken = raw_val.get("is_broken", False)
            item.affix_slots = raw_val.get("affix_slots", 0)
            item.affixes = list(raw_val.get("affixes", []))
            item.removed_stats = list(raw_val.get("removed_stats", []))
            game.player.equipment.slots[slot_k] = item
        else:
            game.player.equipment.slots[slot_k] = raw_val
    game.player.equipment.recalculate_stats(game.player.stats)

    # 6. Restore Skills
    skills_data = p_data.get("skills") or []
    if isinstance(skills_data, (set, list)):
        game.player.skills.learned_skills = set(skills_data)
    elif isinstance(skills_data, dict):
        game.player.skills.learned_skills = set(skills_data.keys())

    if "skill_levels" in p_data and hasattr(game.player.skills, "skill_levels"):
        game.player.skills.skill_levels = dict(p_data["skill_levels"])
    elif isinstance(skills_data, dict) and hasattr(game.player.skills, "skill_levels"):
        game.player.skills.skill_levels = dict(skills_data)

    hotkeys = p_data.get("skill_hotkeys") or {}
    default_hotkeys = {"Q": "power_slash", "F": None, "V": "dash", "R": None}
    if hasattr(game.player.skills, "hotkey_bindings"):
        merged_hotkeys = dict(default_hotkeys)
        merged_hotkeys.update(hotkeys)
        game.player.skills.hotkey_bindings = merged_hotkeys
    if hasattr(game.player.skills, "hotkey_slots"):
        game.player.skills.hotkey_slots = dict(game.player.skills.hotkey_bindings)

    # 7. Restore Boss Progress & Combat Entities
    b_data = data.get("boss_progress") or {}
    game.combat.mini_bosses_slain = b_data.get("mini_bosses_slain", 0)
    game.combat.boss_defeated = b_data.get("boss_defeated", False)
    game.combat.grand_boss_defeated = b_data.get("grand_boss_defeated", False)
    game.combat.dungeon_boss_slain = b_data.get("dungeon_boss_slain", False)

    # Reset combat engine entities completely
    if hasattr(game, "combat"):
        game.combat.boss = None
        game.combat.mobs.clear()
        game.combat.projectiles.clear()
        game.combat.enemy_projectiles.clear()
        game.combat.dropped_items.clear()
        game.combat.damage_numbers.clear()

    # Restore Day/Night cycle
    if hasattr(game, "sky"):
        game.sky.time = float(data.get("sky_time", 0.0))

    # Restore Active Boss if saved
    if data.get("active_boss") and hasattr(game, "combat"):
        b_data = data["active_boss"]
        b_type = b_data.get("type", "lord_malus")
        bx = float(b_data.get("x", 0.0))
        by = float(b_data.get("y", 0.0))
        try:
            from src.entities.boss import create_boss_by_type
            game.combat.boss = create_boss_by_type(b_type, bx, by, game.asset_factory, game.sound_manager)
            game.combat.boss.boss_type = b_type
            game.combat.boss.hp = int(b_data.get("hp", game.combat.boss.hp))
            game.combat.boss.max_hp = int(b_data.get("max_hp", game.combat.boss.max_hp))
            game.combat.boss.phase = int(b_data.get("phase", 1))
        except Exception as e:
            print(f"[SaveManager] Error restoring boss: {e}")

    # Restore Alive Mobs
    if data.get("alive_mobs") and hasattr(game, "combat"):
        from src.entities.mob import create_mob_by_type
        for md in data["alive_mobs"]:
            try:
                m_type = md.get("mob_type", "green_slime")
                mx = float(md.get("x", 0.0))
                my = float(md.get("y", 0.0))
                m = create_mob_by_type(m_type, mx, my, game.asset_factory)
                m.mob_id = md.get("mob_id", game.combat.next_mob_id)
                m.hp = int(md.get("hp", m.hp))
                m.max_hp = int(md.get("max_hp", m.max_hp))
                m.vx = float(md.get("vx", 0.0))
                m.vy = float(md.get("vy", 0.0))
                m.facing_right = bool(md.get("facing_right", True))
                game.combat.mobs.append(m)
            except Exception as e:
                print(f"[SaveManager] Error restoring mob: {e}")

    # Restore Dropped Items
    if data.get("dropped_items") and hasattr(game, "combat"):
        from src.entities.dropped_item import DroppedItem
        for it in data["dropped_items"]:
            try:
                game.combat.dropped_items.append(
                    DroppedItem(it["item_id"], int(it.get("count", 1)), float(it["x"]), float(it["y"]), game.asset_factory)
                )
            except Exception as e:
                print(f"[SaveManager] Error restoring dropped item: {e}")

    # Restore Town NPCs
    if "town_npcs" in data and hasattr(game, "world"):
        game.world.town_npcs.clear()
        from src.entities.npc import TownNPC
        for nd in data["town_npcs"]:
            try:
                npc = TownNPC.from_dict(nd, game.asset_factory, game.sound_manager)
                game.world.town_npcs.append(npc)
            except Exception as e:
                print(f"[SaveManager] Error restoring Town NPC: {e}")

    # Restore Storage Chests
    if hasattr(game, "world"):
        game.world.chests = {}
        from src.world.storage_chest import StorageChest
        for cdata in data.get("chests", []):
            try:
                chest_obj = StorageChest.from_dict(cdata)
                game.world.chests[(chest_obj.tx, chest_obj.ty)] = chest_obj
            except Exception as e:
                print(f"[SaveManager] Error restoring chest: {e}")

    # Restore Playtime
    game.playtime = float(data.get("playtime", 0.0))

    # Update crafting recipes if available
    if hasattr(game, "crafting"):
        game.crafting.update_recipes(game.inventory, game.world, game.player)

    # Re-center camera
    game.camera.set_target(game.player.center_x, game.player.center_y, instant=True)
    print(f"[SaveManager] World '{world_name}' loaded successfully.")
    return True

def delete_world(world_name):
    """Deletes a saved world directory."""
    world_dir = get_world_dir(world_name)
    if os.path.exists(world_dir):
        import shutil
        shutil.rmtree(world_dir)
        print(f"[SaveManager] World '{world_name}' deleted.")
        return True
    return False
