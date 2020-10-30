from pathlib import Path
from typing import BinaryIO

from pdfmajor.healthlog import PDFHealthReport
from pdfmajor.streambuffer import BufferStream
from pdfmajor.xref.xrefdb import XRefDB


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
        self.buffer = buffer
        self.health_report = PDFHealthReport()
        with self.buffer.get_window():
            self.xref_db = XRefDB(buffer)
