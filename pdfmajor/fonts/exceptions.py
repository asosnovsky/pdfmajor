from pdfmajor.exceptions import PDFMajorException


class PDFFontError(PDFMajorException):
    pass


class InvalidFont(PDFFontError):
    def __init__(self, subtype: str) -> None:
        super().__init__(f"The font {subtype} is invalid")
