from typing import Iterator, List, NamedTuple, Type

from pdfmajor.lexer.token import Token, TokenComplexType, TokenComplexTypeVal

from .state import ParsingState
from .exceptions import ParserError
from .objects.base import PDFObject
from .objects.base import PDFContextualObject, PDFObject
from .objects.primitives import PDFInteger, get_obj_from_token_primitive


class ParsingAttempt(NamedTuple):
    success: bool
    next_objs: List[PDFObject]


def attempt_parse_prim(token: Token, state: ParsingState) -> ParsingAttempt:
    """Attempt to parse out a primitive value from the token

    Args:
        token (Token): [description]
        state (ParsingState): [description]

    Returns:
        ParsingAttempt
    """
    prim_obj = get_obj_from_token_primitive(token)
    if prim_obj is not None:
        out: List[PDFObject] = []
        state.set_last_obj(prim_obj)
        if isinstance(prim_obj, PDFInteger):
            if len(state.int_collection) <= 1:
                state.int_collection.append(prim_obj)
            else:
                for obj in state.flush_int_collections():
                    out.append(obj)
        else:
            for obj in state.flush_int_collections():
                out.append(obj)
            out.append(prim_obj)
        return ParsingAttempt(True, out)
    return ParsingAttempt(False, [])


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
