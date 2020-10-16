from dataclasses import dataclass
from typing import Optional
from pdfmajor.lexer.regex import END_STRING, ESC_STRING, OCT_STRING
from pdfmajor.lexer.token import TokenString
from pdfmajor.lexer.exceptions import LexerEOF, LexerError
from pdfmajor.safebufiterator import SafeBufferIt


@dataclass
class StringParseState:
    curtoken: bytes
    paren: int
    escaped_value: Optional[bytes] = None


def parse_string(buffer: SafeBufferIt) -> TokenString:
    """Parses input stream into a simple string object

    Args:
        buffer (SafeBufferIt)

    Returns:
        TokenString
    """
    initialpos = buffer.tell() - 1
    state = StringParseState(b"", 1)
    for curpos, buf in buffer:
        if state.escaped_value is not None:
            buffer.seek(curpos)
            parse_string_escape(buffer, state)
        else:
            m = END_STRING.search(buf, 0)
            if not m:
                state.curtoken += buf
            else:
                j = m.start(0)
                state.curtoken += buf[:j]
                buffer.seek(curpos + j + 1)
                next_char = buf[j : j + 1]
                if next_char == b"\\":
                    state.escaped_value = b""
                elif next_char == b"(":
                    state.paren += 1
                    state.curtoken += next_char
                elif next_char == b")":
                    state.paren -= 1
                    if state.paren:
                        state.curtoken += next_char
                    else:
                        return TokenString(
                            initialpos,
                            buffer.tell(),
                            state.curtoken.decode(),
                        )
    raise LexerEOF


def parse_string_escape(buffer: SafeBufferIt, state: StringParseState):
    if state.escaped_value is None:
        raise LexerError("state.escaped_value is None")
    for pos, buf in buffer:
        for ci in range(len(buf)):
            c = buf[ci : ci + 1]
            if len(state.escaped_value) < 3:  # type: ignore
                state.escaped_value += c
                buffer.seek(pos + ci + 1)
            if len(state.escaped_value) == 1:  # type: ignore
                if (ci < 1) and (c in ESC_STRING):
                    state.curtoken += bytes([ESC_STRING[c]])
                    state.escaped_value = None
                    return
            elif OCT_STRING.match(state.escaped_value):  # type: ignore
                if len(state.escaped_value) == 3:  # type: ignore
                    state.curtoken += bytes([int(state.escaped_value, 8)])  # type: ignore
                    state.escaped_value = None
                    return
            else:
                state.escaped_value = None
                buffer.seekd(-1)
                return
