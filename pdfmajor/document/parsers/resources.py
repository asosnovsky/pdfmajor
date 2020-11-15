from pdfmajor.document.exceptions import BrokenFilePDF
from pdfmajor.pdf_parser.objects.ref import ObjectRef
from pdfmajor.fonts import PDFFont, PDFFontType1
from typing import Dict, Iterator, Tuple
from pdfmajor.pdf_parser import PDFDictionary
from ..page_parser.resources import PDFResources
from ..parse_context import PDFParsingContext


def get_resources(
    pctx: PDFParsingContext, resource_pdfdict: PDFDictionary
) -> PDFResources:
    fonts_obj = resource_pdfdict.get("Font", PDFDictionary())
    if not isinstance(fonts_obj, PDFDictionary):
        raise BrokenFilePDF(f"Invalid font obj {fonts_obj}")
    fonts: Dict[str, PDFFont] = dict(_parse_out_fonts(pctx, fonts_obj))

    return PDFResources(font=fonts, raw=resource_pdfdict)


def _parse_out_fonts(
    pctx: PDFParsingContext, font_pdfdict: PDFDictionary
) -> Iterator[Tuple[str, PDFFont]]:
    for font_alias, font_ref in font_pdfdict.items():
        if isinstance(font_ref, ObjectRef):
            font_obj = pctx.get_object_from_ref(font_ref).get_object()
            if not isinstance(font_obj, PDFDictionary):
                raise BrokenFilePDF(f"Invalid font {font_obj}")
        elif isinstance(font_ref, PDFDictionary):
            font_obj = font_ref
        else:
            raise BrokenFilePDF(f"Invalid font {font_ref}")
        subtype = font_obj["Subtype"]
        if subtype.to_python() in ["/Type1", "/MMType1"]:
            yield font_alias, PDFFontType1.from_dict(font_obj)
