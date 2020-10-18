#  (Boolean values, Integer and Real numbers, Strings, Names), Arrays, Dictionaries, Streams, and the null object


from abc import ABCMeta, abstractmethod
from pdfmajor.execptions import ParserError
from pdfmajor.lexer.token import PDFName, TokenName, TokenPrimitive
from typing import Any, Dict, Generic, List, NamedTuple, Optional, TypeVar, Union

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


class PDFPrimivite(Generic[TToken], PDFObject):
    """A class representing any simple primitive data type as specified in PDF spec 1.7 section 7.3"""

    def __init__(self, token: TToken) -> None:
        self.token: TToken = token

    def get_value(self):
        return self.token.value

    def to_python(self) -> Union[TToken.value]:
        return self.value


class PDFDictionary(Dict[PDFName, PDFObject], PDFObject):
    """A class representing a PDF Dictionary as specified in PDF spec 1.7 section 7.3.7"""

    def __init__(self, strict: bool = False) -> None:
        super().__init__()
        self.name: Optional[PDFName] = None
        self.strict = strict

    def pass_item(self, item: PDFObject):
        if self.name is None:
            if isinstance(item, PDFPrimivite) and isinstance(item.token, TokenName):
                self.name = item.get_value()
                if self.strict:
                    raise ParserError("Invalid token provided to dictionary")
        else:
            self[self.name] = item.get_value()
            self.name = None

    def to_python(self) -> Dict[PDFName, Any]:
        return dict(self)


class PDFArray(List[PDFObject], PDFObject):
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


PDFComplexType = Union[PDFDictionary, PDFArray, PDFStream]
