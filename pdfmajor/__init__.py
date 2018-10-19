
# 
# DO NOT EDIT THIS PAGE
# 
"""
# PDFMajor

PDF-Major is a fork of `PDFMiner.six`. It is meant to be a more light-weight implementation that makes fewer assumptions on the data. Additionally, this version intends to be more up to date with recent versions of python and make liberal use of the typing capabilities of python for improved future maintainability.

## Documentation

See documentation [here](https://asosnovsky.github.io/pdfmajor/).

## Why Another Fork?

`PDFMiner` was designed to run in python 2.7>, `PDFMiner.six` was written to bring cross-version support for python 2 and 3. This versions intends to make use of the latest improvement in the python language while remaining fairly simple to develop with. 


## Features

 * Written entirely in Python.
 * Parse, analyze, and convert PDF documents.
 * PDF-1.7 specification support. (well, almost)
 * CJK languages and vertical writing scripts support.
 * Various font types (Type1, TrueType, Type3, and CID) support.
 * Basic encryption (RC4) support.
 * Font-Color extraction
 * Shape fill and stroke color extraction

**Note**: We took out the layout-analysis process in this version (there is no more LTTextHorizontal or LTTextVertical). While the mathematics behind the grouping process was sound, the coupling of the layout-analysis process with the parsing and interpretation process produced unfriendly-code. This feature could be brought back by extending the `pdfmajor.layouts.PDFLayoutAnalyzer` class, but at the current time is not supported.

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
__version__ = (1, 0, 7)

if __name__ == '__main__':
    print(
        "PDFMajor v" + '.'.join(map(str, __version__))
    )
    print(__doc__)
