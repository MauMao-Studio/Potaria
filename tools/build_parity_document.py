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
import ast

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

def github_slug(text):
    """Generates standard GitHub Flavored Markdown header slug."""
    clean = re.sub(r'[`\*]', '', text).strip().lower()
    clean = re.sub(r'[^\w\s-]', '', clean)
    clean = re.sub(r'\s+', '-', clean)
    return clean.strip('-')

def parse_single_file(fpath, base_dir):
    rel = os.path.relpath(fpath, base_dir).replace("\\", "/")
    try:
        with open(fpath, "r", encoding="utf-8") as f:
            code = f.read()
        tree = ast.parse(code)
    except Exception as e:
        return None

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
                    try:
                        sig = ast.unparse(item.args)
                    except Exception:
                        sig = ", ".join(a.arg for a in item.args.args)
                    methods.append({
                        "name": item.name,
                        "sig": sig,
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
            try:
                sig = ast.unparse(node.args)
            except Exception:
                sig = ", ".join(a.arg for a in node.args.args)
            functions.append({
                "name": node.name,
                "sig": sig,
                "doc": f_doc.strip().split("\n")[0] if f_doc else "",
                "lineno": node.lineno
            })

    return {
        "path": rel,
        "lines": lines,
        "bytes": size_bytes,
        "doc": file_doc.strip().split("\n")[0] if file_doc else "",
        "classes": classes,
        "functions": functions
    }

def parse_all_python_files():
    py_files = [os.path.join(PYGAME_DIR, "main.py")] + sorted(glob.glob(os.path.join(PYGAME_DIR, "src", "**", "*.py"), recursive=True))
    file_records = []
    for fpath in py_files:
        rec = parse_single_file(fpath, PYGAME_DIR)
        if rec:
            file_records.append(rec)
    return file_records

def parse_tooling_python_files():
    root_benchmarks = ["benchmark.py", "profile_pixelarray.py", "test_lighting_perf.py", "test_smoothscale.py"]
    tooling_files = [os.path.join(PYGAME_DIR, f) for f in root_benchmarks if os.path.exists(os.path.join(PYGAME_DIR, f))]
    tooling_files += sorted(glob.glob(os.path.join(PYGAME_DIR, "scripts", "*.py")))
    tooling_files += sorted(glob.glob(os.path.join(PYGAME_DIR, "tools", "*.py")))
    
    records = []
    for fpath in tooling_files:
        rec = parse_single_file(fpath, PYGAME_DIR)
        if rec:
            records.append(rec)
    return records

def build_section_1_header():
    return """# Potaria: Exhaustive Pygame-CE to Unity 6 LTS Feature Parity Specification & Technical Architecture Reference

**Author & Developer:** Kurados  
**Active Development Engine:** Unity 6 LTS (v6000.0.58f1) + 2D Universal Render Pipeline (URP 17.0.3)  
**Legacy Reference Engine:** Pure Python 3.13.16 + Pygame-CE 2.5.8 (Preserved permanently on `pygame-engine` branch)  
**Project Architecture:** One Project Repository (Dual-Profile Architecture: Base Sandbox + Flagship Campaign)  
**Target Verification Standard:** 770 / 770 Pygame Tests Passing; 1,775 Unity ScriptableObjects Validated; 84 / 84 World Gen Tests Passing; 116 / 116 Combat Tests Passing; 57 / 57 Overhaul Systems Tests Passing (0 Errors)  
**Document Classification:** Production-Grade Technical Specification, Codebase Census, and Implementation Parity Audit  

---
"""

def build_section_1_body():
    return """## 1. Executive Technical Architecture & Migration Overview

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
    print("Parsing Python reference engine codebase...")
    records = parse_all_python_files()
    print(f"Parsed {len(records)} engine source files successfully.")

    print("Parsing Python developer tooling and benchmarks...")
    tooling_records = parse_tooling_python_files()
    print(f"Parsed {len(tooling_records)} tooling/benchmark scripts.")

    print("Compiling markdown document sections...")
    sec1_hdr = build_section_1_header()
    sec1_body = build_section_1_body()
    sec2 = build_section_2()
    sec3 = build_section_3(records, tooling_records)
    sec4 = build_section_4()
    sec5 = build_section_5()
    sec6 = build_section_6()
    sec7 = build_section_7()

    body_combined = "\n".join([sec1_body, sec2, sec3, sec4, sec5, sec6, sec7])

    # Extract all ## and ### headings for the dynamic Table of Contents
    heading_matches = re.findall(r'^(#{2,3})\s+(.+)$', body_combined, re.MULTILINE)
    
    toc_lines = ["## Master Table of Contents", ""]
    for level, title in heading_matches:
        slug = github_slug(title)
        indent = "  " if level == "###" else ""
        toc_lines.append(f"{indent}- [{title}](#{slug})")
    
    toc_lines.append("")
    toc_lines.append("---")
    toc_lines.append("")
    toc_block = "\n".join(toc_lines)

    # Insert explicit HTML anchors for every ## and ### heading to guarantee 100% anchor navigation
    def add_explicit_anchor(match):
        level = match.group(1)
        title = match.group(2)
        slug = github_slug(title)
        return f'<a id="{slug}"></a>\n{level} {title}'

    body_with_anchors = re.sub(r'^(#{2,3})\s+(.+)$', add_explicit_anchor, body_combined, flags=re.MULTILINE)

    full_document = f"{sec1_hdr}\n{toc_block}\n{body_with_anchors}"

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
