from ._base import LTComponent
from ..utils import apply_matrix_norm, apply_matrix_pt, matrix2str, Bbox
from ..interpreter.PDFGraphicState import PDFGraphicState
from ..interpreter.PDFFont import PDFFont
from ..interpreter.PDFTextState import PDFTextState
from ..interpreter.PDFColorSpace import PDFColorSpace

##  LTString
##
class LTString(LTComponent):

    def __init__(self, 
        textstate: PDFTextState, 
        seq: bytearray, 
        ncs: PDFColorSpace, 
        graphicstate: PDFGraphicState
    ):
    
    LTComponent.__init__(self, Bbox(x0, y0, x1, y1))