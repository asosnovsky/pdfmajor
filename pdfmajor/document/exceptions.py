from decimal import Decimal
from typing import List, Set

from pdfmajor.exceptions import BrokenFile, PDFMajorException
from pdfmajor.parser.objects import ObjectRef


class PDFDocumentError(PDFMajorException):
    pass


class BrokenFilePDF(BrokenFile):
    pass


class MissingCatalogObj(BrokenFilePDF):
    pass


class InvalidCatalogObj(BrokenFilePDF):
    pass


class TooManyInfoObj(BrokenFilePDF):
    def __init__(self, elms: Set[ObjectRef]) -> None:
        super().__init__(f"Too many info elements found | elms={elms}")
        self.elms = elms


class TooManyRectField(BrokenFilePDF):
    def __init__(self, values: List[Decimal]) -> None:
        super().__init__(f"Too many elements found for rectangle | values={values}")
        self.values = values


class InvalidPagesNodeKids(BrokenFilePDF):
    pass
