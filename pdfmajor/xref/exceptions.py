from pdfmajor.exceptions import BrokenFile, PDFMajorException


class XRefError(PDFMajorException):
    pass


class PDFNoValidXRef(XRefError, BrokenFile, EOFError):
    pass


class InvalidXref(XRefError, KeyError):
    pass


class InvalidIndirectObjAccess(XRefError):
    pass


class UnexpectedEOF(BrokenFile, EOFError):
    pass
