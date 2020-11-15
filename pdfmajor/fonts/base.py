from abc import ABCMeta, abstractclassmethod
from typing import Any, Dict


class PDFFont(metaclass=ABCMeta):
    """an object reprsenting a PDF Font as decribed in PDF Spec 1.7 section 9.5"""

    def __init__(self, subtype: str, **kwrg: Any) -> None:
        self.subtype = subtype
        self.raw = kwrg

    def __repr__(self) -> str:
        return f"PDFFont:{self.subtype}({self.raw})"

    @abstractclassmethod
    def from_dict(cls, d: Dict[str, Any]) -> "PDFFont":
        raise NotImplementedError
