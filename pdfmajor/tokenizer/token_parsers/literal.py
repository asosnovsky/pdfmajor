from dataclasses import dataclass
from pdfmajor.tokenizer.exceptions import TokenizerEOF

from pdfmajor.tokenizer.token_parsers.util import cmp_tsize
from pdfmajor.tokenizer.token_parsers.util import PInput
from pdfmajor.tokenizer.token import TokenLiteral
from pdfmajor.utils import int2byte
from ..constants import HEX, END_LITERAL

from typing import Iterator, NamedTuple, Optional, Union


@dataclass
class LiteralParseState:
    curtoken: bytes
    hex_value: Optional[bytes] = None


def parse_literal(initialpos: int, inp: Iterator[PInput]) -> TokenLiteral:
    """Parses input stream into a literal

    Args:
                    initialpos (int): initial position where we started
                    inp (Iterator[PInput])

    Returns:
                    TokenLiteral
    """
    state = LiteralParseState(b"")
    for curpos, buf in inp:
        skip: int = 0
        for i in range(len(buf) + 1):
            assert i < len(buf), "MAX_LOOP_REACHED"
            if skip >= len(buf):
                break
            if state.hex_value is not None:
                for ci in range(len(buf[skip:])):
                    c = buf[skip + ci : skip + ci + 1]
                    if HEX.match(c) and len(state.hex_value) < 2:
                        state.hex_value += c
                    else:
                        if state.hex_value:
                            state.curtoken += int2byte(int(state.hex_value, 16))
                        state.hex_value = None
                        skip += ci
                        break
            else:
                m = END_LITERAL.search(buf[skip:], 0)
                if not m:
                    state.curtoken += buf[skip:]
                    skip = len(buf)
                else:
                    j: int = m.start(0) + skip
                    state.curtoken += buf[skip:j]
                    c = buf[j : j + 1]
                    if c == b"#":
                        state.hex_value = b""
                        skip = j + 1
                        continue
                    else:
                        return TokenLiteral(
                            initialpos,
                            cmp_tsize(curpos, initialpos, j),
                            state.curtoken.decode(),
                        )
    raise TokenizerEOF
