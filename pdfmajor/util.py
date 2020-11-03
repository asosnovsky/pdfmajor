from typing import List, Optional, TypeVar, Union

T = TypeVar("T")


def get_single_or_list(obj: Optional[Union[List[T], T]]) -> List[T]:
    if obj is None:
        return []
    elif isinstance(obj, list):
        return obj
    else:
        return [obj]
