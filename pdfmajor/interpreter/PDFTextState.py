from .PDFFont import PDFFont
from ..utils import MATRIX_IDENTITY


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
        self.reset()
        # self.matrix is set
        # self.linematrix is set
        return

    def __repr__(self):
        return ('<PDFTextState: font=%r, fontsize=%r, charspace=%r, wordspace=%r, '
                ' scaling=%r, leading=%r, render=%r, rise=%r, '
                ' matrix=%r, linematrix=%r>' %
                (self.font, self.fontsize, self.charspace, self.wordspace,
                 self.scaling, self.leading, self.render, self.rise,
                 self.matrix, self.linematrix))

    def copy(self):
        obj = PDFTextState()
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
        return obj

    def reset(self):
        self.matrix = MATRIX_IDENTITY
        self.linematrix = (0, 0)
        return
