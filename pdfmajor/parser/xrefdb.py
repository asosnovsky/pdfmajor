from pdfmajor.parser.xref import XRefRow

from typing import Dict, Iterator, Tuple

from pdfmajor.parser.exceptions import InvalidXref
from pdfmajor.parser.objects.base import PDFObject
from .objects.indirect import IndirectObject
from .objects.base import PDFObject


class XRefDB:
    """A class for collection references to objects"""

    def __init__(self) -> None:
        self.objs: Dict[Tuple[int, int], IndirectObject] = {}
        self.xrefs: Dict[Tuple[int, int], XRefRow] = {}

    def update_from_xrefiter(self, it_xref: Iterator[XRefRow]):
        for xref in it_xref:
            if xref.use == b"n":
                self.xrefs[(xref.obj_num, xref.gen_num)] = xref

    def save_indobject(self, indobj: IndirectObject):
        if self.objs.get((indobj.obj_num, indobj.gen_num), None) is None:
            self.objs[(indobj.obj_num, indobj.gen_num)] = indobj
        else:
            print("WARN: saving twice", indobj)
