from pdfmajor.parser.PDFParser import PDFStream
from pdfmajor.parser.PDFStream import list_value, dict_value, resolve1
from pdfmajor.parser.PDFStream.PDFObjRef import PDFObjRef
from pdfmajor.parser.PSStackParser import literal_name
from pdfmajor.parser.constants import LITERAL_PDF, LITERAL_TEXT

from .state import PDFColorSpace, PREDEFINED_COLORSPACE
from .state import PDFStateStack, get_font

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

def get_procset(procs):
    for proc in procs:
        if proc is LITERAL_PDF:
            pass
        elif proc is LITERAL_TEXT:
            pass
        else:
            #raise PDFResourceError('ProcSet %r is not supported.' % proc)
            pass
    return

def init_resources(state: PDFStateStack, font_cache: dict = {}):
    for (k, v) in iter(dict_value(state.resources).items()):
        # log.debug('Resource: %r: %r', k, v)
        if k == 'Font':
            for (fontid, spec) in iter(dict_value(v).items()):
                objid = None
                if isinstance(spec, PDFObjRef):
                    objid = spec.objid
                spec = dict_value(spec)
                state.fontmap[fontid] = get_font(objid, spec, font_cache)
        elif k == 'ColorSpace':
            for (csid, spec) in iter(dict_value(v).items()):
                state.colorspace_map[csid] = get_colorspace(resolve1(spec))
        elif k == 'ProcSet':
            get_procset(list_value(v))
        elif k == 'XObject':
            for (xobjid, xobjstrm) in iter(dict_value(v).items()):
                state.xobjmap[xobjid] = xobjstrm