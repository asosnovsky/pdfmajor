import logging

from typing import Dict

from io import BytesIO
from contextlib import contextmanager

from ..layouts import LTPage
from ..layouts import LTItem
from ..layouts import LTCurve
from ..layouts import LTLine
from ..layouts import LTRect
from ..layouts import LTFigure
from ..layouts import LTImage
from ..layouts import LTChar
from ..utils import enc

from .PDFConverter import PDFConverter
from ..interpreter.PDFGraphicState import PDFGraphicStateColor

log = logging.getLogger(__name__)

def get_color(col: PDFGraphicStateColor):
    color_type, color_val = col.get_color()
    if color_type is not None:
        if color_type == 'rgb':
            return f"rgb({','.join(map(str, color_val))})"
        elif color_type == 'cmyk':
            return f"cmyk({','.join(map(str, color_val))})"
        elif color_type == 'gray':
            return f'gray({color_val})'
    return ""

class JSONConverter(PDFConverter):
    def __init__(self, 
        rsrcmgr, 
        outfp: BytesIO, 
        codec: str='utf-8', 
        pageno: int=1, 
        imagewriter=None,
    ):
        PDFConverter.__init__(self, rsrcmgr, outfp, imagewriter=imagewriter, codec=codec, pageno=pageno)
        self.__last_levels_deep:int = None
        self.__levels_deep = 0
        self.write_header()
    
    @property
    def _levels_deep(self): return self.__levels_deep

    @_levels_deep.setter
    def _levels_deep(self, val: int):
        self.__last_levels_deep = self.__levels_deep
        self.__levels_deep = val

    def write(self, text: str):
        if self.__last_levels_deep == self._levels_deep:
            text = ',' + text
        self.write_raw(text)
    
    def write_raw(self, text):
        if self.codec:
            text = text.encode(self.codec)
        self.outfp.write(text)
        self._levels_deep = self._levels_deep
    
    def write_header(self):
        self.write("{")
        self._levels_deep += 1
        if self.codec:
            self.write('"encoding": "%s"' % self.codec)
        self.write('"pages": [')
        self._levels_deep += 1
    
    def write_footer(self):
        self._levels_deep -= 1
        self.write(']')
        self._levels_deep -= 1
        self.write('}')

    @contextmanager
    def place_elm_with_child(self, tag_name: str, attr_dict: Dict[str, str] = {}):
        attrs = ", ".join([
            f'"{name}": "{value}"'
            for name, value in attr_dict.items()
        ])
        self.write('{ "type": "%s", "attrs": { %s } , "children": [' % (tag_name, attrs) )
        self._levels_deep += 1
        yield
        self._levels_deep -= 1
        self.write("]}")

    def place_elm_close(self, tag_name: str, attr_dict: Dict[str, str] = {}):
        attrs = ", ".join([
            f'"{name}": "{value}"'
            for name, value in attr_dict.items()
        ])
        self.write('{ "type": "%s", "attrs": { %s } }' % (tag_name, attrs) ) 

    def place_image(self, item: LTImage):
        name = item.name

        if self.imagewriter is not None:
            name = self.imagewriter.export_image(item)

        self.place_elm_close('img', {
            'src': enc(name, None),
            "x0": item.x0,
            "x1": item.x1,
            "y0": item.y0,
            "y1": item.y1,
        })

    def place_text(self, char: LTChar):
        self.place_elm_close('char', {
            'font-size': char.size,
            'font-family': char.fontname,
            "x0": char.x0,
            "x1": char.x1,
            "y0": char.y0,
            "y1": char.y1,
            "stroke-color": get_color(char.graphicstate.scolor),
            "fill-color": get_color(char.graphicstate.ncolor),
            "text": char.get_text()
        })

    def render_curve(self, item: LTCurve):
        attr = {
            "x0": item.x0,
            "x1": item.x1,
            "y0": item.y0,
            "y1": item.y1,
            "stroke-color": get_color(item.stroke),
            "fill-color": get_color(item.fill),
        }
        if isinstance(item, LTRect):
            return self.place_elm_close('rect', attr)
        elif isinstance(item, LTLine):
            return self.place_elm_close('line', attr)

        with self.place_elm_with_child('curve', attr):
            for path in item.paths:
                with self.place_elm_with_child('path', { "type": path.method.name }):
                    for point in path.points:
                        self.place_elm_close('point', { 'x': point.x, 'y': point.y })

    def receive_layout(self, ltpage: LTPage):
        def render(item: LTItem):
            if isinstance(item, LTPage):
                with self.place_elm_with_child('page', { 
                    "width": item.width,
                    "height": item.height
                }):
                    for child in item:
                        render(child)
            elif isinstance(item, LTCurve):
                self.render_curve(item)
            elif isinstance(item, LTFigure):
                with self.place_elm_with_child('figure', { 
                    "x0": item.x0,
                    "x1": item.x1,
                    "y0": item.y0,
                    "y1": item.y1,
                }):
                    for child in item:
                        render(child)
            elif isinstance(item, LTImage):
                self.place_image(item)
            elif isinstance(item, LTChar):
                self.place_text(item)
        render(ltpage)

    def close(self):
        self.write_footer()
    