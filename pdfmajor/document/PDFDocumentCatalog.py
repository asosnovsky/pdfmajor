from typing import Any, Dict, List, NamedTuple, Optional

from pdfmajor.parser.objects.collections import PDFDictionary
from pdfmajor.parser.objects.indirect import ObjectRef
from pdfmajor.parser.objects.primitives import PDFName


class PDFDocumentCatalog(NamedTuple):
    """A Parsed version of the PDF Catalog object (see PDF spec 1.7 section 7.7.2 for more detail)"""

    version: Optional[PDFName]
    pages: List[ObjectRef]
    page_labels: Optional[PDFDictionary]
    page_layout: Optional[PDFName]
    page_mode: Optional[PDFName]
    metadata: Optional[PDFDictionary]

    raw: Dict[str, Any]  # for other properties
