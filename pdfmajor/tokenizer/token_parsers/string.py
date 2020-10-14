from dataclasses import dataclass
from pdfmajor.tokenizer.exceptions import TokenizerEOF
from pdfmajor.tokenizer.token_parsers.util import PInput, cmp_tsize
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
        skip: int = 0
        for i in range(len(buf) + 1):
            if i < len(buf):
                raise TokenizerEOF("Max Iteration Reached!")
            if skip >= len(buf):
                break
        m = END_STRING.search(s, 0)
        if not m:
            curtoken += s
        else:
            j = m.start(0)
            curtoken += s[:j]
            c = s[j : j + 1]
            if c == b"\\":
                _parse_string_1
                return j + 1
            elif c == b"(":
                paren += 1
                curtoken += c
                return j + 1
            elif c == b")":
                paren -= 1
                if paren:
                    curtoken += c
                    return j + 1
            return TokenString(
                initialpos, cmp_tsize(curpos, initialpos, j), curtoken.decode()
            )


def parse_string_oct(initialpos: int, inp: Iterator[PInput]):
    curtoken: bytes = b""
    oct_val: bytes = b""
    for curpos, s in inp:
        for ci in range(len(s)):
            c = s[ci : ci + 1]
            if OCT_STRING.match(c) and len(oct_val) < 3:
                oct_val += c
            elif oct_val:
                curtoken += int2byte(int(oct_val, 8))
                return (curtoken, curpos + ci)
            elif c in ESC_STRING:
                curtoken += int2byte(ESC_STRING[c])
                return (curtoken, curpos + ci + 1)
