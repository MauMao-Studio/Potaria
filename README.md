# Potaria - The Spudtastic Adventure

**Developer:** Kurados  
**Engine:** Python 3 + Pygame Community Edition (`pygame-ce` 2.5.8+ with SDL 2.32, Pure Python, 100% Offline, Zero External Asset Downloads)

---

## 🥔 Overview

**Potaria** is a boundless 2D sandbox action RPG developed by **Kurados**. You play as **Spud** — an ordinary potato who sprouted with an extraordinary destiny! Explore a truly **infinite, boundary-free open world** populated by diverse biomes, mine valuable ores, discover hidden underground treasure chests, level up your RPG character from Level 1 to 100, equip tiered armor, weapons, and accessories in a classic Chroisen-style paperdoll system, wield ballistic bows and celestial magic starfury swords, master devastating Skill Book spells, listen to dynamic 16-second cinematic procedural synth soundtracks, battle subterranean Mini-Bosses to gather **Portal Shards**, assemble the **Celestial Keystone**, and confront the ultimate two-phase Souls-like Grand Boss: **SOL-RHO THE CELESTIAL TITAN** — solo or in **LAN Cooperative Multiplayer (1 to 5 Players)**!

---

## 🌟 Pygame-ce Engine Upgrades & High-Definition Visuals

Potaria is powered by **Pygame Community Edition (`pygame-ce` 2.5.8+)**, introducing state-of-the-art modern graphics, physics, and audio improvements:

1. **High-Definition (HD) Fullscreen Scaling**:
   - Configured with `SDL_RENDER_SCALE_QUALITY = "best"` hardware texture interpolation, ensuring crisp UI, high-definition fonts, and smooth presentation across all 1080p, 1440p, and 4K fullscreen displays (`F11`).
2. **Fluid 12 FPS Traditional Animation Cycle**:
   - **Spud Walk Cycle**: 8 distinct articulated animation frames at 12 FPS (`1.0 / 12.0 = 0.0833s` per frame) featuring bouncy boot steps, squash/stretch dynamics, and reacting sprout leaf physics.
   - **Breathing & Blinking Idle**: 6-frame idle animation with subtle breathing, chest expansion, and natural blinking.
   - **Dynamic Airborne Poses**: Distinct jump upward stretch and aerodynamic downward falling frames.
   - **14 Bestiary Animation Sets**: 6-frame bouncy Slimes, 6-frame shambling Zombies & Mummies, 6-frame pulsating Demon Eyes, flapping Bats, and scuttling Crawlers.
3. **Sub-Pixel Floating Point Physics (`pygame.FRect`)**:
   - Eliminates rounding jitter on slopes, jumps, and high-velocity dashes.
   - Ground collision detection continuously grounds entities with zero oscillation.
4. **Ballistic Projectiles & Celestial Magic (`pygame.math.Vector2`)**:
   - **Wood Bow & Bone Bow**: Fires ballistic arrows with real parabolic gravity arcs that embed cleanly into solid terrain. Requires ammunition (`wooden_arrow` or `frostburn_arrow`) — no unlimited arrows without crafting ammo!
   - **Starfury Sword**: Swings a golden-hilted azure blade while summoning celestial stars that plunge from the heavens toward the mouse cursor, bursting with 72px AoE radial explosions and screen shake.
5. **16-Second Cinematic Multi-Track BGM & 3D Spatial Stereo Sound Engine (`pygame.mixer`)**:
   - Upgraded from short loops to 16.0-second multi-voice orchestral loops synthesized in pure Python with dynamic crossfading across biomes, caverns, subterranean mini-bosses, and the 2 phases of Grand Boss Sol-Rho!
   - True 2-channel stereo sound effects with distance falloff and directional panning (-1.0 to +1.0).
6. **Atmospheric Lighting with Color Grading**:
   - Dynamic cellular lighting with time-of-day color grading: warm glowing amber dawn/dusk, deep sapphire moonlit nights, radiant midday sunlight, and eerie violet dungeon ambiance.
7. **Safe Tool Mining Mechanics**:
   - Only bare hands or mining tools (Pickaxes, Drills) can harvest tiles. Holding food, potions, armor, blocks, or weapons will never accidentally break world blocks!

---

## 📜 The Story & Dungeon Progression of Potaria

> *In the ancient starchlands of Potaria, the subterranean Nether Dungeon holds the ancient secrets of the cosmos. Cursed overlords guard the deep caverns, but they are merely gatekeepers.*
>
> *Defeating subterranean Mini-Bosses or unearthing ancient chests yields mystical **Portal Shards**. When 4 Portal Shards are united with gold and stone bricks at a Work Bench, they fuse into the **Celestial Keystone**.*
>
> *Channeling the Keystone summons the ultimate supreme deity of the heavens: **SOL-RHO THE CELESTIAL TITAN**. Only heroes who can survive his devastating two-phase Souls-like onslaught — shattering his golden solar form and vanquishing his apocalyptic Awakened Void Incarnate — can earn True Victory and claim the divine **Crown of Potaria**!*

---

## 🌍 Infinite Open World & Diverse Biomes

Potaria features an infinite chunk streaming engine (`ChunkManager`). World chunks (16 tiles wide by 240 tiles deep) are dynamically synthesized on the fly using continuous multi-octave seeded Perlin noise. There are **zero left or right bedrock walls** — you can explore endlessly in either direction!

### Biomes of Potaria:
1. **The Forest (Starchlands)**:
   - Rolling hills covered in green grass, wild potato bushes, oak trees, and daytime ambient sunlight.
   - Inhabitants: Green Slimes, Purple Slimes, surface Zombies, Demon Eyes at night.
   - BGM: Peaceful, uplifting acoustic-synth melody in C Major Pentatonic.
2. **The Desert**:
   - Dunes of golden sand and subterranean sandstone studded with prickly cacti.
   - Inhabitants: Sand Slimes, Desert Scorpions, Mummies.
   - BGM: Exotic, rhythmic Middle-Eastern inspired Phrygian dominant synth.
3. **The Snow Biome**:
   - Frost-covered snow hills and subterranean slippery ice formations.
   - Inhabitants: Frost Slimes, Frozen Zombies, Ice Bats.
   - BGM: Crystalline, twinkling high-register bells and snowy arpeggios.
4. **The Corruption (The Blight)**:
   - Malignant biome characterized by corrupt grass, dark purple ebonstone, and sinister foliage.
   - Inhabitants: Corrupt Slimes, Shadow Crawlers, Demon Eyes.
   - BGM: Dark, menacing tritone synth with haunting subterranean bass pulses.
5. **Glowing Mushroom Caverns**:
   - Underground cavern pockets overgrown with luminescent mushroom grass and giant glowing blue mushrooms that emit natural cellular light.
   - Inhabitants: Cave Bats, Skeletons, Slimes.
   - BGM: Dreamy, ambient synth pads with mysterious echoes.
6. **The Nether Dungeon**:
   - Deep subterranean fortress constructed of indestructible dungeon brick, housing the ancient Altar of Malus.
   - Inhabitants: Lord Malus the Blight-Bringer and his cursed minions.
   - BGM: Fast-paced, driving 140 BPM retro battle theme with syncopated bass.

---

## 👾 Bestiary, Subterranean Mini-Bosses & The Grand Boss

Potaria features 14 distinct monster varieties, 4 unique subterranean Mini-Bosses, and the colossal 2-phase Souls-like Grand Boss:

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
| **Demon Eye** | Night Sky (Flying) | Swooping aerial charges | Torches, Lenses, Warrior Charm |
| **Cave Bat** | Deep Caverns | Erratic flight in the dark | Torches, Lucky Clover |
| **Ice Bat** | Snow Caverns | Freezing flight dive | Frost Core, Band of Regeneration |
| **Desert Scorpion** | Desert Surface/Caves | Fast crawling strike | Cactus, Poison Glands, Hermes Boots |
| **Shadow Crawler** | Corruption Deep | Wall-climbing ambush | Ebonstone, Dark Essences |
| **Lord Malus** *(Mini-Boss)* | Nether Dungeon Chamber | Blight orbs, charge sweep | **Portal Shard** (x1-2), Nether Cleaver, 400 EXP |
| **Ignis Colossus** *(Mini-Boss)*| Nether Dungeon Chamber | Magma bombs, seismic slam | **Portal Shard** (x1-2), Magma Greatsword, Magma Core |
| **Cryo-Spud** *(Mini-Boss)* | Nether Dungeon Chamber | Frost shards, glacial frostbite | **Portal Shard** (x1-2), Frost Blade, Frost Amulet |
| **Necro-Tuber** *(Mini-Boss)*| Nether Dungeon Chamber | Ghost skulls, bone whirl | **Portal Shard** (x1-2), Bone Scythe, Necro Essence |
| **SOL-RHO** *(Phase I)* | Celestial Sky Summon | Radiant Solar Titan: Solar Orbs, Flare Dive | *Resurrects into Phase II upon 0 HP!* |
| **AWAKENED SOL-RHO** *(Phase II)*| Cosmic Void Arena | Void Incarnate: Singularity Vortex, Void Meteors, Warp Blitz | **Crown of Potaria**, **Celestial Greatsword**, **Titan Chestplate**, **Celestial Emblem**, **TRUE VICTORY!** |

### Loot Probability Tiers & Treasure Chests:
Monsters and naturally generated underground **Treasure Chests** roll loot according to strict probability tiers:
- **Common (55%)**: Raw Potatoes, Healing Potions, Basic Ores, Gel.
- **Uncommon (25%)**: Mashed Potato Meals, Swiftness Potions, Refined Metal Bars, Frost Cores.
- **Rare (8%)**: Skill Books (`Power Slash`, `Whirlwind`, `Swift Dash`, `Fireball`, `Frost Nova`, `Meteor Strike`, `Celestial Shield`), Biome Weapons (`Frost Blade`, `Sandstorm Spear`, `Cactus Sword`, `Bone Scythe`), Accessories (`Guardian Ring`, `Warrior Charm`, `Titans Ring`).
- **Epic (2.5%)**: `Hermes Boots` (+115% sprint speed), `Starch Blade`, `Shadow Cleaver`, `Golden Fry`, `Lucky Clover` (+15% Crit Chance), `Band of Regeneration`, `Magma Greatsword`.
- **LEGENDARY (0.9% mob drop, 5% Treasure Chests)**: **Starfury**!
- **MYTHIC KEYSTONES**:
  - **Portal Shards** (35% in dungeon chests, 100% guaranteed 1-2 from Dungeon Mini-Bosses).
  - **Celestial Keystone** (Crafted from 4 Portal Shards + 4 Gold Bars + 8 Stone Bricks). Right-click to summon **Sol-Rho the Celestial Titan**!

### Dynamic Mob Spawner & Despawning:
- When exploring, mobs naturally spawn in the biome and elevation where the player currently stands.
- When traveling far across the infinite world, distant mobs (>1300 pixels from the player) automatically despawn, freeing up memory and ensuring fresh enemies populate every new region you enter.

---

## 🛡️ Chroisen-Style Action RPG Engine

- **Character Statistics (Level 1–100)**:
  - **Level & EXP Progression**: Slay slimes, zombies, demon eyes, and bosses to earn EXP. Leveling up permanently increases Base HP, Base MP, Base ATK, Base DEF, and grants a full heal.
  - **Mana (MP) & Regeneration**: Base mana regenerates at a steady 1.8 MP/s. Magic accessories (Mana Flower, Frost Amulet, Celestial Emblem) provide powerful bonus MP regen.
  - **Defense Mitigation Formula**: Incoming physical damage follows the classic RPG rule:
    $$\text{Damage Taken} = \max(1, \text{Enemy ATK} - \text{Player DEF})$$
  - **Critical Hits**: Attacks roll against player Crit Chance to deal 180% damage with golden popups and heavy screen shake.
- **Paperdoll Armor & Hotbar Dynamic Weapon Equipping**:
  - **Armor & Accessory Slots (`C` Key)**:
    1. **Head**: Potato Cap, Cactus Helmet, Copper/Iron/Gold Helmet, Frost Hood, Shadow Helmet, Potato Miner Helmet (radiant light emitter), Crown of Potaria.
    2. **Chest**: Potato Tunic, Cactus Chestplate, Copper/Iron/Gold Chestplate, Frost Parka, Shadow Plate.
    3. **Legs**: Potato Pants, Cactus Greaves, Copper/Iron/Gold Greaves, Rootrunner Boots, Hermes Boots.
    4. **Accessory**: Warrior Charm (+8 ATK, +4% Crit), Guardian Ring (+8 DEF, +35 HP), Band of Regeneration, Mana Flower (+3.0 MP regen), Lucky Clover (+15% Crit), Titans Ring (+14 ATK, +20 DEF).
  - **Seamless Weapon Wielding**: Weapons do NOT occupy a cumbersome armor slot! Simply place any weapon into your hotbar (slots 1–9, 0). Selecting it immediately equips it in Spud's hand, dynamically granting its weapon ATK power, swing speed, crit bonus, and celestial particle effects.
  - **Quick Equip**: Right-click armor or accessories in your backpack (`E`) to equip them instantly.

---

## ⚡ Skill Grimoire, Upgrades & Grand Legendary Spells

- **Skill Books & Upgrades (Level 1 to 5)**:
  - Right-click a Skill Book in your backpack to learn the ability into your Grimoire (`C` key).
  - Reading duplicate copies of the same Skill Book **levels up the skill** up to Lv. 5!
  - Level 1 skills start with modest damage and very low MP costs. As skills level up, their damage multipliers, AoE blast radius, and tactical utility grow substantially.
- **Active Hotkeys (`Q`, `F`, `V`, `R`)**:
  - `Q` — **Power Slash**: Heavy forward sword cleave dealing 120%–220% ATK damage (Cost: 6–10 MP).
  - `F` — **Whirlwind**: 360-degree spinning strike hitting all surrounding foes (Cost: 10–18 MP).
  - `V` — **Swift Dash**: High-speed directional dash with temporary invincibility (Cost: 5–8 MP).
  - `R` — **Fireball**: Casts an explosive fire orb detonating for 140%–260% ATK damage upon impact (Cost: 8–14 MP).
- **Grand Legendary Spells**:
  - **Meteor Strike**: Calls down a devastating cosmic meteor barrage dealing 320% damage with massive crater impact (Cost: 45 MP, Cooldown: 14.0s).
  - **Celestial Shield**: Envelops Spud in a radiant divine aegis granting complete invulnerability for 4.5 seconds (Cost: 50 MP, Cooldown: 18.0s).
  - **Frost Nova**: Glacial 360° freeze detonation dealing 240% damage and freezing nearby foes (Cost: 28 MP, Cooldown: 8.0s).

---

## 👥 LAN Cooperative Multiplayer (1 to 5 Players)

- **Zero Configuration Required**: Built entirely on pure Python standard library `socket` and `threading`. No external servers, cloud accounts, or third-party drivers needed!
- **Authoritative LAN Host**:
  - Launch Potaria and select **👥 LAN MULTIPLAYER (1-5P)** -> **HOST LAN GAME**.
  - Your host server starts automatically on port `25565`, binding to your local network adapter.
  - Automatically synchronizes the procedural world seed with all joining players.
- **Instant Client Join**:
  - Other computers on the same Wi-Fi or local Ethernet choose **JOIN LAN GAME**, enter the host's IP address (e.g. `192.168.1.50`), and click Join.
- **Synchronized Multiplayer Features**:
  - **Party HUD**: Renders health bars, player names, and levels for up to 5 connected party members.
  - **Remote Potato Avatars**: See your friends walking, jumping, facing, and swinging tools with level badges.
  - **Real-time Block Deltas**: When any party member mines or places a block, the change synchronizes instantly across all players.
  - **In-Game Party Chat**: Press `Enter` to open chat, type your message, and hit `Enter` to broadcast to the entire party.
  - **Party Boss Scaling**: Lord Malus's max health scales dynamically with the size of your party (+40% HP per additional member).

---

## ⚙️ In-Game Pause Menu & Settings Screen

- **In-Game Pause Menu (`Esc` or `P`)**:
  - `▶  RESUME GAME`: Continues your adventure immediately.
  - `⚙  SETTINGS & AUDIO`: Opens the full settings screen in-game without losing your session.
  - `🚪  RETURN TO MAIN MENU`: Cleanly shuts down local LAN connections, halts background music, and returns to the title screen.
- **Settings Screen (Accessible from Main Menu and In-Game Pause)**:
  - **Master Volume Slider**: `[ - ] 100% [ + ]`
  - **Music (BGM) Volume Slider**: `[ - ] 65% [ + ]`
  - **Sound Effects (SFX) Volume Slider**: `[ - ] 85% [ + ]`
  - **Display Mode Toggle**: Toggle between `WINDOWED` (1280x720) and `FULLSCREEN` (also toggleable anytime via `F11`).
  - **Screen Shake Toggle**: Enable or disable dynamic impact camera shake.
  - **INPUT KEY MAPPING**: Fully rebind all movement, jump, inventory, minimap, character panel, and skill hotkeys!

---

## 🌍 Worlds, Difficulties & Game Modes (Minecraft-Style)

### 1. Portable World Saves (`saves/<world_name>/world.json`):
- Worlds are stored as standalone, portable JSON files containing the world seed, terrain dimensions, player inventory, equipment, level, skills, boss progress, and modified block deltas.
- **Save & Quit vs. Quit without Saving:** Pause menu gives explicit control over saving your session.
- Move or backup your save folders freely across computers just like Minecraft!

### 2. World Types:
- **Infinite World:** Endless procedural chunk streaming horizontally in both directions with zero boundaries.
- **Finite World:** A bounded classic world (320 blocks wide) enclosed by ancient bedrock barriers and oceans, randomized on creation.

### 3. Difficulty Modes:
- **Normal:** Start with a basic axe. Mine trees to craft workbenches, swords, and tools. Keeps all inventory and equipment on death.
- **Hardcore:** Start with a completely empty inventory — punch trees for raw wood! Dying drops all 40 backpack items and equipped armor into the world.
- **YOLO (You Only Live Once):** Hardcore rules plus permanently locked to **ONE HEART** (20 HP, cannot be increased by level-ups or food). Features true permadeath with a custom Game Over screen featuring *"Restart your life"* and *"I don't wanna go back! (Main Menu)"*.

### 4. Game Modes (PvP / Last Man Standing):
- **Adventure Mode:** Standard singleplayer or cooperative multiplayer survival RPG.
- **Last Man Standing (LMS / Battle Royale):**
  - Host or local world where players spawn scattered across different biomes (Forest, Desert, Snow, Corruption).
  - **Friendly Fire ON:** Swords, fireballs, and arrows damage other players.
  - Gather resources, gear up, and duel until only 1 player remains, triggering the celebratory Victory Fanfare!

---

## 👾 New Enemy Variants & Biome Mini-Boss Teleportation

- **Rock-Throwing Zombie:** Spawns in rugged Desert and Mountain biomes, hurling ballistic rock projectiles from afar.
- **Shield-Weaver Mob:** Conjures overhead barrier blocks (`TILE_BARRIER`) that deflect Starfury falling celestial stars and arrows!
- **Earth Digger Mob:** Burrows through natural dirt, stone, and sand to ambush players, but **CANNOT** penetrate wooden blocks, player-placed blocks, or house structures.
- **Biome Altar Runes & Arenas:**
  - Each major biome features an altar/rune (Sun Altar Rune, Frost Altar Rune, Necro Altar Rune, Nether Rune) that warps Spud into that Mini-Boss's dedicated arena.
  - Slaying the Mini-Boss awards that biome's Celestial Portal Shard and warps Spud back to the main world.
  - All Mini-Boss (`lord_malus`, `ignis_colossus`, `cryo_spud`, `necro_tuber`) and Grand Boss (`sol_rho`) sprites are exported as physical PNGs in `assets/boss/`!

---

## 🎒 Inventory Drop & Full Backpack Protection

- **Item Dropping:** Hover over any backpack slot and press `Q`, press `Backspace`, press `G`, or click the UI `[DROP]` button to drop items into the world with physics.
- **Full Inventory Protection:** When all 40 slots are full, items on the ground remain safe in the world and are never lost or deleted until you free up inventory space.

---

## 🎮 Complete Controls

| Action | Primary Key | Notes |
|---|---|---|
| **Move Left / Right** | `A` / `D` | Rebindable in Settings -> Controls |
| **Jump** | `Space` / `W` | Rebindable in Settings -> Controls |
| **Drop Through Platform** | `S` | Drops down through wooden platforms |
| **Mine / Attack** | `Left Click` (Hold) | Continuous mining / weapon swinging |
| **Place Block / Torch / Furniture** | `Right Click` (World) | Places selected block from active hotbar slot |
| **Drop Item from Backpack** | `Q` / `Backspace` / `G` | Drops hovered or selected item into the world |
| **Interact / Open Doors** | `Right Click` Door | Toggles doors open/closed (impenetrable when closed) |
| **Open Treasure Chest** | `Right Click` / Mine Chest | Opens chest, bursts with high-tier loot & fanfare |
| **Eat Food / Drink Potion** | `Right Click` (Hotbar) | Restores HP / applies temporary buffs |
| **Toggle Mini-Map Radar** | `M` | Real-time corner mini-map (terrain, player, mobs, chests, boss) |
| **Open Character Panel & Grimoire** | `C` | Paperdoll gear, stats, and **Skill Selection Grimoire** |
| **Toggle Backpack / Crafting** | `E` | Opens 40-slot inventory, crafting stations, and `[DROP]` button |
| **Quick Equip Gear / Learn Skill** | `Right Click` in Bag | Equips armor or learns Skill Book into Grimoire |
| **Rebindable Combat Skills** | `Q`, `F`, `V`, `R` | Configurable in Character Panel (`C`) or Settings |
| **Toggle Fullscreen** | `F11` | Seamless HD hardware scaled fullscreen |
| **Party Chat** | `Enter` | Open typing box / send chat in multiplayer |
| **Select Hotbar Slot** | `1` to `9`, `0` | Cycles through active items |
| **Pause Game** | `P` / `Esc` | Opens pause menu with Save & Quit, Settings, Menu |
| **Debug Info Overlay** | `F1` | Shows FPS, Seed, Coordinates, and RPG Stats |
| **Fast-Forward Time** | `T` | Advances day/night cycle |

---

## 🛠️ Crafting, House Building & Cooking Recipes

| Item | Ingredients | Station | Purpose |
|---|---|---|---|
| **Work Bench** | 10 Wood | By Hand | Essential station unlocking house building & advanced weapons |
| **Wood Platform** (x2) | 1 Wood | By Hand | Permeable building platform |
| **Torch** (x4) | 1 Wood + 1 Gel | By Hand | Illumination preventing mob spawns in houses |
| **Chest** | 8 Wood + 2 Iron Bar | Work Bench | Storage & treasure container |
| **Wooden Door** | 6 Wood | Work Bench | Interactive house entrance (blocks all monster entry) |
| **Wood Planks** (x4) | 1 Wood | Work Bench | Solid timber building blocks |
| **Stone Bricks** (x4) | 4 Stone | Work Bench | Sturdy fortress building blocks |
| **Glass Window** | 2 Sand Block | Furnace | Transparent interior window block |
| **Roof Shingles** (x4) | 2 Wood + 2 Clay | Work Bench | Decorative angled cottage roofing |
| **Wooden Table & Chair** | 8 Wood / 4 Wood | Work Bench | Cozy domestic furniture |
| **Cactus Helmet / Plate / Greaves**| 12 / 18 / 14 Cactus | Work Bench | Desert defensive gear |
| **Cactus Sword** | 10 Cactus | Work Bench | Desert sword (ATK: 12) |
| **Bone Bow** | 12 Bones + 4 Wood | Work Bench | High-velocity ballistic bow (Base: 22) |
| **Wooden Arrows** (x15) | 1 Wood + 1 Stone | Work Bench | Standard bow ammunition |
| **Frostburn Arrows** (x15)| 15 Wooden Arrows + 1 Frost Core | Work Bench | Chilling elemental arrows (+8 bonus DMG) |
| **Furnace** | 20 Stone + 4 Wood + 3 Torches | Work Bench | Smelting ores and cooking food |
| **Copper / Iron / Gold Bar** | 3 Corresponding Ore | Furnace | Smelted crafting metal |
| **Copper / Iron / Gold Pickaxe**| 8 / 10 / 10 Bar + 3 Wood | Work Bench | Mining tools (Power: 25 / 40 / 60) |
| **Mashed Potatoes** | 2 Raw Potato + 1 Wood | Furnace | Nutritious meal (+60 HP heal) |
| **Golden French Fry** | 2 Raw Potato + 1 Gold Bar | Furnace | Royal treat (Full 100% HP heal + Sprint buff) |
| **Lesser / Greater Potion** | Potatoes, Gel, Gold | Work Bench | Instant health restoration |
| **Celestial Keystone** | 4 Portal Shards + 4 Gold Bar + 8 Stone Brick | Work Bench | Summons Grand Boss Sol-Rho the Celestial Titan |

---

## 🧪 Automated Integration & Multiplayer Testing

Potaria includes an exhaustive automated test suite verifying all gameplay mechanics, difficulty modes, world saves, networking, and rendering:

To run all test suites:
```powershell
python tests/test_new_features.py           # 10/10 gameplay expansion tests passing
python tests/test_game.py                   # 14/14 core integration tests passing
python tests/test_lan_hud_mobs_scaling.py   # 11/11 multiplayer & mob sync tests passing
python tests/test_gameplay_fixes.py          # 8/8 gameplay systems tests passing
python tests/test_reviewer_fixes.py          # 6/6 reviewer verification tests passing
```
**Total:** **49/49 automated tests passing with zero errors!**

### Verified Systems Matrix:
1. **Asset Synthesis Engine & Boss Files**: Procedural export of all 4 Mini-Bosses and Grand Boss sprites to physical `.png` files in `assets/boss/`.
2. **Infinite & Finite World Types**: Chunk streaming vs bounded 320-tile bedrock/ocean worlds.
3. **Difficulty Modes**: Normal (keeps gear), Hardcore (empty start, drops gear), and YOLO (1-Heart permadeath with restart/exit screens).
4. **Minecraft-Style World Saves**: JSON persistence in `saves/<world>/`, save/load UI, and safe corrupt file recovery.
5. **Last Man Standing (LMS / PvP)**: Biome scatter spawning, friendly fire, and victory fanfare.
6. **Full Inventory Protection & Dropping**: Items remain on ground when full (zero item loss); dropping via `Q`, `Backspace`, `G`, or `[DROP]` button.
7. **New Mob Variants**: RockZombie (ballistic rocks), ShieldWeaver (overhead barrier blocks), and DiggerMob (burrowing natural tiles only).
8. **Biome Portal Runes**: Altar runes teleporting to Mini-Boss arenas and returning with Celestial Portal Shards.
9. **Starter Balance & Mob Danger**: Tuned copper gear DEF and increased mob damage.
10. **Multiplayer Synchronization & HD Scaling**: Nearest-neighbor integer scaling and authoritative 20 Hz mob sync.

---

## 🚀 How to Run the Game

### Prerequisites
- Python 3.10 or higher
- **Pygame Community Edition (`pygame-ce`)** 2.5 or higher:
  ```powershell
  pip install pygame-ce
  ```

### Start Potaria
```powershell
python main.py
```

---

## 🏆 Credits

- **Game Developer & Lead Architect:** Kurados
- **Lead Protagonist:** Spud the Potato Hero
- **Antagonist:** Lord Malus the Blight-Bringer
- **Procedural Audio & Synth BGM Engine:** Pure Python Retro Sound Synthesizer by Kurados
