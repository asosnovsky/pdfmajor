from decimal import Decimal
from typing import Dict, Generic, Optional, Type, TypeVar

from pdfmajor.lexer.token import (
    Token,
    TokenPrimitive,
    TokenBoolean,
    TokenHexString,
    TokenInteger,
    TokenName,
    TokenNull,
    TokenReal,
    TokenString,
)
from .base import PDFObject


T = TypeVar("T", str, bytes, int, bool, Decimal)


class PDFPrimitiveObject(PDFObject, Generic[T]):
    __slots__ = ("value", "start_loc", "end_loc")

    def __init__(self, value: T, start_loc: int, end_loc: int) -> None:
        self.value: T = value
        self.start_loc = start_loc
        self.end_loc = end_loc

    def to_python(self) -> T:
        return self.value

    @classmethod
    def from_token(cls, token: TokenPrimitive):
        return cls(
            value=token.value,  # type: ignore
            start_loc=token.start_loc,
            end_loc=token.end_loc,
        )


class PDFString(PDFPrimitiveObject[str]):
    pass


class PDFName(PDFPrimitiveObject[str]):
    def to_python(self):
        return "/" + self.value


class PDFBoolean(PDFPrimitiveObject[bool]):
    pass


class PDFHexString(PDFPrimitiveObject[bytes]):
    pass


class PDFInteger(PDFPrimitiveObject[int]):
    pass


class PDFReal(PDFPrimitiveObject[Decimal]):
    pass


class PDFNull(PDFObject):
    """A class representing a PDF null object"""

    def to_python(self):
        return None


_token_to_obj_map: Dict[Type[Token], Type[PDFPrimitiveObject]] = {
    TokenName: PDFName,
    TokenString: PDFString,
    TokenBoolean: PDFBoolean,
    TokenHexString: PDFHexString,
    TokenInteger: PDFInteger,
    TokenReal: PDFReal,
}


def get_obj_from_token_primitive(token: Token) -> Optional[PDFObject]:
    """converts tokens to their primitive object counterparts

    Args:
        token (Token)

    Returns:
        Optional[PDFObject]: None if could not match them
    """
    obj_const = _token_to_obj_map.get(type(token), None)
    if obj_const:
        return obj_const.from_token(token)  # type: ignore
    elif isinstance(token, TokenNull):
        return PDFNull()
    else:
        return None
