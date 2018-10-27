import re
import os

from typing import List
from pdfmajor.converters import convert_file

def rel_path(*arg: List[str]) -> str:
    return os.path.join(os.path.dirname(__file__), *arg)

EXT = 'html'
INPUT_FOLDER = rel_path("./pdf")
OUTPUT_FOLDER = rel_path(f"./output/{EXT}")

if not os.path.exists(OUTPUT_FOLDER):
    os.makedirs(OUTPUT_FOLDER)

# files = os.listdir(INPUT_FOLDER)
# files = ['fonts.pdf']
# files = ['bar-charts.pdf']
# files = ['font-color.pdf']
files = ['tables.pdf']

TOTAL = len(files)
for idx, file_name in enumerate(files):
    file_name_no_ext = re.sub(r'\.pdf$',"", file_name)

    print(f"processing {file_name} {idx}/{TOTAL}")
    if len(file_name) > len(file_name_no_ext):
        with open(os.path.join(INPUT_FOLDER, file_name), 'rb') as input_file:
            with open(os.path.join(OUTPUT_FOLDER, file_name_no_ext + "." + EXT), 'wb') as output_file:
                convert_file(
                    input_file=input_file,
                    output_file=output_file,
                    out_type=EXT,
                    debug=True,
                )
    print(f"processing {idx+1}/{TOTAL}")