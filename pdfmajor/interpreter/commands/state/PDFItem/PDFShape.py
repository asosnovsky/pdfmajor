from typing import List

from ..PDFGraphicState import PDFGraphicState, PDFColorSpace
from ..Curves import CurvePath

from ._base import PDFItem

class PDFShape(PDFItem):
    def __init__(self, gstate: PDFGraphicState, evenodd: bool, paths: List[CurvePath]):
        self.gstate = gstate
        self.evenodd = evenodd
        self.paths = paths