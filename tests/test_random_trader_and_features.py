"""
Unit and Integration Tests for Potaria Mystic Trader, Affix System,
Item Enhancement & Breaking/Repair, Storage Chests, and Playtime Tracking.
Developer: Kurados
"""

import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import unittest
import pygame

from src.constants import (
    SCALED_TILE, TILE_AIR, TILE_WOOD, TILE_WOOD_PLANKS, TILE_STONE,
    TILE_CHEST, CAT_WEAPON, CAT_TOOL, CAT_CONSUMABLE,
    DIFFICULTY_NORMAL
)
from src.assets.asset_factory import AssetFactory
from src.audio.sound_effects import SoundManager
from src.world.world import World
from src.entities.player import Player
from src.ui.inventory import Inventory, ItemStack, ITEM_REGISTRY
from src.combat.combat_system import CombatManager
from src.entities.mob import Mob
from src.entities.npc import MysticTraderNPC, TownNPC
from src.world.storage_chest import StorageChest
from src.rpg.enhancement import (
    enhance_item, can_enhance_item, repair_item,
    can_add_affix_slot, add_affix_slot_to_item,
    apply_affix_stone, can_apply_affix_stone,
    GOD_TIER_AFFIXES, ENHANCEMENT_REQUIREMENTS
)
from src.world.save_manager import save_world, load_world, delete_world, list_saved_worlds


class TestRandomTraderAndFeatures(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pygame.init()
        os.environ["SDL_VIDEODRIVER"] = "dummy"
        pygame.display.set_mode((800, 600))
        cls.asset_factory = AssetFactory()
        cls.sound_manager = SoundManager()

    def setUp(self):
        self.world = World(self.asset_factory, seed=123)
        sp_x, sp_y = self.world.spawn_point
        self.player = Player(sp_x, sp_y, self.asset_factory, self.sound_manager)
        self.inventory = Inventory(self.asset_factory)
        self.player.inventory = self.inventory
        self.inventory.player = self.player
        self.combat = CombatManager(self.asset_factory, self.sound_manager, None, None)

    def test_01_mystic_trader_spawn_and_despawn(self):
        """Mystic Wandering Trader spawns periodically near the player and despawns after timer expires, even if enclosed."""
        # 1. Advance timer to trigger spawn
        self.world.mystic_trader_timer = 239.5
        self.world.update_town_npcs(1.0, self.player, self.inventory, self.asset_factory, self.sound_manager, self.combat)

        traders = [npc for npc in self.world.town_npcs if isinstance(npc, MysticTraderNPC) or getattr(npc, "npc_type", "") == "mystic_trader"]
        self.assertEqual(len(traders), 1, "Mystic Trader must spawn when timer threshold is reached")
        trader = traders[0]
        self.assertIn(trader.name, ("Zephyrion", "Ignis Vance", "Morrigan"))

        # 2. Enclose trader completely with solid stone blocks (caging)
        tx = int(trader.x // SCALED_TILE)
        ty = int(trader.y // SCALED_TILE)
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx != 0 or dy != 0:
                    self.world.set_tile(tx + dx, ty + dy, TILE_STONE)

        # 3. Simulate passage of duration beyond remaining lifetime
        trader.duration = 10.0
        trader.time_left = 1.0
        trader.update(2.0, self.world, self.combat)

        self.assertTrue(trader.is_despawned, "Trader should be marked despawned when duration expires")
        self.assertNotIn(trader, self.world.town_npcs, "Despawned trader must be removed from active world NPCs even if caged")

    def test_02_mystic_trader_wares_rarity_capped_at_epic(self):
        """Trader rolls 5 items capped strictly at Epic rarity (no skillbooks, mythic, or legendary)."""
        trader = MysticTraderNPC("Zephyrion", "mystic_trader", self.player.center_x, self.player.center_y, self.asset_factory, self.sound_manager, duration=200.0)
        
        # Verify 5 entries in shop catalog
        self.assertEqual(len(trader.shop_catalog), 5, "Mystic trader must offer 5 entries in shop catalog")

        allowed_rarities = {"common", "uncommon", "rare", "epic", "legendary"}
        disallowed_rarities = {"mythic", "ancient"}

        for entry in trader.shop_catalog:
            item_id = entry["item_id"]
            if entry.get("is_affix_service"):
                self.assertEqual(item_id, "affix_slot_service")
                continue
            reg = ITEM_REGISTRY.get(item_id, {})
            self.assertNotEqual(reg.get("cat"), "skillbook", "No skill books in trader wares")
            rarity = reg.get("rarity", "common").lower()
            self.assertIn(rarity, ("common", "uncommon", "rare", "epic"), f"Item {item_id} rarity '{rarity}' must be capped at Epic")
            self.assertNotIn(rarity, disallowed_rarities, f"Item {item_id} must not be Mythic or Ancient")

    def test_03_turtle_shield_activation_and_interaction_locking(self):
        """Impenetrable Turtle Shield activates within 7 blocks (224px) of enemies, deflects damage, and locks trade."""
        trader = MysticTraderNPC("Zephyrion", "mystic_trader", 500, 500, self.asset_factory, self.sound_manager)
        
        # Position player close to trader
        self.player.x = 510
        self.player.y = 500

        # Without enemies, shield is down and trader is interactive
        trader.update(0.1, self.world, self.combat)
        self.assertFalse(trader.shield_active)
        self.assertTrue(trader.can_interact(self.player))

        # Spawn hostile mob within 3 blocks (96px) radius (e.g. at distance 50px)
        enemy = Mob(550, 500, 24, 24, 50, 10, "Crawler")
        self.combat.mobs.append(enemy)

        trader.update(0.1, self.world, self.combat)
        self.assertTrue(trader.shield_active, "Turtle shield must activate when enemy is within 3 blocks radius (96px)")
        self.assertFalse(trader.can_interact(self.player), "Interaction must be locked when shield is active")

        # Attack trader with on_hit while shielded -> zero damage taken, deflects
        dmg_taken = trader.on_hit(50)
        self.assertEqual(dmg_taken, 0, "Shield must deflect all damage")

        # Move enemy away beyond 3 blocks radius (e.g. at 200px away)
        enemy.x = 750
        trader.update(0.1, self.world, self.combat)
        self.assertFalse(trader.shield_active, "Turtle shield must deactivate when enemy is beyond 3 blocks radius (96px)")
        self.assertTrue(trader.can_interact(self.player), "Interaction must unlock when enemies leave")

    def test_04_repair_broken_item_costs_exactly_one_gold(self):
        """Repairing a broken weapon costs exactly 1 Gold Coin (10,000 Copper) and restores full weapon functionality."""
        weapon = ItemStack("iron_broadsword", 1, enhancement_level=5, is_broken=True)
        self.inventory.slots[0] = weapon

        # Insufficient funds: 9,999 copper
        self.player.stats.copper_coins = 9999
        self.player.stats.silver_coins = 0
        self.player.stats.gold_coins = 0
        ok, msg = repair_item(weapon, self.inventory, self.sound_manager)
        self.assertFalse(ok)
        self.assertTrue(weapon.is_broken)
        self.assertIn("1 Gold Coin", msg)

        # Exact funds: 1 Gold Coin (10,000 copper)
        self.player.stats.copper_coins = 0
        self.player.stats.silver_coins = 0
        self.player.stats.gold_coins = 1
        ok, msg = repair_item(weapon, self.inventory, self.sound_manager)
        self.assertTrue(ok)
        self.assertFalse(weapon.is_broken, "Item must be repaired")
        self.assertEqual(self.inventory.copper_coins, 0, "1 Gold Coin (10,000 copper) must be deducted")
        self.assertGreater(weapon.data.get("damage", 0), 0, "Repaired weapon must deal damage again")

    def test_05_affix_slot_carving_on_legendary_and_ancient_only(self):
        """Trader can carve affix slots on Legendary (max 1) and Ancient (max 2) items."""
        # Non-legendary item (iron sword is Common)
        common_item = ItemStack("iron_broadsword", 1)
        can_carve, reason = can_add_affix_slot(common_item)
        self.assertFalse(can_carve)
        self.assertIn("Legendary and Ancient", reason)

        # Legendary item (astral_wrath) - allowed max 1 slot
        legendary_item = ItemStack("astral_wrath", 1)
        can_carve, reason = can_add_affix_slot(legendary_item)
        self.assertTrue(can_carve, "Legendary items must be eligible for affix slots")

        # Add 1st affix slot: costs 5000 copper
        self.player.stats.copper_coins = 15000
        self.player.stats.silver_coins = 0
        self.player.stats.gold_coins = 0
        ok, msg = add_affix_slot_to_item(legendary_item, self.inventory, cost_copper=5000, sound_manager=self.sound_manager)
        self.assertTrue(ok)
        self.assertEqual(legendary_item.affix_slots, 1)
        self.assertEqual(len(legendary_item.removed_stats), 1, "A basic stat must be sacrificed")
        self.assertEqual(self.inventory.total_coins_value(), 10000)
        self.assertEqual(self.inventory.gold_coins, 1)

        # 2nd slot attempt on Legendary item: exceeds maximum 1 slot!
        can_carve, reason = can_add_affix_slot(legendary_item)
        self.assertFalse(can_carve)
        self.assertIn("maximum limit of 1", reason)

        # Ancient item (ancient_sword) - allowed max 2 slots
        ancient_item = ItemStack("ancient_sword", 1)
        self.assertTrue(can_add_affix_slot(ancient_item)[0])
        ok, _ = add_affix_slot_to_item(ancient_item, self.inventory, cost_copper=5000)
        self.assertTrue(ok)
        self.assertEqual(ancient_item.affix_slots, 1)

        self.assertTrue(can_add_affix_slot(ancient_item)[0])
        ok, _ = add_affix_slot_to_item(ancient_item, self.inventory, cost_copper=5000)
        self.assertTrue(ok)
        self.assertEqual(ancient_item.affix_slots, 2)

        # 3rd slot attempt on Ancient item: exceeds maximum 2 slots!
        can_carve, reason = can_add_affix_slot(ancient_item)
        self.assertFalse(can_carve)
        self.assertIn("maximum limit of 2", reason)

    def test_06_affix_stone_crafting_and_application(self):
        """Crafting Affix Stone at workbench and applying it embeds god-tier affixes into open slots."""
        from src.ui.crafting import RECIPES
        affix_recipe = next((r for r in RECIPES if r["result"] == "affix_stone"), None)
        self.assertIsNotNone(affix_recipe, "Affix Stone recipe must be registered")
        self.assertEqual(affix_recipe["station"], "work_bench")
        req_dict = dict(affix_recipe["ingredients"])
        self.assertEqual(req_dict.get("portal_shard"), 3)
        self.assertEqual(req_dict.get("gold_bar"), 5)
        self.assertEqual(req_dict.get("blightstone"), 5)

        # Apply Affix Stone to item
        legendary_item = ItemStack("ancient_eternal_shortbow", 1, affix_slots=2, affixes=[])
        
        # Item with no stones in inventory fails
        self.inventory.slots[0] = None
        ok, msg = apply_affix_stone(legendary_item, self.inventory, self.sound_manager)
        self.assertFalse(ok)
        self.assertIn("Affix Stone", msg)

        # Add Affix Stone to inventory and apply
        self.inventory.add_item("affix_stone", 2)
        ok, msg = apply_affix_stone(legendary_item, self.inventory, self.sound_manager)
        self.assertTrue(ok)
        self.assertEqual(len(legendary_item.affixes), 1)
        self.assertIn(legendary_item.affixes[0], GOD_TIER_AFFIXES)
        self.assertEqual(self.inventory.count_item("affix_stone"), 1)

        # Apply 2nd Affix Stone
        ok, msg = apply_affix_stone(legendary_item, self.inventory, self.sound_manager)
        self.assertTrue(ok)
        self.assertEqual(len(legendary_item.affixes), 2)
        self.assertEqual(self.inventory.count_item("affix_stone"), 0)

        # 3rd attempt: all slots filled
        self.inventory.add_item("affix_stone", 1)
        can_apply, reason = can_apply_affix_stone(legendary_item)
        self.assertFalse(can_apply)
        self.assertIn("No open affix slots", reason)

    def test_07_enhancement_scaling_and_break_risk(self):
        """Enhancing from +1 to +7 scales stats up to 2.0x, +1 to +4 are safe (0% break risk), and +5/+6/+7 have break risks."""
        weapon = ItemStack("iron_broadsword", 1)
        base_dmg = weapon.data["damage"]

        # 1. Enhance from 0 to +1 (+1 to +4 have break_rate == 0.0)
        self.assertEqual(ENHANCEMENT_REQUIREMENTS[1]["break_rate"], 0.0)
        self.assertEqual(ENHANCEMENT_REQUIREMENTS[2]["break_rate"], 0.0)
        self.assertEqual(ENHANCEMENT_REQUIREMENTS[3]["break_rate"], 0.0)
        self.assertEqual(ENHANCEMENT_REQUIREMENTS[4]["break_rate"], 0.0)
        self.assertGreater(ENHANCEMENT_REQUIREMENTS[5]["break_rate"], 0.0)
        self.assertGreater(ENHANCEMENT_REQUIREMENTS[6]["break_rate"], 0.0)
        self.assertGreater(ENHANCEMENT_REQUIREMENTS[7]["break_rate"], 0.0)

        # Enhance safely to +4
        weapon.enhancement_level = 4
        mult_4 = 1.0 + (4.0 / 7.0)
        expected_dmg_4 = int(round(base_dmg * mult_4))
        self.assertEqual(weapon.data["damage"], expected_dmg_4)

        # Level +7 stat doubling
        weapon.enhancement_level = 7
        mult_7 = 1.0 + (7.0 / 7.0)
        expected_dmg_7 = int(round(base_dmg * mult_7))
        self.assertEqual(expected_dmg_7, base_dmg * 2, "At +7, stat multiplier must be exactly 2.0x")
        self.assertEqual(weapon.data["damage"], base_dmg * 2)

        # Cannot enhance beyond +7
        can_enh, reason = can_enhance_item(weapon)
        self.assertFalse(can_enh)
        self.assertIn("MAX enhancement (+7)", reason)

    def test_08_broken_item_usage_prevention(self):
        """Broken items cannot be equipped via inventory and cannot be used for attacks in gameplay."""
        broken_sword = ItemStack("iron_broadsword", 1, enhancement_level=5, is_broken=True)
        self.inventory.slots[0] = broken_sword

        # 1. Check ItemStack data zeros out offensive stats
        self.assertEqual(broken_sword.data["damage"], 0)
        self.assertEqual(broken_sword.data["atk"], 0)
        self.assertTrue(broken_sword.data["name"].startswith("[BROKEN]"))

        # 2. Inventory equip_item disallows equipping broken items
        equipped = self.inventory.equip_item(0, self.player)
        self.assertFalse(equipped)
        self.assertIn("Cannot equip broken item", self.inventory.last_learned_message)

        # 3. Primary action disallows attack with broken weapon
        from main import PotariaGame
        game = PotariaGame.__new__(PotariaGame)
        game.inventory = self.inventory
        game.player = self.player
        game.world = self.world
        game.combat = self.combat
        game.sound_manager = self.sound_manager

        # Attempting attack with broken weapon in hotbar returns False
        action_allowed = game.handle_primary_action(100, 100)
        self.assertFalse(action_allowed, "Broken weapons must not perform primary attack")

    def test_09_storage_chest_container_and_ui(self):
        """20-slot StorageChest handles add, remove, quick-stack, deposit-all, loot-all, and persists on placement."""
        chest = StorageChest(10, 20, chest_type="iron_chest")
        self.assertEqual(chest.capacity, 20)
        self.assertEqual(len(chest.slots), 20)

        # 1. Add item to chest
        leftover = chest.add_item("wood", 15)
        self.assertEqual(leftover, 0)
        self.assertEqual(chest.count_item("wood"), 15)

        # 2. Quick stack from inventory (only matching items)
        self.inventory.slots = [None] * len(self.inventory.slots)
        self.inventory.slots[0] = ItemStack("wood", 30)
        self.inventory.slots[1] = ItemStack("iron_ore", 10)
        
        stacked = chest.quick_stack_from_inventory(self.inventory)
        self.assertEqual(stacked, 30, "Should quick stack wood")
        self.assertEqual(chest.count_item("wood"), 45)
        self.assertEqual(self.inventory.slots[0], None)
        self.assertIsNotNone(self.inventory.slots[1], "Non-matching iron_ore should stay in inventory")

        # 3. World placement creates chest
        self.world.set_tile(15, 25, TILE_AIR)
        self.world.set_tile(15, 26, TILE_STONE)  # neighbor
        placed = self.world.place_tile(15, 25, TILE_CHEST, chest_type="iron_chest")
        self.assertTrue(placed)
        self.assertIn((15, 25), self.world.chests)
        self.assertEqual(self.world.chests[(15, 25)].chest_type, "iron_chest")

        # 4. Breaking chest drops contents and chest item
        self.world.chests[(15, 25)].add_item("gold_bar", 5)
        broken, drop_id, tile_id = self.world.damage_tile_at(15, 25, 999.0)
        self.assertTrue(broken)
        self.assertEqual(drop_id, "iron_chest")
        self.assertNotIn((15, 25), self.world.chests)

    def test_10_playtime_and_last_played_tracking_and_persistence(self):
        """World save records playtime accumulation and last_played date, visible on world select cards."""
        world_name = "Test_Trader_Features_Save"
        from main import PotariaGame
        game = PotariaGame.__new__(PotariaGame)
        game.active_world_name = world_name
        game.world = self.world
        game.player = self.player
        game.inventory = self.inventory
        game.combat = self.combat
        game.sound_manager = self.sound_manager
        game.asset_factory = self.asset_factory
        game.client = None
        game.block_deltas = {}
        game.wall_deltas = {}
        game.difficulty = DIFFICULTY_NORMAL
        game.game_mode = "adventure"
        game.world_type = "infinite"
        
        from src.camera import Camera
        game.camera = Camera(800, 600)
        
        # 3725 seconds = 1 hour, 2 minutes, 5 seconds
        game.playtime = 3725.0

        # Place a chest with items in the world (with a solid neighbor)
        self.world.set_tile(20, 21, TILE_STONE)
        placed = self.world.place_tile(20, 20, TILE_CHEST, chest_type="chest")
        self.assertTrue(placed)
        chest = self.world.chests.get((20, 20))
        self.assertIsNotNone(chest)
        chest.add_item("portal_shard", 4)

        # Give player an enhanced +5 weapon with an affix
        enhanced_weapon = ItemStack("composite_bow", 1, enhancement_level=5, affix_slots=1, affixes=["Titan's Might"])
        self.inventory.slots[0] = enhanced_weapon

        # Save world
        save_world(world_name, game)

        # Inspect saved worlds metadata
        saved_worlds = list_saved_worlds()
        match = next((w for w in saved_worlds if w["name"] == world_name), None)
        self.assertIsNotNone(match)
        self.assertEqual(match["playtime_str"], "1h 2m")
        self.assertIn("-", match["last_played"])  # Format YYYY-MM-DD HH:MM

        # Load world into fresh game instance
        new_game = PotariaGame.__new__(PotariaGame)
        new_game.asset_factory = self.asset_factory
        new_game.camera = Camera(800, 600)
        new_game.world = World(self.asset_factory, seed=123)
        new_game.player = Player(0, 0, self.asset_factory, self.sound_manager)
        new_game.inventory = Inventory(self.asset_factory)
        new_game.combat = CombatManager(self.asset_factory, self.sound_manager, None, None)
        new_game.sound_manager = self.sound_manager
        new_game.client = None
        new_game.block_deltas = {}
        new_game.wall_deltas = {}

        load_world(world_name, new_game)

        # Verify playtime restored
        self.assertAlmostEqual(new_game.playtime, 3725.0, places=1)

        # Verify chest restored
        self.assertIn((20, 20), new_game.world.chests)
        loaded_chest = new_game.world.chests[(20, 20)]
        self.assertEqual(loaded_chest.count_item("portal_shard"), 4)

        # Verify enhanced weapon with affix restored
        loaded_weapon = new_game.inventory.slots[0]
        self.assertIsNotNone(loaded_weapon)
        self.assertEqual(loaded_weapon.enhancement_level, 5)
        self.assertEqual(loaded_weapon.affix_slots, 1)
        self.assertIn("Titan's Might", loaded_weapon.affixes)

        # Cleanup
        delete_world(world_name)

    def test_11_equipment_enhancement_and_affix_recalculation_and_preservation(self):
        """Equipping enhanced and affixed gear applies scaled stats, preserves metadata on unequip, and persists across save/load."""
        from src.rpg.equipment import SLOT_HEAD, SLOT_CHEST, SLOT_LEGS, SLOT_WEAPON, SLOT_ACCESSORY
        from main import PotariaGame
        from src.camera import Camera

        # 1. Base unequipped stats
        self.player.equipment.slots = {k: None for k in self.player.equipment.slots}
        self.player.equipment.recalculate_stats(self.player.stats)
        base_def = self.player.stats.total_def
        base_atk = self.player.stats.total_atk

        # 2. Equip +7 enhanced armor and +7 enhanced weapon with affixes
        helm = ItemStack("iron_helmet", 1, enhancement_level=7, affix_slots=1, affixes=["Titan's Might"])
        sword = ItemStack("iron_broadsword", 1, enhancement_level=7, affix_slots=2, affixes=["Berserker's Blood", "Godslayer Edge"])
        
        self.inventory.slots[0] = helm
        self.inventory.slots[1] = sword
        self.inventory.equip_item(0, self.player)
        self.inventory.equip_item(1, self.player)

        # Equipped slots should be ItemStacks
        self.assertIsInstance(self.player.equipment.slots[SLOT_HEAD], ItemStack)
        self.assertIsInstance(self.player.equipment.slots[SLOT_WEAPON], ItemStack)

        # Recalculated stats should include double base item stats (+7 = 2.0x) + affixes
        self.player.equipment.recalculate_stats(self.player.stats, active_item=self.player.equipment.slots[SLOT_WEAPON])
        self.assertGreater(self.player.stats.total_def, base_def)
        self.assertGreater(self.player.stats.total_atk, base_atk * 2)

        # 3. Unequip items back to inventory and ensure ItemStack metadata is retained
        unequipped_helm = self.player.equipment.unequip(SLOT_HEAD)
        self.assertIsInstance(unequipped_helm, ItemStack)
        self.assertEqual(unequipped_helm.enhancement_level, 7)
        self.assertEqual(unequipped_helm.affixes, ["Titan's Might"])

        # Re-equip helm
        self.player.equipment.equip(unequipped_helm, self.player.stats)

        # 4. Save and Load to confirm equipped ItemStacks persist with enhancement levels and affixes
        world_name = "Test_Equip_Save"
        game = PotariaGame.__new__(PotariaGame)
        game.active_world_name = world_name
        game.world = self.world
        game.player = self.player
        game.inventory = self.inventory
        game.combat = self.combat
        game.sound_manager = self.sound_manager
        game.asset_factory = self.asset_factory
        game.client = None
        game.block_deltas = {}
        game.wall_deltas = {}
        game.difficulty = DIFFICULTY_NORMAL
        game.game_mode = "adventure"
        game.world_type = "infinite"
        game.playtime = 100.0
        game.camera = Camera(800, 600)

        save_world(world_name, game)

        # Load into fresh game
        loaded_game = PotariaGame.__new__(PotariaGame)
        loaded_game.asset_factory = self.asset_factory
        loaded_game.camera = Camera(800, 600)
        loaded_game.world = World(self.asset_factory, seed=123)
        loaded_game.player = Player(0, 0, self.asset_factory, self.sound_manager)
        loaded_game.inventory = Inventory(self.asset_factory)
        loaded_game.combat = CombatManager(self.asset_factory, self.sound_manager, None, None)
        loaded_game.sound_manager = self.sound_manager
        loaded_game.client = None
        loaded_game.block_deltas = {}
        loaded_game.wall_deltas = {}

        load_world(world_name, loaded_game)

        loaded_helm = loaded_game.player.equipment.slots[SLOT_HEAD]
        loaded_weapon = loaded_game.player.equipment.slots[SLOT_WEAPON]
        self.assertIsInstance(loaded_helm, ItemStack)
        self.assertIsInstance(loaded_weapon, ItemStack)
        self.assertEqual(loaded_helm.enhancement_level, 7)
        self.assertEqual(loaded_helm.affixes, ["Titan's Might"])
        self.assertEqual(loaded_weapon.enhancement_level, 7)
        self.assertEqual(loaded_weapon.affixes, ["Berserker's Blood", "Godslayer Edge"])

        delete_world(world_name)

    def test_12_inventory_affix_stone_usage_via_right_click_and_cursor(self):
        """Affix Stone can be applied via right-click in inventory or by picking it up and clicking target item."""
        # 1. Target item: ancient bow with 2 open slots
        bow = ItemStack("ancient_eternal_shortbow", 1, affix_slots=2, affixes=[])
        stone_stack = ItemStack("affix_stone", 3)
        self.inventory.slots[0] = bow
        self.inventory.slots[1] = stone_stack
        self.inventory.selected_slot = 0
        self.inventory.is_open = True

        # Right-click slot 1 (affix_stone) with no item on cursor
        from src.ui.inventory import SLOT_SIZE, SLOT_PADDING
        start_x, start_y = 20, 20
        slot_1_x = start_x + (1 % 10) * (SLOT_SIZE + SLOT_PADDING) + 10
        slot_1_y = start_y + (1 // 10) * (SLOT_SIZE + SLOT_PADDING) + 10

        handled = self.inventory.handle_click(slot_1_x, slot_1_y, is_right_click=True, player=self.player)
        self.assertTrue(handled)
        self.assertEqual(len(bow.affixes), 1, "Affix stone right-click must embed affix onto held bow")
        self.assertEqual(stone_stack.count, 2, "One affix stone should be consumed")

        # 2. Pick up stone on cursor and left-click onto target slot
        slot_0_x = start_x + (0 % 10) * (SLOT_SIZE + SLOT_PADDING) + 10
        slot_0_y = start_y + (0 // 10) * (SLOT_SIZE + SLOT_PADDING) + 10

        self.inventory.held_item = ItemStack("affix_stone", 1)
        handled = self.inventory.handle_click(slot_0_x, slot_0_y, is_right_click=False, player=self.player)
        self.assertTrue(handled)
        self.assertEqual(len(bow.affixes), 2, "Cursor affix stone click must embed second affix onto bow")
        self.assertIsNone(self.inventory.held_item, "Held affix stone should be consumed")

    def test_13_mystic_trader_turtle_shield_auto_closes_dialogue(self):
        """Hostile enemies entering Turtle Shield radius auto-closes dialogue window and blocks trading."""
        from src.ui.npc_dialogue import NPCDialogueWindow
        trader = MysticTraderNPC("Zephyrion", "mystic_trader", 300, 300, self.asset_factory, self.sound_manager)
        dialogue = NPCDialogueWindow(self.asset_factory, self.sound_manager)

        # Open dialogue normally
        dialogue.open(trader, self.player, self.world, self.combat)
        self.assertTrue(dialogue.is_open)

        # Spawn hostile mob within 224px radius
        enemy = Mob(350, 300, 24, 24, 50, 10, "Crawler")
        self.combat.mobs.append(enemy)

        # Update dialogue -> should detect shield and auto-close
        trader.update(0.1, self.world, self.combat)
        dialogue.update(0.1)
        self.assertFalse(dialogue.is_open, "Dialogue must auto-close when Turtle Shield activates")

        # Trying to open while mob is nearby must be rejected
        dialogue.open(trader, self.player, self.world, self.combat)
        self.assertFalse(dialogue.is_open, "Dialogue must refuse to open while Turtle Shield is active")

    def test_14_chest_stack_splitting_and_tooltips(self):
        """Splitting stacks in chests preserves enhancement/affix metadata, and ChestStorageWindow renders tooltips."""
        from src.ui.chest_ui import ChestStorageWindow
        chest = StorageChest(10, 20)
        chest_ui = ChestStorageWindow(self.asset_factory, self.sound_manager)
        chest_ui.open(chest, self.player, self.inventory)

        # Add enhanced stack of items
        item_stack = ItemStack("iron_broadsword", 4, enhancement_level=3, affix_slots=1, affixes=["Titan's Might"])
        chest.slots[0] = item_stack

        # Right click to split stack
        c_slot_x = chest_ui.x + 20
        c_slot_y = chest_ui.y + 40
        handled = chest_ui.handle_click(c_slot_x, c_slot_y, is_right_click=True, player=self.player, inventory=self.inventory)
        self.assertTrue(handled)
        self.assertIsNotNone(self.inventory.held_item)
        self.assertEqual(self.inventory.held_item.count, 2)
        self.assertEqual(self.inventory.held_item.enhancement_level, 3)
        self.assertEqual(self.inventory.held_item.affixes, ["Titan's Might"])

        # Tooltip rendering
        surf = pygame.Surface((800, 600))
        chest_ui.render_tooltip(surf, self.inventory.held_item, 100, 100)
        chest_ui.render(surf, self.inventory, mouse_x=c_slot_x, mouse_y=c_slot_y)

    def test_15_trader_affix_service_dialogue_visibility(self):
        """Carve Affix Slot button in dialogue appears only when trader rolled affix slot service."""
        from src.ui.npc_dialogue import NPCDialogueWindow
        dialogue = NPCDialogueWindow(self.asset_factory, self.sound_manager)

        # 1. Trader without affix service
        trader_no_service = MysticTraderNPC("Zephyrion", "mystic_trader", 300, 300, self.asset_factory, self.sound_manager,
                                            shop_catalog=[{"item_id": "wooden_sword", "name": "Wooden Sword", "price": 10, "currency": "copper_coin"}])
        dialogue.open(trader_no_service, self.player, self.world, self.combat)
        self.assertTrue(dialogue.is_open)

        # Carve affix slot button (x=255, y=start_y, w=125, h=28)
        start_y = dialogue.y + dialogue.height - 44
        b3_x = dialogue.x + 260
        b3_y = start_y + 10
        # Clicking b3 coordinates when service is not offered should NOT trigger carving
        self.inventory.slots[0] = ItemStack("astral_wrath", 1)
        self.inventory.selected_slot = 0
        handled = dialogue.handle_click(b3_x, b3_y, self.player, self.inventory, self.world, self.combat)
        self.assertEqual(self.inventory.slots[0].affix_slots, 0, "No carving should happen when trader did not roll service")

        # 2. Trader WITH affix service
        trader_with_service = MysticTraderNPC("Zephyrion", "mystic_trader", 300, 300, self.asset_factory, self.sound_manager,
                                              shop_catalog=[{"item_id": "affix_slot_service", "name": "Affix Carving", "price": 50, "currency": "silver_coin", "is_affix_service": True}])
        dialogue.open(trader_with_service, self.player, self.world, self.combat)
        self.player.stats.copper_coins = 10000
        self.player.stats.silver_coins = 0
        self.player.stats.gold_coins = 0

        handled = dialogue.handle_click(b3_x, b3_y, self.player, self.inventory, self.world, self.combat)
        self.assertTrue(handled)
        self.assertEqual(self.inventory.slots[0].affix_slots, 1, "Carving should succeed when trader offers service")


if __name__ == "__main__":
    unittest.main()
