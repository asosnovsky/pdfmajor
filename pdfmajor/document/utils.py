from typing import Iterator

from pdfmajor.pdf_parser.objects import (
    ObjectRef,
    PDFArray,
    PDFObject,
    validate_object_or_none,
)

from .exceptions import BrokenFilePDF


def iter_single_ref_as_array_ref(kids: PDFObject) -> Iterator[ObjectRef]:
    """Validate that an object is either a list of refs or a single ref, then iterate over it

    Args:
        kids (PDFObject)

    Raises:
        BrokenFile: if the provided object is not a valid PDFObject

    Yields:
        Iterator[ObjectRef]
    """
    if isinstance(kids, ObjectRef):
        yield kids
    elif isinstance(kids, PDFArray):
        for kid in kids:
            vetted_kid = validate_object_or_none(kid, ObjectRef)
            if vetted_kid:
                yield vetted_kid
    else:
        raise BrokenFilePDF(f"expected a list of refs and got {kids}")
