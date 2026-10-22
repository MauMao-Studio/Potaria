# Potaria & Potaria: Root Realm
## Master Game Design Document (GDD)

**Developer:** Kurados  
**Genre:** 2D Sandbox Action RPG  
**Subgenre:** Survival | Exploration | Crafting | Dungeon Crawler | Character Progression | Bullet-Hell Danmaku | Cooperative Multiplayer  
**Perspective:** 2D Side-View  
**Core Inspirations:** Terraria (world sandbox and building), Chroisen (paperdoll equipment and skill trees), Touhou Project (bullet-hell danmaku patterns)  
**Target Platforms:** PC (Steam / Steam Deck / Standalone) and Mobile (Google Play Android)  
**Active Engine:** Unity 6 LTS (v6000.0.58f1) + 2D Universal Render Pipeline (URP 17.0.3)  
**Legacy Engine Branch:** Pure Python 3.13 + Pygame-ce 2.5.8 (Preserved on `pygame-engine` branch, 100% Offline Standalone)  
**Franchise Model:** One Project Repository (Unified Codebase with Dual-Profile Architecture)  
**Player Modes:** Single-Player and 1-5 Player Cooperative Multiplayer (FishNet / Steamworks P2P)  
**World Structure:** Infinite procedurally generated chunk-based open world + Subterranean Dungeon Arenas  
**Document Version:** Unity 6 LTS Architecture Edition  

---

# 1. Game Vision & Design Pillars

The Potaria franchise operates under a unified **One Project Repository** architecture with a dual-profile structure:
- **Potaria (The Base Game)**: The boundless 2D sandbox survival and building experience where players explore infinite procedural terrain, harvest resources, craft across a 129-recipe catalog, construct modular settlements, and engage in casual LAN co-op and Last Man Standing (LMS) arenas.
- **Potaria: Root Realm (The Future Flagship ARPG & Story Franchise)**: The narrative-driven campaign experience featuring structured episodic chapters, the Heartroot world transformation system, the comprehensive POTAdex journal, curated subterranean puzzle dungeons, and dramatic boss encounters.

In both profiles, players embody **Spud**, an ordinary potato who sprouted with an extraordinary destiny to cleanse the realm of subterranean corruption and celestial blight.

### Core Design Pillars:
1. **Boundless Freedom**: Infinite multi-octave chunk generation without artificial boundary walls (-infinity <-- 0 --> +infinity).
2. **Deep RPG Progression**: 100-level character curve, dynamic enemy scaling, equipment enhancement up to +7, affix carving, and 40 skill abilities.
3. **High-Stakes Combat & Danmaku Precision**: Single-target weapon enforcement paired with Touhou-inspired bullet-hell boss encounters, micro-dodging (52% fair lethal core), and perimeter grazing (+1 MP).
4. **Vibrant Settlement & Nomadic Trading**: Specialized animated traders that roam the world, retreat into turtle shell defenses when threatened, and offer gear enhancements and 1-Gold repairs.
5. **Categorized Crafting Depth**: Minecraft-inspired 5-category crafting interface supported by a dedicated asset pipeline isolating craftable gear from droppable items.
6. **Modern 2D URP Engine Architecture**: Hardware-accelerated 2D Universal Render Pipeline (URP) with 2D Lights, PixelPerfectCamera (16 PPU), ScriptableObject data architecture, and multiplatform export to Steam and Google Play Store, with legacy Pygame-ce engine preserved on `pygame-engine` branch.

---

# 2. Lore & Narrative Setting

### 2.1 The Golden Age of Sol-Rho & The Spud Civilization
Long ago, the fertile starchlands of Potaria flourished under the celestial warmth of Sol-Rho and the cosmic resonance of the Celestial Keystone. Vegetable kind thrived in subterranean groves and sprawling surface settlements.

### 2.2 The Celestial Cataclysm & The Sundering
An ancient ambition fractured the Celestial Keystone into four elemental Portal Shards. The cataclysm plunged the starchlands into turmoil:
- Lord Malus, the Blight-Bringer, claimed the subterranean Nether Crypts.
- Ignis Colossus arose from molten magma rifts deep beneath the crust.
- Cryo-Spud entrenched himself within the permafrost glaciers of the north.
- Necro-Tuber harnessed necrotic decay within forgotten crypts.

### 2.3 The Prophecy of the Chosen Tuber
Awakened from the fertile loam with a glowing sprout, Spud is tasked with descending into the subterranean dungeons, slaying the four elemental overlords, reuniting the Portal Shards into the Celestial Keystone, and challenging the cosmic architect: **Sol-Rho The Celestial Titan**.

---

# 3. Character Attributes & Progression

Spud's attributes follow a calibrated 100-level progression curve:

| Attribute | Base Value | Progression / Scaling Formula | Tactical Function |
|---|---|---|---|
| **Level** | 1 | Level 1 to 100 max; siphons EXP from monster takedowns | Core progression tier |
| **HP (Health)** | 100 | Scaled by Base HP + Armor + Set Bonuses + Enhancements | Zero HP triggers downed/respawn state |
| **MP (Mana)** | 50 | Base 1.8 MP/s regen; boosted by gear, passives, and bullet grazing | Fuels active skills and spellcasting |
| **ATK (Physical)** | 10 | Primary multiplier for melee weapons, bows, and tools | Determines raw damage before enemy defense |
| **DEF (Defense)** | 2 | Mitigates incoming damage: $\max(1, \text{Enemy ATK} - \text{DEF})$ | Flat reduction of physical damage |
| **Crit Rate** | 5.0% | Chance to deal 1.8x golden critical strikes with screen shake | Burst damage mechanic |
| **Movement Speed**| 3.0 | Boosted by boots, buffs, and agility affixes | Traversal and combat dodging velocity |
| **Attack Speed** | 1.0x | Modifies swing cooldowns and spellcasting channels | Deliberate combat cadence |

### Dynamic Enemy Scaling
To maintain engaging gameplay across the 100-level journey, hostile enemies scale dynamically based on the player's level and equipment score:
- Enemy HP scales smoothly: $\text{Base HP} \times (1.0 + 0.08 \times \text{Player Level})$.
- Enemy Attack scales modestly: $\text{Base ATK} + 0.75 \times \text{Player Level}$.
- Tools have reduced combat damage to prevent starter axes and pickaxes from trivializing early combat.

---

# 4. RPG Equipment, Enhancements & Affixes

Equipment is managed through a comprehensive paperdoll layout (`C` key):
- **Armor Slots**: Head, Chest, Legs.
- **Weapon Slot**: Active hotbar hand slot with on-sprite rendering.
- **Accessory Slots**: 6 dedicated slots (rings, amulets, boots, charms, shields).
- **Dedicated Coin Purse**: Currency stored independently of the 40-slot backpack (100 Copper = 1 Silver, 100 Silver = 1 Gold).

### 4.1 Thematic Equipment Sets & Visual Auras
Equipping a full 3-piece matching armor set unlocks powerful passive bonuses and activates a continuous radiant visual aura:

| Set Name | Pieces Required | Set Bonus Effects | Active Visual Aura |
|---|---|---|---|
| **Ancient Resonating Set** | Ancient Helmet, Chestplate, Greaves | +35% ATK, +30% DEF, +50 Max HP, +20% Crit Rate | Pulsing golden-crimson celestial aura with orbiting starlight motes |
| **Celestial Titan Set** | Titan Helmet, Chestplate, Greaves | +25% DEF, +30 Max HP, +15% ATK | Celestial blue aegis ward with defensive energy halos |
| **Magma Core Set** | Magma Helmet, Chestplate, Greaves | +20% ATK, +15 Reflected Fire Thorns, +25 HP | Fiery orange molten aura with rising embers |
| **Cryo Carapace Set** | Cryo Helmet, Chestplate, Greaves | +20% DEF, +2.5 MP/s Regen, +35 HP | Cyan permafrost glacial aura with freezing motes |
| **Umbral Shadow Set** | Shadow Helmet, Shadow Plate, Shadow Greaves | +20% Crit, +20% ATK, +0.2 Move Speed, +20 HP | Dark violet void phantom aura |
| **Spud Sovereign Set** | Potato Cap, Potato Tunic, Potato Pants | +30 Max HP, +5 HP/s Regen, +10% ATK, +10% DEF | Emerald green botanical aura |
| **Cactus Needle Set** | Cactus Helmet, Chestplate, Greaves | +15 Reflected Thorns, +10% ATK, +10% DEF | Prickly amber desert spine aura |

### 4.2 Item Enhancement System (+1 to +7)
At the Forge Master trader (Ignis Vance), weapons and equipment can be enhanced up to +7:
- **Stat Growth**: Each enhancement level grants approximately +14% baseline stats, reaching +100% (double stats) at +7.
- **Safe Threshold (+1 to +4)**: Upgrades up to +4 have no risk of item breakage.
- **Danger Threshold (+5 to +7)**: Upgrades carry a failure risk that can crack and break the item:
  - +5: 45% Success, 35% Safe Failure, 20% Break.
  - +6: 30% Success, 35% Safe Failure, 35% Break.
  - +7: 18% Success, 32% Safe Failure, 50% Break.
- **Broken Gear State**: A broken item becomes unusable in combat until repaired by a trader.
- **Trader Restoration**: Any trader can restore broken gear to working order for a flat fee of **1 Gold Coin** (10,000 Copper).

### 4.3 Affix Slot Carving
At the Void Weaver trader (Morrigan), players can modify Legendary and Ancient items:
- Consumes an **Affix Stone**, an endgame catalyst crafted at the Work Bench from rare diamonds, mythic dust, and boss remnants.
- Affix carving replaces a randomly selected secondary stat on the item with an open Affix Slot, rolling from exclusive offensive and defensive modifiers (e.g. Life Steal, Movement Speed, Elemental Pierce, CDR).

### 4.4 Economy & Rarity Drop Rates
- **Common (98.69%)**: Standard drops and basic craftables.
- **Uncommon (1.0%)**: Mildly boosted equipment (+1 minor affix).
- **Rare (0.25%)**: Specialized combat gear (+2 affixes).
- **Epic (0.05%)**: High-tier equipment (+3 affixes).
- **Mythic (0.008%)**: Subterranean dungeon boss drops.
- **Legendary (0.002%)**: Unique active weapon abilities.
- **Ancient (0.0004%)**: 1 in 250,000 ultra-rare relics triggering celebratory fanfare, screen shake, and the Ancient discovery achievement.

---

# 5. Combat Archetypes, Ballistics & Bullet-Hell Encounters

### 5.1 Weapon Archetypes
1. **Melee Blades (Shortswords, Broadswords, Greatswords, Axes)**:
   - Cadenced swing arcs with recovery cooldowns ($0.22\text{s}$ to $0.46\text{s}$).
   - **Single-Target Enforcement**: Melee swings damage at most 1 enemy per attack.
   - **Ancient Cleave Exception**: Ancient melee weapons (e.g. Celestial Greatsword, Astral Wrath) cleave through all enemies in their swing arc.
2. **Ballistic Archery (Shortbows, Recurves, Longbows, Composite Bows)**:
   - Parabolic gravity trajectory ($g = 140\text{ px/s}^2$).
   - Ammunition hierarchy: Astral Arrow > Frostburn Arrow > Flame Arrow > Wooden Arrow.
   - Standard arrows terminate on the first entity struck; Ancient bows fire piercing starlight volleys.
3. **Magic Catalysts**:
   - Fires homing celestial stars with autonomous steering toward the nearest threat (560px range cap).
4. **Magic Staves**:
   - Concentrated elemental bolts (Fire, Frost, Nature, Arcane) inflicting status ticks (560px range cap).
5. **Magic Rods**:
   - High-velocity piercing javelins penetrating up to 3 consecutive enemies (560px range cap).
6. **Magic Scepters**:
   - Expanding radial shockwaves dealing area-of-effect damage to closely packed foes (560px range cap).

### 5.2 Touhou-Inspired Bullet-Hell Boss Danmaku
Boss encounters feature intricate geometric bullet patterns requiring precision dodging:
- **Danmaku Patterns**:
  - 16-way expanding spiral starbursts.
  - Dual rotating celestial cross beams.
  - Targeted bullet rings with narrow micro-gaps.
  - Curved undulating waves of frost needles and magma orbs.
- **52% Fair Lethal Core**: Projectile hitboxes are concentrated into the inner 52% of their visual sprite radius. Visual bullet edges do not register cheap hits.
- **Perimeter Graze Mechanic**: Dodging within 100% to 175% of a projectile's visual radius triggers an auditory chime, visual graze sparks, and awards **+1 Mana (MP)**. This rewards players who aggressively graze bullet curtains to fuel their combat skills.

---

# 6. Specialized Animated Traders & Nomadic Economy

Three specialized nomadic traders wander the Root Realm:

### 6.1 Trader Roster
1. **Zephyrion the Wandering Peddler (Wares)**:
   - Sells up to 5 randomized weapons and equipment.
   - Stock matches world drop rate distributions, capped at Epic rarity (no skill books).
2. **Ignis Vance the Forge Master (Enhance)**:
   - Conducts gear enhancements (+1 to +7) and repairs broken items for 1 Gold.
3. **Morrigan the Void Weaver (Affix)**:
   - Performs affix slot carving using Affix Stones and repairs broken items for 1 Gold.

### 6.2 Trader Behavior & Safeguards
- **Mutual Exclusion**: Only one trader may exist in the world at any given time.
- **Nomadic Rarity**: Spawns randomly at a distance from player shelters to encourage world exploration, lingering for a limited duration before vanishing.
- **Turtle Shell Defense**: If any hostile entity enters within a **3-block radius (96 pixels)**, the trader withdraws into an invulnerable turtle shell defense barrier. All incoming enemy attacks are deflected, and trading is disabled until the player clears the perimeter.
- **Hover Inspection UI**: Browsing shop wares displays comprehensive item tooltips, matching backpack inspection with stat differences, enhancement indicators, and affix details.

---

# 7. Crafting Systems & Dedicated Asset Pipeline

### 7.1 Minecraft-Style 5 Crafting Categories
The crafting window (`E` key) organizes 129 recipes across five distinct categories:
1. **Building Blocks**: Wooden planks, stone bricks, dungeon bricks, glass windows, roof shingles, platforms.
2. **Equipment & Tools**: Swords, composite bows, pickaxes, axes, shovels, armor pieces.
3. **Consumables & Alchemy**: Potions, meals, golden french fries, ammunition arrows.
4. **Furniture & Housing**: Tables, chairs, beds, grandfather clocks, stone fireplaces, bookshelves.
5. **Miscellaneous & Raw**: Affix stones, portal shards, ingots, textiles, mechanical parts.

### 7.2 Dedicated Craftables Asset Directory
All 129 craftable item sprites are strictly stored in `assets/craftable_items/`, completely isolated from the 1,337 droppable items in `assets/items/`. The engine's asset factory checks `assets/craftable_items/` first, ensuring clear separation and modifiability.

### 7.3 Tool Tiers & Bare-Hand Anti-Softlock
- Block breaking speed scales directly with tool tier: Wooden < Copper < Iron < Gold < Celestial.
- Tools have reduced combat damage to prevent starter tools from acting as dominant early-game weapons.
- Bare-hand harvesting allows punching wood and dirt at very slow speeds, ensuring players who lose their tools can never be softlocked.

---

# 8. World Dynamics, Environment & Physics

### 8.1 Boundless Chunk Streaming
Terrain is synthesized using continuous multi-octave Perlin noise in 16x240 tile chunks. Generating chunks executes asynchronously on a background thread pool, eliminating frame drops during high-speed traversal.

### 8.2 Time-of-Day Dynamics
- **Morning Peace ($0.0 \le t < 0.22$)**: Zero surface monster spawns; dedicated time for gathering and construction.
- **Midday ($0.22 \le t < 0.50$)**: Passive wildlife and occasional slimes.
- **Night Peak ($0.50 \le t < 1.0$)**: Aggressive hordes of zombies, night gazers, and crawlers.
- **Nightly Elite Champion**: A single, enlarged elite monster spawns once per night with 2.5x-3.5x HP, custom visual scale, and a unique combat skill.
- **Subterranean Mini-Boss Placement**: Mini-bosses reside exclusively in underground dungeon chambers; random surface mini-boss spawns are disabled.
- **Bed Proximity Safety Check**: Sleeping in a bed is only permitted at night when no hostile entities are within a 6-block radius (192 pixels).

### 8.3 Torch Placement Physics
Torches cannot float freely in open air or be placed underwater. Valid placement requires:
- An adjacent solid support tile (below, left, or right), OR
- A valid background wall (Wood Wall, Stone Wall, Brick Wall).

---

# 9. UI, Controls & Quality of Life

### 9.1 World Selection History
The world selection menu records and displays:
- Accumulated playtime in hours.
- Last played calendar date and timestamp.

### 9.2 Word-Wrapped Auto-Hiding Console & Chat
In-game command feedback and player chat are formatted in a dedicated, word-wrapped text container that smoothly fades after a period of inactivity, keeping the screen clean during combat.

### 9.3 Cross-Platform Input Controls
- **PC Controls**:
  - Movement: `A` / `D` (or Left / Right Arrows)
  - Jump: `Space` / `W`
  - Drop Through Platform: `S`
  - Mine / Attack: Left Mouse Button (Hold for continuous action)
  - Place Block / Interact: Right Mouse Button
  - Inventory & 5-Category Crafting: `E`
  - Character Paperdoll & Grimoire: `C`
  - Active Skills: `Q`, `F`, `V`, `R`
  - Console / Chat: `Enter`, `/`, or `~`
  - Fullscreen Toggle: `F11`
  - Profiler Overlay: `F3`
- **Mobile Controls**:
  - Virtual dynamic left joystick for movement.
  - Right action cluster: Primary Attack/Mine, Jump, Dash, Potion.
  - Radial arc skill cluster (`Q`, `F`, `V`, `R`).
  - Minimum 48x48px touch targets with active press feedback and opacity configuration.

---

# 10. Boss Progression & Climax Encounters

### 10.1 Subterranean Dungeon Mini-Bosses
1. **Lord Malus the Blight-Bringer** (Nether Crypt): Rot spits, sweeping cleaves, and summonable blight slimes. Drops Nether Portal Shard.
2. **Ignis Colossus the Magma Golem** (Cavern Lava Pools): Scorching ground slams and magma waves. Drops Magma Portal Shard.
3. **Cryo-Spud the Glacial Terror** (Snow Depths): Freezing blizzards, icicle spears, and permafrost barriers. Drops Frost Portal Shard.
4. **Necro-Tuber the Crypt Fiend** (Catacombs): Bone volleys, life drain, and teleportation. Drops Shadow Portal Shard.

### 10.2 Grand Boss: Sol-Rho The Celestial Titan
Constructing the **Celestial Keystone** at a Work Bench (4 Portal Shards + 4 Gold Bars + 8 Stone Bricks) summons Sol-Rho:
- **Phase 1: Solar Titan Form (2,500 HP)**: Levitates above the arena, firing 16-way danmaku starbursts, solar flare shockwaves, and rotating cross beams.
- **Phase 2: Awakened Void Incarnate (4,000 HP)**: Enters cosmic void fury with singularity vortexes, rapid warp blitzes, and dense bullet hell curtains.
- **Victory Rewards**: Slain Sol-Rho drops the *Crown of Potaria*, *Astral Wrath*, *Celestial Greatsword*, and the divine achievement.

---

# 11. Technical Architecture & Unity 6 LTS 2D URP Engine

Potaria is architected using **Unity 6 LTS (v6000.0.58f1)** with the **2D Universal Render Pipeline (URP 17.0.3)** for multiplatform deployment across PC (Steam, Steam Deck) and Mobile (Google Play Android):

```
+-------------------------------------------------------------+
|                 Potaria Game Logic & Systems                |
|      (Combat, Inventory, Crafting, Farming, RPG Progression)|
+------------------------------+------------------------------+
                               |
               +---------------+---------------+
               |   Unity 6 LTS Core Framework  |
               | (C# Scripts & ScriptableObjects) |
               +-------+---------------+-------+
                       |               |
      +----------------+------+ +------+----------------------+
      | 2D Universal Render   | | Physics2D & Tilemap Engine  |
      | Pipeline (URP 17.0.3) | | Dual-Tilemap (Solid/Walls)  |
      | Pixel Perfect Camera  | | CompositeCollider2D         |
      | 2D Lights & Post-FX   | | Dynamic Chunk Streaming     |
      +-----------------------+ +-----------------------------+
                               |
               +---------------+---------------+
               | Cross-Platform Input & Network|
               | Unity Input System / FishNet  |
               | Steamworks P2P / Mobile Touch |
               +-------------------------------+
```

### Architectural Principles:
1. **ScriptableObject Data Layer**:
   - Centralized, strongly typed data assets for all 1,775 items, recipes, equipment sets, and crops in `Assets/Data/`.
   - Complete decoupling of gameplay data from runtime instances, enabling data-driven rebalancing without recompilation.
2. **Dual-Tilemap & Chunk Streaming Architecture**:
   - Foreground Tilemap (Terrain) with TilemapCollider2D and CompositeCollider2D for smooth, snag-free player locomotion.
   - Background Tilemap (Walls) for caves, houses, and ambient subterranean depth.
   - Dynamic chunk streaming manager activating and pooling tilemap chunks around the player camera with zero hitching.
3. **2D Universal Render Pipeline (URP)**:
   - Native `UnityEngine.Rendering.Universal.PixelPerfectCamera` configured at 16 Pixels Per Unit ensuring crisp, integer-scaled pixel art across all resolutions.
   - 2D Lights (Global Light for continuous Day/Night cycles; Point Lights for torches, glowing mushrooms, and celestial spells).
   - Integrated URP post-processing (bloom for ancient gear auras, danmaku bullets, and celestial boss attacks).
4. **Cross-Platform Input System**:
   - New Unity Input System with unified action bindings supporting Keyboard/Mouse, Gamepad (Steam Deck, Xbox, PlayStation), and responsive virtual touch controls for mobile.
5. **Multiplayer Architecture (FishNet & Steamworks P2P)**:
   - High-performance, host-authoritative networking supporting 1-5 players.
   - Seamless Steam lobby matchmaking, friend invites, and direct LAN IP connection.
6. **Legacy Pygame Engine Archival**:
   - The verified Pygame-ce prototype (Smart OpenGL HAL, 770 automated regression tests) is permanently preserved on the `pygame-engine` branch for reference and historical parity benchmarking.

---

# 12. Franchise Architecture: One Project Repository (Dual-Profile)

To deliver both boundless sandbox freedom and deep narrative storytelling without splitting the community or codebase, the franchise is organized as **One Project Repository** featuring a dual-profile model:

### Product Profile 1: Potaria (The Base Game)
- **Concept**: The boundless 2D procedural sandbox survival and building adventure.
- **Focus**:
  - Boundless multi-octave terrain exploration (-infinity <-- 0 --> +infinity).
  - 129 categorized crafting recipes across building, tools, consumables, furniture, and materials.
  - Mining, base construction, and settlement defense.
  - 100-level character progression and Chroisen-style paperdoll gear customisation.
  - Casual 1-5 player LAN cooperative multiplayer and Last Man Standing (LMS) PvP arenas.
- **Target Audience**: Fans of open-ended sandbox survival and emergent building gameplay.

### Product Profile 2: Potaria: Root Realm (The Flagship ARPG Franchise)
- **Concept**: The epic narrative-driven action RPG and story campaign.
- **Focus**:
  - Structured narrative chapters with voiced character dialogue (Spud, Pip, Barnaby, Florencia, Russet).
  - Heartroot world transformation mechanics where player choices reshape corrupted biomes into radiant sanctums.
  - The comprehensive POTAdex journal cataloging biological flora, subterranean fauna, and ancient relics.
  - Curated puzzle dungeons, bespoke trap gauntlets, and cinematic boss choreography.
  - Branching story choices with permanent narrative consequences.
- **Target Audience**: Fans of rich narrative RPGs, dungeon crawling adventures, and character-driven stories.

---

# 13. Data-Driven Loot, Rarity & Multi-Affix System (Phase 1)

Potaria and *Potaria: Root Realm* share a unified, data-driven itemization engine (`src/loot/`) built around the **4-Layer Item Model**:

```text
BASE ITEM + AFFIXES + RARITY + OPTIONAL UNIQUE EFFECT
```

### 13.1 Standardized 1,461-Item Registry (`src/loot/item_registry.py`)
- Maps all 1,461 items (including all 129 craftable recipes and 1,337+ droppable items) into canonical `ItemDefinition` schemas across 9 categories: `weapon`, `armor`, `accessory`, `consumable`, `material`, `ammunition`, `skillbook`, `quest_key`, and `relic`.
- Preserves 100% compatibility with `ITEM_REGISTRY`, existing save files, and `/give` console commands.

### 13.2 Canonical 7-Tier Rarity & Multi-Affix Engine (`src/loot/rarity_engine.py`, `src/loot/affix_engine.py`)
- **Rarity Tiers & Affix Budgets**: `Common` (0), `Uncommon` (1), `Rare` (2), `Epic` (3), `Mythic` (4), `Legendary` (5), `Ancient` (6).
- **9 Canonical Affixes (`data/affixes/affixes.json`)**: `Vampiric`, `Burning`, `Frozen`, `Swift`, `Heavy`, `Piercing`, `Rootbound`, `Astral`, `Blighted`, plus thematic suffixes (`of the Root`, `of the Blight`, `of the Cosmos`, `of the Vanguard`).
- **Deterministic Seeded Rolls & Mutual Exclusion**: Uses local `random.Random(rng_seed)` instances with strict category eligibility, rarity gating, and mutual exclusion rules (`Burning` excludes `Frozen`, `Swift` excludes `Heavy`, `Rootbound` excludes `Blighted`).

### 13.3 3-Path Loot Acquisition (`src/loot/loot_system.py`, `data/loot_tables/loot_tables.json`)
1. **Random Drops**: Category and level-filtered world drops.
2. **Targeted Drops**: Boss-specific (`lord_malus`, `ignis_colossus`, `cryo_spud`, `necro_tuber`, `sol_rho`) and biome-specific (`forest`, `desert`, `snow`, `corruption`, `mushroom`, `dungeon`) pools.
3. **Guaranteed Milestone Drops**: Deterministic first-kill and progression milestone rewards (`first_boss`, `malus_first_kill`, `sol_rho_first_kill`, `keystone_forged`).

### 13.4 Official Visual Item Catalogs (`.docx` & `.pdf`)
- **`Potaria_Items_Catalog.docx`** (`scripts/generate_items_docx.py`): Microsoft Word Landscape document with OpenXML row-split protection (`w:cantSplit`) and repeating table headers (`w:tblHeader`).
- **`Potaria_Items_Catalog.pdf`** (`scripts/generate_items_pdf.py`): High-resolution PDF rendered via direct `QPainter` row-height pagination, guaranteeing zero sliced text/icons and zero header/footer overlap across all 1,461 items.
