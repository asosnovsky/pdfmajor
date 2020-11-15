from typing import Any, Dict
from .base import PDFFont


class PDFType0Font(PDFFont):
    """PDF Type 30 object see PDF spec 1.7 section 9.6
    TODO: finish this
    """

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "PDFType0Font":
        return cls("Type3", **d)
