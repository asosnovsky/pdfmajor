from ..utils import get_logger

log = get_logger(__name__)

from ..layouts import PDFLayoutAnalyzer, PDFPage, LTPage

class PDFExctractor(PDFLayoutAnalyzer):
    def end_page(self, page: PDFPage):
        assert not self._stack, str(len(self._stack))
        assert isinstance(self.cur_item, LTPage), str(type(self.cur_item))
        self.pageno += 1
        return self.cur_item
