
# 
# DO NOT EDIT THIS PAGE
# 
"""
# PDFMajor 

<table>
<tr>
  <td>Latest Release</td>
  <td>
    <a href="https://pypi.org/project/pdfmajor/">
    <img src="https://img.shields.io/pypi/v/pdfmajor.svg" alt="latest release" />
    </a>
  </td>
</tr>
</table>

PDF-Major is a fork of `PDFMiner.six`. It is meant to be a more light-weight implementation that makes fewer assumptions on the data. The ultimate goal of this project is to provide a simpler, faster and more functional library that both casual and low-level developers could build upon.

## Documentation

See documentation [here](https://asosnovsky.github.io/pdfmajor/).

## Basic Example
```py
from pdfmajor.interpreter import PDFInterpreter

for page in PDFInterpreter("/path/to/pdf.pdf"):
    print("page start", page.page_num)
    for item in page:
        print(" >", item)
    print("page end", page.page_num)
    
```

## Why Another Fork?

`PDFMiner` was designed to run in python 2.7>, `PDFMiner.six` was written to bring cross-version support for python 2 and 3. However, after attempting to build and extend upon `PDFMiner.six` I found it rather difficult to extend and identify additional details regarding the items encoded in the pdf. This library will attempt to expose as much information as possible to end-users, without having them solely rely on to-xml or to-json exports.

## Features

 * Functional extraction method based on generators
 * Parse, analyze, and convert PDF documents.
 * PDF-1.7 specification support. (well, almost)
 * Font-Color extraction
 * Shape fill and stroke color extraction
 * CJK languages and vertical writing scripts support.
 * Various font types (Type1, TrueType, Type3, and CID) support.
 * Basic encryption (RC4) support.

**Note**: We took out the layout-analysis process in this version (there is no more LTTextHorizontal or LTTextVertical). While the mathematics behind the grouping process was sound, the coupling of the layout-analysis process with the parsing and interpretation process produced unfriendly-code. This feature could be brought back by running your own implementation of it on the `pdfmajor.interpreter.PageInterpreter` class, but at the current time is not supported.

## How to Install

### Source

  * Install Python 3.6.4 or newer.
  * clone this repo

    `git clone https://github.com/asosnovsky/pdfmajor`
  * install repo

    `python setup.py install`

### Pypi
  * Install Python 3.6.4 or newer.
  * install repo

    `pip install pdfmajor`

## Terms and Conditions

(This is so-called MIT/X License)

Copyright (c) 2018-2019  Ariel Sosnovsky <ariel at sosnovsky dot ca>

Permission is hereby granted, free of charge, to any person
obtaining a copy of this software and associated documentation
files (the "Software"), to deal in the Software without
restriction, including without limitation the rights to use,
copy, modify, merge, publish, distribute, sublicense, and/or
sell copies of the Software, and to permit persons to whom the
Software is furnished to do so, subject to the following
conditions:

The above copyright notice and this permission notice shall be
included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY
KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE
WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR
PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR
OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

"""
__version__ = (1, 3, 8)

if __name__ == '__main__':
    print(
        "PDFMajor v" + '.'.join(map(str, __version__))
    )
    print(__doc__)
