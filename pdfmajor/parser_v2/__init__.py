import io
from pdfmajor.parser_v2.exceptions import ParserError
from pdfmajor.parser_v2.objects import PDFArray, PDFDictionary, PDFPrimivite, PDFObject
from typing import Iterator, List, Optional
from pdfmajor.lexer.token import (
    TArrayValue,
    TDictValue,
    TokenArray,
    TokenDictionary,
    TokenPrimitive,
    is_primitive,
)
from pdfmajor.lexer import PDFLexer
from pdfmajor.parser_v2.context import PDFParseContext


class PDFParser:
    def __init__(
        self, fp: io.BufferedIOBase, buffer_size: int = 4096, strict: bool = True
    ) -> None:
        self.lexer = PDFLexer(fp, buffer_size)
        self.strict = strict
        self.context_stack: List[PDFParseContext] = []

    @property
    def current_context(self) -> Optional[PDFParseContext]:
        """Returns the current context of the parsing state

        Returns:
            Optional[PDFParseContext]
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
        """Iterates over the objects in the current stream

        Yields:
            [type]: [description]
        """
        for token in self.lexer.iter_tokens():
            if is_primitive(token):
                cur_ctx = self.current_context
                obj = PDFPrimivite(token)  # type: ignore
                if cur_ctx is None:
                    yield obj
                else:
                    cur_ctx.push(obj)
            elif isinstance(token, TokenArray):
                if token.value == TArrayValue.OPEN:
                    self.context_stack.append(PDFParseContext(PDFArray()))
                elif len(self.context_stack) > 0:
                    last_ctx = self.context_stack.pop()
                    if isinstance(last_ctx.pdfobject, PDFArray):
                        cur_ctx = self.current_context
                        if cur_ctx is None:
                            yield last_ctx.pdfobject
                        else:
                            cur_ctx.push(last_ctx.pdfobject)
                    elif self.strict:
                        raise ParserError(f"Invalid end of array specified at {token}")
                elif self.strict:
                    raise ParserError(
                        f"Invalid end of array specified at {token} with no start"
                    )
            elif isinstance(token, TokenDictionary):
                if token.value == TDictValue.OPEN:
                    self.context_stack.append(PDFParseContext(PDFDictionary()))
                elif len(self.context_stack) > 0:
                    last_ctx = self.context_stack.pop()
                    if isinstance(last_ctx.pdfobject, PDFDictionary):
                        cur_ctx = self.current_context
                        if cur_ctx is None:
                            yield last_ctx.pdfobject
                        else:
                            cur_ctx.push(last_ctx.pdfobject)
                    elif self.strict:
                        raise ParserError(
                            f"Invalid end of dictionary specified at {token}"
                        )
                elif self.strict:
                    raise ParserError(
                        f"Invalid end of dictionary specified at {token} with no start"
                    )
            else:
                raise ParserError(f"Invalid token provided {token}")
