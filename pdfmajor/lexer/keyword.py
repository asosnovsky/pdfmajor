from pdfmajor.streambuffer import BufferStream
from pdfmajor.lexer.exceptions import LexerEOF
from pdfmajor.lexer.token import (
    TObjValue,
    TStreamValue,
    Token,
    TokenBoolean,
    TokenKeyword,
    TokenNull,
    TokenObj,
    TokenStream,
)
from pdfmajor.lexer.regex import END_KEYWORD
from typing import Optional, Union


def parse_keyword(buffer: BufferStream, initialpos: Optional[int] = None) -> Token:
    """Parses input stream into a keyword or bool

    Args:
        buffer (BufferStream)
        initialpos (Optional[int])

    Returns:
        Token
    """
    curtoken = b""
    initialpos = buffer.tell() - 1 if initialpos is None else initialpos
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
            elif curtoken == b"null":
                return TokenNull(initialpos, buffer.tell(), None)
            elif curtoken == b"stream":
                return TokenStream(initialpos, buffer.tell(), TStreamValue.START)
            elif curtoken == b"endstream":
                return TokenStream(initialpos, buffer.tell(), TStreamValue.END)
            elif curtoken == b"obj":
                return TokenObj(initialpos, buffer.tell(), TObjValue.START)
            elif curtoken == b"endobj":
                return TokenObj(initialpos, buffer.tell(), TObjValue.END)
            else:
                return TokenKeyword(initialpos, buffer.tell(), curtoken)
    raise LexerEOF
