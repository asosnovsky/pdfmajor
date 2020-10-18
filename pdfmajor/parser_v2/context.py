from pdfmajor.parser_v2.exceptions import ParserError
from pdfmajor.parser_v2.objects import (
    PDFArray,
    PDFDictionary,
    PDFObject,
    PDFComplexType,
    PDFStream,
)


class PDFParseContext:
    """A parsing context
    This class helps constructs complex PDF types
    """

    __slots__ = ["pdfobject"]

    def __init__(self, pdfobject: PDFComplexType) -> None:
        """
        Args:
            pdfobject (PDFComplexType): the complex pdf object we  are trying to build
        """
        self.pdfobject = pdfobject

    def push(self, item: PDFObject):
        """push any pdf object to the context, process according to the type of complex object we are trying to build

        Args:
            item (PDFObject)

        Raises:
            ParserError: raises if an invalid complex object is used
        """
        if isinstance(self.pdfobject, PDFArray):
            self.pdfobject.pass_item(item)
        elif isinstance(self.pdfobject, PDFDictionary):
            self.pdfobject.pass_item(item)
        elif isinstance(self.pdfobject, PDFStream):
            raise NotImplementedError
        else:
            raise ParserError(f"Invalid Context {type(self.pdfobject)}")
