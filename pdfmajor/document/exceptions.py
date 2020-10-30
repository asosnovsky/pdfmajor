from typing import Set

from pdfmajor.exceptions import BrokenFile, PDFMajorException
from pdfmajor.parser.objects.indirect import ObjectRef


class PDFDocumentError(PDFMajorException):
    pass


class MissingCatalogObj(PDFDocumentError, BrokenFile):
    pass


class InvalidCatalogObj(PDFDocumentError, BrokenFile):
    pass


class TooManyInfoObj(PDFDocumentError, BrokenFile):
    def __init__(self, elms: Set[ObjectRef]) -> None:
        super().__init__(f"Too many info elements found | total={elms}")
        self.elms = elms
