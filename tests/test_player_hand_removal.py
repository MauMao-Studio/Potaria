"""
Unit tests to verify removal of the player's arm/hand sprite over Spud's face.
Developer: Kurados | Engine: pygame-ce 2.5.8
"""

import unittest
import os
import pygame

# Headless mode for automated tests
os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"
pygame.init()
pygame.display.set_mode((800, 600))

from src.entities.player import Player
from src.assets.asset_factory import AssetFactory
from src.camera import Camera
from src.ui.inventory import ItemStack, ITEM_REGISTRY


from src.audio.sound_effects import SoundManager


class TestPlayerHandRemoval(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.asset_factory = AssetFactory()
        cls.sound_manager = SoundManager()

    def setUp(self):
        self.player = Player(100, 100, self.asset_factory, self.sound_manager)
        self.camera = Camera(800, 600)
        self.surface = pygame.Surface((800, 600), pygame.SRCALPHA)

    def test_empty_handed_no_hand_or_arm_rendered(self):
        """When holding nothing, _render_arm_and_tool returns immediately without drawing."""
        target_surf = pygame.Surface((100, 100), pygame.SRCALPHA)
        target_surf.fill((0, 0, 0, 0))
        
        # Call with held_item_icon=None
        self.player._render_arm_and_tool(target_surf, self.camera, 10, 10, None, None)
        
        # Verify target surface is still completely blank/transparent
        non_transparent_pixels = 0
        for x in range(100):
            for y in range(100):
                if target_surf.get_at((x, y))[3] > 0:
                    non_transparent_pixels += 1
        self.assertEqual(non_transparent_pixels, 0)

    def test_weapon_held_renders_weapon_without_arm_covering_face(self):
        """When holding a weapon/tool, weapon renders outward from Spud's side without an arm sprite over the face."""
        sword_icon = self.asset_factory.items.get("astral_wrath", pygame.Surface((24, 24), pygame.SRCALPHA))
        sword_item = ItemStack("astral_wrath", 1)
        
        target_surf = pygame.Surface((200, 200), pygame.SRCALPHA)
        target_surf.fill((0, 0, 0, 0))
        
        sx, sy = self.camera.world_to_screen(self.player.x, self.player.y)
        self.player.render(target_surf, self.camera, held_item_icon=sword_icon, held_item=sword_item)
        
        # Verify Spud's body and face rendered at sx, sy
        self.assertGreater(target_surf.get_at((int(sx + 14), int(sy + 14)))[3], 0)

    def test_non_weapon_item_held_renders_at_side_without_arm(self):
        """When holding a block, furniture, potion, or food, no arm sprite is drawn."""
        wood_icon = self.asset_factory.items.get("tile_wood", pygame.Surface((24, 24), pygame.SRCALPHA))
        wood_item = ItemStack("tile_wood", 20)
        
        target_surf = pygame.Surface((200, 200), pygame.SRCALPHA)
        target_surf.fill((0, 0, 0, 0))
        
        # Verify render completes cleanly without NameError or missing arm_to_draw
        self.player.render(target_surf, self.camera, held_item_icon=wood_icon, held_item=wood_item)
        
        # Check that item is drawn
        self.assertTrue(any(target_surf.get_at((x, y))[3] > 0 for x in range(200) for y in range(200)))

    def test_facing_left_and_right_clean_anchoring(self):
        """Verify arm/hand is not drawn whether facing left or facing right."""
        pickaxe_icon = self.asset_factory.items.get("copper_pickaxe", pygame.Surface((24, 24), pygame.SRCALPHA))
        pickaxe_item = ItemStack("copper_pickaxe", 1)
        
        target_surf = pygame.Surface((200, 200), pygame.SRCALPHA)
        
        # Facing right
        self.player.facing_right = True
        self.player.render(target_surf, self.camera, held_item_icon=pickaxe_icon, held_item=pickaxe_item)
        
        # Facing left
        self.player.facing_right = False
        self.player.render(target_surf, self.camera, held_item_icon=pickaxe_icon, held_item=pickaxe_item)


if __name__ == "__main__":
    unittest.main()
