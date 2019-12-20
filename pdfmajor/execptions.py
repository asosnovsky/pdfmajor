

class PDFMajorException(Exception):
    pass

# Interpreter Errors
class InterpreterError(PDFMajorException):
    pass

class EmptyDocumentError(InterpreterError):
    pass

class CommandProcessorError(InterpreterError):
    pass

class InvalidOperation(CommandProcessorError): 
    pass

class RepeatedCommand(CommandProcessorError): 
    pass

class FontError(InterpreterError):
    pass

class UnicodeNotDefined(FontError): 
    pass

class MissingFont(FontError): 
    pass


# Parser Errors
class ParserError(PDFMajorException):
    pass

class PDFNoOutlines(ParserError): 
    pass

class PDFDestinationNotFound(ParserError):
    pass

class PDFNoValidXRef(ParserError):
    pass

class CMapNotFound(ParserError):
    pass

class PSException(ParserError):
    pass


class PSEOF(PSException):
    pass


class PSSyntaxError(PSException):
    pass


class PSTypeError(PSException):
    pass


class PSValueError(PSException):
    pass

class CCITTExeception(ParserError):
    pass

class EOFB(CCITTExeception):
    pass

class InvalidData(CCITTExeception):
    pass

class ByteSkip(ExceptCCITTExeceptionion):
    pass

class PDFTextExtractionNotAllowed(ParserError):
    pass

# converter error

class ConverterException(PDFMajorException):
    pass 

class FileAccessException(ConverterException):
    pass