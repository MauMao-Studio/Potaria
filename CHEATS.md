# Potaria Developer & Debug Cheat Console Guide

The Potaria in-game developer console enables fast testing, gear verification, monster spawning, time control, and god mode debugging in both **Singleplayer** and **LAN Multiplayer** modes.

---

## 1. Opening the Console

Press any of the following keys during gameplay:
- **`Enter`**: Opens the console input box.
- **`/` (Slash)**: Opens the console with `/` pre-typed.
- **`~` (Backtick / Tilde)**: Opens the console with `/` pre-typed.

Type your command and press **`Enter`** to execute. Press **`Escape`** to dismiss the console.

---

## 2. Command Reference

### Player & Stat Commands

| Command | Arguments | Description | Example |
| :--- | :--- | :--- | :--- |
| `/god`, `/invincible` | *None* | Toggles God Mode (infinite HP, infinite MP, invincibility, infinite breath). | `/god`<br>`/invincible` |
| `/heal` | *None* | Restores Spud to full HP, MP, and breath immediately. | `/heal` |
| `/speed` | `[multiplier]` | Multiplies movement speed (default: 2.0x; resets to 1.0x if run again without args). | `/speed 2.5` |
| `/level` | `[count]` | Levels up Spud by `count` levels (default: 1). | `/level 10` |
| `/allskills` | *None* | Unlocks and elevates all 8 active combat skills to maximum Level 5. | `/allskills` |
| `/clear` | *None* | Clears all backpack items and held cursor items. | `/clear` |

---

### World & Time Commands

| Command | Arguments | Description | Example |
| :--- | :--- | :--- | :--- |
| `/time` | `<morning \| day \| noon \| dusk \| night \| 0.0-1.0>` | Changes the in-game Day/Night cycle clock. | `/time morning`<br>`/time night`<br>`/time 0.25` |

---

### Gear & Item Commands

| Command | Arguments | Description | Example |
| :--- | :--- | :--- | :--- |
| `/<item_id>` | `[count]` | **Direct Item ID Cheat**: Typing any item ID directly gives it to Spud. | `/astral_wrath`<br>`/composite_bow`<br>`/ancient_composite_bow`<br>`/astral_arrow 50` |
| `/give`, `/item` | `<item_id> [count]` | Adds items directly to inventory (or drops excess at feet). | `/give astral_arrow 250`<br>`/item eternal_catalyst 1` |
| `/ancient` | *None* | Equips the complete **Ancient Relic Set** (Helmet, Chestplate, Greaves, Bow, Rod, Catalyst, Greatsword, and 250 Astral Arrows) and activates the radiant pulsing aura. | `/ancient` |
| `/weapons` | *None* | Grants an arsenal showcase pack with all notable bows, arrows, magic staves, rods, scepters, catalysts, and celestial blades. | `/weapons` |

---

### Combat & Spawning Commands

| Command | Arguments | Description | Example |
| :--- | :--- | :--- | :--- |
| `/spawn` | `<mob_or_boss> [count]` | Spawns monsters or bosses near Spud. | `/spawn sol_rho`<br>`/spawn lord_malus`<br>`/spawn zombie 5` |
| `/killall` | *None* | Immediately removes all active hostile monsters and hostile projectiles. | `/killall` |
| `/help` | *None* | Displays command syntax assistance in local chat. | `/help` |

---

## 3. Notable Item IDs

### Ancient & Celestial Equipment Set
- `ancient_helmet` - Ancient Helmet (+18 DEF, +10% Crit)
- `ancient_chestplate` - Ancient Chestplate (+28 DEF, +15% ATK)
- `ancient_greaves` - Ancient Greaves (+20 DEF, +12% Speed)
- `ancient_eternal_shortbow` - Ancient Eternal Shortbow (Ranged)
- `ancient_composite_bow` - Ancient Composite Bow (Ancient Ballistic Archery)
- `composite_bow` - Composite Bow (Rare Recurve)
- `reinforced_composite_bow` - Reinforced Composite Bow (Epic Piercing Bow)
- `ancient_forgotten_rod` - Ancient Forgotten Rod (Piercing Javelin)
- `eternal_catalyst` - Eternal Catalyst (Homing Celestial Stars)
- `celestial_greatsword` - Celestial Greatsword
- `astral_wrath` - Astral Wrath (Starfury Relic)

### Ranged Ammunition
- `wooden_arrow` - Standard arrow
- `flame_arrow` - Burning arrow (+6 damage)
- `frostburn_arrow` - Freezing arrow (+8 damage, slows targets)
- `astral_arrow` - High-velocity celestial arrow (+14 damage)

### Magic Weapons
- `fire_staff` - Fire bolt magic staff
- `frost_staff` - Chilled bolt magic staff
- `void_scepter` - Arcane shockwave pulse scepter
- `glacial_scepter` - Frost shockwave scepter
- `chrono_rod_of_sol_rho` - Time-piercing rod javelin
- `scorpion_catalyst_of_the_vale` - Desert starlight catalyst

### Crafting, Storage & Enhancement Catalysts
- `wooden_sword` - Basic craftable wooden starter blade
- `chest` - Craftable multi-slot storage container
- `affix_stone` - Rare catalyst required for affix slot carving at Morrigan the Void Weaver
- `gold_bar` - Smelted gold ingot used for Keystone crafting and high-tier gear

### Boss Runes & Summoners
- `dungeon_rune` - Warps to Nether Dungeon & summons Lord Malus
- `desert_rune` - Warps to Arid Waste Arena & summons Ignis Colossus
- `cryo_rune` - Warps to Glacial Permafrost & summons Cryo-Spud
- `necro_rune` - Warps to Blight Shadow Crypt & summons Necro-Tuber
- `celestial_keystone` - Summons Grand Boss Sol-Rho The Celestial Titan

---

## 4. Notable Mob & Boss Names for `/spawn`

- **Bosses**: `malus`, `ignis`, `cryo`, `necro`, `sol_rho` (or `titan`)
- **Hostile Mobs**: `green_slime`, `frost_slime`, `sand_slime`, `zombie`, `ice_zombie`, `rock_zombie`, `mummy`, `night_gazer`, `demon_eye`, `skeleton`, `cave_bat`, `ice_bat`, `scorpion`, `crawler`
