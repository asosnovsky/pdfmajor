from pathlib import Path
from unittest import TestCase, main

from pdfmajor.interpreter import PDFInterpreter, exceptions

CURRENT_FOLDER = Path("./")

class BadUnicode(TestCase):
    def test_ensure_failure(self):
        pdf = PDFInterpreter(CURRENT_FOLDER / "tests" / "samples" / "pdf" / "bad-unicode.pdf", ignore_bad_chars=False)
        pages = list(pdf)
        with self.assertRaises(exceptions.PDFUnicodeNotDefined):
            list(pages[2])

    def test_ensure_no_failure(self):
        pdf = PDFInterpreter(CURRENT_FOLDER / "tests" / "samples" / "pdf" / "bad-unicode.pdf", ignore_bad_chars=True)
        pages = list(pdf)
        list(pages[2])


if __name__ == '__main__':
    # Run Tests
    main()
