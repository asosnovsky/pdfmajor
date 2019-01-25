from typing import List

from pdfmajor.parser.PDFContentParser import PDFContentParser, PDFStream
from pdfmajor.parser.PSStackParser import PSKeyword, keyword_name
from pdfmajor.utils import get_logger

from .commands import PDFCommands
from .state import PDFStateStack, PDFGraphicState, PDFTextState
from .state.PDFGraphicState import PDFColor, PDFColorSpace, PREDEFINED_COLORSPACE
from .state import PDFFont, get_font
from .state import LTTextBlock, LTCharBlock, LTChar
from .state import LTCurve, LTLine, LTHorizontalLine, LTVerticalLine, LTRect
from .state import LTImage
from .state import LTXObject
from .state import LTItem, LTComponent, LTContainer
from .utils import init_resources

log = get_logger('process_command_stream')

class CommandProcessorError(Exception): pass

def process_command_stream(streams: List[PDFStream], font_cache: dict = None, state: PDFStateStack = None):
    if font_cache is None:
        font_cache = {}
    parser = PDFContentParser(streams)
    # from .cmd_record import CmdRecord
    # history = CmdRecord()
    for obj in parser:
        if isinstance(obj, PSKeyword):
            name = keyword_name(obj)
            method = name.replace('*', '_a').replace('"', '_w').replace("'", '_q')
            func = None
            args = []
            if method == "Do":
                pass
            if method in PDFCommands.commands.keys():
                func = PDFCommands.commands.get(method)
                nargs = func.__code__.co_argcount-1
                if nargs:
                    args = state.pop(nargs)
                    if len(args) == nargs:
                        func(state, *args)
                    else:
                        raise CommandProcessorError(f"Invalid Number of Args provided {method}")
                else:
                    func(state)
            else:
                log.debug('Unknown operator: %r (i.e. %r)' % (name, method))
            # history.write(name, 
            #     None if func is None else func.__name__
            # , args)
        else:
            state.argstack.append(obj)
            # history.write('arg', None, obj)
        
        for complete_item in state.complete_layout_items:
            if isinstance(complete_item, LTXObject):
                xobj_state = prep_state(
                    state=PDFStateStack(),
                    ctm=complete_item.t_matrix,
                    resources=complete_item.resources,
                    font_cache=font_cache
                )
                xobj_state.graphics = state.graphics.copy()
                for item in process_command_stream(
                    [complete_item.stream], 
                    font_cache=font_cache, 
                    state=xobj_state
                ):
                    complete_item.add(item)
            yield complete_item
        state.complete_layout_items = []

def prep_state(state: PDFStateStack, ctm: tuple, resources: dict, font_cache: dict) -> PDFStateStack:
    state.t_matrix = ctm
    state.resources = resources

    # set some global states.
    state.graphics.ncolspace = state.graphics.scolspace = None 
    if state.colorspace_map:
        col_space = next(iter(state.colorspace_map.values()))
        state.graphics.ncolspace = state.graphics.scolspace = col_space
    init_resources(state, font_cache)
    return state