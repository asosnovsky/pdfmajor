from pdfmajor.document.metadata import PDFMetadata
from pdfmajor.parser.objects import PDFName, PDFObject

from ..exceptions import BrokenFilePDF
from ..parse_context import PDFParsingContext


def get_metadata(pctx: PDFParsingContext, ref: PDFObject):
    obj_def, data = pctx.validated_and_iter_stream(ref)
    if not isinstance(obj_def["Subtype"], PDFName):
        pctx.health_report.write_error(
            BrokenFilePDF(
                f"Metadata data object is missing a valid subtype {ref} {obj_def}"
            )
        )
        return PDFMetadata("", data)
    return PDFMetadata(obj_def["Subtype"].value, data)
