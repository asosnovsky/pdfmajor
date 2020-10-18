from decimal import Decimal
import io
from pdfmajor.parser_v2.objects import PDFName
from pdfmajor.parser_v2.l1 import PDFL1Parser
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
