import io

from typing import Callable, List
from decimal import Decimal
from unittest import TestCase

from pdfmajor.streambuffer import StreamEOF
from pdfmajor.parser.objects.indirect import IndirectObject, IndirectObjectCollection
from pdfmajor.parser.objects.base import PDFObject
from pdfmajor.parser.objects.comment import PDFComment
from pdfmajor.parser.objects.stream import PDFStream
from pdfmajor.parser import PDFParser


class Collections(TestCase):
    def test_parse_dict(self):
        parser = PDFParser(
            io.BytesIO(
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
                            >>"""
            ),
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
        parser = PDFParser(
            io.BytesIO(br"""[ 549  3.14  false  (  Ralph )   /SomeName ]"""),
            strict=True,
        )
        obj = next(parser.iter_objects())
        self.assertListEqual(
            obj.to_python(),
            [549, Decimal("3.14"), False, "  Ralph ", "/SomeName"],
        )

    def test_parse_nested_array(self):
        parser = PDFParser(
            io.BytesIO(
                br"""[ [10 30] [22 33] [
                << /x 0 /y 5 >>
                << /x 10 /y 5 >>
            ] ]"""
            ),
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
        parser = PDFParser(
            io.BytesIO(
                br"""
            12 1 obj (Bring) endobj
            100 0 obj
            <33>
            endobj
            13 8
            obj
            << /x 1 /y 3>> endobj
            """
            ),
            strict=True,
        )
        expected = [
            (12, 1, "Bring"),
            (100, 0, b"3"),
            (13, 8, {"x": 1, "y": 3}),
        ]
        for obj, eobj in zip(parser.iter_objects(), expected):
            self.assertIsInstance(obj, IndirectObject)
            self.assertEqual(
                obj,
                parser.state.indirect_object_collection.get_indobject(eobj[0], eobj[1]),
            )
            self.assertEqual(obj.to_python(), eobj[2])
        with self.assertRaises(StreamEOF):
            next(parser.iter_objects())

    def test_parse_obj_with_references(self):
        parser = PDFParser(
            io.BytesIO(
                br"""
            12 1 obj (Bring) endobj
            10 2 obj << /lastone 12 1 R >> endobj

            """
            ),
            strict=True,
        )
        expected = [
            parser.state.indirect_object_collection.get_indobject(12, 1),
            parser.state.indirect_object_collection.get_indobject(10, 2),
        ]
        for obj, exp in zip(parser.iter_objects(), expected):
            self.assertEqual(obj, exp)
        with self.assertRaises(StreamEOF):
            next(parser.iter_objects())
        sec_obj = parser.state.indirect_object_collection.get_indobject(
            10, 2
        ).get_object()
        self.assertEqual(
            sec_obj.to_python(),
            {"lastone": "Bring"},
        )

    def run_test(
        self,
        raw: bytes,
        expected: Callable[[IndirectObjectCollection], List[PDFObject]],
    ):
        parser = PDFParser(io.BytesIO(raw), strict=True)
        for i, (eobj, obj) in enumerate(
            zip(
                expected(parser.state.indirect_object_collection), parser.iter_objects()
            ),
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
            expected=lambda indobjc: [
                PDFComment(b" object references", (22, 41)),
                PDFComment(b" start of object", (62, 79)),
                PDFComment(b" object content", (110, 126)),
                indobjc.get_indobject(10, 0),
                PDFComment(b"closing the object", (150, 169)),
                indobjc.get_indobject(11, 1),
            ],
        )

    def test_parse_stream(self):
        parser = PDFParser(
            io.BytesIO(
                br"""
            5 0 obj
<< /Type /XRef /Length 124 /Filter /FlateDecode >>
stream
"<99><A3><C1>l01234567890l01234567890l01234567890l01234567890l01234567890l01234567890l01234567890l01234567890l01234567
<80>endstream
endobj
        """
            )
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
