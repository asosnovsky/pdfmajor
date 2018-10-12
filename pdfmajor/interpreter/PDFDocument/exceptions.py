from ..PDFParser import PDFSyntaxError
from ..PDFStream import PDFException

##  Exceptions
##
class PDFNoValidXRef(PDFSyntaxError):
    pass

class PDFNoOutlines(PDFException):
    pass

class PDFDestinationNotFound(PDFException):
    pass

class PDFEncryptionError(PDFException):
    pass

class PDFPasswordIncorrect(PDFEncryptionError):
    pass

class PDFTextExtractionNotAllowed(PDFEncryptionError):
    pass