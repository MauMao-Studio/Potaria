#!/usr/bin/env python3
"""
Potaria - Exhaustive Pygame-CE to Unity 6 LTS Feature Parity Documentation Builder
Developer: Kurados
Generates: docs/PYGAME_TO_UNITY_FEATURE_PARITY_DOCUMENTATION.md

Standing Constraints Adhered To:
- STRICTLY NO EMOJIS in markdown or console outputs.
- STRICTLY NO local machine file paths/URIs (relative repository paths only).
- Complete Table of Contents with working markdown links.
- Exhaustive inventory of all 65 Python files, 123 classes, 1170 methods, 153 standalone functions.
- Exact numeric values, attributes, formulas, physics constants, locomotion speeds, RPG formulas.
- Comprehensive UI/HUD layout details, rendering logic, tooltips, comparison cards ('katabi'), hotbars.
- Full Parity Audit Matrix with direct C# script mapping and [IMPLEMENTED] / [PARTIALLY IMPLEMENTED] / [PENDING / NEED TO IMPLEMENT] status tags.
"""

import os
import sys
import glob
import re

# Ensure tools directory is in sys.path
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)

from docs_section2 import build_section_2
from docs_section3 import build_section_3
from docs_section4 import build_section_4
from docs_section5 import build_section_5
from docs_section6 import build_section_6
from docs_section7 import build_section_7

UNITY_DIR = os.path.abspath(os.path.join(SCRIPT_DIR, ".."))
PYGAME_DIR = os.path.abspath(os.path.join(UNITY_DIR, "..", "Potaria_Pygame_Backup"))
OUTPUT_FILE = os.path.join(UNITY_DIR, "docs", "PYGAME_TO_UNITY_FEATURE_PARITY_DOCUMENTATION.md")

def parse_all_python_files():
    import ast
    py_files = [os.path.join(PYGAME_DIR, "main.py")] + sorted(glob.glob(os.path.join(PYGAME_DIR, "src", "**", "*.py"), recursive=True))
    file_records = []

    for fpath in py_files:
        rel = os.path.relpath(fpath, PYGAME_DIR).replace("\\", "/")
        try:
            with open(fpath, "r", encoding="utf-8") as f:
                code = f.read()
            tree = ast.parse(code)
        except Exception as e:
            continue

        file_doc = ast.get_docstring(tree) or ""
        lines = len(code.splitlines())
        size_bytes = len(code.encode("utf-8"))

        classes = []
        for node in tree.body:
            if isinstance(node, ast.ClassDef):
                c_doc = ast.get_docstring(node) or ""
                methods = []
                for item in node.body:
                    if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                        m_doc = ast.get_docstring(item) or ""
                        args = [a.arg for a in item.args.args]
                        methods.append({
                            "name": item.name,
                            "args": args,
                            "doc": m_doc.strip().split("\n")[0] if m_doc else "",
                            "lineno": item.lineno
                        })
                classes.append({
                    "name": node.name,
                    "doc": c_doc.strip().split("\n")[0] if c_doc else "",
                    "methods": methods,
                    "lineno": node.lineno
                })

        functions = []
        for node in tree.body:
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                f_doc = ast.get_docstring(node) or ""
                args = [a.arg for a in node.args.args]
                functions.append({
                    "name": node.name,
                    "args": args,
                    "doc": f_doc.strip().split("\n")[0] if f_doc else "",
                    "lineno": node.lineno
                })

        file_records.append({
            "path": rel,
            "lines": lines,
            "bytes": size_bytes,
            "doc": file_doc.strip().split("\n")[0] if file_doc else "",
            "classes": classes,
            "functions": functions
        })

    return file_records

def build_section_1():
    return """# Potaria: Exhaustive Pygame-CE to Unity 6 LTS Feature Parity Specification & Technical Architecture Reference

**Author & Developer:** Kurados  
**Active Development Engine:** Unity 6 LTS (v6000.0.58f1) + 2D Universal Render Pipeline (URP 17.0.3)  
**Legacy Reference Engine:** Pure Python 3.13.16 + Pygame-CE 2.5.8 (Preserved permanently on `pygame-engine` branch)  
**Project Architecture:** One Project Repository (Dual-Profile Architecture: Base Sandbox + Flagship Campaign)  
**Target Verification Standard:** 770 / 770 Pygame Tests Passing; 1,775 Unity ScriptableObjects Validated; 84 / 84 World Gen Tests Passing; 116 / 116 Combat Tests Passing; 57 / 57 Overhaul Systems Tests Passing (0 Errors)  
**Document Classification:** Production-Grade Technical Specification, Codebase Census, and Implementation Parity Audit  

---

## Master Table of Contents

- [1. Executive Technical Architecture & Migration Overview](#1-executive-technical-architecture--migration-overview)
  - [1.1 Franchise Strategy & One Project Repository Model](#11-franchise-strategy--one-project-repository-model)
  - [1.2 Legacy Engine Specification: Python 3.13 + Pygame-CE](#12-legacy-engine-specification-python-313--pygame-ce)
  - [1.3 Active Target Engine Specification: Unity 6 LTS + 2D URP](#13-active-target-engine-specification-unity-6-lts--2d-urp)
  - [1.4 Verified Migration Milestones & Test Baselines](#14-verified-migration-milestones--test-baselines)
- [2. System-by-System Deep Technical Architecture Breakdown](#2-system-by-system-deep-technical-architecture-breakdown)
  - [2.1 World Generation, Infinite Chunk Streaming & Procedural Terrain](#21-world-generation-infinite-chunk-streaming--procedural-terrain)
  - [2.2 Dual Tilemap Geometry, Composite Colliders & Snag-Free Platforming](#22-dual-tilemap-geometry-composite-colliders--snag-free-platforming)
  - [2.3 2D Dynamic Lighting, Celestial Day/Night Phases & Subterranean Darkness](#23-2d-dynamic-lighting-celestial-daynight-phases--subterranean-darkness)
  - [2.4 Locomotion, Kinematic Physics & Player Character Controller](#24-locomotion-kinematic-physics--player-character-controller)
  - [2.5 Liquid Physics, Buoyancy, Swimming Mechanics & Oxygen Drowning](#25-liquid-physics-buoyancy-swimming-mechanics--oxygen-drowning)
  - [2.6 Combat Engine: Weapon Archetypes, Attack Speeds & Single-Target Rules](#26-combat-engine-weapon-archetypes-attack-speeds--single-target-rules)
  - [2.7 Ballistics Engine: Parabolic Gravity, Homing, Piercing & Shockwaves](#27-ballistics-engine-parabolic-gravity-homing-piercing--shockwaves)
  - [2.8 Touhou-Inspired Bullet-Hell Boss Encounters & Danmaku Novas](#28-touhou-inspired-bullet-hell-boss-encounters--danmaku-novas)
  - [2.9 Grazing Mechanics, Precision Dodge Sparking & Mana Rewards](#29-grazing-mechanics-precision-dodge-sparking--mana-rewards)
  - [2.10 Celestial Reversal: Timed Projectile Reflection Mechanics](#210-celestial-reversal-timed-projectile-reflection-mechanics)
  - [2.11 Action RPG Statistics, 100-Level EXP Curve & Attribute Scaling](#211-action-rpg-statistics-100-level-exp-curve--attribute-scaling)
  - [2.12 Damage Mitigation Formulas, Defense Curves & Critical Strike Scaling](#212-damage-mitigation-formulas-defense-curves--critical-strike-scaling)
  - [2.13 Philippine Culinary System, 79 Recipes & 5-Meal Buff Framework](#213-philippine-culinary-system-79-recipes--5-meal-buff-framework)
  - [2.14 19 Statutory Meal Buff Contribution Caps](#214-19-statutory-meal-buff-contribution-caps)
  - [2.15 Philippine Agricultural Simulation, Soil Tilling & 8 Native Crops](#215-philippine-agricultural-simulation-soil-tilling--8-native-crops)
  - [2.16 2D Fishing Battle Minigame & 10 Native Philippine Aquatic Species](#216-2d-fishing-battle-minigame--10-native-philippine-aquatic-species)
  - [2.17 Chroisen-Style Paperdoll Equipment System & 10 Equipment Slots](#217-chroisen-style-paperdoll-equipment-system--10-equipment-slots)
  - [2.18 27 Progressive Equipment Sets & Tiered Milestone Synergies](#218-27-progressive-equipment-sets--tiered-milestone-synergies)
  - [2.19 Canonical 7-Tier Rarity Engine & Stat Roll Distribution](#219-canonical-7-tier-rarity-engine--stat-roll-distribution)
  - [2.20 Item Enhancement (+1 to +7) Strategic Risk Curves & Break Risks](#220-item-enhancement-1-to-7-strategic-risk-curves--break-risks)
  - [2.21 Affix Engine, Affix Stone Carving & Slot Allotment Caps](#221-affix-engine-affix-stone-carving--slot-allotment-caps)
  - [2.22 Mobs & Boss AI State Machines (33 Mob Types & 5 Boss Titans)](#222-mobs--boss-ai-state-machines-33-mob-types--5-boss-titans)
  - [2.23 Nomadic Animated Traders, Turtle Shell Shield Defense & 1 Gold Repair](#223-nomadic-animated-traders-turtle-shell-shield-defense--1-gold-repair)
  - [2.24 Housing Validity, Room Enclosure Checks & Village Settlement](#224-housing-validity-room-enclosure-checks--village-settlement)
  - [2.25 HUD Architecture: Hotbars, Hearts, Mana, Clock Badge & Minimap Radar](#225-hud-architecture-hotbars-hearts-mana-clock-badge--minimap-radar)
  - [2.26 Side-by-Side Equipment Comparison Cards ('Katabi') & Tooltips](#226-side-by-side-equipment-comparison-cards-katabi--tooltips)
  - [2.27 F3 Real-Time Profiler Overlay & Frame Telemetry](#227-f3-real-time-profiler-overlay--frame-telemetry)
  - [2.28 Mobile Touch Virtual Controller, Virtual Joystick & Action Clusters](#228-mobile-touch-virtual-controller-virtual-joystick--action-clusters)
  - [2.29 Audio Engine: Synthesized SFX, Dynamic Biome BGM & Narrator Speech](#229-audio-engine-synthesized-sfx-dynamic-biome-bgm--narrator-speech)
  - [2.30 Multi-Layer Save Engine, HMAC Security Signatures & World Caching](#230-multi-layer-save-engine-hmac-security-signatures--world-caching)
  - [2.31 Multiplayer Architecture: LAN UDP Discovery & FishNet/Steamworks P2P](#231-multiplayer-architecture-lan-udp-discovery--fishnetsteamworks-p2p)
  - [2.32 Modding & DLC Content Pack Extensibility System](#232-modding--dlc-content-pack-extensibility-system)
- [3. Exhaustive Inventory of All Pygame-CE Codebase Classes, Functions & Methods](#3-exhaustive-inventory-of-all-pygame-ce-codebase-classes-functions--methods)
- [4. Master Reference of Exact Numeric Values, Formulas & Physical Constants](#4-master-reference-of-exact-numeric-values-formulas--physical-constants)
  - [4.1 Canonical Master Constants Reference (`src/constants.py`)](#41-canonical-master-constants-reference-srcconstantspy)
  - [4.2 Kinematic & Locomotion Tuning Constants](#42-kinematic--locomotion-tuning-constants)
  - [4.3 Fluid Mechanics & Oxygen Depletion Formula](#43-fluid-mechanics--oxygen-depletion-formula)
  - [4.4 Combat & Damage Calculation Formulas](#44-combat--damage-calculation-formulas)
  - [4.5 100-Level RPG Progression & EXP Formulas](#45-100-level-rpg-progression--exp-formulas)
  - [4.6 Statutory Meal Buff Contribution Caps (`MEAL_BUFF_CAPS`)](#46-statutory-meal-buff-contribution-caps-meal_buff_caps)
  - [4.7 7-Tier Rarity Engine Tables & Affix Budgets](#47-7-tier-rarity-engine-tables--affix-budgets)
  - [4.8 Item Enhancement (+1 to +7) Requirements, Success Curves & Break Risks](#48-item-enhancement-1-to-7-requirements-success-curves--break-risks)
  - [4.9 Maximum Additional Affix Slots (`MAX_ADDITIONAL_AFFIX_SLOTS`)](#49-maximum-additional-affix-slots-max_additional_affix_slots)
  - [4.10 Complete 27 Equipment Sets Reference Table](#410-complete-27-equipment-sets-reference-table)
  - [4.11 Complete 40 Action Combat Skills Roster](#411-complete-40-action-combat-skills-roster)
  - [4.12 10 Native Philippine Aquatic Species Tuning Table](#412-10-native-philippine-aquatic-species-tuning-table)
  - [4.13 8 Native Philippine Crops Agricultural Table](#413-8-native-philippine-crops-agricultural-table)
- [5. HUD & UI Layout Specifications, Rendering Logic & Algorithms](#5-hud--ui-layout-specifications-rendering-logic--algorithms)
  - [5.1 Viewport Coordinates & Anchor Offsets](#51-viewport-coordinates--anchor-offsets)
  - [5.2 10-Slot Hotbar Visual & Functional Specification](#52-10-slot-hotbar-visual--functional-specification)
  - [5.3 Life Hearts & Mana Star Render Pipelines](#53-life-hearts--mana-star-render-pipelines)
  - [5.4 Active Meal Buff Tray & Countdown Timers](#54-active-meal-buff-tray--countdown-timers)
  - [5.5 Side-by-Side Equipment Comparison ('Katabi') Layout Algorithm](#55-side-by-side-equipment-comparison-katabi-layout-algorithm)
  - [5.6 Comprehensive Tooltip Line Construction Pipeline](#56-comprehensive-tooltip-line-construction-pipeline)
  - [5.7 Real-Time Profiler Overlay Layout (F3)](#57-real-time-profiler-overlay-layout-f3)
  - [5.8 Pseudo-Code: Celestial Reversal Projectile Reflection Algorithm](#58-pseudo-code-celestial-reversal-projectile-reflection-algorithm)
  - [5.9 Pseudo-Code: 52% Core Hitbox vs. Graze Detection Algorithm](#59-pseudo-code-52-core-hitbox-vs-graze-detection-algorithm)
  - [5.10 Pseudo-Code: Dual-Tilemap Snag-Free Platforming with BoxCast & Normal Detection](#510-pseudo-code-dual-tilemap-snag-free-platforming-with-boxcast--normal-detection)
- [6. Comprehensive Unity 6 Parity Audit Matrix](#6-comprehensive-unity-6-parity-audit-matrix)
- [7. Strategic Porting Roadmap & Prioritized Backlog (Milestones 4 through 7)](#7-strategic-porting-roadmap--prioritized-backlog-milestones-4-through-7)

---

## 1. Executive Technical Architecture & Migration Overview

### 1.1 Franchise Strategy & One Project Repository Model
Potaria is architected under a unified **One Project Repository** model. The repository contains both the sandbox foundation and the narrative flagship:
- **Sandbox Base Game ('Potaria')**: Boundless horizontal sandbox action RPG with infinite chunk generation, building, mining, Philippine farming, tiered cooking, Chroisen paperdoll gear, and cooperative LAN/Steam P2P multiplayer.
- **Narrative Flagship ('Potaria: Root Realm')**: Handcrafted dungeon-crawling story edition built upon the same physics, combat, bullet-hell danmaku, and culinary mechanics.

The migration transfers the proven game systems developed and verified in Python 3.13 into Unity 6 LTS to achieve high-performance native execution across Windows PC, Steam Deck, and Android mobile devices, while eliminating Python's Global Interpreter Lock (GIL) and graphics driver overhead.

### 1.2 Legacy Engine Specification: Python 3.13 + Pygame-CE
The original codebase preserved on the `pygame-engine` branch operates on:
- Runtime: Pure Python 3.13.16 64-bit.
- Graphics / Audio: `pygame-ce` 2.5.8 (SDL 2.32.10).
- Hardware Rendering HAL: Modern OpenGL 3.3 Core Profile via `PyOpenGL 3.1.9` with GLSL vertex and fragment shaders for bloom, vignette, water distortion, and color grading, backed by a pure software SurfaceRenderer fallback.
- Audio Synthesis: Procedural 16-bit 44.1 kHz PCM audio synthesis for swing sounds, damage, footsteps, and spatial audio cues.
- Automated QA: 770 test cases executed via `pytest`, achieving 100% green verification across world generation, inventory, physics, and combat.

### 1.3 Active Target Engine Specification: Unity 6 LTS + 2D URP
The active development branch (`main`) is built upon:
- Engine Version: **Unity 6 LTS (v6000.0.58f1)**.
- Render Pipeline: **2D Universal Render Pipeline (URP 17.0.3)**.
- Physics: 2D Physics engine with `Rigidbody2D` (interpolated fixed time step 0.02s) and `CompositeCollider2D` configured with polygon geometry for snag-free movement.
- Lighting: 2D URP dynamic lights (Global Light 2D for celestial day-night cycles, Point Light 2D for torches, lanterns, and fireplaces with soft shadow attenuation).
- Data Architecture: Typed C# `ScriptableObject` assets for items, weapons, armor, sets, food buffs, crops, and crafting recipes, eliminating hardcoded string dictionaries.
- Input: Unity New Input System (`UnityEngine.InputSystem`) with cross-platform bindings for Keyboard/Mouse, Gamepad (Steam Deck / Xbox), and Mobile Virtual Touch.

### 1.4 Verified Migration Milestones & Test Baselines
- **Milestone 1 (Scaffold, Asset Ingestion & Core Data Layer)**: COMPLETED. 1,775 ScriptableObject assets generated and verified with 0 errors via `PotariaDataImporter`. 2,456 pixel-art PNG sprites organized with 16 PPU, Point filtering, and uncompressed textures.
- **Milestone 2 (2D Tilemaps, Chunk Streaming & Procedural Generation)**: COMPLETED. 84 / 84 tests passing in `PotariaWorldTest`. Dual tilemap layer architecture, CompositeCollider2D, Perlin cave synthesis, ore veins, and asynchronous chunk streaming.
- **Milestone 3 (Player Controller, Physics, Combat, Day/Night Lighting, HUD & Dual Localization)**: COMPLETED. 116 / 116 tests passing in `PotariaCombatTest`; 57 / 57 tests passing in `PotariaOverhaulTest`. Ground detection BoxCastNonAlloc, jump grace timers, 12 FPS animation cycles, danmaku emitters, 52% core hitboxes, graze detection, 10-slot HUD hotbar, life/mana readouts, and English/Filipino localization.
- **Milestone 4 (Inventory, Crafting, Equipment & Responsive UI)**: IN PROGRESS. Backpack inventory, side-by-side comparison cards ('katabi'), 5-tab crafting book, and affix socket indicators.
- **Milestone 5 (Farming, Tiered Cooking & Fishing Minigame)**: SCHEDULED.
- **Milestone 6 (Steamworks & P2P Multiplayer)**: SCHEDULED.
- **Milestone 7 (Multiplatform Commercial Release)**: SCHEDULED.

---
"""

def generate_parity_document():
    print("Parsing Python reference codebase...")
    records = parse_all_python_files()
    print(f"Parsed {len(records)} files successfully.")

    print("Compiling markdown document sections...")
    sec1 = build_section_1()
    sec2 = build_section_2()
    sec3 = build_section_3(records)
    sec4 = build_section_4()
    sec5 = build_section_5()
    sec6 = build_section_6()
    sec7 = build_section_7()

    full_document = "\n".join([sec1, sec2, sec3, sec4, sec5, sec6, sec7])

    # Quality and Constraint Verification
    # 1. Strictly NO emojis
    emoji_pattern = re.compile(r"[\U00010000-\U0010ffff]", flags=re.UNICODE)
    emoji_matches = emoji_pattern.findall(full_document)
    if emoji_matches:
        print(f"ERROR: Found {len(emoji_matches)} unicode emojis! Stripping them...")
        full_document = emoji_pattern.sub("", full_document)

    # 2. Strictly NO local machine file paths/URIs
    local_path_patterns = [
        r"[A-Za-z]:\\[^\s\)\`]+",
        r"[A-Za-z]:/[^\s\)\`]+",
        r"file:///[A-Za-z]:[^\s\)\`]+"
    ]
    for pat in local_path_patterns:
        full_document = re.sub(pat, "relative_path", full_document)

    # Ensure parent directory exists
    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(full_document)

    lines_count = len(full_document.splitlines())
    bytes_count = len(full_document.encode("utf-8"))
    print(f"SUCCESS: Documentation written to {OUTPUT_FILE}")
    print(f"Document Metrics: {lines_count} lines, {bytes_count} bytes.")

if __name__ == "__main__":
    generate_parity_document()
