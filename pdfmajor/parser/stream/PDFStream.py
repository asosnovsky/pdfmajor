from typing import Any, List, Optional, TypeVar, Union

from pdfmajor.parser.objects.base import PDFObject

from ..objects.collections import PDFDictionary
from ..objects.primitives import PDFNull


class PDFStream:
    """A class representing a PDF Stream as specified in PDF spec 1.7 section 7.3.8"""

    def __init__(
        self,
        offset: int = 0,
        length: PDFObject = PDFNull(),
        filter: Optional[List[PDFObject]] = None,
        decode_parms: Optional[List[PDFObject]] = None,
        f: Optional[Any] = None,  # TODO: file-specifications
        ffilter: Optional[List[PDFObject]] = None,
        fdecode_parms: Optional[List[PDFObject]] = None,
        dl: Optional[PDFObject] = None,
    ) -> None:
        """
        Args:
            offset (int): the offset where the stream itself starts
            length (PotentialInt): the length of the stream
            filter (Optional[List[str]], optional): The names of a filter that shall be applied in  processing the stream data. Defaults to None.
            decode_parms (Optional[List[Dict[str, Any]]], optional):  Parameter dictionaries used by the filters specified by filter. Defaults to None.
            f (Optional[Any], optional): The file containing the stream data. If this entry is present, the bytes between stream and endstream shall be ignored. However, the Length entry should still specify the number of those bytes (usually, there are no bytes and Length is 0).. Defaults to None.
            ffilter (Optional[List[str]], optional): The names of a filter that shall be applied in processing of the external file. Defaults to None.
            fdecode_parms (Optional[List[Dict[str, Any]]], optional):  Parameter dictionaries used by the filters specified by ffilter. Defaults to None.
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

    @classmethod
    def from_pdfdict(cls, offset: int, item: PDFDictionary) -> "PDFStream":
        stream = cls(offset, item["Length"])
        stream.filter = get_single_or_list(item.get("Filter", stream.filter))
        stream.decode_parms = get_single_or_list(
            item.get("DecodeParms", stream.decode_parms)
        )
        stream.f = item.get("F", stream.f)
        stream.ffilter = get_single_or_list(item.get("FFilter", stream.ffilter))
        stream.fdecode_parms = get_single_or_list(
            item.get("FDecodeParms", stream.fdecode_parms)
        )
        return stream

    def to_python(self):
        return {
            "offset": self.offset,
            "length": self.length.to_python(),
            "filter": to_python_list(self.filter),
            "decode_parms": to_python_list(self.decode_parms),
            "f": self.f,
            "ffilter": to_python_list(self.ffilter),
            "fdecode_parms": to_python_list(self.fdecode_parms),
            "dl": to_python(self.dl),
        }


T = TypeVar("T")


def get_single_or_list(obj: Optional[Union[List[T], T]]) -> List[T]:
    if obj is None:
        return []
    elif isinstance(obj, list):
        return obj
    else:
        return [obj]


def to_python(obj: Optional[PDFObject]) -> Any:
    if obj is None:
        return None
    return obj.to_python()


def to_python_list(obj: Optional[List[PDFObject]]) -> List[Any]:
    if obj is None:
        return []
    return [x.to_python() for x in obj]
