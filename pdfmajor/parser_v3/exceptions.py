from pdfmajor.execptions import PDFMajorException


class ParserError(PDFMajorException):
    pass


class DecodeFailed(ParserError):
    pass


class InvalidDecoderOrNotImplemented(DecodeFailed, NotImplementedError):
    pass
