from ._base import LTComponent
from pdfmajor.utils import apply_matrix_norm, apply_matrix_pt, matrix2str, Bbox
from ..PDFGraphicState import PDFColor
from ..PDFTextState import PDFTextState, PDFFont

##  LTChar
##
class LTChar(LTComponent):

    def __init__(self, 
        bbox: Bbox, 
        char: str, 
        textstate: PDFTextState, 
        color: PDFColor
    ):
        self._text = char
        self.textstate = textstate
        self.color = color
        LTComponent.__init__(self, bbox)
        if self.textstate.font.is_vertical():
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
    def font(self):
        return self.textstate.font

    @property
    def fontname(self) -> str:
        return self.font.fontname