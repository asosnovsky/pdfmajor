from io import BytesIO

from pdfmajor.parser.PSStackParser import literal_name
from pdfmajor.parser.PDFStream import int_value
from pdfmajor.parser.PDFStream import num_value
from pdfmajor.parser.PDFStream import list_value
from pdfmajor.parser.PDFStream import dict_value
from pdfmajor.parser.PDFStream import PDFStream
from pdfmajor.parser.PDFStream import resolve1
from pdfmajor.parser.cmapdb import CMap, CMapDB, CMapParser
from pdfmajor.parser.cmapdb import FileUnicodeMap
from pdfmajor.utils import settings, apply_matrix_norm

from .PDFFont import PDFFont, PDFSimpleFont
from .util import FontMetricsDB, get_widths, get_widths2
from .Type1FontHeaderParser import Type1FontHeaderParser
from .TrueTypeFont import TrueTypeFont

# PDFType1Font
class PDFType1Font(PDFSimpleFont):

    def __init__(self, spec):
        try:
            self.basefont = literal_name(spec['BaseFont'])
        except KeyError:
            if settings.STRICT:
                raise self.PDFFontError('BaseFont is missing')
            self.basefont = 'unknown'
        try:
            (descriptor, widths) = FontMetricsDB.get_metrics(self.basefont)
        except KeyError:
            descriptor = dict_value(spec.get('FontDescriptor', {}))
            firstchar = int_value(spec.get('FirstChar', 0))
            #lastchar = int_value(spec.get('LastChar', 255))
            widths = list_value(spec.get('Widths', [0]*256))
            widths = dict((i+firstchar, w) for (i, w) in enumerate(widths))
        PDFSimpleFont.__init__(self, descriptor, widths, spec)
        if 'Encoding' not in spec and 'FontFile' in descriptor:
            # try to recover the missing encoding info from the font file.
            self.fontfile = PDFStream.validated_stream(descriptor.get('FontFile'))
            length1 = int_value(self.fontfile['Length1'])
            data = self.fontfile.get_data()[:length1]
            parser = Type1FontHeaderParser(BytesIO(data))
            self.cid2unicode = parser.get_encoding()
        return

    def __repr__(self):
        return '<PDFType1Font: basefont=%r>' % self.basefont


# PDFTrueTypeFont
class PDFTrueTypeFont(PDFType1Font):

    def __repr__(self):
        return '<PDFTrueTypeFont: basefont=%r>' % self.basefont


# PDFType3Font
class PDFType3Font(PDFSimpleFont):

    def __init__(self, spec):
        firstchar = int_value(spec.get('FirstChar', 0))
        #lastchar = int_value(spec.get('LastChar', 0))
        widths = list_value(spec.get('Widths', [0]*256))
        widths = dict((i+firstchar, w) for (i, w) in enumerate(widths))
        if 'FontDescriptor' in spec:
            descriptor = dict_value(spec['FontDescriptor'])
        else:
            descriptor = {'Ascent': 0, 'Descent': 0,
                          'FontBBox': spec['FontBBox']}
        PDFSimpleFont.__init__(self, descriptor, widths, spec)
        self.matrix = tuple(list_value(spec.get('FontMatrix')))
        (_, self.descent, _, self.ascent) = self.bbox
        (self.hscale, self.vscale) = apply_matrix_norm(self.matrix, (1, 1))
        return

    def __repr__(self):
        return '<PDFType3Font>'


# PDFCIDFont
class PDFCIDFont(PDFFont):

    def __init__(self, spec, strict=settings.STRICT):
        try:
            self.basefont = literal_name(spec['BaseFont'])
        except KeyError:
            if strict:
                raise self.PDFFontError('BaseFont is missing')
            self.basefont = 'unknown'
        self.cidsysteminfo = dict_value(spec.get('CIDSystemInfo', {}))
        self.cidcoding = '%s-%s' % (resolve1(self.cidsysteminfo.get('Registry', b'unknown')).decode("latin1"),
                                    resolve1(self.cidsysteminfo.get('Ordering', b'unknown')).decode("latin1"))
        try:
            name = literal_name(spec['Encoding'])
        except KeyError:
            if strict:
                raise self.PDFFontError('Encoding is unspecified')
            name = 'unknown'
        try:
            self.cmap = CMapDB.get_cmap(name)
        except CMapDB.CMapNotFound as e:
            if strict:
                raise self.PDFFontError(e)
            self.cmap = CMap()
        try:
            descriptor = dict_value(spec['FontDescriptor'])
        except KeyError:
            if strict:
                raise self.PDFFontError('FontDescriptor is missing')
            descriptor = {}
        ttf = None
        if 'FontFile2' in descriptor:
            self.fontfile = PDFStream.validated_stream(descriptor.get('FontFile2'))
            ttf = TrueTypeFont(self.basefont,
                               BytesIO(self.fontfile.get_data()))
        self.unicode_map = None
        if 'ToUnicode' in spec:
            strm = PDFStream.validated_stream(spec['ToUnicode'])
            self.unicode_map = FileUnicodeMap()
            CMapParser(self.unicode_map, BytesIO(strm.get_data())).run()
        elif self.cidcoding in ('Adobe-Identity', 'Adobe-UCS'):
            if ttf:
                try:
                    self.unicode_map = ttf.create_unicode_map()
                except TrueTypeFont.CMapNotFound:
                    pass
        else:
            try:
                self.unicode_map = CMapDB.get_unicode_map(self.cidcoding, self.cmap.is_vertical())
            except CMapDB.CMapNotFound as e:
                pass

        self.vertical = self.cmap.is_vertical()
        if self.vertical:
            # writing mode: vertical
            widths = get_widths2(list_value(spec.get('W2', [])))
            self.disps = dict((cid, (vx, vy)) for (cid, (_, (vx, vy))) in iter(widths.items()))
            (vy, w) = spec.get('DW2', [880, -1000])
            self.default_disp = (None, vy)
            widths = dict((cid, w) for (cid, (w, _)) in iter(widths.items()))
            default_width = w
        else:
            # writing mode: horizontal
            self.disps = {}
            self.default_disp = 0
            widths = get_widths(list_value(spec.get('W', [])))
            default_width = spec.get('DW', 1000)
        PDFFont.__init__(self, descriptor, widths, default_width=default_width)
        return

    def __repr__(self):
        return '<PDFCIDFont: basefont=%r, cidcoding=%r>' % (self.basefont, self.cidcoding)

    def is_vertical(self):
        return self.vertical

    def is_multibyte(self):
        return True

    def decode(self, bytes):
        return self.cmap.decode(bytes)

    def char_disp(self, cid):
        "Returns an integer for horizontal fonts, a tuple for vertical fonts."
        return self.disps.get(cid, self.default_disp)

    def to_unichr(self, cid):
        try:
            if not self.unicode_map:
                raise KeyError(cid)
            return self.unicode_map.get_unichr(cid)
        except KeyError:
            raise self.PDFUnicodeNotDefined(self.cidcoding, cid)
