"""
Potaria Documentation Generator - Section 3: Exhaustive Inventory of All Pygame-CE Codebase Classes, Functions & Methods
Developer: Kurados
Strict Constraints: NO emojis, relative paths only.
"""

import os
import ast
import glob

FILE_PARITY_METADATA = {
    "main.py": {
        "target": "Assets/Scripts/Player/PlayerController.cs, Assets/Scripts/UI/PotariaHUD.cs, Assets/Scripts/Editor/PotariaSceneBuilder.cs",
        "status": "[PARTIALLY IMPLEMENTED]",
        "notes": "Fixed timestep physics (0.02s), scene bootstrapping, input routing, and in-game HUD ported into Unity. Game state machine transitions and developer cheat console pending for Milestone 4."
    },
    "src/camera.py": {
        "target": "Assets/Scripts/Camera/CameraController.cs",
        "status": "[IMPLEMENTED]",
        "notes": "Target smoothing damping, deadzone clamping, 3-level discrete zoom toggling (1x/2x/3x via Z), instant snap, and 3.0s pitch-black death transition fully ported and verified."
    },
    "src/constants.py": {
        "target": "Assets/Scripts/World/WorldConstants.cs, Assets/Scripts/Data/ItemCategory.cs, Assets/Scripts/Data/BuffCategory.cs, Assets/Scripts/Data/CraftingStation.cs",
        "status": "[IMPLEMENTED]",
        "notes": "All 77 tile IDs, 16x240 chunk dimensions, world layers (70/115/160/205), item categories, buff categories, and UI palettes fully mapped into Unity constants and enums."
    },
    "src/profiler.py": {
        "target": "Assets/Scripts/UI/PotariaHUD.cs",
        "status": "[IMPLEMENTED]",
        "notes": "F3 real-time profiler overlay, live FPS counter, frame time (ms), active chunks, active mobs, and coordinate readouts ported and verified."
    },
    "src/settings_manager.py": {
        "target": "Assets/Scripts/Localization/LocalizationManager.cs, Planned Assets/Scripts/Settings/SettingsManager.cs",
        "status": "[PARTIALLY IMPLEMENTED]",
        "notes": "English and Filipino localization dictionary switching ('L' key) implemented; visual settings menu and JSON settings persistence scheduled for Milestone 4."
    },
    "src/assets/asset_factory.py": {
        "target": "Assets/Scripts/Editor/PotariaTileImporter.cs, Assets/Scripts/Editor/PotariaDataImporter.cs",
        "status": "[IMPLEMENTED]",
        "notes": "2,456 pixel-art PNG sprites ingested into Unity with 16 PPU, Point filtering, and uncompressed RGBA32 format."
    },
    "src/assets/projectile_factory.py": {
        "target": "Assets/Scripts/Combat/Projectile.cs, Assets/Items/Weapons/",
        "status": "[IMPLEMENTED]",
        "notes": "Projectile sprites and animations sliced and mapped into WeaponItemData ScriptableObjects."
    },
    "src/audio/bgm_manager.py": {
        "target": "Planned Assets/Scripts/Audio/BGMManager.cs",
        "status": "[PARTIALLY IMPLEMENTED]",
        "notes": "BGM audio clips ingested into Assets/Audio/; dynamic biome crossfading controller scheduled for Milestone 4."
    },
    "src/audio/narrator_voice.py": {
        "target": "Planned Assets/Scripts/Audio/NarratorVoice.cs",
        "status": "[PARTIALLY IMPLEMENTED]",
        "notes": "Narrator voice audio clips and phoneme blips ingested; cutscene audio sequencer scheduled for Milestone 4."
    },
    "src/audio/sound_effects.py": {
        "target": "Assets/Scripts/Player/PlayerController.cs, Planned Assets/Scripts/Audio/SFXManager.cs",
        "status": "[PARTIALLY IMPLEMENTED]",
        "notes": "Head-blocked jump sound suppression logic ported; 34 SFX clips ingested; spatial 2D audio emitters scheduled for Milestone 4."
    },
    "src/combat/combat_system.py": {
        "target": "Assets/Scripts/Combat/WeaponController.cs, Assets/Scripts/Mob/MobSpawner.cs",
        "status": "[IMPLEMENTED]",
        "notes": "Weapon swing cooldowns, 0.10s-0.45s swing duration, single-target combat enforcement, Ancient cleave exception, and 15-35 tile mob spawner annulus fully ported and verified (116/116 tests)."
    },
    "src/entities/boss.py": {
        "target": "Assets/Scripts/Combat/BossController.cs",
        "status": "[PARTIALLY IMPLEMENTED]",
        "notes": "BossController with Phase 1 & 2 transitions, player scaling, health bar UI, and danmaku emitter hooks ported. Standalone AI state machines for Malus, Ignis, Cryo, Necro, and Sol-Rho scheduled for Milestone 4."
    },
    "src/entities/bullet_hell.py": {
        "target": "Assets/Scripts/Combat/DanmakuEmitter.cs, Assets/Scripts/Combat/Projectile.cs, Assets/Scripts/Player/PlayerController.cs",
        "status": "[IMPLEMENTED]",
        "notes": "16-way spiral novas, rotating celestial cross beams, 52% core lethal hitbox, perimeter graze detection (+1 MP reward, sparks), and 0.45s Celestial Reversal timed reflection fully ported and verified."
    },
    "src/entities/dropped_item.py": {
        "target": "Planned Assets/Scripts/World/DroppedItem.cs",
        "status": "[PARTIALLY IMPLEMENTED]",
        "notes": "ItemData ScriptableObjects with drop tables ready; physical dropped item GameObject with toss physics and magnet pickup scheduled for Milestone 4."
    },
    "src/entities/mob.py": {
        "target": "Assets/Scripts/Mob/SlimeMob.cs, Assets/Scripts/Mob/ZombieMob.cs, Assets/Scripts/Mob/DemonEyeMob.cs, Assets/Scripts/Mob/Mob.cs",
        "status": "[PARTIALLY IMPLEMENTED]",
        "notes": "Green/Purple Slime hop physics, Surface Zombie auto-step jumping, and Demon Eye nocturnal sinusoidal flight ported and verified; livestock mobs and Aswang predator scheduled for Milestones 4-5."
    },
    "src/entities/npc.py": {
        "target": "Planned Assets/Scripts/NPC/TownNPCController.cs, Planned Assets/Scripts/NPC/TraderController.cs",
        "status": "[PENDING / NEED TO IMPLEMENT]",
        "notes": "Trader ware catalogs imported into ScriptableObjects; Guide/Merchant/Nurse town NPCs, housing room occupancy, turtle shell invulnerability defense, and shop UI scheduled for Milestone 4."
    },
    "src/entities/particle.py": {
        "target": "Assets/Scripts/Player/PlayerController.cs, Assets/Scripts/Combat/WeaponController.cs",
        "status": "[PARTIALLY IMPLEMENTED]",
        "notes": "Graze cyan sparks, melee hit feedback, and damage particle bursts ported; unified 2D particle pool scheduled for Milestone 4."
    },
    "src/entities/player.py": {
        "target": "Assets/Scripts/Player/PlayerController.cs",
        "status": "[IMPLEMENTED]",
        "notes": "Complete kinematic player controller with 6.0 run speed, 40.0 accel, 32.0 decel, 12.0 jump force, 0.45x variable jump cut, 0.15s coyote time, 0.12s jump buffer, 0.08s jump grace timer, liquid swimming, 100 oxygen drowning, and 12 FPS animations ported and verified."
    },
    "src/entities/projectile.py": {
        "target": "Assets/Scripts/Combat/Projectile.cs, Assets/Scripts/Combat/ProjectileManager.cs",
        "status": "[IMPLEMENTED]",
        "notes": "Parabolic gravity arrows (vy += 9.8 * 0.44 * dt), magic catalyst homing stars, staff elemental splash bolts, rod piercing javelins, and scepter shockwaves fully ported and verified."
    },
    "src/entities/vfx.py": {
        "target": "Assets/Scripts/Combat/DanmakuEmitter.cs, Assets/Scripts/Player/PlayerController.cs",
        "status": "[PARTIALLY IMPLEMENTED]",
        "notes": "Camera screen trauma shake, graze chime, and 3.0s death pitch-black fade ported; golden solar flare shockwave explosions scheduled for Milestone 4."
    },
    "src/environment/sky.py": {
        "target": "Assets/Scripts/World/Lighting/DayNightCycle2D.cs, Assets/Scripts/World/Lighting/SkyRenderer2D.cs",
        "status": "[IMPLEMENTED]",
        "notes": "720.0s celestial day/night cycle, 4 distinct phases (Dawn, Noon, Sunset, Night), procedural cubic Hermite sky gradient transitions, and 140 twinkling star sprites fully ported and verified."
    },
    "src/environment/sky_presets.py": {
        "target": "Assets/Scripts/World/Lighting/SkyRenderer2D.cs",
        "status": "[IMPLEMENTED]",
        "notes": "Surface biome sky presets (Forest, Desert, Snow, Cavern, Nether) mapped into URP volume sky gradient interpolators."
    },
    "src/loot/__init__.py": {
        "target": "Assets/Scripts/Data/",
        "status": "[IMPLEMENTED]",
        "notes": "Unified data namespace exports for items, weapons, equipment, sets, and food."
    },
    "src/loot/affix_engine.py": {
        "target": "Assets/Scripts/Data/ItemRarity.cs, Assets/Scripts/Data/ItemData.cs",
        "status": "[PARTIALLY IMPLEMENTED]",
        "notes": "Rarity multiplier tables and statutory affix caps defined; procedural affix roll algorithm on dropped items scheduled for Milestone 4."
    },
    "src/loot/item_registry.py": {
        "target": "Assets/Scripts/World/TileDatabase.cs, Assets/Scripts/Editor/PotariaDataImporter.cs",
        "status": "[IMPLEMENTED]",
        "notes": "1,775 ScriptableObject items registered with category, rarity, icon, description, and stats, replacing Python string dictionaries."
    },
    "src/loot/loot_system.py": {
        "target": "Planned Assets/Scripts/Combat/LootDropper.cs",
        "status": "[PARTIALLY IMPLEMENTED]",
        "notes": "Drop chance data imported into ItemData; physical dropped item instantiation on mob and boss death scheduled for Milestone 4."
    },
    "src/loot/rarity_engine.py": {
        "target": "Assets/Scripts/Data/ItemRarity.cs",
        "status": "[IMPLEMENTED]",
        "notes": "7-tier rarity enum (Common, Uncommon, Rare, Epic, Legendary, Mythic, Ancient), hex colors, drop weights, and stat multipliers fully ported and verified."
    },
    "src/modding/__init__.py": {
        "target": "Planned Assets/Scripts/Modding/",
        "status": "[PENDING / NEED TO IMPLEMENT]",
        "notes": "Modding architecture specifications documented; modding runtime scheduled for Milestone 6."
    },
    "src/modding/mod_manager.py": {
        "target": "Planned Assets/Scripts/Modding/ModManager.cs",
        "status": "[PENDING / NEED TO IMPLEMENT]",
        "notes": "Mod manifest parser schemas preserved; dynamic ScriptableObject and AssetBundle content pack injector scheduled for Milestone 6."
    },
    "src/network/client.py": {
        "target": "Planned Assets/Scripts/Network/NetworkClient.cs",
        "status": "[PENDING / NEED TO IMPLEMENT]",
        "notes": "Networking client architecture documented; target engine: FishNet / Steamworks P2P in Milestone 6."
    },
    "src/network/protocol.py": {
        "target": "Planned Assets/Scripts/Network/NetworkProtocol.cs",
        "status": "[PENDING / NEED TO IMPLEMENT]",
        "notes": "Network packet definitions (JOIN, SYNC, MOVE, BLOCK_BREAK, BLOCK_PLACE, CHAT) defined; binary network serialization scheduled for Milestone 6."
    },
    "src/network/server.py": {
        "target": "Planned Assets/Scripts/Network/NetworkServer.cs",
        "status": "[PENDING / NEED TO IMPLEMENT]",
        "notes": "Authoritative multiplayer host server architecture scheduled for FishNet in Milestone 6."
    },
    "src/rendering/__init__.py": {
        "target": "2D Universal Render Pipeline (URP 17.0.3)",
        "status": "[IMPLEMENTED]",
        "notes": "Python rendering package replaced by native Unity Universal Render Pipeline."
    },
    "src/rendering/base_renderer.py": {
        "target": "2D Universal Render Pipeline (URP 17.0.3)",
        "status": "[IMPLEMENTED]",
        "notes": "Abstract rendering interface replaced by Unity's native C++ rendering pipeline."
    },
    "src/rendering/gl_renderer.py": {
        "target": "2D URP Volume Post-Processing",
        "status": "[IMPLEMENTED]",
        "notes": "ModernGL shaders (bloom, vignette, water distortion) mapped to 2D URP Volume components and post-processing passes."
    },
    "src/rendering/renderer_manager.py": {
        "target": "Unity Quality Settings",
        "status": "[IMPLEMENTED]",
        "notes": "HAL switcher superseded by Unity's automatic multiplatform graphics API selection (DirectX 11/12, Vulkan, Metal)."
    },
    "src/rendering/surface_renderer.py": {
        "target": "2D Universal Render Pipeline (URP 17.0.3)",
        "status": "[IMPLEMENTED]",
        "notes": "Software surface rendering eliminated in favor of hardware-accelerated 2D URP on all devices."
    },
    "src/rpg/achievements.py": {
        "target": "Planned Assets/Scripts/RPG/AchievementManager.cs",
        "status": "[PARTIALLY IMPLEMENTED]",
        "notes": "Achievement JSON schemas preserved; in-game toast notifications and Steam achievements hook scheduled for Milestone 6."
    },
    "src/rpg/affix_system.py": {
        "target": "Assets/Scripts/Data/ItemData.cs, Assets/Scripts/RPG/PlayerStats.cs",
        "status": "[PARTIALLY IMPLEMENTED]",
        "notes": "Affix stat definitions and socket allotment caps mapped; runtime affix evaluation on equipped gear scheduled for Milestone 4."
    },
    "src/rpg/enhancement.py": {
        "target": "Assets/Scripts/Data/ItemData.cs, Planned Assets/Scripts/UI/ForgeMasterUI.cs",
        "status": "[PENDING / NEED TO IMPLEMENT]",
        "notes": "Blacksmith enhancement formulas (+1 to +7 success and break curves), 1 Gold repair, and socket carving rules documented; Forge Master UI scheduled for Milestone 4."
    },
    "src/rpg/equipment.py": {
        "target": "Assets/Scripts/Data/EquipmentItemData.cs, Assets/Scripts/RPG/PlayerStats.cs",
        "status": "[PARTIALLY IMPLEMENTED]",
        "notes": "705 equipment ScriptableObjects generated across 10 paperdoll slots; visual paperdoll equipment UI scheduled for Milestone 4."
    },
    "src/rpg/equipment_update.py": {
        "target": "Assets/Scripts/Data/EquipmentSetData.cs",
        "status": "[PARTIALLY IMPLEMENTED]",
        "notes": "27 EquipmentSetData ScriptableObjects with piece links and 2/4/5-piece milestone thresholds generated; runtime set bonus evaluator scheduled for Milestone 4."
    },
    "src/rpg/skills.py": {
        "target": "Assets/Scripts/Input/PotariaInput.cs, Assets/Scripts/UI/PotariaHUD.cs",
        "status": "[PARTIALLY IMPLEMENTED]",
        "notes": "4 skill HUD badges and keyboard triggers mapped (Power Slash, Whirlwind, Dash, Celestial Guard); full 40-skill casting engine scheduled for Milestone 4."
    },
    "src/rpg/stats.py": {
        "target": "Assets/Scripts/RPG/PlayerStats.cs, Assets/Scripts/RPG/CharacterStats.cs",
        "status": "[IMPLEMENTED]",
        "notes": "100-level EXP curve (int(100 * lvl^2.1)), stat scaling (+15 HP, +8 MP, +3 ATK, +1 DEF), defense mitigation formula, 85% defense cap, Titan's Resolve (3x DEF under 30% HP), and dedicated coin purse auto-conversion fully ported and verified."
    },
    "src/ui/character_panel.py": {
        "target": "Planned Assets/Scripts/UI/CharacterPanelUI.cs",
        "status": "[PARTIALLY IMPLEMENTED]",
        "notes": "Backend PlayerStats ready; 10-slot paperdoll visual inventory window with attribute point allocation scheduled for Milestone 4."
    },
    "src/ui/chest_ui.py": {
        "target": "Planned Assets/Scripts/UI/ChestUI.cs",
        "status": "[PARTIALLY IMPLEMENTED]",
        "notes": "Chest item models ready; 20-slot storage container visual grid with shift-click auto-deposit scheduled for Milestone 4."
    },
    "src/ui/crafting.py": {
        "target": "Assets/Scripts/Data/RecipeData.cs, Assets/Scripts/Data/CraftingStation.cs, Planned Assets/Scripts/UI/CraftingUI.cs",
        "status": "[PARTIALLY IMPLEMENTED]",
        "notes": "80+ RecipeData ScriptableObjects validated; 5-tab crafting window (All, Building, Equipment, Furniture, Survival) scheduled for Milestone 4."
    },
    "src/ui/cutscene.py": {
        "target": "Planned Assets/Scripts/UI/CutsceneUI.cs",
        "status": "[PENDING / NEED TO IMPLEMENT]",
        "notes": "Cutscene narration text and audio assets imported; letterbox cinema bars and typewriter dialogue player scheduled for Milestone 4."
    },
    "src/ui/fishing_minigame.py": {
        "target": "Planned Assets/Scripts/UI/FishingMinigameUI.cs",
        "status": "[PENDING / NEED TO IMPLEMENT]",
        "notes": "10 Philippine fish ScriptableObjects imported; 15.0s urgency timer modal, line tension meter, and thrashing fish AI scheduled for Milestone 5."
    },
    "src/ui/hud.py": {
        "target": "Assets/Scripts/UI/PotariaHUD.cs",
        "status": "[PARTIALLY IMPLEMENTED]",
        "notes": "10-slot hotbar, selection frame, Life text/hearts, Mana bar, clock badge, radar badge, 4 skill badges, and F3 profiler ported and verified; side-by-side tooltips and active meal buff tray scheduled for Milestone 4."
    },
    "src/ui/inventory.py": {
        "target": "Planned Assets/Scripts/UI/InventoryUI.cs",
        "status": "[PARTIALLY IMPLEMENTED]",
        "notes": "Inventory data architecture in PlayerStats ready; 40-slot drag-and-drop backpack grid with item splitting and sorting scheduled for Milestone 4."
    },
    "src/ui/menu.py": {
        "target": "Planned Assets/Scripts/UI/MainMenuUI.cs",
        "status": "[PARTIALLY IMPLEMENTED]",
        "notes": "SceneBuilder scaffolds title sequence; main menu, world selection, and world generator UI modal scheduled for Milestone 4."
    },
    "src/ui/minimap.py": {
        "target": "Assets/Scripts/UI/PotariaHUD.cs",
        "status": "[PARTIALLY IMPLEMENTED]",
        "notes": "Radar badge and cardinal directions in HUD ported; full terrain tilemap texture radar with fog of war scheduled for Milestone 4."
    },
    "src/ui/npc_dialogue.py": {
        "target": "Planned Assets/Scripts/UI/NPCDialogueUI.cs",
        "status": "[PENDING / NEED TO IMPLEMENT]",
        "notes": "Dialogue dictionaries imported; typewriter speech bubble, fast-forward text blips, and shop goods grid scheduled for Milestone 4."
    },
    "src/ui/theme.py": {
        "target": "Assets/Scripts/UI/PotariaHUD.cs",
        "status": "[IMPLEMENTED]",
        "notes": "UI styling constants, background tints, gold text highlights, and white border styling fully ported and verified."
    },
    "src/ui/touch_controller.py": {
        "target": "Assets/Scripts/Input/PotariaInput.cs",
        "status": "[PARTIALLY IMPLEMENTED]",
        "notes": "Cross-platform input abstraction hooks verified; onscreen virtual touch joystick and action clusters scheduled for Milestone 4."
    },
    "src/world/chunk_manager.py": {
        "target": "Assets/Scripts/World/ChunkManager.cs, Assets/Scripts/World/ChunkData.cs",
        "status": "[IMPLEMENTED]",
        "notes": "Boundless horizontal chunk streaming (-inf to +inf), 16x240 tile dimensions, 3-chunk active radius, coordinate hash indexing, and distant chunk eviction fully ported and verified (84/84 tests)."
    },
    "src/world/lighting.py": {
        "target": "Assets/Scripts/World/Lighting/PointLightSource2D.cs, Assets/Scripts/World/Lighting/SubterraneanDarkness2D.cs",
        "status": "[IMPLEMENTED]",
        "notes": "Quadratic depth attenuation below Y = 85, pitch-black illumination at cavern depths (Y >= 160), and 2D dynamic point lights for torches and lanterns fully ported and verified."
    },
    "src/world/noise.py": {
        "target": "Assets/Scripts/World/PerlinNoise.cs",
        "status": "[IMPLEMENTED]",
        "notes": "Deterministic 2D Perlin noise engine with multi-octave synthesis, persistence, and lacunarity fully ported and verified."
    },
    "src/world/save_manager.py": {
        "target": "Planned Assets/Scripts/Save/SaveManager.cs",
        "status": "[PENDING / NEED TO IMPLEMENT]",
        "notes": "Save schemas documented; atomic JSON serializer (`world.json.tmp` -> `world.json`), backup snapshot rotations, and HMAC-SHA256 signature verification scheduled for Milestone 4."
    },
    "src/world/storage_chest.py": {
        "target": "Assets/Scripts/World/TileDatabase.cs, Planned Assets/Scripts/World/StorageChestComponent.cs",
        "status": "[PARTIALLY IMPLEMENTED]",
        "notes": "TileChest (28) and TileIronChest (55) registered; 20-slot storage container tile component scheduled for Milestone 4."
    },
    "src/world/tiles.py": {
        "target": "Assets/Scripts/World/TileDefinition.cs, Assets/Scripts/World/TileDatabase.cs",
        "status": "[IMPLEMENTED]",
        "notes": "Complete tile property definitions (hardness, tool requirements, drops, light opacity, solid/wall flags) fully ported and verified."
    },
    "src/world/world.py": {
        "target": "Assets/Scripts/World/WorldTilemaps.cs, Assets/Scripts/World/WorldGenerator.cs",
        "status": "[IMPLEMENTED]",
        "notes": "Dual Tilemap layer architecture (Solid blocks with CompositeCollider2D and Wall tilemap), zero-friction platforming material, water fluid drag, and farmland hydration simulation fully ported and verified."
    },
    "src/world/world_cache.py": {
        "target": "Unity 2D Tilemap Renderer & URP Batching",
        "status": "[IMPLEMENTED]",
        "notes": "Replaced by Unity's native C++ chunk mesh batching and GPU instanced Tilemap rendering, eliminating Python dirty-rect blits."
    },
    "src/world/world_gen.py": {
        "target": "Assets/Scripts/World/WorldGenerator.cs",
        "status": "[IMPLEMENTED]",
        "notes": "Procedural rolling surface hills, cave network carving, ore vein seeding, and subterranean Nether Dungeon brick chambers fully ported and verified (84/84 tests)."
    }
}

def build_section_3(records, tooling_records=None):
    lines = []
    lines.append("## 3. Exhaustive Inventory of All Pygame-CE Codebase Classes, Functions & Methods")
    lines.append("")
    lines.append("This section provides a 100% complete census of every class, method, and standalone function across all 65 engine source files and 20 developer tooling/benchmark scripts in the Pygame-CE reference codebase (`Potaria_Pygame_Backup` and branch `pygame-engine`).")
    lines.append("")
    
    total_files = len(records)
    total_classes = sum(len(r["classes"]) for r in records)
    total_methods = sum(sum(len(c["methods"]) for c in r["classes"]) for r in records)
    total_funcs = sum(len(r["functions"]) for r in records)
    
    tooling_count = len(tooling_records) if tooling_records else 0
    lines.append(f"**Codebase Census:** {total_files} Engine Files ({tooling_count} Tooling/Benchmark Scripts) | {total_classes} Classes | {total_methods} Class Methods | {total_funcs} Standalone Functions.")
    lines.append("")
    
    # Group by directory category
    groups = {
        "3.1 Root Engine Files": [],
        "3.2 World & Terrain Systems (`src/world/*`)": [],
        "3.3 Entity & Actor Systems (`src/entities/*`)": [],
        "3.4 Combat & Ballistics Systems (`src/combat/*`)": [],
        "3.5 RPG Progression & Equipment Systems (`src/rpg/*`)": [],
        "3.6 Loot, Registry & Affix Systems (`src/loot/*`)": [],
        "3.7 User Interface & HUD Systems (`src/ui/*`)": [],
        "3.8 Environment & Atmospheric Systems (`src/environment/*`)": [],
        "3.9 Audio Systems (`src/audio/*`)": [],
        "3.10 Rendering HAL & Shaders (`src/rendering/*`)": [],
        "3.11 Modding & Extensibility (`src/modding/*`)": [],
        "3.12 Multiplayer & Networking (`src/network/*`)": [],
        "3.13 Asset Generation & Factories (`src/assets/*`)": [],
        "3.14 Core Systems & Settings (`src/*`)": []
    }
    
    for r in records:
        p = r["path"]
        if p == "main.py":
            groups["3.1 Root Engine Files"].append(r)
        elif p.startswith("src/world/"):
            groups["3.2 World & Terrain Systems (`src/world/*`)"].append(r)
        elif p.startswith("src/entities/"):
            groups["3.3 Entity & Actor Systems (`src/entities/*`)"].append(r)
        elif p.startswith("src/combat/"):
            groups["3.4 Combat & Ballistics Systems (`src/combat/*`)"].append(r)
        elif p.startswith("src/rpg/"):
            groups["3.5 RPG Progression & Equipment Systems (`src/rpg/*`)"].append(r)
        elif p.startswith("src/loot/"):
            groups["3.6 Loot, Registry & Affix Systems (`src/loot/*`)"].append(r)
        elif p.startswith("src/ui/"):
            groups["3.7 User Interface & HUD Systems (`src/ui/*`)"].append(r)
        elif p.startswith("src/environment/"):
            groups["3.8 Environment & Atmospheric Systems (`src/environment/*`)"].append(r)
        elif p.startswith("src/audio/"):
            groups["3.9 Audio Systems (`src/audio/*`)"].append(r)
        elif p.startswith("src/rendering/"):
            groups["3.10 Rendering HAL & Shaders (`src/rendering/*`)"].append(r)
        elif p.startswith("src/modding/"):
            groups["3.11 Modding & Extensibility (`src/modding/*`)"].append(r)
        elif p.startswith("src/network/"):
            groups["3.12 Multiplayer & Networking (`src/network/*`)"].append(r)
        elif p.startswith("src/assets/"):
            groups["3.13 Asset Generation & Factories (`src/assets/*`)"].append(r)
        else:
            groups["3.14 Core Systems & Settings (`src/*`)"].append(r)
            
    for g_title, g_files in groups.items():
        if not g_files:
            continue
        lines.append(f"### {g_title}")
        lines.append("")
        for r in g_files:
            rel_path = r["path"]
            meta = FILE_PARITY_METADATA.get(rel_path, {
                "target": "Assets/Scripts/",
                "status": "[PENDING / NEED TO IMPLEMENT]",
                "notes": "Component implementation pending porting."
            })
            
            lines.append(f"#### `{rel_path}`")
            lines.append(f"- **Size:** {r['bytes']} bytes | **Lines:** {r['lines']} lines")
            lines.append(f"- **Unity 6 Target Script:** `{meta['target']}`")
            lines.append(f"- **Parity Status:** `{meta['status']}`")
            lines.append(f"- **Porting & Parity Notes:** {meta['notes']}")
            if r["doc"]:
                lines.append(f"- **Description:** {r['doc']}")
            
            if r["classes"]:
                lines.append(f"- **Classes Defined ({len(r['classes'])}):**")
                for c in r["classes"]:
                    c_doc_str = f" - {c['doc']}" if c['doc'] else ""
                    lines.append(f"  - **`class {c['name']}`** (Line {c['lineno']}){c_doc_str}")
                    if c["methods"]:
                        lines.append(f"    - Methods ({len(c['methods'])}):")
                        for m in c["methods"]:
                            sig = m["sig"]
                            m_doc_str = f": {m['doc']}" if m['doc'] else ""
                            lines.append(f"      - `def {m['name']}({sig})` (Line {m['lineno']}){m_doc_str}")
            
            if r["functions"]:
                lines.append(f"- **Standalone Functions ({len(r['functions'])}):**")
                for f in r["functions"]:
                    sig = f["sig"]
                    f_doc_str = f": {f['doc']}" if f['doc'] else ""
                    lines.append(f"  - `def {f['name']}({sig})` (Line {f['lineno']}){f_doc_str}")
            
            if not r["classes"] and not r["functions"]:
                lines.append("- *Declarative definition module containing data constants, dictionaries, and configurations.*")
            
            lines.append("")

    # Developer Tooling & Benchmarks section
    if tooling_records:
        lines.append("### 3.15 Developer Tooling, Benchmarks & Data Generation Scripts")
        lines.append("")
        lines.append("This subsection audits the 20 developer utilities, benchmark scripts, catalog generators, and asset builders in the Pygame-CE repository (`scripts/*`, `tools/*`, and root benchmarks).")
        lines.append("")
        for r in tooling_records:
            rel_path = r["path"]
            lines.append(f"#### `{rel_path}`")
            lines.append(f"- **Size:** {r['bytes']} bytes | **Lines:** {r['lines']} lines")
            if r["doc"]:
                lines.append(f"- **Description:** {r['doc']}")
            if r["classes"]:
                lines.append(f"- **Classes Defined ({len(r['classes'])}):**")
                for c in r["classes"]:
                    c_doc_str = f" - {c['doc']}" if c['doc'] else ""
                    lines.append(f"  - **`class {c['name']}`** (Line {c['lineno']}){c_doc_str}")
                    if c["methods"]:
                        for m in c["methods"]:
                            lines.append(f"    - `def {m['name']}({m['sig']})` (Line {m['lineno']})")
            if r["functions"]:
                lines.append(f"- **Standalone Functions ({len(r['functions'])}):**")
                for f in r["functions"]:
                    lines.append(f"  - `def {f['name']}({f['sig']})` (Line {f['lineno']})")
            if not r["classes"] and not r["functions"]:
                lines.append("- *Executable automation script.*")
            lines.append("")
            
    lines.append("---")
    lines.append("")
    return "\n".join(lines)

if __name__ == "__main__":
    print("docs_section3 ready.")
