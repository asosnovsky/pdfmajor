from decimal import Decimal
import io
from typing import Callable, List
from pdfmajor.lexer.token import TokenInteger, TokenKeyword, TokenString
from pdfmajor.parser_v2.indirect_objects import IndirectObject, IndirectObjectCollection
from pdfmajor.parser_v2.l2 import PDFL2Parser
from pdfmajor.parser_v2.objects import PDFComment, PDFName, PDFObject, PDFPrimitive
from pdfmajor.parser_v2.l1 import PDFL1Parser
from pdfmajor.streambuffer import StreamEOF
from unittest import TestCase


class L1(TestCase):
    def test_parse_dict(self):
        parser = PDFL1Parser(
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
            )
        )
        obj = next(parser.iter_objects())
        self.assertDictEqual(
            obj,
            {
                PDFName("Type"): PDFName("Example"),
                PDFName("Subtype"): PDFName("DictionaryExample"),
                PDFName("Version"): Decimal("0.01"),
                PDFName("IntegerItem"): 12,
                PDFName("StringItem"): " a string ",
                PDFName("Subdictionary"): {
                    PDFName("Item1"): Decimal("0.4"),
                    PDFName("Item2"): True,
                    PDFName("LastItem"): "  not! ",
                    PDFName("VeryLastItem"): "  OK ",
                },
            },
        )

    def test_parse_array(self):
        parser = PDFL1Parser(
            io.BytesIO(br"""[ 549  3.14  false  (  Ralph )   /SomeName ]""")
        )
        obj = next(parser.iter_objects())
        self.assertListEqual(
            obj, [549, Decimal("3.14"), False, "  Ralph ", PDFName("SomeName")]
        )

    def test_parse_nested_array(self):
        parser = PDFL1Parser(
            io.BytesIO(
                br"""[ [10 30] [22 33] [
                << /x 0 /y 5 >>
                << /x 10 /y 5 >>
            ] ]"""
            )
        )
        obj = next(parser.iter_objects())
        self.assertListEqual(
            obj,
            [
                [10, 30],
                [22, 33],
                [
                    {PDFName("x"): 0, PDFName("y"): 5},
                    {PDFName("x"): 10, PDFName("y"): 5},
                ],
            ],
        )

    def test_parse_keeps_keywords(self):
        parser = PDFL1Parser(
            io.BytesIO(
                br"""
            12 1 obj (Bring) endobj
        """
            )
        )
        expected = [
            PDFPrimitive(TokenInteger(13, 15, 12)),
            PDFPrimitive(TokenInteger(16, 17, 1)),
            TokenKeyword(18, 21, b"obj"),
            PDFPrimitive(TokenString(22, 29, "Bring")),
            TokenKeyword(30, 36, b"endobj"),
        ]
        for obj, eobj in zip(parser.iter_objects(), expected):
            self.assertEqual(obj, eobj)
        with self.assertRaises(StreamEOF):
            next(parser.iter_objects())


class L2(TestCase):
    def run_test(
        self,
        raw: bytes,
        expected: Callable[[IndirectObjectCollection], List[PDFObject]],
    ):
        parser = PDFL2Parser(io.BytesIO(raw))
        for i, (eobj, obj) in enumerate(
            zip(expected(parser.inobjects), parser.iter_objects()), 1
        ):
            self.assertEqual(obj, eobj, f"Failed at example #{i}")
        try:
            next_obj = next(parser.iter_objects())
            self.assertIsNone(next_obj)
        except (EOFError, StopIteration) as e:
            self.assertIsNotNone(e)

    def test_parse_simple_indobj(self):
        parser = PDFL2Parser(
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
            )
        )
        expected = [
            (12, 1, "Bring"),
            (100, 0, b"3"),
            (13, 8, {PDFName("x"): 1, PDFName("y"): 3}),
        ]
        for obj, eobj in zip(parser.iter_objects(), expected):
            self.assertIsInstance(obj, IndirectObject)
            self.assertEqual(obj, parser.inobjects.get_indobject(eobj[0], eobj[1]))
            self.assertEqual(obj.to_python(), eobj[2])
        with self.assertRaises(StreamEOF):
            next(parser.iter_objects())

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
