from typing import Tuple, Optional
from .PDFColorSpace import PDFColorSpace

class PDFColor:
    def __init__(self, color_space: Optional[PDFColorSpace], *values: float):
        self.color_space: Optional[PDFColorSpace] = color_space
        self.values: Tuple[float, ...] = values

    def copy(self):
        return self.__class__(
            self.color_space,
            *self.values
        )
    
    def __repr__(self):
        return f"""<PDFColor space="{
            None if self.color_space is None else self.color_space.name
        }" values={self.values}/>"""
