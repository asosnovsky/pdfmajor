from typing import Any, List, Optional, Union

from pdfmajor.parser.exceptions import IncompleteStream
from pdfmajor.util import get_single_or_list

from .base import PDFObject
from .collections import PDFDictionary
from .primitives import PDFInteger, PDFNull
from .ref import ObjectRef
from .util import to_python, to_python_list


class PDFStream:
    """A class representing a PDF Stream as specified in PDF spec 1.7 section 7.3.8"""

    def __init__(
        self,
        offset: int,
        length: Union[PDFInteger, ObjectRef],
        filter: List[PDFObject],
        decode_parms: List[PDFObject],
        ffilter: List[PDFObject],
        fdecode_parms: List[PDFObject],
        dl: Optional[PDFObject] = None,
        f: Optional[Any] = None,  # TODO: file-specifications
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
        if not isinstance(item["Length"], PDFInteger) and not isinstance(
            item["Length"], ObjectRef
        ):
            raise IncompleteStream(
                f"Invalid length property {item} {type(item['Length'])}"
            )
        filters = get_single_or_list(item.get("Filter", None))
        decode_parms = get_single_or_list(item.get("DecodeParms", None))
        if len(decode_parms) == 0:
            decode_parms = [PDFNull()] * len(filters)
        ffilter = get_single_or_list(item.get("FFilter", None))
        fdecode_parms = get_single_or_list(item.get("FDecodeParms", None))
        if len(fdecode_parms) == 0:
            fdecode_parms = [PDFNull()] * len(ffilter)
        stream = cls(
            offset,
            item["Length"],
            filter=filters,
            decode_parms=decode_parms,
            ffilter=ffilter,
            fdecode_parms=fdecode_parms,
            f=item.get("F", None),
            dl=item.get("DL", None),
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
