import zlib

from typing import Any, Dict, List, Optional
from base64 import a85decode
from binascii import a2b_hex
from ..exceptions import InvalidDecoderOrNotImplemented

from .types import FilterType
from .lzw import lzwdecode
from .rld import rldecode
from .ccit import ccittfaxdecode
from ..exceptions import InvalidDecoderOrNotImplemented


_filter_type_name_mapping: Dict[str, FilterType] = {
    "FlateDecode": FilterType.FlateDecode,
    "Fl": FilterType.FlateDecode,
    "LZWDecode": FilterType.LZWDecode,
    "LZW": FilterType.LZWDecode,
    "ASCII85Decode": FilterType.ASCII85Decode,
    "A85": FilterType.ASCII85Decode,
    "ASCIIHexDecode": FilterType.ASCIIHexDecode,
    "AHx": FilterType.ASCIIHexDecode,
    "RunLengthDecode": FilterType.RunLengthDecode,
    "RL": FilterType.RunLengthDecode,
    "CCITTFaxDecode": FilterType.CCITTFaxDecode,
    "CCF": FilterType.CCITTFaxDecode,
    "DCTDecode": FilterType.DCTDecode,
    "DCT": FilterType.DCTDecode,
    "Crypt": FilterType.Crypt,
    "JBIG2Decode": FilterType.JBIG2Decode,
    "JPXDecode": FilterType.JPXDecode,
}


def process_filters_on_data(
    data: bytes,
    filters: Optional[List[str]],
    decode_params: Optional[List[Dict[str, Any]]],
) -> bytes:
    """runs the filters provided by the list with the provided params against the data

    Args:
        data (bytes)
        filters (Optional[List[str]])
        decode_params (Optional[List[Dict[str, Any]]])

    Returns:
        bytes
    """
    if filters is not None:
        decode_parms = []
        if decode_params is not None:
            decode_parms = decode_params
        for f in filters:
            params = {}
            if len(decode_parms) > 0:
                params = decode_parms.pop()
            filter_type = detect_filter_type(f)
            data = decode_bytes(filter_type, data, **params)
    return data


def detect_filter_type(name: str) -> FilterType:
    """Check to see if the specified filter exists in our codebase

    Args:
        name (str)

    Raises:
        InvalidDecoderOrNotImplemented

    Returns:
        FilterType
    """
    ftype = _filter_type_name_mapping.get(name, None)
    if ftype is None:
        raise InvalidDecoderOrNotImplemented(name)
    return ftype


def decode_bytes(filter_type: FilterType, data: bytes, **kwrgs: Any) -> bytes:
    """Run the decoding function on the filter

    Args:
        filter_type (FilterType)
        data (bytes)

    Raises:
        InvalidDecoderOrNotImplemented

    Returns:
        bytes
    """
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
