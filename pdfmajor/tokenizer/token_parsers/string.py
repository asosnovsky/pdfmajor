from dataclasses import dataclass
from pdfmajor.tokenizer.exceptions import TokenizerEOF
from pdfmajor.tokenizer.token_parsers.util import PInput, SafeBufferIt, cmp_tsize
from pdfmajor.utils import int2byte
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
    oct_value: Optional[bytes] = None


def parse_string(initialpos: int, inp: Iterator[PInput]):
    state = StringParseState(b"", 1)
    for curpos, buf in inp:
        it = SafeBufferIt(buf)
        for s in it.into_iter():
            if state.oct_value is not None:
                it.skip += parse_string_oct(s, state)
            else:
                m = END_STRING.search(s, 0)
                if not m:
                    state.curtoken += s
                else:
                    j = m.start(0)
                    state.curtoken += s[:j]
                    c = s[j : j + 1]
                    if c == b"\\":
                        state.oct_value = b""
                        it.skip += j + 1
                    elif c == b"(":
                        state.paren += 1
                        state.curtoken += c
                        it.skip += j + 1
                    elif c == b")":
                        state.paren -= 1
                        if state.paren:
                            state.curtoken += c
                            it.skip += j + 1
                    return TokenString(
                        initialpos,
                        cmp_tsize(curpos, initialpos, j),
                        state.curtoken.decode(),
                    )


def parse_string_oct(s: bytes, state: StringParseState) -> int:
    for ci in range(len(s)):
        c = s[ci : ci + 1]
        if OCT_STRING.match(c) and len(state.oct_value) < 3:
            state.oct_value += c
        elif state.oct_value:
            state.curtoken += int2byte(int(state.oct_value, 8))
            return ci
        elif c in ESC_STRING:
            state.curtoken += int2byte(ESC_STRING[c])
            state.oct_value = None
            return ci + 1
    state.oct_value = None
    return len(s) + 1
