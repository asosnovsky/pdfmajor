import zlib
from base64 import a85decode
from binascii import a2b_hex
from typing import Any

from .ccit import ccittfaxdecode
from .lzw import lzwdecode
from .rld import rldecode
from .types import PDFFilterDecoder


class ASCIIHexDecode(PDFFilterDecoder):
    @staticmethod
    def decode(data: bytes, **decode_params: Any) -> bytes:
        clean_data = b"".join(data.split(b" "))
        if len(clean_data) & 2 != 0:
            clean_data += b"0"
        return a2b_hex(clean_data)


class ASCII85Decode(PDFFilterDecoder):
    @staticmethod
    def decode(data: bytes, **decode_params: Any) -> bytes:
        return a85decode(data, adobe=True)


class LZWDecode(PDFFilterDecoder):
    @staticmethod
    def decode(data: bytes, **decode_params: Any) -> bytes:
        return lzwdecode(data)


class FlateDecode(PDFFilterDecoder):
    @staticmethod
    def decode(data: bytes, **decode_params: Any) -> bytes:
        return zlib.decompress(data.strip(b"\r\n"))


class RunLengthDecode(PDFFilterDecoder):
    @staticmethod
    def decode(data: bytes, **decode_params: Any) -> bytes:
        return rldecode(data)


class CCITTFaxDecode(PDFFilterDecoder):
    @staticmethod
    def decode(data: bytes, **decode_params: Any) -> bytes:
        return ccittfaxdecode(data, **decode_params)
