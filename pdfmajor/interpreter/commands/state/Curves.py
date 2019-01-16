from enum import Enum
from typing import List
from pdfmajor.utils import apply_matrix_pt

class CurvePoint:
    def __init__(self, ctm: tuple, x: float, y: float):
        # old = (x,y)
        # (x, y) = apply_matrix_pt(ctm, (x, y))
        # if old != (x,y):
        # print("CurvePoint", ctm, old)
        # print(" >", x, y)
        self.x = x
        self.y = y
    
    def __repr__(self) -> str:
        return f'<CurvePoint ({self.x}, {self.y})/>'

class CurveMethod(Enum):
    MOVE_TO='m'
    LINE_TO='l'
    CURVE_BOTH_TO='c'
    CURVE_NEXT_TO='v'
    CURVE_FIRST_TO='y'
    CLOSE_PATH='h'

class CurvePath:
    METHOD = CurveMethod
    def __init__(self, method: CurveMethod, *points: List[CurvePoint]):
        self.method = method
        self.points = points
    
    def __repr__(self) -> str:
        return f'<CurvePath {self.method} path=[{",".join(map(repr, self.points))}]/>'