from pathlib import Path
from unittest import TestCase

from pdfmajor.streambuffer import BufferStream
from pdfmajor.parser.xref import iter_over_xref

CURRENT_FOLDER = Path(__file__).parent


class Standard(TestCase):
    def test_char_doc(self):
        with (CURRENT_FOLDER / "samples" / "pdf" / "chars.pdf").open("rb") as fp:
            buffer = BufferStream(fp)
            for xref in iter_over_xref(buffer):
                print(xref)
