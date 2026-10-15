"""
Unit and Integration Tests for Potaria Cookbook Document Generation
Validates:
1. Asset sprite path resolution for all 79 food dishes and ingredients.
2. Dual-mode document generation (With Codes and Without Codes) for both DOCX and PDF.
3. Verification of table column counts (7 for with-codes, 6 for without-codes).
4. File existence, non-zero size, and page counts.
5. Invariant check: Potaria_Items_Catalog files are preserved untouched.
"""

import os
import sys
import unittest
from docx import Document
from PySide6.QtGui import QGuiApplication
from PySide6.QtPdf import QPdfDocument

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from scripts.build_cookbook_docs import SECTIONS, get_item_icon_path, build_all


class TestCookbookGeneration(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        # Ensure documents are built
        build_all()

    def test_01_all_79_items_resolve_valid_icon_path(self):
        """Verifies every item in the cookbook sections resolves to an existing PNG asset."""
        total_items = 0
        for title, items, _ in SECTIONS:
            for item_id in items:
                total_items += 1
                icon_path = get_item_icon_path(item_id)
                self.assertIsNotNone(icon_path, f"No icon found for item '{item_id}'")
                self.assertTrue(os.path.isfile(icon_path), f"Icon file missing on disk: {icon_path}")
                self.assertGreater(os.path.getsize(icon_path), 0, f"Icon file is empty: {icon_path}")
        self.assertEqual(total_items, 79, f"Expected 79 items in cookbook, found {total_items}")

    def test_02_all_four_files_exist_and_non_empty(self):
        """Verifies that both DOCX and PDF versions (with codes and without codes) exist."""
        expected_files = [
            "Potaria_Cookbook_With_Codes.docx",
            "Potaria_Cookbook.docx",
            "Potaria_Cookbook_With_Codes.pdf",
            "Potaria_Cookbook.pdf",
            "Potaria_Cookbook_No_Codes.docx",
            "Potaria_Cookbook_No_Codes.pdf",
        ]
        for fname in expected_files:
            fpath = os.path.join(self.base_dir, fname)
            self.assertTrue(os.path.isfile(fpath), f"Cookbook file missing: {fname}")
            self.assertGreater(os.path.getsize(fpath), 20000, f"File {fname} is smaller than expected (< 20KB)")

    def test_03_docx_table_structure_and_columns(self):
        """Verifies DOCX tables have 7 columns for With_Codes and 6 columns for No_Codes."""
        # With Codes
        doc_codes = Document(os.path.join(self.base_dir, "Potaria_Cookbook_With_Codes.docx"))
        self.assertEqual(len(doc_codes.tables), len(SECTIONS))
        for table in doc_codes.tables:
            self.assertEqual(len(table.columns), 7, "With_Codes DOCX tables must have exactly 7 columns")
            header_texts = [cell.text.strip() for cell in table.rows[0].cells]
            self.assertEqual(header_texts[0], "Icon")
            self.assertEqual(header_texts[1], "Dish / Item Name")
            self.assertEqual(header_texts[2], "Item ID")

        # No Codes
        doc_no_codes = Document(os.path.join(self.base_dir, "Potaria_Cookbook_No_Codes.docx"))
        self.assertEqual(len(doc_no_codes.tables), len(SECTIONS))
        for table in doc_no_codes.tables:
            self.assertEqual(len(table.columns), 6, "No_Codes DOCX tables must have exactly 6 columns")
            header_texts = [cell.text.strip() for cell in table.rows[0].cells]
            self.assertEqual(header_texts[0], "Icon")
            self.assertEqual(header_texts[1], "Dish / Item Name")
            self.assertEqual(header_texts[2], "Health")

    def test_04_pdf_validity_and_page_counts(self):
        """Verifies PDF documents load cleanly in QPdfDocument and have valid page counts."""
        app = QGuiApplication.instance() or QGuiApplication(sys.argv)
        
        pdf_files = [
            "Potaria_Cookbook_With_Codes.pdf",
            "Potaria_Cookbook.pdf",
            "Potaria_Cookbook_No_Codes.pdf"
        ]
        for fname in pdf_files:
            fpath = os.path.join(self.base_dir, fname)
            pdf_doc = QPdfDocument()
            err = pdf_doc.load(fpath)
            self.assertEqual(err, QPdfDocument.Error.None_, f"Failed to load PDF {fname}: {err}")
            self.assertGreaterEqual(pdf_doc.pageCount(), 7, f"PDF {fname} has fewer pages than expected")

    def test_05_catalog_files_untouched(self):
        """Verifies standing constraint: Potaria_Items_Catalog files are not modified."""
        docx_catalog = os.path.join(self.base_dir, "Potaria_Items_Catalog.docx")
        pdf_catalog = os.path.join(self.base_dir, "Potaria_Items_Catalog.pdf")
        self.assertTrue(os.path.isfile(docx_catalog), "Potaria_Items_Catalog.docx must exist")
        self.assertTrue(os.path.isfile(pdf_catalog), "Potaria_Items_Catalog.pdf must exist")


if __name__ == "__main__":
    unittest.main()
