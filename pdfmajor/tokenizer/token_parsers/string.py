from dataclasses import dataclass
from pdfmajor.tokenizer.token_parsers.util import PInput, SafeBufferIt, cmp_tsize
from pdfmajor.tokenizer.token import (
    TokenString,
)
from pdfmajor.tokenizer.constants import (
    END_STRING,
    ESC_STRING,
    OCT_STRING,
)
from typing import Iterator, Optional


@dataclass
class StringParseState:
    curtoken: bytes
    paren: int
    escaped_value: Optional[bytes] = None


def parse_string(initialpos: int, inp: Iterator[PInput]):
    state = StringParseState(b"", 1)
    for curpos, buf in inp:
        it = SafeBufferIt(buf)
        for s in it.into_iter():
            if state.escaped_value is not None:
                it.skip += parse_string_escape(s, state)
            else:
                m = END_STRING.search(s, 0)
                if not m:
                    state.curtoken += s
                    it.skip = len(s)
                else:
                    j = m.start(0)
                    state.curtoken += s[:j]
                    next_char = s[j : j + 1]
                    if next_char == b"\\":
                        state.escaped_value = b""
                        it.skip += j + 1
                    elif next_char == b"(":
                        state.paren += 1
                        state.curtoken += next_char
                        it.skip += j + 1
                    elif next_char == b")":
                        state.paren -= 1
                        if state.paren:
                            state.curtoken += next_char
                            it.skip += j + 1
                    return TokenString(
                        initialpos,
                        cmp_tsize(curpos, initialpos, j),
                        state.curtoken.decode(),
                    )


def parse_string_escape(s: bytes, state: StringParseState) -> int:
    for ci in range(len(s)):
        c = s[ci : ci + 1]
        if (ci < 1) and (c in ESC_STRING):
            state.curtoken += bytes([ESC_STRING[c]])
            state.escaped_value = None
            return 1
        if OCT_STRING.match(c) and len(state.escaped_value) < 3:
            state.escaped_value += c
        elif len(state.escaped_value) == 3:
            state.curtoken += bytes([int(state.escaped_value, 8)])
            return 3

    state.escaped_value = None
    return len(s) + 1
