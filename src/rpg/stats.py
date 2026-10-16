"""
Potaria - Action RPG Statistics Engine (Chroisen Style)
Calculates Level (1-100), EXP curves, HP, MP, ATK, DEF, Crit, and stat scaling.
Developer: Kurados
"""

import math

class PlayerStats:
    def __init__(self):
        # Level & EXP
        self.level = 1
        self.max_level = 100
        self.current_exp = 0
        self.exp_to_next = 100

        # Base Attributes
        self.base_max_hp = 100
        self.base_max_mp = 50
        self.base_atk = 10
        self.base_def = 2
        self.base_crit_rate = 5.0 # 5% base crit
        self.base_speed = 3.0
        self.base_atk_speed = 1.0 # 1.0x (100%) base attack speed

        # Current Pools
        self.hp = 100
        self.mp = 50

        # Bonuses from Equipment & Buffs
        self.bonus_max_hp = 0
        self.bonus_max_mp = 0
        self.bonus_atk = 0
        self.bonus_def = 0
        self.bonus_crit = 0.0
        self.bonus_speed = 0.0
        self.bonus_atk_speed = 0.0

        # Regeneration (Balanced 1.5 MP/s base + equipment bonuses)
        self.base_mp_regen = 1.5
        self.bonus_mp_regen = 0.0
        self.mp_regen_timer = 0.0
        self.hp_regen_timer = 0.0
        self._mp_fraction = 0.0
        self.locked_one_heart = False
        self.items_recycled = 0

        # Dedicated Coin Purse (100 Copper = 1 Silver, 100 Silver = 1 Gold)
        self.copper_coins = 0
        self.silver_coins = 0
        self.gold_coins = 0

    @property
    def total_copper_value(self):
        """Returns total purchasing power across all coins in copper denomination."""
        return int(self.copper_coins + self.silver_coins * 100 + self.gold_coins * 10000)

    def add_coins(self, copper=0, silver=0, gold=0):
        """Adds currency and automatically normalizes denominations (100c = 1s, 100s = 1g)."""
        total = self.total_copper_value + int(copper) + int(silver) * 100 + int(gold) * 10000
        self.set_from_copper(total)

    def set_from_copper(self, total_copper):
        """Sets the purse coins directly from a total copper integer with automatic breakdown."""
        total_copper = max(0, int(total_copper))
        self.gold_coins = total_copper // 10000
        rem = total_copper % 10000
        self.silver_coins = rem // 100
        self.copper_coins = rem % 100

    def remove_coins(self, total_copper):
        """Deducts total_copper from purse with automatic change breakdown. Returns True if successful."""
        total_copper = int(total_copper)
        if self.total_copper_value >= total_copper:
            self.set_from_copper(self.total_copper_value - total_copper)
            return True
        return False

    def set_yolo_mode(self, enabled=True):
        """Locks player permanently to exactly 1 heart (20 HP) that cannot increment in any means."""
        self.locked_one_heart = enabled
        if enabled:
            self.base_max_hp = 20
            self.bonus_max_hp = 0
            self.hp = min(20, self.hp)

    @property
    def max_hp(self):
        if getattr(self, "locked_one_heart", False):
            return 20
        return self.base_max_hp + self.bonus_max_hp

    @max_hp.setter
    def max_hp(self, val):
        if not getattr(self, "locked_one_heart", False):
            self.base_max_hp = max(1, int(val) - self.bonus_max_hp)

    @property
    def max_mp(self):
        return self.base_max_mp + self.bonus_max_mp

    @max_mp.setter
    def max_mp(self, val):
        self.base_max_mp = max(0, int(val) - self.bonus_max_mp)

    @property
    def total_atk(self):
        return self.base_atk + self.bonus_atk

    @property
    def attack(self):
        return self.total_atk

    @property
    def total_def(self):
        return self.base_def + self.bonus_def

    @property
    def total_crit_rate(self):
        return min(75.0, self.base_crit_rate + self.bonus_crit)

    @property
    def total_crit_damage_multiplier(self):
        return 1.8

    @property
    def total_speed(self):
        return self.base_speed + self.bonus_speed

    @property
    def total_atk_speed(self):
        return round(max(0.2, self.base_atk_speed + self.bonus_atk_speed), 2)

    @property
    def attack_speed(self):
        return self.total_atk_speed

    @property
    def atk_speed(self):
        return self.total_atk_speed

    @property
    def total_mp_regen(self):
        return round(self.base_mp_regen + self.bonus_mp_regen, 2)

    @property
    def exp(self):
        return self.current_exp

    @property
    def crit_chance(self):
        return self.total_crit_rate

    def gain_exp(self, amount):
        return self.add_exp(amount)

    def add_exp(self, amount):
        """Awards EXP and handles level-ups."""
        if self.level >= self.max_level:
            return False

        self.current_exp += amount
        leveled_up = False

        while self.current_exp >= self.exp_to_next and self.level < self.max_level:
            self.current_exp -= self.exp_to_next
            self.level += 1
            leveled_up = True

            # RPG Level Scaling
            if not getattr(self, "locked_one_heart", False):
                self.base_max_hp += 15
            self.base_max_mp += 8
            self.base_atk += 3
            self.base_def += 1
            if self.level % 5 == 0:
                self.base_crit_rate += 1.0

            # Exponential EXP curve
            self.exp_to_next = int(100 * (self.level ** 2.1))

            # Full heal upon level up!
            self.hp = self.max_hp
            self.mp = self.max_mp

        return leveled_up

    def update(self, dt):
        """Regenerates MP (balanced 1.5 MP/s base + equipment bonuses) and subtle HP over time."""
        # MP regeneration
        total_mp_rate = max(0.5, self.base_mp_regen + self.bonus_mp_regen)
        self._mp_fraction += total_mp_rate * dt
        if self._mp_fraction >= 1.0:
            add_mp = int(self._mp_fraction)
            self._mp_fraction -= add_mp
            if self.mp < self.max_mp:
                self.mp = min(self.max_mp, self.mp + add_mp)

        # HP slow regeneration
        self.hp_regen_timer += dt
        if self.hp_regen_timer >= 3.0:
            self.hp_regen_timer = 0.0
            if self.hp < self.max_hp:
                self.hp = min(self.max_hp, self.hp + 1)
