from abc import ABCMeta
from typing import Any

from .exceptions import InvalidDecoderOrNotImplemented


class PDFFilterDecoder(metaclass=ABCMeta):
    @staticmethod
    def decode(data: bytes, **decode_params: Any) -> bytes:
        raise InvalidDecoderOrNotImplemented
