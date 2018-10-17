import logging

log = logging.getLogger(__name__)

from io import TextIOWrapper
from typing import List, Tuple, Union
from ...utils import int2byte

from .exceptions import PSEOF
from .constants import EOL, NONSPC, KWD, END_LITERAL, LIT, HEX
from .constants import SPC, HEX_PAIR
from .constants import END_NUMBER, END_STRING, END_KEYWORD, END_HEX_STRING
from .constants import OCT_STRING, ESC_STRING, KEYWORD_DICT_BEGIN, KEYWORD_DICT_END
from .types import PSLiteral

class PSBaseParser(object):

    """Most basic PostScript parser that performs only tokenization.
    """
    BUFSIZ = 4096

    def __init__(self, fp: TextIOWrapper):
        self.fp = fp
        self.seek(0)
        return

    def __repr__(self):
        return '<%s: %r, bufpos=%d>' % (self.__class__.__name__, self.fp, self.bufpos)

    def flush(self):
        return

    def close(self):
        self.flush()
        return

    def tell(self):
        return self.bufpos+self.charpos

    def poll(self, pos=None, n=80):
        pos0 = self.fp.tell()
        if not pos:
            pos = self.bufpos+self.charpos
        self.fp.seek(pos)
        log.info('poll(%d): %r', pos, self.fp.read(n))
        self.fp.seek(pos0)
        return

    def seek(self, pos: int):
        """Seeks the parser to the given position.
        """
        log.debug('seek: %r', pos)
        self.fp.seek(pos)
        # reset the status for nextline()
        self.bufpos: int = pos
        self.buf: bytes = b''
        self.charpos: int = 0
        # reset the status for nexttoken()
        self._current_parse_func = self._parse_main
        self._curtoken: bytes = b''
        self._curtokenpos: int = 0
        self._tokens: List[Tuple[int, Union[int, float, bool, str, bytes, PSLiteral]]] = []
        return

    def fillbuf(self):
        if self.charpos < len(self.buf):
            return
        # fetch next chunk.
        self.bufpos = self.fp.tell()
        self.buf = self.fp.read(self.BUFSIZ)
        if not self.buf:
            raise PSEOF('Unexpected EOF')
        self.charpos = 0
        return

    def nextline(self):
        """Fetches a next line that ends either with \\r or \\n.
        """
        linebuf = b''
        linepos = self.bufpos + self.charpos
        eol = False
        while 1:
            self.fillbuf()
            if eol:
                c = self.buf[self.charpos:self.charpos+1]
                # handle b'\r\n'
                if c == b'\n':
                    linebuf += c
                    self.charpos += 1
                break
            m = EOL.search(self.buf, self.charpos)
            if m:
                linebuf += self.buf[self.charpos:m.end(0)]
                self.charpos = m.end(0)
                if linebuf[-1:] == b'\r':
                    eol = True
                else:
                    break
            else:
                linebuf += self.buf[self.charpos:]
                self.charpos = len(self.buf)
        log.debug('nextline: %r, %r', linepos, linebuf)

        return (linepos, linebuf)

    def revreadlines(self):
        """Fetches a next line backword.

        This is used to locate the trailers at the end of a file.
        """
        self.fp.seek(0, 2)
        pos = self.fp.tell()
        buf = b''
        while 0 < pos:
            prevpos = pos
            pos = max(0, pos-self.BUFSIZ)
            self.fp.seek(pos)
            s = self.fp.read(prevpos-pos)
            if not s:
                break
            while 1:
                n = max(s.rfind(b'\r'), s.rfind(b'\n'))
                if n == -1:
                    buf = s + buf
                    break
                yield s[n:] + buf
                s = s[:n]
                buf = b''
        return

    def _parse_main(self, s, i):
        m = NONSPC.search(s, i)
        if not m:
            return len(s)
        j = m.start(0)
        c = s[j:j+1]
        self._curtokenpos = self.bufpos+j
        if c == b'%':
            self._curtoken = b'%'
            self._current_parse_func = self._parse_comment
            return j+1
        elif c == b'/':
            self._curtoken = b''
            self._current_parse_func = self._parse_literal
            return j+1
        elif c in b'-+' or c.isdigit():
            self._curtoken = c
            self._current_parse_func = self._parse_number
            return j+1
        elif c == b'.':
            self._curtoken = c
            self._current_parse_func = self._parse_float
            return j+1
        elif c.isalpha():
            self._curtoken = c
            self._current_parse_func = self._parse_keyword
            return j+1
        elif c == b'(':
            self._curtoken = b''
            self.paren = 1
            self._current_parse_func = self._parse_string
            return j+1
        elif c == b'<':
            self._curtoken = b''
            self._current_parse_func = self._parse_wopen
            return j+1
        elif c == b'>':
            self._curtoken = b''
            self._current_parse_func = self._parse_wclose
            return j+1
        else:
            self._add_token(KWD(c))
            return j+1

    def _add_token(self, obj):
        self._tokens.append((self._curtokenpos, obj))
        return

    def _parse_comment(self, s, i):
        m = EOL.search(s, i)
        if not m:
            self._curtoken += s[i:]
            return len(s)
        j = m.start(0)
        self._curtoken += s[i:j]
        self._current_parse_func = self._parse_main
        # We ignore comments.
        #self._tokens.append(self._curtoken)
        return j

    def _parse_literal(self, s, i):
        m = END_LITERAL.search(s, i)
        if not m:
            self._curtoken += s[i:]
            return len(s)
        j = m.start(0)
        self._curtoken += s[i:j]
        c = s[j:j+1]
        if c == b'#':
            self.hex = b''
            self._current_parse_func = self._parse_literal_hex
            return j+1
        try:
            self._curtoken=str(self._curtoken,'utf-8')
        except:
            pass
        self._add_token(LIT(self._curtoken))
        self._current_parse_func = self._parse_main
        return j

    def _parse_literal_hex(self, s, i):
        c = s[i:i+1]
        if HEX.match(c) and len(self.hex) < 2:
            self.hex += c
            return i+1
        if self.hex:
            self._curtoken += int2byte(int(self.hex, 16))
        self._current_parse_func = self._parse_literal
        return i

    def _parse_number(self, s, i):
        m = END_NUMBER.search(s, i)
        if not m:
            self._curtoken += s[i:]
            return len(s)
        j = m.start(0)
        self._curtoken += s[i:j]
        c = s[j:j+1]
        if c == b'.':
            self._curtoken += c
            self._current_parse_func = self._parse_float
            return j+1
        try:
            self._add_token(int(self._curtoken))
        except ValueError:
            pass
        self._current_parse_func = self._parse_main
        return j

    def _parse_float(self, s, i):
        m = END_NUMBER.search(s, i)
        if not m:
            self._curtoken += s[i:]
            return len(s)
        j = m.start(0)
        self._curtoken += s[i:j]
        try:
            self._add_token(float(self._curtoken))
        except ValueError:
            pass
        self._current_parse_func = self._parse_main
        return j

    def _parse_keyword(self, s, i):
        m = END_KEYWORD.search(s, i)
        if not m:
            self._curtoken += s[i:]
            return len(s)
        j = m.start(0)
        self._curtoken += s[i:j]
        if self._curtoken == b'true':
            token = True
        elif self._curtoken == b'false':
            token = False
        else:
            token = KWD(self._curtoken)
        self._add_token(token)
        self._current_parse_func = self._parse_main
        return j

    def _parse_string(self, s, i):
        m = END_STRING.search(s, i)
        if not m:
            self._curtoken += s[i:]
            return len(s)
        j = m.start(0)
        self._curtoken += s[i:j]
        c = s[j:j+1]
        if c == b'\\':
            self.oct = b''
            self._current_parse_func = self._parse_string_1
            return j+1
        if c == b'(':
            self.paren += 1
            self._curtoken += c
            return j+1
        if c == b')':
            self.paren -= 1
            if self.paren:  # WTF, they said balanced parens need no special treatment.
                self._curtoken += c
                return j+1
        self._add_token(self._curtoken)
        self._current_parse_func = self._parse_main
        return j+1

    def _parse_string_1(self, s, i):
        c = s[i:i+1]
        if OCT_STRING.match(c) and len(self.oct) < 3:
            self.oct += c
            return i+1
        if self.oct:
            self._curtoken += int2byte(int(self.oct, 8))
            self._current_parse_func = self._parse_string
            return i
        if c in ESC_STRING:
            self._curtoken += int2byte(ESC_STRING[c])
        self._current_parse_func = self._parse_string
        return i+1

    def _parse_wopen(self, s, i):
        c = s[i:i+1]
        if c == b'<':
            self._add_token(KEYWORD_DICT_BEGIN)
            self._current_parse_func = self._parse_main
            i += 1
        else:
            self._current_parse_func = self._parse_hexstring
        return i

    def _parse_wclose(self, s, i):
        c = s[i:i+1]
        if c == b'>':
            self._add_token(KEYWORD_DICT_END)
            i += 1
        self._current_parse_func = self._parse_main
        return i

    def _parse_hexstring(self, s, i):
        m = END_HEX_STRING.search(s, i)
        if not m:
            self._curtoken += s[i:]
            return len(s)
        j = m.start(0)
        self._curtoken += s[i:j]
        token = HEX_PAIR.sub(lambda m: int2byte(int(m.group(0), 16)),SPC.sub(b'', self._curtoken))
        self._add_token(token)
        self._current_parse_func = self._parse_main
        return j

    def nexttoken(self):
        while not self._tokens:
            self.fillbuf()
            self.charpos = self._current_parse_func(self.buf, self.charpos)
        token = self._tokens.pop(0)
        log.debug('nexttoken: %r', token)
        return token
