import logging

from typing import Dict

from contextlib import contextmanager

from ..layouts import LTPage
from ..layouts import LTItem
from ..layouts import LTCurve
from ..layouts import LTLine
from ..layouts import LTRect
from ..layouts import LTFigure
from ..layouts import LTImage
from ..layouts import LTChar
from ..interpreter.PDFGraphicState import PDFGraphicStateColor
from ..utils import enc

from .PDFConverter import PDFConverter

log = logging.getLogger(__name__)

class TextConverter(PDFConverter):
    def __init__(self, 
        rsrcmgr, 
        outfp, 
        codec='utf-8', 
        pageno=1, 
        imagewriter=None,
    ):
        PDFConverter.__init__(self, rsrcmgr, outfp, imagewriter=imagewriter, codec=codec, pageno=pageno)
    
    def write(self, text: str):
        if self.codec:
            text = text.encode(self.codec)
        self.outfp.write(text)
    
    def place_text(self, char: LTChar):
        self.write(char.get_text())

    def receive_layout(self, ltpage: LTPage):
        def render(item: LTItem):
            if isinstance(item, LTPage):
                self.write(f'\n-----[Page {self.pageno-1}]-----\n')
                for child in item:
                    render(child)
                self.write(f'\n-----[Page {self.pageno-1}]-----\n')
            elif isinstance(item, LTFigure):
                for child in item:
                    render(child)
            elif isinstance(item, LTChar):
                self.place_text(item)
        render(ltpage)
