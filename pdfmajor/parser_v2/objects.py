#  (Boolean values, Integer and Real numbers, Strings, Names), Arrays, Dictionaries, Streams, and the null object


from abc import ABCMeta, abstractmethod
from pdfmajor.execptions import ParserError
from pdfmajor.lexer.token import PDFName, TokenName, TokenPrimitive
from typing import Dict, Generic, List, NamedTuple, Optional, TypeVar, Union

TToken = TypeVar("TToken", bound=TokenPrimitive)


class PDFObject(metaclass=ABCMeta):
    """A common abstract class that other PDF Objects will extend"""

    @abstractmethod
    def get_value(self):
        """return the base value of this object"""
        raise NotImplementedError

    @abstractmethod
    def to_python(self):
        """returns the python variation of this object"""
        raise NotImplementedError


class PDFPrimivite(Generic[TToken], PDFObject):
    def __init__(self, token: TToken) -> None:
        self.token: TToken = token

    def get_value(self):
        return self.token.value

    def to_python(self):
        return self.value


class PDFDictionary(Dict[PDFName, PDFObject], PDFObject):
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

    def get_value(self):
        return self

    def to_python(self):
        return dict(self)


class PDFArray(List[PDFObject], PDFObject):
    def get_value(self):
        return self

    def pass_item(self, item: PDFObject):
        self.append(item.get_value())

    def to_python(self):
        return list(self)


class PDFStream(PDFObject):
    def get_value(self):
        return self

    def to_python(self):
        return self


PDFComplexType = Union[PDFDictionary, PDFArray, PDFStream]
