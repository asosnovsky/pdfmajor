from .PDFColor import PDFColor, PDFColorSpace
from .PDFColorSpace import PREDEFINED_COLORSPACE

class PDFGraphicState(object):
    class InvalidOperation(Exception): pass

    def __init__(self):
        self.linewidth = 0
        self.linecap = None
        self.linejoin = None
        self.miterlimit = None
        self.dash = None
        self.intent = None
        self.flatness = None
        self.scolor:PDFColor = PDFColor(None)
        self.ncolor:PDFColor = PDFColor(None)
        self.scolspace:PDFColorSpace = None
        self.ncolspace:PDFColorSpace = None

    def set_stroke_color(self, colspace: PDFColorSpace, *values):
        if colspace is None:
            colspace = self.scolspace
        self.scolor = PDFColor(colspace, *values)

    def set_nostroke_color(self, colspace: PDFColorSpace, *values):
        if colspace is None:
            colspace = self.ncolspace
        self.ncolor = PDFColor(colspace, *values)

    def copy(self):
        obj = PDFGraphicState()
        obj.linewidth   = self.linewidth
        obj.linecap     = self.linecap
        obj.linejoin    = self.linejoin
        obj.miterlimit  = self.miterlimit
        obj.dash        = self.dash
        obj.intent      = self.intent
        obj.flatness    = self.flatness
        obj.scolor      = self.scolor.copy()
        obj.ncolor      = self.ncolor.copy()
        obj.scolspace   = self.scolspace
        obj.ncolspace   = self.ncolspace
        return obj

    def __repr__(self):
        return ('<PDFGraphicState linewidth=%r, linecap=%r, linejoin=%r, '
                ' miterlimit=%r, dash=%r, intent=%r, flatness=%r, '
                ' stroking color=%r, non stroking color=%r'
                '>' %
                (
                    self.linewidth, self.linecap, self.linejoin,
                    self.miterlimit, self.dash, self.intent, self.flatness,
                    str(self.scolor), str(self.ncolor)
                 )
        )
