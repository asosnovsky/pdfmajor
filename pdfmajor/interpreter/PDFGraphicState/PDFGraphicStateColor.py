class PDFGraphicStateColor:
    class NotSet(Exception): pass

    def __init__(self):
        self.__rgb = None
        self.__gray = None
        self.__cmyk = None

    def get_color(self):
        if self.__rgb is not None:
            return 'rgb', self.rgb
        elif self.__cmyk is not None:
            return 'cmyk', self.cmyk
        elif self.__gray is not None:
            return 'gray', self.gray
        else: return None, None
    
    @property
    def is_set(self):
        return self.__rgb is not None or self.__cmyk is not None or self.__gray is not None

    @property
    def rgb(self):
        if self.__rgb is not None: return [*self.__rgb]
        else: raise self.NotSet

    @property
    def cmyk(self):
        if self.__cmyk is not None: return [*self.__cmyk]
        else: raise self.NotSet

    @property
    def gray(self):
        if self.__gray is not None: return float(self.__gray)
        else: raise self.NotSet

    @rgb.setter
    def rgb(self, rgb):
        self.__rgb = rgb

    @cmyk.setter
    def cmyk(self, cmyk):
        self.__cmyk = cmyk

    @gray.setter
    def gray(self, color):
        self.__gray = color

    def copy(self):
        cp = self.__class__()
        cp.gray = self.__gray
        cp.rgb = self.__rgb
        cp.cmyk = self.__cmyk
        return cp

    def __repr__(self):
        rep = "<PDFGraphicStateColor"
        if self.__gray is not None: rep += f' gray={self.__gray}'
        if self.__rgb is not None: rep += f' rgb=[{",".join(map(str, self.__rgb))}]'
        if self.__cmyk is not None: rep += f' cmyk=[{",".join(map(str, self.__cmyk))}]'
        return rep + '/>'
