#!/usr/bin/env python
import re
import os
import logging

from typing import List
from pdfmajor.converters import convert_file
from xml.etree import ElementTree
from tqdm import tqdm

def rel_path(*arg: List[str]) -> str:
    return os.path.join(os.path.dirname(__file__), *arg)

EXT = 'html'
INPUT_FOLDER = rel_path("./pdf")
OUTPUT_FOLDER = rel_path(f"./output/{EXT}")

if not os.path.exists(OUTPUT_FOLDER):
    os.makedirs(OUTPUT_FOLDER)

files = os.listdir(INPUT_FOLDER)

TOTAL = len(files)
waiter = tqdm(enumerate(files), total=TOTAL)
for idx, file_name in waiter:
    file_name_no_ext = re.sub(r'\.pdf$',"", file_name)
    input_file_path = os.path.join(INPUT_FOLDER, file_name)
    output_file_path = os.path.join(OUTPUT_FOLDER, file_name_no_ext + "." + EXT)

    if len(file_name) > len(file_name_no_ext):
        waiter.set_description(f"Processing {file_name}")
        with open(input_file_path, 'rb') as input_file:
            with open(output_file_path, 'wb') as output_file:
                convert_file(
                    input_file=input_file,
                    output_file=output_file,
                    out_type=EXT,
                    debug_level=logging.NOTSET,
                )
        if EXT == 'xml':
            waiter.set_description(f" > testing format {file_name}")
            ElementTree.parse(output_file_path)
        waiter.refresh()
    waiter.set_description("Done")
waiter.close()