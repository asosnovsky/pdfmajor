import json
from pathlib import Path
from typing import Any, Dict, List, NamedTuple, Optional

CORE_14_FOLDER = Path(__file__).parent / "core14"
ALL_FILES = {fpath.stem: fpath for fpath in CORE_14_FOLDER.iterdir()}


class StandardFontMetric(NamedTuple):
    descriptor: Dict[str, Any]
    char_codes: List[int]
    widths: List[int]


def get_ifexists(font_name: str) -> Optional[StandardFontMetric]:
    """checks if have the font's parsed afm file, and return it's metadata if we do

    Args:
        font_name (str)

    Returns:
        Optional[StandardFontMetric]
    """
    if font_name in ALL_FILES:
        data = json.loads(ALL_FILES[font_name].read_text())
        return StandardFontMetric(
            descriptor=data["descriptor"],
            char_codes=data["metrics"]["codes"],
            widths=data["metrics"]["widths"],
        )
    return None
