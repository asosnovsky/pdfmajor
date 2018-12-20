from typing import List
from .PDFColorSpace import PDFColorSpace

class PDFColor:
    def __init__(self, color_space: PDFColorSpace, *values: List[float]):
        self.color_space: PDFColorSpace = color_space
        self.values: list = values

    def copy(self):
        return self.__class__(
            self.color_space,
            *self.values
        )
    
    def __repr__(self):
        return f"<PDFColor space={self.color_space} values={self.values}/>"
