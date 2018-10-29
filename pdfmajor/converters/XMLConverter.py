import logging

from typing import Dict

from contextlib import contextmanager

from ..layouts import LTPage
from ..layouts import LTItem
from ..layouts import LTCurve
from ..layouts import LTLine
from ..layouts import LTRect
from ..layouts import LTFigure
from ..layouts import LTImage
from ..layouts import LTChar, LTCharBlock
from ..interpreter.PDFGraphicState import PDFGraphicStateColor
from ..utils import enc

from .PDFConverter import PDFConverter

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

class XMLConverter(PDFConverter):
    def __init__(self, 
        rsrcmgr, 
        outfp, 
        codec='utf-8', 
        pageno=1, 
        imagewriter=None,
    ):
        PDFConverter.__init__(self, rsrcmgr, outfp, imagewriter=imagewriter, codec=codec, pageno=pageno)
        self.__levels_deep = 0
        self.write_header()
    
    def write(self, text: str, lineend: str = '\n', deep_space: str = ' '):
        text = deep_space*self.__levels_deep + text + lineend
        self.write_raw(text)
    
    def write_raw(self, text):
        if self.codec:
            text = text.encode(self.codec)
        self.outfp.write(text)
    
    def write_header(self):
        if self.codec:
            self.write('<?xml version="1.0" encoding="%s" ?>' % self.codec)
        else:
            self.write('<?xml version="1.0" ?>')
        
        self.write('<pages>')
        self.__levels_deep += 1
    
    def write_footer(self):
        self.write('</pages>')

    @contextmanager
    def place_elm_with_child(self, tag_name: str, attr_dict: Dict[str, str] = {}, no_additional_char = False):
        lineend = '\n'
        deep_space = ' '
        if no_additional_char:
            lineend = ''
            deep_space = ''
        attrs = " ".join([
            f'{name}="{value}"'
            for name, value in attr_dict.items()
        ])
        self.write(f"<{tag_name} {attrs}>", lineend=lineend)
        self.__levels_deep += 1
        yield
        self.__levels_deep -= 1
        self.write(f"</{tag_name}>", deep_space=deep_space)

    def place_elm_close(self, tag_name: str, attr_dict: Dict[str, str] = {}, as_childless = True):
        attrs = " ".join([
            f'{name}="{value}"'
            for name, value in attr_dict.items()
        ])
        if as_childless:
            self.write(f"<{tag_name} {attrs}></{tag_name}>")
        else:
            self.write(f"<{tag_name} {attrs}/>")
    
    def place_full_container(self, class_name: str, item: LTItem):
        return self.place_elm_with_child(class_name, { 
            "x0": item.x0,
            "x1": item.x1,
            "y0": item.y0,
            "y1": item.y1,
        })    

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
        tag_name = 'char'
        if isinstance(char, LTCharBlock):
            tag_name = 'char-block'
        attr = {
            'size': char.size,
            "color": get_color(char.graphicstate.ncolor),
            "x0": char.x0,
            "x1": char.x1,
            "y0": char.y0,
            "y1": char.y1,
        }
        for key, value in char.font.descriptor.items():
            if key != "Type" and "FontFile" not in key:
                attr["font-" + key] = value
        with self.place_elm_with_child(tag_name, attr, no_additional_char=True):
            self.write(char.get_text(), lineend='', deep_space="")

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
                with self.place_full_container('page', item):
                    for child in item:
                        render(child)
            elif isinstance(item, LTCurve):
                self.render_curve(item)
            elif isinstance(item, LTFigure):
                with self.place_full_container('figure', item):
                    for child in item:
                        render(child)
            elif isinstance(item, LTImage):
                self.place_image(item)
            elif isinstance(item, LTChar) or isinstance(item, LTCharBlock):
                self.place_text(item)
        render(ltpage)

    def close(self):
        self.write_footer()
    