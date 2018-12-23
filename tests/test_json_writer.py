from os import remove
from tempfile import mktemp
from pdfmajor.converters.writers.json import JSONMaker

# Make temp file
FILE_NAME = mktemp()

with JSONMaker(FILE_NAME) as obj:
    obj.number("a", 2)
    obj.string("hello", "world")
assert(open(FILE_NAME, 'r').read() == """{
  "a": 2,
  "hello": "world"
}""")

with JSONMaker(FILE_NAME) as obj:
    with obj.object("test") as child:
        child.number("A", 2)
assert(open(FILE_NAME, 'r').read() == """{
  "test": {
    "A": 2
  }
}""")

with JSONMaker(FILE_NAME) as obj:
    with obj.object("hello") as child:
        with child.object("nested") as nested:
            with nested.object("so") as so:
                so.string("really", 'nested'),
                so.number("man", 2)
            nested.number("he", 3)
        child.string('fo', 'real')
    obj.string('fo', 'real2')
assert(open(FILE_NAME, 'r').read() == """{
  "hello": {
    "nested": {
      "so": {
        "really": "nested",
        "man": 2
      },
      "he": 3
    },
    "fo": "real"
  },
  "fo": "real2"
}""")

with JSONMaker(FILE_NAME) as obj:
    with obj.array("hello") as child:
        child.number(1)
        with child.array() as nchild:
            nchild.string('wow')
        child.number(3)
assert(open(FILE_NAME, 'r').read() == """{
  "hello": [
    1,
    [
      "wow"
    ],
    3
  ]
}""")

with JSONMaker(FILE_NAME) as obj:
    with obj.array("pages") as pages:
        with pages.object() as page:
            page.number("id", 1)
            page.number("height", 20)
            page.number("width", 20)
            with page.array("children") as children:
                with children.object() as item:
                    item.string("type", "char-block")
                    item.string("text", "test")
                    item.string("color_type", "rgb")
                    with item.array("color_vals") as col_vals:
                        col_vals.number(0)
                        col_vals.number(0)
                        col_vals.number(0)
                    item.number("x0", 2)
                    item.number("x1", 4.2)
                    item.number("y0", 231.12)
                    item.number("y1", 331.12)
print(open(FILE_NAME, 'r').read())
assert(open(FILE_NAME, 'r').read() == """{
  "pages": [
    {
      "id": 1,
      "height": 20,
      "width": 20,
      "children": [
        {
          "type": "char-block",
          "text": "test",
          "color_type": "rgb",
          "color_vals": [
            0,
            0,
            0
          ],
          "x0": 2,
          "x1": 4.2,
          "y0": 231.12,
          "y1": 331.12
        }
      ]
    }
  ]
}""")


# Clean up
remove(FILE_NAME)