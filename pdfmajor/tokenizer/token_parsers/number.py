from decimal import Decimal
from pdfmajor.tokenizer.exceptions import InvalidToken, TokenizerEOF, TokenizerError
from pdfmajor.tokenizer.token import (
    TokenDecimal,
    TokenNumber,
    TokenInteger,
)
from pdfmajor.tokenizer.constants import (
    END_NUMBER,
)
from typing import Iterator
from .util import PInput


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
        raise TokenizerError("Number was provided an invalid sign {!r}".format(sign))
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
                    curpos + j + 1,
                    Decimal(curtoken.decode()),
                )
            try:
                if is_dec:
                    return TokenDecimal(
                        initialpos,
                        curpos + j,
                        Decimal(curtoken.decode()),
                    )
                else:
                    return TokenInteger(initialpos, curpos + j, int(curtoken))
            except ValueError:
                raise InvalidToken(initialpos, curtoken)
    raise TokenizerEOF
