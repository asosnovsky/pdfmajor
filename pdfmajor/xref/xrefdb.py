from typing import Dict, Iterator, List, Optional, Tuple

from pdfmajor.parser import get_first_object
from pdfmajor.parser.objects.base import PDFObject
from pdfmajor.parser.objects.collections import PDFDictionary
from pdfmajor.parser.objects.indirect import IndirectObject, ObjectRef
from pdfmajor.parser.objects.primitives import PDFInteger
from pdfmajor.streambuffer import BufferStream

from .exceptions import BrokenFile, InvalidXref, XRefError
from .trailer import PDFFileTrailer
from .xref import XRefRow, find_start_of_xref, iter_over_xref

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
        self.trailers: List[PDFFileTrailer] = []

        with buffer.get_window():
            start_offset = find_start_of_xref(buffer, True)
            while True:
                for xref in iter_over_xref(buffer, start_offset, True):
                    if xref.use == b"n":
                        self.xrefs[(xref.obj_num, xref.gen_num)] = xref
                trailer = PDFFileTrailer.from_buffer(buffer)
                self.trailers.append(trailer)
                if trailer.prev is not None:
                    if isinstance(trailer.prev, PDFInteger):
                        start_offset = trailer.prev.to_python()
                    elif isinstance(trailer.prev, ObjectRef):
                        obj = self.get_obj(
                            trailer.prev.obj_num, trailer.prev.gen_num, buffer=buffer
                        )
                        if not isinstance(obj, PDFInteger):
                            raise BrokenFile(
                                f"trailer had an invalid prev options {trailer.prev}"
                            )
                        else:
                            start_offset = obj.to_python()
                    else:
                        raise BrokenFile(
                            f"trailer had an invalid prev options {trailer.prev}"
                        )
                else:
                    break

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
            obj = self.get_obj(*raw_ref, buffer=buffer)
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
            try:
                obj = self.objs[raw_ref]
            except KeyError:
                raise XRefError(f"Missing valid obj for {xref}")
        if found_obj_type is None:
            raise XRefError("WARN: Failed to find a valid type for", xref)
        return found_obj_type

    def get_obj(
        self,
        obj_num: ObjNum,
        gen_num: GenNum,
        buffer: BufferStream,
    ) -> IndirectObject:
        raw_ref, xref = (obj_num, gen_num), self.xrefs[(obj_num, gen_num)]
        obj = self.objs.get(raw_ref, None)
        if obj is None:
            with buffer.get_window():
                parsed_obj = get_first_object(buffer, xref.offset)
            if not isinstance(parsed_obj, IndirectObject):
                raise InvalidXref(
                    f"Offset for {xref} returned an invalid object {parsed_obj}"
                )
            self.objs[raw_ref] = parsed_obj
        return self.objs[raw_ref]

    def has_xref(self, obj_num: ObjNum, gen_num: GenNum) -> bool:
        return (obj_num, gen_num) in self.xrefs.keys()

    def has_obj(self, obj_num: ObjNum, gen_num: GenNum) -> bool:
        return (obj_num, gen_num) in self.objs.keys()
