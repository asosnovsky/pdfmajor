from pdfmajor.utils import MATRIX_IDENTITY
from pdfmajor.parser.PSStackParser import literal_name
from pdfmajor.parser.PDFParser import PDFStream
from pdfmajor.parser.PSStackParser import PSEOF
from pdfmajor.parser.PSStackParser import PSKeyword
from pdfmajor.parser.PSStackParser import keyword_name
from pdfmajor.parser.PSStackParser import PSStackParser
from pdfmajor.parser.constants import LITERAL_PDF, LITERAL_TEXT, LITERAL_FONT

from pdfmajor.parser.PDFStream import resolve1, list_value, dict_value
from pdfmajor.parser.PDFStream.PDFObjRef import PDFObjRef
from pdfmajor.parser.PDFContentParser import PDFContentParser

from .commands.state import PDFStateStack, PDFColorSpace, PREDEFINED_COLORSPACE
from .commands import PDFCommands, LTXObject
from .utils import init_resources

class XObjectInterpreter:

    class PDFInterpreterError(Exception): pass

    def __init__(self, streams, resources, ctm):
        self.streams = streams
        self.font_cache = {}
        
        self.state = PDFStateStack()
        self.state.t_matrix = ctm
        self.state.resources = resources

        # set some global states.
        self.state.graphics.ncolspace = self.state.graphics.scolspace = None 
        if self.state.colorspace_map:
            col_space = next(iter(self.state.colorspace_map.values()))
            self.state.graphics.ncolspace = self.state.graphics.scolspace = col_space
        init_resources(self.state, self.font_cache)
        
    def __iter__(self):
        parser = PDFContentParser(self.streams)
        for obj in parser:
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
                    interpeter = self.__class__(
                        streams=[complete_item.stream],
                        resources=complete_item.resources,
                        ctm=complete_item.t_matrix
                    )
                    for item in interpeter:
                        complete_item.add(item)
                yield complete_item
            self.state.complete_layout_items = []