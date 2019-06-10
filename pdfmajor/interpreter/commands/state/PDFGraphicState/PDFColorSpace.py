from typing import Dict
from collections import OrderedDict

class PDFColorSpace(object):

    def __init__(self, name: str, ncomponents: int):
        self.name: str = name
        self.ncomponents: int = ncomponents

    def __repr__(self):
        return '<PDFColorSpace: %s, ncomponents=%d>' % (self.name, self.ncomponents)


PREDEFINED_COLORSPACE: Dict[str, PDFColorSpace] = OrderedDict()

for (name, n) in [
    ('DeviceGray', 1),  # default value first
    ('CalRGB', 3),
    ('CalGray', 1),
    ('Lab', 3),
    ('DeviceRGB', 3),
    ('DeviceCMYK', 4),
    ('Separation', 1),
    ('Indexed', 1),
    ('Pattern', 1),
]:
    PREDEFINED_COLORSPACE[name]=PDFColorSpace(name, n)
