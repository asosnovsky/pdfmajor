from pdfmajor.utils import get_logger, settings
from pdfmajor.parser.PSStackParser import literal_name
from pdfmajor.parser.PDFStream import list_value
from pdfmajor.parser.PDFStream import dict_value
from pdfmajor.parser.PDFStream import resolve1
from pdfmajor.parser.constants import LITERAL_FONT

from .fonts import PDFType1Font, PDFTrueTypeFont, PDFType3Font, PDFCIDFont, PDFFont

log = get_logger(__file__)

def get_font(objid: int, spec: dict, cached_fonts: dict = {}):
    if objid and objid in cached_fonts:
        font = cached_fonts[objid]
    else:
        log.debug('get_font: create: objid=%r, spec=%r', objid, spec)
        if settings.STRICT:
            if spec['Type'] is not LITERAL_FONT:
                raise PDFFont.PDFFontError('Type is not /Font')
        # Create a Font object.
        if 'Subtype' in spec:
            subtype = literal_name(spec['Subtype'])
        else:
            if settings.STRICT:
                raise PDFFont.PDFFontError('Font Subtype is not specified.')
            subtype = 'Type1'
        if subtype in ('Type1', 'MMType1'):
            # Type1 Font
            font = PDFType1Font(spec)
        elif subtype == 'TrueType':
            # TrueType Font
            font = PDFTrueTypeFont(spec)
        elif subtype == 'Type3':
            # Type3 Font
            font = PDFType3Font(spec)
        elif subtype in ('CIDFontType0', 'CIDFontType2'):
            # CID Font
            font = PDFCIDFont(spec)
        elif subtype == 'Type0':
            # Type0 Font
            dfonts = list_value(spec['DescendantFonts'])
            assert dfonts
            subspec = dict_value(dfonts[0]).copy()
            for k in ('Encoding', 'ToUnicode'):
                if k in spec:
                    subspec[k] = resolve1(spec[k])
            font = get_font(None, subspec, cached_fonts)
        else:
            if settings.STRICT:
                raise PDFFont.PDFFontError('Invalid Font spec: %r' % spec)
            font = PDFType1Font(spec)  # this is so wrong!
        if objid:
            cached_fonts[objid] = font
    return font



