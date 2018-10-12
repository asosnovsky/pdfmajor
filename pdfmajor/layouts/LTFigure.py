from typing import List

from ._base import LTContainer
from ..utils import Bbox, Point, matrix2str

##  LTFigure
##
class LTFigure(LTContainer):

    def __init__(self, name: str, pts: List[Point], matrix):
        LTContainer.__init__(self, Bbox.from_points(pts))
        self.name = name
        self.matrix = matrix

    def __repr__(self):
        return ('<%s(%s) %s matrix=%s>' %
                (self.__class__.__name__, self.name,
                 str(self.bbox), matrix2str(self.matrix)))
