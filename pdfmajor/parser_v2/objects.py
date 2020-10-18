#  (Boolean values, Integer and Real numbers, Strings, Names), Arrays, Dictionaries, Streams, and the null object


from pdfmajor.execptions import ParserError
from pdfmajor.lexer.token import PDFName, TokenName, TokenPrimitive
from typing import Dict, Generic, List, NamedTuple, Optional, TypeVar, Union

TToken = TypeVar("TToken", bound=TokenPrimitive)


class PDFPrimivite(Generic[TToken]):
    def __init__(self, token: TToken) -> None:
        self.token: TToken = token

    @property
    def value(self):
        return self.token.value


class PDFDictionary(Dict[PDFName, "PDFObject"]):
    def __init__(self, strict: bool = False) -> None:
        super().__init__()
        self.name: Optional[PDFName] = None
        self.strict = strict

    def pass_item(self, item: "PDFObject"):
        if self.name is None:
            if isinstance(item, PDFPrimivite) and isinstance(item.token, TokenName):
                self.name = item.value
                if self.strict:
                    raise ParserError("Invalid token provided to dictionary")
        else:
            self[self.name] = item.value
            self.name = None

    @property
    def value(self):
        return dict(self)


class PDFArray(List["PDFObject"]):
    @property
    def value(self):
        return self


class PDFStream(object):
    @property
    def value(self):
        return self


PDFComplexType = Union[PDFDictionary, PDFArray, PDFStream]
PDFObject = Union[PDFComplexType, PDFPrimivite]
