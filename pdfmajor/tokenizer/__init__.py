import io
from pdfmajor.tokenizer.token_parsers.string import parse_string

from typing import Iterator, Optional

from pdfmajor.tokenizer.constants import NONSPC
from pdfmajor.tokenizer.exceptions import TokenizerEOF
from pdfmajor.tokenizer.token_parsers.keyword import parse_keyword
from pdfmajor.tokenizer.token_parsers.literal import parse_literal
from pdfmajor.tokenizer.token_parsers.number import parse_number
from pdfmajor.tokenizer.token_parsers.comment import parse_comment
from pdfmajor.tokenizer.token_parsers.util import PInput
from pdfmajor.tokenizer.token import Token, TokenKeyword


class PSTokenizer:
    def __init__(self, fp: io.BufferedIOBase, bufsize: int = 4096) -> None:
        self.fp = fp
        self.bufsize = bufsize
        self.bufpos: int = 0
        self.buf: bytes = b""
        self.buf_skipstep: Optional[int] = None

    def inc_buf_skipstep(self, value: int):
        if self.buf_skipstep is None:
            self.buf_skipstep = value
        else:
            self.buf_skipstep += value

    def iter_buffer(self) -> Iterator[PInput]:
        while True:
            if (self.buf_skipstep is not None) and (self.buf_skipstep < len(self.buf)):
                yield PInput(
                    self.bufpos + self.buf_skipstep, self.buf[self.buf_skipstep :]
                )
            else:
                self.buf_skipstep = None
                self.bufpos = self.fp.tell()
                self.buf = self.fp.read(self.bufsize)
                if not self.buf:
                    raise TokenizerEOF("Unexpected EOF")
                else:
                    yield PInput(self.bufpos, self.buf)

    def seek(self, pos: int):
        self.fp.seek(pos)

    def step_back(self, steps: int = 1):
        """Changes the offset of the stream some steps back (each step is equal to 1 self.bufsize)

        Args:
                steps (int, optional): numbers of steps. Defaults to 1.
        """
        self.fp.seek(self.fp.tell() - steps * self.bufsize)

    def iter_tokens(self) -> Iterator[Token]:
        for cur in self.iter_buffer():
            bufpos, buf = cur
            m = NONSPC.search(buf, 0)
            if not m:
                self.buf_skipstep = None
                continue
            else:
                j = m.start(0)
                c = buf[j : j + 1]
                if c == b"%":
                    self.inc_buf_skipstep(j + 1)
                    yield self._check_token(
                        cur, parse_comment(bufpos + j, self.iter_buffer())
                    )
                elif c == b"/":
                    self.inc_buf_skipstep(j + 1)
                    yield self._check_token(
                        cur, parse_literal(bufpos + j, self.iter_buffer())
                    )
                elif c in b"-+":
                    self.inc_buf_skipstep(j + 1)
                    yield self._check_token(
                        cur, parse_number(bufpos + j, self.iter_buffer(), c)
                    )
                elif c.isdigit():
                    self.inc_buf_skipstep(j)
                    yield self._check_token(
                        cur, parse_number(bufpos + j, self.iter_buffer())
                    )
                elif c == b".":
                    self.inc_buf_skipstep(j)
                    yield self._check_token(
                        cur, parse_number(bufpos + j, self.iter_buffer())
                    )
                elif c.isalpha():
                    self.inc_buf_skipstep(j)
                    yield self._check_token(
                        cur, parse_keyword(bufpos + j, self.iter_buffer())
                    )
                elif c == b"(":
                    self.inc_buf_skipstep(j + 1)
                    yield self._check_token(
                        cur, parse_string(bufpos + j, self.iter_buffer())
                    )
                elif c == b"<":
                    raise NotImplementedError
                    # self._curtoken = b""
                    # self._current_parse_func = self._parse_wopen
                    # return j + 1
                elif c == b">":
                    raise NotImplementedError
                    # self._curtoken = b""
                    # self._current_parse_func = self._parse_wclose
                    # return j + 1
                else:
                    self.inc_buf_skipstep(j + 1)
                    yield self._check_token(cur, TokenKeyword(bufpos + j, 1, c))

    def _check_token(self, cur: PInput, token: Token) -> Token:
        self.inc_buf_skipstep(token.size)
        return token
