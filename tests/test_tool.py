from tools.afmparser import CharMetric, ParsedFile, SplitFile, split_file
from unittest import TestCase
from tests.util import CURRENT_FOLDER


class Builders(TestCase):
    def test_char_parser(self):
        self.assertEqual(
            CharMetric(40, 600),
            CharMetric.from_line("C 40 ; WX 600 ; N parenleft ; B 219 -102 461 616 ;"),
        )

    def test_splitter(self):
        self.assertEqual(
            split_file(
                """StartFontMetrics 4.1
Descender -157
StdHW 84
StdVW 106
StartCharMetrics 315
C 32 ; WX 600 ; N space ; B 0 0 0 0 ;
C 33 ; WX 600 ; N exclam ; B 202 -15 398 572 ;
EndCharMetrics
EndFontMetrics
""",
            ),
            SplitFile(
                metrics_raw="""C 32 ; WX 600 ; N space ; B 0 0 0 0 ;
C 33 ; WX 600 ; N exclam ; B 202 -15 398 572 ;""",
                descriptor_raw="""StartFontMetrics 4.1
Descender -157
StdHW 84
StdVW 106""",
            ),
        )

    def test_parse_data(self):
        parsed_f = ParsedFile.from_data(
            """
        StartFontMetrics 4.1
Descender -157
StdHW 84
StdVW 106
FontBBox 100 20 10 400
IsFixedPitch true
FalseyThing false
StartCharMetrics 315
C 32 ; WX 600 ; N space ; B 0 0 0 0 ;
C 33 ; WX 600 ; N exclam ; B 202 -15 398 572 ;
EndCharMetrics
EndFontMetrics
"""
        )
        self.assertEqual(
            parsed_f,
            ParsedFile(
                descriptor={
                    "StartFontMetrics": 4.1,
                    "Descender": -157,
                    "StdHW": 84,
                    "StdVW": 106,
                    "FontBBox": [100, 20, 10, 400],
                    "IsFixedPitch": True,
                    "FalseyThing": False,
                },
                metrics=[
                    CharMetric(char_code=32, width=600),
                    CharMetric(char_code=33, width=600),
                ],
            ),
        )

    def test_parse_file(self):
        path_to_file = CURRENT_FOLDER.parent / "vendor/core14/Courier.afm"
        parsed_f = ParsedFile.from_file_path(path_to_file)
        self.assertDictEqual(
            parsed_f.descriptor,
            {
                "StartFontMetrics": 4.1,
                "Comment": "VMusage 39754 50779",
                "FontName": "Courier",
                "FullName": "Courier",
                "FamilyName": "Courier",
                "Weight": "Medium",
                "ItalicAngle": 0,
                "IsFixedPitch": True,
                "CharacterSet": "ExtendedRoman",
                "FontBBox": [-23, -250, 715, 805],
                "UnderlinePosition": -100,
                "UnderlineThickness": 50,
                "Version": 3.0,
                "Notice": "Copyright (c) 1989, 1990, 1991, 1992, 1993, 1997 Adobe Systems Incorporated.  All Rights Reserved.",
                "EncodingScheme": "AdobeStandardEncoding",
                "CapHeight": 562,
                "XHeight": 426,
                "Ascender": 629,
                "Descender": -157,
                "StdHW": 51,
                "StdVW": 51,
            },
        )
        for charm in parsed_f.metrics:
            self.assertEqual(charm.width, 600)
