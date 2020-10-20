from typing import Any
import zlib
from base64 import a85decode
from binascii import a2b_hex

from .types import FilterType
from .lzw import lzwdecode
from .rld import rldecode
from .ccit import ccittfaxdecode
from ..exceptions import InvalidDecoderOrNotImplemented


def decode_bytes(filter_type: FilterType, data: bytes, **kwrgs: Any) -> bytes:
    if filter_type == FilterType.ASCII85Decode:
        return a85decode(data, adobe=True)
    elif filter_type == FilterType.ASCIIHexDecode:
        clean_data = b"".join(data.split(b" "))
        if len(clean_data) & 2 != 0:
            clean_data += b"0"
        return a2b_hex(clean_data)
    elif filter_type == FilterType.LZWDecode:
        return lzwdecode(data)
    elif filter_type == FilterType.FlateDecode:
        return zlib.decompress(data)
    elif filter_type == FilterType.RunLengthDecode:
        return rldecode(data)
    elif filter_type == FilterType.CCITTFaxDecode:
        return ccittfaxdecode(data, **kwrgs)
    else:
        raise InvalidDecoderOrNotImplemented(filter_type)
    # TODO:
    # elif filter_type == FilterType.JBIG2Decode:
    #     pass
    # elif filter_type == FilterType.DCTDecode:
    #     pass
    # elif filter_type == FilterType.JPXDecode:
    #     pass
    # elif filter_type == FilterType.Crypt:
    #     pass
