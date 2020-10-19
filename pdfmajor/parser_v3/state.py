from typing import Iterator, List, Optional, Tuple

from .exceptions import ParserError
from .objects.base import PDFContextualObject, PDFObject
from .objects.primitives import PDFInteger
from .objects.comment import PDFComment
from .objects.indirect import IndirectObject, IndirectObjectCollection


class ParsingState:

    __slots__ = [
        "context_stack",
        "int_collection",
        "last_obj",
        "indirect_object_collection",
    ]

    def __init__(
        self,
        context_stack: List[PDFContextualObject],
        int_collection: List[PDFInteger],
        last_obj: Optional[PDFObject] = None,
        indirect_object_collection: Optional[IndirectObjectCollection] = None,
    ) -> None:
        self.context_stack = context_stack
        self.int_collection = int_collection
        self.int_collection = int_collection
        self.last_obj = last_obj
        self.indirect_object_collection = (
            indirect_object_collection
            if indirect_object_collection is not None
            else IndirectObjectCollection()
        )

    @property
    def current_context(self) -> Optional[PDFContextualObject]:
        """Returns the current context of the parsing state

        Returns:
            Optional[PDFContextualObject]
        """
        if len(self.context_stack) > 0:
            return self.context_stack[-1]
        else:
            return None

    def set_last_obj(self, new_obj: PDFObject) -> PDFObject:
        """Set the value for the 'last object', special consideration for comments

        Args:
            new_obj (PDFObject)

        Returns:
            PDFObject
        """
        if isinstance(self.last_obj, PDFComment):
            self.last_obj.next_obj = new_obj
        elif isinstance(new_obj, PDFComment):
            new_obj.last_obj = self.last_obj
        self.last_obj = new_obj
        return new_obj

    def get_indobj_values(self) -> Tuple[int, int]:
        """Attempts to convert the values in self.int_collection to a tuple representing the generation and object number of an indirect object

        Raises:
            ParserError: if the int_collection does not have two elements

        Returns:
            Tuple[int, int]: (obj_num, gen_num)
        """
        if len(self.int_collection) == 2:
            gen_num = self.int_collection.pop()
            obj_num = self.int_collection.pop()
            return (obj_num.to_python(), gen_num.to_python())
        raise ParserError("missing leading tokens for object reference")

    def get_indobjects(self) -> IndirectObject:
        """Gets an indirect object, based on the values in 'self.int_collection'

        Raises:
            ParserError: if the int_collection does not have two elements

        Returns:
            IndirectObject
        """
        obj_num, gen_num = self.get_indobj_values()
        return self.indirect_object_collection.get_indobject(obj_num, gen_num)

    def initialize_indirect_obj(self):
        obj_num, gen_num = self.get_indobj_values()
        self.context_stack.append(
            self.indirect_object_collection.create_indobject(obj_num, gen_num)
        )

    def flush_int_collections(self) -> Iterator[PDFObject]:
        """clear out the int-collection

        Yields:
            PDFObject
        """
        cur_ctx = self.current_context
        if cur_ctx is not None:
            for obj in self.int_collection:
                cur_ctx.pass_item(obj)
        else:
            for obj in self.int_collection:
                yield obj
        self.int_collection = []
