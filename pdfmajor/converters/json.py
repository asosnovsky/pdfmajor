from typing import List, Optional

from .writers.json import JSONMaker, JSONMakerObject, JSONMakerArray
from ..interpreter import PDFInterpreter, PageInterpreter, logging
from ..interpreter import LTImage, LTTextBlock, LTCharBlock, LTCurve, LTXObject
from ..interpreter.commands import LTItem
from ..interpreter.commands import LTRect, LTLine
from ..interpreter.commands.state import CurvePath, PDFColor
from ..parser.PSStackParser import PSLiteral
from ..utils import enc

def normalize_color_values(values: list):
    ret = []
    for v in values:
        if isinstance(v, PSLiteral):
            ret.append( enc(str(v.name)).decode() )
        else:
            ret.append( enc(str(v)).decode() )
    return ret

def convert_to_json(
    input_file_path: str, 
    output_file_path: str, 
    image_folder_path: Optional[str] = None,
    dont_export_images: bool = False,
    codec: str = 'utf-8',
    maxpages: int = 0, 
    password: str = Optional[None], 
    caching: bool = True, 
    check_extractable: bool = True,
    pagenos: Optional[List[int]] = None,
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
    with JSONMaker(output_file_path, codec=codec) as json:
        with json.array("pages") as arr:
            for page in intepreter:
                with arr.object() as page_obj:
                    render_page(page_obj, page)

def render_page(json: JSONMakerObject, ltpage: PageInterpreter):  
    json.number("id", ltpage.page_num)
    json.number("width", ltpage.width)
    json.number("height", ltpage.height)
    with json.array("children") as chil_arr:
        for child in ltpage:
            with chil_arr.object() as chil_obj:
                render(chil_obj, child)

def render(json: JSONMakerObject, item: LTItem):
        if isinstance(item, LTCurve):
            place_curve(json, item)
        elif isinstance(item, LTXObject):
            json.string("type", 'xobject')
            json.number("x0", item.x0)
            json.number("x1", item.x1)
            json.number("y0", item.y0)
            json.number("y1", item.y1)
            with json.array("children") as chil_arr:
                for child in item:
                    with chil_arr.object() as chil_obj:
                        render(chil_obj, child)
        elif isinstance(item, LTImage):
            # if json.imagewriter is not None:
            #     name = json.imagewriter.export_image(item)
            json.string("type", 'img')
            json.string("src", enc(item.name, None))
            json.number("x0", item.x0)
            json.number("x1", item.x1)
            json.number("y0", item.y0)
            json.number("y1", item.y1)
        elif isinstance(item, LTTextBlock):
            place_text_block(json, item)

def place_text_block(json: JSONMakerObject, text_block: LTTextBlock):
    json.string("type", 'text-block')
    json.number("x0", text_block.x0)
    json.number("x1", text_block.x1)
    json.number("y0", text_block.y0)
    json.number("y1", text_block.y1)
    with json.array("char_blocks") as cb_arr:
        for cb in text_block:
            with cb_arr.object() as cb_obj:
                place_char_block(cb_obj, cb)

def place_char_block(json: JSONMakerObject, char_block: LTCharBlock):
    json.number("size", char_block.size)
    json.number("x0", char_block.x0)
    json.number("x1", char_block.x1)
    json.number("y0", char_block.y0)
    json.number("y1", char_block.y1)
    if char_block.color.color_space is not None:
        json.place_object("color", {
            "type": enc(char_block.color.color_space.name).decode(),
            "value": normalize_color_values(char_block.color.values)
        })
    for key, value in char_block.font.descriptor.items():
        if key != "Type" and "FontFile" not in key:
            json.string(key, value)
    json.string("text", 
        "".join([
            char.get_text()
            for char in char_block
        ])
    )

def place_curve(json: JSONMakerObject, item: LTCurve):
    json.number("x0", item.x0)
    json.number("x1", item.x1)
    json.number("y0", item.y0)
    json.number("y1", item.y1)
    if item.fill.color_space is not None:
        json.place_object("fill", {
            "type": enc(item.fill.color_space.name).decode(),
            "value": normalize_color_values(item.fill.values)
        })
    if item.stroke.color_space is not None:
        json.place_object("stroke", {
            "type": enc(item.stroke.color_space.name).decode(),
            "value": normalize_color_values(item.stroke.values)
        })
                    
    if isinstance(item, LTRect):
        json.string("type", 'rect')
    elif isinstance(item, LTLine):
        json.string("type", 'line')
    else:
        json.string("type", 'curve')
        with json.array('paths') as paths_arr:
            for path in item.paths:
                paths_arr.place_object({
                    "type": path.method.name,
                    "points": [
                        {"x": point.x, "y": point.y}
                        for point in path.points
                    ]
                })