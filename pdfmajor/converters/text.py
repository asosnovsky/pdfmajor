from typing import List

from ..interpreter import PDFInterpreter, PageInterpreter, logging
from ..interpreter import LTTextBlock, LTXObject


def convert_to_text(
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
    with open(output_file_path, 'wb') as outfp:
        def process_container(container: LTXObject):
            for item in container:
                if isinstance(item, LTTextBlock):
                    for text in item:
                        for char in text:
                            outfp.write(char.get_text().encode(codec))
                elif isinstance(item, LTXObject):
                    process_container(item)
        for page in intepreter:
            outfp.write(f"========== [ page {page.page_num} ] ==========\n".encode(codec))
            process_container(page)
            outfp.write('\n'.encode(codec))
