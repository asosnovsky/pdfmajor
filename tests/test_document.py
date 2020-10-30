from pathlib import Path
from unittest import TestCase

from pdfmajor.document.catalog import PDFDocumentCatalog
from pdfmajor.document.PDFParsingContext import PDFParsingContext
from pdfmajor.parser.objects.indirect import ObjectRef
from pdfmajor.parser.objects.primitives import (
    PDFBoolean,
    PDFInteger,
    PDFName,
    PDFString,
)

from tests.util import all_pdf_files


class Catalog(TestCase):
    def run_test(self, file_name: str, expcat: PDFDocumentCatalog):
        with all_pdf_files[file_name].get_window() as buffer:
            pdf = PDFParsingContext(buffer)
            self.assertEqual(
                pdf.get_catalog(),
                expcat,
            )

    def test_bad_unicode(self):
        self.run_test(
            "bad-unicode.pdf",
            PDFDocumentCatalog(
                version=None,
                pages=[ObjectRef(141, 0)],
                page_labels={"Nums": [PDFInteger(0, 0, 0), ObjectRef(140, 0)]},
                page_layout=None,
                page_mode=None,
                metadata={
                    "Subtype": PDFName("XML", 0, 0),
                    "Length": PDFInteger(3529, 0, 0),
                    "Type": PDFName("Metadata", 0, 0),
                },
                raw={
                    "Metadata": ObjectRef(147, 0),
                    "Pages": ObjectRef(141, 0),
                    "Type": PDFName("Catalog", 0, 0),
                    "PageLabels": ObjectRef(139, 0),
                },
            ),
        )

    def test_bar_charts(self):
        self.run_test(
            "bar-charts.pdf",
            PDFDocumentCatalog(
                version=None,
                pages=[ObjectRef(2, 0)],
                page_labels=None,
                page_layout=None,
                page_mode=None,
                metadata={
                    "Type": PDFName("Metadata", 0, 0),
                    "Subtype": PDFName("XML", 0, 0),
                    "Length": PDFInteger(3065, 0, 0),
                },
                raw={
                    "Type": PDFName("Catalog", 0, 0),
                    "Pages": ObjectRef(2, 0),
                    "Lang": PDFString(b"en-US", 0, 0),
                    "StructTreeRoot": ObjectRef(283, 0),
                    "MarkInfo": {"Marked": PDFBoolean(True, 0, 0)},
                    "Metadata": ObjectRef(646, 0),
                    "ViewerPreferences": ObjectRef(647, 0),
                },
            ),
        )

    def test_all(self):
        for file_path, buffer in all_pdf_files.items():
            with self.subTest(file_path):
                parser = PDFParsingContext(buffer)
                parser.get_catalog()
                self.assertEqual(len(parser.health_report), 0)
