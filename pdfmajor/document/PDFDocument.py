import warnings
from pathlib import Path
from typing import BinaryIO, Iterator, List, Optional

from pdfmajor.document.pages import PDFPage
from pdfmajor.document.parsers.pages import iter_all_page_leafs
from pdfmajor.document.parsers.root import get_catalog, get_info
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
        self.__processed_pages: Optional[List[PDFPage]] = None
        self.__processed_pages_done = False
        self.catalog = get_catalog(self.__parser)
        self.info = get_info(self.__parser)

    @property
    def health_report(self):
        """A log of errors that occured in the document during the processing of the file"""
        return self.__parser.health_report

    @property
    def num_pages(self) -> int:
        """Returns the number of pages that the metadata of the document claims it has.
        This number should be trusted, unless you suspect the document may have encoutered some corruption. To get an excat count do `len(list(self.iter_pages()))`. Please note that this will load all of the metadata of each document into memory.

        Returns:
            int
        """
        return self.catalog.pages.leaft_count

    def iter_pages(self) -> Iterator[PDFPage]:
        """Iterate over all of the pages in the document, this will also keep a record of the pdf page in memory for quicker future retrieval! (use self.clear() to free it up)

        Yields:
            Iterator[PDFPage]
        """
        if self.__processed_pages is not None and self.__processed_pages_done:
            return iter(self.__processed_pages)
        else:
            self.__processed_pages = []
            for page in iter_all_page_leafs(self.__parser, self.catalog.pages):
                self.__processed_pages.append(page)
                yield page
            self.__processed_pages_done = True
            if len(self.__processed_pages) != self.num_pages:
                warnings.warn(
                    "Number of pages proceseed with iter_pages did not match number of pages specified by the document's metadata!"
                    f"\n --> expected pages = {self.num_pages}"
                    f"\n --> found pages = {len(self.__processed_pages)}"
                )

    def clear(self):
        """Clears out memory used by the class as much as possible"""
        self.__processed_pages = None
        self.__processed_pages_done = False
