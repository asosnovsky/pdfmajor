from .PDFGraphicStateColor import PDFGraphicStateColor

class PDFGraphicState(object):

    def __init__(self):
        self.linewidth = 0
        self.linecap = None
        self.linejoin = None
        self.miterlimit = None
        self.dash = None
        self.intent = None
        self.flatness = None

        # stroking color
        self.scolor = PDFGraphicStateColor()

        # non stroking color
        self.ncolor = PDFGraphicStateColor()
        
        return

    def copy(self):
        obj = PDFGraphicState()
        obj.linewidth = self.linewidth
        obj.linecap = self.linecap
        obj.linejoin = self.linejoin
        obj.miterlimit = self.miterlimit
        obj.dash = self.dash
        obj.intent = self.intent
        obj.flatness = self.flatness
        obj.scolor = self.scolor.copy()
        obj.ncolor = self.ncolor.copy()
        return obj

    def __repr__(self):
        return ('<PDFGraphicState: linewidth=%r, linecap=%r, linejoin=%r, '
                ' miterlimit=%r, dash=%r, intent=%r, flatness=%r, '
                ' stroking color=%r, non stroking color=%r'
                '>' %
                (
                    self.linewidth, self.linecap, self.linejoin,
                    self.miterlimit, self.dash, self.intent, self.flatness,
                    str(self.scolor), str(self.ncolor)
                 )
        )
