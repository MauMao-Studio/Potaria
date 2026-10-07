"""
Potaria - Comprehensive Gameplay Systems & Reviewer Fixes Test Suite
Developer: Kurados
Engine: pygame-ce

Tests:
1. Workbench Strict Physical Proximity (2.5 tiles rule, real-time revocation, inventory non-unlock)
2. Demon Eye Spectral Ghost Flight (Phasing freely through solid blocks)
3. Anti-Cheese Mob AI (Wall detection, super leap, and ballistic projectile spit)
4. Melee Line-of-Sight Raycasting (Solid blocks block melee attacks, clear path connects)
5. Framedrop Optimizations (Column biome caching, light surface caching, particle cap, item cap)
6. Skill Upgrade Engine & Grand Legendary Skills (Levels 1-5, duplicate book consumption, balanced MP)
7. Mana Regeneration & Equipment Bonuses (1.5 MP/s base, magic gear MP regen)
8. Hotbar Active Weapon Dynamic Stat Sync (ATK, DEF, crit, speed applied to stats)
"""

import os
import sys
import math

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"

import pygame
from src.constants import (
    SCREEN_WIDTH, SCREEN_HEIGHT, SCALED_TILE,
    TILE_WORK_BENCH, TILE_FURNACE, TILE_STONE, TILE_AIR
)
from src.assets.asset_factory import AssetFactory
from src.audio.sound_effects import SoundManager
from src.world.world import World
from src.world.lighting import LightingEngine
from src.camera import Camera
from src.entities.player import Player
from src.entities.mob import Zombie, GreenSlime, DemonEye, DesertScorpion
from src.entities.particle import ParticleSystem
from src.entities.dropped_item import DroppedItem
from src.entities.projectile import MobSpitProjectile
from src.combat.combat_system import CombatManager, has_line_of_sight
from src.ui.inventory import Inventory, ItemStack, ITEM_REGISTRY
from src.ui.crafting import CraftingSystem
from src.rpg.skills import SkillManager, SKILL_DEFINITIONS
from src.rpg.stats import PlayerStats
from src.rpg.equipment import Equipment, ARMOR_DATA

def test_gameplay_and_reviewer_fixes():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    factory = AssetFactory()
    sounds = SoundManager()
    particles = ParticleSystem()
    cam = Camera(1280, 720)

    print("\n==================================================================")
    print("POTARIA GAMEPLAY SYSTEMS & REVIEWER FIXES VERIFICATION (Kurados)")
    print("==================================================================")

    # -----------------------------------------------------------------
    # Test 1: Workbench Strict Physical Proximity (2.5 tiles)
    # -----------------------------------------------------------------
    print("\n[Test 1] Testing Workbench Strict Physical Proximity (2.5 Tiles)...")
    world = World(factory, seed=12345)
    player = Player(100 * SCALED_TILE, 80 * SCALED_TILE, factory, sounds)
    crafting = CraftingSystem(factory, sounds)
    inv = Inventory(factory)
    inv.slots = [None] * len(inv.slots)

    ptx = int(player.center_x // SCALED_TILE)
    pty = int(player.center_y // SCALED_TILE)

    # 1a. No workbench nearby: has_workbench must be False
    has_wb, has_furn = crafting.check_nearby_stations(world, player)
    assert not has_wb, "No workbench should be detected when none placed"

    # 1b. Inventory presence alone does NOT unlock workbench recipes
    inv.add_item("work_bench", 1)
    crafting.update_recipes(inv, world, player)
    door_rec = next((r for r in crafting.available_recipes if r["result"] == "wooden_door"), None)
    assert door_rec is None, "Inventory presence of workbench must NOT unlock workbench recipes"

    # 1c. Place workbench at 2 tiles away (within 2.5 tiles) -> Unlocked!
    world.set_tile(ptx + 2, pty, TILE_WORK_BENCH)
    has_wb, _ = crafting.check_nearby_stations(world, player)
    assert has_wb, "Workbench at 2.0 tiles distance must be detected (<= 2.5 tiles)"
    crafting.update_recipes(inv, world, player)
    door_rec = next((r for r in crafting.available_recipes if r["result"] == "wooden_door"), None)
    assert door_rec is not None, "Workbench recipes must unlock within 2.5 tiles"

    # 1d. Move workbench to 3 tiles away (> 2.5 tiles) -> Locked!
    world.set_tile(ptx + 2, pty, TILE_AIR)
    world.set_tile(ptx + 3, pty, TILE_WORK_BENCH)
    has_wb, _ = crafting.check_nearby_stations(world, player)
    assert not has_wb, "Workbench at 3.0 tiles distance must NOT be detected (> 2.5 tiles)"
    crafting.update_recipes(inv, world, player)
    door_rec = next((r for r in crafting.available_recipes if r["result"] == "wooden_door"), None)
    assert door_rec is None, "Workbench recipes must NOT be accessible beyond 2.5 tiles"

    # 1e. Destroying workbench immediately revokes access
    world.set_tile(ptx + 1, pty, TILE_WORK_BENCH)
    crafting.update_recipes(inv, world, player)
    assert next((r for r in crafting.available_recipes if r["result"] == "wooden_door"), None) is not None
    # Destroy:
    world.set_tile(ptx + 1, pty, TILE_AIR)
    crafting.update_recipes(inv, world, player)
    assert next((r for r in crafting.available_recipes if r["result"] == "wooden_door"), None) is None, \
        "Destroying workbench must immediately revoke recipe access"
    print("  -> Workbench 2.5-tile proximity and real-time revocation OK.")

    # -----------------------------------------------------------------
    # Test 2: Demon Eye Spectral Phasing
    # -----------------------------------------------------------------
    print("\n[Test 2] Testing Demon Eye Spectral Flight (Phasing Through Solid Blocks)...")
    eye = DemonEye(100 * SCALED_TILE, 80 * SCALED_TILE, factory)
    # Surround eye with solid stone blocks
    for dx in range(-2, 3):
        for dy in range(-2, 3):
            world.set_tile(100 + dx, 80 + dy, TILE_STONE)
    
    # Eye has positive velocity moving through the wall
    eye.vx = 4.0
    eye.vy = 2.0
    initial_x = eye.x
    initial_y = eye.y
    eye.update(0.016, world, player)
    assert eye.x != initial_x and eye.y != initial_y, "Demon Eye must move freely through solid stone blocks without collision stop"
    # Clean up blocks
    for dx in range(-2, 3):
        for dy in range(-2, 3):
            world.set_tile(100 + dx, 80 + dy, TILE_AIR)
    print("  -> Demon Eye spectral phasing OK.")

    # -----------------------------------------------------------------
    # Test 3: Anti-Cheese Mob AI & Projectile Spitting
    # -----------------------------------------------------------------
    print("\n[Test 3] Testing Anti-Cheese Mob AI (Super-Leap & Spit Projectile)...")
    # Set flat solid ground at row 67, clear air above at rows 65 and 66
    for tx in range(48, 56):
        world.set_tile(tx, 67, TILE_STONE)
        world.set_tile(tx, 66, TILE_AIR)
        world.set_tile(tx, 65, TILE_AIR)
    # Place a 2-block tall solid wall right in front of zombie
    world.set_tile(51, 66, TILE_STONE)
    world.set_tile(51, 65, TILE_STONE)
    zombie = Zombie(50 * SCALED_TILE, (67 * SCALED_TILE) - 44, factory)
    player.x = 54 * SCALED_TILE
    player.y = (67 * SCALED_TILE) - 44
    
    # Zombie walks into wall and accumulates stuck_timer
    for _ in range(60): # Simulate ~1.0 second of stuck movement
        zombie.update(0.016, world, player)
    
    # Zombie must have triggered super-leap and spawned anti-cheese spit projectile
    assert len(zombie.pending_projectiles) > 0, "Obstructed zombie must spit anti-cheese projectile"
    spit = zombie.pending_projectiles[0]
    assert isinstance(spit, MobSpitProjectile), "Projectile must be MobSpitProjectile"
    assert spit.damage > 0, "Spit projectile must deal damage"
    
    # Test spit projectile physics and gravity arc
    initial_vy = spit.vel.y
    spit.update(0.05, world)
    assert spit.vel.y > initial_vy, "MobSpitProjectile must experience gravity acceleration"
    print("  -> Anti-cheese mob AI super-leap & projectile spit OK.")

    # -----------------------------------------------------------------
    # Test 4: Melee Line-of-Sight Raycast
    # -----------------------------------------------------------------
    print("\n[Test 4] Testing Melee Line-of-Sight Check...")
    combat = CombatManager(factory, sounds, particles, cam)
    
    # 4a. Clear line of sight
    p_x, p_y = 60 * SCALED_TILE, 70 * SCALED_TILE
    m_x, m_y = 61 * SCALED_TILE, 70 * SCALED_TILE
    world.set_tile(60, 70, TILE_AIR)
    world.set_tile(61, 70, TILE_AIR)
    assert has_line_of_sight(world, p_x, p_y, m_x, m_y), "Open air must have line of sight"
    
    # 4b. Obstructed by solid block
    world.set_tile(60, 70, TILE_STONE)
    assert not has_line_of_sight(world, p_x - 10, p_y + 10, p_x + 40, p_y + 10), \
        "Solid stone tile must block line of sight"
    # Short-distance raycast (<24px) across intermediate solid tile
    assert not has_line_of_sight(world, p_x - 6, p_y + 10, p_x + 10, p_y + 10), \
        "Short-distance raycast across solid tile must block line of sight"
    world.set_tile(60, 70, TILE_AIR)

    # 4c. Weapon swing hitting mob through wall must deal NO damage
    player.x = 60 * SCALED_TILE
    player.y = 70 * SCALED_TILE
    player.aim_angle = 0.0 # Aiming right
    player.is_swinging = True
    player.swing_progress = 0.3
    
    target_mob = Zombie(61 * SCALED_TILE, 70 * SCALED_TILE, factory)
    combat.mobs = [target_mob]
    initial_mob_hp = target_mob.hp
    
    # Place solid stone wall between player and mob
    world.set_tile(60, 70, TILE_STONE)
    combat._check_weapon_hits(player, world)
    assert target_mob.hp == initial_mob_hp, "Mob behind solid wall must take NO damage from melee swings"
    
    # Remove wall: swing must now hit!
    world.set_tile(60, 70, TILE_AIR)
    target_mob.hurt_timer = 0.0
    combat._check_weapon_hits(player, world)
    assert target_mob.hp < initial_mob_hp, "Mob with clear line of sight must take melee damage"
    print("  -> Melee line-of-sight raycasting OK.")

    # -----------------------------------------------------------------
    # Test 5: Framedrop Optimizations & Caps
    # -----------------------------------------------------------------
    print("\n[Test 5] Testing Framedrop Optimizations & Caps...")
    # 5a. Column biomes pre-cached on chunk
    chunk = world.chunk_manager.get_chunk(0)
    assert hasattr(chunk, "col_biomes"), "Chunk must pre-cache col_biomes"
    assert len(chunk.col_biomes) == 16, "Chunk col_biomes must match chunk width"
    col_b = world.chunk_manager.get_column_biome(0)
    assert col_b in ("forest", "desert", "snow", "corruption"), f"Valid biome string expected, got {col_b}"

    # 5b. Particle cap enforced at 250
    p_sys = ParticleSystem(max_particles=250)
    for _ in range(50):
        p_sys.spawn_debris(0, 0, (255, 0, 0), count=10)
    assert len(p_sys.particles) <= 250, f"Particles must be capped at 250 (current: {len(p_sys.particles)})"

    # 5c. Dropped item cap and pruning
    combat.dropped_items.clear()
    for i in range(100):
        it = DroppedItem("copper_ore", 1, 0, 0, factory)
        it.age = 200.0 # Older than 180s
        combat.dropped_items.append(it)
    # Add 10 fresh items
    for i in range(10):
        it = DroppedItem("iron_ore", 1, player.center_x + 50, player.center_y + 50, factory)
        it.age = 1.0
        combat.dropped_items.append(it)
    combat.update(0.016, world, player, is_night=False)
    assert len(combat.dropped_items) <= 64, f"Dropped items must be capped at 64 (current: {len(combat.dropped_items)})"
    # Old items (>180s) must have been pruned
    assert all(it.age < 180.0 for it in combat.dropped_items), "Items older than 180s must be pruned"

    # 5d. Lighting smoothscale caching
    lighting = LightingEngine(1280, 720)
    lighting.compute_viewport_light(world, 0, 0, 20, 20)
    surf1 = pygame.Surface((1280, 720))
    lighting.render_lighting(surf1, 0, 0)
    cached_surf = lighting.cached_smooth_light
    assert cached_surf is not None, "Lighting engine must cache smoothscale surface"
    # Calling render_lighting again without compute_viewport_light should reuse cached surface
    lighting.render_lighting(surf1, 0, 0)
    assert lighting.cached_smooth_light is cached_surf, "Lighting engine must reuse cached surface when clean"
    print("  -> Framedrop optimizations, biome caching, particle/item caps OK.")

    # -----------------------------------------------------------------
    # Test 6: Skill Upgrade System & Grand Legendary Skills
    # -----------------------------------------------------------------
    print("\n[Test 6] Testing Skill Upgrades (Lv. 1-5) & Grand Legendary Skills...")
    skills = SkillManager()
    stats = PlayerStats()

    # Initial level
    assert skills.get_skill_level("power_slash") == 1
    assert skills.get_skill_mp_cost("power_slash") == 8, "Power Slash Lv. 1 must cost exactly 8 MP"
    base_cd = skills.get_skill_cooldown("power_slash")
    base_dmg = skills.get_skill_dmg_mult("power_slash")

    # Upgrade to Lv. 2 via duplicate book
    upgraded = skills.learn_skill("power_slash")
    assert upgraded, "Learning duplicate skill book must upgrade skill level"
    assert skills.get_skill_level("power_slash") == 2
    assert skills.get_skill_dmg_mult("power_slash") > base_dmg, "Upgraded skill must deal higher damage"
    assert skills.get_skill_cooldown("power_slash") <= base_cd, "Upgraded skill cooldown must decrease or stay <= base"

    # Upgrade to Max Lv. 5
    for _ in range(10):
        skills.learn_skill("power_slash")
    assert skills.get_skill_level("power_slash") == 5, "Skill level must cap at max level (5)"
    assert not skills.learn_skill("power_slash"), "Learning beyond Lv. 5 must return False"

    # Grand Legendary Skills
    assert "meteor" in SKILL_DEFINITIONS
    assert "celestial_shield" in SKILL_DEFINITIONS
    assert "void_singularity" in SKILL_DEFINITIONS
    assert SKILL_DEFINITIONS["meteor"].get("legendary", False)
    assert SKILL_DEFINITIONS["meteor"]["mp_cost"] >= 35, "Grand skills must have high MP cost"
    assert SKILL_DEFINITIONS["meteor"]["cooldown"] >= 10.0, "Grand skills must have long cooldown"
    assert "skillbook_void_singularity" in ITEM_REGISTRY, "skillbook_void_singularity must be in ITEM_REGISTRY"
    print("  -> Skill upgrade scaling (Lv. 1-5) & Grand Legendary skills OK.")

    # -----------------------------------------------------------------
    # Test 7: Mana Regeneration & Equipment Bonuses
    # -----------------------------------------------------------------
    print("\n[Test 7] Testing Mana Regeneration (1.5 MP/s Base & Gear Bonuses)...")
    stats = PlayerStats()
    stats.mp = 10.0
    assert stats.base_mp_regen == 1.5, f"Base mana regen must be 1.5 MP/s, got {stats.base_mp_regen}"
    
    # 2 seconds of update with base regen (1.5 MP/s * 2s = +3 MP): 10 + 3 = 13
    stats.update(2.0)
    assert stats.mp == 13, f"MP after 2s base regen (1.5 MP/s) should be 13, got {stats.mp}"

    # Equipping magic accessories increases mana regen
    equipment = Equipment()
    equipment.equip("mana_flower", stats) # +2.5 MP/s
    assert stats.bonus_mp_regen == 2.5, f"Mana flower should add +2.5 MP/s regen, got {stats.bonus_mp_regen}"
    assert stats.total_mp_regen == 4.0, f"Total MP regen should be 4.0 MP/s, got {stats.total_mp_regen}"

    # 1 second with gear (4.0 MP/s * 1s = +4 MP): 13 + 4 = 17
    stats.update(1.0)
    assert stats.mp == 17, f"MP after 1s boosted regen should be 17, got {stats.mp}"
    print("  -> Mana regeneration & gear bonus scaling OK.")

    # -----------------------------------------------------------------
    # Test 8: Hotbar Active Weapon Dynamic Stat Sync
    # -----------------------------------------------------------------
    print("\n[Test 8] Testing Active Hotbar Weapon Dynamic Stat Sync...")
    p_stats = PlayerStats()
    eq = Equipment()
    base_atk = p_stats.total_atk
    
    # When holding iron broadsword in active slot
    eq.recalculate_stats(p_stats, active_item_id="iron_broadsword")
    assert p_stats.total_atk > base_atk, "Holding weapon in hotbar must increase total ATK"
    assert p_stats.bonus_atk == 18, f"Iron broadsword should provide +18 ATK, got {p_stats.bonus_atk}"

    # When switching to empty hand or tool
    eq.recalculate_stats(p_stats, active_item_id=None)
    assert p_stats.bonus_atk == 0, "Empty hand should clear weapon bonus ATK"
    assert p_stats.total_atk == base_atk
    print("  -> Hotbar active weapon dynamic stat sync OK.")

    print("\n==================================================================")
    print("ALL GAMEPLAY & REVIEWER FIXES TESTS PASSED SUCCESSFULLY! (Kurados)")
    print("==================================================================")

if __name__ == "__main__":
    test_gameplay_and_reviewer_fixes()
