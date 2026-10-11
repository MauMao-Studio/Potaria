"""
Potaria - Modding & DLC Expansion System
Provides data-driven loader for custom content, community mods, and expansions.
"""

from src.modding.mod_manager import ModManager, ModManifest, get_mod_manager

__all__ = ["ModManager", "ModManifest", "get_mod_manager"]
