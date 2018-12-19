from typing import List

from ._base import LTContainer
from .LTChar import LTChar

from pdfmajor.utils import apply_matrix_norm, apply_matrix_pt, matrix2str, Bbox, Point
from ..PDFGraphicState import PDFColor
from ..PDFTextState import PDFFont
from ..PDFTextState import PDFTextState

##  LTCharBlock
##
class LTCharBlock(LTContainer):

    def __init__(self, 
        chars: list, # [str, List[Point]]
        textstate: PDFTextState, 
        color: PDFColor
    ):
        c, ((x0, y0), (x1, y1)) = chars[0]
        ltchars = [
            LTChar(
                bbox=Bbox(x0, y0, x1, y1),
                char= c,
                textstate=textstate, 
                color=color
            )
        ]

        for c, pts in chars[1:]:
            ((nx0, ny0), (nx1, ny1)) = pts
            x0 = min([ x0, x1, nx0, nx1 ])
            x1 = max([ x0, x1, nx0, nx1 ])
            y1 = max([ y0, y1, ny0, ny1 ])
            y0 = min([ y0, y1, ny0, ny1 ])
            ltchars.append(LTChar(
                bbox=Bbox(nx0, ny0, nx1, ny1),
                char= c,
                textstate=textstate, 
                color=color
            ))

        LTContainer.__init__(self, Bbox(x0, y0, x1, y1), ltchars)
        
        self.textstate = textstate
        self.color = color

        if self.textstate.font.is_vertical():
            self.size = self.width
        else:
            self.size = self.height
        return

    def __repr__(self):
        return f"""<{self.__class__.__name__} font="{self.fontname}" text="{self.get_text()}"/>"""

    def get_text(self):
        return "".join([ c.get_text() for c in self ])

    @property
    def font(self):
        return self.textstate.font

    @property
    def fontname(self) -> str:
        return self.textstate.font.fontname