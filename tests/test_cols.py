import os
from typing import List
from tqdm import tqdm

# from pdfmajor.extractor import extract_items_from_pdf
from pdfmajor.interpreter import LTCharBlock, PDFInterpreter, logging
from pdfmajor.interpreter import PageInterpreter
from pdfmajor.interpreter.commands import LTCurve, PDFColor, LTXObject
from pdfmajor.interpreter.commands import PREDEFINED_COLORSPACE

CUR_PATH = os.path.dirname(os.path.dirname(__file__))
INPUT_FOLDER = os.path.join(
    CUR_PATH, "tests/samples/pdf"
)
FILES = os.listdir(INPUT_FOLDER)
NUM_LOOPS = 10

file_path = os.path.join(INPUT_FOLDER, "lorem-v4.pdf")

def run_test(file_path: str, curve_defs: List[List[PDFColor]]):
    def run_once(item):
        if isinstance(item, LTCurve):
            t_stroke, t_fill = curve_defs.pop(0)
            # print([item.stroke, item.fill])
            # print('...>', [t_stroke, t_fill])
            assert item.stroke.values == t_stroke.values
            assert item.stroke.color_space == t_stroke.color_space
            assert item.fill.values == t_fill.values
            assert item.fill.color_space == t_fill.color_space
        elif isinstance(item, LTXObject):
            for c in item:
                run_once(c)

    for page in PDFInterpreter(file_path):
        for item in page:
            run_once(item)

run_test(
    os.path.join(INPUT_FOLDER, "lorem-v3.pdf"),
    [
        [
            PDFColor(None),
            PDFColor(PREDEFINED_COLORSPACE['DeviceRGB'], 255, 255, 255),
        ],
        [
            PDFColor(None),
            PDFColor(PREDEFINED_COLORSPACE['DeviceRGB'], 114, 159, 207),
        ],
        [
            PDFColor(PREDEFINED_COLORSPACE['DeviceRGB'], 255, 255, 0),
            PDFColor(PREDEFINED_COLORSPACE['DeviceRGB'], 114, 159, 207),
        ],
        [
            PDFColor(PREDEFINED_COLORSPACE['DeviceRGB'], 255, 255, 0),
            PDFColor(PREDEFINED_COLORSPACE['DeviceRGB'], 114, 159, 207),
        ],
        [
            PDFColor(None),
            PDFColor(PREDEFINED_COLORSPACE['DeviceRGB'], 255, 255, 255),
        ],
        [
            PDFColor(PREDEFINED_COLORSPACE['DeviceRGB'], 0, 0, 128),
            PDFColor(PREDEFINED_COLORSPACE['DeviceRGB'], 255, 0, 0),
        ]
    ] +
    ([[
        PDFColor(PREDEFINED_COLORSPACE['DeviceRGB'], 0, 0, 128),
        PDFColor(PREDEFINED_COLORSPACE['DeviceRGB'], 255, 255, 255),
    ]]*24)+
    ([[
        PDFColor(PREDEFINED_COLORSPACE['DeviceRGB'], 0, 0, 128),
        PDFColor(PREDEFINED_COLORSPACE['DeviceRGB'], 0, 0, 0),
    ]]*11)+
    ([[
        PDFColor(PREDEFINED_COLORSPACE['DeviceRGB'], 128, 128, 128),
        PDFColor(PREDEFINED_COLORSPACE['DeviceRGB'], 0, 0, 0),
    ]]*5)+
    [[
        PDFColor(None),
        PDFColor(PREDEFINED_COLORSPACE['DeviceRGB'], 255, 255, 255),
    ]]
)

run_test(
    os.path.join(INPUT_FOLDER, "lorem-v4.pdf"),
    [
        [
            PDFColor(None),
            PDFColor(PREDEFINED_COLORSPACE['DeviceRGB'], 255, 255, 255),
        ],
        [
            PDFColor(None),
            PDFColor(PREDEFINED_COLORSPACE['DeviceRGB'], 64, 64, 64),
        ]
    ]
)

run_test(
    os.path.join(INPUT_FOLDER, "lorem-v5.pdf"),
    [
        [
            PDFColor(None),
            PDFColor(PREDEFINED_COLORSPACE['DeviceRGB'], 255, 255, 255),
        ],
        [
            PDFColor(None),
            PDFColor(PREDEFINED_COLORSPACE['DeviceRGB'], 128, 128, 128),
        ]
    ]
)
