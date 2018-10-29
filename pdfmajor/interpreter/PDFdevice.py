# -*- coding: utf-8 -*-

from .PDFFont import PDFUnicodeNotDefined

from ..utils import isnumber, apply_matrix_pt
from ..utils import Bbox, mult_matrix, translate_matrix

from .PDFResourceManager import PDFResourceManager
from .PDFGraphicState import PDFGraphicState
from .PDFTextState import PDFTextState
from .PDFColorSpace import PDFColorSpace
from .PDFFont import PDFFont

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
        textstate.matrix = mult_matrix(textstate.matrix, self.ctm)
        textstate.scaling = textstate.scaling * .01
        textstate.charspace = textstate.charspace * textstate.scaling
        textstate.wordspace = textstate.wordspace * textstate.scaling
       
        if textstate.font.is_multibyte():
            textstate.wordspace = 0
        dxscale = .001 * textstate.fontsize * textstate.scaling

        if textstate.font.is_vertical():
            self.__render_string_along(1,
                seq, textstate, dxscale, ncs, graphicstate
            )
        else:
            self.__render_string_along(0,
                seq, textstate, dxscale, ncs, graphicstate
            )

    def __render_string_along(self, idx: int, seq: bytearray, 
        textstate: PDFTextState, dxscale: float, ncs: PDFColorSpace, graphicstate: PDFGraphicState):
        needcharspace = False
        char_meta_datas = []
        for obj in seq:
            if isnumber(obj):
                textstate.linematrix[idx] -= obj*dxscale
                needcharspace = True
            else:
                for cid in textstate.font.decode(obj):
                    if needcharspace:
                        textstate.linematrix[idx] += textstate.charspace
                    
                    text = textstate.font.to_unichr(cid)
                    assert isinstance(text, str), str(type(text))

                    matrix = translate_matrix(textstate.matrix, textstate.linematrix)
                    adv, bbox = self.__compute_char_bbox(matrix, cid, textstate)
                    textstate.linematrix[idx] += adv

                    char_meta_datas.append(
                        ( text, bbox, )
                    )
                    if cid == 32 and textstate.wordspace:
                        textstate.linematrix[idx] += textstate.wordspace
                    needcharspace = True
                    
        self.render_char_box(char_meta_datas, textstate, graphicstate, ncs)

    def __compute_char_bbox(self, matrix, char_id: int, textstate: PDFTextState):
        font = textstate.font
        fontsize = textstate.fontsize
        rise = textstate.rise
        scaling = textstate.scaling

        textwidth = font.char_width(char_id)
        textdisp = font.char_disp(char_id)
        adv = textwidth * fontsize * scaling

        # compute the boundary rectangle.
        if font.is_vertical():
            # vertical
            width = font.get_width() * fontsize
            (vx, vy) = textdisp
            if vx is None:
                vx = width * 0.5
            else:
                vx = vx * fontsize * .001
            vy = (1000 - vy) * fontsize * .001
            tx = -vx
            ty = vy + rise
            bll = (tx, ty+adv)
            bur = (tx+width, ty)
        else:
            # horizontal
            height = font.get_height() * fontsize
            descent = font.get_descent() * fontsize
            ty = descent + rise
            bll = (0, ty)
            bur = (adv, ty+height)
        (x0, y0) = apply_matrix_pt(matrix, bll)
        (x1, y1) = apply_matrix_pt(matrix, bur)
        if x1 < x0:
            (x0, x1) = (x1, x0)
        if y1 < y0:
            (y0, y1) = (y1, y0)
        
        return (adv, ((x0, y0), (x1, y1)))

    def render_char_box(self, chars: list, textstate: PDFTextState, graphicstate: PDFGraphicState, ncs: PDFColorSpace):
        pass
