from dataclasses import dataclass
from pdfmajor.lexer.exceptions import (
    InvalidHexToken,
    LexerEOF,
    LexerError,
)

from pdfmajor.streambuffer import BufferStream
from pdfmajor.lexer.token import PDFName, TokenName
from pdfmajor.lexer.regex import HEX, END_LITERAL


from typing import Optional


@dataclass
class LiteralParseState:
    curtoken: bytes
    hex_value: Optional[bytes] = None


def parse_name(buffer: BufferStream) -> TokenName:
    """Parses input stream into a literal name

    Args:
        buffer (BufferStream)

    Returns:
        TokenName
    """
    initialpos = buffer.tell() - 1
    state = LiteralParseState(b"")
    for pos, buf in buffer:
        if state.hex_value is not None:
            for ci in range(len(buf)):
                c = buf[ci : ci + 1]
                if state.hex_value is None:
                    raise LexerError("state.hex_value became None")
                if HEX.match(c) and len(state.hex_value) < 2:
                    state.hex_value += c
                    buffer.seek(pos + ci + 1)
                    if len(state.hex_value) >= 2:  # type: ignore
                        state.curtoken += bytes([int(state.hex_value, 16)])  # type: ignore
                        state.hex_value = None
                        break
                else:
                    raise InvalidHexToken(buffer.tell() - buffer.buffer_size, c)
        else:
            m = END_LITERAL.search(buf, 0)
            if not m:
                state.curtoken += buf
            else:
                j: int = m.start(0)
                state.curtoken += buf[:j]
                next_char = buf[j : j + 1]
                if next_char == b"#":
                    state.hex_value = b""
                    buffer.seek(pos + j + 1)
                    continue
                else:
                    buffer.seek(pos + j)
                    return TokenName(
                        initialpos,
                        buffer.tell(),
                        PDFName(state.curtoken.decode()),
                    )
    raise LexerEOF
