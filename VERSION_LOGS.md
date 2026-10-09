# POTARIA: ROOT REALM — VERSION LOGS & CHANGELOG
**Lead Developer:** Kurados  
**Game Engine:** Pure Python 3.13 + Pygame Community Edition (`pygame-ce` 2.5.8+, SDL 2.32)  
**Architecture:** 2D Boundless Sandbox Action RPG (100% Offline Standalone, Zero External Downloads)  
**Repository:** [RetsardCo/Potaria](https://github.com/RetsardCo/Potaria.git)  

---

## 📜 Version History Overview

| Version | Release Date | Codename / Focus | Key Milestone |
| :--- | :--- | :--- | :--- |
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

### [v1.2.1] — 1-Block Body Collider & Sprout Clearance (Current Release)
*Release Date: October 2026*

#### Changed & Fixed
- **1-Block Player Body Hitbox (`PLAYER_HEIGHT = 32`)**:
  - Re-scaled the player's physical collision bounding box from 36px to **32px** (precisely 1 tile / `SCALED_TILE`).
  - Removed collision from the top decorative potato sprout leaf, allowing Spud to freely walk under 1-block high ceiling openings, overhangs, and passages without clipping.
  - Adjusted rendering vertical offset (`draw_sy = sy - sprout_offset_y`) so the visual body and feet remain grounded on terrain while the decorative leaf renders smoothly above.
- **Multiplayer & PvP Hitbox Synchronization**:
  - Synchronized remote player hitboxes in multiplayer PvP (`rp_rect`) and projectile/fireball collisions to match the 28x32 body collider.
- **Dedicated Test Suite**: Created [`tests/test_player_collider_1block.py`](file:///C:/Users/Kurados/.gemini/antigravity/scratch/Potaria/tests/test_player_collider_1block.py) with 9 unit tests verifying 1-block tunnel traversal, jump ceiling clearance, platform drop-through, and sprout leaf projectile passthrough.

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
- **Dedicated Test Suite**: Added [`tests/test_night_sleep_elite_and_boss_buffs.py`](file:///C:/Users/Kurados/.gemini/antigravity/scratch/Potaria/tests/test_night_sleep_elite_and_boss_buffs.py) with 18 comprehensive unit tests.

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
- **Dedicated Drop Rate Test Suite**: Created [`tests/test_drop_rates.py`](file:///C:/Users/Kurados/.gemini/antigravity/scratch/Potaria/tests/test_drop_rates.py) providing empirical statistical verification across 20,000 mob kills and 500 chest openings.

#### Changed & Balanced
- **Monster Drop Rates Recalibration (Option 2: Moderate ARPG)**:
  - **Uncommon Gear**: Increased from 1.0% (1 in 100) to **3.5% (1 in ~28)**.
  - **Rare Gear & Skills**: Increased from 0.25% (1 in 400) to **1.5% (1 in ~67)**.
  - **Epic Gear**: Increased from 0.05% (1 in 2,000) to **0.50% (1 in 200)**.
  - **Mythic Relics**: Increased from 0.008% (1 in 12,500) to **0.15% (1 in ~667)**.
  - **Legendary Artifacts**: Increased from 0.002% (1 in 50,000) to **0.05% (1 in 2,000)**.
  - **Ancient Relics**: Increased from 0.0004% (1 in 250,000) to **0.01% (1 in 10,000)**.

#### Fixed
- **Windows Terminal Charmap Encoding**: Replaced Unicode stars (`★★★`) with ASCII asterisks (`***`) in drop announcement logs to eliminate `UnicodeEncodeError (cp1252)` on Windows consoles.
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
  - Script [`scripts/generate_items_pdf.py`](file:///C:/Users/Kurados/.gemini/antigravity/scratch/Potaria/scripts/generate_items_pdf.py) generating `Potaria_Items_Catalog.pdf`, documenting all 1,100+ weapons and equipment with item codes, stats, and asset previews.
- **Dedicated Single-Target Test Suite**: Created [`tests/test_single_target_combat.py`](file:///C:/Users/Kurados/.gemini/antigravity/scratch/Potaria/tests/test_single_target_combat.py) testing melee, archery, javelin, and shockwave behaviors.

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
- **Real-Time F3 Telemetry Profiler**: Injected lightweight sub-millisecond instrumentation tracking Input, Player, AI, World Simulation, Chunk Rendering, Dynamic Lighting, and Present times.
- **Asynchronous Chunk Streaming**: Replaced synchronous chunk generation with background ThreadPool workers, eliminating 250ms movement stutter when traversing chunk boundaries.
- **Pre-computed Starfield Layers**: Pre-rendered twinkling nighttime star layers in `sky.py`, eliminating per-frame trigonometric calculations.

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
- **Touch Settings Customization**: Configurable Touch Controls mode (`Auto`, `On`, `Off`) and opacity slider (`50%`, `75%`, `100%`) persisted in `saves/settings.json`.

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
- **200+ Achievements**: Created `data/achievements.json` tracking Combat, Mining, Crafting, Leveling, and Survival milestones with animated toast popups.

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
  - Full voice narration with offline procedural audio synthesizer and optional Google Gemini TTS integration.
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
  - `data/weapons.json` (550+ weapons) and `data/equipments.json` (550+ armor and accessories).
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
- Initial enemy AI: Green Slimes and surface Zombies.
