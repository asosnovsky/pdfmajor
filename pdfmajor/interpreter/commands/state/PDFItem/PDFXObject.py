from ._base import PDFItem

class PDFXObject(PDFItem):
    def __init__(self, xobj_strem, bbox, resources, ctm):
        self.stream = xobj_strem
        self.bbox = bbox
        self.resources = resources
        self.ctm = ctm
        self.children = []