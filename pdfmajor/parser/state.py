from typing import Iterator, List, Optional, Tuple, Union

from pdfmajor.healthlog import PDFHealthReport

from .exceptions import ParserError
from .objects import (
    IndirectObject,
    PDFComment,
    PDFContextualObject,
    PDFInteger,
    PDFObject,
)


class ParsingState:

    __slots__ = ["context_stack", "int_collection", "last_obj", "health_report"]

    def __init__(
        self,
        context_stack: List[PDFContextualObject],
        int_collection: List[Union[PDFInteger, int]],
        last_obj: Optional[PDFObject] = None,
        health_report: Optional[PDFHealthReport] = None,
    ) -> None:
        self.context_stack = context_stack
        self.int_collection = int_collection
        self.last_obj = last_obj
        self.health_report = (
            health_report if health_report is not None else PDFHealthReport()
        )

    def __repr__(self) -> str:
        return "ParsingState:[{stackc}]({cur_stack}, ints={ints}, last={lobj})".format(
            stackc=len(self.context_stack),
            cur_stack=self.current_context,
            ints=self.int_collection,
            lobj=self.last_obj,
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
            if isinstance(gen_num, PDFInteger):
                gen_num = gen_num.to_python()
            obj_num = self.int_collection.pop()
            if isinstance(obj_num, PDFInteger):
                obj_num = obj_num.to_python()
            return (obj_num, gen_num)
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

    def flush_int_collections(self, up_to: int = 0) -> Iterator[PDFObject]:
        """clear out the int-collection

        Yields:
            PDFObject
        """
        cur_ctx = self.current_context
        if cur_ctx is not None:
            while len(self.int_collection) > up_to:
                obj = self.int_collection.pop(0)
                if not isinstance(obj, PDFInteger):
                    raise ParserError(
                        f"Invalid int-collection contains none PDFInteger types {obj}"
                    )
                cur_ctx.pass_item(obj)
        else:
            while len(self.int_collection) > up_to:
                obj = self.int_collection.pop(0)
                if not isinstance(obj, PDFInteger):
                    raise ParserError(
                        f"Invalid int-collection contains none PDFInteger types {obj}"
                    )
                yield obj

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
