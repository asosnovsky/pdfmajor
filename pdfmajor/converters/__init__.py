import io
import os
import re

from typing import List

from .HTMLConverter import HTMLConverter
from .JSONConverter import JSONConverter
from .XMLConverter import XMLConverter
from .TextConverter import TextConverter

def convert_file(
        input_file: io.TextIOWrapper, 
        output_file: io.TextIOWrapper = None, 
        image_folder_path: str = None,
        codec: str = 'utf-8',
        maxpages: int = 0, 
        password: str = None, 
        caching: bool = True, 
        check_extractable: bool = True,
        pagenos: List[int] = None,
        debug: bool = False,
        out_type: str = 'html',
    ):
    if output_file is None:
        output_file = open(
                os.path.join(
                os.path.dirname(input_file.name),
                os.path.basename(
                    re.sub(r"\.\w+$", "."+out_type, input_file.name)
                )
            ),
            'wb'
        )
    if re.search(re.escape(out_type) + r'$', output_file.name ) is None:
        raise Exception("Please make sure that the file name and output type match!")
    if out_type == 'html':
        return HTMLConverter.parse_file(
            input_file, 
            output_file, 
            image_folder_path,
            codec,
            maxpages, 
            password, 
            caching, 
            check_extractable,
            pagenos,
            debug,
        )
    elif out_type == 'xml':
        return XMLConverter.parse_file(
            input_file, 
            output_file, 
            image_folder_path,
            codec,
            maxpages, 
            password, 
            caching, 
            check_extractable,
            pagenos,
            debug,
        )
    elif out_type == 'json':
        return JSONConverter.parse_file(
            input_file, 
            output_file, 
            image_folder_path,
            codec,
            maxpages, 
            password, 
            caching, 
            check_extractable,
            pagenos,
            debug,
        )
    elif out_type == 'text':
        return TextConverter.parse_file(
            input_file, 
            output_file, 
            image_folder_path,
            codec,
            maxpages, 
            password, 
            caching, 
            check_extractable,
            pagenos,
            debug,
        )
    else: raise Exception("Please specify out_type as 'html' or 'xml' or 'json' or 'text'")