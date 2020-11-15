from typing import Any, Dict
from .base import PDFFont


class PDFCIDFont(PDFFont):
    """PDF Type 3 object see PDF spec 1.7 section 9.7.2
    TODO: finish this
    """

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "PDFCIDFont":
        return cls("Type3", **d)
