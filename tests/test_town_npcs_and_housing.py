"""
Tests for Potaria Town NPCs, Housing Settlement & Settlement Economy Systems.
Developer: Kurados
"""

import os
import unittest
import pygame
from src.constants import (
    SCALED_TILE, TILE_AIR, TILE_WOOD, TILE_WOOD_PLANKS, WALL_WOOD,
    TILE_DOOR_CLOSED, TILE_TORCH, TILE_TABLE, TILE_CHAIR, TILE_BED,
    TILE_BLIGHTSTONE, CAT_WEAPON
)
from src.assets.asset_factory import AssetFactory
from src.audio.sound_effects import SoundManager
from src.world.world import World
from src.entities.player import Player
from src.ui.inventory import Inventory, ItemStack
from src.combat.combat_system import CombatManager
from src.entities.npc import TownNPC, GuideNPC, MerchantNPC, NurseNPC, BlacksmithNPC
from src.ui.npc_dialogue import NPCDialogueWindow
from src.world.save_manager import save_world, load_world, delete_world


class TestTownNPCsAndHousing(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pygame.init()
        os.environ["SDL_VIDEODRIVER"] = "dummy"
        pygame.display.set_mode((800, 600))
        cls.asset_factory = AssetFactory()
        cls.sound_manager = SoundManager()

    def setUp(self):
        self.world = World(self.asset_factory, seed=42)
        sp_x, sp_y = self.world.spawn_point
        self.player = Player(sp_x, sp_y, self.asset_factory, self.sound_manager)
        self.inventory = Inventory(self.asset_factory)
        self.player.inventory = self.inventory
        self.combat = CombatManager(self.asset_factory, self.sound_manager, None, None)

    def _build_test_house(self, start_tx, start_ty, width=8, height=6):
        """Constructs an enclosed valid room with walls, door, torch, table, and chair."""
        # Clear room and fill background walls
        for x in range(start_tx, start_tx + width):
            for y in range(start_ty, start_ty + height):
                self.world.set_tile(x, y, TILE_AIR)
                self.world.set_wall(x, y, WALL_WOOD)

        # Floor and ceiling
        for x in range(start_tx, start_tx + width):
            self.world.set_tile(x, start_ty + height - 1, TILE_WOOD_PLANKS)
            self.world.set_tile(x, start_ty, TILE_WOOD_PLANKS)

        # Left and right walls
        for y in range(start_ty + 1, start_ty + height - 1):
            self.world.set_tile(start_tx, y, TILE_WOOD_PLANKS)
            self.world.set_tile(start_tx + width - 1, y, TILE_WOOD_PLANKS)

        # Door on left side
        self.world.set_tile(start_tx, start_ty + height - 2, TILE_DOOR_CLOSED)

        # Furniture inside
        self.world.set_tile(start_tx + 2, start_ty + 2, TILE_TORCH)
        self.world.set_tile(start_tx + 3, start_ty + height - 2, TILE_TABLE)
        self.world.set_tile(start_tx + 4, start_ty + height - 2, TILE_CHAIR)

        return (start_tx + width // 2, start_ty + height // 2)

    def test_01_valid_house_detection(self):
        """A properly built house meets all validation criteria."""
        cx, cy = self._build_test_house(100, 50, width=8, height=6)
        is_valid, msg, home_x, home_y = self.world.check_house_validity(cx, cy)
        self.assertTrue(is_valid, f"Expected valid house, got: {msg}")
        self.assertEqual(msg, "Valid shelter suitable for Town NPC!")
        self.assertTrue(self.world.check_shelter(cx, cy))

    def test_02_invalid_house_missing_door(self):
        """A sealed box without a door or platform is not a valid house."""
        cx, cy = self._build_test_house(120, 50, width=8, height=6)
        # Seal the door with solid planks
        self.world.set_tile(120, 50 + 6 - 2, TILE_WOOD_PLANKS)
        is_valid, msg, _, _ = self.world.check_house_validity(cx, cy)
        self.assertFalse(is_valid)
        self.assertIn("entrance", msg.lower())

    def test_03_invalid_house_missing_light_source(self):
        """A house missing a torch, candelabra, or fireplace is not valid."""
        cx, cy = self._build_test_house(140, 50, width=8, height=6)
        # Remove torch
        self.world.set_tile(140 + 2, 50 + 2, TILE_AIR)
        is_valid, msg, _, _ = self.world.check_house_validity(cx, cy)
        self.assertFalse(is_valid)
        self.assertIn("light", msg.lower())

    def test_04_invalid_house_missing_comfort_item(self):
        """A house missing a chair or bed is not valid."""
        cx, cy = self._build_test_house(160, 50, width=8, height=6)
        # Remove chair
        self.world.set_tile(160 + 4, 50 + 6 - 2, TILE_AIR)
        is_valid, msg, _, _ = self.world.check_house_validity(cx, cy)
        self.assertFalse(is_valid)
        self.assertIn("comfort", msg.lower())

    def test_05_invalid_house_blight_contamination(self):
        """A house near Blight tiles cannot be settled."""
        cx, cy = self._build_test_house(180, 50, width=8, height=6)
        # Infest floor with Blightstone
        self.world.set_tile(180 + 3, 50 + 6 - 1, TILE_BLIGHTSTONE)
        is_valid, msg, _, _ = self.world.check_house_validity(cx, cy)
        self.assertFalse(is_valid)
        self.assertIn("blight", msg.lower())

    def test_06_guide_spawning_and_advice(self):
        """Guide NPC spawns and provides informative advice."""
        self.world.town_npcs.clear()
        self.world.check_and_spawn_town_npcs(self.player, self.inventory, self.asset_factory, self.sound_manager)
        
        guide = next((npc for npc in self.world.town_npcs if npc.npc_type == "guide"), None)
        self.assertIsNotNone(guide)
        self.assertEqual(guide.name, "Pip")
        advice = guide.get_advice(self.player, self.world, self.combat)
        self.assertTrue(len(advice) > 10)

    def test_07_merchant_spawning_and_trading(self):
        """Merchant arrives when player possesses coins and shelter, offering goods for copper coins."""
        # Guide already settled elsewhere so the newly constructed house is claimed by Merchant
        self.world.town_npcs = [
            GuideNPC("Pip", "guide", 10.0, 10.0, self.asset_factory, self.sound_manager, home_tile=(1, 1))
        ]
        # Build shelter near player
        ptx = int(self.player.center_x // SCALED_TILE)
        pty = int(self.player.center_y // SCALED_TILE)
        self._build_test_house(ptx + 3, pty - 3, width=8, height=6)

        # Give player copper coins
        self.inventory.add_item("copper_coin", 50)
        self.world.check_and_spawn_town_npcs(self.player, self.inventory, self.asset_factory, self.sound_manager)

        merchant = next((npc for npc in self.world.town_npcs if npc.npc_type == "merchant"), None)
        self.assertIsNotNone(merchant)
        self.assertEqual(merchant.name, "Barnaby")

        # Test trading: Buy torches from Merchant
        torch_item = next(item for item in merchant.shop_catalog if item["item_id"] == "torch")
        price = torch_item["price"]
        count = torch_item["count"]
        initial_coins = self.inventory.count_item("copper_coin")
        initial_torches = self.inventory.count_item("torch")
        
        dialogue = NPCDialogueWindow(self.asset_factory, self.sound_manager)
        dialogue.open(merchant, self.player, self.world, self.combat)
        dialogue.current_view = "shop"
        
        # Click buy button for torches (index 0)
        bx = dialogue.x + 20
        by = dialogue.y + 70
        buy_btn_x = bx + 180 + 10
        buy_btn_y = by + 4 + 10
        handled = dialogue.handle_click(buy_btn_x, buy_btn_y, self.player, self.inventory, self.world, self.combat)
        
        self.assertTrue(handled)
        self.assertEqual(self.inventory.count_item("copper_coin"), initial_coins - price)
        self.assertEqual(self.inventory.count_item("torch"), initial_torches + count)

    def test_08_nurse_healing_service(self):
        """Nurse calculates fee based on missing health and restores full HP/MP."""
        nurse = NurseNPC("Florencia", "nurse", 200, 200, self.asset_factory, self.sound_manager)
        self.player.stats.base_max_hp = 100
        self.player.stats.hp = 60
        self.player.health = 60
        
        # Cost should be (100 - 60) // 4 = 10 copper
        cost = nurse.calculate_heal_cost(self.player)
        self.assertEqual(cost, 10)

        # Without coins
        self.inventory.slots = [None] * len(self.inventory.slots)
        success, msg = nurse.heal_player(self.player, self.inventory)
        self.assertFalse(success)
        self.assertIn("Copper Coins", msg)

        # With coins
        self.inventory.add_item("copper_coin", 20)
        success, msg = nurse.heal_player(self.player, self.inventory)
        self.assertTrue(success)
        self.assertEqual(self.player.health, 100)
        self.assertEqual(self.inventory.count_item("copper_coin"), 10)

    def test_09_blacksmith_weapon_honing(self):
        """Blacksmith tempers player weapon to grant permanent +15% ATK and +10% Speed buff."""
        blacksmith = BlacksmithNPC("Russet", "blacksmith", 200, 200, self.asset_factory, self.sound_manager)
        
        # Give player a copper shortsword and coins
        self.inventory.slots[0] = ItemStack("copper_shortsword", 1)
        self.inventory.selected_slot = 0
        self.inventory.add_item("copper_coin", 50)

        orig_atk = self.inventory.slots[0].data.get("atk", 8)
        success, msg = blacksmith.hone_weapon(self.player, self.inventory)
        self.assertTrue(success)
        self.assertIn("Honed", self.inventory.slots[0].data["name"])
        self.assertTrue(self.inventory.slots[0].data["_is_honed"])
        self.assertGreater(self.inventory.slots[0].data["atk"], orig_atk)
        self.assertEqual(self.inventory.count_item("copper_coin"), 15) # 50 - 35 = 15

    def test_10_town_npc_save_and_load_persistence(self):
        """Town NPCs serialize to world.json and restore accurately on world reload."""
        world_name = "Test_Town_NPC_World"
        delete_world(world_name)

        class MockGame:
            pass

        game = MockGame()
        game.world = self.world
        game.player = self.player
        game.inventory = self.inventory
        game.combat = self.combat
        game.block_deltas = {}
        game.wall_deltas = {}
        game.active_world_name = world_name
        game.world_type = "infinite"
        game.difficulty = "normal"
        game.game_mode = "adventure"
        game.asset_factory = self.asset_factory
        game.sound_manager = self.sound_manager
        game.camera = type("MockCam", (), {"set_target": lambda *a, **k: None})()

        # Add NPCs
        self.world.town_npcs = [
            GuideNPC("Pip", "guide", 150.0, 220.0, self.asset_factory, self.sound_manager, home_tile=(10, 20)),
            MerchantNPC("Barnaby", "merchant", 250.0, 220.0, self.asset_factory, self.sound_manager, home_tile=(18, 20)),
        ]

        # Save
        save_world(world_name, game)

        # Clear and reload
        game.world.town_npcs.clear()
        self.assertEqual(len(game.world.town_npcs), 0)

        loaded = load_world(world_name, game)
        self.assertTrue(loaded)
        self.assertEqual(len(game.world.town_npcs), 2)
        
        types = [npc.npc_type for npc in game.world.town_npcs]
        self.assertIn("guide", types)
        self.assertIn("merchant", types)

        # Cleanup
        delete_world(world_name)

    def test_11_town_mechanics_disabled_in_potaria(self):
        """Verifies that town checks and NPC interactions are completely disabled in Potaria."""
        # 1. World default has town housing disabled
        self.assertFalse(self.world.town_housing_enabled)

        # 2. Add an NPC manually to world.town_npcs
        guide = GuideNPC("Pip", "guide", self.player.center_x, self.player.center_y, self.asset_factory, self.sound_manager)
        self.world.town_npcs = [guide]

        # 3. get_npc_at returns None because town is disabled
        self.assertIsNone(self.world.get_npc_at(self.player.center_x, self.player.center_y))

        # 4. update_town_npcs does not advance housing check or spawn new NPCs
        self.world.housing_check_timer = 3.4
        self.world.update_town_npcs(1.0, self.player, self.inventory, self.asset_factory, self.sound_manager, self.combat)
        # Timer should not have reset to 0 or spawned additional NPCs because check is disabled
        self.assertEqual(len(self.world.town_npcs), 1)

        # 5. When explicitly enabled (e.g. in test suites), get_npc_at works
        self.world.town_housing_enabled = True
        self.assertIsNotNone(self.world.get_npc_at(self.player.center_x, self.player.center_y))
        self.world.town_housing_enabled = False


if __name__ == "__main__":
    unittest.main()
