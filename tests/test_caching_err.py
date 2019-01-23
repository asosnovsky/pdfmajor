import os
from tqdm import tqdm

# from pdfmajor.extractor import extract_items_from_pdf
from pdfmajor.interpreter import LTCharBlock, PDFInterpreter, logging
from pdfmajor.interpreter import PageInterpreter
from pdfmajor.interpreter.commands import LTContainer

CUR_PATH = os.path.dirname(os.path.dirname(__file__))
INPUT_FOLDER = os.path.join(
    CUR_PATH, "tests/samples/pdf"
)
FILES = os.listdir(INPUT_FOLDER)
NUM_LOOPS = 10

def count_elms(file_path: str):
    count = 0
    for page in PDFInterpreter(file_path):
        for item in page:
            if isinstance(item, LTContainer):
                count += len([*item])
            else:
                count += 1
    return count

with tqdm(desc='Cache Test', total=len(FILES)*NUM_LOOPS) as waiter:
    for file_name in FILES:
        waiter.set_description(f"Cache Test - [{file_name}]")
        file_path = os.path.join(INPUT_FOLDER, file_name)
        last_count = count_elms(file_path)
        for _ in range(NUM_LOOPS):
            new_count = count_elms(file_path)
            assert new_count == last_count
            last_count = new_count
            waiter.update()
