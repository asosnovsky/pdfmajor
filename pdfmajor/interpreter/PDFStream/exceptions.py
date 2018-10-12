from ..PSStackParser import PSException

class PDFException(PSException):
    pass

class PDFTypeError(PDFException):
    pass

class PDFValueError(PDFException):
    pass

class PDFObjectNotFound(PDFException):
    pass

class PDFNotImplementedError(PDFException):
    pass