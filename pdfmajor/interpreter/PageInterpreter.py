from pdfmajor.parser.PDFPage import PDFPage
from pdfmajor.parser.PDFStream import list_value
from pdfmajor.parser.PDFContentParser import PDFContentParser
from pdfmajor.parser.PSStackParser import PSKeyword
from pdfmajor.parser.PSStackParser import keyword_name

from .commands import PDFStateStack, PDFCommands
from .commands import LTXObject
from .utils import init_resources
from .XObjectInterpreter import XObjectInterpreter

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
        self.state: PDFStateStack = PDFStateStack()
        self.state.t_matrix = ctm
        self.state.resources = page.resources
        # set some global states.
        self.state.graphics.ncolspace = self.state.graphics.scolspace = None 
        if self.state.colorspace_map:
            col_space = next(iter(self.state.colorspace_map.values()))
            self.state.graphics.ncolspace = self.state.graphics.scolspace = col_space
        # Init Resources
        init_resources(self.state, self.font_cache)
    
    def __iter__(self):
        parser = PDFContentParser(list_value(self.page.contents))
        history = []
        for obj in parser:
            history.append(obj)
            if isinstance(obj, PSKeyword):
                name = keyword_name(obj)
                method = name.replace('*', '_a').replace('"', '_w').replace("'", '_q')
                if method in PDFCommands.commands.keys():
                    func = PDFCommands.commands.get(method)
                    nargs = func.__code__.co_argcount-1
                    if nargs:
                        args = self.state.pop(nargs)
                        if len(args) == nargs:
                            func(self.state, *args)
                        else:
                            raise self.PDFInterpreterError(f"Invalid Number of Args provided {method}")
                    else:
                        # log.debug('exec: %s', name)
                        func(self.state)
                else:
                    raise self.PDFInterpreterError('Unknown operator: %r' % name)
            else:
                self.state.argstack.append(obj)
            
            for complete_item in self.state.complete_layout_items:
                if isinstance(complete_item, LTXObject):
                    interpeter = XObjectInterpreter(
                        streams=[complete_item.stream],
                        resources=complete_item.resources,
                        ctm=complete_item.t_matrix
                    )
                    for item in interpeter:
                        complete_item.add(item)
                yield complete_item
            self.state.complete_layout_items = []
    def __repr__(self) -> str:
        return f"<Page:{self.page_num}/>"