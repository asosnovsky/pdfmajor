from pdfmajor.execptions import MissingFont, UnicodeNotDefined
from pdfmajor.utils import MATRIX_IDENTITY
from .PDFFont import PDFFont, get_font

##  PDFTextState
##
class PDFTextState(object):
        
    def __init__(self):
        self.font: PDFFont = None
        self.fontsize: int = 0
        self.charspace: int = 0
        self.wordspace: int = 0
        self.scaling: int = 100
        self.leading: int = 0
        self.render: int = 0
        self.rise: int = 0
        self.matrix = MATRIX_IDENTITY
        self.linematrix = [0, 0]
        self.ignore_bad_chars = False

    def __repr__(self):
        return ('<PDFTextState: font=%r, fontsize=%r, charspace=%r, wordspace=%r, '
                ' scaling=%r, leading=%r, render=%r, rise=%r, '
                ' matrix=%r, linematrix=%r ignore_bad_chars=%r>' %
                (self.font, self.fontsize, self.charspace, self.wordspace,
                 self.scaling, self.leading, self.render, self.rise,
                 self.matrix, self.linematrix, self.ignore_bad_chars))
    
    def to_unichr(self, cid: int) -> str:
        if self.font is None:
            raise MissingFont
        try:
            return self.font.to_unichr(cid)
        except UnicodeNotDefined as e:
            if self.ignore_bad_chars:
                return ""
            else:
                raise e


    def copy(self):
        obj = self.__class__()
        obj.font = self.font
        obj.fontsize = self.fontsize
        obj.charspace = self.charspace
        obj.wordspace = self.wordspace
        obj.scaling = self.scaling
        obj.leading = self.leading
        obj.render = self.render
        obj.rise = self.rise
        obj.matrix = self.matrix
        obj.linematrix = self.linematrix
        obj.ignore_bad_chars = self.ignore_bad_chars
        return obj

    def reset_matrices(self):
        self.matrix = MATRIX_IDENTITY
        self.linematrix = [0, 0]

    @property
    def is_upright(self):
        return (0 < self.matrix[:,0].prod()*self.scaling and self.matrix[0,1:].prod() <= 0)