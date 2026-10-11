"""
Potaria - Combat Engine & Mob Spawner (RPG Integrated)
Damage scaling with Player ATK, Defense mitigation, Critical hits,
EXP gain, Level-Up notifications, Skill Book loot drops, and Lord Malus!
Developer: Kurados
"""

import math
import random
import pygame
from src.constants import (
    SCALED_TILE, BIOME_FOREST, BIOME_DESERT, BIOME_SNOW,
    BIOME_CORRUPTION, BIOME_MUSHROOM, BIOME_DUNGEON, BIOME_CAVERN,
    WALL_WOOD, WALL_STONE_BRICK, WALL_GLASS, TILE_TORCH,
    PLAYER_WIDTH, PLAYER_HEIGHT
)
from src.world.chunk_manager import CHUNK_WIDTH
from src.entities.mob import (
    GreenSlime, PurpleSlime, SandSlime, FrostSlime, CorruptSlime,
    Zombie, IceZombie, Mummy, Skeleton, DemonEye, CaveBat, IceBat,
    DesertScorpion, ShadowCrawler, RockZombie, ShieldWeaver, DiggerMob
)
from src.entities.boss import (
    LordMalus, IgnisColossus, CryoSpud, NecroTuber,
    GrandBossSolRho, DungeonMiniBoss
)
from src.entities.dropped_item import DroppedItem
from src.entities.projectile import (
    ArrowProjectile, CelestialStarProjectile,
    FreezingNeedleProjectile, AstralArrowProjectile,
    SolarFlareShockwave, GravitationalPulseProjectile,
    MobSpitProjectile, CatalystStarProjectile,
    StaffBoltProjectile, RodJavelinProjectile,
    ScepterPulseProjectile
)

class DamageNumber:
    def __init__(self, world_x, world_y, amount, color=(255, 200, 50), is_crit=False):
        self.x = float(world_x)
        self.y = float(world_y)
        self.amount = amount
        self.color = (255, 230, 40) if is_crit else color
        self.is_crit = is_crit
        self.vx = random.uniform(-0.8, 0.8)
        self.vy = -2.6 if is_crit else -2.2
        self.life = 0.75 if is_crit else 0.65
        self.max_life = self.life

    def update(self, dt):
        self.life -= dt
        self.vy += 0.08
        self.x += self.vx
        self.y += self.vy

    def render(self, target_surf, camera, font, font_crit=None):
        if self.life <= 0:
            return
        if font_crit is None:
            font_crit = font
        sx, sy = camera.world_to_screen(self.x, self.y)
        txt = f"{self.amount}!" if self.is_crit else str(self.amount)
        f = font_crit if self.is_crit else font

        shadow = f.render(txt, True, (0, 0, 0))
        target_surf.blit(shadow, (sx + 1, sy + 1))
        num_surf = f.render(txt, True, self.color)
        target_surf.blit(num_surf, (sx, sy))

def has_line_of_sight(world, x1, y1, x2, y2):
    """Enforces line-of-sight raycast through solid blocks to prevent mob wall-farming cheese."""
    if world is None:
        return True
    dist = math.hypot(x2 - x1, y2 - y1)
    if dist <= 0:
        return True
    step_count = max(2, int(math.ceil(dist / 6.0)))
    for i in range(1, step_count):
        t = i / float(step_count)
        sx = x1 + (x2 - x1) * t
        sy = y1 + (y2 - y1) * t
        tx = int(sx // SCALED_TILE)
        ty = int(sy // SCALED_TILE)
        if hasattr(world, "is_tile_solid") and world.is_tile_solid(tx, ty):
            return False
    return True

class CombatManager:
    def __init__(self, asset_factory, sound_manager, particle_system, camera):
        self.asset_factory = asset_factory
        self.sound_manager = sound_manager
        self.particle_system = particle_system
        self.camera = camera
        
        self.mobs = []
        self.projectiles = []
        self.enemy_projectiles = []
        self.damage_numbers = []
        self.show_damage_numbers = True
        self.dropped_items = []
        self.boss = None
        self.secondary_boss = None
        self.boss_defeated = False
        self.grand_boss_defeated = False
        self.dungeon_boss_slain = False
        self.mini_bosses_slain = 0
        self.last_slain_mob = None
        self.defeated_mini_bosses = {
            "lord_malus": False,
            "ignis_colossus": False,
            "cryo_spud": False,
            "necro_tuber": False,
        }
        self.rematch_cycle = 0
        self.rematch_multiplier = 1.0
        
        self.mob_spawn_timer = 0.0
        self.max_mobs = 12
        self.nightly_elite_spawned = False
        self.ancient_drop_banner = None

        self.arrow_sprite = self.asset_factory.projectiles.get("wooden_arrow", self.asset_factory.items.get("wooden_arrow"))
        self.flame_arrow_sprite = self.asset_factory.projectiles.get("flame_arrow", self.asset_factory.items.get("flame_arrow", self.arrow_sprite))
        self.frostburn_arrow_sprite = self.asset_factory.projectiles.get("frostburn_arrow", self.asset_factory.items.get("frostburn_arrow", self.arrow_sprite))
        self.astral_arrow_sprite = self.asset_factory.projectiles.get("astral_arrow", self.asset_factory.items.get("astral_arrow", self.arrow_sprite))
        self.star_sprite = self.asset_factory.items.get("celestial_star")

        self.is_client = False
        self.client = None
        self.next_mob_id = 1
        self.multiplayer_player_positions = []

        from src.ui.theme import font_bold
        self.font = font_bold(14)
        self.font_crit = font_bold(18)

        self._catalog_rarity_pools = {
            "common": [], "uncommon": [], "rare": [], "epic": [],
            "mythic": [], "legendary": [], "ancient": []
        }
        try:
            from src.ui.inventory import ITEM_REGISTRY
            for iid, idata in ITEM_REGISTRY.items():
                r = idata.get("rarity")
                if r in self._catalog_rarity_pools and idata.get("cat") in ("weapon", "armor_head", "armor_chest", "armor_legs", "accessory"):
                    self._catalog_rarity_pools[r].append(iid)
        except Exception:
            pass

    def spawn_projectile(self, proj):
        """Spawns an active ballistic arrow or celestial star projectile."""
        self.projectiles.append(proj)

    def spawn_boss(self, dungeon_x, dungeon_y, boss_cls=None, player=None):
        """Spawns an underground mini-boss (random or specified class/name) with power scaling."""
        if not self.boss or self.boss.is_dead:
            mapping = {
                "lord_malus": LordMalus,
                "ignis_colossus": IgnisColossus,
                "cryo_spud": CryoSpud,
                "necro_tuber": NecroTuber,
            }
            if isinstance(boss_cls, str) and boss_cls in mapping:
                boss_cls = mapping[boss_cls]
            if boss_cls is None:
                boss_cls = random.choice([LordMalus, IgnisColossus, CryoSpud, NecroTuber])
            self.boss = boss_cls(dungeon_x, dungeon_y - 120, self.asset_factory, self.sound_manager)
            self.boss.boss_type = getattr(self.boss, "boss_type", "lord_malus")
            if player and hasattr(player, "stats") and hasattr(self.boss, "scale_to_player"):
                self.boss.scale_to_player(player.stats.level, getattr(player.stats, "total_atk", 0), rematch_multiplier=self.rematch_multiplier)
            print(f"[Combat] Subterranean Mini-Boss Awakened: {self.boss.name}!")
            self.sound_manager.play("hurt")
            if hasattr(self.sound_manager, "play_voice"):
                self.sound_manager.play_voice("titan", volume=0.85)
            if self.camera:
                self.camera.add_shake(8.0, 0.5)

    def spawn_grand_boss(self, x, y, party_size=1, player=None):
        """Summons the Grand Boss SOL-RHO THE CELESTIAL TITAN (Souls-like 2-phase battle!) with scaling."""
        if not self.boss or self.boss.is_dead:
            print("[Combat] SOL-RHO THE CELESTIAL TITAN HAS DESCENDED FROM THE HEAVENS!")
            base_p1 = 1000 if player is None else 14000
            base_p2 = 1400 if player is None else 20000
            self.boss = GrandBossSolRho(x, y - 140, self.asset_factory, self.sound_manager, party_size=party_size, base_p1_hp=base_p1, base_p2_hp=base_p2)
            self.boss.boss_type = "grand_boss_sol_rho"
            if player and hasattr(player, "stats") and hasattr(self.boss, "scale_to_player"):
                self.boss.scale_to_player(player.stats.level, getattr(player.stats, "total_atk", 0), rematch_multiplier=self.rematch_multiplier)
            if self.rematch_cycle >= 1 and not self.secondary_boss:
                from src.entities.boss import LordMalus, IgnisColossus, CryoSpud, NecroTuber
                miniboss_choices = [LordMalus, IgnisColossus, CryoSpud, NecroTuber]
                sub_cls = miniboss_choices[(self.rematch_cycle - 1) % len(miniboss_choices)]
                self.secondary_boss = sub_cls(x - 180, y, self.asset_factory, self.sound_manager)
                if player and hasattr(player, "stats") and hasattr(self.secondary_boss, "scale_to_player"):
                    self.secondary_boss.scale_to_player(player.stats.level, getattr(player.stats, "total_atk", 0), rematch_multiplier=self.rematch_multiplier)
                print(f"[Combat] REMATCH CYCLE {self.rematch_cycle}: DUO-BOSS SUMMONED! {self.secondary_boss.name} aids Sol-Rho!")
            self.sound_manager.play("craft")
            if hasattr(self.sound_manager, "play_voice"):
                self.sound_manager.play_voice("sol_rho", volume=0.95)
            if self.camera:
                self.camera.add_shake(16.0, 1.0)

    # Alias for underground mini-boss summoning
    spawn_mini_boss = spawn_boss

    def spawn_mob(self, mob, player=None):
        if getattr(mob, "mob_id", None) is None:
            mob.mob_id = self.next_mob_id
            self.next_mob_id += 1
        if getattr(mob, "mob_type", None) is None:
            from src.entities.mob import CLASS_TO_MOB_TYPE
            mob.mob_type = CLASS_TO_MOB_TYPE.get(mob.__class__, "green_slime")
        if player and hasattr(player, "stats") and hasattr(mob, "scale_to_player"):
            mob.scale_to_player(player.stats.level, getattr(player.stats, "total_atk", 0))
        self.mobs.append(mob)

    def spawn_damage_number(self, world_x, world_y, amount, color=(255, 210, 50), is_crit=False):
        if not getattr(self, "show_damage_numbers", True):
            return
        self.damage_numbers.append(DamageNumber(world_x, world_y, amount, color, is_crit))

    def _on_mob_slain(self, mob, player):
        """Unified reward & passive trigger hook when any mob is slain."""
        if not mob:
            return
        self.last_slain_mob = mob
        self.particle_system.spawn_sparks(mob.center_x, mob.center_y, (100, 255, 100), 12)
        if hasattr(player, "has_effect") and player.has_effect("soul harvest"):
            player.health = min(player.max_health, player.health + 5)
            self.particle_system.spawn_sparks(player.center_x, player.center_y, (100, 255, 140), count=6)
        base_hp = getattr(mob, "base_max_hp", getattr(mob, "max_hp", 30))
        mob_lvl = getattr(mob, "level", 1)
        exp_reward = max(15, int(base_hp * 0.8 + (mob_lvl - 1) * 6))
        leveled = player.stats.add_exp(exp_reward)
        if leveled:
            self.sound_manager.play("craft")
            self.particle_system.spawn_sparks(player.center_x, player.center_y, (255, 240, 100), count=25)
        self._drop_mob_loot(mob, tuned=True)

    def update(self, dt, world, player, is_night=False, time_of_day=None):
        if time_of_day is None:
            if isinstance(is_night, (int, float)) and not isinstance(is_night, bool):
                time_of_day = float(is_night)
                is_night = (time_of_day >= 0.5)
            elif hasattr(world, "time_of_day"):
                time_of_day = world.time_of_day
            else:
                time_of_day = 0.75 if is_night else 0.25

        if self.ancient_drop_banner:
            self.ancient_drop_banner["timer"] -= dt
            if self.ancient_drop_banner["timer"] <= 0:
                self.ancient_drop_banner = None

        # Maintain player in_boss_fight state
        player.in_boss_fight = bool(self.boss or self.secondary_boss)
        if player.is_dead and (self.boss or self.secondary_boss):
            player.killed_by_boss = True
            self.boss = None
            self.secondary_boss = None

        # 1. Update Boss
        if self.boss:
            # If arena boss is distant (>=2000 tiles) but player is in main world (<2000 tiles), despawn arena boss so it doesn't block Lord Malus
            if abs(self.boss.center_x) >= 2000 * SCALED_TILE and abs(player.center_x) < 2000 * SCALED_TILE:
                self.boss = None
                return
            if hasattr(self.boss, "update_dots"):
                self.boss.update_dots(dt)
            if self.is_client:
                # Client: update timers, animation, and smooth towards host position (no local autonomous AI)
                if self.boss.hurt_timer > 0:
                    self.boss.hurt_timer -= dt
                if hasattr(self.boss, "anim_timer"):
                    self.boss.anim_timer += dt
                    if self.boss.anim_timer >= 0.18:
                        self.boss.anim_timer = 0.0
                        frames_list = getattr(self.boss, "frames", None)
                        if not frames_list:
                            frames_list = getattr(self.boss, "p1_frames" if getattr(self.boss, "phase", 1) == 1 else "p2_frames", [])
                        if frames_list and len(frames_list) > 0:
                            self.boss.frame_idx = (self.boss.frame_idx + 1) % len(frames_list)
                if hasattr(self.boss, "target_x") and hasattr(self.boss, "target_y"):
                    dist_b = math.hypot(self.boss.x - self.boss.target_x, self.boss.y - self.boss.target_y)
                    if dist_b > 120.0:
                        self.boss.x = self.boss.target_x
                        self.boss.y = self.boss.target_y
                    else:
                        self.boss.x = self.boss.x * 0.7 + self.boss.target_x * 0.3
                        self.boss.y = self.boss.y * 0.7 + self.boss.target_y * 0.3
                else:
                    self.boss.x += self.boss.vx * dt * 60
                    self.boss.y += self.boss.vy * dt * 60

                if hasattr(self.boss, "update_client_projectiles"):
                    self.boss.update_client_projectiles(dt, player, self.particle_system, self.camera, combat=self)
            else:
                self.boss.update(dt, world, player, self.particle_system, self.camera, combat=self)
            
            if not self.boss.is_dead and self.boss.rect.colliderect(player.rect):
                knock_dir = 1.0 if player.center_x > self.boss.center_x else -1.0
                damaged = player.take_damage(self.boss.damage, knockback_vx=knock_dir * 6.0, knockback_vy=-4.5)
                if damaged:
                    dmg_val = getattr(player, "last_damage_taken", self.boss.damage)
                    self.spawn_damage_number(player.center_x, player.y - 10, dmg_val, color=(255, 50, 50))
                    self.camera.add_shake(6.0, 0.3)

            if self.boss.is_dead:
                # Slaying Grand Boss Sol-Rho (Phase 2 defeated -> TRUE VICTORY!)
                if isinstance(self.boss, GrandBossSolRho):
                    self.grand_boss_defeated = True
                    self.trigger_victory = True
                    self.boss_defeated = True
                    self.particle_system.spawn_sparks(self.boss.center_x, self.boss.center_y, (255, 215, 0), count=70)
                    player.stats.add_exp(2500)
                    self.dropped_items.append(
                        DroppedItem("crown_of_potaria", 1, self.boss.center_x - 30, self.boss.center_y, self.asset_factory)
                    )
                    self.dropped_items.append(
                        DroppedItem("celestial_greatsword", 1, self.boss.center_x, self.boss.center_y, self.asset_factory)
                    )
                    self.dropped_items.append(
                        DroppedItem("titan_chestplate", 1, self.boss.center_x + 30, self.boss.center_y, self.asset_factory)
                    )
                    self.dropped_items.append(
                        DroppedItem("celestial_emblem", 1, self.boss.center_x - 15, self.boss.center_y - 20, self.asset_factory)
                    )
                    self.dropped_items.append(
                        DroppedItem("celestial_essence", 3, self.boss.center_x + 15, self.boss.center_y - 20, self.asset_factory)
                    )
                    self.sound_manager.play("craft")
                    print("[Combat] TRUE VICTORY! Grand Boss Sol-Rho has been defeated!")

                    # Victory return: Player retains all items, teleports back to home / bed!
                    sp = getattr(player, "spawn_point", None) or getattr(world, "spawn_point", (0, 70 * SCALED_TILE))
                    player.x, player.y = sp
                    player.vx, player.vy = 0.0, 0.0
                    if self.camera:
                        self.camera.set_target(player.center_x, player.center_y, instant=True)

                    # Rematch Cycle increments & mini-boss stats double!
                    self.rematch_cycle += 1
                    self.rematch_multiplier = 2.0 ** self.rematch_cycle
                    for k in self.defeated_mini_bosses:
                        self.defeated_mini_bosses[k] = False
                    self.secondary_boss = None
                    self.boss = None
                    print(f"[Combat] Rematch Cycle {self.rematch_cycle} activated! Mini-boss stats doubled (x{self.rematch_multiplier:.1f})!")
                else:
                    # Slaying Dungeon Mini-Boss (Lord Malus, Ignis Colossus, Cryo-Spud, Necro-Tuber)
                    self.boss_defeated = True
                    self.mini_bosses_slain += 1
                    self.particle_system.spawn_sparks(self.boss.center_x, self.boss.center_y, (255, 230, 80), count=45)
                    player.stats.add_exp(400)
                    
                    # Mark mini-boss as slain in current cycle
                    b_type = getattr(self.boss, "boss_type", "lord_malus")
                    if b_type in self.defeated_mini_bosses:
                        self.defeated_mini_bosses[b_type] = True

                    # Mini-boss guaranteed drops: 1-2 Portal Shards + Royal Treasure Coins!
                    shards_count = random.randint(1, 2)
                    self.dropped_items.append(
                        DroppedItem("portal_shard", shards_count, self.boss.center_x, self.boss.center_y - 15, self.asset_factory)
                    )
                    self.dropped_items.append(
                        DroppedItem("silver_coin", random.randint(8, 18), self.boss.center_x + 15, self.boss.center_y - 10, self.asset_factory)
                    )
                    self.dropped_items.append(
                        DroppedItem("gold_coin", 1, self.boss.center_x - 15, self.boss.center_y - 10, self.asset_factory)
                    )
                    print(f"[Combat] Mini-Boss Slain! Dropped {shards_count} Celestial Portal Shards and Royal Coins!")
                    
                    # Boss-specific weapons & materials
                    b_name = getattr(self.boss, "name", "")
                    if "Ignis" in b_name:
                        self.dropped_items.append(DroppedItem("magma_greatsword", 1, self.boss.center_x - 25, self.boss.center_y, self.asset_factory))
                        self.dropped_items.append(DroppedItem("magma_core", 2, self.boss.center_x + 25, self.boss.center_y, self.asset_factory))
                    elif "Cryo" in b_name:
                        self.dropped_items.append(DroppedItem("frost_blade", 1, self.boss.center_x - 25, self.boss.center_y, self.asset_factory))
                        self.dropped_items.append(DroppedItem("frost_amulet", 1, self.boss.center_x + 25, self.boss.center_y, self.asset_factory))
                    elif "Necro" in b_name:
                        self.dropped_items.append(DroppedItem("bone_scythe", 1, self.boss.center_x - 25, self.boss.center_y, self.asset_factory))
                        self.dropped_items.append(DroppedItem("necro_essence", 2, self.boss.center_x + 25, self.boss.center_y, self.asset_factory))
                    else: # Lord Malus
                        self.dungeon_boss_slain = True
                        malus_loot = random.choice(["nether_cleaver", "crown_of_potaria"])
                        self.dropped_items.append(DroppedItem(malus_loot, 1, self.boss.center_x - 25, self.boss.center_y, self.asset_factory))

                    # Teleport Spud back to overworld if warped via Biome Rune
                    if hasattr(player, "pre_arena_pos") and player.pre_arena_pos:
                        px, py = player.pre_arena_pos
                        if hasattr(world, "chunk_manager"):
                            tcx = int(px // (CHUNK_WIDTH * SCALED_TILE))
                            world.chunk_manager.ensure_chunks_in_range(tcx - 2, tcx + 2)
                        player.x = px
                        player.y = py
                        player.vx = 0.0
                        player.vy = 0.0
                        player.pre_arena_pos = None
                        if self.camera:
                            self.camera.set_target(player.center_x, player.center_y, instant=True)
                        print("[Combat] Boss defeated! Teleporting Spud back to previous location!")

                    self.sound_manager.play("craft")
                    self.boss = None

                    # Check if all 4 biome mini-bosses have fallen!
                    all_mini_bosses_slain = all(self.defeated_mini_bosses.values())
                    if all_mini_bosses_slain:
                        print("[Combat] ALL 4 BIOME LORDS FALLEN! CELESTIAL PORTAL WARPS SPUD TO SKY CITADEL!")
                        if hasattr(world, "chunk_manager"):
                            world.chunk_manager.ensure_chunks_in_range(-3, 3)
                        player.x = 0.0
                        player.y = -165 * SCALED_TILE
                        player.vx = 0.0
                        player.vy = 0.0
                        if self.camera:
                            self.camera.set_target(player.center_x, player.center_y, instant=True)
                        self.spawn_grand_boss(0.0, -170 * SCALED_TILE, player=player)

                        # Rematch Duo Battle: If rematch cycle >= 1, summon one mini-boss alongside Sol-Rho!
                        if self.rematch_cycle >= 1:
                            from src.entities.boss import LordMalus, IgnisColossus, CryoSpud, NecroTuber
                            miniboss_choices = [LordMalus, IgnisColossus, CryoSpud, NecroTuber]
                            sub_cls = miniboss_choices[(self.rematch_cycle - 1) % len(miniboss_choices)]
                            self.secondary_boss = sub_cls(-180, -170 * SCALED_TILE, self.asset_factory, self.sound_manager)
                            if hasattr(self.secondary_boss, "scale_to_player"):
                                self.secondary_boss.scale_to_player(player.stats.level, getattr(player.stats, "total_atk", 0), rematch_multiplier=self.rematch_multiplier)
                            print(f"[Combat] REMATCH CYCLE {self.rematch_cycle}: DUO-BOSS SUMMONED! {self.secondary_boss.name} aids Sol-Rho!")
                    else:
                        remaining = [k.replace('_', ' ').title() for k, v in self.defeated_mini_bosses.items() if not v]
                        print(f"[Combat] Mini-Boss Slain! Remaining biome lords to defeat: {', '.join(remaining)}")

        # 1b. Update Secondary Boss (during rematch duo battles)
        if self.secondary_boss:
            if hasattr(self.secondary_boss, "update_dots"):
                self.secondary_boss.update_dots(dt)
            self.secondary_boss.update(dt, world, player, self.particle_system, self.camera, combat=self)
            if not self.secondary_boss.is_dead and self.secondary_boss.rect.colliderect(player.rect):
                knock_dir = 1.0 if player.center_x > self.secondary_boss.center_x else -1.0
                damaged = player.take_damage(self.secondary_boss.damage, knockback_vx=knock_dir * 6.0, knockback_vy=-4.5)
                if damaged:
                    dmg_val = getattr(player, "last_damage_taken", self.secondary_boss.damage)
                    self.spawn_damage_number(player.center_x, player.y - 10, dmg_val, color=(255, 50, 50))
                    self.camera.add_shake(6.0, 0.3)
            if self.secondary_boss.is_dead:
                self.particle_system.spawn_sparks(self.secondary_boss.center_x, self.secondary_boss.center_y, (255, 230, 80), count=45)
                player.stats.add_exp(500)
                print(f"[Combat] Secondary Boss {self.secondary_boss.name} slain in duo battle!")
                self.secondary_boss = None

        # Despawn distant mobs (>1300 pixels from any player) on Host / Singleplayer
        if not self.is_client:
            for mob in self.mobs:
                if getattr(self, "multiplayer_player_positions", None) and len(self.multiplayer_player_positions) > 0:
                    min_d = min(math.hypot(mob.center_x - px, mob.center_y - py) for px, py in self.multiplayer_player_positions)
                else:
                    min_d = math.hypot(mob.center_x - player.center_x, mob.center_y - player.center_y)
                if min_d > 1300.0:
                    mob.is_dead = True

        # 2. Update regular mobs
        if self.is_client:
            # Client: update positions towards sync targets, advance timers & animations
            for mob in self.mobs:
                if hasattr(mob, "target_x") and hasattr(mob, "target_y"):
                    dist_to_target = math.hypot(mob.x - mob.target_x, mob.y - mob.target_y)
                    if dist_to_target > 100.0:
                        mob.x = mob.target_x
                        mob.y = mob.target_y
                    else:
                        mob.x = mob.x * 0.7 + mob.target_x * 0.3
                        mob.y = mob.y * 0.7 + mob.target_y * 0.3
                else:
                    mob.x += mob.vx * dt * 60
                    mob.y += mob.vy * dt * 60
                if mob.hurt_timer > 0:
                    mob.hurt_timer -= dt
                if mob.hp_bar_timer > 0:
                    mob.hp_bar_timer -= dt
                # Advance animations for all mob types (Slimes, Bats, Walkers, Crawlers)
                if hasattr(mob, "anim_timer"):
                    mob.anim_timer += dt
                    if mob.anim_timer >= 1.0 / 12.0:
                        mob.anim_timer = 0.0
                        if hasattr(mob, "frame_idx") and hasattr(mob, "frames") and len(mob.frames) > 0:
                            mob.frame_idx = (mob.frame_idx + 1) % len(mob.frames)
                        if hasattr(mob, "anim_idx") and hasattr(mob, "frames") and len(mob.frames) > 0:
                            mob.anim_idx = (mob.anim_idx + 1) % len(mob.frames)
                if hasattr(mob, "walk_anim_timer"):
                    mob.walk_anim_timer += dt
                    if mob.walk_anim_timer >= 1.0 / 12.0:
                        mob.walk_anim_timer = 0.0
                        if hasattr(mob, "walk_idx") and hasattr(mob, "walk_frames") and len(mob.walk_frames) > 0:
                            mob.walk_idx = (mob.walk_idx + 1) % len(mob.walk_frames)
                if hasattr(mob, "update_dots"):
                    mob.update_dots(dt)

            # Prune dead mobs on client
            self.mobs = [m for m in self.mobs if not m.is_dead and m.hp > 0]
        else:
            # Host / Singleplayer: full authoritative physics & AI
            p_level = getattr(getattr(player, "stats", None), "level", 1)
            p_atk = getattr(getattr(player, "stats", None), "total_atk", 0)
            for mob in self.mobs:
                if hasattr(mob, "scale_to_player") and getattr(mob, "level", 1) < p_level:
                    mob.scale_to_player(p_level, p_atk)
                if hasattr(mob, "pending_projectiles") and mob.pending_projectiles:
                    self.enemy_projectiles.extend(mob.pending_projectiles)
                    mob.pending_projectiles.clear()
                
                # Dynamic targeting of nearest player across multiplayer party
                target_p = player
                if getattr(self, "multiplayer_player_positions", None) and len(self.multiplayer_player_positions) > 1:
                    best_d = math.hypot(mob.center_x - player.center_x, mob.center_y - player.center_y)
                    best_target = player
                    for (px, py) in self.multiplayer_player_positions:
                        d = math.hypot(mob.center_x - px, mob.center_y - py)
                        if d < best_d:
                            best_d = d
                            class _TargetProxy:
                                def __init__(self, tx, ty):
                                    self.center_x = tx
                                    self.center_y = ty
                                    self.rect = pygame.Rect(int(tx - PLAYER_WIDTH / 2), int(ty - PLAYER_HEIGHT / 2), PLAYER_WIDTH, PLAYER_HEIGHT)
                            best_target = _TargetProxy(px, py)
                    target_p = best_target

                mob.update(dt, world, target_p)
                if hasattr(mob, "update_dots"):
                    mob.update_dots(dt)
                if hasattr(mob, "pending_projectiles") and mob.pending_projectiles:
                    self.enemy_projectiles.extend(mob.pending_projectiles)
                    mob.pending_projectiles.clear()
                if mob.is_dead:
                    if getattr(self, "multiplayer_player_positions", None) and len(self.multiplayer_player_positions) > 0:
                        min_d = min(math.hypot(mob.center_x - px, mob.center_y - py) for px, py in self.multiplayer_player_positions)
                    else:
                        min_d = math.hypot(mob.center_x - player.center_x, mob.center_y - player.center_y)
                    if min_d <= 1250.0:
                        self._on_mob_slain(mob, player)

            self.mobs = [m for m in self.mobs if not m.is_dead and m.hp > 0]

        # 3. Check Player Weapon Swing Hitbox vs Mobs & Boss (with Line of Sight)
        if player.is_swinging and player.swing_progress < 0.65:
            self._check_weapon_hits(player, world)

        # 4. Check Player Fireballs hitting Mobs & Boss
        for fb in player.fireballs:
            if getattr(fb, "life", 0) <= 0:
                continue
            is_ancient_fb = getattr(fb, "is_ancient", False)
            for mob in self.mobs:
                if mob.is_alive and fb.rect.colliderect(mob.rect):
                    if hasattr(fb, "hit_entities") and mob in fb.hit_entities:
                        continue
                    if hasattr(fb, "hit_entities"):
                        fb.hit_entities.add(mob)
                    mob.take_damage(fb.damage, knockback_vx=fb.vx * 0.5, knockback_vy=-3.0)
                    if is_ancient_fb and hasattr(fb, "pierce_left"):
                        fb.pierce_left -= 1
                        if fb.pierce_left <= 0:
                            fb.life = 0
                    else:
                        fb.life = 0
                    self.sound_manager.play("hit_mob")
                    color = (120, 240, 255) if getattr(fb, "element", "") == "frost" or hasattr(fb, "pierce_left") else (255, 220, 80) if hasattr(fb, "rotation") else (255, 120, 40)
                    self.spawn_damage_number(mob.center_x, mob.y - 10, fb.damage, color=color)
                    self.particle_system.spawn_sparks(mob.center_x, mob.center_y, color, count=10)
                    if self.is_client and self.client and self.client.connected:
                        self.client.send_mob_damage(getattr(mob, "mob_id", 0), fb.damage, fb.vx * 0.5, -3.0)
                    if mob.is_dead:
                        self._on_mob_slain(mob, player)
                    if fb.life <= 0:
                        break
            if self.boss and not self.boss.is_dead and fb.life > 0 and fb.rect.colliderect(self.boss.rect):
                if hasattr(fb, "hit_entities") and self.boss in fb.hit_entities:
                    pass
                else:
                    if hasattr(fb, "hit_entities"):
                        fb.hit_entities.add(self.boss)
                    self.boss.take_damage(fb.damage, knockback_vx=fb.vx * 0.2)
                    if is_ancient_fb and hasattr(fb, "pierce_left"):
                        fb.pierce_left -= 1
                        if fb.pierce_left <= 0:
                            fb.life = 0
                    else:
                        fb.life = 0
                    self.sound_manager.play("hit_mob")
                    color = (120, 240, 255) if getattr(fb, "element", "") == "frost" or hasattr(fb, "pierce_left") else (255, 220, 80) if hasattr(fb, "rotation") else (255, 120, 40)
                    self.spawn_damage_number(self.boss.center_x, self.boss.y - 10, fb.damage, color=color)
                    self.particle_system.spawn_sparks(self.boss.center_x, self.boss.center_y, color, count=10)
                    if self.is_client and self.client and self.client.connected:
                        self.client.send_mob_damage("boss", fb.damage, fb.vx * 0.2, 0.0)

        # 4b. Update Projectiles (Arrows, Falling Stars, Freezing Needles, Shockwaves, etc.)
        for p in self.projectiles:
            if isinstance(p, ArrowProjectile):
                p.update(dt, world, self.particle_system, self.sound_manager, player)
                if not p.stuck and p.life > 0:
                    for mob in self.mobs:
                        if mob.is_alive and p.frect.colliderect(mob.rect) and mob.hurt_timer <= 0:
                            if hasattr(p, "hit_entities") and mob in p.hit_entities:
                                continue
                            if not hasattr(p, "hit_entities"):
                                p.hit_entities = set()
                            p.hit_entities.add(mob)
                            is_crit = (random.uniform(0, 100) < player.stats.total_crit_rate)
                            dmg = int((p.damage + player.stats.bonus_atk) * (1.8 if is_crit else random.uniform(0.95, 1.15)))
                            if is_crit:
                                self.sound_manager.play_spatial("crit_hit", p.pos.x, p.pos.y, player.center_x, player.center_y)
                                self.particle_system.spawn_sparks(p.pos.x, p.pos.y, (255, 235, 60), count=16)
                            else:
                                self.sound_manager.play_spatial("hit_mob", p.pos.x, p.pos.y, player.center_x, player.center_y)
                                self.particle_system.spawn_sparks(p.pos.x, p.pos.y, (240, 220, 160), count=6)
                            self.spawn_damage_number(mob.center_x, mob.y - 12, dmg, color=(255, 230, 40) if is_crit else (255, 210, 80), is_crit=is_crit)
                            mob.take_damage(dmg, knockback_vx=p.vel.x * 0.35, knockback_vy=-2.5)

                            # Special arrow elemental effects on mob hit
                            arr_type = getattr(p, "arrow_type", "")
                            if arr_type == "frostburn_arrow":
                                if hasattr(mob, "speed_mult"):
                                    mob.speed_mult = 0.65
                                self.particle_system.spawn_sparks(p.pos.x, p.pos.y, (100, 220, 255), count=12)
                            elif "flame" in arr_type or "magma" in arr_type:
                                if hasattr(mob, "apply_burn"):
                                    mob.apply_burn(4.0, 5)
                                elif hasattr(mob, "burn_timer"):
                                    mob.burn_timer = 4.0
                                self.particle_system.spawn_sparks(p.pos.x, p.pos.y, (255, 130, 40), count=12)
                            elif "astral" in arr_type or "celestial" in arr_type:
                                self.particle_system.spawn_sparks(p.pos.x, p.pos.y, (255, 235, 70), count=14)

                            if self.is_client and self.client and self.client.connected:
                                self.client.send_mob_damage(getattr(mob, "mob_id", 0), dmg, p.vel.x * 0.35, -2.5, is_crit=is_crit)
                            if mob.is_dead:
                                self._on_mob_slain(mob, player)
                            if not getattr(p, "is_ancient", False):
                                p.life = 0
                                break
                            else:
                                if not hasattr(p, "pierce_left"):
                                    p.pierce_left = 4
                                p.pierce_left -= 1
                                if p.pierce_left <= 0:
                                    p.life = 0
                                    break
                    if p.life > 0 and self.boss and not self.boss.is_dead and p.frect.colliderect(self.boss.rect):
                        if hasattr(p, "hit_entities") and self.boss in p.hit_entities:
                            pass
                        else:
                            if not hasattr(p, "hit_entities"):
                                p.hit_entities = set()
                            p.hit_entities.add(self.boss)
                        is_crit = (random.uniform(0, 100) < player.stats.total_crit_rate)
                        dmg = int((p.damage + player.stats.bonus_atk) * (1.8 if is_crit else random.uniform(0.95, 1.15)))
                        self.boss.take_damage(dmg, knockback_vx=p.vel.x * 0.15)
                        if is_crit:
                            self.sound_manager.play_spatial("crit_hit", p.pos.x, p.pos.y, player.center_x, player.center_y)
                            self.particle_system.spawn_sparks(p.pos.x, p.pos.y, (255, 235, 60), count=16)
                        else:
                            self.sound_manager.play_spatial("hit_mob", p.pos.x, p.pos.y, player.center_x, player.center_y)
                            self.particle_system.spawn_sparks(p.pos.x, p.pos.y, (240, 220, 160), count=6)
                        
                        arr_type = getattr(p, "arrow_type", "")
                        if "flame" in arr_type or "magma" in arr_type:
                            if hasattr(self.boss, "apply_burn"):
                                self.boss.apply_burn(4.0, 8)
                            elif hasattr(self.boss, "burn_timer"):
                                self.boss.burn_timer = 4.0
                            self.particle_system.spawn_sparks(p.pos.x, p.pos.y, (255, 130, 40), count=12)
                        elif arr_type == "frostburn_arrow":
                            if hasattr(self.boss, "speed_mult"):
                                self.boss.speed_mult = 0.75
                            self.particle_system.spawn_sparks(p.pos.x, p.pos.y, (100, 220, 255), count=12)
                        elif "astral" in arr_type or "celestial" in arr_type:
                            self.particle_system.spawn_sparks(p.pos.x, p.pos.y, (255, 235, 70), count=14)

                        self.spawn_damage_number(self.boss.center_x, self.boss.y - 12, dmg, color=(255, 230, 40) if is_crit else (255, 210, 80), is_crit=is_crit)
                        if self.is_client and self.client and self.client.connected:
                            self.client.send_mob_damage("boss", dmg, p.vel.x * 0.15, 0.0, is_crit=is_crit)
                        p.life = 0

            elif isinstance(p, CelestialStarProjectile):
                prev_exploded = p.exploded
                p.update(dt, world, self.particle_system, self.sound_manager, self.camera, self.mobs, self.boss, player)
                if p.exploded and not prev_exploded:
                    is_ancient_star = getattr(p, "is_ancient", False)
                    if is_ancient_star:
                        for mob in self.mobs:
                            if mob.is_alive:
                                d = math.hypot(mob.center_x - p.pos.x, mob.center_y - p.pos.y)
                                if d <= 72.0:
                                    dmg = int(p.damage * (1.0 - (d / 72.0) * 0.4))
                                    self.spawn_damage_number(mob.center_x, mob.y - 16, dmg, color=(255, 240, 60), is_crit=True)
                                    if self.is_client and self.client and self.client.connected:
                                        self.client.send_mob_damage(getattr(mob, "mob_id", 0), dmg, 0.0, -2.0, is_crit=True)
                                    if mob.is_dead:
                                        self._on_mob_slain(mob, player)
                    else:
                        closest_mob = None
                        min_d = 72.0
                        for mob in self.mobs:
                            if mob.is_alive:
                                d = math.hypot(mob.center_x - p.pos.x, mob.center_y - p.pos.y)
                                if d <= min_d:
                                    min_d = d
                                    closest_mob = mob
                        if closest_mob:
                            dmg = int(p.damage * (1.0 - (min_d / 72.0) * 0.4))
                            self.spawn_damage_number(closest_mob.center_x, closest_mob.y - 16, dmg, color=(255, 240, 60), is_crit=True)
                            if self.is_client and self.client and self.client.connected:
                                self.client.send_mob_damage(getattr(closest_mob, "mob_id", 0), dmg, 0.0, -2.0, is_crit=True)
                            if closest_mob.is_dead:
                                self._on_mob_slain(closest_mob, player)
                    if self.boss and not self.boss.is_dead:
                        d = math.hypot(self.boss.center_x - p.pos.x, self.boss.center_y - p.pos.y)
                        if d <= 72.0:
                            self.spawn_damage_number(self.boss.center_x, self.boss.y - 16, p.damage, color=(255, 240, 60), is_crit=True)
                            if self.is_client and self.client and self.client.connected:
                                self.client.send_mob_damage("boss", p.damage, 0.0, 0.0, is_crit=True)

            elif isinstance(p, FreezingNeedleProjectile):
                p.update(dt, world, self.particle_system, self.sound_manager, self.mobs, self.boss, player, combat=self)
            elif isinstance(p, AstralArrowProjectile):
                p.update(dt, world, self.particle_system, self.sound_manager, self.mobs, self.boss, player, combat=self)
            elif isinstance(p, SolarFlareShockwave):
                p.update(dt, self.particle_system, self.sound_manager, self.mobs, self.boss, player, combat=self)
            elif isinstance(p, GravitationalPulseProjectile):
                p.update(dt, self.particle_system, self.sound_manager, self.mobs, self.boss, player, combat=self)
            elif isinstance(p, CatalystStarProjectile):
                p.update(dt, world, self.particle_system, mobs=self.mobs, boss=self.boss)
                if p.life > 0:
                    for mob in self.mobs:
                        if mob.is_alive and p.rect.colliderect(mob.rect):
                            is_crit = (random.uniform(0, 100) < player.stats.total_crit_rate)
                            dmg = int((p.damage + player.stats.bonus_atk) * (1.8 if is_crit else random.uniform(0.95, 1.15)))
                            mob.take_damage(dmg, knockback_vx=p.vx * 0.45, knockback_vy=-3.0)
                            self.spawn_damage_number(mob.center_x, mob.y - 12, dmg, color=(255, 230, 80) if is_crit else (255, 215, 60), is_crit=is_crit)
                            self.particle_system.spawn_sparks(p.x, p.y, (255, 225, 80), count=14)
                            self.sound_manager.play_spatial("hit_mob", p.x, p.y, player.center_x, player.center_y)
                            if self.is_client and self.client and self.client.connected:
                                self.client.send_mob_damage(getattr(mob, "mob_id", 0), dmg, p.vx * 0.45, -3.0, is_crit=is_crit)
                            if mob.is_dead:
                                self._on_mob_slain(mob, player)
                            p.life = 0
                            break
                    if p.life > 0 and self.boss and not self.boss.is_dead and p.rect.colliderect(self.boss.rect):
                        is_crit = (random.uniform(0, 100) < player.stats.total_crit_rate)
                        dmg = int((p.damage + player.stats.bonus_atk) * (1.8 if is_crit else random.uniform(0.95, 1.15)))
                        self.boss.take_damage(dmg, knockback_vx=p.vx * 0.2)
                        self.spawn_damage_number(self.boss.center_x, self.boss.y - 14, dmg, color=(255, 230, 80) if is_crit else (255, 215, 60), is_crit=is_crit)
                        self.particle_system.spawn_sparks(p.x, p.y, (255, 225, 80), count=16)
                        self.sound_manager.play_spatial("hit_mob", p.x, p.y, player.center_x, player.center_y)
                        if self.is_client and self.client and self.client.connected:
                            self.client.send_mob_damage("boss", dmg, p.vx * 0.2, 0.0, is_crit=is_crit)
                        p.life = 0
            elif isinstance(p, StaffBoltProjectile):
                p.update(dt, world, self.particle_system)
                if p.life > 0:
                    for mob in self.mobs:
                        if mob.is_alive and p.rect.colliderect(mob.rect):
                            is_crit = (random.uniform(0, 100) < player.stats.total_crit_rate)
                            dmg = int((p.damage + player.stats.bonus_atk) * (1.8 if is_crit else random.uniform(0.95, 1.15)))
                            mob.take_damage(dmg, knockback_vx=p.vx * 0.4, knockback_vy=-2.5)
                            if p.element == "frost" and hasattr(mob, "speed_mult"):
                                mob.speed_mult = 0.65
                            elif p.element == "fire" and hasattr(mob, "apply_burn"):
                                mob.apply_burn(4.0, 6)
                            col = (255, 140, 40) if p.element == "fire" else (100, 220, 255) if p.element == "frost" else (180, 100, 255)
                            self.spawn_damage_number(mob.center_x, mob.y - 12, dmg, color=col, is_crit=is_crit)
                            self.particle_system.spawn_sparks(p.x, p.y, col, count=12)
                            self.sound_manager.play_spatial("hit_mob", p.x, p.y, player.center_x, player.center_y)
                            if self.is_client and self.client and self.client.connected:
                                self.client.send_mob_damage(getattr(mob, "mob_id", 0), dmg, p.vx * 0.4, -2.5, is_crit=is_crit)
                            if mob.is_dead:
                                self._on_mob_slain(mob, player)
                            p.life = 0
                            break
                    if p.life > 0 and self.boss and not self.boss.is_dead and p.rect.colliderect(self.boss.rect):
                        is_crit = (random.uniform(0, 100) < player.stats.total_crit_rate)
                        dmg = int((p.damage + player.stats.bonus_atk) * (1.8 if is_crit else random.uniform(0.95, 1.15)))
                        self.boss.take_damage(dmg, knockback_vx=p.vx * 0.15)
                        col = (255, 140, 40) if p.element == "fire" else (100, 220, 255) if p.element == "frost" else (180, 100, 255)
                        self.spawn_damage_number(self.boss.center_x, self.boss.y - 14, dmg, color=col, is_crit=is_crit)
                        self.particle_system.spawn_sparks(p.x, p.y, col, count=14)
                        self.sound_manager.play_spatial("hit_mob", p.x, p.y, player.center_x, player.center_y)
                        if self.is_client and self.client and self.client.connected:
                            self.client.send_mob_damage("boss", dmg, p.vx * 0.15, 0.0, is_crit=is_crit)
                        p.life = 0
            elif isinstance(p, RodJavelinProjectile):
                p.update(dt, world, self.particle_system)
                if p.life > 0 and p.pierce_left > 0:
                    for mob in self.mobs:
                        if mob.is_alive and mob not in p.hit_entities and p.rect.colliderect(mob.rect):
                            p.hit_entities.add(mob)
                            p.pierce_left -= 1
                            is_crit = (random.uniform(0, 100) < player.stats.total_crit_rate)
                            dmg = int((p.damage + player.stats.bonus_atk) * (1.8 if is_crit else random.uniform(0.95, 1.15)))
                            mob.take_damage(dmg, knockback_vx=p.vx * 0.35, knockback_vy=-2.0)
                            self.spawn_damage_number(mob.center_x, mob.y - 12, dmg, color=(140, 230, 255), is_crit=is_crit)
                            self.particle_system.spawn_sparks(p.x, p.y, (120, 240, 255), count=12)
                            self.sound_manager.play_spatial("hit_mob", p.x, p.y, player.center_x, player.center_y)
                            if self.is_client and self.client and self.client.connected:
                                self.client.send_mob_damage(getattr(mob, "mob_id", 0), dmg, p.vx * 0.35, -2.0, is_crit=is_crit)
                            if mob.is_dead:
                                self._on_mob_slain(mob, player)
                            if not getattr(p, "is_ancient", False) or p.pierce_left <= 0:
                                p.life = 0
                                break
                    if p.pierce_left > 0 and self.boss and not self.boss.is_dead and self.boss not in p.hit_entities and p.rect.colliderect(self.boss.rect):
                        p.hit_entities.add(self.boss)
                        p.pierce_left -= 1
                        is_crit = (random.uniform(0, 100) < player.stats.total_crit_rate)
                        dmg = int((p.damage + player.stats.bonus_atk) * (1.8 if is_crit else random.uniform(0.95, 1.15)))
                        self.boss.take_damage(dmg, knockback_vx=p.vx * 0.15)
                        self.spawn_damage_number(self.boss.center_x, self.boss.y - 14, dmg, color=(140, 230, 255), is_crit=is_crit)
                        self.particle_system.spawn_sparks(p.x, p.y, (120, 240, 255), count=14)
                        self.sound_manager.play_spatial("hit_mob", p.x, p.y, player.center_x, player.center_y)
                        if self.is_client and self.client and self.client.connected:
                            self.client.send_mob_damage("boss", dmg, p.vx * 0.15, 0.0, is_crit=is_crit)
                        if p.pierce_left <= 0:
                            p.life = 0
            elif isinstance(p, ScepterPulseProjectile):
                p.update(dt, world, self.particle_system)
                if p.life > 0:
                    for mob in self.mobs:
                        if mob.is_alive and p.rect.colliderect(mob.rect):
                            is_crit = (random.uniform(0, 100) < player.stats.total_crit_rate)
                            dmg = int((p.damage + player.stats.bonus_atk) * (1.8 if is_crit else random.uniform(0.95, 1.15)))
                            mob.take_damage(dmg, knockback_vx=p.vx * 0.45, knockback_vy=-3.5)
                            self.spawn_damage_number(mob.center_x, mob.y - 12, dmg, color=(220, 140, 255), is_crit=is_crit)
                            self.particle_system.spawn_sparks(p.x, p.y, (210, 100, 255), count=15)
                            self.sound_manager.play_spatial("hit_mob", p.x, p.y, player.center_x, player.center_y)
                            if self.is_client and self.client and self.client.connected:
                                self.client.send_mob_damage(getattr(mob, "mob_id", 0), dmg, p.vx * 0.45, -3.5, is_crit=is_crit)
                            if mob.is_dead:
                                self._on_mob_slain(mob, player)
                            p.life = 0
                            break
                    if p.life > 0 and self.boss and not self.boss.is_dead and p.rect.colliderect(self.boss.rect):
                        is_crit = (random.uniform(0, 100) < player.stats.total_crit_rate)
                        dmg = int((p.damage + player.stats.bonus_atk) * (1.8 if is_crit else random.uniform(0.95, 1.15)))
                        self.boss.take_damage(dmg, knockback_vx=p.vx * 0.2)
                        self.spawn_damage_number(self.boss.center_x, self.boss.y - 14, dmg, color=(220, 140, 255), is_crit=is_crit)
                        self.particle_system.spawn_sparks(p.x, p.y, (210, 100, 255), count=16)
                        self.sound_manager.play_spatial("hit_mob", p.x, p.y, player.center_x, player.center_y)
                        if self.is_client and self.client and self.client.connected:
                            self.client.send_mob_damage("boss", dmg, p.vx * 0.2, 0.0, is_crit=is_crit)
                        p.life = 0


        self.projectiles = [p for p in self.projectiles if p.life > 0]
        if len(self.projectiles) > 50:
            self.projectiles = self.projectiles[-50:]

        # 4c. Update Enemy Projectiles (Spit attacks from obstructed mobs & Rocks)
        for ep in self.enemy_projectiles:
            ep.update(dt, world)

            # Celestial Aegis: Deflects / destroys enemy projectiles near player
            if ep.life > 0 and hasattr(player, "has_effect") and player.has_effect("celestial aegis"):
                if math.hypot(ep.pos.x - player.center_x, ep.pos.y - player.center_y) < 38.0:
                    ep.life = 0
                    self.sound_manager.play_spatial("hit_block", ep.pos.x, ep.pos.y, player.center_x, player.center_y)
                    self.particle_system.spawn_sparks(ep.pos.x, ep.pos.y, (100, 220, 255), count=12)
                    continue

            if ep.life > 0 and ep.rect.colliderect(player.rect):
                ep.life = 0
                knock_x = 4.0 if ep.vel.x > 0 else -4.0
                damaged = player.take_damage(ep.damage, knockback_vx=knock_x, knockback_vy=-3.0)
                if damaged:
                    dmg_val = getattr(player, "last_damage_taken", ep.damage)
                    self.spawn_damage_number(player.center_x, player.y - 10, dmg_val, color=(255, 60, 60))
                    self.sound_manager.play("hurt")
                    self.camera.add_shake(4.0, 0.2)
                    self.particle_system.spawn_sparks(player.center_x, player.center_y, (100, 220, 60), 8)
        self.enemy_projectiles = [ep for ep in self.enemy_projectiles if ep.life > 0]
        if len(self.enemy_projectiles) > 30:
            self.enemy_projectiles = self.enemy_projectiles[-30:]

        # 5. Check Mob Contact Damage to Player
        for mob in self.mobs:
            if mob.is_alive and mob.rect.colliderect(player.rect):
                knock_dir = 1.0 if player.center_x > mob.center_x else -1.0
                damaged = player.take_damage(mob.damage, knockback_vx=knock_dir * 4.5, knockback_vy=-3.5)
                if damaged:
                    dmg_val = getattr(player, "last_damage_taken", mob.damage)
                    self.spawn_damage_number(player.center_x, player.y - 10, dmg_val, color=(255, 50, 50))
                    self.camera.add_shake(5.0, 0.25)
                    self.particle_system.spawn_sparks(player.center_x, player.center_y, (255, 50, 50), 6)

        # 6. Update Damage Numbers
        for dn in self.damage_numbers:
            dn.update(dt)
        self.damage_numbers = [dn for dn in self.damage_numbers if dn.life > 0]
        if len(self.damage_numbers) > 40:
            self.damage_numbers = self.damage_numbers[-40:]

        # 7. Update Dropped Items (Pruning items >180s old or >1400px distant, cap to 64)
        has_magnetic = hasattr(player, "has_effect") and player.has_effect("magnetic aura")
        pickup_radius = 120.0 if has_magnetic else 30.0
        valid_items = []
        for item in self.dropped_items:
            # Check if player can pick up item (coins deposit into dedicated purse)
            is_coin = item.item_id in ("copper_coin", "silver_coin", "gold_coin")
            can_pickup = False
            if is_coin:
                can_pickup = True
            elif hasattr(player, "inventory") and player.inventory is not None:
                can_pickup = player.inventory.can_add_item(item.item_id, 1)

            # Magnetic aura pulls item towards player ONLY if player can accept it
            if can_pickup and has_magnetic and item.age > item.pickup_delay:
                dist_p = math.hypot(item.x - player.center_x, item.y - player.center_y)
                if dist_p < pickup_radius:
                    item.x = item.x * 0.88 + player.center_x * 0.12
                    item.y = item.y * 0.88 + player.center_y * 0.12

            item.update(dt, world, player)
            if item.rect.colliderect(player.rect) and item.age > item.pickup_delay:
                if not can_pickup:
                    pass
                else:
                    item.picked_up = True
                    self.sound_manager.play("pickup")
                    self.particle_system.spawn_sparks(item.x, item.y, (255, 230, 80), 5)
            d_player = math.hypot(item.x - player.center_x, item.y - player.center_y)
            if item.age < 180.0 and (item.age < 10.0 or d_player < 1400.0):
                valid_items.append(item)
        if len(valid_items) > 1:
            merged = []
            for item in valid_items:
                combined = False
                for existing in merged:
                    if existing.item_id == item.item_id and existing.count < 99:
                        if math.hypot(existing.x - item.x, existing.y - item.y) < 28.0:
                            transfer = min(item.count, 99 - existing.count)
                            existing.count += transfer
                            item.count -= transfer
                            if item.count <= 0:
                                combined = True
                                break
                if not combined:
                    merged.append(item)
            valid_items = merged
        if len(valid_items) > 64:
            valid_items = valid_items[-64:]
        self.dropped_items = valid_items

        # 8. Natural Mob Spawner around player (Host / Singleplayer only)
        if not self.is_client:
            # Nightly Elite Enemy ("Champion of the Night") - tracker resets at daytime
            if not is_night:
                self.nightly_elite_spawned = False

            if not self.boss:
                party_size = max(1, len(getattr(self, "multiplayer_player_positions", [])))
                # Diurnal spawn curve based on time_of_day:
                # Morning (0.00-0.22): Morning Peace on surface, slow subterranean interval
                # Midday (0.22-0.50): Gradual daylight spawns
                # Dusk (0.50-0.75): Twilight surge
                # Night (0.75-0.95): Peak midnight invasion
                # Dawn (0.95-1.00): Monsters subside
                tod = float(time_of_day) if time_of_day is not None else (0.75 if is_night else 0.25)
                if tod < 0.22:
                    base_cap = 4
                    base_interval = 8.0
                elif tod < 0.50:
                    base_cap = 8
                    base_interval = 4.8
                elif tod < 0.75:
                    base_cap = 14
                    base_interval = 3.0
                elif tod < 0.95:
                    base_cap = 22
                    base_interval = 1.8
                else:
                    base_cap = 6
                    base_interval = 5.5

                effective_max_mobs = min(40, base_cap * party_size)
                self.mob_spawn_timer += dt
                spawn_interval = base_interval / min(3.0, party_size)
                if self.mob_spawn_timer >= spawn_interval:
                    self.mob_spawn_timer = 0.0
                    if len(self.mobs) < effective_max_mobs:
                        self._spawn_natural_mob(world, player, is_night, tod)

                # Nightly Elite Enemy ("Champion of the Night") - spawns once per night on the surface
                if is_night and not self.nightly_elite_spawned:
                    player_ty = int(player.y // SCALED_TILE)
                    if player_ty < 115:  # Overworld surface
                        self._spawn_nightly_elite(world, player)

    def trigger_weapon_swing_effects(self, player, mouse_wx, mouse_wy, active_item=None):
        """Spawns projectiles and shockwaves for weapon swing effects."""
        effects = []
        if hasattr(player, "equipment") and hasattr(player.equipment, "get_all_active_effects"):
            effects.extend(player.equipment.get_all_active_effects())
        if active_item and hasattr(active_item, "data"):
            effects.extend(active_item.data.get("effects", []))

        is_ancient = False
        if active_item and hasattr(active_item, "data"):
            rarity = str(active_item.data.get("rarity", "")).lower()
            if rarity in ("ancient", "rarity_ancient") or "ancient" in getattr(active_item, "item_id", "").lower():
                is_ancient = True
        elif hasattr(player, "equipment") and hasattr(player.equipment, "slots"):
            eq_weap = player.equipment.slots.get("weapon")
            if eq_weap:
                from src.rpg.equipment import ARMOR_DATA
                eq_data = ARMOR_DATA.get(eq_weap, {})
                rarity = str(eq_data.get("rarity", "")).lower()
                if rarity in ("ancient", "rarity_ancient") or "ancient" in str(eq_weap).lower():
                    is_ancient = True

        angle = math.atan2(mouse_wy - player.center_y, mouse_wx - player.center_x)
        base_atk = player.stats.total_atk

        has_spawned_needle = False
        has_spawned_star = False
        has_spawned_astral = False
        has_spawned_solar = False
        has_spawned_grav = False

        for eff in effects:
            eff_l = eff.lower()
            if "freezing needles" in eff_l and not has_spawned_needle:
                has_spawned_needle = True
                needle_dmg = max(18, int(base_atk * 0.85))
                needle_proj = FreezingNeedleProjectile(player.center_x, player.center_y, angle, damage=needle_dmg, speed=16.0)
                needle_proj.is_ancient = is_ancient
                self.spawn_projectile(needle_proj)
                self.sound_manager.play_spatial("hit_block", player.center_x, player.center_y, player.center_x, player.center_y)

            if "celestial star on swing" in eff_l and not has_spawned_star:
                has_spawned_star = True
                star_dmg = max(35, int(base_atk * 1.2))
                star_proj = CelestialStarProjectile(mouse_wx, mouse_wy, self.camera.offset_y - 80, damage=star_dmg)
                star_proj.is_ancient = is_ancient
                self.spawn_projectile(star_proj)
                self.sound_manager.play_spatial("starfury", player.center_x, player.center_y, player.center_x, player.center_y)

            if "starlight volley" in eff_l and not has_spawned_astral:
                has_spawned_astral = True
                arrow_dmg = max(20, int(base_atk * 0.75))
                p1 = AstralArrowProjectile(player.center_x, player.center_y, angle - 0.12, damage=arrow_dmg, speed=15.0)
                p2 = AstralArrowProjectile(player.center_x, player.center_y, angle + 0.12, damage=arrow_dmg, speed=15.0)
                p1.is_ancient = is_ancient
                p2.is_ancient = is_ancient
                self.spawn_projectile(p1)
                self.spawn_projectile(p2)

            if ("solar flare shockwave" in eff_l or "solar supernova" in eff_l) and not has_spawned_solar:
                has_spawned_solar = True
                shock_dmg = max(26, int(base_atk * 0.9)) if "solar flare shockwave" in eff_l else max(36, int(base_atk * 1.5))
                shock_proj = SolarFlareShockwave(player.center_x, player.center_y, damage=shock_dmg, max_radius=85.0)
                shock_proj.is_ancient = is_ancient
                self.spawn_projectile(shock_proj)
                self.sound_manager.play_spatial("explode", player.center_x, player.center_y, player.center_x, player.center_y)

            if "gravitational pulse" in eff_l and not has_spawned_grav:
                has_spawned_grav = True
                grav_dmg = max(30, int(base_atk * 1.05))
                grav_proj = GravitationalPulseProjectile(mouse_wx, mouse_wy, damage=grav_dmg, pull_radius=110.0)
                grav_proj.is_ancient = is_ancient
                self.spawn_projectile(grav_proj)

    def _check_weapon_hits(self, player, world=None):
        # Ranged weapons (bows, crossbows, staves, wands) deal damage via projectiles, NOT melee strikes!
        active = getattr(player, "inventory", None).get_active_item() if getattr(player, "inventory", None) else None
        is_tool = False
        tool_dmg = 2
        is_ancient = False
        if active:
            item_id = active.item_id.lower()
            item_data = getattr(active, "data", {}) or {}
            item_name = item_data.get("name", "").lower()
            rarity = str(item_data.get("rarity", "")).lower()
            if rarity in ("ancient", "rarity_ancient") or "ancient" in item_id:
                is_ancient = True
            if any(w in item_id or w in item_name for w in ("bow", "crossbow", "recurve", "shortbow", "longbow")) or any(w in item_id or w in item_name for w in ("staff", "wand", "scepter", "rod", "catalyst", "focus", "grimoire")):
                return
            if item_data.get("cat") == "tool" or item_data.get("category") == "tool" or any(t in item_id for t in ("pickaxe", "axe", "shovel", "hammer")) or any(t in item_name for t in ("pickaxe", "axe", "shovel", "hammer")):
                is_tool = True
                tool_dmg = item_data.get("damage", 2)
        elif hasattr(player, "equipment") and hasattr(player.equipment, "slots"):
            eq_weap = player.equipment.slots.get("weapon")
            if eq_weap:
                from src.rpg.equipment import ARMOR_DATA
                eq_data = ARMOR_DATA.get(eq_weap, {})
                rarity = str(eq_data.get("rarity", "")).lower()
                if rarity in ("ancient", "rarity_ancient") or "ancient" in str(eq_weap).lower():
                    is_ancient = True

        # Single-target constraint: Non-ancient melee weapons damage at most 1 enemy per swing!
        if not is_ancient and getattr(player, "swing_hit_targets", None) and len(player.swing_hit_targets) >= 1:
            return

        reach = 40.0
        hx = player.center_x + math.cos(player.aim_angle) * reach
        hy = player.center_y + math.sin(player.aim_angle) * reach
        hitbox = pygame.Rect(int(hx - 18), int(hy - 18), 36, 36)

        # RPG Damage Formula: Scaled by player ATK and Critical Rolls
        if is_tool:
            # Tools deal minimal combat damage and do not leverage full weapon attack power
            lvl_bonus = max(0, (player.stats.level - 1)) * 0.2
            base_dmg = max(1, int(tool_dmg + lvl_bonus))
            is_crit = False
            final_dmg = base_dmg
        else:
            base_dmg = player.stats.total_atk
            has_crit_overdrive = player.has_effect("critical overdrive") if hasattr(player, "has_effect") else False
            crit_mult = 2.0 if has_crit_overdrive else 1.8
            is_crit = (random.uniform(0, 100) < player.stats.total_crit_rate)
            final_dmg = int(base_dmg * (crit_mult if is_crit else random.uniform(0.9, 1.15)))

            if hasattr(player, "has_effect"):
                if player.has_effect("molten blaze"):
                    final_dmg += 12
                if player.has_effect("armor penetration"):
                    final_dmg += 15

        if self.boss and not self.boss.is_dead and self.boss.hurt_timer <= 0:
            if "boss" not in getattr(player, "swing_hit_targets", set()) and hitbox.colliderect(self.boss.rect):
                if has_line_of_sight(world, player.center_x, player.center_y, self.boss.center_x, self.boss.center_y):
                    getattr(player, "swing_hit_targets", set()).add("boss")
                    knock_x = math.cos(player.aim_angle) * 3.0
                    self.boss.take_damage(final_dmg, knockback_vx=knock_x)
                    if is_crit:
                        self.sound_manager.play("crit_hit")
                        self.particle_system.spawn_sparks(hx, hy, (255, 235, 50), count=18)
                        self.particle_system.spawn_debris(hx, hy, (255, 100, 30), count=6)
                        self.camera.add_shake(5.0, 0.22)
                    else:
                        self.sound_manager.play("hit_mob")
                        self.particle_system.spawn_sparks(hx, hy, (255, 230, 100), count=8)
                        self.camera.add_shake(3.0, 0.15)
                    self.spawn_damage_number(self.boss.center_x, self.boss.y - 12, final_dmg, color=(255, 230, 40) if is_crit else (255, 210, 50), is_crit=is_crit)
                    if hasattr(player, "has_effect"):
                        if player.has_effect("starburst explosion"):
                            self.particle_system.spawn_sparks(self.boss.center_x, self.boss.center_y, (255, 215, 60), count=16)
                        if (player.has_effect("molten blaze") or player.has_effect("superheated impact")) and hasattr(self.boss, "apply_burn"):
                            self.boss.apply_burn(dps=12, duration=4.0)
                            self.particle_system.spawn_sparks(self.boss.center_x, self.boss.center_y, (255, 120, 20), count=8)
                        if (player.has_effect("lacerating strike") or player.has_effect("lacerate")) and hasattr(self.boss, "apply_bleed"):
                            self.boss.apply_bleed(dps=10, duration=5.0)
                            self.particle_system.spawn_sparks(self.boss.center_x, self.boss.center_y, (200, 30, 30), count=8)
                    if self.is_client and self.client and self.client.connected:
                        self.client.send_mob_damage("boss", final_dmg, knock_x, 0.0, is_crit=is_crit)
                    if not is_ancient:
                        return

        for mob in self.mobs:
            if mob.is_alive and mob.hurt_timer <= 0 and hitbox.colliderect(mob.rect):
                if mob in getattr(player, "swing_hit_targets", set()):
                    continue
                if not has_line_of_sight(world, player.center_x, player.center_y, mob.center_x, mob.center_y):
                    continue
                getattr(player, "swing_hit_targets", set()).add(mob)
                knock_x = math.cos(player.aim_angle) * 5.0
                knock_y = min(-2.5, math.sin(player.aim_angle) * 4.0)
                actual_dmg = mob.take_damage(final_dmg, knockback_vx=knock_x, knockback_vy=knock_y)
                if not actual_dmg or isinstance(actual_dmg, bool):
                    actual_dmg = final_dmg
                if is_crit:
                    self.sound_manager.play("crit_hit")
                    self.particle_system.spawn_sparks(hx, hy, (255, 235, 50), count=18)
                    self.particle_system.spawn_debris(hx, hy, (255, 100, 30), count=6)
                    self.camera.add_shake(5.0, 0.22)
                else:
                    self.sound_manager.play("hit_mob")
                    self.particle_system.spawn_sparks(hx, hy, (255, 230, 100), count=8)
                    self.camera.add_shake(3.0, 0.15)
                self.spawn_damage_number(mob.center_x, mob.y - 12, actual_dmg, color=(255, 230, 40) if is_crit else (255, 210, 50), is_crit=is_crit)

                if hasattr(player, "has_effect"):
                    if player.has_effect("glacial chill") and hasattr(mob, "speed"):
                        mob.speed = max(0.4, mob.speed * 0.65)
                    if player.has_effect("thunderclap burst"):
                        mob.hurt_timer = 0.5
                    if player.has_effect("superheated impact"):
                        self.particle_system.spawn_sparks(mob.center_x, mob.center_y, (255, 100, 20), count=12)
                    if (player.has_effect("molten blaze") or player.has_effect("superheated impact")) and hasattr(mob, "apply_burn"):
                        mob.apply_burn(dps=8, duration=3.5)
                        self.particle_system.spawn_sparks(mob.center_x, mob.center_y, (255, 120, 20), count=6)
                    if (player.has_effect("lacerating strike") or player.has_effect("lacerate")) and hasattr(mob, "apply_bleed"):
                        mob.apply_bleed(dps=7, duration=4.0)
                        self.particle_system.spawn_sparks(mob.center_x, mob.center_y, (200, 30, 30), count=6)
                    if player.has_effect("starburst explosion") and is_ancient:
                        self.particle_system.spawn_sparks(mob.center_x, mob.center_y, (255, 230, 80), count=15)
                        for other in self.mobs:
                            if other != mob and other.is_alive:
                                if math.hypot(other.center_x - mob.center_x, other.center_y - mob.center_y) <= 72.0:
                                    other.take_damage(max(1, int(final_dmg * 0.65)), knockback_vx=knock_x * 0.5, knockback_vy=-2.0)
                    if player.has_effect("dark cleave") and is_ancient:
                        cleave_count = 0
                        for other in self.mobs:
                            if other != mob and other.is_alive and cleave_count < 3:
                                if math.hypot(other.center_x - mob.center_x, other.center_y - mob.center_y) <= 80.0:
                                    cleave_count += 1
                                    other.take_damage(max(1, int(final_dmg * 0.75)), knockback_vx=knock_x * 0.6, knockback_vy=-2.0)

                if mob.hp <= 0 or mob.is_dead:
                    self._on_mob_slain(mob, player)

                if self.is_client and self.client and self.client.connected:
                    self.client.send_mob_damage(getattr(mob, "mob_id", 0), final_dmg, knock_x, knock_y, is_crit=is_crit)

                # Single-target constraint: Non-ancient weapons only damage 1 enemy per swing!
                if not is_ancient:
                    return

    def _spawn_loot_drop(self, item_id, count, mx, my):
        """Spawns a DroppedItem with natural horizontal scatter so multiple drops spread apart."""
        ox = mx + random.uniform(-6.0, 6.0)
        vx = random.uniform(-2.2, 2.2)
        vy = random.uniform(-3.8, -2.4)
        self.dropped_items.append(
            DroppedItem(item_id, count, ox, my, self.asset_factory, vx=vx, vy=vy)
        )

    def _drop_mob_loot(self, mob, tuned=None):
        if tuned is None:
            tuned = getattr(self, "tuned_mob_drops", False)
        mx, my = mob.center_x, mob.center_y
        m_name = getattr(mob, "name", "")

        if tuned:
            if not hasattr(self, "_catalog_rarity_pools"):
                from src.ui.inventory import ITEM_REGISTRY
                self._catalog_rarity_pools = {
                    "common": [], "uncommon": [], "rare": [], "epic": [],
                    "mythic": [], "legendary": [], "ancient": []
                }
                for iid, idata in ITEM_REGISTRY.items():
                    r = idata.get("rarity")
                    if r in self._catalog_rarity_pools and idata.get("cat") in ("weapon", "armor_head", "armor_chest", "armor_legs", "accessory"):
                        self._catalog_rarity_pools[r].append(iid)

            is_night_elite = getattr(mob, "is_night_elite", False) or getattr(mob, "is_elite", False)
            if is_night_elite:
                # Night Elites (nightly champions) drop up to Epic (high probability of Rare/Epic, no Mythic/Legendary/Ancient)
                drop_count = random.choice([1, 2])
                for _ in range(drop_count):
                    tier_roll = random.random()
                    if tier_roll < 0.45 and self._catalog_rarity_pools.get("epic"):
                        drop_id = random.choice(self._catalog_rarity_pools["epic"])
                    elif tier_roll < 0.85 and self._catalog_rarity_pools.get("rare"):
                        drop_id = random.choice(self._catalog_rarity_pools["rare"])
                    else:
                        drop_id = random.choice(self._catalog_rarity_pools["uncommon"]) if self._catalog_rarity_pools.get("uncommon") else "healing_potion"
                    self._spawn_loot_drop(drop_id, 1, mx, my)
                return

            # Regular mobs: drop random 0-2 items only (not guaranteed 3-5 items).
            # Drop Common, Uncommon, Rare only (never Mythic/Ancient/Legendary/Epic).
            drop_count = random.choices([0, 1, 2], weights=[0.35, 0.45, 0.20])[0]
            if drop_count == 0:
                return

            common_items = ["copper_coin", "spud_sap", "raw_potato", "healing_potion"]
            if "Slime" in m_name:
                common_items = ["spud_sap", "copper_coin", "raw_potato"]
            elif "Skeleton" in m_name:
                common_items = ["bone", "iron_ore", "copper_coin"]
            elif "Zombie" in m_name or "Mummy" in m_name:
                common_items = ["copper_ore", "copper_coin", "healing_potion"]
            elif "Bat" in m_name:
                common_items = ["torch", "copper_coin"]

            for _ in range(drop_count):
                tier_roll = random.random()
                if tier_roll < 0.05 and self._catalog_rarity_pools.get("rare"):
                    drop_id = random.choice(self._catalog_rarity_pools["rare"])
                    cnt = 1
                elif tier_roll < 0.25 and self._catalog_rarity_pools.get("uncommon"):
                    drop_id = random.choice(self._catalog_rarity_pools["uncommon"])
                    cnt = 1
                else:
                    drop_id = random.choice(common_items)
                    cnt = random.randint(1, 4) if drop_id in ("copper_coin", "bone", "copper_ore", "spud_sap") else 1
                self._spawn_loot_drop(drop_id, cnt, mx, my)
            return

        # 1. Base Guaranteed Mob Drop
        if "Slime" in m_name:
            self._spawn_loot_drop("spud_sap", random.randint(1, 3), mx, my)
            if "Frost" in m_name:
                self._spawn_loot_drop("frost_core", 1, mx, my)
            elif "Sand" in m_name:
                self._spawn_loot_drop("sand_block", random.randint(2, 4), mx, my)
        elif "Zombie" in m_name or "Mummy" in m_name:
            self._spawn_loot_drop("copper_ore", random.randint(2, 5), mx, my)
            if "Frozen" in m_name:
                self._spawn_loot_drop("frost_core", 1, mx, my)
        elif "Skeleton" in m_name:
            self._spawn_loot_drop("bone", random.randint(2, 4), mx, my)
            self._spawn_loot_drop("iron_ore", random.randint(1, 3), mx, my)
        elif "Bat" in m_name:
            self._spawn_loot_drop("torch", random.randint(1, 3), mx, my)
            if "Ice" in m_name:
                self._spawn_loot_drop("frost_core", 1, mx, my)
        elif "Scorpion" in m_name:
            self._spawn_loot_drop("cactus", random.randint(2, 5), mx, my)
        elif "Crawler" in m_name or "Corrupt" in m_name or "Blight" in m_name:
            self._spawn_loot_drop("blightstone_block", random.randint(1, 3), mx, my)
        else:
            self._spawn_loot_drop("torch", random.randint(2, 4), mx, my)

        # 1b. Currency Coin Drops (Potaria Economy)
        if "Slime" in m_name:
            c_amount = random.randint(3, 12)
        elif "Zombie" in m_name or "Mummy" in m_name:
            c_amount = random.randint(12, 35)
        elif "Skeleton" in m_name:
            c_amount = random.randint(20, 50)
        else:
            c_amount = random.randint(8, 24)

        self._spawn_loot_drop("copper_coin", c_amount, mx, my)
        if random.random() < 0.12:
            self._spawn_loot_drop("silver_coin", 1, mx, my)

        # Build Rarity Catalog Pools for dynamic drops
        if not hasattr(self, "_catalog_rarity_pools"):
            from src.ui.inventory import ITEM_REGISTRY
            self._catalog_rarity_pools = {
                "common": [], "uncommon": [], "rare": [], "epic": [],
                "mythic": [], "legendary": [], "ancient": []
            }
            for iid, idata in ITEM_REGISTRY.items():
                r = idata.get("rarity")
                if r in self._catalog_rarity_pools and idata.get("cat") in ("weapon", "armor_head", "armor_chest", "armor_legs", "accessory"):
                    self._catalog_rarity_pools[r].append(iid)

        # 2. Common Roll (40% chance): Potato or Potion
        roll = random.random()
        if roll < 0.25:
            self._spawn_loot_drop("raw_potato", 1, mx, my)
        elif roll < 0.40:
            self._spawn_loot_drop("healing_potion", 1, mx, my)

        # 3. Uncommon Equipment Roll (3.5% chance - 1 in ~28):
        if random.random() < 0.035 and self._catalog_rarity_pools.get("uncommon"):
            unc_item = random.choice(self._catalog_rarity_pools["uncommon"])
            self._spawn_loot_drop(unc_item, 1, mx, my)

        # 4. Rare Roll (1.5% chance - 1 in ~67): Skill Books, Accessories, Biome Weapons, Rare Gear
        if random.random() < 0.015:
            rare_pool = [
                "skillbook_power_slash", "skillbook_whirlwind", "skillbook_dash", "skillbook_fireball",
                "skillbook_meteor", "skillbook_frost_nova", "skillbook_celestial_shield", "skillbook_void_singularity",
                "warrior_charm", "guardian_ring", "cactus_sword", "frost_blade", "sandstorm_spear",
                "portal_shard"
            ]
            if random.random() < 0.5 and self._catalog_rarity_pools.get("rare"):
                drop_id = random.choice(self._catalog_rarity_pools["rare"])
            else:
                drop_id = random.choice(rare_pool)
            self._spawn_loot_drop(drop_id, 1, mx, my)

        # 5. Epic Roll (0.50% chance - 1 in 200):
        if random.random() < 0.005:
            epic_pool = ["golden_fry", "zephyr_striders", "starch_blade", "shadow_cleaver", "talisman_of_vigor", "lucky_clover", "arcane_orchid"]
            if random.random() < 0.5 and self._catalog_rarity_pools.get("epic"):
                drop_id = random.choice(self._catalog_rarity_pools["epic"])
            else:
                drop_id = random.choice(epic_pool)
            self._spawn_loot_drop(drop_id, 1, mx, my)

        # 6. MYTHIC ROLL (0.15% chance - 1 in ~667):
        if random.random() < 0.0015 and self._catalog_rarity_pools.get("mythic"):
            m_item = random.choice(self._catalog_rarity_pools["mythic"])
            print(f"[LOOT] MYTHIC DROP! {m_item} has dropped from a defeated monster!")
            self._spawn_loot_drop(m_item, 1, mx, my)
            self.particle_system.spawn_sparks(mx, my, (255, 152, 0), count=30)

        # 7. LEGENDARY ROLL (0.05% chance - 1 in 2,000):
        if random.random() < 0.0005:
            if random.random() < 0.5 or not self._catalog_rarity_pools.get("legendary"):
                leg_item = "astral_wrath"
            else:
                leg_item = random.choice(self._catalog_rarity_pools["legendary"])
            print(f"[LOOT] LEGENDARY DROP! {leg_item} has dropped from a defeated monster!")
            self._spawn_loot_drop(leg_item, 1, mx, my)
            self.particle_system.spawn_sparks(mx, my, (255, 215, 0), count=45)

        # 8. ANCIENT ROLL (0.01% chance from regular mobs - 1 in 10,000):
        if random.random() < 0.0001 and self._catalog_rarity_pools.get("ancient"):
            anc_item = random.choice(self._catalog_rarity_pools["ancient"])
            self._trigger_ancient_drop(anc_item, mx, my)

    def _trigger_ancient_drop(self, anc_item, mx, my):
        """Triggers grand celebratory fanfare, screen shake, and celebratory toast when an Ancient relic drops."""
        from src.ui.inventory import ITEM_REGISTRY
        name = ITEM_REGISTRY.get(anc_item, {}).get("name", anc_item.replace("_", " ").title())
        print(f"[LOOT] *** ANCIENT RELIC DISCOVERED! {name} has fallen! ***")
        self._spawn_loot_drop(anc_item, 1, mx, my)
        self.ancient_drop_banner = {
            "item_id": anc_item,
            "name": name,
            "timer": 6.0,
        }
        if self.camera:
            self.camera.add_shake(16.0, 1.2)
        self.sound_manager.play("craft")
        self.particle_system.spawn_sparks(mx, my, (255, 215, 60), count=80)
        self.particle_system.spawn_debris(mx, my, (245, 60, 75), count=40)

    def _spawn_nightly_elite(self, world, player):
        """Spawns exactly one slightly bigger Champion of the Night with boosted stats & special skill once per night."""
        if self.nightly_elite_spawned:
            return
        # Ensure no other alive Night Elite is roaming before spawning another
        if any(getattr(m, "is_night_elite", False) and not getattr(m, "is_dead", False) and getattr(m, "hp", 0) > 0 for m in self.mobs):
            return

        # Determine surface ground position within 350-500px from player
        side = random.choice([-1, 1])
        spawn_px = player.center_x + side * random.randint(350, 500)
        spawn_tx = int(spawn_px // SCALED_TILE)

        # Scan for surface ground level
        ground_ty = None
        for ty in range(25, 110):
            if hasattr(world, "is_tile_solid") and world.is_tile_solid(spawn_tx, ty):
                ground_ty = ty
                break

        if ground_ty is None:
            ground_ty = max(30, int(player.y // SCALED_TILE))

        spawn_x = spawn_tx * SCALED_TILE
        spawn_y = (ground_ty - 2) * SCALED_TILE

        from src.entities.mob import NightEliteMob
        elite = NightEliteMob(spawn_x, spawn_y, self.asset_factory)

        self.spawn_mob(elite, player=player)
        self.nightly_elite_spawned = True
        print(f"[Combat] A Champion of the Night has arisen: {elite.name}!")
        if self.sound_manager:
            self.sound_manager.play("hurt")

    def _spawn_natural_mob(self, world, player, is_night, time_of_day=None):
        if time_of_day is None:
            time_of_day = getattr(world, "time_of_day", 0.75 if is_night else 0.25)

        # Pocket Dimension Arena or Boss Duel Protection: no stray mobs in arenas
        if abs(player.center_x) >= 2000 * SCALED_TILE or (self.boss and getattr(player, "pre_arena_pos", None)):
            return

        target_x = player.center_x
        target_y = player.center_y
        if getattr(self, "multiplayer_player_positions", None) and len(self.multiplayer_player_positions) > 0:
            target_x, target_y = random.choice(self.multiplayer_player_positions)

        side = random.choice([-1, 1])
        spawn_dist = random.uniform(500, 750)
        spawn_x = target_x + side * spawn_dist
        spawn_tx = int(math.floor(spawn_x / SCALED_TILE))
        player_ty = int(target_y // SCALED_TILE)

        # Search for ground around player's current vertical elevation
        ground_ty = None
        for ty in range(max(10, player_ty - 16), min(world.height - 8, player_ty + 16)):
            if world.get_tile(spawn_tx, ty) != 0 and world.get_tile(spawn_tx, ty - 1) == 0:
                ground_ty = ty
                break

        # Fallback search from surface down if player is in air or jumping
        if ground_ty is None:
            for ty in range(25, world.height - 25):
                if world.get_tile(spawn_tx, ty) != 0 and world.get_tile(spawn_tx, ty - 1) == 0:
                    ground_ty = ty
                    break

        if ground_ty is None:
            return

        is_morning = (time_of_day < 0.22)
        is_surface = (ground_ty < 85)
        if is_morning and is_surface:
            # Morning Peace: 0 aggressive surface monsters spawn so player can mine & chop wood peacefully
            return

        # Player-Built House & Base Protection (Minecraft / Terraria Style)
        # Never spawn monsters inside player-placed walls (wood, stone brick, glass)
        wall_at_spawn = world.get_wall(spawn_tx, ground_ty - 1)
        if wall_at_spawn in (WALL_WOOD, WALL_STONE_BRICK, WALL_GLASS):
            return

        # Check for illuminated enclosed room with ceiling (torches prevent monster spawning)
        has_ceiling = any(world.get_tile(spawn_tx, cy) != 0 for cy in range(max(0, ground_ty - 10), ground_ty - 1))
        if has_ceiling:
            has_torch = False
            for dx in range(-7, 8):
                for dy in range(-6, 7):
                    if world.get_tile(spawn_tx + dx, ground_ty - 1 + dy) == TILE_TORCH:
                        has_torch = True
                        break
                if has_torch:
                    break
            if has_torch:
                return

        spawn_y = (ground_ty - 1) * SCALED_TILE
        biome = world.get_biome_at(spawn_tx, ground_ty)

        # Rare roaming mini-boss encounter strictly underground in subterranean dungeons or deep caverns (never on surface)
        is_subterranean = (ground_ty >= 115 and (ground_ty > 130 or biome == BIOME_DUNGEON))
        if not self.boss and not self.grand_boss_defeated and is_subterranean and random.random() < 0.025:
            from src.entities.boss import IgnisColossus, CryoSpud, NecroTuber, LordMalus
            if biome == BIOME_DESERT:
                self.boss = IgnisColossus(spawn_x, spawn_y, self.asset_factory, self.sound_manager)
            elif biome == BIOME_SNOW:
                self.boss = CryoSpud(spawn_x, spawn_y, self.asset_factory, self.sound_manager)
            elif biome in (BIOME_CORRUPTION, BIOME_DUNGEON):
                self.boss = NecroTuber(spawn_x, spawn_y, self.asset_factory, self.sound_manager)
            else:
                self.boss = LordMalus(spawn_x, spawn_y, self.asset_factory, self.sound_manager)
            self.sound_manager.play("craft")
            print(f"[Combat] A subterranean mini-boss has emerged in {biome.title()}: {self.boss.name}!")
            return

        # Biome-appropriate enemy spawns
        if biome == BIOME_DESERT:
            if is_night or ground_ty > 110:
                mob_cls = random.choice([Mummy, DesertScorpion, SandSlime, RockZombie, DiggerMob])
            else:
                mob_cls = SandSlime
            self.spawn_mob(mob_cls(spawn_x, spawn_y, self.asset_factory), player=player)

        elif biome == BIOME_SNOW:
            if is_night or ground_ty > 110:
                mob_cls = random.choice([IceZombie, IceBat, FrostSlime, RockZombie])
            else:
                mob_cls = FrostSlime
            if mob_cls == IceBat:
                self.spawn_mob(IceBat(spawn_x, spawn_y - 80, self.asset_factory), player=player)
            else:
                self.spawn_mob(mob_cls(spawn_x, spawn_y, self.asset_factory), player=player)

        elif biome == BIOME_CORRUPTION:
            mob_cls = random.choice([CorruptSlime, ShadowCrawler, ShieldWeaver])
            self.spawn_mob(mob_cls(spawn_x, spawn_y, self.asset_factory), player=player)

        elif biome in (BIOME_CAVERN, BIOME_MUSHROOM):
            mob_cls = random.choice([CaveBat, Skeleton, PurpleSlime, DiggerMob, ShieldWeaver, RockZombie])
            if mob_cls == CaveBat:
                self.spawn_mob(CaveBat(spawn_x, spawn_y - 80, self.asset_factory), player=player)
            else:
                self.spawn_mob(mob_cls(spawn_x, spawn_y, self.asset_factory), player=player)

        elif biome == BIOME_DUNGEON:
            mob_cls = random.choice([Skeleton, ShadowCrawler, ShieldWeaver])
            self.spawn_mob(mob_cls(spawn_x, spawn_y, self.asset_factory), player=player)

        else: # BIOME_FOREST
            if is_night:
                r = random.random()
                if r < 0.35:
                    self.spawn_mob(Zombie(spawn_x, spawn_y, self.asset_factory), player=player)
                elif r < 0.60:
                    self.spawn_mob(DemonEye(spawn_x, player.center_y - 140, self.asset_factory), player=player)
                elif r < 0.80:
                    self.spawn_mob(RockZombie(spawn_x, spawn_y, self.asset_factory), player=player)
                else:
                    self.spawn_mob(PurpleSlime(spawn_x, spawn_y, self.asset_factory), player=player)
            else:
                self.spawn_mob(GreenSlime(spawn_x, spawn_y, self.asset_factory), player=player)

    def render(self, target_surf, camera, renderer=None, render_damage_numbers=True):
        for item in self.dropped_items:
            item.render(target_surf, camera)

        for p in self.projectiles:
            if isinstance(p, ArrowProjectile):
                arr_t = getattr(p, "arrow_type", "")
                if arr_t == "frostburn_arrow":
                    sprite = self.frostburn_arrow_sprite
                elif "flame" in arr_t or "fire" in arr_t or "magma" in arr_t:
                    sprite = self.flame_arrow_sprite
                elif "astral" in arr_t or "celestial" in arr_t:
                    sprite = self.astral_arrow_sprite
                else:
                    sprite = self.arrow_sprite
                p.render(target_surf, camera, sprite)
            elif isinstance(p, CelestialStarProjectile):
                p.render(target_surf, camera, self.star_sprite)
            elif hasattr(p, "render"):
                p.render(target_surf, camera)

        # High-density projectile batch rendering (Stage 2 HAL Hardware Acceleration)
        if renderer and hasattr(renderer, "draw_projectiles_batch") and self.enemy_projectiles:
            renderer.draw_projectiles_batch(self.enemy_projectiles, camera)
        else:
            for ep in self.enemy_projectiles:
                ep.render(target_surf, camera)

        for mob in self.mobs:
            mob.render(target_surf, camera)

        if self.boss:
            if hasattr(self.boss, "render"):
                try:
                    self.boss.render(target_surf, camera, renderer=renderer)
                except TypeError:
                    self.boss.render(target_surf, camera)

        if self.secondary_boss:
            if hasattr(self.secondary_boss, "render"):
                try:
                    self.secondary_boss.render(target_surf, camera, renderer=renderer)
                except TypeError:
                    self.secondary_boss.render(target_surf, camera)

        if render_damage_numbers and getattr(self, "show_damage_numbers", True):
            for dn in self.damage_numbers:
                dn.render(target_surf, camera, self.font, self.font_crit)

    def get_enemy_projectiles_sync_data(self):
        """Serializes active enemy projectiles on host for network broadcast."""
        data = []
        for ep in self.enemy_projectiles:
            if ep.life > 0:
                p_type = "rock" if hasattr(ep, "radius") and ep.radius == 6 and not hasattr(ep, "color") else "spit"
                data.append({
                    "type": p_type,
                    "x": round(float(ep.pos.x), 2),
                    "y": round(float(ep.pos.y), 2),
                    "vx": round(float(ep.vel.x), 2),
                    "vy": round(float(ep.vel.y), 2),
                    "damage": int(ep.damage),
                    "color": list(getattr(ep, "color", (80, 220, 60))),
                    "life": round(float(ep.life), 2),
                })
        return data

    def get_dropped_items_sync_data(self):
        """Serializes active dropped items on host for network broadcast."""
        data = []
        for it in self.dropped_items:
            if not getattr(it, "picked_up", False) and getattr(it, "life", 1.0) > 0:
                data.append({
                    "item_id": it.item_id,
                    "count": int(it.count),
                    "x": round(float(it.x), 2),
                    "y": round(float(it.y), 2),
                })
        return data

    def get_mobs_sync_data(self):
        """Serializes active mob states on authoritative host for network broadcast."""
        data = []
        for m in self.mobs:
            if not m.is_dead and m.hp > 0:
                mid = getattr(m, "mob_id", 0)
                mtype = getattr(m, "mob_type", "green_slime")
                data.append({
                    "id": mid,
                    "mob_id": mid,
                    "type": mtype,
                    "mob_type": mtype,
                    "x": round(float(m.x), 2),
                    "y": round(float(m.y), 2),
                    "vx": round(float(m.vx), 2),
                    "vy": round(float(m.vy), 2),
                    "hp": int(m.hp),
                    "max_hp": int(m.max_hp),
                    "facing_right": bool(getattr(m, "facing_right", True)),
                    "on_ground": bool(getattr(m, "on_ground", False)),
                    "anim_state": getattr(m, "state", "idle") if hasattr(m, "state") else ("walk" if abs(getattr(m, "vx", 0.0)) > 0.1 else "idle"),
                    "hurt": getattr(m, "hurt_timer", 0.0) > 0,
                })
        return data

    def get_boss_sync_data(self):
        """Serializes boss state on authoritative host for network broadcast."""
        if not self.boss or self.boss.is_dead:
            return None
        b_type = getattr(self.boss, "boss_type", "lord_malus")
        b_dict = {
            "type": b_type,
            "boss_type": b_type,
            "name": getattr(self.boss, "name", "Boss"),
            "x": round(float(self.boss.x), 2),
            "y": round(float(self.boss.y), 2),
            "vx": round(float(self.boss.vx), 2),
            "vy": round(float(self.boss.vy), 2),
            "hp": int(self.boss.hp),
            "max_hp": int(self.boss.max_hp),
            "phase": int(getattr(self.boss, "phase", 1)),
            "hurt": getattr(self.boss, "hurt_timer", 0.0) > 0,
            "transforming": bool(getattr(self.boss, "is_transforming", False)),
        }
        if hasattr(self.boss, "get_projectiles_sync_data"):
            b_dict["projectiles"] = self.boss.get_projectiles_sync_data()
        return b_dict

    def sync_from_host(self, mobs_data, boss_data=None, enemy_projectiles=None, dropped_items=None):
        """Updates and reconciles client mob entities from authoritative host snapshot."""
        if isinstance(mobs_data, dict):
            boss_data = mobs_data.get("boss", boss_data)
            enemy_projectiles = mobs_data.get("enemy_projectiles", enemy_projectiles)
            dropped_items = mobs_data.get("dropped_items", dropped_items)
            mobs_data = mobs_data.get("mobs", [])

        current_ids = set()
        mobs_by_id = {getattr(m, "mob_id", None): m for m in self.mobs if getattr(m, "mob_id", None) is not None}

        for md in mobs_data:
            m_id = md.get("id") if "id" in md else md.get("mob_id")
            if m_id is None:
                continue
            current_ids.add(m_id)

            if m_id in mobs_by_id:
                mob = mobs_by_id[m_id]
                mob.target_x = float(md.get("x", mob.x))
                mob.target_y = float(md.get("y", mob.y))
                mob.target_sync_x = mob.target_x
                mob.target_sync_y = mob.target_y
                mob.vx = float(md.get("vx", mob.vx))
                mob.vy = float(md.get("vy", mob.vy))
                mob.hp = int(md.get("hp", mob.hp))
                mob.max_hp = int(md.get("max_hp", mob.max_hp))
                mob.facing_right = bool(md.get("facing_right", mob.facing_right))
                mob.on_ground = bool(md.get("on_ground", getattr(mob, "on_ground", False)))
                if md.get("anim_state"):
                    mob.state = md.get("anim_state")
                if md.get("hurt"):
                    mob.hurt_timer = 0.2
                    mob.hp_bar_timer = 3.0
            else:
                m_type = md.get("type") if "type" in md else md.get("mob_type", "green_slime")
                from src.entities.mob import create_mob_by_type
                new_mob = create_mob_by_type(m_type, md.get("x", 0.0), md.get("y", 0.0), self.asset_factory)
                new_mob.mob_id = m_id
                new_mob.mob_type = m_type
                new_mob.vx = float(md.get("vx", 0.0))
                new_mob.vy = float(md.get("vy", 0.0))
                new_mob.hp = int(md.get("hp", new_mob.max_hp))
                new_mob.max_hp = int(md.get("max_hp", new_mob.max_hp))
                new_mob.facing_right = bool(md.get("facing_right", True))
                new_mob.on_ground = bool(md.get("on_ground", False))
                new_mob.target_x = new_mob.x
                new_mob.target_y = new_mob.y
                new_mob.target_sync_x = new_mob.target_x
                new_mob.target_sync_y = new_mob.target_y
                if md.get("anim_state"):
                    new_mob.state = md.get("anim_state")
                self.mobs.append(new_mob)

        # Remove mobs no longer present in host snapshot
        self.mobs = [m for m in self.mobs if getattr(m, "mob_id", None) in current_ids and not m.is_dead and m.hp > 0]

        # Boss reconciliation
        if boss_data:
            b_type = boss_data.get("type", "lord_malus")
            b_x = float(boss_data.get("x", 0.0))
            b_y = float(boss_data.get("y", 0.0))
            if not self.boss or getattr(self.boss, "boss_type", None) != b_type:
                from src.entities.boss import create_boss_by_type
                self.boss = create_boss_by_type(b_type, b_x, b_y, self.asset_factory, self.sound_manager)
                self.boss.boss_type = b_type
            self.boss.name = str(boss_data.get("name", getattr(self.boss, "name", "Boss")))
            self.boss.target_x = b_x
            self.boss.target_y = b_y
            if not hasattr(self.boss, "target_x"):
                self.boss.x = b_x
                self.boss.y = b_y
            self.boss.vx = float(boss_data.get("vx", 0.0))
            self.boss.vy = float(boss_data.get("vy", 0.0))
            self.boss.hp = int(boss_data.get("hp", self.boss.hp))
            self.boss.max_hp = int(boss_data.get("max_hp", self.boss.max_hp))
            self.boss.phase = int(boss_data.get("phase", 1))
            self.boss.is_transforming = bool(boss_data.get("transforming", False))
            if boss_data.get("hurt"):
                self.boss.hurt_timer = 0.2
            if "projectiles" in boss_data and hasattr(self.boss, "sync_projectiles"):
                self.boss.sync_projectiles(boss_data["projectiles"])
        else:
            if self.boss:
                if isinstance(self.boss, GrandBossSolRho):
                    self.grand_boss_defeated = True
                self.boss_defeated = True
                self.boss.is_dead = True
                self.boss = None

        # Reconcile enemy projectiles
        if enemy_projectiles is not None:
            new_eps = []
            for ep_data in enemy_projectiles:
                ptype = ep_data.get("type", "spit")
                px = float(ep_data.get("x", 0.0))
                py = float(ep_data.get("y", 0.0))
                pvx = float(ep_data.get("vx", 0.0))
                pvy = float(ep_data.get("vy", 0.0))
                dmg = int(ep_data.get("damage", 12))
                if ptype == "rock":
                    from src.entities.mob import RockProjectile
                    proj = RockProjectile(px, py, pvx, pvy, damage=dmg)
                else:
                    col = tuple(ep_data.get("color", (80, 220, 60)))
                    proj = MobSpitProjectile(px, py, pvx, pvy, damage=dmg, color=col)
                proj.life = float(ep_data.get("life", 3.0))
                new_eps.append(proj)
            self.enemy_projectiles = new_eps

        # Reconcile dropped items
        if dropped_items is not None:
            from src.entities.dropped_item import DroppedItem
            new_items = []
            for it_data in dropped_items:
                iid = it_data.get("item_id")
                icnt = int(it_data.get("count", 1))
                ix = float(it_data.get("x", 0.0))
                iy = float(it_data.get("y", 0.0))
                matched = None
                for old_it in self.dropped_items:
                    if old_it.item_id == iid and math.hypot(old_it.x - ix, old_it.y - iy) < 36.0:
                        matched = old_it
                        break
                if matched:
                    matched.x = matched.x * 0.7 + ix * 0.3
                    matched.y = matched.y * 0.7 + iy * 0.3
                    matched.count = icnt
                    new_items.append(matched)
                else:
                    new_items.append(DroppedItem(iid, icnt, ix, iy, self.asset_factory))
            self.dropped_items = new_items

    def apply_remote_mob_damage(self, damage_data):
        """Applies damage reported by a client to authoritative mob or boss."""
        m_id = damage_data.get("mob_id")
        dmg = damage_data.get("damage", 10)
        kvx = damage_data.get("knockback_vx", 0.0)
        kvy = damage_data.get("knockback_vy", -2.0)
        is_crit = damage_data.get("is_crit", False)

        if m_id == "boss" and self.boss and not self.boss.is_dead:
            self.boss.take_damage(dmg, knockback_vx=kvx)
            self.sound_manager.play("hit_mob")
            self.spawn_damage_number(self.boss.center_x, self.boss.y - 12, dmg, is_crit=is_crit)
            self.particle_system.spawn_sparks(self.boss.center_x, self.boss.center_y, (255, 230, 100), 8)
            return

        for mob in self.mobs:
            if getattr(mob, "mob_id", None) == m_id and not mob.is_dead:
                mob.take_damage(dmg, knockback_vx=kvx, knockback_vy=kvy)
                self.sound_manager.play("hit_mob")
                self.spawn_damage_number(mob.center_x, mob.y - 12, dmg, is_crit=is_crit)
                self.particle_system.spawn_sparks(mob.center_x, mob.center_y, (255, 230, 100), 8)
                break
