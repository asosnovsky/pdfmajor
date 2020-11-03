from typing import Any, List, Optional, Type, TypeVar, Union

from .base import PDFObject
from .primitives import PDFInteger, PDFReal

T = TypeVar("T")


def to_python(obj: Optional[PDFObject]) -> Any:
    if obj is None:
        return None
    return obj.to_python()


def to_python_list(obj: Optional[List[PDFObject]]) -> List[Any]:
    if obj is None:
        return []
    return [x.to_python() for x in obj]


ExpectedType = TypeVar("ExpectedType", bound=PDFObject)


def validate_object_or_none(
    obj: Optional[PDFObject], objtype: Type[ExpectedType]
) -> Optional[ExpectedType]:
    """Validates the object's type if its not None

    Args:
        obj (Optional[PDFObject])
        objtype (Type[ExpectedType]): expected type of the object

    Raises:
        AssertionError: is raised if the object has an invalid type

    Returns:
        Optional[ExpectedType]
    """
    if obj is None:
        return None
    if isinstance(obj, objtype):
        return obj
    else:
        raise AssertionError(f"obj {obj} is not of expected type {objtype}")


def validate_number_or_none(
    obj: Optional[PDFObject],
) -> Optional[Union[PDFReal, PDFInteger]]:
    """Validates the object's type is some numeric type

    Args:
        obj (Optional[PDFObject])

    Raises:
        AssertionError: is raised if the object has an invalid type

    Returns:
        Optional[Union[PDFReal, PDFInteger]]
    """
    if obj is None:
        return None
    if isinstance(obj, PDFInteger) or isinstance(obj, PDFReal):
        return obj
    else:
        raise AssertionError(f"obj {obj} is not of numeric type")
