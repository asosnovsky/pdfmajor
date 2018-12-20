from pdfmajor.parser.PSStackParser import PSStackParser
from pdfmajor.parser.PSStackParser import PSEOF, KWD
from pdfmajor.parser.PSStackParser import PSLiteral
from pdfmajor.parser.PSStackParser import literal_name
from pdfmajor.parser.EncodingDB import name2unicode

##  Type1FontHeaderParser
##
class Type1FontHeaderParser(PSStackParser):

    KEYWORD_BEGIN = KWD(b'begin')
    KEYWORD_END = KWD(b'end')
    KEYWORD_DEF = KWD(b'def')
    KEYWORD_PUT = KWD(b'put')
    KEYWORD_DICT = KWD(b'dict')
    KEYWORD_ARRAY = KWD(b'array')
    KEYWORD_READONLY = KWD(b'readonly')
    KEYWORD_FOR = KWD(b'for')
    KEYWORD_FOR = KWD(b'for')

    def __init__(self, data):
        PSStackParser.__init__(self, data)
        self._cid2unicode = {}
        return

    def get_encoding(self):
        while 1:
            try:
                (cid, name) = self.nextobject()
            except PSEOF:
                break
            try:
                self._cid2unicode[cid] = name2unicode(name)
            except KeyError:
                pass
        return self._cid2unicode

    def do_keyword(self, pos, token):
        if token is self.KEYWORD_PUT:
            ((_, key), (_, value)) = self.pop(2) # pylint: disable=E0632
            if (isinstance(key, int) and
                isinstance(value, PSLiteral)):
                self.add_results((key, literal_name(value)))
        return

