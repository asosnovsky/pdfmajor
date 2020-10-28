from pdfmajor.parser.xref import iter_over_xref
from pdfmajor.streambuffer import BufferStream
from pdfmajor.parser.objects.indirect import IndirectObject
from pdfmajor.parser.xrefdb import XRefDB
from datetime import datetime
from typing import List, NamedTuple, Tuple


class PDFDocumentMetadata(NamedTuple):
    version: str
    creator: str
    producer: str
    creation_date: datetime
    mediabox: Tuple[int, int, int, int]


class PDFPage(IndirectObject):
    pass


class PDFResoruce(IndirectObject):
    pass


class PDFDocument:
    metadata: PDFDocumentMetadata
    _xrefdb: XRefDB
    _resources: List[PDFResoruce]
    _pages: List[PDFPage]

    def __init__(self, buffer: BufferStream, strict: bool = False) -> None:
        self._xrefdb = XRefDB()
        self._xrefdb.update_from_xrefiter(iter_over_xref(buffer, strict))
        self.metadata = get_metadata_from_buffer(buffer, self._xrefdb)
        self._pages = get_pages_from_buffer(buffer, self._xrefdb)
        self._resources = get_resources_from_buffer(buffer, self._xrefdb)

    def read_page(self, page_num: int) -> PDFPage:
        page_obj = self._pages[page_num]
        # for


# pdf_doc = PDFDocument.from_path('path/to/file.pdf')
# pdf_doc.metadata
