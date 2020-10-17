from pdfmajor.execptions import PDFMajorException


class LexerError(PDFMajorException):
    pass


class LexerEOF(LexerError, EOFError):
    pass


class InvalidHexToken(LexerError):
    def __init__(self, pos: int, token: bytes) -> None:
        super().__init__(
            "Invalid Hex Found at {pos}, of value={v}".format(pos=pos, v=str(token))
        )


class InvalidToken(LexerError):
    def __init__(self, pos: int, token: bytes) -> None:
        super().__init__(
            "Invalid Token Found at {pos}, of value={v}".format(pos=pos, v=str(token))
        )
