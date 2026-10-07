"""
Potaria - Crafting Engine
Recipes for tools, food recipes (mashed potatoes, golden fries), potions,
swords, building blocks, furniture, and the mystical Dungeon Teleporter Rune.
Developer: Kurados
"""

import math
import pygame
from src.constants import (
    SCALED_TILE, TILE_WORK_BENCH, TILE_FURNACE,
    RARITY_COLORS, RARITY_COMMON
)
from src.ui.inventory import ITEM_REGISTRY

RECIPES = [
    # ----------------------------------------------------
    # Basic Crafting (By Hand / Anywhere)
    # ----------------------------------------------------
    {
        "result": "work_bench", "count": 1, "station": None,
        "ingredients": [("wood", 10)]
    },
    {
        "result": "wood_platform", "count": 2, "station": None,
        "ingredients": [("wood", 1)]
    },
    {
        "result": "torch", "count": 3, "station": None,
        "ingredients": [("wood", 1), ("spud_sap", 1)]
    },
    {
        "result": "wood_axe", "count": 1, "station": None,
        "ingredients": [("wood", 6)]
    },
    {
        "result": "wood_shovel", "count": 1, "station": None,
        "ingredients": [("wood", 4)]
    },
    {
        "result": "wooden_arrow", "count": 25, "station": None,
        "ingredients": [("wood", 1), ("stone_block", 1)]
    },
    
    # ----------------------------------------------------
    # Food Cooking & Smelting (Furnace)
    # ----------------------------------------------------
    {
        "result": "mashed_potato", "count": 1, "station": "furnace",
        "ingredients": [("raw_potato", 2), ("wood", 1)]
    },
    {
        "result": "golden_fry", "count": 1, "station": "furnace",
        "ingredients": [("raw_potato", 3), ("gold_bar", 1)]
    },
    {
        "result": "copper_bar", "count": 1, "station": "furnace",
        "ingredients": [("copper_ore", 3)]
    },
    {
        "result": "iron_bar", "count": 1, "station": "furnace",
        "ingredients": [("iron_ore", 3)]
    },
    {
        "result": "gold_bar", "count": 1, "station": "furnace",
        "ingredients": [("gold_ore", 3)]
    },
    {
        "result": "stone_brick", "count": 1, "station": "furnace",
        "ingredients": [("stone_block", 2)]
    },
    {
        "result": "glass_window", "count": 2, "station": "furnace",
        "ingredients": [("sand_block", 2)]
    },

    # ----------------------------------------------------
    # House Blocks & Homestead Furniture (Work Bench)
    # ----------------------------------------------------
    {
        "result": "roof_tiles", "count": 4, "station": "work_bench",
        "ingredients": [("stone_block", 2), ("dirt_block", 2)]
    },
    {
        "result": "wood_planks", "count": 4, "station": "work_bench",
        "ingredients": [("wood", 1)]
    },
    {
        "result": "wooden_door", "count": 1, "station": "work_bench",
        "ingredients": [("wood", 6)]
    },
    {
        "result": "wooden_table", "count": 1, "station": "work_bench",
        "ingredients": [("wood", 8)]
    },
    {
        "result": "wooden_chair", "count": 1, "station": "work_bench",
        "ingredients": [("wood", 4)]
    },
    {
        "result": "wooden_bed", "count": 1, "station": "work_bench",
        "ingredients": [("wood", 12), ("spud_sap", 4)]
    },
    {
        "result": "bookshelf", "count": 1, "station": "work_bench",
        "ingredients": [("wood", 10), ("bone", 2)]
    },
    {
        "result": "grandfather_clock", "count": 1, "station": "work_bench",
        "ingredients": [("wood", 10), ("iron_bar", 2), ("gold_bar", 1)]
    },
    {
        "result": "stone_fireplace", "count": 1, "station": "furnace",
        "ingredients": [("stone_block", 12), ("wood", 4), ("torch", 2)]
    },
    {
        "result": "candelabra", "count": 1, "station": "work_bench",
        "ingredients": [("copper_bar", 3), ("torch", 3)]
    },
    {
        "result": "chandelier", "count": 1, "station": "work_bench",
        "ingredients": [("gold_bar", 3), ("torch", 4), ("iron_bar", 1)]
    },
    {
        "result": "potted_plant", "count": 1, "station": "work_bench",
        "ingredients": [("stone_block", 2), ("dirt_block", 2), ("raw_potato", 1)]
    },
    {
        "result": "wooden_dresser", "count": 1, "station": "work_bench",
        "ingredients": [("wood", 10), ("copper_bar", 1)]
    },
    {
        "result": "wall_tapestry", "count": 1, "station": "work_bench",
        "ingredients": [("wood", 2), ("spud_sap", 4)]
    },
    {
        "result": "bathtub", "count": 1, "station": "work_bench",
        "ingredients": [("iron_bar", 4), ("wood", 2)]
    },
    {
        "result": "sink", "count": 1, "station": "work_bench",
        "ingredients": [("iron_bar", 2), ("wood", 4)]
    },
    {
        "result": "painting", "count": 1, "station": "work_bench",
        "ingredients": [("wood", 4), ("spud_sap", 2), ("gold_bar", 1)]
    },
    {
        "result": "wood_shelf", "count": 2, "station": "work_bench",
        "ingredients": [("wood", 2)]
    },
    {
        "result": "wood_wall", "count": 4, "station": "work_bench",
        "ingredients": [("wood", 1)]
    },
    {
        "result": "stone_brick_wall", "count": 4, "station": "work_bench",
        "ingredients": [("stone_brick", 1)]
    },

    # ----------------------------------------------------
    # Advanced Tools, Weapons & Gear (Work Bench)
    # ----------------------------------------------------
    {
        "result": "furnace", "count": 1, "station": "work_bench",
        "ingredients": [("stone_block", 20), ("wood", 4), ("torch", 3)]
    },
    {
        "result": "wood_bow", "count": 1, "station": "work_bench",
        "ingredients": [("wood", 10)]
    },
    {
        "result": "copper_broadsword", "count": 1, "station": "work_bench",
        "ingredients": [("copper_bar", 8), ("wood", 2)]
    },
    {
        "result": "gold_broadsword", "count": 1, "station": "work_bench",
        "ingredients": [("gold_bar", 8), ("wood", 2)]
    },
    {
        "result": "wood_pickaxe", "count": 1, "station": None,
        "ingredients": [("wood", 10)]
    },
    {
        "result": "iron_pickaxe", "count": 1, "station": "work_bench",
        "ingredients": [("iron_bar", 10), ("wood", 3)]
    },
    {
        "result": "gold_pickaxe", "count": 1, "station": "work_bench",
        "ingredients": [("gold_bar", 10), ("wood", 3)]
    },
    {
        "result": "iron_axe", "count": 1, "station": "work_bench",
        "ingredients": [("iron_bar", 8), ("wood", 3)]
    },
    {
        "result": "gold_axe", "count": 1, "station": "work_bench",
        "ingredients": [("gold_bar", 8), ("wood", 3)]
    },
    {
        "result": "celestial_axe", "count": 1, "station": "work_bench",
        "ingredients": [("celestial_essence", 1), ("gold_bar", 8), ("wood", 5)]
    },
    {
        "result": "celestial_pickaxe", "count": 1, "station": "work_bench",
        "ingredients": [("celestial_essence", 1), ("gold_bar", 10), ("wood", 5)]
    },
    {
        "result": "iron_shovel", "count": 1, "station": "work_bench",
        "ingredients": [("iron_bar", 4), ("wood", 2)]
    },
    {
        "result": "starch_blade", "count": 1, "station": "work_bench",
        "ingredients": [("gold_bar", 8), ("raw_potato", 4), ("spud_sap", 6)]
    },
    {
        "result": "cactus_sword", "count": 1, "station": "work_bench",
        "ingredients": [("cactus", 10)]
    },
    {
        "result": "cactus_helmet", "count": 1, "station": "work_bench",
        "ingredients": [("cactus", 8)]
    },
    {
        "result": "cactus_chestplate", "count": 1, "station": "work_bench",
        "ingredients": [("cactus", 12)]
    },
    {
        "result": "cactus_greaves", "count": 1, "station": "work_bench",
        "ingredients": [("cactus", 10)]
    },
    {
        "result": "bone_bow", "count": 1, "station": "work_bench",
        "ingredients": [("bone", 12), ("spud_sap", 4)]
    },
    {
        "result": "frostburn_arrow", "count": 25, "station": "work_bench",
        "ingredients": [("wooden_arrow", 25), ("frost_core", 1)]
    },
    {
        "result": "flame_arrow", "count": 25, "station": "work_bench",
        "ingredients": [("wooden_arrow", 25), ("torch", 1)]
    },
    {
        "result": "astral_arrow", "count": 25, "station": "work_bench",
        "ingredients": [("wooden_arrow", 25), ("fallen_star", 1)]
    },
    {
        "result": "chest", "count": 1, "station": "work_bench",
        "ingredients": [("wood", 8), ("iron_bar", 2)]
    },
    {
        "result": "greater_healing_potion", "count": 1, "station": "work_bench",
        "ingredients": [("healing_potion", 2), ("glowing_mushroom", 1)]
    },
    {
        "result": "speed_potion", "count": 1, "station": "work_bench",
        "ingredients": [("raw_potato", 1), ("spud_sap", 2)]
    },

    # ----------------------------------------------------
    # Dungeon Teleporter Rune & Keystone
    # ----------------------------------------------------
    {
        "result": "dungeon_rune", "count": 1, "station": "work_bench",
        "ingredients": [("gold_bar", 4), ("spud_sap", 5), ("stone_brick", 6)]
    },
    {
        "result": "desert_rune", "count": 1, "station": "work_bench",
        "ingredients": [("cactus", 6), ("sandstone_block", 8), ("gold_bar", 2)]
    },
    {
        "result": "cryo_rune", "count": 1, "station": "work_bench",
        "ingredients": [("frost_core", 2), ("ice_block", 10), ("iron_bar", 4)]
    },
    {
        "result": "necro_rune", "count": 1, "station": "work_bench",
        "ingredients": [("bone", 8), ("blightstone_block", 10), ("gold_bar", 2)]
    },
    {
        "result": "copper_axe", "count": 1, "station": "work_bench",
        "ingredients": [("copper_bar", 6), ("wood", 2)]
    },
    {
        "result": "copper_shortsword", "count": 1, "station": "work_bench",
        "ingredients": [("copper_bar", 5), ("wood", 2)]
    },
    {
        "result": "copper_pickaxe", "count": 1, "station": "work_bench",
        "ingredients": [("copper_bar", 8), ("wood", 3)]
    },
    {
        "result": "celestial_keystone", "count": 1, "station": "work_bench",
        "ingredients": [("portal_shard", 4), ("gold_bar", 5), ("stone_brick", 10)]
    },

    # ----------------------------------------------------
    # High-Tier Gear Recipes
    # ----------------------------------------------------
    {
        "result": "magma_greatsword", "count": 1, "station": "work_bench",
        "ingredients": [("magma_core", 1), ("gold_bar", 8)]
    },
    {
        "result": "magma_chestplate", "count": 1, "station": "work_bench",
        "ingredients": [("magma_core", 2), ("iron_bar", 10)]
    },
    {
        "result": "cryo_chestplate", "count": 1, "station": "work_bench",
        "ingredients": [("frost_core", 3), ("iron_bar", 10)]
    },
    {
        "result": "bone_scythe", "count": 1, "station": "work_bench",
        "ingredients": [("bone", 16), ("iron_bar", 6)]
    },
    {
        "result": "titans_ring", "count": 1, "station": "work_bench",
        "ingredients": [("celestial_essence", 1), ("gold_bar", 6)]
    },
]

class CraftingSystem:
    def __init__(self, asset_factory, sound_manager):
        self.asset_factory = asset_factory
        self.sound_manager = sound_manager
        self.available_recipes = []
        self.near_workbench = False
        self.near_furnace = False
        self.last_inventory = None
        self.last_crafted_item = None

    def check_nearby_stations(self, world, player):
        """Checks if Spud is within strict physical crafting range (within 2.5 tiles) of a placed Work Bench or Furnace."""
        ptx = int(player.center_x // SCALED_TILE)
        pty = int(player.center_y // SCALED_TILE)
        has_workbench = False
        has_furnace = False

        for dx in range(-4, 5):
            for dy in range(-4, 5):
                dist = math.hypot(dx, dy)
                t_id = world.get_tile(ptx + dx, pty + dy)
                if t_id == TILE_WORK_BENCH and dist <= 2.5:
                    has_workbench = True
                elif t_id == TILE_FURNACE and dist <= 2.5:
                    has_furnace = True

        self.near_workbench = has_workbench
        self.near_furnace = has_furnace
        return has_workbench, has_furnace

    def update_recipes(self, inventory, world, player):
        self.last_inventory = inventory
        has_wb, has_furn = self.check_nearby_stations(world, player)
        
        station_recipes = []
        for r in RECIPES:
            req_station = r["station"]
            if req_station == "work_bench" and not has_wb:
                continue
            if req_station == "furnace" and not has_furn:
                continue

            can_craft = True
            for item_id, count in r["ingredients"]:
                if inventory.count_item(item_id) < count:
                    can_craft = False
                    break
            
            recipe_entry = dict(r)
            recipe_entry["can_craft"] = can_craft
            station_recipes.append(recipe_entry)

        # Sort so craftable recipes appear first, followed by uncraftable station unlocks
        station_recipes.sort(key=lambda r: (not r["can_craft"]))
        self.available_recipes = station_recipes

    def craft(self, recipe, inventory):
        for item_id, count in recipe["ingredients"]:
            if inventory.count_item(item_id) < count:
                return False

        for item_id, count in recipe["ingredients"]:
            inventory.remove_item(item_id, count)

        inventory.add_item(recipe["result"], recipe["count"])
        self.sound_manager.play("craft")
        return True

    def handle_click(self, mouse_x, mouse_y, inventory):
        start_x = 20
        start_y = 258
        icon_size = 36
        padding = 6

        for i, recipe in enumerate(self.available_recipes):
            rx = start_x + (i % 6) * (icon_size + padding)
            ry = start_y + (i // 6) * (icon_size + padding)
            rect = pygame.Rect(rx, ry, icon_size, icon_size)

            if rect.collidepoint(mouse_x, mouse_y):
                if recipe.get("can_craft", True):
                    if self.craft(recipe, inventory):
                        self.last_crafted_item = recipe.get("result")
                else:
                    self.sound_manager.play("hit")
                return True
        return False

    def render(self, target_surf, mouse_x, mouse_y, font):
        start_x = 20
        header_y = 232
        start_y = 258
        icon_size = 36
        padding = 6

        # Crafting Header with Proximity Status Badges (Cleanly separated below inventory drop buttons)
        t_surf = font.render("Crafting Recipes:", True, (255, 230, 100))
        target_surf.blit(t_surf, (start_x, header_y))

        badge_x = start_x + t_surf.get_width() + 8
        if self.near_workbench:
            wb_surf = font.render("[Near Work Bench]", True, (80, 240, 120))
            target_surf.blit(wb_surf, (badge_x, header_y))
            badge_x += wb_surf.get_width() + 6
        if self.near_furnace:
            fn_surf = font.render("[Near Furnace]", True, (255, 170, 60))
            target_surf.blit(fn_surf, (badge_x, header_y))
            badge_x += fn_surf.get_width() + 6
        if not self.near_workbench and not self.near_furnace:
            h_surf = font.render("[By Hand]", True, (170, 185, 205))
            target_surf.blit(h_surf, (badge_x, header_y))

        if not self.available_recipes:
            no_txt = font.render("No craftable items with current materials.", True, (160, 170, 190))
            target_surf.blit(no_txt, (start_x, start_y + 4))
            return

        hovered = None

        for i, recipe in enumerate(self.available_recipes):
            rx = start_x + (i % 6) * (icon_size + padding)
            ry = start_y + (i // 6) * (icon_size + padding)
            rect = pygame.Rect(rx, ry, icon_size, icon_size)

            can_craft = recipe.get("can_craft", True)
            bg_color = (30, 35, 50, 220) if can_craft else (20, 22, 30, 240)
            pygame.draw.rect(target_surf, bg_color, rect)
            border_color = (90, 100, 130) if can_craft else (55, 60, 75)
            pygame.draw.rect(target_surf, border_color, rect, 1)

            res_id = recipe["result"]
            icon = self.asset_factory.items.get(res_id)
            if icon:
                if not can_craft:
                    dimmed = icon.copy()
                    dim_overlay = pygame.Surface(dimmed.get_size(), pygame.SRCALPHA)
                    dim_overlay.fill((0, 0, 0, 130))
                    dimmed.blit(dim_overlay, (0, 0))
                    target_surf.blit(dimmed, (rx + 6, ry + 6))
                else:
                    target_surf.blit(icon, (rx + 6, ry + 6))

            if recipe["count"] > 1:
                cnt_txt = font.render(str(recipe["count"]), True, (255, 255, 255) if can_craft else (140, 140, 140))
                target_surf.blit(cnt_txt, (rx + icon_size - 14, ry + icon_size - 14))

            if rect.collidepoint(mouse_x, mouse_y):
                pygame.draw.rect(target_surf, (255, 230, 80) if can_craft else (200, 90, 90), rect, 2)
                hovered = recipe

        if hovered:
            self._render_recipe_tooltip(target_surf, mouse_x, mouse_y, hovered, font)

    def _render_recipe_tooltip(self, target_surf, mx, my, recipe, font):
        res_data = ITEM_REGISTRY.get(recipe["result"], {})
        name = res_data.get("name", recipe["result"])
        count_suffix = f" (x{recipe['count']})" if recipe["count"] > 1 else ""
        rarity = res_data.get("rarity", RARITY_COMMON)
        r_color = RARITY_COLORS.get(rarity, (255, 255, 255))
        can_craft = recipe.get("can_craft", True)

        lines = [(f"{name}{count_suffix}", r_color)]

        # Station info
        st_text = "Station: By Hand"
        if recipe["station"] == "work_bench":
            st_text = "Station: Work Bench Required"
        elif recipe["station"] == "furnace":
            st_text = "Station: Furnace Required"
        lines.append((st_text, (255, 215, 100)))

        # Description
        desc = res_data.get("desc")
        if desc:
            lines.append((desc, (200, 215, 235)))

        lines.append(("Ingredients:", (220, 220, 220)))
        for iname, icnt in recipe["ingredients"]:
            ing_data = ITEM_REGISTRY.get(iname, {})
            in_title = ing_data.get("name", iname)
            owned = self.last_inventory.count_item(iname) if self.last_inventory else 0
            if owned >= icnt:
                lines.append((f"  • {in_title}: {owned} / {icnt}", (140, 240, 140)))
            else:
                needed = icnt - owned
                lines.append((f"  • {in_title}: {owned} / {icnt} (Need {needed})", (255, 100, 100)))

        if can_craft:
            lines.append(("[Click to Craft]", (100, 220, 255)))
        else:
            lines.append(("[Missing Ingredients]", (240, 80, 80)))

        line_surfs = [font.render(text, True, color) for text, color in lines]
        tip_w = max(s.get_width() for s in line_surfs) + 18
        tip_h = len(line_surfs) * 18 + 12

        tip_x = min(target_surf.get_width() - tip_w - 10, mx + 16)
        tip_y = min(target_surf.get_height() - tip_h - 10, my + 16)

        tip_rect = pygame.Rect(tip_x, tip_y, tip_w, tip_h)
        pygame.draw.rect(target_surf, (20, 24, 38, 245), tip_rect, border_radius=6)
        pygame.draw.rect(target_surf, r_color, tip_rect, 1, border_radius=6)

        for i, s in enumerate(line_surfs):
            target_surf.blit(s, (tip_x + 9, tip_y + 6 + i * 18))
