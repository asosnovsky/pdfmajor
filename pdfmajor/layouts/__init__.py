import logging
import re
import io

from abc import abstractmethod
from typing import Tuple, List

from ._base import LTItem
from .LTPage import LTPage
from .LTCurves import LTCurve, LTLine, LTRect
from .LTFigure import LTFigure
from .LTImage import LTImage
from .LTChar import LTChar

from ..utils import Point, Bbox
from ..utils import apply_matrix_pt, mult_matrix

from ..interpreter.PDFFont import PDFUnicodeNotDefined
from ..interpreter.PDFResourceManager import PDFResourceManager
from ..interpreter.PDFGraphicState import PDFGraphicState, PDFGraphicStateColor
from ..interpreter.PDFdevice import PDFTextDevice
from ..interpreter.PDFPage import PDFPage
from ..interpreter.PDFStream import PDFStream

log = logging.getLogger(__name__)


##  PDFLayoutAnalyzer
##
class PDFLayoutAnalyzer(PDFTextDevice):


    def __init__(self, rsrcmgr: PDFResourceManager, pageno: int=1):
        PDFTextDevice.__init__(self, rsrcmgr)
        self.pageno = pageno
        self._stack = []
        return

    def begin_page(self, page: PDFPage, ctm: Tuple[float]):
        (x0, y0, x1, y1) = page.mediabox
        (x0, y0) = apply_matrix_pt(ctm, (x0, y0))
        (x1, y1) = apply_matrix_pt(ctm, (x1, y1))
        self.cur_item = LTPage(
            self.pageno, 
            Bbox( 0, 0, abs(x0-x1), abs(y0-y1) )
        )
        return

    def end_page(self, page: PDFPage):
        assert not self._stack, str(len(self._stack))
        assert isinstance(self.cur_item, LTPage), str(type(self.cur_item))
        # self.cur_item.analyze()
        self.pageno += 1
        self.receive_layout(self.cur_item)
        return

    def begin_figure(self, name: str, bbox: List[Point], matrix: List[Point]):
        self._stack.append(self.cur_item)

        matrix = mult_matrix(matrix, self.ctm)
        (x, y, w, h) = bbox

        self.cur_item = LTFigure(name, [
            apply_matrix_pt(matrix, (p, q))
            for (p, q) in ((x, y), (x+w, y), (x, y+h), (x+w, y+h))
        ], matrix)

    def end_figure(self, name: str):
        fig = self.cur_item
        assert isinstance(self.cur_item, LTFigure), str(type(self.cur_item))
        self.cur_item = self._stack.pop()
        self.cur_item.add(fig)
        return

    def render_image(self, name: str, stream: PDFStream):
        assert isinstance(self.cur_item, LTFigure), str(type(self.cur_item))
        item = LTImage(
            name, 
            stream,
            Bbox(
                self.cur_item.x0, self.cur_item.y0,
                self.cur_item.x1, self.cur_item.y1
            )
        )
        self.cur_item.add(item)
        return

    def paint_path(self, gstate: PDFGraphicState, evenodd: bool, path: list):
        shape = ''.join(x[0] for x in path)
        if shape == 'ml':
            # horizontal/vertical line
            (_, x0, y0) = path[0]
            (_, x1, y1) = path[1]
            (x0, y0) = apply_matrix_pt(self.ctm, (x0, y0))
            (x1, y1) = apply_matrix_pt(self.ctm, (x1, y1))
            if x0 == x1 or y0 == y1:
                self.cur_item.add(LTLine(
                    gstate.linewidth, 
                    (x0, y0), (x1, y1),
                    stroke=gstate.scolor, 
                    fill=gstate.ncolor, 
                    evenodd=evenodd, 
                ))
                return
        if shape == 'mlllh':
            # rectangle
            (_, x0, y0) = path[0]
            (_, x1, y1) = path[1]
            (_, x2, y2) = path[2]
            (_, x3, y3) = path[3]
            (x0, y0) = apply_matrix_pt(self.ctm, (x0, y0))
            (x1, y1) = apply_matrix_pt(self.ctm, (x1, y1))
            (x2, y2) = apply_matrix_pt(self.ctm, (x2, y2))
            (x3, y3) = apply_matrix_pt(self.ctm, (x3, y3))
            if ((x0 == x1 and y1 == y2 and x2 == x3 and y3 == y0) or
                (y0 == y1 and x1 == x2 and y2 == y3 and x3 == x0)):
                self.cur_item.add(LTRect( 
                    linewidth=gstate.linewidth, 
                    pts=[
                        (x0, y0), (x0, y2), 
                        (x2, y0), (x2, y2)
                    ],
                    evenodd=evenodd, 
                    stroke=gstate.scolor, 
                    fill=gstate.ncolor,
                ))
                return
        # other shapes
        pts = []
        for p in path:
            for i in range(1, len(p), 2):
                pts.append(apply_matrix_pt(self.ctm, (p[i], p[i+1])))
        self.cur_item.add(LTCurve(
            linewidth=gstate.linewidth, 
            pts=pts, 
            evenodd=evenodd,
            stroke=gstate.scolor, 
            fill=gstate.ncolor
        ))
        return

    def render_char(self, matrix: List[Point], font, fontsize, scaling, rise, cid, ncs, graphicstate):
        try:
            text = font.to_unichr(cid)
            assert isinstance(text, str), str(type(text))
        except PDFUnicodeNotDefined:
            text = self.handle_undefined_char(font, cid)
        textwidth = font.char_width(cid)
        textdisp = font.char_disp(cid)
        item = LTChar(
            matrix, 
            font, fontsize, 
            scaling, 
            rise, text, 
            textwidth, textdisp, 
            ncs, graphicstate
        )
        self.cur_item.add(item)
        return item.adv

    def handle_undefined_char(self, font: str, cid: int):
        log.info('undefined: %r, %r', font, cid)
        return '(cid:%d)' % cid


    @abstractmethod
    def receive_layout(self, ltpage: LTPage):
        raise NotImplementedError
