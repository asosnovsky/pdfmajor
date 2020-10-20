from contextlib import contextmanager
from unittest import TestCase, main
from typing import List, Tuple, Callable
from os import remove
from tempfile import mktemp
from pdfmajor.converters.writers.html import HTMLMaker
from tqdm import tqdm

# Make temp file
FILE_NAME = mktemp()

TestFunction = Callable[[HTMLMaker], str];
TESTS: List[Tuple[TestFunction, str]] = [];

class HTMLTester(TestCase):
    @contextmanager
    def get_html(self):
        with HTMLMaker(FILE_NAME) as html:
            yield html
    def compare(self, expected: str):
        with open(FILE_NAME, 'r') as f:
            self.assertEqual(f.read() , expected)

    def test_html_basic(self):
        with self.get_html() as html:
            with html.elm("html", nolineend=True):
                html.write("test")
        self.compare("""<html >
 test
</html>""")

    def test_html_with_attributes(self):
        with self.get_html() as html:
            with html.elm("html", nolineend=True):
                with html.elm("head"):
                    html.singleton("meta", {
                        'http-equiv': "Content-Type",
                        'content': "text/html"
                    })
        self.compare("""<html >
 <head >
  <meta http-equiv="Content-Type" content="text/html" />
 </head>
</html>""")

    def test_html_with_children(self):
        with self.get_html() as html:
            with html.elm("html", nolineend=True):
                with html.elm("head"):
                    html.singleton("meta", {
                        'http-equiv': "Content-Type",
                        'content': "text/html"
                    })
                with html.elm("body"):
                    with html.elm("h1", css={"color": "red"}):
                        html.write("Hello World")
        self.compare("""<html >
 <head >
  <meta http-equiv="Content-Type" content="text/html" />
 </head>
 <body >
  <h1 style="color: red">
   Hello World
  </h1>
 </body>
</html>""")

    def test_html_with_css(self):
        with self.get_html() as html:
            with html.elm('style'):
                html.write('''.page { position: relative; overflow: hidden;border: 1px black solid;}''')
        self.compare("""<style >
 .page { position: relative; overflow: hidden;border: 1px black solid;}
</style>
""")

    
if __name__ == '__main__':
    # Run Tests
    main()
    # Clean up
    remove(FILE_NAME)