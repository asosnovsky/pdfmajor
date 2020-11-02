from decimal import Decimal
from typing import Any, Dict, Iterator, List, Optional

from pdfmajor.document.exceptions import BrokenFilePDF
from pdfmajor.parser.objects.base import PDFObject
from pdfmajor.parser.objects.collections import PDFArray, PDFDictionary
from pdfmajor.parser.objects.indirect import IndirectObject, ObjectRef
from pdfmajor.parser.objects.primitives import PDFInteger, PDFReal
from pdfmajor.parser.stream.PDFStream import PDFStream
from pdfmajor.util import validate_object_or_none

from ..pages import PDFPage, PDFPageTreeNode
from ..parse_context import PDFParsingContext
from ..utils import iter_single_ref_as_array_ref

PDFRawFields = Dict[str, Any]


def iter_all_page_leafs(
    pctx: PDFParsingContext, root_node: PDFPageTreeNode
) -> Iterator[PDFPage]:
    """Iterate over every page in the pdf

    Args:
        pctx (PDFParsingContext)
        root_node (PDFPageTreeNode)

    Yields:
        Iterator[PDFPage]
    """
    current_root: List[PDFPageTreeNode] = [root_node]
    current_root_aspage: List[Dict[str, Optional[PDFObject]]] = [
        parse_pdfpage_fields(pctx, root_node.raw, allow_missing=True)
    ]
    current_child_idx: List[int] = [0]
    while len(current_root) > 0:
        croot = current_root[-1]
        croot_pagedata = current_root_aspage[-1]
        ckids = croot.kids
        cidx = current_child_idx[-1]
        if len(ckids) < cidx + 1:
            try:
                current_root.pop()
                current_root_aspage.pop()
                current_child_idx.pop()
                continue
            except IndexError:
                break
        page_ref = ckids[cidx]
        obj = pctx.get_object_from_ref(page_ref).get_object()
        if isinstance(obj, PDFDictionary):
            if obj["Type"].to_python() == "/Pages":
                current_root.append(PDFPageTreeNode.from_pdfdict(obj))
                current_root_aspage.append(
                    {
                        **croot_pagedata,
                        **parse_pdfpage_fields(pctx, obj, allow_missing=True),
                    }
                )
                current_child_idx[-1] += 1
                current_child_idx.append(0)
                continue
            elif obj["Type"].to_python() == "/Page":
                yield make_pdfpage(croot_pagedata, pctx, obj)
                current_child_idx[-1] += 1
                continue
        # catch all other cases (the above expression will issue a 'continue')
        pctx.health_report.write(
            "InvalidPageobject",
            f"Expecting page ref {page_ref} to be a dictionary with type 'Pages' or 'Page', but got a {obj}",
        )
        current_child_idx[-1] += 1


def make_pdfpage(
    lastpage: Optional[Dict[str, Optional[PDFObject]]],
    pctx: PDFParsingContext,
    pdfdict: PDFDictionary,
) -> PDFPage:
    """Creates a PDFPage object, and handle the inheritance of properties

    Args:
        lastpage (Optional[Dict[str, Optional[PDFObject]]]): the last inheritable properties for the pdf
        pctx (PDFParsingContext)
        pdfdict (PDFDictionary)

    Returns:
        PDFPage
    """
    vetted_fields: Any = parse_pdfpage_fields(
        pctx, pdfdict, lastpage=lastpage, allow_missing=False
    )
    parent = validate_object_or_none(pdfdict.get("Parent"), ObjectRef)
    content_streams: List[PDFStream] = []
    if pdfdict.get("Contents", None) is not None:
        content_streams = list(_parse_page_contents(pdfdict["Contents"], pctx))
    else:
        pctx.health_report.write(
            "MissingPDFPageContents",
            f"Page with data {pdfdict} is missing the 'Contents' property."
            "Will assume that the page has no content.",
        )
    vetted_fields["parent"] = parent
    vetted_fields["contents"] = content_streams
    vetted_fields["raw"] = pdfdict
    vetted_fields["metadata"] = _parse_metadata(pdfdict.get("Metadata", None), pctx)
    return PDFPage(**vetted_fields)


def parse_pdfpage_fields(
    pctx: PDFParsingContext,
    pdfdict: PDFDictionary,
    allow_missing: bool = False,
    lastpage: Optional[PDFRawFields] = None,
) -> PDFRawFields:
    parsed_values = pctx.convert_pdfdict_to_validated_pythondict(
        pdfdict,
        {
            "Resources": ("resources", PDFDictionary),
            "BoxColorInfo": ("boxcolor_info", PDFDictionary),
            "Rotate": ("rotate", PDFInteger),
        },
    )
    mediaboxes = pctx.extract_and_validate_pdf_rectangles(
        pdfdict,
        {
            "MediaBox": "mediabox",
            "CropBox": "cropbox",
            "BleedBox": "bleedbox",
            "TrimBox": "trimbox",
            "ArtBox": "artbox",
        },
    )
    return _deal_with_inheritance(
        {
            **parsed_values,  # type: ignore
            **mediaboxes,  # type: ignore
            "user_unit": pctx.get_validate_numeric(pdfdict.get("UserUnit")),  # type: ignore
        },
        lastpage,
        allow_missing,
    )


def _parse_metadata(
    metadata_raw: Optional[PDFObject], pctx: PDFParsingContext
) -> Optional[PDFStream]:
    if metadata_raw is None:
        return None
    if isinstance(metadata_raw, ObjectRef):
        metadata_obj = pctx.get_object_from_ref(metadata_raw)
    elif isinstance(metadata_raw, IndirectObject):
        metadata_obj = metadata_raw
    else:
        raise BrokenFilePDF(f"Metadata object is not a valid type {metadata_raw}")
    if metadata_obj.stream is None:
        raise BrokenFilePDF(f"Metadata object is missing it's stream {metadata_obj}")
    else:
        return metadata_obj.stream


def _parse_page_contents(contents_raw: PDFObject, pctx: PDFParsingContext):
    for content_ref in iter_single_ref_as_array_ref(contents_raw):
        content_obj = pctx.get_object_from_ref(content_ref)
        if isinstance(content_obj, PDFArray):
            for subref in iter_single_ref_as_array_ref(content_obj):
                sub_obj = pctx.get_object_from_ref(subref)
                if isinstance(sub_obj, IndirectObject):
                    if sub_obj.stream is not None:
                        yield sub_obj.stream
                        continue
                raise BrokenFilePDF(f"Invalid PDFStream found for page {sub_obj}")
            continue
        elif isinstance(content_obj, IndirectObject):
            if content_obj.stream is not None:
                yield content_obj.stream
                continue
        raise BrokenFilePDF(f"Invalid PDFStream found for page {content_obj}")


def _deal_with_inheritance(
    field_dict: Dict[str, Optional[PDFObject]],
    lastpage: Optional[PDFRawFields],
    allow_missing: bool = False,
):
    _deal_with_inheritance_for_field("resources", field_dict, lastpage, PDFDictionary())
    _deal_with_inheritance_for_field(
        "rotate", field_dict, lastpage, PDFInteger(0, 0, 0)
    )
    _deal_with_inheritance_for_field(
        "user_unit", field_dict, lastpage, PDFReal(Decimal("1.0"), 0, 0)
    )
    _deal_with_inheritance_for_field(
        "mediabox", field_dict, lastpage, allow_missing=allow_missing
    )
    _deal_with_inheritance_for_field(
        "cropbox",
        field_dict,
        lastpage,
        default_value=field_dict["mediabox"],
        allow_missing=allow_missing,
    )
    _deal_with_inheritance_for_field(
        "bleedbox",
        field_dict,
        lastpage,
        default_value=field_dict["cropbox"],
        allow_missing=allow_missing,
    )
    _deal_with_inheritance_for_field(
        "trimbox",
        field_dict,
        lastpage,
        default_value=field_dict["cropbox"],
        allow_missing=allow_missing,
    )
    _deal_with_inheritance_for_field(
        "artbox",
        field_dict,
        lastpage,
        default_value=field_dict["cropbox"],
        allow_missing=allow_missing,
    )
    return field_dict


def _deal_with_inheritance_for_field(
    field_name: str,
    field_dict: Dict[str, Optional[PDFObject]],
    lastpage: Optional[PDFRawFields],
    default_value: Optional[PDFObject] = None,
    allow_missing: bool = False,
):
    if not field_dict[field_name]:
        if not lastpage:
            if default_value is not None:
                field_dict[field_name] = default_value
            elif not allow_missing:
                raise BrokenFilePDF(f"Page is missing {field_name}")
        elif lastpage.get(field_name, None):
            field_dict[field_name] = lastpage[field_name]
        elif default_value is not None:
            field_dict[field_name] = default_value
        elif not allow_missing:
            raise BrokenFilePDF(f"Page is missing {field_name}")
