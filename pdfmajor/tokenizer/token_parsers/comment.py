from pdfmajor.tokenizer.token import (
    TokenComment,
)
from pdfmajor.tokenizer.constants import (
    EOL,
)
from typing import Iterator
from .util import cmp_tsize, PInput


def parse_comment(initialpos: int, inp: Iterator[PInput]) -> TokenComment:
    """Parses input stream into a comment

    Args:
            initialpos (int): initial position where we started
            inp (Iterator[PInput])

    Returns:
            TokenComment
    """
    curtoken = b""
    for curpos, s in inp:
        m = EOL.search(s, 0)
        if not m:
            curtoken += s
        else:
            j = m.start(0)
            curtoken += s[:j]
            return TokenComment(initialpos, cmp_tsize(curpos, initialpos, j), curtoken)
