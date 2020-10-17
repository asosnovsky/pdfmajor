from pdfmajor.safebufiterator import BufferStream
from pdfmajor.lexer.exceptions import LexerEOF
from pdfmajor.lexer.token import TokenBoolean, TokenKeyword
from pdfmajor.lexer.regex import END_KEYWORD
from typing import Union


def parse_keyword(buffer: BufferStream) -> Union[TokenKeyword, TokenBoolean]:
    """Parses input stream into a keyword or bool

    Args:
        buffer (BufferStream)

    Returns:
        Union[TokenKeyword, TokenBoolean]
    """
    curtoken = b""
    initialpos = buffer.tell() - 1
    for pos, buf in buffer:
        m = END_KEYWORD.search(buf, 0)
        if not m:
            curtoken += buf
        else:
            j = m.start(0)
            curtoken += buf[:j]
            buffer.seek(pos + j)
            if curtoken == b"true":
                return TokenBoolean(initialpos, buffer.tell(), True)
            elif curtoken == b"false":
                return TokenBoolean(initialpos, buffer.tell(), False)
            else:
                return TokenKeyword(initialpos, buffer.tell(), curtoken)
    raise LexerEOF
