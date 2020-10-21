import enum


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
