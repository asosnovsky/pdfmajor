import logging

from typing import Dict

from contextlib import contextmanager

from ..layouts import LTPage
from ..layouts import LTItem
from ..layouts import LTCurve, LTLine, LTRect, CurvePath
from ..layouts import LTFigure
from ..layouts import LTImage
from ..layouts import LTChar, LTCharBlock
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
            return f'rgba(0,0,0,{1-color_val[0]})'
        elif color_type == "custom":
            # Todo: convert these to more friendly color types
            return f"custom({col.custom['type']})"
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
    
    def write(self, text: str, lineend: str = '\n', deep_space: str = ' '):
        text = deep_space*self.__levels_deep + text + lineend
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
    def place_elm_with_child(self, tag_name: str, attr_dict: Dict[str, str] = {}, css: Dict[str, str] = None, no_additional_char = False):
        lineend = '\n'
        deep_space = ' '
        if no_additional_char:
            lineend = ''
            deep_space = ''

        if css is not None:
            attr_dict['style'] = ";".join([
                f'{name}: {value}'
                for name, value in css.items()
            ])
        attrs = " ".join([
            f'{name}="{value}"'
            for name, value in attr_dict.items()
        ])
        self.write(f"<{tag_name} {attrs}>", lineend=lineend)
        self.__levels_deep += 1
        yield
        self.__levels_deep -= 1
        self.write(f"</{tag_name}>", deep_space=deep_space)

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
        path = ""
        svg_attr = {
            'class': 'curve',
            'z-index': 2
        }

        p_vals = { "x": [], "y": []  }

        for p in item.paths:
            for pt in p.points:
                p_vals['x'].append(pt.x)
                p_vals['y'].append(pt.y)

        mx_x = max([*p_vals['x'], 1])
        mn_x = min([*p_vals['x'], 0])
        mx_y = max([*p_vals['y'], 1])
        mn_y = min([*p_vals['y'], 0])

        if mx_x == mn_x:
            mn_x -= 1
        if mx_y == mn_y:
            mn_y -= 1

        dx = 1/( mx_x - mn_x )
        dy = (item.height/item.width)/( mx_y - mn_y )
        ROUND_VAL = 5
        svg_attr.update({
            # "viewBox": f"{min(p_vals['x'])} {min(p_vals['y'])} {max(p_vals['x'])} {max(p_vals['y'])}",
            "viewBox": f"{round(mn_x*dx, ROUND_VAL)} {round(mn_y*dy, ROUND_VAL)} {round(mx_x*dx , ROUND_VAL)} {round(mx_y*dy, ROUND_VAL)}",
        })

        for p in item.paths:
            if p.method == CurvePath.METHOD.MOVE_TO:
                path += f'M{" ".join( f"{round(dx*pt.x, ROUND_VAL)} {round(dy*pt.y, ROUND_VAL)}" for pt in p.points )} '
            if p.method == CurvePath.METHOD.LINE_TO:
                path += f'L{" ".join( f"{round(dx*pt.x, ROUND_VAL)} {round(dy*pt.y, ROUND_VAL)}" for pt in p.points )} '
            if p.method == CurvePath.METHOD.CLOSE_PATH:
                path += 'Z'
        with self.place_elm_with_child('svg', svg_attr, css):
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
                    'width': item.width,
                    'min-width': item.width,
                    'max-width': item.width,
                    'height': item.height,
                    'min-height': item.height,
                    'max-height': item.height,
                }):
                    self.write(item.get_text())
            elif isinstance(item, LTCharBlock):
                with self.place_elm_with_child('span', { 'class': 'char-block' }, {
                        'position': 'absolute',
                        'left': f'{item.x0}',
                        'bottom': f'{item.y0}',
                        'text-align': 'justify',
                        'font-size': f'{item.size}px',
                        'font-family': item.fontname,
                        'font-weight': item.font.font_weight,
                        'color': get_color(item.graphicstate.ncolor),
                        'width': item.width,
                        'min-width': item.width,
                        'max-width': item.width,
                        'height': item.height,
                        'min-height': item.height,
                        'max-height': item.height,
                        'transform': f'skew({item.font.italic_angle}deg, 0deg)',
                        'text-align': 'center',
                        'display': 'flex',
                        'flex-flow': 'row nowrap',
                        'justify-content': 'space-between',
                        # 'padding-left': item.font.leading
                    }):
                    for char in item:
                        render(char)
        render(ltpage)

    def close(self):
        self.write_footer()
    