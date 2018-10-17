import logging

from .cmapdb import CMapDB, CMap

from .PDFFont import PDFFontError
from .PDFFont import PDFType1Font
from .PDFFont import PDFTrueTypeFont
from .PDFFont import PDFType3Font
from .PDFFont import PDFCIDFont

from .PDFStream import PDFException
from .PDFStream import resolve1, dict_value, list_value
from .constants import LITERAL_PDF, LITERAL_TEXT, LITERAL_FONT
from .PSStackParser import literal_name, settings

log = logging.getLogger(__name__)

##  Exceptions
##
class PDFResourceError(PDFException):
    pass

class PDFInterpreterError(PDFException):
    pass

##  Resource Manager
##
class PDFResourceManager(object):

    """Repository of shared resources.

    ResourceManager facilitates reuse of shared resources
    such as fonts and images so that large objects are not
    allocated multiple times.
    """

    def __init__(self, caching=True):
        self.caching = caching
        self._cached_fonts = {}
        return

    def get_procset(self, procs):
        for proc in procs:
            if proc is LITERAL_PDF:
                pass
            elif proc is LITERAL_TEXT:
                pass
            else:
                #raise PDFResourceError('ProcSet %r is not supported.' % proc)
                pass
        return

    def get_cmap(self, cmapname, strict=False):
        try:
            return CMapDB.get_cmap(cmapname)
        except CMapDB.CMapNotFound:
            if strict:
                raise
            return CMap()

    def get_font(self, objid: int, spec: dict):
        if objid and objid in self._cached_fonts:
            font = self._cached_fonts[objid]
        else:
            log.info('get_font: create: objid=%r, spec=%r', objid, spec)
            if settings.STRICT:
                if spec['Type'] is not LITERAL_FONT:
                    raise PDFFontError('Type is not /Font')
            # Create a Font object.
            if 'Subtype' in spec:
                subtype = literal_name(spec['Subtype'])
            else:
                if settings.STRICT:
                    raise PDFFontError('Font Subtype is not specified.')
                subtype = 'Type1'
            if subtype in ('Type1', 'MMType1'):
                # Type1 Font
                font = PDFType1Font(self, spec)
            elif subtype == 'TrueType':
                # TrueType Font
                font = PDFTrueTypeFont(self, spec)
            elif subtype == 'Type3':
                # Type3 Font
                font = PDFType3Font(self, spec)
            elif subtype in ('CIDFontType0', 'CIDFontType2'):
                # CID Font
                font = PDFCIDFont(self, spec)
            elif subtype == 'Type0':
                # Type0 Font
                dfonts = list_value(spec['DescendantFonts'])
                assert dfonts
                subspec = dict_value(dfonts[0]).copy()
                for k in ('Encoding', 'ToUnicode'):
                    if k in spec:
                        subspec[k] = resolve1(spec[k])
                font = self.get_font(None, subspec)
            else:
                if settings.STRICT:
                    raise PDFFontError('Invalid Font spec: %r' % spec)
                font = PDFType1Font(self, spec)  # this is so wrong!
            if objid and self.caching:
                self._cached_fonts[objid] = font
        return font
