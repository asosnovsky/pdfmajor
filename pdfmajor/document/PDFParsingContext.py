from pathlib import Path
from typing import BinaryIO, Dict, Iterator, Optional, Tuple, Type, TypeVar

from pdfmajor.healthlog import PDFHealthReport
from pdfmajor.parser.objects.base import PDFObject
from pdfmajor.parser.objects.collections import PDFDictionary
from pdfmajor.parser.objects.indirect import IndirectObject, ObjectRef
from pdfmajor.streambuffer import BufferStream
from pdfmajor.util import validate_object_or_none
from pdfmajor.xref.xrefdb import GenNum, ObjNum, XRefDB


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
        """Get an indirect object from it's object reference

        Args:
            objref (ObjectRef)

        Returns:
            IndirectObject
        """
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

    def get_obj_by_type(self, obj_type: str) -> Iterator[IndirectObject]:
        """Iterates over the objects in memeory and filters out for the ones that match the requested type
        If the object is not loaded into memory this function will load it.

        Args:
            obj_type (ObjType)

        Raises:
            InvalidXref: if the object could not be found in memory or the buffer
            XRefError: if the object type if found but the object was never loaded into memory

        Yields:
            Iterator[IndirectObject]
        """
        with self.buffer.get_window() as buffer:
            return self.xrefdb.get_obj_by_type(buffer, obj_type)

    def get_obj(
        self,
        obj_num: ObjNum,
        gen_num: GenNum,
    ) -> IndirectObject:
        """Get's an indirect object from either the pdf stream or a cached version in memeory

        Args:
            obj_num (ObjNum)
            gen_num (GenNum)
            buffer (BufferStream)

        Raises:
            InvalidXref: if the reference returned was not an indirect object

        Returns:
            IndirectObject
        """
        with self.buffer.get_window() as buffer:
            return self.xrefdb.get_obj(obj_num, gen_num, buffer)
