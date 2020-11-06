from typing import Any, Dict, Union

from .base import PDFFont
from . import standard14


class PDFType1(PDFFont):
    """A standard font in the PDF, as is defined by PDF spec 1.7 section 9.6.2"""

    def __init__(
        self,
        base_font: str,
        widths: Dict[int, int],
        font_descriptor: Dict[str, int],
        encoding: Union[str, Dict[str, Any], None],
        to_unicode: Any,
    ) -> None:
        PDFFont.__init__(
            self,
            "Type1",
            base_font=base_font,
            widths=widths,
            font_descriptor=font_descriptor,
            encoding=encoding,
            to_unicode=to_unicode,
        )

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "PDFType1":
        base_font = str(d["BaseFont"])
        stnd_font = standard14.get_ifexists(base_font)
        encoding = d.get("Encoding", None)
        to_unicode = d.get("ToUnicode", None)
        if stnd_font is not None:
            return cls(
                base_font=base_font,
                widths={k: v for k, v in zip(stnd_font.char_codes, stnd_font.widths)},
                font_descriptor=stnd_font.descriptor,
                encoding=encoding,
                to_unicode=to_unicode,
            )
        else:
            first_char = int(d.get("FirstChar", 0))
            last_char = int(d.get("FirstChar", 255))
            if d.get("Widths"):
                widths_array = map(int, d["Widths"])
            else:
                widths_array = (0 for _ in range((last_char - first_char + 1)))
            font_descriptor = dict(d["FontDescriptor"])  # type: Any
            return cls(
                base_font=base_font,
                widths={(i + first_char): w for (i, w) in enumerate(widths_array)},
                font_descriptor=font_descriptor,
                encoding=encoding,
                to_unicode=to_unicode,
            )
