from typing import NamedTuple


class PDFMetadata(NamedTuple):
    """A structure representing the data in a PDF Metadata object as is specified in PDF spec 1.7 section 14.3.2"""

    sub_type: str
    stream_data: bytes
