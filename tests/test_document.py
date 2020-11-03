import warnings
from decimal import Decimal
from typing import List
from unittest import TestCase

from defusedxml.ElementTree import fromstring as xml_parse  # type: ignore

from pdfmajor.document import PDFDocument
from pdfmajor.document.catalog import PDFDocumentCatalog
from pdfmajor.document.exceptions import BrokenFilePDF, TooManyRectField
from pdfmajor.document.metadata import PDFMetadata
from pdfmajor.document.pages import PDFPageTreeNode
from pdfmajor.document.parse_context import PDFParsingContext
from pdfmajor.document.parsers.pages import iter_all_page_leafs
from pdfmajor.document.parsers.root import get_catalog, get_info
from pdfmajor.document.structures import PDFRectangle
from pdfmajor.pdf_parser.objects import (
    ObjectRef,
    PDFArray,
    PDFBoolean,
    PDFDictionary,
    PDFInteger,
    PDFName,
    PDFObject,
    PDFReal,
    PDFString,
)
from pdfmajor.pdf_parser.objects.primitives import PDFNull
from tests.util import all_corrupt_pdf_files, all_pdf_files


class ParsingState(TestCase):
    def run_test(self, file_name: str, expcat: PDFDocumentCatalog):
        with all_pdf_files[file_name].get_window() as buffer:
            pdf = PDFParsingContext(buffer)
            self.assertEqual(len(pdf.health_report), 0)
            cat = get_catalog(pdf)
            self.assertEqual(
                cat.version,
                expcat.version,
            )
            self.assertEqual(
                cat.pages,
                expcat.pages,
            )
            self.assertEqual(
                cat.page_labels,
                expcat.page_labels,
            )
            self.assertEqual(
                cat.page_layout,
                expcat.page_layout,
            )
            self.assertEqual(
                cat.page_mode,
                expcat.page_mode,
            )
            # TODO
            # self.assertEqual(
            #     cat.metadata,
            #     expcat.metadata,
            # )
            self.assertEqual(
                cat.raw,
                expcat.raw,
            )

    def test_pdf_spec(self):
        self.run_test(
            "PDF_spec.1.7.pdf",
            PDFDocumentCatalog(
                version=None,
                pages=PDFPageTreeNode(
                    kids=[
                        ObjectRef(20, 0),
                        ObjectRef(21, 0),
                        ObjectRef(22, 0),
                        ObjectRef(23, 0),
                        ObjectRef(24, 0),
                        ObjectRef(25, 0),
                        ObjectRef(26, 0),
                        ObjectRef(27, 0),
                    ],
                    parent=None,
                    leaft_count=756,
                    raw=PDFDictionary.from_dict(
                        {
                            "Count": PDFInteger(756, 0, 0),
                            "Kids": PDFArray.from_list(
                                [
                                    ObjectRef(20, 0),
                                    ObjectRef(21, 0),
                                    ObjectRef(22, 0),
                                    ObjectRef(23, 0),
                                    ObjectRef(24, 0),
                                    ObjectRef(25, 0),
                                    ObjectRef(26, 0),
                                    ObjectRef(27, 0),
                                ]
                            ),
                            "Type": PDFName("Pages", 0, 0),
                        }
                    ),
                ),
                page_labels=PDFDictionary.from_dict(
                    {
                        "Nums": PDFArray.from_list(
                            [
                                PDFInteger(0, 0, 0),
                                ObjectRef(18, 0),
                                PDFInteger(8, 0, 0),
                                ObjectRef(19, 0),
                            ]
                        )
                    }
                ),
                page_layout=None,
                page_mode=PDFName("UseOutlines", 0, 0),
                metadata=PDFMetadata(sub_type="XML", stream_data=b""),
                raw=PDFDictionary.from_dict(
                    {
                        "MarkInfo": PDFDictionary.from_dict(
                            {"Marked": PDFBoolean(True, 0, 0)}
                        ),
                        "Metadata": ObjectRef(2, 0),
                        "Names": ObjectRef(3, 0),
                        "OpenAction": PDFArray.from_list(
                            [
                                ObjectRef(4, 0),
                                PDFName("XYZ", 0, 0),
                                PDFNull(),
                                PDFNull(),
                                PDFNull(),
                            ]
                        ),
                        "Outlines": ObjectRef(5, 0),
                        "PageLabels": ObjectRef(6, 0),
                        "PageMode": PDFName("UseOutlines", 0, 0),
                        "Pages": ObjectRef(7, 0),
                        "StructTreeRoot": ObjectRef(8, 0),
                        "Type": PDFName("Catalog", 0, 0),
                    }
                ),
            ),
        )

    def test_bad_unicode(self):
        self.run_test(
            "bad-unicode.pdf",
            PDFDocumentCatalog(
                version=None,
                pages=PDFPageTreeNode.from_pdfdict(
                    PDFDictionary.from_dict(
                        {
                            "Count": PDFInteger(47, 0, 0),
                            "Type": PDFName("Pages", 0, 0),
                            "Kids": PDFArray.from_list(
                                [
                                    ObjectRef(142, 0),
                                    ObjectRef(143, 0),
                                    ObjectRef(144, 0),
                                    ObjectRef(145, 0),
                                    ObjectRef(146, 0),
                                ]
                            ),
                        }
                    )
                ),
                page_labels={"Nums": [PDFInteger(0, 0, 0), ObjectRef(140, 0)]},
                page_layout=None,
                page_mode=None,
                metadata=PDFMetadata(
                    "XML",
                    b"",
                ),
                raw=PDFDictionary.from_dict(
                    {
                        "Metadata": ObjectRef(147, 0),
                        "Pages": ObjectRef(141, 0),
                        "Type": PDFName("Catalog", 0, 0),
                        "PageLabels": ObjectRef(139, 0),
                    }
                ),
            ),
        )

    def test_bar_charts(self):
        self.run_test(
            "bar-charts.pdf",
            PDFDocumentCatalog(
                version=None,
                pages=PDFPageTreeNode.from_pdfdict(
                    PDFDictionary.from_dict(
                        {
                            "Count": PDFInteger(6, 0, 0),
                            "Type": PDFName("Pages", 0, 0),
                            "Kids": PDFArray(
                                [
                                    ObjectRef(3, 0),
                                    ObjectRef(9, 0),
                                    ObjectRef(13, 0),
                                    ObjectRef(36, 0),
                                    ObjectRef(66, 0),
                                    ObjectRef(188, 0),
                                ]
                            ),
                        }
                    )
                ),
                page_labels=None,
                page_layout=None,
                page_mode=None,
                metadata=PDFMetadata(
                    "XML",
                    b"",
                ),
                raw=PDFDictionary.from_dict(
                    {
                        "Type": PDFName("Catalog", 0, 0),
                        "Pages": ObjectRef(2, 0),
                        "Lang": PDFString(b"en-US", 0, 0),
                        "StructTreeRoot": ObjectRef(283, 0),
                        "MarkInfo": PDFDictionary.from_dict(
                            {"Marked": PDFBoolean(True, 0, 0)}
                        ),
                        "Metadata": ObjectRef(646, 0),
                        "ViewerPreferences": ObjectRef(647, 0),
                    }
                ),
            ),
        )

    def test_all(self):
        for file_path, buffer in all_pdf_files.items():
            if file_path != "PDF_spec.1.7.pdf":
                with self.subTest(file_path), buffer.get_window():
                    parser = PDFParsingContext(buffer)
                    catalog = get_catalog(parser)
                    self.assertEqual(len(parser.health_report), 0)
                    get_info(parser)
                    list(iter_all_page_leafs(parser, catalog.pages))
                    parser = PDFDocument(buffer)
                    actual_pages = len(list(parser.iter_pages()))
                    self.assertEqual(actual_pages, parser.num_pages)

    def test_metadata(self):
        with all_pdf_files["bad-unicode.pdf"].get_window() as buffer:
            parser = PDFDocument(buffer)
            self.assertIsNotNone(parser.catalog.metadata)
            xml_tree = xml_parse(parser.catalog.metadata.stream_data.decode("utf-8"))
            self.assertEqual(xml_tree[0][0][0].text, "Acrobat Distiller 7.0 (Windows)")
            self.assertEqual(xml_tree[0][1][0].text, "PScript5.dll Version 5.2.2")
            self.assertEqual(xml_tree[0][1][1].text, "2009-01-15T08:49:42-07:00")
            self.assertEqual(xml_tree[0][1][2].text, "2009-01-15T08:49:42-07:00")

    def test_warning_pagecount(self):
        with all_corrupt_pdf_files["bad-page-count.pdf"].get_window() as buffer:
            parser = PDFDocument(buffer)
            with warnings.catch_warnings(record=True) as w:
                actual_pages = len(list(parser.iter_pages()))
                self.assertEqual(len(w), 1)
            self.assertNotEqual(actual_pages, parser.num_pages)


class Structures(TestCase):
    def run_rect_test(self, arr_vals: List[PDFObject], exprect: PDFRectangle):
        self.assertEqual(
            PDFRectangle.from_pdfarray(PDFArray.from_list(arr_vals)),
            exprect,
        )

    def test_rect(self):
        self.run_rect_test(
            [
                PDFInteger(20, 0, 0),
                PDFInteger(10, 0, 0),
                PDFInteger(0, 0, 0),
                PDFInteger(3, 0, 0),
            ],
            PDFRectangle(Decimal(20), Decimal(10), Decimal(0), Decimal(3)),
        )
        self.run_rect_test(
            [
                PDFReal(Decimal("0.23"), 0, 0),
                PDFInteger(10, 0, 0),
                PDFInteger(Decimal("3.3"), 0, 0),
                PDFInteger(3, 0, 0),
            ],
            PDFRectangle(Decimal("0.23"), Decimal(10), Decimal("3.3"), Decimal(3)),
        )

    def test_rect_fail(self):
        with self.assertRaises(BrokenFilePDF):
            PDFRectangle.from_pdfarray(
                PDFArray.from_list(
                    [
                        PDFString("h0", 0, 0),
                        PDFString("h0", 0, 0),
                        PDFString("h0", 0, 0),
                        PDFString("h0", 0, 0),
                    ]
                )
            )

        with self.assertRaises(TooManyRectField):
            PDFRectangle.from_pdfarray(
                PDFArray.from_list(
                    [
                        PDFInteger(3, 0, 0),
                        PDFInteger(3, 0, 0),
                        PDFInteger(3, 0, 0),
                        PDFInteger(3, 0, 0),
                        PDFInteger(3, 0, 0),
                    ]
                )
            )
        with self.assertRaises(BrokenFilePDF):
            PDFRectangle.from_pdfarray(
                PDFArray.from_list(
                    [
                        PDFInteger(3, 0, 0),
                        PDFInteger(3, 0, 0),
                    ]
                )
            )


class Pages(TestCase):
    def test_bad_unicode_page(self):
        with all_pdf_files["bad-unicode.pdf"].get_window() as buffer:
            pdf = PDFDocument(buffer)
            page1 = next(pdf.iter_pages())
            print(page1)
