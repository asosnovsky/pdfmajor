from typing import Optional, Tuple

from .base import PDFObject


class PDFComment(PDFObject):
    """A class representing a PDF comment"""

    def __init__(
        self,
        comment: bytes,
        loc: Tuple[int, int] = (0, 0),
        last_obj: Optional[PDFObject] = None,
        next_obj: Optional[PDFObject] = None,
    ) -> None:
        """
        Args:
            comment (bytes): the comment data
            loc (Tuple[int, int], optional): location of the comment in the byte-stream. Defaults to (0, 0).
        """
        self.comment = comment
        self.location = loc
        self.last_obj = last_obj
        self.next_obj = next_obj

    def to_python(self) -> Tuple[bytes, Tuple[int, int]]:
        """returns the value of the comment and where it is in the byte-strea,

        Returns:
            Tuple[bytes, Tuple[int, int]]: the first value in the tuple is the comment value and the second is the start and end location in the byte stream
        """
        return (self.comment, self.location)
