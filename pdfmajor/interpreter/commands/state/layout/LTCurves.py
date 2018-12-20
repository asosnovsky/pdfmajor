
from typing import List, Tuple

from pdfmajor.utils import Bbox
from ..PDFGraphicState import PDFColor
from ..Curves import CurvePath

from ._base import LTComponent, Bbox

class LTCurve(LTComponent):

    def __init__(self, 
        linewidth: float, 
        paths: List[CurvePath], 
        bbox: Bbox,
        stroke: PDFColor, 
        fill: PDFColor, 
        evenodd: bool, 
    ):
        LTComponent.__init__(self, bbox)
        self.paths = paths
        self.linewidth = linewidth
        self.evenodd = evenodd
        self.stroke = stroke
        self.fill = fill

##  LTLine
##
class LTLine(LTCurve):
    pass

##  LTHorizontalLine
##
class LTHorizontalLine(LTLine):
    pass

##  LTHorizontalLine
##
class LTVerticalLine(LTLine):
    pass

##  LTRect
##
class LTRect(LTCurve):
    pass
