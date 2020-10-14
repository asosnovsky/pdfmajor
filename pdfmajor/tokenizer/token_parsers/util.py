from pdfmajor.tokenizer.exceptions import TokenizerEOF
from pdfmajor.tokenizer.token import Token
from typing import Callable, Iterator, NamedTuple


class PInput(NamedTuple):
    pos: int
    buf: bytes


ParserFunc = Callable[[int, Iterator[PInput]], Token]


def cmp_tsize(curpos: int, initialpos: int, tokenend_idx: int) -> int:
    """Computes the size of the token based on its positional data

    Args:
            curpos (int): current position of the buffer
            initialpos (int): initial position where the parser started working
            tokenend_idx (int): last relevant character index within the last buffered value

    Returns:
            int: length of index
    """
    return curpos - initialpos + tokenend_idx


class SafeBufferIt:
    __slots__ = ["skip", "buffer"]

    def __init__(self, buffer: bytes, skip: int = 0) -> None:
        self.skip = skip
        self.buffer = buffer

    def into_iter(self) -> Iterator[bytes]:
        for i in range(len(self.buffer) + 1):
            if i > len(self.buffer):
                raise TokenizerEOF("Max Iteration Reached!")
            if self.skip >= len(self.buffer):
                break
            yield self.buffer[self.skip :]
