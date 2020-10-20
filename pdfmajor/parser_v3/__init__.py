import io
from pdfmajor.parser_v3.objects.stream import PDFStream
from typing import Iterator, Optional

from pdfmajor.lexer import PDFLexer
from pdfmajor.lexer.token import (
    TArrayValue,
    TDictValue,
    TokenArray,
    TokenComment,
    TokenDictionary,
    TokenKeyword,
)

from .state import ParsingState
from .parsers import attempt_parse_prim, deal_with_collection_object
from .exceptions import ParserError

from .objects.base import PDFObject
from .objects.collections import PDFArray, PDFDictionary
from .objects.comment import PDFComment
from .objects.indirect import IndirectObject


class PDFParser:
    """PDF Parser"""

    def __init__(
        self,
        fp: io.BufferedIOBase,
        buffer_size: int = 4096,
        state: Optional[ParsingState] = None,
        strict: bool = True,
    ) -> None:
        self.lexer = PDFLexer(fp, buffer_size)
        self.strict = strict
        self.state = ParsingState([], []) if state is None else state

    def seek(self, offset: int, state: Optional[ParsingState] = None) -> int:
        """moves the offset of the reader to a certain spot, and returns the new offset

        Args:
            offset (int)

        Returns:
            int: new offset
        """
        self.state = ParsingState([], []) if state is None else state
        return self.lexer.seek(offset)

    def iter_objects(self) -> Iterator[PDFObject]:
        """Iterates over the objects in the current byte stream using level 1 parsing

        Yields:
            PDFObject
        """
        for token in self.lexer.iter_tokens():
            attempt_prim = attempt_parse_prim(token, self.state)
            if attempt_prim.success:
                cur_ctx = self.state.current_context
                for obj in attempt_prim.next_objs:
                    if cur_ctx is not None:
                        cur_ctx.pass_item(obj)
                    else:
                        yield obj
            elif isinstance(token, TokenComment):
                yield self.state.set_last_obj(
                    PDFComment(
                        token.value,
                        (token.start_loc, token.end_loc),
                    )
                )
            elif isinstance(token, TokenKeyword):
                if token.value == b"R":
                    obj = self.state.get_indobjects()
                    cur_ctx = self.state.current_context
                    if cur_ctx is not None:
                        cur_ctx.pass_item(obj)
                    else:
                        yield obj
                elif token.value == b"obj":
                    self.state.initialize_indirect_obj()
                elif token.value == b"endobj":
                    last_ctx = self.state.context_stack.pop()
                    if isinstance(last_ctx, IndirectObject):
                        yield last_ctx.clone()
                    elif self.strict:
                        raise ParserError(f"Invalid position for 'endobj' {token}")
                elif token.value == b"stream":
                    last_ctx = self.state.current_context
                    if last_ctx is not None and isinstance(last_ctx, IndirectObject):
                        stream = PDFStream(token.end_loc, 0)
                        stream.pass_item(last_ctx.get_object())
                        last_ctx.save_object(PDFStream(token.end_loc, 0))
                        self.state.context_stack.append(stream)
                        self.lexer.seek(stream.offset + stream.length)
                    else:
                        raise ParserError(
                            f"PDFStream is missing initilization dictionary"
                        )
                elif token.value == b"endstream":
                    stream = self.state.context_stack.pop()
                    if not isinstance(stream, PDFStream):
                        raise ParserError(f"Invalid position for 'endstream' {token}")
                else:
                    raise ParserError(f"Invalud Keyword {token}")
            elif isinstance(token, TokenArray):
                for obj in self.state.flush_int_collections():
                    yield obj
                obj = deal_with_collection_object(
                    self.state, token, PDFArray, TArrayValue.OPEN, strict=self.strict
                )
                if obj is not None:
                    yield obj
            elif isinstance(token, TokenDictionary):
                for obj in self.state.flush_int_collections():
                    yield obj
                obj = deal_with_collection_object(
                    self.state,
                    token=token,
                    cls_const=PDFDictionary,
                    open_t=TDictValue.OPEN,
                    strict=self.strict,
                )
                if obj is not None:
                    yield obj
