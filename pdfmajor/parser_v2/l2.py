import io
from pdfmajor.parser_v2.l1 import PDFL1Parser
from pdfmajor.parser_v2.exceptions import ParserError
from pdfmajor.parser_v2.objects import (
    PDFComment,
    PDFContextualObject,
    PDFPrimitive,
    PDFObject,
)
from typing import Iterator, List, Tuple
from pdfmajor.lexer.token import (
    TokenInteger,
    TokenKeyword,
)
from pdfmajor.parser_v2.indirect_objects import IndirectObjectCollection


class PDFL2Parser:
    """Level 2 PDF Parser"""

    def __init__(
        self, fp: io.BufferedIOBase, buffer_size: int = 4096, strict: bool = True
    ) -> None:
        self.l1 = PDFL1Parser(fp, buffer_size, strict)
        self.strict = strict
        self.inobjects = IndirectObjectCollection()

    def seek(self, offset: int) -> int:
        """moves the offset of the reader to a certain spot, and returns the new offset

        Args:
            offset (int)

        Returns:
            int: new offset
        """
        return self.l1.seek(offset)

    def iter_objects(self) -> Iterator[PDFObject]:
        """Iterates over the objects in the current byte stream using level 2 parsing

        Yields:
            PDFObject
        """
        object_list: List[PDFObject] = []
        ctx_list: List[PDFContextualObject] = []
        for obj in self.l1.iter_objects():
            if isinstance(obj, TokenKeyword):
                if obj.value == b"obj":
                    if len(object_list) < 2:
                        raise ParserError("recieved 'obj' but missing leading tokens")
                    ctx_list.append(
                        self.inobjects.create_indobject(
                            *_get_indobj_values(object_list)
                        )
                    )
                elif obj.value == b"endobj":
                    if len(ctx_list) > 0:
                        last_ctx_obj = ctx_list.pop()
                        if len(ctx_list) > 0:
                            ctx_list[-1].pass_item(last_ctx_obj)
                        else:
                            yield last_ctx_obj.get_value()
                elif obj.value == b"R":
                    cur_indobj = self.inobjects.get_indobject(
                        *_get_indobj_values(object_list)
                    )
                    if len(ctx_list) > 0:
                        ctx_list[-1].pass_item(cur_indobj)
                    else:
                        yield cur_indobj.get_value()
            elif isinstance(obj, PDFComment):
                yield obj
            elif len(ctx_list) == 0:
                object_list.append(obj)
            elif len(ctx_list) > 0:
                ctx_list[-1].pass_item(obj)
            else:
                raise ParserError(f"Invalid obj provided {obj}")


def _get_indobj_values(object_list: List[PDFObject]) -> Tuple[int, int]:
    gen_num = object_list.pop()
    obj_num = object_list.pop()
    if isinstance(gen_num, PDFPrimitive) and isinstance(obj_num, PDFPrimitive):
        if isinstance(gen_num.token, TokenInteger) and isinstance(
            obj_num.token, TokenInteger
        ):
            return (obj_num.to_python(), gen_num.to_python())
    raise ParserError("missing leading tokens for object reference")
