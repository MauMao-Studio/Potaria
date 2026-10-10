import sys
import os
import io
import json

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

import pygame
pygame.init()
pygame.display.set_mode((1, 1), pygame.NOFRAME)

from src.assets.asset_factory import AssetFactory
from src.ui.inventory import ITEM_REGISTRY
import src.ui.crafting  # Ensures all 129 craftable items are registered in ITEM_REGISTRY

from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QPainter, QFont, QImage, QColor
from PySide6.QtCore import QRectF, QPointF, Qt
from PySide6.QtPrintSupport import QPrinter

RARITY_ORDER = ["common", "uncommon", "rare", "epic", "mythic", "legendary", "ancient"]
RARITY_COLORS = {
    "common": QColor(127, 140, 141),
    "uncommon": QColor(39, 174, 96),
    "rare": QColor(41, 128, 185),
    "epic": QColor(142, 68, 173),
    "mythic": QColor(211, 84, 0),
    "legendary": QColor(212, 172, 13),
    "ancient": QColor(192, 57, 43),
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

    af = AssetFactory()

    items_by_cat = {}
    for item_id, item_data in ITEM_REGISTRY.items():
        cat = item_data.get("cat", "other")
        items_by_cat.setdefault(cat, []).append((item_id, item_data))

    cat_sequence = [
        "tool", "weapon", "armor_head", "armor_chest", "armor_legs",
        "accessory", "skillbook", "consumable", "material", "block",
        "wall", "special", "currency",
    ]
    for c in items_by_cat.keys():
        if c not in cat_sequence:
            cat_sequence.append(c)

    total_items = len(ITEM_REGISTRY)
    output_pdf_path = os.path.join(BASE_DIR, "Potaria_Items_Catalog.pdf")

    printer = QPrinter(QPrinter.HighResolution)
    printer.setOutputFormat(QPrinter.PdfFormat)
    printer.setOutputFileName(output_pdf_path)

    painter = QPainter()
    painter.begin(printer)

    page_rect = printer.pageRect(QPrinter.DevicePixel)
    width = page_rect.width()
    height = page_rect.height()

    margin = 300
    content_top_y = margin + 200
    content_bottom_y = height - margin - 240

    page_num = 1

    font_title = QFont("Segoe UI", 14, QFont.Bold)
    font_cat = QFont("Segoe UI", 12, QFont.Bold)
    font_header = QFont("Segoe UI", 9, QFont.Bold)
    font_text = QFont("Segoe UI", 8)

    current_cat_display = "Overview & Affix System"

    def draw_header_footer():
        # Strict Top Header Band (y: 120 .. 340)
        painter.setFont(font_title)
        painter.setPen(QColor(30, 35, 45))
        title_text = "POTARIA: ROOT REALM - Official Item Catalog"
        if current_cat_display:
            title_text += f" | {current_cat_display}"
        painter.drawText(QRectF(margin, 120, width - 2 * margin, 180), Qt.AlignLeft | Qt.AlignVCenter, title_text)
        painter.setPen(QColor(160, 165, 175))
        painter.drawLine(QPointF(margin, 330), QPointF(width - margin, 330))

        # Strict Bottom Footer Band (y: height - 300 .. height - 120)
        painter.setPen(QColor(160, 165, 175))
        painter.drawLine(QPointF(margin, height - 300), QPointF(width - margin, height - 300))
        painter.setFont(font_text)
        painter.setPen(QColor(60, 65, 75))
        footer_rect = QRectF(margin, height - 270, width - 2 * margin, 120)
        painter.drawText(
            footer_rect,
            Qt.AlignLeft | Qt.AlignVCenter,
            "Developer: Kurados | Potaria & Potaria: Root Realm Item & Affix Reference",
        )
        painter.drawText(
            footer_rect,
            Qt.AlignRight | Qt.AlignVCenter,
            f"Page {page_num} | Total Registered Items: {total_items}",
        )

    col_widths = [0.08, 0.21, 0.21, 0.10, 0.18, 0.22]
    w = width - 2 * margin
    cols = [margin + w * sum(col_widths[:i]) for i in range(len(col_widths))]

    def draw_table_header(y):
        painter.setFont(font_header)
        painter.fillRect(QRectF(margin, y, w, 120), QColor(44, 52, 64))
        painter.setPen(QColor(255, 255, 255))
        headers = ["Icon", "Item Code", "Item Name", "Rarity", "Stats", "Description"]
        for i, text in enumerate(headers):
            painter.drawText(
                QRectF(cols[i] + 15, y, w * col_widths[i] - 30, 120),
                Qt.AlignLeft | Qt.AlignVCenter,
                text,
            )
        return y + 145

    # Draw Page 1 Header & Data-Driven Affix Summary
    draw_header_footer()
    current_y = content_top_y

    affixes_path = os.path.join(BASE_DIR, "data", "affixes", "affixes.json")
    if os.path.exists(affixes_path):
        with open(affixes_path, "r", encoding="utf-8") as f:
            affixes_data = json.load(f)

        painter.setFont(font_cat)
        painter.setPen(QColor(25, 30, 40))
        painter.drawText(
            QRectF(margin, current_y, w, 140),
            Qt.AlignLeft | Qt.AlignVCenter,
            f"Data-Driven Multi-Affix Registry ({len(affixes_data)} Modifiers)",
        )
        current_y += 160

        for aff_key, aff in affixes_data.items():
            line_str = (
                f"[{aff.get('type', 'prefix').upper()}] {aff.get('name', aff_key)} "
                f"(Min Rarity: {aff.get('min_rarity', 'Uncommon')} | Power: {aff.get('power_type', 'stat')}) - "
                f"{aff.get('desc', '')}"
            )
            painter.setFont(font_text)
            painter.setPen(QColor(40, 45, 55))
            painter.drawText(QRectF(margin + 20, current_y, w - 40, 100), Qt.AlignLeft | Qt.AlignVCenter, line_str)
            current_y += 95

        current_y += 80

    # Render each item category with strict row-boundary pagination
    for cat in cat_sequence:
        if cat not in items_by_cat:
            continue

        items_list = items_by_cat[cat]

        def sort_key(item_tuple):
            iid, d = item_tuple
            rar = str(d.get("rarity", "common")).lower()
            rar_idx = RARITY_ORDER.index(rar) if rar in RARITY_ORDER else 99
            name = d.get("name", iid).lower()
            return (rar_idx, name)

        items_list.sort(key=sort_key)

        cat_display = CATEGORY_NAMES.get(cat, cat.replace("_", " ").title())
        current_cat_display = cat_display

        # Require enough vertical space for category header + table header + at least 1 row (680 px)
        if current_y + 680 > content_bottom_y:
            printer.newPage()
            page_num += 1
            draw_header_footer()
            current_y = content_top_y

        painter.setFont(font_cat)
        painter.setPen(QColor(25, 30, 40))
        painter.drawText(
            QRectF(margin, current_y, w, 160),
            Qt.AlignLeft | Qt.AlignVCenter,
            f"{cat_display} ({len(items_list)} items)",
        )
        current_y += 180
        current_y = draw_table_header(current_y)

        for row_idx, (item_id, d) in enumerate(items_list):
            stat_parts = []
            for stat in ["damage", "atk", "def", "crit", "speed", "hp", "mp", "mp_regen", "heal", "special"]:
                if d.get(stat, 0):
                    stat_parts.append(f"{stat.upper()}: {d[stat]}")
            stats_str = ", ".join(stat_parts) if stat_parts else "-"
            desc = d.get("desc", "") or d.get("lore", "") or "-"
            item_name = d.get("name", item_id)

            painter.setFont(font_text)
            flags = Qt.AlignLeft | Qt.AlignTop | Qt.TextWordWrap
            id_rect = painter.boundingRect(QRectF(0, 0, w * col_widths[1] - 30, 5000), flags, item_id)
            name_rect = painter.boundingRect(QRectF(0, 0, w * col_widths[2] - 30, 5000), flags, item_name)
            stats_rect = painter.boundingRect(QRectF(0, 0, w * col_widths[4] - 30, 5000), flags, stats_str)
            desc_rect = painter.boundingRect(QRectF(0, 0, w * col_widths[5] - 30, 5000), flags, desc)

            row_height = max(
                185,
                id_rect.height() + 50,
                name_rect.height() + 50,
                stats_rect.height() + 50,
                desc_rect.height() + 50,
            )

            # Page break check BEFORE drawing anything in this row
            if current_y + row_height > content_bottom_y:
                printer.newPage()
                page_num += 1
                draw_header_footer()
                current_y = content_top_y
                current_y = draw_table_header(current_y)

            # Alternating subtle row shading
            if row_idx % 2 == 1:
                painter.fillRect(QRectF(margin, current_y - 10, w, row_height), QColor(246, 248, 250))

            icon_surf = af.items.get(item_id)
            if not icon_surf:
                icon_surf = af.generate_item_icon(item_id)
            # Crisp nearest-neighbor upscale so pixel art remains razor sharp
            upscaled_surf = pygame.transform.scale(icon_surf, (64, 64))

            buf = io.BytesIO()
            pygame.image.save(upscaled_surf, buf, "png")
            buf.seek(0)
            img = QImage.fromData(buf.read())

            icon_y = current_y + max(0, (row_height - 140) / 2 - 10)
            painter.drawImage(QRectF(cols[0] + 15, icon_y, 140, 140), img)

            text_y = current_y + 15
            painter.setFont(font_text)
            painter.setPen(QColor(20, 20, 20))
            painter.drawText(QRectF(cols[1] + 15, text_y, w * col_widths[1] - 30, row_height - 20), flags, item_id)
            painter.drawText(QRectF(cols[2] + 15, text_y, w * col_widths[2] - 30, row_height - 20), flags, item_name)

            rarity = str(d.get("rarity", "common")).upper()
            painter.setPen(RARITY_COLORS.get(rarity.lower(), QColor(0, 0, 0)))
            painter.drawText(QRectF(cols[3] + 15, text_y, w * col_widths[3] - 30, row_height - 20), flags, rarity)

            painter.setPen(QColor(35, 35, 35))
            painter.drawText(QRectF(cols[4] + 15, text_y, w * col_widths[4] - 30, row_height - 20), flags, stats_str)
            painter.drawText(QRectF(cols[5] + 15, text_y, w * col_widths[5] - 30, row_height - 20), flags, desc)

            current_y += row_height
            painter.setPen(QColor(215, 220, 225))
            painter.drawLine(QPointF(margin, current_y - 10), QPointF(width - margin, current_y - 10))
            current_y += 15

    painter.end()
    print(f"Generated PDF at: {output_pdf_path} (Pages: {page_num}, Items: {total_items})")


if __name__ == "__main__":
    generate_pdf()
