# Potaria Project Deliverables & System Milestones

**Developer:** Kurados  
**Engine:** Pure Python 3.13 + Pygame-ce 2.5.8 (100% Offline Standalone)  
**Franchise Model:** One Project Repository (Unified Codebase with Dual-Profile Architecture)  
**Rendering Architecture:** Smart OpenGL Hardware Abstraction Layer (HAL) with Safe Fallback  
**Test Suite Status:** 357 Tests Passing across 27 Test Suites (100% Green)  
**Current Version:** v1.8.0  

---

## 1. Executive Deliverables Summary

Potaria is a production-grade 2D sandbox action RPG combining boundless procedural terrain generation with deep character customization, paperdoll equipment slots, 40 combat skills, bullet-hell boss encounters, animated specialized traders, item enhancement and affixes, and LAN cooperative multiplayer.

The franchise is structured under a unified **One Project Repository** architecture, cleanly separating the boundless sandbox base game ("Potaria") from the narrative campaign flagship ("Potaria: Root Realm"). The graphics pipeline operates via a **Smart OpenGL Hardware Abstraction Layer (HAL)** that defaults to hardware-accelerated ModernGL rendering while providing instant, automatic safety fallback to native Pygame-ce software blitting if OpenGL drivers are missing or uninitialized.

All systems are fully verified, regression-tested, and operate completely offline without external network dependencies.

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

## 3. Performance & Optimization Verification

- **Frame Rate Benchmark**: 110+ FPS average under standard gameplay scenes; solid 60+ FPS under heavy stress testing with 50+ active entities.
- **Chunk Streaming Stability**: Asynchronous background generation prevents frame stalls when crossing 16-block chunk boundaries (maximum frame time < 16.6ms during active traversal).
- **Lighting Engine Optimization**: 32-bit RGB integer mapping (`map_rgb`) and `absorb_grid` cache reduce per-frame cellular lighting compute from 3.5ms to 0.02ms.
- **Baked Chunk Surfaces**: Static terrain tiles are pre-baked to chunk surfaces (`ChunkSection`), reducing Pygame draw calls by over 90%.

---

## 4. Quality Assurance & Test Coverage

- **Total Test Suites**: 27 distinct suites in `tests/`.
- **Total Automated Tests**: 357 tests passing with zero errors (100% Green).
- **Headless CI/CD Compatibility**: All tests execute cleanly in dummy video/audio driver environments (`SDL_VIDEODRIVER=dummy`, `SDL_AUDIODRIVER=dummy`).
- **Regression Protection**: Automated test coverage spans inventory safety, combat calculations, equipment set bonuses, procedural terrain, trader state machines, bullet-hell hitboxes, crafting categories, world persistence, renderer HAL abstraction, GLSL Bloom pipeline, projectile batching, and the Phase 1 Data-Driven Loot & Affix System.

---

## 5. Strategic Roadmap Deliverables

1. **Stage 1 (Complete)**: Renderer Hardware Abstraction Layer (HAL) decoupling Pygame-ce software blitting from rendering backends, with safe fallback and in-game settings toggle.
2. **Stage 2 (Complete)**: ModernGL / OpenGL hardware acceleration with GLSL lighting, bloom post-processing shaders, high-density projectile batch rendering, and single-log fallback deduplication.
3. **Phase 1 Root Realm Expansion (Complete)**: Data-Driven Loot, Rarity & Multi-Affix System (`src/loot/`) and Complete Word/PDF Visual Item Catalogs (`Potaria_Items_Catalog.docx` & `Potaria_Items_Catalog.pdf`).
4. **Stage 3 (Next)**: Steam PC production packaging via Nuitka C-compilation and gamepad support.
5. **Stage 4**: Google Play Android packaging with virtual touch controls, Buildozer APK/AAB builds, and lifecycle persistence.
6. **Flagship Franchise Release**: *Potaria: Root Realm* (Narrative episodic adventure with Heartroot transformations and POTAdex).
