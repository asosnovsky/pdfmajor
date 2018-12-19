from typing import List
from pdfmajor.utils import MATRIX_IDENTITY

from .PDFGraphicState import PDFGraphicState
from .PDFGraphicState.PDFColor import PDFColor
from .PDFGraphicState.PDFColorSpace import PREDEFINED_COLORSPACE, OrderedDict, PDFColorSpace

from .PDFTextState import PDFTextState

from .Curves import CurvePath
from .PDFItem import PDFItem, PDFImage, PDFShape, PDFXObject, PDFText

class PDFStateStack:
    def __init__(self):
        self.t_matrix = MATRIX_IDENTITY
        self.text = PDFTextState()
        self.graphics = PDFGraphicState()
        self.graphicstack : List[PDFGraphicState] = []
        self.curvestacks: List[CurvePath] = []
        self.argstack: List[bytes] = []
        self.complete_items : List[PDFItem] = []
        self.colorspace_map: OrderedDict = PREDEFINED_COLORSPACE.copy()
        self.fontmap = {}
        self.xobjmap = {}
        self.resources = {}

    def pop(self, n: int) -> bytearray:
        if n == 0:
            return []
        x = self.argstack[-n:]
        self.argstack = self.argstack[:-n]
        return x