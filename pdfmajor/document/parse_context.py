from pathlib import Path
from typing import Any, BinaryIO, Dict, Iterator, Optional, Tuple, Type, TypeVar, Union

from pdfmajor.document.exceptions import BrokenFilePDF
from pdfmajor.document.parsers.stream import decode_stream
from pdfmajor.document.structures import PDFRectangle
from pdfmajor.healthlog import PDFHealthReport
from pdfmajor.pdf_parser.objects import (
    IndirectObject,
    ObjectRef,
    PDFArray,
    PDFDictionary,
    PDFInteger,
    PDFObject,
    PDFReal,
    validate_number_or_none,
    validate_object_or_none,
)
from pdfmajor.pdf_parser.objects.stream import PDFStream
from pdfmajor.streambuffer import BufferStream
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

    def get_validate_numeric(
        self, obj: Optional[PDFObject]
    ) -> Optional[Union[PDFInteger, PDFReal]]:
        """Validates the object is numeric, if its not None

        Args:
            obj (Optional[PDFObject])

        Raises:
            AssertionError: is raised if the object has an invalid type

        Returns:
            Optional[Union[PDFInteger, PDFReal]]
        """
        if isinstance(obj, ObjectRef):
            return validate_number_or_none(self.get_object_from_ref(obj).get_object())
        return validate_number_or_none(obj)

    def convert_pdfdict_to_validated_pythondict(
        self,
        pdfdict: PDFDictionary,
        field_mapping: Dict[str, Tuple[str, Type[PDFObject]]],
    ) -> Dict[str, Optional[PDFObject]]:
        """Takes a pdf-dictionary and converts it to a regular dictionary (but first validates the types of the objects)

        Args:
            pdfdict (PDFDictionary)
            field_mapping (Dict[str, Tuple[Type[PDFObject]]]): mapping of the name as it in the pdf to a tuple with a (new name, expected objcet type)

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

    def extract_and_validate_pdf_rectangles(
        self, pdfdict: PDFDictionary, field_mapping: Dict[str, str]
    ) -> Dict[str, Optional[PDFRectangle]]:
        """Takes a pdf-dictionary and extracts the specified fields. Next it will validate and convert the fields into PDFRectangles

        Args:
            pdfdict (PDFDictionary)
            field_mapping (Dict[str, str]): a mapping of names as they appear in the pdf to requested names

        Returns:
            Dict[str, Optional[PDFRectangle]]
        """
        vetted_values: Any = self.convert_pdfdict_to_validated_pythondict(
            pdfdict,
            {
                pdfname: (newname, PDFArray)
                for pdfname, newname in field_mapping.items()
            },
        )
        return {
            newname: PDFRectangle.from_pdfarray(value) if value is not None else value
            for newname, value in vetted_values.items()
        }

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

    def validated_and_iter_stream(
        self, obj_ref: PDFObject
    ) -> Tuple[PDFDictionary, bytes]:
        """Validates that an object is either an ObjectRef or IndirectObject and then checks that it has a stream.
        Once those checks are passed, this method will decode the stream and return it's contents witht the indirect objects dictionary

        Args:
            obj_ref (PDFObject)

        Raises:
            BrokenFilePDF: if a validation fails

        Returns:
            Tuple[PDFDictionary, bytes]: (metadata, stream data)
        """
        if isinstance(obj_ref, ObjectRef):
            obj = self.get_object_from_ref(obj_ref)
        elif isinstance(obj_ref, IndirectObject):
            obj = obj_ref
        else:
            raise BrokenFilePDF(f"Expected a pdf-stream, instead found {obj_ref}")

        if obj.stream is None:
            raise BrokenFilePDF(f"Expected a pdf-stream, instead found {obj}")
        else:
            obj_def = obj.get_object()
            if not isinstance(obj_def, PDFDictionary):
                self.health_report.write_error(
                    BrokenFilePDF(
                        f"Stream object is missing a defining dictionary {obj_def} {obj_def}"
                    )
                )
                obj_def = PDFDictionary()
            return obj_def, decode_stream(obj.stream, self.buffer)

    def decode_stream(self, stream: PDFStream) -> bytes:
        """Decode the bytes associated with the PDF-Stream

        Args:
            stream (PDFStream)

        Returns:
            bytes
        """
        return decode_stream(stream, self.buffer)
