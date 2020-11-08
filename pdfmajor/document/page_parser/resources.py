from typing import Any, Dict, List, NamedTuple, Union
from pdfmajor.fonts import PDFFont


class PDFResources(NamedTuple):
    """A class storing PDF Resources as described in PDF spec 1.7. section 7.8.3"""

    extgstate: Dict[str, Any]
    color_space: Dict[str, Union[str, List[str]]]
    pattern: Dict[str, Any]
    shading: Dict[str, Any]
    xobject: Dict[str, Any]
    font: Dict[str, PDFFont]
    procset: Dict[str, Any]
