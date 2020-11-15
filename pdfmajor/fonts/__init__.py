from pdfmajor.fonts.exceptions import InvalidFont
from typing import Any, Dict
from .base import PDFFont
from .type3 import PDFType3Font
from .simple_fonts import PDFSimpleFont
from .cidfont import PDFCIDFont
from .type0 import PDFType0Font
from . import standard14


def make_font(spec: Dict[str, Any]) -> PDFFont:
    subtype = str(spec["Subtype"])
    if subtype in ("Type1", "MMType1", "TrueType"):
        return PDFSimpleFont.from_dict(spec)
    elif subtype == "Type3":
        return PDFType3Font.from_dict(spec)
    elif subtype in ("CIDFontType0", "CIDFontType2"):
        return PDFCIDFont.from_dict(spec)
    elif subtype == "Type0":
        return PDFType0Font.from_dict(spec)
        # Type0 Font
        # dfonts = list_value(spec["DescendantFonts"])
        # assert dfonts
        # subspec = dict_value(dfonts[0]).copy()
        # for k in ("Encoding", "ToUnicode"):
        #     if k in spec:
        #         subspec[k] = resolve1(spec[k])
        # font = get_font(None, subspec, cached_fonts)
    else:
        raise InvalidFont(subtype)
