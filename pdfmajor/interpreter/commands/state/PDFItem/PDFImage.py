from pdfmajor.parser.PDFStream import PDFStream
from ._base import PDFItem

class PDFImage(PDFItem):
    def __init__(self, stream: PDFStream):
        self.stream = stream
