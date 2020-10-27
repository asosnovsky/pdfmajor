from pdfmajor.parser.exceptions import ParserError
from typing import Any, Dict, List, Optional, Union

from ..objects.base import PDFObject
from ..objects.collections import PDFDictionary


class PDFStream:
    """A class representing a PDF Stream as specified in PDF spec 1.7 section 7.3.8"""

    def __init__(
        self,
        offset: int = 0,
        length: int = 0,
        filter: Optional[List[str]] = None,
        decode_parms: Optional[List[Dict[str, Any]]] = None,
        f: Optional[Any] = None,  # file-specifications
        ffilter: Optional[List[str]] = None,
        fdecode_parms: Optional[List[Dict[str, Any]]] = None,
        dl: Optional[int] = None,
    ) -> None:
        """
        Args:
            offset (int): the offset where the stream itself starts
            length (int): the length of the stream
            filter (Optional[List[str]], optional): The names of a filter that shall be applied in  processing the stream data. Defaults to None.
            decode_parms (Optional[List[Dict[str, Any]]], optional):  Parameter dictionaries used by the filters specified by filter. Defaults to None.
            f (Optional[Any], optional): The file containing the stream data. If this entry is present, the bytes between stream and endstream shall be ignored. However, the Length entry should still specify the number of those bytes (usually, there are no bytes and Length is 0).. Defaults to None.
            ffilter (Optional[List[str]], optional): The names of a filter that shall be applied in processing of the external file. Defaults to None.
            fdecode_parms (Optional[List[Dict[str, Any]]], optional):  Parameter dictionaries used by the filters specified by ffilter. Defaults to None.
            dl (Optional[int], optional): A  non-negative  integer  representing  the  number  of  bytes  in  the  decoded  (defiltered)  stream.  It  can  be  used to determine, for example, whether enough disk space is available to write a stream to a file.This  value  shall  be  considered  a  hint  only;  for  some  stream  filters, it may not be possible to determine this value precisely. Defaults to None.
        """
        self.offset = offset
        self.length = length
        self.filter: Optional[List[str]] = filter
        self.decode_parms: Optional[List[Dict[str, Any]]] = decode_parms
        self.f: Optional[Any] = f
        self.ffilter: Optional[List[str]] = ffilter
        self.fdecode_parms: Optional[List[Dict[str, Any]]] = fdecode_parms
        self.dl: Optional[int] = dl

    @classmethod
    def from_pdfdict(cls, offset: int, item: PDFObject) -> None:
        if not isinstance(item, PDFDictionary):
            raise ParserError(f"Cannot initilize a pdfstream with {type(item)}")
        data = item.to_python()
        stream = cls(offset, data["Length"])
        stream.filter = get_single_or_list(data.get("Filter", stream.filter))
        stream.decode_parms = get_single_or_list(
            data.get("DecodeParms", stream.decode_parms)
        )
        stream.f = data.get("F", stream.f)
        stream.ffilter = get_single_or_list(data.get("FFilter", stream.ffilter))
        stream.fdecode_parms = get_single_or_list(
            data.get("FDecodeParms", stream.fdecode_parms)
        )
        return stream

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


def get_single_or_list(obj: Optional[Union[List[Any], Any]]) -> List[Any]:
    if obj is None:
        return []
    elif isinstance(obj, list):
        return obj
    else:
        return [obj]
