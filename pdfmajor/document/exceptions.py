from pdfmajor.exceptions import BrokenFile, PDFMajorException


class PDFDocumentError(PDFMajorException):
    pass


class MissingCatalogObj(PDFDocumentError, BrokenFile):
    pass


class InvalidCatalogObj(PDFDocumentError, BrokenFile):
    pass
