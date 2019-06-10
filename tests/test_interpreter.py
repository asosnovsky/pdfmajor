import os
from unittest import TestCase, main
from pdfmajor.interpreter import LTCharBlock, PDFInterpreter, logging
from pdfmajor.interpreter import PageInterpreter
from pdfmajor.interpreter.commands import LTItem
from pdfmajor.interpreter.commands import LTCharBlock, LTChar

CUR_PATH = os.path.dirname(os.path.dirname(__file__))
INPUT_FOLDER = os.path.join(
    CUR_PATH, "tests/samples/pdf"
)
FILES = os.listdir(INPUT_FOLDER)

class TestInterpreter(TestCase):
    def test_pdfintp(self):
        for file_name in FILES:
            self.subTest(file_name=file_name)
            file_path = os.path.join(INPUT_FOLDER, file_name)
            for page in PDFInterpreter(file_path, debug_level=logging.ERROR):
                self.assertTrue( isinstance(page, PageInterpreter) )
                for item in page:
                    self.assertTrue( isinstance(item, LTItem) )
                    if isinstance(item, LTCharBlock):
                        for char in item:
                            self.assertTrue( isinstance(char, LTChar) )

if __name__ == '__main__':
    # Run Tests
    main()
