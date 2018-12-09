import re
import os

from typing import List
from io import BytesIO, StringIO, TextIOWrapper

from tqdm import tqdm

from ..interpreter.PDFResourceManager import PDFResourceManager
from ..interpreter.PDFPage import PDFPage
from ..interpreter.PDFPageInterpreter import PDFPageInterpreter
from ..imagewriter import ImageWriter
from ..utils import set_log_level, get_logger, logging
from .PDFExtractor import PDFExctractor

log = get_logger(__name__)


def extract_items_from_pdf(
    input_file_path: str, 
    maxpages: int = 0, 
    password: str = None, 
    caching: bool = True, 
    check_extractable: bool = True,
    pagenos: List[int] = None,
    debug_level: int = logging.WARNING, 
):
    set_log_level(debug_level)
        
    log.debug("Creating resources....")
    rsrcmgr = PDFResourceManager(caching=caching)
    device = PDFExctractor(
        rsrcmgr=rsrcmgr,
        pageno=0
    )
    interpreter = PDFPageInterpreter(rsrcmgr, device)
    log.debug("Reading pages....")
    with open(input_file_path, 'rb') as input_file:
        pages = PDFPage.get_pages(input_file, pagenos=pagenos, maxpages=maxpages, password=password, caching=caching, check_extractable=check_extractable)
        
        page_waiter = tqdm(enumerate(pages), disable=debug_level > logging.INFO)
        for _, page in page_waiter:
            page_waiter.set_description("Processing pdf...")
            yield interpreter.process_page(page)   
        page_waiter.close() 
        device.close()