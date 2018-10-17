from setuptools import setup, find_namespace_packages
import sys

packages = find_namespace_packages(include=['pdfmajor.*'])

with open('README.md') as file:
    long_description = file.read()

setup(
    name='pdfmajor',
    version='1.0.2',
    packages=packages,
    install_requires=[
        'pycryptodome', 
        'chardet'
    ],
    description='PDF parser',
    long_description=long_description,
    license='MIT/X',
    author='Ariel Sosnovsky + Yusuke Shinyama + Philippe Guglielmetti',
    author_email='ariel@sosnovsky.ca',
    url='https://github.com/asosnovsky/pdfmajor',
    scripts=[
        'tools/pdfconvert.py',
    ],
    keywords=[
        'pdf parser',
        'pdf converter',
        'text mining',
    ],
    classifiers=[
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
)
