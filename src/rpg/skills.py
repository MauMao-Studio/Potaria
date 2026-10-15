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
        "evolved_name": "Cataclysmic Cleave",
        "hotkey": "Q",
        "mp_cost": 8,
        "cooldown": 2.0,
        "dmg_mult": 1.6,
        "desc": "Heavy forward sword cleave dealing 160% damage."
    },
    "whirlwind": {
        "id": "whirlwind",
        "name": "Whirlwind",
        "evolved_name": "Tempest Cyclone",
        "hotkey": "F",
        "mp_cost": 10,
        "cooldown": 3.0,
        "dmg_mult": 1.3,
        "desc": "Spins in 360 degrees striking all surrounding foes."
    },
    "dash": {
        "id": "dash",
        "name": "Swift Dash",
        "evolved_name": "Phantom Dash",
        "hotkey": "V",
        "mp_cost": 5,
        "cooldown": 1.5,
        "dmg_mult": 0.0,
        "desc": "Rapid forward dash with temporary invincibility."
    },
    "fireball": {
        "id": "fireball",
        "name": "Fireball",
        "evolved_name": "Inferno Blast",
        "hotkey": "R",
        "mp_cost": 8,
        "cooldown": 2.2,
        "dmg_mult": 1.8,
        "desc": "Casts a blazing fire orb that detonates on impact."
    },
    "earth_slam": {
        "id": "earth_slam",
        "name": "Earth Slam",
        "evolved_name": "Tectonic Rupture",
        "hotkey": "E",
        "mp_cost": 14,
        "cooldown": 4.0,
        "dmg_mult": 2.2,
        "desc": "Slams the ground producing a seismic shockwave shattering nearby enemies."
    },
    "shield_bash": {
        "id": "shield_bash",
        "name": "Shield Bash",
        "evolved_name": "Aegis Bulwark",
        "hotkey": "B",
        "mp_cost": 12,
        "cooldown": 3.0,
        "dmg_mult": 1.5,
        "desc": "Dashes forward with an impenetrable guard, bashing and stunning foes."
    },
    "meteor": {
        "id": "meteor",
        "name": "Meteor Strike",
        "evolved_name": "Grand Starfall",
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
        "evolved_name": "Glacial Blizzard",
        "hotkey": "X",
        "mp_cost": 12,
        "cooldown": 3.5,
        "dmg_mult": 1.6,
        "desc": "Blasts a freezing blizzard wave chilling and damaging all nearby foes."
    },
    "celestial_shield": {
        "id": "celestial_shield",
        "name": "Celestial Shield",
        "evolved_name": "Divine Sanctuary",
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
        "evolved_name": "Event Horizon",
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
        # Skill combos / charge windows: skill_id -> {"charges_left": int, "window_timer": float, "cd": float}
        self.skill_combos = {}
        
        # Active Skill Slots & Hotkey Bindings
        self.active_slots = ["power_slash", "whirlwind", "dash", "fireball"]
        self.hotkey_bindings = {"Q": "power_slash", "F": "whirlwind", "V": "dash", "R": "fireball"}

    @property
    def all_skills(self):
        return SKILL_DEFINITIONS

    def get_skill_level(self, skill_id):
        return self.skill_levels.get(skill_id, 1)

    def is_skill_evolved(self, skill_id):
        """Returns True if skill has reached evolution tier (Lv. 3+)."""
        return self.get_skill_level(skill_id) >= 3 and ("evolved_name" in SKILL_DEFINITIONS.get(skill_id, {}))

    def get_skill_name(self, skill_id):
        data = SKILL_DEFINITIONS.get(skill_id, {})
        if self.is_skill_evolved(skill_id):
            return data.get("evolved_name", data.get("name", "---"))
        return data.get("name", "---")

    def get_skill_mp_cost(self, skill_id, player=None):
        data = SKILL_DEFINITIONS.get(skill_id, {})
        base = data.get("mp_cost", 10)
        lvl = self.get_skill_level(skill_id)
        cost = base + (lvl - 1)
        if player and hasattr(player, "has_effect") and player.has_effect("arcane conduit"):
            cost = max(1, int(cost * 0.8))
        if player and hasattr(player, "get_meal_buff_val"):
            mcr = player.get_meal_buff_val("mana_cost_reduction")
            if mcr > 0:
                cost = max(1, int(cost * (1.0 - mcr)))
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
        
        # Check combo charges window
        combo = self.skill_combos.get(skill_id)
        if combo and combo.get("charges_left", 0) > 0 and combo.get("window_timer", 0.0) > 0:
            cost = self.get_skill_mp_cost(skill_id, player=player)
            if stats.mp < cost:
                return False, "Not enough MP!"
            return True, "Combo Ready"

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

        # Check if currently inside a combo window (e.g. 2nd dash of Phantom Dash)
        combo = self.skill_combos.get(skill_id)
        if combo and combo.get("charges_left", 0) > 0:
            combo["charges_left"] -= 1
            if combo["charges_left"] <= 0:
                final_cd = combo.get("cd", cd)
                del self.skill_combos[skill_id]
                self.cooldowns[skill_id] = final_cd
            return True

        # First cast
        if skill_id == "dash" and self.is_skill_evolved("dash"):
            # Phantom Dash: grants 1 additional consecutive dash within 1.2s window
            self.skill_combos[skill_id] = {
                "charges_left": 1,
                "window_timer": 1.2,
                "cd": cd
            }
            # Cooldown is NOT started yet while window is active
        else:
            self.cooldowns[skill_id] = cd

        return True

    def update(self, dt):
        """Ticks down active skill cooldowns and combo window timers."""
        # Update combo charge windows
        for s_id in list(self.skill_combos.keys()):
            combo = self.skill_combos[s_id]
            combo["window_timer"] -= dt
            if combo["window_timer"] <= 0:
                # Window expired without using remaining charge -> trigger cooldown
                cd = combo.get("cd", self.get_skill_cooldown(s_id))
                del self.skill_combos[s_id]
                self.cooldowns[s_id] = cd

        # Update active cooldowns
        for s_id in list(self.cooldowns.keys()):
            self.cooldowns[s_id] = max(0.0, self.cooldowns[s_id] - dt)
            if self.cooldowns[s_id] <= 0:
                del self.cooldowns[s_id]
