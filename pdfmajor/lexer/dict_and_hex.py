from pdfmajor.tokenizer.token_parsers.util import PInput
from pdfmajor.safebufiterator import SafeBufferIt
from pdfmajor.lexer.exceptions import LexerEOF
from pdfmajor.lexer.regex import END_HEX_STRING, HEX_PAIR, SPC
from pdfmajor.lexer.token import TDictVaue, TokenDictionary, TokenHexString
from typing import Union


def parse_double_angled_bracket(
    buffer: SafeBufferIt,
) -> Union[TokenHexString, TokenDictionary]:
    """Parses input stream into a hex string object or match a simple dictionary token

    Args:
        buffer (SafeBufferIt)

    Returns:
        Union[TokenHexString, TokenDictionary]
    """
    initialpos = buffer.tell() - 1
    step = next(buffer)
    first_char = step.data[0:1]
    if first_char == b"<":
        buffer.seek(step.pos + 1)
        return TokenDictionary(initialpos, 2, TDictVaue.OPEN)
    buffer.seek(step.pos)
    return parse_hexstring(buffer)


def parse_hexstring(buffer: SafeBufferIt) -> TokenHexString:
    """Parses the input string into hex string

    Args:
        buffer (SafeBufferIt)

    Returns:
        TokenHexString
    """
    curtoken = b""
    initialpos = buffer.tell() - 1
    for pos, buf in buffer:
        m = END_HEX_STRING.search(buf, 0)
        if not m:
            curtoken += buf
        else:
            j = m.start(0)
            curtoken += buf[:j]
            buffer.seek(pos + j + 1)
            token = HEX_PAIR.sub(
                lambda x: bytes([int(x.group(0), 16)]), SPC.sub(b"", curtoken)
            )
            return TokenHexString(initialpos, buffer.tell(), token)
    raise LexerEOF
