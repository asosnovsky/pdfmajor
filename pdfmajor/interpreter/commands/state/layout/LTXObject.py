from typing import List

from pdfmajor.utils import Bbox, Point, matrix2str
from pdfmajor.parser.PDFStream import PDFStream

from ._base import LTContainer

##  LTXObject
##
class LTXObject(LTContainer):

    def __init__(self, name: str, bbox: Bbox, xobj_stream: PDFStream, resources: dict, t_matrix: List[Point] ):
        LTContainer.__init__(self, bbox)
        self.name = name
        self.stream = xobj_stream
        self.t_matrix = t_matrix
        self.resources = resources

    def __repr__(self):
        return ('<%s(%s) %s matrix=%s>' %
                (self.__class__.__name__, self.name,
                 str(self.bbox), matrix2str(self.t_matrix)))
