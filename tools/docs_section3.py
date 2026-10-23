"""
Potaria Documentation Generator - Section 3: Exhaustive Inventory of All Pygame-CE Codebase Classes, Functions & Methods
Developer: Kurados
Strict Constraints: NO emojis, relative paths only.
"""

import os
import ast
import glob

def build_section_3(records):
    lines = []
    lines.append("## 3. Exhaustive Inventory of All Pygame-CE Codebase Classes, Functions & Methods")
    lines.append("")
    lines.append("This section provides a 100% complete census of every class, method, and standalone function across all 65 source files in the Pygame-CE reference codebase (`Potaria_Pygame_Backup` and branch `pygame-engine`).")
    lines.append("")
    
    total_files = len(records)
    total_classes = sum(len(r["classes"]) for r in records)
    total_methods = sum(sum(len(c["methods"]) for c in r["classes"]) for r in records)
    total_funcs = sum(len(r["functions"]) for r in records)
    
    lines.append(f"**Codebase Scope:** {total_files} Files | {total_classes} Classes | {total_methods} Class Methods | {total_funcs} Standalone Functions.")
    lines.append("")
    
    # Group by directory category
    groups = {
        "Root Files": [],
        "World & Terrain Systems (`src/world/*`)": [],
        "Entity & Actor Systems (`src/entities/*`)": [],
        "Combat & Ballistics Systems (`src/combat/*`)": [],
        "RPG Progression & Equipment Systems (`src/rpg/*`)": [],
        "Loot, Registry & Affix Systems (`src/loot/*`)": [],
        "User Interface & HUD Systems (`src/ui/*`)": [],
        "Environment & Atmospheric Systems (`src/environment/*`)": [],
        "Audio Systems (`src/audio/*`)": [],
        "Rendering HAL & Shaders (`src/rendering/*`)": [],
        "Modding & Extensibility (`src/modding/*`)": [],
        "Multiplayer & Networking (`src/network/*`)": [],
        "Asset Generation & Factories (`src/assets/*`)": [],
        "Core Systems & Settings (`src/*`)": []
    }
    
    for r in records:
        p = r["path"]
        if p == "main.py":
            groups["Root Files"].append(r)
        elif p.startswith("src/world/"):
            groups["World & Terrain Systems (`src/world/*`)"].append(r)
        elif p.startswith("src/entities/"):
            groups["Entity & Actor Systems (`src/entities/*`)"].append(r)
        elif p.startswith("src/combat/"):
            groups["Combat & Ballistics Systems (`src/combat/*`)"].append(r)
        elif p.startswith("src/rpg/"):
            groups["RPG Progression & Equipment Systems (`src/rpg/*`)"].append(r)
        elif p.startswith("src/loot/"):
            groups["Loot, Registry & Affix Systems (`src/loot/*`)"].append(r)
        elif p.startswith("src/ui/"):
            groups["User Interface & HUD Systems (`src/ui/*`)"].append(r)
        elif p.startswith("src/environment/"):
            groups["Environment & Atmospheric Systems (`src/environment/*`)"].append(r)
        elif p.startswith("src/audio/"):
            groups["Audio Systems (`src/audio/*`)"].append(r)
        elif p.startswith("src/rendering/"):
            groups["Rendering HAL & Shaders (`src/rendering/*`)"].append(r)
        elif p.startswith("src/modding/"):
            groups["Modding & Extensibility (`src/modding/*`)"].append(r)
        elif p.startswith("src/network/"):
            groups["Multiplayer & Networking (`src/network/*`)"].append(r)
        elif p.startswith("src/assets/"):
            groups["Asset Generation & Factories (`src/assets/*`)"].append(r)
        else:
            groups["Core Systems & Settings (`src/*`)"].append(r)
            
    for g_title, g_files in groups.items():
        if not g_files:
            continue
        lines.append(f"### {g_title}")
        lines.append("")
        for r in g_files:
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
                        lines.append(f"    - Methods ({len(c['methods'])}):")
                        for m in c["methods"]:
                            arg_str = ", ".join(m["args"])
                            m_doc_str = f": {m['doc']}" if m['doc'] else ""
                            lines.append(f"      - `def {m['name']}({arg_str})` (Line {m['lineno']}){m_doc_str}")
            
            if r["functions"]:
                lines.append(f"- **Standalone Functions ({len(r['functions'])}):**")
                for f in r["functions"]:
                    arg_str = ", ".join(f["args"])
                    f_doc_str = f": {f['doc']}" if f['doc'] else ""
                    lines.append(f"  - `def {f['name']}({arg_str})` (Line {f['lineno']}){f_doc_str}")
            
            if not r["classes"] and not r["functions"]:
                lines.append("- *Declarative definition module containing data constants, dictionaries, and configurations.*")
            
            lines.append("")
            
    lines.append("---")
    lines.append("")
    return "\n".join(lines)

if __name__ == "__main__":
    print("docs_section3 ready.")
