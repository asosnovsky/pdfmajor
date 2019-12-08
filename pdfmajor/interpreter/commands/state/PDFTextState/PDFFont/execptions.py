from pdfmajor.parser.PDFStream import PDFException

class PDFFontError(PDFException): pass
class PDFUnicodeNotDefined(PDFFontError): pass
