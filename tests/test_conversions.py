#!/usr/bin/env python
import re
import os
import logging

from unittest import TestCase, main
from typing import List
from pdfmajor.converters import convert_file
from xml.etree import ElementTree
from json import load as json_load
from tqdm import tqdm

def rel_path(*arg: str) -> str:
    return os.path.normpath(os.path.join(os.path.dirname(__file__), *arg))

EXTS = ['text', 'json','xml','html']
INPUT_FOLDER = rel_path("./samples/pdf")
OUTPUT_FOLDER = rel_path(f"./samples/output/")

if not os.path.exists(OUTPUT_FOLDER):
    os.makedirs(OUTPUT_FOLDER)

files = os.listdir(INPUT_FOLDER)

TOTAL = len(files)*len(EXTS)

class ConversionTest(TestCase):
    def test_conversion(self):
    # with tqdm(total=TOTAL) as waiter:
        for idx, file_name in enumerate(files):
            self.subTest(i=idx);
            file_name_no_ext = re.sub(r'\.pdf$',"", file_name)
            input_file_path = os.path.join(INPUT_FOLDER, file_name)

            for ext in EXTS:
                if not os.path.exists(os.path.join(OUTPUT_FOLDER, ext)):
                    os.makedirs(os.path.join(OUTPUT_FOLDER, ext))
                output_file_path = os.path.join(OUTPUT_FOLDER, ext, file_name_no_ext + "." + ext)
                if len(file_name) > len(file_name_no_ext):
                    # waiter.set_description(f"Conversion test -- {file_name}")
                    convert_file(
                        input_file=input_file_path,
                        output_file=output_file_path,
                        out_type=ext,
                        ignore_bad_chars=True,
                        debug_level=logging.WARN,
                    )
                    if ext == 'xml':
                        # waiter.set_description(f" > testing format {file_name}")
                        ElementTree.parse(output_file_path)
                    elif ext == 'json':
                        # waiter.set_description(f" > testing format {file_name}")
                        with open(output_file_path, 'r') as outf:
                            json_load(outf)
                # waiter.update()
            # waiter.set_description("Done")

    
if __name__ == '__main__':
    # Run Tests
    main()