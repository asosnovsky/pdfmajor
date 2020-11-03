from typing import Any, Dict, NamedTuple, Optional

from pdfmajor.document.metadata import PDFMetadata
from pdfmajor.document.pages import PDFPageTreeNode
from pdfmajor.parser.objects import PDFDictionary, PDFName


class PDFDocumentCatalog(NamedTuple):
    """A Parsed version of the PDF Catalog object (see PDF spec 1.7 section 7.7.2 for more detail)"""

    version: Optional[PDFName]
    pages: PDFPageTreeNode
    page_labels: Optional[PDFDictionary]
    page_layout: Optional[PDFName]
    page_mode: Optional[PDFName]
    metadata: Optional[PDFMetadata]

    raw: Dict[str, Any]  # for other properties
