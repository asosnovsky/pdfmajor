from decimal import Decimal
from pdfmajor.parser.PSStackParser.constants import END_LITERAL, HEX
from pdfmajor.utils import int2byte
from pdfmajor.tokenizer.exceptions import InvalidToken
from pdfmajor.tokenizer.token import (
    Token,
    TokenBoolean,
    TokenComment,
    TokenDecimal,
    TokenKeyword,
    TokenLiteral,
    TokenNumber,
    TokenInteger,
    TokenString,
)
from pdfmajor.tokenizer.constants import (
    END_KEYWORD,
    END_NUMBER,
    END_STRING,
    EOL,
    ESC_STRING,
    OCT_STRING,
)
from typing import Callable, Iterator, Literal, NamedTuple, Union


def parse_string(initialpos: int, inp: Iterator[PInput]):
    curtoken = b""
    paren = 1
    for curpos, s in inp:
        m = END_STRING.search(s, 0)
        if not m:
            curtoken += s
        else:
            j = m.start(0)
            curtoken += s[:j]
            c = s[j : j + 1]
            if c == b"\\":
                self._current_parse_func = self._parse_string_1
                return j + 1
            elif c == b"(":
                paren += 1
                curtoken += c
                return j + 1
            elif c == b")":
                paren -= 1
                if paren:  # WTF, they said balanced parens need no special treatment.
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
