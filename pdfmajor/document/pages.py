from typing import List, NamedTuple, Optional

from pdfmajor.document.exceptions import InvalidPagesNodeKids
from pdfmajor.document.structures import PDFRectangle
from pdfmajor.exceptions import PDFMajorException
from pdfmajor.parser.objects import (
    ObjectRef,
    PDFDictionary,
    PDFInteger,
    PDFReal,
    PDFStream,
    validate_object_or_none,
)

from .utils import iter_single_ref_as_array_ref


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
        try:
            vetted_kids: List[ObjectRef] = list(
                iter_single_ref_as_array_ref(pdfdict["Kids"])
            )
        except PDFMajorException:
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
    cropbox: PDFRectangle
    bleedbox: PDFRectangle
    trimbox: PDFRectangle
    artbox: PDFRectangle
    contents: List[PDFStream]
    boxcolor_info: Optional[PDFDictionary]
    rotate: PDFInteger
    metadata: Optional[PDFStream]
    user_unit: PDFReal

    raw: PDFDictionary
