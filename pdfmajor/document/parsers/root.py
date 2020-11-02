from typing import Any, Optional, Set

from pdfmajor.document.pages import PDFPageTreeNode
from pdfmajor.parser.objects.base import PDFObject
from pdfmajor.parser.objects.collections import PDFDictionary
from pdfmajor.parser.objects.indirect import IndirectObject, ObjectRef
from pdfmajor.parser.objects.primitives import PDFName
from pdfmajor.xref.exceptions import InvalidNumberOfRoots, NotRootElement
from pdfmajor.xref.trailer import get_root_obj

from ..catalog import PDFDocumentCatalog
from ..exceptions import InvalidCatalogObj, MissingCatalogObj, TooManyInfoObj
from ..parse_context import PDFParsingContext


def get_info(pctx: PDFParsingContext) -> Optional[PDFObject]:
    """get a Parsed version of the PDF Info object if it exists (see PDF spec 1.7 section 14.3.3 for more detail)"""
    info_obj = _find_indirect_obj_for_info(pctx)
    if info_obj is None:
        return None
    else:
        return info_obj.get_object()


def get_catalog(pctx: PDFParsingContext) -> PDFDocumentCatalog:
    """Gets the catalog for a document

    Raises:
        InvalidCatalogObj: if something is not correctly set in the catalog

    Returns:
        PDFDocumentCatalog
    """
    cat_obj = _find_indirect_obj_for_root(pctx).get_object()
    if not isinstance(cat_obj, PDFDictionary):
        raise InvalidCatalogObj("not a dictionary")
    validated_fields: Any = pctx.convert_pdfdict_to_validated_pythondict(
        cat_obj,
        {
            "Version": ("version", PDFName),
            "PageLabels": ("page_labels", PDFDictionary),
            "PageLayout": ("page_layout", PDFName),
            "PageMode": ("page_mode", PDFName),
        },
    )
    try:
        pages_obj = cat_obj["Pages"]
    except KeyError:
        raise InvalidCatalogObj(f"Missing Pages entry {cat_obj}")
    metadata = pctx.convert_pdfdict_to_validated_pythondict
    if isinstance(pages_obj, ObjectRef):
        pages = pctx.get_object_from_ref(pages_obj).get_object()
        if not isinstance(pages, PDFDictionary):
            raise InvalidCatalogObj(f"Invalid pages ref entry {pages} from {pages_obj}")
    elif isinstance(pages_obj, PDFDictionary):
        pages = pages_obj
    else:
        raise InvalidCatalogObj(f"Invalid pages entry {pages_obj}")

    validated_fields["pages"] = PDFPageTreeNode.from_pdfdict(pages)
    validated_fields["raw"] = cat_obj
    return PDFDocumentCatalog(**validated_fields)


def _find_indirect_obj_for_root(pctx: PDFParsingContext) -> IndirectObject:
    try:
        obj_ref = get_root_obj(pctx.xrefdb.trailers)
        root_element = pctx.get_obj(obj_num=obj_ref.obj_num, gen_num=obj_ref.gen_num)
    except InvalidNumberOfRoots as e:
        pctx.health_report.write_error(e)
        obj_ref = next(iter(e.roots))
        root_element = pctx.get_obj(obj_num=obj_ref.obj_num, gen_num=obj_ref.gen_num)
    except NotRootElement as e:
        pctx.health_report.write_error(e)
        try:
            root_element = next(pctx.get_obj_by_type("/Catalog"))
        except StopIteration:
            raise MissingCatalogObj()
    return root_element


def _find_indirect_obj_for_info(pctx: PDFParsingContext) -> Optional[IndirectObject]:
    elements: Set[ObjectRef] = set()
    for trailer in pctx.xrefdb.trailers:
        if trailer.info is not None:
            elements.add(trailer.info)
    if len(elements) > 1:
        pctx.health_report.write_error(TooManyInfoObj(elements))
    elif len(elements) == 0:
        return None
    ref = next(iter(elements))
    return pctx.get_obj(ref.obj_num, ref.gen_num)
