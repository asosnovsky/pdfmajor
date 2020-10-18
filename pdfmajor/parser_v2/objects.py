#  (Boolean values, Integer and Real numbers, Strings, Names), Arrays, Dictionaries, Streams, and the null object


from abc import ABCMeta, abstractmethod
from pdfmajor.execptions import ParserError
from pdfmajor.lexer.token import (
    PDFName,
    TokenComment,
    TokenKeyword,
    TokenName,
    TokenPrimitive,
)
from typing import Any, Dict, Generic, List, Optional, Tuple, TypeVar

TToken = TypeVar("TToken", bound=TokenPrimitive)


class PDFObject(metaclass=ABCMeta):
    """A common abstract class that other PDF Objects will extend"""

    @abstractmethod
    def get_value(self):
        """return the base value of this object"""
        return self

    @abstractmethod
    def to_python(self):
        """returns the python variation of this object"""
        raise NotImplementedError

    def __eq__(self, o: object) -> bool:
        if not isinstance(o, self.__class__):
            return False
        return o.to_python() == self.to_python()

    def __repr__(self) -> str:
        return "{cls}({data})".format(
            cls=self.__class__.__name__, data=self.to_python()
        )


class PDFContextualObject(PDFObject):
    """An abstract class representing objects that require context for construction"""

    @abstractmethod
    def pass_item(self, item: PDFObject):
        raise NotImplementedError


class PDFPrimitive(Generic[TToken], PDFObject):
    """A class representing any simple primitive data type as specified in PDF spec 1.7 section 7.3"""

    def __init__(self, token: TToken) -> None:
        self.token: TToken = token

    def get_value(self):
        return self.token.value

    def to_python(self):
        return self.get_value()


class PDFComment(PDFObject):
    """A class representing a PDF comment"""

    def __init__(self, comment: bytes, loc: Tuple[int, int] = (0, 0)) -> None:
        """
        Args:
            comment (bytes): the comment data
            loc (Tuple[int, int], optional): location of the comment in the byte-stream. Defaults to (0, 0).
        """
        self.comment = comment
        self.location = loc

    def get_value(self):
        return self.comment

    def to_python(self):
        return (self.get_value(), self.location)


class PDFNull(PDFObject):
    """A class representing a PDF null object"""

    def get_value(self):
        return None

    def to_python(self):
        return None


class PDFDictionary(Dict[PDFName, PDFObject], PDFContextualObject):
    """A class representing a PDF Dictionary as specified in PDF spec 1.7 section 7.3.7"""

    def __init__(self, strict: bool = False) -> None:
        super().__init__()
        self.name: Optional[PDFName] = None
        self.strict = strict

    def pass_item(self, item: PDFObject):
        if self.name is None:
            if isinstance(item, PDFPrimitive) and isinstance(item.token, TokenName):
                self.name = item.get_value()
                if self.strict:
                    raise ParserError("Invalid token provided to dictionary")
        else:
            self[self.name] = item.get_value()
            self.name = None

    def to_python(self) -> Dict[PDFName, Any]:
        return dict(self)


class PDFArray(List[PDFObject], PDFContextualObject):
    """A class representing a PDF Array as specified in PDF spec 1.7 section 7.3.6"""

    def pass_item(self, item: PDFObject):
        self.append(item.get_value())

    def to_python(self) -> List[Any]:
        return list(self)


class PDFStream(PDFObject):
    """A class representing a PDF Stream as specified in PDF spec 1.7 section 7.3.8"""

    def __init__(
        self,
        offset: int,
        length: int,
        filter: Optional[List[PDFName]] = None,
        decode_parms: Optional[List[PDFDictionary]] = None,
        f: Optional[Any] = None,  # file-specifications
        ffilter: Optional[List[PDFName]] = None,
        fdecode_parms: Optional[List[PDFDictionary]] = None,
        dl: Optional[int] = None,
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
