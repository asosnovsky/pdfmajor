# PDFFont
from abc import abstractmethod
from io import BytesIO

from pdfmajor.parser.EncodingDB import EncodingDB
from pdfmajor.parser.PSStackParser import LIT
from pdfmajor.parser.PSStackParser import PSLiteral
from pdfmajor.parser.PSStackParser import literal_name
from pdfmajor.parser.PDFStream import resolve1
from pdfmajor.parser.PDFStream import int_value
from pdfmajor.parser.PDFStream import num_value
from pdfmajor.parser.PDFStream import list_value
from pdfmajor.parser.PDFStream import PDFException
from pdfmajor.parser.PDFStream import PDFStream
from pdfmajor.parser.cmapdb import FileUnicodeMap
from pdfmajor.parser.cmapdb import CMapParser

##  Literals
##
LITERAL_STANDARD_ENCODING = LIT('StandardEncoding')
LITERAL_TYPE1C = LIT('Type1C')


class PDFFont(object):
    class PDFFontError(PDFException): pass
    class PDFUnicodeNotDefined(PDFFontError): pass

    def __init__(self, descriptor, widths, default_width=None):
        self.descriptor = descriptor
        self.widths = widths
        self.fontname = resolve1(descriptor.get('FontName', 'unknown'))
        if isinstance(self.fontname, PSLiteral):
            self.fontname = literal_name(self.fontname)
        self.flags = int_value(descriptor.get('Flags', 0))
        self.ascent = num_value(descriptor.get('Ascent', 0))
        self.descent = num_value(descriptor.get('Descent', 0))
        self.italic_angle = num_value(descriptor.get('ItalicAngle', 0))
        self.default_width = default_width or num_value(descriptor.get('MissingWidth', 0))
        self.leading = num_value(descriptor.get('Leading', 0))
        self.bbox = list_value(descriptor.get('FontBBox', (0, 0, 0, 0)))
        self.hscale = self.vscale = .001
        return

    def __repr__(self):
        return '<PDFFont>'

    def is_vertical(self):
        return False

    def is_multibyte(self):
        return False

    def decode(self, bytes):
        return bytearray(bytes)  # map(ord, bytes)

    def get_ascent(self):
        return self.ascent * self.vscale

    def get_descent(self):
        return self.descent * self.vscale

    def get_width(self):
        w = self.bbox[2]-self.bbox[0]
        if w == 0:
            w = -self.default_width
        return w * self.hscale

    def get_height(self):
        h = self.bbox[3]-self.bbox[1]
        if h == 0:
            h = self.ascent - self.descent
        return h * self.vscale

    def char_width(self, cid):
        try:
            return self.widths[cid] * self.hscale
        except KeyError:
            try:
                return self.widths[self.to_unichr(cid)] * self.hscale
            except (KeyError, self.PDFUnicodeNotDefined):
                return self.default_width * self.hscale

    def char_disp(self, cid):
        return 0

    def string_width(self, s):
        return sum(self.char_width(cid) for cid in self.decode(s))

    @abstractmethod
    def to_unichr(self, cid):
        raise NotImplementedError
    
    @property
    def font_weight(self):
        if 'FontWeight' in self.descriptor.keys():
            return self.descriptor['FontWeight']
        elif 'bold' in self.fontname.lower():
            return 'bold'
        else:
            return None
    
    @property
    def is_bold(self):
        return self.font_weight == 'bold' or self.font_weight > 549

# PDFSimpleFont
class PDFSimpleFont(PDFFont):

    def __init__(self, descriptor, widths, spec):
        # Font encoding is specified either by a name of
        # built-in encoding or a dictionary that describes
        # the differences.
        if 'Encoding' in spec:
            encoding = resolve1(spec['Encoding'])
        else:
            encoding = LITERAL_STANDARD_ENCODING
        if isinstance(encoding, dict):
            name = literal_name(encoding.get('BaseEncoding', LITERAL_STANDARD_ENCODING))
            diff = list_value(encoding.get('Differences', []))
            self.cid2unicode = EncodingDB.get_encoding(name, diff)
        else:
            self.cid2unicode = EncodingDB.get_encoding(literal_name(encoding))
        self.unicode_map = None
        if 'ToUnicode' in spec:
            strm = PDFStream.validated_stream(spec['ToUnicode'])
            self.unicode_map = FileUnicodeMap()
            CMapParser(self.unicode_map, BytesIO(strm.get_data())).run()
        PDFFont.__init__(self, descriptor, widths)
        return

    def to_unichr(self, cid):
        if self.unicode_map:
            try:
                return self.unicode_map.get_unichr(cid)
            except KeyError:
                pass
        try:
            return self.cid2unicode[cid]
        except KeyError:
            raise self.PDFUnicodeNotDefined(None, cid)
