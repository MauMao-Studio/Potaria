# Potaria Development Roadmap & Master Task Tracker

**Developer:** Kurados  
**Engine:** Pure Python 3.13 + Pygame-ce 2.5.8 (100% Offline Standalone)  
**Architecture:** Host-Authoritative 2D Sandbox Action RPG (Smart OpenGL HAL with Safe Fallback)  
**Test Suite Status:** 328 / 328 Tests Passing across 26 Test Suites (100% Green)  
**Current Version:** v1.7.0  
**Last Updated:** October 2026 (v1.7.0 Release)  

---

## Table of Contents
1. [Executive Summary & Current Baseline](#1-executive-summary--current-baseline)
2. [Completed Systems & Verified Milestones (v1.0 - v1.6)](#2-completed-systems--verified-milestones-v10---v16)
3. [Approved Hybrid Architecture & Cross-Platform Roadmap](#3-approved-hybrid-architecture--cross-platform-roadmap)
4. [Dual-Product Vision: Sandbox vs. Story Edition](#4-dual-product-vision-sandbox-vs-story-edition)
5. [Automated Verification & QA Matrix](#5-automated-verification--qa-matrix)

---

## 1. Executive Summary & Current Baseline

Potaria is a 2D sandbox action RPG combining the infinite terrain generation and digging/building mechanics of Terraria with the deep character progression, 40-skill roster, paperdoll equipment customization, and boss gauntlets of classic action RPGs.

The codebase is structured around modular, host-authoritative systems:
- `main.py`: Core game loop, event management, state machine, and HUD rendering.
- `src/world/`: Infinite procedural chunk generator (`chunk_manager.py`), tile physics, wall layers, and optimized cellular lighting engine (`lighting.py`).
- `src/rpg/`: Character leveling (1–100), EXP curves, equipment paperdoll slots, thematic armor set bonuses, radiant auras, and 40 skill books.
- `src/combat/`: Hitbox collision, damage mitigation, critical strikes, single-target combat enforcement, projectile ballistics, and bullet-hell danmaku patterns.
- `src/entities/trader.py`: Animated specialized traders (Wares, Enhance, Affix), turtle shell defenses, and 1-Gold repair mechanics.
- `src/ui/`: Minecraft-style 5-category crafting book (`crafting.py`), dedicated inventory (`inventory.py`), word-wrapped auto-hiding console, and touch control overlays.
- `src/network/`: Host-authoritative LAN socket server (`lan_server.py`) and client (`lan_client.py`) supporting 1–5 player cooperative sessions.
- `assets/craftable_items/`: Dedicated directory isolating all 129 craftable item sprites from droppable items.

---

## 2. Completed Systems & Verified Milestones (v1.0 - v1.6)

### 2.1 World Generation & Engine Optimization
- [x] **Boundless Open World**: Infinite horizontal coordinate generation without artificial boundary walls ($-\infty \leftarrow 0 \rightarrow +\infty$).
- [x] **Asynchronous Chunk Streaming**: Multi-threaded chunk synthesis prevents frame stalls during rapid player traversal.
- [x] **Chunk Surface Baking**: `ChunkSection` pre-renders static tiles to 16x16 chunk surfaces, reducing draw calls by >90%.
- [x] **Optimized Cellular Lighting**: 32-bit integer color mapping and `absorb_grid` cache reduce per-frame lighting calculations to 0.02ms.
- [x] **Torch Placement Physics**: Torches cannot float in mid-air or be placed underwater; they require a supporting solid block or background wall.
- [x] **Removal of Town Checks**: Town housing requirements and automated NPC checks removed from world update loops to preserve pure wilderness sandbox exploration.

### 2.2 RPG Systems, Equipment & Economy
- [x] **Chroisen Paperdoll Roster**: Head, Chest, Legs, Weapon, and 6 Accessory slots with active visual rendering.
- [x] **Thematic Armor Sets & Auras**: 3-piece set bonuses with glowing visual auras (Ancient Resonating, Celestial Titan, Magma Core, Cryo Carapace, Umbral Shadow, Spud Sovereign, Cactus Needle).
- [x] **Dedicated Coin Purse**: Currency moved out of 40-slot backpack into dedicated character status purse with auto-conversion (100 Copper = 1 Silver, 100 Silver = 1 Gold).
- [x] **Item Magnetism Safety**: Dropped items do not chase or hover around the player when inventory is full.
- [x] **Item Description Audit**: Verified non-empty, lore-rich descriptions across all registered catalog items.
- [x] **Rebalanced Leveling Curve**: Higher EXP scaling prevents rapid power spikes, ensuring meaningful progression across sessions.

### 2.3 Specialized Traders, Item Enhancements & Affixes
- [x] **Three Specialized Animated Traders**:
  - Zephyrion (Wares): Sells randomized weapons/equipment (Common to Epic) matching world drop rates.
  - Ignis Vance (Enhance): Upgrades gear from +1 to +7 and performs master repairs.
  - Morrigan (Affixes): Carves specialized affix slots on Legendary and Ancient gear using Affix Stones.
- [x] **Trader Spawn Rules**: Mutual exclusion (max 1 active trader), rare spawning far from player shelters, and limited duration.
- [x] **Turtle Shell Defense**: Traders retreat into an invulnerable shell when enemies are within 3 blocks (96 pixels), disabling trade until safe.
- [x] **1 Gold Gear Restoration**: Broken items (+5 to +7 failed enhancements) can be repaired by any trader for 1 Gold (10,000 Copper).
- [x] **Item Enhancement (+1 to +7)**:
  - +1..+4: Safe upgrades.
  - +5..+7: Failure chance breaks the item, requiring trader repair.
  - +7 doubles baseline weapon/armor stats (+100%).
- [x] **Affix Carving**: Consumes rare Affix Stones to replace a random secondary stat with a high-tier affix slot.

### 2.4 Combat, Ballistics & Bullet-Hell Bosses
- [x] **Single-Target Enforcement**: Melee swings and standard projectiles damage at most 1 target per attack.
- [x] **Ancient Relic Cleave & Pierce**: Ancient and Mythic weapons retain multi-target cleave and infinite piercing capabilities.
- [x] **Ballistic Archery**: Arrows follow parabolic gravity trajectories; four ammo types (Wooden, Flame, Frostburn, Astral).
- [x] **Magic Archetypes**: Catalysts (homing stars), Staves (elemental bolts), Rods (piercing javelins), Scepters (expanding shockwaves).
- [x] **Touhou-Inspired Bullet-Hell Bosses**:
  - Complex geometric danmaku patterns (16-way spiral novas, rotating cross beams, targeted rings).
  - Fair lethal core hitbox (52% radius) for micro-dodging.
  - Perimeter graze system (+1 MP reward and visual sparks when skimming close to bullets).
- [x] **Subterranean Mini-Boss Placement**: Mini-bosses restricted to underground dungeon arenas; surface night spawns eliminated.
- [x] **Nightly Elite Champion**: Single enlarged elite monster spawns once per night with enhanced stats and a unique combat skill.
- [x] **Bed Sleeping Proximity Check**: Sleeping restricted to nighttime with zero hostiles within 6 blocks (192 pixels).

### 2.5 Crafting, Inventory & UI/UX
- [x] **Minecraft-Style 5-Category Crafting Book**:
  - Category 1: Building Blocks.
  - Category 2: Equipment & Tools.
  - Category 3: Consumables & Alchemy.
  - Category 4: Furniture & Housing.
  - Category 5: Miscellaneous & Raw.
- [x] **129 Craftables Catalog**: Full catalog of craftable recipes across all categories.
- [x] **Dedicated Craftable Asset Folder**: All 129 craftable sprites stored exclusively in `assets/craftable_items/`.
- [x] **Craftable Storage Chests**: Multi-slot chests for world storage.
- [x] **Tool Tier Mining Speeds & Damage**: Harvesting speed scales with tool tier; tool combat damage reduced to prevent trivializing combat.
- [x] **Bare-Hand Harvesting**: Anti-softlock feature allowing punching wood and dirt at slow speeds without tools.
- [x] **Auto-Hiding Word-Wrapped Console**: Word-wrapped console and chat box that fades after inactivity.
- [x] **World Selection Tracking**: Displays accumulated playtime in hours and last played date.

---

## 3. Approved Smart OpenGL Architecture & Cross-Platform Roadmap

The approved technical strategy retains the 100% pure Python + Pygame-ce engine as the core simulation authority, layered with a Smart OpenGL / ModernGL Hardware Abstraction Layer (HAL) for maximum cross-platform performance (PC Steam and Google Play Android) with automatic fallback to software blitting.

### Stage 1: Renderer Hardware Abstraction Layer (HAL)
- **Objective**: Decouple game logic from direct Pygame blitting, provide hardware acceleration path with safe fallback, and persist renderer preferences.
- **Tasks**:
  - [x] Implement abstract `BaseRenderer` interface (`draw_sprite`, `draw_surface`, `draw_rect`, `draw_text`, `draw_line`, `draw_circle`, `clear`, `present`, `get_surface`, etc.).
  - [x] Implement `SurfaceRenderer` wrapping native Pygame-ce software blitting (default, 100% backward compatible).
  - [x] Implement `GLRenderer` with safe initialization, ModernGL / OpenGL context detection, texture caching, and automatic fallback to `SurfaceRenderer` when hardware acceleration is unavailable.
  - [x] Implement `RendererManager` holding active renderer, facilitating runtime switching, and wiring into `main.py`.
  - [x] Add configuration toggle in `saves/settings.json`: `"renderer": "hardware" | "software"`.
  - [x] Add in-game Video Settings toggle: `Renderer: [Hardware (ModernGL) / Compatibility (Software)]`.
  - [x] Verify all automated tests pass under HAL (`tests/test_renderer_hal.py`).

### Stage 2: Hardware Acceleration & ModernGL Visuals
- **Objective**: Harness desktop and mobile GPUs for high-density rendering, shaders, and visual effects.
- **Tasks**:
  - [ ] Hardware sprite batching for bullet-hell danmaku patterns (thousands of projectiles at 144+ FPS).
  - [ ] GLSL post-processing shaders: dynamic bloom for Ancient auras, celestial stars, and chromatic aberration on boss phases.
  - [ ] GLSL smooth lighting pass replacing CPU software blitting.
  - [ ] Seamless fallback: if OpenGL context fails to initialize on low-end hardware, automatically fall back to `SurfaceRenderer`.

### Stage 3: Steam PC Production Packaging
- **Objective**: Deliver a self-contained, high-performance desktop release for Windows and Linux (Steam Deck).
- **Tasks**:
  - [ ] Package standalone executable using Nuitka (C-compilation of Python source, eliminating Python interpreter overhead).
  - [ ] Embed SDL2 and asset bundles into single distribution directory.
  - [ ] Full Steam Deck and XInput/DirectInput gamepad controller support.
  - [ ] Steam Cloud save synchronization format verification.

### Stage 4: Google Play Android Packaging
- **Objective**: Deliver a responsive, touch-friendly mobile release on the Google Play Store.
- **Tasks**:
  - [ ] Configure Buildozer / python-for-android pipeline for ARM64 APK and AAB bundle builds.
  - [ ] Refine on-screen virtual joystick and action clusters (48x48px touch targets, haptic feedback).
  - [ ] Android lifecycle handling: pause on screen lock, background save state preservation.
  - [ ] Target Android 14+ (API Level 34) compliance with scoped storage.

---

## 4. Franchise Model: One Project Repository (Unified Codebase)

The franchise development strategy centers on a unified **One Project Repository** architecture with a clean profile/mode structure:

### Product Profile 1: Potaria (The Base Game)
- **Genre**: Boundless 2D Sandbox Survival Action RPG.
- **Inspirations**: Terraria, Starbound, Minecraft.
- **Core Loop**: Procedural exploration, mining, building, crafting 129 items, boss progression, open-ended survival freedom, casual LAN co-op, and Last Man Standing (LMS) PvP arena mode.
- **Distribution**: Steam PC and Google Play Android.

### Product Profile 2: Potaria: Root Realm (The Flagship ARPG Franchise)
- **Genre**: Story-Rich Narrative Action RPG Adventure.
- **Inspirations**: Minecraft: Story Mode, Chrono Trigger, Undertale.
- **Core Loop**:
  - Chapter-based episodic narrative following Spud, Pip the Guide, Barnaby the Merchant, Florencia the Nurse, and Russet the Blacksmith.
  - Heartroot world transformation mechanics reshaping corrupted zones into purified havens.
  - Comprehensive POTAdex journal documenting flora, fauna, and relics.
  - Handcrafted cinematic story levels, custom puzzle dungeons, and dramatic boss encounters.
  - Overhauled combat mechanics tailored for narrative battles, scripted set pieces, and dynamic camera choreography.
- **Distribution**: Flagship ARPG campaign on PC and mobile.

---

## 5. Automated Verification & QA Matrix

All development must maintain zero regressions across the test suite:

### Test Suite Execution Command:
```powershell
python -m unittest discover -s tests
```

### Verified Test Suites (26 Suites):
1. `tests/test_game.py` - Core engine integration and world loops.
2. `tests/test_new_features.py` - Early gameplay expansion tests.
3. `tests/test_lan_hud_mobs_scaling.py` - LAN networking and boss scaling.
4. `tests/test_gameplay_fixes.py` - Gameplay systems and tile physics.
5. `tests/test_reviewer_fixes.py` - Engine consistency checks.
6. `tests/test_water_oxygen_swimming.py` - Liquid physics and underwater oxygen.
7. `tests/test_achievements_and_polish.py` - Achievement tracking and unlock criteria.
8. `tests/test_furniture.py` - Furniture block placement, beds, and clocks.
9. `tests/test_cutscene_engine.py` - Prologue cutscene state flow and typewriter text.
10. `tests/test_inventory_coins_and_tools.py` - Dedicated coin purse and tool tiers.
11. `tests/test_voice_and_audio.py` - Procedural audio synthesis and synth voices.
12. `tests/test_mobile_controls.py` - Virtual joystick and touch control clusters.
13. `tests/test_combat_overhaul_and_cheats.py` - Bow ballistics, staves, rods, scepters, and cheat commands.
14. `tests/test_performance_and_profiler.py` - Performance baseline and F3 profiler metrics.
15. `tests/test_lighting_and_victory_fixes.py` - Cellular lighting optimization and victory screen.
16. `tests/test_wooden_sword.py` - Basic crafting and starter weapons.
17. `tests/test_tool_tier_and_bare_hand.py` - Bare-hand anti-softlock and tool harvest times.
18. `tests/test_item_descriptions_and_balance.py` - Item catalog descriptions and level curve balance.
19. `tests/test_single_target_combat.py` - Single-target melee and ballistic rules.
20. `tests/test_nightly_elite_and_dungeon_bosses.py` - Dungeon mini-bosses, bed proximity, and elite champion.
21. `tests/test_random_trader_and_features.py` - Animated traders, enhancement, affixes, and turtle shield.
22. `tests/test_crafting_categories_and_items.py` - 5-category crafting book and 129 items.
23. `tests/test_danmaku_bullet_hell.py` - Danmaku patterns, 52% hitbox core, and perimeter grazing.
24. `tests/test_traders_ui_and_torch_rules.py` - 3-block shield, shop hover UI, torch physics, and craftable asset folders.
25. `tests/test_world_bleed_multiplayer_effects_assets.py` - World isolation and multiplayer state preservation.
26. `tests/test_renderer_hal.py` - Renderer HAL, BaseRenderer, SurfaceRenderer, GLRenderer fallback, settings persistence, and mode switching.
