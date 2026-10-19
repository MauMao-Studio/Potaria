# POTARIA: ROOT REALM — VERSION LOGS & CHANGELOG
**Lead Developer:** Kurados  
**Game Engine:** Pure Python 3.13 + Pygame Community Edition (`pygame-ce` 2.5.8+, SDL 2.32)  
**Architecture:** 2D Boundless Sandbox Action RPG (100% Offline Standalone, Zero External Downloads)  
**Repository:** [MauMao-Studio/Potaria](https://github.com/MauMao-Studio/Potaria.git)  

---

## Version History Overview

| Version | Release Date | Codename / Focus | Key Milestone |
| :--- | :--- | :--- | :--- |
| **v0.2.8a** | October 2026 | *Skills, Boss Signature Attacks & Timed Projectile Reflection Integration (Current Active Build)* | Full integration of Potaria Skills and Bosses Design Spec: Ancient skill `celestial_reversal` (evolves to Celestial Mirror) with dynamic projectile reflection, reflection budget (12-24), 0.40s-0.52s active timing window, 1.5x damage amplification, and celestial gold/cyan shimmer; 19 new active combat skills with 32x32 icons in `assets/skills/`; 4 dungeon mini-boss signature attacks (`blight_apocalypse`, `caldera_catastrophe`, `absolute_zero`, `kingdom_of_the_unburied`) with animated 8-frame telegraph VFX; projectile preview contact sheet at `assets/projectiles/preview_contact_sheet.png` and `docs/projectiles_preview.png`; updated `UNIQUE_ASSETS_TRACKER.md` (2,445 verified unique assets with 0 collisions); and 732 tests passing across 46 suites (100% Green). |
| **v0.2.7a** | October 2026 | *Potaria Projectile Asset Library Procedural Synthesis & Asset Registry Integration* | Procedural high-art synthesis of all 40 projectile specifications (P01 to P40) from Potaria Projectile Asset Library (crisp 32x32 pixel art, transparent backgrounds, strict palette and silhouette adherence, clean dark outlines, 0 stray pixels), dedicated `ProjectileRegistry` in `src/assets/projectile_factory.py` with multi-alias lookups (`canonical`, `snake_case`, `ID`, `id_lower`, `.png`, path stems), full dict protocol support (`copy`, `pop`, `setdefault`, `del`), public builder functions, automatic disk export to `assets/projectiles/` (58 unique projectile assets, zero collisions), updated `UNIQUE_ASSETS_TRACKER.md` (2,370 verified unique assets), and 714 tests passing across 45 suites (100% Green). |
| **v0.2.6a** | October 2026 | *Weapon Skill Ordering & Streamlined Circular Affix Sockets UI* | Tooltip structure overhaul placing innate weapon skills/perks before affix slots, clean single-line circular socket indicators (`(○)` empty and `(●)` filled) adhering to item rarity socket limits (Epic: 1, Legendary: 1, Mythic: 2, Ancient: 2, Common/Uncommon/Rare: 0), total elimination of confusing 3-line status clutter (`AFFIX SLOTS`, `CARVED AFFIX SLOTS`, `[AVAILABLE TO CARVE]`), active affix deduplication in weapon skills, non-gear item socket exclusion, unified across HUD, Inventory, Chests, Character Panel, and NPC Dialogue windows, and 697 tests passing across 44 suites (100% Green). |
| **v0.2.5a** | October 2026 | *Whole-Game Balance Overhaul, 5-Active-Meal Categorized Architecture & Equipment Tuning* | Full implementation of Potaria Game Balance Plan: 5-active-meal-buff category framework (Offense, Defense, Mobility, Resource, Utility) with strict 1-buff-per-category replacement and no additive stacking, food stat contribution caps (max +12% DMG, +10% ATK SPD, +6% Crit, +6% DR, +2 HP/s regen, +15% Move SPD), standardized meal durations (2/3/4/5 min), dish-effect assignment across Filipino, fish, and potato cuisine with Kinilaw na Tanigue conflict resolution, ranged projectile meal buff damage scaling, non-combat meal buffs (fishing reeling speed, block mining power, mob drop luck), strict affix slot limits (Rare 0, Epic 1, Legendary 1, Mythic 2, Ancient 2), Risk Register suspect item tuning, dedicated pre-balance backup branch (`pre-game-balance-backup`) pushed to origin, and 684 tests passing across 43 suites (100% Green). |
| **v0.2.4a** | October 2026 | *Side-by-Side Gear Comparison, Health HUD Contrast & Direct Culinary Descriptions* | Side-by-side equipment comparison tooltips ("katabi") when hovering gear with Character Info (C) or chest storage open, equipped gear comparison badge `[ CURRENTLY EQUIPPED ]`, direct factual culinary descriptions across all food items, raw fish, meats, seasonings, and cookbook generation scripts without flowery language, high-contrast backing badge plate for numerical Life HUD readout (`Life: X / Y`), decoupling death screen fade overlay from UI surface layer to prevent low-HP text obliteration, and 672 tests passing across 42 suites (100% Green). |
| **v0.2.3a** | October 2026 | *Performance, Lighting Downward Shadow & Persistent World Cache Overhaul* | 108+ FPS baseline performance optimization (down from 22.9ms to 8.8ms frame time, >60 FPS guarantee), roof/ceiling daylight occlusion tracing from y=0 to viewport min_ty, sunlight downward shadow casting with top surface exposure illumination, clamped emitter intensities [0..15] preventing IndexError, version-enveloped lighting cache with selective invalidation on algorithm updates, atomic chunk cache writes, swizzle-safe OpenGL texture streaming fallback, and 653 tests passing across 41 suites (100% Green). |
| **v0.2.2a** | October 2026 | *Food Buff System, Decoupled Culinary Descriptions, Weapons Defense Scrub & UI Ergonomics* | 5-meal archetype food buff system with timed stat bonuses (Satiated, Attack Power, Damage Resistance, Swiftness, Health Regen), pure Filipino culinary descriptions decoupled from mechanical stat benefits, bottom-left food buff HUD overlay with hover tooltips and topmost z-order layering, main menu and settings hover tooltip cleanup (tooltips restricted strictly to icon-only buttons), Achievements card viewport bottom clearance fix, modal boundaries padding in Worlds and Key Bindings screens, complete weapon defense scrub across item registry, affix tables, stat ranges, and tooltip renderers, and 641 tests passing across 40 suites (100% Green). |
| **v0.2.1a** | October 2026 | *Gameplay, UI, Visual & Persistence Overhaul* | Zero player dark illumination by default (equipped gear / held torch light emission only), merchant shop card widening (580px window, 265px card) with name ellipsis truncation, settings reset confirmation modal prompt (settings and keybindings), settings button layout standardization (Back left, Reset right), atomic settings persistence across launches, daytime roof block incident sunlight without shadow bands, 3-level discrete camera zoom (1x, 2x, 3x) with hotkey Z and settings toggle, default Easy difficulty, World Selection ADVENTURE label cleanup, cinematic pitch-black death transition with instant spawn camera snapping, culinary overhaul with authentic Filipino food assets, tree-specific sapling growth animations, tree-specific wood and leaves variants, and 621 tests passing across 39 suites (100% Green). |
| **v0.2.0a** | October 2026 | *Water Buoyancy & Drowning, Tree Harvesting & Leaf Blocks, Pinoy Fishing & Inventory Organize* | Enemy water buoyancy & translucent blue submerged entity overlays, exact 1 heart/sec (10% max HP) drowning damage at 0% air, individual block-by-block tree harvesting without cascade felling, placeable `leaf_block`, leaf sapling drops, barren ground reforestation & daily sun growth animations, natural block world-tile inventory icon parity, inventory `[ORGANIZE]` compaction (filling gaps forward without re-sorting), fishing rod water interaction with 10 authentic Filipino (Pinoy) fishes (Bangus, Tilapia, Galunggong, Lapu-Lapu, Maya-Maya, Tanigue, Tambakol, Hito, Dilis, Dalagang Bukid) in raw and cooked forms with cooking recipes, rope rungs tile parity, dedicated silver steel `TILE_IRON_CHEST` world tile, and 416 tests passing across 38 suites (100% Green). |
| **v0.1.9a** | October 2026 | *Tile & Item Sprite Parity, Duplicate Asset Consolidation, and Craftables Cross-Check* | Redesigned placed world tiles (`TILE_CHEST`, `TILE_WORK_BENCH`, `TILE_FURNACE`) in `_generate_tiles` to 100% match held/inventory item icons, audited and consolidated duplicate/alias items (`wooden_bed` vs `bed`, `wooden_chest` vs `chest`, `wood_sword` vs `wooden_sword`, etc.) with discrete metadata, resolved `stone_fireplace` craftable station to Work Bench under `[FURNITURE & MECHANISMS]`, cleaned unindexed assets across `assets/items/` and `assets/craftable_items/`, refreshed `UNIQUE_ASSETS_TRACKER.md` (2,007 verified unique assets with 0 collisions), and passed all 400 test cases (100% Green). |
| **v0.1.8a** | October 2026 | *Phase 1 Data-Driven Loot & Multi-Affix System, Lantern Ceiling Physics & World Rename* | Standardized 1,461-item `DataDrivenItemRegistry` across 9 canonical categories (including all 129 craftables), 4-layer item model (`BASE ITEM + AFFIXES + RARITY + OPTIONAL UNIQUE EFFECT`), 9 canonical affixes + suffixes with deterministic seeded rolling and mutual exclusion, 3-path loot acquisition (`random`, `targeted`, `milestone`), dedicated Carved Tuber Lantern / Brass Lantern / Spectral Lantern world tiles with North ceiling hanging physics, interactive World Rename in World Selection with duplicate-name protection, and 360 tests passing across 28 suites (100% Green). |
| **v0.1.7a** | October 2026 | *Stage 2 Hardware Acceleration, GLSL Bloom Shaders & Projectile Batching* | Real GPU ModernGL 5.13 acceleration, GLSL Bloom post-processing fragment shader with dynamic luminance extraction and radiant pulse shimmer for Ancient gear and danmaku projectiles, high-density C-level projectile batch rendering (`draw_projectiles_batch`) integrated with boss danmaku barrages, single-log fallback deduplication eliminating startup warning spam, interactive in-game bloom toggle button (`[BLOOM SHADERS: ON / OFF]`) with `"bloom": true` persistence, state-preserving renderer switching, and 338 tests passing across 26 test suites (100% Green). |
| **v0.1.6a** | October 2026 | *Renderer Hardware Abstraction Layer (HAL), Smart OpenGL Architecture & Dual-Profile Franchise Model* | Modular `src/rendering/` architecture (BaseRenderer, SurfaceRenderer, GLRenderer, RendererManager), Smart OpenGL HAL with hardware-first ModernGL acceleration and automatic graceful fallback to Pygame-ce software rendering, in-game Video Settings toggle (Hardware ModernGL / Compatibility Software) with `saves/settings.json` persistence, ratified One Project Repository franchise model (Base Game Potaria + Flagship ARPG Potaria: Root Realm), and 328 tests passing across 26 test suites (100% Green). |
| **v0.1.5a** | October 2026 | *Animated Specialized Traders, Shop Tooltips, Crafting Directory, Auto-Hiding Console & Torch Physics* | 3 distinct animated traders (Wares, Enhance, Affix) with 4-frame animations & 64x64 portraits, single-trader existence & 15-35 tile distant spawn, 3-block turtle shield radius, 1 Gold repair, rich shop hover tooltips, dedicated craftable items catalog and asset directories, word-wrapped 6.0s auto-hiding command console, torch physical support rules, and 309 passing tests. |
| **v0.1.4a** | October 2026 | *Minecraft-Style Crafting Categories & 56+ Craftable Arsenal* | 5-tab category filter system ([ALL], [BUILDING], [EQUIPMENT], [SURVIVAL], [FURNITURE]), mouse-wheel crafting pagination, zero-drop panel hitboxes, 56 new craftable items (114 total recipes), paperdoll shields & off-hands, dynamic consumable healing, and procedural pixel art sprites. |
| **v0.1.3a** | October 2026 | *Bullet-Hell Boss Barrages & Touhou Dodging Mechanics* | High-density geometric bullet patterns for all 4 Mini-Bosses & Grand Boss Sol-Rho (Phases 1 & 2), 52% fair lethal core hitbox, perimeter graze hitbox (+1 MP reward), 60+ FPS quantized surface caching (<1.2ms for 500 projectiles), authoritative LAN multiplayer bullet synchronization. |
| **v0.1.2a** | October 2026 | *Mystic Trader, Affix Grimoire & Storage Chests* | Mystic Wandering Trader, Turtle Shield, Affix Slot Carving & Affix Stones, +1..7 Enhancement & Breaking/Repair, 20-slot Storage Chests, Playtime & Last Played World Select tracking. |
| **v0.1.1a** | October 2026 | *Night Terrors & Dungeon Titan Ascension* | Bed 6-block enemy sleep check, dungeon-only mini-bosses, Nightly Elite Champion, major boss stat buffs, 1-block body collider. |
| **v0.1.0a** | September 2026 | *Foundational Genesis Prototype & Action RPG Mechanics* | 2D tile grid, boundless infinite chunk streaming, dynamic time-of-day cellular lighting, player movement, combat skills, 1,100+ procedural weapons/armors, and initial survival systems. |
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

### [v0.2.8a] — Skills, Boss Signature Attacks & Timed Projectile Reflection Integration (Current Release)
*Release Date: October 2026*

#### Added & Improved
- **Ancient Skill Celestial Reversal & Timed Projectile Reflection**:
  - Implemented Ancient skill `celestial_reversal` (evolution `celestial_mirror` at Level 3, hotkey `Z`, MP cost 24, cooldown 8.0s) in `src/rpg/skills.py`.
  - Added timed reflection field (`reflection_field_timer`, `reflection_budget`, `reflected_projectiles_count`) to `Player` in `src/entities/player.py` with 0.40s-0.52s timing window and 12-24 projectile budget.
  - Implemented `BossProjectile.reflect(target_x, target_y, damage_mult=1.5)` in `src/entities/bullet_hell.py` with infinite loop deflection prevention, velocity redirection, damage amplification, celestial gold/cyan trail shimmering, and multiplayer synchronization serialization.
  - Integrated reflection damage processing into `DungeonMiniBoss` and `GrandBossSolRho` in `src/entities/boss.py`.
- **Expanded Combat Skills Arsenal**:
  - Registered all 19 proposed skills from Section 4: `shuriken_storm`, `star_seeker`, `arcane_barrage`, `venom_volley`, `void_implosion`, `crystal_shatter`, `chain_discharge`, `meteor_shower`, `piercing_blizzard`, `solar_detonation`, `arcane_minefield`, `frost_bomb`, `ember_cluster`, `spectral_pursuit`, `returning_hatchet`, `bolo_cyclone`, `ancestral_guidance`, `sumpang_sibat`, and `magma_eruption`.
  - Added 21 procedural 32x32 skill icons to `_generate_skill_icons()` in `src/assets/asset_factory.py` and exported to `assets/skills/`.
  - Redesigned Grimoire skill layout in `CharacterPanel` (`src/ui/character_panel.py`) into 6 columns to cleanly display all 30 skills with guaranteed >= 40px margin from panel bottom border.
- **Dungeon Mini-Boss Signature Attack Patterns**:
  - Implemented signature bullet-hell patterns in `BulletHellPatterns` (`src/entities/bullet_hell.py`): `spawn_blight_apocalypse`, `spawn_blight_constellation`, `spawn_rotting_roots`, `spawn_caldera_catastrophe`, `spawn_absolute_zero`, `spawn_frozen_clock`, and `spawn_kingdom_of_the_unburied`.
  - Added signature casting methods and HP threshold triggers to all four dungeon mini-bosses in `src/entities/boss.py`.
  - Generated 6 animated 8-frame telegraph and reflection VFX (`celestial_reversal_activate`, `projectile_reflect`, `blight_apocalypse_telegraph`, `caldera_catastrophe_telegraph`, `absolute_zero_telegraph`, `kingdom_of_the_unburied_telegraph`) with strictly unique per-frame geometry and zero hash collisions.
- **Visual Contact Sheet & Verification Suite**:
  - Generated projectile preview contact sheet (1328x794) at `assets/projectiles/preview_contact_sheet.png` and `docs/projectiles_preview.png`.
  - Updated `UNIQUE_ASSETS_TRACKER.md` (2,445 verified unique assets with 0 duplicate collisions).
  - Added comprehensive test suite `tests/test_skills_bosses_spec.py` with 18 tests.
  - Full test suite passes 100% green: 732 passed across 46 test suites.

### [v0.2.7a] — Potaria Projectile Asset Library Procedural Synthesis & Asset Registry Integration
*Release Date: October 2026*

#### Added & Improved
- **Potaria Projectile Asset Library Generation (P01 to P40)**:
  - Procedural 2D pixel-art synthesis engine implemented in `src/assets/projectile_factory.py` for all 40 specifications defined in `Potaria_Projectile_Asset_Library.json`.
  - Every sprite is rendered at native 32x32 resolution with transparent background, consistent dark outlines, deliberate pixel clusters, strict palette conformance, and zero stray pixels.
  - Covers all canonical categories: Physical Ranged (P01 Iron Arrow, P02 Heavy Bolt, P03 Throwing Knife, P04 Spinning Shuriken, P05 Returning Throwing Axe), Magic Elemental (P06 Fireball, P07 Ice Shard, P08 Lightning Bolt, P09 Shadow Orb, P10 Poison Glob, P11 Holy Bolt, P12 Earth Shard, P13 Water Orb, P14 Magma Core, P15 Wind Crescent, P16 Arcane Orb, P17 Arcane Lance), Magic & Tech (P18 Energy Disc, P19 Homing Star, P20 Void Sphere, P21 Spectral Skull, P22 Crystal Bolt), Explosive & Chemical (P23 Fuse Bomb, P24 Spiked Blast Core, P25 Meteor Fragment, P26 Arcane Mine, P27 Frost Bomb, P28 Acid Glob), Filipino-Inspired (P29 Bolo Throw, P30 Araw Sigil, P31 Anting-Anting Charm, P32 Diwa Wisp, P33 Sumpa Spear, P34 Ancestral Spirit Orb, P35 Kampilan Wave), Monster & Boss (P36 Monster Spit, P37 Curse Bolt, P38 Boss Core, P39 Tracking Shards, P40 Abyssal Seed).
- **AssetFactory ProjectileRegistry & Multi-Alias Resolution**:
  - Implemented `ProjectileRegistry(dict)` supporting canonical keys (`p01_iron_arrow`) while seamlessly resolving aliases (`iron_arrow`, `P01`, `p01`, case variants, `.png` extensions, and directory paths) without duplicating keys during iteration or disk exports.
  - Implemented full dictionary protocol for `ProjectileRegistry` including `copy()`, `pop()`, `setdefault()`, `__delitem__`, `@property aliases`, and safe `__contains__` checking target existence.
  - Exported 40 dedicated public builder functions (`build_p01_iron_arrow` through `build_p40_abyssal_seed` and `create_p...`) for programmatic use and asset pipeline extensions.
  - Hardened `AssetFactory.export_all_assets()` condition `has_library_projs` to verify presence of all 40 library projectile sprites on disk.
  - Fixed `write_unique_assets_tracker()` to load custom and mod items, preserving item categories and rarities across tracker generation.
  - Export pipeline in `AssetFactory.export_all_assets()` writes all 40 library projectiles alongside existing weapon and boss projectiles into `assets/projectiles/` (58 total unique projectile PNG assets).
- **Asset Tracker & Verification Suite**:
  - Updated `UNIQUE_ASSETS_TRACKER.md` with 2,370 verified unique assets and 0 duplicate collisions.
  - Expanded test suite `tests/test_generated_projectile_assets.py` to 8 comprehensive unit tests verifying file existence, 32x32 geometry, transparent corners, opaque pixel bounds, bitwise uniqueness, public builder functions, dictionary protocol methods, and flexible normalization lookups.
  - All 714 test cases across 45 test suites pass with 100% Green status.

### [v0.2.6a] — Weapon Skill Ordering & Streamlined Circular Affix Sockets UI
*Release Date: October 2026*

#### Added & Improved
- **Tooltip Structure Overhaul (Skill Before Affix)**:
  - Reordered equipment tooltip layout across all UI windows: innate weapon skills and unique perks (e.g. `• Glacial Chill (-35% Target Speed)`) now render cleanly **before** affix socket lines.
  - Active item affixes are automatically filtered from the native weapon skills list, preventing duplicate mentions of the same affix in both sections.
- **Streamlined Circular Affix Socket Indicators**:
  - Completely eliminated the cluttered, redundant 3-line affix status text:
    - Removed `AFFIX SLOTS: 0/0 (CARVE AT MYSTIC TRADER)`.
    - Removed `CARVED AFFIX SLOTS: 0/1 (LIMIT FOR EPIC)`.
    - Removed `· [AVAILABLE TO CARVE] 1 SLOT(S) OPEN AT MYSTIC TRADER`.
  - Replaced with clean, single-line ARPG circular socket indicators:
    - Empty uncarved slot: `(○) Affix Slot (Carve at Mystic Trader)`
    - Empty carved slot: `(○) Empty Affix Slot`
    - Filled carved slot: `(●) Affix Name (+Bonus Details)`
  - Total socket indicators strictly match item rarity capacity:
    - *Common, Uncommon, Rare*: 0 sockets (no socket lines rendered).
    - *Epic*: 1 socket.
    - *Legendary*: 1 socket.
    - *Mythic*: 2 sockets.
    - *Ancient*: 2 sockets.
  - Non-gear items (consumables, meals, materials, seeds, furniture, currency) are strictly excluded from rendering affix socket indicators.
- **Universal Tooltip Consistency**:
  - Unified this clean layout across all 5 game tooltip presentation modules:
    - Main HUD hotbar & inventory tooltips (`src/ui/hud.py`).
    - Inventory backpack tooltips (`src/ui/inventory.py`).
    - Storage chest container tooltips (`src/ui/chest_ui.py`).
    - Character Status panel tooltips (`src/ui/character_panel.py`).
    - Wandering Trader shop ware tooltips (`src/ui/npc_dialogue.py`).
- **Automated Verification**:
  - Added dedicated test suite `tests/test_weapon_skill_and_affix_socket_ui.py` (13/13 passed).
  - 697 tests passing across 44 test suites (100% Green).

---

### [v0.2.5a] — Whole-Game Balance Overhaul, 5-Active-Meal Categorized Architecture & Equipment Tuning
*Release Date: October 2026*

#### Added & Improved
- **5-Active-Meal-Buff Categorized Architecture**:
  - Implemented the 5-meal category framework according to Section 6 of the Game Balance Plan:
    - *Offense*: Physical/ranged/magic damage, attack speed, crit chance/damage, armor penetration.
    - *Defense*: Flat defense, magic resistance, percentage damage reduction, knockback resistance.
    - *Mobility*: Movement speed, jump force, dash speed/cooldown.
    - *Resource*: HP/MP regeneration, mana cost reduction.
    - *Utility*: Mining/woodcutting speed, fishing power, luck/drop rate, instant status cleanse.
  - Enforced strict 1-buff-per-category limit (maximum 5 active meal buffs total). Consuming a meal in an occupied category replaces that category's buff without transferring remaining duration; consuming in an empty category adds it.
  - Eating the same dish refreshes base duration without stacking stat magnitude or time additively.
  - Immediate HP/MP restoration applies separately from timed meal buffs.
  - Hard stat contribution caps enforced on food bonuses: Damage max +12%, Attack Speed max +10%, Crit Chance max +6%, Crit Damage max +16%, Armor Pen max +10%, Flat DEF max +6, Damage Reduction max +6%, Magic Resist max +15%, Move Speed max +15%, Jump Force max +15%, Dash max +15%, HP Regen max +2 HP/s, MP Regen max +2 MP/s, Mana Cost Reduction max -15%, Luck/Drop Rate max +10%, Mining/Woodcutting max +20%, Fishing Power max +15%.
  - Standardized meal duration tiers: Common/Snack 2 min (120s), Standard 3 min (180s), Rare 4 min (240s), Signature/Feast 5 min (300s).
  - Assigned candidate dish effects across all Filipino dishes, Fish dishes, and Potato dishes in `ITEM_REGISTRY`. Resolved Kinilaw na Tanigue conflict to canonical +90 HP and +12% movement speed (Mobility category, 3 min duration).
- **Ranged Projectile & Non-Combat Meal Buff Integration**:
  - Wired `ranged_damage_mult`, `damage_mult`, `crit_chance`, `crit_dmg_mult`, and `armor_pen` into `ArrowProjectile`, `StaffBoltProjectile`, `RodJavelinProjectile`, and `ScepterPulseProjectile` against both mobs and bosses.
  - Scaled fishing minigame reeling speed by `1.0 + player.get_meal_buff_val("fishing_power")`.
  - Scaled block mining speed by `gathering_speed` meal buff.
  - Scaled mob item drop rates by `luck` meal buff.
- **Affix Slot Budgets & Equipment Balancing**:
  - Enforced strict affix slot limits in `src/rpg/enhancement.py` and trader interactions: Rare max 0 additional slots, Epic max 1, Legendary max 1, Mythic max 2, Ancient max 2.
  - Audited and tuned suspect items from the Risk Register in Section 5:
    - *Genesis World Cleaver*: Balanced to 88 ATK, 24% crit, +60 HP, +80 MP, area explosion, and 90s cooldown fatal-hit ward.
    - *Celestial Titan Plate*: Adjusted to 32 DEF and +15% total damage mitigation.
    - *Crown of Potaria*: 30 HP barrier recharging every 20s.
    - *Ancient Heart*: 50% HP recovery upon reaching 1 HP with 120s cooldown.
    - *Void Edge*: 44 ATK + 10 true damage.
    - *Magma Greatsword*: 32 ATK + 8 fire damage.
    - *Zephyr Striders*: +35% sprint speed.
- **Git Backup Branch**:
  - Created and pushed dedicated backup branch `pre-game-balance-backup` to `origin` before applying balance modifications.
- **Automated Verification**:
  - Added test suite `tests/test_game_balance_overhaul.py` (12/12 passed).
  - Full test suite: 684 passed across 43 test suites (100% Green).

---

### [v0.2.4a] — Side-by-Side Gear Comparison, Health HUD Contrast & Direct Culinary Descriptions
*Release Date: October 2026*

#### Added & Improved
- **Side-by-Side Equipment Comparison Tooltips ("katabi")**:
  - Implemented dual tooltip cards displayed side-by-side when hovering over weapons, armor pieces, shields, or accessories while the Character Panel (`C`) or storage chest window is open.
  - Hovering over an equippable item shows its details card while concurrently displaying the currently equipped piece in that slot right beside it ("katabi") with an ornate gold header badge: `[ CURRENTLY EQUIPPED ]`.
  - Supports duplicate item comparisons with different enhancement levels, affixes, or rolled stats, while cleanly suppressing duplicate cards when hovering over the exact equipped piece itself.
  - Viewport-aware horizontal alignment prevents comparison cards from overflowing the screen edges or overlapping open panels.
- **Health HUD Contrast Badge & Death Overlay Fix**:
  - Resolved low-HP / dying visual bug where player health text was obscured by a dark-red rectangle over hearts.
  - Added a dedicated high-contrast backing badge plate behind the numerical Life readout (`Life: X / Y`) in `src/ui/hud.py` with dynamic health-dependent alpha and tone:
    - Dying/0 HP: Dark crimson plate `(28, 16, 20, 240)` with bright red text.
    - Low HP (<= 25%): Warning maroon plate `(24, 18, 22, 235)` with pulsing contrast.
    - Normal: Slate glass plate `(18, 22, 34, 230)` with crisp white text.
  - Decoupled the cinematic death fade transition surface from the UI layer in `main.py`, rendering death fade overlays directly onto the post-processed frame buffer so health counters, hearts, and HUD numbers remain crisp and visible right up to the final death moment.
- **Direct & Factual Food Culinary Descriptions**:
  - Completely streamlined all 79 dishes, raw seafood, poultry, meats, produce, seasonings, and culinary ingredients in `ITEM_REGISTRY` (`src/ui/inventory.py`), removing flowery, poetic, and dramatic wording.
  - Standardized acquisition notes, ingredient profiles, and section headers in `scripts/build_cookbook_docs.py` to direct, factual culinary statements.
  - Rebuilt all 4 cookbook files (`Potaria_Cookbook_With_Codes.pdf/docx` and `Potaria_Cookbook_No_Codes.pdf/docx`).
- **Automated Verification**:
  - Added comprehensive test suite `tests/test_equipment_comparison_and_death_ui.py` with 19 unit and integration tests.
  - 672 tests passing across 42 test suites (100% Green).

---

### [v0.2.3a] — Performance, Lighting Downward Shadow & Persistent World Cache Overhaul
*Release Date: October 2026*

#### Added & Improved
- **108+ FPS Engine Baseline Optimization**:
  - Reduced average frame time from 22.91 ms (43.7 FPS, 137.4% budget used) down to 8.82 ms (113.4 FPS average, 52.9% frame budget used), guaranteeing rock-solid 60+ FPS even with heavy combat and multiple bosses.
  - Reduced `Update Lighting` from 0.68 ms to 0.04 ms and `Render Lighting` from 2.06 ms to 0.76 ms via pre-flattened module-level tile property arrays (`_TILE_SOLID`, `_TILE_OPAQUE`, `_TILE_ABSORB`, `_TILE_EMIT`, `_TILE_RAD`), eliminating ~486,000 dictionary queries per 100 frames.
  - Eliminated redundant per-frame chunk generation checks, texture allocations, and surface recreations.
- **Overhead Roof and Ceiling Daytime Occlusion**:
  - Implemented full-column daylight occlusion ray-marching from `y = 0` down to `min_ty` using hoisted column tile arrays.
  - Opaque blocks directly stop sunlight (`cur_sun = 0`), properly shadowing interior rooms under player-built roofs, bridge ceilings, tree canopies, and floating sky islands.
  - Top surfaces exposed to the sky receive full incident daylight before light drops off downward, ensuring realistic natural lighting without artificial shadow bands above rooftop blocks.
- **Emitter Intensity Clamping & Error Prevention**:
  - Clamped emitter radial falloff values and light palette LUT indexing to [0, 15] (`min(15, max(0, ...))`), completely eliminating `IndexError` crashes when intense boss spells or high-tier skill auras exceed light level 15.
- **Persistent World Cache & Selective Invalidation**:
  - Added version-enveloped schemas to chunk and lighting caches (`schema_version`, `lighting_version`, `chunk_x`).
  - Implemented selective invalidation in `_ensure_manifest`: updating lighting algorithms invalidates and rebuilds lighting masks without re-generating valid chunk terrain.
  - Switched chunk cache writing to `atomic_write_json`, preventing corrupt cache files on unexpected game exits.
  - Added dimension validation to automatically discard and heal malformed cache files.
- **OpenGL Swizzle-Safe Texture Streaming**:
  - Added verification flags in `GLRenderer` to gate zero-copy `virtual_surface.get_buffer()` writes behind verified texture swizzle support, safely falling back to standard RGBA conversions if unsupported.
- **Automated Verification**:
  - Added comprehensive test suite `tests/test_lighting_and_cache_overhaul.py` (12/12 passed).
  - 653 tests passing across 41 test suites (100% Green).

---

### [v0.2.2a] — Food Buff System, Decoupled Culinary Descriptions, Weapons Defense Scrub & UI Ergonomics
*Release Date: October 2026*

#### Added & Improved
- **Food Buff System & Timed Stat Benefits**:
  - Implemented 5 meal archetypes according to the game balance plan:
    - *Snack / Street Food*: Quick consumption, +10% Speed for 45s (e.g. Banana Cue, Turon, Isaw, Kwek-Kwek, Fish Balls, Taho).
    - *Light Meal*: +15% Attack Power for 90s (e.g. Lugaw, Arroz Caldo, Champorado, Pancit Canton, Pancit Bihon, Pancit Palabok, Longganisa, Tocino, Tapsilog, Tortang Talong).
    - *Balanced Meal*: +20% Attack Power, +15% Damage Resistance for 180s (e.g. Chicken Adobo, Pork Adobo, Sinigang, Tinola, Bicol Express, Pinakbet, Laing).
    - *Feast / Heavy Dish*: +25% Attack Power, +25% Damage Resistance, +2 HP/s Regeneration for 300s (e.g. Lechon Belly, Crispy Pata, Kare-Kare, Bulalo).
    - *Dessert / Sweet Refreshment*: +15% Speed, +1 HP/s Regeneration for 60s (e.g. Halo-Halo, Leche Flan, Ube Halaya, Bibingka, Puto, Biko, Sapin-Sapin).
  - Food buff tracking, expiration ticks, and stat bonuses integrated directly into player update cycles.
- **Pure Culinary Descriptions Decoupled from Mechanics**:
  - Standardized all 79 food and ingredient entries in `ITEM_REGISTRY`: descriptions strictly cover authentic Filipino culinary heritage, aroma, taste profiles, and cooking ingredients without mechanical numbers or `+HP` strings.
  - Stripped legacy lore strings from all produce, pantry spices, and cooked dishes to maintain consistent distinction between item equipment lore and culinary dish descriptions.
- **Bottom-Left Food Buff HUD Widget**:
  - Compact active buff icons with ornate border and circular/bar duration indicators displayed on the bottom-left of the screen.
  - Deferred tooltip rendering to step 9.8 in the HUD draw pipeline, ensuring food buff tooltips render at topmost z-order above chat, party frames, and toasts without occlusion.
  - Rich hover tooltip displaying buff title, detailed stat bonuses, and remaining duration formatted in clean seconds.
- **Main Menu & Settings Tooltip Cleanup**:
  - Removed hover tooltip popups from all standard text buttons on the Main Menu, Settings, and LMS screens. Tooltips are now strictly reserved for icon-only action buttons where visual clarification is needed.
  - Adjusted Achievements cards viewport height (`viewport_h = ph - 165`), providing 28px clearance above the back button and preventing card scrolling overlap.
  - Expanded modal panel heights to 595 and anchored back and reset buttons cleanly within panel borders in Worlds and Key Bindings screens.
- **Complete Elimination of Weapon Defense**:
  - Zeroed out all defense attributes on weapons across `ITEM_REGISTRY`, `weapons.json`, `ARMOR_DATA`, and `NEW_EQUIPMENT_DATA`.
  - Replaced defensive stat range on `frost_blade` in `ITEM_STAT_RANGES` with critical strike chance, and updated `roll_item_stat_ranges()` to strip defensive stats when rolling weapon items.
  - Hardened affix engines (`src/loot/affix_engine.py` and `src/rpg/affix_system.py`) to restrict defensive affixes and stats exclusively to armor and shields.
  - Sanitized both compact and detailed item tooltips in `src/ui/inventory.py` and `src/ui/hud.py` to never display defense stats for weapon items.
- **Rebuilt Culinary Documentation**:
  - Updated `scripts/build_cookbook_docs.py` with separate "Culinary Notes" (pure cultural lore) and "Buff Effects" columns.
  - Rebuilt all 4 cookbook files (`Potaria_Cookbook_With_Codes.pdf/docx` and `Potaria_Cookbook_No_Codes.pdf/docx`).
- **Automated Verification**:
  - Created automated test suite `tests/test_food_buffs_and_menu.py` with 20 comprehensive unit tests.
  - 641 tests passing across 40 test suites (100% Green).

---

### [v0.2.1a] — Gameplay, UI, Visual & Persistence Overhauls
*Release Date: October 2026*

#### Added & Improved
- **Player Dark Illumination Refinement**:
  - Player character emits zero illumination by default in dark caverns or night environments.
  - Eliminated auto-glow bug where Miner Helmet in backpack slot 5 caused continuous glow; illumination now activates strictly when light-emitting gear (Miner Helmet, Crown of Potaria, celestial/radiant accessories) is actively equipped in paperdoll armor slots, or when holding a portable lantern or torch.
- **Merchant Dialogue Shop UI**:
  - Expanded NPC Dialogue Window width to 580px and shop item cards to 265px.
  - Repositioned the green BUY button with clean right-alignment and implemented dynamic text ellipsis truncation for long item names before the buy button, eliminating text overlaps.
- **Settings UI Ergonomics & Persistence Guarantee**:
  - Standardized bottom navigation button layout across both Settings and Keybindings screens: Back button is anchored on the left and Reset Defaults is anchored on the right.
  - Added an in-place confirmation modal prompt before resetting defaults ("RESET ALL SETTINGS TO DEFAULTS", "Are you sure you want to reset all settings to defaults? [Confirm] [Cancel]") to prevent accidental loss of user configurations.
  - Guaranteed `saves/settings.json` persistence across game restarts by loading user configurations on launch rather than resetting to defaults when MenuManager initializes without arguments.
- **Daylight Roof Block Shadow Elimination**:
  - Updated sunlight cellular diffusion in `src/world/lighting.py` so solid surface blocks directly exposed to the open sky receive full incident daylight before light decrements downward, eliminating dark shadow bands directly above rooftops during daytime.
- **Discrete Multi-Level Camera Zoom**:
  - Added 3 discrete camera zoom levels: 1.0 (1x default), 2.0 (2x), and 3.0 (3x), togglable via configurable hotkey (Z) and in the Graphics settings tab.
  - World elements render to a crisp intermediate viewport surface scaled up to the screen, preserving native 1x resolution for UI, HUD, damage numbers, and dialogues without clipping or blur.
- **Difficulty & Menu Streamlining**:
  - Set default world creation and game difficulty to Easy across MenuManager and PotariaGame.
  - Streamlined World Selection card subtitle formatting by removing redundant "· ADVENTURE" mode text.
- **Cinematic Death & Respawn Transition**:
  - Replaced high-speed camera panning across chunks upon player death with a smooth 3.0s cinematic pitch-black transition (fade to black, instant teleport and instant camera snap to spawn while fully black, smooth fade in from black).
- **Culinary Overhaul & Authentic Filipino Food Assets**:
  - Implemented authentic Filipino cuisine dishes, ingredients, and cooking recipes (Sinigang, Adobo, Kare-Kare, Lechon, Halo-Halo, Pancit, Lumpia, Taho, and more) prepared at cooking stations with unique culinary buffs and restorative properties.
  - Synthesized dedicated HD procedural pixel-art assets for raw and cooked Pinoy dishes and integrated them into the culinary cookbook system.
- **Tree-Specific Sapling Types & Maturation Animations**:
  - Implemented dedicated sapling variants for each arboreal species (Oak, Pine, Palm, Blight) with corresponding tile IDs (`TILE_SAPLING_OAK`, `TILE_SAPLING_PINE`, `TILE_SAPLING_PALM`, `TILE_SAPLING_BLIGHT`).
  - Added multi-frame shimmering growth ring animations and biome-matching atmospheric particles during tree development.
- **Tree-Specific Wood & Leaves Foliage**:
  - Added dedicated wood blocks, trunk textures, and leaf variants matching each tree species (`oak_wood`, `pine_wood`, `palm_wood`, `blight_wood`, and their respective foliage blocks).
  - Ensured cross-biome growth, felling drops, and foliage leaf debris particles correspond accurately to the specific harvested tree species.
- **Automated Verification**:
  - Created automated test suite in `tests/test_gameplay_and_ui_overhauls.py` validating all gameplay, UI, visual, and persistence overhauls. 621 tests passing across 39 test suites (100% Green).

---

### [v1.8.0] — Phase 1 Data-Driven Loot & Multi-Affix System, Lantern Ceiling Physics & World Rename
*Release Date: October 2026*

#### Added
- **Data-Driven Item Registry (`src/loot/item_registry.py`)**:
  - Standardizes all 1,461 registered items (including all 129 craftable recipes from `src/ui/crafting.py` and 1,337+ droppable items) into canonical `ItemDefinition` schemas across 9 categories (`weapon`, `armor`, `accessory`, `consumable`, `material`, `ammunition`, `skillbook`, `quest_key`, `relic`).
  - Preserves 100% compatibility with `ITEM_REGISTRY`, save files, and `/give`.
- **4-Layer Item Model & Multi-Affix Engine (`src/loot/affix_engine.py`, `src/loot/rarity_engine.py`, `data/affixes/affixes.json`)**:
  - Implements `BASE ITEM + AFFIXES + RARITY + OPTIONAL UNIQUE EFFECT`.
  - Includes all 9 canonical affixes (`Vampiric`, `Burning`, `Frozen`, `Swift`, `Heavy`, `Piercing`, `Rootbound`, `Astral`, `Blighted`) plus 4 thematic suffixes (`of the Root`, `of the Blight`, `of the Cosmos`, `of the Vanguard`).
  - Enforces category compatibility, rarity slot budgets (`Common: 0` through `Ancient: 6`), mutual exclusion (`Burning`/`Frozen`, `Swift`/`Heavy`, `Rootbound`/`Blighted`), deterministic seeded rolling (`rng_seed`), dynamic prefix/suffix naming, and stat merging.
- **3-Path Loot Acquisition (`src/loot/loot_system.py`, `data/loot_tables/loot_tables.json`)**:
  - Path 1: Random category/level-filtered drops (`roll_random_loot`).
  - Path 2: Targeted boss and biome drop tables (`roll_targeted_loot`).
  - Path 3: Guaranteed milestone drops (`get_guaranteed_milestone_loot`).
- **Dedicated Lantern World Tiles & North Ceiling Hanging Physics (`src/constants.py`, `src/assets/asset_factory.py`, `src/ui/inventory.py`, `src/world/world.py`)**:
  - Assigned dedicated tile IDs (`TILE_CARVED_TUBER_LANTERN = 51`, `TILE_BRASS_LANTERN = 52`, `TILE_SPECTRAL_LANTERN = 53`) so placing a Carved Tuber Lantern (or Brass/Spectral Lantern) places the actual lantern tile sprite in the world and drops the lantern item back when mined, rather than placing a Torch (`TILE_TORCH`).
  - Added ceiling hanging placement physics allowing lanterns (`LANTERN_TILES`) to be placed at the ceiling when there is a solid block to the North (`ty - 1`), on a floor/platform below (`ty + 1`), or on a background wall, automatically detaching if their supporting block is destroyed.
- **Interactive World Rename in World Selection (`src/world/save_manager.py`, `src/ui/menu.py`)**:
  - Added `rename_world(old_name, new_name)` and `can_rename_world(old_name, new_name)` in `src/world/save_manager.py` and interactive `RENAME` buttons + modal text input in the World Selection screen (`STATE_WORLDS`).
  - Strictly blocks renaming if the target world name already exists (case-insensitive) or is empty, displaying a clear error notice in the UI while preserving existing worlds intact.
- **Automated Verification (`tests/test_loot_and_affix_phase1.py`, `tests/test_lantern_and_world_rename.py`)**:
  - Added unit and integration tests verifying Phase 1 itemization, affixes, loot tables, Carved Tuber Lantern ceiling placement/mining, and World Rename duplicate-name protection (360 total tests passing across 28 suites).

### [v1.7.1] — Stage 2 Hardware Acceleration, GLSL Bloom Shaders & Projectile Batching
*Release Date: October 2026*

#### Added
- **ModernGL 5.13 Hardware Acceleration**:
  - Full integration and verification of `moderngl 5.13.0` and `glcontext 3.1.0` in Python 3.13.
  - Real hardware rendering verified on Intel Iris Xe Graphics with zero driver conflicts.
  - Headless/dummy driver resilience: automatic graceful fallback to `SurfaceRenderer` when running under `SDL_VIDEODRIVER=dummy` or non-accelerated environments.
- **GLSL Bloom Post-Processing Shader Pipeline**:
  - Custom GLSL fragment shader performing dynamic luminance threshold extraction (`u_bloom_threshold`), 9-tap 2D Gaussian kernel blur, and radiant pulse shimmer (`u_bloom_intensity`, `u_time`).
  - Fullscreen post-processing applied during `present()` over the scene framebuffer texture.
  - Enhances Ancient and Mythic weapon/armor radiant visual auras, celestial star trails, and bullet-hell boss danmaku projectiles with an ethereal glow.
  - Dedicated bloom configuration controls (`set_bloom_enabled`, `set_bloom_intensity`, `set_bloom_threshold`, `get_bloom_params`) implemented across `GLRenderer`, `SurfaceRenderer`, and `RendererManager`.
  - In-game interactive bloom toggle button (`[BLOOM SHADERS: ON / OFF]`) wired directly in Settings menu and persisted under `"bloom": true` in `saves/settings.json`.
  - State-preserving renderer switching in `RendererManager` maintaining active bloom parameters across backend toggles.
- **High-Density Projectile Batch Rendering**:
  - Implemented `draw_projectiles_batch` across `GLRenderer`, `SurfaceRenderer`, and `RendererManager`.
  - Hardware and software backends utilize optimized multi-blitting (`fblits`) with viewport frustum culling.
  - Fully integrated into `Boss.render`, `MiniBoss.render`, and `CombatSystem.render` to batch-render all boss and enemy danmaku projectiles (`BossProjectile`) in a single draw pass.
  - Added support for both `(x, y)` and vector `pos` projectile data structures.
  - Real-time batch metrics tracking (`last_batch_count`, `total_batched_projectiles`) for performance monitoring.
- **Single-Log Fallback Deduplication**:
  - Added `_logged_fallback` class-level flag to `GLRenderer` to ensure fallback warnings are logged only once during game startup or world loads, completely eliminating repetitive console warning spam.

#### Verified & Tested
- Comprehensive unit tests in `tests/test_renderer_hal.py`:
  - `test_glsl_bloom_shader_pipeline_configuration`: Validates fragment shader compilation, uniform bindings, and toggling logic.
  - `test_real_glsl_bloom_shader_compilation`: Validates real ModernGL context shader compilation syntax and uniform locations directly from production shader constants.
  - `test_projectile_batch_rendering_hardware`: Validates batch culling, coordinate projection, and metric tracking.
  - `test_projectile_batch_pos_attribute_support`: Validates that Vector2 pos projectiles are frustum culled and batched.
  - `test_boss_projectiles_batch_rendering`: Validates that DungeonMiniBoss and GrandBossSolRho batch projectiles through renderer HAL.
  - `test_fallback_warning_logged_only_once`: Validates fallback log deduplication.
  - `test_surface_renderer_batch_and_bloom`: Validates software fallback batching and bloom state queries.
  - `test_manager_batch_and_bloom_delegation`: Validates transparent manager delegation.
  - `test_manager_preserves_bloom_settings_across_switch`: Validates state-preserving bloom parameter retention.
  - `test_menu_settings_bloom_toggle`: Validates in-game Settings menu bloom toggle button and disk persistence.
- 338 tests passing across 26 test suites (100% Green).

### [v1.7.0] — Renderer Hardware Abstraction Layer (HAL), Smart OpenGL Architecture & Dual-Profile Franchise Model
*Release Date: October 2026*

#### Added
- **Renderer Hardware Abstraction Layer (HAL)**:
  - Created modular rendering package `src/rendering/` decoupling high-level game logic from low-level display drivers.
  - Implemented `BaseRenderer` abstract base class defining unified drawing contracts:
    - `draw_sprite(surface, dest, area, special_flags)`
    - `draw_surface(surface, dest, area, special_flags)`
    - `draw_rect(color, rect, width, border_radius)`
    - `draw_text(font, text, pos, color, antialias)`
    - `draw_line(color, start_pos, end_pos, width)`
    - `draw_circle(color, center, radius, width)`
    - `clear(color)`
    - `present()`
    - `get_surface()`
    - `set_mode(width, height, fullscreen)`
  - Implemented `SurfaceRenderer`: wraps native Pygame-ce software blitting with 100% backward compatibility and exact visual parity.
  - Implemented `GLRenderer`: hardware-accelerated OpenGL / ModernGL backend with safe context detection, texture caching, and automatic graceful fallback to `SurfaceRenderer` if GPU context fails or ModernGL/PyOpenGL is missing.
  - Implemented `RendererManager`: centralized factory holding active renderer instance, managing runtime backend toggling, and reporting operational status.

- **In-Game Video Settings & Settings Persistence**:
  - Added renderer preference key `"renderer": "hardware" | "software"` to `saves/settings.json`.
  - Added interactive toggle button in the Settings menu: `Renderer: [Hardware (ModernGL) / Compatibility (Software)]`.
  - Real-time renderer switching without restarting the game or losing player session state.

- **Franchise Architecture: One Project Repository (Dual-Profile)**:
  - Ratified unified single repository structure housing both franchise profiles:
    - **Potaria (The Base Game)**: Boundless 2D procedural sandbox, survival, digging, building, 129 crafting recipes, casual 1-5 player LAN co-op, and Last Man Standing (LMS) arena combat.
    - **Potaria: Root Realm (The Flagship ARPG Franchise)**: Narrative-driven campaign chapters, Heartroot world transformation mechanics, POTAdex journal, curated puzzle dungeons, and dramatic boss encounters.

- **Comprehensive Automated Regression Coverage**:
  - Implemented `tests/test_renderer_hal.py` verifying BaseRenderer interface compliance, SurfaceRenderer drawing operations, GLRenderer fallback behavior, settings persistence, and renderer switching.
  - Verified 100% green pass rate across all 26 test suites (328 tests).

### [v1.6.0] — Animated Specialized Traders, Shop Tooltips, Crafting Directory, Auto-Hiding Console & Torch Physics
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

- **Dedicated Directory for Craftable Items & Assets**:
  - Created a dedicated crafting catalog directory, isolating craftable items from the 1,100+ droppable items catalog for effortless inspection and balancing.
  - Established dedicated asset directories isolating all 129 craftable item sprite assets from droppable item sprites, enabling immediate visual inspection and modding.
  - Separated droppable item assets so droppable and craftable catalogs remain strictly distinguished without mixing.
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
  - Created comprehensive unit tests verifying 3 trader archetypes, animation frames, 64x64 portraits, single-trader spawning, 15-35 block distant spawn, 3-block turtle shield radius, 1 Gold repair, shop hover tooltips, craftable items JSON loading, console auto-hide, torch placement rules, and dedicated craftable asset directory separation.
  - Full project test suite passed 100% green across 309 tests in 25 test suites (`Ran 309 tests in 131.512s, OK`).

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
