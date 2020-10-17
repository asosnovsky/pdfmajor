from pdfmajor.lexer.exceptions import LexerEOF
from pdfmajor.lexer.regex import EOL
from pdfmajor.lexer.token import (
    TokenComment,
)
from pdfmajor.safebufiterator import BufferStream


def parse_comment(buffer: BufferStream) -> TokenComment:
    """Parses input stream into a comment

    Args:
        buffer (BufferStream)

    Returns:
        TokenComment
    """
    curtoken = b""
    initialpos = buffer.tell() - 1
    for pos, buf in buffer:
        m = EOL.search(buf, 0)
        if not m:
            curtoken += buf
        else:
            j = m.start(0)
            curtoken += buf[:j]
            buffer.seek(pos + j)
            return TokenComment(initialpos, buffer.tell(), curtoken)
    raise LexerEOF
