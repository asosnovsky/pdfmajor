from pdfmajor.parser_v3.exceptions import ParserError
from typing import Any, Dict, List, Optional
from .base import PDFContextualObject, PDFObject
from .primitives import PDFName
from .collections import PDFDictionary


class PDFStream(PDFContextualObject):
    """A class representing a PDF Stream as specified in PDF spec 1.7 section 7.3.8"""

    def __init__(
        self,
        offset: int = 0,
        length: int = 0,
        filter: Optional[List[PDFName]] = None,
        decode_parms: Optional[List[PDFDictionary]] = None,
        f: Optional[Any] = None,  # file-specifications
        ffilter: Optional[List[PDFName]] = None,
        fdecode_parms: Optional[List[PDFDictionary]] = None,
        dl: Optional[int] = None,
        other_metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Args:
            offset (int): the offset where the stream itself starts
            length (int): the length of the stream
            filter (Optional[List[PDFName]], optional): The names of a filter that shall be applied in  processing the stream data. Defaults to None.
            decode_parms (Optional[List[PDFDictionary]], optional):  Parameter dictionaries used by the filters specified by filter. Defaults to None.
            f (Optional[Any], optional): The file containing the stream data. If this entry is present, the bytes between stream and endstream shall be ignored. However, the Length entry should still specify the number of those bytes (usually, there are no bytes and Length is 0).. Defaults to None.
            ffilter (Optional[List[PDFName]], optional): The names of a filter that shall be applied in processing of the external file. Defaults to None.
            fdecode_parms (Optional[List[PDFDictionary]], optional):  Parameter dictionaries used by the filters specified by ffilter. Defaults to None.
            dl (Optional[int], optional): A  non-negative  integer  representing  the  number  of  bytes  in  the  decoded  (defiltered)  stream.  It  can  be  used to determine, for example, whether enough disk space is available to write a stream to a file.This  value  shall  be  considered  a  hint  only;  for  some  stream  filters, it may not be possible to determine this value precisely. Defaults to None.
        """
        self.offset = offset
        self.length = length
        self.filter = filter
        self.decode_parms = decode_parms
        self.f = f
        self.ffilter = ffilter
        self.fdecode_parms = fdecode_parms
        self.dl = dl
        self.other_metadata = other_metadata if other_metadata is not None else {}

    def pass_item(self, item: PDFObject) -> None:
        if not isinstance(item, PDFDictionary):
            raise ParserError(f"Cannot initilize a pdfstream with {type(item)}")
        data = item.to_python()
        self.length = data["Length"]
        self.filter = data.get("Filter", self.filter)
        self.decode_parms = data.get("DecodeParms", self.decode_parms)
        self.f = data.get("F", self.f)
        self.ffilter = data.get("FFilter", self.ffilter)
        self.fdecode_parms = data.get("FDecodeParms", self.fdecode_parms)
        self.other_metadata = data

    def to_python(self):
        return {
            "offset": self.offset,
            "length": self.length,
            "filter": self.filter,
            "decode_parms": None
            if self.decode_parms is None
            else [x.to_python() for x in self.decode_parms],
            "f": self.f,
            "ffilter": self.ffilter,
            "fdecode_parms": None
            if self.fdecode_parms is None
            else [x.to_python() for x in self.fdecode_parms],
            "dl": self.dl,
        }
