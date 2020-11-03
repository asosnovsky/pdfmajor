from .base import PDFObject


class ObjectRef(PDFObject):
    """A class representing a reference for other objects"""

    def __init__(self, obj_num: int, gen_num: int) -> None:
        self.obj_num = obj_num
        self.gen_num = gen_num

    def __hash__(self):
        return hash(self.to_python())

    def to_python(self):
        return (self.obj_num, self.gen_num)
