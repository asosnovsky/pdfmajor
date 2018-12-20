import os

# from pdfmajor.extractor import extract_items_from_pdf
from pdfmajor.interpreter import LTCharBlock, PDFInterpreter, logging
from pdfmajor.interpreter import PageInterpreter
from pdfmajor.interpreter.commands import LTItem
from pdfmajor.interpreter.commands import LTCharBlock, LTChar

CUR_PATH = os.path.dirname(os.path.dirname(__file__))
FILE_NAME = os.path.join(
    "../" if CUR_PATH == "" else CUR_PATH,
    "samples/pdf/tables.pdf"
)

for page in PDFInterpreter(FILE_NAME, debug_level=logging.INFO):
    assert isinstance(page, PageInterpreter)
    for item in page:
        assert isinstance(item, LTItem)
        if isinstance(item, LTCharBlock):
            for char in item:
                assert(char, LTChar)