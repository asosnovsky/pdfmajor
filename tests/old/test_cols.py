import os
from typing import List
from unittest import TestCase, main

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

class ColorTest(TestCase):
    def run_test(self, file_path: str, curve_defs: List[List[PDFColor]]):
        def run_once(item):
            if isinstance(item, LTCurve):
                t_stroke, t_fill = curve_defs.pop(0)
                self.assertEqual( item.stroke.values, t_stroke.values )
                self.assertEqual( item.stroke.color_space, t_stroke.color_space )
                self.assertEqual( item.fill.values, t_fill.values )
                self.assertEqual( item.fill.color_space, t_fill.color_space )
            elif isinstance(item, LTXObject):
                for c in item:
                    run_once(c)

        for page in PDFInterpreter(file_path):
            for item in page:
                run_once(item)

    def test_lorem_v3(self):
        self.run_test(
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

    def test_lorem_v4(self):
        self.run_test(
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

    def test_lorem_v5(self):
        self.run_test(
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


if __name__ == '__main__':
    # Run Tests
    main()
