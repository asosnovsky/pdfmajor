from pathlib import Path
from typing import BinaryIO, List

from pdfmajor.document.pages import PDFPageTreeNode
from pdfmajor.document.PDFParsingContext import PDFParsingContext
from pdfmajor.streambuffer import BufferStream


class PDFDocument:
    """A class encapsulating all of the access behavior to the document

    Returns:
        [type]: [description]
    """

    @classmethod
    def from_io(cls, fp: BinaryIO, buffer_size=4096):
        return cls(BufferStream(fp, buffer_size))

    @classmethod
    def from_path(cls, path: Path, buffer_size=4096):
        return cls(BufferStream(path.open("rb"), buffer_size))

    def __init__(self, buffer: BufferStream) -> None:
        self.__parser = PDFParsingContext(buffer)
        self.catalog = self.__parser.get_catalog()
        self.info = self.__parser.get_info()
        self.pages: List[PDFPageTreeNode] = []

    @property
    def health_report(self):
        """A log of errors that occured in the document during the processing of the file"""
        return self.__parser.health_report
