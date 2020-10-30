from pathlib import Path
from typing import Any, BinaryIO, Dict, Optional, Set, Tuple, Type, TypeVar

from pdfmajor.healthlog import PDFHealthReport
from pdfmajor.parser.objects.base import PDFObject
from pdfmajor.parser.objects.collections import PDFArray, PDFDictionary
from pdfmajor.parser.objects.indirect import IndirectObject, ObjectRef
from pdfmajor.parser.objects.primitives import PDFName
from pdfmajor.streambuffer import BufferStream
from pdfmajor.util import validate_object_or_none
from pdfmajor.xref.exceptions import InvalidNumberOfRoots, NotRootElement
from pdfmajor.xref.trailer import get_root_obj
from pdfmajor.xref.xrefdb import XRefDB

from .exceptions import InvalidCatalogObj, MissingCatalogObj, TooManyInfoObj
from .PDFDocumentCatalog import PDFDocumentCatalog


class PDFParsingContext:
    """A utility class to encapsulate various interactions with the raw document stream"""

    @classmethod
    def from_io(cls, fp: BinaryIO, buffer_size=4096):
        return cls(BufferStream(fp, buffer_size))

    @classmethod
    def from_path(cls, path: Path, buffer_size=4096):
        return cls(BufferStream(path.open("rb"), buffer_size))

    def __init__(self, buffer: BufferStream) -> None:
        self.buffer = buffer
        self.health_report = PDFHealthReport()
        with buffer.get_window():
            self.xrefdb = XRefDB(buffer)

    def get_object_from_ref(self, objref: ObjectRef) -> IndirectObject:
        with self.buffer.get_window():
            return self.xrefdb.get_obj(
                objref.obj_num, objref.gen_num, buffer=self.buffer
            )

    ExpectedType = TypeVar("ExpectedType", bound=PDFObject)

    def get_validate_object(
        self, obj: Optional[PDFObject], exptype: Type[ExpectedType]
    ) -> Optional[ExpectedType]:
        """Validates the object's type if its not None

        Args:
            obj (Optional[PDFObject])
            objtype (Type[ExpectedType]): expected type of the object

        Raises:
            AssertionError: is raised if the object has an invalid type

        Returns:
            Optional[ExpectedType]
        """
        if isinstance(obj, ObjectRef):
            return validate_object_or_none(
                self.get_object_from_ref(obj).get_object(), exptype
            )
        return validate_object_or_none(obj, exptype)

    def convert_pdfdict_to_validated_pythondict(
        self,
        pdfdict: PDFDictionary,
        field_mapping: Dict[str, Tuple[str, Type[PDFObject]]],
    ) -> Dict[str, Optional[PDFObject]]:
        """Takes a pdf-dictionary and converts it to a regular dictionary (but first validates the types of the objects)

        Args:
            pdfdict (PDFDictionary)
            field_mapping (Dict[str, Tuple[Type[PDFObject]]])

        Returns:
            dict
        """
        out: Dict[str, Optional[PDFObject]] = {}
        for pdf_name, (new_name, exp_type) in field_mapping.items():
            try:
                out[new_name] = self.get_validate_object(
                    pdfdict.get(pdf_name), exp_type
                )
            except AssertionError as err:
                self.health_report.write_error(err)
        return out

    def get_info(self) -> Optional[PDFObject]:
        """get a Parsed version of the PDF Info object if it exists (see PDF spec 1.7 section 14.3.3 for more detail)"""
        with self.buffer.get_window():
            info_obj = _find_indirect_obj_for_info(
                self.xrefdb, self.buffer, self.health_report
            )
            if info_obj is None:
                return None
            else:
                return info_obj.get_object()

    def get_catalog(self) -> PDFDocumentCatalog:
        """Gets the catalog for a document

        Raises:
            InvalidCatalogObj: if something is not correctly set in the catalog

        Returns:
            PDFDocumentCatalog
        """
        with self.buffer.get_window():
            cat_obj = _find_indirect_obj_for_root(
                self.xrefdb, self.buffer, self.health_report
            ).get_object()
        if not isinstance(cat_obj, PDFDictionary):
            raise InvalidCatalogObj("not a dictionary")
        validated_fields: Any = self.convert_pdfdict_to_validated_pythondict(
            cat_obj,
            {
                "Version": ("version", PDFName),
                "PageLabels": ("page_labels", PDFDictionary),
                "PageLayout": ("page_layout", PDFName),
                "PageMode": ("page_mode", PDFName),
                "Metadata": ("metadata", PDFDictionary),
            },
        )
        try:
            pages_obj = cat_obj["Pages"]
        except KeyError:
            raise InvalidCatalogObj(f"Missing Pages entry {cat_obj}")
        pages = []
        if isinstance(pages_obj, ObjectRef):
            pages = [pages_obj]
        elif not isinstance(pages_obj, PDFArray):
            raise InvalidCatalogObj(f"Invalid pages entry {pages_obj}")
        else:
            for page in pages_obj:
                if isinstance(page, ObjectRef):
                    pages.append(page)
                else:
                    self.health_report.write(
                        "InvalidPageRef", f"The page {page} has an invalid value"
                    )
        validated_fields["pages"] = pages
        validated_fields["raw"] = cat_obj
        return PDFDocumentCatalog(**validated_fields)


def _find_indirect_obj_for_root(
    xrefdb: XRefDB, buffer: BufferStream, health_report: PDFHealthReport
) -> IndirectObject:
    try:
        obj_ref = get_root_obj(xrefdb.trailers)
        with buffer.get_window():
            root_element = xrefdb.get_obj(
                obj_num=obj_ref.obj_num, gen_num=obj_ref.gen_num, buffer=buffer
            )
    except InvalidNumberOfRoots as e:
        health_report.write_error(e)
        obj_ref = next(iter(e.roots))
        with buffer.get_window():
            root_element = xrefdb.get_obj(
                obj_num=obj_ref.obj_num, gen_num=obj_ref.gen_num, buffer=buffer
            )
    except NotRootElement as e:
        health_report.write_error(e)
        try:
            root_element = next(xrefdb.get_obj_by_type(buffer, "/Catalog"))
        except StopIteration:
            raise MissingCatalogObj()
    return root_element


def _find_indirect_obj_for_info(
    xrefdb: XRefDB, buffer: BufferStream, health_report: PDFHealthReport
) -> Optional[IndirectObject]:
    elements: Set[ObjectRef] = set()
    for trailer in xrefdb.trailers:
        if trailer.info is not None:
            elements.add(trailer.info)
    if len(elements) > 1:
        health_report.write_error(TooManyInfoObj(elements))
    elif len(elements) == 0:
        return None
    ref = next(iter(elements))
    return xrefdb.get_obj(ref.obj_num, ref.gen_num, buffer)
