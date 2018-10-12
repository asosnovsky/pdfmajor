from typing import List, Tuple

INF = (1<<31) - 1
Point = Tuple[float]
unicode = str

class Bbox:
    """A generic boundary box
    """

    def __init__(self, x0: float, y0: float, x1: float, y1: float):
        self.x0 = x0
        self.x1 = x1
        self.y0 = y0
        self.y1 = y1
    
    @property
    def height(self) -> float:
        return self.y1 - self.y0
    
    @property
    def width(self) -> float:
        return self.x1 - self.x0

    def __str__(self):
        return '%.3f,%.3f,%.3f,%.3f' % (self.x0, self.y0, self.x1, self.y1)
    
    def __repr__(self):
        return f"<Bbox {str(self)}/>"

    @classmethod
    def from_points(cls, pts: List[Point]):
        """Converts a list of points to a Boundary box."""
        (x0, y0, x1, y1) = (INF, INF, -INF, -INF)
        for (x, y) in pts:
            x0 = min(x0, x)
            y0 = min(y0, y)
            x1 = max(x1, x)
            y1 = max(y1, y)
        return Bbox(x0, y0, x1, y1)