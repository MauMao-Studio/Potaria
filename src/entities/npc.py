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

NPC_TYPES = ("guide", "merchant", "nurse", "blacksmith", "mystic_trader", "trader_wares", "trader_enhance", "trader_affix")

NPC_TITLES = {
    "guide": ("Pip", "Town Guide", (120, 215, 100)),
    "merchant": ("Barnaby", "Town Merchant", (255, 215, 80)),
    "nurse": ("Florencia", "Field Nurse", (255, 140, 170)),
    "blacksmith": ("Russet", "Master Blacksmith", (245, 150, 60)),
    "mystic_trader": ("Zephyrion", "Mystic Trader", (180, 100, 255)),
    "trader_wares": ("Zephyrion", "Wares Merchant", (100, 220, 255)),
    "trader_enhance": ("Ignis Vance", "Grand Artificer", (255, 160, 50)),
    "trader_affix": ("Morrigan", "Runic Occultist", (195, 110, 255)),
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

        # Visual assets & idle animation
        self.sprite = asset_factory.npcs.get(npc_type) if hasattr(asset_factory, "npcs") else None
        self.anim_frames = asset_factory.npc_frames.get(npc_type, []) if hasattr(asset_factory, "npc_frames") else []
        self.anim_timer = 0.0
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
        self.anim_timer += dt
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

        # Draw character sprite (with multi-frame animation if present)
        active_surf = None
        if self.anim_frames:
            f_idx = int((self.anim_timer * 4.0) % len(self.anim_frames))
            active_surf = self.anim_frames[f_idx]
        elif self.sprite:
            active_surf = self.sprite

        if active_surf:
            draw_surf = active_surf if self.facing_right else pygame.transform.flip(active_surf, True, False)
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
            "blacksmith": BlacksmithNPC,
            "mystic_trader": MysticTraderNPC,
            "trader_wares": WaresTraderNPC,
            "trader_enhance": EnhancerTraderNPC,
            "trader_affix": OccultistTraderNPC,
        }
        target_cls = cls_map.get(t_type, TownNPC)
        if target_cls in (MysticTraderNPC, WaresTraderNPC, EnhancerTraderNPC, OccultistTraderNPC) or issubclass(target_cls, MysticTraderNPC):
            dur = data.get("duration", 240.0)
            tl = data.get("time_left", dur)
            sc = data.get("shop_catalog")
            npc_obj = target_cls(name=name, npc_type=t_type, x=x, y=y, asset_factory=asset_factory, sound_manager=sound_manager, home_tile=ht, duration=dur, shop_catalog=sc)
            npc_obj.time_left = tl
            return npc_obj
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


# ==============================================================================
# 5. Mystic Wandering Trader Spud (Zephyrion - Wandering Merchant)
# ==============================================================================
class MysticTraderNPC(TownNPC):
    def __init__(self, name="Zephyrion", npc_type="mystic_trader", x=200.0, y=200.0, asset_factory=None, sound_manager=None, home_tile=None, duration=240.0, shop_catalog=None):
        super().__init__(name, npc_type, x, y, asset_factory, sound_manager, home_tile)
        self.duration = float(duration)
        self.time_left = float(duration)
        self.is_despawned = False
        self.shield_active = False
        self.shield_radius = 3 * SCALED_TILE # 96 px (3 blocks radius)
        self.shield_anim_time = 0.0

        if shop_catalog is not None:
            self.shop_catalog = shop_catalog
        else:
            self.shop_catalog = self.roll_wares()

    def repair_item(self, target_item, inventory):
        """All Mystic Traders can repair broken gear for 1 Gold Coin (10,000 Copper)."""
        from src.rpg.enhancement import repair_item
        return repair_item(target_item, inventory, self.sound_manager)

    def roll_wares(self):
        """
        Rolls 5 weapons/equipment items.
        Show rate is the same as the drop rate:
        - Common: 40.0
        - Uncommon: 3.5
        - Rare: 1.5
        - Epic: 0.5
        Capped strictly at Epic (no skill books, no mythic, legendary, ancient).
        Also randomly offers an Affix Carving chance in store.
        """
        from src.ui.inventory import ITEM_REGISTRY, CAT_WEAPON, CAT_TOOL

        pools = {"common": [], "uncommon": [], "rare": [], "epic": []}
        for iid, idata in ITEM_REGISTRY.items():
            r = idata.get("rarity", "common")
            cat = idata.get("cat", "")
            # Only weapons and equipment, strictly NO skill books and NO tools
            if cat in ("weapon", "armor_head", "armor_chest", "armor_legs", "accessory") and not any(k in iid for k in ("skillbook", "pickaxe", "axe", "shovel")):
                if r in pools:
                    pools[r].append(iid)

        # Fallbacks if any pool empty
        if not pools["common"]:
            pools["common"] = ["wooden_sword", "copper_broadsword", "potato_cap", "potato_tunic"]
        if not pools["uncommon"]:
            pools["uncommon"] = ["cactus_sword", "frost_hood", "iron_helmet", "iron_chestplate"]
        if not pools["rare"]:
            pools["rare"] = ["gold_broadsword", "frost_blade", "shadow_cleaver", "sandstorm_spear"]
        if not pools["epic"]:
            pools["epic"] = ["magma_greatsword", "bone_scythe", "starch_blade", "zephyr_striders", "talisman_of_vigor"]

        weights = {"common": 40.0, "uncommon": 3.5, "rare": 1.5, "epic": 0.5}
        rarity_choices = list(weights.keys())
        rarity_weights = list(weights.values())

        catalog = []
        # Roll 5 items
        for _ in range(5):
            r = random.choices(rarity_choices, weights=rarity_weights, k=1)[0]
            item_pool = pools[r]
            iid = random.choice(item_pool)
            idata = ITEM_REGISTRY.get(iid, {})
            name = idata.get("name", iid.replace("_", " ").title())

            # Prices appropriate to ARPG rarity
            if r == "common":
                price = random.randint(25, 60)
                curr = "copper_coin"
            elif r == "uncommon":
                price = random.randint(120, 250)
                curr = "copper_coin"
            elif r == "rare":
                price = random.randint(4, 9)
                curr = "silver_coin"
            else:
                price = random.randint(18, 35)
                curr = "silver_coin"

            catalog.append({
                "item_id": iid,
                "name": name,
                "price": price,
                "currency": curr,
                "count": 1,
                "rarity": r
            })

        # Random chance to replace one slot with an Affix Slot Carving Voucher
        if random.random() < 0.40 and len(catalog) > 0:
            replace_idx = random.randint(0, len(catalog) - 1)
            catalog[replace_idx] = {
                "item_id": "affix_slot_service",
                "name": "Affix Slot Carving",
                "price": 50,
                "currency": "silver_coin",
                "count": 1,
                "is_affix_service": True,
                "rarity": "legendary"
            }

        return catalog

    def check_hostile_enemies(self, combat):
        """Checks for hostile enemies within 7 blocks (224px). Activates/deactivates Turtle Shield."""
        if not combat:
            self.shield_active = False
            return False

        radius = self.shield_radius
        cx = self.center_x
        cy = self.center_y

        for mob in getattr(combat, "mobs", []):
            if getattr(mob, "is_alive", True) and not getattr(mob, "is_dead", False) and getattr(mob, "hp", 1) > 0:
                dist = math.hypot(mob.center_x - cx, mob.center_y - cy)
                if dist <= radius:
                    self.shield_active = True
                    return True

        boss = getattr(combat, "boss", None)
        if boss and getattr(boss, "is_alive", True) and not getattr(boss, "is_dead", False) and getattr(boss, "hp", 1) > 0:
            dist = math.hypot(boss.center_x - cx, boss.center_y - cy)
            if dist <= radius:
                self.shield_active = True
                return True

        self.shield_active = False
        return False

    def can_interact(self, player):
        """Cannot interact/trade while Turtle Shield is active or when player is too far."""
        if self.shield_active:
            return False
        return super().can_interact(player)

    def on_hit(self, damage=0):
        """When attacked or impacted, the Turtle Shield deflects attacks with zero damage."""
        if self.shield_active:
            if self.sound_manager:
                self.sound_manager.play("hit")
            return 0  # 100% deflected
        return damage

    def update(self, dt, world, combat=None):
        if self.is_despawned:
            return

        self.time_left -= dt
        self.shield_anim_time += dt

        if combat:
            self.check_hostile_enemies(combat)

        # When shielded: Turtle retracts into its shell, completely stationary
        if self.shield_active:
            self.vx = 0.0
            self.target_vx = 0.0
            if self.is_talking:
                self.is_talking = False
            self.vy = min(10.0, self.vy + 0.44)
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
            return

        if self.time_left <= 0.0:
            self.despawn(world)
            return

        super().update(dt, world)

    def despawn(self, world=None):
        """Teleports away regardless of being caged or enclosed in blocks."""
        self.is_despawned = True
        self.is_talking = False
        if world and hasattr(world, "town_npcs") and self in world.town_npcs:
            world.town_npcs.remove(self)

    def get_quote(self):
        quotes = [
            "The cosmic winds whisper of great battles. I have traveled across dimensions to bring you these rare armaments!",
            "Need a broken blade forged anew? For a single gold coin, I can mend even the most shattered relics.",
            "Bring me Legendary or Ancient arms, and I will hollow out an Affix Slot to channel the gods!",
            "I shall depart soon—my dimensional tether only lasts a few moments. Peruse my wares while you may!"
        ]
        return random.choice(quotes)

    def render(self, target_surf, camera, player=None):
        if self.is_despawned:
            return

        sx, sy = camera.world_to_screen(self.x, self.y)

        # 1. Turtle / Energy Shield VFX
        if self.shield_active:
            pulse = math.sin(self.shield_anim_time * 5.0) * 2.0
            shield_w = self.width + 24 + int(pulse)
            shield_h = self.height + 16 + int(pulse)
            shield_x = sx + self.width // 2 - shield_w // 2
            shield_y = sy + self.height // 2 - shield_h // 2

            shield_surf = pygame.Surface((shield_w, shield_h), pygame.SRCALPHA)
            pygame.draw.ellipse(shield_surf, (80, 220, 255, 75), (0, 0, shield_w, shield_h))
            pygame.draw.ellipse(shield_surf, (140, 255, 200, 140), (2, 2, shield_w - 4, shield_h - 4), 2)
            pygame.draw.ellipse(shield_surf, (255, 230, 80, 180), (0, 0, shield_w, shield_h), 2)
            pygame.draw.line(shield_surf, (100, 235, 255, 120), (shield_w // 2, 4), (shield_w // 2, shield_h - 4), 1)
            pygame.draw.line(shield_surf, (100, 235, 255, 120), (4, shield_h // 2), (shield_w - 4, shield_h // 2), 1)
            target_surf.blit(shield_surf, (shield_x, shield_y))

        # 2. Character Sprite
        super().render(target_surf, camera, player)

        # 3. Floating Time Left Badge & Shield Warning
        mins = int(max(0, self.time_left) // 60)
        secs = int(max(0, self.time_left) % 60)
        time_tag = f"{self.role_title} [{mins}:{secs:02d}]"
        t_col = (255, 220, 100) if not self.shield_active else (100, 230, 255)
        t_surf = self.font_hint.render(time_tag, True, t_col)
        tx = sx + self.width // 2 - t_surf.get_width() // 2
        ty = sy - 36
        bg_r = pygame.Rect(tx - 4, ty - 1, t_surf.get_width() + 8, 14)
        pygame.draw.rect(target_surf, (18, 14, 30, 220), bg_r, border_radius=3)
        pygame.draw.rect(target_surf, (180, 100, 255), bg_r, 1, border_radius=3)
        target_surf.blit(t_surf, (tx, ty))

        if self.shield_active:
            sh_txt = self.font_hint.render("[TURTLE SHIELD ACTIVE]", True, (255, 100, 100))
            sx_pos = sx + self.width // 2 - sh_txt.get_width() // 2
            sy_pos = ty - 16
            sh_r = pygame.Rect(sx_pos - 4, sy_pos - 1, sh_txt.get_width() + 8, 14)
            pygame.draw.rect(target_surf, (40, 12, 18, 220), sh_r, border_radius=3)
            pygame.draw.rect(target_surf, (255, 70, 70), sh_r, 1, border_radius=3)
            target_surf.blit(sh_txt, (sx_pos, sy_pos))

    def to_dict(self):
        d = super().to_dict()
        d["duration"] = self.duration
        d["time_left"] = self.time_left
        d["shop_catalog"] = self.shop_catalog
        return d


# ==============================================================================
# 5a. Wares Merchant Spud (Zephyrion - Rare Armaments & Gear)
# ==============================================================================
class WaresTraderNPC(MysticTraderNPC):
    """Zephyrion the Wandering Merchant - Specializes in weapons and armor wares."""
    def __init__(self, name="Zephyrion", npc_type="trader_wares", x=200.0, y=200.0, asset_factory=None, sound_manager=None, home_tile=None, duration=240.0, shop_catalog=None):
        super().__init__(name=name, npc_type=npc_type, x=x, y=y, asset_factory=asset_factory, sound_manager=sound_manager, home_tile=home_tile, duration=duration, shop_catalog=shop_catalog)

    def get_quote(self):
        quotes = [
            "The cosmic winds whisper of great battles! Peruse my rare armaments before I depart.",
            "A broken blade? For 1 gold coin, I can mend even the most shattered relics.",
            "I travel between the stars to bring you these fine blades, bows, and tunics. Choose wisely!",
            "My dimensional tether lasts only a few minutes. Trade while the stars align!"
        ]
        return random.choice(quotes)


# ==============================================================================
# 5b. Grand Artificer Spud (Ignis Vance - Master Gear Enhancer)
# ==============================================================================
class EnhancerTraderNPC(MysticTraderNPC):
    """Ignis Vance the Grand Artificer - Master of equipment forging and enhancement (+1..+7)."""
    def __init__(self, name="Ignis Vance", npc_type="trader_enhance", x=200.0, y=200.0, asset_factory=None, sound_manager=None, home_tile=None, duration=240.0, shop_catalog=None):
        super().__init__(name=name, npc_type=npc_type, x=x, y=y, asset_factory=asset_factory, sound_manager=sound_manager, home_tile=home_tile, duration=duration, shop_catalog=shop_catalog or [])

    def roll_wares(self):
        # Grand Artificer provides enhancement materials and rare smithing catalysts
        catalog = [
            {"item_id": "iron_bar", "name": "Refined Iron Bar", "price": 40, "currency": "copper_coin", "count": 5, "rarity": "common"},
            {"item_id": "gold_bar", "name": "Lustrous Gold Bar", "price": 3, "currency": "silver_coin", "count": 2, "rarity": "uncommon"},
            {"item_id": "celestial_shard", "name": "Celestial Starch Core", "price": 12, "currency": "silver_coin", "count": 1, "rarity": "rare"},
            {"item_id": "affix_stone", "name": "Artificer's Whetstone", "price": 25, "currency": "silver_coin", "count": 1, "rarity": "epic"},
            {"item_id": "titan_alloy", "name": "Titan Forgestone", "price": 45, "currency": "silver_coin", "count": 1, "rarity": "epic"},
        ]
        return catalog

    def get_quote(self):
        quotes = [
            "The arcane forge calls to you! I can hone your weapons and gear up to +7 with my celestial anvil.",
            "Beware pushing past +4! The mystical resonance can break fragile gear. But I can mend broken arms for 1 gold coin.",
            "Give me steel, gold, and celestial shards, and I shall elevate your blade to godlike stature!",
            "A well-tempered blade cuts swifter than a thousand clumsy strikes. Shall we forge?"
        ]
        return random.choice(quotes)


# ==============================================================================
# 5c. Runic Occultist Spud (Morrigan - Affix Stone & Socket Master)
# ==============================================================================
class OccultistTraderNPC(MysticTraderNPC):
    """Morrigan the Runic Occultist - Carves Affix Slots and sockets Affix Stones into Legendary/Ancient gear."""
    def __init__(self, name="Morrigan", npc_type="trader_affix", x=200.0, y=200.0, asset_factory=None, sound_manager=None, home_tile=None, duration=240.0, shop_catalog=None):
        super().__init__(name=name, npc_type=npc_type, x=x, y=y, asset_factory=asset_factory, sound_manager=sound_manager, home_tile=home_tile, duration=duration, shop_catalog=shop_catalog or [])

    def roll_wares(self):
        catalog = [
            {"item_id": "affix_stone", "name": "Pristine Affix Stone", "price": 35, "currency": "silver_coin", "count": 1, "rarity": "epic"},
            {"item_id": "affix_slot_service", "name": "Affix Slot Carving", "price": 50, "currency": "silver_coin", "count": 1, "is_affix_service": True, "rarity": "legendary"},
            {"item_id": "celestial_shard", "name": "Void Resonator", "price": 15, "currency": "silver_coin", "count": 2, "rarity": "rare"},
            {"item_id": "shadow_essence", "name": "Starlight Catalyst", "price": 20, "currency": "silver_coin", "count": 1, "rarity": "epic"},
            {"item_id": "portal_shard", "name": "Runic Keystone", "price": 30, "currency": "silver_coin", "count": 1, "rarity": "epic"},
        ]
        return catalog

    def get_quote(self):
        quotes = [
            "The stars whisper of hidden potentials. Bring me Legendary or Ancient relics, and I shall carve Affix Slots into them!",
            "Through ancient Runic stones, your weapons shall gain powers that defy mortal comprehension.",
            "Broken weapons leak arcane energy. Bring me 1 gold coin, and I shall weave their shattered spirits whole.",
            "Mortals fear the void, but in the void lies infinite power. Let us inscribe your arms."
        ]
        return random.choice(quotes)

