from pdfmajor.exceptions import BrokenFile


class FilterError(BrokenFile):
    pass


class DecodeFailed(FilterError):
    pass


class InvalidDecoderOrNotImplemented(DecodeFailed, NotImplementedError):
    pass


class CCITEOFB(DecodeFailed, EOFError):
    pass


class CCITInvalidData(DecodeFailed):
    pass


class CCITByteSkip(DecodeFailed):
    pass
