from typing import Generic, TypeVar, Union
from decimal import Decimal

T = TypeVar("T")


class Token(Generic[T]):
    __slots__ = ["pos", "size", "value"]

    def __init__(self, pos: int, size: int, value: T) -> None:
        self.size = size
        self.pos = pos
        self.value = value

    def __repr__(self) -> str:
        return "<{cls} pos={pos}>{value}</{cls}>".format(
            cls=self.__class__.__name__, pos=self.pos, value=self.value
        )


class TokenComment(Token[bytes]):
    pass


class TokenHex(Token[bytes]):
    pass


class TokenKeyword(Token[bytes]):
    pass


class TokenLiteral(Token[str]):
    pass


class TokenBoolean(Token[bool]):
    pass


class TokenString(Token[str]):
    pass


class TokenInteger(Token[int]):
    pass


class TokenDecimal(Token[Decimal]):
    pass


TokenNumber = Union[TokenInteger, TokenDecimal]
