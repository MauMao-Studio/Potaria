import os
import sys

sys.path.insert(0, os.getcwd())

from src.ui.inventory import ITEM_REGISTRY
from src.ui.crafting import RECIPES

# docx imports
import docx
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn

# reportlab imports
import reportlab
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether, HRFlowable
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfgen import canvas

filipino_dishes = [
    'chicken_adobo', 'pork_adobo', 'sinigang', 'kare_kare', 'bulalo', 'tinola',
    'lechon', 'pancit_bihon', 'arroz_caldo', 'halo_halo', 'kaldereta', 'balut',
    'itlog_na_maalat', 'sinangag', 'daing_na_bangus', 'sinigang_na_bangus',
    'ginataang_tilapia', 'kinilaw_na_tanigue'
]

cooked_fishes = [
    'cooked_bangus', 'cooked_tilapia', 'cooked_galunggong', 'cooked_maya_maya',
    'cooked_tanigue', 'cooked_tambakol', 'cooked_lapu_lapu', 'cooked_hito',
    'cooked_dilis', 'cooked_dalagang_bukid'
]

potato_delicacies = [
    'mashed_potato', 'golden_fry', 'hearty_root_stew', 'glazed_golden_tuber',
    'smoked_spud_jerky', 'gilded_russet', 'potato_bread', 'sweet_tuber_pie',
    'herbal_salve'
]

raw_fishes = [
    'raw_bangus', 'raw_tilapia', 'raw_galunggong', 'raw_maya_maya', 'raw_tanigue',
    'raw_tambakol', 'raw_lapu_lapu', 'raw_hito', 'raw_dilis', 'raw_dalagang_bukid'
]

raw_meats = [
    'raw_chicken', 'raw_pork', 'pork_belly', 'raw_beef', 'raw_goat_meat',
    'duck_egg', 'carabao_milk'
]

pantry_ingredients = [
    'raw_potato', 'rice', 'garlic', 'onion', 'ginger', 'tamarind', 'eggplant',
    'string_beans', 'black_pepper', 'calamansi', 'soy_sauce', 'vinegar',
    'salt', 'shaved_ice', 'condensed_milk', 'ube_halaya', 'pancit_noodles',
    'peanut_butter', 'coconut_milk', 'spud_sap', 'seaweed', 'snow_block',
    'wood', 'glowing_mushroom', 'gold_bar'
]

recipe_map = {r["result"]: r for r in RECIPES}

ITEM_ACQUISITION = {
    'raw_potato': 'Cultivated from Tilled Soil or harvested from wild Spud patches.',
    'rice': 'Harvested from flooded paddy tiles or purchased from rural traders.',
    'garlic': 'Foraged in lowland grassy meadows or cultivated in home gardens.',
    'onion': 'Cultivated from vegetable seeds or found in agricultural crates.',
    'ginger': 'Harvested from root patches in forest clearings and riverbanks.',
    'tamarind': 'Gathered from tropical wild tamarind trees.',
    'eggplant': 'Farmed in fertile soil patches or collected from wild flora.',
    'string_beans': 'Cultivated along crop trellises or foraged in bushlands.',
    'black_pepper': 'Harvested from pepper vines in deep forest groves.',
    'calamansi': 'Picked from native citrus shrubs found near coastal settlements.',
    'soy_sauce': 'Brewed condiment obtained from general goods traders or fermented cellars.',
    'vinegar': 'Fermented by hand from fresh Spud Sap in glass jars.',
    'salt': 'Smelted in a furnace by evaporating mineral-rich Tangled Seaweed.',
    'shaved_ice': 'Hand-crushed from fresh Mountain Snow Blocks.',
    'condensed_milk': 'Simmered in a furnace using Fresh Carabao Milk and sweet Spud Sap.',
    'ube_halaya': 'Slow-cooked in a furnace with Purple Spuds, condensed milk, and sap.',
    'pancit_noodles': 'Rolled and cut by hand from ground Milagrosa Rice flour.',
    'peanut_butter': 'Roasted and ground in a furnace using tubers, sap, and sea salt.',
    'coconut_milk': 'Extracted by hand from shredded palm fiber and natural sap.',
    'spud_sap': 'Extracted by tapping mature wild tuber roots and sacred trees.',
    'seaweed': 'Dived and foraged along shallow coastal waters and coral reefs.',
    'snow_block': 'Quarried from the frosty peaks of the sub-zero alpine biome.',
    'wood': 'Chopped from forest trees using any woodcutting axe.',
    'glowing_mushroom': 'Harvested from bioluminescent deep cavern biomes.',
    'gold_bar': 'Smelted in a stone furnace from raw gold ore veins.',
    'raw_bangus': 'Caught with fishing rod in brackish estuaries and calm lagoons.',
    'raw_tilapia': 'Caught in freshwater rivers, inland lakes, and ponds.',
    'raw_galunggong': 'Caught in open sea waters and ocean shores.',
    'raw_maya_maya': 'Caught around deep offshore coral drop-offs.',
    'raw_tanigue': 'Prized game fish hooked in open ocean waters using advanced rods.',
    'raw_tambakol': 'Hooked in deep ocean currents with sturdy fishing tackle.',
    'raw_lapu_lapu': 'Rare catch landed around rocky sea caves and deep ocean reefs.',
    'raw_hito': 'Hooked in muddy swamps, marshy pools, and murky riverbeds.',
    'raw_dilis': 'Netted or caught with light tackle along shallow coastal shores.',
    'raw_dalagang_bukid': 'Vibrant reef fish hooked near sunlit coral gardens.',
    'raw_chicken': 'Obtained from native free-range poultry in grassy meadows.',
    'raw_pork': 'Obtained from native wild boars and domesticated pigs.',
    'pork_belly': 'Choice cut harvested from prime livestock or rural butchers.',
    'raw_beef': 'Harvested from pastoral cattle in highland pasturelands.',
    'raw_goat_meat': 'Sourced from agile mountain goats navigating cliffside crags.',
    'duck_egg': 'Gathered from riverside duck nesting grounds and farm coops.',
    'carabao_milk': 'Gently milked from docile carabaos resting near mud wallows.'
}

SECTIONS = [
    ("Authentic Filipino Cuisine", filipino_dishes, "Signature traditional dishes featuring rich savory, sour, and aromatic flavor profiles. Highly effective for major health restoration during perilous explorations."),
    ("Fried, Smoked, and Steamed Fish", cooked_fishes, "Fresh marine and freshwater catches cooked over embers to maximize nutritional and healing value."),
    ("Potato Specialities and Delicacies", potato_delicacies, "Artisanal root-based dishes, energy-dense pastries, and restorative tuber salves crafted from the sacred spuds of Potaria."),
    ("Fresh Catches (Raw Fishes)", raw_fishes, "Wild aquatic species caught with fishing rods across estuaries, lakes, coral reefs, and deep ocean waters."),
    ("Livestock, Poultry, and Dairy", raw_meats, "Nutrient-rich animal cuts, eggs, and farm milks gathered from native domestic animals and livestock."),
    ("Pantry, Spices, and Cooking Essentials", pantry_ingredients, "Foundational crops, milled grains, seasonings, and binding agents essential for preparing the realm's finest dishes.")
]

# -------------------------------------------------------------
# DOCX BUILDER
# -------------------------------------------------------------
def set_cell_background(cell, hex_color):
    shading_elm = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{hex_color}"/>')
    cell._tc.get_or_add_tcPr().append(shading_elm)

def set_cell_margins(cell, top=100, bottom=100, left=140, right=140):
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = parse_xml(f'<w:tcMar {nsdecls("w")}><w:top w:w="{top}" w:type="dxa"/><w:bottom w:w="{bottom}" w:type="dxa"/><w:left w:w="{left}" w:type="dxa"/><w:right w:w="{right}" w:type="dxa"/></w:tcMar>')
    tcPr.append(tcMar)

def build_docx():
    doc = Document()
    
    # Page setup
    sections = doc.sections
    for s in sections:
        s.top_margin = Inches(0.7)
        s.bottom_margin = Inches(0.7)
        s.left_margin = Inches(0.7)
        s.right_margin = Inches(0.7)
    
    # Title Cover
    p_title = doc.add_paragraph()
    p_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_title = p_title.add_run("THE ROYAL POTARIA COOKBOOK")
    r_title.bold = True
    r_title.font.name = "Georgia"
    r_title.font.size = Pt(26)
    r_title.font.color.rgb = RGBColor(123, 17, 19) # Burgundy
    
    p_sub = doc.add_paragraph()
    p_sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_sub = p_sub.add_run("An Epicurean Guide to Culinary Arts, Hearth Recipes, and Native Ingredients of Potaria")
    r_sub.italic = True
    r_sub.font.name = "Georgia"
    r_sub.font.size = Pt(13)
    r_sub.font.color.rgb = RGBColor(140, 100, 40) # Warm bronze
    
    p_meta = doc.add_paragraph()
    p_meta.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_meta = p_meta.add_run("Published by The Royal Culinary Guild of Potaria | Complete Edition 1.0\n")
    r_meta.font.name = "Calibri"
    r_meta.font.size = Pt(10)
    r_meta.font.color.rgb = RGBColor(100, 100, 100)
    
    doc.add_paragraph() # spacer
    
    # Introduction Section
    p_h1 = doc.add_heading(level=1)
    r_h1 = p_h1.add_run("1. Principles of Hearth and Culinary Craft")
    r_h1.font.name = "Georgia"
    r_h1.font.size = Pt(16)
    r_h1.font.color.rgb = RGBColor(123, 17, 19)
    
    p_intro = doc.add_paragraph()
    p_intro.paragraph_format.line_spacing = 1.15
    p_intro.paragraph_format.space_after = Pt(8)
    p_intro.add_run(
        "Culinary craft in the world of Potaria represents one of the most vital disciplines for survival, exploration, "
        "and legendary triumph. While potions offer instantaneous medicinal alchemy, prepared meals provide profound vitality, "
        "replenishing substantial Health Points (HP) to keep adventurers thriving through unforgiving boss battles and deep cavern descents."
    )
    
    p_stations = doc.add_paragraph()
    p_stations.paragraph_format.line_spacing = 1.15
    p_stations.paragraph_format.space_after = Pt(12)
    p_stations.add_run("Potaria features two recognized modes of culinary assembly:\n").bold = True
    p_stations.add_run("• Furnace Hearth Cooking (station=\"furnace\"): ").bold = True
    p_stations.add_run("The traditional hearth utilizes fuel combustion to simmer complex stews (Bulalo, Kare-Kare, Sinigang), deep-fry marine catches, roast prime meats (Lechon Kawali), bake breads, and clarify condensed milks.\n")
    p_stations.add_run("• Artisanal Preparation By Hand (station=None): ").bold = True
    p_stations.add_run("Delicate refreshments, iced desserts (Special Halo-Halo), cured marinades (Kinilaw na Tanigue), fresh brined duck eggs, and noodle rolling require no thermal heat, executed directly from the player's personal craft inventory.")
    
    # Sections and tables
    col_widths = [Inches(1.5), Inches(1.1), Inches(0.8), Inches(0.9), Inches(1.8), Inches(1.0)]
    
    for sec_idx, (title, items, desc_text) in enumerate(SECTIONS, start=2):
        doc.add_page_break()
        
        h_sec = doc.add_heading(level=1)
        r_sec = h_sec.add_run(f"{sec_idx}. {title}")
        r_sec.font.name = "Georgia"
        r_sec.font.size = Pt(15)
        r_sec.font.color.rgb = RGBColor(123, 17, 19)
        
        p_desc = doc.add_paragraph()
        p_desc.paragraph_format.line_spacing = 1.15
        p_desc.paragraph_format.space_after = Pt(10)
        p_desc.add_run(desc_text).italic = True
        
        # Create Table
        table = doc.add_table(rows=1, cols=6)
        table.alignment = WD_TABLE_ALIGNMENT.CENTER
        table.autofit = False
        
        # Header Row
        hdr_cells = table.rows[0].cells
        hdr_titles = ["Dish / Item Name", "Item ID", "Health", "Station", "Ingredients / Source", "Lore Notes"]
        for i, htitle in enumerate(hdr_titles):
            hdr_cells[i].width = col_widths[i]
            set_cell_background(hdr_cells[i], "7B1113")
            set_cell_margins(hdr_cells[i], top=120, bottom=120, left=100, right=100)
            hdr_p = hdr_cells[i].paragraphs[0]
            hdr_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            hdr_run = hdr_p.add_run(htitle)
            hdr_run.bold = True
            hdr_run.font.name = "Calibri"
            hdr_run.font.size = Pt(9.5)
            hdr_run.font.color.rgb = RGBColor(255, 255, 255)
        
        # Data Rows
        for r_idx, item_id in enumerate(items):
            row_cells = table.add_row().cells
            bg_color = "FAF6F0" if r_idx % 2 == 1 else "FFFFFF"
            
            data = ITEM_REGISTRY[item_id]
            name = data.get("name", item_id)
            heal_val = data.get("heal", 0)
            heal_str = f"+{heal_val} HP" if heal_val > 0 else "Base"
            desc_val = data.get("desc", "")
            
            rec = recipe_map.get(item_id)
            if rec:
                st_str = "Furnace" if rec.get("station") == "furnace" else "By Hand"
                req_list = [f"{cnt}x {ITEM_REGISTRY.get(iid, {}).get('name', iid)}" for iid, cnt in rec.get("ingredients", [])]
                ing_str = ", ".join(req_list)
            else:
                st_str = "Forage/Hunt"
                ing_str = ITEM_ACQUISITION.get(item_id, "Natural harvest")
            
            row_data = [name, item_id, heal_str, st_str, ing_str, desc_val]
            for c_i, val in enumerate(row_data):
                row_cells[c_i].width = col_widths[c_i]
                set_cell_background(row_cells[c_i], bg_color)
                set_cell_margins(row_cells[c_i], top=90, bottom=90, left=90, right=90)
                cell_p = row_cells[c_i].paragraphs[0]
                cell_p.paragraph_format.line_spacing = 1.05
                cell_p.paragraph_format.space_after = Pt(2)
                
                if c_i in (1, 2, 3):
                    cell_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
                else:
                    cell_p.alignment = WD_ALIGN_PARAGRAPH.LEFT
                
                run = cell_p.add_run(val)
                run.font.name = "Calibri"
                run.font.size = Pt(8.5)
                if c_i == 0:
                    run.bold = True
                    run.font.color.rgb = RGBColor(40, 40, 40)
                elif c_i == 1:
                    run.font.size = Pt(7.5)
                    run.font.color.rgb = RGBColor(100, 100, 100)
                elif c_i == 2 and heal_val > 0:
                    run.bold = True
                    run.font.color.rgb = RGBColor(34, 139, 34) # Green
                else:
                    run.font.color.rgb = RGBColor(50, 50, 50)
    
    # Save Word Doc
    docx_path = "Potaria_Cookbook.docx"
    doc.save(docx_path)
    print(f"Generated Word Document: {docx_path}")

# -------------------------------------------------------------
# REPORTLAB PDF BUILDER
# -------------------------------------------------------------
class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_page_decorations(self, total_pages):
        page_num = self._pageNumber
        self.saveState()
        
        # Header (Pages > 1)
        if page_num > 1:
            self.setFont("Helvetica-Bold", 8)
            self.setFillColor(colors.HexColor("#7B1113"))
            self.drawString(36, 755, "THE ROYAL POTARIA COOKBOOK")
            self.setFont("Helvetica-Oblique", 8)
            self.setFillColor(colors.HexColor("#777777"))
            self.drawRightString(612 - 36, 755, "Culinary Compendium & Hearth Guide")
            self.setStrokeColor(colors.HexColor("#D4AF37"))
            self.setLineWidth(0.5)
            self.line(36, 750, 612 - 36, 750)
            
        # Footer
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor("#777777"))
        self.drawRightString(612 - 36, 32, f"Page {page_num} of {total_pages}")
        self.drawString(36, 32, "Potaria Official Culinary Records")
        self.restoreState()

def draw_page_background(canvas_obj, doc_obj):
    canvas_obj.saveState()
    # Draw background tint BEFORE story elements
    canvas_obj.setFillColor(colors.HexColor("#FAF7F2"))
    canvas_obj.rect(0, 0, 612, 792, stroke=0, fill=1)
    
    # Decorative border
    canvas_obj.setStrokeColor(colors.HexColor("#D4AF37")) # Gold
    canvas_obj.setLineWidth(1.5)
    canvas_obj.rect(24, 24, 612 - 48, 792 - 48, stroke=1, fill=0)
    canvas_obj.setStrokeColor(colors.HexColor("#7B1113")) # Inner Burgundy
    canvas_obj.setLineWidth(0.5)
    canvas_obj.rect(27, 27, 612 - 54, 792 - 54, stroke=1, fill=0)
    canvas_obj.restoreState()

def build_pdf():
    pdf_path = "Potaria_Cookbook.pdf"
    
    # 36pt margins, page width 612pt -> printable width 540pt
    doc = SimpleDocTemplate(
        pdf_path,
        pagesize=letter,
        leftMargin=36,
        rightMargin=36,
        topMargin=46,
        bottomMargin=46
    )
    
    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=24,
        leading=28,
        textColor=colors.HexColor('#7B1113'),
        alignment=1, # Center
        spaceAfter=8
    )
    
    subtitle_style = ParagraphStyle(
        'DocSubTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Oblique',
        fontSize=12,
        leading=16,
        textColor=colors.HexColor('#8B5A2B'),
        alignment=1,
        spaceAfter=14
    )
    
    meta_style = ParagraphStyle(
        'DocMeta',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.5,
        leading=12,
        textColor=colors.HexColor('#666666'),
        alignment=1,
        spaceAfter=18
    )
    
    h1_style = ParagraphStyle(
        'SectionH1',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=13,
        leading=17,
        textColor=colors.HexColor('#7B1113'),
        spaceBefore=10,
        spaceAfter=6
    )
    
    body_style = ParagraphStyle(
        'SectionBody',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.5,
        leading=11.5,
        textColor=colors.HexColor('#2E2E2E'),
        spaceAfter=8
    )
    
    th_style = ParagraphStyle(
        'TableHeader',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8,
        leading=10,
        textColor=colors.white,
        alignment=1
    )
    
    td_name_style = ParagraphStyle(
        'TableDishName',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=7.5,
        leading=9.5,
        textColor=colors.HexColor('#1A1A1A')
    )
    
    td_id_style = ParagraphStyle(
        'TableDishID',
        parent=styles['Normal'],
        fontName='Courier',
        fontSize=6.5,
        leading=8.5,
        textColor=colors.HexColor('#666666'),
        alignment=1
    )
    
    td_heal_style = ParagraphStyle(
        'TableHeal',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=7.5,
        leading=9.5,
        textColor=colors.HexColor('#1E7E34'),
        alignment=1
    )
    
    td_st_style = ParagraphStyle(
        'TableStation',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=7.5,
        leading=9.5,
        textColor=colors.HexColor('#4A4A4A'),
        alignment=1
    )
    
    td_ing_style = ParagraphStyle(
        'TableIngredients',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=7,
        leading=9,
        textColor=colors.HexColor('#222222')
    )
    
    td_lore_style = ParagraphStyle(
        'TableLore',
        parent=styles['Normal'],
        fontName='Helvetica-Oblique',
        fontSize=6.5,
        leading=8.5,
        textColor=colors.HexColor('#444444')
    )
    
    story = []
    
    # Title & Front Matter
    story.append(Spacer(1, 15))
    story.append(Paragraph("THE ROYAL POTARIA COOKBOOK", title_style))
    story.append(Paragraph("A Comprehensive Culinary Compendium & Epicurean Guide to the Wilds of Potaria", subtitle_style))
    story.append(Paragraph("Authored by the Master Gastronomers of the Realm | Release 1.0.0", meta_style))
    story.append(HRFlowable(width="90%", thickness=1.5, color=colors.HexColor("#D4AF37"), spaceAfter=15, spaceBefore=0))
    
    story.append(Paragraph("Culinary Framework & Gastronomic Lore", h1_style))
    story.append(Paragraph(
        "Cooking in Potaria provides vital sustenance and tactical health sustainment for venturesome pioneers. "
        "Through centuries of culinary development, the denizens of Potaria mastered the fusion of indigenous root vegetables, "
        "abundant marine bounty, and farm-raised livestock. Recipes are processed through two traditional methods: "
        "<b>Furnace Cooking</b> (requiring heat and fuel to boil broths, fry cutlets, and caramelize sugars) and "
        "<b>By-Hand Assembly</b> (delicate cold preparations, iced sweets, curing fish in citrus, or rolling noodles).",
        body_style
    ))
    
    story.append(Spacer(1, 10))
    
    # 540 pt total width across 6 columns
    # 105 + 85 + 50 + 65 + 135 + 100 = 540 pt
    col_widths = [105, 85, 50, 65, 135, 100]
    
    for sec_idx, (title, items, desc_text) in enumerate(SECTIONS, start=1):
        if sec_idx > 1:
            story.append(PageBreak())
        
        story.append(Paragraph(f"Section {sec_idx}: {title}", h1_style))
        story.append(Paragraph(desc_text, body_style))
        story.append(Spacer(1, 4))
        
        table_data = []
        # Header
        table_data.append([
            Paragraph("Dish / Item Name", th_style),
            Paragraph("Item ID", th_style),
            Paragraph("Heal", th_style),
            Paragraph("Station", th_style),
            Paragraph("Recipe Ingredients / Source", th_style),
            Paragraph("Culinary Notes", th_style)
        ])
        
        for r_idx, item_id in enumerate(items):
            data = ITEM_REGISTRY[item_id]
            name = data.get("name", item_id)
            heal_val = data.get("heal", 0)
            heal_str = f"+{heal_val} HP" if heal_val > 0 else "Base"
            desc_val = data.get("desc", "")
            
            rec = recipe_map.get(item_id)
            if rec:
                st_str = "Furnace" if rec.get("station") == "furnace" else "By Hand"
                req_list = [f"{cnt}x {ITEM_REGISTRY.get(iid, {}).get('name', iid)}" for iid, cnt in rec.get("ingredients", [])]
                ing_str = ", ".join(req_list)
            else:
                st_str = "Forage/Hunt"
                ing_str = ITEM_ACQUISITION.get(item_id, "Natural harvest")
            
            p_name = Paragraph(name, td_name_style)
            p_id = Paragraph(item_id, td_id_style)
            p_heal = Paragraph(heal_str, td_heal_style)
            p_st = Paragraph(st_str, td_st_style)
            p_ing = Paragraph(ing_str, td_ing_style)
            p_lore = Paragraph(desc_val, td_lore_style)
            
            table_data.append([p_name, p_id, p_heal, p_st, p_ing, p_lore])
            
        t = Table(table_data, colWidths=col_widths, repeatRows=1)
        t.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#7B1113')),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#DECBB5')),
            ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#7B1113')),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F5EFEB')]),
            ('TOPPADDING', (0, 0), (-1, -1), 3.5),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 3.5),
            ('LEFTPADDING', (0, 0), (-1, -1), 4),
            ('RIGHTPADDING', (0, 0), (-1, -1), 4),
        ]))
        
        story.append(t)
        story.append(Spacer(1, 10))
        
    doc.build(story, onFirstPage=draw_page_background, onLaterPages=draw_page_background, canvasmaker=NumberedCanvas)
    print(f"Generated PDF Document: {pdf_path}")

if __name__ == "__main__":
    build_docx()
    build_pdf()
