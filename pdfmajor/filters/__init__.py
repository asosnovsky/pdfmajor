from typing import Any, Dict, Iterator, List, Optional, Type

from .decoders import (
    ASCII85Decode,
    ASCIIHexDecode,
    CCITTFaxDecode,
    FlateDecode,
    LZWDecode,
    RunLengthDecode
)
from .types import FilterPair, PDFFilterDecoder

_filter_type_name_mapping: Dict[str, Optional[Type[PDFFilterDecoder]]] = {
    "FlateDecode": FlateDecode,
    "Fl": FlateDecode,
    "LZWDecode": LZWDecode,
    "LZW": LZWDecode,
    "ASCII85Decode": ASCII85Decode,
    "A85": ASCII85Decode,
    "ASCIIHexDecode": ASCIIHexDecode,
    "AHx": ASCIIHexDecode,
    "RunLengthDecode": RunLengthDecode,
    "RL": RunLengthDecode,
    "CCITTFaxDecode": CCITTFaxDecode,
    "CCF": CCITTFaxDecode,
    "DCTDecode": None,  # FilterType.DCTDecode,
    "DCT": None,  # FilterType.DCTDecode,
    "Crypt": None,  # FilterType.Crypt,
    "JBIG2Decode": None,  # FilterType.JBIG2Decode,
    "JPXDecode": None,  # FilterType.JPXDecode,
}


def process_filters_on_data(
    data: bytes,
    it_filters: Iterator[FilterPair],
) -> bytes:
    """runs the filters provided by the list with the provided params against the data

    Args:
        data (bytes)
        filters (Optional[List[str]])
        decode_params (Optional[List[Dict[str, Any]]])

    Returns:
        bytes
    """
    for f, params in it_filters:
        decoder = detect_decoder_type(f)
        data = decoder.decode(data, **params)
    return data


def detect_decoder_type(name: str) -> Type[PDFFilterDecoder]:
    """Check to see if the specified filter exists in our codebase

    Args:
        name (str)

    Raises:
        InvalidDecoderOrNotImplemented

    Returns:
        Type[PDFFilterDecoder]
    """
    decoder = _filter_type_name_mapping.get(name)
    if not decoder:
        raise NotImplementedError(
            f"Filter {name} is not implemented yet, feel free to submit a PR and help!"
        )
    return decoder
