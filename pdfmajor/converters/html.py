from ..extractor import extract_items_from_pdf

def convert_to_html(
    input_file_path: str, 
    output_file: io.TextIOWrapper = None, 
    image_folder_path: str = None,
    codec: str = 'utf-8',
    maxpages: int = 0, 
    password: str = None, 
    caching: bool = True, 
    check_extractable: bool = True,
    pagenos: List[int] = None,
    debug_level: int = logging.WARNING,
):
    