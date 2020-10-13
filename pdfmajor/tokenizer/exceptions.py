from pdfmajor.execptions import PDFMajorException


class TokenizerError(PDFMajorException):
    pass


class TokenizerEOF(TokenizerError):
    pass

class InvalidToken(TokenizerError):
	def __init__(self, pos: int, token: bytes) -> None:
		super().__init__("Invalid Token Found at {pos}, of value={v}".format(
			pos=pos,
			v=token
		))
