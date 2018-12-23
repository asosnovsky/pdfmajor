from os import remove
from tempfile import mktemp
from pdfmajor.converters.writers.html import HTMLMaker

# Make temp file
FILE_NAME = mktemp()


with HTMLMaker(FILE_NAME) as html:
    with html.elm("html", nolineend=True):
        html.write("test")
assert(open(FILE_NAME, 'r').read() == """<html >
 test
</html>""")


with HTMLMaker(FILE_NAME) as html:
    with html.elm("html", nolineend=True):
        with html.elm("head"):
            html.singleton("meta", {
                'http-equiv': "Content-Type",
                'content': "text/html"
            })
assert(open(FILE_NAME, 'r').read() == """<html >
 <head >
  <meta http-equiv="Content-Type" content="text/html" />
 </head>
</html>""")

with HTMLMaker(FILE_NAME) as html:
    with html.elm("html", nolineend=True):
        with html.elm("head"):
            html.singleton("meta", {
                'http-equiv': "Content-Type",
                'content': "text/html"
            })
        with html.elm("body"):
            with html.elm("h1", css={"color": "red"}):
                html.write("Hello World")
assert(open(FILE_NAME, 'r').read() == """<html >
 <head >
  <meta http-equiv="Content-Type" content="text/html" />
 </head>
 <body >
  <h1 style="color: red">
   Hello World
  </h1>
 </body>
</html>""")

with HTMLMaker(FILE_NAME) as html:
    with html.elm('style'):
        html.write('''.page { position: relative; overflow: hidden;border: 1px black solid;}''')
assert(open(FILE_NAME, 'r').read() == """<style >
 .page { position: relative; overflow: hidden;border: 1px black solid;}
</style>
""")

# Clean up
remove(FILE_NAME)