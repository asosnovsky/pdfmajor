from pdfmajor.tokenizer.token import Token, TokenKeyword
from typing import Callable, NamedTuple, Optional, Union
from .constants import EOL, NONSPC

ParseFunc = Callable[["ParseInput"], "NextParseAction"]


class NextParseAction(NamedTuple):
    next_parse_action: ParseFunc
    charpos: int
    curtokenpos: int
    curtoken: Union[Token, bytes] = b""
    paren: Optional[int] = None


class ParseInput(NamedTuple):
    bufvalue: bytes
    charpos: int
    bufpos: int


def parse_main(inp: ParseInput) -> NextParseAction:
    m = NONSPC.search(inp.bufvalue, inp.charpos)
    if not m:
        return len(inp.bufvalue)
    j = m.start(0)
    c = inp.bufvalue[j : j + 1]
    if c == b"%":
        return NextParseAction(
            curtoken=b"%",
            next_parse_action=__parse_comment,
            curtokenpos=inp.bufpos + j,
            charpos=j + 1,
        )
    elif c == b"/":
        return NextParseAction(
            next_parse_action=__parse_literal,
            curtokenpos=inp.bufpos + j,
            charpos=j + 1,
        )
    elif c in b"-+" or c.isdigit():
        return NextParseAction(
            curtoken=c,
            next_parse_action=__parse_number,
            curtokenpos=inp.bufpos + j,
            charpos=j + 1,
        )
    elif c == b".":
        return NextParseAction(
            curtoken=c,
            next_parse_action=__parse_float,
            curtokenpos=inp.bufpos + j,
            charpos=j + 1,
        )
    elif c.isalpha():
        return NextParseAction(
            curtoken=c,
            next_parse_action=__parse_keyword,
            curtokenpos=inp.bufpos + j,
            charpos=j + 1,
        )
    elif c == b"(":
        return NextParseAction(
            next_parse_action=__parse_string,
            curtokenpos=inp.bufpos + j,
            charpos=j + 1,
            paren=1,
        )
    elif c == b"<":
        return NextParseAction(
            next_parse_action=__parse_wopen,
            curtokenpos=inp.bufpos + j,
            charpos=j + 1,
        )
    elif c == b">":
        return NextParseAction(
            next_parse_action=__parse_wclose,
            curtokenpos=inp.bufpos + j,
            charpos=j + 1,
        )
    else:
        return NextParseAction(
            next_parse_action=parse_main,
            curtokenpos=inp.bufpos + j,
            charpos=j + 1,
            curtoken=TokenKeyword(inp.bufpos + j, c),
        )


def __parse_comment(s, i):
    m = EOL.search(s, i)
    if not m:
        self._curtoken += s[i:]
        return len(s)
    j = m.start(0)
    self._curtoken += s[i:j]
    self._current_parse_func = self._parse_main
    # We ignore comments.
    # self._tokens.append(self._curtoken)
    return j
