from pdfmajor.parser.objects.collections import PDFDictionary
from pdfmajor.streambuffer import BufferStream
from typing import Dict, Iterator, List, Optional, Tuple

from pdfmajor.parser.objects.indirect import IndirectObject
from pdfmajor.parser import get_first_object
from .xref import XRefRow, iter_over_xref
from .exceptions import InvalidIndirectObjAccess, InvalidXref, XRefError

# simple type aliases for better readability
ObjNum = int
GenNum = int
RawRef = Tuple[ObjNum, GenNum]
ObjType = str


class XRefDB:
    """A class for collection references to objects"""

    def __init__(self, buffer: BufferStream) -> None:
        self.objs: Dict[RawRef, IndirectObject] = {}
        self.types: Dict[RawRef, ObjType] = {}
        self.xrefs: Dict[RawRef, XRefRow] = {}

        with buffer.get_window():
            for xref in iter_over_xref(buffer):
                if xref.use == b"n":
                    self.xrefs[(xref.obj_num, xref.gen_num)] = xref

    def get_obj_by_type(
        self, buffer: BufferStream, obj_type: ObjType
    ) -> Iterator[IndirectObject]:
        """Iterates over the objects in memeory and filters out for the ones that match the requested type
        If the object is not loaded into memory this function will load it.

        Args:
            buffer (BufferStream)
            obj_type (ObjType)

        Raises:
            InvalidXref: if the object could not be found in memory or the buffer
            XRefError: if the object type if found but the object was never loaded into memory

        Yields:
            Iterator[IndirectObject]
        """
        for raw_ref in self.xrefs.keys():
            ftype = self.get_type_for(*raw_ref, buffer=buffer)
            if ftype == obj_type:
                yield self.objs[raw_ref]

    def get_type_for(
        self, obj_num: ObjNum, gen_num: GenNum, buffer: BufferStream
    ) -> str:
        raw_ref, xref = (obj_num, gen_num), self.xrefs[(obj_num, gen_num)]
        found_obj_type: Optional[str] = self.types.get(raw_ref, None)
        if found_obj_type is None:
            obj = self.objs.get(raw_ref, None)
            if obj is None:
                obj = get_first_object(buffer, xref.offset)
                if not isinstance(obj, IndirectObject):
                    raise InvalidXref(
                        f"Offset for {xref} returned an invalid object {obj}"
                    )
            obj_dict = obj.get_object()
            if isinstance(obj_dict, PDFDictionary):
                type_name = obj_dict.get("Type", None)
                if type_name is not None:
                    found_obj_type = type_name.to_python()
                else:
                    found_obj_type = "{{PDFUnknownComplexType}}"
            else:
                found_obj_type = "{{PDFPrimitive}}"
        else:
            obj = self.objs.get(raw_ref, None)
            if obj is None:
                raise XRefError(f"Missing valid obj for {xref}")
        if found_obj_type is None:
            raise XRefError("WARN: Failed to find a valid type for", xref)
        return found_obj_type

    def has_xref(self, obj_num: ObjNum, gen_num: GenNum) -> bool:
        return (obj_num, gen_num) in self.xrefs.keys()

    def has_obj(self, obj_num: ObjNum, gen_num: GenNum) -> bool:
        return (obj_num, gen_num) in self.objs.keys()
