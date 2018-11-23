import re
import os

from typing import List
from io import BytesIO, StringIO, TextIOWrapper

from tqdm import tqdm

from ..layouts import PDFLayoutAnalyzer
from ..interpreter.PDFResourceManager import PDFResourceManager
from ..interpreter.PDFPage import PDFPage
from ..interpreter.PDFPageInterpreter import PDFPageInterpreter
from ..imagewriter import ImageWriter
from ..utils import set_log_level, get_logger, logging

log = get_logger(__name__)

##  PDFConverter
##
class PDFConverter(PDFLayoutAnalyzer):

    @classmethod
    def parse_file(cls, 
        input_file: TextIOWrapper, 
        output_file: TextIOWrapper, 
        image_folder_path: str = None,
        codec: str = 'utf-8',
        maxpages: int = 0, 
        password: str = None, 
        caching: bool = True, 
        check_extractable: bool = True,
        pagenos: List[int] = None,
        dont_export_images: bool = False,
        debug_level: int = logging.WARNING, 
    ) -> TextIOWrapper:
        
        set_log_level(debug_level)
        
        if dont_export_images:
            image_folder_path = None

        if not dont_export_images and image_folder_path is None and output_file.name is not None:
            image_folder_path = os.path.dirname(output_file.name)

        log.debug("Creating resources....")
        rsrcmgr = PDFResourceManager(caching=caching)
        imagewriter=ImageWriter(image_folder_path)
        device = cls(
            rsrcmgr, 
            output_file,
            codec=codec,
            imagewriter=imagewriter
        )
        interpreter = PDFPageInterpreter(rsrcmgr, device)
        log.debug("Reading pages....")
        pages = PDFPage.get_pages(input_file, pagenos=pagenos, maxpages=maxpages, password=password, caching=caching, check_extractable=check_extractable)
        
        page_waiter = tqdm(enumerate(pages), disable=debug_level > logging.INFO)
        for _, page in page_waiter:
            page_waiter.set_description("Processing pdf...")
            interpreter.process_page(page)   
        page_waiter.close() 
        device.close()
        return output_file
        
    def __init__(self, rsrcmgr: PDFResourceManager, outfp: TextIOWrapper, imagewriter: ImageWriter, codec: str='utf-8', pageno: int=1):
        PDFLayoutAnalyzer.__init__(self, rsrcmgr, pageno=pageno)
        self.imagewriter = imagewriter
        self.outfp = outfp
        self.codec = codec
        if hasattr(self.outfp, 'mode'):
            if 'b' in self.outfp.mode:
                self.outfp_binary = True
            else:
                self.outfp_binary = False
        else:
            if isinstance(self.outfp, BytesIO):
                self.outfp_binary = True
            elif isinstance(self.outfp, StringIO):
                self.outfp_binary = False
            else:
                try:
                    self.outfp.write(u"é")
                    self.outfp_binary = False
                except TypeError:
                    self.outfp_binary = True
        return
