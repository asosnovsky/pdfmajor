from typing import List
from ..utils import Bbox

##  LTItem
##
class LTItem(object):
    pass

##  LTComponent
##
class LTComponent(LTItem):
    def __init__(self, bbox: Bbox):
        if isinstance(bbox, Bbox):
            self.bbox = bbox
        else:
            raise Exception("Invalid BBox")
    
    def __repr__(self):
        return ('<%s %s>' %
                (self.__class__.__name__, str(self.bbox)))

    # Disable comparison.
    def __lt__(self, _):
        raise ValueError
    def __le__(self, _):
        raise ValueError
    def __gt__(self, _):
        raise ValueError
    def __ge__(self, _):
        raise ValueError

    @property
    def width(self): return self.bbox.width

    @property
    def height(self): return self.bbox.height

    @property
    def x0(self): return self.bbox.x0

    @property
    def x1(self): return self.bbox.x1

    @property
    def y0(self): return self.bbox.y0

    @property
    def y1(self): return self.bbox.y1

    def is_empty(self):
        return self.width <= 0 or self.height <= 0

    def is_hoverlap(self, obj):
        assert isinstance(obj, LTComponent), str(type(obj))
        return obj.x0 <= self.x1 and self.x0 <= obj.x1

    def hdistance(self, obj):
        assert isinstance(obj, LTComponent), str(type(obj))
        if self.is_hoverlap(obj):
            return 0
        else:
            return min(abs(self.x0-obj.x1), abs(self.x1-obj.x0))

    def hoverlap(self, obj):
        assert isinstance(obj, LTComponent), str(type(obj))
        if self.is_hoverlap(obj):
            return min(abs(self.x0-obj.x1), abs(self.x1-obj.x0))
        else:
            return 0

    def is_voverlap(self, obj):
        assert isinstance(obj, LTComponent), str(type(obj))
        return obj.y0 <= self.y1 and self.y0 <= obj.y1

    def vdistance(self, obj):
        assert isinstance(obj, LTComponent), str(type(obj))
        if self.is_voverlap(obj):
            return 0
        else:
            return min(abs(self.y0-obj.y1), abs(self.y1-obj.y0))

    def voverlap(self, obj):
        assert isinstance(obj, LTComponent), str(type(obj))
        if self.is_voverlap(obj):
            return min(abs(self.y0-obj.y1), abs(self.y1-obj.y0))
        else:
            return 0

##  LTContainer
##
class LTContainer(LTComponent):

    def __init__(self, bbox: Bbox):
        LTComponent.__init__(self, bbox)
        self._objs: List[LTItem] = []
        return

    def __iter__(self):
        return iter(self._objs)

    def __len__(self) -> int:
        return len(self._objs)

    def add(self, obj: LTItem):
        self._objs.append(obj)
        return

    def extend(self, objs: List[LTItem]):
        for obj in objs:
            self.add(obj)
        return




