from typing import Dict, Iterator, Tuple

from pdfmajor.parser.objects.indirect import IndirectObject
from .xref import XRefRow
from .exceptions import InvalidIndirectObjAccess


class XRefDB:
    """A class for collection references to objects"""

    def __init__(self) -> None:
        self.objs: Dict[Tuple[int, int], IndirectObject] = {}
        self.xrefs: Dict[Tuple[int, int], XRefRow] = {}

    @classmethod
    def from_xrefiter(cls, it_xref: Iterator[XRefRow]) -> "XRefDB":
        db = cls()
        db.update_from_xrefiter(it_xref)
        return db

    def has_xref(self, obj_num: int, gen_num: int) -> bool:
        return (obj_num, gen_num) in self.xrefs.keys()

    def has_obj(self, obj_num: int, gen_num: int) -> bool:
        return (obj_num, gen_num) in self.objs.keys()

    def update_from_xrefiter(self, it_xref: Iterator[XRefRow]):
        for xref in it_xref:
            if xref.use == b"n":
                self.xrefs[(xref.obj_num, xref.gen_num)] = xref

    def create_indobject(
        self, obj_num: int, gen_num: int, offset: int
    ) -> IndirectObject:
        if self.has_obj(obj_num, gen_num):
            raise InvalidIndirectObjAccess(
                f"Attempted to recreate {(obj_num, gen_num)}"
            )
        cur_obj = self.objs[(obj_num, gen_num)] = IndirectObject(
            obj_num, gen_num, offset
        )
        return cur_obj

    def get_or_create_indobject(self, obj_num: int, gen_num: int) -> IndirectObject:
        cur_obj = self.objs.get((obj_num, gen_num), None)
        if cur_obj is None:
            print("WARN: got a non-existent reference")
            cur_obj = self.objs[(obj_num, gen_num)] = IndirectObject(
                obj_num, gen_num, -1
            )
        return cur_obj
