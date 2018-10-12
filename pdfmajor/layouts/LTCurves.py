
from typing import List, Tuple

from ..utils import Bbox
from ..interpreter.PDFGraphicState import PDFGraphicStateColor
from ._base import LTComponent

class LTCurve(LTComponent):

    def __init__(self, 
        linewidth: float, 
        pts: List[Tuple[float]], 
        stroke: PDFGraphicStateColor, 
        fill: PDFGraphicStateColor, 
        evenodd: bool, 
    ):
        LTComponent.__init__(self, Bbox.from_points(pts))
        self.pts = pts
        self.linewidth = linewidth
        self.evenodd = evenodd
        self.stroke = stroke
        self.fill = fill

    def get_pts(self):
        return ','.join('%.3f,%.3f' % p for p in self.pts)

##  LTLine
##
class LTLine(LTCurve):

    def __init__(self, linewidth: float, p0:Tuple[float], p1:Tuple[float], stroke = PDFGraphicStateColor(), fill = PDFGraphicStateColor(), evenodd = False):
        LTCurve.__init__(self, 
            linewidth=linewidth, 
            pts=[p0, p1], 
            stroke=stroke, 
            fill=fill, 
            evenodd=evenodd
        )

##  LTRect
##
class LTRect(LTCurve):

    def __init__(self, linewidth: float, pts: List[Tuple[float]], stroke = PDFGraphicStateColor(), fill = PDFGraphicStateColor(), evenodd = False):
        LTCurve.__init__(self, linewidth, pts, stroke, fill, evenodd)
