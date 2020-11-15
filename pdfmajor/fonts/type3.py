from typing import Any, Dict
from .base import PDFFont


class PDFType3Font(PDFFont):
    """PDF Type 3 object see PDF spec 1.7 section 9.6.5
    TODO: finish this
    """

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "PDFType3Font":
        return cls("Type3", **d)
