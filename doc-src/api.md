# API

The library is constructed from 4 base modules:

 * **extractor**: contains a high-level function for functional extraction of pdf-assets
 * **interpreter**: contains low-level classes for extracting fundamental data-structures from the documents
 * **converters**: contains high-level classes for conversion of the fundamental pdf structures to other formats
 * **imagewriter**: contains a simple implementation for converting PDF Image Streams to png/bmp/img formats
 * **layouts**: contains an abstraction layer for the data-structures found in the pdf

## extractors
Contains a high-level function for functional extraction of pdf-assets

### Example
```py
from pdfmajor.extractor import extract_items_from_pdf

for page in extract_items_from_pdf('path/to/your/file.pdf'):
    print('page-start', page)
    for item in page:
        print(' ', item)
    print('page-end', page)
    
```

### extract_items_from_pdf(input_file_path,maxpages,password,caching,check_extractable,pagenos,debug_level) -> generator[LTPage]

This generator-function yields individual pages which contain their respected items.

#### Arguments

- `input_file_path`: [str](str) 
- `maxpages`: [int](#) defaults to 0 
- `password`: [str](#) defaults to None 
- `caching`: [bool](#) defaults to True 
- `check_extractable`: [bool](#) defaults to True
- `pagenos`: [List[int]](#) defaults to None
- `debug_level`: [logging.levels](#https://docs.python.org/3/library/logging.html#levels) defaults logging.WARNING

#### Return Value
This function returns a generator that makes `LTPage`

## interpreter
    WIP

## converters

Contains high-level classes for conversion of the fundamental pdf structures to other formats. This library includes 4 high-level conversion classes:

- HTMLConverter
- JSONConverter
- XMLConverter
- TextConverter

These classes all extend the [PDFConverter](#converters.PDFConverter). To use them simply call the static method [parse_file](#converterspdfconverterparse_fileinput_file-output_file-image_folder_path-codec-maxpages-password-caching-check_extractable-pagenos).

### Example

```py
from pdfmajor.converters import HTMLConverter

input_file = open('path/to/input/file.pdf', 'rb')
output_file = open('path/to/output/file.html', 'wb')
HTMLConverter.parse_file(
    input_file,
    output_file
)
input_file.close()
output_file.close()
```

### converters.convert_file(input_file, output_file, image_folder_path, codec, maxpages, password, caching, check_extractable, pagenos, out_type)

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

### Example (converters.convert_file)

```py
from pdfmajor.converters import convert_file

input_file = open('path/to/input/file.pdf', 'rb')
output_file = open('path/to/output/file.html', 'wb')
convert_file(
    input_file,
    output_file
)
input_file.close()
output_file.close()
```

### converters.PDFConverter

Extends `layouts.PDFLayoutAnalyzer`.

#### converters.PDFConverter.\_\_init\_\_(rsrcmgr, outfp, imagewriter, codec, pageno)

- `rsrcmgr`: [PDFResourceManager](#interpreter.PDFResourceManager)
- `outfp`: [TextIOWrapper](https://docs.python.org/3/library/io.html#io.TextIOWrapper)
- `imagewriter`: [ImageWriter](#imagewriter.ImageWriter)
- `codec`: [str](#) defaults to 'utf-8'
- `pageno`: [int](#) defaults to 1

initialization function for the class

#### converters.PDFConverter.parse_file(input_file, output_file, image_folder_path, codec, maxpages, password, caching, check_extractable, pagenos)

returns the output file [TextIOWrapper](https://docs.python.org/3/library/io.html#io.TextIOWrapper).

- `input_file`: [TextIOWrapper](https://docs.python.org/3/library/io.html#io.TextIOWrapper) 
- `output_file`: [TextIOWrapper](https://docs.python.org/3/library/io.html#io.TextIOWrapper) 
- `image_folder_path`: [str](#) defaults to None
- `codec`: [str](#) defaults to 'utf-8'
- `maxpages`: [int](#) defaults to 0 
- `password`: [str](#) defaults to None 
- `caching`: [bool](#) defaults to True 
- `check_extractable`: [bool](#) defaults to True
- `pagenos`: [List[int]](#) defaults to None

## imagewriter

WIP 

## layouts

WIP: this documentation set is not yet complete.

### Layout Items

All layout items extend the `LTItem` class. There are two kinds of layout items:

- LTComponent: extends the base `LTItem` class, this class will have additional values such as boundary boxes, height and width
- LTContainer: extends the `LTComponent` class, this class is used to contain elements of the pdf that would have child elements. Iterating on this element will output its child elements.


#### Layout Containers
All of these classes extend the LTContainer class.

- LTPage: a layout item containing all elements of the given page.
- LTFigure: a layout item containing LTCurves and LTImages
- LTCharBlock: a layout item containing LTChars

#### Layout Components
All of these classes extend the LTComponent class.

- LTChar: an individual character
- LTCurves: represents a collection of svg-paths (available under `self.paths`)
- LTImage: a component containing information regarding an image

