"""
Potaria Documentation Generator - Section 2: System-by-System Deep Technical Architecture Breakdown
Developer: Kurados
Strict Constraints: NO emojis, relative paths only.
"""

def build_section_2():
    return """## 2. System-by-System Deep Technical Architecture Breakdown

### 2.1 World Generation, Infinite Chunk Streaming & Procedural Terrain
- **Coordinate Space & Scale**: The world operates on a discrete grid where each block is 16x16 pixels in source art, scaled by 2x to 32x32 screen pixels (`SCALED_TILE = 32`). The horizontal dimension is boundless ($-\\infty \\leftarrow 0 \\rightarrow +\\infty$), structured into column chunks of 16 tiles wide by 240 tiles deep (`ChunkWidth = 16`, `ChunkHeight = 240`).
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
    1. Dawn ($0.00 \\le T < 0.25$): Amber morning sky gradient, rising sun, ambient light rising from 0.35 to 1.00.
    2. Noon ($0.25 \\le T < 0.50$): Azure midday sky, full illumination, ambient light at 1.00.
    3. Sunset ($0.50 \\le T < 0.75$): Crimson and purple dusk horizon, setting sun, ambient light decaying from 1.00 to 0.25.
    4. Night ($0.75 \\le T < 1.00$): Midnight indigo abyss, rising lunar crescent, 140 twinkling star sprites, ambient light at 0.15. Hostile surface mobs spawn (Zombies, Demon Eyes).
- **Subterranean Darkness & Radial Point Lights**:
  - As depth exceeds $Y = 85$, surface sunlight attenuates quadratically. Caverns at $Y \\ge 160$ are pitch-black (`Light = 0`).
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
"""

if __name__ == "__main__":
    print(build_section_2()[:200])
