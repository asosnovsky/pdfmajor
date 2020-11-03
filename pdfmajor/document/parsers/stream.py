from itertools import chain
from typing import Any, Dict, List

from pdfmajor.filters import process_filters_on_data
from pdfmajor.parser.exceptions import IncompleteStream
from pdfmajor.parser.objects import PDFDictionary, PDFName, PDFStream
from pdfmajor.streambuffer import BufferStream


def decode_stream(stream: PDFStream, buffer: BufferStream) -> bytes:
    """Decode the bytes associated with the PDF-Stream

    Args:
        stream (PDFStream)
        buffer (BufferStream)

    Returns:
        bytes
    """
    length = stream.length.to_python()
    if length is None:
        raise IncompleteStream(f"Cannot decode stream as it has no specified length")
    with buffer.get_window():
        buffer.seek(stream.offset)
        data = buffer.read(length).data
    filters: List[str] = []
    decode_parms: List[Dict[str, Any]] = []
    for f, dp in chain(
        zip(stream.filter, stream.decode_parms),
        zip(stream.ffilter, stream.fdecode_parms),
    ):
        if not isinstance(f, PDFName):
            raise IncompleteStream(f"Invalid filter name {f}")
        else:
            filter_name = f.value
        params = {}
        if isinstance(dp, PDFDictionary):
            params = dp.to_python()
        filters.append(filter_name)
        decode_parms.append(params)
    data = process_filters_on_data(data, filters, decode_parms)
    return data
