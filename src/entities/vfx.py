"""
Potaria - Visual Effects Engine (Animated VFX)
Handles high-fidelity animated sprite frames for combat skills, ancient weapon slashes,
impact bursts, celestial barriers, and aura mandalas.
Developer: Kurados | Pure Python 3.13 & pygame-ce
"""

import math
import pygame


class AnimatedVFX:
    def __init__(self, x, y, frames, duration=0.5, loop=False, rot_deg=0.0, scale=1.0,
                 anchor=None, offset=(0, 0), blend_mode=None, flip_x=False, flip_y=False):
        self.x = float(x)
        self.y = float(y)
        self.frames = frames if isinstance(frames, list) else [frames]
        self.duration = max(0.05, float(duration))
        self.loop = loop
        self.rot_deg = float(rot_deg)
        self.scale = float(scale)
        self.anchor = anchor
        self.offset = offset
        self.blend_mode = blend_mode
        self.flip_x = bool(flip_x)
        self.flip_y = bool(flip_y)
        self.elapsed = 0.0
        self.is_alive = True
        self.frame_idx = 0

        # Pre-transform frames once at initialization to eliminate per-frame rotations, scaling and flips
        transformed = []
        needs_transform = (self.flip_x or self.flip_y or self.scale != 1.0 or self.rot_deg != 0.0)
        for f in self.frames:
            if not f:
                continue
            s = f
            if needs_transform:
                if self.flip_x or self.flip_y:
                    s = pygame.transform.flip(s, self.flip_x, self.flip_y)
                if self.scale != 1.0:
                    nw = max(1, int(s.get_width() * self.scale))
                    nh = max(1, int(s.get_height() * self.scale))
                    s = pygame.transform.scale(s, (nw, nh))
                if self.rot_deg != 0.0:
                    s = pygame.transform.rotate(s, self.rot_deg)
            transformed.append(s)
        self.prepared_frames = transformed if transformed else self.frames

    def update(self, dt):
        if not self.is_alive:
            return

        self.elapsed += dt
        if self.anchor:
            ax = getattr(self.anchor, "center_x", getattr(self.anchor, "x", self.x))
            ay = getattr(self.anchor, "center_y", getattr(self.anchor, "y", self.y))
            self.x = ax + self.offset[0]
            self.y = ay + self.offset[1]

        if self.elapsed >= self.duration:
            if self.loop:
                self.elapsed = self.elapsed % self.duration
            else:
                self.is_alive = False
                return

        # Calculate active frame based on progress
        if len(self.prepared_frames) > 0:
            frac = min(0.999, self.elapsed / self.duration)
            self.frame_idx = int(frac * len(self.prepared_frames))

    def render(self, target_surf, camera):
        if not self.is_alive or not self.prepared_frames:
            return

        surf = self.prepared_frames[min(self.frame_idx, len(self.prepared_frames) - 1)]
        if not surf:
            return

        sx, sy = camera.world_to_screen(self.x, self.y)
        sw, sh = target_surf.get_width(), target_surf.get_height()
        w, h = surf.get_width(), surf.get_height()
        rx = int(sx) - w // 2
        ry = int(sy) - h // 2

        if rx + w < 0 or rx > sw or ry + h < 0 or ry > sh:
            return

        if self.blend_mode:
            target_surf.blit(surf, (rx, ry), special_flags=self.blend_mode)
        else:
            target_surf.blit(surf, (rx, ry))


class VisualEffectManager:
    def __init__(self, asset_factory):
        self.asset_factory = asset_factory
        self.effects = []

    def spawn_effect(self, anim_name, x, y, duration=None, loop=False, rot_deg=0.0,
                     scale=1.0, anchor=None, offset=(0, 0), blend_mode=None,
                     flip_x=False, flip_y=False):
        """Spawns an animated visual effect from AssetFactory's animated_effects registry."""
        frames = self.asset_factory.animated_effects.get(anim_name, [])
        if not frames:
            return None

        # Default durations tailored to animation type
        if duration is None:
            default_durations = {
                "power_slash": 0.38,
                "whirlwind": 0.45,
                "dash": 0.32,
                "fireball_detonation": 0.42,
                "meteor_impact": 0.70,
                "frost_nova": 0.50,
                "celestial_shield": 3.0,
                "void_singularity": 2.5,
                "ancient_slash": 0.45,
                "ancient_burst": 0.60,
                "ancient_aura": 1.2,
                "ancient_discovery": 1.5,
                "grand_celestial_starfall": 0.65,
                "solar_flare_supernova": 0.60,
                "cryo_frost_shatter": 0.50,
                "thunderclap_strike": 0.40,
                "starlight_volley_burst": 0.45,
                "ancient_cleave_grand": 0.55,
                "ancient_radiant_aura": 1.4,
                "weapon_charge_burst": 0.35,
            }
            duration = default_durations.get(anim_name, 0.45)

        vfx = AnimatedVFX(
            x=x, y=y, frames=frames, duration=duration, loop=loop,
            rot_deg=rot_deg, scale=scale, anchor=anchor, offset=offset,
            blend_mode=blend_mode, flip_x=flip_x, flip_y=flip_y
        )
        self.effects.append(vfx)
        return vfx

    spawn = spawn_effect

    def spawn_custom_vfx(self, vfx):
        if vfx:
            self.effects.append(vfx)

    def remove_anchored_effects(self, anchor_entity, anim_name=None):
        """Removes active looping effects anchored to a specific entity."""
        rem = []
        for e in self.effects:
            if e.anchor == anchor_entity:
                if anim_name is None or getattr(e, "anim_name", None) == anim_name:
                    e.is_alive = False
                else:
                    rem.append(e)
            else:
                rem.append(e)
        self.effects = rem

    def update(self, dt):
        for e in self.effects:
            e.update(dt)
        self.effects = [e for e in self.effects if e.is_alive]

    def render(self, target_surf, camera):
        for e in self.effects:
            e.render(target_surf, camera)

    def clear(self):
        self.effects.clear()
