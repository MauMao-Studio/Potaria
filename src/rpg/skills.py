"""
Potaria - Skill Book & Combat Skills Engine (Chroisen Style)
Handles active combat abilities mapped to hotkeys (Q, F, C, R),
MP costs, cooldown sweeps, and Skill Book consumption.
Developer: Kurados
"""

import math
import pygame

SKILL_DEFINITIONS = {
    "power_slash": {
        "id": "power_slash",
        "name": "Power Slash",
        "hotkey": "Q",
        "mp_cost": 8,
        "cooldown": 2.0,
        "dmg_mult": 1.6,
        "desc": "Heavy forward sword cleave dealing 160% damage."
    },
    "whirlwind": {
        "id": "whirlwind",
        "name": "Whirlwind",
        "hotkey": "F",
        "mp_cost": 10,
        "cooldown": 3.0,
        "dmg_mult": 1.3,
        "desc": "Spins in 360 degrees striking all surrounding foes."
    },
    "dash": {
        "id": "dash",
        "name": "Swift Dash",
        "hotkey": "V",
        "mp_cost": 5,
        "cooldown": 1.5,
        "dmg_mult": 0.0,
        "desc": "Rapid forward dash with temporary invincibility."
    },
    "fireball": {
        "id": "fireball",
        "name": "Fireball",
        "hotkey": "R",
        "mp_cost": 8,
        "cooldown": 2.2,
        "dmg_mult": 1.8,
        "desc": "Casts a blazing fire orb that detonates on impact."
    },
    "meteor": {
        "id": "meteor",
        "name": "Meteor Strike",
        "hotkey": "G",
        "mp_cost": 40,
        "cooldown": 12.0,
        "dmg_mult": 4.5,
        "legendary": True,
        "desc": "[Grand Legendary] Summons a devastating flaming meteor plunging from the sky."
    },
    "frost_nova": {
        "id": "frost_nova",
        "name": "Frost Nova",
        "hotkey": "X",
        "mp_cost": 12,
        "cooldown": 3.5,
        "dmg_mult": 1.6,
        "desc": "Blasts a freezing blizzard wave chilling and damaging all nearby foes."
    },
    "celestial_shield": {
        "id": "celestial_shield",
        "name": "Celestial Shield",
        "hotkey": "Z",
        "mp_cost": 36,
        "cooldown": 14.0,
        "dmg_mult": 2.0,
        "legendary": True,
        "desc": "[Grand Legendary] Summons an orbiting radiant barrier that deflects attacks and harms attackers."
    },
    "void_singularity": {
        "id": "void_singularity",
        "name": "Void Singularity",
        "hotkey": "C",
        "mp_cost": 48,
        "cooldown": 16.0,
        "dmg_mult": 5.0,
        "legendary": True,
        "desc": "[Grand Legendary] Summons a catastrophic gravitational vortex crushing all nearby foes."
    }
}

class SkillManager:
    def __init__(self):
        # Learned skills set & levels (Starts at Lv. 1, up to Lv. 5)
        self.learned_skills = set(["power_slash", "dash"]) # Spud starts knowing basic slash and dash
        self.skill_levels = {"power_slash": 1, "dash": 1}
        self.max_skill_level = 5
        
        # Cooldown trackers: skill_id -> remaining_time
        self.cooldowns = {}
        
        # Active Skill Slots & Hotkey Bindings
        self.active_slots = ["power_slash", "whirlwind", "dash", "fireball"]
        self.hotkey_bindings = {"Q": "power_slash", "F": "whirlwind", "V": "dash", "R": "fireball"}

    @property
    def all_skills(self):
        return SKILL_DEFINITIONS

    def get_skill_level(self, skill_id):
        return self.skill_levels.get(skill_id, 1)

    def get_skill_mp_cost(self, skill_id, player=None):
        data = SKILL_DEFINITIONS.get(skill_id, {})
        base = data.get("mp_cost", 10)
        lvl = self.get_skill_level(skill_id)
        cost = base + (lvl - 1)
        if player and hasattr(player, "has_effect") and player.has_effect("arcane conduit"):
            cost = max(1, int(cost * 0.8))
        return cost

    def get_skill_dmg_mult(self, skill_id):
        data = SKILL_DEFINITIONS.get(skill_id, {})
        base = data.get("dmg_mult", 1.0)
        lvl = self.get_skill_level(skill_id)
        # Power increases by +25% of base per upgrade level
        return round(base * (1.0 + (lvl - 1) * 0.25), 2)

    def get_skill_cooldown(self, skill_id, player=None):
        data = SKILL_DEFINITIONS.get(skill_id, {})
        base = data.get("cooldown", 3.0)
        lvl = self.get_skill_level(skill_id)
        # Higher levels slightly reduce cooldown
        cd = round(max(0.5, base * (1.0 - (lvl - 1) * 0.04)), 1)
        if player and hasattr(player, "has_effect") and player.has_effect("temporal shift"):
            cd = round(max(0.3, cd * 0.85), 2)
        return cd

    def assign_skill(self, hotkey, skill_id):
        """Binds a learned skill to hotkey slot (Q, F, V, R), supporting swapping and unbinding."""
        hk = hotkey.upper()
        if hk == "C":
            hk = "V"
        if hk not in ("Q", "F", "V", "R"):
            return False

        if skill_id is None:
            self.hotkey_bindings[hk] = None
            return True

        if skill_id not in self.learned_skills:
            return False

        # If this skill is already bound to another hotkey, swap with whatever is currently in target hk
        old_target_sid = self.hotkey_bindings.get(hk)
        for existing_hk, bound_sid in list(self.hotkey_bindings.items()):
            if bound_sid == skill_id and existing_hk != hk:
                self.hotkey_bindings[existing_hk] = old_target_sid
                break

        self.hotkey_bindings[hk] = skill_id
        return True

    def learn_skill(self, skill_id):
        """Learns or upgrades a skill by consuming duplicate skillbooks (Lv. 1 to 5)."""
        if skill_id not in SKILL_DEFINITIONS:
            return False

        if skill_id not in self.learned_skills:
            self.learned_skills.add(skill_id)
            self.skill_levels[skill_id] = 1
            return True
        else:
            cur_lvl = self.skill_levels.get(skill_id, 1)
            if cur_lvl < self.max_skill_level:
                self.skill_levels[skill_id] = cur_lvl + 1
                return True
            return False

    def can_use_skill(self, skill_id, stats, player=None):
        if skill_id not in self.learned_skills:
            return False, "Skill not learned!"
        if self.cooldowns.get(skill_id, 0.0) > 0:
            return False, "Skill on cooldown!"
        
        cost = self.get_skill_mp_cost(skill_id, player=player)
        if stats.mp < cost:
            return False, "Not enough MP!"
        return True, "Ready"

    def use_skill(self, skill_id, stats, player=None):
        can_use, _ = self.can_use_skill(skill_id, stats, player=player)
        if not can_use:
            return False

        cost = self.get_skill_mp_cost(skill_id, player=player)
        cd = self.get_skill_cooldown(skill_id, player=player)
        stats.mp -= cost
        self.cooldowns[skill_id] = cd
        return True

    def update(self, dt):
        """Ticks down active skill cooldowns."""
        for s_id in list(self.cooldowns.keys()):
            self.cooldowns[s_id] = max(0.0, self.cooldowns[s_id] - dt)
            if self.cooldowns[s_id] <= 0:
                del self.cooldowns[s_id]
