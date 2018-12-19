from pdfmajor.utils import MATRIX_IDENTITY
from pdfmajor.interpreter.PSStackParser import literal_name
from pdfmajor.interpreter.PSStackParser import PSEOF
from pdfmajor.interpreter.PSStackParser import PSKeyword
from pdfmajor.interpreter.PSStackParser import keyword_name
from pdfmajor.interpreter.PSStackParser import PSStackParser
from pdfmajor.interpreter.PDFParser import PDFStream

from pdfmajor.interpreter.PDFStream import resolve1, list_value, dict_value
from pdfmajor.interpreter.PDFStream.PDFObjRef import PDFObjRef
from pdfmajor.interpreter.PDFContentParser import PDFContentParser

from .commands.state import PDFStateStack, PDFColorSpace, PREDEFINED_COLORSPACE
from .commands import PDFCommands
from .commands.state.PDFItem import PDFXObject, PDFImage, PDFItem, PDFShape, PDFText

def get_colorspace(spec):
    if isinstance(spec, list):
        name = literal_name(spec[0])
    else:
        name = literal_name(spec)
    if name == 'ICCBased' and isinstance(spec, list) and 2 <= len(spec):
        return PDFColorSpace(name, PDFStream.validated_stream(spec[1])['N'])
    elif name == 'DeviceN' and isinstance(spec, list) and 2 <= len(spec):
        return PDFColorSpace(name, len(list_value(spec[1])))
    else:
        return PREDEFINED_COLORSPACE.get(name)

class PDFPageInterpreter:

    class PDFInterpreterError(Exception): pass

    def __init__(self, rsrcmgr):
        self.rsrcmgr = rsrcmgr
        self.state: PDFStateStack = PDFStateStack()
    
    # init_resources(resources):
    #   Prepare the fonts and XObjects listed in the Resource attribute.
    def init_resources(self, resources):
        self.state.resources = resources
        for (k, v) in iter(dict_value(self.state.resources).items()):
            # log.debug('Resource: %r: %r', k, v)
            if k == 'Font':
                for (fontid, spec) in iter(dict_value(v).items()):
                    objid = None
                    if isinstance(spec, PDFObjRef):
                        objid = spec.objid
                    spec = dict_value(spec)
                    self.state.fontmap[fontid] = self.rsrcmgr.get_font(objid, spec)
            elif k == 'ColorSpace':
                for (csid, spec) in iter(dict_value(v).items()):
                    self.state.colorspace_map[csid] = get_colorspace(resolve1(spec))
            elif k == 'ProcSet':
                self.rsrcmgr.get_procset(list_value(v))
            elif k == 'XObject':
                for (xobjid, xobjstrm) in iter(dict_value(v).items()):
                    self.state.xobjmap[xobjid] = xobjstrm
    

    # init_state(ctm)
    #   Initialize the text and graphic states for rendering a page.
    def init_state(self, ctm):
        self.state = PDFStateStack()
        self.state.t_matrix = ctm
        # set some global states.
        self.state.graphics.ncolor.color_space = self.state.graphics.scolor.color_space = None 
        if self.state.colorspace_map:
            col_space = next(iter(self.state.colorspace_map.values()))
            self.state.graphics.ncolor.color_space = self.state.graphics.scolor.color_space = col_space

    # render_contents(resources, streams, ctm)
    #   Render the content streams.
    #   This method may be called recursively.
    def render_contents(self, resources, streams, ctm=MATRIX_IDENTITY):
        self.init_state(ctm)
        self.init_resources(resources)
        return self.execute(list_value(streams))
    
    def process_page(self, page):
        (x0, y0, x1, y1) = page.mediabox
        if page.rotate == 90:
            ctm = [0, -1, 1, 0, -y0, x1]
        elif page.rotate == 180:
            ctm = [-1, 0, 0, -1, x1, y1]
        elif page.rotate == 270:
            ctm = [0, 1, -1, 0, y1, -x0]
        else:
            ctm = [1, 0, 0, 1, -x0, -y0]
        return self.render_contents(page.resources, page.contents, ctm=ctm)

    def execute(self, streams):
        parser = PDFContentParser(streams)
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
            
            for complete_item in self.state.complete_items:
                if isinstance(complete_item, PDFXObject):
                    interpeter = self.__class__(self.rsrcmgr)
                    for item in interpeter.render_contents(
                            streams=[complete_item.stream],
                            resources=complete_item.resources,
                            ctm=complete_item.ctm
                        ):
                        complete_item.children.append(item)
                yield complete_item
            self.state.complete_items = []