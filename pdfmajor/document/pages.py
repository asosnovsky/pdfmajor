from decimal import Decimal
from typing import List, NamedTuple, Optional

from pdfmajor.document.exceptions import InvalidPagesNodeKids
from pdfmajor.document.structures import PDFRectangle
from pdfmajor.parser.objects.collections import PDFArray, PDFDictionary
from pdfmajor.parser.objects.indirect import ObjectRef
from pdfmajor.parser.objects.primitives import PDFInteger
from pdfmajor.parser.stream.PDFStream import PDFStream
from pdfmajor.util import validate_object_or_none


class PDFPageTreeNode(NamedTuple):
    """A PDF Pages Node representation as it confirms with PDF spec 1.7 section 7.7.3.2"""

    kids: List[ObjectRef]
    parent: Optional[ObjectRef]
    leaft_count: int

    raw: PDFDictionary

    @classmethod
    def from_pdfdict(cls, pdfdict: PDFDictionary):
        parent = validate_object_or_none(pdfdict.get("Parent"), ObjectRef)
        kids = pdfdict["Kids"]
        count = validate_object_or_none(pdfdict.get("Count"), PDFInteger)
        vetted_kids: List[ObjectRef] = []
        if isinstance(kids, ObjectRef):
            vetted_kids = [kids]
        elif isinstance(kids, PDFArray):
            for kid in kids:
                vetted_kid = validate_object_or_none(kid, ObjectRef)
                if vetted_kid:
                    vetted_kids.append(vetted_kid)
        else:
            raise InvalidPagesNodeKids(f"{kids}")
        return cls(
            kids=vetted_kids,
            parent=parent,
            raw=pdfdict,
            leaft_count=0 if count is None else count.to_python(),
        )


class PDFPage(NamedTuple):
    """A PDF Page representation as it confirms with PDF Spec 1.7 section 7.7.3.3"""

    parent: ObjectRef
    resources: PDFDictionary
    mediabox: PDFRectangle
    bleedbox: PDFRectangle
    trimbox: PDFRectangle
    contents: List[PDFStream]
    boxcolor_info: Optional[PDFDictionary]
    rotate: Decimal
    metadata: Optional[ObjectRef]
    user_unit: Decimal
