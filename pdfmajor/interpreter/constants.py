
from .PSStackParser import LIT

##  Constants
##
LITERAL_PDF = LIT("PDF")
LITERAL_TEXT = LIT("Text")
LITERAL_FONT = LIT("Font")
LITERAL_FORM = LIT("Form")
LITERAL_IMAGE = LIT("Image")

COMMON_FONT_ATTRIBUTES = [
    "Type",
    "FontName",
    "FontFamily",
    "FontStretch",
    "FontWeight",
    "Flags", 
    "FontBBox", 
    "ItalicAngle", 
    "Ascent", 
    "Descent", 
    "Leading",
    "CapHeight", 
    "XHeight",
    "StemV", 
    "StemH", 
    "AvgWidth",
    "MaxWidth",
    "MissingWidth",
    # "FontFile",
    # "FontFile2",
    # "FontFile3",
    "Charset",
]