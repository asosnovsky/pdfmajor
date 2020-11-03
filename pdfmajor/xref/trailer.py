from typing import List, NamedTuple, Optional, Set

from pdfmajor.lexer import iter_tokens
from pdfmajor.lexer.token import TokenKeyword
from pdfmajor.pdf_parser import get_first_object
from pdfmajor.pdf_parser.objects import (
    ObjectRef,
    PDFArray,
    PDFDictionary,
    PDFInteger,
    PDFObject,
    validate_object_or_none,
)
from pdfmajor.streambuffer import BufferStream

from .exceptions import BrokenFile, InvalidNumberOfRoots, NotRootElement


def get_root_obj(trailers: List["PDFFileTrailer"]) -> ObjectRef:
    """attempts to find the root element of the pdf

    Args:
        trailers (List[)

    Raises:
        InvalidNumberOfRoots
        NotRootElement

    Returns:
        ObjectRef
    """
    root_elements: Set[ObjectRef] = set()
    for trailer in trailers:
        if trailer.root is not None:
            root_elements.add(trailer.root)
    if len(root_elements) == 1:
        return root_elements.pop()
    elif len(root_elements) > 1:
        raise InvalidNumberOfRoots(root_elements)
    else:
        raise NotRootElement


class PDFFileTrailer(NamedTuple):
    """an object representing a PDF file trailer as is specified in PDF spec 1.7 section 7.5.5"""

    size: PDFInteger
    root: Optional[ObjectRef]
    prev: Optional[PDFInteger]
    info: Optional[ObjectRef]
    encrypt: Optional[PDFObject]
    encrypt_id: Optional[PDFArray]

    @classmethod
    def from_pdfdict(cls, pdfdict: PDFDictionary) -> "PDFFileTrailer":
        try:
            size = pdfdict["Size"]
        except KeyError as e:
            raise BrokenFile(f"Failed to get required fields from trailer {e}")

        if not isinstance(size, PDFInteger):
            raise BrokenFile(f"Size of trailer should be an integer instead got {size}")

        root = pdfdict.get("Root", None)
        if root is not None and not isinstance(root, ObjectRef):
            raise BrokenFile(f"Root element is not specified as an indirect obj {root}")

        encrypt = pdfdict.get("Encrypt", None)
        encrypt_id = pdfdict.get("ID", None)
        if encrypt is not None:
            if not isinstance(encrypt_id, PDFArray):
                raise BrokenFile(
                    f"PDF is encrypted without a valid encrypt id encrypt_id={encrypt_id}"
                )
        return cls(
            size=size,
            root=root,
            prev=validate_object_or_none(pdfdict.get("Prev", None), PDFInteger),
            info=validate_object_or_none(pdfdict.get("Info", None), ObjectRef),
            encrypt=encrypt,
            encrypt_id=encrypt_id,  # type: ignore
        )

    @classmethod
    def from_buffer(cls, buffer: BufferStream) -> "PDFFileTrailer":
        """attempts to get a trailer from the buffer stream

        Raises:
            BrokenFile: if the word 'trailer' is missing as the first token
            BrokenFile: if the next object after the word 'trailer' is not a dictionary

        """
        next_token = next(iter_tokens(buffer))
        if not (
            isinstance(next_token, TokenKeyword) and next_token.value == b"trailer"
        ):
            raise BrokenFile(f"Expected trailer but got {next_token}")
        next_obj = get_first_object(buffer, buffer.tell())
        if not isinstance(next_obj, PDFDictionary):
            raise BrokenFile(f"Expected trailer to be a dictionary but got {next_obj}")
        return cls.from_pdfdict(next_obj)
