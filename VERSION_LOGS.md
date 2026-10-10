# POTARIA: ROOT REALM — VERSION LOGS & CHANGELOG
**Lead Developer:** Kurados  
**Game Engine:** Pure Python 3.13 + Pygame Community Edition (`pygame-ce` 2.5.8+, SDL 2.32)  
**Architecture:** 2D Boundless Sandbox Action RPG (100% Offline Standalone, Zero External Downloads)  
**Repository:** [RetsardCo/Potaria](https://github.com/RetsardCo/Potaria.git)  

---

## Version History Overview

| Version | Release Date | Codename / Focus | Key Milestone |
| :--- | :--- | :--- | :--- |
| **v1.6.0** | October 2026 | *Animated Specialized Traders, Shop Tooltips, Crafting Directory, Auto-Hiding Console & Torch Physics* | 3 distinct animated traders (Wares, Enhance, Affix) with 4-frame animations & 64x64 portraits, single-trader existence & 15-35 tile distant spawn, 3-block turtle shield radius, 1 Gold repair, rich shop hover tooltips, dedicated craftable items catalog directory, word-wrapped 6.0s auto-hiding command console, torch physical support rules, and 308 passing tests. |
| **v1.5.0** | October 2026 | *Minecraft-Style Crafting Categories & 56+ Craftable Arsenal* | 5-tab category filter system ([ALL], [BUILDING], [EQUIPMENT], [SURVIVAL], [FURNITURE]), mouse-wheel crafting pagination, zero-drop panel hitboxes, 56 new craftable items (114 total recipes), paperdoll shields & off-hands, dynamic consumable healing, and procedural pixel art sprites. |
| **v1.4.0** | October 2026 | *Bullet-Hell Boss Barrages & Touhou Dodging Mechanics* | High-density geometric bullet patterns for all 4 Mini-Bosses & Grand Boss Sol-Rho (Phases 1 & 2), 52% fair lethal core hitbox, perimeter graze hitbox (+1 MP reward), 60+ FPS quantized surface caching (<1.2ms for 500 projectiles), authoritative LAN multiplayer bullet synchronization. |
| **v1.3.0** | October 2026 | *Mystic Trader, Affix Grimoire & Storage Chests* | Mystic Wandering Trader, Turtle Shield, Affix Slot Carving & Affix Stones, +1..7 Enhancement & Breaking/Repair, 20-slot Storage Chests, Playtime & Last Played World Select tracking. |
| **v1.2.1** | October 2026 | *1-Block Body Collider & Sprout Clearance* | 1-block (32px) body hitbox, decorative leaf collision exclusion, 1-block tunnel traversal. |
| **v1.2.0** | October 2026 | *Night Terrors & Dungeon Titan Ascension* | Bed 6-block enemy sleep check, dungeon-only mini-bosses, Nightly Elite Champion, major boss stat buffs. |
| **v1.1.0** | October 2026 | *Loot Recalibration & Chest Overhaul* | Moderate ARPG drop rates, Epic/Mythic chest loot, Windows console encoding fixes. |
| **v1.0.0** | October 2026 | *Combat Overhaul & Single-Target Balancing* | Single-target combat with Ancient cleave/pierce exceptions, Boss UI/UX, Tool Power removal, PDF catalog. |
| **v0.9.0** | October 2026 | *Performance Engine & 120 FPS Benchmark* | Async chunk streaming, baked chunk surfaces, BFS lighting optimization, F3 profiler. |
| **v0.8.0** | October 2026 | *Cross-Platform & Touch Architecture* | Dual-scheme PC & Mobile virtual controls, ergonomic action cluster, touch settings. |
| **v0.7.0** | October 2026 | *Living World & Survival Mechanics* | Cute Terraria trees, swimming & oxygen meter, furniture beds/clocks, dedicated coin purse, 200+ achievements. |
| **v0.6.0** | October 2026 | *Cinematic Audio & Prologue Cutscene* | 16s dynamic synth soundtracks, 3D spatial audio, retro character blip voices, narrated prologue. |
| **v0.5.0** | October 2026 | *Ranged Arsenal & Titan Gauntlets* | Ballistic arrows, catalysts, staves, rods, scepters, mini-boss arenas, Grand Boss Sol-Rho. |
| **v0.4.0** | October 2026 | *Pygame-ce HD & Anti-Plagiarism Overhaul* | 1,100+ unique procedural weapons/armor, 7-tier rarity hierarchy, original Potaria lore. |
| **v0.3.0** | September 2026 | *Boundless World & Cellular Lighting* | Infinite coordinate chunk generation, dynamic time-of-day lighting, subterranean biomes. |
| **v0.2.0** | September 2026 | *Chroisen RPG Systems & Skill Grimoire* | 1–100 leveling, paperdoll equipment slots, 40 skill books, set bonuses & visual auras. |
| **v0.1.0** | September 2026 | *Genesis Prototype* | 2D tile grid, player movement, basic physics, initial block harvesting. |

---

## Detailed Version Logs

### [v1.6.0] — Animated Specialized Traders, Shop Tooltips, Crafting Directory, Auto-Hiding Console & Torch Physics (Current Release)
*Release Date: October 2026*

#### Added
- **Three Distinct Animated Specialized Traders**:
  - Added 3 distinct wandering trader specializations:
    - **Wares Merchant Spud (`trader_wares`, Zephyrion)**: Wandering cosmic merchant selling 5 weapons and armor pieces rolled at ARPG drop rates (capped strictly at Epic), with a random chance to offer Affix Slot Carving Vouchers.
    - **Grand Artificer Spud (`trader_enhance`, Ignis Vance)**: Master forge artificer selling refined bars, celestial starch cores, and artificer whetstones; provides on-the-spot equipment enhancement up to +7 with broken gear protection warning.
    - **Runic Occultist Spud (`trader_affix`, Morrigan)**: Mystic socket master selling pristine affix stones, keystone shards, and starlight catalysts; carves open Affix Slots into Legendary and Ancient gear in exchange for silver/gold or service vouchers.
  - **Single Trader World Existence Rule**: Strictly **one** trader can exist in the world at any given time. Spawning checks existing active traders across all chunks and suppresses duplicate spawns until the current trader despawns.
  - **Distant Spawning Algorithm**: Traders spawn 15 to 35 blocks (480–1120px) away from the player into safe grounded subterranean or surface locations, ensuring the player must explore to discover them and preventing base camp exploits.
  - **4-Frame Pixel Art Idle Animations**: Handcrafted 4-frame breathing, floating, and tool-swaying sprites synthesized in `AssetFactory.npc_frames` for each trader archetype (Zephyrion's sapphire cloak and glowing lantern, Ignis Vance's glowing rune hammer and forge embers, Morrigan's levitating robes and 3 orbiting runic stones).
  - **64x64 High-Resolution Dialogue Portraits**: Handcrafted 64x64 portraits synthesized in `AssetFactory.npc_portraits` with distinctive character design (Zephyrion's golden spectacles & sapphire cowl, Ignis Vance's brass steampunk goggles & soot smudges, Morrigan's starry cowl & cosmic violet eyes).
  - **Universal Gear Repair**: All three traders provide a reliable gear repair service restoring broken (`is_broken`) weapons and armor to 100% functionality for exactly 1 Gold Coin (10,000 Copper).
  - **Turtle Shield 3-Block Radius (96px)**: Adjusted hostile enemy detection radius from 7 blocks down to **3 blocks radius** (96px). When enemies enter within 96px, the trader retracts into their impenetrable energy shell, locking trades and deflecting 100% of incoming damage.

- **Browse Wares Rich Item Tooltips**:
  - Implemented `_render_shop_item_tooltip()` in `NPCDialogueWindow`. Hovering over any ware card in the shop view instantly displays a comprehensive Diablo/Torchlight-style item card matching inventory tooltips.
  - Displays rarity-colored title, rarity and category badge, attack damage, weapon swing speed, defense, bonus stats, bulleted special perks, description, lore quotes for high-tier relics, and price tag in Copper, Silver, or Gold.

- **Dedicated Directory for Craftable Items**:
  - Created a dedicated crafting catalog directory, isolating craftable items from the 1,100+ droppable items catalog for effortless inspection and balancing.
  - Saved all 129 craftable recipes categorized across `building`, `equipment`, `survival`, and `furniture` with required crafting stations, ingredient counts, descriptions, and rarities.
  - Added `load_craftable_recipes()` which dynamically loads and parses external recipe catalogs with safe fallback to built-in definitions.

- **Word-Wrapped Console & 6.0-Second Auto-Hide**:
  - Redesigned chat and command console into a stylish semi-transparent dark glass window (460px width) with gold accents.
  - Implemented text word-wrapping to prevent long cheat commands (`/give ...`) and system announcements from stretching across the screen or obscuring gameplay.
  - Implemented 6.0-second auto-hide timer: when the console is idle, messages older than 6.0 seconds automatically disappear, providing a 100% clear screen. Pressing `/`, `~`, or `Enter` reopens the console box with full history.
  - Expanded command input text buffer from 40 to 80 characters.

- **Physical Torch Placement & Support Rules**:
  - Torches can no longer be placed underwater (`TILE_WATER`); attempting to place underwater gives clear feedback: *"Torches cannot be placed underwater!"*.
  - Torches can no longer float unsupported in open air. Placement strictly requires physical support:
    - A background wall behind the torch (`self.get_wall(tx, ty) != WALL_AIR`), OR
    - A solid supporting block directly beneath (`self.is_tile_solid(tx, ty + 1)`), OR
    - An adjacent solid block to the left or right (`tx - 1` or `tx + 1`).
  - Attempting to place a torch without support displays *"Torches require a supporting block or background wall!"*.
  - When a block beneath a torch is mined or destroyed, unsupported torches automatically pop off into air.

- **Zero-Crash Item Safety & Procedural Error Handling**:
  - Enhanced `ItemSpriteDict` to safely handle `ItemStack` objects, missing IDs, or corrupt item queries without raising uncaught exceptions.
  - Gracefully logs `[AssetFactory ERROR]` to the console and generates a clean procedural fallback surface, ensuring the game never crashes during item rendering or equipping.

- **Automated Quality Assurance & Verification**:
  - Created 9 comprehensive unit tests verifying 3 trader archetypes, animation frames, 64x64 portraits, single-trader spawning, 15-35 block distant spawn, 3-block turtle shield radius, 1 Gold repair, shop hover tooltips, craftable items JSON loading, console auto-hide, torch placement rules, and item asset generation safety.
  - Full project test suite passed 100% green across 308 tests in 24 test suites (`Ran 308 tests in 143.165s, OK`).

---

### [v1.5.0] — Minecraft-Style Recipe Book Categories & 56+ Craftable Arsenal Expansion
*Release Date: October 2026*

#### Added
- **Minecraft-Style Crafting Category Filter Tabs**:
  - Integrated 5 distinct recipe book category filters:
    - `[ALL]` (`CRAFT_CAT_ALL = "all"`): Displays every recipe matching current station proximities (Hand, Work Bench, Furnace).
    - `[BUILDING]` (`CRAFT_CAT_BUILDING = "building"`): Bricks, masonry blocks, columns, tiled roofs, and glass panes.
    - `[EQUIPMENT]` (`CRAFT_CAT_EQUIPMENT = "equipment"`): Shields, bucklers, aegises, repeaters, totems, satchels, lodestones, spyglasses, quivers, and specialist harvesting tools.
    - `[SURVIVAL & CONSUMABLES]` (`CRAFT_CAT_SURVIVAL = "survival"`): Campfires, torches, portable rations, restorative elixirs, roasted foods, ropes, and leads.
    - `[FURNITURE & MECHANISMS]` (`CRAFT_CAT_FURNITURE = "furniture"`): Storage, lanterns, decorative craft workstations (stonecutters, anvils, looms, mortars, targets), and furniture.
  - Category tabs rendered with dynamic active gold border highlights, glowing selection underline, hover tooltip descriptions, and live recipe count badges.
  - Zero-drop boundary protection: Expanded crafting panel hitbox (`get_panel_rect()`) encompassing all category tabs to eliminate accidental item drop-to-world occurrences when clicking recipe tabs.
  - Multi-page navigation & mouse wheel support: Added smooth mouse wheel scrolling over crafting panel and dedicated up/down scroll buttons.

- **56 New Craftable Items Catalog & Original Potaria Lore**:
  - Expanded craftable catalog from 58 to 114 total recipes across Hand, Work Bench, and Furnace crafting stations with 100% original Potaria names, stats, rarities, tool power, max_stacks, and rich world lore:
    - **Building**: `potaria_clay_bricks`, `granite_masonry_block`, `diorite_masonry_block`, `andesite_masonry_block`, `carved_basalt_pillar`, `chiseled_runic_slate`, `hardened_terracotta_tile`, `glazed_ceramic_tile`, `copper_roof_plates`, `tiled_timber_shingles`, `reinforced_glass_pane`, `iron_mesh_grate`, `woven_thatch_block`, `mossy_dungeon_cobble`.
    - **Equipment**: `oak_buckler`, `iron_aegis`, `arbalest_repeater`, `totem_of_resurgence`, `explorers_satchel`, `magnetic_lodestone`, `brass_far_seer`, `solar_chronometer`, `spud_quiver`, `fiber_clippers`, `pyrite_sparker`, `spud_angler_rod`, `copper_harvester_sickle`, `iron_harvester_sickle`.
    - **Survival & Consumables**: `field_campfire`, `soul_glow_torch`, `potaria_rope_coil`, `hemp_animal_lead`, `potato_bread`, `sweet_tuber_pie`, `smoked_spud_jerky`, `hearty_root_stew`, `glazed_golden_tuber`, `gilded_russet`, `herbal_salve`, `night_gazer_elixir`, `zephyr_tonic`, `spelunkers_flambeau`.
    - **Furniture & Mechanisms**: `iron_hanging_lantern`, `soul_brass_lantern`, `hearth_fire_pit`, `blacksmiths_anvil`, `honing_whetstone`, `alchemical_retort`, `apothecary_mortar`, `iron_trough`, `tailors_loom`, `archers_target`, `stonecutters_saw`, `carved_bookstand`, `rustic_wood_bench`, `oak_trestle_table`.

- **Paperdoll RPG Equipment Registration**:
  - Full paperdoll stat scaling for all new shields, off-hand charms, quivers, repeaters, and tools with Defense, Block Chance, Crit Rate, Knockback Resist, Range, Max HP, and Speed bonuses.

- **Consumables & Elixirs Engine**:
  - Extended `Player.consume_item()` to support all new foods and elixirs, including HP/MP restoration, vitality recovery, and dynamic item healing fallbacks from `ITEM_REGISTRY`.

- **Procedural Pixel Art Icon Generators**:
  - Added dedicated 16x16 / 32x32 vector drawing routines for shields, lanterns, anvils, whetstones, retorts, clippers, sparkers, compasses, spyglasses, clocks, satchels, tethers, totems, quivers, saws, targets, looms, food pastries, and masonry blocks.

- **Automated Quality Assurance Test Suite**:
  - 14 automated unit tests verifying category filtering, tab hitbox clicks, recipe counts, inventory deduction, station proximity requirements, consumable healing, paperdoll stats, and sprite generation.

---

### [v1.4.0] — Bullet-Hell Boss Barrages & Touhou Dodging Mechanics
*Release Date: October 2026*

#### Added
- **Core Bullet-Hell Engine**:
  - `_BULLET_SURF_CACHE`: High-performance pre-rendered vector surface cache with 12° quantization and alpha glow halos for zero-allocation 60+ FPS rendering of orbs, needles, shards, stars/snowflakes, wisps, scythes, meteors, and singularities.
  - `BossProjectile`:
    - **Fair Lethal Core Hitbox**: Precision core hitbox (`core_radius` ~52% of visual radius, e.g. 5.2px for a 10px radius bullet) preventing cheap edge-clipping deaths while weaving through dense bullet curtains.
    - **Perimeter Graze Hitbox**: Expanded graze boundary (`graze_radius = radius + 12.0`) rewarding precision near-miss dodges with +1 MP, audio/spark visual feedback, and graze count tracking.
    - **Rich Projectile Kinematics**: Support for sine-wave undulating streams, angular curve rates, acceleration multipliers, delayed blooms, homing curves, and gravity physics.
    - **Frustum Culling**: Off-screen projectile culling relative to viewport camera, guaranteeing stable 60+ FPS performance even with 500+ active projectiles (<1.2ms per frame benchmark).
    - **LAN Multiplayer Serialization**: `to_sync_dict()` and `from_sync_dict()` for authoritative host synchronization over network sockets.
  - `BulletHellPatterns`:
    - Modular pattern generator algorithms: `spawn_concentric_ring()` with designated safe passage gaps, `spawn_spiral_step()`, `spawn_aimed_spread()`, `spawn_snowflake_burst()`, `spawn_undulating_stream()`, `spawn_crisscross_curtain()`, and `spawn_homing_swarm()`.
- **Boss Bullet-Hell Barrages & Patterns**:
  - **Lord Malus - The Corrupted Oak**:
    - Pattern 1: Expanding toxic spore rings with 35° dodge gaps.
    - Pattern 2: Blighted spiral curse (counter-rotating 3-arm curtain).
    - Pattern 3: Homing dark wisp swarms.
    - Pattern 4: Blight cross aimed spread.
  - **Ignis Colossus - Magma Golem**:
    - Pattern 1: Magma radial bursts (20-to-28 shard starbursts).
    - Pattern 2: Cascading volcanic meteor showers with acceleration.
    - Pattern 3: Blazing fire rings with designated passage gaps.
    - Pattern 4: Magma bomb spread.
  - **Cryo-Spud - The Glacial Terror**:
    - Pattern 1: Symmetrical 16-point geometric crystalline snowflake bursts (32-point hyper-burst in Phase 2).
    - Pattern 2: High-frequency frost needle serpentine sine-wave streams.
    - Pattern 3: Counter-rotating freezing pinwheel vortex.
    - Pattern 4: Glacial shard wall.
  - **Necro-Tuber - The Lich**:
    - Pattern 1: Counter-rotating dual bone shard spirals.
    - Pattern 2: Inward-curving skull scythe arcs.
    - Pattern 3: Perpendicular criss-crossing catacomb grid curtains.
    - Pattern 4: Ghost skull swarm.
  - **Grand Boss Sol-Rho (Celestial Titan)**:
    - **Phase 1 (Radiant Solar Titan)**: Expanding solar flare nova rings (with safe passage gaps), 4-arm rotating sunburst wheel, sweeping continuous solar beam needle arcs, and aimed solar spread.
    - **Phase 2 (Awakened Void Titan)**: 5-arm accelerating abyssal singularity spiral barrage, black hole gravity pulse rings with dodge gaps, cosmic meteor curtain, and 360° starburst nova on warp blitz teleports.
- **Player Grazing Integration**:
  - `graze_count` and `graze_timer` state tracking.
  - `Player.on_graze()` hook rewarding near-misses with +1 MP and graze animation timer.
  - Cyan grazing spark feedback via particle system.
- **LAN Multiplayer Snapshot Synchronization**:
  - Authoritative host serializes boss active projectiles in `get_boss_sync_data()`.
  - LAN client reconstructs, interpolates, and renders synchronized projectiles in `sync_from_host()` and `update_client_projectiles()`.
- **Dedicated Bullet-Hell Test Suite**:
  - 30 comprehensive unit tests validating core hitboxes, grazing near-miss rewards, direct damage, all 4 mini-bosses' patterns, Grand Boss Sol-Rho Phase 1 & 2 patterns, 500-projectile high-density benchmark (< 1.4ms / ~750+ FPS), and multiplayer LAN snapshot serialization & client reconciliation.

#### Changed & Fixed
- **Sol-Rho Phase Transition Bullet Wipe & Freeze Fix**:
  - Fixed 2.2s projectile freeze during Sol-Rho Phase 1 -> Phase 2 transformation. Triggering phase transformation now immediately wipes active Phase 1 projectiles with celestial sparks and cancels ongoing pattern routines, preventing Phase 1 patterns from leaking into Phase 2.
- **Multiplayer Kinematic Desynchronization Fix**:
  - Serialized `delay_move` and `age` (`"del"`, `"age"`) into projectile sync dictionaries. Prevents delayed wave streams and sine-wave oscillations from triggering prematurely or out-of-phase on LAN clients.
- **Multiplayer Client Boss Animation & Transformation Fix**:
  - Fixed Grand Boss Sol-Rho animation frames freezing on LAN clients by checking `p1_frames` / `p2_frames` instead of nonexistent `frames` attribute.
  - Synchronized `is_transforming` status and boss name across multiplayer host/client snapshots.
- **I-Frame Safe Bullet Dissipation**:
  - Boss projectiles colliding with player core during invulnerability frames (`i_frame_timer > 0`) now safely dissipate with white sparks instead of lingering inside the player's hitbox and chain-stunlocking upon invulnerability expiration.
- **Surface Clipping Elimination**:
  - Expanded cached surface dimensions from `pad=4` to dynamic `max_extent = int(math.ceil(radius * 1.85 + 6))` eliminating needle, scythe, and wisp tip clipping at 0°/180° rotation bounds.
- **Graze Audio & Visual Feedback**:
  - Integrated audio chime and expanding cyan perimeter aura ring on precision bullet grazing.
- **Celestial Aegis Projectile Deflection**:
  - Embedded automatic bullet deflection for players wielding the *Celestial Aegis* affix within a 38px defensive radius.
- **Pattern Input Boundary Guards**:
  - Added zero and negative count boundary guards across all `BulletHellPatterns` methods preventing `ZeroDivisionError`.

### [v1.3.0] — Mystic Wandering Trader, Affix Grimoire & Storage Chests
*Release Date: October 2026*

#### Added
- **Mystic Wandering Trader (`MysticTraderNPC`)**:
  - Periodically spawns on a safe surface tile near the player every 3–5 minutes (180–300s).
  - Teleports and despawns after duration expires, even if caged or fully enclosed in solid blocks.
  - Sells 5 random weapons/equipments rolled according to weighted drop rates (Common: 40.0, Uncommon: 3.5, Rare: 1.5, Epic: 0.5), capped strictly at Epic (no skill books, no mythic/legendary/ancient items).
  - Impenetrable **Turtle Shield** automatically activates when hostile enemy mobs or bosses are within 7 blocks (224px). Retracts into shell, deflects 100% of damage, and locks trade interactions until the area is cleared.
  - Offers full weapon restoration for broken items for exactly **1 Gold Coin** (10,000 Copper).
- **Affix Slot & Affix Stone System**:
  - "Carve Affix Slot" service offered by Mystic Trader for Legendary and Ancient items: replaces a random basic stat (ATK, DEF, CRIT, SPEED, MP, HP, DAMAGE) with an open affix slot (up to 3 slots max).
  - Craftable **Affix Stone** at Work Bench requiring rare endgame materials (3 Celestial Portal Shards, 5 Gold Bars, 5 Blightstone).
  - Applying an Affix Stone embeds god-tier affixes (e.g. *Titan's Might*, *Celestial Aegis*, *Chronos Velocity*, *Vampiric Leech*, *Astral Executioner*, *Starch Fortress*, *Void Reaver*, *Solar Flare*).
- **Item Enhancement System (+1 to +7) & Breaking Risk**:
  - Weapons and equipment enhance up to +7 with scaling stats (multiplier = $1.0 + \text{level} / 7.0$, reaching exactly 2.0x base stats at +7).
  - Levels +1 to +4 are 100% safe (0% break risk). Levels +5 (20%), +6 (25%), and +7 (30%) have a chance of breaking on failure!
  - Broken items cannot be equipped or used for combat/mining attacks until repaired by the Mystic Trader for 1 Gold Coin.
- **Craftable 20-Slot Storage Chests**:
  - Craftable `chest` (10 Wood) and `iron_chest` (8 Wood, 2 Iron Bars) at Work Bench.
  - 20-slot storage window (`ChestStorageWindow`) with Quick Stack, Deposit All, and Loot All buttons, enhancement badges (`+N`), broken alerts (`!`), and full tooltip inspection.
  - Player-placed chests instantiate storage entities seamlessly across world saves and loads, dropping their contained loot and chest item when mined.
- **World Selection Menu Playtime & Last Played Date Tracking**:
  - Accumulates total playtime (`playtime += dt`) and tracks `last_played` timestamps in ISO format.
  - Displays formatted `Playtime: Xh Ym` and `Last Played: YYYY-MM-DD HH:MM` on all world selection cards.
- **Dedicated Test Suite**:
  - Created the automated random trader test suite with 15 comprehensive tests verifying trader spawn/despawn, wares cap, turtle shield deflection, repair cost, affix carving, affix stone crafting & embedding, enhancement scaling, broken item blocking, storage chests, and world save persistence. All 255 tests in the project pass 100% green!

#### Changed & Fixed
- **Equipment & Stat Scaling Architecture**: Upgraded paperdoll `Equipment.slots` to preserve `ItemStack` objects intact; active combat calculations and stat caching dynamically incorporate +1..+7 multipliers (up to 2.0x) and god-tier affix attributes into player attack, defense, HP, and crit.
- **Affix Stone Direct Inventory Application**: Implemented right-click usage and cursor drag-and-drop embedding for Affix Stones directly inside inventory UI.
- **Turtle Shield Dialogue Security**: Wired dynamic hostile enemy detection into `NPCDialogueWindow` to auto-close dialogue and prevent trade exploitation when enemies enter the 224px Turtle Shield perimeter.
- **Chest Tooltip & Metadata Preservation**: Added rich tooltips to hovered storage chest slots and preserved enhancement/affix attributes during chest stack splitting.
- **Equipment Save/Load Serialization**: Serialized equipped paperdoll `ItemStack` enhancement levels and affixes into world save files.

---

### [v1.2.1] — 1-Block Body Collider & Sprout Clearance
*Release Date: October 2026*

#### Changed & Fixed
- **1-Block Player Body Hitbox (`PLAYER_HEIGHT = 32`)**:
  - Re-scaled the player's physical collision bounding box from 36px to **32px** (precisely 1 tile / `SCALED_TILE`).
  - Removed collision from the top decorative potato sprout leaf, allowing Spud to freely walk under 1-block high ceiling openings, overhangs, and passages without clipping.
  - Adjusted rendering vertical offset (`draw_sy = sy - sprout_offset_y`) so the visual body and feet remain grounded on terrain while the decorative leaf renders smoothly above.
- **Multiplayer & PvP Hitbox Synchronization**:
  - Synchronized remote player hitboxes in multiplayer PvP (`rp_rect`) and projectile/fireball collisions to match the 28x32 body collider.
- **Dedicated Test Suite**: Created the player collider test suite with 9 unit tests verifying 1-block tunnel traversal, jump ceiling clearance, platform drop-through, and sprout leaf projectile passthrough.

---

### [v1.2.0] — Night Terrors & Dungeon Titan Ascension
*Release Date: October 2026*

#### Added
- **Bed Sleep 6-Block Monster Safety Proximity Check**:
  - Restrained bed sleeping so the player can strictly only sleep during the night when no hostile monsters or bosses are within a **6-block radius** (6 tiles / 192px).
  - Clear user notification feedback: *"You can only sleep at night"* during the day, and *"You cannot sleep now, monsters are nearby within 6 blocks!"* when hostile entities are near.
  - Active sleep interruption: If a monster wanders within 6 blocks during bed fast-forwarding, sleep immediately terminates with the alert: *"You were awakened! Monsters are nearby within 6 blocks!"*.
- **Nightly Elite Enemy ("Champion of the Night")**:
  - Exactly one formidable elite monster spawns on the surface once per night cycle.
  - 1.4x enlarged sprite scale with pulsating violet aura and champion crown badge.
  - Dedicated signature combat skill per champion: **Leap Slam** (gravity leap with ground shockwave), **Shadow Bolt** (void spit projectile), **Frenzy Charge** (speed surge), or **Ground Fissure** (linear tremor).
  - Boosted stats (150–220 HP, 19–24 ATK, 5–8 DEF) tuned to offer a night challenge without rivaling dungeon bosses.
  - Network archetype synchronization across multiplayer parties.
- **Dedicated Test Suite**: Added the night mechanics and boss balance test suite with 18 comprehensive unit tests.

#### Changed & Balanced
- **Dungeon-Exclusive Mini-Boss Placement**:
  - Completely removed random wild mini-boss spawns at night on the overworld surface.
  - Confined Lord Malus, Ignis Colossus, Cryo-Spud, and Necro-Tuber exclusively to deep subterranean dungeon chambers and dedicated pocket dimension arenas.
- **Mini-Boss & Grand Boss Stat Buffs**:
  - **Lord Malus (The Blight-Bringer)**: Max HP buffed from 520 to **900 HP** (+73%), damage buffed from 24 to **38** (+58%), defense increased to **16**.
  - **Ignis Colossus (The Magma Golem)**: Max HP buffed from 650 to **1,100 HP** (+69%), damage buffed from 28 to **44** (+57%), defense increased to **22**.
  - **Cryo-Spud (The Glacial Terror)**: Max HP buffed from 540 to **950 HP** (+76%), damage buffed from 22 to **36** (+64%), defense increased to **18**.
  - **Necro-Tuber (Lord of Bones)**: Max HP buffed from 480 to **880 HP** (+83%), damage buffed from 26 to **40** (+54%), defense increased to **15**.
  - **Grand Boss Sol-Rho (The Celestial Titan)**:
    - Phase 1 (Radiant Golden Titan): Max HP buffed from 600 to **1,000 HP** (+67%).
    - Phase 2 (Awakened Void Incarnate): Max HP buffed from 850 to **1,400 HP** (+65%).
    - Base contact/ability damage buffed from 36 to **52** (+44%), defense buffed to **28**.

---

### [v1.1.0] — Loot Recalibration & Chest Overhaul
*Release Date: October 2026*

#### Added
- **Underground Chest Expanded Rolls**:
  - Added dedicated **15% Epic Gear roll** in underground treasure chests with violet sparkle particles.
  - Added dedicated **3% Mythic Relic roll** in underground treasure chests with orange spark detonations and screen shake.
- **Rarity Pool Pre-initialization**: `self._catalog_rarity_pools` is now indexed during `CombatManager.__init__` rather than deferred until the first monster kill, ensuring chests opened immediately upon world spawn have instant access to all catalog tiers.
- **Dedicated Drop Rate Test Suite**: Created the item drop rates test suite providing empirical statistical verification across 20,000 mob kills and 500 chest openings.

#### Changed & Balanced
- **Monster Drop Rates Recalibration (Option 2: Moderate ARPG)**:
  - **Uncommon Gear**: Increased from 1.0% (1 in 100) to **3.5% (1 in ~28)**.
  - **Rare Gear & Skills**: Increased from 0.25% (1 in 400) to **1.5% (1 in ~67)**.
  - **Epic Gear**: Increased from 0.05% (1 in 2,000) to **0.50% (1 in 200)**.
  - **Mythic Relics**: Increased from 0.008% (1 in 12,500) to **0.15% (1 in ~667)**.
  - **Legendary Artifacts**: Increased from 0.002% (1 in 50,000) to **0.05% (1 in 2,000)**.
  - **Ancient Relics**: Increased from 0.0004% (1 in 250,000) to **0.01% (1 in 10,000)**.

#### Fixed
- **Windows Terminal Charmap Encoding**: Replaced Unicode stars with ASCII asterisks ('***') in drop announcement logs to eliminate `UnicodeEncodeError (cp1252)` on Windows consoles.
- **Test Suite Pass Rate**: All 213 unit tests passing green with zero regressions.

---

### [v1.0.0] — Combat Overhaul & Single-Target Balancing
*Release Date: October 2026*

#### Added
- **Single-Target Combat Restrictions**:
  - Restrained melee weapon swings so non-ancient weapons damage strictly at most **1 enemy per swing**.
  - Restrained bows, staves, rods, catalysts, scepters, and radial shockwaves so non-ancient projectiles damage strictly at most **1 enemy**.
- **Ancient Multi-Target Cleave Exception**:
  - Ancient tier items (`rarity == "ancient"` or `"ancient"` in id) retain multi-target damage capability, cleaving all enemies in the swing arc, piercing projectile lines, and exploding full radial shockwaves.
- **Boss Health Bar UI/UX Overhaul**:
  - Triple-layered boss health bar featuring metallic gothic bezel, pulsing heart jewel, smooth damage-drain ghost bars, and dynamic phase badges.
- **Comprehensive PDF Catalog**:
  - Catalog generator producing `Potaria_Items_Catalog.pdf`, documenting all 1,100+ weapons and equipment with item codes, stats, and asset previews.
- **Dedicated Single-Target Test Suite**: Created the single-target combat test suite testing melee, archery, javelin, and shockwave behaviors.

#### Changed & Balanced
- **Tool Power Removal**: Removed tool combat power rating from tooltips. Tools (pickaxes, axes, shovels) now deal minimal chip damage (2–3 base damage) to prevent trivializing combat with harvesting tools.
- **Dynamic Monster Scaling**: Scaled mob HP, attack damage, and defense dynamically based on player level and equipment power to eliminate early-game one-shot cheese.
- **Complete Item Descriptions**: Enriched descriptions for all weapons and equipment pieces in `ITEM_REGISTRY`.

#### Fixed
- Added `@center_x.setter` and `@center_y.setter` properties on the `Player` class to prevent coordinate attribute errors during automated combat testing.

---

### [v0.9.0] — Performance Engine & 120 FPS Optimization
*Release Date: October 2026*

#### Added
- **Real-Time F3 Telemetry Profiler**: Injected lightweight sub-millisecond instrumentation tracking Input, Player, Entity Logic, World Simulation, Chunk Rendering, Dynamic Lighting, and Present times.
- **Asynchronous Chunk Streaming**: Replaced synchronous chunk generation with background ThreadPool workers, eliminating 250ms movement stutter when traversing chunk boundaries.
- **Pre-computed Starfield Layers**: Pre-rendered twinkling nighttime star layers, eliminating per-frame trigonometric calculations.

#### Changed & Balanced
- **Surface Baking**: Implemented `ChunkSection` tile baking, reducing blit calls from thousands of individual tiles down to 6–9 pre-rendered chunk surfaces per frame.
- **BFS Lighting Optimization**: Optimized cellular lighting propagation using pre-mapped 32-bit RGB integers and `absorb_grid` caching, reducing lighting frame cost from ~3.5ms to <0.02ms.

#### Fixed
- **Victory Screen Navigation**: Fixed button event routing on `STATE_VICTORY`, allowing players to click "CONTINUE EXPLORING" after defeating Grand Boss Sol-Rho.
- **Town NPC Exploration Hitches**: Disabled heavy background housing validation checks during open-world exploration.

---

### [v0.8.0] — Cross-Platform & Mobile Touch Architecture
*Release Date: October 2026*

#### Added
- **Cross-Platform Mobile Touch HUD**:
  - Left virtual joystick / D-pad supporting 8-directional movement, jumping, and platform drop-through.
  - Right action cluster with ergonomic 48x48px touch targets: Attack/Mine, Jump, Dash, and Quick Potion.
  - Arc quick-skill hotkey buttons (Q, F, V, R).
  - Top bar utility pills: Backpack (E), Character Sheet (C), Settings/Pause (ESC).
- **Direct Touch World Interaction**: Tapping on tiles directly mines or places blocks; tapping enemies directs projectile aim.
- **Touch Settings Customization**: Configurable Touch Controls mode (`Auto`, `On`, `Off`) and opacity slider (`50%`, `75%`, `100%`) persisted in settings configuration.

#### Fixed
- Coexistence of mouse/keyboard input and touch emulation without control interference.

---

### [v0.7.0] — Living World & Survival Mechanics
*Release Date: October 2026*

#### Added
- **Cute Terraria Trees**: Handcrafted procedural tree canopies with rounded leafy foliage and textured bark. Chopping the trunk cleanly fells the tree and drops wood; foliage cannot be broken independently.
- **Animated Liquid Water & Swimming**: Liquid water tiles with subtle 1–2px wave sheen, fluid buoyancy drag, and an underwater oxygen bubble meter with drowning damage.
- **Interactive House Furniture**:
  - **Wooden Bed**: Sets player spawn point and provides resting HP regeneration.
  - **Grandfather Clock**: Right-clicking displays current in-game time and day phase.
  - **Fireplaces & Torches**: Ambient warm light emission and rising particle smoke.
- **Dedicated Coin Purse**: Removed coins from regular 40-slot inventory. Currency now deposits directly into character status (Copper, Silver, Gold coins with automatic 100:1 conversion).
- **Progressive Tool Tier Harvesting**: Block breaking speed scales progressively with tool category and tier (Wood -> Copper -> Iron -> Gold -> Celestial).
- **Inventory Recycle Bin**: Added dedicated trash slot in inventory to safely discard unwanted items.
- **200+ Achievements**: Created achievements tracking system for Combat, Mining, Crafting, Leveling, and Survival milestones with animated toast popups.

#### Fixed
- Full inventory item magnetism bug where dropped items hovered infinitely around the player without landing.

---

### [v0.6.0] — Cinematic Audio & Prologue Cutscene
*Release Date: October 2026*

#### Added
- **Prologue Cinematic Cutscene (`STATE_CUTSCENE`)**:
  - 4 multi-layered sequential pixel art illustrations depicting the Golden Age of Sol-Rho, the Cataclysm, the Rise of Nether Titans, and the Chosen Tuber.
  - Cinematic letterboxing, typewriter text animation, and speaker portraits.
- **Cutscene Narrator Audio**:
  - Full voice narration with built-in procedural audio synthesizer and high-fidelity speech narration engine.
- **In-Game Retro Synth Voices**: Animal Crossing / Undertale style phoneme voice chirps during dialogue (Pip the Guide, Sol-Rho, Barnaby the Merchant, Florencia the Nurse, Russet the Blacksmith).
- **16-Second Multi-Track Cinematic BGM**: Procedural orchestral synth themes with smooth crossfading transitions between Day, Night, Caverns, and Boss battles.

---

### [v0.5.0] — Ranged Arsenal & Titan Gauntlets
*Release Date: October 2026*

#### Added
- **Ranged Archery Physics**: Ballistic projectile math with real gravity arcs for Shortbows, Recurve Bows, Longbows, and Composite Bows.
- **Arrow Types**: Wooden Arrows, Frostburn Arrows (chill slow), Flame Arrows (burn damage), and Astral Arrows.
- **Magic Spellcasting Arsenal**:
  - **Catalysts & Tomes**: Cast homing celestial stars and orbs.
  - **Staves & Wands**: Launch fire, frost, and arcane magic bolts.
  - **Piercing Rods**: Fire high-velocity piercing javelins.
  - **Expanding Scepters**: Emit radial void shockwaves.
- **Subterranean Mini-Bosses**: Lord Malus (Nether Dungeon), Ignis Colossus (Desert), Cryo-Spud (Snow), and Necro-Tuber (Blight).
- **Pocket Dimension Altar Arenas**: Sun Altar Rune and Glacial Altar Rune teleports players to dedicated 1v1 arenas for boss duels.
- **Grand Boss Sol-Rho the Celestial Titan**: Colossal two-phase celestial boss encounter requiring the forged Celestial Keystone.

---

### [v0.4.0] — Pygame-ce HD & Anti-Plagiarism Overhaul
*Release Date: October 2026*

#### Added
- **Procedural 1,100+ Item Generator**:
  - Comprehensive catalogs containing 550+ weapons and 550+ armor pieces and accessories.
  - 7-tier Rarity Hierarchy: Common (Gray), Uncommon (Green), Rare (Blue), Epic (Purple), Mythic (Orange), Legendary (Gold), and Ancient (Red).
- **Anti-Plagiarism Name Scrubbing**: Renamed borrowed terminology into original Potaria lore:
  - *Starfury* -> **Astral Wrath**
  - *Hermes Boots* -> **Zephyr Striders**
  - *Demon Eye* -> **Night Gazer**
  - *Gel* -> **Spud Sap**
  - *Mana Flower* -> **Arcane Orchid**
  - *Band of Regeneration* -> **Talisman of Vigor**
  - *Corruption / Ebonstone* -> **The Blight / Blightstone**
- **Full Bestiary Animation Overhaul**: 12 FPS articulated sprites for Spud, slimes, mummies, zombies, and bosses with layered shading.

---

### [v0.3.0] — Boundless World & Cellular Lighting
*Release Date: September 2026*

#### Added
- **Infinite Open World**: Continuous coordinate chunk generation replacing fixed world boundaries ($-\infty \leftarrow 0 \rightarrow +\infty$).
- **Multi-Octave Terrain Synthesis**: Seeded Perlin noise producing natural surface hills, overhangs, cavern networks, and ore veins.
- **Dynamic Cellular Lighting**: Real-time BFS light propagation taking into account tile opacity, torches, and day/night sunlight angles.
- **Diverse Biome Engine**: Forest Starchlands, Arid Desert, Frozen Tundra, Glowing Mushroom Caverns, and the Nether Dungeon.

---

### [v0.2.0] — Chroisen RPG Systems & Skill Grimoire
*Release Date: September 2026*

#### Added
- **Character Progression**: Level 1 to 100 character leveling curve with stat points allocation.
- **Paperdoll Inventory**: Chroisen-inspired equipment slots (Head, Chest, Legs, Weapon, and 6 Accessory slots).
- **40 Unique Skill Books**:
  - Warrior: Power Slash, Whirlwind, Ground Slam, Berserk Rage.
  - Ranger: Volley, Piercing Shot, Dash, Rain of Arrows.
  - Mage: Fireball, Meteor, Frost Nova, Void Singularity, Celestial Shield.
  - Survival: Iron Skin, Regeneration, Swift Step.
- **Armor Set Bonuses & Radiant Auras**: Equipping matching sets (Ancient, Titan, Magma, Cryo, Spud) activates pulsing orbital aura mandalas.

---

### [v0.1.0] — Genesis Prototype
*Release Date: September 2026*

#### Initial Features
- Core 2D tile grid physics and player collision handling.
- Spud character rendering with walking, jumping, and falling states.
- Left-click mining, right-click block placement, and basic tool durability.
- Work Bench and Furnace crafting stations.
- Day/Night cycle clock with ambient darkness.
- Initial enemy behaviors: Green Slimes and surface Zombies.
