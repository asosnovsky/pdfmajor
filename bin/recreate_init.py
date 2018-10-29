#!/bin/python
import os
import re

current_dir = os.path.dirname(__file__)

INIT_TEMPLATE = '''
# 
# DO NOT EDIT THIS PAGE
# 
"""
{long_description}
"""
__version__ = ({version_tuple})

if __name__ == '__main__':
    print(
        "PDFMajor v" + '.'.join(map(str, __version__))
    )
    print(__doc__)
'''


def update_pdfmajor__init___(version: str, doc: str):
    with open('pdfmajor/__init__.py', 'w') as file:
        file.write(INIT_TEMPLATE.format(
            long_description=doc,
            version_tuple=re.sub(r"\.", ", ", version, count=2)
        ))

def update_current_version_lock(version: str):
    with open(".version", 'w') as file:
        file.write("v"+version)
