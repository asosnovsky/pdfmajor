from typing import List
from pdfmajor.utils import apply_matrix_pt, INF, Bbox, Point, MATRIX_IDENTITY, mult_matrix

from ..Curves import CurvePath
from ..PDFGraphicState import PDFGraphicState, PDFColor
from ..PDFTextState import PDFTextState

from ._base import LTItem, LTComponent, LTContainer
from .LTTextBlock import LTTextBlock
from .LTCharBlock import LTCharBlock, LTChar
from .LTCurves import LTCurve, LTLine, LTHorizontalLine, LTRect, LTVerticalLine
from .LTImage import LTImage
from .LTXObject import LTXObject
from .utils.textdecoder import decode_text_seq


def make_char_block(seq: bytearray, ctm: tuple, textstate: PDFTextState, color: PDFColor):
    (char_meta_datas, textstate, color) = decode_text_seq(seq, ctm, textstate, color)
    return LTCharBlock(
        chars=char_meta_datas,
        color=color,
        textstate=textstate
    )

def make_curve(ctm: tuple, gstate: PDFGraphicState, evenodd: bool, paths: List[CurvePath]):
    shape = ''.join(x.method.value for x in paths)
    if shape == 'ml':
        # horizontal/vertical line
        pt0 = paths[0].points[0]
        pt1 = paths[1].points[0]
        (x0, y0) = apply_matrix_pt(ctm, (pt0.x, pt0.y))
        (x1, y1) = apply_matrix_pt(ctm, (pt1.x, pt1.y))
        if x0 == x1:
            return LTVerticalLine(
                linewidth=gstate.linewidth, 
                paths=paths,
                bbox=Bbox( x0, y0, x1, y1 ),
                stroke=gstate.scolor, 
                fill=gstate.ncolor, 
                evenodd=evenodd, 
            )
        elif y0 == y1:
            return LTHorizontalLine(
                linewidth=gstate.linewidth, 
                paths=paths,
                bbox=Bbox( x0, y0, x1, y1 ),
                stroke=gstate.scolor, 
                fill=gstate.ncolor, 
                evenodd=evenodd, 
            )
        else:
            return LTLine(
                linewidth=gstate.linewidth, 
                paths=paths,
                bbox=Bbox( x0, y0, x1, y1 ),
                stroke=gstate.scolor, 
                fill=gstate.ncolor, 
                evenodd=evenodd, 
            )
    elif shape == 'mlllh':
        # rectangle
        pt0 = paths[0].points[0]
        pt1 = paths[1].points[0]
        pt2 = paths[2].points[0]
        pt3 = paths[3].points[0]
        (x0, y0) = apply_matrix_pt(ctm, (pt0.x, pt0.y))
        (x1, y1) = apply_matrix_pt(ctm, (pt1.x, pt1.y))
        (x2, y2) = apply_matrix_pt(ctm, (pt2.x, pt2.y))
        (x3, y3) = apply_matrix_pt(ctm, (pt3.x, pt3.y))
        if ((x0 == x1 and y1 == y2 and x2 == x3 and y3 == y0) or
            (y0 == y1 and x1 == x2 and y2 == y3 and x3 == x0)):
            return LTRect( 
                linewidth=gstate.linewidth, 
                paths=paths,
                bbox=Bbox(
                    x0=min(x0,x1,x2,x3),
                    x1=max(x0,x1,x2,x3),
                    y0=min(y0,y1,y2,y3),
                    y1=max(y0,y1,y2,y3),
                ),
                evenodd=evenodd, 
                stroke=gstate.scolor, 
                fill=gstate.ncolor,
            )
    else:
        (x0, y0, x1, y1) = (INF, INF, -INF, -INF)
        for path in paths:
            if path.method in [CurvePath.METHOD.MOVE_TO, CurvePath.METHOD.LINE_TO]:
                x0 = min(x0, path.points[0].x)
                y0 = min(y0, path.points[0].y)
                x1 = max(x1, path.points[0].x)
                y1 = max(y1, path.points[0].y)
            elif path.method in [CurvePath.METHOD.CURVE_BOTH_TO]:
                x0 = min(x0, path.points[2].x)
                y0 = min(y0, path.points[2].y)
                x1 = max(x1, path.points[2].x)
                y1 = max(y1, path.points[2].y)
            elif path.method in [CurvePath.METHOD.CURVE_NEXT_TO, CurvePath.METHOD.CURVE_FIRST_TO]:
                x0 = min(x0, path.points[1].x)
                y0 = min(y0, path.points[1].y)
                x1 = max(x1, path.points[1].x)
                y1 = max(y1, path.points[1].y)
        return LTCurve(
            linewidth=gstate.linewidth, 
            paths=paths,
            bbox=Bbox(x0,y0,x1,y1), 
            evenodd=evenodd,
            stroke=gstate.scolor, 
            fill=gstate.ncolor
        )

def make_image(obj, ctm):
    matrix = mult_matrix(MATRIX_IDENTITY, ctm)
    return LTImage(
        name=str(id(obj)),
        stream=obj,
        bbox=Bbox.from_points([
            apply_matrix_pt(matrix, (p, q))
            for (p, q) in ((0, 0), (1, 0), (0, 1), (1, 1))
        ])
    )

def make_xobject(obj, bbox, ctm, matrix, resources):
    (x, y, w, h) = bbox
    return LTXObject(
        name=str(id(obj)),
        bbox=Bbox.from_points([
            apply_matrix_pt(matrix, (p, q))
            for (p, q) in ((x, y), (x+w, y), (x, y+h), (x+w, y+h))
        ]),
        xobj_stream=obj,
        resources=resources,
        t_matrix = ctm
    )