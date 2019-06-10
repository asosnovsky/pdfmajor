import os
from unittest import TestCase, main

from pdfmajor.interpreter import LTImage, logging
from pdfmajor.interpreter import PageInterpreter, PDFInterpreter
from pdfmajor.interpreter.commands import LTItem
from pdfmajor.interpreter.commands import LTCharBlock, LTChar

CUR_PATH = os.path.dirname(os.path.dirname(__file__))
FILES = [
    "jpg",
    "looseless"
]
OUTPUT_FOLDER = os.path.join(
    CUR_PATH,
    'samples/output/images'
)

if not os.path.exists(OUTPUT_FOLDER):
    os.makedirs(OUTPUT_FOLDER)

class ImageTester(TestCase):
    def test_image_extract(self):
        for file_name in FILES:
            self.subTest(file_name=file_name)
            for page in PDFInterpreter(os.path.join(
                CUR_PATH,
                f"tests/samples/pdf/{file_name}.pdf"
            ), debug_level=logging.ERROR):
                self.assertTrue( isinstance(page, PageInterpreter) )
                for item_idx, item in enumerate(page):
                    self.assertTrue( isinstance(item, LTItem) )
                    if isinstance(item, LTImage):
                        item.save_image(
                            OUTPUT_FOLDER, 
                            file_name=f'{file_name}_p{page.page_num}i{item_idx}'
                        )

if __name__ == '__main__':
    # Run Tests
    main()
