import io
import os
import re

from typing import List, Optional

from .html import convert_to_html
from .xml import convert_to_xml
from .json import convert_to_json
from .text import convert_to_text
from .yaml import convert_to_yaml
from ..utils import logging

def convert_file(
        input_file: str, 
        output_file: Optional[str] = None, 
        image_folder_path: Optional[str] = None,
        codec: str = 'utf-8',
        maxpages: int = 0, 
        password: Optional[str] = None, 
        caching: bool = True, 
        check_extractable: bool = True,
        pagenos: Optional[List[int]] = None,
        dont_export_images: bool = False,
        debug_level: int = logging.WARNING,
        out_type: str = 'html',
    ):
    if output_file is None:
        output_file = os.path.join(
            os.path.dirname(input_file),
            os.path.basename(
                re.sub(r"\.\w+$", "."+out_type, input_file)
            )
        )
    if re.search(re.escape(out_type) + r'$', output_file ) is None:
        raise Exception("Please make sure that the file name and output type match!")
    if out_type == 'html':
        return convert_to_html(
            input_file_path=input_file, 
            output_file_path=output_file, 
            image_folder_path=image_folder_path,
            dont_export_images=dont_export_images,
            codec=codec,
            maxpages=maxpages, 
            password=password, 
            caching=caching, 
            check_extractable=check_extractable,
            pagenos=pagenos,
            debug_level=debug_level,
        )
    elif out_type == 'xml':
        return convert_to_xml(
            input_file_path=input_file, 
            output_file_path=output_file, 
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
        return convert_to_json(
            input_file_path=input_file, 
            output_file_path=output_file, 
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
    elif out_type == 'yaml' or out_type == 'yml':
        return convert_to_yaml(
            input_file_path=input_file, 
            output_file_path=output_file, 
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
        return convert_to_text(
            input_file_path=input_file, 
            output_file_path=output_file, 
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
    else: raise Exception("Please specify out_type as 'html' or 'xml' or 'json' or 'text' or 'yaml'")