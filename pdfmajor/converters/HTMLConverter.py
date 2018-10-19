import logging

from typing import Dict

from contextlib import contextmanager

from ..layouts import LTPage
from ..layouts import LTItem
from ..layouts import LTCurve, LTLine, LTRect, CurvePath
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
            return f'rgba(0,0,0,{1-color_val})'
    return "none"

class HTMLConverter(PDFConverter):
    def __init__(self, 
        rsrcmgr, 
        outfp, 
        codec='utf-8', 
        pageno=1, 
        imagewriter=None
    ):
        PDFConverter.__init__(self, rsrcmgr, outfp, imagewriter=imagewriter, codec=codec, pageno=pageno)
        self.__levels_deep = 0
        self.__current_height = None
        self.__current_width = None
        self.write_header()
    
    def write(self, text: str):
        text = " "*self.__levels_deep + text + '\n'
        self.write_raw(text)
    
    def write_raw(self, text):
        if self.codec:
            text = text.encode(self.codec)
        self.outfp.write(text)
    
    def write_header(self):
        self.write('<html>')
        self.__levels_deep += 1
        self.write('<head>')
        self.__levels_deep += 1
        meta_attr = {
            'http-equiv': "Content-Type",
            'content': "text/html",
        }
        if self.codec:
            meta_attr['charset'] = self.codec

        self.place_elm_close('meta', attr_dict=meta_attr, as_childless=False)
        with self.place_elm_with_child('style'):
            self.write('''.page { position: relative; overflow: hidden;border: 1px black solid;}''')
        self.__levels_deep -= 1
        self.write('</head>')
        self.write('<body>')
        self.__levels_deep += 1
    
    def write_footer(self):
        self.write('</body>')
        self.__levels_deep -= 1
        self.write('</html>')
        self.__levels_deep -= 1

    @contextmanager
    def place_elm_with_child(self, tag_name: str, attr_dict: Dict[str, str] = {}, css: Dict[str, str] = None):
        if css is not None:
            attr_dict['style'] = ";".join([
                f'{name}: {value}'
                for name, value in css.items()
            ])
        attrs = " ".join([
            f'{name}="{value}"'
            for name, value in attr_dict.items()
        ])
        self.write(f"<{tag_name} {attrs}>")
        self.__levels_deep += 1
        yield
        self.__levels_deep -= 1
        self.write(f"</{tag_name}>")

    def place_elm_close(self, tag_name: str, attr_dict: Dict[str, str] = {}, css: Dict[str, str] = None, as_childless = True):
        if css is not None:
            attr_dict['style'] = ";".join([
                f'{name}: {value}'
                for name, value in css.items()
            ])
        attrs = " ".join([
            f'{name}="{value}"'
            for name, value in attr_dict.items()
        ])
        if as_childless:
            self.write(f"<{tag_name} {attrs}></{tag_name}>")
        else:
            self.write(f"<{tag_name} {attrs}/>")
    
    def place_image(self, item: LTImage):
        name = item.name
        if self.imagewriter is not None:
            name = self.imagewriter.export_image(item)
            self.place_elm_close('img', {
                'src': enc(name, None),
                'width': f"{item.width}px", 
                'height': f"{item.height}px",
            })
        return

    def render_curve(self, item: LTCurve):
        css = {
            'position': 'absolute', 
            'left': f'{item.x0}px', 
            'bottom': f'{item.y0}px', 
            'width': f'{item.width}px', 
            'height': f'{item.height}px',
        }
        if isinstance(item, LTRect):
            self.place_elm_close('div', {'class': 'curve rect'}, {**css, 
                "border-color": get_color(item.stroke),
                "background-color": get_color(item.fill),
                'z-index': 0
            })
        elif isinstance(item, LTLine):
            self.place_elm_close('div', {'class': 'curve line'}, {**css, 
                "background-color": get_color(item.fill),
                "border-color": get_color(item.stroke),
                'z-index': 0
            })
        else:
            path = ""


            dx = (item.width/item.height)/(item.x1-item.x0)
            dy = 1.0/(item.y1-item.y0)

            for p in item.paths:
                if p.method == CurvePath.METHOD.MOVE_TO:
                    path += f'M{" ".join( f"{(item.width - (p.x-item.x0) )*dx} {(item.height- (p.y-item.y0) )*dy}" for p in p.points )} '
                if p.method == CurvePath.METHOD.LINE_TO:
                    path += f'L{" ".join( f"{(item.width - (p.x-item.x0) )*dx} {( item.height - (p.y-item.y0) )*dy}" for p in p.points )} '
                if p.method == CurvePath.METHOD.CLOSE_PATH:
                    path += 'Z'
            with self.place_elm_with_child('svg', {
                    'class': 'curve',
                    "viewBox": f"0 0 {item.width/item.height} 1",
                    'width': f'{item.width}px', 
                    'height': f'{item.height}px',
                    'z-index': 2
                }, css):
                self.place_elm_close('path', {
                    "d": path,
                    'stroke': get_color(item.stroke),
                    'fill': get_color(item.fill),
                })

    def receive_layout(self, ltpage: LTPage):
        def render(item: LTItem):
            if isinstance(item, LTPage):
                with self.place_elm_with_child('div', { "class": 'page', "id": f"page-{item.pageid}" }, { 'width': f'{item.width}px', 'height': f'{item.height}px' }):
                    self.__current_height = item.height
                    self.__current_width = item.width
                    for child in item:
                        render(child)
            elif isinstance(item, LTCurve):
                self.render_curve(item)
            elif isinstance(item, LTFigure):
                with self.place_elm_with_child('div', { "class": 'figure' }, {
                    'position': 'absolute', 
                    'left': f'{item.x0}px', 
                    'bottom': f'{item.y0}px', 
                    'width': f'{item.width}px', 
                    'height': f'{item.height}px',
                }):
                    for child in item:
                        render(child)
            elif isinstance(item, LTImage):
                self.place_image(item)
            elif isinstance(item, LTChar):
                with self.place_elm_with_child('span', { 'class': 'char' }, {
                    'font-size': f'{item.size}px',
                    'font-family': item.fontname,
                    'color': get_color(item.graphicstate.ncolor),
                    'position': 'absolute',
                    'left': f'{item.x0}',
                    'bottom': f'{item.y0}',
                }):
                    self.write(item.get_text())
        render(ltpage)

    def close(self):
        self.write_footer()
    