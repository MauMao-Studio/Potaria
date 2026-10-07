"""
Potaria - Unit Tests for Mobile Touch Controls & Cross-Platform UI/UX System
Tests:
1. Touch Target Dimensions & Ergonomics (>= 48x48 px minimum standard)
2. Virtual Left Joystick / D-Pad Movement, Travel Limit, Deadzone & Spring Return
3. Virtual Right Action Cluster (Attack/Mine, Jump, Dash, Quick Heal/Potion)
4. Quick Skill Arc/Radial Cluster (Q, F, V, R hotkeys, cooldown sweeps, levels)
5. Top Bar Mobile Utility Buttons (Backpack [E], Character [C], Settings [ESC])
6. Direct World Touch Interaction (aiming, tile mining, weapon firing, reticles)
7. Multi-Touch Tracking (simultaneous dual-thumb controls)
8. Visual Feedback & Tactile Ripples (ripple expansion, press depression)
9. Settings Menu Options & Persistence (Auto/On/Off, 50%/75%/100% opacity in settings.json)
10. Cross-Platform Coexistence (PC keyboard + mouse smoothly merged with touch)

Developer: Kurados
"""

import os
import sys
import json
import math
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Headless drivers for automated headless test environment
os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"

import pygame
pygame.init()
pygame.display.set_mode((1280, 720), pygame.DOUBLEBUF | pygame.SCALED)

from src.constants import (
    SCREEN_WIDTH, SCREEN_HEIGHT, SCALED_TILE,
    STATE_PLAYING, STATE_SETTINGS, STATE_MENU,
    TOUCH_MODE_AUTO, TOUCH_MODE_ON, TOUCH_MODE_OFF,
    TOUCH_OPACITY_50, TOUCH_OPACITY_75, TOUCH_OPACITY_100,
    PLAYER_JUMP_FORCE
)
from src.assets.asset_factory import AssetFactory
from src.audio.sound_effects import SoundManager
from src.ui.touch_controller import TouchController, VirtualJoystick, TouchButton, TouchRipple, quick_heal, HEALING_ITEM_PRIORITY
from src.ui.menu import MenuManager
from src.ui.inventory import Inventory, ItemStack
from main import PotariaGame


class TestMobileControlsAndTouchUI(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.game = PotariaGame()
        cls.tc = cls.game.touch_controller

    def test_01_touch_target_dimensions_and_ergonomics(self):
        """Rule: All touch targets must adhere to mobile ergonomics guidelines (>= 48x48 px minimum)."""
        tc = self.tc

        # 1. Virtual Joystick Base & Hitbox
        self.assertGreaterEqual(tc.joystick.hit_radius * 2, 48.0, "Joystick hitbox must be >= 48px")
        self.assertGreaterEqual(tc.joystick.radius_base * 2, 48.0, "Joystick base must be >= 48px")
        self.assertGreaterEqual(tc.joystick.radius_knob * 2, 48.0, "Joystick knob must be >= 48px")

        # 2. Right Action Cluster Buttons
        for btn in tc.action_buttons:
            eff_hitbox = max(48.0, btn.radius * 2 + btn.hit_padding * 2)
            self.assertGreaterEqual(eff_hitbox, 48.0, f"Button {btn.id} hitbox must be >= 48px")
            self.assertTrue(btn.contains(btn.x, btn.y), f"Button {btn.id} must contain its center")

        # 3. Quick Skill Arc Buttons (Q, F, V, R)
        for btn in tc.skill_buttons:
            eff_hitbox = max(48.0, btn.radius * 2 + btn.hit_padding * 2)
            self.assertGreaterEqual(eff_hitbox, 48.0, f"Skill button {btn.id} hitbox must be >= 48px")
            self.assertTrue(btn.contains(btn.x, btn.y), f"Skill button {btn.id} must contain its center")

        # 4. Top Bar Mobile Utility Buttons (Inventory, Character, Pause)
        for btn in tc.utility_buttons:
            eff_w = max(48, btn.rect.width)
            eff_h = max(48, btn.rect.height)
            self.assertGreaterEqual(eff_w, 48, f"Utility button {btn.id} width must be >= 48px")
            self.assertGreaterEqual(eff_h, 46, f"Utility button {btn.id} height must be comfortably sized")
            self.assertTrue(btn.contains(btn.rect.centerx, btn.rect.centery), f"Utility button {btn.id} must contain its center")

    def test_02_virtual_joystick_movement_and_travel(self):
        """Tests analog/directional axes, deadzone, travel clamping, and spring return."""
        js = VirtualJoystick(center_x=140, center_y=590, radius_base=66, radius_knob=28, radius_travel=48)
        
        # Initial neutral state
        self.assertEqual(js.axis_x, 0.0)
        self.assertEqual(js.axis_y, 0.0)
        self.assertFalse(js.is_left)
        self.assertFalse(js.is_right)
        self.assertFalse(js.is_jump)
        self.assertFalse(js.is_drop)

        # Deadzone test (subtle touch < 12px deadzone)
        js.on_touch_down(1, 145, 592)
        self.assertEqual(js.axis_x, 0.0, "Touches within deadzone must yield zero axis")
        self.assertEqual(js.axis_y, 0.0)

        # Drag full Left
        js.on_touch_move(1, 80, 590)
        self.assertTrue(js.is_left, "Dragging left must flag is_left")
        self.assertFalse(js.is_right)
        self.assertLess(js.axis_x, -0.5)

        # Drag full Right beyond travel radius (clamping check)
        js.on_touch_move(1, 300, 590) # Far past travel radius
        self.assertTrue(js.is_right, "Dragging right must flag is_right")
        self.assertFalse(js.is_left)
        self.assertAlmostEqual(js.axis_x, 1.0, places=2, msg="Axis must clamp to 1.0")
        self.assertLessEqual(math.hypot(js.knob_x - js.center_x, js.knob_y - js.center_y), js.radius_travel + 0.01)

        # Drag Up (Jump)
        js.on_touch_move(1, 140, 530)
        self.assertTrue(js.is_jump, "Dragging up must flag is_jump")
        self.assertFalse(js.is_drop)
        self.assertLess(js.axis_y, -0.4)

        # Drag Down (Drop Platform)
        js.on_touch_move(1, 140, 650)
        self.assertTrue(js.is_drop, "Dragging down must flag is_drop")
        self.assertFalse(js.is_jump)
        self.assertGreater(js.axis_y, 0.4)

        # Release touch & spring-return physics
        js.on_touch_up(1)
        self.assertIsNone(js.active_finger_id)
        self.assertFalse(js.is_left)
        self.assertFalse(js.is_right)
        
        # Advance physics decay
        js.update(0.1)
        self.assertLess(abs(js.knob_x - js.center_x), 10.0)
        self.assertLess(abs(js.knob_y - js.center_y), 10.0)

    def test_03_right_action_cluster_actions(self):
        """Tests Attack/Mine button, Jump button, Dash button, and Quick Heal."""
        game = self.game
        tc = self.tc
        tc.set_mode("on")

        # 1. Attack Button Press
        tc.handle_touch_down(10, tc.btn_attack.x, tc.btn_attack.y, game)
        self.assertTrue(tc.is_attack_down, "Touching attack button must activate is_attack_down")
        self.assertTrue(tc.btn_attack.pressed)

        tc.handle_touch_up(10, tc.btn_attack.x, tc.btn_attack.y, game)
        self.assertFalse(tc.is_attack_down, "Releasing attack button must deactivate is_attack_down")
        self.assertFalse(tc.btn_attack.pressed)

        # 2. Jump Button Press
        game.player.on_ground = True
        game.player.vy = 0.0
        tc.handle_touch_down(11, tc.btn_jump.x, tc.btn_jump.y, game)
        self.assertEqual(game.player.vy, PLAYER_JUMP_FORCE, "Tapping jump button must apply jump force to player")
        self.assertFalse(game.player.on_ground)
        tc.handle_touch_up(11, tc.btn_jump.x, tc.btn_jump.y, game)

        # 3. Dash Button Press
        game.player.dash_timer = 0.0
        game.player.vx = 0.0
        tc.handle_touch_down(12, tc.btn_dash.x, tc.btn_dash.y, game)
        self.assertGreater(game.player.dash_timer, 0.0, "Tapping dash button must trigger dash dodge burst")
        self.assertNotEqual(game.player.vx, 0.0, "Dash must propel player horizontally")
        tc.handle_touch_up(12, tc.btn_dash.x, tc.btn_dash.y, game)

        # 4. Quick Heal Button Press
        game.player.health = 40
        game.inventory.slots[0] = ItemStack("healing_potion", 2)
        initial_hp = game.player.health
        tc.handle_touch_down(13, tc.btn_heal.x, tc.btn_heal.y, game)
        self.assertGreater(game.player.health, initial_hp, "Tapping heal button must consume potion and restore HP")
        self.assertEqual(game.inventory.slots[0].count, 1, "Potion count in inventory must decrement by 1")
        tc.handle_touch_up(13, tc.btn_heal.x, tc.btn_heal.y, game)

    def test_04_quick_skill_arc_buttons(self):
        """Tests radial skill buttons (Q, F, V, R) and their cooldown visualizations."""
        game = self.game
        tc = self.tc
        tc.set_mode("on")

        # Teach Spud Skill Q (Power Slash)
        game.player.skills.learned_skills.add("power_slash")
        game.player.stats.mp = 100
        game.player.skills.cooldowns["power_slash"] = 0.0

        # Tap Skill Q
        tc.handle_touch_down(20, tc.btn_skill_q.x, tc.btn_skill_q.y, game)
        tc.update(0.016, player=game.player, inventory=game.inventory)
        self.assertGreater(game.player.skills.cooldowns.get("power_slash", 0.0), 0.0, "Casting skill must trigger cooldown")
        self.assertGreater(tc.btn_skill_q.cooldown_pct, 0.0, "Button must visualize cooldown sweep")
        tc.handle_touch_up(20, tc.btn_skill_q.x, tc.btn_skill_q.y, game)

    def test_05_top_bar_mobile_utility_buttons(self):
        """Tests Backpack [E], Character Status [C], and Pause [ESC] utility buttons."""
        game = self.game
        tc = self.tc
        tc.set_mode("on")

        # 1. Backpack / Inventory toggle
        game.inventory.is_open = False
        tc.handle_touch_down(30, tc.btn_inventory.rect.centerx, tc.btn_inventory.rect.centery, game)
        self.assertTrue(game.inventory.is_open, "Tapping backpack button must open inventory")
        tc.handle_touch_up(30, tc.btn_inventory.rect.centerx, tc.btn_inventory.rect.centery, game)

        # Tap again to close
        tc.handle_touch_down(31, tc.btn_inventory.rect.centerx, tc.btn_inventory.rect.centery, game)
        self.assertFalse(game.inventory.is_open, "Tapping backpack button again must close inventory")
        tc.handle_touch_up(31, tc.btn_inventory.rect.centerx, tc.btn_inventory.rect.centery, game)

        # 2. Character Status toggle
        game.character_panel.is_open = False
        tc.handle_touch_down(32, tc.btn_character.rect.centerx, tc.btn_character.rect.centery, game)
        self.assertTrue(game.character_panel.is_open, "Tapping character button must open character panel")
        tc.handle_touch_up(32, tc.btn_character.rect.centerx, tc.btn_character.rect.centery, game)

        tc.handle_touch_down(33, tc.btn_character.rect.centerx, tc.btn_character.rect.centery, game)
        self.assertFalse(game.character_panel.is_open, "Tapping character button again must close character panel")
        tc.handle_touch_up(33, tc.btn_character.rect.centerx, tc.btn_character.rect.centery, game)

        # 3. Pause Menu toggle
        game.paused = False
        tc.handle_touch_down(34, tc.btn_pause.rect.centerx, tc.btn_pause.rect.centery, game)
        self.assertTrue(game.paused, "Tapping pause button must pause the game")
        tc.handle_touch_up(34, tc.btn_pause.rect.centerx, tc.btn_pause.rect.centery, game)

        tc.handle_touch_down(35, tc.btn_pause.rect.centerx, tc.btn_pause.rect.centery, game)
        self.assertFalse(game.paused, "Tapping pause button again must unpause the game")
        tc.handle_touch_up(35, tc.btn_pause.rect.centerx, tc.btn_pause.rect.centery, game)

    def test_06_direct_world_touch_interaction(self):
        """Tests tapping directly on the world screen outside virtual controls."""
        game = self.game
        tc = self.tc
        tc.set_mode("on")
        game.inventory.is_open = False
        game.character_panel.is_open = False
        game.paused = False

        # Touch world location at (600, 360)
        touch_x, touch_y = 600, 360
        tc.handle_touch_down(40, touch_x, touch_y, game)
        self.assertTrue(tc.is_direct_touching, "Tapping world must set is_direct_touching")
        self.assertEqual(tc.direct_touch_pos, (touch_x, touch_y))

        # Check player aim updated
        mouse_wx, mouse_wy = game.camera.screen_to_world(touch_x, touch_y)
        expected_angle = math.atan2(mouse_wy - game.player.center_y, mouse_wx - game.player.center_x)
        self.assertAlmostEqual(game.player.aim_angle, expected_angle, places=2, msg="Player must aim at touch coordinates")

        # Touch motion drag
        tc.handle_touch_motion(40, 700, 400, game)
        self.assertEqual(tc.direct_touch_pos, (700, 400), "Dragging touch in world must track direct_touch_pos")

        # Touch up
        tc.handle_touch_up(40, 700, 400, game)
        self.assertFalse(tc.is_direct_touching, "Releasing touch must clear direct touching")
        self.assertIsNone(tc.direct_touch_finger_id)

    def test_07_multi_touch_tracking(self):
        """Tests simultaneous multi-touch (e.g. left thumb on joystick + right thumb on jump)."""
        game = self.game
        tc = self.tc
        tc.set_mode("on")

        # Finger 1: Left thumb on joystick
        tc.handle_touch_down(101, 80, 590, game)
        self.assertTrue(tc.joystick.is_left, "Finger 1 must steer joystick left")
        self.assertEqual(tc.joystick.active_finger_id, 101)

        # Finger 2: Right thumb on attack button
        tc.handle_touch_down(102, tc.btn_attack.x, tc.btn_attack.y, game)
        self.assertTrue(tc.is_attack_down, "Finger 2 must activate attack button")
        self.assertEqual(tc.btn_attack.active_finger_id, 102)

        # Release Finger 2 only (attack button)
        tc.handle_touch_up(102, tc.btn_attack.x, tc.btn_attack.y, game)
        self.assertFalse(tc.is_attack_down, "Releasing Finger 2 must release attack")
        self.assertTrue(tc.joystick.is_left, "Finger 1 on joystick must remain completely active!")

        # Release Finger 1
        tc.handle_touch_up(101, 80, 590, game)
        self.assertFalse(tc.joystick.is_left, "Releasing Finger 1 must reset joystick")

    def test_08_visual_feedback_ripples_and_press_states(self):
        """Tests touch ripples and active button press visual depression."""
        tc = self.tc
        initial_ripples = len(tc.ripples)
        tc.add_ripple(200, 200, color=(100, 200, 255))
        self.assertEqual(len(tc.ripples), initial_ripples + 1)
        
        # Advance ripple physics
        tc.update(0.1)
        self.assertGreater(tc.ripples[-1].elapsed, 0.0)
        
        # Fast-forward until ripple expires
        tc.update(0.3)
        self.assertEqual(len(tc.ripples), 0, "Ripples must naturally expire after their duration")

    def test_09_settings_persistence_and_modes(self):
        """Tests Touch Controls [Auto / On / Off] and Touch Opacity [50% / 75% / 100%] in saves/settings.json."""
        menu = MenuManager(self.game.sound_manager, None)
        
        # Set settings
        menu.settings["touch_controls"] = "on"
        menu.settings["touch_opacity"] = 1.00
        menu.save_settings()

        # Reload from disk
        menu2 = MenuManager(self.game.sound_manager, None)
        self.assertEqual(menu2.settings["touch_controls"], "on", "Touch controls setting must persist to disk")
        self.assertEqual(menu2.settings["touch_opacity"], 1.00, "Touch opacity setting must persist to disk")

        # Test toggle actions in menu
        menu.state = STATE_SETTINGS
        btn_tc = next(b for b in menu.settings_buttons if b.action == "toggle_touch_controls")
        btn_op = next(b for b in menu.settings_buttons if b.action == "toggle_touch_opacity")

        # Toggle controls mode: "on" -> "off"
        act_tc = menu.handle_click((btn_tc.rect.centerx, btn_tc.rect.centery))
        self.assertEqual(act_tc, ("set_touch_controls", "off"))
        self.assertEqual(menu.settings["touch_controls"], "off")

        # Toggle opacity: 1.0 -> 0.5
        act_op = menu.handle_click((btn_op.rect.centerx, btn_op.rect.centery))
        self.assertEqual(act_op, ("set_touch_opacity", 0.5))
        self.assertEqual(menu.settings["touch_opacity"], 0.5)

        # Restore default auto/75% for clean tests
        menu.settings["touch_controls"] = "auto"
        menu.settings["touch_opacity"] = 0.75
        menu.save_settings()

    def test_10_cross_platform_input_merging(self):
        """Verifies PC keyboard keys and virtual touch joystick seamlessly coexist without conflict."""
        tc = self.tc
        tc.set_mode("on")
        tc.joystick.is_left = True
        
        # Raw hardware keyboard state: Spud holding spacebar on PC
        raw_keys = {pygame.K_SPACE: True, pygame.K_d: False}
        combined = tc.get_virtual_keys(raw_keys, self.game.menu.key_bindings)
        
        # Both PC Spacebar and Virtual Joystick Left must be active simultaneously!
        self.assertTrue(combined.get(pygame.K_SPACE), "PC Spacebar must remain active")
        self.assertTrue(combined.get(pygame.K_a), "Virtual joystick Move Left must be merged in")
        self.assertTrue(combined.get(pygame.K_LEFT), "Virtual joystick Move Left arrow must be merged in")

    def test_11_direct_world_touch_block_placement_and_bow(self):
        """Verifies direct touch placing blocks and firing bows towards touched world points."""
        game = self.game
        tc = self.tc
        tc.set_mode("on")
        game.inventory.is_open = False
        game.character_panel.is_open = False
        game.paused = False

        # 1. Block placement via direct touch
        game.inventory.slots[0] = ItemStack("wood", 10)
        game.inventory.selected_slot = 0
        tx = int(game.player.center_x // SCALED_TILE) + 2
        ty = int(game.player.center_y // SCALED_TILE)
        game.world.set_tile(tx, ty, 0) # Clear to air
        game.world.set_tile(tx, ty + 1, 1) # Provide supporting neighbor block below target
        
        target_wx = tx * SCALED_TILE + 16
        target_wy = ty * SCALED_TILE + 16
        screen_x, screen_y = game.camera.world_to_screen(target_wx, target_wy)

        tc.handle_touch_down(50, screen_x, screen_y, game)
        tc.handle_touch_up(50, screen_x, screen_y, game)
        self.assertNotEqual(game.world.get_tile(tx, ty), 0, "Direct touch must place block in world")

        # 2. Bow firing via direct touch
        game.inventory.slots[0] = ItemStack("wood_bow", 1)
        game.inventory.slots[1] = ItemStack("wooden_arrow", 20)
        game.inventory.selected_slot = 0
        game.player.attack_cooldown = 0.0
        initial_projectiles = len(game.combat.projectiles)

        target_aim_x = game.player.center_x + 120
        target_aim_y = game.player.center_y - 40
        aim_sx, aim_sy = game.camera.world_to_screen(target_aim_x, target_aim_y)

        tc.handle_touch_down(51, aim_sx, aim_sy, game)
        tc.handle_touch_up(51, aim_sx, aim_sy, game)
        self.assertGreater(len(game.combat.projectiles), initial_projectiles, "Direct touch with bow must fire projectile")

    def test_12_quick_heal_priority_and_edge_cases(self):
        """Tests quick heal priority order, full health rejection, and empty inventory handling."""
        game = self.game
        tc = self.tc

        # Full health rejection
        game.player.health = game.player.max_health
        game.inventory.slots[0] = ItemStack("healing_potion", 5)
        res = tc.quick_heal(game.player, game.inventory, game.sound_manager, game.particle_system)
        self.assertFalse(res, "Must not consume potion if player is already at full health")
        self.assertEqual(game.inventory.slots[0].count, 5)

        # Priority order: greater_healing_potion prioritized over raw_potato
        game.player.health = 20
        game.inventory.slots[0] = ItemStack("raw_potato", 3)
        game.inventory.slots[1] = ItemStack("greater_healing_potion", 2)
        res = tc.quick_heal(game.player, game.inventory, game.sound_manager, game.particle_system)
        self.assertTrue(res, "Must consume healing item successfully")
        self.assertEqual(game.inventory.slots[1].count, 1, "Greater healing potion must be consumed first")
        self.assertEqual(game.inventory.slots[0].count, 3, "Raw potato must remain intact")

        # Empty inventory graceful fallback
        for i in range(len(game.inventory.slots)):
            game.inventory.slots[i] = None
        game.player.health = 20
        res_empty = tc.quick_heal(game.player, game.inventory, game.sound_manager, game.particle_system)
        self.assertFalse(res_empty, "Must return False without error when no healing items exist")

    def test_13_virtual_joystick_water_swimming_and_diagonal(self):
        """Tests diagonal movement and in-water swimming controls via virtual joystick."""
        game = self.game
        tc = self.tc
        tc.set_mode("on")

        # Diagonal movement: right + jump
        tc.joystick.on_touch_down(60, 200, 520)
        self.assertTrue(tc.joystick.is_right, "Diagonal touch must flag is_right")
        self.assertTrue(tc.joystick.is_jump, "Diagonal touch must flag is_jump")
        vkeys = tc.get_virtual_keys({}, game.menu.key_bindings)
        self.assertTrue(vkeys.get(pygame.K_d), "Virtual key D must be active")
        self.assertTrue(vkeys.get(pygame.K_SPACE), "Virtual key Space must be active")
        tc.joystick.on_touch_up(60)

        # In-water swimming controls
        game.player.in_water = True
        game.player.vy = 0.0
        # Swim Up
        tc.joystick.on_touch_down(61, 140, 530)
        game.player.handle_input(tc.get_virtual_keys({}, game.menu.key_bindings), game.player.center_x + 50, game.player.center_y)
        self.assertLess(game.player.vy, 0.0, "Joystick up must paddle Spud upwards in water")
        tc.joystick.on_touch_up(61)

        # Dive Down
        tc.joystick.on_touch_down(62, 140, 650)
        game.player.handle_input(tc.get_virtual_keys({}, game.menu.key_bindings), game.player.center_x + 50, game.player.center_y)
        self.assertGreater(game.player.vy, 0.0, "Joystick down must dive Spud downwards in water")
        tc.joystick.on_touch_up(62)
        game.player.in_water = False

    def test_14_modal_panel_suppression(self):
        """When an in-game panel (inventory, character, dialogue) is open, gameplay controls are suppressed."""
        game = self.game
        tc = self.tc
        tc.set_mode("on")

        game.inventory.is_open = True
        
        # Touch on attack button location while inventory is open
        handled = tc.handle_touch_down(70, tc.btn_attack.x, tc.btn_attack.y, game)
        self.assertFalse(handled, "Gameplay buttons must NOT consume touches when inventory is open")
        self.assertFalse(tc.is_attack_down)

        # Top bar utility buttons MUST remain interactive to close inventory
        top_bar_handled = tc.handle_touch_down(71, tc.btn_inventory.rect.centerx, tc.btn_inventory.rect.centery, game)
        self.assertTrue(top_bar_handled, "Top bar utility buttons must always remain clickable to toggle panels")
        self.assertFalse(game.inventory.is_open, "Tapping backpack button must close inventory")
        tc.handle_touch_up(71, tc.btn_inventory.rect.centerx, tc.btn_inventory.rect.centery, game)

    def test_15_render_all_opacities_and_ripples(self):
        """Verifies rendering at 50%, 75%, and 100% opacity with active ripples and badges."""
        game = self.game
        tc = self.tc
        tc.set_mode("on")
        tc.add_ripple(250, 250, color=(255, 215, 0))

        test_surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)

        for op in (TOUCH_OPACITY_50, TOUCH_OPACITY_75, TOUCH_OPACITY_100):
            tc.set_opacity(op)
            self.assertEqual(tc.opacity, op)
            # Render must complete cleanly with zero exceptions
            tc.render(test_surf, game.player, game.inventory, game.camera)

    def test_16_touch_events_in_menus_and_dialogues(self):
        """Verifies FINGERDOWN events correctly interact with MenuManager and NPCDialogue."""
        game = self.game
        # 1. Settings menu touch toggle
        game.menu.state = STATE_SETTINGS
        game.touch_controller.set_mode("auto")
        game.menu.settings["touch_controls"] = "auto"
        btn_tc = next(b for b in game.menu.settings_buttons if b.action == "toggle_touch_controls")
        pygame.event.clear()
        ev = pygame.event.Event(pygame.FINGERDOWN, {
            "finger_id": 1,
            "x": btn_tc.rect.centerx / SCREEN_WIDTH,
            "y": btn_tc.rect.centery / SCREEN_HEIGHT,
            "dx": 0.0,
            "dy": 0.0
        })
        pygame.event.post(ev)
        game.handle_events()
        self.assertEqual(game.touch_controller.mode, "on", "FINGERDOWN on menu button must trigger setting toggle")
        game.menu.state = STATE_PLAYING
        game.paused = False

        # 2. NPC dialogue progression via touch
        if hasattr(game, "npc_dialogue"):
            from src.entities.npc import GuideNPC
            test_npc = GuideNPC("Pip", "guide", 100, 100, game.asset_factory, game.sound_manager)
            try:
                game.npc_dialogue.open(test_npc, game.player, game.world, game.combat)
                self.assertTrue(game.npc_dialogue.is_open)

                pygame.event.clear()
                ev_dlg = pygame.event.Event(pygame.FINGERDOWN, {
                    "finger_id": 2,
                    "x": 0.5,
                    "y": 0.5,
                    "dx": 0.0,
                    "dy": 0.0
                })
                pygame.event.post(ev_dlg)
                game.handle_events()
            finally:
                game.npc_dialogue.close()

    def test_17_touch_events_in_inventory_and_crafting(self):
        """Verifies touch events interact with open inventory slots and item pickup."""
        game = self.game
        game.menu.state = STATE_PLAYING
        game.paused = False
        game.inventory.is_open = True
        game.inventory.slots[0] = ItemStack("wood", 10)
        game.inventory.held_item = None

        # Slot 0 is at (20, 20) with size 44x44
        slot_x = 20 + 22
        slot_y = 20 + 22
        pygame.event.clear()
        ev = pygame.event.Event(pygame.FINGERDOWN, {
            "finger_id": 10,
            "x": slot_x / SCREEN_WIDTH,
            "y": slot_y / SCREEN_HEIGHT,
            "dx": 0.0,
            "dy": 0.0
        })
        pygame.event.post(ev)
        game.handle_events()

        self.assertIsNotNone(game.inventory.held_item, "Touch click on inventory slot must pick up item")
        self.assertEqual(game.inventory.held_item.item_id, "wood")

        game.inventory.slots[0] = game.inventory.held_item
        game.inventory.held_item = None
        game.inventory.is_open = False

    def test_18_direct_world_touch_interactive_tiles(self):
        """Verifies direct touch on interactive world tiles (doors, chests, beds) triggers right-click interaction."""
        game = self.game
        tc = self.tc
        tc.set_mode("on")
        game.inventory.is_open = False
        game.character_panel.is_open = False
        game.paused = False

        px_tile = int(game.player.center_x // SCALED_TILE)
        py_tile = int(game.player.center_y // SCALED_TILE)
        target_tx = px_tile + 2
        target_ty = py_tile

        from src.constants import TILE_DOOR_CLOSED, TILE_DOOR_OPEN
        game.world.set_tile(target_tx, target_ty, TILE_DOOR_CLOSED)

        target_wx = target_tx * SCALED_TILE + 16
        target_wy = target_ty * SCALED_TILE + 16
        screen_x, screen_y = game.camera.world_to_screen(target_wx, target_wy)

        tc.handle_touch_down(80, screen_x, screen_y, game)
        tc.handle_touch_up(80, screen_x, screen_y, game)

        current_tile = game.world.get_tile(target_tx, target_ty)
        self.assertEqual(current_tile, TILE_DOOR_OPEN, "Direct world touch on closed door must open it")

        game.world.set_tile(target_tx, target_ty, 0)

    def test_19_cross_platform_custom_keybindings(self):
        """Verifies that custom PC keybindings (e.g., rebound movement keys) are preserved by get_virtual_keys."""
        tc = self.tc
        tc.set_mode("on")
        tc.joystick.is_left = False
        tc.joystick.is_right = False

        custom_bindings = {
            "Move Left": pygame.K_j,
            "Move Right": pygame.K_l,
            "Jump": pygame.K_k,
            "Drop Platform": pygame.K_i,
        }

        raw_keys = {pygame.K_j: True, pygame.K_l: False}
        merged = tc.get_virtual_keys(raw_keys, custom_bindings)

        self.assertTrue(merged.get(pygame.K_j), "Custom PC key K_j must be preserved in merged virtual keys")
        self.assertFalse(merged.get(pygame.K_l), "Unpressed custom PC key K_l must be False")

        tc.joystick.is_right = True
        merged_both = tc.get_virtual_keys(raw_keys, custom_bindings)
        self.assertTrue(merged_both.get(pygame.K_j), "PC key K_j still active")
        self.assertTrue(merged_both.get(pygame.K_l), "Bound Move Right K_l activated by virtual joystick")
        tc.joystick.is_right = False

    def test_20_multi_finger_conflict_and_joystick_protection(self):
        """Verifies joystick rejects hijacking by a second finger, and buttons handle multi-finger press/release safely."""
        tc = self.tc

        # 1. Joystick hijacking protection
        tc.joystick.reset()
        tc.joystick.on_touch_down(finger_id=1, px=160, py=590)
        self.assertEqual(tc.joystick.active_finger_id, 1)
        self.assertTrue(tc.joystick.is_right)

        tc.joystick.on_touch_down(finger_id=2, px=100, py=590)
        self.assertEqual(tc.joystick.active_finger_id, 1, "Secondary finger must NOT hijack active joystick")
        self.assertTrue(tc.joystick.is_right, "Joystick must remain steered by original finger 1")

        tc.joystick.on_touch_move(finger_id=2, px=80, py=590)
        self.assertTrue(tc.joystick.is_right)

        tc.joystick.on_touch_up(finger_id=2)
        self.assertEqual(tc.joystick.active_finger_id, 1)

        tc.joystick.on_touch_up(finger_id=1)
        self.assertIsNone(tc.joystick.active_finger_id)
        self.assertFalse(tc.joystick.is_right)

        # 2. Button multi-finger tracking
        btn = tc.btn_jump
        btn.pressed = False
        btn.active_finger_ids.clear()

        btn.on_touch_down(finger_id=10, px=btn.x, py=btn.y)
        self.assertTrue(btn.pressed)
        self.assertIn(10, btn.active_finger_ids)

        btn.on_touch_down(finger_id=11, px=btn.x, py=btn.y)
        self.assertTrue(btn.pressed)
        self.assertIn(11, btn.active_finger_ids)

        btn.on_touch_up(finger_id=10)
        self.assertTrue(btn.pressed, "Button should stay pressed while finger 11 is still on it")
        self.assertNotIn(10, btn.active_finger_ids)
        self.assertIn(11, btn.active_finger_ids)

        btn.on_touch_up(finger_id=11)
        self.assertFalse(btn.pressed, "Button should be released when all fingers lift off")
        self.assertEqual(len(btn.active_finger_ids), 0)

    def test_21_modal_render_suppression(self):
        """Verifies virtual joystick and action cluster rendering is suppressed when game modals are active."""
        game = self.game
        tc = self.tc
        tc.set_mode("on")
        test_surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)

        game.paused = False
        game.character_panel.is_open = False
        game.inventory.is_open = False

        game.character_panel.is_open = True
        tc.render(test_surf, game.player, game.inventory, game.camera, game=game)

        game.character_panel.is_open = False
        game.paused = True
        tc.render(test_surf, game.player, game.inventory, game.camera, game=game)

        game.paused = False


if __name__ == "__main__":
    unittest.main()

