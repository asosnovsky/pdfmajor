from pathlib import Path
from pdfmajor.xref.xrefdb import XRefDB
from unittest import TestCase

from pdfmajor.streambuffer import BufferStream
from pdfmajor.xref.xref import XRefRow, iter_over_xref

CURRENT_FOLDER = Path(__file__).parent


class Standard(TestCase):
    def test_char_doc(self):
        expected_xrefs = {
            (1, 0): XRefRow(offset=27259, obj_num=1, gen_num=0, use=b"n"),
            (2, 0): XRefRow(offset=19, obj_num=2, gen_num=0, use=b"n"),
            (3, 0): XRefRow(offset=344, obj_num=3, gen_num=0, use=b"n"),
            (4, 0): XRefRow(offset=27402, obj_num=4, gen_num=0, use=b"n"),
            (5, 0): XRefRow(offset=364, obj_num=5, gen_num=0, use=b"n"),
            (6, 0): XRefRow(offset=714, obj_num=6, gen_num=0, use=b"n"),
            (7, 0): XRefRow(offset=27545, obj_num=7, gen_num=0, use=b"n"),
            (8, 0): XRefRow(offset=734, obj_num=8, gen_num=0, use=b"n"),
            (9, 0): XRefRow(offset=5949, obj_num=9, gen_num=0, use=b"n"),
            (10, 0): XRefRow(offset=5970, obj_num=10, gen_num=0, use=b"n"),
            (11, 0): XRefRow(offset=6176, obj_num=11, gen_num=0, use=b"n"),
            (12, 0): XRefRow(offset=6503, obj_num=12, gen_num=0, use=b"n"),
            (13, 0): XRefRow(offset=6700, obj_num=13, gen_num=0, use=b"n"),
            (14, 0): XRefRow(offset=11679, obj_num=14, gen_num=0, use=b"n"),
            (15, 0): XRefRow(offset=11701, obj_num=15, gen_num=0, use=b"n"),
            (16, 0): XRefRow(offset=11905, obj_num=16, gen_num=0, use=b"n"),
            (17, 0): XRefRow(offset=12232, obj_num=17, gen_num=0, use=b"n"),
            (18, 0): XRefRow(offset=12427, obj_num=18, gen_num=0, use=b"n"),
            (19, 0): XRefRow(offset=17804, obj_num=19, gen_num=0, use=b"n"),
            (20, 0): XRefRow(offset=17826, obj_num=20, gen_num=0, use=b"n"),
            (21, 0): XRefRow(offset=18037, obj_num=21, gen_num=0, use=b"n"),
            (22, 0): XRefRow(offset=18364, obj_num=22, gen_num=0, use=b"n"),
            (23, 0): XRefRow(offset=18565, obj_num=23, gen_num=0, use=b"n"),
            (24, 0): XRefRow(offset=26258, obj_num=24, gen_num=0, use=b"n"),
            (25, 0): XRefRow(offset=26280, obj_num=25, gen_num=0, use=b"n"),
            (26, 0): XRefRow(offset=26477, obj_num=26, gen_num=0, use=b"n"),
            (27, 0): XRefRow(offset=26882, obj_num=27, gen_num=0, use=b"n"),
            (28, 0): XRefRow(offset=27141, obj_num=28, gen_num=0, use=b"n"),
            (29, 0): XRefRow(offset=27204, obj_num=29, gen_num=0, use=b"n"),
            (30, 0): XRefRow(offset=27650, obj_num=30, gen_num=0, use=b"n"),
            (31, 0): XRefRow(offset=27747, obj_num=31, gen_num=0, use=b"n"),
        }
        expected_types = {
            (1, 0): "/Page",
            (2, 0): "{{PDFUnknownComplexType}}",
            (3, 0): "{{PDFPrimitive}}",
            (4, 0): "/Page",
            (5, 0): "{{PDFUnknownComplexType}}",
            (6, 0): "{{PDFPrimitive}}",
            (7, 0): "/Pages",
            (8, 0): "{{PDFUnknownComplexType}}",
            (9, 0): "{{PDFPrimitive}}",
            (10, 0): "/FontDescriptor",
            (11, 0): "{{PDFUnknownComplexType}}",
            (12, 0): "/Font",
            (13, 0): "{{PDFUnknownComplexType}}",
            (14, 0): "{{PDFPrimitive}}",
            (15, 0): "/FontDescriptor",
            (16, 0): "{{PDFUnknownComplexType}}",
            (17, 0): "/Font",
            (18, 0): "{{PDFUnknownComplexType}}",
            (19, 0): "{{PDFPrimitive}}",
            (20, 0): "/FontDescriptor",
            (21, 0): "{{PDFUnknownComplexType}}",
            (22, 0): "/Font",
            (23, 0): "{{PDFUnknownComplexType}}",
            (24, 0): "{{PDFPrimitive}}",
            (25, 0): "/FontDescriptor",
            (26, 0): "{{PDFUnknownComplexType}}",
            (27, 0): "/Font",
            (28, 0): "{{PDFUnknownComplexType}}",
            (29, 0): "{{PDFUnknownComplexType}}",
            (30, 0): "/Catalog",
            (31, 0): "{{PDFUnknownComplexType}}",
        }
        with (CURRENT_FOLDER / "samples" / "pdf" / "chars.pdf").open("rb") as fp:
            buffer = BufferStream(fp)
            db = XRefDB(buffer)
            self.assertDictEqual(
                db.xrefs,
                expected_xrefs,
            )
            self.assertDictEqual(
                {
                    raw_ref: db.get_type_for(*raw_ref, buffer)
                    for raw_ref in db.xrefs.keys()
                },
                expected_types,
            )
