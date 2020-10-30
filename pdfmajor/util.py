from typing import Any, List, Optional, Type, TypeVar, Union

from pdfmajor.parser.objects.base import PDFObject

T = TypeVar("T")


def get_single_or_list(obj: Optional[Union[List[T], T]]) -> List[T]:
    if obj is None:
        return []
    elif isinstance(obj, list):
        return obj
    else:
        return [obj]


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
