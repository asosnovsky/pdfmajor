from pdfmajor.tokenizer.exceptions import TokenizerError
import re
from dataclasses import dataclass
from pdfmajor.tokenizer.token_parsers.util import PInput, SafeBufferIt
from pdfmajor.tokenizer.token import (
    TokenString,
)
from pdfmajor.tokenizer.constants import (
    END_STRING,
    ESC_STRING,
)
from typing import Iterator, Optional

OCT_STRING = re.compile(br"^[0-7]{1,3}$")


@dataclass
class StringParseState:
    curtoken: bytes
    paren: int
    escaped_value: Optional[bytes] = None


def parse_string(initialpos: int, inp: Iterator[PInput]) -> TokenString:
    """Parses input stream into a simple string object

    Args:
        initialpos (int): initial position where we started
        inp (Iterator[PInput])

    Returns:
        TokenString
    """
    state = StringParseState(b"", 1)
    for curpos, buf in inp:
        it = SafeBufferIt(buf)
        for s in it.into_iter():
            if state.escaped_value is not None:
                parse_string_escape(it, state)
            else:
                m = END_STRING.search(s, 0)
                if not m:
                    state.curtoken += s
                    it.skip += len(s)
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
                        else:
                            return TokenString(
                                initialpos,
                                curpos + it.skip + j + 1,
                                state.curtoken.decode(),
                            )
    raise TokenizerError("end of parse_string")


def parse_string_escape(it: SafeBufferIt, state: StringParseState):
    if state.escaped_value is None:
        raise TokenizerError("state.escaped_value is None")
    for s in it.into_iter():
        for ci in range(len(s)):
            c = s[ci : ci + 1]
            if len(state.escaped_value) < 3:
                it.skip += 1
                state.escaped_value += c
            if len(state.escaped_value) == 1:
                if (ci < 1) and (c in ESC_STRING):
                    state.curtoken += bytes([ESC_STRING[c]])
                    state.escaped_value = None
                    return
            elif OCT_STRING.match(state.escaped_value):
                if len(state.escaped_value) == 3:
                    state.curtoken += bytes([int(state.escaped_value, 8)])
                    state.escaped_value = None
                    return
            else:
                it.skip -= 1
                state.escaped_value = None
                return
