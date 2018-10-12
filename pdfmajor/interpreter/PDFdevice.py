# -*- coding: utf-8 -*-

from .PDFFont import PDFUnicodeNotDefined

from ..utils import isnumber
from ..utils import Bbox, mult_matrix, translate_matrix

from .PDFResourceManager import PDFResourceManager
from .PDFGraphicState import PDFGraphicState

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

    def render_string(self, textstate, seq, ncs, graphicstate: PDFGraphicState):
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
        if font.is_vertical():
            textstate.linematrix = self.render_string_vertical(
                seq, matrix, textstate.linematrix, font, fontsize,
                scaling, charspace, wordspace, rise, dxscale, ncs, graphicstate)
        else:
            textstate.linematrix = self.render_string_horizontal(
                seq, matrix, textstate.linematrix, font, fontsize,
                scaling, charspace, wordspace, rise, dxscale, ncs, graphicstate)
        return

    def render_string_horizontal(self, seq, matrix, pos,
                                 font, fontsize, scaling, charspace, wordspace,
                                 rise, dxscale, ncs, graphicstate: PDFGraphicState):
        (x, y) = pos
        needcharspace = False
        for obj in seq:
            if isnumber(obj):
                x -= obj*dxscale
                needcharspace = True
            else:
                for cid in font.decode(obj):
                    if needcharspace:
                        x += charspace
                    x += self.render_char(translate_matrix(matrix, (x, y)),
                                          font, fontsize, scaling, rise, cid,
                                          ncs, graphicstate)
                    if cid == 32 and wordspace:
                        x += wordspace
                    needcharspace = True
        return (x, y)

    def render_string_vertical(self, seq, matrix, pos,
                               font, fontsize, scaling, charspace, wordspace,
                               rise, dxscale, ncs, graphicstate: PDFGraphicState):
        (x, y) = pos
        needcharspace = False
        for obj in seq:
            if isnumber(obj):
                y -= obj*dxscale
                needcharspace = True
            else:
                for cid in font.decode(obj):
                    if needcharspace:
                        y += charspace
                    y += self.render_char(translate_matrix(matrix, (x, y)),
                                          font, fontsize, scaling, rise, cid,
                                          ncs, graphicstate)
                    if cid == 32 and wordspace:
                        y += wordspace
                    needcharspace = True
        return (x, y)

    def render_char(self, matrix, font, fontsize, scaling, rise, cid, ncs, graphicstate: PDFGraphicState):
        return 0
