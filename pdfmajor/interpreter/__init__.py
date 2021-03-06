from typing import List

from pdfmajor.execptions import EmptyDocumentError

from ..parser.PDFPage import PDFPage
from ..utils import set_log_level, get_logger, logging
from .commands.state import PDFStateStack, PDFColorSpace, PREDEFINED_COLORSPACE
from .commands import PDFCommands
from .commands import LTTextBlock, LTCharBlock, LTChar
from .commands import LTCurve, LTLine, LTHorizontalLine, LTVerticalLine, LTRect
from .commands import LTImage
from .commands import LTXObject
from .PageInterpreter import PageInterpreter

log = get_logger(__name__)

class PDFInterpreter:

    def __init__(self,
        input_file_path: str, 
        maxpages: int = 0, 
        caching: bool = True, 
        check_extractable: bool = True,
        password: str = None, 
        pagenos: List[int] = None,
        preload: bool = False,
        ignore_bad_chars: bool = False,
        debug_level: int = logging.WARNING, 
    ):
        self.input_file_path = input_file_path
        self.maxpages = maxpages
        self.caching = caching
        self.check_extractable = check_extractable
        self.password = password
        self.pagenos = pagenos
        self.ignore_bad_chars = ignore_bad_chars
        self.debug_level = debug_level
        self.__pages = []
        if preload:
            for _ in self.__load_pages():
                pass
        
    def __load_pages(self):
        set_log_level(self.debug_level)
        log.info("Opening file...")
        with open(self.input_file_path, 'rb') as input_file:
            font_cache = {}
            log.info("Parsing file...")
            pages = PDFPage.get_pages(
                input_file, 
                pagenos=self.pagenos, 
                maxpages=self.maxpages, 
                password=self.password, 
                caching=self.caching, 
                check_extractable=self.check_extractable
            )
            for page_num, page in enumerate(pages):
                self.__pages.append(PageInterpreter(page, page_num, font_cache, ignore_bad_chars=self.ignore_bad_chars))
                yield self.__pages[-1]
            log.info(f"Done Reading {len(self.__pages)} pages.")
        set_log_level(logging.WARNING)
        
        if len(self.__pages) == 0:
            raise EmptyDocumentError("No pages found in pdf-file")
    
    def __iter__(self):
        if len(self.__pages) > 0:
            set_log_level(self.debug_level)
            for page in self.__pages:
                yield page
            set_log_level(logging.WARNING)
        else:
            for page in self.__load_pages():
                yield page