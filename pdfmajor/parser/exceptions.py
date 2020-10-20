from pdfmajor.lexer.token import TokenKeyword
from pdfmajor.exceptions import PDFMajorException


class ParserError(PDFMajorException):
    pass


class InvalidKeywordPos(ParserError):
    def __init__(self, token: TokenKeyword) -> None:
        self.token = token
        super().__init__(
            f"keyword '{token.value}' was found at {token.start_loc}:{token.end_loc}"
        )


class InvalidIndirectObjAccess(ParserError):
    pass


class DecodeFailed(ParserError):
    pass


class InvalidDecoderOrNotImplemented(DecodeFailed, NotImplementedError):
    pass
