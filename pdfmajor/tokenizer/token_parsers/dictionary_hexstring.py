from pdfmajor.tokenizer.exceptions import TokenizerError
from pdfmajor.tokenizer.constants import END_HEX_STRING, HEX_PAIR, SPC
from pdfmajor.tokenizer.token import TDictVaue, Token, TokenDictionary, TokenHexString
from pdfmajor.tokenizer.token_parsers.util import PInput
from pdfmajor.utils import int2byte
from typing import Iterator, Union


def parse_double_angled_bracket(initialpos: int, inp: Iterator[PInput]) -> Token:
    """Parses input stream into a simple string object

    Args:
        initialpos (int): initial position where we started
        inp (Iterator[PInput])

    Returns:
        Union[TokenHexString, TokenDictionary]
    """
    step = next(inp)
    first_char = step.buf[0:2]
    if first_char == b"<<":
        return TokenDictionary(initialpos, 2, TDictVaue.OPEN)
    curtoken = parse_hexstring(initialpos, PInput(step.pos + 1, step.buf[1:]), b"")
    if isinstance(curtoken, TokenHexString):
        return curtoken
    else:
        for step in inp:
            curtoken = parse_hexstring(initialpos, step, curtoken)
            if isinstance(curtoken, TokenHexString):
                return curtoken
    raise TokenizerError("parse_double_angled_bracket ended")


def parse_hexstring(
    initialpos: int, inp: PInput, curtoken: bytes
) -> Union[bytes, TokenHexString]:
    m = END_HEX_STRING.search(inp.buf, 0)
    if not m:
        curtoken += inp.buf
        return curtoken
    j = m.start(0)
    curtoken += inp.buf[:j]
    token = HEX_PAIR.sub(
        lambda x: int2byte(int(x.group(0), 16)), SPC.sub(b"", curtoken)
    )
    return TokenHexString(initialpos, inp.pos + j + 1, token)
