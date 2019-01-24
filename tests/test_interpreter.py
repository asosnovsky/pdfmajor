import os
from tqdm import tqdm
from pdfmajor.interpreter import LTCharBlock, PDFInterpreter, logging
from pdfmajor.interpreter import PageInterpreter
from pdfmajor.interpreter.commands import LTItem
from pdfmajor.interpreter.commands import LTCharBlock, LTChar

CUR_PATH = os.path.dirname(os.path.dirname(__file__))
INPUT_FOLDER = os.path.join(
    CUR_PATH, "tests/samples/pdf"
)
FILES = os.listdir(INPUT_FOLDER)

for file_name in tqdm(FILES, desc="Interpreter Test"):
    file_path = os.path.join(INPUT_FOLDER, file_name)
    for page in PDFInterpreter(file_path, debug_level=logging.ERROR):
        assert isinstance(page, PageInterpreter)
        for item in page:
            assert isinstance(item, LTItem)
            if isinstance(item, LTCharBlock):
                for char in item:
                    assert isinstance(char, LTChar)