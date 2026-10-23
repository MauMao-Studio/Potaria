# Potaria Development Roadmap & Master Task Tracker

**Developer:** Kurados  
**Active Engine:** Unity 6 LTS (v6000.0.58f1) + 2D Universal Render Pipeline (URP)  
**Legacy Engine Branch:** Python 3.13 + Pygame-ce 2.5.8 (Preserved on `pygame-engine` branch, 100% Offline Standalone)  
**Architecture:** 2D Boundless Sandbox Action RPG & Multiplayer (FishNet / Steamworks P2P)  
**Verification Baseline:** 770 / 770 Pygame Tests Passing; 1,775 Unity ScriptableObjects Validated; 84 / 84 World Gen Tests Passing; 116 / 116 Combat Tests Passing; 57 / 57 Overhaul Systems Tests Passing (0 Errors)  
**Current Milestone:** Milestone 3 Complete (Character Controller, Physics, Combat, Day/Night Lighting, HUD & Localization); Milestone 4 in Progress (Inventory, Crafting, Equipment & Responsive UI)  
**Last Updated:** October 2026  

---

## Table of Contents
1. [Executive Summary & Engine Migration](#1-executive-summary--engine-migration)
2. [Completed Systems: Pygame Legacy Foundation (v0.1 - v0.2.9a)](#2-completed-systems-pygame-legacy-foundation-v01---v029a)
3. [Unity 6 LTS Master Implementation Roadmap](#3-unity-6-lts-master-implementation-roadmap)
   - [Milestone 1: Project Scaffold, Asset Ingestion & Core Data Layer (COMPLETED)](#milestone-1-project-scaffold-asset-ingestion--core-data-layer-completed)
   - [Milestone 2: 2D Tilemap, Chunk Streaming & Procedural World Generation](#milestone-2-2d-tilemap-chunk-streaming--procedural-world-generation)
   - [Milestone 3: Character Controller, Physics & Action RPG Combat](#milestone-3-character-controller-physics--action-rpg-combat)
   - [Milestone 4: Inventory, Crafting, Equipment & Responsive UI](#milestone-4-inventory-crafting-equipment--responsive-ui)
   - [Milestone 5: Philippine Farming, Tiered Cooking & Fishing Minigame](#milestone-5-philippine-farming-tiered-cooking--fishing-minigame)
   - [Milestone 6: Steamworks Integration & P2P / LAN Multiplayer](#milestone-6-steamworks-integration--p2p--lan-multiplayer)
   - [Milestone 7: Multiplatform Commercial Release (Steam & Google Play Store)](#milestone-7-multiplatform-commercial-release-steam--google-play-store)
4. [Dual-Product Vision: Sandbox Base Game vs. Flagship Story Edition](#4-dual-product-vision-sandbox-base-game-vs-flagship-story-edition)
5. [Automated Verification & QA Matrix](#5-automated-verification--qa-matrix)

---

## 1. Executive Summary & Engine Migration

Potaria is an authentic Philippine-themed 2D boundless sandbox action RPG combining the infinite terrain generation, mining, and building mechanics of Terraria with the deep character progression, 40-skill roster, paperdoll equipment customization, and boss gauntlets of classic action RPGs.

Following extensive architectural evaluation, the project has officially transitioned from the Python/Pygame prototype engine to **Unity 6 LTS (6000.0.58f1)** utilizing the **2D Universal Render Pipeline (URP)**. This migration unlocks:
- **High-Performance Execution**: C# compiled via IL2CPP into native 64-bit C++, eliminating Python's Global Interpreter Lock (GIL) and enabling high frame rates with thousands of active tiles, fluids, and projectiles.
- **Cinematic 2D Lighting**: Native 2D URP dynamic lights, normal-mapped sprites, shadows, and bloom running identically across PC and mobile GPUs.
- **Commercial Publishing**: Native Google Play App Bundle (`.aab`) export targeting Android 14+ (API 34) and official Steamworks integration (Steam Cloud, Achievements, Rich Presence) with zero antivirus false positives.
- **Seamless Multiplayer**: Steam P2P lobby invites via Valve's Steam Datagram Relay (SDR) with zero port forwarding, alongside local Wi-Fi LAN discovery.

The original Python codebase is preserved in its entirety on the `pygame-engine` branch and in a verified physical backup on disk.

---

## 2. Completed Systems: Pygame Legacy Foundation (v0.1 - v0.2.9a)

All foundational systems designed and proven during the Pygame prototype phase serve as the direct functional specification for the Unity 6 implementation:

### 2.1 World Generation & Physics
- [x] Boundless horizontal chunk streaming ($-\infty \leftarrow 0 \rightarrow +\infty$).
- [x] Sub-pixel floating point physics eliminating rounding jitter.
- [x] Water buoyancy, translucent submerged overlays, and 1 heart/sec drowning at 0% oxygen.
- [x] Support physics for light sources (torches require a solid adjacent block or background wall).
- [x] Individual block-by-block tree harvesting with leaf sapling drops.

### 2.2 RPG Systems, Equipment & Economy
- [x] Chroisen-style paperdoll roster: Head, Chest, Legs, Weapon, and 6 Accessory slots with active visual rendering.
- [x] 27 Equipment Sets with 2-piece, 4-piece, and 5-piece milestone passives (including Katipunero, Seven Deadly Sins, and Seven Heavenly Virtues).
- [x] Dedicated Coin Purse with automatic denomination conversion (100 Copper = 1 Silver, 100 Silver = 1 Gold).
- [x] Three animated nomadic traders (Zephyrion, Ignis Vance, Morrigan) with turtle-shell defense barriers and 1 Gold gear repair.
- [x] Item enhancement (+1 to +7) and affix carving using Affix Stones on high-tier gear.

### 2.3 Combat, Ballistics & Boss Gauntlets
- [x] Single-target melee and projectile damage enforcement (with Ancient relic cleave/pierce exceptions).
- [x] Ballistic archery with parabolic gravity arcs and 4 arrow types.
- [x] 4 Magic Archetypes: Catalysts (homing stars), Staves (elemental bolts), Rods (piercing javelins), Scepters (radial shockwaves).
- [x] Touhou-inspired danmaku bullet-hell patterns with 52% lethal core hitbox and perimeter graze system (+1 MP reward).
- [x] 4 Subterranean Dungeon Mini-Bosses and Two-Phase Grand Boss Sol-Rho the Celestial Titan.
- [x] Ancient skill `celestial_reversal` with timed projectile reflection (1.5x damage amplification).

### 2.4 Philippine Culinary & Farming Systems
- [x] 79 Authentic Filipino food and ingredient items with pure descriptive cultural notes.
- [x] 5-Meal active buff framework: strictly 1 active buff per category (Offense, Defense, Mobility, Resource, Utility) with stat caps.
- [x] 8 Native Philippine farming crops (Rice/Palay, Garlic, Onion, Ginger, Eggplant, String Beans, Tamarind, Calamansi) with 4-stage visual growth.
- [x] Bamboo and Iron Hoes, infinite Watering Can, 4-block horizontal water hydration radius, and cave torchlight illumination farming.
- [x] Tier-based cooking durations (2.5s to 20.0s) and direct Inihaw fish grilling on furnaces and campfires.
- [x] Fishing minigame with 12.0s urgency countdown timer, moving sweet-spot 1.5x reel bonus, and escape penalties.
- [x] 10 Native Philippine fish species (Bangus, Tilapia, Galunggong, Lapu-Lapu, Maya-Maya, Tanigue, Tambakol, Hito, Dilis, Dalagang Bukid).

---

## 3. Unity 6 LTS Master Implementation Roadmap

### Milestone 1: Project Scaffold, Asset Ingestion & Core Data Layer (COMPLETED)
- **Objective**: Establish the official Unity 6 LTS 2D URP project, migrate all visual/audio assets, and generate 100% typed ScriptableObjects.
- **Tasks**:
  - [x] Verify standalone duplicate backup on disk (`Potaria_Pygame_Backup`) with 770/770 tests passing.
  - [x] Detect installed Unity 6 version: **Unity 6000.0.58f1** (Unity 6 LTS Editor).
  - [x] Archive complete working Pygame codebase to `pygame-engine` branch and push to GitHub remote `origin`.
  - [x] Synchronize `pre-overhaul-backup` branch with latest Pygame commit (`ae12247`).
  - [x] Initialize Unity 6 project structure on `main` branch with `ProjectVersion.txt` set to `6000.0.58f1`.
  - [x] Configure `Packages/manifest.json` with 2D URP 17.0.3, 2D Tilemap, 2D Sprite, Input System, and TextMeshPro.
  - [x] Configure standard Unity `.gitignore` excluding `Library/`, `Temp/`, `Obj/`, `Build/`, `Logs/`, and user settings.
  - [x] Copy and organize 2,456 pixel-art PNG sprites into `Assets/Sprites/` (`Items/`, `Craftable_Items/`, `Tiles/`, `Mobs/`, `Projectiles/`, `Boss/`, `Branding/`).
  - [x] Configure texture import settings across all sprites: `TextureImporterType.Sprite`, `Filter Mode: Point (no filter)`, `Compression: None`, and `16 PPU`.
  - [x] Generate 36 growth stage sprites (4 stages each) for all 9 agricultural crops in `Assets/Sprites/Crops/`.
  - [x] Transfer 34 audio clips into `Assets/Audio/`.
  - [x] Implement C# data architectures in `Assets/Scripts/Data/`:
    - `ItemData.cs`, `ItemRarity.cs`, `ItemCategory.cs`
    - `FoodItemData.cs` and `FoodBuffData.cs` (79 Filipino dishes, cooking times, 14 buff stats across 5 meal categories)
    - `WeaponItemData.cs` and `EquipmentItemData.cs` (630 weapons, 705 armor and accessories)
    - `EquipmentSetData.cs` (27 sets with 147 piece links and 2/4/5-piece milestone passives)
    - `CropData.cs` (9 Philippine crops, growth stages 0-3, light and moisture rules)
    - `RecipeData.cs` (181 recipes with Hand, Furnace, and Campfire crafting stations)
  - [x] Implement automated Unity batchmode importer (`PotariaDataImporter.cs`) and execute headless generation.
  - [x] Verify serialization integrity: 1,775 ScriptableObject assets generated with 0 compilation errors and 100% valid icon and reference links.
  - [x] Commit and push Milestone 1 to `origin/main` (`6109f37`).

---

### Milestone 2: 2D Tilemap, Chunk Streaming & Procedural World Generation (COMPLETED)
- **Objective**: Implement the boundless procedural world in Unity using 2D Tilemaps, chunk streaming, and 2D URP lighting.
- **Tasks**:
  - [x] Configure Unity 2D Tilemap Grid hierarchy (Background Walls, Solid Blocks, Hazard/Deco Layer, Liquid Layer).
  - [x] Create Unity Tile assets and TileDatabase pipeline linking mined drops, hardness, tool type, and solid/platform collider rules.
  - [x] Configure `CompositeCollider2D` on solid block Tilemap (Geometry: Polygons, Used By Composite) for smooth platformer movement without snagging.
  - [x] Port procedural terrain generation from Python to C# (Perlin cave synthesis, ore distribution, surface hills, multi-tier dungeons).
  - [x] Implement asynchronous boundless chunk streaming, camera-based distance loading, and memory culling.
  - [x] Implement tile destruction, harvesting speeds based on tool tier, and bare-hand fallback punching.
  - [x] Implement 2D URP Dynamic Lighting: Global Light 2D cycling through Day/Night phases (Dawn, Noon, Sunset, Night), Subterranean Darkness depth attenuation, and Point Light 2D components for placed torches and lanterns.
  - [x] Implement 4-block horizontal water hydration simulation for farmland and cave torchlight crop illumination.
  - [x] Construct MainWorld sample scene (`Assets/Scenes/MainWorld.unity`) with Grid, Tilemaps, WorldManager, 2D Lights, and Pixel Perfect Camera (16 PPU).
  - [x] Verify via automated headless batchmode test runner (`PotariaWorldTest`) with 84/84 tests passing (0 errors).

---

### Milestone 3: Character Controller, Physics & Action RPG Combat (COMPLETED)
- **Objective**: Port player movement, paperdoll visual equipment rendering, 40 combat skills, and Touhou-inspired boss battles.
- **Tasks**:
  - [x] Implement 2D Rigidbody character controller with snappy acceleration, 1-block crouch/platform drop, coyote time (0.15s), variable jump height, water swimming, and drowning.
  - [x] Fix ground detection using downward BoxCastNonAlloc and multi-ray sweeps past foot boundary, contact normal detection for 45-degree slopes, and zero-friction physics material.
  - [x] Integrate Unity New Input System supporting keyboard/mouse, gamepad, and mobile touchscreen virtual controls, with dual-backend fallback.
  - [x] Build visual animated character system (12 FPS 8-frame walk, idle breathing, jump stretch, fall) with sprite facing flip and paperdoll hooks.
  - [x] Implement procedural Day/Night SkyRenderer2D with cubic Hermite gradient transitions, camera clear color sync, and 140 twinkling star sprites.
  - [x] Enable 2D dynamic shadow casting on point lights (torches at 0.70 intensity) and CompositeShadowCaster2D on foreground tilemap geometry.
  - [x] Implement complete In-Game HUD: 10-slot hotbar (slots 1-9, 0) with selection highlight and stack count, Life text and hearts, Mana bar and MP readout, 12-hour clock badge (e.g. 12:00 PM DAY, 7:04 PM NIGHT), Radar badge, 4 skill cooldown badges (Q, F, V, R), and F3 profiler overlay.
  - [x] Implement hostile mob behaviors: Green Slime and Purple Slime (hopping and squish/stretch), Surface Zombie (shambling with step-jumping over obstacles), and Night Gazer / Demon Eye (zero-gravity sinusoidal flight and daytime fleeing).
  - [x] Implement MobSpawner: 15-35 tile annulus around player, 10 active mob cap, and >60 tile despawn radius.
  - [x] Implement dual-language localization system (LocalizationManager) with instant runtime toggle ('L' key) between English (en) and Filipino (fil).
  - [x] Implement melee attack hitboxes, single-target damage enforcement, and Ancient relic cleave.
  - [x] Implement projectile ballistics: parabolic gravity arcs for arrows, homing logic for catalysts, piercing javelins, and shockwaves.
  - [x] Port RPG stat system: 100-level curve, EXP formula (100 * lvl^2.1), 5-meal buff slots with statutory caps, and natural MP regen (1.8 MP/s).
  - [x] Implement Touhou-inspired bullet-hell danmaku patterns for dungeon mini-bosses and Grand Boss Sol-Rho (16-way spiral novas, celestial cross beams, targeted rings with dodge corridors).
  - [x] Implement 52% lethal core hitbox and perimeter graze system (+1 MP reward and visual sparks).
  - [x] Implement Ancient skill `celestial_reversal` with timed projectile reflection (1.5x damage amplification and reflection budget).
  - [x] Implement CameraController with follow damping, 3 discrete zoom levels (1x, 2x, 3x via 'Z'), and 3.0s cinematic pitch-black death transition.
  - [x] Verify via automated headless batchmode test runner (`PotariaCombatTest`) with 116/116 tests passing (0 errors).
  - [x] Verify via automated overhaul test runner (`PotariaOverhaulTest`) with 57/57 tests passing (0 errors).


---

### Milestone 4: Inventory, Crafting, Equipment & Responsive UI
- **Objective**: Create clean, responsive UI with side-by-side gear comparison, crafting book, and mobile touch support.
- **Tasks**:
  - [ ] Set up Unity UI Toolkit / Canvas Scaler supporting 16:9, 18:9, 19.5:9, and 20:9 aspect ratios without distortion.
  - [ ] Build 40-slot backpack inventory with item stack dragging, splitting, and automatic `[ORGANIZE]` gap compaction.
  - [ ] Build dedicated coin purse UI with real-time Copper, Silver, and Gold auto-conversion.
  - [ ] Build 5-category crafting book with recipe filtering, search, and crafting station detection (Hand, Work Bench, Furnace, Campfire).
  - [ ] Build side-by-side equipment comparison tooltip ("katabi") showing hovered gear alongside equipped gear with `[ CURRENTLY EQUIPPED ]` badges.
  - [ ] Implement visual circular affix socket indicators (Empty socket and Filled socket indicators) adhering to item rarity limits.
  - [ ] Build bottom-left active food buff HUD overlay with hover tooltips and remaining duration meters.
  - [ ] Build mobile virtual touch controls (onscreen analog joystick, action clusters, touch target sizing).

---

### Milestone 5: Philippine Farming, Tiered Cooking & Fishing Minigame
- **Objective**: Port agricultural growth, timed furnace cooking, and reel tension fishing mechanics.
- **Tasks**:
  - [ ] Implement `CropTileComponent` handling 4-stage visual growth, hydration checks, and harvest yields for all 8 native Philippine crops.
  - [ ] Implement Bamboo and Iron Hoes for tilling soil, and infinite Watering Can for hydrating farmland.
  - [ ] Implement active cooking queues on furnaces and campfires (2.5s to 20.0s durations) with single-food active slot rules.
  - [ ] Implement direct fish grilling into Inihaw na [Fish] variants with authentic culinary descriptions.
  - [ ] Implement 5-meal active buff manager enforcing 1-buff-per-category rules and stat contribution caps.
  - [ ] Implement fishing minigame with 12.0s countdown timer, moving golden sweet-spot 1.5x bonus, tension meter, and escape penalties.

---

### Milestone 6: Steamworks Integration & P2P / LAN Multiplayer
- **Objective**: Implement seamless multiplayer networking via Steam P2P and local Wi-Fi LAN discovery.
- **Tasks**:
  - [ ] Integrate `FishNet` (or Unity Netcode for GameObjects) for authoritative multiplayer synchronization.
  - [ ] Integrate `Steamworks.NET` / `FishySteamworks` transport utilizing Valve's Steam Datagram Relay (SDR).
  - [ ] Implement zero-port-forwarding Steam friend invites (`Invite Friend` / `Join Game` via Steam overlay).
  - [ ] Implement local network broadcast discovery for offline LAN cooperative play.
  - [ ] Implement client-side prediction, entity interpolation, and lag compensation for smooth combat.
  - [ ] Implement Steam Cloud save synchronization format and Steam Achievements tracking.
  - [ ] Implement mobile-to-PC cross-play session connectivity via Unity Relay short room codes.

---

### Milestone 7: Multiplatform Commercial Release (Steam & Google Play Store)
- **Objective**: Package, optimize, and publish Potaria to Steam (PC/Steam Deck) and the Google Play Store (Android).
- **Tasks**:
  - [ ] Configure IL2CPP 64-bit compilation for Windows, Linux, and Android.
  - [ ] Verify Steam Deck compatibility (16:10 1280x800 resolution, full gamepad navigation, font readability).
  - [ ] Configure Android build pipeline: export signed Android App Bundle (`.aab`) targeting Android 14+ (API 34).
  - [ ] Implement Android lifecycle handling: pause on app switch, background save state preservation.
  - [ ] Performance profiling: maintain stable 60 FPS on mid-range Android devices and 120+ FPS on PC.
  - [ ] Store page preparation: localized trailers, screenshots, descriptions, and ratings submissions.

---

## 4. Franchise Model: One Project Repository

The repository houses the dual-profile franchise architecture:
1. **Potaria (The Base Game)**: Boundless 2D sandbox survival action RPG featuring procedural exploration, mining, building, 181 crafting recipes, boss gauntlets, and seamless co-op multiplayer on Steam and Google Play.
2. **Potaria: Root Realm (The Flagship ARPG)**: Episodic narrative action RPG campaign featuring handcrafted story levels, Heartroot world restoration mechanics, the POTAdex journal, and cinematic boss encounters.

---

## 5. Automated Verification & QA Matrix

Development across both engines maintains strict quality baselines:

### Pygame Legacy Verification (Archival):
- **Command**: `pytest -q`
- **Result**: 770 passed across 47 suites (100% Green).

### Unity 6 Verification (Active):
- **Headless Batchmode Importers**: `PotariaDataImporter.ImportAll` and `PotariaTileImporter.GenerateAllTileAssets` executed with exit code 0.
- **Reference Integrity**: 1,775 ScriptableObjects verified (0 missing icons, 0 broken recipe links, 0 unlinked equipment set pieces).
- **Tile Pipeline**: 73 block tiles, 13 wall tiles, TileDatabase registry, and procedural sprite synthesizers.
- **World Gen & Systems Verification**: `PotariaWorldTest.RunTests` executed with 84 / 84 tests passing (0 failed, 0 errors).
- **Combat & Character Physics Verification**: `PotariaCombatTest.RunTests` executed with 116 / 116 tests passing (0 failed, 0 errors).
- **Overhaul Systems Verification**: `PotariaOverhaulTest.RunTests` executed with 45 / 45 tests passing (0 failed, 0 errors).
- **Total Automated Unity Tests**: 245 / 245 tests passing (0 failed, 0 errors).
- **Compilation Status**: 0 errors, 0 warnings in `Assets/Scripts/`.
