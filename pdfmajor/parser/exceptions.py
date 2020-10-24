from pdfmajor.lexer.token import TokenKeyword
from pdfmajor.exceptions import PDFMajorException


class ParserError(PDFMajorException):
    pass


class BrokenFile(ParserError):
    pass


class UnexpectedEOF(BrokenFile, EOFError):
    pass


class InvalidKeywordPos(BrokenFile):
    def __init__(self, token: TokenKeyword) -> None:
        self.token = token
        super().__init__(
            f"keyword '{token.value!r}' was found at {token.start_loc}:{token.end_loc}"
        )


class InvalidIndirectObjAccess(ParserError):
    pass


class DecodeFailed(BrokenFile):
    pass


class InvalidDecoderOrNotImplemented(DecodeFailed, NotImplementedError):
    pass


class PDFNoValidXRef(BrokenFile, EOFError):
    pass


class InvalidXref(ParserError, KeyError):
    pass