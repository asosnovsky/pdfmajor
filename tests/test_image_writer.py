import os
from tqdm import tqdm

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

for file_name in tqdm(FILES, desc='Image Writer Test'):
    for page in PDFInterpreter(os.path.join(
        CUR_PATH,
        f"tests/samples/pdf/{file_name}.pdf"
    ), debug_level=logging.ERROR):
        assert isinstance(page, PageInterpreter)
        for item_idx, item in enumerate(page):
            assert isinstance(item, LTItem)
            if isinstance(item, LTImage):
                item.save_image(
                    OUTPUT_FOLDER, 
                    file_name=f'{file_name}_p{page.page_num}i{item_idx}'
                )