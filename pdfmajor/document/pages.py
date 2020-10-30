from typing import List, NamedTuple, Optional
from pdfmajor.parser.objects.indirect import ObjectRef
from pdfmajor.parser.objects.collections import PDFDictionary


class PDFPageTreeNode(NamedTuple):
    """A PDF Pages Node representation as it confirms with PDF spec 1.7 section 7.7.3.2"""

    kids: List[ObjectRef]
    parent: Optional[ObjectRef] = None


class PDFPage(NamedTuple):
    """A PDF Page representation as it confirms with PDF Spec 1.7 section 7.7.3.3"""

    parent: ObjectRef
    resources: PDFDictionary
