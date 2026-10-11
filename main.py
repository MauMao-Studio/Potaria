"""
Potaria - The Spudtastic Adventure
Infinite Open World 2D Sandbox Action RPG & LAN Cooperative Multiplayer
Developer: Kurados
"""

import os
import sys
import math
import random

# Enable HD crisp pixel scaling (nearest-neighbor) in scaled and fullscreen modes
os.environ["SDL_RENDER_SCALE_QUALITY"] = "nearest"
# Prevent SDL2 from minimizing or hiding the borderless fullscreen window when Win+Shift+S / screenshot overlays take focus
os.environ.setdefault("SDL_VIDEO_MINIMIZE_ON_FOCUS_LOSS", "0")

# Enable 1ms Windows timer resolution for rock-solid 60 FPS frame pacing and 1:1 physical DPI awareness
if sys.platform == "win32":
    try:
        import ctypes
        ctypes.windll.winmm.timeBeginPeriod(1)
        try:
            ctypes.windll.shcore.SetProcessDpiAwareness(1)
        except Exception:
            ctypes.windll.user32.SetProcessDPIAware()
    except Exception:
        pass

import pygame

# Import Game Definitions & Modules
from src.constants import (
    SCREEN_WIDTH, SCREEN_HEIGHT, FPS, TITLE, DEVELOPER, SCALED_TILE,
    STATE_MENU, STATE_STORY, STATE_CUTSCENE, STATE_CONTROLS, STATE_PLAYING, STATE_VICTORY, STATE_SETTINGS,
    STATE_WORLDS, STATE_NEW_WORLD, STATE_GAME_OVER, STATE_MODS, STATE_ACHIEVEMENTS,
    DIFFICULTY_NORMAL, DIFFICULTY_HARDCORE, DIFFICULTY_YOLO,
    WORLD_TYPE_INFINITE, WORLD_TYPE_FINITE, CAVERN_LEVEL, DUNGEON_LEVEL,
    MODE_ADVENTURE, MODE_LAST_MAN_STANDING,
    TILE_AIR, TILE_DIRT, TILE_GRASS, TILE_STONE, TILE_WOOD,
    TILE_WOOD_TRUNK, TILE_LEAVES, TILE_COPPER_ORE, TILE_IRON_ORE,
    TILE_GOLD_ORE, TILE_TORCH, TILE_DUNGEON_ALTAR, TILE_CHEST,
    TILE_SAND, TILE_SANDSTONE, TILE_CACTUS, TILE_SNOW, TILE_ICE,
    TILE_CORRUPT_GRASS, TILE_EBONSTONE, TILE_MUSHROOM_GRASS,
    TILE_DOOR_CLOSED, TILE_DOOR_OPEN, TILE_BARRIER,
    TILE_BED, TILE_GRANDFATHER_CLOCK, TILE_FIREPLACE, TILE_PROPS,
    TILE_CARVED_TUBER_LANTERN, TILE_BRASS_LANTERN, TILE_SPECTRAL_LANTERN, LANTERN_TILES,
    TILE_BEDROCK, TILE_WATER,
    TILE_SAPLING, TILE_IRON_CHEST, TILE_ROPE_RUNGS,
    CAT_TOOL, CAT_WEAPON, CAT_BLOCK, CAT_WALL, CAT_CONSUMABLE, CAT_SPECIAL,
    PLAYER_WIDTH, PLAYER_HEIGHT
)
from src.world.save_manager import save_world, load_world, delete_world, list_saved_worlds
from src.assets.asset_factory import AssetFactory
from src.audio.sound_effects import SoundManager
from src.audio.bgm_manager import BgmManager
from src.world.world import World
from src.world.chunk_manager import CHUNK_WIDTH
from src.world.lighting import LightingEngine
from src.camera import Camera
from src.entities.player import Player
from src.entities.particle import ParticleSystem
from src.entities.vfx import VisualEffectManager
from src.entities.dropped_item import DroppedItem
from src.entities.projectile import (
    ArrowProjectile, CelestialStarProjectile,
    CatalystStarProjectile, StaffBoltProjectile,
    RodJavelinProjectile, ScepterPulseProjectile
)
from src.entities.boss import GrandBossSolRho
from src.combat.combat_system import CombatManager
from src.rpg.equipment import SLOT_WEAPON, SLOT_HEAD
from src.ui.inventory import Inventory, get_mining_damage
from src.ui.crafting import CraftingSystem
from src.ui.hud import HUD
from src.ui.menu import MenuManager, Button
from src.ui.character_panel import CharacterPanel
from src.ui.npc_dialogue import NPCDialogueWindow
from src.ui.chest_ui import ChestStorageWindow
from src.ui.fishing_minigame import FishingBattleMiniGame
from src.ui.touch_controller import TouchController
from src.entities.npc import TownNPC
from src.network.server import LANServer
from src.network.client import LANClient
from src.environment.sky import DayNightCycle
from src.rpg.achievements import AchievementManager
from src.profiler import PotariaProfiler
from src.rendering import (
    BaseRenderer,
    SurfaceRenderer,
    GLRenderer,
    RendererManager,
    RENDERER_HARDWARE,
    RENDERER_SOFTWARE,
    get_renderer_manager,
)

class PotariaGame:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption(f"{TITLE}  |  By {DEVELOPER}")
        # Initialize Renderer Hardware Abstraction Layer (HAL)
        self.renderer_manager = get_renderer_manager()
        self.renderer_manager.initialize(
            width=SCREEN_WIDTH,
            height=SCREEN_HEIGHT,
            title=f"{TITLE}  |  By {DEVELOPER}",
            fullscreen=False,
            requested_type=RENDERER_HARDWARE,
        )
        self.renderer = self.renderer_manager.renderer
        self.screen = self.renderer_manager.surface
        self.ui_screen = self.renderer_manager.ui_surface
        self.clock = pygame.time.Clock()
        self.running = True
        self.paused = False
        self.show_debug = False
        self.fullscreen = False
        self.profiler = PotariaProfiler(history_size=120)
        self.profiler.enabled = True
        self.show_profiler = False
        self.boost_mode = True

        # Fonts (Centralized Typography Theme)
        from src.ui.theme import font_regular, font_bold, font_title, font_compact
        self.font = font_regular(14)
        self.title_font = font_title(28)
        self.boss_font = font_bold(16)
        self.font_fps = font_compact(11)

        # 1. Initialize Asset Synthesis Engine
        print(f"[Engine] Synthesizing all procedural Potaria assets (Developer: {DEVELOPER})...")
        self.asset_factory = AssetFactory()
        self.asset_factory.export_all_assets("assets")

        # Set Window Game Icon!
        pygame.display.set_icon(self.asset_factory.branding["game_icon"])

        # 2. Audio Engine (SFX + Procedural Synth BGM)
        self.sound_manager = SoundManager()
        self.bgm = BgmManager()

        # 3. Particle System, VFX Manager & Camera
        self.particle_system = ParticleSystem()
        self.vfx_manager = VisualEffectManager(self.asset_factory)
        self.camera = Camera(SCREEN_WIDTH, SCREEN_HEIGHT)

        # 4. Generate Procedural World with a Random Seed
        self.world = World(self.asset_factory, seed=None)
        self.world.tree_cascade_felling = False
        self.fishing_bobber = None

        # 5. Spud the Potato Hero
        spawn_x, spawn_y = self.world.spawn_point
        self.player = Player(spawn_x, spawn_y, self.asset_factory, self.sound_manager)
        self.player.spawn_point = (spawn_x, spawn_y)
        self.player.particle_system = self.particle_system
        self.player.vfx_manager = self.vfx_manager
        self.god_mode = False
        self.speed_multiplier = 1.0
        self.camera.set_target(self.player.center_x, self.player.center_y, instant=True)

        # 6. Lighting & Sky
        self.lighting = LightingEngine(SCREEN_WIDTH, SCREEN_HEIGHT)
        self.sky = DayNightCycle(self.asset_factory)
        self.current_day = int(self.sky.time // max(1.0, self.sky.cycle_duration))

        # 7. Inventory, Crafting, HUD, Character Panel & Menu
        self.inventory = Inventory(self.asset_factory)
        self.player.inventory = self.inventory
        self.inventory.player = self.player
        self.crafting = CraftingSystem(self.asset_factory, self.sound_manager)
        self.hud = HUD(self.asset_factory)
        self.character_panel = CharacterPanel(self.asset_factory)
        self.npc_dialogue = NPCDialogueWindow(self.asset_factory, self.sound_manager)
        self.chest_ui = ChestStorageWindow(self.asset_factory, self.sound_manager)
        self.fishing_minigame = FishingBattleMiniGame(self.asset_factory, self.sound_manager)
        self.playtime = 0.0
        self.achievement_manager = AchievementManager(sound_manager=self.sound_manager)
        self.menu = MenuManager(self.asset_factory, self.sound_manager, self.bgm, self.achievement_manager)
        self._apply_graphics_settings()

        # 7b. Modding & DLC Expansion System
        from src.modding.mod_manager import get_mod_manager
        self.mod_manager = get_mod_manager()
        self.mod_manager.load_all(asset_factory=self.asset_factory, crafting_system=self.crafting)

        # 8. Mobile Virtual Touch Controller (Cross-Platform Controls)
        self.touch_controller = TouchController(self.asset_factory, self.sound_manager)
        self.touch_controller.game = self
        if hasattr(self.menu, "settings"):
            self.touch_controller.set_mode(self.menu.settings.get("touch_controls", "auto"))
            self.touch_controller.set_opacity(self.menu.settings.get("touch_opacity", 0.75))

        # World Options, Difficulty & Mode Configuration
        self.world_type = WORLD_TYPE_INFINITE
        self.difficulty = DIFFICULTY_NORMAL
        self.game_mode = MODE_ADVENTURE
        self.active_world_name = "Default World"
        self.block_deltas = {}
        self.wall_deltas = {}
        self.pvp_victor_banner = None
        self.pvp_banner_timer = 0.0

        # Pause Menu Interactive Buttons
        pause_btn_w, pause_btn_h = 280, 40
        pcx = SCREEN_WIDTH // 2 - pause_btn_w // 2
        p_start_y = SCREEN_HEIGHT // 2 - 145
        p_gap = 48
        self.pause_buttons = [
            Button(pcx, p_start_y, pause_btn_w, pause_btn_h, "RESUME GAME", "resume"),
            Button(pcx, p_start_y + p_gap * 2, pause_btn_w, pause_btn_h, "SETTINGS & AUDIO", "settings"),
            Button(pcx, p_start_y + p_gap * 5, pause_btn_w, pause_btn_h, "RETURN TO MENU (NO SAVE)", "main_menu"),
        ]
        self.pause_extra_buttons = [
            Button(pcx, p_start_y + p_gap, pause_btn_w, pause_btn_h, "ACHIEVEMENTS", "achievements"),
        ]
        self.save_buttons = [
            Button(pcx, p_start_y + p_gap * 3, pause_btn_w, pause_btn_h, "SAVE WORLD", "save"),
            Button(pcx, p_start_y + p_gap * 4, pause_btn_w, pause_btn_h, "SAVE & QUIT", "save_and_quit"),
        ]

        # 8. Combat Engine
        self.combat = CombatManager(self.asset_factory, self.sound_manager, self.particle_system, self.camera)

        # 9. LAN Multiplayer Networking (Host / Client)
        self.server = None
        self.client = None
        self.mob_sync_timer = 0.0

        # Mining Cooldown (Continuous Mining)
        self.mining_cooldown = 0.0
        self.continuous_mine_rate = 0.15

    def execute_cheat(self, cmd_str):
        """Executes in-game developer cheat / debugging console command."""
        cmd_str = cmd_str.strip()
        if not cmd_str.startswith("/"):
            return
        parts = cmd_str[1:].split()
        if not parts:
            return
        cmd = parts[0].lower()
        args = parts[1:]

        feedback = None

        if cmd in ("help", "?"):
            feedback = "Commands: /give <id> [count], /<item_id> [count], /god, /invincible, /heal, /speed [mult], /time <day|night|morning|0.0-1.0>, /spawn <mob|boss> [count], /ancient, /weapons, /killall, /level [count], /allskills, /boost, /profile, /clear"

        elif cmd in ("god", "invincible", "invencible", "immortal"):
            self.god_mode = not getattr(self, "god_mode", False)
            if self.god_mode:
                self.player.health = self.player.max_health
                if hasattr(self.player, "stats"):
                    self.player.stats.hp = self.player.stats.max_hp
                    self.player.stats.mp = self.player.stats.max_mp
                self.player.i_frame_timer = 1.0
                feedback = "God Mode: ENABLED (Invincible, Infinite HP/MP)"
            else:
                feedback = "God Mode: DISABLED"

        elif cmd == "heal":
            self.player.health = self.player.max_health
            if hasattr(self.player, "stats"):
                self.player.stats.hp = self.player.stats.max_hp
                self.player.stats.mp = self.player.stats.max_mp
            self.player.oxygen = self.player.max_oxygen
            self.particle_system.spawn_sparks(self.player.center_x, self.player.center_y, (100, 255, 140), count=25)
            self.sound_manager.play("craft")
            feedback = "Spud has been fully healed! (HP and MP restored)"

        elif cmd == "speed":
            mult = 2.0
            if args:
                try:
                    mult = float(args[0])
                except ValueError:
                    mult = 2.0
            elif getattr(self.player, "speed_multiplier", 1.0) > 1.0:
                mult = 1.0
            self.speed_multiplier = mult
            self.player.speed_multiplier = mult
            feedback = f"Movement speed multiplier set to {mult:.1f}x"

        elif cmd == "time":
            if not args:
                feedback = f"Current time: {self.sky.get_time_string()} ({self.sky.time / max(1.0, self.sky.cycle_duration):.2f})"
            else:
                arg = args[0].lower()
                dur = self.sky.cycle_duration
                if arg in ("morning", "dawn", "daybreak"):
                    self.sky.time = dur * 0.10
                elif arg in ("day", "noon", "midday"):
                    self.sky.time = dur * 0.25
                elif arg in ("dusk", "sunset"):
                    self.sky.time = dur * 0.48
                elif arg in ("night", "midnight"):
                    self.sky.time = dur * 0.75
                else:
                    try:
                        val = float(arg)
                        self.sky.time = (val % 1.0) * dur
                    except ValueError:
                        self.sky.time = dur * 0.25
                feedback = f"Time set to: {self.sky.get_time_string()}"

        elif cmd in ("give", "item"):
            if not args:
                feedback = "Usage: /give <item_id> [count]"
            else:
                from src.ui.inventory import ITEM_REGISTRY, ITEM_ALIASES
                item_id = args[0].lower()
                item_id = ITEM_ALIASES.get(item_id, item_id)
                count = 1
                if len(args) > 1:
                    try:
                        count = max(1, min(999, int(args[1])))
                    except ValueError:
                        count = 1
                if item_id in ITEM_REGISTRY:
                    leftover = self.inventory.add_item(item_id, count)
                    if leftover > 0:
                        self.drop_item_into_world(item_id, leftover)
                    name = ITEM_REGISTRY[item_id].get("name", item_id)
                    feedback = f"Gave {count}x {name} to Spud!"
                    self.sound_manager.play("craft")
                else:
                    feedback = f"Unknown item ID '{item_id}'. Check CHEATS.md or item registry."

        elif cmd == "ancient":
            self.player.equipment.slots["head"] = "ancient_helmet"
            self.player.equipment.slots["chest"] = "ancient_chestplate"
            self.player.equipment.slots["legs"] = "ancient_greaves"
            self.player.equipment.slots["weapon"] = "ancient_eternal_shortbow"
            self.player.equipment.recalculate_stats(self.player.stats)
            self.inventory.add_item("astral_arrow", 250)
            self.inventory.add_item("eternal_catalyst", 1)
            self.inventory.add_item("ancient_forgotten_rod", 1)
            self.inventory.add_item("celestial_greatsword", 1)
            self.sound_manager.play("craft")
            self.particle_system.spawn_sparks(self.player.center_x, self.player.center_y, (255, 215, 60), count=60)
            self.particle_system.spawn_debris(self.player.center_x, self.player.center_y, (245, 60, 75), count=30)
            self.camera.add_shake(12.0, 0.8)
            if hasattr(self, "vfx_manager") and self.vfx_manager:
                self.vfx_manager.spawn("ancient_discovery", self.player.center_x, self.player.center_y - 20, duration=1.2)
            feedback = "Equipped full Ancient Equipment Set! Radiant Pulsing Aura activated!"

        elif cmd == "weapons":
            pack = [
                ("ancient_eternal_shortbow", 1), ("celestial_bow", 1), ("magma_bow", 1), ("wood_bow", 1),
                ("astral_arrow", 100), ("frostburn_arrow", 100), ("flame_arrow", 100), ("wooden_arrow", 100),
                ("eternal_catalyst", 1), ("scorpion_catalyst_of_the_vale", 1),
                ("fire_staff", 1), ("frost_staff", 1), ("celestial_staff", 1),
                ("ancient_forgotten_rod", 1), ("chrono_rod_of_sol_rho", 1),
                ("void_scepter", 1), ("glacial_scepter", 1),
                ("astral_wrath", 1), ("celestial_greatsword", 1)
            ]
            for it_id, it_cnt in pack:
                leftover = self.inventory.add_item(it_id, it_cnt)
                if leftover > 0:
                    self.drop_item_into_world(it_id, leftover)
            self.sound_manager.play("craft")
            feedback = "Received Arsenal Showcase Pack (Notable Ancient, Bow, and Magic Weapons)!"

        elif cmd == "spawn":
            if not args:
                feedback = "Usage: /spawn <mob|boss> [count]"
            else:
                target_name = args[0].lower()
                count = 1
                if len(args) > 1:
                    try:
                        count = max(1, min(20, int(args[1])))
                    except ValueError:
                        count = 1

                if target_name in ("malus", "lord_malus"):
                    self.combat.boss = None
                    self.combat.spawn_boss(self.player.center_x + 100, self.player.center_y, boss_cls="lord_malus")
                    feedback = "Spawned Subterranean Mini-Boss: Lord Malus!"
                elif target_name in ("ignis", "ignis_colossus", "magma_golem"):
                    self.combat.boss = None
                    self.combat.spawn_boss(self.player.center_x + 100, self.player.center_y, boss_cls="ignis_colossus")
                    feedback = "Spawned Subterranean Mini-Boss: Ignis Colossus!"
                elif target_name in ("cryo", "cryo_spud", "glacial_terror"):
                    self.combat.boss = None
                    self.combat.spawn_boss(self.player.center_x + 100, self.player.center_y, boss_cls="cryo_spud")
                    feedback = "Spawned Subterranean Mini-Boss: Cryo-Spud!"
                elif target_name in ("necro", "necro_tuber", "crypt_terror"):
                    self.combat.boss = None
                    self.combat.spawn_boss(self.player.center_x + 100, self.player.center_y, boss_cls="necro_tuber")
                    feedback = "Spawned Subterranean Mini-Boss: Necro-Tuber!"
                elif target_name in ("sol_rho", "solrho", "grand_boss", "titan"):
                    self.combat.boss = None
                    self.combat.spawn_grand_boss(self.player.center_x + 100, self.player.center_y)
                    feedback = "Spawned Grand Boss: Sol-Rho The Celestial Titan!"
                else:
                    from src.entities import mob as mob_module
                    mob_map = {
                        "slime": mob_module.GreenSlime, "green_slime": mob_module.GreenSlime,
                        "purple_slime": mob_module.PurpleSlime, "frost_slime": mob_module.FrostSlime,
                        "sand_slime": mob_module.SandSlime, "corrupt_slime": mob_module.CorruptSlime,
                        "zombie": mob_module.Zombie, "ice_zombie": mob_module.IceZombie,
                        "rock_zombie": mob_module.RockZombie, "mummy": mob_module.Mummy,
                        "demon_eye": mob_module.DemonEye, "eye": mob_module.DemonEye,
                        "skeleton": mob_module.Skeleton, "bat": mob_module.CaveBat,
                        "cave_bat": mob_module.CaveBat, "ice_bat": mob_module.IceBat,
                        "scorpion": mob_module.DesertScorpion, "crawler": mob_module.ShadowCrawler,
                        "shadow_crawler": mob_module.ShadowCrawler, "shield_weaver": mob_module.ShieldWeaver,
                    }
                    mob_cls = mob_map.get(target_name, mob_module.GreenSlime)
                    for _ in range(count):
                        ox = self.player.center_x + random.uniform(-150, 150)
                        oy = self.player.center_y - random.uniform(20, 60)
                        m = mob_cls(ox, oy, self.asset_factory)
                        self.combat.mobs.append(m)
                    feedback = f"Spawned {count}x {mob_cls.__name__} near Spud!"

        elif cmd == "killall":
            cnt = len(self.combat.mobs)
            self.combat.mobs.clear()
            self.combat.enemy_projectiles.clear()
            if self.combat.boss:
                self.combat.boss = None
                cnt += 1
            feedback = f"Purged {cnt} active hostile mobs!"

        elif cmd == "level":
            cnt = 1
            if args:
                try:
                    cnt = max(1, min(50, int(args[0])))
                except ValueError:
                    cnt = 1
            for _ in range(cnt):
                self.player.stats.add_exp(self.player.stats.exp_to_next)
            feedback = f"Spud leveled up to Level {self.player.stats.level}!"

        elif cmd in ("allskills", "skills"):
            for s_id in self.player.skills.all_skills:
                self.player.skills.learn_skill(s_id)
                self.player.skills.skill_levels[s_id] = 5
            self.sound_manager.play("craft")
            feedback = "Learned and maximized all combat skills to Level 5!"

        elif cmd == "clear":
            for idx in range(len(self.inventory.slots)):
                self.inventory.slots[idx] = None
            self.inventory.held_item = None
            feedback = "Cleared inventory and held items."

        elif cmd in ("boost", "opt", "optimize"):
            self.boost_mode = not getattr(self, "boost_mode", True)
            self.profiler.enabled = True
            stats = self.profiler.get_summary_line()
            feedback = f"BOOST PIPELINE: {'ACTIVE (High-FPS Caching)' if self.boost_mode else 'DISABLED'}. {stats}"

        elif cmd in ("profile", "profiler", "perf", "telemetry"):
            self.show_profiler = not getattr(self, "show_profiler", False)
            self.profiler.enabled = True
            feedback = f"Performance Profiler Overlay: {'VISIBLE (F3)' if self.show_profiler else 'HIDDEN'}"

        else:
            from src.ui.inventory import ITEM_REGISTRY, ITEM_ALIASES
            cand_id = ITEM_ALIASES.get(cmd, cmd)
            if cand_id in ITEM_REGISTRY:
                count = 1
                if args:
                    try:
                        count = max(1, min(999, int(args[0])))
                    except ValueError:
                        count = 1
                leftover = self.inventory.add_item(cand_id, count)
                if leftover > 0:
                    self.drop_item_into_world(cand_id, leftover)
                name = ITEM_REGISTRY[cand_id].get("name", cand_id)
                feedback = f"Direct item cheat: Gave {count}x {name} ({cand_id}) to Spud!"
                self.sound_manager.play("craft")
            else:
                feedback = f"Unknown command '/{cmd}'. Type /help for command list."

        if feedback:
            if hasattr(self.hud, "add_chat_message"):
                self.hud.add_chat_message("[SYSTEM]", feedback)
            else:
                if not hasattr(self.hud, "local_chat_history"):
                    self.hud.local_chat_history = []
                self.hud.local_chat_history.append(("[SYSTEM]", feedback))
            if hasattr(self.inventory, "notify"):
                self.inventory.notify(feedback)

    def save_game_world(self):
        """Saves current world progress to saves/<active_world_name>/world.json."""
        try:
            save_world(self.active_world_name, self)
            print(f"[Main] Saved world '{self.active_world_name}' successfully.")
        except Exception as e:
            print(f"[Main] Failed to save world: {e}")

    def drop_item_into_world(self, item_id, count=1, world_pos=None):
        """Drops an item into the world as a physical DroppedItem entity with throw physics."""
        if not item_id or count <= 0:
            return
        item_obj = None
        if hasattr(item_id, "item_id"):
            item_obj = item_id
            count = item_obj.count
            actual_id = item_obj.item_id
        else:
            actual_id = item_id
        if world_pos is not None:
            wx, wy = world_pos
        else:
            facing = 1.0 if self.player.facing_right else -1.0
            wx = self.player.center_x + facing * 20.0
            wy = self.player.center_y - 8.0
        facing = 1.0 if self.player.facing_right else -1.0
        vx = facing * 4.5 + random.uniform(-1.0, 1.0)
        vy = -3.5 + random.uniform(-1.0, 1.0)
        dropped = DroppedItem(actual_id, count, wx, wy, self.asset_factory)
        if item_obj is not None:
            dropped.item_stack = item_obj
        dropped.vx = vx
        dropped.vy = vy
        dropped.pickup_delay = 1.2
        self.combat.dropped_items.append(dropped)
        self.sound_manager.play("place")

    def drop_selected_or_held(self, mouse_pos=None):
        """Drops currently held cursor item, hovered inventory slot, or active hotbar item into world."""
        if self.inventory.is_open:
            if self.inventory.held_item:
                dropped = self.inventory.drop_held_item()
                if dropped:
                    self.drop_item_into_world(dropped[0], dropped[1])
                    return
            if mouse_pos:
                mx, my = mouse_pos
                hovered = self.inventory.get_hovered_slot(mx, my)
                if hovered is not None and self.inventory.slots[hovered]:
                    dropped = self.inventory.drop_item(hovered, 1)
                    if dropped:
                        self.drop_item_into_world(dropped[0], dropped[1])
                        return
        dropped = self.inventory.drop_item(self.inventory.selected_slot, 1)
        if dropped:
            self.drop_item_into_world(dropped[0], dropped[1])

    def start_lan_host(self):
        """Initializes authoritative LAN host server and connects local client."""
        try:
            print("[Main] Starting LAN Host Server...")
            self.server = LANServer(port=25565)
            self.server.start(self.world.seed, host_is_client=True)
            self.client = LANClient()
            self.client.connect("127.0.0.1", 25565, player_name="Spud (Host)")
            self.combat.is_client = False
            self.combat.client = self.client
            if self.game_mode == MODE_LAST_MAN_STANDING:
                spawn_x, spawn_y = self.world.get_biome_spawn(player_idx=1)
                self.player.x = spawn_x
                self.player.y = spawn_y
                self.camera.set_target(self.player.center_x, self.player.center_y, instant=True)
            self.player.inventory = self.inventory
        except Exception as e:
            print(f"[Main] Failed to start LAN Host: {e}")

    def join_lan_game(self, host_ip):
        """Connects to remote LAN host and synchronizes procedural world seed."""
        try:
            print(f"[Main] Connecting to LAN Host at {host_ip}...")
            self.client = LANClient()
            success, host_seed = self.client.connect(host_ip, 25565, player_name="Spud_Guest")
            if success and host_seed is not None:
                print(f"[Main] Connected to host! Generating shared world with seed: {host_seed}")
                self.combat.is_client = True
                self.combat.client = self.client
                self.combat.mobs.clear()
                self.combat.boss = None
                self.world = World(self.asset_factory, seed=host_seed)
                if self.game_mode == MODE_LAST_MAN_STANDING:
                    pid = getattr(self.client, "player_id", 2) or 2
                    spawn_x, spawn_y = self.world.get_biome_spawn(player_idx=pid)
                else:
                    spawn_x, spawn_y = self.world.spawn_point
                self.player.x = spawn_x
                self.player.y = spawn_y
                self.player.vx = 0.0
                self.player.vy = 0.0
                self.player.inventory = self.inventory
                self.camera.set_target(self.player.center_x, self.player.center_y, instant=True)
            else:
                print(f"[Main] Could not connect to {host_ip}. Starting local world.")
        except Exception as e:
            print(f"[Main] Connection error: {e}")

    def run(self):
        """Master game loop."""
        while self.running:
            self.profiler.start_frame()
            with self.profiler.section("present"):
                dt = self.clock.tick(FPS) / 1000.0
                dt = min(dt, 0.05)

            with self.profiler.section("input"):
                self.handle_events()
            
            if self.menu.state == STATE_PLAYING and not self.paused:
                self.update_gameplay(dt)
            else:
                mouse_pos = self.get_mouse_pos()
                self.menu.update(dt, mouse_pos)
                if self.menu.state == STATE_VICTORY:
                    self.bgm.update(dt, scene="victory")
                elif self.menu.state in (STATE_STORY, STATE_CUTSCENE):
                    self.bgm.update(dt, scene="cutscene")
                elif self.menu.state != STATE_PLAYING:
                    self.bgm.update(dt, scene="menu")
                elif self.paused:
                    self.bgm.update_tick(dt)

            self.render()
            self.profiler.end_frame()

        # Clean shutdown
        if self.menu.state == STATE_PLAYING:
            self.save_game_world()
        if hasattr(self.menu, "save_settings"):
            self.menu.save_settings()
        if self.client:
            self.client.disconnect()
        if self.server:
            self.server.stop()
        if hasattr(self, "renderer_manager"):
            self.renderer_manager.cleanup()
        if sys.platform == "win32":
            try:
                import ctypes
                ctypes.windll.winmm.timeEndPeriod(1)
            except Exception:
                pass
        pygame.quit()
        sys.exit()

    def get_mouse_pos(self) -> tuple[int, int]:
        """Translates window mouse coordinates to virtual screen coordinates."""
        raw_pos = pygame.mouse.get_pos()
        if hasattr(self, "renderer_manager"):
            return self.renderer_manager.window_to_virtual_pos(raw_pos)
        return raw_pos

    def toggle_fullscreen(self):
        """Toggles borderless fullscreen display mode across all game states (prevents screenshot / Win+Shift+S blackout)."""
        self.set_fullscreen_mode(not self.fullscreen)

    def set_fullscreen_mode(self, enabled: bool):
        """Explicitly sets fullscreen mode (True = Borderless Fullscreen, False = Windowed)."""
        self.fullscreen = bool(enabled)
        if hasattr(self, "menu") and hasattr(self.menu, "settings"):
            self.menu.settings["fullscreen"] = self.fullscreen
            self.menu._refresh_settings_button_labels()
            self.menu.save_settings()
        if hasattr(self, "renderer_manager"):
            self.renderer_manager.set_fullscreen(self.fullscreen)
            self.renderer = self.renderer_manager.renderer
            self.screen = self.renderer_manager.surface
            self.ui_screen = self.renderer_manager.ui_surface
        elif self.fullscreen:
            os.environ["SDL_VIDEO_WINDOW_POS"] = "0,0"
            try:
                self.screen = pygame.display.set_mode(
                    (SCREEN_WIDTH, SCREEN_HEIGHT),
                    pygame.DOUBLEBUF | pygame.SCALED | pygame.NOFRAME
                )
            except pygame.error:
                try:
                    self.screen = pygame.display.set_mode(
                        (SCREEN_WIDTH, SCREEN_HEIGHT),
                        pygame.NOFRAME | pygame.SCALED
                    )
                except pygame.error:
                    self.screen = pygame.display.set_mode(
                        (SCREEN_WIDTH, SCREEN_HEIGHT),
                        pygame.NOFRAME
                    )
        else:
            os.environ["SDL_VIDEO_WINDOW_POS"] = "centered"
            try:
                self.screen = pygame.display.set_mode(
                    (SCREEN_WIDTH, SCREEN_HEIGHT),
                    pygame.DOUBLEBUF | pygame.SCALED
                )
            except pygame.error:
                self.screen = pygame.display.set_mode(
                    (SCREEN_WIDTH, SCREEN_HEIGHT),
                    pygame.DOUBLEBUF
                )

    def set_resolution(self, res_str: str):
        """Sets display resolution mode (e.g. 1920x1080, 1600x900, 1366x768, 1280x720)."""
        try:
            parts = str(res_str).lower().split("x")
            if len(parts) == 2:
                w, h = int(parts[0]), int(parts[1])
                if hasattr(self, "renderer_manager"):
                    self.renderer_manager.set_display_resolution(w, h, fullscreen=self.fullscreen)
                    self.renderer = self.renderer_manager.renderer
                    self.screen = self.renderer_manager.surface
                    self.ui_screen = self.renderer_manager.ui_surface
                if hasattr(self, "menu") and hasattr(self.menu, "settings"):
                    self.menu.settings["resolution"] = res_str
                    self.menu._refresh_settings_button_labels()
        except Exception as e:
            print(f"[Engine] Failed to apply resolution {res_str}: {e}")

    def _apply_graphics_settings(self):
        """Propagates loaded menu settings into active rendering, camera, particle, combat, and inventory systems."""
        if not hasattr(self, "menu") or not hasattr(self.menu, "settings"):
            return
        settings = self.menu.settings
        if "resolution" in settings:
            self.set_resolution(str(settings["resolution"]))
        if hasattr(self, "camera"):
            self.camera.shake_enabled = settings.get("screen_shake", True)
        req_rend = settings.get("renderer", RENDERER_HARDWARE)
        if hasattr(self, "renderer_manager") and req_rend != self.renderer_manager.requested_type:
            self.set_renderer_mode(req_rend)
        if hasattr(self, "renderer_manager"):
            if hasattr(self.renderer_manager, "set_shaders_enabled"):
                self.renderer_manager.set_shaders_enabled(settings.get("shaders", True))
            if hasattr(self.renderer_manager, "set_bloom_enabled"):
                self.renderer_manager.set_bloom_enabled(settings.get("bloom", True))
            if hasattr(self.renderer_manager, "set_vignette_enabled"):
                self.renderer_manager.set_vignette_enabled(settings.get("vignette", True))
            if hasattr(self.renderer_manager, "set_water_distortion_enabled"):
                self.renderer_manager.set_water_distortion_enabled(settings.get("water_effects", True))
            if hasattr(self.renderer_manager, "set_color_grading_mode"):
                self.renderer_manager.set_color_grading_mode(settings.get("color_grade", "vibrant"))
            if hasattr(self.renderer_manager, "set_lighting_quality"):
                self.renderer_manager.set_lighting_quality(settings.get("lighting_quality", "high"))
            if hasattr(self.renderer_manager, "set_particle_density"):
                self.renderer_manager.set_particle_density(settings.get("particle_density", "high"))

        density_map = {"ultra": 500, "high": 250, "medium": 120, "low": 60}
        if hasattr(self, "particle_system"):
            self.particle_system.max_particles = density_map.get(str(settings.get("particle_density", "high")).lower(), 250)
        self.boost_mode = settings.get("boost_mode", True)
        if hasattr(self, "combat"):
            self.combat.show_damage_numbers = settings.get("damage_numbers", True)
        if hasattr(self, "inventory"):
            self.inventory.tooltip_mode = settings.get("tooltips", "detailed")
        if hasattr(self, "hud"):
            self.hud.tooltip_mode = settings.get("tooltips", "detailed")
        if hasattr(self, "chest_ui"):
            self.chest_ui.tooltip_mode = settings.get("tooltips", "detailed")

        if "fullscreen" in settings and bool(settings.get("fullscreen", False)) != self.fullscreen:
            try:
                self.set_fullscreen_mode(bool(settings["fullscreen"]))
            except Exception:
                pass

    def set_renderer_mode(self, mode: str):
        """Switches the active renderer between hardware (ModernGL) and software via HAL."""
        if hasattr(self, "renderer_manager"):
            self.renderer_manager.switch_renderer(mode, fullscreen=self.fullscreen)
            self.renderer = self.renderer_manager.renderer
            self.screen = self.renderer_manager.surface
            self.ui_screen = self.renderer_manager.ui_surface
            if hasattr(self.menu, "settings"):
                self.menu.settings["renderer"] = self.renderer_manager.requested_type
                self.menu._refresh_settings_button_labels()
                if hasattr(self.menu, "save_settings"):
                    self.menu.save_settings()

    def toggle_renderer_mode(self):
        """Toggles between hardware (ModernGL) and software renderer via HAL."""
        if hasattr(self, "renderer_manager"):
            self.renderer_manager.toggle_renderer(fullscreen=self.fullscreen)
            self.renderer = self.renderer_manager.renderer
            self.screen = self.renderer_manager.surface
            self.ui_screen = self.renderer_manager.ui_surface
            if hasattr(self.menu, "settings"):
                self.menu.settings["renderer"] = self.renderer_manager.requested_type
                self.menu._refresh_settings_button_labels()
                if hasattr(self.menu, "save_settings"):
                    self.menu.save_settings()

    def return_to_main_menu(self):
        """Cleanly leaves active session and returns to Main Menu."""
        if self.client:
            try:
                self.client.disconnect()
            except Exception:
                pass
            self.client = None
        if self.server:
            try:
                self.server.stop()
            except Exception:
                pass
            self.server = None
        if self.bgm:
            self.bgm.stop()
        self.combat.is_client = False
        self.combat.client = None
        self.combat.multiplayer_player_positions = []
        self.combat.boss = None
        self.combat.mobs.clear()
        self.combat.projectiles.clear()
        self.combat.enemy_projectiles.clear()
        self.combat.dropped_items.clear()
        self.combat.damage_numbers.clear()
        self.combat.mini_bosses_slain = 0
        self.combat.boss_defeated = False
        self.combat.grand_boss_defeated = False
        self.block_deltas = {}
        self.wall_deltas = {}
        if hasattr(self, "sky"):
            self.sky.time = 0.0
        self.paused = False
        self.character_panel.is_open = False
        self.inventory.is_open = False
        if hasattr(self, "npc_dialogue"):
            self.npc_dialogue.close()
        if hasattr(self, "touch_controller"):
            self.touch_controller.reset()
        self.menu.state = STATE_MENU

    def reset_new_session(self, world_name, world_type=WORLD_TYPE_INFINITE, difficulty=DIFFICULTY_NORMAL, game_mode=MODE_ADVENTURE, seed=None):
        """Reinitializes all gameplay state freshly when creating or starting a new world."""
        if hasattr(self, "npc_dialogue"):
            self.npc_dialogue.close()
        self.active_world_name = world_name
        self.world_type = world_type
        self.difficulty = difficulty
        self.game_mode = game_mode
        self.world = World(self.asset_factory, seed=seed, world_type=self.world_type)
        self.block_deltas = {}
        self.wall_deltas = {}
        self.playtime = 0.0

        # Clear Equipment & Held Weapon
        for slot_k in list(self.player.equipment.slots.keys()):
            self.player.equipment.slots[slot_k] = None
        self.player.equipment.active_weapon_id = None
        self.player.equipment.recalculate_stats(self.player.stats)

        # Reset Player Stats & Health to starting Level 1
        self.player.stats.level = 1
        self.player.stats.current_exp = 0
        self.player.stats.exp_to_next = 100
        self.player.stats.base_max_hp = 100
        self.player.stats.base_max_mp = 50
        self.player.stats.base_atk = 10
        self.player.stats.base_def = 2
        self.player.stats.base_crit_rate = 5.0
        self.player.stats.bonus_max_hp = 0
        self.player.stats.bonus_max_mp = 0
        self.player.stats.bonus_atk = 0
        self.player.stats.bonus_def = 0
        self.player.stats.bonus_crit = 0.0
        self.player.stats.bonus_speed = 0.0
        self.player.stats.bonus_atk_speed = 0.0
        self.player.stats.bonus_mp_regen = 0.0
        self.player.attack_cooldown = 0.0
        if self.difficulty == DIFFICULTY_YOLO:
            self.player.stats.set_yolo_mode(True)
        else:
            self.player.stats.set_yolo_mode(False)
        self.player.stats.hp = self.player.stats.max_hp
        self.player.stats.mp = self.player.stats.max_mp
        self.player.health = self.player.max_health
        self.player.is_dead = False

        # Reset Skills to starting baseline
        if hasattr(self.player, "skills"):
            starting_skills = {"power_slash", "dash"}
            self.player.skills.learned_skills = set(starting_skills)
            self.player.skills.skill_levels = {s: 1 for s in starting_skills}
            self.player.skills.hotkey_bindings = {"Q": "power_slash", "F": None, "V": "dash", "R": None}
            self.player.skills.hotkey_slots = dict(self.player.skills.hotkey_bindings)

        # Reset Inventory Loadout & Coin Purse (Zero World State Bleed)
        self.player.stats.copper_coins = 0
        self.player.stats.silver_coins = 0
        self.player.stats.gold_coins = 0
        self.player.stats.items_recycled = 0
        self.inventory._local_copper = 0
        self.inventory._local_silver = 0
        self.inventory._local_gold = 0
        self.mining_cooldown = 0.0

        self.inventory.set_difficulty_loadout(self.difficulty)
        self.player.inventory = self.inventory
        self.inventory.player = self.player

        # Reset Combat Engine Entities & Boss Progress
        self.combat.boss = None
        self.combat.mobs.clear()
        self.combat.projectiles.clear()
        self.combat.enemy_projectiles.clear()
        self.combat.dropped_items.clear()
        self.combat.damage_numbers.clear()
        self.combat.mini_bosses_slain = 0
        self.combat.boss_defeated = False
        self.combat.grand_boss_defeated = False
        self.combat.dungeon_boss_slain = False
        self.player.pre_arena_pos = None
        self.player.particle_system = self.particle_system
        self.player.vfx_manager = self.vfx_manager
        if hasattr(self, "vfx_manager") and self.vfx_manager:
            self.vfx_manager.clear()
        self.god_mode = False
        self.speed_multiplier = 1.0
        self.player.speed_multiplier = 1.0

        # Reset Day/Night Cycle to Daybreak
        if hasattr(self, "sky"):
            self.sky.time = 0.0

        # Position player at spawn
        if self.game_mode == MODE_LAST_MAN_STANDING:
            spawn_x, spawn_y = self.world.get_biome_spawn(player_idx=1)
        else:
            spawn_x, spawn_y = self.world.spawn_point
        self.player.spawn_point = (spawn_x, spawn_y)
        self.player.x, self.player.y = spawn_x, spawn_y
        self.player.vx, self.player.vy = 0.0, 0.0
        self.player.is_resting = False
        self.player.resting_bed_pos = None
        self.camera.set_target(self.player.center_x, self.player.center_y, instant=True)


    def _execute_menu_action(self, action):
        if action == "quit":
            self.running = False
        elif action == "host_lan":
            self.start_lan_host()
        elif isinstance(action, tuple) and action[0] == "join_lan":
            self.join_lan_game(action[1])
        elif isinstance(action, tuple) and action[0] == "set_fullscreen":
            self.set_fullscreen_mode(action[1])
        elif action == "toggle_fullscreen":
            self.toggle_fullscreen()
        elif isinstance(action, tuple) and action[0] == "set_renderer":
            self.set_renderer_mode(action[1])
        elif action == "toggle_renderer":
            self.toggle_renderer_mode()
        elif isinstance(action, tuple) and action[0] == "set_shaders":
            if hasattr(self, "renderer_manager") and hasattr(self.renderer_manager, "set_shaders_enabled"):
                self.renderer_manager.set_shaders_enabled(action[1])
        elif action == "toggle_shaders":
            cur_s = self.menu.settings.get("shaders", True)
            self.menu.settings["shaders"] = not cur_s
            if hasattr(self, "renderer_manager") and hasattr(self.renderer_manager, "set_shaders_enabled"):
                self.renderer_manager.set_shaders_enabled(not cur_s)
        elif isinstance(action, tuple) and action[0] == "set_bloom":
            if hasattr(self, "renderer_manager") and hasattr(self.renderer_manager, "set_bloom_enabled"):
                self.renderer_manager.set_bloom_enabled(action[1])
        elif action == "toggle_bloom":
            cur_b = self.menu.settings.get("bloom", True)
            self.menu.settings["bloom"] = not cur_b
            if hasattr(self, "renderer_manager") and hasattr(self.renderer_manager, "set_bloom_enabled"):
                self.renderer_manager.set_bloom_enabled(not cur_b)
        elif isinstance(action, tuple) and action[0] == "set_vignette":
            if hasattr(self, "renderer_manager") and hasattr(self.renderer_manager, "set_vignette_enabled"):
                self.renderer_manager.set_vignette_enabled(action[1])
        elif action == "toggle_vignette":
            cur_v = self.menu.settings.get("vignette", True)
            self.menu.settings["vignette"] = not cur_v
            if hasattr(self, "renderer_manager") and hasattr(self.renderer_manager, "set_vignette_enabled"):
                self.renderer_manager.set_vignette_enabled(not cur_v)
        elif isinstance(action, tuple) and action[0] == "set_resolution":
            self.set_resolution(action[1])
        elif action == "cycle_resolution":
            cur_r = str(self.menu.settings.get("resolution", "1920x1080"))
            res_list = getattr(self.menu, "resolutions", ["1920x1080", "1600x900", "1366x768", "1280x720"])
            idx = res_list.index(cur_r) if cur_r in res_list else 0
            next_r = res_list[(idx + 1) % len(res_list)]
            self.menu.settings["resolution"] = next_r
            self.menu._refresh_settings_button_labels()
            self.menu.save_settings()
            self.set_resolution(next_r)
        elif isinstance(action, tuple) and action[0] == "set_water_effects":
            if hasattr(self, "renderer_manager") and hasattr(self.renderer_manager, "set_water_distortion_enabled"):
                self.renderer_manager.set_water_distortion_enabled(action[1])
        elif action == "toggle_water_effects":
            cur_w = self.menu.settings.get("water_effects", True)
            self.menu.settings["water_effects"] = not cur_w
            if hasattr(self, "renderer_manager") and hasattr(self.renderer_manager, "set_water_distortion_enabled"):
                self.renderer_manager.set_water_distortion_enabled(not cur_w)
        elif isinstance(action, tuple) and action[0] == "set_color_grade":
            if hasattr(self, "renderer_manager") and hasattr(self.renderer_manager, "set_color_grading_mode"):
                self.renderer_manager.set_color_grading_mode(action[1])
        elif isinstance(action, tuple) and action[0] == "set_lighting_quality":
            if hasattr(self, "renderer_manager") and hasattr(self.renderer_manager, "set_lighting_quality"):
                self.renderer_manager.set_lighting_quality(action[1])
        elif isinstance(action, tuple) and action[0] == "set_particle_density":
            if hasattr(self, "renderer_manager") and hasattr(self.renderer_manager, "set_particle_density"):
                self.renderer_manager.set_particle_density(action[1])
            if hasattr(self, "particle_system"):
                density_map = {"ultra": 500, "high": 250, "medium": 120, "low": 60}
                self.particle_system.max_particles = density_map.get(str(action[1]).lower(), 250)
        elif isinstance(action, tuple) and action[0] == "set_shake":
            self.camera.shake_enabled = action[1]
        elif action == "toggle_shake":
            cur_s = self.menu.settings.get("screen_shake", True)
            self.menu.settings["screen_shake"] = not cur_s
            self.camera.shake_enabled = not cur_s
        elif isinstance(action, tuple) and action[0] == "set_boost_mode":
            self.boost_mode = bool(action[1])
        elif action == "toggle_boost_mode":
            self.boost_mode = not getattr(self, "boost_mode", True)
            self.menu.settings["boost_mode"] = self.boost_mode
        elif isinstance(action, tuple) and action[0] == "set_damage_numbers":
            if hasattr(self, "combat"):
                self.combat.show_damage_numbers = bool(action[1])
        elif action == "toggle_damage_numbers":
            cur_d = self.menu.settings.get("damage_numbers", True)
            self.menu.settings["damage_numbers"] = not cur_d
            if hasattr(self, "combat"):
                self.combat.show_damage_numbers = not cur_d
        elif isinstance(action, tuple) and action[0] == "set_tooltips":
            tt_mode = str(action[1])
            if hasattr(self, "inventory"):
                self.inventory.tooltip_mode = tt_mode
            if hasattr(self, "hud"):
                self.hud.tooltip_mode = tt_mode
            if hasattr(self, "chest_ui"):
                self.chest_ui.tooltip_mode = tt_mode
        elif action == "toggle_tooltips":
            cur_t = "compact" if self.menu.settings.get("tooltips", "detailed") == "detailed" else "detailed"
            self.menu.settings["tooltips"] = cur_t
            if hasattr(self, "inventory"):
                self.inventory.tooltip_mode = cur_t
            if hasattr(self, "hud"):
                self.hud.tooltip_mode = cur_t
            if hasattr(self, "chest_ui"):
                self.chest_ui.tooltip_mode = cur_t
        elif isinstance(action, tuple) and action[0] == "set_touch_controls":
            if hasattr(self, "touch_controller"):
                self.touch_controller.set_mode(action[1])
        elif isinstance(action, tuple) and action[0] == "set_touch_opacity":
            if hasattr(self, "touch_controller"):
                self.touch_controller.set_opacity(action[1])
        elif action == "resume_paused":
            self.paused = True
            self.menu.state = STATE_PLAYING
        elif action == "start_singleplayer":
            self.reset_new_session("Quick Play World", WORLD_TYPE_INFINITE, DIFFICULTY_NORMAL, MODE_ADVENTURE)
            self.menu.state = STATE_PLAYING
        elif isinstance(action, tuple) and action[0] == "create_world":
            cfg = action[1]
            w_name = cfg.get("name", "Spud World")
            w_type = cfg.get("world_type", WORLD_TYPE_INFINITE)
            w_diff = cfg.get("difficulty", DIFFICULTY_NORMAL)
            w_mode = cfg.get("game_mode", MODE_ADVENTURE)
            self.reset_new_session(w_name, w_type, w_diff, w_mode)
            self.save_game_world()
            self.menu.state = STATE_PLAYING
        elif isinstance(action, tuple) and action[0] == "load_world":
            w_name = action[1]
            if load_world(w_name, self):
                self.player.inventory = self.inventory
                self.menu.state = STATE_PLAYING
            else:
                self.menu.state = STATE_WORLDS
        elif action == "restart_yolo":
            self.player.is_dead = False
            self.player.stats.set_yolo_mode(True)
            self.player.health = 20
            self.player.x, self.player.y = self.world.spawn_point
            self.player.vx, self.player.vy = 0.0, 0.0
            for slot_k in list(self.player.equipment.slots.keys()):
                self.player.equipment.slots[slot_k] = None
            self.player.equipment.recalculate_stats(self.player.stats)
            self.inventory.set_difficulty_loadout(DIFFICULTY_YOLO)
            self.player.inventory = self.inventory
            self.menu.state = STATE_PLAYING
        elif action == "continue_exploring":
            self.paused = False
        elif action == "return_to_menu":
            self.return_to_main_menu()

    def handle_events(self):
        mouse_pos = self.get_mouse_pos()
        mouse_x, mouse_y = mouse_pos

        if self.paused and self.menu.state == STATE_PLAYING:
            for btn in self.pause_buttons:
                btn.update(mouse_pos)
            for btn in self.save_buttons:
                btn.update(mouse_pos)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                if self.menu.state == STATE_PLAYING:
                    self.save_game_world()
                if hasattr(self.menu, "save_settings"):
                    self.menu.save_settings()
                self.running = False

            elif event.type in (pygame.WINDOWFOCUSLOST, getattr(pygame, "WINDOWMINIMIZED", 0)):
                if hasattr(self, "touch_controller"):
                    self.touch_controller.reset()

            elif event.type in (getattr(pygame, "WINDOWFOCUSGAINED", 0), getattr(pygame, "WINDOWRESTORED", 0), getattr(pygame, "VIDEOEXPOSE", 0)):
                if hasattr(self, "lighting"):
                    self.lighting.dirty = True
                if hasattr(self, "renderer_manager") and hasattr(self.renderer_manager, "active_renderer"):
                    rend = self.renderer_manager.active_renderer
                    if hasattr(rend, "_update_viewport"):
                        try:
                            rend._update_viewport()
                        except Exception:
                            pass

            elif event.type in (pygame.FINGERDOWN, pygame.FINGERMOTION, pygame.FINGERUP):
                px = int(round(event.x * SCREEN_WIDTH))
                py = int(round(event.y * SCREEN_HEIGHT))

                if hasattr(self, "touch_controller"):
                    self.touch_controller.has_touch_input = True

                if event.type == pygame.FINGERDOWN:
                    if hasattr(self, "touch_controller"):
                        self.touch_controller.add_ripple(px, py)

                    # 1. In-Menu Touch Interaction (Main Menu, Worlds, Settings, Achievements, etc.)
                    if self.menu.state != STATE_PLAYING:
                        action = self.menu.handle_click((px, py), button=1)
                        self._execute_menu_action(action)
                        continue

                    # 2. In-Game Virtual Touch Controls
                    handled = False
                    if hasattr(self, "touch_controller"):
                        handled = self.touch_controller.handle_touch_down(event.finger_id, px, py, self)

                    if handled:
                        continue

                    # 3. In-Game Modals / Panels / Pause Touch Handling
                    if self.paused:
                        for btn in self.pause_buttons + getattr(self, "pause_extra_buttons", []):
                            if btn.rect.collidepoint((px, py)):
                                self.sound_manager.play("place")
                                if btn.action == "resume":
                                    self.paused = False
                                elif btn.action == "achievements":
                                    self.menu.previous_state = STATE_PLAYING
                                    self.menu.state = STATE_ACHIEVEMENTS
                                elif btn.action == "settings":
                                    self.menu.open_settings(from_state=STATE_PLAYING)
                                elif btn.action == "main_menu":
                                    self.return_to_main_menu()
                                break
                        for btn in self.save_buttons:
                            if btn.rect.collidepoint((px, py)):
                                self.sound_manager.play("craft")
                                if btn.action == "save":
                                    self.save_game_world()
                                elif btn.action == "save_and_quit":
                                    self.save_game_world()
                                    self.return_to_main_menu()
                                break
                        continue

                    if hasattr(self, "npc_dialogue") and self.npc_dialogue.is_open:
                        if self.npc_dialogue.handle_click(px, py, self.player, self.inventory, self.world, self.combat):
                            continue

                    if hasattr(self, "chest_ui") and self.chest_ui.is_open:
                        if self.chest_ui.handle_click(px, py, False, self.player, self.inventory):
                            continue

                    if self.character_panel.is_open:
                        if self.character_panel.handle_click(px, py, self.player, self.inventory, is_right_click=False):
                            continue

                    if self.inventory.is_open:
                        drop_btn = self.inventory.get_drop_button_rect()
                        recycle_btn = self.inventory.get_recycle_button_rect()
                        organize_btn = self.inventory.get_organize_button_rect() if hasattr(self.inventory, "get_organize_button_rect") else None
                        if drop_btn.collidepoint((px, py)):
                            self.drop_selected_or_held(mouse_pos=(px, py))
                        elif recycle_btn.collidepoint((px, py)):
                            recycled = self.inventory.recycle_selected_or_held()
                            if recycled:
                                self.sound_manager.play("dig_dirt")
                                self.particle_system.spawn_debris(px, py, (180, 50, 50), count=10)
                                self.achievement_manager.unlock("clean_freak")
                        elif organize_btn and organize_btn.collidepoint((px, py)):
                            self.inventory.organize_inventory()
                            self.sound_manager.play("craft")
                        elif self.crafting.handle_click(px, py, self.inventory):
                            self.crafting.update_recipes(self.inventory, self.world, self.player)
                            self.achievement_manager.unlock("master_crafter")
                            if getattr(self.crafting, "last_crafted_item", None) == "iron_bar":
                                self.achievement_manager.unlock("iron_age")
                            self.crafting.last_crafted_item = None
                        elif self.inventory.handle_click(px, py, is_right_click=False, player=self.player):
                            self.crafting.update_recipes(self.inventory, self.world, self.player)
                        elif self.inventory.held_item:
                            inv_panel = pygame.Rect(16, 16, 448, 214)
                            craft_panel = self.crafting.get_panel_rect()
                            if not inv_panel.collidepoint((px, py)) and not craft_panel.collidepoint((px, py)):
                                mouse_wx, mouse_wy = self.camera.screen_to_world(px, py)
                                dropped = self.inventory.drop_held_item()
                                if dropped:
                                    self.drop_item_into_world(dropped[0], dropped[1], world_pos=(mouse_wx, mouse_wy))
                        continue

                elif event.type == pygame.FINGERMOTION:
                    if hasattr(self, "touch_controller"):
                        self.touch_controller.handle_touch_motion(event.finger_id, px, py, self)
                    continue

                elif event.type == pygame.FINGERUP:
                    if hasattr(self, "touch_controller"):
                        self.touch_controller.handle_touch_up(event.finger_id, px, py, self)
                    continue

            elif event.type == pygame.KEYDOWN:
                # F11: Fullscreen Toggle (Works in all game states!)
                if event.key == pygame.K_F11:
                    self.toggle_fullscreen()
                    continue

                # In-Menu Keyboard Input (Story, Controls, Multiplayer IP typing, World Name)
                if self.menu.state != STATE_PLAYING:
                    if self.menu.handle_key(event):
                        continue
                    if event.key == pygame.K_ESCAPE and self.menu.state != STATE_MENU:
                        if self.menu.previous_state == STATE_PLAYING:
                            self.menu.state = STATE_PLAYING
                            self.paused = True
                        else:
                            self.menu.state = STATE_MENU
                    continue

                # In-Game Chat / Cheat Console Typing
                if self.hud.chat_active:
                    if event.key == pygame.K_RETURN:
                        msg = self.hud.chat_input_text.strip()
                        if msg:
                            if msg.startswith("/"):
                                self.execute_cheat(msg)
                            elif self.client and self.client.connected:
                                self.client.send_chat("Spud", msg)
                            else:
                                if hasattr(self.hud, "add_chat_message"):
                                    self.hud.add_chat_message("Spud", msg)
                                else:
                                    if not hasattr(self.hud, "local_chat_history"):
                                        self.hud.local_chat_history = []
                                    self.hud.local_chat_history.append(("Spud", msg))
                        self.hud.chat_input_text = ""
                        self.hud.chat_active = False
                    elif event.key == pygame.K_ESCAPE:
                        self.hud.chat_active = False
                        self.hud.chat_input_text = ""
                    elif event.key == pygame.K_BACKSPACE:
                        self.hud.chat_input_text = self.hud.chat_input_text[:-1]
                    elif event.unicode and len(self.hud.chat_input_text) < 80:
                        self.hud.chat_input_text += event.unicode
                    continue

                # Open Chat / Cheat Console with Enter, Slash (/), or Backquote/Tilde (~)
                if event.key in (pygame.K_RETURN, pygame.K_SLASH, pygame.K_BACKQUOTE):
                    self.hud.chat_active = True
                    if event.key in (pygame.K_SLASH, pygame.K_BACKQUOTE):
                        self.hud.chat_input_text = "/"
                    else:
                        self.hud.chat_input_text = ""
                    continue

                # G Key or Backspace Key: Drop selected item from hotbar, held item, or hovered slot
                if event.key in (pygame.K_g, pygame.K_BACKSPACE):
                    self.drop_selected_or_held(mouse_pos=self.get_mouse_pos())
                    continue

                # Q Key: Drop hovered item when inventory is open (otherwise Skill Q when closed)
                if event.key == pygame.K_q and self.inventory.is_open:
                    self.drop_selected_or_held(mouse_pos=self.get_mouse_pos())
                    continue

                # In-Game Configurable Hotkeys
                k_map = self.menu.key_bindings.get("Toggle Mini-Map", pygame.K_m)
                k_char = self.menu.key_bindings.get("Character Status", pygame.K_c)
                k_inv = self.menu.key_bindings.get("Inventory", pygame.K_e)
                k_sq = self.menu.key_bindings.get("Skill Q", pygame.K_q)
                k_sf = self.menu.key_bindings.get("Skill F", pygame.K_f)
                k_sv = self.menu.key_bindings.get("Skill V", pygame.K_v)
                k_sr = self.menu.key_bindings.get("Skill R", pygame.K_r)

                if event.key == pygame.K_ESCAPE:
                    if hasattr(self, "chest_ui") and self.chest_ui.is_open:
                        self.chest_ui.close()
                    elif hasattr(self, "npc_dialogue") and self.npc_dialogue.is_open:
                        self.npc_dialogue.close()
                    elif self.character_panel.is_open:
                        self.character_panel.is_open = False
                    elif self.inventory.is_open:
                        self.inventory.is_open = False
                    else:
                        self.paused = not self.paused

                elif event.key == k_map:
                    self.hud.minimap.toggle()

                elif event.key == k_char:
                    self.character_panel.toggle()

                elif event.key == k_inv:
                    if hasattr(self, "chest_ui") and self.chest_ui.is_open:
                        self.chest_ui.close()
                    # Check if Spud is interacting with a nearby Town NPC
                    nearby_npc = None
                    if not self.inventory.is_open and not (hasattr(self, "npc_dialogue") and self.npc_dialogue.is_open):
                        for npc in getattr(self.world, "town_npcs", []):
                            if npc.can_interact(self.player):
                                nearby_npc = npc
                                break
                    if nearby_npc and hasattr(self, "npc_dialogue"):
                        self.npc_dialogue.open(nearby_npc, self.player, self.world, self.combat)
                    elif hasattr(self, "npc_dialogue") and self.npc_dialogue.is_open:
                        self.npc_dialogue.close()
                    else:
                        self.inventory.is_open = not self.inventory.is_open
                        if self.inventory.is_open:
                            self.crafting.update_recipes(self.inventory, self.world, self.player)

                # Quick skill assignment in Character Panel when open
                elif self.character_panel.is_open and self.character_panel.handle_key(event, self.player, self.menu.key_bindings):
                    pass

                # Combat Skills (Skill Q, Skill F, Skill V, Skill R)
                elif event.key in (k_sq, k_sf, k_sv, k_sr):
                    if event.key == k_sq:
                        self.player.cast_skill_hotkey("Q", self.particle_system, self.camera)
                    elif event.key == k_sf:
                        self.player.cast_skill_hotkey("F", self.particle_system, self.camera)
                    elif event.key == k_sv:
                        self.player.cast_skill_hotkey("V", self.particle_system, self.camera)
                    elif event.key == k_sr:
                        self.player.cast_skill_hotkey("R", self.particle_system, self.camera)

                elif event.key == pygame.K_F1:
                    self.show_debug = not self.show_debug

                elif event.key == pygame.K_F3:
                    self.show_profiler = not getattr(self, "show_profiler", False)
                    self.profiler.enabled = True

                elif event.key == pygame.K_t:
                    self.sky.time += self.sky.cycle_duration * 0.125

                elif event.key == pygame.K_p:
                    self.paused = not self.paused

                # Hotbar 1-9, 0
                elif pygame.K_1 <= event.key <= pygame.K_9:
                    self.inventory.selected_slot = event.key - pygame.K_1
                elif event.key == pygame.K_0:
                    self.inventory.selected_slot = 9

            elif event.type == pygame.MOUSEWHEEL:
                if self.menu.state == STATE_PLAYING and not self.paused:
                    mouse_pos = self.get_mouse_pos()
                    if self.inventory.is_open and self.crafting.get_panel_rect().collidepoint(mouse_pos):
                        self.crafting.handle_scroll(event.y)
                    else:
                        self.inventory.selected_slot = (self.inventory.selected_slot - event.y) % 10
                elif self.menu.state == STATE_ACHIEVEMENTS:
                    self.menu.handle_scroll(event.y)

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if hasattr(self, "renderer_manager"):
                    mouse_pos = self.renderer_manager.window_to_virtual_pos(event.pos)
                else:
                    mouse_pos = event.pos
                mouse_x, mouse_y = mouse_pos
                is_right_click = (event.button == 3)
                is_left_click = (event.button == 1)

                # 0. Town NPC Dialogue & Shop Window interaction (takes highest priority during gameplay)
                if self.menu.state == STATE_PLAYING and hasattr(self, "npc_dialogue") and self.npc_dialogue.is_open:
                    if is_left_click:
                        handled = self.npc_dialogue.handle_click(mouse_x, mouse_y, self.player, self.inventory, self.world, self.combat)
                        if handled:
                            continue

                # Menu interaction (Main Menu, Worlds, New World, Multiplayer, Settings, Story, Controls, Victory, Game Over)
                if self.menu.state != STATE_PLAYING:
                    action = self.menu.handle_click(mouse_pos, button=event.button)
                    self._execute_menu_action(action)
                    continue

                # Pause Menu Interaction
                if self.paused:
                    if is_left_click:
                        for btn in self.pause_buttons + getattr(self, "pause_extra_buttons", []):
                            if btn.rect.collidepoint(mouse_pos):
                                self.sound_manager.play("place")
                                if btn.action == "resume":
                                    self.paused = False
                                elif btn.action == "achievements":
                                    self.menu.previous_state = STATE_PLAYING
                                    self.menu.state = STATE_ACHIEVEMENTS
                                elif btn.action == "settings":
                                    self.menu.open_settings(from_state=STATE_PLAYING)
                                elif btn.action == "main_menu":
                                    self.return_to_main_menu()
                                break
                        for btn in self.save_buttons:
                            if btn.rect.collidepoint(mouse_pos):
                                self.sound_manager.play("craft")
                                if btn.action == "save":
                                    self.save_game_world()
                                elif btn.action == "save_and_quit":
                                    self.save_game_world()
                                    self.return_to_main_menu()
                                break
                    continue

                # Gameplay UI interaction
                ui_consumed = False

                # Mobile Virtual Controls interaction (Top Bar & Virtual Controls)
                if hasattr(self, "touch_controller") and self.touch_controller.is_visible() and is_left_click:
                    if self.touch_controller.handle_mouse_down(mouse_x, mouse_y, event.button, self):
                        ui_consumed = True
                        continue

                # 0.4. Fishing Battle Mini-Game
                if hasattr(self, "fishing_minigame") and self.fishing_minigame.is_active:
                    self.fishing_minigame.handle_click(is_right_click=is_right_click)
                    ui_consumed = True

                # 0.5. Storage Chest Window
                if hasattr(self, "chest_ui") and self.chest_ui.is_open:
                    if self.chest_ui.handle_click(mouse_x, mouse_y, is_right_click, self.player, self.inventory):
                        ui_consumed = True

                # 1. Character & Equipment Paperdoll Panel
                if not ui_consumed and self.character_panel.is_open:
                    if self.character_panel.handle_click(mouse_x, mouse_y, self.player, self.inventory, is_right_click=is_right_click):
                        ui_consumed = True

                # 2. Crafting & Inventory
                if not ui_consumed and self.inventory.is_open:
                    drop_btn = self.inventory.get_drop_button_rect()
                    recycle_btn = self.inventory.get_recycle_button_rect()
                    organize_btn = self.inventory.get_organize_button_rect() if hasattr(self.inventory, "get_organize_button_rect") else None
                    if is_left_click and drop_btn.collidepoint(mouse_x, mouse_y):
                        self.drop_selected_or_held(mouse_pos=(mouse_x, mouse_y))
                        ui_consumed = True
                    elif is_left_click and recycle_btn.collidepoint(mouse_x, mouse_y):
                        recycled = self.inventory.recycle_selected_or_held()
                        if recycled:
                            self.sound_manager.play("dig_dirt")
                            self.particle_system.spawn_debris(mouse_x, mouse_y, (180, 50, 50), count=10)
                            self.achievement_manager.unlock("clean_freak")
                            count = recycled[1] if isinstance(recycled, tuple) else 1
                            if not hasattr(self.player.stats, "items_recycled"):
                                self.player.stats.items_recycled = 0
                            self.player.stats.items_recycled += count
                            total_rec = self.player.stats.items_recycled
                            if total_rec >= 10:
                                self.achievement_manager.unlock("recycle_master_1")
                            if total_rec >= 50:
                                self.achievement_manager.unlock("recycle_master_2")
                            if total_rec >= 100:
                                self.achievement_manager.unlock("recycle_master_3")
                        ui_consumed = True
                    elif is_left_click and organize_btn and organize_btn.collidepoint(mouse_x, mouse_y):
                        self.inventory.organize_inventory()
                        self.sound_manager.play("craft")
                        ui_consumed = True
                    elif self.crafting.handle_click(mouse_x, mouse_y, self.inventory):
                        self.crafting.update_recipes(self.inventory, self.world, self.player)
                        self.achievement_manager.unlock("master_crafter")
                        if getattr(self.crafting, "last_crafted_item", None) == "iron_bar":
                            self.achievement_manager.unlock("iron_age")
                        self.crafting.last_crafted_item = None
                        ui_consumed = True
                    elif self.inventory.handle_click(mouse_x, mouse_y, is_right_click, player=self.player):
                        self.crafting.update_recipes(self.inventory, self.world, self.player)
                        ui_consumed = True
                    elif self.inventory.held_item:
                        # Click was outside inventory & crafting panels while holding an item -> Drop into world!
                        inv_panel = pygame.Rect(16, 16, 448, 214)
                        craft_panel = self.crafting.get_panel_rect()
                        if not inv_panel.collidepoint(mouse_x, mouse_y) and not craft_panel.collidepoint(mouse_x, mouse_y):
                            mouse_wx, mouse_wy = self.camera.screen_to_world(mouse_x, mouse_y)
                            dropped = self.inventory.drop_held_item()
                            if dropped:
                                self.drop_item_into_world(dropped[0], dropped[1], world_pos=(mouse_wx, mouse_wy))
                                ui_consumed = True
                elif not ui_consumed:
                    if self.inventory.handle_click(mouse_x, mouse_y, is_right_click, player=self.player):
                        ui_consumed = True

                # Gameplay World interaction
                if not ui_consumed and not self.paused:
                    mouse_wx, mouse_wy = self.camera.screen_to_world(mouse_x, mouse_y)
                    clicked_npc = self.world.get_npc_at(mouse_wx, mouse_wy, radius=48.0) if hasattr(self.world, "get_npc_at") else None
                    if clicked_npc and clicked_npc.can_interact(self.player):
                        self.npc_dialogue.open(clicked_npc, self.player, self.world, self.combat)
                        ui_consumed = True
                    elif is_right_click:
                        self.handle_right_click(mouse_x, mouse_y)
                    elif is_left_click:
                        self.mining_cooldown = self.continuous_mine_rate
                        self.handle_primary_action(mouse_x, mouse_y)

            elif event.type == pygame.MOUSEMOTION:
                if self.menu.state == STATE_PLAYING and hasattr(self, "touch_controller") and self.touch_controller.is_visible():
                    vpos = self.renderer_manager.window_to_virtual_pos(event.pos) if hasattr(self, "renderer_manager") else event.pos
                    self.touch_controller.handle_mouse_motion(vpos[0], vpos[1], self)

            elif event.type == pygame.MOUSEBUTTONUP:
                if self.menu.state == STATE_PLAYING and hasattr(self, "touch_controller") and self.touch_controller.is_visible():
                    vpos = self.renderer_manager.window_to_virtual_pos(event.pos) if hasattr(self, "renderer_manager") else event.pos
                    self.touch_controller.handle_mouse_up(vpos[0], vpos[1], event.button, self)

    def _open_or_break_chest(self, tx, ty, world_x, world_y):
        """Rolls high-value loot for naturally discovered or drops stored items from placed chests."""
        cur_t = self.world.get_tile(tx, ty) if hasattr(self.world, "get_tile") else TILE_CHEST
        is_player = (tx, ty) in getattr(self.world, "player_placed_tiles", set()) or getattr(self.world, "last_broken_tile_is_player_placed", False)
        chest = None
        if hasattr(self.world, "chests") and (tx, ty) in self.world.chests:
            chest = self.world.chests.pop((tx, ty))
        elif hasattr(self.world, "last_broken_chest") and self.world.last_broken_chest:
            chest = self.world.last_broken_chest
            self.world.last_broken_chest = None
        if chest:
            if getattr(chest, "is_player_placed", False):
                is_player = True
            self.world.set_tile(tx, ty, TILE_AIR)
            self.block_deltas[(tx, ty)] = TILE_AIR
            if self.client and self.client.connected:
                self.client.send_block_delta(tx, ty, TILE_AIR)
            if hasattr(self, "chest_ui") and self.chest_ui.active_chest == chest:
                self.chest_ui.close()
            self.sound_manager.play("craft")
            self.particle_system.spawn_debris(world_x + 16, world_y + 16, (180, 130, 70), count=10)
            # Drop all items stored in chest
            for itm in chest.get_all_items():
                self.combat.dropped_items.append(
                    DroppedItem(itm.item_id, itm.count, world_x + random.randint(4, 12), world_y - random.randint(4, 16), self.asset_factory)
                )
            # Drop the chest container itself
            drop_chest_id = chest.chest_type if getattr(chest, "chest_type", None) in ("iron_chest", "chest") else ("iron_chest" if cur_t == TILE_IRON_CHEST else "chest")
            self.combat.dropped_items.append(DroppedItem(drop_chest_id, 1, world_x + 8, world_y - 8, self.asset_factory))
            return

        chest_drop = "iron_chest" if cur_t == TILE_IRON_CHEST else "chest"
        self.world.set_tile(tx, ty, TILE_AIR)
        self.block_deltas[(tx, ty)] = TILE_AIR
        if self.client and self.client.connected:
            self.client.send_block_delta(tx, ty, TILE_AIR)

        if is_player:
            # Player-placed chest with no storage record: drops ONLY the chest container itself, NEVER dungeon loot
            self.sound_manager.play("craft")
            self.particle_system.spawn_debris(world_x + 16, world_y + 16, (180, 130, 70), count=10)
            self.combat.dropped_items.append(DroppedItem(chest_drop, 1, world_x + 8, world_y - 8, self.asset_factory))
            return

        self.sound_manager.play("craft")
        self.particle_system.spawn_sparks(world_x + 16, world_y + 16, (255, 215, 0), count=30)
        self.particle_system.spawn_debris(world_x + 16, world_y + 16, (180, 130, 70), count=10)

        # 1. Guaranteed Chest Item + Bars + Potions
        self.combat.dropped_items.append(DroppedItem(chest_drop, 1, world_x + 4, world_y - 10, self.asset_factory))
        self.combat.dropped_items.append(DroppedItem(random.choice(["gold_bar", "iron_bar"]), random.randint(3, 7), world_x + 8, world_y - 8, self.asset_factory))
        self.combat.dropped_items.append(DroppedItem(random.choice(["greater_healing_potion", "healing_potion", "speed_potion"]), random.randint(2, 4), world_x + 12, world_y - 8, self.asset_factory))

        # 2. Rare Gear Roll (Accessories / Weapons / Books / Catalog)
        rare_chest_items = [
            "zephyr_striders", "talisman_of_vigor", "lucky_clover", "guardian_ring", "warrior_charm",
            "frost_blade", "shadow_cleaver", "sandstorm_spear", "golden_fry",
            "skillbook_whirlwind", "skillbook_fireball", "skillbook_dash"
        ]
        if hasattr(self.combat, "_catalog_rarity_pools") and self.combat._catalog_rarity_pools.get("rare") and random.random() < 0.4:
            self.combat.dropped_items.append(DroppedItem(random.choice(self.combat._catalog_rarity_pools["rare"]), 1, world_x + 8, world_y - 12, self.asset_factory))
        else:
            self.combat.dropped_items.append(DroppedItem(random.choice(rare_chest_items), 1, world_x + 8, world_y - 12, self.asset_factory))

        # 2.2. Epic Gear Roll in Chests (15% chance to find Epic Catalog Gear!)
        if hasattr(self.combat, "_catalog_rarity_pools") and self.combat._catalog_rarity_pools.get("epic") and random.random() < 0.15:
            epic_drop = random.choice(self.combat._catalog_rarity_pools["epic"])
            print(f"[CHEST] EPIC DISCOVERY! {epic_drop} found in Treasure Chest!")
            self.combat.dropped_items.append(DroppedItem(epic_drop, 1, world_x + 12, world_y - 14, self.asset_factory))
            self.particle_system.spawn_sparks(world_x + 16, world_y + 16, (180, 80, 255), count=25)

        # 2.3. Mythic Relic Roll in Chests (3% chance to find Mythic Relic!)
        if hasattr(self.combat, "_catalog_rarity_pools") and self.combat._catalog_rarity_pools.get("mythic") and random.random() < 0.03:
            mythic_drop = random.choice(self.combat._catalog_rarity_pools["mythic"])
            print(f"[CHEST] MYTHIC DISCOVERY! {mythic_drop} found in Treasure Chest!")
            self.combat.dropped_items.append(DroppedItem(mythic_drop, 1, world_x + 14, world_y - 16, self.asset_factory))
            self.particle_system.spawn_sparks(world_x + 16, world_y + 16, (255, 152, 0), count=35)
            self.camera.add_shake(4.0, 0.25)

        # 2.5. Celestial Portal Shard in Chests (35% chance to find portal shards!)
        if random.random() < 0.35:
            print("[CHEST] MYSTICAL DISCOVERY! Celestial Portal Shard found in Treasure Chest!")
            self.combat.dropped_items.append(DroppedItem("portal_shard", 1, world_x + 10, world_y - 14, self.asset_factory))
            self.particle_system.spawn_sparks(world_x + 16, world_y + 16, (80, 220, 255), count=25)

        # 3. Rare Chest Legendary Roll: 5% chance of Astral Wrath / Legendary Catalog Item!
        if random.random() < 0.05:
            print("[CHEST] LEGENDARY DISCOVERY! Astral Wrath found in Treasure Chest!")
            self.combat.dropped_items.append(DroppedItem("astral_wrath", 1, world_x + 8, world_y - 18, self.asset_factory))
            self.particle_system.spawn_sparks(world_x + 16, world_y + 16, (255, 230, 80), count=50)
            self.camera.add_shake(5.0, 0.3)

    def handle_right_click(self, mouse_x, mouse_y):
        """Handles fishing, eating food, drinking potions, toggling doors, placing walls, opening chests, or placing blocks."""
        # 0. Active Fishing Battle Mini-Game takes top input priority
        if hasattr(self, "fishing_minigame") and self.fishing_minigame and self.fishing_minigame.is_active:
            self.fishing_minigame.handle_click(is_right_click=True)
            return

        # 0a. Fishing Rod Cast / Reel with Right-Click
        active = self.inventory.get_active_item()
        if active and active.item_id == "fishing_rod":
            return self.handle_fishing_action(mouse_x, mouse_y)
        if getattr(self, "fishing_bobber", None) is not None:
            return self.handle_fishing_action(mouse_x, mouse_y)

        tx, ty = self.camera.screen_to_tile(mouse_x, mouse_y)
        tile_world_x = tx * SCALED_TILE
        tile_world_y = ty * SCALED_TILE
        reach = math.hypot(self.player.center_x - (tile_world_x + SCALED_TILE / 2),
                           self.player.center_y - (tile_world_y + SCALED_TILE / 2))

        # 0. World Interactivity within reach (Chest or Wooden Door)
        if reach <= SCALED_TILE * 5.5:
            # 0a. Toggle Wooden Door
            t_id = self.world.get_tile(tx, ty)
            if t_id in (TILE_DOOR_CLOSED, TILE_DOOR_OPEN):
                if self.world.toggle_door(tx, ty, player_rect=self.player.rect):
                    self.sound_manager.play("place")
                    if self.client and self.client.connected:
                        new_tid = self.world.get_tile(tx, ty)
                        self.client.send_block_delta(tx, ty, new_tid)
                    if self.world.check_shelter(tx, ty):
                        self.achievement_manager.unlock("home_sweet_home")
                    return

            # 0b. Open / Break Treasure Chest or Iron Chest
            if t_id in (TILE_CHEST, TILE_IRON_CHEST):
                if hasattr(self.world, "chests") and (tx, ty) in self.world.chests:
                    self.chest_ui.open(self.world.chests[(tx, ty)], self.player, self.inventory)
                    return
                self._open_or_break_chest(tx, ty, tile_world_x, tile_world_y)
                return

            # 0c. Dungeon Altar (Summon / Awaken Biome Boss)
            if t_id == TILE_DUNGEON_ALTAR:
                if not self.combat.boss:
                    if ty <= -150 and abs(tx) <= 25 and all(self.combat.defeated_mini_bosses.values()):
                        self.combat.spawn_grand_boss(tile_world_x, tile_world_y, player=self.player)
                    elif abs(tx - 80) <= 20:
                        self.combat.spawn_boss(tile_world_x, tile_world_y, boss_cls="ignis_colossus", player=self.player)
                    elif abs(tx - (-80)) <= 20:
                        self.combat.spawn_boss(tile_world_x, tile_world_y, boss_cls="cryo_spud", player=self.player)
                    elif abs(tx - 140) <= 20:
                        self.combat.spawn_boss(tile_world_x, tile_world_y, boss_cls="necro_tuber", player=self.player)
                    else:
                        dung_x, dung_y = getattr(self.world, "dungeon_spawn", (tile_world_x, tile_world_y))
                        self.combat.spawn_boss(dung_x, dung_y, boss_cls="lord_malus", player=self.player)
                    self.sound_manager.play("craft")
                    self.particle_system.spawn_sparks(tile_world_x + 16, tile_world_y + 16, (140, 50, 200), count=40)
                    self.camera.add_shake(8.0, 0.5)
                return

            # 0d. Wooden Bed: Set Respawn Point & Sleep / Rest Healing
            if t_id == TILE_BED:
                bed_spawn_x = tile_world_x
                bed_spawn_y = tile_world_y - SCALED_TILE
                self.player.spawn_point = (bed_spawn_x, bed_spawn_y)
                self.world.spawn_point = (bed_spawn_x, bed_spawn_y)

                # If already resting, toggle wake up
                if getattr(self.player, "is_resting", False):
                    self.player.is_resting = False
                    self.player.resting_bed_pos = None
                    self.inventory.notify("Woke up from bed.")
                    return

                # Check daytime / nighttime restriction
                if not getattr(self.sky, "is_night", False):
                    self.inventory.notify("You can only sleep at night")
                    return

                # Check monsters within 6 blocks radius (6 * SCALED_TILE)
                radius = 6 * SCALED_TILE
                nearby_enemy = False
                bed_center_x = tile_world_x + SCALED_TILE / 2
                bed_center_y = tile_world_y + SCALED_TILE / 2

                for mob in getattr(self.combat, "mobs", []):
                    if getattr(mob, "is_alive", True) and not getattr(mob, "is_dead", False) and getattr(mob, "hp", 1) > 0:
                        dist_player = math.hypot(mob.center_x - self.player.center_x, mob.center_y - self.player.center_y)
                        dist_bed = math.hypot(mob.center_x - bed_center_x, mob.center_y - bed_center_y)
                        if dist_player <= radius or dist_bed <= radius:
                            nearby_enemy = True
                            break

                if not nearby_enemy and getattr(self.combat, "boss", None):
                    boss = self.combat.boss
                    if getattr(boss, "is_alive", True) and not getattr(boss, "is_dead", False) and getattr(boss, "hp", 1) > 0:
                        dist_player = math.hypot(boss.center_x - self.player.center_x, boss.center_y - self.player.center_y)
                        dist_bed = math.hypot(boss.center_x - bed_center_x, boss.center_y - bed_center_y)
                        if dist_player <= radius or dist_bed <= radius:
                            nearby_enemy = True

                if nearby_enemy:
                    self.inventory.notify("You cannot sleep now, monsters are nearby within 6 blocks!")
                    return

                self.player.is_resting = True
                self.player.resting_bed_pos = (tx, ty)
                self.sound_manager.play("place")
                self.particle_system.spawn_sparks(tile_world_x + 16, tile_world_y + 8, (120, 200, 255), count=25)
                self.inventory.notify("Spawn point set! Resting in bed... (+HP)")
                return

            # 0e. Grandfather Clock: Display Time
            if t_id == TILE_GRANDFATHER_CLOCK:
                time_str = self.sky.get_time_string()
                self.sound_manager.play("craft")
                self.particle_system.spawn_sparks(tile_world_x + 16, tile_world_y + 16, (255, 215, 0), count=20)
                self.inventory.notify(f"Grandfather Clock: {time_str}")
                return

        active = self.inventory.get_active_item()
        if not active:
            return

        cat = active.data.get("cat")

        # 1. Consumable Food or Potions
        if cat == CAT_CONSUMABLE:
            consumed = self.player.consume_item(active.item_id)
            if consumed:
                active.count -= 1
                if active.count <= 0:
                    self.inventory.slots[self.inventory.selected_slot] = None
                return

        # 1.5. Skill Book Consumption from Hotbar!
        if cat == "skillbook":
            s_to_learn = active.data.get("skill")
            if s_to_learn:
                already_learned = s_to_learn in self.player.skills.learned_skills
                success = self.player.skills.learn_skill(s_to_learn)
                if success:
                    lvl = self.player.skills.get_skill_level(s_to_learn) if hasattr(self.player.skills, "get_skill_level") else 1
                    s_name = self.player.skills.all_skills.get(s_to_learn, {}).get("name", s_to_learn)
                    if already_learned:
                        self.inventory.last_learned_message = f"Upgraded {s_name} to Lv. {lvl}! Damage, radius and speed increased!"
                    else:
                        self.inventory.last_learned_message = f"Learned {s_name} Lv. 1! Open Character Status [C] to view & assign to hotkeys (Q, F, V, R)."
                    self.inventory.last_learned_timer = 6.0
                    self.sound_manager.play("craft")
                    self.particle_system.spawn_sparks(self.player.center_x, self.player.center_y, (100, 220, 255), count=35)
                    self.character_panel.is_open = True
                    self.character_panel.hovered_skill_id = s_to_learn
                    active.count -= 1
                    if active.count <= 0:
                        self.inventory.slots[self.inventory.selected_slot] = None
                    return
                else:
                    self.inventory.last_learned_message = f"{s_to_learn.replace('_', ' ').title()} is already at MAX Level (Lv. 5)!"
                    self.inventory.last_learned_timer = 3.0
                    return

        # 2. BIOME ALTAR & DUNGEON TELEPORTER RUNES!
        if active.item_id == "dungeon_rune":
            self.teleport_to_dungeon()
            active.count -= 1
            if active.count <= 0:
                self.inventory.slots[self.inventory.selected_slot] = None
            return

        if active.item_id == "desert_rune":
            print("[Teleport] Spud uses the Sun Altar Rune to warp to the Arid Waste Arena!")
            self.player.pre_arena_pos = (self.player.x, self.player.y)
            dung_x, dung_y = getattr(self.world, "desert_arena_spawn", (2000, 100))
            if hasattr(self.world, "chunk_manager"):
                tcx = int(dung_x // (CHUNK_WIDTH * SCALED_TILE))
                self.world.chunk_manager.ensure_chunks_in_range(tcx - 2, tcx + 2)
            self.combat.mobs.clear()
            self.player.x = dung_x
            self.player.y = dung_y
            self.player.vx = 0.0
            self.player.vy = 0.0
            self.camera.set_target(self.player.center_x, self.player.center_y, instant=True)
            self.sound_manager.play("craft")
            self.particle_system.spawn_sparks(self.player.center_x, self.player.center_y, (255, 180, 50), count=35)
            self.combat.spawn_boss(dung_x, dung_y, boss_cls="ignis_colossus")
            active.count -= 1
            if active.count <= 0:
                self.inventory.slots[self.inventory.selected_slot] = None
            return

        if active.item_id == "cryo_rune":
            print("[Teleport] Spud uses the Glacial Altar Rune to warp to the Glacial Permafrost Arena!")
            self.player.pre_arena_pos = (self.player.x, self.player.y)
            dung_x, dung_y = getattr(self.world, "cryo_arena_spawn", (-2000, 100))
            if hasattr(self.world, "chunk_manager"):
                tcx = int(dung_x // (CHUNK_WIDTH * SCALED_TILE))
                self.world.chunk_manager.ensure_chunks_in_range(tcx - 2, tcx + 2)
            self.combat.mobs.clear()
            self.player.x = dung_x
            self.player.y = dung_y
            self.player.vx = 0.0
            self.player.vy = 0.0
            self.camera.set_target(self.player.center_x, self.player.center_y, instant=True)
            self.sound_manager.play("craft")
            self.particle_system.spawn_sparks(self.player.center_x, self.player.center_y, (100, 220, 255), count=35)
            self.combat.spawn_boss(dung_x, dung_y, boss_cls="cryo_spud")
            active.count -= 1
            if active.count <= 0:
                self.inventory.slots[self.inventory.selected_slot] = None
            return

        if active.item_id == "necro_rune":
            print("[Teleport] Spud uses the Blight Altar Rune to warp to the Blight Shadow Crypt Arena!")
            self.player.pre_arena_pos = (self.player.x, self.player.y)
            dung_x, dung_y = getattr(self.world, "necro_arena_spawn", (3000, 200))
            if hasattr(self.world, "chunk_manager"):
                tcx = int(dung_x // (CHUNK_WIDTH * SCALED_TILE))
                self.world.chunk_manager.ensure_chunks_in_range(tcx - 2, tcx + 2)
            self.combat.mobs.clear()
            self.player.x = dung_x
            self.player.y = dung_y
            self.player.vx = 0.0
            self.player.vy = 0.0
            self.camera.set_target(self.player.center_x, self.player.center_y, instant=True)
            self.sound_manager.play("craft")
            self.particle_system.spawn_sparks(self.player.center_x, self.player.center_y, (180, 70, 255), count=35)
            self.combat.spawn_boss(dung_x, dung_y, boss_cls="necro_tuber")
            active.count -= 1
            if active.count <= 0:
                self.inventory.slots[self.inventory.selected_slot] = None
            return

        # 2.5. CELESTIAL KEYSTONE -> SUMMON GRAND BOSS SOL-RHO!
        if active.item_id == "celestial_keystone":
            party_sz = (len(self.client.remote_players) + 1) if (self.client and self.client.connected) else 1
            print(f"[Keystone] Spud uses the Celestial Keystone! Party Size: {party_sz}")
            self.sound_manager.play("craft")
            self.particle_system.spawn_sparks(self.player.center_x, self.player.center_y, (255, 215, 0), count=60)
            self.camera.add_shake(16.0, 1.2)
            self.combat.spawn_grand_boss(self.player.center_x, self.player.center_y, party_size=party_sz)
            active.count -= 1
            if active.count <= 0:
                self.inventory.slots[self.inventory.selected_slot] = None
            return

        # 3. Wall Placement (e.g. Wood Wall, Stone Brick Wall)
        if (cat == CAT_WALL or "wall" in active.data) and reach <= SCALED_TILE * 5.5:
            wall_id = active.data.get("wall")
            if wall_id is not None and self.world.place_wall(tx, ty, wall_id):
                self.wall_deltas[(tx, ty)] = wall_id
                self.sound_manager.play("place")
                active.count -= 1
                if active.count <= 0:
                    self.inventory.slots[self.inventory.selected_slot] = None
                if self.world.check_shelter(tx, ty):
                    self.achievement_manager.unlock("home_sweet_home")
                return

        # 4. Block / Furniture / Torch Placement
        if cat == CAT_BLOCK:
            self.handle_block_placement(mouse_x, mouse_y, active)

    def teleport_to_dungeon(self):
        """Teleports Spud directly to the Nether Dungeon Chamber and summons a Subterranean Mini-Boss!"""
        print("[Teleport] Spud uses the Dungeon Rune to warp to the Nether Dungeon!")
        self.sound_manager.play("craft")
        self.particle_system.spawn_sparks(self.player.center_x, self.player.center_y, (200, 60, 255), count=30)
        
        # Warp Spud
        self.player.pre_arena_pos = (self.player.x, self.player.y)
        dung_x, dung_y = self.world.dungeon_spawn
        self.player.x = dung_x
        self.player.y = dung_y
        self.player.vx = 0.0
        self.player.vy = 0.0
        self.camera.set_target(self.player.center_x, self.player.center_y, instant=True)
        self.camera.add_shake(8.0, 0.4)

        # Awaken Dungeon Mini-Boss!
        if not self.combat.is_client:
            self.combat.spawn_boss(dung_x, dung_y)

    def get_weapon_attack_cooldown(self, active_item=None):
        """Calculates effective attack interval in seconds based on weapon archetype,
        custom item use_time, and player attack speed."""
        if not active_item:
            base_time = 0.30
        else:
            item_id = active_item.item_id.lower()
            data = active_item.data
            if "use_time" in data and data["use_time"] > 0:
                base_time = float(data["use_time"])
            elif any(w in item_id for w in ("dagger", "shortsword", "knife", "stiletto")):
                base_time = 0.22 # Very fast
            elif any(w in item_id for w in ("greatsword", "cleaver", "hammer", "scythe", "titan", "colossus")):
                base_time = 0.46 # Heavy, deliberate strike
            elif any(w in item_id for w in ("bow", "crossbow", "recurve", "shortbow", "longbow", "composite")):
                base_time = 0.52 # Archery volley - calibrated fire rate
            elif any(w in item_id for w in ("staff", "wand", "scepter", "rod", "catalyst", "focus", "grimoire", "tome", "orb")):
                base_time = 0.54 # Arcane spellcast / catalyst channel - calibrated fire rate
            elif any(w in item_id for w in ("katana", "saber", "rapier", "spear")):
                base_time = 0.26 # Swift blade
            elif any(w in item_id for w in ("starfury", "astral_wrath")):
                base_time = 0.35 # Celestial starfall
            else:
                base_time = 0.32 # Standard broadsword / blade

        atk_speed_mult = getattr(self.player.stats, "total_atk_speed", 1.0)
        cooldown = max(0.08, base_time / max(0.2, atk_speed_mult))
        return cooldown

    def handle_fishing_action(self, mouse_x, mouse_y):
        if hasattr(self, "fishing_minigame") and self.fishing_minigame.is_active:
            return self.fishing_minigame.handle_click(is_right_click=True)

        mouse_wx, mouse_wy = self.camera.screen_to_world(mouse_x, mouse_y)
        tx, ty = int(mouse_wx // SCALED_TILE), int(mouse_wy // SCALED_TILE)

        if not getattr(self, "fishing_bobber", None):
            is_water = (
                self.world.get_tile(tx, ty) == TILE_WATER or
                self.world.get_tile(tx, ty + 1) == TILE_WATER or
                self.world.get_tile(tx, ty - 1) == TILE_WATER
            )
            if not is_water:
                if hasattr(self.inventory, "notify"):
                    self.inventory.notify("Cast your fishing rod into the water!")
                return False

            bob_x = tx * SCALED_TILE + 16
            bob_y = ty * SCALED_TILE + 16
            dist = math.hypot(self.player.center_x - bob_x, self.player.center_y - bob_y)
            if dist > 350.0:
                if hasattr(self.inventory, "notify"):
                    self.inventory.notify("Too far away to cast!")
                return False

            self.fishing_bobber = {
                "x": bob_x,
                "y": bob_y,
                "state": "waiting",
                "timer": random.uniform(2.0, 4.0),
                "bite_timer": 0.0,
            }
            self.sound_manager.play("swing")
            self.particle_system.spawn_debris(bob_x, bob_y, (60, 140, 240), count=6)
            return True
        else:
            bob = self.fishing_bobber
            if bob.get("state") == "bite":
                pinoy_fishes = [
                    "raw_bangus", "raw_tilapia", "raw_galunggong", "raw_maya_maya",
                    "raw_tanigue", "raw_tambakol", "raw_lapu_lapu", "raw_hito",
                    "raw_dilis", "raw_dalagang_bukid"
                ]
                rare_loot = [
                    "gold_coin", "silver_coin", "iron_ore", "copper_ore",
                    "healing_potion", "speed_potion"
                ]
                if random.random() < 0.85:
                    caught_item = random.choice(pinoy_fishes)
                    caught_count = random.randint(2, 5) if caught_item == "raw_dilis" else 1
                else:
                    caught_item = random.choice(rare_loot)
                    caught_count = random.randint(1, 3)

                self.fishing_bobber = None
                self.fishing_minigame.start(fish_id=caught_item, caught_count=caught_count)
                return True
            else:
                self.sound_manager.play("dig_dirt")

            self.fishing_bobber = None
            return True

    def handle_primary_action(self, mouse_x, mouse_y):
        active = self.inventory.get_active_item()
        if active and active.item_id == "fishing_rod":
            return self.handle_fishing_action(mouse_x, mouse_y)
        if active and getattr(active, "is_broken", False):
            if hasattr(self.inventory, "notify"):
                self.inventory.notify("This weapon is broken! Repair it at the Mystic Trader.")
            return False
        equipped_weapon = getattr(self.player.equipment, "slots", {}).get(SLOT_WEAPON) if hasattr(self.player, "equipment") else None
        if equipped_weapon and getattr(equipped_weapon, "is_broken", False):
            if hasattr(self.inventory, "notify"):
                self.inventory.notify("This weapon is broken! Repair it at the Mystic Trader.")
            return False
        is_held_weapon = (active and active.data.get("cat") == CAT_WEAPON)

        # Check if mouse is targeting an in-reach breakable tile
        tx, ty = self.camera.screen_to_tile(mouse_x, mouse_y)
        tile_world_x = tx * SCALED_TILE
        tile_world_y = ty * SCALED_TILE
        reach = math.hypot(self.player.center_x - (tile_world_x + SCALED_TILE / 2),
                           self.player.center_y - (tile_world_y + SCALED_TILE / 2))
        tile_id = self.world.get_tile(tx, ty)
        mining_dmg = get_mining_damage(active, tile_id)
        is_target_mineable = (reach <= SCALED_TILE * 5.5 and mining_dmg > 0)

        # Bare hands can mine wood and dirt if targeting an in-reach block.
        # If targeting unmineable stone/air, bare hands with an equipped paperdoll weapon performs combat attack.
        is_bare_hands_weapon = (active is None and equipped_weapon is not None and not is_target_mineable)
        is_combat_attack = is_held_weapon or is_bare_hands_weapon

        if is_combat_attack:
            # Rate-limit check: Prevents auto-clickers from spamming multiple attacks in a single frame!
            if not self.player.can_attack():
                return False

            cooldown = self.get_weapon_attack_cooldown(active)
            atk_speed_mult = getattr(self.player.stats, "total_atk_speed", 1.0)

            # Check if active weapon is a ranged bow / crossbow / recurve
            held_id = active.item_id.lower() if active else ""
            held_name = active.data.get("name", "").lower() if active and hasattr(active, "data") else ""
            is_bow = (
                held_id in ("wood_bow", "bone_bow", "magma_bow", "celestial_bow", "composite_bow", "reinforced_composite_bow", "ancient_composite_bow")
                or any(w in held_id or w in held_name for w in ("bow", "crossbow", "recurve", "shortbow", "longbow", "composite"))
            )

            # 1. Ranged Ballistic Bows (wood_bow, bone_bow, magma_bow, celestial_bow, and all 95+ bows/crossbows)
            if is_bow:
                arrow_type = None
                bonus_dmg = 0
                if self.inventory.count_item("astral_arrow") > 0:
                    arrow_type = "astral_arrow"
                    bonus_dmg = 14
                elif self.inventory.count_item("frostburn_arrow") > 0:
                    arrow_type = "frostburn_arrow"
                    bonus_dmg = 8
                elif self.inventory.count_item("flame_arrow") > 0:
                    arrow_type = "flame_arrow"
                    bonus_dmg = 6
                elif self.inventory.count_item("wooden_arrow") > 0:
                    arrow_type = "wooden_arrow"
                    bonus_dmg = 0
                elif (active.data.get("rarity") in ("ancient", "legendary", "mythic") if hasattr(active, "data") else False) or held_id == "celestial_bow":
                    # Ancient & Legendary relic bows channel celestial starlight energy arrows if out of physical arrows!
                    arrow_type = "astral_arrow"
                    bonus_dmg = 10

                if not arrow_type:
                    # Out of arrows! Cannot fire!
                    self.sound_manager.play_spatial("bow", self.player.center_x, self.player.center_y, self.player.center_x, self.player.center_y)
                    self.combat.spawn_damage_number(self.player.center_x, self.player.y - 14, "No Arrows!", color=(255, 120, 100))
                    return False

                if arrow_type in ("astral_arrow", "frostburn_arrow", "flame_arrow", "wooden_arrow"):
                    self.inventory.remove_item(arrow_type, 1)

                # Special arrow upgrade for flame/magma bows
                if arrow_type == "wooden_arrow" and any(w in held_id for w in ("magma", "fire", "flame", "pyre", "smolder", "molten")):
                    arrow_type = "flame_arrow"
                    bonus_dmg += 4

                self.player.trigger_attack(cooldown)
                mouse_wx, mouse_wy = self.camera.screen_to_world(mouse_x, mouse_y)
                self.combat.trigger_weapon_swing_effects(self.player, mouse_wx, mouse_wy, active_item=active)

                bow_table = {"wood_bow": 14, "bone_bow": 22, "magma_bow": 28, "celestial_bow": 42}
                base_bow_atk = active.data.get("atk", active.data.get("damage", bow_table.get(active.item_id, 16)))
                total_arrow_dmg = max(10, base_bow_atk + bonus_dmg)

                special_txt = (active.data.get("special", "") + " " + active.data.get("desc", "")).lower() if hasattr(active, "data") else ""
                arrow_speed = 14.5
                if "velocity" in special_txt or "speed" in special_txt or "crossbow" in held_id:
                    arrow_speed = 17.5

                angle = math.atan2(mouse_wy - self.player.center_y, mouse_wx - self.player.center_x)
                spawn_x = self.player.center_x + math.cos(angle) * 16.0
                spawn_y = self.player.center_y + math.sin(angle) * 16.0
                arrow = ArrowProjectile(spawn_x, spawn_y, angle, speed=arrow_speed, damage=total_arrow_dmg, arrow_type=arrow_type)
                arrow.is_ancient = bool(active and (active.data.get("rarity") == "ancient" or "ancient" in held_id))
                self.combat.spawn_projectile(arrow)
                self.sound_manager.play_spatial("bow", self.player.center_x, self.player.center_y, self.player.center_x, self.player.center_y)

                # Ancient bow visual burst and celestial screen shake
                if active and (active.data.get("rarity") == "ancient" or "ancient" in held_id):
                    if hasattr(self, "vfx_manager") and self.vfx_manager:
                        self.vfx_manager.spawn("ancient_burst", spawn_x, spawn_y, duration=0.55)
                        self.vfx_manager.spawn("starlight_volley_burst", spawn_x, spawn_y, duration=0.45)
                    self.camera.add_shake(5.0, 0.20)
                return True

            # For melee weapons & magic weapons: trigger attack animation & weapon swing effects
            self.player.trigger_attack(cooldown)
            mouse_wx, mouse_wy = self.camera.screen_to_world(mouse_x, mouse_y)
            self.combat.trigger_weapon_swing_effects(self.player, mouse_wx, mouse_wy, active_item=active)

            # Grand Ancient weapon visuals
            is_ancient_weap = bool(active and (active.data.get("rarity") == "ancient" or "ancient" in held_id))
            if is_ancient_weap:
                if hasattr(self, "vfx_manager") and self.vfx_manager:
                    swing_ang = math.atan2(mouse_wy - self.player.center_y, mouse_wx - self.player.center_x)
                    slash_x = self.player.center_x + math.cos(swing_ang) * 32.0
                    slash_y = self.player.center_y + math.sin(swing_ang) * 32.0
                    rot_deg = -math.degrees(swing_ang)
                    self.vfx_manager.spawn("ancient_slash", slash_x, slash_y, duration=0.45, rot_deg=rot_deg)
                    self.vfx_manager.spawn("ancient_burst", slash_x, slash_y, duration=0.55)
                    self.vfx_manager.spawn("ancient_cleave_grand", slash_x, slash_y, duration=0.45, rot_deg=rot_deg)
                self.camera.add_shake(7.0, 0.25)

            # 2. Magic Catalysts (Homing celestial star/orb, max 560px)
            is_catalyst = active and any(w in held_id for w in ("catalyst", "focus", "grimoire", "tome", "orb"))
            if is_catalyst:
                angle = math.atan2(mouse_wy - self.player.center_y, mouse_wx - self.player.center_x)
                speed = 9.0
                fb_vx = math.cos(angle) * speed
                fb_vy = math.sin(angle) * speed
                dmg = active.data.get("atk", active.data.get("damage", 32))
                cat_sprite = self.asset_factory.projectiles.get("catalyst_orb")
                star_proj = CatalystStarProjectile(self.player.center_x, self.player.center_y, fb_vx, fb_vy, sprite=cat_sprite, damage=dmg, max_distance=560.0, combat=self.combat)
                star_proj.is_ancient = is_ancient_weap
                self.player.fireballs.append(star_proj)
                self.sound_manager.play("swing")
                self.particle_system.spawn_sparks(self.player.center_x, self.player.center_y, (255, 220, 80), count=12)
                return True

            # 3. Magic Staves and Wands (Elemental magic bolts, max 560px)
            is_staff = active and (active.item_id in ("fire_staff", "frost_staff") or any(w in held_id for w in ("staff", "wand")))
            if is_staff:
                angle = math.atan2(mouse_wy - self.player.center_y, mouse_wx - self.player.center_x)
                speed = 8.5
                fb_vx = math.cos(angle) * speed
                fb_vy = math.sin(angle) * speed
                dmg = active.data.get("atk", active.data.get("damage", 28))
                elem = "arcane"
                spark_col = (180, 100, 255)
                if any(w in held_id for w in ("frost", "cryo", "ice", "polar")):
                    elem = "frost"
                    spark_col = (100, 220, 255)
                elif any(w in held_id for w in ("fire", "magma", "pyre", "blaze")):
                    elem = "fire"
                    spark_col = (255, 140, 40)
                elif any(w in held_id for w in ("verdant", "bloom", "thorn", "moss", "briar")):
                    elem = "nature"
                    spark_col = (80, 230, 90)
                staff_sprite = self.asset_factory.projectiles.get("staff_bolt")
                bolt = StaffBoltProjectile(self.player.center_x, self.player.center_y, fb_vx, fb_vy, sprite=staff_sprite, damage=dmg, max_distance=560.0, element=elem)
                bolt.is_ancient = is_ancient_weap
                self.player.fireballs.append(bolt)
                self.sound_manager.play("swing")
                self.particle_system.spawn_sparks(self.player.center_x, self.player.center_y, spark_col, count=8)
                return True

            # 4. Piercing Rods (High-velocity piercing javelin, max 560px)
            is_rod = active and any(w in held_id for w in ("rod", "javelin"))
            if is_rod:
                angle = math.atan2(mouse_wy - self.player.center_y, mouse_wx - self.player.center_x)
                speed = 12.0
                fb_vx = math.cos(angle) * speed
                fb_vy = math.sin(angle) * speed
                dmg = active.data.get("atk", active.data.get("damage", 26))
                rod_sprite = self.asset_factory.projectiles.get("rod_javelin")
                javelin = RodJavelinProjectile(self.player.center_x, self.player.center_y, fb_vx, fb_vy, sprite=rod_sprite, damage=dmg, max_distance=560.0)
                javelin.is_ancient = is_ancient_weap
                self.player.fireballs.append(javelin)
                self.sound_manager.play("swing")
                self.particle_system.spawn_sparks(self.player.center_x, self.player.center_y, (120, 240, 255), count=10)
                return True

            # 5. Expanding Scepters (Arcane pulse shockwave, max 560px)
            is_scepter = active and (active.item_id == "void_scepter" or any(w in held_id for w in ("scepter", "pulse")))
            if is_scepter:
                angle = math.atan2(mouse_wy - self.player.center_y, mouse_wx - self.player.center_x)
                speed = 7.0
                fb_vx = math.cos(angle) * speed
                fb_vy = math.sin(angle) * speed
                dmg = active.data.get("atk", active.data.get("damage", 34))
                scepter_sprite = self.asset_factory.projectiles.get("scepter_pulse")
                pulse = ScepterPulseProjectile(self.player.center_x, self.player.center_y, fb_vx, fb_vy, sprite=scepter_sprite, damage=dmg, max_distance=560.0)
                pulse.is_ancient = is_ancient_weap
                self.player.fireballs.append(pulse)
                self.sound_manager.play("swing")
                self.particle_system.spawn_sparks(self.player.center_x, self.player.center_y, (210, 100, 255), count=10)
                return True

            # 6. Celestial Magic Starfury (Summons stars plunging from the heavens!)
            elif active and active.item_id in ("starfury", "astral_wrath"):
                self.sound_manager.play_spatial("starfury", self.player.center_x, self.player.center_y, self.player.center_x, self.player.center_y)
                return True

            if hasattr(self.sound_manager, "play_swing"):
                self.sound_manager.play_swing(cooldown=cooldown, speed_mult=atk_speed_mult)
            else:
                self.sound_manager.play("swing")
            return True

        # Mining: Only tools (pickaxe, axe) or bare hands (active is None) can mine blocks!
        # Holding other items (weapons, food, potions, blocks, armor, materials) will NOT destroy blocks!
        if active is None or active.data.get("cat") == CAT_TOOL:
            self.player.start_swing()
            self._mine_tile_at_mouse(mouse_x, mouse_y, active)
            return True

    def _mine_tile_at_mouse(self, mouse_x, mouse_y, active_item):
        tx, ty = self.camera.screen_to_tile(mouse_x, mouse_y)
        tile_world_x = tx * SCALED_TILE
        tile_world_y = ty * SCALED_TILE

        reach = math.hypot(self.player.center_x - (tile_world_x + SCALED_TILE / 2),
                           self.player.center_y - (tile_world_y + SCALED_TILE / 2))
        if reach > SCALED_TILE * 5.5:
            return

        tile_id = self.world.get_tile(tx, ty)
        if tile_id == TILE_AIR:
            return

        power = get_mining_damage(active_item, tile_id)
        if power <= 0:
            return

        broken, drop_id, tile_id = self.world.damage_tile_at(tx, ty, power)
        
        color = self._get_tile_debris_color(tile_id)
        self.particle_system.spawn_debris(tile_world_x + 16, tile_world_y + 16, color, count=6)

        if tile_id in (TILE_DIRT, TILE_GRASS):
            self.sound_manager.play("dig_dirt")
        elif tile_id in (TILE_STONE, TILE_COPPER_ORE, TILE_IRON_ORE, TILE_GOLD_ORE):
            self.sound_manager.play("dig_stone")
        elif tile_id in (TILE_WOOD, TILE_WOOD_TRUNK, TILE_LEAVES):
            self.sound_manager.play("dig_wood")

        if broken:
            if tile_id in (TILE_CHEST, TILE_IRON_CHEST) or drop_id in ("chest", "iron_chest"):
                self._open_or_break_chest(tx, ty, tile_world_x, tile_world_y)
            else:
                self.block_deltas[(tx, ty)] = TILE_AIR
                if self.client and self.client.connected:
                    self.client.send_block_delta(tx, ty, TILE_AIR)
                if drop_id:
                    self.combat.dropped_items.append(
                        DroppedItem(drop_id, 1, tile_world_x + 8, tile_world_y + 4, self.asset_factory)
                    )
                bonus_drop = getattr(self.world, "last_bonus_drop", None)
                if bonus_drop:
                    self.world.last_bonus_drop = None
                    self.combat.dropped_items.append(
                        DroppedItem(bonus_drop, 1, tile_world_x + 12, tile_world_y + 4, self.asset_factory)
                    )
                # Tree Felling overhaul & Timber achievement
                if tile_id in (TILE_WOOD, TILE_WOOD_TRUNK) or drop_id == "wood":
                    self.achievement_manager.unlock("timber")
                    felled = getattr(self.world, "last_felled_tree", None)
                    if felled:
                        felled_count, leaf_coords = felled[:2]
                        trunk_coords = getattr(self.world, "last_felled_trunks", [])
                        # Record all felled trunks in block deltas & multiplayer network sync
                        for fx, fy in trunk_coords:
                            self.block_deltas[(fx, fy)] = TILE_AIR
                            if self.client and self.client.connected:
                                self.client.send_block_delta(fx, fy, TILE_AIR)
                        # Record all felled leaves in block deltas & multiplayer network sync
                        for lx, ly in leaf_coords:
                            self.block_deltas[(lx, ly)] = TILE_AIR
                            if self.client and self.client.connected:
                                self.client.send_block_delta(lx, ly, TILE_AIR)
                            self.particle_system.spawn_debris(lx * SCALED_TILE + 16, ly * SCALED_TILE + 16, (60, 180, 50), count=4)
                        for _ in range(max(0, felled_count - 1)):
                            self.combat.dropped_items.append(
                                DroppedItem("wood", 1, tile_world_x + random.randint(4, 12), tile_world_y - random.randint(4, 20), self.asset_factory)
                            )
                        # Occasional apple or acorn drop from fallen foliage
                        if random.random() < 0.35:
                            self.combat.dropped_items.append(
                                DroppedItem("apple", 1, tile_world_x + 8, tile_world_y - 12, self.asset_factory)
                            )
                        self.world.last_felled_tree = None
                        self.world.last_felled_trunks = []
                self.lighting.dirty = True
                self.hud.minimap.mark_dirty()

    def _get_tile_debris_color(self, tile_id):
        colors = {
            TILE_DIRT: (134, 96, 67),
            TILE_GRASS: (74, 196, 48),
            TILE_STONE: (128, 128, 128),
            TILE_WOOD: (160, 110, 60),
            TILE_WOOD_TRUNK: (120, 80, 45),
            TILE_LEAVES: (45, 150, 35),
            TILE_COPPER_ORE: (220, 115, 35),
            TILE_IRON_ORE: (190, 195, 205),
            TILE_GOLD_ORE: (255, 215, 0),
            TILE_TORCH: (255, 180, 40),
            TILE_CHEST: (185, 130, 70),
            TILE_IRON_CHEST: (200, 205, 215),
            TILE_SAPLING: (70, 180, 50),
            TILE_ROPE_RUNGS: (160, 120, 70),
            TILE_SAND: (225, 200, 140),
            TILE_SANDSTONE: (195, 165, 110),
            TILE_CACTUS: (50, 150, 60),
            TILE_SNOW: (230, 240, 255),
            TILE_ICE: (160, 210, 255),
            TILE_CORRUPT_GRASS: (120, 70, 160),
            TILE_EBONSTONE: (80, 50, 100),
            TILE_MUSHROOM_GRASS: (50, 140, 220),
        }
        return colors.get(tile_id, (150, 150, 150))

    def handle_block_placement(self, mouse_x, mouse_y, active=None):
        if active is None:
            active = self.inventory.get_active_item()
        if not active:
            return

        tx, ty = self.camera.screen_to_tile(mouse_x, mouse_y)
        tile_world_x = tx * SCALED_TILE
        tile_world_y = ty * SCALED_TILE

        reach = math.hypot(self.player.center_x - (tile_world_x + SCALED_TILE / 2),
                           self.player.center_y - (tile_world_y + SCALED_TILE / 2))
        if reach > SCALED_TILE * 5.5:
            return

        cat = active.data.get("cat") if hasattr(active, "data") else None
        wall_id = active.data.get("wall") if hasattr(active, "data") else None

        # Support Wall placement (e.g. wood wall, stone brick wall)
        if (cat == CAT_WALL or wall_id is not None) and wall_id is not None:
            if self.world.place_wall(tx, ty, wall_id):
                self.wall_deltas[(tx, ty)] = wall_id
                self.sound_manager.play("place")
                active.count -= 1
                if active.count <= 0:
                    self.inventory.slots[self.inventory.selected_slot] = None
                if self.world.check_shelter(tx, ty):
                    self.achievement_manager.unlock("home_sweet_home")
            return

        tile_id_to_place = active.data.get("tile")
        if not tile_id_to_place:
            return

        target_rect = pygame.Rect(tile_world_x, tile_world_y, SCALED_TILE, SCALED_TILE)
        is_solid = TILE_PROPS.get(tile_id_to_place, {}).get("solid", False)
        if is_solid and target_rect.colliderect(self.player.rect):
            return

        chest_type = active.item_id if active and (active.item_id in ("chest", "iron_chest") or "sapling" in active.item_id) else "chest"
        placed = self.world.place_tile(tx, ty, tile_id_to_place, chest_type=chest_type)
        if placed:
            self.block_deltas[(tx, ty)] = tile_id_to_place
            if self.client and self.client.connected:
                self.client.send_block_delta(tx, ty, tile_id_to_place)
            self.sound_manager.play("place")
            active.count -= 1
            if active.count <= 0:
                self.inventory.slots[self.inventory.selected_slot] = None
            if self.world.check_shelter(tx, ty):
                self.achievement_manager.unlock("home_sweet_home")
            self.lighting.dirty = True
            self.hud.minimap.mark_dirty()
        else:
            if tile_id_to_place == TILE_TORCH:
                if self.world.is_water(tx, ty):
                    msg = "Torches cannot be placed underwater!"
                else:
                    msg = "Torches require a supporting block or background wall!"
                if hasattr(self.hud, "add_chat_message"):
                    self.hud.add_chat_message("[NOTICE]", msg)
            elif tile_id_to_place in LANTERN_TILES:
                if self.world.is_water(tx, ty):
                    msg = "Lanterns cannot be placed underwater!"
                else:
                    msg = "Lanterns require a ceiling block to the North, a floor below, or a background wall!"
                if hasattr(self.hud, "add_chat_message"):
                    self.hud.add_chat_message("[NOTICE]", msg)

    def update_gameplay(self, dt):
        self.playtime = getattr(self, "playtime", 0.0) + dt
        self.profiler.start_section("update_other")
        keys = pygame.key.get_pressed()
        mouse_x, mouse_y = self.get_mouse_pos()
        mouse_wx, mouse_wy = self.camera.screen_to_world(mouse_x, mouse_y)

        # Update inventory timers (notification banners, etc.)
        self.inventory.update(dt)
        if self.inventory.is_open:
            self.crafting.update_recipes(self.inventory, self.world, self.player)

        # Update Touch Controller states & dynamic button cooldowns/badges
        if hasattr(self, "touch_controller"):
            self.touch_controller.update(dt, player=self.player, inventory=self.inventory)

        # Update Fishing Battle Mini-Game
        if hasattr(self, "fishing_minigame") and self.fishing_minigame.is_active:
            res = self.fishing_minigame.update(dt)
            if res == "caught":
                fish_id = self.fishing_minigame.fish_id
                fish_cnt = self.fishing_minigame.caught_count
                self.combat.dropped_items.append(
                    DroppedItem(fish_id, fish_cnt, self.player.center_x, self.player.center_y - 20, self.asset_factory)
                )
                from src.ui.inventory import ITEM_REGISTRY
                item_name = ITEM_REGISTRY.get(fish_id, {}).get("name", fish_id.replace("_", " ").title())
                if hasattr(self.hud, "add_chat_message"):
                    self.hud.add_chat_message(f"Caught {item_name} x{fish_cnt}!", (100, 230, 255))
                if hasattr(self.inventory, "notify"):
                    self.inventory.notify(f"Caught {item_name} x{fish_cnt}!")
                self.sound_manager.play("craft")
                self.particle_system.spawn_sparks(self.player.center_x, self.player.center_y - 10, (100, 220, 255), count=15)
                self.fishing_minigame.result = None
            elif res == "escaped":
                if hasattr(self.inventory, "notify"):
                    self.inventory.notify("The fish snapped the line and escaped!")
                self.sound_manager.play("dig_dirt")
                self.fishing_minigame.result = None
            elif res == "cancelled":
                if hasattr(self.inventory, "notify"):
                    self.inventory.notify("Fishing battle cancelled!")
                self.fishing_minigame.result = None

        # Update Fishing Bobber state
        if getattr(self, "fishing_bobber", None):
            bob = self.fishing_bobber
            p_dist = math.hypot(self.player.center_x - bob["x"], self.player.center_y - bob["y"])
            if p_dist > 400.0:
                self.fishing_bobber = None
            elif bob.get("state") == "waiting":
                bob["timer"] -= dt
                if bob["timer"] <= 0:
                    bob["state"] = "bite"
                    bob["bite_timer"] = 2.5
                    self.sound_manager.play("hit")
                    self.particle_system.spawn_debris(bob["x"], bob["y"], (80, 180, 255), count=8)
            elif bob.get("state") == "bite":
                bob["bite_timer"] -= dt
                if bob["bite_timer"] <= 0:
                    bob["state"] = "waiting"
                    bob["timer"] = random.uniform(3.0, 5.0)

        # 1. Continuous Mining & Continuous Attacking / Block Placing (Paced by Fire Rate & Mining Rate)
        is_attack_active = (
            pygame.mouse.get_pressed()[0] or
            (hasattr(self, "touch_controller") and (self.touch_controller.is_attack_down or self.touch_controller.is_direct_touching))
        )
        if is_attack_active and not self.inventory.is_open and not self.character_panel.is_open and not (hasattr(self, "npc_dialogue") and self.npc_dialogue.is_open):
            active_item = self.inventory.get_active_item()
            is_weapon = (active_item and active_item.data.get("cat") == CAT_WEAPON)
            is_block_or_wall = (active_item and (active_item.data.get("cat") in (CAT_BLOCK, CAT_WALL) or active_item.data.get("tile") is not None or active_item.data.get("wall") is not None))

            if hasattr(self, "touch_controller") and self.touch_controller.is_direct_touching and self.touch_controller.direct_touch_pos:
                target_sx, target_sy = self.touch_controller.direct_touch_pos
            elif hasattr(self, "touch_controller") and self.touch_controller.is_attack_down:
                aim_dist = 64.0
                aim_wx = self.player.center_x + math.cos(self.player.aim_angle) * aim_dist
                aim_wy = self.player.center_y + math.sin(self.player.aim_angle) * aim_dist
                target_sx, target_sy = self.camera.world_to_screen(aim_wx, aim_wy)
            else:
                target_sx, target_sy = mouse_x, mouse_y

            if is_weapon:
                if self.player.can_attack():
                    self.handle_primary_action(target_sx, target_sy)
            elif is_block_or_wall:
                self.mining_cooldown -= dt
                if self.mining_cooldown <= 0:
                    self.mining_cooldown = 0.20
                    self.handle_block_placement(target_sx, target_sy, active=active_item)
            else:
                self.mining_cooldown -= dt
                if self.mining_cooldown <= 0:
                    self.mining_cooldown = self.continuous_mine_rate
                    self.handle_primary_action(target_sx, target_sy)
        else:
            self.mining_cooldown = 0.0

        # Synchronize active hotbar weapon stats to Spud dynamically
        active_item = self.inventory.get_active_item()
        active_state = None
        if active_item and not getattr(active_item, "is_broken", False):
            active_state = (
                active_item.item_id,
                getattr(active_item, "enhancement_level", 0),
                getattr(active_item, "is_broken", False),
                tuple(getattr(active_item, "affixes", [])),
                tuple(getattr(active_item, "removed_stats", [])),
            )
        if getattr(self.player, "_last_active_weapon", object()) != active_state:
            self.player._last_active_weapon = active_state
            self.player.equipment.recalculate_stats(self.player.stats, active_item=active_item if (active_item and not getattr(active_item, "is_broken", False)) else None)

        # 2. Player Input & Physics
        aim_target_wx, aim_target_wy = mouse_wx, mouse_wy
        if hasattr(self, "touch_controller") and self.touch_controller.is_visible():
            active_keys = self.touch_controller.get_virtual_keys(keys, key_bindings=self.menu.key_bindings)
            # When touch input is used without direct touching, aim in joystick / facing direction
            if hasattr(self.touch_controller, "has_touch_input") and self.touch_controller.has_touch_input and not self.touch_controller.is_direct_touching:
                js = self.touch_controller.joystick
                if abs(js.axis_x) > 0.15 or abs(js.axis_y) > 0.15:
                    self.player.facing_right = (js.axis_x >= 0)
                    self.player.aim_angle = math.atan2(js.axis_y, js.axis_x)
                aim_target_wx = self.player.center_x + math.cos(self.player.aim_angle) * 100.0
                aim_target_wy = self.player.center_y + math.sin(self.player.aim_angle) * 100.0
        else:
            active_keys = keys
        self.profiler.end_section("update_other")
        with self.profiler.section("update_player"):
            self.player.handle_input(active_keys, aim_target_wx, aim_target_wy, key_bindings=self.menu.key_bindings, world=self.world)
            self.player.update(dt, self.world)

        # Update Achievements & Feat Tracking
        self.achievement_manager.update(dt)
        if getattr(self.player, "in_water", False):
            self.achievement_manager.unlock("deep_diver")
            if getattr(self.player, "is_submerged", False) or abs(self.player.vx) > 0.4 or abs(self.player.vy) > 0.4:
                if random.random() < 0.28:
                    self.particle_system.spawn_bubbles(self.player.center_x + random.randint(-6, 6), self.player.center_y + random.randint(-2, 10), count=1)
        if getattr(self.player, "submerged_duration", 0) >= 5.0:
            self.achievement_manager.unlock("hold_your_breath")
        if (self.player.center_y // SCALED_TILE) >= CAVERN_LEVEL:
            self.achievement_manager.unlock("into_the_depths")
        if all(slot is not None for slot in self.inventory.slots):
            self.achievement_manager.unlock("pack_mule")
        if getattr(self.combat, "last_slain_mob", None):
            self.achievement_manager.unlock("first_blood")
            self.combat.last_slain_mob = None
        if self.combat.boss_defeated:
            self.achievement_manager.unlock("slayer_of_titans")
        if self.combat.grand_boss_defeated:
            self.achievement_manager.unlock("potaria_hero")
            self.achievement_manager.unlock("slayer_of_titans")

        # Check Biome Dungeon Entry or Altar Proximity (Awaken Biome Mini-Boss or Grand Boss)
        # Note: In multiplayer, only host awakens boss from altar to avoid desync
        if not self.combat.is_client:
            ptx = int(self.player.center_x // SCALED_TILE)
            pty = int(self.player.center_y // SCALED_TILE)
            near_altar = False
            for dx in range(-2, 3):
                for dy in range(-2, 3):
                    if self.world.get_tile(ptx + dx, pty + dy) == TILE_DUNGEON_ALTAR:
                        near_altar = True
                        break
                if near_altar:
                    break

            if not self.combat.boss:
                # 1. Forest Nether Dungeon (Lord Malus)
                if (abs(ptx) <= 22 and 195 <= pty <= 218) or (near_altar and abs(ptx) <= 22 and pty >= 150):
                    if not self.combat.defeated_mini_bosses.get("lord_malus", False):
                        dung_x, dung_y = self.world.dungeon_spawn
                        self.combat.spawn_boss(dung_x, dung_y, boss_cls="lord_malus", player=self.player)

                # 2. Magma Underworld Dungeon (Ignis Colossus)
                elif (abs(ptx - 80) <= 22 and 195 <= pty <= 218) or (near_altar and abs(ptx - 80) <= 22 and pty >= 150):
                    if not self.combat.defeated_mini_bosses.get("ignis_colossus", False):
                        self.combat.spawn_boss(80 * SCALED_TILE, 215 * SCALED_TILE, boss_cls="ignis_colossus", player=self.player)

                # 3. Glacial Permafrost Crypt (Cryo-Spud)
                elif (abs(ptx - (-80)) <= 22 and 195 <= pty <= 218) or (near_altar and abs(ptx - (-80)) <= 22 and pty >= 150):
                    if not self.combat.defeated_mini_bosses.get("cryo_spud", False):
                        self.combat.spawn_boss(-80 * SCALED_TILE, 215 * SCALED_TILE, boss_cls="cryo_spud", player=self.player)

                # 4. Catacombs Blight Ossuary (Necro-Tuber)
                elif (abs(ptx - 140) <= 22 and 195 <= pty <= 218) or (near_altar and abs(ptx - 140) <= 22 and pty >= 150):
                    if not self.combat.defeated_mini_bosses.get("necro_tuber", False):
                        self.combat.spawn_boss(140 * SCALED_TILE, 215 * SCALED_TILE, boss_cls="necro_tuber", player=self.player)

                # 5. Sky Citadel (Grand Boss Sol-Rho in Deep Celestial Space)
                elif (abs(ptx) <= 22 and -185 <= pty <= -155) and all(self.combat.defeated_mini_bosses.values()):
                    self.combat.spawn_grand_boss(0.0, -165 * SCALED_TILE, player=self.player)

        # 3. LAN Multiplayer Synchronization
        if self.client and self.client.connected:
            held = self.inventory.get_active_item()
            held_id = held.item_id if held else ""
            if hasattr(self.client, "send_player_update"):
                self.client.send_player_update(
                    self.player.x, self.player.y, self.player.vx, self.player.vy,
                    self.player.stats.hp, self.player.stats.max_hp, self.player.stats.level,
                    self.player.facing_right, self.player.current_anim, held_id
                )
            while getattr(self.client, "pending_block_deltas", None):
                delta = self.client.pending_block_deltas.pop(0)
                tx, ty, tid = delta.get("tx"), delta.get("ty"), delta.get("tile_id")
                if tx is not None and ty is not None:
                    self.world.set_tile(tx, ty, tid)
                    self.block_deltas[(tx, ty)] = tid

            # Multiplayer Boss HP Scaling
            if self.combat.boss and len(self.client.remote_players) > 0 and not self.combat.is_client:
                party_size = len(self.client.remote_players) + 1
                target_max = int(1200 * (1.0 + (party_size - 1) * 0.4))
                if self.combat.boss.max_hp < target_max:
                    diff = target_max - self.combat.boss.max_hp
                    self.combat.boss.max_hp = target_max
                    self.combat.boss.hp += diff

            # Update multiplayer player positions for combat manager (spawning & despawning near all players)
            all_player_positions = [(self.player.center_x, self.player.center_y)]
            for rp in self.client.remote_players.values():
                if isinstance(rp, dict):
                    rpx = float(rp.get("x", 0.0)) + self.player.width / 2.0
                    rpy = float(rp.get("y", 0.0)) + self.player.height / 2.0
                else:
                    rpx = getattr(rp, "center_x", getattr(rp, "x", 0.0) + self.player.width / 2.0)
                    rpy = getattr(rp, "center_y", getattr(rp, "y", 0.0) + self.player.height / 2.0)
                all_player_positions.append((rpx, rpy))
            self.combat.multiplayer_player_positions = all_player_positions

            # Client vs Host Mob Synchronization
            if self.combat.is_client:
                # 1. Apply latest authoritative mob sync snapshot from host
                mob_sync = self.client.get_latest_mob_sync()
                if mob_sync:
                    mobs_data = mob_sync.get("mobs", [])
                    boss_data = mob_sync.get("boss", None)
                    sky_time = mob_sync.get("sky_time", None)
                    if sky_time is not None:
                        self.sky.time = float(sky_time)
                    enemy_proj_data = mob_sync.get("enemy_projectiles", None)
                    dropped_items_data = mob_sync.get("dropped_items", None)
                    self.combat.sync_from_host(mobs_data, boss_data, enemy_projectiles=enemy_proj_data, dropped_items=dropped_items_data)
            else:
                # 1. Apply pending mob damages received from remote clients
                if self.server:
                    for dmg_data in self.server.get_pending_mob_damages():
                        self.combat.apply_remote_mob_damage(dmg_data)
                elif self.client and hasattr(self.client, "get_pending_mob_damages"):
                    for dmg_data in self.client.get_pending_mob_damages():
                        self.combat.apply_remote_mob_damage(dmg_data)

                # 2. Periodically broadcast mob snapshot to all connected clients (at 20 Hz / 50ms)
                self.mob_sync_timer += dt
                if self.mob_sync_timer >= 0.05:
                    self.mob_sync_timer = 0.0
                    mobs_data = self.combat.get_mobs_sync_data()
                    boss_data = self.combat.get_boss_sync_data()
                    sky_time = float(self.sky.time) if hasattr(self, "sky") else 0.0
                    enemy_proj_data = self.combat.get_enemy_projectiles_sync_data()
                    dropped_items_data = self.combat.get_dropped_items_sync_data()
                    if self.server:
                        self.server.broadcast_mobs(mobs_data, boss_data, sky_time=sky_time, enemy_projectiles=enemy_proj_data, dropped_items=dropped_items_data)
                    elif self.client and hasattr(self.client, "send_sync_mobs"):
                        self.client.send_sync_mobs(mobs_data, boss_data, sky_time=sky_time, enemy_projectiles=enemy_proj_data, dropped_items=dropped_items_data)
        else:
            self.combat.multiplayer_player_positions = [(self.player.center_x, self.player.center_y)]

        # 4. Camera Smooth Following
        self.camera.set_target(self.player.center_x, self.player.center_y)
        self.camera.update(dt)

        # 5. World, Town NPCs & Particles
        with self.profiler.section("update_world"):
            self.world.update(dt)
            if hasattr(self.world, "update_town_npcs"):
                self.world.update_town_npcs(dt, self.player, self.inventory, self.asset_factory, self.sound_manager, self.combat)
            if hasattr(self, "npc_dialogue"):
                self.npc_dialogue.update(dt)
            cam_rect = pygame.Rect(self.camera.x - 32, self.camera.y - 32, SCREEN_WIDTH + 64, SCREEN_HEIGHT + 64)
            self.world.emit_fireplace_smoke(self.particle_system, cam_rect)
            self.particle_system.update(dt)
            if hasattr(self, "vfx_manager") and self.vfx_manager:
                self.vfx_manager.update(dt)

        # 6. Day/Night Environment
        self.profiler.start_section("update_other")
        self.sky.update(dt)
        current_day = int(self.sky.time // max(1.0, self.sky.cycle_duration))
        if not hasattr(self, "current_day"):
            self.current_day = current_day
        elif current_day > self.current_day:
            self.current_day = current_day
            self.world.grow_plants_daily()

        # Sleeping fast-forwards through night until morning
        if getattr(self.player, "is_resting", False):
            # Check if any enemy has entered 6-block radius (interrupts sleep)
            radius = 6 * SCALED_TILE
            enemy_interrupted = False
            bed_pos = getattr(self.player, "resting_bed_pos", None)
            bed_cx = (bed_pos[0] * SCALED_TILE + SCALED_TILE / 2) if bed_pos else self.player.center_x
            bed_cy = (bed_pos[1] * SCALED_TILE + SCALED_TILE / 2) if bed_pos else self.player.center_y

            for mob in getattr(self.combat, "mobs", []):
                if getattr(mob, "is_alive", True) and not getattr(mob, "is_dead", False) and getattr(mob, "hp", 1) > 0:
                    d_p = math.hypot(mob.center_x - self.player.center_x, mob.center_y - self.player.center_y)
                    d_b = math.hypot(mob.center_x - bed_cx, mob.center_y - bed_cy)
                    if d_p <= radius or d_b <= radius:
                        enemy_interrupted = True
                        break

            if not enemy_interrupted and getattr(self.combat, "boss", None):
                boss = self.combat.boss
                if getattr(boss, "is_alive", True) and not getattr(boss, "is_dead", False) and getattr(boss, "hp", 1) > 0:
                    d_p = math.hypot(boss.center_x - self.player.center_x, boss.center_y - self.player.center_y)
                    d_b = math.hypot(boss.center_x - bed_cx, boss.center_y - bed_cy)
                    if d_p <= radius or d_b <= radius:
                        enemy_interrupted = True

            if enemy_interrupted:
                self.player.is_resting = False
                self.player.resting_bed_pos = None
                self.inventory.notify("You were awakened! Monsters are nearby within 6 blocks!")
            else:
                if getattr(self.sky, "is_night", False):
                    self.sky.update(dt * 6.0)
                if not getattr(self.sky, "is_night", False):
                    self.player.is_resting = False
                    self.player.resting_bed_pos = None
                    self.player.health = self.player.max_health
                    if hasattr(self.player, "stats"):
                        self.player.stats.hp = self.player.stats.max_hp
                        self.player.stats.mp = getattr(self.player.stats, "max_mp", 100)
                    self.inventory.notify("Morning has broken! Woke up refreshed.")

        self.profiler.end_section("update_other")
        # 7. Combat, Mobs & Boss
        with self.profiler.section("update_combat"):
            hp_before_combat = self.player.health
            time_of_day = getattr(self.sky, "time_of_day", getattr(self.sky, "time", 0.0) / max(1.0, getattr(self.sky, "cycle_duration", 480.0)))
            self.combat.update(dt, self.world, self.player, self.sky.is_night, time_of_day=time_of_day)

            # Interrupt fishing if player took damage from combat
            if self.player.health < hp_before_combat or (self.player.i_frame_timer >= 0.7 and getattr(self.player, "last_damage_taken", 0) > 0):
                if hasattr(self, "fishing_minigame") and self.fishing_minigame.is_active:
                    self.fishing_minigame.cancel()
                    if hasattr(self.inventory, "notify"):
                        self.inventory.notify("Fishing battle interrupted by enemy attack!")
                if getattr(self, "fishing_bobber", None):
                    self.fishing_bobber = None
                    if hasattr(self.inventory, "notify"):
                        self.inventory.notify("Fishing line snapped from enemy damage!")

        # God Mode Enforcement
        self.profiler.start_section("update_other")
        if getattr(self, "god_mode", False):
            self.player.health = self.player.max_health
            if hasattr(self.player, "stats"):
                self.player.stats.hp = self.player.stats.max_hp
                self.player.stats.mp = self.player.stats.max_mp
            self.player.i_frame_timer = 1.0
            self.player.oxygen = self.player.max_oxygen

        # 7.5. Dynamic Biome & Threat BGM Transition
        current_biome = self.world.get_biome_at_world(self.player.center_x, self.player.center_y)
        has_nearby_threat = any(
            mob.is_alive and math.hypot(mob.center_x - self.player.center_x, mob.center_y - self.player.center_y) < 360
            for mob in self.combat.mobs
        )
        is_boss_active = (self.combat.boss is not None and self.combat.boss.is_alive)
        is_grand_boss = isinstance(self.combat.boss, GrandBossSolRho)
        boss_phase = getattr(self.combat.boss, "phase", 1) if self.combat.boss else 1
        is_cavern = (self.player.center_y // SCALED_TILE) >= CAVERN_LEVEL
        self.bgm.update(
            dt, current_biome,
            has_nearby_threat=has_nearby_threat,
            is_boss_active=is_boss_active,
            boss_phase=boss_phase,
            is_grand_boss=is_grand_boss,
            is_night=self.sky.is_night,
            is_cavern=is_cavern
        )

        # Check Victory Trigger (Only slaying Grand Boss Sol-Rho Phase 2 triggers True Victory!)
        if getattr(self.combat, "trigger_victory", False) and self.menu.state == STATE_PLAYING:
            self.menu.state = STATE_VICTORY
            self.combat.trigger_victory = False
            self.sound_manager.play("craft")

        # Player Death Handling per Difficulty Mode
        if self.player.is_dead and not getattr(self.player, "_death_handled", False):
            self.player._death_handled = True
            if self.difficulty == DIFFICULTY_HARDCORE:
                for idx, slot in enumerate(self.inventory.slots):
                    if slot:
                        self.drop_item_into_world(slot.item_id, slot.count)
                        self.inventory.slots[idx] = None
                if self.inventory.held_item:
                    self.drop_item_into_world(self.inventory.held_item.item_id, self.inventory.held_item.count)
                    self.inventory.held_item = None
                for slot_name, eq_item_id in list(self.player.equipment.slots.items()):
                    if eq_item_id:
                        self.drop_item_into_world(eq_item_id, 1)
                        self.player.equipment.slots[slot_name] = None
                self.player.equipment.recalculate_stats(self.player.stats)
            elif self.difficulty == DIFFICULTY_YOLO:
                self.menu.state = STATE_GAME_OVER

        if not self.player.is_dead:
            self.player._death_handled = False

        # Last Man Standing / PvP Friendly Fire
        if self.game_mode == MODE_LAST_MAN_STANDING and self.client and self.client.connected:
            # 1. Projectiles PvP Friendly Fire
            for p in self.combat.projectiles:
                if p.life > 0:
                    for pid, rp in list(self.client.remote_players.items()):
                        rpx = float(rp.get("x", 0.0) if isinstance(rp, dict) else getattr(rp, "x", 0.0))
                        rpy = float(rp.get("y", 0.0) if isinstance(rp, dict) else getattr(rp, "y", 0.0))
                        rp_rect = pygame.Rect(rpx, rpy, self.player.width, self.player.height)
                        p_rect = getattr(p, "frect", getattr(p, "rect", None))
                        if p_rect and p_rect.colliderect(rp_rect):
                            p.life = 0
                            dmg = getattr(p, "damage", 20)
                            self.combat.spawn_damage_number(rpx + self.player.width / 2.0, rpy, dmg, color=(255, 60, 60))
                            self.particle_system.spawn_debris(rpx + self.player.width / 2.0, rpy + self.player.height / 2.0, (220, 50, 50), count=6)
                            self.sound_manager.play("hurt")
                            if isinstance(rp, dict) and "hp" in rp:
                                rp["hp"] = max(0, rp["hp"] - dmg)

            # 2. Melee Sword Swing PvP Friendly Fire
            if self.player.is_swinging and self.player.swing_progress < 0.65:
                reach = 48.0
                atk_rect = pygame.Rect(
                    self.player.center_x + (0 if self.player.facing_right else -reach),
                    self.player.y,
                    reach,
                    self.player.height
                )
                for pid, rp in list(self.client.remote_players.items()):
                    rpx = float(rp.get("x", 0.0) if isinstance(rp, dict) else getattr(rp, "x", 0.0))
                    rpy = float(rp.get("y", 0.0) if isinstance(rp, dict) else getattr(rp, "y", 0.0))
                    rp_rect = pygame.Rect(rpx, rpy, self.player.width, self.player.height)
                    dist = math.hypot(rpx + self.player.width / 2.0 - self.player.center_x, rpy + self.player.height / 2.0 - self.player.center_y)
                    if dist <= reach or atk_rect.colliderect(rp_rect):
                        hit_tracker = getattr(self.player, "_pvp_hit_players", set())
                        if pid not in hit_tracker:
                            hit_tracker.add(pid)
                            self.player._pvp_hit_players = hit_tracker
                            dmg = max(10, getattr(self.player.stats, "total_atk", getattr(self.player.stats, "attack", 10)))
                            self.combat.spawn_damage_number(rpx + self.player.width / 2.0, rpy, dmg, color=(255, 60, 60))
                            self.particle_system.spawn_debris(rpx + self.player.width / 2.0, rpy + self.player.height / 2.0, (220, 50, 50), count=6)
                            self.sound_manager.play("hurt")
                            if isinstance(rp, dict) and "hp" in rp:
                                rp["hp"] = max(0, rp["hp"] - dmg)
            else:
                self.player._pvp_hit_players = set()

            # 3. Fireball PvP Friendly Fire
            for fb in getattr(self.player, "fireballs", []):
                if getattr(fb, "life", 0) > 0:
                    fb_rect = pygame.Rect(fb.x - 8, fb.y - 8, 16, 16)
                    for pid, rp in list(self.client.remote_players.items()):
                        rpx = float(rp.get("x", 0.0) if isinstance(rp, dict) else getattr(rp, "x", 0.0))
                        rpy = float(rp.get("y", 0.0) if isinstance(rp, dict) else getattr(rp, "y", 0.0))
                        rp_rect = pygame.Rect(rpx, rpy, self.player.width, self.player.height)
                        if fb_rect.colliderect(rp_rect):
                            fb.life = 0
                            dmg = getattr(fb, "damage", 30)
                            self.combat.spawn_damage_number(rpx + self.player.width / 2.0, rpy, dmg, color=(255, 100, 30))
                            self.particle_system.spawn_debris(rpx + self.player.width / 2.0, rpy + self.player.height / 2.0, (255, 120, 40), count=8)
                            self.sound_manager.play("explosion")
                            if isinstance(rp, dict) and "hp" in rp:
                                rp["hp"] = max(0, rp["hp"] - dmg)

            # Check if all remote players are dead and local player is standing
            alive_remotes = [
                rp for rp in self.client.remote_players.values()
                if (rp.get("hp", 100) > 0 if isinstance(rp, dict) else getattr(rp, "hp", 100) > 0)
            ]
            if len(self.client.remote_players) > 0 and len(alive_remotes) == 0 and not self.player.is_dead:
                if not self.pvp_victor_banner:
                    self.pvp_victor_banner = "LAST TUBER STANDING! VICTORY!"
                    self.pvp_banner_timer = 10.0
                    self.sound_manager.play("craft")

        if self.pvp_banner_timer > 0:
            self.pvp_banner_timer -= dt
            if self.pvp_banner_timer <= 0:
                self.pvp_victor_banner = None

        # Collect dropped items (Full Inventory Bug Fix: leftover items stay floating on ground and never delete)
        for item in self.combat.dropped_items:
            if getattr(item, "picked_up", False):
                item_to_add = getattr(item, "item_stack", None) or item.item_id
                leftover = self.inventory.add_item(item_to_add, item.count)
                if leftover < item.count:
                    if item.item_id == "fallen_star":
                        self.achievement_manager.unlock("star_catcher")
                    from src.ui.inventory import ITEM_REGISTRY
                    item_info = ITEM_REGISTRY.get(item.item_id, {})
                    rarity = item_info.get("rarity", "")
                    if rarity == "ancient" or "ancient" in item.item_id:
                        self.achievement_manager.unlock("rarity_ancient")
                        if hasattr(self, "vfx_manager") and self.vfx_manager:
                            self.vfx_manager.spawn("ancient_discovery", self.player.center_x, self.player.center_y - 24, duration=1.5)
                        self.sound_manager.play("craft")
                        self.camera.add_shake(8.0, 0.4)
                        self.inventory.notify(f"ANCIENT RELIC DISCOVERED: {item_info.get('name', item.item_id)}!", timer=4.5)
                if leftover > 0:
                    item.count = leftover
                    item.picked_up = False
                if self.inventory.is_open:
                    self.crafting.update_recipes(self.inventory, self.world, self.player)
        self.combat.dropped_items = [it for it in self.combat.dropped_items if not getattr(it, "picked_up", False)]
        self.profiler.end_section("update_other")

        # 8. Dynamic Viewport 2D Lighting (Boundless horizontally)
        with self.profiler.section("update_lighting"):
            base_min_tx = int(self.camera.x // SCALED_TILE) - 1
            base_max_tx = int((self.camera.x + SCREEN_WIDTH) // SCALED_TILE) + 2
            base_min_ty = max(0, int(self.camera.y // SCALED_TILE) - 1)
            base_max_ty = min(self.world.height - 1, int((self.camera.y + SCREEN_HEIGHT) // SCALED_TILE) + 2)
            
            min_tx = base_min_tx - (base_min_tx % 4)
            max_tx = min_tx + (base_max_tx - base_min_tx) + 4
            min_ty = base_min_ty - (base_min_ty % 4)
            max_ty = min_ty + (base_max_ty - base_min_ty) + 4
            
            # Dynamic light sources: Miner Helmet, Torch, Radiance gear, and Glowing Projectiles
            extra_lights = []
            held_item = self.inventory.get_active_item()
            has_helmet = self.inventory.has_miner_helmet() or (self.player.equipment.slots.get(SLOT_HEAD) == "miner_helmet")
            has_radiance = (
                (hasattr(self.player, "equipment") and self.player.equipment.has_light_emitter())
                or (hasattr(self.player, "has_effect") and (
                    self.player.has_effect("light radiance")
                    or self.player.has_effect("celestial radiance")
                    or self.player.has_effect("astral sparkles")
                    or self.player.has_effect("supernova")
                ))
            )
    
            if has_helmet or has_radiance or (held_item and held_item.item_id in ("torch", "carved_tuber_lantern", "curved_tuber_lantern", "brass_lantern", "spectral_lantern")):
                ptx = int(self.player.center_x // SCALED_TILE)
                pty = int(self.player.center_y // SCALED_TILE)
                intensity = 15 if (has_helmet or has_radiance) else 14
                extra_lights.append((ptx, pty, intensity))
    
            # Dynamic light emitted by falling celestial stars and glowing arrows
            for p in self.combat.projectiles:
                if getattr(p, "life", 0) > 0:
                    pos = getattr(p, "pos", None)
                    if pos is not None:
                        px = getattr(pos, "x", None)
                        py = getattr(pos, "y", None)
                    else:
                        px = getattr(p, "x", None)
                        py = getattr(p, "y", None)
                    if px is not None and py is not None:
                        intensity = 15 if isinstance(p, CelestialStarProjectile) else 8
                        extra_lights.append((int(px // SCALED_TILE), int(py // SCALED_TILE), intensity))
    
            # Atmospheric tinting: Deep Nether Dungeon violet vs sky cycle
            if self.player.y > 200 * SCALED_TILE:
                ambient_tint = (1.14, 0.72, 1.28)
            else:
                ambient_tint = self.sky.atmospheric_tint
    
            self.lighting.compute_viewport_light(
                self.world, min_tx, min_ty, max_tx, max_ty,
                ambient_sunlight=self.sky.ambient_sunlight,
                torch_positions=extra_lights,
                ambient_tint=ambient_tint
            )

    def render(self):
        if hasattr(self, "renderer_manager"):
            self.renderer_manager.clear((0, 0, 0))
        elif hasattr(self, "screen") and self.screen:
            self.screen.fill((0, 0, 0))

        ui_surf = getattr(self, "ui_screen", None) or self.screen

        if self.menu.state != STATE_PLAYING:
            self.menu.render(ui_surf)
            if hasattr(self, "renderer_manager"):
                self.renderer_manager.present()
            else:
                pygame.display.flip()
            return

        # Layer 1: Parallax Sky & Celestial Bodies
        with self.profiler.section("render_sky"):
            self.sky.render(self.screen, self.camera)

        # Layer 2: World Tiles & Background Walls
        with self.profiler.section("render_world"):
            self.world.render(self.screen, self.camera, draw_water=False)

        # Layer 3: Particles & Debris
        with self.profiler.section("render_particles"):
            self.particle_system.render(self.screen, self.camera)

        # Layer 4: Mobs, Boss & Dropped Items
        with self.profiler.section("render_combat"):
            self.combat.render(self.screen, self.camera, renderer=getattr(self, "renderer", None))

        # Layer 4.5: Remote LAN Party Members
        if self.client and self.client.connected:
            self.client.render_remote_players(self.screen, self.camera, self.asset_factory)

        # Layer 4.8: Friendly Town NPCs & Villagers
        if hasattr(self.world, "render_town_npcs") and getattr(self.world, "town_npcs", None):
            self.world.render_town_npcs(self.screen, self.camera, player=self.player)

        # Layer 5: Spud the Potato Hero
        active_item = self.inventory.get_active_item()
        held_icon = self.asset_factory.items.get(active_item.item_id) if active_item else None
        self.player.render(self.screen, self.camera, held_item_icon=held_icon, held_item=active_item)

        # Layer 5.1: Fishing Line & Bobber
        if getattr(self, "fishing_bobber", None):
            bob = self.fishing_bobber
            bsx, bsy = self.camera.world_to_screen(bob["x"], bob["y"])
            psx, psy = self.camera.world_to_screen(self.player.center_x + (10 if self.player.facing_right else -10), self.player.center_y - 2)
            pygame.draw.line(self.screen, (220, 220, 220), (psx, psy), (bsx, bsy), 1)
            bob_r = 4
            pygame.draw.circle(self.screen, (240, 240, 240), (bsx, bsy + 2), bob_r)
            pygame.draw.circle(self.screen, (220, 40, 40), (bsx, bsy - 2), bob_r)
            pygame.draw.circle(self.screen, (20, 20, 20), (bsx, bsy), bob_r + 1, 1)
            if bob.get("state") == "bite":
                pygame.draw.circle(self.screen, (100, 200, 255), (bsx, bsy), bob_r + 6, 2)
                pulse = (pygame.time.get_ticks() // 250) % 2
                ex_col = (255, 235, 60) if pulse else (255, 90, 90)
                if getattr(self, "boss_font", None):
                    ex_surf = self.boss_font.render("!", True, ex_col)
                    self.screen.blit(ex_surf, (bsx - ex_surf.get_width() // 2, bsy - 34))
                if getattr(self, "font_fps", None):
                    rc_surf = self.font_fps.render("[RIGHT CLICK!]", True, (255, 255, 255))
                    bg_w, bg_h = rc_surf.get_width() + 6, rc_surf.get_height() + 2
                    bg_rect = pygame.Rect(bsx - bg_w // 2, bsy - 18, bg_w, bg_h)
                    pygame.draw.rect(self.screen, (15, 20, 30, 200), bg_rect, border_radius=3)
                    self.screen.blit(rc_surf, (bsx - rc_surf.get_width() // 2, bsy - 17))

        # Layer 5.2: Aquatic Foreground Water Pass
        self.world.render_water(self.screen, self.camera)

        # Layer 5.5: Grand Animated Visual Effects (Skills, Ancient Slashes, Explosions)
        if hasattr(self, "vfx_manager") and self.vfx_manager:
            self.vfx_manager.render(self.screen, self.camera)

        # Layer 6: Dynamic 2D Lighting Atmosphere
        # Pixel-perfect alignment matching world.render() integer rounding eliminates 1px seams
        with self.profiler.section("render_lighting"):
            cam_x = int(round(self.camera.x - self.camera.shake_offset_x))
            cam_y = int(round(self.camera.y - self.camera.shake_offset_y))
            min_tx = self.lighting._last_min_tx if self.lighting._last_min_tx is not None else (int(cam_x // SCALED_TILE) - 1)
            min_ty = self.lighting._last_min_ty if self.lighting._last_min_ty is not None else max(0, int(cam_y // SCALED_TILE) - 1)
            light_screen_x = min_tx * SCALED_TILE - cam_x
            light_screen_y = min_ty * SCALED_TILE - cam_y
            self.lighting.render_lighting(self.screen, light_screen_x, light_screen_y)

        # Layer 7: Floating Damage Numbers
        for dn in self.combat.damage_numbers:
            dn.render(ui_surf, self.camera, self.font)

        # Layer 8: Boss Health Bar (Centered at screen bottom so it never covers the fight)
        if self.combat.boss:
            self.combat.boss.render_boss_bar(ui_surf, self.boss_font, self.title_font)
        if getattr(self.combat, "secondary_boss", None):
            self.combat.secondary_boss.render_boss_bar(ui_surf, self.boss_font, self.title_font, bar_y=SCREEN_HEIGHT - 120)

        # Layer 9: HUD, Hotbar, Inventory, Reticle, Party, Minimap & Chat
        with self.profiler.section("render_hud"):
            mouse_x, mouse_y = self.get_mouse_pos()
            self.hud.render(
                ui_surf, self.player, self.inventory, self.crafting,
                self.camera, mouse_x, mouse_y, world=self.world, combat=self.combat, lan_client=self.client,
                render_dragged=False, sky=self.sky
            )

            # Layer 9.5: Character & Paperdoll Equipment Panel (Chroisen Style)
            if self.character_panel.is_open:
                self.character_panel.render(ui_surf, self.player, mouse_x, mouse_y)

            # Layer 9.6: Town NPC Dialogue & Shop Window
            if hasattr(self, "npc_dialogue") and self.npc_dialogue.is_open:
                self.npc_dialogue.render(ui_surf, self.player, self.inventory, mouse_x, mouse_y)

            # Layer 9.7: Storage Chest Window
            if hasattr(self, "chest_ui") and self.chest_ui.is_open:
                self.chest_ui.render(ui_surf, self.inventory, mouse_x, mouse_y, render_dragged=False)

            # Layer 9.75: Foreground Dragged Item (Always above Chest UI, Character Panel, and NPC Shop)
            if hasattr(self.hud, "render_dragged_item"):
                self.hud.render_dragged_item(ui_surf, self.inventory, mouse_x, mouse_y)

            # Layer 9.8: PvP Last Man Standing Victory Banner
            if self.pvp_victor_banner:
                bw, bh = 540, 52
                bx = SCREEN_WIDTH // 2 - bw // 2
                by = 40
                pygame.draw.rect(ui_surf, (30, 20, 10, 235), (bx, by, bw, bh), border_radius=10)
                pygame.draw.rect(ui_surf, (255, 215, 0), (bx, by, bw, bh), 2, border_radius=10)
                b_txt = self.title_font.render(self.pvp_victor_banner, True, (255, 230, 60))
                ui_surf.blit(b_txt, (SCREEN_WIDTH // 2 - b_txt.get_width() // 2, by + 10))

            # Layer 9.85: Fishing Battle Mini-Game UI
            if hasattr(self, "fishing_minigame") and (self.fishing_minigame.is_active or self.fishing_minigame.result is not None):
                self.fishing_minigame.render(ui_surf)

            # Layer 9.9: Mobile Virtual Touch Controls
            if hasattr(self, "touch_controller") and self.touch_controller.is_visible():
                self.touch_controller.render(ui_surf, self.player, self.inventory, self.camera, game=self)

        # Layer 10: Debug Overlay
        if self.show_debug:
            self._render_debug_overlay(target_surf=ui_surf)

        # Layer 10.2: Persistent Small-Text FPS Indicator (for performance debugging)
        self._render_fps_counter(target_surf=ui_surf)

        # Layer 10.5: In-Game Achievement Toasts
        if hasattr(self, "achievement_manager"):
            self.achievement_manager.render_toast(
                ui_surf, self.menu.font_title, self.menu.font_sub,
                self.asset_factory.ui.get("achievement_banner")
            )

        # Layer 11: Pause Menu Overlay
        if self.paused:
            self._render_pause_menu(target_surf=ui_surf)
        # Layer 12: Profiler Overlay
        if getattr(self, "show_profiler", False):
            self.profiler.render_overlay(ui_surf, self.font)

        if hasattr(self, "renderer_manager"):
            self.renderer_manager.present()
        else:
            pygame.display.flip()

    def _render_debug_overlay(self, target_surf=None):
        target = target_surf or getattr(self, "ui_screen", None) or self.screen
        fps = int(self.clock.get_fps())
        ptx = int(self.player.center_x // SCALED_TILE)
        pty = int(self.player.center_y // SCALED_TILE)
        tile_under = self.world.get_tile(ptx, pty + 2)
        has_helmet = (self.inventory.has_miner_helmet() or
                      self.player.equipment.slots.get("head") == "miner_helmet")
        lines = [
            f"POTARIA v1.0 | Dev: {DEVELOPER}",
            f"FPS: {fps} | World Seed: {self.world.seed}",
            f"Spud Pos: ({int(self.player.x)}, {int(self.player.y)}) | Tile: ({ptx}, {pty})",
            f"Ground Tile ID: {tile_under}",
            f"Level: {self.player.stats.level} | EXP: {self.player.stats.exp}/{self.player.stats.exp_to_next}",
            f"ATK: {self.player.stats.total_atk} | DEF: {self.player.stats.total_def} | Crit: {self.player.stats.crit_chance:.1f}%",
            f"Active Mobs: {len(self.combat.mobs)} | Boss Active: {self.combat.boss is not None}",
            f"LAN Connected: {self.client.connected if self.client else False} | Remote Players: {len(self.client.remote_players) if self.client else 0}",
            f"Miner Helmet Light: {has_helmet}"
        ]
        for i, l in enumerate(lines):
            txt = self.font.render(l, True, (255, 255, 255))
            pygame.draw.rect(target, (0, 0, 0, 180), (10, 80 + i * 20, txt.get_width() + 8, 18))
            target.blit(txt, (14, 80 + i * 20))

    def _render_fps_counter(self, target_surf=None):
        target = target_surf or getattr(self, "ui_screen", None) or self.screen
        fps = int(self.clock.get_fps())
        # Color coding: Green >= 55, Yellow >= 30, Red < 30
        if fps >= 55:
            color = (80, 240, 100)
        elif fps >= 30:
            color = (255, 215, 60)
        else:
            color = (255, 80, 80)
        txt = self.font_fps.render(f"FPS: {fps}", True, color)
        tw = txt.get_width()
        th = txt.get_height()
        # Clean small pill badge positioned unobtrusively at top-left above hotbar
        bx, by = 20, 3
        badge_rect = pygame.Rect(bx - 3, by - 1, tw + 6, th + 2)
        bg_surf = pygame.Surface((badge_rect.width, badge_rect.height), pygame.SRCALPHA)
        bg_surf.fill((16, 20, 30, 200))
        target.blit(bg_surf, badge_rect.topleft)
        pygame.draw.rect(target, (60, 75, 105, 200), badge_rect, 1, border_radius=3)
        target.blit(txt, (bx, by))

    def _render_pause_menu(self, target_surf=None):
        target = target_surf or getattr(self, "ui_screen", None) or self.screen
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 160))
        target.blit(overlay, (0, 0))

        # Pause modal box
        pw, ph = 420, 440
        px = SCREEN_WIDTH // 2 - pw // 2
        py = SCREEN_HEIGHT // 2 - ph // 2 - 10
        pygame.draw.rect(target, (28, 33, 48, 245), (px, py, pw, ph), border_radius=14)
        pygame.draw.rect(target, (255, 215, 0), (px, py, pw, ph), 2, border_radius=14)

        title = self.title_font.render("GAME PAUSED", True, (255, 215, 0))
        target.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, py + 18))

        mode_str = f"{self.active_world_name}  •  {self.difficulty.upper()}  •  {self.game_mode.replace('_', ' ').upper()}"
        sub = self.font.render(mode_str, True, (200, 210, 230))
        target.blit(sub, (SCREEN_WIDTH // 2 - sub.get_width() // 2, py + 52))

        for btn in self.pause_buttons:
            btn.render(target, self.menu.font_btn)
        for btn in getattr(self, "pause_extra_buttons", []):
            btn.render(target, self.menu.font_btn)
        for btn in self.save_buttons:
            btn.render(target, self.menu.font_btn)

if __name__ == "__main__":
    game = PotariaGame()
    game.run()
