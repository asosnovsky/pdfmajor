from typing import List

from pdfmajor.exceptions import BrokenFile, PDFMajorException
from pdfmajor.lexer.token import TokenKeyword


class ParserError(PDFMajorException):
    pass


class EarlyStop(ParserError, StopIteration):
    pass


class BrokenFileParserError(BrokenFile):
    pass


class UnexpectedEOF(BrokenFileParserError, EOFError):
    pass


class InvalidKeywordPos(BrokenFileParserError):
    def __init__(self, token: TokenKeyword, expected_token: List[bytes]) -> None:
        self.token = token
        super().__init__(
            f"keyword '{token.value!r}' was found at {token.start_loc}:{token.end_loc} when expecting {expected_token}"
        )


class DecodeFailed(BrokenFileParserError):
    pass


class InvalidDecoderOrNotImplemented(DecodeFailed, NotImplementedError):
    pass
