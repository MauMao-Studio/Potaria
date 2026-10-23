"""
Potaria Documentation Generator - Section 7: Strategic Porting Roadmap & Prioritized Backlog
Developer: Kurados
Strict Constraints: NO emojis, relative paths only.
"""

def build_section_7():
    return """## 7. Strategic Porting Roadmap & Prioritized Backlog (Milestones 4 through 7)

### Milestone 4: Inventory, Crafting, Equipment & Responsive UI (CURRENT FOCUS)
- **Objective**: Deliver a responsive, high-fidelity UI layer matching the authentic Pygame reference, featuring side-by-side item comparison, 40-slot backpack inventory, 5-category crafting book, and mobile touch controls.
- **Prioritized Task Backlog**:
  1. **40-Slot Backpack Inventory UI (`Assets/Scripts/UI/InventoryUI.cs`)**:
     - 4 rows by 10 columns grid with 40x40 pixel slot frames and 4px padding.
     - Drag-and-drop item movement, stack splitting (Right-Click splits half stack), and quick transfer (Shift-Click moves to hotbar/chest).
     - `[ORGANIZE]` button performing automatic gap compaction and item type sorting.
     - Dedicated Coin Purse UI displaying Copper, Silver, and Gold denominations with real-time conversion.
  2. **Side-by-Side Equipment Comparison Cards ('Katabi') (`Assets/Scripts/UI/TooltipRenderer.cs`)**:
     - Hovering any equippable item while Character Info panel is open ('C' key) renders candidate item alongside equipped item.
     - Adorns currently equipped item with bold gold badge: `[ CURRENTLY EQUIPPED ]`.
     - Highlights stat differentials (green for improvements, red for decreases).
     - Screen boundary clamping ensuring dual cards never render off-screen.
  3. **Minecraft-Style 5-Category Crafting Book (`Assets/Scripts/UI/CraftingUI.cs`)**:
     - 5 Category Tabs: All, Building, Equipment, Survival & Consumables, Furniture & Mechanisms.
     - Proximity Crafting Station Detection: Checks player radius for Hand (always available), Work Bench (`TILE_WORK_BENCH`), Furnace (`TILE_FURNACE`), and Cozy Hearth (`TILE_FIREPLACE`).
     - Real-time material sufficiency check: Greyed out recipe frames if ingredients are missing.
  4. **Circular Affix Socket Indicators (`Assets/Scripts/UI/AffixSocketRenderer.cs`)**:
     - Clean ARPG socket indicators: `(O) Empty Affix Socket` in grey; `(*) {Affix Name}` in gold/violet.
     - Enforces `MAX_ADDITIONAL_AFFIX_SLOTS` limits (Common 0, Uncommon 0, Rare 0, Epic 1, Legendary 1, Mythic 2, Ancient 2).
  5. **Bottom-Left Active Meal Buff HUD Overlay (`Assets/Scripts/UI/MealBuffTray.cs`)**:
     - 5 category slots (Offense, Defense, Mobility, Resource, Utility) with radial countdown meters.
  6. **Mobile Virtual Touch Controls (`Assets/Scripts/UI/TouchController.cs`)**:
     - Floating virtual analog joystick with smooth vector return.
     - Action button cluster: Attack/Mine, Jump, Dash, Quick Heal.

---

### Milestone 5: Philippine Farming, Tiered Cooking & Fishing Minigame
- **Objective**: Complete the agricultural lifecycle simulation, furnace/campfire cooking queues, and the 2D fishing battle minigame.
- **Prioritized Task Backlog**:
  1. **Agricultural Lifecycle (`Assets/Scripts/World/CropTileComponent.cs`)**:
     - Attaches to tilled farmland tilemap cells.
     - Tracks 4 growth stages (Stages 0-3) for all 8 native crops (Rice, Garlic, Onion, Ginger, Eggplant, String Beans, Tamarind, Calamansi).
     - Daily morning growth advancement conditional on 4-block water proximity and surface/torch illumination.
     - Hoe tilling and infinite Watering Can hydration tools.
  2. **Tiered Cooking Stations & Grilling (`Assets/Scripts/Cooking/CookingManager.cs`)**:
     - Active cooking queues on Furnaces and Cozy Hearths (2.5s to 20.0s durations).
     - Single active cooking slot per furnace, animated smoke particles during cooking.
     - Direct fish grilling: Converts fresh catches into Inihaw na Bangus, Inihaw na Tilapia, etc.
  3. **2D Fishing Battle Minigame (`Assets/Scripts/Fishing/FishingBattleModal.cs`)**:
     - Interactive right-click tug-of-war modal against 10 Philippine fish species.
     - 15.0s countdown urgency timer, Reel Progress bar (0% to 100%), Line Tension bar (0% to 100%).
     - Fish thrash warning states (reeling during thrash causes +15% tension; line snaps at 100%).
     - Moving golden sweet-spot awarding 1.5x reel speed bonus.

---

### Milestone 6: Steamworks Integration & P2P / LAN Multiplayer
- **Objective**: Establish authoritative multiplayer synchronization and official Steamworks platform features.
- **Prioritized Task Backlog**:
  1. **P2P Multiplayer Transport (`Assets/Scripts/Network/NetworkManager.cs`)**:
     - Integrate `FishNet` (or Unity Netcode for GameObjects) with `Steamworks.NET` / `FishySteamworks`.
     - Valve Steam Datagram Relay (SDR) integration: Direct Steam friend invites (`Invite Friend` / `Join Game` via Steam overlay) with zero port forwarding.
     - Local network UDP broadcast discovery on port 45454 for offline LAN cooperative sessions.
  2. **State Synchronization & Lag Compensation**:
     - Client-side prediction for local player movement and platforming.
     - Entity interpolation for remote players, mobs, and boss danmaku projectiles.
     - Block delta packet broadcast ensuring synchronized terrain destruction and building.
  3. **Steam Platform Services**:
     - Steam Cloud save synchronization format (`saves/worlds/*.json`).
     - Steam Achievements integration (tracking 218 achievements from `data/achievements.json`).
     - Steam Rich Presence (e.g. "Exploring Nether Dungeon (Level 35) [Day 14]").

---

### Milestone 7: Multiplatform Commercial Release (Steam & Google Play Store)
- **Objective**: Package, optimize, and publish Potaria to Steam (Windows PC / Steam Deck) and the Google Play Store (Android 14+).
- **Prioritized Task Backlog**:
  1. **IL2CPP 64-Bit Compilation & Target Builds**:
     - Windows 64-bit standalone executable (`Potaria.exe`).
     - Steam Deck optimization: 16:10 aspect ratio (1280x800 resolution), full gamepad navigation, verified controller glyphs.
     - Signed Android App Bundle (`.aab`) targeting Android 14+ (API Level 34).
  2. **Mobile Lifecycle & Power Management**:
     - Pause game simulation upon Android application switch or incoming call.
     - Background save state preservation preventing lost progress on low-memory process termination.
     - Battery consumption profiling: Stable 60 FPS on mid-range mobile GPUs (Adreno 610 / Mali-G57).
  3. **Commercial Storefront Assets**:
     - Dual-language store descriptions (English and Filipino).
     - Trailer captures, localized gameplay screenshots, and ESRB / age rating documentation.

---
"""

if __name__ == "__main__":
    print("docs_section7 ready.")
