import re
from typing import List
from xml.sax import saxutils

from .writers.xml import XMLMaker
from ..interpreter import PDFInterpreter, PageInterpreter, logging
from ..interpreter import LTImage, LTTextBlock, LTCharBlock, LTChar, LTCurve, LTXObject
from ..interpreter.commands import LTItem
from ..interpreter.commands import LTRect, LTLine
from ..interpreter.commands.state import CurvePath, PDFColor
from ..parser.PSStackParser import PSLiteral
from ..utils import enc

FIRST_CAP_RE = re.compile('(.)([A-Z][a-z]+)')
ALL_CAP_RE = re.compile('([a-z0-9])([A-Z])')
def convert_capcase_to_snakecase(text: str) -> str:
    s1 = FIRST_CAP_RE.sub(r'\1-\2', text)
    return ALL_CAP_RE.sub(r'\1-\2', s1).lower()

def normalize_color_values(values: list):
    ret = ""
    for i,v in enumerate(values):
        if i > 0:
            ret += ','
        if isinstance(v, PSLiteral):
            ret += enc(str(v.name)).decode()
        else:
            ret += enc(str(v)).decode()
    return ret

def get_color(col: PDFColor, prefix: str = 'color', codec = 'utf-8'):
    if col.color_space is not None:
        return {
            f"{prefix}-type": enc(col.color_space.name).decode(),
            f"{prefix}-values": normalize_color_values(col.values)
        }
    return {}

def convert_to_xml(
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
    with XMLMaker(output_file_path, codec=codec) as xml:
        with xml.elm("pages"):
            for page in intepreter:
                render_page(xml, page)

def render_page(xml: XMLMaker, ltpage: PageInterpreter):
    def render(item: LTItem):
        if isinstance(item, LTCurve):
            place_curve(xml, item)
        elif isinstance(item, LTXObject):
            with xml.elm('xobject', {
                "x0": item.x0,
                "x1": item.x1,
                "y0": item.y0,
                "y1": item.y1,
            }):
                for child in item:
                    render(child)
        elif isinstance(item, LTImage):
            name = item.name
            # if xml.imagewriter is not None:
            #     name = xml.imagewriter.export_image(item)
            xml.singleton('img', attrs={
                'src': enc(name, None),
                "x0": item.x0,
                "x1": item.x1,
                "y0": item.y0,
                "y1": item.y1,
            })
        elif isinstance(item, LTTextBlock):
            place_text_block(xml, item)
    with xml.elm('page', { 
        "id": ltpage.page_num,
        "width": ltpage.width,
        "height": ltpage.height,
    }):
        for child in ltpage:
            render(child)

def place_char(xml: XMLMaker, char: LTChar):
    with xml.elm('char', {
        'x0': char.x0,
        'x1': char.x1,
        'y0': char.y0,
        'y1': char.y1,
    }, no_additional_char=True):
        xml.write(saxutils.escape(char.get_text()), lineend='', deep_space="")

def place_char_block(xml: XMLMaker, char_block: LTCharBlock):
    attr = {
        'size': char_block.size,
        "x0": char_block.x0,
        "x1": char_block.x1,
        "y0": char_block.y0,
        "y1": char_block.y1,
        **get_color(char_block.color, codec=xml.codec),
    }
    for key, value in char_block.font.descriptor.items():
        if key != "Type" and "FontFile" not in key:
            attr[convert_capcase_to_snakecase(key)] = value
    with xml.elm("char-block", attr):
        for char in char_block:
            place_char(xml, char)

def place_text_block(xml: XMLMaker, text_block: LTCharBlock):
    attr = {
        "x0": text_block.x0,
        "x1": text_block.x1,
        "y0": text_block.y0,
        "y1": text_block.y1,
    }
    with xml.elm("text-block", attr):
        for char_block in text_block:
            place_char_block(xml, char_block)

def place_curve(xml: XMLMaker, item: LTCurve):
    attr = {
        "x0": item.x0,
        "x1": item.x1,
        "y0": item.y0,
        "y1": item.y1,
        **get_color(item.stroke, "stroke", codec=xml.codec),
        **get_color(item.fill, "fill", codec=xml.codec),
    }
    if isinstance(item, LTRect):
        return xml.singleton('rect', attr)
    elif isinstance(item, LTLine):
        return xml.singleton('line', attr)

    with xml.elm('curve', attr):
        for path in item.paths:
            with xml.elm('path', { "type": path.method.name }):
                for point in path.points:
                    xml.singleton('point', { 'x': point.x, 'y': point.y })