import io
from typing import List
from pdfmajor.tokenizer.token import Token
from pdfmajor.tokenizer.exceptions import TokenizerEOF
from pdfmajor.tokenizer.parse_funcs import ParseFunc


class PSTokenizer:
    def __init__(self, fp: io.BufferedIOBase) -> None:
        self.fp = fp
        self.seek(0)

    def seek(self, pos: int):
        """Seeks tokenizer to the given position."""
        self.fp.seek(pos)
        # reset the status for nextline()
        self.bufpos: int = pos
        self.buf: bytes = b""
        self.charpos: int = 0
        # reset the status for nexttoken()
        self._current_parse_func: ParseFunc = self._parse_main
        self._curtoken: bytes = b""
        self._curtokenpos: int = 0
        self._tokens: List[Token] = []
        return

    def __repr__(self):
        return "<%s: %r, bufpos=%d>" % (self.__class__.__name__, self.fp, self.bufpos)

    def nexttoken(self):
        while not self._tokens:
            self.fillbuf()
            self.charpos = self._current_parse_func(self.buf, self.charpos)
        token = self._tokens.pop(0)
        return token

    def fillbuf(self):
        if self.charpos < len(self.buf):
            return
        # fetch next chunk.
        self.bufpos = self.fp.tell()
        self.buf = self.fp.read(self.BUFSIZ)
        if not self.buf:
            raise TokenizerEOF("Unexpected EOF")
        self.charpos = 0
        return
