from unittest import TestCase
from pdfmajor.fonts import standard14


class Standard14(TestCase):
    def test_loading_exists(self):
        # pdf spec 1.7 section 9.6.2.2
        standard_list = [
            "Helvetica",
            "Courier",
            "Symbol",
            "Times-Bold",
            "Helvetica-Bold",
            "Courier-Bold",
            "ZapfDingbats",
            "Times-Italic",
            "Helvetica-Oblique",
            "Courier-Oblique",
            "Times-BoldItalic",
            "Helvetica-BoldOblique",
            "Courier-BoldOblique",
        ]
        for fontname in standard_list:
            self.assertIsNotNone(standard14.get_ifexists(fontname))

    def test_invalid_name(self):
        self.assertIsNone(standard14.get_ifexists("Clowns!"))
