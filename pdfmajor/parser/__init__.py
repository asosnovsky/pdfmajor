from typing import Iterator, Optional

from pdfmajor.lexer import iter_tokens
from pdfmajor.lexer.token import (
    TArrayValue,
    TDictValue,
    TokenArray,
    TokenComment,
    TokenDictionary,
    TokenKeyword,
)
from pdfmajor.parser.objects.primitives import get_obj_from_token_primitive
from pdfmajor.streambuffer import BufferStream

from .exceptions import InvalidKeywordPos
from .objects.base import PDFObject
from .objects.collections import PDFArray, PDFDictionary
from .objects.comment import PDFComment
from .parsers import (
    deal_with_collection_object,
    on_endobj,
    on_indirect_ref_close,
    on_primitive,
    on_stream,
)
from .state import ParsingState


def get_first_object(
    buffer: BufferStream, offset: int, state: Optional[ParsingState] = None
) -> PDFObject:
    buffer.seek(offset)
    return next(iter_objects(buffer, state))


def iter_objects(
    buffer: BufferStream,
    state: Optional[ParsingState] = None,
) -> Iterator[PDFObject]:
    """Iterates over the objects in the current byte stream

    Yields:
        PDFObject
    """
    state = ParsingState([], []) if state is None else state
    for token in iter_tokens(buffer):
        prim_obj = get_obj_from_token_primitive(token)
        if prim_obj is not None:
            yield from on_primitive(prim_obj, state)
        elif isinstance(token, TokenComment):
            yield state.set_last_obj(
                PDFComment(
                    token.value,
                    (token.start_loc, token.end_loc),
                )
            )
        elif isinstance(token, TokenKeyword):
            if token.value == b"R":
                yield from on_indirect_ref_close(state)
            elif token.value == b"obj":
                state.initialize_indirect_obj(token.start_loc)
            elif token.value == b"endobj":
                obj = on_endobj(state, token)
                yield obj
            elif token.value == b"stream":
                yield from on_stream(
                    buffer,
                    state,
                    token,
                )
            else:
                raise InvalidKeywordPos(token, [b"R", b"obj", b"endobj", b"stream"])
        elif isinstance(token, TokenArray):
            yield from state.flush_int_collections()
            yield from deal_with_collection_object(
                state, token, PDFArray, TArrayValue.OPEN
            )
        elif isinstance(token, TokenDictionary):
            yield from state.flush_int_collections()
            yield from deal_with_collection_object(
                state,
                token=token,
                cls_const=PDFDictionary,
                open_t=TDictValue.OPEN,
            )
