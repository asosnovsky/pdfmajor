from enum import Enum
from typing import Any, Generic, TypeVar, Union
from decimal import Decimal

T = TypeVar("T")


class Token(Generic[T]):
    __slots__ = ["pos", "size", "value"]

    def __init__(self, pos: int, size: int, value: T) -> None:
        self.size = size
        self.pos = pos
        self.value = value

    def __repr__(self) -> str:
        return "{cls}(pos={pos}, size={size}, value={value})".format(
            cls=self.__class__.__name__, pos=self.pos, value=self.value, size=self.size
        )

    def __eq__(self, other: Any):
        if isinstance(other, self.__class__):
            return (
                (other.value == self.value)
                and (other.pos == self.pos)
                and (other.size == self.size)
            )
        else:
            return False


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


class TokenLiteral(Token[str]):
    """Token representing literal name tokens
    Detection of this type of token can be found in PDF 1.7 spec section 7.3.5
    """

    pass


class TokenBoolean(Token[bool]):
    """Token representing PDF booleans
    Detection of this type of token can be found in PDF 1.7 spec section 7.3.2
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
    Detection of this type of token can be found in PDF 1.7
    """

    pass


class TokenDecimal(Token[Decimal]):
    """Token representing PDF decimals
    Detection of this type of token can be found in PDF 1.7
    """

    pass


class TDictVaue(Enum):
    OPEN = "<<"
    CLOSE = ">>"


class TokenDictionary(Token[TDictVaue]):
    """Token representing the brackets of dictionary
    Detection of this type of token can be found in PDF 1.7 spec section 7.3.7
    """

    pass


TokenNumber = Union[TokenInteger, TokenDecimal]
