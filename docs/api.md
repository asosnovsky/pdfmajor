# API

The library is constructed from 4 base modules:

 * **interpreter**: contains low-level classes for extracting fundamental data-structures from the documents
 * **converters**: contains high-level classes for conversion of the fundamental pdf structures to other formats
 * **imagewriter**: contains a simple implementation for converting PDF Image Streams to png/bmp/img formats
 * **layouts**: contains an abstraction layer for the data-structures found in the pdf

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

WIP 
