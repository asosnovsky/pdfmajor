from typing import Iterator, List, Optional, Tuple

from .exceptions import ParserError
from .objects.base import PDFContextualObject, PDFObject
from .objects.primitives import PDFInteger
from .objects.comment import PDFComment
from .objects.indirect import IndirectObject


class ParsingState:

    __slots__ = ["context_stack", "int_collection", "last_obj", "strict"]

    def __init__(
        self,
        context_stack: List[PDFContextualObject],
        int_collection: List[PDFInteger],
        last_obj: Optional[PDFObject] = None,
        strict: bool = False,
    ) -> None:
        self.context_stack = context_stack
        self.int_collection = int_collection
        self.last_obj = last_obj
        self.strict = strict

    def __repr__(self) -> str:
        return "ParsingState:[{stackc}]({cur_stack}, ints={ints}, last={lobj}, strict={strict})".format(
            stackc=len(self.context_stack),
            cur_stack=self.current_context,
            ints=self.int_collection,
            lobj=self.last_obj,
            strict=self.strict,
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

    def initialize_indirect_obj(self, offset: int):
        """Initilizes an indirect object based off the values in self.int_collection

        Args:
            offset (int): position for the 'obj' keyword
        """
        obj_num, gen_num = self.get_indobj_values()
        self.context_stack.append(
            IndirectObject(obj_num=obj_num, gen_num=gen_num, offset=offset)
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

    def feed_or_yield_objs(self, next_objs: List[PDFObject]) -> Iterator[PDFObject]:
        """If there context, then feed the objects into it, otherwise yield them

        Args:
            next_objs (List[PDFObject])

        Yields:
            PDFObject
        """
        cur_ctx = self.current_context
        for obj in next_objs:
            if cur_ctx is not None:
                cur_ctx.pass_item(obj)
            else:
                yield obj
