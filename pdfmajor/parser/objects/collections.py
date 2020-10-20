from typing import Any, Dict, List, Optional
from ..exceptions import ParserError
from .base import PDFContextualObject, PDFObject
from .primitives import PDFName


class PDFArray(List[PDFObject], PDFContextualObject):
    """A class representing a PDF Array as specified in PDF spec 1.7 section 7.3.6"""

    def pass_item(self, item: PDFObject):
        self.append(item)

    def to_python(self) -> List[Any]:
        return [x.to_python() for x in self]


class PDFDictionary(Dict[str, PDFObject], PDFContextualObject):
    """A class representing a PDF Dictionary as specified in PDF spec 1.7 section 7.3.7"""

    def __init__(self, strict: bool = False) -> None:
        super().__init__()
        self.name: Optional[PDFName] = None
        self.last_name: Optional[PDFName] = None
        self.strict = strict

    @property
    def last_item_value(self):
        return self[self.last_name]

    def pass_item(self, item: PDFObject):
        if self.name is None:
            if isinstance(item, PDFName):
                self.name = item
            elif self.strict:
                raise ParserError(
                    f"Invalid token provided to dictionary as a key {item}"
                )
        else:
            self[self.name.value] = item
            self.last_name = self.name
            self.name = None

    def to_python(self) -> Dict[str, Any]:
        return {k: v.to_python() for k, v in self.items()}
