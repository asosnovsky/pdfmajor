import io
import os
import re

from typing import List

from .HTMLConverter import HTMLConverter
from .JSONConverter import JSONConverter
from .XMLConverter import XMLConverter
from .TextConverter import TextConverter
from ..utils import logging

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
        dont_export_images: bool = False,
        debug_level: int = logging.WARNING,
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
            input_file=input_file, 
            output_file=output_file, 
            image_folder_path=image_folder_path,
            codec=codec,
            maxpages=maxpages, 
            password=password, 
            caching=caching, 
            check_extractable=check_extractable,
            pagenos=pagenos,
            dont_export_images=dont_export_images,
            debug_level=debug_level,
        )
    elif out_type == 'xml':
        return XMLConverter.parse_file(
            input_file=input_file, 
            output_file=output_file, 
            image_folder_path=image_folder_path,
            codec=codec,
            maxpages=maxpages, 
            password=password, 
            caching=caching, 
            check_extractable=check_extractable,
            pagenos=pagenos,
            dont_export_images=dont_export_images,
            debug_level=debug_level,
        )
    elif out_type == 'json':
        return JSONConverter.parse_file(
            input_file=input_file, 
            output_file=output_file, 
            image_folder_path=image_folder_path,
            codec=codec,
            maxpages=maxpages, 
            password=password, 
            caching=caching, 
            check_extractable=check_extractable,
            pagenos=pagenos,
            dont_export_images=dont_export_images,
            debug_level=debug_level,
        )
    elif out_type == 'text':
        return TextConverter.parse_file(
            input_file=input_file, 
            output_file=output_file, 
            image_folder_path=image_folder_path,
            codec=codec,
            maxpages=maxpages, 
            password=password, 
            caching=caching, 
            check_extractable=check_extractable,
            pagenos=pagenos,
            dont_export_images=dont_export_images,
            debug_level=debug_level,
        )
    else: raise Exception("Please specify out_type as 'html' or 'xml' or 'json' or 'text'")