import io


class PDFLexer:
    def __init__(self, fp: io.BufferedIOBase) -> None:
        self.fp = fp

    def seek(self, pos: int):
        self.fp.seek(pos)
