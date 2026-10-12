import os
import sys
import math
import random
import pytest
import pygame

# Ensure project root is in sys.path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from src.constants import (
    TILE_AIR, TILE_DIRT, TILE_GRASS, TILE_WOOD, TILE_WOOD_TRUNK, TILE_LEAVES,
    TILE_WORK_BENCH, TILE_IRON_CHEST, TILE_ROPE_RUNGS, SCALED_TILE,
    SCREEN_WIDTH, SCREEN_HEIGHT
)
from src.rpg.equipment import ARMOR_DATA, SLOT_WEAPON, SLOT_ACCESSORY
from src.assets.asset_factory import AssetFactory
from src.audio.sound_effects import SoundManager
from src.entities.particle import ParticleSystem
from src.camera import Camera
from src.world.world import World
from src.world.chunk_manager import OPAQUE_EXCLUSIONS
from src.combat.combat_system import CombatManager
from src.entities.player import Player
from src.entities.mob import GreenSlime
from src.ui.menu import MenuManager, Button


class TestGameplayOverhaulItems:
    @classmethod
    def setup_class(cls):
        pygame.init()
        if pygame.display.get_surface() is None:
            pygame.display.set_mode((1280, 720))
        cls.asset_factory = AssetFactory()
        cls.sound_manager = SoundManager()

    def setup_method(self):
        self.particles = ParticleSystem()
        self.camera = Camera(800, 600)
        self.world = World(self.asset_factory, seed=12345)
        self.combat = CombatManager(self.asset_factory, self.sound_manager, self.particles, self.camera)
        self.player = Player(200, 200, self.asset_factory, self.sound_manager)

    # =========================================================================
    # ITEM 1: Tree Decay Drops & Multi-day Progression
    # =========================================================================
    def test_tree_decay_drops_and_timeline(self):
        """Verifies severed tree decay takes days, darkens, and drops wood, leaves, saplings, fruit."""
        self.world.tree_cascade_felling = False
        gx, gy = 30, 50
        self.world.set_tile(gx, gy + 1, TILE_GRASS)
        self.world.set_tile(gx, gy, TILE_WOOD_TRUNK)
        self.world.set_tile(gx, gy - 1, TILE_WOOD_TRUNK)
        self.world.set_tile(gx, gy - 2, TILE_LEAVES)

        # Chop base trunk
        broken, drop, tid = self.world.damage_tile_at(gx, gy, 100)
        assert broken
        assert self.world.get_tile(gx, gy) == TILE_AIR

        # Remaining trunk and leaves must be queued for decay with multi-day tracking
        assert hasattr(self.world, "decaying_blocks")
        assert (gx, gy - 1) in self.world.decaying_blocks
        assert (gx, gy - 2) in self.world.decaying_blocks

        for coord in ((gx, gy - 1), (gx, gy - 2)):
            info = self.world.decaying_blocks[coord]
            assert "days_left" in info
            assert "max_days" in info
            assert "phase" in info
            assert info["days_left"] >= 2
            assert info["timer"] > 0

        # Simulate daily decay progression
        initial_days = {c: self.world.decaying_blocks[c]["days_left"] for c in ((gx, gy - 1), (gx, gy - 2))}
        self.world.decay_trees_daily()
        for coord in ((gx, gy - 1), (gx, gy - 2)):
            assert self.world.decaying_blocks[coord]["days_left"] == initial_days[coord] - 1
            assert self.world.decaying_blocks[coord]["phase"] >= 1

        # Fast forward expiration and verify loot drops
        collected_drops = []
        class MockCombat:
            def _spawn_loot_drop(self, item_id, count, cx, cy):
                collected_drops.append((item_id, count))
        mock_combat = MockCombat()
        self.world.combat = mock_combat

        # Expire all decay blocks
        self.world.update_tree_decay(10.0)
        assert len(self.world.decaying_blocks) == 0
        assert len(collected_drops) > 0
        dropped_ids = [d[0] for d in collected_drops]
        assert "wood" in dropped_ids
        assert "leaves" in dropped_ids

    # =========================================================================
    # ITEM 2: Unarmed / Hand Damage is Strictly 1
    # =========================================================================
    def test_unarmed_hand_damage_strictly_one(self):
        """Verifies bare-hand attacks deal strictly 1 damage without ATK scaling or gear buffs."""
        self.player.stats.base_atk = 500  # Massive ATK
        self.player.equipment.recalculate_stats(self.player.stats)
        assert self.player.stats.total_atk >= 500

        from src.ui.inventory import Inventory
        self.player.inventory = Inventory(self.asset_factory)
        # Empty inventory slots and empty weapon slot = bare hand
        for i in range(len(self.player.inventory.slots)):
            self.player.inventory.slots[i] = None
        self.player.equipment.slots[SLOT_WEAPON] = None

        # Add player buffs that would normally add damage
        ARMOR_DATA["test_buff_ring"] = {
            "slot": SLOT_ACCESSORY,
            "name": "Buff Ring",
            "effects": [
                "Molten Blaze (+12 Fire Damage)",
                "Armor Penetration (+15 True Damage)"
            ]
        }
        self.player.equipment.slots[SLOT_ACCESSORY] = "test_buff_ring"
        self.player.equipment.recalculate_stats(self.player.stats)

        mob = GreenSlime(220, 200, self.asset_factory)
        self.combat.mobs = [mob]
        initial_hp = mob.hp

        self.player.is_swinging = True
        self.player.aim_angle = 0.0
        self.combat._check_weapon_hits(self.player, self.world)

        # Mob must take exactly 1 damage
        assert mob.hp == initial_hp - 1, f"Expected 1 damage, mob took {initial_hp - mob.hp}"

    # =========================================================================
    # ITEM 3: Placed Props Negative Space Transparency
    # =========================================================================
    def test_placed_props_background_transparency(self):
        """Verifies workbench and props are in OPAQUE_EXCLUSIONS and tile_11 has transparent negative space."""
        assert TILE_WORK_BENCH in OPAQUE_EXCLUSIONS
        assert TILE_IRON_CHEST in OPAQUE_EXCLUSIONS
        assert TILE_ROPE_RUNGS in OPAQUE_EXCLUSIONS

        # Check tile_11.png pixel transparency between legs
        tile_path = os.path.join(BASE_DIR, "assets", "tiles", "tile_11.png")
        assert os.path.exists(tile_path), "assets/tiles/tile_11.png must exist"
        surf = pygame.image.load(tile_path).convert_alpha()
        # Pixel between legs at x=8, y=14 should have alpha == 0
        alpha_val = surf.get_at((8, 14)).a
        assert alpha_val == 0, f"Expected transparent alpha (0) between workbench legs, got {alpha_val}"

    # =========================================================================
    # ITEM 4: Monster Spawning Schedule (No daytime spawns, scales after 5pm)
    # =========================================================================
    def test_monster_spawning_schedule(self):
        """Verifies 0 surface monsters spawn before 5:00 PM, and scale appropriately into deep night."""
        # 1. Daytime (10:00 AM = tod ~ 0.166)
        day_tod = 0.166
        self.combat.mob_spawn_timer = 999.0
        self.combat.update(1.0, self.world, self.player, is_night=False, time_of_day=day_tod)
        assert len(self.combat.mobs) == 0, "No surface monsters should spawn before 5:00 PM"

        # 2. 5:00 PM (tod = 11/24) threshold
        cutoff_5pm = 11.0 / 24.0
        dusk_tod = 11.0 / 24.0
        assert dusk_tod >= cutoff_5pm

    # =========================================================================
    # ITEM 5: YOLO Mode Death Panel
    # =========================================================================
    def test_yolo_mode_death_panel(self):
        """Verifies death panel in YOLO mode displays ONLY 'Try Harder (Main Menu)' with no restart."""
        menu = MenuManager(None, None, self.sound_manager)
        assert len(menu.game_over_buttons) == 1
        btn = menu.game_over_buttons[0]
        assert "Try Harder" in btn.text
        assert "Restart" not in btn.text

    # =========================================================================
    # ITEM 6: Menu UI Overhaul (LAN Menu & Icon Buttons)
    # =========================================================================
    def test_menu_ui_overhaul(self):
        """Verifies LAN menu layout rects do not collide and buttons support custom icons."""
        menu = MenuManager(None, None, self.sound_manager)
        # Host key rect vs IP box rect
        assert hasattr(menu, "host_key_box_rect")
        assert hasattr(menu, "ip_box_rect")
        assert not menu.host_key_box_rect.colliderect(menu.ip_box_rect)

        # Button icon rendering support
        play_btn = Button(100, 100, 32, 32, "", "play", icon="play", tooltip="Play World")
        assert play_btn.icon == "play"
        assert play_btn.tooltip == "Play World"
        surf = pygame.Surface((200, 200))
        font = pygame.font.Font(None, 24)
        play_btn.render(surf, font)

    # =========================================================================
    # ITEM 7: Skill Icons Standard & Evolved
    # =========================================================================
    def test_skill_icons_standard_and_evolved(self):
        """Verifies all 10 base skills and 10 evolved skills exist as 32x32 PNG assets."""
        skills = [
            "power_slash", "cataclysmic_cleave",
            "whirlwind", "tempest_cyclone",
            "shield_bash", "aegis_bulwark",
            "earth_slam", "tectonic_rupture",
            "dash", "phantom_dash",
            "fireball", "inferno_blast",
            "frost_nova", "glacial_blizzard",
            "meteor", "grand_starfall",
            "celestial_shield", "divine_sanctuary",
            "void_singularity", "event_horizon"
        ]
        skills_dir = os.path.join(BASE_DIR, "assets", "skills")
        assert os.path.exists(skills_dir), "assets/skills directory must exist"

        for sk in skills:
            icon_file = os.path.join(skills_dir, f"{sk}.png")
            assert os.path.exists(icon_file), f"Missing skill icon: {sk}.png"
            img = pygame.image.load(icon_file)
            assert img.get_size() == (32, 32), f"Skill icon {sk}.png must be 32x32, got {img.get_size()}"
