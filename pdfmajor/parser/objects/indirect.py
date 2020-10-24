from typing import Optional
from ..exceptions import InvalidIndirectObjAccess
from .base import PDFContextualObject, PDFObject
from .primitives import PDFNull


class IndirectObject(PDFContextualObject):
    """A class representing a reference for other objects"""

    def __init__(
        self,
        obj_num: int,
        gen_num: int,
        offset: int,
        data: Optional[PDFObject] = None,
    ) -> None:
        self.offset = offset
        self.obj_num = obj_num
        self.gen_num = gen_num
        self.__data = data

    def __repr__(self) -> str:
        return f"IndirectObject(obj_num={self.obj_num}, gen_num={self.gen_num}, offset={self.offset}, data={self.get_object()})"

    def get_object(self) -> Optional[PDFObject]:
        return self.__data

    def save_object(self, obj: PDFObject):
        # if self.__data is not None:
        #     raise InvalidIndirectObjAccess(
        #         f"attempted to override an initilized reference of an object {obj}"
        #     )
        self.__data = obj

    def into_readonly_copy(self):
        return IndirectObject(
            self.obj_num, self.gen_num, self.offset, self.get_object()
        )

    def to_python(self):
        obj = self.get_object()
        if obj is None:
            return None
        return obj.to_python()

    def pass_item(self, item: PDFObject):
        # if self.__read_only:
        #     raise InvalidIndirectObjAccess(
        #         f"attempted to add to an read-only reference of an object {item}"
        #     )
        cur_obj = self.get_object()
        if isinstance(cur_obj, PDFContextualObject):
            cur_obj.pass_item(item)
        else:
            self.save_object(item)
