from pdfmajor.parser.PDFPage import PDFPage
from pdfmajor.parser.PDFStream import list_value

from .commands import PDFStateStack
from .commands import process_command_stream, prep_state

class PageInterpreter:
    class PDFInterpreterError(Exception): pass

    def __init__(self, page: PDFPage, page_num: int, font_cache: dict = {}):
        (x0, y0, x1, y1) = page.mediabox
        if page.rotate == 90:
            ctm = [0, -1, 1, 0, -y0, x1]
        elif page.rotate == 180:
            ctm = [-1, 0, 0, -1, x1, y1]
        elif page.rotate == 270:
            ctm = [0, 1, -1, 0, y1, -x0]
        else:
            ctm = [1, 0, 0, 1, -x0, -y0]

        # Locals
        self.font_cache = font_cache
        self.page = page
        self.page_num = page_num
        self.height = y1-y0
        self.width = x1-x0

        # Init State
        self.state: PDFStateStack = prep_state(
            PDFStateStack(), 
            ctm=ctm, 
            resources=page.resources, 
            font_cache=self.font_cache
        )

    
    def __iter__(self):
        for item in process_command_stream(
            streams=list_value(self.page.contents),
            font_cache=self.font_cache,
            state=self.state
        ):
            yield item

    def __repr__(self) -> str:
        return f"<Page:{self.page_num} width={self.width} height={self.height}/>"