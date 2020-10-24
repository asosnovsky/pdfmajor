import io

from typing import Dict, Iterator, Optional, Tuple

from pdfmajor.streambuffer import BufferStream
from pdfmajor.parser.objects.stream import PDFStream
from pdfmajor.parser.exceptions import InvalidXref
from pdfmajor.parser.objects.base import PDFObject
from pdfmajor.lexer.token import TokenKeyword
from pdfmajor.lexer import PDFLexer
from pdfmajor.lexer.token import (
    TArrayValue,
    TDictValue,
    TokenArray,
    TokenComment,
    TokenDictionary,
    TokenKeyword,
)
from .objects.indirect import IndirectObject
from .objects.base import PDFContextualObject, PDFObject
from .objects.collections import PDFArray, PDFDictionary
from .objects.comment import PDFComment
from .state import ParsingState
from .parsers import attempt_parse_prim, deal_with_collection_object
from .exceptions import InvalidKeywordPos, BrokenFile, InvalidKeywordPos, ParserError


class XRefDB:
    """A class for collection references to objects"""

    def __init__(self, parser: "PDFParser") -> None:
        self.objs: Dict[Tuple[int, int], IndirectObject] = {}
        self.parser = parser

    def save_indobject(self, indobj: IndirectObject):
        if self.objs.get((indobj.obj_num, indobj.gen_num), None) is None:
            self.objs[(indobj.obj_num, indobj.gen_num)] = indobj

    def get_object_from_indobj(self, indobj: IndirectObject) -> PDFObject:
        return self.get_object(indobj.obj_num, indobj.gen_num)

    def get_object(self, obj_num: int, gen_num: int) -> PDFObject:
        """get the actual value of the reference, if the value does not exists return the Null object as specified in PDF spec 1.7 section 7.3.10

        Args:
            obj_num (int): object number
            gen_num (int): generation number

        Returns:
            PDFObject
        """
        indobj = self.objs.get((obj_num, gen_num), None)
        if indobj is None:
            raise InvalidXref(
                f"xref not found for object retrieval {obj_num}, {gen_num}"
            )
        else:
            obj = indobj.get_object()
            if obj is not None:
                return obj
            cur_pos = self.parser.tell()
            self.parser.seek(indobj.offset)
            obj = next(self.parser.iter_objects())
            indobj.save_object(obj)
            self.parser.seek(cur_pos)
            return obj


class PDFParser:
    """PDF Parser"""

    def __init__(
        self,
        buffer: BufferStream,
        db: Optional[XRefDB] = None,
        strict: bool = True,
    ) -> None:
        """

        Args:
            fp (io.BufferedIOBase)
            buffer_size (int, optional): the size of the reads. Defaults to 4096.
            state (Optional[ParsingState], optional): the parsing state. Defaults to None.
            strict (bool, optional): whether we want to throw errors over common decoding issues. Defaults to True.
        """
        self.lexer = PDFLexer(buffer)
        self.db = XRefDB(self)
        self.strict = strict

    @classmethod
    def from_iobuffer(
        cls,
        fp: io.BufferedIOBase,
        buffer_size: int = 4096,
        strict: bool = True,
    ):
        return cls(
            BufferStream(fp, buffer_size=buffer_size),
            strict=strict,
        )

    @classmethod
    def from_bytes(
        cls,
        data: bytes,
        buffer_size: int = 4096,
        strict: bool = True,
    ):
        return cls(
            BufferStream(io.BytesIO(data), buffer_size=buffer_size),
            strict=strict,
        )

    def seek(self, offset: int) -> int:
        """moves the offset of the reader to a certain spot, and returns the new offset

        Args:
            offset (int)

        Returns:
            int: new offset
        """
        return self.lexer.seek(offset)

    def tell(self) -> int:
        return self.lexer.tell()

    def iter_objects(self) -> Iterator[PDFObject]:
        """Iterates over the objects in the current byte stream

        Yields:
            PDFObject
        """
        state = ParsingState([], [], strict=self.strict)
        for token in self.lexer.iter_tokens():
            attempt_prim = attempt_parse_prim(token, state)
            if attempt_prim.success:
                yield from state.feed_or_yield_objs(attempt_prim.next_objs)
            elif isinstance(token, TokenComment):
                yield state.set_last_obj(
                    PDFComment(
                        token.value,
                        (token.start_loc, token.end_loc),
                    )
                )
            elif isinstance(token, TokenKeyword):
                if token.value == b"R":
                    yield from self._on_indirect_ref_close(state)
                elif token.value == b"obj":
                    state.initialize_indirect_obj(token.start_loc)
                elif token.value == b"endobj":
                    yield self._on_endobj(state, token)
                elif token.value == b"stream":
                    self._on_stream(
                        state,
                        token,
                    )
                elif token.value == b"endstream":
                    self._on_endstream(state, token)
                else:
                    raise InvalidKeywordPos(token)
            elif isinstance(token, TokenArray):
                yield from state.flush_int_collections()
                yield from deal_with_collection_object(
                    state, token, PDFArray, TArrayValue.OPEN, strict=self.strict
                )
            elif isinstance(token, TokenDictionary):
                yield from state.flush_int_collections()
                yield from deal_with_collection_object(
                    state,
                    token=token,
                    cls_const=PDFDictionary,
                    open_t=TDictValue.OPEN,
                    strict=self.strict,
                )

    def _on_endobj(self, state: ParsingState, token: TokenKeyword) -> IndirectObject:
        """finish off the current context, assuming we are handling an indirect-object

        Args:
            token (TokenKeyword)

        Raises:
            BrokenFile: if the object fif not get initilized with two integers
            InvalidKeywordPos: If the context is not an indirect object

        Yields:
            PDFObject
        """
        last_ctx = state.context_stack.pop()
        if isinstance(last_ctx, IndirectObject):
            if len(state.int_collection) > 1:
                raise BrokenFile(f"Invalid number of integers in obj defition {token}")
            for num in state.flush_int_collections():
                last_ctx.pass_item(num)
            obj = last_ctx.into_readonly_copy()
            self.db.save_indobject(obj)
            return obj
        else:
            raise InvalidKeywordPos(token)

    def _on_stream(self, state: ParsingState, token: TokenKeyword):
        """Initilize a PDFStream

        Args:
            token (TokenKeyword)

        Raises:
            ParserError: if the current context is not an indirect object
        """
        last_ctx = state.current_context
        if last_ctx is not None and isinstance(last_ctx, IndirectObject):
            self.db.save_indobject(last_ctx)
            stream = PDFStream(token.end_loc, 0)
            obj = self.db.get_object_from_indobj(last_ctx)
            stream.pass_item(obj)
            last_ctx.save_object(PDFStream(token.end_loc, 0))
            state.context_stack.append(stream)
            self.seek(stream.offset + stream.length)
        else:
            raise ParserError(f"PDFStream is missing initilization dictionary")

    def _on_endstream(self, state: ParsingState, token: TokenKeyword):
        """Finish a PDFStream

        Args:
            token (TokenKeyword)

        Raises:
            InvalidKeywordPos: if the current context is not an indirect stream
        """
        stream: PDFContextualObject = state.context_stack.pop()
        if not isinstance(stream, PDFStream):
            raise InvalidKeywordPos(token)

    def _on_indirect_ref_close(self, state: ParsingState):
        obj_num, gen_num = state.get_indobj_values()
        obj = self.db.get_object(obj_num, gen_num)
        cur_ctx = state.current_context
        if cur_ctx is not None:
            cur_ctx.pass_item(obj)
        else:
            yield obj
