from ._base import LTContainer
from ..utils import Bbox

class LTPage(LTContainer):
    """A class reprensting an extracted page from the pdf
        Arguments:
            pageid {int} -- page number
            bbox {Bbox} -- Boundary Box
            rotate {float} -- rotation of the page (default: {0})
    """

    def __init__(self, pageid: int, bbox: Bbox, rotate: float=0):
        LTContainer.__init__(self, bbox)
        self.pageid = pageid
        self.rotate = rotate

    def __repr__(self):
        return ('<%s(%r) %s rotate=%r>' %
                (self.__class__.__name__, self.pageid,
                 str(self.bbox), self.rotate))