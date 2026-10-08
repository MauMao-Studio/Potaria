"""
Generate Potaria Items & Item Codes Catalog PDF with Asset Images
Exports all 1,402 items with Pixel Art Asset Image, Item Code (ID), Name, Category, Rarity, Key Stats, and Description.
"""

import sys
import os
import io
import html
import base64

# Ensure project root is in path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

import pygame
pygame.init()
pygame.display.set_mode((1, 1), pygame.NOFRAME)

from src.assets.asset_factory import AssetFactory
from src.ui.inventory import ITEM_REGISTRY, ITEM_ALIASES

from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QTextDocument, QPageSize, QPageLayout
from PySide6.QtCore import QSizeF, QMarginsF
from PySide6.QtPrintSupport import QPrinter

RARITY_ORDER = ["common", "uncommon", "rare", "epic", "mythic", "legendary", "ancient"]
RARITY_COLORS = {
    "common": "#7f8c8d",
    "uncommon": "#27ae60",
    "rare": "#2980b9",
    "epic": "#8e44ad",
    "mythic": "#d35400",
    "legendary": "#d4ac0d",
    "ancient": "#c0392b"
}

CATEGORY_NAMES = {
    "tool": "Tools & Mining Equipment",
    "weapon": "Weapons (Melee, Ranged, Magic)",
    "armor_head": "Armor - Helmets & Headwear",
    "armor_chest": "Armor - Chestplates & Robes",
    "armor_legs": "Armor - Greaves & Boots",
    "accessory": "Accessories, Rings & Talismans",
    "skillbook": "Skill Books & Spell Tomes",
    "block": "Blocks & Placeable Tiles",
    "wall": "Background Walls",
    "consumable": "Consumables & Food",
    "special": "Special & Quest Relics",
    "material": "Crafting Materials & Drops",
    "currency": "Currency & Coins",
}

def generate_pdf():
    app = QApplication.instance()
    if not app:
        app = QApplication(sys.argv)

    print("Initializing AssetFactory...")
    af = AssetFactory()

    # Pre-render all item images to base64 data URIs
    print(f"Generating sprite icons for {len(ITEM_REGISTRY)} items...")
    item_icons_b64 = {}
    buf = io.BytesIO()

    for item_id in ITEM_REGISTRY:
        icon_surf = af.items.get(item_id)
        if not icon_surf:
            icon_surf = af.generate_item_icon(item_id)
        
        # Scale to crisp 28x28 if needed for high-res PDF rendering
        if icon_surf.get_size() != (28, 28):
            scaled_surf = pygame.transform.scale(icon_surf, (28, 28))
        else:
            scaled_surf = icon_surf

        buf.seek(0)
        buf.truncate()
        pygame.image.save(scaled_surf, buf, 'png')
        b64_str = base64.b64encode(buf.getvalue()).decode('ascii')
        item_icons_b64[item_id] = b64_str

    print("Grouping and sorting items...")
    items_by_cat = {}
    for item_id, item_data in ITEM_REGISTRY.items():
        cat = item_data.get("cat", "other")
        items_by_cat.setdefault(cat, []).append((item_id, item_data))

    # Sort items within each category: by rarity order, then by name
    for cat in items_by_cat:
        def sort_key(item_tuple):
            iid, d = item_tuple
            rar = str(d.get("rarity", "common")).lower()
            rar_idx = RARITY_ORDER.index(rar) if rar in RARITY_ORDER else 99
            name = d.get("name", iid).lower()
            return (rar_idx, name)
        items_by_cat[cat].sort(key=sort_key)

    total_items = len(ITEM_REGISTRY)

    print("Building HTML document...")
    html_lines = []
    html_lines.append("""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
    body {
        font-family: 'Segoe UI', 'Helvetica Neue', Arial, sans-serif;
        color: #2c3e50;
        margin: 0;
        padding: 0;
        font-size: 8pt;
    }
    .header {
        text-align: center;
        background-color: #1a1e29;
        color: #ffffff;
        padding: 16px 10px;
        margin-bottom: 16px;
        border-radius: 6px;
    }
    .header h1 {
        margin: 0;
        font-size: 19pt;
        color: #f1c40f;
        letter-spacing: 2px;
    }
    .header h2 {
        margin: 4px 0 0 0;
        font-size: 10.5pt;
        color: #ecf0f1;
        font-weight: normal;
    }
    .header p {
        margin: 6px 0 0 0;
        font-size: 8pt;
        color: #bdc3c7;
    }
    .category-section {
        margin-top: 16px;
        margin-bottom: 14px;
    }
    .category-title {
        font-size: 11pt;
        font-weight: bold;
        color: #1a252f;
        border-bottom: 2px solid #34495e;
        padding-bottom: 3px;
        margin-bottom: 6px;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    .category-count {
        font-size: 8.5pt;
        color: #7f8c8d;
        font-weight: normal;
    }
    table {
        width: 100%;
        border-collapse: collapse;
        margin-bottom: 10px;
    }
    th {
        background-color: #2c3e50;
        color: #ffffff;
        text-align: left;
        padding: 5px 6px;
        font-size: 7.5pt;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    td {
        padding: 4px 5px;
        border-bottom: 1px solid #e2e8f0;
        vertical-align: middle;
        font-size: 7.5pt;
    }
    tr:nth-child(even) td {
        background-color: #f8fafc;
    }
    .icon-cell {
        text-align: center;
        width: 34px;
        padding: 2px 4px;
    }
    .icon-box {
        background-color: #222736;
        border-radius: 4px;
        padding: 2px;
        display: inline-block;
    }
    .code-cell {
        font-family: 'Consolas', 'Courier New', monospace;
        font-weight: bold;
        color: #8e44ad;
        font-size: 7.5pt;
        white-space: nowrap;
    }
    .name-cell {
        font-weight: 600;
        color: #1e293b;
        font-size: 8pt;
    }
    .rarity-badge {
        font-weight: bold;
        text-transform: uppercase;
        font-size: 7pt;
        letter-spacing: 0.3px;
    }
    .stats-cell {
        font-size: 7pt;
        color: #475569;
    }
    .desc-cell {
        font-size: 7pt;
        color: #4b5563;
    }
    .footer {
        text-align: center;
        font-size: 7pt;
        color: #95a5a6;
        margin-top: 18px;
        padding-top: 6px;
        border-top: 1px solid #dcdde1;
    }
</style>
</head>
<body>
""")

    # Cover / Header Banner
    html_lines.append(f"""
<div class="header">
    <h1>POTARIA: ROOT REALM</h1>
    <h2>Official Visual Item Catalog & Item Code Reference Guide</h2>
    <p>Complete Reference: {total_items:,} Items with Asset Sprites &bull; 13 Categories &bull; 7 Rarity Tiers &bull; Developer: Kurados</p>
</div>
""")

    # Preferred category sequence
    cat_sequence = [
        "tool", "weapon", "armor_head", "armor_chest", "armor_legs",
        "accessory", "skillbook", "consumable", "material", "block",
        "wall", "special", "currency"
    ]
    for c in items_by_cat.keys():
        if c not in cat_sequence:
            cat_sequence.append(c)

    for cat in cat_sequence:
        if cat not in items_by_cat:
            continue
        items_list = items_by_cat[cat]
        cat_display = CATEGORY_NAMES.get(cat, cat.replace("_", " ").title())

        html_lines.append(f"""
<div class="category-section">
    <div class="category-title">{html.escape(cat_display)} <span class="category-count">({len(items_list)} items)</span></div>
    <table>
        <thead>
            <tr>
                <th style="width: 5%; text-align: center;">Icon</th>
                <th style="width: 20%;">Item Code (ID)</th>
                <th style="width: 20%;">Item Name</th>
                <th style="width: 9%;">Rarity</th>
                <th style="width: 18%;">Combat / Mining Stats</th>
                <th style="width: 28%;">Description & Lore</th>
            </tr>
        </thead>
        <tbody>
""")

        for item_id, d in items_list:
            name = d.get("name", item_id)
            rarity = str(d.get("rarity", "common")).lower()
            rarity_color = RARITY_COLORS.get(rarity, "#7f8c8d")

            # Extract key stats
            stat_parts = []
            if d.get("damage", 0) > 0:
                if cat == "tool":
                    stat_parts.append(f"Tool Dmg: {d['damage']}")
                else:
                    stat_parts.append(f"ATK: {d['damage']}")
            if d.get("atk", 0) > 0:
                stat_parts.append(f"+{d['atk']} ATK")
            if d.get("def", 0) > 0:
                stat_parts.append(f"+{d['def']} DEF")
            if d.get("crit", 0) > 0:
                stat_parts.append(f"+{d['crit']}% Crit")
            if d.get("speed", 0) > 0:
                stat_parts.append(f"+{d['speed']}% Spd")
            if d.get("hp", 0) > 0:
                stat_parts.append(f"+{d['hp']} HP")
            if d.get("mp", 0) > 0:
                stat_parts.append(f"+{d['mp']} MP")
            if d.get("mp_regen", 0) > 0:
                stat_parts.append(f"+{d['mp_regen']} MP/s")
            if d.get("heal", 0) > 0:
                stat_parts.append(f"Heals {d['heal']} HP")
            if d.get("special"):
                stat_parts.append(str(d["special"]))

            stats_str = ", ".join(stat_parts) if stat_parts else "&mdash;"

            desc = d.get("desc", "") or ""
            if not desc:
                desc = d.get("lore", "") or ""

            icon_b64 = item_icons_b64.get(item_id, "")
            img_tag = f'<img src="data:image/png;base64,{icon_b64}" width="22" height="22" />' if icon_b64 else ""

            html_lines.append(f"""
            <tr>
                <td class="icon-cell">{img_tag}</td>
                <td class="code-cell">{html.escape(item_id)}</td>
                <td class="name-cell">{html.escape(name)}</td>
                <td><span class="rarity-badge" style="color: {rarity_color};">{html.escape(rarity.upper())}</span></td>
                <td class="stats-cell">{html.escape(stats_str)}</td>
                <td class="desc-cell">{html.escape(desc)}</td>
            </tr>
""")

        html_lines.append("""
        </tbody>
    </table>
</div>
""")

    # Footer
    html_lines.append(f"""
<div class="footer">
    Potaria: Root Realm &bull; Official Visual Item Catalog &bull; Total Registered Items: {total_items:,} &bull; Page Reference
</div>
</body>
</html>
""")

    full_html = "".join(html_lines)

    output_pdf_path = os.path.join(BASE_DIR, "Potaria_Items_Catalog.pdf")

    print("Rendering PDF via Qt Print Engine...")
    doc = QTextDocument()
    doc.setHtml(full_html)

    printer = QPrinter(QPrinter.HighResolution)
    printer.setOutputFormat(QPrinter.PdfFormat)
    printer.setOutputFileName(output_pdf_path)

    layout = QPageLayout()
    layout.setPageSize(QPageSize(QPageSize.Letter))
    layout.setOrientation(QPageLayout.Portrait)
    layout.setMargins(QMarginsF(10, 10, 10, 10))
    printer.setPageLayout(layout)

    doc.print_(printer)

    print(f"Successfully generated PDF with asset images: {output_pdf_path}")
    print(f"File size: {os.path.getsize(output_pdf_path):,} bytes")
    return output_pdf_path

if __name__ == "__main__":
    generate_pdf()
