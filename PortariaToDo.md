# POTARIA (SPUD: ROOT REALM) — DEVELOPMENT ROADMAP & TODO
**Lead Developer:** Kurados  
**Engine:** Pure Python 3.13 + Pygame-ce 2.5.8 (100% Offline Standalone)  
**Architecture:** Host-Authoritative 2D Sandbox Action RPG  
**Last Updated:** October 2026  

---

## TABLE OF CONTENTS
1. [Executive Summary & Current Architecture](#1-executive-summary--current-architecture)
2. [Completed Systems & Verified Milestones](#2-completed-systems--verified-milestones)
3. [Near-Term Development (v1.1 - v1.3)](#3-near-term-development-v11---v13)
4. [Mid-Term Content Expansion (v1.4 - v1.6)](#4-mid-term-content-expansion-v14---v16)
5. [Long-Term Vision & Engine Scalability (v1.7 - v2.0)](#5-long-term-vision--engine-scalability-v17---v20)
6. [Engine Optimization & Technical Debt Tracker](#6-engine-optimization--technical-debt-tracker)
7. [Automated Verification & QA Matrix](#7-automated-verification--qa-matrix)

---

## 1. EXECUTIVE SUMMARY & CURRENT ARCHITECTURE

Potaria is a boundless 2D sandbox action RPG merging the infinite terrain generation and digging/building freedom of Terraria with the deep character progression, 40-skill roster, paperdoll equipment customization, and boss gauntlets of Chroisen.

### Key Architecture Modules:
- **`main.py`**: Core game state manager, event dispatcher, HUD overlay renderer, in-game cheat console, and multiplayer network sync loop.
- **`src/world/`**: Infinite multi-octave chunk generator (`chunk_manager.py`, `world.py`), tile physics, wall systems, and lighting engine.
- **`src/rpg/`**: Character leveling (1–100), EXP curves, equipment paperdoll slots, thematic armor set bonuses, radiant auras, and 40 skill books.
- **`src/combat/`**: Hitbox collisions, damage formulas with defense mitigation, critical rolls, natural mob spawner, subterranean mini-bosses, and Sol-Rho the Celestial Titan.
- **`src/entities/projectile.py`**: Sub-pixel `pygame.FRect` + `Vector2` ballistic arrows with gravity, homing catalyst stars, piercing rod javelins, elemental staff bolts, and expanding scepter pulses.
- **`src/entities/vfx.py`**: High-performance multi-frame `AnimatedVFX` pipeline supporting 100+ frames of procedural and AI-generated combat effects, entity anchoring, and screen shake.
- **`src/network/`**: Host-authoritative LAN socket server (`lan_server.py`) and client (`lan_client.py`) supporting 1–5 player cooperative sessions.
- **`src/ui/`**: Responsive inventory grid, crafting tree, equipment paperdoll, hotbars, cheat console, local chat, and touch control overlays.

---

## 2. COMPLETED SYSTEMS & VERIFIED MILESTONES

### Core Mechanics & World
- [x] **Boundless Open World**: Infinite horizontal coordinate generation without artificial boundary walls ($-\infty \leftarrow 0 \rightarrow +\infty$).
- [x] **Tile Interaction**: Left-click mining (hold-to-mine), right-click block placement, background wall placement and removal.
- [x] **Illuminated Housing**: Torches, wooden/stone/glass walls, enclosed room detection suppressing monster spawning.
- [x] **Day/Night Cycle & Time-of-Day Pacing**:
  - [x] Continuous cyclical sky clock ($0.0$ to $1.0$).
  - [x] **Morning Peace ($t < 0.22$)**: Zero surface monster spawning for tranquil exploration, logging, and building.
  - [x] **Night Danger Peak ($t \ge 0.50$)**: High density spawning of aggressive Zombies, Demon Eyes, and Shadow Crawlers.
- [x] **Biomes & Arenas**: Forest plains, Desert dunes, Snow tundra, Caverns, Magma chambers, Dungeon Crypts, and Pocket Boss Arenas.

### Combat, Weapon Archetypes & Ballistics
- [x] **Long-Range Weapons & Projectile Behaviors**:
  - [x] **Bows & Ballistics**: Sub-pixel `pygame.FRect` + `Vector2` gravity physics ($g = 140\text{ px/s}^2$) for Shortbows, Recurves, Longbows, and Composite Bows.
  - [x] **Composite Bows**: Multi-layered composite recurves (`composite_bow`, `reinforced_composite_bow`, `ancient_composite_bow`) registered across weapons catalog and inventory.
  - [x] **Ammo Prioritization**: Automatic inventory consumption: Astral Arrow > Frostburn Arrow > Flame Arrow > Wooden Arrow. Out-of-ammo fallback handling.
  - [x] **Relic Bow Starlight Generator**: Relic bows (Ancient Eternal Shortbow, Ancient Composite Bow, Celestial Bow) generate ethereal starlight when out of arrows.
  - [x] **Magic Catalysts**: Autonomous homing celestial stars (`CatalystStarProjectile`) that steer toward the nearest mob/boss with a 560px distance cap.
  - [x] **Magic Staves**: Concentrated elemental bolts (`StaffBoltProjectile`) (Fire, Frost, Arcane, Nature) with custom status effects and a 560px distance cap.
  - [x] **Magic Rods**: Piercing crystalline javelins (`RodJavelinProjectile`) piercing through up to 3 consecutive targets with a 560px distance cap.
  - [x] **Magic Scepters**: Expanding radial shockwaves (`ScepterPulseProjectile`) damaging dense packs with a 560px distance cap.
- [x] **Weapon Cooldown Tuning (Anti-Spam)**:
  - [x] Shortswords: 0.22s base cooldown.
  - [x] Broadswords: 0.32s base cooldown.
  - [x] Greatswords: 0.46s base cooldown.
  - [x] Bows (including Composite Bows): 0.52s calibrated cooldown.
  - [x] Magic Weapons (Catalysts, Staves, Rods, Scepters): 0.54s calibrated cooldown.

### RPG Progression, Equipment & Set Effects
- [x] **Chroisen Paperdoll**: Head, Chest, Legs, Weapon, and 6 Accessory slots.
- [x] **Leveling & Attributes**: 1 to 100 level progression with EXP rewards, HP, MP (1.5 MP/s regen), ATK, DEF, and Crit.
- [x] **Thematic Equipment Sets & Radiant Pulsing Auras**:
  - [x] **Ancient Resonating Set**: +35% ATK, +30% DEF, +50 HP, +20% Crit, radiant pulsing ancient celestial aura.
  - [x] **Celestial Titan Set**: +25% DEF, +30 HP, +15% ATK, celestial ward aura.
  - [x] **Magma Core Set**: +20% ATK, +15 Reflected Fire Thorns, +25 HP, molten magma aura.
  - [x] **Cryo Carapace Set**: +20% DEF, +2.5 MP/s Regen, +35 HP, glacial cryo aura.
  - [x] **Umbral Shadow Set**: +20% Crit, +20% ATK, +0.2 Move Speed, void shadow aura.
  - [x] **Spud Sovereign Set**: +30 Max HP, +5 HP/s Regen, +10% ATK, +10% DEF, earth sprout aura.
  - [x] **Cactus Needle Set**: +15 Reflected Thorns, +10% ATK, +10% DEF, prickly cactus aura.
- [x] **Drop Rate Economy Rebalance (Grind-Rewarding)**:
  - [x] Common (98.69%), Uncommon (1.0%), Rare (0.25%), Epic (0.05%), Mythic (0.008%), Legendary (0.002%), Ancient (0.0004% - 1 in 250,000).
  - [x] Golden celebratory fanfare sound, floating announcement banner, and `rarity_ancient` achievement unlock upon discovering Ancient relics.
  - [x] Diurnal mob spawning curve: Morning Peace ($t < 0.22$) with zero surface hostiles, scaling to midday, dusk, and night peak.

### Visual Effects & Boss Encounters
- [x] **Animated VFX Pipeline**: `VisualEffectManager` and `AnimatedVFX` supporting 26 grand animation suites (202 total frames) exported to disk.
- [x] **Skill Visuals & Failure Feedback**:
  - [x] Power Slash, Whirlwind, Dash, Fireball, Meteor, Frost Nova, Celestial Shield, Void Singularity enhanced with grand multi-frame VFX.
  - [x] Silent failure fix: Unlearned skills, skills on cooldown, or insufficient MP now trigger floating HUD banners and spark feedback.
- [x] **Ancient Weapon Visuals**: Blade swing arc placement for melee slashes (`ancient_slash`, `ancient_cleave_grand`), starlight bursts for ancient bows, and celestial screen shake.
- [x] **Subterranean Mini-Bosses**: Lord Malus, Ignis Colossus, Cryo-Spud, Necro-Tuber with unique attack routines and arena teleportation runes.
- [x] **Grand Boss Sol-Rho**: Souls-like 2-phase battle (Phase 1: 1000 HP levitating titan; Phase 2: 1400 HP enraged supernova).

### Multiplayer & Developer Tools
- [x] **1–5 Player LAN Multiplayer**: Host-authoritative architecture, individual inventories, party HP/ATK scaling, nearest-player targeting, and LAN chat.
- [x] **Developer Cheat Console**:
  - [x] Keybindings: `Enter`, `/`, `~`.
  - [x] Direct Item ID Cheats: Typing any item ID directly gives it to Spud (e.g. `/composite_bow`, `/astral_wrath`, `/astral_arrow 50`).
  - [x] Commands: `/god`, `/invincible`, `/heal`, `/speed [mult]`, `/time [preset|val]`, `/give <id> [count]`, `/item`, `/ancient`, `/weapons`, `/spawn <mob|boss> [count]`, `/killall`, `/level [count]`, `/allskills`, `/clear`, `/help`.
  - [x] Full documentation in `CHEATS.md`.
- [x] **Automated Testing Suite**: 182+ automated unit tests running headless in CI across 14 test suites.

---

## 3. NEAR-TERM DEVELOPMENT (v1.1 - v1.3)

### 3.1 Additional Biomes & World Expansion
- [ ] **Lush Jungle Biome**:
  - Giant vine canopies, mud blocks, mahogany wood, and wild poisonous Spud Wasps.
  - Ancient Jungle Temple ruin with subterranean trap dart blocks and pressure plates.
- [ ] **Floating Sky Islands**:
  - Cloud blocks and rain clouds generating at high elevations ($y < 60$).
  - Lucky Horseshoe and Starfury chests inside gilded cloud temples.
- [ ] **Bioluminescent Mushroom Caves**:
  - Deep cavern biome with glowing blue fungi, mushroom trees, and glowing spores providing natural light.

### 3.2 Town NPCs & Housing Quest Engine
- [ ] **NPC Spawning Validation**: Check suitable housing conditions (table, chair, torch, door, enclosed walls).
- [ ] **NPC Roster**:
  - [ ] **Farmer Spud**: Sells crop seeds, gardening hoes, and basic food recipes.
  - [ ] **Blacksmith Spud**: Repairs durability, sells raw ingots, and offers weapon reforging (re-roll affixes).
  - [ ] **Wizard Spud**: Sells mana potions, elemental tomes, and enchants weapons with elemental affinities.
  - [ ] **Alchemist Spud**: Brews health, mana, stamina, and night-vision potions.
- [ ] **NPC Dialogue & Quest Engine**: Multi-stage questlines awarding rare crafting schematics and accessories.

### 3.3 Agriculture & Cooking Overhaul
- [ ] **Tilled Soil & Crop Growth**: Hoed dirt blocks with watering mechanics.
- [ ] **Crop Types**: Potatoes, Golden Spuds, Carrots, Wheat, Fire Peppers, Frost Berries.
- [ ] **Cooking Station Recipes**:
  - Potato Fries (+15% Movement Speed for 5 minutes).
  - Hearty Potato Stew (+30 Max HP and +2 HP/s regen for 8 minutes).
  - Spicy Pepper Mash (+20% Fire Damage and +10% Attack Speed).

---

## 4. MID-TERM CONTENT EXPANSION (v1.4 - v1.6)

### 4.1 Mounts & Companions
- [ ] **Ridable Mounts**:
  - Starch Beetle (increases ground speed by 150%, jumps over 3-tile ledges).
  - Celestial Stallion (double jump and glide through air).
- [ ] **Summonable Pets**:
  - Mini Potato Golem (draws aggro from small enemies).
  - Starlight Wisp (provides illumination and magnetic item pickup).

### 4.2 Dynamic Weather & Environmental Events
- [ ] **Weather System**:
  - Rain & Thunderstorms: Increases water levels, accelerates crop growth, reduces torch light radius.
  - Desert Sandstorms: Decreases horizontal visibility, causes slight wind drift on projectiles.
  - Cavern Blizzards: Freezes water into ice, inflicts slow status unless near a campfire.
- [ ] **Invasion Events**:
  - **The Rotten Swarm**: Waves of corrupted zombies and flying blight wasps assault Spud's base.
  - **Solar Eclipse**: Day turns dark; ultra-rare cosmic mobs spawn with boosted Ancient item drop rates.

### 4.3 Hardmode / Post-Sol-Rho Celestial World Bleed
- [ ] **Post-Sol-Rho World Awakening**:
  - Defeating Sol-Rho shatters the sky vault, initiating the "Celestial Awakening".
  - Cosmic meteorites crash into the world, spawning Starfall Ores.
  - Four Celestial Pillars emerge across the world that must be destroyed to unlock the final Transcendence Gate.

---

## 5. LONG-TERM VISION & ENGINE SCALABILITY (v1.7 - v2.0)

### 5.1 Gamepad & Steam Deck Optimization
- [ ] **Gamepad Input System**: Full XInput and DirectInput support (Xbox, PlayStation, Nintendo Switch controllers).
- [ ] **Radial Item & Skill Wheel**: Hold bumper/shoulder button to slow time and select skills or inventory items.
- [ ] **Twin-Stick Aiming**: Right thumbstick cursor aiming for bows, staves, and mining.
- [ ] **Steam Deck Verification**: 60 FPS profile, 1280x800 native 16:10 aspect ratio, battery optimization (< 8W).

### 5.2 Mobile & Touch Interface Polish
- [ ] **Virtual Dual Joysticks**: Left thumb virtual stick for movement/jumping; right thumb for targeting and auto-swing.
- [ ] **Pinch-to-Zoom Camera**: Smooth multi-touch viewport scaling.
- [ ] **Mobile HUD Scale Slider**: Adaptive UI scaling for smartphones and tablets.

### 5.3 Extensible Modding API & Data Schemas
- [ ] **Data-Driven Definitions**: Move all items, mobs, recipes, tiles, and skills to JSON schemas (`data/items.json`, `data/recipes.json`, etc.).
- [ ] **Lua / Python Plugin Hooks**: Event hooks for `on_mob_slain`, `on_tile_broken`, `on_player_hit`, and `on_world_gen`.
- [ ] **Custom Tile & Sprite Loader**: Hot-reloadable mod texture packs and sound banks.

### 5.4 Dedicated Server Binary & Headless Host
- [ ] **Headless Server CLI**: Run `potaria_server.py --port 7777 --world MyWorld` without initializing Pygame display surfaces.
- [ ] **Dedicated Admin Commands**: Remote console via TCP socket for server administrators (`kick`, `ban`, `say`, `save`, `reload`).

---

## 6. ENGINE OPTIMIZATION & TECHNICAL DEBT TRACKER

| Area | Current State | Target Optimization | Priority |
|---|---|---|:---:|
| **Chunk Meshing** | Per-tile blit in render loop | Pre-rendered chunk subsurface caching (120+ FPS) | High |
| **Collision Detection** | Iterative bounding box checks | 2D Spatial Hash Grid for entities and projectiles | Medium |
| **Particle Physics** | Vector math on individual objects | Numpy vectorized particle batch processing | Medium |
| **Save Serialization** | JSON formatted text files | Compressed binary format (zlib/msgpack) for large worlds | Low |
| **Audio Mixing** | Standard pygame mixer channels | Dynamic low-pass filtering for underground depths | Low |

---

## 7. AUTOMATED VERIFICATION & QA MATRIX

### Test Suite Execution
To run the automated regression suite across all systems:
```bash
# Run full suite (173+ tests)
python -m unittest discover -s tests

# Run long-range weapons & ballistics tests
python -m unittest tests/test_long_range_weapons.py

# Run ancient sets, time-of-day, and cheat console tests
python -m unittest tests/test_ancient_set_and_cheats.py

# Run attack speed balance tests
python -m unittest tests/test_attack_speed.py

# Run mobile controls and touch UI tests
python -m unittest tests/test_mobile_controls_and_touch_ui.py
```

### Verification Criteria Checklist
- [x] Zero failing tests in `tests/`.
- [x] Headless display compatibility via `SDL_VIDEODRIVER="dummy"`.
- [x] Save isolation: saving/loading worlds never causes entity bleed.
- [x] Clean multiplayer client/server message serialization.
- [x] 100% offline standalone execution with zero external network dependencies.
