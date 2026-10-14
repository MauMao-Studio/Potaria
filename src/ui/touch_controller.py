"""
Potaria - Mobile Touchscreen Virtual Controller & UI/UX System
Implements high-ergonomics virtual touch controls for cross-platform play:
- Virtual Left Joystick / D-Pad with directional indicators and dynamic travel
- Virtual Right Action Cluster (Attack/Mine, Jump, Dash, Quick Heal/Potion)
- Quick Skill Radial/Arc Cluster (Q, F, V, R hotkey skills with cooldown sweeps)
- Top Bar Mobile Utility Buttons (Backpack [E], Character Status [C], Pause/Menu [ESC])
- Direct World Touch Targeting with animated reticles
- Visual touch ripples, active press state depression, and haptic/audio feedback
- Strict adherence to mobile UI/UX guidelines (>= 48x48 px touch targets, thumb-friendly clusters)
- Persisted Touch Controls [Auto / On / Off] and Touch Opacity [50% / 75% / 100%]
Developer: Kurados
"""

import math
import os
import pygame
from src.constants import (
    SCREEN_WIDTH, SCREEN_HEIGHT, SLOT_SIZE, SLOT_PADDING, SCALED_TILE,
    CAT_WEAPON, CAT_TOOL, CAT_BLOCK, CAT_WALL, CAT_CONSUMABLE
)
from src.rpg.skills import SKILL_DEFINITIONS
from src.ui.inventory import ITEM_REGISTRY

# Priority list for Quick Heal consumption
HEALING_ITEM_PRIORITY = (
    "greater_healing_potion",
    "golden_fry",
    "healing_potion",
    "mashed_potato",
    "raw_potato",
)


def quick_heal(player, inventory, sound_manager=None, particle_system=None):
    """Finds and drinks best potion or eats food from inventory."""
    if player.health >= player.max_health:
        if hasattr(inventory, "notify"):
            inventory.notify("Health is already full!")
        return False

    found_slot_idx = None
    found_item_id = None

    for item_name in HEALING_ITEM_PRIORITY:
        for idx, slot in enumerate(inventory.slots):
            if slot and slot.item_id == item_name:
                found_slot_idx = idx
                found_item_id = item_name
                break
        if found_slot_idx is not None:
            break

    if found_slot_idx is not None:
        consumed = player.consume_item(found_item_id)
        if consumed:
            slot = inventory.slots[found_slot_idx]
            slot.count -= 1
            if slot.count <= 0:
                inventory.slots[found_slot_idx] = None
            if sound_manager:
                sound_manager.play("pickup")
            if particle_system:
                particle_system.spawn_sparks(player.center_x, player.center_y, (80, 255, 120), count=25)
            name = ITEM_REGISTRY.get(found_item_id, {}).get("name", found_item_id.replace("_", " ").title())
            if hasattr(inventory, "notify"):
                inventory.notify(f"Quick Heal: Consumed {name}! (+HP)")
            return True

    if hasattr(inventory, "notify"):
        inventory.notify("No potions or food available in inventory!")
    return False


def count_healing_items(inventory):
    count = 0
    p_set = set(HEALING_ITEM_PRIORITY)
    for slot in getattr(inventory, "slots", []):
        if slot and slot.item_id in p_set:
            count += slot.count
    return count


class TouchRipple:
    """Expanding visual touch wave emitted upon finger press for tactile feedback."""
    def __init__(self, x, y, color=(255, 255, 255), max_radius=38, duration=0.25):
        self.x = float(x)
        self.y = float(y)
        self.color = color
        self.max_radius = max_radius
        self.duration = duration
        self.elapsed = 0.0

    def update(self, dt):
        self.elapsed += dt
        return self.elapsed < self.duration

    def render(self, surface, opacity=1.0):
        t = min(1.0, self.elapsed / self.duration)
        current_r = 8.0 + (self.max_radius - 8.0) * t
        alpha = int(210 * (1.0 - t) * opacity)
        if alpha <= 0 or current_r < 2:
            return
        
        # Draw on small temp surface for clean alpha blending
        size = int(current_r * 2) + 4
        rip_surf = pygame.Surface((size, size), pygame.SRCALPHA)
        center = size // 2
        r_col = (*self.color[:3], alpha)
        pygame.draw.circle(rip_surf, r_col, (center, center), int(current_r), width=2)
        surface.blit(rip_surf, (int(self.x - center), int(self.y - center)))


class TouchButton:
    """
    Mobile UI button adhering to touch ergonomics guidelines (>= 48x48 px hitbox,
    active press depression, semi-transparent styling, cooldown clock sweep).
    """
    def __init__(self, btn_id, shape="circle", x=0, y=0, radius=26, rect=None,
                 label="", sublabel="", color=(120, 160, 240), hit_padding=6):
        self.id = btn_id
        self.shape = shape
        self.x = float(x)
        self.y = float(y)
        self.radius = float(radius)
        self.rect = rect or pygame.Rect(int(x - radius), int(y - radius), int(radius * 2), int(radius * 2))
        self.hit_padding = hit_padding
        self.label = label
        self.sublabel = sublabel
        self.color = color
        
        self.pressed = False
        self.press_timer = 0.0
        self.active_finger_id = None
        self.active_finger_ids = set()
        self.badge = ""
        self.cooldown_pct = 0.0
        self.cooldown_time = 0.0
        self.disabled = False

    def contains(self, px, py):
        """Hitbox test guaranteeing >= 48x48 px minimum touch target."""
        if self.shape == "circle":
            eff_r = max(24.0, self.radius + self.hit_padding)
            return math.hypot(px - self.x, py - self.y) <= eff_r
        else:
            eff_rect = self.rect.inflate(max(0, 48 - self.rect.width), max(0, 48 - self.rect.height))
            return eff_rect.collidepoint(px, py)

    def on_touch_down(self, finger_id, px=None, py=None):
        self.pressed = True
        self.press_timer = 0.18
        self.active_finger_id = finger_id
        self.active_finger_ids.add(finger_id)

    def on_touch_up(self, finger_id):
        self.active_finger_ids.discard(finger_id)
        if not self.active_finger_ids:
            self.pressed = False
            self.active_finger_id = None
        else:
            self.active_finger_id = next(iter(self.active_finger_ids))

    def update(self, dt):
        if self.press_timer > 0:
            self.press_timer = max(0.0, self.press_timer - dt)
            if self.press_timer == 0.0 and not self.active_finger_ids:
                self.pressed = False

    def render(self, surface, font, font_sm, font_xs, opacity=1.0):
        # Calculate visual depression
        scale = 0.92 if self.pressed else 1.0
        alpha_mult = max(0.2, min(1.0, opacity))

        if self.shape == "circle":
            self._render_circle(surface, font, font_sm, font_xs, scale, alpha_mult)
        else:
            self._render_rect(surface, font, font_sm, font_xs, scale, alpha_mult)

    def _render_circle(self, surface, font, font_sm, font_xs, scale, alpha_mult):
        r = int(self.radius * scale)
        cx, cy = int(self.x), int(self.y)
        dia = (r + 4) * 2
        btn_surf = pygame.Surface((dia, dia), pygame.SRCALPHA)
        center = dia // 2

        # 1. Outer dark glass background
        bg_alpha = int(175 * alpha_mult) if not self.pressed else int(220 * alpha_mult)
        pygame.draw.circle(btn_surf, (22, 28, 44, bg_alpha), (center, center), r)

        # 2. Glowing inner halo or tint
        tint_alpha = int(70 * alpha_mult) if not self.pressed else int(140 * alpha_mult)
        pygame.draw.circle(btn_surf, (*self.color[:3], tint_alpha), (center, center), max(1, r - 3))

        # 3. Outer border ring
        border_alpha = int(230 * alpha_mult)
        border_col = (255, 235, 120) if self.pressed else self.color
        border_width = 3 if self.pressed else 2
        pygame.draw.circle(btn_surf, (*border_col[:3], border_alpha), (center, center), r, width=border_width)

        # 4. Cooldown clock sweep
        if self.cooldown_pct > 0.01:
            cd_h = int(r * 2 * self.cooldown_pct)
            cd_rect = pygame.Rect(center - r, center + r - cd_h, r * 2, cd_h)
            cd_surf = pygame.Surface((r * 2, cd_h), pygame.SRCALPHA)
            cd_surf.fill((0, 0, 0, int(185 * alpha_mult)))
            btn_surf.blit(cd_surf, cd_rect.topleft)

        # 5. Label text
        label_col = (255, 255, 255) if not self.disabled else (150, 150, 150)
        lbl_render = font_sm.render(self.label, True, label_col)
        btn_surf.blit(lbl_render, (center - lbl_render.get_width() // 2, center - lbl_render.get_height() // 2 + (1 if self.pressed else 0)))

        # 6. Sublabel / Hotkey text (top-left or bottom)
        if self.sublabel:
            sub_col = (255, 220, 80) if not self.disabled else (130, 130, 130)
            sub_render = font_xs.render(self.sublabel, True, sub_col)
            btn_surf.blit(sub_render, (center - r + 5, center - r + 3))

        # 7. Badge text (e.g. potion count "x3" or skill level "Lv.1")
        if self.badge:
            badge_surf = font_xs.render(self.badge, True, (255, 255, 255))
            bw = badge_surf.get_width() + 6
            bh = 13
            bx = center + r - bw + 2
            by = center - r - 2
            pill_rect = pygame.Rect(bx, by, bw, bh)
            pygame.draw.rect(btn_surf, (200, 30, 60, int(235 * alpha_mult)), pill_rect, border_radius=4)
            pygame.draw.rect(btn_surf, (255, 215, 0, int(235 * alpha_mult)), pill_rect, width=1, border_radius=4)
            btn_surf.blit(badge_surf, (bx + 3, by - 1))

        # 8. Numeric Cooldown overlay
        if self.cooldown_time > 0.05:
            cd_txt = font_xs.render(f"{self.cooldown_time:.1f}s", True, (255, 230, 100))
            btn_surf.blit(cd_txt, (center - cd_txt.get_width() // 2, center + r - 14))

        surface.blit(btn_surf, (cx - center, cy - center))

    def _render_rect(self, surface, font, font_sm, font_xs, scale, alpha_mult):
        w = int(self.rect.width * scale)
        h = int(self.rect.height * scale)
        rx = self.rect.centerx - w // 2
        ry = self.rect.centery - h // 2
        
        btn_surf = pygame.Surface((w, h), pygame.SRCALPHA)
        bg_alpha = int(180 * alpha_mult) if not self.pressed else int(235 * alpha_mult)
        pygame.draw.rect(btn_surf, (24, 30, 48, bg_alpha), (0, 0, w, h), border_radius=8)

        # Highlight or color accent
        accent_alpha = int(80 * alpha_mult) if not self.pressed else int(150 * alpha_mult)
        pygame.draw.rect(btn_surf, (*self.color[:3], accent_alpha), (2, 2, w - 4, h - 4), border_radius=6)

        # Border
        border_col = (255, 235, 120) if self.pressed else self.color
        border_alpha = int(235 * alpha_mult)
        pygame.draw.rect(btn_surf, (*border_col[:3], border_alpha), (0, 0, w, h), width=2, border_radius=8)

        # Labels
        lbl_render = font_sm.render(self.label, True, (255, 255, 255))
        btn_surf.blit(lbl_render, (w // 2 - lbl_render.get_width() // 2, h // 2 - lbl_render.get_height() // 2 - 4 + (1 if self.pressed else 0)))

        if self.sublabel:
            sub_render = font_xs.render(self.sublabel, True, (255, 215, 80))
            btn_surf.blit(sub_render, (w // 2 - sub_render.get_width() // 2, h - 14 + (1 if self.pressed else 0)))

        surface.blit(btn_surf, (rx, ry))


class VirtualJoystick:
    """
    Virtual thumbstick / D-Pad for walking, jumping, and dropping platforms.
    Features outer directional indicators (▲ Jump, ▼ Drop, ◄ Left, ► Right),
    a smooth travel limit, deadzone dampening, and spring-return physics.
    """
    def __init__(self, center_x=140, center_y=590, radius_base=66, radius_knob=28, radius_travel=48):
        self.center_x = float(center_x)
        self.center_y = float(center_y)
        self.radius_base = float(radius_base)
        self.radius_knob = float(radius_knob)
        self.radius_travel = float(radius_travel)
        self.deadzone = 12.0
        self.hit_radius = radius_base + 22.0  # Generous 176px diameter touch zone

        self.knob_x = float(center_x)
        self.knob_y = float(center_y)
        self.active_finger_id = None

        self.axis_x = 0.0
        self.axis_y = 0.0
        self.is_left = False
        self.is_right = False
        self.is_jump = False
        self.is_drop = False
        self._jump_debounced = False

    def contains(self, px, py):
        return math.hypot(px - self.center_x, py - self.center_y) <= self.hit_radius

    def on_touch_down(self, finger_id, px, py):
        if self.active_finger_id is not None and self.active_finger_id != finger_id:
            return
        self.active_finger_id = finger_id
        self._update_position(px, py)

    def on_touch_move(self, finger_id, px, py):
        if self.active_finger_id == finger_id:
            self._update_position(px, py)

    def on_touch_up(self, finger_id):
        if self.active_finger_id == finger_id:
            self.reset()

    def reset(self):
        self.active_finger_id = None
        self.axis_x = 0.0
        self.axis_y = 0.0
        self.is_left = False
        self.is_right = False
        self.is_jump = False
        self.is_drop = False
        self._jump_debounced = False
        self.knob_x = self.center_x
        self.knob_y = self.center_y

    def _update_position(self, px, py):
        dx = px - self.center_x
        dy = py - self.center_y
        dist = math.hypot(dx, dy)

        if dist > self.radius_travel:
            scale = self.radius_travel / dist
            self.knob_x = self.center_x + dx * scale
            self.knob_y = self.center_y + dy * scale
        else:
            self.knob_x = px
            self.knob_y = py

        if dist < self.deadzone:
            self.axis_x = 0.0
            self.axis_y = 0.0
            self.is_left = False
            self.is_right = False
            self.is_jump = False
            self.is_drop = False
            self._jump_debounced = False
        else:
            self.axis_x = max(-1.0, min(1.0, dx / self.radius_travel))
            self.axis_y = max(-1.0, min(1.0, dy / self.radius_travel))

            self.is_left = (self.axis_x < -0.28)
            self.is_right = (self.axis_x > 0.28)
            
            # Vertical thresholds
            was_jump = self.is_jump
            self.is_jump = (self.axis_y < -0.42)
            if not self.is_jump:
                self._jump_debounced = False

            self.is_drop = (self.axis_y > 0.42)

    def update(self, dt):
        # Smooth spring-return to center when finger is lifted
        if self.active_finger_id is None:
            decay = math.exp(-22.0 * dt)
            self.knob_x = self.center_x + (self.knob_x - self.center_x) * decay
            self.knob_y = self.center_y + (self.knob_y - self.center_y) * decay

    def render(self, surface, font_sm, font_xs, opacity=1.0):
        alpha_mult = max(0.2, min(1.0, opacity))
        cx, cy = int(self.center_x), int(self.center_y)
        dia = int(self.radius_base * 2 + 16)
        base_surf = pygame.Surface((dia, dia), pygame.SRCALPHA)
        center = dia // 2

        # 1. Frosted glass base plate
        bg_alpha = int(160 * alpha_mult)
        pygame.draw.circle(base_surf, (20, 26, 42, bg_alpha), (center, center), int(self.radius_base))
        pygame.draw.circle(base_surf, (40, 70, 110, int(70 * alpha_mult)), (center, center), int(self.radius_base - 4))
        pygame.draw.circle(base_surf, (100, 160, 240, int(200 * alpha_mult)), (center, center), int(self.radius_base), width=2)

        # 2. D-Pad Directional glyphs on base
        arrows = [
            ("▲", center, center - int(self.radius_base * 0.68), self.is_jump),
            ("▼", center, center + int(self.radius_base * 0.68), self.is_drop),
            ("◄", center - int(self.radius_base * 0.68), center, self.is_left),
            ("►", center + int(self.radius_base * 0.68), center, self.is_right),
        ]
        for glyph, gx, gy, active in arrows:
            col = (255, 230, 90) if active else (130, 160, 200)
            txt = font_sm.render(glyph, True, col)
            base_surf.blit(txt, (gx - txt.get_width() // 2, gy - txt.get_height() // 2))

        # Direction helper sublabels
        txt_jump = font_xs.render("JUMP", True, (255, 235, 100) if self.is_jump else (110, 130, 160))
        txt_drop = font_xs.render("DROP", True, (255, 235, 100) if self.is_drop else (110, 130, 160))
        base_surf.blit(txt_jump, (center - txt_jump.get_width() // 2, center - int(self.radius_base * 0.68) + 12))
        base_surf.blit(txt_drop, (center - txt_drop.get_width() // 2, center + int(self.radius_base * 0.68) - 18))

        surface.blit(base_surf, (cx - center, cy - center))

        # 3. Connection vector line
        kx, ky = int(self.knob_x), int(self.knob_y)
        if math.hypot(kx - cx, ky - cy) > 4:
            line_surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            pygame.draw.line(line_surf, (120, 180, 255, int(120 * alpha_mult)), (cx, cy), (kx, ky), width=3)
            surface.blit(line_surf, (0, 0))

        # 4. Draggable Knob
        knob_dia = int(self.radius_knob * 2 + 8)
        knob_surf = pygame.Surface((knob_dia, knob_dia), pygame.SRCALPHA)
        k_center = knob_dia // 2
        is_active = (self.active_finger_id is not None)

        k_bg = (32, 44, 70, int(220 * alpha_mult)) if is_active else (26, 36, 58, int(195 * alpha_mult))
        pygame.draw.circle(knob_surf, k_bg, (k_center, k_center), int(self.radius_knob))
        
        # Center glow gem
        gem_col = (100, 200, 255) if is_active else (70, 130, 190)
        pygame.draw.circle(knob_surf, (*gem_col, int(210 * alpha_mult)), (k_center, k_center), int(self.radius_knob * 0.46))
        
        # Glowing border
        border_col = (255, 230, 100) if is_active else (120, 180, 255)
        pygame.draw.circle(knob_surf, (*border_col, int(240 * alpha_mult)), (k_center, k_center), int(self.radius_knob), width=2)

        surface.blit(knob_surf, (kx - k_center, ky - k_center))


class TouchController:
    """
    Main manager for mobile touch controls and UI/UX ergonomics.
    Coexists smoothly with PC keyboard & mouse controls.
    """
    def __init__(self, asset_factory=None, sound_manager=None):
        self.asset_factory = asset_factory
        self.sound_manager = sound_manager

        # Settings
        self.mode = "auto"         # "auto", "on", "off"
        self.opacity = 0.75        # 0.50, 0.75, 1.00
        self.has_touch_input = False

        # Fonts (Centralized Typography Theme)
        from src.ui.theme import font_semibold, font_compact
        self.font = font_semibold(14)
        self.font_sm = font_compact(11)
        self.font_xs = font_compact(9)

        # 1. Virtual Joystick (Bottom Left)
        self.joystick = VirtualJoystick(center_x=140, center_y=SCREEN_HEIGHT - 130, radius_base=66, radius_knob=28)

        # 2. Virtual Right Action Cluster
        # Attack/Mine (Primary, prominent 72x72 px hitbox)
        self.btn_attack = TouchButton("attack", "circle", x=1170, y=605, radius=36,
                                      label="ATTACK", sublabel="MINE", color=(235, 75, 75))
        # Jump Button
        self.btn_jump = TouchButton("jump", "circle", x=1075, y=620, radius=28,
                                    label="JUMP", sublabel="▲", color=(60, 160, 240))
        # Dash Button
        self.btn_dash = TouchButton("dash", "circle", x=1055, y=530, radius=26,
                                    label="DASH", sublabel=">>", color=(50, 210, 155))
        # Quick Heal Button (with potion counter badge)
        self.btn_heal = TouchButton("heal", "circle", x=1170, y=490, radius=26,
                                    label="HEAL", sublabel="+", color=(240, 80, 130))

        # 3. Quick Skill Arc Cluster (Radial arc wrapping over action cluster)
        self.btn_skill_q = TouchButton("skill_q", "circle", x=920, y=600, radius=25,
                                       label="SLS", sublabel="Q", color=(255, 180, 50))
        self.btn_skill_f = TouchButton("skill_f", "circle", x=945, y=510, radius=25,
                                       label="WHL", sublabel="F", color=(180, 100, 255))
        self.btn_skill_v = TouchButton("skill_v", "circle", x=1000, y=435, radius=25,
                                       label="DSH", sublabel="V", color=(80, 220, 240))
        self.btn_skill_r = TouchButton("skill_r", "circle", x=1080, y=385, radius=25,
                                       label="FIR", sublabel="R", color=(255, 100, 70))

        # 4. Top Bar Mobile Utility Buttons
        self.btn_inventory = TouchButton("inventory", "rect", rect=pygame.Rect(525, 12, 62, 48),
                                         label="BAG", sublabel="[E]", color=(230, 180, 50))
        self.btn_character = TouchButton("character", "rect", rect=pygame.Rect(597, 12, 62, 48),
                                         label="STAT", sublabel="[C]", color=(100, 200, 255))
        self.btn_pause = TouchButton("pause", "rect", rect=pygame.Rect(669, 12, 62, 48),
                                     label="MENU", sublabel="[ESC]", color=(200, 120, 240))

        self.action_buttons = [self.btn_attack, self.btn_jump, self.btn_dash, self.btn_heal]
        self.skill_buttons = [self.btn_skill_q, self.btn_skill_f, self.btn_skill_v, self.btn_skill_r]
        self.utility_buttons = [self.btn_inventory, self.btn_character, self.btn_pause]
        self.all_buttons = self.action_buttons + self.skill_buttons + self.utility_buttons

        # State Tracking
        self.game = None
        self.is_attack_down = False
        self.direct_touch_finger_id = None
        self.direct_touch_pos = None
        self.is_direct_touching = False
        self.reticle_pulse = 0.0

        # Visual feedback ripples
        self.ripples = []

    def reset(self):
        """Safely resets all virtual touch states, fingers, and hold timers."""
        self.is_attack_down = False
        self.is_direct_touching = False
        self.direct_touch_finger_id = None
        self.direct_touch_pos = None
        self.joystick.reset()
        for btn in self.all_buttons:
            btn.pressed = False
            btn.active_finger_id = None
            if hasattr(btn, "active_finger_ids"):
                btn.active_finger_ids.clear()
            btn.press_timer = 0.0

    def set_mode(self, mode):
        if mode in ("auto", "on", "off"):
            self.mode = mode

    def set_opacity(self, opacity):
        try:
            val = float(opacity)
            self.opacity = max(0.2, min(1.0, val))
        except (ValueError, TypeError):
            self.opacity = 0.75

    def is_visible(self):
        """Returns True if virtual controls should be rendered and processed."""
        if self.mode == "on":
            return True
        elif self.mode == "off":
            return False
        # "auto" mode: Active if touch events detected or mobile environment set
        if self.has_touch_input:
            return True
        if os.environ.get("POTARIA_MOBILE") in ("1", "true", "True"):
            return True
        return False

    def add_ripple(self, x, y, color=(255, 255, 255)):
        self.ripples.append(TouchRipple(x, y, color=color))

    def get_virtual_keys(self, raw_keys, key_bindings=None):
        """
        Synthesizes a combined key mapping including virtual joystick & buttons.
        player.handle_input() accepts dicts natively without breaking physical keyboard.
        """
        key_dict = {}
        # Copy down states from raw_keys (which may be ScancodeWrapper or dict)
        if isinstance(raw_keys, dict):
            key_dict.update(raw_keys)
        else:
            # Check standard movement keys and custom rebound keys from ScancodeWrapper safely
            keys_to_check = {
                pygame.K_a, pygame.K_d, pygame.K_s, pygame.K_w,
                pygame.K_LEFT, pygame.K_RIGHT, pygame.K_UP, pygame.K_DOWN,
                pygame.K_SPACE, pygame.K_q, pygame.K_f, pygame.K_v, pygame.K_r,
                pygame.K_e, pygame.K_c, pygame.K_m, pygame.K_ESCAPE
            }
            if key_bindings:
                for k in key_bindings.values():
                    if isinstance(k, int):
                        keys_to_check.add(k)

            for k in keys_to_check:
                try:
                    if raw_keys[k]:
                        key_dict[k] = True
                except (IndexError, KeyError):
                    pass

        if not self.is_visible():
            return key_dict

        k_left = key_bindings.get("Move Left", pygame.K_a) if key_bindings else pygame.K_a
        k_right = key_bindings.get("Move Right", pygame.K_d) if key_bindings else pygame.K_d
        k_drop = key_bindings.get("Drop Platform", pygame.K_s) if key_bindings else pygame.K_s
        k_jump = key_bindings.get("Jump", pygame.K_SPACE) if key_bindings else pygame.K_SPACE

        if self.joystick.is_left:
            key_dict[k_left] = True
            key_dict[pygame.K_LEFT] = True
            key_dict[pygame.K_a] = True

        if self.joystick.is_right:
            key_dict[k_right] = True
            key_dict[pygame.K_RIGHT] = True
            key_dict[pygame.K_d] = True

        if self.joystick.is_jump or self.btn_jump.pressed:
            key_dict[k_jump] = True
            key_dict[pygame.K_SPACE] = True
            key_dict[pygame.K_UP] = True
            key_dict[pygame.K_w] = True

        if self.joystick.is_drop:
            key_dict[k_drop] = True
            key_dict[pygame.K_DOWN] = True
            key_dict[pygame.K_s] = True

        return key_dict

    def handle_touch_event(self, event, game):
        """Processes native SDL2 / Pygame FINGERDOWN, FINGERMOTION, FINGERUP events."""
        self.has_touch_input = True
        px = int(event.x * SCREEN_WIDTH)
        py = int(event.y * SCREEN_HEIGHT)

        if event.type == pygame.FINGERDOWN:
            return self.handle_touch_down(event.finger_id, px, py, game)
        elif event.type == pygame.FINGERMOTION:
            return self.handle_touch_motion(event.finger_id, px, py, game)
        elif event.type == pygame.FINGERUP:
            return self.handle_touch_up(event.finger_id, px, py, game)
        return False

    def handle_mouse_down(self, mouse_x, mouse_y, button, game):
        """Simulates single-touch interaction from PC mouse for testing/playing."""
        if not self.is_visible() or button != 1:
            return False
        return self.handle_touch_down("mouse", mouse_x, mouse_y, game)

    def handle_mouse_motion(self, mouse_x, mouse_y, game):
        if not self.is_visible():
            return False
        return self.handle_touch_motion("mouse", mouse_x, mouse_y, game)

    def handle_mouse_up(self, mouse_x, mouse_y, button, game):
        if not self.is_visible() or button != 1:
            return False
        return self.handle_touch_up("mouse", mouse_x, mouse_y, game)

    def handle_touch_down(self, finger_id, px, py, game):
        self.game = game
        # 1. Top bar utility buttons take priority regardless of modal panels
        for btn in self.utility_buttons:
            if btn.contains(px, py):
                btn.pressed = True
                btn.press_timer = 0.18
                btn.active_finger_id = finger_id
                if hasattr(btn, "active_finger_ids"):
                    btn.active_finger_ids.add(finger_id)
                self.add_ripple(px, py, color=btn.color)
                if self.sound_manager:
                    self.sound_manager.play("place")

                if btn.id == "inventory":
                    if hasattr(game, "npc_dialogue") and game.npc_dialogue.is_open:
                        game.npc_dialogue.close()
                    else:
                        game.inventory.is_open = not game.inventory.is_open
                        if game.inventory.is_open:
                            game.crafting.update_recipes(game.inventory, game.world, game.player)
                elif btn.id == "character":
                    game.character_panel.toggle()
                elif btn.id == "pause":
                    game.paused = not game.paused
                return True

        # If a modal panel is open, do not handle gameplay touch buttons
        panels_open = (game.inventory.is_open or game.character_panel.is_open or
                       (hasattr(game, "npc_dialogue") and game.npc_dialogue.is_open) or
                       game.paused)
        if panels_open:
            return False

        # 2. Check Virtual Joystick
        if self.joystick.contains(px, py):
            self.joystick.on_touch_down(finger_id, px, py)
            self.add_ripple(px, py, color=(120, 180, 255))
            return True

        # 3. Check Right Action Cluster
        for btn in self.action_buttons:
            if btn.contains(px, py):
                btn.pressed = True
                btn.press_timer = 0.18
                btn.active_finger_id = finger_id
                if hasattr(btn, "active_finger_ids"):
                    btn.active_finger_ids.add(finger_id)
                self.add_ripple(px, py, color=btn.color)
                if self.sound_manager:
                    self.sound_manager.play("place")

                if btn.id == "attack":
                    self.is_attack_down = True
                    self._execute_attack_or_mine(game)
                elif btn.id == "jump":
                    self._execute_jump(game)
                elif btn.id == "dash":
                    self._execute_dash(game)
                elif btn.id == "heal":
                    self.quick_heal(game.player, game.inventory, game.sound_manager, game.particle_system)
                return True

        # 4. Check Quick Skill Arc Cluster
        for btn in self.skill_buttons:
            if btn.contains(px, py):
                btn.pressed = True
                btn.press_timer = 0.18
                btn.active_finger_id = finger_id
                if hasattr(btn, "active_finger_ids"):
                    btn.active_finger_ids.add(finger_id)
                self.add_ripple(px, py, color=btn.color)

                key_map = {"skill_q": "Q", "skill_f": "F", "skill_v": "V", "skill_r": "R"}
                s_key = key_map.get(btn.id, "Q")
                game.player.cast_skill_hotkey(s_key, game.particle_system, game.camera)
                return True

        # 5. Check Hotbar tap selection (top-left hotbar row)
        if 20 <= px <= 460 and 20 <= py <= 64:
            slot_idx = (px - 20) // (SLOT_SIZE + SLOT_PADDING)
            if 0 <= slot_idx < 10:
                game.inventory.selected_slot = slot_idx
                self.add_ripple(px, py, color=(255, 215, 0))
                if self.sound_manager:
                    self.sound_manager.play("place")
                return True

        # 6. Direct World Touch Interaction
        self.direct_touch_finger_id = finger_id
        self.direct_touch_pos = (px, py)
        self.is_direct_touching = True
        self.add_ripple(px, py, color=(255, 255, 255))
        self._execute_direct_world_touch(px, py, game)
        return True

    def handle_touch_motion(self, finger_id, px, py, game):
        if self.joystick.active_finger_id == finger_id:
            self.joystick.on_touch_move(finger_id, px, py)
            return True

        if self.direct_touch_finger_id == finger_id:
            self.direct_touch_pos = (px, py)
            mouse_wx, mouse_wy = game.camera.screen_to_world(px, py)
            game.player.aim_angle = math.atan2(mouse_wy - game.player.center_y, mouse_wx - game.player.center_x)
            game.player.facing_right = (mouse_wx >= game.player.center_x)
            return True

        return False

    def handle_touch_up(self, finger_id, px, py, game):
        handled = False
        if self.joystick.active_finger_id == finger_id:
            self.joystick.on_touch_up(finger_id)
            handled = True

        for btn in self.all_buttons:
            if hasattr(btn, "active_finger_ids") and finger_id in btn.active_finger_ids:
                btn.active_finger_ids.discard(finger_id)
                if not btn.active_finger_ids:
                    btn.pressed = False
                    btn.active_finger_id = None
                    if btn.id == "attack":
                        self.is_attack_down = False
                else:
                    btn.active_finger_id = next(iter(btn.active_finger_ids))
                handled = True
            elif btn.active_finger_id == finger_id:
                btn.active_finger_id = None
                btn.pressed = False
                if btn.id == "attack":
                    self.is_attack_down = False
                handled = True

        if self.direct_touch_finger_id == finger_id:
            self.direct_touch_finger_id = None
            self.is_direct_touching = False
            handled = True

        return handled

    def _execute_attack_or_mine(self, game):
        """Triggers primary attack or mining towards facing/aim angle, or places/consumes active item."""
        active = game.inventory.get_active_item()
        cat = active.data.get("cat") if active and hasattr(active, "data") else None

        aim_dist = 64.0
        aim_x = game.player.center_x + math.cos(game.player.aim_angle) * aim_dist
        aim_y = game.player.center_y + math.sin(game.player.aim_angle) * aim_dist
        target_sx, target_sy = game.camera.world_to_screen(aim_x, aim_y)

        # 1. Block or Wall placement
        if active and (cat in (CAT_BLOCK, CAT_WALL) or active.data.get("tile") is not None or active.data.get("wall") is not None):
            game.handle_block_placement(target_sx, target_sy, active=active)
            return

        # 2. Consumable food or potion
        if active and (cat == CAT_CONSUMABLE or cat == "skillbook"):
            game.handle_right_click(target_sx, target_sy)
            return

        # 3. Weapons, tools, or bare hands attack / mining
        game.mining_cooldown = game.continuous_mine_rate
        game.handle_primary_action(target_sx, target_sy)

    def _execute_jump(self, game):
        """Executes jump or upward swimming."""
        game.player.is_resting = False
        if game.player.in_water:
            if game.player.vy > 0:
                game.player.vy = -1.8
            else:
                game.player.vy = max(-3.6, game.player.vy - 1.4)
        elif game.player.on_ground:
            from src.constants import PLAYER_JUMP_FORCE
            game.player.vy = PLAYER_JUMP_FORCE
            game.player.on_ground = False
            if game.sound_manager:
                has_clearance = True
                if hasattr(game.player, "is_head_blocked"):
                    has_clearance = not game.player.is_head_blocked(getattr(game, "world", None))
                if has_clearance:
                    game.sound_manager.play("jump")

    def _execute_dash(self, game):
        """Triggers dash skill or dodge roll."""
        cast = game.player.cast_skill_hotkey("V", game.particle_system, game.camera)
        if not cast and game.player.dash_timer <= 0:
            game.player.dash_timer = 0.28
            game.player.i_frame_timer = 0.35
            dash_speed = 9.5
            game.player.vx = math.cos(game.player.aim_angle) * dash_speed
            game.player.vy = math.sin(game.player.aim_angle) * dash_speed
            if abs(game.player.vx) > 0.3:
                game.player.facing_right = (game.player.vx > 0)
            if game.player.vy < 0:
                game.player.on_ground = False
            if game.sound_manager:
                game.sound_manager.play("jump")
            game.particle_system.spawn_sparks(game.player.center_x, game.player.center_y, (220, 240, 255), count=10)

    def _execute_direct_world_touch(self, px, py, game):
        """Targets world objects, blocks, interactive tiles, or enemies directly at touch location."""
        mouse_wx, mouse_wy = game.camera.screen_to_world(px, py)
        game.player.aim_angle = math.atan2(mouse_wy - game.player.center_y, mouse_wx - game.player.center_x)
        game.player.facing_right = (mouse_wx >= game.player.center_x)

        # 1. Check friendly NPC interaction (if town mechanics enabled)
        if getattr(game.world, "town_housing_enabled", False):
            clicked_npc = game.world.get_npc_at(mouse_wx, mouse_wy, radius=32.0)
            if clicked_npc and clicked_npc.can_interact(game.player):
                game.npc_dialogue.open(clicked_npc, game.player, game.world, game.combat)
                return

        # 2. Check interactive world tiles within reach (Chests, Doors, Beds, Altar, Clock)
        tx, ty = game.camera.screen_to_tile(px, py)
        tile_world_x = tx * SCALED_TILE
        tile_world_y = ty * SCALED_TILE
        reach = math.hypot(game.player.center_x - (tile_world_x + SCALED_TILE / 2),
                           game.player.center_y - (tile_world_y + SCALED_TILE / 2))
        if reach <= SCALED_TILE * 5.5:
            from src.constants import (
                TILE_DOOR_CLOSED, TILE_DOOR_OPEN, TILE_CHEST,
                TILE_DUNGEON_ALTAR, TILE_BED, TILE_GRANDFATHER_CLOCK
            )
            t_id = game.world.get_tile(tx, ty)
            if t_id in (TILE_DOOR_CLOSED, TILE_DOOR_OPEN, TILE_CHEST, TILE_DUNGEON_ALTAR, TILE_BED, TILE_GRANDFATHER_CLOCK):
                game.handle_right_click(px, py)
                return

        # 3. Check block / wall placement if active item is block/wall
        active = game.inventory.get_active_item()
        cat = active.data.get("cat") if active and hasattr(active, "data") else None
        if active and (cat in (CAT_BLOCK, CAT_WALL) or active.data.get("tile") is not None or active.data.get("wall") is not None):
            game.handle_block_placement(px, py, active=active)
            return

        # 4. Check consumable item (eating food / drinking potion / reading skillbook)
        if active and (cat == CAT_CONSUMABLE or cat == "skillbook"):
            game.handle_right_click(px, py)
            return

        # 5. Otherwise perform primary attack or mining
        game.mining_cooldown = game.continuous_mine_rate
        game.handle_primary_action(px, py)

    def quick_heal(self, player, inventory, sound_manager=None, particle_system=None):
        return quick_heal(player, inventory, sound_manager=sound_manager, particle_system=particle_system)

    def count_healing_items(self, inventory):
        return count_healing_items(inventory)

    def update(self, dt, player=None, inventory=None):
        self.reticle_pulse = (self.reticle_pulse + dt * 4.0) % (math.pi * 2)

        # Update ripples
        self.ripples = [r for r in self.ripples if r.update(dt)]

        # Update joystick
        self.joystick.update(dt)

        # Update buttons
        for btn in self.all_buttons:
            btn.update(dt)

        # Synchronize dynamic button states from player & inventory
        if player:
            # Skill Q, F, V, R cooldowns & levels
            key_pairs = [
                ("Q", self.btn_skill_q),
                ("F", self.btn_skill_f),
                ("V", self.btn_skill_v),
                ("R", self.btn_skill_r),
            ]
            for hotkey, btn in key_pairs:
                s_id = player.skills.hotkey_bindings.get(hotkey) if hasattr(player.skills, "hotkey_bindings") else None
                if not s_id:
                    mapping = {"Q": "power_slash", "F": "whirlwind", "V": "dash", "R": "fireball"}
                    s_id = mapping.get(hotkey)

                is_learned = s_id in player.skills.learned_skills if s_id else False
                btn.disabled = not is_learned

                s_info = SKILL_DEFINITIONS.get(s_id, {})
                s_name = s_info.get("name", hotkey)[:3].upper() if s_id else hotkey
                btn.label = s_name

                if is_learned and hasattr(player.skills, "get_skill_level"):
                    lvl = player.skills.get_skill_level(s_id)
                    btn.badge = f"Lv.{lvl}"
                else:
                    btn.badge = ""

                cd_left = player.skills.cooldowns.get(s_id, 0.0) if s_id else 0.0
                max_cd = s_info.get("cooldown", 1.0)
                btn.cooldown_pct = max(0.0, min(1.0, cd_left / max_cd)) if max_cd > 0 else 0.0
                btn.cooldown_time = cd_left

            # Synchronize Attack button icon/label to held item
            if inventory:
                active = inventory.get_active_item()
                if active:
                    cat = active.data.get("cat", "")
                    if cat == CAT_WEAPON:
                        self.btn_attack.label = "ATTACK"
                        self.btn_attack.sublabel = "WEAPON"
                    elif cat == CAT_TOOL:
                        self.btn_attack.label = "MINE"
                        self.btn_attack.sublabel = "TOOL"
                    elif cat in (CAT_BLOCK, CAT_WALL):
                        self.btn_attack.label = "PLACE"
                        self.btn_attack.sublabel = "BLOCK"
                    else:
                        self.btn_attack.label = "USE"
                        self.btn_attack.sublabel = "ITEM"
                else:
                    self.btn_attack.label = "ATTACK"
                    self.btn_attack.sublabel = "FIST"

        if inventory:
            h_count = self.count_healing_items(inventory)
            self.btn_heal.badge = f"x{h_count}"
            self.btn_heal.disabled = (h_count == 0)

    def render(self, surface, player=None, inventory=None, camera=None, game=None):
        if not self.is_visible():
            return

        active_game = game or getattr(self, "game", None)
        opacity = self.opacity

        # 1. Render active direct world touch reticle if contacting world
        if self.is_direct_touching and self.direct_touch_pos:
            tx, ty = self.direct_touch_pos
            pulse = math.sin(self.reticle_pulse) * 4.0
            r1 = max(6, int(18 + pulse))
            r2 = max(3, int(8 - pulse * 0.5))
            r_surf = pygame.Surface((r1 * 2 + 8, r1 * 2 + 8), pygame.SRCALPHA)
            rc = r_surf.get_width() // 2
            pygame.draw.circle(r_surf, (255, 235, 100, int(190 * opacity)), (rc, rc), r1, width=2)
            pygame.draw.circle(r_surf, (255, 120, 80, int(220 * opacity)), (rc, rc), r2, width=2)
            pygame.draw.line(r_surf, (255, 255, 255, int(160 * opacity)), (rc - r1 - 3, rc), (rc + r1 + 3, rc), 1)
            pygame.draw.line(r_surf, (255, 255, 255, int(160 * opacity)), (rc, rc - r1 - 3), (rc, rc + r1 + 3), 1)
            surface.blit(r_surf, (tx - rc, ty - rc))

        # 2. Render Top Bar Utility Buttons (always accessible)
        for btn in self.utility_buttons:
            btn.render(surface, self.font, self.font_sm, self.font_xs, opacity)

        # Check if modal window is open (inventory, character, dialogue, pause)
        is_paused = getattr(active_game, "paused", False)
        char_open = (getattr(getattr(active_game, "character_panel", None), "is_open", False) or
                     getattr(getattr(player, "character_panel", None), "is_open", False))
        dialogue_open = (getattr(getattr(active_game, "npc_dialogue", None), "is_open", False) or
                         getattr(getattr(player, "npc_dialogue", None), "is_open", False))
        inv_open = (getattr(inventory, "is_open", False) or
                    getattr(getattr(active_game, "inventory", None), "is_open", False))

        panels_open = inv_open or char_open or dialogue_open or is_paused
        if panels_open:
            # Render ripples and return (suppress virtual joystick & action buttons)
            for rip in self.ripples:
                rip.render(surface, opacity)
            return

        # 3. Render Virtual Joystick
        self.joystick.render(surface, self.font_sm, self.font_xs, opacity)

        # 4. Render Right Action Cluster
        for btn in self.action_buttons:
            btn.render(surface, self.font, self.font_sm, self.font_xs, opacity)

        # 5. Render Quick Skill Arc Cluster
        for btn in self.skill_buttons:
            btn.render(surface, self.font, self.font_sm, self.font_xs, opacity)

        # 6. Render Expanding Ripples
        for rip in self.ripples:
            rip.render(surface, opacity)
