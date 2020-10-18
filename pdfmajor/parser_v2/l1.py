import io
from pdfmajor.parser_v2.exceptions import ParserError
from pdfmajor.parser_v2.objects import (
    PDFArray,
    PDFComment,
    PDFContextualObject,
    PDFDictionary,
    PDFKeyword,
    PDFNull,
    PDFPrimitive,
    PDFObject,
)
from typing import Any, Iterator, List, Optional, Type
from pdfmajor.lexer.token import (
    TArrayValue,
    TDictValue,
    TokenArray,
    TokenComment,
    TokenDictionary,
    TokenComplexType,
    TokenComplexTypeVal,
    TokenKeyword,
    TokenNull,
    is_primitive,
)
from pdfmajor.lexer import PDFLexer


def _deal_with_obj(
    context_stack: List[PDFContextualObject],
    token: TokenComplexType,
    cls_const: Type[PDFContextualObject],
    open_t: TokenComplexTypeVal,
    strict: bool = False,
) -> Optional[PDFObject]:
    """generic method for processing things that have a start and end token

    Args:
        token (TokenComplexType)
        cls_const (Any): the class constructor for the object
        open_t (TokenComplexTypeVal): the value represnting 'open' for the object

    Returns:
        Optional[PDFObject]
    """
    if token.value == open_t:
        context_stack.append(cls_const())
    elif len(context_stack) > 0:
        last_ctx = context_stack.pop()
        if isinstance(last_ctx, cls_const):
            cur_ctx = _get_curr_context(context_stack)
            if cur_ctx is None:
                return last_ctx
            else:
                cur_ctx.pass_item(last_ctx)
        elif strict:
            raise ParserError(f"Invalid end of {cls_const} specified at {token}")
    elif strict:
        raise ParserError(
            f"Invalid end of {cls_const} specified at {token} with no start"
        )
    return None


def _get_curr_context(
    context_stack: List[PDFContextualObject],
) -> Optional[PDFContextualObject]:
    """Returns the current context of the parsing state

    Returns:
        Optional[PDFContextualObject]
    """
    if len(context_stack) > 0:
        return context_stack[-1]
    else:
        return None


class PDFL1Parser:
    """Level 1 PDF Parser"""

    def __init__(
        self, fp: io.BufferedIOBase, buffer_size: int = 4096, strict: bool = True
    ) -> None:
        self.lexer = PDFLexer(fp, buffer_size)
        self.strict = strict

    def seek(self, offset: int) -> int:
        """moves the offset of the reader to a certain spot, and returns the new offset

        Args:
            offset (int)

        Returns:
            int: new offset
        """
        return self.lexer.seek(offset)

    def iter_objects(self) -> Iterator[PDFObject]:
        """Iterates over the objects in the current byte stream using level 1 parsing

        Yields:
            PDFObject
        """
        context_stack: List[PDFContextualObject] = []
        for token in self.lexer.iter_tokens():
            if is_primitive(token):
                cur_ctx = _get_curr_context(context_stack)
                obj = PDFPrimitive(token)  # type: ignore
                if cur_ctx is None:
                    yield obj
                else:
                    cur_ctx.pass_item(obj)
            elif isinstance(token, TokenComment):
                yield PDFComment(token)
            elif isinstance(token, TokenKeyword):
                yield PDFKeyword(token)
            elif isinstance(token, TokenNull):
                yield PDFNull()
            elif isinstance(token, TokenArray):
                obj = _deal_with_obj(
                    context_stack, token, PDFArray, TArrayValue.OPEN, strict=self.strict
                )
                if obj is not None:
                    yield obj
            elif isinstance(token, TokenDictionary):
                obj = _deal_with_obj(
                    context_stack=context_stack,
                    token=token,
                    cls_const=PDFDictionary,
                    open_t=TDictValue.OPEN,
                    strict=self.strict,
                )
                if obj is not None:
                    yield obj
            else:
                raise ParserError(f"Invalid token provided {token}")
