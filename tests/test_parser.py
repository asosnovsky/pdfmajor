from pathlib import Path
from pdfmajor.parser.objects.collections import PDFDictionary
from pdfmajor.parser.objects.primitives import PDFHexString, PDFInteger, PDFString

from typing import List
from decimal import Decimal
from unittest import TestCase

from pdfmajor.streambuffer import StreamEOF
from pdfmajor.parser.objects.indirect import IndirectObject
from pdfmajor.parser.objects.base import PDFObject
from pdfmajor.parser.objects.comment import PDFComment
from pdfmajor.parser.objects.stream import PDFStream
from pdfmajor.parser.PDFParser import PDFParser

CURRENT_FOLDER = Path(__file__).parent


class Collections(TestCase):
    def test_parse_dict(self):
        parser = PDFParser.from_bytes(
            br"""<<  /Type      /Example
                         /Subtype   /DictionaryExample      
                         /Version   0.01
                         /IntegerItem  12      
                         /StringItem  ( a string )      
                         /Subdictionary  <<  
                            /Item1  0.4      
                            /Item2  true      
                            /LastItem  (  not! )      
                            /VeryLastItem  (  OK ) >>
                            >>""",
            strict=True,
        )
        obj = next(parser.iter_objects())
        self.assertDictEqual(
            obj.to_python(),
            {
                "Type": "/Example",
                "Subtype": "/DictionaryExample",
                "Version": Decimal("0.01"),
                "IntegerItem": 12,
                "StringItem": " a string ",
                "Subdictionary": {
                    "Item1": Decimal("0.4"),
                    "Item2": True,
                    "LastItem": "  not! ",
                    "VeryLastItem": "  OK ",
                },
            },
        )

    def test_parse_array(self):
        parser = PDFParser.from_bytes(
            br"""[ 549  3.14  false  (  Ralph )   /SomeName ]""",
            strict=True,
        )
        obj = next(parser.iter_objects())
        self.assertListEqual(
            obj.to_python(),
            [549, Decimal("3.14"), False, "  Ralph ", "/SomeName"],
        )

    def test_parse_nested_array(self):
        parser = PDFParser.from_bytes(
            br"""[ [10 30] [22 33] [
                << /x 0 /y 5 >>
                << /x 10 /y 5 >>
            ] ]""",
            strict=True,
        )
        obj = next(parser.iter_objects())
        self.assertListEqual(
            obj.to_python(),
            [
                [10, 30],
                [22, 33],
                [
                    {"x": 0, "y": 5},
                    {"x": 10, "y": 5},
                ],
            ],
        )


class IndirectObjects(TestCase):
    def test_parse_simple_indobj(self):
        parser = PDFParser.from_bytes(
            br"""
            12 1 obj (Bring) endobj
            100 0 obj
            <33>
            endobj
            13 8
            obj
            << /x 1 /y 3>> endobj
            """,
            strict=True,
        )
        expected = [
            IndirectObject(12, 1, 18, PDFString("Bring", 0, 0)),
            IndirectObject(100, 0, 25, PDFHexString(b"3", 0, 0)),
            IndirectObject(
                13,
                8,
                144,
                PDFDictionary.from_dict(
                    {"x": PDFInteger(1, 0, 0), "y": PDFInteger(3, 0, 0)}
                ),
            ),
        ]
        for obj, eobj in zip(parser.iter_objects(), expected):
            self.assertIsInstance(obj, IndirectObject)
            self.assertEqual(obj, eobj)
        with self.assertRaises(StreamEOF):
            next(parser.iter_objects())

    def test_parse_obj_with_references(self):
        parser = PDFParser.from_bytes(
            br"""
            12 1 obj (Bring) endobj
            10 2 obj << /lastone 12 1 R >> endobj

            """,
            strict=True,
        )
        expected = [
            "Bring",
            {"lastone": "Bring"},
        ]
        for obj, exp in zip(parser.iter_objects(), expected):
            self.assertEqual(obj.to_python(), exp)
        with self.assertRaises(StreamEOF):
            next(parser.iter_objects())
        sec_obj = parser.db.get_object(10, 2)
        self.assertEqual(
            sec_obj.to_python(),
            {"lastone": "Bring"},
        )

    def run_test(
        self,
        raw: bytes,
        expected: List[PDFObject],
    ):
        parser = PDFParser.from_bytes(raw, strict=True)
        for i, (eobj, obj) in enumerate(
            zip(expected, parser.iter_objects()),
            1,
        ):
            self.assertEqual(obj, eobj, f"Failed at example #{i}")
        try:
            next_obj = next(parser.iter_objects())
            self.assertIsNone(next_obj)
        except (EOFError, StopIteration) as e:
            self.assertIsNotNone(e)

    def test_parse_comments(self):
        self.run_test(
            br"""
                10 0 % object references
                obj % start of object
                    (testing) % object content
                endobj %closing the object
                11 1 obj 2 endobj
            """,
            expected=[
                PDFComment(b" object references", (22, 41)),
                PDFComment(b" start of object", (62, 79)),
                PDFComment(b" object content", (110, 126)),
                IndirectObject(10, 0, 58, PDFString("testing", 0, 0)),
                PDFComment(b"closing the object", (150, 169)),
                IndirectObject(11, 1, 191, PDFInteger(2, 0, 0)),
            ],
        )

    def test_parse_stream(self):
        parser = PDFParser.from_bytes(
            br"""
            5 0 obj
<< /Type /XRef /Length 124 /Filter /FlateDecode >>
stream
"<99><A3><C1>l01234567890l01234567890l01234567890l01234567890l01234567890l01234567890l01234567890l01234567890l01234567
<80>endstream
endobj
        """
        )
        for obj in parser.iter_objects():
            self.assertIsInstance(obj, IndirectObject)
            self.assertIsInstance(obj.get_object(), PDFStream)
            self.assertDictEqual(
                obj.get_object().to_python(),
                {
                    "offset": 78,
                    "length": 0,
                    "filter": None,
                    "decode_parms": None,
                    "f": None,
                    "ffilter": None,
                    "fdecode_parms": None,
                    "dl": None,
                },
            )


# class PDFStreamParsing(TestCase):
#     def test_simple(self):
#         with (CURRENT_FOLDER / "samples" / "pdf" / "chars.pdf").open("br") as fp:
#             parser = PDFParser(fp)
#             for obj in parser.iter_objects():
#                 print(obj)
