"""
Potaria Documentation Generator - Section 6: Comprehensive Unity 6 Parity Audit Matrix
Developer: Kurados
Strict Constraints: NO emojis, relative paths only.
Audits ALL 65 Pygame reference engine files + developer tooling.
"""

def build_section_6():
    return """## 6. Comprehensive Unity 6 Parity Audit Matrix

This master matrix audits every single game subsystem, source file, mechanic, and architectural component across the entire Potaria franchise. All 65 Pygame-CE reference engine files (`main.py` and all 64 files in `src/*`) plus developer tooling are audited against their corresponding active Unity 6 LTS C# scripts in `Assets/Scripts/`.

Each entry documents its reference Pygame implementation, corresponding Unity 6 LTS C# script, verified implementation status (`[IMPLEMENTED]`, `[PARTIALLY IMPLEMENTED]`, or `[PENDING / NEED TO IMPLEMENT]`), verified functionality from Milestones 1-3, and the exact remaining porting backlog for Milestones 4-7.

### 6.1 Core Engine, Game Loop & Camera Architecture

| Subsystem / Feature | Pygame Reference (`src/...`) | Unity 6 Target Script (`Assets/Scripts/...`) | Parity Status | Implemented Functionality (Milestones 1-3) | Remaining Backlog (Milestones 4-7) |
|:---|:---|:---|:---|:---|:---|
| **Master Game Loop & States** | `main.py` | `Assets/Scripts/Player/PlayerController.cs`, `Assets/Scripts/UI/PotariaHUD.cs`, `Assets/Scripts/Editor/PotariaSceneBuilder.cs` | `[PARTIALLY IMPLEMENTED]` | Fixed timestep execution (0.02s physics), input dispatching, scene bootstrapping, runtime HUD lifecycle, hotbar execution. | World state machine transitions (Title -> World Select -> Gameplay -> Death -> Respawn) and developer cheat console (`execute_cheat`). |
| **Smooth Follow Camera** | `src/camera.py` | `Assets/Scripts/Camera/CameraController.cs` | `[IMPLEMENTED]` | Sub-pixel target damping, deadzone clamping, 3-level discrete zoom toggling (1x, 2x, 3x via Z key), instant camera snap, 3.0s pitch-black death transition. | Dynamic cinematic camera pans for boss intros. |
| **Real-Time F3 Profiler** | `src/profiler.py` | `Assets/Scripts/UI/PotariaHUD.cs` | `[IMPLEMENTED]` | Toggleable F3 overlay, live FPS calculation, frame time telemetry (ms), active chunk count, active mob count, player coordinates display. | Detailed pass-by-pass microsecond memory allocators breakdown. |
| **Settings & Audio/Video Persistence** | `src/settings_manager.py` | `Assets/Scripts/Localization/LocalizationManager.cs`, Planned `Assets/Scripts/Settings/SettingsManager.cs` | `[PARTIALLY IMPLEMENTED]` | Dynamic localization toggle ('L' key) between English and Filipino, volume normalization constants. | In-game Settings Menu UI modal (resolution switcher, borderless fullscreen toggle, BGM/SFX sliders). |
| **Master Constants & Type Registries** | `src/constants.py` | `Assets/Scripts/World/WorldConstants.cs`, `Assets/Scripts/Data/ItemCategory.cs`, `Assets/Scripts/Data/BuffCategory.cs`, `Assets/Scripts/Data/CraftingStation.cs` | `[IMPLEMENTED]` | 77 block tile IDs, 16x240 chunk dimensions, world layers (70/115/160/205), item categories, buff categories, crafting stations, UI palette colors. | Mod custom tile ID offset ranges. |

### 6.2 World Generation, Dual Tilemaps, Chunks & Storage

| Subsystem / Feature | Pygame Reference (`src/...`) | Unity 6 Target Script (`Assets/Scripts/...`) | Parity Status | Implemented Functionality (Milestones 1-3) | Remaining Backlog (Milestones 4-7) |
|:---|:---|:---|:---|:---|:---|
| **Procedural Terrain Synthesis** | `src/world/world_gen.py` | `Assets/Scripts/World/WorldGenerator.cs` | `[IMPLEMENTED]` | Multi-octave Perlin elevation, rolling surface hills, cave network carving, ore vein seeding (Copper, Iron, Gold), Nether dungeon brick chambers at Y >= 205. | Sky Citadels floating island generation. |
| **Deterministic Perlin Noise** | `src/world/noise.py` | `Assets/Scripts/World/PerlinNoise.cs` | `[IMPLEMENTED]` | Custom deterministic 2D Perlin noise engine, octave persistence, lacunarity, smooth gradient interpolation, seed hash permutation table. | Simplex 3D noise for 3D cloud layers. |
| **Infinite Chunk Streaming** | `src/world/chunk_manager.py` | `Assets/Scripts/World/ChunkManager.cs`, `ChunkData.cs` | `[IMPLEMENTED]` | Boundless horizontal streaming (-inf to +inf), 16x240 chunk dimensions, 3-chunk active radius, coordinate hash indexing, distant chunk eviction. | Asynchronous coroutine disk serialization. |
| **Dual Tilemap Layers & Colliders** | `src/world/world.py` | `Assets/Scripts/World/WorldTilemaps.cs` | `[IMPLEMENTED]` | Solid block Tilemap with CompositeCollider2D (Polygons), Background Wall Tilemap, zero-friction physics material, layer collision filtering. | Water surface displacement ripple shader. |
| **Tile Definition & Mining Registry** | `src/world/tiles.py` | `Assets/Scripts/World/TileDefinition.cs`, `TileDatabase.cs` | `[IMPLEMENTED]` | Tool tier validation (Pickaxe, Axe, Shovel, Bare Hand), hardness scaling, tool efficiency math, mined item drops, light opacity values. | Progressive block cracking break stage animation overlay. |
| **Tile Render Caching & Dirty Rects** | `src/world/world_cache.py` | Unity 2D Tilemap Renderer & URP Batching | `[IMPLEMENTED]` | Replaced by Unity's native C++ chunk mesh batching and GPU instanced Tilemap rendering, eliminating Python dirty-rect blits. | Custom chunk mesh collider rebaking optimizations. |
| **Multi-Layer World Save Engine** | `src/world/save_manager.py` | Planned `Assets/Scripts/Save/SaveManager.cs` | `[PENDING / NEED TO IMPLEMENT]` | JSON schemas documented, tile coordinate serialization schemas defined. | Atomic file writes (`world.json.tmp` -> `world.json`), rolling snapshot backup rotations, HMAC-SHA256 signature verification (Milestone 4). |
| **Storage Chest Tile Entity** | `src/world/storage_chest.py` | `Assets/Scripts/World/TileDatabase.cs`, Planned `Assets/Scripts/World/StorageChestComponent.cs` | `[PARTIALLY IMPLEMENTED]` | TileChest (28) and TileIronChest (55) registered, placement validation rules. | Tile entity component tracking 20 inventory slots per placed chest, renaming modal, break-to-drop logic (Milestone 4). |
| **Subterranean Darkness & Attenuation**| `src/world/lighting.py` | `Assets/Scripts/World/Lighting/SubterraneanDarkness2D.cs`, `PointLightSource2D.cs` | `[IMPLEMENTED]` | Quadratic depth attenuation below Y = 85, pitch-black illumination at cavern depths (Y >= 160), 2D dynamic point lights for torches and lanterns. | Cavern ambient dust motes particle overlay. |

### 6.3 Player Kinematics, Locomotion & Physics

| Subsystem / Feature | Pygame Reference (`src/...`) | Unity 6 Target Script (`Assets/Scripts/...`) | Parity Status | Implemented Functionality (Milestones 1-3) | Remaining Backlog (Milestones 4-7) |
|:---|:---|:---|:---|:---|:---|
| **Kinematic Locomotion & Run Accel** | `src/entities/player.py` | `Assets/Scripts/Player/PlayerController.cs` | `[IMPLEMENTED]` | Rigidbody2D interpolated movement, 6.0 run speed, 40.0 acceleration, 32.0 deceleration, velocity clamping, facing flip. | Sprint stamina drain hook in Hardcore mode. |
| **Snag-Free Platforming Jump** | `src/entities/player.py` | `Assets/Scripts/Player/PlayerController.cs` | `[IMPLEMENTED]` | 12.0 jump force, 0.45x variable jump cut multiplier, 0.15s coyote time, 0.12s jump buffer, 0.08s jump grace timer on slope release. | Double jump wings accessory passive hook. |
| **Slope & Ground Detection** | `src/entities/player.py` | `Assets/Scripts/Player/PlayerController.cs` | `[IMPLEMENTED]` | BoxCastNonAlloc downward sweep, 45-degree slope normal detection, zero-friction material preventing ledge snagging. | Footstep dust particle bursts on hard landing. |
| **One-Way Platform Drop-Through** | `src/entities/player.py` | `Assets/Scripts/Player/PlayerController.cs` | `[IMPLEMENTED]` | S / Down input sets 0.25s collision bypass, dropping hero through wooden platforms and scaffolding. | Immediate ground snapping upon landing on lower surface. |
| **Liquid Buoyancy & Swimming** | `src/entities/player.py` | `Assets/Scripts/Player/PlayerController.cs` | `[IMPLEMENTED]` | 0.88x horizontal drag, 0.90x vertical drag, 0.25x gravity reduction, paddle upward / dive downward swimming. | Water splash sound and particle bursts on entry/exit. |
| **Oxygen Meter & Drowning Damage** | `src/entities/player.py` | `Assets/Scripts/Player/PlayerController.cs` | `[IMPLEMENTED]` | 100.0 max oxygen, 7.5/s submerged drain, 40.0/s surfacing replenish, 1 heart/s true damage at 0% oxygen bypassing DEF. | Bubble HUD meter readout above player head. |
| **12 FPS Animated Spud Potato** | `src/entities/player.py` | `Assets/Scripts/Player/PlayerController.cs` | `[IMPLEMENTED]` | 8-frame walk cycle, idle breathing, jump stretch, fall sprite, sprite facing flip, decorative sprout offset. | Armor sprite paperdoll rendering overlay. |
| **Cinematic Death & Snap Respawn** | `src/entities/player.py` | `Assets/Scripts/Player/PlayerController.cs`, `CameraController.cs` | `[IMPLEMENTED]` | 3.0s cinematic pitch-black fade, instant camera snap, spawn point teleportation, health restoration. | Boss item drop penalty in Hardcore mode. |

### 6.4 Combat Engine, Danmaku Bullet-Hell, Ballistics & Boss AI

| Subsystem / Feature | Pygame Reference (`src/...`) | Unity 6 Target Script (`Assets/Scripts/...`) | Parity Status | Implemented Functionality (Milestones 1-3) | Remaining Backlog (Milestones 4-7) |
|:---|:---|:---|:---|:---|:---|
| **Melee Combat & Weapon Swing Arc** | `src/combat/combat_system.py` | `Assets/Scripts/Combat/WeaponController.cs` | `[IMPLEMENTED]` | Swing duration (0.10s-0.45s), weapon attack cooldowns based on weapon tier, weapon aim angle tracking, mouse swing trigger. | Visual slash particle crescent trail. |
| **Single-Target Combat Enforcement** | `src/combat/combat_system.py` | `Assets/Scripts/Combat/WeaponController.cs` | `[IMPLEMENTED]` | Single-target hit registry per swing, Ancient relic cleave (`hasCleave`) exception for multi-target hits. | Floating damage number text integration. |
| **Mob Spawner Annulus & Caps** | `src/combat/combat_system.py` | `Assets/Scripts/Mob/MobSpawner.cs` | `[IMPLEMENTED]` | 15-35 tile spawn annulus, 10 active mob cap, >60 tile despawn radius, daytime mob suppression. | Subterranean biome mob spawn tables. |
| **Ballistic Parabolic Archery** | `src/entities/projectile.py` | `Assets/Scripts/Combat/Projectile.cs`, `ProjectileManager.cs` | `[IMPLEMENTED]` | Parabolic gravity trajectory (`vy += 9.8 * 0.44 * dt`), rotation facing velocity vector, 4 arrow types. | Arrow retrieval from terrain blocks. |
| **Magic Projectile Archetypes** | `src/entities/projectile.py` | `Assets/Scripts/Combat/Projectile.cs`, `ProjectileManager.cs` | `[IMPLEMENTED]` | Catalyst homing stars, Staff elemental splash bolts, Rod piercing javelins, Scepter radial shockwaves. | Mana depletion deduction on cast. |
| **Danmaku Novas & Curtains** | `src/entities/bullet_hell.py` | `Assets/Scripts/Combat/DanmakuEmitter.cs` | `[IMPLEMENTED]` | 16-way spiral novas, rotating celestial cross beams, targeted rings with navigable dodge corridors. | Criss-cross wave curtains pattern. |
| **52% Core Lethal Hitbox** | `src/entities/bullet_hell.py` | `Assets/Scripts/Combat/Projectile.cs` | `[IMPLEMENTED]` | Precise 52% central core lethal hitbox (`radius * 0.52`), eliminating edge clipping deaths. | Hitbox debug visualizer in F3 mode. |
| **Perimeter Bullet Graze System** | `src/entities/bullet_hell.py` | `Assets/Scripts/Combat/Projectile.cs`, `PlayerStats.cs` | `[IMPLEMENTED]` | 100%-175% outer radius graze detection, +1 MP reward, graze chime audio, and cyan spark feedback. | Graze counter badge in In-Game HUD. |
| **Celestial Reversal Reflection** | `src/entities/bullet_hell.py` | `Assets/Scripts/Player/PlayerController.cs` | `[IMPLEMENTED]` | 0.45s timed reflection window, 15 bullet budget, 1.5x damage amplification, boss target inversion. | Golden solar flare shockwave VFX. |
| **Boss Titans State Machines** | `src/entities/boss.py` | `Assets/Scripts/Combat/BossController.cs` | `[PARTIALLY IMPLEMENTED]` | BossController with Phase 1 & 2 transitions, player scaling, health bar UI, and danmaku emitter hooks. | Standalone state machines for Malus, Ignis, Cryo, Necro, and Grand Boss Sol-Rho (Milestone 4). |
| **Mob AI: Slimes, Zombies, Eyes** | `src/entities/mob.py` | `Assets/Scripts/Mob/SlimeMob.cs`, `ZombieMob.cs`, `DemonEyeMob.cs`, `Mob.cs` | `[IMPLEMENTED]` | Green and Purple slimes (squish hop), Zombie (horizontal step jump), Demon Eye (sinusoidal nocturnal flight). | BatMob and CaveBat variants (Milestone 4). |
| **Philippine Livestock Mobs** | `src/entities/mob.py` | Planned `Assets/Scripts/Mob/` | `[PENDING / NEED TO IMPLEMENT]` | Meat ingredient ScriptableObjects imported. | Manok, Pato, Baboy, Kalabaw, Kambing mob AI and drops (Milestone 5). |
| **Mythological Aswang Mob** | `src/entities/mob.py` | Planned `Assets/Scripts/Mob/` | `[PENDING / NEED TO IMPLEMENT]` | None. | High-speed nocturnal predator AI, wall leaping, lifesteal bites (Milestone 4). |
| **Dropped Items & World Physics** | `src/entities/dropped_item.py`| Planned `Assets/Scripts/World/DroppedItem.cs` | `[PARTIALLY IMPLEMENTED]` | ItemData ScriptableObjects with drop tables; physical toss arc math defined. | Physical DroppedItem GameObject with pickup magnet radius (Milestone 4). |
| **Particle System & Debris** | `src/entities/particle.py` | `Assets/Scripts/Player/PlayerController.cs`, `Combat/WeaponController.cs` | `[PARTIALLY IMPLEMENTED]` | Graze cyan sparks, melee hit feedback, damage effects. | Unified 2D particle system pool for block breaking and dust (Milestone 4). |
| **Visual Effects & Screen Trauma** | `src/entities/vfx.py` | `Assets/Scripts/Combat/DanmakuEmitter.cs`, `PlayerController.cs` | `[PARTIALLY IMPLEMENTED]` | Camera screen trauma shake, graze chime, death pitch-black fade. | Radial golden shockwave explosions for boss defeats (Milestone 4). |

### 6.5 Town NPCs, Housing Settlement & Nomadic Traders

| Subsystem / Feature | Pygame Reference (`src/...`) | Unity 6 Target Script (`Assets/Scripts/...`) | Parity Status | Implemented Functionality (Milestones 1-3) | Remaining Backlog (Milestones 4-7) |
|:---|:---|:---|:---|:---|:---|
| **Town NPCs & Room Assignment** | `src/entities/npc.py` | Planned `Assets/Scripts/NPC/TownNPCController.cs` | `[PENDING / NEED TO IMPLEMENT]` | Tile definitions for furniture, doors, tables, and chairs. | Guide, Merchant, Nurse, Blacksmith spawn logic, housing room occupancy assignment (Milestone 4). |
| **Housing Validity Room Check** | `src/world/world.py`, `npc.py` | Planned `Assets/Scripts/World/HousingDetector.cs` | `[PENDING / NEED TO IMPLEMENT]` | Room check rules documented (15-250 tiles, door, light, table, chair, solid walls). | Flood-fill housing algorithm in Unity C# (Milestone 4). |
| **Nomadic Animated Traders** | `src/entities/npc.py` | Planned `Assets/Scripts/NPC/TraderController.cs` | `[PENDING / NEED TO IMPLEMENT]` | Trader ware catalogs imported into ScriptableObjects. | Zephyrion, Ignis Vance, Morrigan spawn logic, turtle shell invulnerability defense, shop UI (Milestone 4). |
| **Forge Master 1 Gold Repair** | `src/entities/npc.py`, `rpg/enhancement.py` | Planned `Assets/Scripts/UI/ForgeMasterUI.cs` | `[PENDING / NEED TO IMPLEMENT]` | Repair formulas verified (1 gold for broken +1 to +7 items). | Interactive repair shop interaction modal (Milestone 4). |

### 6.6 Action RPG Progression, Stats & Enhancement

| Subsystem / Feature | Pygame Reference (`src/...`) | Unity 6 Target Script (`Assets/Scripts/...`) | Parity Status | Implemented Functionality (Milestones 1-3) | Remaining Backlog (Milestones 4-7) |
|:---|:---|:---|:---|:---|:---|
| **100-Level RPG Progression** | `src/rpg/stats.py` | `Assets/Scripts/RPG/PlayerStats.cs`, `CharacterStats.cs` | `[IMPLEMENTED]` | Level 1-100 curve, EXP formula `int(100 * lvl^2.1)`, stat scaling per level (+15 HP, +8 MP, +3 ATK, +1 DEF), level-up heal. | Level-up golden fanfare particle flare. |
| **Damage Mitigation & DEF Caps** | `src/rpg/stats.py` | `Assets/Scripts/RPG/PlayerStats.cs`, `CharacterStats.cs` | `[IMPLEMENTED]` | Physical mitigation formula, 85% defense cap, 15% min pierce, Titan's Resolve (3x DEF under 30% HP). | Armor penetration reduction math. |
| **Dedicated Coin Purse** | `src/rpg/stats.py` | `Assets/Scripts/RPG/PlayerStats.cs` | `[IMPLEMENTED]` | 100c = 1s, 100s = 1g auto-conversion, purchasing power integer representation, coin deduction methods. | Dedicated coin purse visual slot in backpack UI. |
| **40 Action Combat Skills** | `src/rpg/skills.py` | `Assets/Scripts/Input/PotariaInput.cs`, `Assets/Scripts/UI/PotariaHUD.cs` | `[PARTIALLY IMPLEMENTED]` | 4 skill HUD badges and keyboard triggers mapped (Power Slash, Whirlwind, Dash, Celestial Guard). | Full 40-skill casting engine, projectile spawns, and status effect application (Milestone 4). |
| **Chroisen 10-Slot Paperdoll** | `src/rpg/equipment.py` | `Assets/Scripts/Data/EquipmentItemData.cs`, `Assets/Scripts/RPG/PlayerStats.cs` | `[PARTIALLY IMPLEMENTED]` | 705 armor/accessory ScriptableObjects generated and validated across 10 paperdoll slots. | Interactive 10-slot paperdoll visual inventory UI with slot dragging (Milestone 4). |
| **27 Progressive Equipment Sets** | `src/rpg/equipment_update.py`| `Assets/Scripts/Data/EquipmentSetData.cs` | `[PARTIALLY IMPLEMENTED]` | 27 EquipmentSetData ScriptableObjects with piece links and 2/4/5-piece milestone thresholds. | Runtime equipment set count evaluation and active visual auras in combat (Milestone 4). |
| **Item Enhancement (+1 to +7)** | `src/rpg/enhancement.py` | `Assets/Scripts/Data/ItemData.cs`, Planned `Assets/Scripts/UI/ForgeMasterUI.cs` | `[PENDING / NEED TO IMPLEMENT]` | Stat multiplier formula defined, success/break rate curves documented. | Forge Master UI, enhancement success/break risk roller, 1 Gold repair interaction (Milestone 4). |
| **Affix Slot Carving & Stones** | `src/rpg/enhancement.py` | `Assets/Scripts/Data/ItemData.cs`, Planned `Assets/Scripts/UI/AffixCarvingUI.cs` | `[PENDING / NEED TO IMPLEMENT]` | `MAX_ADDITIONAL_AFFIX_SLOTS` limits verified, socket capacities mapped. | Morrigan Void Weaver carving UI, Affix Stone application, circular socket indicators (Milestone 4). |
| **Dynamic Affix System** | `src/rpg/affix_system.py` | `Assets/Scripts/Data/ItemData.cs`, `Assets/Scripts/RPG/PlayerStats.cs` | `[PARTIALLY IMPLEMENTED]` | Affix stat definitions and socket limits mapped; stat modifiers defined. | Dynamic affix stat computation on equipped items in combat (Milestone 4). |
| **In-Game Achievements Engine** | `src/rpg/achievements.py` | Planned `Assets/Scripts/RPG/AchievementManager.cs` | `[PARTIALLY IMPLEMENTED]` | Achievement catalog JSON schema preserved; unlock requirements defined. | In-game achievement toast banner and Steam achievements hook (Milestone 6). |

### 6.7 Loot Tables, Item Registry & Rarity Systems

| Subsystem / Feature | Pygame Reference (`src/...`) | Unity 6 Target Script (`Assets/Scripts/...`) | Parity Status | Implemented Functionality (Milestones 1-3) | Remaining Backlog (Milestones 4-7) |
|:---|:---|:---|:---|:---|:---|
| **Global Master Item Registry** | `src/loot/item_registry.py` | `Assets/Scripts/World/TileDatabase.cs`, `Assets/Scripts/Editor/PotariaDataImporter.cs` | `[IMPLEMENTED]` | 1,775 ScriptableObject items registered with category, rarity, icon, description, and stats. | Dynamic modded item runtime registration. |
| **7-Tier Rarity Engine** | `src/loot/rarity_engine.py` | `Assets/Scripts/Data/ItemRarity.cs` | `[IMPLEMENTED]` | Rarity enum, hex colors, drop weights, and stat multipliers across Common to Ancient. | Procedural prefix/suffix affix roller on dropped items. |
| **Affix Engine & Rollers** | `src/loot/affix_engine.py` | `Assets/Scripts/Data/ItemRarity.cs`, `Assets/Scripts/Data/ItemData.cs` | `[PARTIALLY IMPLEMENTED]` | Rarity multiplier tables and affix caps defined. | Weighted procedural affix selection on newly generated loot (Milestone 4). |
| **Loot System & Drop Evaluator** | `src/loot/loot_system.py` | Planned `Assets/Scripts/Combat/LootDropper.cs` | `[PARTIALLY IMPLEMENTED]` | Drop chance data imported into ItemData; drop tables loaded. | Physical dropped item instantiation on mob and boss death (Milestone 4). |
| **Loot Package Exports** | `src/loot/__init__.py` | `Assets/Scripts/Data/` | `[IMPLEMENTED]` | Unified namespace exports for items, weapons, equipment, sets, and food. | None. |

### 6.8 Philippine Culinary, Agriculture & Fishing Minigame

| Subsystem / Feature | Pygame Reference (`src/...`) | Unity 6 Target Script (`Assets/Scripts/...`) | Parity Status | Implemented Functionality (Milestones 1-3) | Remaining Backlog (Milestones 4-7) |
|:---|:---|:---|:---|:---|:---|
| **5-Meal Buff Framework** | `src/entities/player.py` | `Assets/Scripts/RPG/MealBuffManager.cs`, `MealBuffCaps.cs` | `[IMPLEMENTED]` | 5 concurrent categories (Offense, Defense, Mobility, Resource, Utility), 1-per-category replacement rules, countdown timer tick. | Active meal buff HUD tray overlay with radial fill countdown. |
| **19 Statutory Meal Caps** | `src/entities/player.py` | `Assets/Scripts/RPG/MealBuffCaps.cs` | `[IMPLEMENTED]` | Hard caps across damage mult (12%), atk speed (10%), crit (6%), defense (+6), magic res (15%), move speed (15%), etc. | Tooltip notification when food buff hits cap. |
| **Philippine Food Catalog (79)** | `src/ui/inventory.py` | `Assets/Scripts/Data/FoodItemData.cs`, `FoodBuffData.cs` | `[IMPLEMENTED]` | 79 authentic Filipino dishes and ingredients imported into typed ScriptableObjects with cultural notes. | Cooking queue UI on Campfires and Furnaces (Milestone 5). |
| **Agricultural Soil Hydration** | `src/world/world.py` | `Assets/Scripts/World/TileDatabase.cs` | `[IMPLEMENTED]` | Farmland and Hydrated Farmland tile definitions, 4-block horizontal water hydration simulation. | Hoe tilling and Watering Can actions (Milestone 5). |
| **8 Native Philippine Crops** | `src/world/world.py` | `Assets/Scripts/Data/CropData.cs` | `[PARTIALLY IMPLEMENTED]` | 9 Crop ScriptableObjects, 36 growth stage sprites (stages 0-3) in `Assets/Sprites/Crops/`. | Runtime `CropTileComponent` on tilemap with daily growth stages (Milestone 5). |
| **2D Fishing Battle Minigame** | `src/ui/fishing_minigame.py` | ScriptableObjects in `Assets/Items/` | `[PENDING / NEED TO IMPLEMENT]` | 10 Philippine fish ScriptableObjects imported into project. | 15.0s urgency timer modal, line tension meter, sweet spot bonus, thrashing fish AI (Milestone 5). |

### 6.9 User Interface, In-Game HUD, Inventory & Comparison

| Subsystem / Feature | Pygame Reference (`src/...`) | Unity 6 Target Script (`Assets/Scripts/...`) | Parity Status | Implemented Functionality (Milestones 1-3) | Remaining Backlog (Milestones 4-7) |
|:---|:---|:---|:---|:---|:---|
| **In-Game HUD & 10 Hotbars** | `src/ui/hud.py` | `Assets/Scripts/UI/PotariaHUD.cs` | `[IMPLEMENTED]` | 10-slot hotbar, selection frame, Life text/hearts, Mana bar, clock badge, radar badge, 4 skill badges. | Hover tooltips and active item dragging. |
| **Side-by-Side Comparison ('Katabi')**| `src/ui/hud.py` | `Assets/Scripts/UI/PotariaHUD.cs` | `[PENDING / NEED TO IMPLEMENT]` | Tooltip lines builder and measurement logic defined. | Side-by-side 'katabi' candidate vs equipped dual cards, screen boundary clamping (Milestone 4). |
| **40-Slot Backpack Grid UI** | `src/ui/inventory.py` | Planned `Assets/Scripts/UI/InventoryUI.cs` | `[PARTIALLY IMPLEMENTED]` | Inventory data architecture in PlayerStats; item slot models verified. | Drag-and-drop item visual grid, item splitting, trash slot, auto-sort (Milestone 4). |
| **Chroisen Character Panel UI** | `src/ui/character_panel.py` | Planned `Assets/Scripts/UI/CharacterPanelUI.cs` | `[PARTIALLY IMPLEMENTED]` | Backend PlayerStats ready; attribute points formula mapped. | 10-slot paperdoll visual window, stat readouts, attribute point spend buttons (Milestone 4). |
| **5-Tab Crafting Book UI** | `src/ui/crafting.py` | `Assets/Scripts/Data/RecipeData.cs`, Planned `Assets/Scripts/UI/CraftingUI.cs` | `[PARTIALLY IMPLEMENTED]` | 80+ RecipeData ScriptableObjects validated; station requirements defined. | 5-tab crafting window (All, Building, Equipment, Furniture, Survival), crafting queue (Milestone 4). |
| **Storage Chest Modal UI** | `src/ui/chest_ui.py` | Planned `Assets/Scripts/UI/ChestUI.cs` | `[PARTIALLY IMPLEMENTED]` | Chest item models verified; inventory transfer logic defined. | 20-slot storage chest UI, shift-click auto-deposit, chest renaming modal (Milestone 4). |
| **NPC Dialogue Bubble & Shop UI** | `src/ui/npc_dialogue.py` | Planned `Assets/Scripts/UI/NPCDialogueUI.cs` | `[PENDING / NEED TO IMPLEMENT]` | NPC dialogue text dictionaries imported. | Typewriter text dialogue bubble, fast-forward click, shop goods display grid (Milestone 4). |
| **Prologue Cutscene Engine** | `src/ui/cutscene.py` | Planned `Assets/Scripts/UI/CutsceneUI.cs` | `[PENDING / NEED TO IMPLEMENT]` | Cutscene narration texts and voice assets imported. | Letterbox cinema bars, typewriter dialogue, sprite staging, scene skipping (Milestone 4). |
| **Main Menu & World Generator UI**| `src/ui/menu.py` | Planned `Assets/Scripts/UI/MainMenuUI.cs` | `[PARTIALLY IMPLEMENTED]` | SceneBuilder scaffolds title sequence; world parameters mapped. | Title screen, world selection, new world parameter configurator (Finite/Infinite, Biome) (Milestone 4). |
| **Minimap Radar & Fog of War** | `src/ui/minimap.py` | `Assets/Scripts/UI/PotariaHUD.cs` | `[PARTIALLY IMPLEMENTED]` | Radar badge and cardinal directions in HUD; player coordinate tracker. | Full terrain tilemap texture radar with fog of war revelation (Milestone 4). |
| **Mobile Virtual Touch Controller** | `src/ui/touch_controller.py` | `Assets/Scripts/Input/PotariaInput.cs` | `[PARTIALLY IMPLEMENTED]` | Cross-platform input mapping hooks; virtual simulation tested. | Onscreen virtual touch joystick, action button clusters, touch gesture recognition (Milestone 4). |
| **UI Color Palette & Styling** | `src/ui/theme.py` | `Assets/Scripts/UI/PotariaHUD.cs` | `[IMPLEMENTED]` | Authentic Potaria palette, UI dark background, gold text highlights, white border outlines. | Dynamic UI theme switching. |

### 6.10 Atmospheric Lighting, Celestial Day/Night & Sky Renderer

| Subsystem / Feature | Pygame Reference (`src/...`) | Unity 6 Target Script (`Assets/Scripts/...`) | Parity Status | Implemented Functionality (Milestones 1-3) | Remaining Backlog (Milestones 4-7) |
|:---|:---|:---|:---|:---|:---|
| **720s Celestial Day/Night Cycle** | `src/environment/sky.py` | `Assets/Scripts/World/Lighting/DayNightCycle2D.cs` | `[IMPLEMENTED]` | 720.0s day duration, 4 distinct phases (Dawn, Noon, Sunset, Night), ambient light attenuation, clock badge. | Seasonal weather events (monsoon rain). |
| **Procedural Cubic Hermite Sky** | `src/environment/sky.py` | `Assets/Scripts/World/Lighting/SkyRenderer2D.cs` | `[IMPLEMENTED]` | Procedural cubic Hermite sky gradient transitions, camera clear color sync, 140 twinkling star sprites. | Sun and moon celestial orbit sprites. |
| **Biome Sky Gradient Presets** | `src/environment/sky_presets.py`| `Assets/Scripts/World/Lighting/SkyRenderer2D.cs` | `[IMPLEMENTED]` | Forest, Desert, Snow, Cavern, Nether sky color curves mapped into URP volume transitions. | Blight biome corrupted sky tinting. |

### 6.11 Audio Synthesis, Biome BGM & Narrator Speech

| Subsystem / Feature | Pygame Reference (`src/...`) | Unity 6 Target Script (`Assets/Scripts/...`) | Parity Status | Implemented Functionality (Milestones 1-3) | Remaining Backlog (Milestones 4-7) |
|:---|:---|:---|:---|:---|:---|
| **Procedural SFX & Head Bump Sound**| `src/audio/sound_effects.py` | `Assets/Scripts/Player/PlayerController.cs` | `[PARTIALLY IMPLEMENTED]` | Head unblocked jump sound suppression ported; 34 audio clips ingested into `Assets/Audio/`. | Spatial 2D audio emitters for mob sounds and ambient cavern drips (Milestone 4). |
| **Dynamic Biome BGM Manager** | `src/audio/bgm_manager.py` | Planned `Assets/Scripts/Audio/BGMManager.cs` | `[PARTIALLY IMPLEMENTED]` | Music tracks imported; volume normalization constants established. | Dynamic biome BGM crossfader with seamless looping (Milestone 4). |
| **Prologue Narrator Voice Speech** | `src/audio/narrator_voice.py` | Planned `Assets/Scripts/Audio/NarratorVoice.cs` | `[PARTIALLY IMPLEMENTED]` | Narrator voice wav assets ingested; phoneme blip generators ready. | Cutscene narrator audio sequencer and typewriter phoneme player (Milestone 4). |

### 6.12 Rendering HAL & Multiplatform Shaders

| Subsystem / Feature | Pygame Reference (`src/...`) | Unity 6 Target Script (`Assets/Scripts/...`) | Parity Status | Implemented Functionality (Milestones 1-3) | Remaining Backlog (Milestones 4-7) |
|:---|:---|:---|:---|:---|:---|
| **Rendering HAL Module Namespace** | `src/rendering/__init__.py` | 2D Universal Render Pipeline (URP 17.0.3) | `[IMPLEMENTED]` | Pure Python HAL abstraction replaced by Unity's native multiplatform render pipeline. | None. |
| **Abstract Base Renderer** | `src/rendering/base_renderer.py`| 2D Universal Render Pipeline (URP 17.0.3) | `[IMPLEMENTED]` | Replaced by Unity's native C++ rendering pipeline. | None. |
| **ModernGL Hardware Renderer** | `src/rendering/gl_renderer.py` | 2D URP Volume Post-Processing | `[IMPLEMENTED]` | Bloom, vignette, color adjustments, and 2D dynamic shadow rendering mapped to URP volume components. | Water reflection distortion custom render pass. |
| **Renderer Manager HAL Switcher**| `src/rendering/renderer_manager.py`| Unity Quality Settings | `[IMPLEMENTED]` | Superseded by Unity's automatic platform graphics API selection (DirectX 11/12, Vulkan, Metal). | Quality level selector in Settings Menu. |
| **Software Surface Renderer** | `src/rendering/surface_renderer.py`| 2D Universal Render Pipeline (URP 17.0.3) | `[IMPLEMENTED]` | Replaced by hardware-accelerated 2D URP on all devices, eliminating software CPU pixel rendering. | None. |

### 6.13 Modding, DLC Architecture & Multiplayer Networking

| Subsystem / Feature | Pygame Reference (`src/...`) | Unity 6 Target Script (`Assets/Scripts/...`) | Parity Status | Implemented Functionality (Milestones 1-3) | Remaining Backlog (Milestones 4-7) |
|:---|:---|:---|:---|:---|:---|
| **Modding Architecture Namespace** | `src/modding/__init__.py` | Planned `Assets/Scripts/Modding/` | `[PENDING / NEED TO IMPLEMENT]` | Architecture specifications documented. | Dynamic ScriptableObject mod loader (Milestone 6). |
| **Mod Manifest & Content Loader** | `src/modding/mod_manager.py` | Planned `Assets/Scripts/Modding/ModManager.cs` | `[PENDING / NEED TO IMPLEMENT]` | Manifest JSON parsing schemas preserved. | Runtime AssetBundle and ScriptableObject content pack injector (Milestone 6). |
| **Multiplayer Client Network Loop** | `src/network/client.py` | Planned `Assets/Scripts/Network/NetworkClient.cs` | `[PENDING / NEED TO IMPLEMENT]` | Packet specifications documented. | FishNet / Steamworks P2P networking client (Milestone 6). |
| **Binary Network Protocol** | `src/network/protocol.py` | Planned `Assets/Scripts/Network/NetworkProtocol.cs` | `[PENDING / NEED TO IMPLEMENT]` | Packet types (JOIN, SYNC, MOVE, BLOCK_BREAK, BLOCK_PLACE, CHAT) defined. | ByteBuf binary network serializer (Milestone 6). |
| **Authoritative LAN Server** | `src/network/server.py` | Planned `Assets/Scripts/Network/NetworkServer.cs` | `[PENDING / NEED TO IMPLEMENT]` | Host server architecture documented. | Authoritative multiplayer server loop in FishNet (Milestone 6). |

### 6.14 Asset Generation & Projectile Factories

| Subsystem / Feature | Pygame Reference (`src/...`) | Unity 6 Target Script (`Assets/Scripts/...`) | Parity Status | Implemented Functionality (Milestones 1-3) | Remaining Backlog (Milestones 4-7) |
|:---|:---|:---|:---|:---|:---|
| **Asset Factory Sprite Slicing** | `src/assets/asset_factory.py` | `Assets/Scripts/Editor/PotariaTileImporter.cs` | `[IMPLEMENTED]` | 2,456 PNG sprites sliced with 16 PPU, Point filtering, and uncompressed RGBA32 format. | Automated atlas packing optimizations. |
| **Projectile Sprite Factory** | `src/assets/projectile_factory.py`| `Assets/Scripts/Combat/Projectile.cs`, `Assets/Items/Weapons/` | `[IMPLEMENTED]` | Projectile sprites sliced and assigned to WeaponItemData ScriptableObjects. | Animated projectile trails. |
| **Projectile Library Generator** | `tools/generate_projectile_asset_library.py` | `Assets/Scripts/Editor/PotariaDataImporter.cs` | `[IMPLEMENTED]` | JSON metadata library ingested into Unity ScriptableObjects. | None. |
| **Parallax Background Generator** | `tools/generate_background_assets.py` | `Assets/Sprites/Environment/` | `[IMPLEMENTED]` | Parallax mountain and tree layers generated and imported. | Multi-layer camera parallax scroller script. |

### 6.15 Benchmarking & Developer Tooling

| Subsystem / Feature | Pygame Reference (`src/...`) | Unity 6 Target Script (`Assets/Scripts/...`) | Parity Status | Implemented Functionality (Milestones 1-3) | Remaining Backlog (Milestones 4-7) |
|:---|:---|:---|:---|:---|:---|
| **Headless Benchmark Suite** | `benchmark.py`, `scripts/benchmark_baseline.py` | Unity Profiler & Profile Analyzer | `[IMPLEMENTED]` | Unity native profiling tools provide deep CPU, GPU, and memory telemetry. | Automated CI performance regression benchmark. |
| **PixelArray Manipulation Profile**| `profile_pixelarray.py` | Unity 2D URP Shaders | `[IMPLEMENTED]` | Direct GPU shaders replace CPU PixelArray color tinting and water distortion. | None. |
| **Lighting Performance Benchmark** | `test_lighting_perf.py` | `Assets/Scripts/World/Lighting/PointLightSource2D.cs` | `[IMPLEMENTED]` | Verified 2D URP dynamic lights operate at 60+ FPS with zero CPU overhead. | None. |
| **Surface Smoothscale Benchmark** | `test_smoothscale.py` | Unity Sprite Renderer & PPU Scaling | `[IMPLEMENTED]` | Hardware texture filtering supersedes Pygame software smoothscale. | None. |
| **Item Catalog Generation Script**| `scripts/generate_items.py` | `Assets/Scripts/Editor/PotariaDataImporter.cs` | `[IMPLEMENTED]` | Generates 1,775 ScriptableObject assets directly from canonical JSON data. | None. |
| **Lore & Description Enricher** | `scripts/enrich_item_descriptions.py` | `Assets/Scripts/Editor/PotariaDataImporter.cs` | `[IMPLEMENTED]` | Enriched cultural lore and descriptions preserved in all ScriptableObjects. | None. |
| **Cookbook Documentation Builder** | `scripts/build_cookbook_docs.py` | `docs/POTARIA_COOKBOOK_GUIDE.md` | `[IMPLEMENTED]` | All 79 recipes documented with culinary notes and buff values. | In-game recipe discovery ledger. |

---
"""

if __name__ == "__main__":
    print("docs_section6 ready.")
