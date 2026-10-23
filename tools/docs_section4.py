"""
Potaria Documentation Generator - Section 4: Master Reference of Exact Numeric Values, Formulas & Physical Constants
Developer: Kurados
Strict Constraints: NO emojis, relative paths only.
"""

def build_section_4():
    return """## 4. Master Reference of Exact Numeric Values, Formulas & Physical Constants

### 4.1 Canonical Master Constants Reference (`src/constants.py`)

| Constant Identifier | Value | Unit / Scale | Architectural Purpose |
|:---|:---|:---|:---|
| `SCREEN_WIDTH` | `1280` | Pixels | Reference viewport width |
| `SCREEN_HEIGHT` | `720` | Pixels | Reference viewport height |
| `FPS` | `60` | Frames / Sec | Target frame cadence |
| `SCALE` | `2` | Integer Multiplier | 16x16 pixel sprites rendered at 32x32 |
| `TILE_SIZE` | `16` | Source Pixels | Unscaled tile sprite dimension |
| `SCALED_TILE` | `32` | Viewport Pixels | Scaled in-game tile grid cell dimension |
| `WORLD_WIDTH` | `450` | Tiles (Finite Mode) | Finite world width (Infinite mode ignores bound) |
| `WORLD_HEIGHT` | `240` | Tiles | Total world vertical depth (from Sky to Nether) |
| `SURFACE_LEVEL` | `70` | Tile Y Coordinate | Average surface terrain horizon |
| `UNDERGROUND_LEVEL` | `115` | Tile Y Coordinate | Transition from surface dirt to subterranean stone |
| `CAVERN_LEVEL` | `160` | Tile Y Coordinate | Deep caves, glowing mushroom grottos |
| `DUNGEON_LEVEL` | `205` | Tile Y Coordinate | Nether Dungeon, boss altars, and catacombs |
| `GRAVITY` | `0.44` | px / frame^2 | Gravitational acceleration impulse |
| `TERMINAL_VELOCITY`| `10.0` | px / frame | Maximum downward fall velocity clamp |
| `PLAYER_SPEED` | `3.0` | px / frame | Base horizontal movement speed |
| `PLAYER_ACCEL` | `0.35` | px / frame^2 | Running horizontal acceleration |
| `PLAYER_FRICTION` | `0.22` | px / frame^2 | Ground deceleration friction |
| `PLAYER_JUMP_FORCE`| `-8.0` | px / frame | Upward jump initial impulse |
| `PLAYER_DROP_THROUGH_TIME` | `15` | Ticks (0.25s) | Platform ignore collision duration |
| `PLAYER_WIDTH` | `28` | Pixels | Kinematic body collider width |
| `PLAYER_HEIGHT` | `32` | Pixels | Kinematic body collider height (1 tile high) |
| `PLAYER_SPRITE_WIDTH` | `28` | Pixels | Visual potato sprite width |
| `PLAYER_SPRITE_HEIGHT`| `36` | Pixels | Visual potato sprite height (includes sprout leaf) |
| `HOTBAR_SLOTS` | `10` | Slots | Number of active hotbar inventory slots |
| `INV_COLS` | `10` | Columns | Backpack inventory grid width |
| `INV_ROWS` | `4` | Rows | Backpack inventory grid height |
| `INV_TOTAL_SLOTS` | `40` | Slots | Total backpack storage capacity |
| `SLOT_SIZE` | `40` | Pixels | Inventory slot visual UI bounding box |
| `SLOT_PADDING` | `4` | Pixels | Padding between inventory grid slots |
| `MAX_LIGHT` | `15` | Discrete Units | Maximum cellular illumination intensity |
| `MIN_LIGHT` | `1` | Discrete Units | Minimum ambient light clamp |

#### Complete Tile Definitions & Hardness Registry (`TILE_PROPS`)

| Tile ID | Internal Name | Hardness | Tool Type | Drop Item | Solid | Platform | Light Emit | Absorb |
|:---|:---|:---|:---|:---|:---|:---|:---|:---|
| 0 | Air | 0 | None | None | No | No | 0 | 0 |
| 1 | Dirt | 15 | Shovel | dirt_block | Yes | No | 0 | 3 |
| 2 | Grass | 18 | Shovel | dirt_block | Yes | No | 0 | 3 |
| 3 | Stone | 35 | Pickaxe | stone_block | Yes | No | 0 | 4 |
| 4 | Oak Wood | 20 | Axe | wood | Yes | No | 0 | 3 |
| 5 | Oak Leaves | 5 | Bare Hand | leaves | No | No | 0 | 1 |
| 6 | Oak Wood Trunk | 20 | Axe | wood | No | No | 0 | 2 |
| 7 | Copper Ore | 40 | Pickaxe | copper_ore | Yes | No | 0 | 4 |
| 8 | Iron Ore | 45 | Pickaxe | iron_ore | Yes | No | 0 | 4 |
| 9 | Gold Ore | 55 | Pickaxe | gold_ore | Yes | No | 1 | 4 |
| 10 | Wood Platform | 10 | Axe | wood_platform | No | Yes | 0 | 0 |
| 11 | Work Bench | 25 | Axe | work_bench | No | Yes | 0 | 0 |
| 12 | Furnace | 40 | Pickaxe | furnace | No | No | 8 | 0 |
| 13 | Torch | 5 | Bare Hand | torch | No | No | 10 (r:6) | 0 |
| 14 | Stone Brick | 38 | Pickaxe | stone_brick | Yes | No | 0 | 4 |
| 15 | Bedrock | 9999 | Indestructible | None | Yes | No | 0 | 15 |
| 16 | Dungeon Brick | 9999 | Indestructible | None | Yes | No | 1 | 15 |
| 17 | Dungeon Altar | 9999 | Indestructible | None | No | Yes | 6 | 0 |
| 18 | Sand | 12 | Shovel | sand_block | Yes | No | 0 | 2 |
| 19 | Sandstone | 30 | Pickaxe | sandstone_block | Yes | No | 0 | 4 |
| 20 | Cactus | 15 | Axe | cactus | No | No | 0 | 1 |
| 21 | Snow | 10 | Shovel | snow_block | Yes | No | 0 | 2 |
| 22 | Ice | 22 | Pickaxe | ice_block | Yes | No | 0 | 2 |
| 23 | Blight Grass | 25 | Shovel | dirt_block | Yes | No | 1 | 4 |
| 24 | Blightstone | 50 | Pickaxe | blightstone_block | Yes | No | 0 | 5 |
| 25 | Mushroom Grass | 20 | Shovel | glowing_mushroom | Yes | No | 6 | 2 |
| 26 | Mushroom Stem | 15 | Axe | wood | No | No | 2 | 1 |
| 27 | Mushroom Cap | 12 | Bare Hand | glowing_mushroom | No | No | 9 | 0 |
| 28 | Treasure Chest | 30 | Axe | chest | No | Yes | 3 | 0 |
| 29 | Roof Tiles | 25 | Pickaxe | roof_tiles | Yes | No | 0 | 3 |
| 30 | Wood Planks | 20 | Axe | wood_planks | Yes | No | 0 | 3 |
| 31 | Glass Window | 10 | Pickaxe | glass_window | Yes | No | 0 | 0 |
| 32 | Wooden Door (Closed) | 20 | Axe | wooden_door | Yes | No | 0 | 1 |
| 33 | Wooden Door (Open) | 20 | Axe | wooden_door | No | No | 0 | 0 |
| 34 | Wooden Table | 20 | Axe | wooden_table | No | Yes | 0 | 0 |
| 35 | Wooden Chair | 15 | Axe | wooden_chair | No | No | 0 | 0 |
| 36 | Magical Barrier | 30 | Indestructible | None | Yes | No | 10 | 0 |
| 37 | Liquid Water | 9999 | Liquid Fluid | None | No | No | 0 | 2 |
| 38 | Wooden Bed | 20 | Axe | wooden_bed | No | Yes | 0 | 0 |
| 39 | Bookshelf | 20 | Axe | bookshelf | No | Yes | 0 | 0 |
| 40 | Grandfather Clock | 25 | Axe | grandfather_clock | No | No | 1 | 0 |
| 41 | Stone Fireplace | 35 | Pickaxe | stone_fireplace | No | Yes | 13 (r:11) | 0 |
| 42 | Candelabra | 10 | Bare Hand | candelabra | No | No | 12 (r:10) | 0 |
| 43 | Chandelier | 12 | Bare Hand | chandelier | No | No | 14 (r:14) | 0 |
| 44 | Potted Spud Plant | 10 | Bare Hand | potted_plant | No | No | 2 (r:3) | 0 |
| 45 | Wooden Dresser | 20 | Axe | wooden_dresser | No | Yes | 0 | 0 |
| 46 | Wall Tapestry | 8 | Bare Hand | wall_tapestry | No | No | 0 | 0 |
| 47 | Bathtub | 25 | Pickaxe | bathtub | No | Yes | 0 | 0 |
| 48 | Sink | 20 | Pickaxe | sink | No | Yes | 0 | 0 |
| 49 | Painting | 8 | Bare Hand | painting | No | No | 1 | 0 |
| 50 | Wood Shelf | 10 | Axe | wood_shelf | No | Yes | 0 | 0 |
| 51 | Carved Tuber Lantern | 8 | Bare Hand | carved_tuber_lantern | No | No | 14 (r:8) | 0 |
| 52 | Brass Lantern | 10 | Bare Hand | brass_lantern | No | No | 14 (r:8) | 0 |
| 53 | Spectral Lantern | 10 | Bare Hand | spectral_lantern | No | No | 14 (r:8) | 0 |
| 54 | Oak Sapling | 5 | Bare Hand | oak_sapling | No | No | 0 | 0 |
| 55 | Iron Storage Chest | 35 | Pickaxe | iron_chest | No | Yes | 0 | 0 |
| 56 | Rope Rungs | 10 | Bare Hand | rope_rungs | No | Yes | 0 | 0 |
| 57 | Magma Dungeon Brick | 9999 | Indestructible | None | Yes | No | 2 | 15 |
| 58 | Crypt Dungeon Brick | 9999 | Indestructible | None | Yes | No | 1 | 15 |
| 59 | Catacomb Bone Brick | 9999 | Indestructible | None | Yes | No | 1 | 15 |
| 60 | Dungeon Portcullis | 9999 | Indestructible | None | No | No | 1 | 0 |
| 61 | Brass Lamp | 10 | Bare Hand | brass_lamp | No | No | 14 (r:9) | 0 |
| 62 | Palm Sapling | 5 | Bare Hand | palm_sapling | No | No | 0 | 0 |
| 63 | Pine Sapling | 5 | Bare Hand | pine_sapling | No | No | 0 | 0 |
| 64 | Blight Sapling | 5 | Bare Hand | blight_sapling | No | No | 2 (r:3) | 0 |
| 65 | Pine Wood | 20 | Axe | pine_wood | Yes | No | 0 | 3 |
| 66 | Pine Leaves | 5 | Bare Hand | pine_leaves | No | No | 0 | 1 |
| 67 | Pine Wood Trunk | 20 | Axe | pine_wood | No | No | 0 | 2 |
| 68 | Palm Wood | 20 | Axe | palm_wood | Yes | No | 0 | 3 |
| 69 | Palm Leaves | 5 | Bare Hand | palm_leaves | No | No | 0 | 1 |
| 70 | Palm Wood Trunk | 20 | Axe | palm_wood | No | No | 0 | 2 |
| 71 | Blight Wood | 20 | Axe | blight_wood | Yes | No | 1 | 3 |
| 72 | Blight Leaves | 5 | Bare Hand | blight_leaves | No | No | 1 | 1 |
| 73 | Blight Wood Trunk | 20 | Axe | blight_wood | No | No | 1 | 2 |
| 74 | Dry Farmland Soil | 15 | Shovel | dirt_clod | Yes | No | 0 | 3 |
| 75 | Hydrated Farmland | 15 | Shovel | dirt_clod | Yes | No | 0 | 3 |
| 76 | Planted Crops (0-3) | 1 | Bare Hand | Dynamic Crops | No | No | 0 | 0 |
| 77 | Wild Spud Plant | 1 | Bare Hand | Dynamic Seeds | No | No | 0 | 0 |

---

### 4.2 Kinematic & Locomotion Tuning Constants

| Metric | Pygame-CE Value | Unity 6 LTS Equivalent | Physical Functionality |
|:---|:---|:---|:---|
| Horizontal Max Run Speed | `3.0` px / frame | `6.0` units / sec | Primary run velocity cap |
| Dash Burst Speed Multiplier | `2.2x` | `2.2x` (`13.2` units / sec) | Dash skill velocity impulse |
| Run Acceleration Rate | `0.35` px / frame^2 | `40.0` units / sec^2 | Horizontal speed ramp cadence |
| Run Deceleration Friction | `0.22` px / frame^2 | `32.0` units / sec^2 | Ground stopping deceleration |
| Upward Jump Force | `-8.0` px / frame | `12.0` units / sec | Initial upward leap impulse |
| Variable Jump Cut Multiplier | `0.50x` (early release) | `0.45x` upward truncation | Height control upon early button release |
| Coyote Time Window | N/A (strict ground) | `0.15` seconds (150ms) | Jump allowance after leaving ledge |
| Jump Buffer Window | N/A (strict down) | `0.12` seconds (120ms) | Pre-landing jump command queue |
| Jump Grace Timer | N/A | `0.08` seconds (80ms) | Slope adhesion bypass on liftoff |
| Platform Drop Duration | `15` ticks (0.25s) | `0.25` seconds (250ms) | Collision ignore duration on drop |
| Climb Upward Velocity | `-3.8` px / frame | `5.5` units / sec | Vertical climb speed on rope rungs |
| Climb Downward Velocity | `3.2` px / frame | `4.8` units / sec | Vertical descent speed on rope rungs |
| Ground Detection BoxCast | Rect intersection | `Vector2(0.85, 0.15)` | Downward cast depth 0.08 units |
| Ground Slope Tolerance | 0 deg (axis aligned) | `45.0` degrees | Maximum walkable slope normal angle |
| Potato Collider Box | `28 x 32` pixels | `0.875 x 1.000` units | Kinematic interaction bounding box |
| Potato Sprite Visual Box | `28 x 36` pixels | `0.875 x 1.125` units | Full visual sprite dimension |
| Head Sprout Offset | `4` pixels | `0.125` units | Decorative non-colliding head sprout |

---

### 4.3 Fluid Mechanics & Oxygen Depletion Formula

| Parameter | Exact Value | Mechanical Consequence |
|:---|:---|:---|
| Water Horizontal Drag Multiplier | `0.88x` per tick | Fluid resistance retarding horizontal speed |
| Water Vertical Drag Multiplier | `0.90x` per tick | Fluid resistance retarding vertical speed |
| Water Gravity Factor | `0.25x` normal gravity | Buoyancy dampening downward fall acceleration |
| Maximum Oxygen Capacity | `100.0` units | Total breath reserve pool |
| Oxygen Depletion Rate | `7.5` units / second | Total submerged breath time = `13.33` seconds |
| Oxygen Surface Replenish Rate | `40.0` units / second | Full replenishment upon surfacing = `2.50` seconds |
| Drowning Tick Interval | `1.0` second | Time between consecutive drowning damage hits |
| Drowning Damage Formula | `max(1, max_hp // 10)` | Exactly 10% of Max HP (1 Heart) true damage per second |
| Drowning Armor Penetration | `100%` (True Damage) | Ignores DEF, armor mitigation, and meal resistances |

---

### 4.4 Combat & Damage Calculation Formulas

#### 1. Attack Cooldown & Swing Duration
- Base Swing Duration: `swing_duration = max(0.10, min(attack_cooldown, 0.45))` seconds.
- Attack Speed Meal Reduction: `cooldown = cooldown / (1.0 + atk_speed_mult)`. Minimum attack cooldown is clamped at `0.08` seconds.

#### 2. Physical & Defense Damage Mitigation
$$\\text{Effective DEF} = \\text{Base DEF} + \\text{Bonus DEF} + \\text{Meal DEF}$$
If Titan's Resolve is active (HP $< 30\\%$):
$$\\text{Effective DEF} = \\text{Effective DEF} \\times 3$$
The minimum piercing damage is capped at 15%:
$$\\text{Min Pierce} = \\begin{cases} 1 & \\text{if Titan's Resolve is active} \\\\ \\max(1, \\lceil \\text{Raw Damage} \\times 0.15 \\rceil) & \\text{otherwise} \\end{cases}$$
The net damage taken is:
$$\\text{Mitigated Damage} = \\max(\\text{Min Pierce}, \\text{Raw Damage} - \\text{Effective DEF})$$
Passive Damage Reductions applied multiplicatively:
- If 15% Mitigation active: $\\text{Mitigated Damage} = \\max(\\text{Min Pierce}, \\lfloor \\text{Mitigated Damage} \\times 0.85 \\rfloor)$.
- If 25% Mitigation active: $\\text{Mitigated Damage} = \\max(\\text{Min Pierce}, \\lfloor \\text{Mitigated Damage} \\times 0.75 \\rfloor)$.
- Food Damage Reduction: $\\text{Mitigated Damage} = \\max(\\text{Min Pierce}, \\lfloor \\text{Mitigated Damage} \\times (1.0 - \\text{dmg\\_reduction}) \\rfloor)$.

#### 3. Critical Strike Mechanics
$$\\text{Total Crit Rate} = \\min(75.0\\%, \\text{Base Crit} + \\text{Bonus Crit} + \\text{Meal Crit})$$
$$\\text{Crit Damage Multiplier} = 1.80\\times \\text{ (180\\% Total Damage)}$$

---

### 4.5 100-Level RPG Progression & EXP Formulas

#### Level-Up EXP Curve Formula
$$\\text{EXP\\_To\\_Next}(\\text{level}) = \\left\\lfloor 100 \\times \\left( \\text{level}^{2.1} \\right) \\right\\rfloor$$

#### Sample Level Milestones

| Level | EXP Required for Level | Cumulative Total EXP | Base HP | Base MP | Base ATK | Base DEF | Base Crit |
|:---|:---|:---|:---|:---|:---|:---|:---|
| 1 | 100 | 0 | 100 | 50 | 10 | 2 | 5.0% |
| 5 | 2,933 | 6,340 | 160 | 82 | 22 | 6 | 6.0% |
| 10 | 12,589 | 43,120 | 235 | 122 | 37 | 11 | 7.0% |
| 20 | 54,083 | 321,800 | 385 | 202 | 67 | 21 | 9.0% |
| 50 | 377,414 | 4,215,600 | 835 | 442 | 157 | 51 | 15.0% |
| 100 | 1,584,893 | 32,840,000 | 1,585 | 842 | 307 | 101 | 25.0% |

#### Currency Denomination Auto-Breakdown
$$\\text{Total Copper} = \\text{Copper} + (\\text{Silver} \\times 100) + (\\text{Gold} \\times 10,000)$$
$$\\text{Gold Coins} = \\lfloor \\text{Total Copper} / 10,000 \\rfloor$$
$$\\text{Silver Coins} = \\lfloor (\\text{Total Copper} \\% 10,000) / 100 \\rfloor$$
$$\\text{Copper Coins} = \\text{Total Copper} \\% 100$$

---

### 4.6 Statutory Meal Buff Contribution Caps (`MEAL_BUFF_CAPS`)

| Stat Parameter Name | Hard Cap Limit | Type | Rationale & Balance Boundary |
|:---|:---|:---|:---|
| `damage_mult` | `+12.0%` (`0.12`) | Multiplier | Limits global melee/physical scaling |
| `ranged_damage_mult` | `+12.0%` (`0.12`) | Multiplier | Limits ballistic archery / projectile scaling |
| `atk_speed_mult` | `+10.0%` (`0.10`) | Multiplier | Preserves animation stability and frame cadence |
| `crit_chance` | `+6.0%` (`0.06`) | Additive % | Prevents exceeding 75% hard crit cap |
| `crit_dmg_mult` | `+16.0%` (`0.16`) | Multiplier | Prevents extreme burst spikes on bosses |
| `armor_pen` | `+10.0%` (`0.10`) | Multiplier | Limits true damage bypassing defense curves |
| `def` | `+6` | Flat Integer | Equivalent to 2-3 armor pieces |
| `dmg_reduction` | `+6.0%` (`0.06`) | Multiplier | Prevents invulnerability stacking |
| `magic_res` | `+15.0%` (`0.15`) | Multiplier | Protects against bullet-hell elemental spikes |
| `speed_mult` | `+15.0%` (`0.15`) | Multiplier | Prevents camera tearing and physics tunneling |
| `jump_mult` | `+15.0%` (`0.15`) | Multiplier | Limits maximum vertical leap clearance |
| `dash_mult` | `+15.0%` (`0.15`) | Multiplier | Bounds dodge distance |
| `knockback_res` | `+15.0%` (`0.15`) | Multiplier | Prevents total knockback immunity from food |
| `hp_regen` | `+2.0` HP / sec | Additive Float| Out-of-combat sustain limit |
| `mp_regen` | `+2.0` MP / sec | Additive Float| Sustained combat spellcasting limit |
| `mana_cost_reduction` | `+15.0%` (`0.15`) | Multiplier | Prevents infinite skill spam |
| `luck` | `+10.0%` (`0.10`) | Multiplier | Modifies drop weights for rare loot |
| `gathering_speed` | `+20.0%` (`0.20`) | Multiplier | Boosts mining / chopping tick speed |
| `fishing_power` | `+15.0%` (`0.15`) | Multiplier | Increases bite rate and reel tension leniency |

---

### 4.7 7-Tier Rarity Engine Tables & Affix Budgets

| Rarity Tier | Rank | Hex Color Code | Affix Budget | Stat Multiplier | Drop Weight | Unique Effect Allowed |
|:---|:---|:---|:---|:---|:---|:---|
| Common | 0 | `#9E9E9E` (Grey) | 0 | 1.00x | 55.00% | No |
| Uncommon | 1 | `#4CAF50` (Green) | 1 | 1.10x | 25.00% | No |
| Rare | 2 | `#2196F3` (Blue) | 2 | 1.25x | 12.00% | No |
| Epic | 3 | `#9C27B0` (Purple) | 3 | 1.50x | 5.00% | No |
| Mythic | 4 | `#FF9800` (Orange) | 4 | 2.00x | 2.00% | Yes |
| Legendary | 5 | `#FFD700` (Gold) | 5 | 2.50x | 0.85% | Yes |
| Ancient | 6 | `#00F0E6` (Cyan/Crimson)| 6 | 3.00x | 0.15% | Yes |

---

### 4.8 Item Enhancement (+1 to +7) Requirements, Success Curves & Break Risks

| Target Level | Copper Cost | Material Requirements | Success Rate | Break Risk Rate | Stat Multiplier |
|:---|:---|:---|:---|:---|:---|
| +1 | 20 Copper | 2x Copper Bar | 100% | 0% (Safe) | 1.14x (+14%) |
| +2 | 50 Copper | 2x Iron Bar | 90% | 0% (Safe) | 1.28x (+28%) |
| +3 | 100 Copper | 3x Iron Bar, 1x Gold Bar | 80% | 0% (Safe) | 1.43x (+43%) |
| +4 | 200 Copper | 3x Gold Bar, 2x Spud Sap | 70% | 0% (Safe) | 1.57x (+57%) |
| +5 | 500 Copper | 5x Gold Bar, 3x Blightstone | 50% | 20% (Break Risk) | 1.71x (+71%) |
| +6 | 1,000 Copper | 8x Gold Bar, 1x Portal Shard, 5x Blightstone | 40% | 25% (Break Risk) | 1.86x (+86%) |
| +7 | 2,500 Copper | 10x Gold Bar, 2x Portal Shard, 5x Spud Sap | 30% | 30% (Break Risk) | 2.00x (Double Stats)|

- **Repair Fee**: Broken items can be restored to working status at any nomadic trader for a flat fee of **1 Gold Coin (10,000 Copper)**.

---

### 4.9 Maximum Additional Affix Slots (`MAX_ADDITIONAL_AFFIX_SLOTS`)

| Item Rarity Tier | Maximum Additional Affix Slots Permitted | Affix Stone Requirement |
|:---|:---|:---|
| Common | 0 | Not Permitted |
| Uncommon | 0 | Not Permitted |
| Rare | 0 | Not Permitted |
| Epic | 1 | 1x Affix Stone |
| Legendary | 1 | 1x Affix Stone |
| Mythic | 2 | 2x Affix Stone |
| Ancient | 2 | 2x Affix Stone |

---

### 4.10 Complete 27 Equipment Sets Reference Table

| Set Identifier | Display Set Name | Theme / Classification | 2-Piece Passive Milestone | 4-Piece Passive Milestone | 5-Piece / Full Set Aura Milestone |
|:---|:---|:---|:---|:---|:---|
| `ancient` | Ancient Relic Regalia | Endgame Titan | +20% Skill Damage | +15 DEF, +50 HP | Golden Radiant Aura, Double Celestial Reversal Budget |
| `titan` | Titan Colossus Battlegear | Subterranean Obsidian | +10 DEF, +40 HP | Knockback Immunity | Obsidian Stomp Nova on landing from heights |
| `magma` | Nether Magma Forged Plate | Fire / Lava Nether | +15 Fire ATK | Burn Immunity | Searing Lava Trail igniting struck enemies |
| `cryo` | Permafrost Crypt Armor | Ice / Glacier Frost | +15 Frost ATK | Freeze Immunity | Glacial Blizzard Aura slowing nearby enemies 40% |
| `shadow` | Abyssal Shadow Robes | Void / Evasion | +15% Move Speed | 15% Evasion Step | Abyssal Void Aura, Phasing Dash |
| `spud` | Spud Pioneer Overalls | Starter Agriculture | +10 HP, +5% Speed | +20% Farming Speed | Leaf Sprout Aura, Daily Crop Doubling Chance |
| `cactus` | Desert Spined Carapace | Thorns / Defense | +5 DEF | 20% Thorns Return | Spiked Sand Aura reflecting 35% damage to attackers |
| `sin_pride` | Lucifer's Pride | 7 Deadly Sins | +25% Melee ATK | +15% Crit Rate | Blinding Solar Flare blinding surrounding mobs |
| `sin_greed` | Mammon's Greed | 7 Deadly Sins | +25% Coin Drops | +50% Coin Drops | Golden Midas Aura, Coins burst on critical hit |
| `sin_lust` | Asmodeus's Lust | 7 Deadly Sins | +8% Lifesteal | Charm on Hit | Alluring Rose Aura, Stun attacker on contact |
| `sin_envy` | Leviathan's Envy | 7 Deadly Sins | +10% Magic ATK | Mimics Target Buff | Aquatic Viper Aura, Steals 1 positive mob buff |
| `sin_gluttony` | Beelzebub's Gluttony | 7 Deadly Sins | +50% Food Buff Duration | +25% Food Buff Stats | Feast Aura, Allows 6 concurrent food buffs |
| `sin_wrath` | Satan's Wrath | 7 Deadly Sins | +30% ATK under 50% HP | +50% Attack Speed | Blood Red Berserk Aura, Explosive melee cleave |
| `sin_sloth` | Belphegor's Sloth | 7 Deadly Sins | +30 DEF while still | +5 HP/s while still | Iron Shell Aura, Reflects all projectiles while still |
| `virtue_humility`| Robes of Humility | 7 Heavenly Virtues | +15 DEF, -10% Aggro | +30 Max MP | Pure White Sanctuary Aura, +20% Party Defense |
| `virtue_charity` | Vestments of Charity | 7 Heavenly Virtues | +15% Potion Potency | Share heals with party | Golden Halo Aura, Healing pulses radiate to allies |
| `virtue_chastity`| Mail of Chastity | 7 Heavenly Virtues | +20 Magic Resist | Debuff Immunity | Pristine Silver Aura, Purges negative status effects |
| `virtue_gratitude`| Mantle of Gratitude | 7 Heavenly Virtues | +10% EXP Gain | +25% EXP Gain | Amber Sunburst Aura, Awards bonus EXP on boss kill |
| `virtue_temperance`| Garb of Temperance | 7 Heavenly Virtues | -15% Skill MP Cost | -25% Skill MP Cost | Tranquil Water Aura, Skill cooldowns recover 20% faster|
| `virtue_kindness`| Silks of Kindness | 7 Heavenly Virtues | +2 MP/s Regeneration | Revive ally at full HP | Emerald Leaf Aura, Revives player with 50% HP on death |
| `virtue_diligence`| Harness of Diligence | 7 Heavenly Virtues | +25% Mining Speed | Double Ore Yield | Sparks of Industry Aura, Mining strikes damage enemies |
| `virtue_patience`| Plate of Patience | 7 Heavenly Virtues | +1% ATK per second still| +50% Damage after 5s | Steadfast Mountain Aura, Immense single-strike release |
| `katipunero` | Katipunero Vanguard | Philippine History | +20% Bolo / Spear ATK| +15% Sprint Speed | Bayani Crimson Flag Aura, +30% Damage vs Bosses |
| `diwata_bloom` | Diwata's Blessing | Philippine Myth | +25 Max MP, +2 HP/s | Flower trail heal | Radiant Sampaguita Aura, Blinds corrupted creatures |
| `bakunawa_eclipse`| Bakunawa Serpent Scalemail| Philippine Myth | +20% Night Damage | Lunar Eclipse Crit +25%| Celestial Dragon Shadow Aura, Night immunity |
| `sarimanok_regalia`| Sarimanok Feathered Cloak| Philippine Myth | +15% All Elemental ATK| Tri-elemental projectile| Mythic Rainbow Plumage Aura, Quadruple jump wings |
| `tikbalang_trailblazer`| Tikbalang Mountain Hide| Philippine Myth | +35% Mountain Speed | Double Jump Impulse | Phantom Horse Hoofprint Aura, Disorients tracking mobs |

---

### 4.11 Complete 40 Action Combat Skills Roster

| Skill ID | Skill Name | Evolved Skill Name | Hotkey | MP Cost | Cooldown | Dmg Multiplier | Archetype / Description |
|:---|:---|:---|:---|:---|:---|:---|:---|
| `power_slash` | Power Slash | Cataclysmic Cleave | Q | 8 MP | 2.0s | 1.6x (160%) | Forward sword cleave slashing direction of cursor |
| `whirlwind` | Whirlwind | Tempest Cyclone | F | 10 MP | 3.0s | 1.3x (130%) | 360-degree spin striking all surrounding foes |
| `dash` | Swift Dash | Phantom Dash | V | 5 MP | 1.5s | 0.0x (Dodge) | Rapid forward dash granting 0.3s invulnerability |
| `fireball` | Fireball | Inferno Blast | R | 8 MP | 2.2s | 1.8x (180%) | Blazing fire orb detonating with area splash |
| `earth_slam` | Earth Slam | Tectonic Rupture | E | 14 MP | 4.0s | 2.2x (220%) | Ground slam producing a shattering seismic wave |
| `shield_bash` | Shield Bash | Aegis Bulwark | B | 12 MP | 3.0s | 1.5x (150%) | Forward dash with guard up, stunning enemies |
| `meteor` | Meteor Strike | Grand Starfall | G | 40 MP | 12.0s | 4.5x (450%) | [Legendary] Plunging flaming meteor from the sky |
| `frost_nova` | Frost Nova | Glacial Blizzard | X | 12 MP | 3.5s | 1.6x (160%) | Freezing radial wave chilling and slowing enemies |
| `celestial_shield`| Celestial Shield | Divine Sanctuary | Z | 36 MP | 14.0s | 2.0x (200%) | [Legendary] Absorbs 100% damage and reflects projectiles|
| `void_singularity`| Void Singularity | Event Horizon | T | 45 MP | 16.0s | 3.8x (380%) | [Legendary] Gravitational black hole pulling enemies in |
| `celestial_reversal`| Celestial Reversal | Araw Sigil Reversal | Z | 25 MP | 8.0s | 1.5x (150%) | [Ancient] Reflects enemy danmaku with 1.5x damage |
| `shuriken_storm` | Shuriken Storm | Shinobi Hurricane | Q | 10 MP | 2.5s | 1.4x (140%) | Throws 5 piercing shurikens in an expanding cone |
| `star_seeker` | Star Seeker | Astral Constellation | R | 12 MP | 3.0s | 1.7x (170%) | Homing astral stars tracking nearest enemy |
| `arcane_barrage` | Arcane Barrage | Mystic Annihilation | R | 15 MP | 3.2s | 2.0x (200%) | Rapid volley of 8 high-velocity magic bolts |
| `venom_volley` | Venom Volley | Toxic Deluge | F | 11 MP | 2.8s | 1.3x (130%) | Throws 3 poisonous globs leaving corrosive acid pools |
| `void_implosion` | Void Implosion | Abyssal Collapse | G | 32 MP | 10.0s | 3.2x (320%) | Compresses dark energy, imploding after 1.5 seconds |
| `crystal_shatter`| Crystal Shatter | Prismatic Shrapnel | E | 14 MP | 3.8s | 1.9x (190%) | Fires an amethyst crystal that splinters into 8 shards |
| `chain_discharge`| Chain Discharge | Lightning Overload | F | 16 MP | 4.2s | 2.1x (210%) | Arcs electricity between up to 5 adjacent targets |
| `meteor_shower` | Meteor Shower | Astral Rain | G | 42 MP | 13.0s | 3.5x (350%) | Cascades 6 smaller meteors over an extended area |
| `piercing_blizzard`| Piercing Blizzard | Absolute Permafrost | X | 18 MP | 4.5s | 2.0x (200%) | Linear piercing frost beam freezing everything in line |
| `solar_detonation`| Solar Detonation | Supernova Flare | T | 38 MP | 12.0s | 4.0x (400%) | Blinding solar orb exploding after 2.0s delay |
| `arcane_minefield`| Arcane Minefield | Rune Catastrophe | B | 20 MP | 6.0s | 2.4x (240%) | Deploys 4 hovering arcane mines detonating on contact |
| `frost_bomb` | Frost Bomb | Cryo Cataclysm | X | 14 MP | 3.5s | 1.7x (170%) | Lobs an icy bomb shattering into freezing mist |
| `ember_cluster` | Ember Cluster | Pyre Cascade | R | 12 MP | 3.0s | 1.6x (160%) | Fires 4 bouncing fire embers rolling across ground |
| `spectral_pursuit`| Spectral Pursuit | Soul Phantasm | T | 22 MP | 5.5s | 2.3x (230%) | Releases 2 phantoms phasing through solid blocks |
| `returning_hatchet`| Returning Hatchet | Boomerang Cleaver | Q | 9 MP | 2.2s | 1.5x (150%) | Throws spinning hatchet that boomerangs back to player |
| `bolo_cyclone` | Bolo Cyclone | Katipunan Whirler | F | 12 MP | 3.2s | 1.7x (170%) | [Philippine] Flurry of twin bolo blades with bleed DOT |
| `ancestral_guidance`| Ancestral Guidance | Anito's Blessing | B | 24 MP | 10.0s | 0.0x (Buff) | [Philippine] Summons ancestral spirits granting +30% ATK|
| `sumpang_sibat` | Sumpang Sibat | Cursed Bamboo Spear | E | 16 MP | 3.8s | 2.5x (250%) | [Philippine] Hurls enchanted spear impaling targets |
| `magma_eruption` | Magma Eruption | Caldera Vent | G | 35 MP | 11.0s | 3.6x (360%) | Erupts magma geysers from the ground beneath enemies |
| `heavy_cleave` | Heavy Cleave | Titan Sunder | Q | 12 MP | 2.8s | 2.0x (200%) | Overhead executioner swing shattering armor |
| `lunge_thrust` | Lunge Thrust | Rapier Pinpoint | Q | 7 MP | 1.8s | 1.4x (140%) | Precision forward thrust with +25% critical rate |
| `rebound_shield` | Rebound Shield | Kinetic Aegis | B | 14 MP | 4.0s | 1.6x (160%) | Throws shield bouncing between 3 targets before returning|
| `shadow_step` | Shadow Step | Abyssal Teleport | V | 10 MP | 2.5s | 0.0x (Utility) | Blinks 6 blocks toward cursor through solid blocks |
| `holy_smite` | Holy Smite | Dawn Ray | R | 18 MP | 4.0s | 2.3x (230%) | Calls down a vertical celestial pillar from above |
| `poison_dart` | Poison Dart | Viper's Needle | Q | 6 MP | 1.5s | 1.2x (120%) | Rapid blowgun dart applying stacking poison DOT |
| `ice_barrier` | Ice Barrier | Glacial Bulwark | B | 20 MP | 8.0s | 0.0x (Shield) | Forms ice shield absorbing 60 damage for 10 seconds |
| `blood_rage` | Blood Rage | Berserker's Oath | B | 0 HP (20 HP) | 12.0s | 0.0x (Buff) | Sacrifices 20 HP to gain +40% ATK and +30% Move Speed |
| `wind_cutter` | Wind Cutter | Gale Slice | Q | 8 MP | 2.0s | 1.5x (150%) | Launches horizontal slicing sonic air crescent |
| `grand_cross` | Grand Celestial Cross| Zenith Nova | G | 50 MP | 15.0s | 5.0x (500%) | [Grand Legendary] Cross-shaped celestial blast clearing screen |

---

### 4.12 10 Native Philippine Aquatic Species Tuning Table

| Fish Item ID | Display Fish Name | Rarity Tier | Target Clicks Required | Thrash Frequency Rate | Base Selling Value |
|:---|:---|:---|:---|:---|:---|
| `raw_dilis` | Philippine Dilis | Common | 7 Clicks | 0.25 (Low) | 2 Copper |
| `raw_tilapia` | Freshwater Tilapia | Common | 8 Clicks | 0.30 (Low) | 5 Copper |
| `raw_bangus` | National Milkfish (Bangus) | Uncommon | 11 Clicks | 0.35 (Moderate) | 15 Copper |
| `raw_galunggong` | Round Scad (Galunggong) | Uncommon | 12 Clicks | 0.35 (Moderate) | 18 Copper |
| `raw_hito` | Freshwater Catfish (Hito) | Uncommon | 13 Clicks | 0.40 (Moderate) | 22 Copper |
| `raw_maya_maya` | Red Snapper (Maya-Maya) | Rare | 18 Clicks | 0.45 (High) | 60 Copper |
| `raw_tambakol` | Yellowfin Tuna (Tambakol) | Rare | 20 Clicks | 0.50 (High) | 85 Copper |
| `raw_tanigue` | Spanish Mackerel (Tanigue) | Epic | 25 Clicks | 0.55 (Intense) | 250 Copper (2s 50c) |
| `raw_dalagang_bukid`| Yellowtail Fusilier | Epic | 26 Clicks | 0.55 (Intense) | 280 Copper (2s 80c) |
| `raw_lapu_lapu` | Spotted Grouper (Lapu-Lapu) | Epic | 28 Clicks | 0.60 (Intense) | 350 Copper (3s 50c) |

---

### 4.13 8 Native Philippine Crops Agricultural Table

| Crop Identifier | Common Name | Local Tagalog Name | Growth Stages | Light Requirement | Moisture Radius | Harvest Yield |
|:---|:---|:---|:---|:---|:---|:---|
| `crop_palay` | Rice Grain | Palay / Bigas | 4 (Stages 0-3) | Sun or Torchlight | 4 Blocks from Water | 3-5 Palay Grain, 1-2 Seed |
| `crop_bawang` | Native Garlic | Bawang | 4 (Stages 0-3) | Sun or Torchlight | 4 Blocks from Water | 2-4 Garlic Cloves, 1 Seed |
| `crop_sibuyas` | Red Onion | Sibuyas | 4 (Stages 0-3) | Sun or Torchlight | 4 Blocks from Water | 2-4 Red Onions, 1 Seed |
| `crop_luya` | Wild Ginger | Luya | 4 (Stages 0-3) | Sun or Torchlight | 4 Blocks from Water | 2-3 Ginger Roots, 1 Seed |
| `crop_talong` | Long Purple Eggplant| Talong | 4 (Stages 0-3) | Sun or Torchlight | 4 Blocks from Water | 2-4 Eggplants, 1 Seed |
| `crop_sitaw` | Yardlong String Beans| Sitaw | 4 (Stages 0-3) | Sun or Torchlight | 4 Blocks from Water | 3-5 String Beans, 1 Seed |
| `crop_sampalok` | Sour Tamarind Pods | Sampalok | 4 (Stages 0-3) | Sun or Torchlight | 4 Blocks from Water | 2-4 Tamarind Pods, 1 Seed |
| `crop_calamansi` | Philippine Lime | Calamansi | 4 (Stages 0-3) | Sun or Torchlight | 4 Blocks from Water | 3-6 Calamansi Fruits, 1 Seed|

---
"""

if __name__ == "__main__":
    print("docs_section4 ready.")
