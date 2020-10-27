from pathlib import Path
from pdfmajor.parser.xrefdb import XRefDB
from pdfmajor.parser import _save_or_get_object
from unittest import TestCase

from pdfmajor.streambuffer import BufferStream
from pdfmajor.parser.xref import iter_over_xref

CURRENT_FOLDER = Path(__file__).parent


class Standard(TestCase):
    def test_char_doc(self):
        with (CURRENT_FOLDER / "samples" / "pdf" / "chars.pdf").open("rb") as fp:
            buffer = BufferStream(fp)
            db = XRefDB()
            db.update_from_xrefiter(iter_over_xref(buffer))
            for obj, gen in db.xrefs.keys():
                print(_save_or_get_object(buffer, db, obj, gen))
