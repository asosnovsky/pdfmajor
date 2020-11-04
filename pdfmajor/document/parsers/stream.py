from itertools import chain
from typing import Any, Dict, Iterator

from pdfmajor.filters import FilterPair, process_filters_on_data
from pdfmajor.pdf_parser.exceptions import IncompleteStream
from pdfmajor.pdf_parser.objects import PDFDictionary, PDFName, PDFStream
from pdfmajor.streambuffer import BufferStream


def iter_filters_in_stream(stream: PDFStream) -> Iterator[FilterPair]:
    """loops over all filters and their params in the stream

    Args:
        stream (PDFStream)

    Raises:
        IncompleteStream: if a filter-name is invalid

    Yields:
        Iterator[FilterPair]
    """
    for f, dp in chain(
        zip(stream.filter, stream.decode_parms),
        zip(stream.ffilter, stream.fdecode_parms),
    ):
        if not isinstance(f, PDFName):
            raise IncompleteStream(f"Invalid filter name {f}")
        else:
            filter_name = f.value
        params: Dict[str, Any] = {}
        if isinstance(dp, PDFDictionary):
            params = dp.to_python()
        yield filter_name, params


def decode_stream(
    offset: int, length: int, it_filters: Iterator[FilterPair], buffer: BufferStream
) -> bytes:
    """Decode the bytes associated with the PDF-Stream

    Args:
        offset (int)
        length (int)
        it_filters (Iterator[FilterPair])
        buffer (BufferStream)

    Returns:
        bytes
    """
    with buffer.get_window():
        buffer.seek(offset)
        data = buffer.read(length).data

    data = process_filters_on_data(data, it_filters)
    return data
