"""
Potaria - Town NPCs & Friendly Villagers System
Handles friendly Spud villagers (Guide, Merchant, Nurse, Blacksmith) who settle into
validated player-constructed houses, wander within rooms, and provide vital services,
dialogues, shops, healing, and weapon enhancements.
Developer: Kurados
"""

import math
import random
import pygame
from src.constants import (
    SCALED_TILE, CAT_WEAPON, CAT_TOOL,
    COLOR_GOLD, RARITY_COLORS, RARITY_COMMON
)
from src.ui.inventory import ItemStack, ITEM_REGISTRY

NPC_TYPES = ("guide", "merchant", "nurse", "blacksmith")

NPC_TITLES = {
    "guide": ("Pip", "Town Guide", (120, 215, 100)),
    "merchant": ("Barnaby", "Town Merchant", (255, 215, 80)),
    "nurse": ("Florencia", "Field Nurse", (255, 140, 170)),
    "blacksmith": ("Russet", "Master Blacksmith", (245, 150, 60)),
}


class TownNPC:
    def __init__(self, name, npc_type, x, y, asset_factory, sound_manager, home_tile=None):
        self.name = name
        self.npc_type = npc_type
        self.role_title = NPC_TITLES.get(npc_type, ("Spud", "Villager", (220, 220, 220)))[1]
        self.role_color = NPC_TITLES.get(npc_type, ("Spud", "Villager", (220, 220, 220)))[2]

        self.x = float(x)
        self.y = float(y)
        self.vx = 0.0
        self.vy = 0.0
        self.width = 28
        self.height = 36
        self.frect = pygame.FRect(self.x, self.y, self.width, self.height)

        self.asset_factory = asset_factory
        self.sound_manager = sound_manager
        self.home_tile = home_tile  # (tx, ty) of house
        self.facing_right = True
        self.on_ground = False

        # AI & Wandering
        self.wander_timer = random.uniform(1.5, 4.0)
        self.target_vx = 0.0
        self.is_talking = False

        # Visual assets
        self.sprite = asset_factory.npcs.get(npc_type) if hasattr(asset_factory, "npcs") else None
        self.portrait = asset_factory.npc_portraits.get(npc_type) if hasattr(asset_factory, "npc_portraits") else None

        pygame.font.init()
        self.font = pygame.font.SysFont("Arial", 11, bold=True)
        self.font_hint = pygame.font.SysFont("Arial", 10, bold=True)

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

    def can_interact(self, player):
        """Returns True if the player is within conversational speaking distance."""
        dist = math.hypot(self.center_x - player.center_x, self.center_y - player.center_y)
        return dist <= 68.0

    def update(self, dt, world):
        if self.is_talking:
            self.vx = 0.0
            return

        # Gravity
        self.vy = min(10.0, self.vy + 0.44)

        # Wandering AI
        self.wander_timer -= dt
        if self.wander_timer <= 0.0:
            self.wander_timer = random.uniform(2.5, 6.0)
            if self.home_tile:
                home_px = self.home_tile[0] * SCALED_TILE + SCALED_TILE // 2
                dist_from_home = self.center_x - home_px
                if abs(dist_from_home) > 100.0:
                    # Walk back toward home
                    self.target_vx = -1.1 if dist_from_home > 0 else 1.1
                else:
                    self.target_vx = random.choice([0.0, 0.0, -0.9, 0.9])
            else:
                self.target_vx = random.choice([0.0, 0.0, -0.85, 0.85])

        # Smooth velocity towards target
        self.vx = self.vx * 0.8 + self.target_vx * 0.2
        if abs(self.vx) > 0.15:
            self.facing_right = (self.vx > 0)

        # Autonomous step-up / jump over 1-block obstacles
        if self.on_ground and abs(self.target_vx) > 0.1:
            check_x = self.center_x + (16.0 if self.facing_right else -16.0)
            tx = int(check_x // SCALED_TILE)
            foot_ty = int((self.y + self.height - 4) // SCALED_TILE)
            head_ty = int(self.y // SCALED_TILE)
            if world.is_tile_solid(tx, foot_ty) and not world.is_tile_solid(tx, head_ty - 1):
                self.vy = -6.2
                self.on_ground = False

        # Horizontal movement & collision
        self.x += self.vx
        self.frect.x = self.x
        solids = world.get_solid_rects_in_bounds(self.rect)
        for tile_rect, is_platform in solids:
            if is_platform:
                continue
            if self.frect.colliderect(tile_rect):
                if self.vx > 0:
                    self.frect.right = tile_rect.left
                    self.x = self.frect.x
                    self.target_vx = -self.target_vx
                elif self.vx < 0:
                    self.frect.left = tile_rect.right
                    self.x = self.frect.x
                    self.target_vx = -self.target_vx

        # Vertical movement & collision
        self.y += self.vy
        self.frect.y = self.y
        self.on_ground = False
        solids = world.get_solid_rects_in_bounds(self.rect)
        for tile_rect, is_platform in solids:
            if is_platform:
                if self.vy > 0 and self.frect.bottom >= tile_rect.top and (self.frect.bottom - self.vy) <= tile_rect.top + 6:
                    self.frect.bottom = tile_rect.top
                    self.y = self.frect.y
                    self.vy = 0.0
                    self.on_ground = True
            else:
                if self.frect.colliderect(tile_rect):
                    if self.vy > 0:
                        self.frect.bottom = tile_rect.top
                        self.y = self.frect.y
                        self.vy = 0.0
                        self.on_ground = True
                    elif self.vy < 0:
                        self.frect.top = tile_rect.bottom
                        self.y = self.frect.y
                        self.vy = 0.0

    def render(self, target_surf, camera, player=None):
        sx, sy = camera.world_to_screen(self.x, self.y)

        # Draw character sprite
        if self.sprite:
            draw_surf = self.sprite if self.facing_right else pygame.transform.flip(self.sprite, True, False)
            target_surf.blit(draw_surf, (sx, sy))
        else:
            pygame.draw.rect(target_surf, (200, 150, 90), (sx, sy, self.width, self.height), border_radius=4)

        # Name & Title floating badge
        name_tag = f"{self.name}"
        t_surf = self.font.render(name_tag, True, (255, 255, 255))
        tag_w = t_surf.get_width() + 10
        tag_h = 16
        tx = sx + self.width // 2 - tag_w // 2
        ty = sy - 20

        bg_rect = pygame.Rect(tx, ty, tag_w, tag_h)
        pygame.draw.rect(target_surf, (20, 24, 34, 210), bg_rect, border_radius=4)
        pygame.draw.rect(target_surf, self.role_color, bg_rect, 1, border_radius=4)
        target_surf.blit(t_surf, (tx + 5, ty + 2))

        # Interaction hint [E] Talk
        if player and self.can_interact(player):
            hint_txt = self.font_hint.render("[E] Talk", True, (255, 235, 100))
            hw = hint_txt.get_width() + 10
            hx = sx + self.width // 2 - hw // 2
            hy = ty - 18
            h_rect = pygame.Rect(hx, hy, hw, 14)
            pygame.draw.rect(target_surf, (30, 40, 60, 230), h_rect, border_radius=3)
            pygame.draw.rect(target_surf, (255, 215, 80), h_rect, 1, border_radius=3)
            target_surf.blit(hint_txt, (hx + 5, hy + 1))

    def to_dict(self):
        return {
            "name": self.name,
            "npc_type": self.npc_type,
            "x": self.x,
            "y": self.y,
            "home_tile": list(self.home_tile) if self.home_tile else None
        }

    @classmethod
    def from_dict(cls, data, asset_factory, sound_manager):
        t_type = data.get("npc_type", "guide")
        name = data.get("name", "Pip")
        x = data.get("x", 200.0)
        y = data.get("y", 200.0)
        ht = tuple(data["home_tile"]) if data.get("home_tile") else None
        cls_map = {
            "guide": GuideNPC,
            "merchant": MerchantNPC,
            "nurse": NurseNPC,
            "blacksmith": BlacksmithNPC
        }
        target_cls = cls_map.get(t_type, TownNPC)
        return target_cls(name, t_type, x, y, asset_factory, sound_manager, home_tile=ht)


# ==============================================================================
# 1. Guide Spud (Pip - Guidance, Biome Lore & Crafting Hints)
# ==============================================================================
class GuideNPC(TownNPC):
    def __init__(self, name, npc_type, x, y, asset_factory, sound_manager, home_tile=None):
        super().__init__(name, npc_type, x, y, asset_factory, sound_manager, home_tile)

    def get_advice(self, player, world, combat=None):
        quotes = [
            "Welcome to Potaria! A sheltered cabin with background walls, a door, a torch, a table, and a bed will invite friendly Spuds to settle here.",
            "Mining deep beneath the loam reveals veins of copper, iron, and lustrous gold. Smelt raw ores at a stone furnace!",
            "To face Lord Malus in the Nether Dungeon, seek out the dungeon altar deep underground, or forge a Dungeon Teleporter Rune.",
            "Beware the Glacial Wastes! The Cryo-Spud lurks in a freezing pocket dimension. Prepare warm armor and high-tier weapons.",
            "When night falls, Night Gazers take flight. If you're overwhelmed, retreat into your home and close the wooden door.",
            "Water offers vital resources! You can swim upward by pressing Jump, but watch your oxygen bubbles so you don't drown.",
            "The Legendary Astral Wrath calls down stars from the heavens with every swing. Find celestial portal shards to forge it!"
        ]
        # Contextual advice
        if player.health < player.max_health * 0.4:
            return "You look badly wounded! Visit Florencia the Nurse in her clinic, or consume harvested potatoes to regain your health."
        if combat and combat.boss and not combat.boss.is_dead:
            return f"A titan walks the realm! {combat.boss.name} has awakened! Dodge their attacks and strike when their defenses waver!"
        return random.choice(quotes)


# ==============================================================================
# 2. Merchant Spud (Barnaby - General Goods, Survival Tools & Items)
# ==============================================================================
class MerchantNPC(TownNPC):
    def __init__(self, name, npc_type, x, y, asset_factory, sound_manager, home_tile=None):
        super().__init__(name, npc_type, x, y, asset_factory, sound_manager, home_tile)
        self.shop_catalog = [
            {"item_id": "torch", "name": "Torch", "price": 1, "currency": "copper_coin", "count": 5},
            {"item_id": "wooden_arrow", "name": "Wooden Arrow", "price": 2, "currency": "copper_coin", "count": 25},
            {"item_id": "healing_potion", "name": "Healing Potion", "price": 15, "currency": "copper_coin", "count": 1},
            {"item_id": "speed_potion", "name": "Swiftness Potion", "price": 25, "currency": "copper_coin", "count": 1},
            {"item_id": "copper_pickaxe", "name": "Copper Pickaxe", "price": 30, "currency": "copper_coin", "count": 1},
            {"item_id": "copper_axe", "name": "Copper Axe", "price": 25, "currency": "copper_coin", "count": 1},
            {"item_id": "wood_platform", "name": "Wood Platform", "price": 2, "currency": "copper_coin", "count": 10},
            {"item_id": "stone_brick", "name": "Stone Brick", "price": 5, "currency": "copper_coin", "count": 10},
        ]

    def get_quote(self):
        quotes = [
            "Fresh wares from across the continents! Safe spelunking starts with plenty of torches.",
            "Need arrows for your bow? I keep a fresh bundle stocked at all times.",
            "Got any extra ores or trinkets? I buy all sorts of subterranean oddities for fair coin.",
            "Keep an eye on your coin pouch! 100 copper makes a shining silver piece."
        ]
        return random.choice(quotes)


# ==============================================================================
# 3. Nurse Spud (Florencia - Full Health & Mana Restorative Care)
# ==============================================================================
class NurseNPC(TownNPC):
    def __init__(self, name, npc_type, x, y, asset_factory, sound_manager, home_tile=None):
        super().__init__(name, npc_type, x, y, asset_factory, sound_manager, home_tile)

    def calculate_heal_cost(self, player):
        missing = player.max_health - player.health
        if missing <= 0:
            return 0
        return max(1, missing // 4)

    def heal_player(self, player, inventory):
        cost = self.calculate_heal_cost(player)
        if cost == 0:
            return False, "You are already at peak potato vitality!"
        
        # Count copper coins
        current_copper = inventory.count_item("copper_coin")
        if current_copper < cost:
            return False, f"Healing requires {cost} Copper Coins (You have {current_copper})."
        
        # Deduct coins and heal
        inventory.remove_item("copper_coin", cost)
        player.health = player.max_health
        if hasattr(player, "stats"):
            player.stats.hp = player.max_health
            player.stats.mp = player.stats.max_mp
        player.is_dead = False
        self.sound_manager.play("craft")
        return True, f"Wounds mended and vitality restored to full! (-{cost} Copper Coins)"


# ==============================================================================
# 4. Blacksmith Spud (Russet - Metal Ingots, Bombs & Weapon Honing)
# ==============================================================================
class BlacksmithNPC(TownNPC):
    def __init__(self, name, npc_type, x, y, asset_factory, sound_manager, home_tile=None):
        super().__init__(name, npc_type, x, y, asset_factory, sound_manager, home_tile)
        self.shop_catalog = [
            {"item_id": "copper_bar", "name": "Copper Ingot", "price": 10, "currency": "copper_coin", "count": 1},
            {"item_id": "iron_bar", "name": "Iron Ingot", "price": 25, "currency": "copper_coin", "count": 1},
            {"item_id": "gold_bar", "name": "Gold Ingot", "price": 60, "currency": "copper_coin", "count": 1},
            {"item_id": "bomb", "name": "Excavation Bomb", "price": 20, "currency": "copper_coin", "count": 1},
        ]

    def hone_weapon(self, player, inventory):
        """Tempers player's currently held weapon to grant +15% ATK and +10% Attack Speed."""
        active = inventory.get_active_item()
        if not active or (active.data.get("cat") != CAT_WEAPON and active.data.get("damage", 0) <= 0):
            return False, "Equip or hold a valid weapon in your hand first!"

        honed_tag = active.data.get("_is_honed", False)
        if honed_tag:
            return False, f"{active.data.get('name', 'This weapon')} is already tempered to perfection!"

        cost = 35
        current_copper = inventory.count_item("copper_coin")
        if current_copper < cost:
            return False, f"Weapon honing requires {cost} Copper Coins (You have {current_copper})."

        # Apply forge honing
        inventory.remove_item("copper_coin", cost)
        active.data["_is_honed"] = True
        active.data["atk"] = active.data.get("atk", 10) + max(3, int(active.data.get("atk", 10) * 0.15))
        active.data["speed"] = active.data.get("speed", 0.0) + 0.10
        w_name = active.data.get("name", "Weapon")
        active.data["name"] = f"Honed {w_name}"
        if "effects" not in active.data:
            active.data["effects"] = []
        active.data["effects"].append("Forgemaster's Edge (+15% Damage, +10% Speed)")

        player.equipment.recalculate_stats(player.stats, active.item_id)
        self.sound_manager.play("craft")
        return True, f"Forged and sharpened! {active.data['name']} now strikes with greater power!"
