import io
from typing import Iterator
from pdfmajor.lexer.dict_and_hex import parse_double_angled_bracket
from pdfmajor.lexer.string import parse_string
from pdfmajor.lexer.keyword import parse_keyword
from pdfmajor.lexer.number import parse_number
from pdfmajor.lexer.name import parse_name
from pdfmajor.lexer.comment import parse_comment
from pdfmajor.lexer.regex import NONSPC
from pdfmajor.lexer.token import (
    TArrayValue,
    TDictValue,
    Token,
    TokenDictionary,
    TokenKeyword,
    TokenArray,
)
from pdfmajor.streambuffer import BufferStream


class PDFLexer:
    def __init__(self, buffer: BufferStream) -> None:
        self.buffer = buffer

    @classmethod
    def from_iobuffer(cls, fp: io.BufferedIOBase, buffer_size: int = 4096):
        return cls(BufferStream(fp, buffer_size=buffer_size))

    @classmethod
    def from_bytes(cls, data: bytes, buffer_size: int = 4096):
        return cls(BufferStream(io.BytesIO(data), buffer_size=buffer_size))

    def tell(self) -> int:
        return self.buffer.tell()

    def seek(self, pos: int) -> int:
        """moves the offset of the reader to a certain spot, and returns the new offset

        Args:
            offset (int)

        Returns:
            int: new offset
        """
        return self.buffer.seek(pos)

    def iter_tokens(self) -> Iterator[Token]:
        """Iterates over the tokens in the stream

        Yields:
            Iterator[Token]
        """
        for bufpos, buf in self.buffer:
            m = NONSPC.search(buf, 0)
            if not m:
                self.buf_skipstep = None
                continue
            else:
                j = m.start(0)
                next_char = buf[j : j + 1]
                if next_char == b"%":
                    self.buffer.seek(bufpos + j + 1)
                    yield parse_comment(self.buffer)
                elif next_char == b"/":
                    self.buffer.seek(bufpos + j + 1)
                    yield parse_name(self.buffer)
                elif next_char in b"-+":
                    self.buffer.seek(bufpos + j + 1)
                    yield parse_number(self.buffer, next_char)
                elif next_char.isdigit() or next_char == b".":
                    self.buffer.seek(bufpos + j)
                    yield parse_number(self.buffer, initialpos=self.buffer.tell())
                elif next_char.isalpha():
                    self.buffer.seek(bufpos + j)
                    yield parse_keyword(self.buffer, self.buffer.tell())
                elif next_char == b"(":
                    self.buffer.seek(bufpos + j + 1)
                    yield parse_string(self.buffer)
                elif next_char == b"<":
                    self.buffer.seek(bufpos + j + 1)
                    yield parse_double_angled_bracket(self.buffer)
                elif next_char == b">":
                    self.buffer.seek(bufpos + j + 1)
                    if buf[j : j + 2] == b">>":
                        self.buffer.seekd(1)
                        yield TokenDictionary(
                            bufpos + j, bufpos + j + 2, TDictValue.CLOSE
                        )
                elif next_char == b"[":
                    self.buffer.seek(bufpos + j + 1)
                    yield TokenArray(bufpos + j, bufpos + j + 1, TArrayValue.OPEN)
                elif next_char == b"]":
                    self.buffer.seek(bufpos + j + 1)
                    yield TokenArray(bufpos + j, bufpos + j + 1, TArrayValue.CLOSE)
                else:
                    self.buffer.seek(bufpos + j + 1)
                    yield TokenKeyword(bufpos + j, bufpos + j + 1, next_char)
