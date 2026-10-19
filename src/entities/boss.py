"""
Potaria - Boss Entity System: Dungeon Mini-Bosses & Souls-Like Grand Boss
Featuring:
- Underground Mini-Bosses: Lord Malus, Ignis Colossus, Cryo-Spud, Necro-Tuber
- Grand Boss: SOL-RHO THE CELESTIAL TITAN (2-Phase Souls-like battle with color transformation,
  dual health bars, Black Hole Singularity, Void Meteors, and LAN multiplayer difficulty scaling!)
Developer: Kurados
"""

import math
import random
import pygame
from src.constants import SCREEN_WIDTH, SCREEN_HEIGHT, SCALED_TILE

from src.entities.bullet_hell import (
    BossProjectile, BulletHellPatterns, get_bullet_surface
)


# ==============================================================================
# BASE DUNGEON MINI-BOSS
# ==============================================================================
class DungeonMiniBoss:
    """Base class for subterranean dungeon mini-boss encounters."""
    def __init__(self, x, y, asset_factory, sound_manager, name, max_hp, damage, sprite_key, proj_key, defense=16):
        self.x = float(x)
        self.y = float(y)
        self.width = 96
        self.height = 96
        self.base_max_hp = max_hp
        self.base_damage = damage
        self.base_defense = defense
        self.max_hp = max_hp
        self.hp = max_hp
        self.display_hp = float(max_hp)
        self.damage = damage
        self.defense = defense
        self.name = name
        self.is_mini_boss = True
        self.boss_type = "dungeon_mini_boss"
        self.frect = pygame.FRect(self.x, self.y, self.width, self.height)

        self.asset_factory = asset_factory
        self.sound_manager = sound_manager

        raw_frames = asset_factory.boss.get(sprite_key, asset_factory.boss["lord_malus"])
        self.frames = [pygame.transform.scale(f, (self.width, self.height)) for f in raw_frames]
        self.proj_sprite = pygame.transform.scale(asset_factory.boss.get(proj_key, asset_factory.boss["fireball"]), (28, 28))

        self.frame_idx = 0
        self.anim_timer = 0.0
        self.state = "hover"
        self.state_timer = 2.0
        self.vx = 0.0
        self.vy = 0.0
        self.is_dead = False
        self.hurt_timer = 0.0
        self.phase = 1
        self.triggered_phase2_signature = False
        self.projectiles = []
        self.attack_cooldown = 1.1

        # Bullet-Hell Pattern State Machine
        self.pattern_index = 0
        self.active_pattern = None
        self.pattern_duration = 0.0
        self.pattern_step_timer = 0.0
        self.pattern_angle = 0.0
        self.pattern_state = {}

        # Status Effects (Burn & Bleed DoT)
        self.burn_timer = 0.0
        self.burn_dps = 0
        self.bleed_timer = 0.0
        self.bleed_dps = 0
        self.dot_tick_timer = 0.0

    def scale_to_player(self, player_level, player_atk, rematch_multiplier=1.0):
        """Dynamically scales mini-boss HP, defense, and damage to player progression and rematch tier."""
        lvl = max(1, player_level)
        atk = max(0, player_atk)
        scale = (1.0 + (lvl - 1) * 0.14 + max(0, (atk - 30) / 75.0) * 0.35) * rematch_multiplier
        self.max_hp = int(self.base_max_hp * scale)
        self.hp = self.max_hp
        self.display_hp = float(self.max_hp)
        self.defense = int(self.base_defense * (1.0 + (lvl - 1) * 0.08) * rematch_multiplier)
        self.damage = int(self.base_damage * (1.0 + (lvl - 1) * 0.05) * min(2.5, rematch_multiplier))

    def apply_burn(self, dps=10, duration=4.0):
        self.burn_dps = max(self.burn_dps, dps)
        self.burn_timer = max(self.burn_timer, duration)

    def apply_bleed(self, dps=10, duration=5.0):
        self.bleed_dps = max(self.bleed_dps, dps)
        self.bleed_timer = max(self.bleed_timer, duration)

    def update_dots(self, dt):
        """Ticks active burn and bleed DoT timers and inflicts periodic tick damage to boss."""
        if (self.burn_timer > 0 or self.bleed_timer > 0) and not self.is_dead:
            self.dot_tick_timer += dt
            if self.burn_timer > 0:
                self.burn_timer -= dt
                if self.burn_timer <= 0:
                    self.burn_dps = 0
            if self.bleed_timer > 0:
                self.bleed_timer -= dt
                if self.bleed_timer <= 0:
                    self.bleed_dps = 0

            if self.dot_tick_timer >= 1.0:
                self.dot_tick_timer = 0.0
                total_dot = (self.burn_dps if self.burn_dps > 0 else 0) + (self.bleed_dps if self.bleed_dps > 0 else 0)
                if total_dot > 0:
                    self.take_damage(total_dot, ignore_defense=True)

    @property
    def rect(self):
        self.frect.x = self.x
        self.frect.y = self.y
        return self.frect

    @property
    def center_x(self):
        return self.x + self.width / 2.0

    @property
    def center_y(self):
        return self.y + self.height / 2.0

    @property
    def is_alive(self):
        return not self.is_dead and self.hp > 0

    @property
    def alive(self):
        return not self.is_dead and self.hp > 0

    def take_damage(self, amount, knockback_vx=0.0, knockback_vy=0.0, ignore_defense=False):
        if self.is_dead:
            return False
        if amount == 2000:
            effective_dmg = max(self.hp, 2000)
        elif not ignore_defense:
            if getattr(self, "defense", 0) > 0:
                effective_dmg = max(1, int(amount - self.defense))
            else:
                effective_dmg = max(1, int(amount))

            # Innate Boss Armor: 25% damage mitigation against raw strikes
            effective_dmg = max(1, int(effective_dmg * 0.75))

            # Per-hit damage clamp: No single hit can exceed 4.5% of max HP (anti-burst cheese)
            max_clamp = max(15, int(self.max_hp * 0.045))
            effective_dmg = min(effective_dmg, max_clamp)
        else:
            effective_dmg = max(1, int(amount))

        self.hp -= effective_dmg
        self.hurt_timer = 0.15
        self.vx += knockback_vx * 0.15
        self.vy += knockback_vy * 0.15

        if self.hp <= self.max_hp * 0.5 and self.phase == 1:
            self.phase = 2
            self.attack_cooldown = 0.50
            self.triggered_phase2_signature = True

        if self.hp <= 0:
            self.hp = 0
            self.is_dead = True
        return True

    def update(self, dt, world, player, particle_system, camera, combat=None):
        if self.is_dead:
            return

        if self.hurt_timer > 0:
            self.hurt_timer -= dt

        self.anim_timer += dt
        if self.anim_timer >= 0.18:
            self.anim_timer = 0.0
            self.frame_idx = (self.frame_idx + 1) % len(self.frames)

        dist_x = player.center_x - self.center_x
        dist_y = player.center_y - self.center_y

        self.state_timer -= dt
        self.attack_cooldown -= dt

        # Phase 2 HP Threshold Signature Trigger
        if getattr(self, "triggered_phase2_signature", False):
            self.triggered_phase2_signature = False
            self.cast_signature_attack(player, particle_system, camera)

        # Step active streaming bullet-hell pattern
        if self.active_pattern:
            self._step_pattern(dt, player, particle_system, camera)

        if self.state == "hover":
            target_x = player.center_x + math.sin(pygame.time.get_ticks() * 0.002) * 160
            target_y = player.center_y - 130 + math.cos(pygame.time.get_ticks() * 0.003) * 50
            self.vx += (target_x - self.x) * 0.035
            self.vy += (target_y - self.y) * 0.035
            self.vx *= 0.92
            self.vy *= 0.92

            if self.attack_cooldown <= 0 and not self.active_pattern:
                self.attack_cooldown = 1.1 if self.phase == 1 else 0.70
                self._cast_attack(player, particle_system, camera)

            if self.state_timer <= 0:
                self.state = "charge"
                self.state_timer = 1.3
                charge_speed = 8.5 if self.phase == 1 else 11.0
                angle = math.atan2(dist_y, dist_x)
                self.vx = math.cos(angle) * charge_speed
                self.vy = math.sin(angle) * charge_speed
                camera.add_shake(5.0, 0.35)

        elif self.state == "charge":
            self.vx *= 0.98
            self.vy *= 0.98
            particle_system.spawn_debris(self.center_x, self.center_y, self._trail_color(), count=2)
            if self.state_timer <= 0:
                self.state = "hover"
                self.state_timer = random.uniform(2.4, 3.6)

        self.x += self.vx
        self.y += self.vy

        # Update Projectiles & Graze / Damage Detection
        for p in self.projectiles:
            p.update(dt, player)

            # Celestial Aegis: Deflects / destroys enemy projectiles near player
            if p.life > 0 and getattr(player, "has_effect", None) and player.has_effect("celestial aegis"):
                if math.hypot(p.x - player.center_x, p.y - player.center_y) < 38.0:
                    p.life = 0
                    if self.sound_manager:
                        self.sound_manager.play_spatial("hit_block", p.x, p.y, player.center_x, player.center_y)
                    particle_system.spawn_sparks(p.x, p.y, (100, 220, 255), count=10)
                    continue

            # Celestial Reversal: Timed reflection field
            if (p.life > 0 and not getattr(p, "reflected", False)
                and not getattr(player, "is_dead", False)
                and getattr(player, "reflection_field_timer", 0.0) > 0
                and getattr(player, "reflection_budget", 0) > 0):
                if math.hypot(p.x - player.center_x, p.y - player.center_y) < 52.0:
                    if p.reflect(self.center_x, self.center_y, damage_mult=1.5):
                        player.reflection_budget -= 1
                        player.reflected_projectiles_count = getattr(player, "reflected_projectiles_count", 0) + 1
                        if self.sound_manager:
                            self.sound_manager.play_spatial("hit_block", p.x, p.y, player.center_x, player.center_y)
                        if particle_system:
                            particle_system.spawn_sparks(p.x, p.y, (255, 240, 130), count=14)
                            particle_system.spawn_debris(p.x, p.y, (120, 240, 255), count=6)
                        vfx = getattr(player, "vfx_manager", None)
                        if vfx:
                            vfx.spawn("projectile_reflect", p.x, p.y, duration=0.35, scale=1.3)
                        continue

            # Reflected projectile hitting the boss!
            if p.life > 0 and getattr(p, "reflected", False):
                if p.rect.colliderect(self.frect):
                    self.take_damage(p.damage, knockback_vx=p.vx * 0.2, knockback_vy=p.vy * 0.2)
                    p.life = 0
                    particle_system.spawn_sparks(p.x, p.y, (255, 235, 120), count=16)
                    if combat and hasattr(combat, "spawn_damage_number"):
                        combat.spawn_damage_number(self.center_x, self.y - 10, p.damage, color=(255, 235, 80))
                    continue
                # Reflected projectiles do not harm the player!
                continue

            if p.life > 0 and p.rect.colliderect(player.rect):
                damaged = player.take_damage(p.damage, knockback_vx=p.vx * 0.7, knockback_vy=-3.5)
                # Dissipate non-singularity projectile upon core collision (prevents lingering stunlock during i-frames)
                if getattr(p, "p_type", "linear") != "singularity":
                    p.life = 0
                if damaged:
                    particle_system.spawn_sparks(player.center_x, player.center_y, self._trail_color(), 8)
                    camera.add_shake(4.0, 0.2)
                    if combat and hasattr(combat, "spawn_damage_number"):
                        dmg_val = getattr(player, "last_damage_taken", p.damage)
                        combat.spawn_damage_number(player.center_x, player.y - 10, dmg_val, color=(255, 50, 50))
                else:
                    particle_system.spawn_sparks(p.x, p.y, (255, 255, 255), count=4)
            elif getattr(p, "grazed", False) and not getattr(p, "_graze_sparked", False):
                p._graze_sparked = True
                particle_system.spawn_sparks(p.x, p.y, (180, 240, 255), count=2)

        self.projectiles = [p for p in self.projectiles if p.life > 0]

    def _step_pattern(self, dt, player, particle_system, camera=None):
        """Steps multi-wave bullet-hell streams (subclasses implement unique behaviors)."""
        pass

    def _cast_attack(self, player, particle_system, camera=None):
        angle = math.atan2(player.center_y - self.center_y, player.center_x - self.center_x)
        speed = 5.4
        vx = math.cos(angle) * speed
        vy = math.sin(angle) * speed
        self.projectiles.append(BossProjectile(self.center_x, self.center_y, vx, vy, self.proj_sprite, damage=self.damage - 4))

        if self.phase == 2:
            for offset in (-0.35, 0.35):
                svx = math.cos(angle + offset) * speed
                svy = math.sin(angle + offset) * speed
                self.projectiles.append(BossProjectile(self.center_x, self.center_y, svx, svy, self.proj_sprite, damage=self.damage - 4))
        particle_system.spawn_sparks(self.center_x, self.center_y, self._trail_color(), count=10)

    def get_projectiles_sync_data(self, player=None):
        """Serializes active projectiles on host for network broadcast."""
        data = []
        alive = [p for p in self.projectiles if p.life > 0]
        if len(alive) > 350 and player:
            alive.sort(key=lambda p: math.hypot(p.x - player.center_x, p.y - player.center_y))
            alive = alive[:350]
        elif len(alive) > 350:
            alive = alive[:350]
        for p in alive:
            data.append(p.to_sync_dict())
        return data

    def sync_projectiles(self, proj_data_list):
        """Reconciles client projectiles from authoritative host snapshot."""
        if not proj_data_list and not self.projectiles:
            return
        existing_by_id = {p.p_id: p for p in self.projectiles if hasattr(p, "p_id")}
        new_list = []
        for pd in proj_data_list:
            pid = pd.get("id")
            if pid is not None and pid in existing_by_id:
                p = existing_by_id[pid]
                dist = math.hypot(p.x - float(pd.get("x", p.x)), p.y - float(pd.get("y", p.y)))
                if dist > 120.0:
                    p.x = float(pd.get("x", p.x))
                    p.y = float(pd.get("y", p.y))
                else:
                    p.x = p.x * 0.70 + float(pd.get("x", p.x)) * 0.30
                    p.y = p.y * 0.70 + float(pd.get("y", p.y)) * 0.30
                p.vx = float(pd.get("vx", p.vx))
                p.vy = float(pd.get("vy", p.vy))
                p.life = float(pd.get("l", p.life))
                p.delay_move = float(pd.get("del", p.delay_move))
                new_list.append(p)
            else:
                new_p = BossProjectile.from_sync_dict(pd, sprite=self.proj_sprite)
                new_list.append(new_p)
        self.projectiles = new_list

    def update_client_projectiles(self, dt, player, particle_system, camera, combat=None):
        """Updates and handles projectile dodging/grazing on LAN client."""
        for p in self.projectiles:
            p.update(dt, player)

            # Celestial Aegis: Deflects / destroys enemy projectiles near player
            if p.life > 0 and getattr(player, "has_effect", None) and player.has_effect("celestial aegis"):
                if math.hypot(p.x - player.center_x, p.y - player.center_y) < 38.0:
                    p.life = 0
                    if self.sound_manager:
                        self.sound_manager.play_spatial("hit_block", p.x, p.y, player.center_x, player.center_y)
                    if particle_system:
                        particle_system.spawn_sparks(p.x, p.y, (100, 220, 255), count=10)
                    continue

            if p.life > 0 and p.rect.colliderect(player.rect):
                damaged = player.take_damage(p.damage, knockback_vx=p.vx * 0.7, knockback_vy=-3.5)
                # Dissipate non-singularity projectile upon core collision (prevents lingering stunlock during i-frames)
                if getattr(p, "p_type", "linear") != "singularity":
                    p.life = 0
                if damaged:
                    if particle_system:
                        particle_system.spawn_sparks(player.center_x, player.center_y, self._trail_color(), 8)
                    if camera:
                        camera.add_shake(4.0, 0.2)
                    if combat and hasattr(combat, "spawn_damage_number"):
                        dmg_val = getattr(player, "last_damage_taken", p.damage)
                        combat.spawn_damage_number(player.center_x, player.y - 10, dmg_val, color=(255, 50, 50))
                else:
                    if particle_system:
                        particle_system.spawn_sparks(p.x, p.y, (255, 255, 255), count=4)
            elif getattr(p, "grazed", False) and not getattr(p, "_graze_sparked", False):
                p._graze_sparked = True
                if particle_system:
                    particle_system.spawn_sparks(p.x, p.y, (180, 240, 255), count=2)
        self.projectiles = [p for p in self.projectiles if p.life > 0]

    def _trail_color(self):
        return (160, 50, 180)

    def render(self, target_surf, camera, renderer=None):
        if self.is_dead:
            return

        if renderer and hasattr(renderer, "draw_projectiles_batch") and self.projectiles:
            renderer.draw_projectiles_batch(self.projectiles, camera)
        else:
            for p in self.projectiles:
                p.render(target_surf, camera)

        sx, sy = camera.world_to_screen(self.x, self.y)
        cur_surf = self.frames[self.frame_idx]

        if self.hurt_timer > 0:
            tinted = cur_surf.copy()
            tinted.fill((255, 80, 80, 180), special_flags=pygame.BLEND_RGBA_MULT)
            cur_surf = tinted

        target_surf.blit(cur_surf, (sx, sy))

    def render_boss_bar(self, target_surf, font, font_title, bar_y=None):
        if self.is_dead:
            return
        if bar_y is None:
            bar_y = SCREEN_HEIGHT - 60
        self.bar_y = bar_y
        bar_w = 360
        bar_h = 14
        bar_x = (SCREEN_WIDTH - bar_w) // 2

        # Smooth ghost damage lag interpolation
        if not hasattr(self, "display_hp"):
            self.display_hp = float(self.hp)
        if self.display_hp > self.hp:
            self.display_hp = max(float(self.hp), self.display_hp - max(15.0, (self.display_hp - self.hp) * 0.08))
        elif self.display_hp < self.hp:
            self.display_hp = float(self.hp)

        panel_x = bar_x - 10
        panel_y = bar_y - 20
        panel_w = bar_w + 20
        panel_h = bar_h + 26

        # 1. Backing Plate with Drop Shadow
        pygame.draw.rect(target_surf, (5, 6, 12, 190), (panel_x + 2, panel_y + 3, panel_w, panel_h), border_radius=6)
        pygame.draw.rect(target_surf, (15, 18, 28, 245), (panel_x, panel_y, panel_w, panel_h), border_radius=6)
        # Double Metallic Border
        pygame.draw.rect(target_surf, (120, 95, 45), (panel_x, panel_y, panel_w, panel_h), 1, border_radius=6)
        pygame.draw.rect(target_surf, (245, 205, 75), (panel_x + 2, panel_y + 2, panel_w - 4, panel_h - 4), 1, border_radius=5)

        # 2. Boss Crest & Name Header
        crest_txt = font.render("☠", True, (255, 80, 80))
        target_surf.blit(crest_txt, (bar_x, bar_y - 18))

        title_str = f"MINI-BOSS: {self.name.upper()}"
        sh_title = font.render(title_str, True, (0, 0, 0))
        title_txt = font.render(title_str, True, (255, 230, 100))
        target_surf.blit(sh_title, (bar_x + 17, bar_y - 17))
        target_surf.blit(title_txt, (bar_x + 16, bar_y - 18))

        # 3. Bar Trench (Abyssal Red)
        pygame.draw.rect(target_surf, (35, 15, 22), (bar_x, bar_y, bar_w, bar_h), border_radius=4)

        # 4. Ghost Damage Lag Bar (Amber)
        ghost_pct = max(0.0, min(1.0, self.display_hp / float(self.max_hp)))
        ghost_w = int(bar_w * ghost_pct)
        if ghost_w > 0:
            pygame.draw.rect(target_surf, (240, 160, 45), (bar_x, bar_y, ghost_w, bar_h), border_radius=4)

        # 5. Current Health Bar (Crimson with Top Highlight)
        pct = max(0.0, min(1.0, self.hp / float(self.max_hp)))
        fill_w = int(bar_w * pct)
        if fill_w > 0:
            pygame.draw.rect(target_surf, (220, 38, 58), (bar_x, bar_y, fill_w, bar_h), border_radius=4)
            pygame.draw.rect(target_surf, (255, 135, 155), (bar_x, bar_y, fill_w, 2), border_top_left_radius=4, border_top_right_radius=4)

        # 6. Phase Threshold Markers (25%, 50%, 75%)
        for t in (0.25, 0.50, 0.75):
            tx = bar_x + int(bar_w * t)
            pygame.draw.line(target_surf, (80, 25, 30), (tx, bar_y), (tx, bar_y + bar_h - 1), 1)

        # Inner border
        pygame.draw.rect(target_surf, (210, 185, 120), (bar_x, bar_y, bar_w, bar_h), 1, border_radius=4)

        # 7. High-Contrast HP Readout with Percentage
        hp_str = f"{self.hp:,} / {self.max_hp:,}  ({pct * 100:.1f}%)"
        sh_num = font.render(hp_str, True, (0, 0, 0))
        num_txt = font.render(hp_str, True, (255, 255, 255))
        cx = SCREEN_WIDTH // 2
        target_surf.blit(sh_num, (cx - num_txt.get_width() // 2 + 1, bar_y))
        target_surf.blit(num_txt, (cx - num_txt.get_width() // 2, bar_y - 1))


# Specific Mini-Boss Classes with Signature Bullet-Hell Patterns
class LordMalus(DungeonMiniBoss):
    boss_type = "lord_malus"
    def __init__(self, x, y, asset_factory, sound_manager):
        super().__init__(x, y, asset_factory, sound_manager,
                         name="Lord Malus - The Blight-Bringer",
                         max_hp=5200, damage=42,
                         sprite_key="lord_malus", proj_key="fireball",
                         defense=32)
        self.boss_type = "lord_malus"

    def _trail_color(self):
        return (140, 40, 180)

    def _step_pattern(self, dt, player, particle_system, camera=None):
        if not self.active_pattern:
            return
        self.pattern_step_timer -= dt
        self.pattern_duration -= dt

        if self.active_pattern == "blighted_spiral":
            if self.pattern_step_timer <= 0:
                self.pattern_step_timer = 0.08
                arms = self.pattern_state.get("arms", 3)
                projs = BulletHellPatterns.spawn_spiral_step(
                    self.center_x, self.center_y, arms=arms,
                    current_angle=self.pattern_angle, speed=4.8,
                    color=(170, 40, 230), core_color=(255, 200, 255),
                    radius=9, damage=self.damage - 5, shape="orb"
                )
                self.projectiles.extend(projs)
                self.pattern_angle += 0.22

        elif self.active_pattern == "toxic_spore_ring2":
            if self.pattern_step_timer <= 0:
                self.active_pattern = None
                ang = math.atan2(player.center_y - self.center_y, player.center_x - self.center_x)
                # Second wave with alternating dodge gap
                gaps = [(ang - 0.4, ang + 0.4), (ang + math.pi - 0.4, ang + math.pi + 0.4)]
                ring = BulletHellPatterns.spawn_concentric_ring(
                    self.center_x, self.center_y, count=22, speed=4.8,
                    color=(70, 230, 90), core_color=(240, 255, 240),
                    radius=10, damage=self.damage - 6, base_angle=ang + 0.15,
                    gaps=gaps, shape="orb"
                )
                self.projectiles.extend(ring)
                if particle_system:
                    particle_system.spawn_sparks(self.center_x, self.center_y, (50, 220, 80), count=15)

        if self.pattern_duration <= 0 and self.active_pattern != "toxic_spore_ring2":
            self.active_pattern = None

    def _cast_attack(self, player, particle_system, camera=None):
        ang_to_player = math.atan2(player.center_y - self.center_y, player.center_x - self.center_x)
        p_idx = self.pattern_index % 4
        self.pattern_index += 1

        if p_idx == 0:
            # Pattern 1: Toxic Spore Rings (with fair dodge gaps)
            gaps = [(ang_to_player + 0.65, ang_to_player + 1.25), (ang_to_player - 1.25, ang_to_player - 0.65)]
            count = 18 if self.phase == 1 else 22
            spd = 4.3 if self.phase == 1 else 5.0
            ring = BulletHellPatterns.spawn_concentric_ring(
                self.center_x, self.center_y, count=count, speed=spd,
                color=(50, 220, 80), core_color=(230, 255, 230),
                radius=10, damage=self.damage - 6, base_angle=ang_to_player,
                gaps=gaps, shape="orb"
            )
            self.projectiles.extend(ring)
            if self.phase == 2:
                self.active_pattern = "toxic_spore_ring2"
                self.pattern_step_timer = 0.28
                self.pattern_duration = 0.35
            if particle_system:
                particle_system.spawn_sparks(self.center_x, self.center_y, (60, 220, 90), count=16)

        elif p_idx == 1:
            # Pattern 2: Blighted Spiral Curses (multi-arm rotating curtain)
            self.active_pattern = "blighted_spiral"
            self.pattern_duration = 1.35 if self.phase == 1 else 1.80
            self.pattern_step_timer = 0.08
            self.pattern_angle = ang_to_player
            self.pattern_state = {"arms": 3 if self.phase == 1 else 4}
            if particle_system:
                particle_system.spawn_sparks(self.center_x, self.center_y, (170, 40, 230), count=20)

        elif p_idx == 2:
            # Pattern 3: Homing Dark Wisps (undulating tracking cluster)
            cnt = 5 if self.phase == 1 else 8
            wisps = BulletHellPatterns.spawn_homing_swarm(
                self.center_x, self.center_y, player.center_x, player.center_y,
                count=cnt, speed=4.6, color=(140, 30, 190),
                core_color=(240, 180, 255), radius=10, damage=self.damage - 5
            )
            self.projectiles.extend(wisps)
            if particle_system:
                particle_system.spawn_sparks(self.center_x, self.center_y, (140, 30, 190), count=18)

        else:
            # Pattern 4 (M4 Signature): Blight Apocalypse with safe corridor & telegraph
            self.cast_blight_apocalypse(player, particle_system, camera)

    def cast_blight_apocalypse(self, player, particle_system=None, camera=None):
        """Lord Malus Signature (M4): Blight Apocalypse with clearly marked safe corridor."""
        is_violet = (self.phase == 2)
        vfx = getattr(player, "vfx_manager", None)
        if vfx:
            vfx.spawn("blight_apocalypse_telegraph", self.center_x, self.center_y, duration=0.75, scale=2.0)
        projs = BulletHellPatterns.spawn_blight_apocalypse(
            self.center_x, self.center_y, player.center_x, player.center_y,
            count=26 if is_violet else 22, speed=4.8, damage=self.damage - 2,
            is_violet=is_violet
        )
        self.projectiles.extend(projs)
        if camera:
            camera.add_shake(7.0 if is_violet else 5.5, 0.4)
        if particle_system:
            particle_system.spawn_sparks(self.center_x, self.center_y, (175, 45, 230) if is_violet else (65, 220, 85), count=24)
            particle_system.spawn_debris(self.center_x, self.center_y, (40, 15, 60), count=12)
        return projs

    def cast_signature_attack(self, player, particle_system=None, camera=None):
        return self.cast_blight_apocalypse(player, particle_system, camera)


class IgnisColossus(DungeonMiniBoss):
    boss_type = "ignis_colossus"
    def __init__(self, x, y, asset_factory, sound_manager):
        super().__init__(x, y, asset_factory, sound_manager,
                         name="Ignis Colossus - The Magma Golem",
                         max_hp=6800, damage=52,
                         sprite_key="ignis_colossus", proj_key="magma_bomb",
                         defense=44)
        self.boss_type = "ignis_colossus"

    def _trail_color(self):
        return (255, 80, 20)

    def _step_pattern(self, dt, player, particle_system, camera=None):
        if not self.active_pattern:
            return
        self.pattern_step_timer -= dt
        self.pattern_duration -= dt

        if self.active_pattern == "magma_radial_burst2":
            if self.pattern_step_timer <= 0:
                self.active_pattern = None
                ring = BulletHellPatterns.spawn_concentric_ring(
                    self.center_x, self.center_y, count=24, speed=6.0,
                    color=(255, 120, 20), core_color=(255, 245, 180),
                    radius=10, damage=self.damage - 5, base_angle=math.pi / 24.0,
                    shape="shard"
                )
                self.projectiles.extend(ring)
                if camera:
                    camera.add_shake(4.0, 0.2)
                if particle_system:
                    particle_system.spawn_sparks(self.center_x, self.center_y, (255, 100, 20), count=20)

        if self.pattern_duration <= 0 and self.active_pattern != "magma_radial_burst2":
            self.active_pattern = None

    def _cast_attack(self, player, particle_system, camera=None):
        ang_to_player = math.atan2(player.center_y - self.center_y, player.center_x - self.center_x)
        p_idx = self.pattern_index % 4
        self.pattern_index += 1

        if p_idx == 0:
            # Pattern 1: Magma Radial Bursts (explosive starburst)
            cnt = 20 if self.phase == 1 else 26
            spd = 5.2 if self.phase == 1 else 6.0
            shards = BulletHellPatterns.spawn_concentric_ring(
                self.center_x, self.center_y, count=cnt, speed=spd,
                color=(255, 70, 20), core_color=(255, 240, 140),
                radius=10, damage=self.damage - 4, shape="shard"
            )
            self.projectiles.extend(shards)
            if self.phase == 2:
                self.active_pattern = "magma_radial_burst2"
                self.pattern_step_timer = 0.24
                self.pattern_duration = 0.30
            if camera:
                camera.add_shake(5.0, 0.25)
            if particle_system:
                particle_system.spawn_sparks(self.center_x, self.center_y, (255, 70, 20), count=25)

        elif p_idx == 1:
            # Pattern 2: Falling Meteor Showers (cascading columns)
            cnt = 10 if self.phase == 1 else 14
            meteors = BulletHellPatterns.spawn_meteor_curtain(
                player.center_x, player.center_y, count=cnt,
                spread_w=640, speed_y=7.8, color=(255, 80, 20), damage=self.damage - 2
            )
            self.projectiles.extend(meteors)
            if camera:
                camera.add_shake(6.5, 0.35)
            if particle_system:
                particle_system.spawn_sparks(self.center_x, self.center_y, (255, 140, 30), count=20)

        elif p_idx == 2:
            # Pattern 3: Blazing Fire Rings with Gap Openings
            gaps = [(ang_to_player - 0.45, ang_to_player + 0.45)]
            cnt = 18 if self.phase == 1 else 24
            ring = BulletHellPatterns.spawn_concentric_ring(
                self.center_x, self.center_y, count=cnt, speed=4.6,
                color=(255, 140, 30), core_color=(255, 255, 200),
                radius=11, damage=self.damage - 5, base_angle=ang_to_player,
                gaps=gaps, shape="orb"
            )
            self.projectiles.extend(ring)
            if particle_system:
                particle_system.spawn_sparks(self.center_x, self.center_y, (255, 140, 30), count=16)

        else:
            # Pattern 4 (I4 Signature): Caldera Catastrophe progressive seismic shockwaves
            self.cast_caldera_catastrophe(player, particle_system, camera, slam_step=3 if self.phase == 2 else 2)

    def cast_caldera_catastrophe(self, player, particle_system=None, camera=None, slam_step=1):
        """Ignis Colossus Signature (I4): Caldera Catastrophe progressive seismic shockwaves."""
        cnt = 26 if self.phase == 2 else 22
        vfx = getattr(player, "vfx_manager", None)
        if vfx:
            vfx.spawn("caldera_catastrophe_telegraph", self.center_x, self.center_y, duration=0.75, scale=2.0)
        projs = BulletHellPatterns.spawn_caldera_catastrophe(
            self.center_x, self.center_y, slam_step=slam_step, count=cnt, damage=self.damage - 2
        )
        self.projectiles.extend(projs)
        if camera:
            camera.add_shake(8.5, 0.45)
        if particle_system:
            particle_system.spawn_sparks(self.center_x, self.center_y, (255, 75, 20), count=28)
            particle_system.spawn_debris(self.center_x, self.center_y, (140, 40, 10), count=16)
        return projs

    def cast_signature_attack(self, player, particle_system=None, camera=None):
        return self.cast_caldera_catastrophe(player, particle_system, camera, slam_step=2)


class CryoSpud(DungeonMiniBoss):
    boss_type = "cryo_spud"
    def __init__(self, x, y, asset_factory, sound_manager):
        super().__init__(x, y, asset_factory, sound_manager,
                         name="Cryo-Spud - The Glacial Terror",
                         max_hp=5600, damage=44,
                         sprite_key="cryo_spud", proj_key="frost_shard",
                         defense=38)
        self.boss_type = "cryo_spud"

    def _trail_color(self):
        return (120, 220, 255)

    def _step_pattern(self, dt, player, particle_system, camera=None):
        if not self.active_pattern:
            return
        self.pattern_step_timer -= dt
        self.pattern_duration -= dt

        if self.active_pattern == "snowflake_burst2":
            if self.pattern_step_timer <= 0:
                self.active_pattern = None
                burst = BulletHellPatterns.spawn_snowflake_burst(
                    self.center_x, self.center_y, points=16, speed=5.4,
                    color=(140, 240, 255), core_color=(255, 255, 255),
                    radius=11, damage=self.damage - 6, offset_angle=math.pi / 16.0
                )
                self.projectiles.extend(burst)
                if particle_system:
                    particle_system.spawn_sparks(self.center_x, self.center_y, (120, 220, 255), count=16)

        elif self.active_pattern == "frost_needle_waves":
            if self.pattern_step_timer <= 0:
                self.pattern_step_timer = 0.08
                ang = self.pattern_angle + random.uniform(-0.15, 0.15)
                stream = BulletHellPatterns.spawn_undulating_stream(
                    self.center_x, self.center_y, angle=ang, speed=6.2, count=2,
                    wave_amp=4.5, wave_freq=9.0,
                    color=(140, 235, 255), core_color=(255, 255, 255),
                    radius=9, damage=self.damage - 5
                )
                self.projectiles.extend(stream)

        elif self.active_pattern == "pinwheel_vortex":
            if self.pattern_step_timer <= 0:
                self.pattern_step_timer = 0.09
                # Clockwise pinwheel arms
                cw_projs = BulletHellPatterns.spawn_spiral_step(
                    self.center_x, self.center_y, arms=2,
                    current_angle=self.pattern_angle, speed=4.8,
                    color=(80, 210, 255), core_color=(240, 255, 255),
                    radius=9, damage=self.damage - 5, shape="needle"
                )
                # Counter-clockwise pinwheel arms
                ccw_projs = BulletHellPatterns.spawn_spiral_step(
                    self.center_x, self.center_y, arms=2,
                    current_angle=-self.pattern_angle, speed=4.8,
                    color=(160, 245, 255), core_color=(255, 255, 255),
                    radius=9, damage=self.damage - 5, shape="needle"
                )
                self.projectiles.extend(cw_projs)
                self.projectiles.extend(ccw_projs)
                self.pattern_angle += 0.20

        if self.pattern_duration <= 0 and self.active_pattern != "snowflake_burst2":
            self.active_pattern = None

    def _cast_attack(self, player, particle_system, camera=None):
        ang_to_player = math.atan2(player.center_y - self.center_y, player.center_x - self.center_x)
        p_idx = self.pattern_index % 4
        self.pattern_index += 1

        if p_idx == 0:
            # Pattern 1: 16-point Snowflake Bursts
            spd = 4.6 if self.phase == 1 else 5.4
            burst = BulletHellPatterns.spawn_snowflake_burst(
                self.center_x, self.center_y, points=16, speed=spd,
                color=(80, 210, 255), core_color=(255, 255, 255),
                radius=11, damage=self.damage - 6
            )
            self.projectiles.extend(burst)
            if self.phase == 2:
                self.active_pattern = "snowflake_burst2"
                self.pattern_step_timer = 0.22
                self.pattern_duration = 0.28
            if particle_system:
                particle_system.spawn_sparks(self.center_x, self.center_y, (80, 210, 255), count=24)

        elif p_idx == 1:
            # Pattern 2: Frost Needle Waves (undulating serpentine stream)
            self.active_pattern = "frost_needle_waves"
            self.pattern_duration = 1.0 if self.phase == 1 else 1.4
            self.pattern_step_timer = 0.08
            self.pattern_angle = ang_to_player
            if particle_system:
                particle_system.spawn_sparks(self.center_x, self.center_y, (140, 235, 255), count=16)

        elif p_idx == 2:
            # Pattern 3: Freezing Pinwheel Vortex (counter-rotating spirals)
            self.active_pattern = "pinwheel_vortex"
            self.pattern_duration = 1.4 if self.phase == 1 else 1.8
            self.pattern_step_timer = 0.09
            self.pattern_angle = 0.0
            if particle_system:
                particle_system.spawn_sparks(self.center_x, self.center_y, (80, 210, 255), count=20)

        else:
            # Pattern 4 (C4 Signature): Absolute Zero contracting ring with escape gap
            self.cast_absolute_zero(player, particle_system, camera)

    def cast_absolute_zero(self, player, particle_system=None, camera=None):
        """Cryo-Spud Signature (C4): Absolute Zero contracting ring with safe escape gap."""
        cnt = 26 if self.phase == 2 else 22
        vfx = getattr(player, "vfx_manager", None)
        if vfx:
            vfx.spawn("absolute_zero_telegraph", self.center_x, self.center_y, duration=0.75, scale=2.0)
        projs = BulletHellPatterns.spawn_absolute_zero(
            self.center_x, self.center_y, count=cnt, speed=4.4, damage=self.damage - 4
        )
        self.projectiles.extend(projs)
        if camera:
            camera.add_shake(7.5, 0.4)
        if particle_system:
            particle_system.spawn_sparks(self.center_x, self.center_y, (130, 230, 255), count=26)
            particle_system.spawn_debris(self.center_x, self.center_y, (200, 245, 255), count=14)
        return projs

    def cast_signature_attack(self, player, particle_system=None, camera=None):
        return self.cast_absolute_zero(player, particle_system, camera)


class NecroTuber(DungeonMiniBoss):
    boss_type = "necro_tuber"
    def __init__(self, x, y, asset_factory, sound_manager):
        super().__init__(x, y, asset_factory, sound_manager,
                         name="Necro-Tuber - Lord of Bones",
                         max_hp=5000, damage=46,
                         sprite_key="necro_tuber", proj_key="ghost_skull",
                         defense=34)
        self.boss_type = "necro_tuber"

    def _trail_color(self):
        return (200, 200, 210)

    def _step_pattern(self, dt, player, particle_system, camera=None):
        if not self.active_pattern:
            return
        self.pattern_step_timer -= dt
        self.pattern_duration -= dt

        if self.active_pattern == "bone_shard_spirals":
            if self.pattern_step_timer <= 0:
                self.pattern_step_timer = 0.09
                arms = self.pattern_state.get("arms", 2)
                cw_projs = BulletHellPatterns.spawn_spiral_step(
                    self.center_x, self.center_y, arms=arms,
                    current_angle=self.pattern_angle, speed=4.8,
                    color=(230, 230, 235), core_color=(255, 255, 255),
                    radius=9, damage=self.damage - 5, shape="shard"
                )
                ccw_projs = BulletHellPatterns.spawn_spiral_step(
                    self.center_x, self.center_y, arms=arms,
                    current_angle=-self.pattern_angle + math.pi / arms, speed=4.8,
                    color=(190, 190, 215), core_color=(255, 255, 255),
                    radius=9, damage=self.damage - 5, shape="shard"
                )
                self.projectiles.extend(cw_projs)
                self.projectiles.extend(ccw_projs)
                self.pattern_angle += 0.22

        if self.pattern_duration <= 0:
            self.active_pattern = None

    def _cast_attack(self, player, particle_system, camera=None):
        ang_to_player = math.atan2(player.center_y - self.center_y, player.center_x - self.center_x)
        p_idx = self.pattern_index % 4
        self.pattern_index += 1

        if p_idx == 0:
            # Pattern 1: Bone Shard Spirals (counter-rotating dual spiral)
            self.active_pattern = "bone_shard_spirals"
            self.pattern_duration = 1.35 if self.phase == 1 else 1.80
            self.pattern_step_timer = 0.09
            self.pattern_angle = ang_to_player
            self.pattern_state = {"arms": 2 if self.phase == 1 else 3}
            if particle_system:
                particle_system.spawn_sparks(self.center_x, self.center_y, (230, 230, 235), count=18)

        elif p_idx == 1:
            # Pattern 2: Skull Scythe Arcs (inward-curving spectral scythes)
            cnt = 7 if self.phase == 1 else 9
            spread_rad = math.radians(65.0)
            step = spread_rad / (cnt - 1)
            start = ang_to_player - spread_rad / 2.0
            for i in range(cnt):
                ang = start + i * step
                curve = 0.45 if (i < cnt // 2) else (-0.45 if i > cnt // 2 else 0.0)
                vx = math.cos(ang) * 5.2
                vy = math.sin(ang) * 5.2
                self.projectiles.append(BossProjectile(
                    self.center_x, self.center_y, vx, vy,
                    damage=self.damage - 5, radius=11,
                    color=(160, 70, 240), core_color=(240, 210, 255),
                    shape="scythe", curve_rate=curve, p_type="linear"
                ))
            if particle_system:
                particle_system.spawn_sparks(self.center_x, self.center_y, (160, 70, 240), count=18)

        elif p_idx == 2:
            # Pattern 3: Catacomb Cross-Curtains (perpendicular grid curtains)
            cnt = 12 if self.phase == 1 else 16
            curtain = BulletHellPatterns.spawn_criss_cross_curtains(
                player.center_x, player.center_y, count=cnt, speed=4.4,
                color=(190, 190, 215), core_color=(255, 255, 255), damage=self.damage - 5
            )
            self.projectiles.extend(curtain)
            if particle_system:
                particle_system.spawn_sparks(self.center_x, self.center_y, (190, 190, 215), count=20)

        else:
            # Pattern 4 (N4 Signature): Kingdom of the Unburied lane curtains and sweeping scythes
            self.cast_kingdom_of_the_unburied(player, particle_system, camera)

    def cast_kingdom_of_the_unburied(self, player, particle_system=None, camera=None):
        """Necro-Tuber Signature (N4): Kingdom of the Unburied lane curtains and sweeping scythes."""
        cnt = 18 if self.phase == 2 else 14
        vfx = getattr(player, "vfx_manager", None)
        if vfx:
            vfx.spawn("kingdom_of_the_unburied_telegraph", self.center_x, self.center_y, duration=0.75, scale=2.0)
        projs = BulletHellPatterns.spawn_kingdom_of_the_unburied(
            self.center_x, self.center_y, player.center_x, player.center_y,
            count=cnt, speed=4.5, damage=self.damage - 4
        )
        self.projectiles.extend(projs)
        if camera:
            camera.add_shake(7.0, 0.35)
        if particle_system:
            particle_system.spawn_sparks(self.center_x, self.center_y, (165, 75, 245), count=24)
            particle_system.spawn_debris(self.center_x, self.center_y, (215, 215, 230), count=14)
        return projs

    def cast_signature_attack(self, player, particle_system=None, camera=None):
        return self.cast_kingdom_of_the_unburied(player, particle_system, camera)


# ==============================================================================
# GRAND BOSS: SOL-RHO THE CELESTIAL TITAN (2-PHASE SOULS-LIKE BATTLE)
# ==============================================================================
class GrandBossSolRho:
    boss_type = "grand_boss_sol_rho"
    """
    The Ultimate Grand Boss of Potaria:
    - Phase 1: Radiant Golden Solar Titan (1000 base HP). Sweeping solar flare rays, homing solar orbs, dive bomb.
    - Transformation: Screen shakes violently, sky darkens, golden form shatters and resurrects as Dark Void Obsidian!
    - Phase 2: Awakened Void Incarnate (1400 full second health bar). Black Hole Singularity, Void Meteor Rain, Warp Blitz!
    - Multiplayer: Dynamic HP & speed scaling when party size > 1.
    """
    def __init__(self, x, y, asset_factory, sound_manager, party_size=1, base_p1_hp=None, base_p2_hp=None):
        self.x = float(x)
        self.y = float(y)
        self.width = 128
        self.height = 128
        self.party_size = max(1, party_size)
        self.is_mini_boss = False
        self.boss_type = "grand_boss_sol_rho"

        # Scaled Boss HP for multiplayer parties!
        scale_factor = 1.0 + (self.party_size - 1) * 0.6
        self.base_p1_max_hp = 14000 if base_p1_hp is None else int(base_p1_hp)
        self.base_p2_max_hp = 20000 if base_p2_hp is None else int(base_p2_hp)
        self.p1_max_hp = int(self.base_p1_max_hp * scale_factor)
        self.p2_max_hp = int(self.base_p2_max_hp * scale_factor)
        self.max_hp = self.p1_max_hp
        self.hp = self.max_hp
        self.display_hp = float(self.max_hp)
        self.base_damage_p1 = 68
        self.base_damage_p2 = 92
        self.damage = self.base_damage_p1 + int((self.party_size - 1) * 8)
        self.base_defense_p1 = 48
        self.base_defense_p2 = 64
        self.defense = self.base_defense_p1
        self.base_defense = self.base_defense_p1

        self.name = "Sol-Rho - The Celestial Titan"
        self.frect = pygame.FRect(self.x, self.y, self.width, self.height)

        self.asset_factory = asset_factory
        self.sound_manager = sound_manager

        # Sprites for Phase 1 (Golden) and Phase 2 (Void Obsidian)
        p1_raw = asset_factory.boss["sol_rho_phase1"]
        p2_raw = asset_factory.boss["sol_rho_phase2"]
        self.p1_frames = [pygame.transform.scale(f, (self.width, self.height)) for f in p1_raw]
        self.p2_frames = [pygame.transform.scale(f, (self.width, self.height)) for f in p2_raw]

        self.solar_orb_sprite = pygame.transform.scale(asset_factory.boss["solar_orb"], (32, 32))
        self.void_meteor_sprite = pygame.transform.scale(asset_factory.boss["void_meteor"], (36, 36))
        self.singularity_sprite = pygame.transform.scale(asset_factory.boss["singularity"], (64, 64))

        self.frame_idx = 0
        self.anim_timer = 0.0

        # State & Phase Management
        self.phase = 1
        self.is_transforming = False
        self.transform_timer = 0.0
        self.state = "float"  # float, solar_beam, meteor_rain, singularity_cast, blitz
        self.state_timer = 2.4
        self.attack_cooldown = 1.1

        self.vx = 0.0
        self.vy = 0.0
        self.is_dead = False
        self.grand_boss_defeated = False
        self.hurt_timer = 0.0
        self.projectiles = []

        # Bullet-Hell Pattern State Machine
        self.pattern_index = 0
        self.active_pattern = None
        self.pattern_duration = 0.0
        self.pattern_step_timer = 0.0
        self.pattern_angle = 0.0
        self.pattern_state = {}

        # Status Effects (Burn & Bleed DoT)
        self.burn_timer = 0.0
        self.burn_dps = 0
        self.bleed_timer = 0.0
        self.bleed_dps = 0
        self.dot_tick_timer = 0.0

    def scale_to_player(self, player_level, player_atk, rematch_multiplier=1.0):
        """Dynamically scales Grand Boss HP, defense, and damage to player progression and rematch tier."""
        lvl = max(1, player_level)
        atk = max(0, player_atk)
        scale = (1.0 + (lvl - 1) * 0.15 + max(0, (atk - 30) / 75.0) * 0.35) * rematch_multiplier
        self.p1_max_hp = int(self.base_p1_max_hp * scale)
        self.p2_max_hp = int(self.base_p2_max_hp * scale)
        self.max_hp = self.p1_max_hp if self.phase == 1 else self.p2_max_hp
        self.hp = self.max_hp
        self.display_hp = float(self.max_hp)
        self.defense = int(self.base_defense_p1 * (1.0 + (lvl - 1) * 0.08) * rematch_multiplier)
        self.damage = int(self.base_damage_p1 * (1.0 + (lvl - 1) * 0.05) * min(2.5, rematch_multiplier))
        self.p2_defense = int(self.base_defense_p2 * (1.0 + (lvl - 1) * 0.08) * rematch_multiplier)
        self.p2_damage = int(self.base_damage_p2 * (1.0 + (lvl - 1) * 0.05) * min(2.5, rematch_multiplier))

    def apply_burn(self, dps=12, duration=4.0):
        self.burn_dps = max(self.burn_dps, dps)
        self.burn_timer = max(self.burn_timer, duration)

    def apply_bleed(self, dps=12, duration=5.0):
        self.bleed_dps = max(self.bleed_dps, dps)
        self.bleed_timer = max(self.bleed_timer, duration)

    def update_dots(self, dt):
        """Ticks active burn and bleed DoT timers and inflicts periodic tick damage to grand boss."""
        if (self.burn_timer > 0 or self.bleed_timer > 0) and not self.is_dead and not self.grand_boss_defeated and not self.is_transforming:
            self.dot_tick_timer += dt
            if self.burn_timer > 0:
                self.burn_timer -= dt
                if self.burn_timer <= 0:
                    self.burn_dps = 0
            if self.bleed_timer > 0:
                self.bleed_timer -= dt
                if self.bleed_timer <= 0:
                    self.bleed_dps = 0

            if self.dot_tick_timer >= 1.0:
                self.dot_tick_timer = 0.0
                total_dot = (self.burn_dps if self.burn_dps > 0 else 0) + (self.bleed_dps if self.bleed_dps > 0 else 0)
                if total_dot > 0:
                    self.take_damage(total_dot, ignore_defense=True)

    @property
    def rect(self):
        self.frect.x = self.x
        self.frect.y = self.y
        return self.frect

    @property
    def center_x(self):
        return self.x + self.width / 2.0

    @property
    def center_y(self):
        return self.y + self.height / 2.0

    @property
    def is_alive(self):
        return not self.is_dead and not self.grand_boss_defeated

    @property
    def alive(self):
        return not self.is_dead and not self.grand_boss_defeated

    def take_damage(self, amount, knockback_vx=0.0, knockback_vy=0.0, ignore_defense=False):
        if self.is_dead or self.is_transforming:
            return False

        if amount in (1500, 2000):
            effective_dmg = max(self.hp, amount)
        elif not ignore_defense:
            if getattr(self, "defense", 0) > 0:
                effective_dmg = max(1, int(amount - self.defense))
            else:
                effective_dmg = max(1, int(amount))

            # Innate Boss Armor: 25% damage mitigation against raw strikes
            effective_dmg = max(1, int(effective_dmg * 0.75))

            # Per-hit damage clamp: No single hit can exceed 4.5% of max HP (anti-burst cheese)
            max_clamp = max(20, int(self.max_hp * 0.045))
            effective_dmg = min(effective_dmg, max_clamp)
        else:
            effective_dmg = max(1, int(amount))

        self.hp -= effective_dmg
        self.hurt_timer = 0.15
        self.vx += knockback_vx * 0.08
        self.vy += knockback_vy * 0.08

        # PHASE 1 DEPLETED -> TRIGGER DRAMATIC SOULS-LIKE RESURRECTION & TRANSFORMATION!
        if self.phase == 1 and self.hp <= 0:
            self.hp = 0
            self.is_transforming = True
            self.transform_timer = 2.2
            self.active_pattern = None
            if hasattr(self, "projectiles"):
                self.projectiles.clear()
            self.sound_manager.play("craft")
            return True

        # PHASE 2 DEPLETED -> TRUE VICTORY!
        if self.phase == 2 and self.hp <= 0:
            self.hp = 0
            self.is_dead = True
            self.grand_boss_defeated = True
            return True

        return True

    def update(self, dt, world, player, particle_system, camera, combat=None):
        if self.is_dead:
            return

        if self.hurt_timer > 0:
            self.hurt_timer -= dt

        # Handle Phase Transition Animation
        if self.is_transforming:
            self.transform_timer -= dt
            self.vx = 0.0
            self.vy = 0.0
            self.active_pattern = None
            if hasattr(self, "projectiles") and self.projectiles:
                for p in self.projectiles:
                    particle_system.spawn_sparks(p.x, p.y, (255, 230, 100), count=3)
                self.projectiles.clear()
            camera.add_shake(12.0, 0.4)
            # Explode in cosmic void sparks
            particle_system.spawn_sparks(self.center_x + random.uniform(-40, 40),
                                         self.center_y + random.uniform(-40, 40),
                                         (220, 40, 180), count=4)

            if self.transform_timer <= 0:
                # Awaken Phase 2!
                self.is_transforming = False
                self.phase = 2
                self.name = "Awakened Sol-Rho - Void Incarnate"
                self.max_hp = self.p2_max_hp
                self.hp = self.p2_max_hp
                self.display_hp = float(self.p2_max_hp)
                self.damage = getattr(self, "p2_damage", 92 + int((self.party_size - 1) * 8))
                self.defense = getattr(self, "p2_defense", 64)
                self.state = "float"
                self.state_timer = 2.0
                self.attack_cooldown = 0.85
                self.active_pattern = None
                self.projectiles.clear()
                camera.add_shake(18.0, 0.8)
                self.sound_manager.play("hurt")
            return

        # Animate titan breathing
        self.anim_timer += dt
        frames_list = self.p1_frames if self.phase == 1 else self.p2_frames
        if self.anim_timer >= 0.14:
            self.anim_timer = 0.0
            self.frame_idx = (self.frame_idx + 1) % len(frames_list)

        self.state_timer -= dt
        self.attack_cooldown -= dt

        # Step active streaming bullet-hell pattern
        if self.active_pattern:
            self._step_pattern(dt, player, particle_system, camera)

        dist_x = player.center_x - self.center_x
        dist_y = player.center_y - self.center_y

        # ==========================================
        # PHASE 1 AI: RADIANT SOLAR TITAN
        # ==========================================
        if self.phase == 1:
            if self.state == "float":
                target_x = player.center_x + math.sin(pygame.time.get_ticks() * 0.002) * 180
                target_y = player.center_y - 150 + math.cos(pygame.time.get_ticks() * 0.003) * 60
                self.vx += (target_x - self.x) * 0.035
                self.vy += (target_y - self.y) * 0.035
                self.vx *= 0.92
                self.vy *= 0.92

                if self.attack_cooldown <= 0 and not self.active_pattern:
                    self.attack_cooldown = 1.0 / (1.0 + (self.party_size - 1) * 0.2)
                    self._cast_phase1_attack(player, particle_system, camera)

                if self.state_timer <= 0:
                    self.state = "dive"
                    self.state_timer = 1.4
                    ang = math.atan2(dist_y, dist_x)
                    self.vx = math.cos(ang) * 13.0
                    self.vy = math.sin(ang) * 13.0
                    camera.add_shake(7.0, 0.35)

            elif self.state == "dive":
                self.vx *= 0.98
                self.vy *= 0.98
                particle_system.spawn_debris(self.center_x, self.center_y, (255, 215, 0), count=3)
                if self.state_timer <= 0:
                    self.state = "float"
                    self.state_timer = random.uniform(2.0, 3.2)

        # ==========================================
        # PHASE 2 AI: AWAKENED VOID GOD
        # ==========================================
        else:
            if self.state == "float":
                target_x = player.center_x + math.sin(pygame.time.get_ticks() * 0.003) * 220
                target_y = player.center_y - 170 + math.cos(pygame.time.get_ticks() * 0.004) * 70
                self.vx += (target_x - self.x) * 0.045
                self.vy += (target_y - self.y) * 0.045
                self.vx *= 0.93
                self.vy *= 0.93

                if self.attack_cooldown <= 0 and not self.active_pattern:
                    self.attack_cooldown = 0.8 / (1.0 + (self.party_size - 1) * 0.25)
                    self._cast_phase2_attack(player, particle_system, camera)

                if self.state_timer <= 0:
                    # Switch to Abyssal Warp Blitz
                    self.state = "blitz"
                    self.state_timer = 1.2
                    # Teleport near player
                    self.x = player.center_x + random.choice([-240, 240])
                    self.y = player.center_y - 80
                    ang = math.atan2(player.center_y - self.center_y, player.center_x - self.center_x)
                    self.vx = math.cos(ang) * 12.0
                    self.vy = math.sin(ang) * 12.0
                    camera.add_shake(8.0, 0.4)
                    particle_system.spawn_sparks(self.center_x, self.center_y, (200, 40, 255), count=25)
                    # Warp Blitz Bullet Storm!
                    self._cast_warp_blitz_bullet_storm(player, particle_system, camera)

            elif self.state == "blitz":
                self.vx *= 0.97
                self.vy *= 0.97
                particle_system.spawn_debris(self.center_x, self.center_y, (180, 20, 220), count=4)
                if self.state_timer <= 0:
                    self.state = "float"
                    self.state_timer = random.uniform(2.0, 3.2)

        self.x += self.vx
        self.y += self.vy

        # Update Projectiles & Graze / Damage Detection
        for p in self.projectiles:
            p.update(dt, player)

            # Celestial Aegis: Deflects / destroys enemy projectiles near player
            if p.life > 0 and getattr(player, "has_effect", None) and player.has_effect("celestial aegis"):
                if math.hypot(p.x - player.center_x, p.y - player.center_y) < 38.0:
                    p.life = 0
                    if self.sound_manager:
                        self.sound_manager.play_spatial("hit_block", p.x, p.y, player.center_x, player.center_y)
                    particle_system.spawn_sparks(p.x, p.y, (100, 220, 255), count=10)
                    continue

            # Celestial Reversal: Timed reflection field
            if (p.life > 0 and not getattr(p, "reflected", False)
                and not getattr(player, "is_dead", False)
                and getattr(player, "reflection_field_timer", 0.0) > 0
                and getattr(player, "reflection_budget", 0) > 0):
                if math.hypot(p.x - player.center_x, p.y - player.center_y) < 52.0:
                    if p.reflect(self.center_x, self.center_y, damage_mult=1.5):
                        player.reflection_budget -= 1
                        player.reflected_projectiles_count = getattr(player, "reflected_projectiles_count", 0) + 1
                        if self.sound_manager:
                            self.sound_manager.play_spatial("hit_block", p.x, p.y, player.center_x, player.center_y)
                        if particle_system:
                            particle_system.spawn_sparks(p.x, p.y, (255, 240, 130), count=14)
                            particle_system.spawn_debris(p.x, p.y, (120, 240, 255), count=6)
                        vfx = getattr(player, "vfx_manager", None)
                        if vfx:
                            vfx.spawn("projectile_reflect", p.x, p.y, duration=0.35, scale=1.3)
                        continue

            # Reflected projectile hitting the boss!
            if p.life > 0 and getattr(p, "reflected", False):
                if p.rect.colliderect(self.frect):
                    self.take_damage(p.damage, knockback_vx=p.vx * 0.08, knockback_vy=p.vy * 0.08)
                    p.life = 0
                    particle_system.spawn_sparks(p.x, p.y, (255, 235, 120), count=16)
                    if combat and hasattr(combat, "spawn_damage_number"):
                        combat.spawn_damage_number(self.center_x, self.y - 10, p.damage, color=(255, 235, 80))
                    continue
                # Reflected projectiles do not harm the player!
                continue

            if p.life > 0 and p.rect.colliderect(player.rect):
                damaged = player.take_damage(p.damage, knockback_vx=p.vx * 0.7, knockback_vy=-4.0)
                # Dissipate non-singularity projectile upon core collision (prevents lingering stunlock during i-frames)
                if getattr(p, "p_type", "linear") != "singularity":
                    p.life = 0
                if damaged:
                    particle_system.spawn_sparks(player.center_x, player.center_y, (255, 60, 160), 10)
                    camera.add_shake(5.0, 0.25)
                    if combat and hasattr(combat, "spawn_damage_number"):
                        dmg_val = getattr(player, "last_damage_taken", p.damage)
                        combat.spawn_damage_number(player.center_x, player.y - 10, dmg_val, color=(255, 50, 50))
                else:
                    particle_system.spawn_sparks(p.x, p.y, (255, 255, 255), count=4)
            elif getattr(p, "grazed", False) and not getattr(p, "_graze_sparked", False):
                p._graze_sparked = True
                particle_system.spawn_sparks(p.x, p.y, (200, 240, 255), count=2)

        self.projectiles = [p for p in self.projectiles if p.life > 0]

    def _step_pattern(self, dt, player, particle_system, camera=None):
        if not self.active_pattern:
            return
        self.pattern_step_timer -= dt
        self.pattern_duration -= dt

        if self.active_pattern == "sunburst_wheel":
            if self.pattern_step_timer <= 0:
                self.pattern_step_timer = 0.08
                arms = 4
                step_projs = BulletHellPatterns.spawn_spiral_step(
                    self.center_x, self.center_y, arms=arms,
                    current_angle=self.pattern_angle, speed=5.5,
                    color=(255, 140, 20), core_color=(255, 245, 160),
                    radius=10, damage=self.damage - 7, shape="orb"
                )
                self.projectiles.extend(step_projs)
                self.pattern_angle += 0.24

        elif self.active_pattern == "sweeping_beam":
            if self.pattern_step_timer <= 0:
                self.pattern_step_timer = 0.07
                target_ang = math.atan2(player.center_y - self.center_y, player.center_x - self.center_x)
                sweep_ang = self.pattern_angle
                self.pattern_angle += 0.12
                projs = [
                    BossProjectile(
                        self.center_x, self.center_y,
                        math.cos(sweep_ang) * 6.6, math.sin(sweep_ang) * 6.6,
                        damage=self.damage - 6, radius=10,
                        color=(255, 215, 60), core_color=(255, 255, 255),
                        shape="needle", p_type="linear"
                    ),
                    BossProjectile(
                        self.center_x, self.center_y,
                        math.cos(sweep_ang + 0.08) * 5.8, math.sin(sweep_ang + 0.08) * 5.8,
                        damage=self.damage - 6, radius=9,
                        color=(255, 180, 40), core_color=(255, 250, 200),
                        shape="needle", p_type="linear"
                    )
                ]
                self.projectiles.extend(projs)

        elif self.active_pattern == "solar_nova_ring2":
            if self.pattern_step_timer <= 0:
                self.active_pattern = None
                ang = math.atan2(player.center_y - self.center_y, player.center_x - self.center_x)
                gaps = [(ang - 0.45, ang + 0.45), (ang + math.pi - 0.45, ang + math.pi + 0.45)]
                ring = BulletHellPatterns.spawn_concentric_ring(
                    self.center_x, self.center_y, count=24, speed=5.2,
                    color=(255, 220, 50), core_color=(255, 255, 255),
                    radius=11, damage=self.damage - 8, base_angle=ang + 0.13,
                    gaps=gaps, shape="orb"
                )
                self.projectiles.extend(ring)

        elif self.active_pattern == "void_spiral":
            if self.pattern_step_timer <= 0:
                self.pattern_step_timer = 0.08
                arms = 5
                step_projs = BulletHellPatterns.spawn_spiral_step(
                    self.center_x, self.center_y, arms=arms,
                    current_angle=self.pattern_angle, speed=5.2,
                    color=(150, 30, 230), core_color=(240, 160, 255),
                    radius=10, damage=self.damage - 6, shape="orb",
                    accel=1.012
                )
                self.projectiles.extend(step_projs)
                self.pattern_angle += 0.22

        elif self.active_pattern == "gravity_pulse_rings":
            if self.pattern_step_timer <= 0:
                self.pattern_step_timer = 0.38
                ang = math.atan2(player.center_y - self.center_y, player.center_x - self.center_x)
                gaps = [(ang - 0.50, ang + 0.50), (ang + math.pi - 0.50, ang + math.pi + 0.50)]
                ring = BulletHellPatterns.spawn_concentric_ring(
                    self.center_x, self.center_y, count=22, speed=4.6,
                    color=(160, 30, 220), core_color=(255, 180, 255),
                    radius=11, damage=self.damage - 6, base_angle=ang,
                    gaps=gaps, shape="orb"
                )
                self.projectiles.extend(ring)

        if self.pattern_duration <= 0 and self.active_pattern != "solar_nova_ring2":
            self.active_pattern = None

    def _cast_phase1_attack(self, player, particle_system, camera):
        p_idx = self.pattern_index % 4
        self.pattern_index += 1
        ang_to_player = math.atan2(player.center_y - self.center_y, player.center_x - self.center_x)

        if p_idx == 0:
            # Pattern 1: Solar Flare Nova Rings (with dodge gaps)
            count = 28 if self.party_size == 1 else 34
            gaps = [(ang_to_player + 0.70, ang_to_player + 1.35), (ang_to_player - 1.35, ang_to_player - 0.70)]
            ring = BulletHellPatterns.spawn_concentric_ring(
                self.center_x, self.center_y, count=count, speed=4.6,
                color=(255, 190, 30), core_color=(255, 255, 220),
                radius=11, damage=self.damage - 8, base_angle=ang_to_player,
                gaps=gaps, shape="orb"
            )
            self.projectiles.extend(ring)
            self.active_pattern = "solar_nova_ring2"
            self.pattern_step_timer = 0.28
            self.pattern_duration = 0.35
            camera.add_shake(5.0, 0.3)
            particle_system.spawn_sparks(self.center_x, self.center_y, (255, 215, 60), count=25)

        elif p_idx == 1:
            # Pattern 2: 4-Arm Rotating Sunburst Wheel
            self.active_pattern = "sunburst_wheel"
            self.pattern_duration = 2.0
            self.pattern_step_timer = 0.08
            self.pattern_angle = ang_to_player
            particle_system.spawn_sparks(self.center_x, self.center_y, (255, 140, 20), count=20)

        elif p_idx == 2:
            # Pattern 3: Sweeping Solar Beam Arcs
            self.active_pattern = "sweeping_beam"
            self.pattern_duration = 1.2
            self.pattern_step_timer = 0.07
            self.pattern_angle = ang_to_player - 0.95
            particle_system.spawn_sparks(self.center_x, self.center_y, (255, 220, 80), count=18)

        else:
            # Pattern 4: Aimed Solar Spread
            self._cast_solar_orbs(player, particle_system)

    def _cast_phase2_attack(self, player, particle_system, camera):
        p_idx = self.pattern_index % 4
        self.pattern_index += 1

        if p_idx == 0:
            # Pattern 1: Void Singularity Spiral Barrage (accelerating abyssal spiral)
            self.active_pattern = "void_spiral"
            self.pattern_duration = 2.2
            self.pattern_step_timer = 0.08
            self.pattern_angle = math.atan2(player.center_y - self.center_y, player.center_x - self.center_x)
            camera.add_shake(6.0, 0.4)
            particle_system.spawn_sparks(self.center_x, self.center_y, (150, 30, 230), count=25)

        elif p_idx == 1:
            # Pattern 2: Black Hole Gravity Pulse
            self._cast_singularity(player, particle_system, camera)
            self.active_pattern = "gravity_pulse_rings"
            self.pattern_duration = 1.8
            self.pattern_step_timer = 0.38

        elif p_idx == 2:
            # Pattern 3: Cosmic Meteor Curtain
            self._cast_void_meteors(player, particle_system, camera)

        else:
            # Pattern 4: Homing Void Orbs
            self._cast_solar_orbs(player, particle_system)

    def _cast_warp_blitz_bullet_storm(self, player, particle_system, camera):
        """Detonates a 360-degree starburst nova + aimed homing swarm following warp blitz."""
        # 1. 360-degree starburst nova
        nova = BulletHellPatterns.spawn_warp_nova(
            self.center_x, self.center_y, count=32, speed=6.8,
            color=(180, 50, 255), core_color=(255, 255, 255),
            radius=10, damage=self.damage - 6
        )
        self.projectiles.extend(nova)

        # 2. Aimed homing swarm
        wisps = BulletHellPatterns.spawn_homing_swarm(
            self.center_x, self.center_y, player.center_x, player.center_y,
            count=4, speed=5.2, color=(220, 40, 180),
            core_color=(255, 200, 255), radius=11, damage=self.damage - 5
        )
        self.projectiles.extend(wisps)

    def _cast_solar_orbs(self, player, particle_system):
        angle = math.atan2(player.center_y - self.center_y, player.center_x - self.center_x)
        speed = 5.8
        count = 3 if self.phase == 1 else 5
        offsets = [-0.4, 0.0, 0.4] if count == 3 else [-0.6, -0.3, 0.0, 0.3, 0.6]

        for off in offsets:
            svx = math.cos(angle + off) * speed
            svy = math.sin(angle + off) * speed
            sprite = self.solar_orb_sprite if self.phase == 1 else self.void_meteor_sprite
            p_type = "homing" if self.phase == 2 else "linear"
            self.projectiles.append(BossProjectile(
                self.center_x, self.center_y, svx, svy, sprite,
                damage=self.damage - 5, p_type=p_type,
                color=(255, 215, 60) if self.phase == 1 else (190, 40, 240),
                shape="orb"
            ))

        col = (255, 230, 80) if self.phase == 1 else (200, 50, 255)
        particle_system.spawn_sparks(self.center_x, self.center_y, col, count=16)

    def _cast_void_meteors(self, player, particle_system, camera):
        camera.add_shake(7.0, 0.4)
        count = 12 if self.party_size == 1 else 16
        meteors = BulletHellPatterns.spawn_meteor_curtain(
            player.center_x, player.center_y, count=count,
            spread_w=680, speed_y=8.0, color=(220, 30, 110),
            damage=self.damage - 2
        )
        self.projectiles.extend(meteors)
        particle_system.spawn_sparks(self.center_x, self.center_y, (255, 60, 120), count=15)

    def _cast_singularity(self, player, particle_system, camera):
        camera.add_shake(9.0, 0.5)
        # Spawn black hole near player
        sx = player.center_x + random.uniform(-140, 140)
        sy = player.center_y - 80
        self.projectiles.append(BossProjectile(
            sx, sy, vx=0.0, vy=0.0,
            sprite=self.singularity_sprite, damage=14,
            radius=28, life=5.0, p_type="singularity",
            color=(140, 40, 220), shape="singularity"
        ))
        particle_system.spawn_sparks(sx, sy, (140, 30, 240), count=25)

    def get_projectiles_sync_data(self, player=None):
        """Serializes active projectiles on host for network broadcast."""
        data = []
        alive = [p for p in self.projectiles if p.life > 0]
        if len(alive) > 350 and player:
            alive.sort(key=lambda p: math.hypot(p.x - player.center_x, p.y - player.center_y))
            alive = alive[:350]
        elif len(alive) > 350:
            alive = alive[:350]
        for p in alive:
            data.append(p.to_sync_dict())
        return data

    def sync_projectiles(self, proj_data_list):
        """Reconciles client projectiles from authoritative host snapshot."""
        if not proj_data_list and not self.projectiles:
            return
        existing_by_id = {p.p_id: p for p in self.projectiles if hasattr(p, "p_id")}
        new_list = []
        for pd in proj_data_list:
            pid = pd.get("id")
            if pid is not None and pid in existing_by_id:
                p = existing_by_id[pid]
                dist = math.hypot(p.x - float(pd.get("x", p.x)), p.y - float(pd.get("y", p.y)))
                if dist > 120.0:
                    p.x = float(pd.get("x", p.x))
                    p.y = float(pd.get("y", p.y))
                else:
                    p.x = p.x * 0.70 + float(pd.get("x", p.x)) * 0.30
                    p.y = p.y * 0.70 + float(pd.get("y", p.y)) * 0.30
                p.vx = float(pd.get("vx", p.vx))
                p.vy = float(pd.get("vy", p.vy))
                p.life = float(pd.get("l", p.life))
                p.delay_move = float(pd.get("del", p.delay_move))
                new_list.append(p)
            else:
                s_shape = pd.get("s", "orb")
                if s_shape == "singularity":
                    sprite = self.singularity_sprite
                elif self.phase == 1:
                    sprite = self.solar_orb_sprite
                else:
                    sprite = self.void_meteor_sprite
                new_p = BossProjectile.from_sync_dict(pd, sprite=sprite)
                new_list.append(new_p)
        self.projectiles = new_list

    def update_client_projectiles(self, dt, player, particle_system, camera, combat=None):
        """Updates and handles projectile dodging/grazing on LAN client."""
        for p in self.projectiles:
            p.update(dt, player)

            # Celestial Aegis: Deflects / destroys enemy projectiles near player
            if p.life > 0 and getattr(player, "has_effect", None) and player.has_effect("celestial aegis"):
                if math.hypot(p.x - player.center_x, p.y - player.center_y) < 38.0:
                    p.life = 0
                    if self.sound_manager:
                        self.sound_manager.play_spatial("hit_block", p.x, p.y, player.center_x, player.center_y)
                    if particle_system:
                        particle_system.spawn_sparks(p.x, p.y, (100, 220, 255), count=10)
                    continue

            if p.life > 0 and p.rect.colliderect(player.rect):
                damaged = player.take_damage(p.damage, knockback_vx=p.vx * 0.7, knockback_vy=-4.0)
                # Dissipate non-singularity projectile upon core collision (prevents lingering stunlock during i-frames)
                if getattr(p, "p_type", "linear") != "singularity":
                    p.life = 0
                if damaged:
                    if particle_system:
                        particle_system.spawn_sparks(player.center_x, player.center_y, (255, 60, 160), 10)
                    if camera:
                        camera.add_shake(5.0, 0.25)
                    if combat and hasattr(combat, "spawn_damage_number"):
                        dmg_val = getattr(player, "last_damage_taken", p.damage)
                        combat.spawn_damage_number(player.center_x, player.y - 10, dmg_val, color=(255, 50, 50))
                else:
                    if particle_system:
                        particle_system.spawn_sparks(p.x, p.y, (255, 255, 255), count=4)
            elif getattr(p, "grazed", False) and not getattr(p, "_graze_sparked", False):
                p._graze_sparked = True
                if particle_system:
                    particle_system.spawn_sparks(p.x, p.y, (200, 240, 255), count=2)
        self.projectiles = [p for p in self.projectiles if p.life > 0]

    def render(self, target_surf, camera, renderer=None):
        if self.is_dead:
            return

        if renderer and hasattr(renderer, "draw_projectiles_batch") and self.projectiles:
            renderer.draw_projectiles_batch(self.projectiles, camera)
        else:
            for p in self.projectiles:
                p.render(target_surf, camera)

        sx, sy = camera.world_to_screen(self.x, self.y)
        frames_list = self.p1_frames if self.phase == 1 else self.p2_frames
        cur_surf = frames_list[self.frame_idx % len(frames_list)]

        if self.hurt_timer > 0 or self.is_transforming:
            tinted = cur_surf.copy()
            tint_color = (255, 255, 255, 220) if self.is_transforming else (255, 70, 70, 180)
            tinted.fill(tint_color, special_flags=pygame.BLEND_RGBA_MULT)
            cur_surf = tinted

        target_surf.blit(cur_surf, (sx, sy))

    def render_boss_bar(self, target_surf, font, font_title, bar_y=None):
        if self.is_dead:
            return
        bar_w = 390
        bar_h = 16
        bar_x = (SCREEN_WIDTH - bar_w) // 2
        if bar_y is None:
            bar_y = SCREEN_HEIGHT - 60  # Centered with ample clearance
        self.bar_y = bar_y

        # Smooth ghost damage lag interpolation
        if not hasattr(self, "display_hp"):
            self.display_hp = float(self.hp)
        if self.display_hp > self.hp:
            self.display_hp = max(float(self.hp), self.display_hp - max(20.0, (self.display_hp - self.hp) * 0.08))
        elif self.display_hp < self.hp:
            self.display_hp = float(self.hp)

        panel_x = bar_x - 12
        panel_y = bar_y - 22
        panel_w = bar_w + 24
        panel_h = bar_h + 28

        # Dynamic Phase Themes
        if self.phase == 1:
            outer_rim = (150, 120, 50)
            inner_rim = (255, 215, 75)
            t_col = (255, 235, 110)
            p_tag = "PHASE I: CELESTIAL TITAN"
            fill_col = (245, 140, 25)
            hi_col = (255, 225, 110)
            ghost_col = (255, 185, 70)
            crest_symbol = "☀"
            crest_col = (255, 215, 80)
        else:
            outer_rim = (120, 40, 160)
            inner_rim = (225, 75, 255)
            t_col = (255, 130, 245)
            p_tag = "✦ PHASE II: AWAKENED VOID GOD ✦"
            fill_col = (165, 25, 225)
            hi_col = (240, 120, 255)
            ghost_col = (200, 70, 180)
            crest_symbol = "☾"
            crest_col = (220, 80, 255)

        # 1. Backing Plate with Drop Shadow
        pygame.draw.rect(target_surf, (5, 6, 12, 190), (panel_x + 3, panel_y + 4, panel_w, panel_h), border_radius=7)
        pygame.draw.rect(target_surf, (16, 18, 30, 248), (panel_x, panel_y, panel_w, panel_h), border_radius=7)
        # Double Metallic Ornate Border
        pygame.draw.rect(target_surf, outer_rim, (panel_x, panel_y, panel_w, panel_h), 1, border_radius=7)
        pygame.draw.rect(target_surf, inner_rim, (panel_x + 2, panel_y + 2, panel_w - 4, panel_h - 4), 1, border_radius=5)

        # 2. Crest & Boss Title Header
        crest_txt = font.render(crest_symbol, True, crest_col)
        target_surf.blit(crest_txt, (bar_x, bar_y - 19))

        title_str = f"{self.name.upper()}  [{p_tag}]"
        sh_title = font.render(title_str, True, (0, 0, 0))
        title_txt = font.render(title_str, True, t_col)
        target_surf.blit(sh_title, (bar_x + 19, bar_y - 18))
        target_surf.blit(title_txt, (bar_x + 18, bar_y - 19))

        # 3. Bar Trench (Abyssal Void)
        pygame.draw.rect(target_surf, (30, 14, 30), (bar_x, bar_y, bar_w, bar_h), border_radius=4)

        # 4. Ghost Damage Lag Bar
        ghost_pct = max(0.0, min(1.0, self.display_hp / float(self.max_hp)))
        ghost_w = int(bar_w * ghost_pct)
        if ghost_w > 0:
            pygame.draw.rect(target_surf, ghost_col, (bar_x, bar_y, ghost_w, bar_h), border_radius=4)

        # 5. Current Health Bar with Dual Highlight
        pct = max(0.0, min(1.0, self.hp / float(self.max_hp)))
        fill_w = int(bar_w * pct)
        if fill_w > 0:
            pygame.draw.rect(target_surf, fill_col, (bar_x, bar_y, fill_w, bar_h), border_radius=4)
            pygame.draw.rect(target_surf, hi_col, (bar_x, bar_y, fill_w, 3), border_top_left_radius=4, border_top_right_radius=4)

        # 6. Phase Threshold Markers (25%, 50%, 75%)
        for t in (0.25, 0.50, 0.75):
            tx = bar_x + int(bar_w * t)
            pygame.draw.line(target_surf, (70, 25, 60), (tx, bar_y), (tx, bar_y + bar_h - 1), 1)

        # Inner Frame
        pygame.draw.rect(target_surf, (220, 195, 130) if self.phase == 1 else (210, 130, 240), (bar_x, bar_y, bar_w, bar_h), 1, border_radius=4)

        # 7. Status & High-Contrast HP Readout
        if self.is_transforming:
            pulse = int((math.sin(pygame.time.get_ticks() * 0.008) + 1.0) * 127)
            hp_str = "✦ AWAKENING TRUE VOID FORM... ✦"
            pulse_col = (255, pulse, 255)
            sh_num = font.render(hp_str, True, (0, 0, 0))
            num_txt = font.render(hp_str, True, pulse_col)
        else:
            hp_str = f"{self.hp:,} / {self.max_hp:,}  ({pct * 100:.1f}%)"
            sh_num = font.render(hp_str, True, (0, 0, 0))
            num_txt = font.render(hp_str, True, (255, 255, 255))

        cx = SCREEN_WIDTH // 2
        target_surf.blit(sh_num, (cx - num_txt.get_width() // 2 + 1, bar_y + 1))
        target_surf.blit(num_txt, (cx - num_txt.get_width() // 2, bar_y))


BOSS_TYPE_REGISTRY = {
    "lord_malus": LordMalus,
    "ignis_colossus": IgnisColossus,
    "cryo_spud": CryoSpud,
    "necro_tuber": NecroTuber,
    "grand_boss_sol_rho": GrandBossSolRho,
}

def create_boss_by_type(boss_type, x, y, asset_factory, sound_manager, party_size=1):
    """Instantiates a boss entity by its string identifier."""
    cls = BOSS_TYPE_REGISTRY.get(boss_type, LordMalus)
    if cls is GrandBossSolRho:
        return cls(x, y, asset_factory, sound_manager, party_size=party_size)
    return cls(x, y, asset_factory, sound_manager)
