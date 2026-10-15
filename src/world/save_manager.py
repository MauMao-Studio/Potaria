"""
Potaria - World Save & Load Manager (Minecraft-Style Portable JSON)
Saves complete world state: seed, world type, difficulty, game mode,
block deltas, player stats, inventory, equipment, learned skills, and boss progress.
Developer: Kurados
"""

import os
import json
import time
import shutil
import queue
import threading
from src.constants import (
    DIFFICULTY_NORMAL, DIFFICULTY_HARDCORE, DIFFICULTY_YOLO,
    MODE_ADVENTURE, MODE_LAST_MAN_STANDING,
    WORLD_TYPE_INFINITE, WORLD_TYPE_FINITE,
    PROJECT_ROOT, SAVES_DIR
)
from src.rpg.equipment import SLOT_HEAD, SLOT_CHEST, SLOT_LEGS, SLOT_WEAPON, SLOT_ACCESSORY
from src.ui.inventory import ItemStack

MAX_BACKUP_SNAPSHOTS = 5
RESTORE_NOTIFICATION_MSG = "World restored from recent backup due to abnormal shutdown."


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

def get_backup_file(world_name):
    """Returns path to immediate backup saves/<world_name>/world.json.bak."""
    return get_world_file(world_name) + ".bak"

def get_backups_dir(world_name):
    """Returns directory path to rolling snapshots saves/<world_name>/backups/."""
    return os.path.join(get_world_dir(world_name), "backups")

def atomic_write_json(target_path, data, indent=2):
    """
    Atomically writes JSON data to target_path using:
    1. Temporary file (.tmp)
    2. Buffer flush and hardware disk sync (os.fsync)
    3. Atomic file replacement (os.replace)
    """
    target_dir = os.path.dirname(target_path)
    if target_dir:
        os.makedirs(target_dir, exist_ok=True)
    tmp_path = target_path + ".tmp"
    with open(tmp_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=indent)
        f.flush()
        try:
            os.fsync(f.fileno())
        except (AttributeError, OSError):
            pass
    os.replace(tmp_path, target_path)

def verify_save_data(data):
    """
    Validates dictionary structure and HMAC-SHA256 signature integrity.
    Returns (is_valid: bool, reason: str).
    """
    if not isinstance(data, dict):
        return False, "Save data is not a dictionary"
    if "world_name" not in data and "seed" not in data and "player" not in data:
        return False, "Missing essential world save keys"
    if "save_signature" in data:
        expected_sig = data["save_signature"]
        if not isinstance(expected_sig, str) or not expected_sig:
            return False, "Invalid save signature format"
        verify_dict = {k: v for k, v in data.items() if k != "save_signature"}
        verify_raw = json.dumps(verify_dict, sort_keys=True).encode("utf-8")
        try:
            from src.rpg.equipment_update import verify_save_signature
            if not verify_save_signature(verify_raw, expected_sig):
                return False, "HMAC signature mismatch (tampered or corrupted save)"
        except Exception as e:
            return False, f"HMAC verification error: {e}"
    return True, "OK"

def verify_save_file(file_path):
    """
    Reads a save JSON file and validates its JSON syntax, structure, and integrity.
    Returns (is_valid: bool, data: dict or None, reason: str).
    """
    if not file_path or not os.path.isfile(file_path):
        return False, None, "File does not exist"
    try:
        size = os.path.getsize(file_path)
        if size == 0:
            return False, None, "File is truncated (0 bytes)"
    except OSError as e:
        return False, None, f"Cannot stat file: {e}"

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except (json.JSONDecodeError, UnicodeDecodeError, OSError) as e:
        return False, None, f"JSON parse error: {e}"

    is_valid, reason = verify_save_data(data)
    if not is_valid:
        return False, data, reason

    return True, data, "OK"

def prune_backup_snapshots(world_name, max_backups=MAX_BACKUP_SNAPSHOTS):
    """
    Auto-prunes historical snapshots in saves/<world_name>/backups/.
    Keeps only the most recent `max_backups` (default 5) and deletes older ones.
    """
    backups_dir = get_backups_dir(world_name)
    if not os.path.exists(backups_dir):
        return []

    cand_files = []
    for fname in os.listdir(backups_dir):
        if fname.endswith(".json") and not fname.endswith(".tmp"):
            cand_files.append(os.path.join(backups_dir, fname))

    cand_files.sort(key=lambda p: (os.path.getmtime(p), os.path.basename(p)), reverse=True)
    kept = cand_files[:max_backups]
    pruned = cand_files[max_backups:]
    for old_path in pruned:
        try:
            os.remove(old_path)
            print(f"[SaveManager] Pruned old backup: {os.path.basename(old_path)}")
        except OSError as e:
            print(f"[SaveManager] Failed to prune {old_path}: {e}")
    return kept

def list_world_backups(world_name):
    """Returns list of snapshot file paths in saves/<world_name>/backups/ sorted newest first."""
    backups_dir = get_backups_dir(world_name)
    if not os.path.exists(backups_dir):
        return []
    cand_files = [
        os.path.join(backups_dir, f)
        for f in os.listdir(backups_dir)
        if f.endswith(".json") and not f.endswith(".tmp")
    ]
    cand_files.sort(key=lambda p: (os.path.getmtime(p), os.path.basename(p)), reverse=True)
    return cand_files

def create_backup_snapshot(world_name, game=None, payload=None, reason=None, max_backups=MAX_BACKUP_SNAPSHOTS):
    """
    Creates a timestamped snapshot in saves/<world_name>/backups/world_YYYY-MM-DD_HHMM.json.
    Auto-prunes older snapshots to keep at most `max_backups`.
    Returns the created snapshot path on success, or None on failure.
    """
    backups_dir = get_backups_dir(world_name)
    os.makedirs(backups_dir, exist_ok=True)

    ts_base = time.strftime("%Y-%m-%d_%H%M")
    cand_name = f"world_{ts_base}.json"
    target_path = os.path.join(backups_dir, cand_name)

    if os.path.exists(target_path):
        ts_sec = time.strftime("%Y-%m-%d_%H%M%S")
        target_path = os.path.join(backups_dir, f"world_{ts_sec}.json")
        idx = 1
        while os.path.exists(target_path):
            target_path = os.path.join(backups_dir, f"world_{ts_sec}_{idx}.json")
            idx += 1

    if payload is not None:
        atomic_write_json(target_path, payload)
    elif game is not None:
        save_world(world_name, game, create_snapshot=False)
        primary = get_world_file(world_name)
        if os.path.exists(primary):
            shutil.copy2(primary, target_path)
        else:
            return None
    else:
        primary = get_world_file(world_name)
        if os.path.exists(primary) and os.path.getsize(primary) > 0:
            shutil.copy2(primary, target_path)
        else:
            return None

    reason_str = f" ({reason})" if reason else ""
    print(f"[SaveManager] Created backup snapshot{reason_str}: {os.path.basename(target_path)}")
    prune_backup_snapshots(world_name, max_backups=max_backups)
    return target_path

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
            data = None
            if os.path.exists(json_file):
                try:
                    with open(json_file, "r", encoding="utf-8") as f:
                        cand = json.load(f)
                    if isinstance(cand, dict):
                        data = cand
                except Exception:
                    data = None

            if not isinstance(data, dict):
                bak_file = json_file + ".bak"
                if os.path.exists(bak_file):
                    try:
                        with open(bak_file, "r", encoding="utf-8") as f:
                            cand = json.load(f)
                        if isinstance(cand, dict):
                            data = cand
                    except Exception:
                        data = None

            if not isinstance(data, dict):
                b_dir = os.path.join(entry_path, "backups")
                if os.path.exists(b_dir):
                    bfiles = [
                        os.path.join(b_dir, f)
                        for f in os.listdir(b_dir)
                        if f.endswith(".json") and not f.endswith(".tmp")
                    ]
                    bfiles.sort(key=lambda p: (os.path.getmtime(p), os.path.basename(p)), reverse=True)
                    for bf in bfiles:
                        try:
                            with open(bf, "r", encoding="utf-8") as f:
                                cand = json.load(f)
                            if isinstance(cand, dict):
                                data = cand
                                break
                        except Exception:
                            continue

            if isinstance(data, dict):
                try:
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
                    print(f"[SaveManager] Error reading metadata for {entry}: {e}")
    # Sort worlds by most recently saved
    worlds.sort(key=lambda w: w.get("timestamp", 0), reverse=True)
    return worlds

def extract_save_payload(world_name, game):
    """
    Extracts pure Python dictionary snapshots of game, world, inventory, player,
    and active chunk manager data on the main thread in < 1 millisecond.
    Returns (payload: dict, chunk_payloads: list).
    """
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
                "base_rolls": getattr(slot, "base_rolls", None),
                "additional_affix_slots": getattr(slot, "additional_affix_slots", 0),
                "tags": getattr(slot, "tags", None),
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
                "base_rolls": getattr(item, "base_rolls", None),
                "additional_affix_slots": getattr(item, "additional_affix_slots", 0),
                "tags": getattr(item, "tags", None),
            }
        else:
            equip_data[slot_k] = None

    # 3. Skills serialization
    learned_skills = []
    p_skills = getattr(game.player, "skills", None)
    if p_skills and hasattr(p_skills, "learned_skills"):
        if isinstance(p_skills.learned_skills, (set, list)):
            learned_skills = list(p_skills.learned_skills)
        elif isinstance(p_skills.learned_skills, dict):
            learned_skills = list(p_skills.learned_skills.keys())
    skill_levels = dict(getattr(p_skills, "skill_levels", {})) if p_skills else {}
    skill_hotkeys = dict(getattr(p_skills, "hotkey_bindings", getattr(p_skills, "hotkey_slots", {}))) if p_skills else {}

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

    decaying_blocks_data = []
    if hasattr(game, "world") and hasattr(game.world, "decaying_blocks"):
        for (tx, ty), dinfo in game.world.decaying_blocks.items():
            decaying_blocks_data.append({
                "tx": tx,
                "ty": ty,
                "timer": float(dinfo.get("timer", 0.0)),
                "max_timer": float(dinfo.get("max_timer", 0.0)),
                "days_left": int(dinfo.get("days_left", 1)),
                "max_days": int(dinfo.get("max_days", 1)),
                "phase": int(dinfo.get("phase", 0)),
                "type": int(dinfo.get("type", 0))
            })

    planted_saplings_data = []
    if hasattr(game, "world") and hasattr(game.world, "planted_saplings"):
        for (tx, ty), sdata in game.world.planted_saplings.items():
            planted_saplings_data.append({
                "tx": tx,
                "ty": ty,
                "growth_days": int(sdata.get("growth_days", 0)),
                "sapling_type": str(sdata.get("sapling_type", "oak_sapling"))
            })

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
        "decaying_blocks": decaying_blocks_data,
        "planted_saplings": planted_saplings_data,
    }

    try:
        from src.rpg.equipment_update import compute_save_signature
        payload_raw = json.dumps(payload, sort_keys=True).encode("utf-8")
        payload["save_signature"] = compute_save_signature(payload_raw)
    except Exception:
        pass

    # Extract chunk snapshots
    chunk_payloads = []
    if hasattr(game, "world") and hasattr(game.world, "chunk_manager"):
        cm = game.world.chunk_manager
        if hasattr(cm, "set_world_name"):
            cm.set_world_name(world_name)
        if getattr(cm, "world_cache", None):
            for cx, chk in list(getattr(cm, "chunks", {}).items()):
                sky_t = {f"{k[0]},{k[1]}": v for k, v in getattr(chk, "sky_tiles", {}).items()}
                sky_w = {f"{k[0]},{k[1]}": v for k, v in getattr(chk, "sky_walls", {}).items()}
                tiles_copy = [row[:] for row in chk.tiles] if hasattr(chk, "tiles") else []
                walls_copy = [row[:] for row in chk.walls] if hasattr(chk, "walls") else []
                chk_data = {
                    "chunk_x": cx,
                    "seed": getattr(chk, "seed", None),
                    "surface_heights": list(getattr(chk, "surface_heights", [])),
                    "col_biomes": list(getattr(chk, "col_biomes", [])),
                    "tiles": tiles_copy,
                    "walls": walls_copy,
                    "sky_tiles": sky_t,
                    "sky_walls": sky_w,
                }
                chunk_payloads.append((cx, chk_data))

    return payload, chunk_payloads


def write_save_payload_to_disk(world_name, payload, chunk_payloads=None, create_snapshot=False, reason=None, max_backups=MAX_BACKUP_SNAPSHOTS):
    """Writes pre-extracted save payload and chunk cache files to disk with atomic replacement."""
    ensure_saves_dir()
    world_dir = get_world_dir(world_name)
    os.makedirs(world_dir, exist_ok=True)
    save_path = os.path.join(world_dir, "world.json")
    bak_path = get_backup_file(world_name)

    # 1. Flush chunks to disk under saves/<world_name>/cache/chunks/
    if chunk_payloads:
        chunks_dir = os.path.join(world_dir, "cache", "chunks")
        os.makedirs(chunks_dir, exist_ok=True)
        for cx, chk_data in chunk_payloads:
            chunk_file = os.path.join(chunks_dir, f"chunk_{cx}.json")
            try:
                with open(chunk_file, "w", encoding="utf-8") as cf:
                    json.dump(chk_data, cf)
            except Exception as e:
                print(f"[SaveManager] Failed to write chunk {cx}: {e}")

    # 2. Immediate Backup (world.json.bak)
    if os.path.exists(save_path) and os.path.getsize(save_path) > 0:
        try:
            with open(save_path, "r", encoding="utf-8") as cf:
                cur_data = json.load(cf)
            if isinstance(cur_data, dict):
                shutil.copy2(save_path, bak_path)
        except Exception:
            pass

    # 3. Atomic Write
    atomic_write_json(save_path, payload)

    # 4. Rolling Snapshots
    if create_snapshot:
        create_backup_snapshot(world_name, payload=payload, reason=reason, max_backups=max_backups)

    print(f"[SaveManager] World '{world_name}' successfully saved to {save_path}.")
    return save_path


_SAVE_QUEUE = queue.Queue()
_SAVE_WORKER_THREAD = None
_SAVE_LOCK = threading.Lock()
_PENDING_SAVE_EVENT = threading.Event()
_PENDING_SAVE_EVENT.set()

def _save_worker():
    while True:
        task = _SAVE_QUEUE.get()
        if task is None:
            _SAVE_QUEUE.task_done()
            break
        fn, args, kwargs = task
        try:
            _PENDING_SAVE_EVENT.clear()
            fn(*args, **kwargs)
        except Exception as e:
            print(f"[SaveManager] Background save error: {e}")
        finally:
            _SAVE_QUEUE.task_done()
            if _SAVE_QUEUE.empty():
                _PENDING_SAVE_EVENT.set()

def ensure_save_worker():
    global _SAVE_WORKER_THREAD
    with _SAVE_LOCK:
        if _SAVE_WORKER_THREAD is None or not _SAVE_WORKER_THREAD.is_alive():
            _SAVE_WORKER_THREAD = threading.Thread(target=_save_worker, name="PotariaSaveWorker", daemon=True)
            _SAVE_WORKER_THREAD.start()

def wait_for_pending_saves(timeout=5.0):
    """Waits for all queued background saves to complete disk commit."""
    _SAVE_QUEUE.join()
    _PENDING_SAVE_EVENT.wait(timeout=timeout)


def save_world(world_name, game, create_snapshot=False, reason=None, max_backups=MAX_BACKUP_SNAPSHOTS, async_save=False):
    """
    Serializes the active game session to saves/<world_name>/world.json.
    If async_save=True, snapshot is extracted instantly on main thread (< 1ms)
    and heavy disk I/O (fsync, chunk writes, snapshots) is handled in a daemon worker thread.
    """
    ensure_saves_dir()
    world_dir = get_world_dir(world_name)
    os.makedirs(world_dir, exist_ok=True)
    save_path = os.path.join(world_dir, "world.json")

    payload, chunk_payloads = extract_save_payload(world_name, game)

    if async_save:
        ensure_save_worker()
        _PENDING_SAVE_EVENT.clear()
        _SAVE_QUEUE.put((
            write_save_payload_to_disk,
            (world_name, payload, chunk_payloads),
            {"create_snapshot": create_snapshot, "reason": reason, "max_backups": max_backups}
        ))
        return save_path
    else:
        return write_save_payload_to_disk(
            world_name, payload, chunk_payloads,
            create_snapshot=create_snapshot, reason=reason, max_backups=max_backups
        )

def load_world(world_name, game):
    """
    Loads a world from saves/<world_name>/world.json into the running game
    using a Self-Healing Recovery Pipeline:
    1. Try Primary: Read world.json and verify its JSON structure and HMAC signature.
    2. First Fallback (.bak): If world.json is missing, truncated (0 bytes), or corrupt,
       catch the exception and immediately attempt to load world.json.bak.
    3. Second Fallback (Backups Folder): If world.json.bak is also damaged, scan
       saves/<world_name>/backups/ for the most recent valid timestamped JSON file.
    4. Restore & Notify: Once a valid backup is found, copy it back over world.json
       to repair the world, and display: 'World restored from recent backup due to abnormal shutdown.'
    """
    save_path = get_world_file(world_name)
    bak_path = get_backup_file(world_name)
    backups_dir = get_backups_dir(world_name)

    valid_data = None
    recovered_from = None
    tampered_fallback_data = None

    # 1. Try Primary: Read world.json and verify its JSON structure and HMAC signature
    prim_ok, prim_data, prim_reason = verify_save_file(save_path)
    if prim_ok:
        valid_data = prim_data
    else:
        if isinstance(prim_data, dict) and prim_reason == "HMAC signature mismatch (tampered or corrupted save)":
            tampered_fallback_data = prim_data
        print(f"[SaveManager] Primary save file '{save_path}' invalid or corrupted: {prim_reason}")

        # 2. First Fallback: world.json.bak
        if os.path.exists(bak_path):
            bak_ok, b_data, b_reason = verify_save_file(bak_path)
            if bak_ok:
                valid_data = b_data
                recovered_from = bak_path
                print(f"[SaveManager] Successfully recovered world from immediate backup: {bak_path}")
            else:
                print(f"[SaveManager] Immediate backup '{bak_path}' also corrupted: {b_reason}")

        # 3. Second Fallback: Historical Snapshots in backups/
        if not valid_data and os.path.exists(backups_dir):
            cand_files = []
            for fname in os.listdir(backups_dir):
                if fname.endswith(".json") and not fname.endswith(".tmp"):
                    cand_files.append(os.path.join(backups_dir, fname))
            cand_files.sort(key=lambda p: (os.path.getmtime(p), os.path.basename(p)), reverse=True)

            for cand in cand_files:
                c_ok, c_data, c_reason = verify_save_file(cand)
                if c_ok:
                    valid_data = c_data
                    recovered_from = cand
                    print(f"[SaveManager] Successfully recovered world from historical backup: {cand}")
                    break
                else:
                    print(f"[SaveManager] Historical backup '{cand}' invalid: {c_reason}")

    # Fallback if primary only had signature mismatch and no clean backups exist
    if not valid_data and tampered_fallback_data is not None:
        valid_data = tampered_fallback_data
        setattr(game, "save_file_tampered", True)
        print(f"[SaveManager] WARNING: Save file '{world_name}' signature mismatch (possible manual modification).")

    if not valid_data:
        print(f"[SaveManager] Failed to load world '{world_name}': No valid primary save or backup found.")
        return False

    # 4. Restore & Notify: copy backup over world.json to repair world and display notification
    if recovered_from:
        try:
            atomic_write_json(save_path, valid_data)
            print(f"[SaveManager] Repaired '{save_path}' from backup '{recovered_from}'.")
        except Exception as e:
            print(f"[SaveManager] Warning: Failed to write repaired world.json: {e}")

        msg = RESTORE_NOTIFICATION_MSG
        setattr(game, "world_restored_from_backup", True)
        setattr(game, "restored_backup_path", recovered_from)
        setattr(game, "restore_message", msg)

        if hasattr(game, "inventory") and hasattr(game.inventory, "notify"):
            game.inventory.notify(msg)

        if hasattr(game, "hud"):
            if hasattr(game.hud, "add_chat_message"):
                game.hud.add_chat_message("[SYSTEM]", msg)
            elif hasattr(game.hud, "local_chat_history"):
                game.hud.local_chat_history.append(("[SYSTEM]", msg))

        print(f"[SaveManager] {msg}")

    data = valid_data
    if "save_signature" in data and not getattr(game, "save_file_tampered", False):
        expected_sig = data["save_signature"]
        verify_dict = {k: v for k, v in data.items() if k != "save_signature"}
        verify_raw = json.dumps(verify_dict, sort_keys=True).encode("utf-8")
        try:
            from src.rpg.equipment_update import verify_save_signature
            is_valid = verify_save_signature(verify_raw, expected_sig)
            setattr(game, "save_file_tampered", not is_valid)
            if not is_valid:
                print(f"[SaveManager] WARNING: Save file '{world_name}' signature mismatch (possible manual modification).")
        except Exception:
            pass

    seed = data.get("seed", 123456)
    world_type = data.get("world_type", WORLD_TYPE_INFINITE)
    difficulty = data.get("difficulty", DIFFICULTY_NORMAL)
    game_mode = data.get("game_mode", MODE_ADVENTURE)

    # 1. Rebuild World
    from src.world.world import World
    game.world = World(game.asset_factory, seed=seed, world_type=world_type, world_name=world_name)
    game.world.tree_cascade_felling = False
    game.world.game = game
    game.world.combat = getattr(game, "combat", None)
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
                removed_stats=item.get("removed_stats", []),
                base_rolls=item.get("base_rolls"),
                additional_affix_slots=item.get("additional_affix_slots", 0),
                tags=item.get("tags")
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
            item = ItemStack(
                raw_val["item_id"],
                raw_val.get("count", 1),
                enhancement_level=raw_val.get("enhancement_level", 0),
                is_broken=raw_val.get("is_broken", False),
                affix_slots=raw_val.get("affix_slots", 0),
                affixes=list(raw_val.get("affixes", [])),
                removed_stats=list(raw_val.get("removed_stats", [])),
                base_rolls=raw_val.get("base_rolls"),
                additional_affix_slots=raw_val.get("additional_affix_slots", 0),
                tags=raw_val.get("tags")
            )
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
        for attr in ("mobs", "projectiles", "enemy_projectiles", "dropped_items", "damage_numbers"):
            lst = getattr(game.combat, attr, None)
            if isinstance(lst, list):
                lst.clear()

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

    # Restore Tree Decay Blocks & Planted Saplings
    if hasattr(game, "world"):
        if "decaying_blocks" in data and hasattr(game.world, "decaying_blocks"):
            game.world.decaying_blocks.clear()
            for d in data["decaying_blocks"]:
                game.world.decaying_blocks[(d["tx"], d["ty"])] = {
                    "timer": float(d.get("timer", 0.0)),
                    "max_timer": float(d.get("max_timer", 0.0)),
                    "days_left": int(d.get("days_left", 1)),
                    "max_days": int(d.get("max_days", 1)),
                    "phase": int(d.get("phase", 0)),
                    "type": int(d.get("type", 0))
                }
        if "planted_saplings" in data and hasattr(game.world, "planted_saplings"):
            game.world.planted_saplings.clear()
            from src.constants import SAPLING_ITEM_TO_TILE, TILE_SAPLING
            for s in data["planted_saplings"]:
                tx, ty = s["tx"], s["ty"]
                sap_type = str(s.get("sapling_type", "oak_sapling"))
                game.world.planted_saplings[(tx, ty)] = {
                    "growth_days": int(s.get("growth_days", 0)),
                    "sapling_type": sap_type
                }
                if game.world.get_tile(tx, ty) == TILE_SAPLING and sap_type in SAPLING_ITEM_TO_TILE:
                    upgraded_tid = SAPLING_ITEM_TO_TILE[sap_type]
                    game.world.set_tile(tx, ty, upgraded_tid)
                    if hasattr(game, "block_deltas") and (tx, ty) in game.block_deltas:
                        game.block_deltas[(tx, ty)] = upgraded_tid

    # Restore Playtime
    game.playtime = float(data.get("playtime", 0.0))

    # Update crafting recipes if available
    if hasattr(game, "crafting"):
        game.crafting.update_recipes(game.inventory, game.world, game.player)

    # Re-center camera
    if hasattr(game, "camera") and game.camera:
        game.camera.set_target(game.player.center_x, game.player.center_y, instant=True)
    print(f"[SaveManager] World '{world_name}' loaded successfully.")
    return True

def delete_world(world_name):
    """Deletes a saved world directory."""
    world_dir = get_world_dir(world_name)
    if os.path.exists(world_dir):
        import shutil
        import time
        import stat

        def handle_remove_readonly(func, path, exc_info):
            try:
                os.chmod(path, stat.S_IWRITE)
                func(path)
            except Exception:
                pass

        for attempt in range(10):
            try:
                shutil.rmtree(world_dir, onexc=handle_remove_readonly)
                print(f"[SaveManager] World '{world_name}' deleted.")
                return True
            except (PermissionError, OSError):
                time.sleep(0.05)

        shutil.rmtree(world_dir, ignore_errors=True)
        print(f"[SaveManager] World '{world_name}' deleted.")
        return True
    return False


def sanitize_world_name(world_name):
    """Sanitizes a world name to safe alphanumeric, space, underscore, and hyphen characters."""
    if not isinstance(world_name, str):
        return ""
    return "".join(c for c in world_name if c.isalnum() or c in (" ", "_", "-")).strip()


def can_rename_world(old_name, new_name):
    """
    Validates whether `old_name` can be renamed to `new_name`.
    Rejects empty names and strictly rejects any `new_name` that already exists.
    Returns: (is_valid: bool, message: str)
    """
    ensure_saves_dir()
    old_clean = sanitize_world_name(old_name)
    new_clean = sanitize_world_name(new_name)

    if not new_clean:
        return False, "World name cannot be empty!"

    old_dir = get_world_dir(old_clean) if old_clean else ""
    saved = list_saved_worlds()
    target_entry = None
    for w in saved:
        if w.get("name", "").strip() == str(old_name).strip() or w.get("folder", "").strip() == old_clean:
            target_entry = w
            old_dir = os.path.join(SAVES_DIR, w["folder"])
            break

    if not target_entry and (not old_dir or not os.path.exists(old_dir)):
        return False, "World not found!"

    # Check if the new name is identical or already exists in any saved world or directory (case-insensitive)
    if old_clean.lower() == new_clean.lower():
        return False, "World name already exists!"

    for w in saved:
        existing_name = str(w.get("name", "")).strip().lower()
        existing_folder = str(w.get("folder", "")).strip().lower()
        if new_clean.lower() in (existing_name, existing_folder):
            return False, "World name already exists!"

    new_dir = get_world_dir(new_clean)
    if os.path.exists(new_dir):
        return False, "World name already exists!"

    return True, "OK"


def rename_world(old_name, new_name):
    """
    Renames an existing saved world from `old_name` to `new_name`.
    Cannot rename if `new_name` is empty or already exists in `saves/`.
    Updates both the folder name in `saves/` and `world_name` inside `world.json`.
    Returns True on success, False if invalid or name already exists.
    """
    valid, msg = can_rename_world(old_name, new_name)
    if not valid:
        print(f"[SaveManager] Cannot rename '{old_name}' to '{new_name}': {msg}")
        return False

    old_clean = sanitize_world_name(old_name)
    new_clean = sanitize_world_name(new_name)
    old_dir = get_world_dir(old_clean)
    for w in list_saved_worlds():
        if w.get("name", "").strip() == str(old_name).strip() or w.get("folder", "").strip() == old_clean:
            old_dir = os.path.join(SAVES_DIR, w["folder"])
            break

    new_dir = get_world_dir(new_clean)
    if os.path.exists(new_dir):
        return False

    try:
        json_file = os.path.join(old_dir, "world.json")
        if os.path.exists(json_file):
            with open(json_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            data["world_name"] = new_clean
            if "save_signature" in data:
                try:
                    from src.rpg.equipment_update import compute_save_signature
                    verify_dict = {k: v for k, v in data.items() if k != "save_signature"}
                    raw = json.dumps(verify_dict, sort_keys=True).encode("utf-8")
                    data["save_signature"] = compute_save_signature(raw)
                except Exception:
                    pass
            atomic_write_json(json_file, data)
        os.rename(old_dir, new_dir)
        print(f"[SaveManager] World '{old_name}' renamed to '{new_clean}'.")
        return True
    except Exception as e:
        print(f"[SaveManager] Error renaming world '{old_name}' to '{new_clean}': {e}")
        return False

