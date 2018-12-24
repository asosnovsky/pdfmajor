from typing import List
from pdfmajor.utils import MATRIX_IDENTITY

from .PDFGraphicState import PDFGraphicState
from .PDFGraphicState.PDFColor import PDFColor
from .PDFGraphicState.PDFColorSpace import PREDEFINED_COLORSPACE, OrderedDict, PDFColorSpace

from .PDFTextState import PDFTextState, PDFFont, get_font

from .Curves import CurvePath

from .layout import LTItem, LTComponent, LTContainer
from .layout import LTTextBlock, LTCharBlock, LTChar
from .layout import LTCurve, LTLine, LTHorizontalLine, LTVerticalLine, LTRect
from .layout import LTXObject
from .layout import LTImage

from .layout import make_char_block, make_curve, make_image, make_xobject

class PDFStateStack:
    def __init__(self):
        self.t_matrix = MATRIX_IDENTITY
        self.text = PDFTextState()
        self.graphics = PDFGraphicState()
        self.gstack : list = []
        self.curvestacks: List[CurvePath] = []
        self.argstack: List[bytes] = []
        self.complete_layout_items : List[LTItem] = []
        self.colorspace_map: OrderedDict = PREDEFINED_COLORSPACE.copy()
        self.fontmap = {}
        self.xobjmap = {}
        self.resources = {}
        self.current_textblock: LTTextBlock = None

    def pop(self, n: int) -> bytearray:
        if n == 0:
            return []
        x = self.argstack[-n:]
        self.argstack = self.argstack[:-n]
        return x