from datetime import datetime
from pdfmajor.lexer.token import TokenComment
from typing import Any, Dict, NamedTuple, Optional, Tuple

from pdfmajor.lexer import iter_tokens
from pdfmajor.streambuffer import BufferStream


class PDFDocumentParsedMetadata(NamedTuple):
    """A Parsed version of the PDF Metadata object (see PDF spec 1.7 section 14.3.3 for more detail)

    Args:
        NamedTuple ([type]): [description]
    """

    title: str
    author: str
    subject: str
    keywords: str
    creator: str
    producer: str
    creation_date: datetime
    mod_date: datetime
    trapped: str
    mediabox: Tuple[int, int, int, int]
    raw_metadata: Dict[str, Any]

    @classmethod
    def from_bufferstream(cls, buffer: BufferStream):
        version = _get_version(buffer)


def _get_version(buffer: BufferStream) -> Optional[str]:
    with buffer.get_window():
        token = next(iter_tokens(buffer))
        if isinstance(token, TokenComment):
            return token.value.decode()
    return None
