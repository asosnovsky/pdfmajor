from datetime import datetime
from typing import Any, Dict, NamedTuple, Optional, Tuple

from pdfmajor.lexer import iter_tokens
from pdfmajor.lexer.token import TokenComment
from pdfmajor.streambuffer import BufferStream


class PDFDocumentCatalog(NamedTuple):
    """A Parsed version of the PDF Catalog object (see PDF spec 1.7 section 7.7.2 for more detail)

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
    raw: Dict[str, Any]

    @classmethod
    def from_bufferstream(cls, buffer: BufferStream):
        version = _get_version(buffer)


def _get_version(buffer: BufferStream) -> Optional[str]:
    with buffer.get_window():
        token = next(iter_tokens(buffer))
        if isinstance(token, TokenComment):
            return token.value.decode()
    return None
