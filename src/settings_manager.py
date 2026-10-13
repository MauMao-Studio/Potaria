"""
Potaria - Settings Manager & Configuration Lifecycle
Handles persistent user settings and key bindings:
1. Canonical path resolution anchored to PROJECT_ROOT (CWD-independent)
2. Robust atomic file writes (.tmp -> .bak -> replace) with os.fsync
3. Automatic corruption recovery from .bak
4. Immediate in-memory and disk synchronization
5. Type validation and schema default fallback
Developer: Kurados
"""

import os
import json
import atexit
from typing import Tuple, Dict, Any, Optional

from src.constants import PROJECT_ROOT, SAVES_DIR, SETTINGS_FILE

# Default Game Settings Configuration
DEFAULT_SETTINGS: Dict[str, Any] = {
    "master_volume": 1.0,
    "bgm_volume": 0.65,
    "sfx_volume": 0.85,
    "fullscreen": False,
    "screen_shake": True,
    "touch_controls": "auto",
    "touch_opacity": 0.75,
    "renderer": "hardware",
    "bloom": True,
    "shaders": True,
    "vignette": True,
    "water_effects": False,
    "resolution": "1920x1080",
    "color_grade": "vibrant",
    "lighting_quality": "high",
    "particle_density": "high",
    "boost_mode": True,
    "damage_numbers": True,
    "tooltips": "detailed",
}

# Default Key Bindings (standard scancodes)
# a=97, d=100, space=32, s=115, e=101, c=99, m=109, q=113, f=102, v=118, r=114
DEFAULT_KEY_BINDINGS: Dict[str, int] = {
    "Move Left": 97,
    "Move Right": 100,
    "Jump": 32,
    "Drop Platform": 115,
    "Inventory": 101,
    "Character Status": 99,
    "Toggle Mini-Map": 109,
    "Skill Q": 113,
    "Skill F": 102,
    "Skill V": 118,
    "Skill R": 114,
}

# Global in-memory reference to ensure game and menus share exact same state
_CURRENT_SETTINGS: Optional[Dict[str, Any]] = None
_CURRENT_KEY_BINDINGS: Optional[Dict[str, int]] = None


def load_settings(path: str = SETTINGS_FILE) -> Tuple[Dict[str, Any], Dict[str, int]]:
    """
    Loads persistent user settings and key bindings from disk.
    If the file is missing or corrupted, automatically recovers from backup (.bak).
    Merges saved configuration with schema defaults to guarantee all keys exist.
    """
    global _CURRENT_SETTINGS, _CURRENT_KEY_BINDINGS

    settings = dict(DEFAULT_SETTINGS)
    key_bindings = dict(DEFAULT_KEY_BINDINGS)

    target_path = os.path.abspath(path)
    backup_path = target_path + ".bak"

    data = None

    # 1. Try reading the primary settings file
    if os.path.exists(target_path):
        try:
            with open(target_path, "r", encoding="utf-8") as f:
                content = f.read().strip()
                if content:
                    data = json.loads(content)
        except Exception as e:
            print(f"[SettingsManager] Warning: Failed to read {target_path} ({e}). Checking backup...")
            data = None

    # 2. If primary failed or was invalid, attempt recovery from backup
    if not isinstance(data, dict) and os.path.exists(backup_path):
        try:
            with open(backup_path, "r", encoding="utf-8") as f:
                content = f.read().strip()
                if content:
                    data = json.loads(content)
            print(f"[SettingsManager] Successfully recovered configuration from {backup_path}")
        except Exception as e:
            print(f"[SettingsManager] Backup recovery failed ({e}). Using default configuration.")
            data = None

    # 3. Merge parsed values with defaults
    if isinstance(data, dict):
        saved_cfg = data.get("settings", {})
        if isinstance(saved_cfg, dict):
            for k in DEFAULT_SETTINGS:
                if k in saved_cfg:
                    val = saved_cfg[k]
                    def_val = DEFAULT_SETTINGS[k]
                    if isinstance(def_val, bool):
                        settings[k] = bool(val)
                    elif isinstance(def_val, float):
                        try:
                            settings[k] = float(val)
                        except (ValueError, TypeError):
                            pass
                    elif isinstance(def_val, int):
                        try:
                            settings[k] = int(val)
                        except (ValueError, TypeError):
                            pass
                    elif isinstance(def_val, str):
                        settings[k] = str(val)

        saved_keys = data.get("key_bindings", {})
        if isinstance(saved_keys, dict):
            for action in DEFAULT_KEY_BINDINGS:
                if action in saved_keys:
                    try:
                        key_bindings[action] = int(saved_keys[action])
                    except (ValueError, TypeError):
                        pass

    _CURRENT_SETTINGS = settings
    _CURRENT_KEY_BINDINGS = key_bindings
    return settings, key_bindings


def save_settings(
    settings: Optional[Dict[str, Any]] = None,
    key_bindings: Optional[Dict[str, int]] = None,
    path: str = SETTINGS_FILE
) -> bool:
    """
    Atomically persists user settings and key bindings to disk.
    Uses .tmp file + flush + os.fsync + .bak rotation + os.replace to prevent
    file corruption or truncation on unexpected termination.
    """
    global _CURRENT_SETTINGS, _CURRENT_KEY_BINDINGS

    if settings is not None:
        _CURRENT_SETTINGS = settings
    elif _CURRENT_SETTINGS is not None:
        settings = _CURRENT_SETTINGS
    else:
        settings = dict(DEFAULT_SETTINGS)
        _CURRENT_SETTINGS = settings

    if key_bindings is not None:
        _CURRENT_KEY_BINDINGS = key_bindings
    elif _CURRENT_KEY_BINDINGS is not None:
        key_bindings = _CURRENT_KEY_BINDINGS
    else:
        key_bindings = dict(DEFAULT_KEY_BINDINGS)
        _CURRENT_KEY_BINDINGS = key_bindings

    target_path = os.path.abspath(path)
    os.makedirs(os.path.dirname(target_path), exist_ok=True)
    temp_path = target_path + ".tmp"
    backup_path = target_path + ".bak"

    payload = {
        "settings": settings,
        "key_bindings": key_bindings,
    }

    try:
        # Write to temporary file with flush and fsync
        with open(temp_path, "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2)
            f.flush()
            try:
                os.fsync(f.fileno())
            except (AttributeError, OSError):
                pass

        # Create/update backup copy of existing valid settings
        if os.path.exists(target_path):
            try:
                with open(target_path, "r", encoding="utf-8") as src, open(backup_path, "w", encoding="utf-8") as dst:
                    dst.write(src.read())
                    dst.flush()
                    try:
                        os.fsync(dst.fileno())
                    except (AttributeError, OSError):
                        pass
            except Exception:
                pass

        # Atomically replace target file
        os.replace(temp_path, target_path)
        return True
    except Exception as e:
        print(f"[SettingsManager] Failed to save settings to {target_path}: {e}")
        if os.path.exists(temp_path):
            try:
                os.remove(temp_path)
            except OSError:
                pass
        return False


def get_current_settings() -> Dict[str, Any]:
    """Returns the active in-memory settings dictionary (loads from disk if not yet loaded)."""
    global _CURRENT_SETTINGS, _CURRENT_KEY_BINDINGS
    if _CURRENT_SETTINGS is None:
        load_settings()
    return _CURRENT_SETTINGS


def get_current_key_bindings() -> Dict[str, int]:
    """Returns the active in-memory key bindings dictionary (loads from disk if not yet loaded)."""
    global _CURRENT_SETTINGS, _CURRENT_KEY_BINDINGS
    if _CURRENT_KEY_BINDINGS is None:
        load_settings()
    return _CURRENT_KEY_BINDINGS


def update_setting(key: str, value: Any, auto_save: bool = True, path: str = SETTINGS_FILE) -> None:
    """Updates a single setting in memory and optionally flushes to disk immediately."""
    cur = get_current_settings()
    cur[key] = value
    if auto_save:
        save_settings(cur, get_current_key_bindings(), path=path)


def _on_exit_save():
    """Atexit handler ensuring any modified settings are safely flushed to disk on shutdown."""
    if _CURRENT_SETTINGS is not None:
        save_settings(_CURRENT_SETTINGS, _CURRENT_KEY_BINDINGS)


atexit.register(_on_exit_save)
