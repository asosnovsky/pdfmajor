from pdfmajor.tokenizer.exceptions import TokenizerEOF
from pdfmajor.tokenizer.token import TokenBoolean, TokenKeyword
from pdfmajor.tokenizer.constants import END_KEYWORD
from typing import Iterator, Union
from .util import cmp_tsize, PInput


def parse_keyword(
    initialpos: int, inp: Iterator[PInput]
) -> Union[TokenKeyword, TokenBoolean]:
    """Parses input stream into a keyword or bool

    Args:
        initialpos (int): initial position where we started
        inp (Iterator[PInput])

    Returns:
        Union[TokenKeyword, TokenBoolean]
    """
    curtoken = b""
    for curpos, s in inp:
        m = END_KEYWORD.search(s, 0)
        if not m:
            curtoken += s
        else:
            j = m.start(0)
            curtoken += s[:j]
            if curtoken == b"true":
                return TokenBoolean(initialpos, cmp_tsize(curpos, initialpos, j), True)
            elif curtoken == b"false":
                return TokenBoolean(initialpos, cmp_tsize(curpos, initialpos, j), False)
            else:
                return TokenKeyword(
                    initialpos, cmp_tsize(curpos, initialpos, j), curtoken
                )
    raise TokenizerEOF
