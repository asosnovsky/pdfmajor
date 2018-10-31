# ==============
# Dependencies
# ==============
from setuptools import setup, find_packages
import sys

# ==============
# PARAMS
# ==============
with open('README.md') as readme_file:
    SETUP = {
        "name": "pdfmajor",
        "version": "1.1.6",
        "packages": find_packages(include=['pdfmajor*']),
        "install_requires": [
            'pycryptodome', 
            'chardet'
        ],
        "description": 'PDF parser',
        "long_description": readme_file.read(),
        "license": 'MIT/X',
        "author": 'Ariel Sosnovsky + Yusuke Shinyama + Philippe Guglielmetti',
        "author_email": 'ariel@sosnovsky.ca',
        "url": 'https://github.com/asosnovsky/pdfmajor',
        "scripts": [
            'tools/pdfconvert.py',
        ],
        "keywords": [
            'pdf parser',
            'pdf converter',
            'text mining',
        ],
        "classifiers": [
            'Programming Language :: Python',
            'Programming Language :: Python :: 3.6',
            'Programming Language :: Python :: 3.7',
            'Development Status :: 5 - Production/Stable',
            'Environment :: Console',
            'Intended Audience :: Developers',
            'Intended Audience :: Science/Research',
            'License :: OSI Approved :: MIT License',
            'Topic :: Text Processing',
        ],
    }

# ==============
# Update __init__.py
# ==============
from bin.recreate_init import update_pdfmajor__init___, update_current_version_lock
update_pdfmajor__init___(SETUP["version"], SETUP["long_description"])
update_current_version_lock(SETUP["version"])

# ==============
# Run Setup
# ==============
setup(**SETUP)
