# Potaria Project Deliverables & System Milestones

**Developer:** Kurados  
**Active Engine:** Unity 6 LTS (v6000.0.58f1) + 2D Universal Render Pipeline (URP 17.0.3)  
**Legacy Engine Branch:** Pure Python 3.13 + Pygame-ce 2.5.8 (Preserved on `pygame-engine` branch, 100% Offline Standalone)  
**Franchise Model:** One Project Repository (Unified Codebase with Dual-Profile Architecture)  
**Verification Baseline:** 770 / 770 Pygame Tests Passing (100% Green); 1,775 Unity ScriptableObjects Validated via Batchmode (0 Errors)  
**Current Milestone:** Milestone 3 Complete (Character Controller, Physics & Action RPG Combat); Milestone 4 in Progress  
**Current Version:** Unity 6 LTS Milestone 3  

---

## 1. Executive Deliverables Summary

Potaria is an authentic Philippine-themed 2D boundless sandbox action RPG combining boundless procedural terrain generation with deep character customization, paperdoll equipment slots, 40 combat skills, bullet-hell boss encounters, animated specialized traders, item enhancement and affixes, Philippine farming and cooking, and cooperative multiplayer.

### Engine Architecture & Commercial Migration:
To deliver maximum performance, native multiplatform export (Steam PC, Steam Deck, Google Play Store), and seamless peer-to-peer / LAN multiplayer:
- **Active Development (`main` branch)**: Implemented in **Unity 6 LTS (v6000.0.58f1)** utilizing the 2D Universal Render Pipeline (URP 17.0.3), 2D Tilemap system, C# ScriptableObject data layer, and FishNet / Steamworks P2P networking.
- **Legacy Foundation (`pygame-engine` branch)**: The complete, working Python 3.13 + Pygame-ce game with Smart OpenGL HAL, 770 automated regression tests, and full gameplay loop is permanently preserved on the `pygame-engine` branch.

The franchise operates under a unified **One Project Repository** architecture, cleanly separating the boundless sandbox base game ("Potaria") from the narrative campaign flagship ("Potaria: Root Realm"). All data, sprites, and item logic are synchronized across both engines.

---

## 2. Core Feature Deliverables Matrix

### 2.1 Specialized Animated Traders & Settlement Economy
- **Three Unique Animated Traders**:
  - **Zephyrion the Wandering Peddler**: Wares trader selling up to 5 randomized weapons and equipment (rarities Common to Epic, aligned with world drop rates).
  - **Ignis Vance the Forge Master**: Specialized item enhancer offering gear upgrades from +1 to +7, and master equipment restoration.
  - **Morrigan the Void Weaver**: Mystic enchantress offering affix slot carving on Legendary and Ancient gear using rare Affix Stones.
- **Mutual Exclusion & Rarity**: Only one trader may appear in the world at any given time. Spawns are rare, temporary (limited duration), and occur away from player camps to encourage world exploration.
- **Turtle Shell Shield Defense**: When any hostile entity is within a 3-block radius (96 pixels), the trader withdraws into an invulnerable turtle shell defense barrier, preventing damage and disabling trade interactions until the perimeter is secured.
- **1 Gold Gear Restoration**: Broken items (+5 to +7 failed enhancements) can be fully repaired by any trader for a flat fee of 1 Gold Coin (10,000 Copper).
- **Interactive Shop UI**: Hover tooltips display comprehensive gear stats, comparisons, affix descriptions, and enhancement levels identical to backpack inventory inspection.

### 2.2 Touhou-Inspired Bullet-Hell Boss Mechanics
- **Geometric Danmaku Bullet Patterns**: Bosses and subterranean mini-bosses execute intricate multi-wave projectile patterns:
  - 16-way expanding spiral novas.
  - Rotating celestial cross beams.
  - Targeted bullet rings with micro-gaps.
  - Alternating curved trajectory waves.
- **Fair Lethal Hitbox (52% Core)**: Projectile collision uses a precise central core hitbox (52% of visual radius), eliminating unfair edge clippings and rewarding precise micro-dodging.
- **Perimeter Graze System**: Grazing close to lethal enemy projectiles (within 100% to 175% of radius) triggers a visual graze spark, audio feedback, and awards +1 Mana (MP), incentivizing skilled evasive maneuvers.

### 2.3 Item Enhancement & Affix Carving Systems
- **Item Enhancement (+1 to +7)**:
  - Weapons and equipment can be upgraded up to +7 at the Forge Master.
  - Success rates follow a strategic risk curve (100% at +1..+2, 85% at +3, 65% at +4, 45% at +5, 30% at +6, 18% at +7).
  - Enhancing scales baseline stats significantly (up to +100% / double stats at +7).
  - Risk Curve: Levels +1 to +4 are safe. Levels +5 to +7 carry a risk of breaking the item, rendering it unusable until repaired by a trader for 1 Gold.
  - Crafting materials for enhancement require rare subterranean ores and boss essences.
- **Affix Slot Carving**:
  - Exclusive to Legendary and Ancient rarity items.
  - Consumes an Affix Stone (crafted at the Work Bench using rare diamonds, mythic dust, and boss remnants).
  - Replaces a randomly selected existing secondary stat with an Affix Slot granting specialized offensive or defensive traits.

### 2.4 Minecraft-Style 5-Category Crafting Book & 129 Craftables Catalog
- **Categorized Crafting Navigation**:
  - 1. **Building Blocks**: Wooden planks, stone bricks, dungeon bricks, glass windows, roof shingles, platforms.
  - 2. **Equipment & Tools**: Swords, bows, composite bows, pickaxes, axes, shovels, armor pieces.
  - 3. **Consumables & Alchemy**: Potions, cooked meals, mashed potatoes, golden french fries, ammo arrows.
  - 4. **Furniture & Housing**: Tables, chairs, beds, bookshelves, clocks, fireplaces, dressers, chests.
  - 5. **Miscellaneous & Raw**: Affix stones, portal shards, ingots, refined textiles, mechanical gears.
- **Craftable Chests**: Craftable wooden and reinforced chests offering limited storage slots for persistent item management.
- **Dedicated Asset Architecture**: All 129 craftable item sprites are strictly organized in a dedicated project directory (`assets/craftable_items/`), cleanly separated from the 1,337 droppable item assets (`assets/items/`).

### 2.5 Combat Rebalance & Single-Target Rules
- **Single-Target Enforcement**: Melee swings and standard ballistic projectiles damage at most 1 enemy per attack, preventing low-tier starter weapons from clearing entire swarms in a single swing.
- **Ancient Relic Multi-Target Exceptions**: Only Ancient and Mythic tier weapons (e.g. Celestial Greatsword, Ancient Composite Bow, Astral Wrath) possess cleave, piercing, and area-of-effect multi-target capabilities.
- **Subterranean Mini-Boss Placement**: Mini-bosses are restricted to underground dungeons and dedicated lairs. Random surface spawns at night are eliminated.
- **Nightly Elite Champion**: A single, enlarged elite monster spawns once per night with enhanced health (2.5x-3.5x), custom title, and an exclusive combat skill.
- **Bed Proximity Safety Check**: Sleeping in a bed is only permitted at night when no hostile monsters are within a 6-block radius (192 pixels).

### 2.6 Environment Physics & World Quality of Life
- **Torch Support Physics**: Torches cannot float in mid-air or be placed underwater. They require an adjacent supporting solid block or a background wall.
- **Auto-Hiding Word-Wrapped Console & Chat**: In-game chat and command output format with automatic word wrapping in an unobtrusive box, fading out after a configurable delay to preserve screen real estate.
- **World Selection History**: World selection UI displays total accumulated playtime in hours and the exact timestamp of the last played session.

### 2.7 Renderer Hardware Abstraction Layer (HAL) & Stage 2 ModernGL Visuals
- **BaseRenderer Abstract Interface**: Defines standardized drawing contracts (`draw_sprite`, `draw_surface`, `draw_rect`, `draw_text`, `draw_line`, `draw_circle`, `clear`, `present`, `get_surface`, `set_mode`, `draw_projectiles_batch`) decoupling game logic from graphical backends.
- **SurfaceRenderer**: High-performance native Pygame-ce software blitting engine providing 100% exact parity with legacy rendering.
- **GLRenderer**: ModernGL / OpenGL accelerated renderer featuring safe context detection, texture caching, and automatic fallback to `SurfaceRenderer` upon initialization failure or missing libraries.
- **GLSL Bloom Post-Processing Pipeline**: Stage 2 custom fragment shader implementing dynamic luminance extraction, 2D Gaussian kernel blur, and radiant pulse shimmer for Ancient weapon/armor radiant visual auras, celestial star trails, and boss danmaku projectiles.
- **High-Density Projectile Batch Rendering**: `draw_projectiles_batch` on `GLRenderer`, `SurfaceRenderer`, and `RendererManager` optimizing hundreds of active bullet-hell projectiles in a single pass using C-level multi-blitting (`fblits`) with viewport frustum culling.
- **Single-Log Fallback Deduplication**: Automatic safety fallback warnings are logged only once via `_logged_fallback`, completely eliminating console spam on game startup and world reloads.
- **Configurable Shader Uniforms**: Clean uniform controls (`set_bloom_enabled`, `set_bloom_intensity`, `set_bloom_threshold`, `get_bloom_params`) across hardware and software backends.
- **RendererManager & Dynamic Toggle**: Centralized manager providing real-time backend switching, state-preserving bloom parameter retention, and user preference persistence in `saves/settings.json`.
- **In-Game Video Settings Integration**: Interactive toggles in Video Settings (`Renderer: [Hardware (ModernGL) / Compatibility (Software)]` and `Bloom Shaders: [BLOOM SHADERS: ON / OFF]`) with disk persistence in `saves/settings.json`.

### 2.8 Franchise Architecture: One Project Repository (Dual-Profile)
- **Unified Codebase**: Both profiles share common world simulation, physics, networking, and item registries.
- **Profile 1 - Potaria (Base Game)**: Boundless sandbox, 129 crafting recipes, building, open-ended survival, casual LAN co-op, and LMS arena mode.
- **Profile 2 - Potaria: Root Realm (Flagship ARPG)**: Episodic narrative chapters, Heartroot world transformation, POTAdex journal, and handcrafted puzzle dungeons.

### 2.9 Data-Driven Loot, Rarity & Multi-Affix System (Phase 1) & Visual Catalogs
- **Standardized Item Registry (`src/loot/item_registry.py`)**: Wraps all 1,461 registered items (including all 129 craftable recipes and 1,337+ droppable items) into canonical `ItemDefinition` schemas across 9 categories (`weapon`, `armor`, `accessory`, `consumable`, `material`, `ammunition`, `skillbook`, `quest_key`, `relic`) while maintaining 100% backward compatibility with `ITEM_REGISTRY`, world saves, and `/give`.
- **4-Layer Item Model (`src/loot/affix_engine.py`, `src/loot/rarity_engine.py`)**: Constructs item instances via `BASE ITEM + AFFIXES + RARITY + OPTIONAL UNIQUE EFFECT`, supporting dynamic prefix/suffix naming (e.g., `Vampiric Swift Iron Broadsword`), deterministic seeded rolling (`rng_seed`), category compatibility, rarity gating, and mutual exclusion (`Burning` excludes `Frozen`, `Swift` excludes `Heavy`, `Rootbound` excludes `Blighted`).
- **9 Canonical Affixes (`data/affixes/affixes.json`)**: `Vampiric`, `Burning`, `Frozen`, `Swift`, `Heavy`, `Piercing`, `Rootbound`, `Astral`, `Blighted`, plus thematic suffixes (`of the Root`, `of the Blight`, `of the Cosmos`, `of the Vanguard`).
- **3-Path Loot Acquisition (`src/loot/loot_system.py`, `data/loot_tables/loot_tables.json`)**: Supports random category drops, targeted boss/biome drops, and guaranteed first-kill/milestone drops.
- **Word (`.docx`) and PDF (`.pdf`) Visual Item Catalogs**: `Potaria_Items_Catalog.docx` (generated via `scripts/generate_items_docx.py` with OpenXML `w:cantSplit` and repeating `w:tblHeader`) and `Potaria_Items_Catalog.pdf` (generated via `scripts/generate_items_pdf.py` with direct `QPainter` row-height pagination) include all 1,461 items and crisp 64x64 pixel-art sprites with zero text/image slicing and zero header/footer overlap.

---

### 2.10 Unity 6 LTS Migration & Core Data Layer (Milestone 1 Deliverables)
- **Unity 6 LTS Project Scaffold**:
  - Initialized clean Unity 6000.0.58f1 project with 2D URP 17.0.3, 2D Tilemap, and modern Input System.
  - Excluded deprecated legacy pixel-perfect package; configured URP's integrated `UnityEngine.Rendering.Universal.PixelPerfectCamera` at 16 Pixels Per Unit.
- **Sprite & Audio Asset Migration**:
  - Ingested 2,456 pixel-art PNG sprites into `Assets/Sprites/` with Point (no filter) texture settings, uncompressed format, and 16 PPU.
  - Generated 36 new crop growth stage sprites in `Assets/Sprites/Crops/` across all 9 native crops (4 growth stages each).
  - Migrated 34 audio files (sound effects and synth tracks) into `Assets/Audio/`.
- **C# Data Models**:
  - Created strongly typed ScriptableObject classes in `Assets/Scripts/Data/`: `ItemData`, `FoodItemData` (with 14 serialized buff parameters), `WeaponItemData`, `EquipmentItemData`, `EquipmentSetData`, `CropData`, and `RecipeData`.
- **Headless Batchmode Importer**:
  - Built `PotariaDataImporter.cs` in `Assets/Scripts/Editor/` with CLI entry point `PotariaDataImporter.ImportAll`.
  - Generated and validated **1,775 ScriptableObject assets**:
    - 79 Food Items (14 buff parameters serialized)
    - 9 Crops & 8 Seeds
    - 136 Materials
    - 630 Weapons
    - 705 Equipment Pieces
    - 27 Equipment Sets (147 piece links)
    - 181 Crafting Recipes (100% input/output item linkages)
  - Zero broken references, zero missing icons, and 100% valid GUID linkages.

### 2.11 2D Tilemaps, Procedural World Generation & 2D URP Lighting (Milestone 2 Deliverables)
- **Multi-Layered 2D Tilemaps & Composite Colliders**:
  - Grid hierarchy with Terrain Tilemap (solid blocks), Wall Tilemap (background walls), Platform Tilemap (one-way platforms), and Water Tilemap (liquid trigger colliders).
  - `CompositeCollider2D` with Polygon geometry for seamless, snag-free platformer navigation.
  - Universal Render Pipeline `Sprite-Lit-Default` materials across all tilemap renderers.
- **TileDatabase & Tile Assets**:
  - `TileDatabase.cs` registering 117+ tile definitions with mining hardness, tool requirements (Pickaxe, Axe, Shovel), light emission, item drops, and collider rules.
  - Generated Unity `Tile` assets in `Assets/ScriptableObjects/Tiles/` and `Assets/ScriptableObjects/Walls/`.
  - Procedural 16x16 pixel sprites for dry/hydrated farmland, crops, wild plants, and ores.
- **Procedural Generation & 6-Ore Distribution**:
  - Multi-octave Perlin heightmap generation across Forest, Desert, Snow, Blight, and Nether Dungeon biomes.
  - Subterranean cave worm generation with boundary protection for all 4 underground dungeons.
  - 6-Ore vein clustering across geological depth zones: Coal, Copper, Iron, Gold, Diamond, and Netherite.
- **Boundless Chunk Streaming**:
  - `ChunkManager.cs` dynamic 16x240 tile chunk loading, generation, caching, and distance culling.
  - Runtime tile modification (`SetTile`, `DamageTile`) with tool tier scaling, bare-hand fallback, and live collider regeneration.
  - 4-block horizontal water hydration for crops and cave torchlight illumination.
- **2D URP Dynamic Lighting Pipeline**:
  - Configured `UniversalRenderPipeline2D.asset` and `UniversalRenderPipeline2D_Renderer.asset` in project settings.
  - `DayNightCycle2D.cs` Global Light 2D transitioning across Dawn, Noon, Sunset, and Moonlit Night.
  - `SubterraneanDarkness2D.cs` depth attenuation for underground darkness.
  - `PointLightSource2D.cs` with dynamic point light pooling for torches, lamps, and campfires.
- **Scene Architecture & Batchmode Test Validation**:
  - Sample scene `Assets/Scenes/MainWorld.unity` with Grid, Tilemaps, WorldManager, 2D Lights, and Pixel Perfect Camera (16 PPU).
  - `PotariaWorldTest.cs` batchmode runner with 84 automated tests passing (0 errors, 100% Green).

### 2.12 Character Controller, Physics, RPG Progression & Action RPG Combat (Milestone 3 Deliverables)
- **Player Controller & 2D Platformer Locomotion**:
  - `PlayerController.cs` with interpolated `Rigidbody2D` and `BoxCollider2D`.
  - Snappy acceleration/deceleration, variable jump height, coyote time (0.15s), jump buffering (0.12s), and platform drop-through (`S`).
  - Liquid swimming buoyancy, oxygen meter, underwater drag, and drowning damage.
  - Head-blocked jump audio raycast check.
  - Animated sprite rendering (walk cycle, idle breathing, jump stretch, and fall frames).
- **Cross-Platform Input System**:
  - `PotariaInput.cs` supporting Keyboard/Mouse, Gamepad (Steam Deck/Xbox), and mobile virtual touch controls.
- **RPG Progression & 5-Meal Buff System**:
  - 100-level curve (`EXP = 100 * lvl^2.1`), stat progression, and defense mitigation `max(1, ATK - DEF)`.
  - Natural MP regeneration (1.8 MP/s) + bullet grazing reward (+1 MP).
  - Single-target combat enforcement for melee and ranged attacks (Ancient cleave exceptions).
  - 5-active-meal buff slots (Offense, Defense, Mobility, Resource, Utility) with statutory stat caps and replacement rules.
- **Weapons, Ballistics & Celestial Reversal Skill**:
  - `WeaponController.cs` with rotational melee swing arcs.
  - `Projectile.cs` & `ProjectileManager.cs` supporting parabolic arrow gravity, homing magic, and javelins.
  - Ancient skill `Celestial Reversal` timed projectile reflection (0.40s-0.52s window, 1.5x damage amplification, reflection budget).
- **Danmaku Bullet-Hell & Sol-Rho Boss Combat**:
  - `DanmakuEmitter.cs` & `BossController.cs` for two-phase Sol-Rho encounter.
  - Geometric bullet patterns: 16-way spiral novas, celestial cross beams, and targeted rings.
  - 52% fair lethal core hitbox and 175% perimeter graze (+1 MP reward and sparks).
- **Camera Follow, Zoom & Death Transitions**:
  - `CameraController.cs` smooth follow damping, 3 discrete zoom levels (1x, 2x, 3x via Z), and 3.0s cinematic pitch-black death transition with spawn point snapping.
- **Automated Verification**:
  - `PotariaCombatTest.cs` batchmode runner with 116 automated tests passing with 0 errors (combined total: 200 Unity 6 tests passing, 100% Green).

## 3. Performance & Optimization Verification

- **Frame Rate Benchmark**: 110+ FPS average under standard gameplay scenes; solid 60+ FPS under heavy stress testing with 50+ active entities.
- **Chunk Streaming Stability**: Asynchronous background generation prevents frame stalls when crossing 16-block chunk boundaries (maximum frame time < 16.6ms during active traversal).
- **Lighting Engine Optimization**: 32-bit RGB integer mapping (`map_rgb`) and `absorb_grid` cache reduce per-frame cellular lighting compute from 3.5ms to 0.02ms.
- **Baked Chunk Surfaces**: Static terrain tiles are pre-baked to chunk surfaces (`ChunkSection`), reducing Pygame draw calls by over 90%.

---

## 4. Quality Assurance & Multi-Tier Verification

### 1. Unity 6 LTS Verification (Active Production Baseline)
- **Automated Batchmode Test Suites**: **200 / 200 automated tests passing with zero errors (100% Green)**:
  - `PotariaCombatTest`: 116 tests passing (Player locomotion, coyote time, jump buffering, 100-level EXP curve, damage mitigation, single-target rules, projectile reflection, 52% core hitboxes, graze rewards, boss phases, camera zoom).
  - `PotariaWorldTest`: 84 tests passing (Perlin noise determinism, tile lookups, boundless chunk streaming, mining formulas, 4-block water hydration, 2D URP lighting curves, 6-ore vein clustering, dungeon protection, point light pooling).
- **Headless Batchmode Importer**: Executed via `PotariaDataImporter.ImportAll` in headless Unity batchmode (Exit code 0).
- **ScriptableObject Assets Verified**: **1,775 ScriptableObject assets** validated with zero broken references, zero missing icons, and 100% valid GUID linkages:
  - 79 Food Items with 14 serialized buff parameters
  - 9 Philippine Crops & 8 Seeds
  - 136 Materials
  - 630 Weapons
  - 705 Equipment Pieces
  - 27 Equipment Sets (147 piece links)
  - 181 Crafting Recipes (100% input/output links)
- **Compilation Health**: 0 compilation errors, 0 warnings across all C# scripts in `Assets/Scripts/`.

### 2. Pygame-ce Regression Verification (Legacy Foundation Baseline)
- **Test Runner**: `pytest`
- **Status**: **770 / 770 automated tests passing with zero errors across 47 test suites (100% Green).**
- **Headless CI/CD Compatibility**: All tests execute cleanly in dummy video/audio driver environments (`SDL_VIDEODRIVER=dummy`, `SDL_AUDIODRIVER=dummy`).
- **Regression Protection**: Automated test coverage spans inventory safety, combat calculations, equipment set bonuses, procedural terrain, trader state machines, bullet-hell hitboxes, crafting categories, world persistence, renderer HAL abstraction, GLSL Bloom pipeline, projectile batching, and Philippine agriculture/cooking systems.

---

## 5. Strategic Roadmap Deliverables (Unity 6 LTS Implementation)

The production roadmap transitions Potaria into a commercial multiplatform release:

1. **Milestone 1: Project Scaffold, Asset Ingestion & Core Data Layer (COMPLETED)**:
   - Unity 6000.0.58f1 + 2D URP 17.0.3 project setup with clean directory structure and .gitignore.
   - Preserved working Pygame-ce engine on dedicated `pygame-engine` remote branch.
   - Ingested 2,456 pixel-art sprites (16 PPU, Point filter) and 34 audio files.
   - Generated 36 new crop growth stage sprites in `Assets/Sprites/Crops/`.
   - Created C# data models (`ItemData`, `FoodItemData`, `WeaponItemData`, `EquipmentItemData`, `EquipmentSetData`, `CropData`, `RecipeData`).
   - Built headless batchmode importer generating 1,775 verified ScriptableObjects (0 broken references).
2. **Milestone 2: 2D Tilemap, Chunk Streaming & Procedural World Generation (COMPLETED)**:
   - Dual-tilemap architecture: Terrain Tilemap (solid foreground) and Wall Tilemap (ambient background).
   - Chunk streaming manager handling dynamic generation and culling around camera.
   - Multi-octave Perlin noise generation for Forest, Desert, Snow, Blight, and Nether Dungeon biomes.
   - RuleTiles / Terrain Tile palettes for 117+ block types with smooth autotiling.
   - 2D URP lighting integration (Day/Night global light cycling and subterranean torch point lights).
3. **Milestone 3: Character Controller, Physics & Action RPG Combat (COMPLETED)**:
   - Rigidbody2D + BoxCollider2D player controller with responsive jump physics, coyote time, and jump buffering.
   - Unity Input System actions supporting Keyboard/Mouse, Gamepad (Steam Deck / Xbox / DualSense), and Touch.
   - 100-level RPG stat progression curve (HP, MP, ATK, DEF, Crit Rate).
   - 40 Skill Book abilities with VFX, cooldowns, and bullet-reflection mechanics (`Celestial Reversal`).
   - Danmaku boss combat system with 52% core lethal hitboxes and perimeter grazing (+1 MP).
4. **Milestone 4: Inventory, Crafting, Equipment & Responsive UI (IN PROGRESS)**:
   - 40-slot backpack inventory with item stack dragging, splitting, and `[ORGANIZE]` gap compaction.
   - Dedicated coin purse UI with real-time Copper, Silver, and Gold auto-conversion.
   - 5-category crafting book with station filtering (Hand, Work Bench, Furnace, Campfire).
   - Side-by-side equipment comparison tooltip ("katabi") with `[ CURRENTLY EQUIPPED ]` badges.
   - Visual circular affix socket indicators ((Empty Socket) and (Filled Socket)) adhering to rarity limits.
   - Bottom-left food buff HUD overlay with hover tooltips and remaining duration meters.
5. **Milestone 5: Philippine Farming, Tiered Cooking & Fishing Minigame**:
   - 4-stage visual growth progression for 9 crops with hydration dynamics and subterranean cave lighting.
   - Timed furnace cooking queues (2.5s-20.0s) with single-food-per-furnace limit and direct fish grilling.
   - 12.0s tension-based fishing minigame with moving golden sweet spot and escape penalty.
6. **Milestone 6: Steamworks Integration & P2P / LAN Multiplayer**:
   - FishNet / Steamworks P2P networking for 1-5 player cooperative multiplayer.
   - Automatic Steam lobby matchmaking, friend invites, and direct LAN IP fallback.
   - Client-side prediction and host-authoritative block modification deltas.
   - Steam Achievements, Cloud Saves, and Steam Deck verification.
7. **Milestone 7: Multiplatform Commercial Release (Steam & Google Play Store)**:
   - Production Windows/macOS/Linux Steam builds.
   - Google Play Store Android AAB export with Scoped Storage, adaptive framerate (60/120 Hz), and touch virtual controls.
