# Potaria: Exhaustive Pygame-CE to Unity 6 LTS Feature Parity Specification & Technical Architecture Reference

**Author & Developer:** Kurados  
**Active Development Engine:** Unity 6 LTS (v6000.0.58f1) + 2D Universal Render Pipeline (URP 17.0.3)  
**Legacy Reference Engine:** Pure Python 3.13.16 + Pygame-CE 2.5.8 (Preserved permanently on `pygame-engine` branch)  
**Project Architecture:** One Project Repository (Dual-Profile Architecture: Base Sandbox + Flagship Campaign)  
**Target Verification Standard:** 770 / 770 Pygame Tests Passing; 1,775 Unity ScriptableObjects Validated; 84 / 84 World Gen Tests Passing; 116 / 116 Combat Tests Passing; 57 / 57 Overhaul Systems Tests Passing (0 Errors)  
**Document Classification:** Production-Grade Technical Specification, Codebase Census, and Implementation Parity Audit  

---

## Master Table of Contents

- [1. Executive Technical Architecture & Migration Overview](#1-executive-technical-architecture--migration-overview)
  - [1.1 Franchise Strategy & One Project Repository Model](#11-franchise-strategy--one-project-repository-model)
  - [1.2 Legacy Engine Specification: Python 3.13 + Pygame-CE](#12-legacy-engine-specification-python-313--pygame-ce)
  - [1.3 Active Target Engine Specification: Unity 6 LTS + 2D URP](#13-active-target-engine-specification-unity-6-lts--2d-urp)
  - [1.4 Verified Migration Milestones & Test Baselines](#14-verified-migration-milestones--test-baselines)
- [2. System-by-System Deep Technical Architecture Breakdown](#2-system-by-system-deep-technical-architecture-breakdown)
  - [2.1 World Generation, Infinite Chunk Streaming & Procedural Terrain](#21-world-generation-infinite-chunk-streaming--procedural-terrain)
  - [2.2 Dual Tilemap Geometry, Composite Colliders & Snag-Free Platforming](#22-dual-tilemap-geometry-composite-colliders--snag-free-platforming)
  - [2.3 2D Dynamic Lighting, Celestial Day/Night Phases & Subterranean Darkness](#23-2d-dynamic-lighting-celestial-daynight-phases--subterranean-darkness)
  - [2.4 Locomotion, Kinematic Physics & Player Character Controller](#24-locomotion-kinematic-physics--player-character-controller)
  - [2.5 Liquid Physics, Buoyancy, Swimming Mechanics & Oxygen Drowning](#25-liquid-physics-buoyancy-swimming-mechanics--oxygen-drowning)
  - [2.6 Combat Engine: Weapon Archetypes, Attack Speeds & Single-Target Rules](#26-combat-engine-weapon-archetypes-attack-speeds--single-target-rules)
  - [2.7 Ballistics Engine: Parabolic Gravity, Homing, Piercing & Shockwaves](#27-ballistics-engine-parabolic-gravity-homing-piercing--shockwaves)
  - [2.8 Touhou-Inspired Bullet-Hell Boss Encounters & Danmaku Novas](#28-touhou-inspired-bullet-hell-boss-encounters--danmaku-novas)
  - [2.9 Grazing Mechanics, Precision Dodge Sparking & Mana Rewards](#29-grazing-mechanics-precision-dodge-sparking--mana-rewards)
  - [2.10 Celestial Reversal: Timed Projectile Reflection Mechanics](#210-celestial-reversal-timed-projectile-reflection-mechanics)
  - [2.11 Action RPG Statistics, 100-Level EXP Curve & Attribute Scaling](#211-action-rpg-statistics-100-level-exp-curve--attribute-scaling)
  - [2.12 Damage Mitigation Formulas, Defense Curves & Critical Strike Scaling](#212-damage-mitigation-formulas-defense-curves--critical-strike-scaling)
  - [2.13 Philippine Culinary System, 79 Recipes & 5-Meal Buff Framework](#213-philippine-culinary-system-79-recipes--5-meal-buff-framework)
  - [2.14 19 Statutory Meal Buff Contribution Caps](#214-19-statutory-meal-buff-contribution-caps)
  - [2.15 Philippine Agricultural Simulation, Soil Tilling & 8 Native Crops](#215-philippine-agricultural-simulation-soil-tilling--8-native-crops)
  - [2.16 2D Fishing Battle Minigame & 10 Native Philippine Aquatic Species](#216-2d-fishing-battle-minigame--10-native-philippine-aquatic-species)
  - [2.17 Chroisen-Style Paperdoll Equipment System & 10 Equipment Slots](#217-chroisen-style-paperdoll-equipment-system--10-equipment-slots)
  - [2.18 27 Progressive Equipment Sets & Tiered Milestone Synergies](#218-27-progressive-equipment-sets--tiered-milestone-synergies)
  - [2.19 Canonical 7-Tier Rarity Engine & Stat Roll Distribution](#219-canonical-7-tier-rarity-engine--stat-roll-distribution)
  - [2.20 Item Enhancement (+1 to +7) Strategic Risk Curves & Break Risks](#220-item-enhancement-1-to-7-strategic-risk-curves--break-risks)
  - [2.21 Affix Engine, Affix Stone Carving & Slot Allotment Caps](#221-affix-engine-affix-stone-carving--slot-allotment-caps)
  - [2.22 Mobs & Boss AI State Machines (33 Mob Types & 5 Boss Titans)](#222-mobs--boss-ai-state-machines-33-mob-types--5-boss-titans)
  - [2.23 Nomadic Animated Traders, Turtle Shell Shield Defense & 1 Gold Repair](#223-nomadic-animated-traders-turtle-shell-shield-defense--1-gold-repair)
  - [2.24 Housing Validity, Room Enclosure Checks & Village Settlement](#224-housing-validity-room-enclosure-checks--village-settlement)
  - [2.25 HUD Architecture: Hotbars, Hearts, Mana, Clock Badge & Minimap Radar](#225-hud-architecture-hotbars-hearts-mana-clock-badge--minimap-radar)
  - [2.26 Side-by-Side Equipment Comparison Cards ('Katabi') & Tooltips](#226-side-by-side-equipment-comparison-cards-katabi--tooltips)
  - [2.27 F3 Real-Time Profiler Overlay & Frame Telemetry](#227-f3-real-time-profiler-overlay--frame-telemetry)
  - [2.28 Mobile Touch Virtual Controller, Virtual Joystick & Action Clusters](#228-mobile-touch-virtual-controller-virtual-joystick--action-clusters)
  - [2.29 Audio Engine: Synthesized SFX, Dynamic Biome BGM & Narrator Speech](#229-audio-engine-synthesized-sfx-dynamic-biome-bgm--narrator-speech)
  - [2.30 Multi-Layer Save Engine, HMAC Security Signatures & World Caching](#230-multi-layer-save-engine-hmac-security-signatures--world-caching)
  - [2.31 Multiplayer Architecture: LAN UDP Discovery & FishNet/Steamworks P2P](#231-multiplayer-architecture-lan-udp-discovery--fishnetsteamworks-p2p)
  - [2.32 Modding & DLC Content Pack Extensibility System](#232-modding--dlc-content-pack-extensibility-system)
- [3. Exhaustive Inventory of All Pygame-CE Codebase Classes, Functions & Methods](#3-exhaustive-inventory-of-all-pygame-ce-codebase-classes-functions--methods)
- [4. Master Reference of Exact Numeric Values, Formulas & Physical Constants](#4-master-reference-of-exact-numeric-values-formulas--physical-constants)
  - [4.1 Canonical Master Constants Reference (`src/constants.py`)](#41-canonical-master-constants-reference-srcconstantspy)
  - [4.2 Kinematic & Locomotion Tuning Constants](#42-kinematic--locomotion-tuning-constants)
  - [4.3 Fluid Mechanics & Oxygen Depletion Formula](#43-fluid-mechanics--oxygen-depletion-formula)
  - [4.4 Combat & Damage Calculation Formulas](#44-combat--damage-calculation-formulas)
  - [4.5 100-Level RPG Progression & EXP Formulas](#45-100-level-rpg-progression--exp-formulas)
  - [4.6 Statutory Meal Buff Contribution Caps (`MEAL_BUFF_CAPS`)](#46-statutory-meal-buff-contribution-caps-meal_buff_caps)
  - [4.7 7-Tier Rarity Engine Tables & Affix Budgets](#47-7-tier-rarity-engine-tables--affix-budgets)
  - [4.8 Item Enhancement (+1 to +7) Requirements, Success Curves & Break Risks](#48-item-enhancement-1-to-7-requirements-success-curves--break-risks)
  - [4.9 Maximum Additional Affix Slots (`MAX_ADDITIONAL_AFFIX_SLOTS`)](#49-maximum-additional-affix-slots-max_additional_affix_slots)
  - [4.10 Complete 27 Equipment Sets Reference Table](#410-complete-27-equipment-sets-reference-table)
  - [4.11 Complete 40 Action Combat Skills Roster](#411-complete-40-action-combat-skills-roster)
  - [4.12 10 Native Philippine Aquatic Species Tuning Table](#412-10-native-philippine-aquatic-species-tuning-table)
  - [4.13 8 Native Philippine Crops Agricultural Table](#413-8-native-philippine-crops-agricultural-table)
- [5. HUD & UI Layout Specifications, Rendering Logic & Algorithms](#5-hud--ui-layout-specifications-rendering-logic--algorithms)
  - [5.1 Viewport Coordinates & Anchor Offsets](#51-viewport-coordinates--anchor-offsets)
  - [5.2 10-Slot Hotbar Visual & Functional Specification](#52-10-slot-hotbar-visual--functional-specification)
  - [5.3 Life Hearts & Mana Star Render Pipelines](#53-life-hearts--mana-star-render-pipelines)
  - [5.4 Active Meal Buff Tray & Countdown Timers](#54-active-meal-buff-tray--countdown-timers)
  - [5.5 Side-by-Side Equipment Comparison ('Katabi') Layout Algorithm](#55-side-by-side-equipment-comparison-katabi-layout-algorithm)
  - [5.6 Comprehensive Tooltip Line Construction Pipeline](#56-comprehensive-tooltip-line-construction-pipeline)
  - [5.7 Real-Time Profiler Overlay Layout (F3)](#57-real-time-profiler-overlay-layout-f3)
  - [5.8 Pseudo-Code: Celestial Reversal Projectile Reflection Algorithm](#58-pseudo-code-celestial-reversal-projectile-reflection-algorithm)
  - [5.9 Pseudo-Code: 52% Core Hitbox vs. Graze Detection Algorithm](#59-pseudo-code-52-core-hitbox-vs-graze-detection-algorithm)
  - [5.10 Pseudo-Code: Dual-Tilemap Snag-Free Platforming with BoxCast & Normal Detection](#510-pseudo-code-dual-tilemap-snag-free-platforming-with-boxcast--normal-detection)
- [6. Comprehensive Unity 6 Parity Audit Matrix](#6-comprehensive-unity-6-parity-audit-matrix)
- [7. Strategic Porting Roadmap & Prioritized Backlog (Milestones 4 through 7)](#7-strategic-porting-roadmap--prioritized-backlog-milestones-4-through-7)

---

## 1. Executive Technical Architecture & Migration Overview

### 1.1 Franchise Strategy & One Project Repository Model
Potaria is architected under a unified **One Project Repository** model. The repository contains both the sandbox foundation and the narrative flagship:
- **Sandbox Base Game ('Potaria')**: Boundless horizontal sandbox action RPG with infinite chunk generation, building, mining, Philippine farming, tiered cooking, Chroisen paperdoll gear, and cooperative LAN/Steam P2P multiplayer.
- **Narrative Flagship ('Potaria: Root Realm')**: Handcrafted dungeon-crawling story edition built upon the same physics, combat, bullet-hell danmaku, and culinary mechanics.

The migration transfers the proven game systems developed and verified in Python 3.13 into Unity 6 LTS to achieve high-performance native execution across Windows PC, Steam Deck, and Android mobile devices, while eliminating Python's Global Interpreter Lock (GIL) and graphics driver overhead.

### 1.2 Legacy Engine Specification: Python 3.13 + Pygame-CE
The original codebase preserved on the `pygame-engine` branch operates on:
- Runtime: Pure Python 3.13.16 64-bit.
- Graphics / Audio: `pygame-ce` 2.5.8 (SDL 2.32.10).
- Hardware Rendering HAL: Modern OpenGL 3.3 Core Profile via `PyOpenGL 3.1.9` with GLSL vertex and fragment shaders for bloom, vignette, water distortion, and color grading, backed by a pure software SurfaceRenderer fallback.
- Audio Synthesis: Procedural 16-bit 44.1 kHz PCM audio synthesis for swing sounds, damage, footsteps, and spatial audio cues.
- Automated QA: 770 test cases executed via `pytest`, achieving 100% green verification across world generation, inventory, physics, and combat.

### 1.3 Active Target Engine Specification: Unity 6 LTS + 2D URP
The active development branch (`main`) is built upon:
- Engine Version: **Unity 6 LTS (v6000.0.58f1)**.
- Render Pipeline: **2D Universal Render Pipeline (URP 17.0.3)**.
- Physics: 2D Physics engine with `Rigidbody2D` (interpolated fixed time step 0.02s) and `CompositeCollider2D` configured with polygon geometry for snag-free movement.
- Lighting: 2D URP dynamic lights (Global Light 2D for celestial day-night cycles, Point Light 2D for torches, lanterns, and fireplaces with soft shadow attenuation).
- Data Architecture: Typed C# `ScriptableObject` assets for items, weapons, armor, sets, food buffs, crops, and crafting recipes, eliminating hardcoded string dictionaries.
- Input: Unity New Input System (`UnityEngine.InputSystem`) with cross-platform bindings for Keyboard/Mouse, Gamepad (Steam Deck / Xbox), and Mobile Virtual Touch.

### 1.4 Verified Migration Milestones & Test Baselines
- **Milestone 1 (Scaffold, Asset Ingestion & Core Data Layer)**: COMPLETED. 1,775 ScriptableObject assets generated and verified with 0 errors via `PotariaDataImporter`. 2,456 pixel-art PNG sprites organized with 16 PPU, Point filtering, and uncompressed textures.
- **Milestone 2 (2D Tilemaps, Chunk Streaming & Procedural Generation)**: COMPLETED. 84 / 84 tests passing in `PotariaWorldTest`. Dual tilemap layer architecture, CompositeCollider2D, Perlin cave synthesis, ore veins, and asynchronous chunk streaming.
- **Milestone 3 (Player Controller, Physics, Combat, Day/Night Lighting, HUD & Dual Localization)**: COMPLETED. 116 / 116 tests passing in `PotariaCombatTest`; 57 / 57 tests passing in `PotariaOverhaulTest`. Ground detection BoxCastNonAlloc, jump grace timers, 12 FPS animation cycles, danmaku emitters, 52% core hitboxes, graze detection, 10-slot HUD hotbar, life/mana readouts, and English/Filipino localization.
- **Milestone 4 (Inventory, Crafting, Equipment & Responsive UI)**: IN PROGRESS. Backpack inventory, side-by-side comparison cards ('katabi'), 5-tab crafting book, and affix socket indicators.
- **Milestone 5 (Farming, Tiered Cooking & Fishing Minigame)**: SCHEDULED.
- **Milestone 6 (Steamworks & P2P Multiplayer)**: SCHEDULED.
- **Milestone 7 (Multiplatform Commercial Release)**: SCHEDULED.

---

## 2. System-by-System Deep Technical Architecture Breakdown

### 2.1 World Generation, Infinite Chunk Streaming & Procedural Terrain
- **Coordinate Space & Scale**: The world operates on a discrete grid where each block is 16x16 pixels in source art, scaled by 2x to 32x32 screen pixels (`SCALED_TILE = 32`). The horizontal dimension is boundless ($-\infty \leftarrow 0 \rightarrow +\infty$), structured into column chunks of 16 tiles wide by 240 tiles deep (`ChunkWidth = 16`, `ChunkHeight = 240`).
- **Vertical Altitude Strata**:
  - Sky Layer ($Y < 0$ to $Y = 70$): Open air, floating sky citadels, bird/demon eye flight space.
  - Surface Horizon ($Y = 70$ avg): Rolling hills synthesized using multi-octave 1D Perlin noise (`fractal1d(x * 0.04, octaves=4)`), topped with Grass, Wild Crops, Oak/Palm/Pine trees.
  - Underground Dirt & Stone Transition ($Y = 70$ to $115$): Dirt pockets, Copper Ore veins, surface caves.
  - Cavern Depth ($Y = 115$ to $160$): Solid Stone bedrock matrix, Iron Ore, Gold Ore, glowing subterranean Mushroom Grottos (`TILE_MUSHROOM_GRASS`, `TILE_MUSHROOM_STEM`, `TILE_MUSHROOM_CAP` with blue illumination).
  - Nether Dungeon & Catacombs ($Y = 160$ to $205+$): Indestructible Dungeon Bricks (`TILE_DUNGEON_BRICK`, Magma, Ice, Bone variants), Boss Altar, Dungeon Gate portcullis, and Lord Malus summoning room.
- **Asynchronous Chunk Streaming**:
  - Distance-based loading: Chunks are streamed into memory based on player horizontal coordinate $X$. Chunks within a radius of 3 chunks (48 tiles) are loaded and active.
  - Eviction policy: Chunks outside an active radius of 6 chunks (96 tiles) are serialized to cache and purged from memory to prevent RAM bloat.
  - Procedural Carving: 2D Perlin noise (`fractal2d(x * 0.08, y * 0.08)`) with a density threshold of $> 0.58$ generates Swiss-cheese cave networks, subterranean lakes, and abandoned mine shafts.

### 2.2 Dual Tilemap Geometry, Composite Colliders & Snag-Free Platforming
- **Layer Separation**:
  - Background Wall Tilemap: Rendered behind entities (`Z = 1.0`), non-colliding. Absorbs ambient light and validates room shelter.
  - Solid Block Tilemap: Rendered at `Z = 0.0` with `CompositeCollider2D` set to `GeometryType.Polygons` and `UsedByComposite = true`.
  - Platforms & Rungs: Thin one-way horizontal platforms (`TILE_WOOD_PLATFORM`, shelves, tables, altars) and vertical climbable ropes (`TILE_ROPE_RUNGS`).
- **Snag-Free Movement Physics**:
  - In traditional tile-based platformers, individual BoxCollider2D components on each tile create internal edge seams that catch the player's collider during horizontal runs, causing phantom stops.
  - Solution: Potaria merges all contiguous solid foreground tiles into a single unified polygon perimeter via `CompositeCollider2D`. The player collider uses a vertical BoxCollider2D with a zero-friction physics material (`Friction = 0.0`, `Bounciness = 0.0`), preventing slope adhesion or seam catching.

### 2.3 2D Dynamic Lighting, Celestial Day/Night Phases & Subterranean Darkness
- **Day/Night Celestial Cycle**:
  - One complete game day spans 720.0 seconds (12.0 real minutes).
  - Four distinct celestial phases:
    1. Dawn ($0.00 \le T < 0.25$): Amber morning sky gradient, rising sun, ambient light rising from 0.35 to 1.00.
    2. Noon ($0.25 \le T < 0.50$): Azure midday sky, full illumination, ambient light at 1.00.
    3. Sunset ($0.50 \le T < 0.75$): Crimson and purple dusk horizon, setting sun, ambient light decaying from 1.00 to 0.25.
    4. Night ($0.75 \le T < 1.00$): Midnight indigo abyss, rising lunar crescent, 140 twinkling star sprites, ambient light at 0.15. Hostile surface mobs spawn (Zombies, Demon Eyes).
- **Subterranean Darkness & Radial Point Lights**:
  - As depth exceeds $Y = 85$, surface sunlight attenuates quadratically. Caverns at $Y \ge 160$ are pitch-black (`Light = 0`).
  - Torches (`TILE_TORCH`) emit warm orange point light (radius 6 blocks / 192 px, intensity 0.70) with dynamic 2D shadow casting.
  - Spectral Lanterns emit azure light (radius 8 blocks, intensity 0.85); Chandeliers emit grand white illumination (radius 14 blocks).

### 2.4 Locomotion, Kinematic Physics & Player Character Controller
- **Locomotion Kinematics**:
  - Base Run Speed: 6.0 units/sec (scaled from Pygame 3.0 px/frame).
  - Horizontal Run Acceleration: 40.0 units/sec^2. Deceleration / Friction: 32.0 units/sec^2.
  - Jump Velocity: 12.0 units/sec upward impulse (Pygame `PLAYER_JUMP_FORCE = -8.0`).
  - Variable Jump Cut Multiplier: 0.45x. Releasing the Jump key while ascending truncates upward velocity, allowing micro-hops over ground spikes.
  - Coyote Time: 0.15s window. The player can jump within 150ms after walking off a ledge, eliminating dropped inputs.
  - Jump Buffering: 0.12s window. Pressing Jump within 120ms prior to touchdown executes an instant hop upon landing.
  - Jump Grace Timer: 0.08s window. Temporarily bypasses ground snapping to prevent slope adhesion canceling upward leaps.
  - Platform Drop-Through: Pressing S or Down sets `_platformDropTimer = 0.25s`, disabling platform collision layers to drop down through wooden platforms and scaffolding.
  - Head Unblocked Jump Check: Grounded jump sounds trigger only if the tile directly above the player's head is non-solid.
  - 12 FPS Animation Engine: 8-frame walk cycle, idle breathing, jump stretch, and fall frames cycling at 0.0833s per frame.

### 2.5 Liquid Physics, Buoyancy, Swimming Mechanics & Oxygen Drowning
- **Water Contact & Submersion**:
  - Lower-body contact (`in_water = true`): Horizontal drag applies 0.88x velocity damping; vertical drag applies 0.90x damping. Gravity is reduced to 0.25x (`GRAVITY * 0.25`).
  - Swimming Controls: Holding Jump/Up/W paddles upward (`vy = max(-3.6, vy - 1.4)`); holding Drop/Down/S dives downward (`vy = min(2.8, vy + 0.8)`).
- **Oxygen Depletion & Drowning**:
  - Submersion (`is_submerged = true`): When head center is submerged in water, oxygen drains at 7.5 units/sec from a max pool of 100.0 (total breath duration = 13.3 seconds).
  - Surfacing: Oxygen rapidly replenishes at 40.0 units/sec (fully restored in 2.5 seconds).
  - Drowning Tick: At 0.0 oxygen, `_drownTimer` accumulates. Every 1.0 second submerged at zero oxygen, the player suffers true damage equal to 10% of Max HP (1 full heart), completely ignoring physical and magical defense.

### 2.6 Combat Engine: Weapon Archetypes, Attack Speeds & Single-Target Rules
- **Attack Speed Categories**:
  - Very Fast (0.22s fire rate / cooldown): Daggers, stilettos, throwing knives, shortswords.
  - Fast (0.26s - 0.32s fire rate): Katanas, rapiers, sabers, spears, arming swords.
  - Average (0.34s - 0.36s fire rate): Staves, wands, compound bows, composite crossbows.
  - Slow, Heavy (0.46s fire rate): Greatswords, battleaxes, warhammers, colossal cleavers, scythes.
- **Single-Target Rule & Ancient Relic Cleave**:
  - Every melee swing and ballistic projectile hits at most 1 enemy target per attack.
  - Exception: Ancient-tier weapons and weapons rolling the `Cleave` or `Pierce` traits damage all enemies intersected by the swing arc or projectile line.

### 2.7 Ballistics Engine: Parabolic Gravity, Homing, Piercing & Shockwaves
- **Ballistic Archery**:
  - Arrow projectiles (`ArrowProjectile`) simulate true parabolic ballistic trajectory: `x += vx * dt`, `vy += 9.8 * 0.44 * dt`, rotating sprite angle to face instantaneous velocity vector `atan2(vy, vx)`.
  - Arrow types: Wooden Arrow (baseline), Fire Arrow (ignites burn DOT), Frost Arrow (chills and slows target 40%), Spectral Arrow (bypasses solid blocks).
- **Magic Archetypes**:
  - Catalysts: Fires homing celestial stars that calculate angle delta to nearest enemy target, turning up to 180 deg/sec.
  - Staves: Fires straight elemental bolts that detonate with area splash upon impact.
  - Rods: Fires piercing astral javelins that penetrate up to 3 consecutive enemies before dissipating.
  - Scepters: Emits expanding radial shockwaves pushing back swarming mobs.

### 2.8 Touhou-Inspired Bullet-Hell Boss Encounters & Danmaku Novas
- **Pattern Generators (`DanmakuEmitter`)**:
  - 16-Way Spiral Nova: Omnidirectional expanding starburst with curving angular velocity (`curveRate = 0.25`).
  - Rotating Celestial Cross Beams: 4-way or 8-way rotating cruciform beams creating moving dodge corridors.
  - Targeted Bullet Rings: Expanding circular rings directed at the player's center with deliberate micro-gaps for weaving maneuvers.
  - Criss-Cross Curtains: Alternating left-and-right curved projectile waves blanketing the battle arena.
- **Fair 52% Lethal Core Hitbox**:
  - While visual bullet sprites measure 16x16 to 24x24 pixels, the lethal damage collider is restricted strictly to the central 52% core radius (`radius * 0.52`).
  - Eliminates unfair clipping deaths and rewards micro-dodging through tight bullet clusters.

### 2.9 Grazing Mechanics, Precision Dodge Sparking & Mana Rewards
- **Graze Radius**:
  - Defined as the outer annular perimeter between 100% and 175% of the projectile's visual radius (`core < hit <= 1.75 * radius`).
- **Reward & Feedback**:
  - When an enemy bullet passes through the player's graze ring without intersecting the 52% lethal core, grazing triggers.
  - Awards +1 MP instantly, plays an audio graze chime, and emits radiant cyan sparks from the potato hero's body.
  - Encourages daring evasive maneuvers during bullet-hell boss encounters.

### 2.10 Celestial Reversal: Timed Projectile Reflection Mechanics
- **Active Reflection Field**:
  - Triggered by Ancient skill `celestial_reversal` (or hotkey Z).
  - Opens a high-potency reflection window of 0.45 seconds (0.40s - 0.52s tuning range).
  - Reflection Budget: Up to 15 projectiles can be reflected per cast.
- **Kinematic & Damage Amplification**:
  - Any enemy projectile within 2.5 blocks of player center is inverted: `velocity = -velocity * 1.25`.
  - The projectile's ownership is transferred to the player (`isEnemy = false`), rendering it immune to player collision and capable of damaging boss entities.
  - Damage is amplified by 1.5x (150% original damage), turning devastating boss bullet storms back upon their summoners.

### 2.11 Action RPG Statistics, 100-Level EXP Curve & Attribute Scaling
- **Progression Curve (Levels 1 to 100)**:
  - Base Attributes at Level 1: Max HP = 100, Max MP = 50, Base ATK = 10, Base DEF = 2, Crit Rate = 5.0%, Crit Multiplier = 1.8x, Base Speed = 3.0, Base Attack Speed = 1.0, Base MP Regen = 1.8 MP/s.
  - Scaling per Level: +15 Max HP, +8 Max MP, +3 Base ATK, +1 Base DEF.
  - Crit Rate Milestones: +1.0% Crit Rate every 5 levels.
  - EXP to Next Level Formula: `exp_to_next = int(100 * (level ** 2.1))`.
  - Level-Up Reward: Complete replenishment of both HP and MP pools to their new maximum caps.
  - YOLO Difficulty Mode: Locks player permanently to exactly 1 Heart (20 HP) that cannot increase under any circumstances.

### 2.12 Damage Mitigation Formulas, Defense Curves & Critical Strike Scaling
- **Defense Mitigation Formula**:
  - Incoming physical damage is mitigated directly: `damage_taken = max(min_pierce, raw_damage - total_def)`.
  - Defense Cap: DEF cannot mitigate more than 85% of incoming damage. Minimum piercing damage is guaranteed: `min_pierce = max(1, ceil(raw_damage * 0.15))`.
- **Special Combat Passives**:
  - Titan's Resolve: Triples total DEF (`effective_def *= 3`) whenever current HP falls below 30% of Max HP. Minimum pierce is reduced to 1.
  - Total Damage Mitigation: Multiplicative reduction (15% or 25%) applied after DEF subtraction.
  - Evasion Step: 15% flat chance to completely evade an incoming strike, triggering 0.3s invulnerability frames.
  - Starch Barrier: Blocks lethal fatal damage once every 90 seconds, setting HP to 25% of Max HP with 2.0s invulnerability frames.
  - Eternal Bloom: Restores 50% HP upon reaching 1 HP once every 180 seconds with 1.5s invulnerability frames.

### 2.13 Philippine Culinary System, 79 Recipes & 5-Meal Buff Framework
- **5-Meal Buff Framework**:
  - Players can maintain up to 5 concurrent food buffs, strictly restricted to 1 active buff per category:
    1. Offense (e.g., Adobo, Bulalo, Bistek Tagalog, Sisig).
    2. Defense (e.g., Sinigang na Baboy, Dinuguan, Pinangat, Tinola).
    3. Mobility (e.g., Pancit Bihon, Pancit Palabok, Lumpia Shanghai, Arroz Caldo).
    4. Resource / Regeneration (e.g., Halo-Halo, Taho, Leche Flan, Turon, Bibingka).
    5. Utility / Luck (e.g., Ukoy, Kare-Kare, Kinilaw, Bicol Express).
  - Consuming a new dish in an already occupied category overwrites the previous buff; durations do not stack.
- **Tiered Cooking Stations & Durations**:
  - Raw food must be prepared at Furnaces, Cozy Hearth Pits, or Campfires.
  - Duration scales by culinary tier: Quick snacks = 2.5s to 5.0s; Standard dishes = 8.0s to 12.0s; Grand festive meals (Lechon, Kare-Kare) = 15.0s to 20.0s.
  - Inihaw Grilling: Direct fish catches can be grilled on open fires into Inihaw na Bangus, Inihaw na Tilapia, etc.

### 2.14 19 Statutory Meal Buff Contribution Caps
To preserve action RPG combat balance and prevent multiplicative stat inflation, Section 6.4 of the Potaria specification enforces hard caps on food buff contributions:
- `damage_mult`: Cap at +12% (+0.12).
- `ranged_damage_mult`: Cap at +12% (+0.12).
- `atk_speed_mult`: Cap at +10% (+0.10).
- `crit_chance`: Cap at +6.0% (+0.06).
- `crit_dmg_mult`: Cap at +16% (+0.16).
- `armor_pen`: Cap at +10% (+0.10).
- `def`: Cap at +6 Flat Defense.
- `dmg_reduction`: Cap at +6% (+0.06).
- `magic_res`: Cap at +15% (+0.15).
- `speed_mult`: Cap at +15% (+0.15).
- `jump_mult`: Cap at +15% (+0.15).
- `dash_mult`: Cap at +15% (+0.15).
- `knockback_res`: Cap at +15% (+0.15).
- `hp_regen`: Cap at +2.0 HP/sec.
- `mp_regen`: Cap at +2.0 MP/sec.
- `mana_cost_reduction`: Cap at +15% (+0.15).
- `luck`: Cap at +10% (+0.10).
- `gathering_speed`: Cap at +20% (+0.20).
- `fishing_power`: Cap at +15% (+0.15).

### 2.15 Philippine Agricultural Simulation, Soil Tilling & 8 Native Crops
- **Soil Hydration & Tilling**:
  - Dirt blocks can be tilled using Bamboo or Iron Hoes into Farmland (`TILE_FARMLAND`).
  - Hydration Check: If water (`TILE_WATER`) is present within a 4-block horizontal radius, Farmland converts to Hydrated Farmland (`TILE_FARMLAND_WET`).
  - Watering Can: Imbues dry farmland with moisture directly.
- **Crop Lifecycle**:
  - 8 Native Philippine Crops: Rice (Palay), Garlic (Bawang), Onion (Sibuyas), Ginger (Luya), Eggplant (Talong), String Beans (Sitaw), Tamarind (Sampalok), Calamansi.
  - 4 Growth Stages (Stage 0: Seedling, Stage 1: Sprout, Stage 2: Vegetative, Stage 3: Mature Harvestable).
  - Illumination Rule: Crops require surface sunlight or cave torchlight within 5 blocks to advance growth stages. Stage advance occurs every game morning at Dawn.
  - Harvest: Yields 2 to 4 food ingredients and 1 to 2 seed packets for replanting.

### 2.16 2D Fishing Battle Minigame & 10 Native Philippine Aquatic Species
- **Tug-of-War Mechanics**:
  - Casting fishing rod into deep water pools initiates a bite after 3.0s to 8.0s.
  - Interactive battle window opens: 15.0s urgency timer, Reel Progress meter (0% to 100%), and Line Tension meter (0% to 100%).
  - Right-Click reeling advances progress (+4% to +8% per click).
  - Fish Thrashing: Fish randomly thrash with red warning indicators. Reeling during a thrash spikes line tension (+15%); line snaps at 100% tension resulting in fish escape.
  - Golden Sweet-Spot: A moving marker along the progress bar awards 1.5x reel speed when timed correctly.
- **10 Native Species**:
  - Common: Dilis (7 clicks), Tilapia (8 clicks).
  - Uncommon: Bangus (11 clicks), Galunggong (12 clicks), Hito (13 clicks).
  - Rare: Maya-Maya (18 clicks), Tambakol (20 clicks).
  - Epic: Tanigue (25 clicks), Dalagang Bukid (26 clicks), Lapu-Lapu (28 clicks).

### 2.17 Chroisen-Style Paperdoll Equipment System & 10 Equipment Slots
- **Equipment Slot Roster**:
  - 10 Dedicated Slots: Head, Chest, Legs, Weapon, and 6 Accessory slots (Ring 1, Ring 2, Amulet, Belt, Charm, Artifact).
  - Active visual paperdoll: Equipping armor updates the player sprite layer rendering helmet, breastplate, and boots directly onto the animated potato model.
- **Recalculation Pipeline**:
  - Whenever an item is equipped, unequipped, enhanced, or affixed, `Equipment.recalculate_stats(playerStats)` iterates across all 10 slots, summing primary attributes, flat bonuses, percentage multipliers, and active passive keywords.

### 2.18 27 Progressive Equipment Sets & Tiered Milestone Synergies
- **Tiered Milestone Bonuses (Torchlight 2 Style)**:
  - Sets grant escalating passive bonuses at 2-piece, 4-piece, and 5-piece thresholds.
- **27 Complete Sets**:
  - 7 Deadly Sins: Pride (celestial nova burst), Greed (+50% coin drops), Lust (charm lifesteal), Envy (steals boss buffs), Gluttony (doubles food buff caps), Wrath (berserk attack speed under 50% HP), Sloth (iron shell defense while stationary).
  - 8 Heavenly Virtues: Humility, Charity, Chastity, Gratitude, Temperance, Kindness, Diligence, Patience.
  - 5 Philippine Cultural / Mythological Sets: Katipunero (+25% bolo/spear damage, sprint stamina), Diwata Bloom (healing flower trail), Bakunawa Eclipse (moonlit void criticals), Sarimanok Regalia (tri-elemental feather projectiles), Tikbalang Trailblazer (+35% mountain path velocity).
  - 7 Dungeon / Progression Sets: Ancient (celestial reversal boost, golden aura), Titan (stomp wave, obsidian aura), Magma (flame trail, ember aura), Cryo (frostbite slow aura), Shadow (evasion step, abyssal aura), Spud (potato growth rate), Cactus (thorns damage return).

### 2.19 Canonical 7-Tier Rarity Engine & Stat Roll Distribution
- **7 Discrete Tiers**:
  1. Common: Grey (#9E9E9E), rank 0, 0 affixes, 1.0x stat multiplier, 55.0% drop weight.
  2. Uncommon: Green (#4CAF50), rank 1, 1 affix, 1.1x stat multiplier, 25.0% drop weight.
  3. Rare: Blue (#2196F3), rank 2, 2 affixes, 1.25x stat multiplier, 12.0% drop weight.
  4. Epic: Purple (#9C27B0), rank 3, 3 affixes, 1.5x stat multiplier, 5.0% drop weight.
  5. Mythic: Orange (#FF9800), rank 4, 4 affixes, 2.0x stat multiplier, 2.0% drop weight. Unique effects enabled.
  6. Legendary: Gold (#FFD700), rank 5, 5 affixes, 2.5x stat multiplier, 0.85% drop weight. Unique effects and affix carving enabled.
  7. Ancient: Crimson / Cyan (#00F0E6 / #F44336), rank 6, 6 affixes, 3.0x stat multiplier, 0.15% drop weight. Full set aura, god-tier affixes, and cleave enabled.

### 2.20 Item Enhancement (+1 to +7) Strategic Risk Curves & Break Risks
- **Enhancement Mechanics**:
  - Weapons and armor can be honed up to +7 at Ignis Vance the Forge Master.
  - Stat multiplier follows: `multiplier = 1.0 + (level / 7.0)`, reaching double stats (2.0x) at +7.
- **Risk Curve**:
  - Levels +1 to +4: Safe (0% break rate).
  - Level +5: 50% success rate, 20% break risk.
  - Level +6: 40% success rate, 25% break risk.
  - Level +7: 30% success rate, 30% break risk.
- **Broken Status & 1 Gold Repair**:
  - Failing a +5 to +7 roll can break the item (`is_broken = true`), rendering it un-equippable.
  - Any trader can restore a broken item to working order for a flat fee of 1 Gold Coin (10,000 Copper).

### 2.21 Affix Engine, Affix Stone Carving & Slot Allotment Caps
- **4-Layer Item Generation Model**:
  - `Base Item + Affixes + Rarity Multiplier + Optional Unique Perk`.
- **Affix Stone Carving**:
  - Available from Morrigan the Void Weaver for Legendary and Ancient items.
  - Consumes an Affix Stone to convert a standard secondary attribute into an Affix Socket.
- **Strict Slot Allotment Caps (`MAX_ADDITIONAL_AFFIX_SLOTS`)**:
  - Common, Uncommon, Rare: 0 additional affix slots allowed.
  - Epic: Maximum 1 additional slot.
  - Legendary: Maximum 1 additional slot.
  - Mythic: Maximum 2 additional slots.
  - Ancient: Maximum 2 additional slots.

### 2.22 Mobs & Boss AI State Machines (33 Mob Types & 5 Boss Titans)
- **Mob Behavioral Archetypes**:
  - Slimes (Green, Purple, Sand, Frost, Corrupt): Passive resting, squish/stretch animation, hop toward player when alerted, bounce on solid walls.
  - Walkers (Zombies, Skeletons, Cultists, Mummies): Horizontal patrolling, sensory radius (12 blocks), obstacle auto-step jumping (detects solid block ahead and hops 1 tile up).
  - Flying Predators (Demon Eye / Night Gazer, Bats): Zero-gravity sinusoidal flight paths, dive-bombing passes, daylight flee-and-despawn behavior.
  - Crawlers (Desert Scorpion, Shadow Crawler): Clings to ceilings and cave walls, dropping down when player passes underneath.
  - Mythological Beasts: Aswang (rapid night stalker, leaps over obstacles, lifesteals on bite).
  - Philippine Livestock: Manok (chicken, wing flap deceleration), Pato (duck, floats on water surfaces), Baboy (wild boar), Kalabaw (high HP pack animal), Kambing (goat).
- **Boss Titans**:
  - Subterranean Mini-Bosses: Lord Malus (Blight), Ignis Colossus (Magma), Cryo Spud (Ice), Necro Tuber (Catacomb).
  - Grand Boss: Sol-Rho the Celestial Titan (Phase 1: Solar flare novas, orbital star beams; Phase 2: Warp blitz, bullet storm spirals, void singularity vortex).

### 2.23 Nomadic Animated Traders, Turtle Shell Shield Defense & 1 Gold Repair
- **Nomadic Traders**:
  - Zephyrion the Wandering Peddler (weapons and rare accessories).
  - Ignis Vance the Forge Master (item enhancement and socket honing).
  - Morrigan the Void Weaver (affix slot carving and dark enchantments).
- **Mutual Exclusion & Turtle Shell Defense**:
  - Only one nomadic trader may be present in the world at any time.
  - When any hostile mob enters a 3-block radius (96 pixels), the trader withdraws into an invulnerable turtle shell defense barrier, reflecting hostile attacks and disabling shop menus until the threat is neutralized.

### 2.24 Housing Validity, Room Enclosure Checks & Village Settlement
- **Room Validation Algorithm (`check_house_validity`)**:
  - Flood fill checks room volume: Minimum 15 tiles, maximum 250 tiles.
  - Required Elements:
    1. Fully enclosed perimeter of solid blocks, wooden platforms, or doors.
    2. Continuous background walling (`wall != WALL_AIR`) with no open air gaps > 4 tiles.
    3. At least one valid entrance/exit door (`TILE_DOOR_CLOSED`, `TILE_DOOR_OPEN`, or platform).
    4. At least one light source (Torch, Fireplace, Candelabra, Chandelier, Lantern).
    5. At least one flat workstation / table (Table, Work Bench, Dresser).
    6. At least one comfort piece (Chair, Bed).
- **Town NPC Migration**:
  - Building valid housing attracts Town NPCs: Guide, Merchant, Nurse (heals player for copper fee), Blacksmith (repairs gear).

### 2.25 HUD Architecture: Hotbars, Hearts, Mana, Clock Badge & Minimap Radar
- **Screen Canvas**: 1280x720 reference resolution, UI Canvas Scaler set to expand or shrink responsively.
- **Top-Left**: 10-slot Hotbar (slots 1-9, 0), slot size 40x40 px, 4px padding, active gold selection frame, numeric stack count badges.
- **Top-Right**:
  - Life Hearts: Red heart icons (20 HP per full heart) + text display `Life: X / Y Lv.Z`.
  - Mana Bar: Azure mana meter with star icon + text `MP: A / B`.
  - Celestial Clock: 12-hour badge displaying game time and phase (e.g. `12:00 PM DAY`, `7:04 PM NIGHT`).
  - Radar Badge: Toggleable mini-map radar (`[M]`).
- **Bottom-Center**: 4 Skill badges showing assigned hotkeys (Q, F, V, R), skill level, and dynamic cooldown radial fill.
- **Top-Left (Toggle)**: F3 Profiler overlay.

### 2.26 Side-by-Side Equipment Comparison Cards ('Katabi') & Tooltips
- **Comparison Trigger**:
  - Hovering over an equippable weapon, armor piece, or accessory while the Character Info panel is open ('C' key) triggers side-by-side comparison mode ('katabi').
- **Dual Card Rendering**:
  - Left Card: Hovered candidate item.
  - Right Card: Currently equipped item in that slot, adorned with a bold gold header badge: `[ CURRENTLY EQUIPPED ]`.
  - Delta Calculations: Primary stat differences are highlighted with colored text (green for improvements `+5 ATK`, red for reductions `-2 DEF`).
  - Boundary Clamping: Both cards are measured and placed side-by-side (`tw1 + 12px gap + tw2`). If overflowing the right screen edge, the entire dual card flips to the left of the cursor.

### 2.27 F3 Real-Time Profiler Overlay & Frame Telemetry
- **Telemetry Readout**:
  - Pressing F3 toggles real-time performance telemetry.
  - Displays: Instantaneous FPS, rolling average FPS (60-frame window), frame delta time (ms), active chunk count, active mob count, projectile count, and microsecond CPU timers for World, Chunks, Lighting, Entities, Projectiles, and UI rendering passes.

### 2.28 Mobile Touch Virtual Controller, Virtual Joystick & Action Clusters
- **Mobile Control Architecture**:
  - Three modes: `auto` (detects touchscreen device), `on` (forced visible), `off` (hidden).
  - Dynamic opacity: 50%, 75%, 100%.
- **Control Layout**:
  - Bottom-Left: Floating dynamic virtual analog joystick with smooth vector return.
  - Bottom-Right: Ergonomic thumb cluster: Attack / Mine primary button, Jump button, Dash button, Quick Heal potion button.
  - Hotbar touch carousel and ripple visual feedback on touch down.

### 2.29 Audio Engine: Synthesized SFX, Dynamic Biome BGM & Narrator Speech
- **Procedural & Synthesized Audio**:
  - Real-time 44.1 kHz PCM audio synthesis for weapon swings, jump impulses, block hits, mob hurts, and level-up chimes.
  - Head-blocked jump suppression: Jump sound only plays if player's head is clear of solid ceilings.
- **Dynamic BGM Manager**:
  - Multi-track background music crossfading smoothly between biomes (Forest, Desert, Snow, Blight, Cavern, Nether Dungeon).
  - Boss Encounter Override: Boss entrance crossfades instantly to high-tempo battle themes.

### 2.30 Multi-Layer Save Engine, HMAC Security Signatures & World Caching
- **Atomic Disk Serialization**:
  - Game saves write to a temporary file (`world.tmp`) and perform an atomic file rename, preventing corruption on sudden power loss or process kill.
  - Backup Rotations: Automatically maintains rotating backup snapshots (`saves/backups/<world>/`).
- **HMAC Anti-Tamper Security**:
  - Character equipment, coin purse, and stats calculate an HMAC-SHA256 signature using `_SAVE_HMAC_PEPPER`.
  - Modifying coins or stats via external text editors triggers signature mismatch detection and safety fallbacks.

### 2.31 Multiplayer Architecture: LAN UDP Discovery & FishNet/Steamworks P2P
- **LAN Discovery & Protocol**:
  - UDP broadcast beacon on port 45454 advertises local host sessions.
  - TCP socket stream exchanges compact binary delta packets for block modifications, player movement, projectile spawns, and mob health sync.
- **Steamworks P2P Plan**:
  - Transition to FishNet / Steamworks.NET using Valve's Steam Datagram Relay (SDR) for seamless friend invites and zero port forwarding.

### 2.32 Modding & DLC Content Pack Extensibility System
- **JSON Mod Manifest**:
  - Extensibility engine scans `mods/` and `dlc/` directories.
  - Reads `mod_manifest.json` declaring custom items, blocks, recipes, weapons, and textures.
  - ModManager registers custom content dynamically into the global Item Registry, Tile Database, and Recipe Book without altering base game files.

---

## 3. Exhaustive Inventory of All Pygame-CE Codebase Classes, Functions & Methods

This section provides a 100% complete census of every class, method, and standalone function across all 65 source files in the Pygame-CE reference codebase (`Potaria_Pygame_Backup` and branch `pygame-engine`).

**Codebase Scope:** 65 Files | 123 Classes | 1170 Class Methods | 153 Standalone Functions.

### Root Files

#### `main.py`
- **Size:** 218082 bytes | **Lines:** 3968 lines
- **Description:** Potaria - The Spudtastic Adventure
- **Classes Defined (1):**
  - **`class PotariaGame`** (Line 137)
    - Methods (37):
      - `def __init__(self)` (Line 138)
      - `def execute_cheat(self, cmd_str)` (Line 307): Executes in-game developer cheat / debugging console command.
      - `def save_game_world(self, create_snapshot, reason, async_save)` (Line 565): Saves current world progress to saves/<active_world_name>/world.json.
      - `def drop_item_into_world(self, item_id, count, world_pos)` (Line 577): Drops an item into the world as a physical DroppedItem entity with throw physics.
      - `def drop_selected_or_held(self, mouse_pos)` (Line 606): Drops currently held cursor item, hovered inventory slot, or active hotbar item into world.
      - `def start_lan_host(self, server_name, room_key)` (Line 626): Initializes authoritative LAN host server and connects local client.
      - `def join_lan_game(self, host_ip, room_key)` (Line 646): Connects to remote LAN host and synchronizes procedural world seed.
      - `def run(self)` (Line 677): Master game loop.
      - `def _pre_load_window_icon(self)` (Line 725): Loads and sets the custom Potaria window icon prior to display creation.
      - `def _apply_window_icon(self)` (Line 739): Applies the official Potaria game icon to the pygame display and Windows HWND.
      - `def get_mouse_pos(self)` (Line 767): Translates window mouse coordinates to virtual screen coordinates.
      - `def window_to_virtual_pos(self, pos)` (Line 774): Translates physical window pixel coordinates to virtual screen coordinates (1280x720).
      - `def toggle_fullscreen(self)` (Line 780): Toggles borderless fullscreen display mode across all game states (prevents screenshot / Win+Shift+S blackout).
      - `def set_fullscreen_mode(self, enabled)` (Line 784): Explicitly sets fullscreen mode (True = Borderless Fullscreen, False = Windowed).
      - `def set_resolution(self, res_str)` (Line 828): Sets display resolution mode (e.g. 1920x1080, 1600x900, 1366x768, 1280x720).
      - `def _apply_graphics_settings(self)` (Line 846): Propagates loaded menu settings into active rendering, camera, particle, combat, and inventory systems.
      - `def set_renderer_mode(self, mode)` (Line 909): Switches the active renderer between hardware (ModernGL) and software via HAL.
      - `def toggle_renderer_mode(self)` (Line 923): Toggles between hardware (ModernGL) and software renderer via HAL.
      - `def return_to_main_menu(self)` (Line 936): Cleanly leaves active session and returns to Main Menu.
      - `def reset_new_session(self, world_name, world_type, difficulty, game_mode, seed)` (Line 978): Reinitializes all gameplay state freshly when creating or starting a new world.
      - `def _execute_menu_action(self, action)` (Line 1093)
      - `def handle_events(self)` (Line 1308)
      - `def _open_or_break_chest(self, tx, ty, world_x, world_y)` (Line 1781): Rolls high-value loot for naturally discovered or drops stored items from placed chests.
      - `def handle_right_click(self, mouse_x, mouse_y)` (Line 1873): Handles fishing, eating food, drinking potions, toggling doors, placing walls, opening chests, or placing blocks.
      - `def teleport_to_dungeon(self)` (Line 2265): Teleports Spud directly to the Nether Dungeon Chamber and summons a Subterranean Mini-Boss!
      - `def get_weapon_attack_cooldown(self, active_item)` (Line 2285): Calculates effective attack interval in seconds based on weapon archetype,
      - `def handle_fishing_action(self, mouse_x, mouse_y)` (Line 2314)
      - `def handle_primary_action(self, mouse_x, mouse_y)` (Line 2472)
      - `def _mine_tile_at_mouse(self, mouse_x, mouse_y, active_item)` (Line 2743)
      - `def _get_tile_debris_color(self, tile_id)` (Line 2843)
      - `def handle_block_placement(self, mouse_x, mouse_y, active)` (Line 2883)
      - `def update_gameplay(self, dt)` (Line 2953)
      - `def _get_zoom_world_surf(self)` (Line 3600)
      - `def render(self)` (Line 3612)
      - `def _render_debug_overlay(self, target_surf)` (Line 3832)
      - `def _render_fps_counter(self, target_surf)` (Line 3858)
      - `def _render_pause_menu(self, target_surf)` (Line 3880)
- **Standalone Functions (1):**
  - `def main()` (Line 3919)

### World & Terrain Systems (`src/world/*`)

#### `src/world/chunk_manager.py`
- **Size:** 51271 bytes | **Lines:** 1056 lines
- **Description:** Potaria - Infinite Chunk-Based Open World Manager
- **Classes Defined (3):**
  - **`class ChunkSection`** (Line 64)
    - Methods (2):
      - `def __init__(self, chunk_x, section_y)` (Line 67)
      - `def bake(self, world)` (Line 75)
  - **`class Chunk`** (Line 250)
    - Methods (11):
      - `def __init__(self, chunk_x, seed, noise_surface, noise_caves, noise_ores, noise_biome)` (Line 251)
      - `def get_tile_local(self, lx, ty)` (Line 265)
      - `def set_tile_local(self, lx, ty, tile_id)` (Line 272)
      - `def get_wall_local(self, lx, ty)` (Line 278)
      - `def set_wall_local(self, lx, ty, wall_id)` (Line 285)
      - `def mark_section_dirty(self, sec_y)` (Line 291)
      - `def mark_all_sections_dirty(self)` (Line 295)
      - `def get_or_bake_section(self, sec_y, world)` (Line 299)
      - `def _generate(self, seed, noise_surface, noise_caves, noise_ores, noise_biome)` (Line 307)
      - `def _carve_grand_biome_dungeon(self, center_gx, brick_tile, wall_id)` (Line 685): Carves out a grand multi-tier biome underground dungeon with entrance gates, wings, bridges, and boss room.
      - `def _carve_sky_citadel(self)` (Line 761): Carves out Sol-Rho's Celestial Sky Citadel high in the celestial atmosphere / space stratum (y = -185..-162).
  - **`class ChunkManager`** (Line 807)
    - Methods (16):
      - `def __init__(self, seed, world_type, world_name)` (Line 808)
      - `def set_world_name(self, world_name)` (Line 827)
      - `def _create_chunk(self, chunk_x)` (Line 831)
      - `def _generate_async(self, chunk_x)` (Line 866)
      - `def has_chunk(self, chunk_x)` (Line 875): Returns True if the chunk at chunk_x is already generated and cached.
      - `def _evict_if_needed(self, keep_around_cx)` (Line 880): Evicts oldest unpinned chunks from RAM to keep memory strictly bounded.
      - `def evict_distant_surfaces(self, cam_cx)` (Line 904): Frees baked Pygame surfaces for chunks beyond visible camera radius to bound RAM usage.
      - `def get_chunk(self, chunk_x)` (Line 915): Retrieves or procedurally generates the chunk at chunk_x.
      - `def get_column_biome(self, gx)` (Line 936): Returns the surface/column biome for a given global X coordinate from cached chunk biomes.
      - `def get_biome_at(self, gx, gy)` (Line 945): Returns the active biome string for the given coordinates.
      - `def get_tile(self, gx, gy)` (Line 956): Retrieves tile ID at global coordinates (gx, gy).
      - `def set_tile(self, gx, gy, tile_id)` (Line 973): Sets tile ID at global coordinates (gx, gy).
      - `def get_wall(self, gx, gy)` (Line 1007): Retrieves background wall ID at global coordinates (gx, gy).
      - `def set_wall(self, gx, gy, wall_id)` (Line 1022)
      - `def ensure_chunks_in_range(self, min_gx, max_gx)` (Line 1036): Pre-generates all chunks spanning min_gx to max_gx.
      - `def get_surface_height(self, gx)` (Line 1049): Returns the procedural surface height (y tile coord) for column gx.

#### `src/world/lighting.py`
- **Size:** 16592 bytes | **Lines:** 372 lines
- **Description:** Terraria Pygame - 2D Dynamic Lighting Engine
- **Classes Defined (1):**
  - **`class LightingEngine`** (Line 26)
    - Methods (7):
      - `def __init__(self, screen_width, screen_height, tile_size, scale)` (Line 27)
      - `def dirty(self)` (Line 62)
      - `def dirty(self, val)` (Line 66)
      - `def _get_radial_offsets(self, intensity, radius)` (Line 71)
      - `def compute_viewport_light(self, world, min_tx, min_ty, max_tx, max_ty, ambient_sunlight, torch_positions, ambient_tint)` (Line 88): Calculates 2D light levels for the current camera viewport using direct column tracing and BFS propagation.
      - `def get_light_level(self, tx, ty)` (Line 344): Returns the computed light intensity level [0..15] for world tile (tx, ty).
      - `def render_lighting(self, target_surf, offset_x, offset_y)` (Line 353): Scales the low-res light surface up smoothly and multiplies onto target_surf.

#### `src/world/noise.py`
- **Size:** 2432 bytes | **Lines:** 77 lines
- **Description:** Terraria Pygame - Fast Procedural Noise Module
- **Classes Defined (1):**
  - **`class PerlinNoise`** (Line 9)
    - Methods (9):
      - `def __init__(self, seed)` (Line 10)
      - `def _fade(self, t)` (Line 16)
      - `def _lerp(self, t, a, b)` (Line 19)
      - `def _grad1d(self, hash_val, x)` (Line 22)
      - `def _grad2d(self, hash_val, x, y)` (Line 25)
      - `def noise1d(self, x)` (Line 31)
      - `def noise2d(self, x, y)` (Line 37)
      - `def fractal1d(self, x, octaves, persistence, lacunarity)` (Line 55)
      - `def fractal2d(self, x, y, octaves, persistence, lacunarity)` (Line 67)

#### `src/world/save_manager.py`
- **Size:** 50336 bytes | **Lines:** 1183 lines
- **Description:** Potaria - World Save & Load Manager (Minecraft-Style Portable JSON)
- **Standalone Functions (23):**
  - `def ensure_saves_dir()` (Line 27)
  - `def get_world_dir(world_name)` (Line 31)
  - `def get_world_file(world_name)` (Line 37)
  - `def get_backup_file(world_name)` (Line 40): Returns path to immediate backup saves/<world_name>/world.json.bak.
  - `def get_backups_dir(world_name)` (Line 44): Returns directory path to rolling snapshots saves/<world_name>/backups/.
  - `def atomic_write_json(target_path, data, indent)` (Line 48): Atomically writes JSON data to target_path using:
  - `def verify_save_data(data)` (Line 68): Validates dictionary structure and HMAC-SHA256 signature integrity.
  - `def verify_save_file(file_path)` (Line 91): Reads a save JSON file and validates its JSON syntax, structure, and integrity.
  - `def prune_backup_snapshots(world_name, max_backups)` (Line 117): Auto-prunes historical snapshots in saves/<world_name>/backups/.
  - `def list_world_backups(world_name)` (Line 142): Returns list of snapshot file paths in saves/<world_name>/backups/ sorted newest first.
  - `def create_backup_snapshot(world_name, game, payload, reason, max_backups)` (Line 155): Creates a timestamped snapshot in saves/<world_name>/backups/world_YYYY-MM-DD_HHMM.json.
  - `def list_saved_worlds()` (Line 197): Returns a list of dictionaries with metadata for all saved worlds.
  - `def extract_save_payload(world_name, game)` (Line 277): Extracts pure Python dictionary snapshots of game, world, inventory, player,
  - `def write_save_payload_to_disk(world_name, payload, chunk_payloads, create_snapshot, reason, max_backups)` (Line 556): Writes pre-extracted save payload and chunk cache files to disk with atomic replacement.
  - `def _save_worker()` (Line 602)
  - `def ensure_save_worker()` (Line 619)
  - `def wait_for_pending_saves(timeout)` (Line 626): Waits for all queued background saves to complete disk commit.
  - `def save_world(world_name, game, create_snapshot, reason, max_backups, async_save)` (Line 632): Serializes the active game session to saves/<world_name>/world.json.
  - `def load_world(world_name, game)` (Line 660): Loads a world from saves/<world_name>/world.json into the running game
  - `def delete_world(world_name)` (Line 1060): Deletes a saved world directory.
  - `def sanitize_world_name(world_name)` (Line 1089): Sanitizes a world name to safe alphanumeric, space, underscore, and hyphen characters.
  - `def can_rename_world(old_name, new_name)` (Line 1096): Validates whether `old_name` can be renamed to `new_name`.
  - `def rename_world(old_name, new_name)` (Line 1138): Renames an existing saved world from `old_name` to `new_name`.

#### `src/world/storage_chest.py`
- **Size:** 10693 bytes | **Lines:** 251 lines
- **Description:** Potaria - Craftable Storage Chest System
- **Classes Defined (1):**
  - **`class StorageChest`** (Line 12)
    - Methods (13):
      - `def __init__(self, tx, ty, capacity, chest_type, is_player_placed)` (Line 13)
      - `def is_empty(self)` (Line 21)
      - `def get_all_items(self)` (Line 24): Returns list of all non-empty ItemStack objects.
      - `def count_wood(self)` (Line 28): Returns total wood count across all wood variants.
      - `def count_item(self, item_id)` (Line 39)
      - `def can_add_item(self, item_id, count)` (Line 51)
      - `def add_item(self, item_id, count, enhancement_level, is_broken, affix_slots, affixes, removed_stats, base_rolls, additional_affix_slots, tags)` (Line 69): Adds items into chest, stacking where applicable. Returns remaining count.
      - `def add_stack(self, stack)` (Line 111): Adds an existing ItemStack into chest.
      - `def quick_stack_from_inventory(self, inventory)` (Line 132): Deposits items from player inventory that already exist in chest.
      - `def deposit_all_from_inventory(self, inventory)` (Line 158): Transfers as many items as possible from inventory into chest.
      - `def take_all_to_inventory(self, inventory)` (Line 183): Transfers all items from chest into player inventory, depositing from back to preserve hotbar.
      - `def to_dict(self)` (Line 200)
      - `def from_dict(cls, data)` (Line 227)

#### `src/world/tiles.py`
- **Size:** 3155 bytes | **Lines:** 71 lines
- **Description:** Potaria - Tile Definitions & Sapling Ecosystem
- **Standalone Functions (6):**
  - `def is_sapling_tile(tile_id)` (Line 40): Returns True if the given tile ID is any tree sapling variant.
  - `def get_sapling_item(tile_id)` (Line 45): Returns the dropped item identifier for a given sapling tile ID, or None if not a sapling.
  - `def get_sapling_tile(item_id)` (Line 50): Returns the corresponding world tile ID for a given sapling item identifier, or None if not a sapling item.
  - `def is_wood_tile(tile_id)` (Line 58): Returns True if the given tile ID is any wood variant (trunk or solid block).
  - `def is_trunk_tile(tile_id)` (Line 63): Returns True if the given tile ID is any tree trunk variant.
  - `def is_leaf_tile(tile_id)` (Line 68): Returns True if the given tile ID is any tree leaves / foliage variant.

#### `src/world/world.py`
- **Size:** 102364 bytes | **Lines:** 2052 lines
- **Description:** Potaria - World Manager (Boundless Open World)
- **Classes Defined (1):**
  - **`class World`** (Line 42)
    - Methods (53):
      - `def __init__(self, asset_factory, seed, world_type, world_name)` (Line 43)
      - `def set_world_name(self, world_name)` (Line 219)
      - `def get_biome_spawn(self, player_idx)` (Line 224): Returns surface spawn coordinates in different biomes for LMS / PvP mode.
      - `def update(self, dt)` (Line 232)
      - `def get_tile(self, tx, ty)` (Line 308)
      - `def has_chunk(self, chunk_x)` (Line 311)
      - `def set_tile(self, tx, ty, tile_id)` (Line 314)
      - `def get_wall(self, tx, ty)` (Line 327)
      - `def set_wall(self, tx, ty, wall_id)` (Line 330)
      - `def get_surface_height(self, tx)` (Line 333)
      - `def get_biome_at(self, tx, ty)` (Line 336)
      - `def get_biome_at_world(self, world_x, world_y)` (Line 339)
      - `def is_water(self, tx, ty)` (Line 344): Returns True if the tile at (tx, ty) is liquid water.
      - `def is_water_world(self, wx, wy)` (Line 348): Returns True if world pixel coordinates are inside liquid water.
      - `def get_water_rects_in_bounds(self, rect_world_px)` (Line 354): Returns bounding rects of liquid water tiles overlapping rect_world_px.
      - `def _get_wood_drop_for_tile(self, tile_id, tx, ty, is_player_placed)` (Line 375): Returns the species-appropriate wood drop item ID based on tile_id or biome.
      - `def _get_leaf_drop_for_tile(self, tile_id, tx, ty, is_player_placed)` (Line 394): Returns the species-appropriate leaf drop item ID based on tile_id or biome.
      - `def fell_tree(self, start_tx, start_ty)` (Line 413): Fells tree starting from (start_tx, start_ty) upwards.
      - `def decay_trees_daily(self, game)` (Line 534): Advances tree decay by a daily step.
      - `def grow_plants_daily(self, game)` (Line 552): Called once per day at dawn/daylight transition: grows planted/wild saplings in sunlight into full trees.
      - `def can_mine_tile(self, tx, ty)` (Line 715): Returns True if the block at (tx, ty) can be legally mined and broken.
      - `def damage_tile_at(self, tx, ty, power)` (Line 725)
      - `def _check_tree_decay(self, tx, ty)` (Line 886): Scans for unsupported trunk blocks and canopy leaves after a tree block is broken, starting their decay.
      - `def update_tree_decay(self, dt, game)` (Line 990): Ticks down decaying blocks, darkens them, and drops items on expiration.
      - `def place_tile(self, tx, ty, tile_id, chest_type)` (Line 1085)
      - `def toggle_door(self, tx, ty, player_rect)` (Line 1167): Toggles a wooden door between open and closed state without trapping the player.
      - `def place_wall(self, tx, ty, wall_id)` (Line 1181): Places a background wall at (tx, ty).
      - `def is_farmland_near_water(self, gx, gy)` (Line 1191): Checks if farmland tile is within 4 horizontal tiles of water for permanent hydration.
      - `def has_crop_light(self, gx, gy)` (Line 1199): Returns True if crop has sufficient light: natural sky light OR artificial torchlight.
      - `def till_soil(self, gx, gy)` (Line 1221): Tills dirt or grass into farmland using a hoe.
      - `def water_soil(self, gx, gy, duration)` (Line 1234): Hydrates dry farmland with a watering can for duration seconds.
      - `def plant_crop(self, gx, gy, seed_id)` (Line 1245): Plants a crop seed on farmland.
      - `def harvest_crop(self, gx, gy)` (Line 1272): Harvests mature crop or wild plant, returning drops list [(item, count), ...].
      - `def get_crop_sprite(self, crop_name, stage)` (Line 1296): Returns pre-scaled 32x32 sprite surface for given crop and growth stage (0-3).
      - `def update_crops(self, dt)` (Line 1308): Updates crop growth stages, farmland hydration, and wild crop population.
      - `def water_open_farmland(self)` (Line 1368): Rain/Weather Hook: automatically hydrates all outdoor farmland exposed to sky.
      - `def is_furnace_busy(self, gx, gy)` (Line 1382): Returns True if the furnace at (gx, gy) is actively cooking.
      - `def get_cooking_duration(self, item_id)` (Line 1387): Returns cooking duration in seconds based on food rarity tier.
      - `def start_furnace_cooking(self, gx, gy, item_id, count, station_type)` (Line 1402): Starts a timed cooking job on a furnace or fireplace.
      - `def update_furnaces(self, dt, particle_system)` (Line 1417): Updates active cooking jobs across all furnaces and hearths.
      - `def collect_furnace_food(self, gx, gy, inventory)` (Line 1437): Collects cooked food if ready, or returns remaining cooking time.
      - `def check_house_validity(self, tx, ty, visited_cache)` (Line 1452): Validates if (tx, ty) belongs to a fully sheltered, furnished, and illuminated
      - `def check_shelter(self, tx, ty, radius)` (Line 1583): Checks if (tx, ty) is part of a valid sheltered house with walls, door, and torch.
      - `def check_and_spawn_town_npcs(self, player, inventory, asset_factory, sound_manager, combat)` (Line 1605): Periodically scans surrounding player-built houses and settles eligible Town NPCs.
      - `def spawn_mystic_trader(self, player, asset_factory, sound_manager, duration, trader_type)` (Line 1687): Spawns one of three specialized wandering traders far from the player (15 to 35 blocks away).
      - `def update_town_npcs(self, dt, player, inventory, asset_factory, sound_manager, combat)` (Line 1768): Updates AI for active Town NPCs and Mystic Wandering Trader.
      - `def render_town_npcs(self, target_surf, camera, player)` (Line 1794): Renders Town NPCs and their name badges.
      - `def get_npc_at(self, world_x, world_y, radius)` (Line 1804): Returns the TownNPC closest to (world_x, world_y) within reach radius, if any.
      - `def is_tile_solid(self, tx, ty)` (Line 1816): Returns True if the tile at (tx, ty) is solid.
      - `def get_solid_rects_in_bounds(self, rect_world_px)` (Line 1821)
      - `def emit_fireplace_smoke(self, particle_system, cam_rect)` (Line 1844): Emits subtle rising smoke and warm embers from active fireplaces.
      - `def render(self, target_surf, camera, draw_water)` (Line 1855)
      - `def render_water(self, target_surf, camera)` (Line 2023): Renders foreground aquatic animated water surfaces and transparent submerged volume pass.

#### `src/world/world_cache.py`
- **Size:** 12818 bytes | **Lines:** 329 lines
- **Description:** Potaria - World-Scoped Exploration Cache Manager
- **Classes Defined (1):**
  - **`class WorldCache`** (Line 33) - Manages disk caching of explored chunks and lighting data within a world save folder.
    - Methods (19):
      - `def __init__(self, world_name, base_dir)` (Line 36)
      - `def set_world_name(self, world_name)` (Line 55)
      - `def _init_paths(self)` (Line 59)
      - `def _ensure_manifest(self)` (Line 73): Creates or validates the world cache manifest file.
      - `def _atomic_write_json(self, target_path, data)` (Line 106): Atomically writes JSON data to disk using temporary file replacement.
      - `def _chunk_file_path(self, chunk_x)` (Line 123)
      - `def _lighting_file_path(self, chunk_x)` (Line 126)
      - `def has_chunk_cache(self, chunk_x)` (Line 129)
      - `def load_chunk_data(self, chunk_x, expected_seed)` (Line 133): Loads and validates cached chunk dictionary from disk, or None if invalid/corrupt.
      - `def save_chunk(self, chunk_x, chunk, seed)` (Line 189): Serializes chunk tiles, walls, sky structures, and column metadata safely to cache.
      - `def has_lighting_cache(self, chunk_x)` (Line 218)
      - `def load_lighting_data(self, chunk_x, expected_version)` (Line 222)
      - `def save_lighting(self, chunk_x, lighting_data)` (Line 259): Saves explored fog-of-war masks or lighting snapshot for chunk atomically.
      - `def get_cached_chunk_count(self)` (Line 274)
      - `def get_cache_size_bytes(self)` (Line 280)
      - `def clear_chunks_cache(self)` (Line 290): Clears all cached chunk terrain files for this world.
      - `def clear_lighting_cache(self)` (Line 299): Clears all cached lighting files for this world.
      - `def clear_cache(self)` (Line 308): Clears all cached chunk and lighting files for this world, leaving authoritative saves intact.
      - `def get_telemetry(self)` (Line 313): Returns diagnostic telemetry metrics for cache usage.
- **Standalone Functions (1):**
  - `def clean_folder_name(name)` (Line 28)

#### `src/world/world_gen.py`
- **Size:** 6742 bytes | **Lines:** 172 lines
- **Description:** Potaria - Procedural World Generator
- **Standalone Functions (1):**
  - `def generate_terrain(width, height, seed)` (Line 19): Generates a full 2D tile map and background wall map with a random seed.

### Entity & Actor Systems (`src/entities/*`)

#### `src/entities/boss.py`
- **Size:** 83698 bytes | **Lines:** 1803 lines
- **Description:** Potaria - Boss Entity System: Dungeon Mini-Bosses & Souls-Like Grand Boss
- **Classes Defined (6):**
  - **`class DungeonMiniBoss`** (Line 23) - Base class for subterranean dungeon mini-boss encounters.
    - Methods (20):
      - `def __init__(self, x, y, asset_factory, sound_manager, name, max_hp, damage, sprite_key, proj_key, defense)` (Line 25)
      - `def scale_to_player(self, player_level, player_atk, rematch_multiplier)` (Line 78): Dynamically scales mini-boss HP, defense, and damage to player progression and rematch tier.
      - `def apply_burn(self, dps, duration)` (Line 89)
      - `def apply_bleed(self, dps, duration)` (Line 93)
      - `def update_dots(self, dt)` (Line 97): Ticks active burn and bleed DoT timers and inflicts periodic tick damage to boss.
      - `def rect(self)` (Line 117)
      - `def center_x(self)` (Line 123)
      - `def center_y(self)` (Line 127)
      - `def is_alive(self)` (Line 131)
      - `def alive(self)` (Line 135)
      - `def take_damage(self, amount, knockback_vx, knockback_vy, ignore_defense)` (Line 138)
      - `def update(self, dt, world, player, particle_system, camera, combat)` (Line 173)
      - `def _step_pattern(self, dt, player, particle_system, camera)` (Line 295): Steps multi-wave bullet-hell streams (subclasses implement unique behaviors).
      - `def _cast_attack(self, player, particle_system, camera)` (Line 299)
      - `def get_projectiles_sync_data(self, player)` (Line 313): Serializes active projectiles on host for network broadcast.
      - `def sync_projectiles(self, proj_data_list)` (Line 326): Reconciles client projectiles from authoritative host snapshot.
      - `def update_client_projectiles(self, dt, player, particle_system, camera, combat)` (Line 353): Updates and handles projectile dodging/grazing on LAN client.
      - `def _trail_color(self)` (Line 390)
      - `def render(self, target_surf, camera, renderer)` (Line 393)
      - `def render_boss_bar(self, target_surf, font, font_title, bar_y)` (Line 413)
  - **`class LordMalus`** (Line 487)
    - Methods (6):
      - `def __init__(self, x, y, asset_factory, sound_manager)` (Line 489)
      - `def _trail_color(self)` (Line 497)
      - `def _step_pattern(self, dt, player, particle_system, camera)` (Line 500)
      - `def _cast_attack(self, player, particle_system, camera)` (Line 538)
      - `def cast_blight_apocalypse(self, player, particle_system, camera)` (Line 588): Lord Malus Signature (M4): Blight Apocalypse with clearly marked safe corridor.
      - `def cast_signature_attack(self, player, particle_system, camera)` (Line 607)
  - **`class IgnisColossus`** (Line 611)
    - Methods (6):
      - `def __init__(self, x, y, asset_factory, sound_manager)` (Line 613)
      - `def _trail_color(self)` (Line 621)
      - `def _step_pattern(self, dt, player, particle_system, camera)` (Line 624)
      - `def _cast_attack(self, player, particle_system, camera)` (Line 648)
      - `def cast_caldera_catastrophe(self, player, particle_system, camera, slam_step)` (Line 703): Ignis Colossus Signature (I4): Caldera Catastrophe progressive seismic shockwaves.
      - `def cast_signature_attack(self, player, particle_system, camera)` (Line 720)
  - **`class CryoSpud`** (Line 724)
    - Methods (6):
      - `def __init__(self, x, y, asset_factory, sound_manager)` (Line 726)
      - `def _trail_color(self)` (Line 734)
      - `def _step_pattern(self, dt, player, particle_system, camera)` (Line 737)
      - `def _cast_attack(self, player, particle_system, camera)` (Line 791)
      - `def cast_absolute_zero(self, player, particle_system, camera)` (Line 834): Cryo-Spud Signature (C4): Absolute Zero contracting ring with safe escape gap.
      - `def cast_signature_attack(self, player, particle_system, camera)` (Line 851)
  - **`class NecroTuber`** (Line 855)
    - Methods (6):
      - `def __init__(self, x, y, asset_factory, sound_manager)` (Line 857)
      - `def _trail_color(self)` (Line 865)
      - `def _step_pattern(self, dt, player, particle_system, camera)` (Line 868)
      - `def _cast_attack(self, player, particle_system, camera)` (Line 897)
      - `def cast_kingdom_of_the_unburied(self, player, particle_system, camera)` (Line 947): Necro-Tuber Signature (N4): Kingdom of the Unburied lane curtains and sweeping scythes.
      - `def cast_signature_attack(self, player, particle_system, camera)` (Line 965)
  - **`class GrandBossSolRho`** (Line 972)
    - Methods (24):
      - `def __init__(self, x, y, asset_factory, sound_manager, party_size, base_p1_hp, base_p2_hp)` (Line 981)
      - `def scale_to_player(self, player_level, player_atk, rematch_multiplier)` (Line 1056): Dynamically scales Grand Boss HP, defense, and damage to player progression and rematch tier.
      - `def apply_burn(self, dps, duration)` (Line 1071)
      - `def apply_bleed(self, dps, duration)` (Line 1075)
      - `def update_dots(self, dt)` (Line 1079): Ticks active burn and bleed DoT timers and inflicts periodic tick damage to grand boss.
      - `def rect(self)` (Line 1099)
      - `def center_x(self)` (Line 1105)
      - `def center_y(self)` (Line 1109)
      - `def is_alive(self)` (Line 1113)
      - `def alive(self)` (Line 1117)
      - `def take_damage(self, amount, knockback_vx, knockback_vy, ignore_defense)` (Line 1120)
      - `def update(self, dt, world, player, particle_system, camera, combat)` (Line 1166)
      - `def _step_pattern(self, dt, player, particle_system, camera)` (Line 1362)
      - `def _cast_phase1_attack(self, player, particle_system, camera)` (Line 1448)
      - `def _cast_phase2_attack(self, player, particle_system, camera)` (Line 1490)
      - `def _cast_warp_blitz_bullet_storm(self, player, particle_system, camera)` (Line 1518): Detonates a 360-degree starburst nova + aimed homing swarm following warp blitz.
      - `def _cast_solar_orbs(self, player, particle_system)` (Line 1536)
      - `def _cast_void_meteors(self, player, particle_system, camera)` (Line 1557)
      - `def _cast_singularity(self, player, particle_system, camera)` (Line 1568)
      - `def get_projectiles_sync_data(self, player)` (Line 1581): Serializes active projectiles on host for network broadcast.
      - `def sync_projectiles(self, proj_data_list)` (Line 1594): Reconciles client projectiles from authoritative host snapshot.
      - `def update_client_projectiles(self, dt, player, particle_system, camera, combat)` (Line 1628): Updates and handles projectile dodging/grazing on LAN client.
      - `def render(self, target_surf, camera, renderer)` (Line 1665)
      - `def render_boss_bar(self, target_surf, font, font_title, bar_y)` (Line 1687)
- **Standalone Functions (1):**
  - `def create_boss_by_type(boss_type, x, y, asset_factory, sound_manager, party_size)` (Line 1798): Instantiates a boss entity by its string identifier.

#### `src/entities/bullet_hell.py`
- **Size:** 33401 bytes | **Lines:** 890 lines
- **Description:** Potaria - Bullet-Hell Shooter Engine & Projectile Systems
- **Classes Defined (2):**
  - **`class BossProjectile`** (Line 148) - Universal bullet-hell projectile featuring:
    - Methods (9):
      - `def __init__(self, x, y, vx, vy, sprite, damage, radius, life, p_type, gravity, core_radius, color, core_color, glow_color, shape, wave_amplitude, wave_frequency, curve_rate, accel, delay_move, p_id, reflectable, reflected)` (Line 157)
      - `def reflect(self, target_x, target_y, damage_mult)` (Line 230): Reflects this eligible projectile back towards (target_x, target_y).
      - `def rect(self)` (Line 275): Authoritative lethal core hitbox.
      - `def visual_rect(self)` (Line 282): Full visual bounding rect.
      - `def graze_rect(self)` (Line 289): Perimeter graze bounding rect for precision dodging rewards.
      - `def update(self, dt, player)` (Line 295)
      - `def render(self, target_surf, camera)` (Line 366)
      - `def to_sync_dict(self)` (Line 398): Serializes bullet state for multiplayer network broadcast.
      - `def from_sync_dict(cls, d, sprite)` (Line 427): Reconstructs projectile from authoritative host sync packet.
  - **`class BulletHellPatterns`** (Line 462) - Mathematical generator for rich geometric and dynamic bullet patterns.
    - Methods (16):
      - `def spawn_concentric_ring(cx, cy, count, speed, color, core_color, radius, damage, base_angle, gaps, shape)` (Line 466): Expanding concentric ring with designated dodge gaps.
      - `def spawn_spiral_step(cx, cy, arms, current_angle, speed, color, core_color, radius, damage, shape, curve_rate, accel)` (Line 513): Single time-step of a rotating multi-arm spiral barrage.
      - `def spawn_aimed_spread(cx, cy, target_x, target_y, count, spread_angle_deg, speed, color, core_color, radius, damage, shape)` (Line 536): Aimed fan of projectiles centered on the player's vector.
      - `def spawn_snowflake_burst(cx, cy, points, speed, color, core_color, radius, damage, offset_angle)` (Line 566): Symmetrical 16-point geometric crystalline snowflake burst.
      - `def spawn_undulating_stream(cx, cy, angle, speed, count, wave_amp, wave_freq, color, core_color, radius, damage)` (Line 588): High-velocity serpentine sine-wave stream.
      - `def spawn_criss_cross_curtains(target_x, target_y, count, speed, color, core_color, damage)` (Line 612): Perpendicular criss-crossing bullet grids forming moving dodge corridors.
      - `def spawn_homing_swarm(cx, cy, target_x, target_y, count, speed, color, core_color, radius, damage)` (Line 642): Cluster of tracking shadow wisps.
      - `def spawn_meteor_curtain(target_x, target_y, count, spread_w, speed_y, color, damage)` (Line 666): Cascading angled meteor curtain falling across the battlefield.
      - `def spawn_warp_nova(cx, cy, count, speed, color, core_color, radius, damage)` (Line 690): Omni-directional 360-degree starburst nova following a warp/blitz.
      - `def spawn_blight_apocalypse(cx, cy, player_x, player_y, count, speed, damage, is_violet)` (Line 712): Lord Malus Signature (M4): Blight Apocalypse.
      - `def spawn_blight_constellation(cx, cy, player_x, player_y, count, speed, damage)` (Line 750): Lord Malus (M1): Blight Constellation.
      - `def spawn_rotting_roots(target_x, target_y, count, damage)` (Line 770): Lord Malus (M2): Rotting Roots.
      - `def spawn_caldera_catastrophe(cx, cy, slam_step, count, damage)` (Line 791): Ignis Colossus Signature (I4): Caldera Catastrophe.
      - `def spawn_absolute_zero(cx, cy, radius_corridor, count, speed, damage)` (Line 824): Cryo-Spud Signature (C4): Absolute Zero.
      - `def spawn_frozen_clock(cx, cy, arms, angle, speed, damage, reversed_dir)` (Line 850): Cryo-Spud (C3): Frozen Clock.
      - `def spawn_kingdom_of_the_unburied(cx, cy, player_x, player_y, count, speed, damage)` (Line 866): Necro-Tuber Signature (N4): Kingdom of the Unburied.
- **Standalone Functions (2):**
  - `def get_bullet_surface(shape, color, core_color, radius, angle_deg)` (Line 18): Returns an optimized pre-rendered bullet surface from cache.
  - `def _get_next_proj_id()` (Line 142)

#### `src/entities/dropped_item.py`
- **Size:** 4742 bytes | **Lines:** 120 lines
- **Description:** Terraria Pygame - Dropped Item Entity
- **Classes Defined (1):**
  - **`class DroppedItem`** (Line 11)
    - Methods (4):
      - `def __init__(self, item_id, count, world_x, world_y, asset_factory, vx, vy)` (Line 12)
      - `def rect(self)` (Line 35)
      - `def update(self, dt, world, player)` (Line 38)
      - `def render(self, target_surf, camera)` (Line 113)

#### `src/entities/mob.py`
- **Size:** 70452 bytes | **Lines:** 1712 lines
- **Description:** Terraria Pygame - Mobs & Enemy AI System
- **Classes Defined (33):**
  - **`class RockProjectile`** (Line 18) - Ballistic boulder thrown by RockZombie.
    - Methods (4):
      - `def __init__(self, x, y, vx, vy, damage, radius)` (Line 20)
      - `def rect(self)` (Line 29)
      - `def update(self, dt, world)` (Line 32)
      - `def render(self, target_surf, camera)` (Line 43)
  - **`class Mob`** (Line 51) - Base class for all Terraria monsters.
    - Methods (14):
      - `def __init__(self, x, y, width, height, max_hp, damage, name, defense)` (Line 53)
      - `def apply_burn(self, dps, duration)` (Line 90)
      - `def apply_bleed(self, dps, duration)` (Line 94)
      - `def update_dots(self, dt)` (Line 98): Ticks active burn and bleed DoT timers and inflicts periodic tick damage.
      - `def rect(self)` (Line 118)
      - `def center_x(self)` (Line 124)
      - `def center_y(self)` (Line 128)
      - `def is_alive(self)` (Line 132)
      - `def alive(self)` (Line 136)
      - `def scale_to_player(self, player_level, player_power)` (Line 139): Dynamically scales mob health, damage, and defense based on player progression.
      - `def take_damage(self, amount, knockback_vx, knockback_vy, ignore_defense)` (Line 162): Applies damage and knockback, accounting for mob defense.
      - `def render_health_bar(self, target_surf, camera)` (Line 184): Draws miniature health bar above mob when recently damaged.
      - `def update_water_buoyancy(self, world)` (Line 195): Checks lower-body water intersection and applies half buoyancy (slow sinking) with fluid drag.
      - `def apply_water_overlay(self, surf)` (Line 219): Returns sprite surface directly without tinting transparent bounding-box pixels blue.
  - **`class SlimeMob`** (Line 226)
    - Methods (3):
      - `def __init__(self, x, y, asset_factory, sprite_key, max_hp, damage, name, speed_mult)` (Line 227)
      - `def update(self, dt, world, player)` (Line 243)
      - `def render(self, target_surf, camera)` (Line 348)
  - **`class GreenSlime`** (Line 371)
    - Methods (1):
      - `def __init__(self, x, y, asset_factory)` (Line 373)
  - **`class PurpleSlime`** (Line 377)
    - Methods (1):
      - `def __init__(self, x, y, asset_factory)` (Line 379)
  - **`class SandSlime`** (Line 383)
    - Methods (1):
      - `def __init__(self, x, y, asset_factory)` (Line 385)
  - **`class FrostSlime`** (Line 389)
    - Methods (1):
      - `def __init__(self, x, y, asset_factory)` (Line 391)
  - **`class CorruptSlime`** (Line 395)
    - Methods (1):
      - `def __init__(self, x, y, asset_factory)` (Line 397)
  - **`class WalkerMob`** (Line 405)
    - Methods (3):
      - `def __init__(self, x, y, asset_factory, sprite_key, max_hp, damage, name, speed)` (Line 406)
      - `def update(self, dt, world, player)` (Line 421)
      - `def render(self, target_surf, camera)` (Line 521)
  - **`class Zombie`** (Line 570)
    - Methods (1):
      - `def __init__(self, x, y, asset_factory)` (Line 572)
  - **`class IceZombie`** (Line 576)
    - Methods (1):
      - `def __init__(self, x, y, asset_factory)` (Line 578)
  - **`class Mummy`** (Line 582)
    - Methods (1):
      - `def __init__(self, x, y, asset_factory)` (Line 584)
  - **`class Skeleton`** (Line 588)
    - Methods (1):
      - `def __init__(self, x, y, asset_factory)` (Line 590)
  - **`class BlightCultist`** (Line 594)
    - Methods (1):
      - `def __init__(self, x, y, asset_factory)` (Line 596)
  - **`class Aswang`** (Line 600)
    - Methods (1):
      - `def __init__(self, x, y, asset_factory)` (Line 602)
  - **`class Goblin`** (Line 606)
    - Methods (1):
      - `def __init__(self, x, y, asset_factory)` (Line 608)
  - **`class PassiveAnimalMob`** (Line 622) - Base class for friendly, non-hostile Philippine land animals & livestock.
    - Methods (4):
      - `def __init__(self, x, y, width, height, max_hp, name, speed, sprite_key, asset_factory)` (Line 624)
      - `def take_damage(self, amount, knockback_vx, knockback_vy, ignore_defense)` (Line 648)
      - `def update(self, dt, world, player)` (Line 655)
      - `def render(self, target_surf, camera)` (Line 752)
  - **`class ManokMob`** (Line 771) - Native Philippine Chicken / Rooster with flutter falling.
    - Methods (2):
      - `def __init__(self, x, y, asset_factory)` (Line 774)
      - `def update(self, dt, world, player)` (Line 778)
  - **`class PatoMob`** (Line 785) - Native Philippine Duck / Pato (Muscovy duck with iconic red caruncles and natural plumage variants).
    - Methods (2):
      - `def __init__(self, x, y, asset_factory, variant)` (Line 788)
      - `def update(self, dt, world, player)` (Line 797)
  - **`class BaboyMob`** (Line 805) - Native Philippine Pig / Baboy-damo.
    - Methods (1):
      - `def __init__(self, x, y, asset_factory)` (Line 808)
  - **`class KalabawMob`** (Line 813) - National Carabao / Water Buffalo with majestic horns and high resilience.
    - Methods (1):
      - `def __init__(self, x, y, asset_factory)` (Line 816)
  - **`class KambingMob`** (Line 822) - Native Philippine Goat with agile high jumping.
    - Methods (1):
      - `def __init__(self, x, y, asset_factory)` (Line 825)
  - **`class DemonEye`** (Line 834)
    - Methods (3):
      - `def __init__(self, x, y, asset_factory)` (Line 836)
      - `def update(self, dt, world, player)` (Line 848)
      - `def render(self, target_surf, camera)` (Line 895)
  - **`class BatMob`** (Line 915)
    - Methods (3):
      - `def __init__(self, x, y, asset_factory, sprite_key, max_hp, damage, name)` (Line 916)
      - `def update(self, dt, world, player)` (Line 925)
      - `def render(self, target_surf, camera)` (Line 982)
  - **`class CaveBat`** (Line 1000)
    - Methods (1):
      - `def __init__(self, x, y, asset_factory)` (Line 1002)
  - **`class IceBat`** (Line 1006)
    - Methods (1):
      - `def __init__(self, x, y, asset_factory)` (Line 1008)
  - **`class CrawlerMob`** (Line 1016)
    - Methods (3):
      - `def __init__(self, x, y, asset_factory, sprite_key, max_hp, damage, name, speed)` (Line 1017)
      - `def update(self, dt, world, player)` (Line 1026)
      - `def render(self, target_surf, camera)` (Line 1111)
  - **`class DesertScorpion`** (Line 1130)
    - Methods (1):
      - `def __init__(self, x, y, asset_factory)` (Line 1132)
  - **`class ShadowCrawler`** (Line 1136)
    - Methods (1):
      - `def __init__(self, x, y, asset_factory)` (Line 1138)
  - **`class RockZombie`** (Line 1146)
    - Methods (2):
      - `def __init__(self, x, y, asset_factory)` (Line 1148)
      - `def update(self, dt, world, player)` (Line 1153)
  - **`class ShieldWeaver`** (Line 1172)
    - Methods (4):
      - `def __init__(self, x, y, asset_factory)` (Line 1174)
      - `def update(self, dt, world, player)` (Line 1186)
      - `def _cleanup_barriers(self, world)` (Line 1260)
      - `def render(self, target_surf, camera)` (Line 1266)
  - **`class DiggerMob`** (Line 1284)
    - Methods (3):
      - `def __init__(self, x, y, asset_factory)` (Line 1286)
      - `def update(self, dt, world, player)` (Line 1297)
      - `def render(self, target_surf, camera)` (Line 1369)
  - **`class NightEliteMob`** (Line 1388) - Champion of the Night - Formidable nightly elite mob spawning once per night.
    - Methods (3):
      - `def __init__(self, x, y, asset_factory, archetype, skill)` (Line 1401)
      - `def update(self, dt, world, player)` (Line 1474)
      - `def render(self, target_surf, camera)` (Line 1616)
- **Standalone Functions (2):**
  - `def _is_solid(world, tx, ty)` (Line 13)
  - `def create_mob_by_type(mob_type, x, y, asset_factory)` (Line 1707): Factory creating an authoritative or synced mob instance by its string identifier.

#### `src/entities/npc.py`
- **Size:** 34336 bytes | **Lines:** 709 lines
- **Description:** Potaria - Town NPCs & Friendly Villagers System
- **Classes Defined (9):**
  - **`class TownNPC`** (Line 32)
    - Methods (9):
      - `def __init__(self, name, npc_type, x, y, asset_factory, sound_manager, home_tile)` (Line 33)
      - `def rect(self)` (Line 69)
      - `def center_x(self)` (Line 75)
      - `def center_y(self)` (Line 79)
      - `def can_interact(self, player)` (Line 82): Returns True if the player is within conversational speaking distance.
      - `def update(self, dt, world)` (Line 87)
      - `def render(self, target_surf, camera, player)` (Line 167)
      - `def to_dict(self)` (Line 208)
      - `def from_dict(cls, data, asset_factory, sound_manager)` (Line 218)
  - **`class GuideNPC`** (Line 248)
    - Methods (2):
      - `def __init__(self, name, npc_type, x, y, asset_factory, sound_manager, home_tile)` (Line 249)
      - `def get_advice(self, player, world, combat)` (Line 252)
  - **`class MerchantNPC`** (Line 273)
    - Methods (2):
      - `def __init__(self, name, npc_type, x, y, asset_factory, sound_manager, home_tile)` (Line 274)
      - `def get_quote(self)` (Line 287)
  - **`class NurseNPC`** (Line 300)
    - Methods (3):
      - `def __init__(self, name, npc_type, x, y, asset_factory, sound_manager, home_tile)` (Line 301)
      - `def calculate_heal_cost(self, player)` (Line 304)
      - `def heal_player(self, player, inventory)` (Line 310)
  - **`class BlacksmithNPC`** (Line 334)
    - Methods (2):
      - `def __init__(self, name, npc_type, x, y, asset_factory, sound_manager, home_tile)` (Line 335)
      - `def hone_weapon(self, player, inventory)` (Line 344): Tempers player's currently held weapon to grant +15% ATK and +10% Attack Speed.
  - **`class MysticTraderNPC`** (Line 378)
    - Methods (11):
      - `def __init__(self, name, npc_type, x, y, asset_factory, sound_manager, home_tile, duration, shop_catalog)` (Line 379)
      - `def repair_item(self, target_item, inventory)` (Line 393): All Mystic Traders can repair broken gear for 1 Gold Coin (10,000 Copper).
      - `def roll_wares(self)` (Line 398): Rolls 5 weapons/equipment items.
      - `def check_hostile_enemies(self, combat)` (Line 481): Checks for hostile enemies within 7 blocks (224px). Activates/deactivates Turtle Shield.
      - `def can_interact(self, player)` (Line 508): Cannot interact/trade while Turtle Shield is active or when player is too far.
      - `def on_hit(self, damage)` (Line 514): When attacked or impacted, the Turtle Shield deflects attacks with zero damage.
      - `def update(self, dt, world, combat)` (Line 522)
      - `def despawn(self, world)` (Line 565): Teleports away regardless of being caged or enclosed in blocks.
      - `def get_quote(self)` (Line 572)
      - `def render(self, target_surf, camera, player)` (Line 581)
      - `def to_dict(self)` (Line 628)
  - **`class WaresTraderNPC`** (Line 639) - Zephyrion the Wandering Merchant - Specializes in weapons and armor wares.
    - Methods (2):
      - `def __init__(self, name, npc_type, x, y, asset_factory, sound_manager, home_tile, duration, shop_catalog)` (Line 641)
      - `def get_quote(self)` (Line 644)
  - **`class EnhancerTraderNPC`** (Line 657) - Ignis Vance the Grand Artificer - Master of equipment forging and enhancement (+1..+7).
    - Methods (3):
      - `def __init__(self, name, npc_type, x, y, asset_factory, sound_manager, home_tile, duration, shop_catalog)` (Line 659)
      - `def roll_wares(self)` (Line 662)
      - `def get_quote(self)` (Line 673)
  - **`class OccultistTraderNPC`** (Line 686) - Morrigan the Runic Occultist - Carves Affix Slots and sockets Affix Stones into Legendary/Ancient gear.
    - Methods (3):
      - `def __init__(self, name, npc_type, x, y, asset_factory, sound_manager, home_tile, duration, shop_catalog)` (Line 688)
      - `def roll_wares(self)` (Line 691)
      - `def get_quote(self)` (Line 701)

#### `src/entities/particle.py`
- **Size:** 4089 bytes | **Lines:** 104 lines
- **Description:** Terraria Pygame - Particle & Debris System
- **Classes Defined (2):**
  - **`class Particle`** (Line 12)
    - Methods (3):
      - `def __init__(self, x, y, vx, vy, color, size, life, gravity)` (Line 13)
      - `def update(self, dt)` (Line 24)
      - `def render(self, target_surf, camera)` (Line 31)
  - **`class ParticleSystem`** (Line 41)
    - Methods (7):
      - `def __init__(self, max_particles)` (Line 42)
      - `def spawn_debris(self, world_x, world_y, color, count)` (Line 47): Spawns digging block debris fragments.
      - `def spawn_sparks(self, world_x, world_y, color, count)` (Line 61): Spawns combat sparks or critical hit stars.
      - `def spawn_bubbles(self, world_x, world_y, count)` (Line 71): Spawns rising underwater oxygen bubbles.
      - `def spawn_smoke(self, world_x, world_y, color, count)` (Line 83): Spawns gentle rising smoke or fireplace chimney puffs.
      - `def update(self, dt)` (Line 95)
      - `def render(self, target_surf, camera)` (Line 102)

#### `src/entities/player.py`
- **Size:** 63737 bytes | **Lines:** 1371 lines
- **Description:** Potaria - Player Entity: Spud the Potato Hero (RPG Integrated)
- **Classes Defined (2):**
  - **`class PlayerFireball`** (Line 44)
    - Methods (4):
      - `def __init__(self, x, y, vx, vy, sprite, damage, max_distance)` (Line 45)
      - `def rect(self)` (Line 61)
      - `def update(self, dt, world, particle_system)` (Line 66)
      - `def render(self, target_surf, camera)` (Line 88)
  - **`class Player`** (Line 92)
    - Methods (29):
      - `def __init__(self, spawn_x, spawn_y, asset_factory, sound_manager)` (Line 93)
      - `def rect(self)` (Line 204)
      - `def center_x(self)` (Line 212)
      - `def center_x(self, val)` (Line 216)
      - `def center_y(self)` (Line 220)
      - `def center_y(self, val)` (Line 224)
      - `def health(self)` (Line 228)
      - `def health(self, val)` (Line 232)
      - `def max_health(self)` (Line 236)
      - `def max_health(self, val)` (Line 240)
      - `def current_anim(self)` (Line 244): Current 12 FPS animation state for networking and sprites.
      - `def check_climbable(self, world)` (Line 253): Checks if the player's hitbox overlaps rope rungs or scaffolding/platforms.
      - `def handle_input(self, keys, mouse_world_x, mouse_world_y, key_bindings, world)` (Line 291)
      - `def is_head_blocked(self, world)` (Line 391): Checks if the player's head is directly blocked by a solid non-platform ceiling block.
      - `def cast_skill_hotkey(self, key_name, particle_system, camera)` (Line 414): Executes active skill mapped to hotkey (Q, F, V, R).
      - `def can_attack(self)` (Line 601): Returns True if the player is off attack cooldown and ready to strike or fire.
      - `def trigger_attack(self, cooldown)` (Line 605): Initiates an attack, sets attack cooldown (fire rate), and synchronizes visual swing duration.
      - `def start_swing(self)` (Line 617)
      - `def get_meal_buff_val(self, stat_name)` (Line 623): Returns the total active meal buff contribution for stat_name, bounded by provisional caps.
      - `def consume_item(self, item_id)` (Line 640)
      - `def has_effect(self, kw)` (Line 713)
      - `def take_damage(self, amount, knockback_vx, knockback_vy, ignore_defense, is_magic)` (Line 729)
      - `def reset_reflection_state(self)` (Line 831): Immediately collapses active projectile reflection field and exhausts budget.
      - `def on_graze(self)` (Line 836): Called when a boss projectile grazes player perimeter without hitting core hitbox (Touhou style).
      - `def update(self, dt, world, active_item_id)` (Line 846)
      - `def render(self, target_surf, camera, held_item_icon, held_item)` (Line 1134)
      - `def _render_arm_and_tool(self, target_surf, camera, player_sx, player_sy, held_item_icon, held_item)` (Line 1186)
      - `def _render_active_aura(self, target_surf, cx, cy, aura_type)` (Line 1309): Renders radiant pulsing aura mandalas and orbiting starlight motes around Spud.
      - `def get_rod_tip_pos(self)` (Line 1355): Calculates the dynamic world position of the held rod tip based on player posture, position, and aim.

#### `src/entities/projectile.py`
- **Size:** 39985 bytes | **Lines:** 919 lines
- **Description:** Potaria - Projectiles Engine (Pygame-ce Powered)
- **Classes Defined (11):**
  - **`class ArrowProjectile`** (Line 13)
    - Methods (4):
      - `def __init__(self, x, y, angle_rad, speed, damage, angle, arrow_type)` (Line 14)
      - `def rect(self)` (Line 28)
      - `def update(self, dt, world, particle_system, sound_manager, player)` (Line 31)
      - `def render(self, target_surf, camera, arrow_sprite)` (Line 64)
  - **`class CelestialStarProjectile`** (Line 84)
    - Methods (5):
      - `def __init__(self, target_world_x, target_world_y, camera_y, damage)` (Line 85)
      - `def rect(self)` (Line 108)
      - `def update(self, dt, world, particle_system, sound_manager, camera, mobs, boss, player)` (Line 111)
      - `def explode(self, particle_system, sound_manager, camera, mobs, boss, player)` (Line 151)
      - `def render(self, target_surf, camera, star_sprite)` (Line 208)
  - **`class MobSpitProjectile`** (Line 216) - Anti-cheese arcing projectile spat by obstructed mobs over player walls.
    - Methods (4):
      - `def __init__(self, x, y, vx, vy, damage, color, radius)` (Line 218)
      - `def rect(self)` (Line 228)
      - `def update(self, dt, world)` (Line 231)
      - `def render(self, target_surf, camera)` (Line 243)
  - **`class FreezingNeedleProjectile`** (Line 251) - Piercing crystalline ice needle launched by weapons with Freezing Needles.
    - Methods (4):
      - `def __init__(self, x, y, angle_rad, damage, speed, max_distance)` (Line 253)
      - `def rect(self)` (Line 267)
      - `def update(self, dt, world, particle_system, sound_manager, mobs, boss, player, combat)` (Line 270)
      - `def render(self, target_surf, camera)` (Line 330)
  - **`class AstralArrowProjectile`** (Line 342) - Bonus astral arrow fired by Starlight Volley effect.
    - Methods (4):
      - `def __init__(self, x, y, angle_rad, damage, speed, max_distance)` (Line 344)
      - `def rect(self)` (Line 355)
      - `def update(self, dt, world, particle_system, sound_manager, mobs, boss, player, combat)` (Line 358)
      - `def render(self, target_surf, camera)` (Line 401)
  - **`class SolarFlareShockwave`** (Line 409) - Expanding radial solar flare shockwave.
    - Methods (7):
      - `def __init__(self, x, y, damage, max_radius)` (Line 411)
      - `def rect(self)` (Line 422)
      - `def frect(self)` (Line 426)
      - `def pos(self)` (Line 430)
      - `def pos(self, val)` (Line 434)
      - `def update(self, dt, particle_system, sound_manager, mobs, boss, player, combat)` (Line 438)
      - `def render(self, target_surf, camera)` (Line 487)
  - **`class GravitationalPulseProjectile`** (Line 495) - Pulls enemies toward blast center then detonates.
    - Methods (7):
      - `def __init__(self, x, y, damage, pull_radius)` (Line 497)
      - `def rect(self)` (Line 507)
      - `def frect(self)` (Line 511)
      - `def pos(self)` (Line 515)
      - `def pos(self, val)` (Line 519)
      - `def update(self, dt, particle_system, sound_manager, mobs, boss, player, combat)` (Line 523)
      - `def render(self, target_surf, camera)` (Line 576)
  - **`class CatalystStarProjectile`** (Line 585) - Homing celestial star/orb fired by Catalysts (max 560px range).
    - Methods (6):
      - `def __init__(self, x, y, vx, vy, sprite, damage, max_distance, combat)` (Line 587)
      - `def rect(self)` (Line 606)
      - `def pos(self)` (Line 611)
      - `def pos(self, val)` (Line 615)
      - `def update(self, dt, world, particle_system, mobs, boss)` (Line 619)
      - `def render(self, target_surf, camera)` (Line 678)
  - **`class StaffBoltProjectile`** (Line 693) - Elemental magic bolt fired by Staves (max 560px range).
    - Methods (6):
      - `def __init__(self, x, y, vx, vy, sprite, damage, max_distance, element)` (Line 695)
      - `def rect(self)` (Line 712)
      - `def pos(self)` (Line 717)
      - `def pos(self, val)` (Line 721)
      - `def update(self, dt, world, particle_system)` (Line 725)
      - `def render(self, target_surf, camera)` (Line 759)
  - **`class RodJavelinProjectile`** (Line 774) - High-velocity piercing javelin / spark needle fired by Rods (max 560px range).
    - Methods (6):
      - `def __init__(self, x, y, vx, vy, sprite, damage, max_distance)` (Line 776)
      - `def rect(self)` (Line 794)
      - `def pos(self)` (Line 799)
      - `def pos(self, val)` (Line 803)
      - `def update(self, dt, world, particle_system)` (Line 807)
      - `def render(self, target_surf, camera)` (Line 833)
  - **`class ScepterPulseProjectile`** (Line 850) - Expanding arcane shockwave pulse fired by Scepters (max 560px range).
    - Methods (6):
      - `def __init__(self, x, y, vx, vy, sprite, damage, max_distance)` (Line 852)
      - `def rect(self)` (Line 868)
      - `def pos(self)` (Line 873)
      - `def pos(self, val)` (Line 877)
      - `def update(self, dt, world, particle_system)` (Line 881)
      - `def render(self, target_surf, camera)` (Line 907)

#### `src/entities/vfx.py`
- **Size:** 6668 bytes | **Lines:** 181 lines
- **Description:** Potaria - Visual Effects Engine (Animated VFX)
- **Classes Defined (2):**
  - **`class AnimatedVFX`** (Line 12)
    - Methods (3):
      - `def __init__(self, x, y, frames, duration, loop, rot_deg, scale, anchor, offset, blend_mode, flip_x, flip_y, anim_name)` (Line 13)
      - `def update(self, dt)` (Line 52)
      - `def render(self, target_surf, camera)` (Line 75)
  - **`class VisualEffectManager`** (Line 98)
    - Methods (7):
      - `def __init__(self, asset_factory)` (Line 99)
      - `def spawn_effect(self, anim_name, x, y, duration, loop, rot_deg, scale, anchor, offset, blend_mode, flip_x, flip_y)` (Line 103): Spawns an animated visual effect from AssetFactory's animated_effects registry.
      - `def spawn_custom_vfx(self, vfx)` (Line 154)
      - `def remove_anchored_effects(self, anchor_entity, anim_name)` (Line 158): Removes active looping effects anchored to a specific entity.
      - `def update(self, dt)` (Line 171)
      - `def render(self, target_surf, camera)` (Line 176)
      - `def clear(self)` (Line 180)

### Combat & Ballistics Systems (`src/combat/*`)

#### `src/combat/combat_system.py`
- **Size:** 123235 bytes | **Lines:** 2065 lines
- **Description:** Potaria - Combat Engine & Mob Spawner (RPG Integrated)
- **Classes Defined (2):**
  - **`class DamageNumber`** (Line 39)
    - Methods (3):
      - `def __init__(self, world_x, world_y, amount, color, is_crit)` (Line 40)
      - `def update(self, dt)` (Line 51)
      - `def render(self, target_surf, camera, font, font_crit)` (Line 57)
  - **`class CombatManager`** (Line 89)
    - Methods (22):
      - `def __init__(self, asset_factory, sound_manager, particle_system, camera)` (Line 90)
      - `def spawn_projectile(self, proj)` (Line 151): Spawns an active ballistic arrow or celestial star projectile.
      - `def spawn_boss(self, dungeon_x, dungeon_y, boss_cls, player)` (Line 155): Spawns an underground mini-boss (random or specified class/name) with power scaling.
      - `def spawn_grand_boss(self, x, y, party_size, player)` (Line 179): Summons the Grand Boss SOL-RHO THE CELESTIAL TITAN (Souls-like 2-phase battle!) with scaling.
      - `def spawn_mob(self, mob, player)` (Line 206)
      - `def spawn_damage_number(self, world_x, world_y, amount, color, is_crit)` (Line 217)
      - `def _on_mob_slain(self, mob, player)` (Line 222): Unified reward & passive trigger hook when any mob is slain.
      - `def update(self, dt, world, player, is_night, time_of_day)` (Line 240)
      - `def trigger_weapon_swing_effects(self, player, mouse_wx, mouse_wy, active_item)` (Line 1082): Spawns projectiles and shockwaves for weapon swing effects.
      - `def _check_weapon_hits(self, player, world)` (Line 1156)
      - `def _spawn_loot_drop(self, item_id, count, mx, my)` (Line 1359): Spawns a DroppedItem with natural horizontal scatter so multiple drops spread apart.
      - `def _drop_mob_loot(self, mob, tuned, player)` (Line 1368)
      - `def _trigger_ancient_drop(self, anc_item, mx, my)` (Line 1586): Triggers grand celebratory fanfare, screen shake, and celebratory toast when an Ancient relic drops.
      - `def _spawn_nightly_elite(self, world, player)` (Line 1603): Spawns exactly one slightly bigger Champion of the Night with boosted stats & special skill once per night.
      - `def _spawn_natural_mob(self, world, player, is_night, time_of_day)` (Line 1638)
      - `def render(self, target_surf, camera, renderer, render_damage_numbers)` (Line 1783)
      - `def get_enemy_projectiles_sync_data(self)` (Line 1832): Serializes active enemy projectiles on host for network broadcast.
      - `def get_dropped_items_sync_data(self)` (Line 1850): Serializes active dropped items on host for network broadcast.
      - `def get_mobs_sync_data(self)` (Line 1863): Serializes active mob states on authoritative host for network broadcast.
      - `def get_boss_sync_data(self)` (Line 1888): Serializes boss state on authoritative host for network broadcast.
      - `def sync_from_host(self, mobs_data, boss_data, enemy_projectiles, dropped_items)` (Line 1911): Updates and reconciles client mob entities from authoritative host snapshot.
      - `def apply_remote_mob_damage(self, damage_data)` (Line 2044): Applies damage reported by a client to authoritative mob or boss.
- **Standalone Functions (1):**
  - `def has_line_of_sight(world, x1, y1, x2, y2)` (Line 71): Enforces line-of-sight raycast through solid blocks to prevent mob wall-farming cheese.

### RPG Progression & Equipment Systems (`src/rpg/*`)

#### `src/rpg/achievements.py`
- **Size:** 12848 bytes | **Lines:** 313 lines
- **Description:** Potaria - Achievements Engine & Toast Notification System
- **Classes Defined (2):**
  - **`class AchievementToast`** (Line 18)
    - Methods (3):
      - `def __init__(self, achievement_data)` (Line 19)
      - `def update(self, dt)` (Line 30)
      - `def render(self, target_surf, font_title, font_desc, toast_bg)` (Line 34)
  - **`class AchievementManager`** (Line 76)
    - Methods (10):
      - `def __init__(self, catalog_path, save_path, sound_manager)` (Line 77)
      - `def load_catalog(self)` (Line 91): Loads achievements catalog definition from JSON.
      - `def load_progress(self)` (Line 104): Loads persistent unlocked achievements from disk.
      - `def save_progress(self)` (Line 118): Saves unlocked achievements to disk.
      - `def unlock(self, ach_id, sound_manager)` (Line 130): Unlocks an achievement if not already earned, triggers sound and toast.
      - `def is_unlocked(self, ach_id)` (Line 157)
      - `def get_progress(self)` (Line 160)
      - `def update(self, dt)` (Line 166): Advances active toast timer and pops next toast from queue.
      - `def render_toast(self, target_surf, font_title, font_desc, toast_bg)` (Line 176): Renders currently active popup toast banner.
      - `def render_browser(self, target_surf, mouse_pos, scroll_y)` (Line 181): Renders full-screen or modal achievements browser.

#### `src/rpg/affix_system.py`
- **Size:** 3298 bytes | **Lines:** 99 lines
- **Description:** Affix System and Category Restriction Rules Engine for Potaria.
- **Standalone Functions (3):**
  - `def is_defensive_affix(affix_data)` (Line 52): Checks whether an affix modifies any defensive attributes or is a known defensive affix.
  - `def is_affix_allowed_on_category(affix_data, category)` (Line 69): Validates whether an affix can be applied to an item of the given category.
  - `def scrub_defensive_stats_from_weapon(weapon_data)` (Line 82): Ensures a weapon dictionary has strictly 0 defense across all stat mappings.

#### `src/rpg/enhancement.py`
- **Size:** 13241 bytes | **Lines:** 319 lines
- **Description:** Potaria - Item Enhancement & Affix System
- **Standalone Functions (8):**
  - `def get_enhancement_multiplier(level)` (Line 85): Returns stat scaling multiplier for enhancement level (+0 to +7).
  - `def can_enhance_item(item)` (Line 93): Checks if an item can be enhanced.
  - `def enhance_item(item, inventory, sound_manager)` (Line 109): Attempts to enhance item to the next level using player inventory resources.
  - `def repair_item(item, inventory, sound_manager)` (Line 165): Repairs a broken equipment item for 1 Gold Coin (10,000 Copper).
  - `def can_add_affix_slot(item)` (Line 184): Checks if item is eligible for an Affix Slot.
  - `def add_affix_slot_to_item(item, inventory, cost_copper, sound_manager)` (Line 221): Carves an Affix Slot into an eligible piece by sacrificing a random basic stat.
  - `def can_apply_affix_stone(item)` (Line 262): Checks whether an item can receive an Affix Stone.
  - `def apply_affix_stone(item, inventory, sound_manager)` (Line 276): Embeds an Affix Stone into an open affix slot on an eligible Epic/Legendary/Mythic/Ancient item.

#### `src/rpg/equipment.py`
- **Size:** 45307 bytes | **Lines:** 819 lines
- **Description:** Potaria - Equipment & Paperdoll Engine (Chroisen Style)
- **Classes Defined (1):**
  - **`class Equipment`** (Line 432)
    - Methods (13):
      - `def __init__(self)` (Line 433)
      - `def clear_all_items(self, stats)` (Line 442): Clears all equipped armor, weapons, and accessories from slots.
      - `def equip(self, item_or_id, stats)` (Line 449): Equips an item or ItemStack into its designated paperdoll slot.
      - `def unequip(self, slot_name, stats)` (Line 470): Unequips item from given slot, returning the ItemStack or item_id intact.
      - `def has_light_emitter(self)` (Line 480): Checks if equipped headpiece emits light (e.g. Miner Helmet) or any gear has radiance/illumination effects.
      - `def has_astral_radiance(self)` (Line 498): Checks if equipped gear emits high-intensity Astral Sparkles / Celestial Radiance.
      - `def has_miner_helmet_equipped(self)` (Line 511): Checks if Potato Miner Helmet or light-emitting helmet is equipped in head slot.
      - `def get_all_active_effects(self)` (Line 526): Returns a list of all active effect strings from equipped gear and active weapon.
      - `def has_effect(self, effect_keyword)` (Line 551): Checks if any currently equipped item or held weapon contains the given effect keyword.
      - `def get_active_set(self)` (Line 559): Returns (set_key, set_info) if qualifying progressive set threshold or equipment set is active.
      - `def has_ancient_set(self)` (Line 604): Checks if the player has an active Ancient equipment set bonus.
      - `def get_active_aura(self)` (Line 609): Returns aura type string ('ancient', 'titan', 'magma', 'cryo', 'shadow', 'spud', 'cactus', 'solar', etc.) or None.
      - `def recalculate_stats(self, stats, active_item_id, active_item)` (Line 652): Recalculates all player bonus stats based on equipped gear and held weapon.
- **Standalone Functions (4):**
  - `def load_equipment_catalog()` (Line 121)
  - `def get_item_equipment_slot(item)` (Line 331): Returns the designated equipment slot (SLOT_HEAD, SLOT_CHEST, SLOT_LEGS, SLOT_ACCESSORY, SLOT_WEAPON)
  - `def get_equipped_item_for_slot(player, slot)` (Line 376): Retrieves the currently equipped item or ItemStack in the given slot for the player.
  - `def is_item_already_equipped(item, player)` (Line 399): Returns True if the item is currently equipped by the player (in paperdoll slots or active weapon).

#### `src/rpg/equipment_update.py`
- **Size:** 121163 bytes | **Lines:** 2083 lines
- **Description:** Potaria Equipment Update - Core Data and Rules Engine
- **Standalone Functions (16):**
  - `def get_tag_info(tag_id)` (Line 270): Returns metadata for a given stable tag ID.
  - `def get_item_stat_ranges(item_id)` (Line 457): Returns the predefined attribute min/max ranges for an item ID.
  - `def roll_item_stat_ranges(item_id, rng_seed)` (Line 461): Rolls randomized values strictly within the predefined attribute ranges of the item definition.
  - `def validate_stat_rolls(item_id, rolls)` (Line 495): Validates that all rolls are within configured min/max and only use declared attributes.
  - `def get_max_additional_slots(rarity)` (Line 525): Returns the maximum additional affix slots permitted through the slot addition system.
  - `def can_add_additional_affix_slot(item)` (Line 529): Strict validation rule for additional affix slots per equipmentUpdate spec:
  - `def add_additional_affix_slot(item, inventory, cost_copper, sound_manager)` (Line 563): Carves 1 additional affix slot up to the strict rarity-based ceiling.
  - `def get_equipped_set_counts(equipped_ids)` (Line 916): Returns mapping of set_id -> number of matching pieces equipped.
  - `def get_active_threshold_bonuses(equipped_ids, cumulative)` (Line 929): Returns list of tuples (set_id, threshold, bonus_dict) for active progressive thresholds.
  - `def get_all_active_threshold_bonuses(equipped_ids)` (Line 950): Returns all active progressive thresholds where count >= threshold (cumulative Torchlight 2 style).
  - `def build_set_tooltip_lines(item_id, player, font, wrap_width)` (Line 954): Builds rich Torchlight 2-style equipment set tooltip lines for an item or ItemStack:
  - `def build_affix_socket_lines(item, font, wrap_width)` (Line 1037): Builds clean ARPG-style circular affix socket lines for an item:
  - `def register_new_equipment_into_catalogs()` (Line 1949): Registers all new weapons, sets, and accessories into ARMOR_DATA, EQUIPMENT_SETS,
  - `def compute_save_signature(payload_bytes)` (Line 2056): Computes an HMAC-SHA256 signature for world save JSON byte payload.
  - `def verify_save_signature(payload_bytes, signature)` (Line 2060): Verifies that the save file payload matches its cryptographic HMAC signature.
  - `def create_equipment_stack(item_id, count, enhancement_level, affixes, tags, rng_seed)` (Line 2065): Creates an ItemStack with randomized base stats rolled strictly within predefined attribute ranges,

#### `src/rpg/skills.py`
- **Size:** 20345 bytes | **Lines:** 581 lines
- **Description:** Potaria - Skill Book & Combat Skills Engine (Chroisen Style)
- **Classes Defined (1):**
  - **`class SkillManager`** (Line 406)
    - Methods (13):
      - `def __init__(self)` (Line 407)
      - `def all_skills(self)` (Line 423)
      - `def get_skill_level(self, skill_id)` (Line 426)
      - `def is_skill_evolved(self, skill_id)` (Line 429): Returns True if skill has reached evolution tier (Lv. 3+).
      - `def get_skill_name(self, skill_id)` (Line 433)
      - `def get_skill_mp_cost(self, skill_id, player)` (Line 439)
      - `def get_skill_dmg_mult(self, skill_id)` (Line 452)
      - `def get_skill_cooldown(self, skill_id, player)` (Line 459)
      - `def assign_skill(self, hotkey, skill_id)` (Line 469): Binds a learned skill to hotkey slot (Q, F, V, R), supporting swapping and unbinding.
      - `def learn_skill(self, skill_id)` (Line 494): Learns or upgrades a skill by consuming duplicate skillbooks (Lv. 1 to 5).
      - `def can_use_skill(self, skill_id, stats, player)` (Line 512)
      - `def use_skill(self, skill_id, stats, player)` (Line 532)
      - `def update(self, dt)` (Line 565): Ticks down active skill cooldowns and combo window timers.

#### `src/rpg/stats.py`
- **Size:** 6295 bytes | **Lines:** 204 lines
- **Description:** Potaria - Action RPG Statistics Engine (Chroisen Style)
- **Classes Defined (1):**
  - **`class PlayerStats`** (Line 9)
    - Methods (25):
      - `def __init__(self)` (Line 10)
      - `def total_copper_value(self)` (Line 54): Returns total purchasing power across all coins in copper denomination.
      - `def add_coins(self, copper, silver, gold)` (Line 58): Adds currency and automatically normalizes denominations (100c = 1s, 100s = 1g).
      - `def set_from_copper(self, total_copper)` (Line 63): Sets the purse coins directly from a total copper integer with automatic breakdown.
      - `def remove_coins(self, total_copper)` (Line 71): Deducts total_copper from purse with automatic change breakdown. Returns True if successful.
      - `def set_yolo_mode(self, enabled)` (Line 79): Locks player permanently to exactly 1 heart (20 HP) that cannot increment in any means.
      - `def max_hp(self)` (Line 88)
      - `def max_hp(self, val)` (Line 94)
      - `def max_mp(self)` (Line 99)
      - `def max_mp(self, val)` (Line 103)
      - `def total_atk(self)` (Line 107)
      - `def attack(self)` (Line 111)
      - `def total_def(self)` (Line 115)
      - `def total_crit_rate(self)` (Line 119)
      - `def total_crit_damage_multiplier(self)` (Line 123)
      - `def total_speed(self)` (Line 127)
      - `def total_atk_speed(self)` (Line 131)
      - `def attack_speed(self)` (Line 135)
      - `def atk_speed(self)` (Line 139)
      - `def total_mp_regen(self)` (Line 143)
      - `def exp(self)` (Line 147)
      - `def crit_chance(self)` (Line 151)
      - `def gain_exp(self, amount)` (Line 154)
      - `def add_exp(self, amount)` (Line 157): Awards EXP and handles level-ups.
      - `def update(self, dt)` (Line 188): Regenerates MP (balanced 1.5 MP/s base + equipment bonuses) and subtle HP over time.

### Loot, Registry & Affix Systems (`src/loot/*`)

#### `src/loot/__init__.py`
- **Size:** 559 bytes | **Lines:** 25 lines
- **Description:** Data-Driven Loot, Rarity, and Multi-Affix Package for Potaria & Potaria: Root Realm.
- *Declarative definition module containing data constants, dictionaries, and configurations.*

#### `src/loot/affix_engine.py`
- **Size:** 9893 bytes | **Lines:** 246 lines
- **Description:** Data-Driven Multi-Affix Engine for Potaria & Potaria: Root Realm.
- **Classes Defined (1):**
  - **`class AffixEngine`** (Line 21)
    - Methods (7):
      - `def __init__(self, affixes_path)` (Line 22)
      - `def load_affixes(self)` (Line 28)
      - `def get_affix(self, affix_key)` (Line 33)
      - `def is_affix_compatible(self, affix_key, item_category, rarity, already_selected)` (Line 41)
      - `def generate_name(self, base_name, applied_affixes)` (Line 83)
      - `def roll_affixes(self, item_id, rarity, rng_seed, max_affixes)` (Line 103)
      - `def generate_loot(self, base_item, rarity, rng_seed, forced_affixes)` (Line 131): Constructs a 4-layer item dictionary:

#### `src/loot/item_registry.py`
- **Size:** 8715 bytes | **Lines:** 215 lines
- **Description:** Potaria: Root Realm - Phase 1 Data-Driven Item Registry
- **Classes Defined (2):**
  - **`class ItemDefinition`** (Line 65) - Canonical 4-Layer Item Base Definition.
    - Methods (2):
      - `def __init__(self, data)` (Line 68)
      - `def to_dict(self)` (Line 90): Converts definition back into a flat dictionary compatible with ITEM_REGISTRY.
  - **`class DataDrivenItemRegistry`** (Line 113) - Centralized item registry bridging legacy ITEM_REGISTRY and data-driven schemas.
    - Methods (5):
      - `def __init__(self)` (Line 116)
      - `def load_from_legacy_registry(self)` (Line 121)
      - `def get(self, item_id)` (Line 190)
      - `def get_by_category(self, category)` (Line 198)
      - `def load_schema(self, path)` (Line 205)
- **Standalone Functions (1):**
  - `def map_to_canonical_category(item_id, item_data)` (Line 31): Maps legacy ITEM_REGISTRY categories or category strings to the 9 canonical Phase 1 categories.

#### `src/loot/loot_system.py`
- **Size:** 4711 bytes | **Lines:** 115 lines
- **Description:** 3-Path Loot Acquisition System for Potaria & Potaria: Root Realm.
- **Classes Defined (1):**
  - **`class LootSystem`** (Line 21)
    - Methods (6):
      - `def __init__(self, tables_path)` (Line 22)
      - `def load_tables(self)` (Line 29)
      - `def roll_random_loot(self, source_category, level, rng_seed, as_instance)` (Line 34)
      - `def roll_targeted_loot(self, source_id, rng_seed, as_instance)` (Line 55)
      - `def get_guaranteed_milestone_loot(self, milestone_id, rng_seed, as_instance)` (Line 86)
      - `def generate_loot_drop(self, item_id, rarity, rng_seed)` (Line 109)

#### `src/loot/rarity_engine.py`
- **Size:** 3601 bytes | **Lines:** 123 lines
- **Description:** Canonical 7-Tier Rarity Engine for Potaria & Potaria: Root Realm.
- **Classes Defined (1):**
  - **`class RarityEngine`** (Line 10)
    - Methods (4):
      - `def get_tier(self, rarity)` (Line 87)
      - `def get_rank(self, rarity)` (Line 92)
      - `def is_at_least(self, rarity, min_rarity)` (Line 95)
      - `def roll_rarity(self, rng_seed, luck_bonus, min_rarity, max_rarity)` (Line 98)

### User Interface & HUD Systems (`src/ui/*`)

#### `src/ui/character_panel.py`
- **Size:** 34781 bytes | **Lines:** 708 lines
- **Description:** Potaria - Character & Paperdoll Equipment Panel (Chroisen Style)
- **Classes Defined (1):**
  - **`class CharacterPanel`** (Line 21)
    - Methods (7):
      - `def __init__(self, asset_factory)` (Line 22)
      - `def toggle(self)` (Line 47)
      - `def handle_click(self, mouse_x, mouse_y, player, inventory, is_right_click)` (Line 50): Allows clicking equipped slots to unequip, or selecting and assigning combat skills.
      - `def handle_key(self, event, player, key_bindings)` (Line 105): Allows hovering over a learned skill and pressing configured skill keys to bind it immediately.
      - `def render(self, target_surf, player, mouse_x, mouse_y)` (Line 138)
      - `def _render_skill_tooltip(self, target_surf, mx, my, player, skill_id)` (Line 458): Displays rich hover description popup for combat skills in Character Status.
      - `def _render_equipped_tooltip(self, target_surf, mx, my, item_id, is_held, player)` (Line 533)

#### `src/ui/chest_ui.py`
- **Size:** 21993 bytes | **Lines:** 452 lines
- **Description:** Potaria - Storage Chest Interactive UI Window
- **Classes Defined (1):**
  - **`class ChestStorageWindow`** (Line 19)
    - Methods (9):
      - `def __init__(self, asset_factory, sound_manager)` (Line 20)
      - `def open(self, chest, player, inventory)` (Line 42)
      - `def close(self)` (Line 51)
      - `def handle_click(self, mouse_x, mouse_y, is_right_click, player, inventory)` (Line 56)
      - `def render(self, target_surf, inventory, mouse_x, mouse_y, render_dragged, player, character_panel)` (Line 171)
      - `def _build_chest_tooltip_lines(self, item, player, is_equipped)` (Line 286)
      - `def _measure_chest_tooltip(self, lines)` (Line 374)
      - `def _draw_chest_card(self, target_surf, tx, ty, tw, th, lines)` (Line 380)
      - `def render_tooltip(self, target_surf, item, mx, my, player, character_panel)` (Line 393): Renders rich item tooltip for chest slots with side-by-side comparison if character panel is open.

#### `src/ui/crafting.py`
- **Size:** 59248 bytes | **Lines:** 1338 lines
- **Description:** Potaria - Crafting Engine (Minecraft-Style Categorized Recipe Book)
- **Classes Defined (1):**
  - **`class CraftingSystem`** (Line 809)
    - Methods (16):
      - `def __init__(self, asset_factory, sound_manager)` (Line 810)
      - `def _init_tab_rects(self)` (Line 828): Initializes exact screen bounding rectangles for all category tabs.
      - `def get_panel_rect(self)` (Line 848): Returns the full interactive panel Rect encompassing crafting header, tabs, and grid.
      - `def set_category(self, cat_id)` (Line 852): Sets the active category filter tab and resets scroll position.
      - `def handle_scroll(self, scroll_y)` (Line 867): Smoothly scrolls the recipe grid up (scroll_y > 0) or down (scroll_y < 0).
      - `def filtered_recipes(self)` (Line 875): Returns recipes filtered by the active category tab.
      - `def get_filtered_recipes(self, category)` (Line 881): Explicit getter for filtered recipes supporting loose category strings.
      - `def get_nearest_cooking_station(self, world, player)` (Line 899): Returns (gx, gy) of closest furnace or fireplace within cooking range.
      - `def check_nearby_stations(self, world, player)` (Line 918): Checks if Spud is within physical range (within 2.5 tiles) of a placed Work Bench or Furnace/Fireplace.
      - `def _infer_recipe_category(self, result_id)` (Line 943): Infers category for any recipe lacking an explicit category tag.
      - `def update_recipes(self, inventory, world, player)` (Line 955)
      - `def craft(self, recipe, inventory, world, player)` (Line 999)
      - `def handle_click(self, mouse_x, mouse_y, inventory)` (Line 1050)
      - `def render(self, target_surf, mouse_x, mouse_y, font)` (Line 1100)
      - `def _render_tab_tooltip(self, target_surf, mx, my, tab, font)` (Line 1253): Displays tooltip describing category tab filter contents.
      - `def _render_recipe_tooltip(self, target_surf, mx, my, recipe, font)` (Line 1274)
- **Standalone Functions (1):**
  - `def load_craftable_recipes()` (Line 780): Loads categorized crafting recipes from data/crafting/craftable_items.json if present,

#### `src/ui/cutscene.py`
- **Size:** 25447 bytes | **Lines:** 565 lines
- **Description:** Potaria - Cinematic 2D Prologue Cutscene Engine
- **Classes Defined (1):**
  - **`class CutsceneEngine`** (Line 20)
    - Methods (13):
      - `def __init__(self, asset_factory, sound_manager, bgm_manager)` (Line 21)
      - `def _get_wrapped_lines(self, text, max_width)` (Line 190)
      - `def _init_particles(self)` (Line 211)
      - `def start(self)` (Line 225): Starts or resets the cutscene sequence.
      - `def _play_narrator_for_current_entry(self)` (Line 244): Automatically plays the deep, mythic narrator voice track for the current dialogue entry.
      - `def _play_narrator_for_current_scene(self)` (Line 254): Helper alias to play narrator voice track for current entry / scene.
      - `def is_finished(self)` (Line 258)
      - `def skip(self)` (Line 261): Immediately ends cutscene and signals return to main menu.
      - `def advance_dialogue(self)` (Line 272): Advances typewriter or moves to the next dialogue entry.
      - `def handle_click(self, mouse_pos, button)` (Line 325)
      - `def handle_key(self, event)` (Line 341)
      - `def update(self, dt, mouse_pos)` (Line 357)
      - `def render(self, target_surf)` (Line 449)

#### `src/ui/fishing_minigame.py`
- **Size:** 16564 bytes | **Lines:** 371 lines
- **Description:** Potaria - 2D Fishing Battle Mini-Game
- **Classes Defined (1):**
  - **`class FishingBattleMiniGame`** (Line 27)
    - Methods (6):
      - `def __init__(self, asset_factory, sound_manager)` (Line 28)
      - `def start(self, fish_id, caught_count)` (Line 64): Initializes and begins the fishing tug-of-war battle.
      - `def cancel(self)` (Line 126): Cancels mini-game immediately (e.g. when player takes damage).
      - `def handle_click(self, is_right_click, player)` (Line 132): Processes player click input during the battle (right-click on PC, tap on mobile).
      - `def update(self, dt)` (Line 185): Updates fish AI, tension decay, thrashing cycles, and timers.
      - `def render(self, surface)` (Line 236): Draws the retro pixel-art fishing battle window with meters and prompts.

#### `src/ui/hud.py`
- **Size:** 63754 bytes | **Lines:** 1227 lines
- **Description:** Potaria - Heads-Up Display (HUD) & Party Interface
- **Classes Defined (1):**
  - **`class HUD`** (Line 21)
    - Methods (22):
      - `def __init__(self, asset_factory)` (Line 22)
      - `def render(self, target_surf, player, inventory, crafting_system, camera, mouse_x, mouse_y, world, combat, lan_client, render_dragged, sky, character_panel, render_tooltips)` (Line 80)
      - `def render_hovered_tooltip(self, target_surf, mouse_x, mouse_y, player, character_panel)` (Line 143): Renders deferred item tooltip in topmost z-order over character and chest panels.
      - `def render_dragged_item(self, target_surf, inventory, mouse_x, mouse_y)` (Line 151): Renders the currently dragged item at the cursor in the foreground.
      - `def _render_notification_banner(self, target_surf, message)` (Line 161): Displays a prominent banner across top-center when learning skills or completing feats.
      - `def _render_hp_and_mp(self, target_surf, player)` (Line 174): Draws health hearts, numeric life, and glowing mana bar positioned to the left of the radar map.
      - `def _render_skill_bar(self, target_surf, player)` (Line 271): Draws active skill icons and cooldown sweeps dynamically from player's hotkey loadout with sleek badges.
      - `def _render_food_buffs(self, target_surf, player, mouse_x, mouse_y, draw_tooltip)` (Line 385): Displays small Food Buff HUD widget at bottom-left (x=20, y=SCREEN_HEIGHT-44).
      - `def _render_food_buff_tooltip(self, target_surf, hovered_buff, hovered_rect)` (Line 468): Renders high-contrast tooltip for hovered food buff.
      - `def _render_inventory(self, target_surf, inventory, mouse_x, mouse_y, player)` (Line 524)
      - `def _render_party_hud(self, target_surf, lan_client, inventory, crafting_system)` (Line 630): Displays party members (up to 5 players) with health bars in a dedicated clean panel.
      - `def add_chat_message(self, sender, text)` (Line 685): Adds a timestamped message to the local chat and console history.
      - `def _render_chat(self, target_surf, lan_client)` (Line 699): Draws word-wrapped chat/command console box with 6.0s auto-hide when idle.
      - `def _render_ancient_drop_toast(self, target_surf, banner_name)` (Line 818): Renders radiant celebratory toast banner for Ancient Relic discoveries.
      - `def _get_item_rarity_color(self, item)` (Line 838)
      - `def _build_tooltip_lines(self, item, player, is_equipped)` (Line 848): Constructs formatted text lines and colors for rich Diablo/Torchlight-style item tooltip.
      - `def _measure_tooltip(self, lines)` (Line 1020): Calculates surface renderings and bounding box dimensions for a tooltip.
      - `def _draw_tooltip_box(self, target_surf, tx, ty, tw, th, rendered_surfs, r_color)` (Line 1028): Draws background plate, rarity border, and text surfaces for a tooltip card.
      - `def _render_tooltip(self, target_surf, mx, my, item, player, character_panel)` (Line 1039): Rich Diablo/Torchlight-style item tooltip with rarity tiers, stats, lore, and descriptions.
      - `def _render_reticle(self, target_surf, player, camera, mouse_x, mouse_y, inventory, world)` (Line 1114)
      - `def get_game_time_string(self, sky)` (Line 1175): Returns formatted (time_str, period, is_night) from sky DayNightCycle time_of_day.
      - `def _render_clock_widget(self, target_surf, sky)` (Line 1189): Displays in-game celestial time (12-hour AM/PM) with Sun/Moon icon docked below or beside the minimap.

#### `src/ui/inventory.py`
- **Size:** 208240 bytes | **Lines:** 4076 lines
- **Description:** Potaria - Inventory & Item System (Chroisen Style)
- **Classes Defined (2):**
  - **`class ItemStack`** (Line 2884)
    - Methods (4):
      - `def __init__(self, item_id, count, enhancement_level, is_broken, affix_slots, affixes, removed_stats, base_rolls, additional_affix_slots, tags, roll_if_empty)` (Line 2885)
      - `def clone(self, count)` (Line 2907): Creates an independent clone of this ItemStack with all enhancement, affix, and roll metadata intact.
      - `def data(self)` (Line 2923)
      - `def max_stack(self)` (Line 2992)
  - **`class Inventory`** (Line 2995)
    - Methods (37):
      - `def __init__(self, asset_factory, difficulty)` (Line 2996)
      - `def player(self)` (Line 3024)
      - `def player(self, p)` (Line 3028)
      - `def copper_coins(self)` (Line 3037)
      - `def copper_coins(self, val)` (Line 3043)
      - `def silver_coins(self)` (Line 3050)
      - `def silver_coins(self, val)` (Line 3056)
      - `def gold_coins(self)` (Line 3063)
      - `def gold_coins(self, val)` (Line 3069)
      - `def total_coins_value(self)` (Line 3075): Returns total spending power in copper denomination across all coins.
      - `def add_coins(self, copper, silver, gold)` (Line 3081): Deposits coins with automatic denomination breakdown (100c = 1s, 100s = 1g).
      - `def remove_coins(self, total_copper)` (Line 3093): Deducts currency with automatic change making. Returns True if sufficient funds.
      - `def migrate_coins(self)` (Line 3108): Scans all 40 slots and held item; transfers any coin items into the Coin Purse and frees up the slots.
      - `def set_difficulty_loadout(self, difficulty)` (Line 3129): Initializes starter inventory according to difficulty mode.
      - `def clear_all_items(self)` (Line 3154): Clears all carried items and held cursor item (used on boss defeat penalty).
      - `def can_add_item(self, item_id, count)` (Line 3159): Returns True if the inventory has sufficient slot or stack capacity to hold count items.
      - `def drop_item(self, slot_idx, count)` (Line 3180): Removes items from slot to drop into the world. Returns (item_id, count_dropped) or None.
      - `def drop_held_item(self, count)` (Line 3198): Drops currently held item. Returns (item_id, count_dropped) or None.
      - `def get_hovered_slot(self, mouse_x, mouse_y)` (Line 3213): Returns the slot index under (mouse_x, mouse_y) or None.
      - `def get_drop_button_rect(self)` (Line 3228): Returns the screen Rect for the UI [DROP] button when inventory is open.
      - `def get_recycle_button_rect(self)` (Line 3235): Returns the screen Rect for the UI [RECYCLE] button to dispose unwanted items.
      - `def get_organize_button_rect(self)` (Line 3242): Returns the screen Rect for the UI [ORGANIZE] button to fill gaps.
      - `def organize_inventory(self, include_hotbar)` (Line 3249): Compacts inventory items forward in current sequential order to fill all missing slots (None)
      - `def recycle_selected_or_held(self)` (Line 3285): Permanently disposes of the held item or currently selected item.
      - `def notify(self, message, timer)` (Line 3301): Displays a banner notification on the HUD.
      - `def update(self, dt)` (Line 3306): Updates notification timers for learned skill banners and migrates coins.
      - `def get_active_item(self)` (Line 3314)
      - `def add_item(self, item_id, count, from_back)` (Line 3317)
      - `def get_item_data(self, item_id)` (Line 3389)
      - `def count_wood(self)` (Line 3393): Returns total wood count across all wood variants (wood, oak_wood, pine_wood, palm_wood, blight_wood).
      - `def count_item(self, item_id)` (Line 3403)
      - `def is_empty(self)` (Line 3423): Returns True if every inventory slot is currently empty.
      - `def has_miner_helmet(self)` (Line 3427)
      - `def remove_item(self, item_id, count)` (Line 3430)
      - `def handle_click(self, mouse_x, mouse_y, is_right_click, player)` (Line 3494)
      - `def equip_item(self, slot_idx, player)` (Line 3615): Programmatically equips the item in slot_idx into the player's equipment. Prevents equipping broken items.
      - `def render_tooltip(self, target_surf, item, mx, my, player)` (Line 3635): Renders rich RPG tooltip for an item or ItemStack with Compact and Detailed modes.
- **Standalone Functions (2):**
  - `def load_custom_items()` (Line 2777)
  - `def get_mining_damage(active_item, tile_id)` (Line 3992): Calculates mining damage per swing based on tool type, tier power, and block category.

#### `src/ui/menu.py`
- **Size:** 124452 bytes | **Lines:** 2319 lines
- **Description:** Potaria - Main Menu, Story, Controls, Multiplayer Lobby, Settings, Input Mapping & Victory Screens
- **Classes Defined (2):**
  - **`class Button`** (Line 37)
    - Methods (4):
      - `def __init__(self, x, y, width, height, text, action, icon, tooltip)` (Line 38)
      - `def update(self, mouse_pos)` (Line 50)
      - `def _render_icon(self, target_surf, cx, cy)` (Line 53)
      - `def render(self, target_surf, font)` (Line 110)
  - **`class MenuManager`** (Line 143)
    - Methods (30):
      - `def __init__(self, asset_factory, sound_manager, bgm_manager, achievement_manager, settings, key_bindings)` (Line 144)
      - `def _apply_audio_volumes(self)` (Line 419): Immediately applies volume settings to sound and bgm managers.
      - `def load_settings(self)` (Line 429): Loads persistent user settings and key bindings from disk.
      - `def save_settings(self)` (Line 437): Persists current user settings and key bindings to disk atomically.
      - `def open_settings(self, from_state)` (Line 442)
      - `def _refresh_settings_button_labels(self)` (Line 447)
      - `def load_mods(self)` (Line 498): Loads enabled add-ons from saves/mods.json.
      - `def save_mods(self)` (Line 509): Saves enabled add-ons to saves/mods.json.
      - `def _refresh_mods_button_labels(self)` (Line 518)
      - `def update(self, dt, mouse_pos)` (Line 522)
      - `def _refresh_saved_worlds(self)` (Line 691)
      - `def rename_saved_world(self, old_name, new_name)` (Line 715): Attempts to rename `old_name` to `new_name`. Rejects if `new_name` is empty or already exists.
      - `def handle_click(self, mouse_pos, button)` (Line 737)
      - `def handle_key(self, event)` (Line 1281)
      - `def render(self, target_surf)` (Line 1392)
      - `def _render_settings_screen(self, target_surf)` (Line 1435)
      - `def _render_input_mapping(self, target_surf, mouse_pos)` (Line 1578)
      - `def _render_reset_confirm_modal(self, target_surf)` (Line 1650)
      - `def _render_background(self, target_surf)` (Line 1672)
      - `def _render_main_menu(self, target_surf)` (Line 1697)
      - `def _render_multiplayer_menu(self, target_surf)` (Line 1753)
      - `def _render_story_screen(self, target_surf)` (Line 1910)
      - `def _render_controls_screen(self, target_surf)` (Line 1913)
      - `def _render_victory_screen(self, target_surf)` (Line 1957)
      - `def _render_worlds_screen(self, target_surf)` (Line 1988)
      - `def _render_new_world_screen(self, target_surf)` (Line 2117)
      - `def _render_mods_screen(self, target_surf, mouse_pos)` (Line 2207)
      - `def handle_scroll(self, scroll_delta)` (Line 2272): Handles mouse wheel scrolling in menus (e.g. Achievements browser, Worlds list).
      - `def _render_achievements_screen(self, target_surf, mouse_pos)` (Line 2286)
      - `def _render_game_over_screen(self, target_surf)` (Line 2291)

#### `src/ui/minimap.py`
- **Size:** 15444 bytes | **Lines:** 334 lines
- **Description:** Potaria - Dynamic Radar & HUD Mini-Map
- **Classes Defined (1):**
  - **`class MiniMap`** (Line 103)
    - Methods (4):
      - `def __init__(self)` (Line 104)
      - `def mark_dirty(self)` (Line 124): Forces minimap terrain to re-bake on next render.
      - `def toggle(self)` (Line 128): Cycles between Corner Minimap -> Large Map -> Hidden.
      - `def render(self, target_surf, world, player, combat, lan_client)` (Line 142)

#### `src/ui/npc_dialogue.py`
- **Size:** 43050 bytes | **Lines:** 797 lines
- **Description:** Potaria - NPC Dialogue & Shop Interface
- **Classes Defined (1):**
  - **`class NPCDialogueWindow`** (Line 19)
    - Methods (8):
      - `def __init__(self, asset_factory, sound_manager)` (Line 20)
      - `def open(self, npc, player, world, combat)` (Line 47)
      - `def close(self)` (Line 82)
      - `def update(self, dt, player)` (Line 88)
      - `def _wrap_text(self, text, max_width, font)` (Line 118)
      - `def handle_click(self, mouse_x, mouse_y, player, inventory, world, combat)` (Line 134)
      - `def render(self, target_surf, player, inventory, mouse_x, mouse_y)` (Line 474)
      - `def _render_shop_item_tooltip(self, target_surf, mx, my, entry)` (Line 672): Displays rich Diablo/Torchlight-style item tooltip for shop wares.

#### `src/ui/theme.py`
- **Size:** 4396 bytes | **Lines:** 143 lines
- **Description:** Potaria - Centralized Typography & UI Theme Engine
- **Standalone Functions (9):**
  - `def _get_font_file_path(font_key)` (Line 38)
  - `def get_font(font_key, size)` (Line 51): Retrieves a cached pygame.font.Font instance for the specified font key and size.
  - `def font_regular(size)` (Line 88)
  - `def font_semibold(size)` (Line 92)
  - `def font_bold(size)` (Line 96)
  - `def font_title(size)` (Line 100)
  - `def font_compact(size)` (Line 104)
  - `def clear_font_cache()` (Line 108): Clears the font cache.
  - `def wrap_text_lines(text, font, max_width)` (Line 113): Wraps a string into a list of lines so none exceeds max_width pixels.

#### `src/ui/touch_controller.py`
- **Size:** 45446 bytes | **Lines:** 1024 lines
- **Description:** Potaria - Mobile Touchscreen Virtual Controller & UI/UX System
- **Classes Defined (4):**
  - **`class TouchRipple`** (Line 84) - Expanding visual touch wave emitted upon finger press for tactile feedback.
    - Methods (3):
      - `def __init__(self, x, y, color, max_radius, duration)` (Line 86)
      - `def update(self, dt)` (Line 94)
      - `def render(self, surface, opacity)` (Line 98)
  - **`class TouchButton`** (Line 114) - Mobile UI button adhering to touch ergonomics guidelines (>= 48x48 px hitbox,
    - Methods (8):
      - `def __init__(self, btn_id, shape, x, y, radius, rect, label, sublabel, color, hit_padding)` (Line 119)
      - `def contains(self, px, py)` (Line 141): Hitbox test guaranteeing >= 48x48 px minimum touch target.
      - `def on_touch_down(self, finger_id, px, py)` (Line 150)
      - `def on_touch_up(self, finger_id)` (Line 156)
      - `def update(self, dt)` (Line 164)
      - `def render(self, surface, font, font_sm, font_xs, opacity)` (Line 170)
      - `def _render_circle(self, surface, font, font_sm, font_xs, scale, alpha_mult)` (Line 180)
      - `def _render_rect(self, surface, font, font_sm, font_xs, scale, alpha_mult)` (Line 239)
  - **`class VirtualJoystick`** (Line 269) - Virtual thumbstick / D-Pad for walking, jumping, and dropping platforms.
    - Methods (9):
      - `def __init__(self, center_x, center_y, radius_base, radius_knob, radius_travel)` (Line 275)
      - `def contains(self, px, py)` (Line 296)
      - `def on_touch_down(self, finger_id, px, py)` (Line 299)
      - `def on_touch_move(self, finger_id, px, py)` (Line 305)
      - `def on_touch_up(self, finger_id)` (Line 309)
      - `def reset(self)` (Line 313)
      - `def _update_position(self, px, py)` (Line 325)
      - `def update(self, dt)` (Line 361)
      - `def render(self, surface, font_sm, font_xs, opacity)` (Line 368)
  - **`class TouchController`** (Line 428) - Main manager for mobile touch controls and UI/UX ergonomics.
    - Methods (22):
      - `def __init__(self, asset_factory, sound_manager)` (Line 433)
      - `def reset(self)` (Line 499): Safely resets all virtual touch states, fingers, and hold timers.
      - `def set_mode(self, mode)` (Line 513)
      - `def set_opacity(self, opacity)` (Line 517)
      - `def is_visible(self)` (Line 524): Returns True if virtual controls should be rendered and processed.
      - `def add_ripple(self, x, y, color)` (Line 539)
      - `def get_virtual_keys(self, raw_keys, key_bindings)` (Line 542): Synthesizes a combined key mapping including virtual joystick & buttons.
      - `def handle_touch_event(self, event, game)` (Line 602): Processes native SDL2 / Pygame FINGERDOWN, FINGERMOTION, FINGERUP events.
      - `def handle_mouse_down(self, mouse_x, mouse_y, button, game)` (Line 616): Simulates single-touch interaction from PC mouse for testing/playing.
      - `def handle_mouse_motion(self, mouse_x, mouse_y, game)` (Line 622)
      - `def handle_mouse_up(self, mouse_x, mouse_y, button, game)` (Line 627)
      - `def handle_touch_down(self, finger_id, px, py, game)` (Line 632)
      - `def handle_touch_motion(self, finger_id, px, py, game)` (Line 735)
      - `def handle_touch_up(self, finger_id, px, py, game)` (Line 749)
      - `def _execute_attack_or_mine(self, game)` (Line 780): Triggers primary attack or mining towards facing/aim angle, or places/consumes active item.
      - `def _execute_jump(self, game)` (Line 804): Executes jump or upward swimming.
      - `def _execute_dash(self, game)` (Line 823): Triggers dash skill or dodge roll.
      - `def _execute_direct_world_touch(self, px, py, game)` (Line 840): Targets world objects, blocks, interactive tiles, or enemies directly at touch location.
      - `def quick_heal(self, player, inventory, sound_manager, particle_system)` (Line 892)
      - `def count_healing_items(self, inventory)` (Line 895)
      - `def update(self, dt, player, inventory)` (Line 898)
      - `def render(self, surface, player, inventory, camera, game)` (Line 970)
- **Standalone Functions (2):**
  - `def quick_heal(player, inventory, sound_manager, particle_system)` (Line 35): Finds and drinks best potion or eats food from inventory.
  - `def count_healing_items(inventory)` (Line 75)

### Environment & Atmospheric Systems (`src/environment/*`)

#### `src/environment/sky.py`
- **Size:** 16508 bytes | **Lines:** 369 lines
- **Description:** Terraria Pygame - Sky, Day/Night Cycle & Multi-Plane Parallax Backgrounds
- **Classes Defined (1):**
  - **`class DayNightCycle`** (Line 18)
    - Methods (16):
      - `def __init__(self, asset_factory, cycle_duration)` (Line 19)
      - `def _load_background_assets(self)` (Line 52): Loads, pre-scales, and RLE-accelerates multi-plane parallax pixel art layers from assets/backgrounds/.
      - `def time_of_day(self)` (Line 89): Returns 0.0 to 1.0 representing progress through 24-hour cycle.
      - `def is_night(self)` (Line 94): Returns True if it is currently nighttime.
      - `def ambient_sunlight(self)` (Line 101): Calculates 2D light intensity (3 to 15) for the lighting engine.
      - `def atmospheric_tint(self)` (Line 123): Returns (r_mult, g_mult, b_mult) color grading based on celestial time.
      - `def update(self, dt)` (Line 137)
      - `def get_time_string(self)` (Line 140): Returns user-friendly in-game celestial time (e.g. '12:00 PM (Day)').
      - `def _lerp_color(self, c1, c2, t)` (Line 154)
      - `def get_sky_colors(self)` (Line 162): Returns (top_color, bottom_color) based on current celestial time.
      - `def get_altitude_sky_colors(self, camera_y_tile)` (Line 197): Transitions sky colors naturally based on altitude:
      - `def _create_mountain_silhouette(self)` (Line 236)
      - `def _create_tree_silhouette(self)` (Line 250)
      - `def _create_star_frames(self)` (Line 260)
      - `def _create_star_surfaces(self)` (Line 275)
      - `def render(self, target_surf, camera)` (Line 293): Draws pure sky gradient, twinkling stars, and sun/moon celestial bodies.

#### `src/environment/sky_presets.py`
- **Size:** 4646 bytes | **Lines:** 131 lines
- **Description:** Potaria - Celestial Day-Night Presets & Color Interpolation Engine
- **Standalone Functions (5):**
  - `def srgb_to_linear(c)` (Line 49): Converts 8-bit sRGB color to linear photometric color space.
  - `def linear_to_srgb(c_lin)` (Line 58): Converts linear color space values back to clamped 8-bit sRGB.
  - `def hermite_smoothstep(t)` (Line 67): Cubic Hermite S-curve interpolation factor with zero derivatives at endpoints.
  - `def lerp_color_hermite(c1, c2, t)` (Line 73): Interpolates between two sRGB colors in linear color space using cubic Hermite smoothing.
  - `def get_procedural_sky_colors(time_of_day)` (Line 89): Computes exact top and bottom sky gradient colors for any celestial time of day

### Audio Systems (`src/audio/*`)

#### `src/audio/bgm_manager.py`
- **Size:** 24244 bytes | **Lines:** 506 lines
- **Description:** Potaria - Cinematic Procedural Synth Background Music (BGM) Engine
- **Classes Defined (1):**
  - **`class BgmManager`** (Line 20)
    - Methods (9):
      - `def __init__(self)` (Line 21)
      - `def _make_loop_sound(self, samples, sample_rate, track_name)` (Line 49)
      - `def _synthesize_all_tracks(self)` (Line 69)
      - `def set_volumes(self, master, bgm)` (Line 355)
      - `def _apply_channel_volumes(self, blend_a, blend_b)` (Line 363)
      - `def transition_to(self, track_name)` (Line 373)
      - `def update(self, dt, current_biome, has_nearby_threat, is_boss_active, boss_phase, is_grand_boss, scene, is_night, is_cavern)` (Line 402)
      - `def update_tick(self, dt)` (Line 471): Advances active crossfade without switching target tracks (e.g. while paused in-game).
      - `def stop(self)` (Line 500)

#### `src/audio/narrator_voice.py`
- **Size:** 20405 bytes | **Lines:** 496 lines
- **Description:** Potaria - Cinematic Narrator Voice Engine
- **Standalone Functions (6):**
  - `def resolve_target_dir(d)` (Line 22): Resolves relative asset paths to absolute paths anchored at project root.
  - `def normalize_scene_key(scene_id)` (Line 131): Normalizes any scene name, integer, or identifier to standard narrator track key.
  - `def save_wav_file(filepath, samples, sample_rate)` (Line 164): Writes normalized mono/stereo floating point samples (-1.0 to 1.0) as 16-bit stereo WAV.
  - `def synthesize_procedural_narrator_track(text, sample_rate)` (Line 180): Synthesizes deep, mythic, resonant cinematic storyteller narration.
  - `def generate_narrator_voices_with_gemini(api_key, target_dirs, track_dict)` (Line 308): Attempts to generate high-fidelity cinematic narrator voice tracks using the Gemini API
  - `def ensure_narrator_audio_assets(target_dirs, force_regenerate, sample_rate)` (Line 430): Ensures that all narrator cutscene WAV files exist on disk (both 4 scene acts and dialogue segments).

#### `src/audio/sound_effects.py`
- **Size:** 28257 bytes | **Lines:** 689 lines
- **Description:** Terraria Pygame - Procedural Retro Sound Engine
- **Classes Defined (1):**
  - **`class SoundManager`** (Line 12)
    - Methods (12):
      - `def __init__(self)` (Line 13)
      - `def set_volumes(self, master, sfx, bgm)` (Line 39)
      - `def _make_sound(self, samples, sample_rate)` (Line 45): Converts floating point samples (-1.0 to 1.0) into a stereo pygame Sound object.
      - `def _synthesize_all_sounds(self)` (Line 55)
      - `def _load_or_synthesize_narrator_sounds(self)` (Line 495): Loads or synthesizes the cutscene cinematic narrator voice tracks (scenes and segments).
      - `def play(self, sound_name, volume)` (Line 515): Plays a sound uniformly at given volume.
      - `def play_spatial(self, sound_name, sound_x, sound_y, listener_x, listener_y, max_distance)` (Line 543): Plays 3D spatial directional stereo sound with distance attenuation and panning.
      - `def play_swing(self, cooldown, speed_mult)` (Line 570): Plays weapon swing swoosh scaled to weapon archetype and attack speed.
      - `def play_voice(self, speaker, volume)` (Line 578): Plays a character's retro synth voice blip according to speaker identity.
      - `def play_narrator(self, scene_id, volume)` (Line 635): Plays the deep, mythic cinematic cutscene narrator voice track for the specified scene or dialogue entry.
      - `def stop_narrator(self, fade_ms)` (Line 666): Stops or smoothly fades out the cutscene narrator voice track.
      - `def is_narrator_playing(self)` (Line 679): Returns True if the narrator voice track is currently actively playing.

### Rendering HAL & Shaders (`src/rendering/*`)

#### `src/rendering/__init__.py`
- **Size:** 1349 bytes | **Lines:** 47 lines
- **Description:** Potaria - Rendering Package (Hardware Abstraction Layer)
- **Standalone Functions (2):**
  - `def get_renderer_manager()` (Line 17): Returns the singleton RendererManager instance.
  - `def create_renderer(renderer_type, width, height, title, fullscreen)` (Line 22): Factory function to instantiate a specific renderer directly.

#### `src/rendering/base_renderer.py`
- **Size:** 7573 bytes | **Lines:** 250 lines
- **Description:** Potaria - Renderer Hardware Abstraction Layer (HAL)
- **Classes Defined (1):**
  - **`class BaseRenderer`** (Line 16) - Abstract Base Class for Potaria's Hardware Abstraction Layer.
    - Methods (35):
      - `def __init__(self, width, height, title, fullscreen)` (Line 22)
      - `def initialize(self)` (Line 36): Initializes the rendering context / display window.
      - `def clear(self, color)` (Line 44): Clears the screen or backbuffer with the specified color.
      - `def draw_sprite(self, surface, dest, area, special_flags)` (Line 49): Draws a sprite or sub-rectangle of a surface onto the target buffer.
      - `def draw_surface(self, surface, dest, area, special_flags)` (Line 60): Draws a pygame Surface onto the target buffer.
      - `def draw_rect(self, color, rect, width, border_radius)` (Line 71): Draws a rectangle with optional border outline and rounded corners.
      - `def draw_text(self, font, text, pos, color, antialias)` (Line 82): Renders and draws text at the target position, returning the bounding rect.
      - `def draw_line(self, color, start_pos, end_pos, width)` (Line 94): Draws a line between two points.
      - `def draw_circle(self, color, center, radius, width)` (Line 105): Draws a circle at the given center coordinates.
      - `def present(self)` (Line 116): Presents the rendered frame to the display window (flips backbuffer).
      - `def get_surface(self)` (Line 121): Returns the native pygame.Surface target for direct blitting.
      - `def set_mode(self, width, height, fullscreen)` (Line 129): Reconfigures resolution and fullscreen state.
      - `def is_hardware_accelerated(self)` (Line 134): Returns True if the backend is actively using hardware GPU acceleration.
      - `def get_renderer_type(self)` (Line 139): Returns 'hardware' or 'software'.
      - `def draw_projectiles_batch(self, projectiles, camera)` (Line 144): Renders a high-density batch of projectiles in an optimized pass.
      - `def set_bloom_enabled(self, enabled)` (Line 155): Configures GLSL bloom post-processing state.
      - `def set_bloom_intensity(self, intensity)` (Line 159): Sets bloom post-processing aura intensity.
      - `def set_bloom_threshold(self, threshold)` (Line 163): Sets bloom luminance extraction threshold.
      - `def get_bloom_params(self)` (Line 167): Returns active bloom parameters.
      - `def set_shaders_enabled(self, enabled)` (Line 171): Toggles master GLSL post-processing shaders.
      - `def is_shaders_enabled(self)` (Line 175): Returns True if post-processing shaders are active.
      - `def set_vignette_enabled(self, enabled)` (Line 179): Toggles atmospheric cinematic vignette.
      - `def set_vignette_intensity(self, intensity)` (Line 183): Configures vignette corner falloff intensity.
      - `def set_water_distortion_enabled(self, enabled)` (Line 187): Toggles water wave refraction and distortion.
      - `def set_water_distortion_intensity(self, intensity)` (Line 191): Configures water wave distortion amplitude.
      - `def set_color_grading_mode(self, mode)` (Line 195): Configures color grading profile (standard, vibrant, cinematic, cool).
      - `def set_saturation(self, saturation)` (Line 199): Configures color vibrance saturation factor.
      - `def set_contrast(self, contrast)` (Line 203): Configures color grading contrast ratio.
      - `def set_lighting_quality(self, quality)` (Line 207): Configures dynamic lighting resolution quality.
      - `def set_particle_density(self, density)` (Line 211): Configures particle generation density.
      - `def get_graphics_params(self)` (Line 215): Returns comprehensive graphics configuration dictionary.
      - `def get_ui_surface(self)` (Line 233): Returns the pygame.Surface dedicated to crisp UI/HUD rendering (without bloom).
      - `def set_display_resolution(self, width, height, fullscreen)` (Line 237): Sets the target display resolution mode (e.g. 1920x1080, 1600x900, 1366x768, 1280x720).
      - `def window_to_virtual_pos(self, pos)` (Line 242): Translates window mouse coordinates to virtual screen coordinates.
      - `def cleanup(self)` (Line 247): Releases all graphics and windowing resources cleanly.

#### `src/rendering/gl_renderer.py`
- **Size:** 42626 bytes | **Lines:** 1080 lines
- **Description:** Potaria - Renderer Hardware Abstraction Layer (HAL)
- **Classes Defined (1):**
  - **`class GLRenderer`** (Line 32) - Hardware-accelerated OpenGL / ModernGL Renderer with automatic safety fallback.
    - Methods (46):
      - `def reset_fallback_log(cls)` (Line 190): Resets the fallback warning logged state (primarily for automated unit tests).
      - `def __init__(self, width, height, title, fullscreen)` (Line 195)
      - `def using_fallback(self)` (Line 248): Indicates whether this GLRenderer has fallen back to software blitting.
      - `def _get_desktop_resolution(self)` (Line 252): Returns the primary monitor desktop resolution for borderless fullscreen.
      - `def initialize(self)` (Line 264): Attempts to initialize a ModernGL hardware context.
      - `def _cleanup_gl_resources(self)` (Line 312): Safely releases ModernGL textures, buffers, arrays, programs, and contexts.
      - `def _engage_fallback(self, reason)` (Line 338): Activates graceful fallback to SurfaceRenderer.
      - `def _init_gl_pipeline(self)` (Line 370): Sets up the ModernGL full-screen quad shader, world FBO, UI overlay, and virtual surfaces.
      - `def _update_viewport(self)` (Line 460): Calculates and sets the OpenGL viewport to fit/fill the window while preserving aspect ratio.
      - `def _update_shader_uniforms(self)` (Line 498): Updates active shader uniforms for bloom, vignette, water distortion, color grading, resolution, and time.
      - `def clear(self, color)` (Line 525)
      - `def draw_sprite(self, surface, dest, area, special_flags)` (Line 540)
      - `def draw_surface(self, surface, dest, area, special_flags)` (Line 554)
      - `def draw_rect(self, color, rect, width, border_radius)` (Line 568)
      - `def draw_text(self, font, text, pos, color, antialias)` (Line 582)
      - `def draw_line(self, color, start_pos, end_pos, width)` (Line 598)
      - `def draw_circle(self, color, center, radius, width)` (Line 612)
      - `def present(self)` (Line 626): Presents the frame via ModernGL quad or falls back to standard blit flip.
      - `def draw_projectiles_batch(self, projectiles, camera)` (Line 686): Renders a high-density batch of projectiles in an optimized pass.
      - `def set_bloom_enabled(self, enabled)` (Line 771)
      - `def set_bloom_intensity(self, intensity)` (Line 779)
      - `def set_bloom_threshold(self, threshold)` (Line 787)
      - `def get_bloom_params(self)` (Line 795)
      - `def set_shaders_enabled(self, enabled)` (Line 802)
      - `def is_shaders_enabled(self)` (Line 810)
      - `def set_vignette_enabled(self, enabled)` (Line 813)
      - `def set_vignette_intensity(self, intensity)` (Line 821)
      - `def set_water_distortion_enabled(self, enabled)` (Line 829)
      - `def set_water_distortion_intensity(self, intensity)` (Line 837)
      - `def set_color_grading_mode(self, mode)` (Line 845)
      - `def set_saturation(self, saturation)` (Line 857)
      - `def set_contrast(self, contrast)` (Line 865)
      - `def set_lighting_quality(self, quality)` (Line 873)
      - `def set_particle_density(self, density)` (Line 879)
      - `def get_graphics_params(self)` (Line 885)
      - `def get_surface(self)` (Line 902): Returns the target surface for backward compatibility.
      - `def get_ui_surface(self)` (Line 913): Returns the dedicated UI surface for clean, bloom-free interface rendering.
      - `def window_to_virtual_pos(self, pos)` (Line 921): Translates window mouse coordinates to virtual screen coordinates.
      - `def set_display_resolution(self, width, height, fullscreen)` (Line 945): Sets target display resolution mode (e.g. 1920x1080, 1600x900, 1366x768, 1280x720).
      - `def set_mode(self, width, height, fullscreen)` (Line 982)
      - `def _sync_window_frame_and_pos(self)` (Line 996): Synchronizes SDL2 window borderless frame, size, and position for runtime fullscreen toggling.
      - `def _apply_display_mode(self)` (Line 1028): Applies windowed or borderless fullscreen display mode smoothly without monitor stalling.
      - `def is_hardware_accelerated(self)` (Line 1054)
      - `def get_renderer_type(self)` (Line 1057)
      - `def get_status_description(self)` (Line 1062): Returns human-readable renderer status.
      - `def cleanup(self)` (Line 1070)

#### `src/rendering/renderer_manager.py`
- **Size:** 16833 bytes | **Lines:** 406 lines
- **Description:** Potaria - Renderer Hardware Abstraction Layer (HAL)
- **Classes Defined (1):**
  - **`class RendererManager`** (Line 20) - Central manager for Potaria's graphics backends.
    - Methods (41):
      - `def get_instance(cls)` (Line 30): Returns the singleton instance of RendererManager.
      - `def __init__(self)` (Line 36)
      - `def initialize(self, width, height, title, fullscreen, requested_type)` (Line 59): Initializes the active renderer according to requested type.
      - `def switch_renderer(self, new_type, fullscreen)` (Line 118): Switches the rendering backend to new_type ('hardware' or 'software')
      - `def set_fullscreen(self, fullscreen)` (Line 147): Sets fullscreen or windowed display mode on the active renderer.
      - `def toggle_renderer(self, fullscreen)` (Line 162): Toggles between Hardware and Software renderer.
      - `def renderer(self)` (Line 172): Returns the active BaseRenderer instance.
      - `def surface(self)` (Line 179): Returns the active pygame.Surface for rendering.
      - `def ui_surface(self)` (Line 184): Returns the active pygame.Surface for crisp UI/HUD rendering (without bloom).
      - `def get_ui_surface(self)` (Line 188): Explicit getter for UI surface.
      - `def window_to_virtual_pos(self, pos)` (Line 192): Translates window mouse coordinates to virtual screen coordinates.
      - `def set_display_resolution(self, width, height, fullscreen)` (Line 198): Sets the display resolution for the active renderer.
      - `def is_hardware(self)` (Line 211): Returns True if the active renderer is using GPU acceleration.
      - `def using_fallback(self)` (Line 216): Returns True if the active renderer is in fallback mode.
      - `def get_status_label(self)` (Line 220): Returns the formatted label for the Video Settings button:
      - `def clear(self, color)` (Line 230)
      - `def present(self)` (Line 233)
      - `def draw_sprite(self, surface, dest, area, special_flags)` (Line 236)
      - `def draw_surface(self, surface, dest, area, special_flags)` (Line 245)
      - `def draw_rect(self, color, rect, width, border_radius)` (Line 254)
      - `def draw_text(self, font, text, pos, color, antialias)` (Line 263)
      - `def draw_line(self, color, start_pos, end_pos, width)` (Line 273)
      - `def draw_circle(self, color, center, radius, width)` (Line 282)
      - `def draw_projectiles_batch(self, projectiles, camera)` (Line 291): Delegates high-density projectile batch rendering to active renderer.
      - `def set_bloom_enabled(self, enabled)` (Line 301): Configures GLSL bloom post-processing on active renderer.
      - `def set_bloom_intensity(self, intensity)` (Line 307): Sets bloom post-processing aura intensity on active renderer.
      - `def set_bloom_threshold(self, threshold)` (Line 313): Sets bloom luminance threshold on active renderer.
      - `def get_bloom_params(self)` (Line 319): Returns active bloom parameters from active renderer.
      - `def set_shaders_enabled(self, enabled)` (Line 325)
      - `def is_shaders_enabled(self)` (Line 330)
      - `def set_vignette_enabled(self, enabled)` (Line 335)
      - `def set_vignette_intensity(self, intensity)` (Line 340)
      - `def set_water_distortion_enabled(self, enabled)` (Line 345)
      - `def set_water_distortion_intensity(self, intensity)` (Line 350)
      - `def set_color_grading_mode(self, mode)` (Line 355)
      - `def set_saturation(self, saturation)` (Line 364)
      - `def set_contrast(self, contrast)` (Line 369)
      - `def set_lighting_quality(self, quality)` (Line 374)
      - `def set_particle_density(self, density)` (Line 379)
      - `def get_graphics_params(self)` (Line 384)
      - `def cleanup(self)` (Line 403)

#### `src/rendering/surface_renderer.py`
- **Size:** 17582 bytes | **Lines:** 456 lines
- **Description:** Potaria - Renderer Hardware Abstraction Layer (HAL)
- **Classes Defined (1):**
  - **`class SurfaceRenderer`** (Line 16) - Native Pygame-ce Software Renderer.
    - Methods (37):
      - `def __init__(self, width, height, title, fullscreen)` (Line 23)
      - `def _get_desktop_resolution(self)` (Line 51): Returns the primary monitor desktop resolution for borderless fullscreen.
      - `def _sync_window_frame_and_pos(self)` (Line 63): Synchronizes SDL2 window borderless frame, size, and position for runtime fullscreen toggling.
      - `def initialize(self)` (Line 95): Initializes the Pygame display mode with double-buffering and crisp scaling.
      - `def clear(self, color)` (Line 128): Fills the primary display surface with a solid color and clears the UI layer.
      - `def draw_sprite(self, surface, dest, area, special_flags)` (Line 135): Blits a sprite surface directly to the target surface.
      - `def draw_surface(self, surface, dest, area, special_flags)` (Line 146): Blits an arbitrary surface directly to the target surface.
      - `def draw_rect(self, color, rect, width, border_radius)` (Line 157): Draws a geometric rectangle onto the display surface.
      - `def draw_text(self, font, text, pos, color, antialias)` (Line 168): Renders text and blits it at the given coordinates.
      - `def draw_line(self, color, start_pos, end_pos, width)` (Line 182): Draws a line on the display surface.
      - `def draw_circle(self, color, center, radius, width)` (Line 193): Draws a circle on the display surface.
      - `def present(self)` (Line 204): Presents the frame by compositing the UI layer and flipping the display buffer.
      - `def get_surface(self)` (Line 210): Returns the active display surface for seamless compatibility.
      - `def get_ui_surface(self)` (Line 216): Returns the dedicated UI surface for clean, bloom-free interface rendering.
      - `def set_mode(self, width, height, fullscreen)` (Line 222): Reconfigures resolution and fullscreen state.
      - `def set_display_resolution(self, width, height, fullscreen)` (Line 229): Sets target display resolution mode.
      - `def is_hardware_accelerated(self)` (Line 262): SurfaceRenderer uses CPU-side software blitting.
      - `def get_renderer_type(self)` (Line 266): Returns 'software'.
      - `def draw_projectiles_batch(self, projectiles, camera)` (Line 270): Renders a high-density batch of projectiles using optimized C-level multi-blitting.
      - `def set_bloom_enabled(self, enabled)` (Line 352)
      - `def set_bloom_intensity(self, intensity)` (Line 355)
      - `def set_bloom_threshold(self, threshold)` (Line 358)
      - `def get_bloom_params(self)` (Line 361)
      - `def set_shaders_enabled(self, enabled)` (Line 368)
      - `def is_shaders_enabled(self)` (Line 371)
      - `def set_vignette_enabled(self, enabled)` (Line 374)
      - `def set_vignette_intensity(self, intensity)` (Line 377)
      - `def set_water_distortion_enabled(self, enabled)` (Line 380)
      - `def set_water_distortion_intensity(self, intensity)` (Line 383)
      - `def set_color_grading_mode(self, mode)` (Line 386)
      - `def set_saturation(self, saturation)` (Line 393)
      - `def set_contrast(self, contrast)` (Line 396)
      - `def set_lighting_quality(self, quality)` (Line 399)
      - `def set_particle_density(self, density)` (Line 402)
      - `def get_graphics_params(self)` (Line 405)
      - `def window_to_virtual_pos(self, pos)` (Line 422): Translates physical window/touchscreen coordinates to virtual canvas (1280x720).
      - `def cleanup(self)` (Line 452): Releases renderer resources.

### Modding & Extensibility (`src/modding/*`)

#### `src/modding/__init__.py`
- **Size:** 267 bytes | **Lines:** 8 lines
- **Description:** Potaria - Modding & DLC Expansion System
- *Declarative definition module containing data constants, dictionaries, and configurations.*

#### `src/modding/mod_manager.py`
- **Size:** 22182 bytes | **Lines:** 549 lines
- **Description:** Potaria - Modding & DLC Expansion Engine
- **Classes Defined (2):**
  - **`class ModManifest`** (Line 79) - Represents a discovered Mod or DLC manifest.
    - Methods (2):
      - `def __init__(self, content_id, name, version, author, description, content_type, enabled, directory, manifest_file, items, recipes, tiles, mobs, textures, raw_data)` (Line 81)
      - `def to_dict(self)` (Line 115)
  - **`class ModManager`** (Line 130) - Central manager for discovering, loading, and applying community mods
    - Methods (19):
      - `def __init__(self, mods_dir, dlc_dir)` (Line 135)
      - `def ensure_directories(self)` (Line 145): Creates the default mods/ and dlc/ directories if they don't exist.
      - `def discover(self)` (Line 150): Scans mods/ and dlc/ directories for mod.json and dlc.json manifests.
      - `def _parse_manifest(self, manifest_file, directory, default_type)` (Line 182): Reads and validates a manifest JSON file.
      - `def load_all(self, asset_factory, crafting_system)` (Line 222): Discovers and registers all enabled mods and DLCs.
      - `def _apply_manifest(self, manifest, asset_factory, crafting_system)` (Line 260): Applies items, recipes, and textures defined in a manifest.
      - `def register_item(self, item_id, item_data, asset_factory)` (Line 305): Safely normalizes and registers an item into ITEM_REGISTRY.
      - `def unregister_item(self, item_id)` (Line 375): Removes an item from ITEM_REGISTRY and data-driven registry.
      - `def register_recipe(self, recipe_data, crafting_system)` (Line 389): Safely normalizes and registers a crafting recipe into RECIPES.
      - `def unregister_recipe(self, recipe_or_result, crafting_system)` (Line 444): Removes a crafting recipe from RECIPES and data-driven registry.
      - `def unload_all(self, asset_factory, crafting_system)` (Line 462): Unloads all registered items, recipes, and textures from mods and DLCs.
      - `def register_texture(self, category, key, image_path, asset_factory)` (Line 474): Loads an external sprite image and registers it into AssetFactory or internal cache.
      - `def get_mod(self, mod_id)` (Line 507)
      - `def get_dlc(self, dlc_id)` (Line 510)
      - `def get_all_mods(self)` (Line 513)
      - `def get_all_dlc(self)` (Line 516)
      - `def is_mod_loaded(self, mod_id)` (Line 519)
      - `def is_dlc_loaded(self, dlc_id)` (Line 522)
      - `def set_content_enabled(self, content_id, enabled)` (Line 525): Enables or disables a mod or DLC manifest and updates manifest on disk.
- **Standalone Functions (1):**
  - `def get_mod_manager()` (Line 545)

### Multiplayer & Networking (`src/network/*`)

#### `src/network/client.py`
- **Size:** 13336 bytes | **Lines:** 338 lines
- **Description:** Potaria - LAN Client Network Handler
- **Classes Defined (2):**
  - **`class LANDiscovery`** (Line 25) - Listens for UDP broadcast beacons on DISCOVERY_PORT and tracks active LAN servers.
    - Methods (5):
      - `def __init__(self, port)` (Line 27)
      - `def start(self)` (Line 34)
      - `def _listen_loop(self)` (Line 41)
      - `def get_servers(self)` (Line 90)
      - `def stop(self)` (Line 94)
  - **`class LANClient`** (Line 103)
    - Methods (12):
      - `def __init__(self)` (Line 104)
      - `def connect(self, host_ip, port, player_name, room_key)` (Line 121)
      - `def _recv_loop(self)` (Line 157)
      - `def send_player_update(self, x, y, vx, vy, hp, max_hp, level, facing, anim, held_item)` (Line 208)
      - `def send_block_delta(self, tx, ty, tile_id)` (Line 221)
      - `def send_chat(self, name, text)` (Line 230)
      - `def send_mob_damage(self, mob_id, damage, knockback_vx, knockback_vy, is_crit)` (Line 239): Sends client-inflicted damage to a mob or boss to authoritative server.
      - `def send_sync_mobs(self, mobs_data, boss_data, sky_time, enemy_projectiles, dropped_items)` (Line 255): Called by Host client to upload authoritative mobs list to server.
      - `def get_latest_mob_sync(self)` (Line 271): Retrieves and consumes the latest mob state snapshot from host.
      - `def get_pending_mob_damages(self)` (Line 278): Retrieves and consumes pending mob damage events.
      - `def render_remote_players(self, target_surf, camera, asset_factory)` (Line 285): Draws other connected potato players in the world with sub-pixel lerp smoothing and 12 FPS animations.
      - `def disconnect(self)` (Line 332)

#### `src/network/protocol.py`
- **Size:** 1735 bytes | **Lines:** 45 lines
- **Description:** Potaria - LAN Cooperative Multiplayer Protocol
- **Standalone Functions (2):**
  - `def encode_packet(pkt_type, data)` (Line 21): Encodes a packet into UTF-8 JSON bytes with newline delimiter.
  - `def decode_packets(raw_buffer)` (Line 26): Decodes all complete newline-delimited JSON packets from a buffer.

#### `src/network/server.py`
- **Size:** 10194 bytes | **Lines:** 259 lines
- **Description:** Potaria - LAN Authoritative Server
- **Classes Defined (1):**
  - **`class LANServer`** (Line 23)
    - Methods (11):
      - `def __init__(self, host, port, max_players, server_name, room_key)` (Line 24)
      - `def start(self, world_seed, host_is_client)` (Line 41)
      - `def _beacon_broadcast_loop(self)` (Line 74): Broadcasts UDP presence beacon on DISCOVERY_PORT every 1.5 seconds.
      - `def _accept_loop(self)` (Line 103)
      - `def _client_handler(self, player_id, sock)` (Line 134)
      - `def _broadcast_sync_loop(self)` (Line 192): Broadcasts player states to all clients at 20 Hz (every 50ms).
      - `def update_host_player(self, x, y, vx, vy, hp, max_hp, level, facing, anim, held_item)` (Line 207): Called by Host client to update Player 1 state.
      - `def broadcast(self, pkt_type, data, exclude_pid)` (Line 217): Sends packet to all connected client sockets.
      - `def broadcast_mobs(self, mobs_data, boss_data, sky_time, enemy_projectiles, dropped_items)` (Line 228): Sends authoritative mobs and boss state to all connected clients.
      - `def get_pending_mob_damages(self)` (Line 241): Called by Host to retrieve and drain client-inflicted mob damage events.
      - `def stop(self)` (Line 248)

### Asset Generation & Factories (`src/assets/*`)

#### `src/assets/asset_factory.py`
- **Size:** 574903 bytes | **Lines:** 9972 lines
- **Description:** Potaria - Procedural Pixel Art Asset Engine (Terraria x Stardew Valley Aesthetic)
- **Classes Defined (2):**
  - **`class ItemSpriteDict`** (Line 155) - Dynamic sprite dictionary with procedural generation and alias resolution.
    - Methods (4):
      - `def __init__(self, factory)` (Line 157)
      - `def __getitem__(self, key)` (Line 161)
      - `def get(self, key, default)` (Line 200)
      - `def __contains__(self, key)` (Line 208)
  - **`class AssetFactory`** (Line 219)
    - Methods (86):
      - `def __init__(self)` (Line 220)
      - `def generate_all(self)` (Line 244)
      - `def _get_item_palette(self, item_id, rarity, h)` (Line 265)
      - `def _draw_sapling_sprite(self, surf, item_id, h)` (Line 339): Draws unique saplings: oak, palm, pine, blight
      - `def _draw_fishing_rod_sprite(self, surf, item_id, with_string)` (Line 379)
      - `def get_rod_sprite(self, item_id, in_use)` (Line 404): Returns the fishing rod sprite asset. If in_use=True, returns rod without string to avoid redundancy when casting/fishing.
      - `def _draw_pinoy_fish(self, surf, item_id, h)` (Line 418)
      - `def _draw_pinoy_cooked_fish(self, surf, item_id, h)` (Line 517)
      - `def _draw_hoe_sprite(self, surf, item_id, h)` (Line 618): Draws authentic farming hoes (Kawayan Bamboo Hoe or Forged Iron Hoe).
      - `def _draw_watering_can_sprite(self, surf, item_id, h)` (Line 645): Draws traditional Philippine tin/metal watering can (Regadera).
      - `def _draw_seed_packet_sprite(self, surf, item_id, h)` (Line 671): Draws rustic burlap/abaca seed pouch with native crop emblem.
      - `def _is_pinoy_food_or_ingredient(self, id_lower)` (Line 717)
      - `def _draw_pinoy_food_and_ingredients(self, surf, item_id, h)` (Line 732)
      - `def generate_item_icon(self, item_id)` (Line 1394): Generates a unique, beautifully shaded 24x24 pixel art icon for any item.
      - `def _apply_grand_silhouette_accents(self, surf, pal, rarity, h)` (Line 1551): Upper rarity silhouette finishing (floating motes removed to avoid stray pixels).
      - `def _apply_hallmark_insignia(self, surf, pal, rarity, h)` (Line 1555): Applies a distinct visible runic signature glyph or facet based on hash.
      - `def _draw_five_point_star(self, surf, cx, cy, r_outer, r_inner, outline_col, fill_col, core_col, rot_offset)` (Line 1602)
      - `def _draw_bespoke_iconic_item(self, surf, item_id, pal, rarity, h)` (Line 1619)
      - `def _draw_weapon_sprite(self, surf, item_id, pal, rarity, h)` (Line 2152)
      - `def _draw_cleaver_sprite(self, surf, item_id, pal, rarity, h)` (Line 2186): Heavy butcher/war cleaver with broad rectangular/curved chopping blade & spine hole.
      - `def _draw_rapier_sprite(self, surf, item_id, pal, rarity, h)` (Line 2212): Aristocratic dueling rapier with ornate swept-hilt cup guard & needle-thin blade.
      - `def _draw_cutlass_sprite(self, surf, item_id, pal, rarity, h)` (Line 2232): Curved pirate/cavalry saber/cutlass with brass D-shaped knuckle bow.
      - `def _draw_focus_catalyst_sprite(self, surf, item_id, pal, rarity, h)` (Line 2253): Floating arcane astrolabe / polyhedral crystal catalyst with orbital rings.
      - `def _draw_katana_sprite(self, surf, item_id, pal, rarity, h)` (Line 2280): Authentic Japanese curved katana with hamon temper line, disc tsuba & wrapped tsuka.
      - `def _draw_sword_sprite(self, surf, item_id, pal, rarity, h)` (Line 2313): Broadsword, greatsword, claymore, flamberge, or shortsword.
      - `def _draw_crossbow_sprite(self, surf, item_id, pal, rarity, h)` (Line 2408): Crossbow: heavy wooden/metal stock, horizontal recurve prods, trigger, iron stirrup.
      - `def _draw_bow_sprite(self, surf, item_id, pal, rarity, h)` (Line 2430): Bow / Longbow / Recurve / Shortbow with distinct limb curvature.
      - `def _draw_staff_sprite(self, surf, item_id, pal, rarity, h)` (Line 2472): Staff / Wand / Rod / Scepter with noun-specific length and head ornament.
      - `def _draw_tome_sprite(self, surf, item_id, pal, rarity, h)` (Line 2525): Grimoire / Tome / Skillbook with brass corners, spine shading & glowing arcane sigil.
      - `def _draw_hammer_sprite(self, surf, item_id, pal, rarity, h)` (Line 2564): Warhammer (twin-faced block/beak) vs Mace/Morningstar (spiked flanged sphere).
      - `def _draw_scythe_sprite(self, surf, item_id, pal, rarity, h)` (Line 2607): Scythe vs Halberd vs Glaive polearms.
      - `def _draw_spear_sprite(self, surf, item_id, pal, rarity, h)` (Line 2645): Spear / Pike / Lance with distinct head geometry.
      - `def _draw_dagger_sprite(self, surf, item_id, pal, rarity, h)` (Line 2686): Dagger / Kris / Stiletto: compact sharp blade with jewel pommel.
      - `def _draw_head_sprite(self, surf, item_id, pal, rarity, h)` (Line 2710)
      - `def _draw_chest_sprite(self, surf, item_id, pal, rarity, h)` (Line 2895)
      - `def _draw_legs_sprite(self, surf, item_id, pal, rarity, h)` (Line 3081)
      - `def _draw_accessory_sprite(self, surf, item_id, pal, rarity, h)` (Line 3179)
      - `def _draw_arrow_sprite(self, surf, item_id, pal, rarity, h)` (Line 3332): Renders diagonal fletched arrows with elemental tips and trails.
      - `def _draw_tool_sprite(self, surf, item_id, pal, rarity, h)` (Line 3386)
      - `def _draw_consumable_sprite(self, surf, item_id, pal, rarity, h)` (Line 3437)
      - `def _draw_material_sprite(self, surf, item_id, pal, rarity, h)` (Line 3453)
      - `def _draw_generic_sprite(self, surf, item_id, pal, rarity, h)` (Line 3482)
      - `def _draw_shield_sprite(self, surf, item_id, pal, rarity, h)` (Line 3488)
      - `def _draw_lantern_sprite(self, surf, item_id, pal, rarity, h)` (Line 3518)
      - `def _draw_hearth_sprite(self, surf, item_id, pal, rarity, h)` (Line 3547)
      - `def _draw_anvil_sprite(self, surf, item_id, pal, rarity, h)` (Line 3566)
      - `def _draw_whetstone_sprite(self, surf, item_id, pal, rarity, h)` (Line 3573)
      - `def _draw_retort_sprite(self, surf, item_id, pal, rarity, h)` (Line 3580)
      - `def _draw_clippers_sprite(self, surf, item_id, pal, rarity, h)` (Line 3588)
      - `def _draw_sparker_sprite(self, surf, item_id, pal, rarity, h)` (Line 3594)
      - `def _draw_compass_sprite(self, surf, item_id, pal, rarity, h)` (Line 3599)
      - `def _draw_spyglass_sprite(self, surf, item_id, pal, rarity, h)` (Line 3610)
      - `def _draw_clock_sprite(self, surf, item_id, pal, rarity, h)` (Line 3617)
      - `def _draw_satchel_sprite(self, surf, item_id, pal, rarity, h)` (Line 3636)
      - `def _draw_tether_sprite(self, surf, item_id, pal, rarity, h)` (Line 3642)
      - `def _draw_cauldron_sprite(self, surf, item_id, pal, rarity, h)` (Line 3648)
      - `def _draw_totem_sprite(self, surf, item_id, pal, rarity, h)` (Line 3656)
      - `def _draw_quiver_sprite(self, surf, item_id, pal, rarity, h)` (Line 3664)
      - `def _draw_saw_sprite(self, surf, item_id, pal, rarity, h)` (Line 3674)
      - `def _draw_target_sprite(self, surf, item_id, pal, rarity, h)` (Line 3680)
      - `def _draw_loom_sprite(self, surf, item_id, pal, rarity, h)` (Line 3688)
      - `def _draw_food_sprite(self, surf, item_id, pal, rarity, h)` (Line 3694)
      - `def _draw_craft_block_sprite(self, surf, item_id, pal, rarity, h)` (Line 3718)
      - `def _create_cute_leaf_variant(self, base_surf, up, down, left, right, hi_col, sh_col, snow_cap)` (Line 4303): Creates an organic, cute, non-square pixel-art leaf variant for exposed edges and rounded corners.
      - `def _generate_tiles(self)` (Line 4357)
      - `def get_crop_sprite(self, crop_name, stage)` (Line 5691): Returns 16x16 sprite surface for specified crop and growth stage (0-3).
      - `def _generate_walls(self)` (Line 5705)
      - `def _generate_potato_player(self)` (Line 5737)
      - `def _generate_npcs(self)` (Line 5846)
      - `def _generate_boss_sprites(self)` (Line 6205)
      - `def _generate_mobs(self)` (Line 6526)
      - `def _generate_fish_mobs(self)` (Line 7094): Generates authentic 2D pixel-art fish mob sprites for all 10 Philippine fish species.
      - `def _generate_items(self)` (Line 7360)
      - `def _generate_branding(self)` (Line 7509)
      - `def _generate_ui(self)` (Line 7543)
      - `def _generate_environment(self)` (Line 7604)
      - `def _generate_cutscene_assets(self)` (Line 7625)
      - `def _generate_cutscene_portraits(self)` (Line 7634)
      - `def _generate_scene_1_frame(self, frame)` (Line 7834)
      - `def _generate_scene_2_frame(self, frame)` (Line 7964)
      - `def _generate_scene_3_frame(self, frame)` (Line 8074)
      - `def _generate_scene_4_frame(self, frame)` (Line 8184)
      - `def _generate_projectiles(self)` (Line 8311)
      - `def _generate_grand_animated_effects(self)` (Line 8431)
      - `def _generate_skill_icons(self)` (Line 8997): Procedurally generates 32x32 crisp RPG pixel art skill icons for all 10 skills
      - `def export_all_assets(self, target_dir, force)` (Line 9462)
- **Standalone Functions (6):**
  - `def _clamp(v, lo, hi)` (Line 49)
  - `def _adjust(c, factor)` (Line 53)
  - `def _blend(c1, c2, t)` (Line 57)
  - `def write_unique_assets_tracker(target_dir, tracker_path, gemini_model, image_model, gemini_mode)` (Line 9701): Scans all generated PNG assets in target_dir, verifies pixel/byte uniqueness,
  - `def generate_effects_with_gemini(api_key, target_dir)` (Line 9833): Gemini API integration hook for generating and enhancing grand skill/effect visual frames.
  - `def generate_assets_with_gemini(api_key, target_dir, tracker_path, max_live_images)` (Line 9894): End-to-end Gemini AI asset generation & bespoke pixel-art synthesis pipeline.

#### `src/assets/projectile_factory.py`
- **Size:** 37782 bytes | **Lines:** 883 lines
- **Description:** Potaria - Projectile Asset Factory (Crisp 32x32 2D Pixel Art)
- **Classes Defined (1):**
  - **`class ProjectileRegistry`** (Line 764) - Specialized dictionary for Potaria projectiles supporting canonical keys
    - Methods (12):
      - `def __init__(self)` (Line 771)
      - `def register_alias(self, alias, canonical_key)` (Line 775)
      - `def aliases(self)` (Line 779): Returns a copy of registered alias mappings.
      - `def _normalize_key(self, key)` (Line 783)
      - `def _resolve_canonical_key(self, key)` (Line 794)
      - `def get(self, key, default)` (Line 827)
      - `def __getitem__(self, key)` (Line 833)
      - `def __contains__(self, key)` (Line 839)
      - `def pop(self, key)` (Line 842)
      - `def __delitem__(self, key)` (Line 850)
      - `def setdefault(self, key, default)` (Line 857)
      - `def copy(self)` (Line 864)
- **Standalone Functions (41):**
  - `def _create_p01_iron_arrow()` (Line 13)
  - `def _create_p02_heavy_bolt()` (Line 39)
  - `def _create_p03_throwing_knife()` (Line 64)
  - `def _create_p04_spinning_shuriken()` (Line 90)
  - `def _create_p05_returning_throwing_axe()` (Line 108)
  - `def _create_p06_fireball()` (Line 128)
  - `def _create_p07_ice_shard()` (Line 148)
  - `def _create_p08_lightning_bolt()` (Line 162)
  - `def _create_p09_shadow_orb()` (Line 177)
  - `def _create_p10_poison_glob()` (Line 191)
  - `def _create_p11_holy_bolt()` (Line 211)
  - `def _create_p12_earth_shard()` (Line 226)
  - `def _create_p13_water_orb()` (Line 241)
  - `def _create_p14_magma_core()` (Line 257)
  - `def _create_p15_wind_crescent()` (Line 274)
  - `def _create_p16_arcane_orb()` (Line 287)
  - `def _create_p17_arcane_lance()` (Line 304)
  - `def _create_p18_energy_disc()` (Line 318)
  - `def _create_p19_homing_star()` (Line 333)
  - `def _create_p20_void_sphere()` (Line 352)
  - `def _create_p21_spectral_skull()` (Line 369)
  - `def _create_p22_crystal_bolt()` (Line 389)
  - `def _create_p23_fuse_bomb()` (Line 404)
  - `def _create_p24_spiked_blast_core()` (Line 423)
  - `def _create_p25_meteor_fragment()` (Line 445)
  - `def _create_p26_arcane_mine()` (Line 461)
  - `def _create_p27_frost_bomb()` (Line 477)
  - `def _create_p28_acid_glob()` (Line 498)
  - `def _create_p29_bolo_throw()` (Line 514)
  - `def _create_p30_araw_sigil()` (Line 534)
  - `def _create_p31_anting_anting_charm()` (Line 553)
  - `def _create_p32_diwa_wisp()` (Line 571)
  - `def _create_p33_sumpa_spear()` (Line 585)
  - `def _create_p34_ancestral_spirit_orb()` (Line 604)
  - `def _create_p35_kampilan_wave()` (Line 617)
  - `def _create_p36_monster_spit()` (Line 631)
  - `def _create_p37_curse_bolt()` (Line 646)
  - `def _create_p38_boss_core()` (Line 660)
  - `def _create_p39_tracking_shards()` (Line 681)
  - `def _create_p40_abyssal_seed()` (Line 698)
  - `def generate_library_projectiles()` (Line 870): Generates all 40 projectiles from the library specifications.

### Core Systems & Settings (`src/*`)

#### `src/camera.py`
- **Size:** 4186 bytes | **Lines:** 121 lines
- **Description:** Potaria - Smooth Tracking Camera (Infinite World)
- **Classes Defined (1):**
  - **`class Camera`** (Line 14)
    - Methods (11):
      - `def __init__(self, screen_width, screen_height)` (Line 15)
      - `def set_zoom(self, zoom_level)` (Line 35): Restricts zoom to exactly 3 discrete levels: 1.0 (1x), 2.0 (2x), and 3.0 (3x).
      - `def cycle_zoom(self)` (Line 60): Cycles zoom level: 1x -> 2x -> 3x -> 1x.
      - `def offset_x(self)` (Line 71)
      - `def offset_y(self)` (Line 75)
      - `def set_target(self, target_px_x, target_px_y, instant)` (Line 78)
      - `def add_shake(self, intensity, duration)` (Line 92)
      - `def update(self, dt)` (Line 98)
      - `def screen_to_world(self, sx, sy)` (Line 107)
      - `def world_to_screen(self, wx, wy)` (Line 112)
      - `def screen_to_tile(self, sx, sy)` (Line 119)

#### `src/constants.py`
- **Size:** 24505 bytes | **Lines:** 460 lines
- **Description:** Potaria - Constants and Game Definitions
- *Declarative definition module containing data constants, dictionaries, and configurations.*

#### `src/profiler.py`
- **Size:** 6785 bytes | **Lines:** 194 lines
- **Description:** Potaria - Lightweight Real-Time Performance Profiler & Frame-Time Telemetry
- **Classes Defined (2):**
  - **`class ProfilerSection`** (Line 10)
    - Methods (3):
      - `def __init__(self, name, profiler)` (Line 13)
      - `def __enter__(self)` (Line 17)
      - `def __exit__(self, exc_type, exc_val, exc_tb)` (Line 22)
  - **`class PotariaProfiler`** (Line 30)
    - Methods (9):
      - `def __init__(self, history_size)` (Line 31)
      - `def start_frame(self)` (Line 52)
      - `def end_frame(self)` (Line 58)
      - `def section(self, name)` (Line 70): Context manager for timing a named execution section.
      - `def start_section(self, name)` (Line 74): Explicit section start timer.
      - `def end_section(self, name)` (Line 79): Explicit section end timer.
      - `def _recalculate_stats(self)` (Line 87)
      - `def get_summary_line(self)` (Line 113): Returns single-line performance summary string.
      - `def render_overlay(self, screen, font, x, y)` (Line 120): Draws the detailed real-time profiler overlay on screen.

#### `src/settings_manager.py`
- **Size:** 8383 bytes | **Lines:** 245 lines
- **Description:** Potaria - Settings Manager & Configuration Lifecycle
- **Standalone Functions (6):**
  - `def load_settings(path)` (Line 65): Loads persistent user settings and key bindings from disk.
  - `def save_settings(settings, key_bindings, path)` (Line 141): Atomically persists user settings and key bindings to disk.
  - `def get_current_settings()` (Line 215): Returns the active in-memory settings dictionary (loads from disk if not yet loaded).
  - `def get_current_key_bindings()` (Line 223): Returns the active in-memory key bindings dictionary (loads from disk if not yet loaded).
  - `def update_setting(key, value, auto_save, path)` (Line 231): Updates a single setting in memory and optionally flushes to disk immediately.
  - `def _on_exit_save()` (Line 239): Atexit handler ensuring any modified settings are safely flushed to disk on shutdown.

---

## 4. Master Reference of Exact Numeric Values, Formulas & Physical Constants

### 4.1 Canonical Master Constants Reference (`src/constants.py`)

| Constant Identifier | Value | Unit / Scale | Architectural Purpose |
|:---|:---|:---|:---|
| `SCREEN_WIDTH` | `1280` | Pixels | Reference viewport width |
| `SCREEN_HEIGHT` | `720` | Pixels | Reference viewport height |
| `FPS` | `60` | Frames / Sec | Target frame cadence |
| `SCALE` | `2` | Integer Multiplier | 16x16 pixel sprites rendered at 32x32 |
| `TILE_SIZE` | `16` | Source Pixels | Unscaled tile sprite dimension |
| `SCALED_TILE` | `32` | Viewport Pixels | Scaled in-game tile grid cell dimension |
| `WORLD_WIDTH` | `450` | Tiles (Finite Mode) | Finite world width (Infinite mode ignores bound) |
| `WORLD_HEIGHT` | `240` | Tiles | Total world vertical depth (from Sky to Nether) |
| `SURFACE_LEVEL` | `70` | Tile Y Coordinate | Average surface terrain horizon |
| `UNDERGROUND_LEVEL` | `115` | Tile Y Coordinate | Transition from surface dirt to subterranean stone |
| `CAVERN_LEVEL` | `160` | Tile Y Coordinate | Deep caves, glowing mushroom grottos |
| `DUNGEON_LEVEL` | `205` | Tile Y Coordinate | Nether Dungeon, boss altars, and catacombs |
| `GRAVITY` | `0.44` | px / frame^2 | Gravitational acceleration impulse |
| `TERMINAL_VELOCITY`| `10.0` | px / frame | Maximum downward fall velocity clamp |
| `PLAYER_SPEED` | `3.0` | px / frame | Base horizontal movement speed |
| `PLAYER_ACCEL` | `0.35` | px / frame^2 | Running horizontal acceleration |
| `PLAYER_FRICTION` | `0.22` | px / frame^2 | Ground deceleration friction |
| `PLAYER_JUMP_FORCE`| `-8.0` | px / frame | Upward jump initial impulse |
| `PLAYER_DROP_THROUGH_TIME` | `15` | Ticks (0.25s) | Platform ignore collision duration |
| `PLAYER_WIDTH` | `28` | Pixels | Kinematic body collider width |
| `PLAYER_HEIGHT` | `32` | Pixels | Kinematic body collider height (1 tile high) |
| `PLAYER_SPRITE_WIDTH` | `28` | Pixels | Visual potato sprite width |
| `PLAYER_SPRITE_HEIGHT`| `36` | Pixels | Visual potato sprite height (includes sprout leaf) |
| `HOTBAR_SLOTS` | `10` | Slots | Number of active hotbar inventory slots |
| `INV_COLS` | `10` | Columns | Backpack inventory grid width |
| `INV_ROWS` | `4` | Rows | Backpack inventory grid height |
| `INV_TOTAL_SLOTS` | `40` | Slots | Total backpack storage capacity |
| `SLOT_SIZE` | `40` | Pixels | Inventory slot visual UI bounding box |
| `SLOT_PADDING` | `4` | Pixels | Padding between inventory grid slots |
| `MAX_LIGHT` | `15` | Discrete Units | Maximum cellular illumination intensity |
| `MIN_LIGHT` | `1` | Discrete Units | Minimum ambient light clamp |

#### Complete Tile Definitions & Hardness Registry (`TILE_PROPS`)

| Tile ID | Internal Name | Hardness | Tool Type | Drop Item | Solid | Platform | Light Emit | Absorb |
|:---|:---|:---|:---|:---|:---|:---|:---|:---|
| 0 | Air | 0 | None | None | No | No | 0 | 0 |
| 1 | Dirt | 15 | Shovel | dirt_block | Yes | No | 0 | 3 |
| 2 | Grass | 18 | Shovel | dirt_block | Yes | No | 0 | 3 |
| 3 | Stone | 35 | Pickaxe | stone_block | Yes | No | 0 | 4 |
| 4 | Oak Wood | 20 | Axe | wood | Yes | No | 0 | 3 |
| 5 | Oak Leaves | 5 | Bare Hand | leaves | No | No | 0 | 1 |
| 6 | Oak Wood Trunk | 20 | Axe | wood | No | No | 0 | 2 |
| 7 | Copper Ore | 40 | Pickaxe | copper_ore | Yes | No | 0 | 4 |
| 8 | Iron Ore | 45 | Pickaxe | iron_ore | Yes | No | 0 | 4 |
| 9 | Gold Ore | 55 | Pickaxe | gold_ore | Yes | No | 1 | 4 |
| 10 | Wood Platform | 10 | Axe | wood_platform | No | Yes | 0 | 0 |
| 11 | Work Bench | 25 | Axe | work_bench | No | Yes | 0 | 0 |
| 12 | Furnace | 40 | Pickaxe | furnace | No | No | 8 | 0 |
| 13 | Torch | 5 | Bare Hand | torch | No | No | 10 (r:6) | 0 |
| 14 | Stone Brick | 38 | Pickaxe | stone_brick | Yes | No | 0 | 4 |
| 15 | Bedrock | 9999 | Indestructible | None | Yes | No | 0 | 15 |
| 16 | Dungeon Brick | 9999 | Indestructible | None | Yes | No | 1 | 15 |
| 17 | Dungeon Altar | 9999 | Indestructible | None | No | Yes | 6 | 0 |
| 18 | Sand | 12 | Shovel | sand_block | Yes | No | 0 | 2 |
| 19 | Sandstone | 30 | Pickaxe | sandstone_block | Yes | No | 0 | 4 |
| 20 | Cactus | 15 | Axe | cactus | No | No | 0 | 1 |
| 21 | Snow | 10 | Shovel | snow_block | Yes | No | 0 | 2 |
| 22 | Ice | 22 | Pickaxe | ice_block | Yes | No | 0 | 2 |
| 23 | Blight Grass | 25 | Shovel | dirt_block | Yes | No | 1 | 4 |
| 24 | Blightstone | 50 | Pickaxe | blightstone_block | Yes | No | 0 | 5 |
| 25 | Mushroom Grass | 20 | Shovel | glowing_mushroom | Yes | No | 6 | 2 |
| 26 | Mushroom Stem | 15 | Axe | wood | No | No | 2 | 1 |
| 27 | Mushroom Cap | 12 | Bare Hand | glowing_mushroom | No | No | 9 | 0 |
| 28 | Treasure Chest | 30 | Axe | chest | No | Yes | 3 | 0 |
| 29 | Roof Tiles | 25 | Pickaxe | roof_tiles | Yes | No | 0 | 3 |
| 30 | Wood Planks | 20 | Axe | wood_planks | Yes | No | 0 | 3 |
| 31 | Glass Window | 10 | Pickaxe | glass_window | Yes | No | 0 | 0 |
| 32 | Wooden Door (Closed) | 20 | Axe | wooden_door | Yes | No | 0 | 1 |
| 33 | Wooden Door (Open) | 20 | Axe | wooden_door | No | No | 0 | 0 |
| 34 | Wooden Table | 20 | Axe | wooden_table | No | Yes | 0 | 0 |
| 35 | Wooden Chair | 15 | Axe | wooden_chair | No | No | 0 | 0 |
| 36 | Magical Barrier | 30 | Indestructible | None | Yes | No | 10 | 0 |
| 37 | Liquid Water | 9999 | Liquid Fluid | None | No | No | 0 | 2 |
| 38 | Wooden Bed | 20 | Axe | wooden_bed | No | Yes | 0 | 0 |
| 39 | Bookshelf | 20 | Axe | bookshelf | No | Yes | 0 | 0 |
| 40 | Grandfather Clock | 25 | Axe | grandfather_clock | No | No | 1 | 0 |
| 41 | Stone Fireplace | 35 | Pickaxe | stone_fireplace | No | Yes | 13 (r:11) | 0 |
| 42 | Candelabra | 10 | Bare Hand | candelabra | No | No | 12 (r:10) | 0 |
| 43 | Chandelier | 12 | Bare Hand | chandelier | No | No | 14 (r:14) | 0 |
| 44 | Potted Spud Plant | 10 | Bare Hand | potted_plant | No | No | 2 (r:3) | 0 |
| 45 | Wooden Dresser | 20 | Axe | wooden_dresser | No | Yes | 0 | 0 |
| 46 | Wall Tapestry | 8 | Bare Hand | wall_tapestry | No | No | 0 | 0 |
| 47 | Bathtub | 25 | Pickaxe | bathtub | No | Yes | 0 | 0 |
| 48 | Sink | 20 | Pickaxe | sink | No | Yes | 0 | 0 |
| 49 | Painting | 8 | Bare Hand | painting | No | No | 1 | 0 |
| 50 | Wood Shelf | 10 | Axe | wood_shelf | No | Yes | 0 | 0 |
| 51 | Carved Tuber Lantern | 8 | Bare Hand | carved_tuber_lantern | No | No | 14 (r:8) | 0 |
| 52 | Brass Lantern | 10 | Bare Hand | brass_lantern | No | No | 14 (r:8) | 0 |
| 53 | Spectral Lantern | 10 | Bare Hand | spectral_lantern | No | No | 14 (r:8) | 0 |
| 54 | Oak Sapling | 5 | Bare Hand | oak_sapling | No | No | 0 | 0 |
| 55 | Iron Storage Chest | 35 | Pickaxe | iron_chest | No | Yes | 0 | 0 |
| 56 | Rope Rungs | 10 | Bare Hand | rope_rungs | No | Yes | 0 | 0 |
| 57 | Magma Dungeon Brick | 9999 | Indestructible | None | Yes | No | 2 | 15 |
| 58 | Crypt Dungeon Brick | 9999 | Indestructible | None | Yes | No | 1 | 15 |
| 59 | Catacomb Bone Brick | 9999 | Indestructible | None | Yes | No | 1 | 15 |
| 60 | Dungeon Portcullis | 9999 | Indestructible | None | No | No | 1 | 0 |
| 61 | Brass Lamp | 10 | Bare Hand | brass_lamp | No | No | 14 (r:9) | 0 |
| 62 | Palm Sapling | 5 | Bare Hand | palm_sapling | No | No | 0 | 0 |
| 63 | Pine Sapling | 5 | Bare Hand | pine_sapling | No | No | 0 | 0 |
| 64 | Blight Sapling | 5 | Bare Hand | blight_sapling | No | No | 2 (r:3) | 0 |
| 65 | Pine Wood | 20 | Axe | pine_wood | Yes | No | 0 | 3 |
| 66 | Pine Leaves | 5 | Bare Hand | pine_leaves | No | No | 0 | 1 |
| 67 | Pine Wood Trunk | 20 | Axe | pine_wood | No | No | 0 | 2 |
| 68 | Palm Wood | 20 | Axe | palm_wood | Yes | No | 0 | 3 |
| 69 | Palm Leaves | 5 | Bare Hand | palm_leaves | No | No | 0 | 1 |
| 70 | Palm Wood Trunk | 20 | Axe | palm_wood | No | No | 0 | 2 |
| 71 | Blight Wood | 20 | Axe | blight_wood | Yes | No | 1 | 3 |
| 72 | Blight Leaves | 5 | Bare Hand | blight_leaves | No | No | 1 | 1 |
| 73 | Blight Wood Trunk | 20 | Axe | blight_wood | No | No | 1 | 2 |
| 74 | Dry Farmland Soil | 15 | Shovel | dirt_clod | Yes | No | 0 | 3 |
| 75 | Hydrated Farmland | 15 | Shovel | dirt_clod | Yes | No | 0 | 3 |
| 76 | Planted Crops (0-3) | 1 | Bare Hand | Dynamic Crops | No | No | 0 | 0 |
| 77 | Wild Spud Plant | 1 | Bare Hand | Dynamic Seeds | No | No | 0 | 0 |

---

### 4.2 Kinematic & Locomotion Tuning Constants

| Metric | Pygame-CE Value | Unity 6 LTS Equivalent | Physical Functionality |
|:---|:---|:---|:---|
| Horizontal Max Run Speed | `3.0` px / frame | `6.0` units / sec | Primary run velocity cap |
| Dash Burst Speed Multiplier | `2.2x` | `2.2x` (`13.2` units / sec) | Dash skill velocity impulse |
| Run Acceleration Rate | `0.35` px / frame^2 | `40.0` units / sec^2 | Horizontal speed ramp cadence |
| Run Deceleration Friction | `0.22` px / frame^2 | `32.0` units / sec^2 | Ground stopping deceleration |
| Upward Jump Force | `-8.0` px / frame | `12.0` units / sec | Initial upward leap impulse |
| Variable Jump Cut Multiplier | `0.50x` (early release) | `0.45x` upward truncation | Height control upon early button release |
| Coyote Time Window | N/A (strict ground) | `0.15` seconds (150ms) | Jump allowance after leaving ledge |
| Jump Buffer Window | N/A (strict down) | `0.12` seconds (120ms) | Pre-landing jump command queue |
| Jump Grace Timer | N/A | `0.08` seconds (80ms) | Slope adhesion bypass on liftoff |
| Platform Drop Duration | `15` ticks (0.25s) | `0.25` seconds (250ms) | Collision ignore duration on drop |
| Climb Upward Velocity | `-3.8` px / frame | `5.5` units / sec | Vertical climb speed on rope rungs |
| Climb Downward Velocity | `3.2` px / frame | `4.8` units / sec | Vertical descent speed on rope rungs |
| Ground Detection BoxCast | Rect intersection | `Vector2(0.85, 0.15)` | Downward cast depth 0.08 units |
| Ground Slope Tolerance | 0 deg (axis aligned) | `45.0` degrees | Maximum walkable slope normal angle |
| Potato Collider Box | `28 x 32` pixels | `0.875 x 1.000` units | Kinematic interaction bounding box |
| Potato Sprite Visual Box | `28 x 36` pixels | `0.875 x 1.125` units | Full visual sprite dimension |
| Head Sprout Offset | `4` pixels | `0.125` units | Decorative non-colliding head sprout |

---

### 4.3 Fluid Mechanics & Oxygen Depletion Formula

| Parameter | Exact Value | Mechanical Consequence |
|:---|:---|:---|
| Water Horizontal Drag Multiplier | `0.88x` per tick | Fluid resistance retarding horizontal speed |
| Water Vertical Drag Multiplier | `0.90x` per tick | Fluid resistance retarding vertical speed |
| Water Gravity Factor | `0.25x` normal gravity | Buoyancy dampening downward fall acceleration |
| Maximum Oxygen Capacity | `100.0` units | Total breath reserve pool |
| Oxygen Depletion Rate | `7.5` units / second | Total submerged breath time = `13.33` seconds |
| Oxygen Surface Replenish Rate | `40.0` units / second | Full replenishment upon surfacing = `2.50` seconds |
| Drowning Tick Interval | `1.0` second | Time between consecutive drowning damage hits |
| Drowning Damage Formula | `max(1, max_hp // 10)` | Exactly 10% of Max HP (1 Heart) true damage per second |
| Drowning Armor Penetration | `100%` (True Damage) | Ignores DEF, armor mitigation, and meal resistances |

---

### 4.4 Combat & Damage Calculation Formulas

#### 1. Attack Cooldown & Swing Duration
- Base Swing Duration: `swing_duration = max(0.10, min(attack_cooldown, 0.45))` seconds.
- Attack Speed Meal Reduction: `cooldown = cooldown / (1.0 + atk_speed_mult)`. Minimum attack cooldown is clamped at `0.08` seconds.

#### 2. Physical & Defense Damage Mitigation
$$\text{Effective DEF} = \text{Base DEF} + \text{Bonus DEF} + \text{Meal DEF}$$
If Titan's Resolve is active (HP $< 30\%$):
$$\text{Effective DEF} = \text{Effective DEF} \times 3$$
The minimum piercing damage is capped at 15%:
$$\text{Min Pierce} = \begin{cases} 1 & \text{if Titan's Resolve is active} \\ \max(1, \lceil \text{Raw Damage} \times 0.15 \rceil) & \text{otherwise} \end{cases}$$
The net damage taken is:
$$\text{Mitigated Damage} = \max(\text{Min Pierce}, \text{Raw Damage} - \text{Effective DEF})$$
Passive Damage Reductions applied multiplicatively:
- If 15% Mitigation active: $\text{Mitigated Damage} = \max(\text{Min Pierce}, \lfloor \text{Mitigated Damage} \times 0.85 \rfloor)$.
- If 25% Mitigation active: $\text{Mitigated Damage} = \max(\text{Min Pierce}, \lfloor \text{Mitigated Damage} \times 0.75 \rfloor)$.
- Food Damage Reduction: $\text{Mitigated Damage} = \max(\text{Min Pierce}, \lfloor \text{Mitigated Damage} \times (1.0 - \text{dmg\_reduction}) \rfloor)$.

#### 3. Critical Strike Mechanics
$$\text{Total Crit Rate} = \min(75.0\%, \text{Base Crit} + \text{Bonus Crit} + \text{Meal Crit})$$
$$\text{Crit Damage Multiplier} = 1.80\times \text{ (180\% Total Damage)}$$

---

### 4.5 100-Level RPG Progression & EXP Formulas

#### Level-Up EXP Curve Formula
$$\text{EXP\_To\_Next}(\text{level}) = \left\lfloor 100 \times \left( \text{level}^{2.1} \right) \right\rfloor$$

#### Sample Level Milestones

| Level | EXP Required for Level | Cumulative Total EXP | Base HP | Base MP | Base ATK | Base DEF | Base Crit |
|:---|:---|:---|:---|:---|:---|:---|:---|
| 1 | 100 | 0 | 100 | 50 | 10 | 2 | 5.0% |
| 5 | 2,933 | 6,340 | 160 | 82 | 22 | 6 | 6.0% |
| 10 | 12,589 | 43,120 | 235 | 122 | 37 | 11 | 7.0% |
| 20 | 54,083 | 321,800 | 385 | 202 | 67 | 21 | 9.0% |
| 50 | 377,414 | 4,215,600 | 835 | 442 | 157 | 51 | 15.0% |
| 100 | 1,584,893 | 32,840,000 | 1,585 | 842 | 307 | 101 | 25.0% |

#### Currency Denomination Auto-Breakdown
$$\text{Total Copper} = \text{Copper} + (\text{Silver} \times 100) + (\text{Gold} \times 10,000)$$
$$\text{Gold Coins} = \lfloor \text{Total Copper} / 10,000 \rfloor$$
$$\text{Silver Coins} = \lfloor (\text{Total Copper} \% 10,000) / 100 \rfloor$$
$$\text{Copper Coins} = \text{Total Copper} \% 100$$

---

### 4.6 Statutory Meal Buff Contribution Caps (`MEAL_BUFF_CAPS`)

| Stat Parameter Name | Hard Cap Limit | Type | Rationale & Balance Boundary |
|:---|:---|:---|:---|
| `damage_mult` | `+12.0%` (`0.12`) | Multiplier | Limits global melee/physical scaling |
| `ranged_damage_mult` | `+12.0%` (`0.12`) | Multiplier | Limits ballistic archery / projectile scaling |
| `atk_speed_mult` | `+10.0%` (`0.10`) | Multiplier | Preserves animation stability and frame cadence |
| `crit_chance` | `+6.0%` (`0.06`) | Additive % | Prevents exceeding 75% hard crit cap |
| `crit_dmg_mult` | `+16.0%` (`0.16`) | Multiplier | Prevents extreme burst spikes on bosses |
| `armor_pen` | `+10.0%` (`0.10`) | Multiplier | Limits true damage bypassing defense curves |
| `def` | `+6` | Flat Integer | Equivalent to 2-3 armor pieces |
| `dmg_reduction` | `+6.0%` (`0.06`) | Multiplier | Prevents invulnerability stacking |
| `magic_res` | `+15.0%` (`0.15`) | Multiplier | Protects against bullet-hell elemental spikes |
| `speed_mult` | `+15.0%` (`0.15`) | Multiplier | Prevents camera tearing and physics tunneling |
| `jump_mult` | `+15.0%` (`0.15`) | Multiplier | Limits maximum vertical leap clearance |
| `dash_mult` | `+15.0%` (`0.15`) | Multiplier | Bounds dodge distance |
| `knockback_res` | `+15.0%` (`0.15`) | Multiplier | Prevents total knockback immunity from food |
| `hp_regen` | `+2.0` HP / sec | Additive Float| Out-of-combat sustain limit |
| `mp_regen` | `+2.0` MP / sec | Additive Float| Sustained combat spellcasting limit |
| `mana_cost_reduction` | `+15.0%` (`0.15`) | Multiplier | Prevents infinite skill spam |
| `luck` | `+10.0%` (`0.10`) | Multiplier | Modifies drop weights for rare loot |
| `gathering_speed` | `+20.0%` (`0.20`) | Multiplier | Boosts mining / chopping tick speed |
| `fishing_power` | `+15.0%` (`0.15`) | Multiplier | Increases bite rate and reel tension leniency |

---

### 4.7 7-Tier Rarity Engine Tables & Affix Budgets

| Rarity Tier | Rank | Hex Color Code | Affix Budget | Stat Multiplier | Drop Weight | Unique Effect Allowed |
|:---|:---|:---|:---|:---|:---|:---|
| Common | 0 | `#9E9E9E` (Grey) | 0 | 1.00x | 55.00% | No |
| Uncommon | 1 | `#4CAF50` (Green) | 1 | 1.10x | 25.00% | No |
| Rare | 2 | `#2196F3` (Blue) | 2 | 1.25x | 12.00% | No |
| Epic | 3 | `#9C27B0` (Purple) | 3 | 1.50x | 5.00% | No |
| Mythic | 4 | `#FF9800` (Orange) | 4 | 2.00x | 2.00% | Yes |
| Legendary | 5 | `#FFD700` (Gold) | 5 | 2.50x | 0.85% | Yes |
| Ancient | 6 | `#00F0E6` (Cyan/Crimson)| 6 | 3.00x | 0.15% | Yes |

---

### 4.8 Item Enhancement (+1 to +7) Requirements, Success Curves & Break Risks

| Target Level | Copper Cost | Material Requirements | Success Rate | Break Risk Rate | Stat Multiplier |
|:---|:---|:---|:---|:---|:---|
| +1 | 20 Copper | 2x Copper Bar | 100% | 0% (Safe) | 1.14x (+14%) |
| +2 | 50 Copper | 2x Iron Bar | 90% | 0% (Safe) | 1.28x (+28%) |
| +3 | 100 Copper | 3x Iron Bar, 1x Gold Bar | 80% | 0% (Safe) | 1.43x (+43%) |
| +4 | 200 Copper | 3x Gold Bar, 2x Spud Sap | 70% | 0% (Safe) | 1.57x (+57%) |
| +5 | 500 Copper | 5x Gold Bar, 3x Blightstone | 50% | 20% (Break Risk) | 1.71x (+71%) |
| +6 | 1,000 Copper | 8x Gold Bar, 1x Portal Shard, 5x Blightstone | 40% | 25% (Break Risk) | 1.86x (+86%) |
| +7 | 2,500 Copper | 10x Gold Bar, 2x Portal Shard, 5x Spud Sap | 30% | 30% (Break Risk) | 2.00x (Double Stats)|

- **Repair Fee**: Broken items can be restored to working status at any nomadic trader for a flat fee of **1 Gold Coin (10,000 Copper)**.

---

### 4.9 Maximum Additional Affix Slots (`MAX_ADDITIONAL_AFFIX_SLOTS`)

| Item Rarity Tier | Maximum Additional Affix Slots Permitted | Affix Stone Requirement |
|:---|:---|:---|
| Common | 0 | Not Permitted |
| Uncommon | 0 | Not Permitted |
| Rare | 0 | Not Permitted |
| Epic | 1 | 1x Affix Stone |
| Legendary | 1 | 1x Affix Stone |
| Mythic | 2 | 2x Affix Stone |
| Ancient | 2 | 2x Affix Stone |

---

### 4.10 Complete 27 Equipment Sets Reference Table

| Set Identifier | Display Set Name | Theme / Classification | 2-Piece Passive Milestone | 4-Piece Passive Milestone | 5-Piece / Full Set Aura Milestone |
|:---|:---|:---|:---|:---|:---|
| `ancient` | Ancient Relic Regalia | Endgame Titan | +20% Skill Damage | +15 DEF, +50 HP | Golden Radiant Aura, Double Celestial Reversal Budget |
| `titan` | Titan Colossus Battlegear | Subterranean Obsidian | +10 DEF, +40 HP | Knockback Immunity | Obsidian Stomp Nova on landing from heights |
| `magma` | Nether Magma Forged Plate | Fire / Lava Nether | +15 Fire ATK | Burn Immunity | Searing Lava Trail igniting struck enemies |
| `cryo` | Permafrost Crypt Armor | Ice / Glacier Frost | +15 Frost ATK | Freeze Immunity | Glacial Blizzard Aura slowing nearby enemies 40% |
| `shadow` | Abyssal Shadow Robes | Void / Evasion | +15% Move Speed | 15% Evasion Step | Abyssal Void Aura, Phasing Dash |
| `spud` | Spud Pioneer Overalls | Starter Agriculture | +10 HP, +5% Speed | +20% Farming Speed | Leaf Sprout Aura, Daily Crop Doubling Chance |
| `cactus` | Desert Spined Carapace | Thorns / Defense | +5 DEF | 20% Thorns Return | Spiked Sand Aura reflecting 35% damage to attackers |
| `sin_pride` | Lucifer's Pride | 7 Deadly Sins | +25% Melee ATK | +15% Crit Rate | Blinding Solar Flare blinding surrounding mobs |
| `sin_greed` | Mammon's Greed | 7 Deadly Sins | +25% Coin Drops | +50% Coin Drops | Golden Midas Aura, Coins burst on critical hit |
| `sin_lust` | Asmodeus's Lust | 7 Deadly Sins | +8% Lifesteal | Charm on Hit | Alluring Rose Aura, Stun attacker on contact |
| `sin_envy` | Leviathan's Envy | 7 Deadly Sins | +10% Magic ATK | Mimics Target Buff | Aquatic Viper Aura, Steals 1 positive mob buff |
| `sin_gluttony` | Beelzebub's Gluttony | 7 Deadly Sins | +50% Food Buff Duration | +25% Food Buff Stats | Feast Aura, Allows 6 concurrent food buffs |
| `sin_wrath` | Satan's Wrath | 7 Deadly Sins | +30% ATK under 50% HP | +50% Attack Speed | Blood Red Berserk Aura, Explosive melee cleave |
| `sin_sloth` | Belphegor's Sloth | 7 Deadly Sins | +30 DEF while still | +5 HP/s while still | Iron Shell Aura, Reflects all projectiles while still |
| `virtue_humility`| Robes of Humility | 7 Heavenly Virtues | +15 DEF, -10% Aggro | +30 Max MP | Pure White Sanctuary Aura, +20% Party Defense |
| `virtue_charity` | Vestments of Charity | 7 Heavenly Virtues | +15% Potion Potency | Share heals with party | Golden Halo Aura, Healing pulses radiate to allies |
| `virtue_chastity`| Mail of Chastity | 7 Heavenly Virtues | +20 Magic Resist | Debuff Immunity | Pristine Silver Aura, Purges negative status effects |
| `virtue_gratitude`| Mantle of Gratitude | 7 Heavenly Virtues | +10% EXP Gain | +25% EXP Gain | Amber Sunburst Aura, Awards bonus EXP on boss kill |
| `virtue_temperance`| Garb of Temperance | 7 Heavenly Virtues | -15% Skill MP Cost | -25% Skill MP Cost | Tranquil Water Aura, Skill cooldowns recover 20% faster|
| `virtue_kindness`| Silks of Kindness | 7 Heavenly Virtues | +2 MP/s Regeneration | Revive ally at full HP | Emerald Leaf Aura, Revives player with 50% HP on death |
| `virtue_diligence`| Harness of Diligence | 7 Heavenly Virtues | +25% Mining Speed | Double Ore Yield | Sparks of Industry Aura, Mining strikes damage enemies |
| `virtue_patience`| Plate of Patience | 7 Heavenly Virtues | +1% ATK per second still| +50% Damage after 5s | Steadfast Mountain Aura, Immense single-strike release |
| `katipunero` | Katipunero Vanguard | Philippine History | +20% Bolo / Spear ATK| +15% Sprint Speed | Bayani Crimson Flag Aura, +30% Damage vs Bosses |
| `diwata_bloom` | Diwata's Blessing | Philippine Myth | +25 Max MP, +2 HP/s | Flower trail heal | Radiant Sampaguita Aura, Blinds corrupted creatures |
| `bakunawa_eclipse`| Bakunawa Serpent Scalemail| Philippine Myth | +20% Night Damage | Lunar Eclipse Crit +25%| Celestial Dragon Shadow Aura, Night immunity |
| `sarimanok_regalia`| Sarimanok Feathered Cloak| Philippine Myth | +15% All Elemental ATK| Tri-elemental projectile| Mythic Rainbow Plumage Aura, Quadruple jump wings |
| `tikbalang_trailblazer`| Tikbalang Mountain Hide| Philippine Myth | +35% Mountain Speed | Double Jump Impulse | Phantom Horse Hoofprint Aura, Disorients tracking mobs |

---

### 4.11 Complete 40 Action Combat Skills Roster

| Skill ID | Skill Name | Evolved Skill Name | Hotkey | MP Cost | Cooldown | Dmg Multiplier | Archetype / Description |
|:---|:---|:---|:---|:---|:---|:---|:---|
| `power_slash` | Power Slash | Cataclysmic Cleave | Q | 8 MP | 2.0s | 1.6x (160%) | Forward sword cleave slashing direction of cursor |
| `whirlwind` | Whirlwind | Tempest Cyclone | F | 10 MP | 3.0s | 1.3x (130%) | 360-degree spin striking all surrounding foes |
| `dash` | Swift Dash | Phantom Dash | V | 5 MP | 1.5s | 0.0x (Dodge) | Rapid forward dash granting 0.3s invulnerability |
| `fireball` | Fireball | Inferno Blast | R | 8 MP | 2.2s | 1.8x (180%) | Blazing fire orb detonating with area splash |
| `earth_slam` | Earth Slam | Tectonic Rupture | E | 14 MP | 4.0s | 2.2x (220%) | Ground slam producing a shattering seismic wave |
| `shield_bash` | Shield Bash | Aegis Bulwark | B | 12 MP | 3.0s | 1.5x (150%) | Forward dash with guard up, stunning enemies |
| `meteor` | Meteor Strike | Grand Starfall | G | 40 MP | 12.0s | 4.5x (450%) | [Legendary] Plunging flaming meteor from the sky |
| `frost_nova` | Frost Nova | Glacial Blizzard | X | 12 MP | 3.5s | 1.6x (160%) | Freezing radial wave chilling and slowing enemies |
| `celestial_shield`| Celestial Shield | Divine Sanctuary | Z | 36 MP | 14.0s | 2.0x (200%) | [Legendary] Absorbs 100% damage and reflects projectiles|
| `void_singularity`| Void Singularity | Event Horizon | T | 45 MP | 16.0s | 3.8x (380%) | [Legendary] Gravitational black hole pulling enemies in |
| `celestial_reversal`| Celestial Reversal | Araw Sigil Reversal | Z | 25 MP | 8.0s | 1.5x (150%) | [Ancient] Reflects enemy danmaku with 1.5x damage |
| `shuriken_storm` | Shuriken Storm | Shinobi Hurricane | Q | 10 MP | 2.5s | 1.4x (140%) | Throws 5 piercing shurikens in an expanding cone |
| `star_seeker` | Star Seeker | Astral Constellation | R | 12 MP | 3.0s | 1.7x (170%) | Homing astral stars tracking nearest enemy |
| `arcane_barrage` | Arcane Barrage | Mystic Annihilation | R | 15 MP | 3.2s | 2.0x (200%) | Rapid volley of 8 high-velocity magic bolts |
| `venom_volley` | Venom Volley | Toxic Deluge | F | 11 MP | 2.8s | 1.3x (130%) | Throws 3 poisonous globs leaving corrosive acid pools |
| `void_implosion` | Void Implosion | Abyssal Collapse | G | 32 MP | 10.0s | 3.2x (320%) | Compresses dark energy, imploding after 1.5 seconds |
| `crystal_shatter`| Crystal Shatter | Prismatic Shrapnel | E | 14 MP | 3.8s | 1.9x (190%) | Fires an amethyst crystal that splinters into 8 shards |
| `chain_discharge`| Chain Discharge | Lightning Overload | F | 16 MP | 4.2s | 2.1x (210%) | Arcs electricity between up to 5 adjacent targets |
| `meteor_shower` | Meteor Shower | Astral Rain | G | 42 MP | 13.0s | 3.5x (350%) | Cascades 6 smaller meteors over an extended area |
| `piercing_blizzard`| Piercing Blizzard | Absolute Permafrost | X | 18 MP | 4.5s | 2.0x (200%) | Linear piercing frost beam freezing everything in line |
| `solar_detonation`| Solar Detonation | Supernova Flare | T | 38 MP | 12.0s | 4.0x (400%) | Blinding solar orb exploding after 2.0s delay |
| `arcane_minefield`| Arcane Minefield | Rune Catastrophe | B | 20 MP | 6.0s | 2.4x (240%) | Deploys 4 hovering arcane mines detonating on contact |
| `frost_bomb` | Frost Bomb | Cryo Cataclysm | X | 14 MP | 3.5s | 1.7x (170%) | Lobs an icy bomb shattering into freezing mist |
| `ember_cluster` | Ember Cluster | Pyre Cascade | R | 12 MP | 3.0s | 1.6x (160%) | Fires 4 bouncing fire embers rolling across ground |
| `spectral_pursuit`| Spectral Pursuit | Soul Phantasm | T | 22 MP | 5.5s | 2.3x (230%) | Releases 2 phantoms phasing through solid blocks |
| `returning_hatchet`| Returning Hatchet | Boomerang Cleaver | Q | 9 MP | 2.2s | 1.5x (150%) | Throws spinning hatchet that boomerangs back to player |
| `bolo_cyclone` | Bolo Cyclone | Katipunan Whirler | F | 12 MP | 3.2s | 1.7x (170%) | [Philippine] Flurry of twin bolo blades with bleed DOT |
| `ancestral_guidance`| Ancestral Guidance | Anito's Blessing | B | 24 MP | 10.0s | 0.0x (Buff) | [Philippine] Summons ancestral spirits granting +30% ATK|
| `sumpang_sibat` | Sumpang Sibat | Cursed Bamboo Spear | E | 16 MP | 3.8s | 2.5x (250%) | [Philippine] Hurls enchanted spear impaling targets |
| `magma_eruption` | Magma Eruption | Caldera Vent | G | 35 MP | 11.0s | 3.6x (360%) | Erupts magma geysers from the ground beneath enemies |
| `heavy_cleave` | Heavy Cleave | Titan Sunder | Q | 12 MP | 2.8s | 2.0x (200%) | Overhead executioner swing shattering armor |
| `lunge_thrust` | Lunge Thrust | Rapier Pinpoint | Q | 7 MP | 1.8s | 1.4x (140%) | Precision forward thrust with +25% critical rate |
| `rebound_shield` | Rebound Shield | Kinetic Aegis | B | 14 MP | 4.0s | 1.6x (160%) | Throws shield bouncing between 3 targets before returning|
| `shadow_step` | Shadow Step | Abyssal Teleport | V | 10 MP | 2.5s | 0.0x (Utility) | Blinks 6 blocks toward cursor through solid blocks |
| `holy_smite` | Holy Smite | Dawn Ray | R | 18 MP | 4.0s | 2.3x (230%) | Calls down a vertical celestial pillar from above |
| `poison_dart` | Poison Dart | Viper's Needle | Q | 6 MP | 1.5s | 1.2x (120%) | Rapid blowgun dart applying stacking poison DOT |
| `ice_barrier` | Ice Barrier | Glacial Bulwark | B | 20 MP | 8.0s | 0.0x (Shield) | Forms ice shield absorbing 60 damage for 10 seconds |
| `blood_rage` | Blood Rage | Berserker's Oath | B | 0 HP (20 HP) | 12.0s | 0.0x (Buff) | Sacrifices 20 HP to gain +40% ATK and +30% Move Speed |
| `wind_cutter` | Wind Cutter | Gale Slice | Q | 8 MP | 2.0s | 1.5x (150%) | Launches horizontal slicing sonic air crescent |
| `grand_cross` | Grand Celestial Cross| Zenith Nova | G | 50 MP | 15.0s | 5.0x (500%) | [Grand Legendary] Cross-shaped celestial blast clearing screen |

---

### 4.12 10 Native Philippine Aquatic Species Tuning Table

| Fish Item ID | Display Fish Name | Rarity Tier | Target Clicks Required | Thrash Frequency Rate | Base Selling Value |
|:---|:---|:---|:---|:---|:---|
| `raw_dilis` | Philippine Dilis | Common | 7 Clicks | 0.25 (Low) | 2 Copper |
| `raw_tilapia` | Freshwater Tilapia | Common | 8 Clicks | 0.30 (Low) | 5 Copper |
| `raw_bangus` | National Milkfish (Bangus) | Uncommon | 11 Clicks | 0.35 (Moderate) | 15 Copper |
| `raw_galunggong` | Round Scad (Galunggong) | Uncommon | 12 Clicks | 0.35 (Moderate) | 18 Copper |
| `raw_hito` | Freshwater Catfish (Hito) | Uncommon | 13 Clicks | 0.40 (Moderate) | 22 Copper |
| `raw_maya_maya` | Red Snapper (Maya-Maya) | Rare | 18 Clicks | 0.45 (High) | 60 Copper |
| `raw_tambakol` | Yellowfin Tuna (Tambakol) | Rare | 20 Clicks | 0.50 (High) | 85 Copper |
| `raw_tanigue` | Spanish Mackerel (Tanigue) | Epic | 25 Clicks | 0.55 (Intense) | 250 Copper (2s 50c) |
| `raw_dalagang_bukid`| Yellowtail Fusilier | Epic | 26 Clicks | 0.55 (Intense) | 280 Copper (2s 80c) |
| `raw_lapu_lapu` | Spotted Grouper (Lapu-Lapu) | Epic | 28 Clicks | 0.60 (Intense) | 350 Copper (3s 50c) |

---

### 4.13 8 Native Philippine Crops Agricultural Table

| Crop Identifier | Common Name | Local Tagalog Name | Growth Stages | Light Requirement | Moisture Radius | Harvest Yield |
|:---|:---|:---|:---|:---|:---|:---|
| `crop_palay` | Rice Grain | Palay / Bigas | 4 (Stages 0-3) | Sun or Torchlight | 4 Blocks from Water | 3-5 Palay Grain, 1-2 Seed |
| `crop_bawang` | Native Garlic | Bawang | 4 (Stages 0-3) | Sun or Torchlight | 4 Blocks from Water | 2-4 Garlic Cloves, 1 Seed |
| `crop_sibuyas` | Red Onion | Sibuyas | 4 (Stages 0-3) | Sun or Torchlight | 4 Blocks from Water | 2-4 Red Onions, 1 Seed |
| `crop_luya` | Wild Ginger | Luya | 4 (Stages 0-3) | Sun or Torchlight | 4 Blocks from Water | 2-3 Ginger Roots, 1 Seed |
| `crop_talong` | Long Purple Eggplant| Talong | 4 (Stages 0-3) | Sun or Torchlight | 4 Blocks from Water | 2-4 Eggplants, 1 Seed |
| `crop_sitaw` | Yardlong String Beans| Sitaw | 4 (Stages 0-3) | Sun or Torchlight | 4 Blocks from Water | 3-5 String Beans, 1 Seed |
| `crop_sampalok` | Sour Tamarind Pods | Sampalok | 4 (Stages 0-3) | Sun or Torchlight | 4 Blocks from Water | 2-4 Tamarind Pods, 1 Seed |
| `crop_calamansi` | Philippine Lime | Calamansi | 4 (Stages 0-3) | Sun or Torchlight | 4 Blocks from Water | 3-6 Calamansi Fruits, 1 Seed|

---

## 5. HUD & UI Layout Specifications, Rendering Logic & Algorithms

### 5.1 Viewport Coordinates & Anchor Offsets

The reference UI viewport is fixed to **1280 x 720** pixels. Responsive canvas scalers adjust coordinates dynamically on mobile and ultrawide monitors while maintaining the core aspect ratio.

```
+--------------------------------------------------------------------------------------------------+ (0,0)
| [HOTBAR SLOTS 1 - 10]                                    [LIFE HEARTS & HP] [MANA BAR] [CLOCK]    |
| (10, 10) -> (446, 50)                                    (850, 10) -> (1270, 60)                  |
|                                                                                                  |
| [F3 PROFILER OVERLAY]                                                                            |
| (10, 70) -> (240, 260)                                                                           |
|                                                                                                  |
|                                         (SCREEN CENTER)                                          |
|                                            (640, 360)                                            |
|                                                                                                  |
|                                                                                                  |
| [MEAL BUFF TRAY: 5 SLOTS]                                              [SKILL BADGES: Q, F, V, R]|
| (10, 640) -> (260, 700)                                                (480, 650) -> (800, 705)  |
+--------------------------------------------------------------------------------------------------+ (1280, 720)
```

---

### 5.2 10-Slot Hotbar Visual & Functional Specification

- **Anchor & Sizing**:
  - Root position: `X = 10`, `Y = 10`.
  - Individual Slot Dimension: `40 x 40` pixels.
  - Padding Between Slots: `4` pixels.
  - Total Hotbar Width: $10 \times 40 + 9 \times 4 = 436$ pixels. Total Height: `40` pixels.
- **Visual Elements per Slot**:
  - Background Plate: Dark slate rectangle `(35, 40, 58, 220)` with 1px border `(85, 95, 130)`.
  - Number Badge: Displayed at top-left `(slot_x + 3, slot_y + 2)` in bold gold font showing numbers `1` through `9`, and `0` for the 10th slot.
  - Centered Item Icon: Scaled to `32 x 32` pixels centered at `(slot_x + 4, slot_y + 4)`.
  - Stack Count Label: Rendered at bottom-right `(slot_x + 36, slot_y + 26)` in compact white text with 1px black outline shadow. Suppressed if count $\le 1$.
  - Selection Highlight: Active gold border frame `(255, 215, 0)` with thickness of 2 pixels rendered at `(selected_slot * 44 + 8, 8)` with size `44 x 44`.
- **Keyboard & Gamepad Navigation**:
  - Number Keys 1-9 and 0 select slots 0 through 9 directly.
  - Mouse Scroll Wheel cycles active slot: `selected_slot = (selected_slot + scroll_delta) % 10`.
  - Gamepad Bumpers (LB / RB) cycle left and right across the hotbar.

---

### 5.3 Life Hearts & Mana Star Render Pipelines

- **Life Hearts Layout (Top-Right)**:
  - Text Header: `Life: {current_hp} / {max_hp} Lv.{level}` rendered in bold white text at `(SCREEN_WIDTH - 240, 10)`.
  - 10 Heart Icons: Displayed horizontally below the text header from right to left:
    - Each heart represents $10\%$ of Max HP (20 HP per heart on 200 Max HP base).
    - Full Heart: Radiant crimson heart sprite.
    - Half Heart: Split crimson/grey sprite if current HP is within $[\text{slot}\times 20 - 10, \text{slot}\times 20)$.
    - Empty Heart: Dark grey hollow heart outline.
- **Mana Bar & Readout**:
  - Positioned at `(SCREEN_WIDTH - 240, 36)`.
  - Text Label: `MP: {current_mp} / {max_mp}` rendered in azure text `(100, 180, 255)`.
  - Azure Mana Meter: Progress bar width = $180$ pixels, height = $8$ pixels.
  - Star Insignia: A 5-point glowing astral star icon anchored to the left of the bar.
- **12-Hour Celestial Clock & Radar Badge**:
  - Positioned at `(SCREEN_WIDTH - 110, 54)`.
  - Format: `{Hours}:{Minutes:02d} {AM/PM} {DAY/NIGHT}` (e.g. `12:00 PM DAY`, `7:04 PM NIGHT`).
  - Radar Key: Small square button labeled `[M]` indicating toggle state of subterranean mini-map radar.

---

### 5.4 Active Meal Buff Tray & Countdown Timers

- **Bottom-Left Layout**:
  - Position: `X = 10`, `Y = SCREEN_HEIGHT - 60` (Y = 660).
  - 5 Dedicated Category Slots spaced horizontally:
    1. Slot 1: Offense (Sword icon badge).
    2. Slot 2: Defense (Shield icon badge).
    3. Slot 3: Mobility (Winged boot icon badge).
    4. Slot 4: Resource / Regen (Flask / Potion icon badge).
    5. Slot 5: Utility / Luck (Four-leaf clover icon badge).
- **Slot Visuals & Countdown Ring**:
  - Background slot size: `36 x 36` pixels with category tint.
  - Centered Food Icon: 24x24 pixel sprite of the active Filipino dish.
  - Radial Countdown Fill: Translucent black radial sweep indicating percentage remaining (`duration / max_duration`).
  - Duration Badge: Time remaining formatted as `3m` or `45s` at slot bottom.
  - Tooltip: Hovering over any active buff slot displays dish name, meal category, duration remaining, and full stat breakdown.

---

### 5.5 Side-by-Side Equipment Comparison ('Katabi') Layout Algorithm

When the player hovers an equippable item in backpack or chest storage while the Character Information panel is open ('C' key), the tooltip engine triggers side-by-side comparison mode ('katabi'):

```
Candidate Item Tooltip Box                  Currently Equipped Tooltip Box
+------------------------------------+      +------------------------------------+
| Dragon Katana                      |      | [ CURRENTLY EQUIPPED ]             |
| [EPIC WEAPON]                      |      | Steel Broadsword                   |
| Weapon Power: 38 Damage (+10 ATK)  | <--> | [RARE WEAPON]                      |
| Use Speed: Fast Speed (0.26s)      |      | Weapon Power: 28 Damage            |
| Enhanced: +3                       |      | Use Speed: Fast Speed (0.32s)      |
| Affix: (O) Empty Socket            |      | Enhanced: +1                       |
| Lore: "Forged in the caldera..."   |      | Lore: "Standard infantry blade."   |
+------------------------------------+      +------------------------------------+
  Width: tw1                                  Width: tw2
  <---------------- total_w = tw1 + 12px + tw2 ---------------->
```

#### Placement Math & Screen Clamping:
1. Candidate tooltip width $tw_1$ and height $th_1$ measured from text lines.
2. Equipped tooltip width $tw_2$ and height $th_2$ measured from text lines.
3. Total width: $W_{\text{total}} = tw_1 + 12 + tw_2$. Total height: $H_{\text{total}} = \max(th_1, th_2)$.
4. Horizontal Placement:
   - Default: `tx1 = mouse_x + 16`.
   - Right overflow check: If `tx1 + W_total > SCREEN_WIDTH - 10`:
     - Try placing to left of cursor: `tx1 = mouse_x - 16 - W_total`.
     - If left side also overflows: clamp to screen edge: `tx1 = max(10, SCREEN_WIDTH - W_total - 10)`.
   - Equipped card position: `tx2 = tx1 + tw1 + 12`.
5. Vertical Placement:
   - Default: `ty = mouse_y + 16`.
   - Bottom overflow check: If `ty + H_total > SCREEN_HEIGHT - 10`:
     - Try placing above cursor: `ty = max(10, mouse_y - H_total - 8)`.
     - Clamped minimum: `ty = max(10, ty)`.

---

### 5.6 Comprehensive Tooltip Line Construction Pipeline

Every item tooltip in Potaria is assembled through a deterministic 7-stage pipeline:

```
[Stage 1: Header]
  • If currently equipped comparison card: "[ CURRENTLY EQUIPPED ]" (Bold Gold #FFD700)
  • Item Name (Formatted in Rarity Tier Color)
  • Rarity & Category Badge: "[RARITY CATEGORY]" (e.g. "[EPIC WEAPON]")

[Stage 2: Core Numeric Stats]
  • Weapons: "Weapon Power: {damage} Damage", "Use Speed: {speed_desc}"
  • Armor: "+{def} Defense", "+{hp} Max HP", "+{mp} Max MP"
  • Accessories: "+{speed}% Movement Speed", "+{crit}% Critical Strike Chance"
  • Food: "Meal Buff [{CATEGORY}] ({duration}s): {dish_name}", Bulleted stat list

[Stage 3: Enhancement & Broken State]
  • If enhanced: "Enhanced: +{level} (Double Stats at +7)" (Cyan #50F0FF)
  • If broken: "[BROKEN] Requires repair at Mystic Trader!" (Red #FF4646)

[Stage 4: Rolled Base Stats & Tags]
  • Rolled stats: "Rolled Base Stats: +{v} {STAT}" (Goldenrod #FFE68C)
  • Item tags: "Tags: {tag1} • {tag2} • {tag3}" (Light Cyan #64DCFF)

[Stage 5: Special Perks & Affix Sockets]
  • Special perks: "• {effect_description}" (Aqua #64F0F0)
  • Affix sockets:
    - Empty: "(O) Empty Affix Socket" (Grey #A0A0A0)
    - Filled: "(*) {Affix Name}: {Affix Description}" (Gold / Violet)

[Stage 6: Equipment Set Membership]
  • Set header: "Set: {Set Name} ({active_count}/{total_pieces})" (Gold)
  • Threshold milestones: "(2) +X Stat", "(4) +Y Stat", "(5) Active Aura" (Dim if inactive)

[Stage 7: Narrative & Lore]
  • Description: "{Word-wrapped item usage text}" (Light Slate #D7E1F0)
  • Lore Quote (Legendary/Mythic/Ancient only): '"{Author quote}"' (Amber #F0CD78)
```

---

### 5.7 Real-Time Profiler Overlay Layout (F3)

- Pressing **F3** toggles the real-time diagnostic telemetry HUD:
  - Line 1: `Potaria Engine v0.2.0a [Unity 6 LTS / URP 17.0.3]` (White)
  - Line 2: `FPS: 60.0 (Target: 60.0) | Frame Time: 16.6ms` (Green $>55$, Yellow $30-55$, Red $<30$)
  - Line 3: `Active Chunks: 12 (Cached: 48) | Tilemap Geometry: 4,890 Polygons`
  - Line 4: `Active Entities: 14 (Player: 1, Mobs: 8, Projectiles: 5, Drops: 0)`
  - Line 5: `Lighting Engine: Day/Night (Time: 0.35 NOON) | Point Lights: 6`
  - Line 6: `Pass Timers: World: 1.8ms | Physics: 3.2ms | Projectiles: 0.9ms | HUD: 1.4ms`

---

### 5.8 Pseudo-Code: Celestial Reversal Projectile Reflection Algorithm

```csharp
// Executed every frame during active Celestial Reversal window
public void UpdateCelestialReversal(float dt)
{
    if (_reflectionTimer <= 0f || _reflectionBudget <= 0) return;

    _reflectionTimer -= dt;
    Vector2 playerCenter = GetCenter();
    float radiusSquared = _reflectionRadius * _reflectionRadius;

    var activeProjectiles = ProjectileManager.Instance.ActiveProjectiles;
    for (int i = 0; i < activeProjectiles.Count; i++)
    {
        var proj = activeProjectiles[i];
        if (proj == null || !proj.IsEnemy || proj.IsReflected) continue;

        // Check if projectile center is within reflection field radius
        float distSq = (proj.Position - playerCenter).sqrMagnitude;
        if (distSq <= radiusSquared)
        {
            // Reflect: reverse velocity and amplify speed by 25%
            proj.Velocity = -proj.Velocity * 1.25f;

            // Invert ownership so bullet damages bosses instead of player
            proj.IsEnemy = false;
            proj.IsReflected = true;

            // Apply 1.5x damage amplification multiplier
            proj.Damage = Mathf.RoundToInt(proj.Damage * 1.5f);

            // Extend lifetime to ensure bullet can travel back to boss
            proj.RemainingLife += 2.0f;

            // Spawn radiant golden reflection spark VFX
            SpawnReflectionSpark(proj.Position);

            // Decrement active reflection budget
            _reflectionBudget--;
            if (_reflectionBudget <= 0)
            {
                _reflectionTimer = 0f;
                break;
            }
        }
    }
}
```

---

### 5.9 Pseudo-Code: 52% Core Hitbox vs. Graze Detection Algorithm

```csharp
// Evaluated during projectile motion against the player entity
public void CheckPlayerCollision(Projectile proj, PlayerController player)
{
    Vector2 projCenter = proj.Position;
    Vector2 playerCenter = player.Center;
    float dist = Vector2.Distance(projCenter, playerCenter);

    float visualRadius = proj.VisualRadius;
    float lethalCoreRadius = visualRadius * 0.52f;      // 52% Core Hitbox
    float grazeOuterRadius = visualRadius * 1.75f;      // 175% Graze Perimeter

    // 1. Check for Lethal Core Hitbox Collision
    if (dist <= lethalCoreRadius + player.HitboxRadius)
    {
        // Lethal Strike
        player.TakeDamage(proj.Damage);
        proj.Despawn();
        return;
    }

    // 2. Check for Perimeter Graze Collision
    if (dist <= grazeOuterRadius + player.HitboxRadius && !proj.HasGrazed)
    {
        proj.HasGrazed = true; // Each projectile grazes at most once

        // Award +1 MP grazing reward
        player.Stats.RestoreMp(1);

        // Trigger visual and auditory graze feedback
        player.TriggerGrazeFeedback();
    }
}
```

---

### 5.10 Pseudo-Code: Dual-Tilemap Snag-Free Platforming with BoxCast & Normal Detection

```csharp
// Rigidbody2D FixedUpdate execution for ground and slope detection
private void FixedUpdate()
{
    // Perform downward BoxCast past the bottom of player collider
    Vector2 boxSize = new Vector2(_collider.size.x * 0.85f, 0.08f);
    Vector2 boxOrigin = (Vector2)transform.position + _collider.offset - new Vector2(0f, _collider.size.y * 0.5f);

    int hitCount = Physics2D.BoxCastNonAlloc(
        boxOrigin,
        boxSize,
        0f,
        Vector2.down,
        _groundHitBuffer,
        0.06f,
        _groundLayerMask
    );

    bool groundedThisStep = false;
    Vector2 averageNormal = Vector2.up;

    for (int i = 0; i < hitCount; i++)
    {
        var hit = _groundHitBuffer[i];
        if (hit.collider == null || hit.collider == _collider) continue;

        // Verify surface angle is walkable (slope <= 45 degrees)
        float slopeAngle = Vector2.Angle(hit.normal, Vector2.up);
        if (slopeAngle <= 45.0f)
        {
            groundedThisStep = true;
            averageNormal = hit.normal;
            break;
        }
    }

    // Handle jump grace timer to prevent slope adhesion canceling upward leaps
    if (_jumpGraceTimer > 0f)
    {
        _jumpGraceTimer -= Time.fixedDeltaTime;
        _isGrounded = false;
    }
    else
    {
        _isGrounded = groundedThisStep;
        _groundNormal = averageNormal;
    }

    // Refresh Coyote Timer while grounded
    if (_isGrounded)
    {
        _coyoteTimer = _coyoteTime;
    }
    else
    {
        _coyoteTimer -= Time.fixedDeltaTime;
    }
}
```

---

## 6. Comprehensive Unity 6 Parity Audit Matrix

This master matrix audits every single game subsystem, mechanic, and architectural component across the entire Potaria franchise. Each entry documents its reference Pygame implementation, corresponding Unity 6 LTS C# script in `Assets/Scripts/`, verified implementation status (`[IMPLEMENTED]`, `[PARTIALLY IMPLEMENTED]`, or `[PENDING / NEED TO IMPLEMENT]`), and exact remaining backlog.

| Subsystem / Feature | Pygame Reference (`src/...`) | Unity 6 Target Script (`Assets/Scripts/...`) | Parity Status | Implemented Functionality (Milestones 1-3) | Remaining Backlog (Milestones 4-7) |
|:---|:---|:---|:---|:---|:---|
| **Infinite Terrain Synthesis** | `src/world/world_gen.py`, `noise.py` | `Assets/Scripts/World/WorldGenerator.cs`, `PerlinNoise.cs` | `[IMPLEMENTED]` | Multi-octave Perlin noise, rolling surface hills, cave networks, ore generation, dungeon tiers. | Sky citadels procedural generator fine-tuning. |
| **Chunk Streaming & Culling** | `src/world/chunk_manager.py` | `Assets/Scripts/World/ChunkManager.cs`, `ChunkData.cs` | `[IMPLEMENTED]` | Boundless horizontal streaming ($-\infty \leftarrow 0 \rightarrow +\infty$), 3-chunk active radius, distant chunk eviction. | Asynchronous coroutine disk serialization. |
| **Dual Tilemaps & Colliders** | `src/world/world.py`, `tiles.py` | `Assets/Scripts/World/WorldTilemaps.cs`, `TileDatabase.cs` | `[IMPLEMENTED]` | Solid block Tilemap with CompositeCollider2D (Polygons), Background Wall Tilemap, zero-friction physics material. | Water surface displacement shader. |
| **Tile Hardness & Mining** | `src/world/world.py`, `constants.py` | `Assets/Scripts/World/TileDefinition.cs`, `TileDatabase.cs` | `[IMPLEMENTED]` | Tool tier validation (Pickaxe, Axe, Shovel, Bare Hand), hardness scaling, tool efficiency math, mined item drops. | Block break cracking stage animation overlay. |
| **Celestial Day/Night Cycle** | `src/environment/sky.py` | `Assets/Scripts/World/Lighting/DayNightCycle2D.cs` | `[IMPLEMENTED]` | 720.0s day duration, 4 distinct phases (Dawn, Noon, Sunset, Night), ambient light attenuation, clock badge. | Seasonal weather events (monsoon rain). |
| **Dynamic Sky & Starfield** | `src/environment/sky.py` | `Assets/Scripts/World/Lighting/SkyRenderer2D.cs` | `[IMPLEMENTED]` | Procedural cubic Hermite sky gradient transitions, camera clear color sync, 140 twinkling star sprites. | Sun and moon celestial orbit sprites. |
| **2D Dynamic Point Lights** | `src/world/lighting.py` | `Assets/Scripts/World/Lighting/PointLightSource2D.cs` | `[IMPLEMENTED]` | Point Light 2D components for torches, lanterns, and chandeliers, 2D dynamic shadow casting on foreground blocks. | Torch support physics (drops if adjacent wall breaks).|
| **Subterranean Darkness** | `src/world/lighting.py` | `Assets/Scripts/World/Lighting/SubterraneanDarkness2D.cs` | `[IMPLEMENTED]` | Quadratic depth attenuation below $Y = 85$, pitch-black illumination at cavern depths ($Y \ge 160$). | Cavern ambient particle dust motes. |
| **Player Kinematics & Run** | `src/entities/player.py` | `Assets/Scripts/Player/PlayerController.cs` | `[IMPLEMENTED]` | Rigidbody2D interpolated movement, 6.0 run speed, 40.0 accel, 32.0 decel, velocity clamping. | Sprint stamina consumption in Hardcore mode. |
| **Platforming Jump Mechanics**| `src/entities/player.py` | `Assets/Scripts/Player/PlayerController.cs` | `[IMPLEMENTED]` | 12.0 jump force, 0.45x variable jump cut, 0.15s coyote time, 0.12s jump buffer, 0.08s jump grace timer. | Double jump wings accessory passive hook. |
| **Ground & Slope Detection** | `src/entities/player.py` | `Assets/Scripts/Player/PlayerController.cs` | `[IMPLEMENTED]` | BoxCastNonAlloc downward sweep, 45-degree slope normal detection, zero-friction material preventing snagging. | Dynamic footing particle dust on landing. |
| **Platform Drop-Through** | `src/entities/player.py` | `Assets/Scripts/Player/PlayerController.cs` | `[IMPLEMENTED]` | S / Down input sets 0.25s collision bypass, dropping hero through wooden platforms and scaffolding. | Re-engage ground snapping immediately on landing. |
| **Rope Rungs Climbing** | `src/entities/player.py` | `Assets/Scripts/Player/PlayerController.cs` | `[PARTIALLY IMPLEMENTED]`| Climbable tile detection hooks. | Upward (-3.8) and downward (3.2) climbing velocity physics states on rope ladders. |
| **Liquid Buoyancy & Swimming**| `src/entities/player.py` | `Assets/Scripts/Player/PlayerController.cs` | `[IMPLEMENTED]` | 0.88x horizontal drag, 0.90x vertical drag, 0.25x gravity reduction, paddle upward / dive downward swimming. | Water splash sound and particle bursts on entry. |
| **Oxygen Meter & Drowning** | `src/entities/player.py` | `Assets/Scripts/Player/PlayerController.cs` | `[IMPLEMENTED]` | 100.0 max oxygen, 7.5/s submerged drain, 40.0/s surfacing replenish, 1 heart/s true damage at 0% oxygen. | Bubble HUD meter overlay above player head. |
| **12 FPS Animated Potato** | `src/entities/player.py` | `Assets/Scripts/Player/PlayerController.cs` | `[IMPLEMENTED]` | 8-frame walk cycle, idle breathing, jump stretch, fall sprite, sprite facing flip, decorative sprout offset. | Armor sprite paperdoll rendering overlay. |
| **Death Transition & Respawn**| `src/entities/player.py` | `Assets/Scripts/Player/PlayerController.cs`, `CameraController.cs` | `[IMPLEMENTED]` | 3.0s cinematic pitch-black fade, instant camera snap, spawn point teleportation, health restoration. | Boss item drop penalty in Hardcore mode. |
| **Melee Combat & Swings** | `src/combat/combat_system.py` | `Assets/Scripts/Combat/WeaponController.cs` | `[IMPLEMENTED]` | Swing duration (0.10s-0.45s), weapon attack cooldowns based on weapon tier, weapon aim angle tracking. | Visual slash particle crescent trail. |
| **Single-Target Combat Rule** | `src/combat/combat_system.py` | `Assets/Scripts/Combat/WeaponController.cs` | `[IMPLEMENTED]` | Single-target hit registry per swing, Ancient relic cleave (`hasCleave`) exception for multi-target hits. | Floating damage number text integration. |
| **Ballistic Archery** | `src/entities/projectile.py` | `Assets/Scripts/Combat/Projectile.cs`, `ProjectileManager.cs` | `[IMPLEMENTED]` | Parabolic gravity trajectory (`vy += 9.8 * 0.44 * dt`), rotation facing velocity vector, 4 arrow types. | Arrow retrieval from terrain blocks. |
| **Magic Projectile Archetypes**| `src/entities/projectile.py`| `Assets/Scripts/Combat/Projectile.cs`, `ProjectileManager.cs` | `[IMPLEMENTED]` | Catalyst homing stars, Staff elemental splash bolts, Rod piercing javelins, Scepter radial shockwaves. | Mana depletion deduction on cast. |
| **Danmaku Pattern Novas** | `src/entities/bullet_hell.py`| `Assets/Scripts/Combat/DanmakuEmitter.cs` | `[IMPLEMENTED]` | 16-way spiral novas, rotating celestial cross beams, targeted rings with navigable dodge corridors. | Criss-cross wave curtains pattern. |
| **52% Core Lethal Hitbox** | `src/entities/bullet_hell.py`| `Assets/Scripts/Combat/Projectile.cs` | `[IMPLEMENTED]` | Precise 52% central core lethal hitbox (`radius * 0.52`), eliminating edge clipping deaths. | Hitbox debug visualizer in F3 mode. |
| **Perimeter Graze System** | `src/entities/bullet_hell.py`| `Assets/Scripts/Combat/Projectile.cs`, `PlayerStats.cs` | `[IMPLEMENTED]` | 100%-175% outer radius graze detection, +1 MP reward, graze chime audio, and cyan spark feedback. | Graze counter badge in In-Game HUD. |
| **Celestial Reversal** | `src/entities/bullet_hell.py`| `Assets/Scripts/Player/PlayerController.cs` | `[IMPLEMENTED]` | 0.45s timed reflection window, 15 bullet budget, 1.5x damage amplification, boss target inversion. | Golden solar flare shockwave VFX. |
| **100-Level RPG Progression** | `src/rpg/stats.py` | `Assets/Scripts/RPG/PlayerStats.cs` | `[IMPLEMENTED]` | Level 1-100 curve, EXP formula `int(100 * lvl^2.1)`, stat scaling per level (+15 HP, +8 MP, +3 ATK, +1 DEF). | Level up golden fanfare audio and particle flare. |
| **Damage Mitigation & DEF** | `src/rpg/stats.py` | `Assets/Scripts/RPG/PlayerStats.cs`, `CharacterStats.cs` | `[IMPLEMENTED]` | Physical mitigation formula, 85% defense cap, 15% min pierce, Titan's Resolve (3x DEF under 30% HP). | Armor penetration reduction math. |
| **Dedicated Coin Purse** | `src/rpg/stats.py` | `Assets/Scripts/RPG/PlayerStats.cs` | `[IMPLEMENTED]` | 100c = 1s, 100s = 1g auto-conversion, purchasing power integer representation, coin deduction methods. | Coin purse visual UI slot in backpack. |
| **5-Meal Buff Framework** | `src/entities/player.py` | `Assets/Scripts/RPG/MealBuffManager.cs`, `MealBuffCaps.cs` | `[IMPLEMENTED]` | 5 concurrent categories (Offense, Defense, Mobility, Resource, Utility), 1-per-category replacement rules. | Active meal buff HUD tray overlay with radial fill.|
| **19 Statutory Meal Caps** | `src/entities/player.py` | `Assets/Scripts/RPG/MealBuffCaps.cs` | `[IMPLEMENTED]` | Hard caps across damage mult (12%), atk speed (10%), crit (6%), defense (+6), magic res (15%), etc. | Tooltip notification when food buff hits cap. |
| **Philippine Food Catalog** | `src/ui/inventory.py` | `Assets/Scripts/Data/FoodItemData.cs`, `FoodBuffData.cs` | `[IMPLEMENTED]` | 79 authentic Filipino dishes and ingredients imported into typed ScriptableObjects with cultural notes. | Cooking queue UI on Campfires and Furnaces. |
| **Agricultural Soil Hydration**| `src/world/world.py` | `Assets/Scripts/World/TileDatabase.cs` | `[IMPLEMENTED]` | Farmland and Hydrated Farmland tile definitions, 4-block horizontal water hydration simulation. | Hoe tilling and Watering Can actions. |
| **8 Philippine Crops** | `src/world/world.py` | `Assets/Scripts/Data/CropData.cs` | `[PARTIALLY IMPLEMENTED]`| 9 Crop ScriptableObjects, 36 growth stage sprites (stages 0-3) in `Assets/Sprites/Crops/`. | Runtime `CropTileComponent` on tilemap. |
| **2D Fishing Minigame** | `src/ui/fishing_minigame.py` | ScriptableObjects in `Assets/Items/` | `[PENDING / NEED TO IMPLEMENT]`| 10 Philippine fish ScriptableObjects imported into project. | 15.0s urgency timer modal, line tension meter, sweet spot bonus, thrashing fish AI (Milestone 5). |
| **Paperdoll Equipment UI** | `src/ui/character_panel.py` | `Assets/Scripts/Data/EquipmentItemData.cs` | `[PARTIALLY IMPLEMENTED]`| 705 armor/accessory ScriptableObjects generated and validated. | 10-slot paperdoll visual inventory UI with slot dragging and equipment stat preview (Milestone 4). |
| **27 Equipment Sets** | `src/rpg/equipment_update.py`| `Assets/Scripts/Data/EquipmentSetData.cs` | `[PARTIALLY IMPLEMENTED]`| 27 EquipmentSetData ScriptableObjects with piece links and 2/4/5-piece milestone thresholds. | Runtime equipment set count evaluation and active visual auras in combat (Milestone 4). |
| **7-Tier Rarity Engine** | `src/loot/rarity_engine.py`| `Assets/Scripts/Data/ItemRarity.cs` | `[IMPLEMENTED]` | Rarity enum, hex colors, drop weights, and stat multipliers across Common to Ancient. | Procedural prefix/suffix affix roller on dropped items.|
| **Item Enhancement (+1 to +7)**| `src/rpg/enhancement.py` | `Assets/Scripts/Data/ItemData.cs` | `[PENDING / NEED TO IMPLEMENT]`| Basic stat multiplier formula defined. | Forge Master UI, enhancement success/break risk roller, 1 Gold repair interaction (Milestone 4). |
| **Affix Slot Carving** | `src/rpg/enhancement.py` | `Assets/Scripts/Data/ItemData.cs` | `[PENDING / NEED TO IMPLEMENT]`| `MAX_ADDITIONAL_AFFIX_SLOTS` limits verified. | Morrigan Void Weaver carving UI, Affix Stone application, circular socket indicators (Milestone 4). |
| **Slime Mob Behaviors** | `src/entities/mob.py` | `Assets/Scripts/Mob/SlimeMob.cs` | `[IMPLEMENTED]` | Green and Purple slimes, squish/stretch animation, grounded hops, wall bouncing, contact damage. | Sand, Frost, and Corrupt slime variants. |
| **Zombie Mob Behaviors** | `src/entities/mob.py` | `Assets/Scripts/Mob/ZombieMob.cs` | `[IMPLEMENTED]` | Surface Zombie, horizontal patrolling, sensory tracking (12 blocks), obstacle auto-step jumping. | Ice Zombie, Mummy, and Skeleton variants. |
| **Demon Eye Mob Behaviors** | `src/entities/mob.py` | `Assets/Scripts/Mob/DemonEyeMob.cs` | `[IMPLEMENTED]` | Night Gazer / Demon Eye, zero-gravity sinusoidal flight, dive-bomb tracking, daytime fleeing/despawn. | BatMob and CaveBat variants. |
| **Mob Spawner System** | `src/combat/combat_system.py` | `Assets/Scripts/Mob/MobSpawner.cs` | `[IMPLEMENTED]` | 15-35 tile spawn annulus, 10 active mob cap, >60 tile despawn radius, daytime mob suppression. | Subterranean biome mob spawn tables. |
| **Philippine Livestock Mobs** | `src/entities/mob.py` | Planned `Assets/Scripts/Mob/` | `[PENDING / NEED TO IMPLEMENT]`| Meat ingredient ScriptableObjects imported. | Manok, Pato, Baboy, Kalabaw, Kambing mob AI and drops (Milestone 5). |
| **Mythological Aswang Mob** | `src/entities/mob.py` | Planned `Assets/Scripts/Mob/` | `[PENDING / NEED TO IMPLEMENT]`| None. | High-speed nocturnal predator AI, wall leaping, lifesteal bites (Milestone 4). |
| **Dungeon Boss Encounters** | `src/entities/boss.py` | `Assets/Scripts/Combat/BossController.cs` | `[PARTIALLY IMPLEMENTED]`| BossController with Phase 1 & 2 transitions, bullet-hell emitter hooks, health bar UI. | Standalone state machines for Malus, Ignis, Cryo, Necro, and Grand Boss Sol-Rho (Milestone 4). |
| **Nomadic Animated Traders** | `src/entities/npc.py` | Planned `Assets/Scripts/NPC/` | `[PENDING / NEED TO IMPLEMENT]`| Trader ware definitions. | Zephyrion, Ignis Vance, Morrigan spawn logic, turtle shell invulnerability defense, shop UI (Milestone 4). |
| **Housing Validity & Town NPCs**| `src/world/world.py`, `npc.py` | Planned `Assets/Scripts/World/` | `[PENDING / NEED TO IMPLEMENT]`| Tile definitions for furniture, doors, and lights. | Flood fill room check (15-250 tiles, door, light, table, chair, walls), Guide/Nurse spawn (Milestone 4). |
| **In-Game HUD & Hotbar** | `src/ui/hud.py` | `Assets/Scripts/UI/PotariaHUD.cs` | `[IMPLEMENTED]` | 10-slot hotbar, selection frame, Life text/hearts, Mana bar, clock badge, radar badge, 4 skill badges. | Hover tooltips and active item dragging. |
| **Side-by-Side Tooltips** | `src/ui/hud.py` | `Assets/Scripts/UI/PotariaHUD.cs` | `[PENDING / NEED TO IMPLEMENT]`| Tooltip lines builder and measurement logic defined. | Side-by-side 'katabi' candidate vs equipped dual cards, screen boundary clamping (Milestone 4). |
| **F3 Real-Time Profiler** | `src/profiler.py` | `Assets/Scripts/UI/PotariaHUD.cs` | `[IMPLEMENTED]` | Toggleable diagnostic panel, FPS counter, frame time (ms), active chunks/mobs telemetry. | Microsecond pass timer breakdowns. |
| **Dual Localization (EN / FIL)**| Project string dicts | `Assets/Scripts/Localization/LocalizationManager.cs` | `[IMPLEMENTED]` | English ('en') and Filipino ('fil') localization dictionaries, zero-allocation lookup, 'L' key toggle. | Full narrative dialogue translation in cutscenes. |
| **Input System & Gamepad** | `src/ui/touch_controller.py` | `Assets/Scripts/Input/PotariaInput.cs` | `[IMPLEMENTED]` | Unity New Input System + legacy fallback, Keyboard/Mouse, Steam Deck / Xbox gamepad bindings. | Onscreen virtual touch joystick rendering. |
| **Audio SFX & Jump Check** | `src/audio/sound_effects.py` | `Assets/Scripts/Player/PlayerController.cs` | `[PARTIALLY IMPLEMENTED]`| Head unblocked jump sound suppression, 34 audio clips ingested into `Assets/Audio/`. | Dynamic biome BGM crossfader, spatial sound playback (Milestone 4). |
| **Save Engine & HMAC Security** | `src/world/save_manager.py` | Planned `Assets/Scripts/Save/` | `[PENDING / NEED TO IMPLEMENT]`| Save structure schemas. | Atomic JSON file write, backup snapshot rotations, HMAC-SHA256 signature verification (Milestone 4). |
| **Multiplayer LAN / P2P** | `src/network/client.py`, `server.py` | Planned `Assets/Scripts/Network/` | `[PENDING / NEED TO IMPLEMENT]`| Binary network packet definitions. | FishNet / Steamworks P2P networking, lobby invites, entity synchronization (Milestone 6). |
| **Modding & DLC System** | `src/modding/mod_manager.py`| Planned `Assets/Scripts/Modding/` | `[PENDING / NEED TO IMPLEMENT]`| Mod manifest schemas. | Dynamic ScriptableObject / AssetBundle content pack loader (Milestone 6). |

---

## 7. Strategic Porting Roadmap & Prioritized Backlog (Milestones 4 through 7)

### Milestone 4: Inventory, Crafting, Equipment & Responsive UI (CURRENT FOCUS)
- **Objective**: Deliver a responsive, high-fidelity UI layer matching the authentic Pygame reference, featuring side-by-side item comparison, 40-slot backpack inventory, 5-category crafting book, and mobile touch controls.
- **Prioritized Task Backlog**:
  1. **40-Slot Backpack Inventory UI (`Assets/Scripts/UI/InventoryUI.cs`)**:
     - 4 rows by 10 columns grid with 40x40 pixel slot frames and 4px padding.
     - Drag-and-drop item movement, stack splitting (Right-Click splits half stack), and quick transfer (Shift-Click moves to hotbar/chest).
     - `[ORGANIZE]` button performing automatic gap compaction and item type sorting.
     - Dedicated Coin Purse UI displaying Copper, Silver, and Gold denominations with real-time conversion.
  2. **Side-by-Side Equipment Comparison Cards ('Katabi') (`Assets/Scripts/UI/TooltipRenderer.cs`)**:
     - Hovering any equippable item while Character Info panel is open ('C' key) renders candidate item alongside equipped item.
     - Adorns currently equipped item with bold gold badge: `[ CURRENTLY EQUIPPED ]`.
     - Highlights stat differentials (green for improvements, red for decreases).
     - Screen boundary clamping ensuring dual cards never render off-screen.
  3. **Minecraft-Style 5-Category Crafting Book (`Assets/Scripts/UI/CraftingUI.cs`)**:
     - 5 Category Tabs: All, Building, Equipment, Survival & Consumables, Furniture & Mechanisms.
     - Proximity Crafting Station Detection: Checks player radius for Hand (always available), Work Bench (`TILE_WORK_BENCH`), Furnace (`TILE_FURNACE`), and Cozy Hearth (`TILE_FIREPLACE`).
     - Real-time material sufficiency check: Greyed out recipe frames if ingredients are missing.
  4. **Circular Affix Socket Indicators (`Assets/Scripts/UI/AffixSocketRenderer.cs`)**:
     - Clean ARPG socket indicators: `(O) Empty Affix Socket` in grey; `(*) {Affix Name}` in gold/violet.
     - Enforces `MAX_ADDITIONAL_AFFIX_SLOTS` limits (Common 0, Uncommon 0, Rare 0, Epic 1, Legendary 1, Mythic 2, Ancient 2).
  5. **Bottom-Left Active Meal Buff HUD Overlay (`Assets/Scripts/UI/MealBuffTray.cs`)**:
     - 5 category slots (Offense, Defense, Mobility, Resource, Utility) with radial countdown meters.
  6. **Mobile Virtual Touch Controls (`Assets/Scripts/UI/TouchController.cs`)**:
     - Floating virtual analog joystick with smooth vector return.
     - Action button cluster: Attack/Mine, Jump, Dash, Quick Heal.

---

### Milestone 5: Philippine Farming, Tiered Cooking & Fishing Minigame
- **Objective**: Complete the agricultural lifecycle simulation, furnace/campfire cooking queues, and the 2D fishing battle minigame.
- **Prioritized Task Backlog**:
  1. **Agricultural Lifecycle (`Assets/Scripts/World/CropTileComponent.cs`)**:
     - Attaches to tilled farmland tilemap cells.
     - Tracks 4 growth stages (Stages 0-3) for all 8 native crops (Rice, Garlic, Onion, Ginger, Eggplant, String Beans, Tamarind, Calamansi).
     - Daily morning growth advancement conditional on 4-block water proximity and surface/torch illumination.
     - Hoe tilling and infinite Watering Can hydration tools.
  2. **Tiered Cooking Stations & Grilling (`Assets/Scripts/Cooking/CookingManager.cs`)**:
     - Active cooking queues on Furnaces and Cozy Hearths (2.5s to 20.0s durations).
     - Single active cooking slot per furnace, animated smoke particles during cooking.
     - Direct fish grilling: Converts fresh catches into Inihaw na Bangus, Inihaw na Tilapia, etc.
  3. **2D Fishing Battle Minigame (`Assets/Scripts/Fishing/FishingBattleModal.cs`)**:
     - Interactive right-click tug-of-war modal against 10 Philippine fish species.
     - 15.0s countdown urgency timer, Reel Progress bar (0% to 100%), Line Tension bar (0% to 100%).
     - Fish thrash warning states (reeling during thrash causes +15% tension; line snaps at 100%).
     - Moving golden sweet-spot awarding 1.5x reel speed bonus.

---

### Milestone 6: Steamworks Integration & P2P / LAN Multiplayer
- **Objective**: Establish authoritative multiplayer synchronization and official Steamworks platform features.
- **Prioritized Task Backlog**:
  1. **P2P Multiplayer Transport (`Assets/Scripts/Network/NetworkManager.cs`)**:
     - Integrate `FishNet` (or Unity Netcode for GameObjects) with `Steamworks.NET` / `FishySteamworks`.
     - Valve Steam Datagram Relay (SDR) integration: Direct Steam friend invites (`Invite Friend` / `Join Game` via Steam overlay) with zero port forwarding.
     - Local network UDP broadcast discovery on port 45454 for offline LAN cooperative sessions.
  2. **State Synchronization & Lag Compensation**:
     - Client-side prediction for local player movement and platforming.
     - Entity interpolation for remote players, mobs, and boss danmaku projectiles.
     - Block delta packet broadcast ensuring synchronized terrain destruction and building.
  3. **Steam Platform Services**:
     - Steam Cloud save synchronization format (`saves/worlds/*.json`).
     - Steam Achievements integration (tracking 218 achievements from `data/achievements.json`).
     - Steam Rich Presence (e.g. "Exploring Nether Dungeon (Level 35) [Day 14]").

---

### Milestone 7: Multiplatform Commercial Release (Steam & Google Play Store)
- **Objective**: Package, optimize, and publish Potaria to Steam (Windows PC / Steam Deck) and the Google Play Store (Android 14+).
- **Prioritized Task Backlog**:
  1. **IL2CPP 64-Bit Compilation & Target Builds**:
     - Windows 64-bit standalone executable (`Potaria.exe`).
     - Steam Deck optimization: 16:10 aspect ratio (1280x800 resolution), full gamepad navigation, verified controller glyphs.
     - Signed Android App Bundle (`.aab`) targeting Android 14+ (API Level 34).
  2. **Mobile Lifecycle & Power Management**:
     - Pause game simulation upon Android application switch or incoming call.
     - Background save state preservation preventing lost progress on low-memory process termination.
     - Battery consumption profiling: Stable 60 FPS on mid-range mobile GPUs (Adreno 610 / Mali-G57).
  3. **Commercial Storefront Assets**:
     - Dual-language store descriptions (English and Filipino).
     - Trailer captures, localized gameplay screenshots, and ESRB / age rating documentation.

---
