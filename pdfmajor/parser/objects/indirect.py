from typing import Optional

from pdfmajor.parser.stream import PDFStream

from .base import PDFContextualObject, PDFObject


class ObjectRef(PDFObject):
    """A class representing a reference for other objects"""

    def __init__(self, obj_num: int, gen_num: int) -> None:
        self.obj_num = obj_num
        self.gen_num = gen_num

    def __hash__(self):
        return hash(self.to_python())

    def to_python(self):
        return (self.obj_num, self.gen_num)


class IndirectObject(PDFContextualObject):
    """A class representing a referencable object"""

    def __init__(
        self,
        obj_num: int,
        gen_num: int,
        offset: int,
        data: Optional[PDFObject] = None,
        stream: Optional[PDFStream] = None,
    ) -> None:
        self.offset = offset
        self.obj_num = obj_num
        self.gen_num = gen_num
        self.__data = data
        self.stream = stream
        self.read: bool = False

    def __repr__(self) -> str:
        return f"IndirectObject(obj_num={self.obj_num}, gen_num={self.gen_num}, offset={self.offset}, data={self.get_object()})"

    def get_object(self) -> Optional[PDFObject]:
        return self.__data

    def save_object(self, obj: PDFObject):
        """This method will override the current stored object

        Args:
            obj (PDFObject)

        """
        self.__data = obj

    def to_python(self):
        data = self.get_object()
        if data is not None:
            data = data.to_python()
        return (self.obj_num, self.gen_num, self.offset, data)

    def pass_item(self, item: PDFObject):
        """This method will either propogate the item to it's child (in case the child is a contexual object) or override it's own data with the incoming

        Args:
            item (PDFObject): [description]
        """
        cur_obj = self.get_object()
        if isinstance(cur_obj, PDFContextualObject):
            cur_obj.pass_item(item)
        else:
            self.save_object(item)
