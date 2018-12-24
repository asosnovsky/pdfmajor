from typing import List

from pdfmajor.utils import apply_matrix_norm, apply_matrix_pt, matrix2str, Bbox, Point

from ..PDFGraphicState import PDFColor
from ..PDFTextState import PDFFont
from ..PDFTextState import PDFTextState

from ._base import LTContainer
from .LTCharBlock import LTCharBlock
from .utils.textdecoder import decode_text_seq


##  LTTextBlock
##
class LTTextBlock(LTContainer):
    def __init__(self, x0=None, y0=None, x1=None, y1=None):
        LTContainer.__init__(self, 
            Bbox(x0, y0, x1, y1),
            []
        )
    
    def add_char_block(self, seq: bytearray, ctm: tuple, textstate: PDFTextState, color: PDFColor):
        (char_meta_datas, textstate, color) = decode_text_seq(seq, ctm, textstate, color)
        char_block = LTCharBlock(
            chars=char_meta_datas,
            color=color,
            textstate=textstate
        )
        if None in [self.bbox.x0, self.bbox.x1, self.bbox.y0, self.bbox.y1]:
            self.bbox.x0 = char_block.x0
            self.bbox.x1 = char_block.x1
            self.bbox.y0 = char_block.y0
            self.bbox.y1 = char_block.y1
        else:
            self.bbox.x0 = min([self.bbox.x0, char_block.x0])
            self.bbox.x1 = max([self.bbox.x1, char_block.x1])
            self.bbox.y0 = min([self.bbox.y0, char_block.y0])
            self.bbox.y1 = max([self.bbox.y1, char_block.y1])
        self.add(char_block)