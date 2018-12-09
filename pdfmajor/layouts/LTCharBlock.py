from typing import List

from ._base import LTContainer
from .LTChar import LTChar

from ..utils import apply_matrix_norm, apply_matrix_pt, matrix2str, Bbox, Point
from ..interpreter.PDFGraphicState import PDFGraphicState
from ..interpreter.PDFFont import PDFFont
from ..interpreter.PDFColorSpace import PDFColorSpace
from ..interpreter.PDFTextState import PDFTextState

##  LTCharBlock
##
class LTCharBlock(LTContainer):

    def __init__(self, 
        chars: List[Point], 
        textstate: PDFTextState, 
        ncs: PDFColorSpace, 
        graphicstate: PDFGraphicState
    ):
        ((x0, y0), (x1, y1)) = chars[0][1]
        ltchars = [
            LTChar(
                bbox=Bbox(x0, y0, x1, y1),
                char= chars[0][0],
                textstate=textstate, 
                ncs=ncs, 
                graphicstate=graphicstate
            )
        ]

        for char in chars[1:]:
            ((nx0, ny0), (nx1, ny1)) = char[1]
            x0 = min([ x0, x1, nx0, nx1 ])
            x1 = max([ x0, x1, nx0, nx1 ])
            y1 = max([ y0, y1, ny0, ny1 ])
            y0 = min([ y0, y1, ny0, ny1 ])
            ltchars.append(LTChar(
                bbox=Bbox(nx0, ny0, nx1, ny1),
                char= char[0],
                textstate=textstate, 
                ncs=ncs, 
                graphicstate=graphicstate
            ))

        LTContainer.__init__(self, Bbox(x0, y0, x1, y1), ltchars)
        
        self.font = textstate.font
        self.textstate = textstate
        self.ncs = ncs
        self.graphicstate = graphicstate

        if self.font.is_vertical():
            self.size = self.width
        else:
            self.size = self.height
        return

    def __repr__(self):
        return f"""<{self.__class__.__name__} font="{self.fontname}" text="{self.get_text()}"/>"""

    def get_text(self):
        return "".join([ c.get_text() for c in self ])

    @property
    def fontname(self) -> str:
        return self.font.fontname