#  (Boolean values, Integer and Real numbers, Strings, Names), Arrays, Dictionaries, Streams, and the null object


from abc import ABCMeta, abstractmethod
from typing import Any


class PDFObject(metaclass=ABCMeta):
    """A common abstract class that other PDF Objects will extend"""

    @abstractmethod
    def to_python(self) -> Any:
        """returns the python variation of this object"""
        raise NotImplementedError

    def __eq__(self, o: object) -> bool:
        if not isinstance(o, self.__class__):
            return False
        return o.to_python() == self.to_python()  # type: ignore

    def __repr__(self) -> str:
        return "{cls}({data})".format(
            cls=self.__class__.__name__, data=self.to_python()
        )


class PDFContextualObject(PDFObject):
    """An abstract class representing objects that require context for construction"""

    @abstractmethod
    def pass_item(self, item: PDFObject) -> None:
        raise NotImplementedError
