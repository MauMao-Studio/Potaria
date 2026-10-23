"""
Potaria Documentation Generator - Section 5: HUD & UI Layout Specifications, Rendering Logic & Algorithms
Developer: Kurados
Strict Constraints: NO emojis, relative paths only.
"""

def build_section_5():
    return """## 5. HUD & UI Layout Specifications, Rendering Logic & Algorithms

### 5.1 Viewport Coordinates & Anchor Offsets

The reference UI viewport is fixed to **1280 x 720** pixels. Responsive canvas scalers adjust coordinates dynamically on mobile and ultrawide monitors while maintaining the core aspect ratio.

```
+--------------------------------------------------------------------------------------------------+ (0,0)
| [HOTBAR SLOTS 1 - 10]                                    [LIFE HEARTS & HP] [MANA BAR] [CLOCK]    |
| (10, 10) -> (446, 50)                                    (850, 10) -> (1270, 60)                  |
|                                                                                                  |
| [F3 PROFILER OVERLAY]                                                                            |
| (10, 70) -> (240, 260)                                                                           |
|                                                                                                  |
|                                         (SCREEN CENTER)                                          |
|                                            (640, 360)                                            |
|                                                                                                  |
|                                                                                                  |
| [MEAL BUFF TRAY: 5 SLOTS]                                              [SKILL BADGES: Q, F, V, R]|
| (10, 640) -> (260, 700)                                                (480, 650) -> (800, 705)  |
+--------------------------------------------------------------------------------------------------+ (1280, 720)
```

---

### 5.2 10-Slot Hotbar Visual & Functional Specification

- **Anchor & Sizing**:
  - Root position: `X = 10`, `Y = 10`.
  - Individual Slot Dimension: `40 x 40` pixels.
  - Padding Between Slots: `4` pixels.
  - Total Hotbar Width: $10 \\times 40 + 9 \\times 4 = 436$ pixels. Total Height: `40` pixels.
- **Visual Elements per Slot**:
  - Background Plate: Dark slate rectangle `(35, 40, 58, 220)` with 1px border `(85, 95, 130)`.
  - Number Badge: Displayed at top-left `(slot_x + 3, slot_y + 2)` in bold gold font showing numbers `1` through `9`, and `0` for the 10th slot.
  - Centered Item Icon: Scaled to `32 x 32` pixels centered at `(slot_x + 4, slot_y + 4)`.
  - Stack Count Label: Rendered at bottom-right `(slot_x + 36, slot_y + 26)` in compact white text with 1px black outline shadow. Suppressed if count $\\le 1$.
  - Selection Highlight: Active gold border frame `(255, 215, 0)` with thickness of 2 pixels rendered at `(selected_slot * 44 + 8, 8)` with size `44 x 44`.
- **Keyboard & Gamepad Navigation**:
  - Number Keys 1-9 and 0 select slots 0 through 9 directly.
  - Mouse Scroll Wheel cycles active slot: `selected_slot = (selected_slot + scroll_delta) % 10`.
  - Gamepad Bumpers (LB / RB) cycle left and right across the hotbar.

---

### 5.3 Life Hearts & Mana Star Render Pipelines

- **Life Hearts Layout (Top-Right)**:
  - Text Header: `Life: {current_hp} / {max_hp} Lv.{level}` rendered in bold white text at `(SCREEN_WIDTH - 240, 10)`.
  - 10 Heart Icons: Displayed horizontally below the text header from right to left:
    - Each heart represents $10\\%$ of Max HP (20 HP per heart on 200 Max HP base).
    - Full Heart: Radiant crimson heart sprite.
    - Half Heart: Split crimson/grey sprite if current HP is within $[\\text{slot}\\times 20 - 10, \\text{slot}\\times 20)$.
    - Empty Heart: Dark grey hollow heart outline.
- **Mana Bar & Readout**:
  - Positioned at `(SCREEN_WIDTH - 240, 36)`.
  - Text Label: `MP: {current_mp} / {max_mp}` rendered in azure text `(100, 180, 255)`.
  - Azure Mana Meter: Progress bar width = $180$ pixels, height = $8$ pixels.
  - Star Insignia: A 5-point glowing astral star icon anchored to the left of the bar.
- **12-Hour Celestial Clock & Radar Badge**:
  - Positioned at `(SCREEN_WIDTH - 110, 54)`.
  - Format: `{Hours}:{Minutes:02d} {AM/PM} {DAY/NIGHT}` (e.g. `12:00 PM DAY`, `7:04 PM NIGHT`).
  - Radar Key: Small square button labeled `[M]` indicating toggle state of subterranean mini-map radar.

---

### 5.4 Active Meal Buff Tray & Countdown Timers

- **Bottom-Left Layout**:
  - Position: `X = 10`, `Y = SCREEN_HEIGHT - 60` (Y = 660).
  - 5 Dedicated Category Slots spaced horizontally:
    1. Slot 1: Offense (Sword icon badge).
    2. Slot 2: Defense (Shield icon badge).
    3. Slot 3: Mobility (Winged boot icon badge).
    4. Slot 4: Resource / Regen (Flask / Potion icon badge).
    5. Slot 5: Utility / Luck (Four-leaf clover icon badge).
- **Slot Visuals & Countdown Ring**:
  - Background slot size: `36 x 36` pixels with category tint.
  - Centered Food Icon: 24x24 pixel sprite of the active Filipino dish.
  - Radial Countdown Fill: Translucent black radial sweep indicating percentage remaining (`duration / max_duration`).
  - Duration Badge: Time remaining formatted as `3m` or `45s` at slot bottom.
  - Tooltip: Hovering over any active buff slot displays dish name, meal category, duration remaining, and full stat breakdown.

---

### 5.5 Side-by-Side Equipment Comparison ('Katabi') Layout Algorithm

When the player hovers an equippable item in backpack or chest storage while the Character Information panel is open ('C' key), the tooltip engine triggers side-by-side comparison mode ('katabi'):

```
Candidate Item Tooltip Box                  Currently Equipped Tooltip Box
+------------------------------------+      +------------------------------------+
| Dragon Katana                      |      | [ CURRENTLY EQUIPPED ]             |
| [EPIC WEAPON]                      |      | Steel Broadsword                   |
| Weapon Power: 38 Damage (+10 ATK)  | <--> | [RARE WEAPON]                      |
| Use Speed: Fast Speed (0.26s)      |      | Weapon Power: 28 Damage            |
| Enhanced: +3                       |      | Use Speed: Fast Speed (0.32s)      |
| Affix: (O) Empty Socket            |      | Enhanced: +1                       |
| Lore: "Forged in the caldera..."   |      | Lore: "Standard infantry blade."   |
+------------------------------------+      +------------------------------------+
  Width: tw1                                  Width: tw2
  <---------------- total_w = tw1 + 12px + tw2 ---------------->
```

#### Placement Math & Screen Clamping:
1. Candidate tooltip width $tw_1$ and height $th_1$ measured from text lines.
2. Equipped tooltip width $tw_2$ and height $th_2$ measured from text lines.
3. Total width: $W_{\\text{total}} = tw_1 + 12 + tw_2$. Total height: $H_{\\text{total}} = \\max(th_1, th_2)$.
4. Horizontal Placement:
   - Default: `tx1 = mouse_x + 16`.
   - Right overflow check: If `tx1 + W_total > SCREEN_WIDTH - 10`:
     - Try placing to left of cursor: `tx1 = mouse_x - 16 - W_total`.
     - If left side also overflows: clamp to screen edge: `tx1 = max(10, SCREEN_WIDTH - W_total - 10)`.
   - Equipped card position: `tx2 = tx1 + tw1 + 12`.
5. Vertical Placement:
   - Default: `ty = mouse_y + 16`.
   - Bottom overflow check: If `ty + H_total > SCREEN_HEIGHT - 10`:
     - Try placing above cursor: `ty = max(10, mouse_y - H_total - 8)`.
     - Clamped minimum: `ty = max(10, ty)`.

---

### 5.6 Comprehensive Tooltip Line Construction Pipeline

Every item tooltip in Potaria is assembled through a deterministic 7-stage pipeline:

```
[Stage 1: Header]
  • If currently equipped comparison card: "[ CURRENTLY EQUIPPED ]" (Bold Gold #FFD700)
  • Item Name (Formatted in Rarity Tier Color)
  • Rarity & Category Badge: "[RARITY CATEGORY]" (e.g. "[EPIC WEAPON]")

[Stage 2: Core Numeric Stats]
  • Weapons: "Weapon Power: {damage} Damage", "Use Speed: {speed_desc}"
  • Armor: "+{def} Defense", "+{hp} Max HP", "+{mp} Max MP"
  • Accessories: "+{speed}% Movement Speed", "+{crit}% Critical Strike Chance"
  • Food: "Meal Buff [{CATEGORY}] ({duration}s): {dish_name}", Bulleted stat list

[Stage 3: Enhancement & Broken State]
  • If enhanced: "Enhanced: +{level} (Double Stats at +7)" (Cyan #50F0FF)
  • If broken: "[BROKEN] Requires repair at Mystic Trader!" (Red #FF4646)

[Stage 4: Rolled Base Stats & Tags]
  • Rolled stats: "Rolled Base Stats: +{v} {STAT}" (Goldenrod #FFE68C)
  • Item tags: "Tags: {tag1} • {tag2} • {tag3}" (Light Cyan #64DCFF)

[Stage 5: Special Perks & Affix Sockets]
  • Special perks: "• {effect_description}" (Aqua #64F0F0)
  • Affix sockets:
    - Empty: "(O) Empty Affix Socket" (Grey #A0A0A0)
    - Filled: "(*) {Affix Name}: {Affix Description}" (Gold / Violet)

[Stage 6: Equipment Set Membership]
  • Set header: "Set: {Set Name} ({active_count}/{total_pieces})" (Gold)
  • Threshold milestones: "(2) +X Stat", "(4) +Y Stat", "(5) Active Aura" (Dim if inactive)

[Stage 7: Narrative & Lore]
  • Description: "{Word-wrapped item usage text}" (Light Slate #D7E1F0)
  • Lore Quote (Legendary/Mythic/Ancient only): '"{Author quote}"' (Amber #F0CD78)
```

---

### 5.7 Real-Time Profiler Overlay Layout (F3)

- Pressing **F3** toggles the real-time diagnostic telemetry HUD:
  - Line 1: `Potaria Engine v0.2.0a [Unity 6 LTS / URP 17.0.3]` (White)
  - Line 2: `FPS: 60.0 (Target: 60.0) | Frame Time: 16.6ms` (Green $>55$, Yellow $30-55$, Red $<30$)
  - Line 3: `Active Chunks: 12 (Cached: 48) | Tilemap Geometry: 4,890 Polygons`
  - Line 4: `Active Entities: 14 (Player: 1, Mobs: 8, Projectiles: 5, Drops: 0)`
  - Line 5: `Lighting Engine: Day/Night (Time: 0.35 NOON) | Point Lights: 6`
  - Line 6: `Pass Timers: World: 1.8ms | Physics: 3.2ms | Projectiles: 0.9ms | HUD: 1.4ms`

---

### 5.8 Pseudo-Code: Celestial Reversal Projectile Reflection Algorithm

```csharp
// Executed every frame during active Celestial Reversal window
public void UpdateCelestialReversal(float dt)
{
    if (_reflectionTimer <= 0f || _reflectionBudget <= 0) return;

    _reflectionTimer -= dt;
    Vector2 playerCenter = GetCenter();
    float radiusSquared = _reflectionRadius * _reflectionRadius;

    var activeProjectiles = ProjectileManager.Instance.ActiveProjectiles;
    for (int i = 0; i < activeProjectiles.Count; i++)
    {
        var proj = activeProjectiles[i];
        if (proj == null || !proj.IsEnemy || proj.IsReflected) continue;

        // Check if projectile center is within reflection field radius
        float distSq = (proj.Position - playerCenter).sqrMagnitude;
        if (distSq <= radiusSquared)
        {
            // Reflect: reverse velocity and amplify speed by 25%
            proj.Velocity = -proj.Velocity * 1.25f;

            // Invert ownership so bullet damages bosses instead of player
            proj.IsEnemy = false;
            proj.IsReflected = true;

            // Apply 1.5x damage amplification multiplier
            proj.Damage = Mathf.RoundToInt(proj.Damage * 1.5f);

            // Extend lifetime to ensure bullet can travel back to boss
            proj.RemainingLife += 2.0f;

            // Spawn radiant golden reflection spark VFX
            SpawnReflectionSpark(proj.Position);

            // Decrement active reflection budget
            _reflectionBudget--;
            if (_reflectionBudget <= 0)
            {
                _reflectionTimer = 0f;
                break;
            }
        }
    }
}
```

---

### 5.9 Pseudo-Code: 52% Core Hitbox vs. Graze Detection Algorithm

```csharp
// Evaluated during projectile motion against the player entity
public void CheckPlayerCollision(Projectile proj, PlayerController player)
{
    Vector2 projCenter = proj.Position;
    Vector2 playerCenter = player.Center;
    float dist = Vector2.Distance(projCenter, playerCenter);

    float visualRadius = proj.VisualRadius;
    float lethalCoreRadius = visualRadius * 0.52f;      // 52% Core Hitbox
    float grazeOuterRadius = visualRadius * 1.75f;      // 175% Graze Perimeter

    // 1. Check for Lethal Core Hitbox Collision
    if (dist <= lethalCoreRadius + player.HitboxRadius)
    {
        // Lethal Strike
        player.TakeDamage(proj.Damage);
        proj.Despawn();
        return;
    }

    // 2. Check for Perimeter Graze Collision
    if (dist <= grazeOuterRadius + player.HitboxRadius && !proj.HasGrazed)
    {
        proj.HasGrazed = true; // Each projectile grazes at most once

        // Award +1 MP grazing reward
        player.Stats.RestoreMp(1);

        // Trigger visual and auditory graze feedback
        player.TriggerGrazeFeedback();
    }
}
```

---

### 5.10 Pseudo-Code: Dual-Tilemap Snag-Free Platforming with BoxCast & Normal Detection

```csharp
// Rigidbody2D FixedUpdate execution for ground and slope detection
private void FixedUpdate()
{
    // Perform downward BoxCast past the bottom of player collider
    Vector2 boxSize = new Vector2(_collider.size.x * 0.85f, 0.08f);
    Vector2 boxOrigin = (Vector2)transform.position + _collider.offset - new Vector2(0f, _collider.size.y * 0.5f);

    int hitCount = Physics2D.BoxCastNonAlloc(
        boxOrigin,
        boxSize,
        0f,
        Vector2.down,
        _groundHitBuffer,
        0.06f,
        _groundLayerMask
    );

    bool groundedThisStep = false;
    Vector2 averageNormal = Vector2.up;

    for (int i = 0; i < hitCount; i++)
    {
        var hit = _groundHitBuffer[i];
        if (hit.collider == null || hit.collider == _collider) continue;

        // Verify surface angle is walkable (slope <= 45 degrees)
        float slopeAngle = Vector2.Angle(hit.normal, Vector2.up);
        if (slopeAngle <= 45.0f)
        {
            groundedThisStep = true;
            averageNormal = hit.normal;
            break;
        }
    }

    // Handle jump grace timer to prevent slope adhesion canceling upward leaps
    if (_jumpGraceTimer > 0f)
    {
        _jumpGraceTimer -= Time.fixedDeltaTime;
        _isGrounded = false;
    }
    else
    {
        _isGrounded = groundedThisStep;
        _groundNormal = averageNormal;
    }

    // Refresh Coyote Timer while grounded
    if (_isGrounded)
    {
        _coyoteTimer = _coyoteTime;
    }
    else
    {
        _coyoteTimer -= Time.fixedDeltaTime;
    }
}
```

---
"""

if __name__ == "__main__":
    print("docs_section5 ready.")
