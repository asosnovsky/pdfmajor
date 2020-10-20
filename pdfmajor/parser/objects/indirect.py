from typing import Dict, Tuple
from ..exceptions import InvalidIndirectObjAccess, ParserError
from .base import PDFContextualObject, PDFObject
from .primitives import PDFNull


class IndirectObjectCollection:
    """A class for collection references to objects"""

    def __init__(self) -> None:
        self.objs: Dict[Tuple[int, int], PDFObject] = {}

    def create_indobject(self, obj_num: int, gen_num: int) -> "IndirectObject":
        """Create an indirect object and store its value in the collection
        return the reference to where this object lies at

        Returns:
            IndirectObject:
        """
        return IndirectObject(self, obj_num, gen_num, read_only=False)

    def get_indobject(self, obj_num: int, gen_num: int) -> "IndirectObject":
        """creates a reference to an object

        Returns:
            IndirectObject
        """
        return IndirectObject(self, obj_num, gen_num, read_only=True)

    def get_object(self, obj_num: int, gen_num: int) -> PDFObject:
        """get the actual value of the reference, if the value does not exists return the Null object as specified in PDF spec 1.7 section 7.3.10

        Args:
            obj_num (int): object number
            gen_num (int): generation number

        Returns:
            PDFObject
        """
        return self.objs.get((obj_num, gen_num), PDFNull())


class IndirectObject(PDFContextualObject):
    """A class representing a reference for other objects"""

    def __init__(
        self,
        collection: IndirectObjectCollection,
        obj_num: int,
        gen_num: int,
        read_only: bool = True,
    ) -> None:
        self.obj_num = obj_num
        self.gen_num = gen_num
        self.__read_only = read_only
        self.__col = collection

    def __repr__(self) -> str:
        return f"IndirectObject({self.obj_num}, {self.gen_num})"

    def get_object(self) -> PDFObject:
        return self.__col.get_object(self.obj_num, self.gen_num)

    def save_object(self, obj: PDFObject):
        if self.__read_only:
            raise InvalidIndirectObjAccess(
                f"attempted to override a read-only reference of an object {obj}"
            )
        self.__col.objs[(self.obj_num, self.gen_num)] = obj

    def clone(self):
        return IndirectObject(self.__col, self.obj_num, self.gen_num, True)

    def to_python(self):
        return self.get_object().to_python()

    def pass_item(self, item: PDFObject):
        if self.__read_only:
            raise InvalidIndirectObjAccess(
                f"attempted to add to an read-only reference of an object {item}"
            )
        cur_obj = self.get_object()
        if isinstance(cur_obj, PDFContextualObject):
            cur_obj.pass_item(item)
        elif isinstance(cur_obj, PDFNull):
            self.save_object(item)
        else:
            raise InvalidIndirectObjAccess(f"Invalid redefinition of an object {item}")
