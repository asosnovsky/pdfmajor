from decimal import Decimal
from pdfmajor.parser.PSStackParser.constants import END_LITERAL, HEX
from pdfmajor.utils import int2byte
from pdfmajor.tokenizer.exceptions import InvalidToken, TokenizerEOF
from pdfmajor.tokenizer.token import (
    TokenDecimal,
    TokenNumber,
    TokenInteger,
)
from pdfmajor.tokenizer.constants import (
    END_NUMBER,
)
from typing import Iterator, Literal, Union
from .util import cmp_tsize, PInput


def parse_number(
    initialpos: int, inp: Iterator[PInput], sign: bytes = b"+"
) -> TokenNumber:
    """Parses input stream into a number

    Args:
        initialpos (int): initial position where we started
        inp (Iterator[PInput])
        sign (str): either a + or -

    Returns:
        TokenNumber
    """
    if sign not in [b"+", b"-"]:
        raise InvalidToken("Number was provided an invalid sign {!r}".format(sign))
    curtoken = b"" + sign
    is_dec = False
    for curpos, s in inp:
        m = END_NUMBER.search(s, 0)
        if not m:
            curtoken += s
        else:
            j = m.start(0)
            curtoken += s[:j]
            c = s[j : j + 1]
            if (c == b".") and not is_dec:
                is_dec = True
                curtoken += c
                s = s[j + 1 :]
                m = END_NUMBER.search(s, 0)
                if not m:
                    curtoken += s
                    continue
                else:
                    nj = m.start(0)
                    curtoken += s[:nj]
                    j += nj
                return TokenDecimal(
                    initialpos,
                    cmp_tsize(curpos, initialpos, j),
                    Decimal(curtoken.decode()),
                )
            try:
                if is_dec:
                    return TokenDecimal(
                        initialpos,
                        cmp_tsize(curpos, initialpos, j),
                        Decimal(curtoken.decode()),
                    )
                else:
                    return TokenInteger(
                        initialpos, cmp_tsize(curpos, initialpos, j), int(curtoken)
                    )
            except ValueError:
                raise InvalidToken(initialpos, curtoken)
    raise TokenizerEOF
