from typing import Iterator, List, NamedTuple, Type, Union

from pdfmajor.lexer import iter_tokens
from pdfmajor.lexer.token import (
    Token,
    TokenComplexType,
    TokenComplexTypeVal,
    TokenKeyword,
)
from pdfmajor.streambuffer import BufferStream

from .exceptions import BrokenFile, EarlyStop, ParserError
from .objects.base import PDFContextualObject, PDFObject
from .objects.collections import PDFDictionary
from .objects.indirect import IndirectObject, ObjectRef
from .objects.primitives import (
    PDFInteger,
    PDFNull,
    PDFPrimitiveObject,
    get_obj_from_token_primitive,
)
from .state import ParsingState
from .stream.PDFStream import PDFStream


def on_primitive(
    pobj: Union[PDFPrimitiveObject, PDFNull], state: ParsingState
) -> Iterator[PDFObject]:
    """Parses out a primitive value from the token

    Args:
        pobj (PDFPrimitiveObject)
        state (ParsingState)

    Yields:
        Iterator[PDFObject]
    """
    state.set_last_obj(pobj)
    if isinstance(pobj, PDFInteger):
        for obj in state.flush_int_collections(1):
            yield obj
        state.int_collection.append(pobj)
    else:
        for obj in state.flush_int_collections():
            yield obj
        cur_ctx = state.current_context
        if cur_ctx is not None:
            cur_ctx.pass_item(pobj)
        else:
            yield pobj


def deal_with_collection_object(
    state: ParsingState,
    token: TokenComplexType,
    cls_const: Type[PDFContextualObject],
    open_t: TokenComplexTypeVal,
) -> Iterator[PDFObject]:
    """generic method for processing things that have a start and end token

    Args:
        token (TokenComplexType)
        cls_const (Any): the class constructor for the object
        open_t (TokenComplexTypeVal): the value represnting 'open' for the object

    Returns:
        Optional[PDFObject]
    """
    if token.value == open_t:
        state.context_stack.append(cls_const())
    elif len(state.context_stack) > 0:
        last_ctx = state.context_stack.pop()
        if isinstance(last_ctx, cls_const):
            cur_ctx = state.current_context
            if cur_ctx is None:
                yield last_ctx
                return
            else:
                cur_ctx.pass_item(last_ctx)
        else:
            raise ParserError(f"Invalid end of {cls_const} specified at {token}")
    else:
        raise ParserError(
            f"Invalid end of {cls_const} specified at {token} with no start"
        )


def on_endobj(state: ParsingState, token: TokenKeyword) -> IndirectObject:
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


def on_stream(buffer: BufferStream, state: ParsingState, token: TokenKeyword):
    """Initilize a PDFStream

    Args:
        token (TokenKeyword)

    Raises:
        ParserError: if the current context is not an indirect object
    """
    last_ctx = state.current_context
    if last_ctx is not None and isinstance(last_ctx, IndirectObject):
        obj = last_ctx.get_object()
        if not isinstance(obj, PDFDictionary):
            raise ParserError(f"Cannot initilize a pdfstream with {type(obj)}")
        last_ctx.stream = stream = PDFStream.from_pdfdict(token.end_loc + 1, obj)
        if isinstance(stream.length, PDFInteger):
            buffer.seek(stream.offset + stream.length.to_python())
            next_token = None
            for i, next_token in enumerate(iter_tokens(buffer)):
                if (
                    isinstance(next_token, TokenKeyword)
                    and next_token.value == b"endstream"
                ):
                    if i > 0:
                        stream.length.value = next_token.start_loc - stream.offset
                        state.health_report.write(
                            issue_name="InvalidPDFStreamLength",
                            additional_info=f"""
                            start_token={token}
                            end_token={next_token}
                            object_dictionary={obj}
                        """,
                        )
                    break
            if not (
                isinstance(next_token, TokenKeyword)
                and next_token.value == b"endstream"
            ):
                raise BrokenFile(
                    f"stream did not contain 'endstream', instead the token {next_token} was found"
                )
        elif isinstance(stream.length, ObjectRef):
            yield last_ctx
            raise EarlyStop(
                "cannot proceed parsing as the stream.length object is an indirect object"
            )
    else:
        raise ParserError(f"PDFStream is missing initilization dictionary")


def on_indirect_ref_close(state: ParsingState):
    obj_num, gen_num = state.get_indobj_values()
    obj = ObjectRef(obj_num, gen_num)
    cur_ctx = state.current_context
    if cur_ctx is not None:
        cur_ctx.pass_item(obj)
    else:
        yield obj
