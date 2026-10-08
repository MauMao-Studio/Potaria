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

### Core Mechanics, World, & Engine Performance
- [x] **Boundless Open World**: Infinite horizontal coordinate generation without artificial boundary walls ($-\infty \leftarrow 0 \rightarrow +\infty$).
- [x] **Engine Performance & Chunk Streaming**: Asynchronous ThreadPool chunk generation. Chunk fetching never blocks the main thread, resulting in a solid 60+ FPS experience without 300ms stuttering when moving across chunk boundaries.
- [x] **Lighting Optimization**: 32-bit RGB integer mapping (`map_rgb`) and `absorb_grid` cache.
- [x] **Chunk Surface Baking**: `ChunkSection` bakes static tiles to 16x16 chunk surfaces to drastically reduce blit calls per frame.
- [x] **Tile Interaction**: Left-click mining, right-click block placement, background wall placement.

### Combat, RPG, & Visual Effects
- [x] **Chroisen Paperdoll & Thematic Sets**: Head, Chest, Legs, Weapon, and 6 Accessory slots. Armor sets grant pulsing visual auras and powerful stat buffs.
- [x] **Long-Range Weapons & Projectile Behaviors**: Ballistic physics for bows, homing catalysts, piercing rods, and expanding scepters.
- [x] **Skill System**: 40 unique abilities (Warrior, Ranger, Mage, Survival, Mobility).
- [x] **Multiplayer**: Host-authoritative LAN socket server for up to 5 players.

---

## 3. OUTSTANDING USER REQUESTS & ACTIVE TODOs (v1.1)

These are the immediate priorities requested for the next milestones:

### 3.1 Artstyle Rework & Visual Overhaul
- [ ] **Terraria x Stardew Valley Aesthetic**: Rework the global artstyle with rich pixel shading and warm palettes.
- [ ] **Unique Item Sprites**: Overhaul the procedural asset generator so upper-tier weapons and armor have grand, ornate silhouettes (crystalline blades, gilded engravings) rather than identical sprites.
- [ ] **Boss Design Polish**: Rework Lord Malus, Ignis Colossus, Cryo-Spud, Necro-Tuber, and Sol-Rho with multi-layered pixel shading, organic textures, and epic transitions.
- [ ] **Cute Terraria Trees**: Replace blocky bush trees with appealing rounded leafy canopies and organic bark. Player can only mine the wood trunk, not the leaves.
- [ ] **Animated Water & Swimming System**: Implement liquid water with animated surface waves, semi-transparent refraction. Add swimming physics, buoyancy, and an underwater oxygen meter.

### 3.2 UI / UX & Quality of Life
- [ ] **Create New World Polish**: Fix UI layout. Remove the "MODE: ADVENTURE" button from world creation.
- [ ] **Mods / Add-ons Menu**: Move game modes (e.g., "Last Man Standing" PvP) to a dedicated Mods/Add-ons menu accessible from the Main Menu.

### 3.3 Audio & Achievements
- [ ] **Cinematic BGM System**: Implement dynamic, cinematic synth BGM with smooth fade-in/out transitions across menus, day/night, biomes, and boss fights.
- [ ] **Achievement System**: Create `data/achievements.json`. Add an Achievement Browser to the Main Menu and trigger floating in-game popups when an achievement is unlocked (e.g., "Slayer of Titans").

---

## 4. MID-TERM CONTENT EXPANSION (v1.4 - v1.6)

### 4.1 Additional Biomes & World Expansion
- [ ] **Lush Jungle Biome**: Giant vine canopies, mud blocks, mahogany wood, Spud Wasps.
- [ ] **Floating Sky Islands**: Cloud blocks, high-altitude generation, Starfury chests.

### 4.2 Town NPCs & Housing Quest Engine
- [ ] **NPC Spawning Validation**: Check suitable housing conditions (table, chair, torch, door).
- [ ] **NPC Roster**: Farmer Spud, Blacksmith Spud, Wizard Spud, Alchemist Spud.
- [ ] **NPC Dialogue & Quests**: Multi-stage questlines awarding rare schematics.

---

## 5. LONG-TERM VISION & ENGINE SCALABILITY (v1.7 - v2.0)

### 5.1 Gamepad & Steam Deck Optimization
- [ ] **Gamepad Input System**: Full XInput and DirectInput support.
- [ ] **Radial Item & Skill Wheel**: Hold bumper to slow time and select skills.
- [ ] **Twin-Stick Aiming**: Right thumbstick cursor aiming.

### 5.2 Mobile & Touch Interface Polish
- [ ] **Virtual Dual Joysticks**: Left thumb movement; right thumb targeting/auto-swing.
- [ ] **Pinch-to-Zoom Camera**: Smooth multi-touch viewport scaling.

### 5.3 Extensible Modding API & Data Schemas
- [ ] **Data-Driven Definitions**: Move items, mobs, recipes, tiles, and skills to JSON schemas.
- [ ] **Lua / Python Plugin Hooks**: Event hooks for world_gen, player_hit, etc.
- [ ] **Custom Tile & Sprite Loader**: Hot-reloadable mod texture packs and sound banks.

---

## 6. AUTOMATED VERIFICATION & QA MATRIX

### Test Suite Execution
To run the automated regression suite across all systems:
```bash
# Run full suite
python -m unittest discover -s tests
```
- [x] Zero failing tests in `tests/`.
- [x] Headless display compatibility via `SDL_VIDEODRIVER="dummy"`.
- [x] Save isolation: saving/loading worlds never causes entity bleed.
- [x] 100% offline standalone execution with zero external network dependencies.
