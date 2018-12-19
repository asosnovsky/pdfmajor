import os

from pdfmajor.extractor import v2_extract_items_from_pdf
from pdfmajor.interpreter_v2 import PDFText

CUR_PATH = os.path.dirname(os.path.dirname(__file__))
CUR_PATH = os.path.dirname(os.getcwd())

FILE_NAME = os.path.join(
    CUR_PATH,
    "samples/pdf/fonts.pdf"
)

for page in v2_extract_items_from_pdf(FILE_NAME):
    for item in page:
        if isinstance(item, PDFText):
            print(item.chars)
        else:
            print(item)