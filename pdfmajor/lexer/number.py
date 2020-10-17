from decimal import Decimal
from typing import Optional
from pdfmajor.streambuffer import BufferStream
from pdfmajor.lexer.exceptions import InvalidToken, LexerEOF, LexerError
from pdfmajor.lexer.token import (
    TokenDecimal,
    TokenNumber,
    TokenInteger,
)
from pdfmajor.lexer.regex import (
    END_NUMBER,
)


def parse_number(
    buffer: BufferStream, sign: bytes = b"+", initialpos: Optional[int] = None
) -> TokenNumber:
    """Parses input stream into a number

    Args:
        buffer (BufferStream)
        sign (str): either a + or -
        initialpos (Optional[int])

    Returns:
        TokenNumber
    """
    if sign not in [b"+", b"-"]:
        raise LexerError("Number was provided an invalid sign {!r}".format(sign))
    curtoken = b"" + sign
    is_decimal = False
    initialpos = buffer.tell() - 1 if initialpos is None else initialpos
    for pos, buf in buffer:
        m = END_NUMBER.search(buf, 0)
        if not m:
            curtoken += buf
        else:
            j = m.start(0)
            c = buf[j : j + 1]
            if (c == b".") and not is_decimal:
                is_decimal = True
                buffer.seek(pos + j + 1)
                curtoken += buf[: j + 1]
            else:
                curtoken += buf[:j]
                buffer.seek(pos + j)
                try:
                    if is_decimal:
                        return TokenDecimal(
                            initialpos,
                            buffer.tell(),
                            Decimal(curtoken.decode()),
                        )
                    else:
                        return TokenInteger(initialpos, buffer.tell(), int(curtoken))
                except ValueError:
                    raise InvalidToken(initialpos, curtoken)
    raise LexerEOF
