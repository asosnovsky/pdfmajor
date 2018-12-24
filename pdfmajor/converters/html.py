from typing import List
from .writers.html import HTMLMaker
from ..interpreter import PDFInterpreter, PageInterpreter, logging
from ..interpreter import LTImage, LTTextBlock, LTCharBlock, LTChar, LTCurve, LTXObject
from ..interpreter.commands import LTItem
from ..interpreter.commands.state import CurvePath, PDFColor

def convert_to_html(
    input_file_path: str, 
    output_file_path: str, 
    image_folder_path: str = None,
    dont_export_images: bool = False,
    codec: str = 'utf-8',
    maxpages: int = 0, 
    password: str = None, 
    caching: bool = True, 
    check_extractable: bool = True,
    pagenos: List[int] = None,
    debug_level: int = logging.WARNING,
):
    intepreter = PDFInterpreter(input_file_path, 
        maxpages=maxpages, 
        password=password, 
        caching=caching,
        check_extractable=check_extractable,
        pagenos=pagenos,
        debug_level=debug_level
    )
    with HTMLMaker(output_file_path, codec=codec) as html:
        with html.elm("html", nolineend=True):
            with html.elm("head"):
                meta_attr = {
                    'http-equiv': "Content-Type",
                    'content': "text/html",
                }
                if html.codec:
                    meta_attr['charset'] = html.codec
                html.singleton("meta", meta_attr)
                with html.elm('style'):
                    html.write('''.page { position: relative; overflow: hidden;border: 1px black solid;}''')
            with html.elm("body"):
                for page in intepreter:
                    render_page(html, page)

def render_page(html: HTMLMaker, ltpage: PageInterpreter):
    def render(item: LTItem):
        if isinstance(item, LTCurve):
            render_curve(html, item)
        elif isinstance(item, LTXObject):
            with html.elm('div', { "class": 'xobject' }, {
                'position': 'absolute', 
                'left': f'{item.x0}px', 
                'bottom': f'{item.y0}px', 
                'width': f'{item.width}px', 
                'height': f'{item.height}px',
            }):
                for child in item:
                    render(child)
        elif isinstance(item, LTImage):
            name = item.name
            # if html.imagewriter is not None:
            #     name = html.imagewriter.export_image(item)
            html.singleton('img', attrs={
                'src': name,
                'background': 'red',
                'width': f"{item.width}px", 
                'height': f"{item.height}px",
            })
        elif isinstance(item, LTChar):
            with html.elm('span', { 'class': 'char' }, {
                'width': item.width,
                'min-width': item.width,
                'max-width': item.width,
                'height': item.height,
                'min-height': item.height,
                'max-height': item.height,
            }):
                html.write(item.get_text())
        elif isinstance(item, LTTextBlock):
            for char in item:
                render(char)
        elif isinstance(item, LTCharBlock):
            with html.elm('span', {'class': 'char-block'}):
                with html.elm('p', { 'class': 'text-block' }, {
                    'position': 'absolute',
                    'left': f'{item.x0}',
                    'bottom': f'{item.y0}',
                    'font-size': f'{item.size}px',
                    'font-family': item.fontname,
                    'font-weight': item.font.font_weight,
                    'color': get_color(item.color, default="black"),
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
    
    with html.elm('div', { "class": 'page', "id": f"page-{ltpage.page_num}" }, { 
        'width': f'{ltpage.width}px', 
        'height': f'{ltpage.height}px' 
    }):
        for child in ltpage:
            render(child)

def get_color(col: PDFColor, default: str = ""):
    if col.color_space is not None:
        if col.color_space.ncomponents == 1:
            if type(col.values[0]) in [float, int]:
                return f"rgba(0,0,0,{1 - float(col.values[0])})"
        elif col.color_space.ncomponents == 3:
            return f"rgb({','.join(map(str, col.values))})"
        elif col.color_space.ncomponents == 4:
            return f"cmyk({','.join(map(str, col.values))})"
        return f"{col.color_space.name}({','.join(map(str, col.values))})"
    else:
        return default

def render_curve(html: HTMLMaker, item: LTCurve):
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
        path_css = {

        }

        # Compute ViewBox
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
        
        # Compute shape
        for p in item.paths:
            if p.method == CurvePath.METHOD.MOVE_TO:
                path += f'M{" ".join( f"{round(dx*pt.x, ROUND_VAL)} {round(dy*pt.y, ROUND_VAL)}" for pt in p.points )} '
            if p.method == CurvePath.METHOD.LINE_TO:
                path += f'L{" ".join( f"{round(dx*pt.x, ROUND_VAL)} {round(dy*pt.y, ROUND_VAL)}" for pt in p.points )} '
            if p.method == CurvePath.METHOD.CLOSE_PATH:
                path += 'Z'
        
        stroke_col = get_color(item.stroke)
        fill_col = get_color(item.fill)
        if fill_col:
            path_css['fill'] = fill_col
        if stroke_col:
            path_css['stroke'] = stroke_col

        with html.elm('svg', svg_attr, css):
            html.singleton('path', {
                "d": path,
                **path_css
            }, {
                **path_css
            })
