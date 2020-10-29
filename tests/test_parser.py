from pathlib import Path
from pdfmajor.parser import iter_objects
from pdfmajor.parser.objects.collections import PDFDictionary
from pdfmajor.parser.objects.primitives import PDFHexString, PDFInteger, PDFString

from typing import Any, Callable, List, Optional
from decimal import Decimal
from unittest import TestCase

from pdfmajor.streambuffer import BufferStream
from pdfmajor.parser.objects.indirect import IndirectObject, ObjectRef
from pdfmajor.parser.objects.base import PDFObject
from pdfmajor.parser.objects.comment import PDFComment
from pdfmajor.parser.stream.PDFStream import PDFStream

CURRENT_FOLDER = Path(__file__).parent


class Collections(TestCase):
    def run_test(self, raw: bytes, expected: Any):
        size = len(raw)
        for buf_size in [
            2,
            3,
            size // 4,
            size // 3,
            size // 2,
            3 * size // 4,
            size,
            2 * size,
            4 * size,
        ]:
            buffer = BufferStream.from_bytes(raw, buffer_size=buf_size)
            it = iter_objects(buffer)
            obj = next(it)
            self.assertEqual(obj.to_python(), expected)
            with self.assertRaises(StopIteration):
                next(it)

    def test_parse_dict(self):
        self.run_test(
            raw=br"""<<  /Type      /Example
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
            expected={
                "Type": "/Example",
                "Subtype": "/DictionaryExample",
                "Version": Decimal("0.01"),
                "IntegerItem": 12,
                "StringItem": b" a string ",
                "Subdictionary": {
                    "Item1": Decimal("0.4"),
                    "Item2": True,
                    "LastItem": b"  not! ",
                    "VeryLastItem": b"  OK ",
                },
            },
        )

    def test_parse_array(self):
        self.run_test(
            raw=br"""[ 549  3.14  false  (  Ralph )   /SomeName ]""",
            expected=[549, Decimal("3.14"), False, b"  Ralph ", "/SomeName"],
        )

    def test_parse_nested_array(self):
        self.run_test(
            raw=br"""[ [10 30] [22 33] [
                << /x 0 /y 5 >>
                << /x 10 /y 5 >>
            ] ]""",
            expected=[
                [10, 30],
                [22, 33],
                [
                    {"x": 0, "y": 5},
                    {"x": 10, "y": 5},
                ],
            ],
        )


class IndirectObjects(TestCase):
    def run_test(
        self,
        raw: bytes,
        expected: List[PDFObject],
    ):
        size = len(raw)
        for buf_size in [
            2,
            3,
            size // 4,
            size // 3,
            size // 2,
            3 * size // 4,
            size,
            2 * size,
            4 * size,
        ]:
            buffer = BufferStream.from_bytes(raw, buffer_size=buf_size)
            it = iter_objects(buffer)
            for obj, eobj in zip(it, expected):
                self.assertEqual(
                    obj,
                    eobj,
                    f"objects do not match\n incoming={obj}\n expected={eobj}",
                )
            with self.assertRaises((StopIteration, EOFError)):
                next(it)

    def test_parse_simple_indobj(self):
        self.run_test(
            raw=br"""
            12 1 obj (Bring) endobj
            100 0 obj
            <33>
            endobj
            13 8
            obj
            << /x 1 /y 3>> endobj
            """,
            expected=[
                IndirectObject(12, 1, 18, PDFString(b"Bring", 0, 0)),
                IndirectObject(100, 0, 55, PDFHexString(b"3", 0, 0)),
                IndirectObject(
                    13,
                    8,
                    124,
                    PDFDictionary.from_dict(
                        {"x": PDFInteger(1, 0, 0), "y": PDFInteger(3, 0, 0)}
                    ),
                ),
            ],
        )

    def test_parse_obj_with_references(self):
        self.run_test(
            raw=br"""
            12 1 obj (Bring) endobj
            10 2 obj << /lastone 12 1 R >> endobj

            """,
            expected=[
                IndirectObject(12, 1, 18, PDFString(b"Bring", 0, 0)),
                IndirectObject(
                    10,
                    2,
                    54,
                    data=PDFDictionary.from_dict({"lastone": ObjectRef(12, 1)}),
                ),
            ],
        )

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
                IndirectObject(10, 0, 58, PDFString(b"testing", 0, 0)),
                PDFComment(b"closing the object", (150, 169)),
                IndirectObject(11, 1, 191, PDFInteger(2, 0, 0)),
            ],
        )

    def test_parse_stream(self):
        buffer = BufferStream.from_bytes(
            br"""
            5 0 obj
<< /Type /XRef /Length 123 /Filter /FlateDecode /otherfeature [10 20]>>
stream
"<99><A3><C1>l01234567890l01234567890l01234567890l01234567890l01234567890l01234567890l01234567890l01234567890l01234567
<80>endstream
endobj
        """
        )
        for obj in iter_objects(buffer):
            self.assertIsInstance(obj, IndirectObject)
            self.assertIsInstance(obj.get_object(), PDFDictionary)
            self.assertIsInstance(obj.stream, PDFStream)  # type: ignore
            self.assertDictEqual(
                obj.stream.to_python(),  # type: ignore
                {
                    "offset": 100,
                    "length": 123,
                    "filter": ["/FlateDecode"],
                    "decode_parms": [],
                    "f": None,
                    "ffilter": [],
                    "fdecode_parms": [],
                    "dl": None,
                },
            )
            self.assertDictEqual(
                obj.get_object().to_python(),
                {
                    "Filter": "/FlateDecode",
                    "Length": 123,
                    "Type": "/XRef",
                    "otherfeature": [10, 20],
                },
            )

    def test_parse_bad_len_stream(self):
        buffer = BufferStream.from_bytes(
            br"""
            5 0 obj
<< /Type /XRef /Length 123 /Filter /FlateDecode /otherfeature [10 20]>>
stream
"<99><A3><C1>l01234567890l01234567890l01234567890l01234567890l01234567890l01234567890l01234567890l01234567890l01234567
<80>]]]]]endstream
endobj
        """
        )
        for obj in iter_objects(buffer):
            self.assertIsInstance(obj, IndirectObject)
            self.assertIsInstance(obj.get_object(), PDFDictionary)
            self.assertIsInstance(obj.stream, PDFStream)  # type: ignore
            self.assertDictEqual(
                obj.stream.to_python(),  # type: ignore
                {
                    "offset": 100,
                    "length": 123 + 5,
                    "filter": ["/FlateDecode"],
                    "decode_parms": [],
                    "f": None,
                    "ffilter": [],
                    "fdecode_parms": [],
                    "dl": None,
                },
            )
            self.assertDictEqual(
                obj.get_object().to_python(),
                {
                    "Filter": "/FlateDecode",
                    "Length": 123 + 5,
                    "Type": "/XRef",
                    "otherfeature": [10, 20],
                },
            )
