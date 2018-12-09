#!/usr/bin/env python
import re
import os
import logging

from typing import List
from pdfmajor.converters import convert_file
from xml.etree import ElementTree
from tqdm import tqdm

from pdfmajor.extractor import extract_items_from_pdf
from pdfmajor.layouts import LTPage

def rel_path(*arg: List[str]) -> str:
    return os.path.join(os.path.dirname(__file__), *arg)

print(extract_items_from_pdf(rel_path('pdf/chars.pdf')))
# for page in extract_items_from_pdf(rel_path('pdf/chars.pdf')):
#     print('page-start', page)
#     for item in page:
#         print(' ', item)
#     print('page-end', page)
    