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


def iter_tokens(buffer: BufferStream) -> Iterator[Token]:
    """Iterates over the tokens in the stream

    Yields:
        Iterator[Token]
    """
    for bufpos, buf in buffer:
        m = NONSPC.search(buf, 0)
        if not m:
            continue
        else:
            j = m.start(0)
            next_char = buf[j : j + 1]
            if next_char == b"~":
                continue
            elif next_char == b"%":
                buffer.seek(bufpos + j + 1)
                yield parse_comment(buffer)
            elif next_char == b"/":
                buffer.seek(bufpos + j + 1)
                yield parse_name(buffer)
            elif next_char in b"-+":
                buffer.seek(bufpos + j + 1)
                yield parse_number(buffer, next_char)
            elif next_char.isdigit() or next_char == b".":
                buffer.seek(bufpos + j)
                yield parse_number(buffer, initialpos=buffer.tell())
            elif next_char.isalpha():
                buffer.seek(bufpos + j)
                yield parse_keyword(buffer, buffer.tell())
            elif next_char == b"(":
                buffer.seek(bufpos + j + 1)
                yield parse_string(buffer)
            elif next_char == b"<":
                buffer.seek(bufpos + j + 1)
                yield parse_double_angled_bracket(buffer)
            elif next_char == b">":
                buffer.seek(bufpos + j + 1)
                if buf[j : j + 2] == b">>":
                    buffer.seekd(1)
                    yield TokenDictionary(bufpos + j, bufpos + j + 2, TDictValue.CLOSE)
            elif next_char == b"[":
                buffer.seek(bufpos + j + 1)
                yield TokenArray(bufpos + j, bufpos + j + 1, TArrayValue.OPEN)
            elif next_char == b"]":
                buffer.seek(bufpos + j + 1)
                yield TokenArray(bufpos + j, bufpos + j + 1, TArrayValue.CLOSE)
            else:
                buffer.seek(bufpos + j + 1)
                yield TokenKeyword(bufpos + j, bufpos + j + 1, next_char)
