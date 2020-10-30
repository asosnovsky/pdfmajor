from decimal import Decimal
from pdfmajor.document.exceptions import BrokenFilePDF, TooManyRectField
from pdfmajor.parser.objects.primitives import PDFInteger, PDFReal
from typing import List, NamedTuple
from pdfmajor.parser.objects.collections import PDFArray


class PDFRectangle(NamedTuple):
    """A PDF Rectangle as specified by PDF spec 1.7 section 7.9.5"""

    llx: Decimal
    lly: Decimal
    urx: Decimal
    ury: Decimal

    @classmethod
    def from_pdfarray(cls, arr: PDFArray):
        vals: List[Decimal] = []
        for obj in arr:
            if isinstance(obj, PDFInteger):
                vals.append(Decimal(obj.to_python()))
            elif isinstance(obj, PDFReal):
                vals.append(obj.to_python())
            else:
                raise BrokenFilePDF(f"Invalid type for initilizing rectangle {obj}")
        if len(vals) > 4:
            raise TooManyRectField(vals)
        elif len(vals) < 4:
            raise BrokenFilePDF(
                f"Insufficient number of fields for rectangle {arr} {vals}"
            )
        return cls(*vals)
