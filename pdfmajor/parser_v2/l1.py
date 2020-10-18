import io
from pdfmajor.parser_v2.exceptions import ParserError
from pdfmajor.parser_v2.objects import (
    PDFArray,
    PDFContextualObject,
    PDFDictionary,
    PDFPrimivite,
    PDFObject,
)
from typing import Any, Iterator, List, Optional
from pdfmajor.lexer.token import (
    TArrayValue,
    TDictValue,
    TokenArray,
    TokenDictionary,
    TokenComplexType,
    TokenComplexTypeVal,
    is_primitive,
)
from pdfmajor.lexer import PDFLexer


class PDFL1Parser:
    """Level 1 PDF Parser"""

    def __init__(
        self, fp: io.BufferedIOBase, buffer_size: int = 4096, strict: bool = True
    ) -> None:
        self.lexer = PDFLexer(fp, buffer_size)
        self.strict = strict
        self.context_stack: List[PDFContextualObject] = []

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
        for token in self.lexer.iter_tokens():
            if is_primitive(token):
                cur_ctx = self.current_context
                obj = PDFPrimivite(token)  # type: ignore
                if cur_ctx is None:
                    yield obj
                else:
                    cur_ctx.pass_item(obj)
            elif isinstance(token, TokenArray):
                obj = self.__deal_with_obj(token, PDFArray, TArrayValue.OPEN)
                if obj is not None:
                    yield obj
            elif isinstance(token, TokenDictionary):
                obj = self.__deal_with_obj(token, PDFDictionary, TDictValue.OPEN)
                if obj is not None:
                    yield obj
            else:
                raise ParserError(f"Invalid token provided {token}")

    def __deal_with_obj(
        self,
        token: TokenComplexType,
        cls_const: Any,
        open_t: TokenComplexTypeVal,
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
            self.context_stack.append(cls_const())
        elif len(self.context_stack) > 0:
            last_ctx = self.context_stack.pop()
            if isinstance(last_ctx, cls_const):
                cur_ctx = self.current_context
                if cur_ctx is None:
                    return last_ctx
                else:
                    cur_ctx.pass_item(last_ctx)
            elif self.strict:
                raise ParserError(f"Invalid end of {cls_const} specified at {token}")
        elif self.strict:
            raise ParserError(
                f"Invalid end of {cls_const} specified at {token} with no start"
            )
