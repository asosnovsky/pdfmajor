from ._base import LTComponent
from ..utils import apply_matrix_norm, apply_matrix_pt, matrix2str, Bbox
from ..interpreter.PDFGraphicState import PDFGraphicState
from ..interpreter.PDFFont import PDFFont
from ..interpreter.PDFColorSpace import PDFColorSpace
from ..interpreter.PDFTextState import PDFTextState

##  LTChar
##
class LTChar(LTComponent):

    def __init__(self, 
        bbox: Bbox, 
        char: str, 
        textstate: PDFTextState, 
        ncs: PDFColorSpace, 
        graphicstate: PDFGraphicState
    ):
        self._text = char
        self.font = textstate.font
        self.textstate = textstate
        self.ncs = ncs
        self.graphicstate = graphicstate
        LTComponent.__init__(self, bbox)
        if self.font.is_vertical():
            self.size = self.width
        else:
            self.size = self.height
        return

    def __repr__(self):
        return (
            '<%s %s font=%r text=%r>' %
            (
                self.__class__.__name__, 
                str(self.bbox),
                self.fontname, 
                self.get_text()
            )
        )

    def get_text(self):
        return self._text

    @property
    def fontname(self) -> str:
        return self.font.fontname