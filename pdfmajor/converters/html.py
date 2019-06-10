from typing import List, Optional
from .writers.html import HTMLMaker
from ..interpreter import PDFInterpreter, PageInterpreter, logging
from ..interpreter import LTImage, LTTextBlock, LTCharBlock, LTChar, LTCurve, LTXObject
from ..interpreter.commands import LTItem
from ..interpreter.commands.state import CurvePath, PDFColor

INF = (1<<31) - 1

def convert_to_html(
    input_file_path: str, 
    output_file_path: str, 
    image_folder_path: Optional[str] = None,
    dont_export_images: bool = False,
    codec: str = 'utf-8',
    maxpages: int = 0, 
    password: Optional[str] = None, 
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
    def render(item: LTItem, block = True):
        if isinstance(item, LTCurve):
            render_curve(html, ltpage, item)
        elif isinstance(item, LTXObject):
            with html.elm('div', { "class": 'xobject' }, {
                # 'position': 'absolute', 
                'left': f'{item.x0}px', 
                'right': f'{item.x1}px', 
                'bottom': f'{item.y0}px', 
                'top': f'{item.y1}px', 
                'width': f'{item.width}px', 
                'height': f'{item.height}px',
            }):
                for child in item:
                    render(child, False)
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
                'width': str(item.width) + "px",
                'min-width': str(item.width) + "px",
                'max-width': str(item.width) + "px",
                'height': str(item.height) + "px",
                'min-height': str(item.height) + "px",
                'max-height': str(item.height) + "px",
            }):
                html.write(item.get_text())
        elif isinstance(item, LTTextBlock):
            with html.elm('span', {'class': 'text-block'}):
                for char in item:
                    render(char)
        elif isinstance(item, LTCharBlock):
            with html.elm('span', { 'class': 'char-block' }, {
                'position': 'absolute',
                'left': f'{item.x0}',
                'bottom': f'{item.y0}',
                'font-size': f'{item.size}px',
                'font-family': item.fontname,
                'font-weight': item.font.font_weight,
                'color': get_color(item.color, default="black"),
                'width': str(item.width) + "px",
                'min-width': str(item.width) + "px",
                'max-width': str(item.width) + "px",
                'height': str(item.height) + "px",
                'min-height': str(item.height) + "px",
                'max-height': str(item.height) + "px",
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

def render_curve(html: HTMLMaker, ltpage: PageInterpreter, item: LTCurve):
    path, svg_attr = create_svg_path(item)
    
    stroke_col = get_color(item.stroke)
    fill_col = get_color(item.fill)
    path_css = {}
    if fill_col:
        path_css['fill'] = fill_col
    if stroke_col:
        path_css['stroke'] = stroke_col

    with html.elm('svg', svg_attr, css={
        'border': '1px solid black',
        'position': 'absolute', 
        'left': f'{item.x0}px', 
        'bottom': f'{ltpage.height - item.y0}px', 
        'top': f'{ltpage.height - item.y1}px', 
        'right': f'{item.x1}px', 
        'width': f'{item.width}px',
        'height': f'{item.height}px',
    }):
        html.singleton('path', {
            "d": path,
            **path_css
        }, {
            **path_css
        })

def create_svg_path(item: LTCurve):
    path = ""
    svg_attr = {
        'class': 'curve',
        'z-index': 2
    }

    if item.height > 0:
        dy = 1.0/item.height
        dx = (item.width/item.height)/max([(item.x1-item.x0),0.01])
        svg_attr.update({
            "viewBox": "0 0 %s %s" % ( item.width/item.height, 1 )
        })
    else:
        dx = 1.0/(item.x1-item.x0)
        dy = 1.0
        svg_attr.update({
            "viewBox": "0 0 1 1"
        })

    if item.height > 1:
        svg_attr.update({
            'height': f'{item.height}px',
        })
    else:
        svg_attr.update({
            'height': '1px',
        })
    
    if item.width > 1:
        svg_attr.update({
            'width': f'{item.width}px',
        })
    else:
        svg_attr.update({
            'width': '1px',
        })

    def pX(val: float) -> float:
        return ( val-item.x0 )*dx
    def pY(val: float) -> float:
        return ( item.height- (val-item.y0) )*dy

    for p in item.paths:
        if p.method == CurvePath.METHOD.MOVE_TO:
            path += f'M{" ".join( f"{pX(p.x)} {pY(p.y)}" for p in p.points )} '
        elif p.method == CurvePath.METHOD.LINE_TO:
            path += f'L{" ".join( f"{pX(p.x)} {pY(p.y)}" for p in p.points )} '
        elif p.method == CurvePath.METHOD.CLOSE_PATH:
            path += 'Z'
        elif p.method == CurvePath.METHOD.CURVE_BOTH_TO:
            path += f'C{" ".join( f"{pX(pt.x)} {pY(pt.y)}" for pt in p.points )} '
    
    return path, svg_attr

# def render_textblock(html: HTMLMaker, ltpage: PageInterpreter, item: LTTextBlock):
#     (x0, y0, x1, y1) = (INF, INF, -INF, -INF)

#     for c_block in item:
#         x0 = min(x0, c_block.x0)
#         y0 = min(y0, c_block.y0)
#         x1 = max(x1, c_block.x1)
#         y1 = max(y1, c_block.y1)
    
#     with html.elm('span')
