# -*- coding: utf-8 -*-

from .PDFFont import PDFUnicodeNotDefined

from ..utils import isnumber
from ..utils import Bbox, mult_matrix, translate_matrix

from .PDFResourceManager import PDFResourceManager
from .PDFGraphicState import PDFGraphicState
from .PDFTextState import PDFTextState
from .PDFColorSpace import PDFColorSpace

##  PDFDevice
##
class PDFDevice(object):

    def __init__(self, rsrcmgr: PDFResourceManager):
        self.rsrcmgr = rsrcmgr
        self.ctm = None
        return

    def __repr__(self):
        return '<PDFDevice>'

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def close(self):
        return

    def set_ctm(self, ctm):
        self.ctm = ctm
        return

    def begin_tag(self, tag, props=None):
        return

    def end_tag(self):
        return

    def do_tag(self, tag, props=None):
        return

    def begin_page(self, page, ctm):
        return

    def end_page(self, page):
        return

    def begin_figure(self, name, bbox: Bbox, matrix):
        return

    def end_figure(self, name):
        return

    def paint_path(self, graphicstate: PDFGraphicState, stroke, fill, evenodd, path):
        return

    def render_image(self, name, stream):
        return

    def render_string(self, textstate, seq, ncs, graphicstate: PDFGraphicState):
        return


##  PDFTextDevice
##
class PDFTextDevice(PDFDevice):

    def render_string(self, textstate: PDFTextState, seq: bytearray, ncs: PDFColorSpace, graphicstate: PDFGraphicState):
        matrix = mult_matrix(textstate.matrix, self.ctm)
        font = textstate.font
        fontsize = textstate.fontsize
        scaling = textstate.scaling * .01
        charspace = textstate.charspace * scaling
        wordspace = textstate.wordspace * scaling
        rise = textstate.rise
       
        if font.is_multibyte():
            wordspace = 0
        dxscale = .001 * fontsize * scaling

        if textstate.font.is_vertical():
            textstate.linematrix = self.__render_string_along(1,
                seq, matrix, textstate.linematrix, font, fontsize,
                scaling, charspace, wordspace, rise, dxscale, ncs, graphicstate)
        else:
            textstate.linematrix = self.__render_string_along(0,
                seq, matrix, textstate.linematrix, font, fontsize,
                scaling, charspace, wordspace, rise, dxscale, ncs, graphicstate)

    def __render_string_along(self, idx: int, seq: bytearray, matrix: list, pos: tuple,
                                 font, fontsize, scaling, charspace, wordspace,
                                 rise, dxscale, ncs, graphicstate: PDFGraphicState):
        pos_copy = [*pos]
        needcharspace = False
        for obj in seq:
            if isnumber(obj):
                pos_copy[idx] -= obj*dxscale
                needcharspace = True
            else:
                for cid in font.decode(obj):
                    if needcharspace:
                        pos_copy[idx] += charspace
                    pos_copy[idx] += self.render_char(translate_matrix(matrix, pos_copy),
                                          font, fontsize, scaling, rise, cid,
                                          ncs, graphicstate)
                    if cid == 32 and wordspace:
                        pos_copy[idx] += wordspace
                    needcharspace = True
        return pos_copy

    def render_char(self, matrix, font, fontsize, scaling, rise, cid, ncs, graphicstate: PDFGraphicState):
        return NotImplementedError
