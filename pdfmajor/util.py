from typing import Any, Dict, List, Optional, TypeVar, Union

T = TypeVar("T")


def get_single_or_list(obj: Optional[Union[List[T], T]]) -> List[T]:
    if obj is None:
        return []
    elif isinstance(obj, list):
        return obj
    else:
        return [obj]


D = TypeVar("D", bound=Dict)


def deep_copy(dst: D, src: D):
    for (k, v) in src.items():
        if isinstance(v, dict):
            d: Any = {}
            dst[k] = d
            deep_copy(d, v)
        else:
            dst[k] = v
