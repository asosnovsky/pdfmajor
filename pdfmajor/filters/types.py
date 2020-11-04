from abc import ABCMeta
from typing import Any, Dict, Tuple

from .exceptions import InvalidDecoderOrNotImplemented


class PDFFilterDecoder(metaclass=ABCMeta):
    @staticmethod
    def decode(data: bytes, **decode_params: Any) -> bytes:
        raise InvalidDecoderOrNotImplemented


FilterPair = Tuple[str, Dict[str, Any]]
