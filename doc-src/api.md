# API

The library is constructed from 4 base modules:

 * **parser**: contains low-level classes for extracting fundamental data-structures from the documents
 * **interpreter**: a interpreter of the pdf-standard commands
 * **converters**: contains high-level functions for conversion of the fundamental pdf structures to other formats
 * **imagewriter**: contains a simple implementation for converting PDF Image Streams to png/bmp/img formats

## parser

WIP

## interpreter
a interpreter of the pdf-standard commands

### Example
```py
from pdfmajor.interpreter import PageInterpreter

for page in PDFInterpreter("/path/to/pdf.pdf"):
    print("page start", page.page_num)
    for item in page:
        print(" >", item)
    print("page end", page.page_num)
```

### interpreter.PDFInterpreter

This generator-function yields individual pages which contain their respected items.

#### Arguments

- `input_file_path`: [str](#)
- `preload`: [bool](#) defaults to False
- `maxpages`: [int](#) defaults to 0 
- `password`: [str](#) defaults to None 
- `caching`: [bool](#) defaults to True 
- `check_extractable`: [bool](#) defaults to True
- `pagenos`: [List[int]](#) defaults to None
- `debug_level`: [logging.levels](#https://docs.python.org/3/library/logging.html#levels) defaults logging.WARNING

#### Yield Value
This function returns a generator that yields [PDFInterpreter](#interpreterpageinterpreter).

### interpreter.PageInterpreter

This generator-function-class yields individual [layout items](#layout-items).
### Layout Items

All layout items extend the `LTItem` class. There are two kinds of layout items:

- LTComponent: extends the base `LTItem` class, this class will have additional values such as boundary boxes, height and width
- LTContainer: extends the `LTComponent` class, this class is used to contain elements of the pdf that would have child elements. Iterating on this element will output its child elements.


#### Layout Containers
All of these classes extend the LTContainer class.

- LTXObject: a layout item containing other additional layout items
- LTCharBlock: a layout item containing LTChars

#### Layout Components
All of these classes extend the LTComponent class.

- LTChar: an individual character
- LTCurves: represents a collection of svg-paths (available under `self.paths`)
- LTImage: a component containing information regarding an image

## converters

Contains high-level functions for conversion of the fundamental pdf structures to other formats. This library includes 4 high-level conversion cases:

- HTML
- JSON
- XML
- Text

These formats are all generated using the [PageInterpreter](#PDFInterpreter). To use them simply call the static method [parse_file](#converterspdfconverter).

### Example

```py
from pdfmajor.converters import convert_file

convert_file(
    "path/to/input/file.pdf",
    "path/to/output/file.html",
    out_type="html"
)
```

### converters.convert_file

A high-level abstraction for the conversion classes.

- `input_file`: [TextIOWrapper](https://docs.python.org/3/library/io.html#io.TextIOWrapper) 
- `output_file`: [TextIOWrapper](https://docs.python.org/3/library/io.html#io.TextIOWrapper) 
- `image_folder_path`: [str](#) defaults to None
- `codec`: [str](#) defaults to 'utf-8'
- `maxpages`: [int](#) defaults to 0 
- `password`: [str](#) defaults to None 
- `caching`: [bool](#) defaults to True 
- `check_extractable`: [bool](#) defaults to True
- `pagenos`: [List[int]](#) defaults to None
- `out_type`: [str](#) defaults to 'html'

## imagewriter

WIP 
