from typing import List

from .writers.yaml import YAMLMaker, YAMLMakerObject, YAMLMakerArray
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

def convert_to_yaml(
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
    with YAMLMaker(output_file_path, codec=codec) as yaml:
        with yaml.array("pages") as arr:
            for page in intepreter:
                with arr.object() as page_obj:
                    render_page(page_obj, page)

def render_page(yaml: YAMLMakerObject, ltpage: PageInterpreter):  
    yaml.write("id", ltpage.page_num)
    yaml.write("width", ltpage.width)
    yaml.write("height", ltpage.height)
    with yaml.array("children") as chil_arr:
        for child in ltpage:
            with chil_arr.object() as chil_obj:
                render(chil_obj, child)

def render(yaml: YAMLMakerObject, item: LTItem):
    if isinstance(item, LTCurve):
        place_curve(yaml, item)
    elif isinstance(item, LTXObject):
        yaml.write("type", 'xobject')
        yaml.write("x0", item.x0)
        yaml.write("x1", item.x1)
        yaml.write("y0", item.y0)
        yaml.write("y1", item.y1)
        with yaml.array("children") as chil_arr:
            for child in item:
                with chil_arr.object() as chil_obj:
                    render(chil_obj, child)
    elif isinstance(item, LTImage):
        # if yaml.imagewriter is not None:
        #     name = yaml.imagewriter.export_image(item)
        yaml.write("type", 'img')
        yaml.write("src", enc(item.name, None))
        yaml.write("x0", item.x0)
        yaml.write("x1", item.x1)
        yaml.write("y0", item.y0)
        yaml.write("y1", item.y1)
    elif isinstance(item, LTTextBlock):
        place_text_block(yaml, item)

def place_text_block(yaml: YAMLMakerObject, text_block: LTTextBlock):
    yaml.write("type", 'text-block')
    yaml.write("x0", text_block.x0)
    yaml.write("x1", text_block.x1)
    yaml.write("y0", text_block.y0)
    yaml.write("y1", text_block.y1)
    with yaml.array("char_blocks") as cb_arr:
        for cb in text_block:
            with cb_arr.object() as cb_obj:
                place_char_block(cb_obj, cb)

def place_char_block(yaml: YAMLMakerObject, char_block: LTCharBlock):
    yaml.write("size", char_block.size)
    yaml.write("x0", char_block.x0)
    yaml.write("x1", char_block.x1)
    yaml.write("y0", char_block.y0)
    yaml.write("y1", char_block.y1)
    if char_block.color.color_space is not None:
        yaml.place_object("color", {
            "type": enc(char_block.color.color_space.name).decode(),
            "value": normalize_color_values(char_block.color.values)
        })
    for key, value in char_block.font.descriptor.items():
        if key != "Type" and "FontFile" not in key:
            yaml.write(key, value)
    yaml.write("text", 
        "".join([
            char.get_text()
            for char in char_block
        ])
    )

def place_curve(yaml: YAMLMakerObject, item: LTCurve):                  
    if isinstance(item, LTRect):
        yaml.write("type", 'rect')
    elif isinstance(item, LTLine):
        yaml.write("type", 'line')
    else:
        yaml.write("type", 'curve')
        with yaml.array('paths') as paths_arr:
            for path in item.paths:
                paths_arr.place_object({
                    "type": path.method.name,
                    "points": [
                        {"x": point.x, "y": point.y}
                        for point in path.points
                    ]
                })

    yaml.write("x0", item.x0)
    yaml.write("x1", item.x1)
    yaml.write("y0", item.y0)
    yaml.write("y1", item.y1)
    if item.fill.color_space is not None:
        yaml.place_object("fill", {
            "type": enc(item.fill.color_space.name).decode(),
            "value": normalize_color_values(item.fill.values)
        })
    if item.stroke.color_space is not None:
        yaml.place_object("stroke", {
            "type": enc(item.stroke.color_space.name).decode(),
            "value": normalize_color_values(item.stroke.values)
        })