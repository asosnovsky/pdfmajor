from decimal import Decimal
import io
from pdfmajor.parser_v2.objects import PDFName
from pdfmajor.parser_v2 import PDFParser
from unittest import TestCase


class Basic(TestCase):
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
