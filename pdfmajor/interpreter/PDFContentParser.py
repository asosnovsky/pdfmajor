import re
import operator

from typing import List
from io import BytesIO

from ..utils import int2byte, choplist, settings

from .PSStackParser import literal_name
from .PSStackParser import PSStackParser
from .PSStackParser import PSEOF, PSTypeError
from .PSStackParser import KWD

from .PDFStream import PDFStream

class PDFContentParser(PSStackParser):

    def __init__(self, streams: List[PDFStream]):
        self.streams = streams
        self.istream = 0
        PSStackParser.__init__(self, None)
        return

    def fillfp(self):
        if not self.fp:
            if self.istream < len(self.streams):
                strm = PDFStream.validated_stream(self.streams[self.istream])
                self.istream += 1
            else:
                raise PSEOF('Unexpected EOF, file truncated?')
            self.fp = BytesIO(strm.get_data())
        return

    def seek(self, pos):
        self.fillfp()
        PSStackParser.seek(self, pos)
        return

    def fillbuf(self):
        if self.charpos < len(self.buf):
            return
        while 1:
            self.fillfp()
            self.bufpos = self.fp.tell()
            self.buf = self.fp.read(self.BUFSIZ)
            if self.buf:
                break
            self.fp = None
        self.charpos = 0
        return

    def get_inline_data(self, pos, target=b'EI'):
        self.seek(pos)
        i = 0
        data = b''
        while i <= len(target):
            self.fillbuf()
            if i:
                c = operator.getitem(self.buf,self.charpos)
                c = int2byte(c)
                data += c
                self.charpos += 1
                if len(target) <= i and c.isspace():
                    i += 1
                elif i < len(target) and c == (int2byte(target[i])):
                    i += 1
                else:
                    i = 0
            else:
                try:
                    j = self.buf.index(target[0], self.charpos)
                    data += self.buf[self.charpos:j+1]
                    self.charpos = j+1
                    i = 1
                except ValueError:
                    data += self.buf[self.charpos:]
                    self.charpos = len(self.buf)
        data = data[:-(len(target)+1)]  # strip the last part
        data = re.sub(br'(\x0d\x0a|[\x0d\x0a])$', b'', data)
        return (pos, data)

    def flush(self):
        self.add_results(*self.popall())
        return

    KEYWORD_BI = KWD(b'BI')
    KEYWORD_ID = KWD(b'ID')
    KEYWORD_EI = KWD(b'EI')

    def do_keyword(self, pos, token):
        if token is self.KEYWORD_BI:
            # inline image within a content stream
            self.start_type(pos, 'inline')
        elif token is self.KEYWORD_ID:
            try:
                (_, objs) = self.end_type('inline')
                if len(objs) % 2 != 0:
                    raise PSTypeError('Invalid dictionary construct: %r' % objs)
                d = dict((literal_name(k), v) for (k, v) in choplist(2, objs))
                (pos, data) = self.get_inline_data(pos+len(b'ID '))
                obj = PDFStream(d, data)
                self.push((pos, obj))
                self.push((pos, self.KEYWORD_EI))
            except PSTypeError:
                if settings.STRICT:
                    raise
        else:
            self.push((pos, token))
        return
