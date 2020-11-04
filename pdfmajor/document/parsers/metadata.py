from pdfmajor.document.metadata import PDFMetadata
from pdfmajor.pdf_parser.objects import PDFName, PDFObject

from ..exceptions import BrokenFilePDF
from ..parse_context import PDFParsingContext


def get_metadata(pctx: PDFParsingContext, ref: PDFObject):
    obj_def, data = pctx.validated_and_iter_stream(ref)
    subtype = obj_def["Subtype"]
    if not isinstance(subtype, PDFName):
        pctx.health_report.write_error(
            BrokenFilePDF(
                f"Metadata data object is missing a valid subtype {ref} {obj_def}"
            )
        )
        return PDFMetadata("", data)
    return PDFMetadata(subtype.value, data)
