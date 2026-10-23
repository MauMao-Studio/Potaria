# Potaria - The Spudtastic Adventure

**Developer:** Kurados  
**Active Engine:** Unity 6 LTS (v6000.0.58f1) + 2D Universal Render Pipeline (URP 17.0.3)  
**Legacy Engine Branch:** Pure Python 3.13 + Pygame Community Edition (`pygame-ce` 2.5.8+ with SDL 2.32, preserved on `pygame-engine` branch)  
**Architecture:** 2D Boundless Sandbox Action RPG & Multiplayer (FishNet / Steamworks P2P)  
**Franchise Model:** One Project Repository (Unified Codebase with Dual-Profile Architecture)  
**Verification Baseline:** 770 / 770 Pygame Tests Passing; 1,775 Unity ScriptableObjects Validated via Batchmode; 417 / 417 Unity Automated Tests Passing across 4 Suites (0 Errors, 100% Green)  
**Current Milestone:** Milestone 4 Complete (Inventory, Crafting, Equipment, Forge, Chest & Responsive UI); Milestone 5 in Planning  
**Version:** Unity 6 LTS Milestone 4  
**Master Parity Documentation:** [docs/PYGAME_TO_UNITY_FEATURE_PARITY_DOCUMENTATION.md](docs/PYGAME_TO_UNITY_FEATURE_PARITY_DOCUMENTATION.md)  

---

## 1. Overview

Potaria is an authentic Philippine-themed boundless 2D sandbox action RPG developed by Kurados. You play as Spud, an ordinary potato who sprouted with an extraordinary destiny. Explore an infinite, boundary-free open world populated by diverse biomes, mine valuable ores, discover hidden underground treasure chests, level up your RPG character from Level 1 to 100, equip tiered armor, weapons, and accessories in a classic Chroisen-style paperdoll system, wield ballistic bows, staves, rods, scepters, and celestial blades, cultivate native Philippine crops, master devastating Skill Book spells, trade with nomadic animated merchants, enhance your gear up to +7, carve custom affix sockets, dodge intricate bullet-hell danmaku patterns in boss gauntlets, and challenge the two-phase Grand Boss: SOL-RHO THE CELESTIAL TITAN - solo or in Cooperative Multiplayer (1 to 5 Players).

### Dual-Engine Development Strategy
To prepare Potaria for commercial release on Steam (PC/Mac/Steam Deck) and the Google Play Store (Android):
- **Active Development (`main` branch)**: Built on **Unity 6 LTS (v6000.0.58f1)** utilizing the 2D Universal Render Pipeline (URP), 2D Tilemap system, C# ScriptableObject architecture, and FishNet / Steamworks P2P networking.
- **Legacy Foundation (`pygame-engine` branch)**: The complete, working Python 3.13 + Pygame-ce implementation (with Smart OpenGL HAL, 770 automated unit tests, and full gameplay loop) is permanently preserved on the `pygame-engine` branch.

### Franchise Architecture: One Project Repository
- **Potaria (The Base Game)**: Boundless procedural sandbox survival, mining, building, 181 crafting recipes, Philippine agriculture, and seamless co-op multiplayer.
- **Potaria: Root Realm (The Flagship ARPG)**: Narrative episodic story campaign featuring chapter progression, Heartroot world transformation mechanics, the POTAdex journal, and curated subterranean puzzle dungeons.

### Master Feature Parity Reference & Architecture Guide
For the complete technical specification detailing every Python file, class, method, numeric formula, mechanics balance table, HUD layout, and migration audit status from the legacy Pygame codebase to the active Unity 6 LTS architecture, see:
- [Pygame to Unity Master Feature Parity Documentation](docs/PYGAME_TO_UNITY_FEATURE_PARITY_DOCUMENTATION.md)

---

## 2. Key Features (v1.6.0 Baseline)

### 2.1 Specialized Animated Traders & Nomadic Economy
- **Three Unique Animated Nomads**:
  - **Zephyrion the Wandering Peddler**: Wares trader selling up to 5 randomized weapons and equipment (rarities Common to Epic, aligned with world drop rates).
  - **Ignis Vance the Forge Master**: Equipment enhancer offering weapon and armor upgrades from +1 to +7, and master repairs.
  - **Morrigan the Void Weaver**: Enchantress carving specialized affix slots onto Legendary and Ancient gear using rare Affix Stones.
- **Mutual Exclusion & Rarity**: Only one trader exists in the world at a time. Spawns occur rarely, far from player shelters, and last for a limited time to encourage active exploration.
- **Turtle Shell Shield Defense**: When any hostile entity enters within a 3-block radius (96 pixels), the trader withdraws into an invulnerable turtle shell defense barrier, deflecting all damage and disabling trading until the perimeter is cleared.
- **1 Gold Gear Restoration**: Broken items (+5 to +7 failed enhancements) can be repaired by any trader for a flat fee of 1 Gold Coin (10,000 Copper).
- **Interactive Shop UI**: Hover tooltips show full gear stats, enhancement levels, and affix details matching inventory inspection.

### 2.2 Item Enhancement (+1 to +7) & Affix Carving
- **Item Enhancement (+1 to +7)**:
  - Weapons and armor can be upgraded up to +7 at the Forge Master.
  - Baseline attributes scale up to +100% (double stats) at +7.
  - Safe progression from +1 to +4. Levels +5 to +7 carry a risk of breaking the item, requiring trader restoration.
- **Affix Slot Carving**:
  - Exclusive to Legendary and Ancient rarity gear.
  - Consumes an Affix Stone (crafted at the Work Bench from rare diamonds, mythic dust, and boss remnants).
  - Replaces a randomly selected secondary stat with an open Affix Slot granting specialized offensive or defensive modifiers.

### 2.3 Touhou-Inspired Bullet-Hell Boss Danmaku
- **Geometric Danmaku Bullet Patterns**: Bosses execute multi-wave geometric projectile patterns including 16-way spiral novas, rotating celestial cross beams, and targeted rings with micro-gaps.
- **Fair Lethal Hitbox (52% Core)**: Projectile collision is concentrated in the inner 52% of the visual sprite radius, eliminating unfair edge hits.
- **Perimeter Graze Mechanic**: Skimming close to lethal enemy projectiles (within 100% to 175% of radius) triggers visual graze sparks, an audio chime, and awards +1 Mana (MP), incentivizing bold micro-dodging during combat.

### 2.4 Minecraft-Style 5-Category Crafting Book & 129 Craftables Catalog
- **Categorized Crafting Navigation**:
  - 1. Building Blocks (planks, bricks, glass, roof shingles, platforms).
  - 2. Equipment & Tools (swords, bows, composite bows, pickaxes, axes, armor).
  - 3. Consumables & Alchemy (potions, meals, golden french fries, arrows).
  - 4. Furniture & Housing (tables, chairs, beds, clocks, fireplaces, dressers, chests).
  - 5. Miscellaneous & Raw (affix stones, portal shards, ingots, textiles).
- **Craftable Storage Chests**: Multi-slot chests for organized world item storage.
- **Dedicated Asset Architecture**: All 129 craftable item sprites are stored exclusively in `assets/craftable_items/`, cleanly separated from the 1,337 droppable items in `assets/items/`.

### 2.5 Combat Rebalance & Single-Target Rules
- **Single-Target Enforcement**: Melee swings and standard ballistic projectiles damage at most 1 enemy per attack, preventing starter weapons from wiping out mobs in one blow.
- **Ancient Relic Multi-Target Exceptions**: Ancient and Mythic weapons (e.g. Celestial Greatsword, Ancient Composite Bow, Astral Wrath) retain cleave, piercing, and area-of-effect damage.
- **Subterranean Mini-Boss Placement**: Mini-bosses are restricted to underground dungeons and dedicated lairs; random surface night spawns are eliminated.
- **Nightly Elite Champion**: A single enlarged elite monster spawns once per night with 2.5x-3.5x HP, custom visual scale, and a unique combat skill.
- **Bed Proximity Safety Check**: Sleeping in a bed is only permitted at night when no hostile monsters are within a 6-block radius (192 pixels).

### 2.6 Environment Physics & World Quality of Life
- **Torch Support Physics**: Torches cannot float in mid-air or be placed underwater; they require a supporting solid block or background wall.
- **Auto-Hiding Word-Wrapped Console & Chat**: In-game chat and command feedback format with automatic word wrapping in an unobtrusive box that fades after inactivity.
- **World Selection History**: Displays total accumulated playtime in hours and the exact timestamp of the last played session.
- **Dedicated Coin Purse**: Currency stored independently of the 40-slot backpack (100 Copper = 1 Silver, 100 Silver = 1 Gold).
- **Tool Tier Harvesting Speeds**: Progressive block breaking speeds based on tool tier, with bare-hand harvesting as an anti-softlock backup.

### 2.7 Renderer Hardware Abstraction Layer (HAL) & Stage 2 ModernGL Visuals
- **Modular Renderer HAL**: Decoupled rendering architecture via abstract `BaseRenderer` interface with unified drawing operations (`draw_sprite`, `draw_surface`, `draw_rect`, `draw_text`, `draw_line`, `draw_circle`, `clear`, `present`, `get_surface`, `draw_projectiles_batch`).
- **SurfaceRenderer**: Native Pygame-ce software blitting engine guaranteeing 100% backward compatibility, exact visual parity, and fast multi-blitting (`fblits`) for projectile batches.
- **Smart OpenGL Fallback Engine (`GLRenderer`)**: Hardware-first ModernGL backend with safe context initialization, texture caching, single-log fallback deduplication, and automatic fallback to `SurfaceRenderer` whenever OpenGL drivers or libraries are missing.
- **GLSL Bloom Post-Processing Shader Pipeline**: Hardware post-processing fragment shader with dynamic luminance extraction, 2D Gaussian kernel blur, and radiant pulse shimmer for Ancient gear auras, celestial trails, and boss danmaku projectiles.
- **High-Density Projectile Batch Rendering**: Dedicated `draw_projectiles_batch` optimizing hundreds of active bullet-hell projectiles with viewport frustum culling, integrated directly into boss danmaku barrages.
- **In-Game Video Settings Toggle**: Interactive toggles for Renderer (`[Hardware (ModernGL) / Compatibility (Software)]`) and Bloom Shaders (`[BLOOM SHADERS: ON / OFF]`) with disk persistence in `saves/settings.json`.

---

## 3. High-Definition Visuals & Audio Engine

1. **High-Definition (HD) Fullscreen Scaling**:
   - Configured with `SDL_RENDER_SCALE_QUALITY = "best"` hardware texture interpolation, ensuring crisp UI, high-definition fonts, and smooth presentation across 1080p, 1440p, and 4K fullscreen displays (`F11`).
2. **Traditional Articulated Animation**:
   - 8-frame walk cycles with squash/stretch dynamics and sprout physics.
   - 6-frame idle breathing and natural blinking.
   - Dynamic jump upward stretch and aerodynamic downward falling frames.
   - Complete bestiary animation sets: slimes, zombies, night gazers, bats, and crawlers.
3. **Sub-Pixel Floating Point Physics (`pygame.FRect`)**:
   - Eliminates rounding jitter on slopes, jumps, and high-velocity dashes.
4. **Ballistic Projectiles & Magic Weapons (`pygame.math.Vector2`)**:
   - Parabolic gravity arcs for archery bows.
   - Homing celestial stars for catalysts, piercing javelins for rods, elemental bolts for staves, and radial shockwaves for scepters.
5. **Cinematic Multi-Track Procedural Synth Audio (`pygame.mixer`)**:
   - Multi-voice orchestral loops synthesized in pure Python with dynamic crossfading across biomes, caverns, subterranean mini-bosses, and Grand Boss Sol-Rho.
   - True 2-channel stereo sound effects with distance falloff and directional panning.
6. **Optimized Cellular Lighting**:
   - Dynamic cellular lighting with time-of-day color grading: amber dawn/dusk, sapphire moonlit nights, radiant midday sunlight, and eerie violet dungeon ambiance.

---

## 4. The Story & Dungeon Progression

> In the ancient starchlands of Potaria, the subterranean Nether Dungeon holds the ancient secrets of the cosmos. Cursed overlords guard the deep caverns, but they are merely gatekeepers.
>
> Defeating subterranean Mini-Bosses yields mystical Portal Shards. When 4 Portal Shards are united with gold and stone bricks at a Work Bench, they fuse into the Celestial Keystone.
>
> Channeling the Keystone summons the ultimate supreme deity of the heavens: SOL-RHO THE CELESTIAL TITAN. Only heroes who can survive his devastating two-phase onslaught — shattering his golden solar form and vanquishing his Awakened Void Incarnate — can earn True Victory and claim the divine Crown of Potaria!

---

## 5. Infinite Open World & Diverse Biomes

Potaria features an asynchronous chunk streaming engine (`ChunkManager`). World chunks (16 tiles wide by 240 tiles deep) are dynamically synthesized on the fly using continuous multi-octave seeded Perlin noise without artificial left or right bedrock walls.

### Biomes of Potaria:
1. **The Forest (Starchlands)**:
   - Rolling hills covered in green grass, wild potato bushes, oak trees, and daytime ambient sunlight.
   - Inhabitants: Green Slimes, Purple Slimes, surface Zombies, Night Gazers at night.
2. **The Desert**:
   - Dunes of golden sand and subterranean sandstone studded with prickly cacti.
   - Inhabitants: Sand Slimes, Desert Scorpions, Mummies.
3. **The Snow Biome**:
   - Frost-covered snow hills and subterranean slippery ice formations.
   - Inhabitants: Frost Slimes, Frozen Zombies, Ice Bats.
4. **The Corruption (The Blight)**:
   - Malignant biome characterized by corrupt grass, dark purple ebonstone, and sinister foliage.
   - Inhabitants: Corrupt Slimes, Shadow Crawlers, Night Gazers.
5. **Glowing Mushroom Caverns**:
   - Underground cavern pockets overgrown with luminescent mushroom grass and giant glowing blue mushrooms that emit natural cellular light.
   - Inhabitants: Cave Bats, Skeletons, Slimes.
6. **The Nether Dungeon**:
   - Deep subterranean fortress constructed of indestructible dungeon brick, housing ancient altar arenas.
   - Inhabitants: Lord Malus the Blight-Bringer, Ignis Colossus, Cryo-Spud, and Necro-Tuber.

---

## 6. Bestiary, Mini-Bosses & The Grand Boss

| Monster / Boss | Biome / Location | Behavior & Abilities | Primary Drops |
|---|---|---|---|
| **Green Slime** | Forest Surface | Bounces toward player | Gel, Raw Potato, Healing Potion |
| **Purple Slime** | Forest / Night | Aggressive, higher jump | Gel, Potions, Copper Ore |
| **Sand Slime** | Desert | Camouflaged bouncing | Gel, Sand Blocks, Swiftness Potion |
| **Frost Slime** | Snow Biome | Chilling leap attack | Gel, Frost Core, Ice Blocks |
| **Corrupt Slime** | The Corruption | Fast, venomous bounce | Gel, Ebonstone, Shadow Cleaver |
| **Surface Zombie** | Forest / Night | Relentless shambling | Copper Ore, Potatoes, Skill Books |
| **Frozen Zombie** | Snow / Night | High durability, slow | Frost Core, Iron Ore, Frost Hood |
| **Desert Mummy** | Desert Caverns | Rapid pursuit | Sandstone, Gold Ore, Sandstorm Spear |
| **Skeletal Warrior**| Caverns (Underground) | Tough, high knockback | Bones, Iron Ore, Bone Bow |
| **Night Gazer** | Night Sky (Flying) | Swooping aerial charges | Torches, Lenses, Warrior Charm |
| **Cave Bat** | Deep Caverns | Erratic flight in the dark | Torches, Lucky Clover |
| **Ice Bat** | Snow Caverns | Freezing flight dive | Frost Core, Talisman of Vigor |
| **Desert Scorpion** | Desert Surface/Caves | Fast crawling strike | Cactus, Poison Glands, Hermes Boots |
| **Shadow Crawler** | Corruption Deep | Wall-climbing ambush | Ebonstone, Dark Essences |
| **Nightly Champion**| Overworld Surface | Enlarged elite with unique skill | High EXP, Gold Coins, Rare Gear |
| **Lord Malus** | Nether Dungeon Crypt | Blight orbs, sweeping cleave | Nether Portal Shard, Nether Cleaver |
| **Ignis Colossus** | Magma Cavern Lair | Magma bombs, seismic slams | Magma Portal Shard, Magma Greatsword |
| **Cryo-Spud** | Glacial Permafrost | Frost shards, blizzard breath | Frost Portal Shard, Frost Blade |
| **Necro-Tuber** | Subterranean Catacomb | Ghost skulls, bone whirl | Shadow Portal Shard, Bone Scythe |
| **SOL-RHO (Phase I)**| Celestial Sky Summon | Solar Titan: 16-way danmaku, solar flare | Resurrects into Phase II |
| **AWAKENED SOL-RHO (Phase II)**| Cosmic Void Arena | Void Incarnate: Singularity vortex, bullet curtains | Crown of Potaria, Celestial Greatsword, Astral Wrath |

---

## 7. Chroisen-Style RPG Equipment & Progression

- **Character Statistics (Level 1–100)**:
  - Slaying monsters and bosses earns EXP. Leveling up permanently increases Base HP, Base MP, Base ATK, Base DEF, and grants a full heal.
  - Natural MP regeneration fuels active combat skills; bullet grazing grants +1 MP per projectile.
  - Defense Mitigation: $\text{Damage Taken} = \max(1, \text{Enemy ATK} - \text{Player DEF})$.
  - Critical Hits deal 180% damage with golden damage popups and screen shake.
- **Paperdoll Armor Slots (`C` Key)**:
  - Head, Chest, Legs, and 6 Accessory slots.
  - Thematic 3-piece sets (Ancient Resonating, Celestial Titan, Magma Core, Cryo Carapace, Umbral Shadow, Spud Sovereign, Cactus Needle) grant radiant pulsing visual auras and substantial stat bonuses.
- **Weapon Hotbar Equipping**:
  - Weapons do not occupy paperdoll slots; place any weapon into hotbar slots (1–9, 0) to equip it dynamically.

---

## 8. Skill Grimoire & Combat Spells

- **Skill Books & Upgrades (Level 1 to 5)**:
  - Reading a Skill Book unlocks the ability into your Grimoire (`C` key). Reading duplicates levels up the skill up to Lv. 5.
- **Active Hotkeys (`Q`, `F`, `V`, `R`)**:
  - `Q` — Power Slash: Heavy forward cleave.
  - `F` — Whirlwind: 360-degree spinning strike.
  - `V` — Swift Dash: High-speed dash with invincibility frames.
  - `R` — Fireball: Explosive fire orb detonating upon impact.
- **Grand Legendary Spells**:
  - Meteor Strike: Cosmic meteor barrage dealing massive damage.
  - Celestial Shield: Divine aegis granting complete invulnerability for 4.5 seconds.
  - Frost Nova: Glacial 360° freeze detonation slowing and damaging all surrounding foes.

---

## 9. LAN Cooperative Multiplayer (1 to 5 Players)

- **Pure Python Networking**: Built entirely on standard library `socket` and `threading` with zero external drivers required.
- **Authoritative LAN Host**: Launch Potaria -> LAN Multiplayer -> Host LAN Game. Binds to port `25565` and syncs world seed automatically.
- **Instant Client Join**: Other PCs on the same Wi-Fi or Ethernet choose Join LAN Game and enter the host IP address.
- **Synchronized Systems**:
  - Party HUD displaying player health bars and levels for up to 5 members.
  - Remote potato avatars showing movement, facing, swinging, and badges.
  - Real-time block modification deltas.
  - Integrated party chat with auto-wrapping text.
  - Dynamic boss health scaling (+40% HP per additional player).

---

## 10. Complete Controls

| Action | Primary Key | Notes |
|---|---|---|
| **Move Left / Right** | `A` / `D` | Rebindable in Settings -> Controls |
| **Jump** | `Space` / `W` | Rebindable in Settings -> Controls |
| **Drop Through Platform** | `S` | Drops down through wooden platforms |
| **Mine / Attack** | `Left Click` (Hold) | Continuous mining / weapon swinging |
| **Place Block / Interact** | `Right Click` (World) | Places selected item or interacts with objects |
| **Drop Item from Backpack** | `Q` / `Backspace` / `G` | Drops hovered item into the world |
| **Toggle Mini-Map Radar** | `M` | Real-time corner mini-map |
| **Character Panel & Grimoire** | `C` | Paperdoll gear, stats, and Grimoire |
| **Backpack & 5-Category Crafting** | `E` | Opens 40-slot inventory and categorized crafting book |
| **Quick Equip / Learn Skill** | `Right Click` in Bag | Equips armor or learns Skill Book |
| **Active Combat Skills** | `Q`, `F`, `V`, `R` | Configurable in Character Panel (`C`) |
| **Toggle Fullscreen** | `F11` | Seamless HD hardware-scaled fullscreen |
| **Developer Console / Chat** | `Enter`, `/`, `~` | In-game command and chat console |
| **Select Hotbar Slot** | `1` to `9`, `0` | Cycles through active hotbar slots |
| **Pause Game** | `P` / `Esc` | Opens pause menu with Settings and Save & Quit |
| **Profiler Overlay** | `F3` | Real-time subsystem performance breakdown |

---

## 11. Automated Regression & System Verification

Potaria maintains rigorous multi-tier verification across both engine baselines:

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

### Key Test Coverage:
1. Procedural generation & chunk baking (`test_game.py`).
2. LAN multiplayer synchronization & boss scaling (`test_lan_hud_mobs_scaling.py`).
3. Liquid water physics & oxygen meter (`test_water_oxygen_swimming.py`).
4. Cutscene engine & typewriter audio (`test_cutscene_engine.py`, `test_voice_and_audio.py`).
5. Touch controls & mobile ergonomics (`test_mobile_controls.py`).
6. Archery ballistics, magic weapons & cheats (`test_combat_overhaul_and_cheats.py`).
7. Profiler timing & cellular lighting (`test_performance_and_profiler.py`, `test_lighting_and_victory_fixes.py`).
8. Tool tiers, bare-hand harvesting & balance (`test_tool_tier_and_bare_hand.py`, `test_item_descriptions_and_balance.py`).
9. Single-target melee & ballistic rules (`test_single_target_combat.py`).
10. Dungeon mini-bosses, bed proximity & nightly champion (`test_nightly_elite_and_dungeon_bosses.py`).
11. Specialized animated traders, enhancements & affixes (`test_random_trader_and_features.py`).
12. Minecraft-style 5 crafting categories & 129 items (`test_crafting_categories_and_items.py`).
13. Touhou bullet-hell danmaku, 52% core & grazing (`test_danmaku_bullet_hell.py`).
14. Turtle shield, hover UI, torch physics & craftable assets (`test_traders_ui_and_torch_rules.py`).
15. World isolation & multiplayer integrity (`test_world_bleed_multiplayer_effects_assets.py`).
16. Renderer HAL, BaseRenderer, SurfaceRenderer, GLRenderer fallback, and Video Settings toggle (`test_renderer_hal.py`).
17. Phase 1 Data-Driven Item Registry (1,461 items), 4-layer item model, 9 canonical affixes, 3-path loot tables, and Word/PDF visual item catalogs (`test_loot_and_affix_phase1.py`).

---

## 12. Strategic Technical Roadmap (Unity 6 LTS Implementation)

The production roadmap transitions Potaria from the verified Pygame foundation into an enterprise-grade Unity 6 LTS multiplatform release:

### Milestone 1: Project Scaffold, Asset Ingestion & Core Data Layer (COMPLETED)
- Configured Unity 6 LTS (v6000.0.58f1) with 2D URP 17.0.3, 2D Tilemap, and Input System.
- Created standalone backup and published `pygame-engine` archival branch to origin.
- Ingested 2,456 pixel-art sprites into `Assets/Sprites/` (16 PPU, Point filter) and 34 audio files into `Assets/Audio/`.
- Generated 36 new crop growth stage sprites in `Assets/Sprites/Crops/`.
- Created typed C# data models in `Assets/Scripts/Data/`.
- Implemented headless batchmode importer generating 1,775 verified ScriptableObjects (0 broken references).

### Milestone 2: 2D Tilemap, Chunk Streaming & Procedural World Generation (COMPLETED)
- Dual-tilemap architecture: Terrain Tilemap (solid foreground) and Wall Tilemap (ambient background).
- Chunk streaming manager handling dynamic generation and culling around the camera.
- Multi-octave Perlin noise generation for Forest, Desert, Snow, Blight, and Nether Dungeon biomes.
- RuleTiles / Terrain Tile palettes for 117+ block types with smooth autotiling.
- 2D URP lighting integration (Day/Night global light cycling and subterranean torch point lights).

### Milestone 3: Character Controller, Physics & Action RPG Combat (COMPLETED)
- Rigidbody2D + BoxCollider2D player controller with responsive jump physics, coyote time, and jump buffering.
- Unity Input System actions supporting Keyboard/Mouse, Gamepad (Steam Deck / Xbox / DualSense), and Touch.
- 100-level RPG stat progression curve (HP, MP, ATK, DEF, Crit Rate).
- 40 Skill Book abilities with VFX, cooldowns, and bullet-reflection mechanics (`Celestial Reversal`).
- Danmaku boss combat system with 52% core lethal hitboxes and perimeter grazing (+1 MP).

### Milestone 4: Inventory, Crafting, Equipment & Responsive UI (COMPLETED)
- 40-slot backpack inventory (`PlayerInventory.cs`, `InventoryUI.cs`, `E` key) with item stack dragging, splitting, quick-trash/drop, auto-sort, and `[ORGANIZE]` gap compaction.
- 10-slot paperdoll equipment and character panel (`PlayerEquipment.cs`, `CharacterPanelUI.cs`, `C` key) with immediate `PlayerStats` recalculation and active 27 equipment set milestone bonuses (2-piece, 4-piece, 5-piece).
- Dedicated coin purse UI with real-time Copper, Silver, and Gold auto-conversion (100:1 conversion, 10,000 Copper = 1 Gold).
- 5-category crafting interface (`CraftingUI.cs`) with 4-block station proximity filtering (Hand, Workbench, Furnace, Anvil, Cooking Pot / Campfire), material sufficiency highlights, and one-click crafting.
- Side-by-side equipment comparison tooltip ("Katabi", `KatabiTooltipUI.cs`) with `[ CURRENTLY EQUIPPED ]` badges, TextMeshProUGUI, screen clamping, circular affix sockets `(●) / (○)`, weapon perks, and stat diffs.
- Forge Master enhancement (+1 to +7) with failure/break risk curves and stat scaling up to 2x at +7, 1 Gold (10,000 Copper) repair UI, and affix stone carving/embedding (`ForgeSystem.cs`, `ForgeUI.cs`).
- 30-slot storage chest container entity and modal UI (`StorageChest.cs`, `ChestUI.cs`) with Quick-Deposit and Loot-All.
- Bottom-left food buff HUD overlay with hover tooltips and remaining duration meters.

### Milestone 5: Philippine Farming, Tiered Cooking & Fishing Minigame
- 4-stage visual growth progression for 9 crops with hydration dynamics and subterranean cave lighting.
- Timed furnace cooking queues (2.5s-20.0s) with single-food-per-furnace limit and direct fish grilling.
- 12.0s tension-based fishing minigame with moving golden sweet spot and escape penalty.

### Milestone 6: Steamworks Integration & P2P / LAN Multiplayer
- FishNet / Steamworks P2P networking for 1-5 player cooperative multiplayer.
- Automatic Steam lobby matchmaking, friend invites, and direct LAN IP fallback.
- Client-side prediction and host-authoritative block modification deltas.
- Steam Achievements, Cloud Saves, and Steam Deck verification.

### Milestone 7: Multiplatform Commercial Release (Steam & Google Play Store)
- Production Windows/macOS/Linux Steam builds.
- Google Play Store Android AAB export with Scoped Storage, adaptive framerate (60/120 Hz), and touch virtual controls.

---

## 13. Getting Started & How to Run

### Option A: Unity 6 LTS (Active Main Branch)

#### Prerequisites:
- **Unity Hub** installed.
- **Unity 6000.0.58f1 (Unity 6 LTS)** installed with:
  - Windows / Mac / Linux Build Support
  - Android Build Support (OpenJDK, Android SDK & NDK tools)

#### Opening the Project:
1. Clone the repository:
   ```powershell
   git clone https://github.com/MauMao-Studio/Potaria.git
   ```
2. Open Unity Hub, click **Add project from disk**, and select the `Potaria` directory.
3. Select Editor Version **6000.0.58f1**.
4. Unity will resolve dependencies via `Packages/manifest.json`.
5. All ScriptableObjects and assets are pre-imported and ready to inspect in `Assets/Data/` and `Assets/Sprites/`.

#### Re-running the Data Importer (Optional):
In the Unity Editor menu bar, select:
`Potaria -> Import All Data from Pygame`
Or run headlessly via command line:
```powershell
Unity.exe -batchmode -quit -projectPath . -executeMethod PotariaDataImporter.ImportAll -logFile -
```

---

### Option B: Pygame-CE Legacy Engine (Archival Branch)

The complete Python 3.13 + Pygame-ce game is preserved on the `pygame-engine` branch:

#### Running the Legacy Build:
```powershell
git checkout pygame-engine
python -m venv .potaria_venv
.potaria_venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

#### Running the Pygame Automated Test Suite:
```powershell
pytest
# Verified: 770 passed across 47 suites (100% Green)
```

---

## 14. Credits

- **Game Developer & Lead Architect:** Kurados
- **Lead Protagonist:** Spud the Potato Hero
- **Antagonist:** Lord Malus the Blight-Bringer
- **Cosmic Ruler:** Sol-Rho The Celestial Titan
- **Audio & Sound Synthesis:** Pure Python Procedural Sound Synthesizer by Kurados
