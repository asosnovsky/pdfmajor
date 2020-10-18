from enum import Enum
from typing import Any, Generic, TypeVar, Union
from decimal import Decimal

T = TypeVar("T")


class Token(Generic[T]):
    """A generic class representing PDF Token"""

    __slots__ = ["start_loc", "end_loc", "value"]

    def __init__(self, start_loc: int, end_loc: int, value: T) -> None:
        self.start_loc = start_loc
        self.end_loc = end_loc
        self.value = value

    def __repr__(self) -> str:
        return (
            "{cls}(start_loc={start_loc}, end_loc={end_loc}, value='{value}')".format(
                cls=self.__class__.__name__,
                start_loc=self.start_loc,
                value=self.value,
                end_loc=self.end_loc,
            )
        )

    def __eq__(self, other: Any):
        if isinstance(other, self.__class__):
            return (
                (other.value == self.value)
                and (other.start_loc == self.start_loc)
                and (other.end_loc == self.end_loc)
            )
        else:
            return False


# Primitive Tokens
class TokenComment(Token[bytes]):
    """Token representing PDF comments
    Detection of this type of token can be found in PDF 1.7 spec section 7.2.3
    """

    pass


class TokenKeyword(Token[bytes]):
    """Token representing PDF comments
    Detection of this type of token can be found in PDF 1.7 spec
    """

    pass


class TokenName(Token[str]):
    """Token representing literal name tokens
    Detection of this type of token can be found in PDF 1.7 spec section 7.3.5
    """

    pass


class TokenBoolean(Token[bool]):
    """Token representing PDF booleans
    Detection of this type of token can be found in PDF 1.7 spec section 7.3.2
    """

    pass


class TokenNull(Token[None]):
    """Token representing the PDF null object
    Detection of this type of token can be found in PDF 1.7 spec section 7.3.9
    """

    pass


class TokenString(Token[str]):
    """Token representing PDF literal string
    Detection of this type of token can be found in PDF 1.7 spec section 7.3.4.2
    """

    pass


class TokenHexString(Token[bytes]):
    """Token representing PDF hex strings
    Detection of this type of token can be found in PDF 1.7 spec section 7.3.4.3
    """

    pass


class TokenInteger(Token[int]):
    """Token representing PDF integers
    Detection of this type of token can be found in PDF 1.7 spec section 7.3.3
    """

    pass


class TokenReal(Token[Decimal]):
    """Token representing PDF decimals
    Detection of this type of token can be found in PDF 1.7 spec section 7.3.3
    """

    pass


TokenNumber = Union[TokenInteger, TokenReal]
TokenPrimitive = Union[
    TokenComment,
    TokenKeyword,
    TokenName,
    TokenBoolean,
    TokenNull,
    TokenString,
    TokenHexString,
    TokenInteger,
    TokenReal,
]


def is_primitive(token: Token) -> bool:
    """determins is a token represents a primitive pdf object such as boolean, null, integer etc

    Args:
        token (Token)

    Returns:
        bool: True if primitive
    """
    for opt in [
        TokenComment,
        TokenKeyword,
        TokenName,
        TokenBoolean,
        TokenNull,
        TokenString,
        TokenHexString,
        TokenInteger,
        TokenReal,
    ]:
        if isinstance(token, opt):
            return True
    return False


# Tokens for complex objects
class TDictValue(Enum):
    OPEN = "<<"
    CLOSE = ">>"


class TokenDictionary(Token[TDictValue]):
    """Token representing the brackets of dictionary
    Detection of this type of token can be found in PDF 1.7 spec section 7.3.7
    """

    pass


class TArrayValue(Enum):
    OPEN = "["
    CLOSE = "]"


class TokenArray(Token[TArrayValue]):
    """Token representing the brackets of an array
    Detection of this type of token can be found in PDF 1.7 spec section 7.3.6
    """

    pass
