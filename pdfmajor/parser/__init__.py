from pdfmajor.parser.stream.PDFStream import PDFStream
from pdfmajor.parser.xref import XRefRow
from pdfmajor.parser.xrefdb import XRefDB
from typing import Iterator, Optional
from pdfmajor.streambuffer import BufferStream
from pdfmajor.lexer.token import (
    TArrayValue,
    TDictValue,
    TokenArray,
    TokenComment,
    TokenDictionary,
    TokenKeyword,
)
from pdfmajor.lexer import iter_tokens
from .objects.indirect import IndirectObject
from .objects.base import PDFObject
from .objects.collections import PDFArray, PDFDictionary
from .objects.comment import PDFComment
from .state import ParsingState
from .parsers import attempt_parse_prim, deal_with_collection_object
from .exceptions import (
    InvalidKeywordPos,
    BrokenFile,
    InvalidKeywordPos,
    InvalidXref,
    ParserError,
)


def iter_objects(
    buffer: BufferStream,
    xrefdb: XRefDB,
    state: Optional[ParsingState] = None,
) -> Iterator[PDFObject]:
    """Iterates over the objects in the current byte stream

    Yields:
        PDFObject
    """
    state = ParsingState([], []) if state is None else state
    for token in iter_tokens(buffer):
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
                yield from _on_indirect_ref_close(buffer, state, xrefdb)
            elif token.value == b"obj":
                state.initialize_indirect_obj(token.start_loc)
            elif token.value == b"endobj":
                obj = _on_endobj(state, token)
                xrefdb.save_indobject(obj)
                yield obj
            elif token.value == b"stream":
                _on_stream(
                    buffer,
                    state,
                    xrefdb,
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


def _on_endobj(state: ParsingState, token: TokenKeyword) -> IndirectObject:
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
        return last_ctx
    else:
        raise ParserError(f"Recived an endobj while not procesing an indirect object")


def _on_stream(
    buffer: BufferStream, state: ParsingState, xrefdb: XRefDB, token: TokenKeyword
):
    """Initilize a PDFStream

    Args:
        token (TokenKeyword)

    Raises:
        ParserError: if the current context is not an indirect object
    """
    last_ctx = state.current_context
    if last_ctx is not None and isinstance(last_ctx, IndirectObject):
        xrefdb.save_indobject(last_ctx)
        # stream = PDFStream(token.end_loc + 1, 0)
        obj = _save_or_get_object(buffer, xrefdb, last_ctx.obj_num, last_ctx.gen_num)
        last_ctx.stream = stream = PDFStream.from_pdfdict(token.end_loc, obj)
        buffer.seek(stream.offset + stream.length)
        next_token = next(iter_tokens(buffer))
        if not (
            isinstance(next_token, TokenKeyword) and next_token.value == b"endstream"
        ):
            raise BrokenFile(
                f"stream did not contain 'endstream', instead the token {next_token} was found"
            )
    else:
        raise ParserError(f"PDFStream is missing initilization dictionary")


def _on_indirect_ref_close(buffer: BufferStream, state: ParsingState, xrefdb: XRefDB):
    obj_num, gen_num = state.get_indobj_values()
    obj = _save_or_get_object(buffer, xrefdb, obj_num, gen_num)
    cur_ctx = state.current_context
    if cur_ctx is not None:
        cur_ctx.pass_item(obj)
    else:
        yield obj


def _save_or_get_object(
    buffer: BufferStream, xrefdb: XRefDB, obj_num: int, gen_num: int
) -> PDFObject:
    """get the actual value of the reference, if the value does not exists return the Null object as specified in PDF spec 1.7 section 7.3.10

    Args:
        obj_num (int): object number
        gen_num (int): generation number

    Returns:
        PDFObject
    """
    indobj = xrefdb.objs.get((obj_num, gen_num), None)
    if indobj is None:
        xref = xrefdb.xrefs.get((obj_num, gen_num), None)
        if xref is None:
            raise InvalidXref(
                f"xref not found for object retrieval {obj_num}, {gen_num}"
            )
        return _read_object_from_xref(xref, xrefdb, buffer)
    else:
        return _read_object_from_db_or_buffer(indobj, xrefdb, buffer)


def _read_object_from_xref(
    xref: XRefRow, xrefdb: XRefDB, buffer: BufferStream
) -> PDFObject:
    indobj = IndirectObject(xref.obj_num, xref.gen_num, xref.offset)
    with buffer.get_window():
        buffer.seek(indobj.offset)
        obj = next(iter_objects(buffer, xrefdb))
        indobj.save_object(obj)
        xrefdb.save_indobject(indobj)
        return obj


def _read_object_from_db_or_buffer(
    indobj: IndirectObject, xrefdb: XRefDB, buffer: BufferStream
) -> PDFObject:
    obj = indobj.get_object()
    if obj is not None:
        return obj
    with buffer.get_window():
        buffer.seek(indobj.offset)
        obj = next(iter_objects(buffer, xrefdb))
        indobj.save_object(obj)
        return obj
