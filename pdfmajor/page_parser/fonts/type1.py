from typing import Any, Dict, Union

from .base import PDFFont


class PDFType1(PDFFont):
    def __init__(
        self,
        base_font: str,
        widths: Dict[bytes, int],
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

    # def from_dict(cls, d: Dict[str, Any]) -> "PDFType1":
    #     base_font = str(d["BaseFont"])
    #     if base_font in STANDARD14_FONT_METRICS.keys():
    #         font_descriptor, widths_raw = STANDARD14_FONT_METRICS[base_font]
    #         widths = {c.encode(): w for c, w in widths_raw.items()}
    #     else:
    #         first_char = int(d.get("FirstChar", 0))
    #         last_char = int(d.get("FirstChar", 255))
    #         if d.get("Widths"):
    #             widthts_array = map(int, d["Widths"])
    #         else:
    #             widthts_array = [0] * (last_char - first_char + 1)
    #         font_descriptor = dict(d["FontDescriptor"])
    #         widths = {
    #             bytes([(i + first_char)]): w for (i, w) in enumerate(widthts_array)
    #         }
    #     encoding = d.get("Encoding", None)
    #     to_unicode = d.get("ToUnicode", None)
    #     return cls(base_font, widths, font_descriptor, encoding, to_unicode)
