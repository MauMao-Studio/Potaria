# SPUD: ROOT REALM (POTARIA)
## Master Game Design Document (GDD)

**Developer:** Kurados  
**Genre:** 2D Sandbox Action RPG  
**Subgenre:** Survival • Exploration • Crafting • Dungeon Crawler • Character Progression • Cooperative Multiplayer  
**Perspective:** 2D Side-View  
**Core Inspiration:** Terraria-style sandbox exploration + Chroisen-style Action RPG equipment & skills  
**Target Platform:** PC (Pygame-ce Community Edition Engine, 100% Offline Standalone)  
**Player Mode:** Single-Player & 1–5 Player LAN Cooperative Multiplayer  
**World Structure:** Infinite procedurally generated chunk-based open world + Subterranean Arenas & Nether Dungeon  

---

# 1. GAME VISION

**SPUD: Root Realm (Potaria)** is a 2D sandbox action RPG where the player controls **SPUD**, a humble potato destined to cleanse the Root Realm of primordial corruption and celestial blight.

The player explores an infinite, boundless procedurally generated world, gathers resources, constructs fortified settlements, crafts hundreds of weapons and armor sets, masters 40 RPG skills from ancient Skill Books, defeats subterranean mini-bosses, and challenges the cosmic ruler **Sol-Rho The Celestial Titan**.

### Core Pillars:
- **Boundless Sandbox**: Continuous multi-octave Perlin noise chunks with zero artificial borders ($-\infty \leftarrow 0 \rightarrow +\infty$).
- **Deep RPG Customization**: Chroisen-style paperdoll slots, layered armor sets with set bonuses and radiant pulsing auras, and 100 character levels.
- **Diverse Combat Archetypes**: Melee blades, ballistics-driven archery with ammo variants, homing catalysts, piercing rods, elemental staves, and shockwave scepters.
- **Visual Grandeur**: Procedural animated visual effects (100+ frames), screen shake, glowing aura mandalas, and orbital starlight motes.
- **Balanced Pacing**: Morning Peace for peaceful daytime gathering, escalating night danger, and rewarding grind with ultra-rare ancient drops.
- **LAN Cooperative Multiplayer**: Host-authoritative server supporting 1–5 players with nearest-player targeting and dynamic boss scaling.
- **Developer Debug Suite**: Full in-game cheat console for testing and content showcase.

---

# 2. STORY & LORE

### 2.1 The Root Realm & The Heartroot
Long ago, the ancient **Starchlands of Potaria** thrived beneath the nurturing glow of the **Heartroot**, a colossal living starch core radiating life force to all vegetable kind.

### 2.2 The Corruption of Lord Malus
Deep beneath the mantle, **Lord Malus**, an ancient root guardian, sought to siphon the Heartroot's cosmic starch. The unstable power decayed his flesh into an abomination of blight. Bound within the Nether Dungeon, Malus unleashes hordes of zombies, corrupted slimes, and demon eyes into the surface world.

### 2.3 Sol-Rho The Celestial Titan
Beyond the subterranean darkness lies the cosmic architect: **Sol-Rho The Celestial Titan**. Wielding solar fire and gravitational pulses, Sol-Rho judges mortal civilizations. Only a hero clad in full Ancient Relic armor wielding cosmic weaponry can stand before Sol-Rho's two-phase celestial trial.

---

# 3. PLAYER ATTRIBUTES & RPG SCALING

Spud's progression follows a 100-level Action RPG curve with dedicated stat point allocation:

| Attribute | Base | Scaling / Effect |
|---|---|---|
| **Level** | 1 | 1 to 100 max; siphons EXP from monster and boss takedowns |
| **HP (Health)** | 100 | Scaled by Base HP + Armor bonuses + Set effects; zero HP enters downed/respawn state |
| **MP (Mana)** | 50 | Scaled by Gear + Passives; base 1.5 MP/s natural regeneration; fuels spells & skills |
| **ATK (Physical)**| 10 | Primary damage multiplier for melee swords, axes, spears, and bows |
| **DEF (Defense)** | 2 | Mitigates damage: $\text{Damage Taken} = \max(1, \text{Enemy ATK} - \text{DEF})$ |
| **Crit Rate** | 5.0% | Chance to deal 1.5x–2.0x golden damage numbers |
| **Speed** | 3.0 | Movement velocity; boosted by boots, french fries, and set bonuses |
| **Attack Speed** | 1.0x | Modifies weapon swing and cast recovery rates |

---

# 4. CHROISEN-STYLE RPG EQUIPMENT & ARMOR SETS

Equipment is managed through a comprehensive paperdoll inventory system:
- **Head**: Potato Cap, Wooden Helmet, Copper Helmet, Iron Helmet, Gold Helmet, Ancient Helmet, Titan Helmet, Magma Helmet, Cryo Helmet, Shadow Helmet, Cactus Helmet.
- **Chest**: Potato Tunic, Wooden Chestplate, Copper Chestplate, Iron Chestplate, Gold Chestplate, Ancient Chestplate, Titan Chestplate, Magma Chestplate, Cryo Chestplate, Shadow Plate, Cactus Chestplate.
- **Legs**: Potato Pants, Wooden Greaves, Copper Greaves, Iron Greaves, Gold Greaves, Ancient Greaves, Titan Greaves, Magma Greaves, Cryo Greaves, Shadow Greaves, Cactus Greaves.
- **Weapon**: Active weapon slot with on-hand rendering.
- **Accessories**: 6 accessory slots supporting charms, rings, quivers, boots, and shields.

### 4.1 Thematic Equipment Sets & Radiant Pulsing Auras

When a player equips a complete 3-piece armor set (Head, Chest, Legs), a powerful set bonus activates alongside a dynamic glowing visual aura rendered around Spud:

| Set Name | Pieces Required | Set Bonus Effects | Active Visual Aura |
|---|---|---|---|
| **Ancient Resonating Set** | Ancient Helmet, Chestplate, Greaves | **+35% ATK, +30% DEF, +50 Max HP, +20% Crit Rate** | Radiant golden-crimson celestial aura with orbiting starlight motes |
| **Celestial Titan Set** | Titan Helmet, Chestplate, Greaves | **+25% DEF, +30 Max HP, +15% ATK** | Celestial blue aegis ward aura with defensive halos |
| **Magma Core Set** | Magma Helmet, Chestplate, Greaves | **+20% ATK, +15 Reflected Fire Thorns, +25 HP** | Pulsing fiery orange molten aura with floating embers |
| **Cryo Carapace Set** | Cryo Helmet, Chestplate, Greaves | **+20% DEF, +2.5 MP/s Regen, +35 HP** | Cyan permafrost glacial aura with freezing frost motes |
| **Umbral Shadow Set** | Shadow Helmet, Shadow Plate, Shadow Greaves | **+20% Crit, +20% ATK, +0.2 Move Speed, +20 HP** | Dark violet void phantom aura |
| **Spud Sovereign Set** | Potato Cap, Potato Tunic, Potato Pants | **+30 Max HP, +5 HP/s Regen, +10% ATK, +10% DEF** | Emerald green earth sprout aura with botanical particles |
| **Cactus Needle Set** | Cactus Helmet, Chestplate, Greaves | **+15 Reflected Thorns, +10% ATK, +10% DEF** | Prickly amber desert spine aura |

### 4.2 Drop Rates & Economy Rebalance

To make item acquisition rewarding and grinding purposeful over hours, days, and months, equipment drop rates follow strict rarity weighting:

| Rarity Tier | Drop Chance | Visual Color | Characteristics |
|---|---|---|---|
| **Common** | 98.69% | `#FFFFFF` White | Baseline equipment and craftable tools |
| **Uncommon** | 1.0% | `#4CAF50` Green | Modest stat additions (+1 affix) |
| **Rare** | 0.25% | `#2196F3` Blue | Enhanced combat attributes (+2 affixes) |
| **Epic** | 0.05% | `#9C27B0` Purple | Specialized passive traits (+3 affixes) |
| **Mythic** | 0.008% | `#F44336` Crimson | Endgame dungeon boss drops |
| **Legendary**| 0.002% | `#FF9800` Gold | Unique active weapon abilities |
| **Ancient** | **0.0004%** | `#FFD700` Relic Gold | Mythological relics (1 in 250,000); unlocks `rarity_ancient` achievement, celebratory fanfare, ancient discovery VFX, & screen shake |

---

# 5. WEAPON ARCHETYPES, BALLISTICS & ATTACK SPEEDS

### 5.1 Long-Range Weapon Archetypes

1. **Bows & Archery Ammo System (Shortbows, Recurves, Longbows, Composite Bows)**:
   - Arrows utilize sub-pixel `pygame.FRect` + `Vector2` physics subject to realistic downward gravity ($g = 140\text{ px/s}^2$).
   - **Composite Bows**: Multi-layered horn/timber bows with higher arrow velocities (`composite_bow`, `reinforced_composite_bow`, `ancient_composite_bow`).
   - **Ammo Priority**: Bows automatically consume arrows from inventory in descending order of power:
     $$\text{Astral Arrow} > \text{Frostburn Arrow} > \text{Flame Arrow} > \text{Wooden Arrow}$$
   - **Ammo Types**:
     - *Wooden Arrow*: Baseline arrow (+0 bonus damage).
     - *Flame Arrow*: Inflicts fire damage (+6 dmg) and burning status ticks.
     - *Frostburn Arrow*: Inflicts freezing chill (+8 dmg) and slows enemy movement.
     - *Astral Arrow*: Starlight velocity (+14 dmg) with zero gravity drop-off.
   - **Relic Bows**: Weapons like *Ancient Eternal Shortbow*, *Ancient Composite Bow*, and *Celestial Bow* channel ethereal starlight, firing astral projectiles even when conventional arrows are exhausted.

2. **Magic Catalysts**:
   - Casts celestial homing stars (`CatalystStarProjectile`).
   - Features autonomous steering vectors toward the closest hostile mob or active boss.
   - Strict range cap of **560 pixels** to prevent off-screen cheese.

3. **Magic Staves**:
   - Projects concentrated elemental bolts (`StaffBoltProjectile`) across Arcane, Frost, Fire, and Nature affinities.
   - High velocity with custom status application upon impact; capped at **560 pixels** range.

4. **Magic Rods**:
   - Launches high-velocity piercing javelins (`RodJavelinProjectile`).
   - Penetrates through up to **3 consecutive enemies** before expiring; capped at **560 pixels** range.

5. **Magic Scepters**:
   - Releases expanding radial shockwave pulses (`ScepterPulseProjectile`).
   - Deals area-of-effect damage to closely packed swarms; capped at **560 pixels** range.

### 5.2 Weapon Attack Speeds & Anti-Spam Tuning

Weapon attack speeds are calibrated to deliver deliberate combat weight and prevent spamming:
- **Shortswords / Daggers**: $0.22\text{s}$ base cooldown (quick agile slashes).
- **Broadswords / Battleaxes**: $0.32\text{s}$ base cooldown (balanced strikes).
- **Greatswords / Warhammers**: $0.46\text{s}$ base cooldown (heavy crushing blows).
- **Bows (including Composite Bows)**: $0.52\text{s}$ base cooldown (calibrated draw cadence).
- **Magic Weapons (Catalysts, Staves, Rods, Scepters)**: $0.54\text{s}$ base cooldown (focused spellcasting channel).

---

# 6. SKILL SYSTEM & ANIMATED VFX PIPELINE

### 6.1 40-Skill Roster
Skills are acquired by reading **Skill Books** discovered in ancient ruins chests and dropped by dungeon bosses:
- **Warrior (10)**: Power Slash, Heavy Strike, Whirlwind, Shield Bash, Ground Slam, Charge, Uppercut, Blade Storm, Berserk, Last Stand.
- **Ranger (8)**: Rapid Shot, Piercing Shot, Multi Shot, Explosive Arrow, Rain of Arrows, Hunter's Mark, Critical Shot, Phantom Arrow.
- **Mage (10)**: Magic Missile, Fireball, Ice Shard, Lightning Bolt, Root Bind, Fire Nova, Arcane Burst, Blight Storm, Nether Beam, Nether Explosion.
- **Survival (6)**: Efficient Mining, Lumberjack, Forager, Treasure Hunter, Cook's Knowledge, Resourceful.
- **Mobility (6)**: Dash / Roll, Double Jump, Air Dash, Wall Climb, Blink, Nether Step.

### 6.2 Animated VFX Pipeline
- **VisualEffectManager & AnimatedVFX**: Handles complex multi-frame particle animations, screen flashes, and shockwave halos.
- **Procedural & Offline Synthesis**: 100+ frames of animated visual effects synthesized procedurally at launch with offline fallbacks.
- **Dynamic Anchoring**: Effects can be locked to world coordinates or anchored dynamically to living entities.
- **Screen Shake Integration**: Heavy impacts (e.g. Celestial Greatsword swing, ancient relic discovery, boss roars) trigger camera trauma shake.

---

# 7. INFINITE BOUNDLESS WORLD & TIME-OF-DAY DYNAMICS

### 7.1 Boundless Generation
The world generates dynamically via 16-block wide chunks with continuous multi-octave Perlin noise. The coordinate space is boundless horizontally ($-\infty \leftarrow 0 \rightarrow +\infty$).

### 7.2 Time-of-Day Pacing: Morning Peace vs. Night Danger
The in-game sky clock progresses cyclically from $0.0$ to $1.0$:

- **Morning Peace ($0.0 \le t < 0.22$)**:
  - Surface monster spawn rate is set to **0**.
  - Players can safely mine, harvest timber, farm crops, and construct homes without harassment.
- **Midday ($0.22 \le t < 0.50$)**:
  - Gentle surface wildlife and occasional green slimes roam the plains.
- **Night Peak ($0.50 \le t < 1.0$)**:
  - Aggressive undead spawn en masse: Zombies, Rock Zombies, Demon Eyes, and Shadow Crawlers.
  - Subterranean depths remain perilous regardless of surface time.
- **Sheltered Housing Protection**:
  - Monster spawning is strictly suppressed inside enclosed structures featuring placed background walls (Wood, Stone Brick, Glass) and illumination (Torches).

---

# 8. DEVELOPER DEBUG CONSOLE & CHEAT ENGINE

To facilitate rapid QA verification and sandbox experimentation, an integrated developer console is built into the engine.

### 8.1 Console Access
Press **`Enter`**, **`/`**, or **`~` (Tilde)** during active gameplay to open the command console.

### 8.2 Command Reference
| Command | Syntax | Description |
|---|---|---|
| `/god` | `/god` | Toggles God Mode (invulnerability, continuous full HP/MP restoration) |
| `/heal` | `/heal` | Instantly restores maximum Health, Mana, and Oxygen |
| `/speed` | `/speed [mult]` | Sets movement speed multiplier (e.g. `/speed 3.0`) |
| `/time` | `/time <preset\|0.0-1.0>` | Sets time of day (`morning`, `day`, `dusk`, `night`, or float) |
| `/give` | `/give <item_id> [count]` | Spawns specified quantity of any catalog item directly to inventory |
| `/ancient` | `/ancient` | Equips full Ancient Set, activates pulsing aura, grants 250 Astral Arrows & Relic weapons |
| `/weapons` | `/weapons` | Fills inventory with complete showcase pack of bows, arrows, and magic weapons |
| `/spawn` | `/spawn <mob\|boss> [count]` | Spawns specified enemies or bosses (`slime`, `zombie`, `malus`, `sol_rho`) |
| `/killall` | `/killall` | Clears all active hostile mobs, enemy projectiles, and active bosses |
| `/level` | `/level [count]` | Levels up Spud by specified increments, increasing base attributes |
| `/clear` | `/clear` | Empties all inventory and held item slots |
| `/help` | `/help` | Displays available cheat command listings in system chat |

*Detailed instructions and full item IDs are documented in `CHEATS.md`.*

---

# 9. LAN COOPERATIVE MULTIPLAYER (1 TO 5 PLAYERS)

- **Network Architecture**: Host-authoritative LAN socket server.
- **Party Scalability**: Seamless support for 1 Host + up to 4 Client players over local Wi-Fi or Ethernet.
- **Dynamic Boss Scaling**: Boss HP scales from 100% (solo) up to 350% (5 players); boss ATK scales from 100% up to 140%.
- **Nearest-Player Targeting**: Host AI evaluates Euclidean distance to all active party members, directing mob aggro to the closest threat.
- **Individual Loot Drops**: Drop tables roll independently per player to prevent resource hoarding.
- **In-Game Chat**: `Enter` key enables cross-player communication with system broadcast tags.

---

# 10. BOSS PROGRESSION & CLIMAX

### 10.1 Subterranean Mini-Bosses
1. **Lord Malus The Blight-Bringer** (Underground Crypts): Rot spits, sweeping cleaves, and summonable blight slimes.
2. **Ignis Colossus The Magma Golem** (Cavern Lava Pools): Scorching ground slams, magma projectiles, and fire waves.
3. **Cryo-Spud The Glacial Terror** (Snow Biome Depths): Freezing blizzards, icicle spears, and permafrost barriers.
4. **Necro-Tuber The Crypt Fiend** (Deep Dungeon): Bone volleys, life drain, and teleportation.

### 10.2 Grand Boss: Sol-Rho The Celestial Titan
The culmination of Potaria's campaign:
- **Phase 1: Celestial Form (1000 HP)**: Levitates above the arena, firing tracking celestial stars, solar flare shockwaves, and orbital lasers.
- **Phase 2: Enraged Supernova (1400 HP)**: Descends into high-speed dive attacks, gravitational vortex singularity pulls, and relentless screen-shaking solar bursts.
- **Rewards**: Slain Sol-Rho yields the legendary *Crown of Potaria*, *Astral Wrath*, Celestial Portal Shards, and royal fortunes in coin.

---

# 11. CONTROLS SUMMARY

- **Movement**: `A` / `D` or Left / Right Arrows
- **Jump**: `W` / Space / Up Arrow
- **Drop Through Platforms**: `S` + Jump or Down Arrow
- **Primary Attack / Mine**: Left Mouse Button (Hold to continuously mine)
- **Secondary Action / Place**: Right Mouse Button
- **Inventory & Crafting**: `E` or `Esc`
- **Character Equipment & Paperdoll**: `C` (or Equipment tab in `E`)
- **Active Skills**: `Q` (Power Slash), `F` (Whirlwind), `C` (Dash), `R` (Fireball)
- **Hotbar Selection**: `1`–`9`, `0` or Mouse Scroll Wheel
- **Cheat Console / Chat**: `Enter`, `/`, or `~`
- **Toggle Fullscreen**: `F11`
- **Debug Overlay**: `F1`
