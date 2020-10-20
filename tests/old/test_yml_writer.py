from os import remove
from tempfile import mktemp
from pdfmajor.converters.writers.yaml import YAMLMaker

# Make temp file
FILE_NAME = mktemp()


with YAMLMaker(FILE_NAME) as yml:
    yml.write("name", "bob")
    yml.write("age", "20")
    with yml.object("wife") as wife:
        wife.write("name", "kory") 
        wife.write("age", "21")
    with yml.array("children") as children:
        with children.object() as child:
            child.write("name", "Mike")
            with child.array("toys") as toys:
                toys.write("lion")
                toys.write("bear")
    with yml.object("computer") as computer:
        computer.write("type", "awesome")
assert(open(FILE_NAME, 'r').read() == """name: bob
age: 20
wife:
  name: kory
  age: 21
children:
  - name: Mike
    toys:
      - lion
      - bear
computer:
  type: awesome""")

with YAMLMaker(FILE_NAME) as yml:
    yml.write("name", "bob")
    yml.write("age", "20")
    yml.place_object("wife", {
        "name": "kory",
        "age": 21
    })
    with yml.array("children") as children:
        with children.object() as child:
            child.write("name", "Mike")
            child.place_array("toys", [
                "lion", "bear"
            ])
    yml.place_object("computer", {"type": "awesome"})
assert(open(FILE_NAME, 'r').read() == """name: bob
age: 20
wife:
  name: kory
  age: 21
children:
  - name: Mike
    toys:
      - lion
      - bear
computer:
  type: awesome""")

with YAMLMaker(FILE_NAME) as yml:
    with yml.array('pages') as pages:
        with pages.object() as page:
            page.write("id", 0)
            page.write("width", 100)
            page.write("height", 200)
            with page.array("children") as children:
                with children.object() as curve:
                    with curve.object("stroke") as fill:
                        fill.write("type", "DeviceRGB")
                        fill.write("value", ['1','2','3'])
                    curve.write("x0", 0)
                    curve.write("x1", 1)
                    with curve.object("fill") as fill:
                        fill.write("type", "DeviceRGB")
                        fill.write("value", ['1','2','3'])
                    curve.write("y0", 0)
                    curve.write("y1", 1)

assert(open(FILE_NAME, 'r').read() == """pages:
  - id: 0
    width: 100
    height: 200
    children:
      - stroke:
          type: DeviceRGB
          value: ['1', '2', '3']
        x0: 0
        x1: 1
        fill:
          type: DeviceRGB
          value: ['1', '2', '3']
        y0: 0
        y1: 1""")



# Clean up
remove(FILE_NAME)