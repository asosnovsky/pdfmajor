from dataclasses import dataclass
from pdfmajor.tokenizer.exceptions import (
    InvalidHexToken,
    InvalidToken,
    TokenizerEOF,
    TokenizerError,
)

from pdfmajor.tokenizer.token_parsers.util import SafeBufferIt, cmp_tsize
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
        it = SafeBufferIt(buf)
        for subbuf in it.into_iter():
            if state.hex_value is not None:
                for ci in range(len(subbuf)):
                    c = subbuf[ci : ci + 1]
                    if HEX.match(c) and len(state.hex_value) < 2:
                        state.hex_value += c
                        it.skip += 1
                        if len(state.hex_value) >= 2:
                            state.curtoken += int2byte(int(state.hex_value, 16))
                            state.hex_value = None
                            break
                    else:
                        raise InvalidHexToken(curpos + ci, c)
            else:
                m = END_LITERAL.search(buf[it.skip :], 0)
                if not m:
                    state.curtoken += buf[it.skip :]
                    it.skip = len(buf)
                else:
                    j: int = m.start(0) + it.skip
                    state.curtoken += buf[it.skip : j]
                    c = buf[j : j + 1]
                    if c == b"#":
                        state.hex_value = b""
                        it.skip = j + 1
                        continue
                    else:
                        return TokenLiteral(
                            initialpos,
                            cmp_tsize(curpos, initialpos, j),
                            state.curtoken.decode(),
                        )
    raise TokenizerEOF
