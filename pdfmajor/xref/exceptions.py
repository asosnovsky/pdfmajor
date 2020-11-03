from typing import Set

from pdfmajor.exceptions import BrokenFile, PDFMajorException
from pdfmajor.parser.objects import ObjectRef


class XRefError(PDFMajorException):
    pass


class PDFNoValidXRef(XRefError, BrokenFile, EOFError):
    pass


class InvalidXref(XRefError):
    pass


class InvalidIndirectObjAccess(XRefError):
    pass


class UnexpectedEOF(BrokenFile, EOFError):
    pass


class InvalidNumberOfRoots(XRefError):
    def __init__(self, roots: Set[ObjectRef]) -> None:
        super().__init__(f"Too many root elements found| total={roots}")
        self.roots = roots


class NotRootElement(XRefError):
    pass
