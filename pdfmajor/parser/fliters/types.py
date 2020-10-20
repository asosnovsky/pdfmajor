import enum
from typing import Dict
from ..exceptions import InvalidDecoderOrNotImplemented


class FilterType(enum.Enum):
    """Standard PDF Filter types see PDF spec 1.7 section 7.4 table 6"""

    ASCIIHexDecode = enum.auto()
    ASCII85Decode = enum.auto()
    LZWDecode = enum.auto()
    FlateDecode = enum.auto()
    RunLengthDecode = enum.auto()
    CCITTFaxDecode = enum.auto()
    JBIG2Decode = enum.auto()
    DCTDecode = enum.auto()
    JPXDecode = enum.auto()
    Crypt = enum.auto()


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


def detect_filter_type(name: str) -> FilterType:
    ftype = _filter_type_name_mapping.get(name, None)
    if ftype is None:
        raise InvalidDecoderOrNotImplemented(name)
    return ftype
